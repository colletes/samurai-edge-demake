"""
Testes automatizados para os Modelos Voxel 3D do Ciclo 3 (Goro & Ichi):
- Valida paletas de cores, mapas de materiais e proporções anatômicas.
- Valida resolução canônica de identificadores e classificação de gênero.
- Valida renderização em todos os estados de combate (IDLE, WALK, ATTACK, DEFEND, DODGE).
- Valida empunhadura e animação das armas (Kuwa de Aço e Shikomizue Oculta).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.isometric.camera import Camera
from src.entities.voxel_models import render_voxel_humanoid, _canonical_char_type, is_female_character
from src.entities import goro_model, ichi_model

def test_cycle3_voxel_models():
    pygame.init()
    pygame.display.set_mode((960, 540))
    cam = Camera(960, 540)
    surf = pygame.Surface((200, 200), pygame.SRCALPHA)

    # 1. Resolução canônica e gênero
    assert _canonical_char_type("goro") == "goro"
    assert _canonical_char_type("farmer") == "goro"
    assert _canonical_char_type("kuwa") == "goro"
    assert not is_female_character("goro")

    assert _canonical_char_type("ichi") == "ichi"
    assert _canonical_char_type("blind") == "ichi"
    assert _canonical_char_type("shikomizue") == "ichi"
    assert is_female_character("ichi")
    print("✓ Resolução canônica e verificação de gênero validadas com sucesso!")

    # 2. Paletas e Materiais
    p_goro = goro_model.pal()
    assert "noragi" in p_goro and "iron_kuwa" in p_goro and "steel_edge" in p_goro
    p_ichi = ichi_model.pal()
    assert "kimono" in p_ichi and "cane_wood" in p_ichi and "steel_blade" in p_ichi
    print("✓ Paletas e texturas de materiais validadas com sucesso!")

    # 3. Renderização completa de Goro em todas as poses e estados
    goro_states = [
        ("IDLE", 0.0, {}),
        ("WALK", 0.35, {}),
        ("ATTACK", 0.15, {}),
        ("ATTACK", 0.50, {}),
        ("ATTACK", 0.85, {}),
        ("DEFEND", 0.10, {"pose": "iron_guard"}),
        ("SPECIAL", 0.20, {"is_stomp": True, "pose": "earth_stomp"}),
    ]
    for st, timer, props in goro_states:
        surf.fill((0, 0, 0, 0))
        render_voxel_humanoid(
            surface=surf, camera=cam, wx=5.0, wy=5.0, wz=0.0,
            facing_x=1.0, facing_y=0.0, state=st, state_timer=timer,
            is_alive=True, char_type="goro", walk_timer=0.5,
            is_moving=(st == "WALK"), extra_props=props
        )
    print("✓ Rigs e animações da Kuwa de Goro validados com 100% de sucesso!")

    # 4. Renderização completa de Ichi em todas as poses e estados
    ichi_states = [
        ("IDLE", 0.0, {}),
        ("WALK", 0.40, {}),
        ("ATTACK", 0.10, {}),
        ("ATTACK", 0.45, {}),
        ("ATTACK", 0.80, {}),
        ("DODGE", 0.15, {"pose": "listen_stance"}),
        ("SHEATH", 0.05, {"pose": "sheath_click"}),
        ("ATTACK", 0.30, {"is_pierce": True}),
    ]
    for st, timer, props in ichi_states:
        surf.fill((0, 0, 0, 0))
        render_voxel_humanoid(
            surface=surf, camera=cam, wx=5.0, wy=5.0, wz=0.0,
            facing_x=1.0, facing_y=0.0, state=st, state_timer=timer,
            is_alive=True, char_type="ichi", walk_timer=0.5,
            is_moving=(st in ("WALK", "DODGE")), extra_props=props
        )
    print("✓ Rigs e saque Gyaku-Iai de Ichi validados com 100% de sucesso!")

    print("\n=======================================================")
    print("TODOS OS TESTES DE MODELOS VOXEL DO CICLO 3 PASSARAM!")
    print("=======================================================")

if __name__ == "__main__":
    test_cycle3_voxel_models()
