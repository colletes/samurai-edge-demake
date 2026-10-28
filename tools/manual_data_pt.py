"""
Banco de dados completo em Português para a geração do Manual Oficial de Samurai Edge em PDF.
Edição Final de Alta Densidade (24 Páginas).
"""

LORE_PT = {
    "title": "A LENDA DO BAKUMATSU & O SELO DAS CINZAS",
    "p1": (
        "No crepúsculo do século XIX (década de 1860), o Japão foi sacudido pela chegada dos 'Navios Negros' do Comodoro Perry, "
        "rompendo abruptamente mais de dois séculos de isolamento sagrado (Sakoku). A terra do sol nascente rachou em uma guerra civil "
        "selvagem e impiedosa: de um lado, os lealistas do Xogunato Tokugawa lutando para preservar a ordem feudal e o código samurai; "
        "do outro, os rebeldes monarquistas de Choshu e Satsuma que exigiam a restauração do poder imperial supremo e a expulsão dos estrangeiros."
    ),
    "p2": (
        "No entanto, sob o véu das disputas políticas entre espadachins e do avanço implacável das armas de fogo ocidentais, uma força "
        "ancestral muito mais aterrorizante começou a se agitar. Na província montanhosa e impenetrável de Iga, sob "
        "o manto perpétuo da Caverna Sombria, jazia selado há mais de mil anos o Oni Gashadokuro: o titã esquelético "
        "colossal forjado a partir do ódio acumulado e da agonia de dezenas de milhares de guerreiros mortos em guerras antigas e abandonados sem sepultura."
    ),
    "p3": (
        "A profecia dos antigos monges de Onmyodo previa que, se o solo do arquipélago fosse novamente inundado com o sangue "
        "de inocentes e guerreiros sem descanso espiritual, os grilhões mágicos que aprisionavam o titã se romperiam. "
        "Sem saber, cada duelo de espadas travado nos becos em chamas de Kyoto, cada emboscada nas florestas de bambu "
        "e cada execução sumária realizada nas docas chuvosas de Dejima alimenta a escuridão crescente, acelerando o retorno "
        "do titã faminto para extinguir toda a vida nas quatro ilhas do Japão."
    ),
    "p4": (
        "Enquanto os líderes militares conspiram em salões de chá protegidos por guardas, as estradas e arrozais do Japão "
        "tornaram-se campos de caça para mercenários sem mestre, alquimistas clandestinos e espadachins errantes. O destino "
        "da nação já não pertence aos diplomatas nem aos tratados selados em tinta: ele será esculpido pelo gume de lâminas afiadas."
    ),
    "p5": (
        "Apenas aqueles capazes de transcender o medo da própria finitude e dominar a fração de segundo que separa o corte mortal "
        "do vazio do erro conseguirão alcançar o coração da montanha de Iga e decidir se o Japão renascerá sob uma nova era de honra "
        "ou será engolido pelas mandíbulas de ferro do titã das cinzas."
    ),
    "quote": "«No fio da navalha, entre o saque e o corte, não há espaço para o ódio: apenas a verdade nua do aço.»"
}

