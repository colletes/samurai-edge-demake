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
            "KNIFE_SLASH": "KUNAI_THROW",
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
    SWORD_SLASH = "sword_slash"            # Corte de espada no ar (whiff genérico)
    SLASH_KATANA = "slash_katana"          # Corte de katana (aço veloz e cortante)
    SLASH_HEAVY = "slash_heavy"            # Golpe pesado (naginata Benkei, kuwa Goro, alfanje Anne)
    SLASH_RAPIER = "slash_rapier"          # Estocada/corte de florete fino (Julie)
    SWING_BLUNT = "swing_blunt"            # Golpe de bastão de madeira/punhos (Ren, Daiki)
    SLASH_CHAIN = "slash_chain"            # Zunido cortante de corrente e foice (Kasumi, Murasaki)
    SWING_SHAMISEN = "swing_shamisen"      # Acorde ressonante com lâmina oculta (O-Rin)
    SWORD_CLASH = "sword_clash"            # Choque simultâneo de lâminas
    CLASH_MUTUAL = "sword_clash"           # Alias para choque simultâneo
    PARRY = "parry"                        # Bloqueio perfeito / aparada frontal
    FATAL_STRIKE = "fatal_strike"          # Golpe de morte súbita (1-hit kill)
    FLESH_CLEAVE = "flesh_cleave"          # Impacto visceral de carne e corte profundo
    BONE_CRUSH = "bone_crush"              # Fratura óssea / impacto contundente pesado
    ARTERIAL_SPRAY = "arterial_spray"      # Jato arterial visceral dos golpes de finalização
    ARMOR_CLANG = "armor_clang"            # Deflexão metálica contra armadura
    WOOD_SHATTER = "wood_shatter"          # Estilhaçamento de bambu, caixas ou barreiras
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
    SHURIKEN_THROW = "shuriken_throw"      # Arremesso de shuriken giratória
    KUNAI_THROW = "kunai_throw"            # Estocada / arremesso de faca tática ou kunai (Joe, Hanzo)
    KNIFE_SLASH = "kunai_throw"            # Alias para corte de faca tática
    CHAIN_WHIP = "chain_whip"              # Movimento da corrente Kusarigama (Murasaki)
    CHAIN_SPIN = "chain_whip"              # Alias para giro de corrente

    # Movimentação, Criaturas & Superfícies
    DODGE_WHOOSH = "dodge_whoosh"          # Esquiva / roll / cambalhota
    DASH_ROLL = "dodge_whoosh"             # Alias para roll/dash
    SHUKUCHI = "shukuchi"                  # Teletransporte / pós-imagem relâmpago
    RYUU_TSUI_SEN = "ryuu_tsui_sen"        # Descida cortante do ápice aéreo
    SMOKE_PUFF = "smoke_puff"              # Bomba de fumaça ninja (Kasumi)
    POISON_BREATH = "poison_breath"        # Sopro de veneno Dokukiri (Okuni)
    FOOTSTEP = "footstep"                  # Passo padrão genérico
    FOOTSTEP_GRASS = "footstep_grass"      # Passos em relva / vegetação
    FOOTSTEP_WOOD = "footstep_wood"        # Passos em pranchas de madeira / pontes
    FOOTSTEP_STONE = "footstep_stone"      # Passos em pedras / lajes de templos
    FOOTSTEP_GRAVEL = "footstep_gravel"    # Passos em cascalho / terra solta
    FOOTSTEP_WATER = "footstep_water"      # Chapinhar de passos em água / poças
    FOOTSTEP_MUD = "footstep_mud"          # Passos pegajosos em lama / arrozais
    DOG_BARK = "dog_bark"                  # Latido / investida de Yamato (American Ninja)
    CHAIN_RATTLE = "chain_rattle"          # Corrente de ferro balançando no teto (aviso do pêndulo da gruta)
    SHIP_CREAK = "ship_creak"              # Ranger de madeira do navio adernando (aviso do balanço)
    FALL = "fall"                          # Queda em buraco da arena (assobio descendente + baque distante)
    HEARTBEAT = "heartbeat"                # Batimento cardíaco surdo de tensão visceral dos finishers

    # Interface & Apresentação de Partida
    ROUND_START = "round_start"            # Tambor Taiko de início de duelo
    ROUND_WIN = "round_win"                # Gongo cerimonial de vitória
    UI_SELECT = "ui_select"                # Navegação nos menus
    MENU_SELECT = "ui_select"              # Alias para navegação nos menus
    UI_CONFIRM = "ui_confirm"              # Confirmação de lutador / opção
    MENU_CONFIRM = "ui_confirm"            # Alias para confirmação de opção
    UI_CANCEL = "ui_cancel"                # Cancelamento / retorno
    MENU_CANCEL = "ui_cancel"              # Alias para retorno


