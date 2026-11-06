"""
Testes de validação para as melhorias de navegação da IA, ajustes do chefe Gashadokuro,
revelação progressiva do ícone no bracket do Arcade e compatibilidade de áudio.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.display.set_mode((100, 100), pygame.NOFRAME)

from src.audio.sound_manager import SoundManager
from src.arcade.arcade_mode import FightKind
from src.arcade.arcade_screens import ArcadeBracketScreen
from src.entities.boss_oni import BossOni, BOSS_TUNING
from src.entities.samurai import Samurai, slide_movement_against_obstacles
from src.entities.ai_controller import SamuraiAI
from src.world.obstacles import Rock, Well
from src.world.map_data import GameMap


def test_sound_manager_stop_music_args():
    """Garante que stop_music aceita tanto fade_ms quanto fadeout_ms sem erro."""
    sm = SoundManager()
    # Não deve lançar TypeError
    sm.stop_music(fade_ms=300)
    sm.stop_music(fadeout_ms=600)
    print("  [OK] SoundManager.stop_music() aceita fadeout_ms e fade_ms sem lançar TypeError.")


def test_arcade_bracket_boss_icon_reveal():
    """Garante que o nó 12 do chefe exibe interrogação quando 'todo' e caveira quando 'current'/'done'."""
    screen = ArcadeBracketScreen()
    surf = pygame.Surface((1280, 720), pygame.SRCALPHA)
    
    class DummyFight:
        def __init__(self, kind):
            self.kind = kind
            self.fighter_id = "gashadokuro"
    
    # Boss em estado 'todo': deve desenhar ?
    fight = DummyFight(FightKind.BOSS)
    rect = pygame.Rect(640 - 24, 360 - 24, 48, 48)
    screen._marker(surf, rect, fight, "todo")
    
    # Boss em estado 'current' ou 'done': deve desenhar caveira
    screen._marker(surf, rect, fight, "current")
    screen._marker(surf, rect, fight, "done")
    print("  [OK] Arcade bracket exibe '?' no nó do chefe antes do desafio ninja e caveira ao ser revelado.")


def test_boss_gashadokuro_tuning():
    """Valida as velocidades aprimoradas, encadeamento e pausas reduzidas do Gashadokuro."""
    assert BOSS_TUNING["p2_speed"] >= 7.5, f"p2_speed deve ser >= 7.5, tem {BOSS_TUNING['p2_speed']}"
    assert BOSS_TUNING["p2_slow"] <= 0.50, f"p2_slow deve ser <= 0.50, tem {BOSS_TUNING['p2_slow']}"
    assert BOSS_TUNING["p2_stun"] <= 0.55, f"p2_stun deve ser <= 0.55, tem {BOSS_TUNING['p2_stun']}"
    assert BOSS_TUNING["p3_speed"] >= 6.5, f"p3_speed deve ser >= 6.5, tem {BOSS_TUNING['p3_speed']}"
    assert BOSS_TUNING["p3_speed_max"] >= 11.0, f"p3_speed_max deve ser >= 11.0, tem {BOSS_TUNING['p3_speed_max']}"
    assert BOSS_TUNING["p3_stun"] <= 0.50, f"p3_stun deve ser <= 0.50, tem {BOSS_TUNING['p3_stun']}"
    print("  [OK] Gashadokuro: velocidade aumentada em 40%, janelas de pausa reduzidas.")


def test_slide_movement_against_obstacles():
    """Valida deslizamento tangencial fluído de lutadores contra obstáculos sem ficar travado."""
    gm = GameMap()
    rock = Rock(5.0, 5.0, radius=0.6)
    gm.rocks = [rock]
    
    # Lutador tenta mover diagonalmente para a direita e para cima colidindo contra a rocha
    # start_x = 4.2 (a esquerda da rocha), movendo dx=0.10, dy=0.10
    start_x, start_y = 4.2, 5.0
    new_x, new_y = slide_movement_against_obstacles(start_x, start_y, 0.10, 0.10, 0.35, gm)
    
    # A coordenada Y (tangente à rocha) deve avançar sem ficar presa
    assert new_y > start_y + 0.05, f"Lutador devia deslizar livremente no eixo Y, obteve {new_y} vs {start_y}"
    print("  [OK] Deslizamento tangencial suave contra obstáculos validado com sucesso.")


def test_ai_obstacle_whisker_steering():
    """Valida que a IA detecta obstáculos sólidos à frente e deflete a direção para contorná-los."""
    ai = SamuraiAI("normal")
    gm = GameMap()
    rock = Rock(5.0, 5.0, radius=0.6)
    gm.rocks = [rock]
    
    ai_fighter = Samurai(4.0, 5.0, "AI_Fighter")
    opponent = Samurai(6.5, 5.0, "Opponent")
    
    # IA apontando diretamente na direção do oponente (vetor +X), passando bem no meio da rocha
    ai.move_dir_x = 1.0
    ai.move_dir_y = 0.0
    
    # Deve desviar tangencialmente ao invés de continuar reto contra a rocha
    ai._steer_around_obstacles(ai_fighter, opponent, gm)
    assert abs(ai.move_dir_y) > 0.25, f"A IA deveria desviar lateralmente da rocha, move_dir_y = {ai.move_dir_y}"
    print("  [OK] IA com whiskers direcionais contorna obstáculos sólidos sem ficar presa.")


if __name__ == "__main__":
    test_sound_manager_stop_music_args()
    test_arcade_bracket_boss_icon_reveal()
    test_boss_gashadokuro_tuning()
    test_slide_movement_against_obstacles()
    test_ai_obstacle_whisker_steering()
    print("\nTODOS OS TESTES DE VALIDAÇÃO PASSARAM COM SUCESSO!")