FACTIONS_PT = [
    {
        "name": "1. Protetores do Povo & Ronins Virtuosos",
        "desc": "Espadachins, arqueiras, monges e camponeses que pegaram em armas não por ambição política, mas para proteger vilarejos, templos e camponeses inocentes contra massacres e pilhagens da guerra civil.",
        "members": ["Kenshi", "Tomoe", "Daiki", "Goro", "Benkei"],
        "philosophy": "A espada que preserva a vida (Katsujinken). Defendem os indefesos contra a tirania feudal e a opressão dos senhores da guerra."
    },
    {
        "name": "2. Duelistas do Auge & Buscadores de Glória",
        "desc": "Mestres de artes marciais lendárias que veem o tumulto do Bakumatsu como o crisol definitivo para testar seus limites físicos e espirituais contra os combatentes mais letais do mundo.",
        "members": ["Musashi", "Ren", "Raiden"],
        "philosophy": "A busca intransigente pela maestria marcial absoluta, onde cada duelo de lâminas é um diálogo direto com a própria mortalidade."
    },
    {
        "name": "3. Lealistas & Servidores da Ordem",
        "desc": "Guerreiros implacáveis guiados por juramentos inquebrantáveis de lealdade a seus comandantes, ao Xogunato, ao Imperador ou a coroas soberanas estrangeiras.",
        "members": ["Saitou", "Julie", "Ichi"],
        "philosophy": "Dever absoluto, honra militar e lealdade cega à bandeira jurada até o último sopro de vida."
    },
    {
        "name": "4. Oportunistas & Cientistas do Caos",
        "desc": "Eruditos excêntricos, necromantes arcanos e dançarinas místicas que operam nas sombras da guerra, aproveitando o sangue derramado para conduzir experimentos proibidos e colher poder sobrenatural.",
        "members": ["Hendrika", "Valerius", "Okuni"],
        "philosophy": "O caos é um laboratório fértil. A moralidade tradicional é descartada em prol do avanço alquímico e da colheita espiritual."
    },
    {
        "name": "5. Mercenários & Corsários de Guerra",
        "desc": "Atiradores de aluguel e navegadores audaciosos que singram as fendas do comércio marítimo e dos conflitos feudais em busca de riqueza, pólvora e liberdade irrestrita.",
        "members": ["Anne", "Teppo"],
        "philosophy": "Sobrevivência, ouro e independência. Lutam pelo melhor pagador ou pela própria tripulação sem submissão a senhores de terras."
    },
    {
        "name": "6. Os Guardiões do Selo (Clã Shinobi de Iga)",
        "desc": "A elite das sombras de Iga. Aparentam ser assassinos impiedosos aos olhos do mundo, mas na verdade formam a linha secreta de defesa que guarda a Caverna Sombria para impedir que o Oni Gashadokuro desperte.",
        "members": ["Hanzo", "Kasumi", "Murasaki", "Chiyo"],
        "philosophy": "Sacrifício invisível. Manter o titã adormecido mesmo que a história os condene como sombras cruéis e conspiratórias."
    },
    {
        "name": "7. O Viajante Temporal & Aliado Inusitado",
        "desc": "Um fuzileiro americano e operador tático do século XXI, fanático por animes e cultura pop, acidentalmente lançado no Japão de 1863 por uma falha em experimento governamental secreto.",
        "members": ["Joe"],
        "philosophy": "Sobrevivência com estilo ninja militar moderno. Ao descobrir o nobre sacrifício dos ninjas de Iga, jurou lutar ao seu lado com seu fiel cão de guerra Yamato."
    }
]

CONTROLS_PT = {
    "title": "COMANDOS BÁSICOS & SISTEMA DE DUELO",
    "desc": (
        "Samurai Edge utiliza um sistema de combate isométrico diegético inspirado no cinema clássico de Akira Kurosawa "
        "e na precisão cirúrgica de Bushido Blade. Cada golpe carrega letalidade brutal e posicionamento tridimensional estrito."
    ),
    "table": [
        ("Movimento 8-Way", "D-Pad / Analógico Esquerdo", "[W, A, S, D] (P1) / [Setas] (P2)", "Deslocamento e posicionamento tridimensional na arena"),
        ("Ataque Primário", "Botão X / Quadrado", "[E] (P1) / [U] (P2)", "Golpe principal da arma (saque Battojutsu, corte rápido, estocada ou tiro)"),
        ("Ação Secundária / Especial", "Botão Y / Triângulo", "[R] (P1) / [I] (P2)", "Golpe especial exclusivo, acrobacia, projétil ou parry reativo"),
        ("Esquiva / Rolamento", "Botão B / Círculo", "[T] (P1) / [O] (P2)", "Rolamento acrobático dedicado com 12 frames de invulnerabilidade"),
        ("Bloqueio / Parry Universal", "Botão RB / R1", "[F] (P1) / [I] (P2)", "Postura de guarda com janela de deflexão e contra-golpe"),
        ("Pausa / Menu Cerimonial", "Botão Start / Opções", "[ESC]", "Pausa em pergaminho Sumi-E e consulta de golpes")
    ],
    "mechanics": [
        ("Choque de Lâminas (Blade Clash QTE)", "Quando dois ataques de corte simétricos colidem no mesmo frame espacial, o tempo congela por 600ms com faíscas cinemáticas. O jogador que teclar mais rápido o botão de ataque desequilibra o rival, forçando 24 frames de cambaleio."),
        ("Precedência Absoluta", "Certos golpes (como a Foice da Kusarigama de Murasaki ou a Estocada Ácida de Hendrika) possuem prioridade matemática garantida, ignorando o Choque de Lâminas e interrompendo qualquer ataque comum."),
        ("Quebra de Postura (Guard Crush)", "Disparos de pólvora pesada (Teppo), golpes de maça maciça (Benkei) e estocadas químicas (Hendrika) quebram posturas de bloqueio ativo, aplicando atordoamento severo no defensor."),
        ("Letalidade Cirúrgica (1 a 3 HP)", "Quase todos os combatentes possuem 2 Pontos de Vida (com exceção de Musashi e Raiden, que possuem 3 HP). Um único golpe limpo desferido durante a recuperação do rival decide a vida instantaneamente.")
    ]
}

