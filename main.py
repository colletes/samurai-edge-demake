"""
Ponto de entrada principal: Duelo de Samurais Isométrico 2.5D.
Suporte à Seleção de Personagens: Kenshi (Vermelho), Musashi (Azul) e Ninja Hanzo (Amarelo).
"""
import sys
import os

# Ajuste automático de CWD para executáveis empacotados (PyInstaller)
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    search_dirs = [
        getattr(sys, '_MEIPASS', None),
        exe_dir,
        os.path.join(exe_dir, "_internal"),
    ]
    if "Contents/MacOS" in exe_dir or "Contents/MacOS" in exe_dir.replace("\\", "/"):
        contents_dir = os.path.dirname(exe_dir)
        search_dirs.extend([
            os.path.join(contents_dir, "Resources"),
            os.path.join(contents_dir, "Resources", "_internal"),
            os.path.join(contents_dir, "MacOS"),
        ])
    for s_dir in search_dirs:
        if s_dir and os.path.exists(os.path.join(s_dir, "assets")):
            try:
                os.chdir(s_dir)
                break
            except Exception:
                pass

import math
import random
import pygame
from src.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    COLOR_BG, COLOR_WHITE, COLOR_GOLD, COLOR_RED_AURA, COLOR_BLUE_AURA, COLOR_YELLOW_AURA,
    KEY_RESTART, KEY_TOGGLE_AI, KEY_SETTINGS, DEFAULT_CONTROLS,
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE,
    CHAR_SAITOU, CHAR_RIFLE, CHAR_KABUKI, CHAR_ARCHER, CHAR_PIRATE, CHAR_MUSKETEER,
    CHAR_REN, CHAR_CHIYO, CHAR_BOSS,
    COLOR_GRAY_NINJA, COLOR_PURPLE_NINJA, COLOR_SAITOU_AURA,
    COLOR_RIFLE_AURA, COLOR_KABUKI_AURA, COLOR_ARCHER_AURA,
    COLOR_PIRATE_AURA, COLOR_MUSKETEER_AURA, COLOR_REN_AURA, COLOR_CHIYO_AURA,
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_RANDOM
)
from src.isometric.iso_math import input_to_world_direction
from src.isometric.camera import Camera
from src.world.arenas import create_arena, arena_ids
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.purple_ninja import PurpleNinja
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.rifleman import Rifleman, PowderTrap
from src.entities.kabuki import Kabuki, PoisonCloud
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.ren_monk import RenMonk
from src.entities.chiyo_kunoichi import ChiyoKunoichi
from src.entities.boss_oni import BossOni
from src.entities.ai_controller import SamuraiAI
from src.entities.pickups import PowderPouch
from src.combat.collision import CombatSystem
from src.combat.clash_system import ClashSystem
from src.effects.particles import AmbientLeafParticle, SparkParticle, BloodParticle, FloatingBanner, SmokeParticle
from src.effects.cinematic_director import CinematicDirector
from src.effects.lighting import ArenaLighting
from src.effects.terrain_particles import TerrainFX
from src.effects.fog import FogVolume
from src.effects.particles import set_wind_source
from src.effects import quality
from src.effects.fall_render import render_falling_fighter
from src.entities.samurai import STATE_FALL, STATE_IDLE, STATE_INTRO, STATE_VICTORY
from src.entities.pose_scripts import BeatPlayer
from src.ui.round_intro import RoundIntroScreen
from src.ui.round_result import RoundResultScreen, check_match_winner, render_round_pips, render_damage_bars, render_boss_bar, MATCH_WINS_NEEDED
from src.ui.match_intro import MatchIntro
from src.ui.outcome_sequence import OutcomeSequence
from src.ui.pause_menu import (
    PauseMenu, ACTION_RESUME, ACTION_SETTINGS, ACTION_ARENA, ACTION_FIGHTER, ACTION_MAIN_MENU, ACTION_QUIT, ACTION_ABANDON
)
from src.arcade import arcade_save
from src.edition import is_demo, DEMO_ARENA
from src.arcade.arcade_mode import ArcadeRun, FIGHT_WON, FIGHT_LOST, NEXT_OPPONENT, FightKind
from src.arcade.arcade_screens import ArcadeDifficultyScreen, ArcadeBracketScreen, ArcadeResultScreen
from src.arcade.arcade_credits import ArcadeCreditsScreen
from src.ui.settings_menu import SettingsMenu, format_key_name
from src.ui.character_select import CharacterSelectScreen
from src.ui.title_screen import SumieTitleScreen
from src.ui.opening_video import OpeningVideoScreen
from src.ui.arena_select import ArenaSelectScreen
from src.ui.portraits import preload_portraits
from src.ui.svg_icon_renderer import render_text_with_icons
from src.ui.loading_screen import LoadingScreen
from src.ui.fonts import get_title_font, get_text_font
from src.i18n import t
from src.input import get_controller_manager, TouchControls, DisplayScaler
from src.input.controls_storage import load_controls_config, save_controls_config
from src.audio import SoundManager, SoundEvent, MusicTrack

from enum import Enum

# Estados Globais do Jogo
class GameState(Enum):
    """Máquina de estados unificada para o jogo."""
    OPENING_VIDEO = "opening_video"
    TITLE = "title"
    CHARACTER_SELECT = "character_select"
    ARENA_SELECT = "arena_select"
    DUEL_PLAYING = "duel_playing"
    DUEL_RESULT = "duel_result"
    ARCADE_DIFFICULTY = "arcade_difficulty"
    ARCADE_CHAR_SELECT = "arcade_char_select"
    ARCADE_BRACKET = "arcade_bracket"
    ARCADE_CREDITS = "arcade_credits"
    ARCADE_RESULT = "arcade_result"

# Compatibilidade com código existente
STATE_OPENING_VIDEO = GameState.OPENING_VIDEO.value
STATE_TITLE = GameState.TITLE.value
STATE_CHAR_SELECT = GameState.CHARACTER_SELECT.value
STATE_ARENA_SELECT = GameState.ARENA_SELECT.value
STATE_DUEL_PLAYING = GameState.DUEL_PLAYING.value
STATE_ARCADE_DIFFICULTY = GameState.ARCADE_DIFFICULTY.value
STATE_ARCADE_CHAR_SELECT = GameState.ARCADE_CHAR_SELECT.value
STATE_ARCADE_BRACKET = GameState.ARCADE_BRACKET.value
STATE_ARCADE_CREDITS = GameState.ARCADE_CREDITS.value
STATE_ARCADE_RESULT = GameState.ARCADE_RESULT.value

def create_fighter(char_id: str, wx: float, wy: float):
    """Fábrica de lutadores com base no ID escolhido."""
    if char_id == CHAR_KENSHIN:
        return RedSamurai(wx, wy)
    elif char_id == CHAR_MUSASHI:
        return BlueSamurai(wx, wy)
    elif char_id == CHAR_NINJA:
        return YellowNinja(wx, wy)
    elif char_id == CHAR_AMERICAN:
        return AmericanNinja(wx, wy)
    elif char_id == CHAR_GRAY:
        return GrayNinja(wx, wy)
    elif char_id == CHAR_PURPLE:
        return PurpleNinja(wx, wy)
    elif char_id == CHAR_SAITOU:
        return SaitouSamurai(wx, wy)
    elif char_id == CHAR_RIFLE:
        return Rifleman(wx, wy)
    elif char_id == CHAR_KABUKI:
        return Kabuki(wx, wy)
    elif char_id == CHAR_ARCHER:
        return KyudoArcher(wx, wy)
    elif char_id == CHAR_PIRATE:
        return PirateSwordswoman(wx, wy)
    elif char_id == CHAR_MUSKETEER:
        return Musketeer(wx, wy)
    elif char_id == CHAR_REN:
        return RenMonk(wx, wy)
    elif char_id == CHAR_CHIYO:
        return ChiyoKunoichi(wx, wy)
    elif char_id == CHAR_BOSS:
        return BossOni(wx, wy)
    return RedSamurai(wx, wy)

def get_fighter_color(fighter):
    if isinstance(fighter, BossOni):
        return (226, 96, 64)
    if getattr(fighter, "mirror_alt", False):
        return (70, 210, 200)  # espelho do Arcade: cor alternativa para distinguir do jogador
    if isinstance(fighter, RedSamurai):
        return COLOR_RED_AURA
    elif isinstance(fighter, BlueSamurai):
        return COLOR_BLUE_AURA
    elif isinstance(fighter, YellowNinja):
        return COLOR_YELLOW_AURA
    elif isinstance(fighter, AmericanNinja):
        return (255, 130, 45)
    elif isinstance(fighter, GrayNinja):
        return COLOR_GRAY_NINJA
    elif isinstance(fighter, PurpleNinja):
        return COLOR_PURPLE_NINJA
    elif isinstance(fighter, SaitouSamurai):
        return COLOR_SAITOU_AURA
    elif isinstance(fighter, Rifleman):
        return COLOR_RIFLE_AURA
    elif isinstance(fighter, Kabuki):
        return COLOR_KABUKI_AURA
    elif isinstance(fighter, KyudoArcher):
        return COLOR_ARCHER_AURA
    elif isinstance(fighter, PirateSwordswoman):
        return COLOR_PIRATE_AURA
    elif isinstance(fighter, Musketeer):
        return COLOR_MUSKETEER_AURA
    elif isinstance(fighter, RenMonk):
        return COLOR_REN_AURA
    elif isinstance(fighter, ChiyoKunoichi):
        return COLOR_CHIYO_AURA
    return COLOR_WHITE

def get_fighter_action_labels(fighter):
    """Retorna os rótulos de comandos (Ataque, Secundário)."""
    if isinstance(fighter, RedSamurai):
        return "Iai Flash", "Shukuchi"
    elif isinstance(fighter, BlueSamurai):
        return "3-Cortes", "Parry"
    elif isinstance(fighter, YellowNinja):
        if getattr(fighter, "has_kunai", True):
            return "Arremesso Kunai", "Salto Parabólico"
        return "Estocada Tanto", "Salto Parabólico"
    elif isinstance(fighter, AmericanNinja):
        return "Shuriken", "Cão Dash"
    elif isinstance(fighter, GrayNinja):
        return "Bomba Arco", "Bomba Fumaça"
    elif isinstance(fighter, PurpleNinja):
        return "Corte Foice", "Kusarigama Puxão"
    elif isinstance(fighter, SaitouSamurai):
        return "Gatotsu", "Zeroshiki"
    elif isinstance(fighter, Rifleman):
        return "Tiro / Coronhada", "Salto Evasivo"
    elif isinstance(fighter, Kabuki):
        return "Leques de Aço", "Kawarimi Decoy"
    elif isinstance(fighter, KyudoArcher):
        return "Flecha Yumi", "Hamaya Sagrada"
    elif isinstance(fighter, PirateSwordswoman):
        return "Alfanje 180°", "Pólvora nos Olhos"
    elif isinstance(fighter, Musketeer):
        return "Estocada Fleche", "Capa Riposte"
    elif isinstance(fighter, RenMonk):
        return "Flurry Shaolin", "Kiai Repulsão"
    elif isinstance(fighter, ChiyoKunoichi):
        return "Tesoura Nodachi", "Dança Mai"
    return "Ataque", "Especial"

