"""
HUD Rondel Onmyōdō (Bússola dos 6 Elementos de Seimei):
Renderizador de alta fidelidade visual para o mostrador elemental de Seimei no rodapé da tela.
- Estilo: Bússola cerimonial de bronze Heian patinado, laca urushi escura e incrustações em folha de ouro.
- Elementos: Madeira (木), Fogo (火), Terra (土), Metal (金), Água (水), Yin-Yang / Oráculo (☯).
- Dinâmica: Rotação suave animada (60° por avanço) com gemas pulsantes e indicador superior luminoso.
"""
import math
import random
import pygame
from src.config import COLOR_GOLD
from src.ui.fonts import get_text_font, get_title_font
from src.entities.seimei import ELEMENT_SPELL_NAMES, ELEMENT_COLORS

ELEMENT_DATA = [
    {
        "id": "wood",
        "kanji": "木",
        "name": "MADEIRA",
        "jp_name": "Moku",
        "color": (45, 215, 120),
        "glow_color": (30, 170, 90),
        "spell_primary": "Kusabi-Bari",
        "spell_secondary": "Shinju no Ibuki",
        "gem_color": (35, 185, 95),
    },
    {
        "id": "fire",
        "kanji": "火",
        "name": "FOGO",
        "jp_name": "Ka",
        "color": (255, 75, 45),
        "glow_color": (210, 40, 30),
        "spell_primary": "Guren no Ofuda",
        "spell_secondary": "Hi-bashira",
        "gem_color": (220, 50, 35),
    },
    {
        "id": "earth",
        "kanji": "土",
        "name": "TERRA",
        "jp_name": "Do",
        "color": (235, 185, 65),
        "glow_color": (195, 140, 40),
        "spell_primary": "Ganseki-dan",
        "spell_secondary": "Doryū-heki",
        "gem_color": (205, 155, 45),
    },
    {
        "id": "metal",
        "kanji": "金",
        "name": "METAL",
        "jp_name": "Kin",
        "color": (245, 248, 255),
        "glow_color": (180, 195, 225),
        "spell_primary": "Hagane no Yaiba",
        "spell_secondary": "Kongō-jin",
        "gem_color": (215, 225, 245),
    },
    {
        "id": "water",
        "kanji": "水",
        "name": "ÁGUA",
        "jp_name": "Sui",
        "color": (65, 175, 255),
        "glow_color": (35, 115, 215),
        "spell_primary": "Suiryū no Ya",
        "spell_secondary": "Kagami-Mizu",
        "gem_color": (45, 140, 235),
    },
    {
        "id": "yinyang",
        "kanji": "☯",
        "name": "ORÁCULO",
        "jp_name": "In-Yō",
        "color": (225, 160, 255),
        "glow_color": (160, 85, 215),
        "spell_primary": "Senkō / Kurayami",
        "spell_secondary": "Tenmei no Senkoku",
        "gem_color": (190, 110, 240),
    },
]

NUM_ELEMENTS = len(ELEMENT_DATA)  # 6
ANGLE_PER_ELEMENT = 360.0 / NUM_ELEMENTS  # 60.0 graus


