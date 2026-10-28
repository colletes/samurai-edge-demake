"""
Testes automatizados para os Entregáveis C-1.1, C-1.2 e C-1.3:
- C-1.1: Tighter Duel Base Zoom (1.75x desktop / 1.90x mobile até 0.95x em longa distância)
- C-1.2: Margens de Segurança Vertical (Overhead Clamping) & Anti-Corte de HUD
- C-1.3: Enquadramento Direcional Reativo de Projéteis Rápidos (Balística & Zoom Suave)
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import math
from src.isometric.camera import Camera
from src.entities.samurai import Samurai
from src.entities.projectile import MusketBulletProjectile, KyudoArrowProjectile

class MockFighter:
    def __init__(self, wx: float, wy: float, wz: float = 0.0, height: float = 1.65):
        self.wx = wx
        self.wy = wy
        self.wz = wz
        self.height = height
        self.state = "IDLE"
        self.is_alive = True
        self.facing_x = 1.0
        self.facing_y = 0.0

def test_c1_1_compute_distance_zoom_desktop():
    # Distância próxima (<= 2.8 tiles) deve retornar exatamente ZOOM_CLOSE (1.75x)
    assert Camera.compute_distance_zoom(1.0, is_mobile=False) == 1.75
    assert Camera.compute_distance_zoom(2.0, is_mobile=False) == 1.75
    assert Camera.compute_distance_zoom(2.8, is_mobile=False) == 1.75

    # Distância intermediária (ex: 5.65 tiles) deve estar entre 1.75x e 0.95x
    mid_zoom = Camera.compute_distance_zoom(5.65, is_mobile=False)
    assert 0.95 < mid_zoom < 1.75
    # No ponto médio (t=0.5), smoothstep(0.5) = 0.5 -> zoom deve ser média exata
    expected_mid = 1.75 + (0.95 - 1.75) * 0.5
    assert abs(mid_zoom - expected_mid) < 0.001

    # Distância distante (>= 8.5 tiles) deve retornar ZOOM_FAR (0.95x)
    assert Camera.compute_distance_zoom(8.5, is_mobile=False) == 0.95
    assert Camera.compute_distance_zoom(12.0, is_mobile=False) == 0.95

def test_c1_1_compute_distance_zoom_mobile():
    # Mobile deve ter base mais próxima (1.90x)
    assert Camera.compute_distance_zoom(1.5, is_mobile=True) == 1.90
    assert Camera.compute_distance_zoom(2.8, is_mobile=True) == 1.90

    # Distante deve retornar 0.95x
    assert Camera.compute_distance_zoom(9.0, is_mobile=True) == 0.95

def test_c1_1_zoom_tracking_convergence():
    cam = Camera(10.0, 10.0)
    p1 = MockFighter(9.0, 10.0)
    p2 = MockFighter(11.0, 10.0) # dist = 2.0 tiles (close combat)

    # Simular frames de combate
    for _ in range(60):
        cam.update_combat_framing(p1, p2, dt=0.016)

    # Zoom deve convergir para 1.75x (desktop)
    assert abs(cam.zoom - 1.75) < 0.02, f"Esperado zoom próximo de 1.75x, obtido {cam.zoom}"

    # Agora os lutadores se afastam para dist = 10.0 tiles
    p2.wx = 19.0
    for _ in range(60):
        cam.update_combat_framing(p1, p2, dt=0.016)

    # Zoom deve convergir para 0.95x
    assert abs(cam.zoom - 0.95) < 0.02, f"Esperado zoom recuado de 0.95x, obtido {cam.zoom}"

def test_c1_2_overhead_clamping_ground_fighters():
    cam = Camera(10.0, 10.0)
    p1 = MockFighter(10.0, 10.0, wz=0.0)
    p2 = MockFighter(11.0, 10.0, wz=0.0)

    for _ in range(30):
        cam.update_combat_framing(p1, p2, dt=0.016)

    # No solo, screen_y deve permanecer no centro padrão (360)
    assert cam.screen_y == cam.base_screen_y
    assert cam.overhead_offset_y == 0.0

def test_c1_2_overhead_clamping_jumping_fighter():
    cam = Camera(10.0, 10.0)
    # P1 salta alto (ex: Ryuu Tsui Sen / Pole Vault) em posição recuada no mapa
    p1 = MockFighter(9.0, 9.0, wz=2.6)
    p1.state = "RYUU_TSUI_SEN"
    p2 = MockFighter(11.0, 11.0, wz=0.0)

    # Simular atualização de combate
    for _ in range(60):
        cam.update_combat_framing(p1, p2, dt=0.016)

    # A câmera deve ter deslocado screen_y para baixo para acomodar o topo do salto
    assert cam.screen_y > cam.base_screen_y, f"screen_y deveria ser maior que 360, obtido {cam.screen_y}"
    assert cam.overhead_offset_y > 0.0

    # Testar que o topo da cabeça de P1 projetado na tela respeita a margem de segurança do HUD
    head_wz = p1.wz + p1.height + 0.35
    _, head_screen_y = cam.apply(p1.wx, p1.wy, head_wz)
    assert head_screen_y >= (Camera.HUD_SAFE_TOP - 2.0), f"Cabeça projetada em {head_screen_y}px colide com HUD (mínimo {Camera.HUD_SAFE_TOP}px)"

    # Agora o lutador pousa no chão
    p1.wz = 0.0
    p1.state = "IDLE"
    for _ in range(90):
        cam.update_combat_framing(p1, p2, dt=0.016)

    # screen_y deve retornar suavemente ao centro base (360)
    assert abs(cam.screen_y - cam.base_screen_y) <= 1, f"screen_y deveria retornar a 360, obtido {cam.screen_y}"

def test_c1_3_bullet_directional_framing():
    cam = Camera(10.0, 10.0)
    p1 = MockFighter(10.0, 10.0)
    p2 = MockFighter(16.0, 10.0)

    # Sem projéteis, bias deve ser 0.0
    cam.update_combat_framing(p1, p2, dt=0.016)
    assert cam.projectile_bias_x == 0.0
    assert cam.projectile_bias_y == 0.0

    # Teppo dispara um tiro de mosquete supersônico em direção a P2 (+X)
    bullet = MusketBulletProjectile(wx=11.0, wy=10.0, wz=0.9, dir_x=1.0, dir_y=0.0, owner=p1)
    projectiles = [bullet]

    # Simular avanço da bala durante voo
    for _ in range(15):
        bullet.wx += 0.25
        cam.update_combat_framing(p1, p2, dt=0.016, projectiles=projectiles)

    # A câmera deve ter adiantado o enquadramento suavemente na direção do disparo (+X)
    assert cam.projectile_bias_x > 0.0, f"projectile_bias_x deveria ser positivo na direção do disparo, obtido {cam.projectile_bias_x}"
    assert abs(cam.projectile_bias_y) < 0.001

    # Quando a bala impacta / é desativada
    bullet.is_active = False
    for _ in range(40):
        cam.update_combat_framing(p1, p2, dt=0.016, projectiles=projectiles)

    # O deslocamento balístico deve decair suavemente de volta a zero sem solavanco
    assert abs(cam.projectile_bias_x) < 0.01, f"projectile_bias_x deveria retornar a zero, obtido {cam.projectile_bias_x}"

def test_c1_3_long_range_projectile_zoom_expansion():
    cam = Camera(10.0, 10.0)
    p1 = MockFighter(8.0, 10.0)
    p2 = MockFighter(12.0, 10.0) # dist = 4.0 tiles

    # Zoom sem projéteis em 4.0 tiles
    for _ in range(40):
        cam.update_combat_framing(p1, p2, dt=0.016)
    neutral_zoom = cam.zoom

    # Disparo de flecha Yumi de longo alcance que voa além de P2 (wx = 17.0)
    arrow = KyudoArrowProjectile(wx=17.0, wy=10.0, wz=1.0, dir_x=1.0, dir_y=0.0, owner=p1)
    projectiles = [arrow]

    for _ in range(30):
        cam.update_combat_framing(p1, p2, dt=0.016, projectiles=projectiles)

    # O enquadramento dinâmico deve expandir sutilmente o campo de visão (zoom menor que neutral_zoom)
    assert cam.zoom < neutral_zoom, f"Zoom com projétil distante ({cam.zoom}) deveria ser mais aberto que neutral ({neutral_zoom})"

if __name__ == "__main__":
    test_c1_1_compute_distance_zoom_desktop()
    test_c1_1_compute_distance_zoom_mobile()
    test_c1_1_zoom_tracking_convergence()
    test_c1_2_overhead_clamping_ground_fighters()
    test_c1_2_overhead_clamping_jumping_fighter()
    test_c1_3_bullet_directional_framing()
    test_c1_3_long_range_projectile_zoom_expansion()
    print("Todos os testes dos Entregáveis C-1.1, C-1.2 e C-1.3 passaram com 100% de sucesso!")
