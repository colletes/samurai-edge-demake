"""
Entregável 8.1: regras do Modo Torneio Arcade (módulo puro, sem pygame).

A jornada tem 11 lutas: 7 duelos BO3 (sem ninjas), espelho, endurance (1x2), ninja challenge e o chefe.
Os Continues são infinitos, contados e penalizados na pontuação; a dificuldade da IA sobe e desce durante a jornada.
"""
import random
from dataclasses import dataclass, field
from enum import Enum

from src.config import CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE, CHAR_NINJA, CHAR_BOSS, ARENA_SHADOW_CAVE, ARENA_GASHADOKURO
from src.roster import ARCADE_TIER_ORDER, ARCADE_MATCHUP_TABLE, ARENA_BY_FIGHTER, ROSTER_ORDER

# Ninja challenge: Joe, Kasumi, Murasaki e Hanzo, nessa ordem
NINJA_ORDER = (CHAR_AMERICAN, CHAR_GRAY, CHAR_PURPLE, CHAR_NINJA)
NINJAS = frozenset(NINJA_ORDER)
DUEL_COUNT = 7
ROUNDS_TO_WIN = 2
CHALLENGE_PLAYER_LIVES = 2
DIFFICULTIES = ("easy", "normal", "hard")

SCORE_FIGHT = 1000
SCORE_FLAWLESS_ROUND = 500
SCORE_STYLE_KILL = 100
SCORE_TIME_PER_SECOND = 10
TIME_BONUS_WINDOW = 60.0
CONTINUE_PENALTY = 2000
CLEAN_STREAK_FOR_RISE = 2

# Resultado de um round (`on_round_end`)
NEXT_ROUND = "NEXT_ROUND"
NEXT_OPPONENT = "NEXT_OPPONENT"
FIGHT_WON = "FIGHT_WON"
FIGHT_LOST = "FIGHT_LOST"

ORDER_TIER = "tier"
ORDER_RANDOM = "random"


class FightKind(Enum):
    DUEL = "duel"
    MIRROR = "mirror"
    ENDURANCE = "endurance"
    NINJA_CHALLENGE = "ninja_challenge"
    BOSS = "boss"


@dataclass(frozen=True)
class ArcadeFight:
    kind: FightKind
    opponents: tuple
    arena_id: str
    rounds_to_win: int = ROUNDS_TO_WIN
    player_round_lives: int | None = None  # None nos duelos BO3; 2 nos desafios 9 e 10

    @property
    def is_challenge(self) -> bool:
        return self.player_round_lives is not None


def _non_ninjas_without(player_char: str) -> list[str]:
    return [c for c in ARCADE_TIER_ORDER if c not in NINJAS and c != player_char]


def _strongest_vs(player_char: str, candidates: list[str], count: int) -> list[str]:
    """Os `count` candidatos com melhor taxa de vitória contra o lutador do jogador, do mais fraco ao mais forte."""
    def rate(c):
        return ARCADE_MATCHUP_TABLE.get(c, {}).get(player_char, 50.0)
    best = sorted(candidates, key=lambda c: (-rate(c), ARCADE_TIER_ORDER.index(c)))[:count]
    return sorted(best, key=lambda c: (rate(c), -ARCADE_TIER_ORDER.index(c)))


