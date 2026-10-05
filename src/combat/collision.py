"""
Gerenciador de regras de combate: lâminas, kunais, shurikens com stun,
botes letais do cão Doberman e contra-ataques que nocauteiam o cão.
"""
import math
from src.isometric.iso_math import world_distance
from src.effects.particles import (
    SparkParticle, BloodParticle, FloatingBanner
)
from src.entities.samurai import STATE_PARRY, STATE_RECOVERY, STATE_STUNNED
from src.entities.projectile import (
    KunaiProjectile, ShurikenProjectile, TimedBombEntity, SmokeCloudEntity,
    KusarigamaChainEntity, MusketBulletProjectile, PoisonCloudProjectile,
    KyudoArrowProjectile, RopeArrowProjectile, CannonballProjectile,
    RemoteMineEntity, HamayaArrowProjectile, MusashiWaveProjectile
)
from src.entities.doberman import STATE_DOG_CHARGE, STATE_DOG_KNOCKED_OUT, STATE_DOG_BARK

def _get_death_style_for_attacker(attacker, weapon: str | None = None):
    """Estilo de morte pelo golpe recebido: `weapon` (kunai, shuriken, arrow) tem prioridade sobre o atacante."""
    if weapon in ("kunai", "shuriken"):
        return "KUNAI_PIN"
    if weapon == "arrow":
        return "ARROW_PIN"
    char_type = getattr(attacker, "char_type", "").lower()
    state = getattr(attacker, "state", "")
    if "kenshin" in char_type or "red" in char_type:
        return "KENSHIN_SPLIT"
    elif "murasaki" in char_type or "purple" in char_type:
        return "MURASAKI_DECAP"
    elif "pirate" in char_type or "anne" in char_type:
        return "PIRATE_CLEAVE"
    elif "musketeer" in char_type or "julie" in char_type or "saitou" in char_type or state == "GATOTSU_CHARGE":
        return "SAITOU_IMPALE"
    elif "ninja" in char_type or "hanzo" in char_type or "joe" in char_type or "american" in char_type \
            or "gray" in char_type or "kasumi" in char_type or "kemuri" in char_type:
        return "STAB_FALL"
    elif "rifle" in char_type or "teppo" in char_type or "tomoe" in char_type or "archer" in char_type:
        return "BLUNT_FALL"
    elif "kabuki" in char_type or "okuni" in char_type:
        return "MURASAKI_DECAP"
    return "KENSHIN_SPLIT"

# Maior que o alcance do combo de Musashi (hitbox 0.9 + 2.06 + raio), para o ferido não contra-atacar na hora.
HIT_KNOCKBACK_DISTANCE = 3.6

