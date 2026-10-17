"""
Suite de Testes de Integração e Validação da Fase M-2:
Modelos 3D Esculpidos, Cinemática Articulada, Hitboxes Geométricas e Física 3D de Cadáveres.
"""
import os
import sys
import math
import pygame

# Execução headless
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((400, 300))

from src.isometric.camera import Camera
from src.isometric.mesh_primitives import (
    draw_tapered_frustum_3d,
    draw_ribbon_mesh_3d,
    draw_sculpted_head_3d,
    draw_portrait_face_3d,
    PORTRAIT_FACE_STYLES,
)
from src.isometric.voxel_rig import (
    calc_spine_and_pelvis_rig,
    martial_ease_3phase,
)
from src.combat.hitboxes import (
    CapsuleHitbox,
    ArcSectorHitbox,
    RadialHitbox,
    build_fighter_melee_hitbox,
    check_fighter_melee_hit,
    align_finisher_pair,
    HitboxDebugInspector,
)
from src.entities.red_samurai import RedSamurai
from src.entities.blue_samurai import BlueSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.kabuki import Kabuki
from src.entities.rifleman import Rifleman
from src.entities.voxel_corpse import VoxelCorpse, VoxelCorpsePiece
from src.world.map_data import GameMap


def test_mesh_primitives_render():
    """Testa renderização das 4 primitivas de malha 3D pura."""
    surface = pygame.Surface((300, 300))
    camera = Camera(10.0, 10.0)

    # 1. Tapered Frustum
    draw_tapered_frustum_3d(
        surface, camera,
        (10.0, 10.0, 0.2), (10.0, 10.0, 0.8),
        0.3, 0.2, 0.4, 0.3,
        (180, 40, 50),
        outline=True,
    )

    # 2. Ribbon Mesh (Fita contínua 3D)
    spine = [(10.0, 10.0, 0.9), (10.1, 10.1, 0.6), (10.2, 10.2, 0.3)]
    widths = [0.12, 0.15, 0.18]
    colors = [(200, 30, 40), (160, 20, 30)]
    draw_ribbon_mesh_3d(
        surface, camera,
        spine_points=spine,
        widths=widths,
        depth_thick=0.06,
        colors=colors,
        side_vec=(1.0, 0.0, 0.0),
        normal_vec=(0.0, 1.0, 0.0),
        outline=True,
    )

    # 3. Sculpted Head
    draw_sculpted_head_3d(
        surface, camera,
        10.0, 10.0, 1.2, 0.16,
        1.0, 0.0, 0.0, 1.0,
        (245, 215, 190), (210, 175, 145),
    )

    # 4. Portrait Face Features
    class DummyContext:
        def __init__(self):
            self.surface = surface
            self.camera = camera
            self.base_x = 10.0
            self.base_y = 10.0
            self.head_z = 1.2
            self.head_w = 0.16
            self.fx = 1.0
            self.fy = 0.0
            self.px = 0.0
            self.py = 1.0
            self.alpha = 255
            self.materials = {}

    c = DummyContext()
    for char_key in ("kenshin", "musashi", "saitou", "okuni", "kasumi"):
        draw_portrait_face_3d(c, char_type=char_key)
        assert char_key in PORTRAIT_FACE_STYLES


def test_spine_rig_and_martial_ease():
    """Testa cinemática de coluna, inclinação e curva de ataque trifásica."""
    # Curva trifásica: antecipação lenta (p < 0.22), estocada/chicote explosivo, zanshin suave
    e0 = martial_ease_3phase(0.0)
    e_coil = martial_ease_3phase(0.20)
    e_strike = martial_ease_3phase(0.50)
    e_end = martial_ease_3phase(1.0)
    assert e0 == 0.0
    assert e_coil < 0.15
    assert e_strike > 0.40
    assert abs(e_end - 1.0) < 1e-4

    # Rig de coluna ao caminhar vs atacar
    rig_walk = calc_spine_and_pelvis_rig(
        char_type="kenshin",
        state="WALK",
        is_moving=True,
        is_melee=False,
        atk_progress=0.0,
        walk_timer=0.5,
        fx=1.0, fy=0.0, px=0.0, py=1.0,
    )
    assert "hip_sway_y" in rig_walk
    assert "sh_px" in rig_walk
    assert rig_walk["chest_lean_x"] > 0.0

    rig_melee = calc_spine_and_pelvis_rig(
        char_type="kenshin",
        state="ATTACK",
        is_moving=False,
        is_melee=True,
        atk_progress=0.5,
        walk_timer=0.0,
        fx=1.0, fy=0.0, px=0.0, py=1.0,
    )
    assert rig_melee["eased_atk"] > 0.0
    assert "shoulder_yaw" in rig_melee


