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
                "• Cross Guard Parry [R]: Ergue ambas as lâminas cruzadas em X (0.28s de parry frontal). Se defletir um golpe, libera o punitivo Cross Shockwave.\n"
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
                "• Cross Guard Parry [R]: Crosses dual blades frontally (0.28s parry window). Deflecting an attack arms the punishing Cross Shockwave.\n"
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
            "title": "Mestre Ashigaru da Pólvora Tanegashima",
            "style": "Tanegashima-jutsu (Balística & Infantaria Feudal)",
            "vel": "[3.8/5] Veterano Tático & Cadência",
            "dano": "Tiro Fatal (1-Hit Kill) / Coronhada Stun (0.65s)",
            "especial": "Mina de Pólvora Negra / Trench Dive",
            "keys_p1": "[E] Tiro / Coronhada | [R] Mina | [T] Trench Dive",
            "keys_p2": "[U] Tiro / Coronhada | [I] Mina | [O] Trench Dive",
            "conceito": (
                "Veterano soldado ashigaru com armadura Dō com rebites, Jingasa laqueada com brasão Tonbo e bandoleira de tubos hayago. "
                "Empunha um pesado arcabuz Tanegashima capaz de liquidar qualquer samurai à distância e controla o campo com minas de pólvora negra."
            ),
            "habilidades": (
                "• Tiro de Arcabuz [E / Ataque]: Disparo supersônico balístico a 26 m/s com 1-Hit Kill fatal. Recarga automática fluida por vareta (ramrod).\n"
                "• Coronhada de Carvalho [E / sem bala]: Golpe pesado com a coronha que atordoa o rival por 0.65s e o arremessa 1.8m para trás.\n"
                "• Mina de Pólvora Negra [R / Secundário]: Deposita uma carga de pólvora no solo que detona ao contato, bloqueando investidas de espadachins.\n"
                "• Trench Ashigaru Dive [T / Esquiva]: Mergulho rústico rasante com i-frames completos que conclui a recarga do arcabuz ao levantar."
            ),
            "estrategia_ofensiva": (
                "• Teppo já começa o round CARREGADO com bala na agulha! Alinhe a mira e aguarde a queima da mecha para o disparo mortal.\n"
                "• Plante a Mina de Pólvora [R] para criar um gargalo tático que pune aproximações em linha reta (como o Gatotsu de Saitou e Shukuchi de Kenshi).\n"
                "• Se errar o tiro ou for encurralado, desfira a Coronhada [E] para afastar o rival e execute o Trench Dive [T] para recarregar imediatamente."
            ),
            "estrategia_defensiva": (
                "• Como vencer Teppo: Cuidado com o brilho da brasa na ponta do cano durante a mira — use a esquiva direcional no timing exato da fumaça! "
                "Cuidado ao saltar cegamente sobre o solo minado; force-o a gastar a munição e pressione-o enquanto ele puxa a vareta de ferro."
            )
        },
        "en": {
            "name": "TEPPO",
            "title": "Ashigaru Matchlock Master",
            "style": "Tanegashima-jutsu (Feudal Ballistics & Gunpowder)",
            "vel": "[3.8/5] Tactical Veteran & Cadence",
            "dano": "Fatal Shot (1-Hit Kill) / Butt Stun (0.65s)",
            "especial": "Black Powder Ground Trap / Trench Dive",
            "keys_p1": "[E] Shoot / Rifle Butt | [R] Trap | [T] Trench Dive",
            "keys_p2": "[U] Shoot / Rifle Butt | [I] Trap | [O] Trench Dive",
            "conceito": (
                "Veteran Ashigaru soldier clad in riveted Dō cuirass, lacquered Tonbo Jingasa and hayago bamboo bandolier. "
                "Wields an authentic Tanegashima matchlock rifle capable of dropping any samurai at range, dominating space with explosive powder traps."
            ),
            "habilidades": (
                "• Matchlock Shot [E / Attack]: Supersonic 26 m/s ballistic bullet with 1-Hit Kill fatality. Fluid automatic ramrod reload.\n"
                "• Oak Rifle Butt [E / unloaded]: Heavy blunt smash that stuns the opponent for 0.65s and knocks them back 1.8m.\n"
                "• Black Powder Ground Trap [R / Secondary]: Deploys a volatile powder charge on the ground that detonates on contact, shutting down rushes.\n"
                "• Trench Ashigaru Dive [T / Dodge]: Prone tactical dive with full i-frames that automatically chambers a new bullet upon rising."
            ),
            "estrategia_ofensiva": (
                "• Teppo starts each round FULLY LOADED! Align your sights and let the match cord trigger the deadly shot.\n"
                "• Plant Ground Traps [R] to establish zoning choke points that punish aggressive dashers (like Saitou's Gatotsu or Kenshi's Shukuchi).\n"
                "• If crowded or out of ammo, strike with the Oak Rifle Butt [E] to create breathing room and Trench Dive [T] to reload instantly."
            ),
            "estrategia_defensiva": (
                "• How to defeat Teppo: Watch for the glowing match spark on his barrel during aim — time your dodge precisely as smoke erupts! "
                "Steer clear of glowing ground canisters; bait his shot and close the gap while he pumps the iron ramrod."
            )
        }
    },
    {
        "id": CHAR_PURPLE,
        "color": COLOR_PURPLE_AURA,
        "char_type": "murasaki",
        "pt": {
            "name": "MURASAKI",
            "title": "Kunoichi da Kusarigama",
            "style": "Kusarigamajutsu (Foice & Corrente)",
            "vel": "[5/5] Acrobática e Letal",
            "dano": "Kama Strike (1.30m) & Chain Drag (1 HP)",
            "especial": "Chain Drag & Chain Whirl Backflip",
            "keys_p1": "[E] Golpe de Foice (Ataque)",
            "keys_p2": "[R] Chain Drag (Especial)",
            "conceito": (
                "Kunoichi acrobática que domina a Kusarigama: foice curva Kama de aço carbono e corrente de ferro "
                "com peso esférico Fundo. Combina controle de espaço a 3.80m com golpes fatais à queima-roupa."
            ),
            "habilidades": (
                "• Golpe de Foice (Kama Strike) [E]: Golpe cortante rápido com 1.30m de alcance e precedência de combate.\n"
                "• Chain Drag [R]: Arremessa a corrente (3.80m); ao acertar, causa 1 de dano, aplica 0.45s de stun e arrasta o rival. Fatal se o rival tiver 1 HP!\n"
                "• Chain Whirl Backflip [Esquiva]: Salto mortal 360° com escudo giratório de corrente que deflete e destrói projéteis leves."
            ),
            "estrategia_ofensiva": (
                "• Domínio de Zona: Use o Chain Drag [R] a média distância para arrastar o oponente ou executá-lo diretamente caso esteja com 1 HP.\n"
                "• Na curta distância, o Kama Strike [E] corta com velocidade extrema e vence trocas diretas.\n"
                "• Use o Chain Whirl Backflip para saltar por cima de ataques e anular projéteis inimigos em pleno ar."
            ),
            "estrategia_defensiva": (
                "• Como vencer Murasaki: O Chain Drag possui tempo de retorno ao errar; ataque no vácuo de recuperação da corrente.\n"
                "• Dê parry na corrente para fazê-la retrair imediatamente, e evite trocar golpes frontais com a foice."
            )
        },
        "en": {
            "name": "MURASAKI",
            "title": "Kusarigama Kunoichi",
            "style": "Kusarigamajutsu (Chain & Sickle)",
            "vel": "[5/5] Acrobatic & Lethal",
            "dano": "Kama Strike (1.30m) & Chain Drag (1 HP)",
            "especial": "Chain Drag & Chain Whirl Backflip",
            "keys_p1": "[E] Kama Sickle Slash (Attack)",
            "keys_p2": "[R] Chain Drag (Special)",
            "conceito": (
                "Deadly acrobatic kunoichi wielding the Kusarigama: a high-carbon steel Kama sickle linked to a heavy "
                "iron chain with spherical weight. Controls the battlefield at 3.80m and executes at point-blank."
            ),
            "habilidades": (
                "• Kama Strike [E]: Fast sickle slash with 1.30m reach and combat precedence.\n"
                "• Chain Drag [R]: Flings the chain weight (3.80m); deals 1 damage, 0.45s stun, and drags foe to melee. Fatal if foe has 1 HP!\n"
                "• Chain Whirl Backflip [Dodge]: 360° somersault with vertical spinning chain shield that deflects/destroys light projectiles."
            ),
            "estrategia_ofensiva": (
                "• Zone Control: Hook foes from 3.80m with Chain Drag [R] to reel them in or execute them when at 1 HP.\n"
                "• At close range, Kama Strike [E] delivers swift slashes with top priority in direct exchanges.\n"
                "• Utilize Chain Whirl Backflip to leap over low swipes and obliterate incoming projectiles."
            ),
            "estrategia_defensiva": (
                "• How to defeat Murasaki: Whiffed chain drags leave her vulnerable during retraction; punish from the flank.\n"
                "• Parry the incoming chain to force an instant retraction and avoid head-on clashes with the Kama."
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
            "style": "Névoa, Adaga Tanto, Pólvora & Minas",
            "vel": "[5/5] Ágil, Furtiva e Acrobática",
            "dano": "Adaga Melee (2 Dano) + Bomba Horoku + Mina Remota",
            "especial": "Mina Remota & Rolo de Fumaça",
            "keys_p1": "[E] Adaga Tanto / Bomba Horoku (Híbrido)",
            "keys_p2": "[R] Mina Remota (Planta / Detona)",
            "conceito": (
                "Sabotadora e ilusionista das sombras, mestra em misturas pirotécnicas e combate furtivo com Tanto. "
                "Transforma a arena em um campo minado caótico de fumaça, chamas e detonações cirúrgicas."
            ),
            "habilidades": (
                "• Sistema Híbrido [E]: Corte relâmpago de adaga Tanto à queima-roupa (alcance 1.20m, 2 de dano, clash prioritário); à distância (>1.6m), lança bomba Horoku em arco 3D parabólico (limite de 1 ativa, recarga de 2.0s; golpes durante a recarga utilizam a adaga Tanto).\n"
                "• Mina de Detonação Remota [R]: 1º toque planta a mina no solo; 2º toque detona remotamente num raio de 2.2m (2 de dano). Não suicida se Kasumi tiver 1 HP.\n"
                "• Esquiva Furtiva: Rolo ninja acrobático que liberta um tapete de fumaça espesso e concede camuflagem (alpha=15)."
            ),
            "estrategia_ofensiva": (
                "• Use a adaga Tanto em combates próximos para superar espadas longas antes do recuo.\n"
                "• Plante a mina remota [R] em pontos de afunilamento e detone assim que o rival passar.\n"
                "• Combine o rolo de fumaça com arremessos de Horoku para manter o oponente desorientado."
            ),
            "estrategia_defensiva": (
                "• Como vencer Kasumi: Fique atento ao solo para não pisar na mina remota ativa. "
                "Pressione-a em meia distância onde a bomba Horoku demora a cair e a adaga não alcança."
            )
        },
        "en": {
            "name": "KASUMI",
            "title": "Mist Kunoichi",
            "style": "Mist, Tanto Dagger, Horoku Bombs & Mines",
            "vel": "[5/5] Agile, Stealthy & Acrobatic",
            "dano": "Melee Tanto (2 Dmg) + Horoku Bomb + Remote Mine",
            "especial": "Remote Mine & Smoke Roll",
            "keys_p1": "[E] Tanto Dagger / Horoku Bomb (Hybrid)",
            "keys_p2": "[R] Remote Mine (Plant / Detonate)",
            "conceito": (
                "Shadow saboteur and illusionist, master of pyrotechnic blends and lethal close-quarters Tanto strikes. "
                "Transforms the arena into a chaotic minefield of smoke, sparks, and precision detonations."
            ),
            "habilidades": (
                "• Hybrid Strike [E]: Swift point-blank Tanto dagger slash (1.20m range, 2 damage, high priority clash); at distance (>1.6m), hurls a parabolic 3D Horoku ceramic bomb (max 1 active bomb, 2.0s cooldown; strikes during cooldown use the Tanto dagger).\n"
                "• Remote Detonation Mine [R]: 1st press plants mine into the ground; 2nd press detonates remotely within 2.2m radius (2 damage). Kasumi is immune to lethal self-damage at 1 HP.\n"
                "• Smoke Roll: Agile ninja roll that drops dense volumetric smoke and provides stealth concealment (alpha=15)."
            ),
            "estrategia_ofensiva": (
                "• Use the Tanto dagger in close quarters to intercept longer weapons before their recovery.\n"
                "• Plant remote mines [R] in chokepoints and detonate the instant the opponent enters the radius.\n"
                "• Chain the smoke roll with Horoku bomb tosses to strike from hidden angles."
            ),
            "estrategia_defensiva": (
                "• How to defeat Kasumi: Watch the ground carefully for armed remote mines. "
                "Engage at mid-range where Horoku bombs take time to arc down and the Tanto dagger cannot reach."
            )
        }
    },
    {
        "id": CHAR_KABUKI,
        "color": (240, 115, 30),
        "char_type": "okuni",
        "pt": {
            "name": "OKUNI",
            "title": "Dançarina Kabuki dos Leques de Aço",
            "style": "Tessen-jutsu & Névoa Dokukiri",
            "vel": "[4/5] Acrobata Teatral Ágil",
            "dano": "Leques Tessen (Dano 2) / Dokukiri Stun",
            "especial": "Finta Kawarimi & Sopro Dokukiri",
            "keys_p1": "[J] Leques Tessen  [K] Dokukiri  [L] Kawarimi",
            "keys_p2": "[1] Leques Tessen  [2] Dokukiri  [3] Kawarimi",
            "conceito": (
                "Inspirada em Izumo no Okuni, pioneira do teatro Kabuki. Combina combate corpo a corpo elegante "
                "com leques de lâminas de ferro afiadas (Tessen), sopro venenoso Dokukiri que repele e atordoa "
                "adversários, e piruetas teatrais com manequim de seda (Kawarimi Decoy)."
            ),
            "habilidades": (
                "• Dança dos Leques [Ataque]: Golpe duplo veloz e cortante com leques de ferro (1.45m de alcance, Dano 2 letal).\n"
                "• Sopro Dokukiri [Secundário]: Exala névoa cáustica em cone frontal (3.0m) que repele o rival (1.6m), "
                "causa tosse e Whiff Stun (0.8s) e aplica debuff de lentidão (-25% SPD).\n"
                "• Finta Kawarimi [Esquiva]: Pirueta evasiva rápida com i-frames que deixa um manequim de seda. "
                "Se o rival golpear a ilusão, sofre whiff punish de 0.45s!"
            ),
            "estrategia_ofensiva": (
                "• Controle o ritmo com o Sopro Dokukiri para repelir o rival e aplicar o stun de tosse de 0.8s.\n"
                "• Avance imediatamente durante o stun com a Dança dos Leques Tessen para uma execução limpa!\n"
                "• Em situações de pressão adversária, ative a Finta Kawarimi para induzir o oponente ao erro e punir severamente."
            ),
            "estrategia_defensiva": (
                "• Como vencer Okuni: Fique atento ao sopro roxo/verde de Dokukiri e mantenha esquivas laterais para "
                "não ser pego pelo cone frontal. Nunca ataque o manequim de seda recém-deixado após a pirueta, "
                "sob risco de stun punitivo."
            )
        },
        "en": {
            "name": "OKUNI",
            "title": "Kabuki Iron Fan Dancer",
            "style": "Tessen-jutsu & Dokukiri Mist",
            "vel": "[4/5] Agile Theatrical Acrobat",
            "dano": "Tessen Fans (2 Damage) / Dokukiri Stun",
            "especial": "Kawarimi Feint & Dokukiri Breath",
            "keys_p1": "[J] Tessen Fans  [K] Dokukiri  [L] Kawarimi",
            "keys_p2": "[1] Tessen Fans  [2] Dokukiri  [3] Kawarimi",
            "conceito": (
                "Inspired by Izumo no Okuni, founder of Kabuki theatre. Blends graceful melee combat using "
                "razor-sharp iron war fans (Tessen), toxic Dokukiri breath that knocks back and stuns rivals, "
                "and elusive silk mannequin substitution feints (Kawarimi Decoy)."
            ),
            "habilidades": (
                "• Tessen Fan Dance [Attack]: Swift, lethal double slash with iron war fans (1.45m range, 2 damage).\n"
                "• Dokukiri Breath [Secondary]: Exhales a caustic mist in a 3.0m frontal cone, pushing foes back (1.6m), "
                "inflicting cough Whiff Stun (0.8s) and a -25% SPD slow debuff.\n"
                "• Kawarimi Feint [Dodge]: Rapid evasive pirouette with i-frames, leaving a silk decoy behind. "
                "If struck by the enemy, it inflicts a punishing 0.45s stun!"
            ),
            "estrategia_ofensiva": (
                "• Dictate spacing using Dokukiri Breath to repel incoming rushdowns and trigger the 0.8s cough stun.\n"
                "• Close the distance during the stun window and execute with the lethal Tessen Fan Dance!\n"
                "• Bait aggressive opponents into striking your Kawarimi silk decoy for an easy whiff punish."
            ),
            "estrategia_defensiva": (
                "• How to defeat Okuni: Circle laterally to avoid the frontal Dokukiri cone. Never commit attacks into "
                "the newly spawned silk decoy after her dodge pirouette to avoid severe whiff stuns."
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
            "style": "Kyudo Sagrado & Flechas Hamaya",
            "vel": "[4/5] Ágil e Concentrada",
            "dano": "Flecha Yumi Fatal (Alcance Máximo)",
            "especial": "Chuva Sagrada (Disparo em Arco)",
            "keys_p1": "[E] Retesar e Atirar (Ataque)",
            "keys_p2": "[R] Chuva Sagrada (Especial)",
            "conceito": (
                "Sacerdotisa miko do santuário nas montanhas, mestre na arte marcial meditativa do arco e flecha (Kyudo). "
                "Sua presença transmite serenidade, foco inabalável e disparos mortais milimétricos com o grande arco Yumi."
            ),
            "habilidades": (
                "• Disparo Yumi [E]: Disparo direto e veloz de flecha Ya perfurante com rastro visível. Colide com obstáculos sólidos do cenário e pode ser evitado por esquivas com i-frames (1-Hit Kill).\n"
                "• Chuva Sagrada em Arco [R]: Lança uma salva de flechas sagradas Hamaya aos céus que desce em arco parabólico sobre a área visada causando dano letal (Cooldown: 3.0s).\n"
                "• Flecha de Corda & Miko Roll [Esquiva]: Hold & Release para disparar flecha de corda e se puxar pelo mapa. Caso a corda esteja em recarga (2.0s), executa um mergulho ágil ao chão com 12 i-frames.\n"
                "• Fatalidades: Jifuu Kyoukyuu (地縫強弓 - Flecha cravada na garganta pregando o rival ao solo com fonte de sangue arterial) & Hama Tenkan (破魔天貫 - Salva purificadora que desce do zênite celestial)."
            ),
            "estrategia_ofensiva": (
                "• Mantenha a maior distância possível do inimigo; seu arco tem alcance superior a qualquer espada.\n"
                "• Use os obstáculos sólidos do mapa como proteção; posicione-se para alvejar o adversário quando ele contornar cercas ou rochas.\n"
                "• Use a Chuva Sagrada em Arco [R] para punir inimigos que se escondem atrás de barricadas intransponíveis."
            ),
            "estrategia_defensiva": (
                "• Como vencer Tomoe: As flechas retilíneas colidem com árvores, pedras e cercas. Aproxime-se "
                "em zigue-zague ou use esquivas ágeis durante o voo da flecha para aproveitar os i-frames."
            )
        },
        "en": {
            "name": "TOMOE",
            "title": "Shrine Maiden Archer",
            "style": "Sacred Kyudo & Hamaya Volley",
            "vel": "[4/5] Calm & Focused",
            "dano": "Fatal Yumi Arrow (Max Range)",
            "especial": "Sacred Arrow Volley (Sky Arch)",
            "keys_p1": "[E] Draw & Release (Attack)",
            "keys_p2": "[R] Sacred Volley (Special)",
            "conceito": (
                "Mountain shrine maiden master of the meditative martial art of Japanese archery (Kyudo). "
                "Radiates serene focus, unshakable patience, and pinpoint lethal arrows with the asymmetric Yumi bow."
            ),
            "habilidades": (
                "• Yumi Bow Shot [E]: Direct high-velocity Ya arrow with visible aerodynamic slipstream. Collides with solid obstacles and is dodgeable with i-frames (1-Hit Kill).\n"
                "• Sacred Volley [R]: Arcs multiple sacred Hamaya arrows into the zenith, descending upon target ground coordinates with lethal impact (Cooldown: 3.0s).\n"
                "• Rope Arrow & Miko Roll [Dodge]: Hold & Release to launch a rope arrow and zip across the map. When rope is on cooldown (2.0s), performs a standard evasive ground dive with 12 i-frames.\n"
                "• Fatalities: Jifuu Kyoukyuu (地縫強弓 - Pinned to Earth by Yumi arrow through throat with arterial blood fountain) & Hama Tenkan (破魔天貫 - Zenith holy arrow cleave)."
            ),
            "estrategia_ofensiva": (
                "• Maintain maximum distance; your Yumi bow out-ranges any sword.\n"
                "• Leverage arena obstacles as cover; draw while shielded and loose the arrow as enemies emerge.\n"
                "• Use Sacred Volley [R] to lob celestial arrows over fences and barricades when enemies turtle behind solid terrain."
            ),
            "estrategia_defensiva": (
                "• How to defeat Tomoe: Direct arrows stop against trees, lanterns, and hedges. Advance "
                "behind solid props or time your dodge rolls to phase through incoming arrows using i-frames."
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
            "style": "Alfanje Bucaneiro & Bombardeio Naval Celeste",
            "vel": "[4/5] Robusta e Rápida",
            "dano": "Cutlass Cleave 180° (1.65m / 2 HP)",
            "especial": "Bombardeio Naval Orbital & Pólvora Negra",
            "keys_p1": "[E] Cutlass Cleave 180° (Ataque)",
            "keys_p2": "[R] Bombardeio Naval (Segure e Solte)",
            "conceito": (
                "Pirata destemida acostumada a motins, abordagens navais e duelos impiedosos. "
                "Combina a força bruta de seu alfanje curvo de 180° com bombardeios de artilharia naval celestial e fuligem de pólvora."
            ),
            "habilidades": (
                "• Cutlass Cleave 180° [E]: Arco amplo frontal e lateral de 1.65m com lunge de 0.65m e 2 de dano.\n"
                "• Bombardeio Naval [R]: Astrolábio isométrico vindo dos céus. Segure [R] para guiar o retículo e solte para disparar uma bala de canhão orbital devastadora.\n"
                "• Rolamento com Pólvora [T]: Esquiva pesada com 12 i-frames que solta fuligem espessa no solo, causando lentidão no rival.\n"
                "• Fatalities: Aranami Ryoudan (荒波両断 - Bissecção diagonal do alfanje) e Kanpou Senmetsu (艦砲殲滅 - Impacto orbital do canhão)."
            ),
            "estrategia_ofensiva": (
                "• Use o avanço vigoroso do Cutlass Cleave [E] para atropelar tentativas de esquiva lateral rasa.\n"
                "• Force o adversário a se mover sob a mira do Bombardeio Naval [R] e corte-o na aproximação!\n"
                "• Deixe a fuligem da pólvora [T] no chão para reduzir a velocidade do adversário."
            ),
            "estrategia_defensiva": (
                "• Como vencer Anne: Ao ver a mira dourada do canhão no chão, saia imediatamente da área. Ataque nos momentos de recuperação pós-golpe do alfanje com golpes rápidos ou projéteis."
            )
        },
        "en": {
            "name": "ANNE",
            "title": "Wolf of the High Seas",
            "style": "Buccaneer Cutlass & Celestial Naval Bombardment",
            "vel": "[4/5] Heavy & Fast",
            "dano": "180° Cutlass Cleave (1.65m / 2 HP)",
            "especial": "Orbital Cannonball Strike & Black Powder Dash",
            "keys_p1": "[E] Cutlass Cleave 180° (Attack)",
            "keys_p2": "[R] Naval Artillery (Hold & Release)",
            "conceito": (
                "Fearless pirate captain forged in boarding skirmishes and naval battles. "
                "Combines heavy 180° cutlass cleaves with devastating celestial cannonball strikes and blinding powder soot."
            ),
            "habilidades": (
                "• Cutlass Cleave 180° [E]: Wide 180-degree horizontal arc covering 1.65m with a 0.65m lunge dealing 2 damage.\n"
                "• Naval Artillery [R]: Isometric celestial astrolabe. Hold [R] to guide the target reticle and release to call a devastating orbital cannonball.\n"
                "• Black Powder Dash [T]: Heavy dodge with 12 i-frames leaving black powder soot on the ground to slow the opponent.\n"
                "• Fatalities: Aranami Ryoudan (荒波両断 - Diagonal Cutlass Bisection) and Kanpou Senmetsu (艦砲殲滅 - Orbital Cannon Obliteration)."
            ),
            "estrategia_ofensiva": (
                "• Use Cutlass Cleave's forward lunge [E] to punish shallow lateral sidesteps.\n"
                "• Pressure the opponent with the descending Naval Artillery [R] and intercept them with the cutlass!\n"
                "• Lay black powder soot [T] to impair enemy mobility."
            ),
            "estrategia_defensiva": (
                "• How to defeat Anne: When you see the golden cannon reticle on the floor, exit the zone immediately. Punish her long cutlass recovery with quick counter-thrusts or projectiles."
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
                "• Fleche Thrust [E]: Investida frontal alongada em passo de flecha com 1.30m de alcance, 2 de dano e precisão cirúrgica (hitbox 0.70m).\n"
                "• Pederneira / Floreio de Capa [R]: Com a pistola pronta, dispara a até 5.8m; em recarga, o floreio de capa com chute repele oponentes em 2.0m e desvia projéteis.\n"
                "• Salto com Capa [T]: Rolamento evasivo com 13 i-frames que atravessa obstáculos e desvia projéteis em pleno ar.\n"
                "• Fatalities: Hyakka Rantotsu (百花乱突 - Fonte de sangue arterial de 18 estocadas) e Zero-Kyori Juusatsu (零距離銃殺 - Fuzilamento à queima-roupa com pederneira)."
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
                "• Fleche Thrust [E]: Extended acrobatic lunging thrust with 1.30m reach, 2 damage, and pinpoint accuracy (hitbox 0.70m).\n"
                "• Flintlock / Cape Flip [R]: Fires the pocket flintlock up to 5.8m when ready; while reloading, the cape flip and coup de pied repels foes by 2.0m and deflects projectiles.\n"
                "• Cape Swirl Roll [T]: Acrobatic roll with 13 i-frames that clears obstacles and deflects projectiles in mid-air.\n"
                "• Fatalities: Hyakka Rantotsu (百花乱突 - 18-Thrust Arterial Blood Fountain) and Zero-Kyori Juusatsu (零距離銃殺 - Point-Blank Flintlock Execution)."
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
            "style": "Punhos de Ferro & Kiai Místico",
            "vel": "[5/5] Relâmpago",
            "dano": "Combo 3 Golpes (Socos, Palmas e Chutes)",
            "especial": "Grito Kiai (Barreira 360°)",
            "keys_p1": "[E] Combo Punhos | [R] Kiai",
            "keys_p2": "[U] Combo Punhos | [I] Kiai",
            "conceito": (
                "Monge budista peregrino do lendário templo Shaolin. Mestre supremo do combate desarmado, "
                "combina velocidade de punhos avassaladora com a canalização espiritual do Chi e do Kiai."
            ),
            "habilidades": (
                "• Combo Shaolin [E]: Sequência rítmica fluida de 3 passos com avanço e buffering: 1. Jab frontal veloz (1 Dano) -> 2. Palma de Ferro quebra-guarda (1 Dano) -> 3. Chute Alto do Dragão Shaolin com Chi concentrado (2 Dano Letal).\n"
                "• Grito Místico Kiai [R]: Emite uma barreira esférica de Chi dourado de 2.4m em 360° que repele e reflete projéteis inimigos, empurrando oponentes com alto knockback e atordoamento leve.\n"
                "• Salto Acrobático [Esquiva]: Mortal frontal baixo com 12 i-frames, cancelável nos últimos 40% diretamente para o Passo 1 ou 2 do combo herdando o momento cinético.\n"
                "• Fatalidades: Hyakuretsu Ken (百烈拳 - Rajada supersônica nos pontos vitais, pausa de costas e detonação interna do torso) & Kiai Shougeki (気合衝撃 - Rugido de Chi e dupla palma de choque)."
            ),
            "estrategia_ofensiva": (
                "• Use a velocidade colossal de 5.4 e a esquiva acrobática para fechar distância rapidamente contra oponentes com espadas ou armas de fogo.\n"
                "• Dispare o Grito Kiai [R] para rebater projéteis em 360° direto contra seus atacantes e criar aberturas fatais.\n"
                "• Pressione o Ataque Primário na recuperação do salto mortal para surpreender o rival com o cancelamento ofensivo no Jab ou Palma de Ferro."
            ),
            "estrategia_defensiva": (
                "• Como vencer Ren: O combate desarmado de Ren exige proximidade estrita. Use estocadas longas e varreduras de lança para mantê-lo fora do alcance de seus punhos. Não atire projéteis quando ele tiver o Kiai disponível."
            )
        },
        "en": {
            "name": "REN",
            "title": "Shaolin Monk",
            "style": "Iron Fists & Mystic Kiai",
            "vel": "[5/5] Lightning Speed",
            "dano": "3-Hit Martial Combo",
            "especial": "Kiai Shout (360° Barrier)",
            "keys_p1": "[E] Fist Combo | [R] Kiai",
            "keys_p2": "[U] Fist Combo | [I] Kiai",
            "conceito": (
                "Wandering Buddhist monk from the legendary Shaolin temple. Master of unarmed combat fusing "
                "blistering fist speed with spiritual Chi shockwaves."
            ),
            "habilidades": (
                "• Shaolin Combo [E]: Fluid 3-step martial sequence with buffering: 1. Fast lead Jab (1 Dmg) -> 2. Iron Palm guard-crusher (1 Dmg) -> 3. High Dragon Kick with concentrated Chi (2 Lethal Dmg).\n"
                "• Kiai Shout [R]: Unleashes a 360° golden Chi barrier (2.4m radius) reflecting incoming projectiles and shoving foes with high knockback and soft stun.\n"
                "• Acrobatic Somersault [Dodge]: Low forward roll with 12 i-frames, cancelable in the last 40% into Combo Step 1 or 2 while preserving kinetic momentum.\n"
                "• Fatalities: Hyakuretsu Ken (百烈拳 - Vital-point supersonic flurry with delayed torso detonation) & Kiai Shougeki (気合衝撃 - Chi shockwave palm blast)."
            ),
            "estrategia_ofensiva": (
                "• Exploit your top 5.4 movement speed and acrobatic roll to close distance aggressively against armed rivals.\n"
                "• Time your Kiai Shout [R] to turn enemy bullets, arrows, and shurikens back at their owners.\n"
                "• Attack during the tail end of your dodge roll to execute a surprise offensive cancel into Jab or Iron Palm."
            ),
            "estrategia_defensiva": (
                "• How to defeat Ren: Ren must get into point-blank range to connect punches. Keep him at bay with long thrusts and polearms, and bait his Kiai cooldown before firing projectiles."
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
            "style": "Dança das Duas Kodachi & Acrobacias Evasivas",
            "vel": "[5/5] Extrema",
            "dano": "Corte Duplo Tesoura & Lunge",
            "especial": "Dança Mai & Salto Acrobático",
            "keys_p1": "[E] Kodachi | [R] Dança Mai / Lunge",
            "keys_p2": "[U] Kodachi | [I] Dança Mai / Lunge",
            "conceito": (
                "Kunoichi ágil e acrobática que maneja duas lâminas Kodachi com técnica cirúrgica, giros evasivos de deflexão e botes aéreos fulminantes."
            ),
            "habilidades": (
                "• Corte Kodachi Duplo [E]: Combo fluido de 3 passos com arcos amplos em tesoura (1.20m de alcance, 7 frames de startup e 0.28s de cooldown).\n"
                "• Dança Mai & Salto Acrobático Lunge [R]: Giro evasivo de 0.40s com deflexão de projéteis e golpes. Pressionar [R] novamente durante o giro cancela a dança em um bote acrobático de 3.2m com estocada dupla (3.2s de cooldown).\n"
                "• Shadow Step Slip [Espaço]: Deslizamento evasivo de alta velocidade com 14 frames de invulnerabilidade e rastro de pétalas carmesins de Higanbana."
            ),
            "estrategia_ofensiva": (
                "• Use a Dança Mai para desviar ou defletir investidas inimigas e converta instantaneamente no Salto Acrobático Lunge para perfurar o oponente a 3.2m.\n"
                "• O Shadow Step Slip permite atravessar projéteis e reposicionar-se nas costas do rival para iniciar o combo de 3 passos de Kodachi."
            ),
            "estrategia_defensiva": (
                "• Como vencer Chiyo: O Salto Acrobático Lunge deixa Chiyo vulnerável a parry ou esquiva lateral se errar (0.28s de whiff recovery). Aguarde o término da Dança Mai ou do salto antes de retaliar com ataques pesados."
            )
        },
        "en": {
            "name": "CHIYO",
            "title": "Twin Kodachi Kunoichi",
            "style": "Dual Kodachi Dance & Evasive Acrobatics",
            "vel": "[5/5] Extreme",
            "dano": "Scissor Cross Cuts & Lunge",
            "especial": "Mai Dance & Acrobat Lunge",
            "keys_p1": "[E] Kodachi | [R] Mai Dance / Lunge",
            "keys_p2": "[U] Kodachi | [I] Mai Dance / Lunge",
            "conceito": (
                "Graceful and acrobatic kunoichi master of dual kodachi blades, excelling at evasive spins, projectile deflections, and aerial lunges."
            ),
            "habilidades": (
                "• Twin Kodachi Cross Slice [E]: Fluid 3-hit scissor combo (1.20m reach, 7f startup, 0.28s recovery).\n"
                "• Mai Dance & Acrobat Lunge [R]: Whirling 0.40s evasive spin with weapon/projectile deflection. Re-pressing [R] during the dance cancels into a 3.2m acrobatic leap with a twin blade thrust (3.2s cooldown).\n"
                "• Shadow Step Slip [Space]: Low evasive glide with 14 invulnerability frames, projectile immunity, and a trail of Higanbana crimson petals."
            ),
            "estrategia_ofensiva": (
                "• Deflect incoming attacks with Mai Dance and immediately press [R] again to trigger the Acrobat Lunge, closing 3.2m of distance instantly.\n"
                "• Use Shadow Step Slip to slip cleanly through ranged projectiles and flank into your 3-hit kodachi scissor combo."
            ),
            "estrategia_defensiva": (
                "• How to defeat Chiyo: If Chiyo whiffs her Acrobat Lunge, she incurs 0.28s of recovery frames. Sidestep her straight leap and punish heavily before she can recover."
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
            "vel": "[2/5] Walking Tank",
            "dano": "Varredura 170° (2.4m) / Estocada (2.8m)",
            "especial": "Adamantine Push, Arremesso & Tackle",
            "keys_p1": "[E] Combo Naginata/Tackle | [R] Arremesso | [T] Adamantine Push",
            "keys_p2": "[U] Combo Naginata/Tackle | [I] Arremesso | [O] Adamantine Push",
            "conceito": (
                "Monge guerreiro sōhei colossal e inabalável que acumulou 999 armas na Ponte Gojō. "
                "Não possui aparo técnico, compensando com armadura maciça, alcance desmedido da naginata em combo de inércia, "
                "um avanço blindado que repele projéteis e um tackle desarmado brutal de atropelamento."
            ),
            "habilidades": (
                "• Combo de Inércia da Naginata [E]: Passo 1 Varredura Circular em Arco (170°, 2.40m, rec 0.16s) conectando em Passo 2 Estocada Perfurante Monumental (2.8m com avanço de 0.45m).\n"
                "• Arremesso de Naginata [R]: Lança a haste pesada a longa distância que se crava no solo sem jamais cair em buracos ou água.\n"
                "• Tackle Atropelo [E desarmado]: Investida brutal que causa 0 dano letal, aplica STUN garantido (1.2s) e recupera a arma.\n"
                "• Adamantine Guard Push [T]: Deslize firme com o ombro encouraçado (12 i-frames) que reflete/destrói projéteis em raio de 1.8m e empurra oponentes adjacentes."
            ),
            "estrategia_ofensiva": (
                "• Domine o centro da arena e a ponte usando a varredura circular de 170° e encadeie de imediato na estocada colossal de 2.8m.\n"
                "• Use o Adamantine Guard Push [T] para passar ileso por projéteis e empurrar rivais agressivos para trás.\n"
                "• Se o adversário recuar, arremesse a naginata [R] e em seguida use o Tackle [E] para atordoá-lo e recuperar a haste."
            ),
            "estrategia_defensiva": (
                "• Como vencer Benkei: Benkei não tem parry e possui velocidade 4.35. Espere o fim de sua estocada colossal (recovery de 0.22s) ou flanqueie durante o arremesso para puni-lo antes do tackle."
            )
        },
        "en": {
            "name": "BENKEI",
            "title": "Sōhei Warrior Monk",
            "style": "Heavy Plate Armor & Naginata",
            "vel": "[2/5] Walking Tank",
            "dano": "170° Cleave (2.4m) / Thrust (2.8m)",
            "especial": "Adamantine Push, Spear Throw & Tackle",
            "keys_p1": "[E] Naginata Combo/Tackle | [R] Throw | [T] Adamantine Push",
            "keys_p2": "[U] Naginata Combo/Tackle | [I] Throw | [O] Adamantine Push",
            "conceito": (
                "Colossal warrior monk of legend on Gojō Bridge. Lacks technical parry, relying on heavy lacquered iron armor, "
                "massive naginata reach in a 2-step inertia combo, a projectile-repelling armored shoulder push, and an unstoppable unarmed charging tackle."
            ),
            "habilidades": (
                "• Naginata Inertia Combo [E]: Step 1 Wide Cleave Arc (170°, 2.40m, 0.16s rec) linking into Step 2 Colossal Thrust (2.8m reach with 0.45m forward step).\n"
                "• Naginata Throw [R]: Hurls the heavy spear across long range, embedding safely in solid ground.\n"
                "• Stun Tackle [E unarmed]: High-speed kinetic charge that inflicts 0 lethal damage, applies guaranteed STUN (1.2s), and recovers the weapon.\n"
                "• Adamantine Guard Push [T]: Armored shoulder charge (12 i-frames) that deflects/destroys projectiles within 1.8m and displaces adjacent foes."
            ),
            "estrategia_ofensiva": (
                "• Dominate corridors and bridge choke points with your 170° sweep, buffering directly into the 2.8m colossal thrust.\n"
                "• Use Adamantine Guard Push [T] to slip invulnerably through enemy projectiles and shove aggressive rivals.\n"
                "• Throw the naginata [R] to catch retreating foes, then tackle with [E] for guaranteed stun and weapon recovery."
            ),
            "estrategia_defensiva": (
                "• How to defeat Benkei: Benkei cannot parry and has 4.35 movement speed. Sidestep his linear colossal thrust and punish during his 0.22s recovery window."
            )
        }
    },
    {
        "id": CHAR_ORIN,
        "color": COLOR_ORIN_AURA,
        "char_type": "orin",
        "pt": {
            "name": "O-RIN",
            "title": "A Menestrel de Yoshiwara",
            "style": "Tsugaru Shamisen Acústico & Kamaitachi",
            "vel": "[5/5] Zoner Evasiva de Elite",
            "dano": "Combo Kamaitachi (5.5m) | V-Twin Blades",
            "especial": "Ressonância 360° Repelente & Deslize de Seda",
            "keys_p1": "[E] Kamaitachi | [R] Ressonância | [T] Deslize",
            "keys_p2": "[U] Kamaitachi | [I] Ressonância | [O] Deslize",
            "conceito": (
                "Cortesã lendária e virtuose do Tsugaru Shamisen de Yoshiwara. Jamais empunha uma lâmina física: "
                "seus golpes são lâminas invisíveis de vácuo acústico Kamaitachi que fatiam o ar com precisão letal."
            ),
            "habilidades": (
                "• Combo Kamaitachi [E]: Rítmica em 2 etapas. Etapa 1 dispara lâmina sônica linear de 5.5m; Etapa 2 executa dedilhado duplo em V cruzado (±0.14 rad) com micro-passo de 0.20m.\n"
                "• Ressonância 360° [R]: Acorde devastador com onda de choque concêntrica (2.0m). Deflete projéteis, empurra rivais com 0.35s de atordoamento e lança 3 ondas em espiral (120°).\n"
                "• Deslize de Seda [T]: Esquiva acrobática com 13 i-frames e imunidade a projéteis, deslizando suavemente com o esvoaçar das mangas longas Furisode."
            ),
            "estrategia_ofensiva": (
                "• Controle o ritmo da arena: use a Etapa 1 para forçar a esquiva do adversário e emende a Etapa 2 em V para punir rolamentos laterais.\n"
                "• Se o rival tentar fechar distância, ative a Ressonância [R] para desviar ataques, atordoá-lo e restabelecer o zoneamento ideal com o Deslize de Seda [T]."
            ),
            "estrategia_defensiva": (
                "• Como vencer O-Rin: O-Rin é frágil e possui 1.4s de recarga na Ressonância 360°. Esquive pelas aberturas diagonais entre as ondas e ataque à queima-roupa durante o intervalo de dedilhado."
            )
        },
        "en": {
            "name": "O-RIN",
            "title": "The Yoshiwara Minstrel",
            "style": "Acoustic Tsugaru Shamisen & Kamaitachi",
            "vel": "[5/5] Elite Evasive Zoner",
            "dano": "Kamaitachi Combo (5.5m) | Twin V-Blades",
            "especial": "360° Repulsion Resonance & Silk Sleeve Glide",
            "keys_p1": "[E] Kamaitachi | [R] Resonance | [T] Glide",
            "keys_p2": "[U] Kamaitachi | [I] Resonance | [O] Glide",
            "conceito": (
                "Legendary courtesan and acoustic virtuoso of Yoshiwara. Never touches a steel blade: "
                "attacks entirely through razor-sharp acoustic vacuum blades (Kamaitachi) generated by her Tsugaru shamisen."
            ),
            "habilidades": (
                "• Kamaitachi Combo [E]: 2-step rhythmic strike. Step 1 unleashes a linear 5.5m sonic wave; Step 2 unleashes crossed twin V-blades (±0.14 rad) with a 0.20m micro-step.\n"
                "• 360° Resonance Chord [R]: Expanding acoustic repulsion shockwave (2.0m radius). Deflects projectiles, pushes rivals with 0.35s stun, and emits 3 spiral waves at 120°.\n"
                "• Silk Sleeve Glide [T]: Graceful evasive dodge with 13 i-frames and projectile immunity, gliding past danger with flowing Furisode sleeves."
            ),
            "estrategia_ofensiva": (
                "• Control arena pacing: bait rival dodges with Step 1 and punish recovery angles with the twin V-blades of Step 2.\n"
                "• When opponents rush in, pop 360° Resonance [R] to repel projectiles, stun them, and reset distance using Silk Sleeve Glide [T]."
            ),
            "estrategia_defensiva": (
                "• How to defeat O-Rin: O-Rin has high vulnerability during her 1.4s Resonance cooldown. Bait her shockwave, roll diagonally through her wave gaps, and punish at point-blank range."
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
            "style": "Enxada Kuwa de Ferro & Terremoto",
            "vel": "[3/5] Guerreiro Telúrico",
            "dano": "Kuwa Heavy Cleave (2.4m | Quebra de Guarda)",
            "especial": "Pisotão Sísmico (4.2m) & Pocket Dirt",
            "keys_p1": "[E] Corte da Kuwa | [R] Pisotão | [T] Rolamento / Terra",
            "keys_p2": "[U] Corte da Kuwa | [I] Pisotão | [O] Rolamento / Terra",
            "conceito": (
                "Líder camponês e rebelde implacável da era Bakumatsu, forjado no trabalho bruto da terra. "
                "Não empunha aço refinado, mas sim uma enxada pesada de carvalho e ferro forjado que esmaga defesas e racha o solo."
            ),
            "habilidades": (
                "• Corte da Kuwa [E]: Pancada vertical demolidora com alcance de 2.40m e hiper-inércia. Quebra guardas e escudos adversários.\n"
                "• Pisotão Sísmico [R]: Golpe violento no solo criando uma fissura telúrica de 4.2m que levanta pedras, dissipa projéteis e atordoa por 0.8s.\n"
                "• Rolamento de Lavrador & Pocket Dirt [T]: Esquiva rente à terra com 13 i-frames. Pressionar ataque [E] durante o rolamento lança um punhado de terra no rosto do rival (micro-stun de 0.22s)."
            ),
            "estrategia_ofensiva": (
                "• Controle o espaço com o Pisotão Sísmico [R] para quebrar investidas e atordoar oponentes rápidos.\n"
                "• Cancele a esquiva em Pocket Dirt [E] para cegar o adversário à queima-roupa e conectar o Corte da Kuwa [E] indefensável."
            ),
            "estrategia_defensiva": (
                "• Como vencer Goro: A descida da Kuwa possui grande inércia e recuperação. Esquive diagonalmente e puna pelas costas antes que ele desenganche a lâmina do solo."
            )
        },
        "en": {
            "name": "GORO",
            "title": "The Rebel Peasant",
            "style": "Forged Iron Kuwa & Earthquake",
            "vel": "[3/5] Earthborn Brawler",
            "dano": "Heavy Kuwa Cleave (2.4m | Guard Break)",
            "especial": "Seismic Stomp (4.2m) & Pocket Dirt",
            "keys_p1": "[E] Kuwa Cleave | [R] Earth Stomp | [T] Mud Roll / Dirt",
            "keys_p2": "[U] Kuwa Cleave | [I] Earth Stomp | [O] Mud Roll / Dirt",
            "conceito": (
                "Unyielding peasant rebel leader of the Bakumatsu era, hardened by relentless soil work. "
                "Wields a heavy forged-iron agricultural hoe that shatters armor and cracks the bedrock open."
            ),
            "habilidades": (
                "• Heavy Kuwa Cleave [E]: Downward crushing smash with 2.40m reach and hyper-inertia. Penetrates blocks and breaks guard.\n"
                "• Seismic Earth Stomp [R]: Slams boot into the soil, creating a 4.2m fissure that raises earth, deflects ground projectiles, and stuns for 0.8s.\n"
                "• Peasant Mud Roll & Pocket Dirt [T]: Low dodge with 13 i-frames. Pressing attack [E] during the roll flings a handful of pocket dirt into the rival's eyes (0.22s micro-stun)."
            ),
            "estrategia_ofensiva": (
                "• Halt aggressive opponents with Seismic Stomp [R] to stop their momentum and leave them vulnerable.\n"
                "• Cancel Mud Roll into Pocket Dirt [E] to blind foes at point-blank range and follow up with a devastating Kuwa Cleave [E]."
            ),
            "estrategia_defensiva": (
                "• How to defeat Goro: His heavy hoe swing has significant recovery frames. Evade diagonally and punish from behind while his weapon is lodged in the ground."
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
            "dano": "Saque Gyaku-Iai (0.11s | Alcance 1.8m)",
            "especial": "Postura de Escuta & Desvio da Bengala (13 i-frames)",
            "keys_p1": "[E] Gyaku-Iai | [R] Escuta | [T] Desvio da Bengala",
            "keys_p2": "[U] Gyaku-Iai | [I] Escuta | [O] Desvio da Bengala",
            "conceito": (
                "Mestra espadachim cega lendária inspirada no clássico Zatoichi. Caminha com uma bengala de cerejeira "
                "que oculta uma lâmina afiada como navalha, guiando-se pelo som e pela vibração do ar."
            ),
            "habilidades": (
                "• Gyaku-Iai [E]: Saque relâmpago em empunhadura invertida a partir da bengala oculta (startup 7 frames / 0.11s, alcance 1.80m, 2 HP).\n"
                "• Postura de Escuta [R]: Assume foco auditivo sensorial e proteção com a bainha. Ao detectar ataques ou projéteis frontais, apara o impacto e desfere contra-ataque perfurante automático (Blind Counter-Thrust).\n"
                "• Desvio da Bengala [T]: Deslize evasivo fluído com 13 i-frames (0.22s de invulnerabilidade) guiado pelo toque da bengala, ideal para escapar de ataques em área e perigos de arena."
            ),
            "estrategia_ofensiva": (
                "• Avance com calma e aproveite o saque mais rápido do jogo [E] para punir tentativas afobadas do rival.\n"
                "• Ative a Postura de Escuta [R] na meia-distância para atrair ataques e disparos de projéteis, punindo com o contra-ataque letal.\n"
                "• Use o Desvio da Bengala [T] para reposicionar-se instantaneamente atrás do adversário ou desviar de carruagens de Kyoto."
            ),
            "estrategia_defensiva": (
                "• Como vencer Ichi: Jamais ataque diretamente de frente quando ela estiver na Postura de Escuta [R]. Use fintas, ataques por trás ou espere o término da janela ativa de escuta para castigar sua recuperação."
            )
        },
        "en": {
            "name": "ICHI",
            "title": "The Blind Blade",
            "style": "Shikomizue (Gyaku-Iai) & Sensory Stance",
            "vel": "[5/5] Extreme Reflexes",
            "dano": "Gyaku-Iai Lightning Draw (0.11s | Reach 1.8m)",
            "especial": "Listen Stance & Cane Tap Slip (13 i-frames)",
            "keys_p1": "[E] Gyaku-Iai | [R] Listen Stance | [T] Cane Slip",
            "keys_p2": "[U] Gyaku-Iai | [I] Listen Stance | [O] Cane Slip",
            "conceito": (
                "Serene blind master swordsman inspired by Zatoichi. Wields a disguised cherry wood walking cane concealing a razor-sharp blade, "
                "sensing opponents through vibrations, footsteps, and rustling air."
            ),
            "habilidades": (
                "• Gyaku-Iai [E]: Blindingly swift reverse-grip draw strike from her concealed cane (startup 7 frames / 0.11s, reach 1.80m, 2 HP).\n"
                "• Listen Stance [R]: Closes senses to focus purely on sound; automatically parries incoming frontal strikes/projectiles with the wooden sheath and counters with a lethal thrust.\n"
                "• Cane Tap Slip [T]: Fluid evasive slide with 13 i-frames (0.22s of invulnerability) guided by the cane tip, allowing complete avoidance of stage hazards and Kyoto carriages."
            ),
            "estrategia_ofensiva": (
                "• Utilize her lightning draw [E] to interrupt opposing attacks in close quarters.\n"
                "• Bait aggressive rushdown foes or projectile fire into your Listen Stance [R] for an unblockable counter-thrust.\n"
                "• Use Cane Tap Slip [T] to slip past stage hazards or reposition instantly behind the opponent."
            ),
            "estrategia_defensiva": (
                "• How to defeat Ichi: Do not swing blindly into her Listen Stance [R]. Bait the stance with feints, attack from behind, or punish during her cooldown recovery."
            )
        }
    },
    {
        "id": CHAR_VALERIUS,
        "color": COLOR_VALERIUS_AURA,
        "char_type": "valerius",
        "pt": {
            "name": "VALERIUS",
            "title": "O Necromante / Exorcista Prussiano",
            "style": "Foice Espectral & Tríade dos Mortos",
            "vel": "[3/5] Passo Cerimonial",
            "dano": "Cursed Scythe Reap (2 HP)",
            "especial": "Tríade dos Mortos & Detonação Cadavérica",
            "keys_p1": "[E] Ceifada | [R] Invocar / Detonar | [T] Névoa",
            "keys_p2": "[U] Ceifada | [I] Invocar / Detonar | [O] Névoa",
            "conceito": (
                "Aristocrata e exorcista prussiano em terras nipônicas durante a era Bakumatsu. Empunha uma imponente foice cerimonial "
                "com rastro de chamas azuis e comanda a Tríade dos Mortos — servos rituais que rastejam, golpeiam ou explodem sob seu comando."
            ),
            "habilidades": (
                "• Ceifada Cerimonial (Soul Reap) [E]: Golpe ceifador amplo em arco largo com rastro de chamas azuis espectrais (alcance 1.95m, raio 1.35m, 2 HP).\n"
                "• Tríade dos Mortos [R]: Invoca em ciclo ritual um dos 3 servos das profundezas:\n"
                "    1. Rastejante de Tornozelos: persegue a 3.4 m/s e imobiliza o rival por 1.4s (0 dano).\n"
                "    2. Soldado com Espada: marcha com Pickelhaube e sabre enferrujado causando 1 de dano.\n"
                "    3. Wight de Chamas Azuis: corre em disparada a 4.4 m/s e explode em área (raio 1.6m, 1 dano) ao aproximar-se ou ser golpeado.\n"
                "• Detonação de Cadáver [R com servo ativo]: Estala os dedos e explode o servo prematuramente em chamas azuis de área onde estiver!\n"
                "• Névoa Espectral (Mist Dash) [T]: Deslizamento etéreo com 13 i-frames (0.22s de invulnerabilidade) em fumaça violeta e fagulhas azuis."
            ),
            "estrategia_ofensiva": (
                "• Use o Rastejante para imobilizar o rival e garantir a Ceifada Cerimonial de 2 HP à queima-roupa.\n"
                "• Com o Wight ou Soldado em campo, pressione [R] para detonar o lacaio quando o oponente tentar esquivar ou contra-atacar."
            ),
            "estrategia_defensiva": (
                "• Como vencer Valerius: Destrua o lacaio com um golpe antes que ele se aproxime (ou aparo técnico/parry para defleti-lo). Cuidado extremo com a explosão do Wight ao matá-lo corpo a corpo!"
            )
        },
        "en": {
            "name": "VALERIUS",
            "title": "The Prussian Necromancer",
            "style": "Spectral Scythe & Triad of the Dead",
            "vel": "[3/5] Ceremonial Stride",
            "dano": "Cursed Scythe Reap (2 HP)",
            "especial": "Triad of the Dead & Corpse Detonation",
            "keys_p1": "[E] Scythe Reap | [R] Summon / Detonate | [T] Mist",
            "keys_p2": "[U] Scythe Reap | [I] Summon / Detonate | [O] Mist",
            "conceito": (
                "Prussian aristocrat and dark exorcist navigating Bakumatsu Japan. Wields a colossal ceremonial funeral scythe "
                "with an azure spectral flame trail and commands the Triad of the Dead — minions that crawl, strike, or detonate on his command."
            ),
            "habilidades": (
                "• Cursed Scythe Reap [E]: Broad sweeping horizontal reap with azure flame wake (reach 1.95m, radius 1.35m, 2 HP).\n"
                "• Triad of the Dead [R]: Summons in a ritual cycle one of 3 specialized undead minions:\n"
                "    1. Crawling Grasper: crawls low at 3.4 m/s and pins the foe with a 1.4s heavy immobilize/slow (0 direct damage).\n"
                "    2. Bone Swordsman: marches upright in a Pickelhaube with rusty saber, slashing for 1 damage.\n"
                "    3. Pyre Wight: sprints at 4.4 m/s engulfed in azure flames, detonating in an area blast (radius 1.6m, 1 damage) on contact or upon destruction.\n"
                "• Corpse Detonation [R while minion is alive]: Snaps fingers to prematurely detonate the active minion in an azure pyre blast anywhere on the field!\n"
                "• Mist Dash [T]: Ethereal ghost slide with 13 i-frames (0.22s invulnerability) leaving dark violet smoke and azure embers."
            ),
            "estrategia_ofensiva": (
                "• Send the Crawling Grasper to pin the enemy and guarantee a lethal 2 HP Cursed Scythe Reap.\n"
                "• If the foe maneuvers around your minion, press [R] to trigger Corpse Detonation and catch them with the area blast."
            ),
            "estrategia_defensiva": (
                "• How to defeat Valerius: Destroy or parry his minions before they close the distance. Beware of the Pyre Wight's death explosion when engaging in melee!"
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
            "vel": "[4/5] Movimento Fluido & Deslize Shikigami",
            "dano": "Talismãs Ofuda Retos (2 HP / Bloqueados por Obstáculos) + 6 Selos Kekkai",
            "especial": "Rondel dos 6 Elementos (Madeira, Fogo, Terra, Metal, Água, Yin-Yang) + 6 Fatalidades Elementais Únicas",
            "keys_p1": "[E] Feitiço Primário | [R] Rito Secundário",
            "keys_p2": "[U] Feitiço Primário | [I] Rito Secundário",
            "conceito": (
                "Suprema mestra Onmyōji descendente da corte imperial Heian. Manipula o Rondel Gogyō de adivinhação oracular, "
                "que avança continuamente entre os 5 elementos ancestrais e o estado supremo de Yin-Yang a cada ação desferida."
            ),
            "habilidades": (
                "• Disparo de Ofuda Reto: Talismã veloz em linha reta (alcance 6.5m, dano 2 HP). Bloqueado por obstáculos sólidos do cenário (árvores, rochas, construções).\n"
                "• Rondel Onmyōdō: Mostrador no rodapé que avança no ciclo generativo a cada ação (Madeira -> Fogo -> Terra -> Metal -> Água -> Yin-Yang).\n"
                "• Selo Sagrado Kekkai: Invoca selo elemental persistente por 5.5s (limite de 2 selos ativos simultaneamente).\n"
                "• Deslize Shikigami: Esquiva com asas de papel origami flutuantes e 13 i-frames (0.22s de invulnerabilidade).\n"
                "• 6 Fatalidades Elementais Únicas: Fogo (Seien Kaijin - Cinzas e Brasas), Água (Suisou Shouka - Orvalho e Poça Cristalina), "
                "Madeira (Shinju Rinne - Árvore Sagrada Kodama), Metal (Kongou Fuubaku - Círculo de 5 Lâminas Astrais), "
                "Terra (Ganshuku Kaseki - Estátua de Granito Kintsugi) e Yin-Yang (In-You Tenchuu - Portal Celestial Taijitu)."
            ),
            "estrategia_ofensiva": (
                "• Use o alcance de 6.5m dos talismãs em corredores limpos e controle a arena posicionando até 2 selos Kekkai.\n"
                "• Antecipe o elemento do Rondel para alternar entre contenção, lentidão, refração e explosão máxima."
            ),
            "estrategia_defensiva": (
                "• Como vencer Seimei: Use rochas e edifícios para bloquear os talismãs retos. Evite pisar nos selos Kekkai terrestres e avance durante o tempo de recuperação dos seus ritos."
            )
        },
        "en": {
            "name": "SEIMEI",
            "title": "The Onmyoji of the Six Elements",
            "style": "Onmyōdō Gogyō Rondel & Celestial Oracle",
            "vel": "[4/5] Fluid Motion & Shikigami Glide",
            "dano": "Straight Ofuda Talismans (2 HP / Blocked by Obstacles) + 6 Kekkai Wards",
            "especial": "Six-Element Rondel (Wood, Fire, Earth, Metal, Water, Yin-Yang) + 6 Unique Elemental Fatalities",
            "keys_p1": "[E] Primary Spell | [R] Secondary Rite",
            "keys_p2": "[U] Primary Spell | [I] Secondary Rite",
            "conceito": (
                "Supreme onmyoji spiritualist preserving ancient Heian cosmology. Wields the Gogyō divination Rondel at the bottom of the screen, "
                "which continuously rotates through the 5 elemental phases plus divine Yin-Yang with every spell cast."
            ),
            "habilidades": (
                "• Straight Ofuda Toss: High-speed straight talisman (6.5m range, 2 HP damage). Strictly blocked by solid environment obstacles (trees, rocks, buildings).\n"
                "• Onmyōdō Rondel: Rotating dial on the bottom HUD advancing clockwise on every action (Wood -> Fire -> Earth -> Metal -> Water -> Yin-Yang).\n"
                "• Sacred Kekkai Ward: Places a protective/elemental stasis ward for 5.5s (limit 2 active wards simultaneously).\n"
                "• Shikigami Glide: Evasive paper wing glide with 13 i-frames (0.22s invulnerability).\n"
                "• 6 Unique Elemental Fatalities: Fire (Seien Kaijin - Azure Ashes & Embers), Water (Suisou Shouka - Mist & Clear Ripple Pond), "
                "Wood (Shinju Rinne - Sacred Kodama Tree), Metal (Kongou Fuubaku - 5 Astral Impaling Blades), "
                "Earth (Ganshuku Kaseki - Kintsugi Stone Statue), and Yin-Yang (In-You Tenchuu - Celestial Taijitu Banishing Portal)."
            ),
            "estrategia_ofensiva": (
                "• Capitalize on the 6.5m range in open lines of sight and dictate zone control with up to 2 active Kekkai wards.\n"
                "• Track the dial indicator to adapt instantly between ranged bolts and protective boundaries."
            ),
            "estrategia_defensiva": (
                "• How to defeat Seimei: Take cover behind rocks and buildings to stop incoming talismans. Avoid stepping into ground wards and pressure her during casting recovery."
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