class CombatSystem:
    def __init__(self):
        self.hitstop_timer = 0.0

    @staticmethod
    def _apply_hit_knockback(attacker, victim, game_map):
        """Empurra o ferido (não morto) para longe do agressor; pode arremessá-lo em um buraco."""
        dx = victim.wx - attacker.wx
        dy = victim.wy - attacker.wy
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            dx, dy = attacker.facing_x, attacker.facing_y
            dist = math.hypot(dx, dy) or 1.0
        ux, uy = dx / dist, dy / dist
        travel = HIT_KNOCKBACK_DISTANCE
        pit_at = getattr(game_map, "pit_at", None)
        if pit_at is not None:
            # Um buraco no caminho captura o ferido em vez de ele "pular" por cima.
            step = 0.1
            for i in range(1, int(HIT_KNOCKBACK_DISTANCE / step) + 1):
                if pit_at(victim.wx + ux * step * i, victim.wy + uy * step * i) is not None:
                    travel = step * i
                    break
        victim.apply_forced_displacement(ux * travel, uy * travel, game_map)

    def _play_sound(self, event, volume: float = 1.0):
        """Helper seguro para disparo de efeitos sonoros em combate."""
        try:
            from src.audio import get_sound_manager, SoundEvent
            ev = getattr(SoundEvent, event.upper(), event) if isinstance(event, str) else event
            get_sound_manager().play(ev, volume_scale=volume)
        except Exception:
            pass

    def process_combat(self, p1, p2, game_map, particles: list, banners: list, camera, projectiles: list, dt: float = 0.016, cinematic_director = None, decoys: list = None, ctrl_mgr = None, clash_system = None) -> str | None:
        """
        Processa interações de combate: corpo a corpo, projéteis e ataques de cães.
        Retorna 'P1_WINS', 'P2_WINS' ou None.
        """
        winner = None

        # -------------------------------------------------------------
        # 1. ATUALIZAR E PROCESSAR PROJÉTEIS (KUNAI, SHURIKEN, BALAS, FLECHAS, ETC.)
        # -------------------------------------------------------------
        # Deflexão de Projéteis por Lâminas e Habilidades Ativas
        # -------------------------------------------------------------
        for def_fighter in (p1, p2):
            if not def_fighter.is_alive:
                continue
            char_t = getattr(def_fighter, "char_type", "")

            # 1. Kenshin: Iai Flash ou Shukuchi Dash
            if char_t == "kenshin" and (def_fighter.hitbox_active or def_fighter.state in ("ATTACK", "SHUKUCHI")):
                kx = def_fighter.hitbox_center[0] if def_fighter.hitbox_active else def_fighter.wx
                ky = def_fighter.hitbox_center[1] if def_fighter.hitbox_active else def_fighter.wy
                kr = def_fighter.hitbox_radius if def_fighter.hitbox_active else 1.25
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        if world_distance(kx, ky, proj.wx, proj.wy) < (kr + 0.45):
                            proj.is_active = False
                            for _ in range(12):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                            banners.append(FloatingBanner("SLASH DEFLECTION!", proj.wx, proj.wy, wz=1.7, color=(255, 230, 80)))
                            camera.add_shake(5.0)
                            self._play_sound("sword_clash")

            # 2. Murasaki: Giro Protetor de Corrente da Kusarigama (Apenas Frente - Item 10)
            elif getattr(def_fighter, "is_spinning_chain", False):
                mx, my = def_fighter.wx, def_fighter.wy
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        dist = world_distance(mx, my, proj.wx, proj.wy)
                        if dist < 1.75:
                            dx = proj.wx - def_fighter.wx
                            dy = proj.wy - def_fighter.wy
                            dot = (dx * def_fighter.facing_x + dy * def_fighter.facing_y) / max(0.001, dist)
                            if dot > 0.15:  # Protege estritamente a frente (cone de ~140°)
                                proj.is_active = False
                                for _ in range(12):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                                banners.append(FloatingBanner("FRONTAL CHAIN DEFLECTION!", proj.wx, proj.wy, wz=1.7, color=(220, 140, 255)))
                                camera.add_shake(5.0)
                                self._play_sound("chain_whip")

            # 3. Anne: Corte em Meia-Lua do Alfanje (Cutlass Cleave Deflection ampliado)
            elif char_t == "pirate" and def_fighter.hitbox_active:
                cx, cy = def_fighter.hitbox_center
                cr = def_fighter.hitbox_radius
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        if world_distance(cx, cy, proj.wx, proj.wy) < (cr + 0.65):
                            proj.is_active = False
                            for _ in range(12):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                            banners.append(FloatingBanner("CUTLASS DEFLECTION!", proj.wx, proj.wy, wz=1.7, color=(255, 215, 80)))
                            camera.add_shake(5.0)
                            self._play_sound("sword_clash")

            # 4. Tomoe: Barreira dos Ventos Kami (Ofuda Ward Deflection)
            elif getattr(def_fighter, "is_ofuda_active", None) and def_fighter.is_ofuda_active():
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        if world_distance(def_fighter.wx, def_fighter.wy, proj.wx, proj.wy) < 1.85:
                            proj.is_active = False
                            for _ in range(10):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.5))
                            banners.append(FloatingBanner("OFUDA WARD!", proj.wx, proj.wy, wz=1.7, color=(120, 220, 160)))
                            camera.add_shake(4.0)
                            self._play_sound("parry")

            # 5. Julie: Floreio de Capa Defensivo (Cape Deflection - Cone Frontal de ~120°)
            elif char_t == "musketeer" and def_fighter.state == "CAPE_FLOURISH":
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        dist = world_distance(def_fighter.wx, def_fighter.wy, proj.wx, proj.wy)
                        if dist < 1.95:
                            # Verifica cone frontal: apenas projéteis vindos de frente são defletidos
                            proj_dx = proj.wx - def_fighter.wx
                            proj_dy = proj.wy - def_fighter.wy
                            dot = (proj_dx * def_fighter.facing_x + proj_dy * def_fighter.facing_y) / max(0.001, dist)
                            if dot > 0.0:  # Cone frontal de 90° de cada lado (180° total de frente)
                                proj.is_active = False
                                for _ in range(12):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.55, color=(100, 180, 255)))
                                banners.append(FloatingBanner("CAPE DEFLECTION!", def_fighter.wx, def_fighter.wy, wz=1.75, color=(100, 180, 255)))
                                camera.add_shake(4.5)
                                self._play_sound("dodge_whoosh")



        active_projectiles = []
        for proj in projectiles:
            if isinstance(proj, HamayaArrowProjectile):
                still_valid = proj.update(dt, game_map, particles, projectiles=projectiles)
            else:
                still_valid = proj.update(dt, game_map, particles)
            if not still_valid:
                continue

            # Interceptação de projéteis por bonecos Kawarimi (Decoys)
            if decoys:
                decoy_intercepted = False
                for decoy in decoys:
                    if decoy.is_active and getattr(proj, "owner", None) != decoy.owner:
                        if world_distance(proj.wx, proj.wy, decoy.wx, decoy.wy) < (decoy.radius + 0.45):
                            proj.is_active = False
                            decoy.on_hit(getattr(proj, "owner", None), particles, banners, camera)
                            decoy_intercepted = True
                            break
                if decoy_intercepted or not getattr(proj, "is_active", True):
                    continue

            # Item 23: O cão do ninja americano é atingível por armas e projéteis inimigos
            target_dog = None
            if getattr(proj, "owner", None) == p1 and hasattr(p2, "dog") and p2.dog and p2.dog.state != "KNOCKED_OUT":
                target_dog = p2.dog
            elif getattr(proj, "owner", None) == p2 and hasattr(p1, "dog") and p1.dog and p1.dog.state != "KNOCKED_OUT":
                target_dog = p1.dog

            if target_dog and not isinstance(proj, (TimedBombEntity, RemoteMineEntity)):
                proj_flying = (getattr(proj, "state", "FLYING") == "FLYING") if hasattr(proj, "state") else getattr(proj, "is_active", True)
                if proj_flying and world_distance(proj.wx, proj.wy, target_dog.wx, target_dog.wy) < (0.45 + target_dog.radius):
                    target_dog.knock_out(2.0)
                    camera.add_shake(6.0)
                    banners.append(FloatingBanner("DOG STUNNED! (2.0s)", target_dog.wx, target_dog.wy, wz=1.4, color=(255, 80, 80)))
                    for _ in range(12):
                        particles.append(SparkParticle(target_dog.wx, target_dog.wy, 0.4))
                    if isinstance(proj, KunaiProjectile):
                        proj.state = "ON_GROUND"
                        proj.wz = 0.05
                    else:
                        proj.is_active = False
                    continue

            # Se for KUNAI em vôo
            if isinstance(proj, KunaiProjectile) and proj.state == "FLYING":
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"

                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.45 + target.radius):
                    if target.state == STATE_PARRY:
                        # Musashi pode refletir projéteis durante os primeiros 0.15s da parry
                        if (target.__class__.__name__ == "BlueSamurai" and 
                            getattr(target, "parry_reflect_active_timer", 0) > 0 and 
                            not getattr(proj, "has_been_reflected", False)):
                            # REFLETE: inverte direção e muda dono
                            proj.vx = -proj.vx
                            proj.vy = -proj.vy
                            proj.dir_x = -proj.dir_x
                            proj.dir_y = -proj.dir_y
                            proj.owner = target
                            proj.has_been_reflected = True
                            proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                            banners.append(FloatingBanner("PARRY REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                            camera.add_shake(6.0)
                            self._play_sound("parry")
                        else:
                            # Absorção normal de parry
                            for _ in range(10):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                            banners.append(FloatingBanner("PARRY KUNAI!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                            camera.add_shake(5.0)
                            self._play_sound("parry")
                            proj.state = "ON_GROUND"
                            proj.wz = 0.05
                    else:
                        hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=2)
                        if dead:
                            camera.add_shake(15.0)
                            banners.append(FloatingBanner("KUNAI SNIPE - 1 HIT KILL!", target.wx, target.wy, wz=1.8, color=(255, 220, 50)))
                            for _ in range(25):
                                particles.append(BloodParticle(target.wx, target.wy, 0.6))
                            self.hitstop_timer = 0.12
                            winner = winner_id
                            proj.is_active = False
                            self._play_sound("fatal_strike")
                            if cinematic_director:
                                death_style = _get_death_style_for_attacker(proj.owner, weapon="kunai")
                                cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))

            # Se for SHURIKEN (Não mata! Apenas aplica stun!)
            elif isinstance(proj, ShurikenProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1

                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.45 + target.radius):
                    if target.state == STATE_PARRY:
                        # Musashi pode refletir projéteis durante os primeiros 0.15s da parry
                        if (target.__class__.__name__ == "BlueSamurai" and 
                            getattr(target, "parry_reflect_active_timer", 0) > 0 and 
                            not getattr(proj, "has_been_reflected", False)):
                            # REFLETE: inverte direção e muda dono
                            proj.vx = -proj.vx
                            proj.vy = -proj.vy
                            proj.dir_x = -proj.dir_x
                            proj.dir_y = -proj.dir_y
                            proj.owner = target
                            proj.has_been_reflected = True
                            proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                            banners.append(FloatingBanner("PARRY REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                            camera.add_shake(6.0)
                            self._play_sound("parry")
                        else:
                            # Absorção normal de parry
                            for _ in range(8):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                            banners.append(FloatingBanner("PARRY!", target.wx, target.wy, wz=1.6, color=(100, 200, 255)))
                            self._play_sound("parry")
                    else:
                        is_target_moving = getattr(target, "is_moving", False) or target.state in ("WALK", "RUN", "ROLL", "DASH", "SHUKUCHI")
                        target.stun(0.24)  # Atordoamento tático calibrado!
                        if is_target_moving:
                            hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=1)
                            camera.add_shake(6.0)
                            for _ in range(12):
                                particles.append(BloodParticle(target.wx, target.wy, 0.5))
                            if dead:
                                winner = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                                self._play_sound("fatal_strike")
                                if cinematic_director:
                                    death_style = _get_death_style_for_attacker(proj.owner, weapon="shuriken")
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))
                        else:
                            camera.add_shake(4.0)
                            banners.append(FloatingBanner("STUNNED!", target.wx, target.wy, wz=1.7, color=(200, 220, 255)))
                            for _ in range(8):
                                particles.append(SparkParticle(target.wx, target.wy, 0.6))
                        self._play_sound("obstacle_hit")
                    proj.is_active = False


            # Se for BOMBA NORMAL EM ARCO (TimedBombEntity)
            elif isinstance(proj, TimedBombEntity):
                # Detona por término do pavio ou por contato com combatentes (evitando colisão aérea imediata com o lançador)
                target = p2 if proj.owner == p1 else p1
                owner = proj.owner
                target_touch = target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.65 + target.radius)
                owner_touch = (not proj.is_airborne) and (proj.fuse_timer < 0.9) and world_distance(proj.wx, proj.wy, owner.wx, owner.wy) < (0.65 + owner.radius)
                should_detonate = (proj.fuse_timer <= 0) or target_touch or owner_touch

                if should_detonate:
                    proj.is_active = False
                    camera.add_shake(18.0)
                    banners.append(FloatingBanner("BOOM! - BOMB DETONATION!", proj.wx, proj.wy, wz=1.8, color=(255, 140, 20)))
                    self._play_sound("bomb_explode")
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.9, 0.7, 280)
                        ctrl_mgr.rumble_player(1, 0.9, 0.7, 280)

                    # Efeito de fogo e cinzas em área
                    for _ in range(30):
                        particles.append(SparkParticle(proj.wx, proj.wy, 0.5))

                    # A explosão acende props interativos (barris de pólvora)
                    for prop in getattr(game_map, "interactives", ()):
                        prop.ignite(proj.wx, proj.wy, proj.explosion_radius)

                    # Destruir bambus ao redor
                    for b in game_map.bamboos:
                        if not b.is_cut and world_distance(proj.wx, proj.wy, b.wx, b.wy) < proj.explosion_radius:
                            slice_part = b.cut((1.0, 0.0))
                            if slice_part:
                                particles.append(slice_part)

                    # Dano em área (com 50% de redução de dano para Kasumi contra sua própria bomba)
                    for dog_cand in [getattr(p1, "dog", None), getattr(p2, "dog", None)]:
                        if dog_cand and dog_cand.state != "KNOCKED_OUT" and world_distance(proj.wx, proj.wy, dog_cand.wx, dog_cand.wy) < proj.explosion_radius:
                            dog_cand.knock_out(2.0)
                            banners.append(FloatingBanner("DOG STUNNED! (2.0s)", dog_cand.wx, dog_cand.wy, wz=1.4, color=(255, 80, 80)))

                    p1_in_range = p1.is_alive and world_distance(proj.wx, proj.wy, p1.wx, p1.wy) < proj.explosion_radius
                    p2_in_range = p2.is_alive and world_distance(proj.wx, proj.wy, p2.wx, p2.wy) < proj.explosion_radius

                    # Entregável 4.3: Imunidade a auto-dano para Kasumi se estiver com <= 1 HP
                    p1_dmg = 0 if (proj.owner == p1 and getattr(p1, "char_type", "") == "kasumi" and p1.hp <= 1) else (1 if (proj.owner == p1 and getattr(p1, "char_type", "") == "kasumi") else 2)
                    p2_dmg = 0 if (proj.owner == p2 and getattr(p2, "char_type", "") == "kasumi" and p2.hp <= 1) else (1 if (proj.owner == p2 and getattr(p2, "char_type", "") == "kasumi") else 2)

                    p1_dead = False
                    p2_dead = False

                    if p1_in_range:
                        if p1_dmg > 0:
                            _, p1_dead = p1.take_hit((0, 0), damage=p1_dmg)
                            for _ in range(25 if p1_dead else 10):
                                particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                            if p1_dead and cinematic_director:
                                cinematic_director.trigger_fatal_strike(proj.owner, p1, "KASUMI_EXPLODE", (0, 0))
                        else:
                            p1.stun(0.20)
                            camera.add_shake(5.0)

                    if p2_in_range:
                        if p2_dmg > 0:
                            _, p2_dead = p2.take_hit((0, 0), damage=p2_dmg)
                            for _ in range(25 if p2_dead else 10):
                                particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                            if p2_dead and cinematic_director:
                                cinematic_director.trigger_fatal_strike(proj.owner, p2, "KASUMI_EXPLODE", (0, 0))
                        else:
                            p2.stun(0.20)
                            camera.add_shake(5.0)

                    if p1_dead or p2_dead:
                        self._play_sound("fatal_strike")

                    if p1_dead and p2_dead:
                        winner = "DRAW"
                    elif p1_dead:
                        # Se p2 já estiver morto (ex: abatido por kunai antes) ou se P1 já tinha vencido, resulta em Double KO (DRAW)
                        if (not p2.is_alive) or (winner == "P1_WINS"):
                            winner = "DRAW"
                        else:
                            winner = "P2_WINS"
                    elif p2_dead:
                        # Se p1 já estiver morto ou se P2 já tinha vencido, resulta em Double KO (DRAW)
                        if (not p1.is_alive) or (winner == "P2_WINS"):
                            winner = "DRAW"
                        else:
                            winner = "P1_WINS"

            # Se for TIRO DE MOSQUETE (MusketBulletProjectile)
            elif isinstance(proj, MusketBulletProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.55 + target.radius):
                    # Respeita invulnerabilidade do dodge (Cape Flourish, Roll, Shukuchi, etc.)
                    target_in_dodge = (
                        target.state in ("ROLL", "CAPE_FLOURISH", "SHUKUCHI", "KAWARIMI_ROLL", "DODGE")
                        and getattr(target, "is_invulnerable_dodge", False)
                    )
                    if target_in_dodge:
                        pass  # Bala passa através sem detonar (o dodge garante i-frames totais)
                    else:
                        if target.state == STATE_PARRY:
                            # Musashi pode refletir projéteis durante os primeiros 0.15s da parry
                            if (target.__class__.__name__ == "BlueSamurai" and 
                                getattr(target, "parry_reflect_active_timer", 0) > 0 and 
                                not getattr(proj, "has_been_reflected", False)):
                                # REFLETE: inverte direção e muda dono
                                proj.vx = -proj.vx
                                proj.vy = -proj.vy
                                proj.dir_x = -proj.dir_x
                                proj.dir_y = -proj.dir_y
                                proj.owner = target
                                proj.has_been_reflected = True
                                proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                                banners.append(FloatingBanner("PARRY REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                                camera.add_shake(6.0)
                                self._play_sound("parry")
                            else:
                                # Absorção normal de parry
                                proj.is_active = False
                                banners.append(FloatingBanner("PARRY BULLET!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                                for _ in range(14):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.7))
                                self._play_sound("parry")
                        else:
                            proj.is_active = False
                            hit, dead = target.take_hit((proj.vx, proj.vy), damage=2)
                            if dead:
                                camera.add_shake(16.0)
                                owner_type = getattr(proj.owner, "char_type", "")
                                if owner_type in ("musketeer", "julie"):
                                    banner_text = "POCKET FLINTLOCK SNIPE!"
                                    banner_color = (255, 215, 70)
                                else:
                                    banner_text = "TANEGASHIMA HEADSHOT!"
                                    banner_color = (255, 180, 50)
                                banners.append(FloatingBanner(banner_text, target.wx, target.wy, wz=1.8, color=banner_color))
                                for _ in range(30):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.6))
                                self.hitstop_timer = 0.14
                                winner = winner_id
                                self._play_sound("fatal_strike")
                                if cinematic_director:
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, "HEADSHOT_EXPLODE", (proj.vx, proj.vy))

            # Se for NUVEM DE VENENO (PoisonCloudProjectile)
            elif isinstance(proj, PoisonCloudProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (proj.radius + target.radius):
                    if not getattr(target, "is_poisoned", False):
                        proj.is_active = False
                        target.is_poisoned = True
                        target.poison_timer = 6.0
                        target.speed *= 1.08  # Leve boost de adrenalina sem torná-lo invencível
                        if hasattr(proj.owner, "on_poison_inflicted"):
                            proj.owner.on_poison_inflicted(target)
                        camera.add_shake(7.0)
                        banners.append(FloatingBanner("POISONED! 6s TO SURVIVE!", target.wx, target.wy, wz=1.8, color=(80, 225, 120), duration=2.5))
                        for _ in range(16):
                            particles.append(SparkParticle(target.wx, target.wy, 0.5))
                        self._play_sound("poison_breath")

            # Se for FLECHA DE KYUDO (KyudoArrowProjectile)
            elif isinstance(proj, KyudoArrowProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.50 + target.radius):
                    if target.state == STATE_PARRY:
                        # Musashi pode refletir projéteis durante os primeiros 0.15s da parry
                        if (target.__class__.__name__ == "BlueSamurai" and 
                            getattr(target, "parry_reflect_active_timer", 0) > 0 and 
                            not getattr(proj, "has_been_reflected", False)):
                            # REFLETE: inverte direção e muda dono
                            proj.vx = -proj.vx
                            proj.vy = -proj.vy
                            proj.dir_x = -proj.dir_x
                            proj.dir_y = -proj.dir_y
                            proj.owner = target
                            proj.has_been_reflected = True
                            proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                            banners.append(FloatingBanner("PARRY REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                            camera.add_shake(6.0)
                            self._play_sound("parry")
                        else:
                            # Absorção normal de parry
                            proj.is_active = False
                            banners.append(FloatingBanner("PARRY ARROW!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                            for _ in range(10):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                            self._play_sound("parry")
                    else:
                        proj.is_active = False
                        hit, dead = target.take_hit((proj.vx, proj.vy), damage=2)
                        if dead:
                            camera.add_shake(15.0)
                            banners.append(FloatingBanner("YUMI HEART SHOT!", target.wx, target.wy, wz=1.8, color=(100, 220, 140)))
                            for _ in range(25):
                                particles.append(BloodParticle(target.wx, target.wy, 0.6))
                            self.hitstop_timer = 0.12
                            winner = winner_id
                            self._play_sound("fatal_strike")
                            if cinematic_director:
                                cinematic_director.trigger_fatal_strike(proj.owner, target, "ARROW_PIN", (proj.vx, proj.vy))

            # Se for FLECHA SAGRADA DE KYUDO (HamayaArrowProjectile)
            elif isinstance(proj, HamayaArrowProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.55 + target.radius):
                    # Projétil sagrado perfurante: quebra parry ou atinge letalmente
                    proj.is_active = False
                    hit, dead = target.take_hit((proj.vx, proj.vy), damage=2)
                    if dead:
                        camera.add_shake(16.0)
                        banners.append(FloatingBanner("HAMAYA PURIFICATION!", target.wx, target.wy, wz=1.8, color=(255, 225, 90)))
                        for _ in range(30):
                            particles.append(BloodParticle(target.wx, target.wy, 0.6))
                        for _ in range(16):
                            particles.append(SparkParticle(target.wx, target.wy, 0.6, color=(255, 230, 100)))
                        self.hitstop_timer = 0.14
                        winner = winner_id
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(proj.owner, target, "ARROW_PIN", (proj.vx, proj.vy))

            # Se for BOMBA DE FUMAÇA (SmokeCloudEntity)
            elif isinstance(proj, SmokeCloudEntity) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                if target.is_alive and proj.is_inside(target.wx, target.wy):
                    target.apply_slow(2.5)  # Reduz velocidade em 65%!

            # Se for CORRENTE DE KUSARIGAMA (KusarigamaChainEntity)
            elif isinstance(proj, KusarigamaChainEntity) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                if proj.state == "FLYING" and target.is_alive:
                    if world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.55 + target.radius):
                        if target.state == STATE_PARRY:
                            for _ in range(10):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                            banners.append(FloatingBanner("PARRY CHAIN!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                            camera.add_shake(5.0)
                            proj.state = "RETRACTING"
                            self._play_sound("parry")
                        else:
                            proj.state = "HOOKED_PULLING"
                            proj.target = target
                            target.stun(0.35)
                            # Entregável 4.2: Dano de 1 HP no impacto do hook
                            hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=1)
                            camera.add_shake(6.0)
                            for _ in range(12):
                                particles.append(BloodParticle(target.wx, target.wy, 0.4))
                            self._play_sound("chain_whip")
                            if dead:
                                winner = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                                self._play_sound("fatal_strike")
                                if cinematic_director:
                                    death_style = _get_death_style_for_attacker(proj.owner)
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))

            # Se for ONDA DO MUSASHI (MusashiWaveProjectile)
            elif isinstance(proj, MusashiWaveProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.45 + target.radius + 0.75):  # Onda é maior
                    # Onda pode ser refletida durante parry
                    if target.state == STATE_PARRY:
                        if (target.__class__.__name__ == "BlueSamurai" and 
                            getattr(target, "parry_reflect_active_timer", 0) > 0 and 
                            not getattr(proj, "has_been_reflected", False)):
                            # REFLETE: inverte direção e muda dono
                            proj.vx = -proj.vx
                            proj.vy = -proj.vy
                            proj.dir_x = -proj.dir_x
                            proj.dir_y = -proj.dir_y
                            proj.owner = target
                            proj.has_been_reflected = True
                            proj.dist_traveled = 0
                            banners.append(FloatingBanner("PARRY REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                            camera.add_shake(6.0)
                            self._play_sound("parry")
                        else:
                            # Absorção normal de parry
                            for _ in range(12):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                            banners.append(FloatingBanner("PARRY WAVE!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                            camera.add_shake(5.0)
                            self._play_sound("parry")
                            proj.is_active = False
                    else:
                        # Onda causa 2 danos
                        hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=2)
                        if dead:
                            camera.add_shake(15.0)
                            banners.append(FloatingBanner("MUSASHI WAVE - 1 HIT KILL!", target.wx, target.wy, wz=1.8, color=(100, 200, 255)))
                            for _ in range(25):
                                particles.append(BloodParticle(target.wx, target.wy, 0.6))
                            self.hitstop_timer = 0.12
                            winner = winner_id
                            self._play_sound("fatal_strike")
                            if cinematic_director:
                                death_style = _get_death_style_for_attacker(proj.owner)
                                cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))
                        else:
                            camera.add_shake(8.0)
                            for _ in range(15):
                                particles.append(SparkParticle(target.wx, target.wy, 0.5))
                            self._play_sound("obstacle_hit")
                        proj.is_active = False

            # Se for BALA DE CANHÃO NAVAL (CannonballProjectile)
            elif isinstance(proj, CannonballProjectile) and proj.is_active:
                if proj.has_exploded:
                    self._play_sound("cannon_fire")
                    # Explodir e atingir adversários no solo
                    for target, win_id in ((p1, "P2_WINS"), (p2, "P1_WINS")):
                        if target.is_alive and target != proj.owner:
                            if world_distance(proj.wx, proj.wy, target.wx, target.wy) < (proj.radius + target.radius):
                                hit, dead = target.take_hit((0, 0), damage=2)
                                if dead:
                                    camera.add_shake(20.0)
                                    banners.append(FloatingBanner("NAVAL CANNON FATALITY!", target.wx, target.wy, wz=2.0, color=(255, 120, 30)))
                                    for _ in range(35):
                                        particles.append(BloodParticle(target.wx, target.wy, 0.7))
                                    self.hitstop_timer = 0.16
                                    if winner is None:
                                        winner = win_id
                                    self._play_sound("fatal_strike")
                                    if cinematic_director:
                                        cinematic_director.trigger_fatal_strike(proj.owner, target, "KASUMI_EXPLODE", (0, 0))



            if proj.is_active:
                active_projectiles.append(proj)

        projectiles.clear()
        projectiles.extend(active_projectiles)

        # Atualizar cronômetro de veneno dos combatentes
        for fighter, other_id in ((p1, "P2_WINS"), (p2, "P1_WINS")):
            if fighter.is_alive and getattr(fighter, "is_poisoned", False):
                fighter.poison_timer -= dt
                # Oponente envenenado ganha adrenalina: cooldowns 20% menores (recuperam 25% mais rápido)
                bonus_dt = dt * 0.25
                for cd_attr in (
                    "ryuu_timer", "dash_recovery_timer", "jump_timer", "jump_cooldown_timer",
                    "chain_timer", "mine_timer", "bomb_timer", "smoke_timer", "rope_timer",
                    "arrow_cooldown_timer", "ofuda_cooldown_timer", "cannon_cooldown_timer",
                    "flintlock_timer", "cape_timer", "trap_timer", "zeroshiki_timer",
                    "shuriken_timer", "thrust_timer", "kama_timer", "backstep_timer", "cleave_timer"
                ):
                    val = getattr(fighter, cd_attr, 0.0)
                    if val > 0:
                        setattr(fighter, cd_attr, max(0.0, val - bonus_dt))
                if hasattr(fighter, "dog") and fighter.dog and getattr(fighter.dog, "cooldown_timer", 0.0) > 0:
                    fighter.dog.cooldown_timer = max(0.0, fighter.dog.cooldown_timer - bonus_dt)

                if fighter.poison_timer <= 0:
                    fighter.is_poisoned = False
                    _, poison_dead = fighter.take_hit((0, 0), damage=2)
                    if poison_dead:
                        banners.append(FloatingBanner("POISON DEATH!", fighter.wx, fighter.wy, wz=1.8, color=(80, 225, 120)))
                        for _ in range(30):
                            particles.append(BloodParticle(fighter.wx, fighter.wy, 0.6))
                        if winner is None:
                            winner = other_id
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(None, fighter, "OKUNI_MELT", (0, 0))
                    else:
                        for _ in range(10):
                            particles.append(BloodParticle(fighter.wx, fighter.wy, 0.6))

        # -------------------------------------------------------------
        # 2. COMBATE DO CÃO DOBERMAN (SE HOUVER AMERICAN NINJA)
        # -------------------------------------------------------------
        # Cão do Jogador 1 contra Jogador 2 (Item 23)
        if hasattr(p1, "dog") and p1.dog and p1.dog.state != STATE_DOG_KNOCKED_OUT:
            dog = p1.dog
            # Item 6: O cão só pode ser golpeado/atordoado se estiver atacando (BARK ou CHARGE)!
            if dog.state in (STATE_DOG_CHARGE, STATE_DOG_BARK) and p2.is_alive and p2.hitbox_active and world_distance(p2.hitbox_center[0], p2.hitbox_center[1], dog.wx, dog.wy) < (p2.hitbox_radius + dog.radius):
                dog.knock_out(2.0)
                for _ in range(12):
                    particles.append(SparkParticle(dog.wx, dog.wy, 0.4))
                camera.add_shake(6.0)
                banners.append(FloatingBanner("DOG STUNNED! (2.0s)", dog.wx, dog.wy, wz=1.4, color=(255, 80, 80)))
                if ctrl_mgr:
                    ctrl_mgr.rumble_player(0, 0.5, 0.7, 200)
            elif dog.state == STATE_DOG_CHARGE and p2.is_alive and world_distance(dog.wx, dog.wy, p2.wx, p2.wy) < (dog.hitbox_radius + p2.radius):
                # O cão atingiu o oponente!
                if p2.state == STATE_PARRY:
                    dog.knock_out(2.0)
                    camera.add_shake(7.0)
                    banners.append(FloatingBanner("PARRY DOG!", p2.wx, p2.wy, wz=1.7, color=(100, 200, 255)))
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.5, 0.7, 200)
                        ctrl_mgr.rumble_player(1, 0.6, 0.8, 180)
                else:
                    # MORTE FATAL PELO DOBERMAN!
                    hit, dead = p2.take_hit((dog.facing_x, dog.facing_y), damage=2)
                    if dead:
                        camera.add_shake(16.0)
                        banners.append(FloatingBanner("DOBERMAN BITE - FATAL!", p2.wx, p2.wy, wz=1.8, color=(255, 45, 45)))
                        for _ in range(30):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        self.hitstop_timer = 0.14
                        winner = "P1_WINS"
                        dog.state = "FOLLOW"
                        dog.hitbox_active = False
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p1, p2, "MAULED", (dog.facing_x, dog.facing_y))
                        if ctrl_mgr:
                            ctrl_mgr.rumble_player(0, 0.8, 1.0, 320)
                            ctrl_mgr.rumble_player(1, 1.0, 1.0, 400)

        # Cão do Jogador 2 contra Jogador 1 (Item 23)
        if hasattr(p2, "dog") and p2.dog and p2.dog.state != STATE_DOG_KNOCKED_OUT and winner is None:
            dog = p2.dog
            # Item 6: O cão só pode ser golpeado/atordoado se estiver atacando (BARK ou CHARGE)!
            if dog.state in (STATE_DOG_CHARGE, STATE_DOG_BARK) and p1.is_alive and p1.hitbox_active and world_distance(p1.hitbox_center[0], p1.hitbox_center[1], dog.wx, dog.wy) < (p1.hitbox_radius + dog.radius):
                dog.knock_out(2.0)
                for _ in range(12):
                    particles.append(SparkParticle(dog.wx, dog.wy, 0.4))
                camera.add_shake(6.0)
                banners.append(FloatingBanner("DOG STUNNED! (2.0s)", dog.wx, dog.wy, wz=1.4, color=(255, 80, 80)))
                if ctrl_mgr:
                    ctrl_mgr.rumble_player(1, 0.5, 0.7, 200)
            elif dog.state == STATE_DOG_CHARGE and p1.is_alive and world_distance(dog.wx, dog.wy, p1.wx, p1.wy) < (dog.hitbox_radius + p1.radius):
                if p1.state == STATE_PARRY:
                    dog.knock_out(2.0)
                    camera.add_shake(7.0)
                    banners.append(FloatingBanner("PARRY DOG!", p1.wx, p1.wy, wz=1.7, color=(100, 200, 255)))
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(1, 0.5, 0.7, 200)
                        ctrl_mgr.rumble_player(0, 0.6, 0.8, 180)
                else:
                    hit, dead = p1.take_hit((dog.facing_x, dog.facing_y), damage=2)
                    if dead:
                        camera.add_shake(16.0)
                        banners.append(FloatingBanner("DOBERMAN BITE - FATAL!", p1.wx, p1.wy, wz=1.8, color=(255, 45, 45)))
                        for _ in range(30):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        self.hitstop_timer = 0.14
                        winner = "P2_WINS"
                        dog.state = "FOLLOW"
                        dog.hitbox_active = False
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p2, p1, "MAULED", (dog.facing_x, dog.facing_y))
                        if ctrl_mgr:
                            ctrl_mgr.rumble_player(1, 0.8, 1.0, 320)
                            ctrl_mgr.rumble_player(0, 1.0, 1.0, 400)

        # -------------------------------------------------------------
        # 3. CORTE DE BAMBUS E FAÍSCAS EM ROCHAS
        # -------------------------------------------------------------
        self._check_bamboo_cuts(p1, game_map, particles)
        self._check_bamboo_cuts(p2, game_map, particles)
        self._check_obstacle_sparks(p1, game_map, particles, camera, ctrl_mgr, p_idx=0)
        self._check_obstacle_sparks(p2, game_map, particles, camera, ctrl_mgr, p_idx=1)
        if getattr(game_map, "interactives", None):
            self._check_interactives(p1, p2, game_map, projectiles)

        if not p1.is_alive or not p2.is_alive:
            return winner

        # -------------------------------------------------------------
        # 4. CHOQUE SIMULTÂNEO DE ATAQUES (CLASH & PRECEDÊNCIA ABSOLUTA)
        # -------------------------------------------------------------
        if p1.hitbox_active and p2.hitbox_active:
            hx1, hy1 = p1.hitbox_center
            hx2, hy2 = p2.hitbox_center
            if world_distance(hx1, hy1, hx2, hy2) < (p1.hitbox_radius + p2.hitbox_radius) * 0.7:
                p1_priority = getattr(p1, "is_priority_strike", False)
                p2_priority = getattr(p2, "is_priority_strike", False)

                # PRECEDÊNCIA ABSOLUTA: Foice curta do Ninja Roxo ganha de qualquer outro ataque!
                if p1_priority and not p2_priority:
                    # P1 tem precedência absoluta! Cancela ataque do P2 e desfere golpe fatal
                    p2.hitbox_active = False
                    hit, dead = p2.take_hit(p1.slash_dir, damage=2)
                    camera.add_shake(16.0)
                    banners.append(FloatingBanner("PRECEDÊNCIA ABSOLUTA! (FOICE)", p2.wx, p2.wy, wz=1.8, color=(220, 140, 255)))
                    for _ in range(25):
                        particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                    self.hitstop_timer = 0.14
                    self._play_sound("fatal_strike")
                    if cinematic_director:
                        cinematic_director.trigger_fatal_strike(p1, p2, "MURASAKI_DECAP", p1.slash_dir)
                    return "P1_WINS"

                elif p2_priority and not p1_priority:
                    # P2 tem precedência absoluta! Cancela ataque do P1 e desfere golpe fatal
                    p1.hitbox_active = False
                    hit, dead = p1.take_hit(p2.slash_dir, damage=2)
                    camera.add_shake(16.0)
                    banners.append(FloatingBanner("PRECEDÊNCIA ABSOLUTA! (FOICE)", p1.wx, p1.wy, wz=1.8, color=(220, 140, 255)))
                    for _ in range(25):
                        particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                    self.hitstop_timer = 0.14
                    self._play_sound("fatal_strike")
                    if cinematic_director:
                        cinematic_director.trigger_fatal_strike(p2, p1, "MURASAKI_DECAP", p2.slash_dir)
                    return "P2_WINS"

                else:
                    # Ambos têm mesma prioridade -> Choque de Lâminas (CLASH!)
                    mid_x = (hx1 + hx2) / 2
                    mid_y = (hy1 + hy2) / 2

                    if clash_system is not None:
                        # Fase 5.1: Clash de Espadas Tsubazeriai (QTE "STRIKE!")
                        p1.hitbox_active = False
                        p2.hitbox_active = False
                        clash_system.trigger(p1, p2, mid_x, mid_y, camera=camera, particles=particles, banners=banners, ctrl_mgr=ctrl_mgr)
                        return None

                    # Comportamento legado (sem ClashSystem): atordoamento mútuo simples
                    for _ in range(15):
                        particles.append(SparkParticle(mid_x, mid_y, 0.6))
                    banners.append(FloatingBanner("CLASH!", mid_x, mid_y, wz=1.6, color=(255, 230, 80)))
                    camera.add_shake(7.0)
                    p1.stun(0.4)
                    p2.stun(0.4)
                    self._play_sound("sword_clash")
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.6, 0.8, 180)
                        ctrl_mgr.rumble_player(1, 0.6, 0.8, 180)
                    return None


        # -------------------------------------------------------------
        # 5. ATAQUE MELEE: P1 CONTRA DECOYS OU P2
        # -------------------------------------------------------------
        if p1.hitbox_active and decoys:
            hx, hy = p1.hitbox_center
            for decoy in decoys:
                if decoy.is_active and getattr(decoy, "owner", None) != p1:
                    if world_distance(hx, hy, decoy.wx, decoy.wy) < (p1.hitbox_radius + decoy.radius):
                        p1.hitbox_active = False
                        decoy.on_hit(p1, particles, banners, camera)
                        break

        if p1.hitbox_active and p2.is_alive:
            hx, hy = p1.hitbox_center
            if world_distance(hx, hy, p2.wx, p2.wy) < (p1.hitbox_radius + p2.radius) and getattr(p2, "wz", 0.0) < 0.65:
                p1.hitbox_active = False

                if p2.state == STATE_PARRY:
                    for _ in range(12):
                        particles.append(SparkParticle(p2.wx, p2.wy, 0.7))
                    parry_msg = "PARRY GATOTSU!" if p1.state == "GATOTSU_CHARGE" else "PARRY!"
                    banners.append(FloatingBanner(parry_msg, p2.wx, p2.wy, wz=1.7, color=(100, 200, 255)))
                    camera.add_shake(8.0)
                    p1.stun(0.85)
                    self._play_sound("parry")
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.5, 0.8, 200)
                        ctrl_mgr.rumble_player(1, 0.6, 0.8, 180)
                elif getattr(p1, "is_rifle_butt", False):
                    # Coronhada agressiva do Teppo: causa 1 de dano, afasta 1.6m e atordoa o adversário
                    hit, dead = p2.take_hit(p1.slash_dir, damage=1)
                    p2.stun(0.50)
                    p2.wx = max(1.0, min(game_map.cols - 1.0, p2.wx + p1.facing_x * 1.6))
                    p2.wy = max(1.0, min(game_map.rows - 1.0, p2.wy + p1.facing_y * 1.6))
                    camera.add_shake(8.0)
                    for _ in range(12):
                        particles.append(SparkParticle(p2.wx, p2.wy, 0.5))
                    self._play_sound("obstacle_hit")
                    if dead:
                        winner = "P1_WINS"
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p1, p2, "BLUNT_FALL", p1.slash_dir)
                else:
                    is_ninja = (getattr(p1, "char_type", "") == "ninja" or hasattr(p1, "has_kunai"))
                    kill_label = None
                    if is_ninja:
                        # 1-Hit Kill em Contra-Ataque (adversário em recovery/stunned) ou Costas (backstab)
                        dot_facing = p1.facing_x * p2.facing_x + p1.facing_y * p2.facing_y
                        is_backstab = (dot_facing > 0.20)
                        is_punish = (p2.state in (STATE_RECOVERY, STATE_STUNNED))
                        if is_backstab or is_punish:
                            damage = 2
                            kill_label = "BACKSTAB - 1 HIT KILL!" if is_backstab else "PUNISH - 1 HIT KILL!"
                        else:
                            damage = 1
                    else:
                        damage = 2

                    hit, dead = p2.take_hit(p1.slash_dir, damage=damage)
                    if dead or hit:
                        if hasattr(p1, "on_hit_success"):
                            p1.on_hit_success()
                    if dead:
                        camera.add_shake(14.0)
                        if kill_label:
                            kill_msg = kill_label
                        elif p1.state == "GATOTSU_CHARGE":
                            kill_msg = "GATOTSU - 1 HIT KILL!"
                        else:
                            kill_msg = "FATAL STRIKE!"
                        banners.append(FloatingBanner(kill_msg, p2.wx, p2.wy, wz=1.8, color=(255, 220, 50) if kill_label else ((120, 210, 255) if p1.state == "GATOTSU_CHARGE" else (255, 60, 60))))
                        for _ in range(25):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        self.hitstop_timer = 0.12
                        winner = "P1_WINS"
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            death_style = _get_death_style_for_attacker(p1)
                            cinematic_director.trigger_fatal_strike(p1, p2, death_style, p1.slash_dir)
                    elif hit:
                        camera.add_shake(7.0)
                        for _ in range(12):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        self._play_sound("sword_slash")
                        self._apply_hit_knockback(p1, p2, game_map)


        # -------------------------------------------------------------
        # 6. ATAQUE MELEE: P2 CONTRA DECOYS OU P1
        # -------------------------------------------------------------
        if p2.hitbox_active and decoys:
            hx, hy = p2.hitbox_center
            for decoy in decoys:
                if decoy.is_active and getattr(decoy, "owner", None) != p2:
                    if world_distance(hx, hy, decoy.wx, decoy.wy) < (p2.hitbox_radius + decoy.radius):
                        p2.hitbox_active = False
                        decoy.on_hit(p2, particles, banners, camera)
                        break

        if p2.hitbox_active and p1.is_alive and winner is None:
            hx, hy = p2.hitbox_center
            if world_distance(hx, hy, p1.wx, p1.wy) < (p2.hitbox_radius + p1.radius) and getattr(p1, "wz", 0.0) < 0.65:
                p2.hitbox_active = False

                if p1.state == STATE_PARRY:
                    for _ in range(12):
                        particles.append(SparkParticle(p1.wx, p1.wy, 0.7))
                    parry_msg = "PARRY GATOTSU!" if p2.state == "GATOTSU_CHARGE" else "PARRY!"
                    banners.append(FloatingBanner(parry_msg, p1.wx, p1.wy, wz=1.7, color=(100, 200, 255)))
                    camera.add_shake(8.0)
                    p2.stun(0.85)
                    self._play_sound("parry")
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(1, 0.5, 0.8, 200)
                        ctrl_mgr.rumble_player(0, 0.6, 0.8, 180)
                elif getattr(p2, "is_rifle_butt", False):
                    # Coronhada agressiva do Teppo: causa 1 de dano, afasta 1.6m e atordoa o adversário
                    hit, dead = p1.take_hit(p2.slash_dir, damage=1)
                    p1.stun(0.50)
                    p1.wx = max(1.0, min(game_map.cols - 1.0, p1.wx + p2.facing_x * 1.6))
                    p1.wy = max(1.0, min(game_map.rows - 1.0, p1.wy + p2.facing_y * 1.6))
                    camera.add_shake(8.0)
                    for _ in range(12):
                        particles.append(SparkParticle(p1.wx, p1.wy, 0.5))
                    self._play_sound("obstacle_hit")
                    if dead:
                        winner = "P2_WINS"
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p2, p1, "BLUNT_FALL", p2.slash_dir)
                else:
                    is_ninja = getattr(p2, "char_type", "") == "ninja"
                    kill_label = None
                    if is_ninja:
                        dot_facing = p2.facing_x * p1.facing_x + p2.facing_y * p1.facing_y
                        is_backstab = (dot_facing > 0.20)
                        is_punish = (p1.state in (STATE_RECOVERY, STATE_STUNNED))
                        if is_backstab or is_punish:
                            damage = 2
                            kill_label = "BACKSTAB - 1 HIT KILL!" if is_backstab else "PUNISH - 1 HIT KILL!"
                        else:
                            damage = 1
                    else:
                        damage = 2

                    hit, dead = p1.take_hit(p2.slash_dir, damage=damage)
                    if dead or hit:
                        if hasattr(p2, "on_hit_success"):
                            p2.on_hit_success()
                    if dead:
                        camera.add_shake(14.0)
                        if kill_label:
                            kill_msg = kill_label
                        elif p2.state == "GATOTSU_CHARGE":
                            kill_msg = "GATOTSU - 1 HIT KILL!"
                        else:
                            kill_msg = "FATAL STRIKE!"
                        banners.append(FloatingBanner(kill_msg, p1.wx, p1.wy, wz=1.8, color=(255, 220, 50) if kill_label else ((120, 210, 255) if p2.state == "GATOTSU_CHARGE" else (70, 150, 255))))
                        for _ in range(25):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        self.hitstop_timer = 0.12
                        winner = "P2_WINS"
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            death_style = _get_death_style_for_attacker(p2)
                            cinematic_director.trigger_fatal_strike(p2, p1, death_style, p2.slash_dir)
                    elif hit:
                        camera.add_shake(7.0)
                        for _ in range(12):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        self._play_sound("sword_slash")
                        self._apply_hit_knockback(p2, p1, game_map)


        # -------------------------------------------------------------
        # 7. ATUALIZAR E REMOVER DECOYS EXPIRADOS
        # -------------------------------------------------------------
        if decoys:
            for d in decoys:
                d.update(dt)
            decoys[:] = [d for d in decoys if d.is_active]

        return winner

    @staticmethod
    def _check_interactives(p1, p2, game_map, projectiles: list):
        """Golpes e projéteis em voo acendem os props interativos da arena (ex.: pavio do canhão)."""
        for prop in game_map.interactives:
            for fighter in (p1, p2):
                if fighter.is_alive and fighter.hitbox_active:
                    prop.ignite(*fighter.hitbox_center, fighter.hitbox_radius)
            for proj in projectiles:
                if getattr(proj, "is_active", True) and hasattr(proj, "dir_x") and hasattr(proj, "wx"):
                    prop.ignite(proj.wx, proj.wy, 0.25)

    def _check_bamboo_cuts(self, fighter, game_map, particles: list):
        if not fighter.hitbox_active:
            return
        hx, hy = fighter.hitbox_center
        hradius = fighter.hitbox_radius

        for bamboo in game_map.bamboos:
            if not bamboo.is_cut:
                if world_distance(hx, hy, bamboo.wx, bamboo.wy) < (hradius + bamboo.radius):
                    slice_part = bamboo.cut(fighter.slash_dir)
                    if slice_part:
                        particles.append(slice_part)
                        for _ in range(5):
                            particles.append(SparkParticle(bamboo.wx, bamboo.wy, bamboo.stump_height))
                        self._play_sound("sword_slash")

    def _check_obstacle_sparks(self, fighter, game_map, particles: list, camera, ctrl_mgr = None, p_idx: int = 0):
        if not fighter.hitbox_active:
            return
        # Não gera faíscas nem hitstop de obstáculos terrestres se o lutador estiver no ar (ex: descendo no Ryuu Tsui Sen)
        if getattr(fighter, "wz", 0.0) > 0.40:
            return
        # Cooldown para evitar múltiplos hitstops consecutivos no mesmo golpe contra o mesmo obstáculo sólido
        if getattr(fighter, "obstacle_spark_timer", 0.0) > 0:
            return

        hx, hy = fighter.hitbox_center
        hradius = fighter.hitbox_radius * 0.75
        hit_solid = False

        # 1. Rochas da arena
        for rock in getattr(game_map, "rocks", []):
            if world_distance(hx, hy, rock.wx, rock.wy) < (hradius + getattr(rock, "radius", 0.65)):
                hit_solid = True
                break

        # 2. Lavatório Tsukubai / Poço
        if not hit_solid and getattr(game_map, "well", None):
            if world_distance(hx, hy, game_map.well.wx, game_map.well.wy) < (hradius + getattr(game_map.well, "radius", 0.70)):
                hit_solid = True

        # 3. Lanternas Ishi-doro (Kyoto e Bamboo Forest)
        if not hit_solid:
            for lantern in getattr(game_map, "lanterns", []):
                if world_distance(hx, hy, lantern.wx, lantern.wy) < (hradius + 0.45):
                    hit_solid = True
                    break

        # 4. Carruagens em disparada (Kyoto)
        if not hit_solid:
            for carriage in getattr(game_map, "carriages", []):
                if carriage.is_active and carriage.warning_timer <= 0:
                    if world_distance(hx, hy, carriage.wx, carriage.wy) < (hradius + getattr(carriage, "hit_radius", 1.2)):
                        hit_solid = True
                        break

        # 5. Árvores e Pilares Torii
        if not hit_solid:
            for tree in getattr(game_map, "trees", []):
                if world_distance(hx, hy, tree.wx, tree.wy) < (hradius + getattr(tree, "radius", 0.60)):
                    hit_solid = True
                    break
            if not hit_solid:
                for torii in getattr(game_map, "torii_gates", []):
                    if world_distance(hx, hy, torii.wx, torii.wy) < (hradius + getattr(torii, "radius", 0.70)):
                        hit_solid = True
                        break

        if hit_solid:
            fighter.obstacle_spark_timer = 0.25  # Evita re-trigger durante o mesmo golpe
            for _ in range(4):
                particles.append(SparkParticle(hx, hy, 0.55))
            camera.add_shake(2.0)
            self.hitstop_timer = max(self.hitstop_timer, 0.035)
            self._play_sound("obstacle_hit")
            if ctrl_mgr:
                ctrl_mgr.rumble_player(p_idx, 0.30, 0.4, 70)


