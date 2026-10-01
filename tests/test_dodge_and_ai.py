"""
Testes unitários e de integração para o Sistema de Esquiva Rebalanceada e IA Humanizada (Fase 4 - Prioridade).
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_PIRATE, CHAR_KABUKI, CHAR_ARCHER,
    CHAR_SAITOU, CHAR_RIFLE, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE, CHAR_MUSKETEER
)
from src.entities.samurai import Samurai
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.kabuki import Kabuki
from src.entities.pirate import PirateSwordswoman
from src.entities.ai_controller import SamuraiAI, DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD
from src.world.map_data import GameMap
from src.world.kyoto_map import KyotoMap, RunawayCarriage
from src.ui.settings_menu import SettingsMenu
from src.ui.character_select import CharacterSelectScreen
from src.input.controls_storage import load_controls_config, save_controls_config

def test_agile_vs_heavy_dodge_properties():
    """Verifica que combatentes ágeis e pesados têm as velocidades e recuperações corretas."""
    # Ágeis
    kenshi = RedSamurai(5.0, 5.0)
    okuni = Kabuki(5.0, 5.0)
    
    assert kenshi.is_agile_dodge is True
    assert kenshi.roll_speed == 10.5
    assert kenshi.roll_recovery_duration == 0.12
    assert kenshi.roll_cooldown_duration == 0.35

    assert okuni.is_agile_dodge is True
    assert okuni.roll_speed == 10.5
    assert okuni.roll_recovery_duration == 0.12
    assert okuni.roll_cooldown_duration == 0.35

    # Pesados
    musashi = BlueSamurai(5.0, 5.0)
    anne = PirateSwordswoman(5.0, 5.0)

    assert musashi.is_agile_dodge is False
    assert musashi.roll_speed == 8.5
    assert musashi.roll_recovery_duration == 0.18
    assert musashi.roll_cooldown_duration == 0.38

    assert anne.is_agile_dodge is False
    assert anne.roll_speed == 8.5
    assert anne.roll_recovery_duration == 0.18
    assert anne.roll_cooldown_duration == 0.38

def test_dodge_recovery_stun_and_immobility():
    """Testa que durante a recuperação pós-esquiva o combatente fica vulnerável e não pode se mover nem agir."""
    game_map = GameMap()
    musashi = BlueSamurai(5.0, 5.0)
    musashi.trigger_roll(1.0, 0.0)
    assert musashi.state == "ROLL"

    # Atualizar até o fim do roll para entrar em recovery
    musashi.update(0.21, game_map)
    assert musashi.state == "IDLE"
    assert musashi.roll_recovery_timer > 0.0
    assert musashi.can_move() is False
    assert musashi.can_act() is False

    # Tentar se mover durante a recuperação (deve ser bloqueado por can_move)
    pos_before_x = musashi.wx
    musashi.apply_movement(1.0, 0.0, 0.05, game_map)
    assert musashi.wx == pos_before_x  # Posição inalterada durante a recuperação (stun)

    # Deixar a recuperação expirar mas ainda em cooldown
    musashi.update(0.20, game_map)
    assert musashi.roll_recovery_timer == 0.0
    assert musashi.roll_cooldown_timer > 0.0
    assert musashi.can_move() is True
    # Não pode dar esquiva novamente enquanto estiver em cooldown
    assert musashi.can_act() is True
    musashi.trigger_roll(1.0, 0.0)
    assert musashi.state != "ROLL"

def test_dodge_spam_prevention():
    """Verifica que spam de esquiva não é mais possível (rejeita novo roll durante cooldown)."""
    game_map = GameMap()
    okuni = Kabuki(5.0, 5.0)
    okuni.trigger_kabuki_roll(1.0, 0.0)
    assert okuni.state == "KABUKI_ROLL"

    okuni.update(0.23, game_map)  # Termina o roll
    assert okuni.roll_recovery_timer > 0.0

    # Tentar novo roll durante recovery -> Rejeitado
    okuni.trigger_kabuki_roll(1.0, 0.0)
    assert okuni.state != "KABUKI_ROLL"

    # Avança além da recovery para o cooldown
    okuni.update(0.13, game_map)
    assert okuni.roll_recovery_timer == 0.0
    assert okuni.roll_cooldown_timer > 0.0

    # Tentar novo roll durante cooldown -> Rejeitado
    okuni.trigger_kabuki_roll(1.0, 0.0)
    assert okuni.state != "KABUKI_ROLL"

    # Avança além do cooldown -> Agora pode esquivar!
    okuni.update(0.36, game_map)
    assert okuni.roll_cooldown_timer == 0.0
    okuni.trigger_kabuki_roll(1.0, 0.0)
    assert okuni.state == "KABUKI_ROLL"

def test_anne_cannon_cooldown_at_round_start():
    """Verifica que Anne Bonny inicia a rodada com 4.5s de cooldown de canhão, evitando nuke instantâneo."""
    game_map = GameMap()
    anne = PirateSwordswoman(5.0, 5.0)
    assert anne.cannon_cooldown_timer == 4.5

    # Tentar disparar canhão no início da rodada -> Falha
    anne.start_cannon_strike(10.0, 10.0)
    assert anne.is_aiming_cannon is False

    # Após 4.5s
    anne.update(4.6, game_map)
    assert anne.cannon_cooldown_timer == 0.0
    anne.start_cannon_strike(10.0, 10.0)
    assert anne.is_aiming_cannon is True

def test_ai_difficulty_and_humanized_parry():
    """Testa parâmetros de dificuldade da IA e que o Musashi IA não dá parry instantâneo."""
    game_map = GameMap()
    ai = SamuraiAI(difficulty=DIFFICULTY_NORMAL)
    assert ai.difficulty == DIFFICULTY_NORMAL
    assert ai._get_parry_chance() == 0.55
    
    ai.set_difficulty(DIFFICULTY_HARD)
    assert ai._get_parry_chance() == 0.85
    
    ai.set_difficulty(DIFFICULTY_EASY)
    assert ai._get_parry_chance() == 0.30

    # Delay de reação humano
    ai.set_difficulty(DIFFICULTY_NORMAL)
    musashi_ai = BlueSamurai(5.0, 5.0)
    player = RedSamurai(5.8, 5.0)
    player.trigger_iai_attack(5.0, 5.0)

    # Frame 0 do ataque do jogador: Musashi IA deve agendar defesa com tempo de reação, NÃO parry imediato
    ai.update(musashi_ai, player, 0.016, game_map, [])
    assert musashi_ai.state != "PARRY"
    assert ai.pending_defense_timer > 0.0

def test_ai_evades_kyoto_carriage():
    """Verifica que a IA detecta carruagens em aproximação e realiza esquiva perpendicular."""
    kyoto = KyotoMap()
    ai = SamuraiAI(difficulty=DIFFICULTY_HARD)
    ai_fighter = BlueSamurai(6.0, 7.0)
    player = RedSamurai(18.0, 7.0)

    # Cria uma carruagem vindo na direção da IA
    carriage = RunawayCarriage((4.0, 7.0), (20.0, 7.0))
    carriage.warning_timer = 0.0
    carriage.is_active = True
    kyoto.carriages = [carriage]

    # Atualizar IA: deve esquivar perpendicularmente (subir ou descer em Y)
    ai.update(ai_fighter, player, 0.02, kyoto, [])
    assert ai_fighter.state == "ROLL"
    # Direção de esquiva deve ser perpendicular (em Y, não em X)
    assert abs(ai_fighter.facing_y) > 0.5
    assert abs(ai_fighter.facing_x) < 0.1

def test_difficulty_ui_cycling():
    """Testa alternância de dificuldade nas telas de UI."""
    # Settings menu
    menu = SettingsMenu({}, ai_difficulty="normal")
    assert menu.ai_difficulty == "normal"
    menu.cycle_ai_difficulty()
    assert menu.ai_difficulty == "hard"
    menu.cycle_ai_difficulty()
    assert menu.ai_difficulty == "easy"
    menu.cycle_ai_difficulty()
    assert menu.ai_difficulty == "normal"

    # Character select screen
    select = CharacterSelectScreen(ai_difficulty="normal")
    assert select.ai_difficulty == "normal"
    select.cycle_ai_difficulty()
    assert select.ai_difficulty == "hard"
    select.cycle_ai_difficulty()
    assert select.ai_difficulty == "easy"
    select.cycle_ai_difficulty()
    assert select.ai_difficulty == "normal"


if __name__ == "__main__":
    pygame.init()
    test_agile_vs_heavy_dodge_properties()
    print("✓ test_agile_vs_heavy_dodge_properties passed!")
    test_dodge_recovery_stun_and_immobility()
    print("✓ test_dodge_recovery_stun_and_immobility passed!")
    test_dodge_spam_prevention()
    print("✓ test_dodge_spam_prevention passed!")
    test_anne_cannon_cooldown_at_round_start()
    print("✓ test_anne_cannon_cooldown_at_round_start passed!")
    test_ai_difficulty_and_humanized_parry()
    print("✓ test_ai_difficulty_and_humanized_parry passed!")
    test_ai_evades_kyoto_carriage()
    print("✓ test_ai_evades_kyoto_carriage passed!")
    test_difficulty_ui_cycling()
    print("✓ test_difficulty_ui_cycling passed!")
    print("\nALL DODGE & AI HUMANIZATION TESTS PASSED SUCCESSFULLY!")
