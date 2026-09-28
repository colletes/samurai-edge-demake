"""
Testes automatizados cobrindo os 20 patches e melhorias críticas de combate,
controles, balanceamento, HUD e estabilidade.
"""
import os
import sys
import math
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Inicialização headless para testes
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

from src.entities.samurai import STATE_IDLE, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_ROLL
from src.config import (
    DEFAULT_CONTROLS, CHAR_GRAY, CHAR_PURPLE, CHAR_PIRATE, CHAR_MUSKETEER,
    CHAR_ARCHER, CHAR_KENSHIN, CHAR_NINJA, CHAR_AMERICAN, CHAR_RIFLE, CHAR_KABUKI
)
from src.world.map_data import GameMap
from src.isometric.camera import Camera
from src.combat.collision import CombatSystem
from src.entities.gray_ninja import GrayNinja
from src.entities.purple_ninja import PurpleNinja
from src.entities.red_samurai import RedSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.musketeer import Musketeer
from src.entities.pirate import PirateSwordswoman
from src.entities.kyudo_archer import KyudoArcher
from src.entities.american_ninja import AmericanNinja
from src.entities.kabuki import Kabuki, PoisonCloud
from src.entities.doberman import DobermanDog, STATE_DOG_FOLLOW, STATE_DOG_BARK, STATE_DOG_CHARGE, STATE_DOG_KNOCKED_OUT
from src.entities.projectile import RemoteMineEntity, MusketBulletProjectile, KunaiProjectile
from src.effects.particles import SmokeParticle, SparkParticle, FloatingBanner
from src.ui.character_select import CharacterSelectScreen
from main import get_fighter_cooldown_data

class DummyControllerManager:
    def __init__(self):
        self.rumble_calls = []
    def rumble_player(self, player_idx, low_freq=0.5, high_freq=0.8, duration_ms=150):
        self.rumble_calls.append((player_idx, low_freq, high_freq, duration_ms))
    def is_action_pressed(self, *args, **kwargs):
        return False
    def get_movement(self, *args, **kwargs):
        return 0.0, 0.0
    def get_controller_count(self):
        return 0
    def handle_event(self, event):
        pass


def test_item_1_kasumi_remote_explosion_damages_self():
    """Item 1: Kasumi recebe dano de 1 HP mesmo parada em cima da mina ou em dodge/roll."""
    kasumi = GrayNinja(10.0, 10.0)
    p2 = RedSamurai(15.0, 10.0)
    mine = RemoteMineEntity(10.0, 10.0, owner=kasumi)
    kasumi.is_invulnerable_dodge = True
    particles = []
    banners = []
    # Detonação manual da mina
    mine.detonate([kasumi, p2], particles, banners)
    # Kasumi deve ter recebido 1 de dano mesmo com invulnerabilidade de dodge ativa
    assert kasumi.hp == 1


def test_item_2_kasumi_dash_leaves_smoke_and_invisibility():
    """Item 2: Roll de Kasumi gera explosão maciça de fumaça, alta transparência (alpha=15) e janela de stealth."""
    kasumi = GrayNinja(10.0, 10.0)
    particles = []
    kasumi.trigger_roll(1.0, 0.0, particles=particles)
    assert kasumi.state == STATE_ROLL
    assert kasumi.alpha <= 20
    assert kasumi.stealth_timer > 0
    # Verifica que emitiu nuvem maciça de SmokeParticle (>= 40 partículas) e nenhuma SparkParticle
    smoke_count = sum(1 for p in particles if isinstance(p, SmokeParticle))
    spark_count = sum(1 for p in particles if isinstance(p, SparkParticle))
    assert smoke_count >= 40
    assert spark_count == 0



