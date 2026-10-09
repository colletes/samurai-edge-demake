"""
src/isometric/decal_renderer.py - Subsistema de Decalques e Overlays 2.5D (Técnica 3)

Renderiza camadas gráficas semi-transparentes de alta fidelidade (overlays/decalques)
ancoradas diretamente nos nós anatômicos tridimensionais do modelo de micro-voxels:
- Base volumétrica de micro-voxels sólida (sem distorções afins na rotação de câmera).
- Overlays com canal alfa (RGBA) desenhados com precisão cristalina.
- Verificação de orientação angular da normal da face para garantir que decalques frontais
  (olhos, maquiagem, fivelas) desapareçam quando a câmera estiver nas costas, e que
  decalques dorsais (brasão Makoto 誠, nós de quimono) só apareçam na vista traseira.
- Escalonamento suave pelo zoom da câmera com preservação de nitidez.
"""
import math
import pygame
from src.isometric.iso_math import rotate_xy

# Cache global de superfícies de decalques
_DECAL_CACHE: dict[str, pygame.Surface] = {}


def get_or_create_decal(name: str, width: int, height: int, builder_fn) -> pygame.Surface:
    """Retorna uma superfície RGBA do cache ou cria invocando a função geradora."""
    if name not in _DECAL_CACHE:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        builder_fn(surf)
        _DECAL_CACHE[name] = surf
    return _DECAL_CACHE[name]


def draw_decal_billboard(
    surface: pygame.Surface,
    camera,
    wx: float, wy: float, wz: float,
    decal_surf: pygame.Surface,
    normal_dir: tuple[float, float] = (0.0, 1.0),
    scale: float = 1.0,
    alpha: int = 255,
    facing_threshold: float = 0.05,
    offset_screen: tuple[int, int] = (0, 0)
) -> bool:
    """
    Renderiza um decalque ancorado no espaço 3D (wx, wy, wz).
    
    normal_dir: (nx, ny) normal do decalque no plano mundial (ex: (0, 1) = voltado para frente).
    facing_threshold: limiar do produto escalar com a direção da câmera para visibilidade.
    Retorna True se desenhado, False se descartado por ângulo ou profundidade.
    """
    # 1. Verificação angular de visibilidade da normal em relação ao azimute da câmera
    azimuth = getattr(camera, "azimuth", 0.0)
    rx, ry = rotate_xy(normal_dir[0], normal_dir[1], azimuth)
    facing_dot = rx + ry  # componente apontando na direção do observador

    if facing_dot < facing_threshold:
        return False  # Oculto (voltado para longe do observador)

    # 2. Projeção 3D -> Tela
    sx, sy = camera.apply(wx, wy, wz)
    sx += offset_screen[0]
    sy += offset_screen[1]

    # 3. Escalonamento pelo zoom da câmera
    zoom = getattr(camera, "zoom", 2.8)
    final_scale = (scale * zoom) / 2.8

    orig_w, orig_h = decal_surf.get_size()
    target_w = max(1, int(orig_w * final_scale))
    target_h = max(1, int(orig_h * final_scale))

    scaled_surf = pygame.transform.smoothscale(decal_surf, (target_w, target_h))

    # Modulação de alfa se necessário
    if alpha < 255:
        scaled_surf.set_alpha(alpha)

    # 4. Centralização do decalque na coordenada projetada
    dest_rect = scaled_surf.get_rect(center=(sx, sy))
    surface.blit(scaled_surf, dest_rect)
    return True


# =============================================================================
# BIBLIOTECA DE DECALQUES 2.5D — OKUNI
# =============================================================================

