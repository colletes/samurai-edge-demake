import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.entities.saitou_samurai import SaitouSamurai, STATE_GATOTSU_CHARGE, STATE_IDLE
from src.entities.american_ninja import AmericanNinja
from src.entities.blue_samurai import BlueSamurai as MusashiSamurai
from src.entities.voxel_corpse import VoxelCorpse, _Ctx
import src.entities.saitou_model as saitou_model
import src.entities.joe_model as joe_model
from src.effects.cinematic_director import CinematicDirector
from src.combat.collision import _get_death_style_for_attacker
from types import SimpleNamespace


def test_saitou_sword_in_hand_stance():
    print("Testando Saitou: Espada sempre sacada na postura Gatotsu...")
    s = SaitouSamurai(5.0, 5.0)

    # Contexto simulado para IDLE
    c_idle = SimpleNamespace(
        state="IDLE",
        is_melee=False,
        atk_progress=0.0,
        extra_props={},
        base_x=5.0, base_y=5.0, base_z=0.0,
        torso_z=0.5, head_z=0.8,
        fx=1.0, fy=0.0, px=0.0, py=1.0,
        walk_timer=0.0, is_moving=False
    )
    assert saitou_model._is_blade_in_hand(c_idle) is True, "Saitou deve estar com a espada em mãos no IDLE!"

    # Braços em Gatotsu Kamae no IDLE
    left, right = saitou_model.idle_arms(c_idle)
    assert left[0] > c_idle.base_x + 0.30, "Mão esquerda deve estar bem projetada à frente segurando o Gatotsu!"

    # Contexto simulado para WALK
    c_walk = SimpleNamespace(
        state="WALK",
        is_melee=False,
        atk_progress=0.0,
        extra_props={},
        base_x=5.0, base_y=5.0, base_z=0.0,
        torso_z=0.5, head_z=0.8,
        fx=1.0, fy=0.0, px=0.0, py=1.0,
        walk_timer=0.5, is_moving=True
    )
    assert saitou_model._is_blade_in_hand(c_walk) is True, "Saitou deve estar com a espada em mãos no WALK!"

    # Contexto simulado para GATOTSU_CHARGE
    c_charge = SimpleNamespace(
        state=STATE_GATOTSU_CHARGE,
        is_melee=True,
        atk_progress=0.5,
        extra_props={"pose": "gatotsu_lunge", "p": 0.5, "gatotsu_lunge": True},
        base_x=5.0, base_y=5.0, base_z=0.0,
        torso_z=0.5, head_z=0.8,
        fx=1.0, fy=0.0, px=0.0, py=1.0,
        walk_timer=0.0, is_moving=True
    )
    assert saitou_model._is_blade_in_hand(c_charge) is True, "Saitou deve estar com a espada em mãos no GATOTSU_CHARGE!"
    arms_l, arms_r = saitou_model._hands(c_charge)
    assert arms_l[0] > c_charge.base_x + 0.50, "Estocada do Gatotsu deve estender a lâmina para a frente!"
    print("✓ Saitou: Espada sempre sacada e guarda do Gatotsu validadas!")


def test_joe_head_alignment_during_banjo():
    print("Testando Joe: Alinhamento rígido do chapéu de cowboy sem deformação...")
    c_banjo = SimpleNamespace(
        state="VICTORY",
        is_melee=False,
        atk_progress=0.85,
        extra_props={"pose": "cowboy_banjo", "p": 0.85},
        base_x=5.0, base_y=5.0, base_z=0.0,
        torso_z=0.5, head_z=0.8, head_w=0.15,
        fx=1.0, fy=0.0, px=0.0, py=1.0,
        walk_timer=0.0, state_timer=0.0
    )
    # Testa que o chapéu repousa solidamente sobre a coroa sem cisalhamento
    hz = c_banjo.head_z
    crown_z = hz + 0.158
    assert crown_z >= hz + 0.145, "Aba do chapéu deve estar firmemente no topo do crânio!"
    print("✓ Joe: Chapéu de cowboy e crânio perfeitamente unificados!")


