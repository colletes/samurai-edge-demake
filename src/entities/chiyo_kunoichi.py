"""
Chiyo (A Kunoichi das Duas Nodachi):
Guerreira shinobi graciosa e letal armada com duas lâminas gigantes Nodachi de 1,60m.
Possui estilo de luta defensivo e evasivo, utilizando a lendária Dança Mai com as
duas nodachi para confundir, defletir projéteis e desferir cortes em tesoura com alcance estendido.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY
)
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle, FloatingBanner

COLOR_CHIYO_AURA = (210, 36, 48)

class ChiyoKunoichi(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Chiyo")
        self.char_type = "chiyo"
        self.speed = 4.8  # Movimentação fluida e evasiva
        self.max_hp = 2
        self.hp = 2

        # Ataque Primário: Corte Duplo Tesoura das Nodachi
        self.scissor_cooldown = 0.40
        self.scissor_timer = 0.0

        # Ação Secundária: Dança Mai com as 2 Kodachi (Esquiva/Parry Dançante de Janela Longa)
        self.mai_dance_cooldown = 2.2        # Cooldown reduzido (era 3.0s)
        self.mai_dance_timer = 0.0
        self.mai_cooldown = 2.2
        self.mai_timer = 0.0
        self.mai_dance_duration = 0.75       # Janela de 0.75s (maior que os 0.45s do Musashi)
        self.mai_whiff_recovery = 0.18       # Exaustão calibrada (era 0.45s) para punição justa sem morte garantida
        self.mai_active = False
        self.mai_parried_anything = False
        self.mai_exhausted = False
        self.mai_counter_ready = False
        self.mai_spin_angle = 0.0
        self.dance_dir_x = 1.0
        self.dance_dir_y = 0.0

        # Esquiva ágil
        self.is_agile_dodge = True
        self.roll_speed = 9.2
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.14
        self.roll_cooldown_duration = 0.35
        self.recovery_duration = 0.26

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and not getattr(self, "mai_exhausted", False)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_kodachi_strike(self, target_wx: float, target_wy: float):
        """Ataque Primário: Corte Cruzado com as 2 Kodachi (Lâminas Curtas Duplas)."""
        if not self.can_act() or self.scissor_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.combo_step = (getattr(self, "combo_step", 0) % 3) + 1
        self.state = STATE_ATTACK
        self.state_timer = 0.14
        self.hitbox_active = True
        self.hitbox_radius = 1.50  # Alcance ampliado (era 1.25m)
        self.hitbox_damage = 2     # Golpe letal
        self.slash_dir = (self.facing_x, self.facing_y)
        # Passo ágil e agressivo com as lâminas curtas (0.35m)
        self.wx += self.facing_x * 0.35
        self.wy += self.facing_y * 0.35
        self.hitbox_center = (self.wx + self.facing_x * 0.90, self.wy + self.facing_y * 0.90)
        self.scissor_timer = self.scissor_cooldown

    def trigger_primary_attack(self, target_wx: float, target_wy: float):
        self.trigger_kodachi_strike(target_wx, target_wy)

    trigger_scissor_strike = trigger_kodachi_strike
    trigger_scissor_slash = trigger_kodachi_strike

    def trigger_mai_dance(self, target_wx: float = None, target_wy: float = None, opponent=None, projectiles: list = None, particles: list = None, banners: list = None):
        """
        Ação Secundária: Dança Mai das Duas Kodachi (Parry/Esquiva Dançante).
        - Janela longa de 0.75s (maior que os 0.45s do Musashi) em pirueta contínua de 360°.
        - Apara ataques corpo a corpo (respondendo com um corte de raspão de 1 HP + recuo) e reflete projéteis.
        - Desvantagem: Se a dança terminar no vazio sem aparar nenhum golpe/projétil, Chiyo fica
          sem fôlego por 0.45s (exaustão vulnerável e lenta).
        """
        if not self.can_act() or self.mai_dance_timer > 0:
            return

        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)
        self.mai_dance_timer = self.mai_dance_cooldown
        self.state = "MAI_DANCE"
        self.state_timer = self.mai_dance_duration
        self.is_invulnerable_dodge = False  # Permite interceptar ataques no sistema de colisão como Parry Dançante
        self.mai_active = True
        self.mai_parried_anything = False
        self.mai_exhausted = False
        self.mai_counter_ready = False
        self.mai_spin_angle = 0.0
        # Deslize lateral/diagonal gracioso de dança
        self.dance_dir_x = self.facing_x * 0.65 - self.facing_y * 0.75
        self.dance_dir_y = self.facing_y * 0.65 + self.facing_x * 0.75
        self.hitbox_active = False
        self.hitbox_radius = 1.30
        self.hitbox_damage = 1
        self.hitbox_center = (self.wx, self.wy)

        if banners is not None:
            banners.append(FloatingBanner("DANÇA MAI!", self.wx, self.wy - 0.6, wz=1.7, color=COLOR_CHIYO_AURA))

        # Partículas de pétalas de Higanbana e faíscas escarlates
        if particles is not None:
            for _ in range(18):
                ang = random.uniform(0, math.pi * 2)
                particles.append(SparkParticle(self.wx + math.cos(ang) * 0.45, self.wy + math.sin(ang) * 0.45, 0.38, color=(215, 38, 52)))

        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.SWORD_CLASH)
        except Exception:
            pass

        # Defletir projéteis já próximos no instante inicial do giro
        if projectiles is not None:
            for proj in projectiles:
                if getattr(proj, "owner", None) != self and getattr(proj, "is_active", getattr(proj, "active", True)):
                    dx = proj.wx - self.wx
                    dy = proj.wy - self.wy
                    if math.hypot(dx, dy) <= 1.85:
                        proj.vx = -proj.vx * 1.2
                        proj.vy = -proj.vy * 1.2
                        if hasattr(proj, "dir_x"):
                            proj.dir_x = -proj.dir_x
                            proj.dir_y = -proj.dir_y
                        proj.owner = self
                        self.on_mai_parry_success()

    def on_mai_parry_success(self, attacker=None, game_map=None):
        """Chamado quando a Dança Mai apara um ataque ou reflete um projétil com sucesso."""
        self.mai_parried_anything = True
        self.mai_counter_ready = True
        self.mai_exhausted = False
        # Encerra o giro suavemente após o contra-corte e reduz o cooldown como recompensa
        self.state_timer = min(self.state_timer, 0.20)
        self.mai_dance_timer = max(0.9, self.mai_dance_timer - 1.2)
        if attacker is not None and game_map is not None:
            # Passo de seda: desliza graciosamente para fora da linha de ataque
            glide_x = -self.facing_y * 0.65 - self.facing_x * 0.35
            glide_y = self.facing_x * 0.65 - self.facing_y * 0.35
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + glide_x))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + glide_y))

    def trigger_secondary_action(self, target_wx: float = None, target_wy: float = None, opponent=None, projectiles: list = None, particles: list = None, banners: list = None):
        self.trigger_mai_dance(target_wx, target_wy, opponent=opponent, projectiles=projectiles, particles=particles, banners=banners)

    trigger_nodachi_mai = trigger_mai_dance

    def update(self, dt: float, game_map, particles: list = None, banners: list = None, opponent=None, **kwargs):
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)
        self.update_pit(dt, game_map, particles, banners)

        if self.scissor_timer > 0:
            self.scissor_timer = max(0.0, self.scissor_timer - dt)

        if self.mai_dance_timer > 0:
            self.mai_dance_timer = max(0.0, self.mai_dance_timer - dt)
        self.mai_timer = self.mai_dance_timer

        if self.state in (STATE_ATTACK, "SCISSOR_SLASH"):
            self.state_timer -= dt
            step = 3.6 * dt
            new_wx = self.wx + self.facing_x * step
            new_wy = self.wy + self.facing_y * step
            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85)
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.mai_exhausted = False

        # Coreografia contínua da Dança Mai (0.75s)
        elif self.state == "MAI_DANCE":
            self.state_timer -= dt
            progress = 1.0 - max(0.0, self.state_timer / max(0.01, self.mai_dance_duration))
            # Duas piruetas completas (720 graus) ao longo da dança
            self.mai_spin_angle = progress * math.pi * 4.0

            # Deslize bailado em curva suave
            curve_vx = self.dance_dir_x * math.cos(progress * math.pi) * 1.85
            curve_vy = self.dance_dir_y * math.cos(progress * math.pi) * 1.85
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + curve_vx * dt))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + curve_vy * dt))
            self.hitbox_center = (self.wx, self.wy)

            if particles is not None and random.random() < 0.55:
                p_ang = self.mai_spin_angle + random.uniform(-0.4, 0.4)
                px = self.wx + math.cos(p_ang) * 0.55
                py = self.wy + math.sin(p_ang) * 0.55
                particles.append(SparkParticle(px, py, 0.32, color=(215, 36, 52)))

            if self.state_timer <= 0:
                self.is_invulnerable_dodge = False
                self.mai_active = False
                self.mai_spin_angle = 0.0
                if not self.mai_parried_anything:
                    # Desvantagem compensatória: Dançou no vazio -> perde o fôlego e fica vulnerável!
                    self.state = STATE_RECOVERY
                    self.state_timer = self.mai_whiff_recovery
                    self.mai_exhausted = True
                    self.apply_slow(self.mai_whiff_recovery + 0.15)
                    if banners is not None:
                        banners.append(FloatingBanner("SEM FÔLEGO!", self.wx, self.wy - 0.5, wz=1.6, color=(235, 165, 90)))
                else:
                    self.state = STATE_IDLE
                    self.mai_exhausted = False

        elif self.state == STATE_ROLL:
            self.update_roll(dt, game_map)

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            self.mai_exhausted = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera, shadow: bool = True):
        # Efeito visual de fitas e pétalas giratórias durante a Dança Mai
        if self.state == "MAI_DANCE":
            cx, cy = camera.apply(self.wx, self.wy, 0.3)
            zoom = getattr(camera, "zoom", 1.0)
            r_px = int(36 * zoom)
            vortex_surf = pygame.Surface((r_px * 2 + 16, r_px * 2 + 16), pygame.SRCALPHA)
            center = (r_px + 8, r_px + 8)
            pygame.draw.circle(vortex_surf, (215, 38, 52, 125), center, r_px, 2)
            pygame.draw.circle(vortex_surf, (255, 130, 145, 95), center, max(1, int(r_px * 0.72)), 1)
            # Pétalas orbitais de Higanbana acompanhando o giro
            for i in range(4):
                a = self.mai_spin_angle + i * (math.pi / 2.0)
                px_orb = int(center[0] + math.cos(a) * r_px * 0.88)
                py_orb = int(center[1] + math.sin(a) * r_px * 0.55)
                pygame.draw.circle(vortex_surf, (240, 45, 62, 195), (px_orb, py_orb), max(2, int(4 * zoom)))
            surface.blit(vortex_surf, (cx - center[0], cy - center[1]))

        # Durante a Dança Mai, gira a orientação visual em 360° para esculpir a pirueta
        vis_fx, vis_fy = self.facing_x, self.facing_y
        if self.state == "MAI_DANCE":
            ca = math.cos(self.mai_spin_angle)
            sa = math.sin(self.mai_spin_angle)
            vis_fx = self.facing_x * ca - self.facing_y * sa
            vis_fy = self.facing_x * sa + self.facing_y * ca

        render_voxel_humanoid(
            surface, camera, self.wx, self.wy, self.wz,
            vis_fx, vis_fy, self.state, self.state_timer,
            self.is_alive, char_type="chiyo", walk_timer=self.walk_cycle,
            alpha=self.alpha, is_moving=self.is_moving,
            extra_props={
                "combo_step": getattr(self, "combo_step", 3),
                "mai_spin_angle": getattr(self, "mai_spin_angle", 0.0),
                "mai_exhausted": getattr(self, "mai_exhausted", False),
            }
        )

    render_voxel = render

