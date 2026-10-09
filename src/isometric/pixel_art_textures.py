"""
src/isometric/pixel_art_textures.py - Banco de Texturas em Pixel Art para Voxel UV (Técnica 2)

Define matrizes de texels estilizadas pixel-a-pixel para aplicação nas faces dos
modelos de personagens (Okuni, Kasumi, Saitou).
Cada textura é uma matriz 2D de tuplas RGB: list[list[tuple[int, int, int]]].
"""

# =============================================================================
# PALETAS DE CORES AUXILIARES
# =============================================================================

# Okuni
_WHT  = (252, 250, 246)  # Oshiroi (pó branco kabuki)
_SKN  = (255, 238, 230)  # Pele clara suave
_BLS  = (240, 150, 165)  # Rubor suave
_KUM  = (210, 30, 50)    # Kumadori (vermelho ao redor dos olhos)
_LIP  = (225, 25, 50)    # Lábio carmesim
_LIPG = (255, 140, 160)  # Brilho labial
_EYE  = (20, 18, 25)     # Olho/delineador
_SPC  = (255, 255, 255)  # Reflexo do olhar
_BRW  = (35, 30, 40)     # Sobrancelha
_HDK  = (16, 16, 20)     # Cabelo preto laqueado
_HLT  = (45, 45, 58)     # Brilho do cabelo
_GLD  = (245, 205, 65)   # Ouro brilhante (kanzashi / brocado)
_GLDD = (185, 145, 40)   # Ouro sombreado
_CRMS = (180, 24, 40)    # Carmesim real do quimono
_CRMD = (125, 15, 28)    # Carmesim sombra
_CRML = (220, 45, 65)    # Carmesim realce
_SAK  = (255, 195, 215)  # Pétala de flor de cerejeira (sakura)
_SAKW = (255, 235, 242)  # Sakura centro/branco
_JAD  = (65, 185, 150)   # Jade verde do obidome
_OBK  = (28, 26, 32)     # Obi preto
_STL  = (220, 230, 245)  # Aço das lâminas do leque tessen
_STLD = (150, 165, 185)  # Aço sombreado


# =============================================================================
# 1. OKUNI — TEXTURAS PIXEL ART
# =============================================================================

def build_okuni_face_front() -> list[list[tuple[int, int, int]]]:
    """
    Rosto Kabuki refinado 12x12:
    - Base de pó de arroz branco (oshiroi) com queixo esculpido
    - Sobrancelhas altas de cortesã
    - Olhos com delineado alongado, kumadori vermelho teatral e ponto de luz
    - Pequeno lábio em botão com reflexo de laca vermelha
    """
    H = _HDK
    W = _WHT
    B = _BRW
    K = _KUM
    E = _EYE
    S = _SPC
    L = _LIP
    G = _LIPG
    R = _BLS

    grid = [
        # 0: Topo da testa / franja
        [H, H, H, H, H, H, H, H, H, H, H, H],
        # 1: Raiz do cabelo
        [H, H, W, W, W, W, W, W, W, W, H, H],
        # 2: Testa com sobrancelhas kabuki altas
        [H, W, W, B, B, W, W, B, B, W, W, H],
        # 3: Espaço entre sobrancelha e olhos
        [H, W, W, W, W, W, W, W, W, W, W, H],
        # 4: Olhos com delineado e kumadori vermelho
        [H, W, K, E, S, W, W, S, E, K, W, H],
        # 5: Canto inferior dos olhos com kumadori e rubor
        [H, W, W, K, W, W, W, W, K, W, W, H],
        # 6: Maçãs do rosto com rubor suave
        [H, W, R, W, W, W, W, W, W, R, W, H],
        # 7: Nariz sutil
        [H, W, W, W, W, _SKN, W, W, W, W, W, H],
        # 8: Lábio superior em botão carmesim
        [H, W, W, W, W, L, L, W, W, W, W, H],
        # 9: Lábio inferior com brilho laqueado
        [H, W, W, W, W, G, L, W, W, W, W, H],
        # 10: Queixo delicado
        [H, H, W, W, W, W, W, W, W, W, H, H],
        # 11: Base do pescoço
        [H, H, H, W, W, W, W, W, W, H, H, H],
    ]
    return grid


