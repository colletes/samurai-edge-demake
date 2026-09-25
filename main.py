"""
Ponto de entrada principal: Duelo de Samurais Isométrico 2.5D.
Suporte à Seleção de Personagens: Kenshi (Vermelho), Musashi (Azul) e Ninja Hanzo (Amarelo).
"""
import sys
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
from src.entities.rifleman import Rifleman
from src.entities.kabuki import Kabuki
from src.entities.kyudo_archer import KyudoArcher
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.entities.ai_controller import SamuraiAI
from src.entities.pickups import PowderPouch
from src.combat.collision import CombatSystem
from src.effects.particles import AmbientLeafParticle
from src.effects.cinematic_director import CinematicDirector
from src.ui.settings_menu import SettingsMenu, format_key_name
from src.ui.character_select import CharacterSelectScreen
from src.ui.title_screen import SumieTitleScreen
from src.ui.arena_select import ArenaSelectScreen
from src.i18n import t
from src.input import get_controller_manager, TouchControls, DisplayScaler

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
                fighter.trigger_jump_and_throw(aim_x, aim_y, projectiles)
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

def execute_fighter_dash(fighter, aim_x: float, aim_y: float, dwx: float, dwy: float, projectiles: list, particles: list, decoys: list, opponent=None, game_map=None):
    """Executa a ação secundária de esquiva/parry/especial do lutador."""
    if isinstance(fighter, RedSamurai):
        fighter.trigger_dash(dwx, dwy)
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
        fighter.trigger_smoke_bomb(aim_x, aim_y, projectiles)
    elif isinstance(fighter, PurpleNinja):
        fighter.trigger_kusarigama_pull(aim_x, aim_y, projectiles)
    elif isinstance(fighter, SaitouSamurai):
        fighter.trigger_zeroshiki(aim_x, aim_y)
    elif isinstance(fighter, Rifleman):
        fighter.trigger_evasive_backstep(particles)
    elif isinstance(fighter, Kabuki):
        fighter.trigger_kawarimi_decoy(dwx, dwy, decoys, particles)
    elif isinstance(fighter, KyudoArcher):
        fighter.start_rope_arrow_charge(aim_x, aim_y, game_map)
    elif isinstance(fighter, PirateSwordswoman):
        fighter.trigger_gunpowder_blind(aim_x, aim_y, opponent=opponent, particles=particles)
    elif isinstance(fighter, Musketeer):
        fighter.trigger_cloak_riposte()

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

