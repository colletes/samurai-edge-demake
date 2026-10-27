"""
Banco de dados estratégico das 24 Arenas de Samurai Edge (Bilíngue PT/EN).
Pareadas perfeitamente com os 24 lutadores.
Cada ficha de arena detalha:
- Nome, localização geográfica e contexto histórico real no Japão do Bakumatsu (1860s).
- Perigos ambientais (fossos de morte, água rasa, fogueiras, carruagens, piso quebrável).
- Composição do solo e reagentes alquímicos (essencial para a coleta de Hendrika e rituais de Seimei).
- Táticas de controle espacial, zoneamento e manobras de ring-out.
"""

ARENAS_DATA = [
    # 1. KENSHI — BOSQUE DE BAMBU SAGRADO
    {
        "id": "bamboo",
        "fighter_id": "kenshin",
        "name_pt": "Bosque de Bambu Sagrado (Arashiyama)",
        "name_en": "Sacred Bamboo Grove (Arashiyama)",
        "location_pt": "Arashiyama, Periferia Oeste de Kyoto (Outono de 1863)",
        "location_en": "Arashiyama, Western Outskirts of Kyoto (Autumn 1863)",
        "concept_art": "assets/concepts/bamboo_forest_concept.jpg",
        "historical_context_pt": (
            "As densas florestas de bambu de Sagano e Arashiyama serviam como refúgio clandestino e rotas de fuga "
            "para lealistas imperiais perseguidos pelas forças do Xogunato. O farfalhar constante dos colmos altos "
            "ao vento abafava os passos de assassinos políticos e ronins errantes. Na mitologia do jogo, é a fronteira "
            "espiritual onde Kenshi medita e defende os peregrinos rurais contra as patrulhas violentas."
        ),
        "historical_context_en": (
            "The dense bamboo groves of Sagano and Arashiyama served as clandestine hideouts and escape corridors "
            "for imperial loyalists hunted by Shogunate forces. The constant rustling of tall bamboo culms muffled "
            "the footsteps of political assassins and wandering ronin. In the game's lore, it marks the spiritual frontier "
            "where Kenshi meditates and shields rural pilgrims from brutal martial patrols."
        ),
        "hazards_pt": (
            "Colmos de bambu cortáveis que obstruem projéteis e linhas de visão iniciais. Desfiladeiros estreitos "
            "nas bordas oeste e sul onde recuos forçados causam quedas fatais em penhascos rochosos."
        ),
        "hazards_en": (
            "Cuttable bamboo stalks blocking initial projectiles and lines of sight. Narrow ravine drop-offs along the "
            "western and southern edges where heavy knockbacks induce fatal ring-outs onto jagged rocks."
        ),
        "soil_alchemy_pt": (
            "Solo: Húmus vegetal úmido e terra negra rica em matéria orgânica. Coleta de Hendrika: Raízes Medicinais e "
            "Carvão Vegetal (Chave para Poções de Cura e Estamina). Seimei: Propriedades puras do elemento Madeira (Wood)."
        ),
        "soil_alchemy_en": (
            "Soil: Moist vegetal humus and rich black loam. Hendrika Gathering: Medicinal Roots and Plant Charcoal "
            "(Essential for Healing and Stamina draughts). Seimei: Pure Wood elemental resonance."
        ),
        "tactics_pt": (
            "Corte o bambu com golpes cortantes para abrir linhas de investida direta. Use a vegetação densa para "
            "desviar flechas e disparos de pólvora. Force o oponente em direção às margens do desfiladeiro para vitórias rápidas por ring-out."
        ),
        "tactics_en": (
            "Slice bamboo stalks with horizontal slashes to clear direct charge corridors. Exploit dense vegetation to "
            "deflect incoming arrows and rifle rounds. Pressure opponents toward cliff ledges for swift ring-out finishes."
        )
    },

    # 2. MUSASHI — DUELO NA ILHA GANRYU
    {
        "id": "ganryu",
        "fighter_id": "musashi",
        "name_pt": "Duelo na Ilha Ganryu (Funajima)",
        "name_en": "Duel on Ganryu Island (Funajima)",
        "location_pt": "Estreito de Kanmon, Mar Interior de Seto (Madrugada de Névoa)",
        "location_en": "Kanmon Strait, Seto Inland Sea (Misty Dawn)",
        "concept_art": "assets/concepts/ganryu_island_concept.jpg",
        "historical_context_pt": (
            "A lendária ilha deserta no estreito marítimo onde Miyamoto Musashi e Sasaki Kojiro travaram o maior "
            "duelo da história japonesa em 1612. Durante o Bakumatsu, o estreito tornou-se palco de bombardeios navais "
            "ocidentais contra o domínio Choshu. A praia de areia branca e rochedos pontiagudos é varrida por maresia salgada "
            "e marés traiçoeiras, preservando a aura mística do teste marcial supremo."
        ),
        "historical_context_en": (
            "The legendary sandbar island in the maritime strait where Miyamoto Musashi and Sasaki Kojiro fought history's "
            "most famous duel in 1612. During the Bakumatsu, the strait became ground zero for Western naval bombardments against "
            "the Choshu domain. Its white sand beaches and jagged reefs are swept by salty spray and treacherous tides, "
            "preserving the sacred aura of the ultimate martial proving ground."
        ),
        "hazards_pt": (
            "Arrebentação marítima profunda que afoga combatentes arremessados na água além da linha de areia. "
            "Cascos de barcos de pesca encalhados que servem de obstáculos para ricochete de adagas e projéteis."
        ),
        "hazards_en": (
            "Deep maritime surf instantly drowning combatants knocked past the shoreline boundary. Beached wooden fishing "
            "skiffs acting as tactical rebound barriers for throwing knives and projectiles."
        ),
        "soil_alchemy_pt": (
            "Solo: Areia marinha salina, conchas trituradas e depósitos de calcário. Coleta de Hendrika: Salitre Purificado "
            "e Cinzas de Salmoura (Componente explosivo crítico). Seimei: Ressonância elemental pura de Água (Water)."
        ),
        "soil_alchemy_en": (
            "Soil: Saline sea sand, crushed shells, and limestone silt. Hendrika Gathering: Refined Saltpeter and Brine Ash "
            "(Critical explosive reagent). Seimei: High Water elemental resonance."
        ),
        "tactics_pt": (
            "Arena ampla e desobstruída favorável a duelos técnicos de espaçamento puro. Controle o centro da faixa de areia; "
            "quem for encurralado na linha de maré perde mobilidade de esquiva e fica vulnerável a arremessos letais nas ondas."
        ),
        "tactics_en": (
            "Vast, open shoreline favoring technical spacing and mid-range dueling. Dominate the central sand strip; "
            "fighters backed into the tidal surf suffer dodge deceleration and risk instant drowning knockouts."
        )
    },

    # 3. HANZO — TELHADOS NOTURNOS DE IGA
    {
        "id": "iga",
        "fighter_id": "ninja",
        "name_pt": "Telhados Noturnos de Iga",
        "name_en": "Night Rooftops of Iga",
        "location_pt": "Castelo das Sombras, Província Montanhosa de Iga (Meia-Noite Chuvosa)",
        "location_en": "Shadow Castle, Mountainous Iga Province (Rainy Midnight)",
        "concept_art": "assets/concepts/iga_rooftops_concept.jpg",
        "historical_context_pt": (
            "A fortaleza ancestral dos clãs Shinobi nas montanhas isoladas da província de Iga. Fortificada com "
            "telhados íngremes de telhas cerâmicas e beirais pontiagudos projetados para dificultar invasões de infantaria. "
            "Sob a chuva torrencial do Bakumatsu, Hanzo e seus discípulos mantêm vigília eterna sobre as passagens secretas "
            "que descem até a Caverna Sombria do Gashadokuro."
        ),
        "historical_context_en": (
            "The ancestral mountain stronghold of the Shinobi clans in the rugged heights of Iga Province. Engineered "
            "with steep ceramic-tiled roofs and sweeping eves designed to break conventional infantry assaults. Under "
            "torrential Bakumatsu rain, Hanzo and his disciples maintain eternal watch over the subterranean passages "
            "descending into Gashadokuro's Shadow Cave."
        ),
        "hazards_pt": (
            "Abismo vertical total ao redor de todas as beiradas do telhado (queda mortal imediata). Chaminés de terracota "
            "e cumeeiras ornamentais que bloqueiam disparos lineares e criam pontos de emboscada aérea."
        ),
        "hazards_en": (
            "Total vertical abyss surrounding all roof perimeters (instant fall death). Terracotta chimneys and ridge tiles "
            "blocking horizontal ballistic trajectories and enabling aerial ambush angles."
        ),
        "soil_alchemy_pt": (
            "Solo: Telhas cerâmicas vitrificadas, fuligem antiga e argila cozida. Coleta de Hendrika: Enxofre Seco e "
            "Fuligem Concentrada (Essencial para Bombas Ácidas e Granadas de Fumaça). Seimei: Afinidade com Fogo e Metal."
        ),
        "soil_alchemy_en": (
            "Soil: Glazed ceramic tiles, aged chimney soot, and kiln clay. Hendrika Gathering: Dry Sulfur and Concentrated "
            "Soot (Crucial for Acid Bombs and Smoke Screens). Seimei: Strong Fire and Metal elemental affinity."
        ),
        "tactics_pt": (
            "O controle de borda é a chave absoluta nesta arena. Personagens com ataques de empurrão (como Hanzo e Musashi) "
            "conseguem finalizar o round em menos de três segundos. Evite rolar descontroladamente para as diagonais externas."
        ),
        "tactics_en": (
            "Ring-out edge control is paramount. Fighters boasting high-recoil strikes (such as Hanzo and Musashi) can "
            "terminate rounds in under three seconds. Strictly avoid panic rolling toward outer corner diagonals."
        )
    },

    # 4. JOE — ACAMPAMENTO SECRETO NA FLORESTA
    {
        "id": "forest_camp",
        "fighter_id": "american",
        "name_pt": "Acampamento Secreto na Floresta",
        "name_en": "Secret Forest Outpost",
        "location_pt": "Bosque Oculto nos Vales de Iga (Tarde Encoberta)",
        "location_en": "Hidden Grove in the Iga Valleys (Overcast Dusk)",
        "concept_art": "assets/concepts/forest_camp_concept.jpg",
        "historical_context_pt": (
            "Uma base de operações camuflada entre carvalhos centenários onde Joe montou seu refúgio após ser "
            "arremessado no tempo. Caixas de suprimentos militares modernos misturam-se a pergaminhos ninjas e fogueiras "
            "de campanha. É o local onde Joe treina seu doberman 'Shadow' e afia suas lâminas táticas enquanto estuda "
            "os mapas do selo milenar de Iga."
        ),
        "historical_context_en": (
            "A camouflaged forward operating camp sheltered beneath ancient oaks where Joe established his sanctuary "
            "after being displaced across time. Modern military supply crates sit beside Shinobi scrolls and field campfires. "
            "Here, Joe drills his tactical doberman 'Shadow' and hones modern combat blades while deciphering ancient Iga seal charts."
        ),
        "hazards_pt": (
            "Fogueira acesa no centro que queima e causa dano contínuo ao toque. Caixas de madeira e barris destrutíveis "
            "que podem ocultar armadilhas e alterar as linhas de corrida."
        ),
        "hazards_en": (
            "Central roaring campfire dealing tick fire damage upon contact. Destructible wooden crates and military barrels "
            "that block movement lines and absorb stray projectile hits."
        ),
        "soil_alchemy_pt": (
            "Solo: Terra batida misturada com cinzas de fogueira, folhas secas e pólvora descartada. Coleta de Hendrika: "
            "Carvão Vegetal e Pólvora Negra Concentrada. Seimei: Propriedades de Madeira e Fogo."
        ),
        "soil_alchemy_en": (
            "Soil: Compacted dirt infused with campfire embers, fallen foliage, and stray gunpowder. Hendrika Gathering: "
            "Plant Charcoal and Coarse Black Powder. Seimei: Wood and Fire elemental synthesis."
        ),
        "tactics_pt": (
            "Use as caixas de suprimentos como cobertura tática contra atiradores e projéteis. Force o adversário contra as chamas "
            "da fogueira central para interromper posturas defensivas e aplicar punições limpas."
        ),
        "tactics_en": (
            "Use supply crates as ballistic cover against snipers and throwing stars. Herd opponents into the central fire pit "
            "to disrupt defensive stances and guarantee clean follow-up strikes."
        )
    },

    # 5. SAITOU — KYOTO: BAKUMATSU EM CHAMAS
    {
        "id": "kyoto",
        "fighter_id": "saitou",
        "name_pt": "Kyoto: Bakumatsu em Chamas",
        "name_en": "Kyoto: Bakumatsu in Flames",
        "location_pt": "Distrito de Sanjo, Kyoto (Incidente Ikedaya, Noite de 1864)",
        "location_en": "Sanjo District, Kyoto (Ikedaya Incident, Night of 1864)",
        "concept_art": "assets/concepts/kyoto_bakumatsu_concept.jpg",
        "historical_context_pt": (
            "A antiga capital imperial consumida pelas chamas durante a rebelião Hamaguri e o ataque do Shinsengumi "
            "à hospedaria Ikedaya. Carruagens nobres ardem no meio das ruas empedradas enquanto os 'Lobos de Mibu' patrulham "
            "sem piedade. O sangue que mancha os paralelepípedos desta noite alimenta diretamente o despertar do Gashadokuro "
            "nas profundezas da terra."
        ),
        "historical_context_en": (
            "The ancient imperial capital engulfed in infernos during the Hamaguri Gate rebellion and the Shinsengumi's "
            "raid on the Ikedaya Inn. Aristocratic palanquins blaze amid cobblestone thoroughfares as the 'Wolves of Mibu' "
            "hunt without quarter. The blood pooling upon Kyoto's stone streets directly feeds Gashadokuro's subterranean awakening."
        ),
        "hazards_pt": (
            "Carruagem nobre em chamas no centro que queima combatentes em choque. Paredes de lojas em colapso com vigas incandescentes "
            "que desabam quando atingidas por golpes pesados."
        ),
        "hazards_en": (
            "Blazing aristocratic ox-cart in the center dealing burn damage and knocking back careless fighters. Collapsing timber "
            "shopfront facades that drop flaming beams when struck by heavy attacks."
        ),
        "soil_alchemy_pt": (
            "Solo: Paralelepípedos de granito encharcados de sangue e fuligem urbana. Coleta de Hendrika: Enxofre de Pólvora e "
            "Sangue de Combatente (Matéria-prima de Poções Venenosas e Ácido). Seimei: Propriedades intensas de Fogo e Terra."
        ),
        "soil_alchemy_en": (
            "Soil: Granite paving stones drenched in blood and burning embers. Hendrika Gathering: Gunpowder Sulfur and "
            "Fresh Blood Residue (Prime reagents for Poison and Acid vials). Seimei: Overwhelming Fire and Earth alignment."
        ),
        "tactics_pt": (
            "Espaço urbano denso com linhas de choque retilíneas perfeitas para a estocada Gatotsu de Saitou. "
            "Empurre os inimigos contra as rodas em chamas da carruagem para garantir quebras de postura instantâneas."
        ),
        "tactics_en": (
            "Dense urban corridor with straight sightlines ideal for Saitou's Gatotsu thrusts. Shove adversaries into the "
            "burning carriage wheels to trigger instant guard breaks and lethal openings."
        )
    },

    # 6. TEPPO — TRINCHEIRAS DE NAGASHINO
    {
        "id": "nagashino",
        "fighter_id": "rifleman",
        "name_pt": "Trincheiras de Nagashino",
        "name_en": "Trenches of Nagashino",
        "location_pt": "Planície de Shitaragahara, Província de Mikawa (Alvorecer Nebuloso)",
        "location_en": "Shitaragahara Plains, Mikawa Province (Misty Dawn)",
        "concept_art": "assets/concepts/nagashino_field_concept.jpg",
        "historical_context_pt": (
            "O campo de batalha histórico onde as voleios de arcabuzes Tanegashima dizimaram a outrora invencível cavalaria Takeda em 1575, "
            "reaberto no Bakumatsu como terreno de testes para a moderna infantaria de fuzil rifado. Paliçadas de madeira "
            "farpada e trincheiras de lama marcam o triunfo da pólvora sobre a tradição da espada feudal."
        ),
        "historical_context_en": (
            "The historic battlefield where synchronized Tanegashima matchlock volleys shattered the invincible Takeda cavalry in 1575, "
            "re-established during the Bakumatsu as a proving ground for rifled infantry warfare. Barbed wooden palisades "
            "and muddy trenches memorialize gunpowder's bloody victory over feudal sword tradition."
        ),
        "hazards_pt": (
            "Paliçadas defensivas pontiagudas de estacas de madeira que empalam combatentes arremessados contra elas. "
            "Trincheiras de lama densa que reduzem a velocidade de caminhada e rolamento em 20%."
        ),
        "hazards_en": (
            "Pointed wooden defensive palisades that impale fighters hurled against them. Deep mud trenches slowing "
            "running and rolling movement speed by 20%."
        ),
        "soil_alchemy_pt": (
            "Solo: Argila pesada saturada de chuva, ferro oxidado e resíduos de pólvora antiga. Coleta de Hendrika: Salitre "
            "e Minério de Ferro (Aumenta dano de estilhaços). Seimei: Propriedades equilibradas de Terra e Metal."
        ),
        "soil_alchemy_en": (
            "Soil: Heavy rain-saturated clay, oxidized iron filings, and aged gunpowder silt. Hendrika Gathering: Crude Saltpeter "
            "and Iron Ore (Enhances explosive shrapnel damage). Seimei: Earth and Metal elemental balance."
        ),
        "tactics_pt": (
            "Mantenha a infantaria e os duelistas afastados controlando as linhas entre as paliçadas. Utilize o terreno lamacento "
            "para prender oponentes rápidos em disparos de fuzil de longa distância e arremessos de baioneta."
        ),
        "tactics_en": (
            "Control firing lanes between palisade rows to pin agile duelists. Funnel sprinting foes into deep mud to rob "
            "their dash momentum, leaving them open to long-range rifle volleys and bayonet lunges."
        )
    },

    # 7. MURASAKI — CAVERNA SOMBRIA DO SELO
    {
        "id": "shadow_cave",
        "fighter_id": "purple",
        "name_pt": "Caverna Sombria do Selo",
        "name_en": "Shadow Cave of the Seal",
        "location_pt": "Profundezas Subterrâneas do Monte Suzuka, Fronteira de Iga (Eterna Escuridão)",
        "location_en": "Subterranean Deeps of Mount Suzuka, Iga Border (Eternal Stygian Dark)",
        "concept_art": "assets/concepts/shadow_cave_concept.jpg",
        "historical_context_pt": (
            "Um complexo de cavernas vulcânicas subterrâneas onde os fundadores do clã Iga ergueram estátuas guardiãs "
            "e cordas sagradas Shimenawa para selar os ossos colossais do Oni Gashadokuro. A névoa miasmática que emana "
            "das fendas na rocha corrompe os sentidos. Murasaki vigia a câmara central, empunhando sua kusarigama venenosa "
            "para garantir que nenhum intruso derrame sangue suficiente para despertar a abominação."
        ),
        "historical_context_en": (
            "A cavernous volcanic underworld where the founders of the Iga clan raised guardian monoliths and sacred "
            "Shimenawa ropes to seal the colossal skeletal remains of Oni Gashadokuro. Miasmic vapors rising from subterranean "
            "fissures distort perception. Murasaki guards the central shrine, wielding her venomous kusarigama to ensure "
            "no outsider spills the innocent blood needed to revive the titan."
        ),
        "hazards_pt": (
            "Gás venenoso púrpura que vaza de fendas no solo e estalactites pontiagudas que caem do teto quando ocorrem impactos no chão. "
            "Fossos de breu insondável nos cantos nordeste e sudeste."
        ),
        "hazards_en": (
            "Toxic purple vents seeping from floor fissures and razor stalactites that drop from the ceiling following heavy ground slams. "
            "Bottomless stygian chasms situated at the northeast and southeast edges."
        ),
        "soil_alchemy_pt": (
            "Solo: Basalto vulcânico, fungos cavernosos fluorescentes e cinzas amaldiçoadas. Coleta de Hendrika: Miasma "
            "Concentrado e Fungo Venenoso (Poção Venenosa Fatal). Seimei: Propriedades corrompidas de Escuridão e Terra."
        ),
        "soil_alchemy_en": (
            "Soil: Volcanic basalt, bioluminescent cave fungi, and cursed skeletal ash. Hendrika Gathering: Concentrated "
            "Miasma and Toxic Spores (Lethal Poison Vial brew). Seimei: Corrupted Earth and Shadow resonance."
        ),
        "tactics_pt": (
            "Aproveite as sombras e o alcance curvado da Kusarigama para golpear além dos pilares de pedra. Posicione-se "
            "próximo às fendas de gás para que o oponente sofra envenenamento passivo durante o duelo."
        ),
        "tactics_en": (
            "Exploit cave pillars to wrap curved kusarigama strikes around solid cover. Anchor fights near toxic gas vents "
            "to subject opponents to continuous health attrition while maintaining mid-range zoning."
        )
    },

    # 8. KASUMI — TEMPLO DA NÉVOA OCULTA
    {
        "id": "mist_temple",
        "fighter_id": "gray",
        "name_pt": "Templo da Névoa Oculta",
        "name_en": "Hidden Mist Temple",
        "location_pt": "Mosteiro de Tendai nas Alturas de Hiei (Neblina Matinal)",
        "location_en": "Tendai Monastery in the Heights of Mount Hiei (Morning Mist)",
        "concept_art": "assets/concepts/mist_temple_concept.jpg",
        "historical_context_pt": (
            "Um templo budista antigo erguido nos picos enevoados do Monte Hiei, com pisos de ripas de cedro polidas "
            "e portas shoji translúcidas. Durante a convulsão do Bakumatsu, o mosteiro serviu de refúgio espiritual e "
            "escola de treinamento para kunoichis do clã Iga. A densa névoa da montanha oculta degraus milenares e "
            "abismos vertiginosos cobertos de musgo."
        ),
        "historical_context_en": (
            "An ancient Buddhist sanctuary perched upon the mist-shrouded crags of Mount Hiei, featuring polished cedar "
            "decking and translucent shoji screens. Amid the convulsions of the Bakumatsu, the mountain temple served as a spiritual "
            "refuge and elite training monastery for Iga kunoichi. Dense highland mist veils moss-covered stone steps and sheer precipices."
        ),
        "hazards_pt": (
            "Névoa dinâmica que reduz a visibilidade a longa distância. Paredes de biombo shoji destrutíveis que revelam "
            "bordas de penhasco sem parapeito."
        ),
        "hazards_en": (
            "Dynamic fog rolls obscuring long-distance vision. Destructible paper shoji screens that, once slashed away, "
            "expose unguarded precipice drops."
        ),
        "soil_alchemy_pt": (
            "Solo: Madeira de cedro envelhecida, musgo de altitude e incenso cerimonial. Coleta de Hendrika: Resina de Cedro e "
            "Cinzas de Mirra (Acelera recuperação de vigor). Seimei: Propriedades puras de Vento e Água."
        ),
        "soil_alchemy_en": (
            "Soil: Weathered cedar planks, highland moss, and ceremonial incense ash. Hendrika Gathering: Cedar Resin and "
            "Temple Incense Powder (Stamina regeneration draughts). Seimei: Wind and Water elemental harmony."
        ),
        "tactics_pt": (
            "A névoa favorece técnicas furtivas e esquivas de alta agilidade. Destrua os biombos para criar novas rotas "
            "de flanco e use o tatame central para confundir o alcance do adversário com ataques aéreos."
        ),
        "tactics_en": (
            "Mist patterns favor stealth repositioning and high-agility dodge rolls. Slash open shoji walls to create flanking "
            "corridors and bait opponents toward exposed cliff drops behind shattered woodwork."
        )
    },

    # 9. OKUNI — PALCO FLUTUANTE DE KABUKI
    {
        "id": "kabuki_stage",
        "fighter_id": "kabuki",
        "name_pt": "Palco Flutuante de Kabuki",
        "name_en": "Floating Kabuki Stage",
        "location_pt": "Leito Arenoso do Rio Kamo, Shijo-Kawaramachi, Kyoto (Entardecer Festivo)",
        "location_en": "Dry Riverbed of the Kamo River, Shijo-Kawaramachi, Kyoto (Festive Dusk)",
        "concept_art": "assets/concepts/kabuki_stage_concept.jpg",
        "historical_context_pt": (
            "O berço histórico do teatro Kabuki fundado pela sacerdotisa Izumo no Okuni nas margens do Rio Kamo. "
            "Construído sobre pilares de pinho sobre a água corrente, o tablado de tábuas de hinoki é decorado com lanternas "
            "de seda vermelha e leques dourados. Durante as noites de festival no Bakumatsu, apresentações dramáticas "
            "mascaravam reuniões conspiratórias entre rebeldes imperiais e cortesãs místicas."
        ),
        "historical_context_en": (
            "The historic birthplace of Kabuki theater founded by priestess Izumo no Okuni on the riverbanks of the Kamo River. "
            "Raised on pine stilts over flowing river waters, the hinoki wood stage is adorned with crimson silk lanterns "
            "and golden fans. During Bakumatsu festival nights, flamboyant dramatic performances masked secret conclaves "
            "between imperial conspirators and mystic courtesans."
        ),
        "hazards_pt": (
            "Queda imediata nas águas caudalosas do Rio Kamo além da borda do tablado de madeira. Lanternas suspensas "
            "que oscilam e podem ser derrubadas para espalhar brasas no piso."
        ),
        "hazards_en": (
            "Instant ring-out drownings in the swift currents of the Kamo River beyond the stage edge. Hanging silk lanterns "
            "that swing dynamically and drop embers when severed by high attacks."
        ),
        "soil_alchemy_pt": (
            "Solo: Tábuas polidas de cipreste Hinoki e pó cerimonial de arroz (Oshiroi). Coleta de Hendrika: Pó Facial Alcalino "
            "e Resina de Madeira Nobre (Criação de névoas ofuscantes). Seimei: Propriedades ricas de Madeira e Fogo."
        ),
        "soil_alchemy_en": (
            "Soil: Polished Hinoki cypress planks and ceremonial white rice powder (Oshiroi). Hendrika Gathering: Alkaline "
            "Face Chalk and Noble Wood Rosin (Blinding smoke mixtures). Seimei: Vibrant Wood and Fire resonance."
        ),
        "tactics_pt": (
            "O formato quadrado e compacto do tablado torna qualquer erro de posicionamento fatal. Force o rival para as bordas "
            "aquáticas utilizando golpes giratórios de leque e ataques em arco amplo para vencer por expulsão."
        ),
        "tactics_en": (
            "The compact square platform amplifies spatial danger. Sweep opponents toward the open water edges with wide "
            "fan arcs and spinning strikes to achieve sudden ring-out victories."
        )
    },

    # 10. TOMOE — SANTUÁRIO DA MONTANHA SAGRADA
    {
        "id": "mountain_shrine",
        "fighter_id": "archer",
        "name_pt": "Santuário da Montanha Sagrada",
        "name_en": "Sacred Mountain Shrine",
        "location_pt": "Pico Espiritual do Monte Kurama, Norte de Kyoto (Tarde Dourada)",
        "location_en": "Spiritual Peak of Mount Kurama, North of Kyoto (Golden Sunset)",
        "concept_art": "assets/concepts/mountain_shrine_concept.jpg",
        "historical_context_pt": (
            "O santuário ancestral de montanha onde, segundo a lenda, Minamoto no Yoshitsune aprendeu os segredos da espada "
            "com o Grande Tengu. Portais Torii de vermelhão enfileirados conduzem ao pátio de pedra cercado por cedros milenares. "
            "Tomoe treina seu tiro com arco Yumi nestas alturas sagradas, protegendo os registros secretos dos templos "
            "contra a profanação das guerras feudais."
        ),
        "historical_context_en": (
            "The ancient mountain shrine where, legend tells, Minamoto no Yoshitsune learned swordcraft from the Great Tengu. "
            "Rows of vermilion Torii gates lead to a flagstone courtyard encircled by thousand-year-old cedars. "
            "Tomoe masters her Yumi archery in these sacred highlands, safeguarding holy temple scrolls from the "
            "profanations of civil war."
        ),
        "hazards_pt": (
            "Portais Torii colossais de madeira que bloqueiam flechas e estocadas lineares. Degraus íngremes de pedra "
            "com desnível que afeta o ângulo de tiros balísticos."
        ),
        "hazards_en": (
            "Colossal vermilion Torii gate pillars blocking arrows and linear thrusts. Steep stone steps that create elevation "
            "shifts impacting projectile trajectories."
        ),
        "soil_alchemy_pt": (
            "Solo: Cascalho branco sagrado (Shirakawa-suna), terra montanhosa e agulhas de cedro. Coleta de Hendrika: Minério "
            "Sagrado e Cânfora de Madeira (Poções de Foco e Estamina). Seimei: Ressonância com Céu, Metal e Madeira."
        ),
        "soil_alchemy_en": (
            "Soil: Sacred white gravel (Shirakawa-suna), mountain loam, and cedar needles. Hendrika Gathering: Purified Cinnabar "
            "and Camphor Crystals (Focus and Stamina enhancements). Seimei: Pure Heaven, Metal, and Wood alignment."
        ),
        "tactics_pt": (
            "Ideal para atiradores de elite. Utilize as colunas dos portais Torii para quebrar o avanço de combatentes de espada curta, "
            "disparando flechas perfurantes nos momentos em que o oponente contorna os pilares."
        ),
        "tactics_en": (
            "Archetype playground for archers and marksmen. Interpose heavy Torii pillars between yourself and melee rushers, "
            "loosing charged arrows as they emerge from cover."
        )
    },

    # 11. ANNE — CONVÉS DO NAVIO CORSÁRIO
    {
        "id": "pirate_deck",
        "fighter_id": "pirate",
        "name_pt": "Convés do Navio Corsário",
        "name_en": "Privateer Ship Deck",
        "location_pt": "Baía de Uraga, Costa de Kanagawa (Tempestade Noturna em Alto-Mar)",
        "location_en": "Uraga Bay, Kanagawa Coast (Night High-Seas Gale)",
        "concept_art": "assets/concepts/pirate_deck_concept.jpg",
        "historical_context_pt": (
            "O convés de carvalho reforçado do galeão corsário capitaneado por Anne Bonny. Ancorado nas proximidades de Uraga "
            "onde os 'Navios Negros' americanos desembarcaram pela primeira vez forçando a abertura do Japão em 1853. "
            "Canhões navais de bronze estão trancados com cordas, barris de rum e pólvora rolam com o balanço das ondas, "
            "e o mar revolto ruge logo abaixo dos mastros sob chuva torrencial."
        ),
        "historical_context_en": (
            "The iron-reinforced oak deck of the privateer frigate captained by Anne Bonny. Anchored near Uraga Bay "
            "where the American 'Black Ships' first forced Japan's opening in 1853. Heavy bronze cannons are lashed with hemp, "
            "rum barrels and gunpowder kegs roll across deck planks with the swell, and violent storm waves crash against the hull."
        ),
        "hazards_pt": (
            "Balanço oscilante do navio e amuradas baixas que permitem arremesso direto no oceano revolto (morte por afogamento). "
            "Barris de pólvora que explodem em contato com projéteis de fogo."
        ),
        "hazards_en": (
            "Rolling deck tilt and low gunwales permitting direct throw ring-outs into raging ocean waves (instant drowning). "
            "Volatile gunpowder kegs that explode upon fire projectile impact."
        ),
        "soil_alchemy_pt": (
            "Solo: Tábuas de teca alcatroadas, sal marinho encrostado e resíduos de pederneira naval. Coleta de Hendrika: "
            "Alcatrão Náutico e Salitre Puro (Multiplica o raio de explosão das bombas). Seimei: Propriedades tempestuosas de Água e Trovão."
        ),
        "soil_alchemy_en": (
            "Soil: Tarred teak planking, crusted sea salt, and naval flint grit. Hendrika Gathering: Maritime Pitch and "
            "Refined Saltpeter (Greatly expands bomb blast radiuses). Seimei: Tempestuous Water and Thunder affinity."
        ),
        "tactics_pt": (
            "O espaço linear e estreito do convés favorece investidas de alfanje e disparos de pistola à queima-roupa. "
            "Empurrar o adversário por cima das amuradas nas laterais norte ou sul garante eliminações instantâneas."
        ),
        "tactics_en": (
            "Linear corridor geometry favors cutlass dashes and point-blank pistol volleys. Forcing adversaries over the "
            "low gunwales on the north or south flanks yields instant knockout ring-outs."
        )
    },

    # 12. JULIE — CORTE BARROCA DA EMBAIXADA FRANCESA
    {
        "id": "baroque_court",
        "fighter_id": "musketeer",
        "name_pt": "Corte Barroca da Embaixada Francesa",
        "name_en": "Baroque Court of the French Embassy",
        "location_pt": "Enclave Diplomático Europeu de Yokohama (Noite de Baile de 1865)",
        "location_en": "European Diplomatic Enclave of Yokohama (Gala Night of 1865)",
        "concept_art": "assets/concepts/baroque_court_concept.jpg",
        "historical_context_pt": (
            "Um palacete com arquitetura clássica francesa erguido no assentamento estrangeiro do porto recém-aberto de Yokohama. "
            "Lustres de cristal pendem de tetos afrescados, colunas de mármore douradas delimitam o salão de baile "
            "e tapeçarias de seda retratam vitórias napoleônicas. Julie atua como guarda de honra e duelista oficial "
            "da missão militar francesa enviada para modernizar as forças do Xogunato."
        ),
        "historical_context_en": (
            "A classical French palace erected in the foreign treaty port settlement of newly opened Yokohama. Crystal chandeliers "
            "hang from frescoed ceilings, gilded marble colonnades outline the grand ballroom, and silk tapestries depict Napoleonic "
            "victories. Julie serves as elite royal guard and official duel champion for the French military mission assisting the Shogunate."
        ),
        "hazards_pt": (
            "Colunas de mármore maciço que ricocheteiam projéteis e limitam o ângulo de corrida. Lustre de cristal suspenso "
            "que desaba sobre o centro se atingido por disparos aéreos."
        ),
        "hazards_en": (
            "Solid marble columns reflecting deflected projectiles and limiting diagonal running lanes. Suspended crystal "
            "chandelier dropping glass shards onto the center if clipped by aerial projectiles."
        ),
        "soil_alchemy_pt": (
            "Solo: Parquet de carvalho nobre encerado e mármore de Carrara polido. Coleta de Hendrika: Cera de Abelha Nobre e "
            "Pó de Mármore (Criação de óleos lubrificantes de alta mobilidade). Seimei: Propriedades elegantes de Metal e Luz."
        ),
        "soil_alchemy_en": (
            "Soil: Waxed oak parquet and polished Carrara marble floor tiles. Hendrika Gathering: Refined Beeswax and "
            "Marble Dust (High-mobility agility draughts). Seimei: Noble Metal and Light element resonance."
        ),
        "tactics_pt": (
            "Piso extremamente liso ideal para as estocadas velozes e passos de esgrima de Julie. Use as colunas de mármore "
            "para quebrar o ímpeto de armas pesadas como machados e clavas, atacando em ângulos agudos."
        ),
        "tactics_en": (
            "Pristine smooth flooring tailored for fencing footwork and blistering rapier lunges. Weave behind marble "
            "colonnades to absorb heavy club or broadsword swings before punishing during weapon recovery."
        )
    },

    # 13. REN — MOSTEIRO SHAOLIN DAS MONTANHAS
    {
        "id": "shaolin",
        "fighter_id": "ren",
        "name_pt": "Mosteiro Shaolin das Montanhas",
        "name_en": "Mountain Shaolin Temple",
        "location_pt": "Pátio dos Mestres, Mosteiro nas Alturas da Província de Henan (Névoa Mística)",
        "location_en": "Masters Courtyard, High Monastery in Henan Province (Mystic Cloud Sea)",
        "concept_art": "assets/concepts/shaolin_temple_concept.jpg",
        "historical_context_pt": (
            "O lendário pátio de treinamento dos monges guerreiros Shaolin nas montanhas Songshan. Marcado por pisos de lajes "
            "de pedra afundadas por séculos de posturas de ferro e estátuas de leões de bronze guardiões. Ren viajou dos "
            "mosteiros da China ao Japão do Bakumatsu para rastrear os ecos de energia espiritual corrompida que prenunciam "
            "o despertar de um demônio colossal que ameaça o equilíbrio do continente."
        ),
        "historical_context_en": (
            "The legendary training terrace of Shaolin warrior monks in the mist-crowned Songshan mountains. Flagstones "
            "bear deep depressions from centuries of iron-stance drills beside roaring bronze guardian lions. Ren crossed from "
            "Chinese temples to Bakumatsu Japan to trace turbulent spiritual echoes forewarning that an ancient demon is stirring."
        ),
        "hazards_pt": (
            "Sinos de bronze cerimonial e estátuas de leão Foo Dog que absorvem golpes. Abismo de névoa sem fundo além "
            "das escadarias do terraço exterior."
        ),
        "hazards_en": (
            "Ceremonial bronze bells and stone Foo Dog sculptures that absorb impact. Bottomless cloud chasm extending past "
            "the open terrace staircases."
        ),
        "soil_alchemy_pt": (
            "Solo: Granito esculpido milenar, terra vermelha de montanha e incenso de lótus. Coleta de Hendrika: Raiz de Ginseng "
            "Selvagem e Cinza de Mirra (Poções de Força e Regeneração). Seimei: Harmonia absoluta dos Cinco Elementos."
        ),
        "soil_alchemy_en": (
            "Soil: Ancient chiseled granite, red highland clay, and lotus incense residue. Hendrika Gathering: Wild Mountain "
            "Ginseng and Myrrh Ash (Strength and Vitality draughts). Seimei: Harmonious balance of all Five Elements."
        ),
        "tactics_pt": (
            "Arena que premia artes marciais de contato corpo a corpo e controle de centro. Use a velocidade das voadoras "
            "e socos Shaolin para prender o adversário contra as estátuas de leão e finalizar com combos aéreos."
        ),
        "tactics_en": (
            "Reward ground for close-quarters kung-fu and center-ring control. Use lightning-quick flying kicks and palm thrusts "
            "to pin foes against stone guardian statues before executing devastating aerial knockouts."
        )
    },

    # 14. CHIYO — CAMPOS VERMELHOS DE HIGANBANA
    {
        "id": "higanbana",
        "fighter_id": "chiyo",
        "name_pt": "Campos Vermelhos de Higanbana",
        "name_en": "Crimson Higanbana Meadows",
        "location_pt": "Planícies de Asuka, Província de Yamato (Crepúsculo Carmesim)",
        "location_en": "Plains of Asuka, Yamato Province (Crimson Dusk)",
        "concept_art": "assets/concepts/higanbana_garden_concept.jpg",
        "historical_context_pt": (
            "Campos infinitos cobertos por lírios vermelhos da aranha (Higanbana), as lendárias flores que florescem "
            "nos cemitérios e marcam a passagem das almas para o pós-vida (Sanzu-no-Kawa). No folclore do Bakumatsu, "
            "a cor carmesim viva das flores deriva do sangue de incontáveis soldados caídos em rebeliões esquecidas. "
            "Chiyo dança entre as flores com sua naginata afiada, guiando os espíritos e expiando o massacre da guerra."
        ),
        "historical_context_en": (
            "Endless plains carpeted in crimson red spider lilies (Higanbana), the fabled blooms that flourish around cemeteries "
            "and guide departed souls across the River Sanzu into the afterlife. In Bakumatsu folklore, the blossoms' deep scarlet "
            "springs from the blood of fallen warriors. Chiyo glides among the blooms with her sweeping naginata, shepherding spirits "
            "and cleansing the slaughter of war."
        ),
        "hazards_pt": (
            "Manto denso de pétalas venenosas que camufla o solo e reduz levemente a precisão de projéteis rasteiros. "
            "Túmulos de pedra antigos que agem como pilares de bloqueio."
        ),
        "hazards_en": (
            "Thick carpet of toxic crimson petals masking ground terrain and slightly swaying low projectile paths. Ancient "
            "moss-grown tombstones acting as immovable obstacle blocks."
        ),
        "soil_alchemy_pt": (
            "Solo: Terra negra de cemitério saturada de alcaloides tóxicos florais. Coleta de Hendrika: Bulbo de Higanbana e "
            "Pólen Paralisante (Componente para Poções de Atordoamento e Veneno). Seimei: Propriedades arcanas de Alma e Madeira."
        ),
        "soil_alchemy_en": (
            "Soil: Dark graveyard earth saturated with toxic floral alkaloids. Hendrika Gathering: Higanbana Flower Bulbs and "
            "Paralytic Pollen (Prime ingredient for Stun and Neurotoxin brews). Seimei: High Soul and Wood occult resonance."
        ),
        "tactics_pt": (
            "O longo alcance da Naginata de Chiyo domina este descampado aberto. Mantenha os duelistas de espada curta "
            "na distância máxima da ponta da lâmina, usando giros de 360 graus para controlar todo o perímetro."
        ),
        "tactics_en": (
            "The sweeping reach of the naginata reigns supreme over these open flats. Keep short-blade rushers at maximum "
            "spearhead range, deploying 360-degree sweeps to deny all flanking maneuvers."
        )
    },

    # 15. BENKEI — PONTE GOJO À MEIA-NOITE
    {
        "id": "gojo_bridge",
        "fighter_id": "benkei",
        "name_pt": "Ponte Gojo à Meia-Noite",
        "name_en": "Gojo Bridge at Midnight",
        "location_pt": "Ponte Gojo sobre o Rio Kamo, Kyoto Central (Madrugada de Lua Cheia)",
        "location_en": "Gojo Bridge over the Kamo River, Central Kyoto (Full Moon Midnight)",
        "concept_art": "assets/concepts/gojo_bridge_concept.jpg",
        "historical_context_pt": (
            "A célebre ponte cerimonial de madeira e pilares de pedra no coração de Kyoto, onde o monge guerreiro Benkei "
            "derrotou 999 samurais para tomar suas lâminas antes de seu mítico encontro com Minamoto no Yoshitsune. "
            "Durante a turbulência do Bakumatsu, a ponte era o posto de controle mais tenso da cidade, onde patrulhas imperiais "
            "e rebeldes cruzavam olhares sob a luz fria da lua cheia sobre as águas negras do rio."
        ),
        "historical_context_en": (
            "The famed ceremonial bridge of timber spans and stone pylons in the heart of Kyoto where the warrior monk Benkei "
            "defeated 999 samurai to claim their swords before meeting Minamoto no Yoshitsune. In the Bakumatsu turbulence, "
            "the bridge became the city's most tense choke point, where imperial patrols and rebels clashed under the icy moonlight "
            "reflected upon dark flowing waters."
        ),
        "hazards_pt": (
            "Corredor estreitíssimo com parapeitos baixos de madeira que podem ser partidos. Queda imediata no rio profundo "
            "em ambas as laterais (vitória por ring-out garantida)."
        ),
        "hazards_en": (
            "Extremely narrow choke-point bridge corridor with fragile wooden railings. Plunging into the deep river waters "
            "on either side results in immediate ring-out drowning."
        ),
        "soil_alchemy_pt": (
            "Solo: Vigas maciças de carvalho tratadas com betume e pregos de ferro fundido. Coleta de Hendrika: Limalha de Ferro "
            "e Resina de Carvalho (Poções de Pele de Pedra / Armadura). Seimei: Propriedades puras de Água e Metal."
        ),
        "soil_alchemy_en": (
            "Soil: Massive oak timbers sealed with pitch and wrought-iron structural nails. Hendrika Gathering: Iron Filings "
            "and Oak Resin (Stone-skin Armor strengthening draughts). Seimei: Water and Metal alignment."
        ),
        "tactics_pt": (
            "A arena de maior risco de ring-out do jogo. Golpes de empurrão com a Kanabo de Benkei ou estocadas longas "
            "jogam o oponente diretamente na água. Nunca role para as bordas laterais durante um choque de lâminas."
        ),
        "tactics_en": (
            "Highest ring-out hazard density in the game. Heavy club knockbacks and linear charges effortlessly catapult "
            "adversaries into the river below. Strictly avoid rolling laterally near the fractured railings."
        )
    },

    # 16. O-RIN — BECO NOTURNO DE YOSHIWARA
    {
        "id": "yoshiwara",
        "fighter_id": "orin",
        "name_pt": "Beco Noturno de Yoshiwara",
        "name_en": "Night Alley of Yoshiwara",
        "location_pt": "Distrito do Prazer de Yoshiwara, Edo (Chuva de Pétalas à Noite)",
        "location_en": "Yoshiwara Pleasure Quarter, Edo (Night Cherry Blossom Rain)",
        "concept_art": "assets/concepts/yoshiwara_alley_concept.jpg",
        "historical_context_pt": (
            "O lendário distrito murado das cortesãs em Edo, iluminado por centenas de lanternas vermelhas de papel e "
            "galhos de cerejeira em flor. Por trás do glamour das danças e do som dos shamisens, os becos escuros abrigavam "
            "espiões, contrabandistas e ronins em busca de refúgio. O-Rin conhece cada reentrância deste labirinto, "
            "usando sua beleza e lâminas ocultas para caçar alvos que ameaçam a paz do distrito."
        ),
        "historical_context_en": (
            "The fabled walled courtesan quarter of Edo, glowing under hundreds of crimson paper lanterns and blooming sakura "
            "branches. Behind the glamorous facade of musical banquets and shamisen melodies, shadowed alleys sheltered spies, "
            "smugglers, and hunted ronin. O-Rin knows every nook of this labyrinth, employing lethal grace and hidden steel "
            "to hunt targets threatening the district's fragile sanctuary."
        ),
        "hazards_pt": (
            "Beco fechado sem perigo de queda, mas cercado por balcões de madeira baixos e varais com quimonos de seda "
            "que cegam temporariamente a visão quando cortados."
        ),
        "hazards_en": (
            "Enclosed alley arena with zero ring-out pits, hemmed in by low timber balconies and laundry lines with hanging silk "
            "kimonos that momentarily obscure sightlines when slashed."
        ),
        "soil_alchemy_pt": (
            "Solo: Paralelepípedos úmidos de Edo, pétalas de cerejeira maceradas e óleo aromático de camélia. Coleta de Hendrika: "
            "Óleo de Camélia e Essência de Cerejeira (Acelera mobilidade e furtividade). Seimei: Propriedades de Água e Madeira."
        ),
        "soil_alchemy_en": (
            "Soil: Moist Edo cobblestones, trampled sakura petals, and fragrant camellia grooming oil. Hendrika Gathering: "
            "Camellia Oil and Sakura Extract (High-speed mobility and stealth potions). Seimei: Water and Wood affinity."
        ),
        "tactics_pt": (
            "Espaço claustrofóbico que anula táticas de fuga e zoneamento longo. Personagens com ataques curtos de adaga "
            "e golpes de desarme conseguem encurralar oponentes nas paredes para combos implacáveis."
        ),
        "tactics_en": (
            "Claustrophobic quarters neutralizing long-range projectile zoning. Short-range dagger wielders and close-contact "
            "brawlers can pin adversaries against the wooden walls for inescapable corner traps."
        )
    },

    # 17. GORO — ARROZAIS E DIQUES DE ÁGUA
    {
        "id": "rice_paddies",
        "fighter_id": "goro",
        "name_pt": "Arrozais e Diques de Água",
        "name_en": "Rice Paddies and Irrigation Dykes",
        "location_pt": "Campos Rurais da Província de Omi (Tarde Chuvosa de Verão)",
        "location_en": "Rural Terraces of Omi Province (Rainy Summer Afternoon)",
        "concept_art": "assets/concepts/rice_paddies_concept.jpg",
        "historical_context_pt": (
            "Os campos agrícolas ancestrais que sustentavam a alimentação da população camponesa e dos exércitos feudais. "
            "Divididos por diques estreitos de terra batida e canais de irrigação de água corrente límpida. Durante as requisições "
            "violentas de arroz e mantimentos feitas por bandos de samurais desertores no Bakumatsu, agricultores como Goro "
            "ergueram enxadas, foices Kama e ancinhos para defender a colheita de suas famílias até a morte."
        ),
        "historical_context_en": (
            "The ancestral agricultural wetlands that sustained rural populations and feeding feudal armies for centuries. "
            "Segmented by narrow earthen dykes and rushing irrigation sluice channels. When renegade samurai bands raided "
            "villages for rice stores during the Bakumatsu, farmers like Goro took up sickles, hoes, and threshing flails "
            "to defend their family harvest to the death."
        ),
        "hazards_pt": (
            "Canais de água que reduzem a velocidade de corrida ao pisar fora dos diques centrais. Cercas de vime e espantalhos "
            "que podem ser estilhaçados em lascas de madeira."
        ),
        "hazards_en": (
            "Flooded paddy water slowing sprint speed when stepping off central raised dykes. Wicker fencing and straw scarecrows "
            "that shatter into flying wooden splinters when struck."
        ),
        "soil_alchemy_pt": (
            "Solo: Lama fértil alagada, palha de arroz fermentada e água doce mineral. Coleta de Hendrika: Nitrato Agrícola e "
            "Lodo Orgânico (Criação de Poções de Lama Paralisante e Ácido). Seimei: Ressonância pura de Terra e Água."
        ),
        "soil_alchemy_en": (
            "Soil: Saturated alluvial mud, decomposed rice straw, and mineral-rich fresh water. Hendrika Gathering: Agricultural "
            "Niter and Organic Sludge (Paralytic mud and caustic acid vials). Seimei: Pure Earth and Water resonance."
        ),
        "tactics_pt": (
            "Lute sempre em cima dos diques elevados de terra batida para preservar a velocidade de esquiva. Arremesse o oponente "
            "para dentro da lama funda do arrozal para cortar sua mobilidade e aplicar golpes de corte pesado sem risco de contra-ataque."
        ),
        "tactics_en": (
            "Fight from the raised dry dykes to maintain crisp dodge recovery. Knock opponents into the submerged mud beds "
            "to rob their foot speed before executing heavy, unhurried sickle cleaves."
        )
    },

    # 18. ICHI — MOINHO CHUVOSO NAS MONTANHAS
    {
        "id": "rain_mill",
        "fighter_id": "ichi",
        "name_pt": "Moinho Chuvoso nas Montanhas",
        "name_en": "Mountain Rain Mill",
        "location_pt": "Passagem de Hakone, Província de Sagami (Chuva Torrencial Contínua)",
        "location_en": "Hakone Mountain Pass, Sagami Province (Torrential Continuous Downpour)",
        "concept_art": "assets/concepts/rain_mill_concept.jpg",
        "historical_context_pt": (
            "Um antigo moinho de grãos movido por uma roda d'água monumental sobre uma cachoeira impetuosa na passagem de Hakone. "
            "Sob a chuva implacável do outono, o barulho constante da água girando as pás abafa qualquer som de passos. "
            "Para Ichi, o espadachim cego, este ambiente barulhento e chuvoso é seu território perfeito: ele não depende da visão, "
            "mas sente as vibrações das gotas e do fluxo do vento para abater qualquer rival que cruze seu caminho."
        ),
        "historical_context_en": (
            "An aged grain mill powered by a massive wooden waterwheel over a rushing cataract in the Hakone mountain pass. "
            "Under relentless autumn rain, the deafening roar of turning water paddles masks all footfalls. "
            "For Ichi, the blind swordsman, this stormy mill is home ground: relying not on sight but on rain vibrations "
            "and wind shifts to cut down any challenger crossing his path."
        ),
        "hazards_pt": (
            "A grande roda d'água de madeira gira continuamente no lado oeste (esmagamento letal se arremessado contra as pás). "
            "A cascata profunda nas costas causa queda fatal imediata."
        ),
        "hazards_en": (
            "The colossal timber waterwheel churns continuously on the west side (lethal crush damage upon contact). "
            "The steep waterfall drop-off to the rear causes instant fatal ring-outs."
        ),
        "soil_alchemy_pt": (
            "Solo: Tábuas de pinho encharcadas de musgo, rochas de rio polidas e névoa d'água. Coleta de Hendrika: Musgo Aquático "
            "e Minério de Moagem (Poções de Foco Sensorial e Estamina). Seimei: Propriedades soberanas de Água e Vento."
        ),
        "soil_alchemy_en": (
            "Soil: Moss-slick pine decking, polished riverstones, and dense water mist. Hendrika Gathering: Aquatic Moss and "
            "Millstone Grit (Sensory focus and stamina recovery brews). Seimei: Overwhelming Water and Wind supremacy."
        ),
        "tactics_pt": (
            "Evite a proximidade da roda d'água giratória a menos que pretenda empurrar o oponente contra as pás de madeira. "
            "Utilize a sonoridade da chuva para mascarar preparações de golpe e use ataques de saque frontal reto."
        ),
        "tactics_en": (
            "Steer clear of the turning waterwheel unless setting up a throw into its crushing wooden paddles. "
            "Rely on straight, lightning-fast linear draws that punish opponents blinded by cascading rain."
        )
    },

    # 19. VALERIUS — CEMITÉRIO PRUSSIANO GÓTICO
    {
        "id": "gothic_cemetery",
        "fighter_id": "valerius",
        "name_pt": "Cemitério Prussiano Gótico",
        "name_en": "Gothic Prussian Cemetery",
        "location_pt": "Cripta Ancestral nas Florestas da Silésia (Noite Eclipsada)",
        "location_en": "Ancestral Crypt in the Silesian Forests (Eclipse Midnight)",
        "concept_art": "assets/concepts/gothic_cemetery_concept.jpg",
        "historical_context_pt": (
            "Um cemitério gótico secular cercado por grades de ferro forjado e mausoléus de granito negro na Europa Central. "
            "Valerius, nobre prussiano e cavaleiro da Ordem Negra, cruzou os continentes fascinado pela lenda do despertar do "
            "Oni Gashadokuro no Japão. Suas pesquisas sobre a imortalidade e necromancia exigem a colheita de almas guerreiras, "
            "e este sepulcro frio é o portal de onde ele conjura espectros e canaliza energia de sepultura para sua lâmina Zweihänder."
        ),
        "historical_context_en": (
            "A centuries-old Gothic necropolis enclosed by wrought-iron fences and black granite mausoleums in Central Europe. "
            "Valerius, Prussian aristocrat and knight of the Black Order, traversed continents enthralled by legends of Oni "
            "Gashadokuro stirring in Japan. His dark quests into immortality and necromancy demand warrior souls, "
            "and this frozen sepulcher serves as the nexus from which he summons apparitions into his Zweihänder blade."
        ),
        "hazards_pt": (
            "Cruzes de ferro pontiagudas e lápides góticas que perfuram oponentes empurrados. Névoa necromântica que causa "
            "lentidão nos cantos mais escuros da arena."
        ),
        "hazards_en": (
            "Jagged iron cemetery spires and stone sarcophagi impaling knocked-back opponents. Spectral ground fog causing "
            "movement sluggishness in the darkest perimeter corners."
        ),
        "soil_alchemy_pt": (
            "Solo: Terra fria de sepultura, pó de ossos humanos e cinza de ferro oxidado. Coleta de Hendrika: Pó Cadavérico e "
            "Óleo Negro (Criação do Fogo Valírio e Venenos Necróticos). Seimei: Afinidade extrema com Escuridão e Morte."
        ),
        "soil_alchemy_en": (
            "Soil: Frozen graveyard soil, pulverized skeletal bone dust, and oxidized iron ash. Hendrika Gathering: Corpse Dust "
            "and Black Ichors (Valyrian Hellfire and necrotic poisons). Seimei: Extreme Darkness and Nether affinity."
        ),
        "tactics_pt": (
            "Use o tamanho titânico da Zweihänder de Valerius para manter os rivais longe das grades de ferro. "
            "Encurrale o oponente contra os túmulos de pedra para garantir que o arco vertical de corte esmague defesas de parry."
        ),
        "tactics_en": (
            "Exploit the immense arc of the Prussian Zweihänder to herd foes toward iron cemetery gates. Pin enemies "
            "against stone crypts where heavy overhead cleaves shatter parry blocks and trigger fatal guard breaks."
        )
    },

    # 20. SEIMEI — SANTUÁRIO HEIAN DE ONMYODO
    {
        "id": "heian_shrine",
        "fighter_id": "seimei",
        "name_pt": "Santuário Heian de Onmyodo",
        "name_en": "Heian Shrine of Onmyodo",
        "location_pt": "Altar Astral de Seimei-jinja, Kyoto Imperial (Meia-Noite sob Eclipse Astral)",
        "location_en": "Astral Altar of Seimei-jinja, Imperial Kyoto (Astral Eclipse Midnight)",
        "concept_art": "assets/concepts/heian_shrine_concept.jpg",
        "historical_context_pt": (
            "O santuário ancestral fundado no local da residência oficial de Abe no Seimei, o maior mestre de Onmyodo da corte imperial. "
            "O pátio sagrado ostenta um imenso Rondel Pentagrama (Gomanboshi) gravado em ouro e mármore branco no chão, alinhado com as "
            "constelações das Quatro Bestas Sagradas. Durante o Bakumatsu, Seimei canaliza os cinco elementos primordiais no círculo mágico "
            "para conter as correntes telúricas malignas do Oni Gashadokuro."
        ),
        "historical_context_en": (
            "The ancestral sanctuary established upon the estate of Abe no Seimei, paramount Onmyodo master of the imperial court. "
            "The holy courtyard features a colossal Pentagram Rondel (Gomanboshi) carved in gold and white marble across the flagstones, "
            "aligned with the constellations of the Four Celestial Beasts. In the Bakumatsu, Seimei channels the five primordial elements "
            "through the magical circle to suppress Gashadokuro's malignant tremors."
        ),
        "hazards_pt": (
            "Glifos elementais no piso do Rondel que disparam labaredas de fogo e rajadas de choque quando ativados por magias. "
            "Estátuas de Shikigami nas quatro quinas que bloqueiam manobras de rolamento."
        ),
        "hazards_en": (
            "Elemental glyphs in the pentagram floor that flare with mystic flames and shock waves when activated by spells. "
            "Four carved Shikigami monoliths at the corners blocking evasive roll paths."
        ),
        "soil_alchemy_pt": (
            "Solo: Mármore branco ritual, pó de jade e areia estelar santificada. Coleta de Hendrika: Mercúrio Alquímico e "
            "Salitre Místico (Elixires de Alta Potência). Seimei: Amplificação de 100% de todos os feitiços do Rondel."
        ),
        "soil_alchemy_en": (
            "Soil: Ritual white marble, jade powder, and sanctified celestial sand. Hendrika Gathering: Alchemical Quicksilver "
            "and Mystic Saltpeter (Maximum Potency brews). Seimei: 100% elemental amplification for all Rondel spells."
        ),
        "tactics_pt": (
            "Controle absoluto da geometria do pátio. Lute no interior do pentagrama para recarregar runas e orbes espirituais. "
            "Use o leque de Seimei para repelir combatentes de espada curta contra os glifos elementais ativos."
        ),
        "tactics_en": (
            "Dominate the courtyard geometry. Position inside the pentagram circle to accelerate spirit orb recharge. "
            "Use tessen fan gusts to blast short-range melee fighters onto active elemental floor glyphs."
        )
    },

    # 21. DAIKI — FLORESTA DOS PINHEIROS NEVADOS
    {
        "id": "pine_forest",
        "fighter_id": "daiki",
        "name_pt": "Floresta dos Pinheiros Nevados",
        "name_en": "Snowy Pine Forest",
        "location_pt": "Trilha dos Peregrinos no Monte Koya (Manhã Glacial de Inverno)",
        "location_en": "Pilgrims Path on Mount Koya (Glacial Winter Dawn)",
        "concept_art": "assets/concepts/pine_forest_concept.jpg",
        "historical_context_pt": (
            "A montanha sagrada do budismo Shingon, coberta por um manto espesso de neve cristalina e pinheiros vermelhos japoneses "
            "de mais de quinhentos anos. Lanternas de pedra votivas cobertas de gelo delimitam a trilha sagrada. Daiki vive aqui "
            "em retiro monástico, empunhando seu pesado cajado de carvalho (Bo) para ensinar a harmonia entre o corpo e o espírito "
            "e proteger os monges contra bandos de saqueadores que aproveitam o caos da guerra civil."
        ),
        "historical_context_en": (
            "The sacred peak of Shingon Buddhism, blanketed under deep crystalline snow and five-hundred-year-old red pines. "
            "Frost-covered stone Toro lanterns mark the ancient pilgrim trail. Daiki lives here in ascetic solitude, wielding "
            "his heavy oak Bo-staff to maintain spiritual peace and shield mountain pilgrims from renegade pillagers exploiting "
            "the Bakumatsu civil war."
        ),
        "hazards_pt": (
            "Neve fofa que reduz a aceleração inicial de corrida. Galhos de pinheiro pesados de gelo que desabam blocos de neve "
            "quando golpeados por armas altas, atordoando combatentes embaixo."
        ),
        "hazards_en": (
            "Deep snowbanks reducing initial sprint acceleration. Heavy frost-laden pine branches that drop snow packs "
            "when struck by high swings, momentarily dazing combatants beneath."
        ),
        "soil_alchemy_pt": (
            "Solo: Terra congelada sob neve virgem, agulhas de pinheiro vermelho e resina âmbar. Coleta de Hendrika: Seiva de Pinheiro "
            "e Cristais de Gelo Puro (Poções de Resfriamento e Vigor). Seimei: Propriedades de Madeira e Água/Gelo."
        ),
        "soil_alchemy_en": (
            "Soil: Frozen permafrost under virgin snow, red pine needles, and fossil amber resin. Hendrika Gathering: Pine Resin "
            "and Pure Frost Crystals (Chilling ice vials and Stamina brews). Seimei: Wood and Water/Ice affinity."
        ),
        "tactics_pt": (
            "O alcance de 360 graus do cajado Bo de Daiki domina as clareiras de neve. Mantenha os espadachins a meia distância "
            "onde o impacto da madeira esmaga a guarda do adversário antes que ele consiga entrar no raio da katana."
        ),
        "tactics_en": (
            "The sweeping 360-degree reach of the oak staff dominates snowy clearings. Keep swordsmen at mid-range where the "
            "kinetic force of the wooden Bo shatters guard postures before they can step into katana cutting range."
        )
    },

    # 22. AOI — TAIGA SELVAGEM DE EZO
    {
        "id": "ezo_taiga",
        "fighter_id": "aoi",
        "name_pt": "Taiga Selvagem de Ezo",
        "name_en": "Wild Taiga of Ezo",
        "location_pt": "Florestas Primitivas de Hokkaido (Terras Ancestrais Ainu, Inverno Rigoroso)",
        "location_en": "Primeval Wilderness of Hokkaido (Ancestral Ainu Lands, Deep Winter)",
        "concept_art": "assets/concepts/ezo_taiga_concept.jpg",
        "historical_context_pt": (
            "A imensidão selvagem do extremo norte do Japão, antes de ser rebatizada como Hokkaido durante a Restauração Meiji. "
            "Bosques de bétulas brancas cobertos por nevascas ferozes, habitados por ursos-pardos de Ussuri e tribos Ainu que mantêm "
            "suas tradições em comunhão com os espíritos da natureza (Kamuy). Aoi caça nestas florestas glaciais com seu arco de chifre "
            "e faca cerimonial Makiri, caçando desertores militares que trazem a podridão da guerra para as terras sagradas."
        ),
        "historical_context_en": (
            "The untamed primeval frontier of Japan's far north, prior to being renamed Hokkaido during the Meiji Restoration. "
            "Dense birch forests lashed by Arctic blizzards, prowled by Ussuri brown bears and protected by Ainu clans living in "
            "harmony with nature spirits (Kamuy). Aoi patrols these glacial taiga forests with her horn composite bow and ceremonial "
            "Makiri blade, purging renegade soldiers who bring the rot of civil war into sacred wilderness."
        ),
        "hazards_pt": (
            "Nevasca contínua com rajadas de vento que alteram a velocidade de projéteis leves. Lagos de gelo fino quebradiço "
            "onde combatentes caem na água congelante se pisarem em rachaduras."
        ),
        "hazards_en": (
            "Continuous Arctic blizzard with wind shear altering arrow trajectories. Thin frozen ice patches that fracture under "
            "heavy footfalls, plunging combatants into freezing water."
        ),
        "soil_alchemy_pt": (
            "Soil: Permafrost glacial, líquen de rena e chifre de cervo triturado. Coleta de Hendrika: Líquen Ártico e "
            "Gelo Puro (Elixires de Velocidade e Resfriamento). Seimei: Máxima ressonância com Água, Gelo e Vento."
        ),
        "soil_alchemy_en": (
            "Soil: Glacial permafrost, reindeer lichen, and crushed antler silt. Hendrika Gathering: Arctic Lichen and "
            "Permanent Ice (Speed Draughts and Cryogenic Flasks). Seimei: Peak resonance with Water, Ice, and Wind."
        ),
        "tactics_pt": (
            "Aproveite as rajadas de neve para mascarar disparos de flecha à distância. Atraia o adversário para as manchas de gelo fino "
            "e use disparos rasteiros para forçar quedas d'água incapacitantes."
        ),
        "tactics_en": (
            "Use blizzard gusts to mask long-distance bow shots. Lure aggressively charging rushers onto thin ice fractures "
            "to cause chilling stumbles that guarantee lethal arrow follow-ups."
        )
    },

    # 23. RAIDEN — DOHYO SAGRADO DO SANTUÁRIO XINTOÍSTA
    {
        "id": "sacred_dohyo",
        "fighter_id": "raiden",
        "name_pt": "Dohyo Sagrado do Santuário Xintoísta",
        "name_en": "Sacred Dohyo of the Shinto Shrine",
        "location_pt": "Grande Santuário de Sumiyoshi Taisha, Osaka (Alvorecer Cerimonial)",
        "location_en": "Grand Shrine of Sumiyoshi Taisha, Osaka (Ceremonial Dawn)",
        "concept_art": "assets/concepts/sacred_dohyo_concept.jpg",
        "historical_context_pt": (
            "O círculo cerimonial de argila batida (Dohyo) construído sob o teto suspenso de estilo Shinto que emula os santuários sagrados. "
            "Antes de ser um esporte, o Sumô era um ritual sagrado para apaziguar os deuses (Kami) e garantir colheitas férteis. "
            "No crepúsculo do Bakumatsu, o Grande Campeão Raiden pisa no barro consagrado para provar que a força física pura e a devoção "
            "espiritual sobrepujam qualquer arma de fogo ou katana forjada pelo homem."
        ),
        "historical_context_en": (
            "The sacred clay ring (Dohyo) consecrated beneath a floating Shinto shrine-style roof canopy. Before becoming a sport, "
            "Sumo was a sacred Shinto ceremony performed to appease the gods (Kami) and ensure bountiful harvests. "
            "In the Bakumatsu twilight, Grand Champion Raiden stamps the consecrated ring to demonstrate that pure physical mass "
            "and divine devotion surpass any firearm or steel blade forged by man."
        ),
        "hazards_pt": (
            "O anel elevado de fardos de palha (Tawara): pisar fora do círculo sagrado constitui Ring-Out e derrota instantânea! "
            "Pilares de madeira do dossel que esmagam oponentes arremessados."
        ),
        "hazards_en": (
            "The raised boundary ring of woven straw bales (Tawara): being pushed or knocked outside the circle is an instant Ring-Out defeat! "
            "Massive wooden shrine canopy pillars dealing heavy rebound impact."
        ),
        "soil_alchemy_pt": (
            "Solo: Argila cerimonial de Arakida compactada e purificada com sal consagrado. Coleta de Hendrika: Sal Sagrado de Purificação "
            "e Terra de Altar (Poções de Resistência e Neutralização de Veneno). Seimei: Propriedades sagradas de Terra e Pureza."
        ),
        "soil_alchemy_en": (
            "Soil: Consecrated Arakida clay compacted and cleansed with sacred ritual salt. Hendrika Gathering: Sanctified Purifying Salt "
            "and Shrine Earth (Resistance and Poison Neutralizing draughts). Seimei: Sacred Earth and Purity elemental alignment."
        ),
        "tactics_pt": (
            "A arena de Ring-Out por excelência. Controle o centro absoluto do círculo. Utilize as palmadas pesadas (Harite) e empurrões "
            "corporais de Raiden para forçar o rival contra os fardos de palha Tawara, encerrando a luta com expulsão imediata."
        ),
        "tactics_en": (
            "The quintessential Ring-Out arena. Maintain absolute center-ring supremacy. Deploy Raiden's heavy open-palm slaps (Harite) "
            "and unstoppable body thrusts to drive challengers over the Tawara straw perimeter for instant victories."
        )
    },

    # 24. HENDRIKA — ARMAZÉM DE DEJIMA COM DOCA CHUVOSA
    {
        "id": "dejima_dock",
        "fighter_id": "hendrika",
        "name_pt": "Armazém de Dejima com Doca Chuvosa",
        "name_en": "Dejima Warehouse with Rainy Dock",
        "location_pt": "Feitoria Comercial Holandesa de Dejima, Porto de Nagasaki (Noite Tempestuosa de 1866)",
        "location_en": "Dutch Trading Post of Dejima, Port of Nagasaki (Stormy Night of 1866)",
        "concept_art": "assets/concepts/dejima_warehouse_concept.jpg",
        "historical_context_pt": (
            "A ilha artificial em forma de leque na baía de Nagasaki que funcionou por mais de dois séculos como o único "
            "ponto de contato comercial e científico entre o Japão fechado (Sakoku) e o mundo ocidental através da Companhia Holandesa "
            "das Índias Orientais (VOC). Entre armazéns de madeira repletos de especiarias, livros de medicina ocidental (Rangaku), "
            "alambiques de vidro e barris de produtos químicos importados, Hendrika montou seu laboratório clandestino para colher "
            "reagentes raros trazidos pelos navios e destilar compostos proibidos sob a chuva constante do porto."
        ),
        "historical_context_en": (
            "The fan-shaped artificial island in Nagasaki harbor that served for over two centuries as Japan's sole window of trade "
            "and scientific exchange (Rangaku) with the Western world via the Dutch East India Company (VOC). Among timber warehouses "
            "packed with spices, anatomical treatises, glass retorts, and imported chemical carboys, Hendrika established her clandestine "
            "laboratory to gather rare overseas reagents and brew forbidden compounds under the harbor's ceaseless downpours."
        ),
        "hazards_pt": (
            "Doca marítima sem guarda-corpo no lado sul: queda direta nas águas profundas do porto (morte imediata por afogamento). "
            "Garrafões de vidro e frascos químicos destrutíveis que, ao quebrarem com golpes de espada, espalham poças corrosivas de ácido."
        ),
        "hazards_en": (
            "Unguarded ocean dock edge along the southern pier: direct drop into harbor depths (instant drowning ring-out). "
            "Destructible glass carboys and chemical retorts that shatter under weapon strikes, leaving caustic acid pools across the floor."
        ),
        "soil_alchemy_pt": (
            "Solo: Tábuas de pinho tratadas com zarcão, encharcadas de água salgada, resíduos de ácido sulfúrico e pó de enxofre importado. "
            "Coleta de Hendrika: Enxofre Puro, Salitre Fino e Resíduos Ácidos (O paraíso alquímico: tempo de coleta reduzido em 30%!). "
            "Seimei: Propriedades corrosivas de Água, Metal e Fogo."
        ),
        "soil_alchemy_en": (
            "Soil: Salt-soaked pine dock planks stained with red lead, sulfuric acid residues, and imported elemental sulfur powder. "
            "Hendrika Gathering: Pure Sulfur, Fine Saltpeter, and Caustic Residues (The Alchemical Paradise: gathering speed boosted by 30%!). "
            "Seimei: Corrosive Water, Metal, and Fire elemental blend."
        ),
        "tactics_pt": (
            "O paraíso dos combatentes alquímicos e táticos. Quebre os frascos de reagente intencionalmente para criar barreiras de ácido "
            "que desintegram a postura do oponente. Use o florete rápido de Hendrika para empurrar os atacantes em direção à borda da doca chuvosa."
        ),
        "tactics_en": (
            "Tactical haven for alchemists and fencing specialists. Deliberately shatter reagent carboys to lay down acid zones that "
            "disintegrate enemy poise. Utilize swift rapier lunges to herd overeager brawlers off the wet dock into the harbor."
        )
    }
]