def build_okuni_face_back() -> list[list[tuple[int, int, int]]]:
    """Costas da cabeça 12x12: Penteado Shimada com nuca 'komata' e fita kanoko."""
    H = _HDK
    L = _HLT
    W = _WHT  # Oshiroi na nuca
    K = _CRMS # Fita vermelha kanoko
    G = _GLD

    grid = [
        [H, H, H, H, L, L, L, H, H, H, H, H],
        [H, H, H, L, L, L, L, L, H, H, H, H],
        [H, H, L, L, H, H, H, L, L, H, H, H],
        [H, H, L, H, H, H, H, H, L, H, H, H],
        [H, H, H, H, K, K, K, H, H, H, H, H],
        [H, H, H, K, G, G, G, K, H, H, H, H],
        [H, H, H, H, K, K, K, H, H, H, H, H],
        [H, H, H, H, H, H, H, H, H, H, H, H],
        # Nuca tradicional komata (dois bicos de pó branco descendo)
        [H, H, H, W, H, H, H, W, H, H, H, H],
        [H, H, W, W, H, H, H, W, W, H, H, H],
        [H, H, W, W, W, H, W, W, W, H, H, H],
        [H, H, W, W, W, W, W, W, W, H, H, H],
    ]
    return grid


def build_okuni_hair_top() -> list[list[tuple[int, int, int]]]:
    """Topo da cabeça 12x12: Pente kushi dourado e kanzashi sobre o cabelo laqueado."""
    H = _HDK
    L = _HLT
    G = _GLD
    GD= _GLDD
    K = _CRMS

    grid = [
        [H, H, H, H, H, H, H, H, H, H, H, H],
        [H, H, L, L, L, L, L, L, L, L, H, H],
        # Pente frontal Kushi esculpido em ouro
        [H, GD, G, G, G, G, G, G, G, G, GD, H],
        [H, G, GD, G, GD, G, GD, G, GD, G, G, H],
        [H, H, L, L, L, L, L, L, L, L, H, H],
        [H, H, L, H, H, H, H, H, H, L, H, H],
        # Agulhas Kanzashi douradas cruzadas
        [G, H, H, H, K, K, K, K, H, H, H, G],
        [H, G, H, H, K, G, G, K, H, H, G, H],
        [H, H, G, H, H, K, K, H, H, G, H, H],
        [H, H, H, G, H, H, H, H, G, H, H, H],
        [H, H, H, H, L, L, L, L, H, H, H, H],
        [H, H, H, H, H, H, H, H, H, H, H, H],
    ]
    return grid


def build_okuni_hair_side() -> list[list[tuple[int, int, int]]]:
    """Lateral da cabeça 12x12: Curvas do penteado shimada e pingentes kanzashi."""
    H = _HDK
    L = _HLT
    G = _GLD
    W = _WHT
    R = _BLS

    grid = [
        [H, H, H, H, H, H, H, H, H, H, H, H],
        [H, H, L, L, L, L, L, H, H, H, H, H],
        [H, L, L, H, H, H, L, L, H, G, G, G], # Ponta do pente
        [H, L, H, H, H, H, H, L, H, H, G, H],
        [H, L, H, H, H, H, H, L, H, H, G, H],
        [H, H, H, W, W, W, H, H, H, H, G, H], # Rosto / têmpora
        [H, H, W, W, R, W, W, H, H, H, G, H],
        [H, H, W, W, W, W, W, H, H, G, G, H], # Pingente bira-bira
        [H, H, H, W, W, W, W, H, H, H, G, H],
        [H, H, H, W, W, W, W, H, H, H, H, H],
        [H, H, H, H, W, W, W, H, H, H, H, H],
        [H, H, H, H, H, W, W, H, H, H, H, H],
    ]
    return grid


