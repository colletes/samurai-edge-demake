"""
Comprehensive English dataset for the Samurai Edge Official Game Manual in PDF.
"""

LORE_EN = {
    "title": "THE LEGEND OF BAKUMATSU & THE ASH SEAL",
    "p1": (
        "In the twilight of the 19th century (1860s), Japan was rocked by the sudden arrival of Western 'Black Ships', "
        "shattering more than two centuries of sacred isolation (Sakoku). The realm fractured into a savage civil war: "
        "on one side stood the Tokugawa Shogunate loyalists fighting to preserve feudal order; on the other, imperial "
        "nationalists and rebel clans demanding the supreme restoration of the Emperor."
    ),
    "p2": (
        "Yet beneath the veil of political upheaval and the merciless advance of rifled firearms, an ancient and far more "
        "terrifying power stirred. In the impenetrable mountain fastness of Iga Province, buried deep within the stygian "
        "depths of the Shadow Cave, lay sealed for over a thousand years the Oni Gashadokuro: a colossal skeletal titan "
        "forged from the condensed hatred and agony of myriad warriors and innocents slain in forgotten wars and left unburied."
    ),
    "p3": (
        "The ancient prophecies of the Onmyodo mystics warned that should Japan's soil once again be flooded with the blood "
        "of unavenged fallen warriors, the spiritual talismans binding the titan would shatter. Unwittingly, each deadly duel "
        "fought in the burning streets of Kyoto, each ambush in the sacred bamboo groves, and each assassination on the rainy "
        "docks of Dejima feeds the swelling darkness, accelerating the return of the starving titan to consume all life across Japan."
    )
}

FACTIONS_EN = [
    {
        "name": "1. Protectors of the People & Virtuous Ronin",
        "desc": "Swordsmen, miko archers, monks, and peasant farmers who took up arms not for political dominion, but to shield vulnerable villages, temples, and innocent families from the rampant slaughter of civil war.",
        "members": ["Kenshi", "Tomoe", "Daiki", "Goro", "Benkei"],
        "philosophy": "The life-giving sword (Katsujinken). Defending the defenseless against tyranny and merciless warlords."
    },
    {
        "name": "2. Peak Duelists & Glory Seekers",
        "desc": "Legendary martial artists who view the chaos of the Bakumatsu as the ultimate crucible to test their physical limits and spiritual discipline against the deadliest fighters alive.",
        "members": ["Musashi", "Ren", "Raiden"],
        "philosophy": "The uncompromising pursuit of absolute martial mastery, where every clash of steel is a direct communion with mortality."
    },
    {
        "name": "3. Loyalists & Order Servants",
        "desc": "Disciplined soldiers and officers bound by unbreakable oaths of loyalty to their commanders, the Shogunate, the Imperial Court, or sovereign foreign crowns.",
        "members": ["Saitou", "Julie", "Ichi"],
        "philosophy": "Absolute duty, unyielding military discipline, and steadfast allegiance to the banners they swore to uphold until their dying breath."
    },
    {
        "name": "4. Opportunists & Chaos Scientists",
        "desc": "Eccentric foreign savants, arcane necromancers, and mystic dancers operating in the shadowed crevices of civil war, turning spilled blood into forbidden alchemical and spiritual power.",
        "members": ["Hendrika", "Valerius", "Okuni"],
        "philosophy": "Chaos is a fertile laboratory. Traditional feudal morals are cast aside in the pursuit of revolutionary alchemical and occult breakthroughs."
    },
    {
        "name": "5. Mercenaries & War Privateers",
        "desc": "High-seas corsairs and freelance riflemen plying the fractured trade ports and battlefields of feudal Japan in search of gold, gunpowder, and untamed personal liberty.",
        "members": ["Anne", "Teppo"],
        "philosophy": "Survival, coin, and independence. Fighting for the highest bidder or their own crew without subservience to feudal daimyo."
    },
    {
        "name": "6. The Seal Keepers (Iga Shinobi Clan)",
        "desc": "The shadow elite of Iga. Feared as ruthless shadow assassins, they form the secret defense line guarding the subterranean Shadow Cave to keep Oni Gashadokuro chained.",
        "members": ["Hanzo", "Kasumi", "Murasaki"],
        "philosophy": "Silent sacrifice. Keeping the ancient titan asleep even if the world reviles them as cold-blooded specters."
    },
    {
        "name": "7. The Time Traveler & Unlikely Ally",
        "desc": "A 21st-century American marine and tactical operative, obsessed with anime and martial pop culture, who was violently displaced across time into the dawn of the Meiji Restoration.",
        "members": ["Joe"],
        "philosophy": "High-tech survival with anime ninja flair. Upon uncovering the noble purpose of the Iga Shinobi, swore his modern arsenal and doberman to their cause."
    }
]

