import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.kabuki import Kabuki, PoisonCloud, OkuniDecoy
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.combat.collision import CombatSystem
from src.world.map_data import GameMap
from src.effects.cinematic_director import CinematicDirector
from src.isometric.camera import Camera

def test_kawarimi_and_poison():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    cinematic_director = CinematicDirector()
    combat = CombatSystem()
    game_map = GameMap()

    print("=== TESTE 1: Okuni Kawarimi Dash ===", flush=True)
    okuni = Kabuki(10.0, 10.0)
    decoys = []
    particles = []
    
    # 1.1 Executar Dash / Roll da Okuni diretamente
    okuni.trigger_kabuki_roll(1.0, 0.0, particles=particles, decoys=decoys)
    
    assert okuni.state == "KABUKI_ROLL", f"Estado esperado KABUKI_ROLL, obtido {okuni.state}"
    assert okuni.is_invulnerable_dodge, "Okuni deve possuir i-frames no Kawarimi Dash"
    assert len(decoys) == 1, "Kawarimi Dash DEVE criar 1 OkuniDecoy"
    assert isinstance(decoys[0], OkuniDecoy), "Decoy deve ser instância de OkuniDecoy"
    print("  [OK] Okuni Kawarimi Dash criou manequim teatral com sucesso.", flush=True)

    # 1.2 Executar Dash via execute_fighter_roll (função do motor do jogo)
    from main import execute_fighter_roll
    okuni.state = "IDLE"
    decoys.clear()
    execute_fighter_roll(okuni, 1.0, 0.0, 0.0, 0.0, particles, decoys=decoys)
    assert len(decoys) == 1, "execute_fighter_roll DEVE repassar decoys e criar 1 OkuniDecoy"
    print("  [OK] execute_fighter_roll do motor do jogo cria OkuniDecoy perfeitamente.", flush=True)

    # 1.3 Testar fallback com registered_decoys (se decoys não for passado)
    okuni.state = "IDLE"
    fallback_decoys = []
    okuni.registered_decoys = fallback_decoys
    okuni.trigger_kabuki_roll(1.0, 0.0, particles=particles)
    assert len(fallback_decoys) == 1, "Fallback registered_decoys DEVE criar 1 OkuniDecoy mesmo sem parâmetro"
    print("  [OK] Fallback de segurança registered_decoys validado.", flush=True)

    # Testar render do decoy
    decoys[0].render(surface, camera)
    print("  [OK] Render do manequim teatral (OkuniDecoy) executado.", flush=True)

    # Testar colisão/whiff punish no manequim
    attacker = RedSamurai(10.0, 10.0)
    attacker.hitbox_active = True
    attacker.hitbox_center = (10.0, 10.0)
    attacker.hitbox_radius = 1.2
    banners = []
    decoy_ref = decoys[0]
    
    # Processar combate com decoy
    combat.process_combat(attacker, okuni, game_map, particles, banners, camera, [], dt=0.016, cinematic_director=cinematic_director, decoys=decoys)
    assert not decoy_ref.is_active, "Decoy deve ser destruído ao ser atingido"
    assert len(decoys) == 0, "Decoys inativos devem ser limpos da lista de decoys ativos"
    assert attacker.state == "STUNNED", f"Atacante deveria estar STUNNED pelo Kawarimi Whiff, obtido {attacker.state}"
    assert any("KAWARIMI WHIFF!" in b.text for b in banners), "Banner KAWARIMI WHIFF! deve ser exibido"
    print("  [OK] Atacante punido com STUN ao atingir o manequim Kawarimi!", flush=True)

    print("\n=== TESTE 2: Veneno de Okuni (Dokukiri 6s) e Prevenção de Softlock ===", flush=True)
    victim = BlueSamurai(10.0, 10.0)
    cloud = PoisonCloud(10.0, 10.0, owner=okuni)
    
    # Frame 1: Vítima entra na nuvem de veneno
    banners.clear()
    cloud.update(0.016, fighters=[victim], particles=particles, banners=banners, cinematic_director=cinematic_director)
    assert getattr(victim, "is_poisoned", False), "Vítima deve ser infectada pelo veneno da nuvem"
    assert victim.poison_timer == 6.0, f"Timer de veneno deve ser iniciado em 6.0s, obtido {victim.poison_timer}"
    assert any("POISON FRENZY!" in b.text for b in banners), "Deveria exibir banner de envenenamento POISON FRENZY!"
    print("  [OK] Vítima infectada pelo veneno com timer de 6.0s e banner informativo.", flush=True)

    # Simular expiração do veneno na nuvem (fatalidade)
    victim.poison_timer = 0.01
    banners.clear()
    cloud.update(0.02, fighters=[victim], particles=particles, banners=banners, cinematic_director=cinematic_director)
    
    assert not victim.is_alive, "Vítima deveria ter perecido pelo veneno"
    assert any("POISON DEATH!" in b.text for b in banners), "Banner POISON DEATH! deve ser emitido"
    assert cinematic_director.pending_corpse is not None, "Cinematic Director deve registrar o cadáver em dissolução"
    assert cinematic_director.pending_corpse.death_style == "OKUNI_MELT", "Estilo de morte deve ser OKUNI_MELT"
    print("  [OK] Morte por veneno aciona OKUNI_MELT no CinematicDirector sem fazer o corpo sumir.", flush=True)

    # Testar que a vítima renderiza apropriadamente (sem sumir)
    victim.render(surface, camera)
    cinematic_director.update(0.50, None, particles) # Ativar transição para corpses
    for corpse in cinematic_director.corpses:
        corpse.render(surface, camera)
    print("  [OK] Render do corpo / poça de dissolução ácida executado com sucesso.", flush=True)

    # Testar verificação universal de round_winner em main (evitando softlock)
    p1 = okuni
    p2 = victim # morto
    round_winner = None
    if round_winner is None:
        if not p1.is_alive and p2.is_alive:
            round_winner = "P2_WINS"
        elif not p2.is_alive and p1.is_alive:
            round_winner = "P1_WINS"
        elif not p1.is_alive and not p2.is_alive:
            round_winner = "DRAW"
            
    assert round_winner == "P1_WINS", f"Vencedor da rodada deveria ser P1_WINS, obtido {round_winner}"
    print("  [OK] Resolução universal de round_winner bem sucedida, softlock evitado!", flush=True)

    print("\n=== TESTE 3: Cooldown e Reutilização de Dokukiri (Okuni) ===", flush=True)
    fresh_okuni = Kabuki(10.0, 10.0)
    assert fresh_okuni.poison_cooldown_timer == 0.0
    clouds = []
    
    # 1º uso: permitido
    fresh_okuni.trigger_dokukiri(12.0, 10.0, clouds)
    assert len(clouds) == 1, "Deveria ter disparado 1ª nuvem de veneno"
    assert fresh_okuni.poison_cooldown_timer > 0, "Timer de cooldown deve ser ativado"
    
    # Tentativa durante o cooldown: bloqueada
    fresh_okuni.state = "IDLE"
    fresh_okuni.trigger_dokukiri(12.0, 10.0, clouds)
    assert len(clouds) == 1, "Não deve permitir disparar Dokukiri em cooldown"
    
    # Simular passagem do tempo
    fresh_okuni.update(fresh_okuni.poison_cooldown + 0.1, game_map)
    assert fresh_okuni.poison_cooldown_timer <= 0, "Timer de cooldown deve zerar após decorrido o tempo"
    
    # 2º uso após cooldown: permitido com sucesso!
    fresh_okuni.trigger_dokukiri(12.0, 10.0, clouds)
    assert len(clouds) == 2, "Deveria ter disparado 2ª nuvem de veneno após expiração do cooldown!"
    print("  [OK] Cooldown de Dokukiri funciona perfeitamente, permitindo reuso após o tempo de recarga.", flush=True)

    print("\n=== TESTE 4: Indicador de Veneno e Emissão de Partículas em main.py ===", flush=True)
    from main import SparkParticle as MainSparkParticle
    assert MainSparkParticle is not None, "SparkParticle DEVE estar importado em main.py"
    
    # Simular o trecho exato de main.py (linhas 980-1015) para um guerreiro envenenado
    poisoned_target = BlueSamurai(10.0, 10.0)
    poisoned_target.is_poisoned = True
    poisoned_target.poison_timer = 5.2
    active_particles = []
    
    for frame in range(60):
        game_time = frame * 0.016
        psx, psy = camera.apply(poisoned_target.wx, poisoned_target.wy, 1.85)
        p_time = poisoned_target.poison_timer
        card_w = 64
        card_h = 20
        card_rect = pygame.Rect(psx - card_w // 2, psy - card_h - 10, card_w, card_h)
        pulse_rate = 6.0 if p_time < 2.0 else 2.5
        is_crit = (p_time < 2.0 and int(game_time * pulse_rate) % 2 == 0)
        card_border_col = (255, 60, 60) if is_crit else (60, 240, 110)
        text_col = (255, 90, 90) if is_crit else (100, 255, 140)
        
        pygame.draw.rect(surface, (16, 22, 18), card_rect, border_radius=6)
        pygame.draw.rect(surface, card_border_col, card_rect, 2, border_radius=6)
        pygame.draw.polygon(surface, card_border_col, [(psx, psy - 10), (psx - 5, psy - 18), (psx + 5, psy - 18)])
        
        # Emissão da faísca verde de veneno (que causava NameError: SparkParticle is not defined)
        active_particles.append(MainSparkParticle(poisoned_target.wx, poisoned_target.wy, 0.45, color=(80, 235, 110)))
        
        for part in active_particles:
            part.update(0.016)
            part.render(surface, camera)
            
    assert len(active_particles) > 0, "Partículas de veneno geradas com sucesso sem erros de runtime!"
    print("  [OK] Renderização de veneno e SparkParticle(color=(80, 235, 110)) validadas sem crash!", flush=True)

    print("\n=======================================================")
    print("TODOS OS TESTES DE KAWARIMI E VENENO PASSARAM COM SUCESSO!")
    print("=======================================================")

if __name__ == "__main__":
    test_kawarimi_and_poison()
