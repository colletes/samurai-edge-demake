#!/usr/bin/env python3
"""
Compilador Oficial do Manual de Instruções em PDF de Samurai Edge: Bakumatsu.
Gera duas edições completas e ultra-profissionais:
- docs/Samurai_Edge_Manual_PT.pdf (Edição em Português)
- docs/Samurai_Edge_Manual_EN.pdf (Edição em Inglês)

Diagramação:
- Formato A4 Vertical (595.27 x 841.89 pt) no estilo clássico de manuais Neo Geo / 90s Arcade.
- Pergaminho Sumi-E estilizado (#FAF6ED) com moldura dupla em laca escura (#4A2C18).
- Tipografia: Shojumaru (títulos ornamentais) e Zen Antique Soft (corpo de texto lírico).
- 24 Lutadores e 24 Arenas dispostos em páginas duplas espelhadas (Página Par = Lutador, Página Ímpar = Arena).
- 60 Páginas exatas sem transbordamentos indesejados.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Importar bases de dados
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
COLOR_ACCENT_BLUE = colors.HexColor("#1B3B54")


class NumberedParchmentCanvas(canvas.Canvas):
    """Canvas com numeração de duas etapas e cabeçalhos / rodapés cerimoniais."""
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

        # Capa (Página 1) e Contra-capa (Página 60) possuem molduras especiais
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
        self.rect(18, 18, w - 36, h - 36)
        self.setStrokeColor(COLOR_BORDER_GOLD)
        self.setLineWidth(0.6)
        self.rect(22, 22, w - 44, h - 44)

        # Cabeçalho cerimonial
        self.setStrokeColor(COLOR_CRIMSON)
        self.setLineWidth(1.0)
        self.line(36, h - 32, w - 36, h - 32)

        lang = getattr(self, "lang_code", "PT")
        hdr_left = "SAMURAI EDGE: BAKUMATSU — MANUAL OFICIAL" if lang == "PT" else "SAMURAI EDGE: BAKUMATSU — OFFICIAL MANUAL"
        hdr_right = "幕末の血闘 (FATAL EXPANSION)"
        
        self.setFont("ZenAntique", 8)
        self.setFillColor(COLOR_CRIMSON)
        self.drawString(36, h - 28, hdr_left)
        self.drawRightString(w - 36, h - 28, hdr_right)

        # Rodapé cerimonial
        self.setStrokeColor(COLOR_BORDER_DARK)
        self.setLineWidth(0.8)
        self.line(36, 38, w - 36, 38)

        ftr_left = "24 GUERREIROS & 24 ARENAS" if lang == "PT" else "24 WARRIORS & 24 ARENAS"
        ftr_right = "EDIÇÃO DE COLECIONADOR" if lang == "PT" else "COLLECTOR'S EDITION"
        page_str = f"— 頁 {page} / {total_pages} —"

        self.setFont("ZenAntique", 7.5)
        self.setFillColor(COLOR_MUTED_TEXT)
        self.drawString(36, 27, ftr_left)
        self.drawRightString(w - 36, 27, ftr_right)

        self.setFont("ZenAntique", 8.5)
        self.setFillColor(COLOR_CRIMSON)
        self.drawCentredString(w / 2.0, 26, page_str)

        self.restoreState()


def draw_parchment_background(canvas_obj, doc):
    """Pinta o fundo de pergaminho cru em todas as páginas."""
    w, h = A4
    canvas_obj.saveState()
    canvas_obj.setFillColor(COLOR_BG_PARCHMENT)
    canvas_obj.rect(0, 0, w, h, fill=1, stroke=0)
    canvas_obj.restoreState()


def create_styles():
    """Gera o conjunto de estilos tipográficos com fontes embutidas."""
    styles = getSampleStyleSheet()

    title_cover = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=28,
        leading=34,
        textColor=COLOR_CRIMSON,
        alignment=1, # Centro
        spaceAfter=10
    )
    subtitle_cover = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=12,
        leading=16,
        textColor=COLOR_INK_BLACK,
        alignment=1,
        spaceAfter=15
    )
    badge_cover = ParagraphStyle(
        "CoverBadge",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=10,
        leading=14,
        textColor=COLOR_BORDER_GOLD,
        alignment=1,
        spaceAfter=10
    )

    page_header = ParagraphStyle(
        "PageHeader",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=15,
        leading=18,
        textColor=COLOR_CRIMSON,
        spaceAfter=3
    )
    page_sub = ParagraphStyle(
        "PageSub",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_MUTED_TEXT,
        spaceAfter=6
    )
    faction_badge = ParagraphStyle(
        "FactionBadge",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_BORDER_GOLD,
        spaceAfter=4
    )

    sec_heading = ParagraphStyle(
        "SecHeading",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=8.5,
        leading=10.5,
        textColor=COLOR_CRIMSON,
        spaceBefore=4,
        spaceAfter=2
    )

    body_text = ParagraphStyle(
        "BodyTextZen",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_INK_BLACK,
        spaceAfter=3
    )

    body_bold = ParagraphStyle(
        "BodyBoldZen",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_INK_BLACK
    )

    table_header_style = ParagraphStyle(
        "TableHdr",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=7.2,
        leading=8.8,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=6.8,
        leading=8.2,
        textColor=COLOR_INK_BLACK
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=7.0,
        leading=8.5,
        textColor=COLOR_CRIMSON
    )

    return {
        "title_cover": title_cover,
        "subtitle_cover": subtitle_cover,
        "badge_cover": badge_cover,
        "page_header": page_header,
        "page_sub": page_sub,
        "faction_badge": faction_badge,
        "sec_heading": sec_heading,
        "body_text": body_text,
        "body_bold": body_bold,
        "table_header": table_header_style,
        "table_cell": table_cell_style,
        "table_cell_bold": table_cell_bold,
    }


def build_cover_page(story, styles, lang="PT"):
    """Página 1: Capa cerimonial estilo pergaminho Sumi-E."""
    logo_path = "assets/concepts/sumie_title_logo_concept.jpg"
    w_avail = 520
    img_h = w_avail * (768.0 / 1376.0) # ~290 pt

    story.append(Spacer(1, 20))
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=480, height=268))
    else:
        story.append(Spacer(1, 200))

    story.append(Spacer(1, 25))
    if lang == "PT":
        story.append(Paragraph("SAMURAI EDGE", styles["title_cover"]))
        story.append(Paragraph("幕末血風録 — O CREPÚSCULO DO AÇO", styles["subtitle_cover"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph("MANUAL DE INSTRUÇÕES & GUIA ESTRATÉGICO OFICIAL", styles["subtitle_cover"]))
        story.append(Paragraph("EXPANSÃO COMPLETA: 24 GUERREIROS • 24 ARENAS TEMÁTICAS", styles["badge_cover"]))
        story.append(Spacer(1, 40))
        story.append(Paragraph("ARQUIVO HISTÓRICO & TÁTICAS DE COMBATE DIEGÉTICO", styles["badge_cover"]))
        story.append(Paragraph("EDO • KYOTO • IGA • NAGASAKI (1860–1868)", styles["subtitle_cover"]))
    else:
        story.append(Paragraph("SAMURAI EDGE", styles["title_cover"]))
        story.append(Paragraph("BAKUMATSU COMBAT CHRONICLES — TWILIGHT OF STEEL", styles["subtitle_cover"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph("OFFICIAL INSTRUCTION MANUAL & STRATEGY GUIDE", styles["subtitle_cover"]))
        story.append(Paragraph("MASTER EXPANSION: 24 FIGHTERS • 24 THEMATIC ARENAS", styles["badge_cover"]))
        story.append(Spacer(1, 40))
        story.append(Paragraph("HISTORICAL ARCHIVE & DIEGETIC DUEL COMBAT DOCTRINE", styles["badge_cover"]))
        story.append(Paragraph("EDO • KYOTO • IGA • NAGASAKI (1860–1868)", styles["subtitle_cover"]))

    story.append(PageBreak())


def build_toc_page(story, styles, lang="PT"):
    """Página 2: Índice geral organizado."""
    title = "ÍNDICE GERAL DE COMBATE" if lang == "PT" else "TABLE OF CONTENTS"
    sub = "ESTRUTURA METÓDICA DO MANUAL DO GUERREIRO" if lang == "PT" else "METHODICAL MANUAL STRUCTURE"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    entries_pt = [
        ("I. SUMÁRIO & CONTEXTO HISTÓRICO", "A Lenda do Bakumatsu e o Selo das Cinzas", "Pág. 03"),
        ("II. AS SETE FACÇÕES EM GUERRA", "Ideologias, Alianças e os Protetores do Povo", "Pág. 04"),
        ("III. COMANDOS & SISTEMA DE DUELO", "Controles Básicos, Clash QTE e Precedência", "Pág. 05"),
        ("IV. MODOS DE COMBATE", "Modo Arcade (12 Lutas) e Modo Versus Local", "Pág. 06"),
        ("V. PRELÚDIO DO TORNEIO", "Filosofia Marcial e Regras do Espaço", "Pág. 07"),
        ("VI. OS 24 COMBATENTES & ARENAS", "Fichas Estratégicas em Páginas Espelhadas", "Págs. 08–55"),
        ("   • 01. Kenshi & Bosque de Bambu Sagrado", "Arashiyama, Kyoto Ocidental", "Págs. 08–09"),
        ("   • 02. Musashi & Duelo na Ilha Ganryu", "Estreito Marítimo de Kanmon", "Págs. 10–11"),
        ("   • 03. Hanzo & Telhados Noturnos de Iga", "Fortaleza das Sombras de Iga", "Págs. 12–13"),
        ("   • 04. Joe & Acampamento Secreto na Floresta", "Posto Avançado Tático de Iga", "Págs. 14–15"),
        ("   • 05. Saitou & Kyoto: Bakumatsu em Chamas", "Incidente Ikedaya / Shinsengumi", "Págs. 16–17"),
        ("   • 06. Teppo & Trincheiras de Nagashino", "Bastião de Infantaria Tanegashima", "Págs. 18–19"),
        ("   • 07. Murasaki & Caverna Sombria do Selo", "Covil Subterrâneo do Titã Esquelético", "Págs. 20–21"),
        ("   • 08. Kasumi & Templo da Névoa Oculta", "Mosteiro de Tendai no Monte Hiei", "Págs. 22–23"),
        ("   • 09. Okuni & Palco Flutuante de Kabuki", "Leito do Rio Kamo, Shijo-Kawaramachi", "Págs. 24–25"),
        ("   • 10. Tomoe & Santuário da Montanha Sagrada", "Monte Kurama, Pátio dos Portais Torii", "Págs. 26–27"),
        ("   • 11. Anne & Convés do Navio Corsário", "Baía de Uraga, Fragata dos Mares", "Págs. 28–29"),
        ("   • 12. Julie & Corte Barroca da Embaixada", "Enclave Francês no Porto de Yokohama", "Págs. 30–31"),
        ("   • 13. Ren & Mosteiro Shaolin das Montanhas", "Songshan, Pátio dos Leões de Bronze", "Págs. 32–33"),
        ("   • 14. Chiyo & Campos Vermelhos de Higanbana", "Planícies de Asuka, Lírios da Morte", "Págs. 34–35"),
        ("   • 15. Benkei & Ponte Gojo à Meia-Noite", "Passagem Cerimonial sobre o Rio Kamo", "Págs. 36–37"),
        ("   • 16. O-Rin & Beco Noturno de Yoshiwara", "Distrito das Flores e Lanternas de Edo", "Págs. 38–39"),
        ("   • 17. Goro & Arrozais e Diques de Água", "Campos Agrícolas de Omi", "Págs. 40–41"),
        ("   • 18. Ichi & Moinho Chuvoso nas Montanhas", "Cataratas da Passagem de Hakone", "Págs. 42–43"),
        ("   • 19. Valerius & Cemitério Prussiano Gótico", "Cripta e Mausoléus da Silésia", "Págs. 44–45"),
        ("   • 20. Seimei & Santuário Heian de Onmyōdō", "Altar Astral com Rondel Pentagrama", "Págs. 46–47"),
        ("   • 21. Daiki & Floresta dos Pinheiros Nevados", "Monte Koya, Trilha dos Peregrinos", "Págs. 48–49"),
        ("   • 22. Aoi & Taiga Selvagem de Ezo", "Hokkaido Primitivo, Terras Ainu", "Págs. 50–51"),
        ("   • 23. Raiden & Dohyo Sagrado Xintoísta", "Sumiyoshi Taisha, Círculo de Sal", "Págs. 52–53"),
        ("   • 24. Hendrika & Armazém de Dejima com Doca", "Feitoria Comercial Holandesa de Nagasaki", "Págs. 54–55"),
        ("VII. O DESPERTAR PROIBIDO — O CHEFE FINAL", "O Titã Esquelético Oni Gashadokuro", "Pág. 56"),
        ("VIII. APÊNDICE: TABELA GERAL DE DESEMPENHO", "Simulação Massiva de 6.624 Duelos (Tier List)", "Pág. 57"),
        ("IX. APÊNDICE: GUIA DE PRIORIDADES & PRECEDÊNCIA", "Mecânicas Avançadas e Choque de Lâminas", "Pág. 58"),
        ("X. APÊNDICE: TABELA DE REAGENTES DE SOLO", "Alquimia Clandestina & Elementos de Seimei", "Pág. 59"),
        ("XI. CONTRA-CAPA & CRÉDITOS DA PRODUÇÃO", "Ficha Técnica e Agradecimentos Especiais", "Pág. 60")
    ]

    entries_en = [
        ("I. INTRODUCTION & HISTORICAL LORE", "The Legend of Bakumatsu and the Ash Seal", "Page 03"),
        ("II. THE SEVEN WARRING FACTIONS", "Ideologies, Alliances & Protectors of the People", "Page 04"),
        ("III. CONTROLS & DUEL MECHANICS", "Basic Controls, Clash QTE & Absolute Precedence", "Page 05"),
        ("IV. COMBAT MODES", "Arcade Mode (12-Fight Ladder) & Local Versus", "Page 06"),
        ("V. TOURNAMENT PRELUDE", "Diegetic Combat Philosophy & Spacing Laws", "Page 07"),
        ("VI. THE 24 FIGHTERS & ARENAS", "Deep Strategic Dossiers on Facing Pages", "Pages 08–55"),
        ("   • 01. Kenshi & Sacred Bamboo Grove", "Arashiyama, Western Kyoto", "Pages 08–09"),
        ("   • 02. Musashi & Duel on Ganryu Island", "Kanmon Maritime Strait", "Pages 10–11"),
        ("   • 03. Hanzo & Night Rooftops of Iga", "Iga Mountain Shadow Fortress", "Pages 12–13"),
        ("   • 04. Joe & Secret Forest Outpost", "Tactical Camp in the Iga Woods", "Pages 14–15"),
        ("   • 05. Saitou & Kyoto: Bakumatsu in Flames", "Ikedaya Incident / Shinsengumi", "Pages 16–17"),
        ("   • 06. Teppo & Trenches of Nagashino", "Tanegashima Matchlock Stronghold", "Pages 18–19"),
        ("   • 07. Murasaki & Shadow Cave of the Seal", "Subterranean Skeletal Titan Den", "Pages 20–21"),
        ("   • 08. Kasumi & Hidden Mist Temple", "Tendai Sanctuary on Mount Hiei", "Pages 22–23"),
        ("   • 09. Okuni & Floating Kabuki Stage", "Kamo Riverbed, Shijo-Kawaramachi", "Pages 24–25"),
        ("   • 10. Tomoe & Sacred Mountain Shrine", "Mount Kurama Torii Courtyard", "Pages 26–27"),
        ("   • 11. Anne & Privateer Ship Deck", "Uraga Bay Maritime Frigate", "Pages 28–29"),
        ("   • 12. Julie & Baroque Embassy Court", "French Enclave in Yokohama Harbor", "Pages 30–31"),
        ("   • 13. Ren & Mountain Shaolin Temple", "Songshan Bronze Lions Courtyard", "Pages 32–33"),
        ("   • 14. Chiyo & Crimson Higanbana Meadows", "Plains of Asuka, Lilies of the Sanzu", "Pages 34–35"),
        ("   • 15. Benkei & Gojo Bridge at Midnight", "Kyoto Ceremonial Span over Kamo River", "Pages 36–37"),
        ("   • 16. O-Rin & Night Alley of Yoshiwara", "Edo Red Lantern Entertainment Quarter", "Pages 38–39"),
        ("   • 17. Goro & Rice Paddies and Dykes", "Rural Agricultural Fields of Omi", "Pages 40–41"),
        ("   • 18. Ichi & Mountain Rain Mill", "Hakone Cataracts & Turning Waterwheel", "Pages 42–43"),
        ("   • 19. Valerius & Gothic Prussian Cemetery", "Silesian Crypts and Iron Spired Tombs", "Pages 44–45"),
        ("   • 20. Seimei & Heian Shrine of Onmyōdō", "Astral Pentagram Rondel Shrine", "Pages 46–47"),
        ("   • 21. Daiki & Snowy Pine Forest", "Mount Koya Sacred Pilgrim Path", "Pages 48–49"),
        ("   • 22. Aoi & Wild Taiga of Ezo", "Primeval Hokkaido, Ancestral Ainu Lands", "Pages 50–51"),
        ("   • 23. Raiden & Sacred Shinto Dohyo", "Sumiyoshi Taisha, Consecrated Clay Ring", "Pages 52–53"),
        ("   • 24. Hendrika & Dejima Warehouse with Dock", "Nagasaki Dutch VOC Trading Factory", "Pages 54–55"),
        ("VII. THE FORBIDDEN AWAKENING — FINAL BOSS", "The Skeletal Titan Oni Gashadokuro", "Page 56"),
        ("VIII. APPENDIX: OVERALL PERFORMANCE TABLE", "Large-Scale 6,624 Duels Simulation (Tier List)", "Page 57"),
        ("IX. APPENDIX: ABSOLUTE PRECEDENCE RULES", "Advanced Combat Priority & Blade Clash QTE", "Page 58"),
        ("X. APPENDIX: SOIL REAGENTS ALCHEMY TABLE", "Clandestine Alchemy & Seimei Elements", "Page 59"),
        ("XI. BACK COVER & PRODUCTION CREDITS", "Technical Colophon & Special Dedication", "Page 60")
    ]

    entries = entries_pt if lang == "PT" else entries_en
    table_data = []
    for section, desc, page_num in entries:
        table_data.append([
            Paragraph(section, styles["table_cell_bold"]),
            Paragraph(desc, styles["table_cell"]),
            Paragraph(f"<b>{page_num}</b>", styles["table_cell_bold"])
        ])

    toc_table = Table(table_data, colWidths=[200, 260, 60])
    toc_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E0D6C3")),
    ]))

    story.append(toc_table)
    story.append(PageBreak())


def build_lore_page(story, styles, lang="PT"):
    """Página 3: Lore & Ambientação Histórica do Bakumatsu."""
    l_data = data_pt.LORE_PT if lang == "PT" else data_en.LORE_EN

    story.append(Paragraph(l_data["title"], styles["page_header"]))
    sub = "O CREPÚSCULO DO XOGUNATO & A PROFECIA DO SANGUE" if lang == "PT" else "TWILIGHT OF THE SHOGUNATE & THE BLOOD PROPHECY"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=10))

    banner_art = "assets/concepts/kyoto_bakumatsu_concept.jpg"
    if os.path.exists(banner_art):
        story.append(Image(banner_art, width=520, height=180))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>1. O Fim de Dois Séculos de Paz (Sakoku)</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p1"], styles["body_text"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>2. O Titã Adormecido na Caverna Sombria</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p2"], styles["body_text"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>3. A Conspiração do Despertar</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p3"], styles["body_text"]))

    story.append(PageBreak())


def build_factions_page(story, styles, lang="PT"):
    """Página 4: As 7 Facções em Guerra."""
    factions = data_pt.FACTIONS_PT if lang == "PT" else data_en.FACTIONS_EN
    title = "AS SETE FACÇÕES EM GUERRA" if lang == "PT" else "THE SEVEN WARRING FACTIONS"
    sub = "ALIANÇAS, LEALDADES E MOTIVAÇÕES DO SANGUE" if lang == "PT" else "ALLIANCES, LOYALTIES & BLOOD MOTIVATIONS"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    for idx, f in enumerate(factions):
        story.append(Paragraph(f["name"], styles["sec_heading"]))
        members_str = ", ".join(f["members"])
        lbl_members = "<b>Integrantes:</b> " if lang == "PT" else "<b>Members:</b> "
        lbl_phil = "<b>Filosofia Marcial:</b> " if lang == "PT" else "<b>Martial Philosophy:</b> "

        p_desc = f"{f['desc']}<br/>{lbl_members}<font color='#8C1D13'>{members_str}</font><br/>{lbl_phil}<i>{f['philosophy']}</i>"
        story.append(Paragraph(p_desc, styles["body_text"]))
        story.append(Spacer(1, 4))

    story.append(PageBreak())


def build_controls_page(story, styles, lang="PT"):
    """Página 5: Comandos Básicos & Mecânicas de Duelo."""
    c_data = data_pt.CONTROLS_PT if lang == "PT" else data_en.CONTROLS_EN

    story.append(Paragraph(c_data["title"], styles["page_header"]))
    sub = "SISTEMA DE CONTROLE DIEGÉTICO E LETALIDADE DE UMA LÂMINA" if lang == "PT" else "DIEGETIC CONTROL SYSTEM & SINGLE-BLADE LETHALITY"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    story.append(Paragraph(c_data["desc"], styles["body_text"]))
    story.append(Spacer(1, 8))

    # Tabela de controles
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

    ctrl_table = Table(table_rows, colWidths=[100, 120, 110, 190])
    ctrl_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(ctrl_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Mecânicas Centrais de Duelo:</b>" if lang == "PT" else "<b>Core Dueling Mechanics:</b>", styles["sec_heading"]))
    for m_title, m_desc in c_data["mechanics"]:
        story.append(Paragraph(f"• <b>{m_title}:</b> {m_desc}", styles["body_text"]))
        story.append(Spacer(1, 3))

    story.append(PageBreak())


def build_modes_page(story, styles, lang="PT"):
    """Página 6: Modos de Jogo (Arcade 12 Lutas & Versus)."""
    m_data = data_pt.MODES_PT if lang == "PT" else data_en.MODES_EN

    story.append(Paragraph(m_data["title"], styles["page_header"]))
    sub = "A ESCADA DO DESTINO & CONFRONTOS MULTIJOGADOR" if lang == "PT" else "THE LADDER OF DESTINY & MULTIPLAYER CLASHES"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    story.append(Paragraph(f"<b>{m_data['arcade_title']}</b>", styles["sec_heading"]))
    story.append(Paragraph(m_data["arcade_desc"], styles["body_text"]))
    story.append(Spacer(1, 6))

    for stg_title, stg_desc in m_data["arcade_stages"]:
        story.append(Paragraph(f"• <b>{stg_title}:</b> {stg_desc}", styles["body_text"]))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>{m_data['versus_title']}</b>", styles["sec_heading"]))
    story.append(Paragraph(m_data["versus_desc"], styles["body_text"]))

    story.append(PageBreak())


def build_prelude_page(story, styles, lang="PT"):
    """Página 7: Prelúdio Marcial & Filosofia do Duelo."""
    title = "PRELÚDIO MARCIAL — A FILOSOFIA DO COMBATE DIEGÉTICO" if lang == "PT" else "MARTIAL PRELUDE — THE PHILOSOPHY OF DIEGETIC COMBAT"
    sub = "A ARTE DO ESPAÇO, DA ANTECIPAÇÃO E DA MORTE SILENCIOSA" if lang == "PT" else "THE ART OF SPACING, ANTICIPATION & SILENT LETHALITY"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    art_p = "assets/concepts/sumie_title_logo_concept.jpg"
    if os.path.exists(art_p):
        story.append(Image(art_p, width=520, height=160))
        story.append(Spacer(1, 8))

    if lang == "PT":
        story.append(Paragraph("<b>1. A Dança das Distâncias (Maai - 間合い)</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "Em Samurai Edge, o espaçamento não é apenas uma vantagem táctica: é a fronteira exata entre a vida e a morte. "
            "Cada combatente possui um arco de ameaça milimetricamente medido pelo comprimento de sua arma. Um duelista "
            "de espada curta que tenta disputar espaço aberto contra a Naginata de Benkei ou as flechas de Tomoe encontrará "
            "o túmulo antes mesmo de conseguir desembainhar. Dominar o recuo da esquiva e avançar milésimos de segundo "
            "após o erro do oponente é o princípio de ouro de todo Kensei.",
            styles["body_text"]
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>2. A Mente Vazia (Mushin - 無心) e o Choque de Lâminas</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "Quando dois golpes se cruzam simultaneamente, o tempo desacelera no Choque de Lâminas (Clash). Não hesite: "
            "a vitória pertence a quem mantiver o foco e desferir o contra-ataque mais célere. Contudo, fique atento à "
            "regra de Precedência Absoluta: certas armas e ataques pesados ignoram o choque e esmagam lâminas menores com "
            "força gravitacional pura.",
            styles["body_text"]
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>3. A Conexão Sagrada entre Lutador e Arena</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "Nas próximas 48 páginas, cada guerreiro é apresentado lado a lado com sua arena temática natal. O solo onde "
            "você pisa não é um mero cenário decorativo: ele dita a velocidade dos rolamentos, os reagentes que Hendrika "
            "pode colher em tempo real, as runas elementais que Seimei invoca, e os perigos de precipícios onde um único "
            "empurrão encerra o duelo sem piedade.",
            styles["body_text"]
        ))
    else:
        story.append(Paragraph("<b>1. The Dance of Distance (Maai - 間合い)</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "In Samurai Edge, spacing is not merely a tactical advantage: it is the exact boundary between survival and demise. "
            "Each warrior commands a threat perimeter dictated by weapon reach. A short-blade duelist attempting to contest "
            "open terrain against Benkei's massive Naginata or Tomoe's longbow volleys will meet death before closing distance. "
            "Mastering dodge recovery and stepping forward milliseconds after an opponent's whiff is the cornerstone of every Kensei.",
            styles["body_text"]
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>2. The Empty Mind (Mushin - 無心) and the Blade Clash</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "When two attacks cross simultaneously within the same frame, time fractures in a Blade Clash. Never hesitate: "
            "victory belongs to the combatant who maintains supreme composure and mashes the counter-strike fastest. "
            "However, heed the law of Absolute Precedence: certain heavy strikes and signature thrusts bypass clashes entirely, "
            "crushing lesser steel under pure kinetic mass.",
            styles["body_text"]
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>3. The Sacred Bond Between Fighter and Arena</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "Across the next 48 pages, each champion is paired alongside their ancestral home arena. The earth beneath your feet "
            "is no mere decorative backdrop: it dictates dodge roll deceleration, the chemical reagents Hendrika can synthesize "
            "in real time, the elemental pentagrams Seimei channels, and lethal precipice drop-offs where a single throw decides the round.",
            styles["body_text"]
        ))

    story.append(PageBreak())


def build_fighter_page(story, styles, fighter, lang="PT"):
    """Página Par (Esquerda): Ficha Estratégica Completa do Lutador."""
    name = fighter["name_pt"] if lang == "PT" else fighter["name_en"]
    title = fighter["title_pt"] if lang == "PT" else fighter["title_en"]
    faction = fighter["faction_pt"] if lang == "PT" else fighter["faction_en"]
    lore = fighter["lore_pt"] if lang == "PT" else fighter["lore_en"]
    reach = fighter["reach_pt"] if lang == "PT" else fighter["reach_en"]
    style_m = fighter["style_pt"] if lang == "PT" else fighter["style_en"]
    moves = fighter["moveset_pt"] if lang == "PT" else fighter["moveset_en"]

    story.append(Paragraph(name, styles["page_header"]))
    story.append(Paragraph(title, styles["page_sub"]))
    story.append(Paragraph(f"<b>{faction}</b>", styles["faction_badge"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_CRIMSON, spaceAfter=4))

    # Bloco Superior: Imagem Conceitual à Esquerda + Stats & Lore à Direita
    img_path = fighter["concept_art"]
    img_flow = Spacer(1, 130)
    if os.path.exists(img_path):
        img_flow = Image(img_path, width=100, height=134)

    stats_pt = (
        f"<b>HP:</b> {fighter['hp']} Pontos &nbsp;|&nbsp; <b>Velocidade:</b> {fighter['speed']}<br/>"
        f"<b>Alcance:</b> {reach}<br/>"
        f"<b>Estilo Marcial:</b> {style_m}"
    )
    stats_en = (
        f"<b>HP:</b> {fighter['hp']} Points &nbsp;|&nbsp; <b>Speed:</b> {fighter['speed']}<br/>"
        f"<b>Reach:</b> {reach}<br/>"
        f"<b>Martial Style:</b> {style_m}"
    )
    stats_str = stats_pt if lang == "PT" else stats_en

    p_stats = Paragraph(stats_str, styles["body_text"])
    p_lore = Paragraph(f"<b>Lore & Origem:</b> {lore}" if lang == "PT" else f"<b>Lore & Origin:</b> {lore}", styles["body_text"])

    right_col = [p_stats, Spacer(1, 3), p_lore]
    top_table = Table([[img_flow, right_col]], colWidths=[108, 412])
    top_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(top_table)
    story.append(Spacer(1, 4))

    # Tabela de Comandos do Personagem
    m_headers = ["Ataque / Técnica", "Gamepad", "Teclado P1/P2", "Efeito & Aplicação Tática"] if lang == "PT" else ["Strike / Technique", "Gamepad", "Keyboard P1/P2", "Tactical Application"]
    m_rows = [[
        Paragraph(m_headers[0], styles["table_header"]),
        Paragraph(m_headers[1], styles["table_header"]),
        Paragraph(m_headers[2], styles["table_header"]),
        Paragraph(m_headers[3], styles["table_header"])
    ]]

    for m_name, pad, kb, effect in moves:
        m_rows.append([
            Paragraph(f"<b>{m_name}</b>", styles["table_cell_bold"]),
            Paragraph(pad, styles["table_cell"]),
            Paragraph(kb, styles["table_cell"]),
            Paragraph(effect, styles["table_cell"])
        ])

    m_table = Table(m_rows, colWidths=[110, 85, 95, 230])
    m_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 4))

    # Análise de Armas
    w_title = "ANÁLISE DE ARMAS & MECÂNICAS PRÓPRIAS" if lang == "PT" else "WEAPON ANALYSIS & SIGNATURE MECHANICS"
    story.append(Paragraph(w_title, styles["sec_heading"]))
    w_text = fighter["weapons_pt"] if lang == "PT" else fighter["weapons_en"]
    story.append(Paragraph(w_text, styles["body_text"]))
    story.append(Spacer(1, 3))

    # Ciclo de Vitória (Plano de Jogo em 3 Fases)
    gp_title = "O CICLO DE VITÓRIA (PLANO DE JOGO PASSO A PASSO)" if lang == "PT" else "THE VICTORY CYCLE (STEP-BY-STEP GAMEPLAN)"
    story.append(Paragraph(gp_title, styles["sec_heading"]))
    gp_text = fighter["gameplan_pt"] if lang == "PT" else fighter["gameplan_en"]
    gp_html = gp_text.strip().replace("\n", "<br/>")
    story.append(Paragraph(gp_html, styles["body_text"]))
    story.append(Spacer(1, 3))

    # Como Vencer (Estratégia Defensiva)
    def_title = "COMO VENCER (ESTRATÉGIA DEFENSIVA & JANELAS DE PUNIÇÃO)" if lang == "PT" else "HOW TO BEAT (DEFENSIVE STRATEGY & PUNISH WINDOWS)"
    story.append(Paragraph(def_title, styles["sec_heading"]))
    def_text = fighter["how_to_beat_pt"] if lang == "PT" else fighter["how_to_beat_en"]
    story.append(Paragraph(def_text, styles["body_text"]))

    story.append(PageBreak())


def build_arena_page(story, styles, arena, lang="PT"):
    """Página Ímpar (Direita): Ficha da Arena Temática Pareada."""
    name = arena["name_pt"] if lang == "PT" else arena["name_en"]
    loc = arena["location_pt"] if lang == "PT" else arena["location_en"]
    hist = arena["historical_context_pt"] if lang == "PT" else arena["historical_context_en"]
    hazards = arena["hazards_pt"] if lang == "PT" else arena["hazards_en"]
    soil = arena["soil_alchemy_pt"] if lang == "PT" else arena["soil_alchemy_en"]
    tactics = arena["tactics_pt"] if lang == "PT" else arena["tactics_en"]

    story.append(Paragraph(name, styles["page_header"]))
    story.append(Paragraph(loc, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_CRIMSON, spaceAfter=4))

    # Arte Conceitual 16:9 Panorâmica
    img_path = arena["concept_art"]
    if os.path.exists(img_path):
        story.append(Image(img_path, width=520, height=270))
        story.append(Spacer(1, 6))
    else:
        story.append(Spacer(1, 270))

    # Contexto Histórico de 1860
    h_title = "CONTEXTO HISTÓRICO & AMBIENTAÇÃO (1860s)" if lang == "PT" else "HISTORICAL CONTEXT & ATMOSPHERE (1860s)"
    story.append(Paragraph(h_title, styles["sec_heading"]))
    story.append(Paragraph(hist, styles["body_text"]))
    story.append(Spacer(1, 4))

    # Perigos Ambientais
    hz_title = "PERIGOS AMBIENTAIS & FOSSOS DE QUEDA (RING-OUT)" if lang == "PT" else "ENVIRONMENTAL HAZARDS & RING-OUT PRECIPICES"
    story.append(Paragraph(hz_title, styles["sec_heading"]))
    story.append(Paragraph(hazards, styles["body_text"]))
    story.append(Spacer(1, 4))

    # Solo & Alquimia
    sl_title = "COMPOSIÇÃO DO SOLO & REAGENTES ALQUÍMICOS (HENDRIKA & SEIMEI)" if lang == "PT" else "SOIL COMPOSITION & ALCHEMICAL REAGENTS (HENDRIKA & SEIMEI)"
    story.append(Paragraph(sl_title, styles["sec_heading"]))
    story.append(Paragraph(soil, styles["body_text"]))
    story.append(Spacer(1, 4))

    # Táticas Espaciais
    tc_title = "TÁTICAS DE CONTROLE ESPACIAL & ZONEAMENTO" if lang == "PT" else "SPATIAL TACTICS & ZONE CONTROL"
    story.append(Paragraph(tc_title, styles["sec_heading"]))
    story.append(Paragraph(tactics, styles["body_text"]))

    story.append(PageBreak())


def build_boss_page(story, styles, lang="PT"):
    """Página 56: O Despertar Proibido — O Chefe Final Oni Gashadokuro."""
    b_data = data_pt.BOSS_TEASER_PT if lang == "PT" else data_en.BOSS_TEASER_EN

    story.append(Paragraph(b_data["title"], styles["page_header"]))
    story.append(Paragraph(f"<b>{b_data['name']}</b> — {b_data['subtitle']}", styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=6))

    img_p = b_data["concept_art"]
    if os.path.exists(img_p):
        story.append(Image(img_p, width=520, height=260))
        story.append(Spacer(1, 6))

    story.append(Paragraph("<b>A Lenda do Colosso Adormecido:</b>" if lang == "PT" else "<b>Legend of the Slumbering Colossus:</b>", styles["sec_heading"]))
    story.append(Paragraph(b_data["lore"], styles["body_text"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph(f"<b>{b_data['warning_title']}</b>", styles["sec_heading"]))
    for w_title, w_desc in b_data["warning_points"]:
        story.append(Paragraph(f"• <b>{w_title}:</b> {w_desc}", styles["body_text"]))
        story.append(Spacer(1, 2))

    story.append(PageBreak())


def build_appendix_tier_page(story, styles, lang="PT"):
    """Página 57: Tabela Geral de Desempenho (6.624 Simulações)."""
    app = data_pt.APPENDIX_PT if lang == "PT" else data_en.APPENDIX_EN

    story.append(Paragraph(app["title"], styles["page_header"]))
    story.append(Paragraph(app["tier_title"], styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=6))

    story.append(Paragraph(app["tier_desc"], styles["body_text"]))
    story.append(Spacer(1, 4))

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
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(tier_table)

    story.append(PageBreak())


def build_appendix_priority_page(story, styles, lang="PT"):
    """Página 58: Guia de Prioridades & Precedência Absoluta de Golpes."""
    title = "GUIA DE PRIORIDADES & PRECEDÊNCIA ABSOLUTA" if lang == "PT" else "ABSOLUTE PRECEDENCE & PRIORITY DIRECTIVE"
    sub = "MATEMÁTICA DE CHOQUE DE LÂMINAS & FRAMES DE INICIATIVA" if lang == "PT" else "BLADE CLASH MATHEMATICS & INITIATIVE FRAMES"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    if lang == "PT":
        story.append(Paragraph("<b>1. A Hierarquia Universal de Impacto</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "Em Samurai Edge, os ataques são processados em 4 camadas de precedência matemática estrita. Quando dois combatentes "
            "atacam dentro do mesmo ciclo de verificação espacial, o motor do jogo consulta a seguinte ordem de resolução:",
            styles["body_text"]
        ))
        p_layers = [
            ("Nível 4: Precedência Absoluta (Imparável)", "Golpes como a Foice da Kusarigama de Murasaki e a Estocada de Florete de Hendrika possuem garantia matemática de corte. Ignoram Choque de Lâminas e interrompem qualquer golpe de nível inferior."),
            ("Nível 3: Quebra de Guarda Pesada (Guard Crush)", "Disparos de festim da baioneta de Teppo, martelos de guerra (Kanabo de Benkei) e golpes de solo de Raiden. Esmagam posições de Parry ativo, aplicando Stun severo no defensor."),
            ("Nível 2: Disputa Simétrica (Choque de Lâminas / Clash)", "Ataques de corte padrão de espadas médias e longas (Kenshi, Musashi, Saitou, Chiyo, Julie). Provocam travamento cinemático com faíscas e iniciam o evento QTE de digitação rápida."),
            ("Nível 1: Ataques Leves & Projéteis Menores", "Shurikens, kunais de longo alcance, facas de arremesso e golpes de mão desarmada. São defletidos instantaneamente por qualquer postura de Parry ou golpe de espada.")
        ]
        for l_title, l_desc in p_layers:
            story.append(Paragraph(f"• <b>{l_title}:</b> {l_desc}", styles["body_text"]))
            story.append(Spacer(1, 3))

        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>2. Anatomia do Choque de Lâminas (Blade Clash QTE)</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "Durante um Choque de Lâminas, a tela congela por 600 milissegundos enquanto partículas de centelhas emanam "
            "do ponto de colisão tridimensional. O combatente que registrar a maior taxa de acionamentos do botão primário de ataque "
            "desequilibra o rival: o perdedor sofre 24 frames de cambaleio forçado (Off-Balance), ficando completamente exposto "
            "ao golpe de misericórdia sem chance de esquiva ou bloqueio.",
            styles["body_text"]
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>3. A Regra de Ouro da Invulnerabilidade de Rolamento</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "O rolamento evasivo confere 12 frames de invulnerabilidade total a cortes horizontais e projéteis. Contudo, "
            "ataques com trajetória descendente cravada (como o Pisotão de Raiden ou a Lança de Aoi) atingem combatentes "
            "no solo mesmo durante o rolamento, punindo esquivas precipitadas.",
            styles["body_text"]
        ))
    else:
        story.append(Paragraph("<b>1. The Universal Impact Hierarchy</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "In Samurai Edge, attacks are resolved across 4 strict mathematical priority layers. When two combatants swing "
            "within the same spatial verification tick, the engine applies the following resolution order:",
            styles["body_text"]
        ))
        p_layers_en = [
            ("Tier 4: Absolute Precedence (Unstoppable)", "Signature strikes like Murasaki's Kusarigama Scythe and Hendrika's Piercing Rapier boast hard-coded priority. They bypass Blade Clashes and cleanly sever any lower-tier attack."),
            ("Tier 3: Guard Crush Heavy Strikes", "Teppo's blank-charge blast, Benkei's Kanabo war club, and Raiden's ground slams. They shatter active parry stances and inflict crushing stun upon defenders."),
            ("Tier 2: Symmetric Clashes (Blade Clash QTE)", "Standard horizontal cuts and slashes from mid-to-long swords (Kenshi, Musashi, Saitou, Chiyo, Julie). They trigger cinematic sparks and initiate the micro-mash event."),
            ("Tier 1: Light Strikes & Secondary Projectiles", "Shurikens, thrown kunai, darts, and unarmed jabs. Deflected effortlessly by any active parry stance or sword cut.")
        ]
        for l_title, l_desc in p_layers_en:
            story.append(Paragraph(f"• <b>{l_title}:</b> {l_desc}", styles["body_text"]))
            story.append(Spacer(1, 3))

        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>2. Anatomy of the Blade Clash QTE</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "During a Blade Clash, the screen freezes for 600 milliseconds as metallic sparks burst from the 3D contact point. "
            "The player recording the higher attack button tap frequency overpowers the lock: the defeated fighter suffers 24 frames "
            "of off-balance stagger, remaining entirely defenseless against a follow-up coup de grâce.",
            styles["body_text"]
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>3. The Golden Rule of Dodge Invulnerability</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "Evasive rolls grant 12 frames of invulnerability to horizontal slashes and projectiles. However, ground-pounding "
            "downward strikes (such as Raiden's stomp or Aoi's spear pin) track low hitboxes, punishing panic rolls mercilessly.",
            styles["body_text"]
        ))

    story.append(PageBreak())


def build_appendix_soil_page(story, styles, lang="PT"):
    """Página 59: Tabela de Reagentes de Solo Alquímicos."""
    app = data_pt.APPENDIX_PT if lang == "PT" else data_en.APPENDIX_EN

    story.append(Paragraph(app["soil_table_title"], styles["page_header"]))
    sub = "GUIA DE REAGENTES NATURAIS & ELEMENTOS DO RONDEL" if lang == "PT" else "NATURAL REAGENTS & RONDEL ELEMENTS DIRECTIVE"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    desc_pt = (
        "Hendrika sintetiza poções alquímicas em tempo real colhendo minerais e ervas do solo da arena. "
        "A tabela abaixo detalha as propriedades de cada bioma e seus benefícios exclusivos para poções e feitiços de Onmyōdō:"
    )
    desc_en = (
        "Hendrika synthesizes combat flasks in real time by gathering minerals and herbs from the arena floor. "
        "The table below details biome properties and unique benefits conferred upon alchemical brews and Onmyōdō spells:"
    )
    story.append(Paragraph(desc_pt if lang == "PT" else desc_en, styles["body_text"]))
    story.append(Spacer(1, 6))

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

    s_table = Table(rows, colWidths=[120, 140, 140, 120])
    s_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 10))

    if lang == "PT":
        story.append(Paragraph("<b>Guia Rápido dos Cinco Elementos de Seimei (Onmyōdō):</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "• <b>Madeira (Wood):</b> Curvatura de projéteis e aprisionamento em raízes nos bosques de Arashiyama e Koya.<br/>"
            "• <b>Fogo (Fire):</b> Labaredas em leque e dano contínuo acelerado nas ruas em chamas de Kyoto e forjas.<br/>"
            "• <b>Terra (Earth):</b> Barreiras de estalactite e muralhas protetoras nos arrozais de Omi e Dohyo sagrado.<br/>"
            "• <b>Metal (Metal):</b> Deflexão passiva e projéteis afiados na corte francesa de Julie e Dejima.<br/>"
            "• <b>Água (Water):</b> Névoas ofuscantes e ondas de impacto cinético na Ilha Ganryu e Ponte Gojo.",
            styles["body_text"]
        ))
    else:
        story.append(Paragraph("<b>Quick Guide to Seimei's Five Elements (Onmyōdō):</b>", styles["sec_heading"]))
        story.append(Paragraph(
            "• <b>Wood:</b> Projectile curve tracing and root entanglements across Arashiyama and Mount Koya forests.<br/>"
            "• <b>Fire:</b> Fan-shaped firewalls and rapid ticking burn damage across burning Kyoto streets.<br/>"
            "• <b>Earth:</b> Stalagmite barriers and shockwave deflectors across Omi rice paddies and sacred Dohyo.<br/>"
            "• <b>Metal:</b> Passive weapon deflection and razor talismans in Julie's French embassy and Dejima docks.<br/>"
            "• <b>Water:</b> Blinding fogs and hydraulic kinetic waves on Ganryu Island and Gojo Bridge.",
            styles["body_text"]
        ))

    story.append(PageBreak())


def build_back_cover_page(story, styles, lang="PT"):
    """Página 60: Contra-capa cerimonial e créditos de encerramento."""
    app = data_pt.APPENDIX_PT if lang == "PT" else data_en.APPENDIX_EN

    story.append(Spacer(1, 40))
    title = "SAMURAI EDGE: BAKUMATSU"
    sub = "幕末の血闘 — FICHA TÉCNICA & CRÉDITOS DA PRODUÇÃO" if lang == "PT" else "BAKUMATSU COMBAT — TECHNICAL COLOPHON & CREDITS"

    story.append(Paragraph(title, styles["title_cover"]))
    story.append(Paragraph(sub, styles["subtitle_cover"]))
    story.append(HRFlowable(width="80%", thickness=1.5, color=COLOR_CRIMSON, spaceAfter=20))

    logo_path = "assets/concepts/sumie_title_logo_concept.jpg"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=380, height=212))
        story.append(Spacer(1, 20))

    story.append(Paragraph(f"<b>{app['credits_title']}</b>", styles["sec_heading"]))
    story.append(Spacer(1, 6))

    for role, name in app["credits"]:
        story.append(Paragraph(f"<b>{role}:</b> {name}", styles["body_text"]))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 30))
    end_text_pt = (
        "<i>«A lâmina afiada decide o destino em um único sopro.<br/>"
        "Aquele que hesita diante da névoa de Iga já repousa na terra com os ancestrais.»</i><br/><br/>"
        "<b>SAMURAI EDGE STUDIOS • 2026 • TODOS OS DIREITOS RESERVADOS</b>"
    )
    end_text_en = (
        "<i>«A single breath decides the sword's fatal path.<br/>"
        "He who wavers before the mists of Iga already rests beneath the earth with the ancestors.»</i><br/><br/>"
        "<b>SAMURAI EDGE STUDIOS • 2026 • ALL RIGHTS RESERVED</b>"
    )
    story.append(Paragraph(end_text_pt if lang == "PT" else end_text_en, styles["subtitle_cover"]))


def compile_manual(lang="PT", output_path=None):
    """Compila o manual completo de 60 páginas."""
    if output_path is None:
        output_path = f"docs/Samurai_Edge_Manual_{lang}.pdf"

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    print(f"=== Compilando Manual Samurai Edge ({lang}) em '{output_path}' ===")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
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

    # Página 6: Modos de Jogo
    build_modes_page(story, styles, lang=lang)

    # Página 7: Prelúdio do Torneio
    build_prelude_page(story, styles, lang=lang)

    # Páginas 8 a 55: Os 24 Pares (Lutador [Par] / Arena [Ímpar])
    fighters = fighters_db.FIGHTERS_DATA
    arenas = arenas_db.ARENAS_DATA

    for idx in range(len(fighters)):
        f_entry = fighters[idx]
        a_entry = arenas[idx]
        build_fighter_page(story, styles, f_entry, lang=lang)
        build_arena_page(story, styles, a_entry, lang=lang)

    # Página 56: O Chefe Final Oni Gashadokuro
    build_boss_page(story, styles, lang=lang)

    # Página 57: Tabela de Desempenho / Tier List
    build_appendix_tier_page(story, styles, lang=lang)

    # Página 58: Guia de Precedência & Clash QTE
    build_appendix_priority_page(story, styles, lang=lang)

    # Página 59: Reagentes de Solo Alquímicos
    build_appendix_soil_page(story, styles, lang=lang)

    # Página 60: Contra-capa cerimonial
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

    # Verificação do arquivo gerado
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Sucesso: '{output_path}' gerado com sucesso ({file_size_mb:.2f} MB).")
    return output_path


def main():
    compile_manual(lang="PT", output_path="docs/Samurai_Edge_Manual_PT.pdf")
    compile_manual(lang="EN", output_path="docs/Samurai_Edge_Manual_EN.pdf")
    print("\nTodos os manuais em PDF foram gerados com êxito!")


if __name__ == "__main__":
    main()
