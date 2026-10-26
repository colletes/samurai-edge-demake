"""
Guerreira Ciclo 6 — Hendrika van der Bilt (Alquimista Tática / Mad Science de Dejima).

Características:
- Vida: 2 HP (precisão e agilidade europeia).
- Velocidade: 4.60 m/s (passo leve e esquivas ágeis).
- Ataque Primário: Stiletto Corrosivo (estocada perfurante veloz de adaga com solvente cáustico quebra-guarda).
- Ação Secundária: Frasco Alquímico Arremessável em Arco 3D com 5 Reagentes e 2 Gradações:
  1. Ácido Corrosivo (Verde): poça ácida que drena vida e corrói defesas/armaduras.
  2. Fogo Grego (Laranja): detonação pirotécnica em chamas com repulsão.
  3. Éter Soporífero (Roxo): nuvem densa de vapor que cega e atordoa (Stun).
  4. Salitre Congelante (Ciano): cristalização gélida do solo com lentidão profunda (-50% vel).
  5. Miasma Neurotóxico (Amarelo): gás deletério que causa dano e inverte controles de direção.
  - Gradações: Tier 1 (síntese portátil) e Tier 2 (reagente puro coletado de bancadas/barris da arena).
- Defesa: Desvio de estilete com dispersão de fumaça química.
- Fatalidades:
  - Primário: Estilete no pescoço com frasco quebrado na lâmina, dissolvendo o torso em ácido verde.
  - Secundário: Varia dinamicamente de acordo com o reagente arremessado (Ácido = dissolução, Fogo = cinzas, Éter = sufocamento espectral, Salitre = congelamento e quebra, Miasma = colapso convulsivo).
"""
import math
import random
import pygame

from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_PARRY, STATE_STUNNED, STATE_ROLL, resolve_playable_bounds,
)
from src.entities.voxel_models import render_voxel_humanoid
from src.entities.projectile import AlchemicFlaskProjectile, ChemicalPoolHazard, REAGENT_COLORS
from src.effects.particles import SparkParticle, BloodParticle, FloatingBanner, SmokeParticle

COLOR_HENDRIKA_AURA = (65, 215, 165)

REAGENT_NAMES = {
    "acid": "Ácido Corrosivo",
    "fire": "Fogo Grego",
    "ether": "Éter Soporífero",
    "frost": "Salitre Congelante",
    "miasma": "Miasma Neurotóxico",
}


