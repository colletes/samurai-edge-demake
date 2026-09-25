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
    COLOR_MUSKETEER_AURA, CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA,
    CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE, CHAR_SAITOU, CHAR_RIFLE,
    CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER
)
from src.isometric.iso_math import world_to_iso
from src.entities.voxel_models import render_voxel_humanoid, render_voxel_doberman
from src.i18n import t, get_lang, set_lang, toggle_lang, LANG_PT, LANG_EN
from src.ui.portraits import get_portrait

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
            "style": "Niten Ichi-ryū (Duas Lâminas)",
            "vel": "[2/5] Firme e Pesado",
            "dano": "Combo 3-Cortes (Resiliente)",
            "especial": "Parry / Guarda Perfeita Defensiva",
            "keys_p1": "[E] Combo de Lâminas (Ataque)",
            "keys_p2": "[R] Parry (Defesa)",
            "conceito": (
                "O maior duelista da história do Japão, empunhando a Katana longa e a Wakizashi curta ao mesmo "
                "tempo. Musashi personifica a serenidade tática, a resistência física e o contra-ataque esmagador."
            ),
            "habilidades": (
                "• Combo 3-Cortes [E]: Sequência encadeada de golpes pesados com as duas espadas.\n"
                "• Parry [R]: Ergue as espadas em cruz frontal. Anula qualquer ataque frontal com faíscas."
            ),
            "estrategia_ofensiva": (
                "• Jogue na defensiva paciente. Aguarde o oponente tomar a iniciativa e aperte [R] para o Parry.\n"
                "• Ao aparar com sucesso, o oponente entra em hitstop e recuo; avance desferindo o combo completo.\n"
                "• Use o peso e tamanho das suas lâminas para controlar o centro do mapa e a ponte estreita."
            ),
            "estrategia_defensiva": (
                "• Como vencer Musashi: O Parry só bloqueia ataques pela frente! Flanqueie-o pelas diagonais "
                "ou ataque-o pelas costas. Arqueiros, bombas e projéteis à distância ignoram o Parry tradicional."
            )
        },
        "en": {
            "name": "MUSASHI",
            "title": "The Sword Saint",
            "style": "Niten Ichi-ryū (Two Swords)",
            "vel": "[2/5] Resilient & Heavy",
            "dano": "3-Slash Combo (Tough)",
            "especial": "Parry / Perfect Defense",
            "keys_p1": "[E] Blade Combo (Attack)",
            "keys_p2": "[R] Parry (Deflect)",
            "conceito": (
                "Japan's most famed swordsman, wielding both Katana and Wakizashi simultaneously. "
                "Musashi embodies disciplined patience, rugged physical resilience, and crushing counter-attacks."
            ),
            "habilidades": (
                "• 3-Slash Combo [E]: Heavy chained combo strikes with both blades.\n"
                "• Parry [R]: Crosses dual blades frontally, deflecting any forward strike with bright sparks."
            ),
            "estrategia_ofensiva": (
                "• Play patiently on defense. Wait for your foe to commit forward, then press [R] to Parry.\n"
                "• A successful parry inflicts hitstop and heavy pushback on your foe; counter with your combo.\n"
                "• Dominate the central bridge with your wide dual blades."
            ),
            "estrategia_defensiva": (
                "• How to defeat Musashi: The Parry only deflects frontal attacks! Flank him diagonally or "
                "strike his back. Ranged projectiles, bombs, and arrows bypass the parry."
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
            "dano": "Estocada Tanto (Desarmado) / Kunai Aérea",
            "especial": "Salto Parabólico Evasivo (Arremesso Aéreo)",
            "keys_p1": "[E] Tanto (Sem Kunai) / Salto Kunai",
            "keys_p2": "[R] Salto Parabólico Evasivo",
            "conceito": (
                "Shinobi lendário das sombras feudais. Especializado em acrobacias aéreas, esquiva "
                "por salto parabólico sobre golpes rasteiros e arremesso aéreo de Kunai. "
                "Seu ataque corpo a corpo com a Tanto fica disponível apenas quando estiver desarmado (sem kunai)."
            ),
            "habilidades": (
                "• Salto Parabólico [R]: Salto alto evasivo que passa por cima de cortes baixos. Permite arremessar a Kunai no ar.\n"
                "• Estocada Tanto [E]: Golpe corpo a corpo rápido com a Tanto (disponível apenas quando a Kunai foi lançada)."
            ),
            "estrategia_ofensiva": (
                "• Use o Salto Parabólico para saltar sobre estocadas e disparar a Kunai do ar com ângulo superior.\n"
                "• Se errar ou a Kunai for bloqueada, aproxime-se para lutar com a adaga Tanto ou recupere a Kunai do solo.\n"
                "• Sua mobilidade aérea desorienta adversários de golpes lineares como Kenshi e Saitou."
            ),
            "estrategia_defensiva": (
                "• Como vencer Hanzo: Acompanhe o arco de queda do Salto Parabólico. No momento em que Hanzo aterrissa, "
                "há uma fração de segundo de vulnerabilidade antes de poder se mover ou saltar novamente."
            )
        },
        "en": {
            "name": "HANZO",
            "title": "Iga Master Shinobi",
            "style": "Iga Ninjutsu & Kunai",
            "vel": "[5/5] Extreme Agility",
            "dano": "Tanto Thrust (Unarmed) / Midair Kunai",
            "especial": "Parabolic Evasive Jump (Air Throw)",
            "keys_p1": "[E] Tanto (No Kunai) / Jump Throw",
            "keys_p2": "[R] Parabolic Evasive Jump",
            "conceito": (
                "Legendary shinobi of feudal shadows. Master of acrobatic leaps, parabolic jumps "
                "vaulting over ground slashes, and deadly mid-air Kunai throws. "
                "His close-quarters Tanto dagger thrust is only active when unarmed (after throwing the kunai)."
            ),
            "habilidades": (
                "• Parabolic Jump [R]: High evasive jump leaping over low strikes. Allows mid-air Kunai throw.\n"
                "• Tanto Thrust [E]: Swift close-range dagger thrust (only available while kunai is deployed)."
            ),
            "estrategia_ofensiva": (
                "• Use Parabolic Jump to clear incoming slashes and fling your Kunai downwards from above.\n"
                "• Once unarmed, engage directly with rapid Tanto strikes or retrieve your Kunai from the terrain.\n"
                "• Your superior vertical evasion counters linear dash attackers like Kenshi and Saitou."
            ),
            "estrategia_defensiva": (
                "• How to defeat Hanzo: Anticipate the landing arc of his parabolic jump. As he lands on the ground, "
                "there is a brief window of recovery before he can leap again."
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
                "• Shuriken [E]: Estrela de metal ninja arremessada rapidamente; atordoa o oponente no impacto.\n"
                "• Comando Cão [R]: O Doberman avança em disparada furiosa, desferindo uma mordida fatal (1-Hit Kill)."
            ),
            "estrategia_ofensiva": (
                "• A estratégia clássica de pinça: lance a Shuriken para paralisar o alvo com stun.\n"
                "• Enquanto o oponente estiver atordoado, pressione [R] para o Doberman finalizar com 1-Hit Kill!\n"
                "• Mantenha-se distante enquanto seu cão pressiona as linhas do oponente."
            ),
            "estrategia_defensiva": (
                "• Como vencer Joe: O Doberman avança em linha reta previsível. Golpes cortantes de ampla abertura "
                "podem interceptar a investida. Pressione Joe diretamente para impedir que ele mire suas shurikens."
            )
        },
        "en": {
            "name": "JOE",
            "title": "American Ninja",
            "style": "Tactical Combat & Doberman",
            "vel": "[4/5] Tactical & Quick",
            "dano": "Metal Shuriken (Stun)",
            "especial": "Doberman Attack (1-Hit Kill)",
            "keys_p1": "[E] Shuriken (Attack)",
            "keys_p2": "[R] Dog Dash (Special)",
            "conceito": (
                "Western tactical operative trained in secret ninjutsu arts, fighting alongside his trained "
                "combat Doberman. Specializes in pincer maneuvers and tactical distractions."
            ),
            "habilidades": (
                "• Shuriken [E]: Rapidly tossed metal throwing star; briefly stuns on impact.\n"
                "• Dog Command [R]: The Doberman sprints forward at top speed, delivering a fatal 1-Hit Kill bite."
            ),
            "estrategia_ofensiva": (
                "• Classic pincer maneuver: throw your Shuriken to freeze the rival in hitstun.\n"
                "• While the enemy is stunned, immediately command your Doberman [R] to finish them from afar!\n"
                "• Stay at safe distance while your hound pressures the enemy."
            ),
            "estrategia_defensiva": (
                "• How to defeat Joe: The Doberman charges in a predictable straight line. Wide slashes can "
                "intercept the dog. Rush Joe directly to disrupt his throwing aim."
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
            "style": "Shinsengumi (Gatotsu Shinsen)",
            "vel": "[5/5] Impulso Explosivo",
            "dano": "Estocada Letal Acelerada (1-Hit)",
            "especial": "Zeroshiki (Gatotsu Queima-Roupa)",
            "keys_p1": "[E] Gatotsu Shinsen (Ataque)",
            "keys_p2": "[R] Zeroshiki (Especial)",
            "conceito": (
                "Líder de divisão do Shinsengumi, frio, impiedoso e guiado pelo lema Aku Soku Zan (Corte o Mal Imediatamente). "
                "Sua postura única com a mão esquerda gera a mais temida e penetrante estocada da era feudal: o Gatotsu."
            ),
            "habilidades": (
                "• Gatotsu Shinsen [E]: Disparo em carga ultra-rápida. Pode ser guiado no volante direcional na corrida.\n"
                "• Zeroshiki [R]: Estocada explosiva de queima-roupa sem corrida prévia, punindo aproximações."
            ),
            "estrategia_ofensiva": (
                "• O Gatotsu tem altíssima prioridade frontal. Ao ver o oponente iniciar um ataque, dispare a carga!\n"
                "• Você pode curvar a trajetória do Gatotsu usando os direcionais enquanto corre para perseguir o alvo.\n"
                "• Se o inimigo tentar colar em você no corpo a corpo, aperte [R] para o Zeroshiki instantâneo."
            ),
            "estrategia_defensiva": (
                "• Como vencer Saitou: O Gatotsu ricocheteia com faíscas se colidir com rochas, poço ou árvores! "
                "Lute perto de obstáculos e desvie lateralmente na hora em que ele acelerar. A recuperação é longa."
            )
        },
        "en": {
            "name": "SAITOU",
            "title": "The Wolf of Mibu",
            "style": "Shinsengumi (Gatotsu Shinsen)",
            "vel": "[5/5] Explosive Lunge",
            "dano": "Accelerated Lethal Thrust (1-Hit)",
            "especial": "Zeroshiki (Point-Blank Thrust)",
            "keys_p1": "[E] Gatotsu Shinsen (Attack)",
            "keys_p2": "[R] Zeroshiki (Special)",
            "conceito": (
                "Feared Shinsengumi division captain, cold, merciless, living by Aku Soku Zan (Slay Evil Immediately). "
                "His left-handed stance yields the deadliest thrust in feudal history."
            ),
            "habilidades": (
                "• Gatotsu Shinsen [E]: Devastating accelerated charge with absolute frontal priority; can be steered mid-sprint.\n"
                "• Zeroshiki [R]: Explosive point-blank Gatotsu thrust with no windup, punishing close-range rushes."
            ),
            "estrategia_ofensiva": (
                "• Gatotsu has overwhelming forward priority. When you spot an enemy windup, launch the charge!\n"
                "• You can steer your charge using movement keys to curve toward a dodging opponent.\n"
                "• If the enemy crowds you in melee, press [R] for an instant Zeroshiki point-blank kill."
            ),
            "estrategia_defensiva": (
                "• How to defeat Saitou: Gatotsu violently ricochets off rocks, well, and trees with sparks! "
                "Fight near obstacles and dodge sideways when he charges. His whiff recovery is lengthy."
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
            "style": "Kyudo Sagrado & Flecha de Corda",
            "vel": "[4/5] Ágil e Concentrada",
            "dano": "Flecha Yumi Fatal (Alcance Máximo)",
            "especial": "Flecha de Corda (Zip Mobility)",
            "keys_p1": "[E] Retesar e Atirar (Ataque)",
            "keys_p2": "[R] Flecha de Corda (Especial)",
            "conceito": (
                "Sacerdotisa miko do santuário nas montanhas, mestre na arte marcial meditativa do arco e flecha (Kyudo). "
                "Sua presença transmite serenidade, foco inabalável e disparos mortais milimétricos."
            ),
            "habilidades": (
                "• Disparo Yumi [E]: Segure/pressione para retesar o arco e soltar uma flecha mortal (1-Hit Kill).\n"
                "• Flecha de Corda [R]: Dispara flecha atrelada a corda de cânhamo para puxar alvos ou reposicionar-se."
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
            "especial": "Capa Riposte (Desvio & Contra-Ataque)",
            "keys_p1": "[E] Estocada Fleche (Ataque)",
            "keys_p2": "[R] Capa Riposte (Especial)",
            "conceito": (
                "Nobre duelista europeia mestre na arte do florete e capa de esgrima. Campeã invicta em duelos "
                "de honra, combina elegância aristocrática, estocadas de alcance cirúrgico e defesas perfeitas."
            ),
            "habilidades": (
                "• Fleche Thrust [E]: Investida frontal alongada em passo de flecha de longo alcance e precisão cirúrgica.\n"
                "• Capa Riposte [R]: Gira a capa de combate de seda reforçada para aparar golpes e contra-atacar fatalmente."
            ),
            "estrategia_ofensiva": (
                "• O Fleche tem alcance superior ao das katanas convencionais. Pique o oponente de fora do alcance dele!\n"
                "• Se você antecipar o ataque inimigo, ative o Riposte [R]: a capa desviará a lâmina e perfurará o rival.\n"
                "• Abuse de sua velocidade 5/5 para entrar, atacar e recuar com graça e impunidade."
            ),
            "estrategia_defensiva": (
                "• Como vencer Julie: O Fleche tem linha reta muito estreita; esquivas laterais limpas abrem as costas "
                "dela para punição. Fique atento ao Riposte da capa para não cair na armadilha do contra-ataque."
            )
        },
        "en": {
            "name": "JULIE",
            "title": "Flower of the Royal Guard",
            "style": "French Fencing (Rapier & Cloak)",
            "vel": "[5/5] Elite Fencing Speed",
            "dano": "Long Precision Fleche Thrust",
            "especial": "Cloak Riposte (Deflect & Counter)",
            "keys_p1": "[E] Fleche Thrust (Attack)",
            "keys_p2": "[R] Cloak Riposte (Special)",
            "conceito": (
                "Aristocratic European duelist, undefeated master of rapier and combat cloak fencing. "
                "Melds courtly elegance with surgical reach and deadly counter-ripostes."
            ),
            "habilidades": (
                "• Fleche Thrust [E]: Extended acrobatic lunging thrust with extreme range and pinpoint accuracy.\n"
                "• Cloak Riposte [R]: Swirls her reinforced silk cloak to parry attacks and immediately counter with a fatal thrust."
            ),
            "estrategia_ofensiva": (
                "• Fleche out-ranges conventional samurai katanas. Strike from just outside their range!\n"
                "• If you anticipate an enemy strike, trigger Cloak Riposte [R] to parry and instantly pierce them.\n"
                "• Abuse your 5/5 top speed to lunge, hit, and dance away untouched."
            ),
            "estrategia_defensiva": (
                "• How to defeat Julie: The Fleche travels along a narrow straight line; clean lateral sidesteps "
                "expose her back to punishment. Watch out for her cloak riposte trap."
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

    def open(self, tab: int = TAB_RULES, fighter_idx: int = 0):
        self.is_open = True
        self.current_tab = tab
        self.scroll_y = 0.0
        self.fighter_sub_section = self.SEC_ALL
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
            # Alternar idioma: Triângulo (3) ou Quadrado (2)
            elif event.button in (2, 3):
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
                if event.value > 0.65:
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 36.0)
                elif event.value < -0.65:
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
        overlay.fill((10, 14, 12, 220))
        surface.blit(overlay, (0, 0))

        # Dimensões da Caixa Modal (1160 x 640)
        mw, mh = 1160, 640
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        self.modal_rect = pygame.Rect(mx, my, mw, mh)

        # Fundo do Modal & Borda Dourada Estilizada
        pygame.draw.rect(surface, (20, 26, 23), self.modal_rect, border_radius=14)
        pygame.draw.rect(surface, COLOR_GOLD, self.modal_rect, 2, border_radius=14)

        # Barra de Título Superior
        header_rect = pygame.Rect(mx, my, mw, 56)
        pygame.draw.rect(surface, (28, 36, 32), header_rect, border_top_left_radius=14, border_top_right_radius=14)
        pygame.draw.line(surface, (60, 75, 68), (mx, my + 56), (mx + mw, my + 56), 1)

        title_s = font_large.render(t("help_modal_title"), True, COLOR_GOLD)
        surface.blit(title_s, (mx + 28, my + 10))

        # Botão Seletor Flutuante de Idioma [ PT | EN ] (Padrão Boardbots)
        self.lang_btn_rect = pygame.Rect(mx + mw - 165, my + 11, 100, 34)
        pygame.draw.rect(surface, (30, 40, 35), self.lang_btn_rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_GOLD, self.lang_btn_rect, 1, border_radius=6)

        pt_col = COLOR_GOLD if lang == LANG_PT else (140, 155, 148)
        en_col = COLOR_GOLD if lang == LANG_EN else (140, 155, 148)
        pt_bg = (48, 64, 54) if lang == LANG_PT else (25, 34, 29)
        en_bg = (48, 64, 54) if lang == LANG_EN else (25, 34, 29)

        r_pt = pygame.Rect(self.lang_btn_rect.x + 3, self.lang_btn_rect.y + 3, 44, 28)
        r_en = pygame.Rect(self.lang_btn_rect.x + 53, self.lang_btn_rect.y + 3, 44, 28)
        pygame.draw.rect(surface, pt_bg, r_pt, border_radius=4)
        pygame.draw.rect(surface, en_bg, r_en, border_radius=4)

        s_pt = font_small.render("PT", True, pt_col)
        s_en = font_small.render("EN", True, en_col)
        surface.blit(s_pt, (r_pt.centerx - s_pt.get_width() // 2, r_pt.centery - s_pt.get_height() // 2))
        surface.blit(s_en, (r_en.centerx - s_en.get_width() // 2, r_en.centery - s_en.get_height() // 2))

        # Botão Fechar [ X ]
        self.close_btn_rect = pygame.Rect(mx + mw - 48, my + 11, 34, 34)
        pygame.draw.rect(surface, (45, 30, 32), self.close_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (220, 80, 80), self.close_btn_rect, 1, border_radius=6)
        x_lbl = font_mid.render("X", True, (240, 140, 140))
        surface.blit(x_lbl, (self.close_btn_rect.centerx - x_lbl.get_width() // 2, self.close_btn_rect.centery - x_lbl.get_height() // 2))

        # Abas de Navegação Superiores
        tab_names = [t("tab_rules"), t("tab_controls"), t("tab_fighters")]
        tab_w = 255
        tab_h = 34
        start_tab_x = mx + 28
        tab_y = my + 66

        self.tab_rects.clear()
        for i, name in enumerate(tab_names):
            t_rect = pygame.Rect(start_tab_x + i * (tab_w + 10), tab_y, tab_w, tab_h)
            self.tab_rects.append(t_rect)
            is_active = (self.current_tab == i)

            t_bg = (42, 55, 48) if is_active else (25, 32, 28)
            t_border = COLOR_GOLD if is_active else (55, 70, 62)
            t_col = COLOR_GOLD if is_active else (180, 195, 185)

            pygame.draw.rect(surface, t_bg, t_rect, border_radius=6)
            pygame.draw.rect(surface, t_border, t_rect, 2 if is_active else 1, border_radius=6)
            t_surf = font_mid.render(name, True, t_col)
            surface.blit(t_surf, (t_rect.centerx - t_surf.get_width() // 2, t_rect.centery - t_surf.get_height() // 2))

        # Dica sutil de rolagem
        hint_txt = font_small.render(t("scroll_hint"), True, (150, 170, 160))
        surface.blit(hint_txt, (mx + mw - hint_txt.get_width() - 28, tab_y + 9))

        # Área de Conteúdo
        content_rect = pygame.Rect(mx + 28, my + 110, mw - 56, mh - 130)

        if self.current_tab == self.TAB_RULES:
            self._render_tab_rules(surface, content_rect, font_mid, font_small)
        elif self.current_tab == self.TAB_CONTROLS:
            self._render_tab_controls(surface, content_rect, font_mid, font_small)
        elif self.current_tab == self.TAB_FIGHTERS:
            self._render_tab_fighters(surface, content_rect, font_mid, font_small)

    def _render_tab_rules(self, surface: pygame.Surface, rect: pygame.Rect, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        # 3 Painéis temáticos anti-overflow
        col_w = (rect.width - 24) // 3

        boxes = [
            (t("rules_box1_title"), COLOR_GOLD, t("rules_box1_lines")),
            (t("rules_box2_title"), (110, 205, 150), t("rules_box2_lines")),
            (t("rules_box3_title"), (245, 140, 110), t("rules_box3_lines")),
        ]

        self.max_scroll = 0.0

        for i, (btitle, bcol, lines) in enumerate(boxes):
            bx = rect.x + i * (col_w + 12)
            b_rect = pygame.Rect(bx, rect.y, col_w, rect.height)
            pygame.draw.rect(surface, (25, 33, 29), b_rect, border_radius=8)
            pygame.draw.rect(surface, (48, 62, 54), b_rect, 1, border_radius=8)

            head_h = 36
            pygame.draw.rect(surface, (32, 42, 37), (bx, rect.y, col_w, head_h), border_top_left_radius=8, border_top_right_radius=8)
            t_surf = font_mid.render(btitle, True, bcol)
            surface.blit(t_surf, (bx + 12, rect.y + 8))

            cur_y = rect.y + 46
            for line in lines:
                l_surf = font_small.render(line, True, (220, 230, 225) if line.startswith("•") else (170, 185, 180))
                surface.blit(l_surf, (bx + 12, cur_y))
                cur_y += 18

    def _render_tab_controls(self, surface: pygame.Surface, rect: pygame.Rect, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        half_w = (rect.width - 16) // 2

        # Painel Esquerdo: Controles P1 e P2
        p_left = pygame.Rect(rect.x, rect.y, half_w, rect.height)
        pygame.draw.rect(surface, (25, 33, 29), p_left, border_radius=8)
        pygame.draw.rect(surface, (48, 62, 54), p_left, 1, border_radius=8)

        t1 = font_mid.render(t("ctrl_p1_title"), True, COLOR_GOLD)
        surface.blit(t1, (p_left.x + 16, p_left.y + 12))

        cy = p_left.y + 44
        color_map = {
            "header": COLOR_RED_AURA,
            "header2": COLOR_BLUE_AURA,
            "body": (220, 225, 220),
            "body_e": (255, 205, 205),
            "body_r": (255, 220, 220),
            "tip": (255, 215, 120),
            "body_dim": (180, 195, 190),
            "sep": (0, 0, 0),
        }
        for text, style in t("ctrl_p1_lines"):
            if text:
                s = font_small.render(text, True, color_map.get(style, (220, 225, 220)))
                surface.blit(s, (p_left.x + 14, cy))
            cy += 19

        # Painel Direito: Atalhos do Sistema
        p_right = pygame.Rect(rect.x + half_w + 16, rect.y, half_w, rect.height)
        pygame.draw.rect(surface, (25, 33, 29), p_right, border_radius=8)
        pygame.draw.rect(surface, (48, 62, 54), p_right, 1, border_radius=8)

        t2 = font_mid.render(t("ctrl_p2_title"), True, (110, 205, 150))
        surface.blit(t2, (p_right.x + 16, p_right.y + 12))

        color_map2 = {
            "key": COLOR_GOLD,
            "key_action": (255, 140, 110),
            "body": (220, 225, 220),
            "body_dim": (180, 195, 190),
            "sep": (0, 0, 0),
        }
        cy = p_right.y + 44
        for text, style in t("ctrl_p2_lines"):
            if text:
                s = font_small.render(text, True, color_map2.get(style, (220, 225, 220)))
                surface.blit(s, (p_right.x + 14, cy))
            cy += 19

    def _render_tab_fighters(self, surface: pygame.Surface, rect: pygame.Rect, font_mid: pygame.font.Font, font_small: pygame.font.Font):
        lang = get_lang()

        # 1. Carrossel de 12 Botões no topo
        btn_h = 28
        btn_w = (rect.width - 11 * 6) // 12
        btn_y = rect.y

        self.fighter_tab_rects.clear()
        for i, fdata in enumerate(FIGHTERS_GUIDE_DATA):
            bx = rect.x + i * (btn_w + 6)
            b_rect = pygame.Rect(bx, btn_y, btn_w, btn_h)
            self.fighter_tab_rects.append(b_rect)

            is_cur = (self.selected_fighter_idx == i)
            bg_col = (45, 58, 50) if is_cur else (22, 28, 25)
            border_col = fdata["color"] if is_cur else (45, 55, 50)

            pygame.draw.rect(surface, bg_col, b_rect, border_radius=4)
            pygame.draw.rect(surface, border_col, b_rect, 2 if is_cur else 1, border_radius=4)

            short_name = fdata[lang]["name"][:7]
            n_surf = font_small.render(short_name, True, fdata["color"] if is_cur else (160, 175, 170))
            surface.blit(n_surf, (b_rect.centerx - n_surf.get_width() // 2, b_rect.centery - n_surf.get_height() // 2))

        # 2. Painel Central da Ficha do Combatente Escolhido
        cur_fighter = FIGHTERS_GUIDE_DATA[self.selected_fighter_idx]
        cur_data = cur_fighter[lang]
        detail_y = rect.y + 36
        detail_h = rect.height - 36
        detail_rect = pygame.Rect(rect.x, detail_y, rect.width, detail_h)

        pygame.draw.rect(surface, (23, 30, 26), detail_rect, border_radius=8)
        pygame.draw.rect(surface, cur_fighter["color"], detail_rect, 2, border_radius=8)

        # Coluna Esquerda: Retrato Voxel 3D e Dados Básicos (largura 310px)
        left_col_w = 310
        portrait_cx = detail_rect.x + 56
        portrait_cy = detail_y + 66

        # Moldura circular e Retrato de Busto HD-2D do guerreiro
        pygame.draw.circle(surface, (16, 22, 19), (portrait_cx, portrait_cy), 44)
        pygame.draw.circle(surface, cur_fighter["color"], (portrait_cx, portrait_cy), 44, 3)

        p_size = (84, 84)
        p_surf = get_portrait(cur_fighter["id"], size=p_size, circular=True)
        if p_surf is not None:
            surface.blit(p_surf, (portrait_cx - p_size[0] // 2, portrait_cy - p_size[1] // 2))
        else:
            # Fallback para o render Voxel do guerreiro
            cam = HelpPreviewCam(portrait_cx, portrait_cy + 20)
            c_type = cur_fighter["char_type"]
            if c_type == "american_ninja":
                render_voxel_humanoid(surface, cam, -0.20, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type=c_type)
                render_voxel_doberman(surface, cam, 0.35, -0.10, 0, 1.0, 0.0, "IDLE", 0.0, True)
            elif c_type == "yellow_ninja":
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type=c_type, extra_props={"has_kunai": True})
            else:
                render_voxel_humanoid(surface, cam, 0, 0, 0, 1.0, 0.0, "IDLE", 0.0, True, char_type=c_type)

        # Nome, Título e Estilo
        n_surf = font_mid.render(cur_data["name"], True, cur_fighter["color"])
        t_surf = font_small.render(cur_data["title"], True, COLOR_WHITE)
        s_surf = font_small.render(cur_data["style"], True, COLOR_GOLD)

        surface.blit(n_surf, (detail_rect.x + 112, detail_y + 24))
        surface.blit(t_surf, (detail_rect.x + 112, detail_y + 50))
        surface.blit(s_surf, (detail_rect.x + 112, detail_y + 70))

        # Atributos e Teclas
        stat_y = detail_y + 122
        pygame.draw.line(surface, (45, 58, 52), (detail_rect.x + 16, stat_y), (detail_rect.x + left_col_w, stat_y), 1)

        stat_lines = [
            f"{t('stat_speed')} {cur_data['vel']}",
            f"{t('stat_damage')} {cur_data['dano']}",
            f"{t('stat_special')} {cur_data['especial']}",
            "",
            cur_data["keys_p1"],
            cur_data["keys_p2"]
        ]
        sy = stat_y + 8
        for sl in stat_lines:
            if sl:
                is_speed = sl.startswith(t('stat_speed'))
                is_key = sl.startswith("[")
                col = (230, 220, 180) if is_speed else ((255, 210, 180) if is_key else (205, 215, 210))
                s_s = font_small.render(sl, True, col)
                surface.blit(s_s, (detail_rect.x + 16, sy))
            sy += 19

        # Botões Anterior / Próximo na base da coluna esquerda
        btn_nav_y = detail_rect.bottom - 44
        self.prev_fighter_btn = pygame.Rect(detail_rect.x + 16, btn_nav_y, 130, 32)
        self.next_fighter_btn = pygame.Rect(detail_rect.x + 160, btn_nav_y, 130, 32)

        pygame.draw.rect(surface, (35, 45, 40), self.prev_fighter_btn, border_radius=6)
        pygame.draw.rect(surface, (60, 75, 68), self.prev_fighter_btn, 1, border_radius=6)
        prev_lbl = font_small.render(t("btn_prev"), True, COLOR_GOLD)
        surface.blit(prev_lbl, (self.prev_fighter_btn.centerx - prev_lbl.get_width() // 2, self.prev_fighter_btn.centery - prev_lbl.get_height() // 2))

        pygame.draw.rect(surface, (35, 45, 40), self.next_fighter_btn, border_radius=6)
        pygame.draw.rect(surface, (60, 75, 68), self.next_fighter_btn, 1, border_radius=6)
        next_lbl = font_small.render(t("btn_next"), True, COLOR_GOLD)
        surface.blit(next_lbl, (self.next_fighter_btn.centerx - next_lbl.get_width() // 2, self.next_fighter_btn.centery - next_lbl.get_height() // 2))

        # Divisória vertical
        sep_x = detail_rect.x + left_col_w + 14
        pygame.draw.line(surface, (45, 58, 52), (sep_x, detail_y + 14), (sep_x, detail_rect.bottom - 14), 1)

        # Coluna Direita: Sub-filtros e Conteúdo Estratégico com Rolagem Anti-Overflow
        right_x = sep_x + 16
        right_w = detail_rect.right - right_x - 18

        # 3. Pílulas de Sub-seção no topo da coluna direita (Padrão Boardbots)
        if lang == LANG_PT:
            sub_labels = ["TODOS", "CONCEITO", "ARSENAL", "COMO JOGAR", "COMO VENCER"]
        else:
            sub_labels = ["ALL", "CONCEPT", "ARSENAL", "HOW TO PLAY", "HOW TO COUNTER"]
        sub_w = 145
        sub_h = 24
        sub_y = detail_y + 10

        self.sub_sec_btn_rects.clear()
        for s_idx, s_lbl in enumerate(sub_labels):
            sb_rect = pygame.Rect(right_x + s_idx * (sub_w + 10), sub_y, sub_w, sub_h)
            self.sub_sec_btn_rects.append(sb_rect)
            is_active_sub = (self.fighter_sub_section == s_idx)
            s_bg = (48, 62, 54) if is_active_sub else (26, 33, 29)
            s_bcol = COLOR_GOLD if is_active_sub else (50, 62, 55)
            pygame.draw.rect(surface, s_bg, sb_rect, border_radius=4)
            pygame.draw.rect(surface, s_bcol, sb_rect, 1, border_radius=4)
            s_txt = font_small.render(s_lbl, True, COLOR_GOLD if is_active_sub else (160, 175, 168))
            surface.blit(s_txt, (sb_rect.centerx - s_txt.get_width() // 2, sb_rect.centery - s_txt.get_height() // 2))

        # Seções de Conteúdo a serem exibidas
        all_sections = [
            (t("sec_concept"), COLOR_GOLD, cur_data["conceito"], self.SEC_CONCEPT),
            (t("sec_arsenal"), (110, 205, 150), cur_data["habilidades"], self.SEC_ARSENAL),
            (t("sec_offense"), (255, 205, 120), cur_data["estrategia_ofensiva"], self.SEC_OFFENSE),
            (t("sec_defense"), (255, 130, 120), cur_data["estrategia_defensiva"], self.SEC_DEFENSE)
        ]

        if self.fighter_sub_section == self.SEC_ALL:
            active_sections = all_sections
        else:
            active_sections = [s for s in all_sections if s[3] == self.fighter_sub_section]

        # Janela com Clipping e Rolagem Vertical Suave
        clip_top = sub_y + sub_h + 8
        clip_h = detail_rect.bottom - clip_top - 12
        clip_rect = pygame.Rect(right_x, clip_top, right_w, clip_h)

        # Cálculo do total de altura necessário
        text_w = right_w - 18  # Reserva espaço para a barra de rolagem
        total_content_height = 0
        layout_blocks = []

        for sec_title, sec_color, sec_text, _ in active_sections:
            block_lines = [("title", sec_title, sec_color)]
            for rline in sec_text.split("\n"):
                words = rline.split(" ")
                cur_line = ""
                for w in words:
                    test_line = cur_line + (" " if cur_line else "") + w
                    if font_small.size(test_line)[0] > text_w:
                        block_lines.append(("line", cur_line, (215, 225, 220)))
                        cur_line = w
                    else:
                        cur_line = test_line
                if cur_line:
                    block_lines.append(("line", cur_line, (215, 225, 220)))
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
                    t_s = font_mid.render(itext, True, icol)
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
            pygame.draw.rect(surface, (28, 36, 31), (track_x, track_y, 6, track_h), border_radius=3)

            # Cálculo do polegar da barra de rolagem (Thumb)
            thumb_ratio = max(0.15, clip_h / (clip_h + self.max_scroll))
            thumb_h = int(track_h * thumb_ratio)
            thumb_pos = int((track_h - thumb_h) * (self.scroll_y / self.max_scroll))
            thumb_y = track_y + thumb_pos

            pygame.draw.rect(surface, COLOR_GOLD, (track_x, thumb_y, 6, thumb_h), border_radius=3)
