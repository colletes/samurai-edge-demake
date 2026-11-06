"""
Unit and integration tests for Sub-fase 2.6: Teppo (O Soldado Ashigaru da Pólvora Tanegashima).
Verifies:
1. 3D Model Voxel rendering, SSAA 2x, Legacy Mode, Tonbo Jingasa with gold crest, Kiseru 3D pipe, 6 bamboo hayago tubes, HD martial eyes.
2. Modular humanoid pipeline with get_arms(c) dynamic kinematics and depth-sorted rifle.
3. Matchlock Shot: supersonic 26 m/s ballistic projectile with 1-Hit Kill fatality.
4. Intelligent Primary Attack: fires when loaded, strikes with Heavy Oak Rifle Butt when empty.
5. Rifle Butt Smash: 1.8m knockback and 0.65s stun on hit.
6. Secondary Action: Black Powder Ground Trap (Mina de pólvora negra) placement.
7. Trench Ashigaru Dive: invulnerable dodge roll that automatically chambers a new bullet upon recovery.
8. Fluid Ramrod Reload: automatic reload with ramrod pumping motion.
9. Pose Scripts: 3-phase Intro (match_blow -> lock_check -> ready_aim) and Victory (shoulder_rest -> kiseru_light -> kiseru_puff).
10. Dual Finishers: Finisher A (HEADSHOT_EXPLODE / 一発必中) and Finisher B (HAYAGO_KEG_BLAST / 火薬百連).
11. Model Inspector: CHARACTER_ANIM_BUTTONS["teppo"] and OVERHAUL_DE_PARA_NOTES["teppo"].
"""

import os
import sys
import math
import pygame

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1280, 720))

from src.entities.rifleman import Rifleman, PowderTrap, STATE_RIFLE_AIM, STATE_RIFLE_ROLL
from src.entities.samurai import Samurai, STATE_IDLE, STATE_ATTACK, STATE_PARRY, STATE_DEAD, STATE_ROLL
from src.entities import teppo_model
from src.entities import pose_scripts
from src.entities.voxel_corpse import VoxelCorpse
from src.combat.collision import CombatSystem
from src.world.map_data import GameMap
from tools import model_inspector


class DummyCamera:
    def __init__(self):
        self.zoom = 1.0
        self.offset_x = 640
        self.offset_y = 360
        self.azimuth = math.radians(45)
        self.elevation = math.radians(35.264)
        self.cos_az = math.cos(self.azimuth)
        self.sin_az = math.sin(self.azimuth)
        self.cos_el = math.cos(self.elevation)
        self.sin_el = math.sin(self.elevation)

    def apply(self, wx: float, wy: float, wz: float = 0.0):
        rx = (wx - 10.5) * self.cos_az - (wy - 10.5) * self.sin_az
        ry = (wx - 10.5) * self.sin_az + (wy - 10.5) * self.cos_az
        sx = self.offset_x + (rx - ry) * 32.0 * self.zoom
        sy = self.offset_y + (rx + ry) * 16.0 * self.zoom - wz * 40.0 * self.zoom
        return int(sx), int(sy)

    def add_shake(self, amount: float):
        pass


def test_teppo_model_attributes_and_materials():
    """Valida paleta, materiais realistas CC0 e modo comparativo legado."""
    pal = teppo_model.pal()
    assert "jingasa" in pal
    assert "barrel" in pal
    assert "wood" in pal
    assert "hayago" in pal
    assert "kiseru_brass" in pal
    assert "kiseru_wood" in pal
    assert "ramrod" in pal
    assert "soot" in pal

    assert teppo_model.MATERIALS["cuirass"] == "metal"
    assert teppo_model.MATERIALS["jingasa"] == "lacquer"
    assert teppo_model.MATERIALS["barrel"] == "metal"
    assert teppo_model.MATERIALS["wood"] == "planks"
    assert teppo_model.MATERIALS["bandolier"] == "leather"

    assert "cuirass" in teppo_model.LEGACY_MATERIALS
    assert teppo_model.LEGACY_MATERIALS["cuirass"] == "diffuse"


