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

    def _get_reaction_delay(self, is_explosive: bool = False) -> float:
        """Tempo de reação humano calibrado por dificuldade. Explosivos usam reação rápida de emergência."""
        if is_explosive:
            if self.difficulty == DIFFICULTY_EASY:
                return random.uniform(0.06, 0.10)
            elif self.difficulty == DIFFICULTY_HARD:
                return random.uniform(0.01, 0.03)
            else:  # NORMAL
                return random.uniform(0.03, 0.06)

        if self.difficulty == DIFFICULTY_EASY:
            return random.uniform(0.16, 0.22)
        elif self.difficulty == DIFFICULTY_HARD:
            return random.uniform(0.02, 0.05)
        else: # NORMAL
            return random.uniform(0.08, 0.14)

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
    def _is_bomb_or_hazard_projectile(p, fighter=None) -> bool:
        """Retorna True se o projétil for explosivo ou armadilha letal no solo/ar."""
        if not getattr(p, "is_active", True):
            return False
        cname = p.__class__.__name__
        if cname in ("TimedBombEntity", "RemoteMineEntity", "CannonballProjectile"):
            return True
        if cname == "BearTrapProjectile":
            if fighter is None or getattr(p, "owner", None) != fighter:
                return True
        return False

    @classmethod
    def _is_path_threatened_by_explosives(cls, fighter, tx: float, ty: float, projectiles: list, reach: float = 4.0, danger_radius: float = 2.3) -> bool:
        """Retorna True se houver bomba, mina ou armadilha ativa no caminho ou no destino do golpe."""
        if not projectiles:
            return False
        fx, fy = fighter.wx, fighter.wy
        dx, dy = tx - fx, ty - fy
        length = math.hypot(dx, dy)
        if length < 0.001:
            dest_x, dest_y = fx, fy
        else:
            actual_reach = min(length, reach)
            dest_x = fx + (dx / length) * actual_reach
            dest_y = fy + (dy / length) * actual_reach

        for p in projectiles:
            if not cls._is_bomb_or_hazard_projectile(p, fighter):
                continue
            p_wx, p_wy = p.wx, p.wy
            # 1. Proximidade ao destino final (evita cair dentro do raio da explosão)
            if world_distance(dest_x, dest_y, p_wx, p_wy) < danger_radius:
                return True
            # 2. Proximidade ao longo do segmento de travessia (evita atravessar a bomba e detoná-la por toque)
            seg_dx = dest_x - fx
            seg_dy = dest_y - fy
            seg_len_sq = seg_dx * seg_dx + seg_dy * seg_dy
            if seg_len_sq > 0.0001:
                t = max(0.0, min(1.0, ((p_wx - fx) * seg_dx + (p_wy - fy) * seg_dy) / seg_len_sq))
                proj_x = fx + t * seg_dx
                proj_y = fy + t * seg_dy
                if world_distance(proj_x, proj_y, p_wx, p_wy) < danger_radius:
                    return True
        return False

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

    @classmethod
    def _lunge_safe(cls, fighter, tx: float, ty: float, game_map, projectiles: list, reach: float) -> bool:
        """Verifica se uma investida/salto é segura contra buracos (pits) E bombas/armadilhas ativas."""
        if not cls._lunge_clear(fighter, tx, ty, game_map, reach):
            return False
        if cls._is_path_threatened_by_explosives(fighter, tx, ty, projectiles, reach=reach):
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

    def update(self, ai_fighter, opponent, dt: float, game_map, projectiles: list = None, powder_pouches: list = None, decoys: list = None, poison_clouds: list = None):
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
        # 2. Se for Teppo (Rifleman) e estiver RECARREGANDO: manter distância segura ou coronhada defensiva
        if getattr(ai_fighter, "char_type", "") in ("rifleman", "teppo") and not getattr(ai_fighter, "has_ammo", False):
            if dist < 2.0:
                if hasattr(ai_fighter, "trigger_rifle_butt") and random.random() < 0.90:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_rifle_butt(aim_x, aim_y)
                    return
                elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.60:
                    ai_fighter.trigger_evasive_backstep()
                    return
            dx = ai_fighter.wx - opponent.wx
            dy = ai_fighter.wy - opponent.wy
            length = math.hypot(dx, dy)
            if length > 0.05 and ai_fighter.can_move():
                self.move_dir_x, self.move_dir_y = dx / length, dy / length
                self._steer_around_pits(ai_fighter, opponent, game_map)
                ai_fighter.apply_movement(self.move_dir_x, self.move_dir_y, dt, game_map)
                return

        # -------------------------------------------------------------
        # 3. REAÇÃO DEFENSIVA HUMANIZADA (Com Reaction Delay)
        # -------------------------------------------------------------
        incoming_projectile = False
        urgent_proj = None
        min_impact_time = 999.0

        if projectiles:
            for p in projectiles:
                if not getattr(p, "is_active", True) or getattr(p, "owner", None) != opponent:
                    continue
                p_wx, p_wy = p.wx, p.wy
                dist_p = world_distance(ai_fighter.wx, ai_fighter.wy, p_wx, p_wy)
                if dist_p > 8.5:
                    continue

                to_ai_x = ai_fighter.wx - p_wx
                to_ai_y = ai_fighter.wy - p_wy
                vx = getattr(p, "vx", 0.0)
                vy = getattr(p, "vy", 0.0)
                speed_p = math.hypot(vx, vy)

                is_threat = False
                impact_time = dist_p / max(1.0, speed_p)
                is_explosive_p = self._is_bomb_or_hazard_projectile(p, ai_fighter)

                if speed_p > 1.5:
                    # Produto escalar: verifica se voa na direção da IA
                    dot = (to_ai_x * vx + to_ai_y * vy) / (speed_p * max(0.001, dist_p))
                    if dot > 0.25:
                        # Distância perpendicular à trajetória retilínea
                        perp_dist = abs(to_ai_x * vy - to_ai_y * vx) / speed_p
                        if perp_dist < 1.65 and impact_time <= 0.95:
                            is_threat = True
                elif is_explosive_p and dist_p < 3.8:
                    # Bombas no chão/ar, minas ou armadilhas dentro do perímetro de perigo
                    is_threat = True
                    impact_time = 0.05
                elif dist_p < 3.2:
                    # Projéteis estáticos/lentos (fumaça/névoa tóxica)
                    is_threat = True
                    impact_time = 0.20

                if is_threat:
                    incoming_projectile = True
                    if impact_time < min_impact_time:
                        min_impact_time = impact_time
                        urgent_proj = p

        # Ameaça corpo a corpo: detecta alcance estendido (alfanje de Anne, estocadas e avanços têm alcance até ~3.5m)
        is_melee_threat = (
            getattr(opponent, "hitbox_active", False)
            or opponent.state in (STATE_ATTACK, "CUTLASS_CLEAVE", "GATOTSU_CHARGE", "RYUU_TSUI_SEN", "FLECHE")
        ) and dist <= 3.5

        def _execute_defensive_action(is_proj=False, urgent_proj=None):
            threat_x = urgent_proj.wx if (is_proj and urgent_proj) else opponent.wx
            threat_y = urgent_proj.wy if (is_proj and urgent_proj) else opponent.wy
            is_unparriable = is_proj and urgent_proj and self._is_bomb_or_hazard_projectile(urgent_proj, ai_fighter)

            # Se a ameaça NÃO for explosiva/imparável, tenta habilidades de parry ou reflexão
            if not is_unparriable:
                # Musashi (BlueSamurai): Parry mestre de duas lâminas (reflete projéteis e apara melee)
                if ai_fighter.__class__.__name__ == "BlueSamurai" and hasattr(ai_fighter, "trigger_parry"):
                    if ai_fighter.can_move() and ai_fighter.dash_recovery_timer <= 0:
                        ai_fighter.set_facing(threat_x, threat_y)
                        ai_fighter.trigger_parry()
                        return True

                # Julie (Musketeer): Floreio de Capa / Riposte de esgrima (desvia projéteis e contra-ataca melee)
                if ai_fighter.__class__.__name__ == "Musketeer":
                    ai_fighter.set_facing(threat_x, threat_y)
                    if getattr(ai_fighter, "cape_timer", 0.0) <= 0:
                        if hasattr(ai_fighter, "trigger_cloak_riposte"):
                            ai_fighter.trigger_cloak_riposte(threat_x, threat_y, opponent=opponent, projectiles=projectiles)
                            return True
                        elif hasattr(ai_fighter, "trigger_parry"):
                            ai_fighter.trigger_parry(threat_x, threat_y, opponent=opponent)
                            return True
                    elif hasattr(ai_fighter, "trigger_parry"):
                        ai_fighter.trigger_parry(threat_x, threat_y, opponent=opponent)
                        return True

                # Ren (Shaolin Monk): Grito Kiai de 360° repele projéteis e atordoa
                if hasattr(ai_fighter, "trigger_kiai_shout") and getattr(ai_fighter, "kiai_timer", 0.0) <= 0:
                    ai_fighter.trigger_kiai_shout(opponent=opponent, game_map=game_map)
                    return True

                # Chiyo (Twin Nodachi): Dança Mai giratória em vórtice de lâminas
                if hasattr(ai_fighter, "trigger_nodachi_mai") and getattr(ai_fighter, "mai_timer", 0.0) <= 0:
                    ai_fighter.trigger_nodachi_mai(threat_x, threat_y, opponent=opponent)
                    return True

                # O-Rin (Acoustic Minstrel): Pulso de choque acústico ressonante 360° repele oponentes e desvia projéteis
                if hasattr(ai_fighter, "trigger_resonance_shockwave") and getattr(ai_fighter, "resonance_timer", 0.0) <= 0:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_resonance_shockwave(aim_x, aim_y, projectiles)
                    return True

                # Ichi (A Lâmina Cega): Postura de Escuta Auditiva (contra-ataque sensorial automático)
                if hasattr(ai_fighter, "trigger_listen_stance") and getattr(ai_fighter, "listen_timer", 0.0) <= 0:
                    ai_fighter.set_facing(threat_x, threat_y)
                    ai_fighter.trigger_listen_stance(threat_x, threat_y)
                    return True

                # Demais combatentes com trigger_parry genérico (exceto contra bombas/explosivos!)
                if hasattr(ai_fighter, "trigger_parry") and ai_fighter.can_move():
                    ai_fighter.set_facing(threat_x, threat_y)
                    ai_fighter.trigger_parry()
                    return True

            # Kenshin: Dash evasivo (afastando-se ou perpendicular)
            if hasattr(ai_fighter, "trigger_dash"):
                dash_reach = getattr(ai_fighter, "dash_speed", 22.0) * getattr(ai_fighter, "dash_duration", 0.16)
                dx = ai_fighter.wx - threat_x
                dy = ai_fighter.wy - threat_y
                length = math.hypot(dx, dy)
                if length > 0.001:
                    if self._landing_ok(ai_fighter, game_map, dx / length, dy / length, dash_reach):
                        ai_fighter.trigger_dash(dx / length, dy / length)
                        return True
                    for perp in [(-dy / length, dx / length), (dy / length, -dx / length)]:
                        if self._landing_ok(ai_fighter, game_map, perp[0], perp[1], dash_reach):
                            ai_fighter.trigger_dash(perp[0], perp[1])
                            return True

            # Gray Ninja / Kasumi: Bomba de fumaça instantânea
            if hasattr(ai_fighter, "trigger_smoke_bomb") and projectiles is not None:
                aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                ai_fighter.trigger_smoke_bomb(aim_x, aim_y, projectiles)
                return True

            # Rifleman / Teppo: Salto evasivo para trás
            if hasattr(ai_fighter, "trigger_evasive_backstep") and self._away_ok(
                    ai_fighter, opponent, game_map, 1.6):
                ai_fighter.trigger_evasive_backstep()
                return True

            # Okuni / Kabuki: Finta Kawarimi Decoy
            if hasattr(ai_fighter, "trigger_kawarimi_decoy") and (decoys is not None) and self._away_ok(
                    ai_fighter, opponent, game_map, self._roll_reach(ai_fighter)):
                dx = ai_fighter.wx - threat_x
                dy = ai_fighter.wy - threat_y
                ai_fighter.trigger_kawarimi_decoy(dx, dy, decoys)
                return True

            # Kyudo Archer / Tomoe: Flecha de corda
            if not is_unparriable and hasattr(ai_fighter, "trigger_rope_arrow") and projectiles is not None:
                aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                ai_fighter.trigger_rope_arrow(aim_x, aim_y, projectiles, game_map=game_map)
                return True

            # Pirata / Anne: Pólvora nos olhos
            if not is_unparriable and hasattr(ai_fighter, "trigger_gunpowder_blind"):
                aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                ai_fighter.trigger_gunpowder_blind(aim_x, aim_y, opponent=opponent)
                return True

            # Evasão universal: rolamento inteligente
            if hasattr(ai_fighter, "trigger_roll") and ai_fighter.can_act():
                reach = self._roll_reach(ai_fighter)

                # Esquiva inteligente lateral (sidestep 90°) se for projétil com velocidade no ar
                if is_proj and urgent_proj:
                    pvx = getattr(urgent_proj, "vx", 0.0)
                    pvy = getattr(urgent_proj, "vy", 0.0)
                    plen = math.hypot(pvx, pvy)
                    if plen > 0.05:
                        cand1 = (-pvy / plen, pvx / plen)
                        cand2 = (pvy / plen, -pvx / plen)
                        ok1 = self._landing_ok(ai_fighter, game_map, cand1[0], cand1[1], reach)
                        ok2 = self._landing_ok(ai_fighter, game_map, cand2[0], cand2[1], reach)
                        if ok1 and not ok2:
                            ai_fighter.trigger_roll(cand1[0], cand1[1])
                            return True
                        elif ok2 and not ok1:
                            ai_fighter.trigger_roll(cand2[0], cand2[1])
                            return True
                        elif ok1 and ok2:
                            r_dx, r_dy = random.choice([cand1, cand2])
                            ai_fighter.trigger_roll(r_dx, r_dy)
                            return True

                # Rolamento padrão afastando-se da ameaça
                dx = ai_fighter.wx - threat_x
                dy = ai_fighter.wy - threat_y
                length = math.hypot(dx, dy)
                if length > 0.001:
                    if self._landing_ok(ai_fighter, game_map, dx / length, dy / length, reach):
                        ai_fighter.trigger_roll(dx / length, dy / length)
                        return True
                    # Se para trás estiver bloqueado, tenta esquiva lateral (90° / -90°)
                    cand1 = (-dy / length, dx / length)
                    cand2 = (dy / length, -dx / length)
                    ok1 = self._landing_ok(ai_fighter, game_map, cand1[0], cand1[1], reach)
                    ok2 = self._landing_ok(ai_fighter, game_map, cand2[0], cand2[1], reach)
                    if ok1 and not ok2:
                        ai_fighter.trigger_roll(cand1[0], cand1[1])
                        return True
                    elif ok2 and not ok1:
                        ai_fighter.trigger_roll(cand2[0], cand2[1])
                        return True
                    elif ok1 and ok2:
                        r_dx, r_dy = random.choice([cand1, cand2])
                        ai_fighter.trigger_roll(r_dx, r_dy)
                        return True
                    # NUNCA rola na direção de uma bomba ou explosivo!
                    if not is_unparriable and self._landing_ok(ai_fighter, game_map, -dx / length, -dy / length, reach):
                        ai_fighter.trigger_roll(-dx / length, -dy / length)
                        return True
            return False

        # DEFESA CORPO A CORPO (Humanizada com Reaction Delay)
        if is_melee_threat:
            if self.pending_defense_threat != "ATTACK":
                self.pending_defense_threat = "ATTACK"
                self.pending_defense_timer = self._get_reaction_delay()
                self.pending_defense_ready = False
            else:
                self.pending_defense_timer -= dt
                if self.pending_defense_timer <= 0:
                    self.pending_defense_ready = True
        else:
            if self.pending_defense_threat == "ATTACK":
                self.pending_defense_threat = None
                self.pending_defense_timer = 0.0
                self.pending_defense_ready = False

        if is_melee_threat and self.pending_defense_ready:
            self.pending_defense_threat = None
            self.pending_defense_ready = False
            if random.random() < self._get_parry_chance():
                if _execute_defensive_action(is_proj=False):
                    return

        # DEFESA CONTRA PROJÉTEIS: Mantém o delay de reação (com delay de emergência para bombas)
        if incoming_projectile:
            is_urgent_explosive = urgent_proj and self._is_bomb_or_hazard_projectile(urgent_proj, ai_fighter)
            if self.pending_defense_threat != "PROJECTILE":
                self.pending_defense_threat = "PROJECTILE"
                self.pending_defense_timer = self._get_reaction_delay(is_explosive=bool(is_urgent_explosive))
                self.pending_defense_ready = False
            else:
                self.pending_defense_timer -= dt
                if self.pending_defense_timer <= 0:
                    self.pending_defense_ready = True
        else:
            if self.pending_defense_threat == "PROJECTILE":
                self.pending_defense_threat = None
                self.pending_defense_timer = 0.0
                self.pending_defense_ready = False

        if incoming_projectile and self.pending_defense_ready:
            self.pending_defense_threat = None
            self.pending_defense_ready = False
            proj_defense_chance = {
                DIFFICULTY_EASY: 0.70,
                DIFFICULTY_HARD: 0.98,
            }.get(self.difficulty, 0.88)
            if random.random() < proj_defense_chance:
                if _execute_defensive_action(is_proj=True, urgent_proj=urgent_proj):
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
            melee_unsafe = dist <= 3.5 and not self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, 3.8)

            # Ninja Amarelo (Hanzo): estocada melee a curta distância ou arremesso de kunai à média distância
            # Yellow Ninja (Hanzo): estocada frontal de curto alcance ou arremesso de kunai
            if hasattr(ai_fighter, "has_kunai") and hasattr(ai_fighter, "trigger_thrust_attack") and dist <= 1.70 and not melee_unsafe:
                ai_fighter.trigger_thrust_attack(opponent.wx, opponent.wy)
                return
            elif hasattr(ai_fighter, "has_kunai") and ai_fighter.has_kunai and projectiles is not None:
                if 1.8 <= dist <= 6.5 and random.random() < 0.65:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_throw_attack(aim_x, aim_y, projectiles)
                    return

            # American Ninja: shuriken com dispersão ou comando do cão
            if hasattr(ai_fighter, "trigger_shuriken") and projectiles is not None:
                if 1.8 <= dist <= 6.5 and random.random() < 0.60:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_shuriken(aim_x, aim_y, projectiles)
                    return
                if hasattr(ai_fighter, "dog") and ai_fighter.dog and ai_fighter.dog.can_attack() and dist <= 5.0 and random.random() < 0.50:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_dog_attack(aim_x, aim_y)
                    return

            # Gray Ninja (Kasumi): corte de adaga Tanto a curta distância ou bombas à média distância
            if hasattr(ai_fighter, "trigger_tanto_slash") and dist <= 1.80 and not melee_unsafe:
                ai_fighter.trigger_tanto_slash(opponent.wx, opponent.wy)
                return
            if hasattr(ai_fighter, "trigger_throw_bomb") and projectiles is not None:
                if dist < 2.2 and random.random() < 0.40:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_smoke_bomb(aim_x, aim_y, projectiles)
                    return
                elif 1.8 <= dist <= 6.2 and random.random() < 0.70:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_throw_bomb(aim_x, aim_y, projectiles)
                    return

            # Murasaki: Kusarigama com dispersão
            if hasattr(ai_fighter, "trigger_kusarigama_pull") and projectiles is not None:
                if 2.0 <= dist <= 5.0 and random.random() < 0.55:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_kusarigama_pull(aim_x, aim_y, projectiles)
                    return

            # Saitou: Zeroshiki à queima-roupa e Gatotsu à média distância
            if hasattr(ai_fighter, "trigger_gatotsu_thrust"):
                if dist <= 1.65 and hasattr(ai_fighter, "trigger_zeroshiki") and not melee_unsafe:
                    ai_fighter.trigger_zeroshiki(opponent.wx, opponent.wy)
                    return
                elif 2.2 <= dist <= 6.8 and random.random() < 0.60 \
                        and self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, 7.5):
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_gatotsu_thrust(aim_x, aim_y)
                    return

            # Golpes corpo a corpo avançam o lutador: nada de golpear em direção a um buraco aberto ou bomba ativa
            melee_unsafe = dist <= 3.5 and not self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, 3.8)

            # Musashi: Combate com espadas duplas — inicia combo ao se aproximar do oponente
            if hasattr(ai_fighter, "trigger_combo_attack") and not melee_unsafe:
                if dist <= 1.6 and random.random() < 0.75:
                    ai_fighter.trigger_combo_attack(opponent.wx, opponent.wy)
                    return

            # Kenshin: usa o avanço Iai como ferramenta de aproximação à média distância,
            # em vez de só golpear quando já está parado ao lado do oponente
            if hasattr(ai_fighter, "trigger_iai_attack") and not melee_unsafe:
                if 1.6 <= dist <= 3.2 and random.random() < 0.50 and self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, 3.2):
                    ai_fighter.set_facing(opponent.wx, opponent.wy)
                    ai_fighter.trigger_iai_attack(opponent.wx, opponent.wy)
                    return
                # Ryuu Tsui Sen: salto aéreo com i-frames como engajamento alternativo contra zoneadores (seguro contra bombas!)
                if getattr(ai_fighter, "ryuu_timer", 0.0) <= 0 and 2.0 <= dist <= 4.2 and random.random() < 0.40:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    if self._lunge_safe(ai_fighter, aim_x, aim_y, game_map, projectiles, 4.2):
                        ai_fighter.trigger_ryuu_tsui_sen(aim_x, aim_y)
                        return

            # Teppo: tiro com dispersão de mira ou coronhada defensiva
            if hasattr(ai_fighter, "trigger_shoot"):
                if getattr(ai_fighter, "has_ammo", False) and getattr(ai_fighter, "cocking_timer", 0.0) <= 0 and projectiles is not None:
                    if dist >= 1.25 and (random.random() < 0.85 or dist > 2.5):
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_shoot(aim_x, aim_y, projectiles)
                        return
                    elif dist < 1.25:
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_rifle_butt(aim_x, aim_y)
                        return
                elif not melee_unsafe:
                    if dist < 1.80:
                        if hasattr(ai_fighter, "trigger_rifle_butt") and random.random() < 0.85:
                            ai_fighter.trigger_rifle_butt(opponent.wx, opponent.wy)
                            return
                        elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.65 and self._away_ok(
                                ai_fighter, opponent, game_map, 1.6):
                            ai_fighter.trigger_evasive_backstep()
                            return

            # Okuni: Sopro Venenoso Dokukiri, Leques Tessen ou finta Kawarimi
            if hasattr(ai_fighter, "trigger_dokukiri") and poison_clouds is not None:
                if 1.4 <= dist <= 3.2 and getattr(ai_fighter, "poison_cooldown_timer", 0.0) <= 0 and random.random() < 0.65:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_dokukiri(aim_x, aim_y, clouds=poison_clouds)
                    return

            if hasattr(ai_fighter, "trigger_fan_strike") and not melee_unsafe:
                if dist <= 1.70:
                    ai_fighter.trigger_fan_strike(opponent.wx, opponent.wy)
                    return
                elif dist <= 2.2 and random.random() < 0.35 and decoys is not None and self._away_ok(
                        ai_fighter, opponent, game_map, self._roll_reach(ai_fighter)):
                    ai_fighter.trigger_kawarimi_decoy(-ai_fighter.facing_x, -ai_fighter.facing_y, decoys)
                    return

            # Kyudo Archer: arco com dispersão de mira e salva sagrada em arco
            if hasattr(ai_fighter, "trigger_quick_volley") and projectiles is not None:
                if dist >= 2.5 and getattr(ai_fighter, "volley_cooldown_timer", 0.0) <= 0:
                    if random.random() < 0.45:
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_quick_volley(aim_x, aim_y, projectiles)
                        return

            if hasattr(ai_fighter, "trigger_bow_draw") and projectiles is not None:
                if 1.2 <= dist <= 7.5 and random.random() < 0.65:
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
                    if ai_fighter.can_act() and self._toward_ok(ai_fighter, opponent, game_map, self._roll_reach(ai_fighter)) \
                            and self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, self._roll_reach(ai_fighter)):
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

                if 1.20 <= dist <= 2.10 and random.random() < 0.65:
                    ai_fighter.trigger_fleche_thrust(opponent.wx, opponent.wy)
                    return

            # Ren (Shaolin Monk): combo veloz de socos marciais e Kiai
            if hasattr(ai_fighter, "trigger_punch_combo") and not melee_unsafe:
                if dist <= 2.45:
                    ai_fighter.trigger_punch_combo(opponent.wx, opponent.wy)
                    return
                if getattr(ai_fighter, "kiai_timer", 0.0) <= 0 and dist <= 2.6 and random.random() < 0.55:
                    ai_fighter.trigger_kiai_shout(opponent=opponent, game_map=game_map)
                    return

            # Chiyo (Twin Nodachi Kunoichi): tesoura dupla de longo alcance (2.3m) e Dança Mai
            if hasattr(ai_fighter, "trigger_scissor_slash") and not melee_unsafe:
                if 1.2 <= dist <= 2.35 and random.random() < 0.70:
                    ai_fighter.trigger_scissor_slash(opponent.wx, opponent.wy)
                    return
                if getattr(ai_fighter, "mai_timer", 0.0) <= 0 and dist <= 2.1 and random.random() < 0.40:
                    ai_fighter.trigger_nodachi_mai(opponent.wx, opponent.wy, opponent=opponent)
                    return

            # Benkei (Sōhei Warrior Monk): Colossal Thrust / Naginata Throw / Tackle Charge
            if hasattr(ai_fighter, "trigger_naginata_thrust") and not melee_unsafe:
                if getattr(ai_fighter, "is_unarmed", False):
                    # Se desarmado, prioriza Tackle Charge no rival ou buscar arma
                    if getattr(ai_fighter, "tackle_timer", 0.0) <= 0 and dist <= 3.8 and random.random() < 0.75 \
                            and self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, 3.8):
                        ai_fighter.trigger_tackle_charge(opponent.wx, opponent.wy)
                        return
                else:
                    # Se armado e a longa distância (> 4.2m), arremessa a Naginata
                    if getattr(ai_fighter, "throw_timer", 0.0) <= 0 and dist >= 4.2 and random.random() < 0.60:
                        aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                        ai_fighter.trigger_naginata_throw(aim_x, aim_y, projectiles)
                        return
                    # Alcance colossal de 3.2m
                    if 1.3 <= dist <= 3.25 and random.random() < 0.85:
                        ai_fighter.trigger_naginata_thrust(opponent.wx, opponent.wy)
                        return

            # O-Rin (Acoustic Courtesan Minstrel): Kamaitachi Vacuum Blades e Acorde Ressonante
            if hasattr(ai_fighter, "trigger_kamaitachi_pluck"):
                # Se oponente muito perto (< 2.2m), aciona Acorde Ressonante defensivo
                if getattr(ai_fighter, "resonance_timer", 0.0) <= 0 and dist <= 2.2 and random.random() < 0.80:
                    ai_fighter.trigger_resonance_shockwave(opponent.wx, opponent.wy, projectiles)
                    return
                # Ataque Kamaitachi a média/longa distância
                if dist <= 6.8 and random.random() < 0.80:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_kamaitachi_pluck(aim_x, aim_y, projectiles)
                    return

            # Goro (Fazendeiro da Kuwa): Pisotão Sísmico e Descida da Kuwa
            if hasattr(ai_fighter, "trigger_earth_stomp"):
                if getattr(ai_fighter, "stomp_timer", 0.0) <= 0 and dist <= 3.8 and random.random() < 0.75:
                    ai_fighter.trigger_earth_stomp(opponent.wx, opponent.wy, shockwaves=projectiles)
                    return
            if hasattr(ai_fighter, "trigger_kuwa_cleave") and not melee_unsafe:
                if dist <= 2.2 and random.random() < 0.85:
                    ai_fighter.trigger_kuwa_cleave(opponent.wx, opponent.wy)
                    return

            # Ichi (A Lâmina Cega / Shikomizue): Postura de Escuta e Saque Gyaku-Iai
            if hasattr(ai_fighter, "trigger_listen_stance"):
                if getattr(ai_fighter, "listen_timer", 0.0) <= 0 and dist <= 2.8 and (getattr(opponent, "hitbox_active", False) or random.random() < 0.45):
                    ai_fighter.trigger_listen_stance(opponent.wx, opponent.wy)
                    return
            if hasattr(ai_fighter, "trigger_gyaku_iai") and not melee_unsafe:
                if dist <= 2.0 and random.random() < 0.85:
                    ai_fighter.trigger_gyaku_iai(opponent.wx, opponent.wy)
                    return

            # Valerius (Necromante Prussiano): Invocação de Esqueletos e Foice Fúnebre
            if hasattr(ai_fighter, "trigger_summon_undead"):
                if getattr(ai_fighter, "summon_timer", 0.0) <= 0 and dist >= 2.8 and random.random() < 0.50:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_summon_undead(aim_x, aim_y, opponent=opponent)
                    return
            if hasattr(ai_fighter, "trigger_scythe_reap") and not melee_unsafe:
                if dist <= 1.95 and random.random() < 0.75:
                    ai_fighter.trigger_scythe_reap(opponent.wx, opponent.wy)
                    return

            # Seimei (Onmyoji dos Talismãs - Rondel Onmyōdō)
            if hasattr(ai_fighter, "trigger_sacred_ward") or hasattr(ai_fighter, "trigger_ofuda_toss"):
                cur_el = getattr(ai_fighter, "current_element", "wood")
                # Se estiver com elemento defensivo (Madeira, Metal, Terra) e oponente próximo, prioriza rito/barreira
                if cur_el in ("wood", "metal", "earth") and dist <= 2.2 and getattr(ai_fighter, "ward_timer", 0.0) <= 0:
                    ai_fighter.trigger_sacred_ward(opponent.wx, opponent.wy, projectiles=projectiles)
                    return
                # Se estiver com elemento de ataque direto / oráculo à distância, dispara feitiço primário
                if hasattr(ai_fighter, "trigger_ofuda_toss") and getattr(ai_fighter, "ofuda_timer", 0.0) <= 0 and dist <= 5.8 and random.random() < 0.55:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_ofuda_toss(aim_x, aim_y, projectiles)
                    return
                # Em distâncias médias/curtas com rito disponível
                if hasattr(ai_fighter, "trigger_sacred_ward") and getattr(ai_fighter, "ward_timer", 0.0) <= 0 and dist <= 2.4 and random.random() < 0.45:
                    ai_fighter.trigger_sacred_ward(opponent.wx, opponent.wy, projectiles=projectiles)
                    return

            # Daiki (Peregrino do Bastão Bō): Salto com Vara (Pole Vault) e Bastão Bō de Longo Alcance
            if hasattr(ai_fighter, "trigger_pole_vault"):
                if getattr(ai_fighter, "vault_timer", 0.0) <= 0 and 1.8 <= dist <= 3.8 and random.random() < 0.38 \
                        and self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, 4.0):
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_pole_vault(aim_x, aim_y, opponent=opponent, game_map=game_map)
                    return
            if hasattr(ai_fighter, "trigger_bo_strike") and not melee_unsafe:
                if dist <= 2.15 and random.random() < 0.75:
                    ai_fighter.trigger_bo_strike(opponent.wx, opponent.wy)
                    return

            # Aoi (Caçadora Ainu de Hokkaido): Armadilha de Urso (Bear Trap) e Estocada de Lança Op
            if hasattr(ai_fighter, "trigger_bear_trap"):
                if getattr(ai_fighter, "trap_timer", 0.0) <= 0 and 1.4 <= dist <= 3.4 and projectiles is not None and random.random() < 0.55:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_bear_trap(aim_x, aim_y, projectiles=projectiles, game_map=game_map)
                    return
            if hasattr(ai_fighter, "trigger_spear_thrust") and not melee_unsafe:
                if dist <= 1.90 and random.random() < 0.75:
                    ai_fighter.trigger_spear_thrust(opponent.wx, opponent.wy)
                    return

            # Raiden (Yokozuna Invicto): Tachiai Tackle (investida de ombro) e Tsuppari Rush (rajada de palmas)
            if hasattr(ai_fighter, "trigger_tachiai_tackle"):
                if getattr(ai_fighter, "tackle_timer", 0.0) <= 0 and 1.8 <= dist <= 5.2 and random.random() < 0.65 \
                        and self._lunge_safe(ai_fighter, opponent.wx, opponent.wy, game_map, projectiles, 4.5):
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_tachiai_tackle(aim_x, aim_y, opponent=opponent, game_map=game_map)
                    return
            if hasattr(ai_fighter, "trigger_tsuppari_rush") and not melee_unsafe:
                if dist <= 1.85 and random.random() < 0.85:
                    ai_fighter.trigger_tsuppari_rush(opponent.wx, opponent.wy)
                    return

            # Hendrika (Alquimista de Dejima): Frasco Alquímico à média distância e Estilete Perfurante
            if hasattr(ai_fighter, "trigger_stiletto_thrust") and not melee_unsafe:
                if dist <= 1.95:
                    ai_fighter.trigger_stiletto_thrust(opponent.wx, opponent.wy, opponent=opponent)
                    return
            if hasattr(ai_fighter, "trigger_flask_throw"):
                if getattr(ai_fighter, "flask_timer", 0.0) <= 0 and 2.2 <= dist <= 6.0 and projectiles is not None and random.random() < 0.65:
                    aim_x, aim_y = self._get_aim_target(ai_fighter, opponent, opponent.wx, opponent.wy)
                    ai_fighter.trigger_flask_throw(aim_x, aim_y, projectiles=projectiles)
                    return

            # Movimentação Não-Linear e Espaçamento
            if hasattr(ai_fighter, "trigger_kamaitachi_pluck") or hasattr(ai_fighter, "trigger_ofuda_toss"):
                # O-Rin & Seimei são Pure Zoners: se oponente chegar a < 3.0m, recua para manter distância
                if dist < 3.0:
                    dx = ai_fighter.wx - opponent.wx
                    dy = ai_fighter.wy - opponent.wy
                    length = math.hypot(dx, dy)
                    if length > 0.001:
                        self.move_dir_x = dx / length
                        self.move_dir_y = dy / length
                else:
                    dx = opponent.wx - ai_fighter.wx
                    dy = opponent.wy - ai_fighter.wy
                    if dist > 0.001:
                        self.move_dir_x = -dy / dist
                        self.move_dir_y = dx / dist
            elif getattr(ai_fighter, "is_unarmed", False) and getattr(ai_fighter, "active_naginata_projectile", None):
                # Benkei desarmado: corre em direção à Naginata cravada
                proj = ai_fighter.active_naginata_projectile
                if getattr(proj, "is_active", False):
                    pdx = proj.wx - ai_fighter.wx
                    pdy = proj.wy - ai_fighter.wy
                    plen = math.hypot(pdx, pdy)
                    if plen > 0.1:
                        self.move_dir_x = pdx / plen
                        self.move_dir_y = pdy / plen
            elif hasattr(ai_fighter, "trigger_shoot") and not getattr(ai_fighter, "has_ammo", False):
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

        # Evasão e repulsão contínua de bombas, minas e armadilhas no solo
        if projectiles and ai_fighter.can_move():
            bomb_repel_x = 0.0
            bomb_repel_y = 0.0
            nearest_hazard_dist = 999.0
            nearest_hazard = None

            for p in projectiles:
                if not self._is_bomb_or_hazard_projectile(p, ai_fighter):
                    continue
                p_dist = world_distance(ai_fighter.wx, ai_fighter.wy, p.wx, p.wy)
                if p_dist < nearest_hazard_dist:
                    nearest_hazard_dist = p_dist
                    nearest_hazard = p
                # Repulsão se estiver a menos de 3.6m da bomba
                if p_dist < 3.6 and p_dist > 0.001:
                    p_dx = ai_fighter.wx - p.wx
                    p_dy = ai_fighter.wy - p.wy
                    weight = (3.6 - p_dist) / 3.6
                    bomb_repel_x += (p_dx / p_dist) * weight * 3.5
                    bomb_repel_y += (p_dy / p_dist) * weight * 3.5

            if math.hypot(bomb_repel_x, bomb_repel_y) > 0.01:
                self.move_dir_x += bomb_repel_x
                self.move_dir_y += bomb_repel_y
                m_len = math.hypot(self.move_dir_x, self.move_dir_y)
                if m_len > 0.001:
                    self.move_dir_x /= m_len
                    self.move_dir_y /= m_len

            # Se estiver na zona de perigo letal (< 2.2m) e puder agir: esquiva imediata para longe ou perpendicular
            if nearest_hazard is not None and nearest_hazard_dist < 2.2 and ai_fighter.can_act():
                esc_dx = ai_fighter.wx - nearest_hazard.wx
                esc_dy = ai_fighter.wy - nearest_hazard.wy
                esc_len = math.hypot(esc_dx, esc_dy)
                if esc_len > 0.001:
                    reach = self._roll_reach(ai_fighter)
                    if self._landing_ok(ai_fighter, game_map, esc_dx / esc_len, esc_dy / esc_len, reach):
                        if hasattr(ai_fighter, "trigger_roll"):
                            ai_fighter.trigger_roll(esc_dx / esc_len, esc_dy / esc_len)
                            return
                        elif hasattr(ai_fighter, "trigger_dash"):
                            ai_fighter.trigger_dash(esc_dx / esc_len, esc_dy / esc_len)
                            return
                    else:
                        for perp in [(-esc_dy / esc_len, esc_dx / esc_len), (esc_dy / esc_len, -esc_dx / esc_len)]:
                            if self._landing_ok(ai_fighter, game_map, perp[0], perp[1], reach):
                                if hasattr(ai_fighter, "trigger_roll"):
                                    ai_fighter.trigger_roll(perp[0], perp[1])
                                    return
                                elif hasattr(ai_fighter, "trigger_dash"):
                                    ai_fighter.trigger_dash(perp[0], perp[1])
                                    return

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
            if getattr(ai_fighter, "confused_timer", 0.0) > 0:
                self.move_dir_x, self.move_dir_y = -self.move_dir_x, -self.move_dir_y
            ai_fighter.apply_movement(self.move_dir_x, self.move_dir_y, dt, game_map)
            ai_fighter.set_facing(opponent.wx, opponent.wy)

    def _execute_attack(self, fighter, target, projectiles):
        """Executa o ataque primário de acordo com a classe do lutador."""
        # Golpes corpo a corpo avançam o lutador: não ataca em direção a um buraco aberto ou bomba ativa logo à frente
        if world_distance(fighter.wx, fighter.wy, target.wx, target.wy) <= 3.5 \
                and not self._lunge_safe(fighter, target.wx, target.wy, getattr(self, "_map", None), projectiles, 3.8):
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
        elif hasattr(fighter, "trigger_tanto_slash") and world_distance(fighter.wx, fighter.wy, target.wx, target.wy) <= 1.55:
            fighter.trigger_tanto_slash(target.wx, target.wy)
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
        elif hasattr(fighter, "trigger_punch_combo"):
            fighter.trigger_punch_combo(target.wx, target.wy)
        elif hasattr(fighter, "trigger_scissor_slash"):
            fighter.trigger_scissor_slash(target.wx, target.wy)
        elif hasattr(fighter, "trigger_naginata_thrust"):
            if getattr(fighter, "is_unarmed", False):
                if hasattr(fighter, "trigger_tackle_charge") and getattr(fighter, "tackle_timer", 0.0) <= 0:
                    fighter.trigger_tackle_charge(target.wx, target.wy)
            else:
                fighter.trigger_naginata_thrust(target.wx, target.wy)
        elif hasattr(fighter, "trigger_kamaitachi_pluck"):
            if projectiles is not None:
                aim_x, aim_y = self._get_aim_target(fighter, target, target.wx, target.wy)
                fighter.trigger_kamaitachi_pluck(aim_x, aim_y, projectiles)
        elif hasattr(fighter, "trigger_kuwa_cleave"):
            fighter.trigger_kuwa_cleave(target.wx, target.wy)
        elif hasattr(fighter, "trigger_gyaku_iai"):
            fighter.trigger_gyaku_iai(target.wx, target.wy)
        elif hasattr(fighter, "trigger_scythe_reap"):
            fighter.trigger_scythe_reap(target.wx, target.wy)
        elif hasattr(fighter, "trigger_ofuda_toss"):
            if projectiles is not None:
                aim_x, aim_y = self._get_aim_target(fighter, target, target.wx, target.wy)
                fighter.trigger_ofuda_toss(aim_x, aim_y, projectiles)
        elif hasattr(fighter, "trigger_bo_strike"):
            fighter.trigger_bo_strike(target.wx, target.wy)
        elif hasattr(fighter, "trigger_spear_thrust"):
            fighter.trigger_spear_thrust(target.wx, target.wy)
        elif hasattr(fighter, "trigger_tsuppari_rush"):
            fighter.trigger_tsuppari_rush(target.wx, target.wy)
        elif hasattr(fighter, "trigger_stiletto_thrust"):
            fighter.trigger_stiletto_thrust(target.wx, target.wy, opponent=target)