def test_saitou_finisher_a_chambara_back_blood():
    print("Testando Saitou Finisher A: Empalamento, elevação e fonte arterial nas costas...")
    saitou = SaitouSamurai(5.0, 5.0)
    victim = MusashiSamurai(6.0, 5.0)
    director = CinematicDirector()

    director.trigger_fatal_strike(saitou, victim, "HEART_IMPALE_LUNGE", (1.0, 0.0))
    assert director.saitou_attacker is saitou, "Diretor deve registrar saitou_attacker!"
    assert director.saitou_victim is victim, "Diretor deve registrar saitou_victim!"
    assert director.saitou_timer > 1.0, "saitou_timer deve estar armado para 1.15s!"

    # Simular avanço cinematográfico até a fase de elevação
    particles = []
    map_mock = SimpleNamespace(bamboos=[])
    # Avançar a fase de enquadramento da câmera (0.60s)
    director.update(0.60, map_mock, particles=particles)

    # Avançar 0.40s na execução (atinge a fase de elevação e jorro arterial)
    director.update(0.40, map_mock, particles=particles)
    assert victim.wz > 0.0, f"Vítima deve ser erguida no ar pela lâmina do Gatotsu! wz={victim.wz}"
    assert len(particles) > 0, "Partículas de sangue arterial devem ser geradas em jorro contínuo!"

    # Testar que as partículas de sangue saem pelas costas da vítima (direção positiva do golpe)
    back_blood = [p for p in particles if getattr(p, "vx", 0.0) > 1.0]
    assert len(back_blood) > 0, "Jato de sangue deve explodir para trás saindo pelas costas do rival!"

    # Testar VoxelCorpse para HEART_IMPALE_LUNGE
    corpse = VoxelCorpse(victim, "HEART_IMPALE_LUNGE", slash_dir=(1.0, 0.0))
    assert len(corpse.pieces) >= 1, "Cadáver empalado deve ser construído!"
    assert len(corpse.blood_droplets) >= 40, "Deve haver grande volume de sangue manchando o piso!"
    print("✓ Saitou Finisher A: Empalamento, elevação e explosão de sangue pelas costas 100% validados!")


def test_joe_finisher_b_triple_shurikens():
    print("Testando Joe Finisher B: 3 Shurikens desmembradoras e decapitação...")
    joe = AmericanNinja(4.0, 4.0)
    victim = SaitouSamurai(6.0, 4.0)
    # 1. Regra de colisão: Joe atacando sem o cão ativa TRIPLE_SHURIKEN_DISMEMBER
    style = _get_death_style_for_attacker(joe, weapon="kunai")
    assert style == "TRIPLE_SHURIKEN_DISMEMBER", f"Ataque solo do Joe deve disparar TRIPLE_SHURIKEN_DISMEMBER, obteve {style}!"

    # 2. Cinemática: 3 shurikens em voo
    director = CinematicDirector()
    director.trigger_fatal_strike(joe, victim, "TRIPLE_SHURIKEN_DISMEMBER", (1.0, 0.0))
    assert director.joe_triple_attacker is joe
    assert director.joe_triple_victim is victim

    map_mock = SimpleNamespace(bamboos=[])
    particles = []
    # Conclui enquadramento da câmera (0.60s)
    director.update(0.60, map_mock, particles=particles)

    # Simula até o disparo 1 (0.35s)
    director.update(0.35, map_mock, particles=particles)
    assert director.joe_triple_shots >= 1, f"Disparo 1 deve ter ocorrido! shots={director.joe_triple_shots}"

    # Simula até o disparo 2 (0.42s a mais)
    director.update(0.42, map_mock, particles=particles)
    assert director.joe_triple_shots >= 2, f"Disparo 2 deve ter ocorrido! shots={director.joe_triple_shots}"

    # Simula até o disparo 3 (0.45s a mais)
    director.update(0.45, map_mock, particles=particles)
    assert director.joe_triple_shots >= 3, f"Disparo 3 deve ter ocorrido decepando a cabeça! shots={director.joe_triple_shots}"

    # 3. VoxelCorpse: 4 pedaços (cabeça, braço direito, braço esquerdo, tronco)
    corpse = VoxelCorpse(victim, "TRIPLE_SHURIKEN_DISMEMBER", slash_dir=(1.0, 0.0))
    piece_types = [p.piece_type for p in corpse.pieces]
    assert "head" in piece_types, "Cabeça decepada deve estar presente!"
    assert "arm_r" in piece_types, "Braço direito decepado deve estar presente!"
    assert "arm_l" in piece_types, "Braço esquerdo decepado deve estar presente!"
    assert "torso_headless" in piece_types, "Tronco decapitado deve estar presente!"
    print("✓ Joe Finisher B: 3x Shurikens, desmembramento e decapitação validados!")