CONTROLS_EN = {
    "title": "CORE CONTROLS & DUEL MECHANICS",
    "desc": (
        "Samurai Edge features an isometric diegetic combat system inspired by the classic cinema of Akira Kurosawa "
        "and the lethal precision of Bushido Blade. Every single strike carries brutal consequence and 3D positioning demands."
    ),
    "table": [
        ("8-Way Movement", "D-Pad / Left Stick", "[W, A, S, D] (P1) / [Arrow Keys] (P2)", "Tactical positioning and arena displacement"),
        ("Primary Strike", "X Button / Square", "[E] (P1) / [U] (P2)", "Main weapon slash, quick-draw, thrust, or rifle shot"),
        ("Secondary Action", "Y Button / Triangle", "[R] (P1) / [I] (P2)", "Special stance, projectile volley, or alchemical brew"),
        ("Block / Parry", "RB / R1", "[F] (P1) / [O] (P2)", "Defensive guard with precise parry window and projectile deflection"),
        ("Evasive Roll", "A Button / Cross", "[Space] (P1) / [P] (P2)", "Low-profile acrobatic tumble with invulnerability frames"),
        ("Tactical Leap", "LB / L1", "[Q] (P1) / [Y] (P2)", "Vertical and directional leap over chasms and ground hazards"),
        ("Pause / Menu", "Start / Options", "[ESC]", "Ceremonial pause overlay upon Sumi-E parchment")
    ],
    "mechanics": [
        ("Blade Clash (Clash QTE)", "When two simultaneous strikes collide within the same spatial hitbox frame, the weapons lock with cinematic sparks. The fighter who mashes the attack button faster wins the clash and inflicts an off-balance stagger upon the opponent."),
        ("Absolute Precedence", "Specific signature attacks (such as Murasaki's Kusarigama Scythe or Hendrika's Piercing Rapier) boast hard-coded priority, interrupting standard swings and cutting off opponent momentum."),
        ("Guard Crush", "Caustic acid-coated weapons, heavy artillery rounds, and titanic war hammers shatter parry stances, inflicting extended stun frames upon the defender."),
        ("Surgical Lethality", "Combatants possess between 1 and 3 Hit Points (HP). A single clean strike landed during opponent recovery or counter-hit decides the fate of the round immediately.")
    ]
}

MODES_EN = {
    "title": "COMBAT MODES & PROGRESSION",
    "arcade_title": "ARCADE MODE — THE 12-FIGHT LADDER",
    "arcade_desc": (
        "The definitive solo campaign. The player chooses a champion and ascends a gauntlet of 12 ceremonial duels "
        "where spilled blood resonates across feudal Japan, fracturing the ancient seals of the Shadow Cave:"
    ),
    "arcade_stages": [
        ("Fights 1 to 8: Ranked Duels", "Classic Best-of-3 (BO3) duels against 8 fighters seeded democratically across all four difficulty tiers, ensuring dynamic and unpredictable journeys."),
        ("Fight 9: Mirror Match", "The champion faces their own spectral doppelgänger within their home arena. A psychological and technical battle of identical weapons and identical range."),
        ("Fight 10: Endurance Challenge", "Two elite adversaries in unbroken succession, sharing only 2 round lives. Victory demands discipline and spatial conservation."),
        ("Fight 11: The Seal Keepers (Ninja Gauntlet)", "Entry into the stygian Shadow Cave. The player must vanquish the entire phalanx of the 4 Iga Guardians (Joe, Kasumi, Murasaki, and Hanzo) amid toxic vapors."),
        ("Fight 12: Titan's Awakening (Final Boss)", "With the guardians fallen, the thousand-year seal shatters. The gargantuan Oni Gashadokuro rises from the cavern ashes in a colossal 1-round survival showdown.")
    ],
    "versus_title": "LOCAL VERSUS & AI DUELS",
    "versus_desc": (
        "Direct combat for 2 local players or player versus Artificial Intelligence. Offers unrestricted selection "
        "across all 24 fighters, 24 thematic arenas, round limits (1 to 5), and 3 distinct AI difficulty levels (Easy, Normal, Hard)."
    )
}

