"""
Módulo de Internacionalização (i18n) no Padrão Boardbots.
Suporta Português (pt) e Inglês (en) para todo o ecossistema de interface,
regras do jogo, HUD, controles e manuais estratégicos dos 12 guerreiros.
"""

LANG_PT = "pt"
LANG_EN = "en"

_current_lang = LANG_PT

def get_lang() -> str:
    return _current_lang

def set_lang(lang: str):
    global _current_lang
    if lang in (LANG_PT, LANG_EN):
        _current_lang = lang

def toggle_lang() -> str:
    global _current_lang
    _current_lang = LANG_EN if _current_lang == LANG_PT else LANG_PT
    return _current_lang

def t(key: str, **kwargs) -> str:
    """Retorna o texto localizado para a chave solicitada."""
    lang_dict = I18N.get(_current_lang, I18N[LANG_PT])
    text = lang_dict.get(key, I18N[LANG_PT].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

# Dicionário Geral de Textos (Padrão Boardbots const I18N = { pt: {...}, en: {...} })
I18N = {
    LANG_PT: {
        # Interface Geral & Seleção
        "select_title": "ESCOLHA SEU GUERREIRO",
        "btn_help": "[ H ] GUIA DO JOGO / AJUDA",
        "btn_start": "INICIAR DUELO (ENTER)",
        "mode_1p": "[1P vs IA] (TAB para 2P)",
        "mode_2p": "[2 JOGADORES] (P1: WASD | P2: Setas)",
        "guide_nav": "P1: [WASD] / Clique Esq   |   IA/P2: [Setas] / Clique Dir   |   [TAB]: Modo   |   [H]: Guia   |   [F/?]: Estratégia",
        "badge_p1": "[P1]",
        "badge_ia": "[IA]",
        "badge_p2": "[P2]",
        "change_warriors": "<< MUDAR GUERREIROS",
        "settings_btn": "[C] Controles / Settings",

        # HUD & Gameplay
        "mode_hud_1p": "[1P vs IA]",
        "mode_hud_2p": "[2 JOGADORES]",
        "arrows_label": "Setas",
        "powder_badge": "PÓLVORA",
        "powder_tracker": "PÓLVORA {dist:.1f}m",
        "draw_text": "EMPATE! (DOUBLE KO)",
        "victory_text": "VITÓRIA DE {name}!",
        "next_round_hint": "Pressione ESPAÇO para o próximo duelo ou ESC para trocar lutadores",

        # Modal de Ajuda - Cabeçalho e Abas
        "help_modal_title": "MANUAL DO GUERREIRO & GUIA DE COMBATE",
        "tab_rules": "1. REGRAS & MECÂNICAS",
        "tab_controls": "2. CONTROLES & MODOS",
        "tab_fighters": "3. GUIA DOS 12 GUERREIROS",
        "btn_prev": "< ANTERIOR",
        "btn_next": "PROXIMO >",
        "scroll_hint": "Roda do mouse ou teclas UP / DOWN para rolar",

        # Modal de Ajuda - Ficha de Guerreiro
        "stat_speed": "Velocidade:",
        "stat_damage": "Dano:",
        "stat_special": "Especial:",
        "stat_keys": "Comandos:",
        "sec_concept": "[ CONCEITO HISTÓRICO & TEMÁTICO ]",
        "sec_arsenal": "[ ARSENAL & HABILIDADES DE COMBATE ]",
        "sec_offense": "[ COMO JOGAR: ESTRATÉGIA OFENSIVA & POSICIONAMENTO ]",
        "sec_defense": "[ COMO VENCER: DEFESA, WHIFFS & PONTOS FRACOS ]",

        # Aba 1: Regras
        "rules_box1_title": "A FILOSOFIA DO DUELO",
        "rules_box1_lines": [
            "• Letalidade Rápida (1-Hit Kill): Na maioria das lutas,",
            "  um único corte limpo encerra o duelo. A paciência",
            "  e o respeito à lâmina são tudo.",
            "",
            "• Maai (Controle de Espaço): Manter a distância",
            "  correta da ponta da lâmina rival define quem",
            "  vive e quem tomba na terra sagrada.",
            "",
            "• Hyoshi (Cadência & Timing): Desferir um golpe",
            "  no ar (whiff) gera tempo de recuperação e deixa",
            "  você completamente vulnerável ao contra-ataque!",
            "",
            "• Cinema Samurai Noir: Golpes fatais disparam",
            "  o efeito Kurosawa com hitstop congelado,",
            "  flashes preto & branco e cortes físicos de voxels."
        ],
        "rules_box2_title": "PERIGOS DO CENÁRIO",
        "rules_box2_lines": [
            "• Floresta de Bambus: Caules de bambu cortáveis!",
            "  Investidas e lâminas ceifam bambus pelo caminho,",
            "  abrindo novas clareiras e ângulos de emboscada.",
            "",
            "• Obstáculos Rígidos (Rochas, Poço e Árvores):",
            "  Estruturas maciças inquebráveis. Bloqueiam a",
            "  passagem e fazem ataques ricochetearem com",
            "  faíscas, interrompendo avanços e tiros.",
            "",
            "• O Lago & a Ponte de Madeira: Terreno de água",
            "  afoga ou desacelera dramaticamente combatentes.",
            "  A ponte central estreita funciona como funil",
            "  mortal onde recuos são quase impossíveis."
        ],
        "rules_box3_title": "SISTEMAS DE COMBATE",
        "rules_box3_lines": [
            "• Ataque Primário [E] vs Ação Secundária [R]:",
            "  Todo guerreiro equilibra um ataque mortal e uma",
            "  ferramenta tática (dash, parry, recarga, cão).",
            "",
            "• Sistema de Precedência: Certos golpes velozes",
            "  (como a Kusarigama) têm prioridade absoluta",
            "  sobre investidas lentas.",
            "",
            "• Efeitos de Status:",
            "  - Stun: Paralisa por frações de segundo.",
            "  - Veneno (Okuni): Contagem regressiva fatal de 10s!",
            "  - Cegueira: Lenta o oponente na névoa de pólvora.",
            "",
            "• Pólvora na Arena: Marcada por SETAS DOURADAS,",
            "  indispensável para o arcabuz do Teppo!"
        ],

        # Aba 2: Controles
        "ctrl_p1_title": "CONTROLES DE COMBATE",
        "ctrl_p1_lines": [
            ("[ JOGADOR 1 (VOCÊ) ]", "header"),
            ("  • W / A / S / D : Movimento no Plano Isométrico 2.5D", "body"),
            ("  • [ E ] : Ataque Primário (Golpe mortal, disparo ou flecha)", "body_e"),
            ("  • [ R ] : Ação Secundária (Dash, Parry, Kunai, Cão, Fumaça)", "body_r"),
            ("", "sep"),
            ("[ JOGADOR 2 / OPONENTE ]", "header2"),
            ("  • SETAS (↑, ←, ↓, →) : Movimentação no Cenário", "body"),
            ("  • [ U ] : Ataque Primário", "body_e"),
            ("  • [ I ] : Ação Secundária / Especial / Parry", "body_r"),
            ("", "sep"),
            ("[ DICA DE MIRA TÁTICA ]", "tip"),
            ("  Segure os direcionais para mirar estocadas, projéteis ou", "body_dim"),
            ("  Gatotsu na direção desejada antes de apertar a tecla!", "body_dim")
        ],
        "ctrl_p2_title": "ATALHOS & GERENCIAMENTO",
        "ctrl_p2_lines": [
            ("[ TECLA TAB ]", "key"),
            ("  Alterna instantaneamente entre Modo [1P vs IA] e", "body"),
            ("  Modo [2 Jogadores Local] na mesma máquina.", "body_dim"),
            ("", "sep"),
            ("[ TECLA C ]", "key"),
            ("  Abre o Menu de Configurações onde você pode remapear", "body"),
            ("  qualquer tecla de P1 ou P2 e ajustar preferências.", "body_dim"),
            ("", "sep"),
            ("[ TECLA H ]", "key"),
            ("  Abre ou fecha este Manual Completo de Ajuda e Dicas.", "body"),
            ("", "sep"),
            ("[ TECLA F ou Clique em '?' ]", "key"),
            ("  Abre a Ficha Estratégica detalhada do lutador selecionado.", "body"),
            ("", "sep"),
            ("[ ESPAÇO / ENTER ]", "key_action"),
            ("  Inicia o Duelo após a escolha dos guerreiros.", "body")
        ]
    },

    LANG_EN: {
        # General UI & Selection
        "select_title": "CHOOSE YOUR WARRIOR",
        "btn_help": "[ H ] GAME GUIDE / HELP",
        "btn_start": "START DUEL (ENTER)",
        "mode_1p": "[1P vs AI] (TAB for 2P)",
        "mode_2p": "[2 PLAYERS] (P1: WASD | P2: Arrows)",
        "guide_nav": "P1: [WASD] / Left-Click   |   AI/P2: [Arrows] / Right-Click   |   [TAB]: Mode   |   [H]: Help   |   [F/?]: Strategy",
        "badge_p1": "[P1]",
        "badge_ia": "[AI]",
        "badge_p2": "[P2]",
        "change_warriors": "<< CHANGE WARRIORS",
        "settings_btn": "[C] Controls / Settings",

        # HUD & Gameplay
        "mode_hud_1p": "[1P vs AI]",
        "mode_hud_2p": "[2 PLAYERS]",
        "arrows_label": "Arrows",
        "powder_badge": "POWDER",
        "powder_tracker": "POWDER {dist:.1f}m",
        "draw_text": "DRAW! (DOUBLE KO)",
        "victory_text": "VICTORY: {name}!",
        "next_round_hint": "Press SPACE for next duel or ESC to switch warriors",

        # Help Modal - Header and Tabs
        "help_modal_title": "WARRIOR MANUAL & COMBAT GUIDE",
        "tab_rules": "1. RULES & MECHANICS",
        "tab_controls": "2. CONTROLS & MODES",
        "tab_fighters": "3. 12 WARRIORS GUIDE",
        "btn_prev": "< PREVIOUS",
        "btn_next": "NEXT >",
        "scroll_hint": "Mouse wheel or UP / DOWN keys to scroll",

        # Help Modal - Warrior Profile
        "stat_speed": "Speed:",
        "stat_damage": "Damage:",
        "stat_special": "Special:",
        "stat_keys": "Controls:",
        "sec_concept": "[ HISTORICAL & THEMATIC CONCEPT ]",
        "sec_arsenal": "[ COMBAT ARSENAL & ABILITIES ]",
        "sec_offense": "[ HOW TO PLAY: OFFENSIVE STRATEGY & POSITIONING ]",
        "sec_defense": "[ HOW TO COUNTER: DEFENSE, WHIFFS & WEAKNESSES ]",

        # Tab 1: Rules
        "rules_box1_title": "PHILOSOPHY OF THE DUEL",
        "rules_box1_lines": [
            "• Sudden Lethality (1-Hit Kill): In most clashes,",
            "  a single clean slash ends the duel. Patience",
            "  and reverence for the blade are everything.",
            "",
            "• Maai (Spatial Spacing): Maintaining the exact",
            "  distance from your rival's blade tip determines",
            "  who survives and who falls on sacred soil.",
            "",
            "• Hyoshi (Cadence & Timing): Swinging into thin air",
            "  (whiffing) incurs recovery frames and leaves",
            "  you completely vulnerable to a lethal counter!",
            "",
            "• Kurosawa Noir Cinema: Fatal blows trigger the",
            "  dramatic Kurosawa effect with frozen hitstop,",
            "  black & white flashes and voxel slicing."
        ],
        "rules_box2_title": "ARENA HAZARDS",
        "rules_box2_lines": [
            "• Bamboo Grove: Cuttable bamboo stalks! Dashes and",
            "  slashes sever stalks along their path, creating",
            "  new clearings and tactical ambush angles.",
            "",
            "• Solid Obstacles (Rocks, Stone Well & Trees):",
            "  Massive unbreakable cover. They block movement",
            "  and cause blades to ricochet with bright sparks,",
            "  interrupting charging lunges and projectiles.",
            "",
            "• The Lake & Wooden Bridge: Deep water drowns or",
            "  drastically slows combatants. The narrow central",
            "  bridge acts as a deadly choke point where retreat",
            "  is practically impossible."
        ],
        "rules_box3_title": "COMBAT SYSTEMS",
        "rules_box3_lines": [
            "• Primary Attack [E] vs Secondary Action [R]:",
            "  Every warrior balances a lethal weapon strike with",
            "  a tactical utility (dash, parry, reload, dog).",
            "",
            "• Precedence Priority: High-speed strikes",
            "  (such as Murasaki's Kusarigama) hold absolute",
            "  priority over slower charging attacks.",
            "",
            "• Status Effects:",
            "  - Stun: Freezes the foe for critical fractions of a sec.",
            "  - Poison (Okuni): 10-second countdown to fatal death!",
            "  - Gunpowder Blind: Blinds & heavily slows opponent.",
            "",
            "• Gunpowder Kegs: Highlighted by FLOATING GOLD ARROWS,",
            "  vital for Teppo to reload his deadly tanegashima!"
        ],

        # Tab 2: Controls
        "ctrl_p1_title": "COMBAT CONTROLS",
        "ctrl_p1_lines": [
            ("[ PLAYER 1 (YOU) ]", "header"),
            ("  • W / A / S / D : Movement in 2.5D Isometric Space", "body"),
            ("  • [ E ] : Primary Attack (Lethal slash, shot or arrow)", "body_e"),
            ("  • [ R ] : Secondary Action (Dash, Parry, Kunai, Dog, Smoke)", "body_r"),
            ("", "sep"),
            ("[ PLAYER 2 / OPPONENT ]", "header2"),
            ("  • ARROWS (↑, ←, ↓, →) : Movement Across the Arena", "body"),
            ("  • [ U ] : Primary Attack", "body_e"),
            ("  • [ I ] : Secondary Action / Special / Parry", "body_r"),
            ("", "sep"),
            ("[ TACTICAL AIMING TIP ]", "tip"),
            ("  Hold movement directionals to steer lunges, projectiles", "body_dim"),
            ("  or Gatotsu charge before pressing attack keys!", "body_dim")
        ],
        "ctrl_p2_title": "SYSTEM SHORTCUTS",
        "ctrl_p2_lines": [
            ("[ TAB KEY ]", "key"),
            ("  Instantly toggles between [1P vs AI] Mode and", "body"),
            ("  [2 Players Local] Mode on the same machine.", "body_dim"),
            ("", "sep"),
            ("[ C KEY ]", "key"),
            ("  Opens Settings Menu to remap keys for P1 or P2", "body"),
            ("  and customize gameplay preferences.", "body_dim"),
            ("", "sep"),
            ("[ H KEY ]", "key"),
            ("  Opens or closes this Full Game Guide & Manual.", "body"),
            ("", "sep"),
            ("[ F KEY or Click '?' ]", "key"),
            ("  Opens the detailed Strategy Guide for focused warrior.", "body"),
            ("", "sep"),
            ("[ SPACE / ENTER ]", "key_action"),
            ("  Starts the Duel after choosing combatants.", "body")
        ]
    }
}
