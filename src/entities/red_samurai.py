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
    STATE_DASH, STATE_STUNNED, STATE_DEAD
)
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.iso_math import world_to_iso

class RedSamurai(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Kenshi")
        self.char_type = "kenshin"
        self.speed = 5.4  # Agilidade máxima do retalhador

        # Parâmetros do Iai-jutsu
        self.dash_speed = 22.0
        self.dash_duration = 0.16   # Avanço supersônico
        self.recovery_duration = 0.80 # Calibrado: cooldown justo embainhando a katana!
        self.attack_range = 2.4

        # Ação Secundária: Ryuu Tsui Sen (竜槌閃 - Item 17)
        self.ryuu_cooldown = 3.5
        self.ryuu_timer = 0.0

        # Efeito visual de rastro de lâmina
        self.slash_trail_points: list[tuple[float, float]] = []

    def can_act(self) -> bool:
        """Kenshi pode agir se estiver viva, em IDLE/WALK e sem recovery de dash."""
        return self.is_alive and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY) and self.dash_recovery_timer <= 0

    def can_move(self) -> bool:
        """Kenshi pode se mover livremente enquanto embainha a katana (STATE_RECOVERY)."""
        if self.state == STATE_RECOVERY:
            return self.is_alive
        return super().can_move()

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        """Aplica movimentação mantendo o estado de RECOVERY (embainhar/noto) se aplicável."""
        if self.state == STATE_RECOVERY:
            saved_state = self.state
            super().apply_movement(move_x, move_y, dt, game_map)
            self.state = saved_state
        else:
            super().apply_movement(move_x, move_y, dt, game_map)

    def trigger_iai_attack(self, target_wx: float, target_wy: float):
        """Inicia o golpe Iai-jutsu se puder agir."""
        if not self.can_act():
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.dash_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.25  # Arco ampliado para 1.25 para consistência do corte
        self.slash_dir = (self.facing_x, self.facing_y)
        self.slash_trail_points = [(self.wx, self.wy)]
        self.hitbox_center = (self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8)

    def trigger_ryuu_tsui_sen(self, target_wx: float, target_wy: float, particles: list = None, banners: list = None, opponent = None):
        """
        Ação Secundária: Ryuu Tsui Sen (竜槌閃 - Item 17).
        Kenshi desaparece com blur de velocidade, salta alto no ar acima de sua posição
        e despenca com um devastador corte vertical descendente com a katana.
        """
        if not self.can_act() or self.ryuu_timer > 0:
            return

        self.set_facing(target_wx, target_wy)
        self.ryuu_timer = self.ryuu_cooldown
        self.state = "RYUU_TSUI_SEN"
        self.state_timer = 0.38
        self.is_invulnerable_dodge = True
        self.hitbox_active = False

        # Pós-imagem de velocidade inicial
        if not hasattr(self, "zanzou_ghosts"):
            self.zanzou_ghosts = []
        self.zanzou_ghosts.append({
            "wx": self.wx, "wy": self.wy,
            "facing_x": self.facing_x, "facing_y": self.facing_y,
            "alpha": 220, "duration": 0.35
        })

        if particles is not None:
            from src.effects.particles import SparkParticle
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.4))

    def trigger_tsuka_ate(self, target_wx: float, target_wy: float, particles: list = None, opponent = None, banners: list = None):
        """Compatibilidade: redireciona para Ryuu Tsui Sen."""
        self.trigger_ryuu_tsui_sen(target_wx, target_wy, particles=particles, banners=banners, opponent=opponent)

    def trigger_dash(self, dir_x: float, dir_y: float):
        """Terceira Ação: Passo Relâmpago Shukuchi (縮地) — Deslocamento veloz com pós-imagens e i-frames."""
        if not self.is_alive or self.state not in (STATE_IDLE, STATE_WALK) or self.dash_recovery_timer > 0:
            return
        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y # Recuo para trás
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.state = "SHUKUCHI"
        self.state_timer = 0.15
        self.shukuchi_speed = 28.0
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.zanzou_spawn_timer = 0.0
        # Registrar primeira pós-imagem fantasma (zanzou)
        if not hasattr(self, "zanzou_ghosts"):
            self.zanzou_ghosts = []
        self.zanzou_ghosts.append({
            "wx": self.wx, "wy": self.wy,
            "facing_x": self.facing_x, "facing_y": self.facing_y,
            "alpha": 200, "duration": 0.28
        })

    def update(self, dt: float, game_map, particles: list = None):
        """Atualiza os estados e timings do Samurai Vermelho."""
        if not hasattr(self, "zanzou_ghosts"):
            self.zanzou_ghosts = []

        # Atualizar e desvanecer pós-imagens zanzou
        for g in self.zanzou_ghosts:
            g["duration"] -= dt
            g["alpha"] = max(0, int(200 * (g["duration"] / 0.28)))
        self.zanzou_ghosts = [g for g in self.zanzou_ghosts if g["duration"] > 0]

        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.ryuu_timer > 0:
            self.ryuu_timer -= dt
        if self.dash_recovery_timer > 0:
            self.dash_recovery_timer -= dt
            # Avanço relâmpago Iai
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
            self.hitbox_center = (self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8)

            if self.state_timer <= 0:
                # Fim do avanço: entra no LONGO RECOVERY embainhando a espada
                self.state = STATE_RECOVERY
                self.state_timer = self.recovery_duration
                self.hitbox_active = False

        elif self.state == STATE_RECOVERY:
            # Samurai fica travado no cooldown vulnerável
            self.state_timer -= dt
            self.hitbox_active = False
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.slash_trail_points.clear()

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
                    "wx": self.wx, "wy": self.wy,
                    "facing_x": self.facing_x, "facing_y": self.facing_y,
                    "alpha": 180, "duration": 0.28
                })

            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_invulnerable_dodge = False
                self.dash_recovery_timer = self.dash_recovery_duration

        elif self.state == "RYUU_TSUI_SEN":
            self.state_timer -= dt
            progress = max(0.0, min(1.0, 1.0 - (self.state_timer / 0.38)))
            # Salto vertical parabólico até o ápice e queda veloz cortando com a katana (Item 17)
            self.wz = math.sin(progress * math.pi) * 1.65

            if progress < 0.45:
                self.is_invulnerable_dodge = True
                self.hitbox_active = False
            else:
                # Descendo com o corte vertical
                self.is_invulnerable_dodge = False
                self.hitbox_active = True
                self.hitbox_radius = 1.35
                self.slash_dir = (self.facing_x, self.facing_y)
                self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)

            if self.state_timer <= 0:
                self.wz = 0.0
                self.state = STATE_RECOVERY
                self.state_timer = 0.22
                self.hitbox_active = False
                self.is_invulnerable_dodge = False
                if particles is not None:
                    from src.effects.particles import SparkParticle
                    for _ in range(14):
                        particles.append(SparkParticle(self.wx + self.facing_x * 0.6, self.wy + self.facing_y * 0.6, 0.5))

        elif self.state == "TSUKA_ATE":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_DASH:
            self.state = "SHUKUCHI"
            self.state_timer = 0.15
            self.is_invulnerable_dodge = True

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Samurai Vermelho e suas pós-imagens Shukuchi no estilo Voxel 3D."""
        # Renderizar rastro brilhante do corte do Iai no chão
        if len(self.slash_trail_points) >= 2:
            pts = [camera.apply(px, py, 0.05) for px, py in self.slash_trail_points]
            if len(pts) >= 2:
                pygame.draw.lines(surface, COLOR_RED_AURA, False, pts, 4)
                pygame.draw.lines(surface, COLOR_WHITE, False, pts, 2)

        # Renderizar pós-imagens zanzou translúcidas deixadas pelo Shukuchi
        if hasattr(self, "zanzou_ghosts"):
            for g in self.zanzou_ghosts:
                if g["alpha"] > 20:
                    render_voxel_humanoid(
                        surface, camera,
                        g["wx"], g["wy"], self.wz,
                        g["facing_x"], g["facing_y"],
                        "IDLE", 0.0, True,
                        char_type="kenshin",
                        alpha=g["alpha"]
                    )

        # Indicador de stealth (camuflagem no bambuzal)
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="kenshin",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving
        )
