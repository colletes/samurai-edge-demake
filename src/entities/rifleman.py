"""
Rifleman (Tanegashima Teppo — Fase 2 Overhaul):
- Mestre atirador da infantaria Ashigaru armado com arcabuz feudal de mecha.
- Golpe Primário: Tiro fatal de longo alcance (26 m/s, 1-Hit Kill) quando municiado.
  Se descarregado, desfere a Coronhada Pesada de Carvalho (Rifle Butt Smash) que atordoa (0.65s) e afasta o rival.
- Ação Secundária Dedicada: Black Powder Ground Trap (Mina de pólvora negra para zoneamento contra espadachins).
- Terceira Ação: Trench Ashigaru Dive (Mergulho corporal de trincheira com i-frames completos que conclui a recarga fluida de emergência).
- Recarga Tática: Automática por vareta de ferro (ramrod) ou instantânea ao concluir a esquiva de trincheira.
- Suporte a Pose LERP 0.08s e SSAA 2x Offscreen.
"""
import math
import random
import pygame
from src.config import (
    COLOR_RIFLE_COAT, COLOR_RIFLE_HAT, COLOR_RIFLE_AURA, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import MusketBulletProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_BACKSTEP = "BACKSTEP"
STATE_RIFLE_ROLL = "RIFLE_ROLL"
STATE_RIFLE_AIM = "RIFLE_AIM"

class PowderTrap:
    """Mina terrestre de pólvora negra (Taru de Pólvora) que detona ao contato de rivais ou disparos."""
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.05
        self.owner = owner
        self.radius = 0.85
        self.trigger_radius = 0.85
        self.max_blast_radius = 1.65
        self.lifetime = 12.0
        self.is_ignited = False
        self.blast_timer = 0.0
        self.blast_duration = 0.42
        self.is_active = True
        self.has_dealt_damage = False

    def detonate(self, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None):
        """Detonação imediata do barril: gera onda de choque hemisférica e causa dano de área."""
        if self.is_ignited:
            return
        self.is_ignited = True
        self.blast_timer = 0.0

        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.EXPLOSION, volume_scale=1.0)
        except Exception:
            pass

        if banners is not None:
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("KEG DETONATED!", self.wx, self.wy, wz=1.4, color=(255, 120, 30), duration=1.2))

        if particles is not None:
            from src.effects.particles import SparkParticle, SmokeParticle
            for _ in range(22):
                particles.append(SparkParticle(self.wx, self.wy, 0.45, color=(255, random.randint(110, 230), 30)))
            for _ in range(8):
                particles.append(SmokeParticle(self.wx, self.wy, 0.35, color=(65, 55, 50), size=6))

        # Dano imediato na área ao detonar
        if fighters and not self.has_dealt_damage:
            self.has_dealt_damage = True
            for f in fighters:
                if f is not self.owner and getattr(f, "is_alive", False):
                    if math.hypot(f.wx - self.wx, f.wy - self.wy) < (self.max_blast_radius + getattr(f, "radius", 0.45)):
                        hit, dead = f.take_hit((0.0, 0.0), damage=2)
                        if dead and cinematic_director:
                            cinematic_director.trigger_fatal_strike(self.owner, f, "HAYAGO_KEG_BLAST", (0, 0))

    def ignite(self, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None):
        """Alias de detonação para compatibilidade."""
        self.detonate(fighters=fighters, particles=particles, banners=banners, cinematic_director=cinematic_director)

    def update(self, dt: float, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None, projectiles: list = None) -> bool:
        if not self.is_ignited:
            self.lifetime -= dt
            if self.lifetime <= 0:
                self.is_active = False
                return False

            # 1. Se o rival pisar na área da mina, detona automaticamente!
            if fighters:
                for f in fighters:
                    if f is not self.owner and getattr(f, "is_alive", False):
                        if math.hypot(f.wx - self.wx, f.wy - self.wy) < (self.trigger_radius + getattr(f, "radius", 0.45)):
                            self.detonate(fighters, particles, banners, cinematic_director)
                            break

            # 2. Se alvejada por qualquer projétil (bala, flecha, kunai, bomba), detona imediatamente!
            if not self.is_ignited and projectiles:
                for pr in projectiles:
                    if getattr(pr, "is_active", False):
                        pr_rad = getattr(pr, "radius", 0.35)
                        if math.hypot(pr.wx - self.wx, pr.wy - self.wy) < (self.trigger_radius + pr_rad):
                            pr.is_active = False  # Projétil colide e detona o barril
                            self.detonate(fighters, particles, banners, cinematic_director)
                            break
        else:
            # Em expansão explosiva hemisférica
            self.blast_timer += dt
            if particles is not None and random.random() < 0.50:
                from src.effects.particles import SparkParticle
                particles.append(SparkParticle(self.wx, self.wy, 0.4, color=(255, 140, 40)))

            # Checar combatentes que porventura entrem na hemisfera enquanto ela se expande
            if fighters and not self.has_dealt_damage:
                prog = min(1.0, self.blast_timer / max(0.001, self.blast_duration))
                cur_r = self.max_blast_radius * (1.0 - (1.0 - prog) ** 3)
                for f in fighters:
                    if f is not self.owner and getattr(f, "is_alive", False):
                        if math.hypot(f.wx - self.wx, f.wy - self.wy) < (cur_r + getattr(f, "radius", 0.45)):
                            self.has_dealt_damage = True
                            hit, dead = f.take_hit((0.0, 0.0), damage=2)
                            if dead and cinematic_director:
                                cinematic_director.trigger_fatal_strike(self.owner, f, "HAYAGO_KEG_BLAST", (0, 0))

            if self.blast_timer >= self.blast_duration:
                self.is_active = False
                return False
        return self.is_active

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box

        ticks = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(ticks * 0.009)

        if not self.is_ignited:
            # Sombra suave no chão
            base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
            pygame.draw.ellipse(surface, (14, 18, 16), (base_sx - 16, base_sy - 8, 32, 16))

            # Efeito de brilho de solo sutil (aura militar feudal da mina armada)
            ground_glow_rad = int(12 + pulse * 4)
            ground_glow = pygame.Surface((ground_glow_rad * 2, ground_glow_rad * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(ground_glow, (255, 140, 30, int(30 + pulse * 25)), (0, ground_glow_rad // 2, ground_glow_rad * 2, ground_glow_rad))
            surface.blit(ground_glow, (base_sx - ground_glow_rad, base_sy - ground_glow_rad // 2))

            # -----------------------------------------------------------------
            # MODELO VOXEL 3D: BARRIL FEUDAL DE PÓLVORA NEGRA (TARU DE PÓLVORA)
            # -----------------------------------------------------------------
            # 1. Aro inferior de ferro forjado
            draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.20, 0.0, 0.40, 0.40, 0.08, (38, 42, 46))
            # 2. Corpo do barril em madeira escura tratada
            draw_voxel_box(surface, camera, self.wx - 0.23, self.wy - 0.23, 0.07, 0.46, 0.46, 0.20, (82, 48, 26))
            # 3. Faixa central carmesim de pólvora militar feudal (com selo de fogo)
            draw_voxel_box(surface, camera, self.wx - 0.24, self.wy - 0.24, 0.14, 0.48, 0.48, 0.07, (175, 40, 32))
            # 4. Aro superior de ferro forjado
            draw_voxel_box(surface, camera, self.wx - 0.20, self.wy - 0.20, 0.26, 0.40, 0.40, 0.07, (38, 42, 46))
            # 5. Tampa de madeira do barril
            draw_voxel_box(surface, camera, self.wx - 0.17, self.wy - 0.17, 0.32, 0.34, 0.34, 0.05, (95, 58, 32))
            # 6. Batoque / Pavio trançado de corda com queima
            draw_voxel_box(surface, camera, self.wx - 0.035, self.wy - 0.035, 0.37, 0.07, 0.07, 0.09, (190, 150, 90))
            # 7. Brasa no topo do pavio (ponto quente ativo e faiscante)
            ember_c = (255, int(140 + pulse * 80), 30)
            draw_voxel_box(surface, camera, self.wx - 0.025, self.wy - 0.025, 0.45, 0.05, 0.05, 0.05, ember_c, outline=False)

            # Faísca sutil flutuante da brasa
            fsx, fsy = camera.apply(self.wx, self.wy, 0.52)
            pygame.draw.circle(surface, (255, 200, 70), (fsx, int(fsy - pulse * 3)), 2)
        else:
            # -----------------------------------------------------------------
            # ONDA DE CHOQUE 3D EM FORMA DE HEMISFERA EM EXPANSÃO (EXPLOSION DOME)
            # -----------------------------------------------------------------
            prog = min(1.0, self.blast_timer / max(0.001, self.blast_duration))
            # Curva de expansão explosiva rápida (ease-out cubic)
            exp = 1.0 - (1.0 - prog) ** 3
            cur_r = max(0.20, self.max_blast_radius * exp)
            cur_h = cur_r * 0.90
            alpha = int(255 * max(0.0, 1.0 - prog ** 1.3))

            apex_sx, apex_sy = camera.apply(self.wx, self.wy, cur_h)

            num_pts = 16
            angles = [(i / num_pts) * (math.pi * 2.0) for i in range(num_pts)]

            # A. Anel de Solo (Ground Blast Ring, z=0)
            ground_pts = [camera.apply(self.wx + math.cos(a) * cur_r, self.wy + math.sin(a) * cur_r, 0.0) for a in angles]
            if len(ground_pts) >= 3 and alpha > 0:
                surf_base = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
                poly_color = (255, 120, 20, max(0, min(140, int(alpha * 0.55))))
                pygame.draw.polygon(surf_base, poly_color, ground_pts)
                surface.blit(surf_base, (0, 0))
                pygame.draw.polygon(surface, (255, 190, 40), ground_pts, 3)

            # B. Anel Médio da Hemisfera (Mid-Latitude Ring, z=cur_h * 0.55, r=cur_r * 0.835)
            mid_r = cur_r * 0.835
            mid_z = cur_h * 0.55
            mid_pts = [camera.apply(self.wx + math.cos(a) * mid_r, self.wy + math.sin(a) * mid_r, mid_z) for a in angles]
            if len(mid_pts) >= 3:
                pygame.draw.polygon(surface, (255, 150, 30), mid_pts, 2)

            # C. Anel Superior da Hemisfera (High-Latitude Ring, z=cur_h * 0.85, r=cur_r * 0.527)
            high_r = cur_r * 0.527
            high_z = cur_h * 0.85
            high_pts = [camera.apply(self.wx + math.cos(a) * high_r, self.wy + math.sin(a) * high_r, high_z) for a in angles]
            if len(high_pts) >= 3:
                pygame.draw.polygon(surface, (255, 210, 60), high_pts, 2)

            # D. Arcos Meridianos Verticais da Cúpula (4 arcos cruzando o zênite)
            for arc_ang in (0.0, math.pi * 0.25, math.pi * 0.50, math.pi * 0.75):
                arc_pts = []
                for step in range(9):
                    t = (step / 8.0) * math.pi
                    rad_t = cur_r * math.cos(t)
                    z_t = cur_h * math.sin(t)
                    pt = camera.apply(self.wx + math.cos(arc_ang) * rad_t, self.wy + math.sin(arc_ang) * rad_t, z_t)
                    arc_pts.append(pt)
                if len(arc_pts) >= 2:
                    pygame.draw.lines(surface, (255, 175, 40), False, arc_pts, 2)

            # E. Núcleo incandescente e clarão de ápice
            if prog < 0.35:
                flash_r = int(18 * (1.0 - prog / 0.35))
                pygame.draw.circle(surface, (255, 255, 230), (apex_sx, apex_sy), flash_r)
                pygame.draw.circle(surface, (255, 200, 60), (apex_sx, apex_sy), flash_r + 4, 2)
            else:
                pygame.draw.circle(surface, (255, 180, 50), (apex_sx, apex_sy), 4)


class Rifleman(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Teppo")
        self.char_type = "teppo"
        self.speed = 3.85  # Velocidade ágil e calibrada de veterano Ashigaru

        # Mecânica de Munição e Pólvora
        self.has_ammo = True           # Inicia CARREGADO com munição
        self.cocking_timer = 0.35      # Delay de armação de cão antes do tiro no início do round
        self.reload_cooldown = 1.30    # Recarga por vareta calibrada para janela de aproximação justa
        self.reload_timer = 0.0
        self.is_reloading = False
        self.reload_progress = 0.0

        # Mecânica de Mira (Windup antes do disparo para permitir esquiva)
        self.aim_duration = 0.22       # Calibrado: telegraph claro da queima da mecha antes do disparo
        self.target_aim_wx = 0.0
        self.target_aim_wy = 0.0
        self.pending_projectiles = None
        self.pending_particles = None

        # Subterfúgio Evasivo
        self.backstep_cooldown = 0.60
        self.backstep_timer = 0.0
        self.backstep_duration = 0.20

        # Ação Secundária: Armadilha de Pólvora (Zoneamento tático)
        self.trap_cooldown = 4.5
        self.trap_timer = 0.0
        self.active_trap = None

        # Terceira Ação: Trench Ashigaru Dive (Mergulho de trincheira com recarga fluida ao levantar)
        self.is_agile_dodge = True
        self.roll_speed = 8.5
        self.roll_duration = 0.28
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.25
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0

        # Coronhada de carvalho
        self.is_rifle_butt = False
        self.attack_duration = 0.20

        # Rastreador de Pose LERP 0.08s
        self.pose_lerp_tracker = {
            "lerp_duration": 0.08,
            "blend_timer": 0.0,
            "pose_key": None,
            "prev_snap": None,
            "last_snap": None,
            "transitions_count": 0,
        }

    def trigger_attack(self, target_wx: float, target_wy: float, projectiles: list = None, particles: list = None) -> bool:
        """
        Ataque Primário Inteligente:
        - Se municiado: mira rápida e disparo de arcabuz supersônico a 26 m/s.
        - Se descarregado: desfere a Coronhada Pesada de Carvalho (Rifle Butt Smash) com knockback de 1.8m e stun de 0.65s.
        """
        if not self.can_act():
            return False

        if self.has_ammo and self.cocking_timer <= 0:
            return self.trigger_shoot(target_wx, target_wy, projectiles, particles)
        else:
            return self.trigger_rifle_butt(target_wx, target_wy, particles)

    def trigger_secondary(self, target_wx: float = 0.0, target_wy: float = 0.0, traps: list = None, particles: list = None) -> bool:
        """Ação Secundária: Black Powder Ground Trap (Planta a mina de zoneamento no solo)."""
        return self.trigger_powder_trap(target_wx, target_wy, traps, particles)

    def trigger_trench_dive(self, dir_x: float, dir_y: float, particles: list = None) -> bool:
        """Alias para o Mergulho de Trincheira Ashigaru."""
        return self.trigger_roll(dir_x, dir_y, particles)

    def trigger_powder_trap(self, target_wx: float = 0.0, target_wy: float = 0.0, traps: list = None, particles: list = None):
        """Ação Secundária: Black Powder Ground Trap — arma mina no solo para controlar aproximação."""
        if not self.can_act() or self.trap_timer > 0:
            return False
        if self.active_trap is not None and getattr(self.active_trap, "is_active", False):
            return False
        self.trap_timer = self.trap_cooldown

        trap_list = traps
        if isinstance(target_wx, list):
            trap_list = target_wx
        elif isinstance(target_wy, list):
            trap_list = target_wy

        if trap_list is not None:
            new_trap = PowderTrap(self.wx, self.wy, owner=self)
            self.active_trap = new_trap
            trap_list.append(new_trap)
        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.40))
        return True

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Terceira Ação: Trench Ashigaru Dive — mergulho corporal rasante com recarga ao concluir."""
        if (
            not self.is_alive
            or self.state in (STATE_RIFLE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK)
            or self.roll_recovery_timer > 0
            or self.roll_cooldown_timer > 0
            or self.dash_recovery_timer > 0
        ):
            return False

        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = self.facing_x, self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.state = STATE_RIFLE_ROLL
        self.state_timer = self.roll_duration
        self.roll_dir_x = dir_x
        self.roll_dir_y = dir_y
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.hitbox_active = False

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.35, color=(165, 140, 110)))
        return True

    def trigger_tumble_roll(self, dir_x: float, dir_y: float, particles: list = None):
        return self.trigger_roll(dir_x, dir_y, particles)

    def check_powder_pickup(self, pouches: list, particles: list = None) -> bool:
        """Compatibilidade: recarga instantânea ao passar por munição se descarregado."""
        if self.has_ammo or not self.is_alive:
            return False
        for pouch in pouches:
            if getattr(pouch, "is_active", False):
                if math.hypot(self.wx - pouch.wx, self.wy - pouch.wy) < (pouch.radius + self.radius + 0.25):
                    pouch.is_active = False
                    pouch.wx = -999.0
                    pouch.wy = -999.0
                    pouch.respawn_timer = 10.0
                    self.has_ammo = True
                    self.cocking_timer = 0.25
                    if particles is not None:
                        for _ in range(14):
                            particles.append(SparkParticle(self.wx, self.wy, 0.6))
                    return True
        return False

    def on_round_start(self):
        """Inicia o round carregado com sutil atraso para evitar disparo no primeiro frame."""
        self.has_ammo = True
        self.cocking_timer = 0.40

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_RIFLE_AIM)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_shoot(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None, immediate: bool = False):
        """Ataque Primário: Aponta o arcabuz em mira e aguarda queima da mecha antes do disparo fatal."""
        if not self.can_act():
            return False

        if not self.has_ammo or self.cocking_timer > 0:
            if not self.has_ammo:
                return self.trigger_rifle_butt(target_wx, target_wy, particles)
            return False

        self.set_facing(target_wx, target_wy)

        if immediate:
            self._fire_musket(target_wx, target_wy, projectiles, particles)
            return True

        self.state = STATE_RIFLE_AIM
        self.state_timer = self.aim_duration
        self.target_aim_wx = target_wx
        self.target_aim_wy = target_wy
        self.pending_projectiles = projectiles
        self.pending_particles = particles

        if particles is not None:
            px = self.wx + self.facing_x * 0.45
            py = self.wy + self.facing_y * 0.45
            for _ in range(6):
                particles.append(SparkParticle(px, py, 0.40, color=(255, 180, 50)))
        return True

    def _fire_musket(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """Disparo efetivo da bala de arcabuz supersônica após a conclusão da mira."""
        if not self.has_ammo or not self.is_alive:
            return

        self.set_facing(target_wx, target_wy)
        self.has_ammo = False
        self.reload_timer = self.reload_cooldown
        self.is_reloading = False
        self.reload_progress = 0.0

        self.state = STATE_RECOVERY
        self.state_timer = 0.32        # Recuo e recuperação pós-tiro (whiff punish balanceado)

        # Recuo da pólvora
        self.wx -= self.facing_x * 0.35
        self.wy -= self.facing_y * 0.35

        # Projétil supersônico balístico
        bx = self.wx + self.facing_x * 0.65
        by = self.wy + self.facing_y * 0.65
        bullet = MusketBulletProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
        if projectiles is not None:
            projectiles.append(bullet)

        if particles is not None:
            for _ in range(16):
                particles.append(SparkParticle(bx, by, 0.55))

        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.TANEGASHIMA_SHOT, volume_scale=1.0)
        except Exception:
            pass

    def trigger_rifle_butt(self, target_wx: float, target_wy: float, particles: list = None):
        """Coronhada de Carvalho: Golpe pesado que atordoa (0.65s) e empurra o adversário 1.8m para trás."""
        if not self.can_act():
            return False
        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_radius = 1.35
        self.is_rifle_butt = True
        self.hitbox_center = (self.wx + self.facing_x * 0.70, self.wy + self.facing_y * 0.70)
        self.slash_dir = (self.facing_x, self.facing_y)
        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.SWING_BLUNT, volume_scale=0.90)
        except Exception:
            pass
        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.35))
        return True

    def trigger_reload_hold(self):
        """Suporte a recarga manual mantida se desejado."""
        if not self.can_act() or self.has_ammo:
            return
        self.is_reloading = True

    def trigger_evasive_backstep(self, particles: list = None):
        """Subterfúgio: Salto evasivo recuado."""
        if not self.is_alive or self.backstep_timer > 0:
            return
        self.backstep_timer = self.backstep_cooldown
        self.state = STATE_BACKSTEP
        self.state_timer = self.backstep_duration
        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.3))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)

        if self.backstep_timer > 0:
            self.backstep_timer -= dt
        if self.trap_timer > 0:
            self.trap_timer -= dt
        if self.cocking_timer > 0:
            self.cocking_timer -= dt

        # Recarga fluida automática com animação de vareta
        if not self.has_ammo:
            self.reload_timer -= dt
            self.reload_progress = max(0.0, min(1.0, 1.0 - (self.reload_timer / max(0.001, self.reload_cooldown))))
            if self.reload_timer <= 0:
                self.has_ammo = True
                self.cocking_timer = 0.15
                self.reload_progress = 0.0
                if particles is not None:
                    for _ in range(8):
                        particles.append(SparkParticle(self.wx, self.wy, 0.45, color=(255, 210, 80)))
                try:
                    from src.audio import play_sfx, SoundEvent
                    play_sfx(SoundEvent.PARRY, volume_scale=0.35)
                except Exception:
                    pass

        # Atualiza timer do blend LERP
        if self.pose_lerp_tracker["blend_timer"] > 0:
            self.pose_lerp_tracker["blend_timer"] = max(0.0, self.pose_lerp_tracker["blend_timer"] - dt)

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.hitbox_active = False
                self.is_rifle_butt = False

        elif self.state == STATE_RIFLE_ROLL:
            self.state_timer -= dt
            step = self.roll_speed * dt
            new_wx = self.wx + self.roll_dir_x * step
            new_wy = self.wy + self.roll_dir_y * step

            if particles is not None and random.random() < 0.65:
                particles.append(SparkParticle(self.wx, self.wy, 0.04, color=(160, 135, 100)))

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_invulnerable_dodge = False
                self.roll_recovery_timer = self.roll_recovery_duration
                self.roll_cooldown_timer = self.roll_cooldown_duration
                self.dash_recovery_timer = self.roll_cooldown_duration
                # Mergulho de trincheira conclui recarga imediatamente!
                if not self.has_ammo:
                    self.has_ammo = True
                    self.cocking_timer = 0.25
                    self.reload_progress = 0.0
                    if particles is not None:
                        for _ in range(12):
                            particles.append(SparkParticle(self.wx, self.wy, 0.45))

        elif self.state == STATE_BACKSTEP:
            self.state_timer -= dt
            step = 7.5 * dt
            new_wx = self.wx - self.facing_x * step
            new_wy = self.wy - self.facing_y * step
            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True
            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RIFLE_AIM:
            self.state_timer -= dt
            if particles is not None and random.random() < 0.40:
                px = self.wx + self.facing_x * 0.60
                py = self.wy + self.facing_y * 0.60
                particles.append(SparkParticle(px, py, 0.35, color=(255, 160, 40)))

            if self.state_timer <= 0:
                self._fire_musket(
                    self.target_aim_wx,
                    self.target_aim_wy,
                    self.pending_projectiles,
                    particles or self.pending_particles
                )

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza Teppo com SSAA 2x, Pose LERP e indicador de mira/munição."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        # Indicador visual brilhante no cano quando em mira
        if self.state == STATE_RIFLE_AIM:
            mx, my = camera.apply(self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85, 0.58)
            pygame.draw.circle(surface, (255, 220, 60), (mx, my), 5)
            pygame.draw.circle(surface, (255, 255, 255), (mx, my), 2)

        # Determinar pose semântica e cinemática 3D para renderizador
        pose_name = ""
        pose_p = 0.0
        roll_prog = 0.0
        somersault_angle = 0.0
        somersault_pivot_z = self.wz + 0.24
        render_wz = self.wz

        if self.state == STATE_RIFLE_AIM:
            pose_name = "ready_aim"
            pose_p = 1.0 - (self.state_timer / max(0.001, self.aim_duration))
        elif self.state == STATE_ATTACK:
            pose_name = "rifle_butt" if self.is_rifle_butt else "aim_shoot"
            pose_p = 1.0 - (self.state_timer / max(0.001, self.attack_duration))
        elif self.state == STATE_RIFLE_ROLL:
            pose_name = "trench_dive"
            roll_prog = max(0.0, min(1.0, 1.0 - (self.state_timer / max(0.001, self.roll_duration))))
            pose_p = roll_prog
            # Rotação fluida 360° em torno do eixo transversal de pitch
            somersault_angle = -360.0 * roll_prog
            # Mergulho rasante ao solo no meio do rolamento
            if roll_prog < 0.30:
                dip = (roll_prog / 0.30) * 0.14
            elif roll_prog < 0.70:
                dip = 0.14
            else:
                dip = (1.0 - (roll_prog - 0.70) / 0.30) * 0.14
            render_wz = max(0.0, self.wz - dip)
        elif not self.has_ammo and self.state == STATE_IDLE:
            pose_name = "ramrod_reload"
            pose_p = self.reload_progress

        extra_props = {
            "ssaa_2x": True,
            "has_ammo": self.has_ammo,
            "is_reloading": (not self.has_ammo and self.state == STATE_IDLE),
            "is_rifle_butt": self.is_rifle_butt,
            "pose": pose_name,
            "p": pose_p,
            "pose_lerp_tracker": self.pose_lerp_tracker,
            "somersault_angle": somersault_angle,
            "somersault_pivot_z": somersault_pivot_z,
            "is_roll": (self.state == STATE_RIFLE_ROLL),
            "roll_prog": roll_prog,
        }

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, render_wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="teppo",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props=extra_props
        )

        # Indicador de Munição sutil acima da Jingasa
        bx, by = camera.apply(self.wx, self.wy, 1.45)
        if self.has_ammo:
            pygame.draw.circle(surface, COLOR_GOLD, (bx, by), 4)
            pygame.draw.circle(surface, (255, 255, 200), (bx - 1, by - 1), 2)
        else:
            # Anel cinza indicando recarga de pólvora com progresso circular
            pygame.draw.circle(surface, (140, 50, 50), (bx, by), 4, 1)
