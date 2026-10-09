"""
Texturas procedurais nas faces dos voxels grandes (6.5.3).

Cada padrão é desenhado como linhas e pontos calculados nos cantos do polígono da face (a, b, c, d: origem, +u, +u+v, +v),
então acompanha azimute e zoom sem imagens. O espaçamento é em unidades de mundo, para o desenho ficar do tamanho da
madeira, da pedra ou da telha de verdade, e some em faces pequenas demais (`MIN_FACE_PX`) para não virar ruído.
Quem chama: `draw_voxel_box(..., texture="planks")`. Não se aplica a voxels translúcidos.
"""
import math

import pygame

from src.effects import quality

MIN_FACE_PX = 3     # arestas menores que isso (em pixels) ficam lisas (3px permite micro-voxels detalhados)
MIN_GAP_PX = 2.0    # espaçamento mínimo entre linhas; abaixo disso o padrão é afinado


def _tone(color, k: float):
    return (max(0, min(255, int(color[0] * k))), max(0, min(255, int(color[1] * k))), max(0, min(255, int(color[2] * k))))


def _light(shade, k=1.5, add=10):
    return (min(255, int(shade[0] * k) + add), min(255, int(shade[1] * k) + add), min(255, int(shade[2] * k) + add))


MAX_LINES = 40      # teto de chamadas de linha por face: telhados e paredes enormes custam caro no quadro


def _grid(f, spacing_u: float, spacing_v: float):
    """Divisões (nu, nv) de uma face em grade, afinadas para caber no teto de linhas."""
    nu, nv = _count(f.ulen, spacing_u, f.lu), _count(f.vlen, spacing_v, f.lv)
    while nu * nv > MAX_LINES:
        if nu >= nv and nu > 1:
            nu = max(1, int(nu * 0.7))
        elif nv > 1:
            nv = max(1, int(nv * 0.7))
        else:
            break
    return nu, nv


def _count(extent_world: float, spacing: float, extent_px: float) -> int:
    """Quantas divisões cabem, afinando quando os pixels ficariam juntos demais."""
    n = max(1, int(round(extent_world / spacing)))
    while n > 1 and extent_px / n < MIN_GAP_PX:
        n -= 1
    return n