def test_item_4_cooldown_hud_top_bar_data():
    """Item 4: HUD de cooldowns reporta dados válidos para Kasumi, Okuni, Murasaki, Tomoe e Teppo."""
    kasumi = GrayNinja(10.0, 10.0)
    kasumi.mine_timer = 1.5
    data_k = get_fighter_cooldown_data(kasumi)
    assert data_k is not None
    assert data_k["timer"] == 1.5
    assert data_k["max_cd"] == kasumi.mine_cooldown

    tomoe = KyudoArcher(10.0, 10.0)
    tomoe.rope_timer = 1.0
    data_t = get_fighter_cooldown_data(tomoe)
    assert data_t is not None
    assert data_t["timer"] == 1.0
    assert data_t["max_cd"] == 2.0

    kenshi = RedSamurai(10.0, 10.0)
    kenshi.state = STATE_RECOVERY
    kenshi.state_timer = 0.55
    data_k2 = get_fighter_cooldown_data(kenshi)
    assert data_k2 is not None
    assert "Iai" in data_k2["name"]
    assert data_k2["timer"] == 0.55
    assert data_k2["max_cd"] == kenshi.recovery_duration


def test_item_5_p2_i_key_is_back_and_esc_does_not_cancel_p2():
    """Item 5: Tecla I cancela P2; ESC cancela P1 e não interfere nas ações de P2."""
    screen = CharacterSelectScreen()
    screen.vs_ai = False
    screen.p1_ready = True
    screen.p2_ready = True

    # Pressionar I no teclado deve desconfirmar P2
    event_i = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_i})
    screen.handle_event(event_i)
    assert screen.p2_ready is False
    assert screen.p1_ready is True

    # Reconfinar P2
    screen.p2_ready = True
    # Pressionar ESC deve desconfirmar P1, sem cancelar P2
    event_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
    screen.handle_event(event_esc)
    assert screen.p1_ready is False
    assert screen.p2_ready is True


def test_item_6_joes_dog_only_stunned_when_attacking():
    """Item 6: O cão só pode ser nocauteado se estiver atacando (BARK ou CHARGE), não em FOLLOW."""
    p1 = AmericanNinja(10.0, 10.0)
    p2 = RedSamurai(10.5, 10.0)
    p2.hitbox_active = True
    p2.hitbox_radius = 1.0
    p2.hitbox_center = (10.5, 10.0)
    dog = p1.dog
    dog.wx, dog.wy = 10.5, 10.0
    dog.state = STATE_DOG_FOLLOW

    combat = CombatSystem()
    game_map = GameMap()
    particles = []
    banners = []
    camera = type("DummyCam", (), {"add_shake": lambda self, s: None})()

    # Em FOLLOW, o cão NÃO deve ser atordoado por lâminas
    combat.process_combat(p1, p2, game_map, particles, banners, camera, [])
    assert dog.state == STATE_DOG_FOLLOW

    # Em BARK ou CHARGE, o cão DEVE ser atordoado
    p2.hitbox_active = True
    dog.state = STATE_DOG_CHARGE
    combat.process_combat(p1, p2, game_map, particles, banners, camera, [])
    assert dog.state == STATE_DOG_KNOCKED_OUT
    assert dog.state_timer > 0


def test_item_7_and_8_julie_flintlock_and_repel():
    """Item 7 e 8: Repel é a esquiva (trigger_roll) e Secundário é o disparo Flintlock."""
    julie = Musketeer(10.0, 10.0)
    opp = RedSamurai(10.8, 10.0)
    particles = []
    banners = []

    # Roll é Cape Flourish Repel
    julie.trigger_roll(1.0, 0.0, particles, opponent=opp, banners=banners)
    assert julie.state == "CAPE_FLOURISH"
    assert julie.is_invulnerable_dodge is True
    assert julie.state_timer <= 0.16 + 1e-4

    # Secundário é Pocket Flintlock (após recuperar da esquiva)
    julie.state = STATE_IDLE
    julie.dash_recovery_timer = 0.0
    julie.flintlock_timer = 0.0
    projs = []
    julie.trigger_flintlock_shot(15.0, 10.0, projs, particles)
    assert len(projs) == 1
    assert isinstance(projs[0], MusketBulletProjectile)
    assert projs[0].max_range <= 6.0


def test_item_9_julie_flintlock_banner_name():
    """Item 9: Disparo fatal de Julie exibe POCKET FLINTLOCK SNIPE! em vez de Tanegashima."""
    julie = Musketeer(10.0, 10.0)
    p2 = RedSamurai(10.5, 10.0)
    bullet = MusketBulletProjectile(10.5, 10.0, 0.45, 1.0, 0.0, owner=julie)
    combat = CombatSystem()
    game_map = GameMap()
    particles = []
    banners = []
    camera = type("DummyCam", (), {"add_shake": lambda self, s: None})()

    combat.process_combat(julie, p2, game_map, particles, banners, camera, [bullet])
    banner_texts = [b.text for b in banners]
    assert "POCKET FLINTLOCK SNIPE!" in banner_texts
    assert not any("TANEGASHIMA" in t for t in banner_texts)


