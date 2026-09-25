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
from src.entities.pickups import PowderPouch
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

    # Testar movimentação enquanto guarda a espada (STATE_RECOVERY)
    kenshin.state = "RECOVERY"
    old_wx = kenshin.wx
    kenshin.apply_movement(1.0, 0.0, 0.1, game_map)
    assert kenshin.wx > old_wx, "Kenshin deve conseguir se mover enquanto embainha a katana!"
    assert kenshin.state == "RECOVERY", "O estado deve permanecer RECOVERY para manter o timer de embainhar!"
    print(f"Teste 2: Kenshin Shukuchi e Movimento ao Embainhar (Noto) OK!")

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

    # Testar Auto-Dano: Kasumi possui 50% de blindagem contra sua própria bomba (toma 1 dano e sobrevive, matando o rival!)
    projectiles.clear()
    bomb_suicide = GrayNinja(wx=10.0, wy=10.0)
    suicide_target = RedSamurai(wx=10.2, wy=10.0)
    bomb_suicide.trigger_throw_bomb(10.1, 10.0, projectiles)
    assert len(projectiles) == 1
    p_bomb = projectiles[0]
    p_bomb.fuse_timer = 0.0  # Pavio expirou bem no pé de ambos!
    winner = combat.process_combat(bomb_suicide, suicide_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS", f"Esperada vitória de Kasumi pela blindagem contra a própria bomba, obtido {winner}"
    assert bomb_suicide.is_alive == True and bomb_suicide.hp == 1, "Kasumi deve sobreviver com 1 HP pela blindagem de 50%!"
    assert suicide_target.is_alive == False, "Alvo deve morrer com dano total de 2!"

    # Uma segunda explosão mata Kasumi
    bomb_suicide.state = "IDLE"
    bomb_suicide.trigger_throw_bomb(10.0, 10.0, projectiles)
    assert len(projectiles) == 1
    projectiles[0].fuse_timer = 0.0
    combat.process_combat(bomb_suicide, suicide_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert bomb_suicide.is_alive == False, "Segunda explosão deve abater Kasumi!"
    print("Teste 3: Kasumi Bomba em Arco 3D (Limite de 2, Auto-Dano com 50% Blast Armor) OK!")

    # 4. Testar Rifleman (Teppo): Início Carregado, Coleta de Pólvora no Chão, Coronhada e Salto Evasivo
    projectiles.clear()
    rifleman = Rifleman(wx=6.0, wy=11.0)
    samurai_target = BlueSamurai(wx=11.0, wy=11.0)
    assert rifleman.has_ammo == True, "Teppo deve começar municiado!"
    rifleman.has_ammo = False

    # Criação de um PowderPouch na posição do Teppo
    pouch = PowderPouch(wx=6.0, wy=11.0)
    assert pouch.is_active == True
    picked = rifleman.check_powder_pickup([pouch])
    assert picked == True, "Teppo deve coletar a pólvora ao passar por cima!"
    assert pouch.is_active == False, "Pouch deve ficar inativo após coleta!"
    assert rifleman.cocking_timer > 0.0

    # Engatilhar em 0.40s
    rifleman.update(0.45, game_map)
    assert rifleman.has_ammo == True, "Teppo deve estar municiado após engatilhar!"

    # Disparo com arma carregada
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

    # Testar coronhada tática do Teppo (1 dano + knockback 1.6m + stun)
    melee_dummy = BlueSamurai(wx=6.8, wy=11.0)
    rifleman.trigger_rifle_butt(melee_dummy.wx, melee_dummy.wy)
    assert rifleman.hitbox_active == True
    combat.process_combat(rifleman, melee_dummy, game_map, particles, banners, camera, projectiles, 0.016)
    assert melee_dummy.hp == 1, "Coronhada deve causar 1 de dano!"
    assert melee_dummy.state == "STUNNED", "Coronhada deve atordoar o oponente!"
    assert melee_dummy.wx >= 8.0, "Coronhada deve empurrar o oponente para trás!"

    # Salto evasivo para trás
    initial_wx = rifleman.wx
    rifleman.facing_x = 1.0
    rifleman.facing_y = 0.0
    rifleman.trigger_evasive_backstep()
    assert rifleman.state == "BACKSTEP"
    rifleman.update(0.1, game_map)
    assert rifleman.wx < initial_wx  # Recuou na direção oposta ao olhar

    # Testar spawn de arena com 1 pouch garantido a média distância do Teppo (Opção 2)
    arena_pouches = PowderPouch.create_arena_pouches(game_map, [rifleman], total_pouches=3)
    assert len(arena_pouches) == 3
    dist_to_pouch = math.hypot(rifleman.wx - arena_pouches[0].wx, rifleman.wy - arena_pouches[0].wy)
    assert 3.5 <= dist_to_pouch <= 5.5, f"Pouch deve nascer a média distância ({dist_to_pouch:.2f}m) do Teppo!"
    print("Teste 4: Tanegashima Rifleman (Coleta de Pólvora, Tiro Fatal, Coronhada, Salto e Spawn a Média Distância) OK!")

    # 5. Testar Okuni: Leques de Aço (Tessen) e Finta Teatral Kawarimi com Whiff Stun
    projectiles.clear()
    okuni = Kabuki(wx=8.0, wy=11.0)
    musashi_target = BlueSamurai(wx=8.8, wy=11.0)

    # Ataque Melee: Leques de Aço Tessen
    okuni.trigger_fan_strike(musashi_target.wx, musashi_target.wy)
    assert okuni.hitbox_active == True
    assert okuni.state == "ATTACK"
    winner = combat.process_combat(okuni, musashi_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS"
    assert musashi_target.is_alive == False

    # Teste da Finta Teatral Kawarimi (deixa boneco e aplica whiff stun no atacante)
    decoys = []
    okuni2 = Kabuki(wx=10.0, wy=10.0)
    attacker = BlueSamurai(wx=10.5, wy=10.0)
    okuni2.trigger_kawarimi_decoy(-1.0, 0.0, decoys)
    assert len(decoys) == 1, "Deve criar 1 boneco manequim de seda!"
    decoy = decoys[0]
    assert decoy.is_active == True
    assert okuni2.state == "KABUKI_ROLL"

    # Atacante desfere golpe melee onde estava o manequim
    attacker.trigger_combo_attack(decoy.wx, decoy.wy)
    assert attacker.hitbox_active == True
    combat.process_combat(attacker, okuni2, game_map, particles, banners, camera, projectiles, 0.016, decoys=decoys)
    assert decoy.is_active == False, "O manequim deve ser destruído ao absorver o golpe!"
    assert attacker.state == "STUNNED", "Atacante que golpear o manequim deve sofrer Whiff Stun!"
    print("Teste 5: Okuni (Leques de Aço Tessen-jutsu & Finta Teatral Kawarimi com Whiff Stun) OK!")

    # 6. Testar Kyudo Archer: Disparo Imediato sem Windup e Flecha de Corda sem Cooldown
    projectiles.clear()
    archer = KyudoArcher(wx=6.0, wy=11.0)
    archer_target = RedSamurai(wx=12.0, wy=11.0)

    # Disparo imediato (mira manual sem windup)
    archer.trigger_bow_draw(archer_target.wx, archer_target.wy, projectiles)
    assert len(projectiles) == 1  # Flecha Yumi disparada imediatamente!
    assert archer.draw_duration == 0.0
    arrow = projectiles[0]
    arrow.wx = archer_target.wx
    arrow.wy = archer_target.wy
    winner = combat.process_combat(archer, archer_target, game_map, particles, banners, camera, projectiles, 0.016)
    assert winner == "P1_WINS"
    assert archer_target.is_alive == False

    # Testar Flecha de Corda sem cooldown
    projectiles.clear()
    archer2 = KyudoArcher(wx=5.0, wy=5.0)
    assert archer2.rope_cooldown == 0.0
    archer2.trigger_rope_arrow(12.0, 5.0, projectiles)
    assert len(projectiles) == 1
    rope = projectiles[0]
    assert rope.is_active == True
    print("Teste 6: Kyudo Archer (Disparo Yumi Imediato e Flecha de Corda sem Cooldown) OK!")

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

    # 9. Testar Hajime Saitou: Gatotsu contínuo, frenagem e contenção rígida nos limites do mapa
    saitou = SaitouSamurai(wx=10.5, wy=7.0)
    saitou.trigger_gatotsu(10.5, 15.0)
    assert saitou.state == "GATOTSU_CHARGE"
    for _ in range(15):
        saitou.update(0.05, game_map, particles)
    assert saitou.charge_speed >= 12.0

    # Testar que investida rumo à borda do mapa respeita os limites e não vaza para fora
    saitou_edge = SaitouSamurai(wx=20.0, wy=11.0)
    saitou_edge.trigger_gatotsu(30.0, 11.0) # Apontado para fora do mapa no eixo X
    for _ in range(30):
        saitou_edge.update(0.05, game_map, particles)
    assert 1.0 <= saitou_edge.wx <= game_map.cols - 1.0
    assert 1.0 <= saitou_edge.wy <= game_map.rows - 1.0
    assert saitou_edge.wx == game_map.cols - 1.0
    print("Teste 9: Gatotsu Saitou aceleração e limites de mapa OK!")

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

    # Testar Pólvora nos Olhos (Stun + Slow)
    anne.state = "IDLE"
    initial_wx = anne.wx
    anne.trigger_gunpowder_blind(target_dummy.wx, target_dummy.wy, opponent=target_dummy, particles=particles)
    assert anne.state == "RECOVERY"
    assert anne.wx > initial_wx  # Avançou agressivamente fechando a distância
    assert target_dummy.state == "STUNNED"  # Alvo cegado/atordoado!
    assert target_dummy.slow_timer > 0.0    # Desacelerado pela pólvora!
    print("Teste 11: Espadachim Pirata Anne (Cutlass Cleave 180° e Avanço com Pólvora) OK!")

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

    # 14. Testar Seleção Sequencial P1 -> IA no modo vs_ai
    # A. No modo vs_ai, P2 (setas) fica desativado. P1 escolhe P1 primeiro e depois a IA.
    cs_test = CharacterSelectScreen()
    assert cs_test.vs_ai == True
    assert cs_test.selection_step == "P1"
    # P2 tenta mover com setas, mas não deve alterar nada
    cs_test.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert cs_test.p2_choice_idx == 1  # Permanece inalterado

    # P1 move com D (Musashi) e confirma escolha do P1
    cs_test.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d))
    assert cs_test.p1_choice_idx == 1
    cs_test.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    assert cs_test.selection_step == "AI"

    # Agora P1 navega para a IA (ex: S para baixo na grade: 1 + 6 = 7 Kasumi)
    cs_test.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
    assert cs_test.p2_choice_idx == 7  # Kasumi (IA) selecionada pelo P1!
    assert cs_test.p1_choice_idx == 1  # P1 permanece intacto!

    # Teste de regressão do bug de ESC:
    # No passo AI, apertar ESC deve voltar para o passo P1 (não sair para o menu principal)
    res_esc_ai = cs_test.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert res_esc_ai == False, "ESC no passo AI deve retornar False e voltar para P1"
    assert cs_test.selection_step == "P1", "selection_step deve retornar para P1"

    # Agora no passo P1, apertar ESC deve retornar 'BACK' para voltar ao menu principal
    res_esc_p1 = cs_test.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert res_esc_p1 == "BACK", "ESC no passo P1 deve retornar 'BACK'"

    # Testar método reset()
    cs_test.selection_step = "AI"
    cs_test.reset()
    assert cs_test.selection_step == "P1"

    # B. Render de coronhada de Teppo sem UnboundLocalError
    teppo_melee = Rifleman(wx=10.0, wy=10.0)
    teppo_melee.trigger_rifle_butt(12.0, 10.0)
    assert teppo_melee.state == "ATTACK"
    teppo_melee.render(screen, camera)

    # C. Hanzo Kunai Snipe contra Kasumi confere P1_WINS
    hanzo_p1 = YellowNinja(wx=5.0, wy=5.0)
    kasumi_p2 = GrayNinja(wx=8.0, wy=5.0)
    kunai_projs = []
    hanzo_p1.trigger_throw_attack(8.0, 5.0, kunai_projs)
    k_winner = None
    for _ in range(60):
        kw = combat.process_combat(hanzo_p1, kasumi_p2, game_map, [], [], camera, kunai_projs, 0.016, cinematic_director=director)
        if kw:
            k_winner = kw
            break
    assert k_winner == "P1_WINS"
    assert kasumi_p2.is_alive == False
    assert hanzo_p1.is_alive == True
    print("Teste 14: Seleção Direta de IA, Render de Coronhada Teppo e Hanzo Kunai Snipe OK!")

    # 15. Testar Novo Asset de Pólvora Voxel do Teppo com Seta Indicadora Flutuante
    pouch_test = PowderPouch(wx=10.0, wy=10.0)
    assert pouch_test.is_active == True
    # Renderizar com camera e font sem erros
    font_test = pygame.font.Font(None, 20)
    pouch_test.render(screen, camera, font_test)
    # Atualizar animação de glow/bobbing
    pouch_test.update(0.1, game_map)
    assert pouch_test.glow_timer > 0.0
    print("Teste 15: Novo Asset de Pólvora Voxel do Teppo com Seta Indicadora Flutuante OK!")

    # 16. Testar Sistema Completo de Ajuda (GameHelpModal) e Estratégia dos 12 Lutadores
    from src.ui.game_help import GameHelpModal, FIGHTERS_GUIDE_DATA
    help_modal = GameHelpModal()
    assert not help_modal.is_open

    # Abrir na aba de Regras
    help_modal.open(GameHelpModal.TAB_RULES)
    assert help_modal.is_open
    assert help_modal.current_tab == GameHelpModal.TAB_RULES
    help_modal.render(screen, pygame.font.Font(None, 36), font_test, pygame.font.Font(None, 16))

    # Alternar abas via TAB
    help_modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    assert help_modal.current_tab == GameHelpModal.TAB_CONTROLS
    help_modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))
    assert help_modal.current_tab == GameHelpModal.TAB_FIGHTERS

    # Navegação entre os 12 lutadores na aba de lutadores
    assert len(FIGHTERS_GUIDE_DATA) == 12, f"Esperado 12 combatentes no guia, encontrado {len(FIGHTERS_GUIDE_DATA)}"
    for f in FIGHTERS_GUIDE_DATA:
        assert len(f["pt"]["conceito"]) > 30, f"Conceito PT de {f['pt']['name']} deve ser descritivo!"
        assert len(f["pt"]["habilidades"]) > 20, f"Habilidades PT de {f['pt']['name']} devem ser descritivas!"
        assert len(f["pt"]["estrategia_ofensiva"]) > 30, f"Estratégia ofensiva PT de {f['pt']['name']} deve ser descritiva!"
        assert len(f["pt"]["estrategia_defensiva"]) > 30, f"Estratégia defensiva PT de {f['pt']['name']} deve ser descritiva!"
        assert len(f["en"]["conceito"]) > 30, f"Conceito EN de {f['en']['name']} deve ser descritivo!"
        assert len(f["en"]["habilidades"]) > 20, f"Habilidades EN de {f['en']['name']} devem ser descritivas!"
        assert len(f["en"]["estrategia_ofensiva"]) > 30, f"Estratégia ofensiva EN de {f['en']['name']} deve ser descritiva!"
        assert len(f["en"]["estrategia_defensiva"]) > 30, f"Estratégia defensiva EN de {f['en']['name']} deve ser descritiva!"

    # Navegar com D e A
    help_modal.selected_fighter_idx = 0
    help_modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d))
    assert help_modal.selected_fighter_idx == 1
    help_modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
    assert help_modal.selected_fighter_idx == 0

    # Fechar com ESC
    help_modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert not help_modal.is_open

    # Testar integração na CharacterSelectScreen
    cs_screen = CharacterSelectScreen()
    assert not cs_screen.help_modal.is_open
    cs_screen.render(screen, pygame.font.Font(None, 36), font_test, pygame.font.Font(None, 16))
    assert len(cs_screen.info_btn_rects) == 12, f"Esperado 12 botões de interrogação [?], obtido {len(cs_screen.info_btn_rects)}"

    # Tecla H abre o guia de regras
    cs_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
    assert cs_screen.help_modal.is_open
    assert cs_screen.help_modal.current_tab == GameHelpModal.TAB_RULES
    cs_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert not cs_screen.help_modal.is_open

    # Tecla F abre a ficha de estratégia do guerreiro focado (P1)
    cs_screen.p1_choice_idx = 5  # Teppo
    cs_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f))
    assert cs_screen.help_modal.is_open
    assert cs_screen.help_modal.current_tab == GameHelpModal.TAB_FIGHTERS
    assert cs_screen.help_modal.selected_fighter_idx == 5
    print("Teste 16: Sistema Completo de Ajuda e Guia Estratégico dos 12 Guerreiros OK!")

    # 17. Testar Módulo i18n Padrão Boardbots, Alternância de Idioma e Rolagem/Anti-Overflow do Modal
    from src.i18n import get_lang, set_lang, toggle_lang, t, LANG_PT, LANG_EN
    set_lang(LANG_PT)
    assert get_lang() == "pt"
    assert t("select_title") == "ESCOLHA SEU GUERREIRO"
    assert t("powder_badge") == "PÓLVORA"
    assert t("powder_tracker", dist=4.2) == "PÓLVORA 4.2m"

    # Alternar para inglês
    assert toggle_lang() == "en"
    assert get_lang() == "en"
    assert t("select_title") == "CHOOSE YOUR WARRIOR"
    assert t("powder_badge") == "POWDER"
    assert t("powder_tracker", dist=4.2) == "POWDER 4.2m"

    # Alternar de volta para português
    assert toggle_lang() == "pt"
    assert get_lang() == "pt"

    # Testar Rolagem Vertical e Anti-Overflow no GameHelpModal
    help_modal.open(GameHelpModal.TAB_FIGHTERS)
    help_modal.selected_fighter_idx = 0
    help_modal.scroll_y = 0.0
    help_modal.render(screen, pygame.font.Font(None, 36), font_test, pygame.font.Font(None, 16))

    # Quando max_scroll > 0 (conteúdo que ultrapassa a janela visível), rolagem deve ser funcional
    help_modal.max_scroll = 120.0

    # Roda do mouse para baixo (MOUSEWHEEL y=-1) deve aumentar scroll_y
    ev_wheel_down = pygame.event.Event(pygame.MOUSEWHEEL, y=-1, x=0)
    help_modal.handle_event(ev_wheel_down)
    assert help_modal.scroll_y > 0.0, f"Esperado scroll_y > 0 após roda do mouse para baixo, obtido {help_modal.scroll_y}"

    # Roda do mouse para cima (MOUSEWHEEL y=1) deve diminuir scroll_y
    ev_wheel_up = pygame.event.Event(pygame.MOUSEWHEEL, y=1, x=0)
    help_modal.handle_event(ev_wheel_up)
    assert help_modal.scroll_y == 0.0, f"Esperado scroll_y == 0 após retorno ao topo, obtido {help_modal.scroll_y}"

    # Teclas DOWN e UP também realizam rolagem
    ev_key_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    help_modal.handle_event(ev_key_down)
    assert help_modal.scroll_y > 0.0

    ev_key_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    help_modal.handle_event(ev_key_up)
    assert help_modal.scroll_y == 0.0

    # Filtros de Subseção (TODOS, CONCEITO, ARSENAL, OFENSIVA, DEFENSIVA)
    help_modal.set_sub_section(GameHelpModal.SEC_CONCEPT)
    assert help_modal.fighter_sub_section == GameHelpModal.SEC_CONCEPT
    assert help_modal.scroll_y == 0.0

    help_modal.scroll_y = 40.0
    help_modal.set_sub_section(GameHelpModal.SEC_ARSENAL)
    assert help_modal.fighter_sub_section == GameHelpModal.SEC_ARSENAL
    assert help_modal.scroll_y == 0.0  # Resetou a rolagem ao trocar de subseção

    help_modal.set_sub_section(GameHelpModal.SEC_ALL)
    assert help_modal.fighter_sub_section == GameHelpModal.SEC_ALL

    # Alternar idioma pelo botão na CharacterSelectScreen via tecla L
    curr = get_lang()
    cs_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_l))
    assert get_lang() != curr
    cs_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_l))
    assert get_lang() == curr
    print("Teste 17: Localização i18n Bilíngue Boardbots, Rolagem Vertical Anti-Overflow e Filtros de Seção OK!")

    # 18. Testar Tela de Título Sumi-E & Seletor de Modos
    from src.ui.title_screen import SumieTitleScreen, MODE_ARCADE, MODE_VERSUS, MODE_OPTIONS
    title_screen = SumieTitleScreen()
    assert title_screen.selected_mode == MODE_VERSUS  # Versus é o padrão

    # Navegar para Arcade (Cima / W)
    title_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    assert title_screen.selected_mode == MODE_ARCADE
    # Tentar confirmar Arcade -> Deve bloquear e retornar None, ativando notice_timer
    res_arcade = title_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert res_arcade is None
    assert title_screen.notice_timer > 0.0

    # Navegar para Versus e confirmar
    title_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert title_screen.selected_mode == MODE_VERSUS
    res_vs = title_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert res_vs == "VERSUS"

    # Navegar para Options e confirmar
    title_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert title_screen.selected_mode == MODE_OPTIONS
    res_opt = title_screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    assert res_opt == "OPTIONS"

    # Atualizar e renderizar Title Screen sem erros
    title_screen.update(0.016)
    title_screen.render(screen, pygame.font.Font(None, 48), font_test, pygame.font.Font(None, 20))
    print("Teste 18: Tela de Título Sumi-E (Seletor Arcade/Versus/Options, Partículas de Cinzas e Bloqueios) OK!")

    # 19. Testar Tela de Seleção de Arena
    from src.ui.arena_select import ArenaSelectScreen
    from src.config import ARENA_BAMBOO, ARENA_KYOTO, ARENA_RANDOM
    arena_sel = ArenaSelectScreen()
    assert arena_sel.selected_idx == 1  # Kyoto selecionado inicialmente
    assert arena_sel.get_resolved_arena_id() == ARENA_KYOTO

    # Navegar para a esquerda -> Floresta de Bambu
    arena_sel.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    assert arena_sel.selected_idx == 0
    assert arena_sel.get_resolved_arena_id() == ARENA_BAMBOO

    # Navegar para a direita duas vezes -> Aleatório
    arena_sel.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
    arena_sel.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
    assert arena_sel.selected_idx == 2
    rand_res = arena_sel.get_resolved_arena_id()
    assert rand_res in (ARENA_BAMBOO, ARENA_KYOTO)

    # Testar tecla ESC voltando
    esc_res = arena_sel.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert esc_res == "BACK"

    # Atualizar e renderizar Arena Select Screen
    arena_sel.update(0.016)
    arena_sel.render(screen, pygame.font.Font(None, 48), font_test, pygame.font.Font(None, 20))
    print("Teste 19: Tela de Seleção de Arena (Cards, Prévias Gráficas, Resolução Random e Navegação) OK!")

    # 20. Testar Arena Kyoto Bakumatsu (Voxel 3D, Carruagens Assassinas e Escombros Flamejantes)
    from src.world.kyoto_map import KyotoMap, RunawayCarriage, FallingDebris
    from main import get_kyoto_arena_spawns

    kyoto = KyotoMap()
    assert kyoto.cols == 22 and kyoto.rows == 22
    assert len(kyoto.buildings) > 0  # Fachadas machiya geradas

    # Testar spawns seguros na avenida central
    sp1, sp2 = get_kyoto_arena_spawns(kyoto, min_distance=7.0)
    assert math.hypot(sp1[0] - sp2[0], sp1[1] - sp2[1]) >= 7.0
    assert kyoto.is_water(sp1[0], sp1[1]) is False

    # Testar colisão fatal da Carruagem Desgovernada Voxel
    cinematic_director = CinematicDirector()
    dummy_p1 = RedSamurai(wx=10.0, wy=10.0)
    dummy_p2 = BlueSamurai(wx=18.0, wy=18.0)
    carriage = RunawayCarriage(start_pos=(8.0, 10.0), end_pos=(20.0, 10.0), speed=14.0)
    carriage.warning_timer = 0.0  # Ativa imediatamente
    c_particles = []
    c_banners = []

    # Verificar atropelamento letal do P1
    hit_carriage = carriage.check_fighter_hit(dummy_p1, c_particles, c_banners, camera, cinematic_director)
    assert hit_carriage is True
    assert dummy_p1.is_alive is False
    assert len(c_banners) > 0

    # Testar queda e impacto letal dos Escombros Flamejantes
    debris = FallingDebris(target_x=18.0, target_y=18.0)
    debris.timer = debris.warning_duration + 0.1  # Avança fase de telegrafia
    debris.wz = 0.1  # Quase tocando o chão
    d_particles = []
    d_banners = []

    # Atualizar escombro para tocar o solo em cima de dummy_p2
    debris.update(0.05, camera, d_particles, [dummy_p1, dummy_p2], d_banners, cinematic_director)
    assert debris.has_impacted is True
    assert dummy_p2.is_alive is False
    assert len(d_banners) > 0

    # Testar renderização de terreno e objetos da Arena Kyoto
    kyoto.render_terrain(screen, camera, 1.0)
    for b in kyoto.buildings:
        b.render(screen, camera, 1.0)
    # Testar duas carruagens simultâneas passando em sentidos opostos
    c1 = RunawayCarriage(start_pos=(9.8, -4.0), end_pos=(9.8, 26.0), speed=14.0)
    c2 = RunawayCarriage(start_pos=(11.2, 26.0), end_pos=(11.2, -4.0), speed=14.0)
    assert c1.dir_y > 0 and c2.dir_y < 0 # Sentidos rigorosamente opostos
    c1.warning_timer = 0.0
    c2.warning_timer = 0.0
    for _ in range(10):
        c1.update(0.05, camera, c_particles)
        c2.update(0.05, camera, c_particles)
    assert c1.wy > -4.0 and c2.wy < 26.0
    c1.render(screen, camera)
    c2.render(screen, camera)

    # Testar update do mapa Kyoto com timers acelerados gerando perigos
    kyoto.carriage_timer = 0.0
    kyoto.debris_timer = 0.0
    kyoto.update(0.05, [dummy_p1, dummy_p2], camera, c_particles, c_banners, cinematic_director)
    assert len(kyoto.carriages) >= 1
    assert len(kyoto.falling_debris) >= 1

    print("Teste 20: Arena Kyoto Bakumatsu (Avenida Espaçosa, Mobilidade Total, Carruagens Cruzadas e Alta Frequência de Escombros) OK!")

    # 21. Testar Nome Kenshi, Pólvora Condicional e Portraits Conceituais de Arena
    kenshi_fighter = RedSamurai(wx=5.0, wy=5.0)
    assert kenshi_fighter.name == "Kenshi", f"Nome do lutador deve ser Kenshi, obtido: {kenshi_fighter.name}"
    
    from src.config import DEFAULT_CONTROLS
    from src.ui.settings_menu import SettingsMenu
    settings_menu = SettingsMenu(DEFAULT_CONTROLS)
    p1_items = [key for key, label, col in settings_menu.items if key.startswith("P1_")]
    assert len(p1_items) >= 6, f"Esperado ao menos 6 itens remapeáveis para Player 1, encontrados: {len(p1_items)}"
    p2_items = [key for key, label, col in settings_menu.items if key.startswith("P2_")]
    assert len(p2_items) >= 6, f"Esperado ao menos 6 itens remapeáveis para Player 2, encontrados: {len(p2_items)}"
    legacy_fighter_labels = [label for key, label, col in settings_menu.items if any(n in label for n in ["Kenshin", "Kenshi", "Musashi"])]
    assert len(legacy_fighter_labels) == 0, f"Nenhuma string deve conter nomes de lutadores específicos no SettingsMenu! Encontradas: {legacy_fighter_labels}"

    # Pólvora condicional: SEM teppo = lista vazia
    pouches_no_teppo = PowderPouch.create_arena_pouches(game_map, [kenshi_fighter, dummy_p2], total_pouches=3)
    assert len(pouches_no_teppo) == 0, "Sem combatente de arma de fogo, não deve gerar saquinhos de pólvora!"

    # Pólvora condicional: COM teppo = 3 saquinhos
    pouches_with_teppo = PowderPouch.create_arena_pouches(game_map, [kenshi_fighter, rifleman], total_pouches=3)
    assert len(pouches_with_teppo) == 3, "Com Teppo presente, deve gerar a quantidade correta de pólvora!"

    # Portraits Conceituais da Seleção de Arena
    assert arena_sel.preview_surfs.get(ARENA_BAMBOO) is not None, "Portrait da Floresta de Bambu deve estar carregado!"
    assert arena_sel.preview_surfs.get(ARENA_KYOTO) is not None, "Portrait de Kyoto Bakumatsu deve estar carregado!"
    assert arena_sel.preview_surfs.get(ARENA_RANDOM) is not None, "Portrait da Arena Aleatória deve estar carregado!"
    print("Teste 21: Ajustes de Nome Kenshi, Pólvora Condicional e Portraits Conceituais de Arena OK!")

    print("\n=======================================================")
    print("TODOS OS 21 TESTES DE SISTEMA PASSARAM COM 100% DE SUCESSO!")
    print("=======================================================\n")
    pygame.quit()

if __name__ == "__main__":
    test_complete_roster()