class _Face:
    __slots__ = ("surface", "a", "ux", "uy", "vx", "vy", "kind", "ulen", "vlen", "lu", "lv", "shade", "state")

    def __init__(self, surface, poly, kind, ulen, vlen, shade, seed):
        a, b, _, d = poly
        self.surface, self.a, self.kind = surface, a, kind
        self.ux, self.uy = b[0] - a[0], b[1] - a[1]
        self.vx, self.vy = d[0] - a[0], d[1] - a[1]
        self.ulen, self.vlen, self.shade = ulen, vlen, shade
        self.lu, self.lv = math.hypot(self.ux, self.uy), math.hypot(self.vx, self.vy)
        self.state = (seed * 2654435761 + 1) & 0xFFFFFFFF or 1

    def random(self) -> float:
        """xorshift32: determinístico por face e bem mais barato que criar um random.Random."""
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x
        return (x & 0xFFFFFF) / 16777216.0

    def uniform(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.random()

    def pt(self, u: float, v: float):
        u, v = 0.02 + 0.96 * u, 0.02 + 0.96 * v  # fica um tico para dentro do contorno
        return self.a[0] + self.ux * u + self.vx * v, self.a[1] + self.uy * u + self.vy * v

    def line(self, color, u0, v0, u1, v1, width=1):
        pygame.draw.line(self.surface, color, self.pt(u0, v0), self.pt(u1, v1), max(1, int(width)))

    def dot(self, color, u, v, size=1):
        x, y = self.pt(u, v)
        self.surface.fill(color, (int(x), int(y), size, size))

    def quad(self, color, u0: float, v0: float, u1: float, v1: float):
        """Preenche uma faixa ou retângulo em UV [u0, u1] x [v0, v1] mapeado para os pixels da face."""
        p0 = self.pt(u0, v0)
        p1 = self.pt(u1, v0)
        p2 = self.pt(u1, v1)
        p3 = self.pt(u0, v1)
        pygame.draw.polygon(self.surface, color, (p0, p1, p2, p3))

    def poly(self, color, pts_uv):
        """Preenche polígono arbitrário em UV na face."""
        pts = [self.pt(u, v) for u, v in pts_uv]
        if len(pts) >= 3:
            pygame.draw.polygon(self.surface, color, pts)

    def const_line(self, color, axis: str, value: float, start=0.0, end=1.0, width=1):
        """Linha com u (axis 'u') ou v (axis 'v') constante, de start a end no outro eixo."""
        if axis == "u":
            self.line(color, value, start, value, end, width=width)
        else:
            self.line(color, start, value, end, value, width=width)


def _planks(f: _Face):
    dark = _tone(f.shade, 0.72)
    if f.kind == "top":
        axis, along, across, across_px = ("v", f.ulen, f.vlen, f.lv) if f.ulen >= f.vlen else ("u", f.vlen, f.ulen, f.lu)
    else:  # parede: tábuas na vertical
        axis, along, across, across_px = "u", f.vlen, f.ulen, f.lu
    n = min(_count(across, 0.28, across_px), 14)
    for i in range(1, n):
        f.const_line(dark, axis, i / n)
    for i in range(n):  # emendas de topo, deslocadas de tábua para tábua
        t = (f.random() * 0.6 + 0.2)
        lo, hi = i / n, (i + 1) / n
        if axis == "u":
            f.line(dark, lo, t, hi, t)
        else:
            f.line(dark, t, lo, t, hi)


def _stone(f: _Face):
    dark = _tone(f.shade, 0.70)
    nu, nv = _grid(f, 0.62, 0.34)
    for j in range(nv):
        if j:
            f.line(dark, 0.0, j / nv, 1.0, j / nv)
        off = 0.5 if j % 2 else 0.0
        for i in range(nu + 1):
            u = (i + off) / nu
            if 0.02 < u < 0.98:
                f.line(dark, u, j / nv, u, (j + 1) / nv)


def _roof_tile(f: _Face):
    dark, light = _tone(f.shade, 0.68), _tone(f.shade, 1.14)
    nu, nv = _grid(f, 0.3, 0.2)
    for j in range(nv):
        if j:
            f.line(dark, 0.0, j / nv, 1.0, j / nv)
        off = 0.5 if j % 2 else 0.0
        for i in range(nu + 1):
            u = (i + off) / nu
            if 0.02 < u < 0.98:
                f.line(dark, u, j / nv, u, (j + 0.65) / nv)
        f.line(light, 0.0, (j + 0.12) / nv, 1.0, (j + 0.12) / nv)


def _thatch(f: _Face):
    dark, light = _tone(f.shade, 0.68), _tone(f.shade, 1.2)
    n = max(6, min(18, int(f.lu * f.lv / 140)))
    for k in range(n):
        u, v = f.random() * 0.92, f.random() * 0.82
        f.line(dark if k % 2 else light, u, v, u + 0.07, v + 0.16)


def _bark(f: _Face):
    dark = _tone(f.shade, 0.62)
    n = max(2, min(9, int(f.lu / 5)))
    for _ in range(n):
        u = f.random()
        v0 = f.random() * 0.5
        f.line(dark, u, v0, u + f.uniform(-0.03, 0.03), min(1.0, v0 + f.uniform(0.25, 0.6)))


def _cloth(f: _Face):
    tone = _tone(f.shade, 0.86)
    nu, nv = min(_count(f.ulen, 0.18, f.lu), 12), min(_count(f.vlen, 0.18, f.lv), 12)
    for i in range(1, nu):
        f.line(tone, i / nu, 0.0, i / nu, 1.0)
    for j in range(1, nv):
        f.line(tone, 0.0, j / nv, 1.0, j / nv)


def _plaster(f: _Face):
    dark, light = _tone(f.shade, 0.82), _tone(f.shade, 1.12)
    n = max(4, min(12, int(f.lu * f.lv / 100)))
    for k in range(n):
        f.dot(dark if k % 2 else light, f.random(), f.random())


def _foliage(f: _Face):
    dark = _tone(f.shade, 0.7)
    light = (min(255, int(f.shade[0] * 1.25)), min(255, int(f.shade[1] * 1.28)), min(255, int(f.shade[2] * 1.1)))
    n = max(6, min(14, int(f.lu * f.lv / 90)))
    for k in range(n):
        f.dot(dark if k % 3 == 0 else light, f.random() * 0.95, f.random() * 0.95, 2)


def _marble(f: _Face):
    dark, light = _tone(f.shade, 0.82), _tone(f.shade, 1.1)
    for k in range(3):
        u, v = f.uniform(0.0, 0.7), 0.0
        pts = [(u, v)]
        for _ in range(4):
            u += f.uniform(0.05, 0.22)
            v += 0.25
            pts.append((min(1.0, u), min(1.0, v)))
        color = dark if k % 2 == 0 else light
        for p, q in zip(pts, pts[1:]):
            f.line(color, p[0], p[1], q[0], q[1])


def _stripes(f: _Face):
    dark = _tone(f.shade, 0.78)
    nb = _count(f.vlen, 0.22, f.lv)
    for j in range(1, nb):
        f.line(dark, 0.0, j / nb, 1.0, j / nb)


def _pleats(f: _Face):
    """Pregas verticais do hakama: linhas escuras com uma clara ao lado, espaçadas como pregas de verdade."""
    dark, light = _tone(f.shade, 0.72), _tone(f.shade, 1.16)
    n = min(_count(f.ulen, 0.045, f.lu), 14)
    for i in range(1, n):
        f.line(dark, i / n, 0.0, i / n, 1.0)
        if i % 2 and f.lu / n > 4.5:
            f.line(light, (i + 0.5) / n, 0.04, (i + 0.5) / n, 0.9)


def _weave(f: _Face):
    """Trama em espinha de peixe do punho dourado das mangas."""
    dark, light = _tone(f.shade, 0.66), _tone(f.shade, 1.18)
    nu, nv = _grid(f, 0.04, 0.04)
    for j in range(nv):
        for i in range(nu):
            if (i + j) % 2:
                f.line(dark, i / nu, j / nv, (i + 1) / nu, (j + 1) / nv)
            else:
                f.line(light, i / nu, (j + 1) / nv, (i + 1) / nu, j / nv)


def _gloss(f: _Face):
    """Reflexo lustroso de curvatura suave com hotspot."""
    f.quad(_light(f.shade, 1.4, 25), 0.20, 0.08, 0.45, 0.92)
    f.line(_light(f.shade, 1.85, 60), 0.28, 0.08, 0.36, 0.92, width=1)
    f.dot((255, 255, 255), 0.32, 0.42, size=2)


def _silk(f: _Face):
    """Seda: dobras compridas e suaves com um brilho claro correndo ao lado de cada uma."""
    dark, light = _tone(f.shade, 0.8), _light(f.shade, 1.28, 6)
    n = max(2, min(_count(f.ulen, 0.11, f.lu), 6))
    for i in range(1, n):
        u = i / n
        f.line(dark if i % 2 else light, u - 0.05, 0.0, u + 0.05, 1.0)
        if i % 2:
            f.line(light, u + 0.06, 0.1, u + 0.12, 0.9)


def _latex(f: _Face):
    """
    Látex / Vinil brilhante (PBR: Roughness ~0.08, alto contraste especular, rim Fresnel):
    - Faixa de reflexo especular de alta intensidade com núcleo branco puro (255, 255, 255).
    - Reflexo Fresnel de borda (rim light) nas arestas de ângulo rasante.
    - Hotspot focalizado com brilho secundário suave e corte nítido de sombra.
    """
    if f.kind == "top":
        # Topo de voxel zenital: reflexo circular/diamante de estúdio
        f.quad(_light(f.shade, 1.45, 45), 0.16, 0.16, 0.72, 0.72)
        f.line(_light(f.shade, 1.9, 90), 0.20, 0.20, 0.68, 0.68, width=2)
        f.dot((255, 255, 255), 0.42, 0.42, size=2)
        return

    # Faces laterais (+X / +Y): curvatura vertical/diagonal pronunciada
    soft_sheen = _light(f.shade, 1.42, 38)
    intense_spec = _light(f.shade, 1.85, 95)
    rim_fresnel = _light(f.shade, 1.65, 75)
    dark_contour = _tone(f.shade, 0.62)

    # 1. Faixa externa de brilho acetinado
    f.quad(soft_sheen, 0.18, 0.04, 0.46, 0.96)
    # 2. Faixa interna de alta intensidade especular
    f.quad(intense_spec, 0.25, 0.04, 0.38, 0.96)
    # 3. Núcleo branco puro no centro do feixe de luz
    f.line((255, 255, 255), 0.30, 0.04, 0.33, 0.96, width=1)
    # 4. Ponto de reflexo especular absoluto (hotspot)
    f.dot((255, 255, 255), 0.31, 0.42, size=2)
    # 5. Efeito Fresnel rasante na borda externa (rim lighting de silhueta)
    f.line(rim_fresnel, 0.04, 0.02, 0.04, 0.98, width=1)
    # 6. Reflexo secundário sutil de rebatimento no lado oposto
    f.line(_light(f.shade, 1.25, 22), 0.68, 0.12, 0.72, 0.88, width=1)
    # 7. Linha de sombra profunda de oclusão ao lado do brilho para máximo contraste
    f.line(dark_contour, 0.48, 0.06, 0.50, 0.94, width=1)


def _leather(f: _Face):
    """
    Couro tratado e polido / Lustroso (PBR: Roughness ~0.28, sheen suave, granulação tátil):
    - Faixa de brilho lustroso contínua ao longo da curvatura da bota, cinto ou colete.
    - Realce de borda chanfrada encerada.
    - Microtextura orgânica pontilhada de poros e costura artesanal tracejada.
    """
    sheen_soft = _light(f.shade, 1.35, 26)
    sheen_bright = _light(f.shade, 1.68, 52)
    edge_waxed = _light(f.shade, 1.45, 22)
    dark_pore = _tone(f.shade, 0.70)
    light_pore = _light(f.shade, 1.22, 12)

    # 1. Faixa larga de brilho de couro polido/hidratado (sheen)
    f.quad(sheen_soft, 0.20, 0.05, 0.46, 0.95)
    f.quad(sheen_bright, 0.27, 0.05, 0.38, 0.95)
    f.line(_light(f.shade, 1.92, 75), 0.32, 0.05, 0.34, 0.95, width=1)
    f.dot(_light(f.shade, 2.1, 95), 0.33, 0.38, size=2)

    # 2. Borda encerada polida (bevel)
    f.line(edge_waxed, 0.05, 0.04, 0.05, 0.96, width=1)

    # 3. Micro-poros orgânicos discretos para relevo de couro
    n_pores = max(3, min(8, int(f.lu * f.lv / 180)))
    for k in range(n_pores):
        f.dot(dark_pore if k % 2 else light_pore, f.uniform(0.52, 0.92), f.random())

    # 4. Costura artesanal pontilhada reforçada na margem direita
    for i in range(0, 8, 2):
        f.line(_light(f.shade, 1.5, 16), 0.92, i / 8.0, 0.92, (i + 0.6) / 8.0, width=1)


def _velvet(f: _Face):
    """Veludo: pelo curto, muitos pontos finos de tom um pouco acima e abaixo."""
    dark, light = _tone(f.shade, 0.84), _light(f.shade, 1.18, 4)
    n = max(8, min(22, int(f.lu * f.lv / 70)))
    for k in range(n):
        f.dot(dark if k % 3 else light, f.random(), f.random())


def _brocade(f: _Face):
    """Brocado: losangos pequenos e pontos dourados em grade, no tom claro da cor."""
    gold = _light(f.shade, 1.7, 40)
    nu, nv = _grid(f, 0.07, 0.07)
    for j in range(nv):
        for i in range(nu):
            if (i + j) % 2 == 0:
                cu, cv = (i + 0.5) / nu, (j + 0.5) / nv
                f.line(gold, cu - 0.4 / nu, cv, cu + 0.4 / nu, cv)
                f.line(gold, cu, cv - 0.4 / nv, cu, cv + 0.4 / nv)


def _canvas(f: _Face):
    """Lona e linho: trama cruzada fina, mais clara que o tom da face."""
    tone = _tone(f.shade, 0.88)
    nu, nv = min(_count(f.ulen, 0.07, f.lu), 9), min(_count(f.vlen, 0.07, f.lv), 9)
    for i in range(1, nu):
        f.line(tone, i / nu, 0.0, i / nu, 1.0)
    for j in range(1, nv, 2):
        f.line(_light(f.shade, 1.1, 2), 0.0, j / nv, 1.0, j / nv)


def _knit(f: _Face):
    """Malha: fileiras de pontos em V."""
    dark = _tone(f.shade, 0.78)
    nu, nv = _grid(f, 0.05, 0.05)
    for j in range(nv):
        for i in range(nu):
            if (i + j) % 2 == 0:
                cu, cv = (i + 0.5) / nu, (j + 0.5) / nv
                f.line(dark, cu - 0.4 / nu, cv - 0.4 / nv, cu, cv + 0.4 / nv)
                f.line(dark, cu, cv + 0.4 / nv, cu + 0.4 / nu, cv - 0.4 / nv)


def _metal(f: _Face):
    """
    Metal Polido & Aço (PBR: Conductor, Metallic 1.0, reflexo de horizonte e estrias anisotrópicas):
    - Reflexo de céu (porção superior clara) e horizonte de solo (corte escuro).
    - Estria vertical anisotrópica espelhada de alto brilho com gume chanfrado (255, 255, 255).
    - Hotspot intenso de reflexão direta da fonte de luz.
    """
    sky_refl = _light(f.shade, 1.55, 50)
    ground_refl = _light(f.shade, 1.22, 18)
    horizon_dark = _tone(f.shade, 0.52)
    spec_streak = _light(f.shade, 1.95, 95)

    if f.kind == "top":
        # Placa superior com chanfro de luz nas 2 arestas superiores
        f.line((255, 255, 255), 0.04, 0.04, 0.96, 0.04, width=1)
        f.line((255, 255, 255), 0.04, 0.04, 0.04, 0.96, width=1)
        f.quad(_light(f.shade, 1.5, 45), 0.15, 0.15, 0.85, 0.85)
        f.dot((255, 255, 255), 0.38, 0.38, size=2)
        return

    # 1. Reflexão de céu na metade superior
    f.quad(sky_refl, 0.04, 0.04, 0.96, 0.46)
    # 2. Linha nítida do horizonte metálico
    f.line(horizon_dark, 0.04, 0.48, 0.96, 0.48, width=1)
    # 3. Reflexão da metade inferior
    f.quad(ground_refl, 0.04, 0.50, 0.96, 0.92)

    # 4. Chanfro superior e lateral de aresta em branco puro (bevel glint)
    f.line((255, 255, 255), 0.04, 0.04, 0.96, 0.04, width=1)
    f.line((255, 255, 255), 0.04, 0.04, 0.04, 0.48, width=1)

    # 5. Faixa anisotrópica vertical reluzente
    f.quad(spec_streak, 0.26, 0.04, 0.38, 0.96)
    f.line((255, 255, 255), 0.31, 0.04, 0.33, 0.96, width=1)
    # 6. Hotspots brancos concentrados
    f.dot((255, 255, 255), 0.32, 0.22, size=2)
    f.dot((255, 255, 255), 0.32, 0.70, size=1)


def _chrome(f: _Face):
    """Cromo espelhado de altíssima refletividade (variação ultra-nítida de metal)."""
    _metal(f)


def _steel(f: _Face):
    """Aço laminado / lâminas de katana, adagas e floretes."""
    _metal(f)


def _gold(f: _Face):
    """
    Ouro Polido (PBR: Conductor com coloração metálica dourada rica):
    - Reflexos em amarelo-dourado vibrante e núcleo platina-ouro (255, 250, 195).
    - Bevel e chanfros dourados cintilantes.
    """
    gold_sky = (min(255, int(f.shade[0] * 1.55) + 60), min(255, int(f.shade[1] * 1.50) + 50), min(255, int(f.shade[2] * 1.05) + 15))
    gold_spec = (min(255, int(f.shade[0] * 1.85) + 85), min(255, int(f.shade[1] * 1.80) + 80), min(255, int(f.shade[2] * 1.20) + 35))
    gold_core = (255, 250, 195)
    gold_dark = _tone(f.shade, 0.60)

    if f.kind == "top":
        f.line(gold_core, 0.04, 0.04, 0.96, 0.04, width=1)
        f.line(gold_core, 0.04, 0.04, 0.04, 0.96, width=1)
        f.quad(gold_sky, 0.15, 0.15, 0.85, 0.85)
        f.dot(gold_core, 0.38, 0.38, size=2)
        return

    # Reflexos dourados
    f.quad(gold_sky, 0.04, 0.04, 0.96, 0.46)
    f.line(gold_dark, 0.04, 0.48, 0.96, 0.48, width=1)
    f.quad(_tone(gold_sky, 0.8), 0.04, 0.50, 0.96, 0.92)

    # Aresta superior cintilante
    f.line(gold_core, 0.04, 0.04, 0.96, 0.04, width=1)
    # Faixa anisotrópica
    f.quad(gold_spec, 0.26, 0.04, 0.40, 0.96)
    f.line(gold_core, 0.32, 0.04, 0.34, 0.96, width=1)
    f.dot((255, 255, 240), 0.33, 0.24, size=2)


def _brushed_metal(f: _Face):
    """Metal escovado: riscos finos e longos ao longo da face com faixa de reflexo brilhante."""
    dark, light = _tone(f.shade, 0.78), _light(f.shade, 1.55, 28)
    # Faixa de brilho do metal
    f.quad(_light(f.shade, 1.50, 35), 0.24, 0.04, 0.42, 0.96)
    f.line((255, 255, 255), 0.32, 0.04, 0.34, 0.96, width=1)
    # Riscos anisotrópicos
    n = max(3, min(_count(f.vlen, 0.04, f.lv), 9))
    for j in range(1, n):
        v = j / n
        a = f.uniform(0.0, 0.3)
        f.line(dark if j % 2 else light, a, v, min(1.0, a + f.uniform(0.4, 0.8)), v, width=1)
    # Bevel superior
    f.line((255, 255, 255), 0.04, 0.04, 0.96, 0.04, width=1)
    f.dot((255, 255, 255), 0.33, 0.28, size=2)


def _lacquer(f: _Face):
    """Laca japonesa (urushi): reflexo nítido de espelho, faixa de transição e brilho pontual."""
    f.quad(_light(f.shade, 1.4, 30), 0.16, 0.04, 0.34, 0.96)
    f.line(_light(f.shade, 1.95, 75), 0.22, 0.04, 0.26, 0.96, width=1)
    f.line(_tone(f.shade, 0.55), 0.36, 0.04, 0.40, 0.96, width=1)
    f.dot((255, 255, 255), 0.24, 0.32, size=2)


PATTERNS = {
    "planks": _planks, "stone": _stone, "roof_tile": _roof_tile, "thatch": _thatch, "bark": _bark,
    "cloth": _cloth, "plaster": _plaster, "foliage": _foliage, "marble": _marble, "stripes": _stripes,
    "pleats": _pleats, "weave": _weave, "gloss": _gloss,
    "silk": _silk, "latex": _latex, "leather": _leather, "velvet": _velvet, "brocade": _brocade, "canvas": _canvas, "knit": _knit,
    "brushed_metal": _brushed_metal, "metal": _metal, "chrome": _chrome, "steel": _steel, "gold": _gold, "lacquer": _lacquer,
}


def draw_face_texture(surface, name, poly, kind, ulen, vlen, shade, seed=0):
    """Desenha o padrão `name` na face (poly = a, b, c, d) com arestas de ulen x vlen unidades de mundo."""
    pattern = PATTERNS.get(name)
    if pattern is None or not quality.is_high():
        return
    face = _Face(surface, poly, kind, ulen, vlen, shade, seed)
    if face.lu < MIN_FACE_PX or face.lv < MIN_FACE_PX:
        return
    pattern(face)
