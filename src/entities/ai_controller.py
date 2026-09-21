"""
Inteligência Artificial tática capaz de controlar todos os combatentes da arena.
Adapta-se ao kit de habilidades de cada guerreiro (combos, parry, iai, kunai,
tiro de Tanegashima com coleta de pólvora, leques de aço com finta Kawarimi, etc.).
"""
import math
import random
from src.isometric.iso_math import world_distance
from src.entities.samurai import STATE_RECOVERY, STATE_ATTACK, STATE_IDLE, STATE_WALK

class SamuraiAI:
    def __init__(self):
        self.decision_timer = 0.0
        self.move_dir_x = 0.0
        self.move_dir_y = 0.0

    def update(self, ai_fighter, opponent, dt: float, game_map, projectiles: list = None, powder_pouches: list = None, decoys: list = None):
        """Atualiza a IA controlando ai_fighter contra o opponent."""
        if not ai_fighter.is_alive or not opponent.is_alive:
            return

        self.decision_timer -= dt
        dist = world_distance(ai_fighter.wx, ai_fighter.wy, opponent.wx, opponent.wy)

        # 1. Se for Ninja e estiver DESARMADO: prioridade máxima é correr até a kunai no chão!
        if hasattr(ai_fighter, "has_kunai") and not ai_fighter.has_kunai and projectiles:
            ground_kunai = None
            for p in projectiles:
                if p.owner == ai_fighter and p.state == "ON_GROUND":
                    ground_kunai = p
                    break
            if ground_kunai:
                dx = ground_kunai.wx - ai_fighter.wx
                dy = ground_kunai.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0.05 and ai_fighter.can_move():
                    ai_fighter.apply_movement(dx / length, dy / length, dt, game_map)
                    return

        # 2. Se for Teppo (Rifleman) e estiver SEM MUNIÇÃO: caçar PowderPouch mais próximo!
        if getattr(ai_fighter, "char_type", "") in ("rifleman", "teppo") and not getattr(ai_fighter, "has_ammo", False) and powder_pouches:
            active_pouches = [p for p in powder_pouches if p.is_active]
            if active_pouches:
                nearest_pouch = min(active_pouches, key=lambda p: world_distance(ai_fighter.wx, ai_fighter.wy, p.wx, p.wy))
                # Se o oponente estiver muito próximo durante a busca, defender com coronhada ou backstep
                if dist < 1.5:
                    if hasattr(ai_fighter, "trigger_rifle_butt") and random.random() < 0.70:
                        ai_fighter.trigger_rifle_butt(opponent.wx, opponent.wy)
                        return
                    elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.60:
                        ai_fighter.trigger_evasive_backstep()
                        return

                dx = nearest_pouch.wx - ai_fighter.wx
                dy = nearest_pouch.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0.05 and ai_fighter.can_move():
                    ai_fighter.apply_movement(dx / length, dy / length, dt, game_map)
                    return

        # 3. Reação defensiva a ataques adversários ou projéteis perigosos em aproximação
        incoming_projectile = False
        if projectiles:
            for p in projectiles:
                if getattr(p, "is_active", True) and getattr(p, "owner", None) == opponent:
                    if world_distance(ai_fighter.wx, ai_fighter.wy, p.wx, p.wy) < 3.2:
                        incoming_projectile = True
                        break

        if (opponent.state == STATE_ATTACK and dist < 2.5) or incoming_projectile:
            # Se for Musashi: tenta Parry
            if hasattr(ai_fighter, "trigger_parry") and random.random() < 0.65:
                ai_fighter.set_facing(opponent.wx, opponent.wy)
                ai_fighter.trigger_parry()
                return
            # Se for Kenshin: tenta Dash evasivo
            elif hasattr(ai_fighter, "trigger_dash") and random.random() < 0.50:
                dx = ai_fighter.wx - opponent.wx
                dy = ai_fighter.wy - opponent.wy
                length = math.hypot(dx, dy)
                if length > 0:
                    ai_fighter.trigger_dash(dx / length, dy / length)
                    return
            # Se for Gray Ninja: solta bomba de fumaça instantânea para desacelerar o adversário
            elif hasattr(ai_fighter, "trigger_smoke_bomb") and projectiles is not None and random.random() < 0.60:
                ai_fighter.trigger_smoke_bomb(opponent.wx, opponent.wy, projectiles)
                return
            # Se for Rifleman: salto evasivo para trás
            elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.70:
                ai_fighter.trigger_evasive_backstep()
                return
            # Se for Okuni (Kabuki): finta Kawarimi Decoy (deixa boneco e evade)
            elif hasattr(ai_fighter, "trigger_kawarimi_decoy") and (decoys is not None) and random.random() < 0.75:
                dx = ai_fighter.wx - opponent.wx
                dy = ai_fighter.wy - opponent.wy
                ai_fighter.trigger_kawarimi_decoy(dx, dy, decoys)
                return
            # Se for Kyudo Archer: flecha de corda para fuga rápida
            elif hasattr(ai_fighter, "trigger_rope_arrow") and projectiles is not None and random.random() < 0.65:
                ai_fighter.trigger_rope_arrow(opponent.wx, opponent.wy, projectiles)
                return
            # Se for Pirata (Anne): pólvora nos olhos para cegar o oponente
            elif hasattr(ai_fighter, "trigger_gunpowder_blind") and random.random() < 0.60:
                ai_fighter.trigger_gunpowder_blind(opponent.wx, opponent.wy, opponent=opponent)
                return
            # Se for Mosqueteira (Julie): riposte com a capa para anular o golpe
            elif hasattr(ai_fighter, "trigger_cloak_riposte") and random.random() < 0.65:
                ai_fighter.trigger_cloak_riposte()
                return

        # 4. Punição quando o oponente estiver em RECOVERY ou STUNNED
        if opponent.state in (STATE_RECOVERY, "STUNNED"):
            ai_fighter.set_facing(opponent.wx, opponent.wy)
            # Se for American Ninja e o oponente estiver atordoado ou vulnerável: MANDA O DOBERMAN!
            if hasattr(ai_fighter, "dog") and ai_fighter.dog and ai_fighter.dog.can_attack():
                ai_fighter.trigger_dog_attack(opponent.wx, opponent.wy)
                return

            if dist < 2.2:
                self._execute_attack(ai_fighter, opponent, projectiles)
                return
            else:
                dx = opponent.wx - ai_fighter.wx
                dy = opponent.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0 and ai_fighter.can_move():
                    ai_fighter.apply_movement(dx / length, dy / length, dt, game_map)
                return

        # 5. Comportamento Neutro / Espaçamento
        if self.decision_timer <= 0:
            self.decision_timer = random.uniform(0.28, 0.55)
            # Chance de Ninja arremessar kunai a média distância
            if hasattr(ai_fighter, "has_kunai") and ai_fighter.has_kunai and projectiles is not None:
                if 2.2 <= dist <= 5.5 and random.random() < 0.4:
                    ai_fighter.trigger_throw_attack(opponent.wx, opponent.wy, projectiles)
                    return

            # American Ninja: arremessar shurikens a média/longa distância
            if hasattr(ai_fighter, "trigger_shuriken") and projectiles is not None:
                if 2.0 <= dist <= 6.0 and random.random() < 0.6:
                    ai_fighter.trigger_shuriken(opponent.wx, opponent.wy, projectiles)
                    return
                # Ou mandar o Doberman se tiver boa oportunidade
                if hasattr(ai_fighter, "dog") and ai_fighter.dog and ai_fighter.dog.can_attack() and dist <= 4.5 and random.random() < 0.45:
                    ai_fighter.trigger_dog_attack(opponent.wx, opponent.wy)
                    return

            # Gray Ninja: arremessar bomba relógio a média distância ou fumaça se estiver cercado
            if hasattr(ai_fighter, "trigger_throw_bomb") and projectiles is not None:
                if dist < 2.2 and random.random() < 0.5:
                    ai_fighter.trigger_smoke_bomb(opponent.wx, opponent.wy, projectiles)
                    return
                elif 2.0 <= dist <= 5.5 and random.random() < 0.55:
                    ai_fighter.trigger_throw_bomb(opponent.wx, opponent.wy, projectiles)
                    return

            # Purple Ninja (Murasaki): arremessar Kusarigama para puxar a média distância
            if hasattr(ai_fighter, "trigger_kusarigama_pull") and projectiles is not None:
                if 2.0 <= dist <= 5.0 and random.random() < 0.55:
                    ai_fighter.trigger_kusarigama_pull(opponent.wx, opponent.wy, projectiles)
                    return

            # Hajime Saitou: disparar Gatotsu acelerado na média/longa distância
            if hasattr(ai_fighter, "trigger_gatotsu_thrust"):
                if 2.8 <= dist <= 6.8 and random.random() < 0.50:
                    ai_fighter.trigger_gatotsu_thrust(opponent.wx, opponent.wy)
                    return

            # Teppo (Rifleman): disparar tiro se tiver munição e arma engatilhada
            if hasattr(ai_fighter, "trigger_shoot"):
                if getattr(ai_fighter, "has_ammo", False) and getattr(ai_fighter, "cocking_timer", 0.0) <= 0 and projectiles is not None:
                    if 2.5 <= dist <= 8.5 and random.random() < 0.70:
                        ai_fighter.trigger_shoot(opponent.wx, opponent.wy, projectiles)
                        return
                else:
                    if dist < 1.6:
                        if hasattr(ai_fighter, "trigger_rifle_butt") and random.random() < 0.75:
                            ai_fighter.trigger_rifle_butt(opponent.wx, opponent.wy)
                            return
                        elif hasattr(ai_fighter, "trigger_evasive_backstep") and random.random() < 0.65:
                            ai_fighter.trigger_evasive_backstep()
                            return

            # Okuni: dança dos leques em aproximação corpo a corpo ou finta Kawarimi
            if hasattr(ai_fighter, "trigger_fan_strike"):
                if dist <= 1.45:
                    ai_fighter.trigger_fan_strike(opponent.wx, opponent.wy)
                    return
                elif dist <= 2.2 and random.random() < 0.35 and decoys is not None:
                    ai_fighter.trigger_kawarimi_decoy(-ai_fighter.facing_x, -ai_fighter.facing_y, decoys)
                    return

            # Kyudo Archer: puxar corda do arco a média/longa distância
            if hasattr(ai_fighter, "trigger_bow_draw") and projectiles is not None:
                if 2.8 <= dist <= 7.5 and random.random() < 0.55:
                    ai_fighter.trigger_bow_draw(opponent.wx, opponent.wy, projectiles)
                    return

            # Pirata (Anne): sopro de pólvora nos olhos a curta/média distância
            if hasattr(ai_fighter, "trigger_gunpowder_blind"):
                if 1.6 <= dist <= 3.2 and random.random() < 0.60:
                    ai_fighter.trigger_gunpowder_blind(opponent.wx, opponent.wy, opponent=opponent)
                    return

            # Mosqueteira (Julie): investida longa Fleche
            if hasattr(ai_fighter, "trigger_fleche_thrust"):
                if 1.4 <= dist <= 2.8 and random.random() < 0.60:
                    ai_fighter.trigger_fleche_thrust(opponent.wx, opponent.wy)
                    return

            # Comportamento de Movimentação do Teppo (afasta se armado, busca se desarmado)
            if hasattr(ai_fighter, "trigger_shoot") and not getattr(ai_fighter, "has_ammo", False):
                # Se não há pouches por perto, recua do adversário
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
                # Aproximar
                dx = opponent.wx - ai_fighter.wx
                dy = opponent.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                if length > 0.001:
                    self.move_dir_x = dx / length
                    self.move_dir_y = dy / length
                else:
                    self.move_dir_x = 1.0
                    self.move_dir_y = 0.0
            elif dist < 1.45:
                if random.random() < 0.60:
                    self._execute_attack(ai_fighter, opponent, projectiles)
                else:
                    # Recuar ligeiramente
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

        if ai_fighter.can_move():
            ai_fighter.apply_movement(self.move_dir_x, self.move_dir_y, dt, game_map)
            ai_fighter.set_facing(opponent.wx, opponent.wy)

    def _execute_attack(self, fighter, target, projectiles):
        """Executa o ataque primário de acordo com a classe do lutador."""
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
                fighter.trigger_shuriken(target.wx, target.wy, projectiles)
        elif hasattr(fighter, "trigger_throw_bomb"):
            if projectiles is not None:
                fighter.trigger_throw_bomb(target.wx, target.wy, projectiles)
        elif hasattr(fighter, "trigger_kama_strike"):
            fighter.trigger_kama_strike(target.wx, target.wy)
        elif hasattr(fighter, "trigger_gatotsu_thrust"):
            dist = world_distance(fighter.wx, fighter.wy, target.wx, target.wy)
            if dist < 1.3:
                fighter.trigger_zeroshiki(target.wx, target.wy)
            else:
                fighter.trigger_gatotsu_thrust(target.wx, target.wy)
        elif hasattr(fighter, "trigger_shoot"):
            if getattr(fighter, "has_ammo", False) and getattr(fighter, "cocking_timer", 0.0) <= 0 and projectiles is not None:
                fighter.trigger_shoot(target.wx, target.wy, projectiles)
            elif hasattr(fighter, "trigger_rifle_butt"):
                fighter.trigger_rifle_butt(target.wx, target.wy)
        elif hasattr(fighter, "trigger_bow_draw"):
            fighter.trigger_bow_draw(target.wx, target.wy, projectiles)
        elif hasattr(fighter, "trigger_cutlass_cleave"):
            fighter.trigger_cutlass_cleave(target.wx, target.wy)
        elif hasattr(fighter, "trigger_fleche_thrust"):
            fighter.trigger_fleche_thrust(target.wx, target.wy)
