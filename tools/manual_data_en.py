"""
Complete English database for generating the official Samurai Edge Game Manual PDF.
Final High-Density Condensed Edition (24 Pages).
"""

LORE_EN = {
    "title": "THE LEGEND OF BAKUMATSU & THE ASH SEAL",
    "p1": (
        "In the twilight of the 19th century (1860s), Japan was violently shaken by the sudden arrival of Commodore Perry's "
        "'Black Ships', abruptly shattering over two centuries of sacred isolation (Sakoku). The land of the rising sun fractured "
        "into a savage, merciless civil war: on one side stood the Tokugawa Shogunate loyalists fighting to preserve feudal order "
        "and the samurai caste; on the other, rebel imperialists from Choshu and Satsuma demanding supreme imperial restoration."
    ),
    "p2": (
        "Yet beneath the veil of political assassinations and the relentless advance of Western firearms, a far more terrifying "
        "primordial nightmare stirred. In the impenetrable, mist-shrouded peaks of Iga Province, within the eternal dark of the "
        "Shadow Cave, lay sealed for over a millennium the Oni Gashadokuro: a colossal skeletal titan forged from the collective malice "
        "and despair of tens of thousands of warriors slain in ancient wars and abandoned without burial."
    ),
    "p3": (
        "Ancient Onmyodo prophecy foretold that should Japan's soil once again become saturated with the spilled blood of unsettled "
        "souls, the divine shimenawa cords binding the colossus would shatter. Unwittingly, every clash of steel across burning Kyoto "
        "streets, every ambush in bamboo thickets, and every duel on rain-slicked Dejima wharves feeds this awakening darkness, "
        "hastening the titan's return to extinguish all life across the four islands of Japan."
    ),
    "p4": (
        "While political warlords scheme behind guarded shoji screens, highways and terraced rice paddies have turned into hunting grounds "
        "for masterless ronin, clandestine alchemists, and wandering swordsmen. The fate of the nation no longer rests upon diplomatic "
        "treaties sealed in ink: it will be carved by the razor edge of drawn steel."
    ),
    "p5": (
        "Only those who conquer the fear of mortality and master the razor-thin fraction of a second between a lethal draw and the void "
        "of a whiffed strike will reach the heart of the Iga mountains, deciding whether Japan will rise into a new dawn of honor "
        "or be swallowed whole by the titan of ash and iron."
    ),
    "quote": "«Upon the razor's edge, between the draw and the cleave, there is no room for hatred: only the naked truth of steel.»"
}

FACTIONS_EN = [
    {
        "name": "1. Protectors of the People & Virtuous Ronin",
        "desc": "Swordsmen, archers, monks, and rebellious peasants who took up arms not for political dominion, but to defend helpless villages, shrines, and innocents against the carnage and pillaging of civil war.",
        "members": ["Kenshi", "Tomoe", "Daiki", "Goro", "Benkei"],
        "philosophy": "The life-giving sword (Katsujinken). Defending the defenseless against feudal tyranny and the rampaging violence of warlords."
    },
    {
        "name": "2. Duelists of the Pinnacle & Glory Seekers",
        "desc": "Legendary martial artists who view the turbulence of the Bakumatsu as the ultimate crucible to test their physical and spiritual limits against the deadliest fighters alive.",
        "members": ["Musashi", "Ren", "Raiden"],
        "philosophy": "Uncompromising pursuit of supreme martial mastery, where every blade duel is an intimate dialogue with mortality itself."
    },
    {
        "name": "3. Loyalists & Keepers of the Order",
        "desc": "Disciplined soldiers bound by unshakable oaths of allegiance to their commanders, the Shogunate, the Emperor, or foreign sovereign crowns.",
        "members": ["Saitou", "Julie", "Ichi"],
        "philosophy": "Absolute duty, martial honor, and blind loyalty to the banner they swore to protect until their dying breath."
    },
    {
        "name": "4. Opportunists & Scientists of Chaos",
        "desc": "Eccentric scholars, eldritch necromancers, and mystic dancers operating within the shadows of war, exploiting spilled blood to conduct forbidden experiments and harness occult power.",
        "members": ["Hendrika", "Valerius", "Okuni"],
        "philosophy": "Chaos is fertile soil. Traditional morality is cast aside in favor of empirical alchemical breakthrough and spiritual harvest."
    },
    {
        "name": "5. Mercenaries & Privateers of War",
        "desc": "Guns for hire and audacious seafarers navigating maritime trade and feudal strife in relentless pursuit of gold, black powder, and unbridled freedom.",
        "members": ["Anne", "Teppo"],
        "philosophy": "Survival, gold, and sovereignty. Fighting for the highest bidder or their own loyal crew without fealty to feudal lords."
    },
    {
        "name": "6. Guardians of the Seal (Iga Shinobi Clan)",
        "desc": "The shadow elite of Iga. Feared as ruthless assassins by the outside world, they are in truth the clandestine vanguard guarding the Shadow Cave to prevent the slumbering Oni Gashadokuro from rising.",
        "members": ["Hanzo", "Kasumi", "Murasaki", "Chiyo"],
        "philosophy": "Invisible sacrifice. Preserving the ancient seal even if history forever condemns them as cruel monsters."
    },
    {
        "name": "7. The Temporal Traveler & Unlikely Ally",
        "desc": "A 21st-century US Marine tactical operator and anime enthusiast accidentally hurled back in time to 1863 following a catastrophic classified government wormhole experiment.",
        "members": ["Joe"],
        "philosophy": "Survival via high-speed tactical modern ninjutsu. Upon witnessing the noble duty of the Iga clan, he swore to stand beside them with his faithful war hound Yamato."
    }
]

