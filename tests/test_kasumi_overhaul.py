"""
Testes de Regressão e Validação da Fase 2 Overhaul: Kasumi (Sub-fase 2.8)
Verifica os 12 entregáveis:
1. Paleta, Materiais PBR e Cachecol Shinobi sem vazamento de pele no pescoço/mandíbula
2. Cinemática Articulada Modular (get_arms) e 12 poses da Fase 2
3. Golpe Primário Híbrido: Adaga Tanto (<= 1.6m / 2 Dano / Clash) vs Bomba Horoku (> 1.6m em arco 3D)
4. Ação Secundária: Mina de Detonação Remota (1º toque planta, 2º toque detona)
5. Proteção de Auto-Dano da Mina: Imunidade a suicídio se Kasumi tiver 1 HP
6. Esquiva Furtiva: Rolo de fumaça ágil (14 i-frames, alpha=15, nós de névoa)
7. Finisher A: Moujin Shundan (霧刃瞬断 — Decapitação limpa com adaga Tanto)
8. Finisher B: Bakuen Funsai (爆炎粉砕 — Cataclismo pirotécnico em 26+ pedaços)
9. Roteiro de Intro em 3 fases (drop_shinobi -> fuse_draw -> mist_stance) com beats
10. Roteiro de Vitória em 3 fases (chiburi_sheath -> smoke_drop -> mist_vanish) com beats
11. Integração no Model Inspector (De/Para, Botões de animação e alias)
12. Integração no Manual de Ajuda do Jogo (game_help.py)
"""
import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

from src.entities.gray_ninja import GrayNinja
from src.entities.red_samurai import RedSamurai
from src.entities import kasumi_model
from src.entities.projectile import TimedBombEntity, RemoteMineEntity
from src.entities.voxel_corpse import VoxelCorpse
from src.entities import pose_scripts
from src.combat.collision import CombatSystem, _get_death_style_for_attacker
from src.effects.cinematic_director import CinematicDirector
from tools.model_inspector import CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES
from src.ui.game_help import FIGHTERS_GUIDE_DATA
from src.config import CHAR_GRAY


class DummyCamera:
    azimuth = 0.0
    elevation = math.radians(35.0)
    zoom = 1.0

    def apply(self, x, y, z=0.0):
        return int(x * 50), int(y * 50 - z * 50)

    def add_shake(self, amount):
        pass


class DummyMap:
    bamboos = []
    rocks = []
    well = None
    pits = []


class DummyModelContext:
    def __init__(self, state="IDLE", atk_prog=0.0, extra=None):
        self.surface = pygame.Surface((100, 100))
        self.camera = DummyCamera()
        self.base_x, self.base_y, self.base_z = 0.0, 0.0, 0.0
        self.torso_z = 0.50
        self.head_z = 0.85
        self.pelvis_z = 0.40
        self.pelvis_w = 0.22
        self.pelvis_d = 0.16
        self.head_w = 0.20
        self.neck_z = 0.76
        self.fx, self.fy = 1.0, 0.0
        self.px, self.py = 0.0, 1.0
        self.state = state
        self.atk_progress = atk_prog
        self.is_melee = (state == "ATTACK")
        self.is_moving = False
        self.walk_timer = 0.0
        self.alpha = 255
        self.extra_props = extra or {}
        self.legs_data = {
            "L": {"thigh": (0.0, 0.05, 0.2), "shin": (0.0, 0.05, 0.1), "foot": (0.0, 0.05, 0.0)},
            "R": {"thigh": (0.0, -0.05, 0.2), "shin": (0.0, -0.05, 0.1), "foot": (0.0, -0.05, 0.0)},
        }


