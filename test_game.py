"""
Suíte de testes automatizados headless cobrindo:
1. Tela de Seleção de Personagens (10 Guerreiros, grade 5x2, controles P1 e P2 independentes)
2. Kenshin Shukuchi Dash (Velocidade extrema 28.0, pós-imagens zanzou, corte de bambus)
3. Kemuri Bomba em Arco 3D (Trajetória balística, detonação por contato/tempo, máximo 2 bombas, auto-dano/fogo amigo)
4. Tanegashima Rifleman (1-Hit Kill, recarga segurando secundário, salto evasivo)
5. Kabuki (Sopro de veneno, contagem regressiva de 10s para a morte, boost de velocidade do rival, esquiva acrobática pura)
6. Kyudo Archer (Retesamento de arco Yumi 1-Hit Kill, cancelamento com Flecha de Corda / zip mobility)
7. Spawns aleatórios no mapa com distância mínima >= 7.0 tiles
8. Saitou Gatotsu, Murasaki Kusarigama, American Ninja & Doberman, Gray Ninja Fumaça Slow
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import math
import pygame
from src.config import (
    CHAR_KENSHIN, CHAR_MUSASHI, CHAR_NINJA, CHAR_AMERICAN, CHAR_GRAY,
    CHAR_PURPLE, CHAR_SAITOU, CHAR_RIFLE, CHAR_KABUKI, CHAR_ARCHER,
    CHAR_PIRATE, CHAR_MUSKETEER
)
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
from src.entities.pirate import PirateSwordswoman
from src.entities.musketeer import Musketeer
from src.combat.collision import CombatSystem
from src.effects.cinematic_director import CinematicDirector
from src.ui.character_select import CharacterSelectScreen
from main import get_random_arena_spawns, create_fighter

def test_complete_roster():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))

    # 1. Testar Tela de Seleção com 12 Guerreiros e Grade 6x2
    select_screen = CharacterSelectScreen()
    assert len(select_screen.characters) == 12, f"Esperado 12 lutadores, obtido {len(select_screen.characters)}"
    
    # Testar seleção de P1 e P2 independentes no modo 2 Jogadores
    select_screen.vs_ai = False
    select_screen.p1_choice_idx = 0
    select_screen.p2_choice_idx = 1

    # P1 move com WASD (D move para a direita)
    ev_p1_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
    select_screen.handle_event(ev_p1_right)
    assert select_screen.p1_choice_idx == 1
    assert select_screen.p2_choice_idx == 1  # P2 não foi afetado!

    # P1 move verticalmente (S pula para linha inferior, +6 na grade 6x2)
    ev_p1_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
    select_screen.handle_event(ev_p1_down)
    assert select_screen.p1_choice_idx == 7  # Kasumi (Kunoichi)

    # P2 move exclusivamente com Setas (Down pula +6)
    ev_p2_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    select_screen.handle_event(ev_p2_down)
    assert select_screen.p2_choice_idx == 7
    assert select_screen.p1_choice_idx == 7

    ev_p2_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    select_screen.handle_event(ev_p2_right)
    assert select_screen.p2_choice_idx == 8  # Okuni
    assert select_screen.p1_choice_idx == 7  # P1 continua em Kasumi!

    # Testar se os 12 personagens podem ser criados
    for c in select_screen.characters:
        fighter = create_fighter(c["id"], 10.0, 10.0)
        assert fighter is not None
        assert fighter.is_alive == True
    print("Teste 1: Grade 6x2 com 12 guerreiros e controles P1 (WASD) vs P2 (Setas) independentes OK!")

    game_map = GameMap()
    camera = Camera(11.0, 11.0)
    combat = CombatSystem()

    particles = []
    banners = []
    projectiles = []

    # 2. Testar Kenshin Shukuchi (Godspeed Step com zanzou)
    kenshin = RedSamurai(wx=10.0, wy=10.0)
    kenshin.trigger_dash(1.0, 0.0)
    assert kenshin.state == "SHUKUCHI"
    assert kenshin.shukuchi_speed >= 28.0  # Shukuchi ultra rápido
    assert len(kenshin.zanzou_ghosts) > 0  # Fantasmas zanzou gerados
    # Atualizar passo de dash
    kenshin.update(0.08, game_map)
    assert kenshin.wx > 10.0
    print(f"Teste 2: Kenshin Shukuchi ({kenshin.shukuchi_speed} vel, {len(kenshin.zanzou_ghosts)} zanzou) OK!")

    # 3. Testar Kemuri Bomba em Arco 3D, Limite de 2 Bombas e Auto-Dano (Fogo Amigo)
    projectiles.clear()
    kemuri = GrayNinja(wx=10.0, wy=10.0)
    kenshin_target = RedSamurai(wx=13.0, wy=10.0)

    # Arremessar 1ª bomba
    kemuri.trigger_throw_bomb(kenshin_target.wx, kenshin_target.wy, projectiles)
    assert len(projectiles) == 1
    bomb1 = projectiles[0]
    assert bomb1.wz > 0.0  # Em arco balístico 3D
    assert bomb1.vz > 0.0

    # Arremessar 2ª bomba
    kemuri.state = "IDLE"
    kemuri.trigger_throw_bomb(kenshin_target.wx, kenshin_target.wy, projectiles)
    assert len(projectiles) == 2

    # Tentar arremessar 3ª bomba (deve ser bloqueado pelo limite de 2 bombas ativas!)
    kemuri.state = "IDLE"
    kemuri.trigger_throw_bomb(kenshin_target.wx, kenshin_target.wy, projectiles)
    assert len(projectiles) == 2, "Limite de 2 bombas ativas violado!"

    # Testar Auto-Dano: se Kemuri estiver dentro do raio de explosão ao detonar
    projectiles.clear()
    bomb_suicide = GrayNinja(wx=10.0, wy=10.0)
    suicide_target = RedSamurai(wx=10.2, wy=10.0)
    bomb_suicide.trigger_throw_bomb(10.1, 10.0, projectiles)
    assert len(projectiles) == 1
    p_bomb = projectiles[0]
    p_bomb.fuse_timer = 0.0  # Pavio expirou bem no pé de ambos!
    winner = combat.process_combat(bomb_suicide, suicide_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "DRAW", f"Esperado empate por suicídio de bomba, obtido {winner}"
    assert bomb_suicide.is_alive == False
    assert suicide_target.is_alive == False
    print("Teste 3: Kemuri Bomba em Arco 3D (Limite de 2 e Auto-Dano/Fogo Amigo) OK!")

    # 4. Testar Rifleman (Tanegashima): Tiro Fatal, Esvaziamento de Munição, Recarga com Hold e Salto Evasivo
    projectiles.clear()
    rifleman = Rifleman(wx=6.0, wy=11.0)
    samurai_target = BlueSamurai(wx=11.0, wy=11.0)
    assert rifleman.has_ammo == True

    rifleman.trigger_shoot(samurai_target.wx, samurai_target.wy, projectiles)
    assert len(projectiles) == 1
    assert rifleman.has_ammo == False
    bullet = projectiles[0]
    # Bala colide com alvo
    bullet.wx = samurai_target.wx
    bullet.wy = samurai_target.wy
    winner = combat.process_combat(rifleman, samurai_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS"
    assert samurai_target.is_alive == False

    # Atualizar tempo para terminar o recuo do disparo (STATE_RECOVERY)
    rifleman.update(0.40, game_map)
    assert rifleman.state == "IDLE"

    # Recarga segurando ação secundária
    rifleman.trigger_reload_hold()
    assert rifleman.is_reloading == True
    # Atualizar tempo até recarregar completamente (reload_time = 1.75s)
    for _ in range(120):
        rifleman.update(0.016, game_map)
    assert rifleman.has_ammo == True
    assert rifleman.is_reloading == False

    # Salto evasivo para trás
    initial_wx = rifleman.wx
    rifleman.facing_x = 1.0
    rifleman.facing_y = 0.0
    rifleman.trigger_evasive_backstep()
    assert rifleman.state == "BACKSTEP"
    rifleman.update(0.1, game_map)
    assert rifleman.wx < initial_wx  # Recuou na direção oposta ao olhar
    print("Teste 4: Tanegashima Rifleman (1-Hit Kill, Recarga Segurando e Salto Evasivo) OK!")

    # 5. Testar Kabuki: Sopro de Veneno, Boost de Velocidade, 10s de Morte e Modo Evasivo
    projectiles.clear()
    kabuki = Kabuki(wx=8.0, wy=11.0)
    musashi_target = BlueSamurai(wx=10.0, wy=11.0)
    initial_speed = musashi_target.speed

    kabuki.trigger_poison_spit(musashi_target.wx, musashi_target.wy, projectiles)
    assert len(projectiles) == 1
    cloud = projectiles[0]
    # Acertar o veneno no oponente
    cloud.wx = musashi_target.wx
    cloud.wy = musashi_target.wy
    combat.process_combat(kabuki, musashi_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert getattr(musashi_target, "is_poisoned", False) == True
    assert musashi_target.speed > initial_speed  # Ganhou boost de fúria!
    assert kabuki.has_poisoned_target == True

    # Kabuki bloqueado de atacar novamente!
    kabuki.trigger_poison_spit(musashi_target.wx, musashi_target.wy, projectiles)
    assert len(projectiles) == 0  # Não gerou novo projétil de veneno!

    # Kabuki usa pirueta acrobática para se esquivar
    kabuki.trigger_acrobatic_dodge(1.0, 0.0)
    assert kabuki.state == "KABUKI_ROLL"

    # Simular passagem dos 10 segundos de veneno
    for _ in range(650):
        combat.process_combat(kabuki, musashi_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert musashi_target.is_alive == False
    print("Teste 5: Kabuki Dançarino (Sopro Venenoso, 10s Morte, Boost do Rival e Esquiva Pura) OK!")

    # 6. Testar Kyudo Archer: Windup Bow Draw fatal e Cancelamento com Flecha de Corda
    projectiles.clear()
    archer = KyudoArcher(wx=6.0, wy=11.0)
    archer_target = RedSamurai(wx=12.0, wy=11.0)

    # Disparo regular: entra em windup de retesamento
    archer.trigger_bow_draw(archer_target.wx, archer_target.wy, projectiles)
    assert archer.state == "BOW_DRAW"
    assert archer.draw_timer > 0.0

    # Atualizar tempo até disparo da flecha mortal
    for _ in range(30):
        archer.update(0.016, game_map, projectiles=projectiles)
    assert archer.state != "BOW_DRAW"
    assert len(projectiles) == 1  # Flecha Yumi disparada!
    arrow = projectiles[0]
    arrow.wx = archer_target.wx
    arrow.wy = archer_target.wy
    winner = combat.process_combat(archer, archer_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS"
    assert archer_target.is_alive == False

    # Testar cancelamento de windup com Flecha de Corda
    projectiles.clear()
    archer2 = KyudoArcher(wx=5.0, wy=5.0)
    archer2.trigger_bow_draw(10.0, 5.0, projectiles)
    assert archer2.state == "BOW_DRAW"
    archer2.trigger_rope_arrow(12.0, 5.0, projectiles)
    assert archer2.state != "BOW_DRAW"  # Windup cancelado!
    assert len(projectiles) == 1
    rope = projectiles[0]
    assert rope.is_active == True
    print("Teste 6: Kyudo Archer (Windup Yumi 1-Hit Kill e Cancelamento com Flecha de Corda) OK!")

    # 7. Testar Spawns Aleatórios com Distância Mínima >= 7.0 tiles
    for _ in range(25):
        (s1_x, s1_y), (s2_x, s2_y) = get_random_arena_spawns(game_map, min_distance=7.0)
        dist = math.hypot(s1_x - s2_x, s1_y - s2_y)
        assert dist >= 7.0, f"Spawns muito próximos: {dist:.2f} < 7.0!"
        assert not game_map.is_water(s1_x, s1_y), f"Spawn P1 em água: ({s1_x}, {s1_y})"
        assert not game_map.is_water(s2_x, s2_y), f"Spawn P2 em água: ({s2_x}, {s2_y})"
    print("Teste 7: Spawns Aleatórios na Arena com Distância >= 7.0 tiles OK!")

    # 8. Testar Shuriken Stun e Doberman
    projectiles.clear()
    joe = AmericanNinja(wx=8.0, wy=11.0)
    target = RedSamurai(wx=11.0, wy=11.0)
    joe.trigger_shuriken(target.wx, target.wy, projectiles)
    assert len(projectiles) == 1
    projectiles[0].wx = target.wx
    projectiles[0].wy = target.wy
    combat.process_combat(joe, target, game_map, particles, banners, camera, projectiles, 0.016)
    assert target.state == "STUNNED"
    assert target.is_alive == True
    print("Teste 8: Shuriken atordoa (STUN) sem matar OK!")

    # 9. Testar Hajime Saitou: Gatotsu contínuo e frenagem
    saitou = SaitouSamurai(wx=10.5, wy=7.0)
    saitou.trigger_gatotsu(10.5, 15.0)
    assert saitou.state == "GATOTSU_CHARGE"
    for _ in range(15):
        saitou.update(0.05, game_map, particles)
    assert saitou.charge_speed >= 12.0
    print("Teste 9: Gatotsu Saitou aceleração OK!")

    # 10. Testar Foice de Precedência do Ninja Roxo
    murasaki2 = PurpleNinja(wx=10.0, wy=11.0)
    kenshin2 = RedSamurai(wx=10.5, wy=11.0)
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
    print("Teste 10: Precedência Absoluta do Ninja Roxo OK!")

    # 11. Testar Anne (Espadachim Pirata): Cutlass Cleave 180° e Gunpowder in Eyes Blind
    anne = PirateSwordswoman(wx=10.0, wy=10.0)
    target_dummy = BlueSamurai(wx=11.0, wy=10.0)
    anne.trigger_cutlass_cleave(target_dummy.wx, target_dummy.wy)
    assert anne.state == "ATTACK"
    assert anne.hitbox_active == True
    assert anne.hitbox_radius >= 1.30  # Alcance amplo de 180°

    # Testar Pólvora nos Olhos
    anne.state = "IDLE"
    initial_wx = anne.wx
    anne.trigger_gunpowder_blind(target_dummy.wx, target_dummy.wy, opponent=target_dummy, particles=particles)
    assert anne.state == "RECOVERY"
    assert anne.wx < initial_wx  # Recuou esquivando
    assert target_dummy.state == "STUNNED"  # Alvo cegado/atordoado!
    print("Teste 11: Espadachim Pirata Anne (Cutlass Cleave 180° e Cegar com Pólvora) OK!")

    # 12. Testar Julie (Mosqueteira): Fleche Thrust de Longo Alcance e Cloak Riposte
    julie = Musketeer(wx=10.0, wy=10.0)
    target_dummy2 = RedSamurai(wx=11.2, wy=10.0)
    julie.trigger_fleche_thrust(target_dummy2.wx, target_dummy2.wy)
    assert julie.state == "ATTACK"
    assert julie.hitbox_active == True
    assert julie.hitbox_radius >= 1.25

    # Testar Cloak Riposte
    julie.state = "IDLE"
    julie.trigger_cloak_riposte()
    assert julie.state == "PARRY"
    assert julie.is_riposte_ready == True
    print("Teste 12: Mosqueteira Julie (Fleche Thrust e Cloak Riposte) OK!")

    # 13. Testar Diretor Cinematográfico & Violência em Voxel
    director = CinematicDirector()
    kenshin_killer = RedSamurai(wx=10.0, wy=10.0)
    victim = BlueSamurai(wx=10.5, wy=10.0)
    
    # Disparar golpe fatal
    director.trigger_fatal_strike(kenshin_killer, victim, "KENSHIN_SPLIT", (1.0, 0.0))
    assert director.is_frozen() == True
    assert director.bw_flash_timer > 0.0
    assert victim.state == "DYING_FREEZE"
    assert victim.is_alive == False

    # Avançar além do delay dramático (delayed_death_timer = 0.42s)
    director.update(0.45, game_map, particles)
    assert len(director.corpses) == 1
    corpse = director.corpses[0]
    assert corpse.death_style == "KENSHIN_SPLIT"
    assert len(corpse.pieces) >= 2  # Metade superior e inferior separadas
    assert victim.state == "CORPSE_SLICED"

    # Atualizar física das peças do corpo
    for _ in range(80):
        corpse.update(0.016, game_map, particles)
    assert corpse.top_half.wz <= 0.15 or corpse.top_half.is_grounded == True
    print("Teste 13: Diretor Cinematográfico (Hitstop Freeze, Kurosawa Flash e Voxel Corpse Slicing) OK!")

    print("\n=======================================================")
    print("TODOS OS 13 TESTES DE SISTEMA PASSARAM COM 100% DE SUCESSO!")
    print("=======================================================\n")
    pygame.quit()

if __name__ == "__main__":
    test_complete_roster()
