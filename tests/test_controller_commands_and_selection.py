"""
Testes dedicados para os novos comandos padronizados de controle,
fluxo sequencial de seleção de personagens no modo 1P vs IA,
bloqueio de teclado P2 e ajustes de balanceamento (Tomoe e Teppo).
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_ARCHER, CHAR_RIFLE
)
from src.input.controller_manager import (
    ControllerManager, ControllerDevice,
    CONTROLLER_TYPE_DUALSENSE, CONTROLLER_TYPE_XBOX,
    ACTION_ATTACK, ACTION_DASH, ACTION_CONFIRM, ACTION_CANCEL, ACTION_MENU
)
from src.ui.character_select import CharacterSelectScreen
from src.entities.kyudo_archer import KyudoArcher
from src.entities.rifleman import Rifleman


def test_ps5_controller_mappings():
    class MockDualSenseJoystick:
        def get_instance_id(self): return 10
        def get_name(self): return "DualSense Wireless Controller"
        def get_guid(self): return "030000004c050000e60c000011010000"
        def get_numbuttons(self): return 15
        def get_numaxes(self): return 4
        def get_numhats(self): return 1
        def get_hat(self, idx): return (0, 0)
        def get_axis(self, idx): return 0.0
        def get_button(self, idx): return False

    dev = ControllerDevice(MockDualSenseJoystick())
    assert dev.controller_type == CONTROLLER_TYPE_DUALSENSE

    # Glifos visuais PlayStation
    assert dev.get_button_glyph(ACTION_ATTACK) == "▢"
    assert dev.get_button_glyph(ACTION_DASH) == "✕"
    assert dev.get_button_glyph(ACTION_CONFIRM) == "✕"
    assert dev.get_button_glyph(ACTION_CANCEL) == "○"
    assert dev.get_button_glyph(ACTION_MENU) == "Options"

    # Mapeamentos padrão SDL GameController para DualSense no macOS:
    # Botão 2: ▢ Quadrado (Ação Principal de Ataque)
    assert dev.is_action_pressed(2, ACTION_ATTACK) is True
    # Botão 10: R1 (Ação Principal de Ataque alternativa)
    assert dev.is_action_pressed(10, ACTION_ATTACK) is True
    # Botão 0: ✕ Cruz (Ação Secundária & Confirmação de Menus)
    assert dev.is_action_pressed(0, ACTION_DASH) is True
    assert dev.is_action_pressed(0, ACTION_CONFIRM) is True
    # Botão 1: ○ Círculo (Volta nos Menus)
    assert dev.is_action_pressed(1, ACTION_CANCEL) is True
    # Botão 6: Options (Pausa & Menu)
    assert dev.is_action_pressed(6, ACTION_MENU) is True

    # Garantir que L1 (9) e D-Pad (13) NUNCA acionem Menu ou Restart
    assert dev.is_action_pressed(9, ACTION_MENU) is False
    assert dev.is_action_pressed(13, "restart") is False
    assert dev.is_action_pressed(2, ACTION_CANCEL) is False # Quadrado NÃO é cancelar!

    print("Teste PS5: Mapeamento de botões correto para DualSense (Quadrado=Ataque, Cruz=Dash, Círculo=Volta) OK!")


def test_char_select_sequential_vs_ai_flow():
    screen = CharacterSelectScreen()
    assert screen.vs_ai is True
    assert screen.selection_step == "P1"

    # 1. P1 escolhe o primeiro lutador (Kenshi, idx 0) e confirma com ESPAÇO
    e_space = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE})
    result1 = screen.handle_event(e_space)
    assert result1 is False, "Primeira confirmação apenas trava o P1 e avança para a IA!"
    assert screen.selection_step == "AI", "Deve mudar para a etapa de seleção da IA!"

    # 2. Navegação agora move a escolha da IA (P2/IA) com o mesmo teclado WASD ou controle do P1!
    e_down = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_s})
    screen.handle_event(e_down)
    assert screen.p2_choice_idx == (1 + 6) % 12, "WASD deve mover a IA na etapa 2!"
    assert screen.p1_choice_idx == 0, "A escolha do P1 deve permanecer travada!"

    # 3. Teclado P2 (setas) NÃO deve ter efeito no modo contra IA!
    old_p2_idx = screen.p2_choice_idx
    e_arrow = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT})
    screen.handle_event(e_arrow)
    assert screen.p2_choice_idx == old_p2_idx, "Teclado do Jogador 2 não deve funcionar no modo IA!"

    # 4. Pressionar ESC volta da seleção da IA para o P1
    e_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    res_back = screen.handle_event(e_esc)
    assert res_back is False
    assert screen.selection_step == "P1", "ESC na etapa IA deve retornar para a etapa P1!"

    # 5. Pressionar ESC na etapa P1 retorna 'BACK' para voltar ao título
    res_title = screen.handle_event(e_esc)
    assert res_title == "BACK", "ESC na etapa P1 deve retornar BACK para a tela de título!"

    print("Teste Fluxo IA: Seleção sequencial P1 -> IA e bloqueio de teclado P2 OK!")


def test_char_select_mode_toggle_navigation():
    screen = CharacterSelectScreen()
    assert screen.focus_zone == "GRID"
    screen.p1_choice_idx = 2 # Primeira linha (0 a 5)

    # Navegar para CIMA a partir da primeira linha deve focar no botão de modo
    e_up = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_w})
    screen.handle_event(e_up)
    assert screen.focus_zone == "MODE_BTN", "Navegar para cima na linha 0 deve focar no botão de modo!"

    # Pressionar confirmação com o botão de modo focado alterna o modo
    e_confirm = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
    screen.handle_event(e_confirm)
    assert screen.vs_ai is False, "Confirmar no botão de modo deve alternar para 1P vs 2P!"

    # Pressionar para BAIXO retorna o foco para a grade
    e_down = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_s})
    screen.handle_event(e_down)
    assert screen.focus_zone == "GRID", "Navegar para baixo deve retornar para a grade!"

    print("Teste Navegação de Modo: Foco e alternância via direcional OK!")


def test_tomoe_and_teppo_balance():
    # Teppo inicia municiado
    teppo = Rifleman(5.0, 5.0)
    assert teppo.has_ammo is True, "Teppo deve iniciar municiado!"

    # Tomoe disparo imediato e corda sem cooldown
    tomoe = KyudoArcher(5.0, 5.0)
    assert tomoe.draw_duration == 0.0, "Tomoe não deve ter windup no arco!"
    assert tomoe.rope_cooldown == 0.0, "Tomoe não deve ter cooldown na corda!"

    projs = []
    tomoe.trigger_bow_draw(10.0, 5.0, projs)
    assert len(projs) == 1, "Disparo do arco deve ser instantâneo!"

    tomoe.trigger_rope_arrow(12.0, 5.0, projs)
    assert len(projs) == 2, "Flecha de corda deve ser disparada!"

    print("Teste Balanceamento: Tomoe sem windup/cooldown e Teppo com munição inicial OK!")


def test_murasaki_hanzo_anne_buffs():
    from src.entities.purple_ninja import PurpleNinja
    from src.entities.yellow_ninja import YellowNinja
    from src.entities.pirate import PirateSwordswoman
    from src.entities.red_samurai import RedSamurai
    from src.entities.projectile import MusketBulletProjectile, KunaiProjectile
    from src.combat.collision import CombatSystem
    from src.isometric.camera import Camera
    from src.world.map_data import GameMap

    game_map = GameMap()
    camera = Camera(10.0, 10.0)
    combat = CombatSystem()

    # 1. Teppo: Velocidade da bala calibrada para 18.5
    teppo = Rifleman(5.0, 5.0)
    bullet = MusketBulletProjectile(5.0, 5.0, 0.5, 1.0, 0.0, teppo)
    assert round(math.hypot(bullet.vx, bullet.vy), 1) == 18.5, "Bala do Teppo deve ser 18.5 tiles/s!"

    # 2. Murasaki: Windup 0.04s, alcance 1.15m e giro protetor de corrente
    murasaki = PurpleNinja(10.0, 10.0)
    assert murasaki.windup_time == 0.04, "Windup de Murasaki deve ser 0.04s!"
    murasaki.trigger_kama_strike(11.0, 10.0)
    assert murasaki.hitbox_radius == 1.15, "Alcance da foice de Murasaki deve ser 1.15m!"

    projs = []
    murasaki.state = "IDLE"
    murasaki.trigger_kusarigama_pull(15.0, 10.0, projs)
    assert murasaki.is_spinning_chain is True, "Giro protetor de corrente deve ativar!"
    assert murasaki.chain_spin_timer > 0.0

    # Deflexão de projétil pelo giro de corrente
    kunai_in = KunaiProjectile(10.8, 10.0, 0.5, -1.0, 0.0, teppo)
    projs = [kunai_in]
    dummy_p2 = RedSamurai(18.0, 10.0)
    combat.process_combat(murasaki, dummy_p2, game_map, [], [], camera, projs, 0.016)
    assert kunai_in.is_active is False, "Corrente em giro deve defletir projétil!"

    # 3. Hanzo: Pulo Parabólico e Tanto bloqueado se tiver Kunai
    hanzo = YellowNinja(10.0, 10.0)
    assert hanzo.has_kunai is True
    # Tanto não dispara enquanto tiver a kunai!
    hanzo.trigger_thrust_attack(11.0, 10.0)
    assert hanzo.state == "IDLE", "Tanto deve estar bloqueado enquanto Hanzo tiver a Kunai!"

    # Salto parabólico evasivo
    hanzo.trigger_jump(12.0, 10.0)
    assert hanzo.state == "JUMP", "Ação secundária deve iniciar pulo parabólico!"
    hanzo.update(0.24, game_map)
    assert hanzo.wz > 0.5, "Durante o pulo parabólico Hanzo deve estar alto no ar (wz > 0.5)!"

    # Arremesso de kunai em pleno ar
    projs = []
    hanzo.trigger_midair_throw(15.0, 10.0, projs)
    assert hanzo.has_kunai is False, "Kunai foi arremessada no ar!"
    assert len(projs) == 1

    # Após aterrissar e sem kunai, o ataque da Tanto é liberado!
    hanzo.update(0.30, game_map)
    assert hanzo.state == "IDLE"
    assert hanzo.wz == 0.0
    hanzo.trigger_thrust_attack(11.0, 10.0)
    assert hanzo.state == "ATTACK", "Com Hanzo desarmado/sem kunai, a Tanto é liberada!"

    # Backstab fatal: Hanzo golpeia pelas costas (ambos olhando para a direita)
    enemy = RedSamurai(10.7, 10.0)
    enemy.facing_x = 1.0; enemy.facing_y = 0.0
    hanzo.facing_x = 1.0; hanzo.facing_y = 0.0
    hanzo.hitbox_active = True
    hanzo.hitbox_center = (10.7, 10.0)
    winner = combat.process_combat(hanzo, enemy, game_map, [], [], camera, [], 0.016)
    assert winner == "P1_WINS", "Estocada pelas costas com Tanto deve ser 1-Hit Kill!"
    assert enemy.is_alive is False

    # 4. Anne: Velocidade 4.9, avanço na pólvora e deflexão com alfanje
    anne = PirateSwordswoman(10.0, 10.0)
    assert anne.speed == 4.9, "Velocidade da Anne deve ser 4.9!"
    old_x = anne.wx
    anne.trigger_gunpowder_blind(11.0, 10.0, opponent=enemy)
    assert anne.wx > old_x, "Anne deve avançar para frente ao lançar pólvora!"

    anne.state = "IDLE"
    anne.trigger_cutlass_cleave(11.0, 10.0)
    assert anne.hitbox_active is True
    kunai_anne = KunaiProjectile(10.6, 10.0, 0.5, -1.0, 0.0, dummy_p2)
    projs = [kunai_anne]
    combat.process_combat(anne, dummy_p2, game_map, [], [], camera, projs, 0.016)
    assert kunai_anne.is_active is False, "Arco do alfanje deve defletir projéteis frontais!"

    print("Teste Melhorias Murasaki, Hanzo e Anne OK!")


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))
    test_ps5_controller_mappings()
    test_char_select_sequential_vs_ai_flow()
    test_char_select_mode_toggle_navigation()
    test_tomoe_and_teppo_balance()
    test_murasaki_hanzo_anne_buffs()
    print("\nTODOS OS TESTES ESPECÍFICOS DE CONTROLE E SELEÇÃO PASSARAM COM SUCESSO!\n")
