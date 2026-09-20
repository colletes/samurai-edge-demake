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
from src.config import CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE
from src.isometric.camera import Camera
from src.world.map_data import GameMap
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.american_ninja import AmericanNinja
from src.entities.gray_ninja import GrayNinja
from src.entities.purple_ninja import PurpleNinja
from src.combat.collision import CombatSystem
from src.ui.character_select import CharacterSelectScreen

def test_complete_roster():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))

    # 1. Testar Tela de Seleção com 6 Guerreiros
    select_screen = CharacterSelectScreen()
    assert len(select_screen.characters) == 6
    select_screen.p1_choice_idx = 5  # Murasaki (Purple Ninja)
    p1_id, p2_id, vs_ai = select_screen.get_selected_characters()
    assert p1_id == CHAR_PURPLE
    print("Teste 1: Tela de Seleção com 6 guerreiros OK!")

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

    print("SUÍTE COMPLETA PASSOU COM 100% DE SUCESSO!")
    pygame.quit()

if __name__ == "__main__":
    test_complete_roster()
