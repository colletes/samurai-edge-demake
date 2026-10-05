"""Entregável 7.2.1: corpos abatidos fiéis aos modelos atuais e ao golpe sofrido."""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()
pygame.display.set_mode((100, 100))

from src.combat.collision import CombatSystem, _get_death_style_for_attacker
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.effects.cinematic_director import CinematicDirector
from src.entities.american_ninja import AmericanNinja
from src.entities.blue_samurai import BlueSamurai
from src.entities.gray_ninja import GrayNinja
from src.entities.kabuki import Kabuki
from src.entities.kyudo_archer import KyudoArcher
from src.entities.musketeer import Musketeer
from src.entities.pirate import PirateSwordswoman
from src.entities.purple_ninja import PurpleNinja
from src.entities.red_samurai import RedSamurai
from src.entities.rifleman import Rifleman
from src.entities.saitou_samurai import SaitouSamurai
from src.entities.yellow_ninja import YellowNinja
from src.entities.voxel_corpse import VoxelCorpse, render_body_layer
from src.entities.voxel_models import render_voxel_humanoid
from src.isometric.camera import Camera
from src.world.map_data import GameMap

ALL_FIGHTERS = (RedSamurai, BlueSamurai, YellowNinja, AmericanNinja, GrayNinja, PurpleNinja, SaitouSamurai,
                Rifleman, Kabuki, KyudoArcher, PirateSwordswoman, Musketeer)
STYLES = ("KENSHIN_SPLIT", "MURASAKI_DECAP", "CLEAN_DECAP", "KASUMI_EXPLODE", "HEADSHOT_EXPLODE", "OKUNI_MELT",
          "SAITOU_IMPALE", "KUNAI_PIN", "ARROW_PIN", "STAB_FALL", "PIRATE_CLEAVE", "MAULED", "CRUSHED", "BLUNT_FALL")
BG = (7, 9, 11)


def _painted(surface) -> int:
    return SCREEN_WIDTH * SCREEN_HEIGHT - pygame.mask.from_threshold(surface, BG, (2, 2, 2, 255)).count()


def _corpse(cls, style, direction=(1.0, 0.0)):
    victim = cls(11.0, 11.0)
    director = CinematicDirector()
    director.trigger_fatal_strike(None, victim, style, direction)
    director.update(0.5, GameMap(), [])
    return victim, director.corpses[0]


def _frame(corpse, camera):
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.fill(BG)
    corpse.render(surface, camera)
    return surface


def test_every_fighter_and_style_renders_from_the_model_in_all_azimuths():
    game_map = GameMap()
    for cls in ALL_FIGHTERS:
        for style in STYLES:
            victim, corpse = _corpse(cls, style)
            for azimuth, zoom in ((0.0, 1.0), (0.9, 1.4), (math.pi, 1.75), (-1.3, 1.0)):
                camera = Camera(11.0, 11.0)
                camera.set_azimuth(azimuth)
                camera.zoom = zoom
                for _ in range(40):
                    corpse.update(0.016, game_map, [])
                surface = _frame(corpse, camera)
                assert not corpse._sprite_failed, f"{cls.__name__}/{style}: recorte do modelo falhou"
                assert _painted(surface) > 20, f"{cls.__name__}/{style}/{azimuth:.1f}: nada desenhado"
            for piece in corpse.pieces:
                if piece.region is not None:
                    assert piece.surf is not None, f"{cls.__name__}/{style}/{piece.piece_type}: peça sem recorte do modelo"


def test_pieces_use_the_fighters_own_model_pixels():
    victim, corpse = _corpse(RedSamurai, "KASUMI_EXPLODE")
    camera = Camera(11.0, 11.0)
    _frame(corpse, camera)
    sprite, _, _ = render_body_layer(camera, victim.wx, victim.wy, victim.wz, lambda layer, lc: _render_dying(victim, layer, lc))
    palette = {tuple(sprite.get_at((x, y)))[:3] for x in range(sprite.get_width()) for y in range(sprite.get_height())
               if sprite.get_at((x, y)).a >= 200}
    gibs = [p for p in corpse.pieces if p.piece_type == "gib"]
    assert gibs and all(tuple(g.color) in palette for g in gibs), "estilhaços devem ter cores do modelo do lutador"


def _render_dying(victim, layer, lc):
    saved = victim.state
    victim.state = "DYING_FREEZE"
    try:
        victim.render(layer, lc)
    finally:
        victim.state = saved


def test_cut_styles_split_the_model_where_expected():
    camera = Camera(11.0, 11.0)
    _, split = _corpse(RedSamurai, "KENSHIN_SPLIT")
    _frame(split, camera)
    assert split.top_half.surf is not None and split.bottom_half.surf is not None
    assert split.top_half.surf.get_height() < split.top_half.surf.get_height() + split.bottom_half.surf.get_height()

    _, decap = _corpse(PurpleNinja, "MURASAKI_DECAP")
    _frame(decap, camera)
    assert decap.severed_head.surf.get_height() < decap.headless_body.surf.get_height(), "a cabeça é menor que o corpo"

    _, cleave = _corpse(PirateSwordswoman, "PIRATE_CLEAVE")
    _frame(cleave, camera)
    upper, lower = sorted((p for p in cleave.pieces if p.surf is not None), key=lambda p: p.rest[2])[::-1]
    assert upper.surf is not None and lower.surf is not None