def build_ladder(player_char: str, seed: int = 0, order: str = ORDER_TIER) -> list[ArcadeFight]:
    """Monta as 11 lutas da jornada para o lutador escolhido."""
    rng = random.Random(seed)
    pool = _non_ninjas_without(player_char)  # do mais fraco ao mais forte
    if len(pool) > DUEL_COUNT:  # jogador ninja: sobram 8 e um é descartado pela semente
        pool.remove(rng.choice(pool))
    if order == ORDER_RANDOM:
        rng.shuffle(pool)
    ladder = [ArcadeFight(FightKind.DUEL, (opp,), ARENA_BY_FIGHTER[opp]) for opp in pool]

    ladder.append(ArcadeFight(FightKind.MIRROR, (player_char,), ARENA_BY_FIGHTER[player_char]))

    endurance = tuple(_strongest_vs(player_char, _non_ninjas_without(player_char), 2))
    ladder.append(ArcadeFight(FightKind.ENDURANCE, endurance, ARENA_BY_FIGHTER[endurance[0]],
                              player_round_lives=CHALLENGE_PLAYER_LIVES))

    # Se o jogador é ninja, a vez dele na ordem é o espelho: a lista já o contém, então sempre há 4 oponentes
    ladder.append(ArcadeFight(FightKind.NINJA_CHALLENGE, NINJA_ORDER, ARENA_SHADOW_CAVE,
                              player_round_lives=CHALLENGE_PLAYER_LIVES))

    # Luta 11: o Oni Gashadokuro (8.2) numa só luta: 1 ponto de vitória e a primeira derrota vale um Continue (D8)
    ladder.append(ArcadeFight(FightKind.BOSS, (CHAR_BOSS,), ARENA_GASHADOKURO, rounds_to_win=1))
    return ladder


