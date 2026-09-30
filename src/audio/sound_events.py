"""
Constantes e identificadores universais de eventos sonoros (SFX e BGM) para o Samurai Edge Demake.
Inclui metaclase com fallback resiliente para prevenir AttributeErrors e suportar aliases sem quebras.
"""
from enum import Enum, EnumMeta


class _SoundEventMeta(EnumMeta):
    """Metaclasse resiliente: permite aliases e fallback seguro sem lançar AttributeError."""
    def __getattr__(cls, name: str):
        name_upper = name.upper()
        # Verificar se o nome em maiúsculo existe
        if name_upper in cls._member_map_:
            return cls._member_map_[name_upper]
        # Mapa de aliases comuns para garantir 100% de robustez
        aliases = {
            "MENU_SELECT": "UI_SELECT",
            "MENU_CONFIRM": "UI_CONFIRM",
            "MENU_CANCEL": "UI_CANCEL",
            "CLASH_MUTUAL": "SWORD_CLASH",
            "BAMBOO_CUT": "SWORD_SLASH",
            "GUNSHOT": "TANEGASHIMA_SHOT",
            "FLINTLOCK_FIRE": "FLINTLOCK_SHOT",
            "BOMB_FUSE": "SMOKE_PUFF",
            "BOMB_EXPLOSION": "BOMB_EXPLODE",
            "BOW_RELEASE": "ARROW_RELEASE",
            "KUNAI_THROW": "SHURIKEN_THROW",
            "CHAIN_SPIN": "CHAIN_WHIP",
            "DASH_ROLL": "DODGE_WHOOSH",
            "FOOTSTEP_GRASS": "FOOTSTEP",
            "FOOTSTEP_STONE": "FOOTSTEP",
        }
        if name_upper in aliases:
            target = aliases[name_upper]
            if target in cls._member_map_:
                return cls._member_map_[target]
        # Fallback gracioso silencioso para som padrão de interface/combate
        if "UI_SELECT" in cls._member_map_:
            return cls._member_map_["UI_SELECT"]
        return super().__getattr__(name)


class SoundEvent(str, Enum, metaclass=_SoundEventMeta):
    # Combate de Espadas & Armas Brancas
    SWORD_SLASH = "sword_slash"            # Corte de espada no ar (whiff)
    SWORD_CLASH = "sword_clash"            # Choque simultâneo de lâminas
    CLASH_MUTUAL = "sword_clash"           # Alias para choque simultâneo
    PARRY = "parry"                        # Bloqueio perfeito / aparada frontal
    FATAL_STRIKE = "fatal_strike"          # Golpe de morte súbita (1-hit kill)
    OBSTACLE_HIT = "obstacle_hit"          # Lâmina colidindo com rocha / sólida
    BAMBOO_CUT = "sword_slash"             # Corte de tronco de bambu

    # Armas de Fogo e Explosivos
    FLINTLOCK_SHOT = "flintlock_shot"      # Tiro de pistola de pederneira (Julie)
    FLINTLOCK_FIRE = "flintlock_shot"      # Alias para tiro de pederneira
    TANEGASHIMA_SHOT = "tanegashima_shot"  # Tiro de arcabuz Tanegashima (Teppo)
    GUNSHOT = "tanegashima_shot"           # Alias para tiro de rifle
    BOMB_EXPLODE = "bomb_explode"          # Detonação de bomba de pólvora / mina
    BOMB_EXPLOSION = "bomb_explode"        # Alias para explosão
    BOMB_FUSE = "smoke_puff"               # Ruído de pavio ou arremesso
    CANNON_FIRE = "cannon_fire"            # Disparo de canhão naval (Anne)

    # Armas de Longo Alcance & Projéteis
    ARROW_RELEASE = "arrow_release"        # Disparo da corda do arco Yumi (Tomoe)
    BOW_RELEASE = "arrow_release"          # Alias para disparo de arco
    ARROW_HIT = "arrow_hit"                # Flecha cravando no chão ou alvo
    SHURIKEN_THROW = "shuriken_throw"      # Arremesso de shuriken
    KUNAI_THROW = "shuriken_throw"         # Alias para arremesso de kunai
    CHAIN_WHIP = "chain_whip"              # Movimento da corrente Kusarigama (Murasaki)
    CHAIN_SPIN = "chain_whip"              # Alias para giro de corrente

    # Movimentação, Criaturas & Técnicas Especiais
    DODGE_WHOOSH = "dodge_whoosh"          # Esquiva / roll / cambalhota
    DASH_ROLL = "dodge_whoosh"             # Alias para roll/dash
    SHUKUCHI = "shukuchi"                  # Teletransporte / pós-imagem relâmpago
    RYUU_TSUI_SEN = "ryuu_tsui_sen"        # Descida cortante do ápice aéreo
    SMOKE_PUFF = "smoke_puff"              # Bomba de fumaça ninja (Kasumi)
    POISON_BREATH = "poison_breath"        # Sopro de veneno Dokukiri (Okuni)
    FOOTSTEP = "footstep"                  # Passos na grama / pedra
    FOOTSTEP_GRASS = "footstep"            # Alias passos na grama
    FOOTSTEP_STONE = "footstep"            # Alias passos na pedra
    DOG_BARK = "dog_bark"                  # Latido / investida de Yamato (American Ninja)

    # Interface & Apresentação de Partida
    ROUND_START = "round_start"            # Tambor Taiko de início de duelo
    ROUND_WIN = "round_win"                # Gongo cerimonial de vitória
    UI_SELECT = "ui_select"                # Navegação nos menus
    MENU_SELECT = "ui_select"              # Alias para navegação nos menus
    UI_CONFIRM = "ui_confirm"              # Confirmação de lutador / opção
    MENU_CONFIRM = "ui_confirm"            # Alias para confirmação de opção
    UI_CANCEL = "ui_cancel"                # Cancelamento / retorno
    MENU_CANCEL = "ui_cancel"              # Alias para retorno


class MusicTrack(str, Enum):
    TITLE_THEME = "bgm_menu"              # Tema da tela de título e seleção
    BAMBOO_THEME = "bgm_bamboo"           # Tema da Floresta de Bambu e Lago Zen
    KYOTO_THEME = "bgm_kyoto"             # Tema da Avenida Bakumatsu em chamas