class HendrikaAlchemist(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Hendrika")
        self.char_type = "hendrika"
        self.speed = 4.60
        self.max_hp = 2
        self.hp = 2
        self.can_parry = True

        # Ataque Primário: Estilete Alquímico Corrosivo
        self.stiletto_duration = 0.12
        self.stiletto_recovery = 0.12
        self.stiletto_reach = 1.85
        self.stiletto_radius = 1.10

        # Ação Secundária: Frascos Químicos (5 Reagentes em Ciclo)
        self.reagents = ["acid", "fire", "ether", "frost", "miasma"]
        self.active_reagent_idx = 0
        self.reagent_tier = 1
        self.reagent_surface_timer = 0.0
        self.surface_sample_reagent = "acid"
        self.last_harvested_reagent = "acid"
        self.flask_cooldown = 2.8
        self.flask_timer = 0.0
        self.active_flasks: list[AlchemicFlaskProjectile] = []
        self.active_pools: list[ChemicalPoolHazard] = []

        # Esquiva: Rolamento Acrobático Europeu
        self.is_agile_dodge = True
        self.roll_speed = 9.2
        self.roll_duration = 0.20
        self.roll_recovery_duration = 0.15
        self.roll_cooldown_duration = 0.32
        self.recovery_duration = self.stiletto_recovery

    @property
    def active_reagent(self) -> str:
        return self.reagents[self.active_reagent_idx]

    def can_act(self) -> bool:
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def cycle_reagent(self, banners: list = None, particles: list = None) -> str:
        """Cicla para o próximo composto alquímico da bandoleira."""
        self.active_reagent_idx = (self.active_reagent_idx + 1) % len(self.reagents)
        r = self.active_reagent
        name = REAGENT_NAMES.get(r, r.upper())
        col_core, _ = REAGENT_COLORS.get(r, ((255, 255, 255), (100, 100, 100)))

        if banners is not None:
            tier_str = " (T2)" if self.reagent_tier == 2 else ""
            banners.append(FloatingBanner(f"{name}{tier_str}!", self.wx, self.wy, wz=1.75, color=col_core, duration=0.85))

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.40, color=col_core))

        return r

    def check_reagent_pickup(self, game_map=None, banners: list = None, particles: list = None, dt: float = 0.016) -> bool:
        """
        Síntese Alquímica pelo Ambiente e Piso em Qualquer Arena:
        1. Proximidade com fogo/tochas/lanternas (< 2.2m) -> Fogo Grego ('fire')
        2. Pisos gélidos/água ('water', 'ice', 'snow') -> Salitre Congelante ('frost')
        3. Pisos rochosos/alvenaria ('stone', 'gravel', 'marble', 'roof') -> Éter Soporífero ('ether')
        4. Pisos orgânicos/vegetais/madeira ('wood', 'tatami', 'thatch') -> Miasma Neurotóxico ('miasma')
        5. Pisos de solo natural/lama/terra ('grass', 'dirt', 'mud', 'sand', 'earth') -> Ácido Corrosivo ('acid')
        - Permanecer sobre o solo/elemento por >= 0.85s sintetiza a fórmula daquele piso.
        - Permanecer por >= 2.0s potencializa a fórmula para Tier 2 (ou instantâneo junto a bancadas/barris).
        """
        if not game_map or not self.is_alive:
            return False

        # 1. Checar bancadas ou barris alquímicos para Tier 2 instantâneo
        nearby_lab = False
        all_props = getattr(game_map, "rocks", []) + getattr(game_map, "buildings", []) + getattr(game_map, "props", [])
        for obj in all_props:
            kind = getattr(obj, "__class__", None).__name__.lower()
            if "alchemy" in kind or "barrel" in kind or "reagent" in kind:
                dist = math.hypot(getattr(obj, "wx", -999.0) - self.wx, getattr(obj, "wy", -999.0) - self.wy)
                if dist <= 1.85:
                    nearby_lab = True
                    break

        if nearby_lab and self.reagent_tier < 2:
            self.reagent_tier = 2
            col_core, _ = REAGENT_COLORS.get(self.active_reagent, ((45, 225, 120), (20, 140, 65)))
            if banners is not None:
                banners.append(FloatingBanner("TIER 2 POTENCIALIZADO!", self.wx, self.wy, wz=1.85, color=col_core, duration=1.0))
            if particles is not None:
                for _ in range(16):
                    particles.append(SparkParticle(self.wx, self.wy, 0.50, color=col_core))
            return True

        # 2. Identificar reagente do ambiente imediato
        detected_reagent = None

        # A. Proximidade com fontes de chamas (tochas, lanternas, braseiros)
        for obj in all_props:
            kind = getattr(obj, "__class__", None).__name__.lower()
            if any(term in kind for term in ("torch", "lantern", "fire", "brazier", "lamp", "fissure")):
                dist = math.hypot(getattr(obj, "wx", -999.0) - self.wx, getattr(obj, "wy", -999.0) - self.wy)
                if dist <= 2.2:
                    detected_reagent = "fire"
                    break

        # B. Superfície do piso sob as botas de Hendrika
        if detected_reagent is None and hasattr(game_map, "surface_at"):
            surf = game_map.surface_at(self.wx, self.wy)
            if surf in ("water", "ice", "snow"):
                detected_reagent = "frost"
            elif surf in ("stone", "gravel", "marble", "roof"):
                detected_reagent = "ether"
            elif surf in ("wood", "tatami", "thatch"):
                detected_reagent = "miasma"
            elif surf in ("grass", "dirt", "mud", "sand", "wet_sand", "earth"):
                detected_reagent = "acid"
            else:
                detected_reagent = "acid"
        elif detected_reagent is None:
            detected_reagent = "acid"

        # 3. Temporizador de extração/síntese de solo
        if detected_reagent == self.surface_sample_reagent:
            self.reagent_surface_timer += dt
        else:
            self.surface_sample_reagent = detected_reagent
            self.reagent_surface_timer = 0.0

        # Transição de reagente ativo após permanecer no material por >= 0.85s
        if self.reagent_surface_timer >= 0.85 and self.active_reagent != self.surface_sample_reagent:
            if self.surface_sample_reagent in self.reagents:
                self.active_reagent_idx = self.reagents.index(self.surface_sample_reagent)
                self.reagent_tier = 1
                r_name = REAGENT_NAMES.get(self.active_reagent, self.active_reagent.upper())
                col_core, _ = REAGENT_COLORS.get(self.active_reagent, ((45, 225, 120), (20, 140, 65)))
                if banners is not None:
                    banners.append(FloatingBanner(f"SÍNTESE: {r_name}!", self.wx, self.wy, wz=1.75, color=col_core, duration=0.85))
                if particles is not None:
                    for _ in range(12):
                        particles.append(SparkParticle(self.wx, self.wy, 0.40, color=col_core))
                return True

        # Potencialização para Tier 2 ao permanecer por >= 2.0s
        if self.reagent_surface_timer >= 2.0 and self.reagent_tier < 2:
            self.reagent_tier = 2
            col_core, _ = REAGENT_COLORS.get(self.active_reagent, ((45, 225, 120), (20, 140, 65)))
            if banners is not None:
                banners.append(FloatingBanner("TIER 2 POTENCIALIZADO!", self.wx, self.wy, wz=1.85, color=col_core, duration=1.0))
            if particles is not None:
                for _ in range(16):
                    particles.append(SparkParticle(self.wx, self.wy, 0.50, color=col_core))
            return True

        return False

    def trigger_parry(self) -> bool:
        """Deflexão de Estilete com dispersão de fumaça alquímica protetora."""
        if not self.can_act():
            return False
        self.state = STATE_PARRY
        self.state_timer = 0.36
        return True

    def trigger_stiletto_thrust(self, aim_x: float, aim_y: float, particles: list = None, opponent=None) -> bool:
        """Ataque Primário: Estocada perfurante com solvente cáustico que corrói defesas."""
        if not self.can_act():
            return False

        self.set_facing(aim_x, aim_y)
        self.state = STATE_ATTACK
        self.state_timer = self.stiletto_duration
        self.hitbox_active = True
        self.hitbox_damage = 2

        self.hitbox_center = (
            self.wx + self.facing_x * 1.15,
            self.wy + self.facing_y * 1.15
        )
        self.hitbox_radius = self.stiletto_radius
        self.slash_dir = (self.facing_x, self.facing_y)

        # Quebra guarda frontal de parry devido ao ácido corrosivo na ponta
        if opponent and getattr(opponent, "is_alive", False) and getattr(opponent, "state", "") == STATE_PARRY:
            dist_opp = math.hypot(opponent.wx - self.hitbox_center[0], opponent.wy - self.hitbox_center[1])
            if dist_opp <= self.hitbox_radius + getattr(opponent, "radius", 0.35):
                opponent.stun(0.45)

        if particles is not None:
            col_core, _ = REAGENT_COLORS.get(self.active_reagent, ((45, 225, 120), (20, 140, 65)))
            for _ in range(8):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.30, color=col_core))

        return True

    def trigger_primary(self, aim_x: float, aim_y: float, particles: list = None, opponent=None, **kwargs) -> bool:
        return self.trigger_stiletto_thrust(aim_x, aim_y, particles, opponent)

    def trigger_flask_throw(self, aim_x: float, aim_y: float, projectiles: list = None, particles: list = None, banners: list = None, **kwargs) -> bool:
        """Ação Secundária: Arremesso de Frasco Químico em arco 3D balístico."""
        if not self.can_act() or self.flask_timer > 0:
            return False

        self.set_facing(aim_x, aim_y)
        self.state = "FLASK_THROW"
        self.state_timer = 0.14
        self.flask_timer = self.flask_cooldown

        flask = AlchemicFlaskProjectile(
            owner=self,
            start_x=self.wx + self.facing_x * 0.45,
            start_y=self.wy + self.facing_y * 0.45,
            target_x=aim_x,
            target_y=aim_y,
            reagent=self.active_reagent,
            tier=self.reagent_tier
        )

        if projectiles is not None:
            projectiles.append(flask)
        self.active_flasks.append(flask)

        r_name = REAGENT_NAMES.get(self.active_reagent, self.active_reagent.upper())
        col_core, _ = REAGENT_COLORS.get(self.active_reagent, ((45, 225, 120), (20, 140, 65)))

        if banners is not None:
            banners.append(FloatingBanner(f"{r_name}!", self.wx, self.wy, wz=1.75, color=col_core, duration=0.80))

        if particles is not None:
            for _ in range(10):
                particles.append(SparkParticle(self.wx, self.wy, 0.45, color=col_core))

        return True

    def trigger_secondary(self, aim_x: float, aim_y: float, projectiles: list = None, particles: list = None, banners: list = None, **kwargs) -> bool:
        return self.trigger_flask_throw(aim_x, aim_y, projectiles, particles, banners, **kwargs)

    def update(self, dt: float, game_map=None, particles: list = None, opponent=None, projectiles: list = None, banners: list = None, **kwargs):
        self.update_dodge_timers(dt)

        if self.flask_timer > 0:
            self.flask_timer = max(0.0, self.flask_timer - dt)

        # Síntese e extração de reagentes baseada no material do piso e ambiente
        self.check_reagent_pickup(game_map, banners, particles, dt=dt)

        # Atualizar poças químicas ativas geradas por Hendrika
        fighters = [self]
        if opponent:
            fighters.append(opponent)
        cd = kwargs.get("cinematic_director")
        for pool in list(self.active_pools):
            if not pool.update(dt, fighters=fighters, particles=particles, banners=banners, cinematic_director=cd):
                self.active_pools.remove(pool)

        if self.state == STATE_ROLL:
            self.update_roll(dt, game_map, particles)
            return

        if not self.is_alive:
            self.wz = 0.0
            return

        if self.state == STATE_STUNNED:
            self.wz = 0.0
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
            return

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            step_speed = 4.0
            new_wx = self.wx + self.facing_x * step_speed * dt
            new_wy = self.wy + self.facing_y * step_speed * dt
            if game_map is not None:
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx, self.wy = new_wx, new_wy

            self.hitbox_center = (
                self.wx + self.facing_x * 1.15,
                self.wy + self.facing_y * 1.15
            )
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = self.stiletto_recovery
                self.hitbox_active = False
            return

        if self.state == "FLASK_THROW":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_RECOVERY
                self.state_timer = 0.08
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
        extra = {
            "reagent": self.active_reagent,
            "reagent_tier": self.reagent_tier
        }
        if self.state == "FLASK_THROW":
            extra["pose"] = "flask_throw"
        elif self.state in ("DEFEND", "PARRY") or getattr(self, "is_parrying", False):
            extra["pose"] = "stiletto_parry"

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
            char_type="hendrika",
            walk_timer=getattr(self, "walk_cycle", 0.0),
            alpha=getattr(self, "alpha", 255),
            is_moving=getattr(self, "is_moving", False),
            extra_props=extra
        )