@dataclass
class ArcadeRun:
    player_char: str
    difficulty_start: int = 1
    seed: int = 0
    order: str = ORDER_TIER
    difficulty_level: int = field(default=-1)
    clean_streak: int = 0
    continues: int = 0
    score: int = 0
    points_lost_to_continues: int = 0
    index: int = 0
    elapsed: float = 0.0
    stats: list = field(default_factory=list)
    last_difficulty_change: int = 0  # +1/-1 na última mudança, para a seta nas chaves
    ladder: list = field(default_factory=list)
    # Estado da luta atual
    opponent_index: int = 0
    rounds_won_vs_current: int = 0
    rounds_lost_vs_current: int = 0
    player_round_lives: int = 0
    fight_score: int = 0
    boss_phase: int = 0  # checkpoint do chefe: fase mais avançada alcançada (0 a 4)

    def __post_init__(self):
        self.difficulty_start = max(0, min(2, self.difficulty_start))
        if self.difficulty_level < 0:
            self.difficulty_level = self.difficulty_start
        if not self.ladder:
            self.ladder = build_ladder(self.player_char, self.seed, self.order)
        self._reset_fight_state()

    # ------------------------------------------------------------------ consulta
    @property
    def is_finished(self) -> bool:
        return self.index >= len(self.ladder)

    def current_fight(self) -> ArcadeFight | None:
        return None if self.is_finished else self.ladder[self.index]

    def current_opponent(self) -> str | None:
        fight = self.current_fight()
        return None if fight is None else fight.opponents[self.opponent_index]

    @property
    def difficulty_name(self) -> str:
        return DIFFICULTIES[self.difficulty_level]

    @property
    def lives_left(self) -> int | None:
        fight = self.current_fight()
        return None if fight is None or not fight.is_challenge else self.player_round_lives

    def add_time(self, dt: float):
        self.elapsed += dt

    # ------------------------------------------------------------------ regras
    def _reset_fight_state(self):
        fight = self.current_fight()
        self.opponent_index = 0
        self.rounds_won_vs_current = 0
        self.rounds_lost_vs_current = 0
        self.player_round_lives = fight.player_round_lives if fight and fight.is_challenge else 0
        self.fight_score = 0

    def _round_points(self, round_time: float, flawless: bool, kill_style: bool) -> int:
        pts = int(max(0.0, TIME_BONUS_WINDOW - round_time) * SCORE_TIME_PER_SECOND)
        if flawless:
            pts += SCORE_FLAWLESS_ROUND
        if kill_style:
            pts += SCORE_STYLE_KILL
        return pts

    def on_round_end(self, winner: str, round_time: float = TIME_BONUS_WINDOW, flawless: bool = False,
                     kill_style: bool = False) -> str:
        """`winner` é "P1" (o jogador), "P2" ou "DRAW". Devolve NEXT_ROUND, NEXT_OPPONENT, FIGHT_WON ou FIGHT_LOST."""
        fight = self.current_fight()
        if fight is None or winner == "DRAW":
            return NEXT_ROUND
        if winner == "P1":
            pts = self._round_points(round_time, flawless, kill_style)
            self.score += pts
            self.fight_score += pts
            self.rounds_won_vs_current += 1
            if self.rounds_won_vs_current < fight.rounds_to_win:
                return NEXT_ROUND
            if fight.is_challenge and self.opponent_index + 1 < len(fight.opponents):
                self.opponent_index += 1
                self.rounds_won_vs_current = 0
                self.rounds_lost_vs_current = 0
                return NEXT_OPPONENT
            self.on_fight_won()
            return FIGHT_WON
        # O jogador perdeu o round
        self.rounds_lost_vs_current += 1
        if fight.is_challenge:
            self.player_round_lives -= 1
            return FIGHT_LOST if self.player_round_lives <= 0 else NEXT_ROUND
        return FIGHT_LOST if self.rounds_lost_vs_current >= fight.rounds_to_win else NEXT_ROUND

    def on_fight_won(self):
        """Pontua a luta, ajusta a dificuldade e avança a jornada."""
        self.score += SCORE_FIGHT
        self.fight_score += SCORE_FIGHT
        self.boss_phase = 0
        self.stats.append({"fight": self.index, "kind": self.current_fight().kind.value, "score": self.fight_score,
                           "continues": self.continues})
        self.clean_streak += 1
        self.last_difficulty_change = 0
        if self.clean_streak >= CLEAN_STREAK_FOR_RISE:
            self.clean_streak = 0
            if self.difficulty_level < len(DIFFICULTIES) - 1:
                self.difficulty_level += 1
                self.last_difficulty_change = 1
        self.index += 1
        self._reset_fight_state()

    def on_continue(self):
        """Continue infinito: tira 2000 pontos (nunca abaixo de zero), baixa a dificuldade e refaz a luta inteira."""
        self.continues += 1
        lost = min(self.score, CONTINUE_PENALTY)
        self.score -= lost
        self.points_lost_to_continues += lost
        self.clean_streak = 0
        self.last_difficulty_change = 0
        if self.difficulty_level > 0:
            self.difficulty_level -= 1
            self.last_difficulty_change = -1
        self._reset_fight_state()

    # ------------------------------------------------------------------ persistência
    def to_dict(self) -> dict:
        return {"player_char": self.player_char, "difficulty_start": self.difficulty_start, "seed": self.seed,
                "order": self.order, "difficulty_level": self.difficulty_level, "clean_streak": self.clean_streak,
                "continues": self.continues, "score": self.score, "points_lost_to_continues": self.points_lost_to_continues,
                "index": self.index, "elapsed": round(self.elapsed, 2), "stats": list(self.stats),
                "boss_phase": self.boss_phase}

    @classmethod
    def from_dict(cls, data: dict) -> "ArcadeRun":
        if data.get("player_char") not in ROSTER_ORDER:
            raise ValueError("lutador desconhecido")
        run = cls(player_char=data["player_char"], difficulty_start=int(data.get("difficulty_start", 1)),
                  seed=int(data.get("seed", 0)), order=data.get("order", ORDER_TIER),
                  difficulty_level=max(0, min(2, int(data.get("difficulty_level", 1)))))
        run.clean_streak = int(data.get("clean_streak", 0))
        run.continues = int(data.get("continues", 0))
        run.score = int(data.get("score", 0))
        run.points_lost_to_continues = int(data.get("points_lost_to_continues", 0))
        run.index = max(0, min(len(run.ladder), int(data.get("index", 0))))
        run.elapsed = float(data.get("elapsed", 0.0))
        run.stats = list(data.get("stats", []))
        run.boss_phase = max(0, min(4, int(data.get("boss_phase", 0))))
        run._reset_fight_state()
        return run
