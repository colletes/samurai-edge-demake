"""
Módulo do Sistema Completo de Ajuda e Guia Estratégico (Game Help & Strategy Manual).
Implementa Internacionalização (i18n) no padrão Boardbots (PT/EN),
resolução de overflow com rolagem suave / filtro de seções,
e manual detalhado dos 12 combatentes.
"""
import math
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, COLOR_WHITE, COLOR_BG,
    COLOR_RED_AURA, COLOR_BLUE_AURA, COLOR_YELLOW_AURA, COLOR_STEEL,
    COLOR_SAITOU_LIGHT_BLUE, COLOR_PURPLE_AURA, COLOR_PIRATE_AURA,
    COLOR_MUSKETEER_AURA, COLOR_REN_AURA, COLOR_CHIYO_AURA, COLOR_BENKEI_AURA, COLOR_ORIN_AURA,
    COLOR_GORO_AURA, COLOR_ICHI_AURA, COLOR_VALERIUS_AURA, COLOR_SEIMEI_AURA, COLOR_BOSS_AURA,
    COLOR_DAIKI_AURA, COLOR_AOI_AURA, COLOR_RAIDEN_AURA, COLOR_HENDRIKA_AURA,
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA,
    CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE, CHAR_SAITOU, CHAR_RIFLE,
    CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER,
    CHAR_REN, CHAR_CHIYO, CHAR_BENKEI, CHAR_ORIN,
    CHAR_GORO, CHAR_ICHI, CHAR_VALERIUS, CHAR_SEIMEI,
    CHAR_DAIKI, CHAR_AOI, CHAR_RAIDEN, CHAR_HENDRIKA, CHAR_BOSS
)
from src.isometric.iso_math import world_to_iso
from src.entities.voxel_models import render_voxel_humanoid, render_voxel_doberman
from src.i18n import t, get_lang, set_lang, toggle_lang, LANG_PT, LANG_EN
from src.ui.portraits import get_portrait
from src.effects import parchment as pm

class HelpPreviewCam:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
    def apply(self, wx, wy, wz=0.0):
        ix, iy = world_to_iso(wx, wy, wz)
        return int(self.cx + ix), int(self.cy + iy)