def build_okuni_torso_front() -> list[list[tuple[int, int, int]]]:
    """
    Torso Frontal 12x16:
    - Decote cruzado com gola branca interna e gola dourada intermediária
    - Quimono carmesim com flores sakura bordadas (pétalas cor-de-rosa e centros dourados)
    - Faixa Obi com broche de jade esmeralda
    """
    C = _CRMS
    CD= _CRMD
    CL= _CRML
    W = _WHT
    G = _GLD
    GD= _GLDD
    P = _SAK   # Pétala sakura
    PW= _SAKW  # Centro sakura
    J = _JAD   # Jade
    B = _OBK

    grid = [
        # 0-3: Golas duplas no decote
        [C, C, W, W, W, W, W, W, W, W, C, C],
        [C, C, C, W, G, G, G, G, W, C, C, C],
        [C, C, C, C, W, G, G, W, C, C, C, C],
        [C, C, C, C, C, W, W, C, C, C, C, C],
        # 4-9: Peito com flores sakura bordadas
        [C, CL, C, P, PW, P, C, C, C, C, CL, C],
        [C, C, P, PW, G, PW, P, C, P, PW, P, C],
        [CD, C, C, P, PW, P, C, P, PW, G, PW, P],
        [C, C, C, C, P, C, C, C, P, PW, P, C],
        [C, P, PW, P, C, C, C, C, C, P, C, C],
        [CD, P, G, P, C, C, CL, C, C, C, CD, C],
        # 10-15: Faixa Obi frontal com broche de jade e xadrez ouro/preto
        [B, B, G, G, B, B, G, G, B, B, G, G],
        [G, G, B, B, G, G, B, B, G, G, B, B],
        [C, C, C, G, J, J, J, J, G, C, C, C], # Broche de Jade
        [C, C, C, G, J, W, J, J, G, C, C, C],
        [B, B, G, G, B, B, G, G, B, B, G, G],
        [G, G, B, B, G, G, B, B, G, G, B, B],
    ]
    return grid


def build_okuni_torso_back() -> list[list[tuple[int, int, int]]]:
    """Costas do Torso 12x16: Quimono carmesim com padrão floral e laço Musubi volumoso."""
    C = _CRMS
    CD= _CRMD
    CL= _CRML
    G = _GLD
    GD= _GLDD
    P = _SAK
    PW= _SAKW
    B = _OBK

    grid = [
        [C, C, C, C, C, C, C, C, C, C, C, C],
        [C, CL, C, C, P, PW, P, C, C, CL, C, C],
        [CD, C, C, P, PW, G, PW, P, C, C, C, CD],
        [C, C, C, C, P, PW, P, C, C, C, C, C],
        [C, C, P, PW, P, C, C, C, P, PW, P, C],
        [C, C, P, G, P, C, C, P, PW, G, PW, P],
        [CD, C, C, P, C, C, C, C, P, PW, P, C],
        [C, C, C, C, C, C, CL, C, C, P, C, C],
        # Laço Musubi de Borboleta nas costas
        [G, G, B, B, C, C, C, C, B, B, G, G],
        [G, GD, G, B, B, C, C, B, B, G, GD, G],
        [B, G, GD, G, B, G, G, B, G, GD, G, B],
        [B, B, G, G, B, G, G, B, G, G, B, B],
        [B, B, B, G, G, GD, GD, G, G, B, B, B],
        [C, B, B, G, G, G, G, G, G, B, B, C],
        [C, C, B, B, G, G, G, G, B, B, C, C],
        [C, C, C, B, B, B, B, B, B, C, C, C],
    ]
    return grid