CONTROLS_EN = {
    "title": "BASIC CONTROLS & DUEL SYSTEM",
    "desc": (
        "Samurai Edge employs an isometric diegetic combat system inspired by the timeless cinema of Akira Kurosawa "
        "and the uncompromising surgical precision of Bushido Blade. Every slash carries lethal consequence and rigorous 3D spatial alignment."
    ),
    "table": [
        ("8-Way Movement", "D-Pad / Left Analog Stick", "[W, A, S, D] (P1) / [Arrows] (P2)", "Tactical 3D positioning and distance management across the arena floor"),
        ("Primary Attack", "Button X / Square", "[E] (P1) / [U] (P2)", "Signature weapon strike (rapid draw Battojutsu, cleave, thrust, or gunshot)"),
        ("Secondary / Special Action", "Button Y / Triangle", "[R] (P1) / [I] (P2)", "Fighter-specific special maneuver, acrobatics, projectile, or reactive parry"),
        ("Dedicated Roll / Dash", "Button B / Circle", "[T] (P1) / [O] (P2)", "High-speed evasive roll with 12 frames of invulnerability"),
        ("Universal Guard / Parry", "Button RB / R1", "[F] (P1) / [I] (P2)", "Defensive stance with active parry deflection window against enemy slashes"),
        ("Pause / Ceremonial Menu", "Start / Options Button", "[ESC]", "Parchment Sumi-E menu pause and real-time moveset inspection")
    ],
    "mechanics": [
        ("Blade Clash QTE", "When two symmetric slashes connect within the exact same spatial frame, the duel freezes for 600ms amidst blinding sparks. The duelist who mashes the primary attack button faster overpowers the lock, staggering their foe with 24 frames of off-balance stun."),
        ("Absolute Precedence", "Certain attacks (such as Murasaki's Kusarigama scythe sweep and Hendrika's piercing corrosive rapier) possess hardcoded mathematical priority, cleanly cutting through clashes and interrupting ordinary slashes."),
        ("Guard Crush", "Heavy blank artillery discharges (Teppo), spiked iron club smashes (Benkei), and alchemical acid thrusts (Hendrika) shatter active parry stances, inflicting heavy daze upon defending opponents."),
        ("Surgical Lethality (1 to 3 HP)", "Almost all fighters possess 2 Hit Points (with the sole exceptions of Musashi and Raiden, who possess 3 HP). A single clean counter-hit delivered during an enemy's whiffed recovery decides the duel instantly.")
    ]
}

MODES_EN = {
    "title": "COMBAT MODES & PROGRESSION",
    "arcade_title": "ARCADE MODE — THE 12-FIGHT GAUNTLET",
    "arcade_desc": (
        "The definitive solo campaign. The player selects their warrior and journeys through an escalating ladder of 12 ritual duels "
        "where spilled blood resonates across the four islands of Japan, systematically destabilizing the sacred seal of the Shadow Cave:"
    ),
    "arcade_stages": [
        ("Act I: Ranked Duels 1 to 4", "Classic Best-of-3 (BO3) duels against introductory challengers drawn democratically across initial roster tiers."),
        ("Act II: Trial of the Masters 5 to 8", "High-tension tactical encounters against veteran masters, archers, and exotic weapon specialists across treacherous battlefields."),
        ("Act III: The Mirror Duel (Fight 9)", "The warrior faces their own spectral shadow within their home arena. A battle of nerves and pure technique under identical weapon parameters."),
        ("Act IV: Endurance Gauntlet (Fight 10)", "Two elite adversaries in unbroken succession, sharing the player's round life pool. Demands strict spatial awareness and poise."),
        ("Act V: The Shadow Gate (Fight 11)", "Entering the subterranean depths of Mount Suzuka. The player must defeat the Iga Guardian phalanx (Joe, Kasumi, Murasaki, Hanzo, and Chiyo) under toxic fumes."),
        ("Epilogue: The Titan Awakens (Fight 12)", "With the guardians fallen, the ancient seal shatters. The towering Oni Gashadokuro rises from the cavern floor in a monumental 1-round survival clash.")
    ],
    "versus_title": "LOCAL VERSUS & AI SKIRMISH",
    "versus_desc": (
        "Head-to-head combat for 2 local players or player vs Artificial Intelligence. Features unrestricted selection "
        "across all 24 warriors, 24 thematic arenas, round configuration (1 to 5), and 3 selectable AI difficulty tiers (Easy, Normal, Hard)."
    )
}

