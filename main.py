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
    COLOR_GRAY_NINJA, COLOR_PURPLE_NINJA, COLOR_SAITOU_AURA,
    COLOR_RIFLE_AURA, COLOR_KABUKI_AURA, COLOR_ARCHER_AURA,
    COLOR_PIRATE_AURA, COLOR_MUSKETEER_AURA,
    ARENA_BAMBOO, ARENA_KYOTO, ARENA_RANDOM, COLOR_KYOTO_BG
)
from src.isometric.iso_math import input_to_world_direction
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.world.kyoto_map import KyotoMap
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
from src.entities.ai_controller import SamuraiAI
from src.entities.pickups import PowderPouch
from src.combat.collision import CombatSystem
from src.effects.particles import AmbientLeafParticle, SparkParticle, BloodParticle, FloatingBanner, SmokeParticle
from src.effects.cinematic_director import CinematicDirector
from src.ui.settings_menu import SettingsMenu, format_key_name
from src.ui.character_select import CharacterSelectScreen
from src.ui.title_screen import SumieTitleScreen
from src.ui.arena_select import ArenaSelectScreen
from src.ui.loading_screen import LoadingScreen
from src.ui.fonts import get_title_font, get_text_font
from src.i18n import t
from src.input import get_controller_manager, TouchControls, DisplayScaler
from src.input.controls_storage import load_controls_config, save_controls_config

# Estados Globais do Jogo
STATE_TITLE = "TITLE"
STATE_CHAR_SELECT = "SELECT"
STATE_ARENA_SELECT = "ARENA_SELECT"
STATE_DUEL_PLAYING = "PLAYING"

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
    return RedSamurai(wx, wy)

def get_fighter_color(fighter):
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
        return "Puxar Yumi", "Flecha Corda"
    elif isinstance(fighter, PirateSwordswoman):
        return "Alfanje 180°", "Pólvora nos Olhos"
    elif isinstance(fighter, Musketeer):
        return "Estocada Fleche", "Capa Riposte"
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
        r_timer = max(0.0, getattr(fighter, "rope_timer", 0.0))
        if r_timer > 0:
            return {"name": "Flecha Corda", "timer": r_timer, "max_cd": getattr(fighter, "rope_cooldown", 2.0), "color": (210, 185, 120)}
        a_timer = max(0.0, getattr(fighter, "arrow_cooldown_timer", 0.0))
        if a_timer > 0:
            return {"name": "Flecha Yumi", "timer": a_timer, "max_cd": getattr(fighter, "arrow_cooldown", 1.20), "color": (100, 215, 140)}
        timer = max(0.0, getattr(fighter, "ofuda_cooldown_timer", 0.0))
        cd = getattr(fighter, "ofuda_cooldown", 3.2)
        return {"name": "Barreira Kami", "timer": timer, "max_cd": cd, "color": (130, 230, 180)}

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

    return None

def get_player_aim_target(fighter, controls, prefix: str, distance: float = 4.0, move_dir: tuple[float, float] | None = None) -> tuple[float, float]:
    """Calcula as coordenadas de mira para o ataque com base na entrada direcional ativa ou na orientação do lutador."""
    if move_dir and (move_dir[0] != 0 or move_dir[1] != 0):
        dwx, dwy = input_to_world_direction(move_dir[0], move_dir[1])
        return fighter.wx + dwx * distance, fighter.wy + dwy * distance
    keys = pygame.key.get_pressed()
    dx = keys[controls[f"{prefix}_RIGHT"]] - keys[controls[f"{prefix}_LEFT"]]
    dy = keys[controls[f"{prefix}_DOWN"]] - keys[controls[f"{prefix}_UP"]]
    if dx != 0 or dy != 0:
        dwx, dwy = input_to_world_direction(dx, dy)
        return fighter.wx + dwx * distance, fighter.wy + dwy * distance
    return fighter.wx + fighter.facing_x * distance, fighter.wy + fighter.facing_y * distance