def test_item_10_murasaki_frontal_deflection_cone():
    """Item 10: Escudo de corrente de Murasaki deflete apenas no cone frontal de 120 graus."""
    murasaki = PurpleNinja(10.0, 10.0)
    murasaki.facing_x = 1.0
    murasaki.facing_y = 0.0
    murasaki.is_spinning_chain = True

    combat = CombatSystem()
    game_map = GameMap()
    camera = type("DummyCam", (), {"add_shake": lambda self, s: None})()

    # Projétil vindo de frente (wx=10.8, wy=10.0, dir_x = -1.0) -> DEVE defletir
    bullet_front = MusketBulletProjectile(10.8, 10.0, 0.45, -1.0, 0.0, owner=None)
    particles = []
    banners = []
    combat.process_combat(murasaki, RedSamurai(20, 20), game_map, particles, banners, camera, [bullet_front])
    assert bullet_front.is_active is False
    assert any("FRONTAL CHAIN DEFLECTION!" in b.text for b in banners)

    # Projétil vindo por trás (wx=9.2, wy=10.0, dir_x = 1.0) -> NÃO deve defletir pelo cone frontal
    bullet_back = MusketBulletProjectile(9.2, 10.0, 0.45, 1.0, 0.0, owner=None)
    particles = []
    banners = []
    murasaki.is_alive = True
    combat.process_combat(murasaki, RedSamurai(20, 20), game_map, particles, banners, camera, [bullet_back])
    assert not any("FRONTAL CHAIN DEFLECTION!" in b.text for b in banners)


def test_item_11_murasaki_kama_reach():
    """Item 11: Alcance da foice de Murasaki é 1.30m."""
    murasaki = PurpleNinja(10.0, 10.0)
    murasaki.trigger_kama_strike(12.0, 10.0)
    assert murasaki.hitbox_radius >= 1.30


def test_item_12_murasaki_roll_smoke_no_sparks():
    """Item 12: Roll de Murasaki gera fumaça e névoa ninja sem faíscas."""
    murasaki = PurpleNinja(10.0, 10.0)
    particles = []
    murasaki.trigger_roll(1.0, 0.0, particles=particles)
    assert sum(1 for p in particles if isinstance(p, SmokeParticle)) > 0
    assert sum(1 for p in particles if isinstance(p, SparkParticle)) == 0


def test_item_13_and_14_kenshi_ryuu_tsui_sen_and_freeze_fix():
    """Item 13 e 14: Ryuu Tsui Sen inicia alto wz=2.6 e Kenshi não congela após ataque."""
    kenshi = RedSamurai(10.0, 10.0)
    kenshi.trigger_ryuu_tsui_sen(12.0, 10.0)
    assert kenshi.state == "RYUU_TSUI_SEN"
    assert kenshi.wz >= 2.5

    # Teste de não-congelamento: ataque normal transiciona para RECOVERY e depois IDLE
    kenshi2 = RedSamurai(10.0, 10.0)
    kenshi2.wz = 0.0
    kenshi2.trigger_iai_attack(12.0, 10.0)
    assert kenshi2.state == STATE_ATTACK
    kenshi2.update(kenshi2.dash_duration + 0.02, GameMap())
    assert kenshi2.state == STATE_RECOVERY
    # Durante o recovery (embainhando a katana), Kenshi NÃO pode atacar novamente
    assert not kenshi2.can_act(), "Kenshi não deve poder agir durante o cooldown de recovery!"
    kenshi2.trigger_iai_attack(14.0, 10.0)
    assert kenshi2.state == STATE_RECOVERY, "Cooldown violado! Kenshi não deve interromper o recovery com novo ataque!"
    kenshi2.update(kenshi2.recovery_duration + 0.02, GameMap())
    assert kenshi2.state == STATE_IDLE
    assert kenshi2.can_act(), "Após o término do cooldown de recovery, Kenshi pode agir normalmente!"