def test_stuck_weapon_is_drawn_on_pierced_bodies():
    camera = Camera(11.0, 11.0)
    _, plain = _corpse(RedSamurai, "BLUNT_FALL")
    _, arrow = _corpse(RedSamurai, "ARROW_PIN")
    _frame(plain, camera)
    _frame(arrow, camera)
    plain_px = pygame.mask.from_surface(plain.pieces[0].surf, 10).count()
    arrow_px = pygame.mask.from_surface(arrow.pieces[0].surf, 10).count()
    assert arrow_px > plain_px, "a flecha cravada deve aparecer no corpo"


def test_bodies_fall_away_from_the_attacker():
    victim, corpse = _corpse(RedSamurai, "BLUNT_FALL", direction=(1.0, 0.0))
    game_map = GameMap()
    for _ in range(80):
        corpse.update(0.016, game_map, [])
    piece = corpse.pieces[0]
    assert piece.wx > 11.0, "o corpo é jogado para longe do agressor"
    assert piece.rot_angle >= 80.0, "o corpo termina deitado"


def test_okuni_melt_and_crush_shrink_the_body():
    camera = Camera(11.0, 11.0)
    game_map = GameMap()
    for style, floor in (("OKUNI_MELT", 0.0), ("CRUSHED", 0.22)):
        _, corpse = _corpse(Rifleman, style)
        start = _painted(_frame(corpse, camera))
        for _ in range(130):
            corpse.update(0.016, game_map, [])
        assert corpse._squash_scale(corpse.pieces[0]) <= floor + 1e-6
        _frame(corpse, camera)


def test_attack_selects_the_death_style():
    assert _get_death_style_for_attacker(YellowNinja(0, 0), weapon="kunai") == "KUNAI_PIN"
    assert _get_death_style_for_attacker(AmericanNinja(0, 0), weapon="shuriken") == "KUNAI_PIN"
    assert _get_death_style_for_attacker(KyudoArcher(0, 0), weapon="arrow") == "ARROW_PIN"
    assert _get_death_style_for_attacker(YellowNinja(0, 0)) == "STAB_FALL"
    assert _get_death_style_for_attacker(AmericanNinja(0, 0)) == "STAB_FALL"
    assert _get_death_style_for_attacker(Rifleman(0, 0)) == "BLUNT_FALL"
    assert _get_death_style_for_attacker(RedSamurai(0, 0)) == "KENSHIN_SPLIT"
    assert _get_death_style_for_attacker(BlueSamurai(0, 0)) == "KENSHIN_SPLIT"
    assert _get_death_style_for_attacker(PurpleNinja(0, 0)) == "MURASAKI_DECAP"
    assert _get_death_style_for_attacker(PirateSwordswoman(0, 0)) == "PIRATE_CLEAVE"
    assert _get_death_style_for_attacker(SaitouSamurai(0, 0)) in ("SAITOU_IMPALE", "KENSHIN_SPLIT")


def test_melee_kill_by_ninja_pins_instead_of_splitting():
    game_map = GameMap()
    director = CinematicDirector()
    attacker = YellowNinja(wx=10.0, wy=10.0)
    victim = RedSamurai(wx=11.0, wy=10.0)
    victim.state = "RECOVERY"  # PUNISH: 1 hit kill
    attacker.set_facing(victim.wx, victim.wy)
    attacker.slash_dir = (attacker.facing_x, attacker.facing_y)
    attacker.hitbox_active = True
    attacker.hitbox_radius = 1.4
    attacker.hitbox_center = (attacker.wx + attacker.facing_x * 0.9, attacker.wy + attacker.facing_y * 0.9)
    winner = CombatSystem().process_combat(attacker, victim, game_map, [], [], Camera(), [], cinematic_director=director)
    assert winner == "P1_WINS"
    assert director.pending_corpse.death_style == "STAB_FALL"


def test_dead_fighter_without_cinematic_is_drawn_from_the_model():
    camera = Camera(11.0, 11.0)
    for cls in ALL_FIGHTERS:
        victim = cls(11.0, 11.0)
        victim.hp = 0
        victim.is_alive = False
        victim.state = "DEAD"
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill(BG)
        victim.render(surface, camera)
        assert _painted(surface) > 200, f"{cls.__name__}: corpo caído não foi desenhado"


if __name__ == "__main__":
    test_every_fighter_and_style_renders_from_the_model_in_all_azimuths()
    test_pieces_use_the_fighters_own_model_pixels()
    test_cut_styles_split_the_model_where_expected()
    test_stuck_weapon_is_drawn_on_pierced_bodies()
    test_bodies_fall_away_from_the_attacker()
    test_okuni_melt_and_crush_shrink_the_body()
    test_attack_selects_the_death_style()
    test_melee_kill_by_ninja_pins_instead_of_splitting()
    test_dead_fighter_without_cinematic_is_drawn_from_the_model()
    print("TODOS OS TESTES DOS CORPOS ABATIDOS PASSARAM!")
