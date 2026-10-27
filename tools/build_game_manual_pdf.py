#!/usr/bin/env python3
"""
Compilador Oficial do Manual de Instruções em PDF de Samurai Edge: Bakumatsu.
Edição Condensada de 36 Páginas (Lutador e Arena Unificados na mesma página).

Gera duas edições completas e profissionais:
- docs/Samurai_Edge_Manual_PT.pdf (Edição em Português)
- docs/Samurai_Edge_Manual_EN.pdf (Edição em Inglês)

Diagramação:
- Formato A4 Vertical (595.27 x 841.89 pt) no estilo clássico Neo Geo / 90s Arcade.
- Pergaminho Sumi-E estilizado (#FAF6ED) com moldura dupla em laca e ouro (#3C2214 / #9E7A38).
- Tipografia: Shojumaru (títulos ornamentais) e Zen Antique Soft (corpo e tabelas com suporte kanji/japonês).
- 24 Dossiês Unificados (Páginas 7 a 30): Metade superior = Lutador, Metade inferior = Arena Natal.
- Dados 100% canônicos extraídos do motor de jogo (HP de Musashi/Raiden = 3, cão Yamato, Ryuu Tsui-Sen de Kenshi, Kodachi de Chiyo, e perigos/fossos reais das arenas).
"""

import os
import sys

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
        self.line(32, h - 28, w - 32, h - 28)

        lang = getattr(self, "lang_code", "PT")
        hdr_left = "SAMURAI EDGE: BAKUMATSU — MANUAL OFICIAL" if lang == "PT" else "SAMURAI EDGE: BAKUMATSU — OFFICIAL MANUAL"
        hdr_right = "幕末の血闘 (UNIFIED DOSSIERS)"
        
        self.setFont("ZenAntique", 7.8)
        self.setFillColor(COLOR_CRIMSON)
        self.drawString(32, h - 24, hdr_left)
        self.drawRightString(w - 32, h - 24, hdr_right)

        # Rodapé cerimonial
        self.setStrokeColor(COLOR_BORDER_DARK)
        self.setLineWidth(0.8)
        self.line(32, 34, w - 32, 34)

        ftr_left = "24 GUERREIROS & 24 ARENAS" if lang == "PT" else "24 WARRIORS & 24 ARENAS"
        ftr_right = "EDIÇÃO CONDENSADA" if lang == "PT" else "CONDENSED EDITION"
        page_str = f"— 頁 {page} / {total_pages} —"

        self.setFont("ZenAntique", 7.5)
        self.setFillColor(COLOR_MUTED_TEXT)
        self.drawString(32, 23, ftr_left)
        self.drawRightString(w - 32, 23, ftr_right)

        self.setFont("ZenAntique", 8.5)
        self.setFillColor(COLOR_CRIMSON)
        self.drawCentredString(w / 2.0, 23, page_str)

        self.restoreState()


def draw_parchment_background(canvas_obj, doc):
    """Pinta o fundo de pergaminho cru em todas as páginas."""
    w, h = A4
    canvas_obj.saveState()
    canvas_obj.setFillColor(COLOR_BG_PARCHMENT)
    canvas_obj.rect(0, 0, w, h, fill=1, stroke=0)
    canvas_obj.restoreState()


def create_styles():
    """Gera o conjunto de estilos tipográficos condensados."""
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
        fontSize=7.8,
        leading=10,
        textColor=COLOR_MUTED_TEXT,
        spaceAfter=4
    )
    faction_badge = ParagraphStyle(
        "FactionBadge",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=7.0,
        leading=8.8,
        textColor=COLOR_BORDER_GOLD,
        spaceAfter=3
    )

    sec_heading = ParagraphStyle(
        "SecHeading",
        parent=styles["Normal"],
        fontName="Shojumaru",
        fontSize=7.6,
        leading=9.4,
        textColor=COLOR_CRIMSON,
        spaceBefore=2,
        spaceAfter=1
    )

    body_text = ParagraphStyle(
        "BodyTextZen",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=6.8,
        leading=8.3,
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
        fontSize=6.2,
        leading=7.6,
        textColor=COLOR_INK_BLACK
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="ZenAntique",
        fontSize=6.5,
        leading=7.8,
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
        "table_header": table_header_style,
        "table_cell": table_cell_style,
        "table_cell_bold": table_cell_bold,
    }