def execute_fighter_attack(fighter, aim_x: float, aim_y: float, projectiles: list, particles: list):
    """Executa a ação primária de ataque do lutador em direção às coordenadas de mira."""
    if isinstance(fighter, RedSamurai):
        fighter.trigger_iai_attack(aim_x, aim_y)
    elif isinstance(fighter, BlueSamurai):
        fighter.trigger_combo_attack(aim_x, aim_y)
    elif isinstance(fighter, YellowNinja):
        if fighter.has_kunai:
            if fighter.state == "JUMP":
                fighter.trigger_midair_throw(aim_x, aim_y, projectiles)
            else:
                fighter.trigger_standing_throw(aim_x, aim_y, projectiles)
        else:
            fighter.trigger_thrust_attack(aim_x, aim_y)
    elif isinstance(fighter, AmericanNinja):
        fighter.trigger_shuriken(aim_x, aim_y, projectiles)
    elif isinstance(fighter, GrayNinja):
        fighter.trigger_throw_bomb(aim_x, aim_y, projectiles)
    elif isinstance(fighter, PurpleNinja):
        fighter.trigger_kama_strike(aim_x, aim_y)
    elif isinstance(fighter, SaitouSamurai):
        fighter.trigger_gatotsu_thrust(aim_x, aim_y)
    elif isinstance(fighter, Rifleman):
        if fighter.has_ammo:
            fighter.trigger_shoot(aim_x, aim_y, projectiles, particles)
        else:
            fighter.trigger_rifle_butt(aim_x, aim_y, particles)
    elif isinstance(fighter, Kabuki):
        fighter.trigger_fan_strike(aim_x, aim_y, particles)
    elif isinstance(fighter, KyudoArcher):
        fighter.trigger_bow_draw(aim_x, aim_y, projectiles)
    elif isinstance(fighter, PirateSwordswoman):
        fighter.trigger_cutlass_cleave(aim_x, aim_y)
    elif isinstance(fighter, Musketeer):
        fighter.trigger_fleche_thrust(aim_x, aim_y)

def execute_fighter_secondary(fighter, aim_x: float, aim_y: float, dwx: float, dwy: float, projectiles: list, particles: list, decoys: list, poison_clouds: list, powder_traps: list, opponent=None, game_map=None, banners: list = None):
    """Executa a Ação Secundária (Técnica Especial / Defesa / Contra-ataque) do combatente."""
    if isinstance(fighter, RedSamurai):
        # Kenshi: Ryuu Tsui Sen (Salto vertical e corte descendente devastador)
        fighter.trigger_ryuu_tsui_sen(aim_x, aim_y, particles=particles, banners=banners, opponent=opponent)
    elif isinstance(fighter, BlueSamurai):
        fighter.set_facing(aim_x, aim_y)
        fighter.trigger_parry()
    elif isinstance(fighter, YellowNinja):
        if fighter.state == "JUMP" and fighter.has_kunai:
            fighter.trigger_midair_throw(aim_x, aim_y, projectiles)
        else:
            fighter.trigger_jump(aim_x, aim_y, projectiles)
    elif isinstance(fighter, AmericanNinja):
        fighter.trigger_dog_attack(aim_x, aim_y)
    elif isinstance(fighter, GrayNinja):
        all_f = [fighter, opponent] if opponent else [fighter]
        fighter.trigger_remote_mine(aim_x, aim_y, projectiles, fighters=all_f, particles=particles, banners=banners)
    elif isinstance(fighter, PurpleNinja):
        fighter.start_chain_shield(aim_x, aim_y)
    elif isinstance(fighter, SaitouSamurai):
        fighter.trigger_zeroshiki(aim_x, aim_y)
    elif isinstance(fighter, Rifleman):
        # Teppo: Black Powder Ground Trap (Trilha de pólvora inflamável no solo)
        fighter.trigger_powder_trap(aim_x, aim_y, powder_traps, particles)
    elif isinstance(fighter, Kabuki):
        # Okuni: Dokukiri (Sopro de névoa venenosa com leques de ferro)
        fighter.trigger_dokukiri(aim_x, aim_y, poison_clouds)
    elif isinstance(fighter, KyudoArcher):
        # Tomoe: Barreira dos Ventos Kami (3 Ofudas defensivos em órbita)
        fighter.trigger_ofuda_barrier()
    elif isinstance(fighter, PirateSwordswoman):
        # Anne Bonny: Naval Artillery Strike (Hold & release orbital cannonball)
        fighter.start_cannon_strike(aim_x, aim_y)
    elif isinstance(fighter, Musketeer):
        # Julie: Disparo veloz de pederneira (Pocket Flintlock de curto alcance - Item 7 e 20)
        fighter.trigger_flintlock_shot(aim_x, aim_y, projectiles, particles=particles)