def test_01_materials_and_palette():
    """Valida materiais PBR, modo de compatibilidade e ausência de vazamento de pele na gola."""
    mats = kasumi_model.MATERIALS
    assert mats["scarf"] == "canvas"
    assert mats["torso"] == "leather"
    assert mats["chrome"] == "chrome"
    assert mats["blade"] == "steel"

    legacy_mats = kasumi_model.LEGACY_MATERIALS
    assert legacy_mats["scarf"] == "matte"
    assert legacy_mats["blade"] == "matte"

    pal = kasumi_model.pal()
    assert pal["neck"] == pal["scarf"], "neck deve herdar cor do cachecol para evitar vazamento de pele sob a gola"
    assert pal["jaw"] == pal["scarf"], "jaw deve herdar cor do cachecol para evitar queixo de pele exposto sob a máscara"
    print("Test 1 PASS: Materiais PBR e Gola Shinobi sem vazamento.")


def test_02_kinematics_and_get_arms():
    """Valida cinemática modular get_arms para as poses da Fase 2."""
    c = DummyModelContext()
    arm_l, arm_r = kasumi_model.get_arms(c)
    assert len(arm_l) == 3 and len(arm_r) == 3

    poses = [
        "tanto_slash", "bomb_throw", "plant_mine", "smoke_roll",
        "drop_shinobi", "fuse_draw", "mist_stance",
        "chiburi_sheath", "smoke_drop", "mist_vanish",
        "finisher_tanto", "finisher_bomb"
    ]
    coords = set()
    for p_name in poses:
        ctx = DummyModelContext(extra={"pose": p_name, "p": 0.5})
        al, ar = kasumi_model.get_arms(ctx)
        sig = (round(al[0], 2), round(al[1], 2), round(al[2], 2),
               round(ar[0], 2), round(ar[1], 2), round(ar[2], 2))
        assert sig not in coords, f"Pose {p_name} gerou cinemática duplicada"
        coords.add(sig)
    print("Test 2 PASS: get_arms e 12 poses articuladas com cinemática única.")


def test_03_primary_hybrid_strike():
    """Valida o sistema híbrido de ataque: Tanto à queima-roupa e Horoku à distância."""
    k = GrayNinja(0.0, 0.0)
    projs = []

    # 1. Curta distância (<= 1.6m): golpe de Adaga Tanto
    res_melee = k.trigger_hybrid_attack(1.2, 0.0, projectiles=projs)
    assert res_melee == "tanto"
    assert k.state == "ATTACK"
    assert k.hitbox_radius == 1.20
    assert k.hitbox_damage == 2
    assert len(projs) == 0

    # 2. Média/longa distância (> 1.6m): bomba Horoku
    k.state = "IDLE"
    k.bomb_timer = 0.0
    res_ranged = k.trigger_hybrid_attack(3.5, 0.0, projectiles=projs)
    assert res_ranged == "bomb"
    assert len(projs) == 1
    assert isinstance(projs[0], TimedBombEntity)
    assert k.bomb_cooldown == 2.0
    assert k.bomb_timer == 2.0

    # 3. Durante cooldown (2.0s) ou com 1 bomba ativa: fallback para golpe Tanto à distância
    k.state = "IDLE"
    res_fallback = k.trigger_hybrid_attack(3.5, 0.0, projectiles=projs)
    assert res_fallback == "tanto"
    assert len(projs) == 1, "Não deve permitir mais de 1 bomba ativa ao mesmo tempo!"

    print("Test 3 PASS: Sistema híbrido Tanto (<= 1.6m) vs Horoku (> 1.6m) com cooldown 2.0s e limite de 1 bomba.")


