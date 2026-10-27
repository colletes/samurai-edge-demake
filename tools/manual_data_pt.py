"""
Banco de dados completo em Português para a geração do Manual Oficial de Samurai Edge em PDF.
"""

LORE_PT = {
    "title": "A LENDA DO BAKUMATSU & O SELO DAS CINZAS",
    "p1": (
        "No crepúsculo do século XIX (década de 1860), o Japão foi sacudido pela chegada dos 'Navios Negros' do Ocidente, "
        "rompendo mais de dois séculos de isolamento sagrado (Sakoku). A terra do sol nascente rachou em uma guerra civil "
        "selvagem e impiedosa: de um lado, os lealistas do Xogunato Tokugawa lutando para preservar a ordem feudal; "
        "do outro, os rebeldes e nacionalistas que exigiam a restauração do poder imperial supremo."
    ),
    "p2": (
        "No entanto, sob o véu das disputas políticas e do avanço implacável da pólvora e das armas modernas, uma força "
        "ancestral muito mais aterrorizante começou a se agitar. Na província montanhosa e impenetrável de Iga, sob "
        "o manto perpétuo da Caverna Sombria, jazia selado há mais de mil anos o Oni Gashadokuro: o titã esquelético "
        "colossal forjado a partir do ódio e da agonia de milhares de almas mortas em guerras antigas e deixadas sem sepultura."
    ),
    "p3": (
        "A profecia dos antigos monges de Onmyodo previa que, se o solo do Japão fosse novamente inundado com o sangue "
        "de guerreiros e inocentes sem descanso espiritual, os grilhões mágicos que aprisionavam o titã se romperiam. "
        "Sem saber, cada duelo de espadas travado nos becos em chamas de Kyoto, cada emboscada nas florestas de bambu "
        "e cada execução sumária realizada nas docas chuvosas de Dejima alimenta a escuridão crescente, acelerando o retorno "
        "do titã faminto para extinguir toda a vida nas quatro ilhas do Japão."
    )
}

FACTIONS_PT = [
    {
        "name": "1. Protetores do Povo & Ronins Virtuosos",
        "desc": "Espadachins, arqueiras, monges e camponeses que pegaram em armas não por ambição política, mas para proteger vilarejos, templos e inocentes contra os massacres e pilhagens da guerra civil.",
        "members": ["Kenshi", "Tomoe", "Daiki", "Goro", "Benkei"],
        "philosophy": "A espada que protege a vida (Katsujinken). Defendem os fracos contra a tirania e a violência desenfreada."
    },
    {
        "name": "2. Duelistas do Auge & Buscadores de Glória",
        "desc": "Mestres de artes marciais lendárias que veem o tumulto do Bakumatsu como o crisol definitivo para testar seus limites físicos e espirituais contra os guerreiros mais letais do mundo.",
        "members": ["Musashi", "Ren", "Raiden"],
        "philosophy": "A busca intransigente pela maestria marcial absoluta, onde cada duelo de lâminas é um diálogo com a própria mortalidade."
    },
    {
        "name": "3. Lealistas & Servidores da Ordem",
        "desc": "Guerreiros disciplinados guiados por juramentos inquebrantáveis de lealdade a seus comandantes, ao Xogunato, ao Imperador ou a coroas soberanas estrangeiras.",
        "members": ["Saitou", "Julie", "Ichi"],
        "philosophy": "Dever absoluto, honra militar e lealdade cega à bandeira que juraram servir até o último sopro de vida."
    },
    {
        "name": "4. Oportunistas & Cientistas do Caos",
        "desc": "Eruditos excêntricos, necromantes arcanos e dançarinas místicas que operam nas sombras da guerra civil, aproveitando o sangue derramado para conduzir experimentos proibidos e colher poder sobrenatural.",
        "members": ["Hendrika", "Valerius", "Okuni"],
        "philosophy": "O caos é um laboratório fértil. A moralidade tradicional é descartada em prol do avanço científico e alquímico."
    },
    {
        "name": "5. Mercenários & Corsários de Guerra",
        "desc": "Atiradores de aluguel e navegadores audaciosos que singram as fendas do comércio marítimo e dos conflitos feudais em busca de riqueza, pólvora e liberdade absoluta.",
        "members": ["Anne", "Teppo"],
        "philosophy": "Sobrevivência, ouro e independência. Lutam pelo melhor pagador ou pela própria tripulação sem submissão a senhores feudais."
    },
    {
        "name": "6. Os Guardiões do Selo (Clã Shinobi de Iga)",
        "desc": "A elite das sombras de Iga. Aparentam ser assassinos impiedosos, mas na verdade formam a linha secreta de defesa que guarda a Caverna Sombria para impedir que o Oni Gashadokuro desperte.",
        "members": ["Hanzo", "Kasumi", "Murasaki"],
        "philosophy": "Sacrifício invisível. Manter o titã adormecido mesmo que o mundo os veja como vilões e sombras cruéis."
    },
    {
        "name": "7. O Viajante Temporal & Aliado Inusitado",
        "desc": "Um fuzileiro americano e agente tático do século XXI, fanático por cultura pop japonesa e animes, que acidentalmente viajou no tempo para o crepúsculo do xogunato.",
        "members": ["Joe"],
        "philosophy": "Sobrevivência com estilo ninja tático moderno. Ao descobrir a nobre causa dos ninjas de Iga, jurou protegê-los com seu cão e seu arsenal militar."
    }
]

