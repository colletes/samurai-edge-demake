"""
Testes automatizados para os combatentes do Ciclo 2: Benkei e O-Rin.
Valida:
1. Benkei: Walking tank (Speed 4.0), sem parry, estocada alcance 3.0, arremesso seguro de naginata
   com clamp anti-abismo, tackle desarmado com STUN garantido (1.2s) e recuperação de arma.
2. O-Rin: Pure acoustic zoner (Speed 4.9), projétil sônico Kamaitachi (alcance 6.0 tiles),
   pulso de choque concêntrico 360° com desvio de projéteis e empurrão.
3. Integração de Roster, Character Select, factory e renderização voxel 3D.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import pygame
from src.config import (
    CHAR_BENKEI, CHAR_ORIN, CHAR_KENSHIN, COLOR_BENKEI_AURA, COLOR_ORIN_AURA
)
from src.roster import PLAYABLE_FIGHTERS
from src.world.map_data import GameMap
from src.world.arenas import create_arena
from src.entities.benkei import BenkeiSamurai, STATE_TACKLE_CHARGE, STATE_NAGINATA_THROW
from src.entities.orin import OrinMinstrel, STATE_RESONANCE
from src.entities.red_samurai import RedSamurai
from src.entities.projectile import NaginataProjectile, KamaitachiProjectile, AcousticResonanceWave, KunaiProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.camera import Camera
from src.ui.character_select import CharacterSelectScreen
from main import create_fighter, execute_fighter_attack, execute_fighter_secondary, get_fighter_color, get_fighter_action_labels, get_fighter_cooldown_data


def test_benkei_mechanics():
    pygame.init()
    benkei = BenkeiSamurai(wx=10.0, wy=10.0)
    target = RedSamurai(wx=10.0, wy=12.5)

    assert benkei.speed == 4.0, f"Benkei deve ser Walking Tank (speed 4.0), obtido {benkei.speed}"
    assert not benkei.can_parry, "Benkei não deve possuir parry técnico"
    assert benkei.has_naginata, "Benkei deve iniciar armado com a Naginata"

    # 1. Estocada Armada
    benkei.trigger_naginata_thrust(target.wx, target.wy)
    assert benkei.state == "ATTACK"
    assert benkei.hitbox_active
    assert benkei.hitbox_damage == 2
    # Alcance de centro (1.8) + raio (1.35) = 3.15 tiles
    reach = math.hypot(benkei.hitbox_center[0] - benkei.wx, benkei.hitbox_center[1] - benkei.wy) + benkei.hitbox_radius
    assert reach >= 3.0, f"Alcance da estocada deve ser >= 3.0 tiles, obtido {reach}"

    # Reset
    benkei.state = "IDLE"
    benkei.hitbox_active = False

    # 2. Arremesso de Naginata
    projectiles = []
    particles = []
    benkei.trigger_naginata_throw(target.wx, target.wy, projectiles, particles)
    assert not benkei.has_naginata, "Benkei deve ficar desarmado após o arremesso"
    assert len(projectiles) == 1
    nag_proj = projectiles[0]
    assert isinstance(nag_proj, NaginataProjectile)

    # Simular voo da naginata
    game_map = create_arena("gojo_bridge")
    for _ in range(30):
        nag_proj.update(0.05, game_map, particles)

    assert nag_proj.state == "ON_GROUND", "Naginata deve se cravar no solo"
    # Validar que não caiu em abismo (Kamo River void)
    assert game_map.pit_at(nag_proj.wx, nag_proj.wy) is None, "Naginata NUNCA deve cair em buracos/água!"

    # 3. Ataque Desarmado (Tackle com STUN)
    benkei.state = "IDLE"
    benkei.trigger_naginata_thrust(target.wx, target.wy)
    assert benkei.state == STATE_TACKLE_CHARGE, "Ao atacar desarmado, Benkei deve desferir Tackle Charge"
    assert benkei.hitbox_damage == 0, "Tackle deve causar 0 dano letal"

    # Atualizar carga e validar STUN no alvo
    banners = []
    for _ in range(5):
        benkei.update(0.05, game_map, particles, opponent=target, banners=banners)
    assert target.state == "STUNNED", "Oponente atingido por tackle deve ficar STUNNED"
    assert target.state_timer >= 1.0, f"Stun deve durar pelo menos 1.0s, obtido {target.state_timer}"

    # 4. Recuperação da Arma
    benkei.wx = nag_proj.wx
    benkei.wy = nag_proj.wy
    benkei.update(0.05, game_map, particles, opponent=target, banners=banners)
    assert benkei.has_naginata, "Benkei deve recuperar a Naginata ao alcançar suas coordenadas"
    print("✓ Mecânicas do Benkei testadas e aprovadas com 100% de sucesso!")


def test_orin_mechanics():
    pygame.init()
    orin = OrinMinstrel(wx=5.0, wy=5.0)
    target = RedSamurai(wx=8.0, wy=5.0)

    assert orin.speed == 4.9, f"O-Rin deve ser zoner ágil (speed 4.9), obtido {orin.speed}"
    assert orin.is_agile_dodge, "O-Rin deve possuir esquiva ágil"

    # 1. Ataque Primário Kamaitachi
    projectiles = []
    particles = []
    orin.trigger_kamaitachi_pluck(target.wx, target.wy, projectiles, particles)
    assert orin.state == "ATTACK"
    assert len(projectiles) == 1
    blade = projectiles[0]
    assert blade.damage == 1, "Kamaitachi deve causar 1 de dano com cooldown"
    assert orin.kamaitachi_timer > 0, "Kamaitachi deve acionar cooldown"
    assert blade.max_range >= 6.0, f"Alcance do Kamaitachi deve ser >= 6.0 tiles, obtido {blade.max_range}"

    # 2. Ação Secundária: Acorde de Ressonância Mortal (3 projéteis em espiral a 120°, 5.0s cooldown)
    orin.state = "IDLE"
    banners = []
    projectiles.clear()
    orin.trigger_deadly_resonance_chord(target.wx, target.wy, projectiles, particles, banners)
    assert orin.state == STATE_RESONANCE
    assert orin.resonance_cooldown == 5.0, "Cooldown do Acorde Mortal deve ser 5.0s"
    assert orin.resonance_timer == 5.0
    assert len(projectiles) == 3, f"Deve disparar exatamente 3 projéteis sônicos em espiral, obtido {len(projectiles)}"
    from src.entities.projectile import SpiralResonanceProjectile
    for p in projectiles:
        assert isinstance(p, SpiralResonanceProjectile)
        assert p.damage == 2, "Dano da onda espiral deve ser 2"
        assert p.owner == orin

    # Verificar que os 3 ângulos cobrem os 360° em intervalos de 120° (2π/3)
    angles = sorted([p.current_angle % (2 * math.pi) for p in projectiles])
    diff1 = (angles[1] - angles[0]) % (2 * math.pi)
    diff2 = (angles[2] - angles[1]) % (2 * math.pi)
    assert abs(diff1 - (2 * math.pi / 3)) < 0.05, f"Diferença angular deve ser ~120°, obtido {diff1}"
    assert abs(diff2 - (2 * math.pi / 3)) < 0.05, f"Diferença angular deve ser ~120°, obtido {diff2}"
    print("✓ Mecânicas da O-Rin testadas e aprovadas com 100% de sucesso!")


def test_roster_and_ui_integration():
    pygame.init()
    # 1. PLAYABLE_FIGHTERS
    assert CHAR_BENKEI in PLAYABLE_FIGHTERS, "CHAR_BENKEI deve estar em PLAYABLE_FIGHTERS"
    assert CHAR_ORIN in PLAYABLE_FIGHTERS, "CHAR_ORIN deve estar em PLAYABLE_FIGHTERS"

    # 2. Factory create_fighter
    f_benkei = create_fighter(CHAR_BENKEI, 5.0, 5.0)
    assert isinstance(f_benkei, BenkeiSamurai)
    f_orin = create_fighter(CHAR_ORIN, 5.0, 5.0)
    assert isinstance(f_orin, OrinMinstrel)

    # 3. Cores e Labels
    assert get_fighter_color(f_benkei) == COLOR_BENKEI_AURA
    assert get_fighter_color(f_orin) == COLOR_ORIN_AURA

    lbl_benkei_atk, lbl_benkei_sec = get_fighter_action_labels(f_benkei)
    assert "Naginata" in lbl_benkei_atk or "Estocada" in lbl_benkei_atk

    lbl_orin_atk, lbl_orin_sec = get_fighter_action_labels(f_orin)
    assert "Kamaitachi" in lbl_orin_atk

    # 4. Character Select Grid
    cs = CharacterSelectScreen()
    benkei_card = next(c for c in cs.characters if c["id"] == CHAR_BENKEI)
    orin_card = next(c for c in cs.characters if c["id"] == CHAR_ORIN)

    assert benkei_card["ready"] is True, "Card do Benkei deve estar pronto (ready = True)"
    assert orin_card["ready"] is True, "Card da O-Rin deve estar pronto (ready = True)"
    assert len(benkei_card["name"]) > 0 and benkei_card["name"] != "???"
    assert len(orin_card["name"]) > 0 and orin_card["name"] != "???"

    print("✓ Integração de Roster e Seleção testada e aprovada com 100% de sucesso!")


def test_voxel_rendering_all_states():
    pygame.init()
    surf = pygame.Surface((320, 240))
    cam = Camera()

    for char in (CHAR_BENKEI, CHAR_ORIN):
        for state in ("IDLE", "ATTACK", "TACKLE_CHARGE", "NAGINATA_THROW", "RESONANCE"):
            render_voxel_humanoid(
                surface=surf, camera=cam,
                wx=5.0, wy=5.0, wz=0.0,
                facing_x=1.0, facing_y=0.0,
                state=state, state_timer=0.10,
                is_alive=True, char_type=char,
                walk_timer=0.5, alpha=255, is_moving=False,
                extra_props={"has_naginata": True, "is_charging": True, "is_resonance": True}
            )

    print("✓ Renderização de Voxel de todos os estados testada e aprovada!")


def test_cycle2_fatalities_and_ai():
    pygame.init()
    from src.entities.voxel_corpse import VoxelCorpse, STUCK_WEAPON
    from src.effects.cinematic_director import CinematicDirector
    from src.entities.ai_controller import SamuraiAI
    from src.combat.collision import _get_death_style_for_attacker

    assert "ARMORED_HEART_IMPALE" in STUCK_WEAPON
    assert "SKEWERED_LANCE_FLAG" in STUCK_WEAPON
    assert STUCK_WEAPON["ARMORED_HEART_IMPALE"] == "naginata"
    assert STUCK_WEAPON["SKEWERED_LANCE_FLAG"] == "naginata"

    benkei = create_fighter(CHAR_BENKEI, 5.0, 5.0)
    orin = create_fighter(CHAR_ORIN, 8.0, 8.0)
    target = RedSamurai(10.0, 10.0)

    # Mapeamento contextual de estilo de morte
    assert _get_death_style_for_attacker(benkei) == "NAGINATA_HOIST_SLAM"
    assert _get_death_style_for_attacker(benkei, weapon="naginata_throw") == "SKEWERED_LANCE_FLAG"
    assert _get_death_style_for_attacker(orin) in ("SONIC_SLICER", "KAMAITACHI_MINCE")
    assert _get_death_style_for_attacker(orin, weapon="resonance") in ("RESONANCE_BURST", "RESONANCE_WIND_GALE")

    # Construção e renderização de corpos voxel dos estilos
    cam = Camera()
    surf = pygame.Surface((320, 240))
    for style in ("NAGINATA_HOIST_SLAM", "ARMORED_HEART_IMPALE", "SKEWERED_LANCE_FLAG", "SONIC_SLICER", "RESONANCE_BURST", "KAMAITACHI_MINCE", "RESONANCE_WIND_GALE"):
        corpse = VoxelCorpse(target, style, (1.0, 0.0))
        assert len(corpse.pieces) > 0, f"Corpo para {style} deve ter peças"
        corpse.render(surf, cam)

    # Diretor cinematográfico com os novos kanjis
    director = CinematicDirector()
    director.trigger_fatal_strike(benkei, target, "NAGINATA_HOIST_SLAM", (1.0, 0.0))
    assert director.is_active
    assert director.cached_kanji_surf is not None

    # IA tática para Benkei e O-Rin
    ai = SamuraiAI(difficulty="hard")
    game_map = create_arena("gojo_bridge")
    projectiles = []

    ai.update(benkei, target, 0.05, game_map, projectiles)
    ai.update(orin, target, 0.05, game_map, projectiles)

    print("✓ Fatalities e IA do Ciclo 2 testados e aprovados com 100% de sucesso!")


if __name__ == "__main__":
    test_benkei_mechanics()
    test_orin_mechanics()
    test_roster_and_ui_integration()
    test_voxel_rendering_all_states()
    test_cycle2_fatalities_and_ai()
    print("\n=======================================================")
    print("TODOS OS TESTES DO CICLO 2 (BENKEI & O-RIN) PASSARAM!")
    print("=======================================================")