def execute_fighter_roll(fighter, dwx: float, dwy: float, aim_x: float, aim_y: float, particles: list, decoys: list = None, game_map=None, opponent=None, banners=None):
    """Executa a Terceira Ação (Roll / Dash dedicado) com invulnerabilidade temporária (i-frames)."""
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
    elif isinstance(fighter, Musketeer):
        # Julie: Cape Flourish & Coup de Pied (Repel de esquiva - Item 7)
        fighter.trigger_roll(dwx, dwy, particles=particles, opponent=opponent, banners=banners)
    else:
        # Demais personagens (BlueSamurai, YellowNinja, AmericanNinja, GrayNinja, PurpleNinja, SaitouSamurai)
        if hasattr(fighter, "trigger_roll"):
            fighter.trigger_roll(dwx, dwy, particles)

def execute_fighter_dash(fighter, aim_x: float, aim_y: float, dwx: float, dwy: float, projectiles: list, particles: list, decoys: list, opponent=None, game_map=None, poison_clouds=None, powder_traps=None):
    """Compatibilidade legada: direciona para a terceira ação de roll/dash dedicado."""
    execute_fighter_roll(fighter, dwx, dwy, aim_x, aim_y, particles, decoys=decoys, game_map=game_map)

def get_random_arena_spawns(game_map, min_distance: float = 7.0) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Gera duas posições aleatórias válidas (chão firme) no mapa
    com distância euclidiana mínima garantida (>= min_distance) para evitar acerto melee de início.
    """
    for _ in range(250):
        wx1 = round(random.uniform(3.0, game_map.cols - 3.0), 1)
        wy1 = round(random.uniform(3.0, game_map.rows - 3.0), 1)
        if game_map.is_water(wx1, wy1):
            continue
        if any(math.hypot(wx1 - r.wx, wy1 - r.wy) < (r.radius + 0.65) for r in game_map.rocks):
            continue
        if game_map.well and math.hypot(wx1 - game_map.well.wx, wy1 - game_map.well.wy) < 1.6:
            continue
        if any(math.hypot(wx1 - t.wx, wy1 - t.wy) < 1.7 for t in game_map.trees):
            continue

        for _ in range(40):
            wx2 = round(random.uniform(3.0, game_map.cols - 3.0), 1)
            wy2 = round(random.uniform(3.0, game_map.rows - 3.0), 1)
            if math.hypot(wx1 - wx2, wy1 - wy2) < min_distance:
                continue
            if game_map.is_water(wx2, wy2):
                continue
            if any(math.hypot(wx2 - r.wx, wy2 - r.wy) < (r.radius + 0.65) for r in game_map.rocks):
                continue
            if game_map.well and math.hypot(wx2 - game_map.well.wx, wy2 - game_map.well.wy) < 1.6:
                continue
            if any(math.hypot(wx2 - t.wx, wy2 - t.wy) < 1.7 for t in game_map.trees):
                continue
            return (wx1, wy1), (wx2, wy2)

    # Fallback garantido: extremidades norte e sul da ponte de madeira (distância = 8.0 tiles)
    return (10.5, 7.0), (10.5, 15.0)

def get_kyoto_arena_spawns(game_map, min_distance: float = 7.0) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Gera duas posições de spawn equilibradas na rua estreita diagonal de Kyoto (wx entre 9.5 e 11.5)
    com distância mínima garantida (>= min_distance).
    """
    for _ in range(150):
        wx1 = round(random.uniform(9.5, 11.5), 1)
        wy1 = round(random.uniform(4.0, game_map.rows - 4.0), 1)

        for _ in range(30):
            wx2 = round(random.uniform(9.5, 11.5), 1)
            wy2 = round(random.uniform(4.0, game_map.rows - 4.0), 1)
            if math.hypot(wx1 - wx2, wy1 - wy2) >= min_distance:
                return (wx1, wy1), (wx2, wy2)
    return (10.5, 6.0), (10.5, 15.0)


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