MODES_PT = {
    "title": "MODOS DE COMBATE & PROGRESSÃO",
    "arcade_title": "MODO ARCADE — A JORNADA DE 12 LUTAS",
    "arcade_desc": (
        "A campanha solo definitiva. O jogador escolhe seu guerreiro e avança por uma escada de 12 confrontos rituais "
        "onde o sangue derramado ecoa pelos quatro cantos do Japão, desestabilizando progressivamente o selo sagrado da Caverna Sombria:"
    ),
    "arcade_stages": [
        ("Ato I: Duelos Ranqueados 1 a 4", "Confrontos clássicos Melhor-de-3 (BO3) contra espadachins e guerreiros sorteados democraticamente entre as categorias iniciais de dificuldade."),
        ("Ato II: A Prova dos Mestres 5 a 8", "Duelos de alta tensão tática contra mestres veteranos, arqueiros e especialistas em armas exóticas nas arenas mais perigosas do país."),
        ("Ato III: O Confronto de Espelho (Luta 9)", "O guerreiro enfrenta sua própria sombra espectral em sua arena natal. Uma batalha de reflexos e técnica pura com paridade absoluta de armas."),
        ("Ato IV: Desafio de Resistência (Luta 10)", "Dois adversários de elite consecutivos em sequência ininterrupta, compartilhando as mesmas vidas de round. Exige controle rigoroso de espaço e paciência."),
        ("Ato V: O Portão dos Guardiões (Luta 11)", "Entrada na Caverna Sombria de Iga. O jogador deve derrotar a falange dos Guardiões do Selo (Joe, Kasumi, Murasaki, Hanzo e Chiyo) sob névoa venenosa."),
        ("Epílogo: O Despertar do Titã (Luta 12)", "Com a queda dos guardiões, o selo milenar racha. O gigantesco Oni Gashadokuro ergue-se das profundezas em um duelo colossal de 1 round de pura sobrevivência.")
    ],
    "versus_title": "MODO VERSUS LOCAL & DUELOS DE IA",
    "versus_desc": (
        "Duelo direto para 2 jogadores locais ou jogador contra Inteligência Artificial. Permite seleção livre "
        "entre todos os 24 lutadores, as 24 arenas temáticas, configuração de rounds (1 a 5) e escolha entre 3 níveis de IA (Fácil, Normal e Difícil)."
    )
}