def run_game():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    # Dispositivos de Entrada e Viewport Responsivo
    ctrl_mgr = get_controller_manager()
    touch_controls = TouchControls()
    scaler = DisplayScaler(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Menus e Telas
    controls = dict(DEFAULT_CONTROLS)
    settings_menu = SettingsMenu(controls, touch_controls=touch_controls)
    title_screen = SumieTitleScreen()
    char_select_screen = CharacterSelectScreen()
    arena_select_screen = ArenaSelectScreen()

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

    round_winner = None
    game_time = 0.0
    round_start_timer = 2.4

    def start_new_match():
        nonlocal p1, p2, game_map, camera, particles, banners, projectiles, ambient_leaves, round_winner, round_start_timer, powder_pouches, decoys
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
        camera = Camera(target_wx=(p1_wx + p2_wx) / 2.0, target_wy=(p1_wy + p2_wy) / 2.0)
        particles.clear()
        banners.clear()
        projectiles.clear()
        decoys.clear()
        powder_pouches = PowderPouch.create_arena_pouches(game_map, [p1, p2], total_pouches=3)
        ambient_leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(45)]
        round_winner = None
        round_start_timer = 2.4
        cinematic_director.reset_round()

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
                    start_new_match()
                elif event.key == KEY_TOGGLE_AI:
                    vs_ai_mode = not vs_ai_mode

                # Comandos Jogador 1 (Teclado)
                if p1.is_alive and round_winner is None:
                    if event.key == controls["P1_ATTACK"]:
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_attack(p1, aim_x, aim_y, projectiles, particles)
                    elif event.key == controls["P1_DASH"]:
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_dash(p1, aim_x, aim_y, p1_dwx, p1_dwy, projectiles, particles, decoys, opponent=p2, game_map=game_map)

                # Comandos Jogador 2 (Teclado)
                if not vs_ai_mode and p2.is_alive and round_winner is None:
                    if event.key == controls["P2_ATTACK"]:
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_attack(p2, aim_x, aim_y, projectiles, particles)
                    elif event.key == controls["P2_PARRY"]:
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_dash(p2, aim_x, aim_y, p2_dwx, p2_dwy, projectiles, particles, decoys, opponent=p1, game_map=game_map)

            elif event.type == pygame.JOYBUTTONDOWN:
                if ctrl_mgr.is_event_menu_pause(event, 0) or (getattr(event, "button", None) == 6):
                    settings_menu.open()
                elif ctrl_mgr.is_event_action(event, 0, "restart"):
                    if round_winner is not None:
                        start_new_match()
                elif p1.is_alive and round_winner is None:
                    if ctrl_mgr.is_event_action(event, 0, "attack"):
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_attack(p1, aim_x, aim_y, projectiles, particles)
                    elif ctrl_mgr.is_event_action(event, 0, "dash"):
                        aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                        execute_fighter_dash(p1, aim_x, aim_y, p1_dwx, p1_dwy, projectiles, particles, decoys, opponent=p2, game_map=game_map)

                # Gamepad Jogador 2
                if not vs_ai_mode and p2.is_alive and round_winner is None:
                    if ctrl_mgr.is_event_menu_pause(event, 1) or (getattr(event, "button", None) == 6):
                        settings_menu.open()
                    elif ctrl_mgr.is_event_action(event, 1, "attack"):
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_attack(p2, aim_x, aim_y, projectiles, particles)
                    elif ctrl_mgr.is_event_action(event, 1, "dash"):
                        aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                        execute_fighter_dash(p2, aim_x, aim_y, p2_dwx, p2_dwy, projectiles, particles, decoys, opponent=p1, game_map=game_map)

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

        if p1.is_alive and round_winner is None:
            if touch_controls.is_attack_just_pressed():
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                execute_fighter_attack(p1, aim_x, aim_y, projectiles, particles)
            elif touch_controls.is_dash_just_pressed():
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                execute_fighter_dash(p1, aim_x, aim_y, p1_dwx, p1_dwy, projectiles, particles, decoys, opponent=p2, game_map=game_map)

        # Hitstop congelado
        if combat_system.hitstop_timer > 0:
            combat_system.hitstop_timer -= dt
            pygame.display.flip()
            continue

        game_time += dt

        # Suporte ao carregamento contínuo de pólvora do Rifleman (segurando botão de ação secundária)
        p1_dash_held = keys[controls["P1_DASH"]] or ctrl_mgr.is_action_down(0, "dash") or touch_controls.is_dash_held()
        if isinstance(p1, Rifleman) and p1.is_alive and round_winner is None:
            if p1_dash_held:
                p1.trigger_reload_hold()
            else:
                p1.is_reloading = False

        # Suporte ao Hold and Release da Flecha de Corda de Tomoe (KyudoArcher)
        if isinstance(p1, KyudoArcher) and p1.is_alive and round_winner is None:
            if p1_dash_held:
                aim_x, aim_y = get_player_aim_target(p1, controls, "P1", move_dir=p1_active_dir)
                if not p1.is_charging_rope:
                    p1.start_rope_arrow_charge(aim_x, aim_y, game_map)
                else:
                    p1.update_rope_charge(dt, aim_x, aim_y, game_map)
            else:
                if p1.is_charging_rope:
                    p1.release_rope_arrow(projectiles, particles, game_map)

        p2_dash_held = keys[controls["P2_PARRY"]] or ctrl_mgr.is_action_down(1, "dash")
        if not vs_ai_mode and isinstance(p2, Rifleman) and p2.is_alive and round_winner is None:
            if p2_dash_held:
                p2.trigger_reload_hold()
            else:
                p2.is_reloading = False

        if not vs_ai_mode and isinstance(p2, KyudoArcher) and p2.is_alive and round_winner is None:
            if p2_dash_held:
                aim_x, aim_y = get_player_aim_target(p2, controls, "P2", move_dir=p2_active_dir)
                if not p2.is_charging_rope:
                    p2.start_rope_arrow_charge(aim_x, aim_y, game_map)
                else:
                    p2.update_rope_charge(dt, aim_x, aim_y, game_map)
            else:
                if p2.is_charging_rope:
                    p2.release_rope_arrow(projectiles, particles, game_map)

        # Cancelar carregamento se a rodada terminou
        if round_winner is not None:
            if isinstance(p1, KyudoArcher):
                p1.is_charging_rope = False
            if isinstance(p2, KyudoArcher):
                p2.is_charging_rope = False

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

            for pouch in powder_pouches:
                pouch.update(dt, game_map, particles)
            for f in (p1, p2):
                if isinstance(f, Rifleman):
                    f.check_powder_pickup(powder_pouches, particles)
                if isinstance(f, SaitouSamurai):
                    f.update(dt, game_map, particles)
                elif isinstance(f, (Rifleman, Kabuki, PirateSwordswoman, Musketeer)):
                    f.update(dt, game_map, particles)
                elif isinstance(f, KyudoArcher):
                    f.update(dt, game_map, particles, projectiles)
                else:
                    f.update(dt, game_map)

        # Atualizar Diretor Cinematográfico (Temporizadores e Corpos Voxel)
        cinematic_director.update(dt, game_map, particles)

        # Processar Combate & Projéteis
        winner = combat_system.process_combat(p1, p2, game_map, particles, banners, camera, projectiles, dt, cinematic_director=cinematic_director, decoys=decoys)
        if winner and round_winner is None:
            round_winner = winner
            ctrl_mgr.rumble_player(0, 0.7, 1.0, 260)
            ctrl_mgr.rumble_player(1, 0.7, 1.0, 260)
            if winner == "P1_WINS":
                score_p1 += 1
            elif winner == "P2_WINS":
                score_p2 += 1

        # Câmera segue o ponto médio
        mid_x = (p1.wx + p2.wx) / 2.0
        mid_y = (p1.wy + p2.wy) / 2.0
        camera.update(mid_x, mid_y, dt)

        particles = [p for p in particles if p.update(dt)]
        banners = [b for b in banners if b.update(dt)]
        for leaf in ambient_leaves:
            leaf.update(dt)

        # -------------------------------------------------------------
        # RENDERIZAÇÃO COM Y-SORTING
        # -------------------------------------------------------------
        bg_col = COLOR_KYOTO_BG if isinstance(game_map, KyotoMap) else COLOR_BG
        screen.fill(bg_col)
        game_map.render_terrain(screen, camera, game_time)

        render_queue = []
        for bamboo in game_map.bamboos:
            render_queue.append((bamboo.wx + bamboo.wy, 'bamboo', bamboo))
        for rock in game_map.rocks:
            render_queue.append((rock.wx + rock.wy, 'rock', rock))
        if game_map.well:
            render_queue.append((game_map.well.wx + game_map.well.wy, 'well', game_map.well))
        for tree in game_map.trees:
            render_queue.append((tree.wx + tree.wy, 'tree', tree))

        # Adicionar elementos de cenário exclusivos (Torii, Lanternas, Construções de Kyoto)
        if hasattr(game_map, 'torii_gates'):
            for tg in game_map.torii_gates:
                render_queue.append((tg.wx + tg.wy, 'torii', tg))
        if hasattr(game_map, 'buildings'):
            for b in game_map.buildings:
                render_queue.append((b.wx + b.wy + b.depth * 0.5, 'building', b))
        if hasattr(game_map, 'lanterns'):
            for l in game_map.lanterns:
                render_queue.append((l.wx + l.wy, 'lantern', l))
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
            round_start_timer -= dt
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

        # -------------------------------------------------------------
        # INTERFACE DE USUÁRIO (HUD)
        # -------------------------------------------------------------
        panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 240, 14, 480, 54)
        pygame.draw.rect(screen, (20, 24, 22, 210), panel_rect, border_radius=8)
        pygame.draw.rect(screen, (60, 75, 68), panel_rect, 2, border_radius=8)

        p1_color = get_fighter_color(p1)
        p2_color = get_fighter_color(p2)

        p1_name = p1.name.split()[0].upper()
        p2_name = p2.name.split()[0].upper()

        p1_title = font_mid.render(f"{p1_name}  {score_p1}", True, p1_color)
        p2_title = font_mid.render(f"{score_p2}  {p2_name}", True, p2_color)
        screen.blit(p1_title, (panel_rect.x + 20, panel_rect.y + 16))
        screen.blit(p2_title, (panel_rect.right - p2_title.get_width() - 20, panel_rect.y + 16))

        mode_text = t("mode_hud_1p") if vs_ai_mode else t("mode_hud_2p")
        mode_surf = font_small.render(mode_text, True, COLOR_GOLD)
        screen.blit(mode_surf, (panel_rect.centerx - mode_surf.get_width() // 2, panel_rect.y + 18))

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
