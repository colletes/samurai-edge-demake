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

        # Efeito visual de rastro de lâmina
        self.slash_trail_points: list[tuple[float, float]] = []

    def can_move(self) -> bool:
        """Kenshin pode se movimentar em IDLE, WALK e durante o RECOVERY (guardando a espada na bainha)."""
        return self.is_alive and self.state in (STATE_IDLE, STATE_WALK, STATE_RECOVERY)

    def apply_movement(self, move_x: float, move_y: float, dt: float, game_map):
        if not self.can_move():
            return
        if self.state == STATE_RECOVERY:
            # Movimento gracioso (75% da velocidade) enquanto embainha a katana (Noto)
            self.is_moving = (move_x != 0 or move_y != 0)
            if not self.is_moving:
                return
            self.walk_cycle += dt * 8.0
            current_speed = self.speed * 0.75
            if self.slow_timer > 0:
                current_speed *= 0.35
                self.slow_timer -= dt
            if game_map.is_water(self.wx, self.wy):
                current_speed *= 0.55

            new_wx = self.wx + move_x * current_speed * dt
            new_wy = self.wy + move_y * current_speed * dt
            self.facing_x = move_x
            self.facing_y = move_y

            new_wx = max(1.0, min(game_map.cols - 1.0, new_wx))
            new_wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            for rock in game_map.rocks:
                col, ox, oy = rock.check_collision(new_wx, new_wy, self.radius)
                if col:
                    new_wx, new_wy = ox, oy
            if game_map.well:
                col, ox, oy = game_map.well.check_collision(new_wx, new_wy, self.radius)
                if col:
                    new_wx, new_wy = ox, oy
            self.wx, self.wy = new_wx, new_wy
        else:
            super().apply_movement(move_x, move_y, dt, game_map)

    def trigger_iai_attack(self, target_wx: float, target_wy: float):
        """Inicia o golpe Iai-jutsu se puder agir."""
        if self.state not in (STATE_IDLE, STATE_WALK):
            return

        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = self.dash_duration
        self.hitbox_active = True
        self.hitbox_radius = 1.25  # Arco ampliado para 1.25 para consistência do corte
        self.slash_dir = (self.facing_x, self.facing_y)
        self.slash_trail_points = [(self.wx, self.wy)]
        self.hitbox_center = (self.wx + self.facing_x * 0.8, self.wy + self.facing_y * 0.8)

    def trigger_dash(self, dir_x: float, dir_y: float):
        """Passo Relâmpago Shukuchi (縮地): Deslocamento veloz com pós-imagens."""
        if self.state not in (STATE_IDLE, STATE_WALK):
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

        if self.state == STATE_ATTACK:
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

        elif self.state == STATE_DASH:
            self.state = "SHUKUCHI"
            self.state_timer = 0.15

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