BOSS_TEASER_PT = {
    "title": "O DESPERTAR PROIBIDO — O CHEFE FINAL",
    "name": "ONI GASHADOKURO (鬼鵺・餓者髑髏)",
    "subtitle": "O Titã Esquelético Forjado no Ódio de Dez Mil Cadáveres sem Sepultura",
    "concept_art": "assets/concepts/gashadokuro_silhouette_tease.jpg",
    "lore": (
        "Nas profundezas insondáveis da Caverna Sombria de Iga, além dos altares milenares e dos selos sagrados "
        "de Shimenawa, jaz o segredo mais apavorante do Japão feudal. O Gashadokuro não é um demônio comum: "
        "ele é uma força da natureza sobrenatural, um titã colossal composto pelos ossos fundidos de todos os combatentes, "
        "camponeses e inocentes massacrados nas guerras sangrentas desde a era Sengoku até o crepúsculo do Bakumatsu. "
        "\n\nOs Ninjas Guardiões de Iga (Hanzo, Kasumi, Murasaki, Chiyo e Joe) dedicaram suas vidas a repelir qualquer "
        "intruso para manter o solo calmo. Mas quando os doze duelos do Modo Arcade chegam ao fim e o sangue dos melhores "
        "espadachins é absorvido pelas fendas da caverna, os grilhões espirituais se partem com o estrondo de um trovão. "
        "Um par de olhos incandescentes acende na escuridão, e uma mão esquelética gigante com garras de ferro emerge "
        "do chão para purgar o mundo dos vivos."
    ),
    "warning_title": "ADVERTÊNCIA TÁTICA DO CONFRONTO FINAL",
    "warning_points": [
        ("Massa Inabalável (Hiper-Armadura)", "O Oni Gashadokuro ignora completamente o recuo de ataques normais de espada. Não tente disputar prioridade frontalmente."),
        ("Impactos de Terremoto & Clava Titânica", "Seus golpes verticais racham o piso da caverna, fazendo desabar estalactites rochosas sobre toda a arena."),
        ("A Janela de Fadiga Espectral", "Após realizar uma sequência colapsante de três golpes devastadores, o Titã entra em um estado momentâneo de exaustão espiritual. Esta é a única brecha para desferir cortes limpos com dano multiplicado."),
        ("Duelo de Round Único", "Não há segunda chance no confronto contra o Gashadokuro. Um único erro de posicionamento resulta em aniquilação imediata.")
    ]
}