def run_game():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

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

    settings_menu = SettingsMenu(controls, touch_controls=touch_controls)

    loading_screen.update(0.50, "Carregando atmosfera Sumi-e e tela inicial...", delay_ms=40)
    title_screen = SumieTitleScreen()

    loading_screen.update(0.72, "Carregando retratos e atributos dos 12 guerreiros...", delay_ms=50)
    char_select_screen = CharacterSelectScreen()

    loading_screen.update(0.90, "Sintonizando arenas e cenários dinâmicos...", delay_ms=40)
    arena_select_screen = ArenaSelectScreen()

    loading_screen.update(1.0, "Pronto! Entrando no Bakumatsu...", delay_ms=60)

    game_state = STATE_TITLE
    selected_arena_id = ARENA_KYOTO

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
    ai = SamuraiAI()

    particles = []
    banners = []
    projectiles = []
    ambient_leaves = []
    powder_pouches = []
    decoys = []
    poison_clouds = []
    powder_traps = []

    round_winner = None
    game_time = 0.0
    round_start_timer = 1.8
    round_start_shaken = False

    static_render_queue = []

    def start_new_match():
        nonlocal p1, p2, game_map, camera, particles, banners, projectiles, ambient_leaves, round_winner, round_start_timer, round_start_shaken, powder_pouches, decoys, poison_clouds, powder_traps, static_render_queue
        if selected_arena_id == ARENA_KYOTO:
            game_map = KyotoMap()
            (p1_wx, p1_wy), (p2_wx, p2_wy) = get_kyoto_arena_spawns(game_map, min_distance=7.0)
        else:
            game_map = GameMap()
            (p1_wx, p1_wy), (p2_wx, p2_wy) = get_random_arena_spawns(game_map, min_distance=7.0)

        p1 = create_fighter(p1_char_id, wx=p1_wx, wy=p1_wy)
        p2 = create_fighter(p2_char_id, wx=p2_wx, wy=p2_wy)
        p1.set_facing(p2.wx, p2.wy)
        p2.set_facing(p1.wx, p1.wy)
        for f in (p1, p2):
            if isinstance(f, Kabuki):
                f.registered_decoys = decoys
        camera = Camera(target_wx=(p1_wx + p2_wx) / 2.0, target_wy=(p1_wy + p2_wy) / 2.0)
        particles.clear()
        banners.clear()
        projectiles.clear()
        decoys.clear()
        poison_clouds.clear()
        powder_traps.clear()
        powder_pouches = PowderPouch.create_arena_pouches(game_map, [p1, p2], total_pouches=3)
        ambient_leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(45)]
        round_winner = None
        round_start_timer = 1.8
        round_start_shaken = False
        cinematic_director.reset_round()
        static_render_queue = build_static_render_queue(game_map)

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

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
                        char_select_screen.reset()
                        game_state = STATE_CHAR_SELECT
                    elif action == "OPTIONS":
                        settings_menu.open()
                    elif action == "QUIT":
                        running = False

            title_screen.update(dt)
            title_screen.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # TELA DE SELEÇÃO DE PERSONAGENS
        # -------------------------------------------------------------
        if game_state == STATE_CHAR_SELECT:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                else:
                    start_match = char_select_screen.handle_event(event)
                    if start_match == "BACK":
                        game_state = STATE_TITLE
                    elif start_match:
                        p1_char_id, p2_char_id, vs_ai_mode = char_select_screen.get_selected_characters()
                        game_state = STATE_ARENA_SELECT

            char_select_screen.update(dt)
            char_select_screen.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # TELA DE SELEÇÃO DE ARENA
        # -------------------------------------------------------------
        if game_state == STATE_ARENA_SELECT:
            for event in pygame.event.get():
                ctrl_mgr.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                else:
                    arena_choice = arena_select_screen.handle_event(event)
                    if arena_choice == "BACK":
                        game_state = STATE_CHAR_SELECT
                    elif arena_choice in (ARENA_BAMBOO, ARENA_KYOTO):
                        selected_arena_id = arena_choice
                        start_new_match()
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
            settings_menu.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # DUELO EM ANDAMENTO (GAME LOOP)
        # -------------------------------------------------------------
        touch_controls.reset_frame_triggers()

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

        p1_dwx, p1_dwy = input_to_world_direction(p1_active_dir[0], p1_active_dir[1])
        p2_dwx, p2_dwy = input_to_world_direction(p2_active_dir[0], p2_active_dir[1])

        # Atualização do Temporizador de Abertura de Round e Tremor de Tela (Item 10)
        if round_start_timer > -0.5:
            round_start_timer -= dt
            if round_start_timer <= 0.6 and not round_start_shaken:
                camera.add_shake(4.5)
                ctrl_mgr.rumble_player(0, 0.4, 0.6, 120)
                ctrl_mgr.rumble_player(1, 0.4, 0.6, 120)
                round_start_shaken = True

        # Bloqueio de movimentação durante abertura do round (Item 10)
        if round_start_timer > 0:
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
                    game_state = STATE_ARENA_SELECT
                elif event.key == KEY_SETTINGS:
                    settings_menu.open()
                elif event.key == KEY_RESTART:
                    if round_winner is not None:
                        start_new_match()
                elif event.key == KEY_TOGGLE_AI:
                    vs_ai_mode = not vs_ai_mode

                # Ao terminar um duelo, permitir que Quadrado / Ação Primária reinicie o duelo (mas nunca com duelo em andamento)
                if round_winner is not None:
                    if event.key in (KEY_RESTART, controls["P1_ATTACK"], controls["P2_ATTACK"]):
                        start_new_match()

                # Comandos Jogador 1 (Teclado)
                if p1.is_alive and round_winner is None and round_start_timer <= 0:
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
                if not vs_ai_mode and p2.is_alive and round_winner is None and round_start_timer <= 0:
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
                    settings_menu.open()
                elif round_winner is not None:
                    # Ao terminar o duelo, tanto restart quanto quadrado/ação primária reiniciam
                    if (ctrl_mgr.is_event_action(event, 0, "restart") or
                        ctrl_mgr.is_event_action(event, 0, "attack") or
                        ctrl_mgr.is_event_action(event, 1, "restart") or
                        ctrl_mgr.is_event_action(event, 1, "attack")):
                        start_new_match()
                elif p1.is_alive and round_winner is None and round_start_timer <= 0:
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
                if not vs_ai_mode and p2.is_alive and round_winner is None and round_start_timer <= 0:
                    if ctrl_mgr.is_event_menu_pause(event, 1) or (getattr(event, "button", None) == 6):
                        settings_menu.open()
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
                    start_new_match()
                else:
                    settings_btn_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 44, 180, 28)
                    if settings_btn_rect.collidepoint(mx, my):
                        settings_menu.open()
                    select_btn_rect = pygame.Rect(25, 20, 160, 32)
                    if select_btn_rect.collidepoint(mx, my):
                        game_state = STATE_ARENA_SELECT

        # Comandos de Ação Touchscreen
        if touch_controls.is_menu_requested():
            settings_menu.open()
        if touch_controls.is_select_requested():
            game_state = STATE_ARENA_SELECT

        if p1.is_alive and round_winner is None and round_start_timer <= 0:
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
        if isinstance(p1, PirateSwordswoman) and p1.is_alive and round_winner is None and round_start_timer <= 0:
            if p1_sec_held:
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                p1.update_cannon_strike(dt, aim_x, aim_y)
            else:
                if p1.is_aiming_cannon:
                    p1.release_cannon_strike(projectiles, particles)

        p2_sec_key = controls.get("P2_SECONDARY", pygame.K_i)
        p2_sec_held = keys[p2_sec_key] or (controls.get("P2_PARRY") and keys[controls["P2_PARRY"]]) or ctrl_mgr.is_action_down(1, "secondary")
        if not vs_ai_mode and isinstance(p2, PirateSwordswoman) and p2.is_alive and round_winner is None and round_start_timer <= 0:
            if p2_sec_held:
                aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                p2.update_cannon_strike(dt, aim_x, aim_y)
            else:
                if p2.is_aiming_cannon:
                    p2.release_cannon_strike(projectiles, particles)

        # Suporte ao carregamento contínuo de pólvora do Rifleman (segurando ação secundária)
        if isinstance(p1, Rifleman) and p1.is_alive and round_winner is None and round_start_timer <= 0:
            if p1_sec_held and not p1.has_ammo:
                p1.trigger_reload_hold()
            else:
                p1.is_reloading = False

        if not vs_ai_mode and isinstance(p2, Rifleman) and p2.is_alive and round_winner is None and round_start_timer <= 0:
            if p2_sec_held and not p2.has_ammo:
                p2.trigger_reload_hold()
            else:
                p2.is_reloading = False

        # Suporte ao Hold and Release da Flecha de Corda de Tomoe (KyudoArcher) na Terceira Ação (Roll / Dash dedicado)
        p1_dash_held = keys[controls.get("P1_DASH", pygame.K_t)] or ctrl_mgr.is_action_down(0, "dash") or touch_controls.is_dash_held()
        if isinstance(p1, KyudoArcher) and p1.is_alive and round_winner is None and round_start_timer <= 0:
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
        if not vs_ai_mode and isinstance(p2, KyudoArcher) and p2.is_alive and round_winner is None and round_start_timer <= 0:
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
        if isinstance(p1, PurpleNinja) and p1.is_alive and round_winner is None and round_start_timer <= 0:
            if p1_sec_held:
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                p1.update_chain_shield(dt, aim_x, aim_y)
            else:
                if getattr(p1, "is_holding_shield", False):
                    p1.release_chain_shield(projectiles, particles)

        if not vs_ai_mode and isinstance(p2, PurpleNinja) and p2.is_alive and round_winner is None and round_start_timer <= 0:
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
                elif isinstance(f, PirateSwordswoman):
                    f.is_aiming_cannon = False
                elif isinstance(f, PurpleNinja):
                    f.is_holding_shield = False
                    f.is_spinning_chain = False

        # Suporte ao congelamento dramático de cinema samurai
        is_cinematic_freeze = cinematic_director.is_frozen()

        if not is_cinematic_freeze:
            # Movimento Jogador 1
            if hasattr(p1, "apply_gatotsu_steering") and p1.state == "GATOTSU_CHARGE":
                p1.apply_gatotsu_steering(p1_dwx, p1_dwy, dt)
            else:
                p1.apply_movement(p1_dwx, p1_dwy, dt, game_map)

            # Movimento Jogador 2 (IA ou Humano)
            if vs_ai_mode:
                if round_start_timer <= 0:
                    ai.update(p2, p1, dt, game_map, projectiles, powder_pouches, decoys)
            else:
                if hasattr(p2, "apply_gatotsu_steering") and p2.state == "GATOTSU_CHARGE":
                    p2.apply_gatotsu_steering(p2_dwx, p2_dwy, dt)
                else:
                    p2.apply_movement(p2_dwx, p2_dwy, dt, game_map)

        # Atualizações dos combatentes e coletáveis
        if not is_cinematic_freeze:
            # Atualização de perigos da Arena de Kyoto (Carruagens e Escombros)
            if isinstance(game_map, KyotoMap):
                game_map.update(dt, [p1, p2], camera, particles, banners, cinematic_director)

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

            for f in (p1, p2):
                opp = p2 if f is p1 else p1
                if isinstance(f, Rifleman):
                    f.check_powder_pickup(powder_pouches, particles)
                if isinstance(f, PirateSwordswoman):
                    f.update(dt, game_map, particles, opponent=opp, banners=banners)
                elif isinstance(f, SaitouSamurai):
                    f.update(dt, game_map, particles)
                elif isinstance(f, (Rifleman, Kabuki, Musketeer, GrayNinja)):
                    f.update(dt, game_map, particles)
                elif isinstance(f, KyudoArcher):
                    f.update(dt, game_map, particles, projectiles)
                else:
                    f.update(dt, game_map)

                # Decremento universal de cooldown de impacto com obstáculos sólidos
                if getattr(f, "obstacle_spark_timer", 0) > 0:
                    f.obstacle_spark_timer -= dt

                # Item 17: Indicador visual e decremento de lentidão (fuligem de pólvora escorrendo aos pés)
                if f.is_alive and getattr(f, "slow_timer", 0) > 0:
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

        # Atualizar Diretor Cinematográfico (Temporizadores e Corpos Voxel)
        cinematic_director.update(dt, game_map, particles)

        # Processar Combate & Projéteis
        winner = combat_system.process_combat(p1, p2, game_map, particles, banners, camera, projectiles, dt, cinematic_director=cinematic_director, decoys=decoys, ctrl_mgr=ctrl_mgr)
        if winner and round_winner is None:
            round_winner = winner
            ctrl_mgr.rumble_player(0, 0.7, 1.0, 260)
            ctrl_mgr.rumble_player(1, 0.7, 1.0, 260)
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
            elif not p2.is_alive and p1.is_alive:
                round_winner = "P1_WINS"
                score_p1 += 1
                ctrl_mgr.rumble_player(0, 0.7, 1.0, 260)
                ctrl_mgr.rumble_player(1, 0.7, 1.0, 260)
            elif not p1.is_alive and not p2.is_alive:
                round_winner = "DRAW"

        # Câmera segue o ponto médio
        mid_x = (p1.wx + p2.wx) / 2.0
        mid_y = (p1.wy + p2.wy) / 2.0
        camera.update(mid_x, mid_y, dt)

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
            leaf.update(dt)

        # -------------------------------------------------------------
        # RENDERIZAÇÃO COM Y-SORTING DIVIDIDO (ESTÁTICO VS DINÂMICO)
        # -------------------------------------------------------------
        bg_col = COLOR_KYOTO_BG if isinstance(game_map, KyotoMap) else COLOR_BG
        screen.fill(bg_col)
        game_map.render_terrain(screen, camera, game_time)

        # Entregável 1.3: Reutiliza a fila estática pré-calculada do cenário
        if not static_render_queue:
            static_render_queue = build_static_render_queue(game_map)
        render_queue = list(static_render_queue)

        # Adicionar elementos dinâmicos exclusivos (Carruagens, Escombros de Kyoto)
        if hasattr(game_map, 'carriages'):
            for c in game_map.carriages:
                if c.is_active and c.warning_timer <= 0:
                    render_queue.append((c.wx + c.wy, 'carriage', c))
        if hasattr(game_map, 'falling_debris'):
            for d in game_map.falling_debris:
                if d.is_active:
                    render_queue.append((d.target_x + d.target_y, 'debris', d))


        render_queue.append((p1.wx + p1.wy, 'fighter', p1))
        render_queue.append((p2.wx + p2.wy, 'fighter', p2))

        # Adicionar cão Doberman ao Y-sorting se houver American Ninja na partida
        if hasattr(p1, "dog") and p1.dog:
            render_queue.append((p1.dog.wx + p1.dog.wy, 'dog', p1.dog))
        if hasattr(p2, "dog") and p2.dog:
            render_queue.append((p2.dog.wx + p2.dog.wy, 'dog', p2.dog))

        # Adicionar corpos voxel fatiados ao Y-sorting
        for corpse in cinematic_director.corpses:
            render_queue.append((corpse.wx + corpse.wy, 'corpse', corpse))

        for pouch in powder_pouches:
            if pouch.is_active:
                render_queue.append((pouch.wx + pouch.wy, 'pouch', pouch))

        for decoy in decoys:
            if decoy.is_active:
                render_queue.append((decoy.wx + decoy.wy, 'decoy', decoy))

        for pt in powder_traps:
            if pt.is_active:
                render_queue.append((pt.wx + pt.wy, 'powder_trap', pt))

        for pc in poison_clouds:
            if pc.is_active:
                render_queue.append((pc.wx + pc.wy, 'poison_cloud', pc))

        for proj in projectiles:
            render_queue.append((proj.wx + proj.wy, 'projectile', proj))

        for p in particles:
            if hasattr(p, 'wx') and hasattr(p, 'wy'):
                render_queue.append((p.wx + p.wy, 'particle', p))

        render_queue.sort(key=lambda item: item[0])

        for _, item_type, obj in render_queue:
            if item_type == 'bamboo':
                obj.render(screen, camera, game_time)
            elif item_type in ('rock', 'well', 'tree', 'torii'):
                obj.render(screen, camera)
            elif item_type == 'building':
                obj.render(screen, camera, game_time)
            elif item_type == 'lantern':
                obj.render(screen, camera, game_time)
            elif item_type == 'carriage':
                obj.render(screen, camera)
            elif item_type == 'debris':
                obj.render(screen, camera)
            elif item_type == 'fighter':
                obj.render(screen, camera)
            elif item_type == 'dog':
                obj.render(screen, camera)
            elif item_type == 'corpse':
                obj.render(screen, camera)
            elif item_type == 'pouch':
                obj.render(screen, camera, font_small)
            elif item_type == 'decoy':
                obj.render(screen, camera)
            elif item_type == 'powder_trap':
                obj.render(screen, camera)
            elif item_type == 'poison_cloud':
                obj.render(screen, camera)
            elif item_type == 'projectile':
                obj.render(screen, camera)
            elif item_type == 'particle':
                obj.render(screen, camera)

        for leaf in ambient_leaves:
            leaf.render(screen, camera)

        # Vaga-lumes bioluminescentes sobre o lago zen
        if hasattr(game_map, 'fireflies'):
            for fx, fy, fz in game_map.fireflies:
                w_fx = fx + math.sin(game_time * 2.0 + fy) * 0.12
                w_fy = fy + math.cos(game_time * 1.8 + fx) * 0.12
                w_fz = fz + math.sin(game_time * 2.5 + fx * 2.0) * 0.08
                fsx, fsy = camera.apply(w_fx, w_fy, w_fz)
                pygame.draw.circle(screen, (180, 255, 80), (fsx, fsy), 3)
                pygame.draw.circle(screen, (220, 255, 160), (fsx, fsy), 6, 1)

        for banner in banners:
            banner.render(screen, camera, font_mid)

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

        p1_title = font_mid.render(f"{p1_name}  {score_p1}", True, p1_color)
        p2_title = font_mid.render(f"{score_p2}  {p2_name}", True, p2_color)
        screen.blit(p1_title, (panel_rect.x + 20, panel_rect.y + 10))
        screen.blit(p2_title, (panel_rect.right - p2_title.get_width() - 20, panel_rect.y + 10))

        mode_text = t("mode_hud_1p") if vs_ai_mode else t("mode_hud_2p")
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


        # Botão Trocar Personagens no topo esquerdo
        select_btn = pygame.Rect(25, 20, 180, 32)
        pygame.draw.rect(screen, (26, 34, 30, 210), select_btn, border_radius=6)
        pygame.draw.rect(screen, COLOR_GOLD, select_btn, 1, border_radius=6)
        sel_txt = font_small.render(t("change_warriors"), True, COLOR_GOLD)
        screen.blit(sel_txt, (select_btn.centerx - sel_txt.get_width() // 2, select_btn.y + 7))

        # Guia de Controles no Rodapé (Teclado, Gamepad Dinâmico ou Touch)
        footer_rect = pygame.Rect(20, SCREEN_HEIGHT - 48, SCREEN_WIDTH - 40, 36)
        pygame.draw.rect(screen, (16, 20, 18, 200), footer_rect, border_radius=6)

        k_atk = format_key_name(controls["P1_ATTACK"])
        k_sec = format_key_name(controls["P1_DASH"])
        m_atk = format_key_name(controls["P2_ATTACK"])
        m_sec = format_key_name(controls["P2_PARRY"])

        p1_a1, p1_a2 = get_fighter_action_labels(p1)
        p2_a1, p2_a2 = get_fighter_action_labels(p2)

        # Prompts contextuais para P1
        if ctrl_mgr.has_controller(0):
            badge1 = ctrl_mgr.get_badge_text(0)
            ctrl1 = ctrl_mgr.get_controller_for_player(0)
            btn_atk1 = ctrl1.get_button_glyph("attack") if ctrl1 else "▢"
            btn_sec1 = ctrl1.get_button_glyph("dash") if ctrl1 else "✕"
            btn_menu1 = ctrl1.get_button_glyph("menu") if ctrl1 else "Options"
            c1 = font_small.render(f"{badge1} P1: Stick | [{btn_atk1}] = {p1_a1} | [{btn_sec1}] = {p1_a2} | [{btn_menu1}] = Menu", True, (245, 205, 205))
        elif touch_controls.is_visible:
            c1 = font_small.render(f"[TOUCH] P1 ({p1_name}): Joy = Mover | [ATK] = {p1_a1} | [DASH] = {p1_a2}", True, (245, 205, 205))
        else:
            c1 = font_small.render(f"P1 ({p1_name}): W/A/S/D | {k_atk} = {p1_a1} | {k_sec} = {p1_a2}", True, (245, 205, 205))

        # Prompts contextuais para P2
        if not vs_ai_mode and ctrl_mgr.has_controller(1):
            badge2 = ctrl_mgr.get_badge_text(1)
            ctrl2 = ctrl_mgr.get_controller_for_player(1)
            btn_atk2 = ctrl2.get_button_glyph("attack") if ctrl2 else "▢"
            btn_sec2 = ctrl2.get_button_glyph("dash") if ctrl2 else "✕"
            btn_menu2 = ctrl2.get_button_glyph("menu") if ctrl2 else "Options"
            c2 = font_small.render(f"{badge2} P2: Stick | [{btn_atk2}] = {p2_a1} | [{btn_sec2}] = {p2_a2} | [{btn_menu2}] = Menu", True, (205, 225, 245))
        else:
            c2 = font_small.render(f"P2 ({p2_name}): {t('arrows_label')} | {m_atk} = {p2_a1} | {m_sec} = {p2_a2}", True, (205, 225, 245))

        screen.blit(c1, (30, SCREEN_HEIGHT - 40))
        screen.blit(c2, (SCREEN_WIDTH // 2 - c2.get_width() // 2 - 30, SCREEN_HEIGHT - 40))

        # Renderizar Controles Virtuais Touchscreen (se ativos/visíveis)
        touch_controls.set_action_labels(p1_a1, p1_a2)
        touch_controls.render(screen, font_mid, font_small)

        settings_btn_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 44, 180, 28)
        pygame.draw.rect(screen, (40, 52, 45), settings_btn_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_GOLD, settings_btn_rect, 1, border_radius=4)
        c3 = font_small.render(t("settings_btn"), True, COLOR_GOLD)
        screen.blit(c3, (settings_btn_rect.centerx - c3.get_width() // 2, settings_btn_rect.y + 5))

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

        # Banner de Vitória
        if round_winner:
            if round_winner == "DRAW":
                w_msg = t("draw_text")
                w_color = COLOR_GOLD
            else:
                w_fighter = p1 if round_winner == "P1_WINS" else p2
                w_msg = t("victory_text", name=w_fighter.name.upper())
                w_color = get_fighter_color(w_fighter)
            v_surf = font_large.render(w_msg, True, w_color)
            sub_surf = font_mid.render(t("next_round_hint"), True, COLOR_WHITE)

            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2 - 40
            screen.blit(v_surf, (center_x - v_surf.get_width() // 2, center_y))
            screen.blit(sub_surf, (center_x - sub_surf.get_width() // 2, center_y + 48))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