def test_04_remote_mine_plant_and_detonate():
    """Valida o ciclo da mina remota: 1º toque planta, 2º toque detona após delay de armamento."""
    k = GrayNinja(0.0, 0.0)
    projs = []
    gmap = DummyMap()

    # 1º toque: Planta a mina no solo
    ok_plant = k.trigger_remote_mine(projectiles=projs)
    assert ok_plant is True
    assert k.planted_mine is not None
    assert len(projs) == 1
    mine = projs[0]
    assert isinstance(mine, RemoteMineEntity)
    assert mine.is_active is True

    # 2º toque imediato antes de armar: não detona
    ok_det_early = k.trigger_remote_mine(fighters=[k])
    assert ok_det_early is False
    assert mine.is_active is True

    # Avança tempo para armar
    mine.update(0.35, gmap)
    assert mine.is_ready_to_detonate() is True

    # 2º toque após armamento: detona com sucesso
    ok_det = k.trigger_remote_mine(fighters=[k])
    assert ok_det is True
    assert mine.is_active is False
    assert k.planted_mine is None
    print("Test 4 PASS: Mina Remota ciclo de planto e detonação.")


def test_05_remote_mine_self_damage_protection():
    """Valida que Kasumi não se auto-elimina com a mina se estiver com <= 1 HP."""
    k = GrayNinja(0.0, 0.0)
    k.hp = 1
    rival = RedSamurai(0.5, 0.0)
    rival.hp = 2

    mine = RemoteMineEntity(0.0, 0.0, owner=k)
    mine.age = 0.5
    assert mine.is_ready_to_detonate()

    mine.detonate(fighters=[k, rival])
    assert k.is_alive is True, "Kasumi não deve morrer para a própria mina quando em 1 HP"
    assert k.hp == 1
    assert rival.hp == 0
    assert rival.is_alive is False
    print("Test 5 PASS: Imunidade a suicídio com mina remota a 1 HP.")


def test_06_smoke_roll_dodge_and_stealth():
    """Valida a esquiva ágil com rolo de fumaça, i-frames e camuflagem."""
    k = GrayNinja(0.0, 0.0)
    ok_roll = k.trigger_roll(1.0, 0.0)
    assert ok_roll is True
    assert k.state == "ROLL"
    assert k.alpha == 15, "Deve entrar em alta transparência (alpha=15)"
    assert k.stealth_timer == 1.0
    assert k.roll_duration == 0.28
    assert k.roll_speed == 9.5
    assert len(k.fog_nodes) >= 1
    print("Test 6 PASS: Esquiva Rolo de Fumaça com camuflagem furtiva.")


def test_07_finisher_a_moujin_shundan():
    """Valida o Finisher A: Moujin Shundan (decapitação limpa com Tanto)."""
    k = GrayNinja(0.0, 0.0)
    target = RedSamurai(1.0, 0.0)
    style = _get_death_style_for_attacker(k, weapon="tanto")
    assert style == "MOUJIN_SHUNDAN"

    corpse = VoxelCorpse(target, "MOUJIN_SHUNDAN", (1.0, 0.0))
    assert hasattr(corpse, "headless_body") and corpse.headless_body is not None
    assert hasattr(corpse, "severed_head") and corpse.severed_head is not None
    print("Test 7 PASS: Finisher A Moujin Shundan decapitação limpa.")


def test_08_finisher_b_bakuen_funsai():
    """Valida o Finisher B: Bakuen Funsai (cataclismo pirotécnico em 26+ pedaços)."""
    k = GrayNinja(0.0, 0.0)
    target = RedSamurai(1.0, 0.0)
    style = _get_death_style_for_attacker(k, weapon="bomb")
    assert style == "BAKUEN_FUNSAI"

    corpse = VoxelCorpse(target, "BAKUEN_FUNSAI", (1.0, 0.0))
    gibs = [p for p in corpse.pieces if getattr(p, "piece_type", "") == "gib"]
    assert len(gibs) >= 26, f"Esperado >= 26 fragmentos de explosão, obteve {len(gibs)}"
    print("Test 8 PASS: Finisher B Bakuen Funsai 26+ pedaços de explosão.")


