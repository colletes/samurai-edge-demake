"""
Entregável 8.2.7: calibração do Oni Gashadokuro. A IA de cada lutador enfrenta o chefe em muitas execuções com semente e
o script mede a taxa de vitória e a fase alcançada. Ajuste `BOSS_TUNING` (src/entities/boss_oni.py) e registre o
resultado em BALANCE_REPORT_boss.md.

Uso: python3 tools/simulate_boss.py [execuções por lutador] [easy|normal|hard]
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import pygame

pygame.init()
pygame.display.set_mode((1280, 720))

import math

from main import create_fighter, execute_fighter_attack, execute_fighter_roll
from simulate_tournament import update_fighter
from src.combat.collision import CombatSystem
from src.config import ARENA_GASHADOKURO, CHAR_BOSS
from src.entities.ai_controller import SamuraiAI
from src.entities.boss_oni import BossOni
from src.entities.pickups import PowderPouch
from src.isometric.camera import Camera
from src.roster import ROSTER_ORDER
from src.world.arenas import create_arena

DT = 0.016
MAX_TIME = 150.0
REACTION = 0.3   # atraso humano para começar a desviar de um aviso
STRIKE_RANGE = 1.7


class BossBot:
    """Jogador roteirizado que sabe do telégrafo: foge das áreas avisadas, rola nos anéis e ataca nas janelas de dano."""

    def __init__(self, fighter, boss, game_map):
        self.f, self.boss, self.map = fighter, boss, game_map

    def _flee(self, cx, cy):
        dx, dy = self.f.wx - cx, self.f.wy - cy
        n = math.hypot(dx, dy) or 1.0
        return dx / n, dy / n

    def threat(self):
        f, boss = self.f, self.boss
        for h in boss.hazards:
            if h.t < REACTION and h.kind != "ring":
                continue
            if h.kind == "circle" and math.hypot(f.wx - h.x, f.wy - h.y) < h.shape["r"] + 0.8:
                return self._flee(h.x, h.y), False
            if h.kind == "sector" and math.hypot(f.wx - h.x, f.wy - h.y) < h.shape["r"] + 0.8:
                return self._flee(h.x, h.y), h.is_active
            if h.kind == "ring":
                r = h.radius_now()
                if abs(math.hypot(f.wx - h.x, f.wy - h.y) - (r - h.shape["width"] / 2)) < 1.2:
                    return self._flee(h.x, h.y), True
            if h.kind == "path":
                pts = h.shape["points"]
                near = min(pts, key=lambda p: math.hypot(f.wx - p[0], f.wy - p[1]))
                if math.hypot(f.wx - near[0], f.wy - near[1]) < 1.8:
                    return self._flee(*near), False
            if h.kind == "arrow":
                ax, ay = h.shape["dx"], h.shape["dy"]
                rel = (f.wx - h.x, f.wy - h.y)
                along, side = rel[0] * ax + rel[1] * ay, rel[0] * -ay + rel[1] * ax
                if 0 < along < h.shape["len"] and abs(side) < 1.6:
                    return (-ay * (1 if side >= 0 else -1), ax * (1 if side >= 0 else -1)), False
        if boss.sub in ("run", "bounce") and math.hypot(f.wx - boss.wx, f.wy - boss.wy) < 3.0:
            return self._flee(boss.wx, boss.wy), False
        return None, False

    def act(self, dt, projectiles, particles):
        f, boss = self.f, self.boss
        move, roll = self.threat()
        if move is not None:
            if roll:
                execute_fighter_roll(f, move[0], move[1], boss.wx, boss.wy, particles, game_map=self.map)
            f.apply_movement(move[0], move[1], dt, self.map)
            return
        dist = math.hypot(boss.wx - f.wx, boss.wy - f.wy)
        if boss.vulnerable and not boss.transforming:
            if dist > STRIKE_RANGE:
                f.apply_movement((boss.wx - f.wx) / dist, (boss.wy - f.wy) / dist, dt, self.map)
            else:
                f.set_facing(boss.wx, boss.wy)
                if f.can_act():
                    execute_fighter_attack(f, boss.wx, boss.wy, projectiles, particles)
        elif dist < 4.5:
            f.apply_movement(-(boss.wx - f.wx) / dist, -(boss.wy - f.wy) / dist, dt, self.map)


def fight(char_id: str, seed: int, difficulty: str = "normal"):
    """Uma luta completa, sem Continues. Devolve (venceu, fase mais alta (0 a 4), duração)."""
    game_map = create_arena(ARENA_GASHADOKURO)
    cam = Camera(10.5, 10.5)
    combat = CombatSystem()
    ai = SamuraiAI(difficulty=difficulty)
    p1 = create_fighter(char_id, 10.5, 17.5)
    bot = None
    boss = BossOni(10.5, 7.5, seed)
    boss.set_difficulty(difficulty)
    p1.set_facing(boss.wx, boss.wy)
    projectiles, particles, banners, decoys = [], [], [], []
    pouches = PowderPouch.create_arena_pouches(game_map, [p1, boss], total_pouches=3)
    bot = BossBot(p1, boss, game_map)
    elapsed, winner, best = 0.0, None, 0
    while elapsed < MAX_TIME and winner is None:
        if elapsed > 2.0:
            bot.act(DT, projectiles, particles)
        decoys[:] = [d for d in decoys if d.update(DT)]
        update_fighter(p1, DT, game_map, particles, projectiles, pouches, opponent=boss)
        boss.update(DT, game_map, p1, particles, banners, projectiles, cam)
        winner = combat.process_combat(p1, boss, game_map, particles, banners, cam, projectiles, DT, decoys=decoys)
        if not p1.is_alive and winner is None:
            winner = "P2_WINS"
        best = max(best, boss.phase)
        if len(particles) > 60:
            particles.clear()
        if len(banners) > 30:
            banners.clear()
        boss.pop_events()
        elapsed += DT
    return winner == "P1_WINS", best, elapsed


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    difficulty = sys.argv[2] if len(sys.argv) > 2 else "normal"
    total_wins = total = 0
    print(f"Oni Gashadokuro — {runs} execuções por lutador, dificuldade {difficulty}")
    for char_id in ROSTER_ORDER:
        wins, phases, times = 0, [], []
        for seed in range(runs):
            won, phase, elapsed = fight(char_id, seed, difficulty)
            wins += won
            phases.append(phase + 1)
            times.append(elapsed)
        total_wins += wins
        total += runs
        print(f"  {char_id:10s} vitórias {wins}/{runs} ({100 * wins / runs:3.0f}%)  fase média {sum(phases) / runs:.1f}  tempo médio {sum(times) / runs:5.1f}s")
    print(f"Taxa geral de conclusão: {100 * total_wins / total:.0f}%")


if __name__ == "__main__":
    main()