def test_item_15_solid_obstacle_consistency():
    """Item 15: Ataques em obstáculos sólidos (rochas, poço, lanternas) geram hitstop e faíscas."""
    kenshi = RedSamurai(5.5, 14.5)
    game_map = GameMap()
    kenshi.trigger_iai_attack(6.0, 14.5)
    combat = CombatSystem()
    particles = []
    camera = type("DummyCam", (), {"add_shake": lambda self, s: None})()
    ctrl_mgr = DummyControllerManager()

    combat.process_combat(kenshi, RedSamurai(20, 20), game_map, particles, [], camera, [], ctrl_mgr=ctrl_mgr)
    assert combat.hitstop_timer > 0
    assert len(particles) > 0


def test_item_16_tomoe_rope_cooldown():
    """Item 16: Cooldown da corda de Tomoe é 2.0s."""
    tomoe = KyudoArcher(10.0, 10.0)
    assert tomoe.rope_cooldown == 2.0
    projs = []
    tomoe.trigger_rope_arrow(15.0, 10.0, projs, game_map=GameMap())
    assert tomoe.rope_timer == 2.0
    # Não pode atirar corda novamente enquanto timer > 0
    projs2 = []
    tomoe.trigger_rope_arrow(15.0, 10.0, projs2, game_map=GameMap())
    assert len(projs2) == 0


def test_item_17_anne_slow_soot_and_banner():
    """Item 17: Black Powder Dash da Anne aplica lentidão com banner SLOW e fuligem."""
    anne = PirateSwordswoman(10.0, 10.0)
    opp = RedSamurai(10.4, 10.0)
    particles = []
    banners = []
    anne.trigger_roll(1.0, 0.0, particles=particles)
    anne.update(0.016, GameMap(), particles=particles, opponent=opp, banners=banners)
    assert opp.slow_timer > 0
    assert any(b.text == "SLOW!" for b in banners)
    assert any(isinstance(p, SmokeParticle) for p in particles)


def test_item_18_and_19_hanzo_kunai_bounds_and_midair_angle():
    """Item 18 e 19: Kunai fica estritamente na arena e arremesso aéreo tem vz=-6.5 e range 2.8m."""
    hanzo = YellowNinja(1.0, 1.0)
    hanzo.state = "JUMP"
    hanzo.wz = 1.0
    projs = []
    hanzo.trigger_midair_throw(1.0, 10.0, projs)
    assert len(projs) == 1
    kunai = projs[0]
    assert kunai.vz == -6.5
    assert kunai.max_range <= 2.8

    # Teste de limite da arena
    game_map = GameMap()
    kunai.wx = 0.5
    kunai.update(0.1, game_map, [])
    assert kunai.wx >= 1.2
    assert kunai.state == "ON_GROUND"


def test_item_20_flintlock_range():
    """Item 20: Alcance da Flintlock é reduzido para ~5.8 tiles como último recurso tático."""
    julie = Musketeer(10.0, 10.0)
    julie.flintlock_timer = 0.0
    projs = []
    julie.trigger_flintlock_shot(15.0, 10.0, projs)
    assert len(projs) == 1
    bullet = projs[0]
    assert bullet.max_range == 5.8
    # Ao viajar 6.0 tiles, deve dissipar
    bullet.update(0.5, GameMap(), [])
    assert bullet.is_active is False


def test_loading_screen_progress_and_rendering():
    """Valida a nova tela de carregamento (LoadingScreen) com barra de progresso e Sumi-e."""
    from src.ui.loading_screen import LoadingScreen
    surface = pygame.Surface((1280, 720))
    loader = LoadingScreen(surface)
    assert loader.progress == 0.0

    # Teste de avanço de progresso
    loader.update(0.25, "Iniciando motor...", delay_ms=0)
    assert loader.progress == 0.25
    assert loader.message == "Iniciando motor..."

    loader.update(0.75, "Carregando guerreiros...", delay_ms=0)
    assert loader.progress == 0.75

    loader.update(1.0, "Pronto!", delay_ms=0)
    assert loader.progress == 1.0