def get_fighter_cooldown_data(fighter) -> dict | None:
    """Retorna os dados da principal habilidade com cooldown do combatente para renderização no HUD e na arena."""
    if not fighter or not getattr(fighter, "is_alive", True):
        return None

    if isinstance(fighter, RedSamurai):
        if getattr(fighter, "state", "") == "RECOVERY" and getattr(fighter, "state_timer", 0.0) > 0.0:
            rec_cd = getattr(fighter, "recovery_duration", 0.80)
            return {"name": "Iai Noto", "timer": fighter.state_timer, "max_cd": rec_cd, "color": (235, 60, 60)}
        timer = max(0.0, getattr(fighter, "ryuu_timer", 0.0))
        cd = getattr(fighter, "ryuu_cooldown", 3.5)
        return {"name": "Ryuu Tsui Sen", "timer": timer, "max_cd": cd, "color": (235, 60, 60)}

    elif isinstance(fighter, BlueSamurai):
        if getattr(fighter, "combo_window_timer", 0.0) > 0:
            timer = getattr(fighter, "combo_window_timer", 0.0)
            return {"name": f"Combo {fighter.combo_step}/3", "timer": timer, "max_cd": 0.45, "color": (255, 215, 60)}
        timer = max(0.0, getattr(fighter, "parry_timer", 0.0))
        return {"name": "Parry", "timer": timer, "max_cd": 1.8, "color": (60, 140, 255)}

    elif isinstance(fighter, YellowNinja):
        if not getattr(fighter, "has_kunai", True):
            return {"name": "Sem Kunai", "timer": 1.0, "max_cd": 1.0, "color": (230, 70, 70), "warning": True}
        timer = max(0.0, getattr(fighter, "jump_timer", 0.0))
        cd = getattr(fighter, "jump_cooldown", 3.2)
        return {"name": "Salto Ninja", "timer": timer, "max_cd": cd, "color": (245, 210, 40)}

    elif isinstance(fighter, AmericanNinja):
        if hasattr(fighter, "dog") and fighter.dog and getattr(fighter.dog, "state", "") == "KNOCKED_OUT":
            timer = max(0.0, getattr(fighter.dog, "state_timer", 0.0))
            return {"name": "Cão Yamato KO", "timer": timer, "max_cd": 2.0, "color": (240, 60, 60), "warning": True}
        dog_cd = getattr(getattr(fighter, "dog", None), "cooldown_timer", 0.0)
        timer = max(0.0, dog_cd)
        return {"name": "Yamato Dash", "timer": timer, "max_cd": 3.0, "color": (220, 70, 70)}

    elif isinstance(fighter, SaitouSamurai):
        timer = max(0.0, getattr(fighter, "zeroshiki_timer", 0.0))
        cd = getattr(fighter, "zeroshiki_cooldown", 2.5)
        return {"name": "Zeroshiki", "timer": timer, "max_cd": cd, "color": (115, 205, 245)}

    elif isinstance(fighter, Rifleman):
        if not getattr(fighter, "has_ammo", True):
            return {"name": "Sem Pólvora", "timer": 1.0, "max_cd": 1.0, "color": (230, 80, 80), "warning": True}
        timer = max(0.0, getattr(fighter, "trap_timer", 0.0))
        cd = getattr(fighter, "trap_cooldown", 5.0)
        return {"name": "Armadilha", "timer": timer, "max_cd": cd, "color": (225, 165, 80)}

    elif isinstance(fighter, PurpleNinja):
        timer = max(0.0, getattr(fighter, "chain_timer", 0.0))
        cd = getattr(fighter, "chain_cooldown", 3.0)
        return {"name": "Corrente Foice", "timer": timer, "max_cd": cd, "color": (185, 110, 245)}

    elif isinstance(fighter, GrayNinja):
        m_timer = max(0.0, getattr(fighter, "mine_timer", 0.0))
        if m_timer > 0:
            return {"name": "Mina Remota", "timer": m_timer, "max_cd": getattr(fighter, "mine_cooldown", 2.2), "color": (175, 185, 195)}
        b_timer = max(0.0, getattr(fighter, "bomb_timer", 0.0))
        if b_timer > 0:
            return {"name": "Bomba 3D", "timer": b_timer, "max_cd": getattr(fighter, "bomb_cooldown", 0.50), "color": (220, 140, 50)}
        timer = max(0.0, getattr(fighter, "smoke_timer", 0.0))
        cd = getattr(fighter, "smoke_cooldown", 2.0)
        return {"name": "Fumaça", "timer": timer, "max_cd": cd, "color": (160, 170, 180)}

    elif isinstance(fighter, Kabuki):
        p_timer = max(0.0, getattr(fighter, "poison_cooldown_timer", 0.0))
        if p_timer > 0:
            return {"name": "Dokukiri", "timer": p_timer, "max_cd": getattr(fighter, "poison_cooldown", 3.5), "color": (80, 230, 120)}
        timer = max(0.0, getattr(fighter, "decoy_cooldown_timer", 0.0))
        cd = 3.0
        return {"name": "Kawarimi", "timer": timer, "max_cd": cd, "color": (210, 70, 150)}

    elif isinstance(fighter, KyudoArcher):
        v_timer = max(0.0, getattr(fighter, "volley_cooldown_timer", getattr(fighter, "sacred_volley_cooldown_timer", 0.0)))
        v_cd = getattr(fighter, "volley_cooldown", getattr(fighter, "sacred_volley_cooldown", 4.5))
        if v_timer > 0:
            return {"name": "Chuva Sagrada", "timer": v_timer, "max_cd": v_cd, "color": (255, 215, 60)}
        r_timer = max(0.0, getattr(fighter, "rope_timer", 0.0))
        if r_timer > 0:
            return {"name": "Flecha Corda", "timer": r_timer, "max_cd": getattr(fighter, "rope_cooldown", 2.0), "color": (210, 185, 120)}
        a_timer = max(0.0, getattr(fighter, "arrow_cooldown_timer", 0.0))
        if a_timer > 0:
            return {"name": "Flecha Yumi", "timer": a_timer, "max_cd": getattr(fighter, "arrow_cooldown", 1.20), "color": (100, 215, 140)}
        return {"name": "Chuva Sagrada", "timer": v_timer, "max_cd": v_cd, "color": (255, 215, 60)}

    elif isinstance(fighter, PirateSwordswoman):
        timer = max(0.0, getattr(fighter, "cannon_cooldown_timer", 0.0))
        cd = getattr(fighter, "cannon_cooldown", 4.5)
        return {"name": "Canhão Naval", "timer": timer, "max_cd": cd, "color": (240, 110, 45)}

    elif isinstance(fighter, Musketeer):
        f_timer = max(0.0, getattr(fighter, "flintlock_timer", 0.0))
        if f_timer > 0:
            return {"name": "Pederneira", "timer": f_timer, "max_cd": getattr(fighter, "flintlock_cooldown", 4.5), "color": (245, 195, 60)}
        timer = max(0.0, getattr(fighter, "cape_timer", 0.0))
        cd = getattr(fighter, "cape_cooldown", 2.4)
        return {"name": "Floreio Capa", "timer": timer, "max_cd": cd, "color": (80, 160, 255)}

    elif isinstance(fighter, RenMonk):
        timer = max(0.0, getattr(fighter, "kiai_timer", 0.0))
        cd = getattr(fighter, "kiai_cooldown", 3.2)
        return {"name": "Grito Kiai", "timer": timer, "max_cd": cd, "color": (245, 175, 45)}

    elif isinstance(fighter, ChiyoKunoichi):
        timer = max(0.0, getattr(fighter, "mai_timer", 0.0))
        cd = getattr(fighter, "mai_cooldown", 2.8)
        return {"name": "Dança Mai", "timer": timer, "max_cd": cd, "color": (60, 220, 180)}

    return None

# Azimute atual da câmera, lido pelas conversões de entrada (W continua sendo "para cima na tela")
_view_azimuth = 0.0
CAMERA_ORBIT_SPEED = math.radians(60.0)

def get_player_aim_target(fighter, controls, prefix: str, distance: float = 4.0, move_dir: tuple[float, float] | None = None) -> tuple[float, float]:
    """Calcula as coordenadas de mira para o ataque com base na entrada direcional ativa ou na orientação do lutador."""
    if move_dir and (move_dir[0] != 0 or move_dir[1] != 0):
        dwx, dwy = input_to_world_direction(move_dir[0], move_dir[1], _view_azimuth)
        return fighter.wx + dwx * distance, fighter.wy + dwy * distance
    keys = pygame.key.get_pressed()
    dx = keys[controls[f"{prefix}_RIGHT"]] - keys[controls[f"{prefix}_LEFT"]]
    dy = keys[controls[f"{prefix}_DOWN"]] - keys[controls[f"{prefix}_UP"]]
    if dx != 0 or dy != 0:
        dwx, dwy = input_to_world_direction(dx, dy, _view_azimuth)
        return fighter.wx + dwx * distance, fighter.wy + dwy * distance
    return fighter.wx + fighter.facing_x * distance, fighter.wy + fighter.facing_y * distance

def play_sfx(event: SoundEvent):
    """Dispara um efeito sonoro feudal através do SoundManager global."""
    try:
        SoundManager.get_instance().play(event)
    except Exception:
        pass

def execute_fighter_attack(fighter, aim_x: float, aim_y: float, projectiles: list, particles: list):
    """Executa a ação primária de ataque do lutador em direção às coordenadas de mira."""
    if isinstance(fighter, RedSamurai):
        fighter.trigger_iai_attack(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, BlueSamurai):
        fighter.trigger_combo_attack(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, YellowNinja):
        if fighter.has_kunai:
            if fighter.state == "JUMP":
                fighter.trigger_midair_throw(aim_x, aim_y, projectiles)
            else:
                fighter.trigger_standing_throw(aim_x, aim_y, projectiles)
            play_sfx(SoundEvent.KUNAI_THROW)
        else:
            fighter.trigger_thrust_attack(aim_x, aim_y)
            play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, AmericanNinja):
        fighter.trigger_shuriken(aim_x, aim_y, projectiles)
        play_sfx(SoundEvent.KUNAI_THROW)
    elif isinstance(fighter, GrayNinja):
        fighter.trigger_throw_bomb(aim_x, aim_y, projectiles)
        play_sfx(SoundEvent.BOMB_FUSE)
    elif isinstance(fighter, PurpleNinja):
        fighter.trigger_kama_strike(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, SaitouSamurai):
        fighter.trigger_gatotsu_thrust(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, Rifleman):
        if fighter.has_ammo:
            fighter.trigger_shoot(aim_x, aim_y, projectiles, particles)
            play_sfx(SoundEvent.GUNSHOT)
        else:
            fighter.trigger_rifle_butt(aim_x, aim_y, particles)
            play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, Kabuki):
        fighter.trigger_fan_strike(aim_x, aim_y, particles)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, KyudoArcher):
        fighter.trigger_bow_draw(aim_x, aim_y, projectiles)
        play_sfx(SoundEvent.BOW_RELEASE)
    elif isinstance(fighter, PirateSwordswoman):
        fighter.trigger_cutlass_cleave(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, Musketeer):
        fighter.trigger_fleche_thrust(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, RenMonk):
        fighter.trigger_punch_combo(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, ChiyoKunoichi):
        fighter.trigger_scissor_slash(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)

def execute_fighter_secondary(fighter, aim_x: float, aim_y: float, dwx: float, dwy: float, projectiles: list, particles: list, decoys: list, poison_clouds: list, powder_traps: list, opponent=None, game_map=None, banners: list = None):
    """Executa a Ação Secundária (Técnica Especial / Defesa / Contra-ataque) do combatente."""
    if isinstance(fighter, RedSamurai):
        # Kenshi: Ryuu Tsui Sen (Salto vertical e corte descendente devastador)
        fighter.trigger_ryuu_tsui_sen(aim_x, aim_y, particles=particles, banners=banners, opponent=opponent)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, BlueSamurai):
        fighter.set_facing(aim_x, aim_y)
        fighter.trigger_parry()
        play_sfx(SoundEvent.PARRY)
    elif isinstance(fighter, YellowNinja):
        if fighter.state == "JUMP" and fighter.has_kunai:
            fighter.trigger_midair_throw(aim_x, aim_y, projectiles)
            play_sfx(SoundEvent.KUNAI_THROW)
        else:
            fighter.trigger_jump(aim_x, aim_y, projectiles)
            play_sfx(SoundEvent.DASH_ROLL)
    elif isinstance(fighter, AmericanNinja):
        fighter.trigger_dog_attack(aim_x, aim_y)
        play_sfx(SoundEvent.DOG_BARK)
    elif isinstance(fighter, GrayNinja):
        all_f = [fighter, opponent] if opponent else [fighter]
        fighter.trigger_remote_mine(aim_x, aim_y, projectiles, fighters=all_f, particles=particles, banners=banners)
        play_sfx(SoundEvent.BOMB_FUSE)
    elif isinstance(fighter, PurpleNinja):
        fighter.start_chain_shield(aim_x, aim_y)
        play_sfx(SoundEvent.CHAIN_SPIN)
    elif isinstance(fighter, SaitouSamurai):
        fighter.trigger_zeroshiki(aim_x, aim_y)
        play_sfx(SoundEvent.SWORD_SLASH)
    elif isinstance(fighter, Rifleman):
        # Teppo: Black Powder Ground Trap (Trilha de pólvora inflamável no solo)
        fighter.trigger_powder_trap(aim_x, aim_y, powder_traps, particles)
        play_sfx(SoundEvent.BOMB_FUSE)
    elif isinstance(fighter, Kabuki):
        # Okuni: Dokukiri (Sopro de névoa venenosa com leques de ferro)
        fighter.trigger_dokukiri(aim_x, aim_y, poison_clouds)
        play_sfx(SoundEvent.POISON_BREATH)
    elif isinstance(fighter, KyudoArcher):
        # Tomoe: Chuva / Salva de Flechas Sagradas em Arco (Mecanismo idêntico ao da Anne: Hold & Release)
        fighter.start_sacred_volley(aim_x, aim_y)
        play_sfx(SoundEvent.BOW_RELEASE)
    elif isinstance(fighter, PirateSwordswoman):
        # Anne Bonny: Naval Artillery Strike (Hold & release orbital cannonball)
        fighter.start_cannon_strike(aim_x, aim_y)
    elif isinstance(fighter, Musketeer):
        # Julie: pederneira quando pronta; com ela recarregando, floreio de capa (repele e desvia projéteis)
        result = fighter.trigger_secondary(aim_x, aim_y, projectiles, particles=particles, opponent=opponent)
        if result == "shot":
            play_sfx(SoundEvent.FLINTLOCK_FIRE)
        elif result == "flip":
            play_sfx(SoundEvent.DODGE_WHOOSH)
    elif isinstance(fighter, RenMonk):
        # Ren: Grito Kiai de 360° que repele projéteis e atordoa
        fighter.trigger_kiai_shout(particles=particles, banners=banners, opponent=opponent)
        play_sfx(SoundEvent.DODGE_WHOOSH)
    elif isinstance(fighter, ChiyoKunoichi):
        # Chiyo: Dança Mai giratória com duas Nodachis em vórtice circular
        fighter.trigger_nodachi_mai(aim_x, aim_y, particles=particles, banners=banners, opponent=opponent)
        play_sfx(SoundEvent.SWORD_SLASH)

def execute_fighter_roll(fighter, dwx: float, dwy: float, aim_x: float, aim_y: float, particles: list, decoys: list = None, game_map=None, opponent=None, banners=None):
    """Executa a Terceira Ação (Roll / Dash dedicado) com invulnerabilidade temporária (i-frames)."""
    play_sfx(SoundEvent.DASH_ROLL)
    if isinstance(fighter, RedSamurai):
        fighter.trigger_dash(dwx, dwy)
    elif isinstance(fighter, Kabuki):
        fighter.trigger_kabuki_roll(dwx, dwy, particles=particles, decoys=decoys)
    elif isinstance(fighter, Rifleman):
        fighter.trigger_tumble_roll(dwx, dwy, particles)
    elif isinstance(fighter, PirateSwordswoman):
        fighter.trigger_roll(dwx, dwy, particles)
    elif isinstance(fighter, KyudoArcher):
        # Tomoe: Flecha de corda para movimentação rápida
        fighter.start_rope_arrow_charge(aim_x, aim_y, game_map)
    else:
        # Demais personagens (BlueSamurai, YellowNinja, AmericanNinja, GrayNinja, PurpleNinja, SaitouSamurai)
        if hasattr(fighter, "trigger_roll"):
            fighter.trigger_roll(dwx, dwy, particles)

def execute_fighter_dash(fighter, aim_x: float, aim_y: float, dwx: float, dwy: float, projectiles: list, particles: list, decoys: list, opponent=None, game_map=None, poison_clouds=None, powder_traps=None):
    """Compatibilidade legada: direciona para a terceira ação de roll/dash dedicado."""
    execute_fighter_roll(fighter, dwx, dwy, aim_x, aim_y, particles, decoys=decoys, game_map=game_map)

def get_random_arena_spawns(game_map, min_distance: float = 7.0) -> tuple[tuple[float, float], tuple[float, float]]:
    """Duas posições válidas (chão firme) separadas por pelo menos min_distance, segundo a regra de spawn da arena."""
    return game_map.pick_spawns(min_distance)


