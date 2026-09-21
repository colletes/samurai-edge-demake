"""
Inteligência Artificial tática capaz de controlar Musashi, Kenshin ou Ninja Hanzo.
Adapta-se ao kit de habilidades de cada guerreiro (combos, parry, iai ou arremesso/coleta de kunai).
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

    def update(self, ai_fighter, opponent, dt: float, game_map, projectiles: list = None):
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

        # 2. Reação defensiva a ataques adversários
        if opponent.state == STATE_ATTACK and dist < 2.5:
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
            # Se for Kabuki: pirueta acrobática evasiva
            elif hasattr(ai_fighter, "trigger_acrobatic_dodge") and random.random() < 0.75:
                dx = ai_fighter.wx - opponent.wx
                dy = ai_fighter.wy - opponent.wy
                ai_fighter.trigger_acrobatic_dodge(dx, dy)
                return
            # Se for Kyudo Archer: flecha de corda para fuga rápida
            elif hasattr(ai_fighter, "trigger_rope_arrow") and projectiles is not None and random.random() < 0.65:
                ai_fighter.trigger_rope_arrow(opponent.wx, opponent.wy, projectiles)
                return

        # 3. Punição quando o oponente estiver em RECOVERY ou STUNNED
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

        # 4. Comportamento Específico: Kabuki pós-veneno (Sobrevivência Pura!)
        if hasattr(ai_fighter, "has_poisoned_target") and ai_fighter.has_poisoned_target:
            # Fugir ativamente do oponente envenenado que está sob efeito de fúria!
            dx = ai_fighter.wx - opponent.wx
            dy = ai_fighter.wy - opponent.wy
            length = math.hypot(dx, dy)
            if dist < 2.8 and hasattr(ai_fighter, "trigger_acrobatic_dodge"):
                ai_fighter.trigger_acrobatic_dodge(dx, dy)
            elif length > 0 and ai_fighter.can_move():
                ai_fighter.apply_movement(dx / length, dy / length, dt, game_map)
            return

        # 5. Comportamento Específico: Rifleman recarregando
        if hasattr(ai_fighter, "has_ammo") and not ai_fighter.has_ammo:
            ai_fighter.trigger_reload_hold()
            # Manter distância enquanto recarrega
            dx = ai_fighter.wx - opponent.wx
            dy = ai_fighter.wy - opponent.wy
            length = math.hypot(dx, dy)
            if dist < 2.2 and hasattr(ai_fighter, "trigger_evasive_backstep"):
                ai_fighter.trigger_evasive_backstep()
            elif length > 0 and ai_fighter.can_move():
                ai_fighter.apply_movement(dx / length, dy / length, dt, game_map)
            return

        # 6. Comportamento Neutro / Espaçamento
        if self.decision_timer <= 0:
            self.decision_timer = random.uniform(0.3, 0.65)
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

            # Rifleman: disparar tiro supersônico se tiver munição
            if hasattr(ai_fighter, "trigger_shoot") and getattr(ai_fighter, "has_ammo", False) and projectiles is not None:
                if 2.5 <= dist <= 8.5 and random.random() < 0.65:
                    ai_fighter.trigger_shoot(opponent.wx, opponent.wy, projectiles)
                    return

            # Kabuki: sopro de veneno a média distância
            if hasattr(ai_fighter, "trigger_poison_spit") and not getattr(ai_fighter, "has_poisoned_target", False) and projectiles is not None:
                if 1.8 <= dist <= 4.8 and random.random() < 0.55:
                    ai_fighter.trigger_poison_spit(opponent.wx, opponent.wy, projectiles)
                    return

            # Kyudo Archer: puxar corda do arco a média/longa distância
            if hasattr(ai_fighter, "trigger_bow_draw") and projectiles is not None:
                if 2.8 <= dist <= 7.5 and random.random() < 0.55:
                    ai_fighter.trigger_bow_draw(opponent.wx, opponent.wy, projectiles)
                    return

            if dist > 3.2:
                # Aproximar
                dx = opponent.wx - ai_fighter.wx
                dy = opponent.wy - ai_fighter.wy
                length = math.hypot(dx, dy)
                self.move_dir_x = dx / length
                self.move_dir_y = dy / length
            elif dist < 1.6:
                if random.random() < 0.55:
                    self._execute_attack(ai_fighter, opponent, projectiles)
                else:
                    # Recuar um pouco
                    dx = ai_fighter.wx - opponent.wx
                    dy = ai_fighter.wy - opponent.wy
                    length = math.hypot(dx, dy)
                    self.move_dir_x = dx / length
                    self.move_dir_y = dy / length
            else:
                # Circunavegar lateralmente
                dx = opponent.wx - ai_fighter.wx
                dy = opponent.wy - ai_fighter.wy
                self.move_dir_x = -dy / dist
                self.move_dir_y = dx / dist

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
        elif hasattr(fighter, "trigger_shoot") and getattr(fighter, "has_ammo", False):
            if projectiles is not None:
                fighter.trigger_shoot(target.wx, target.wy, projectiles)
        elif hasattr(fighter, "trigger_poison_spit") and not getattr(fighter, "has_poisoned_target", False):
            if projectiles is not None:
                fighter.trigger_poison_spit(target.wx, target.wy, projectiles)
        elif hasattr(fighter, "trigger_bow_draw"):
            fighter.trigger_bow_draw(target.wx, target.wy, projectiles)
