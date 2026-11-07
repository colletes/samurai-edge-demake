"""
Seimei (A Onmyoji dos Talismãs - Ciclo 4 - Overhaul 2.20):
Mestra das artes astrais, espíritos Shikigami e selos sagrados Onmyōdō do período Heian.
- Arquétipo: Feiticeira e zoner espiritual de controle e precisão (velocidade 4.7, 2 HP).
- Guarda Astral (Parry técnico canalizado pelo leque cerimonial e drapeado das mangas Kariginu).
- Ataque Primário: Ofuda Cortante (OFUDA_TOSS) - arremesso de talismã de papel sagrado em alta velocidade (projétil reto, alcance 6.5m, dano 2 HP).
  Bloqueado estritamente por obstáculos sólidos não destrutíveis do cenário (rochas, muros, poço, árvores).
  Ao disparar, manifesta as propriedades do elemento ativo e avança o Rondel Onmyōdō.
- Ação Secundária: Selo Sagrado Kekkai (SACRED_WARD) - crava no solo um mandala elemental de proteção por 5.5s (limite de 2 selos ativos simultâneos).
- Esquiva: Deslize Shikigami (SHIKIGAMI_GLIDE) - deslizamento fluido com asas de papel origami e 13 i-frames (0.22s de invulnerabilidade).
- Sistema de 6 Fatalidades Astrais: Ao aplicar o golpe fatal, executa o finisher correspondente ao elemento ativo no momento:
  1. Fogo: SEIMEI_FATAL_FIRE (青炎灰燼 — Seien Kaijin)
  2. Água: SEIMEI_FATAL_WATER (水葬昇華 — Suisou Shouka)
  3. Madeira: SEIMEI_FATAL_WOOD (神樹輪廻 — Shinju Rinne)
  4. Metal: SEIMEI_FATAL_METAL (金剛封縛 — Kongou Fuubaku)
  5. Terra: SEIMEI_FATAL_EARTH (岩宿化石 — Ganshuku Kaseki)
  6. Yin-Yang: SEIMEI_FATAL_YINYANG (陰陽天誅 — In-You Tenchuu)
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
        self.speed = 4.70
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Rondel Onmyōdō de 6 Elementos
        self.rondel_index = 0
        self.ofuda_cooldown = 0.88  # Cadência tática calibrada
        self.ofuda_timer = 0.0

        # Ação Secundária: Ritos e Barreiras Kekkai
        self.ward_cooldown = 1.40
        self.ward_timer = 0.0
        self.active_wards: list[TalismanWard] = []

        # Esquiva: Deslize Shikigami
        self.is_agile_dodge = True
        self.roll_speed = 9.20
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.16
        self.roll_cooldown_duration = 0.36
        self.recovery_duration = 0.18
        self.projectiles: list = []

    @property
    def current_element(self) -> str:
        return ELEMENTS[self.rondel_index % len(ELEMENTS)]

    @current_element.setter
    def current_element(self, elem: str):
        if elem in ELEMENTS:
            self.rondel_index = ELEMENTS.index(elem)

    @property
    def is_invulnerable(self) -> bool:
        return self.state == STATE_ROLL or getattr(self, "roll_iframes", 0) > 0 or getattr(self, "invulnerable", False)

    @property
    def finisher_style_primary(self) -> str:
        """Determina a fatalidade com base no elemento ativo no Rondel."""
        return f"SEIMEI_FATAL_{self.current_element.upper()}"

    @property
    def finisher_style_secondary(self) -> str:
        """Determina a fatalidade com base no elemento ativo no Rondel."""
        return f"SEIMEI_FATAL_{self.current_element.upper()}"

    def advance_rondel(self, banners: list = None):
        """Avança o Rondel 60° no sentido horário pelo Ciclo Generativo Onmyōdō."""
        self.rondel_index = (self.rondel_index + 1) % len(ELEMENTS)
        el = self.current_element
        p_name, s_name = ELEMENT_SPELL_NAMES[el]
        col = ELEMENT_COLORS[el]
        if banners is not None:
            banners.append(FloatingBanner(f"[{el.upper()}] {p_name} / {s_name}", self.wx, self.wy, wz=1.9, color=col, duration=0.85))

    advance_element = advance_rondel

    def trigger_parry(self) -> bool:
        """Apara golpes canalizando a barreira Onmyōdō com as mangas largas de seda sagrada e leque Sensu."""
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

    def trigger_ofuda_toss(self, aim_x: float, aim_y: float, projectiles: list = None, particles: list = None, banners: list = None, immediate: bool = False) -> bool:
        """Ataque Primário: Dispara o talismã sagrado reto (6.5m, 2 HP) com o elemento ativo no Rondel e avança o ciclo."""
        if not self.can_act() or self.ofuda_timer > 0:
            return False

        if projectiles is None:
            projectiles = self.projectiles

        self.set_facing(aim_x, aim_y)
        self.ofuda_timer = self.ofuda_cooldown
        self.state = STATE_ATTACK
        self.state_timer = 0.28  # Duração total do ritual
        self.cast_windup_timer = 0.12  # Windup telegrafado para leitura e esquiva justa

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

        if immediate:
            self.pending_ofuda = None
            self.cast_windup_timer = 0.0
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
                for _ in range(12):
                    particles.append(SparkParticle(spawn_x, spawn_y, 0.45, color=col))
            self.advance_rondel(banners=banners)
            return True

        self.pending_ofuda = (spawn_x, spawn_y, dir_x, dir_y, el, p_name, col, projectiles, particles, banners)

        # Partículas iniciais de preparação do ritual nos dedos de Seimei
        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(
                    self.wx + self.facing_x * 0.35,
                    self.wy + self.facing_y * 0.35,
                    0.50,
                    color=col
                ))
        return True

    def trigger_sacred_ward(self, aim_x: float = None, aim_y: float = None, projectiles: list = None, particles: list = None, banners: list = None, game_map=None) -> bool:
        """Ação Secundária: Conjura a barreira Kekkai do elemento ativo no solo à frente e avança o ciclo."""
        if not self.can_act() or self.ward_timer > 0:
            return False

        if projectiles is None:
            projectiles = self.projectiles

        if aim_x is not None and aim_y is not None:
            self.set_facing(aim_x, aim_y)

        el = self.current_element
        s_name = ELEMENT_SPELL_NAMES[el][1]
        col = ELEMENT_COLORS[el]

        ward_x = self.wx + self.facing_x * 1.35
        ward_y = self.wy + self.facing_y * 1.35

        if game_map is not None:
            min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
            ward_x = max(min_x + 0.4, min(max_x - 0.4, ward_x))
            ward_y = max(min_y + 0.4, min(max_y - 0.4, ward_y))

        # Limite estrito de 2 selos simultâneos
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
            for _ in range(16):
                ang = random.uniform(0, math.pi * 2)
                r = random.uniform(0.1, 1.2)
                particles.append(SparkParticle(
                    ward_x + math.cos(ang) * r,
                    ward_y + math.sin(ang) * r,
                    0.10,
                    color=col
                ))

        # Avança o Rondel
        self.advance_rondel(banners=banners)
        return True

    def trigger_shikigami_glide(self, dwx: float, dwy: float, particles: list = None) -> bool:
        """Esquiva especial: Deslizamento com asas de papel origami e 13 i-frames."""
        if not self.can_act() or self.roll_cooldown_timer > 0:
            return False

        res = super().trigger_roll(dwx, dwy, particles)
        if not res:
            return False

        if particles is not None:
            col = ELEMENT_COLORS.get(self.current_element, (225, 200, 255))
            for _ in range(12):
                particles.append(SparkParticle(
                    self.wx + random.uniform(-0.18, 0.18),
                    self.wy + random.uniform(-0.18, 0.18),
                    0.20 + random.uniform(0.0, 0.40),
                    color=col
                ))
            for _ in range(6):
                particles.append(SmokeParticle(
                    self.wx + random.uniform(-0.15, 0.15),
                    self.wy + random.uniform(-0.15, 0.15),
                    wz=0.15,
                    color=(45, 30, 60),
                    radius=0.18,
                    lifetime=0.40
                ))
        return True

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, cinematic_director=None, **kwargs):
        """Atualiza a máquina de estados, timers de recarga e barreiras ativas."""
        self.update_dodge_timers(dt)

        if self.ofuda_timer > 0:
            self.ofuda_timer = max(0.0, self.ofuda_timer - dt)

        if self.ward_timer > 0:
            self.ward_timer = max(0.0, self.ward_timer - dt)

        # Filtra barreiras ativas
        self.active_wards = [w for w in self.active_wards if getattr(w, "is_active", False)]

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive or self.state == STATE_STUNNED:
            self.pending_ofuda = None
            if self.state == STATE_STUNNED:
                self.state_timer -= dt
                if self.state_timer <= 0:
                    self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            if hasattr(self, "cast_windup_timer") and self.cast_windup_timer > 0:
                self.cast_windup_timer -= dt
                if particles is not None and random.random() < 0.65:
                    col = ELEMENT_COLORS.get(self.current_element, (255, 255, 255))
                    particles.append(SparkParticle(
                        self.wx + self.facing_x * 0.38,
                        self.wy + self.facing_y * 0.38,
                        0.52,
                        color=col
                    ))
                if self.cast_windup_timer <= 0 and hasattr(self, "pending_ofuda") and self.pending_ofuda:
                    spawn_x, spawn_y, dir_x, dir_y, el, p_name, col, proj_list, part_list, ban_list = self.pending_ofuda
                    self.pending_ofuda = None
                    ofuda = OfudaProjectile(
                        spawn_x, spawn_y,
                        wz=0.45,
                        dir_x=dir_x,
                        dir_y=dir_y,
                        owner=self,
                        max_range=6.5,
                        element=el
                    )
                    if proj_list is not None:
                        proj_list.append(ofuda)
                    if ban_list is not None:
                        ban_list.append(FloatingBanner(f"{p_name}!", self.wx, self.wy, wz=1.75, color=col, duration=0.75))
                    if part_list is not None:
                        for _ in range(12):
                            part_list.append(SparkParticle(spawn_x, spawn_y, 0.45, color=col))
                    self.advance_rondel(banners=ban_list)
                    try:
                        from src.audio import play_sfx, SoundEvent
                        play_sfx(SoundEvent.SHURIKEN_THROW)
                    except Exception:
                        pass
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
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

    def render(self, surface: pygame.Surface, camera):
        extra = {"element": self.current_element}
        if hasattr(self, "extra_props") and self.extra_props:
            extra.update(self.extra_props)
        if self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra["pose"] = "astral_guard"
        elif self.state == STATE_ROLL:
            extra["pose"] = "shikigami_glide"

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
            walk_timer=getattr(self, "walk_cycle", 0.0) or getattr(self, "walk_timer", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