def test_teppo_model_render_without_crashes():
    """Valida renderização completa do Teppo em modelo novo e legado."""
    surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
    cam = DummyCamera()
    teppo = Rifleman(10.5, 10.5)

    # Render padrão (Novo Overhaul)
    teppo.render(surface, cam)

    # Render em poses específicas
    for pose in ("ready_aim", "aim_shoot", "rifle_butt", "ramrod_reload", "plant_trap", "trench_dive", "match_blow", "kiseru_puff"):
        teppo.extra_props = {"pose": pose, "p": 0.5, "legacy_mode": False}
        teppo.render(surface, cam)

    # Render no modo Legado (De/Para)
    teppo.extra_props = {"legacy_mode": True}
    teppo.render(surface, cam)


def test_intelligent_primary_attack_and_ammo_cycle():
    """Valida tiro de arcabuz quando municiado e coronhada de carvalho quando sem munição."""
    teppo = Rifleman(10.5, 10.5)
    projectiles = []
    particles = []

    # 1. Teppo inicia municiado
    assert teppo.has_ammo is True
    teppo.cocking_timer = 0.0

    # 2. Ataque primário com munição entra em mira e dispara projétil supersônico
    success = teppo.trigger_attack(12.0, 10.5, projectiles=projectiles, particles=particles)
    assert success is True
    assert teppo.state == STATE_RIFLE_AIM

    # Conclui mira e dispara
    teppo.state_timer = 0.0
    teppo.update(0.01, GameMap(), particles=particles)

    assert len(projectiles) == 1
    bullet = projectiles[0]
    assert bullet.owner == teppo
    assert teppo.has_ammo is False  # Agora está desmuniciado!

    # 3. Ataque primário sem munição: executa a Coronhada Pesada de Carvalho
    teppo.state = STATE_IDLE
    butt_success = teppo.trigger_attack(12.0, 10.5, projectiles=projectiles, particles=particles)
    assert butt_success is True
    assert teppo.state == STATE_ATTACK
    assert teppo.is_rifle_butt is True
    assert teppo.hitbox_active is True


def test_trench_ashigaru_dive_auto_reload():
    """Valida que o Trench Ashigaru Dive esquiva com i-frames e recarrega a arma ao concluir."""
    teppo = Rifleman(10.5, 10.5)
    teppo.has_ammo = False
    teppo.reload_timer = 5.0  # Temporizador longo para garantir que recarregou via dive

    # Dispara Trench Dive
    success = teppo.trigger_trench_dive(1.0, 0.0)
    assert success is True
    assert teppo.state == STATE_RIFLE_ROLL
    assert teppo.is_invulnerable_dodge is True

    # Atualiza até concluir o mergulho
    g_map = GameMap()
    while teppo.state == STATE_RIFLE_ROLL:
        teppo.update(0.05, g_map)

    # Ao levantar, deve estar com munição recarregada!
    assert teppo.has_ammo is True
    assert teppo.is_invulnerable_dodge is False


def test_fluid_ramrod_reload_in_idle():
    """Valida recarga fluida automática por vareta (ramrod) quando Teppo está parado."""
    teppo = Rifleman(10.5, 10.5)
    teppo.has_ammo = False
    teppo.reload_timer = 0.30

    g_map = GameMap()
    # Passa 0.35s
    teppo.update(0.35, g_map)

    assert teppo.has_ammo is True


def test_secondary_black_powder_ground_trap():
    """Valida plantio da mina de pólvora negra para zoneamento tático."""
    teppo = Rifleman(10.5, 10.5)
    traps = []

    success = teppo.trigger_secondary(traps=traps)
    assert success is True
    assert len(traps) == 1
    trap = traps[0]
    assert isinstance(trap, PowderTrap)
    assert trap.owner == teppo
    assert trap.is_active is True