APPENDIX_PT = {
    "title": "APÊNDICE TÉCNICO & DIRETRIZES DE COMBATE",
    "tier_title": "TABELA GERAL DE DESEMPENHO & TAXA DE VITÓRIA (6.624 COMBATES SIMULADOS)",
    "tier_desc": (
        "Dados computados a partir da simulação massiva oficial de torneio com paridade simétrica de arenas "
        "(Dohyo Sagrado, Telhados de Iga, Ilha Ganryu e Kyoto em Chamas) contra IA em nível NORMAL:"
    ),
    "tier_table": [
        ("1", "Seimei", "Onmyoji dos Talismãs (Ofuda / Rondel Pentagrama)", "125", "51", "67.9%", "Tier S"),
        ("2", "Teppo", "Marksman de Pólvora (Tanegashima / Baioneta)", "116", "66", "63.0%", "Tier S"),
        ("3", "Hanzo", "Ninja Mestre de Iga (Kunai / Saque Tático)", "115", "69", "62.5%", "Tier S"),
        ("4", "Saitou", "Lobo de Mibu (Shinsengumi / Gatotsu)", "115", "68", "62.5%", "Tier S"),
        ("5", "Hendrika", "Alquimista de Dejima (Florete / 5 Reagentes Alquímicos)", "109", "74", "59.2%", "Tier S"),
        ("6", "Joe", "American Ninja Tático (Shuriken / Fuzil / Doberman)", "108", "76", "58.7%", "Tier S"),
        ("7", "Kenshi", "Retalhador do Crepúsculo (Hiten Iaijutsu / Shukuchi)", "107", "76", "58.1%", "Tier S"),
        ("8", "Tomoe", "Arqueira Miko Sagrada (Arco Longo Yumi / Flecha Espiritual)", "107", "77", "58.1%", "Tier S"),
        ("9", "Murasaki", "Kunoichi das Sombras (Kusarigama Venenosa)", "93", "90", "50.5%", "Tier B"),
        ("10", "Valerius", "Necromante Prussiano (Zweihänder / Chamas Negras)", "93", "91", "50.5%", "Tier B"),
        ("11", "Ichi", "Lâmina Cega (Shikomizue / Gyaku-Iai Reverso)", "92", "90", "50.0%", "Tier B"),
        ("12", "Musashi", "Kensei Duas Lâminas (Niten Ichi-ryu / Katanas Gêmeas)", "87", "96", "47.3%", "Tier B"),
        ("13", "Kasumi", "Kunoichi da Névoa (Ninja-to / Bombas de Fumaça)", "87", "96", "47.3%", "Tier B"),
        ("14", "Aoi", "Caçadora Selvagem Ainu (Arco de Chifre / Makiri Nórdico)", "87", "97", "47.3%", "Tier B"),
        ("15", "Chiyo", "Dançarina das Lâminas (Dual Kodachi Higanbana)", "82", "102", "44.6%", "Tier C"),
        ("16", "Daiki", "Peregrino do Cajado (Bo de Carvalho / Salto com Vara)", "81", "103", "44.0%", "Tier C"),
        ("17", "Goro", "Fazendeiro Rebelde (Foice Kuwa / Pisotão Sísmico)", "80", "103", "43.5%", "Tier C"),
        ("18", "Anne", "Capitã Corsária (Alfanje Pirata 180° / Pistola de Pederneira)", "78", "105", "42.4%", "Tier C"),
        ("19", "Julie", "Mosqueteira Real (Florete Francês / Riposte Preciso)", "77", "107", "41.9%", "Tier D"),
        ("20", "Ren", "Monge dos Punhos Shaolin (Palmas de Ferro / Chute Flurry)", "76", "107", "41.3%", "Tier D"),
        ("21", "O-Rin", "Menestrel de Yoshiwara (Shamisen Cortante / Lâmina Oculta)", "74", "105", "40.2%", "Tier D"),
        ("22", "Okuni", "Sacerdotisa de Kabuki (Leque Tessen Cortante / Miasma)", "70", "113", "38.0%", "Tier D"),
        ("23", "Raiden", "Yokozuna Invicto (Tsuppari Pesado / Empurrão Tachiai)", "68", "111", "37.0%", "Tier D"),
        ("24", "Benkei", "Monge Guerreiro Sohei (Kanabo de Ferro / Naginata Colossal)", "64", "118", "34.8%", "Tier D")
    ],
    "soil_table_title": "TABELA DE REAGENTES DE SOLO & ALQUIMIA CLANDESTINA (HENDRIKA & SEIMEI)",
    "soil_table": [
        ("Armazém de Dejima / Portos", "Enxofre Puro, Salitre Fino, Resíduos Ácidos", "Poção Ácida (Quebra de Guarda) & Fogo Alquímico", "+30% velocidade de coleta de frascos"),
        ("Kyoto em Chamas / Ruas", "Sangue Fresco, Fuligem de Fogo, Pólvora", "Poção Venenosa Fatal & Granada Incendiária", "Resistência a dano contínuo de fogo"),
        ("Bosques / Pinheiros / Taiga", "Raízes Medicinais, Seiva de Pinheiro, Resina", "Elixir de Restauração de HP & Vigor Máximo", "Acelera recuperação de esquiva e rolamento"),
        ("Cemitérios / Caverna Sombria", "Pó Cadavérico, Miasma Fúngico, Cinza Negra", "Névoa Ofuscante & Neurotoxina Paralisante", "Causa lentidão na velocidade do oponente"),
        ("Santuários / Dohyo Sagrado", "Sal Consagrado, Cânfora, Areia Estelar", "Poção de Armadura de Ferro & Elixir de Foco", "Anula sangramento e venenos ativos"),
        ("Planícies de Asuka / Arrozais", "Argila Fina, Água de Nascente, Brotos de Bambu", "Bálsamo Fortificante & Névoa de Camuflagem", "Aumenta distância de impulsão do dash"),
        ("Criptas da Silésia / Enclave", "Prata Fundida, Óleo de Pederneira, Salpetra", "Frasco de Chamas Purificadoras & Ácido Real", "Amplifica atordoamento de contra-golpe")
    ],
    "credits_title": "CRÉDITOS & COLABORADORES",
    "credits": [
        ("Game Designer, Songwriter & Artist", "Colletes"),
        ("Toolset de Desenvolvimento", "Gemini / Antigravity, Suno, Google Flow"),
        ("Dedicatória", "À Lorena. Sempre à Lorena, que me apoia nas minhas loucuras.")
    ],
    "dedication_production": "Inspirado pelas grandes obras e mangás do Japão Feudal."
}