BOSS_TEASER_EN = {
    "title": "THE FORBIDDEN AWAKENING — FINAL BOSS",
    "name": "ONI GASHADOKURO (鬼鵺・餓者髑髏)",
    "subtitle": "The Skeletal Titan Forged from the Malice of Ten Thousand Unburied Souls",
    "concept_art": "assets/concepts/gashadokuro_silhouette_tease.jpg",
    "lore": (
        "Within the unfathomable depths of the Shadow Cave in Iga, beyond forgotten altars and sacred Shimenawa talismans, "
        "slumbers feudal Japan's most horrifying secret. The Gashadokuro is no mere demon: it is a primeval cataclysm, "
        "a towering colossus formed from the fused bones of all warriors, peasants, and innocents slaughtered in wars from the Sengoku era "
        "to the twilight of the Bakumatsu. "
        "\n\nThe Iga Guardians (Hanzo, Kasumi, Murasaki, Chiyo, and Joe) dedicated their lives to turning back every intruder "
        "to keep the ground calm. But when the twelve duels of the Arcade ladder culminate and the spilled blood of elite champions "
        "seeps into the bedrock, the mystical seals rupture with a thunderous roar. "
        "A pair of burning crimson eyes ignites in the dark, and a massive skeletal hand armed with iron claws rises from the earth "
        "to purge the realm of the living."
    ),
    "warning_title": "FINAL BATTLE TACTICAL WARNINGS",
    "warning_points": [
        ("Unshakable Mass (Hyper-Armor)", "The Oni Gashadokuro completely ignores recoil from standard weapon strikes. Never attempt to trade frontal attacks."),
        ("Seismic Ground Slams & Titan Fist", "Its vertical fists shatter the cavern floor, raining razor-sharp stalactites across the entire stage."),
        ("Spectral Fatigue Window", "Following a three-hit devastating combo, the Titan collapses momentarily in supernatural exhaustion. This is your sole opening to deliver amplified clean cuts."),
        ("Single-Round Sudden Death", "There are no second chances against the Gashadokuro. A single positioning misstep results in immediate annihilation.")
    ]
}