# Banco de dados bilíngue completo dos 12 guerreiros
FIGHTERS_GUIDE_DATA = [
    {
        "id": CHAR_KENSHIN,
        "color": COLOR_RED_AURA,
        "char_type": "kenshin",
        "pt": {
            "name": "KENSHI",
            "title": "A Espadachim Lendária",
            "style": "Hiten Mitsurugi-ryū (Iaijutsu)",
            "vel": "[5/5] Velocidade Máxima",
            "dano": "1-Hit Kill Instantâneo (Saque Veloz)",
            "especial": "Shukuchi (Investida Relâmpago)",
            "keys_p1": "[E] Iai Flash (Ataque)",
            "keys_p2": "[R] Shukuchi Dash (Especial)",
            "conceito": (
                "Inspirada nos mestres de Battojutsu do Bakumatsu. Kenshi é uma duelista purista "
                "que aposta tudo na velocidade suprema do saque da espada diretamente da bainha. "
                "Seu combate é baseado na antecipação fulminante e na leitura precisa do adversário."
            ),
            "habilidades": (
                "• Iai Flash [E]: Saque frontal em altíssima velocidade. 1-Hit Kill letal que corta até bambus.\n"
                "• Shukuchi [R]: Movimento quase instantâneo que deixa pós-imagens (zanzou) no ar."
            ),
            "estrategia_ofensiva": (
                "• Use o Shukuchi para fechar distância no exato instante em que o rival errar um golpe.\n"
                "• Seu Iai Flash tem alcance frontal respeitável e mata na hora; posicione-se em linha reta.\n"
                "• Corte bambus do cenário durante o ataque para criar clareiras de emboscada."
            ),
            "estrategia_defensiva": (
                "• Como vencer Kenshi: Imediatamente após o Iai Flash, Kenshi entra na animação de Noto "
                "(embainhar a lâmina), ficando 100% indefesa por uma fração de segundo. Se ela errar (whiff), "
                "ataque imediatamente! Mantenha obstáculos como rochas entre você e ela para impedir o Iai direto."
            )
        },
        "en": {
            "name": "KENSHI",
            "title": "The Legendary Swordswoman",
            "style": "Hiten Mitsurugi-ryū (Iaijutsu)",
            "vel": "[5/5] Maximum Speed",
            "dano": "Instant 1-Hit Kill (Flash Draw)",
            "especial": "Shukuchi (Lightning Dash)",
            "keys_p1": "[E] Iai Flash (Attack)",
            "keys_p2": "[R] Shukuchi Dash (Special)",
            "conceito": (
                "Inspired by Bakumatsu Battojutsu masters. Kenshi is a purist duelist betting everything "
                "on supreme quick-draw speed straight from the scabbard. Her style relies on lightning "
                "anticipation and flawless spatial reading of her opponent."
            ),
            "habilidades": (
                "• Iai Flash [E]: Lightning forward draw. Instant 1-Hit Kill that even cuts bamboo stalks.\n"
                "• Shukuchi [R]: Near-instantaneous movement leaving after-images (zanzou) behind."
            ),
            "estrategia_ofensiva": (
                "• Use Shukuchi to close the gap the moment your rival whiffs a heavy strike.\n"
                "• Iai Flash has great straight-line priority and kills instantly; align your spacing.\n"
                "• Cut bamboo groves during your charge to clear ambush routes and open angles."
            ),
            "estrategia_defensiva": (
                "• How to defeat Kenshi: Immediately after Iai Flash, Kenshi enters the Noto (resheathing) "
                "recovery, leaving her 100% defenseless for a split second. If she whiffs, strike instantly! "
                "Keep solid obstacles like rocks between you and her direct charge line."
            )
        }
    },
    {
        "id": CHAR_MUSASHI,
        "color": COLOR_BLUE_AURA,
        "char_type": "musashi",
        "pt": {
            "name": "MUSASHI",
            "title": "O Santo da Espada",
            "style": "Hyoho Niten Ichi-ryū (Duas Lâminas)",
            "vel": "[2/5] Firme e Pesado",
            "dano": "Combo Niten 3 Cortes (3 HP Resiliente)",
            "especial": "Cross Guard Parry & Cross Shockwave",
            "keys_p1": "[E] Combo de Lâminas (Ataque)",
            "keys_p2": "[R] Cross Guard / Shockwave",
            "conceito": (
                "O maior duelista da história do Japão, empunhando a Katana longa e a Wakizashi curta ao mesmo "
                "tempo sem nunca embainhar durante o combate. Musashi personifica a serenidade tática, a resistência física "
                "e o contra-ataque devastador."
            ),
            "habilidades": (
                "• Combo 3-Cortes [E]: Sequência ritmada de Katana descendente, Wakizashi ascendente e clivagem dupla em X com avanço e onda cortante.\n"
                "• Cross Guard Parry [R]: Ergue ambas as lâminas cruzadas em X (0.28s de reflexão frontal). Se defletir um golpe, libera o punitivo Cross Shockwave.\n"
                "• Rolamento Tático [Espaço]: Esquiva fluida de ombro no solo sem zanzou, cancelável aos 40% finais em lunge de ataque instantâneo.\n"
                "• Finalizações: Niten Ichi-ryu (Empalamento sequencial e rasgo em 3 partes) e Cross Vacuum Slicer (Corte em X em 4 partes)."
            ),
            "estrategia_ofensiva": (
                "• Encadeie os golpes no ritmo exato para manter a pressão; o terceiro golpe projeta um lunge vigoroso acompanhado de onda de vácuo.\n"
                "• Use o Rolamento Tático para fechar distância e aperte Ataque nos últimos 40% da esquiva para cancelar imediatamente no golpe corrido.\n"
                "• Defletir com o Cross Guard permite contra-atacar imediatamente com o devastador Cross Shockwave à queima-roupa."
            ),
            "estrategia_defensiva": (
                "• Como vencer Musashi: O Cross Guard só deflete ataques frontais! Flanqueie-o pelas diagonais "
                "ou ataque-o pelas costas enquanto ele se recupera. Bombas e armadilhas no solo ignoram o bloqueio."
            )
        },
        "en": {
            "name": "MUSASHI",
            "title": "The Sword Saint",
            "style": "Hyoho Niten Ichi-ryū (Two Swords)",
            "vel": "[2/5] Resilient & Heavy",
            "dano": "3-Slash Niten Combo (3 HP Tough)",
            "especial": "Cross Guard Parry & Cross Shockwave",
            "keys_p1": "[E] Blade Combo (Attack)",
            "keys_p2": "[R] Cross Guard / Shockwave",
            "conceito": (
                "Japan's legendary duel master, wielding both Katana and Wakizashi simultaneously without "
                "ever re-sheathing during combat. Musashi embodies disciplined patience, rugged physical resilience, "
                "and crushing counter-attacks."
            ),
            "habilidades": (
                "• 3-Slash Combo [E]: Rhythmic descending Katana, rising Wakizashi, and double X-cleave with forward lunge and vacuum wave.\n"
                "• Cross Guard Parry [R]: Crosses dual blades frontally (0.28s reflection window). Deflecting an attack arms the punishing Cross Shockwave.\n"
                "• Tactical Roll [Space]: Ground shoulder roll without zanzou, cancellable in the last 40% into an instant running strike.\n"
                "• Finishers: Niten Ichi-ryu (Sequential dual impale tearing torso into 3) and Cross Vacuum Slicer (X-wave dividing into 4 quadrants)."
            ),
            "estrategia_ofensiva": (
                "• Time your combo strikes rhythmically to sustain offensive pressure; the 3rd slash unleashes a forward lunge and cutting wave.\n"
                "• Use the Tactical Roll to close distance, cancelling with Attack during the final 40% for an instant surprise lunging cut.\n"
                "• Deflecting with Cross Guard allows an immediate lethal Cross Shockwave counter at point-blank range."
            ),
            "estrategia_defensiva": (
                "• How to defeat Musashi: The Cross Guard only deflects frontal attacks! Flank him diagonally or "
                "strike his back while he recovers. Ground bombs and traps bypass his guard."
            )
        }
    },
    {
        "id": CHAR_NINJA,
        "color": COLOR_YELLOW_AURA,
        "char_type": "yellow_ninja",
        "pt": {
            "name": "HANZO",
            "title": "Ninja Mestre de Iga",
            "style": "Iga Ninjutsu & Kunai",
            "vel": "[5/5] Extrema Agilidade",
            "dano": "Ninjato Invertida (2 Tempos) / Kunai Snipe",
            "especial": "Salto Ninja Parabólico (Landing Cancel)",
            "keys_p1": "[E] Ninjato Combo | [R] Kunai Snipe",
            "keys_p2": "[Space/Roll] Salto Acrobático",
            "conceito": (
                "Shinobi lendário das sombras feudais de Iga. Mestre em combate letal de curta distância "
                "com Ninjato empunhada de modo invertido (Reverse Grip) e arremessos precisos de Kunai. "
                "Possui salto acrobático parabólico que passa por cima de golpes baixos e permite cancelamento "
                "ofensivo veloz na aterrissagem (Landing Strike Lunge)."
            ),
            "habilidades": (
                "• Ninjato 2-Golpes [E]: Combo de 2 tempos com corte reverso horizontal e estocada penetrante no plexo solar com avanço.\n"
                "• Kunai Snipe [R]: Disparo de kunai a 24 m/s em trajetória horizontal no solo ou mergulho descendente íngreme no ar.\n"
                "• Salto Ninja [Space/Roll]: Salto parabólico evasivo (wz até 1.35m) sem zanzou. Nos 40% finais da aterrissagem, pressionar ataque cancela o lag em estocada imediata!"
            ),
            "estrategia_ofensiva": (
                "• Salte sobre ataques terrestres previsíveis e dispare a Kunai do ar para punir o oponente em ângulo descendente.\n"
                "• Use o Landing Cancel para surpreender o rival imediatamente ao tocar o chão com uma estocada profunda de 2 de dano.\n"
                "• O golpe Melee de Ninjato sempre está pronto e possui recuo rápido, permitindo encadear combos com alta pressão."
            ),
            "estrategia_defensiva": (
                "• Como vencer Hanzo: Se Hanzo atacar durante o salto aéreo, execute um Parry certeiro — Hanzo cairá imediatamente no solo atordoado, anulando qualquer flutuação aérea."
            )
        },
        "en": {
            "name": "HANZO",
            "title": "Iga Master Shinobi",
            "style": "Iga Ninjutsu & Reverse Ninjato",
            "vel": "[5/5] Extreme Agility",
            "dano": "Reverse Ninjato (2-Step) / Kunai Snipe",
            "especial": "Acrobatic Shinobi Jump (Landing Cancel)",
            "keys_p1": "[E] Ninjato Combo | [R] Kunai Snipe",
            "keys_p2": "[Space/Roll] Shinobi Jump",
            "conceito": (
                "Legendary shinobi of the Iga clan. Master of close-quarters assassination with "
                "a reverse-grip Ninjato short sword and high-velocity Kunai snipes. "
                "Features parabolic acrobatic evasion vaulting over ground slashes with instant "
                "offensive cancel upon landing (Landing Strike Lunge)."
            ),
            "habilidades": (
                "• Ninjato 2-Step [E]: Agile 2-hit combo: horizontal reverse slash followed by a deep solar plexus thrust.\n"
                "• Kunai Snipe [R]: High-speed 24 m/s throw traveling horizontally on ground or diving steeply downward from mid-air.\n"
                "• Shinobi Jump [Space/Roll]: High evasive vault (wz up to 1.35m). During the final 40% of landing, pressing attack cancels recovery into an immediate forward strike!"
            ),
            "estrategia_ofensiva": (
                "• Vault over low horizontal slashes and snipe downward from above with steep Kunai trajectory.\n"
                "• Use Landing Cancel to close distance instantly as your boots touch down, dealing 2 fatal damage.\n"
                "• Your reverse-grip Ninjato is always drawn for melee without needing to retrieve or discard weapons."
            ),
            "estrategia_defensiva": (
                "• How to defeat Hanzo: If Hanzo strikes while airborne, time your Parry cleanly — he will immediately plummet to the earth stunned, completely canceling any mid-air floating."
            )
        }
    },
    {
        "id": CHAR_AMERICAN,
        "color": (255, 130, 45),
        "char_type": "american_ninja",
        "pt": {
            "name": "JOE",
            "title": "American Ninja",
            "style": "Combate Tático com Doberman",
            "vel": "[4/5] Rápido e Tático",
            "dano": "Shuriken de Metal (Stun)",
            "especial": "Ataque do Cão Doberman (1-Hit Kill)",
            "keys_p1": "[E] Shuriken (Ataque)",
            "keys_p2": "[R] Cão Dash (Especial)",
            "conceito": (
                "Operativo tático ocidental treinado nas artes secretas do Ninjutsu, acompanhado por seu leal "
                "cão de combate Doberman. Sua doutrina se baseia no ataque em pinça e na distração estratégica."
            ),
            "habilidades": (
                "• Shuriken [E]: Estrela de metal veloz a 15.5 m/s (cooldown ágil 0.45s); inflige micro-stun e quebra golpes.\n"
                "• Yamato Dash [R]: O leal Doberman Yamato dispara a 18.5 m/s com teleguiamento predatório e mordida fatal de 1-Hit Kill.\n"
                "• Flic-Flac [Espaço]: Salto acrobático 360° para frente, encadeável continuamente com extrema agilidade."
            ),
            "estrategia_ofensiva": (
                "• A estratégia de pinça tática: dispare a Shuriken a curta ou média distância para cancelar ataques rivais com micro-stun.\n"
                "• Com o oponente atordoado, comande o bote predatório de Yamato [R] para finalizar a luta!\n"
                "• Use o Flic-Flac contínuo na direção desejada para atravessar o combate e flanquear o inimigo."
            ),
            "estrategia_defensiva": (
                "• Como vencer Joe: Yamato tem velocidade extrema (18.5 m/s) mas ainda pode ser aparado com Parry (atordoando o cão por 2.0s). "
                "Cuidado ao pressionar Joe contra rochas e paredes: bater em obstáculos sólidos durante o flic-flac o atordoa por 0.60s!"
            )
        },
        "en": {
            "name": "JOE",
            "title": "American Ninja",
            "style": "Tactical Combat & Doberman",
            "vel": "[5/5] Tactical & Agile",
            "dano": "Metal Shuriken (Micro-Stun)",
            "especial": "Doberman Attack (1-Hit Kill)",
            "keys_p1": "[E] Shuriken (Attack)",
            "keys_p2": "[R] Dog Dash (Special)",
            "conceito": (
                "Western tactical operative trained in secret ninjutsu arts, fighting alongside his trained "
                "combat Doberman Yamato. Specializes in pincer maneuvers, forward acrobatic rolls, and rapid zoning."
            ),
            "habilidades": (
                "• Shuriken [E]: Rapid 15.5 m/s throwing star with 0.45s cooldown; cancels enemy startup attacks with micro-stun.\n"
                "• Yamato Dash [R]: Loyal combat Doberman sprints at 18.5 m/s with predatory homing steering for a lethal 1-Hit Kill.\n"
                "• Flic-Flac [Space]: Forward 360° somersault handspring chainable continuously with high agility."
            ),
            "estrategia_ofensiva": (
                "• Tactical pincer maneuver: throw rapid Shurikens to freeze and interrupt the rival with micro-stun.\n"
                "• While the enemy flinches, command Yamato's [R] homing charge to close the distance and strike!\n"
                "• Use chained Flic-Flacs in any direction to outmaneuver opponents."
            ),
            "estrategia_defensiva": (
                "• How to defeat Joe: Yamato is faster than ever (18.5 m/s) but can still be parried, stunning the dog for 2.0s. "
                "Cornering Joe near solid obstacles (rocks, walls) can cause his flic-flac to crash, stunning him for 0.60s!"
            )
        }
    },
    {
        "id": CHAR_SAITOU,
        "color": COLOR_SAITOU_LIGHT_BLUE,
        "char_type": "saitou",
        "pt": {
            "name": "SAITOU",
            "title": "O Lobo de Mibu",
            "style": "Shinsengumi (Gatotsu Ishiki)",
            "vel": "[5/5] Impulso Explosivo",
            "dano": "Estocada Letal Acelerada (1-Hit)",
            "especial": "Zeroshiki (Gatotsu Queima-Roupa / Chip Damage)",
            "keys_p1": "[E] Gatotsu Ishiki (Ataque)",
            "keys_p2": "[R] Zeroshiki (Especial)",
            "conceito": (
                "Capitão da 3ª Divisão do Shinsengumi, frio, impiedoso e guiado pelo lema Aku Soku Zan (Corte o Mal Imediatamente). "
                "Sua postura única com a mão esquerda gera a mais temida e penetrante estocada da era feudal: o Gatotsu."
            ),
            "habilidades": (
                "• Gatotsu Ishiki [E]: Carga frontal acelerada (5.2 -> 14.5 m/s) com alta prioridade frontal. Cancelável em Haori Sidestep nos primeiros 50%.\n"
                "• Zeroshiki [R]: Explosão de queima-roupa com 1 de Dano Garantido (Chip Damage através do Parry inimigo).\n"
                "• Haori Sidestep [Espaço]: Esquiva tática ágil com 14 frames de invencibilidade."
            ),
            "estrategia_ofensiva": (
                "• O Gatotsu Ishiki acelera até 14.5 m/s com prioridade frontal absoluta contra ataques convencionais.\n"
                "• Se o oponente antecipar o golpe ou armar defesa, cancele a corrida em Haori Sidestep nos primeiros 50% para flanqueá-lo.\n"
                "• Contra defensores passivos em Parry, aperte [R] no corpo a corpo: o Zeroshiki perfura o Parry causando 1 de dano garantido!"
            ),
            "estrategia_defensiva": (
                "• Como vencer Saitou: O Gatotsu ricocheteia com faíscas se colidir com rochas, poço ou árvores! "
                "Lute perto de obstáculos e desvie lateralmente na hora em que ele acelerar. Cuidado com o Zeroshiki a queima-roupa."
            )
        },
        "en": {
            "name": "SAITOU",
            "title": "The Wolf of Mibu",
            "style": "Shinsengumi (Gatotsu Ishiki)",
            "vel": "[5/5] Explosive Lunge",
            "dano": "Accelerated Lethal Thrust (1-Hit)",
            "especial": "Zeroshiki (Point-Blank Thrust / Chip Damage)",
            "keys_p1": "[E] Gatotsu Ishiki (Attack)",
            "keys_p2": "[R] Zeroshiki (Special)",
            "conceito": (
                "Feared Shinsengumi 3rd Division Captain, cold, merciless, living by Aku Soku Zan (Slay Evil Immediately). "
                "His left-handed stance yields the deadliest thrust in feudal history."
            ),
            "habilidades": (
                "• Gatotsu Ishiki [E]: Devastating accelerated charge (5.2 -> 14.5 m/s) with frontal priority; cancelable into Haori Sidestep in first 50%.\n"
                "• Zeroshiki [R]: Explosive point-blank thrust guaranteeing 1 Chip Damage even through the opponent's Parry.\n"
                "• Haori Sidestep [Space]: Swift tactical evasion with 14 invulnerability frames."
            ),
            "estrategia_ofensiva": (
                "• Gatotsu accelerates up to 14.5 m/s with overwhelming forward priority against regular strikes.\n"
                "• If the rival expects the thrust, cancel the charge into Haori Sidestep in the first 50% to flank them.\n"
                "• Against parry turtles, strike with Zeroshiki [R] at point-blank range to pierce the parry for guaranteed 1 chip damage!"
            ),
            "estrategia_defensiva": (
                "• How to defeat Saitou: Gatotsu bounces off solid terrain (rocks, well, trees) with heavy recoil! "
                "Stay near obstacles and dodge sideways as he sprints. Never hold parry close to him: Zeroshiki pierces guard for 1 damage."
            )
        }
    },
    {
        "id": CHAR_RIFLE,
        "color": (225, 170, 100),
        "char_type": "rifleman",
        "pt": {
            "name": "TEPPO",
            "title": "Marksman do Arcabuz Feudal",
            "style": "Tanegashima (Balística Feudal)",
            "vel": "[3/5] Cadência & Pólvora",
            "dano": "Tiro Fatal (1-Hit) / Coronhada Stun",
            "especial": "Salto Evasivo com Fumaça / Recarga",
            "keys_p1": "[E] Disparo / Coronhada (Ataque)",
            "keys_p2": "[R] Salto Evasivo (Especial)",
            "conceito": (
                "Soldado ashigaru especialista na introdução das armas de fogo no Japão feudal (Batalha de Nagashino). "
                "Empunha um pesado arcabuz Tanegashima capaz de matar qualquer samurai com um único projétil fatal."
            ),
            "habilidades": (
                "• Disparo de Arcabuz [E]: Tiro de longa distância devastador (1-Hit Kill). Se descarregado, aplica Coronhada.\n"
                "• Coronhada de Madeira [E]: Golpe tático com a coronha do rifle que atordoa e afasta o adversário.\n"
                "• Salto Evasivo [R]: Salto acrobático para trás soltando fumaça, ótimo para escapar de cortes."
            ),
            "estrategia_ofensiva": (
                "• ATENÇÃO: Teppo começa a luta DESMUNICIADO! Sua missão número 1 é correr até a PÓLVORA!\n"
                "• Siga a SETA DOURADA FLUTUANTE e a BÚSSOLA no topo da tela para achar o Barril de Pólvora.\n"
                "• Ao coletar a pólvora, mantenha a distância, alinhe a mira e dispare com [E] para a vitória imediata.\n"
                "• Se o rival te encurralar antes de recarregar, dê a Coronhada [E] para atordoá-lo e use o Salto [R]."
            ),
            "estrategia_defensiva": (
                "• Como vencer Teppo: Não o deixe chegar nos barris de pólvora! Pressione-o desde o segundo zero. "
                "Se ele já estiver carregado, use bambus ou a esquiva no instante da fumaça do disparo."
            )
        },
        "en": {
            "name": "TEPPO",
            "title": "Tanegashima Marksman",
            "style": "Feudal Ballistics & Gunpowder",
            "vel": "[3/5] Cadence & Powder",
            "dano": "Fatal Shot (1-Hit) / Butt Stun",
            "especial": "Evasive Backstep / Reload",
            "keys_p1": "[E] Shoot / Rifle Butt (Attack)",
            "keys_p2": "[R] Evasive Backstep (Special)",
            "conceito": (
                "Ashigaru marksman pioneering gunpowder warfare in feudal Japan (Battle of Nagashino). "
                "Wields a heavy matchlock Tanegashima arcabuz capable of dropping any samurai with a single bullet."
            ),
            "habilidades": (
                "• Arcabuz Shot [E]: Long-range devastating 1-Hit Kill shot. If unloaded, delivers a wooden Rifle Butt strike.\n"
                "• Rifle Butt [E]: Tactical melee strike with the musket stock that stuns and knocks back.\n"
                "• Evasive Backstep [R]: Backwards leap releasing smoke, great for evading incoming sword slashes."
            ),
            "estrategia_ofensiva": (
                "• WARNING: Teppo starts each round UNLOADED! Your #1 priority is running to the GUNPOWDER KEG!\n"
                "• Follow the FLOATING GOLDEN ARROW and the HUD COMPASS at the top to reach the Gunpowder Keg.\n"
                "• Once loaded, keep distance, align your sights, and fire [E] for an instant kill.\n"
                "• If crowded before loading, strike with Rifle Butt [E] to stun, then use Evasive Backstep [R]."
            ),
            "estrategia_defensiva": (
                "• How to defeat Teppo: Never let him reach the gunpowder kegs! Rush him down from second zero. "
                "If he is already loaded, utilize bamboo for cover and evade when you see matchlock smoke."
            )
        }
    },
    {
        "id": CHAR_PURPLE,
        "color": COLOR_PURPLE_AURA,
        "char_type": "murasaki",
        "pt": {
            "name": "MURASAKI",
            "title": "Kunoichi da Foice",
            "style": "Kusarigamajutsu (Foice & Corrente)",
            "vel": "[4/5] Ágil e Flexível",
            "dano": "Corte com Precedência Absoluta",
            "especial": "Puxão de Corrente à Distância",
            "keys_p1": "[E] Corte de Foice (Ataque)",
            "keys_p2": "[R] Puxar Corrente (Especial)",
            "conceito": (
                "Assassina acrobática que domina a Kusarigama: foice de colheita atrelada a uma longa corrente de aço "
                "com peso de chumbo. Sua arte quebra a distância convencional e dita as regras do espaço."
            ),
            "habilidades": (
                "• Corte de Foice [E]: Golpe cortante dotado de Precedência Absoluta — vence qualquer golpe simultâneo!\n"
                "• Puxão de Corrente [R]: Arremessa a corrente; se atingir, laça e arrasta o oponente até seus pés."
            ),
            "estrategia_ofensiva": (
                "• A Kusarigama é a rainha do controle de zona: lance a corrente com [R] para fisgar o inimigo de longe.\n"
                "• Ao puxar o oponente para perto, desabafe com a Foice [E]. Graças à Precedência, seu golpe acerta primeiro!\n"
                "• Não tema trocar ataques ao mesmo tempo: sua foice tem prioridade no motor de combate."
            ),
            "estrategia_defensiva": (
                "• Como vencer Murasaki: A corrente tem tempo de arremesso e retorno. Se ela errar o puxão, "
                "avance diagonalmente na recuperação dela. Evite trocar ataques retos ao mesmo tempo contra a foice."
            )
        },
        "en": {
            "name": "MURASAKI",
            "title": "Sickle Kunoichi",
            "style": "Kusarigamajutsu (Chain & Sickle)",
            "vel": "[4/5] Agile & Flexible",
            "dano": "Absolute Precedence Slash",
            "especial": "Ranged Chain Snare & Reel",
            "keys_p1": "[E] Sickle Slash (Attack)",
            "keys_p2": "[R] Chain Pull (Special)",
            "conceito": (
                "Graceful acrobat wielding the Kusarigama: a harvesting kama sickle linked to a heavy steel "
                "chain and iron weight. Dictates space and shatters conventional engagement ranges."
            ),
            "habilidades": (
                "• Sickle Slash [E]: Lethal strike with Absolute Precedence — beats any simultaneous normal attack!\n"
                "• Chain Pull [R]: Flings the chain forward; on hit, snares and pulls the foe directly to your feet."
            ),
            "estrategia_ofensiva": (
                "• Master of zone control: toss your chain with [R] to hook the enemy from afar.\n"
                "• As they are reeled in, strike with the Sickle [E]. Precedence guarantees you land the fatal hit first!\n"
                "• Never hesitate in simultaneous trades: your sickle wins priority in the combat engine."
            ),
            "estrategia_defensiva": (
                "• How to defeat Murasaki: The chain has throw and retract frames. If she misses the snare, "
                "rush in diagonally during recovery. Avoid direct simultaneous trades against the sickle."
            )
        }
    },
    {
        "id": CHAR_GRAY,
        "color": (165, 180, 190),
        "char_type": "kasumi",
        "pt": {
            "name": "KASUMI",
            "title": "Kunoichi da Névoa",
            "style": "Névoa, Bombas de Cerâmica & Pólvora",
            "vel": "[4/5] Ágil e Evasiva",
            "dano": "Granada Parabólica 3D (Explosão)",
            "especial": "Bomba de Fumaça (Slow + Fuga)",
            "keys_p1": "[E] Lançar Bomba (Ataque)",
            "keys_p2": "[R] Cortina de Fumaça (Especial)",
            "conceito": (
                "Sabotadora e ilusionista das sombras, mestra em misturas pirotécnicas e pós ofuscantes. "
                "Transforma a arena em um campo minado caótico de fumaça, chamas e detonações."
            ),
            "habilidades": (
                "• Bomba em Arco 3D [E]: Lança bomba de cerâmica que voa em parábola e explode em área (1-Hit Kill).\n"
                "• Cortina de Fumaça [R]: Detona fumaça espessa aos seus pés, cegando e reduzindo a velocidade do rival."
            ),
            "estrategia_ofensiva": (
                "• Lance bombas por cima de obstáculos (rochas e bambus) para atingir alvos sem linha de visão direta.\n"
                "• Solte a fumaça [R] no meio da arena ou na ponte estreita para deixar o oponente lento como tartaruga.\n"
                "• CUIDADO COM O AUTO-DANO: Não fique colado na explosão da sua própria bomba!"
            ),
            "estrategia_defensiva": (
                "• Como vencer Kasumi: Pressione-a em combate corpo a corpo colado! Se ela jogar a bomba muito perto, "
                "ela mesma será atingida pela explosão. Saia da nuvem de fumaça para recuperar sua velocidade."
            )
        },
        "en": {
            "name": "KASUMI",
            "title": "Mist Kunoichi",
            "style": "Mist, Ceramic Bombs & Gunpowder",
            "vel": "[4/5] Agile & Evasive",
            "dano": "Parabolic 3D Bomb (Explosive)",
            "especial": "Smoke Screen (Slow + Escape)",
            "keys_p1": "[E] Throw Bomb (Attack)",
            "keys_p2": "[R] Smoke Screen (Special)",
            "conceito": (
                "Shadow saboteur and illusionist, master of pyrotechnic blends and obscuring powders. "
                "Transforms the arena into a chaotic minefield of smoke, sparks, and lethal detonations."
            ),
            "habilidades": (
                "• 3D Arc Bomb [E]: Hurls a ceramic powder bomb in a parabolic arc that detonates on contact/timer (1-Hit Kill).\n"
                "• Smoke Screen [R]: Drops thick smoke at her feet, blinding and drastically slowing down the rival."
            ),
            "estrategia_ofensiva": (
                "• Lob bombs over obstacles (rocks and bamboo) to strike enemies without direct line of sight.\n"
                "• Drop smoke [R] in the arena center or bridge to slow charging foes to a crawl.\n"
                "• WATCH OUT FOR SELF-DAMAGE: Do not stand in the blast radius of your own bomb!"
            ),
            "estrategia_defensiva": (
                "• How to defeat Kasumi: Close the distance into point-blank melee! If she throws a bomb at point-blank, "
                "she will catch herself in the blast. Evade the smoke cloud to maintain mobility."
            )
        }
    },
    {
        "id": CHAR_KABUKI,
        "color": (240, 115, 30),
        "char_type": "okuni",
        "pt": {
            "name": "OKUNI",
            "title": "Mestra do Teatro Kabuki",
            "style": "Tessen-jutsu & Dança do Veneno",
            "vel": "[4/5] Acrobata Exímia",
            "dano": "Sopro de Veneno (10s Morte Certa)",
            "especial": "Kawarimi Decoy (Substituição)",
            "keys_p1": "[E] Sopro de Veneno (Ataque)",
            "keys_p2": "[R] Kawarimi Decoy (Especial)",
            "conceito": (
                "Homenagem à lendária Izumo no Okuni, fundadora do teatro Kabuki. Usa leques afiados com lâminas de ferro, "
                "pós tóxicos letais e a arte clássica da substituição por boneco de madeira (Kawarimi)."
            ),
            "habilidades": (
                "• Sopro de Veneno [E]: Lança nuvem carmesim tóxica. Inicia contagem regressiva de 10 SEGUNDOS para a MORTE!\n"
                "• Kawarimi Decoy [R]: Salto evasivo que deixa um boneco de madeira no local e absorve ataques."
            ),
            "estrategia_ofensiva": (
                "• Sua condição de vitória é única: Aproxime-se no início e acerte o Sopro de Veneno [E].\n"
                "• Uma vez que o rival esteja infectado pela contagem de 10s, SUA ÚNICA MISSÃO É SOBREVIVER!\n"
                "• Use o Kawarimi [R], pule obstáculos, corra ao redor do lago e deixe o veneno fazer o trabalho!"
            ),
            "estrategia_defensiva": (
                "• Como vencer Okuni: Se for envenenado, seu tempo está correndo! Você ganha um pequeno bônus de "
                "fúria e velocidade: vá para o tudo ou nada e mate Okuni antes dos 10 segundos acabarem!"
            )
        },
        "en": {
            "name": "OKUNI",
            "title": "Kabuki Theatre Master",
            "style": "Tessen-jutsu & Poison Dance",
            "vel": "[4/5] Master Acrobat",
            "dano": "Poison Breath (10s Fatal Death)",
            "especial": "Kawarimi Decoy (Substitution)",
            "keys_p1": "[E] Poison Breath (Attack)",
            "keys_p2": "[R] Kawarimi Decoy (Special)",
            "conceito": (
                "Homage to Izumo no Okuni, pioneer of Kabuki. Wields iron-ribbed war fans (tessen), "
                "lethal contact poisons, and the classic Kawarimi substitution technique."
            ),
            "habilidades": (
                "• Poison Breath [E]: Exhales a toxic crimson cloud. Triggers a 10-SECOND COUNTDOWN TO CERTAIN DEATH!\n"
                "• Kawarimi Decoy [R]: Evasive leap leaving a wooden log doll behind that absorbs incoming attacks."
            ),
            "estrategia_ofensiva": (
                "• Unique win condition: Close in early and land the Poison Breath [E].\n"
                "• Once your rival is infected by the 10s timer, YOUR ONLY MISSION IS SURVIVAL!\n"
                "• Use Kawarimi [R], leap over obstacles, kite around the lake, and let the poison claim victory!"
            ),
            "estrategia_defensiva": (
                "• How to defeat Okuni: If poisoned, your clock is ticking! You gain a brief fury/speed boost: "
                "go all-out and kill Okuni before the 10-second timer expires!"
            )
        }
    },
    {
        "id": CHAR_ARCHER,
        "color": (110, 195, 135),
        "char_type": "tomoe",
        "pt": {
            "name": "TOMOE",
            "title": "Arqueira Miko",
            "style": "Kyudo Sagrado & Flechas Sagradas",
            "vel": "[4/5] Ágil e Concentrada",
            "dano": "Flecha Yumi Fatal (Alcance Máximo)",
            "especial": "Chuva Sagrada (Disparo em Arco)",
            "keys_p1": "[E] Retesar e Atirar (Ataque)",
            "keys_p2": "[R] Chuva Sagrada (Especial)",
            "conceito": (
                "Sacerdotisa miko do santuário nas montanhas, mestre na arte marcial meditativa do arco e flecha (Kyudo). "
                "Sua presença transmite serenidade, foco inabalável e disparos mortais milimétricos."
            ),
            "habilidades": (
                "• Disparo Yumi [E]: Pressione para disparar uma flecha mortal de longo alcance (1-Hit Kill).\n"
                "• Chuva Sagrada [R]: Disparo em arco de várias flechas sagradas em uma pequena área com dano letal (2 HP). Segure para mirar e solte para disparar (idêntico à Anne)."
            ),
            "estrategia_ofensiva": (
                "• Mantenha a maior distância possível do inimigo; seu arco tem alcance superior a qualquer espada.\n"
                "• Retese o arco atrás de rochas e saia da cobertura apenas para desferir o disparo certeiro.\n"
                "• Se o oponente tentar avançar em linha reta, solte a flecha no caminho previsto dele."
            ),
            "estrategia_defensiva": (
                "• Como vencer Tomoe: O arco Yumi exige um breve tempo de retesamento (windup). Aproxime-se "
                "em zigue-zague usando bambus e rochas como escudo. Ela fica vulnerável enquanto prepara o tiro."
            )
        },
        "en": {
            "name": "TOMOE",
            "title": "Shrine Maiden Archer",
            "style": "Sacred Kyudo & Rope Arrow",
            "vel": "[4/5] Calm & Focused",
            "dano": "Fatal Yumi Arrow (Max Range)",
            "especial": "Rope Arrow (Zip Mobility)",
            "keys_p1": "[E] Draw & Release (Attack)",
            "keys_p2": "[R] Rope Arrow (Special)",
            "conceito": (
                "Mountain shrine maiden master of the meditative martial art of Japanese archery (Kyudo). "
                "Radiates serene focus, unshakable patience, and pinpoint lethal arrows."
            ),
            "habilidades": (
                "• Yumi Bow Shot [E]: Draw and release a lethal infinite-range arrow (1-Hit Kill). Requires windup time.\n"
                "• Rope Arrow [R]: Fires an arrow tied to hemp rope for grappling, pulling targets or quick repositioning."
            ),
            "estrategia_ofensiva": (
                "• Maintain maximum distance; your Yumi bow out-ranges any sword.\n"
                "• Draw your bow behind rocks or bamboo cover, stepping out only to loose the fatal shot.\n"
                "• If the foe charges in a straight line, release into their predicted path."
            ),
            "estrategia_defensiva": (
                "• How to defeat Tomoe: The Yumi bow requires a brief draw windup. Approach in a zig-zag pattern "
                "using bamboo and rocks as shields. She is vulnerable during her draw."
            )
        }
    },
    {
        "id": CHAR_PIRATE,
        "color": COLOR_PIRATE_AURA,
        "char_type": "pirate",
        "pt": {
            "name": "ANNE",
            "title": "A Loba dos Mares",
            "style": "Alfanje Bucaneiro & Pólvora nos Olhos",
            "vel": "[4/5] Robusta e Rápida",
            "dano": "Cleave Amplo de 180° com Alfanje",
            "especial": "Pólvora nos Olhos (Cegueira/Slow)",
            "keys_p1": "[E] Giro de Alfanje (Ataque)",
            "keys_p2": "[R] Pólvora nos Olhos (Especial)",
            "conceito": (
                "Pirata destemida acostumada a motins, abordagens navais e brigas de taverna sujas. "
                "Combina a força bruta de seu alfanje curvo de 180° com truques covardes de pólvora cegante."
            ),
            "habilidades": (
                "• Giro de Alfanje [E]: Golpe com arco monumental de 180 graus na frente e nos flancos.\n"
                "• Pólvora nos Olhos [R]: Arremessa pólvora no rosto do adversário, cegando-o e causando atordoamento."
            ),
            "estrategia_ofensiva": (
                "• Aproxime-se e lance a Pólvora nos Olhos [R] para cegar e desorientar o rival completamente.\n"
                "• Com o adversário cego e sem saber para onde golpear, desfira o giro de 180° com o Alfanje [E].\n"
                "• Seu golpe cobre toda a frente, impossibilitando desvios laterais curtos."
            ),
            "estrategia_defensiva": (
                "• Como vencer Anne: A pólvora dela tem alcance curto. Mantenha distância média e use golpes perfurantes "
                "retos e longos (como Gatotsu ou Florete) para atingi-la fora do alcance do lançamento da pólvora."
            )
        },
        "en": {
            "name": "ANNE",
            "title": "Wolf of the High Seas",
            "style": "Buccaneer Cutlass & Pocket Powder",
            "vel": "[4/5] Heavy & Fast",
            "dano": "180° Broad Cutlass Cleave",
            "especial": "Pocket Powder (Blind/Slow)",
            "keys_p1": "[E] Cutlass Cleave (Attack)",
            "keys_p2": "[R] Pocket Powder (Special)",
            "conceito": (
                "Fearless pirate captain forged in boarding skirmishes and dirty tavern brawls. "
                "Combines heavy 180° cutlass cleaves with blinding gunpowder thrown into the eyes."
            ),
            "habilidades": (
                "• Cutlass Cleave [E]: Sweeping 180-degree horizontal arc covering front and flanks.\n"
                "• Pocket Powder [R]: Hurls gunpowder into the opponent's face, blinding and heavily staggering them."
            ),
            "estrategia_ofensiva": (
                "• Close in and throw Pocket Powder [R] to blind and disorient your rival.\n"
                "• While the enemy is blinded and unable to aim, unleash the 180° Cutlass Cleave [E].\n"
                "• Your wide arc makes short lateral sidesteps impossible to escape."
            ),
            "estrategia_defensiva": (
                "• How to defeat Anne: Her gunpowder throw has short range. Maintain mid-range and use linear piercing "
                "thrusts (like Gatotsu or Fleche) to hit her outside her powder range."
            )
        }
    },
    {
        "id": CHAR_MUSKETEER,
        "color": COLOR_MUSKETEER_AURA,
        "char_type": "musketeer",
        "pt": {
            "name": "JULIE",
            "title": "A Flor da Guarda Real",
            "style": "Esgrima Francesa (Florete & Capa)",
            "vel": "[5/5] Velocidade de Elite",
            "dano": "Fleche Thrust Longo e Preciso",
            "especial": "Pederneira, Floreio de Capa e Rolamento Desviante",
            "keys_p1": "[E] Estocada Fleche (Ataque)",
            "keys_p2": "[R] Pederneira / Floreio de Capa (Especial)",
            "conceito": (
                "Nobre duelista europeia mestre na arte do florete e capa de esgrima. Campeã invicta em duelos "
                "de honra, combina elegância aristocrática, estocadas de alcance cirúrgico e defesas perfeitas."
            ),
            "habilidades": (
                "• Fleche Thrust [E]: Investida frontal alongada em passo de flecha de longo alcance e precisão cirúrgica.\n"
                "• Pederneira / Floreio de Capa [R]: com a pistola pronta, dispara; com ela recarregando, o floreio de capa repele quem está perto e desvia projéteis.\n"
                "• Rolamento [T]: rolamento grande com i-frames que atravessa buracos e desvia projéteis."
            ),
            "estrategia_ofensiva": (
                "• O Fleche tem alcance superior ao das katanas convencionais. Pique o oponente de fora do alcance dele!\n"
                "• Atire com a pederneira [R] de média distância; com a pistola recarregando, use o floreio de capa [R] para repelir o rival.\n"
                "• Abuse de sua velocidade 5/5 para entrar, atacar e recuar com graça e impunidade."
            ),
            "estrategia_defensiva": (
                "• Como vencer Julie: O Fleche tem linha reta muito estreita; esquivas laterais limpas abrem as costas "
                "dela para punição. Ela rola para longe e desvia projéteis durante o rolamento: atire quando ela estiver em recuperação."
            )
        },
        "en": {
            "name": "JULIE",
            "title": "Flower of the Royal Guard",
            "style": "French Fencing (Rapier & Cloak)",
            "vel": "[5/5] Elite Fencing Speed",
            "dano": "Long Precision Fleche Thrust",
            "especial": "Flintlock, Cape Flip and Deflecting Roll",
            "keys_p1": "[E] Fleche Thrust (Attack)",
            "keys_p2": "[R] Flintlock / Cape Flip (Special)",
            "conceito": (
                "Aristocratic European duelist, undefeated master of rapier and combat cloak fencing. "
                "Melds courtly elegance with surgical reach and deadly counter-ripostes."
            ),
            "habilidades": (
                "• Fleche Thrust [E]: Extended acrobatic lunging thrust with extreme range and pinpoint accuracy.\n"
                "• Flintlock / Cape Flip [R]: fires the pistol when ready; while it reloads, the cape flip repels nearby foes and deflects projectiles.\n"
                "• Roll [T]: a large invulnerable roll that clears pits and deflects projectiles."
            ),
            "estrategia_ofensiva": (
                "• Fleche out-ranges conventional samurai katanas. Strike from just outside their range!\n"
                "• Shoot the flintlock [R] from mid-range; while it reloads, use the cape flip [R] to repel your rival.\n"
                "• Abuse your 5/5 top speed to lunge, hit, and dance away untouched."
            ),
            "estrategia_defensiva": (
                "• How to defeat Julie: The Fleche travels along a narrow straight line; clean lateral sidesteps "
                "expose her back to punishment. She rolls away and deflects projectiles mid-roll: shoot when she is recovering."
            )
        }
    },
    {
        "id": CHAR_REN,
        "color": COLOR_REN_AURA,
        "char_type": "ren",
        "pt": {
            "name": "REN",
            "title": "O Monge Shaolin",
            "style": "Punhos de Ferro & Kiai",
            "vel": "[5/5] Relâmpago",
            "dano": "Combo 3 Golpes (Socos e Chutes)",
            "especial": "Grito Kiai (Barreira 360°)",
            "keys_p1": "[E] Combo Punhos | [R] Kiai",
            "keys_p2": "[U] Combo Punhos | [I] Kiai",
            "conceito": (
                "Monge budista peregrino do templo Shaolin. Especialista em artes marciais desarmadas, "
                "combina velocidade de socos inigualável com o poder espiritual do Kiai."
            ),
            "habilidades": (
                "• Combo Shaolin [E]: Sequência fluida de 3 golpes (Jab, Palma e Chute Dragão).\n"
                "• Grito Kiai [R]: Emite um pulso de energia mística que repele projéteis e atordoa oponentes."
            ),
            "estrategia_ofensiva": (
                "• Use a velocidade de 5.4 para pressionar incessantemente os oponentes armados.\n"
                "• Dispare o Kiai para anular projéteis e fechar a distância com segurança."
            ),
            "estrategia_defensiva": (
                "• Como vencer Ren: Ren precisa colar no corpo a corpo; mantenha distância com armas de longo alcance ou estocadas."
            )
        },
        "en": {
            "name": "REN",
            "title": "Shaolin Monk",
            "style": "Iron Fists & Kiai",
            "vel": "[5/5] Lightning Speed",
            "dano": "3-Hit Martial Combo",
            "especial": "Kiai Shout (360° Barrier)",
            "keys_p1": "[E] Fist Combo | [R] Kiai",
            "keys_p2": "[U] Fist Combo | [I] Kiai",
            "conceito": (
                "Wandering Buddhist Shaolin monk. Unarmed martial artist fusing unmatched fist speed with spiritual shockwaves."
            ),
            "habilidades": (
                "• Shaolin Combo [E]: Fluid 3-hit sequence (Jab, Palm Strike, Dragon Kick).\n"
                "• Kiai Shout [R]: Mystic energy wave reflecting projectiles and shoving foes."
            ),
            "estrategia_ofensiva": (
                "• Pressure armed rivals with high movement speed and fast combo cancels.\n"
                "• Counter projectile zoners with well-timed Kiai shockwaves."
            ),
            "estrategia_defensiva": (
                "• How to defeat Ren: Keep spacing outside his short unarmed melee reach with long blades or polearms."
            )
        }
    },
    {
        "id": CHAR_CHIYO,
        "color": COLOR_CHIYO_AURA,
        "char_type": "chiyo",
        "pt": {
            "name": "CHIYO",
            "title": "A Kunoichi das Duas Kodachi",
            "style": "Duas Kodachi em Tesoura",
            "vel": "[4/5] Ágil",
            "dano": "Corte Duplo Tesoura",
            "especial": "Dança Mai (Parry Dançante)",
            "keys_p1": "[E] Kodachi | [R] Dança Mai",
            "keys_p2": "[U] Kodachi | [I] Dança Mai",
            "conceito": (
                "Kunoichi graciosa e acrobática que maneja duas lâminas Kodachi com agilidade cirúrgica e técnica evasiva."
            ),
            "habilidades": (
                "• Corte Tesoura [E]: Golpe duplo rápido e letal com as duas lâminas curtas.\n"
                "• Dança Mai [R]: Giro acrobático defensivo que deflete ataques e contra-ataca em seguida."
            ),
            "estrategia_ofensiva": (
                "• Use a Dança Mai para aparar golpes agressivos e punir o adversário com cortes cruzados."
            ),
            "estrategia_defensiva": (
                "• Como vencer Chiyo: Evite atacar impulsivamente durante a Dança Mai; espere a janela de recuperação."
            )
        },
        "en": {
            "name": "CHIYO",
            "title": "Twin Kodachi Kunoichi",
            "style": "Dual Kodachi Scissor Cuts",
            "vel": "[4/5] Agile",
            "dano": "Scissor Cross Cuts",
            "especial": "Mai Dance (Whirling Parry)",
            "keys_p1": "[E] Kodachi | [R] Mai Dance",
            "keys_p2": "[U] Kodachi | [I] Mai Dance",
            "conceito": (
                "Graceful kunoichi master of dual kodachi blades, excelling at evasive spins and counter-strikes."
            ),
            "habilidades": (
                "• Scissor Cut [E]: Fast, lethal double-blade cross slice.\n"
                "• Mai Dance [R]: Whirling evasive dance that deflects incoming blades."
            ),
            "estrategia_ofensiva": (
                "• Bait opponents into swinging, absorb their blow with Mai Dance, then punish immediately."
            ),
            "estrategia_defensiva": (
                "• How to defeat Chiyo: Do not commit to heavy attacks while she spins; strike when her dance ends."
            )
        }
    },
    {
        "id": CHAR_BENKEI,
        "color": COLOR_BENKEI_AURA,
        "char_type": "benkei",
        "pt": {
            "name": "BENKEI",
            "title": "Guardião Sōhei",
            "style": "Naginata & Armadura Pesada",
            "vel": "[2/5] Tanque",
            "dano": "Estocada Colossal (Alcance 3.0)",
            "especial": "Arremesso de Haste & Tackle com Stun",
            "keys_p1": "[E] Estocada/Tackle | [R] Arremesso",
            "keys_p2": "[U] Estocada/Tackle | [I] Arremesso",
            "conceito": (
                "Monge guerreiro sōhei colossal e inabalável que acumulou 999 armas na Ponte Gojo. "
                "Não possui aparo técnico, compensando com armadura maciça, alcance desmedido da naginata "
                "e um tackle desarmado brutal de atropelamento."
            ),
            "habilidades": (
                "• Estocada Colossal [E]: Golpe frontal penetrante de 3.0 tiles de alcance com alto knockback.\n"
                "• Arremesso de Naginata [R]: Lança a haste pesada a longa distância que se crava no solo sem cair em buracos ou água.\n"
                "• Tackle Atropelo [E desarmado]: Investida de choque que aplica STUN garantido (1.2s) e recupera a arma."
            ),
            "estrategia_ofensiva": (
                "• Domine o centro da arena e a ponte usando a estocada de 3 tiles antes que o rival chegue perto.\n"
                "• Se o adversário fugir, arremesse a naginata [R] e em seguida use o Tackle [E] para atordoá-lo e recuperar a haste."
            ),
            "estrategia_defensiva": (
                "• Como vencer Benkei: Benkei não tem parry e é o lutador mais lento (Velocidade 4.0). Flanqueie pelas diagonais ou use rolamentos para entrar na sua guarda."
            )
        },
        "en": {
            "name": "BENKEI",
            "title": "Sōhei Warrior Monk",
            "style": "Naginata & Heavy Plate Armor",
            "vel": "[2/5] Walking Tank",
            "dano": "Colossal Spear Thrust (Range 3.0)",
            "especial": "Naginata Throw & Stun Tackle",
            "keys_p1": "[E] Thrust/Tackle | [R] Throw",
            "keys_p2": "[U] Thrust/Tackle | [I] Throw",
            "conceito": (
                "Colossal warrior monk of legend on Gojo Bridge. Lacks technical parry, relying on heavy lacquered iron armor, "
                "massive naginata reach, and an unstoppable unarmed charging tackle."
            ),
            "habilidades": (
                "• Colossal Thrust [E]: Penetrating 3.0-tile reach spear strike with devastating knockback.\n"
                "• Naginata Throw [R]: Hurls the heavy spear across long range, embedding safely in the ground.\n"
                "• Stun Tackle [E unarmed]: High-speed kinetic charge that inflicts guaranteed STUN (1.2s) and recovers the weapon."
            ),
            "estrategia_ofensiva": (
                "• Dominate corridors and bridge choke points with your 3.0-tile reach.\n"
                "• Throw the naginata [R] to catch retreating foes, then tackle with [E] for guaranteed stun and weapon recovery."
            ),
            "estrategia_defensiva": (
                "• How to defeat Benkei: Benkei cannot parry and has 4.0 movement speed. Sidestep his linear thrusts and strike during recovery."
            )
        }
    },
    {
        "id": CHAR_ORIN,
        "color": COLOR_ORIN_AURA,
        "char_type": "orin",
        "pt": {
            "name": "O-RIN",
            "title": "Menestrel de Yoshiwara",
            "style": "Tsugaru Shamisen Acústico",
            "vel": "[5/5] Evasiva",
            "dano": "Lâmina Sônica Kamaitachi (Alcance 6.0)",
            "especial": "Ressonância 360° Repelente",
            "keys_p1": "[E] Kamaitachi | [R] Ressonância",
            "keys_p2": "[U] Kamaitachi | [I] Ressonância",
            "conceito": (
                "Cortesã e musicista genial dos becos de Yoshiwara. Nunca empunha uma lâmina física: "
                "seus ataques são ondas sônicas de alta frequência e vácuo disparadas pelas cordas do shamisen com precisão cirúrgica."
            ),
            "habilidades": (
                "• Kamaitachi [E]: Lâmina em crescente de vácuo sônico disparada pelo dedilhado rápido. 1-Hit Kill com alcance de 6.0 tiles.\n"
                "• Ressonância 360° [R]: Acorde potente que emite um pulso acústico concêntrico, desviando projéteis e repelindo oponentes próximos."
            ),
            "estrategia_ofensiva": (
                "• Mantenha o espaçamento máximo: Kamaitachi tem 6.0 tiles de alcance e atravessa a arena velozmente.\n"
                "• Use a Ressonância [R] se o rival avançar de perto para empurrá-lo para longe e cancelar ataques dele."
            ),
            "estrategia_defensiva": (
                "• Como vencer O-Rin: O-Rin é extremamente frágil e não tem golpe corpo a corpo físico. Use o Roll [T] para atravessar o Kamaitachi e ataque à queima-roupa."
            )
        },
        "en": {
            "name": "O-RIN",
            "title": "Yoshiwara Minstrel",
            "style": "Tsugaru Shamisen Acoustic",
            "vel": "[5/5] Evasive Zoner",
            "dano": "Kamaitachi Vacuum Blade (Range 6.0)",
            "especial": "360° Acoustic Resonance",
            "keys_p1": "[E] Kamaitachi | [R] Resonance",
            "keys_p2": "[U] Kamaitachi | [I] Resonance",
            "conceito": (
                "Brilliant courtesan and acoustic minstrel of Yoshiwara. Never wields a physical blade; "
                "attacks entirely through razor-sharp vacuum soundwaves produced by her Tsugaru shamisen."
            ),
            "habilidades": (
                "• Kamaitachi [E]: Crescent vacuum soundwave blade plucked from the shamisen strings. 1-Hit Kill with 6.0-tile reach.\n"
                "• 360° Resonance [R]: Expanding acoustic pulse that reflects light projectiles and shoves nearby rivals away."
            ),
            "estrategia_ofensiva": (
                "• Keep maximum zoning distance: Kamaitachi has a massive 6.0-tile reach and flies at high speed.\n"
                "• Activate Resonance [R] whenever opponents dash or dive in close to repel them."
            ),
            "estrategia_defensiva": (
                "• How to defeat O-Rin: O-Rin has no physical melee blade. Use Roll [T] i-frames to pass cleanly through her Kamaitachi wave."
            )
        }
    },
    {
        "id": CHAR_GORO,
        "color": COLOR_GORO_AURA,
        "char_type": "goro",
        "pt": {
            "name": "GORO",
            "title": "O Camponês Rebelde",
            "style": "Kuwa de Ferro & Pisotão Sísmico",
            "vel": "[3/5] Camponês Robusto",
            "dano": "Kuwa Cleave Pesado (2 HP)",
            "especial": "Pisotão Sísmico (Stun e Onda de Choque)",
            "keys_p1": "[E] Kuwa Cleave | [R] Pisotão",
            "keys_p2": "[U] Kuwa Cleave | [I] Pisotão",
            "conceito": (
                "Guerreiro camponês rebelde do Bakumatsu forjado no trabalho duro da terra. "
                "Empunha uma enxada agrícola pesada de ferro forjado capaz de esmagar armaduras e destruir obstáculos."
            ),
            "habilidades": (
                "• Kuwa Cleave [E]: Golpe descendente demolidor que causa 2 de dano e quebra coberturas no cenário.\n"
                "• Pisotão Sísmico [R]: Bate a bota pesada no solo, liberando uma onda de choque que causa knockback e stun de 0.8s em área."
            ),
            "estrategia_ofensiva": (
                "• Abra caminho com o Pisotão Sísmico [R] para atordoar alvos rápidos ou esquivos.\n"
                "• Conecte imediatamente o Kuwa Cleave [E] durante o stun para garantir dano letal massivo."
            ),
            "estrategia_defensiva": (
                "• Como vencer Goro: O golpe de kuwa tem recuperação mais lenta. Esquive-se para os lados ou use recuo para punir suas investidas."
            )
        },
        "en": {
            "name": "GORO",
            "title": "The Rebel Farmer",
            "style": "Forged Kuwa & Earth Stomp",
            "vel": "[3/5] Heavy Peasant",
            "dano": "Heavy Kuwa Cleave (2 HP)",
            "especial": "Earth Stomp (AoE Stun & Shockwave)",
            "keys_p1": "[E] Kuwa Cleave | [R] Earth Stomp",
            "keys_p2": "[U] Kuwa Cleave | [I] Earth Stomp",
            "conceito": (
                "Battle-hardened peasant rebel of the Bakumatsu era. "
                "Wields a heavy hand-forged agricultural hoe capable of crushing armor and shattering obstacles."
            ),
            "habilidades": (
                "• Kuwa Cleave [E]: Downward crushing cleave dealing 2 damage and destroying destructible cover.\n"
                "• Earth Stomp [R]: Slams boot into the terrain, unleashing a radial shockwave with knockback and 0.8s stun."
            ),
            "estrategia_ofensiva": (
                "• Disrupt evasive foes with Earth Stomp [R] to stop their momentum.\n"
                "• Punish their recovery immediately with the devastating Kuwa Cleave [E]."
            ),
            "estrategia_defensiva": (
                "• How to defeat Goro: His agricultural hoe has longer recovery frames. Sidestep his vertical swing and punish from behind."
            )
        }
    },
    {
        "id": CHAR_ICHI,
        "color": COLOR_ICHI_AURA,
        "char_type": "ichi",
        "pt": {
            "name": "ICHI",
            "title": "A Lâmina Cega",
            "style": "Shikomizue (Gyaku-Iai) & Escuta",
            "vel": "[5/5] Reflexo Extremo",
            "dano": "Saque Gyaku-Iai (0.14s / 2 HP)",
            "especial": "Postura de Escuta (Contra-Ataque Perfurante)",
            "keys_p1": "[E] Gyaku-Iai | [R] Escuta",
            "keys_p2": "[U] Gyaku-Iai | [I] Escuta",
            "conceito": (
                "Mestra espadachim cega lendária inspirada no clássico Zatoichi. Caminha com uma bengala de madeira "
                "que oculta uma katana afiada como navalha, guiando-se pelo som e pela vibração do ar."
            ),
            "habilidades": (
                "• Gyaku-Iai [E]: Saque relâmpago em empunhadura invertida a partir da bengala oculta (0.14s, 2 HP).\n"
                "• Postura de Escuta [R]: Assume foco auditivo sereno. Se atingida nesta janela, bloqueia o ataque e desfere contra-ataque perfurante automático."
            ),
            "estrategia_ofensiva": (
                "• Avance com calma e aproveite o saque mais rápido do jogo para punir tentativas afobadas do rival.\n"
                "• Ative a Postura de Escuta [R] na meia-distância para atrair ataques impulsivos e contra-atacar letalmente."
            ),
            "estrategia_defensiva": (
                "• Como vencer Ichi: Jamais ataque diretamente quando ela estiver na Postura de Escuta. Use fintas, projéteis ou armas de longo alcance para atacá-la com segurança."
            )
        },
        "en": {
            "name": "ICHI",
            "title": "The Blind Blade",
            "style": "Shikomizue (Gyaku-Iai) & Sensory Stance",
            "vel": "[5/5] Extreme Reflexes",
            "dano": "Gyaku-Iai Lightning Draw (0.14s / 2 HP)",
            "especial": "Listen Stance (Sensory Counter-Thrust)",
            "keys_p1": "[E] Gyaku-Iai | [R] Listen Stance",
            "keys_p2": "[U] Gyaku-Iai | [I] Listen Stance",
            "conceito": (
                "Serene blind master swordsman. Wields a disguised wooden walking cane concealing a razor-sharp blade, "
                "sensing opponents through vibrations, footsteps, and rustling air."
            ),
            "habilidades": (
                "• Gyaku-Iai [E]: Blindingly swift reverse-grip draw strike from her concealed cane (0.14s, 2 HP).\n"
                "• Listen Stance [R]: Closes senses to focus purely on sound; automatically counters incoming strikes with a lethal forward thrust."
            ),
            "estrategia_ofensiva": (
                "• Utilize her lightning draw to interrupt opposing attacks in close quarters.\n"
                "• Bait aggressive rushdown foes into your Listen Stance [R] for an unblockable counter-thrust."
            ),
            "estrategia_defensiva": (
                "• How to defeat Ichi: Do not swing blindly into her Listen Stance. Bait the stance with feints or zone her with projectiles."
            )
        }
    },
    {
        "id": CHAR_VALERIUS,
        "color": COLOR_VALERIUS_AURA,
        "char_type": "valerius",
        "pt": {
            "name": "VALERIUS",
            "title": "O Necromante Prussiano",
            "style": "Ceifada Fúnebre & Summons Mortos",
            "vel": "[3/5] Passo Cerimonial",
            "dano": "Ceifada Ampla Soul Reap (2 HP)",
            "especial": "Invocação de Esqueleto (Agarrão & Lentidão)",
            "keys_p1": "[E] Ceifada | [R] Invocação",
            "keys_p2": "[U] Ceifada | [I] Invocação",
            "conceito": (
                "Aristocrata e ocultista prussiano em missão obscura no Bakumatsu. Empunha uma foice fúnebre de ferro forjado "
                "e invoca mortos-vivos das profundezas da terra para imobilizar seus oponentes."
            ),
            "habilidades": (
                "• Ceifada Fúnebre [E]: Golpe horizontal amplo com alcance devastador de duas mãos (2 HP).\n"
                "• Invocação de Esqueleto [R]: Invoca um esqueleto guerreiro autônomo que avança até o rival, causa 1 HP de dano e o segura aplicando lentidão (slow) por tempo limitado."
            ),
            "estrategia_ofensiva": (
                "• Utilize o esqueleto para colocar pressão e forçar o rival a recuar ou ficar preso.\n"
                "• Aproveite o momento em que o rival é agarrado pelo lacaio para aplicar a Ceifada Fúnebre com segurança máxima."
            ),
            "estrategia_defensiva": (
                "• Como vencer Valerius: Destrua o esqueleto com um golpe rápido ou mantenha distância diagonal para desviar do arco largo da foice."
            )
        },
        "en": {
            "name": "VALERIUS",
            "title": "The Prussian Necromancer",
            "style": "Funeral Scythe & Undead Summons",
            "vel": "[3/5] Ceremonial Stride",
            "dano": "Soul Reap Scythe Slash (2 HP)",
            "especial": "Skeleton Minion (Grab & Slow)",
            "keys_p1": "[E] Scythe Slash | [R] Summon",
            "keys_p2": "[U] Scythe Slash | [I] Summon",
            "conceito": (
                "Prussian aristocrat and dark occultist navigating Bakumatsu Japan. Wields a colossal forged-iron funeral scythe "
                "and summons undead minions from cemetery soil to pin foes."
            ),
            "habilidades": (
                "• Funeral Scythe [E]: Wide horizontal sweeping reap with great reach and priority (2 HP).\n"
                "• Undead Summon [R]: Spawns an autonomous skeleton minion that marches towards the foe, dealing 1 HP damage and grabbing them with a lingering slow."
            ),
            "estrategia_ofensiva": (
                "• Send the skeleton forward to control neutral space and force defensive errors.\n"
                "• Punish pinned or slowed opponents with a clean Soul Reap execution."
            ),
            "estrategia_defensiva": (
                "• How to defeat Valerius: Intercept or dash past the skeleton minion. Punish the heavy recovery frames of his funeral scythe."
            )
        }
    },
    {
        "id": CHAR_SEIMEI,
        "color": COLOR_SEIMEI_AURA,
        "char_type": "seimei",
        "pt": {
            "name": "SEIMEI",
            "title": "A Onmyoji dos 6 Elementos",
            "style": "Rondel Onmyōdō Gogyō & Oráculo Sagrado",
            "vel": "[4/5] Movimento Fluido",
            "dano": "12 Feitiços Elementais (1 a 2 HP / Efeitos Únicos)",
            "especial": "Rondel dos 6 Elementos (Madeira, Fogo, Terra, Metal, Água, Yin-Yang)",
            "keys_p1": "[E] Feitiço Primário | [R] Rito Secundário",
            "keys_p2": "[U] Feitiço Primário | [I] Rito Secundário",
            "conceito": (
                "Suprema mestra Onmyōji descendente da corte imperial Heian. Manipula o Rondel Gogyō de adivinhação oracular, "
                "que avança continuamente entre os 5 elementos ancestrais e o estado supremo de Yin-Yang a cada feitiço desferido."
            ),
            "habilidades": (
                "• Rondel Onmyōdō: Mostrador texturizado no rodapé que avança no ciclo horário a cada ação (Madeira -> Fogo -> Terra -> Metal -> Água -> Yin-Yang).\n"
                "• 12 Feitiços Elementais:\n"
                "  - Madeira (木): Primário Kusabi-Bari (enraizamento 0.8s) | Secundário Shinju no Ibuki (muralha de raízes e espinhos).\n"
                "  - Fogo (火): Primário Guren no Ofuda (lótus incandescente explosiva) | Secundário Hi-bashira (pilar de fogo eruptivo).\n"
                "  - Terra (土): Primário Ganseki-dan (rocha sísmica com knockback) | Secundário Doryū-heki (megalito com 2 HP de cobertura).\n"
                "  - Metal (金): Primário Hagane no Yaiba (lâmina de prata a 26 m/s que quebra guarda) | Secundário Kongō-jin (escudo com sino Kagura de contra-stun).\n"
                "  - Água (水): Primário Suiryū no Ya (torrente ricocheteante com lentidão) | Secundário Kagami-Mizu (espelho d'água que reflete projéteis).\n"
                "  - Yin-Yang (☯): Primário Senkō / Kurayami (orbes espirais duplas teleguiadas) | Secundário Tenmei no Senkoku (oráculo de estase cósmica)."
            ),
            "estrategia_ofensiva": (
                "• Domine a sequência generativa do Rondel para encadear controle (Madeira/Terra) e dano explosivo (Fogo/Metal/Yin-Yang).\n"
                "• Use o indicador do rodapé para antecipar o próximo elemento e ditar o ritmo da luta."
            ),
            "estrategia_defensiva": (
                "• Como vencer Seimei: Observe a cor da aura e o Rondel no rodapé para saber qual feitiço ela possui. Esquive de lado nas agulhas de Madeira e não ataque de frente durante o elemento Metal."
            )
        },
        "en": {
            "name": "SEIMEI",
            "title": "The Onmyoji of the Six Elements",
            "style": "Onmyōdō Gogyō Rondel & Celestial Oracle",
            "vel": "[4/5] Fluid Motion",
            "dano": "12 Elemental Spells (1 to 2 HP / Unique Spellcraft)",
            "especial": "Six-Element Rondel (Wood, Fire, Earth, Metal, Water, Yin-Yang)",
            "keys_p1": "[E] Primary Spell | [R] Secondary Rite",
            "keys_p2": "[U] Primary Spell | [I] Secondary Rite",
            "conceito": (
                "Supreme onmyoji spiritualist preserving ancient Heian cosmology. Wields the Gogyō divination Rondel at the bottom of the screen, "
                "which continuously rotates through the 5 elemental phases plus divine Yin-Yang with every spell cast."
            ),
            "habilidades": (
                "• Onmyōdō Rondel: Rotating dial on the bottom HUD advancing clockwise on every action (Wood -> Fire -> Earth -> Metal -> Water -> Yin-Yang).\n"
                "• 12 Unique Spells:\n"
                "  - Wood (木): Primary Kusabi-Bari (0.8s root) | Secondary Shinju no Ibuki (sprouting briar root barrier).\n"
                "  - Fire (火): Primary Guren no Ofuda (lotus explosion) | Secondary Hi-bashira (erupting pillar of flame).\n"
                "  - Earth (土): Primary Ganseki-dan (heavy seismic rock with knockback) | Secondary Doryū-heki (2-hit solid megalith cover).\n"
                "  - Metal (金): Primary Hagane no Yaiba (26 m/s silver blade piercing parry) | Secondary Kongō-jin (adamantine Kagura counter-stun shield).\n"
                "  - Water (水): Primary Suiryū no Ya (bouncing spiral torrent with slow) | Secondary Kagami-Mizu (reflective water mirror dome).\n"
                "  - Yin-Yang (☯): Primary Senkō / Kurayami (twin homing light/void spiral) | Secondary Tenmei no Senkoku (celestial stasis oracle diagram)."
            ),
            "estrategia_ofensiva": (
                "• Master the predictable generative cycle to plan combo chains and space denial.\n"
                "• Track the dial indicator to adapt instantly between ranged bolts and protective boundaries."
            ),
            "estrategia_defensiva": (
                "• How to defeat Seimei: Watch her foot aura and bottom Rondel to read her active element. Dodge laterally against Wood needles and avoid striking into Metal's adamantine counter-guard."
            )
        }
    },
    {
        "id": CHAR_DAIKI,
        "color": COLOR_DAIKI_AURA,
        "char_type": "daiki",
        "pt": {
            "name": "DAIKI",
            "title": "O Peregrino do Bastão Bō",
            "style": "Bōjutsu Monástico & Queda Meteórica",
            "vel": "[4/5] Dinâmico e Ágil",
            "dano": "Golpes de Bastão de Carvalho (1 a 2 HP)",
            "especial": "Salto de Alavanca & Queda Meteórica (Quebra-Guarda)",
            "keys_p1": "[E] Bastão Bō | [R] Salto com Vara",
            "keys_p2": "[U] Bastão Bō | [I] Salto com Vara",
            "conceito": (
                "Monge guerreiro peregrino que percorre as montanhas de pinheiros no Bakumatsu. "
                "Empunha um pesado bastão Bō de carvalho com ponteiras de ferro, combinando amplitude defensiva, "
                "deflexão de projéteis e acrobacias aéreas fulminantes."
            ),
            "habilidades": (
                "• Golpe de Bastão Bō [E]: Varreduras horizontais e estocadas em longo alcance com o bastão de duas mãos.\n"
                "• Salto com Vara [R]: Crava o bastão no solo e se projeta alto no ar, refletindo projéteis na subida e desferindo uma Queda Meteórica que esmaga guardas na aterrissagem."
            ),
            "estrategia_ofensiva": (
                "• Use a amplitude do bastão para golpear fora do alcance de katanas convencionais.\n"
                "• Surpreenda oponentes defensivos com o Salto com Vara para esmagar bloqueios e abrir brechas letais."
            ),
            "estrategia_defensiva": (
                "• Como vencer Daiki: Cuidado ao atirar projéteis quando ele estiver prestes a saltar. Espere o momento de aterrissagem do Salto com Vara para punir sua breve recuperação."
            )
        },
        "en": {
            "name": "DAIKI",
            "title": "The Bō Staff Pilgrim",
            "style": "Monastic Bōjutsu & Meteor Drop",
            "vel": "[4/5] Dynamic & Agile",
            "dano": "Oak Bō Staff Strikes (1-2 HP)",
            "especial": "Vault Leap & Meteor Drop (Guard Crush)",
            "keys_p1": "[E] Bō Staff | [R] Vault Leap",
            "keys_p2": "[U] Bō Staff | [I] Vault Leap",
            "conceito": (
                "Wandering pilgrim monk traversing pine forest trails in Bakumatsu Japan. Wields a heavy 6-foot oak Bō "
                "staff reinforced with forged iron rings, combining wide spacing, projectile deflection, and aerial acrobatics."
            ),
            "habilidades": (
                "• Bō Staff Strike [E]: Sweeping arcs and thrusts with long reach, controlling mid-range space.\n"
                "• Vault Leap [R]: Plants staff into earth to launch airborne, deflecting projectiles on ascent and crashing down with a Meteor Drop that crushes guards on landing."
            ),
            "estrategia_ofensiva": (
                "• Dominate neutral distance using superior staff maai against shorter blades.\n"
                "• Use Vault Leap against blocking opponents to trigger guard crush and open lethal finishers."
            ),
            "estrategia_defensiva": (
                "• How to defeat Daiki: Avoid shooting projectiles when he is ready to vault. Evade the downward Meteor Drop and punish his landing frames."
            )
        }
    },
    {
        "id": CHAR_AOI,
        "color": COLOR_AOI_AURA,
        "char_type": "aoi",
        "pt": {
            "name": "AOI",
            "title": "A Caçadora Ainu de Hokkaido",
            "style": "Lança Op & Armadilha de Urso",
            "vel": "[4/5] Ágil e Furtiva",
            "dano": "Estocadas de Lança Op (1 HP)",
            "especial": "Armadilha de Urso (Dano Letal por Contato)",
            "keys_p1": "[E] Lança Op | [R] Armadilha",
            "keys_p2": "[U] Lança Op | [I] Armadilha",
            "conceito": (
                "Jovem caçadora das florestas boreais de Ezo (Hokkaido). Especialista em sobrevivência no rigor do inverno, "
                "combina perfurações rápidas com sua lança cerimonial Op e armadilhas de urso serrilhadas de ferro pesado."
            ),
            "habilidades": (
                "• Estocada de Lança Op [E]: Ataque penetrante rápido de longo alcance com ponta de aço e borla de pele.\n"
                "• Armadilha de Urso [R]: Posiciona uma armadilha mecânica de mandíbulas afiadas no chão. Mata instantaneamente qualquer rival que pisar nela."
            ),
            "estrategia_ofensiva": (
                "• Plante armadilhas em rotas estreitas e induza o rival a recuar em direção às mandíbulas de aço.\n"
                "• Mantenha pressão à distância com a ponta da lança Op sem se expor a contra-ataques."
            ),
            "estrategia_defensiva": (
                "• Como vencer Aoi: Observe atentamente o piso para não pisar nas armadilhas de urso metálicas. Pule ou esquive para fechar distância e puna suas estocadas lineares."
            )
        },
        "en": {
            "name": "AOI",
            "title": "The Ainu Huntress of Hokkaido",
            "style": "Op Spear & Steel Bear Trap",
            "vel": "[4/5] Agile & Elusive",
            "dano": "Op Spear Piercing (1 HP)",
            "especial": "Bear Trap (Instant Contact Kill)",
            "keys_p1": "[E] Op Spear | [R] Bear Trap",
            "keys_p2": "[U] Op Spear | [I] Bear Trap",
            "conceito": (
                "Fierce young huntress from the snowy wilderness of Ezo (Hokkaido). An expert arctic tracker "
                "combining quick reach with her traditional Op hunting spear and heavy serrated steel bear traps."
            ),
            "habilidades": (
                "• Op Spear Thrust [E]: Swift piercing spear thrust with sharp steel blade and fur tassel.\n"
                "• Bear Trap [R]: Places a heavy spring-loaded iron jaw trap on the ground. Instantly executes anyone who steps on it."
            ),
            "estrategia_ofensiva": (
                "• Plant bear traps in high-traffic combat lanes to restrict movement.\n"
                "• Use spear thrusts to keep distance and herd the rival into planted traps."
            ),
            "estrategia_defensiva": (
                "• How to defeat Aoi: Keep your eyes on the ground to avoid iron bear traps. Use diagonal dashes to bypass linear thrusts and engage at close quarters."
            )
        }
    },
    {
        "id": CHAR_RAIDEN,
        "color": COLOR_RAIDEN_AURA,
        "char_type": "raiden",
        "pt": {
            "name": "RAIDEN",
            "title": "O Yokozuna dos Trovões",
            "style": "Sumô Imperial Rikishi, Combo Tsuppari & Tachiai 3-Fases",
            "vel": "[2/5] Colossal e Inabalável (3 HP)",
            "dano": "1 Dano (Harite), 1 Dano + Quebra de Guarda (Morote), 1 a 2 Danos (Tachiai)",
            "especial": "Esquiva Shiko Slip-Step, Hiperarmadura & Guarda Gassho-hineri",
            "keys_p1": "[E] Combo Tsuppari | [R] Tachiai Tackle",
            "keys_p2": "[U] Combo Tsuppari | [I] Tachiai Tackle",
            "conceito": (
                "Grande campeão Yokozuna do Bakumatsu. Um colosso de força pura e disciplina ritual inabalável, "
                "que usa seus 3 HP e hiperarmadura para avançar sem recuar contra projéteis leves, "
                "empurrando e arremessando adversários para fora do ringue e contra os abismos da arena."
            ),
            "habilidades": (
                "• Combo Tsuppari [E]: Sequência de 2 golpes de sumô. Golpe 1: Harite (palma pesada de direita). Golpe 2: Morote-Tsuppari (dupla palma sônica frontal) que quebra parries e a guarda adversária com pushback massivo.\n"
                "• Tachiai Tackle [R]: Investida autêntica de 3 fases (agachamento ritual -> aceleração contínua de 4.0 a 12.5 m/s com esteira de poeira -> choque sísmico). Causa 1 de dano no início e escala para 2 de dano fatal + projeção aérea de 5.2m se atingir na velocidade máxima!\n"
                "• Shiko Slip-Step [Shift/Barra]: Deslize terrestre pesado de sumô (Suriashi) com pés plantados e 12 i-frames de imunidade sem rolar no chão."
            ),
            "estrategia_ofensiva": (
                "• Conecte o Morote-Tsuppari para estilhaçar parries inimigos e abrir brechas indefensáveis.\n"
                "• Inicie o Tachiai Tackle à meia distância para atingir aceleração máxima (>=10 m/s), desferindo o devastador impacto de 2 de dano que arremessa o oponente para fora dos limites."
            ),
            "estrategia_defensiva": (
                "• Como vencer Raiden: Não tente aparar (parry) o segundo golpe do Tsuppari, pois ele quebra defesas! Esquive em diagonal quando vir Raiden agachar para o Tachiai, punindo sua desaceleração pelas costas."
            )
        },
        "en": {
            "name": "RAIDEN",
            "title": "The Thunder Yokozuna",
            "style": "Imperial Rikishi Sumo, 2-Hit Tsuppari Combo & 3-Phase Tachiai",
            "vel": "[2/5] Colossal & Unyielding (3 HP)",
            "dano": "1 Dmg (Harite), 1 Dmg + Guard Break (Morote), 1 to 2 Critical Dmg (Tachiai)",
            "especial": "Shiko Slip-Step Dodge, Super Armor & Gassho-hineri Guard",
            "keys_p1": "[E] Tsuppari Combo | [R] Tachiai Tackle",
            "keys_p2": "[U] Tsuppari Combo | [I] Tachiai Tackle",
            "conceito": (
                "Legendary Yokozuna champion of the Bakumatsu era. A colossal titan of raw power and ritual discipline, "
                "utilizing 3 HP and advance super armor to ignore light projectiles while shoving rivals into pits and ring borders."
            ),
            "habilidades": (
                "• Tsuppari Combo [E]: 2-hit sumo sequence. Hit 1: Harite (heavy right open-palm). Hit 2: Morote-Tsuppari (dual sonic palm strike) that shatters enemy parries and breaks guard with massive pushback.\n"
                "• Tachiai Tackle [R]: Authentic 3-phase charge (crouch startup -> continuous acceleration from 4.0 to 12.5 m/s with dust trail -> seismic slam). Deals 1 damage early, scaling up to 2 lethal damage + 5.2m aerial launch if impacting at top speed!\n"
                "• Shiko Slip-Step [Shift/Space]: Heavy clay slide (Suriashi) with low center of gravity and 12 i-frames without rolling."
            ),
            "estrategia_ofensiva": (
                "• Use Morote-Tsuppari to shatter defensive parries and leave rivals wide open.\n"
                "• Initiate Tachiai Tackle from mid-range to build maximum momentum (>=10 m/s), unleashing the 2-damage critical impact that launches foes into hazards."
            ),
            "estrategia_defensiva": (
                "• How to defeat Raiden: Never try to parry the second hit of Tsuppari as it breaks guards! Dodge diagonally when Raiden crouches for Tachiai, then punish his deceleration from behind."
            )
        }
    },
    {
        "id": CHAR_HENDRIKA,
        "color": COLOR_HENDRIKA_AURA,
        "char_type": "hendrika",
        "pt": {
            "name": "HENDRIKA",
            "title": "A Alquimista de Dejima",
            "style": "Alquimia Holandesa, Estilete Corrosivo & 5 Reagentes",
            "vel": "[4/5] Rápida e Imprevisível (2 HP)",
            "dano": "Estocadas Ácidas & Poças Químicas (1 a 2 HP)",
            "especial": "5 Frascos Reagentes c/ Potencialização de Cenário (Tier 1 & Tier 2)",
            "keys_p1": "[E] Estilete Ácido | [R] Frasco Alquímico",
            "keys_p2": "[U] Estilete Ácido | [I] Frasco Alquímico",
            "conceito": (
                "Cientista holandesa excêntrica e genial da feitoria de Dejima em Nagasaki. "
                "Combina a rapidez cirúrgica de um estilete cáustico com o arremesso de frascos químicos "
                "de 5 compostos distintos, potencializados ao coletar reagentes de bancadas e barris do cenário."
            ),
            "habilidades": (
                "• Estilete Corrosivo [E]: Estocada rápida perfurante banhada em ácido que erode e quebra posturas de defesa.\n"
                "• Frasco Alquímico [R]: Arremessa em arco 3D frascos de Ácido (Verde), Fogo Grego (Laranja), Éter (Roxo), Salitre (Ciano) e Miasma (Amarelo), criando poças e nuvens persistentes."
            ),
            "estrategia_ofensiva": (
                "• Intercale estocadas de estilete com o arremesso de frascos para controlar rotas e negar espaço ao rival.\n"
                "• Aproxime-se de bancadas e barris do cenário para potencializar seus compostos ao Tier 2 com raio e dano ampliados."
            ),
            "estrategia_defensiva": (
                "• Como vencer Hendrika: Evite permanecer dentro das poças ácidas e névoas congelantes no solo. Use armas pesadas de longo alcance para golpeá-la antes que ela estabeleça controle de área."
            )
        },
        "en": {
            "name": "HENDRIKA",
            "title": "The Dejima Alchemist",
            "style": "Dutch Alchemy, Corrosive Stiletto & 5 Reagents",
            "vel": "[4/5] Fast & Unpredictable (2 HP)",
            "dano": "Acid Punctures & Chemical Pools (1-2 HP)",
            "especial": "5 Reagent Flasks w/ Arena Upgrades (Tier 1 & Tier 2)",
            "keys_p1": "[E] Acid Stiletto | [R] Alchemical Flask",
            "keys_p2": "[U] Acid Stiletto | [I] Alchemical Flask",
            "conceito": (
                "Brilliant and eccentric Dutch scholar at the VOC Dejima factory in Nagasaki. "
                "Blends swift corrosive stiletto strikes with arcing chemical flasks across 5 distinct compounds, "
                "upgraded to Tier 2 by scavenging nearby laboratory workbenches and reagent barrels."
            ),
            "habilidades": (
                "• Corrosive Stiletto [E]: Quick piercing dagger thrust coated in acid that erodes guards and counters.\n"
                "• Alchemical Flask [R]: Hurls an arcing vial of Acid (Green), Greek Fire (Orange), Ether (Purple), Frost (Cyan), or Miasma (Yellow), generating lingering area-denial hazard pools."
            ),
            "estrategia_ofensiva": (
                "• Mix stiletto thrusts with area flasks to trap foes between corrosive pools and water pits.\n"
                "• Move near chemical barrels or workbenches to boost concoctions to Tier 2 with enhanced radius and potency."
            ),
            "estrategia_defensiva": (
                "• How to defeat Hendrika: Steer clear of glowing ground pools and freezing vapor mists. Utilize extended-reach weapons to strike outside her short stiletto range."
            )
        }
    },
    {
        "id": CHAR_BOSS,
        "color": COLOR_BOSS_AURA,
        "char_type": "gashadokuro",
        "pt": {
            "name": "GASHADOKURO",
            "title": "Oni Colossal da Fome Insaciável (Final Boss)",
            "style": "Transmorfo de Ossos Ancestrais & Fogo Espectral",
            "vel": "[2/5] Colossal & Ponderoso",
            "dano": "Impactos Devastadores (1 a 2 HP / Área de Choque)",
            "especial": "Metamorfose em 5 Fases de Batalha (Bípede, Serpente, Torso, Clava, Crânio)",
            "keys_p1": "[Chefe Final do Modo Arcade]",
            "keys_p2": "[Invulnerável Fora das Janelas de Vulnerabilidade]",
            "conceito": (
                "Entidade titânica formada pelas almas de guerreiros caídos e não sepultados no Bakumatsu. "
                "Assume 5 formas anatômicas distintas à medida que seus ossos se fragmentam sob os golpes de seu adversário."
            ),
            "habilidades": (
                "• Golpe Colossal: Cortes com lâmina gigante de ferro negro e pisões sísmicos.\n"
                "• Metamorfose das 5 Fases: Alterna entre Bípede, Serpente Rastejante, Torso Saltador, Clava Viva e Crânio Voador.\n"
                "• Fogo Espectral: Bolas de fogo roxas e fissuras no solo que ardem com almas vingativas."
            ),
            "estrategia_ofensiva": (
                "• Observe a telegrafia vermelha no solo e desvie dos círculos e linhas de impacto antes que a investida ocorra.\n"
                "• Ataque o ponto fraco revelado exclusivamente quando o chefe ficar atordoado ou cravado no chão."
            ),
            "estrategia_defensiva": (
                "• Como vencer Gashadokuro: Nunca tente atacar durante suas investidas, pois seus ossos bloqueiam 100% do dano. Espere pacientemente a janela de fadiga (após colidir com uma rocha ou cravar a clava) para desferir o golpe certeiro!"
            )
        },
        "en": {
            "name": "GASHADOKURO",
            "title": "Colossal Starvation Oni (Final Boss)",
            "style": "Ancient Bone Transmutation & Spectral Fire",
            "vel": "[2/5] Colossal & Weighty",
            "dano": "Devastating Impacts (1-2 HP / Area of Effect)",
            "especial": "5-Phase Battle Metamorphosis (Biped, Serpent, Torso, Club, Skull)",
            "keys_p1": "[Arcade Mode Final Boss]",
            "keys_p2": "[Invulnerable Outside Vulnerability Windows]",
            "conceito": (
                "Colossal skeletal demon gathered from the vengeful spirits of unburied warriors during the Bakumatsu era. "
                "Shifts through 5 distinct anatomical configurations as its bones fracture under mortal steel."
            ),
            "habilidades": (
                "• Colossal Strike: Cleaving arc with dark iron blade and ground-shaking foot stomps.\n"
                "• 5-Phase Metamorphosis: Transmutes between Bipedal Titan, Crawling Spine Serpent, Bounding Torso, Living Club, and Flying Skull.\n"
                "• Spectral Miasma: Purple soul fireballs and burning ground fissures erupting across the arena."
            ),
            "estrategia_ofensiva": (
                "• Respect ground telegraphs and roll out of circle markers before tectonic impacts land.\n"
                "• Strike the exposed vulnerable weak point only when the boss stuns itself or lodges into the ground."
            ),
            "estrategia_defensiva": (
                "• How to defeat Gashadokuro: Never attack while the boss is charging or leaping; its bones deflect all incoming blades. Wait for fatigue windows when it crashes into tombstones or embeds its club, then strike swiftly!"
            )
        }
    }
]

