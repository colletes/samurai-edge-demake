"""
Ponto de entrada principal: Duelo de Samurais Isométrico 2.5D.
Suporte à Seleção de Personagens: Kenshin (Vermelho), Musashi (Azul) e Ninja Hanzo (Amarelo).
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
    CHAR_SAITOU, CHAR_RIFLE, CHAR_KABUKI, CHAR_ARCHER,
    COLOR_GRAY_NINJA, COLOR_PURPLE_NINJA, COLOR_SAITOU_AURA,
    COLOR_RIFLE_AURA, COLOR_KABUKI_AURA, COLOR_ARCHER_AURA
)
from src.isometric.iso_math import input_to_world_direction
from src.isometric.camera import Camera
from src.world.map_data import GameMap
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
from src.entities.ai_controller import SamuraiAI
from src.combat.collision import CombatSystem
from src.effects.particles import AmbientLeafParticle
from src.ui.settings_menu import SettingsMenu, format_key_name
from src.ui.character_select import CharacterSelectScreen

# Estados Globais do Jogo
STATE_CHAR_SELECT = "SELECT"
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
    return COLOR_WHITE

def get_fighter_action_labels(fighter):
    """Retorna os rótulos de comandos (Ataque, Secundário)."""
    if isinstance(fighter, RedSamurai):
        return "Iai Flash", "Shukuchi"
    elif isinstance(fighter, BlueSamurai):
        return "3-Cortes", "Parry"
    elif isinstance(fighter, YellowNinja):
        return "Estocada", "Arremessar Kunai"
    elif isinstance(fighter, AmericanNinja):
        return "Shuriken", "Cão Dash"
    elif isinstance(fighter, GrayNinja):
        return "Bomba Arco", "Bomba Fumaça"
    elif isinstance(fighter, PurpleNinja):
        return "Corte Foice", "Kusarigama Puxão"
    elif isinstance(fighter, SaitouSamurai):
        return "Gatotsu", "Zeroshiki"
    elif isinstance(fighter, Rifleman):
        return "Tiro Mosquete", "Recarga (Hold) / Salto"
    elif isinstance(fighter, Kabuki):
        return "Sopro Veneno", "Esquiva Kabuki"
    elif isinstance(fighter, KyudoArcher):
        return "Puxar Yumi", "Flecha Corda"
    return "Ataque", "Especial"

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

def run_game():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    font_large = pygame.font.Font(None, 48)
    font_mid = pygame.font.Font(None, 26)
    font_small = pygame.font.Font(None, 20)

    # Menus
    controls = dict(DEFAULT_CONTROLS)
    settings_menu = SettingsMenu(controls)
    char_select_screen = CharacterSelectScreen()

    game_state = STATE_CHAR_SELECT

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
    ai = SamuraiAI()

    particles = []
    banners = []
    projectiles = []
    ambient_leaves = []

    round_winner = None
    game_time = 0.0
    round_start_timer = 2.4

    def start_new_match():
        nonlocal p1, p2, game_map, camera, particles, banners, projectiles, ambient_leaves, round_winner, round_start_timer
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
        ambient_leaves = [AmbientLeafParticle(game_map.cols, game_map.rows) for _ in range(45)]
        round_winner = None
        round_start_timer = 2.4

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        # -------------------------------------------------------------
        # TELA DE SELEÇÃO DE PERSONAGENS
        # -------------------------------------------------------------
        if game_state == STATE_CHAR_SELECT:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    start_match = char_select_screen.handle_event(event)
                    if start_match:
                        p1_char_id, p2_char_id, vs_ai_mode = char_select_screen.get_selected_characters()
                        start_new_match()
                        game_state = STATE_DUEL_PLAYING

            char_select_screen.update(dt)
            char_select_screen.render(screen, font_large, font_mid, font_small)
            pygame.display.flip()
            continue

        # -------------------------------------------------------------
        # TELA DE CONFIGURAÇÕES DE CONTROLES (OVERLAY)
        # -------------------------------------------------------------
        if settings_menu.is_open:
            for event in pygame.event.get():
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Voltar para a tela de seleção de personagens
                    game_state = STATE_CHAR_SELECT
                elif event.key == KEY_SETTINGS:
                    settings_menu.open()
                elif event.key == KEY_RESTART:
                    start_new_match()
                elif event.key == KEY_TOGGLE_AI:
                    vs_ai_mode = not vs_ai_mode

                # Comandos Jogador 1
                if p1.is_alive and round_winner is None:
                    if event.key == controls["P1_ATTACK"]:
                        if isinstance(p1, RedSamurai):
                            p1.trigger_iai_attack(p2.wx, p2.wy)
                        elif isinstance(p1, BlueSamurai):
                            p1.trigger_combo_attack(p2.wx, p2.wy)
                        elif isinstance(p1, YellowNinja):
                            p1.trigger_thrust_attack(p2.wx, p2.wy)
                        elif isinstance(p1, AmericanNinja):
                            p1.trigger_shuriken(p2.wx, p2.wy, projectiles)
                        elif isinstance(p1, GrayNinja):
                            p1.trigger_throw_bomb(p2.wx, p2.wy, projectiles)
                        elif isinstance(p1, PurpleNinja):
                            p1.trigger_kama_strike(p2.wx, p2.wy)
                        elif isinstance(p1, SaitouSamurai):
                            p1.trigger_gatotsu_thrust(p2.wx, p2.wy)
                        elif isinstance(p1, Rifleman):
                            p1.trigger_shoot(p2.wx, p2.wy, projectiles, particles)
                        elif isinstance(p1, Kabuki):
                            p1.trigger_poison_spit(p2.wx, p2.wy, projectiles, particles)
                        elif isinstance(p1, KyudoArcher):
                            p1.trigger_bow_draw(p2.wx, p2.wy, projectiles)

                    elif event.key == controls["P1_DASH"]:
                        if isinstance(p1, RedSamurai):
                            keys = pygame.key.get_pressed()
                            dx = (keys[controls["P1_RIGHT"]] - keys[controls["P1_LEFT"]])
                            dy = (keys[controls["P1_DOWN"]] - keys[controls["P1_UP"]])
                            dwx, dwy = input_to_world_direction(dx, dy)
                            p1.trigger_dash(dwx, dwy)
                        elif isinstance(p1, BlueSamurai):
                            p1.set_facing(p2.wx, p2.wy)
                            p1.trigger_parry()
                        elif isinstance(p1, YellowNinja):
                            p1.trigger_throw_attack(p2.wx, p2.wy, projectiles)
                        elif isinstance(p1, AmericanNinja):
                            p1.trigger_dog_attack(p2.wx, p2.wy)
                        elif isinstance(p1, GrayNinja):
                            p1.trigger_smoke_bomb(p2.wx, p2.wy, projectiles)
                        elif isinstance(p1, PurpleNinja):
                            p1.trigger_kusarigama_pull(p2.wx, p2.wy, projectiles)
                        elif isinstance(p1, SaitouSamurai):
                            p1.trigger_zeroshiki(p2.wx, p2.wy)
                        elif isinstance(p1, Rifleman):
                            p1.trigger_evasive_backstep(particles)
                        elif isinstance(p1, Kabuki):
                            keys = pygame.key.get_pressed()
                            dx = (keys[controls["P1_RIGHT"]] - keys[controls["P1_LEFT"]])
                            dy = (keys[controls["P1_DOWN"]] - keys[controls["P1_UP"]])
                            dwx, dwy = input_to_world_direction(dx, dy)
                            p1.trigger_acrobatic_dodge(dwx, dwy, particles)
                        elif isinstance(p1, KyudoArcher):
                            p1.trigger_rope_arrow(p2.wx, p2.wy, projectiles, particles)

                # Comandos Jogador 2 (se não for IA)
                if not vs_ai_mode and p2.is_alive and round_winner is None:
                    if event.key == controls["P2_ATTACK"]:
                        if isinstance(p2, RedSamurai):
                            p2.trigger_iai_attack(p1.wx, p1.wy)
                        elif isinstance(p2, BlueSamurai):
                            p2.trigger_combo_attack(p1.wx, p1.wy)
                        elif isinstance(p2, YellowNinja):
                            p2.trigger_thrust_attack(p1.wx, p1.wy)
                        elif isinstance(p2, AmericanNinja):
                            p2.trigger_shuriken(p1.wx, p1.wy, projectiles)
                        elif isinstance(p2, GrayNinja):
                            p2.trigger_throw_bomb(p1.wx, p1.wy, projectiles)
                        elif isinstance(p2, PurpleNinja):
                            p2.trigger_kama_strike(p1.wx, p1.wy)
                        elif isinstance(p2, SaitouSamurai):
                            p2.trigger_gatotsu_thrust(p1.wx, p1.wy)
                        elif isinstance(p2, Rifleman):
                            p2.trigger_shoot(p1.wx, p1.wy, projectiles, particles)
                        elif isinstance(p2, Kabuki):
                            p2.trigger_poison_spit(p1.wx, p1.wy, projectiles, particles)
                        elif isinstance(p2, KyudoArcher):
                            p2.trigger_bow_draw(p1.wx, p1.wy, projectiles)

                    elif event.key == controls["P2_PARRY"]:
                        if isinstance(p2, RedSamurai):
                            keys = pygame.key.get_pressed()
                            dx = (keys[controls["P2_RIGHT"]] - keys[controls["P2_LEFT"]])
                            dy = (keys[controls["P2_DOWN"]] - keys[controls["P2_UP"]])
                            dwx, dwy = input_to_world_direction(dx, dy)
                            p2.trigger_dash(dwx, dwy)
                        elif isinstance(p2, BlueSamurai):
                            p2.set_facing(p1.wx, p1.wy)
                            p2.trigger_parry()
                        elif isinstance(p2, YellowNinja):
                            p2.trigger_throw_attack(p1.wx, p1.wy, projectiles)
                        elif isinstance(p2, AmericanNinja):
                            p2.trigger_dog_attack(p1.wx, p1.wy)
                        elif isinstance(p2, GrayNinja):
                            p2.trigger_smoke_bomb(p1.wx, p1.wy, projectiles)
                        elif isinstance(p2, PurpleNinja):
                            p2.trigger_kusarigama_pull(p1.wx, p1.wy, projectiles)
                        elif isinstance(p2, SaitouSamurai):
                            p2.trigger_zeroshiki(p1.wx, p1.wy)
                        elif isinstance(p2, Rifleman):
                            p2.trigger_evasive_backstep(particles)
                        elif isinstance(p2, Kabuki):
                            keys = pygame.key.get_pressed()
                            dx = (keys[controls["P2_RIGHT"]] - keys[controls["P2_LEFT"]])
                            dy = (keys[controls["P2_DOWN"]] - keys[controls["P2_UP"]])
                            dwx, dwy = input_to_world_direction(dx, dy)
                            p2.trigger_acrobatic_dodge(dwx, dwy, particles)
                        elif isinstance(p2, KyudoArcher):
                            p2.trigger_rope_arrow(p1.wx, p1.wy, projectiles, particles)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                settings_btn_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 44, 180, 28)
                if settings_btn_rect.collidepoint(mx, my):
                    settings_menu.open()
                select_btn_rect = pygame.Rect(25, 20, 160, 32)
                if select_btn_rect.collidepoint(mx, my):
                    game_state = STATE_CHAR_SELECT

        # Hitstop congelado
        if combat_system.hitstop_timer > 0:
            combat_system.hitstop_timer -= dt
            pygame.display.flip()
            continue

        game_time += dt
        keys = pygame.key.get_pressed()

        # Suporte ao carregamento contínuo de pólvora do Rifleman (segurando botão de ação secundária)
        if isinstance(p1, Rifleman) and p1.is_alive and round_winner is None:
            if keys[controls["P1_DASH"]]:
                p1.trigger_reload_hold()
            else:
                p1.is_reloading = False

        if not vs_ai_mode and isinstance(p2, Rifleman) and p2.is_alive and round_winner is None:
            if keys[controls["P2_PARRY"]]:
                p2.trigger_reload_hold()
            else:
                p2.is_reloading = False

        # Movimento Jogador 1
        p1_dx = (keys[controls["P1_RIGHT"]] - keys[controls["P1_LEFT"]])
        p1_dy = (keys[controls["P1_DOWN"]] - keys[controls["P1_UP"]])
        p1_dwx, p1_dwy = input_to_world_direction(p1_dx, p1_dy)
        if hasattr(p1, "apply_gatotsu_steering") and p1.state == "GATOTSU_CHARGE":
            p1.apply_gatotsu_steering(p1_dwx, p1_dwy, dt)
        else:
            p1.apply_movement(p1_dwx, p1_dwy, dt, game_map)

        # Movimento Jogador 2 (IA ou Humano)
        if vs_ai_mode:
            ai.update(p2, p1, dt, game_map, projectiles)
        else:
            p2_dx = (keys[controls["P2_RIGHT"]] - keys[controls["P2_LEFT"]])
            p2_dy = (keys[controls["P2_DOWN"]] - keys[controls["P2_UP"]])
            p2_dwx, p2_dwy = input_to_world_direction(p2_dx, p2_dy)
            if hasattr(p2, "apply_gatotsu_steering") and p2.state == "GATOTSU_CHARGE":
                p2.apply_gatotsu_steering(p2_dwx, p2_dwy, dt)
            else:
                p2.apply_movement(p2_dwx, p2_dwy, dt, game_map)

        # Atualizações dos combatentes
        for f in (p1, p2):
            if isinstance(f, SaitouSamurai):
                f.update(dt, game_map, particles)
            elif isinstance(f, (Rifleman, Kabuki)):
                f.update(dt, game_map, particles)
            elif isinstance(f, KyudoArcher):
                f.update(dt, game_map, particles, projectiles)
            else:
                f.update(dt, game_map)

        # Processar Combate & Projéteis
        winner = combat_system.process_combat(p1, p2, game_map, particles, banners, camera, projectiles, dt)
        if winner and round_winner is None:
            round_winner = winner
            if winner == "P1_WINS":
                score_p1 += 1
            else:
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
        screen.fill(COLOR_BG)
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

        render_queue.append((p1.wx + p1.wy, 'fighter', p1))
        render_queue.append((p2.wx + p2.wy, 'fighter', p2))

        # Adicionar cão Doberman ao Y-sorting se houver American Ninja na partida
        if hasattr(p1, "dog") and p1.dog:
            render_queue.append((p1.dog.wx + p1.dog.wy, 'dog', p1.dog))
        if hasattr(p2, "dog") and p2.dog:
            render_queue.append((p2.dog.wx + p2.dog.wy, 'dog', p2.dog))

        for proj in projectiles:
            render_queue.append((proj.wx + proj.wy, 'projectile', proj))

        for p in particles:
            if hasattr(p, 'wx') and hasattr(p, 'wy'):
                render_queue.append((p.wx + p.wy, 'particle', p))

        render_queue.sort(key=lambda item: item[0])

        for _, item_type, obj in render_queue:
            if item_type == 'bamboo':
                obj.render(screen, camera, game_time)
            elif item_type in ('rock', 'well', 'tree'):
                obj.render(screen, camera)
            elif item_type == 'fighter':
                obj.render(screen, camera)
            elif item_type == 'dog':
                obj.render(screen, camera)
            elif item_type == 'projectile':
                obj.render(screen, camera)
            elif item_type == 'particle':
                obj.render(screen, camera)

        for leaf in ambient_leaves:
            leaf.render(screen, camera)

        for banner in banners:
            banner.render(screen, camera, font_mid)

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

        mode_text = "[1P vs IA]" if vs_ai_mode else "[2 JOGADORES]"
        mode_surf = font_small.render(mode_text, True, COLOR_GOLD)
        screen.blit(mode_surf, (panel_rect.centerx - mode_surf.get_width() // 2, panel_rect.y + 18))

        # Botão Trocar Personagens no topo esquerdo
        select_btn = pygame.Rect(25, 20, 180, 32)
        pygame.draw.rect(screen, (26, 34, 30, 210), select_btn, border_radius=6)
        pygame.draw.rect(screen, COLOR_GOLD, select_btn, 1, border_radius=6)
        sel_txt = font_small.render("<< MUDAR GUERREIROS", True, COLOR_GOLD)
        screen.blit(sel_txt, (select_btn.centerx - sel_txt.get_width() // 2, select_btn.y + 7))

        # Guia de Controles no Rodapé
        footer_rect = pygame.Rect(20, SCREEN_HEIGHT - 48, SCREEN_WIDTH - 40, 36)
        pygame.draw.rect(screen, (16, 20, 18, 200), footer_rect, border_radius=6)

        k_atk = format_key_name(controls["P1_ATTACK"])
        k_sec = format_key_name(controls["P1_DASH"])
        m_atk = format_key_name(controls["P2_ATTACK"])
        m_sec = format_key_name(controls["P2_PARRY"])

        p1_a1, p1_a2 = get_fighter_action_labels(p1)
        p2_a1, p2_a2 = get_fighter_action_labels(p2)

        c1 = font_small.render(f"P1 ({p1_name}): W/A/S/D | {k_atk} = {p1_a1} | {k_sec} = {p1_a2}", True, (245, 205, 205))
        c2 = font_small.render(f"P2 ({p2_name}): Setas | {m_atk} = {p2_a1} | {m_sec} = {p2_a2}", True, (205, 225, 245))

        screen.blit(c1, (30, SCREEN_HEIGHT - 40))
        screen.blit(c2, (SCREEN_WIDTH // 2 - c2.get_width() // 2 - 30, SCREEN_HEIGHT - 40))

        settings_btn_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 44, 180, 28)
        pygame.draw.rect(screen, (40, 52, 45), settings_btn_rect, border_radius=4)
        pygame.draw.rect(screen, COLOR_GOLD, settings_btn_rect, 1, border_radius=4)
        c3 = font_small.render("[C] Controles / Settings", True, COLOR_GOLD)
        screen.blit(c3, (settings_btn_rect.centerx - c3.get_width() // 2, settings_btn_rect.y + 5))

        # Banner de Vitória
        if round_winner:
            w_fighter = p1 if round_winner == "P1_WINS" else p2
            w_msg = f"VITÓRIA DE {w_fighter.name.upper()}!"
            w_color = get_fighter_color(w_fighter)
            v_surf = font_large.render(w_msg, True, w_color)
            sub_surf = font_mid.render("Pressione ESPAÇO para o próximo duelo ou ESC para trocar lutadores", True, COLOR_WHITE)

            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2 - 40
            screen.blit(v_surf, (center_x - v_surf.get_width() // 2, center_y))
            screen.blit(sub_surf, (center_x - sub_surf.get_width() // 2, center_y + 48))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
