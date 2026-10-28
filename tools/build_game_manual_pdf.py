#!/usr/bin/env python3
"""
Compilador Oficial do Manual de Instruções em PDF de Samurai Edge: Bakumatsu.
Edição Condensada de 24 Páginas (Dois Lutadores e Duas Arenas por Página).

Gera duas edições completas e profissionais:
- docs/Samurai_Edge_Manual_PT.pdf (Edição em Português)
- docs/Samurai_Edge_Manual_EN.pdf (Edição em Inglês)

Diagramação:
- Formato A4 Vertical (595.27 x 841.89 pt) no estilo clássico Neo Geo / 90s Arcade.
- Pergaminho Sumi-E estilizado (#FAF6ED) com moldura dupla em laca e ouro (#3C2214 / #9E7A38).
- Tipografia: Shojumaru (títulos ornamentais) e Zen Antique Soft (corpo e tabelas com suporte kanji/japonês).
- Distribuição espacial otimizada preenchendo toda a extensão da página com proporção áurea.
- Imagens 100% proporcionais sem distorção ou esticamento.
- Tabela Fiel de 2 Ações Específicas do Combatente (Ataque Primário + Ação Secundária).
- Dados 100% canônicos do motor (Musashi 3 HP, Raiden 3 HP, cão Yamato, Chiyo Dual Kodachi, Kenshi Ryuu Tsui-Sen, e perigos/fossos reais das arenas).
"""

import os
import sys
from PIL import Image as PILImage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Importar bases de dados sincronizadas
import tools.manual_fighters_data as fighters_db
import tools.manual_arenas_data as arenas_db
import tools.manual_data_pt as data_pt
import tools.manual_data_en as data_en

# Registro de fontes
FONTS_DIR = "assets/fonts"
pdfmetrics.registerFont(TTFont("Shojumaru", os.path.join(FONTS_DIR, "Shojumaru-Regular.ttf")))
pdfmetrics.registerFont(TTFont("ZenAntique", os.path.join(FONTS_DIR, "ZenAntique-Regular.ttf")))
if os.path.exists(os.path.join(FONTS_DIR, "Cinzel-Regular.ttf")):
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(FONTS_DIR, "Cinzel-Regular.ttf")))
else:
    pdfmetrics.registerFont(TTFont("Cinzel", os.path.join(FONTS_DIR, "Shojumaru-Regular.ttf")))

# Paleta de cores Sumi-E Neo-Geo
COLOR_BG_PARCHMENT = colors.HexColor("#FAF6ED")
COLOR_BORDER_DARK = colors.HexColor("#3C2214")
COLOR_BORDER_GOLD = colors.HexColor("#9E7A38")
COLOR_CRIMSON = colors.HexColor("#8C1D13")
COLOR_INK_BLACK = colors.HexColor("#1A1410")
COLOR_MUTED_TEXT = colors.HexColor("#4A3B32")
COLOR_TABLE_HEADER = colors.HexColor("#2B180E")
COLOR_TABLE_ALT = colors.HexColor("#F2EDE0")


