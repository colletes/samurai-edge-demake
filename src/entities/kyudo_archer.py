"""
Kyudo Archer (Arqueiro Tradicional de Hakama):
Mestre da arte milenar do arco Yumi.
Possui windup preparatório para retesar a corda e disparar flecha fatal de longo alcance.
Pode cancelar o disparo e usar a Flecha de Corda para se puxar pelo mapa em fuga rápida,
tornando a partida um jogo de gato e rato.
"""
import math
import random
import pygame
from src.config import (
    COLOR_ARCHER_HAKAMA, COLOR_ARCHER_KIMONO, COLOR_ARCHER_AURA,
    COLOR_BOW_WOOD, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import (
    KyudoArrowProjectile, RopeArrowProjectile, HamayaArrowProjectile,
    SacredArrowVolleyProjectile
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_BOW_DRAW = "BOW_DRAW"

class KyudoArcher(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Tomoe")
        self.char_type = "tomoe"
        self.speed = 4.2

        # Mecânica de Disparo com Yumi (Mira Manual - Sem Windup)
        self.draw_duration = 0.0
        self.draw_timer = 0.0
        self.target_aim_x = 0.0
        self.target_aim_y = 0.0

        # Mecânica de Flecha com Corda (Hold & Release)
        self.is_charging_rope = False
        self.rope_charge_time = 0.0
        self.rope_charge_duration = 0.45  # 0.45s para atingir alcance máximo
        self.rope_min_range = 3.0
        self.rope_max_range = 10.5
        self.target_rope_x = self.wx
        self.target_rope_y = self.wy
        self.rope_cooldown = 2.0
        self.rope_timer = 0.0

        # Mecânica de Recarga de Flecha Yumi (Cooldown)
        self.arrow_cooldown = 1.20
        self.arrow_cooldown_timer = 0.0

        # Ação Secundária: Chuva de Flechas Sagradas em Arco (Salva Sagrada - Mecanismo de mira e cooldown idênticos à Anne)
        self.volley_cooldown = 4.5
        self.volley_cooldown_timer = 4.5  # Inicia com 4.5s no round para evitar nuke instantâneo no spawn (idêntico à Anne)
        self.is_aiming_volley = False
        self.volley_target_wx = self.wx + 3.0
        self.volley_target_wy = self.wy
        self.volley_reticle_pulse = 0.0

        # Ação Secundária Retrocompatível: Barreira dos Ventos Kami (Ofuda Barrier)
        self.ofuda_barrier_timer = 0.0
        self.ofuda_barrier_duration = 0.85
        self.ofuda_cooldown = 3.2
        self.ofuda_cooldown_timer = 0.0
        self.ofuda_orbit_angle = 0.0

        # Terceira Ação: Esquiva Ágil Miko
        self.is_agile_dodge = True
        self.roll_speed = 10.5
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.35

    @property
    def sacred_volley_cooldown(self) -> float:
        return self.volley_cooldown

    @sacred_volley_cooldown.setter
    def sacred_volley_cooldown(self, val: float):
        self.volley_cooldown = val

    @property
    def sacred_volley_cooldown_timer(self) -> float:
        return self.volley_cooldown_timer

    @sacred_volley_cooldown_timer.setter
    def sacred_volley_cooldown_timer(self, val: float):
        self.volley_cooldown_timer = val

    @property
    def hamaya_cooldown(self) -> float:
        return self.volley_cooldown

    @hamaya_cooldown.setter
    def hamaya_cooldown(self, val: float):
        self.volley_cooldown = val

    @property
    def hamaya_cooldown_timer(self) -> float:
        return self.volley_cooldown_timer

    @hamaya_cooldown_timer.setter
    def hamaya_cooldown_timer(self, val: float):
        self.volley_cooldown_timer = val

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def start_sacred_volley(self, target_wx: float, target_wy: float):
        """Inicia a mira em arco da Chuva de Flechas Sagradas (Hold). Tomoe pode se mover livremente."""
        if not self.is_alive or self.volley_cooldown_timer > 0:
            return
        self.is_aiming_volley = True
        self.volley_target_wx = target_wx
        self.volley_target_wy = target_wy

    def start_volley_strike(self, target_wx: float, target_wy: float):
        self.start_sacred_volley(target_wx, target_wy)

    def update_sacred_volley(self, dt: float, target_wx: float, target_wy: float):
        """Atualiza o retículo de mira da chuva de flechas enquanto o botão secundário for mantido pressionado."""
        if not self.is_alive or not self.is_aiming_volley:
            self.is_aiming_volley = False
            return
        self.volley_reticle_pulse += dt * 8.0
        self.volley_target_wx += (target_wx - self.volley_target_wx) * min(1.0, dt * 10.0)
        self.volley_target_wy += (target_wy - self.volley_target_wy) * min(1.0, dt * 10.0)

    def update_volley_strike(self, dt: float, target_wx: float, target_wy: float):
        self.update_sacred_volley(dt, target_wx, target_wy)

    def release_sacred_volley(self, projectiles: list, particles: list = None):
        """Dispara a salva de flechas sagradas em arco ao soltar o botão secundário (Release)."""
        if not self.is_aiming_volley or not self.is_alive:
            self.is_aiming_volley = False
            return
        self.is_aiming_volley = False
        self.volley_cooldown_timer = self.volley_cooldown
        self.sacred_volley_cooldown_timer = self.volley_cooldown
        self.hamaya_cooldown_timer = self.volley_cooldown

        from src.entities.projectile import SacredArrowVolleyProjectile
        projectiles.append(SacredArrowVolleyProjectile(self.wx, self.wy, self.volley_target_wx, self.volley_target_wy, owner=self))

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.45, color=(255, 230, 90)))
            for _ in range(6):
                particles.append(SparkParticle(self.wx, self.wy, 0.55, color=(255, 255, 240)))

    def release_volley_strike(self, projectiles: list, particles: list = None):
        self.release_sacred_volley(projectiles, particles)

    def trigger_quick_volley(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """Disparo Imediato da Salva de Flechas Sagradas em Arco (Tap rápido ou IA)."""
        if not self.is_alive or self.volley_cooldown_timer > 0 or projectiles is None:
            return
        self.volley_cooldown_timer = self.volley_cooldown
        self.sacred_volley_cooldown_timer = self.volley_cooldown
        self.hamaya_cooldown_timer = self.volley_cooldown
        self.is_aiming_volley = False

        from src.entities.projectile import SacredArrowVolleyProjectile
        projectiles.append(SacredArrowVolleyProjectile(self.wx, self.wy, target_wx, target_wy, owner=self))

        if particles is not None:
            for _ in range(12):
                particles.append(SparkParticle(self.wx, self.wy, 0.45, color=(255, 230, 90)))
            for _ in range(6):
                particles.append(SparkParticle(self.wx, self.wy, 0.55, color=(255, 255, 240)))

    def trigger_hamaya_shot(self, target_wx: float, target_wy: float, projectiles: list = None, particles: list = None):
        """Retrocompatibilidade: dispara a salva rápida de flechas sagradas em arco."""
        proj_list = projectiles if projectiles is not None else getattr(self, "projectiles_ref", None)
        if proj_list is not None:
            self.trigger_quick_volley(target_wx, target_wy, proj_list, particles)

    def trigger_ofuda_barrier(self, particles: list = None):
        """Ação Secundária: Barreira dos Ventos Kami — talismãs sagrados giratórios que repelem projéteis e empurram oponentes."""
        if not self.can_act() or self.ofuda_cooldown_timer > 0:
            return
        self.ofuda_barrier_timer = self.ofuda_barrier_duration
        self.ofuda_cooldown_timer = self.ofuda_cooldown
        if particles is not None:
            for _ in range(14):
                particles.append(SparkParticle(self.wx, self.wy, 0.45))

    def is_ofuda_active(self) -> bool:
        return self.is_alive and self.ofuda_barrier_timer > 0

    def can_move(self) -> bool:
        if self.is_charging_rope:
            return self.is_alive
        return super().can_move()

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        if self.is_charging_rope:
            orig_speed = self.speed
            self.speed = orig_speed * 0.45  # Movimentação tática cuidadosa enquanto mira a corda
            super().apply_movement(move_x, move_y, dt, game_map)
            self.speed = orig_speed
        else:
            super().apply_movement(move_x, move_y, dt, game_map)

    def trigger_bow_draw(self, target_wx: float, target_wy: float, projectiles: list = None, particles: list = None):
        """Ataque Primário: Disparo imediato da flecha Yumi sem windup (mira manual)."""
        if not self.can_act() or self.arrow_cooldown_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.target_aim_x = target_wx
        self.target_aim_y = target_wy
        self.state = STATE_RECOVERY
        self.state_timer = 0.20
        self.arrow_cooldown_timer = self.arrow_cooldown

        proj_list = projectiles if projectiles is not None else getattr(self, "projectiles_ref", None)
        if proj_list is not None:
            bx = self.wx + self.facing_x * 0.65
            by = self.wy + self.facing_y * 0.65
            arrow = KyudoArrowProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
            proj_list.append(arrow)

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.4))

    def start_rope_arrow_charge(self, target_wx: float, target_wy: float, game_map=None):
        """Inicia o tensionamento da corda (Hold)."""
        if not self.can_act() or self.rope_timer > 0:
            return
        self.is_charging_rope = True
        self.rope_charge_time = 0.0
        self.set_facing(target_wx, target_wy)
        self._calculate_rope_target(game_map)

    def update_rope_charge(self, dt: float, target_wx: float, target_wy: float, game_map=None):
        """Atualiza a mira e alcance contínuo enquanto o botão é mantido pressionado."""
        if not self.is_alive or not self.is_charging_rope:
            self.is_charging_rope = False
            return
        if self.state in (STATE_STUNNED, STATE_DEAD):
            self.is_charging_rope = False
            return
        self.rope_charge_time += dt
        self.set_facing(target_wx, target_wy)
        self._calculate_rope_target(game_map)

    def _calculate_rope_target(self, game_map=None):
        """Calcula o ponto exato de impacto respeitando os limites da arena e obstáculos."""
        charge_ratio = min(1.0, self.rope_charge_time / self.rope_charge_duration)
        cur_range = self.rope_min_range + (self.rope_max_range - self.rope_min_range) * charge_ratio

        min_x = 1.0
        max_x = (game_map.cols - 1.0) if game_map else 20.0
        min_y = 1.0
        max_y = (game_map.rows - 1.0) if game_map else 20.0

        step_sz = 0.25
        steps = max(1, int(cur_range / step_sz))
        cx, cy = self.wx, self.wy

        for i in range(1, steps + 1):
            nx = self.wx + self.facing_x * (i * step_sz)
            ny = self.wy + self.facing_y * (i * step_sz)

            # Limite estrito do mapa: para exatamente na borda
            if nx <= min_x or nx >= max_x or ny <= min_y or ny >= max_y:
                cx = max(min_x, min(max_x, nx))
                cy = max(min_y, min(max_y, ny))
                break

            # Trava em obstáculos sólidos da arena (rochas e poço - bambus são transpassados)
            hit = False
            if game_map:
                for r in game_map.rocks:
                    if math.hypot(nx - r.wx, ny - r.wy) < (r.radius + 0.2):
                        hit = True; break
                if not hit and game_map.well and math.hypot(nx - game_map.well.wx, ny - game_map.well.wy) < (game_map.well.radius + 0.2):
                    hit = True
            if hit:
                cx, cy = nx, ny
                break
            cx, cy = nx, ny

        self.target_rope_x = max(min_x, min(max_x, cx))
        self.target_rope_y = max(min_y, min(max_y, cy))

    def release_rope_arrow(self, projectiles: list, particles: list = None, game_map=None):
        """Ao soltar o botão, crava a flecha na posição mirada e puxa Tomoe para lá."""
        if not self.is_alive or not self.is_charging_rope:
            self.is_charging_rope = False
            return
        self.is_charging_rope = False

        min_x = 1.0
        max_x = (game_map.cols - 1.0) if game_map else 20.0
        min_y = 1.0
        max_y = (game_map.rows - 1.0) if game_map else 20.0

        tx = max(min_x, min(max_x, self.target_rope_x))
        ty = max(min_y, min(max_y, self.target_rope_y))

        rope = RopeArrowProjectile(tx, ty, wz=0.25, dir_x=self.facing_x, dir_y=self.facing_y, owner=self, start_latched=True)
        projectiles.append(rope)

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(tx, ty, 0.35))
            for _ in range(4):
                particles.append(SparkParticle(self.wx, self.wy, 0.25))

        self.state = STATE_RECOVERY
        self.state_timer = 0.08
        self.rope_timer = self.rope_cooldown

    def trigger_rope_arrow(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None, game_map=None):
        """
        Ação Secundária: Flecha de Corda direta (compatibilidade com IA e testes).
        """
        if not self.can_act() or self.rope_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.is_charging_rope = True
        self.rope_charge_time = self.rope_charge_duration
        self._calculate_rope_target(game_map)
        self.release_rope_arrow(projectiles, particles, game_map)

    def update(self, dt: float, game_map, particles: list = None, projectiles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.arrow_cooldown_timer > 0:
            self.arrow_cooldown_timer -= dt
        self.update_dodge_timers(dt)

        if self.rope_timer > 0:
            self.rope_timer -= dt

        if self.volley_cooldown_timer > 0:
            self.volley_cooldown_timer = max(0.0, self.volley_cooldown_timer - dt)
            self.sacred_volley_cooldown_timer = self.volley_cooldown_timer
            self.hamaya_cooldown_timer = self.volley_cooldown_timer

        proj_list = projectiles if projectiles is not None else getattr(self, "projectiles_ref", None)
        if self.state == STATE_BOW_DRAW:
            self.draw_timer -= dt
            if self.draw_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.24

                if proj_list is not None:
                    bx = self.wx + self.facing_x * 0.65
                    by = self.wy + self.facing_y * 0.65
                    arrow = KyudoArrowProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
                    proj_list.append(arrow)

                if particles is not None:
                    for _ in range(8):
                        particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.4))

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.is_charging_rope = False
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        # Atualização dos cronômetros e efeitos da Barreira dos Ventos Kami
        if self.ofuda_cooldown_timer > 0:
            self.ofuda_cooldown_timer -= dt
        if self.ofuda_barrier_timer > 0:
            self.ofuda_barrier_timer -= dt
            self.ofuda_orbit_angle += dt * 8.0

    def update_ofuda_barrier_effects(self, dt: float, projectiles: list = None, opponent = None, particles: list = None):
        """Aplica os efeitos de deflexão e repulsão da Barreira Kami."""
        if not self.is_ofuda_active():
            return

        # 1. Defletir / Anular projéteis inimigos
        if projectiles:
            for p in projectiles:
                if getattr(p, "is_active", False) and getattr(p, "owner", None) is not self:
                    if math.hypot(p.wx - self.wx, p.wy - self.wy) < 1.85:
                        p.is_active = False
                        if particles is not None:
                            for _ in range(6):
                                particles.append(SparkParticle(p.wx, p.wy, 0.35))

        # 2. Empurrão / Knockback em oponente melee
        if opponent is not None and getattr(opponent, "is_alive", False):
            d = math.hypot(opponent.wx - self.wx, opponent.wy - self.wy)
            if d < 1.75 and d > 0.001:
                push = 5.0 * dt
                opponent.wx += ((opponent.wx - self.wx) / d) * push
                opponent.wy += ((opponent.wy - self.wy) / d) * push
                if hasattr(opponent, "hitbox_active") and opponent.hitbox_active:
                    opponent.hitbox_active = False

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Arqueiro Kyudo e seu arco Yumi em Voxel 3D."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        # Efeito visual da Barreira dos Ventos Kami (3 Ofudas Sagradas em Órbita)
        if self.is_ofuda_active():
            cx, cy = camera.apply(self.wx, self.wy, 0.6)
            orbit_r = 34
            pygame.draw.circle(surface, (255, 230, 100), (cx, cy), orbit_r, 1)
            for i in range(3):
                ang = self.ofuda_orbit_angle + i * (2.0 * math.pi / 3.0)
                ox = int(cx + orbit_r * math.cos(ang))
                oy = int(cy + (orbit_r * 0.55) * math.sin(ang))
                pygame.draw.rect(surface, (250, 250, 245), (ox - 4, oy - 7, 8, 14), border_radius=1)
                pygame.draw.line(surface, (220, 40, 40), (ox - 2, oy - 4), (ox + 2, oy + 4), 2)

        # 1. Guia Visual Tática de Mira (Hold & Release)
        if self.is_charging_rope and self.is_alive:
            ox, oy = self.wx, self.wy
            tx, ty = self.target_rope_x, self.target_rope_y
            sx_from, sy_from = camera.apply(ox, oy, 0.4)
            sx_to, sy_to = camera.apply(tx, ty, 0.1)

            # Linha pontilhada de corda de cânhamo
            dist_pts = max(4, int(math.hypot(sx_to - sx_from, sy_to - sy_from) / 10))
            for i in range(dist_pts):
                t = i / float(dist_pts)
                px = int(sx_from + (sx_to - sx_from) * t)
                py = int(sy_from + (sy_to - sy_from) * t)
                if i % 2 == 0:
                    pygame.draw.circle(surface, (225, 205, 140), (px, py), 2)

            # Retículo de impacto na posição exata onde a flecha cravará
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.012)
            tgt_radius = int(8 + pulse * 3)
            pygame.draw.circle(surface, (235, 195, 50), (int(sx_to), int(sy_to)), tgt_radius, 2)
            pygame.draw.circle(surface, (255, 60, 50), (int(sx_to), int(sy_to)), 3)
            pygame.draw.line(surface, (235, 195, 50), (int(sx_to) - tgt_radius - 2, int(sy_to)), (int(sx_to) + tgt_radius + 2, int(sy_to)), 1)
            pygame.draw.line(surface, (235, 195, 50), (int(sx_to), int(sy_to) - tgt_radius - 2), (int(sx_to), int(sy_to) + tgt_radius + 2), 1)

            # Barra de carregamento de alcance sobre Tomoe
            bx, by = camera.apply(self.wx, self.wy, 1.45)
            charge_ratio = min(1.0, self.rope_charge_time / self.rope_charge_duration)
            bar_w = 34
            bar_h = 5
            pygame.draw.rect(surface, (24, 20, 22), (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)
            charge_col = (int(255 * charge_ratio + 140 * (1 - charge_ratio)), int(210 * charge_ratio + 120 * (1 - charge_ratio)), 50)
            pygame.draw.rect(surface, charge_col, (bx - bar_w // 2, by, int(bar_w * charge_ratio), bar_h), border_radius=2)
            pygame.draw.rect(surface, COLOR_GOLD, (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), 1, border_radius=2)

        # Retículo de mira de arco sagrado (Mecanismo idêntico à Anne: Selo Shinto Isométrico)
        if getattr(self, "is_aiming_volley", False) and self.is_alive:
            cx, cy = camera.apply(self.volley_target_wx, self.volley_target_wy, 0.0)
            top_x, top_y = camera.apply(self.volley_target_wx, self.volley_target_wy, 4.5)

            # Trajetória balística zenital pontilhada vindo dos céus (idêntico à Anne)
            dash_steps = 7
            for i in range(dash_steps):
                if i % 2 == 0:
                    t1 = i / dash_steps
                    t2 = (i + 1) / dash_steps
                    p1 = (int(top_x + (cx - top_x) * t1), int(top_y + (cy - top_y) * t1))
                    p2 = (int(top_x + (cx - top_x) * t2), int(top_y + (cy - top_y) * t2))
                    pygame.draw.line(surface, (255, 215, 60), p1, p2, 1)

            # Arco parabólico pontilhado conectando a arqueira ao ponto de impacto
            arc_steps = 8
            for i in range(arc_steps):
                if i % 2 == 0:
                    ta = i / arc_steps
                    tb = (i + 1) / arc_steps
                    xa = self.wx + (self.volley_target_wx - self.wx) * ta
                    ya = self.wy + (self.volley_target_wy - self.wy) * ta
                    za = 0.65 * (1.0 - ta) + 4.5 * 4.0 * ta * (1.0 - ta)
                    xb = self.wx + (self.volley_target_wx - self.wx) * tb
                    yb = self.wy + (self.volley_target_wy - self.wy) * tb
                    zb = 0.65 * (1.0 - tb) + 4.5 * 4.0 * tb * (1.0 - tb)
                    pa = camera.apply(xa, ya, za)
                    pb = camera.apply(xb, yb, zb)
                    pygame.draw.line(surface, (255, 235, 120), (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1])), 1)

            rx = int(28 + 3 * math.sin(self.volley_reticle_pulse * 2.0))
            ry = max(10, rx // 2)

            # Brilho suave translúcido no piso sob a mira
            glow_surf = pygame.Surface((rx * 2 + 16, ry * 2 + 16), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 215, 60, 45), (8, 8, rx * 2, ry * 2))
            surface.blit(glow_surf, (cx - rx - 8, cy - ry - 8))

            # Anel externo dourado sagrado
            pygame.draw.ellipse(surface, (255, 215, 60), (cx - rx, cy - ry, rx * 2, ry * 2), 2)

            # Anel interno carmim xintoísta
            rx_in = rx - 7
            ry_in = max(7, rx_in // 2)
            pygame.draw.ellipse(surface, (220, 50, 40), (cx - rx_in, cy - ry_in, rx_in * 2, ry_in * 2), 1)

            # 4 Pontos cardeais do selo sagrado girando suavemente
            rot = self.volley_reticle_pulse * 0.9
            for k in range(4):
                angle = rot + k * (math.pi / 2)
                ox = int(rx * math.cos(angle))
                oy = int(ry * math.sin(angle))
                # Marcadores de luz sagrada na borda
                pygame.draw.circle(surface, (255, 245, 180), (cx + ox, cy + oy), 2)
                # Hastes finas apontando para fora
                out_ox = int((rx + 5) * math.cos(angle))
                out_oy = int((ry + 3) * math.sin(angle))
                pygame.draw.line(surface, (255, 215, 60), (cx + ox, cy + oy), (cx + out_ox, cy + out_oy), 1)

            # Mira central de precisão e rubi sagrado central
            pygame.draw.line(surface, (255, 230, 90), (cx - 7, cy), (cx + 7, cy), 1)
            pygame.draw.line(surface, (255, 230, 90), (cx, cy - 4), (cx, cy + 4), 1)
            pygame.draw.circle(surface, (255, 245, 180), (cx, cy), 3)
            pygame.draw.circle(surface, (220, 40, 30), (cx, cy), 1)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="archer",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"is_drawing": (self.state == STATE_BOW_DRAW or self.is_charging_rope or getattr(self, "is_aiming_volley", False))}
        )

        # Indicador de retesamento do arco Yumi (mira precisa)
        if self.state == STATE_BOW_DRAW:
            bx, by = camera.apply(self.wx, self.wy, 1.35)
            progress = max(0.0, min(1.0, 1.0 - (self.draw_timer / self.draw_duration)))
            bar_w = 32
            bar_h = 5
            pygame.draw.rect(surface, (20, 30, 25), (bx - bar_w // 2 - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)
            pygame.draw.rect(surface, (100, 220, 140), (bx - bar_w // 2, by, int(bar_w * progress), bar_h), border_radius=2)