BOSS_TEASER_EN = {
    "title": "THE FORBIDDEN AWAKENING — FINAL BOSS",
    "name": "ONI GASHADOKURO (鬼鵺・餓者髑髏)",
    "subtitle": "The Skeletal Titan Forged from the Malice of Ten Thousand Unburied Corpses",
    "concept_art": "assets/concepts/gashadokuro_silhouette_tease.jpg",
    "lore": (
        "In the unfathomable abyss of the Iga Shadow Cave, beyond forgotten altars and sacred Shimenawa talismans, "
        "lies feudal Japan's most horrifying secret. The Gashadokuro is no mere demon: it is a supernatural force of nature, "
        "a titanic abomination sculpted from the fused bones of countless warriors, peasants, and innocents butchered across "
        "centuries of civil war from the Sengoku era to the twilight of the Bakumatsu. "
        "\n\nThe four Iga Shinobi Guardians (Hanzo, Kasumi, Murasaki, and Joe) dedicated their lives to driving away all intruders "
        "to keep the cavern floor undisturbed. But when the twelve duels of the Arcade Ladder conclude and the blood of Japan's "
        "greatest duelists is swallowed by subterranean rifts, the mystic talismans rupture with thunderous fury. "
        "Twin incandescent eyes blaze within the void, and a colossal skeletal hand armed with iron talons tears through "
        "the earth to scour the realm of the living."
    ),
    "warning_title": "FINAL BATTLE TACTICAL DIRECTIVE",
    "warning_points": [
        ("Unshakable Mass (Hyper-Armor)", "Oni Gashadokuro completely disregards knockback and stagger from standard sword slashes. Never attempt to contest priority head-on."),
        ("Earthquake Impacts & Titanic Greatclub", "Its vertical ground slams shatter cavern flagstones, sending razor stalactites raining across the entire arena."),
        ("Spectral Fatigue Window", "Following a catastrophic three-hit assault, the Titan enters a fleeting state of spiritual exhaustion. This is your sole opportunity to execute high-damage clean cuts."),
        ("Single-Round Sudden Death", "There are no second chances against Gashadokuro. A single misstep in positioning results in instant and total annihilation.")
    ]
}

