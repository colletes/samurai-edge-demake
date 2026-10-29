"""Teste da finalização cinematográfica do Oni Gashadokuro:

- Desabamento dos ossos (BONE_COLLAPSE).
- Irrupção de sombras roxas e névoa espectral (PURPLE_DISSOLVE).
- Desaparecimento gradual do esqueleto (alpha decresce até 0).
- Branqueamento total da tela (whiteout_alpha cresce até 255).
- Transição direta para os créditos ao concluir a dissolução.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT
from src.entities.boss_oni import BossOni
from src.effects.particles import SmokeParticle
from src.arcade.arcade_credits import ArcadeCreditsScreen


def test_boss_dissolve_sequence():
    pygame.init()
    boss = BossOni(10.5, 7.5, seed=42)
    assert boss.state != "BONE_COLLAPSE"
    assert boss.whiteout_alpha == 0.0
    assert not boss.dissolve_complete

    # 1. Início do colapso
    boss.begin_collapse()
    assert boss.state == "BONE_COLLAPSE"
    assert boss.alpha == 255
    assert boss.whiteout_alpha == 0.0
    assert not boss.dissolve_complete

    particles = []
    # 2. Passo antes do início das sombras (0.4s)
    boss.update(0.4, particles=particles)
    assert boss.state == "BONE_COLLAPSE"
    assert boss.whiteout_alpha == 0.0

    # 3. Transição para PURPLE_DISSOLVE (passando de 0.6s)
    boss.update(0.3, particles=particles)
    assert boss.state == "PURPLE_DISSOLVE"
    assert len(particles) > 0
    # Verifica que partículas púrpuras foram geradas
    smoke_particles = [p for p in particles if isinstance(p, SmokeParticle)]
    assert len(smoke_particles) > 0
    # Pelo menos uma partícula tem componente azul/vermelho característico de roxo
    has_purple = any(p.color[0] > 50 and p.color[2] > 100 for p in smoke_particles)
    assert has_purple, "Deveria ter gerado partículas em tons de sombra roxa/violeta"

    # 4. Progressão da dissolução (mais 1.5s): esqueleto desaparece e branco sobe
    boss.update(1.5, particles=particles)
    assert boss.alpha < 255, f"Alpha deveria estar decrescendo: {boss.alpha}"
    assert boss.whiteout_alpha > 0.0, f"Whiteout deveria estar subindo: {boss.whiteout_alpha}"
    assert not boss.dissolve_complete

    # 5. Conclusão total da dissolução (mais 1.5s): esqueleto sumiu e tela 100% branca
    boss.update(1.5, particles=particles)
    assert boss.alpha == 0, f"Alpha final deveria ser 0: {boss.alpha}"
    assert boss.whiteout_alpha >= 254.0, f"Whiteout final deveria ser 255: {boss.whiteout_alpha}"
    assert boss.dissolve_complete is True


def test_arcade_credits_white_fade_in():
    pygame.init()
    scr = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    credits = ArcadeCreditsScreen()
    credits.open(None, white_fade_in=True)
    assert credits.white_fade_in is True
    # Renderizar frame inicial (slide_timer = 0.0)
    credits.render(scr)
    # No centro da tela com fade branco puro, a cor deve ter alta luminância branca
    c = scr.get_at((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    # Com alpha máximo do fade branco inicial, o pixel não deve ser escuro
    assert (c.r + c.g + c.b) > 300, f"Deveria ter overlay branco sobre o slide: {c}"


if __name__ == "__main__":
    test_boss_dissolve_sequence()
    test_arcade_credits_white_fade_in()
    print("test_boss_dissolve OK")