APPENDIX_EN = {
    "title": "TECHNICAL APPENDIX & COMBAT DIRECTIVES",
    "tier_title": "OVERALL PERFORMANCE TABLE & WINRATES (6,624 SIMULATED COMBATS)",
    "tier_desc": (
        "Data compiled from official automated tournament simulations under symmetric arena rotations "
        "(Sacred Dohyo, Iga Rooftops, Ganryu Island, and Burning Kyoto) against NORMAL level AI:"
    ),
    "tier_table": [
        ("1", "Seimei", "Talisman Onmyoji (Ofuda / Pentagram Rondel)", "125", "51", "67.9%", "Tier S"),
        ("2", "Teppo", "Gunpowder Marksman (Tanegashima / Bayonet)", "116", "66", "63.0%", "Tier S"),
        ("3", "Hanzo", "Iga Shinobi Grandmaster (Kunai / Tactical Draw)", "115", "69", "62.5%", "Tier S"),
        ("4", "Saitou", "Wolf of Mibu (Shinsengumi / Gatotsu)", "115", "68", "62.5%", "Tier S"),
        ("5", "Hendrika", "Dejima Alchemist (Rapier / 5 Chemical Flasks)", "109", "74", "59.2%", "Tier S"),
        ("6", "Joe", "Tactical American Ninja (Shuriken / Rifle / Doberman)", "108", "76", "58.7%", "Tier S"),
        ("7", "Kenshi", "Twilight Battosai (Hiten Iaijutsu / Shukuchi)", "107", "76", "58.1%", "Tier S"),
        ("8", "Tomoe", "Sacred Miko Archer (Longbow Yumi / Spirit Arrow)", "107", "77", "58.1%", "Tier S"),
        ("9", "Murasaki", "Shadow Kunoichi (Venomous Kusarigama)", "93", "90", "50.5%", "Tier B"),
        ("10", "Valerius", "Prussian Necromancer (Zweihänder / Dark Flames)", "93", "91", "50.5%", "Tier B"),
        ("11", "Ichi", "Blind Blade (Shikomizue / Reverse Gyaku-Iai)", "92", "90", "50.0%", "Tier B"),
        ("12", "Musashi", "Dual Blade Kensei (Niten Ichi-ryu / Twin Blades)", "87", "96", "47.3%", "Tier B"),
        ("13", "Kasumi", "Mist Kunoichi (Ninja-to / Smoke Bombs)", "87", "96", "47.3%", "Tier B"),
        ("14", "Aoi", "Wild Ainu Huntress (Horn Bow / Nordic Makiri)", "87", "97", "47.3%", "Tier B"),
        ("15", "Chiyo", "Blade Dancer (Dual Higanbana Kodachi Whirlwind)", "82", "102", "44.6%", "Tier C"),
        ("16", "Daiki", "Bo Staff Pilgrim (Oak Bo / Pole Vault)", "81", "103", "44.0%", "Tier C"),
        ("17", "Goro", "Rebel Farmer (Kuwa Mattock / Seismic Stomp)", "80", "103", "43.5%", "Tier C"),
        ("18", "Anne", "Corsair Captain (180° Cutlass / Flintlock Pistol)", "78", "105", "42.4%", "Tier C"),
        ("19", "Julie", "Royal Musketeer (French Rapier / Precise Riposte)", "77", "107", "41.9%", "Tier D"),
        ("20", "Ren", "Shaolin Fist Monk (Iron Palm / Flurry Kick)", "76", "107", "41.3%", "Tier D"),
        ("21", "O-Rin", "Yoshiwara Minstrel (Razor Shamisen / Concealed Dagger)", "74", "105", "40.2%", "Tier D"),
        ("22", "Okuni", "Kabuki Priestess (Iron Tessen Fan / Miasma)", "70", "113", "38.0%", "Tier D"),
        ("23", "Raiden", "Undefeated Yokozuna (Heavy Tsuppari / Tachiai Charge)", "68", "111", "37.0%", "Tier D"),
        ("24", "Benkei", "Sohei Warrior Monk (Iron Kanabo / Colossal Naginata)", "64", "118", "34.8%", "Tier D")
    ],
    "soil_table_title": "SOIL REAGENTS & CLANDESTINE ALCHEMY DIRECTIVE (HENDRIKA & SEIMEI)",
    "soil_table": [
        ("Dejima Warehouse / Harbors", "Pure Sulfur, Fine Saltpeter, Acid Residues", "Acid Flask (Guard Crush) & Alchemical Fire", "+30% flask gathering speed"),
        ("Burning Kyoto / City Streets", "Fresh Blood, Fire Soot, Black Powder", "Lethal Venom Brew & Incendiary Grenade", "Resistance to ticking fire damage"),
        ("Forests / Red Pines / Taiga", "Medicinal Roots, Pine Sap, Natural Resin", "HP Restoration Elixir & Max Stamina Tonic", "Faster roll recovery frames"),
        ("Graveyards / Shadow Cave", "Corpse Dust, Fungal Miasma, Dark Ash", "Blinding Smokescreen & Paralytic Neurotoxin", "Slows enemy movement speed"),
        ("Shrines / Sacred Dohyo", "Consecrated Salt, Camphor, Star Sand", "Iron Armor Potion & Focus Elixir", "Cancels active venom and bleeding"),
        ("Asuka Plains / Rice Fields", "Fine Clay, Spring Water, Bamboo Shoots", "Fortifying Balm & Camouflage Mist", "Boosts dash lunging distance"),
        ("Silesian Crypts / Enclave", "Molten Silver, Flint Oil, Crude Saltpeter", "Purifying Flame Flask & Royal Acid", "Amplifies counter-hit stun duration")
    ],
    "credits_title": "CREDITS & CONTRIBUTORS",
    "credits": [
        ("Game Designer, Songwriter & Artist", "Colletes"),
        ("Development Toolset", "Gemini / Antigravity, Suno, Google Flow"),
        ("Dedication", "To Lorena. Always to Lorena, who supports me in my madness.")
    ],
    "dedication_production": "Inspired by the great masterworks and manga of Feudal Japan."
}