APPENDIX_EN = {
    "title": "TECHNICAL APPENDIX & COMBAT DATA",
    "tier_title": "OVERALL PERFORMANCE & WINRATE TABLE (6,624 SIMULATED MATCHES)",
    "tier_desc": (
        "Compiled from the official large-scale tournament simulation with symmetric arena parity "
        "(Sacred Dohyo, Iga Rooftops, Ganryu Island, and Kyoto in Flames) against NORMAL AI difficulty:"
    ),
    "tier_table": [
        ("1", "Seimei", "Ofuda Onmyoji (Talisman Wards / Five Elements Rondel)", "125", "51", "67.9%", "Tier S"),
        ("2", "Teppo", "Gunpowder Marksman (Tanegashima Matchlock / Bayonet)", "116", "66", "63.0%", "Tier S"),
        ("3", "Hanzo", "Iga Grandmaster (Kunai Barrage / Tactical Quick-Draw)", "115", "69", "62.5%", "Tier S"),
        ("4", "Saitou", "Wolf of Mibu (Shinsengumi / Gatotsu Piercing Lunge)", "115", "68", "62.5%", "Tier S"),
        ("5", "Hendrika", "Dejima Alchemist (Stiletto Rapier / 5 Chemical Reagents)", "109", "74", "59.2%", "Tier S"),
        ("6", "Joe", "Tactical American Ninja (Shuriken / Assault Rifle / Doberman)", "108", "76", "58.7%", "Tier S"),
        ("7", "Kenshi", "Twilight Battousai (Hiten Iaijutsu / Shukuchi Dash)", "107", "76", "58.1%", "Tier S"),
        ("8", "Tomoe", "Sacred Miko Archer (Yumi Longbow / Piercing Spirit Arrow)", "107", "77", "58.1%", "Tier S"),
        ("9", "Murasaki", "Shadow Kunoichi (Venomous Scythe Kusarigama)", "93", "90", "50.5%", "Tier B"),
        ("10", "Valerius", "Prussian Necromancer (Zweihänder / Nether Flame Magic)", "93", "91", "50.5%", "Tier B"),
        ("11", "Ichi", "Blind Cane Sword (Shikomizue / Reverse Gyaku-Iai)", "92", "90", "50.0%", "Tier B"),
        ("12", "Musashi", "Dual Kensei (Niten Ichi-ryu / Twin Katana Cross-Cut)", "87", "96", "47.3%", "Tier B"),
        ("13", "Kasumi", "Mist Kunoichi (Ninja-to / Concealment Smoke Flasks)", "87", "96", "47.3%", "Tier B"),
        ("14", "Aoi", "Wilderness Ainu Hunter (Composite Horn Bow / Makiri Knife)", "87", "97", "47.3%", "Tier B"),
        ("15", "Chiyo", "Blade Dancer (Dual Higanbana Nodachi Whirlwind)", "82", "102", "44.6%", "Tier C"),
        ("16", "Daiki", "Pilgrim of the Staff (Oak Bo / High Pole-Vault Sweep)", "81", "103", "44.0%", "Tier C"),
        ("17", "Goro", "Rebel Farmer (Forged Kuwa Sickle / Seismic Stomp)", "80", "103", "43.5%", "Tier C"),
        ("18", "Anne", "Privateer Captain (180° Pirate Cutlass / Flintlock Pistol)", "78", "105", "42.4%", "Tier C"),
        ("19", "Julie", "Royal Musketeer (French Rapier / Precise Counter-Riposte)", "77", "107", "41.9%", "Tier D"),
        ("20", "Ren", "Shaolin Iron Fist (Vibrational Palm / Lightning Flurry Kicks)", "76", "107", "41.3%", "Tier D"),
        ("21", "O-Rin", "Yoshiwara Minstrel (Bladed Shamisen / Concealed Stiletto)", "74", "105", "40.2%", "Tier D"),
        ("22", "Okuni", "Kabuki Priestess (Razor Tessen Fan / Poison Miasma Cloud)", "70", "113", "38.0%", "Tier D"),
        ("23", "Raiden", "Undefeated Yokozuna (Heavy Tsuppari Palms / Tachiai Charge)", "68", "111", "37.0%", "Tier D"),
        ("24", "Benkei", "Sohei Warrior Monk (Iron-Studded Kanabo / Titanic Naginata)", "64", "118", "34.8%", "Tier D")
    ],
    "soil_table_title": "SOIL REAGENTS & CLANDESTINE ALCHEMY TABLE (HENDRIKA & SEIMEI)",
    "soil_table": [
        ("Dejima Warehouse / Harbor Docks", "Pure Sulfur, Refined Saltpeter, Acid Residues", "Acid Vial (Guard Crush) & Alchemical Fire", "+30% gathering speed bonus"),
        ("Kyoto in Flames / City Streets", "Fresh Blood, Fire Soot, Coarse Gunpowder", "Lethal Poison Vial & Incendiary Grenade", "Inherent fire damage resistance"),
        ("Groves / Red Pines / Snowy Taiga", "Medicinal Roots, Pine Sap, Amber Resin", "HP Restoration Draught & Max Stamina Brew", "Accelerates dodge cooldown"),
        ("Cemeteries / Stygian Cave", "Corpse Dust, Toxic Fungal Spores, Black Ash", "Blinding Mist Flask & Paralytic Neurotoxin", "Applies slow status to opponent"),
        ("Sacred Shrines / Consecrated Dohyo", "Sanctified Salt, Camphor, Star Gravel", "Iron-Skin Elixir & Focus Draught", "Neutralizes poisons and bleed")
    ],
    "credits_title": "PRODUCTION CREDITS",
    "credits": [
        ("Original Concept & Game Design", "Thiago Carvalho"),
        ("Code Architecture & AI Systems", "Antigravity AI (Google DeepMind)"),
        ("Art Direction & 3D Voxel Sculpting", "Samurai Edge Bakumatsu Studio"),
        ("Music & Soundscapes", "Original Bakumatsu Folk Compositions"),
        ("Special Dedication", "To all masters of epic samurai cinema and the golden era of 90s fighting game manuals.")
    ]
}
