"""
Constantes e identificadores universais de eventos sonoros (SFX e BGM) para o Samurai Edge Demake.
"""
from enum import Enum


class SoundEvent(str, Enum):
    # Combate de Espadas & Armas Brancas
    SWORD_SLASH = "sword_slash"            # Corte de espada no ar (whiff)
    SWORD_CLASH = "sword_clash"            # Choque simultâneo de lâminas
    PARRY = "parry"                        # Bloqueio perfeito / aparada frontal
    FATAL_STRIKE = "fatal_strike"          # Golpe de morte súbita (1-hit kill)
    OBSTACLE_HIT = "obstacle_hit"          # Lâmina colidindo com rocha / sólida

    # Armas de Fogo e Explosivos
    FLINTLOCK_SHOT = "flintlock_shot"      # Tiro de pistola de pederneira (Julie)
    TANEGASHIMA_SHOT = "tanegashima_shot"  # Tiro de arcabuz Tanegashima (Teppo)
    BOMB_EXPLODE = "bomb_explode"          # Detonação de bomba de pólvora / mina
    CANNON_FIRE = "cannon_fire"            # Disparo de canhão naval (Anne)

    # Armas de Longo Alcance & Projéteis
    ARROW_RELEASE = "arrow_release"        # Disparo da corda do arco Yumi (Tomoe)
    ARROW_HIT = "arrow_hit"                # Flecha cravando no chão ou alvo
    SHURIKEN_THROW = "shuriken_throw"      # Arremesso de shuriken ou kunai
    CHAIN_WHIP = "chain_whip"              # Movimento da corrente Kusarigama (Murasaki)

    # Movimentação & Técnicas Especiais
    DODGE_WHOOSH = "dodge_whoosh"          # Esquiva / roll / cambalhota
    SHUKUCHI = "shukuchi"                  # Teletransporte / pós-imagem relâmpago
    RYUU_TSUI_SEN = "ryuu_tsui_sen"        # Descida cortante do ápice aéreo
    SMOKE_PUFF = "smoke_puff"              # Bomba de fumaça ninja (Kasumi)
    POISON_BREATH = "poison_breath"        # Sopro de veneno Dokukiri (Okuni)
    FOOTSTEP = "footstep"                  # Passos na grama / pedra

    # Interface & Apresentação de Partida
    ROUND_START = "round_start"            # Tambor Taiko de início de duelo
    ROUND_WIN = "round_win"                # Gongo cerimonial de vitória
    UI_SELECT = "ui_select"                # Navegação nos menus
    UI_CONFIRM = "ui_confirm"              # Confirmação de lutador / opção
    UI_CANCEL = "ui_cancel"                # Cancelamento / retorno


class MusicTrack(str, Enum):
    TITLE_THEME = "bgm_menu"              # Tema da tela de título e seleção
    BAMBOO_THEME = "bgm_bamboo"           # Tema da Floresta de Bambu e Lago Zen
    KYOTO_THEME = "bgm_kyoto"             # Tema da Avenida Bakumatsu em chamas
