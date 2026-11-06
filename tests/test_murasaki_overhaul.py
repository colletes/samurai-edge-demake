"""
Testes de Regressão e Validação da Fase 2 Overhaul: Murasaki (Sub-fase 2.7)
Verifica os 11 entregáveis:
1. Paleta, Materiais Físicos e Máscara Shinobi sem vazamento de pele no pescoço/mandíbula
2. Cinemática Articulada Modular (get_arms) e 11 poses
3. Golpe Primário: Kama Strike (1.30m de alcance, precedência e clash)
4. Ação Secundária: Chain Drag (3.80m, Dano 1 + Puxão + Stun 0.45s)
5. Finisher A: Kamaitachi Chain Decap (三弦微塵)
6. Finisher B: Senpuu Chain Shred Tornado (旋風爆砕)
7. Esquiva: Chain Whirl Backflip (360° com deflexão de projéteis leves)
8. Corpse Physics: VoxelCorpse para Finisher A e Finisher B
9. Roteiros de Intro e Vitória em 3 fases com beats audiovisuais
10. Integração no Model Inspector e Ajuda do Jogo
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

from src.entities.purple_ninja import PurpleNinja
from src.entities.red_samurai import RedSamurai
from src.entities import murasaki_model
from src.entities.projectile import KusarigamaChainEntity, KunaiProjectile, ShurikenProjectile, OfudaProjectile
from src.entities.voxel_corpse import VoxelCorpse
from src.entities import pose_scripts
from src.combat.collision import CombatSystem, _get_death_style_for_attacker
from src.effects.cinematic_director import CinematicDirector
from tools.model_inspector import CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES
from src.ui.game_help import FIGHTERS_GUIDE_DATA
from src.config import CHAR_PURPLE


class DummyCamera:
    azimuth = 0.0
    elevation = math.radians(35.0)

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
        self.head_w = 0.20
        self.fx, self.fy = 1.0, 0.0
        self.px, self.py = 0.0, 1.0
        self.state = state
        self.atk_progress = atk_prog
        self.is_melee = (state == "ATTACK")
        self.is_moving = False
        self.walk_timer = 0.0
        self.alpha = 255
        self.extra_props = extra or {}


def test_01_murasaki_palette_and_materials():
    """1. Paleta, Materiais Físicos e Máscara Shinobi sem vazamento de pele."""
    pal = murasaki_model.pal()
    assert "suit" in pal and "wrap" in pal and "blade" in pal and "chain" in pal
    assert "ball" in pal and "mask" in pal
    # Diretriz de Máscara Shinobi: neck e jaw devem ter a cor da máscara para evitar vazamento de pele
    assert pal["neck"] == pal["mask"]
    assert pal["jaw"] == pal["mask"]
    assert murasaki_model.MATERIALS["suit"] == "latex"
    assert murasaki_model.MATERIALS["blade"] == "steel"
    assert murasaki_model.MATERIALS["ball"] == "metal"
    assert murasaki_model.LEGACY_MATERIALS["suit"] == "matte"


def test_02_modular_get_arms():
    """2. Cinemática Articulada Modular (get_arms)."""
    c = DummyModelContext()
    left, right = murasaki_model.get_arms(c)
    assert len(left) == 3 and len(right) == 3
    # A mão direita empunha a foice (Kama), a mão esquerda empunha a corrente
    assert isinstance(left[0], float) and isinstance(right[0], float)


def test_03_hands_kinematics_all_poses():
    """3. Cinemática em todas as 11 poses chave."""
    poses = [
        "kama_strike", "chain_drag", "chain_whirl_backflip",
        "finger_spin", "palm_catch", "kunoichi_stance",
        "chain_reel", "kama_rest", "shadow_vanish",
        "finisher_decap", "finisher_tornado_shred"
    ]
    for pose_name in poses:
        c = DummyModelContext(extra={"pose": pose_name, "p": 0.5})
        right, left = murasaki_model._hands(c)
        assert len(right) == 3 and len(left) == 3
        assert not math.isnan(right[0]) and not math.isnan(left[0])


def test_04_primary_strike_kama_reach():
    """4. Golpe Primário: Kama Strike (1.30m de alcance, precedência e clash)."""
    murasaki = PurpleNinja(0.0, 0.0)
    assert murasaki.can_act()
    res = murasaki.trigger_kama_strike(1.0, 0.0)
    assert res is True
    assert murasaki.state == "ATTACK"
    assert murasaki.hitbox_radius == 1.50


def test_05_secondary_action_chain_drag_properties():
    """5. Ação Secundária: Chain Drag (alcance calibrado para 3.80m)."""
    murasaki = PurpleNinja(0.0, 0.0)
    chain = KusarigamaChainEntity(0.0, 0.0, 0.4, 1.0, 0.0, owner=murasaki)
    assert chain.max_reach == 3.80
    assert chain.speed == 17.0
    assert chain.state == "FLYING"


def test_06_chain_drag_damage_and_stun():
    """6. Chain Drag causa 1 de dano, puxa o oponente e aplica 0.45s de stun."""
    combat = CombatSystem()
    murasaki = PurpleNinja(0.0, 0.0)
    target = RedSamurai(2.5, 0.0)
    target.hp = 2

    chain = KusarigamaChainEntity(2.4, 0.0, 0.4, 1.0, 0.0, owner=murasaki)
    particles = []
    banners = []
    g_map = DummyMap()
    cam = DummyCamera()

    combat.process_combat(murasaki, target, g_map, particles, banners, cam, [chain], dt=0.016)

    assert target.hp == 1
    assert target.state == "STUNNED"
    assert target.state_timer >= 0.40
    assert chain.state == "HOOKED_PULLING"


def test_07_chain_drag_fatal_finisher_b():
    """7. Chain Drag contra rival com 1 HP restante desencadeia o Finisher B (Senpuu Chain Shred)."""
    combat = CombatSystem()
    director = CinematicDirector()
    murasaki = PurpleNinja(0.0, 0.0)
    target = RedSamurai(2.5, 0.0)
    target.hp = 1

    chain = KusarigamaChainEntity(2.4, 0.0, 0.4, 1.0, 0.0, owner=murasaki)
    particles = []
    banners = []
    g_map = DummyMap()
    cam = DummyCamera()

    combat.process_combat(murasaki, target, g_map, particles, banners, cam, [chain], dt=0.016, cinematic_director=director)

    assert not target.is_alive
    assert director.is_active
    assert director.finisher_style == "SENPUU_CHAIN_SHRED"
    assert director.current_kanji_text == "旋風爆砕"


def test_08_kama_melee_fatal_finisher_a():
    """8. Golpe fatal melee com a foice Kama desencadeia o Finisher A (Kamaitachi Chain Decap)."""
    murasaki = PurpleNinja(0.0, 0.0)
    style = _get_death_style_for_attacker(murasaki, weapon="kama")
    assert style == "KAMAITACHI_CHAIN_DECAP"

    director = CinematicDirector()
    target = RedSamurai(1.0, 0.0)
    director.trigger_fatal_strike(murasaki, target, style, (1.0, 0.0))
    assert director.is_active
    assert director.current_kanji_text == "三弦微塵"


def test_09_backflip_dodge_projectile_deflection():
    """9. Chain Whirl Backflip (esquiva 360°) deflete e destrói projéteis leves sem reflexão."""
    combat = CombatSystem()
    murasaki = PurpleNinja(0.0, 0.0)
    rival = RedSamurai(3.0, 0.0)

    # Aciona esquiva ativa (Chain Whirl Backflip)
    assert murasaki.trigger_roll(-1.0, 0.0) is True
    assert murasaki.state == "ROLL"
    assert murasaki.is_invulnerable_dodge is True

    kunai = KunaiProjectile(0.2, 0.0, 0.4, -1.0, 0.0, owner=rival)
    shuriken = ShurikenProjectile(0.2, 0.0, 0.4, -1.0, 0.0, owner=rival)
    ofuda = OfudaProjectile(0.2, 0.0, 0.4, -1.0, 0.0, owner=rival, element="wood")

    # Verifica deflexão direta pelo escudo giratório da corrente
    evaded_kunai = combat.check_projectile_dodge_evasion(kunai, murasaki)
    assert evaded_kunai is True
    assert not kunai.is_active

    evaded_shuriken = combat.check_projectile_dodge_evasion(shuriken, murasaki)
    assert evaded_shuriken is True
    assert not shuriken.is_active

    evaded_ofuda = combat.check_projectile_dodge_evasion(ofuda, murasaki)
    assert evaded_ofuda is True
    assert not ofuda.is_active


def test_10_voxel_corpse_finisher_a_and_b():
    """10. VoxelCorpse para Finisher A (Decapitação) e Finisher B (Tornado Shred de Tronco)."""
    target = RedSamurai(0.0, 0.0)

    # Finisher A: Kamaitachi Chain Decap
    corpse_a = VoxelCorpse(target, "KAMAITACHI_CHAIN_DECAP", (1.0, 0.0))
    piece_types_a = [p.piece_type for p in corpse_a.pieces]
    assert "body" in piece_types_a
    assert "head" in piece_types_a

    # Finisher B: Senpuu Chain Shred
    corpse_b = VoxelCorpse(target, "SENPUU_CHAIN_SHRED", (1.0, 0.0))
    piece_types_b = [p.piece_type for p in corpse_b.pieces]
    assert "legs" in piece_types_b
    assert "head" in piece_types_b
    assert piece_types_b.count("gib") >= 6


def test_11_pose_scripts_intro_victory():
    """11. Roteiros de Intro e Vitória em 3 fases dinâmicas com beats audiovisuais."""
    # Intro
    f0 = pose_scripts.sample("murasaki", "intro", 0.15)
    f1 = pose_scripts.sample("murasaki", "intro", 0.50)
    f2 = pose_scripts.sample("murasaki", "intro", 0.85)
    assert f0.extra.get("pose") == "finger_spin"
    assert f1.extra.get("pose") == "palm_catch"
    assert f2.extra.get("pose") == "kunoichi_stance"

    # Vitória
    v0 = pose_scripts.sample("murasaki", "victory", 0.20)
    v1 = pose_scripts.sample("murasaki", "victory", 0.55)
    v2 = pose_scripts.sample("murasaki", "victory", 0.85)
    assert v0.extra.get("pose") == "chain_reel"
    assert v1.extra.get("pose") == "kama_rest"
    assert v2.extra.get("pose") == "shadow_vanish"

    # Beats
    intro_beats = [b[1] for b in pose_scripts.BEATS["intro"]["murasaki"]]
    assert "sfx:chain_spin" in intro_beats
    assert "sfx:parry" in intro_beats

    victory_beats = [b[1] for b in pose_scripts.BEATS["victory"]["murasaki"]]
    assert "sfx:chain_spin" in victory_beats
    assert "fx:smoke" in victory_beats


def test_12_model_inspector_and_game_help_integration():
    """12. Registro no Model Inspector e Ajuda do Jogo."""
    assert "murasaki" in CHARACTER_ANIM_BUTTONS
    assert "purple" in CHARACTER_ANIM_BUTTONS
    buttons = [btn[0] for btn in CHARACTER_ANIM_BUTTONS["murasaki"]]
    assert "KAMA_STRIKE" in buttons
    assert "CHAIN_DRAG" in buttons
    assert "BACKFLIP" in buttons
    assert "FINISHER_1" in buttons
    assert "FINISHER_2" in buttons

    assert "murasaki" in OVERHAUL_DE_PARA_NOTES
    assert len(OVERHAUL_DE_PARA_NOTES["murasaki"]) >= 5

    # Ajuda do Jogo
    manual_entry = next((e for e in FIGHTERS_GUIDE_DATA if e.get("id") == CHAR_PURPLE), None)
    assert manual_entry is not None
    assert "Kama Strike" in manual_entry["pt"]["habilidades"]
    assert "Chain Drag" in manual_entry["pt"]["habilidades"]
    assert "Chain Whirl Backflip" in manual_entry["pt"]["habilidades"]


if __name__ == "__main__":
    test_01_murasaki_palette_and_materials()
    test_02_modular_get_arms()
    test_03_hands_kinematics_all_poses()
    test_04_primary_strike_kama_reach()
    test_05_secondary_action_chain_drag_properties()
    test_06_chain_drag_damage_and_stun()
    test_07_chain_drag_fatal_finisher_b()
    test_08_kama_melee_fatal_finisher_a()
    test_09_backflip_dodge_projectile_deflection()
    test_10_voxel_corpse_finisher_a_and_b()
    test_11_pose_scripts_intro_victory()
    test_12_model_inspector_and_game_help_integration()
    print("ALL 12 MURASAKI KUSARIGAMA OVERHAUL TESTS PASSED SUCCESSFULLY! ✅")