def test_geometric_hitboxes():
    """Testa CapsuleHitbox, ArcSectorHitbox e RadialHitbox."""
    # 1. CapsuleHitbox (Segmento de (0, 0) a (2, 0) com raio 0.4)
    capsule = CapsuleHitbox(ax=0.0, ay=0.0, bx=2.0, by=0.0, radius=0.4)
    assert capsule.intersects_circle(1.0, 0.3, 0.2)  # Perto do meio
    assert capsule.intersects_circle(2.2, 0.0, 0.3)  # Perto da ponta
    assert not capsule.intersects_circle(1.0, 2.0, 0.2)  # Muito longe lateralmente

    # 2. ArcSectorHitbox (Arco frontal de 90° e alcance 1.8)
    arc = ArcSectorHitbox(ox=0.0, oy=0.0, fx=1.0, fy=0.0, reach=1.8, half_angle_rad=math.radians(45))
    assert arc.intersects_circle(1.2, 0.2, 0.2)  # Dentro do cone frontal
    assert not arc.intersects_circle(-1.0, 0.0, 0.2)  # Atrás do atacante
    assert not arc.intersects_circle(3.0, 0.0, 0.2)  # Fora do alcance

    # 3. RadialHitbox
    radial = RadialHitbox(cx=5.0, cy=5.0, radius=1.5)
    assert radial.intersects_circle(5.5, 5.5, 0.3)
    assert not radial.intersects_circle(8.0, 8.0, 0.3)


def test_fighter_hitbox_generation_and_check():
    """Testa geração automática de hitboxes e colisão."""
    p1 = RedSamurai(10.0, 10.0)
    p2 = BlueSamurai(11.2, 10.0)
    p1.set_facing(p2.wx, p2.wy)
    p1.hitbox_active = True
    p1.hitbox_radius = 1.0
    p1.hitbox_center = (p1.wx + p1.facing_x * 0.8, p1.wy + p1.facing_y * 0.8)

    shape = build_fighter_melee_hitbox(p1)
    assert shape is not None

    hit = check_fighter_melee_hit(p1, p2.wx, p2.wy, p2.radius)
    assert hit is True

    # P3 fora do alcance
    p3_wx, p3_wy = 18.0, 18.0
    hit_miss = check_fighter_melee_hit(p1, p3_wx, p3_wy, 0.4)
    assert hit_miss is False


def test_align_finisher_pair():
    """Testa alinhamento magnético suave no golpe fatal."""
    p1 = RedSamurai(10.0, 10.0)
    p2 = BlueSamurai(12.5, 10.0)  # Afastado a 2.5m
    game_map = GameMap()

    orig_p2_x = p2.wx
    align_finisher_pair(p1, p2, game_map)

    # A vítima deve ter sido atraída para mais perto do alcance fatal ideal (~1.08 - 1.35m)
    dist_after = math.hypot(p2.wx - p1.wx, p2.wy - p1.wy)
    assert dist_after < (orig_p2_x - p1.wx)
    assert p1.facing_x > 0.9  # Atacante perfeitamente orientado para a vítima


def test_hitbox_debug_inspector():
    """Testa o inspetor de hitboxes F3."""
    inspector = HitboxDebugInspector(enabled=False)
    assert not inspector.enabled
    inspector.toggle()
    assert inspector.enabled

    surface = pygame.Surface((300, 300))
    camera = Camera(10.0, 10.0)
    p1 = RedSamurai(10.0, 10.0)
    p2 = Kabuki(11.0, 10.0)
    p1.hitbox_active = True

    # Renderiza sem exceções
    inspector.render(surface, camera, [p1, p2], [])


def test_corpse_3d_caps_and_tumbling():
    """Testa renderização de seções transversais 3D do cadáver."""
    victim = RedSamurai(10.0, 10.0)
    corpse = VoxelCorpse(victim, "KENSHIN_SPLIT", (1.0, 0.0))
    surface = pygame.Surface((300, 300))
    camera = Camera(10.0, 10.0)

    # Renderiza sem exceções e executa tampas 3D
    corpse.render(surface, camera)
    assert len(corpse.pieces) >= 2

    # Verifica peça com render_box 3D
    piece = VoxelCorpsePiece(10.0, 10.0, 0.5, 0.2, 0.2, 0.2, (180, 40, 40))
    piece.rot_angle = 45.0
    piece.render_box(surface, camera)


def run_all():
    print("Executando Suite Master Fase M-2...")
    test_mesh_primitives_render()
    print("1. Primitivas de Malha 3D e Feições Faciais OK!")
    test_spine_rig_and_martial_ease()
    print("2. Rig Articulado de Coluna e Curva Trifásica OK!")
    test_geometric_hitboxes()
    print("3. Hitboxes Geométricas (Cápsula, Arco e Radial) OK!")
    test_fighter_hitbox_generation_and_check()
    print("4. Geração Dinâmica e Checagem de Hitbox OK!")
    test_align_finisher_pair()
    print("5. Alinhamento Magnético de Finishers OK!")
    test_hitbox_debug_inspector()
    print("6. Inspetor Visual de Hitboxes F3 OK!")
    test_corpse_3d_caps_and_tumbling()
    print("7. Tampas Anatômicas 3D e Queda 3D de Cadáveres OK!")
    print("\nTODOS OS TESTES DA FASE M-2 PASSARAM COM SUCESSO!")


if __name__ == "__main__":
    run_all()