def build_cover_page(story, styles, lang="PT"):
    """Página 1: Capa cerimonial."""
    logo_path = "assets/concepts/sumie_title_logo_concept.jpg"
    story.append(Spacer(1, 15))
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=480, height=268))
    else:
        story.append(Spacer(1, 200))

    story.append(Spacer(1, 25))
    if lang == "PT":
        story.append(Paragraph("SAMURAI EDGE", styles["title_cover"]))
        story.append(Paragraph("幕末血風録 — O CREPÚSCULO DO AÇO", styles["subtitle_cover"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph("MANUAL DE INSTRUÇÕES & GUIA ESTRATÉGICO OFICIAL", styles["subtitle_cover"]))
        story.append(Paragraph("EDIÇÃO UNIFICADA: 24 GUERREIROS & 24 ARENAS NATAL", styles["badge_cover"]))
        story.append(Spacer(1, 35))
        story.append(Paragraph("ARQUIVO HISTÓRICO & TÁTICAS DE COMBATE DIEGÉTICO", styles["badge_cover"]))
        story.append(Paragraph("EDO • KYOTO • IGA • NAGASAKI (1860–1868)", styles["subtitle_cover"]))
    else:
        story.append(Paragraph("SAMURAI EDGE", styles["title_cover"]))
        story.append(Paragraph("BAKUMATSU COMBAT CHRONICLES — TWILIGHT OF STEEL", styles["subtitle_cover"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph("OFFICIAL INSTRUCTION MANUAL & STRATEGY GUIDE", styles["subtitle_cover"]))
        story.append(Paragraph("UNIFIED EDITION: 24 WARRIORS & 24 HOME ARENAS", styles["badge_cover"]))
        story.append(Spacer(1, 35))
        story.append(Paragraph("HISTORICAL ARCHIVE & DIEGETIC DUEL COMBAT DOCTRINE", styles["badge_cover"]))
        story.append(Paragraph("EDO • KYOTO • IGA • NAGASAKI (1860–1868)", styles["subtitle_cover"]))

    story.append(PageBreak())


def build_toc_page(story, styles, lang="PT"):
    """Página 2: Índice geral organizado para 36 páginas."""
    title = "ÍNDICE GERAL DE COMBATE" if lang == "PT" else "TABLE OF CONTENTS"
    sub = "ESTRUTURA METÓDICA DO MANUAL DO GUERREIRO (36 PÁGINAS)" if lang == "PT" else "METHODICAL MANUAL STRUCTURE (36 PAGES)"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    entries_pt = [
        ("I. SUMÁRIO & CONTEXTO HISTÓRICO", "A Lenda do Bakumatsu e o Selo das Cinzas", "Pág. 03"),
        ("II. AS SETE FACÇÕES EM GUERRA", "Ideologias, Alianças e os Protetores do Povo", "Pág. 04"),
        ("III. COMANDOS & SISTEMA DE DUELO", "Controles Básicos, Clash QTE e Precedência", "Pág. 05"),
        ("IV. MODOS DE COMBATE & PRELÚDIO", "Arcade (12 Lutas), Versus e Filosofia do Duelo", "Pág. 06"),
        ("V. DOSSIÊS UNIFICADOS (LUTADOR + ARENA)", "24 Guerreiros e suas Arenas na Mesma Página", "Págs. 07–30"),
        ("   • 01. Kenshi & Bosque de Bambu Sagrado", "Arashiyama, Kyoto Ocidental", "Pág. 07"),
        ("   • 02. Musashi & Duelo na Ilha Ganryu", "Estreito Marítimo de Kanmon", "Pág. 08"),
        ("   • 03. Hanzo & Telhados Noturnos de Iga", "Fortaleza das Sombras de Iga", "Pág. 09"),
        ("   • 04. Joe & Acampamento Secreto (Cão Yamato)", "Posto Avançado Tático de Iga", "Pág. 10"),
        ("   • 05. Saitou & Kyoto: Bakumatsu em Chamas", "Incidente Ikedaya / Shinsengumi", "Pág. 11"),
        ("   • 06. Teppo & Trincheiras de Nagashino", "Bastião de Infantaria Tanegashima", "Pág. 12"),
        ("   • 07. Murasaki & Caverna Sombria do Selo", "Covil Subterrâneo do Titã Esquelético", "Pág. 13"),
        ("   • 08. Kasumi & Templo da Névoa Oculta", "Mosteiro de Tendai no Monte Hiei", "Pág. 14"),
        ("   • 09. Okuni & Palco Flutuante de Kabuki", "Leito do Rio Kamo, Shijo-Kawaramachi", "Pág. 15"),
        ("   • 10. Tomoe & Santuário da Montanha Sagrada", "Monte Kurama, Pátio dos Portais Torii", "Pág. 16"),
        ("   • 11. Anne & Convés do Navio Corsário", "Baía de Uraga, Fragata dos Mares", "Pág. 17"),
        ("   • 12. Julie & Corte Barroca da Embaixada", "Enclave Francês no Porto de Yokohama", "Pág. 18"),
        ("   • 13. Ren & Mosteiro Shaolin das Montanhas", "Songshan, Pátio dos Leões de Bronze", "Pág. 19"),
        ("   • 14. Chiyo & Campos de Higanbana (Dual Kodachi)", "Planícies de Asuka, Lírios da Morte", "Pág. 20"),
        ("   • 15. Benkei & Ponte Gojo à Meia-Noite", "Passagem Cerimonial sobre o Rio Kamo", "Pág. 21"),
        ("   • 16. O-Rin & Beco Noturno de Yoshiwara", "Distrito das Flores e Lanternas de Edo", "Pág. 22"),
        ("   • 17. Goro & Arrozais e Diques de Água", "Campos Agrícolas de Omi", "Pág. 23"),
        ("   • 18. Ichi & Moinho Chuvoso nas Montanhas", "Cataratas da Passagem de Hakone", "Pág. 24"),
        ("   • 19. Valerius & Cemitério Prussiano Gótico", "Cripta e Mausoléus da Silésia", "Pág. 25"),
        ("   • 20. Seimei & Santuário Heian de Onmyōdō", "Altar Astral com Rondel Pentagrama", "Pág. 26"),
        ("   • 21. Daiki & Floresta dos Pinheiros Nevados", "Monte Koya, Trilha dos Peregrinos", "Pág. 27"),
        ("   • 22. Aoi & Taiga Selvagem de Ezo", "Hokkaido Primitivo, Terras Ainu", "Pág. 28"),
        ("   • 23. Raiden & Dohyo Sagrado (3 HP)", "Sumiyoshi Taisha, Círculo de Sal", "Pág. 29"),
        ("   • 24. Hendrika & Armazém de Dejima com Doca", "Feitoria Comercial Holandesa de Nagasaki", "Pág. 30"),
        ("VI. O DESPERTAR PROIBIDO — O CHEFE FINAL", "O Titã Esquelético Oni Gashadokuro", "Pág. 31"),
        ("VII. APÊNDICE: TABELA GERAL DE DESEMPENHO", "Simulação Massiva de 6.624 Duelos (Tier List)", "Pág. 32"),
        ("VIII. APÊNDICE: GUIA DE PRIORIDADES & PRECEDÊNCIA", "Mecânicas Avançadas e Choque de Lâminas", "Pág. 33"),
        ("IX. APÊNDICE: TABELA DE REAGENTES DE SOLO", "Alquimia Clandestina & Elementos de Seimei", "Pág. 34"),
        ("X. APÊNDICE: GLOSSÁRIO MARCIAL & BUSHIDO", "Termos Clássicos do Combate Samurai", "Pág. 35"),
        ("XI. CONTRA-CAPA & CRÉDITOS DA PRODUÇÃO", "Ficha Técnica e Agradecimentos Especiais", "Pág. 36")
    ]

    entries_en = [
        ("I. INTRODUCTION & HISTORICAL LORE", "The Legend of Bakumatsu and the Ash Seal", "Page 03"),
        ("II. THE SEVEN WARRING FACTIONS", "Ideologies, Alliances & Protectors of the People", "Page 04"),
        ("III. CONTROLS & DUEL MECHANICS", "Basic Controls, Clash QTE & Absolute Precedence", "Page 05"),
        ("IV. COMBAT MODES & PRELUDE", "Arcade Ladder (12 Fights), Versus & Spacing", "Page 06"),
        ("V. UNIFIED DOSSIERS (FIGHTER + ARENA)", "24 Champions & Home Arenas on Single Pages", "Pages 07–30"),
        ("   • 01. Kenshi & Sacred Bamboo Grove", "Arashiyama, Western Kyoto", "Page 07"),
        ("   • 02. Musashi & Duel on Ganryu Island", "Kanmon Maritime Strait", "Page 08"),
        ("   • 03. Hanzo & Night Rooftops of Iga", "Iga Mountain Shadow Fortress", "Page 09"),
        ("   • 04. Joe & Secret Forest Outpost (Dog Yamato)", "Tactical Camp in the Iga Woods", "Page 10"),
        ("   • 05. Saitou & Kyoto: Bakumatsu in Flames", "Ikedaya Incident / Shinsengumi", "Page 11"),
        ("   • 06. Teppo & Trenches of Nagashino", "Tanegashima Matchlock Stronghold", "Page 12"),
        ("   • 07. Murasaki & Shadow Cave of the Seal", "Subterranean Skeletal Titan Den", "Page 13"),
        ("   • 08. Kasumi & Hidden Mist Temple", "Tendai Sanctuary on Mount Hiei", "Page 14"),
        ("   • 09. Okuni & Floating Kabuki Stage", "Kamo Riverbed, Shijo-Kawaramachi", "Page 15"),
        ("   • 10. Tomoe & Sacred Mountain Shrine", "Mount Kurama Torii Courtyard", "Page 16"),
        ("   • 11. Anne & Privateer Ship Deck", "Uraga Bay Maritime Frigate", "Page 17"),
        ("   • 12. Julie & Baroque Embassy Court", "French Enclave in Yokohama Harbor", "Page 18"),
        ("   • 13. Ren & Mountain Shaolin Temple", "Songshan Bronze Lions Courtyard", "Page 19"),
        ("   • 14. Chiyo & Crimson Higanbana (Dual Kodachi)", "Plains of Asuka, Lilies of the Sanzu", "Page 20"),
        ("   • 15. Benkei & Gojo Bridge at Midnight", "Kyoto Ceremonial Span over Kamo River", "Page 21"),
        ("   • 16. O-Rin & Night Alley of Yoshiwara", "Edo Red Lantern Entertainment Quarter", "Page 22"),
        ("   • 17. Goro & Rice Paddies and Dykes", "Rural Agricultural Fields of Omi", "Page 23"),
        ("   • 18. Ichi & Mountain Rain Mill", "Hakone Cataracts & Turning Waterwheel", "Page 24"),
        ("   • 19. Valerius & Gothic Prussian Cemetery", "Silesian Crypts and Iron Spired Tombs", "Page 25"),
        ("   • 20. Seimei & Heian Shrine of Onmyōdō", "Astral Pentagram Rondel Shrine", "Page 26"),
        ("   • 21. Daiki & Snowy Pine Forest", "Mount Koya Sacred Pilgrim Path", "Page 27"),
        ("   • 22. Aoi & Wild Taiga of Ezo", "Primeval Hokkaido, Ancestral Ainu Lands", "Page 28"),
        ("   • 23. Raiden & Sacred Shinto Dohyo (3 HP)", "Sumiyoshi Taisha, Consecrated Clay Ring", "Page 29"),
        ("   • 24. Hendrika & Dejima Warehouse with Dock", "Nagasaki Dutch VOC Trading Factory", "Page 30"),
        ("VI. THE FORBIDDEN AWAKENING — FINAL BOSS", "The Skeletal Titan Oni Gashadokuro", "Page 31"),
        ("VII. APPENDIX: OVERALL PERFORMANCE TABLE", "Large-Scale 6,624 Duels Simulation (Tier List)", "Page 32"),
        ("VIII. APPENDIX: ABSOLUTE PRECEDENCE RULES", "Advanced Combat Priority & Blade Clash QTE", "Page 33"),
        ("IX. APPENDIX: SOIL REAGENTS ALCHEMY TABLE", "Clandestine Alchemy & Seimei Elements", "Page 34"),
        ("X. APPENDIX: MARTIAL GLOSSARY & BUSHIDO", "Classical Samurai Combat Terms", "Page 35"),
        ("XI. BACK COVER & PRODUCTION CREDITS", "Technical Colophon & Special Dedication", "Page 36")
    ]

    entries = entries_pt if lang == "PT" else entries_en
    table_data = []
    for section, desc, page_num in entries:
        table_data.append([
            Paragraph(section, styles["table_cell_bold"]),
            Paragraph(desc, styles["table_cell"]),
            Paragraph(f"<b>{page_num}</b>", styles["table_cell_bold"])
        ])

    toc_table = Table(table_data, colWidths=[205, 260, 55])
    toc_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
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
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    banner_art = "assets/concepts/kyoto_bakumatsu_concept.jpg"
    if os.path.exists(banner_art):
        story.append(Image(banner_art, width=520, height=180))
        story.append(Spacer(1, 8))

    story.append(Paragraph("<b>1. O Fim de Dois Séculos de Paz (Sakoku)</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p1"], styles["body_text"]))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2. O Titã Adormecido na Caverna Sombria</b>", styles["sec_heading"]))
    story.append(Paragraph(l_data["p2"], styles["body_text"]))
    story.append(Spacer(1, 4))

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
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=6))

    for f in factions:
        story.append(Paragraph(f["name"], styles["sec_heading"]))
        members_str = ", ".join(f["members"])
        lbl_members = "<b>Integrantes:</b> " if lang == "PT" else "<b>Members:</b> "
        lbl_phil = "<b>Filosofia:</b> " if lang == "PT" else "<b>Philosophy:</b> "

        p_desc = f"{f['desc']}<br/>{lbl_members}<font color='#8C1D13'>{members_str}</font> &nbsp;|&nbsp; {lbl_phil}<i>{f['philosophy']}</i>"
        story.append(Paragraph(p_desc, styles["body_text"]))
        story.append(Spacer(1, 3))

    story.append(PageBreak())


def build_controls_page(story, styles, lang="PT"):
    """Página 5: Comandos Básicos & Mecânicas de Duelo."""
    c_data = data_pt.CONTROLS_PT if lang == "PT" else data_en.CONTROLS_EN

    story.append(Paragraph(c_data["title"], styles["page_header"]))
    sub = "SISTEMA DE CONTROLE DIEGÉTICO E LETALIDADE DE UMA LÂMINA" if lang == "PT" else "DIEGETIC CONTROL SYSTEM & SINGLE-BLADE LETHALITY"
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=6))

    story.append(Paragraph(c_data["desc"], styles["body_text"]))
    story.append(Spacer(1, 6))

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
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(ctrl_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Mecânicas Centrais de Duelo:</b>" if lang == "PT" else "<b>Core Dueling Mechanics:</b>", styles["sec_heading"]))
    for m_title, m_desc in c_data["mechanics"]:
        story.append(Paragraph(f"• <b>{m_title}:</b> {m_desc}", styles["body_text"]))
        story.append(Spacer(1, 2))

    story.append(PageBreak())


def build_modes_and_prelude_page(story, styles, lang="PT"):
    """Página 6: Modos de Jogo & Prelúdio Marcial."""
    m_data = data_pt.MODES_PT if lang == "PT" else data_en.MODES_EN

    title = "MODOS DE COMBATE & PRELÚDIO DO TORNEIO" if lang == "PT" else "COMBAT MODES & TOURNAMENT PRELUDE"
    sub = "A ESCADA DO DESTINO & FILOSOFIA DO COMBATE DIEGÉTICO" if lang == "PT" else "THE LADDER OF DESTINY & DIEGETIC DUEL PHILOSOPHY"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=6))

    story.append(Paragraph(f"<b>{m_data['arcade_title']}</b>", styles["sec_heading"]))
    story.append(Paragraph(m_data["arcade_desc"], styles["body_text"]))
    story.append(Spacer(1, 4))

    for stg_title, stg_desc in m_data["arcade_stages"]:
        story.append(Paragraph(f"• <b>{stg_title}:</b> {stg_desc}", styles["body_text"]))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>{m_data['versus_title']}</b>", styles["sec_heading"]))
    story.append(Paragraph(m_data["versus_desc"], styles["body_text"]))
    story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=0.6, color=COLOR_BORDER_GOLD, spaceAfter=4))
    p_title = "FILOSOFIA DO DUELO DIEGÉTICO (MAAI & MUSHIN)" if lang == "PT" else "DIEGETIC DUEL PHILOSOPHY (MAAI & MUSHIN)"
    story.append(Paragraph(f"<b>{p_title}</b>", styles["sec_heading"]))

    if lang == "PT":
        story.append(Paragraph(
            "Em Samurai Edge, cada golpe carrega letalidade cirúrgica. Dominar o <i>Maai</i> (a métrica sagrada do espaço) "
            "e manter a mente calma (<i>Mushin</i>) após o erro do adversário decide o duelo em um único segundo. "
            "Nas páginas a seguir, cada guerreiro é detalhado junto de sua arena temática natal.",
            styles["body_text"]
        ))
    else:
        story.append(Paragraph(
            "In Samurai Edge, every strike carries surgical lethality. Mastering <i>Maai</i> (the sacred measure of distance) "
            "and maintaining an empty, calm mind (<i>Mushin</i>) following an opponent's whiff decides the clash in a single breath. "
            "In the following pages, each champion is paired directly with their ancestral home arena.",
            styles["body_text"]
        ))

    story.append(PageBreak())


