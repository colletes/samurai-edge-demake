"""
Entidades de Itens e Coletáveis da Arena.
Contém o PowderPouch (saquinho / chifre de pólvora dourado coletado pelo Teppo).
"""
import math
import random
import pygame
from src.isometric.iso_math import world_to_iso
from src.config import COLOR_GOLD, COLOR_WHITE

class PowderPouch:
    def __init__(self, wx: float, wy: float):
        self.wx = wx
        self.wy = wy
        self.wz = 0.0
        self.radius = 0.40
        self.is_active = True
        self.respawn_timer = 0.0
        self.glow_timer = random.uniform(0.0, math.pi * 2)

    @classmethod
    def spawn_random(cls, game_map):
        p = cls(0.0, 0.0)
        p.respawn(game_map)
        return p

    @classmethod
    def spawn_near(cls, game_map, origin_wx: float, origin_wy: float, min_dist: float = 3.8, max_dist: float = 5.0):
        """Gera um pouch a uma distância média de um combatente em terreno firme."""
        p = cls(0.0, 0.0)
        for _ in range(150):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(min_dist, max_dist)
            rx = round(origin_wx + math.cos(angle) * dist, 1)
            ry = round(origin_wy + math.sin(angle) * dist, 1)
            if not (2.0 <= rx <= game_map.cols - 2.0 and 2.0 <= ry <= game_map.rows - 2.0):
                continue
            if game_map.is_water(rx, ry):
                continue
            if any(math.hypot(rx - r.wx, ry - r.wy) < (r.radius + 0.6) for r in game_map.rocks):
                continue
            if game_map.well and math.hypot(rx - game_map.well.wx, ry - game_map.well.wy) < 1.6:
                continue
            p.wx = rx
            p.wy = ry
            p.is_active = True
            p.respawn_timer = 0.0
            return p
        return cls.spawn_random(game_map)

    @classmethod
    def create_arena_pouches(cls, game_map, fighters: list = None, total_pouches: int = 3):
        """
        Cria os pouches para o início do round.
        Se houver Teppo (Rifleman) entre os lutadores, garante que 1 dos 3 nasça a uma
        distância média (~3.8m a 5.0m) dele, e os demais aleatoriamente pela arena.
        """
        pouches = []
        riflemen = [f for f in (fighters or []) if getattr(f, "char_type", "") in ("rifleman", "teppo")]
        if riflemen:
            teppo = riflemen[0]
            pouches.append(cls.spawn_near(game_map, teppo.wx, teppo.wy, min_dist=3.8, max_dist=5.0))

        while len(pouches) < total_pouches:
            pouches.append(cls.spawn_random(game_map))

        return pouches

    def update(self, dt: float, game_map, particles: list = None):
        self.glow_timer += dt * 4.0
        if not self.is_active:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn(game_map)

    def respawn(self, game_map):
        """Reaparece em uma posição válida aleatória de terra firme."""
        for _ in range(100):
            rx = round(random.uniform(3.0, game_map.cols - 3.0), 1)
            ry = round(random.uniform(3.0, game_map.rows - 3.0), 1)
            if game_map.is_water(rx, ry):
                continue
            if any(math.hypot(rx - r.wx, ry - r.wy) < (r.radius + 0.6) for r in game_map.rocks):
                continue
            if game_map.well and math.hypot(rx - game_map.well.wx, ry - game_map.well.wy) < 1.6:
                continue
            self.wx = rx
            self.wy = ry
            self.is_active = True
            self.respawn_timer = 0.0
            break

    def render(self, surface: pygame.Surface, camera, font: pygame.font.Font = None):
        if not self.is_active:
            return

        from src.isometric.voxel_renderer import draw_voxel_box

        # Sombra suave no chão
        base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
        pygame.draw.ellipse(surface, (14, 18, 16), (base_sx - 18, base_sy - 9, 36, 18))

        # Efeito de brilho de solo sutil (aura de munição)
        pulse = 0.5 + 0.5 * math.sin(self.glow_timer * 3.0)
        ground_glow_rad = int(14 + pulse * 6)
        ground_glow = pygame.Surface((ground_glow_rad * 2, ground_glow_rad * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(ground_glow, (255, 175, 40, int(40 + pulse * 35)), (0, ground_glow_rad // 2, ground_glow_rad * 2, ground_glow_rad))
        surface.blit(ground_glow, (base_sx - ground_glow_rad, base_sy - ground_glow_rad // 2))

        # -----------------------------------------------------------------
        # MODELO VOXEL 3D: BARRIL FEUDAL DE PÓLVORA NEGRA (TARU DE PÓLVORA)
        # -----------------------------------------------------------------
        # 1. Aro inferior de ferro forjado
        draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.22, 0.0, 0.44, 0.44, 0.09, (38, 42, 46))
        # 2. Corpo do barril em madeira escura tratada
        draw_voxel_box(surface, camera, self.wx - 0.25, self.wy - 0.25, 0.08, 0.50, 0.50, 0.22, (82, 48, 26))
        # 3. Faixa central carmesim de pólvora militar feudal (com selo de fogo)
        draw_voxel_box(surface, camera, self.wx - 0.26, self.wy - 0.26, 0.16, 0.52, 0.52, 0.07, (175, 40, 32))
        # 4. Aro superior de ferro forjado
        draw_voxel_box(surface, camera, self.wx - 0.22, self.wy - 0.22, 0.29, 0.44, 0.44, 0.08, (38, 42, 46))
        # 5. Tampa de madeira do barril
        draw_voxel_box(surface, camera, self.wx - 0.19, self.wy - 0.19, 0.36, 0.38, 0.38, 0.06, (95, 58, 32))
        # 6. Batoque / Pavio trançado de corda
        draw_voxel_box(surface, camera, self.wx - 0.04, self.wy - 0.04, 0.42, 0.08, 0.08, 0.10, (190, 150, 90))
        # 7. Brasa no topo do pavio (ponto quente sutil)
        ember_color = (255, 140 + int(pulse * 80), 30)
        draw_voxel_box(surface, camera, self.wx - 0.03, self.wy - 0.03, 0.51, 0.06, 0.06, 0.05, ember_color, outline=False)

        # -----------------------------------------------------------------
        # SETA INDICADORA FLUTUANTE (BOBBING ARROW) & BADGE "PÓLVORA"
        # -----------------------------------------------------------------
        arrow_sx, arrow_sy = camera.apply(self.wx, self.wy, 0.85)
        bob = math.sin(self.glow_timer * 4.0) * 7.0
        tip_y = arrow_sy + bob
        tip_x = arrow_sx

        # Vértices da seta estilizada apontando para baixo
        arrow_pts = [
            (tip_x, tip_y),                     # Ponta da seta
            (tip_x - 11, tip_y - 13),           # Canto esquerdo da ponta
            (tip_x - 5, tip_y - 13),            # Recuo esquerdo
            (tip_x - 5, tip_y - 23),            # Haste esquerda
            (tip_x + 5, tip_y - 23),            # Haste direita
            (tip_x + 5, tip_y - 13),            # Recuo direito
            (tip_x + 11, tip_y - 13)            # Canto direito da ponta
        ]

        # Sombra externa da seta
        shadow_pts = [(x, y + 2) for x, y in arrow_pts]
        pygame.draw.polygon(surface, (15, 18, 16), shadow_pts)

        # Preenchimento e contorno da seta em tons quentes dourados
        arrow_color = (255, 210, 45)
        arrow_border = (160, 110, 20)
        pygame.draw.polygon(surface, arrow_color, arrow_pts)
        pygame.draw.polygon(surface, arrow_border, arrow_pts, 2)

        # Mini Badge com texto luminoso [ PÓLVORA / POWDER ]
        badge_y = tip_y - 36
        if font is None:
            font = pygame.font.Font(None, 16)

        from src.i18n import t
        lbl = font.render(t("powder_badge"), True, (255, 240, 160))
        bw = lbl.get_width() + 10
        bh = 16
        bx = tip_x - bw // 2

        b_rect = pygame.Rect(bx, badge_y, bw, bh)
        pygame.draw.rect(surface, (18, 24, 21), b_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 200, 50), b_rect, 1, border_radius=4)
        surface.blit(lbl, (b_rect.centerx - lbl.get_width() // 2, b_rect.centery - lbl.get_height() // 2 + 1))