def _build_okuni_kabuki_face(surf: pygame.Surface):
    """Maquiagem teatral kabuki em alta definição: kumadori vermelho, olhos amendoados e lábios."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2

    # Fundo suave de porcelana oshiroi com transparência oval
    pygame.draw.ellipse(surf, (252, 250, 246, 230), (cx - 18, cy - 20, 36, 40))

    # Sobrancelhas pretas delicadas arqueadas
    pygame.draw.arc(surf, (35, 30, 40, 255), (cx - 14, cy - 14, 12, 10), math.radians(20), math.radians(160), 2)
    pygame.draw.arc(surf, (35, 30, 40, 255), (cx + 2, cy - 14, 12, 10), math.radians(20), math.radians(160), 2)

    # Kumadori carmesim teatral ao redor dos olhos
    pygame.draw.polygon(surf, (215, 30, 52, 220), [(cx - 14, cy - 6), (cx - 4, cy - 4), (cx - 12, cy - 1)])
    pygame.draw.polygon(surf, (215, 30, 52, 220), [(cx + 14, cy - 6), (cx + 4, cy - 4), (cx + 12, cy - 1)])

    # Olhos amendoados de gueixa com delineador preto
    pygame.draw.ellipse(surf, (18, 16, 22, 255), (cx - 12, cy - 6, 8, 4))
    pygame.draw.ellipse(surf, (18, 16, 22, 255), (cx + 4, cy - 6, 8, 4))

    # Ponto de luz especular nos olhos
    pygame.draw.circle(surf, (255, 255, 255, 255), (cx - 9, cy - 5), 1)
    pygame.draw.circle(surf, (255, 255, 255, 255), (cx + 7, cy - 5), 1)

    # Rubor suave nas maçãs do rosto
    pygame.draw.ellipse(surf, (240, 120, 140, 110), (cx - 14, cy - 1, 6, 4))
    pygame.draw.ellipse(surf, (240, 120, 140, 110), (cx + 8, cy - 1, 6, 4))

    # Nariz sutil
    pygame.draw.line(surf, (220, 190, 180, 180), (cx, cy), (cx, cy + 4), 1)

    # Lábios delicados carmesim com reflexo de laca brilhante
    pygame.draw.ellipse(surf, (215, 25, 48, 255), (cx - 4, cy + 7, 8, 5))
    pygame.draw.circle(surf, (255, 140, 165, 255), (cx - 1, cy + 8), 1)


def _build_okuni_gold_kamon(surf: pygame.Surface):
    """Kamon floral de cerejeira (sakura) imperial em ouro polido."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    gold = (245, 205, 65, 240)
    gold_dark = (185, 145, 40, 240)

    # 5 pétalas de sakura douradas
    for i in range(5):
        angle = i * (math.pi * 2 / 5) - math.pi / 2
        px = cx + int(math.cos(angle) * 7)
        py = cy + int(math.sin(angle) * 7)
        pygame.draw.circle(surf, gold, (px, py), 4)
        pygame.draw.circle(surf, gold_dark, (px, py), 4, 1)

    # Centro dourado com ponto de brilho
    pygame.draw.circle(surf, (255, 240, 160, 255), (cx, cy), 3)


def _build_okuni_jade_brooch(surf: pygame.Surface):
    """Broche obidome de jade esmeralda com moldura de filigrana dourada."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2
    pygame.draw.rect(surf, (240, 195, 55, 255), (cx - 8, cy - 5, 16, 10), border_radius=3)
    pygame.draw.rect(surf, (60, 185, 150, 255), (cx - 6, cy - 3, 12, 6), border_radius=2)
    pygame.draw.circle(surf, (255, 255, 255, 230), (cx - 2, cy - 1), 1)


def _build_okuni_fan_emblem(surf: pygame.Surface):
    """Emblema de sol nascente e ondas marinhas seigaiha no leque Tessen."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2

    # Sol nascente dourado
    pygame.draw.circle(surf, (248, 210, 65, 245), (cx, cy - 2), 9)
    pygame.draw.circle(surf, (255, 235, 130, 255), (cx, cy - 2), 6)

    # Raios solares sutis
    for i in range(8):
        ang = i * (math.pi / 4)
        rx = cx + int(math.cos(ang) * 14)
        ry = (cy - 2) + int(math.sin(ang) * 14)
        pygame.draw.line(surf, (245, 205, 65, 180), (cx, cy - 2), (rx, ry), 1)

    # Ondas Seigaiha estilizadas em prata/branco na base
    pygame.draw.arc(surf, (230, 240, 255, 220), (cx - 12, cy + 2, 12, 8), 0, math.pi, 2)
    pygame.draw.arc(surf, (230, 240, 255, 220), (cx, cy + 2, 12, 8), 0, math.pi, 2)


# =============================================================================
# FUNÇÕES DE ACESSO AOS DECALQUES DE OKUNI
# =============================================================================

def get_decal_okuni_face() -> pygame.Surface:
    return get_or_create_decal("okuni_face_t3", 44, 48, _build_okuni_kabuki_face)