def build_unified_dossier_page(story, styles, fighter, arena, lang="PT"):
    """
    Páginas 7 a 30: Dossiê Unificado (Lutador na metade superior, Arena na metade inferior).
    """
    name = fighter["name_pt"] if lang == "PT" else fighter["name_en"]
    title = fighter["title_pt"] if lang == "PT" else fighter["title_en"]
    faction = fighter["faction_pt"] if lang == "PT" else fighter["faction_en"]
    lore = fighter["lore_pt"] if lang == "PT" else fighter["lore_en"]
    reach = fighter["reach_pt"] if lang == "PT" else fighter["reach_en"]
    style_m = fighter["style_pt"] if lang == "PT" else fighter["style_en"]
    moves = fighter["moveset_pt"] if lang == "PT" else fighter["moveset_en"]

    a_name = arena["name_pt"] if lang == "PT" else arena["name_en"]
    a_loc = arena["location_pt"] if lang == "PT" else arena["location_en"]
    a_hist = arena["historical_context_pt"] if lang == "PT" else arena["historical_context_en"]
    a_hazards = arena["hazards_pt"] if lang == "PT" else arena["hazards_en"]
    a_soil = arena["soil_alchemy_pt"] if lang == "PT" else arena["soil_alchemy_en"]
    a_tactics = arena["tactics_pt"] if lang == "PT" else arena["tactics_en"]

    # --- METADE SUPERIOR: O COMBATENTE ---
    story.append(Paragraph(name, styles["page_header"]))
    story.append(Paragraph(f"{title} &nbsp;|&nbsp; <font color='{COLOR_BORDER_GOLD.hexval()}'><b>{faction}</b></font>", styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=COLOR_CRIMSON, spaceAfter=3))

    img_fighter_p = fighter["concept_art"]
    img_fighter = Spacer(1, 95)
    if os.path.exists(img_fighter_p):
        img_fighter = Image(img_fighter_p, width=72, height=96)

    hp_val = fighter["hp"]
    hp_badge = f"<font color='#8C1D13'><b>{hp_val} HP</b></font>" if hp_val > 2 else f"<b>{hp_val} HP</b>"
    stats_pt = (
        f"<b>Vitalidade:</b> {hp_badge} &nbsp;|&nbsp; <b>Velocidade:</b> {fighter['speed']}<br/>"
        f"<b>Alcance:</b> {reach}<br/>"
        f"<b>Estilo Marcial:</b> {style_m}"
    )
    stats_en = (
        f"<b>Health:</b> {hp_badge} &nbsp;|&nbsp; <b>Speed:</b> {fighter['speed']}<br/>"
        f"<b>Reach:</b> {reach}<br/>"
        f"<b>Martial Style:</b> {style_m}"
    )
    stats_str = stats_pt if lang == "PT" else stats_en

    p_stats = Paragraph(stats_str, styles["body_text"])
    p_lore = Paragraph(f"<b>Lore & Origem:</b> {lore}" if lang == "PT" else f"<b>Lore & Origin:</b> {lore}", styles["body_text"])

    fighter_top_table = Table([[img_fighter, [p_stats, Spacer(1, 2), p_lore]]], colWidths=[76, 444])
    fighter_top_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(fighter_top_table)
    story.append(Spacer(1, 2))

    # Tabela de Movimentos
    m_headers = ["Técnica / Golpe", "Gamepad", "Teclado", "Aplicação Tática"] if lang == "PT" else ["Technique / Strike", "Gamepad", "Keyboard", "Tactical Application"]
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

    m_table = Table(m_rows, colWidths=[105, 78, 85, 252])
    m_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 1.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.0),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 2))

    # Análise de Armas & Ciclo de Vitória
    sec_armas_title = "ANÁLISE DE ARMAS & PLANO DE JOGO (CICLO DE VITÓRIA)" if lang == "PT" else "WEAPON ANALYSIS & THE VICTORY CYCLE"
    story.append(Paragraph(sec_armas_title, styles["sec_heading"]))
    w_text = fighter["weapons_pt"] if lang == "PT" else fighter["weapons_en"]
    gp_text = fighter["gameplan_pt"] if lang == "PT" else fighter["gameplan_en"]
    w_and_gp = f"{w_text}<br/>{gp_text.strip().replace(chr(10), '<br/>')}"
    story.append(Paragraph(w_and_gp, styles["body_text"]))
    story.append(Spacer(1, 1))

    # Como Vencer
    def_title = "COMO VENCER (ESTRATÉGIA DEFENSIVA & JANELAS DE PUNIÇÃO)" if lang == "PT" else "HOW TO BEAT (DEFENSIVE STRATEGY & PUNISH WINDOWS)"
    story.append(Paragraph(def_title, styles["sec_heading"]))
    def_text = fighter["how_to_beat_pt"] if lang == "PT" else fighter["how_to_beat_en"]
    story.append(Paragraph(def_text, styles["body_text"]))
    story.append(Spacer(1, 3))

    # --- METADE INFERIOR: A ARENA NATAL ---
    story.append(HRFlowable(width="100%", thickness=1.0, color=COLOR_BORDER_GOLD, spaceAfter=2))
    lbl_arena = "ARENA NATAL" if lang == "PT" else "HOME ARENA"
    story.append(Paragraph(f"<b>{lbl_arena}: {a_name.upper()}</b> — <font color='{COLOR_MUTED_TEXT.hexval()}'>{a_loc}</font>", styles["sec_heading"]))

    img_arena_p = arena["concept_art"]
    img_arena = Spacer(1, 95)
    if os.path.exists(img_arena_p):
        img_arena = Image(img_arena_p, width=175, height=98)

    # Textos da Arena condensados
    lbl_hist = "<b>Contexto Histórico:</b> " if lang == "PT" else "<b>Historical Context:</b> "
    lbl_haz = "<b>Perigos & Fossos:</b> " if lang == "PT" else "<b>Hazards & Pits:</b> "
    lbl_soil = "<b>Solo & Alquimia:</b> " if lang == "PT" else "<b>Soil & Alchemy:</b> "
    lbl_tact = "<b>Controle Espacial:</b> " if lang == "PT" else "<b>Spatial Tactics:</b> "

    # Resumo conciso do histórico (máximo 160 caracteres para caber perfeito)
    short_hist = a_hist if len(a_hist) <= 170 else a_hist[:167] + "..."

    a_text = [
        Paragraph(f"{lbl_hist}{short_hist}", styles["body_text"]),
        Paragraph(f"{lbl_haz}{a_hazards}", styles["body_text"]),
        Paragraph(f"{lbl_soil}{a_soil}", styles["body_text"]),
        Paragraph(f"{lbl_tact}{a_tactics}", styles["body_text"])
    ]

    arena_table = Table([[img_arena, a_text]], colWidths=[180, 340])
    arena_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(arena_table)

    story.append(PageBreak())