def build_okuni_skirt_front() -> list[list[tuple[int, int, int]]]:
    """
    Saia Frontal 12x16:
    - Cascata de pétalas de cerejeira (sakura) ao vento
    - Barra acolchoada (fuki) com meandros de ouro
    """
    C = _CRMS
    CD= _CRMD
    CL= _CRML
    G = _GLD
    GD= _GLDD
    P = _SAK
    PW= _SAKW

    grid = [
        [C, C, CL, C, C, C, C, C, C, CL, C, C],
        [C, P, PW, P, C, C, C, P, PW, P, C, C],
        [CD, P, G, P, C, C, P, PW, G, PW, P, CD],
        [C, C, P, C, C, C, C, P, PW, P, C, C],
        [C, C, C, C, CL, C, C, C, P, C, C, C],
        [C, C, C, P, PW, P, C, C, C, C, CL, C],
        [CD, C, P, PW, G, PW, P, C, C, C, C, CD],
        [C, C, C, P, PW, P, C, C, P, PW, P, C],
        [C, CL, C, C, P, C, C, P, PW, G, PW, P],
        [C, P, PW, P, C, C, C, C, P, PW, P, C],
        [CD, P, G, P, C, C, CL, C, C, P, C, CD],
        [C, C, P, C, C, C, C, C, C, C, C, C],
        # Barra Fuki acolchoada com meandros de ouro
        [GD, GD, GD, GD, GD, GD, GD, GD, GD, GD, GD, GD],
        [G, G, GD, G, G, GD, G, G, GD, G, G, GD],
        [GD, G, G, GD, G, G, GD, G, G, GD, G, G],
        [CD, CD, CD, CD, CD, CD, CD, CD, CD, CD, CD, CD],
    ]
    return grid


def build_okuni_sleeve() -> list[list[tuple[int, int, int]]]:
    """Manga Furisode 12x16: Tecido carmesim com flor sakura e barra com bordado dourado."""
    C = _CRMS
    CD= _CRMD
    CL= _CRML
    G = _GLD
    GD= _GLDD
    P = _SAK
    PW= _SAKW

    grid = [
        [C, C, CL, C, C, C, C, C, C, CL, C, C],
        [C, C, C, C, C, P, PW, P, C, C, C, C],
        [CD, C, C, C, P, PW, G, PW, P, C, C, CD],
        [C, C, CL, C, C, P, PW, P, C, C, C, C],
        [C, C, P, PW, P, C, P, C, C, CL, C, C],
        [C, P, PW, G, PW, P, C, C, C, C, C, C],
        [CD, C, P, PW, P, C, C, C, P, PW, P, CD],
        [C, C, C, P, C, C, C, P, PW, G, PW, P],
        [C, CL, C, C, C, C, C, C, P, PW, P, C],
        [C, C, C, C, CL, C, C, C, C, P, C, C],
        [CD, C, C, C, C, C, C, CL, C, C, C, CD],
        [C, C, CL, C, C, C, C, C, C, C, C, C],
        # Barrado bordado em fio de ouro
        [GD, G, GD, G, GD, G, GD, G, GD, G, GD, G],
        [G, GD, G, GD, G, GD, G, GD, G, GD, G, GD],
        [GD, G, GD, G, GD, G, GD, G, GD, G, GD, G],
        [CD, CD, CD, CD, CD, CD, CD, CD, CD, CD, CD, CD],
    ]
    return grid


def build_okuni_fan_tessen() -> list[list[tuple[int, int, int]]]:
    """
    Leque de Aço Tessen 12x12:
    - Borda externa de lâminas afiadas de aço
    - Centro de papel carmesim com sol nascente dourado e ondas estilizadas
    """
    S = _STL
    SD= _STLD
    C = _CRMS
    CD= _CRMD
    G = _GLD
    GD= _GLDD
    W = _WHT

    grid = [
        # Pontas afiadas de aço
        [SD, S, S, S, S, S, S, S, S, S, S, SD],
        [S, SD, S, S, S, S, S, S, S, S, SD, S],
        # Papel carmesim com sol dourado
        [S, C, C, C, G, G, G, G, C, C, C, S],
        [S, C, C, G, G, GD, GD, G, G, C, C, S],
        [S, C, G, G, GD, G, G, GD, G, G, C, S],
        [S, C, G, GD, G, G, G, G, GD, G, C, S],
        [S, C, G, GD, G, G, G, G, GD, G, C, S],
        [S, C, C, G, G, GD, GD, G, G, C, C, S],
        # Ondas de laca branca/dourada
        [S, C, W, C, G, G, G, G, C, W, C, S],
        [S, W, C, W, C, C, C, C, W, C, W, S],
        [SD, C, C, C, C, GD, GD, C, C, C, C, SD],
        # Rebite / cabo
        [SD, SD, SD, SD, G, GD, GD, G, SD, SD, SD, SD],
    ]
    return grid


