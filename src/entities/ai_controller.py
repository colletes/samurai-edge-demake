"""
Inteligência Artificial tática humanizada com suporte a Níveis de Dificuldade,
dispersão de mira, tempo de reação realista e evasão ativa de perigos de arena.
"""
import math
import random
from src.isometric.iso_math import world_distance
from src.entities.samurai import STATE_RECOVERY, STATE_ATTACK, STATE_IDLE, STATE_WALK

DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"

class SamuraiAI:
    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty if difficulty in (DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD) else DIFFICULTY_NORMAL
        self.decision_timer = 0.0
        self.move_dir_x = 0.0
        self.move_dir_y = 0.0

        # Humanização de Reações (Delay de reação para Parry / Evasão)
        self.pending_defense_timer = 0.0
        self.pending_defense_threat = None  # "ATTACK" ou "PROJECTILE"
        self.pending_defense_ready = False

        # Navegação não-linear e flanqueamento
        self.flank_sign = 1.0 if random.random() < 0.5 else -1.0
        self.flank_switch_timer = random.uniform(1.2, 2.5)

    def set_difficulty(self, difficulty: str):
        """Atualiza o nível de dificuldade da IA."""
        if difficulty in (DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD):
            self.difficulty = difficulty

    def _get_reaction_delay(self) -> float:
        """Tempo de reação humano calibrado por dificuldade."""
        if self.difficulty == DIFFICULTY_EASY:
            return random.uniform(0.32, 0.45)
        elif self.difficulty == DIFFICULTY_HARD:
            return random.uniform(0.12, 0.17)
        else: # NORMAL
            return random.uniform(0.18, 0.28)

    def get_clash_reaction(self) -> float | None:
        """Tempo até a IA apertar o botão do choque de espadas (QTE 'STRIKE!'); None = não reage a tempo."""
        press_chance, low, high = {
            DIFFICULTY_EASY: (0.50, 0.35, 0.60),
            DIFFICULTY_HARD: (0.92, 0.14, 0.28),
        }.get(self.difficulty, (0.75, 0.22, 0.45))
        if random.random() > press_chance:
            return None
        return random.uniform(low, high)

    def _get_parry_chance(self) -> float:
        """Probabilidade de acertar o timing do Parry."""
        if self.difficulty == DIFFICULTY_EASY:
            return 0.30
        elif self.difficulty == DIFFICULTY_HARD:
            return 0.85
        else:
            return 0.55

    def _get_punish_chance(self) -> float:
        """Probabilidade de punir o oponente em Recovery."""
        if self.difficulty == DIFFICULTY_EASY:
            return 0.40
        elif self.difficulty == DIFFICULTY_HARD:
            return 0.95
        else:
            return 0.75

    def _get_aim_target(self, ai_fighter, target, base_x: float, base_y: float) -> tuple[float, float]:
        """Calcula coordenadas de mira com dispersão angular baseada na dificuldade e velocidade do alvo."""
        dx = base_x - ai_fighter.wx
        dy = base_y - ai_fighter.wy
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            return base_x, base_y

        base_angle = math.atan2(dy, dx)

        # Dispersão base por dificuldade
        if self.difficulty == DIFFICULTY_EASY:
            dispersion = 0.28  # ~16°
        elif self.difficulty == DIFFICULTY_HARD:
            dispersion = 0.05  # ~3°
        else:
            dispersion = 0.16  # ~9°

        # Se o alvo estiver correndo ou se movendo ativamente, erro de dispersão aumenta em +50%
        if getattr(target, "is_moving", False):
            dispersion *= 1.50

        spread = random.uniform(-dispersion, dispersion)
        fog = getattr(getattr(self, "_map", None), "fog", None)
        if fog is not None:  # alvo dentro do rastro de névoa da Kasumi: a mira se perde
            spread += random.uniform(-1.0, 1.0) * fog.trail_density_at(target.wx, target.wy) * 0.45
        final_angle = base_angle + spread
        return (
            ai_fighter.wx + math.cos(final_angle) * dist,
            ai_fighter.wy + math.sin(final_angle) * dist
        )

    @staticmethod
    def _roll_reach(fighter) -> float:
        return getattr(fighter, "roll_speed", 8.5) * getattr(fighter, "roll_duration", 0.20)

    @staticmethod
    def _landing_ok(fighter, game_map, dir_x: float, dir_y: float, reach: float) -> bool:
        """False se o ponto de pouso de uma travessia de alcance `reach` cair dentro de um buraco."""
        if not getattr(game_map, "pits", None):
            return True
        mag = math.hypot(dir_x, dir_y)
        if mag < 0.001:
            return True
        end_x = fighter.wx + dir_x / mag * reach
        end_y = fighter.wy + dir_y / mag * reach
        return game_map.pit_at(end_x, end_y) is None

    @staticmethod
    def _lunge_clear(fighter, tx: float, ty: float, game_map, reach: float) -> bool:
        """False se uma investida em linha reta até `reach` passar por buraco sem proteção (não dá para frear a tempo)."""
        pits = getattr(game_map, "pits", None)
        if not pits:
            return True
        dx, dy = tx - fighter.wx, ty - fighter.wy
        mag = math.hypot(dx, dy)
        if mag < 0.001:
            return True
        for i in range(1, int(reach / 0.25) + 1):
            pit = game_map.pit_at(fighter.wx + dx / mag * i * 0.25, fighter.wy + dy / mag * i * 0.25)
            if pit is not None and not pit.railed:
                return False
        return True

    @staticmethod
    def _avoid_ship_roll(fighter, game_map) -> bool:
        """Durante o aviso e o balanço, foge para o lado oposto se o empurrão levaria a um buraco ou ao mar."""
        for hazard in getattr(game_map, "hazards", ()):
            direction = getattr(hazard, "direction", None)
            if direction is None or not hasattr(hazard, "push_speed") or getattr(hazard, "phase", "idle") == "idle":
                continue
            reach = hazard.push_speed * hazard.active_time * 0.85
            for i in range(1, 8):
                if game_map.pit_at(fighter.wx, fighter.wy + direction * reach * i / 7.0) is not None:
                    return True
        return False

    @staticmethod
    def _avoid_pendulum(fighter, game_map) -> tuple[float, float] | None:
        """Durante o aviso e a varredura do pêndulo, sai da faixa pelo lado mais curto; None se já está a salvo."""
        for hazard in getattr(game_map, "hazards", ()):
            lanes = getattr(hazard, "lanes", None)
            if lanes is None or getattr(hazard, "phase", "idle") == "idle":
                continue
            cx, cy, dx, dy = lanes[hazard.lane]
            px, py = -dy, dx
            side = (fighter.wx - cx) * px + (fighter.wy - cy) * py
            along = (fighter.wx - cx) * dx + (fighter.wy - cy) * dy
            if abs(side) < 2.0 and abs(along) < hazard.danger_half_length + 1.2:
                sign = 1.0 if side >= 0.0 else -1.0
                return px * sign, py * sign
        return None

    @staticmethod
    def _avoid_circles(fighter, game_map) -> tuple[float, float] | None:
        """Durante o aviso e a explosão, sai de dentro (ou da borda) dos círculos de morteiro, para longe do centro."""
        for hazard in getattr(game_map, "hazards", ()):
            circles = getattr(hazard, "circles", None)
            if not circles or getattr(hazard, "phase", "idle") == "idle":
                continue
            for cx, cy, r in circles:
                d = math.hypot(fighter.wx - cx, fighter.wy - cy)
                if d < r + 0.9:
                    return ((fighter.wx - cx) / d, (fighter.wy - cy) / d) if d > 0.01 else (1.0, 0.0)
        for prop in getattr(game_map, "interactives", ()):  # barris de pólvora com o pavio aceso
            circle = prop.danger_circle() if hasattr(prop, "danger_circle") else None
            if circle:
                cx, cy, r = circle
                d = math.hypot(fighter.wx - cx, fighter.wy - cy)
                if d < r + 0.9:
                    return ((fighter.wx - cx) / d, (fighter.wy - cy) / d) if d > 0.01 else (1.0, 0.0)
        return None

    @staticmethod
    def _avoid_traps(fighter, game_map) -> tuple[float, float] | None:
        """Vetor para longe das armadilhas armadas e visíveis (soma ao movimento, sem anular a perseguição)."""
        rx = ry = 0.0
        for e in getattr(game_map, "emitters", ()):
            if getattr(e, "armed", False):
                d = math.hypot(fighter.wx - e.wx, fighter.wy - e.wy)
                if d < e.RADIUS + 1.3:
                    w = (e.RADIUS + 1.3 - d) / (e.RADIUS + 1.3)
                    rx += (fighter.wx - e.wx) / max(d, 0.05) * w
                    ry += (fighter.wy - e.wy) / max(d, 0.05) * w
        return (rx, ry) if (rx or ry) else None

    def _away_ok(self, fighter, opponent, game_map, reach: float) -> bool:
        return self._landing_ok(fighter, game_map, fighter.wx - opponent.wx, fighter.wy - opponent.wy, reach)

    def _toward_ok(self, fighter, opponent, game_map, reach: float) -> bool:
        return self._landing_ok(fighter, game_map, opponent.wx - fighter.wx, opponent.wy - fighter.wy, reach)

    @staticmethod
    def _nav_graph(game_map):
        """Grafo de visibilidade entre as quinas dos buracos e os pontos de navegação do spec (calculado uma vez por mapa)."""
        graph = getattr(game_map, "_ai_nav", None)
        if graph is None:
            nodes = []
            for pit in game_map.pits:
                for cx, cy in ((pit.x0 - 0.9, pit.y0 - 0.9), (pit.x1 + 0.9, pit.y0 - 0.9),
                               (pit.x1 + 0.9, pit.y1 + 0.9), (pit.x0 - 0.9, pit.y1 + 0.9)):
                    if 0.3 <= cx <= game_map.cols - 0.3 and 0.3 <= cy <= game_map.rows - 0.3 \
                            and game_map.pit_edge_distance(cx, cy) >= 0.5:
                        nodes.append((cx, cy))
            nodes += list(getattr(game_map, "nav_points", ()))
            adj = [[] for _ in nodes]
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    if not game_map.segment_crosses_pit(*nodes[i], *nodes[j]):
                        d = math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1])
                        adj[i].append((j, d))
                        adj[j].append((i, d))
            graph = game_map._ai_nav = (nodes, adj)
        return graph

    def _route_waypoint(self, fighter, opponent, game_map):
        """Primeiro ponto da rota mais curta até o rival passando por quinas e vigas (Dijkstra); None se não houver rota."""
        import heapq
        nodes, adj = self._nav_graph(game_map)
        dist = {}
        prev = {}
        heap = []
        for i, (x, y) in enumerate(nodes):
            d = math.hypot(x - fighter.wx, y - fighter.wy)
            if d >= 0.7 and not game_map.segment_crosses_pit(fighter.wx, fighter.wy, x, y):
                dist[i] = d
                heapq.heappush(heap, (d, i))
        goal = {}
        for i, (x, y) in enumerate(nodes):
            if not game_map.segment_crosses_pit(x, y, opponent.wx, opponent.wy):
                goal[i] = math.hypot(x - opponent.wx, y - opponent.wy)
        best_total, best_node = None, None
        done = set()
        while heap:
            d, i = heapq.heappop(heap)
            if i in done:
                continue
            done.add(i)
            if i in goal and (best_total is None or d + goal[i] < best_total):
                best_total, best_node = d + goal[i], i
            for j, w in adj[i]:
                if d + w < dist.get(j, math.inf):
                    dist[j] = d + w
                    prev[j] = i
                    heapq.heappush(heap, (d + w, j))
        if best_node is None:
            return None
        node = best_node
        while node in prev:
            node = prev[node]
        return nodes[node]

    def _steer_around_pits(self, fighter, opponent, game_map):
        """Contorna buracos: segue a rota mais curta (quinas e vigas) quando o caminho até o rival os cruza e afasta das bordas."""
        pits = getattr(game_map, "pits", None)
        if not pits:
            return
        if game_map.segment_crosses_pit(fighter.wx, fighter.wy, opponent.wx, opponent.wy):
            self._route_tick = getattr(self, "_route_tick", 0) + 1
            wp = getattr(self, "_route_wp", None)
            if wp is None or self._route_tick % 10 == 0 \
                    or math.hypot(wp[0] - fighter.wx, wp[1] - fighter.wy) < 0.7 \
                    or game_map.segment_crosses_pit(fighter.wx, fighter.wy, wp[0], wp[1]):
                wp = self._route_wp = self._route_waypoint(fighter, opponent, game_map)
            if wp is not None:
                dx, dy = wp[0] - fighter.wx, wp[1] - fighter.wy
                length = math.hypot(dx, dy)
                if length > 0.001:
                    self.move_dir_x, self.move_dir_y = dx / length, dy / length
        else:
            self._route_wp = None
        # Nunca encosta na borda: gira a direção até haver folga à frente
        for angle in (0.0, 0.6, -0.6, 1.2, -1.2, 1.9, -1.9):
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            dir_x = self.move_dir_x * cos_a - self.move_dir_y * sin_a
            dir_y = self.move_dir_x * sin_a + self.move_dir_y * cos_a
            if game_map.pit_edge_distance(fighter.wx + dir_x * 0.7, fighter.wy + dir_y * 0.7) >= 0.45:
                self.move_dir_x, self.move_dir_y = dir_x, dir_y
                return

    def update(self, ai_fighter, opponent, dt: float, game_map, projectiles: list = None, powder_pouches: list = None, decoys: list = None):
        """Atualiza a IA controlando ai_fighter contra o opponent."""
        if not ai_fighter.is_alive or not opponent.is_alive:
            return

        self._map = game_map
        self.decision_timer -= dt
        dist = world_distance(ai_fighter.wx, ai_fighter.wy, opponent.wx, opponent.wy)        # -------------------------------------------------------------
        # 0. DETECÇÃO E EVASÃO DE PERIGOS DE KYOTO (Carruagens e Escombros)
        # -------------------------------------------------------------
        if game_map and hasattr(game_map, "carriages"):
            for carriage in game_map.carriages:
                if getattr(carriage, "is_active", False):
                    to_ai_x = ai_fighter.wx - carriage.wx
                    to_ai_y = ai_fighter.wy - carriage.wy
                    c_dir_x = getattr(carriage, "dir_x", 0.0)
                    c_dir_y = getattr(carriage, "dir_y", 1.0)
                    proj = to_ai_x * c_dir_x + to_ai_y * c_dir_y
                    c_dist = world_distance(ai_fighter.wx, ai_fighter.wy, carriage.wx, carriage.wy)

                    # Se a carruagem está vindo na direção da IA
                    if proj > -1.2 and c_dist < 6.8:
                        perp_offset = to_ai_x * (-c_dir_y) + to_ai_y * c_dir_x
                        if abs(perp_offset) < 2.3:  # Na rota de perigo!
                            perp_dir_x = -c_dir_y if perp_offset >= 0 else c_dir_y
                            perp_dir_y = c_dir_x if perp_offset >= 0 else -c_dir_x

                            # Se perigo iminente (<= 3.2 tiles), executa roll emergencial para a calçada!
                            if c_dist <= 3.2 and ai_fighter.can_act():
                                if hasattr(ai_fighter, "trigger_roll"):
                                    ai_fighter.trigger_roll(perp_dir_x, perp_dir_y)
                                    return

                            # Movimento prioritário de fuga para as laterais
                            if ai_fighter.can_move():
                                ai_fighter.apply_movement(perp_dir_x, perp_dir_y, dt, game_map)
                                return

        if game_map and hasattr(game_map, "falling_debris"):
            for debris in game_map.falling_debris:
                if getattr(debris, "is_active", False) and not getattr(debris, "has_impacted", False):
                    deb_dist = world_distance(ai_fighter.wx, ai_fighter.wy, debris.target_x, debris.target_y)
                    deb_radius = getattr(debris, "radius", 1.05)
                    if deb_dist < (deb_radius + 1.3):
                        esc_x = ai_fighter.wx - debris.target_x
                        esc_y = ai_fighter.wy - debris.target_y
                        length = math.hypot(esc_x, esc_y)
                        if length > 0.01:
                            esc_x /= length
                            esc_y /= length
                        else:
                            esc_x, esc_y = 1.0, 0.0

                        if deb_dist < (deb_radius + 0.5) and ai_fighter.can_act():
                            if hasattr(ai_fighter, "trigger_roll"):
                                ai_fighter.trigger_roll(esc_x, esc_y)
                                return
                        elif ai_fighter.can_move():
                            ai_fighter.apply_movement(esc_x, esc_y, dt, game_map)
                            return

        # -------------------------------------------------------------
        # 1. Se for Ninja e estiver DESARMADO: correr até a kunai no chão
        # -------------------------------------------------------------
        if hasattr(ai_fighter, "has_kunai") and not ai_fighter.has_kunai and projectiles:
            ground_kunai = None
            for p in projectiles:
                if getattr(p, "owner", None) == ai_fighter and getattr(p, "state", "") == "ON_GROUND":
                    ground_kunai = p
                    break
            if ground_kunai:
                dx = ground_kunai.wx - ai_fighter.wx
                dy = ground_kunai.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0.05 and ai_fighter.can_move():
                    self.move_dir_x, self.move_dir_y = dx / length, dy / length
                    self._steer_around_pits(ai_fighter, ground_kunai, game_map)
                    ai_fighter.apply_movement(self.move_dir_x, self.move_dir_y, dt, game_map)
                    return

        # -------------------------------------------------------------
        # 2. Se for Teppo (Rifleman) e estiver SEM MUNIÇÃO: caçar PowderPouch
        # -------------------------------------------------------------
        if getattr(ai_fighter, "char_type", "") in ("rifleman", "teppo") and not getattr(ai_fighter, "has_ammo", False) and powder_pouches:
            active_pouches = [p for p in powder_pouches if getattr(p, "is_active", False)]
            if active_pouches:
                nearest_pouch = min(active_pouches, key=lambda p: world_distance(ai_fighter.wx, ai_fighter.wy, p.wx, p.wy))
                if dist < 1.5:
                    if hasattr(ai_fighter, "trigger_rifle_butt") and random.random() < 0.70:
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_rifle_butt(aim_x, aim_y)
                        return
                    elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.60:
                        ai_fighter.trigger_evasive_backstep()
                        return

                dx = nearest_pouch.wx - ai_fighter.wx
                dy = nearest_pouch.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0.05 and ai_fighter.can_move():
                    self.move_dir_x, self.move_dir_y = dx / length, dy / length
                    self._steer_around_pits(ai_fighter, nearest_pouch, game_map)
                    ai_fighter.apply_movement(self.move_dir_x, self.move_dir_y, dt, game_map)
                    return

        # -------------------------------------------------------------
        # 3. REAÇÃO DEFENSIVA HUMANIZADA (Com Reaction Delay)
        # -------------------------------------------------------------
        incoming_projectile = False
        if projectiles:
            for p in projectiles:
                if getattr(p, "is_active", True) and getattr(p, "owner", None) == opponent:
                    if world_distance(ai_fighter.wx, ai_fighter.wy, p.wx, p.wy) < 3.2:
                        incoming_projectile = True
                        break

        threat_active = (opponent.state == STATE_ATTACK and dist < 2.5) or incoming_projectile
        if threat_active:
            if self.pending_defense_threat is None:
                self.pending_defense_threat = "ATTACK" if (opponent.state == STATE_ATTACK and dist < 2.5) else "PROJECTILE"
                self.pending_defense_timer = self._get_reaction_delay()
                self.pending_defense_ready = False
            else:
                self.pending_defense_timer -= dt
                if self.pending_defense_timer <= 0:
                    self.pending_defense_ready = True
        else:
            self.pending_defense_threat = None
            self.pending_defense_timer = 0.0
            self.pending_defense_ready = False

        if threat_active and self.pending_defense_ready:
            self.pending_defense_threat = None
            self.pending_defense_ready = False

            # Musashi: Parry com reflexão de projéteis (janela ativa 0.25s)
            # Rebalanceamento C: Aumentado para 0.70 (melhor defesa contra zoners)
            musashi_parry_bonus = 0.70 if (incoming_projectile and ai_fighter.__class__.__name__ == "BlueSamurai") else 0.0
            if hasattr(ai_fighter, "trigger_parry") and random.random() < (self._get_parry_chance() + musashi_parry_bonus):
                ai_fighter.set_facing(opponent.wx, opponent.wy)
                ai_fighter.trigger_parry()
                return
            # Kenshin: Dash evasivo
            elif hasattr(ai_fighter, "trigger_dash") and random.random() < 0.60 and self._away_ok(
                    ai_fighter, opponent, game_map,
                    getattr(ai_fighter, "dash_speed", 22.0) * getattr(ai_fighter, "dash_duration", 0.16)):
                dx = ai_fighter.wx - opponent.wx
                dy = ai_fighter.wy - opponent.wy
                length = math.hypot(dx, dy)
                if length > 0:
                    ai_fighter.trigger_dash(dx / length, dy / length)
                    return
            # Gray Ninja: Bomba de fumaça instantânea
            elif hasattr(ai_fighter, "trigger_smoke_bomb") and projectiles is not None and random.random() < 0.60:
                aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                ai_fighter.trigger_smoke_bomb(aim_x, aim_y, projectiles)
                return
            # Rifleman: Salto evasivo para trás
            elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.70 and self._away_ok(
                    ai_fighter, opponent, game_map, 1.6):
                ai_fighter.trigger_evasive_backstep()
                return
            # Okuni: Finta Kawarimi Decoy
            elif hasattr(ai_fighter, "trigger_kawarimi_decoy") and (decoys is not None) and random.random() < 0.75 and self._away_ok(
                    ai_fighter, opponent, game_map, self._roll_reach(ai_fighter)):
                dx = ai_fighter.wx - opponent.wx
                dy = ai_fighter.wy - opponent.wy
                ai_fighter.trigger_kawarimi_decoy(dx, dy, decoys)
                return
            # Kyudo Archer: Flecha de corda
            elif hasattr(ai_fighter, "trigger_rope_arrow") and projectiles is not None and random.random() < 0.65:
                aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                ai_fighter.trigger_rope_arrow(aim_x, aim_y, projectiles, game_map=game_map)
                return
            # Pirata (Anne): Pólvora nos olhos
            elif hasattr(ai_fighter, "trigger_gunpowder_blind") and random.random() < 0.60:
                aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                ai_fighter.trigger_gunpowder_blind(aim_x, aim_y, opponent=opponent)
                return
            # Mosqueteira (Julie): Riposte de capa
            elif hasattr(ai_fighter, "trigger_cloak_riposte") and random.random() < 0.65:
                ai_fighter.trigger_cloak_riposte()
                return
            # Evasão universal: se puder rolar
            elif hasattr(ai_fighter, "trigger_roll") and random.random() < 0.50 and self._away_ok(
                    ai_fighter, opponent, game_map, self._roll_reach(ai_fighter)):
                dx = ai_fighter.wx - opponent.wx
                dy = ai_fighter.wy - opponent.wy
                length = math.hypot(dx, dy)
                if length > 0 and ai_fighter.can_act():
                    ai_fighter.trigger_roll(dx / length, dy / length)
                    return
            # Musashi: Parry reativo como defesa secundária
            elif hasattr(ai_fighter, "trigger_parry") and random.random() < 0.40:
                ai_fighter.trigger_parry()
                return

        # -------------------------------------------------------------
        # 4. PUNIÇÃO EM RECOVERY OU STUNNED
        # -------------------------------------------------------------
        if opponent.state in (STATE_RECOVERY, "STUNNED") and random.random() < self._get_punish_chance():
            ai_fighter.set_facing(opponent.wx, opponent.wy)
            if hasattr(ai_fighter, "dog") and ai_fighter.dog and ai_fighter.dog.can_attack():
                aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                ai_fighter.trigger_dog_attack(aim_x, aim_y)
                return

            if dist < 2.2:
                self._execute_attack(ai_fighter, opponent, projectiles)
                return
            else:
                dx = opponent.wx - ai_fighter.wx
                dy = opponent.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0 and ai_fighter.can_move():
                    self.move_dir_x, self.move_dir_y = dx / length, dy / length
                    self._steer_around_pits(ai_fighter, opponent, game_map)
                    ai_fighter.apply_movement(self.move_dir_x, self.move_dir_y, dt, game_map)
                return

        # -------------------------------------------------------------
        # 5. COMPORTAMENTO NEUTRO & APROXIMAÇÃO NÃO-LINEAR
        # -------------------------------------------------------------
        if self.decision_timer <= 0:
            self.decision_timer = random.uniform(0.28, 0.55)

            # Ninja: arremesso de kunai com dispersão
            if hasattr(ai_fighter, "has_kunai") and ai_fighter.has_kunai and projectiles is not None:
                if 2.2 <= dist <= 5.5 and random.random() < 0.40:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_throw_attack(aim_x, aim_y, projectiles)
                    return

            # American Ninja: shuriken com dispersão ou comando do cão
            if hasattr(ai_fighter, "trigger_shuriken") and projectiles is not None:
                if 2.0 <= dist <= 6.0 and random.random() < 0.55:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_shuriken(aim_x, aim_y, projectiles)
                    return
                if hasattr(ai_fighter, "dog") and ai_fighter.dog and ai_fighter.dog.can_attack() and dist <= 4.5 and random.random() < 0.45:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_dog_attack(aim_x, aim_y)
                    return

            # Gray Ninja: bomba com dispersão ou fumaça se cercado
            if hasattr(ai_fighter, "trigger_throw_bomb") and projectiles is not None:
                if dist < 2.2 and random.random() < 0.50:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_smoke_bomb(aim_x, aim_y, projectiles)
                    return
                elif 2.0 <= dist <= 5.5 and random.random() < 0.55:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_throw_bomb(aim_x, aim_y, projectiles)
                    return

            # Murasaki: Kusarigama com dispersão
            if hasattr(ai_fighter, "trigger_kusarigama_pull") and projectiles is not None:
                if 2.0 <= dist <= 5.0 and random.random() < 0.55:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_kusarigama_pull(aim_x, aim_y, projectiles)
                    return

            # Saitou: Gatotsu
            if hasattr(ai_fighter, "trigger_gatotsu_thrust"):
                if 2.8 <= dist <= 6.8 and random.random() < 0.50 \
                        and self._lunge_clear(ai_fighter, opponent.wx, opponent.wy, game_map, 7.5):
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_gatotsu_thrust(aim_x, aim_y)
                    return

            # Golpes corpo a corpo avançam o lutador: nada de golpear em direção a um buraco aberto
            melee_unsafe = dist <= 3.5 and not self._lunge_clear(ai_fighter, opponent.wx, opponent.wy, game_map, 3.8)

            # Musashi: Combate com espadas duplas — inicia combo ao se aproximar do oponente
            if hasattr(ai_fighter, "trigger_combo_attack") and not melee_unsafe:
                if dist <= 1.6 and random.random() < 0.75:
                    ai_fighter.trigger_combo_attack(opponent.wx, opponent.wy)
                    return

            # Kenshin: usa o avanço Iai como ferramenta de aproximação à média distância,
            # em vez de só golpear quando já está parado ao lado do oponente
            if hasattr(ai_fighter, "trigger_iai_attack") and not melee_unsafe:
                if 1.6 <= dist <= 3.2 and random.random() < 0.50:
                    ai_fighter.set_facing(opponent.wx, opponent.wy)
                    ai_fighter.trigger_iai_attack(opponent.wx, opponent.wy)
                    return
                # Ryuu Tsui Sen: salto aéreo com i-frames como engajamento alternativo contra zoneadores
                if getattr(ai_fighter, "ryuu_timer", 0.0) <= 0 and 2.0 <= dist <= 4.2 and random.random() < 0.40:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_ryuu_tsui_sen(aim_x, aim_y)
                    return

            # Teppo: tiro com dispersão de mira
            if hasattr(ai_fighter, "trigger_shoot"):
                if getattr(ai_fighter, "has_ammo", False) and getattr(ai_fighter, "cocking_timer", 0.0) <= 0 and projectiles is not None:
                    if 2.5 <= dist <= 8.5 and random.random() < 0.70:
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_shoot(aim_x, aim_y, projectiles)
                        return
                elif not melee_unsafe:
                    if dist < 1.6:
                        if hasattr(ai_fighter, "trigger_rifle_butt") and random.random() < 0.75:
                            ai_fighter.trigger_rifle_butt(opponent.wx, opponent.wy)
                            return
                        elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.65 and self._away_ok(
                                ai_fighter, opponent, game_map, 1.6):
                            ai_fighter.trigger_evasive_backstep()
                            return

            # Okuni: leques ou finta Kawarimi
            if hasattr(ai_fighter, "trigger_fan_strike") and not melee_unsafe:
                if dist <= 1.45:
                    ai_fighter.trigger_fan_strike(opponent.wx, opponent.wy)
                    return
                elif dist <= 2.2 and random.random() < 0.35 and decoys is not None and self._away_ok(
                        ai_fighter, opponent, game_map, self._roll_reach(ai_fighter)):
                    ai_fighter.trigger_kawarimi_decoy(-ai_fighter.facing_x, -ai_fighter.facing_y, decoys)
                    return

            # Kyudo Archer: arco com dispersão de mira
            if hasattr(ai_fighter, "trigger_bow_draw") and projectiles is not None:
                if 2.8 <= dist <= 7.5 and random.random() < 0.55:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_bow_draw(aim_x, aim_y, projectiles)
                    return

            # Pirata (Anne): canhão naval humanizado com dispersão
            if hasattr(ai_fighter, "trigger_cutlass_cleave"):
                if dist >= 2.5 and getattr(ai_fighter, "cannon_cooldown_timer", 0.0) <= 0 and projectiles is not None:
                    if hasattr(ai_fighter, "trigger_quick_cannon") and random.random() < 0.70:
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_quick_cannon(aim_x, aim_y, projectiles)
                        return

                if dist >= 2.8 and random.random() < 0.40 and hasattr(ai_fighter, "trigger_roll"):
                    if ai_fighter.can_act() and self._toward_ok(ai_fighter, opponent, game_map, self._roll_reach(ai_fighter)):
                        dx = opponent.wx - ai_fighter.wx
                        dy = opponent.wy - ai_fighter.wy
                        ai_fighter.trigger_roll(dx, dy)
                        return

                if dist <= 1.85 and not melee_unsafe:
                    ai_fighter.trigger_cutlass_cleave(opponent.wx, opponent.wy)
                    return

            # Mosqueteira (Julie): florete e pederneira com dispersão
            if hasattr(ai_fighter, "trigger_fleche_thrust"):
                if projectiles and getattr(ai_fighter, "cape_timer", 0.0) <= 0:
                    for p in projectiles:
                        if getattr(p, "is_active", True) and getattr(p, "owner", None) != ai_fighter:
                            p_dist = world_distance(ai_fighter.wx, ai_fighter.wy, p.wx, p.wy)
                            if p_dist < 2.8:
                                ai_fighter.trigger_cape_flourish(opponent.wx, opponent.wy, opponent=opponent, projectiles=projectiles)
                                return

                if dist < 1.70 and getattr(ai_fighter, "cape_timer", 0.0) <= 0 and random.random() < 0.65:
                    ai_fighter.trigger_cape_flourish(opponent.wx, opponent.wy, opponent=opponent, projectiles=projectiles)
                    return

                if dist >= 2.8 and getattr(ai_fighter, "flintlock_timer", 99.0) <= 0 and projectiles is not None:
                    if hasattr(ai_fighter, "trigger_flintlock_shot") and random.random() < 0.70:
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_flintlock_shot(aim_x, aim_y, projectiles)
                        return

                if 1.30 <= dist <= 2.65 and random.random() < 0.65:
                    ai_fighter.trigger_fleche_thrust(opponent.wx, opponent.wy)
                    return

            # Movimentação Não-Linear e Espaçamento
            if hasattr(ai_fighter, "trigger_shoot") and not getattr(ai_fighter, "has_ammo", False):
                dx = ai_fighter.wx - opponent.wx
                dy = ai_fighter.wy - opponent.wy
                length = math.hypot(dx, dy)
                if length > 0.001:
                    self.move_dir_x = dx / length
                    self.move_dir_y = dy / length
                else:
                    self.move_dir_x = 1.0
                    self.move_dir_y = 0.0
            elif dist > 3.0:
                # Aproximação em arco / flanqueamento (não em linha reta rígida)
                self.flank_switch_timer -= dt
                if self.flank_switch_timer <= 0:
                    self.flank_switch_timer = random.uniform(1.2, 2.5)
                    self.flank_sign = -self.flank_sign

                dx = opponent.wx - ai_fighter.wx
                dy = opponent.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0.001:
                    dir_x = dx / length
                    dir_y = dy / length
                    perp_x = -dir_y * self.flank_sign
                    perp_y = dir_x * self.flank_sign
                    final_x = dir_x * 0.75 + perp_x * 0.35
                    final_y = dir_y * 0.75 + perp_y * 0.35
                    f_len = math.hypot(final_x, final_y)
                    self.move_dir_x = final_x / f_len
                    self.move_dir_y = final_y / f_len
                else:
                    self.move_dir_x = 1.0
                    self.move_dir_y = 0.0
            elif dist < 1.45:
                if random.random() < 0.60:
                    self._execute_attack(ai_fighter, opponent, projectiles)
                else:
                    dx = ai_fighter.wx - opponent.wx
                    dy = ai_fighter.wy - opponent.wy
                    length = math.hypot(dx, dy)
                    if length > 0.001:
                        self.move_dir_x = dx / length
                        self.move_dir_y = dy / length
                    else:
                        self.move_dir_x = -1.0
                        self.move_dir_y = 0.0
            else:
                # Circunavegar lateralmente
                dx = opponent.wx - ai_fighter.wx
                dy = opponent.wy - ai_fighter.wy
                if dist > 0.001:
                    self.move_dir_x = -dy / dist
                    self.move_dir_y = dx / dist
                else:
                    self.move_dir_x = 1.0
                    self.move_dir_y = 0.0

        # Desvio de obstáculos sólidos no caminho
        if game_map and hasattr(game_map, "rocks"):
            for rock in game_map.rocks:
                r_dist = world_distance(ai_fighter.wx, ai_fighter.wy, rock.wx, rock.wy)
                r_rad = getattr(rock, "radius", 0.5)
                if r_dist < (r_rad + 1.1):
                    r_dx = ai_fighter.wx - rock.wx
                    r_dy = ai_fighter.wy - rock.wy
                    r_len = math.hypot(r_dx, r_dy)
                    if r_len > 0.01:
                        self.move_dir_x += (r_dx / r_len) * 0.6
                        self.move_dir_y += (r_dy / r_len) * 0.6
                        m_len = math.hypot(self.move_dir_x, self.move_dir_y)
                        if m_len > 0.001:
                            self.move_dir_x /= m_len
                            self.move_dir_y /= m_len

        if ai_fighter.can_move():
            repel = self._avoid_traps(ai_fighter, game_map) if game_map else None
            if repel is not None:
                mx, my = self.move_dir_x + repel[0] * 2.0, self.move_dir_y + repel[1] * 2.0
                length = math.hypot(mx, my)
                if length > 0.001:
                    self.move_dir_x, self.move_dir_y = mx / length, my / length
            escape = (self._avoid_pendulum(ai_fighter, game_map) or self._avoid_circles(ai_fighter, game_map)) if game_map else None
            if escape is not None:
                self.move_dir_x, self.move_dir_y = escape
            if game_map and self._avoid_ship_roll(ai_fighter, game_map):
                direction = next(h.direction for h in game_map.hazards if hasattr(h, "direction"))
                self.move_dir_x, self.move_dir_y = 0.0, -direction
            self._steer_around_pits(ai_fighter, opponent, game_map)
            ai_fighter.apply_movement(self.move_dir_x, self.move_dir_y, dt, game_map)
            ai_fighter.set_facing(opponent.wx, opponent.wy)

    def _execute_attack(self, fighter, target, projectiles):
        """Executa o ataque primário de acordo com a classe do lutador."""
        # Golpes corpo a corpo avançam o lutador: não ataca em direção a um buraco aberto logo à frente
        if world_distance(fighter.wx, fighter.wy, target.wx, target.wy) <= 3.5 \
                and not self._lunge_clear(fighter, target.wx, target.wy, getattr(self, "_map", None), 3.8):
            return
        if hasattr(fighter, "trigger_iai_attack"):
            fighter.trigger_iai_attack(target.wx, target.wy)
        elif hasattr(fighter, "trigger_combo_attack"):
            fighter.trigger_combo_attack(target.wx, target.wy)
        elif hasattr(fighter, "trigger_thrust_attack"):
            fighter.trigger_thrust_attack(target.wx, target.wy)
        elif hasattr(fighter, "trigger_fan_strike"):
            fighter.trigger_fan_strike(target.wx, target.wy)
        elif hasattr(fighter, "trigger_shuriken"):
            if projectiles is not None:
                aim_x, aim_y = self._get_aim_target(fighter, target, target.wx, target.wy)
                fighter.trigger_shuriken(aim_x, aim_y, projectiles)
        elif hasattr(fighter, "trigger_throw_bomb"):
            if projectiles is not None:
                aim_x, aim_y = self._get_aim_target(fighter, target, target.wx, target.wy)
                fighter.trigger_throw_bomb(aim_x, aim_y, projectiles)
        elif hasattr(fighter, "trigger_kama_strike"):
            fighter.trigger_kama_strike(target.wx, target.wy)
        elif hasattr(fighter, "trigger_gatotsu_thrust"):
            dist = world_distance(fighter.wx, fighter.wy, target.wx, target.wy)
            if dist < 1.3:
                fighter.trigger_zeroshiki(target.wx, target.wy)
            elif self._lunge_clear(fighter, target.wx, target.wy, getattr(self, "_map", None), 7.5):
                fighter.trigger_gatotsu_thrust(target.wx, target.wy)
        elif hasattr(fighter, "trigger_shoot"):
            if getattr(fighter, "has_ammo", False) and getattr(fighter, "cocking_timer", 0.0) <= 0 and projectiles is not None:
                aim_x, aim_y = self._get_aim_target(fighter, target, target.wx, target.wy)
                fighter.trigger_shoot(aim_x, aim_y, projectiles)
            elif hasattr(fighter, "trigger_rifle_butt"):
                fighter.trigger_rifle_butt(target.wx, target.wy)
        elif hasattr(fighter, "trigger_bow_draw"):
            aim_x, aim_y = self._get_aim_target(fighter, target, target.wx, target.wy)
            fighter.trigger_bow_draw(aim_x, aim_y, projectiles)
        elif hasattr(fighter, "trigger_cutlass_cleave"):
            fighter.trigger_cutlass_cleave(target.wx, target.wy)
        elif hasattr(fighter, "trigger_fleche_thrust"):
            fighter.trigger_fleche_thrust(target.wx, target.wy)
