"""
Suíte de testes de integração e mecânicas do Overhaul do Hanzo (Sub-fase 2.3 — Iga Ninjutsu).
Verifica os 11 entregáveis de padrão idêntico ao de Kenshi e Musashi:
1. Combo Melee 2 tempos com Ninjato invertida (Reverse Slash + Solar Plexus Thrust com avanço).
2. Kunai Snipe de alta precisão (horizontal no solo e mergulho íngreme vz=-6.5 no ar).
3. Salto Ninja Acrobático Parabólico com checagem de altura 3D (golpes baixos passam por baixo).
4. Landing Cancel: cancelamento ofensivo nos 40% finais da aterrissagem em estocada rápida.
5. Anti-Floating Mandate: queda imediata no solo (wz = 0.0) se sofrer parry no ar.
6. Finisher 1: HEART_THROAT_STAB (短刀急所) com fonte arterial volumétrica.
7. Finisher 2: FOREHEAD_PIN (苦無眉間) com kunai cravada na testa.
8. Rig 3D, Bainha das costas vazia ao sacar a Ninjato, LEGACY_MATERIALS e Olhos Marciais Ambarinos HD.
9. SSAA 2x offscreen buffer e Pose LERP 0.08s contínua.
10. Model Inspector com modo De/Para e 12 botões interativos de teste.
11. Manual dos guerreiros (Game Help) atualizado em PT/EN.
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
pygame.display.set_mode((800, 600))

from src.entities.yellow_ninja import YellowNinja
from src.entities.blue_samurai import BlueSamurai
from src.entities import hanzo_model, pose_scripts
from src.entities.projectile import KunaiProjectile
from src.entities.voxel_corpse import VoxelCorpse, STUCK_WEAPON
from src.effects.cinematic_director import CinematicDirector
from src.isometric.camera import Camera
from src.combat.collision import _is_vertical_hit
from tools.model_inspector import CHARACTER_ANIM_BUTTONS, OVERHAUL_DE_PARA_NOTES, ModelInspector
from src.ui.game_help import FIGHTERS_GUIDE_DATA


class DummyMap:
    def __init__(self):
        self.cols = 20
        self.rows = 20
        self.rocks = []
        self.well = None
        self.bamboos = []
        self.destructibles = []

    def is_tile_walkable(self, tx, ty):
        return True

    def is_hidden_in_bamboo(self, wx, wy):
        return False


def test_hanzo_initialization():
    """Testa atributos base e estado do Hanzo overhaul."""
    hanzo = YellowNinja(10.0, 10.0)
    assert hanzo.char_type == "ninja"
    assert hanzo.speed == 5.4
    assert hanzo.ssaa_enabled is True
    assert hasattr(hanzo, "_pose_lerp_tracker")
    assert hanzo._pose_lerp_tracker["lerp_duration"] == 0.08
    assert hanzo.combo_step == 0
    assert hanzo.has_kunai is True
    assert hanzo.kunai_cooldown == 1.5


def test_hanzo_two_step_combo():
    """Testa o combo ágil de 2 tempos com Ninjato (Reverse Slash + Solar Plexus Thrust)."""
    hanzo = YellowNinja(10.0, 10.0)
    game_map = DummyMap()

    # Passo 1: Reverse Slash
    hanzo.trigger_combo_attack(12.0, 10.0)
    assert hanzo.state == "ATTACK"
    assert hanzo.combo_step == 1
    assert hanzo.hitbox_active is True
    assert hanzo.hitbox_radius == 1.30
    assert hanzo.hitbox_damage == 1

    # Buffer do segundo golpe durante o primeiro
    hanzo.trigger_combo_attack(12.0, 10.0)
    assert hanzo.combo_buffered is True

    # Avançar até transição automática para o passo 2
    hanzo.update(0.12, game_map)
    assert hanzo.state == "ATTACK"
    assert hanzo.combo_step == 2
    assert hanzo.hitbox_radius == 1.45
    assert hanzo.hitbox_damage == 2


def test_hanzo_kunai_snipe_ground_and_air():
    """Testa o Kunai Snipe no solo (horizontal) e no ar (mergulho íngreme vz=-6.5)."""
    hanzo = YellowNinja(10.0, 10.0)
    projectiles = []

    # Disparo no solo
    assert hanzo.has_kunai is True
    success = hanzo.trigger_kunai_snipe(12.0, 10.0, projectiles)
    assert success is True
    assert hanzo.has_kunai is False
    assert len(projectiles) == 1
    kunai_ground = projectiles[0]
    assert isinstance(kunai_ground, KunaiProjectile)
    assert kunai_ground.vz == 0.0

    # Recarregar kunai
    hanzo.has_kunai = True

    # Salto Ninja
    hanzo.trigger_jump(1.0, 0.0)
    assert hanzo.state == "JUMP"
    hanzo.wz = 1.0  # Simula ápice do salto

    # Disparo em pleno ar
    success_air = hanzo.trigger_kunai_snipe(12.0, 10.0, projectiles)
    assert success_air is True
    assert len(projectiles) == 2
    kunai_air = projectiles[1]
    assert kunai_air.vz == -6.5


def test_hanzo_shinobi_jump_and_vertical_evasion():
    """Testa o salto parabólico (wz até 1.35m) e a checagem vertical 3D contra ataques rasteiros."""
    hanzo = YellowNinja(10.0, 10.0)
    musashi = BlueSamurai(10.5, 10.0)

    # Hanzo salta
    hanzo.trigger_jump(1.0, 0.0)
    hanzo.wz = 0.85  # No ar acima de 0.40m

    # Musashi tenta golpear do solo (wz = 0.0)
    musashi.wz = 0.0
    # Golpes no solo (att_wz < 0.30) NÃO devem acertar alvos no ar (def_wz >= 0.40m)
    hit_connects = _is_vertical_hit(musashi, hanzo)
    assert hit_connects is False, "Golpe no solo não deve atingir ninja no ar durante o salto!"

    # Quando Hanzo toca o chão (wz = 0.15), o golpe conecta normalmente
    hanzo.wz = 0.15
    assert _is_vertical_hit(musashi, hanzo) is True


def test_hanzo_landing_cancel():
    """Testa o cancelamento ofensivo nos 40% finais da aterrissagem em corte rápido."""
    hanzo = YellowNinja(10.0, 10.0)
    hanzo.trigger_jump(1.0, 0.0)
    assert hanzo.state == "JUMP"

    # Simular que está nos 30% finais do salto
    hanzo.state_timer = hanzo.jump_duration * 0.30
    assert hanzo.can_cancel_jump() is True

    # Pressionar ataque cancela a aterrissagem em estocada rápida imediata
    canceled = hanzo.trigger_combo_attack(12.0, 10.0)
    assert canceled is True
    assert hanzo.state == "ATTACK"
    assert hanzo.combo_step == 2
    assert hanzo.is_landing_cancel is True
    assert hanzo.wz == 0.0


def test_hanzo_anti_floating_on_parry():
    """Diretiva Crítica: Se o ninja for parriado no ar, cai imediatamente no solo (wz = 0.0)."""
    hanzo = YellowNinja(10.0, 10.0)
    hanzo.trigger_jump(1.0, 0.0)
    hanzo.wz = 1.20
    assert hanzo.wz > 0.0

    # Sofre parry no ar
    hanzo.on_parried()

    # Deve cair imediatamente com wz = 0.0 e entrar em atordoamento
    assert hanzo.wz == 0.0
    assert hanzo.state == "STUNNED"
    assert hanzo.combo_step == 0


def test_hanzo_fatalities_corpse():
    """Testa os dois Finishers bespoke e peças de cadáver associadas."""
    # 1. HEART_THROAT_STAB na tabela STUCK_WEAPON
    assert "HEART_THROAT_STAB" in STUCK_WEAPON
    assert STUCK_WEAPON["HEART_THROAT_STAB"] == "blade"
    assert "FOREHEAD_PIN" in STUCK_WEAPON
    assert STUCK_WEAPON["FOREHEAD_PIN"] == "kunai"

    # 2. Cinematic Director Kanji
    cd = CinematicDirector()
    cd._build_kanji_overlay(None, None, "HEART_THROAT_STAB")
    assert cd.current_kanji_text == "短刀急所"
    assert "TANTOU KYUUSHO" in cd.current_kanji_subtitle

    cd._build_kanji_overlay(None, None, "FOREHEAD_PIN")
    assert cd.current_kanji_text == "苦無眉間"
    assert "KUNAI MIKEN" in cd.current_kanji_subtitle

    # 3. VoxelCorpse para ambos os golpes
    victim = BlueSamurai(10.0, 10.0)
    corpse_throat = VoxelCorpse(victim, "HEART_THROAT_STAB", (1.0, 0.0))
    assert len(corpse_throat.blood_droplets) >= 30

    corpse_pin = VoxelCorpse(victim, "FOREHEAD_PIN", (1.0, 0.0))
    assert len(corpse_pin.blood_droplets) >= 20


def test_hanzo_3d_model_and_sword_sheath_state():
    """Testa a lógica da bainha vazia nas costas quando a Ninjato é sacada na mão."""
    class DummyContext:
        def __init__(self, is_melee=False, pose=""):
            self.is_melee = is_melee
            self.extra_props = {"pose": pose}

    # Desembainhada durante combate melee
    c_melee = DummyContext(is_melee=True)
    assert hanzo_model.is_sword_drawn(c_melee) is True

    # Desembainhada em pose de saque/guarda
    c_draw = DummyContext(pose="ninjato_draw")
    assert hanzo_model.is_sword_drawn(c_draw) is True

    c_stance = DummyContext(pose="shinobi_stance")
    assert hanzo_model.is_sword_drawn(c_stance) is True

    # Embainhada nas costas em Idle/Walk comum
    c_idle = DummyContext(is_melee=False, pose="")
    assert hanzo_model.is_sword_drawn(c_idle) is False

    # Materiais e paletas
    assert hasattr(hanzo_model, "LEGACY_MATERIALS")
    assert hasattr(hanzo_model, "MATERIALS")
    assert hasattr(hanzo_model, "LEGACY_PALETTE")


def test_hanzo_intro_victory_and_model_inspector():
    """Testa sequências de intro, vitória e registro completo no Model Inspector."""
    # Intro
    intro_segs = pose_scripts.INTRO.get("ninja")
    assert intro_segs is not None
    poses_intro = [s[6].get("pose") for s in intro_segs if s[6].get("pose")]
    assert "leaf_crouch" in poses_intro
    assert "ninjato_draw" in poses_intro
    assert "shinobi_stance" in poses_intro

    # Vitória
    vic_segs = pose_scripts.VICTORY.get("ninja")
    assert vic_segs is not None
    poses_vic = [s[6].get("pose") for s in vic_segs if s[6].get("pose")]
    assert "kuji_kiri" in poses_vic
    assert "smoke_vanish" in poses_vic

    # Model Inspector Catalog
    assert "ninja" in CHARACTER_ANIM_BUTTONS
    buttons = CHARACTER_ANIM_BUTTONS["ninja"]
    b_ids = [b[0] for b in buttons]
    assert "ATTACK_1" in b_ids
    assert "ATTACK_2" in b_ids
    assert "KUNAI_SNIPE" in b_ids
    assert "KUNAI_AERIAL" in b_ids
    assert "SHINOBI_JUMP" in b_ids
    assert "JUMP_CANCEL" in b_ids
    assert "PARRY_RECOIL" in b_ids
    assert "FINISHER_1" in b_ids
    assert "FINISHER_2" in b_ids

    assert "ninja" in OVERHAUL_DE_PARA_NOTES
    notes = OVERHAUL_DE_PARA_NOTES["ninja"]
    assert any("SSAA 2x" in n for n in notes)
    assert any("Ninjato com Empunhadura Invertida" in n for n in notes)
    assert any("Anti-Floating" in n for n in notes)


def test_hanzo_game_help_integration():
    """Testa se o manual dos guerreiros foi atualizado em PT e EN com o novo moveset."""
    hanzo_card = next((c for c in FIGHTERS_GUIDE_DATA if c.get("pt", {}).get("name") == "HANZO"), None)
    assert hanzo_card is not None
    pt = hanzo_card["pt"]
    en = hanzo_card["en"]

    assert "Ninjato" in pt["dano"]
    assert "Kunai Snipe" in pt["dano"]
    assert "Landing Cancel" in pt["especial"]
    assert "Ninjato" in en["dano"]
    assert "Kunai Snipe" in en["dano"]
    assert "Landing Cancel" in en["especial"]


if __name__ == "__main__":
    test_hanzo_initialization()
    print("✓ test_hanzo_initialization passou!")
    test_hanzo_two_step_combo()
    print("✓ test_hanzo_two_step_combo passou!")
    test_hanzo_kunai_snipe_ground_and_air()
    print("✓ test_hanzo_kunai_snipe_ground_and_air passou!")
    test_hanzo_shinobi_jump_and_vertical_evasion()
    print("✓ test_hanzo_shinobi_jump_and_vertical_evasion passou!")
    test_hanzo_landing_cancel()
    print("✓ test_hanzo_landing_cancel passou!")
    test_hanzo_anti_floating_on_parry()
    print("✓ test_hanzo_anti_floating_on_parry passou!")
    test_hanzo_fatalities_corpse()
    print("✓ test_hanzo_fatalities_corpse passou!")
    test_hanzo_3d_model_and_sword_sheath_state()
    print("✓ test_hanzo_3d_model_and_sword_sheath_state passou!")
    test_hanzo_intro_victory_and_model_inspector()
    print("✓ test_hanzo_intro_victory_and_model_inspector passou!")
    test_hanzo_game_help_integration()
    print("✓ test_hanzo_game_help_integration passou!")
    print("\nTODOS OS 10 TESTES DO OVERHAUL DO HANZO PASSARAM COM 100% DE SUCESSO!")