def build_boss_page(story, styles, lang="PT"):
    """Página 31: O Despertar Proibido — O Chefe Final Oni Gashadokuro."""
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
    """Página 32: Tabela Geral de Desempenho (6.624 Simulações)."""
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
        ("TOPPADDING", (0, 0), (-1, -1), 1.0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.0),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(tier_table)

    story.append(PageBreak())


def build_appendix_priority_page(story, styles, lang="PT"):
    """Página 33: Guia de Prioridades & Precedência Absoluta de Golpes."""
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
            "ataques com trajetória descendente cravada (como o Pisotão de Raiden ou a descida Ryuu Tsui-Sen de Kenshi) atingem "
            "combatentes no solo mesmo durante o rolamento, punindo esquivas precipitadas.",
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
            "downward strikes (such as Raiden's stomp or Kenshi's Ryuu Tsui-Sen dive) track low hitboxes, punishing panic rolls mercilessly.",
            styles["body_text"]
        ))

    story.append(PageBreak())


def build_appendix_soil_page(story, styles, lang="PT"):
    """Página 34: Tabela de Reagentes de Solo Alquímicos."""
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
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_TABLE_ALT]),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 8))

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


def build_appendix_glossary_page(story, styles, lang="PT"):
    """Página 35: Glossário Marcial & Filosofia do Bushido."""
    title = "GLOSSÁRIO MARCIAL & TERMOS DO COMBATE SAMURAI" if lang == "PT" else "MARTIAL GLOSSARY & SAMURAI COMBAT TERMS"
    sub = "CONCEITOS HISTÓRICOS & DISCIPLINA DO AÇO NO BAKUMATSU" if lang == "PT" else "HISTORICAL CONCEPTS & DISCIPLINE OF BAKUMATSU STEEL"

    story.append(Paragraph(title, styles["page_header"]))
    story.append(Paragraph(sub, styles["page_sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_CRIMSON, spaceAfter=8))

    glossary_pt = [
        ("Iaijutsu (居合術)", "A arte milenar de desembainhar a espada e cortar no mesmo movimento fluido e instantâneo, mortalmente aperfeiçoada por mestres como Kenshi."),
        ("Noto (納刀)", "O ato cerimonial de limpar e embainhar a katana após o corte. No jogo, é a janela de recuperação vulnerável de Kenshi onde o contra-ataque é fatal."),
        ("Maai (間合い)", "A distância de combate entre dois oponentes. Engloba não apenas o espaço físico, mas o tempo necessário para cruzar a distância de ataque."),
        ("Mushin (無心)", "'Mente sem mente'. Estado meditativo de foco absoluto onde o guerreiro age por puro reflexo intuitivo sem hesitação."),
        ("Katsujinken (活人剣)", "A espada que preserva a vida. A filosofia dos Protetores do Povo que empunham o aço para defender inocentes contra tiranos."),
        ("Setsuninto (殺人刀)", "A espada que ceifa vidas. A doutrina de assassinos impiedosos que veem a lâmina apenas como ferramenta de massacre e ambição política."),
        ("Zanzou (残像)", "Pós-imagem visual deixada no ar por movimentos em velocidade sobre-humana, como o Shukuchi Dash de Kenshi e as esquivas de Kasumi."),
        ("Kodachi (小太刀)", "Espada curta japonesa com lâmina entre 50 e 60 cm. Empunhada em pares por Chiyo para cortes velozes e deflexão acrobática."),
        ("Kanabo (金砕棒)", "Clava de guerra octogonal de madeira reforçada com cravos de ferro fundido, empunhada com força esmagadora por Benkei."),
        ("Tsuppari (突っ張り)", "Série de palmadas rápidas com a mão aberta usadas pelos lutadores de Sumô como Raiden para desestabilizar e empurrar rivais."),
        ("Rangaku (蘭学)", "'Estudos Holandeses'. O corpo de conhecimento científico, médico e químico ocidental que Hendrika pesquisa clandestinamente em Dejima.")
    ]

    glossary_en = [
        ("Iaijutsu (居合術)", "The classical martial art of drawing the sword and cutting in a single continuous motion, mastered to perfection by duelists like Kenshi."),
        ("Noto (納刀)", "The ceremonial act of sheathing the blade following a slash. In-game, this represents Kenshi's vulnerable recovery window where counter-hits kill."),
        ("Maai (間合い)", "The spatial combat engagement distance between two duelists. Encompasses both physical reach and the exact time required to strike."),
        ("Mushin (無心)", "'Mind without mind'. A state of pure spontaneous focus where the martial artist acts upon instinct without conscious pause."),
        ("Katsujinken (活人剣)", "The life-giving sword. The moral doctrine of the Protectors of the People who wield steel solely to shield innocents from tyrants."),
        ("Setsuninto (殺人刀)", "The life-taking sword. The doctrine of merciless killers who view the blade purely as an instrument of slaughter and dominance."),
        ("Zanzou (残像)", "Visual afterimage left behind by hypersonic martial displacement, seen in Kenshi's Shukuchi Dash and Kasumi's smoke steps."),
        ("Kodachi (小太刀)", "Japanese short sword with a blade length between 50 and 60 cm. Dual-wielded by Chiyo for rapid slashes and acrobatic deflections."),
        ("Kanabo (金砕棒)", "Heavy octagonal war club studded with iron spikes, wielded with crushing momentum by the warrior monk Benkei."),
        ("Tsuppari (突っ張り)", "Rapid open-palm thrusts employed by Sumo rikishi like Raiden to break guard stances and drive opponents out of the ring."),
        ("Rangaku (蘭学)", "'Dutch Learning'. The body of Western scientific, alchemical, and medical treatises studied clandestinely by Hendrika at Dejima.")
    ]

    glossary = glossary_pt if lang == "PT" else glossary_en
    for term, defn in glossary:
        story.append(Paragraph(f"• <b>{term}:</b> {defn}", styles["body_text"]))
        story.append(Spacer(1, 2))

    story.append(PageBreak())


def build_back_cover_page(story, styles, lang="PT"):
    """Página 36: Contra-capa cerimonial e créditos de encerramento."""
    app = data_pt.APPENDIX_PT if lang == "PT" else data_en.APPENDIX_EN

    story.append(Spacer(1, 35))
    title = "SAMURAI EDGE: BAKUMATSU"
    sub = "幕末の血闘 — FICHA TÉCNICA & CRÉDITOS DA PRODUÇÃO" if lang == "PT" else "BAKUMATSU COMBAT — TECHNICAL COLOPHON & CREDITS"

    story.append(Paragraph(title, styles["title_cover"]))
    story.append(Paragraph(sub, styles["subtitle_cover"]))
    story.append(HRFlowable(width="80%", thickness=1.5, color=COLOR_CRIMSON, spaceAfter=18))

    logo_path = "assets/concepts/sumie_title_logo_concept.jpg"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=380, height=212))
        story.append(Spacer(1, 18))

    story.append(Paragraph(f"<b>{app['credits_title']}</b>", styles["sec_heading"]))
    story.append(Spacer(1, 4))

    for role, name in app["credits"]:
        story.append(Paragraph(f"<b>{role}:</b> {name}", styles["body_text"]))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 25))
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
    """Compila o manual condensado completo de 36 páginas."""
    if output_path is None:
        output_path = f"docs/Samurai_Edge_Manual_{lang}.pdf"

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    print(f"=== Compilando Manual Samurai Edge Condensado ({lang}) em '{output_path}' ===")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
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

    # Páginas 7 a 30: Os 24 Dossiês Unificados (Lutador + Arena na mesma página)
    fighters = fighters_db.FIGHTERS_DATA
    arenas = arenas_db.ARENAS_DATA

    for idx in range(len(fighters)):
        f_entry = fighters[idx]
        a_entry = arenas[idx]
        build_unified_dossier_page(story, styles, f_entry, a_entry, lang=lang)

    # Página 31: O Chefe Final Oni Gashadokuro
    build_boss_page(story, styles, lang=lang)

    # Página 32: Tabela de Desempenho / Tier List
    build_appendix_tier_page(story, styles, lang=lang)

    # Página 33: Guia de Precedência & Clash QTE
    build_appendix_priority_page(story, styles, lang=lang)

    # Página 34: Reagentes de Solo Alquímicos
    build_appendix_soil_page(story, styles, lang=lang)

    # Página 35: Glossário Marcial & Bushido
    build_appendix_glossary_page(story, styles, lang=lang)

    # Página 36: Contra-capa cerimonial
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
    print("\nTodos os manuais em PDF foram gerados com êxito!")


if __name__ == "__main__":
    main()