# =============================================================================
# 2. KASUMI — TEXTURAS PIXEL ART
# =============================================================================

# Paleta Kasumi
_K_METL = (215, 228, 242)  # Cromo metálico brilhante
_K_METD = (130, 150, 175)  # Cromo sombreado
_K_SPEC = (255, 255, 255)  # Especular puro
_K_LEA  = (38, 42, 50)     # Couro tático cinza-escuro
_K_LEAD = (24, 26, 32)     # Couro sombra
_K_LEAL = (65, 72, 85)     # Costuras do colete / realces
_K_MSH  = (48, 52, 62)     # Malha ninja (kusari)
_K_MSHL = (80, 88, 102)    # Nós da malha
_K_EYEB = (70, 175, 240)   # Olho azul-gelo
_K_EYEP = (15, 50, 95)     # Pupila azul-marinho
_K_MSK  = (32, 35, 42)     # Tecido da máscara ninja
_K_MSKL = (55, 60, 72)     # Costura central da máscara
_K_SKN  = (250, 228, 215)  # Pele visível entre bandana e máscara
_K_SCF  = (140, 180, 220)  # Cachecol azul-celeste
_K_SCFD = (95, 135, 175)   # Sombra do cachecol


def build_kasumi_face_front() -> list[list[tuple[int, int, int]]]:
    """
    Rosto Shinobi 12x12:
    - Bandô com placa protetora cromada no topo
    - Olhos azuis-gelo afiados e penetrantes com reflexo branco
    - Máscara ninja cobrindo o nariz e a boca com costura respirável central
    """
    M = _K_METL
    MD= _K_METD
    S = _K_SPEC
    B = _K_EYEB
    P = _K_EYEP
    K = _K_SKN
    MK= _K_MSK
    ML= _K_MSKL
    H = _HDK

    grid = [
        # 0: Topo do cabelo
        [H, H, H, H, H, H, H, H, H, H, H, H],
        # 1-2: Placa protetora de testa (hitai-ate) cromada
        [H, MD, M, M, M, S, M, M, M, M, MD, H],
        [H, MD, MD, M, M, M, M, M, M, MD, MD, H],
        # 3: Tira de pele e sobrancelhas determinadas
        [H, K, _BRW, _BRW, K, K, K, _BRW, _BRW, K, K, H],
        # 4: Olhos azuis-gelo afiados com ponto especular
        [H, K, P, B, S, K, K, S, B, P, K, H],
        # 5: Borda superior da máscara sobre a ponte do nariz
        [H, MK, MK, MK, MK, ML, ML, MK, MK, MK, MK, H],
        # 6-9: Máscara ninja cobrindo bochechas e queixo com nervura central
        [H, MK, MK, MK, MK, ML, ML, MK, MK, MK, MK, H],
        [H, MK, MK, MK, MK, ML, ML, MK, MK, MK, MK, H],
        [H, MK, MK, ML, MK, ML, ML, MK, ML, MK, MK, H],
        [H, H, MK, MK, MK, ML, ML, MK, MK, MK, H, H],
        # 10-11: Base do queixo e pescoço com gola tática
        [H, H, H, MK, MK, ML, ML, MK, MK, H, H, H],
        [H, H, H, H, MK, MK, MK, MK, H, H, H, H],
    ]
    return grid


def build_kasumi_face_back() -> list[list[tuple[int, int, int]]]:
    """Costas da cabeça 12x12: Cabelo negro preso com nó da bandana e cauda shinobi."""
    H = _HDK
    L = _HLT
    M = _K_LEA
    ML= _K_LEAL

    grid = [
        [H, H, H, H, L, L, L, H, H, H, H, H],
        [H, H, L, L, L, L, L, L, H, H, H, H],
        [H, L, L, H, H, H, H, L, L, H, H, H],
        # Nó da bandana ninja
        [H, M, ML, M, ML, M, ML, M, ML, M, H, H],
        [H, H, M, ML, M, ML, M, ML, M, H, H, H],
        # Cauda do rabo de cavalo esvoaçante
        [H, H, H, H, L, L, L, H, H, H, H, H],
        [H, H, H, L, L, H, L, L, H, H, H, H],
        [H, H, H, L, H, H, H, L, H, H, H, H],
        [H, H, H, L, H, H, H, L, H, H, H, H],
        [H, H, H, H, L, H, L, H, H, H, H, H],
        [H, H, H, H, H, L, H, H, H, H, H, H],
        [H, H, H, H, H, H, H, H, H, H, H, H],
    ]
    return grid