def get_decal_okuni_kamon() -> pygame.Surface:
    return get_or_create_decal("okuni_kamon_t3", 24, 24, _build_okuni_gold_kamon)


def get_decal_okuni_brooch() -> pygame.Surface:
    return get_or_create_decal("okuni_brooch_t3", 22, 14, _build_okuni_jade_brooch)


def get_decal_okuni_fan() -> pygame.Surface:
    return get_or_create_decal("okuni_fan_t3", 32, 32, _build_okuni_fan_emblem)


# =============================================================================
# BIBLIOTECA DE DECALQUES 2.5D — KASUMI
# =============================================================================

def _build_kasumi_mask_eyes(surf: pygame.Surface):
    """Olhos azuis-gelo afiados e protetor de testa cromado reluzente."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2

    # Placa protetora de testa (hitai-ate) cromada com rebites
    pygame.draw.rect(surf, (220, 230, 245, 255), (cx - 15, cy - 14, 30, 7), border_radius=2)
    pygame.draw.rect(surf, (140, 160, 185, 255), (cx - 15, cy - 14, 30, 7), 1, border_radius=2)
    pygame.draw.line(surf, (255, 255, 255, 255), (cx - 13, cy - 12), (cx + 5, cy - 12), 1)
    pygame.draw.circle(surf, (70, 80, 95, 255), (cx - 12, cy - 11), 1)
    pygame.draw.circle(surf, (70, 80, 95, 255), (cx + 12, cy - 11), 1)

    # Tira de pele suave entre bandana e máscara
    pygame.draw.rect(surf, (248, 225, 210, 240), (cx - 13, cy - 7, 26, 7))

    # Sobrancelhas afiadas determinadas
    pygame.draw.line(surf, (30, 26, 35, 255), (cx - 12, cy - 6), (cx - 4, cy - 4), 2)
    pygame.draw.line(surf, (30, 26, 35, 255), (cx + 4, cy - 4), (cx + 12, cy - 6), 2)

    # Olhos azuis-gelo afiados penetrantes
    pygame.draw.ellipse(surf, (15, 45, 80, 255), (cx - 11, cy - 4, 7, 3))
    pygame.draw.ellipse(surf, (15, 45, 80, 255), (cx + 4, cy - 4, 7, 3))
    pygame.draw.circle(surf, (75, 180, 245, 255), (cx - 8, cy - 3), 1)
    pygame.draw.circle(surf, (75, 180, 245, 255), (cx + 7, cy - 3), 1)
    pygame.draw.circle(surf, (255, 255, 255, 255), (cx - 9, cy - 3), 1)
    pygame.draw.circle(surf, (255, 255, 255, 255), (cx + 6, cy - 3), 1)

    # Máscara ninja cobrindo do nariz para baixo com costura central
    pygame.draw.polygon(surf, (32, 35, 42, 245), [
        (cx - 13, cy), (cx + 13, cy), (cx + 8, cy + 14), (cx - 8, cy + 14)
    ])
    pygame.draw.line(surf, (55, 60, 72, 230), (cx, cy), (cx, cy + 14), 1)


def _build_kasumi_tactical_buckles(surf: pygame.Surface):
    """4 fivelas cromadas horizontais de alta definição com reflexos metálicos."""
    w, h = surf.get_size()
    cx = w // 2

    # 4 fivelas em alturas espaçadas
    y_positions = [6, 14, 22, 30]
    for y in y_positions:
        # Correia de couro escura
        pygame.draw.rect(surf, (28, 30, 36, 230), (cx - 14, y, 28, 5), border_radius=1)
        # Fivela cromada retangular
        pygame.draw.rect(surf, (215, 228, 242, 255), (cx - 6, y - 1, 12, 7), border_radius=2)
        pygame.draw.rect(surf, (120, 140, 165, 255), (cx - 6, y - 1, 12, 7), 1, border_radius=2)
        # Pino central da fivela e reflexo especular branco
        pygame.draw.line(surf, (255, 255, 255, 255), (cx - 4, y), (cx + 1, y), 1)
        pygame.draw.rect(surf, (50, 55, 65, 255), (cx - 1, y + 1, 2, 3))


def get_decal_kasumi_mask() -> pygame.Surface:
    return get_or_create_decal("kasumi_mask_t3", 36, 36, _build_kasumi_mask_eyes)


def get_decal_kasumi_buckles() -> pygame.Surface:
    return get_or_create_decal("kasumi_buckles_t3", 34, 40, _build_kasumi_tactical_buckles)


# =============================================================================
# BIBLIOTECA DE DECALQUES 2.5D — SAITOU
# =============================================================================

def _build_saitou_makoto_crest(surf: pygame.Surface):
    """Brasão histórico do Shinsengumi: Ideograma 'Makoto' (誠 - Fidelidade/Sinceridade)."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2

    # Moldura circular sutil branca
    pygame.draw.circle(surf, (252, 252, 255, 240), (cx, cy), 16, 2)

    # Ideograma 誠 (Makoto) desenhado em pinceladas brancas nítidas
    white = (255, 255, 255, 255)
    # Radical da palavra (言 - esquerda)
    # Ponto superior
    pygame.draw.line(surf, white, (cx - 9, cy - 8), (cx - 5, cy - 8), 2)
    # Traços horizontais
    pygame.draw.line(surf, white, (cx - 11, cy - 5), (cx - 3, cy - 5), 1)
    pygame.draw.line(surf, white, (cx - 10, cy - 2), (cx - 4, cy - 2), 1)
    pygame.draw.line(surf, white, (cx - 10, cy + 1), (cx - 4, cy + 1), 1)
    # Boca inferior (口)
    pygame.draw.rect(surf, white, (cx - 10, cy + 3, 6, 5), 1)

    # Radical da conclusão (成 - direita)
    pygame.draw.line(surf, white, (cx - 1, cy - 7), (cx + 8, cy - 7), 2)  # traço horizontal
    pygame.draw.line(surf, white, (cx + 1, cy - 7), (cx + 1, cy + 9), 2)  # traço vertical curvado
    pygame.draw.line(surf, white, (cx + 1, cy - 2), (cx + 9, cy - 2), 1)  # travessão
    pygame.draw.line(surf, white, (cx + 6, cy - 9), (cx + 6, cy + 8), 2)  # haste da alabarda
    pygame.draw.circle(surf, white, (cx + 10, cy - 6), 1)                 # pingo superior


