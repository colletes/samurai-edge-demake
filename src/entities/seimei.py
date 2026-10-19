"""
Seimei (A Onmyoji dos Talismãs - Ciclo 4):
Mestra das artes astrais, espíritos Shikigami e selos sagrados Onmyodo do período Heian.
- Arquétipo: Feiticeira e zoner espiritual de controle e precisão (velocidade 4.7, 2 HP).
- Guarda Astral (Parry técnico com o leque cerimonial e o drapeado sagrado das mangas do Kariginu).
- Ataque Primário: Ofuda Cortante (OFUDA_TOSS) - arremesso em alta velocidade de talismã de papel encantado com caligrafia mística vermelha/dourada (projétil veloz, alcance 6.0m, dano 2). No golpe fatal (SEAL_STASIS_COLLAPSE), o amuleto crava no alvo e este é consumido em chamas verdes espirituais até que só sobrem cinzas. Cooldown 0.45s.
- Ação Secundária: Selo Sagrado (SACRED_WARD) - crava no solo um mandala de proteção que detona em Pilar de Fogo Sagrado ao contato do rival ou após 5.5s (2 de dano no epicentro, repel/stun e purificação de projéteis). Cooldown 4.0s.
- Esquiva: Deslize Shikigami (SHIKIGAMI_GLIDE) - deslizamento fluido com asas de papel origami translúcido e partículas celestiais com i-frames.
"""
import math
import random
import pygame
from src.config import (
    COLOR_STEEL, COLOR_WHITE, COLOR_GOLD, COLOR_SEIMEI_AURA
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_STUNNED, STATE_DEAD, STATE_ROLL, STATE_PARRY, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import OfudaProjectile, TalismanWard
from src.effects.particles import SparkParticle, SmokeParticle, FloatingBanner


class SeimeiOnmyoji(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Seimei")
        self.char_type = "seimei"
        self.speed = 4.7
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Ofuda Cortante
        self.ofuda_cooldown = 0.45
        self.ofuda_timer = 0.0

        # Ação Secundária: Selo Sagrado (Talisman Ward)
        self.ward_cooldown = 4.0
        self.ward_timer = 0.0
        self.active_wards: list[TalismanWard] = []

        # Esquiva: Deslize Shikigami
        self.is_agile_dodge = True
        self.roll_speed = 9.2
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.36
        self.recovery_duration = 0.18

    def trigger_parry(self) -> bool:
        """Apara golpes canalizando a barreira Onmyodo com as mangas largas de seda sagrada."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.38
        return True

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_ofuda_toss(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None) -> bool:
        """Ataque Primário: Dispara um talismã cortante veloz com kanji sagrado."""
        if not self.can_act() or self.ofuda_timer > 0 or projectiles is None:
            return False

        self.set_facing(aim_x, aim_y)
        self.ofuda_timer = self.ofuda_cooldown
        self.state = STATE_ATTACK
        self.state_timer = 0.14

        dx = aim_x - self.wx
        dy = aim_y - self.wy
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x, dir_y = self.facing_x, self.facing_y

        spawn_x = self.wx + dir_x * 0.45
        spawn_y = self.wy + dir_y * 0.45

        ofuda = OfudaProjectile(
            spawn_x, spawn_y,
            wz=0.45,
            dir_x=dir_x,
            dir_y=dir_y,
            owner=self,
            max_range=6.2
        )
        projectiles.append(ofuda)

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(
                    spawn_x, spawn_y, 0.45,
                    color=random.choice([(140, 205, 255), (255, 245, 160)])
                ))
        return True

    def trigger_sacred_ward(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, banners: list = None, game_map = None) -> bool:
        """Ação Secundária: Posiciona no chão um Selo Sagrado de purificação à frente de Seimei."""
        if not self.can_act() or self.ward_timer > 0 or projectiles is None:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        # A barreira é posicionada de forma consistente exatamente à frente de Seimei (1.35m)
        ward_x = self.wx + self.facing_x * 1.35
        ward_y = self.wy + self.facing_y * 1.35

        if game_map is not None:
            from src.entities.samurai import resolve_playable_bounds
            min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
            ward_x = max(min_x + 0.4, min(max_x - 0.4, ward_x))
            ward_y = max(min_y + 0.4, min(max_y - 0.4, ward_y))

        # Limitar número de selos simultâneos a 2
        self.active_wards = [w for w in self.active_wards if getattr(w, "is_active", False)]
        if len(self.active_wards) >= 2:
            oldest = self.active_wards.pop(0)
            oldest.detonate()

        ward = TalismanWard(ward_x, ward_y, owner=self, duration=5.5)
        self.active_wards.append(ward)
        projectiles.append(ward)

        self.ward_timer = self.ward_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.15

        if banners is not None:
            banners.append(FloatingBanner("SACRED WARD!", ward_x, ward_y, wz=1.6, color=(80, 190, 255)))

        if particles is not None:
            for _ in range(12):
                ang = random.uniform(0, math.pi * 2)
                r = random.uniform(0.1, 1.2)
                particles.append(SparkParticle(
                    ward_x + math.cos(ang) * r,
                    ward_y + math.sin(ang) * r,
                    0.10,
                    color=(160, 220, 255)
                ))
        return True

    def trigger_shikigami_glide(self, dwx: float, dwy: float, particles: list = None):
        """Esquiva especial: Deslize místico com asas de papel Shikigami e i-frames."""
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return

        super().trigger_roll(dwx, dwy, particles)
        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.25, 0.25),
                    self.wy + random.uniform(-0.25, 0.25),
                    random.uniform(0.1, 0.5),
                    color=random.choice([(252, 250, 245), (140, 190, 255), (255, 240, 140)])
                ))

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None):
        """Atualiza a máquina de estados e tempos de recarga dos feitiços Onmyodo."""
        self.update_dodge_timers(dt)

        if self.ofuda_timer > 0:
            self.ofuda_timer = max(0.0, self.ofuda_timer - dt)

        if self.ward_timer > 0:
            self.ward_timer = max(0.0, self.ward_timer - dt)

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            return

        if self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False
            return

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        elif self.state == STATE_PARRY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        # Filtra selos expirados
        self.active_wards = [w for w in self.active_wards if getattr(w, "is_active", False)]

    def render(self, surface: pygame.Surface, camera):
        extra = {}
        if self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra = {"pose": "astral_guard"}

        render_voxel_humanoid(
            surface=surface,
            camera=camera,
            wx=self.wx,
            wy=self.wy,
            wz=getattr(self, "wz", 0.0),
            facing_x=self.facing_x,
            facing_y=self.facing_y,
            state=self.state,
            state_timer=self.state_timer,
            is_alive=self.is_alive,
            char_type="seimei",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
