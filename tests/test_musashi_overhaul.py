"""
Suíte de testes de integração e mecânicas do Overhaul do Musashi (Sub-fase 2.2 — Hyoho Niten Ichi-ryu).
Verifica os 11 entregáveis de padrão idêntico ao da Kenshi:
1. Combo 3 tempos sem embainhar + avanço com projétil de onda no 3º golpe.
2. Cross Guard Parry (0.28s reflexão) com contra-ataque Cross Shockwave.
3. Rolamento Tático sem sombras Zanzou e com cancelamento ofensivo aos 40% finais.
4. Finisher 1: DUAL_IMPALE_X_SPREAD (3 partes de torso + cabeça + 二天一流).
5. Finisher 2: CROSS_VACUUM_SLICER (4 quadrantes simétricos + 十字真空波).
6. Intro: Saque duplo & atrito de lâminas em 'X' com faíscas metálicas.
7. Vitória: Duplo Chiburi simultâneo & Postura dos Dois Céus sem embainhar.
8. Rig 3D, Materiais realistas, LEGACY_MATERIALS e Rosto marcial com cicatriz.
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

from src.entities.blue_samurai import BlueSamurai
from src.entities.red_samurai import RedSamurai
from src.entities import musashi_model, pose_scripts
from src.entities.projectile import MusashiWaveProjectile
from src.entities.voxel_corpse import VoxelCorpse
from src.effects.cinematic_director import CinematicDirector
from src.isometric.camera import Camera
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


def test_musashi_initialization():
    """Testa atributos base e estado do Musashi overhaul."""
    musashi = BlueSamurai(10.0, 10.0)
    assert musashi.char_type == "musashi"
    assert musashi.max_hp == 3
    assert musashi.hp == 3
    assert musashi.speed == 4.0
    assert musashi.ssaa_enabled is True
    assert hasattr(musashi, "_pose_lerp_tracker")
    assert musashi._pose_lerp_tracker["lerp_duration"] == 0.08
    assert musashi.counter_shockwave_ready is False
    assert musashi.combo_step == 0


def test_musashi_three_step_combo():
    """Testa o combo ritmado de 3 tempos e projétil de onda no 3º corte."""
    musashi = BlueSamurai(10.0, 10.0)
    game_map = DummyMap()
    projectiles = []

    # Passo 1: Corte Katana Descendente
    musashi.trigger_combo_attack(12.0, 10.0)
    assert musashi.state == "ATTACK"
    assert musashi.combo_step == 1
    assert musashi.hitbox_active is True
    assert musashi.hitbox_radius == 1.45

    # Buffer do segundo golpe durante o primeiro
    musashi.trigger_combo_attack(12.0, 10.0)
    assert musashi.combo_buffered is True

    # Avançar até transição para o passo 2
    musashi.update(0.19, game_map, projectiles=projectiles)
    assert musashi.state == "ATTACK"
    assert musashi.combo_step == 2
    assert musashi.hitbox_radius == 1.62

    # Buffer do terceiro golpe
    musashi.trigger_combo_attack(12.0, 10.0)
    assert musashi.combo_buffered is True

    # Avançar até transição para o passo 3 (Lunge + Onda)
    musashi.update(0.19, game_map, projectiles=projectiles)
    assert musashi.state == "ATTACK"
    assert musashi.combo_step == 3
    assert musashi.hitbox_radius == 2.06
    assert len(projectiles) == 1
    assert isinstance(projectiles[0], MusashiWaveProjectile)
    assert projectiles[0].owner == musashi

    # Final do combo entra em RECOVERY sem embainhar (swords drawn)
    musashi.update(0.19, game_map, projectiles=projectiles)
    assert musashi.state == "RECOVERY"
    assert musashi.can_move() is True  # Pode andar a 50% de velocidade em recovery sem embainhar


def test_musashi_cross_guard_and_shockwave():
    """Testa Cross Guard Parry, janela de reflexão e contra-ataque Cross Shockwave."""
    musashi = BlueSamurai(10.0, 10.0)
    game_map = DummyMap()
    projectiles = []

    # Ativa Cross Guard Parry
    assert musashi.trigger_parry() is True
    assert musashi.state == "PARRY"
    assert musashi.parry_reflect_active_timer == 0.28

    # Bloqueio frontal bem-sucedido
    musashi.on_parry_successful(None)
    assert musashi.counter_shockwave_ready is True

    # Com counter_shockwave_ready, disparar parry desencadeia o Cross Shockwave
    musashi.trigger_parry(projectiles=projectiles)
    assert musashi.state == "CROSS_SHOCKWAVE"
    assert musashi.hitbox_active is True
    assert musashi.hitbox_radius == 2.20
    assert musashi.counter_shockwave_ready is False
    assert len(projectiles) == 1
    assert isinstance(projectiles[0], MusashiWaveProjectile)


def test_musashi_tactical_roll_no_zanzou_and_offensive_cancel():
    """Testa rolamento tático sem sombras zanzou e cancelamento ofensivo aos 40% finais."""
    musashi = BlueSamurai(10.0, 10.0)
    game_map = DummyMap()

    # Dispara rolamento tático
    musashi.trigger_roll(1.0, 0.0)
    assert musashi.state == "ROLL"
    assert musashi.is_invulnerable_dodge is True
    assert not hasattr(musashi, "zanzou_ghosts") or len(getattr(musashi, "zanzou_ghosts", [])) == 0

    # No início do roll (100% restante), não pode cancelar
    assert musashi.can_cancel_roll() is False

    # Avançar 65% do roll (ficando com 35% restante <= 40%)
    dt_advance = musashi.roll_duration * 0.65
    musashi.update_roll(dt_advance, game_map)
    assert musashi.can_cancel_roll() is True

    # Pressionar ataque durante a janela de cancelamento dispara corte corrido imediatamente
    musashi.trigger_combo_attack(12.0, 10.0)
    assert musashi.state == "ATTACK"
    assert musashi.is_roll_cancel is True
    assert musashi.is_invulnerable_dodge is False
    assert musashi.hitbox_active is True


def test_musashi_finishers_voxel_corpse_and_kanji():
    """Testa os dois Finishers cinemáticos: Niten Ichi-ryu (3 partes) e Cross Vacuum Slicer (4 quadrantes)."""
    victim = RedSamurai(10.0, 10.0)
    cd = CinematicDirector()

    # 1. Finisher 1: DUAL_IMPALE_X_SPREAD
    corpse1 = VoxelCorpse(victim, "DUAL_IMPALE_X_SPREAD", (1.0, 0.0))
    # Deve conter cabeça decepada, tronco esquerdo, tronco direito e tronco base
    assert hasattr(corpse1, "severed_head")
    assert hasattr(corpse1, "torso_left")
    assert hasattr(corpse1, "torso_right")
    assert hasattr(corpse1, "torso_base")
    assert len(corpse1.pieces) >= 4

    cd._build_kanji_overlay(None, None, "DUAL_IMPALE_X_SPREAD")
    assert cd.current_kanji_text == "二天一流"
    assert "NITEN ICHI-RYUU" in cd.current_kanji_subtitle

    # 2. Finisher 2: CROSS_VACUUM_SLICER
    corpse2 = VoxelCorpse(victim, "CROSS_VACUUM_SLICER", (1.0, 0.0))
    # Deve conter 4 partes principais (quadrantes em X)
    assert len(corpse2.pieces) >= 4

    cd._build_kanji_overlay(None, None, "CROSS_VACUUM_SLICER")
    assert cd.current_kanji_text == "十字真空波"
    assert "JUUJI SHINKUU-HA" in cd.current_kanji_subtitle


def test_musashi_intro_and_victory_pose_scripts():
    """Testa os scripts e eventos rítmicos de Intro e Vitória do Musashi."""
    assert "musashi" in pose_scripts.INTRO
    assert "musashi" in pose_scripts.VICTORY
    assert "musashi" in pose_scripts.BEATS["intro"]
    assert "musashi" in pose_scripts.BEATS["victory"]

    # Amostragem do início da Intro: saque duplo
    frame_intro_start = pose_scripts.sample("musashi", "intro", 0.15)
    assert frame_intro_start.extra.get("pose") == "dual_draw"

    # Amostragem do meio da Intro: atrito em X com faíscas
    frame_intro_mid = pose_scripts.sample("musashi", "intro", 0.45)
    assert frame_intro_mid.extra.get("pose") == "cross_blade_clash"

    # Amostragem do fim da Intro: guarda dos dois céus
    frame_intro_end = pose_scripts.sample("musashi", "intro", 0.85)
    assert frame_intro_end.extra.get("pose") == "two_heavens_guard"

    # Amostragem da Vitória: Duplo Chiburi -> Postura dos Dois Céus
    frame_vic_start = pose_scripts.sample("musashi", "victory", 0.20)
    assert frame_vic_start.extra.get("pose") == "double_chiburi"

    frame_vic_end = pose_scripts.sample("musashi", "victory", 0.70)
    assert frame_vic_end.extra.get("pose") == "two_heavens_victory"


def test_musashi_model_materials_and_inspector_integration():
    """Testa materiais realistas, LEGACY_MATERIALS e registro no Model Inspector."""
    assert hasattr(musashi_model, "MATERIALS")
    assert hasattr(musashi_model, "LEGACY_MATERIALS")
    assert "kimono" in musashi_model.MATERIALS
    assert "saya" in musashi_model.MATERIALS
    assert "steel" in musashi_model.MATERIALS

    # Model Inspector: notas De/Para e botões interativos
    assert "musashi" in OVERHAUL_DE_PARA_NOTES
    assert len(OVERHAUL_DE_PARA_NOTES["musashi"]) >= 4

    assert "musashi" in CHARACTER_ANIM_BUTTONS
    btn_ids = [bid for bid, _lbl, _dur in CHARACTER_ANIM_BUTTONS["musashi"]]
    assert "IDLE" in btn_ids
    assert "WALK" in btn_ids
    assert "ATTACK_1" in btn_ids
    assert "ATTACK_2" in btn_ids
    assert "ATTACK_3" in btn_ids
    assert "CROSS_GUARD" in btn_ids
    assert "CROSS_SHOCKWAVE" in btn_ids
    assert "TACTICAL_ROLL" in btn_ids
    assert "ROLL_CANCEL" in btn_ids
    assert "INTRO" in btn_ids
    assert "VICTORY" in btn_ids
    assert "FINISHER_1" in btn_ids
    assert "FINISHER_2" in btn_ids


def test_musashi_rendering_ssaa_and_lerp():
    """Testa pipeline de renderização com SSAA 2x e Pose LERP sem falhas."""
    musashi = BlueSamurai(10.0, 10.0)
    surf = pygame.Surface((800, 600))
    cam = Camera(800, 600)

    # Render em IDLE
    musashi.render(surf, cam)

    # Render em PARRY
    musashi.state = "PARRY"
    musashi.current_pose = "cross_guard"
    musashi.render(surf, cam)

    # Render em ROLL
    musashi.state = "ROLL"
    musashi.current_pose = "tactical_roll"
    musashi.render(surf, cam)

    # Render em CROSS_SHOCKWAVE
    musashi.state = "CROSS_SHOCKWAVE"
    musashi.render(surf, cam)


def test_musashi_game_help_manual():
    """Testa o manual dos guerreiros atualizado para Musashi em PT e EN."""
    musashi_entry = None
    for entry in FIGHTERS_GUIDE_DATA:
        if entry.get("char_type") == "blue_samurai" or entry.get("id") == "musashi" or "MUSASHI" in entry.get("pt", {}).get("name", ""):
            musashi_entry = entry
            break

    assert musashi_entry is not None
    assert "Hyoho Niten" in musashi_entry["pt"]["style"]
    assert "Cross Guard" in musashi_entry["pt"]["especial"]
    assert "Rolamento Tático" in musashi_entry["pt"]["habilidades"]
    assert "Cross Vacuum Slicer" in musashi_entry["pt"]["habilidades"]

    assert "Hyoho Niten" in musashi_entry["en"]["style"]
    assert "Cross Guard" in musashi_entry["en"]["especial"]
    assert "Tactical Roll" in musashi_entry["en"]["habilidades"]
    assert "Cross Vacuum Slicer" in musashi_entry["en"]["habilidades"]


if __name__ == "__main__":
    print("=== Executando Testes do Overhaul de Musashi (Sub-fase 2.2) ===")
    test_musashi_initialization()
    print("✓ test_musashi_initialization passou!")
    test_musashi_three_step_combo()
    print("✓ test_musashi_three_step_combo passou!")
    test_musashi_cross_guard_and_shockwave()
    print("✓ test_musashi_cross_guard_and_shockwave passou!")
    test_musashi_tactical_roll_no_zanzou_and_offensive_cancel()
    print("✓ test_musashi_tactical_roll_no_zanzou_and_offensive_cancel passou!")
    test_musashi_finishers_voxel_corpse_and_kanji()
    print("✓ test_musashi_finishers_voxel_corpse_and_kanji passou!")
    test_musashi_intro_and_victory_pose_scripts()
    print("✓ test_musashi_intro_and_victory_pose_scripts passou!")
    test_musashi_model_materials_and_inspector_integration()
    print("✓ test_musashi_model_materials_and_inspector_integration passou!")
    test_musashi_rendering_ssaa_and_lerp()
    print("✓ test_musashi_rendering_ssaa_and_lerp passou!")
    test_musashi_game_help_manual()
    print("✓ test_musashi_game_help_manual passou!")
    print("\n=======================================================")
    print("TODOS OS TESTES DO OVERHAUL DE MUSASHI PASSARAM 100%!")
    print("=======================================================")