def _build_saitou_grim_face(surf: pygame.Surface):
    """Rosto severo do Lobo de Mibu com olhar penetrante, cicatriz sutil e bandô."""
    w, h = surf.get_size()
    cx, cy = w // 2, h // 2

    # Bandô branco Shinsengumi na testa com nó
    pygame.draw.rect(surf, (248, 250, 252, 255), (cx - 14, cy - 14, 28, 6), border_radius=2)
    pygame.draw.circle(surf, (220, 225, 235, 255), (cx, cy - 11), 2)

    # Pele bronzeada masculina
    pygame.draw.rect(surf, (235, 195, 170, 245), (cx - 13, cy - 8, 26, 18), border_radius=3)

    # Sobrancelhas grossas pretas e severas inclinadas em V de determinação
    pygame.draw.line(surf, (20, 18, 22, 255), (cx - 12, cy - 7), (cx - 2, cy - 4), 2)
    pygame.draw.line(surf, (20, 18, 22, 255), (cx + 2, cy - 4), (cx + 12, cy - 7), 2)

    # Olhos estreitos intimidantes de predador
    pygame.draw.line(surf, (15, 12, 18, 255), (cx - 11, cy - 3), (cx - 3, cy - 3), 2)
    pygame.draw.line(surf, (15, 12, 18, 255), (cx + 3, cy - 3), (cx + 11, cy - 3), 2)
    pygame.draw.circle(surf, (255, 255, 255, 240), (cx - 6, cy - 3), 1)
    pygame.draw.circle(surf, (255, 255, 255, 240), (cx + 6, cy - 3), 1)

    # Nariz reto e queixo quadrado firme
    pygame.draw.line(surf, (185, 145, 120, 255), (cx, cy - 2), (cx, cy + 3), 2)
    pygame.draw.line(surf, (140, 70, 60, 255), (cx - 5, cy + 6), (cx + 5, cy + 6), 2)


def get_decal_saitou_makoto() -> pygame.Surface:
    return get_or_create_decal("saitou_makoto_t3", 38, 38, _build_saitou_makoto_crest)


def get_decal_saitou_face() -> pygame.Surface:
    return get_or_create_decal("saitou_face_t3", 34, 38, _build_saitou_grim_face)