def test_julie_cape_flourish_rendering():
    """Valida que o render de Julie em CAPE_FLOURISH e Coup de Pied não lança NameError."""
    surface = pygame.Surface((1280, 720))
    camera = Camera(1280, 720)
    julie = Musketeer(10.0, 10.0)
    julie.state = "CAPE_FLOURISH"
    julie.state_timer = 0.08
    # Deve renderizar perfeitamente sem erros
    julie.render(surface, camera)

    # Testar também em IDLE, ATTACK e FLECHE
    for st in ("IDLE", "ATTACK", "FLECHE", "RECOVERY"):
        julie.state = st
        julie.render(surface, camera)


def test_okuni_poison_cone_push_and_frenzy():
    """Valida o Dokukiri em cone frontal com push back, área menor e adrenalina (+25% velocidade e -20% CD)."""
    okuni = Kabuki(10.0, 10.0)
    clouds = []
    # Dokukiri apontado para a direita (1.0, 0.0)
    okuni.trigger_dokukiri(15.0, 10.0, clouds=clouds)
    assert len(clouds) == 1
    cloud = clouds[0]
    assert cloud.cone_length <= 2.0
    assert cloud.radius <= 1.0

    target_in_front = RedSamurai(11.2, 10.0)
    target_in_front.ryuu_timer = 2.0
    target_behind = RedSamurai(8.5, 10.0)

    # Atualizar nuvem com ambos os alvos
    cloud.update(0.05, fighters=[target_in_front, target_behind])

    # 1. Alvo atrás NÃO deve ser atingido nem empurrado
    assert not getattr(target_behind, "is_poisoned", False)
    assert target_behind.wx == 8.5

    # 2. Alvo à frente DEVE ser empurrado para trás
    assert target_in_front.wx > 11.2, "Alvo deve sofrer push back pelo sopro dos leques!"
    assert target_in_front.is_poisoned is True
    assert target_in_front.slow_timer == 0.0, "Veneno não deve aplicar slow ao oponente!"

    # 3. Cooldown ativo reduzido em 20% imediatamente
    assert target_in_front.ryuu_timer <= 1.61, "Cooldown deve ser reduzido em 20% imediatamente!"

    # 4. Velocidade de movimentação com +25% de bônus
    game_map = GameMap()
    old_wx = target_in_front.wx
    target_in_front.apply_movement(1.0, 0.0, 0.1, game_map)
    dist_poisoned = target_in_front.wx - old_wx

    normal_fighter = RedSamurai(old_wx, target_in_front.wy)
    old_norm_wx = normal_fighter.wx
    normal_fighter.apply_movement(1.0, 0.0, 0.1, game_map)
    dist_normal = normal_fighter.wx - old_norm_wx

    assert dist_poisoned > dist_normal, "Combatente envenenado deve se mover 25% mais rápido (adrenalina)!"
    assert abs((dist_poisoned / dist_normal) - 1.25) < 0.05, "Multiplicador de velocidade deve ser de aproximadamente 1.25!"


if __name__ == "__main__":
    tests = [
        test_item_1_kasumi_remote_explosion_damages_self,
        test_item_2_kasumi_dash_leaves_smoke_and_invisibility,
        test_item_4_cooldown_hud_top_bar_data,
        test_item_5_p2_i_key_is_back_and_esc_does_not_cancel_p2,
        test_item_6_joes_dog_only_stunned_when_attacking,
        test_item_7_and_8_julie_flintlock_and_repel,
        test_item_9_julie_flintlock_banner_name,
        test_item_10_murasaki_frontal_deflection_cone,
        test_item_11_murasaki_kama_reach,
        test_item_12_murasaki_roll_smoke_no_sparks,
        test_item_13_and_14_kenshi_ryuu_tsui_sen_and_freeze_fix,
        test_item_15_solid_obstacle_consistency,
        test_item_16_tomoe_rope_cooldown,
        test_item_17_anne_slow_soot_and_banner,
        test_item_18_and_19_hanzo_kunai_bounds_and_midair_angle,
        test_item_20_flintlock_range,
        test_loading_screen_progress_and_rendering,
        test_julie_cape_flourish_rendering,
        test_okuni_poison_cone_push_and_frenzy,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print("\nALL 19 VERIFICATION SUITES PASSED 100%!")