def get_kyoto_arena_spawns(game_map, min_distance: float = 7.0) -> tuple[tuple[float, float], tuple[float, float]]:
    """Compatibilidade: a regra de spawn de cada arena (ex.: faixa da rua em Kyoto) vem do próprio spec."""
    return game_map.pick_spawns(min_distance)


def build_static_render_queue(current_map):
    """Constrói a fila ordenada de elementos estáticos do cenário (bambus, rochas, construções)."""
    queue = []
    for bamboo in current_map.bamboos:
        queue.append((bamboo.wx + bamboo.wy, 'bamboo', bamboo))
    for rock in current_map.rocks:
        queue.append((rock.wx + rock.wy, 'rock', rock))
    if current_map.well:
        queue.append((current_map.well.wx + current_map.well.wy, 'well', current_map.well))
    for tree in current_map.trees:
        queue.append((tree.wx + tree.wy, 'tree', tree))
    if hasattr(current_map, 'torii_gates'):
        for tg in current_map.torii_gates:
            queue.append((tg.wx + tg.wy, 'torii', tg))
    if hasattr(current_map, 'buildings'):
        for b in current_map.buildings:
            queue.append((b.wx + b.wy + b.depth * 0.5, 'building', b))
    if hasattr(current_map, 'lanterns'):
        for l in current_map.lanterns:
            queue.append((l.wx + l.wy, 'lantern', l))
    return queue


def static_item_center(item_type: str, obj) -> tuple[float, float]:
    """Ponto de referência para ordenar um item estático quando a câmera está girada."""
    if item_type == 'building':
        return obj.wx + obj.width * 0.5, obj.wy + obj.depth * 0.5
    return obj.wx, obj.wy