def build_kasumi_torso_front() -> list[list[tuple[int, int, int]]]:
    """
    Torso Frontal 12x16:
    - Malha shinobi respirável no colarinho
    - Colete-espartilho tático com 4 fivelas cromadas horizontais reluzentes
    - Costuras reforçadas e placas peitorais
    """
    L = _K_LEA
    LD= _K_LEAD
    LL= _K_LEAL
    M = _K_METL
    MD= _K_METD
    S = _K_SPEC
    MS= _K_MSH
    ML= _K_MSHL

    grid = [
        # 0-2: Colarinho com malha shinobi
        [L, L, MS, ML, MS, ML, MS, ML, MS, ML, L, L],
        [L, L, ML, MS, ML, MS, ML, MS, ML, MS, L, L],
        [L, LL, L, MS, ML, MS, ML, MS, L, LL, L, L],
        # 3-5: Fivela 1 (superior peitoral)
        [LD, L, LL, MD, M, S, S, M, MD, LL, L, LD],
        [LD, L, L, L, LL, L, L, LL, L, L, L, LD],
        # 6-8: Fivela 2 (médio-peitoral)
        [LD, L, LL, MD, M, S, S, M, MD, LL, L, LD],
        [LD, L, L, L, LL, L, L, LL, L, L, L, LD],
        # 9-11: Fivela 3 (abdômen)
        [LD, L, LL, MD, M, S, S, M, MD, LL, L, LD],
        [LD, L, L, L, LL, L, L, LL, L, L, L, LD],
        # 12-14: Fivela 4 (cinto / espartilho inferior)
        [LD, L, LL, MD, M, S, S, M, MD, LL, L, LD],
        [LD, LD, L, L, L, L, L, L, L, L, LD, LD],
        # 15: Cintura tática
        [LD, LD, LD, L, L, L, L, L, L, LD, LD, LD],
    ]
    return grid


def build_kasumi_torso_back() -> list[list[tuple[int, int, int]]]:
    """Costas do Torso 12x16: Arnês tático em X e bainha dorsal de shuriken/kunai."""
    L = _K_LEA
    LD= _K_LEAD
    LL= _K_LEAL
    M = _K_METL
    MD= _K_METD

    grid = [
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        [LD, L, LL, L, L, L, L, L, L, LL, L, LD],
        # Correias táticas cruzando em X
        [LD, L, L, LL, L, L, L, L, LL, L, L, LD],
        [LD, L, L, L, LL, M, M, LL, L, L, L, LD],
        [LD, L, L, L, MD, M, M, MD, L, L, L, LD],
        [LD, L, L, LL, L, L, L, L, LL, L, L, LD],
        [LD, L, LL, L, L, L, L, L, L, LL, L, LD],
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        # Bolsa de equipamentos e cinto traseiro
        [LD, LD, L, L, L, L, L, L, L, L, LD, LD],
        [LD, MD, M, M, LD, L, L, LD, M, M, MD, LD],
        [LD, MD, M, M, LD, L, L, LD, M, M, MD, LD],
        [LD, LD, LD, LD, L, L, L, L, LD, LD, LD, LD],
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        [LD, LD, L, L, L, L, L, L, L, L, LD, LD],
        [LD, LD, LD, LD, LD, LD, LD, LD, LD, LD, LD, LD],
    ]
    return grid