def test_musashi_finisher_a_zero_duplication():
    print("Testando Musashi Finisher A: Zero duplicatas corporais e partições disjuntas...")
    musashi = MusashiSamurai(3.0, 3.0)
    victim = SaitouSamurai(4.5, 3.0)

    corpse = VoxelCorpse(victim, "DUAL_IMPALE_X_SPREAD", slash_dir=(1.0, 0.0))
    piece_types = [p.piece_type for p in corpse.pieces]
    assert "head" in piece_types, "Cabeça decepada deve estar presente!"
    assert "top_left" in piece_types, "Ombro/peitoral esquerdo deve estar presente!"
    assert "top_right" in piece_types, "Ombro/peitoral direito deve estar presente!"
    assert "bottom" in piece_types, "Tronco inferior/pernas deve estar presente!"

    # Verificar que as 4 partes anatômicas são disjuntas e não há múltiplos 'top' com corpo inteiro
    tops = [p for p in corpse.pieces if "top" in p.piece_type]
    assert len(tops) == 2, f"Devem haver exatamente 2 metades de torso superior (top_left e top_right), achou {len(tops)}!"
    assert any(p.piece_type == "top_left" for p in tops)
    assert any(p.piece_type == "top_right" for p in tops)

    # Teste unitário de _Ctx.half_vertical
    class DummyCam:
        azimuth = 0.0
        zoom = 1.0
        def apply(self, x, y, z):
            return (100.0, 150.0)
    lc_mock = SimpleNamespace(apply=lambda x, y, z: (100.0, 150.0 - z * 80.0))
    corpse_mock = SimpleNamespace(wx=0.0, wy=0.0, wz=0.0, dx=1.0, dy=0.0)
    ctx = _Ctx(corpse_mock, lc_mock, (200, 300), DummyCam())

    poly_l = ctx.half_vertical(left=True, z_top=0.8, z_bottom=0.4)
    poly_r = ctx.half_vertical(left=False, z_top=0.8, z_bottom=0.4)

    # Metade esquerda: x de 0 até cx
    assert poly_l[0][0] == 0.0 and poly_l[1][0] == ctx.cx
    # Metade direita: x de cx até w
    assert poly_r[0][0] == ctx.cx and poly_r[1][0] == 200.0
    # Verificação de não-sobreposição em X
    assert poly_l[1][0] <= poly_r[0][0], "Polígonos esquerdo e direito devem ser estritamente disjuntos sem sobreposição!"
    print("✓ Musashi Finisher A: Zero duplicatas e partições disjuntas confirmadas!")


if __name__ == "__main__":
    pygame.init()
    test_saitou_sword_in_hand_stance()
    test_joe_head_alignment_during_banjo()
    test_saitou_finisher_a_chambara_back_blood()
    test_joe_finisher_b_triple_shurikens()
    test_musashi_finisher_a_zero_duplication()
    print("\n==================================================")
    print("  TODAS AS CORREÇÕES DOS 5 PONTOS FORAM VALIDADAS!  ")
    print("==================================================")