def test_09_intro_script_and_beats():
    """Valida o roteiro de Intro de 3 fases e beats audiovisuais de Kasumi."""
    f1 = pose_scripts.sample("kasumi", "intro", 0.15)
    assert f1.extra.get("pose") == "drop_shinobi"

    f2 = pose_scripts.sample("kasumi", "intro", 0.50)
    assert f2.extra.get("pose") == "fuse_draw"

    f3 = pose_scripts.sample("kasumi", "intro", 0.85)
    assert f3.extra.get("pose") == "mist_stance"

    beats = pose_scripts.BEATS["intro"]["kasumi"]
    events = [b[1] for b in beats]
    assert "sfx:dodge_whoosh" in events
    assert "sfx:bomb_fuse" in events
    assert "sfx:sword_slash" in events
    print("Test 9 PASS: Intro de 3 fases com beats sonoros.")


def test_10_victory_script_and_beats():
    """Valida o roteiro de Vitória de 3 fases e beats audiovisuais de Kasumi."""
    f1 = pose_scripts.sample("kasumi", "victory", 0.15)
    assert f1.extra.get("pose") == "chiburi_sheath"

    f2 = pose_scripts.sample("kasumi", "victory", 0.50)
    assert f2.extra.get("pose") == "smoke_drop"

    f3 = pose_scripts.sample("kasumi", "victory", 0.85)
    assert f3.extra.get("pose") == "mist_vanish"
    assert f3.alpha < 1.0, "Fase 3 deve desvanecer alfa na névoa"

    beats = pose_scripts.BEATS["victory"]["kasumi"]
    events = [b[1] for b in beats]
    assert "sfx:sword_slash" in events
    assert "sfx:smoke_puff" in events
    assert "fx:smoke" in events
    print("Test 10 PASS: Vitória de 3 fases com beats e dissolução na névoa.")


def test_11_model_inspector_registration():
    """Valida o registro de Kasumi no Model Inspector (De/Para e Botões)."""
    assert "kasumi" in CHARACTER_ANIM_BUTTONS
    assert "gray" in CHARACTER_ANIM_BUTTONS
    buttons = CHARACTER_ANIM_BUTTONS["kasumi"]
    btn_keys = [b[0] for b in buttons]
    assert "TANTO_SLASH" in btn_keys
    assert "HOROKU_BOMB" in btn_keys
    assert "REMOTE_MINE" in btn_keys
    assert "SMOKE_ROLL" in btn_keys
    assert "FINISHER_1" in btn_keys
    assert "FINISHER_2" in btn_keys

    assert "kasumi" in OVERHAUL_DE_PARA_NOTES
    assert "gray" in OVERHAUL_DE_PARA_NOTES
    notes = OVERHAUL_DE_PARA_NOTES["kasumi"]
    assert len(notes) >= 6
    print("Test 11 PASS: Model Inspector catalogado com De/Para e botões de animação.")


def test_12_game_help_card():
    """Valida os dados atualizados de Kasumi no Manual de Ajuda do Jogo (game_help.py)."""
    kasumi_card = next((entry for entry in FIGHTERS_GUIDE_DATA if entry.get("id") == CHAR_GRAY), None)
    assert kasumi_card is not None
    assert "Tanto" in kasumi_card["pt"]["keys_p1"]
    assert "Mina Remota" in kasumi_card["pt"]["keys_p2"]
    assert "Tanto" in kasumi_card["en"]["keys_p1"]
    assert "Remote Mine" in kasumi_card["en"]["keys_p2"]
    print("Test 12 PASS: Manual de Ajuda atualizado em PT e EN.")


if __name__ == "__main__":
    test_01_materials_and_palette()
    test_02_kinematics_and_get_arms()
    test_03_primary_hybrid_strike()
    test_04_remote_mine_plant_and_detonate()
    test_05_remote_mine_self_damage_protection()
    test_06_smoke_roll_dodge_and_stealth()
    test_07_finisher_a_moujin_shundan()
    test_08_finisher_b_bakuen_funsai()
    test_09_intro_script_and_beats()
    test_10_victory_script_and_beats()
    test_11_model_inspector_registration()
    test_12_game_help_card()
    print("\nALL 12 KASUMI OVERHAUL TESTS PASSED SUCCESSFULLY! ✅")