def build_kasumi_arm_guard() -> list[list[tuple[int, int, int]]]:
    """Bracelete Tático 12x16: Placa de cromo com iluminação metálica e correias."""
    M = _K_METL
    MD= _K_METD
    S = _K_SPEC
    L = _K_LEA
    LD= _K_LEAD

    grid = [
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        [L, MD, M, M, S, S, M, M, MD, L, L, L],
        [L, MD, M, M, S, S, M, M, MD, L, L, L],
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        [LD, MD, M, M, S, S, M, M, MD, L, L, LD],
        [LD, MD, M, M, S, S, M, M, MD, L, L, LD],
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        [LD, MD, M, M, S, S, M, M, MD, L, L, LD],
        [LD, MD, M, M, S, S, M, M, MD, L, L, LD],
        [LD, L, L, L, L, L, L, L, L, L, L, LD],
        [L, L, L, L, L, L, L, L, L, L, L, L],
        [L, L, L, L, L, L, L, L, L, L, L, L],
        [LD, LD, LD, LD, LD, LD, LD, LD, LD, LD, LD, LD],
        [L, L, L, L, L, L, L, L, L, L, L, L],
        [L, L, L, L, L, L, L, L, L, L, L, L],
        [LD, LD, LD, LD, LD, LD, LD, LD, LD, LD, LD, LD],
    ]
    return grid


def build_kasumi_dagger() -> list[list[tuple[int, int, int]]]:
    """Adaga Shinobi 12x12: Lâmina afiada com sulco fuller e anel de arremesso."""
    M = _K_METL
    MD= _K_METD
    S = _K_SPEC
    L = _K_LEA
    LD= _K_LEAD

    grid = [
        # Ponta afiada
        [None, None, None, None, None, S, S, None, None, None, None, None],
        [None, None, None, None, M, S, MD, None, None, None, None, None],
        [None, None, None, None, M, S, MD, None, None, None, None, None],
        # Lâmina com sulco central escuro
        [None, None, None, M, M, LD, MD, MD, None, None, None, None],
        [None, None, None, M, M, LD, MD, MD, None, None, None, None],
        [None, None, None, M, M, LD, MD, MD, None, None, None, None],
        # Guarda / tsuba em cromo
        [None, None, MD, M, M, M, M, M, MD, None, None, None],
        # Cabo trançado
        [None, None, None, None, L, LD, L, None, None, None, None, None],
        [None, None, None, None, LD, L, LD, None, None, None, None, None],
        [None, None, None, None, L, LD, L, None, None, None, None, None],
        # Anel de arremesso no pomo
        [None, None, None, None, M, MD, M, None, None, None, None, None],
        [None, None, None, None, None, M, None, None, None, None, None, None],
    ]
    # Substitui None por cor vazia ou transparente
    filled_grid = []
    for row in grid:
        filled_grid.append([(0, 0, 0) if px is None else px for px in row])
    return filled_grid


# =============================================================================
# REGISTRO GLOBAL DE TODAS AS TEXTURAS PIXEL ART
# =============================================================================
def init_pixel_art_textures():
    """Registra todas as texturas UV pixel art no subsistema de renderização."""
    from src.isometric.uv_voxel_renderer import register_pixel_texture

    # Okuni
    register_pixel_texture("okuni_face_front", build_okuni_face_front())
    register_pixel_texture("okuni_face_back", build_okuni_face_back())
    register_pixel_texture("okuni_hair_top", build_okuni_hair_top())
    register_pixel_texture("okuni_hair_side", build_okuni_hair_side())
    register_pixel_texture("okuni_torso_front", build_okuni_torso_front())
    register_pixel_texture("okuni_torso_back", build_okuni_torso_back())
    register_pixel_texture("okuni_skirt_front", build_okuni_skirt_front())
    register_pixel_texture("okuni_skirt_back", build_okuni_skirt_front())
    register_pixel_texture("okuni_sleeve", build_okuni_sleeve())
    register_pixel_texture("okuni_fan", build_okuni_fan_tessen())

    # Kasumi
    register_pixel_texture("kasumi_face_front", build_kasumi_face_front())
    register_pixel_texture("kasumi_face_back", build_kasumi_face_back())
    register_pixel_texture("kasumi_torso_front", build_kasumi_torso_front())
    register_pixel_texture("kasumi_torso_back", build_kasumi_torso_back())
    register_pixel_texture("kasumi_arm_guard", build_kasumi_arm_guard())
    register_pixel_texture("kasumi_dagger", build_kasumi_dagger())