CONTROLS_PT = {
    "title": "COMANDOS BÁSICOS & SISTEMA DE DUELO",
    "desc": (
        "Samurai Edge utiliza um sistema de combate isométrico diegético inspirado no cinema clássico de Akira Kurosawa "
        "e na precisão cirúrgica de Bushido Blade. Cada golpe carrega letalidade brutal e posicionamento tridimensional estrito."
    ),
    "table": [
        ("Movimento 8-Way", "D-Pad / Analógico Esquerdo", "[W, A, S, D] (P1) / [Setas] (P2)", "Deslocamento e posicionamento tático na arena"),
        ("Ataque Primário", "Botão X / Quadrado", "[E] (P1) / [U] (P2)", "Golpe principal da arma (saque, corte, estocada ou tiro)"),
        ("Ação Secundária", "Botão Y / Triângulo", "[R] (P1) / [I] (P2)", "Habilidade especial, projétil, postura ou magia alquímica"),
        ("Defesa / Parry", "Botão RB / R1", "[F] (P1) / [O] (P2)", "Postura de bloqueio com janela de parry e deflexão de projéteis"),
        ("Esquiva / Rolamento", "Botão A / Cruz", "[Espaço] (P1) / [P] (P2)", "Rolamento acrobático com frames de invulnerabilidade"),
        ("Salto Tático", "Botão LB / L1", "[Q] (P1) / [Y] (P2)", "Salto vertical/direcional sobre buracos e fossos"),
        ("Pausa / Menu", "Start / Opções", "[ESC]", "Pausa cerimonial em pergaminho Sumi-E")
    ],
    "mechanics": [
        ("Choque de Lâminas (Clash QTE)", "Quando dois ataques simultâneos colidem no mesmo frame espacial, as lâminas se travam com faíscas cinemáticas. O combatente que pressionar o botão de ataque mais rápido no micro-evento vence o choque e desequilibra o rival com recuo forçado."),
        ("Precedência Absoluta", "Certos golpes (como a Foice da Kusarigama de Murasaki ou a Estocada de Hendrika) possuem prioridade matemática garantida, vencendo disputas normais e cortando a iniciativa do oponente."),
        ("Quebra de Postura (Guard Crush)", "Golpes banhados em ácido, projéteis pesados de artilharia ou martelos titânicos quebram defesas de Parry, aplicando Stun prolongado no defensor."),
        ("Letalidade Cirúrgica", "Os lutadores possuem entre 1 e 3 Pontos de Vida (HP). Um único acerto limpo em momento de recuperação ou contra-ataque decide o destino do round instantaneamente.")
    ]
}