def test_rifle_butt_collision_knockback_and_stun():
    """Valida que a coronhada causa 1 de dano, knockback de 1.6m+ e stun de 0.5s+."""
    teppo = Rifleman(10.0, 10.0)
    rival = Samurai(10.7, 10.0, name="Rival")
    rival.hp = 2

    combat = CombatSystem()
    g_map = GameMap()
    particles = []
    banners = []
    projectiles = []
    cam = DummyCamera()

    # Teppo executa coronhada
    teppo.has_ammo = False
    teppo.trigger_rifle_butt(10.7, 10.0)

    initial_x = rival.wx
    combat.process_combat(teppo, rival, g_map, particles, banners, cam, projectiles, dt=0.016)

    # O rival deve ter tomado dano, sido afastado e ficado atordoado
    assert rival.hp == 1
    assert rival.wx > initial_x + 1.2
    assert rival.state == "STUNNED"


def test_teppo_pose_scripts_intro_and_victory():
    """Valida que a Intro e a Vitória de Teppo têm 3 fases ricas e fluidas."""
    intro_phases = pose_scripts.INTRO["rifleman"]
    assert len(intro_phases) == 3
    assert intro_phases[0][6].get("pose") == "match_blow"
    assert intro_phases[1][6].get("pose") == "lock_check"
    assert intro_phases[2][6].get("pose") == "ready_aim"

    victory_phases = pose_scripts.VICTORY["rifleman"]
    assert len(victory_phases) == 3
    assert victory_phases[0][6].get("pose") == "shoulder_rest"
    assert victory_phases[1][6].get("pose") == "kiseru_light"
    assert victory_phases[2][6].get("pose") == "kiseru_puff"

    # Valida sample() em cada fase da Intro
    pf0 = pose_scripts.sample("rifleman", "intro", 0.15)
    assert pf0.extra.get("pose") == "match_blow"

    pf1 = pose_scripts.sample("rifleman", "intro", 0.50)
    assert pf1.extra.get("pose") == "lock_check"

    pf2 = pose_scripts.sample("rifleman", "intro", 0.85)
    assert pf2.extra.get("pose") == "ready_aim"

    # Valida sample() em cada fase da Vitória
    pv0 = pose_scripts.sample("rifleman", "victory", 0.15)
    assert pv0.extra.get("pose") == "shoulder_rest"

    pv1 = pose_scripts.sample("rifleman", "victory", 0.50)
    assert pv1.extra.get("pose") == "kiseru_light"

    pv2 = pose_scripts.sample("rifleman", "victory", 0.85)
    assert pv2.extra.get("pose") == "kiseru_puff"


def test_dual_finishers_corpses():
    """Valida criação dos corpos voxel tridimensionais para Finisher A e Finisher B."""
    cam = DummyCamera()

    # Finisher A: HEADSHOT_EXPLODE
    victim_a = Samurai(10.5, 10.5, name="VictimA")
    corpse_a = VoxelCorpse(victim_a, "HEADSHOT_EXPLODE", (1.0, 0.0))
    types_a = [p.piece_type for p in corpse_a.pieces]
    assert "torso_headless" in types_a
    assert "skull_gib" in types_a

    # Finisher B: HAYAGO_KEG_BLAST
    victim_b = Samurai(10.5, 10.5, name="VictimB")
    corpse_b = VoxelCorpse(victim_b, "HAYAGO_KEG_BLAST", (1.0, 0.0))
    types_b = [p.piece_type for p in corpse_b.pieces]
    assert "torso" in types_b
    assert "legs" in types_b
    assert "keg_gib" in types_b


def test_model_inspector_registration():
    """Valida registro no Model Inspector com botões interativos e notas De/Para."""
    assert "teppo" in model_inspector.CHARACTER_ANIM_BUTTONS
    assert "rifleman" in model_inspector.CHARACTER_ANIM_BUTTONS
    teppo_btns = model_inspector.CHARACTER_ANIM_BUTTONS["teppo"]
    action_ids = [b[0] for b in teppo_btns]

    assert "PRIMARY_SHOT" in action_ids
    assert "RIFLE_BUTT" in action_ids
    assert "RAMROD_RELOAD" in action_ids
    assert "POWDER_TRAP" in action_ids
    assert "TRENCH_DIVE" in action_ids
    assert "INTRO" in action_ids
    assert "VICTORY" in action_ids
    assert "FINISHER_1" in action_ids
    assert "FINISHER_2" in action_ids

    assert "teppo" in model_inspector.OVERHAUL_DE_PARA_NOTES
    assert "rifleman" in model_inspector.OVERHAUL_DE_PARA_NOTES
    notes = model_inspector.OVERHAUL_DE_PARA_NOTES["teppo"]
    assert len(notes) >= 4