class GameHelpModal:
    """Modal Interativo de Ajuda Completa do Jogo e Guia dos 12 Guerreiros com i18n e Rolagem Suave."""
    TAB_RULES = 0
    TAB_CONTROLS = 1
    TAB_FIGHTERS = 2

    # Seções da ficha técnica de guerreiro
    SEC_ALL = 0
    SEC_CONCEPT = 1
    SEC_ARSENAL = 2
    SEC_OFFENSE = 3
    SEC_DEFENSE = 4

    def __init__(self):
        self.is_open = False
        self.current_tab = self.TAB_RULES
        self.selected_fighter_idx = 0
        self.fighter_sub_section = self.SEC_ALL
        self.anim_timer = 0.0

        # Controle de rolagem vertical (anti-overflow)
        self.scroll_y = 0.0
        self.max_scroll = 0.0

        # Retângulos de interação calculados em render
        self.modal_rect = pygame.Rect(0, 0, 0, 0)
        self.close_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.lang_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.tab_rects = []
        self.fighter_tab_rects = []
        self.sub_sec_btn_rects = []
        self.prev_fighter_btn = pygame.Rect(0, 0, 0, 0)
        self.next_fighter_btn = pygame.Rect(0, 0, 0, 0)
        self._axis_x_held = False
        self._axis_y_held = False

    @staticmethod
    def _fit_text(font: pygame.font.Font, text: str, color, max_w: int) -> pygame.Surface:
        """Renderiza o texto ajustando se exceder a largura máxima com elipse '...'."""
        surf = font.render(text, True, color)
        if surf.get_width() <= max_w:
            return surf
        while len(text) > 1 and font.size(text + "...")[0] > max_w:
            text = text[:-1]
        return font.render(text.rstrip() + "...", True, color)

    @staticmethod
    def _wrap_text(font: pygame.font.Font, text: str, max_w: int, indent: str = "") -> list[str]:
        """Quebra um texto em várias linhas respeitando max_w."""
        lines = []
        for raw_line in text.split("\n"):
            if not raw_line:
                lines.append("")
                continue
            words = raw_line.split(" ")
            cur_line = ""
            for w in words:
                test_line = (cur_line + " " + w) if cur_line else w
                if font.size(test_line)[0] <= max_w:
                    cur_line = test_line
                else:
                    if cur_line:
                        lines.append(cur_line)
                    cur_line = indent + w
            if cur_line:
                lines.append(cur_line)
        return lines

    def open(self, tab: int = TAB_RULES, fighter_idx: int = 0, char_id: str | None = None):
        self.is_open = True
        self.current_tab = tab
        self.scroll_y = 0.0
        self.fighter_sub_section = self.SEC_ALL
        if char_id:
            for idx, fdata in enumerate(FIGHTERS_GUIDE_DATA):
                if fdata["id"] == char_id:
                    self.selected_fighter_idx = idx
                    return
        if 0 <= fighter_idx < len(FIGHTERS_GUIDE_DATA):
            self.selected_fighter_idx = fighter_idx

    def close(self):
        self.is_open = False

    def set_sub_section(self, idx: int):
        self.fighter_sub_section = idx
        self.scroll_y = 0.0

    def update(self, dt: float):
        if self.is_open:
            self.anim_timer += dt

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retorna True se o evento foi consumido pelo modal."""
        if not self.is_open:
            return False

        # --- 1. SUPORTE A GAMEPAD NO GUIA / AJUDA ---
        if event.type == pygame.JOYBUTTONDOWN:
            from src.input.controller_manager import get_dpad_motion_from_event
            # Fechar modal: Círculo (1) ou Options (6)
            if event.button in (1, 6):
                self.close()
                return True
            # Confirmar / Selecionar seção: Cruz (0) ou Quadrado (2)
            elif event.button in (0, 2):
                if self.current_tab == self.TAB_FIGHTERS:
                    self.fighter_sub_section = (self.fighter_sub_section + 1) % 4
                    self.scroll_y = 0.0
                return True
            # Alternar idioma: Triângulo (3)
            elif event.button == 3:
                toggle_lang()
                self.scroll_y = 0.0
                return True
            # Alternar abas: L1 (9) ou R1 (10)
            elif event.button == 9:
                self.current_tab = (self.current_tab - 1) % 3
                self.scroll_y = 0.0
                return True
            elif event.button == 10:
                self.current_tab = (self.current_tab + 1) % 3
                self.scroll_y = 0.0
                return True

            # D-Pad botões virtuais (11=Up, 12=Down, 13=Left, 14=Right)
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                dx, dy = d_dir
                if dy < 0:
                    self.scroll_y = max(0.0, self.scroll_y - 48.0)
                    return True
                elif dy > 0:
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 48.0)
                    return True
                if self.current_tab == self.TAB_FIGHTERS and dx != 0:
                    self.selected_fighter_idx = (self.selected_fighter_idx + dx) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    return True

        elif event.type == pygame.JOYHATMOTION:
            from src.input.controller_manager import get_dpad_motion_from_event
            d_dir = get_dpad_motion_from_event(event)
            if d_dir:
                dx, dy = d_dir
                if dy < 0:
                    self.scroll_y = max(0.0, self.scroll_y - 48.0)
                    return True
                elif dy > 0:
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 48.0)
                    return True
                if self.current_tab == self.TAB_FIGHTERS and dx != 0:
                    self.selected_fighter_idx = (self.selected_fighter_idx + dx) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    return True

        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:
                from src.input.controller_manager import get_controller_manager
                ctrl_mgr = get_controller_manager()
                val = -event.value if getattr(ctrl_mgr, "invert_y", False) else event.value
                if val > 0.65:
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 36.0)
                elif val < -0.65:
                    self.scroll_y = max(0.0, self.scroll_y - 36.0)
            elif event.axis == 0 and self.current_tab == self.TAB_FIGHTERS:
                if event.value > 0.65 and not self._axis_x_held:
                    self.selected_fighter_idx = (self.selected_fighter_idx + 1) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    self._axis_x_held = True
                elif event.value < -0.65 and not self._axis_x_held:
                    self.selected_fighter_idx = (self.selected_fighter_idx - 1) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    self._axis_x_held = True
                elif abs(event.value) < 0.25:
                    self._axis_x_held = False

        # --- 2. TECLADO ---
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_h):
                self.close()
                return True
            elif event.key == pygame.K_l:
                toggle_lang()
                self.scroll_y = 0.0
                return True
            elif event.key == pygame.K_TAB:
                self.current_tab = (self.current_tab + 1) % 3
                self.scroll_y = 0.0
                return True
            elif event.key in (pygame.K_UP, pygame.K_PAGEUP):
                self.scroll_y = max(0.0, self.scroll_y - 48.0)
                return True
            elif event.key in (pygame.K_DOWN, pygame.K_PAGEDOWN):
                self.scroll_y = min(self.max_scroll, self.scroll_y + 48.0)
                return True
            elif self.current_tab == self.TAB_FIGHTERS:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected_fighter_idx = (self.selected_fighter_idx - 1) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    return True
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected_fighter_idx = (self.selected_fighter_idx + 1) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    return True

        elif event.type == pygame.MOUSEWHEEL:
            # Rolagem vertical suave (suporta trackpad e roda de mouse)
            self.scroll_y = max(0.0, min(self.max_scroll, self.scroll_y - event.y * 36.0))
            return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Botão fechar [X]
            if self.close_btn_rect.collidepoint(mx, my):
                self.close()
                return True

            # Botão de idioma [ PT | EN ]
            if self.lang_btn_rect.collidepoint(mx, my):
                toggle_lang()
                self.scroll_y = 0.0
                return True

            # Clique fora do modal
            if not self.modal_rect.collidepoint(mx, my):
                self.close()
                return True

            # Abas principais
            for idx, rect in enumerate(self.tab_rects):
                if rect.collidepoint(mx, my):
                    self.current_tab = idx
                    self.scroll_y = 0.0
                    return True

            # Controles da aba de guerreiros
            if self.current_tab == self.TAB_FIGHTERS:
                if self.prev_fighter_btn.collidepoint(mx, my):
                    self.selected_fighter_idx = (self.selected_fighter_idx - 1) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    return True
                if self.next_fighter_btn.collidepoint(mx, my):
                    self.selected_fighter_idx = (self.selected_fighter_idx + 1) % len(FIGHTERS_GUIDE_DATA)
                    self.scroll_y = 0.0
                    return True
                for idx, rect in enumerate(self.fighter_tab_rects):
                    if rect.collidepoint(mx, my):
                        self.selected_fighter_idx = idx
                        self.scroll_y = 0.0
                        return True
                for idx, rect in enumerate(self.sub_sec_btn_rects):
                    if rect.collidepoint(mx, my):
                        self.fighter_sub_section = idx
                        self.scroll_y = 0.0
                        return True

            return True

        return True  # Bloqueia outros inputs enquanto modal estiver aberto

    def render(self, surface: pygame.Surface, font_large: pygame.font.Font, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        if not self.is_open:
            return

        lang = get_lang()

        # Escurecimento dramático do fundo
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        from src.effects import parchment as pm

        overlay.fill((10, 14, 12, 220))
        surface.blit(overlay, (0, 0))

        # Dimensões da Caixa Modal (1160 x 640)
        mw, mh = 1160, 640
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        self.modal_rect = pygame.Rect(mx, my, mw, mh)

        # Fundo do Modal em Pergaminho Sumi-E Envelhecido com Varas de Madeira
        paper = pm.make_paper(mw, mh, seed=77, ragged=(False, False, True, True), burn=0.25)
        surface.blit(pm._soft_shadow(paper, blur=8, opacity=140), (mx + 3, my + 5))
        surface.blit(paper, (mx, my))

        pm.draw_rod(surface, "top", self.modal_rect.centerx, self.modal_rect.y - 14, mw + 32)
        pm.draw_rod(surface, "bottom", self.modal_rect.centerx, self.modal_rect.bottom - 22, mw + 32)

        # Barra de Título Superior
        title_s = font_large.render(t("help_modal_title"), True, pm.INK)
        surface.blit(title_s, (mx + 36, my + 24))

        # Botão Seletor Flutuante de Idioma [ PT | EN ] (Padrão Boardbots)
        self.lang_btn_rect = pygame.Rect(mx + mw - 175, my + 24, 100, 32)
        pygame.draw.rect(surface, (226, 212, 185), self.lang_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (140, 125, 105), self.lang_btn_rect, 1, border_radius=6)

        pt_col = COLOR_WHITE if lang == LANG_PT else pm.INK_SOFT
        en_col = COLOR_WHITE if lang == LANG_EN else pm.INK_SOFT
        pt_bg = pm.SEAL_RED if lang == LANG_PT else (210, 195, 170)
        en_bg = pm.SEAL_RED if lang == LANG_EN else (210, 195, 170)

        r_pt = pygame.Rect(self.lang_btn_rect.x + 3, self.lang_btn_rect.y + 3, 44, 26)
        r_en = pygame.Rect(self.lang_btn_rect.x + 53, self.lang_btn_rect.y + 3, 44, 26)
        pygame.draw.rect(surface, pt_bg, r_pt, border_radius=4)
        pygame.draw.rect(surface, en_bg, r_en, border_radius=4)

        s_pt = font_small.render("PT", True, pt_col)
        s_en = font_small.render("EN", True, en_col)
        surface.blit(s_pt, (r_pt.centerx - s_pt.get_width() // 2, r_pt.centery - s_pt.get_height() // 2))
        surface.blit(s_en, (r_en.centerx - s_en.get_width() // 2, r_en.centery - s_en.get_height() // 2))

        # Botão Fechar [ X ]
        self.close_btn_rect = pygame.Rect(mx + mw - 56, my + 24, 32, 32)
        pygame.draw.rect(surface, pm.SEAL_RED, self.close_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (212, 175, 55), self.close_btn_rect, 1, border_radius=6)
        x_lbl = font_mid.render("X", True, COLOR_WHITE)
        surface.blit(x_lbl, (self.close_btn_rect.centerx - x_lbl.get_width() // 2, self.close_btn_rect.centery - x_lbl.get_height() // 2))

        # Abas de Navegação Superiores
        tab_names = [t("tab_rules"), t("tab_controls"), t("tab_fighters")]
        tab_w = 230
        tab_h = 34
        start_tab_x = mx + 36
        tab_y = my + 72

        self.tab_rects.clear()
        for i, name in enumerate(tab_names):
            t_rect = pygame.Rect(start_tab_x + i * (tab_w + 12), tab_y, tab_w, tab_h)
            self.tab_rects.append(t_rect)
            is_active = (self.current_tab == i)

            t_bg = (238, 226, 202) if is_active else (226, 212, 185)
            t_border = pm.SEAL_RED if is_active else (160, 145, 125)
            t_col = pm.SEAL_RED if is_active else pm.INK

            pygame.draw.rect(surface, t_bg, t_rect, border_radius=6)
            pygame.draw.rect(surface, t_border, t_rect, 2 if is_active else 1, border_radius=6)
            t_surf = font_mid.render(name, True, t_col)
            surface.blit(t_surf, (t_rect.centerx - t_surf.get_width() // 2, t_rect.centery - t_surf.get_height() // 2))

        # Dica sutil de rolagem (posicionada à direita das abas sem sobreposição)
        hint_txt = font_small.render(t("scroll_hint"), True, pm.INK_SOFT)
        surface.blit(hint_txt, (mx + mw - hint_txt.get_width() - 36, tab_y + 8))

        # Área de Conteúdo
        content_rect = pygame.Rect(mx + 36, my + 116, mw - 72, mh - 138)

        if self.current_tab == self.TAB_RULES:
            self._render_tab_rules(surface, content_rect, font_mid, font_small)
        elif self.current_tab == self.TAB_CONTROLS:
            self._render_tab_controls(surface, content_rect, font_mid, font_small)
        elif self.current_tab == self.TAB_FIGHTERS:
            self._render_tab_fighters(surface, content_rect, font_mid, font_small)

    def _render_tab_rules(self, surface: pygame.Surface, rect: pygame.Rect, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        # 3 Painéis temáticos anti-overflow com quebra automática de linha
        col_w = (rect.width - 24) // 3
        max_line_w = col_w - 24

        boxes = [
            (t("rules_box1_title"), pm.SEAL_RED, t("rules_box1_lines")),
            (t("rules_box2_title"), pm.GOLD_INK, t("rules_box2_lines")),
            (t("rules_box3_title"), pm.SEAL_BLUE, t("rules_box3_lines")),
        ]

        self.max_scroll = 0.0

        for i, (btitle, bcol, lines) in enumerate(boxes):
            bx = rect.x + i * (col_w + 12)
            b_rect = pygame.Rect(bx, rect.y, col_w, rect.height)
            pygame.draw.rect(surface, (234, 222, 198), b_rect, border_radius=8)
            pygame.draw.rect(surface, (160, 145, 125), b_rect, 1, border_radius=8)

            head_h = 36
            pygame.draw.rect(surface, (224, 210, 184), (bx, rect.y, col_w, head_h), border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.line(surface, (160, 145, 125), (bx, rect.y + head_h), (bx + col_w, rect.y + head_h), 1)
            t_surf = self._fit_text(font_mid, btitle, bcol, max_line_w)
            surface.blit(t_surf, (bx + 12, rect.y + 8))

            cur_y = rect.y + 44
            for raw_line in lines:
                if not raw_line:
                    cur_y += 7
                    continue
                is_bullet = raw_line.lstrip().startswith("•")
                col = pm.INK if is_bullet else pm.INK_SOFT
                indent = "   " if is_bullet else "  "
                wrapped = self._wrap_text(font_small, raw_line, max_line_w, indent=indent)
                for wline in wrapped:
                    l_surf = font_small.render(wline, True, col)
                    surface.blit(l_surf, (bx + 12, cur_y))
                    cur_y += 17

    def _render_tab_controls(self, surface: pygame.Surface, rect: pygame.Rect, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        half_w = (rect.width - 16) // 2
        max_line_w = half_w - 28

        # Painel Esquerdo: Controles P1 e P2
        p_left = pygame.Rect(rect.x, rect.y, half_w, rect.height)
        pygame.draw.rect(surface, (234, 222, 198), p_left, border_radius=8)
        pygame.draw.rect(surface, (160, 145, 125), p_left, 1, border_radius=8)

        t1 = self._fit_text(font_mid, t("ctrl_p1_title"), pm.SEAL_RED, max_line_w)
        surface.blit(t1, (p_left.x + 14, p_left.y + 12))

        cy = p_left.y + 44
        color_map = {
            "header": pm.SEAL_RED,
            "header2": pm.SEAL_BLUE,
            "body": pm.INK,
            "body_e": (160, 42, 38),
            "body_r": (160, 42, 38),
            "tip": pm.GOLD_INK,
            "body_dim": pm.INK_SOFT,
            "sep": (0, 0, 0),
        }
        for text, style in t("ctrl_p1_lines"):
            if not text:
                cy += 8
                continue
            col = color_map.get(style, pm.INK)
            wrapped = self._wrap_text(font_small, text, max_line_w, indent="    ")
            for wline in wrapped:
                s = font_small.render(wline, True, col)
                surface.blit(s, (p_left.x + 14, cy))
                cy += 18

        # Painel Direito: Atalhos do Sistema
        p_right = pygame.Rect(rect.x + half_w + 16, rect.y, half_w, rect.height)
        pygame.draw.rect(surface, (234, 222, 198), p_right, border_radius=8)
        pygame.draw.rect(surface, (160, 145, 125), p_right, 1, border_radius=8)

        t2 = self._fit_text(font_mid, t("ctrl_p2_title"), pm.GOLD_INK, max_line_w)
        surface.blit(t2, (p_right.x + 14, p_right.y + 12))

        color_map2 = {
            "key": pm.GOLD_INK,
            "key_action": pm.SEAL_RED,
            "body": pm.INK,
            "body_dim": pm.INK_SOFT,
            "sep": (0, 0, 0),
        }
        cy = p_right.y + 44
        for text, style in t("ctrl_p2_lines"):
            if not text:
                cy += 8
                continue
            col = color_map2.get(style, pm.INK)
            wrapped = self._wrap_text(font_small, text, max_line_w, indent="    ")
            for wline in wrapped:
                s = font_small.render(wline, True, col)
                surface.blit(s, (p_right.x + 14, cy))
                cy += 18

    def _render_tab_fighters(self, surface: pygame.Surface, rect: pygame.Rect, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        lang = get_lang()

        # 1. Carrossel em 2 Linhas de Botões de Guerreiros no topo (evita overflow em elencos grandes)
        num_f = len(FIGHTERS_GUIDE_DATA)
        row0_count = (num_f + 1) // 2
        row1_count = num_f - row0_count
        gap = 5
        btn_h = 22
        btn_w0 = (rect.width - (row0_count - 1) * gap) // row0_count
        btn_w1 = (rect.width - (row1_count - 1) * gap) // row1_count

        self.fighter_tab_rects.clear()
        for i, fdata in enumerate(FIGHTERS_GUIDE_DATA):
            if i < row0_count:
                bx = rect.x + i * (btn_w0 + gap)
                by = rect.y
                bw = btn_w0
            else:
                col_idx = i - row0_count
                bx = rect.x + col_idx * (btn_w1 + gap)
                by = rect.y + btn_h + 3
                bw = btn_w1

            b_rect = pygame.Rect(bx, by, bw, btn_h)
            self.fighter_tab_rects.append(b_rect)

            is_cur = (self.selected_fighter_idx == i)
            bg_col = (238, 226, 202) if is_cur else (224, 210, 184)
            border_col = fdata["color"] if is_cur else (160, 145, 125)

            pygame.draw.rect(surface, bg_col, b_rect, border_radius=4)
            pygame.draw.rect(surface, border_col, b_rect, 2 if is_cur else 1, border_radius=4)

            short_name = fdata[lang]["name"]
            txt_col = fdata["color"] if is_cur else pm.INK_SOFT
            n_surf = self._fit_text(font_small, short_name, txt_col, bw - 6)
            surface.blit(n_surf, (b_rect.centerx - n_surf.get_width() // 2, b_rect.centery - n_surf.get_height() // 2))

        # 2. Painel Central da Ficha do Combatente Escolhido
        cur_fighter = FIGHTERS_GUIDE_DATA[self.selected_fighter_idx]
        cur_data = cur_fighter[lang]
        detail_y = rect.y + (btn_h * 2 + 8)
        detail_h = rect.height - (btn_h * 2 + 8)
        detail_rect = pygame.Rect(rect.x, detail_y, rect.width, detail_h)

        pygame.draw.rect(surface, (234, 222, 198), detail_rect, border_radius=8)
        pygame.draw.rect(surface, cur_fighter["color"], detail_rect, 2, border_radius=8)

        # Coluna Esquerda: Retrato Voxel 3D e Dados Básicos (largura 310px)
        left_col_w = 310
        portrait_cx = detail_rect.x + 48
        portrait_cy = detail_y + 44

        # Moldura circular e Retrato de Busto HD-2D do guerreiro
        pygame.draw.circle(surface, (218, 204, 178), (portrait_cx, portrait_cy), 36)
        pygame.draw.circle(surface, cur_fighter["color"], (portrait_cx, portrait_cy), 36, 2)

        p_size = (68, 68)
        p_surf = get_portrait(cur_fighter["id"], size=p_size, circular=True)
        if p_surf is not None:
            surface.blit(p_surf, (portrait_cx - p_size[0] // 2, portrait_cy - p_size[1] // 2))
        else:
            # Fallback para o render Voxel do guerreiro
            cam = HelpPreviewCam(portrait_cx, portrait_cy + 16)
            c_type = cur_fighter["char_type"]
            if c_type == "american_ninja":
                render_voxel_humanoid(surface, cam, -0.20, 0, 0, 0.9, 0.0, "IDLE", 0.0, True, char_type=c_type)
                render_voxel_doberman(surface, cam, 0.35, -0.10, 0, 0.9, 0.0, "IDLE", 0.0, True)
            elif c_type == "yellow_ninja":
                render_voxel_humanoid(surface, cam, 0, 0, 0, 0.9, 0.0, "IDLE", 0.0, True, char_type=c_type, extra_props={"has_kunai": True})
            else:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 0.9, 0.0, "IDLE", 0.0, True, char_type=c_type)

        # Nome, Título e Estilo com proteção contra overflow
        text_x = detail_rect.x + 92
        max_title_w = left_col_w - 92 - 10
        n_surf = self._fit_text(font_mid, cur_data["name"], cur_fighter["color"], max_title_w)
        t_surf = self._fit_text(font_small, cur_data["title"], pm.INK, max_title_w)
        s_surf = self._fit_text(font_small, cur_data["style"], pm.GOLD_INK, max_title_w)

        surface.blit(n_surf, (text_x, detail_y + 12))
        surface.blit(t_surf, (text_x, detail_y + 36))
        surface.blit(s_surf, (text_x, detail_y + 56))

        # Atributos e Teclas com quebra automática de linha
        stat_y = detail_y + 88
        pygame.draw.line(surface, (175, 160, 140), (detail_rect.x + 14, stat_y), (detail_rect.x + left_col_w, stat_y), 1)

        stat_max_w = left_col_w - 28
        stat_items = [
            (f"{t('stat_speed')} {cur_data['vel']}", pm.INK),
            (f"{t('stat_damage')} {cur_data['dano']}", pm.INK),
            (f"{t('stat_special')} {cur_data['especial']}", pm.INK),
            ("", None),
            (cur_data["keys_p1"], pm.SEAL_RED),
            (cur_data["keys_p2"], pm.SEAL_RED),
        ]
        sy = stat_y + 6
        for sl, col in stat_items:
            if not sl:
                sy += 6
                continue
            is_key = sl.startswith("[")
            indent = "  " if not is_key else ""
            wrapped = self._wrap_text(font_small, sl, stat_max_w, indent=indent)
            for wline in wrapped:
                s_s = font_small.render(wline, True, col)
                surface.blit(s_s, (detail_rect.x + 14, sy))
                sy += 16

        # Botões Anterior / Próximo na base da coluna esquerda
        btn_nav_y = detail_rect.bottom - 40
        self.prev_fighter_btn = pygame.Rect(detail_rect.x + 14, btn_nav_y, 134, 30)
        self.next_fighter_btn = pygame.Rect(detail_rect.x + 158, btn_nav_y, 134, 30)

        pygame.draw.rect(surface, (224, 210, 184), self.prev_fighter_btn, border_radius=6)
        pygame.draw.rect(surface, (160, 145, 125), self.prev_fighter_btn, 1, border_radius=6)
        prev_lbl = self._fit_text(font_small, t("btn_prev"), pm.INK, 124)
        surface.blit(prev_lbl, (self.prev_fighter_btn.centerx - prev_lbl.get_width() // 2, self.prev_fighter_btn.centery - prev_lbl.get_height() // 2))

        pygame.draw.rect(surface, (224, 210, 184), self.next_fighter_btn, border_radius=6)
        pygame.draw.rect(surface, (160, 145, 125), self.next_fighter_btn, 1, border_radius=6)
        next_lbl = self._fit_text(font_small, t("btn_next"), pm.INK, 124)
        surface.blit(next_lbl, (self.next_fighter_btn.centerx - next_lbl.get_width() // 2, self.next_fighter_btn.centery - next_lbl.get_height() // 2))

        # Divisória vertical
        sep_x = detail_rect.x + left_col_w + 12
        pygame.draw.line(surface, (175, 160, 140), (sep_x, detail_y + 12), (sep_x, detail_rect.bottom - 12), 1)

        # Coluna Direita: Sub-filtros e Conteúdo Estratégico com Rolagem Anti-Overflow
        right_x = sep_x + 14
        right_w = detail_rect.right - right_x - 16

        # 3. Pílulas de Sub-seção no topo da coluna direita (dimensões proporcionais para não vazar)
        if lang == LANG_PT:
            sub_labels = ["TODOS", "CONCEITO", "ARSENAL", "COMO JOGAR", "COMO VENCER"]
        else:
            sub_labels = ["ALL", "CONCEPT", "ARSENAL", "HOW TO PLAY", "HOW TO COUNTER"]
        num_subs = len(sub_labels)
        sub_gap = 8
        sub_w = (right_w - (num_subs - 1) * sub_gap) // num_subs
        sub_h = 24
        sub_y = detail_y + 10

        self.sub_sec_btn_rects.clear()
        for s_idx, s_lbl in enumerate(sub_labels):
            sb_rect = pygame.Rect(right_x + s_idx * (sub_w + sub_gap), sub_y, sub_w, sub_h)
            self.sub_sec_btn_rects.append(sb_rect)
            is_active_sub = (self.fighter_sub_section == s_idx)
            s_bg = (238, 226, 202) if is_active_sub else (224, 210, 184)
            s_bcol = pm.SEAL_RED if is_active_sub else (160, 145, 125)
            pygame.draw.rect(surface, s_bg, sb_rect, border_radius=4)
            pygame.draw.rect(surface, s_bcol, sb_rect, 2 if is_active_sub else 1, border_radius=4)
            s_txt = self._fit_text(font_small, s_lbl, pm.SEAL_RED if is_active_sub else pm.INK, sub_w - 6)
            surface.blit(s_txt, (sb_rect.centerx - s_txt.get_width() // 2, sb_rect.centery - s_txt.get_height() // 2))

        # Seções de Conteúdo a serem exibidas
        all_sections = [
            (t("sec_concept"), pm.SEAL_RED, cur_data["conceito"], self.SEC_CONCEPT),
            (t("sec_arsenal"), pm.GOLD_INK, cur_data["habilidades"], self.SEC_ARSENAL),
            (t("sec_offense"), pm.SEAL_BLUE, cur_data["estrategia_ofensiva"], self.SEC_OFFENSE),
            (t("sec_defense"), (160, 42, 38), cur_data["estrategia_defensiva"], self.SEC_DEFENSE)
        ]

        if self.fighter_sub_section == self.SEC_ALL:
            active_sections = all_sections
        else:
            active_sections = [s for s in all_sections if s[3] == self.fighter_sub_section]

        # Janela com Clipping e Rolagem Vertical Suave
        clip_top = sub_y + sub_h + 8
        clip_h = detail_rect.bottom - clip_top - 12
        clip_rect = pygame.Rect(right_x, clip_top, right_w, clip_h)

        # Cálculo do total de altura necessário com quebra de linha precisa
        text_w = right_w - 20  # Reserva espaço para a barra de rolagem
        total_content_height = 0
        layout_blocks = []

        for sec_title, sec_color, sec_text, _ in active_sections:
            block_lines = [("title", sec_title, sec_color)]
            for rline in sec_text.split("\n"):
                indent = "  " if rline.lstrip().startswith("•") else ""
                wrapped = self._wrap_text(font_small, rline, text_w, indent=indent)
                for wline in wrapped:
                    block_lines.append(("line", wline, pm.INK))
            layout_blocks.append(block_lines)

        for blk in layout_blocks:
            total_content_height += 24  # Título
            for item in blk[1:]:
                total_content_height += 18
            total_content_height += 12  # Espaçamento entre seções

        # Atualizar max_scroll
        self.max_scroll = max(0.0, total_content_height - clip_h)
        self.scroll_y = max(0.0, min(self.max_scroll, self.scroll_y))

        # Renderizar com Clipping
        surface.set_clip(clip_rect)
        draw_y = clip_top - int(self.scroll_y)

        for blk in layout_blocks:
            for item_type, itext, icol in blk:
                if item_type == "title":
                    t_s = self._fit_text(font_mid, itext, icol, text_w)
                    surface.blit(t_s, (right_x, draw_y))
                    draw_y += 24
                else:
                    l_surf = font_small.render(itext, True, icol)
                    surface.blit(l_surf, (right_x + 8, draw_y))
                    draw_y += 18
            draw_y += 12

        # Resetar clipping
        surface.set_clip(None)

        # 4. Barra de Rolagem Visual Estilizada (quando houver conteúdo excedente)
        if self.max_scroll > 0.0:
            track_x = right_x + right_w - 8
            track_y = clip_top
            track_h = clip_h
            pygame.draw.rect(surface, (215, 202, 178), (track_x, track_y, 6, track_h), border_radius=3)

            # Cálculo do polegar da barra de rolagem (Thumb)
            thumb_ratio = max(0.15, clip_h / (clip_h + self.max_scroll))
            thumb_h = int(track_h * thumb_ratio)
            thumb_pos = int((track_h - thumb_h) * (self.scroll_y / self.max_scroll))
            thumb_y = track_y + thumb_pos

            pygame.draw.rect(surface, pm.SEAL_RED, (track_x, thumb_y, 6, thumb_h), border_radius=3)
