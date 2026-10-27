"""
Banco de dados estratégico dos 24 Combatentes de Samurai Edge (Bilíngue PT/EN).
Cada ficha segue rigorosamente o padrão de dissecação técnica:
- Identidade marcial, HP, velocidade, alcance, tempo de recuperação
- Lore e papel na guerra do Bakumatsu e conspiração do Gashadokuro
- Tabela de comandos (Gamepad Universal + Teclado P1/P2)
- Análise aprofundada de armas e mecânicas próprias
- Ciclo de Vitória (Plano de jogo passo a passo em 3 Fases)
- Estratégia Defensiva (Como Vencer)
"""

FIGHTERS_DATA = [
    # 1. KENSHI
    {
        "id": "kenshin",
        "name_pt": "KENSHI",
        "name_en": "KENSHI",
        "title_pt": "O Retalhador do Crepúsculo",
        "title_en": "The Twilight Battousai",
        "faction_pt": "1. Protetores do Povo & Ronins Virtuosos",
        "faction_en": "1. Protectors of the People & Virtuous Ronin",
        "hp": 2,
        "speed": "5.00 m/s (Velocidade Máxima)",
        "reach_pt": "Médio-Longo (Estocada de Saque Frontal)",
        "reach_en": "Medium-Long (Frontal Quick-Draw)",
        "style_pt": "Hiten Mitsurugi-ryu (Iaijutsu & Battojutsu de Saque Veloz)",
        "style_en": "Hiten Mitsurugi-ryu (Swift Draw Iaijutsu & Battojutsu)",
        "concept_art": "assets/concepts/kenshi_full_concept.jpg",
        "bust_art": "assets/portraits/kenshi_bust.png",
        "lore_pt": (
            "Veterano das primeiras guerras de Kyoto, Kenshi empunhava uma lâmina de sangue até perceber "
            "que as mortes inocentes alimentavam algo sinistro nas profundezas da terra. Renegou os senhores feudais "
            "e jurou proteger os camponeses indefesos contra os saques do Bakumatsu. Sua técnica foca na velocidade "
            "suprema do desembainhar, decidindo o duelo em um único instante de silêncio mortal."
        ),
        "lore_en": (
            "A scarred veteran of the early Kyoto skirmishes, Kenshi once wielded a blood-soaked blade until recognizing "
            "that innocent slaughter fed an ancient horror stirring beneath the soil. Forsaking all feudal masters, he swore "
            "to defend helpless villagers from the chaos of the Bakumatsu. His art relies on supreme drawing speed, deciding "
            "fatal duels in a single breath of razor-sharp stillness."
        ),
        "moveset_pt": [
            ("Iai Flash (Saque Letal)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Saque frontal fulminante com corte limpo. Decapita oponente e corta bambus do cenário."),
            ("Shukuchi Dash", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Investida instantânea com zanzo (pós-imagens). Fecha distância e corta ângulos cegos."),
            ("Parry de Bainha", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Deflexão precisa usando a curva da saya. Reflete projéteis e desvia estocadas."),
            ("Esquiva Ágil", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Rolamento acrobático rente ao solo com recuperação ultrarrápida.")
        ],
        "moveset_en": [
            ("Iai Flash (Lethal Draw)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Blistering frontal quick-draw slash. Cleanly severs foes and bamboo thickets."),
            ("Shukuchi Dash", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Instantaneous shadow dash leaving afterimages. Closes gaps and flanks blind spots."),
            ("Sheath Parry", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Precise saya deflection. Parries thrusts and reflects incoming arrows."),
            ("Agile Roll", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Low-profile tumbling evasion with ultra-fast recovery frames.")
        ],
        "weapons_pt": (
            "O Iai Flash possui um dos tempos de iniciação mais rápidos do jogo (0.08s). Durante a animação de embainhar (Noto), "
            "Kenshi pode se movimentar livremente a 60% da velocidade, preparando o próximo saque. O Shukuchi Dash permite atravessar "
            "o alcance de projéteis e reaparecer colado ao oponente."
        ),
        "weapons_en": (
            "Iai Flash features one of the fastest startup frames in the roster (0.08s). During the resheathing animation (Noto), "
            "Kenshi retains 60% walking mobility to reset spacing. Shukuchi Dash bypasses incoming ranged projectiles and repositions "
            "instantly within lethal striking distance."
        ),
        "gameplan_pt": (
            "• Fase 1 (Zoneamento): Mantenha distância média de 3 metros, rondando o rival e esperando qualquer whiff de golpe.\n"
            "• Fase 2 (Aproximação Shukuchi): No instante em que o oponente errar o tempo de um ataque ou atirar um projétil, use o Shukuchi para fechar a lacuna.\n"
            "• Fase 3 (Execução Iai): Dispare o Iai Flash na linha reta do oponente para garantir a morte instantânea em 1 acerto."
        ),
        "gameplan_en": (
            "• Phase 1 (Spacing): Circle at mid-range (3 meters), baiting errant swings while tracking the enemy's attack cadence.\n"
            "• Phase 2 (Shukuchi Engagement): The moment the foe misses a thrust or commits to a shot, trigger Shukuchi Dash to close the gap.\n"
            "• Phase 3 (Iai Execution): Release Iai Flash straight along their centerline for a lethal single-strike finish."
        ),
        "how_to_beat_pt": (
            "O Iai Flash possui uma linha de corte estreita e requer embainhamento prévio. Flanqueie Kenshi pelas diagonais com rolamentos rápidos "
            "ou use armas de arco amplo (como a Naginata de Benkei ou a Foice de Murasaki) para puni-lo no momento do Noto."
        ),
        "how_to_beat_en": (
            "Iai Flash has a strictly linear hitbox and requires a brief resheathing window. Flank Kenshi diagonally with agile evasions "
            "or exploit wide sweeping arcs (like Benkei's Naginata or Murasaki's Scythe) during his Noto recovery."
        )
    },

    # 2. MUSASHI
    {
        "id": "musashi",
        "name_pt": "MUSASHI",
        "name_en": "MUSASHI",
        "title_pt": "O Santo da Espada Dupla",
        "title_en": "The Dual-Blade Sword Saint",
        "faction_pt": "2. Duelistas do Auge & Buscadores de Glória",
        "faction_en": "2. Peak Duelists & Glory Seekers",
        "hp": 2,
        "speed": "4.30 m/s (Cadência Equilibrada)",
        "reach_pt": "Médio (Katana Daito) & Curto (Wakizashi Shoto)",
        "reach_en": "Medium (Katana Daito) & Short (Wakizashi Shoto)",
        "style_pt": "Niten Ichi-ryu (Duas Espadas sob o Mesmo Céu)",
        "style_en": "Niten Ichi-ryu (Two Swords as One Heaven)",
        "concept_art": "assets/concepts/musashi_full_concept.jpg",
        "bust_art": "assets/portraits/musashi_bust.png",
        "lore_pt": (
            "Inconformado com as restrições da esgrima clássica, Musashi percorre os campos de batalha do Bakumatsu "
            "empunhando a katana na destra e a wakizashi na canhota. Para ele, o despertar de guerreiros míticos e abominações "
            "é a oportunidade definitiva para coroar o estilo Niten Ichi-ryu como a arte marcial invicta na história japonesa."
        ),
        "lore_en": (
            "Unbound by classical fencing dogma, Musashi wanders the Bakumatsu battlegrounds wielding a katana in his right hand "
            "and a wakizashi in his left. To his relentless spirit, the awakening of ancient horrors and mythical swordsmen represents "
            "the ultimate crucible to prove Niten Ichi-ryu as the supreme martial art in history."
        ),
        "moveset_pt": [
            ("Corte Duplo Niten", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Combo rápido de duas lâminas: golpe descendente de katana seguido por estocada ascendente de wakizashi."),
            ("Contra-Golpe Cruzado (Cross Counter)", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Parry ofensivo imediato: cruza as duas lâminas e desfere retaliação instantânea letal."),
            ("Bloqueio Niten Ichi", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Guarda frontal dupla com absorção de impacto e resistência a quebra de postura."),
            ("Passo Flutuante (Hyoho)", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Esquiva lateral curta que mantém a ponta das duas lâminas sempre apontadas para a garganta do rival.")
        ],
        "moveset_en": [
            ("Niten Double Slash", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Two-hit blade chain: downward katana cut followed by upward wakizashi riposte."),
            ("Cross Counter Stance", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Immediate offensive parry: crosses dual blades and retaliates with an instantaneous fatal cross-slash."),
            ("Dual Blade Block", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Double frontal guard with enhanced impact absorption and high poise."),
            ("Floating Stride (Hyoho)", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Lateral evasive pivot that keeps dual weapon tips locked on the foe's throat.")
        ],
        "weapons_pt": (
            "Musashi possui a maior taxa de sucesso em contra-ataques do jogo. Seu Cross Counter [R] absorve ataques frontais "
            "e desfecha dano letal sem necessidade de confirmação prévia de parry. O segundo golpe do combo tem hitbox ampla."
        ),
        "weapons_en": (
            "Musashi boasts the highest counter-attack conversion rate in the game. His Cross Counter [R] absorbs frontal strikes "
            "and delivers an instant lethal riposte. The second swing of his normal chain features extended horizontal coverage."
        ),
        "gameplan_pt": (
            "• Fase 1 (Pressão Contida): Avance com pequenos passos, forçando o adversário a atacar por impulso.\n"
            "• Fase 2 (Bait de Contra-Ataque): Arme o Cross Counter no momento em que o rival iniciar a animação de ataque.\n"
            "• Fase 3 (Finalização Niten): Se o rival tentar defender, use a estocada de wakizashi para quebrar o ritmo e finalizar."
        ),
        "gameplan_en": (
            "• Phase 1 (Controlled Pressure): Advance steadily with micro-steps, coaxing the opponent into desperate swings.\n"
            "• Phase 2 (Counter Bait): Trigger Cross Counter right as the foe winds up their primary attack.\n"
            "• Phase 3 (Niten Finish): If the foe retreats or turtle-blocks, crack their guard with the wakizashi follow-up."
        ),
        "how_to_beat_pt": (
            "O Cross Counter só funciona contra ataques que venham frontalmente. Nunca ataque Musashi de frente quando ele hesitar; "
            "role para suas costas ou use projéteis de longa distância (Yumi de Tomoe, Frascos de Hendrika) para puni-lo de longe."
        ),
        "how_to_beat_en": (
            "Cross Counter only guards frontal angles. Never strike Musashi head-on when he stands still; "
            "flank behind him with rolling steps or deploy ranged artillery (Tomoe's Yumi, Hendrika's Flasks) to punish him outside reach."
        )
    },

    # 3. HANZO
    {
        "id": "ninja",
        "name_pt": "HANZO",
        "name_en": "HANZO",
        "title_pt": "O Grão-Mestre Shinobi de Iga",
        "title_en": "Grandmaster Shinobi of Iga",
        "faction_pt": "6. Os Guardiões do Selo (Clã Shinobi de Iga)",
        "faction_en": "6. Guardians of the Seal (Iga Shinobi Clan)",
        "hp": 2,
        "speed": "4.85 m/s (Hiper-Mobilidade)",
        "reach_pt": "Médio (Ninjato de Aço Escuro) & Longo (Kunai Sniper)",
        "reach_en": "Medium (Dark-Steel Ninjato) & Long (Sniper Kunai)",
        "style_pt": "Iga-ryu Ninjutsu (Lâmina Oculta & Acrobacias Aéreas)",
        "style_en": "Iga-ryu Ninjutsu (Hidden Blade & Aerial Acrobatics)",
        "concept_art": "assets/concepts/hanzo_full_concept.jpg",
        "bust_art": "assets/portraits/hanzo_bust.png",
        "lore_pt": (
            "Líder supremo dos ninjas guardiões, Hanzo sabe que a lenda do Gashadokuro não é mito, mas uma catástrofe que seu clã "
            "jurou conter por gerações. Protegendo a Caverna Sombria sob a capa da noite, ele elimina qualquer intruso que se aproxime "
            "do selo, mesmo que para isso precise carregar a pecha de assassino frio aos olhos do Japão."
        ),
        "lore_en": (
            "Supreme leader of the guardian shinobi, Hanzo knows the tale of Gashadokuro is no mere folklore, but an apocalyptic titan "
            "his clan has guarded for centuries. Protecting the Shadow Cave under the veil of night, he eliminates any trespasser nearing "
            "the seal, willingly bearing the stigma of a cold-blooded assassin to keep Japan safe."
        ),
        "moveset_pt": [
            ("Corte Ninjato", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Golpe horizontal veloz com a espada reta de Iga. Rápida recuperação e corte limpo."),
            ("Salto Parabólico & Kunai Snipe", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Salto acrobático alto que passa por cima de buracos e dispara uma kunai precisa em pleno ar."),
            ("Guarda Shinobi", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Defesa compacta com lâmina invertida."),
            ("Passo das Sombras (Shunshin)", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Esquiva evasiva ultraveloz com dispersão de folhas e cinzas escuras.")
        ],
        "moveset_en": [
            ("Ninjato Slash", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Swift horizontal cleave with the straight Iga blade. Extremely short recovery window."),
            ("Parabolic Leap & Kunai Snipe", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "High aerial vault clearing ground hazards while launching a pinpoint kunai mid-flight."),
            ("Shinobi Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Reverse-grip compact defensive guard."),
            ("Shadow Step (Shunshin)", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Ultra-fast evasive roll scattering dark ash and leaves.")
        ],
        "weapons_pt": (
            "O Salto Parabólico [R] confere invulnerabilidade vertical completa a golpes terrestres e permite atravessar os fossos mais "
            "largos da arena Telhados de Iga. A kunai arremessada no ápice atordoa o rival por 0.40s, abrindo caminho para o abate na queda."
        ),
        "weapons_en": (
            "Parabolic Leap [R] grants full vertical immunity to ground swings and allows leaping across the widest chasms in Iga Rooftops. "
            "The kunai thrown at the apex stuns the target for 0.40s, setting up an unblockable descending execution."
        ),
        "gameplan_pt": (
            "• Fase 1 (Assédio Aéreo): Utilize o salto acrobático [R] para manter o rival desconfortável e escapar de investidas terrestres.\n"
            "• Fase 2 (Confirmação de Kunai): Acerte a kunai aérea para causar Stun momentâneo no oponente.\n"
            "• Fase 3 (Aterrissagem Fatal): Finalize imediatamente com o golpe de Ninjato assim que tocar o solo."
        ),
        "gameplan_en": (
            "• Phase 1 (Aerial Harassment): Use Parabolic Leap [R] to keep foes off-balance and clear ground hazards.\n"
            "• Phase 2 (Kunai Confirm): Land the aerial kunai to stagger the opponent with hitstun.\n"
            "• Phase 3 (Lethal Touchdown): Execute immediately with the Ninjato slash upon landing."
        ),
        "how_to_beat_pt": (
            "Acompanhe o arco de queda do Salto Parabólico. Hanzo fica vulnerável nos 0.15s imediatamente após aterrissar. Posicione-se "
            "no ponto de pouso com um golpe perfurante preparado."
        ),
        "how_to_beat_en": (
            "Track Hanzo's trajectory during the Parabolic Leap. He suffers a 0.15s landing recovery window upon touching the ground. "
            "Anticipate his landing coordinates with a pre-emptive thrust."
        )
    },

    # 4. JOE
    {
        "id": "american",
        "name_pt": "JOE",
        "name_en": "JOE",
        "title_pt": "O Operador Tático Viajante",
        "title_en": "The Time-Traveling Operator",
        "faction_pt": "7. O Viajante Temporal & Aliado Inusitado",
        "faction_en": "7. The Time Traveler & Unlikely Ally",
        "hp": 2,
        "speed": "4.55 m/s (Passo Militar Ágil)",
        "reach_pt": "Curto (Faca de Combate / Kunai) & Longo (Ataque de Cão Doberman)",
        "reach_en": "Short (Combat Knife / Kunai) & Long (Doberman Hound Strike)",
        "style_pt": "Táticas Especiais Militares & Ninjutsu Otaku",
        "style_en": "Modern Special Tactics & Otaku Ninjutsu",
        "concept_art": "assets/concepts/joe_full_concept.jpg",
        "bust_art": "assets/portraits/joe_bust.png",
        "lore_pt": (
            "Membro de forças especiais dos EUA e fã incorrigível de animes ninjas clássicos, Joe acabou transportado ao século XIX "
            "durante um experimento governamental sigiloso que deu errado. Fascinado por viver a era dos samurais reais, uniu-se a Hanzo "
            "e ao clã de Iga ao entender a gravidade do selo do Gashadokuro. Luta ao lado de seu leal cão de guerra Doberman e shurikens modernas."
        ),
        "lore_en": (
            "A modern special forces operative and diehard ninja anime enthusiast, Joe was flung back to 19th-century Japan "
            "during a classified temporal experiment gone awry. Thrilled to experience authentic samurai warfare, he pledged loyalty "
            "to Hanzo's clan upon realizing the cataclysmic stakes of the Gashadokuro seal. Fights alongside his trained Doberman hound."
        ),
        "moveset_pt": [
            ("Estocada de Faca Tática", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Golpe perfurante seco com faca militar / kunai. Extremamente veloz à queima-roupa."),
            ("Comando Doberman (Bote do Cão)", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Ordena ao seu Doberman um bote rasante que avança veloz pela arena, mordendo e derrubando o rival."),
            ("Bloqueio Tático", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Postura de defesa militar com antebraço e lâmina."),
            ("Rolamento Militar", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Rolamento tático rápido de combate.")
        ],
        "moveset_en": [
            ("Tactical Knife Thrust", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Crisp military combat knife / kunai stab. Lethal at point-blank range."),
            ("Doberman Charge Order", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Commands his tactical Doberman hound to sprint across the arena and tackle the target to the ground."),
            ("Tactical Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Close-quarters defensive stance with reinforced forearm block."),
            ("Combat Roll", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Crisp evasive military dive-roll.")
        ],
        "weapons_pt": (
            "O Doberman de Joe é um projétil vivo imparável. Quando o cão atinge o rival, causa 1 de dano e aplica Stun de derrubada (Knockdown) "
            "por 0.80s, permitindo que Joe corra em linha reta para executar o rival caído no chão com a faca tática."
        ),
        "weapons_en": (
            "Joe's Doberman acts as a living homing projectile. Upon connecting, the hound deals 1 damage and inflicts an 0.80s knockdown stun, "
            "allowing Joe to sprint in and execute the grounded foe with his tactical combat blade."
        ),
        "gameplan_pt": (
            "• Fase 1 (Envio do Cão): Mantenha distância segura e acione o Comando Doberman [R] para interceptar o movimento do rival.\n"
            "• Fase 2 (Avanço no Knockdown): No momento em que o cão derrubar o rival, avance em velocidade máxima.\n"
            "• Fase 3 (Estocada Final): Golpeie com a faca tática [E] antes que o oponente se recupere da queda."
        ),
        "gameplan_en": (
            "• Phase 1 (Hound Deployment): Hang back safely and unleash the Doberman Command [R] to cut off enemy approaches.\n"
            "• Phase 2 (Knockdown Rush): The instant the hound pins the foe, sprint forward at full speed.\n"
            "• Phase 3 (Execution Stab): Strike with the tactical knife [E] before the opponent recovers from the ground."
        ),
        "how_to_beat_pt": (
            "O Doberman avança em linha reta previsível. Um golpe cortante de ampla abertura (como o Cutlass da Anne ou o Golpe de Kuwa do Goro) "
            "atinge e afugenta o cão antes do impacto, deixando Joe desprotegido."
        ),
        "how_to_beat_en": (
            "The Doberman charges in a predictable straight trajectory. A wide horizontal cleave (such as Anne's Cutlass or Goro's Kuwa swing) "
            "swipes the hound aside mid-charge, leaving Joe completely exposed."
        )
    },

    # 5. SAITOU
    {
        "id": "saitou",
        "name_pt": "SAITOU",
        "name_en": "SAITOU",
        "title_pt": "O Lobo Solitário de Mibu",
        "title_en": "The Lone Wolf of Mibu",
        "faction_pt": "3. Lealistas & Servidores da Ordem",
        "faction_en": "3. Loyalists & Order Keepers",
        "hp": 2,
        "speed": "4.45 m/s (Caminhada Predatória)",
        "reach_pt": "Longo (Investida Estocada Gatotsu)",
        "reach_en": "Long (Gatotsu Penetrating Charge)",
        "style_pt": "Mizo-ryu & Shinsengumi Kenjutsu (Gatotsu Letal de Canhota)",
        "style_en": "Mizo-ryu & Shinsengumi Kenjutsu (Left-Handed Lethal Gatotsu)",
        "concept_art": "assets/concepts/saitou_full_concept.jpg",
        "bust_art": "assets/portraits/saitou_bust.png",
        "lore_pt": (
            "Capitão da terceira divisão do temido Shinsengumi. Saitou é a encarnação do lema 'Aku Soku Zan' (Eliminar o Mal Imediatamente). "
            "Fiel servidor da lei e da ordem em Kyoto, vê os traidores do Xogunato e os conspiradores místicos como ameaças que devem ser "
            "perfuradas sem piedade. Sua estocada de mão esquerda é uma das armas mais letais de todo o período Bakumatsu."
        ),
        "lore_en": (
            "Captain of the Shinsengumi's 3rd Unit, Saitou embodies the ruthless code of 'Aku Soku Zan' (Slay Evil Immediately). "
            "A steadfast enforcer of law and order in Kyoto, he treats rebels and dark occultists alike as vermin to be impaled without mercy. "
            "His left-handed thrust is among the most lethal martial techniques of the Bakumatsu era."
        ),
        "moveset_pt": [
            ("Gatotsu Ishiki (Investida Frontal)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Estocada horizontal penetrante disparada pela mão esquerda. Avança em altíssima velocidade atravessando defesas."),
            ("Gatotsu Zeroshiki (Quebra-Guarda à Queima-Roupa)", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Estocada sem recuo executada com o corpo colado. Quebra parries e mata instantaneamente sem windup."),
            ("Bloqueio de Lobo", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Guarda horizontal rígida com haori azul do Shinsengumi."),
            ("Recuo Predatório", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Passo evasivo para trás seguido de rearme de postura.")
        ],
        "moveset_en": [
            ("Gatotsu Ishiki (Charging Thrust)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Left-handed piercing charge propelled with explosive speed, shattering loose guards."),
            ("Gatotsu Zeroshiki (Point-Blank Crush)", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Zero-distance instant thrust without startup windup. Crushes parries and kills at point-blank."),
            ("Wolf's Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Rigid horizontal blade stance draped in Shinsengumi blue."),
            ("Predatory Backstep", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Defensive evasive backstep instantly re-priming the Gatotsu stance.")
        ],
        "weapons_pt": (
            "O Gatotsu Ishiki [E] tem alcance de quase 4 metros e aceleração instantânea de 14.0 m/s. Se o rival tentar defender com parry, "
            "o Zeroshiki [R] à queima-roupa quebra a guarda instantaneamente com 1-Hit Kill."
        ),
        "weapons_en": (
            "Gatotsu Ishiki [E] spans nearly 4 meters of range with 14.0 m/s sprint acceleration. If the enemy turtles behind a parry, "
            "Zeroshiki [R] at point-blank range crushes the defense outright with an instant 1-Hit Kill."
        ),
        "gameplan_pt": (
            "• Fase 1 (Alinhamento de Mira): Posicione-se rigorosamente na mesma linha axial do oponente.\n"
            "• Fase 2 (Disparo do Gatotsu): Acione o Gatotsu Ishiki no momento em que o oponente iniciar um passo ou whiff.\n"
            "• Fase 3 (Zeroshiki de Fechamento): Em situações coladas onde o rival ergue a guarda, solte o Zeroshiki para finalizar."
        ),
        "gameplan_en": (
            "• Phase 1 (Axis Alignment): Position yourself strictly along the same axial plane as the opponent.\n"
            "• Phase 2 (Gatotsu Release): Launch Gatotsu Ishiki the moment the enemy commits to a stride or whiff.\n"
            "• Phase 3 (Zeroshiki Clinch): In close quarters against a guarding foe, release Zeroshiki to end the round."
        ),
        "how_to_beat_pt": (
            "O Gatotsu avança estritamente em linha reta e ricocheteia se atingir rochas, carruagens ou paredes de Kyoto. "
            "Mantenha-se nas diagonais com esquivas laterais e contra-ataque durante a recuperação da estocada."
        ),
        "how_to_beat_en": (
            "Gatotsu travels in a strict linear line and sparks harmlessly off rocks, carts, or walls in Kyoto. "
            "Circle diagonally with side rolls and strike his exposed flank during thrust recovery."
        )
    },

    # 6. TEPPO
    {
        "id": "rifleman",
        "name_pt": "TEPPO",
        "name_en": "TEPPO",
        "title_pt": "O Atirador de Tanegashima",
        "title_en": "The Tanegashima Marksman",
        "faction_pt": "5. Mercenários & Corsários de Guerra",
        "faction_en": "5. Mercenaries & War Corsairs",
        "hp": 2,
        "speed": "4.20 m/s (Caminhada Cadenciada com Arcabuz)",
        "reach_pt": "Infinito (Projétil de Arcabuz) & Curto (Coronhada de Carvalho)",
        "reach_en": "Infinite (Matchlock Shot) & Short (Oak Stock Strike)",
        "style_pt": "Hojutsu (Tiro Tradicional de Arcabuz & Artilharia Leve)",
        "style_en": "Hojutsu (Matchlock Gunnery & Tactical Artillery)",
        "concept_art": "assets/concepts/teppo_full_concept.jpg",
        "bust_art": "assets/portraits/teppo_bust.png",
        "lore_pt": (
            "Mestre atirador experiente nas guerras entre os clãs feudais. Teppo não acredita em mitos ou códigos de honra samurai: "
            "para ele, a pólvora negra é o grande equalizador da história. Vende sua pontaria ao melhor pagador durante o Bakumatsu, "
            "recolhendo suprimentos de pólvora nos campos de batalha para manter seu arcabuz de mecha sempre letal."
        ),
        "lore_en": (
            "A seasoned marksman tempered in the wars between feudal clans, Teppo places no faith in myths or samurai honor codes: "
            "to his eyes, black powder is history's ultimate equalizer. Selling his deadly marksmanship to the highest bidder in the Bakumatsu, "
            "he scavenges powder horns from battlefields to ensure his heavy matchlock gun remains primed and lethal."
        ),
        "moveset_pt": [
            ("Tiro Letal de Tanegashima", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Disparo ensurdecedor de mecha que viaja toda a extensão da arena. 1-Hit Kill instantâneo. Consome pólvora."),
            ("Coronhada Pesada / Recarga", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Golpe contundente com a coronha de carvalho reforçada (quebra parry e afasta) ou recarrega cartucho se houver pólvora."),
            ("Guarda com Arcabuz", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Bloqueio com o cano de ferro do rifle."),
            ("Salto para Trás de Desengajamento", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Salto evasivo recuando enquanto aponta a boca da arma para frente.")
        ],
        "moveset_en": [
            ("Lethal Matchlock Shot", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Deafening gunshot spanning the entire arena. 1-Hit Kill on connection. Consumes powder."),
            ("Stock Strike / Reload", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Heavy strike with reinforced oak stock (knocks back and staggers) or reloads powder if pouches are collected."),
            ("Rifle Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Heavy iron barrel defensive deflection."),
            ("Disengaging Leap", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Backwards evasive leap maintaining weapon aim towards the opponent.")
        ],
        "weapons_pt": (
            "O tiro de Tanegashima é 100% imparável em linha reta por defesas comuns. A coronhada [R] afasta oponentes que colarem no corpo a corpo "
            "e aplica Stun, concedendo o tempo exato para coletar sacos de pólvora caídos na arena."
        ),
        "weapons_en": (
            "The Tanegashima bullet is unblockable along its line of fire by ordinary parries. His heavy stock strike [R] repels rushing foes "
            "and inflicts stun, granting the critical window needed to snatch powder horns scattered across the arena."
        ),
        "gameplan_pt": (
            "• Fase 1 (Tiro Inicial): Comece o round alinhando a mira para disparar a bala inicial carregada.\n"
            "• Fase 2 (Coleta de Pólvora): Após atirar, use a mobilidade e a coronhada para afastar o rival e coletar pólvora flutuante.\n"
            "• Fase 3 (Recarga e Finalização): Recarregue com [R] em zona segura e desfeche o segundo tiro fatal."
        ),
        "gameplan_en": (
            "• Phase 1 (Opening Shot): Begin the round locking aim to discharge the pre-loaded matchlock round.\n"
            "• Phase 2 (Powder Scavenge): After firing, use agile leaps and stock strikes to fend off rushes and grab powder pouches.\n"
            "• Phase 3 (Reload & Execution): Prime the rifle safely and deliver the decisive second shot."
        ),
        "how_to_beat_pt": (
            "Não dê espaço para Teppo recarregar! Pressione-o desde o primeiro segundo com aproximação em zigue-zague e rolamentos diagonais. "
            "Quando ele estiver descarregado, seu alcance efetivo se reduz à coronha."
        ),
        "how_to_beat_en": (
            "Never give Teppo breathing room to reload! Smother him with zig-zagging dashes and diagonal rolls from second zero. "
            "When unloaded, his combat range collapses entirely to point-blank stock bashes."
        )
    },

    # 7. MURASAKI
    {
        "id": "purple",
        "name_pt": "MURASAKI",
        "name_en": "MURASAKI",
        "title_pt": "A Kunoichi da Foice Sombria",
        "title_en": "The Shadow Sickle Kunoichi",
        "faction_pt": "6. Os Guardiões do Selo (Clã Shinobi de Iga)",
        "faction_en": "6. Guardians of the Seal (Iga Shinobi Clan)",
        "hp": 2,
        "speed": "4.65 m/s (Passo Sinuoso de Serpente)",
        "reach_pt": "Longo (Corrente de Ferro) & Médio (Kama Curva)",
        "reach_en": "Long (Iron Chain Link) & Medium (Curved Kama)",
        "style_pt": "Kusarigamajutsu de Iga (Precedência Absoluta de Corte)",
        "style_en": "Iga Kusarigamajutsu (Absolute Precedence Sickle)",
        "concept_art": "assets/concepts/murasaki_full_concept.jpg",
        "bust_art": "assets/portraits/murasaki_bust.png",
        "lore_pt": (
            "Guardiã direta da entrada da Caverna Sombria. Murasaki tece suas correntes de ferro na escuridão para capturar "
            "qualquer samurai que ouse perturbar o sono do Gashadokuro. Sua foice curva carrega o princípio marcial da Precedência Absoluta: "
            "quando golpeia simultaneamente com outro atacante, sua lâmina corta primeiro, ceifando a vida do adversário sem choque."
        ),
        "lore_en": (
            "Direct sentinel of the Shadow Cave threshold, Murasaki weaves iron chains through the dark to snare any warrior "
            "daring to disturb the Gashadokuro's crypt. Her curved sickle embodies Absolute Precedence: in simultaneous strikes, "
            "her scythe cuts first without entering weapon clash, claiming the rival's life in mid-motion."
        ),
        "moveset_pt": [
            ("Corte de Foice (Precedência Absoluta)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Arco cortante de foice que vence qualquer ataque simultâneo com prioridade matemática. Mata na hora."),
            ("Arremesso de Corrente & Puxão", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Lança a corrente de ferro pesada a até 5.5 metros, puxando o rival em sua direção desarmado e atordoado."),
            ("Defesa de Corrente Giratória", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Gira a corrente em círculo vertical, criando um escudo impenetrável contra projéteis e estocadas."),
            ("Deslize de Sombra", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Esquiva rasteira sinuosa.")
        ],
        "moveset_en": [
            ("Scythe Cleave (Absolute Priority)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Curved sickle arc boasting mathematical strike priority over simultaneous blows. 1-Hit Kill."),
            ("Chain Throw & Harpoon Reel", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Hurls weighted iron chain up to 5.5m, dragging the staggered rival directly into striking range."),
            ("Spinning Chain Shield", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Spins the chain in a vertical vortex, deflecting all incoming projectiles and thrusts."),
            ("Shadow Glide", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Low, serpentine sliding evasion.")
        ],
        "weapons_pt": (
            "A foice de Murasaki ignora a regra de Clash QTE: em trocas de golpes simultâneos, ela vence automaticamente. "
            "O puxão de corrente [R] arrasta o adversário por cima de buracos e o coloca exatamente na ponta de corte da sua foice."
        ),
        "weapons_en": (
            "Murasaki's sickle bypasses weapon clashes entirely: in mutual strike frames, her blade lands first. "
            "Her chain throw [R] drags opponents across floor pits directly onto her lethal sickle tip."
        ),
        "gameplan_pt": (
            "• Fase 1 (Captura com Corrente): Lance a corrente [R] na meia distância para desequilibrar o oponente.\n"
            "• Fase 2 (Puxão Forçado): Puxe o adversário em linha reta na sua direção enquanto ele estiver atordoado.\n"
            "• Fase 3 (Corte com Precedência): Golpei com a Foice [E]; mesmo se ele tentar atacar em desespero, sua foice corta primeiro."
        ),
        "gameplan_en": (
            "• Phase 1 (Chain Snare): Launch the weighted chain [R] at mid-range to hook and stagger the enemy.\n"
            "• Phase 2 (Reel In): Drag the opponent helplessly into execution distance.\n"
            "• Phase 3 (Precedence Slice): Cleave with the sickle [E]; even if they swing in panic, your precedence ensures victory."
        ),
        "how_to_beat_pt": (
            "A corrente de Murasaki tem tempo de arremesso e retorno. Se ela errar o puxão, fica travada em recuperação por 0.40s. "
            "Esquive-se de lado e puna com um golpe rápido."
        ),
        "how_to_beat_en": (
            "Murasaki's chain requires significant travel and recovery time. If she whiffs the pull, she is frozen for 0.40s. "
            "Sidestep the projectile and punish her open flank."
        )
    },

    # 8. KASUMI
    {
        "id": "gray",
        "name_pt": "KASUMI",
        "name_en": "KASUMI",
        "title_pt": "A Kunoichi da Névoa Tóxica",
        "title_en": "The Toxic Mist Kunoichi",
        "faction_pt": "6. Os Guardiões do Selo (Clã Shinobi de Iga)",
        "faction_en": "6. Guardians of the Seal (Iga Shinobi Clan)",
        "hp": 2,
        "speed": "4.75 m/s (Caminhada Silenciosa)",
        "reach_pt": "Curto (Ninjato Duplo) & Área (Bombas em Arco 3D)",
        "reach_en": "Short (Dual Ninjato) & Area (3D Arcing Bombs)",
        "style_pt": "Névoa Oculta de Iga (Armas Químicas & Fumaça Sufocante)",
        "style_en": "Iga Hidden Mist (Chemical Bombs & Choking Smoke)",
        "concept_art": "assets/concepts/kasumi_full_concept.jpg",
        "bust_art": "assets/portraits/kasumi_bust.png",
        "lore_pt": (
            "A mais engenhosa das guardiãs de Iga. Kasumi protege as passagens subterrâneas da Caverna Sombria utilizando bombas de fumaça "
            "e venenos que asfixiam e cegam qualquer guerreiro imprudente. Ciente de que o sangue atrai o Gashadokuro, ela prefere neutralizar "
            "os invasores com nuvens químicas antes que eles consigam quebrar o selo milenar."
        ),
        "lore_en": (
            "The most inventive sentinel of Iga, Kasumi protects the subterranean passages of the Shadow Cave utilizing chemical bombs "
            "and choking mists that disorient intruders. Knowing that bloodshed hastens the Gashadokuro's awakening, she neutralizes "
            "adversaries with toxic smoke screens before they can disturb the sacred seals."
        ),
        "moveset_pt": [
            ("Corte Duplo de Ninjato", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Golpe rápido cruzado de adagas ninjas. Dano direto à queima-roupa."),
            ("Arremesso de Bomba de Fumaça em Arco 3D", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Lança bombas esféricas de cerâmica em arco parabólico. Cria nuvem de veneno e fumaça que drena vida e cega."),
            ("Guarda Oculta", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Defesa ágil com dispersão de fumaça."),
            ("Salto de Fumaça", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Esquiva rápida com névoa acinzentada.")
        ],
        "moveset_en": [
            ("Twin Ninjato Strike", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Snappy dual dagger cross-cleave for close quarters."),
            ("3D Arcing Chemical Bomb", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Hurls ceramic smoke orbs in a parabolic arc. Leaves dense choking poison mist that blinds and burns HP."),
            ("Mist Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Agile blade defense veiled in smoke."),
            ("Vapor Leap", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Rolling retreat cloaked in gray ash.")
        ],
        "weapons_pt": (
            "Kasumi pode manter até 2 bombas ativas simultaneamente na arena. As nuvens de fumaça causam lentidão profunda e dano DoT contínuo "
            "a qualquer inimigo que permaneça em seu interior por mais de 0.8s."
        ),
        "weapons_en": (
            "Kasumi can field up to 2 active chemical bombs concurrently. Lingering smoke clouds inflict severe slow and continuous damage "
            "to any enemy trapped within their haze for longer than 0.8s."
        ),
        "gameplan_pt": (
            "• Fase 1 (Saturação de Área): Arremesse bombas [R] nas passagens estreitas e perto do centro da arena.\n"
            "• Fase 2 (Controle de Névoa): Force o oponente a contornar a fumaça ou recuar contra as bordas do mapa.\n"
            "• Fase 3 (Execução Oculta): Ataque com o corte duplo [E] enquanto o oponente tosse e tenta escapar do gás."
        ),
        "gameplan_en": (
            "• Phase 1 (Area Denial): Bombard choke points and arena centers with parabolic smoke bombs [R].\n"
            "• Phase 2 (Mist Corral): Steer the enemy around the hazardous fumes towards map edges or pitfalls.\n"
            "• Phase 3 (Ambush Strike): Ambush through the smoke with twin daggers [E] while the foe is blinded and taking DoT."
        ),
        "how_to_beat_pt": (
            "Nunca permaneça dentro da nuvem de fumaça de Kasumi! Pressione-a em combate colado: se ela tentar jogar a bomba à queima-roupa, "
            "sua animação de arremesso é vulnerável a cortes rápidos."
        ),
        "how_to_beat_en": (
            "Never stand inside Kasumi's smoke clouds! Pressure her closely: if she attempts to throw a bomb at point-blank range, "
            "her throwing windup leaves her fully open to quick thrusts."
        )
    },

    # 9. OKUNI
    {
        "id": "kabuki",
        "name_pt": "OKUNI",
        "name_en": "OKUNI",
        "title_pt": "A Mestra Dançarina dos Leques",
        "title_en": "The Steel-Fan Kabuki Maiden",
        "faction_pt": "4. Oportunistas & Cientistas do Caos",
        "faction_en": "4. Opportunists & Chaos Occultists",
        "hp": 2,
        "speed": "4.70 m/s (Danças Rítmicas Flutuantes)",
        "reach_pt": "Médio (Leques de Ferro Tessen-jutsu)",
        "reach_en": "Medium (Iron War Fan Tessen-jutsu)",
        "style_pt": "Kabuki Mai & Tessen-jutsu (Leques Cortantes & Finta Kawarimi)",
        "style_en": "Kabuki Mai & Tessen-jutsu (Steel War Fans & Kawarimi Feint)",
        "concept_art": "assets/concepts/okuni_full_concept.jpg",
        "bust_art": "assets/portraits/okuni_bust.png",
        "lore_pt": (
            "Fundadora mística do teatro Kabuki nas margens do Rio Kamo em Kyoto. Sob o disfarce de entretenimento cerimonial, "
            "Okuni colhe a essência espiritual e o fervor das multidões para alimentar suas danças rituais. Vê na comoção da guerra "
            "do Bakumatsu a oportunidade perfeita para transformar o Japão em seu próprio palco de tragédia teatral."
        ),
        "lore_en": (
            "Mystical pioneer of Kabuki theatre along Kyoto's Kamo River. Under the guise of ceremonial performances, "
            "Okuni reaps spiritual fervor and crowd essence to empower her esoteric dances. She views the upheaval of the Bakumatsu "
            "as the ultimate stage to orchestrate Japan's grandest tragic performance."
        ),
        "moveset_pt": [
            ("Dança dos Leques Cortantes", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Golpe em leque duplo cortante com lâminas de aço afiadíssimas nas bordas de seda carmim."),
            ("Finta Teatral Kawarimi (Substituição)", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Desaparece em uma chuva de pétalas de cerejeira e ressurge atrás do atacante se golpeada."),
            ("Parry de Leque Aberto", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Abre os leques de ferro rígidos absorvendo o impacto da lâmina inimiga."),
            ("Giro de Dança (Mai)", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Giro gracioso esquivando-se em espiral.")
        ],
        "moveset_en": [
            ("Steel Fan Dance", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Twin iron war fan cleave embedded with razor-sharp steel tips beneath scarlet silk."),
            ("Kawarimi Illusion Feint", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Vanishes in a swirl of sakura petals upon taking a hit, reappearing behind the attacker."),
            ("Open Fan Parry", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Snaps heavy iron fans open to catch and arrest incoming blades."),
            ("Kabuki Pirouette", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Graceful spiraling evasion across the floor.")
        ],
        "weapons_pt": (
            "A Finta Kawarimi [R] funciona como um parry ilusório. Se o oponente atacar durante a janela do Kawarimi, Okuni teleporta "
            "imediatamente para as costas dele, aplicando um Stun de desorientação de 0.60s."
        ),
        "weapons_en": (
            "Kawarimi Feint [R] functions as an evasive illusion counter. If the enemy strikes during the feint window, Okuni instantly "
            "teleports behind them, inflicting a 0.60s disorientation stun."
        ),
        "gameplan_pt": (
            "• Fase 1 (Isolamento em Ritmo): Mantenha o rival em distância média com golpes de leque abertos.\n"
            "• Fase 2 (Bait de Kawarimi): Quando o adversário tentar atacar agressivamente, acione a Finta Kawarimi [R].\n"
            "• Fase 3 (Punhalada nas Costas): Reapareça nas costas do rival atordoado e corte com os leques de ferro [E]."
        ),
        "gameplan_en": (
            "• Phase 1 (Rhythmic Spacing): Keep foes at bay with sweeping steel fan swings.\n"
            "• Phase 2 (Kawarimi Bait): When the enemy rushes in with an aggressive swing, trigger Kawarimi Feint [R].\n"
            "• Phase 3 (Backstab Climax): Reappear behind the stunned attacker and execute with the steel fans [E]."
        ),
        "how_to_beat_pt": (
            "Se Okuni errar o tempo do Kawarimi e ninguém a atacar, ela sofre um breve Whiff Stun de fadiga. Fure o ritmo dela com fintas "
            "e golpes atrasados para puni-la quando o truque falhar."
        ),
        "how_to_beat_en": (
            "If Okuni miscalculates Kawarimi and no blow connects, she suffers an 0.35s whiff recovery stagger. Use delayed strikes "
            "and feints to punish her whenever the illusion fails to trigger."
        )
    },

    # 10. TOMOE
    {
        "id": "archer",
        "name_pt": "TOMOE",
        "name_en": "TOMOE",
        "title_pt": "A Donzela Arqueira do Santuário",
        "title_en": "The Sacred Shrine Archer",
        "faction_pt": "1. Protetores do Povo & Ronins Virtuosos",
        "faction_en": "1. Protectors of the People & Virtuous Ronin",
        "hp": 2,
        "speed": "4.40 m/s (Postura Serena)",
        "reach_pt": "Infinito (Flecha de Arco Yumi)",
        "reach_en": "Infinite (Yumi Longbow Arrow)",
        "style_pt": "Kyudo Sagrado & Ofuda Purificador (Arco Longo Yumi)",
        "style_en": "Sacred Kyudo & Purifying Ofuda (Yumi Longbow)",
        "concept_art": "assets/concepts/tomoe_full_concept.jpg",
        "bust_art": "assets/portraits/tomoe_bust.png",
        "lore_pt": (
            "Miko consagrada do Santuário Kurama nas montanhas ao norte de Kyoto. Através de visões oraculares, Tomoe testemunhou o titã "
            "esquelético erguendo-se sobre as chamas da capital. Desceu as montanhas com seu arco Yumi sagrado e flechas purificadoras, "
            "determinada a abater os vilões que sangram o povo e restaurar o selo divino do Gashadokuro."
        ),
        "lore_en": (
            "Consecrated Miko of Mount Kurama Shrine north of Kyoto. Through divine visions, Tomoe witnessed the skeletal titan "
            "rising over the burning capital. She descended the sacred peaks armed with her Yumi longbow and sanctified arrows, "
            "sworn to fell the warlords whose slaughter weakens the Gashadokuro's divine seal."
        ),
        "moveset_pt": [
            ("Tiro Preciso de Yumi", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Disparo frontal veloz de flecha sagrada. Atravessa toda a arena em linha reta instantaneamente. 1-Hit Kill."),
            ("Salva Sagrada em Arco (Chuva de Flechas)", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Retesa o arco em ângulo zenital e dispara 3 flechas que caem em arco parabólico sobre a posição do rival."),
            ("Guarda com o Arco Yumi", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Usa o arco de bambu reforçado para defletir estocadas leves."),
            ("Recuo Sagrado", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Salto para trás com rearmamento imediato de flecha.")
        ],
        "moveset_en": [
            ("Pinpoint Yumi Shot", "[X] / [Square]", "[E] (P1) / [U] (P2)", "High-velocity sanctified arrow traversing the entire arena in a straight trajectory. 1-Hit Kill."),
            ("Sacred Arrow Volley (Sky Arc)", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Draws bow skyward, raining down 3 sanctified arrows in an arcing volley upon the enemy's coordinates."),
            ("Yumi Bow Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Reinforced bamboo bow defensive parry."),
            ("Shrine Evasion", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Graceful backward leap immediately nocking the next arrow.")
        ],
        "weapons_pt": (
            "Tomoe possui munição ilimitada com recarga automática de 0.25s. A Salva Sagrada [R] atinge oponentes escondidos atrás de rochas, "
            "árvores e coberturas do cenário, impedindo que adversários fiquem acampados."
        ),
        "weapons_en": (
            "Tomoe possesses unlimited arrows with a rapid 0.25s draw cycle. Her Sacred Volley [R] bypasses line-of-sight obstacles, "
            "striking targets hiding behind rocks, trees, or temple pillars."
        ),
        "gameplan_pt": (
            "• Fase 1 (Assédio de Longa Distância): Dispare flechas retas [E] forçando o rival a esquivar ou pular constantemente.\n"
            "• Fase 2 (Punição de Cobertura): Se o rival se esconder atrás de rochas, use a Salva Sagrada [R] para forçá-lo a sair.\n"
            "• Fase 3 (Tiro de Interceptação): No momento em que o oponente correr em desespero em linha reta, solte a flecha direta para a vitória."
        ),
        "gameplan_en": (
            "• Phase 1 (Long-Range Sniping): Rain straight arrows [E] across the map, compelling the foe to burn stamina dodging.\n"
            "• Phase 2 (Cover Flush): If the rival hides behind props or shrine stones, call down the Sacred Volley [R] to flush them out.\n"
            "• Phase 3 (Intercept Shot): As the flustered opponent charges in a straight desperation run, loose the direct arrow for the kill."
        ),
        "how_to_beat_pt": (
            "O arco Yumi exige um breve tempo de retesamento (windup). Aproxime-se em zigue-zague com rolamentos nos momentos em que ela levantar o braço. "
            "No corpo a corpo colado, Tomoe tem dificuldade em disparar."
        ),
        "how_to_beat_en": (
            "The Yumi bow requires a brief drawing windup. Close in via zig-zagging rolls timed to her arm lift. "
            "At point-blank range, Tomoe struggles to discharge arrows safely."
        )
    },

    # 11. ANNE
    {
        "id": "pirate",
        "name_pt": "ANNE",
        "name_en": "ANNE",
        "title_pt": "A Corsária dos Mares do Sul",
        "title_en": "The South Seas Corsair",
        "faction_pt": "5. Mercenários & Corsários de Guerra",
        "faction_en": "5. Mercenaries & War Corsairs",
        "hp": 2,
        "speed": "4.50 m/s (Passo Largo de Marinheira)",
        "reach_pt": "Médio-Largo (Alfanje Cutlass 180°)",
        "reach_en": "Medium-Wide (180° Cutlass Cleave)",
        "style_pt": "Esgrima Naval Corsária & Pólvora Negra (Cutlass Pesado)",
        "style_en": "Naval Cutlass Fencing & Black Powder (Heavy Cleave)",
        "concept_art": "assets/concepts/anne_full_concept.jpg",
        "bust_art": "assets/portraits/anne_bust.png",
        "lore_pt": (
            "Capitã de um navio corsário que aportou na Baía de Uraga durante o auge do comércio de armas do Bakumatsu. "
            "Anne não segue mestres nem impérios: seu objetivo é saquear os carregamentos de ouro e armas do Xogunato "
            "e navegar livre. Seu estilo naval combina o corte brutal de um pesado alfanje naval com rajadas de pólvora negra."
        ),
        "lore_en": (
            "Captain of a rogue corsair vessel anchored in Uraga Bay amidst the Bakumatsu arms smuggling boom. "
            "Anne bows to no emperor or shogun: her goal is plundering gold and military galleons to rule the open seas. "
            "Her naval fencing blends wide, bone-cracking cutlass sweeps with explosive bursts of black powder."
        ),
        "moveset_pt": [
            ("Cutlass Cleave (Varredura 180°)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Arco cortante horizontal massivo de 180 graus. Impossível de esquivar para os lados. Dano letal 1-Hit Kill."),
            ("Avanço Explosivo de Pólvora", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Detona uma carga de pólvora aos seus pés, projetando-se para frente em alta velocidade com corte de alfanje."),
            ("Guarda com Alfanje & Gancho", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Defesa naval firme suportando impactos pesados."),
            ("Pulo de Bordo", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Salto acrobático lateral de convés.")
        ],
        "moveset_en": [
            ("Cutlass Cleave (180° Sweep)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Massive horizontal 180-degree cleave. Impossible to evade laterally. Instant 1-Hit Kill."),
            ("Powder Burst Lunge", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Ignites a powder charge at her feet, launching forward with an explosive cutlass charge."),
            ("Cutlass & Hook Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Rugged naval parry absorbing heavy kinetic force."),
            ("Deckside Leap", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Agile naval vault over obstacles.")
        ],
        "weapons_pt": (
            "O Cutlass Cleave [E] tem o arco lateral mais amplo de todo o elenco: varre 180° na frente e nos flancos de Anne. "
            "O Avanço Explosivo [R] atravessa projéteis menores e quebra distâncias instantaneamente."
        ),
        "weapons_en": (
            "Cutlass Cleave [E] commands the widest horizontal coverage in the roster: a full 180° hemisphere in front and flank. "
            "Her Powder Burst Lunge [R] blows through light projectiles while closing distance in a flash."
        ),
        "gameplan_pt": (
            "• Fase 1 (Explosão de Distância): Use o Avanço Explosivo [R] para surpreender o rival que tentar manter distância.\n"
            "• Fase 2 (Encurralamento Angular): Posicione-se para cortar o caminho de fuga lateral do oponente.\n"
            "• Fase 3 (Varredura de 180°): Dispare o Cutlass Cleave [E] cobrindo toda a área frontal para garantir o abate."
        ),
        "gameplan_en": (
            "• Phase 1 (Burst Engagement): Deploy Powder Burst Lunge [R] to catch long-range gunners off-guard.\n"
            "• Phase 2 (Corner Trap): Herd the opponent towards arena edges where lateral dodges are restricted.\n"
            "• Phase 3 (180° Cleave): Unleash the Cutlass Cleave [E] wiping out the entire frontal hemisphere for the kill."
        ),
        "how_to_beat_pt": (
            "O Cutlass de Anne é pesado e tem uma janela de recuperação pós-corte de 0.28s. Mantenha distância média e use estocadas "
            "perfurantes de ponta fina (como o Florete de Julie ou o Gatotsu de Saitou) para golpeá-la de fora do seu alcance."
        ),
        "how_to_beat_en": (
            "Anne's heavy cutlass carries an 0.28s post-swing recovery lag. Maintain mid-range and utilize precise piercing thrusts "
            "(like Julie's Rapier or Saitou's Gatotsu) to strike outside her perimeter."
        )
    },

    # 12. JULIE
    {
        "id": "musketeer",
        "name_pt": "JULIE",
        "name_en": "JULIE",
        "title_pt": "A Mosqueteira da Coroa Francesa",
        "title_en": "The French Crown Musketeer",
        "faction_pt": "3. Lealistas & Servidores da Ordem",
        "faction_en": "3. Loyalists & Order Keepers",
        "hp": 2,
        "speed": "4.75 m/s (Passadas Nobres e Velozes)",
        "reach_pt": "Longo (Florete de Duelo / Rapier Francês)",
        "reach_en": "Long (French Dueling Rapier)",
        "style_pt": "Esgrima Clássica Francesa & Capa e Espada (Flèche & Riposte)",
        "style_en": "French Classical Fencing & Cloak & Dagger (Flèche & Riposte)",
        "concept_art": "assets/concepts/julie_full_concept.jpg",
        "bust_art": "assets/portraits/julie_bust.png",
        "lore_pt": (
            "Oficial de guarda de elite enviada na comitiva diplomática francesa em Yokohama para treinar as forças modernizadas "
            "do Xogunato. Orgulhosa e nobre, Julie vê na esgrima ocidental o ápice da elegância e da eficácia militar. Quando assassinatos "
            "estranhos ameaçam a embaixada, ela empunha seu florete de aço temperado e sua capa cerimonial para impor a honra da França."
        ),
        "lore_en": (
            "Elite guard officer sent with the French military and diplomatic mission in Yokohama to train modernized shogunate brigades. "
            "Proud and disciplined, Julie champions Western fencing as the pinnacle of military grace and speed. When ritualistic killings "
            "threaten the diplomatic enclave, she unsheathes her dueling rapier and swirling cape to defend her sovereign's honor."
        ),
        "moveset_pt": [
            ("Flèche Thrust (Estocada Relâmpago)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Estocada aerodinâmica em linha reta com extensão máxima do braço. Perfura pontos vitais com precisão absoluta. 1-Hit Kill."),
            ("Cape Flourish & Rodopio Acrobático", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Gira sua capa azul cerimonial em arco de 360°, cegando o rival e desferindo um chute acrobático alto que causa Stun."),
            ("En Garde & Riposte com Cazoleta", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Postura de esgrima com a concha dourada protegendo a mão. Se atacada, desfere estocada de riposte imediata."),
            ("Passo Evasivo (Passata Sotto)", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Agachamento e deslize no solo esquivando cortes altos.")
        ],
        "moveset_en": [
            ("Flèche Thrust (Lightning Lunge)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Aerodynamic straight-line dueling lunge with maximum arm extension. Clean 1-Hit Kill vital thrust."),
            ("Cape Flourish & Acrobatic Kick", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Swirls her royal blue cape in a 360° blinding circle, delivering a stunning high equestrian kick."),
            ("En Garde & Shell Riposte", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Fencing guard shielded by a gilded cazoleta. Triggers an instantaneous piercing riposte upon parrying."),
            ("Passata Sotto", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Low ducking slide bypassing high horizontal cleaves.")
        ],
        "weapons_pt": (
            "O Flèche Thrust [E] tem o maior alcance pontual em linha reta entre todas as armas brancas físicas (2.10m). "
            "O Cape Flourish [R] serve como ferramenta de quebra de ritmo, cegando o rival por 0.50s para permitir o riposte fatal."
        ),
        "weapons_en": (
            "Flèche Thrust [E] boasts the longest pinpoint reach among physical melee weapons (2.10m). "
            "Cape Flourish [R] interrupts rushing opponents, blinding them for 0.50s to guarantee a lethal fencing lunge."
        ),
        "gameplan_pt": (
            "• Fase 1 (Manutenção de Distância): Fique exatamente na ponta do alcance do florete (2 metros), intimidando com a ponta da lâmina.\n"
            "• Fase 2 (Cape Flourish no Avanço): Se o rival tentar fechar a distância agressivamente, acione o Cape Flourish [R] para atordoá-lo.\n"
            "• Fase 3 (Estocada Flèche): Finalize instantaneamente com o Flèche Thrust [E] no peito do oponente atordoado."
        ),
        "gameplan_en": (
            "• Phase 1 (Tip Spacing): Hover exactly at the rapier's maximum extension (2 meters), menacing the opponent's centerline.\n"
            "• Phase 2 (Cape Flourish Check): If the enemy lunges aggressively, trigger Cape Flourish [R] to stagger and blind them.\n"
            "• Phase 3 (Flèche Execution): Puncture the stunned foe instantly with the piercing Flèche Thrust [E]."
        ),
        "how_to_beat_pt": (
            "O Flèche de Julie tem uma linha reta extremamente estreita (apenas 0.15m de largura lateral). Esquivas limpas para os lados "
            "abrem totalmente suas costas para um corte letal."
        ),
        "how_to_beat_en": (
            "Julie's Flèche operates along an exceptionally narrow beam (0.15m lateral width). Clean diagonal sidesteps bypass her tip entirely, "
            "leaving her flank wide open to swift counter-cleaves."
        )
    },

    # 13. REN
    {
        "id": "ren",
        "name_pt": "REN",
        "name_en": "REN",
        "title_pt": "O Monge dos Punhos de Ferro",
        "title_en": "The Iron-Fist Shaolin Monk",
        "faction_pt": "2. Duelistas do Auge & Buscadores de Glória",
        "faction_en": "2. Peak Duelists & Glory Seekers",
        "hp": 2,
        "speed": "4.65 m/s (Passos Rápidos e Firmes)",
        "reach_pt": "Curto (Punhos Fechados) & Médio (Kiai de Choque)",
        "reach_en": "Short (Iron Fists) & Medium (Kiai Shockwave)",
        "style_pt": "Shaolin Quanfa & Grito Kiai Espiritual (Punhos Vigorosos)",
        "style_en": "Shaolin Quanfa & Spiritual Kiai Roar (Iron Strike)",
        "concept_art": "assets/concepts/ren_full_concept.jpg",
        "bust_art": "assets/portraits/ren_bust.png",
        "lore_pt": (
            "Monge peregrino treinado nas tradições marciais do continente que viajou ao Japão em busca de iluminação pelo combate. "
            "Ren despreza espadas e armas de corte: seus punhos calejados quebram lâminas de aço como se fossem galhos secos. "
            "Ele busca o confronto com os guerreiros mais letais para despertar a força interior que dissipa a ilusão do medo."
        ),
        "lore_en": (
            "A wandering monk forged in continental martial traditions who crossed the seas to Japan seeking enlightenment through combat. "
            "Ren disdains blades and steel weapons: his calloused iron knuckles shatter forged swords like dried twigs. "
            "He seeks duels against the most lethal masters to unlock the primordial spiritual force that shatters the illusion of fear."
        ),
        "moveset_pt": [
            ("Flurry de Punhos de Ferro", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Sequência fulminante de 3 socos velozes. O golpe final projeta o rival para longe com dano letal."),
            ("Rugido Kiai Espiritual", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Emite uma onda de choque sônica dourada que reflete projéteis e atordoa oponentes em 360°."),
            ("Corpo de Ferro (Iron Shirt)", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Defesa corporal impenetrável que repele lâminas afiadas com som metálico."),
            ("Salto de Garça", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Salto acrobático leve.")
        ],
        "moveset_en": [
            ("Iron Fist Flurry", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Blistering 3-punch barrage. The concluding strike launches the enemy backward with lethal impact."),
            ("Spiritual Kiai Roar", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Emits a 360° golden sonic shockwave that deflects projectiles and staggers all surrounding foes."),
            ("Iron Shirt Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Impenetrable body hardening repelling blade strikes with ringing metallic chimes."),
            ("Crane Leap", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Lightweight acrobatic evasion.")
        ],
        "weapons_pt": (
            "O Rugido Kiai [R] quebra a guarda de parry de qualquer inimigo a até 2.5 metros e desvia projéteis (flechas e kunais). "
            "Seus punhos possuem alta cadência de ataque que impede o rival de respirar."
        ),
        "weapons_en": (
            "Spiritual Kiai Roar [R] shatters enemy parry guards within a 2.5-meter radius and reflects projectiles (arrows, kunais). "
            "His fists deliver relentless attack pressure, smothering opposing windups."
        ),
        "gameplan_pt": (
            "• Fase 1 (Aproximação com Kiai): Avance e solte o Kiai [R] para desviar projéteis e atordoar o rival.\n"
            "• Fase 2 (Quebra de Distância): Cole no corpo a corpo imediato durante o atordoamento do Kiai.\n"
            "• Fase 3 (Flurry Devastador): Descarregue o Flurry de Punhos [E] quebrando qualquer tentativa de defesa."
        ),
        "gameplan_en": (
            "• Phase 1 (Kiai Pressure): Close in and unleash Kiai Roar [R] to neutralize projectiles and stun the foe.\n"
            "• Phase 2 (Distance Elimination): Swarm into point-blank range while the enemy is disoriented.\n"
            "• Phase 3 (Devastating Flurry): Discharge the Iron Fist Flurry [E], overpowering any desperate defensive attempt."
        ),
        "how_to_beat_pt": (
            "Ren precisa colar no corpo a corpo para causar dano. Mantenha distância usando armas longas (Lança de Aoi, Naginata de Benkei) "
            "ou projéteis contínuos para impedi-lo de chegar perto."
        ),
        "how_to_beat_en": (
            "Ren is bound strictly to close-quarters combat. Keep him at bay using long-reach polearms (Aoi's Spear, Benkei's Naginata) "
            "or sustained projectile zoning to prevent him from closing the distance."
        )
    },

    # 14. CHIYO
    {
        "id": "chiyo",
        "name_pt": "CHIYO",
        "name_en": "CHIYO",
        "title_pt": "A Kunoichi das Nodachi Gêmeas",
        "title_en": "The Twin Nodachi Kunoichi",
        "faction_pt": "6. Os Guardiões do Selo (Clã Shinobi de Iga)",
        "faction_en": "6. Guardians of the Seal (Iga Shinobi Clan)",
        "hp": 2,
        "speed": "4.55 m/s (Passos Elegantes de Dança)",
        "reach_pt": "Longo (Duas Grandes Lâminas Nodachi)",
        "reach_en": "Long (Twin Colossal Nodachi Blades)",
        "style_pt": "Dança das Espadas Gêmeas de Higanbana (Dual Nodachi)",
        "style_en": "Higanbana Twin-Blade Dance (Dual Nodachi)",
        "concept_art": "assets/concepts/chiyo_full_concept.jpg",
        "bust_art": "assets/portraits/chiyo_bust.png",
        "lore_pt": (
            "Especialista em armas pesadas do clã de Iga. Diferente dos ninjas convencionais que usam adagas discretas, Chiyo maneja "
            "duas gigantescas lâminas Nodachi com a leveza de pétalas de lírio vermelho. Sua missão é interceptar regimentos inteiros "
            "que marcham em direção à Caverna Sombria, cortando soldados e cavaleiros com arcos circulares devastadores."
        ),
        "lore_en": (
            "Heavy weapon specialist of the Iga shinobi clan. Unlike traditional assassins who rely on small daggers, Chiyo brandishes "
            "two colossal Nodachi greatswords with the graceful lightness of scarlet spider lilies. Her duty is ambushing advancing armies "
            "marching towards the Shadow Cave, cleaving soldiers and cavalry in sweeping circular whirlwinds."
        ),
        "moveset_pt": [
            ("Corte Duplo Nodachi", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Arco cortante duplo devastador com as duas espadas longas. Alcance e dano brutais."),
            ("Vórtice Carmim de Higanbana", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Giro contínuo de 720° com as duas lâminas abertas, criando um turbilhão de cortes que engole inimigos em volta."),
            ("Guarda em X de Lâminas Longas", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Cruza as duas espadas de 1.5m em X, bloqueando qualquer investida pesada."),
            ("Salto dos Lírios", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Esquiva acrobática leve.")
        ],
        "moveset_en": [
            ("Twin Nodachi Cleave", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Devastating dual-blade sweep with two colossal greatswords. Massive reach and killing power."),
            ("Higanbana Crimson Vortex", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Continuous 720° spin with both extended blades, creating a lethal whirlwind swallowing surrounding foes."),
            ("Cross-Blade Nodachi Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Locks both 1.5m blades into an X-guard, absorbing heavy kinetic attacks."),
            ("Lily Leap", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Graceful acrobatic roll.")
        ],
        "weapons_pt": (
            "O Vórtice Carmim [R] possui 360 graus de cobertura contínua e quebra defesas normais se o oponente ficar preso nas lâminas. "
            "Seu alcance normal é um dos maiores do jogo entre espadas (1.90m)."
        ),
        "weapons_en": (
            "Crimson Vortex [R] delivers continuous 360° coverage and overwhelms standard guards if the rival is caught in the storm. "
            "Her basic reach is among the longest in the roster for edged weapons (1.90m)."
        ),
        "gameplan_pt": (
            "• Fase 1 (Controle de Alcance): Aproveite as duas lâminas longas para atacar de uma distância onde katanas normais não chegam.\n"
            "• Fase 2 (Vórtice no Desespero): Quando o rival tentar esquivar para seus flancos, acione o Vórtice Carmim [R].\n"
            "• Fase 3 (Execução Dupla): Finalize com o Corte Duplo [E] na recuperação do oponente."
        ),
        "gameplan_en": (
            "• Phase 1 (Reach Dominance): Use the dual greatswords to dictate exchanges outside standard katana range.\n"
            "• Phase 2 (Vortex Trap): When the enemy attempts to sidestep around your flanks, unleash Crimson Vortex [R].\n"
            "• Phase 3 (Twin Cleave Finish): Decapitate with Twin Nodachi Cleave [E] during the opponent's staggering recovery."
        ),
        "how_to_beat_pt": (
            "Após girar no Vórtice Carmim, Chiyo sofre uma janela de tontura/recuperação de 0.30s. Espere o giro terminar de fora do alcance "
            "e puna imediatamente com uma estocada rápida."
        ),
        "how_to_beat_en": (
            "Following the Crimson Vortex spin, Chiyo experiences an 0.30s dizziness recovery lag. Wait outside her spin perimeter "
            "and punish her instantly the moment her rotation ceases."
        )
    },

    # 15. BENKEI
    {
        "id": "benkei",
        "name_pt": "BENKEI",
        "name_en": "BENKEI",
        "title_pt": "O Monge Guerreiro da Naginata Colossal",
        "title_en": "The Colossal Naginata Sohei",
        "faction_pt": "1. Protetores do Povo & Ronins Virtuosos",
        "faction_en": "1. Protectors of the People & Virtuous Ronin",
        "hp": 3,
        "speed": "4.00 m/s (Passos Pesados e Implacáveis)",
        "reach_pt": "Colossal (Naginata Gigante de 2.5 Metros)",
        "reach_en": "Colossal (2.5-Meter Giant Naginata)",
        "style_pt": "Sohei Kenjutsu (Armadura Pesada O-Yoroi & Naginata)",
        "style_en": "Sohei Kenjutsu (Heavy O-Yoroi Armor & Naginata)",
        "concept_art": "assets/concepts/benkei_full_concept.jpg",
        "bust_art": "assets/portraits/benkei_bust.png",
        "lore_pt": (
            "O lendário monge guerreiro que jurou proteger a sagrada Ponte Gojo e os templos de Kyoto contra qualquer tirano. "
            "Com sua couraça de placas de ferro e sua naginata colossal, Benkei é uma muralha viva: possui 3 Pontos de Vida (HP) "
            "e suporta múltiplos golpes fatais antes de tombar, empunhando sua lâmina curva para proteger camponeses e peregrinos."
        ),
        "lore_en": (
            "The legendary warrior monk who swore to defend Gojo Bridge and Kyoto's sacred temples from tyrannical warlords. "
            "Clad in heavy iron-plated O-Yoroi armor and brandishing a colossal naginata, Benkei is a living fortress: boasting 3 HP, "
            "he withstands fatal strikes before falling, sweeping his massive glaive to shield pilgrims and the defenseless."
        ),
        "moveset_pt": [
            ("Varredura Colossal de Naginata", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Corte em arco gigantesco com alcance de 2.5 metros. Causa dano massivo e arremessa o oponente longe."),
            ("Pisotão Sísmico & Rugido de Guarda", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Pisa com força descomunal no piso, quebrando tábuas/pedras e atordoando inimigos ao redor com onda de choque."),
            ("Bloqueio de Muralha de Ferro", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Usa o cabo de carvalho blindado da naginata como barreira inamovível."),
            ("Avanço Pesado", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Investida com ombro blindado absorvendo impactos leves.")
        ],
        "moveset_en": [
            ("Colossal Naginata Sweep", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Gigantic sweeping arc spanning 2.5 meters. Deals crushing damage and sends opponents flying."),
            ("Seismic Stomp & Roar", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Slams his armored foot into the floor, fracturing cobblestones and staggering nearby foes with a shockwave."),
            ("Iron Wall Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Anchors the reinforced oak haft as an unyielding fortress barricade."),
            ("Armored Shoulder Rush", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Heavy forward stride absorbing light kinetic impacts.")
        ],
        "weapons_pt": (
            "Benkei possui 3 HP (o maior do jogo) e Hiperarmadura (Poise): seus ataques não são interrompidos por golpes leves no início. "
            "Sua naginata atinge alvos a distâncias que nenhuma espada tradicional alcança."
        ),
        "weapons_en": (
            "Benkei boasts 3 HP (highest in the roster) and heavy Poise: his colossal windups cannot be interrupted by light jabs. "
            "His naginata reaches targets at ranges no standard sword can contest."
        ),
        "gameplan_pt": (
            "• Fase 1 (Manutenção de Parede): Use a Varredura de Naginata [E] para manter o adversário longe.\n"
            "• Fase 2 (Pisotão Sísmico): Se o rival tentar rolar para baixo da lâmina, use o Pisotão [R] para atordoá-lo no chão.\n"
            "• Fase 3 (Golpe Esmagador): Finalize o oponente atordoado com o corte descendente pesado."
        ),
        "gameplan_en": (
            "• Phase 1 (Perimeter Wall): Maintain spacing using the Colossal Naginata Sweep [E] to dominate the arena.\n"
            "• Phase 2 (Seismic Shock): When agile foes roll beneath your blade, crush them with the Seismic Stomp [R].\n"
            "• Phase 3 (Crushing Cleave): Dispatch the staggered opponent with a thunderous overhead chop."
        ),
        "how_to_beat_pt": (
            "Benkei é o combatente mais lento do jogo (4.00 m/s) e sua recuperação pós-golpe é demorada. Flanqueie pelas diagonais "
            "com combatentes rápidos (Kenshi, Hanzo, Hendrika) e ataque durante a recuperação da naginata."
        ),
        "how_to_beat_en": (
            "Benkei is the slowest fighter in the roster (4.00 m/s) with significant recovery lag. Flank diagonally using agile skirmishers "
            "(Kenshi, Hanzo, Hendrika) and punish his exposed rear during weapon swings."
        )
    },

    # 16. O-RIN
    {
        "id": "orin",
        "name_pt": "O-RIN",
        "name_en": "O-RIN",
        "title_pt": "A Menestrel Cega do Shamisen",
        "title_en": "The Blind Shamisen Minstrel",
        "faction_pt": "4. Oportunistas & Cientistas do Caos",
        "faction_en": "4. Opportunists & Chaos Occultists",
        "hp": 2,
        "speed": "4.45 m/s (Caminhada Suave Guiada pelo Som)",
        "reach_pt": "Infinito (Lâminas Sônicas Kamaitachi)",
        "reach_en": "Infinite (Kamaitachi Sonic Blades)",
        "style_pt": "Oto-jutsu & Kamaitachi (Lâminas de Vácuo do Shamisen)",
        "style_en": "Oto-jutsu & Kamaitachi (Vacuum Soundwaves from Shamisen)",
        "concept_art": "assets/concepts/orin_full_concept.jpg",
        "bust_art": "assets/portraits/orin_bust.png",
        "lore_pt": (
            "Menestrel cega que percorre os becos de Yoshiwara tocando seu shamisen de três cordas. Por trás da aparência frágil "
            "esconde-se uma mestre das ondas de choque acústicas: suas notas musicais rasgam o ar gerando lâminas de vácuo (Kamaitachi) "
            "que decepam inimigos à distância. Ela se alimenta da melancolia dos condenados da guerra para afinar seu instrumento mortal."
        ),
        "lore_en": (
            "A blind minstrel wandering the lantern-lit alleys of Yoshiwara strumming her three-stringed shamisen. Behind her fragile facade "
            "lies an acoustic sorceress: her sharp musical chords tear the atmosphere, firing razor vacuum blades (Kamaitachi) that decapitate "
            "foes from afar. She feeds on the melancholy of fallen souls to tune her deadly instrument."
        ),
        "moveset_pt": [
            ("Lâmina Sônica Kamaitachi", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Toca um acorde agudo que projeta uma lâmina de vácuo cortante em linha reta por toda a arena. 1-Hit Kill."),
            ("Acorde Ressonante em Leque", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Dispara 3 ondas sônicas em leque que ricocheteiam nas paredes e atordoam quem for atingido."),
            ("Escudo Acústico de Cordas", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Vibração de alta frequência que dissipa projéteis e desvia golpes físicos."),
            ("Passo Deslizante Sonoro", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Esquiva suave guiada pela acústica do ambiente.")
        ],
        "moveset_en": [
            ("Kamaitachi Sonic Blade", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Plucks a sharp chord launching a razor-sharp vacuum blade traversing the entire arena. 1-Hit Kill."),
            ("Resonant Fan Chord", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Fires 3 fan-shaped soundwaves that ricochet off walls, staggering anyone caught in their path."),
            ("Acoustic String Ward", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "High-frequency string resonance vaporizing incoming projectiles and deflecting blows."),
            ("Echo Slide", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Gentle evasive slide guided by spatial acoustic echo.")
        ],
        "weapons_pt": (
            "As lâminas Kamaitachi [E] viajam a 16.0 m/s e atravessam inimigos e obstáculos destrutíveis. "
            "O Acorde Ressonante [R] preenche salas fechadas (como Yoshiwara e Rain Mill) com ricochetes perigosos."
        ),
        "weapons_en": (
            "Kamaitachi blades [E] fly at 16.0 m/s, piercing through destructible props and enemies. "
            "Her Resonant Fan Chord [R] saturates enclosed stages (such as Yoshiwara and Rain Mill) with dangerous ricochets."
        ),
        "gameplan_pt": (
            "• Fase 1 (Bombardeio Acústico): Dispare notas Kamaitachi [E] mantendo o oponente sempre na defensiva.\n"
            "• Fase 2 (Leque de Ricochete): Use o Acorde em Leque [R] perto de paredes para criar armadilhas sonoras.\n"
            "• Fase 3 (Disparo no Pânico): Quando o oponente tentar pular os ricochetes, acerte a lâmina sônica direta."
        ),
        "gameplan_en": (
            "• Phase 1 (Acoustic Pressure): Fire straight Kamaitachi chords [E] forcing the foe into defensive dodging.\n"
            "• Phase 2 (Ricochet Trap): Deploy the Fan Chord [R] near obstacles to create bouncing sound hazards.\n"
            "• Phase 3 (Panic Punish): The moment the foe stumbles over ricochet waves, loose the direct sonic blade for the kill."
        ),
        "how_to_beat_pt": (
            "O-Rin é extremamente frágil e não possui golpes de corte físico corpo a corpo. Use o rolamento [Espaço] para passar "
            "por baixo da onda sonora e ataque-a à queima-roupa onde ela não tem defesa."
        ),
        "how_to_beat_en": (
            "O-Rin is fragile and possesses no physical close-quarters blade. Use forward rolls [Space] to slip beneath the sonic waves "
            "and strike her at point-blank range where she cannot contest."
        )
    },

    # 17. GORO
    {
        "id": "goro",
        "name_pt": "GORO",
        "name_en": "GORO",
        "title_pt": "O Camponês Rebelde da Enxada",
        "title_en": "The Peasant Rebel of the Kuwa",
        "faction_pt": "1. Protetores do Povo & Ronins Virtuosos",
        "faction_en": "1. Protectors of the People & Virtuous Ronin",
        "hp": 2,
        "speed": "4.40 m/s (Passo Rústico e Pesado)",
        "reach_pt": "Médio-Longo (Enxada Pesada de Ferro Forjado)",
        "reach_en": "Medium-Long (Forged Iron Heavy Kuwa)",
        "style_pt": "Nogu-jutsu (Implementos Agrícolas & Força Bruta Camponesa)",
        "style_en": "Nogu-jutsu (Farming Implements & Raw Peasant Strength)",
        "concept_art": "assets/concepts/goro_full_concept.jpg",
        "bust_art": "assets/portraits/goro_bust.png",
        "lore_pt": (
            "Líder dos levantes camponeses de Omi, Goro cansou de ver suas colheitas queimadas e suas famílias massacradas "
            "pelas guerras dos nobres e samurais. Transformou sua enxada pesada de ferro (Kuwa) em uma arma letal de insurreição. "
            "Ele luta ao lado de Kenshi e Benkei para garantir que o sangue dos pobres não seja o combustível do retorno do Gashadokuro."
        ),
        "lore_en": (
            "Leader of the Omi peasant rebellions, Goro grew sick of seeing harvests torched and farming families slaughtered "
            "by the squabbles of lords and samurai. He forged his heavy farming hoe (Kuwa) into an insurrectionist weapon of war. "
            "He fights alongside Kenshi and Benkei to ensure the blood of the poor does not fuel the Gashadokuro's resurrection."
        ),
        "moveset_pt": [
            ("Golpe Esmagador de Kuwa", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Golpe descendente violento com a lâmina pesada de ferro da enxada. Esmaga parries e enterra o rival no solo. 1-Hit Kill."),
            ("Pisotão de Lama & Arremesso de Cascalho", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Pisa no solo arremessando lama e cascalho nos olhos do rival, cegando e aplicando Stun."),
            ("Bloqueio com o Cabo de Carvalho", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Usa o cabo de madeira maciça da enxada para bloquear golpes cortantes."),
            ("Salto de Dique", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Salto rústico cruzando diques e valas de água.")
        ],
        "moveset_en": [
            ("Kuwa Earth Cleave", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Violent overhead slam with the heavy iron hoe. Shatters parries and pins the foe to the earth. 1-Hit Kill."),
            ("Mud Stomp & Gravel Throw", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Stomps the soil hurling mud and sharp gravel into the enemy's eyes, blinding and staggering them."),
            ("Hardwood Haft Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Reinforced wooden hoe haft defensive block."),
            ("Paddy Dike Leap", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Rugged hurdle vaulting over irrigation ditches.")
        ],
        "weapons_pt": (
            "A enxada Kuwa possui dano contundente misturado com corte: quebra defesas de parry leves automaticamente. "
            "O Pisotão de Lama [R] desacelera o adversário em 40% em terrenos de terra e arrozais."
        ),
        "weapons_en": (
            "The Kuwa hoe combines blunt kinetic force with chopping cleaves: it shatters light parries automatically. "
            "Mud Stomp [R] slows down opponents by 40% across dirt and paddy fields."
        ),
        "gameplan_pt": (
            "• Fase 1 (Cegueira com Cascalho): Aproxime-se e solte o Pisotão [R] para cegar o oponente temporariamente.\n"
            "• Fase 2 (Avanço no Desequilíbrio): Avance com passadas largas enquanto o rival tenta esfregar os olhos.\n"
            "• Fase 3 (Esmagamento de Kuwa): Desça a lâmina da enxada [E] esmagando a cabeça do adversário."
        ),
        "gameplan_en": (
            "• Phase 1 (Gravel Blind): Close in and trigger Mud Stomp [R] to spray blinding debris into the foe's eyes.\n"
            "• Phase 2 (Stagger Charge): Advance with heavy strides while the blinded enemy reels back.\n"
            "• Phase 3 (Kuwa Slam): Bring down the heavy iron hoe [E] directly onto the opponent's skull."
        ),
        "how_to_beat_pt": (
            "O golpe da Kuwa é pesado e lento para se recuperar se errar o alvo (0.32s). Esquive-se para os lados e ataque "
            "as costas desprotegidas de Goro antes que ele levante a enxada do chão."
        ),
        "how_to_beat_en": (
            "Goro's Kuwa slam has high recovery lag if he misses the mark (0.32s). Roll sideways and strike his exposed back "
            "before he can dislodge the heavy iron hoe from the dirt."
        )
    },

    # 18. ICHI
    {
        "id": "ichi",
        "name_pt": "ICHI",
        "name_en": "ICHI",
        "title_pt": "A Massagista Cega da Lâmina Oculta",
        "title_en": "The Blind Masseuse of the Cane Blade",
        "faction_pt": "3. Lealistas & Servidores da Ordem",
        "faction_en": "3. Loyalists & Order Keepers",
        "hp": 2,
        "speed": "4.60 m/s (Passo Silencioso com Bengala)",
        "reach_pt": "Médio (Shikomizue de Saque Invertido)",
        "reach_en": "Medium (Reverse-Grip Shikomizue Cane)",
        "style_pt": "Gyaku-Iaijutsu (Espada Oculta em Bengala de Massagista)",
        "style_en": "Gyaku-Iaijutsu (Concealed Cane Blade of the Masseuse)",
        "concept_art": "assets/concepts/ichi_full_concept.jpg",
        "bust_art": "assets/portraits/ichi_bust.png",
        "lore_pt": (
            "Trabalhando como massagista itinerante cega pelas tabernas e moinhos de Kyoto, Ichi guarda lealdade secreta aos "
            "magistrados lealistas da ordem pública. Sob a aparência dócil e frágil, sua bengala de massagista oculta uma lâmina "
            "afiada como navalha. Seus ouvidos captam a respiração e a tensão muscular dos assassinos, decapitando-os com saque invertido."
        ),
        "lore_en": (
            "Working as a blind traveling masseuse through the taverns and mills of Kyoto, Ichi harbors secret allegiance "
            "to loyalist peace magistrates. Beneath her meek, gentle demeanor, her walking cane conceals a razor-sharp steel blade. "
            "Her heightened hearing tracks the heartbeat and muscle twitches of assassins, executing them with reverse-grip draws."
        ),
        "moveset_pt": [
            ("Gyaku-Iai (Saque Invertido da Bengala)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Desembainha a lâmina oculta em pegada invertida com corte ascendente relâmpago. 1-Hit Kill."),
            ("Postura de Escuta Espiritual", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Fica imóvel ouvindo o vento: se o oponente iniciar um ataque, Ichi esquiva automaticamente e desfere contra-ataque letal."),
            ("Parry com a Bengala de Madeira", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Usa o corpo de bambu da bengala para desviar golpes."),
            ("Passo Cego de Deslize", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Deslize evasivo fluido rente ao chão.")
        ],
        "moveset_en": [
            ("Gyaku-Iai (Reverse Cane Draw)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Unsheathes the concealed blade in reverse grip with an upward lightning slash. 1-Hit Kill."),
            ("Listening Trance Counter", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Stands motionlessly reading the wind: automatically evades incoming swings and counters with an unblockable thrust."),
            ("Cane Wood Parry", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Deflects incoming edges using the lacquered bamboo cane casing."),
            ("Blind Glide Step", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Smooth evasive slip across the floorboards.")
        ],
        "weapons_pt": (
            "A Postura de Escuta [R] é o contra-ataque mais perfeito do jogo contra ataques previsíveis. Ela não depende de mira: "
            "desvia e pune o atacante em qualquer ângulo de 360 graus."
        ),
        "weapons_en": (
            "Listening Trance [R] is the most flawless counter-stance against predictable strikes. It requires no directional aiming: "
            "she slips and executes the attacker across a full 360-degree perimeter."
        ),
        "gameplan_pt": (
            "• Fase 1 (Provocação Silenciosa): Aproxime-se lentamente batendo a ponta da bengala no chão para provocar o ataque rival.\n"
            "• Fase 2 (Postura de Escuta): Ative a Postura de Escuta [R] no momento em que o rival engajar.\n"
            "• Fase 3 (Contra-Ataque Gyaku-Iai): Deixe o sistema esquivar e cortar a garganta do atacante automaticamente."
        ),
        "gameplan_en": (
            "• Phase 1 (Silent Bait): Walk forward tapping the cane tip, provoking the enemy into an aggressive swing.\n"
            "• Phase 2 (Listening Trance): Engage Listening Trance [R] right as the rival commits to their forward stride.\n"
            "• Phase 3 (Gyaku-Iai Decapitation): Let the automatic slip-counter sever the foe's throat."
        ),
        "how_to_beat_pt": (
            "Jamais ataque Ichi diretamente quando ela estiver parada na Postura de Escuta! Use fintas com cancelamento de golpe, "
            "projéteis de longe ou aguarde os 0.50s da postura expirar para puni-la."
        ),
        "how_to_beat_en": (
            "Never swing directly at Ichi when she stands still in Listening Trance! Use attack feints, ranged projectiles, "
            "or wait out the 0.50s trance duration to strike her during stance recovery."
        )
    },

    # 19. VALERIUS
    {
        "id": "valerius",
        "name_pt": "VALERIUS",
        "name_en": "VALERIUS",
        "title_pt": "O Necromante Diplomata da Prússia",
        "title_en": "The Prussian Necromancer Diplomat",
        "faction_pt": "4. Oportunistas & Cientistas do Caos",
        "faction_en": "4. Opportunists & Chaos Occultists",
        "hp": 2,
        "speed": "4.40 m/s (Passadas Sinistras e Nobres)",
        "reach_pt": "Longo (Foice de Guerra Gótica) & Convocação de Mortos",
        "reach_en": "Long (Gothic War Scythe) & Undead Summoning",
        "style_pt": "Nigromancia Prussiana & Esgrima de Foice Sepulcral",
        "style_en": "Prussian Necromancy & Sepulchral Scythe Combat",
        "concept_art": "assets/concepts/valerius_full_concept.jpg",
        "bust_art": "assets/portraits/valerius_bust.png",
        "lore_pt": (
            "Conselheiro secreto na embaixada prussiana enviado ao Japão sob pretexto de tratados comerciais. Valerius é um adepto "
            "das artes proibidas da necromancia europeia: percebeu que o Bakumatsu acumula a maior concentração de almas em agonia "
            "do século XIX. Ele busca canalizar essa energia para quebrar o selo do Gashadokuro e subjugar o titã sob sua vontade macabra."
        ),
        "lore_en": (
            "Secret occult advisor attached to the Prussian embassy under the guise of commercial treaty negotiations. Valerius is a master "
            "of forbidden European necromancy: recognizing that the Bakumatsu harbors the dense concentration of agonizing souls in the world, "
            "he seeks to harness this death energy to crack the Gashadokuro's crypt and bind the titan to his macabre will."
        ),
        "moveset_pt": [
            ("Corte de Foice Gótica", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Arco largo e afiado com a foice sepulcral. Alcance longo que rasga carne e quebra defesas leves. 1-Hit Kill."),
            ("Invocação do Servo Esqueleto", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Ergue das profundezas da terra um servo esqueleto armado que avança contra o rival, distraindo e golpeando."),
            ("Escudo de Ossos e Éter", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Cria uma barreira de ossos espectrais absorvendo ataques."),
            ("Passo das Brumas Sepulcrais", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Desvanece em névoa negra esquivando golpes.")
        ],
        "moveset_en": [
            ("Gothic Scythe Reaping", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Wide reaping sweep with his sepulchral war scythe. Long reach that shreds flesh and breaks light guards. 1-Hit Kill."),
            ("Skeleton Minion Summon", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Rises an armed skeletal minion from the soil that relentlessly chases and harasses the opponent."),
            ("Bone & Ether Ward", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Summons an ethereal cage of bones absorbing incoming blade swings."),
            ("Sepulchral Mist Fade", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Dissolves into dark mist to evade oncoming attacks.")
        ],
        "weapons_pt": (
            "O Servo Esqueleto [R] funciona como um segundo combatente ativo na arena: absorve um golpe do oponente ou ataca com espada, "
            "criando a distração perfeita para Valerius ceifar com a foice."
        ),
        "weapons_en": (
            "The Skeleton Minion [R] functions as an active field ally: it absorbs an incoming blow or swings an ancient blade, "
            "creating the ideal distraction for Valerius to reap with his scythe."
        ),
        "gameplan_pt": (
            "• Fase 1 (Erguer o Morto): Convoque o Servo Esqueleto [R] no início do duelo.\n"
            "• Fase 2 (Pinça Dupla): Avance em ângulo oposto ao do esqueleto, forçando o rival a escolher quem defender.\n"
            "• Fase 3 (Ceifada Fatal): No instante em que o adversário virar para golpear o esqueleto, ceife-o com a foice [E]."
        ),
        "gameplan_en": (
            "• Phase 1 (Rise Minion): Summon the Skeleton Minion [R] right at the opening bell.\n"
            "• Phase 2 (Pincer Encirclement): Advance along the opposite flank, forcing the foe to divide their guard.\n"
            "• Phase 3 (Fatal Reaping): The moment the enemy turns to swat the minion, reap them with the war scythe [E]."
        ),
        "how_to_beat_pt": (
            "Destrua o esqueleto com um golpe rápido ou mantenha distância diagonal para desviar do arco largo da foice. "
            "Valerius tem recuperação lenta após errar a foice."
        ),
        "how_to_beat_en": (
            "Shatter the skeleton with a quick strike or circle diagonally outside the scythe's reach. "
            "Valerius suffers significant recovery lag after whiffing a heavy reaping swing."
        )
    },

    # 20. SEIMEI
    {
        "id": "seimei",
        "name_pt": "SEIMEI",
        "name_en": "SEIMEI",
        "title_pt": "A Mestra Onmyoji dos Cinco Elementos",
        "title_en": "The Five-Element Onmyoji Maiden",
        "faction_pt": "4. Oportunistas & Cientistas do Caos",
        "faction_en": "4. Opportunists & Chaos Occultists",
        "hp": 2,
        "speed": "4.60 m/s (Passos Flutuantes Místicos)",
        "reach_pt": "Infinito (Ofudas dos 6 Elementos do Rondel)",
        "reach_en": "Infinite (6-Element Rondel Ofuda Talismans)",
        "style_pt": "Onmyodo Imperial & Magia dos Selos Elementais (Rondel Heian)",
        "style_en": "Imperial Onmyodo & Elemental Talisman Magic (Heian Rondel)",
        "concept_art": "assets/concepts/seimei_full_concept.jpg",
        "bust_art": "assets/portraits/seimei_bust.png",
        "lore_pt": (
            "Descendente direta do lendário Abe no Seimei. Guardiã dos registros cósmicos imperiais de Heian, Seimei compreende "
            "que o Gashadokuro é uma entidade cósmica ligada ao equilíbrio do Yin e Yang. Manipulando o Rondel dos 6 Elementos "
            "(Madeira, Fogo, Terra, Metal, Água e Vazio), ela canaliza feitiços para moldar o destino do Bakumatsu e submeter o titã à sua autoridade."
        ),
        "lore_en": (
            "Direct blood descendant of the legendary Abe no Seimei. Keeper of Heian's imperial cosmic scrolls, Seimei understands "
            "that the Gashadokuro is an ancient entity intertwined with the balance of Yin and Yang. Manipulating the 6-Element Rondel "
            "(Wood, Fire, Earth, Metal, Water, and Void), she channels incantations to reshape the Bakumatsu and bend the titan to her divine will."
        ),
        "moveset_pt": [
            ("Disparo Elemental Onmyodo", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Dispara o feitiço do elemento ativo no Rondel (Madeira: enraizamento; Fogo: explosão; Terra: monólito; Metal: lâmina supersônica; Água: serpente teleguiada; Vazio: confusão)."),
            ("Rotação do Rondel Onmyodo", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Gira o Rondel místico para o próximo elemento divino, adaptando o feitiço às fraquezas do oponente."),
            ("Barreira de Selos Místicos", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Ergue uma barreira de pergaminhos ofuda dourados que desintegra projéteis e repele lâminas."),
            ("Passo Etéreo Onmyoji", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Deslize flutuante deixando caracteres arcanos luminosos no piso.")
        ],
        "moveset_en": [
            ("Elemental Onmyodo Talisman", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Unleashes the active spell from the Rondel (Wood: rooting roots; Fire: guard-breaking blaze; Earth: crushing monolith; Metal: supersonic unblockable blade; Water: homing ricochet serpent; Void: control confusion)."),
            ("Rondel Element Cycle", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Rotates the mystical Rondel to the next element, tailoring incantations to counter opponent matchups."),
            ("Sacred Talisman Ward", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Erects a protective barrier of golden ofuda talismans vaporizing incoming projectiles and repelling steel."),
            ("Ethereal Step", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Levitating glide scattering glowing celestial kanji across the floor.")
        ],
        "weapons_pt": (
            "Seimei é a lutadora com a maior taxa de vitória da simulação global (67.9% ~ 70.7%). Cada elemento possui propriedade única: "
            "Madeira (imobiliza por 2s), Fogo (quebra de guarda), Terra (derruba), Metal (100% imparável a 32 m/s), Água (ricochete teleguiado) e Vazio (inversão de controles)."
        ),
        "weapons_en": (
            "Seimei ranks as the highest-winrate combatant in the global simulation (67.9% ~ 70.7%). Each element yields a unique tactical property: "
            "Wood (2s rooting), Fire (guard crush), Earth (knockdown monolith), Metal (100% unblockable at 32 m/s), Water (homing double ricochet), and Void (control inversion)."
        ),
        "gameplan_pt": (
            "• Fase 1 (Rotação Tática): Selecione o elemento ideal contra o arquétipo rival (Metal contra defensores, Água contra ágeis).\n"
            "• Fase 2 (Imobilização / Zoneamento): Dispare o feitiço ativo [E] travando os movimentos do rival.\n"
            "• Fase 3 (Execução Elemental): Se o rival for enraizado ou desorientado, encadeie o disparo fatal de Metal ou Fogo."
        ),
        "gameplan_en": (
            "• Phase 1 (Tactical Selection): Dial the ideal element counter against the enemy archetype (Metal vs turtles, Water vs speedsters).\n"
            "• Phase 2 (Immobilize / Zone): Loose the active incantation [E] locking down opposing footwork.\n"
            "• Phase 3 (Elemental Execution): Once the target is rooted or stunned, deliver the decisive Metal or Fire talisman."
        ),
        "how_to_beat_pt": (
            "Observe a cor da aura e o Rondel no rodapé para saber qual feitiço ela possui. Esquive-se lateralmente nas agulhas de Madeira "
            "e jamais tente usar parry contra o elemento Metal."
        ),
        "how_to_beat_en": (
            "Track Seimei's glowing aura and bottom Rondel icon to read her loaded element. Roll sideways against Wood needles "
            "and never attempt to parry the supersonic Metal blade."
        )
    },

    # 21. DAIKI
    {
        "id": "daiki",
        "name_pt": "DAIKI",
        "name_en": "DAIKI",
        "title_pt": "O Peregrino do Bastão Bo",
        "title_en": "The Bo Staff Pilgrim",
        "faction_pt": "1. Protetores do Povo & Ronins Virtuosos",
        "faction_en": "1. Protectors of the People & Virtuous Ronin",
        "hp": 2,
        "speed": "4.60 m/s (Passadas Altas de Montanha)",
        "reach_pt": "Longo (Bastão de Carvalho Bo de 1.8m)",
        "reach_en": "Long (1.8m Oak Bo Staff)",
        "style_pt": "Bojutsu Tradicional dos Peregrinos de Yamabushi",
        "style_en": "Yamabushi Mountain Pilgrim Bojutsu",
        "concept_art": "assets/concepts/daiki_full_concept.jpg",
        "bust_art": "assets/portraits/daiki_bust.png",
        "lore_pt": (
            "Monge asceta das montanhas sagradas de Hida que desceu ao mundo dos homens após ter suas trilhas de peregrinação "
            "infestadas por bandidos e tropas desertoras. Recusa-se a derramar sangue com lâminas de aço afiadas: seu bastão de carvalho "
            "Bo desfere pancadas contundentes que desarmam e incapacitam os agressores, protegendo viajantes e templos com serenidade inabalável."
        ),
        "lore_en": (
            "Ascetic monk from the sacred mountains of Hida who descended into the lowlands after bandit gangs and deserters overrun "
            "ancient pilgrimage routes. Refusing to spill blood with edged steel blades, his seasoned oak Bo staff delivers crushing "
            "kinetic sweeps that disarm and incapacitate tyrants, shielding weary pilgrims with resolute serenity."
        ),
        "moveset_pt": [
            ("Varredura Rápida de Bo", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Golpe horizontal veloz de ponta dupla com o bastão de carvalho. Alcance longo com desestabilização."),
            ("Salto com Vara (Pole Vault Leap)", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Finca o bastão no chão e projeta-se alto no ar, passando por cima de buracos e caindo com pancada descendente."),
            ("Bloqueio Giratório de Bo", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Gira o bastão com as duas mãos repelindo projéteis e lâminas."),
            ("Esquiva com Salto de Vara", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Acrobacia lateral leve apoiando a ponta do bastão.")
        ],
        "moveset_en": [
            ("Swift Bo Sweep", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Rapid double-ended horizontal staff strike. Extended reach that staggers rival balance."),
            ("Pole Vault Leap", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Plants the oak staff into the ground, vaulting skyward over chasms and descending with a crushing overhead blow."),
            ("Spinning Staff Ward", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Two-handed spinning staff defense deflecting arrows and blades."),
            ("Vault Slip", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Lightweight lateral evasive pivot using the staff tip.")
        ],
        "weapons_pt": (
            "O Salto com Vara [R] permite atravessar precipícios e escapar de poças e armadilhas no solo, caindo com um golpe de impacto "
            "de 1-Hit Kill que esmaga oponentes desprevenidos."
        ),
        "weapons_en": (
            "Pole Vault Leap [R] clears wide floor gaps and evades ground traps, coming down with a crushing 1-Hit Kill impact "
            "over the heads of unprepared opponents."
        ),
        "gameplan_pt": (
            "• Fase 1 (Zonear com a Ponta): Mantenha o adversário longe usando a ponta do bastão [E].\n"
            "• Fase 2 (Salto com Vara no Ataque): Quando o rival iniciar um projétil ou golpe pesado, salte por cima dele com [R].\n"
            "• Fase 3 (Pancada na Aterrissagem): Desça o golpe de carvalho esmagador no topo da cabeça do oponente."
        ),
        "gameplan_en": (
            "• Phase 1 (Tip Harass): Keep rivals outside threat range using the outer reach of the Bo staff [E].\n"
            "• Phase 2 (Pole Vault Evasion): When the enemy winds up an artillery shot or heavy strike, vault over them with [R].\n"
            "• Phase 3 (Overhead Descent): Descend directly onto the opponent's skull for an instantaneous knockout."
        ),
        "how_to_beat_pt": (
            "Cuidado ao disparar projéteis quando Daiki estiver prestes a saltar. Espere o momento de aterrissagem do Salto com Vara "
            "para punir sua breve recuperação de 0.20s."
        ),
        "how_to_beat_en": (
            "Beware firing projectiles when Daiki is primed to leap. Track his landing coordinates and punish his brief 0.20s "
            "touchdown recovery lag."
        )
    },

    # 22. AOI
    {
        "id": "aoi",
        "name_pt": "AOI",
        "name_en": "AOI",
        "title_pt": "A Caçadora Ainu das Terras de Ezo",
        "title_en": "The Ainu Huntress of Ezo",
        "faction_pt": "1. Protetores do Povo & Ronins Virtuosos",
        "faction_en": "1. Protectors of the People & Virtuous Ronin",
        "hp": 2,
        "speed": "4.70 m/s (Passadas Silenciosas na Neve)",
        "reach_pt": "Longo (Lança Tradicional Ainu Op)",
        "reach_en": "Long (Traditional Ainu Op Spear)",
        "style_pt": "Arte de Caça de Ezo (Lança Op & Armadilhas de Urso)",
        "style_en": "Ezo Hunting Mastery (Op Spear & Iron Bear Traps)",
        "concept_art": "assets/concepts/aoi_full_concept.jpg",
        "bust_art": "assets/portraits/aoi_bust.png",
        "lore_pt": (
            "Guerreira e caçadora do povo nativo Ainu vinda das florestas boreais de Ezo (atual Hokkaido). Quando presságios sinistros "
            "revelaram que os espíritos Kamuy das montanhas estavam sendo perturbados pela maldição de sangue de Kyoto, Aoi desceu ao sul "
            "para caçar as abominações que ameaçam a terra sagrada, armada com sua lança de caça Op e armadilhas metálicas de urso."
        ),
        "lore_en": (
            "Huntress and protector of the indigenous Ainu people from the northern boreal wilderness of Ezo (Hokkaido). When ominous omens "
            "revealed that the sacred Kamuy mountain spirits were being corrupted by Kyoto's blood sacrifice, Aoi ventured south "
            "to hunt the horrors defiling the earth, armed with her carved Op hunting spear and spring-loaded bear traps."
        ),
        "moveset_pt": [
            ("Estocada Perfurante de Lança Op", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Estocada direta e veloz com a lança de caça Ainu. Alcance superior a katanas com alta capacidade perfurante. 1-Hit Kill."),
            ("Plantar Armadilha de Urso", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Planta uma armadilha metálica dentada oculta no piso. Se o rival pisar, fica preso sangrando e paralisado por 2.5s."),
            ("Bloqueio de Lança", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Usa a haste reforçada da lança para defletir lâminas."),
            ("Esquiva da Taiga", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Salto ágil de caçadora na neve.")
        ],
        "moveset_en": [
            ("Op Hunting Spear Thrust", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Crisp direct thrust with the carved Ainu spear. Outranges katanas with deadly piercing lethality. 1-Hit Kill."),
            ("Plant Iron Bear Trap", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Conceals a spring-loaded toothed iron trap on the floor. Foes stepping upon it suffer bleed and 2.5s absolute root."),
            ("Spear Haft Guard", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Deflects blade swings using the reinforced wooden spear haft."),
            ("Taiga Tumble", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Agile huntress leap adapted for snowy terrain.")
        ],
        "weapons_pt": (
            "A Armadilha de Urso [R] é invisível no calor do combate. Quando o rival cai nela, fica travado no local sem poder se mover "
            "ou esquivar, virando alvo fácil para a estocada de lança."
        ),
        "weapons_en": (
            "The Iron Bear Trap [R] is nearly undetectable amidst battle chaos. Stepping on it completely immobilizes the foe for 2.5s, "
            "turning them into an effortless target for the Op spear thrust."
        ),
        "gameplan_pt": (
            "• Fase 1 (Armadilha Estratégica): Plante a armadilha de urso [R] no centro da arena ou entre passagens de árvores.\n"
            "• Fase 2 (Atrair o Rival): Recue mantendo distância com a lança, induzindo o adversário a correr sobre a armadilha.\n"
            "• Fase 3 (Estocada de Caça): Com o inimigo preso nos dentes de ferro, crave a lança Op [E] no peito."
        ),
        "gameplan_en": (
            "• Phase 1 (Trap Setup): Plant the iron bear trap [R] along choke points or between tree lines.\n"
            "• Phase 2 (Bait & Kiting): Retreat while jabbing with the spear tip, luring the rival into sprinting across the trap.\n"
            "• Phase 3 (Spear Impalement): With the enemy snared in iron jaws, impale their chest with the Op spear [E]."
        ),
        "how_to_beat_pt": (
            "Observe atentamente o piso para não pisar nas mandíbulas metálicas de Aoi! Pule ou esquive para fechar distância "
            "e puna suas estocadas lineares de lança contornando suas laterais."
        ),
        "how_to_beat_en": (
            "Watch the floor carefully to avoid stepping into Aoi's iron jaws! Vault or roll past the trap and punish her linear spear "
            "thrusts by flanking her sides."
        )
    },

    # 23. RAIDEN
    {
        "id": "raiden",
        "name_pt": "RAIDEN",
        "name_en": "RAIDEN",
        "title_pt": "O Yokozuna Invicto dos Deuses",
        "title_en": "The Undefeated Yokozuna of the Gods",
        "faction_pt": "2. Duelistas do Auge & Buscadores de Glória",
        "faction_en": "2. Peak Duelists & Glory Seekers",
        "hp": 3,
        "speed": "3.85 m/s (Passadas Titânicas de Sumô)",
        "reach_pt": "Médio (Golpe de Palmas Harite / Tsuppari) & Investida Tachiai",
        "reach_en": "Medium (Harite / Tsuppari Palm Strikes) & Tachiai Tackle",
        "style_pt": "Sumô Sagrado Xintoísta & Palmas Destruidoras (Tsuppari & Tachiai)",
        "style_en": "Sacred Shinto Sumo & Crushing Palm Thrusts (Tsuppari & Tachiai)",
        "concept_art": "assets/concepts/raiden_full_concept.jpg",
        "bust_art": "assets/portraits/raiden_bust.png",
        "lore_pt": (
            "O maior Yokozuna da história do Japão, cuja força física é reverenciada como uma manifestação direta dos deuses do trovão. "
            "Raiden entrou na arena sagrada do Bakumatsu após desafiar mestres de espada que duvidavam da eficácia do combate desarmado. "
            "Com 3 HP e hiperarmadura titânica, suas palmas abertas esmagam espadas e ossos como se fossem feitos de papel."
        ),
        "lore_en": (
            "The greatest Yokozuna in Japanese history, whose sheer physical might is revered as a direct manifestation of the thunder kami. "
            "Raiden stepped into the sacred arena after challenging swordmasters who scoffed at unarmed combat. "
            "Boasting 3 HP and titanic Poise, his open-palm strikes shatter katanas and ribcages as if forged from parchment."
        ),
        "moveset_pt": [
            ("Tsuppari Combo (Palmas Sísmicas de Sumô)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Combo cadenciado em duas fases: Golpe 1 (Harite que desequilibra com empurrão) seguido por Golpe 2 (Morote-Tsuppari com dano massivo 2 HP e recuo violento)."),
            ("Tachiai Tackle (Investida Teleguiada de Corpo)", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Investida explosiva de corpo inteiro com hiperarmadura. Empurra o rival por até 4 metros arremessando-o para fora da arena."),
            ("Shiko Stomp (Pisotão Ritual)", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Pisa firme no solo purificando o dohyo e absorvendo impactos frontais."),
            ("Deslocamento de Cintura (Suriashi)", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Passo arrastado tradicional de sumô.")
        ],
        "moveset_en": [
            ("Tsuppari Combo (Seismic Sumo Palms)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Two-hit timed combo: Strike 1 (Harite stagger push) leading into Strike 2 (Morote-Tsuppari dealing 2 HP damage and crushing knockback)."),
            ("Tachiai Tackle (Homing Body Charge)", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Explosive full-body charge coated in heavy Poise. Shoves opponents across 4 meters and hurls them out of the ring."),
            ("Shiko Ritual Stomp", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Ceremonial ground stomp purifying the ring while absorbing frontal blows."),
            ("Suriashi Footwork", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Traditional dragging sumo step maintaining constant ground balance.")
        ],
        "weapons_pt": (
            "Raiden possui 3 HP e Hiperarmadura completa durante o Tachiai [R]: golpes leves de espada não interrompem seu avanço. "
            "O segundo golpe do Tsuppari [E] causa 2 de dano puro e derruba qualquer oponente que não estiver esquivando."
        ),
        "weapons_en": (
            "Raiden boasts 3 HP and full Poise during Tachiai Tackle [R]: incoming sword jabs cannot halt his momentum. "
            "The second strike of his Tsuppari chain [E] inflicts 2 flat damage, bowling over any rival caught standing."
        ),
        "gameplan_pt": (
            "• Fase 1 (Tachiai de Entrada): Inicie o confronto disparando o Tachiai Tackle [R] para engolir a distância e encurralar o rival.\n"
            "• Fase 2 (Harite de Desestabilização): Conecte o primeiro golpe de palma [E] causando recuo e quebra de ritmo.\n"
            "• Fase 3 (Morote-Tsuppari Fatal): Pressione imediatamente o segundo golpe de [E] para desfechar o combo devastador de 2 HP."
        ),
        "gameplan_en": (
            "• Phase 1 (Opening Tachiai): Initiate with Tachiai Tackle [R] to erase distance and pin the enemy against stage limits.\n"
            "• Phase 2 (Harite Stagger): Connect with the first palm slap [E] to disrupt opposing guard and momentum.\n"
            "• Phase 3 (Morote-Tsuppari KO): Trigger the second strike of [E] immediately to deliver the devastating 2-HP finisher."
        ),
        "how_to_beat_pt": (
            "Não dispute trocas frontais diretas contra o Tsuppari ou o Tachiai de Raiden! Sua hiperarmadura absorverá seu golpe. "
            "Mantenha distância com esquivas laterais e contra-ataque pelas costas após ele errar a investida."
        ),
        "how_to_beat_en": (
            "Never trade blows head-on against Raiden's armored palm charges or Tachiai tackle! His Poise will absorb your attack. "
            "Circle around using lateral dashes and punish his exposed flanks during tackle recovery."
        )
    },

    # 24. HENDRIKA
    {
        "id": "hendrika",
        "name_pt": "HENDRIKA",
        "name_en": "HENDRIKA",
        "title_pt": "A Alquimista Tática de Dejima",
        "title_en": "The Tactical Dejima Alchemist",
        "faction_pt": "4. Oportunistas & Cientistas do Caos",
        "faction_en": "4. Opportunists & Chaos Occultists",
        "hp": 2,
        "speed": "4.60 m/s (Passos Rápidos e Imprevisíveis)",
        "reach_pt": "Curto (Estilete Cáustico Quebra-Parry) & Área (5 Frascos em Arco 3D)",
        "reach_en": "Short (Caustic Guard-Crush Stiletto) & Area (5 Arcing 3D Flasks)",
        "style_pt": "Alquimia Holandesa de Dejima (5 Reagentes & Síntese de Solo)",
        "style_en": "Dutch VOC Alchemy (5 Chemical Reagents & Field Synthesis)",
        "concept_art": "assets/concepts/hendrika_full_concept.jpg",
        "bust_art": "assets/portraits/hendrika_bust.png",
        "lore_pt": (
            "Erudita holandesa alocada na feitoria da Companhia das Índias Orientais (VOC) na ilha artificial de Dejima, em Nagasaki. "
            "Excêntrica, genial e moralmente pragmática, Hendrika enxerga o Bakumatsu como um gigantesco laboratório a céu aberto. "
            "Desenvolveu um estilete cirúrgico banhado em ácido que dissolve armaduras e frascos de cinco compostos químicos letais, "
            "sintetizados diretamente a partir das propriedades minerais do solo onde pisa."
        ),
        "lore_en": (
            "Brilliant Dutch scholar stationed at the VOC trading factory on the artificial island of Dejima in Nagasaki. "
            "Eccentric, calculating, and morally pragmatic, Hendrika treats the turmoil of the Bakumatsu as a sprawling open-air laboratory. "
            "She perfected a surgical stiletto coated in vitriol acid that dissolves enemy armor and five arcing chemical flasks, "
            "synthesizing lethal concoctions directly from the mineral composition of the soil beneath her boots."
        ),
        "moveset_pt": [
            ("Estilete Corrosivo (Quebra-Parry)", "[X] / [Quadrado]", "[E] (P1) / [U] (P2)", "Estocada ultrarrápida banhada em ácido. Se o rival tentar usar Parry, o estilete quebra a guarda dele (Guard Crush) e aplica Stun imediato."),
            ("Frasco Alquímico em Arco 3D", "[Y] / [Triângulo]", "[R] (P1) / [I] (P2)", "Arremessa um frasco químico que gera poça persistente no solo (Ácido: corrosão; Fogo: repulsão; Éter: sono profundo; Salitre: congelamento; Miasma: confusão de controles)."),
            ("Deflexão de Estilete com Fumaça", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Bloqueio com dispersão de fumaça cáustica."),
            ("Rolamento Acrobático Europeu", "[A] / [Cruz]", "[Espaço] (P1) / [P] (P2)", "Rolamento acrobático ágil com invulnerabilidade.")
        ],
        "moveset_en": [
            ("Corrosive Stiletto (Guard Crush)", "[X] / [Square]", "[E] (P1) / [U] (P2)", "Blistering acid-coated dagger thrust. If the enemy attempts to Parry, the stiletto shatters their posture (Guard Crush) inflicting instant stun."),
            ("3D Arcing Alchemical Flask", "[Y] / [Triangle]", "[R] (P1) / [I] (P2)", "Hurls an arcing chemical vial leaving lingering hazard pools (Acid: corrosion; Fire: repulsion knockback; Ether: sleep stun; Frost: freeze slow; Miasma: control inversion)."),
            ("Stiletto Deflection & Smoke", "[RB] / [R1]", "[F] (P1) / [O] (P2)", "Blade deflection veiled in chemical smoke."),
            ("Acrobatic European Roll", "[A] / [Cross]", "[Space] (P1) / [P] (P2)", "Agile tumbling evasion with clean invulnerability.")
        ],
        "weapons_pt": (
            "O estilete de Hendrika quebra qualquer parry com atordoamento de 0.45s a 1.10s. Seus frascos arremessados duram até 6 segundos no solo. "
            "Ao permanecer 0.85s sobre qualquer piso, sintetiza a fórmula daquele terreno (Gelo para Salitre, Rocha para Éter, Madeira para Miasma, Terra para Ácido). "
            "Ficar 2.0s no mesmo piso eleva a fórmula para Tier 2 (raio expandido para 1.65m e efeitos potencializados)."
        ),
        "weapons_en": (
            "Hendrika's stiletto crushes parries outright with an 0.45s to 1.10s stun. Her chemical pools linger on the ground for up to 6.0 seconds. "
            "Standing 0.85s on any ground synthesizes that terrain's formula (Ice for Frost, Stone for Ether, Wood for Miasma, Soil for Acid). "
            "Remaining 2.0s on the same material elevates concoctions to Tier 2 (expanded 1.65m radius and boosted potency)."
        ),
        "gameplan_pt": (
            "• Fase 1 (Zoneamento de Abertura): Não corra em linha reta; arremesse o frasco [R] para criar uma poça no caminho do adversário.\n"
            "• Fase 2 (Punição por Status): Se acertar Éter (sono), caminhe até ele; se acertar Salitre (gelo) ou Miasma (confusão), flanqueie com rolamento.\n"
            "• Fase 3 (Bait de Parry com Estilete): Quando o adversário acuado erguer a guarda de parry, fure com o Estilete Cáustico [E] para o Guard Crush letal."
        ),
        "gameplan_en": (
            "• Phase 1 (Opening Zoning): Never charge in straight lines; lob a flask [R] to block the opponent's approach path.\n"
            "• Phase 2 (Status Exploitation): If Ether connects (sleep), walk forward; if Frost (freeze) or Miasma (confusion) lands, flank with agile rolls.\n"
            "• Phase 3 (Stiletto Parry Bait): When the cornered foe panics and raises a parry guard, puncture with Corrosive Stiletto [E] for a lethal Guard Crush."
        ),
        "how_to_beat_pt": (
            "Evite permanecer dentro das poças químicas no solo! Jamais use parry contra o estilete de Hendrika. Utilize armas pesadas "
            "de longo alcance (Naginata de Benkei, Lança de Aoi, Arco de Tomoe) para golpeá-la antes que ela estabeleça controle de área."
        ),
        "how_to_beat_en": (
            "Steer completely clear of glowing chemical pools on the floor! Never attempt to parry Hendrika's stiletto. Utilize extended-reach "
            "weapons (Benkei's Naginata, Aoi's Spear, Tomoe's Bow) to strike her outside her short dagger range before she sets area traps."
        )
    }
]