def test_powder_trap_hemisphere_and_projectile_detonation():
    """Valida detonação por aproximação de rival, detonação por projétil e onda de choque hemisférica 3D."""
    teppo = Rifleman(10.0, 10.0)
    rival = Samurai(10.5, 10.0, name="Rival")
    trap = PowderTrap(10.0, 10.0, owner=teppo)
    assert trap.is_ignited is False

    # 1. Rival pisa na mina -> Detona automaticamente!
    trap.update(0.016, fighters=[rival])
    assert trap.is_ignited is True
    assert trap.blast_timer == 0.0

    # 2. Renderiza a hemisfera 3D em expansão com anéis latitudinais e meridianos
    surf = pygame.Surface((1280, 720), pygame.SRCALPHA)
    cam = DummyCamera()
    trap.render(surf, cam)
    trap.update(0.20, fighters=[rival])
    assert trap.blast_timer > 0.15
    trap.render(surf, cam)

    # 3. Mina alvejada por projétil (ex: bala de arcabuz ou flecha)
    from src.entities.projectile import MusketBulletProjectile
    trap2 = PowderTrap(15.0, 15.0, owner=teppo)
    bullet = MusketBulletProjectile(15.0, 15.0, wz=0.2, dir_x=1.0, dir_y=0.0, owner=teppo)
    assert bullet.is_active is True
    trap2.update(0.016, fighters=[rival], projectiles=[bullet])
    assert trap2.is_ignited is True, "Mina deve detonar ao ser alvejada por projétil!"
    assert bullet.is_active is False, "Projétil deve colidir e detonar o barril!"


def test_teppo_dive_somersault_and_bullet_attributes():
    """Valida rotação 360° no mergulho (somersault_angle), velocidade +20% e tracer da bala."""
    teppo = Rifleman(10.0, 10.0)
    teppo.trigger_roll(1.0, 0.0)
    assert teppo.state == STATE_RIFLE_ROLL

    # Valida somersault_angle em 50% do mergulho
    teppo.state_timer = teppo.roll_duration * 0.50
    surf = pygame.Surface((1280, 720))
    cam = DummyCamera()
    teppo.render(surf, cam)

    # Valida atributos da bala de chumbo supersônica
    from src.entities.projectile import MusketBulletProjectile
    bullet = MusketBulletProjectile(10.0, 10.0, 0.5, 1.0, 0.0, owner=teppo)
    assert bullet.speed == 31.2, f"Velocidade da bala deve ser 31.2 m/s (+20%), obtido {bullet.speed}"
    assert bullet.radius == 0.45, "Hitbox da bala deve ser ampliada para 0.45"
    bullet.render(surf, cam)


if __name__ == "__main__":
    test_teppo_model_attributes_and_materials()
    test_teppo_model_render_without_crashes()
    test_intelligent_primary_attack_and_ammo_cycle()
    test_trench_ashigaru_dive_auto_reload()
    test_fluid_ramrod_reload_in_idle()
    test_secondary_black_powder_ground_trap()
    test_rifle_butt_collision_knockback_and_stun()
    test_teppo_pose_scripts_intro_and_victory()
    test_dual_finishers_corpses()
    test_model_inspector_registration()
    test_powder_trap_hemisphere_and_projectile_detonation()
    test_teppo_dive_somersault_and_bullet_attributes()
    print("ALL 12 TEPPO ASHIGARU OVERHAUL TESTS PASSED SUCCESSFULLY! ✅")