MODES_PT = {
    "title": "MODOS DE COMBATE & PROGRESSÃO",
    "arcade_title": "MODO ARCADE — A JORNADA DE 12 LUTAS",
    "arcade_desc": (
        "A campanha solo definitiva. O jogador escolhe seu guerreiro e avança por uma escada de 12 confrontos rituais "
        "onde o sangue derramado ecoa pelos quatro cantos do Japão, desestabilizando o selo da Caverna Sombria:"
    ),
    "arcade_stages": [
        ("Lutas 1 a 8: Duelos Ranqueados", "Confrontos clássicos Melhor-de-3 (BO3) contra 8 guerreiros sorteados democraticamente entre todas as 4 faixas de dificuldade, garantindo jornadas sempre imprevisíveis."),
        ("Luta 9: Confronto de Espelho (Mirror Match)", "O guerreiro enfrenta sua própria sombra espectral em sua arena natal. Uma batalha psicológica e técnica com paridade absoluta de armas."),
        ("Luta 10: Desafio de Resistência (Endurance Challenge)", "Dois adversários de elite consecutivos em sequência ininterrupta, compartilhando apenas 2 vidas de round. A vitória exige compostura e gestão de espaço."),
        ("Luta 11: O Desafio dos Guardiões (Ninja Challenge)", "Entrada na Caverna Sombria de Iga. O jogador deve derrotar a falange completa dos 4 Ninjas Guardiões (Joe, Kasumi, Murasaki e Hanzo) sob névoa venenosa."),
        ("Luta 12: O Despertar do Titã (Final Boss)", "Com a queda dos guardiões, o selo milenar se rompe. O gigantesco Oni Gashadokuro ergue-se das cinzas da caverna em um duelo colossal de 1 round de pura sobrevivência.")
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
        "\n\nOs quatro Ninjas Guardiões de Iga (Hanzo, Kasumi, Murasaki e Joe) dedicaram suas vidas a repelir qualquer "
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
        ("15", "Chiyo", "Dançarina das Lâminas (Dual Nodachi Higanbana)", "82", "102", "44.6%", "Tier C"),
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
        ("Armazém de Dejima / Portos", "Enxofre Puro, Salitre Fino, Resíduos Ácidos", "Poção Ácida (Quebra de Guarda) & Fogo Alquímico", "+30% velocidade de coleta"),
        ("Kyoto em Chamas / Ruas", "Sangue Fresco, Fuligem de Fogo, Pólvora", "Poção Venenosa Fatal & Granada Incendiária", "Resistência a dano de fogo"),
        ("Bosques / Pinheiros / Taiga", "Raízes Medicinais, Seiva de Pinheiro, Resina", "Elixir de Restauração de HP & Vigor Máximo", "Acelera recuperação de esquiva"),
        ("Cemitérios / Caverna Sombria", "Pó Cadavérico, Miasma Fúngico, Cinza Negra", "Névoa Ofuscante & Neurotoxina Paralisante", "Causa lentidão no oponente"),
        ("Santuários / Dohyo Sagrado", "Sal Consagrado, Cânfora, Areia Estelar", "Poção de Armadura de Ferro & Elixir de Foco", "Anula venenos e sangramento")
    ],
    "credits_title": "CRÉDITOS DA PRODUÇÃO",
    "credits": [
        ("Concepção Original & Game Design", "Thiago Carvalho"),
        ("Arquitetura de Código & Engenharia de IA", "Antigravity AI (Google DeepMind)"),
        ("Direção de Arte & Modelagem Voxel 3D", "Estúdio Samurai Edge Bakumatsu"),
        ("Música & Paisagens Sonoras", "Composições Originais do Folclore Bakumatsu"),
        ("Dedicatória Especial", "A todos os mestres do cinema épico de samurai e da era de ouro dos jogos de luta dos anos 90.")
    ]
}