class NumberedParchmentCanvas(canvas.Canvas):
    """Canvas com numeração em duas etapas e cabeçalhos / rodapés cerimoniais."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        w, h = A4
        page = self._pageNumber

        # Capa (Página 1) e Contra-capa (Página final) possuem molduras especiais
        if page == 1 or page == total_pages:
            self.saveState()
            self.setStrokeColor(COLOR_BORDER_DARK)
            self.setLineWidth(2.5)
            self.rect(20, 20, w - 40, h - 40)
            self.setStrokeColor(COLOR_BORDER_GOLD)
            self.setLineWidth(0.8)
            self.rect(24, 24, w - 48, h - 48)
            self.restoreState()
            return

        self.saveState()
        # Moldura geométrica Sumi-E
        self.setStrokeColor(COLOR_BORDER_DARK)
        self.setLineWidth(1.5)
        self.rect(16, 16, w - 32, h - 32)
        self.setStrokeColor(COLOR_BORDER_GOLD)
        self.setLineWidth(0.6)
        self.rect(20, 20, w - 40, h - 40)

        # Cabeçalho cerimonial
        self.setStrokeColor(COLOR_CRIMSON)
        self.setLineWidth(1.0)
        self.line(32, h - 26, w - 32, h - 26)

        lang = getattr(self, "lang_code", "PT")
        hdr_left = "SAMURAI EDGE: BAKUMATSU — MANUAL OFICIAL" if lang == "PT" else "SAMURAI EDGE: BAKUMATSU — OFFICIAL MANUAL"
        hdr_right = "幕末の血闘 (UNIFIED DOSSIERS)"
        
        self.setFont("ZenAntique", 7.8)
        self.setFillColor(COLOR_CRIMSON)
        self.drawString(32, h - 22, hdr_left)
        self.drawRightString(w - 32, h - 22, hdr_right)

        # Rodapé cerimonial
        self.setStrokeColor(COLOR_BORDER_DARK)
        self.setLineWidth(0.8)
        self.line(32, 32, w - 32, 32)

        ftr_left = "24 GUERREIROS & 24 ARENAS" if lang == "PT" else "24 WARRIORS & 24 ARENAS"
        ftr_right = "EDIÇÃO CONDENSADA (24 PÁGINAS)" if lang == "PT" else "CONDENSED EDITION (24 PAGES)"
        page_str = f"— 頁 {page} / {total_pages} —"

        self.setFont("ZenAntique", 7.5)
        self.setFillColor(COLOR_MUTED_TEXT)
        self.drawString(32, 22, ftr_left)
        self.drawRightString(w - 32, 22, ftr_right)

        self.setFont("ZenAntique", 8.5)
        self.setFillColor(COLOR_CRIMSON)
        self.drawCentredString(w / 2.0, 22, page_str)

        self.restoreState()


def draw_parchment_background(canvas_obj, doc):
    """Pinta o fundo de pergaminho cru em todas as páginas."""
    w, h = A4
    canvas_obj.saveState()
    canvas_obj.setFillColor(COLOR_BG_PARCHMENT)
    canvas_obj.rect(0, 0, w, h, fill=1, stroke=0)
    canvas_obj.restoreState()


def get_proportional_img(path, target_w=None, target_h=None):
    """Garante que a imagem mantenha 100% de sua proporção intrínseca sem distorcer."""
    if not os.path.exists(path):
        return Spacer(1, target_h or 60)
    try:
        with PILImage.open(path) as im:
            ow, oh = im.size
        if target_w and not target_h:
            th = target_w * (oh / float(ow))
            return Image(path, width=target_w, height=th)
        elif target_h and not target_w:
            tw = target_h * (ow / float(oh))
            return Image(path, width=tw, height=target_h)
        elif target_w and target_h:
            r = min(target_w / float(ow), target_h / float(oh))
            return Image(path, width=ow * r, height=oh * r)
    except Exception:
        pass
    return Image(path, width=target_w or 60, height=target_h or 60)


def create_styles():
    """Gera o conjunto de estilos tipográficos com fontes embutidas."""
    styles = getSampleStyleSheet()

    title_cover = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=26,
        leading=32,
        textColor=COLOR_CRIMSON,
        alignment=1,
        spaceAfter=8
    )
    subtitle_cover = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=11,
        leading=15,
        textColor=COLOR_INK_BLACK,
        alignment=1,
        spaceAfter=12
    )
    badge_cover = ParagraphStyle(
        "CoverBadge",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=9.5,
        leading=13,
        textColor=COLOR_BORDER_GOLD,
        alignment=1,
        spaceAfter=8
    )

    page_header = ParagraphStyle(
        "PageHeader",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=13,
        leading=16,
        textColor=COLOR_CRIMSON,
        spaceAfter=2
    )
    page_sub = ParagraphStyle(
        "PageSub",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=7.6,
        leading=9.5,
        textColor=COLOR_MUTED_TEXT,
        spaceAfter=3
    )

    sec_heading = ParagraphStyle(
        "SecHeading",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=8.0,
        leading=10.0,
        textColor=COLOR_CRIMSON,
        spaceBefore=2,
        spaceAfter=1.5
    )

    body_text = ParagraphStyle(
        "BodyTextZen",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=6.8,
        leading=8.4,
        textColor=COLOR_INK_BLACK,
        spaceAfter=2
    )

    table_header_style = ParagraphStyle(
        "TableHdr",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=6.8,
        leading=8.2,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=6.4,
        leading=7.8,
        textColor=COLOR_INK_BLACK
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=6.6,
        leading=8.0,
        textColor=COLOR_CRIMSON
    )

    poem_jp = ParagraphStyle(
        "PoemJP",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=10.5,
        leading=14.5,
        textColor=COLOR_INK_BLACK,
        alignment=1
    )

    poem_author = ParagraphStyle(
        "PoemAuthor",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=8.0,
        leading=10.5,
        textColor=COLOR_MUTED_TEXT,
        alignment=1
    )

    poem_tr = ParagraphStyle(
        "PoemTR",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=8.5,
        leading=11.5,
        textColor=COLOR_CRIMSON,
        alignment=1
    )

    return {
        "title_cover": title_cover,
        "subtitle_cover": subtitle_cover,
        "badge_cover": badge_cover,
        "page_header": page_header,
        "page_sub": page_sub,
        "sec_heading": sec_heading,
        "body_text": body_text,
        "table_header": table_header_style,
        "table_cell": table_cell_style,
        "table_cell_bold": table_cell_bold,
        "poem_jp": poem_jp,
        "poem_author": poem_author,
        "poem_tr": poem_tr,
    }


def build_cover_page(story, styles, lang="PT"):
    """Página 1: Capa cerimonial."""
    logo_path = "assets/concepts/sumie_title_logo_concept.jpg"
    story.append(Spacer(1, 15))
    if os.path.exists(logo_path):
        story.append(get_proportional_img(logo_path, target_w=480))
    else:
        story.append(Spacer(1, 200))

    story.append(Spacer(1, 25))
    if lang == "PT":
        story.append(Paragraph("SAMURAI EDGE", styles["title_cover"]))
        story.append(Paragraph("幕末血風録 — O CREPÚSCULO DO AÇO", styles["subtitle_cover"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph("MANUAL DE INSTRUÇÕES & GUIA ESTRATÉGICO OFICIAL", styles["subtitle_cover"]))
        story.append(Paragraph("EDIÇÃO UNIFICADA CONDENSADA: 24 GUERREIROS & 24 ARENAS", styles["badge_cover"]))
        story.append(Spacer(1, 35))
        story.append(Paragraph("ARQUIVO HISTÓRICO & TÁTICAS DE COMBATE DIEGÉTICO", styles["badge_cover"]))
        story.append(Paragraph("EDO • KYOTO • IGA • NAGASAKI (1860–1868)", styles["subtitle_cover"]))
    else:
        story.append(Paragraph("SAMURAI EDGE", styles["title_cover"]))
        story.append(Paragraph("BAKUMATSU COMBAT CHRONICLES — TWILIGHT OF STEEL", styles["subtitle_cover"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph("OFFICIAL INSTRUCTION MANUAL & STRATEGY GUIDE", styles["subtitle_cover"]))
        story.append(Paragraph("CONDENSED UNIFIED EDITION: 24 WARRIORS & 24 HOME ARENAS", styles["badge_cover"]))
        story.append(Spacer(1, 35))
        story.append(Paragraph("HISTORICAL ARCHIVE & DIEGETIC DUEL COMBAT DOCTRINE", styles["badge_cover"]))
        story.append(Paragraph("EDO • KYOTO • IGA • NAGASAKI (1860–1868)", styles["subtitle_cover"]))

    story.append(PageBreak())


def build_toc_page(story, styles, lang="PT"):
    """Página 2: Índice geral organizado para a edição condensada de 24 páginas."""
    title = "ÍNDICE GERAL DE COMBATE" if lang == "PT" else "TABLE OF CONTENTS"
    sub = "ESTRUTURA METÓDICA DO MANUAL DO GUERREIRO (24 PÁGINAS)" if lang == "PT" else "METHODICAL MANUAL STRUCTURE (24 PAGES)"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    entries_pt = [
        ("I. SUMÁRIO & CONTEXTO HISTÓRICO", "A Lenda do Bakumatsu e o Selo das Cinzas", "Pág. 03"),
        ("II. AS SETE FACÇÕES EM GUERRA", "Ideologias, Alianças e os Protetores do Povo", "Pág. 04"),
        ("III. COMANDOS BÁSICOS & SISTEMA", "Controles (E / R / T / WASD), Clash QTE e Precedência", "Pág. 05"),
        ("IV. MODOS DE COMBATE & PRELÚDIO", "Arcade (12 Lutas), Versus e Filosofia Maai/Mushin", "Pág. 06"),
        ("V. DOSSIÊS UNIFICADOS (2 LUTADORES & 2 ARENAS POR PÁGINA)", "24 Guerreiros e Arenas em Alta Densidade", "Págs. 07–18"),
        ("   • 01. Kenshi (Bambu) & 02. Musashi (Ilha Ganryu)", "Arashiyama / Estreito de Kanmon", "Pág. 07"),
        ("   • 03. Hanzo (Iga) & 04. Joe (Acampamento / Cão Yamato)", "Fortaleza das Sombras / Vales de Iga", "Pág. 08"),
        ("   • 05. Saitou (Kyoto) & 06. Teppo (Nagashino)", "Incidente Ikedaya / Bastião Tanegashima", "Pág. 09"),
        ("   • 07. Murasaki (Gruta) & 08. Kasumi (Templo da Névoa)", "Covil do Titã / Monte Hiei", "Pág. 10"),
        ("   • 09. Okuni (Kabuki) & 10. Tomoe (Santuário da Montanha)", "Rio Kamo / Monte Kurama", "Pág. 11"),
        ("   • 11. Anne (Navio) & 12. Julie (Corte Barroca)", "Baía de Uraga / Porto de Yokohama", "Pág. 12"),
        ("   • 13. Ren (Shaolin) & 14. Chiyo (Higanbana / Dual Kodachi)", "Songshan / Planícies de Asuka", "Pág. 13"),
        ("   • 15. Benkei (Ponte Gojo) & 16. O-Rin (Beco Yoshiwara)", "Passagem Cerimonial / Distrito das Flores", "Pág. 14"),
        ("   • 17. Goro (Arrozais) & 18. Ichi (Moinho Chuvoso)", "Campos de Omi / Passagem de Hakone", "Pág. 15"),
        ("   • 19. Valerius (Cemitério) & 20. Seimei (Pavilhão Heian)", "Criptas da Silésia / Altar Astral", "Pág. 16"),
        ("   • 21. Daiki (Pinheiros) & 22. Aoi (Taiga de Ezo)", "Monte Koya / Terras Ancestrais Ainu", "Pág. 17"),
        ("   • 23. Raiden (Dohyo / 3 HP) & 24. Hendrika (Dejima)", "Sumiyoshi Taisha / Feitoria Holandesa", "Pág. 18"),
        ("VI. O DESPERTAR PROIBIDO — O CHEFE FINAL", "O Titã Esquelético Oni Gashadokuro", "Pág. 19"),
        ("VII. APÊNDICE: TABELA GERAL DE DESEMPENHO", "Simulação Massiva de 6.624 Duelos (Tier List)", "Pág. 20"),
        ("VIII. APÊNDICE: GUIA DE PRIORIDADES & PRECEDÊNCIA", "Mecânicas Avançadas e Choque de Lâminas", "Pág. 21"),
        ("IX. APÊNDICE: TABELA DE REAGENTES DE SOLO", "Alquimia Clandestina & Elementos de Seimei", "Pág. 22"),
        ("X. APÊNDICE: GLOSSÁRIO MARCIAL & BUSHIDO", "Termos Clássicos do Combate Samurai", "Pág. 23"),
        ("XI. CONTRA-CAPA & CRÉDITOS DA PRODUÇÃO", "Ficha Técnica e Agradecimentos Especiais", "Pág. 24")
    ]

    entries_en = [
        ("I. INTRODUCTION & HISTORICAL LORE", "The Legend of Bakumatsu and the Ash Seal", "Page 03"),
        ("II. THE SEVEN WARRING FACTIONS", "Ideologies, Alliances & Protectors of the People", "Page 04"),
        ("III. BASIC CONTROLS & DUEL SYSTEM", "Controls (E / R / T / WASD), Clash QTE & Priority", "Page 05"),
        ("IV. COMBAT MODES & PRELUDE", "Arcade Ladder (12 Fights), Versus & Maai/Mushin", "Page 06"),
        ("V. UNIFIED DOSSIERS (2 FIGHTERS & 2 ARENAS PER PAGE)", "24 Champions & Home Arenas in High Density", "Pages 07–18"),
        ("   • 01. Kenshi (Bamboo) & 02. Musashi (Ganryu Island)", "Arashiyama / Kanmon Strait", "Page 07"),
        ("   • 03. Hanzo (Iga) & 04. Joe (Forest Camp / Dog Yamato)", "Shadow Fortress / Iga Woods", "Page 08"),
        ("   • 05. Saitou (Kyoto) & 06. Teppo (Nagashino)", "Ikedaya Raid / Matchlock Stronghold", "Page 09"),
        ("   • 07. Murasaki (Cave) & 08. Kasumi (Mist Temple)", "Titan Den / Mount Hiei Sanctuary", "Page 10"),
        ("   • 09. Okuni (Kabuki) & 10. Tomoe (Mountain Shrine)", "Kamo Riverbed / Mount Kurama", "Page 11"),
        ("   • 11. Anne (Ship Deck) & 12. Julie (Baroque Court)", "Uraga Bay Frigate / Yokohama Enclave", "Page 12"),
        ("   • 13. Ren (Shaolin) & 14. Chiyo (Higanbana / Dual Kodachi)", "Songshan / Asuka Plains", "Page 13"),
        ("   • 15. Benkei (Gojo Bridge) & 16. O-Rin (Yoshiwara)", "Kyoto Span / Red Lantern Quarter", "Page 14"),
        ("   • 17. Goro (Paddies) & 18. Ichi (Rain Mill)", "Omi Terraces / Hakone Cataracts", "Page 15"),
        ("   • 19. Valerius (Cemetery) & 20. Seimei (Heian Altar)", "Silesian Crypts / Astral Pentagram", "Page 16"),
        ("   • 21. Daiki (Pines) & 22. Aoi (Ezo Taiga)", "Mount Koya / Ancestral Ainu Lands", "Page 17"),
        ("   • 23. Raiden (Dohyo / 3 HP) & 24. Hendrika (Dejima)", "Sumiyoshi Taisha / Dutch VOC Factory", "Page 18"),
        ("VI. THE FORBIDDEN AWAKENING — FINAL BOSS", "The Skeletal Titan Oni Gashadokuro", "Page 19"),
        ("VII. APPENDIX: OVERALL PERFORMANCE TABLE", "Large-Scale 6,624 Duels Simulation (Tier List)", "Page 20"),
        ("VIII. APPENDIX: ABSOLUTE PRECEDENCE RULES", "Advanced Combat Priority & Blade Clash QTE", "Page 21"),
        ("IX. APPENDIX: SOIL REAGENTS ALCHEMY TABLE", "Clandestine Alchemy & Seimei Elements", "Page 22"),
        ("X. APPENDIX: MARTIAL GLOSSARY & BUSHIDO", "Classical Samurai Combat Terms", "Page 23"),
        ("XI. BACK COVER & PRODUCTION CREDITS", "Technical Colophon & Special Dedication", "Page 24")
    ]

    entries = entries_pt if lang == "PT" else entries_en
    table_data = []
    for section, desc, page_num in entries:
        table_data.append([
            Paragraph(section, styles["table_cell_bold"]),
            Paragraph(desc, styles["table_cell"]),
            Paragraph(f"<b>{page_num}</b>", styles["table_cell_bold"])
        ])

    toc_table = Table(table_data, colWidths=[210, 265, 55])
    toc_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0D6C3")),
    ]))

    story.append(toc_table)
    story.append(Spacer(1, 8))

    # Painel explicativo e cerimonial sobre a estrutura e o compêndio (2 Colunas)
    col1_title = "ESTRUTURA METÓDICA DO COMPÊNDIO" if lang == "PT" else "METHODICAL COMPENDIUM STRUCTURE"
    col1_p1 = (
        "• <b>Dossiês Unificados em Alta Densidade (Págs. 07–18):</b> Cada página reúne dois guerreiros com suas respectivas "
        "arenas natais, apresentando biografia condensada, atributos canônicos e dinâmica de solo." if lang == "PT" else
        "• <b>High-Density Unified Dossiers (Pages 07–18):</b> Each page unites two fighters alongside their home arenas, "
        "presenting concise lore, canonical metrics, and soil dynamics."
    )
    col1_p2 = (
        "• <b>Proporcionalidade Visual Preservada:</b> Retratos verticais de combate (3:4) e ilustrações panorâmicas de arenas (16:9) "
        "foram dimensionados respeitando rigorosamente suas proporções nativas." if lang == "PT" else
        "• <b>Strict Visual Proportions:</b> Fighter combat portraits (3:4) and widescreen arena previews (16:9) are strictly "
        "scaled to their native aspect ratios without distortion."
    )
    col1_p3 = (
        "• <b>Fidelidade Matemática ao Motor:</b> Vitalidade canônica (3 HP para Musashi e Raiden, 2 HP para os demais), "
        "velocidades reais em m/s e contagem precisa de fossos de queda." if lang == "PT" else
        "• <b>Engine Ground Truth:</b> Vitality metrics (3 HP for Musashi and Raiden, 2 HP for all other 22 fighters), "
        "velocities (m/s), and ring-out pit counts match engine source code."
    )

    col2_title = "CONVENÇÕES & SIMBOLOGIA MARCIAL" if lang == "PT" else "MARTIAL CONVENTIONS & SYMBOLOGY"
    col2_p1 = (
        "• <b>Comandos Universais Diegéticos:</b> Saque Primário [E], Ação Especial [R], Esquiva Dedicada [T] e Bloqueio [F] "
        "constituem a base de resposta instantânea para todos os 24 estilos." if lang == "PT" else
        "• <b>Universal Diegetic Inputs:</b> Primary Attack [E], Special Action [R], Dedicated Roll [T], and Guard [F] "
        "form the core instant-response foundation for all 24 combat styles."
    )
    col2_p2 = (
        "• <b>Morte Súbita sem Barras Infladas:</b> Não existem barras de vida alongadas. O primeiro acerto limpo em contra-golpe "
        "ou na recuperação de um erro sela o destino do confronto." if lang == "PT" else
        "• <b>Sudden Death Lethality:</b> No inflated health bars. The first clean strike landed during counter-attack "
        "or whiffed recovery seals the outcome of the clash."
    )
    col2_p3 = (
        "• <b>Choque de Lâminas (Blade Clash QTE):</b> Colisão simétrica no mesmo frame aciona disputa em tempo real "
        "de digitação veloz, forçando 24 frames de cambaleio no perdedor." if lang == "PT" else
        "• <b>Blade Clash QTE:</b> Symmetric blade collision on the exact same frame triggers real-time rapid-mash contest, "
        "inflicting 24 frames of off-balance stagger upon the loser."
    )

    motto = (
        "<i>«O guerreiro sábio estuda o terreno e a lâmina antes de desembainhar o aço no primeiro duelo.»</i>" if lang == "PT" else
        "<i>«The wise warrior studies both the ground and the blade before drawing steel in the opening clash.»</i>"
    )

    t_box = Table([[
        [
            Paragraph(f"<b>{col1_title}</b>", styles["sec_heading"]),
            Spacer(1, 2),
            Paragraph(col1_p1, styles["body_text"]),
            Spacer(1, 1.5),
            Paragraph(col1_p2, styles["body_text"]),
            Spacer(1, 1.5),
            Paragraph(col1_p3, styles["body_text"]),
        ],
        [
            Paragraph(f"<b>{col2_title}</b>", styles["sec_heading"]),
            Spacer(1, 2),
            Paragraph(col2_p1, styles["body_text"]),
            Spacer(1, 1.5),
            Paragraph(col2_p2, styles["body_text"]),
            Spacer(1, 1.5),
            Paragraph(col2_p3, styles["body_text"]),
        ]
    ]], colWidths=[260, 265])
    t_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.8, COLOR_BORDER_GOLD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 5))

    t_motto = Table([[Paragraph(f"<font color='#8C1D13'><b>{motto}</b></font>", styles["page_sub"])]], colWidths=[530])
    t_motto.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_motto)

    story.append(PageBreak())


def build_lore_page(story, styles, lang="PT"):
    """Página 3: Lore & Ambientação Histórica do Bakumatsu."""
    l_data = data_pt.LORE_PT if lang == "PT" else data_en.LORE_EN

    story.append(Paragraph(l_data["title"], styles["page_header"]))
    sub = "O CREPÚSCULO DO XOGUNATO & A PROFECIA DO SANGUE" if lang == "PT" else "TWILIGHT OF THE SHOGUNATE & THE BLOOD PROPHECY"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=5))

    banner_art = "assets/concepts/kyoto_bakumatsu_concept.jpg"
    if os.path.exists(banner_art):
        story.append(get_proportional_img(banner_art, target_w=530))
        story.append(Spacer(1, 5))

    story.append(Paragraph("<b>1. O Fim de Dois Séculos de Paz (Sakoku)</b>" if lang == "PT" else "<b>1. The End of Two Centuries of Peace (Sakoku)</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p1"], styles["body_text"]))
    story.append(Spacer(1, 3.5))

    story.append(Paragraph("<b>2. O Titã Adormecido na Caverna Sombria</b>" if lang == "PT" else "<b>2. The Slumbering Titan in the Shadow Cave</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p2"], styles["body_text"]))
    story.append(Spacer(1, 3.5))

    story.append(Paragraph("<b>3. A Conspiração do Despertar</b>" if lang == "PT" else "<b>3. The Conspiracy of the Awakening</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p3"], styles["body_text"]))
    story.append(Spacer(1, 3.5))

    story.append(Paragraph("<b>4. O Dilema Moral do Aço (Katsujinken vs Setsuninto)</b>" if lang == "PT" else "<b>4. The Moral Dilemma of Steel (Katsujinken vs Setsuninto)</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p4"], styles["body_text"]))
    story.append(Spacer(1, 3.5))

    story.append(Paragraph("<b>5. O Ponto sem Retorno no Crepúsculo de 1863</b>" if lang == "PT" else "<b>5. The Point of No Return in the Twilight of 1863</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p5"], styles["body_text"]))
    story.append(Spacer(1, 5))

    # Painel de crônica e citação sagrada de fechamento
    cron_title = "CRÔNICA DO CREPÚSCULO & O DESTINO DE IGA" if lang == "PT" else "CHRONICLE OF THE TWILIGHT & THE FATE OF IGA"
    cron_p = (
        "O sangue derramado nas províncias de Kyoto, Iga, Ezo e Nagasaki atua como o catalisador espiritual para romper o selo de ferro "
        "do Oni Gashadokuro. Apenas a espada que preserva a vida (Katsujinken) possui o poder de purificar as cinzas do Japão feudal." if lang == "PT" else
        "The spilled blood across Kyoto, Iga, Ezo, and Nagasaki serves as the spiritual catalyst shattering the ancient iron seal "
        "of the Oni Gashadokuro. Only the life-giving sword (Katsujinken) holds the virtue to purify the ashes of feudal Japan."
    )
    quote_str = (
        "«No fio da navalha, entre o saque e o corte, não há espaço para o ódio: apenas a verdade nua do aço.<br/>"
        "Aquele que hesita diante da névoa de Iga já repousa na terra com os ancestrais.»" if lang == "PT" else
        "«Upon the razor's edge, between the draw and the cleave, there is no room for hatred: only the naked truth of steel.<br/>"
        "He who wavers before the mists of Iga already rests beneath the earth with the ancestors.»"
    )

    t_lore_box = Table([[
        [
            Paragraph(f"<b>{cron_title}</b>", styles["sec_heading"]),
            Spacer(1, 2),
            Paragraph(cron_p, styles["body_text"]),
            Spacer(1, 3),
            Paragraph(f"<font color='#8C1D13'><b>{quote_str}</b></font>", styles["page_sub"])
        ]
    ]], colWidths=[530])
    t_lore_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.8, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_lore_box)

    story.append(PageBreak())


def build_factions_page(story, styles, lang="PT"):
    """Página 4: As 7 Facções em Guerra."""
    factions = data_pt.FACTIONS_PT if lang == "PT" else data_en.FACTIONS_EN
    title = "AS SETE FACÇÕES EM GUERRA" if lang == "PT" else "THE SEVEN WARRING FACTIONS"
    sub = "ALIANÇAS, LEALDADES E MOTIVAÇÕES DO SANGUE" if lang == "PT" else "ALLIANCES, LOYALTIES & BLOOD MOTIVATIONS"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    for f in factions:
        story.append(Paragraph(f["name"], styles["sec_heading"]))
        members_str = ", ".join(f["members"])
        lbl_members = "<b>Integrantes:</b> " if lang == "PT" else "<b>Members:</b> "
        lbl_phil = "<b>Filosofia:</b> " if lang == "PT" else "<b>Philosophy:</b> "

        p_desc = f"{f['desc']}<br/>{lbl_members}<font color='#8C1D13'>{members_str}</font> &nbsp;|&nbsp; {lbl_phil}<i>{f['philosophy']}</i>"
        story.append(Paragraph(p_desc, styles["body_text"]))
        story.append(Spacer(1, 2.5))

    story.append(Spacer(1, 3))
    mat_hdr = "DINÂMICA DE ALIANÇAS & COALIZÕES NO MODO ARCADE" if lang == "PT" else "ALLIANCE DYNAMICS & COALITIONS IN ARCADE MODE"
    story.append(Paragraph(f"<b>{mat_hdr}</b>", styles["sec_heading"]))

    matrix_rows = [
        [
            Paragraph("<b>Coalizão</b>" if lang == "PT" else "<b>Coalition</b>", styles["table_header"]),
            Paragraph("<b>Facções Integradas</b>" if lang == "PT" else "<b>Aligned Factions</b>", styles["table_header"]),
            Paragraph("<b>Postura Diante do Despertar do Titã</b>" if lang == "PT" else "<b>Stance on the Titan Awakening</b>", styles["table_header"])
        ],
        [
            Paragraph("<b>Aliança Protetora</b>" if lang == "PT" else "<b>Guardian Alliance</b>", styles["table_cell_bold"]),
            Paragraph("Protetores do Povo & Aliado Temporal (Joe)" if lang == "PT" else "Protectors of the People & Temporal Ally (Joe)", styles["table_cell"]),
            Paragraph("Unem forças aos ninjas de Iga para conter o massacre e proteger civis indefesos." if lang == "PT" else "Join forces with the Iga shinobi to stem bloodshed and shield defenseless villagers.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Selo das Sombras</b>" if lang == "PT" else "<b>Shadow Seal</b>", styles["table_cell_bold"]),
            Paragraph("Guardiões de Iga (Hanzo, Kasumi, Murasaki, Chiyo)" if lang == "PT" else "Iga Guardians (Hanzo, Kasumi, Murasaki, Chiyo)", styles["table_cell"]),
            Paragraph("Sacrifício absoluto: guardam a Caverna Sombria até a morte contra qualquer invasor." if lang == "PT" else "Absolute sacrifice: defend the Shadow Cave to the death against any and all intruders.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Duelistas de Honra</b>" if lang == "PT" else "<b>Duelists of Honor</b>", styles["table_cell_bold"]),
            Paragraph("Duelistas do Auge, Lealistas e Mercenários" if lang == "PT" else "Duelists of the Pinnacle, Loyalists & Mercenaries", styles["table_cell"]),
            Paragraph("Lutam por dever ou maestria; ao testemunharem o Oni, unem seu aço à salvação do país." if lang == "PT" else "Fight for honor or oaths; upon witnessing the Oni arise, unite their steel to save the realm.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Colheita Oculta</b>" if lang == "PT" else "<b>Occult Harvesters</b>", styles["table_cell_bold"]),
            Paragraph("Oportunistas & Cientistas do Caos" if lang == "PT" else "Opportunists & Scientists of Chaos", styles["table_cell"]),
            Paragraph("Buscam catalisar miasmas alquímicos e colher relíquias místicas alimentadas pelo massacre." if lang == "PT" else "Seek to catalyze alchemical miasmas and harvest eldritch relics fueled by the slaughter.", styles["table_cell"])
        ]
    ]

    mat_table = Table(matrix_rows, colWidths=[110, 160, 260])
    mat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(mat_table)
    story.append(Spacer(1, 4))

    # Matriz de rivalidades históricas canônicas para preenchimento harmônico
    riv_title = "MATRIZ DE RIVALIDADES CANÔNICAS & DUELOS HISTÓRICOS" if lang == "PT" else "CANONICAL RIVALRY MATRIX & HISTORIC CLASHES"
    riv_points = [
        "• <b>Kenshi vs Saitou:</b> O confronto ideológico supremo entre o Protetor dos Fracos e o Lobo Lealista do Shinsengumi nas ruas de Kyoto." if lang == "PT" else
        "• <b>Kenshi vs Saitou:</b> The supreme ideological duel between the Protector of Innocents and the Shinsengumi Wolf across Kyoto.",

        "• <b>Hanzo vs Joe:</b> O choque de doutrinas entre o mestre do Ninjutsu feudal e o operador militar com armas táticas modernas e Yamato." if lang == "PT" else
        "• <b>Hanzo vs Joe:</b> The clash of doctrines between the feudal Ninjutsu master and the modern tactical operator with Yamato.",

        "• <b>Musashi vs Benkei:</b> Duelo monumental entre o virtuosismo das Duas Espadas e o peso esmagador do Kanabo sobre a Ponte Gojo." if lang == "PT" else
        "• <b>Musashi vs Benkei:</b> Monumental clash pitting the virtuosity of Dual Blades against the crushing weight of the Kanabo on Gojo Bridge.",

        "• <b>Hendrika vs Seimei:</b> O embate da ciência química ocidental de Dejima contra o misticismo cósmico milenar do Onmyodo." if lang == "PT" else
        "• <b>Hendrika vs Seimei:</b> The epistemological duel between Western chemical science at Dejima and the cosmic mysticism of Onmyodo."
    ]

    t_riv = Table([[
        [
            Paragraph(f"<b>{riv_title}</b>", styles["sec_heading"]),
            Spacer(1, 1.5),
            Paragraph(riv_points[0], styles["body_text"]),
            Paragraph(riv_points[1], styles["body_text"]),
            Paragraph(riv_points[2], styles["body_text"]),
            Paragraph(riv_points[3], styles["body_text"])
        ]
    ]], colWidths=[530])
    t_riv.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_riv)
    story.append(Spacer(1, 3))

    fac_note = (
        "<i>«A jornada individual de cada guerreiro no Modo Arcade reflete sua filiação: enquanto os Protetores buscam pacificar "
        "as províncias, os Oportunistas tentam usurpar a energia da Caverna Sombria para seus próprios experimentos profanos.»</i>" if lang == "PT" else
        "<i>«Each warrior's path through Arcade Mode reflects their allegiance: while the Protectors strive to pacify warring provinces, "
        "the Opportunists scheme to harness the dark power of the Shadow Cave for their own forbidden alchemy.»</i>"
    )
    t_fn = Table([[Paragraph(f"<font color='#8C1D13'>{fac_note}</font>", styles["page_sub"])]], colWidths=[530])
    t_fn.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_fn)

    story.append(PageBreak())


def build_controls_page(story, styles, lang="PT"):
    """Página 5: Comandos Básicos & Mecânicas de Duelo."""
    c_data = data_pt.CONTROLS_PT if lang == "PT" else data_en.CONTROLS_EN

    story.append(Paragraph(c_data["title"], styles["page_header"]))
    sub = "SISTEMA DE CONTROLE DIEGÉTICO E LETALIDADE DE UMA LÂMINA" if lang == "PT" else "DIEGETIC CONTROL SYSTEM & SINGLE-BLADE LETHALITY"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    story.append(Paragraph(c_data["desc"], styles["body_text"]))
    story.append(Spacer(1, 3))

    headers = ["Ação Marcial", "Gamepad Universal", "Teclado (P1 / P2)", "Efeito Tático"] if lang == "PT" else ["Martial Action", "Universal Gamepad", "Keyboard (P1 / P2)", "Tactical Effect"]
    table_rows = [[
        Paragraph(headers[0], styles["table_header"]),
        Paragraph(headers[1], styles["table_header"]),
        Paragraph(headers[2], styles["table_header"]),
        Paragraph(headers[3], styles["table_header"])
    ]]

    for action, pad, kb, effect in c_data["table"]:
        table_rows.append([
            Paragraph(f"<b>{action}</b>", styles["table_cell_bold"]),
            Paragraph(pad, styles["table_cell"]),
            Paragraph(kb, styles["table_cell"]),
            Paragraph(effect, styles["table_cell"])
        ])

    ctrl_table = Table(table_rows, colWidths=[105, 120, 110, 195])
    ctrl_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 2.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(ctrl_table)
    story.append(Spacer(1, 3.5))

    story.append(Paragraph("<b>Mecânicas Centrais de Duelo:</b>" if lang == "PT" else "<b>Core Dueling Mechanics:</b>", styles["sec_heading"]))
    for m_title, m_desc in c_data["mechanics"]:
        story.append(Paragraph(f"• <b>{m_title}:</b> {m_desc}", styles["body_text"]))
        story.append(Spacer(1, 1.5))

    story.append(Spacer(1, 2.5))

    # Dois cartões táticos complementares de alta resolução
    tactical_cards = [
        [
            Paragraph(
                "<b>Anatomia do Choque de Lâminas (Blade Clash QTE):</b><br/>"
                "Quando dois ataques de corte simétricos colidem no mesmo frame espacial, o motor paralisa a tela por "
                "600 milissegundos com faíscas cinemáticas. Ambos os combatentes entram em disputa de digitação veloz: "
                "o duelista que registrar a maior frequência de acionamentos no botão primário empurra a arma inimiga, impondo "
                "24 frames de cambaleio forçado (Off-Balance) ao perdedor, deixando-o vulnerável ao corte de misericórdia." if lang == "PT" else
                "<b>Anatomy of the Blade Clash QTE:</b><br/>"
                "When two symmetric slashes connect on the exact same frame, time slows down for 600ms amid dazzling sparks. "
                "Both duelists enter a rapid mash contest: the fighter recording the higher primary attack tap frequency "
                "overpowers the bind, inflicting 24 frames of off-balance stagger upon the loser, leaving them defenseless.",
                styles["body_text"]
            ),
            Paragraph(
                "<b>Invulnerabilidade & Trajetórias Tridimensionais:</b><br/>"
                "O rolamento dedicado [T] confere 12 frames de invulnerabilidade absoluta contra golpes horizontais, "
                "flechas, tiros de pólvora e magias elementais. Contudo, ataques descendentes cravados no piso (como o Pisotão de "
                "Raiden ou a descida Ryuu Tsui-Sen de Kenshi) ignoram os frames de esquiva e atingem combatentes no chão, "
                "punindo severamente evasões em pânico." if lang == "PT" else
                "<b>Invulnerability & 3D Attack Trajectories:</b><br/>"
                "The dedicated roll [T] grants 12 frames of invulnerability against horizontal slashes, "
                "arrows, gunfire, and spells. However, downward strikes plunging into the floor (such as Raiden's stomp "
                "or Kenshi's Ryuu Tsui-Sen dive) ignore roll frames and strike prone targets, severely punishing panic evasions.",
                styles["body_text"]
            )
        ]
    ]

    t_tactical = Table(tactical_cards, colWidths=[260, 265])
    t_tactical.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_tactical)
    story.append(Spacer(1, 3))

    macro_hdr = "DIRETRIZES DE MAESTRIA MARCIAL (INPUTS AVANÇADOS)" if lang == "PT" else "ADVANCED MARTIAL EXECUTION DIRECTIVES"
    macro_bullets = [
        "• <b>Saque em Movimento:</b> Acionar Ataque [E] empurrando o direcional projeta um corte com avanço frontal de 0.85 metros." if lang == "PT" else
        "• <b>Moving Draw:</b> Pressing Attack [E] while tilting the directional stick lunges forward by 0.85 meters.",

        "• <b>Cancelamento Evasivo:</b> O rolamento [T] cancela frames iniciais de corrida e golpes lentos para reposicionamento veloz." if lang == "PT" else
        "• <b>Evasive Cancel:</b> The dedicated roll [T] cancels initial sprint frames and slow startup swings for rapid repositioning.",

        "• <b>Janela de Parry Ativo:</b> A postura de guarda [F] dura 14 frames; falhar o bloqueio no vazio impõe 18 frames de vulnerabilidade." if lang == "PT" else
        "• <b>Active Parry Window:</b> The guard stance [F] lasts 14 frames; whiffing a parry imposes an 18-frame punishable recovery lag.",

        "• <b>Cancelamento de Feint:</b> Tocar Guarda [F] no início do golpe [E] engana a reação do rival, induzindo parries falsos." if lang == "PT" else
        "• <b>Feint Cancellation:</b> Tapping Guard [F] during attack [E] startup feints the strike, baiting defensive whiffs.",

        "• <b>Recuperação de Queda (Tech Roll):</b> Pressionar [T] no exato momento da queda dissipa o impacto e restaura postura instantaneamente." if lang == "PT" else
        "• <b>Tech Roll Recovery:</b> Pressing [T] at the exact instant of knockdown cancels ground lag and immediately restores combat poise."
    ]
    t_macro = Table([[
        [
            Paragraph(f"<b>{macro_hdr}</b>", styles["sec_heading"]),
            Spacer(1, 1.5),
            Paragraph(macro_bullets[0], styles["body_text"]),
            Paragraph(macro_bullets[1], styles["body_text"]),
            Paragraph(macro_bullets[2], styles["body_text"]),
            Paragraph(macro_bullets[3], styles["body_text"]),
            Paragraph(macro_bullets[4], styles["body_text"])
        ]
    ]], colWidths=[530])
    t_macro.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_macro)

    story.append(PageBreak())


def build_modes_and_prelude_page(story, styles, lang="PT"):
    """Página 6: Modos de Jogo & Prelúdio Marcial."""
    m_data = data_pt.MODES_PT if lang == "PT" else data_en.MODES_EN

    title = "MODOS DE COMBATE & PRELÚDIO DO TORNEIO" if lang == "PT" else "COMBAT MODES & TOURNAMENT PRELUDE"
    sub = "A ESCADA DO DESTINO & FILOSOFIA DO COMBATE DIEGÉTICO" if lang == "PT" else "THE LADDER OF DESTINY & DIEGETIC DUEL PHILOSOPHY"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    story.append(Paragraph(f"<b>{m_data['arcade_title']}</b>", styles["sec_heading"]))
    story.append(Paragraph(m_data["arcade_desc"], styles["body_text"]))
    story.append(Spacer(1, 2.5))

    # Tabela estruturada dos 12 Atos do Modo Arcade
    arc_hdrs = ["Ato / Fase", "Adversários & Províncias", "Regras & Condição de Vitória"] if lang == "PT" else ["Act / Stage", "Adversaries & Provinces", "Rules & Victory Condition"]
    arc_rows = [[
        Paragraph(arc_hdrs[0], styles["table_header"]),
        Paragraph(arc_hdrs[1], styles["table_header"]),
        Paragraph(arc_hdrs[2], styles["table_header"])
    ]]
    for stg_title, stg_desc in m_data["arcade_stages"]:
        parts = stg_desc.split(". ", 1)
        adv_p = parts[0]
        rule_p = parts[1] if len(parts) > 1 else "Eliminação direta"
        arc_rows.append([
            Paragraph(f"<b>{stg_title}</b>", styles["table_cell_bold"]),
            Paragraph(adv_p, styles["table_cell"]),
            Paragraph(rule_p, styles["table_cell"])
        ])

    t_arc = Table(arc_rows, colWidths=[120, 205, 205])
    t_arc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(t_arc)
    story.append(Spacer(1, 3))

    story.append(Paragraph(f"<b>{m_data['versus_title']}</b>", styles["sec_heading"]))
    story.append(Paragraph(m_data["versus_desc"], styles["body_text"]))
    story.append(Spacer(1, 3))

    p_title = "OS TRÊS MANDAMENTOS DO COMBATE DIEGÉTICO" if lang == "PT" else "THE THREE COMMANDMENTS OF DIEGETIC COMBAT"
    story.append(Paragraph(f"<b>{p_title}</b>", styles["sec_heading"]))

    three_commandments = [
        ("1. Maai (間合い - Métrica do Espaço)",
         "A arte do espaço milimétrico. Um passo à frente significa corte; um passo em recuo no golpe rival abre a brecha letal." if lang == "PT" else
         "The art of millimetric spatial control. One step forward invites execution; one step back as the foe swings opens the fatal breach."),

        ("2. Mushin (無心 - Mente sem Hesitação)",
         "O estado reflexivo onde os instintos precedem o pensamento. Quem hesita diante do brilho do aço inimigo é sepultado no primeiro segundo." if lang == "PT" else
         "The intuitive state where reflex precedes calculation. Hesitation before the glint of enemy steel seals your burial."),

        ("3. Zanshin (残心 - Vigilância Contínua)",
         "A postura de prontidão mantida após desferir o corte. Jamais relaxe: o oponente pode possuir 3 HP ou contra-ataque derradeiro." if lang == "PT" else
         "Sustained alert awareness held even after landing a hit. Never drop your guard: foes may possess 3 HP or a dying reprisal.")
    ]

    for c_title, c_desc in three_commandments:
        story.append(Paragraph(f"• <b>{c_title}:</b> {c_desc}", styles["body_text"]))
        story.append(Spacer(1, 1.2))

    story.append(Spacer(1, 2.5))

    surv_title = "REGRAS SAGRADAS DO ROUND DECISIVO (SURVIVAL RULES)" if lang == "PT" else "SACRED DUEL SURVIVAL RULES"
    surv_bullets = [
        ("• <b>Letalidade Diegética:</b> Não há barras infladas de vida. O primeiro acerto limpo em contra-ataque ou recuperação decide o duelo.") if lang == "PT" else
        ("• <b>Diegetic Lethality:</b> No inflated health bars. The first clean counter-hit or whiff punish decides the round."),

        ("• <b>Fossos de Queda Mortal:</b> Em arenas como Ilha Ganryu, Telhados de Iga e Dejima, ser arremessado para fora causa morte imediata por queda.") if lang == "PT" else
        ("• <b>Instant Ring-Out Pits:</b> Across arenas like Ganryu Island, Iga Rooftops, and Dejima, being pushed over triggers instant ring-out death."),

        ("• <b>Alquimia e Reagentes de Solo:</b> O solo sob seus pés dita as poções que Hendrika pode sintetizar e as ressonâncias mágicas de Abe no Seimei.") if lang == "PT" else
        ("• <b>Dynamic Soil Alchemy:</b> The terrain beneath your sandals governs the draughts Hendrika can synthesize and Seimei's elemental resonances.")
    ]
    t_surv = Table([[
        [
            Paragraph(f"<b>{surv_title}</b>", styles["sec_heading"]),
            Spacer(1, 1),
            Paragraph(surv_bullets[0], styles["body_text"]),
            Paragraph(surv_bullets[1], styles["body_text"]),
            Paragraph(surv_bullets[2], styles["body_text"])
        ]
    ]], colWidths=[530])
    t_surv.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_surv)

    story.append(Spacer(1, 2.5))
    final_note = (
        "<i>«Nas páginas a seguir (Págs. 07 a 18), cada dossiê apresenta dois guerreiros e duas arenas natais em alta densidade técnica, "
        "com seus atributos físicos, movesets autênticos e dinâmica real de solo.»</i>" if lang == "PT" else
        "<i>«Across the following pages (Pages 07 to 18), each dossier presents two champions and two home arenas in high technical density, "
        "detailing their physical metrics, authentic movesets, and true ground dynamics.»</i>"
    )
    t_note = Table([[Paragraph(f"<font color='#8C1D13'>{final_note}</font>", styles["page_sub"])]], colWidths=[530])
    t_note.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_note)

    story.append(PageBreak())


def build_single_dossier_flowables(f, a, styles, lang="PT"):
    """Constrói o bloco de 1 combatente + 1 arena para compor 2 por página."""
    res = []

    name = f["name_pt"] if lang == "PT" else f["name_en"]
    title = f["title_pt"] if lang == "PT" else f["title_en"]
    faction = f["faction_pt"] if lang == "PT" else f["faction_en"]
    lore = f["lore_pt"] if lang == "PT" else f["lore_en"]
    reach = f["reach_pt"] if lang == "PT" else f["reach_en"]
    style_m = f["style_pt"] if lang == "PT" else f["style_en"]

    a_name = a["name_pt"] if lang == "PT" else a["name_en"]
    a_loc = a["location_pt"] if lang == "PT" else a["location_en"]
    a_hist = a["historical_context_pt"] if lang == "PT" else a["historical_context_en"]
    a_hazards = a["hazards_pt"] if lang == "PT" else a["hazards_en"]
    a_soil = a["soil_alchemy_pt"] if lang == "PT" else a["soil_alchemy_en"]
    a_tactics = a["tactics_pt"] if lang == "PT" else a["tactics_en"]

    # Header do Lutador
    res.append(Paragraph(name, styles["page_header"]))
    res.append(Paragraph(f"{title} &nbsp;|&nbsp; <font color='{COLOR_BORDER_GOLD.hexval()}'><b>{faction}</b></font>", styles["page_sub"]))
    res.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_CRIMSON, spaceAfter=3))

    # Lutador Imagem Proporcional + Stats & Lore
    img_f = get_proportional_img(f["concept_art"], target_w=75)
    hp_val = f["hp"]
    hp_txt = f"<font color='#8C1D13'><b>{hp_val} HP</b></font>" if hp_val > 2 else f"<b>{hp_val} HP</b>"
    
    lbl_vit = "<b>Vitalidade:</b> " if lang == "PT" else "<b>Health:</b> "
    lbl_spd = " &nbsp;|&nbsp; <b>Velocidade:</b> " if lang == "PT" else " &nbsp;|&nbsp; <b>Speed:</b> "
    lbl_rch = "<b>Alcance:</b> " if lang == "PT" else "<b>Reach:</b> "
    lbl_stl = "<b>Estilo:</b> " if lang == "PT" else "<b>Style:</b> "
    lbl_lor = "<b>Lore:</b> " if lang == "PT" else "<b>Lore:</b> "

    stats_p = Paragraph(
        f"{lbl_vit}{hp_txt}{lbl_spd}{f['speed']}<br/>"
        f"{lbl_rch}{reach}<br/>"
        f"{lbl_stl}{style_m}<br/>"
        f"{lbl_lor}{lore}",
        styles["body_text"]
    )

    f_table = Table([[img_f, stats_p]], colWidths=[80, 460])
    f_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    res.append(f_table)
    res.append(Spacer(1, 3))

    # Tabela 2 Ações Reais (Opção 1)
    moves = f["moveset_pt"] if lang == "PT" else f["moveset_en"]
    m_primary = moves[0]
    m_secondary = moves[1]

    th_act = "Ação de Combate" if lang == "PT" else "Combat Action"
    th_pad = "Gamepad"
    th_kb = "Teclado (P1 / P2)" if lang == "PT" else "Keyboard (P1 / P2)"
    th_eff = "Aplicação Tática Real" if lang == "PT" else "Real Tactical Effect"

    lbl_atk = "Ataque: " if lang == "PT" else "Attack: "
    lbl_spc = "Especial: " if lang == "PT" else "Special: "

    m_rows = [
        [Paragraph(th_act, styles["table_header"]), Paragraph(th_pad, styles["table_header"]), Paragraph(th_kb, styles["table_header"]), Paragraph(th_eff, styles["table_header"])],
        [Paragraph(f"<b>{lbl_atk}{m_primary[0]}</b>", styles["table_cell_bold"]), Paragraph(m_primary[1], styles["table_cell"]), Paragraph(m_primary[2], styles["table_cell"]), Paragraph(m_primary[3], styles["table_cell"])],
        [Paragraph(f"<b>{lbl_spc}{m_secondary[0]}</b>", styles["table_cell_bold"]), Paragraph(m_secondary[1], styles["table_cell"]), Paragraph(m_secondary[2], styles["table_cell"]), Paragraph(m_secondary[3], styles["table_cell"])],
    ]
    m_table = Table(m_rows, colWidths=[130, 75, 95, 240])
    m_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 2.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    res.append(m_table)
    res.append(Spacer(1, 3))

    # Dinâmica Tática & Como Vencer
    w_text = f["weapons_pt"] if lang == "PT" else f["weapons_en"]
    def_text = f["how_to_beat_pt"] if lang == "PT" else f["how_to_beat_en"]
    lbl_w = "• <b>Dinâmica de Armas & Plano de Jogo:</b> " if lang == "PT" else "• <b>Weapon Dynamics & Gameplan:</b> "
    lbl_d = "<br/>• <b>Como Vencer (Defesa & Punição):</b> " if lang == "PT" else "<br/>• <b>How to Beat (Defense & Punishment):</b> "

    tact_txt = f"{lbl_w}{w_text}{lbl_d}{def_text}"
    res.append(Paragraph(tact_txt, styles["body_text"]))
    res.append(Spacer(1, 3))

    # Arena Natal
    lbl_arena = "ARENA NATAL: " if lang == "PT" else "HOME ARENA: "
    res.append(Paragraph(f"<b>{lbl_arena}{a_name.upper()}</b> — <font color='{COLOR_MUTED_TEXT.hexval()}'>{a_loc}</font>", styles["sec_heading"]))
    img_a = get_proportional_img(a["concept_art"], target_w=165)

    lbl_hist = "<b>Contexto Histórico:</b> " if lang == "PT" else "<b>Historical Context:</b> "
    lbl_haz = "<b>Perigos & Fossos Reais:</b> " if lang == "PT" else "<b>Real Hazards & Pits:</b> "
    lbl_soil = "<b>Solo & Alquimia:</b> " if lang == "PT" else "<b>Soil & Alchemy:</b> "
    lbl_tact = "<b>Tática Espacial:</b> " if lang == "PT" else "<b>Spatial Tactics:</b> "

    short_hist = a_hist if len(a_hist) <= 175 else a_hist[:172] + "..."

    a_info = [
        Paragraph(f"{lbl_hist}{short_hist}", styles["body_text"]),
        Paragraph(f"{lbl_haz}{a_hazards}", styles["body_text"]),
        Paragraph(f"{lbl_soil}{a_soil}", styles["body_text"]),
        Paragraph(f"{lbl_tact}{a_tactics}", styles["body_text"])
    ]
    a_table = Table([[img_a, a_info]], colWidths=[170, 370])
    a_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    res.append(a_table)
    return res


def build_two_per_page(story, styles, f1, a1, f2, a2, lang="PT"):
    """Monta uma página única contendo 2 combatentes e suas 2 arenas."""
    # Primeiro Combatente + Arena
    story.extend(build_single_dossier_flowables(f1, a1, styles, lang=lang))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.2, color=COLOR_BORDER_GOLD, spaceAfter=6))
    # Segundo Combatente + Arena
    story.extend(build_single_dossier_flowables(f2, a2, styles, lang=lang))
    story.append(PageBreak())


def build_boss_page(story, styles, lang="PT"):
    """Página 19: O Despertar Proibido — O Chefe Final Oni Gashadokuro."""
    b_data = data_pt.BOSS_TEASER_PT if lang == "PT" else data_en.BOSS_TEASER_EN

    story.append(Paragraph(b_data["title"], styles["page_header"]))
    story.append(Paragraph(f"<b>{b_data['name']}</b> — {b_data['subtitle']}", styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    img_p = b_data["concept_art"]
    if os.path.exists(img_p):
        story.append(get_proportional_img(img_p, target_w=530))
        story.append(Spacer(1, 4))

    story.append(Paragraph("<b>A Lenda do Colosso Adormecido:</b>" if lang == "PT" else "<b>Legend of the Slumbering Colossus:</b>", styles["sec_heading"]))
    story.append(Paragraph(b_data["lore"], styles["body_text"]))
    story.append(Spacer(1, 3))

    story.append(Paragraph("<b>As Três Fases do Confronto:</b>" if lang == "PT" else "<b>The Three Combat Phases:</b>", styles["sec_heading"]))
    phases = [
        ("Fase 1: Punho Esmagador & Clava Titânica",
         "O Titã possui hiper-armadura total contra golpes frontais. Seus impactos sísmicos no chão racham a rocha e provocam o desabamento de estalactites afiadas por toda a arena." if lang == "PT" else
         "The Titan boasts complete frontal hyper-armor. Seismic fist slams fracture bedrock, triggering jagged stalactite collapses across the entire battlefield."),

        ("Fase 2: Cortina de Miasma & Névoa Venenosa",
         "Ao perder parte de seu vigor espiritual, o colosso expele jatos de fumaça tóxica e chamas espectrais roxas nas margens da caverna, encurralando o jogador no anel central." if lang == "PT" else
         "Upon losing initial spiritual vigor, the colossus exhales toxic miasma and violet soulfire along cavern perimeters, penning the player into the central circle."),

        ("Fase 3: Queda na Borda & Janela da Gema",
         "Após uma sequência de 3 golpes devastadores, o Titã colapsa em fadiga por 1.8 segundos, descansando o crânio na borda do fosso. Esta é a única oportunidade de desferir o golpe de misericórdia na gema da testa." if lang == "PT" else
         "Following a three-hit cataclysmic sequence, the Titan collapses in exhaustion for 1.8s, resting its skull upon the pit edge. This is your sole opening to deliver the fatal coup de grâce to the forehead gem.")
    ]
    for p_title, p_desc in phases:
        story.append(Paragraph(f"• <b>{p_title}:</b> {p_desc}", styles["body_text"]))
        story.append(Spacer(1, 1.2))

    story.append(Spacer(1, 2.5))
    warn_text = (
        "<b>REGRA DE FERRO DO DUELO FINAL (ROUND ÚNICO DE VIDA OU MORTE):</b><br/>"
        "Não há melhor de 3 contra o Oni Gashadokuro. Um único erro de rolamento ou cálculo de distância resulta em "
        "aniquilação imediata. Mantenha a compostura (Mushin) e ataque apenas quando a cabeça do titã desabar exausta na beirada." if lang == "PT" else
        "<b>IRONCLAD RULE OF THE FINAL CLASH (SINGLE-ROUND SUDDEN DEATH):</b><br/>"
        "There is no Best-of-3 against the Oni Gashadokuro. A single misjudged roll or distance error results in instant obliteration. "
        "Maintain perfect calm (Mushin) and strike solely when the titan's skull rests exhausted upon the precipice."
    )
    t_warn = Table([[Paragraph(f"<font color='#8C1D13'>{warn_text}</font>", styles["body_text"])]], colWidths=[530])
    t_warn.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_CRIMSON),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_warn)
    story.append(Spacer(1, 3))

    # Painel de Estratégias Recomendadas por Arquétipo
    strat_title = "ESTRATÉGIAS RECOMENDADAS POR ARQUÉTIPO MARCIAL" if lang == "PT" else "RECOMMENDED STRATEGIES BY MARTIAL ARCHETYPE"
    strat_rows = [
        ("Espadachins Rápidos & Assassinos (Kenshi, Saitou, Chiyo, Julie, Kasumi):",
         "Utilize o rolamento [T] com precisão milimétrica para passar sob os golpes da clava titânica. Permaneça em meia-distância lateral e use o ataque primário [E] no milissegundo em que o crânio descansar exausto na borda." if lang == "PT" else
         "Utilize dedicated roll [T] to slip beneath seismic club arcs. Hold mid-range diagonally and strike with primary attack [E] the instant the skull rests upon the pit edge."),

        ("Colossos & Combatentes Pesados (Raiden, Benkei, Valerius, Goro):",
         "Sua vitalidade de 3 HP e hiper-armadura permitem absorver estalactites menores. Carregue ataques de quebra de guarda (Guard Crush) para infligir atordoamento crítico na gema da testa na transição da Fase 3." if lang == "PT" else
         "Your 3 HP pool and hyper-armor weather falling rock debris. Charge heavy Guard Crush strikes to inflict devastating impact upon the forehead gem during Phase 3 exhaustion."),

        ("Zoners & Atiradores de Pólvora/Magia (Teppo, Hanzo, Seimei, Tomoe, Hendrika):",
         "Mantenha fogo contínuo à distância segura para acelerar o esgotamento do miasma espiritual da Fase 2. Ao soar o colapso do chefe, avance imediatamente para desferir o golpe corpo a corpo na cabeça vulnerável." if lang == "PT" else
         "Maintain continuous ranged pressure to accelerate Phase 2 miasma depletion. When the titan collapses, sprint in instantly to land the decisive melee cut on the grounded head.")
    ]

    t_strat = Table([[
        [
            Paragraph(f"<b>{strat_title}</b>", styles["sec_heading"]),
            Spacer(1, 1.5),
            Paragraph(f"• <b>{strat_rows[0][0]}</b> {strat_rows[0][1]}", styles["body_text"]),
            Spacer(1, 1),
            Paragraph(f"• <b>{strat_rows[1][0]}</b> {strat_rows[1][1]}", styles["body_text"]),
            Spacer(1, 1),
            Paragraph(f"• <b>{strat_rows[2][0]}</b> {strat_rows[2][1]}", styles["body_text"])
        ]
    ]], colWidths=[530])
    t_strat.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_strat)

    story.append(PageBreak())


def build_appendix_tier_page(story, styles, lang="PT"):
    """Página 20: Tabela Geral de Desempenho (6.624 Simulações)."""
    app = data_pt.APPENDIX_PT if lang == "PT" else data_en.APPENDIX_EN

    story.append(Paragraph(app["title"], styles["page_header"]))
    story.append(Paragraph(app["tier_title"], styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    story.append(Paragraph(app["tier_desc"], styles["body_text"]))
    story.append(Spacer(1, 2.5))

    hdrs = ["Rank", "Lutador", "Arquétipo / Arma Principal", "Vitórias", "Derrotas", "Winrate", "Tier"] if lang == "PT" else ["Rank", "Fighter", "Archetype / Primary Weapon", "Wins", "Losses", "Winrate", "Tier"]
    rows = [[
        Paragraph(hdrs[0], styles["table_header"]),
        Paragraph(hdrs[1], styles["table_header"]),
        Paragraph(hdrs[2], styles["table_header"]),
        Paragraph(hdrs[3], styles["table_header"]),
        Paragraph(hdrs[4], styles["table_header"]),
        Paragraph(hdrs[5], styles["table_header"]),
        Paragraph(hdrs[6], styles["table_header"])
    ]]

    for rk, f_name, arq, w, l, wr, tier in app["tier_table"]:
        t_color = "#8C1D13" if "S" in tier else ("#1B3B54" if "B" in tier else "#4A3B32")
        rows.append([
            Paragraph(f"<b>{rk}</b>", styles["table_cell_bold"]),
            Paragraph(f"<b>{f_name}</b>", styles["table_cell_bold"]),
            Paragraph(arq, styles["table_cell"]),
            Paragraph(w, styles["table_cell"]),
            Paragraph(l, styles["table_cell"]),
            Paragraph(f"<b>{wr}</b>", styles["table_cell_bold"]),
            Paragraph(f"<font color='{t_color}'><b>{tier}</b></font>", styles["table_cell_bold"])
        ])

    tier_table = Table(rows, colWidths=[28, 72, 195, 54, 54, 48, 69])
    tier_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(tier_table)
    story.append(Spacer(1, 4))

    # Painel analítico de equilíbrio de combate e metagame em 4 Tiers
    meta_title = "ANÁLISE DE EQUILÍBRIO & METAGAME DIEGÉTICO" if lang == "PT" else "BALANCE ANALYSIS & DIEGETIC METAGAME"
    meta_p1 = (
        "• <b>Tier S (Winrate > 58% — Controle de Neutro):</b> Seimei, Teppo, Hanzo, Saitou, Hendrika, Joe, Kenshi e Tomoe "
        "dominam a simulação simétrica por acumular vantagens com projéteis e ferramentas de espaçamento antes da aproximação corpo a corpo." if lang == "PT" else
        "• <b>Tier S (Winrate > 58% — Neutral Control):</b> Seimei, Teppo, Hanzo, Saitou, Hendrika, Joe, Kenshi, and Tomoe "
        "lead automated bouts by leveraging projectile zoning and space-denial tools before melee engagement."
    )
    meta_p2 = (
        "• <b>Tier B (Winrate 47%–50% — Versáteis & Anti-Meta):</b> Murasaki, Valerius, Ichi, Musashi, Kasumi e Aoi equilibram contra-ataques "
        "mortais, ferramentas evasivas e letalidade consistente em duelos de média distância." if lang == "PT" else
        "• <b>Tier B (Winrate 47%–50% — Versatile Anti-Meta):</b> Murasaki, Valerius, Ichi, Musashi, Kasumi, and Aoi combine lethal "
        "parry counters, smoke evasion, and solid mid-range combat lethality."
    )
    meta_p3 = (
        "• <b>Tier C & D (Colossos sob Controle Humano):</b> Duelistas como Raiden e Benkei registram menor taxa na IA devido "
        "ao tempo de recuperação de seus ataques. Contudo, nas mãos de um jogador humano experiente, seus 3 HP, hiper-armadura e "
        "golpes Guard Crush convertem qualquer hesitação em aniquilação fatal imediata." if lang == "PT" else
        "• <b>Tier C & D (Heavy Colossi in Human Hands):</b> Heavyweights like Raiden and Benkei record lower automated AI winrates "
        "due to substantial recovery frames. In the hands of skilled human players, their 3 HP life pool, hyper-armor, and Guard Crush strikes "
        "turn a single enemy misstep into instant fatality."
    )

    t_meta = Table([[
        [
            Paragraph(f"<b>{meta_title}</b>", styles["sec_heading"]),
            Spacer(1, 1.5),
            Paragraph(meta_p1, styles["body_text"]),
            Spacer(1, 1),
            Paragraph(meta_p2, styles["body_text"]),
            Spacer(1, 1),
            Paragraph(meta_p3, styles["body_text"])
        ]
    ]], colWidths=[530])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(t_meta)

    story.append(PageBreak())


def build_appendix_priority_page(story, styles, lang="PT"):
    """Página 21: Guia de Prioridades & Precedência Absoluta de Golpes."""
    title = "GUIA DE PRIORIDADES & PRECEDÊNCIA ABSOLUTA" if lang == "PT" else "ABSOLUTE PRECEDENCE & PRIORITY DIRECTIVE"
    sub = "MATEMÁTICA DE CHOQUE DE LÂMINAS & FRAMES DE INICIATIVA" if lang == "PT" else "BLADE CLASH MATHEMATICS & INITIATIVE FRAMES"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    p_intro = (
        "Em Samurai Edge, os ataques são processados em 4 camadas de precedência matemática estrita. Quando dois combatentes "
        "atacam dentro do mesmo ciclo de verificação espacial, o motor do jogo consulta a seguinte ordem de resolução:" if lang == "PT" else
        "In Samurai Edge, attacks are resolved across 4 strict mathematical priority layers. When two combatants swing "
        "within the same spatial verification tick, the engine applies the following resolution order:"
    )
    story.append(Paragraph(p_intro, styles["body_text"]))
    story.append(Spacer(1, 2.5))

    # Tabela visual da matriz de prioridades
    matrix_headers = ["Camada", "Classificação de Impacto", "Exemplos Notáveis", "Resultado da Colisão"] if lang == "PT" else ["Layer", "Impact Classification", "Notable Examples", "Collision Outcome"]
    matrix_data = [
        [
            Paragraph(matrix_headers[0], styles["table_header"]),
            Paragraph(matrix_headers[1], styles["table_header"]),
            Paragraph(matrix_headers[2], styles["table_header"]),
            Paragraph(matrix_headers[3], styles["table_header"])
        ],
        [
            Paragraph("<b>Nível 4</b>" if lang == "PT" else "<b>Tier 4</b>", styles["table_cell_bold"]),
            Paragraph("<b>Precedência Absoluta</b>" if lang == "PT" else "<b>Absolute Precedence</b>", styles["table_cell_bold"]),
            Paragraph("Foice de Murasaki, Estilete de Hendrika" if lang == "PT" else "Murasaki Kusarigama, Hendrika Rapier", styles["table_cell"]),
            Paragraph("Corte garantido. Ignora Choque de Lâminas e interrompe qualquer ataque rival." if lang == "PT" else "Guaranteed sever. Bypasses clashes and interrupts any rival swing.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Nível 3</b>" if lang == "PT" else "<b>Tier 3</b>", styles["table_cell_bold"]),
            Paragraph("<b>Quebra de Guarda (Crush)</b>" if lang == "PT" else "<b>Guard Crush Heavy</b>", styles["table_cell_bold"]),
            Paragraph("Baioneta de Teppo, Kanabo de Benkei, Pisotão" if lang == "PT" else "Teppo Bayonet, Benkei Kanabo, Raiden Stomp", styles["table_cell"]),
            Paragraph("Esmaga defesas de Parry ativo, aplicando Stun severo no defensor." if lang == "PT" else "Shatters active parry stances, applying heavy daze and stun.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Nível 2</b>" if lang == "PT" else "<b>Tier 2</b>", styles["table_cell_bold"]),
            Paragraph("<b>Choque Simétrico (Clash)</b>" if lang == "PT" else "<b>Symmetric Clash</b>", styles["table_cell_bold"]),
            Paragraph("Katanas de Kenshi, Musashi, Saitou, Chiyo, Julie" if lang == "PT" else "Katanas of Kenshi, Musashi, Saitou, Chiyo, Julie", styles["table_cell"]),
            Paragraph("Congela o tempo por 600ms e inicia o micro-evento QTE de digitação veloz." if lang == "PT" else "Freezes time for 600ms and triggers the rapid-mash QTE micro-contest.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Nível 1</b>" if lang == "PT" else "<b>Tier 1</b>", styles["table_cell_bold"]),
            Paragraph("<b>Projéteis & Ataques Leves</b>" if lang == "PT" else "<b>Projectiles & Light</b>", styles["table_cell_bold"]),
            Paragraph("Shurikens, Kunais de arremesso, socos desarmados" if lang == "PT" else "Shurikens, thrown Kunai, unarmed jabs", styles["table_cell"]),
            Paragraph("Defletidos instantaneamente por qualquer postura de guarda ou corte de espada." if lang == "PT" else "Deflected effortlessly by any active parry stance or sword cut.", styles["table_cell"])
        ]
    ]

    p_table = Table(matrix_data, colWidths=[48, 125, 155, 202])
    p_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 3))

    # Seção II: Anatomia Tridimensional dos Hitboxes (Engine Isométrica 3D)
    geo_title = "ANATOMIA TRIDIMENSIONAL DOS HITBOXES (ENGINE 3D)" if lang == "PT" else "3D HITBOX ANATOMY & ISOMETRIC COLLISION ENGINE"
    geo_p1 = (
        "• <b>Voxel Boxes Orientados (mk.obox):</b> Caixas de colisão de lâminas e membros giram no espaço 3D tridimensional de acordo "
        "com vetores de avanço (rx, ry) e elevação (z), garantindo detecção precisa sem distorções em ângulos de 360 graus." if lang == "PT" else
        "• <b>Oriented Voxel Boxes (mk.obox):</b> Weapon and limb collision volumes rotate dynamically through 3D space according to "
        "advance vectors (rx, ry) and elevation (z), ensuring flawless mathematical verification across full 360-degree angles."
    )
    geo_p2 = (
        "• <b>Back-Face Culling & Winding Order:</b> Todos os polígonos de corte possuem vetores normais apontando estritamente para fora, "
        "eliminando o risco de golpes se tornarem intangíveis ou invisíveis quando vistos em perfil lateral (90° / 270°)." if lang == "PT" else
        "• <b>Back-Face Culling & Winding Order:</b> All collision face sets point strictly outward, eliminating any risk of weapon "
        "swings becoming intangible or culled when viewed from profile camera angles (90° / 270°)."
    )

    t_geo = Table([[
        [
            Paragraph(f"<b>{geo_title}</b>", styles["sec_heading"]),
            Spacer(1, 1),
            Paragraph(geo_p1, styles["body_text"]),
            Spacer(1, 1),
            Paragraph(geo_p2, styles["body_text"])
        ]
    ]], colWidths=[530])
    t_geo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_geo)
    story.append(Spacer(1, 3))

    # Seção III: Tabela de Frames de Recuperação (Whiff Lag)
    whiff_hdrs = ["Categoria de Arma", "Startup", "Frames Ativos", "Recuperação (Whiff)", "Vulnerabilidade Tática"] if lang == "PT" else ["Weapon Class", "Startup", "Active Frames", "Whiff Recovery", "Tactical Exposure"]
    whiff_rows = [
        [
            Paragraph(whiff_hdrs[0], styles["table_header"]),
            Paragraph(whiff_hdrs[1], styles["table_header"]),
            Paragraph(whiff_hdrs[2], styles["table_header"]),
            Paragraph(whiff_hdrs[3], styles["table_header"]),
            Paragraph(whiff_hdrs[4], styles["table_header"])
        ],
        [
            Paragraph("<b>Adagas & Kodachis</b>" if lang == "PT" else "<b>Daggers & Kodachis</b>", styles["table_cell_bold"]),
            Paragraph("0.08s (5f)", styles["table_cell"]),
            Paragraph("0.06s (4f)", styles["table_cell"]),
            Paragraph("0.12s (7f)", styles["table_cell_bold"]),
            Paragraph("Risco Baixo. Recupera a guarda quase instantaneamente." if lang == "PT" else "Low Risk. Rapid guard recovery denies whiff punishes.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Katanas & Espadas Médias</b>" if lang == "PT" else "<b>Katanas & Medium Blades</b>", styles["table_cell_bold"]),
            Paragraph("0.12s (7f)", styles["table_cell"]),
            Paragraph("0.08s (5f)", styles["table_cell"]),
            Paragraph("0.20s (12f)", styles["table_cell_bold"]),
            Paragraph("Risco Moderado. Vulnerável a estocadas se errar o vazio." if lang == "PT" else "Moderate. Punishable by forward lunges upon whiffing.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Bastões Bo & Naginatas</b>" if lang == "PT" else "<b>Bo Staffs & Naginatas</b>", styles["table_cell_bold"]),
            Paragraph("0.16s (10f)", styles["table_cell"]),
            Paragraph("0.12s (7f)", styles["table_cell"]),
            Paragraph("0.28s (17f)", styles["table_cell_bold"]),
            Paragraph("Risco Elevado. Esquiva lateral garante contra-golpe limpo." if lang == "PT" else "High Risk. Sidestep roll guarantees clean counter-decapitation.", styles["table_cell"])
        ],
        [
            Paragraph("<b>Armas Colossais (Kanabo)</b>" if lang == "PT" else "<b>Colossal Kanabo / Clubs</b>", styles["table_cell_bold"]),
            Paragraph("0.24s (14f)", styles["table_cell"]),
            Paragraph("0.14s (8f)", styles["table_cell"]),
            Paragraph("0.42s (25f)", styles["table_cell_bold"]),
            Paragraph("Risco Crítico. Recuperação longa com exposição total a punição." if lang == "PT" else "Critical Risk. Heavy ground lag invites fatal retribution.", styles["table_cell"])
        ]
    ]

    t_whiff = Table(whiff_rows, colWidths=[120, 65, 75, 95, 175])
    t_whiff.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(t_whiff)
    story.append(Spacer(1, 3))

    # Seção IV: Mecânicas Avançadas de Choque e Punição
    adv_title = "MECÂNICAS AVANÇADAS DE CHOQUE, PUNIÇÃO & CONTROLE ESPACIAL" if lang == "PT" else "ADVANCED CLASH, PUNISHMENT & SPATIAL CONTROL"
    adv_points = [
        ("Resolução do Choque de Lâminas (Blade Clash QTE)",
         "O duelista derrotado na disputa de digitação veloz sofre 24 frames de cambaleio forçado (Off-Balance), "
         "ficando totalmente exposto ao golpe final de misericórdia sem possibilidade de esquiva ou bloqueio." if lang == "PT" else
         "The duelist overpowered in the rapid-mash contest suffers 24 frames of off-balance stagger, "
         "remaining completely defenseless against a decisive follow-up execution."),

        ("A Regra de Ouro do Rolamento Evasivo",
         "O rolamento evasivo dedicado [T] concede 12 frames de invulnerabilidade total a ataques horizontais, flechas e tiros de pólvora. "
         "Contudo, ataques cravados de topo para baixo punem o rolamento no chão, desferindo dano pleno." if lang == "PT" else
         "The dedicated dodge roll [T] confers 12 frames of invulnerability to horizontal slashes and projectiles. However, "
         "downward-plunging strikes track prone bodies, punishing panic rolls mercilessly."),

        ("Janelas de Recuperação & Punição Fatal (Whiff Punish)",
         "Armas longas e pesadas possuem janelas de recuperação entre 0.20s e 0.42s. Um passo em recuo (Back-Step) "
         "seguido de estocada imediata pune com decapitação limpa qualquer golpe que erre o alvo no vazio." if lang == "PT" else
         "Massive weapons carry vulnerable recovery windows between 0.20s and 0.42s. Back-stepping and lunging "
         "immediately punishes any strike that whiffs in the air with clean decapitation.")
    ]

    t_adv = Table([[
        [
            Paragraph(f"<b>{adv_title}</b>", styles["sec_heading"]),
            Spacer(1, 1),
            Paragraph(f"• <b>{adv_points[0][0]}:</b> {adv_points[0][1]}", styles["body_text"]),
            Paragraph(f"• <b>{adv_points[1][0]}:</b> {adv_points[1][1]}", styles["body_text"]),
            Paragraph(f"• <b>{adv_points[2][0]}:</b> {adv_points[2][1]}", styles["body_text"]),
        ]
    ]], colWidths=[530])
    t_adv.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_adv)
    story.append(Spacer(1, 2.5))

    p_maxim = (
        "<i>«No caminho da espada, o aço não mente: quem calcula os frames de iniciativa domina o destino do combate; "
        "quem ataca no vazio entrega a própria cabeça.»</i>" if lang == "PT" else
        "<i>«On the path of the blade, steel tells no falsehood: he who calculates initiative frames commands fate; "
        "he who swings into the empty air forfeits his own skull.»</i>"
    )
    t_max = Table([[Paragraph(f"<font color='#8C1D13'><b>{p_maxim}</b></font>", styles["page_sub"])]], colWidths=[530])
    t_max.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_max)

    story.append(PageBreak())


def build_appendix_soil_page(story, styles, lang="PT"):
    """Página 22: Tabela de Reagentes de Solo Alquímicos."""
    app = data_pt.APPENDIX_PT if lang == "PT" else data_en.APPENDIX_EN

    story.append(Paragraph(app["soil_table_title"], styles["page_header"]))
    sub = "GUIA DE REAGENTES NATURAIS & ELEMENTOS DO RONDEL" if lang == "PT" else "NATURAL REAGENTS & RONDEL ELEMENTS DIRECTIVE"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    desc_pt = (
        "Hendrika sintetiza poções alquímicas em tempo real colhendo minerais e ervas do solo da arena. "
        "A tabela abaixo detalha as propriedades de cada bioma e seus benefícios exclusivos para poções e feitiços de Onmyodo:"
    )
    desc_en = (
        "Hendrika synthesizes combat flasks in real time by gathering minerals and herbs from the arena floor. "
        "The table below details biome properties and unique benefits conferred upon alchemical brews and Onmyodo spells:"
    )
    story.append(Paragraph(desc_pt if lang == "PT" else desc_en, styles["body_text"]))
    story.append(Spacer(1, 2.5))

    hdrs = ["Bioma / Arenas", "Reagentes Coletáveis", "Poções Sintetizadas", "Efeito Ambiental"] if lang == "PT" else ["Biome / Arenas", "Harvestable Reagents", "Synthesized Draughts", "Environmental Perk"]
    rows = [[
        Paragraph(hdrs[0], styles["table_header"]),
        Paragraph(hdrs[1], styles["table_header"]),
        Paragraph(hdrs[2], styles["table_header"]),
        Paragraph(hdrs[3], styles["table_header"])
    ]]

    for bio, reag, pot, eff in app["soil_table"]:
        rows.append([
            Paragraph(f"<b>{bio}</b>", styles["table_cell_bold"]),
            Paragraph(reag, styles["table_cell"]),
            Paragraph(pot, styles["table_cell"]),
            Paragraph(eff, styles["table_cell"])
        ])

    s_table = Table(rows, colWidths=[120, 140, 140, 130])
    s_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 2.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.0),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 3))

    # Catálogo detalhado de poções de Hendrika e Elementos de Seimei
    col_pt_hendrika = [
        Paragraph("<b>Catálogo de Poções de Hendrika:</b>", styles["sec_heading"]),
        Spacer(1, 1),
        Paragraph("• <b>Poção Ácida:</b> Enxofre + Ácido. Estocada corrosiva que destrói posturas de Parry (Guard Crush).", styles["body_text"]),
        Paragraph("• <b>Fogo Alquímico:</b> Salitre + Pólvora. Frasco incendiário com onda de choque e repulsão de área.", styles["body_text"]),
        Paragraph("• <b>Éter Soporífero:</b> Raízes + Resina. Poça tranquilizante que drena vigor e anula corridas do rival.", styles["body_text"]),
        Paragraph("• <b>Salitre Criogênico:</b> Geada que desacelera os frames de recuperação de golpes adversários em 40%.", styles["body_text"]),
        Paragraph("• <b>Miasma Confuso:</b> Névoa de fungos que desorienta os comandos de aproximação temporariamente.", styles["body_text"])
    ]
    col_pt_seimei = [
        Paragraph("<b>Cinco Elementos de Seimei (Onmyodo):</b>", styles["sec_heading"]),
        Spacer(1, 1),
        Paragraph("• <b>Madeira (Wood):</b> Raízes aprisionadoras e curvatura teleguiada de talismãs nos bosques.", styles["body_text"]),
        Paragraph("• <b>Fogo (Fire):</b> Labaredas em leque e dano contínuo acelerado nas ruas de Kyoto em Chamas.", styles["body_text"]),
        Paragraph("• <b>Terra (Earth):</b> Barreiras rochosas de estalactite e muralhas protetoras nos arrozais de Asuka.", styles["body_text"]),
        Paragraph("• <b>Metal (Metal):</b> Deflexão passiva e lâminas de talismã afiadas na corte imperial e Dejima.", styles["body_text"]),
        Paragraph("• <b>Água (Water):</b> Névoas ofuscantes e ondas de impacto cinético na praia da Ilha Ganryu.", styles["body_text"])
    ]

    col_en_hendrika = [
        Paragraph("<b>Hendrika's Combat Flask Catalog:</b>", styles["sec_heading"]),
        Spacer(1, 1),
        Paragraph("• <b>Acid Draught:</b> Sulfur + Acid. Corrosive rapier lunge that shatters parry stances (Guard Crush).", styles["body_text"]),
        Paragraph("• <b>Alchemical Fire:</b> Saltpeter + Powder. Thrown concoction creating blast knockback and burn ticks.", styles["body_text"]),
        Paragraph("• <b>Soporific Ether:</b> Roots + Resin. Tranquilizer puddle sapping stamina and preventing sprints.", styles["body_text"]),
        Paragraph("• <b>Cryogenic Saltpeter:</b> Freezing frost cloud delaying enemy swing recovery frames by 40%.", styles["body_text"]),
        Paragraph("• <b>Confusion Miasma:</b> Fungal spores temporarily reversing opponent directional inputs.", styles["body_text"])
    ]
    col_en_seimei = [
        Paragraph("<b>Seimei's Five Elements (Onmyodo):</b>", styles["sec_heading"]),
        Spacer(1, 1),
        Paragraph("• <b>Wood:</b> Entangling root traps and amplified homing curvature across forest grounds.", styles["body_text"]),
        Paragraph("• <b>Fire:</b> Fan-shaped firewalls and rapid ticking burn damage on burning Kyoto alleys.", styles["body_text"]),
        Paragraph("• <b>Earth:</b> Stalagmite barricades and shockwave absorption across Asuka paddies.", styles["body_text"]),
        Paragraph("• <b>Metal:</b> Passive projectile deflection and razor talismans at Dejima and the court.", styles["body_text"]),
        Paragraph("• <b>Water:</b> Blinding fog screens and high-pressure hydraulic waves on Ganryu shorelines.", styles["body_text"])
    ]

    two_cols = Table([
        [col_pt_hendrika if lang == "PT" else col_en_hendrika,
         col_pt_seimei if lang == "PT" else col_en_seimei]
    ], colWidths=[260, 265])
    two_cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(two_cols)
    story.append(Spacer(1, 3))

    # Seção III: Diretrizes Táticas de Coleta & Ciclo de Transmutação
    trans_title = "DIRETRIZES TÁTICAS DE COLETA & CICLO DO RONDEL PENTAGRAMA" if lang == "PT" else "TACTICAL HARVEST & PENTAGRAM RONDEL CYCLE DIRECTIVE"
    trans_bullets = [
        "• <b>Capacidade do Alforje & Coleta Neutra:</b> Hendrika carrega até 3 frascos simultaneamente; coletar minerais e ervas em postura neutra requer 0.45s de imobilidade. Golpes sofridos durante a coleta interrompem a síntese." if lang == "PT" else
        "• <b>Satchel Capacity & Neutral Gathering:</b> Hendrika holds up to 3 synthesized draughts; harvesting ground reagents in neutral stance requires 0.45s of stillness. Enemy hits during gathering cancel synthesis.",

        "• <b>Ciclo Cosmoteórico do Onmyodo:</b> Madeira alimenta Fogo; Fogo gera Terra; Terra produz Metal; Metal atrai Água; Água nutre Madeira. Alternar magias no ciclo correto reduz o custo de vigor espiritual em 25%." if lang == "PT" else
        "• <b>Onmyodo Pentagram Resonance:</b> Wood feeds Fire; Fire creates Earth; Earth yields Metal; Metal attracts Water; Water nourishes Wood. Casting spells in cycle reduces stamina cost by 25%.",

        "• <b>Ressonância do Solo:</b> Lutar sobre biomas congruentes amplifica a velocidade de disparo e o raio de dispersão elemental de Seimei e Hendrika." if lang == "PT" else
        "• <b>Soil Affinity Boost:</b> Engaging on matching terrain biomes amplifies projectile velocity and elemental dispersal radius."
    ]

    t_trans = Table([[
        [
            Paragraph(f"<b>{trans_title}</b>", styles["sec_heading"]),
            Spacer(1, 1),
            Paragraph(trans_bullets[0], styles["body_text"]),
            Paragraph(trans_bullets[1], styles["body_text"]),
            Paragraph(trans_bullets[2], styles["body_text"])
        ]
    ]], colWidths=[530])
    t_trans.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_trans)
    story.append(Spacer(1, 2.5))

    soil_motto = (
        "<i>«A terra sob seus pés não é mero chão: é o laboratório vivo e o templo ancestral de onde brotam o veneno da morte e o elixir da vitória.»</i>" if lang == "PT" else
        "<i>«The earth beneath your sandals is no ordinary soil: it is the living crucible and ancestral shrine whence spring both lethal venom and the elixir of triumph.»</i>"
    )
    t_sm = Table([[Paragraph(f"<font color='#8C1D13'><b>{soil_motto}</b></font>", styles["page_sub"])]], colWidths=[530])
    t_sm.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_sm)

    story.append(PageBreak())


def build_appendix_glossary_page(story, styles, lang="PT"):
    """Página 23: Glossário Marcial & Filosofia do Bushido."""
    title = "GLOSSÁRIO MARCIAL & TERMOS DO COMBATE SAMURAI" if lang == "PT" else "MARTIAL GLOSSARY & SAMURAI COMBAT TERMS"
    sub = "CONCEITOS HISTÓRICOS & DISCIPLINA DO AÇO NO BAKUMATSU" if lang == "PT" else "HISTORICAL CONCEPTS & DISCIPLINE OF BAKUMATSU STEEL"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=4))

    terms_part1_pt = [
        ("Iaijutsu (居合術)", "A arte milenar de desembainhar a espada e cortar no mesmo movimento fluido e instantâneo, mortalmente aperfeiçoada por Kenshi."),
        ("Noto (納刀)", "O ato cerimonial de limpar e embainhar a katana após o corte. No jogo, é a janela de recuperação onde o contra-ataque é fatal."),
        ("Maai (間合い)", "A distância de combate entre dois oponentes. Engloba o espaço físico e o tempo exato para cruzar a distância de ataque."),
        ("Mushin (無心)", "'Mente sem mente'. Estado meditativo de foco absoluto onde o guerreiro age por puro reflexo intuitivo sem hesitação."),
        ("Zanshin (残心)", "'Mente restante'. A vigilância serena mantida após desferir o corte para não ser surpreendido por contra-ataques."),
        ("Katsujinken (活人剣)", "A espada que preserva a vida. Filosofia dos Protetores do Povo que empunham o aço para defender inocentes contra tiranos."),
        ("Setsuninto (殺人刀)", "A espada que ceifa vidas. A doutrina de assassinos impiedosos que veem a lâmina apenas como ferramenta de massacre e ambição."),
        ("Sen-no-sen (先の先)", "A iniciativa absoluta: perceber a intenção hostil do adversário e cortar no momento exato em que ele inicia sua investida."),
        ("Go-no-sen (後の先)", "O contra-golpe reativo: permitir que o rival ataque no vazio e desferir o corte fatal durante sua recuperação vulnerável."),
        ("Fudoshin (不動心)", "'Mente inabalável'. Serenidade imperturbável diante do perigo mortal ou de provocações do adversário."),
        ("Shisei (姿勢)", "Postura física e alinhamento do centro de gravidade, permitindo transições ágeis entre corrida, rolamento e estocada."),
        ("Kiai (気合)", "A projeção concentrada da energia espiritual e da respiração no momento do corte para maximizar a força de impacto.")
    ]
    terms_part1_en = [
        ("Iaijutsu (居合術)", "The classical martial art of drawing the sword and cutting in a single continuous motion, mastered to perfection by Kenshi."),
        ("Noto (納刀)", "The ceremonial act of sheathing the blade following a slash. In-game, this represents Kenshi's vulnerable whiff recovery window."),
        ("Maai (間合い)", "The spatial combat engagement distance between two duelists. Encompasses both physical reach and the time required to strike."),
        ("Mushin (無心)", "'Mind without mind'. A state of pure spontaneous focus where the martial artist acts upon instinct without conscious pause."),
        ("Zanshin (残心)", "'Remaining mind'. Sustained alert awareness maintained following a strike to deny any counter-offensive surprises."),
        ("Katsujinken (活人剣)", "The life-giving sword. The moral doctrine of the Protectors of the People who wield steel to shield innocents from tyrants."),
        ("Setsuninto (殺人刀)", "The life-taking sword. The doctrine of merciless killers who view the blade purely as an instrument of slaughter and dominance."),
        ("Sen-no-sen (先の先)", "Seizing absolute initiative: sensing hostile intent and cutting at the precise split-second the adversary commits to their advance."),
        ("Go-no-sen (後の先)", "Reactive counter-strike: baiting an enemy into whiffing in the air, then executing them during their recovery lag."),
        ("Fudoshin (不動心)", "'Unshakable mind'. Imperturbable serenity in the face of imminent death or psychological provocations."),
        ("Shisei (姿勢)", "Physical posture and balance of one's center of gravity, facilitating seamless transitions between sprints, rolls, and strikes."),
        ("Kiai (気合)", "The concentrated projection of spiritual energy and breath upon the point of impact to maximize cutting force.")
    ]

    col1_items = [Paragraph("<b>I. Filosofia da Lâmina & Conduta Marcial:</b>" if lang == "PT" else "<b>I. Philosophy of the Blade & Martial Conduct:</b>", styles["sec_heading"]), Spacer(1, 1)]
    terms_1 = terms_part1_pt if lang == "PT" else terms_part1_en
    for term, defn in terms_1:
        col1_items.append(Paragraph(f"• <b>{term}:</b> {defn}", styles["body_text"]))
        col1_items.append(Spacer(1, 1))

    t_gloss1 = Table([[col1_items]], colWidths=[530])
    t_gloss1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_gloss1)
    story.append(Spacer(1, 2.5))

    terms_part2_pt = [
        ("Zanzou (残像)", "Pós-imagem visual deixada no ar por movimentos em velocidade sobre-humana, como o Shukuchi Dash de Kenshi."),
        ("Kodachi (小太刀)", "Espada curta japonesa com lâmina entre 50 e 60 cm. Empunhada em pares por Chiyo para cortes velozes e deflexão."),
        ("Kanabo (金砕棒)", "Clava de guerra octogonal de madeira reforçada com cravos de ferro fundido, empunhada com força esmagadora por Benkei."),
        ("Tsuppari (突っ張り)", "Série de palmadas rápidas com a mão aberta usadas pelos lutadores de Sumô como Raiden para desestabilizar rivais."),
        ("Rangaku (蘭学)", "'Estudos Holandeses'. O corpo de conhecimento científico, médico e químico ocidental que Hendrika pesquisa em Dejima."),
        ("Onmyodo (陰陽道)", "Cosmologia tradicional dos cinco elementos (Madeira, Fogo, Terra, Metal, Água) dominada por Abe no Seimei."),
        ("Gashadokuro (餓者髑髏)", "Titã colossal esquelético nascido do rancor acumulado de milhares de guerreiros mortos sem sepultura em guerras antigas."),
        ("Sakoku (鎖国)", "O período de dois séculos e meio de isolamento estrito das fronteiras do Japão feudal rompido pelo início do Bakumatsu."),
        ("Tanegashima (種子島)", "Arcabuz clássico de mecha introduzido por mercadores portugueses em 1543, aperfeiçoado pelo atirador Teppo."),
        ("Shikomizue (仕込み杖)", "Espada oculta camuflada no interior de uma bengala de madeira inofensiva, empunhada com maestria por Ichi."),
        ("Shimenawa (注連縄)", "Corda sagrada de palha de arroz trançada usada em templos e dohyos para delimitar e consagrar espaços rituais."),
        ("Bokken (木剣)", "Espada de treino esculpida em carvalho maciço japonês, utilizada para forjar a mente e os reflexos de espadachins.")
    ]
    terms_part2_en = [
        ("Zanzou (残像)", "Visual afterimage left behind by hypersonic martial displacement, seen in Kenshi's Shukuchi Dash and Kasumi's steps."),
        ("Kodachi (小太刀)", "Japanese short sword with a blade length between 50 and 60 cm. Dual-wielded by Chiyo for rapid slashes and deflections."),
        ("Kanabo (金砕棒)", "Heavy octagonal war club studded with iron spikes, wielded with crushing momentum by the warrior monk Benkei."),
        ("Tsuppari (突っ張り)", "Rapid open-palm thrusts employed by Sumo rikishi like Raiden to break guard stances and drive opponents out of the ring."),
        ("Rangaku (蘭学)", "'Dutch Learning'. The body of Western scientific, alchemical, and medical treatises studied clandestinely by Hendrika."),
        ("Onmyodo (陰陽道)", "Traditional Japanese esoteric cosmology based upon the five elemental phases wielded by Abe no Seimei."),
        ("Gashadokuro (餓者髑髏)", "Colossal skeletal titan forged from the collective malice of thousands of warriors abandoned without grave in ancient wars."),
        ("Sakoku (鎖国)", "The two-and-a-half centuries of strict maritime isolation imposed by the Shogunate, shattered by the dawn of the Bakumatsu."),
        ("Tanegashima (種子島)", "Classical matchlock arquebus introduced to Japan in 1543, mastered with deadly precision by marksman Teppo."),
        ("Shikomizue (仕込み杖)", "Concealed blade disguised within an unassuming wooden walking stick, wielded with deadly speed by blind master Ichi."),
        ("Shimenawa (注連縄)", "Sacred braided rice-straw cord hung across Shinto shrines and sumo dohyos to ward off evil spirits and purify holy ground."),
        ("Bokken (木剣)", "Solid oak practice katana utilized in classical dojos to temper martial discipline and reflex without lethal bloodshed.")
    ]

    col2_items = [Paragraph("<b>II. Armas Tradicionais, Táticas & Folclore:</b>" if lang == "PT" else "<b>II. Traditional Weapons, Tactics & Folklore:</b>", styles["sec_heading"]), Spacer(1, 1)]
    terms_2 = terms_part2_pt if lang == "PT" else terms_part2_en
    for term, defn in terms_2:
        col2_items.append(Paragraph(f"• <b>{term}:</b> {defn}", styles["body_text"]))
        col2_items.append(Spacer(1, 1))

    t_gloss2 = Table([[col2_items]], colWidths=[530])
    t_gloss2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_gloss2)
    story.append(Spacer(1, 2.5))

    # Seção III: Três Virtudes Cardeais do Bushido
    virt_title = "III. AS TRÊS VIRTUDES CARDEAIS DO DUELISTA DIEGÉTICO" if lang == "PT" else "III. THREE CARDINAL VIRTUES OF THE DIEGETIC DUELIST"
    virt_bullets = [
        "• <b>Giri (義理 - Dever & Respeito):</b> Reverência incondicional à lâmina do adversário; cada combate é um diálogo sagrado de honra e perícia." if lang == "PT" else
        "• <b>Giri (Duty & Honor):</b> Unconditional reverence toward the adversary's blade; every encounter is a sacred dialogue of poise and skill.",

        "• <b>Meiyo (名誉 - Glória sem Covardia):</b> Permanecer resoluto no raio de combate da arena, sem evasões desonrosas ou recuos infinitos." if lang == "PT" else
        "• <b>Meiyo (Unyielding Poise):</b> Remaining resolute within engagement range, rejecting dishonorable panic retreats or infinite evasions.",

        "• <b>Makoto (誠 - Sinceridade no Aço):</b> Desferir cada golpe com a convicção de que não há retorno: a lâmina expressa a verdade da alma." if lang == "PT" else
        "• <b>Makoto (Absolute Truth):</b> Executing every cut with irrevocable commitment: the drawn edge manifests the warrior's spirit."
    ]

    t_virt = Table([[
        [
            Paragraph(f"<b>{virt_title}</b>", styles["sec_heading"]),
            Spacer(1, 1),
            Paragraph(virt_bullets[0], styles["body_text"]),
            Paragraph(virt_bullets[1], styles["body_text"]),
            Paragraph(virt_bullets[2], styles["body_text"])
        ]
    ]], colWidths=[530])
    t_virt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_virt)
    story.append(Spacer(1, 2))

    g_motto = (
        "<i>«Aquele que compreende as palavras antigas compreende a lâmina. O aço é apenas a extensão da vontade; "
        "quando a mente é pura, o corte é invencível.»</i>" if lang == "PT" else
        "<i>«He who grasps the ancient words grasps the blade itself. Steel is merely an extension of will; "
        "when the mind is pure, the strike is invincible.»</i>"
    )
    t_gm = Table([[Paragraph(f"<font color='#8C1D13'><b>{g_motto}</b></font>", styles["page_sub"])]], colWidths=[530])
    t_gm.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_gm)

    story.append(PageBreak())


def build_back_cover_page(story, styles, lang="PT"):
    """Página 24: Contra-capa cerimonial e créditos de encerramento."""
    app = data_pt.APPENDIX_PT if lang == "PT" else data_en.APPENDIX_EN

    story.append(Spacer(1, 4))
    title = "SAMURAI EDGE: BAKUMATSU"
    sub = "幕末の血闘 — FICHA TÉCNICA & CRÉDITOS DA PRODUÇÃO" if lang == "PT" else "BAKUMATSU COMBAT — TECHNICAL COLOPHON & CREDITS"

    story.append(Paragraph(title, styles["title_cover"]))
    story.append(Paragraph(sub, styles["subtitle_cover"]))
    story.append(HRFlowable(width="80%", thickness=1.5, color=COLOR_CRIMSON, spaceAfter=6))

    logo_path = "assets/concepts/sumie_title_logo_concept.jpg"
    if os.path.exists(logo_path):
        story.append(get_proportional_img(logo_path, target_w=390))
        story.append(Spacer(1, 7))

    story.append(Paragraph(f"<b>{app['credits_title']}</b>", styles["sec_heading"]))
    story.append(Spacer(1, 2))

    # Tabela com créditos e toolset atualizados
    credits_rows = [
        ("Game Designer, Songwriter, Artist", "Colletes"),
        ("Toolset de Desenvolvimento" if lang == "PT" else "Development Toolset", "Gemini / Antigravity, Suno, Google Flow"),
        ("Dedicatória" if lang == "PT" else "Dedication", "À Lorena. Sempre à Lorena, que me apoia nas minhas loucuras." if lang == "PT" else "To Lorena. Always to Lorena, who supports me in my madness.")
    ]
    t_credits_data = []
    for role, name in credits_rows:
        t_credits_data.append([
            Paragraph(f"<b>{role}:</b>", styles["body_text"]),
            Paragraph(name, styles["body_text"])
        ])
    t_cred = Table(t_credits_data, colWidths=[185, 345])
    t_cred.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_cred)
    story.append(Spacer(1, 5))

    # Painel técnico da engine e especificações de reprodução
    tech_hdr = "ESPECIFICAÇÕES TÉCNICAS DA ENGINE" if lang == "PT" else "TECHNICAL ENGINE SPECIFICATIONS"
    tech_bullets = [
        "• <b>Taxa de Quadros & Resolução:</b> 60 FPS fixos a 1920x1080 Full HD nativo com renderização isométrica diegética." if lang == "PT" else
        "• <b>Framerate & Resolution:</b> Rock-solid 60 FPS at native 1920x1080 Full HD featuring diegetic isometric projection.",

        "• <b>Arquitetura Visual 3D:</b> Modelagem Low-Poly facetada inspirada na era de ouro do PS1 (Tekken 2/3), sem adesivos planos 2D." if lang == "PT" else
        "• <b>3D Visual Architecture:</b> Low-Poly faceted geometry inspired by the PS1 golden era (Tekken 2/3), strictly free of flat 2D decals.",

        "• <b>Simulação de Choque Vetorial:</b> Detecção tridimensional de corte com caixas de colisão orientadas (mk.obox) em 360°." if lang == "PT" else
        "• <b>Vector Collision Simulation:</b> True 3D weapon blade detection via dynamically oriented voxel bounding boxes (mk.obox).",

        "• <b>Paisagens Sonoras Acústicas:</b> Instrumentação tradicional folclórica (taiko, shakuhachi, shamisen, biwa e koto) sem vocais." if lang == "PT" else
        "• <b>Acoustic Folk Soundscapes:</b> Authentic traditional instrumentation (taiko, shakuhachi, shamisen, biwa, and koto) without vocals."
    ]

    t_tech = Table([[
        [
            Paragraph(f"<b>{tech_hdr}</b>", styles["sec_heading"]),
            Spacer(1, 1.2),
            Paragraph(tech_bullets[0], styles["body_text"]),
            Paragraph(tech_bullets[1], styles["body_text"]),
            Paragraph(tech_bullets[2], styles["body_text"]),
            Paragraph(tech_bullets[3], styles["body_text"])
        ]
    ]], colWidths=[530])
    t_tech.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 5))

    # Dedicatória da produção
    ded_hdr = "DEDICATÓRIA DA PRODUÇÃO" if lang == "PT" else "PRODUCTION DEDICATION"
    ded_body = "Inspirado pelas grandes obras e mangás do Japão Feudal." if lang == "PT" else "Inspired by the great masterworks and manga of Feudal Japan."
    t_ded = Table([[
        [
            Paragraph(f"<b>{ded_hdr}:</b> {ded_body}", styles["body_text"])
        ]
    ]], colWidths=[530])
    t_ded.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_ded)
    story.append(Spacer(1, 6))

    # Poema de Morte (Jisei) de Yoshida Shōin e Tradução
    poem_jp_lines = "身はたとひ<br/>武蔵の野辺に<br/>朽ちぬとも<br/>留め置かまし<br/>大和魂"
    author_str = "— <font face='Cinzel'><b>Yoshida Shōin</b></font> (吉田松陰) —"
    poem_tr_pt = (
        "«Mesmo que o meu corpo<br/>"
        "Nas planícies de Musashi<br/>"
        "Venha a apodrecer,<br/>"
        "Deixarei para trás<br/>"
        "O espírito japonês.»"
    )
    poem_tr_en = (
        "«Even should my body<br/>"
        "Upon the plains of Musashi<br/>"
        "Decay and turn to dust,<br/>"
        "I shall leave behind<br/>"
        "The Japanese soul.»"
    )
    poem_tr_lines = poem_tr_pt if lang == "PT" else poem_tr_en

    t_poem = Table([[
        [
            Paragraph(poem_jp_lines, styles["poem_jp"]),
            Spacer(1, 2),
            Paragraph(author_str, styles["poem_author"]),
            Spacer(1, 2),
            Paragraph(poem_tr_lines, styles["poem_tr"]),
        ]
    ]], colWidths=[530])
    t_poem.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_TABLE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.6, COLOR_BORDER_GOLD),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_poem)
    story.append(Spacer(1, 8))

    # Fechamento com Colletes
    colletes_line_pt = "<b>COLLETES • 2026 • TODOS OS DIREITOS RESERVADOS</b>"
    colletes_line_en = "<b>COLLETES • 2026 • ALL RIGHTS RESERVED</b>"
    story.append(Paragraph(colletes_line_pt if lang == "PT" else colletes_line_en, styles["subtitle_cover"]))


def compile_manual(lang="PT", output_path=None):
    """Compila o manual condensado completo de 24 páginas (2 lutadores e 2 arenas por página)."""
    if output_path is None:
        output_path = f"docs/Samurai_Edge_Manual_{lang}.pdf"

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    print(f"=== Compilando Manual Samurai Edge Condensado ({lang}) em '{output_path}' ===")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=26,
        rightMargin=26,
        topMargin=26,
        bottomMargin=26
    )

    styles = create_styles()
    story = []

    # Página 1: Capa
    build_cover_page(story, styles, lang=lang)

    # Página 2: Índice Geral
    build_toc_page(story, styles, lang=lang)

    # Página 3: Lore & Ambientação
    build_lore_page(story, styles, lang=lang)

    # Página 4: As 7 Facções em Guerra
    build_factions_page(story, styles, lang=lang)

    # Página 5: Comandos Básicos & Mecânicas
    build_controls_page(story, styles, lang=lang)

    # Página 6: Modos de Jogo & Prelúdio Marcial
    build_modes_and_prelude_page(story, styles, lang=lang)

    # Páginas 7 a 18: Os 24 Dossiês Unificados (2 LUTADORES E 2 ARENAS POR PÁGINA)
    fighters = fighters_db.FIGHTERS_DATA
    arenas = arenas_db.ARENAS_DATA

    for idx in range(0, len(fighters), 2):
        f1 = fighters[idx]
        a1 = arenas[idx]
        f2 = fighters[idx + 1]
        a2 = arenas[idx + 1]
        build_two_per_page(story, styles, f1, a1, f2, a2, lang=lang)

    # Página 19: O Chefe Final Oni Gashadokuro
    build_boss_page(story, styles, lang=lang)

    # Página 20: Tabela de Desempenho / Tier List
    build_appendix_tier_page(story, styles, lang=lang)

    # Página 21: Guia de Precedência & Clash QTE
    build_appendix_priority_page(story, styles, lang=lang)

    # Página 22: Reagentes de Solo Alquímicos
    build_appendix_soil_page(story, styles, lang=lang)

    # Página 23: Glossário Marcial & Bushido
    build_appendix_glossary_page(story, styles, lang=lang)

    # Página 24: Contra-capa cerimonial
    build_back_cover_page(story, styles, lang=lang)

    # Compilação com Canvas Numerado
    canvas_maker = NumberedParchmentCanvas
    canvas_maker.lang_code = lang

    doc.build(
        story,
        canvasmaker=canvas_maker,
        onFirstPage=draw_parchment_background,
        onLaterPages=draw_parchment_background
    )

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Sucesso: '{output_path}' gerado com sucesso ({file_size_mb:.2f} MB).")
    return output_path


def main():
    compile_manual(lang="PT", output_path="docs/Samurai_Edge_Manual_PT.pdf")
    compile_manual(lang="EN", output_path="docs/Samurai_Edge_Manual_EN.pdf")
    print("\nTodos os manuais em PDF (24 páginas) foram gerados com êxito!")


if __name__ == "__main__":
    main()