def run_game():
    global _view_azimuth
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"{TITLE} (Demo)" if is_demo() else TITLE)
    clock = pygame.time.Clock()
    quality.load_effects_quality(quality.SETTINGS_PATH)

    # Tela de Carregamento Estilizada com feedback imediato ao usuário
    loading_screen = LoadingScreen(screen)
    loading_screen.update(0.12, "Iniciando motor e renderizador...", delay_ms=40)

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    # Dispositivos de Entrada e Viewport Responsivo
    ctrl_mgr = get_controller_manager()
    touch_controls = TouchControls()
    scaler = DisplayScaler(SCREEN_WIDTH, SCREEN_HEIGHT)

    loading_screen.update(0.30, "Carregando configurações de controles...", delay_ms=40)

    # Carregar configurações de controles salvas (Fase 3 / Item 8)
    saved_cfg = load_controls_config()
    controls = dict(DEFAULT_CONTROLS)
    for k, v in saved_cfg.get("keyboard", {}).items():
        if k in controls:
            controls[k] = int(v)
    if "controllers" in saved_cfg:
        ctrl_mgr.apply_saved_mappings(saved_cfg["controllers"])
    if touch_controls and "touch_mode" in saved_cfg:
        touch_controls.mode = saved_cfg["touch_mode"]

    ai_difficulty = saved_cfg.get("ai_difficulty", "normal")
    settings_menu = SettingsMenu(controls, touch_controls=touch_controls, ai_difficulty=ai_difficulty)
    pause_menu = PauseMenu()
    match_intro = MatchIntro()

    loading_screen.update(0.50, "Carregando atmosfera Sumi-e e tela inicial...", delay_ms=40)
    title_screen = SumieTitleScreen()

    loading_screen.update(0.72, "Carregando retratos e atributos dos 12 guerreiros...", delay_ms=50)
    preload_portraits()
    char_select_screen = CharacterSelectScreen(ai_difficulty=ai_difficulty)

    loading_screen.update(0.90, "Sintonizando arenas e cenários dinâmicos...", delay_ms=40)
    arena_select_screen = ArenaSelectScreen()

    loading_screen.update(1.0, "Pronto! Entrando no Bakumatsu...", delay_ms=60)

    opening_screen = OpeningVideoScreen()
    if not opening_screen.is_finished:
        game_state = STATE_OPENING_VIDEO
    else:
        game_state = STATE_TITLE
    selected_arena_id = ARENA_KYOTO
    demo_start_pending = False

    # Dados da Partida
    p1_char_id = CHAR_KENSHIN
    p2_char_id = CHAR_MUSASHI
    vs_ai_mode = True
    score_p1 = 0
    score_p2 = 0

    p1 = None
    p2 = None
    game_map = None
    camera = None
    combat_system = CombatSystem()
    cinematic_director = CinematicDirector()
    outcome_seq = OutcomeSequence()
    cine_beats = {}  # batidas de SFX/partículas das animações de apresentação e vitória (7.3/7.4)
    clash_system = ClashSystem()
    round_intro = RoundIntroScreen()
    round_result_screen = RoundResultScreen()
    ai = SamuraiAI(difficulty=ai_difficulty)

    particles = []
    banners = []
    projectiles = []
    ambient_leaves = []
    lighting_fx = None
    terrain_fx = TerrainFX()
    fog = None
    powder_pouches = []
    decoys = []
    poison_clouds = []
    powder_traps = []

    round_winner = None
    game_time = 0.0
    round_start_timer = 1.8
    round_start_shaken = False
    round_intro_timer = 0.0
    round_started = False
    match_winner = None
    round_number = 1

    # Arcade (8.1): a jornada vive em `arcade_run`; as regras ficam em src/arcade/arcade_mode.py
    arcade_run: ArcadeRun | None = None
    arcade_start_level = 1
    arcade_fight_over = None      # "won" | "lost" quando a luta atual terminou
    arcade_round_status = None    # último resultado de `on_round_end`
    arcade_round_reported = False
    round_clock = 0.0
    arcade_difficulty_screen = ArcadeDifficultyScreen()
    arcade_bracket = ArcadeBracketScreen()
    arcade_credits_screen = ArcadeCreditsScreen()
    arcade_result_screen = ArcadeResultScreen()

    static_render_queue = []

    def start_new_match(play_intro: bool = False):
        nonlocal p1, p2, game_map, camera, particles, banners, projectiles, ambient_leaves, lighting_fx, terrain_fx, fog, round_winner, round_start_timer, round_start_shaken, round_intro_timer, round_started, powder_pouches, decoys, poison_clouds, powder_traps, static_render_queue, arcade_round_reported, round_clock
        game_map = create_arena(selected_arena_id)
        (p1_wx, p1_wy), (p2_wx, p2_wy) = game_map.pick_spawns(min_distance=7.0)
        if p2_char_id == CHAR_BOSS:
            (p1_wx, p1_wy), (p2_wx, p2_wy) = (10.5, 17.5), (10.5, 7.5)  # o chefe nasce do monte; o jogador, na borda oposta

        p1 = create_fighter(p1_char_id, wx=p1_wx, wy=p1_wy)
        p2 = create_fighter(p2_char_id, wx=p2_wx, wy=p2_wy)
        p1.set_facing(p2.wx, p2.wy)
        p2.set_facing(p1.wx, p1.wy)
        if isinstance(p2, BossOni):
            if arcade_run is not None:
                p2.set_difficulty(arcade_run.difficulty_name)
                p2.set_phase(arcade_run.boss_phase)
        if arcade_run is not None and p2_char_id == p1_char_id:
            p2.mirror_alt = True
            p2.name = f"{p2.name} ({t('arcade_mirror_tag')})"
        arcade_round_reported = False
        round_clock = 0.0
        for f in (p1, p2):
            if isinstance(f, Kabuki):
                f.registered_decoys = decoys
        camera = game_map.attach_camera(Camera(target_wx=(p1_wx + p2_wx) / 2.0, target_wy=(p1_wy + p2_wy) / 2.0))
        particles.clear()
        banners.clear()
        projectiles.clear()
        decoys.clear()
        poison_clouds.clear()
        powder_traps.clear()
        powder_pouches = PowderPouch.create_arena_pouches(game_map, [p1, p2], total_pouches=3)
        lighting_fx = ArenaLighting(game_map)
        terrain_fx = TerrainFX()
        fog = game_map.fog = FogVolume(game_map)
        set_wind_source(lambda x, y: game_map.wind_at(x, y, game_time))
        ambient_leaves = [AmbientLeafParticle(game_map.cols, game_map.rows, game_map.spec.drift_petals)
                          for _ in range(game_map.spec.drift_count)]
        round_winner = None
        round_start_timer = 1.8
        round_start_shaken = False
        round_intro_timer = 2.0
        round_started = False
        cinematic_director.reset_round()
        outcome_seq.reset()
        cine_beats.clear()
        static_render_queue = build_static_render_queue(game_map)
        round_intro.start(
            p1.name, p2.name,
            p1_color=get_fighter_color(p1), p2_color=get_fighter_color(p2),
            round_label=f"RODADA {round_number}"
        )
        match_intro.active = False
        if play_intro:
            # A introdução orbital substitui o pergaminho do round 1 e só ocorre ao iniciar uma batalha
            round_intro_timer = 0.0
            match_intro.start(
                game_map.intro_stage_point(), ((p1_wx, p1_wy), (p2_wx, p2_wy)),
                (p1.name, p2.name), (p1_char_id, p2_char_id),
                (get_fighter_color(p1), get_fighter_color(p2)), vs_ai_mode
            )
        sound_mgr.play_music(game_map.music)

    def request_rematch():
        """Entregável 5.3: reinicia a partida inteira (placar e rounds zerados) após o fim de uma partida Melhor-de-3."""
        nonlocal score_p1, score_p2, match_winner, round_number
        score_p1 = 0
        score_p2 = 0
        match_winner = None
        round_number = 1
        round_result_screen.hide()
        start_new_match()

    def request_next_round():
        """Entregável 5.3: avança para o próximo round da mesma partida (placar preservado)."""
        nonlocal round_number
        round_number += 1
        start_new_match()

    def save_arcade_run():
        data = arcade_save.load()
        data["current_run"] = arcade_run.to_dict() if arcade_run is not None else None
        arcade_save.save(data)

    def leave_arcade():
        """Sai do Arcade de volta ao título; a dificuldade do Versus volta ao valor salvo."""
        nonlocal arcade_run, arcade_fight_over, arcade_round_status, game_state, match_winner
        arcade_run = None
        arcade_fight_over = None
        arcade_round_status = None
        match_winner = None
        char_select_screen.arcade_mode = False
        ai.set_difficulty(settings_menu.ai_difficulty)
        round_result_screen.hide()
        pause_menu.close()
        sound_mgr.play_music(MusicTrack.TITLE_THEME)
        game_state = STATE_TITLE

    def abandon_arcade():
        data = arcade_save.load()
        data["current_run"] = None
        arcade_save.save(data)
        leave_arcade()

    def open_arcade_bracket(banner=None, gained=0):
        nonlocal game_state
        arcade_bracket.open(arcade_run, banner, gained)
        sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
        game_state = STATE_ARCADE_BRACKET

    def begin_arcade_fight():
        """Prepara e inicia a luta atual da jornada (arena, lutadores, IA) com a introdução orbital."""
        nonlocal p1_char_id, p2_char_id, vs_ai_mode, selected_arena_id, score_p1, score_p2, match_winner
        nonlocal round_number, arcade_fight_over, arcade_round_status, game_state
        fight = arcade_run.current_fight()
        selected_arena_id = fight.arena_id
        p1_char_id = arcade_run.player_char
        p2_char_id = arcade_run.current_opponent()
        vs_ai_mode = True
        ai.set_difficulty(arcade_run.difficulty_name)
        score_p1 = score_p2 = 0
        match_winner = None
        round_number = 1
        arcade_fight_over = None
        arcade_round_status = None
        round_result_screen.hide()
        start_new_match(play_intro=True)
        game_state = STATE_DUEL_PLAYING

    def advance_arcade_opponent():
        """Desafios 9 e 10: próximo oponente na mesma arena, com o placar de rounds zerado."""
        nonlocal p2_char_id, score_p1, score_p2, round_number, arcade_round_status
        p2_char_id = arcade_run.current_opponent()
        score_p1 = score_p2 = 0
        round_number = 1
        arcade_round_status = None
        start_new_match()

    def finish_arcade_fight():
        """Fim da luta: vitória avança as chaves (ou fecha a jornada), derrota oferece o Continue."""
        nonlocal game_state
        if arcade_fight_over == "lost":
            open_arcade_bracket("defeat")
            return
        gained = arcade_run.stats[-1]["score"] if arcade_run.stats else 0
        if arcade_run.is_finished:
            data = arcade_save.load()
            rank = arcade_save.add_high_score(data, arcade_run)
            data["current_run"] = None
            arcade_save.save(data)
            arcade_credits_screen.open(arcade_run, rank, data["high_scores"])
            sound_mgr.play_music(MusicTrack.TITLE_THEME)
            game_state = STATE_ARCADE_CREDITS
        else:
            save_arcade_run()
            open_arcade_bracket("cleared", gained)

    def request_restart():
        """Ponto único de reinício: decide entre revanche completa (partida encerrada) ou próximo round."""
        if arcade_run is not None:
            if arcade_fight_over is not None:
                if outcome_seq.active or outcome_seq.pending:
                    outcome_seq.skip()
                    OutcomeSequence.restore_classic(camera)
                else:
                    finish_arcade_fight()
            elif arcade_round_status == NEXT_OPPONENT:
                advance_arcade_opponent()
            else:
                request_next_round()
            return
        if match_winner is not None:
            if outcome_seq.active or outcome_seq.pending:
                outcome_seq.skip()
                OutcomeSequence.restore_classic(camera)
            elif round_result_screen.can_accept_rematch():
                request_rematch()
        else:
            request_next_round()

    def draw_world_queue(render_queue):
        """Ordena (painter's algorithm) e desenha os itens do cenário/entidades já projetados pela câmera."""
        render_queue.sort(key=lambda item: item[0])

        for _, item_type, obj in render_queue:
            if item_type in ('bamboo', 'building', 'lantern'):
                obj.render(screen, camera, game_time)
            elif item_type == 'fighter' and getattr(obj, 'state', None) == STATE_FALL:
                render_falling_fighter(screen, obj, camera)
            elif item_type == 'fighter' and getattr(obj, 'fell_into_pit', False):
                continue
            elif item_type == 'fighter' and fog is not None and obj.is_alive and (vis := fog.visibility_at(obj.wx, obj.wy)) < 0.97:
                saved_alpha = obj.alpha
                obj.alpha = int(saved_alpha * vis)
                try:
                    obj.render(screen, camera)
                finally:
                    obj.alpha = saved_alpha
            elif item_type == 'pouch':
                obj.render(screen, camera, font_small)
            elif getattr(obj, 'animated', False):  # rochas animadas (ex.: fonte barroca)
                obj.render(screen, camera, game_time)
            else:
                obj.render(screen, camera)

    def draw_world_ambience():
        """Folhas ao vento, elementos no ar da arena e, por cima de tudo no mundo, iluminação e atmosfera (6.4)."""
        for leaf in ambient_leaves:
            leaf.render(screen, camera)

        game_map.render_overhead(screen, camera, game_time)
        if lighting_fx is not None:
            lighting_fx.render(screen, camera, game_time)

    def run_cine_beat(name, fighter):
        """Executa uma batida (SFX ou partículas) de uma animação de apresentação/vitória."""
        kind, _, arg = name.partition(":")
        if kind == "sfx":
            ev = getattr(SoundEvent, arg.upper(), None)
            if ev is not None:
                play_sfx(ev)
        elif kind == "fx" and arg == "smoke":
            for _ in range(10):
                particles.append(SmokeParticle(fighter.wx + random.uniform(-0.3, 0.3), fighter.wy + random.uniform(-0.3, 0.3),
                                               wz=random.uniform(0.1, 0.9), color=(150, 155, 165)))
        elif kind == "fx" and arg == "petals":
            for _ in range(14):
                particles.append(SparkParticle(fighter.wx + random.uniform(-0.5, 0.5), fighter.wy + random.uniform(-0.5, 0.5),
                                               random.uniform(0.8, 1.6), color=(255, 190, 205)))
        elif kind == "fx" and arg == "sparks":
            for _ in range(8):
                particles.append(SparkParticle(fighter.wx, fighter.wy, random.uniform(0.6, 1.4)))

    def step_idle_fighter(f, opp, dt_):
        """Avança só a animação do lutador (introdução cinematográfica), sem física de combate e sem drenar cooldowns."""
        if isinstance(f, PirateSwordswoman):
            f.update(0.0, game_map, particles, opponent=opp, banners=banners)
        elif isinstance(f, (SaitouSamurai, Rifleman, Kabuki, Musketeer, GrayNinja)):
            f.update(0.0, game_map, particles)
        elif isinstance(f, (BlueSamurai, KyudoArcher)):
            f.update(0.0, game_map, particles, projectiles)
        else:
            f.update(0.0, game_map)
    sound_mgr = SoundManager.get_instance()
    audio_cfg = saved_cfg.get("audio", {})
    sound_mgr.set_master_volume(audio_cfg.get("master", 1.0))
    sound_mgr.set_sfx_volume(audio_cfg.get("sfx", 1.0))
    sound_mgr.set_bgm_volume(audio_cfg.get("bgm", 0.7))
    if game_state == STATE_TITLE:
        sound_mgr.play_music(MusicTrack.TITLE_THEME)

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)
        sound_mgr.update(dt)

        # -------------------------------------------------------------
        # VÍDEO CINEMATOGRÁFICO DE ABERTURA
        # -------------------------------------------------------------
        if game_state == STATE_OPENING_VIDEO:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    opening_screen.stop()
                else:
                    if opening_screen.handle_event(event):
                        game_state = STATE_TITLE
                        sound_mgr.play_music(MusicTrack.TITLE_THEME)
                        break

            if game_state == STATE_OPENING_VIDEO:
                opening_screen.update(dt)
                if opening_screen.is_finished:
                    game_state = STATE_TITLE
                    sound_mgr.play_music(MusicTrack.TITLE_THEME)
                else:
                    opening_screen.render(screen)
                    pygame.display.flip()
                    continue

        # -------------------------------------------------------------
        # TELA DE TÍTULO SUMI-E & SELETOR DE MODOS
        # -------------------------------------------------------------
        if game_state == STATE_TITLE:
            if settings_menu.is_open:
                for event in pygame.event.get():
                    ctrl_mgr.handle_event(event)
                    if event.type == pygame.QUIT:
                        running = False
                    else:
                        settings_menu.handle_event(event)
                settings_menu.update(dt)
                if not settings_menu.is_open:
                    char_select_screen.ai_difficulty = settings_menu.ai_difficulty
                    ai.set_difficulty(settings_menu.ai_difficulty)
                title_screen.render(screen, font_large, font_mid, font_small)
                settings_menu.render(screen, font_large, font_mid, font_small)
                pygame.display.flip()
                continue

            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    action = title_screen.handle_event(event)
                    if action == "VERSUS":
                        play_sfx(SoundEvent.MENU_SELECT)
                        char_select_screen.reset()
                        sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
                        game_state = STATE_CHAR_SELECT
                    elif action == "ARCADE":
                        play_sfx(SoundEvent.MENU_SELECT)
                        saved = arcade_save.load()
                        saved_run = saved["current_run"]
                        try:
                            if saved_run is not None:
                                ArcadeRun.from_dict(saved_run)
                        except (ValueError, KeyError, TypeError):
                            saved_run = None
                        arcade_difficulty_screen.open(
                            {"easy": 0, "normal": 1, "hard": 2}.get(settings_menu.ai_difficulty, 1), saved_run, saved["high_scores"])
                        game_state = STATE_ARCADE_DIFFICULTY
                    elif action == "OPTIONS":
                        play_sfx(SoundEvent.MENU_SELECT)
                        settings_menu.open()
                    elif action == "QUIT":
                        running = False

            title_screen.update(dt)
            title_screen.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # ARCADE (8.1): dificuldade, seleção do lutador, chaves e resultado final
        # -------------------------------------------------------------
        if game_state == STATE_ARCADE_DIFFICULTY:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    continue
                result = arcade_difficulty_screen.handle_event(event, ctrl_mgr)
                if result == "BACK":
                    play_sfx(SoundEvent.MENU_SELECT)
                    game_state = STATE_TITLE
                elif result == "RESUME":
                    play_sfx(SoundEvent.MENU_SELECT)
                    arcade_run = ArcadeRun.from_dict(arcade_difficulty_screen.saved_run)
                    open_arcade_bracket()
                elif isinstance(result, tuple):
                    play_sfx(SoundEvent.MENU_SELECT)
                    arcade_start_level = result[1]
                    char_select_screen.arcade_mode = True
                    char_select_screen.vs_ai = True
                    char_select_screen.reset()
                    sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
                    game_state = STATE_ARCADE_CHAR_SELECT
                if game_state != STATE_ARCADE_DIFFICULTY:
                    break
            if game_state == STATE_ARCADE_DIFFICULTY:
                arcade_difficulty_screen.render(screen)
                pygame.display.flip()
            continue

        if game_state == STATE_ARCADE_CHAR_SELECT:
            start_arcade = False
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    continue
                result = char_select_screen.handle_event(event)
                if result == "BACK":
                    play_sfx(SoundEvent.MENU_SELECT)
                    char_select_screen.arcade_mode = False
                    game_state = STATE_ARCADE_DIFFICULTY
                elif result:
                    start_arcade = True
            if char_select_screen.update(dt):
                start_arcade = True
            if start_arcade and game_state == STATE_ARCADE_CHAR_SELECT:
                play_sfx(SoundEvent.MENU_SELECT)
                chosen, _, _ = char_select_screen.get_selected_characters()
                char_select_screen.arcade_mode = False
                arcade_run = ArcadeRun(player_char=chosen, difficulty_start=arcade_start_level, seed=random.randrange(2 ** 31))
                save_arcade_run()
                open_arcade_bracket()
            elif game_state == STATE_ARCADE_CHAR_SELECT:
                char_select_screen.render(screen, font_large, font_mid, font_small)
                pygame.display.flip()
            continue

        if game_state == STATE_ARCADE_BRACKET:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    continue
                result = arcade_bracket.handle_event(event, ctrl_mgr)
                if result == "FIGHT":
                    play_sfx(SoundEvent.MENU_SELECT)
                    if arcade_bracket.banner == "defeat":
                        arcade_run.on_continue()
                        save_arcade_run()
                    begin_arcade_fight()
                    break
                if result == "ABANDON":
                    play_sfx(SoundEvent.MENU_SELECT)
                    abandon_arcade()
                    break
            if game_state == STATE_ARCADE_BRACKET:
                arcade_bracket.update(dt)
                arcade_bracket.render(screen)
                pygame.display.flip()
            continue

        if game_state == STATE_ARCADE_CREDITS:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if arcade_credits_screen.handle_event(event, ctrl_mgr) == "DONE":
                    play_sfx(SoundEvent.MENU_SELECT)
                    arcade_result_screen.open(arcade_credits_screen.run, arcade_credits_screen.rank, arcade_credits_screen.high_scores)
                    game_state = STATE_ARCADE_RESULT
                    break
            if game_state == STATE_ARCADE_CREDITS:
                if arcade_credits_screen.update(dt) == "DONE":
                    arcade_result_screen.open(arcade_credits_screen.run, arcade_credits_screen.rank, arcade_credits_screen.high_scores)
                    game_state = STATE_ARCADE_RESULT
                else:
                    arcade_credits_screen.render(screen)
                    pygame.display.flip()
            continue

        if game_state == STATE_ARCADE_RESULT:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    continue
                if arcade_result_screen.handle_event(event, ctrl_mgr) == "DONE":
                    play_sfx(SoundEvent.MENU_SELECT)
                    leave_arcade()
                    break
            if game_state == STATE_ARCADE_RESULT:
                arcade_result_screen.update(dt)
                arcade_result_screen.render(screen)
                pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # TELA DE SELEÇÃO DE PERSONAGENS
        # -------------------------------------------------------------
        if game_state == STATE_CHAR_SELECT:
            start_match = False
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                else:
                    result = char_select_screen.handle_event(event)
                    if result == "BACK":
                        play_sfx(SoundEvent.MENU_SELECT)
                        sound_mgr.play_music(MusicTrack.TITLE_THEME)
                        game_state = STATE_TITLE
                    elif result:
                        start_match = True

            # O sorteio do Aleatório termina dentro de update(), que também pode iniciar a partida
            if char_select_screen.update(dt):
                start_match = True
            if start_match and game_state == STATE_CHAR_SELECT:
                play_sfx(SoundEvent.MENU_SELECT)
                p1_char_id, p2_char_id, vs_ai_mode = char_select_screen.get_selected_characters()
                ai.set_difficulty(char_select_screen.ai_difficulty)
                settings_menu.ai_difficulty = char_select_screen.ai_difficulty
                demo_start_pending = is_demo()
                game_state = STATE_ARENA_SELECT
            char_select_screen.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # TELA DE SELEÇÃO DE ARENA
        # -------------------------------------------------------------
        if game_state == STATE_ARENA_SELECT:
            if is_demo():
                # Demo: não há escolha de cenário; depois dos lutadores vai direto à arena da Kenshi
                if demo_start_pending:
                    selected_arena_id = DEMO_ARENA
                    score_p1 = 0
                    score_p2 = 0
                    match_winner = None
                    round_number = 1
                    round_result_screen.hide()
                    start_new_match(play_intro=True)
                    game_state = STATE_DUEL_PLAYING
                else:
                    char_select_screen.reset()
                    game_state = STATE_CHAR_SELECT
                demo_start_pending = False
                continue
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                else:
                    arena_choice = arena_select_screen.handle_event(event)
                    if arena_choice == "BACK":
                        play_sfx(SoundEvent.MENU_SELECT)
                        sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
                        game_state = STATE_CHAR_SELECT
                    elif arena_choice in arena_ids():
                        play_sfx(SoundEvent.MENU_SELECT)
                        selected_arena_id = arena_choice
                        score_p1 = 0
                        score_p2 = 0
                        match_winner = None
                        round_number = 1
                        round_result_screen.hide()
                        start_new_match(play_intro=True)
                        game_state = STATE_DUEL_PLAYING

            arena_select_screen.update(dt)
            arena_select_screen.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # TELA DE CONFIGURAÇÕES DE CONTROLES (OVERLAY)
        # -------------------------------------------------------------
        if settings_menu.is_open:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                else:
                    settings_menu.handle_event(event)

            settings_menu.update(dt)
            if not settings_menu.is_open:
                char_select_screen.ai_difficulty = settings_menu.ai_difficulty
                ai.set_difficulty(arcade_run.difficulty_name if arcade_run is not None else settings_menu.ai_difficulty)
            settings_menu.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # MENU DE PAUSA (ESC durante o duelo)
        # -------------------------------------------------------------
        if pause_menu.is_open:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    break
                action = pause_menu.handle_event(event, ctrl_mgr)
                if action is None:
                    continue
                play_sfx(SoundEvent.MENU_SELECT)
                if action == ACTION_SETTINGS:
                    settings_menu.open()
                elif action == ACTION_QUIT:
                    running = False
                elif action == ACTION_ABANDON:
                    abandon_arcade()
                else:
                    pause_menu.close()
                    if action == ACTION_ARENA:
                        sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
                        game_state = STATE_ARENA_SELECT
                    elif action == ACTION_FIGHTER:
                        char_select_screen.reset()
                        sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
                        game_state = STATE_CHAR_SELECT
                    elif action == ACTION_MAIN_MENU:
                        sound_mgr.play_music(MusicTrack.TITLE_THEME)
                        game_state = STATE_TITLE
                break

            if pause_menu.is_open:
                pause_menu.render(screen)
                pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # INTRODUÇÃO CINEMATOGRÁFICA DA BATALHA (câmera orbital, só no início da batalha)
        # -------------------------------------------------------------
        if match_intro.active:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause_menu.open(screen, arcade=arcade_run is not None, demo=is_demo())
                        break
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        match_intro.skip()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    match_intro.skip()
                elif event.type == pygame.JOYBUTTONDOWN:
                    if ctrl_mgr.is_event_menu_pause(event, 0) or getattr(event, "button", None) == 6:
                        pause_menu.open(screen, arcade=arcade_run is not None, demo=is_demo())
                        break
                    if ctrl_mgr.is_event_menu_confirm(event) or getattr(event, "button", None) == 0:
                        match_intro.skip()
            if pause_menu.is_open or not running:
                continue

            match_intro.update(dt)
            game_time += dt
            spawn_1, spawn_2 = match_intro.spawns

            if match_intro.active:
                intro_phase, _ = match_intro.phase()
                visible = match_intro.visible_fighters()
                stage_x, stage_y = match_intro.stage
                for idx, (fighter, opponent, spawn) in enumerate(((p1, p2, spawn_1), (p2, p1, spawn_2))):
                    if intro_phase in ("p1", "p2"):
                        fighter.wx, fighter.wy = (stage_x, stage_y) if visible[idx] else spawn
                        fighter.set_facing(stage_x + 1.0, stage_y + 1.0)
                    else:
                        fighter.wx, fighter.wy = spawn
                        fighter.set_facing(*((spawn_2 if idx == 0 else spawn_1)))
                    if visible[idx]:
                        step_idle_fighter(fighter, opponent, dt)
                        if intro_phase in ("p1", "p2"):
                            # Entregável 7.3: roteiro de apresentação do personagem durante o seu ato
                            ip = match_intro.fighter_progress()
                            key = ("intro", id(fighter))
                            if key not in cine_beats:
                                cine_beats[key] = BeatPlayer((p1_char_id, p2_char_id)[idx], "intro")
                            for beat in cine_beats[key].advance(ip):
                                run_cine_beat(beat, fighter)
                            fighter.state = STATE_INTRO
                            fighter.state_timer = ip
                            fighter.hitbox_active = False
                        elif fighter.state == STATE_INTRO:
                            fighter.state = STATE_IDLE
                            fighter.state_timer = 0.0
                    elif fighter.state == STATE_INTRO:
                        fighter.state = STATE_IDLE
                        fighter.state_timer = 0.0
                    on_stage = intro_phase in ("p1", "p2") and visible[idx]
                    fighter.wz = match_intro.stage_z if on_stage else 0.0

                for leaf in ambient_leaves:
                    leaf.update(dt, game_map.wind_at(leaf.wx, leaf.wy, game_time))
                particles[:] = [pt for pt in particles if pt.update(dt)]
                fog.update(dt, game_time)
                match_intro.apply_camera(camera)

                screen.fill(game_map.bg_color)
                game_map.render_terrain(screen, camera, game_time)
                intro_queue = [(camera.depth(*static_item_center(t_, o_)), t_, o_) for _, t_, o_ in static_render_queue]
                for idx, fighter in enumerate((p1, p2)):
                    if visible[idx]:
                        intro_queue.append((camera.depth(fighter.wx, fighter.wy), 'fighter', fighter))
                        if getattr(fighter, "dog", None):
                            fighter.dog.wx, fighter.dog.wy = fighter.wx - 0.9, fighter.wy + 0.4
                            intro_queue.append((camera.depth(fighter.dog.wx, fighter.dog.wy), 'dog', fighter.dog))
                for pt in particles:
                    if hasattr(pt, 'wx') and hasattr(pt, 'wy'):
                        intro_queue.append((camera.depth(pt.wx, pt.wy), 'particle', pt))
                intro_queue.extend(fog.queue_items(camera))
                draw_world_queue(intro_queue)
                draw_world_ambience()
                match_intro.render_overlay(screen)
                pygame.display.flip()
                continue

            # Fim da introdução: lutadores nas posições iniciais e câmera de volta à vista clássica
            p1.wx, p1.wy = spawn_1
            p2.wx, p2.wy = spawn_2
            p1.wz = p2.wz = 0.0
            for f_ in (p1, p2):
                if f_.state == STATE_INTRO:
                    f_.state = STATE_IDLE
                    f_.state_timer = 0.0
            cine_beats.clear()
            p1.set_facing(*spawn_2)
            p2.set_facing(*spawn_1)
            camera.zoom = 1.0
            camera.ground_z = 0.0
            camera.screen_y = SCREEN_HEIGHT // 2
            camera.set_azimuth(0.0)
            camera.wx, camera.wy = match_intro.mid

        # -------------------------------------------------------------
        # DUELO EM ANDAMENTO (GAME LOOP)
        # -------------------------------------------------------------
        touch_controls.reset_frame_triggers()

        real_dt = dt
        if arcade_run is not None:
            arcade_run.add_time(real_dt)
        if round_winner is None and round_start_timer <= 0 and round_intro_timer <= 0:
            round_clock += real_dt
        dt *= outcome_seq.time_scale()

        # Determinar direções ativas de movimentação/mira prévia
        keys = pygame.key.get_pressed()
        c1_dx, c1_dy = ctrl_mgr.get_movement(0)
        t_dx, t_dy = touch_controls.get_movement()
        k1_dx = keys[controls["P1_RIGHT"]] - keys[controls["P1_LEFT"]]
        k1_dy = keys[controls["P1_DOWN"]] - keys[controls["P1_UP"]]

        if math.hypot(c1_dx, c1_dy) > 0.05:
            p1_active_dir = (c1_dx, c1_dy)
        elif math.hypot(t_dx, t_dy) > 0.05:
            p1_active_dir = (t_dx, t_dy)
        else:
            p1_active_dir = (float(k1_dx), float(k1_dy))

        c2_dx, c2_dy = ctrl_mgr.get_movement(1)
        k2_dx = keys[controls["P2_RIGHT"]] - keys[controls["P2_LEFT"]]
        k2_dy = keys[controls["P2_DOWN"]] - keys[controls["P2_UP"]]
        if math.hypot(c2_dx, c2_dy) > 0.05:
            p2_active_dir = (c2_dx, c2_dy)
        else:
            p2_active_dir = (float(k2_dx), float(k2_dy))

        _view_azimuth = camera.azimuth
        p1_dwx, p1_dwy = input_to_world_direction(p1_active_dir[0], p1_active_dir[1], _view_azimuth)
        p2_dwx, p2_dwy = input_to_world_direction(p2_active_dir[0], p2_active_dir[1], _view_azimuth)

        # Atualização da Cinemática de Abertura de Round (Entregável 5.2) e do
        # Temporizador de Abertura de Round com Tremor de Tela (Item 10)
        if round_intro_timer > 0:
            round_intro_timer -= dt
            # A arena gira levemente e para na vista clássica quando o cronômetro acaba (get_rotation_angle devolve 0)
            camera.set_azimuth(math.radians(round_intro.get_rotation_angle(round_intro_timer)))
        elif round_start_timer > -0.5:
            round_start_timer -= dt
            if round_start_timer <= 0.6 and not round_start_shaken:
                camera.add_shake(4.5)
                ctrl_mgr.rumble_player(0, 0.4, 0.6, 120)
                ctrl_mgr.rumble_player(1, 0.4, 0.6, 120)
                play_sfx(SoundEvent.ROUND_START)
                round_start_shaken = True

        # Bloqueio de movimentação durante a cinemática de abertura e o início do round (Item 10 / Entregável 5.2)
        round_in_progress = (round_winner is None and round_start_timer <= 0 and round_intro_timer <= 0)
        if round_in_progress and not round_started:
            round_started = True
            for f in (p1, p2):
                if f and hasattr(f, "on_round_start"):
                    f.on_round_start()

        if not round_in_progress:
            p1_dwx, p1_dwy = 0.0, 0.0
            p2_dwx, p2_dwy = 0.0, 0.0

        for event in pygame.event.get():
            ctrl_mgr.handle_event(event)
            if touch_controls.handle_event(event, scaler):
                continue
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu.open(screen, arcade=arcade_run is not None, demo=is_demo())
                    break
                elif event.key == KEY_SETTINGS:
                    settings_menu.open()
                elif event.key == KEY_RESTART:
                    if round_winner is not None:
                        request_restart()
                elif event.key == KEY_TOGGLE_AI and arcade_run is None:
                    vs_ai_mode = not vs_ai_mode

                # Ao terminar um duelo, permitir que Quadrado / Ação Primária reinicie o duelo (mas nunca com duelo em andamento)
                if round_winner is not None:
                    if event.key in (KEY_RESTART, controls["P1_ATTACK"], controls["P2_ATTACK"]):
                        request_restart()

                # Entregável 5.1: registra o aperto do botão de ataque durante o Choque de Espadas (QTE "STRIKE!")
                if clash_system.is_frozen():
                    if event.key == controls["P1_ATTACK"]:
                        clash_system.register_press(0)
                    elif event.key == controls["P2_ATTACK"]:
                        clash_system.register_press(1)

                # Comandos Jogador 1 (Teclado)
                if p1.is_alive and round_winner is None and round_in_progress:
                    if event.key == controls["P1_ATTACK"]:
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_attack(p1, aim_x, aim_y, projectiles, particles)
                    elif event.key == controls.get("P1_SECONDARY", pygame.K_r):
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_secondary(p1, aim_x, aim_y, p1_dwx, p1_dwy, projectiles, particles, decoys, poison_clouds, powder_traps, opponent=p2, game_map=game_map, banners=banners)
                    elif event.key == controls.get("P1_DASH", pygame.K_t):
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_roll(p1, p1_dwx, p1_dwy, aim_x, aim_y, particles, decoys=decoys, game_map=game_map, opponent=p2, banners=banners)

                # Comandos Jogador 2 (Teclado)
                if not vs_ai_mode and p2.is_alive and round_winner is None and round_in_progress:
                    if event.key == controls["P2_ATTACK"]:
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_attack(p2, aim_x, aim_y, projectiles, particles)
                    elif event.key in (controls.get("P2_SECONDARY"), controls.get("P2_PARRY")):
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_secondary(p2, aim_x, aim_y, p2_dwx, p2_dwy, projectiles, particles, decoys, poison_clouds, powder_traps, opponent=p1, game_map=game_map, banners=banners)
                    elif event.key == controls.get("P2_DASH", pygame.K_o):
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_roll(p2, p2_dwx, p2_dwy, aim_x, aim_y, particles, decoys=decoys, game_map=game_map, opponent=p1, banners=banners)

            elif event.type == pygame.JOYBUTTONDOWN:
                if ctrl_mgr.is_event_menu_pause(event, 0) or ctrl_mgr.is_event_menu_pause(event, 1) or (getattr(event, "button", None) == 6):
                    pause_menu.open(screen, arcade=arcade_run is not None, demo=is_demo())
                    break
                elif round_winner is not None:
                    # Ao terminar o duelo, tanto restart quanto quadrado/ação primária reiniciam
                    if (ctrl_mgr.is_event_action(event, 0, "restart") or
                        ctrl_mgr.is_event_action(event, 0, "attack") or
                        ctrl_mgr.is_event_action(event, 1, "restart") or
                        ctrl_mgr.is_event_action(event, 1, "attack")):
                        request_restart()
                elif clash_system.is_frozen():
                    # Entregável 5.1: registra o botão de ataque/confirmação durante o Choque de Espadas (QTE "STRIKE!")
                    if ctrl_mgr.is_event_action(event, 0, "attack"):
                        clash_system.register_press(0)
                    if ctrl_mgr.is_event_action(event, 1, "attack"):
                        clash_system.register_press(1)
                elif p1.is_alive and round_winner is None and round_in_progress:
                    if ctrl_mgr.is_event_action(event, 0, "attack"):
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_attack(p1, aim_x, aim_y, projectiles, particles)
                    elif ctrl_mgr.is_event_action(event, 0, "secondary"):
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_secondary(p1, aim_x, aim_y, p1_dwx, p1_dwy, projectiles, particles, decoys, poison_clouds, powder_traps, opponent=p2, game_map=game_map, banners=banners)
                    elif ctrl_mgr.is_event_action(event, 0, "dash"):
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_roll(p1, p1_dwx, p1_dwy, aim_x, aim_y, particles, decoys=decoys, game_map=game_map, opponent=p2, banners=banners)

                # Gamepad Jogador 2
                if not vs_ai_mode and p2.is_alive and round_winner is None and round_in_progress:
                    if ctrl_mgr.is_event_menu_pause(event, 1) or (getattr(event, "button", None) == 6):
                        pause_menu.open(screen, arcade=arcade_run is not None, demo=is_demo())
                        break
                    elif ctrl_mgr.is_event_action(event, 1, "attack"):
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_attack(p2, aim_x, aim_y, projectiles, particles)
                    elif ctrl_mgr.is_event_action(event, 1, "secondary"):
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_secondary(p2, aim_x, aim_y, p2_dwx, p2_dwy, projectiles, particles, decoys, poison_clouds, powder_traps, opponent=p1, game_map=game_map, banners=banners)
                    elif ctrl_mgr.is_event_action(event, 1, "dash"):
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_roll(p2, p2_dwx, p2_dwy, aim_x, aim_y, particles, decoys=decoys, game_map=game_map, opponent=p1, banners=banners)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if round_winner is not None:
                    request_restart()
                else:
                    select_btn_rect = pygame.Rect(25, 20, 160, 32)
                    if arcade_run is None and select_btn_rect.collidepoint(mx, my):
                        play_sfx(SoundEvent.MENU_SELECT)
                        sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
                        game_state = STATE_ARENA_SELECT

        # Comandos de Ação Touchscreen
        if touch_controls.is_menu_requested():
            pause_menu.open(screen, arcade=arcade_run is not None, demo=is_demo())
        if touch_controls.is_select_requested() and arcade_run is None:
            play_sfx(SoundEvent.MENU_SELECT)
            sound_mgr.play_music(MusicTrack.CHAR_SELECT_THEME)
            game_state = STATE_ARENA_SELECT

        if pause_menu.is_open:
            continue

        if p1.is_alive and round_winner is None and round_in_progress:
            if touch_controls.is_attack_just_pressed():
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                execute_fighter_attack(p1, aim_x, aim_y, projectiles, particles)
            elif touch_controls.is_dash_just_pressed():
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                execute_fighter_roll(p1, p1_dwx, p1_dwy, aim_x, aim_y, particles, decoys=decoys, game_map=game_map)

        # Hitstop congelado
        if combat_system.hitstop_timer > 0:
            combat_system.hitstop_timer -= dt
            pygame.display.flip()
            continue

        game_time += dt

        # Suporte ao Hold and Release do Bombardeio de Canhão Celestial da Pirata Anne Bonny
        p1_sec_held = keys[controls.get("P1_SECONDARY", pygame.K_r)] or ctrl_mgr.is_action_down(0, "secondary")
        if isinstance(p1, PirateSwordswoman) and p1.is_alive and round_in_progress:
            if p1_sec_held:
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                p1.update_cannon_strike(dt, aim_x, aim_y)
            else:
                if p1.is_aiming_cannon:
                    p1.release_cannon_strike(projectiles, particles)

        p2_sec_key = controls.get("P2_SECONDARY", pygame.K_i)
        p2_sec_held = keys[p2_sec_key] or (controls.get("P2_PARRY") and keys[controls["P2_PARRY"]]) or ctrl_mgr.is_action_down(1, "secondary")
        if not vs_ai_mode and isinstance(p2, PirateSwordswoman) and p2.is_alive and round_in_progress:
            if p2_sec_held:
                aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                p2.update_cannon_strike(dt, aim_x, aim_y)
            else:
                if p2.is_aiming_cannon:
                    p2.release_cannon_strike(projectiles, particles)

        # Suporte ao Hold and Release da Chuva de Flechas Sagradas em Arco de Tomoe (KyudoArcher)
        if isinstance(p1, KyudoArcher) and p1.is_alive and round_in_progress:
            if p1_sec_held:
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                p1.update_sacred_volley(dt, aim_x, aim_y)
            else:
                if getattr(p1, "is_aiming_volley", False):
                    p1.release_sacred_volley(projectiles, particles)

        if not vs_ai_mode and isinstance(p2, KyudoArcher) and p2.is_alive and round_in_progress:
            if p2_sec_held:
                aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                p2.update_sacred_volley(dt, aim_x, aim_y)
            else:
                if getattr(p2, "is_aiming_volley", False):
                    p2.release_sacred_volley(projectiles, particles)

        # Suporte ao carregamento contínuo de pólvora do Rifleman (segurando ação secundária)
        if isinstance(p1, Rifleman) and p1.is_alive and round_in_progress:
            if p1_sec_held and not p1.has_ammo:
                p1.trigger_reload_hold()
            else:
                p1.is_reloading = False

        if not vs_ai_mode and isinstance(p2, Rifleman) and p2.is_alive and round_in_progress:
            if p2_sec_held and not p2.has_ammo:
                p2.trigger_reload_hold()
            else:
                p2.is_reloading = False

        # Suporte ao Hold and Release da Flecha de Corda de Tomoe (KyudoArcher) na Terceira Ação (Roll / Dash dedicado)
        p1_dash_held = keys[controls.get("P1_DASH", pygame.K_t)] or ctrl_mgr.is_action_down(0, "dash") or touch_controls.is_dash_held()
        if isinstance(p1, KyudoArcher) and p1.is_alive and round_in_progress:
            if p1_dash_held:
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                if not p1.is_charging_rope:
                    p1.start_rope_arrow_charge(aim_x, aim_y, game_map)
                else:
                    p1.update_rope_charge(dt, aim_x, aim_y, game_map)
            else:
                if p1.is_charging_rope:
                    p1.release_rope_arrow(projectiles, particles, game_map)

        p2_dash_key = controls.get("P2_DASH", pygame.K_o)
        p2_dash_held = keys[p2_dash_key] or ctrl_mgr.is_action_down(1, "dash")
        if not vs_ai_mode and isinstance(p2, KyudoArcher) and p2.is_alive and round_in_progress:
            if p2_dash_held:
                aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                if not p2.is_charging_rope:
                    p2.start_rope_arrow_charge(aim_x, aim_y, game_map)
                else:
                    p2.update_rope_charge(dt, aim_x, aim_y, game_map)
            else:
                if p2.is_charging_rope:
                    p2.release_rope_arrow(projectiles, particles, game_map)

        # Suporte ao Hold & Release do Escudo de Corrente de Murasaki (Item 24)
        if isinstance(p1, PurpleNinja) and p1.is_alive and round_in_progress:
            if p1_sec_held:
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                p1.update_chain_shield(dt, aim_x, aim_y)
            else:
                if getattr(p1, "is_holding_shield", False):
                    p1.release_chain_shield(projectiles, particles)

        if not vs_ai_mode and isinstance(p2, PurpleNinja) and p2.is_alive and round_in_progress:
            if p2_sec_held:
                aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                p2.update_chain_shield(dt, aim_x, aim_y)
            else:
                if getattr(p2, "is_holding_shield", False):
                    p2.release_chain_shield(projectiles, particles)

        # Cancelar carregamentos se a rodada terminou
        if round_winner is not None:
            for f in (p1, p2):
                if isinstance(f, KyudoArcher):
                    f.is_charging_rope = False
                    f.is_aiming_volley = False
                elif isinstance(f, PirateSwordswoman):
                    f.is_aiming_cannon = False
                elif isinstance(f, PurpleNinja):
                    f.is_holding_shield = False
                    f.is_spinning_chain = False

        # Suporte ao congelamento dramático de cinema samurai e ao Choque de Espadas (Entregável 5.1)
        is_cinematic_freeze = cinematic_director.is_frozen()
        is_clash_freeze = clash_system.is_frozen()

        if not is_cinematic_freeze and not is_clash_freeze:
            # Movimento Jogador 1
            if hasattr(p1, "apply_gatotsu_steering") and p1.state == "GATOTSU_CHARGE":
                p1.apply_gatotsu_steering(p1_dwx, p1_dwy, dt)
            else:
                p1.apply_movement(p1_dwx, p1_dwy, dt, game_map)

            # Movimento Jogador 2 (IA ou Humano)
            if isinstance(p2, BossOni):
                pass  # o chefe se move pelo próprio cérebro (BossOni.update)
            elif vs_ai_mode:
                if round_in_progress:
                    ai.update(p2, p1, dt, game_map, projectiles, powder_pouches, decoys)
            else:
                if hasattr(p2, "apply_gatotsu_steering") and p2.state == "GATOTSU_CHARGE":
                    p2.apply_gatotsu_steering(p2_dwx, p2_dwy, dt)
                else:
                    p2.apply_movement(p2_dwx, p2_dwy, dt, game_map)

        # Atualizações dos combatentes e coletáveis
        if not is_cinematic_freeze and not is_clash_freeze:
            # Atualização de perigos da Arena de Kyoto (Carruagens e Escombros)
            if game_map.has_updates:
                game_map.update(dt, [p1, p2], camera, particles, banners, cinematic_director)

            if game_map.dispel_requested:  # sino do santuário: dissipa a fumaça da Kasumi e o veneno da Okuni
                game_map.dispel_requested = False
                poison_clouds.clear()
                fog.dispel()
                for pr in projectiles:
                    if type(pr).__name__ in ("SmokeCloudEntity", "PoisonCloudProjectile"):
                        pr.is_active = False

            for pouch in powder_pouches:
                pouch.update(dt, game_map, particles)

            # Atualizar manequins teatrais Kawarimi de Okuni
            decoys[:] = [d for d in decoys if d.update(dt)]

            # Atualizar nuvens de veneno Dokukiri de Okuni
            poison_clouds = [pc for pc in poison_clouds if pc.update(dt, [p1, p2], particles, banners=banners, cinematic_director=cinematic_director)]

            # Atualizar armadilhas de pólvora negra de Teppo
            powder_traps = [pt for pt in powder_traps if pt.update(dt, [p1, p2], particles, banners=banners, cinematic_director=cinematic_director)]

            # Atualizar Barreira dos Ventos Kami de Tomoe
            for archer, opp in ((p1, p2), (p2, p1)):
                if isinstance(archer, KyudoArcher):
                    archer.update_ofuda_barrier_effects(dt, projectiles, opponent=opp, particles=particles)

            f_dt = dt if round_in_progress else 0.0

            for f in (p1, p2):
                opp = p2 if f is p1 else p1
                if f.state == STATE_FALL:
                    f.update_pit(f_dt, game_map, particles, banners)
                    continue
                if isinstance(f, BossOni):
                    if round_in_progress:
                        f.update(dt, game_map, opp, particles, banners, projectiles, camera)
                    else:
                        f.update(0.0)
                    continue
                if isinstance(f, Rifleman):
                    if round_in_progress:
                        f.check_powder_pickup(powder_pouches, particles)
                if isinstance(f, PirateSwordswoman):
                    f.update(f_dt, game_map, particles, opponent=opp, banners=banners)
                elif isinstance(f, SaitouSamurai):
                    f.update(f_dt, game_map, particles)
                elif isinstance(f, (Rifleman, Kabuki, Musketeer, GrayNinja)):
                    f.update(f_dt, game_map, particles)
                elif isinstance(f, BlueSamurai):
                    f.update(f_dt, game_map, particles, projectiles)
                elif isinstance(f, KyudoArcher):
                    f.update(f_dt, game_map, particles, projectiles)
                elif isinstance(f, (RenMonk, ChiyoKunoichi)):
                    f.update(f_dt, game_map, particles, opponent=opp)
                else:
                    f.update(f_dt, game_map)

                # Decremento universal de cooldown de impacto com obstáculos sólidos
                if round_in_progress and getattr(f, "obstacle_spark_timer", 0) > 0:
                    f.obstacle_spark_timer -= dt

                # Item 17: Indicador visual e decremento de lentidão (fuligem de pólvora escorrendo aos pés)
                if round_in_progress and f.is_alive and getattr(f, "slow_timer", 0) > 0:
                    f.slow_timer -= dt
                    if random.random() < 0.40:
                        particles.append(SmokeParticle(
                            f.wx + random.uniform(-0.16, 0.16),
                            f.wy + random.uniform(-0.16, 0.16),
                            wz=random.uniform(0.04, 0.20),
                            color=(50, 45, 45),
                            radius=random.uniform(0.12, 0.20),
                            lifetime=random.uniform(0.35, 0.60)
                        ))

                # Queda em buracos da arena: toca o som e treme a câmera no frame em que começa
                if round_in_progress and f.update_pit(dt, game_map, particles, banners):
                    play_sfx(SoundEvent.FALL)
                    camera.add_shake(3.0)

            for f in (p1, p2):
                if round_in_progress:
                    terrain_fx.step(f, game_map, dt)
                    if hasattr(f, "drain_fog_nodes"):
                        for node in f.drain_fog_nodes():
                            fog.add_trail(*node)

        # Eventos do chefe: nova fase, checkpoint do Arcade e golpes
        if isinstance(p2, BossOni):
            for ev in p2.pop_events():
                if ev.startswith("phase_"):
                    phase_no = int(ev[6:])
                    if arcade_run is not None:
                        arcade_run.boss_phase = max(arcade_run.boss_phase, phase_no)
                    camera.add_shake(18.0)
                    play_sfx(SoundEvent.BOMB_EXPLODE)
                    banners.append(FloatingBanner(t("boss_phase_label", n=phase_no + 1, title=p2.phase_title), p2.wx, p2.wy,
                                                  wz=4.2, color=(255, 190, 120), duration=2.4))
                elif ev == "hit":
                    play_sfx(SoundEvent.SWORD_SLASH)
                elif ev in ("env_fireball", "env_spikes"):
                    play_sfx(SoundEvent.BOMB_EXPLODE if ev == "env_fireball" else SoundEvent.OBSTACLE_HIT)
                elif ev == "env_lava":
                    play_sfx(SoundEvent.CANNON_FIRE)
                elif ev == "player_hit":
                    ctrl_mgr.rumble_player(0, 0.7, 1.0, 220)

        # Atualizar Diretor Cinematográfico (Temporizadores e Corpos Voxel)
        cinematic_director.update(dt, game_map, particles)

        # Atualizar Choque de Espadas Tsubazeriai (Entregável 5.1: QTE "STRIKE!")
        clash_system.ai_player = 1 if vs_ai_mode else None
        clash_system.ai_reaction_fn = ai.get_clash_reaction
        clash_system.key_hints = (pygame.key.name(controls["P1_ATTACK"]).upper(), "" if vs_ai_mode else pygame.key.name(controls["P2_ATTACK"]).upper())
        clash_system.update(dt, camera=camera, particles=particles, banners=banners, ctrl_mgr=ctrl_mgr, game_map=game_map)

        # Processar Combate & Projéteis
        winner = combat_system.process_combat(p1, p2, game_map, particles, banners, camera, projectiles, dt, cinematic_director=cinematic_director, decoys=decoys, ctrl_mgr=ctrl_mgr, clash_system=clash_system)
        if winner and round_winner is None:
            round_winner = winner
            ctrl_mgr.rumble_player(0, 0.7, 1.0, 260)
            ctrl_mgr.rumble_player(1, 0.7, 1.0, 260)
            play_sfx(SoundEvent.ROUND_WIN)
            if winner == "P1_WINS":
                score_p1 += 1
            elif winner == "P2_WINS":
                score_p2 += 1

        # Verificação universal de vencedor de rodada (caso qualquer combatente tenha morrido por qualquer razão)
        if round_winner is None:
            if not p1.is_alive and p2.is_alive:
                round_winner = "P2_WINS"
                score_p2 += 1
                ctrl_mgr.rumble_player(0, 0.7, 1.0, 260)
                ctrl_mgr.rumble_player(1, 0.7, 1.0, 260)
                play_sfx(SoundEvent.ROUND_WIN)
            elif not p2.is_alive and p1.is_alive:
                round_winner = "P1_WINS"
                score_p1 += 1
                ctrl_mgr.rumble_player(0, 0.7, 1.0, 260)
                ctrl_mgr.rumble_player(1, 0.7, 1.0, 260)
                play_sfx(SoundEvent.ROUND_WIN)
            elif not p1.is_alive and not p2.is_alive:
                round_winner = "DRAW"
                play_sfx(SoundEvent.ROUND_WIN)

        if round_winner is not None:
            sound_mgr.play_death_music(fadeout_ms=350)

        # Arcade (8.1): informa o round à jornada uma única vez; as regras decidem se a luta, o oponente ou o round continua
        if arcade_run is not None and round_winner is not None and not arcade_round_reported:
            arcade_round_reported = True
            arcade_round_status = arcade_run.on_round_end(
                {"P1_WINS": "P1", "P2_WINS": "P2"}.get(round_winner, "DRAW"), round_clock, flawless=p1.hp >= p1.max_hp)
            arcade_fight_over = {FIGHT_WON: "won", FIGHT_LOST: "lost"}.get(arcade_round_status)

        # Entregável 5.3: Contador Best of 3 (BO3) — verifica se a partida terminou
        if round_winner in ("P1_WINS", "P2_WINS"):
            loser = p2 if round_winner == "P1_WINS" else p1
            victor = p1 if round_winner == "P1_WINS" else p2
            if arcade_run is not None:
                ends_match = arcade_fight_over == "won"
            else:
                ends_match = check_match_winner(score_p1, score_p2) is not None
            outcome_seq.arm((loser.wx, loser.wy), winner_idx=0 if victor is p1 else 1,
                            winner_pos=(victor.wx, victor.wy), match_end=ends_match)
        if outcome_seq.pending and not cinematic_director.is_frozen():
            outcome_seq.begin()

        if arcade_run is None and round_winner is not None and match_winner is None:
            mw = check_match_winner(score_p1, score_p2)
            if mw is not None:
                match_winner = mw
                winner_fighter = p1 if mw == "P1" else p2
                outcome_seq.deferred_result = (winner_fighter.name.upper(), get_fighter_color(winner_fighter), score_p1, score_p2)

        # A tela de resultados só aparece depois do replay de nocaute e da pose de vitória
        if outcome_seq.deferred_result and not outcome_seq.active and not outcome_seq.pending:
            round_result_screen.show(*outcome_seq.deferred_result)
            outcome_seq.deferred_result = None

        round_result_screen.update(dt)

        # Câmera segue o ponto médio (contra o chefe, 35% jogador / 65% chefe)
        boss_fight = isinstance(p2, BossOni)
        w_boss = 0.65 if boss_fight else 0.5
        mid_x = p1.wx * (1.0 - w_boss) + p2.wx * w_boss
        mid_y = p1.wy * (1.0 - w_boss) + p2.wy * w_boss
        # Atalhos de desenvolvimento do azimute (Entregável 6.1): [ e ] giram a câmera, \ restaura a vista clássica
        if keys[pygame.K_LEFTBRACKET]:
            camera.rotate(-CAMERA_ORBIT_SPEED * dt)
        if keys[pygame.K_RIGHTBRACKET]:
            camera.rotate(CAMERA_ORBIT_SPEED * dt)
        if keys[pygame.K_BACKSLASH]:
            camera.set_azimuth(0.0)
        camera_was_replaying = outcome_seq.active
        victory_f = None
        if round_winner in ("P1_WINS", "P2_WINS"):
            victory_f = p1 if round_winner == "P1_WINS" else p2
        outcome_seq.update(real_dt, (mid_x, mid_y),
                           winner_pos=(victory_f.wx, victory_f.wy) if victory_f else None,
                           winner_alive=victory_f.is_alive if victory_f else True)
        victory_p = outcome_seq.victory_progress()
        if victory_f is not None and victory_p is not None:
            # Entregável 7.4: pose de vitória do vencedor (sem efeito de combate)
            if victory_f.state != STATE_VICTORY:
                victory_f.set_facing(victory_f.wx + 1.0, victory_f.wy + 1.0)
                cine_beats["victory"] = BeatPlayer((p1_char_id, p2_char_id)[0 if victory_f is p1 else 1], "victory")
            victory_f.state = STATE_VICTORY
            victory_f.state_timer = victory_p
            victory_f.hitbox_active = False
            for beat in cine_beats["victory"].advance(victory_p):
                run_cine_beat(beat, victory_f)
        if outcome_seq.active:
            outcome_seq.apply_camera(camera, real_dt)
        else:
            camera.update(mid_x, mid_y, dt)
            if boss_fight and round_intro_timer <= 0:
                camera.zoom = 0.85  # o chefe tem até ~5 unidades de altura
            if camera_was_replaying:
                OutcomeSequence.restore_classic(camera)

        particles = [p for p in particles if p.update(dt)]
        # Entregável 1.4: Particle Cap Global (limite de 150 para prevenir sobrecarga de memória)
        if len(particles) > 150:
            cosmetic_idx = [i for i, p in enumerate(particles) if not isinstance(p, (BloodParticle, FloatingBanner))]
            excess = len(particles) - 150
            if excess > 0:
                to_remove = set(cosmetic_idx[:excess])
                particles = [p for i, p in enumerate(particles) if i not in to_remove]

        banners = [b for b in banners if b.update(dt)]
        for leaf in ambient_leaves:
            leaf.update(dt, game_map.wind_at(leaf.wx, leaf.wy, game_time))
        terrain_fx.update(dt, game_map, game_time)
        fog.update(dt, game_time)

        # -------------------------------------------------------------
        # RENDERIZAÇÃO COM Y-SORTING DIVIDIDO (ESTÁTICO VS DINÂMICO)
        # -------------------------------------------------------------
        bg_col = game_map.bg_color
        screen.fill(bg_col)
        game_map.render_terrain(screen, camera, game_time)

        # Entregável 1.3: Reutiliza a fila estática pré-calculada do cenário
        if not static_render_queue:
            static_render_queue = build_static_render_queue(game_map)
        if abs(camera.azimuth) > 1e-6:
            render_queue = [(camera.depth(*static_item_center(t_, o_)), t_, o_) for _, t_, o_ in static_render_queue]
        else:
            render_queue = list(static_render_queue)

        # Adicionar elementos dinâmicos exclusivos (Carruagens, Escombros de Kyoto)
        if hasattr(game_map, 'carriages'):
            for c in game_map.carriages:
                if c.is_active and c.warning_timer <= 0:
                    render_queue.append((camera.depth(c.wx, c.wy), 'carriage', c))
        if hasattr(game_map, 'falling_debris'):
            for d in game_map.falling_debris:
                if d.is_active:
                    render_queue.append((camera.depth(d.target_x, d.target_y), 'debris', d))


        render_queue.append((camera.depth(p1.wx, p1.wy), 'fighter', p1))
        render_queue.append((camera.depth(p2.wx, p2.wy), 'fighter', p2))
        if isinstance(p2, BossOni):
            for hazard in p2.hazards:
                render_queue.append((-1e9, 'boss_ground', hazard))
                if hazard.kind == "fireball":
                    render_queue.append((camera.depth(hazard.x, hazard.y) + 40.0, 'boss_air', hazard.air_view))

        # Adicionar cão Doberman ao Y-sorting se houver American Ninja na partida
        if hasattr(p1, "dog") and p1.dog:
            render_queue.append((camera.depth(p1.dog.wx, p1.dog.wy), 'dog', p1.dog))
        if hasattr(p2, "dog") and p2.dog:
            render_queue.append((camera.depth(p2.dog.wx, p2.dog.wy), 'dog', p2.dog))

        # Adicionar corpos voxel fatiados ao Y-sorting
        for corpse in cinematic_director.corpses:
            render_queue.append((camera.depth(corpse.wx, corpse.wy), 'corpse', corpse))

        for pouch in powder_pouches:
            if pouch.is_active:
                render_queue.append((camera.depth(pouch.wx, pouch.wy), 'pouch', pouch))

        for decoy in decoys:
            if decoy.is_active:
                render_queue.append((camera.depth(decoy.wx, decoy.wy), 'decoy', decoy))

        for pt in powder_traps:
            if pt.is_active:
                render_queue.append((camera.depth(pt.wx, pt.wy), 'powder_trap', pt))

        for pc in poison_clouds:
            if pc.is_active:
                render_queue.append((camera.depth(pc.wx, pc.wy), 'poison_cloud', pc))

        for proj in projectiles:
            render_queue.append((camera.depth(proj.wx, proj.wy), 'projectile', proj))

        for p in particles:
            if hasattr(p, 'wx') and hasattr(p, 'wy'):
                render_queue.append((camera.depth(p.wx, p.wy), 'particle', p))
        for p in terrain_fx.particles:
            render_queue.append((camera.depth(p.wx, p.wy), 'particle', p))
        render_queue.extend(fog.queue_items(camera))

        draw_world_queue(render_queue)
        draw_world_ambience()

        for banner in banners:
            banner.render(screen, camera, font_mid)

        # Entregável 5.1: Choque de Espadas Tsubazeriai (QTE "STRIKE!")
        clash_system.render(screen, camera)

        # Aplicar filtro Kurosawa Noir (Flash preto e branco de cinema samurai com sangue vívido)
        cinematic_director.apply_cinematic_filter(screen)

        # Marcadores piscantes [ P1 ] e [ P2 ] no início de cada round
        if round_start_timer > 0:
            if (int(round_start_timer * 6.5)) % 2 == 0:
                for fighter, label, col in ((p1, "P1", (255, 85, 85)), (p2, "P2", (95, 170, 255))):
                    if fighter and fighter.is_alive:
                        sx, sy = camera.apply(fighter.wx, fighter.wy, 1.80)
                        txt = font_mid.render(f"[ {label} ]", True, col)
                        bg_w = txt.get_width() + 14
                        bg_h = 24
                        bg_rect = pygame.Rect(sx - bg_w // 2, sy - 34, bg_w, bg_h)
                        pygame.draw.rect(screen, (18, 22, 24), bg_rect, border_radius=6)
                        pygame.draw.rect(screen, col, bg_rect, 2, border_radius=6)
                        screen.blit(txt, (bg_rect.centerx - txt.get_width() // 2, bg_rect.centery - txt.get_height() // 2))
                        # Pequena seta indicadora apontando para a cabeça
                        pygame.draw.polygon(screen, col, [(sx, sy - 8), (sx - 6, sy - 16), (sx + 6, sy - 16)])

        # Contador Regressivo de Veneno (Dokukiri) com alarme visual e barra decrescente
        for fighter in (p1, p2):
            if fighter and fighter.is_alive and getattr(fighter, "is_poisoned", False):
                p_time = max(0.0, getattr(fighter, "poison_timer", 0.0))
                psx, psy = camera.apply(fighter.wx, fighter.wy, 1.95)

                card_w = 84
                card_h = 28
                card_rect = pygame.Rect(psx - card_w // 2, psy - 42, card_w, card_h)

                # Alerta visual pulsante (pisca vermelho rápido quando < 2.0s)
                pulse_rate = 14.0 if p_time < 2.0 else 5.0
                is_crit = (p_time < 2.0 and int(game_time * pulse_rate) % 2 == 0)
                card_border_col = (255, 60, 60) if is_crit else (60, 240, 110)
                text_col = (255, 90, 90) if is_crit else (100, 255, 140)

                pygame.draw.rect(screen, (16, 22, 18), card_rect, border_radius=6)
                pygame.draw.rect(screen, card_border_col, card_rect, 2, border_radius=6)

                try:
                    p_txt = font_small.render(f"☠ {p_time:.1f}s", True, text_col)
                except Exception:
                    p_txt = font_small.render(f"POISON {p_time:.1f}s", True, text_col)
                screen.blit(p_txt, (card_rect.centerx - p_txt.get_width() // 2, card_rect.y + 4))

                # Barra horizontal proporcional aos 6.0s totais
                bar_pct = max(0.0, min(1.0, p_time / 6.0))
                bar_w = int((card_w - 8) * bar_pct)
                bar_rect = pygame.Rect(card_rect.x + 4, card_rect.bottom - 6, bar_w, 3)
                pygame.draw.rect(screen, card_border_col, bar_rect, border_radius=2)

                # Pequena gota/seta indicadora sobre a cabeça
                pygame.draw.polygon(screen, card_border_col, [(psx, psy - 10), (psx - 5, psy - 18), (psx + 5, psy - 18)])

                if random.random() < 0.28:
                    particles.append(SparkParticle(fighter.wx, fighter.wy, 0.45, color=(80, 235, 110)))

        # Barra de Cooldown flutuante sobre a cabeça dos combatentes na arena (Item 6)
        if round_winner is None:
            for fighter in (p1, p2):
                if fighter and fighter.is_alive:
                    cd_data = get_fighter_cooldown_data(fighter)
                    if cd_data and (cd_data.get("timer", 0.0) > 0.0 or cd_data.get("warning")):
                        fsx, fsy = camera.apply(fighter.wx, fighter.wy, 1.82)
                        bar_w = 46
                        bar_h = 5
                        bx = fsx - bar_w // 2
                        by = fsy - 28

                        # Sombra / Fundo
                        pygame.draw.rect(screen, (14, 18, 16, 210), (bx - 1, by - 1, bar_w + 2, bar_h + 2), border_radius=2)

                        if cd_data.get("warning"):
                            if int(game_time * 8.0) % 2 == 0:
                                pygame.draw.rect(screen, cd_data.get("color", (240, 60, 60)), (bx, by, bar_w, bar_h), border_radius=2)
                            lbl_surf = font_small.render(cd_data["name"], True, (255, 190, 190))
                            screen.blit(lbl_surf, (fsx - lbl_surf.get_width() // 2, by - 13))
                        else:
                            timer = cd_data.get("timer", 0.0)
                            max_cd = max(0.01, cd_data.get("max_cd", 1.0))
                            pct = max(0.0, min(1.0, 1.0 - timer / max_cd))
                            fill_w = int(bar_w * pct)

                            pygame.draw.rect(screen, (36, 44, 40), (bx, by, bar_w, bar_h), border_radius=1)
                            if fill_w > 0:
                                pygame.draw.rect(screen, cd_data.get("color", (100, 200, 255)), (bx, by, fill_w, bar_h), border_radius=1)
                            pygame.draw.rect(screen, (170, 180, 175), (bx - 1, by - 1, bar_w + 2, bar_h + 2), 1, border_radius=2)

                            lbl_surf = font_small.render(f"{timer:.1f}s", True, (230, 240, 235))
                            screen.blit(lbl_surf, (fsx - lbl_surf.get_width() // 2, by - 14))

        # -------------------------------------------------------------
        # INTERFACE DE USUÁRIO (HUD)
        # -------------------------------------------------------------
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 270, 10, 540, 66)
        pygame.draw.rect(screen, (20, 24, 22, 220), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 75, 68), panel_rect, 2, border_radius=8)

        p1_color = get_fighter_color(p1)
        p2_color = get_fighter_color(p2)

        p1_name = p1.name.split()[0].upper()
        p2_name = p2.name.split()[0].upper()
        if getattr(p2, "mirror_alt", False):
            p2_name = t("arcade_mirror_tag")

        # Desafios: após vencer a luta, a jornada já avançou; o HUD continua mostrando a luta que acabou
        hud_fight = None
        if arcade_run is not None:
            hud_idx = arcade_run.index - 1 if arcade_fight_over == "won" else arcade_run.index
            hud_fight = arcade_run.ladder[hud_idx] if 0 <= hud_idx < len(arcade_run.ladder) else None
        challenge_total = len(hud_fight.opponents) * hud_fight.rounds_to_win if hud_fight is not None and hud_fight.is_challenge else 0
        if not challenge_total:
            p1_round_score = score_p1
        elif arcade_fight_over == "won":
            p1_round_score = challenge_total
        else:
            p1_round_score = arcade_run.challenge_rounds_won
        p1_title = font_mid.render(f"{p1_name}  {p1_round_score}", True, p1_color)
        p2_title = font_mid.render(f"{score_p2}  {p2_name}", True, p2_color)
        screen.blit(p1_title, (panel_rect.x + 20, panel_rect.y + 10))
        screen.blit(p2_title, (panel_rect.right - p2_title.get_width() - 20, panel_rect.y + 10))

        # Entregável 5.3: Marcadores (pips) de rounds vencidos — Melhor-de-3 (BO3)
        if isinstance(p2, BossOni):
            render_boss_bar(screen, p2, panel_rect)
            render_damage_bars(screen, p1, p2, p1_color, p2_color, panel_rect)
        else:
            render_round_pips(screen, p1_round_score, score_p2, p1_color, p2_color, panel_rect=panel_rect, p1_total=challenge_total or None)
            render_damage_bars(screen, p1, p2, p1_color, p2_color, panel_rect)

        mode_text = t("mode_hud_1p") if vs_ai_mode else t("mode_hud_2p")
        if arcade_run is not None:
            fight_no = arcade_run.index if arcade_fight_over == "won" else arcade_run.index + 1
            mode_text = t("arcade_fight_n_of_m", n=fight_no, m=len(arcade_run.ladder))
            if challenge_total:
                opp_no = len(hud_fight.opponents) if arcade_fight_over == "won" else arcade_run.opponent_index + 1
                mode_text += f"  |  {t('arcade_opponent_n_of_m', n=opp_no, m=len(hud_fight.opponents))}"
        mode_surf = font_small.render(mode_text, True, COLOR_GOLD)
        screen.blit(mode_surf, (panel_rect.centerx - mode_surf.get_width() // 2, panel_rect.y + 12))

        # Badges de Veneno no HUD (posicionadas ao lado dos nomes)
        if getattr(p1, "is_poisoned", False) and p1.is_alive:
            p1_p_time = max(0.0, getattr(p1, "poison_timer", 0.0))
            try:
                p1_badge = font_small.render(f"☠ FRENZY {p1_p_time:.1f}s", True, (80, 245, 120))
            except Exception:
                p1_badge = font_small.render(f"POISON {p1_p_time:.1f}s", True, (80, 245, 120))
            screen.blit(p1_badge, (panel_rect.x + p1_title.get_width() + 28, panel_rect.y + 12))

        if getattr(p2, "is_poisoned", False) and p2.is_alive:
            p2_p_time = max(0.0, getattr(p2, "poison_timer", 0.0))
            try:
                p2_badge = font_small.render(f"☠ FRENZY {p2_p_time:.1f}s", True, (80, 245, 120))
            except Exception:
                p2_badge = font_small.render(f"POISON {p2_p_time:.1f}s", True, (80, 245, 120))
            screen.blit(p2_badge, (panel_rect.right - p2_title.get_width() - p2_badge.get_width() - 28, panel_rect.y + 12))

        # Barras Sincronizadas de Cooldown no HUD (Item 6)
        cd1 = get_fighter_cooldown_data(p1)
        if cd1 and p1.is_alive:
            bar_w = 150
            bar_h = 7
            bar_x1 = panel_rect.x + 20
            bar_y1 = panel_rect.y + 48

            if cd1.get("warning"):
                t_col = (255, 90, 90) if (int(game_time * 8.0) % 2 == 0) else (255, 180, 180)
                txt1 = font_small.render(f"⚠ {cd1['name']}", True, t_col)
                screen.blit(txt1, (bar_x1, panel_rect.y + 32))
                pygame.draw.rect(screen, (40, 20, 20), (bar_x1, bar_y1, bar_w, bar_h), border_radius=2)
                pygame.draw.rect(screen, (240, 70, 70), (bar_x1, bar_y1, bar_w, bar_h), 1, border_radius=2)
            else:
                t1 = cd1["timer"]
                m1 = max(0.01, cd1["max_cd"])
                pct1 = max(0.0, min(1.0, 1.0 - t1 / m1))
                fill_w1 = int(bar_w * pct1)

                if t1 > 0:
                    status_str = f"{cd1['name']}  {t1:.1f}s"
                    status_col = (215, 220, 220)
                else:
                    status_str = f"{cd1['name']}  READY"
                    status_col = (130, 250, 170)

                txt1 = font_small.render(status_str, True, status_col)
                screen.blit(txt1, (bar_x1, panel_rect.y + 32))

                pygame.draw.rect(screen, (34, 40, 36), (bar_x1, bar_y1, bar_w, bar_h), border_radius=2)
                if fill_w1 > 0:
                    fill_col1 = cd1["color"] if t1 > 0 else (60, 205, 120)
                    pygame.draw.rect(screen, fill_col1, (bar_x1, bar_y1, fill_w1, bar_h), border_radius=2)
                pygame.draw.rect(screen, (75, 90, 82), (bar_x1, bar_y1, bar_w, bar_h), 1, border_radius=2)

        cd2 = get_fighter_cooldown_data(p2)
        if cd2 and p2.is_alive:
            bar_w = 150
            bar_h = 7
            bar_x2 = panel_rect.right - 20 - bar_w
            bar_y2 = panel_rect.y + 48

            if cd2.get("warning"):
                t_col = (255, 90, 90) if (int(game_time * 8.0) % 2 == 0) else (255, 180, 180)
                txt2 = font_small.render(f"⚠ {cd2['name']}", True, t_col)
                screen.blit(txt2, (panel_rect.right - 20 - txt2.get_width(), panel_rect.y + 32))
                pygame.draw.rect(screen, (40, 20, 20), (bar_x2, bar_y2, bar_w, bar_h), border_radius=2)
                pygame.draw.rect(screen, (240, 70, 70), (bar_x2, bar_y2, bar_w, bar_h), 1, border_radius=2)
            else:
                t2 = cd2["timer"]
                m2 = max(0.01, cd2["max_cd"])
                pct2 = max(0.0, min(1.0, 1.0 - t2 / m2))
                fill_w2 = int(bar_w * pct2)

                if t2 > 0:
                    status_str = f"{t2:.1f}s  {cd2['name']}"
                    status_col = (215, 220, 220)
                else:
                    status_str = f"READY  {cd2['name']}"
                    status_col = (130, 250, 170)

                txt2 = font_small.render(status_str, True, status_col)
                screen.blit(txt2, (panel_rect.right - 20 - txt2.get_width(), panel_rect.y + 32))

                pygame.draw.rect(screen, (34, 40, 36), (bar_x2, bar_y2, bar_w, bar_h), border_radius=2)
                if fill_w2 > 0:
                    fill_col2 = cd2["color"] if t2 > 0 else (60, 205, 120)
                    pygame.draw.rect(screen, fill_col2, (bar_x2 + bar_w - fill_w2, bar_y2, fill_w2, bar_h), border_radius=2)
                pygame.draw.rect(screen, (75, 90, 82), (bar_x2, bar_y2, bar_w, bar_h), 1, border_radius=2)

        # Indicador Tático de Pólvora para o Teppo (quando desmuniciado)
        for fighter in (p1, p2):
            if isinstance(fighter, Rifleman) and fighter.is_alive and round_winner is None:
                active_pouches = [p for p in powder_pouches if getattr(p, "is_active", False)]
                if not fighter.has_ammo and active_pouches:
                    nearest_pouch = min(active_pouches, key=lambda p: math.hypot(p.wx - fighter.wx, p.wy - fighter.wy))
                    dist = math.hypot(nearest_pouch.wx - fighter.wx, nearest_pouch.wy - fighter.wy)
                    fsx, fsy = camera.apply(fighter.wx, fighter.wy, 1.4)
                    psx, psy = camera.apply(nearest_pouch.wx, nearest_pouch.wy, 0.4)
                    sdx = psx - fsx
                    sdy = psy - fsy
                    s_dist = math.hypot(sdx, sdy)
                    if s_dist > 0.001:
                        nx = sdx / s_dist
                        ny = sdy / s_dist
                        ptr_dist = 42
                        ptr_x = fsx + nx * ptr_dist
                        ptr_y = fsy + ny * ptr_dist
                        perp_x = -ny * 7
                        perp_y = nx * 7
                        p_tip = (ptr_x + nx * 8, ptr_y + ny * 8)
                        p_left = (ptr_x - nx * 6 + perp_x, ptr_y - ny * 6 + perp_y)
                        p_right = (ptr_x - nx * 6 - perp_x, ptr_y - ny * 6 - perp_y)
                        pygame.draw.polygon(screen, (15, 18, 16), [p_tip, p_left, p_right])
                        pygame.draw.polygon(screen, (255, 215, 40), [p_tip, p_left, p_right])
                        pygame.draw.polygon(screen, (160, 110, 20), [p_tip, p_left, p_right], 1)
                        dist_lbl = font_small.render(t("powder_tracker", dist=dist), True, (255, 240, 160))
                        d_bg = pygame.Rect(ptr_x - dist_lbl.get_width() // 2 - 4, ptr_y - 24, dist_lbl.get_width() + 8, 16)
                        pygame.draw.rect(screen, (18, 24, 21), d_bg, border_radius=4)
                        pygame.draw.rect(screen, (255, 210, 50), d_bg, 1, border_radius=4)
                        screen.blit(dist_lbl, (d_bg.x + 4, d_bg.y + 1))


        # Botão Trocar Personagens no topo esquerdo (não existe no Arcade)
        if arcade_run is None:
            select_btn = pygame.Rect(25, 20, 180, 32)
            pygame.draw.rect(screen, (26, 34, 30, 210), select_btn, border_radius=6)
            pygame.draw.rect(screen, COLOR_GOLD, select_btn, 1, border_radius=6)
            sel_txt = font_small.render(t("change_warriors"), True, COLOR_GOLD)
            screen.blit(sel_txt, (select_btn.centerx - sel_txt.get_width() // 2, select_btn.y + 7))

        # Renderizar Controles Virtuais Touchscreen (se ativos/visíveis)
        p1_a1, p1_a2 = get_fighter_action_labels(p1)
        touch_controls.set_action_labels(p1_a1, p1_a2)
        touch_controls.render(screen, font_mid, font_small)

        # Banner Central de Início de Round (Item 10)
        if round_start_timer > -0.45 and round_winner is None:
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2 - 40
            card_w = 260
            card_h = 92

            if round_start_timer > 0.0:
                banner_alpha = 240
            else:
                banner_alpha = int(240 * max(0.0, (round_start_timer + 0.45) / 0.45))

            if banner_alpha > 5:
                banner_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(banner_surf, (16, 22, 19, banner_alpha), (0, 0, card_w, card_h), border_radius=10)

                if round_start_timer > 0.6:
                    # 準備 (Junbi / READY...)
                    border_col = (200, 170, 80, banner_alpha)
                    pygame.draw.rect(banner_surf, border_col, (0, 0, card_w, card_h), 2, border_radius=10)

                    font_kanji = get_text_font(46)
                    k_surf = font_kanji.render("準備", True, (250, 240, 205))
                    k_surf.set_alpha(banner_alpha)
                    banner_surf.blit(k_surf, (card_w // 2 - k_surf.get_width() // 2, 8))

                    font_sub = get_title_font(18)
                    sub_surf = font_sub.render("READY...", True, (215, 200, 160))
                    sub_surf.set_alpha(banner_alpha)
                    banner_surf.blit(sub_surf, (card_w // 2 - sub_surf.get_width() // 2, 60))
                else:
                    # 始め! (Hajime! / START!)
                    border_col = (245, 70, 60, banner_alpha)
                    pygame.draw.rect(banner_surf, border_col, (0, 0, card_w, card_h), 3, border_radius=10)

                    font_kanji = get_text_font(48)
                    k_surf = font_kanji.render("始め!", True, (255, 85, 75))
                    k_surf.set_alpha(banner_alpha)
                    banner_surf.blit(k_surf, (card_w // 2 - k_surf.get_width() // 2, 6))

                    font_sub = get_title_font(20)
                    sub_surf = font_sub.render("START!", True, (255, 220, 90))
                    sub_surf.set_alpha(banner_alpha)
                    banner_surf.blit(sub_surf, (card_w // 2 - sub_surf.get_width() // 2, 60))

                screen.blit(banner_surf, (center_x - card_w // 2, center_y - card_h // 2))

        # Banner de Vitória (oculto quando a partida Melhor-de-3 já foi decidida — ver tela de resultados abaixo)
        if round_winner and match_winner is None and not (outcome_seq.active or outcome_seq.pending):
            if round_winner == "DRAW":
                w_msg = t("draw_text")
                w_color = COLOR_GOLD
            else:
                w_fighter = p1 if round_winner == "P1_WINS" else p2
                w_msg = t("victory_text", name=w_fighter.name.upper())
                w_color = get_fighter_color(w_fighter)
            v_surf = font_large.render(w_msg, True, w_color)
            hint_msg = t("next_round_hint")
            if arcade_run is not None:
                hint_key = {"won": "arcade_next_fight", "lost": "arcade_continue_hint"}.get(arcade_fight_over, "rematch_prompt")
                hint_msg = t(hint_key)

            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2 - 40
            screen.blit(v_surf, (center_x - v_surf.get_width() // 2, center_y))
            render_text_with_icons(screen, font_mid, hint_msg, center_x, center_y + 48, COLOR_WHITE, icon_size=20)

        # Entregável 7.4: letterbox e banner do vencedor durante a pose de vitória
        if outcome_seq.phase == "victory" and victory_f is not None:
            outcome_seq.render_overlay(screen, victory_f.name, get_fighter_color(victory_f),
                                       (p1_char_id, p2_char_id)[0 if victory_f is p1 else 1])

        # Entregável 5.2: pergaminho vertical Sumi-E na abertura do round (a rotação é feita no azimute da câmera)
        if round_intro_timer > 0:
            round_intro.render(screen, round_intro_timer)

        # Entregável 5.3: Tela final de partida Melhor-de-3 (com revanche rápida via Espaço)
        if match_winner is not None:
            round_result_screen.render(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
