"""
Suíte de testes automatizados headless cobrindo:
1. Tela de Seleção de Personagens (5 Guerreiros)
2. American Ninja & Doberman (Shuriken com Stun e Dog Dash Fatal)
3. Gray Ninja (Bomba Relógio com delay e explosão fatal em área)
4. Gray Ninja (Bomba de Fumaça instantânea causando Slow para fuga)
5. Kenshin, Musashi e Ninja Hanzo
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.config import CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE, CHAR_SAITOU
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.purple_ninja import PurpleNinja
from src.entities.saitou_samurai import SaitouSamurai
from src.combat.collision import CombatSystem
from src.ui.character_select import CharacterSelectScreen

def test_complete_roster():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))

    # 1. Testar Tela de Seleção com 7 Guerreiros e Grade 2D (UP/DOWN/LEFT/RIGHT)
    select_screen = CharacterSelectScreen()
    assert len(select_screen.characters) == 7
    select_screen.p1_choice_idx = 6  # Hajime Saitou
    p1_id, p2_id, vs_ai = select_screen.get_selected_characters()
    assert p1_id == CHAR_SAITOU

    # Navegação vertical entre linhas da grade 2D
    ev_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    select_screen.handle_event(ev_up)
    assert select_screen.p1_choice_idx == 2  # Saitou (idx 6) -> Hanzo (idx 2)

    ev_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    select_screen.handle_event(ev_down)
    assert select_screen.p1_choice_idx == 6  # Hanzo (idx 2) -> Saitou (idx 6)
    print("Teste 1: Tela de Seleção com 7 guerreiros e navegação 2D em 2 linhas OK!")

    game_map = GameMap()
    camera = Camera(11.0, 11.0)
    combat = CombatSystem()

    particles = []
    banners = []
    projectiles = []

    # 2. Testar Shuriken Stun (Não mata, apenas atordoa)
    joe = AmericanNinja(wx=8.0, wy=11.0)
    target = RedSamurai(wx=11.0, wy=11.0)

    joe.trigger_shuriken(target.wx, target.wy, projectiles)
    assert len(projectiles) == 1
    # Colidir shuriken com o alvo
    projectiles[0].wx = target.wx
    projectiles[0].wy = target.wy
    combat.process_combat(joe, target, game_map, particles, banners, camera, projectiles, 0.016)
    assert target.state == "STUNNED"
    assert target.is_alive == True
    print("Teste 2: Shuriken atordoa (STUN) sem matar OK!")

    # 3. Testar Nocaute do Doberman (Oponente ataca o cão durante a investida)
    joe.dog.charge(target.wx, target.wy)
    assert joe.dog.state == "CHARGE"
    # Oponente ataca com espada
    target.state = "ATTACK"
    target.hitbox_active = True
    target.hitbox_center = (joe.dog.wx, joe.dog.wy)
    target.hitbox_radius = 1.0
    combat.process_combat(joe, target, game_map, particles, banners, camera, projectiles, 0.016)
    assert joe.dog.state == "KNOCKED_OUT"
    assert joe.dog.can_attack() == False
    print("Teste 3: Contra-ataque no Doberman causa nocaute temporário OK!")

    # 4. Testar Morte Fatal pelo Doberman (Cão atinge oponente desprotegido)
    target2 = YellowNinja(wx=12.0, wy=11.0)
    joe.dog.state = "FOLLOW"
    joe.dog.charge(target2.wx, target2.wy)
    joe.dog.wx = target2.wx
    joe.dog.wy = target2.wy
    winner = combat.process_combat(joe, target2, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS"
    assert target2.is_alive == False
    print("Teste 4: Doberman executa abate fatal (1-Hit Kill) OK!")

    # 5. Testar Gray Ninja: Bomba Relógio (Delay fuse + Explosão Fatal em Área)
    projectiles.clear()
    kemuri = GrayNinja(wx=6.0, wy=11.0)
    kenshin = RedSamurai(wx=10.0, wy=11.0)

    kemuri.trigger_throw_bomb(kenshin.wx, kenshin.wy, projectiles)
    assert len(projectiles) == 1
    bomb = projectiles[0]
    assert bomb.fuse_timer == 1.5
    # Simular passagem do tempo até o pavio queimar
    for _ in range(100):
        bomb.update(0.016, game_map)
    assert bomb.fuse_timer <= 0.0
    # Processar combate na explosão
    winner = combat.process_combat(kemuri, kenshin, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS"
    assert kenshin.is_alive == False
    assert bomb.is_active == False
    print("Teste 5: Gray Ninja Bomba Relógio com Delay e Explosão em Área OK!")

    # 6. Testar Gray Ninja: Bomba de Fumaça Instantânea com Efeito Slow
    projectiles.clear()
    kemuri2 = GrayNinja(wx=8.0, wy=11.0)
    musashi = BlueSamurai(wx=8.0, wy=11.0)
    kemuri2.trigger_smoke_bomb(musashi.wx, musashi.wy, projectiles)
    assert len(projectiles) == 1
    smoke = projectiles[0]
    smoke.update(0.016, game_map)
    assert smoke.is_active == True
    combat.process_combat(kemuri2, musashi, game_map, particles, banners, camera, projectiles, 0.016)
    assert musashi.slow_timer > 0.0
    print(f"Teste 6: Bomba de Fumaça ativada com Slow ({musashi.slow_timer:.1f}s) OK!")

    # 7. Testar Ninja Roxo (Murasaki): Puxão de Kusarigama e Liberdade de Ação do Alvo
    projectiles.clear()
    murasaki = PurpleNinja(wx=7.0, wy=11.0)
    rival = RedSamurai(wx=11.0, wy=11.0)
    initial_dist = 4.0

    murasaki.trigger_kusarigama_pull(rival.wx, rival.wy, projectiles)
    assert len(projectiles) == 1
    chain = projectiles[0]
    assert chain.state == "FLYING"

    # Corrente viaja e acerta o rival
    chain.wx = rival.wx
    chain.wy = rival.wy
    combat.process_combat(murasaki, rival, game_map, particles, banners, camera, projectiles, 0.016)
    assert chain.state == "HOOKED_PULLING"
    assert chain.target == rival

    # Atualizar tração: rival deve ser puxado para perto
    chain.update(0.1, game_map, particles)
    new_dist = rival.wx - murasaki.wx
    assert new_dist < initial_dist  # Foi puxado em direção ao Ninja Roxo!

    # Validar que o alvo NÃO está travado nem congelado: pode desferir ataque normalmente!
    assert rival.can_move() or rival.state in ("IDLE", "WALK")
    rival.trigger_iai_attack(murasaki.wx, murasaki.wy)
    assert rival.state == "ATTACK"
    print("Teste 7: Kusarigama puxa o oponente e o oponente pode atacar livremente OK!")

    # 8. Testar Precedência Absoluta: Foice Curta do Ninja Roxo ganha de outros golpes sem CLASH
    murasaki2 = PurpleNinja(wx=10.0, wy=11.0)
    kenshin2 = RedSamurai(wx=10.5, wy=11.0)

    # Ambos atacam no mesmo instante em alcance corpo a corpo
    murasaki2.trigger_kama_strike(kenshin2.wx, kenshin2.wy)
    kenshin2.trigger_iai_attack(murasaki2.wx, murasaki2.wy)

    murasaki2.hitbox_active = True
    murasaki2.hitbox_center = (10.25, 11.0)
    murasaki2.hitbox_radius = 0.70
    murasaki2.is_priority_strike = True

    kenshin2.hitbox_active = True
    kenshin2.hitbox_center = (10.25, 11.0)
    kenshin2.hitbox_radius = 1.0
    kenshin2.is_priority_strike = False

    winner = combat.process_combat(murasaki2, kenshin2, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS"
    assert kenshin2.is_alive == False
    assert murasaki2.is_alive == True
    print("Teste 8: Precedência Absoluta do Ninja Roxo anula golpe adversário e vence OK!")

    # 9. Testar Spawns nas Extremidades da Ponte
    from main import create_fighter
    p1 = create_fighter(CHAR_SAITOU, wx=10.5, wy=7.0)
    p2 = create_fighter(CHAR_KENSHIN, wx=10.5, wy=15.0)
    p1.set_facing(p2.wx, p2.wy)
    p2.set_facing(p1.wx, p1.wy)
    assert p1.wx == 10.5 and p1.wy == 7.0
    assert p2.wx == 10.5 and p2.wy == 15.0
    assert abs(p1.facing_y - 1.0) < 0.01  # Olhando para o Sul (em direção à ponte)
    assert abs(p2.facing_y - (-1.0)) < 0.01 # Olhando para o Norte (em direção à ponte)
    print("Teste 9: Spawns posicionados perfeitamente nas extremidades da ponte OK!")

    # 10. Testar Hajime Saitou: Aceleração contínua do Gatotsu
    saitou = SaitouSamurai(wx=10.5, wy=7.0)
    saitou.trigger_gatotsu(10.5, 15.0)
    assert saitou.state == "GATOTSU_CHARGE"
    assert saitou.charge_speed == 4.8  # Velocidade inicial moderada

    # Atualizar dt e verificar aceleração
    saitou.update(0.1, game_map, particles)
    assert saitou.charge_speed > 4.8  # Ganhou velocidade
    for _ in range(15):
        saitou.update(0.05, game_map, particles)
    assert saitou.charge_speed >= 12.0  # Velocidade extrema acumulada!
    print("Teste 10: Gatotsu acelera continuamente de 4.8 até alta velocidade OK!")

    # 11. Testar Hajime Saitou: Inércia de Frenagem (Braking State)
    saitou_brake = SaitouSamurai(wx=10.5, wy=7.0)
    saitou_brake.trigger_gatotsu(10.5, 15.0)
    saitou_brake.gatotsu_timer = 0.89
    saitou_brake.update(0.02, game_map, particles)
    assert saitou_brake.state == "BRAKING"
    assert saitou_brake.can_move() == False
    assert saitou_brake.state_timer > 0.0
    print("Teste 11: Whiff do Gatotsu entra em frenagem com inércia e punição OK!")

    # 12. Testar Hajime Saitou: Recuo e Stun ao colidir com obstáculo sólido
    target_rock = game_map.rocks[0]
    saitou_wall = SaitouSamurai(wx=target_rock.wx - (target_rock.radius + 0.3), wy=target_rock.wy)
    saitou_wall.trigger_gatotsu(target_rock.wx, target_rock.wy)
    saitou_wall.update(0.05, game_map, particles)
    assert saitou_wall.state == "STUNNED"
    assert saitou_wall.state_timer > 0.0
    print("Teste 12: Colisão com obstáculo sólido causa recuo e Stun no Saitou OK!")

    # 13. Testar Musashi Parry contra Gatotsu de Saitou
    saitou_atk = SaitouSamurai(wx=10.5, wy=10.0)
    musashi_def = BlueSamurai(wx=10.5, wy=11.2)
    musashi_def.trigger_parry()  # Entra em PARRY
    assert musashi_def.state == "PARRY"

    saitou_atk.trigger_gatotsu(musashi_def.wx, musashi_def.wy)
    saitou_atk.hitbox_active = True
    saitou_atk.hitbox_center = (musashi_def.wx, musashi_def.wy)
    saitou_atk.hitbox_radius = 0.8

    winner = combat.process_combat(saitou_atk, musashi_def, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner is None
    assert musashi_def.is_alive == True
    assert saitou_atk.state == "STUNNED"
    print("Teste 13: Parry do Musashi repele e atordoa o Gatotsu de Saitou com sucesso OK!")

    print("SUÍTE COMPLETA PASSOU COM 100% DE SUCESSO!")
    pygame.quit()

if __name__ == "__main__":
    test_complete_roster()
