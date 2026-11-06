"""
Chiyo (A Kunoichi das Sombras — Kodachi Dupla):
Guerreira shinobi graciosa e letal armada com duas espadas curtas Kodachi em pegada invertida (Gyakute).
Possui estilo de luta hiper-ágil e evasivo:
- Golpe Primário: Twin Kodachi Cross Slice (Cruzamento rápido em 'X' das duas kodachis, decapitação em tesoura).
- Golpe Secundário: Híbrido Dança Mai + Avanço (Twin Blade Acrobat Lunge — Giro evasivo que se transforma em salto perfurante de 3.2m).
- Terceira Ação (Esquiva): Shadow Step Slip (Deslize rasteiro rente ao chão com 14 i-frames, rastro de sombras e pétalas de Higanbana).
- Finishers Bespoke: Triple Scissor Cleave (双刃十字) e Shadow Lotus Flurry (影蓮乱舞).
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
from src.i18n import t

COLOR_CHIYO_AURA = (210, 36, 48)
COLOR_HIGANBANA = (220, 32, 45)


class ChiyoKunoichi(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Chiyo")
        self.char_type = "chiyo"
        self.speed = 5.1  # Movimentação hiper-ágil e evasiva de kunoichi
        self.max_hp = 2
        self.hp = 2

        # -------------------------------------------------------------
        # Entregável 2.14.1: Golpe Primário — Twin Kodachi Cross Slice
        # -------------------------------------------------------------
        self.scissor_cooldown = 0.28
        self.scissor_timer = 0.0
        self.attack_duration = 0.14
        self.combo_step = 0

        # -------------------------------------------------------------
        # Entregável 2.14.2: Golpe Secundário — Híbrido Dança Mai + Acrobat Lunge
        # -------------------------------------------------------------
        self.mai_dance_cooldown = 3.2
        self.acrobat_cooldown = 3.2
        self.mai_dance_timer = 0.0
        self.mai_timer = 0.0
        self.acrobat_timer = 0.0
        self.mai_dance_duration = 0.40       # Janela ágil de giro evasivo com deflexão
        self.acrobat_duration = 0.24         # Salto rasante perfurante de 3.2m
        self.acrobat_whiff_recovery = 0.28   # Recuperação punível se o avanço errar o alvo
        self.mai_active = False
        self.mai_parried_anything = False
        self.mai_exhausted = False
        self.mai_spin_angle = 0.0
        self.dance_dir_x = 1.0
        self.dance_dir_y = 0.0

        # -------------------------------------------------------------
        # Entregável 2.14.3: Mobilidade & Defesa — Shadow Step Slip
        # -------------------------------------------------------------
        self.is_agile_dodge = True
        self.roll_speed = 9.2
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.32
        self.recovery_duration = 0.20
        self.zanzou_ghosts = []

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and not getattr(self, "mai_exhausted", False)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    # -----------------------------------------------------------------
    # ATAQUE PRIMÁRIO: Twin Kodachi Cross Slice
    # -----------------------------------------------------------------
    def trigger_kodachi_strike(self, target_wx: float, target_wy: float):
        """Ataque Primário: Cruzamento rápido em X em pegada invertida das 2 kodachis."""
        if not self.can_act() or self.scissor_timer > 0:
            return False

        self.set_facing(target_wx, target_wy)
        self.combo_step = (getattr(self, "combo_step", 0) % 3) + 1
        self.state = STATE_ATTACK
        self.state_timer = self.attack_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.20   # Alcance ágil de lâminas gêmeas (0.95m a 1.20m)
        self.hitbox_damage = 2      # Letal
        self.slash_dir = (self.facing_x, self.facing_y)

        # Passo agressivo avançando 0.45m
        self.wx += self.facing_x * 0.45
        self.wy += self.facing_y * 0.45
        self.hitbox_center = (self.wx + self.facing_x * 0.85, self.wy + self.facing_y * 0.85)
        self.scissor_timer = self.scissor_cooldown

        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.SWORD_SLASH, volume_scale=0.95)
        except Exception:
            pass

        return True

    def trigger_primary_attack(self, target_wx: float, target_wy: float):
        return self.trigger_kodachi_strike(target_wx, target_wy)

    trigger_scissor_strike = trigger_kodachi_strike
    trigger_scissor_slash = trigger_kodachi_strike

    # -----------------------------------------------------------------
    # AÇÃO SECUNDÁRIA: Híbrido Dança Mai + Acrobat Lunge
    # -----------------------------------------------------------------
    def trigger_mai_dance(self, target_wx: float = None, target_wy: float = None, opponent=None, projectiles: list = None, particles: list = None, banners: list = None):
        """
        Ação Secundária Híbrida:
        - Se chamada fora da dança: Inicia o giro evasivo Dança Mai (0.40s) com deflexão e i-frames.
        - Se reativada durante a Dança Mai: Cancela imediatamente no Twin Blade Acrobat Lunge (salto de 3.2m).
        """
        # Reativação durante a Dança Mai -> Executa o Salto Acrobático Lunge!
        if self.state == "MAI_DANCE":
            return self.trigger_acrobat_lunge(target_wx, target_wy, particles=particles, banners=banners)

        if not self.can_act() or self.mai_dance_timer > 0:
            return False

        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)
        self.mai_dance_timer = self.mai_dance_cooldown
        self.mai_timer = self.mai_dance_cooldown
        self.acrobat_timer = self.mai_dance_cooldown
        self.state = "MAI_DANCE"
        self.state_timer = self.mai_dance_duration
        self.is_invulnerable_dodge = True
        self.invulnerable = True
        self.mai_active = True
        self.mai_parried_anything = False
        self.mai_exhausted = False
        self.mai_spin_angle = 0.0

        # Deslize lateral e gracioso da Dança
        self.dance_dir_x = self.facing_x * 0.65 - self.facing_y * 0.75
        self.dance_dir_y = self.facing_y * 0.65 + self.facing_x * 0.75
        self.hitbox_active = False
        self.hitbox_radius = 1.25
        self.hitbox_damage = 1
        self.hitbox_center = (self.wx, self.wy)

        if banners is not None:
            banners.append(FloatingBanner(t("banner_mai_dance"), self.wx, self.wy - 0.6, wz=1.7, color=COLOR_CHIYO_AURA))

        # Partículas de pétalas de Higanbana e faíscas escarlates
        if particles is not None:
            for _ in range(16):
                ang = random.uniform(0, math.pi * 2)
                particles.append(SparkParticle(self.wx + math.cos(ang) * 0.45, self.wy + math.sin(ang) * 0.45, 0.38, color=COLOR_HIGANBANA))

        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.SWORD_CLASH, volume_scale=0.90)
        except Exception:
            pass

        # Defletir projéteis próximos no raio do giro
        if projectiles is not None:
            self._deflect_projectiles_in_range(projectiles)

        return True

    def trigger_acrobat_lunge(self, target_wx: float = None, target_wy: float = None, particles: list = None, banners: list = None):
        """Salto acrobático rasteiro avançando 3.2m com as duas kodachis estendidas em pinça perfurante."""
        if target_wx is not None and target_wy is not None:
            self.set_facing(target_wx, target_wy)

        self.state = "ACROBAT_LUNGE"
        self.state_timer = self.acrobat_duration
        self.is_invulnerable_dodge = False
        self.invulnerable = False
        self.hitbox_active = True
        self.hitbox_radius = 1.35
        self.hitbox_damage = 2
        self.hitbox_center = (self.wx + self.facing_x * 0.95, self.wy + self.facing_y * 0.95)
        self.slash_dir = (self.facing_x, self.facing_y)

        # Zanzou e faíscas no arranque do salto
        self._spawn_zanzou_ghost(alpha=180, duration=0.28)
        if particles is not None:
            for _ in range(12):
                ang = random.uniform(0, math.pi * 2)
                particles.append(SparkParticle(self.wx + math.cos(ang) * 0.35, self.wy + math.sin(ang) * 0.35, 0.40, color=COLOR_HIGANBANA))

        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.DODGE_WHOOSH, volume_scale=1.1)
            SoundManager.get_instance().play(SoundEvent.SWORD_SLASH, volume_scale=1.0)
        except Exception:
            pass

        return True

    def _deflect_projectiles_in_range(self, projectiles: list):
        """Reflete e redireciona projéteis inimigos no raio da Dança Mai."""
        for proj in projectiles:
            if getattr(proj, "owner", None) != self and getattr(proj, "is_active", getattr(proj, "active", True)):
                dx = proj.wx - self.wx
                dy = proj.wy - self.wy
                if math.hypot(dx, dy) <= 1.85:
                    proj.vx = -proj.vx * 1.25
                    proj.vy = -proj.vy * 1.25
                    if hasattr(proj, "dir_x"):
                        proj.dir_x = -proj.dir_x
                        proj.dir_y = -proj.dir_y
                    proj.owner = self
                    self.on_mai_parry_success()

    def on_mai_parry_success(self, attacker=None, game_map=None):
        """Chamado quando a Dança Mai apara um golpe corpo a corpo ou reflete projéteis."""
        self.mai_parried_anything = True
        self.mai_exhausted = False
        self.state_timer = min(self.state_timer, 0.18)
        self.mai_dance_timer = max(0.8, self.mai_dance_timer - 1.2)
        if attacker is not None and game_map is not None:
            glide_x = -self.facing_y * 0.65 - self.facing_x * 0.35
            glide_y = self.facing_x * 0.65 - self.facing_y * 0.35
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + glide_x))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + glide_y))

    def trigger_secondary_action(self, target_wx: float = None, target_wy: float = None, opponent=None, projectiles: list = None, particles: list = None, banners: list = None):
        return self.trigger_mai_dance(target_wx, target_wy, opponent=opponent, projectiles=projectiles, particles=particles, banners=banners)

    trigger_nodachi_mai = trigger_secondary_action
    trigger_secondary_attack = trigger_secondary_action

    # -----------------------------------------------------------------
    # ESQUIVA DEDICADA: Shadow Step Slip (Passo Fantasma)
    # -----------------------------------------------------------------
    def trigger_shadow_step(self, dwx: float, dwy: float, particles: list = None):
        """Deslize rasteiro rente ao chão com 14 i-frames, rastro de sombras e pétalas carmesim."""
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return False

        mag = math.hypot(dwx, dwy)
        if mag > 0.05:
            self.roll_dir_x = dwx / mag
            self.roll_dir_y = dwy / mag
            self.set_facing(self.wx + self.roll_dir_x, self.wy + self.roll_dir_y)
        else:
            self.roll_dir_x = self.facing_x
            self.roll_dir_y = self.facing_y

        self.state = STATE_ROLL
        self.state_timer = self.roll_duration
        self.roll_timer = self.roll_duration
        self.invulnerable = True
        self.is_invulnerable_dodge = True
        self.roll_cooldown_timer = self.roll_cooldown_duration

        # Rastro de sombras (after-images) e pétalas de Higanbana
        self._spawn_zanzou_ghost(alpha=200, duration=0.25)
        if particles is not None:
            for _ in range(8):
                ang = random.uniform(0, math.pi * 2)
                sp = SparkParticle(self.wx + math.cos(ang) * 0.25, self.wy + math.sin(ang) * 0.25, 0.22, color=COLOR_HIGANBANA)
                sp.vz = random.uniform(0.4, 1.2)
                particles.append(sp)

        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(SoundEvent.DODGE_WHOOSH, volume_scale=0.95)
        except Exception:
            pass

        return True

    def trigger_roll(self, dwx: float = 0.0, dwy: float = 0.0, particles: list = None):
        return self.trigger_shadow_step(dwx, dwy, particles=particles)

    def _spawn_zanzou_ghost(self, alpha: int = 180, duration: float = 0.25):
        self.zanzou_ghosts.append({
            "wx": self.wx,
            "wy": self.wy,
            "wz": self.wz,
            "facing_x": self.facing_x,
            "facing_y": self.facing_y,
            "alpha": alpha,
            "duration": duration,
            "max_duration": duration,
        })

    # -----------------------------------------------------------------
    # UPDATE DO COMBATENTE
    # -----------------------------------------------------------------
    def update(self, dt: float, game_map, particles: list = None, banners: list = None, opponent=None, projectiles: list = None, **kwargs):
        if not self.is_alive:
            return

        self.update_stealth(game_map)
        self.update_dodge_timers(dt)
        self.update_pit(dt, game_map, particles, banners)

        # Atualizar temporizadores de recarga
        if self.scissor_timer > 0:
            self.scissor_timer = max(0.0, self.scissor_timer - dt)

        if self.mai_dance_timer > 0:
            self.mai_dance_timer = max(0.0, self.mai_dance_timer - dt)
        self.mai_timer = self.mai_dance_timer
        self.acrobat_timer = self.mai_dance_timer

        # Atualizar fantasmas de rastro de sombra (Zanzou)
        if self.zanzou_ghosts:
            for g in self.zanzou_ghosts:
                g["duration"] -= dt
            self.zanzou_ghosts = [g for g in self.zanzou_ghosts if g["duration"] > 0]

        # 1. Ataque Primário: Twin Kodachi Cross Slice
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

        # 2. Salto Acrobático Perfurante: Twin Blade Acrobat Lunge (3.2m em avanço rasante)
        elif self.state == "ACROBAT_LUNGE":
            self.state_timer -= dt
            lunge_speed = 3.2 / max(0.01, self.acrobat_duration)
            new_wx = self.wx + self.facing_x * lunge_speed * dt
            new_wy = self.wy + self.facing_y * lunge_speed * dt
            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.hitbox_center = (self.wx + self.facing_x * 0.90, self.wy + self.facing_y * 0.90)

            # Rastro contínuo de sombras
            if random.random() < 0.40:
                self._spawn_zanzou_ghost(alpha=140, duration=0.20)

            if self.state_timer <= 0:
                self.hitbox_active = False
                # Whiff: fica vulnerável nas costas
                self.state = STATE_RECOVERY
                self.state_timer = self.acrobat_whiff_recovery
                self.apply_slow(self.acrobat_whiff_recovery + 0.10)

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.mai_exhausted = False

        # 3. Dança Mai (Pirueta Evasiva de 0.40s)
        elif self.state == "MAI_DANCE":
            self.state_timer -= dt
            progress = 1.0 - max(0.0, self.state_timer / max(0.01, self.mai_dance_duration))
            self.mai_spin_angle = progress * math.pi * 4.0

            # Deslize lateral suave
            curve_vx = self.dance_dir_x * math.cos(progress * math.pi) * 1.85
            curve_vy = self.dance_dir_y * math.cos(progress * math.pi) * 1.85
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + curve_vx * dt))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + curve_vy * dt))
            self.hitbox_center = (self.wx, self.wy)

            # Defletir projéteis durante toda a pirueta
            if projectiles is not None:
                self._deflect_projectiles_in_range(projectiles)

            if particles is not None and random.random() < 0.55:
                p_ang = self.mai_spin_angle + random.uniform(-0.4, 0.4)
                px = self.wx + math.cos(p_ang) * 0.55
                py = self.wy + math.sin(p_ang) * 0.55
                particles.append(SparkParticle(px, py, 0.32, color=COLOR_HIGANBANA))

            if self.state_timer <= 0:
                self.is_invulnerable_dodge = False
                self.invulnerable = False
                self.mai_active = False
                self.mai_spin_angle = 0.0
                self.state = STATE_IDLE

        # 4. Esquiva Rasteira Shadow Step Slip
        elif self.state == STATE_ROLL:
            self.state_timer -= dt
            self.roll_timer = max(0.0, self.roll_timer - dt)
            slip_speed = self.roll_speed
            self.wx = max(1.0, min(game_map.cols - 1.0, self.wx + self.roll_dir_x * slip_speed * dt))
            self.wy = max(1.0, min(game_map.rows - 1.0, self.wy + self.roll_dir_y * slip_speed * dt))

            if random.random() < 0.35:
                self._spawn_zanzou_ghost(alpha=130, duration=0.20)

            if self.state_timer <= 0:
                self.invulnerable = False
                self.is_invulnerable_dodge = False
                self.state = STATE_RECOVERY
                self.state_timer = self.roll_recovery_duration

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            self.mai_exhausted = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    # -----------------------------------------------------------------
    # RENDERIZAÇÃO
    # -----------------------------------------------------------------
    def render(self, surface: pygame.Surface, camera, shadow: bool = True):
        # 1. Rastro de Sombras (Zanzou Ghosts)
        if self.zanzou_ghosts and self.state not in ("VICTORY", "INTRO"):
            for g in self.zanzou_ghosts:
                ratio = max(0.0, min(1.0, g["duration"] / max(0.001, g.get("max_duration", 0.25))))
                g_alpha = int(g["alpha"] * ratio)
                if g_alpha > 10:
                    render_voxel_humanoid(
                        surface, camera, g["wx"], g["wy"], g["wz"],
                        g["facing_x"], g["facing_y"], "IDLE", 0.0,
                        self.is_alive, char_type="chiyo", walk_timer=self.walk_cycle,
                        alpha=g_alpha, is_moving=False,
                        extra_props={"pose": "shadow_step", "sheathed": False}
                    )

        # 2. Vórtice e Pétalas Orbitais da Dança Mai
        if self.state == "MAI_DANCE":
            cx, cy = camera.apply(self.wx, self.wy, 0.3)
            zoom = getattr(camera, "zoom", 1.0)
            r_px = int(36 * zoom)
            vortex_surf = pygame.Surface((r_px * 2 + 16, r_px * 2 + 16), pygame.SRCALPHA)
            center = (r_px + 8, r_px + 8)
            pygame.draw.circle(vortex_surf, (215, 38, 52, 125), center, r_px, 2)
            pygame.draw.circle(vortex_surf, (255, 130, 145, 95), center, max(1, int(r_px * 0.72)), 1)
            for i in range(4):
                a = self.mai_spin_angle + i * (math.pi / 2.0)
                px_orb = int(center[0] + math.cos(a) * r_px * 0.88)
                py_orb = int(center[1] + math.sin(a) * r_px * 0.55)
                pygame.draw.circle(vortex_surf, (240, 45, 62, 195), (px_orb, py_orb), max(2, int(4 * zoom)))
            surface.blit(vortex_surf, (cx - center[0], cy - center[1]))

        # Orientação visual e pose
        vis_fx, vis_fy = self.facing_x, self.facing_y
        if self.state == "MAI_DANCE":
            ca = math.cos(self.mai_spin_angle)
            sa = math.sin(self.mai_spin_angle)
            vis_fx = self.facing_x * ca - self.facing_y * sa
            vis_fy = self.facing_x * sa + self.facing_y * ca

        active_pose = getattr(self, "current_pose", None)
        if self.state == STATE_ROLL:
            active_pose = "shadow_step"
        elif self.state == "ACROBAT_LUNGE":
            active_pose = "acrobat_lunge"

        render_voxel_humanoid(
            surface, camera, self.wx, self.wy, self.wz,
            vis_fx, vis_fy, self.state, self.state_timer,
            self.is_alive, char_type="chiyo", walk_timer=self.walk_cycle,
            alpha=self.alpha, is_moving=self.is_moving,
            extra_props={
                "combo_step": getattr(self, "combo_step", 1),
                "mai_spin_angle": getattr(self, "mai_spin_angle", 0.0),
                "mai_exhausted": getattr(self, "mai_exhausted", False),
                "pose": active_pose,
                "sheathed": False,
            }
        )

    render_voxel = render
