"""
Samurai Vermelho (Kenshi): Mestre do Iai-jutsu.
Ataque relâmpago de saque instantâneo com avanço veloz,
mas com alto tempo de recuperação (recovery) após o golpe.
"""
import math
import pygame
from src.config import (
    COLOR_RED_KIMONO, COLOR_RED_HAIR, COLOR_RED_HAKAMA,
    COLOR_RED_AURA, COLOR_STEEL, COLOR_GOLD, COLOR_WHITE, COLOR_BLACK
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY,
    STATE_DASH, STATE_STUNNED, STATE_DEAD, STATE_ROLL,
    slide_movement_against_obstacles, resolve_playable_bounds
)
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.iso_math import world_to_iso

class RedSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kenshi")
        self.char_type = "kenshin"
        self.speed = 5.4  # Agilidade máxima do retalhador

        # Parâmetros do Iai-jutsu (Entregável 2.1.1: Shukuchi Battoujutsu Slice)
        self.iai_startup_duration = 0.10  # 6 frames de postura Iai profunda com brilho na tsuba (Koiguchi-kiri)
        self.iai_startup_timer = 0.0
        self.is_shukuchi_cancel = False
        self.base_dash_speed = 20.0
        self.dash_speed = 20.0
        self.dash_duration = 0.14         # Avanço supersônico (~2.8 tiles)
        self.recovery_duration = 0.45     # Embainhamento (Noto) caminhando a 50% da velocidade
        self.noto_walk_speed_mult = 0.50
        self.attack_range = 2.6

        # Ação Secundária: Ryuu Tsui Sen (龍槌閃 - Entregável 2.1.2)
        self.ryuu_cooldown = 3.5
        self.ryuu_timer = 0.0
        self.ryuu_phase = "ASCEND"
        self.ryuu_ascend_duration = 0.08
        self.ryuu_apex_duration = 0.06
        self.ryuu_descend_duration = 0.14
        self.ryuu_phase_timer = 0.0
        self.ryuu_start_wz = 0.35
        self.ryuu_apex_wz = 2.60

        # Efeito visual de rastro de lâmina
        self.slash_trail_points: list[tuple[float, float]] = []

        # Terceira Ação: Shukuchi Especial / Ágil (Entregável 2.1.3)
        self.is_agile_dodge = True
        self.shukuchi_duration = 0.15
        self.shukuchi_speed = 28.0
        self.roll_speed = 10.5
        self.roll_duration = 0.22
        self.roll_recovery_duration = 0.12
        self.roll_cooldown_duration = 0.35
        self.post_shukuchi_iframe_timer = 0.0

        # Variáveis de deflexão e acrobacia pós-parry (Backhop terrestre & Mortal aéreo)
        self.zanzou_spawn_timer = 0.0
        self.zanzou_ghosts = []
        self.is_aerial_parry = False
        self.somersault_angle = 0.0
        self.parry_hop_start_wz = 0.0
        self.parry_hop_dir = (0.0, 0.0)
        self.parry_hop_speed = 9.0
        self.parry_hop_duration = 0.30

        # Qualidade Visual & Fluidez (Entregáveis 2.1.7 e 2.1.9)
        self.ssaa_enabled = True
        self._pose_lerp_tracker = {
            "lerp_duration": 0.08,
            "blend_timer": 0.0,
            "pose_key": None,
            "prev_snap": None,
            "last_snap": None,
            "transitions_count": 0,
        }

    def take_hit(self, slash_dir: tuple[float, float], damage: int = 2) -> tuple[bool, bool]:
        """Aplica dano e limpa rastros e pós-imagens de Kenshi ao ser atingida ou morta."""
        hit, killed = super().take_hit(slash_dir, damage)
        if hit:
            self.slash_trail_points.clear()
            self.zanzou_ghosts.clear()
        return hit, killed

    def can_act(self) -> bool:
        """Kenshi só pode agir se estiver viva, em IDLE/WALK e sem recovery de dash/golpes."""
        return (
            self.is_alive
            and self.state in (STATE_IDLE, STATE_WALK)
            and self.roll_recovery_timer <= 0
            and self.dash_recovery_timer <= 0
        )

    def can_move(self) -> bool:
        """Kenshi pode se mover livremente enquanto embainha a katana (STATE_RECOVERY)."""
        if self.roll_recovery_timer > 0:
            return False
        if self.state == STATE_RECOVERY:
            return self.is_alive
        return super().can_move()

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        """Aplica movimentação mantendo o estado de RECOVERY (embainhar/noto) a 50% da velocidade."""
        if self.state == STATE_RECOVERY:
            saved_state = self.state
            saved_speed = self.speed
            self.speed = saved_speed * getattr(self, "noto_walk_speed_mult", 0.50)
            try:
                super().apply_movement(move_x, move_y, dt, game_map)
            finally:
                self.speed = saved_speed
                self.state = saved_state
        else:
            super().apply_movement(move_x, move_y, dt, game_map)

    def can_cancel_shukuchi(self) -> bool:
        """
        Entregável 2.1.3 (Shukuchi Battou-Giri):
        Permite cancelar os últimos 40% do Shukuchi (state_timer <= 0.06s) diretamente no Iai Slice.
        """
        shukuchi_dur = getattr(self, "shukuchi_duration", 0.15)
        return (
            self.is_alive
            and self.state == "SHUKUCHI"
            and self.state_timer <= shukuchi_dur * 0.40 + 1e-5
        )

    def trigger_iai_attack(self, target_wx: float, target_wy: float, instant: bool = False):
        """
        Entregável 2.1.1 & 2.1.3: Shukuchi Battoujutsu Slice.
        - Startup telegrafado de 0.10s (6f) em postura Iai profunda com brilho na tsuba (Koiguchi-kiri) e som metálico.
        - Se acionado nos últimos 40% do Shukuchi (Shukuchi Battou-Giri), cancela a recuperação do dash,
          herda o momentum e reduz o startup pela metade (0.05s / 3f).
        """
        is_cancel = self.can_cancel_shukuchi()
        if not self.can_act() and not is_cancel:
            return False

        self.set_facing(target_wx, target_wy)
        self.is_shukuchi_cancel = is_cancel
        self.state = STATE_ATTACK
        self.state_timer = self.dash_duration
        self.dash_speed = self.base_dash_speed * (1.15 if is_cancel else 1.0)
        if instant:
            self.iai_startup_timer = 0.0
            self.hitbox_active = True
        else:
            self.iai_startup_timer = (self.iai_startup_duration * 0.5) if is_cancel else self.iai_startup_duration
            self.hitbox_active = (self.iai_startup_timer <= 0.0)
        self.is_invulnerable_dodge = False
        self.hitbox_radius = 1.25  # Arco ampliado para 1.25m para consistência do corte
        self.slash_dir = (self.facing_x, self.facing_y)
        self.slash_trail_points = [(self.wx, self.wy)]
        self.hitbox_center = (self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8)

        try:
            from src.audio import play_sfx, SoundEvent
            if self.iai_startup_timer > 0:
                play_sfx(SoundEvent.PARRY, volume_scale=0.65)
            else:
                play_sfx(SoundEvent.SLASH_KATANA, volume_scale=0.92)
        except Exception:
            pass
        return True

    def trigger_ryuu_tsui_sen(self, target_wx: float, target_wy: float, particles: list = None, banners: list = None, opponent = None):
        """
        Entregável 2.1.2: Ação Secundária — Ryuu Tsui Sen (龍槌閃).
        Salto parabólico ultra-veloz em 3 fases com sombras Zanzou:
        1. ASCEND (0.08s): Subida explosiva estilo Shukuchi até wz=2.6m deixando pós-imagens Zanzou.
        2. APEX (0.06s): Paira no ápice com katana erguida acima da cabeça com as duas mãos e brilho dourado.
        3. DESCEND (0.14s): Queda meteórica vertical com corte de cima para baixo (raio 1.45m).
        """
        if not self.can_act() or self.ryuu_timer > 0:
            return False

        self.set_facing(target_wx, target_wy)
        self.ryuu_timer = self.ryuu_cooldown
        self.state = "RYUU_TSUI_SEN"
        self.ryuu_phase = "ASCEND"
        self.ryuu_phase_timer = self.ryuu_ascend_duration
        self.state_timer = self.ryuu_ascend_duration + self.ryuu_apex_duration + self.ryuu_descend_duration
        self.wz = self.ryuu_start_wz  # Impulso inicial imediato do salto Shukuchi (wz > 0 no frame 0)
        self.is_invulnerable_dodge = True
        self.hitbox_active = False
        self.slash_trail_points.clear()
        self.zanzou_spawn_timer = 0.0

        # Pós-imagem do impulso de subida com sombras Shukuchi
        if not hasattr(self, "zanzou_ghosts"):
            self.zanzou_ghosts = []
        self.zanzou_ghosts.append({
            "wx": self.wx, "wy": self.wy, "wz": 0.0,
            "facing_x": self.facing_x, "facing_y": self.facing_y,
            "alpha": 210, "duration": 0.30
        })

        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.SHUKUCHI, volume_scale=0.85)
            play_sfx(SoundEvent.RYUU_TSUI_SEN, volume_scale=1.0)
        except Exception:
            pass

        if particles is not None:
            from src.effects.particles import SmokeParticle, SparkParticle
            for _ in range(8):
                particles.append(SmokeParticle(self.wx, self.wy, 0.25, color=(230, 235, 245), size=6))
                particles.append(SparkParticle(self.wx, self.wy, 0.35, color=(255, 215, 110)))
        return True

    def trigger_tsuka_ate(self, target_wx: float, target_wy: float, particles: list = None, opponent = None, banners: list = None):
        """Compatibilidade: executa Tsuka-ate de quebra de guarda ou redireciona para Ryuu Tsui Sen."""
        if opponent is not None and banners is not None:
            self.state = "TSUKA_ATE"
            self.state_timer = 0.25
            self.set_facing(target_wx, target_wy)
            if hasattr(opponent, "stun"):
                opponent.stun(0.40)
            from src.effects.particles import FloatingBanner
            banners.append(FloatingBanner("TSUKA-ATE! GUARD BREAK!", opponent.wx, opponent.wy, wz=1.75, color=(240, 210, 110)))
        else:
            self.trigger_ryuu_tsui_sen(target_wx, target_wy, particles=particles, banners=banners, opponent=opponent)

    def trigger_dash(self, dir_x: float, dir_y: float):
        """Terceira Ação: Passo Relâmpago Shukuchi (縮地) — Deslocamento veloz com pós-imagens e i-frames."""
        if (
            not self.is_alive
            or self.state not in (STATE_IDLE, STATE_WALK)
            or self.roll_recovery_timer > 0
            or self.roll_cooldown_timer > 0
            or self.dash_recovery_timer > 0
        ):
            return False
        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y # Recuo para trás
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.state = "SHUKUCHI"
        self.state_timer = self.shukuchi_duration
        self.shukuchi_speed = 28.0
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.slash_trail_points.clear()  # Limpar para nunca deixar rastro vermelho no dash
        self.zanzou_spawn_timer = 0.0
        # Registrar primeira pós-imagem fantasma (zanzou)
        if not hasattr(self, "zanzou_ghosts"):
            self.zanzou_ghosts = []
        self.zanzou_ghosts.append({
            "wx": self.wx, "wy": self.wy, "wz": self.wz,
            "facing_x": self.facing_x, "facing_y": self.facing_y,
            "alpha": 190, "duration": 0.28
        })

        try:
            from src.audio import play_sfx, SoundEvent
            play_sfx(SoundEvent.SHUKUCHI, volume_scale=0.9)
        except Exception:
            pass
        return True

    def stun(self, duration: float = 0.8):
        """Atordoa Kenshi garantindo queda/aterrissagem física (wz = 0.0) sem flutuação."""
        super().stun(duration)
        self.wz = 0.0
        self.iai_startup_timer = 0.0

    def on_parried(self, opponent, game_map=None, banners: list = None, particles: list = None):
        """
        Entregáveis 2.1.1 e 2.1.2 — Mitigação e Acrobacia de Deflexão ao ser aparada:
        1. Se for aparada durante o Ryuu Tsui Sen (ou no ar):
           Kenshi usa o impulso da colisão das lâminas para dar um MORTAL PARA TRÁS NO AR
           (somersault 360°), recuando ~2.95 tiles e aterrissando fora do alcance de contra-ataque melee.
        2. Se for aparada em golpe terrestre (Iai):
           Kenshi executa um salto acrobático animado para trás (~2.70 tiles, fora do alcance de
           contra-ataque melee), e ao aterrissar faz o embainhamento (Noto / STATE_RECOVERY) podendo andar.
        """
        self.hitbox_active = False
        self.iai_startup_timer = 0.0
        self.slash_trail_points.clear()

        # Calcular vetor de repulsão / recuo para longe do oponente
        if opponent is not None:
            dx = self.wx - opponent.wx
            dy = self.wy - opponent.wy
            dist = math.hypot(dx, dy)
            if dist > 0.001:
                hop_dir_x = dx / dist
                hop_dir_y = dy / dist
            else:
                hop_dir_x = -self.facing_x
                hop_dir_y = -self.facing_y
        else:
            hop_dir_x = -self.facing_x
            hop_dir_y = -self.facing_y

        is_aerial = (self.state == "RYUU_TSUI_SEN" or self.wz > 0.1)

        self.state = "PARRY_BACKHOP"
        self.is_invulnerable_dodge = True
        self.is_aerial_parry = is_aerial
        self.parry_hop_dir = (hop_dir_x, hop_dir_y)
        self.somersault_angle = 0.0

        if is_aerial:
            self.parry_hop_duration = 0.36
            self.state_timer = self.parry_hop_duration
            self.parry_hop_speed = 8.2  # ~2.95 tiles de recuo com mortal para trás
            self.parry_hop_start_wz = max(0.85, self.wz)
            self.wz = self.parry_hop_start_wz
            if banners is not None:
                from src.effects.particles import FloatingBanner
                banners.append(FloatingBanner("AERIAL SOMERSAULT!", self.wx, self.wy, wz=self.wz + 0.3, color=(255, 210, 110)))
        else:
            self.parry_hop_duration = 0.30
            self.state_timer = self.parry_hop_duration
            self.parry_hop_speed = 9.0  # ~2.70 tiles de salto para trás (fora do alcance melee)
            self.parry_hop_start_wz = 0.05
            self.wz = 0.05
            if banners is not None:
                from src.effects.particles import FloatingBanner
                banners.append(FloatingBanner("ACROBATIC BACKHOP!", self.wx, self.wy, wz=1.75, color=(255, 215, 120)))

        # Zanzou inicial do recuo
        if not hasattr(self, "zanzou_ghosts"):
            self.zanzou_ghosts = []
        self.zanzou_ghosts.append({
            "wx": self.wx, "wy": self.wy, "wz": self.wz,
            "facing_x": self.facing_x, "facing_y": self.facing_y,
            "alpha": 180, "duration": 0.25
        })

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(6):
                particles.append(SparkParticle(self.wx, self.wy, max(0.45, self.wz), color=(255, 220, 140)))

    def update(self, dt: float, game_map, particles: list = None):
        """Atualiza os estados e timings do Samurai Vermelho."""
        if not hasattr(self, "zanzou_ghosts"):
            self.zanzou_ghosts = []

        # Atualizar interpolador de pose (Pose LERP 0.08s — Entregável 2.1.9; avança mesmo em INTRO/VICTORY quando dt == 0)
        lerp_dt = dt if dt > 0.0 else (1.0 / 60.0)
        if hasattr(self, "_pose_lerp_tracker") and self._pose_lerp_tracker["blend_timer"] > 0.0:
            self._pose_lerp_tracker["blend_timer"] = max(0.0, self._pose_lerp_tracker["blend_timer"] - lerp_dt)

        # Atualizar e desvanecer pós-imagens zanzou (continua desvanecendo mesmo no pós-round quando dt == 0)
        if not self.is_alive or self.state in ("VICTORY", "INTRO"):
            self.zanzou_ghosts.clear()
        else:
            decay_dt = dt if dt > 0.0 else (1.0 / 60.0)
            for g in self.zanzou_ghosts:
                if "max_duration" not in g:
                    g["max_duration"] = max(0.01, float(g["duration"]))
                if "max_alpha" not in g:
                    g["max_alpha"] = max(0, min(255, int(g.get("alpha", 200))))
                g["duration"] -= decay_dt
                g["alpha"] = max(0, min(255, int(g["max_alpha"] * (g["duration"] / g["max_duration"]))))
            self.zanzou_ghosts = [g for g in self.zanzou_ghosts if g["duration"] > 0]

        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.ryuu_timer > 0:
            self.ryuu_timer -= dt
        if self.post_shukuchi_iframe_timer > 0:
            self.post_shukuchi_iframe_timer = max(0.0, self.post_shukuchi_iframe_timer - dt)
            if self.post_shukuchi_iframe_timer <= 0 and self.state not in (STATE_ROLL, "SHUKUCHI", "RYUU_TSUI_SEN", "PARRY_BACKHOP"):
                self.is_invulnerable_dodge = False
        self.update_dodge_timers(dt)
        if self.state not in ("RYUU_TSUI_SEN", "PARRY_BACKHOP", "JUMP") and self.wz > 0.0:
            self.wz = max(0.0, self.wz - 16.0 * dt)

        if self.state == STATE_ATTACK:
            # Fase 1 do Iai: Startup telegrafado Koiguchi-kiri (0.10s ou 0.05s no Shukuchi Cancel)
            if self.iai_startup_timer > 0.0:
                self.iai_startup_timer -= dt
                if self.iai_startup_timer > 0.0:
                    return
                # Startup concluído: dispara o corte supersônico!
                overflow_dt = -self.iai_startup_timer
                self.iai_startup_timer = 0.0
                self.hitbox_active = True
                try:
                    from src.audio import play_sfx, SoundEvent
                    play_sfx(SoundEvent.SLASH_KATANA, volume_scale=0.95)
                except Exception:
                    pass
                dt = overflow_dt
                if dt <= 0.0:
                    return

            # Fase 2 do Iai: Avanço relâmpago Battoujutsu
            self.state_timer -= dt
            dash_dist = self.dash_speed * dt
            new_wx = self.wx + self.facing_x * dash_dist
            new_wy = self.wy + self.facing_y * dash_dist

            # Verificar colisão com rochas/poço durante o golpe
            hit_obstacle = False
            for r in game_map.rocks:
                c, _, _ = r.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True
                    break
            if game_map.well:
                c, _, _ = game_map.well.check_collision(new_wx, new_wy, self.radius)
                if c:
                    hit_obstacle = True

            if hit_obstacle:
                # Bateu em pedra durante o corte! Ricocheteia e fica atordoado
                self.stun(duration=1.0)
                return

            self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))
            self.slash_trail_points.append((self.wx, self.wy))
            if len(self.slash_trail_points) > 12:
                self.slash_trail_points.pop(0)
            self.hitbox_center = (self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8)

            if self.state_timer <= 0:
                # Fim do avanço: entra no RECOVERY embainhando a espada (Noto caminhando a 50%)
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False
                self.slash_trail_points.clear()

        elif self.state == STATE_RECOVERY:
            # Kenshi embainha a katana (Noto) podendo caminhar a 50% da velocidade
            self.state_timer -= dt
            self.hitbox_active = False
            self.slash_trail_points.clear()
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == "SHUKUCHI":
            self.state_timer -= dt
            step = self.shukuchi_speed * dt
            new_wx = self.wx + self.facing_x * step
            new_wy = self.wy + self.facing_y * step

            # Cortar bambus no caminho com a velocidade extrema do passo relâmpago
            for b in game_map.bamboos:
                if not b.is_cut:
                    b_dist = math.hypot(new_wx - b.wx, new_wy - b.wy)
                    if b_dist < 0.55:
                        part = b.cut((self.facing_x, self.facing_y))
                        if part and particles is not None:
                            particles.append(part)

            # Parar em obstáculos sólidos
            hit_col = False
            for r in game_map.rocks:
                c, _, _ = r.check_collision(new_wx, new_wy, self.radius)
                if c: hit_col = True; break
            if game_map.well:
                c, _, _ = game_map.well.check_collision(new_wx, new_wy, self.radius)
                if c: hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            # Gerar pós-imagens sucessivas (Zanzou)
            self.zanzou_spawn_timer += dt
            if self.zanzou_spawn_timer >= 0.035:
                self.zanzou_spawn_timer = 0.0
                self.zanzou_ghosts.append({
                    "wx": self.wx, "wy": self.wy, "wz": self.wz,
                    "facing_x": self.facing_x, "facing_y": self.facing_y,
                    "alpha": 180, "duration": 0.28
                })

            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.post_shukuchi_iframe_timer = 0.12
                self.is_invulnerable_dodge = True
                self.roll_recovery_timer = self.roll_recovery_duration
                self.roll_cooldown_timer = self.roll_cooldown_duration
                self.dash_recovery_timer = self.roll_recovery_duration

        elif self.state == "RYUU_TSUI_SEN":
            # Entregável 2.1.2: Salto Parabólico em 3 fases (ASCEND -> APEX -> DESCEND) com sombras Shukuchi
            self.state_timer -= dt
            self.ryuu_phase_timer -= dt

            if self.ryuu_phase == "ASCEND":
                prog = max(0.0, min(1.0, 1.0 - (self.ryuu_phase_timer / max(0.001, self.ryuu_ascend_duration))))
                # Curva parabólica explosiva de subida até 2.6m
                ease_out = 1.0 - (1.0 - prog) * (1.0 - prog)
                self.wz = self.ryuu_start_wz + (self.ryuu_apex_wz - self.ryuu_start_wz) * ease_out
                self.is_invulnerable_dodge = True
                self.hitbox_active = False

                # Leve avanço parabólico em direção ao alvo durante o salto
                if game_map is not None:
                    adv = 4.5 * dt
                    nx, ny = slide_movement_against_obstacles(self.wx, self.wy, self.facing_x * adv, self.facing_y * adv, self.radius, game_map)
                    min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                    self.wx = max(min_x, min(max_x, nx))
                    self.wy = max(min_y, min(max_y, ny))

                # Gerar sombras Zanzou estilo Shukuchi na subida aérea!
                self.zanzou_spawn_timer += dt
                if self.zanzou_spawn_timer >= 0.024:
                    self.zanzou_spawn_timer = 0.0
                    self.zanzou_ghosts.append({
                        "wx": self.wx, "wy": self.wy, "wz": self.wz,
                        "facing_x": self.facing_x, "facing_y": self.facing_y,
                        "alpha": 195, "duration": 0.26
                    })

                if self.ryuu_phase_timer <= 0.0:
                    self.ryuu_phase = "APEX"
                    self.ryuu_phase_timer = self.ryuu_apex_duration
                    self.wz = self.ryuu_apex_wz

            elif self.ryuu_phase == "APEX":
                # Paira no ápice com a katana erguida acima da cabeça com as duas mãos e brilho dourado
                self.wz = self.ryuu_apex_wz
                self.is_invulnerable_dodge = True
                self.hitbox_active = False
                if self.ryuu_phase_timer <= 0.0:
                    self.ryuu_phase = "DESCEND"
                    self.ryuu_phase_timer = self.ryuu_descend_duration

            else:
                # DESCEND: Queda meteórica vertical com corte de cima para baixo
                prog = max(0.0, min(1.0, 1.0 - (self.ryuu_phase_timer / max(0.001, self.ryuu_descend_duration))))
                ease_in = prog * prog
                self.wz = max(0.0, self.ryuu_apex_wz * (1.0 - ease_in))

                if self.wz > 1.8:
                    self.is_invulnerable_dodge = True
                    self.hitbox_active = False
                else:
                    self.is_invulnerable_dodge = (self.wz > 1.2)
                    self.hitbox_active = True
                    self.hitbox_radius = 1.45
                    self.slash_dir = (self.facing_x, self.facing_y)
                    self.hitbox_center = (self.wx + self.facing_x * 0.80, self.wy + self.facing_y * 0.80)
                    self.slash_trail_points.append((self.wx, self.wy))

                if self.wz <= 0.0 or self.ryuu_phase_timer <= 0.0 or self.state_timer <= 0.0:
                    self.wz = 0.0
                    self.state = STATE_RECOVERY
                    self.state_timer = 0.28
                    self.hitbox_active = False
                    self.is_invulnerable_dodge = False
                    if particles is not None:
                        from src.effects.particles import SparkParticle, SmokeParticle
                        for _ in range(16):
                            particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.2))
                        for _ in range(8):
                            particles.append(SmokeParticle(self.wx, self.wy, 0.1, color=(240, 240, 250), size=6))

        elif self.state == "TSUKA_ATE":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_DASH:
            self.state = "SHUKUCHI"
            self.state_timer = self.shukuchi_duration
            self.is_invulnerable_dodge = True

        elif self.state == "PARRY_BACKHOP":
            self.state_timer -= dt
            step = self.parry_hop_speed * dt
            dx = self.parry_hop_dir[0] * step
            dy = self.parry_hop_dir[1] * step

            if game_map is not None:
                new_wx, new_wy = slide_movement_against_obstacles(self.wx, self.wy, dx, dy, self.radius, game_map)
                if getattr(game_map, "has_rails", False):
                    new_wx, new_wy = self.block_pit_entry(game_map, new_wx, new_wy)
                min_x, min_y, max_x, max_y = resolve_playable_bounds(game_map)
                self.wx = max(min_x, min(max_x, new_wx))
                self.wy = max(min_y, min(max_y, new_wy))
            else:
                self.wx += dx
                self.wy += dy

            prog = max(0.0, min(1.0, 1.0 - (self.state_timer / max(0.001, self.parry_hop_duration))))
            # Atualização da altura vertical (Z) e rotação acrobática
            if getattr(self, "is_aerial_parry", False):
                # Deflexão aérea (Ryuu Tsui Sen): mortal para trás de 360° no ar usando o impulso da lâmina!
                self.somersault_angle = prog * 360.0
                start_z = getattr(self, "parry_hop_start_wz", 1.5)
                arc_boost = math.sin(prog * math.pi) * 0.45
                self.wz = max(0.0, start_z * (1.0 - prog) + arc_boost)
                landed = (self.state_timer <= 0.0)
            else:
                # Salto parabólico terrestre animado de recuo (~2.7 tiles para trás)
                self.somersault_angle = 0.0
                self.wz = max(0.0, math.sin(prog * math.pi) * 0.55)
                landed = (self.state_timer <= 0.0)

            # Efeito de rastro zanzou suave
            self.zanzou_spawn_timer += dt
            if self.zanzou_spawn_timer >= 0.045:
                self.zanzou_spawn_timer = 0.0
                self.zanzou_ghosts.append({
                    "wx": self.wx, "wy": self.wy, "wz": self.wz,
                    "facing_x": self.facing_x, "facing_y": self.facing_y,
                    "alpha": 145, "duration": 0.22
                })

            if landed or self.state_timer <= 0:
                self.wz = 0.0
                self.somersault_angle = 0.0
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration * 0.70  # Embainhamento (Noto) ao aterrissar a distância segura
                self.hitbox_active = False
                self.is_invulnerable_dodge = False
                # Permite caminhar imediatamente durante o embainhamento (Noto) pós-aterrissagem!
                self.roll_recovery_timer = 0.0
                self.roll_cooldown_timer = self.roll_cooldown_duration
                self.dash_recovery_timer = 0.0
                if particles is not None:
                    from src.effects.particles import SmokeParticle, SparkParticle
                    for _ in range(6):
                        particles.append(SmokeParticle(self.wx, self.wy, 0.12, color=(230, 230, 235), size=5))
                    for _ in range(4):
                        particles.append(SparkParticle(self.wx, self.wy, 0.3, color=(240, 240, 255)))

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.wz > 0:
                self.wz = max(0.0, self.wz - 10.0 * dt)
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.wz = 0.0

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Samurai Vermelho e suas pós-imagens Shukuchi no estilo Voxel 3D com SSAA 2x e Pose LERP."""
        # Renderizar rastro brilhante do corte do Iai no chão apenas durante o golpe e se estiver viva
        if self.is_alive and self.state in (STATE_ATTACK, "RYUU_TSUI_SEN") and len(self.slash_trail_points) >= 2:
            pts = [camera.apply(px, py, 0.05) for px, py in self.slash_trail_points]
            if len(pts) >= 2:
                pygame.draw.lines(surface, COLOR_RED_AURA, False, pts, 4)
                pygame.draw.lines(surface, COLOR_WHITE, False, pts, 2)

        # Renderizar pós-imagens zanzou translúcidas deixadas pelo Shukuchi / Ryuu Tsui Sen
        if hasattr(self, "zanzou_ghosts") and self.state not in ("VICTORY", "INTRO"):
            for g in self.zanzou_ghosts:
                if g["alpha"] > 20:
                    render_voxel_humanoid(
                        surface, camera,
                        g["wx"], g["wy"], g.get("wz", self.wz),
                        g["facing_x"], g["facing_y"],
                        "IDLE", 0.0, True,
                        char_type="kenshin",
                        alpha=g["alpha"]
                    )

        # Indicador de stealth (camuflagem no bambuzal)
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        # Determinar pose especial ativa (Koiguchi-kiri startup ou Noto sheathing)
        active_pose = ""
        if self.state == STATE_ATTACK and getattr(self, "iai_startup_timer", 0.0) > 0.0:
            active_pose = "koiguchi_glint"
        elif self.state == STATE_RECOVERY:
            active_pose = "noto_sheath"

        extra_props = {
            "ssaa_2x": getattr(self, "ssaa_enabled", True),
            "pose_lerp_tracker": getattr(self, "_pose_lerp_tracker", None),
            "ryuu_phase": getattr(self, "ryuu_phase", "DESCEND"),
            "is_aerial_parry": getattr(self, "is_aerial_parry", False),
            "somersault_angle": getattr(self, "somersault_angle", 0.0),
        }
        if active_pose:
            extra_props["pose"] = active_pose

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="kenshin",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props=extra_props,
        )