def get_weapon_swing_event(char_type: str) -> SoundEvent:
    """Mapeia o arquétipo do lutador para o som característico de seu golpe/arma."""
    c = str(char_type).lower()
    if c in ("benkei", "goro", "pirate", "anne"):
        return SoundEvent.SLASH_HEAVY
    elif c in ("musketeer", "julie"):
        return SoundEvent.SLASH_RAPIER
    elif c in ("ren_monk", "ren", "daiki"):
        return SoundEvent.SWING_BLUNT
    elif c in ("purple_ninja", "murasaki"):
        return SoundEvent.SLASH_CHAIN
    elif c in ("orin", "o-rin"):
        return SoundEvent.SWING_SHAMISEN
    elif c in ("american", "joe", "ninja", "hanzo"):
        return SoundEvent.KUNAI_THROW
    elif c in ("aoi",):
        return SoundEvent.SLASH_HEAVY
    return SoundEvent.SLASH_KATANA


def get_surface_footstep_event(tile_type: str) -> SoundEvent:
    """Retorna o evento sonoro de passo correspondente ao tipo de terreno."""
    t = str(tile_type).lower()
    if any(k in t for k in ("grass", "moss", "foliage", "leaf", "turf", "pine")):
        return SoundEvent.FOOTSTEP_GRASS
    elif any(k in t for k in ("wood", "bridge", "deck", "plank", "tatami", "floor")):
        return SoundEvent.FOOTSTEP_WOOD
    elif any(k in t for k in ("stone", "rock", "street", "pavement", "curb", "temple", "slate")):
        return SoundEvent.FOOTSTEP_STONE
    elif any(k in t for k in ("gravel", "sand", "dirt", "earth", "dune", "snow")):
        return SoundEvent.FOOTSTEP_GRAVEL
    elif any(k in t for k in ("water", "puddle", "river", "sea", "lake", "tide", "ice")):
        return SoundEvent.FOOTSTEP_WATER
    elif any(k in t for k in ("mud", "swamp", "rice", "paddy", "bog")):
        return SoundEvent.FOOTSTEP_MUD
    return SoundEvent.FOOTSTEP


class MusicTrack(str, Enum):
    TITLE_THEME = "bgm_menu"              # Tema da tela de título (Bakumatsu Theme)
    CHAR_SELECT_THEME = "bgm_char_select" # Tema da seleção de personagens
    BAMBOO_THEME = "bgm_bamboo"           # Tema da Floresta de Bambu e Lago Zen
    KYOTO_THEME = "bgm_kyoto"             # Tema da Avenida Bakumatsu em chamas
    GASHADOKURO_THEME = "bgm_gashadokuro" # Tema da batalha contra Oni Gashadokuro (Arcade Boss)
    DEATH_THEME = "bgm_death"             # Tema da cena de morte no round
    SHAOLIN_THEME = "bgm_shaolin_temple"   # Tema do Pátio Shaolin (Ren)
    HIGANBANA_THEME = "bgm_higanbana_garden" # Tema dos Lírios Carmim (Chiyo)
    GOJO_BRIDGE_THEME = "bgm_gojo_bridge"   # Tema da Ponte Gojo (Benkei)
    YOSHIWARA_THEME = "bgm_yoshiwara_alley" # Tema do Beco Yoshiwara (O-Rin)
    RICE_PADDIES_THEME = "bgm_rice_paddies" # Tema dos Arrozais Terraciados (Goro)
    RAIN_MILL_THEME = "bgm_rain_mill"       # Tema do Moinho na Chuva (Ichi)
    PRUSSIAN_CEMETERY_THEME = "bgm_prussian_cemetery" # Tema do Cemitério Gótico (Valerius)
    HEIAN_TEMPLE_THEME = "bgm_heian_temple" # Tema do Pavilhão Astral Heian (Seimei)
    SACRED_PINES_THEME = "bgm_sacred_pines" # Tema da Floresta dos Pinheiros (Daiki)
    EZO_TUNDRA_THEME = "bgm_ezo_tundra"     # Tema da Taiga Gelada de Ezo (Aoi)

