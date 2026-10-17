"""
Testes automatizados para as Arenas do Ciclo 3 e Revamps Visuais:
- Rice Paddies (Terraços de Arroz - Goro)
- Rain Mill (Moinho sob Chuva - Ichi)
- Revamp Visual de Ganryu Island (Dunas, capim de praia, névoa costeira)
- Revamp Visual de Iga Rooftops (Névoa noturna de alto contraste, telhas)
- Integração completa com ArenaSelectScreen e i18n
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.config import (
    ARENA_RICE_PADDIES, ARENA_RAIN_MILL, ARENA_GANRYU, ARENA_IGA
)
from src.world.arenas import create_arena, ARENA_SPECS, arena_ids
from src.world.decor import Scarecrow, HayBale, WaterMillWheel, DuneGrass
from src.ui.arena_select import ArenaSelectScreen
from src.i18n import set_lang, t


def test_rice_paddies_spec_and_instance():
    pygame.init()
    arena = create_arena(ARENA_RICE_PADDIES)
    assert arena is not None, "create_arena(ARENA_RICE_PADDIES) retornou None"
    assert arena.spec.id == ARENA_RICE_PADDIES
    assert arena.spec.cols == 22 and arena.spec.rows == 22
    assert arena.spec.music == "bgm_rice_paddies"

    # Props no spec
    prop_kinds = [p.kind for p in arena.spec.props]
    assert "scarecrow" in prop_kinds, "Rice Paddies deve conter scarecrow"
    assert "hay_bale" in prop_kinds, "Rice Paddies deve conter hay_bale"

    # Verifica instâncias nos collections do mapa
    assert any(isinstance(p, Scarecrow) for p in arena.lanterns), "lanterns deve instanciar Scarecrow"
    assert any(isinstance(p, HayBale) for p in arena.rocks), "rocks deve instanciar HayBale"

    # Efeitos atmosféricos
    atmos = [a.kind for a in arena.spec.lighting.atmosphere]
    assert "dust" in atmos or "mist" in atmos
    assert arena.spec.drift_count >= 30

    # Spawns seguros
    p1, p2 = arena.pick_spawns()
    assert arena.pit_at(p1[0], p1[1]) is None, "Spawn 1 não pode estar em pit"
    assert arena.pit_at(p2[0], p2[1]) is None, "Spawn 2 não pode estar em pit"


def test_rain_mill_spec_and_instance():
    pygame.init()
    arena = create_arena(ARENA_RAIN_MILL)
    assert arena is not None, "create_arena(ARENA_RAIN_MILL) retornou None"
    assert arena.spec.id == ARENA_RAIN_MILL
    assert arena.spec.cols == 22 and arena.spec.rows == 22
    assert arena.spec.music == "bgm_rain_mill"

    # Clima chuva densa
    atmos = [a.kind for a in arena.spec.lighting.atmosphere]
    assert "rain" in atmos
    assert arena.spec.drift_count >= 40

    # Roda d'água monumental
    prop_kinds = [p.kind for p in arena.spec.props]
    assert "watermill" in prop_kinds, "Rain Mill deve conter watermill"
    mill_props = [p for p in arena.buildings if isinstance(p, WaterMillWheel)]
    assert len(mill_props) >= 1, "Deve haver pelo menos um WaterMillWheel instanciado"

    # Rio turbulento como abismo VOID
    assert len(arena.spec.pits) >= 1, "Rain Mill deve ter abismo no rio"
    has_void_pit = any(p.gap_class == "VOID" for p in arena.spec.pits)
    assert has_void_pit, "Rain Mill deve possuir pelo menos um pit de classe VOID no rio"

    # Posições de spawn fora do rio
    p1, p2 = arena.pick_spawns()
    assert arena.pit_at(p1[0], p1[1]) is None, "Spawn 1 não pode estar no leito do rio"
    assert arena.pit_at(p2[0], p2[1]) is None, "Spawn 2 não pode estar no leito do rio"


def test_revamps_ganryu_and_iga():
    pygame.init()
    # Ganryu Island Revamp
    ganryu = create_arena(ARENA_GANRYU)
    ganryu_props = [p.kind for p in ganryu.spec.props]
    assert "dune_grass" in ganryu_props, "Ganryu Island deve ter props dune_grass"
    assert "boat" in ganryu_props, "Ganryu Island deve ter prop boat"
    ganryu_atmos = [a.kind for a in ganryu.spec.lighting.atmosphere]
    assert "mist" in ganryu_atmos
    assert ganryu.spec.drift_count >= 40

    # Iga Rooftops Revamp
    iga = create_arena(ARENA_IGA)
    iga_atmos = [a.kind for a in iga.spec.lighting.atmosphere]
    assert "mist" in iga_atmos or "fogbank" in iga_atmos
    assert iga.spec.drift_count >= 45
    iga_props = [p.kind for p in iga.spec.props]
    assert "solid_block" in iga_props, "Iga Rooftops deve ter blocos sólidos de telhado"


def test_arena_select_integration_cycle3():
    pygame.init()
    pygame.font.init()
    screen = ArenaSelectScreen()

    rice_card = next((c for c in screen.arenas if c["id"] == ARENA_RICE_PADDIES), None)
    assert rice_card is not None, "Arena Rice Paddies deve existir na tela de seleção"
    assert not rice_card["locked"], "Arena Rice Paddies deve estar desbloqueada"
    assert rice_card["theme_color"] != (108, 102, 96), "Rice Paddies deve ter theme_color específico"

    mill_card = next((c for c in screen.arenas if c["id"] == ARENA_RAIN_MILL), None)
    assert mill_card is not None, "Arena Rain Mill deve existir na tela de seleção"
    assert not mill_card["locked"], "Arena Rain Mill deve estar desbloqueada"
    assert mill_card["theme_color"] != (108, 102, 96), "Rain Mill deve ter theme_color específico"

    # Teste de i18n em ambos idiomas
    for lang in ("pt", "en"):
        set_lang(lang)
        screen = ArenaSelectScreen()
        r_card = next(c for c in screen.arenas if c["id"] == ARENA_RICE_PADDIES)
        m_card = next(c for c in screen.arenas if c["id"] == ARENA_RAIN_MILL)

        assert len(r_card["name"]) > 0 and len(r_card["subtitle"]) > 0
        assert len(r_card["hazard_level"]) > 0 and len(r_card["features"]) > 0
        assert len(m_card["name"]) > 0 and len(m_card["subtitle"]) > 0
        assert len(m_card["hazard_level"]) > 0 and len(m_card["features"]) > 0


def test_cycle3_arena_music_playback():
    from src.audio.sound_manager import SoundManager
    sm = SoundManager()
    assert sm._play_music_file("bgm_rice_paddies") is True, "Falha ao carregar bgm_rice_paddies.mp3"
    assert sm._play_music_file("bgm_rain_mill") is True, "Falha ao carregar bgm_rain_mill.mp3"


if __name__ == "__main__":
    print("Executando test_rice_paddies_spec_and_instance...")
    test_rice_paddies_spec_and_instance()
    print("Executando test_rain_mill_spec_and_instance...")
    test_rain_mill_spec_and_instance()
    print("Executando test_revamps_ganryu_and_iga...")
    test_revamps_ganryu_and_iga()
    print("Executando test_arena_select_integration_cycle3...")
    test_arena_select_integration_cycle3()
    print("Executando test_cycle3_arena_music_playback...")
    test_cycle3_arena_music_playback()
    print("Todos os testes de arenas do Ciclo 3 passaram com sucesso!")
