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


ELEMENTS = ["wood", "fire", "earth", "metal", "water", "yinyang"]

ELEMENT_SPELL_NAMES = {
    "wood": ("Kusabi-Bari", "Shinju no Ibuki"),
    "fire": ("Guren no Ofuda", "Hi-bashira"),
    "earth": ("Ganseki-dan", "Doryū-heki"),
    "metal": ("Hagane no Yaiba", "Kongō-jin"),
    "water": ("Suiryū no Ya", "Kagami-Mizu"),
    "yinyang": ("Senkō / Kurayami", "Tenmei no Senkoku"),
}

ELEMENT_COLORS = {
    "wood": (45, 215, 120),
    "fire": (255, 75, 45),
    "earth": (235, 185, 65),
    "metal": (245, 248, 255),
    "water": (65, 175, 255),
    "yinyang": (225, 160, 255),
}


class SeimeiOnmyoji(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Seimei")
        self.char_type = "seimei"
        self.speed = 4.7
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Rondel Onmyōdō de 6 Elementos
        self.rondel_index = 0
        self.ofuda_cooldown = 0.65  # Ritmo universal balanceado
        self.ofuda_timer = 0.0

        # Ação Secundária: Ritos e Barreiras Kekkai
        self.ward_cooldown = 0.95  # Ritmo universal fluido
        self.ward_timer = 0.0
        self.active_wards: list[TalismanWard] = []

        # Esquiva: Deslize Shikigami
        self.is_agile_dodge = True
        self.roll_speed = 9.2
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.36
        self.recovery_duration = 0.18

    @property
    def current_element(self) -> str:
        return ELEMENTS[self.rondel_index % len(ELEMENTS)]

    def advance_rondel(self, banners: list = None):
        """Avança o Rondel 60° no sentido horário pelo Ciclo Generativo Onmyodo."""
        self.rondel_index = (self.rondel_index + 1) % len(ELEMENTS)
        el = self.current_element
        p_name, s_name = ELEMENT_SPELL_NAMES[el]
        col = ELEMENT_COLORS[el]
        if banners is not None:
            banners.append(FloatingBanner(f"[{el.upper()}] {p_name} / {s_name}", self.wx, self.wy, wz=1.9, color=col, duration=0.85))

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
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def trigger_ofuda_toss(self, aim_x: float, aim_y: float, projectiles: list, particles: list = None, banners: list = None) -> bool:
        """Ataque Primário: Dispara o feitiço elemental do elemento ativo no Rondel e avança o ciclo."""
        if not self.can_act() or self.ofuda_timer > 0 or projectiles is None:
            return False

        self.set_facing(aim_x, aim_y)
        self.ofuda_timer = self.ofuda_cooldown
        self.state = STATE_ATTACK
        self.state_timer = 0.24  # Tempo de conjuração para permitir reação defensiva da IA

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

        el = self.current_element
        p_name = ELEMENT_SPELL_NAMES[el][0]
        col = ELEMENT_COLORS[el]

        if el == "wood":
            # Madeira: Dispara leque triplo de agulhas Kusabi-Bari com dispersão em leque
            base_ang = math.atan2(dir_y, dir_x)
            for d_ang in (-0.20, 0.0, 0.20):
                ang = base_ang + d_ang
                fx = math.cos(ang)
                fy = math.sin(ang)
                ofuda = OfudaProjectile(
                    self.wx + fx * 0.45, self.wy + fy * 0.45,
                    wz=0.45,
                    dir_x=fx,
                    dir_y=fy,
                    owner=self,
                    max_range=6.5,
                    element="wood"
                )
                projectiles.append(ofuda)
        else:
            ofuda = OfudaProjectile(
                spawn_x, spawn_y,
                wz=0.45,
                dir_x=dir_x,
                dir_y=dir_y,
                owner=self,
                max_range=6.5,
                element=el
            )
            projectiles.append(ofuda)

        if banners is not None:
            banners.append(FloatingBanner(f"{p_name}!", self.wx, self.wy, wz=1.75, color=col, duration=0.75))

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(
                    spawn_x, spawn_y, 0.45,
                    color=col
                ))

        # Avança o Rondel para o próximo elemento!
        self.advance_rondel()
        return True

    def trigger_sacred_ward(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, banners: list = None, game_map = None) -> bool:
        """Ação Secundária: Conjura o Rito / Barreira Kekkai do elemento ativo no Rondel e avança o ciclo."""
        if not self.can_act() or self.ward_timer > 0 or projectiles is None:
            return False

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        el = self.current_element
        s_name = ELEMENT_SPELL_NAMES[el][1]
        col = ELEMENT_COLORS[el]

        # Posicionamento da barreira à frente de Seimei (1.35m)
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

        ward = TalismanWard(ward_x, ward_y, owner=self, duration=5.5, element=el)
        self.active_wards.append(ward)
        projectiles.append(ward)

        self.ward_timer = self.ward_cooldown
        self.state = STATE_RECOVERY
        self.state_timer = 0.22

        if banners is not None:
            banners.append(FloatingBanner(f"{s_name}!", ward_x, ward_y, wz=1.65, color=col, duration=0.80))

        if particles is not None:
            for _ in range(14):
                ang = random.uniform(0, math.pi * 2)
                r = random.uniform(0.1, 1.2)
                particles.append(SparkParticle(
                    ward_x + math.cos(ang) * r,
                    ward_y + math.sin(ang) * r,
                    0.10,
                    color=col
                ))

        # Avança o Rondel para o próximo elemento!
        self.advance_rondel()
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

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, cinematic_director=None, **kwargs):
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

        # Aura Elemental Dinâmica no Solo sob os pés de Seimei
        if self.is_alive:
            el = self.current_element
            col = ELEMENT_COLORS.get(el, (225, 160, 255))
            sx, sy = camera.apply(self.wx, self.wy, 0.0)
            r_px = int(24 * camera.zoom)
            t = pygame.time.get_ticks() * 0.005
            p_pulse = int(90 + math.sin(t * 3.0) * 35)

            # Anel místico pulsante no piso
            aura_surf = pygame.Surface((r_px * 2 + 8, r_px + 8), pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, (*col, p_pulse), (4, 4, r_px * 2, r_px), 2)
            pygame.draw.ellipse(aura_surf, (*col, p_pulse // 3), (4 + r_px // 2, 4 + r_px // 4, r_px, r_px // 2), 1)
            surface.blit(aura_surf, (sx - r_px - 4, sy - r_px // 2 - 4))

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

        # Partículas elementais sutis flutuando na mão / leque
        if self.is_alive and random.random() < 0.25:
            from src.effects.particles import SparkParticle
            hand_wx = self.wx + self.facing_x * 0.25
            hand_wy = self.wy + self.facing_y * 0.25
            hx, hy = camera.apply(hand_wx, hand_wy, 0.55)
            pygame.draw.circle(surface, ELEMENT_COLORS.get(self.current_element, (255, 255, 255)), (int(hx), int(hy)), 2)
