"""
Banco de dados estrategico das 24 Arenas de Samurai Edge (Bilingue PT/EN).
Atualizado com os perigos e fossos exatos do motor de jogo.
"""

ARENAS_DATA = [   {   'concept_art': 'assets/concepts/bamboo_forest_concept.jpg',
        'fighter_id': 'kenshin',
        'hazards_en': 'Zero environmental traps and zero ring-out pits. Pure neutral duel ground: bamboo stalks can be '
                      'sliced by weapon strikes to clear open charge corridors.',
        'hazards_pt': 'Sem perigos ambientais ou fossos de queda. Arena neutra e pura: os colmos de bambu podem ser '
                      'cortados por golpes de espada para abrir novas linhas de investida.',
        'historical_context_en': 'The dense bamboo groves of Sagano and Arashiyama served as clandestine hideouts and '
                                 'escape corridors for imperial loyalists hunted by Shogunate forces. The constant '
                                 'rustling of tall bamboo culms muffled the footsteps of political assassins and '
                                 "wandering ronin. In the game's lore, it marks the spiritual frontier where Kenshi "
                                 'meditates and shields rural pilgrims from brutal martial patrols.',
        'historical_context_pt': 'As densas florestas de bambu de Sagano e Arashiyama serviam como refúgio clandestino '
                                 'e rotas de fuga para lealistas imperiais perseguidos pelas forças do Xogunato. O '
                                 'farfalhar constante dos colmos altos ao vento abafava os passos de assassinos '
                                 'políticos e ronins errantes. Na mitologia do jogo, é a fronteira espiritual onde '
                                 'Kenshi medita e defende os peregrinos rurais contra as patrulhas violentas.',
        'id': 'bamboo',
        'location_en': 'Arashiyama, Western Outskirts of Kyoto (Autumn 1863)',
        'location_pt': 'Arashiyama, Periferia Oeste de Kyoto (Outono de 1863)',
        'name_en': 'Sacred Bamboo Grove (Arashiyama)',
        'name_pt': 'Bosque de Bambu Sagrado (Arashiyama)',
        'soil_alchemy_en': 'Soil: Moist vegetal humus and rich black loam. Hendrika Gathering: Medicinal Roots and '
                           'Plant Charcoal (Essential for Healing and Stamina draughts). Seimei: Pure Wood elemental '
                           'resonance.',
        'soil_alchemy_pt': 'Solo: Húmus vegetal úmido e terra negra rica em matéria orgânica. Coleta de Hendrika: '
                           'Raízes Medicinais e Carvão Vegetal (Chave para Poções de Cura e Estamina). Seimei: '
                           'Propriedades puras do elemento Madeira (Wood).',
        'tactics_en': 'Slice bamboo stalks with horizontal slashes to clear direct charge corridors. Exploit dense '
                      'vegetation to deflect incoming arrows and rifle rounds. Pressure opponents toward cliff ledges '
                      'for swift ring-out finishes.',
        'tactics_pt': 'Corte o bambu com golpes cortantes para abrir linhas de investida direta. Use a vegetação densa '
                      'para desviar flechas e disparos de pólvora. Force o oponente em direção às margens do '
                      'desfiladeiro para vitórias rápidas por ring-out.'},
    {   'concept_art': 'assets/concepts/ganryu_island_concept.jpg',
        'fighter_id': 'musashi',
        'hazards_en': '4 ring-out pits (deep ocean waters beyond the beach). Active hazard: periodic high-tide surges '
                      'sweep across the sand, dragging combatants toward drowning boundaries.',
        'hazards_pt': '4 fossos de queda (mar profundo nas bordas). Perigo ativo: ondas de mare alta (Tide Surge) '
                      'varrem a praia periodicamente, empurrando lutadores em direcao ao afogamento.',
        'historical_context_en': 'The legendary sandbar island in the maritime strait where Miyamoto Musashi and '
                                 "Sasaki Kojiro fought history's most famous duel in 1612. During the Bakumatsu, the "
                                 'strait became ground zero for Western naval bombardments against the Choshu domain. '
                                 'Its white sand beaches and jagged reefs are swept by salty spray and treacherous '
                                 'tides, preserving the sacred aura of the ultimate martial proving ground.',
        'historical_context_pt': 'A lendária ilha deserta no estreito marítimo onde Miyamoto Musashi e Sasaki Kojiro '
                                 'travaram o maior duelo da história japonesa em 1612. Durante o Bakumatsu, o estreito '
                                 'tornou-se palco de bombardeios navais ocidentais contra o domínio Choshu. A praia de '
                                 'areia branca e rochedos pontiagudos é varrida por maresia salgada e marés '
                                 'traiçoeiras, preservando a aura mística do teste marcial supremo.',
        'id': 'ganryu',
        'location_en': 'Kanmon Strait, Seto Inland Sea (Misty Dawn)',
        'location_pt': 'Estreito de Kanmon, Mar Interior de Seto (Madrugada de Névoa)',
        'name_en': 'Duel on Ganryu Island (Funajima)',
        'name_pt': 'Duelo na Ilha Ganryu (Funajima)',
        'soil_alchemy_en': 'Soil: Saline sea sand, crushed shells, and limestone silt. Hendrika Gathering: Refined '
                           'Saltpeter and Brine Ash (Critical explosive reagent). Seimei: High Water elemental '
                           'resonance.',
        'soil_alchemy_pt': 'Solo: Areia marinha salina, conchas trituradas e depósitos de calcário. Coleta de '
                           'Hendrika: Salitre Purificado e Cinzas de Salmoura (Componente explosivo crítico). Seimei: '
                           'Ressonância elemental pura de Água (Water).',
        'tactics_en': 'Vast, open shoreline favoring technical spacing and mid-range dueling. Dominate the central '
                      'sand strip; fighters backed into the tidal surf suffer dodge deceleration and risk instant '
                      'drowning knockouts.',
        'tactics_pt': 'Arena ampla e desobstruída favorável a duelos técnicos de espaçamento puro. Controle o centro '
                      'da faixa de areia; quem for encurralado na linha de maré perde mobilidade de esquiva e fica '
                      'vulnerável a arremessos letais nas ondas.'},
    {   'concept_art': 'assets/concepts/iga_rooftops_concept.jpg',
        'fighter_id': 'ninja',
        'hazards_en': '7 vertical ring-out drops (instant fatal falls off roof perimeters). Terracotta chimneys and '
                      'ridge tiles provide solid obstacle cover.',
        'hazards_pt': '7 fossos de queda vertical (queda fatal imediata nos beirais dos telhados). Chamines de '
                      'terracota e telhas ornamentais agem como obstaculos de cobertura.',
        'historical_context_en': 'The ancestral mountain stronghold of the Shinobi clans in the rugged heights of Iga '
                                 'Province. Engineered with steep ceramic-tiled roofs and sweeping eves designed to '
                                 'break conventional infantry assaults. Under torrential Bakumatsu rain, Hanzo and his '
                                 'disciples maintain eternal watch over the subterranean passages descending into '
                                 "Gashadokuro's Shadow Cave.",
        'historical_context_pt': 'A fortaleza ancestral dos clãs Shinobi nas montanhas isoladas da província de Iga. '
                                 'Fortificada com telhados íngremes de telhas cerâmicas e beirais pontiagudos '
                                 'projetados para dificultar invasões de infantaria. Sob a chuva torrencial do '
                                 'Bakumatsu, Hanzo e seus discípulos mantêm vigília eterna sobre as passagens secretas '
                                 'que descem até a Caverna Sombria do Gashadokuro.',
        'id': 'iga',
        'location_en': 'Shadow Castle, Mountainous Iga Province (Rainy Midnight)',
        'location_pt': 'Castelo das Sombras, Província Montanhosa de Iga (Meia-Noite Chuvosa)',
        'name_en': 'Night Rooftops of Iga',
        'name_pt': 'Telhados Noturnos de Iga',
        'soil_alchemy_en': 'Soil: Glazed ceramic tiles, aged chimney soot, and kiln clay. Hendrika Gathering: Dry '
                           'Sulfur and Concentrated Soot (Crucial for Acid Bombs and Smoke Screens). Seimei: Strong '
                           'Fire and Metal elemental affinity.',
        'soil_alchemy_pt': 'Solo: Telhas cerâmicas vitrificadas, fuligem antiga e argila cozida. Coleta de Hendrika: '
                           'Enxofre Seco e Fuligem Concentrada (Essencial para Bombas Ácidas e Granadas de Fumaça). '
                           'Seimei: Afinidade com Fogo e Metal.',
        'tactics_en': 'Ring-out edge control is paramount. Fighters boasting high-recoil strikes (such as Hanzo and '
                      'Musashi) can terminate rounds in under three seconds. Strictly avoid panic rolling toward outer '
                      'corner diagonals.',
        'tactics_pt': 'O controle de borda é a chave absoluta nesta arena. Personagens com ataques de empurrão (como '
                      'Hanzo e Musashi) conseguem finalizar o round em menos de três segundos. Evite rolar '
                      'descontroladamente para as diagonais externas.'},
    {   'concept_art': 'assets/concepts/forest_camp_concept.jpg',
        'fighter_id': 'american',
        'hazards_en': 'No ring-out pits and zero lethal traps. Central campfire dealing contact burn ticks and '
                      'destructible wooden crates for ballistic cover.',
        'hazards_pt': 'Sem fossos de queda e sem armadilhas letais. Fogueira central que causa dano ao contato e '
                      'caixas de madeira destrutiveis para cobertura tatica.',
        'historical_context_en': 'A camouflaged forward operating camp sheltered beneath ancient oaks where Joe '
                                 'established his sanctuary after being displaced across time. Modern military supply '
                                 'crates sit beside Shinobi scrolls and field campfires. Here, Joe drills his tactical '
                                 "doberman 'Shadow' and hones modern combat blades while deciphering ancient Iga seal "
                                 'charts.',
        'historical_context_pt': 'Uma base de operações camuflada entre carvalhos centenários onde Joe montou seu '
                                 'refúgio após ser arremessado no tempo. Caixas de suprimentos militares modernos '
                                 'misturam-se a pergaminhos ninjas e fogueiras de campanha. É o local onde Joe treina '
                                 "seu doberman 'Shadow' e afia suas lâminas táticas enquanto estuda os mapas do selo "
                                 'milenar de Iga.',
        'id': 'forest_camp',
        'location_en': 'Hidden Grove in the Iga Valleys (Overcast Dusk)',
        'location_pt': 'Bosque Oculto nos Vales de Iga (Tarde Encoberta)',
        'name_en': 'Secret Forest Outpost',
        'name_pt': 'Acampamento Secreto na Floresta',
        'soil_alchemy_en': 'Soil: Compacted dirt infused with campfire embers, fallen foliage, and stray gunpowder. '
                           'Hendrika Gathering: Plant Charcoal and Coarse Black Powder. Seimei: Wood and Fire '
                           'elemental synthesis.',
        'soil_alchemy_pt': 'Solo: Terra batida misturada com cinzas de fogueira, folhas secas e pólvora descartada. '
                           'Coleta de Hendrika: Carvão Vegetal e Pólvora Negra Concentrada. Seimei: Propriedades de '
                           'Madeira e Fogo.',
        'tactics_en': 'Use supply crates as ballistic cover against snipers and throwing stars. Herd opponents into '
                      'the central fire pit to disrupt defensive stances and guarantee clean follow-up strikes.',
        'tactics_pt': 'Use as caixas de suprimentos como cobertura tática contra atiradores e projéteis. Force o '
                      'adversário contra as chamas da fogueira central para interromper posturas defensivas e aplicar '
                      'punições limpas.'},
    {   'concept_art': 'assets/concepts/kyoto_bakumatsu_concept.jpg',
        'fighter_id': 'saitou',
        'hazards_en': 'No ring-out pits. Active hazards: speeding noble ox-carriages periodically barrel through the '
                      'street trampling fighters, alongside falling burning debris and roof tiles.',
        'hazards_pt': 'Sem fossos de queda. Perigos ativos: carruagens nobres em alta velocidade cruzam a via '
                      'periodicamente atropelando lutadores, e escombros e telhas incandescentes chovem do ceu.',
        'historical_context_en': 'The ancient imperial capital engulfed in infernos during the Hamaguri Gate rebellion '
                                 "and the Shinsengumi's raid on the Ikedaya Inn. Aristocratic palanquins blaze amid "
                                 "cobblestone thoroughfares as the 'Wolves of Mibu' hunt without quarter. The blood "
                                 "pooling upon Kyoto's stone streets directly feeds Gashadokuro's subterranean "
                                 'awakening.',
        'historical_context_pt': 'A antiga capital imperial consumida pelas chamas durante a rebelião Hamaguri e o '
                                 'ataque do Shinsengumi à hospedaria Ikedaya. Carruagens nobres ardem no meio das ruas '
                                 "empedradas enquanto os 'Lobos de Mibu' patrulham sem piedade. O sangue que mancha os "
                                 'paralelepípedos desta noite alimenta diretamente o despertar do Gashadokuro nas '
                                 'profundezas da terra.',
        'id': 'kyoto',
        'location_en': 'Sanjo District, Kyoto (Ikedaya Incident, Night of 1864)',
        'location_pt': 'Distrito de Sanjo, Kyoto (Incidente Ikedaya, Noite de 1864)',
        'name_en': 'Kyoto: Bakumatsu in Flames',
        'name_pt': 'Kyoto: Bakumatsu em Chamas',
        'soil_alchemy_en': 'Soil: Granite paving stones drenched in blood and burning embers. Hendrika Gathering: '
                           'Gunpowder Sulfur and Fresh Blood Residue (Prime reagents for Poison and Acid vials). '
                           'Seimei: Overwhelming Fire and Earth alignment.',
        'soil_alchemy_pt': 'Solo: Paralelepípedos de granito encharcados de sangue e fuligem urbana. Coleta de '
                           'Hendrika: Enxofre de Pólvora e Sangue de Combatente (Matéria-prima de Poções Venenosas e '
                           'Ácido). Seimei: Propriedades intensas de Fogo e Terra.',
        'tactics_en': "Dense urban corridor with straight sightlines ideal for Saitou's Gatotsu thrusts. Shove "
                      'adversaries into the burning carriage wheels to trigger instant guard breaks and lethal '
                      'openings.',
        'tactics_pt': 'Espaço urbano denso com linhas de choque retilíneas perfeitas para a estocada Gatotsu de '
                      'Saitou. Empurre os inimigos contra as rodas em chamas da carruagem para garantir quebras de '
                      'postura instantâneas.'},
    {   'concept_art': 'assets/concepts/nagashino_field_concept.jpg',
        'fighter_id': 'rifleman',
        'hazards_en': 'No ring-out pits. Pointed wooden anti-cavalry palisades and deep mud trenches that reduce '
                      'running movement speed.',
        'hazards_pt': 'Sem fossos de queda. Palicadas pontiagudas anti-cavalaria de madeira e trincheiras de lama '
                      'pesada que reduzem a velocidade de deslocamento.',
        'historical_context_en': 'The historic battlefield where synchronized Tanegashima matchlock volleys shattered '
                                 'the invincible Takeda cavalry in 1575, re-established during the Bakumatsu as a '
                                 'proving ground for rifled infantry warfare. Barbed wooden palisades and muddy '
                                 "trenches memorialize gunpowder's bloody victory over feudal sword tradition.",
        'historical_context_pt': 'O campo de batalha histórico onde as voleios de arcabuzes Tanegashima dizimaram a '
                                 'outrora invencível cavalaria Takeda em 1575, reaberto no Bakumatsu como terreno de '
                                 'testes para a moderna infantaria de fuzil rifado. Paliçadas de madeira farpada e '
                                 'trincheiras de lama marcam o triunfo da pólvora sobre a tradição da espada feudal.',
        'id': 'nagashino',
        'location_en': 'Shitaragahara Plains, Mikawa Province (Misty Dawn)',
        'location_pt': 'Planície de Shitaragahara, Província de Mikawa (Alvorecer Nebuloso)',
        'name_en': 'Trenches of Nagashino',
        'name_pt': 'Trincheiras de Nagashino',
        'soil_alchemy_en': 'Soil: Heavy rain-saturated clay, oxidized iron filings, and aged gunpowder silt. Hendrika '
                           'Gathering: Crude Saltpeter and Iron Ore (Enhances explosive shrapnel damage). Seimei: '
                           'Earth and Metal elemental balance.',
        'soil_alchemy_pt': 'Solo: Argila pesada saturada de chuva, ferro oxidado e resíduos de pólvora antiga. Coleta '
                           'de Hendrika: Salitre e Minério de Ferro (Aumenta dano de estilhaços). Seimei: Propriedades '
                           'equilibradas de Terra e Metal.',
        'tactics_en': 'Control firing lanes between palisade rows to pin agile duelists. Funnel sprinting foes into '
                      'deep mud to rob their dash momentum, leaving them open to long-range rifle volleys and bayonet '
                      'lunges.',
        'tactics_pt': 'Mantenha a infantaria e os duelistas afastados controlando as linhas entre as paliçadas. '
                      'Utilize o terreno lamacento para prender oponentes rápidos em disparos de fuzil de longa '
                      'distância e arremessos de baioneta.'},
    {   'concept_art': 'assets/concepts/shadow_cave_concept.jpg',
        'fighter_id': 'purple',
        'hazards_en': 'No ring-out pits. Active hazard: massive swinging iron-chain pendulums and volcanic rocks '
                      'sweeping through the cavern dealing blunt knockback.',
        'hazards_pt': 'Sem fossos de queda. Perigo ativo: pendulos gigantescos de correntes de ferro suspensas e '
                      'rochas vulcanicas oscilam na caverna causando dano contundente.',
        'historical_context_en': 'A cavernous volcanic underworld where the founders of the Iga clan raised guardian '
                                 'monoliths and sacred Shimenawa ropes to seal the colossal skeletal remains of Oni '
                                 'Gashadokuro. Miasmic vapors rising from subterranean fissures distort perception. '
                                 'Murasaki guards the central shrine, wielding her venomous kusarigama to ensure no '
                                 'outsider spills the innocent blood needed to revive the titan.',
        'historical_context_pt': 'Um complexo de cavernas vulcânicas subterrâneas onde os fundadores do clã Iga '
                                 'ergueram estátuas guardiãs e cordas sagradas Shimenawa para selar os ossos colossais '
                                 'do Oni Gashadokuro. A névoa miasmática que emana das fendas na rocha corrompe os '
                                 'sentidos. Murasaki vigia a câmara central, empunhando sua kusarigama venenosa para '
                                 'garantir que nenhum intruso derrame sangue suficiente para despertar a abominação.',
        'id': 'shadow_cave',
        'location_en': 'Subterranean Deeps of Mount Suzuka, Iga Border (Eternal Stygian Dark)',
        'location_pt': 'Profundezas Subterrâneas do Monte Suzuka, Fronteira de Iga (Eterna Escuridão)',
        'name_en': 'Shadow Cave of the Seal',
        'name_pt': 'Caverna Sombria do Selo',
        'soil_alchemy_en': 'Soil: Volcanic basalt, bioluminescent cave fungi, and cursed skeletal ash. Hendrika '
                           'Gathering: Concentrated Miasma and Toxic Spores (Lethal Poison Vial brew). Seimei: '
                           'Corrupted Earth and Shadow resonance.',
        'soil_alchemy_pt': 'Solo: Basalto vulcânico, fungos cavernosos fluorescentes e cinzas amaldiçoadas. Coleta de '
                           'Hendrika: Miasma Concentrado e Fungo Venenoso (Poção Venenosa Fatal). Seimei: Propriedades '
                           'corrompidas de Escuridão e Terra.',
        'tactics_en': 'Exploit cave pillars to wrap curved kusarigama strikes around solid cover. Anchor fights near '
                      'toxic gas vents to subject opponents to continuous health attrition while maintaining mid-range '
                      'zoning.',
        'tactics_pt': 'Aproveite as sombras e o alcance curvado da Kusarigama para golpear além dos pilares de pedra. '
                      'Posicione-se próximo às fendas de gás para que o oponente sofra envenenamento passivo durante o '
                      'duelo.'},
    {   'concept_art': 'assets/concepts/mist_temple_concept.jpg',
        'fighter_id': 'gray',
        'hazards_en': 'No ring-out pits. Active hazard: ceremonial firework mortar explosions detonating on the floor '
                      'creating shockwaves and dense smoke screens.',
        'hazards_pt': 'Sem fossos de queda. Perigo ativo: morteiros de fogos rituais estouram no piso criando '
                      'explosoes de polvora e densas cortinas de fumaca.',
        'historical_context_en': 'An ancient Buddhist sanctuary perched upon the mist-shrouded crags of Mount Hiei, '
                                 'featuring polished cedar decking and translucent shoji screens. Amid the convulsions '
                                 'of the Bakumatsu, the mountain temple served as a spiritual refuge and elite '
                                 'training monastery for Iga kunoichi. Dense highland mist veils moss-covered stone '
                                 'steps and sheer precipices.',
        'historical_context_pt': 'Um templo budista antigo erguido nos picos enevoados do Monte Hiei, com pisos de '
                                 'ripas de cedro polidas e portas shoji translúcidas. Durante a convulsão do '
                                 'Bakumatsu, o mosteiro serviu de refúgio espiritual e escola de treinamento para '
                                 'kunoichis do clã Iga. A densa névoa da montanha oculta degraus milenares e abismos '
                                 'vertiginosos cobertos de musgo.',
        'id': 'mist_temple',
        'location_en': 'Tendai Monastery in the Heights of Mount Hiei (Morning Mist)',
        'location_pt': 'Mosteiro de Tendai nas Alturas de Hiei (Neblina Matinal)',
        'name_en': 'Hidden Mist Temple',
        'name_pt': 'Templo da Névoa Oculta',
        'soil_alchemy_en': 'Soil: Weathered cedar planks, highland moss, and ceremonial incense ash. Hendrika '
                           'Gathering: Cedar Resin and Temple Incense Powder (Stamina regeneration draughts). Seimei: '
                           'Wind and Water elemental harmony.',
        'soil_alchemy_pt': 'Solo: Madeira de cedro envelhecida, musgo de altitude e incenso cerimonial. Coleta de '
                           'Hendrika: Resina de Cedro e Cinzas de Mirra (Acelera recuperação de vigor). Seimei: '
                           'Propriedades puras de Vento e Água.',
        'tactics_en': 'Mist patterns favor stealth repositioning and high-agility dodge rolls. Slash open shoji walls '
                      'to create flanking corridors and bait opponents toward exposed cliff drops behind shattered '
                      'woodwork.',
        'tactics_pt': 'A névoa favorece técnicas furtivas e esquivas de alta agilidade. Destrua os biombos para criar '
                      'novas rotas de flanco e use o tatame central para confundir o alcance do adversário com ataques '
                      'aéreos.'},
    {   'concept_art': 'assets/concepts/kabuki_stage_concept.jpg',
        'fighter_id': 'kabuki',
        'hazards_en': 'No ring-out pits. Active hazard: the central mechanical rotating turntable shifts beneath '
                      'fighters feet, continuously altering spatial alignment.',
        'hazards_pt': 'Sem fossos de queda. Perigo ativo: a plataforma central giratoria (rotunda mecanica) gira sob '
                      'os pes dos guerreiros alterando o posicionamento relativo.',
        'historical_context_en': 'The historic birthplace of Kabuki theater founded by priestess Izumo no Okuni on the '
                                 'riverbanks of the Kamo River. Raised on pine stilts over flowing river waters, the '
                                 'hinoki wood stage is adorned with crimson silk lanterns and golden fans. During '
                                 'Bakumatsu festival nights, flamboyant dramatic performances masked secret conclaves '
                                 'between imperial conspirators and mystic courtesans.',
        'historical_context_pt': 'O berço histórico do teatro Kabuki fundado pela sacerdotisa Izumo no Okuni nas '
                                 'margens do Rio Kamo. Construído sobre pilares de pinho sobre a água corrente, o '
                                 'tablado de tábuas de hinoki é decorado com lanternas de seda vermelha e leques '
                                 'dourados. Durante as noites de festival no Bakumatsu, apresentações dramáticas '
                                 'mascaravam reuniões conspiratórias entre rebeldes imperiais e cortesãs místicas.',
        'id': 'kabuki_stage',
        'location_en': 'Dry Riverbed of the Kamo River, Shijo-Kawaramachi, Kyoto (Festive Dusk)',
        'location_pt': 'Leito Arenoso do Rio Kamo, Shijo-Kawaramachi, Kyoto (Entardecer Festivo)',
        'name_en': 'Floating Kabuki Stage',
        'name_pt': 'Palco Flutuante de Kabuki',
        'soil_alchemy_en': 'Soil: Polished Hinoki cypress planks and ceremonial white rice powder (Oshiroi). Hendrika '
                           'Gathering: Alkaline Face Chalk and Noble Wood Rosin (Blinding smoke mixtures). Seimei: '
                           'Vibrant Wood and Fire resonance.',
        'soil_alchemy_pt': 'Solo: Tábuas polidas de cipreste Hinoki e pó cerimonial de arroz (Oshiroi). Coleta de '
                           'Hendrika: Pó Facial Alcalino e Resina de Madeira Nobre (Criação de névoas ofuscantes). '
                           'Seimei: Propriedades ricas de Madeira e Fogo.',
        'tactics_en': 'The compact square platform amplifies spatial danger. Sweep opponents toward the open water '
                      'edges with wide fan arcs and spinning strikes to achieve sudden ring-out victories.',
        'tactics_pt': 'O formato quadrado e compacto do tablado torna qualquer erro de posicionamento fatal. Force o '
                      'rival para as bordas aquáticas utilizando golpes giratórios de leque e ataques em arco amplo '
                      'para vencer por expulsão.'},
    {   'concept_art': 'assets/concepts/mountain_shrine_concept.jpg',
        'fighter_id': 'archer',
        'hazards_en': 'No ring-out pits and zero lethal traps. Sacred vermilion Torii pillars and stone steps '
                      'obstructing straight arrow volleys and lunges.',
        'hazards_pt': 'Sem fossos de queda e sem perigos letais. Portais Torii de madeira sagrada e degraus de pedra '
                      'que bloqueiam disparos de flechas e estocadas em linha reta.',
        'historical_context_en': 'The ancient mountain shrine where, legend tells, Minamoto no Yoshitsune learned '
                                 'swordcraft from the Great Tengu. Rows of vermilion Torii gates lead to a flagstone '
                                 'courtyard encircled by thousand-year-old cedars. Tomoe masters her Yumi archery in '
                                 'these sacred highlands, safeguarding holy temple scrolls from the profanations of '
                                 'civil war.',
        'historical_context_pt': 'O santuário ancestral de montanha onde, segundo a lenda, Minamoto no Yoshitsune '
                                 'aprendeu os segredos da espada com o Grande Tengu. Portais Torii de vermelhão '
                                 'enfileirados conduzem ao pátio de pedra cercado por cedros milenares. Tomoe treina '
                                 'seu tiro com arco Yumi nestas alturas sagradas, protegendo os registros secretos dos '
                                 'templos contra a profanação das guerras feudais.',
        'id': 'mountain_shrine',
        'location_en': 'Spiritual Peak of Mount Kurama, North of Kyoto (Golden Sunset)',
        'location_pt': 'Pico Espiritual do Monte Kurama, Norte de Kyoto (Tarde Dourada)',
        'name_en': 'Sacred Mountain Shrine',
        'name_pt': 'Santuário da Montanha Sagrada',
        'soil_alchemy_en': 'Soil: Sacred white gravel (Shirakawa-suna), mountain loam, and cedar needles. Hendrika '
                           'Gathering: Purified Cinnabar and Camphor Crystals (Focus and Stamina enhancements). '
                           'Seimei: Pure Heaven, Metal, and Wood alignment.',
        'soil_alchemy_pt': 'Solo: Cascalho branco sagrado (Shirakawa-suna), terra montanhosa e agulhas de cedro. '
                           'Coleta de Hendrika: Minério Sagrado e Cânfora de Madeira (Poções de Foco e Estamina). '
                           'Seimei: Ressonância com Céu, Metal e Madeira.',
        'tactics_en': 'Archetype playground for archers and marksmen. Interpose heavy Torii pillars between yourself '
                      'and melee rushers, loosing charged arrows as they emerge from cover.',
        'tactics_pt': 'Ideal para atiradores de elite. Utilize as colunas dos portais Torii para quebrar o avanço de '
                      'combatentes de espada curta, disparando flechas perfurantes nos momentos em que o oponente '
                      'contorna os pilares.'},
    {   'concept_art': 'assets/concepts/pirate_deck_concept.jpg',
        'fighter_id': 'pirate',
        'hazards_en': '5 ocean ring-out drops beyond the gunwales. Active hazard: violent gale-force ship rolling that '
                      'forces combatants across the tilting deck.',
        'hazards_pt': '5 fossos de queda no oceano alem da amurada. Perigo ativo: balanco violento do navio sob '
                      'tempestade (Ship Roll) que empurra os lutadores de um bordo ao outro.',
        'historical_context_en': 'The iron-reinforced oak deck of the privateer frigate captained by Anne Bonny. '
                                 "Anchored near Uraga Bay where the American 'Black Ships' first forced Japan's "
                                 'opening in 1853. Heavy bronze cannons are lashed with hemp, rum barrels and '
                                 'gunpowder kegs roll across deck planks with the swell, and violent storm waves crash '
                                 'against the hull.',
        'historical_context_pt': 'O convés de carvalho reforçado do galeão corsário capitaneado por Anne Bonny. '
                                 "Ancorado nas proximidades de Uraga onde os 'Navios Negros' americanos desembarcaram "
                                 'pela primeira vez forçando a abertura do Japão em 1853. Canhões navais de bronze '
                                 'estão trancados com cordas, barris de rum e pólvora rolam com o balanço das ondas, e '
                                 'o mar revolto ruge logo abaixo dos mastros sob chuva torrencial.',
        'id': 'pirate_deck',
        'location_en': 'Uraga Bay, Kanagawa Coast (Night High-Seas Gale)',
        'location_pt': 'Baía de Uraga, Costa de Kanagawa (Tempestade Noturna em Alto-Mar)',
        'name_en': 'Privateer Ship Deck',
        'name_pt': 'Convés do Navio Corsário',
        'soil_alchemy_en': 'Soil: Tarred teak planking, crusted sea salt, and naval flint grit. Hendrika Gathering: '
                           'Maritime Pitch and Refined Saltpeter (Greatly expands bomb blast radiuses). Seimei: '
                           'Tempestuous Water and Thunder affinity.',
        'soil_alchemy_pt': 'Solo: Tábuas de teca alcatroadas, sal marinho encrostado e resíduos de pederneira naval. '
                           'Coleta de Hendrika: Alcatrão Náutico e Salitre Puro (Multiplica o raio de explosão das '
                           'bombas). Seimei: Propriedades tempestuosas de Água e Trovão.',
        'tactics_en': 'Linear corridor geometry favors cutlass dashes and point-blank pistol volleys. Forcing '
                      'adversaries over the low gunwales on the north or south flanks yields instant knockout '
                      'ring-outs.',
        'tactics_pt': 'O espaço linear e estreito do convés favorece investidas de alfanje e disparos de pistola à '
                      'queima-roupa. Empurrar o adversário por cima das amuradas nas laterais norte ou sul garante '
                      'eliminações instantâneas.'},
    {   'concept_art': 'assets/concepts/baroque_court_concept.jpg',
        'fighter_id': 'musketeer',
        'hazards_en': 'No ring-out pits and zero environmental traps. Grand hall featuring solid marble colonnades '
                      'that absorb heavy swings and smooth waxed parquet flooring.',
        'hazards_pt': 'Sem fossos de queda e sem perigos ambientais. Salao nobre com colunas macicas de marmore que '
                      'absorvem golpes e piso de parquet polido de alta aderencia.',
        'historical_context_en': 'A classical French palace erected in the foreign treaty port settlement of newly '
                                 'opened Yokohama. Crystal chandeliers hang from frescoed ceilings, gilded marble '
                                 'colonnades outline the grand ballroom, and silk tapestries depict Napoleonic '
                                 'victories. Julie serves as elite royal guard and official duel champion for the '
                                 'French military mission assisting the Shogunate.',
        'historical_context_pt': 'Um palacete com arquitetura clássica francesa erguido no assentamento estrangeiro do '
                                 'porto recém-aberto de Yokohama. Lustres de cristal pendem de tetos afrescados, '
                                 'colunas de mármore douradas delimitam o salão de baile e tapeçarias de seda retratam '
                                 'vitórias napoleônicas. Julie atua como guarda de honra e duelista oficial da missão '
                                 'militar francesa enviada para modernizar as forças do Xogunato.',
        'id': 'baroque_court',
        'location_en': 'European Diplomatic Enclave of Yokohama (Gala Night of 1865)',
        'location_pt': 'Enclave Diplomático Europeu de Yokohama (Noite de Baile de 1865)',
        'name_en': 'Baroque Court of the French Embassy',
        'name_pt': 'Corte Barroca da Embaixada Francesa',
        'soil_alchemy_en': 'Soil: Waxed oak parquet and polished Carrara marble floor tiles. Hendrika Gathering: '
                           'Refined Beeswax and Marble Dust (High-mobility agility draughts). Seimei: Noble Metal and '
                           'Light element resonance.',
        'soil_alchemy_pt': 'Solo: Parquet de carvalho nobre encerado e mármore de Carrara polido. Coleta de Hendrika: '
                           'Cera de Abelha Nobre e Pó de Mármore (Criação de óleos lubrificantes de alta mobilidade). '
                           'Seimei: Propriedades elegantes de Metal e Luz.',
        'tactics_en': 'Pristine smooth flooring tailored for fencing footwork and blistering rapier lunges. Weave '
                      'behind marble colonnades to absorb heavy club or broadsword swings before punishing during '
                      'weapon recovery.',
        'tactics_pt': 'Piso extremamente liso ideal para as estocadas velozes e passos de esgrima de Julie. Use as '
                      'colunas de mármore para quebrar o ímpeto de armas pesadas como machados e clavas, atacando em '
                      'ângulos agudos.'},
    {   'concept_art': 'assets/concepts/shaolin_temple_concept.jpg',
        'fighter_id': 'ren',
        'hazards_en': 'No ring-out pits and zero environmental traps. Sacred courtyard featuring stone Foo Dog '
                      'guardian statues and bronze bells providing static cover.',
        'hazards_pt': 'Sem fossos de queda e sem perigos ambientais. Patio sagrado de treino com estatuas de leao Foo '
                      'Dog e sinos de bronze que agem como cobertura estatica.',
        'historical_context_en': 'The legendary training terrace of Shaolin warrior monks in the mist-crowned Songshan '
                                 'mountains. Flagstones bear deep depressions from centuries of iron-stance drills '
                                 'beside roaring bronze guardian lions. Ren crossed from Chinese temples to Bakumatsu '
                                 'Japan to trace turbulent spiritual echoes forewarning that an ancient demon is '
                                 'stirring.',
        'historical_context_pt': 'O lendário pátio de treinamento dos monges guerreiros Shaolin nas montanhas '
                                 'Songshan. Marcado por pisos de lajes de pedra afundadas por séculos de posturas de '
                                 'ferro e estátuas de leões de bronze guardiões. Ren viajou dos mosteiros da China ao '
                                 'Japão do Bakumatsu para rastrear os ecos de energia espiritual corrompida que '
                                 'prenunciam o despertar de um demônio colossal que ameaça o equilíbrio do continente.',
        'id': 'shaolin',
        'location_en': 'Masters Courtyard, High Monastery in Henan Province (Mystic Cloud Sea)',
        'location_pt': 'Pátio dos Mestres, Mosteiro nas Alturas da Província de Henan (Névoa Mística)',
        'name_en': 'Mountain Shaolin Temple',
        'name_pt': 'Mosteiro Shaolin das Montanhas',
        'soil_alchemy_en': 'Soil: Ancient chiseled granite, red highland clay, and lotus incense residue. Hendrika '
                           'Gathering: Wild Mountain Ginseng and Myrrh Ash (Strength and Vitality draughts). Seimei: '
                           'Harmonious balance of all Five Elements.',
        'soil_alchemy_pt': 'Solo: Granito esculpido milenar, terra vermelha de montanha e incenso de lótus. Coleta de '
                           'Hendrika: Raiz de Ginseng Selvagem e Cinza de Mirra (Poções de Força e Regeneração). '
                           'Seimei: Harmonia absoluta dos Cinco Elementos.',
        'tactics_en': 'Reward ground for close-quarters kung-fu and center-ring control. Use lightning-quick flying '
                      'kicks and palm thrusts to pin foes against stone guardian statues before executing devastating '
                      'aerial knockouts.',
        'tactics_pt': 'Arena que premia artes marciais de contato corpo a corpo e controle de centro. Use a velocidade '
                      'das voadoras e socos Shaolin para prender o adversário contra as estátuas de leão e finalizar '
                      'com combos aéreos.'},
    {   'concept_art': 'assets/concepts/higanbana_garden_concept.jpg',
        'fighter_id': 'chiyo',
        'hazards_en': 'No ring-out pits and zero traps. Open meadow carpeted by red spider lilies and ancient granite '
                      'gravestones.',
        'hazards_pt': 'Sem fossos de queda e sem armadilhas. Descanso aberto coberto por manto infinito de lirios '
                      'vermelhos da aranha e lapides milenares de pedra.',
        'historical_context_en': 'Endless plains carpeted in crimson red spider lilies (Higanbana), the fabled blooms '
                                 'that flourish around cemeteries and guide departed souls across the River Sanzu into '
                                 "the afterlife. In Bakumatsu folklore, the blossoms' deep scarlet springs from the "
                                 'blood of fallen warriors. Chiyo glides among the blooms with paired Kodachi short '
                                 'swords, shepherding spirits and cleansing the slaughter of war.',
        'historical_context_pt': 'Campos infinitos cobertos por lírios vermelhos da aranha (Higanbana), as lendárias '
                                 'flores que florescem nos cemitérios e marcam a passagem das almas para o pós-vida '
                                 '(Sanzu-no-Kawa). No folclore do Bakumatsu, a cor carmesim viva das flores deriva do '
                                 'sangue de incontáveis soldados caídos em rebeliões esquecidas. Chiyo dança entre as '
                                 'flores com suas duas lâminas Kodachi, interceptando invasores antes que alcancem o '
                                 'selo da Caverna Sombria.',
        'id': 'higanbana',
        'location_en': 'Plains of Asuka, Yamato Province (Crimson Dusk)',
        'location_pt': 'Planícies de Asuka, Província de Yamato (Crepúsculo Carmesim)',
        'name_en': 'Crimson Higanbana Meadows',
        'name_pt': 'Campos Vermelhos de Higanbana',
        'soil_alchemy_en': 'Soil: Dark graveyard earth saturated with toxic floral alkaloids. Hendrika Gathering: '
                           'Higanbana Flower Bulbs and Paralytic Pollen (Prime ingredient for Stun and Neurotoxin '
                           'brews). Seimei: High Soul and Wood occult resonance.',
        'soil_alchemy_pt': 'Solo: Terra negra de cemitério saturada de alcaloides tóxicos florais. Coleta de Hendrika: '
                           'Bulbo de Higanbana e Pólen Paralisante (Componente para Poções de Atordoamento e Veneno). '
                           'Seimei: Propriedades arcanas de Alma e Madeira.',
        'tactics_en': 'The open field offers unrestricted freedom of movement. Control the center ring and use Chiyo\'s '
                      'superior speed to flank opponents diagonally, evading wide slashes and punishing recoveries with '
                      'rapid dual-blade cuts.',
        'tactics_pt': 'O descampado aberto oferece liberdade total de movimentação. Controle o centro da arena e aproveite '
                      'a alta velocidade para flanquear o oponente pelas diagonais, esquivando de golpes pesados e punindo '
                      'com cortes velozes de kodachi.'},
    {   'concept_art': 'assets/concepts/gojo_bridge_concept.jpg',
        'fighter_id': 'benkei',
        'hazards_en': '2 instant-drowning ring-out drops into the deep Kamo River on both bridge edges. High-tension '
                      'narrow ceremonial bridge corridor.',
        'hazards_pt': '2 fossos de queda letal nas aguas profundas do Rio Kamo nas duas bordas da ponte. Corredor '
                      'estreito cerimonial de altissima tensao tatica.',
        'historical_context_en': 'The famed ceremonial bridge of timber spans and stone pylons in the heart of Kyoto '
                                 'where the warrior monk Benkei defeated 999 samurai to claim their swords before '
                                 'meeting Minamoto no Yoshitsune. In the Bakumatsu turbulence, the bridge became the '
                                 "city's most tense choke point, where imperial patrols and rebels clashed under the "
                                 'icy moonlight reflected upon dark flowing waters.',
        'historical_context_pt': 'A célebre ponte cerimonial de madeira e pilares de pedra no coração de Kyoto, onde o '
                                 'monge guerreiro Benkei derrotou 999 samurais para tomar suas lâminas antes de seu '
                                 'mítico encontro com Minamoto no Yoshitsune. Durante a turbulência do Bakumatsu, a '
                                 'ponte era o posto de controle mais tenso da cidade, onde patrulhas imperiais e '
                                 'rebeldes cruzavam olhares sob a luz fria da lua cheia sobre as águas negras do rio.',
        'id': 'gojo_bridge',
        'location_en': 'Gojo Bridge over the Kamo River, Central Kyoto (Full Moon Midnight)',
        'location_pt': 'Ponte Gojo sobre o Rio Kamo, Kyoto Central (Madrugada de Lua Cheia)',
        'name_en': 'Gojo Bridge at Midnight',
        'name_pt': 'Ponte Gojo à Meia-Noite',
        'soil_alchemy_en': 'Soil: Massive oak timbers sealed with pitch and wrought-iron structural nails. Hendrika '
                           'Gathering: Iron Filings and Oak Resin (Stone-skin Armor strengthening draughts). Seimei: '
                           'Water and Metal alignment.',
        'soil_alchemy_pt': 'Solo: Vigas maciças de carvalho tratadas com betume e pregos de ferro fundido. Coleta de '
                           'Hendrika: Limalha de Ferro e Resina de Carvalho (Poções de Pele de Pedra / Armadura). '
                           'Seimei: Propriedades puras de Água e Metal.',
        'tactics_en': 'Highest ring-out hazard density in the game. Heavy club knockbacks and linear charges '
                      'effortlessly catapult adversaries into the river below. Strictly avoid rolling laterally near '
                      'the fractured railings.',
        'tactics_pt': 'A arena de maior risco de ring-out do jogo. Golpes de empurrão com a Kanabo de Benkei ou '
                      'estocadas longas jogam o oponente diretamente na água. Nunca role para as bordas laterais '
                      'durante um choque de lâminas.'},
    {   'concept_art': 'assets/concepts/yoshiwara_alley_concept.jpg',
        'fighter_id': 'orin',
        'hazards_en': 'No ring-out pits. Claustrophobic urban alley bordered by wooden balconies and hanging laundry '
                      'lines that obscure line of sight.',
        'hazards_pt': 'Sem fossos de queda. Beco urbano estreito e claustrofobico cercado por balcoes de madeira e '
                      'varais com tecidos suspensos que limitam a visao.',
        'historical_context_en': 'The fabled walled courtesan quarter of Edo, glowing under hundreds of crimson paper '
                                 'lanterns and blooming sakura branches. Behind the glamorous facade of musical '
                                 'banquets and shamisen melodies, shadowed alleys sheltered spies, smugglers, and '
                                 'hunted ronin. O-Rin knows every nook of this labyrinth, employing lethal grace and '
                                 "hidden steel to hunt targets threatening the district's fragile sanctuary.",
        'historical_context_pt': 'O lendário distrito murado das cortesãs em Edo, iluminado por centenas de lanternas '
                                 'vermelhas de papel e galhos de cerejeira em flor. Por trás do glamour das danças e '
                                 'do som dos shamisens, os becos escuros abrigavam espiões, contrabandistas e ronins '
                                 'em busca de refúgio. O-Rin conhece cada reentrância deste labirinto, usando sua '
                                 'beleza e lâminas ocultas para caçar alvos que ameaçam a paz do distrito.',
        'id': 'yoshiwara',
        'location_en': 'Yoshiwara Pleasure Quarter, Edo (Night Cherry Blossom Rain)',
        'location_pt': 'Distrito do Prazer de Yoshiwara, Edo (Chuva de Pétalas à Noite)',
        'name_en': 'Night Alley of Yoshiwara',
        'name_pt': 'Beco Noturno de Yoshiwara',
        'soil_alchemy_en': 'Soil: Moist Edo cobblestones, trampled sakura petals, and fragrant camellia grooming oil. '
                           'Hendrika Gathering: Camellia Oil and Sakura Extract (High-speed mobility and stealth '
                           'potions). Seimei: Water and Wood affinity.',
        'soil_alchemy_pt': 'Solo: Paralelepípedos úmidos de Edo, pétalas de cerejeira maceradas e óleo aromático de '
                           'camélia. Coleta de Hendrika: Óleo de Camélia e Essência de Cerejeira (Acelera mobilidade e '
                           'furtividade). Seimei: Propriedades de Água e Madeira.',
        'tactics_en': 'Claustrophobic quarters neutralizing long-range projectile zoning. Short-range dagger wielders '
                      'and close-contact brawlers can pin adversaries against the wooden walls for inescapable corner '
                      'traps.',
        'tactics_pt': 'Espaço claustrofóbico que anula táticas de fuga e zoneamento longo. Personagens com ataques '
                      'curtos de adaga e golpes de desarme conseguem encurralar oponentes nas paredes para combos '
                      'implacáveis.'},
    {   'concept_art': 'assets/concepts/rice_paddies_concept.jpg',
        'fighter_id': 'goro',
        'hazards_en': 'No ring-out pits. Raised dry earthen dykes bordered by submerged alluvial mud paddies that slow '
                      'dodge rolls and sprint speed.',
        'hazards_pt': 'Sem fossos de queda. Diques elevados de terra batida seca cercados por canais de arrozal '
                      'alagados que reduzem a velocidade de esquiva.',
        'historical_context_en': 'The ancestral agricultural wetlands that sustained rural populations and feeding '
                                 'feudal armies for centuries. Segmented by narrow earthen dykes and rushing '
                                 'irrigation sluice channels. When renegade samurai bands raided villages for rice '
                                 'stores during the Bakumatsu, farmers like Goro took up sickles, hoes, and threshing '
                                 'flails to defend their family harvest to the death.',
        'historical_context_pt': 'Os campos agrícolas ancestrais que sustentavam a alimentação da população camponesa '
                                 'e dos exércitos feudais. Divididos por diques estreitos de terra batida e canais de '
                                 'irrigação de água corrente límpida. Durante as requisições violentas de arroz e '
                                 'mantimentos feitas por bandos de samurais desertores no Bakumatsu, agricultores como '
                                 'Goro ergueram enxadas, foices Kama e ancinhos para defender a colheita de suas '
                                 'famílias até a morte.',
        'id': 'rice_paddies',
        'location_en': 'Rural Terraces of Omi Province (Rainy Summer Afternoon)',
        'location_pt': 'Campos Rurais da Província de Omi (Tarde Chuvosa de Verão)',
        'name_en': 'Rice Paddies and Irrigation Dykes',
        'name_pt': 'Arrozais e Diques de Água',
        'soil_alchemy_en': 'Soil: Saturated alluvial mud, decomposed rice straw, and mineral-rich fresh water. '
                           'Hendrika Gathering: Agricultural Niter and Organic Sludge (Paralytic mud and caustic acid '
                           'vials). Seimei: Pure Earth and Water resonance.',
        'soil_alchemy_pt': 'Solo: Lama fértil alagada, palha de arroz fermentada e água doce mineral. Coleta de '
                           'Hendrika: Nitrato Agrícola e Lodo Orgânico (Criação de Poções de Lama Paralisante e '
                           'Ácido). Seimei: Ressonância pura de Terra e Água.',
        'tactics_en': 'Fight from the raised dry dykes to maintain crisp dodge recovery. Knock opponents into the '
                      'submerged mud beds to rob their foot speed before executing heavy, unhurried sickle cleaves.',
        'tactics_pt': 'Lute sempre em cima dos diques elevados de terra batida para preservar a velocidade de esquiva. '
                      'Arremesse o oponente para dentro da lama funda do arrozal para cortar sua mobilidade e aplicar '
                      'golpes de corte pesado sem risco de contra-ataque.'},
    {   'concept_art': 'assets/concepts/rain_mill_concept.jpg',
        'fighter_id': 'ichi',
        'hazards_en': '2 fatal precipice drops down the rocky waterfall behind the mill. The massive wooden waterwheel '
                      'churns continuously on the western flank.',
        'hazards_pt': '2 fossos de queda na catarata rochosa atras do moinho. A monumental roda d agua mecanica de '
                      'madeira gira continuamente no flanco oeste.',
        'historical_context_en': 'An aged grain mill powered by a massive wooden waterwheel over a rushing cataract in '
                                 'the Hakone mountain pass. Under relentless autumn rain, the deafening roar of '
                                 'turning water paddles masks all footfalls. For Ichi, the blind swordsman, this '
                                 'stormy mill is home ground: relying not on sight but on rain vibrations and wind '
                                 'shifts to cut down any challenger crossing his path.',
        'historical_context_pt': "Um antigo moinho de grãos movido por uma roda d'água monumental sobre uma cachoeira "
                                 'impetuosa na passagem de Hakone. Sob a chuva implacável do outono, o barulho '
                                 'constante da água girando as pás abafa qualquer som de passos. Para Ichi, o '
                                 'espadachim cego, este ambiente barulhento e chuvoso é seu território perfeito: ele '
                                 'não depende da visão, mas sente as vibrações das gotas e do fluxo do vento para '
                                 'abater qualquer rival que cruze seu caminho.',
        'id': 'rain_mill',
        'location_en': 'Hakone Mountain Pass, Sagami Province (Torrential Continuous Downpour)',
        'location_pt': 'Passagem de Hakone, Província de Sagami (Chuva Torrencial Contínua)',
        'name_en': 'Mountain Rain Mill',
        'name_pt': 'Moinho Chuvoso nas Montanhas',
        'soil_alchemy_en': 'Soil: Moss-slick pine decking, polished riverstones, and dense water mist. Hendrika '
                           'Gathering: Aquatic Moss and Millstone Grit (Sensory focus and stamina recovery brews). '
                           'Seimei: Overwhelming Water and Wind supremacy.',
        'soil_alchemy_pt': "Solo: Tábuas de pinho encharcadas de musgo, rochas de rio polidas e névoa d'água. Coleta "
                           'de Hendrika: Musgo Aquático e Minério de Moagem (Poções de Foco Sensorial e Estamina). '
                           'Seimei: Propriedades soberanas de Água e Vento.',
        'tactics_en': 'Steer clear of the turning waterwheel unless setting up a throw into its crushing wooden '
                      'paddles. Rely on straight, lightning-fast linear draws that punish opponents blinded by '
                      'cascading rain.',
        'tactics_pt': "Evite a proximidade da roda d'água giratória a menos que pretenda empurrar o oponente contra as "
                      'pás de madeira. Utilize a sonoridade da chuva para mascarar preparações de golpe e use ataques '
                      'de saque frontal reto.'},
    {   'concept_art': 'assets/concepts/gothic_cemetery_concept.jpg',
        'fighter_id': 'valerius',
        'hazards_en': 'No ring-out pits. Active hazard: spectral ground mist inducing temporary sluggishness in dark '
                      'corners and jagged iron grave spires.',
        'hazards_pt': 'Sem fossos de queda. Perigo ativo: bruma espectral que causa lentidao temporaria nos cantos '
                      'escuros e cruzes de ferro forjado pontiagudas.',
        'historical_context_en': 'A centuries-old Gothic necropolis enclosed by wrought-iron fences and black granite '
                                 'mausoleums in Central Europe. Valerius, Prussian aristocrat and knight of the Black '
                                 'Order, traversed continents enthralled by legends of Oni Gashadokuro stirring in '
                                 'Japan. His dark quests into immortality and necromancy demand warrior souls, and '
                                 'this frozen sepulcher serves as the nexus from which he summons apparitions into his '
                                 'Zweihänder blade.',
        'historical_context_pt': 'Um cemitério gótico secular cercado por grades de ferro forjado e mausoléus de '
                                 'granito negro na Europa Central. Valerius, nobre prussiano e cavaleiro da Ordem '
                                 'Negra, cruzou os continentes fascinado pela lenda do despertar do Oni Gashadokuro no '
                                 'Japão. Suas pesquisas sobre a imortalidade e necromancia exigem a colheita de almas '
                                 'guerreiras, e este sepulcro frio é o portal de onde ele conjura espectros e canaliza '
                                 'energia de sepultura para sua lâmina Zweihänder.',
        'id': 'gothic_cemetery',
        'location_en': 'Ancestral Crypt in the Silesian Forests (Eclipse Midnight)',
        'location_pt': 'Cripta Ancestral nas Florestas da Silésia (Noite Eclipsada)',
        'name_en': 'Gothic Prussian Cemetery',
        'name_pt': 'Cemitério Prussiano Gótico',
        'soil_alchemy_en': 'Soil: Frozen graveyard soil, pulverized skeletal bone dust, and oxidized iron ash. '
                           'Hendrika Gathering: Corpse Dust and Black Ichors (Valyrian Hellfire and necrotic poisons). '
                           'Seimei: Extreme Darkness and Nether affinity.',
        'soil_alchemy_pt': 'Solo: Terra fria de sepultura, pó de ossos humanos e cinza de ferro oxidado. Coleta de '
                           'Hendrika: Pó Cadavérico e Óleo Negro (Criação do Fogo Valírio e Venenos Necróticos). '
                           'Seimei: Afinidade extrema com Escuridão e Morte.',
        'tactics_en': 'Exploit the immense arc of the Prussian Zweihänder to herd foes toward iron cemetery gates. Pin '
                      'enemies against stone crypts where heavy overhead cleaves shatter parry blocks and trigger '
                      'fatal guard breaks.',
        'tactics_pt': 'Use o tamanho titânico da Zweihänder de Valerius para manter os rivais longe das grades de '
                      'ferro. Encurrale o oponente contra os túmulos de pedra para garantir que o arco vertical de '
                      'corte esmague defesas de parry.'},
    {   'concept_art': 'assets/concepts/heian_shrine_concept.jpg',
        'fighter_id': 'seimei',
        'hazards_en': 'No ring-out pits. Active hazard: elemental glyphs upon the Pentagram Rondel flare with mystic '
                      'flares and shockwaves when charged by spells.',
        'hazards_pt': 'Sem fossos de queda. Perigo ativo: os glifos do Rondel Pentagrama (Gomanboshi) disparam '
                      'labaredas e explosoes de energia ao serem ativados por magias.',
        'historical_context_en': 'The ancestral sanctuary established upon the estate of Abe no Seimei, paramount '
                                 'Onmyodo master of the imperial court. The holy courtyard features a colossal '
                                 'Pentagram Rondel (Gomanboshi) carved in gold and white marble across the flagstones, '
                                 'aligned with the constellations of the Four Celestial Beasts. In the Bakumatsu, '
                                 'Seimei channels the five primordial elements through the magical circle to suppress '
                                 "Gashadokuro's malignant tremors.",
        'historical_context_pt': 'O santuário ancestral fundado no local da residência oficial de Abe no Seimei, o '
                                 'maior mestre de Onmyodo da corte imperial. O pátio sagrado ostenta um imenso Rondel '
                                 'Pentagrama (Gomanboshi) gravado em ouro e mármore branco no chão, alinhado com as '
                                 'constelações das Quatro Bestas Sagradas. Durante o Bakumatsu, Seimei canaliza os '
                                 'cinco elementos primordiais no círculo mágico para conter as correntes telúricas '
                                 'malignas do Oni Gashadokuro.',
        'id': 'heian_shrine',
        'location_en': 'Astral Altar of Seimei-jinja, Imperial Kyoto (Astral Eclipse Midnight)',
        'location_pt': 'Altar Astral de Seimei-jinja, Kyoto Imperial (Meia-Noite sob Eclipse Astral)',
        'name_en': 'Heian Shrine of Onmyodo',
        'name_pt': 'Santuário Heian de Onmyodo',
        'soil_alchemy_en': 'Soil: Ritual white marble, jade powder, and sanctified celestial sand. Hendrika Gathering: '
                           'Alchemical Quicksilver and Mystic Saltpeter (Maximum Potency brews). Seimei: 100% '
                           'elemental amplification for all Rondel spells.',
        'soil_alchemy_pt': 'Solo: Mármore branco ritual, pó de jade e areia estelar santificada. Coleta de Hendrika: '
                           'Mercúrio Alquímico e Salitre Místico (Elixires de Alta Potência). Seimei: Amplificação de '
                           '100% de todos os feitiços do Rondel.',
        'tactics_en': 'Dominate the courtyard geometry. Position inside the pentagram circle to accelerate spirit orb '
                      'recharge. Use tessen fan gusts to blast short-range melee fighters onto active elemental floor '
                      'glyphs.',
        'tactics_pt': 'Controle absoluto da geometria do pátio. Lute no interior do pentagrama para recarregar runas e '
                      'orbes espirituais. Use o leque de Seimei para repelir combatentes de espada curta contra os '
                      'glifos elementais ativos.'},
    {   'concept_art': 'assets/concepts/pine_forest_concept.jpg',
        'fighter_id': 'daiki',
        'hazards_en': 'No ring-out pits. Active hazard: deep snow drifts dampening sprint starts and heavy ice blocks '
                      'dropping from aged pine boughs.',
        'hazards_pt': 'Sem fossos de queda. Perigo ativo: densa camada de neve que afeta a arrancada inicial e blocos '
                      'de gelo que desabam dos pinheiros centenarios.',
        'historical_context_en': 'The sacred peak of Shingon Buddhism, blanketed under deep crystalline snow and '
                                 'five-hundred-year-old red pines. Frost-covered stone Toro lanterns mark the ancient '
                                 'pilgrim trail. Daiki lives here in ascetic solitude, wielding his heavy oak Bo-staff '
                                 'to maintain spiritual peace and shield mountain pilgrims from renegade pillagers '
                                 'exploiting the Bakumatsu civil war.',
        'historical_context_pt': 'A montanha sagrada do budismo Shingon, coberta por um manto espesso de neve '
                                 'cristalina e pinheiros vermelhos japoneses de mais de quinhentos anos. Lanternas de '
                                 'pedra votivas cobertas de gelo delimitam a trilha sagrada. Daiki vive aqui em retiro '
                                 'monástico, empunhando seu pesado cajado de carvalho (Bo) para ensinar a harmonia '
                                 'entre o corpo e o espírito e proteger os monges contra bandos de saqueadores que '
                                 'aproveitam o caos da guerra civil.',
        'id': 'pine_forest',
        'location_en': 'Pilgrims Path on Mount Koya (Glacial Winter Dawn)',
        'location_pt': 'Trilha dos Peregrinos no Monte Koya (Manhã Glacial de Inverno)',
        'name_en': 'Snowy Pine Forest',
        'name_pt': 'Floresta dos Pinheiros Nevados',
        'soil_alchemy_en': 'Soil: Frozen permafrost under virgin snow, red pine needles, and fossil amber resin. '
                           'Hendrika Gathering: Pine Resin and Pure Frost Crystals (Chilling ice vials and Stamina '
                           'brews). Seimei: Wood and Water/Ice affinity.',
        'soil_alchemy_pt': 'Solo: Terra congelada sob neve virgem, agulhas de pinheiro vermelho e resina âmbar. Coleta '
                           'de Hendrika: Seiva de Pinheiro e Cristais de Gelo Puro (Poções de Resfriamento e Vigor). '
                           'Seimei: Propriedades de Madeira e Água/Gelo.',
        'tactics_en': 'The sweeping 360-degree reach of the oak staff dominates snowy clearings. Keep swordsmen at '
                      'mid-range where the kinetic force of the wooden Bo shatters guard postures before they can step '
                      'into katana cutting range.',
        'tactics_pt': 'O alcance de 360 graus do cajado Bo de Daiki domina as clareiras de neve. Mantenha os '
                      'espadachins a meia distância onde o impacto da madeira esmaga a guarda do adversário antes que '
                      'ele consiga entrar no raio da katana.'},
    {   'concept_art': 'assets/concepts/ezo_taiga_concept.jpg',
        'fighter_id': 'aoi',
        'hazards_en': 'No ring-out pits. Active hazard: intermittent Arctic blizzard gusts altering arrow trajectories '
                      'and fragile thin ice patches across the permafrost.',
        'hazards_pt': 'Sem fossos de queda. Perigo ativo: rajadas intermitentes de nevasca artica que desviam flechas '
                      'e placas de gelo fino quebradico no solo.',
        'historical_context_en': "The untamed primeval frontier of Japan's far north, prior to being renamed Hokkaido "
                                 'during the Meiji Restoration. Dense birch forests lashed by Arctic blizzards, '
                                 'prowled by Ussuri brown bears and protected by Ainu clans living in harmony with '
                                 'nature spirits (Kamuy). Aoi patrols these glacial taiga forests with her horn '
                                 'composite bow and ceremonial Makiri blade, purging renegade soldiers who bring the '
                                 'rot of civil war into sacred wilderness.',
        'historical_context_pt': 'A imensidão selvagem do extremo norte do Japão, antes de ser rebatizada como '
                                 'Hokkaido durante a Restauração Meiji. Bosques de bétulas brancas cobertos por '
                                 'nevascas ferozes, habitados por ursos-pardos de Ussuri e tribos Ainu que mantêm suas '
                                 'tradições em comunhão com os espíritos da natureza (Kamuy). Aoi caça nestas '
                                 'florestas glaciais com seu arco de chifre e faca cerimonial Makiri, caçando '
                                 'desertores militares que trazem a podridão da guerra para as terras sagradas.',
        'id': 'ezo_taiga',
        'location_en': 'Primeval Wilderness of Hokkaido (Ancestral Ainu Lands, Deep Winter)',
        'location_pt': 'Florestas Primitivas de Hokkaido (Terras Ancestrais Ainu, Inverno Rigoroso)',
        'name_en': 'Wild Taiga of Ezo',
        'name_pt': 'Taiga Selvagem de Ezo',
        'soil_alchemy_en': 'Soil: Glacial permafrost, reindeer lichen, and crushed antler silt. Hendrika Gathering: '
                           'Arctic Lichen and Permanent Ice (Speed Draughts and Cryogenic Flasks). Seimei: Peak '
                           'resonance with Water, Ice, and Wind.',
        'soil_alchemy_pt': 'Soil: Permafrost glacial, líquen de rena e chifre de cervo triturado. Coleta de Hendrika: '
                           'Líquen Ártico e Gelo Puro (Elixires de Velocidade e Resfriamento). Seimei: Máxima '
                           'ressonância com Água, Gelo e Vento.',
        'tactics_en': 'Use blizzard gusts to mask long-distance bow shots. Lure aggressively charging rushers onto '
                      'thin ice fractures to cause chilling stumbles that guarantee lethal arrow follow-ups.',
        'tactics_pt': 'Aproveite as rajadas de neve para mascarar disparos de flecha à distância. Atraia o adversário '
                      "para as manchas de gelo fino e use disparos rasteiros para forçar quedas d'água "
                      'incapacitantes.'},
    {   'concept_art': 'assets/concepts/sacred_dohyo_concept.jpg',
        'fighter_id': 'raiden',
        'hazards_en': 'No pits. Sacred hazard: the raised straw bale ring (Tawara). Stepping or being pushed outside '
                      'the circular boundary triggers an immediate Ring-Out defeat!',
        'hazards_pt': 'Sem fossos de queda. Perigo sagrado: o anel elevado de fardos de palha (Tawara). Ultrapassar ou '
                      'ser empurrado para fora do circulo constitui derrota imediata por Ring-Out!',
        'historical_context_en': 'The sacred clay ring (Dohyo) consecrated beneath a floating Shinto shrine-style roof '
                                 'canopy. Before becoming a sport, Sumo was a sacred Shinto ceremony performed to '
                                 'appease the gods (Kami) and ensure bountiful harvests. In the Bakumatsu twilight, '
                                 'Grand Champion Raiden stamps the consecrated ring to demonstrate that pure physical '
                                 'mass and divine devotion surpass any firearm or steel blade forged by man.',
        'historical_context_pt': 'O círculo cerimonial de argila batida (Dohyo) construído sob o teto suspenso de '
                                 'estilo Shinto que emula os santuários sagrados. Antes de ser um esporte, o Sumô era '
                                 'um ritual sagrado para apaziguar os deuses (Kami) e garantir colheitas férteis. No '
                                 'crepúsculo do Bakumatsu, o Grande Campeão Raiden pisa no barro consagrado para '
                                 'provar que a força física pura e a devoção espiritual sobrepujam qualquer arma de '
                                 'fogo ou katana forjada pelo homem.',
        'id': 'sacred_dohyo',
        'location_en': 'Grand Shrine of Sumiyoshi Taisha, Osaka (Ceremonial Dawn)',
        'location_pt': 'Grande Santuário de Sumiyoshi Taisha, Osaka (Alvorecer Cerimonial)',
        'name_en': 'Sacred Dohyo of the Shinto Shrine',
        'name_pt': 'Dohyo Sagrado do Santuário Xintoísta',
        'soil_alchemy_en': 'Soil: Consecrated Arakida clay compacted and cleansed with sacred ritual salt. Hendrika '
                           'Gathering: Sanctified Purifying Salt and Shrine Earth (Resistance and Poison Neutralizing '
                           'draughts). Seimei: Sacred Earth and Purity elemental alignment.',
        'soil_alchemy_pt': 'Solo: Argila cerimonial de Arakida compactada e purificada com sal consagrado. Coleta de '
                           'Hendrika: Sal Sagrado de Purificação e Terra de Altar (Poções de Resistência e '
                           'Neutralização de Veneno). Seimei: Propriedades sagradas de Terra e Pureza.',
        'tactics_en': "The quintessential Ring-Out arena. Maintain absolute center-ring supremacy. Deploy Raiden's "
                      'heavy open-palm slaps (Harite) and unstoppable body thrusts to drive challengers over the '
                      'Tawara straw perimeter for instant victories.',
        'tactics_pt': 'A arena de Ring-Out por excelência. Controle o centro absoluto do círculo. Utilize as palmadas '
                      'pesadas (Harite) e empurrões corporais de Raiden para forçar o rival contra os fardos de palha '
                      'Tawara, encerrando a luta com expulsão imediata.'},
    {   'concept_art': 'assets/concepts/dejima_warehouse_concept.jpg',
        'fighter_id': 'hendrika',
        'hazards_en': '5 ring-out drops (southern dock edge directly over harbor waters). Active hazard: breakable '
                      'alchemical glass carboys that leave caustic acid pools.',
        'hazards_pt': '5 fossos de queda (doca sul sem parapeito sobre as aguas do porto). Perigo ativo: garrafoes de '
                      'vidro quimicos destrutiveis que espalham pocas de acido caustico.',
        'historical_context_en': 'The fan-shaped artificial island in Nagasaki harbor that served for over two '
                                 "centuries as Japan's sole window of trade and scientific exchange (Rangaku) with the "
                                 'Western world via the Dutch East India Company (VOC). Among timber warehouses packed '
                                 'with spices, anatomical treatises, glass retorts, and imported chemical carboys, '
                                 'Hendrika established her clandestine laboratory to gather rare overseas reagents and '
                                 "brew forbidden compounds under the harbor's ceaseless downpours.",
        'historical_context_pt': 'A ilha artificial em forma de leque na baía de Nagasaki que funcionou por mais de '
                                 'dois séculos como o único ponto de contato comercial e científico entre o Japão '
                                 'fechado (Sakoku) e o mundo ocidental através da Companhia Holandesa das Índias '
                                 'Orientais (VOC). Entre armazéns de madeira repletos de especiarias, livros de '
                                 'medicina ocidental (Rangaku), alambiques de vidro e barris de produtos químicos '
                                 'importados, Hendrika montou seu laboratório clandestino para colher reagentes raros '
                                 'trazidos pelos navios e destilar compostos proibidos sob a chuva constante do porto.',
        'id': 'dejima_dock',
        'location_en': 'Dutch Trading Post of Dejima, Port of Nagasaki (Stormy Night of 1866)',
        'location_pt': 'Feitoria Comercial Holandesa de Dejima, Porto de Nagasaki (Noite Tempestuosa de 1866)',
        'name_en': 'Dejima Warehouse with Rainy Dock',
        'name_pt': 'Armazém de Dejima com Doca Chuvosa',
        'soil_alchemy_en': 'Soil: Salt-soaked pine dock planks stained with red lead, sulfuric acid residues, and '
                           'imported elemental sulfur powder. Hendrika Gathering: Pure Sulfur, Fine Saltpeter, and '
                           'Caustic Residues (The Alchemical Paradise: gathering speed boosted by 30%!). Seimei: '
                           'Corrosive Water, Metal, and Fire elemental blend.',
        'soil_alchemy_pt': 'Solo: Tábuas de pinho tratadas com zarcão, encharcadas de água salgada, resíduos de ácido '
                           'sulfúrico e pó de enxofre importado. Coleta de Hendrika: Enxofre Puro, Salitre Fino e '
                           'Resíduos Ácidos (O paraíso alquímico: tempo de coleta reduzido em 30%!). Seimei: '
                           'Propriedades corrosivas de Água, Metal e Fogo.',
        'tactics_en': 'Tactical haven for alchemists and fencing specialists. Deliberately shatter reagent carboys to '
                      'lay down acid zones that disintegrate enemy poise. Utilize swift rapier lunges to herd '
                      'overeager brawlers off the wet dock into the harbor.',
        'tactics_pt': 'O paraíso dos combatentes alquímicos e táticos. Quebre os frascos de reagente intencionalmente '
                      'para criar barreiras de ácido que desintegram a postura do oponente. Use o florete rápido de '
                      'Hendrika para empurrar os atacantes em direção à borda da doca chuvosa.'}]