class RondelHUD:
    """Gerencia a renderização em laca, rotação e partículas do mostrador de Seimei."""
    _instance = None

    def __init__(self):
        self.current_angle = 0.0
        self.target_angle = 0.0
        self.pulse_timer = 0.0
        self.spark_particles: list[dict] = []
        self._cached_disc: pygame.Surface | None = None
        self._disc_size = 136

    @classmethod
    def get(cls) -> "RondelHUD":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build_procedural_textured_disc(self) -> pygame.Surface:
        """Cria o disco texturizado com camadas de bronze, laca urushi e anéis em folha de ouro."""
        size = self._disc_size
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        r_outer = size // 2 - 4

        # 1. Sombra projetada do artefato
        pygame.draw.circle(surf, (8, 10, 12, 180), (cx, cy + 3), r_outer)

        # 2. Aro externo de bronze fundido patinado
        pygame.draw.circle(surf, (42, 36, 32), (cx, cy), r_outer)
        pygame.draw.circle(surf, (72, 60, 50), (cx, cy), r_outer, 2)
        pygame.draw.circle(surf, (28, 24, 22), (cx, cy), r_outer - 3)

        # 3. Anel intermediário em filigrana de ouro batido
        pygame.draw.circle(surf, (218, 175, 75), (cx, cy), r_outer - 5, 2)
        pygame.draw.circle(surf, (160, 120, 45), (cx, cy), r_outer - 7, 1)

        # 4. Miolo de laca Urushi preta acetinada
        pygame.draw.circle(surf, (18, 16, 20), (cx, cy), r_outer - 8)

        # 5. Entalhes radiais dourados (trigramas sutis a cada 60 graus)
        for i in range(NUM_ELEMENTS):
            ang = math.radians(i * ANGLE_PER_ELEMENT - 90)
            x1 = cx + math.cos(ang) * (r_outer - 28)
            y1 = cy + math.sin(ang) * (r_outer - 28)
            x2 = cx + math.cos(ang) * (r_outer - 10)
            y2 = cy + math.sin(ang) * (r_outer - 10)
            pygame.draw.line(surf, (140, 105, 38), (x1, y1), (x2, y2), 1)

        # 6. Cubo central / orbe de fixação com estrela Onmyodo de 5 pontas estilizada
        pygame.draw.circle(surf, (36, 30, 26), (cx, cy), 14)
        pygame.draw.circle(surf, (218, 175, 75), (cx, cy), 14, 2)
        pygame.draw.circle(surf, (250, 220, 110), (cx, cy), 5)

        return surf

    def render(self, surface: pygame.Surface, seimei_fighter, center_x: int, center_y: int, dt: float = 0.016):
        """Renderiza o Rondel Onmyōdō no rodapé com animação, iluminação de gemas e runas."""
        if self._cached_disc is None:
            self._cached_disc = self._build_procedural_textured_disc()

        active_idx = getattr(seimei_fighter, "rondel_index", 0) % NUM_ELEMENTS
        self.target_angle = active_idx * ANGLE_PER_ELEMENT

        # Interpolação angular suave (curva com amortecimento suave para avanço de 60 graus)
        diff = (self.target_angle - self.current_angle)
        # Normalização de volta mais curta
        diff = (diff + 180) % 360 - 180
        if abs(diff) > 0.01:
            self.current_angle += diff * min(1.0, dt * 14.0)
        else:
            self.current_angle = self.target_angle

        self.pulse_timer += dt * 3.5
        pulse = 0.75 + 0.25 * math.sin(self.pulse_timer)

        size = self._disc_size
        cx, cy = size // 2, size // 2
        r_outer = size // 2 - 4
        gem_radius_orbit = r_outer - 19

        # Superfície giratória para o disco base e os elementos
        rotating_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        rotating_surf.blit(self._cached_disc, (0, 0))

        font_kanji = get_text_font(18)
        font_yinyang = get_text_font(16)

        # Desenhar os 6 receptáculos e kanjis na superfície que gira
        for i, el in enumerate(ELEMENT_DATA):
            # O elemento i fica posicionado no ângulo base + rotação do disco
            # Ângulo relativo no disco: quando i == 0 e rotação == 0, fica no topo (-90°)
            el_angle_deg = (i * ANGLE_PER_ELEMENT) - 90
            rad = math.radians(el_angle_deg)
            gx = cx + math.cos(rad) * gem_radius_orbit
            gy = cy + math.sin(rad) * gem_radius_orbit

            # Gema / Engaste
            is_active = (i == active_idx)
            c_gem = el["gem_color"]
            c_core = el["color"]

            # Engaste de metal escuro
            pygame.draw.circle(rotating_surf, (24, 20, 22), (int(gx), int(gy)), 13)
            pygame.draw.circle(rotating_surf, (160, 130, 60), (int(gx), int(gy)), 13, 1)

            # Brilho interno da gema
            gem_r = 11 if not is_active else 12
            pygame.draw.circle(rotating_surf, c_gem, (int(gx), int(gy)), gem_r)

            if is_active:
                # Destaque de gema ativa iluminada
                pygame.draw.circle(rotating_surf, (255, 255, 255), (int(gx), int(gy)), gem_r, 2)

            # Símbolo Kanji
            if el["id"] == "yinyang":
                # Desenho procedural vetorizado de Yin-Yang para perfeição visual anti-serrilhada
                r_yy = 8
                pygame.draw.circle(rotating_surf, (245, 245, 245), (int(gx), int(gy)), r_yy)
                pygame.draw.circle(rotating_surf, (15, 15, 20), (int(gx), int(gy)), r_yy, 1)
                # Metade escura
                rect_half = pygame.Rect(int(gx) - r_yy, int(gy) - r_yy, r_yy, r_yy * 2)
                pygame.draw.circle(rotating_surf, (15, 15, 20), (int(gx), int(gy) - r_yy // 2), r_yy // 2)
                pygame.draw.circle(rotating_surf, (245, 245, 245), (int(gx), int(gy) + r_yy // 2), r_yy // 2)
                # Pontos inversos
                pygame.draw.circle(rotating_surf, (245, 245, 245), (int(gx), int(gy) - r_yy // 2), 2)
                pygame.draw.circle(rotating_surf, (15, 15, 20), (int(gx), int(gy) + r_yy // 2), 2)
            else:
                kanji_str = el["kanji"]
                k_col = (255, 255, 255) if is_active else (225, 225, 220)
                try:
                    k_surf = font_kanji.render(kanji_str, True, k_col)
                    rotating_surf.blit(k_surf, (gx - k_surf.get_width() // 2, gy - k_surf.get_height() // 2 - 1))
                except Exception:
                    pass

        # Girar a superfície completa de acordo com a rotação atual para que o elemento ativo aponte para o TOP (12h)
        # Quando active_idx avança, rotacionamos o mostrador no sentido anti-horário pelo ângulo para levar a gema ao topo
        rot_angle = -self.current_angle
        rotated = pygame.transform.rotozoom(rotating_surf, rot_angle, 1.0)
        rw, rh = rotated.get_size()
        dest_x = center_x - rw // 2
        dest_y = center_y - rh // 2
        surface.blit(rotated, (dest_x, dest_y))

        # =========================================================================
        # EFEITOS FIXOS SUPERIORES (PONTEIRO DO ORÁCULO E BADGE DE FEITIÇO)
        # =========================================================================
        curr_el = ELEMENT_DATA[active_idx]
        cur_col = curr_el["color"]
        cur_glow = curr_el["glow_color"]

        # 1. Ponteiro / Agulha entalhada de ouro apontando para as 12 horas
        ptr_y = center_y - (r_outer - 12)
        ptr_tip = (center_x, ptr_y - 12)
        ptr_l = (center_x - 6, ptr_y + 4)
        ptr_r = (center_x + 6, ptr_y + 4)
        pygame.draw.polygon(surface, (12, 14, 16), [ptr_tip, ptr_l, ptr_r])
        pygame.draw.polygon(surface, COLOR_GOLD, [ptr_tip, ptr_l, ptr_r])
        pygame.draw.polygon(surface, (255, 245, 160), [ptr_tip, (center_x, ptr_y + 2), ptr_l])

        # 2. Halo de Brilho Místico Pulsante no topo (Elemento Ativo)
        halo_surf = pygame.Surface((44, 44), pygame.SRCALPHA)
        halo_alpha = int(140 * pulse)
        pygame.draw.circle(halo_surf, (*cur_glow, halo_alpha), (22, 22), int(18 * pulse))
        pygame.draw.circle(halo_surf, (*cur_col, int(halo_alpha * 0.7)), (22, 22), int(12 * pulse))
        surface.blit(halo_surf, (center_x - 22, ptr_y - 22), special_flags=pygame.BLEND_ADD)

        # 3. Partículas flutuantes desprendendo-se do rondel na cor do elemento ativo
        if random.random() < 0.35:
            self.spark_particles.append({
                "x": center_x + random.uniform(-18, 18),
                "y": ptr_y + random.uniform(-6, 6),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-1.2, -0.4),
                "life": 0.45,
                "color": cur_col,
                "size": random.randint(2, 3),
            })

        for sp in list(self.spark_particles):
            sp["x"] += sp["vx"]
            sp["y"] += sp["vy"]
            sp["life"] -= dt
            if sp["life"] <= 0:
                self.spark_particles.remove(sp)
            else:
                p_alpha = max(0, min(255, int(255 * (sp["life"] / 0.45))))
                sp_surf = pygame.Surface((sp["size"] * 2, sp["size"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(sp_surf, (*sp["color"], p_alpha), (sp["size"], sp["size"]), sp["size"])
                surface.blit(sp_surf, (int(sp["x"]) - sp["size"], int(sp["y"]) - sp["size"]), special_flags=pygame.BLEND_ADD)

        # 4. Placa / Flâmula de Feitiços Ativos do Elemento
        # Posicionada imediatamente acima do mostrador com moldura de laca
        badge_w = 230
        badge_h = 42
        badge_x = center_x - badge_w // 2
        badge_y = center_y - r_outer - badge_h - 10

        b_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        # Fundo laca Urushi com borda dourada
        pygame.draw.rect(b_surf, (15, 14, 18, 235), (0, 0, badge_w, badge_h), border_radius=6)
        pygame.draw.rect(b_surf, cur_col, (0, 0, badge_w, badge_h), 1, border_radius=6)
        pygame.draw.rect(b_surf, (180, 145, 60), (2, 2, badge_w - 4, badge_h - 4), 1, border_radius=5)

        # Título: [Elemento] + Próximo Feitiço Primário & Secundário
        f_sub = get_text_font(13)
        f_main = get_title_font(15)

        el_title = f"{curr_el['kanji']} {curr_el['name']} ({curr_el['jp_name']})"
        t_surf = f_main.render(el_title, True, cur_col)
        b_surf.blit(t_surf, (badge_w // 2 - t_surf.get_width() // 2, 3))

        sp_info = f"1: {curr_el['spell_primary']}  |  2: {curr_el['spell_secondary']}"
        sp_surf = f_sub.render(sp_info, True, (220, 215, 205))
        b_surf.blit(sp_surf, (badge_w // 2 - sp_surf.get_width() // 2, 21))

        surface.blit(b_surf, (badge_x, badge_y))
