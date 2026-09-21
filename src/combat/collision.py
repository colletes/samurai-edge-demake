"""
Gerenciador de regras de combate: lâminas, kunais, shurikens com stun,
botes letais do cão Doberman e contra-ataques que nocauteiam o cão.
"""
import math
from src.isometric.iso_math import world_distance
from src.effects.particles import (
    SparkParticle, BloodParticle, FloatingBanner
)
from src.entities.samurai import STATE_PARRY
from src.entities.projectile import (
    KunaiProjectile, ShurikenProjectile, TimedBombEntity, SmokeCloudEntity,
    KusarigamaChainEntity, MusketBulletProjectile, PoisonCloudProjectile,
    KyudoArrowProjectile, RopeArrowProjectile
)
from src.entities.doberman import STATE_DOG_CHARGE

def _get_death_style_for_attacker(attacker):
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
    elif "gray" in char_type or "kasumi" in char_type or "kemuri" in char_type:
        return "KASUMI_EXPLODE"
    elif "rifle" in char_type or "teppo" in char_type:
        return "HEADSHOT_EXPLODE"
    elif "kabuki" in char_type or "okuni" in char_type:
        return "MURASAKI_DECAP"
    return "KENSHIN_SPLIT"

class CombatSystem:
    def __init__(self):
        self.hitstop_timer = 0.0

    def process_combat(self, p1, p2, game_map, particles: list, banners: list, camera, projectiles: list, dt: float = 0.016, cinematic_director = None, decoys: list = None) -> str | None:
        """
        Processa interações de combate: corpo a corpo, projéteis e ataques de cães.
        Retorna 'P1_WINS', 'P2_WINS' ou None.
        """
        winner = None

        # -------------------------------------------------------------
        # 1. ATUALIZAR E PROCESSAR PROJÉTEIS (KUNAI, SHURIKEN, BALAS, FLECHAS, ETC.)
        # -------------------------------------------------------------
        # Deflexão de Projéteis pela Lâmina do Kenshin (Iai Flash ou Shukuchi)
        for k_fighter in (p1, p2):
            if getattr(k_fighter, "char_type", "") == "kenshin" and k_fighter.is_alive:
                if k_fighter.hitbox_active or k_fighter.state in ("ATTACK", "SHUKUCHI"):
                    kx = k_fighter.hitbox_center[0] if k_fighter.hitbox_active else k_fighter.wx
                    ky = k_fighter.hitbox_center[1] if k_fighter.hitbox_active else k_fighter.wy
                    kr = k_fighter.hitbox_radius if k_fighter.hitbox_active else 1.25
                    for proj in projectiles:
                        if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != k_fighter:
                            if world_distance(kx, ky, proj.wx, proj.wy) < (kr + 0.45):
                                proj.is_active = False
                                for _ in range(12):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                                banners.append(FloatingBanner("SLASH DEFLECTION!", proj.wx, proj.wy, wz=1.7, color=(255, 230, 80)))
                                camera.add_shake(5.0)

        active_projectiles = []
        for proj in projectiles:
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

            # Se for KUNAI em vôo
            if isinstance(proj, KunaiProjectile) and proj.state == "FLYING":
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"

                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.45 + target.radius):
                    if target.state == STATE_PARRY:
                        for _ in range(10):
                            particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                        banners.append(FloatingBanner("PARRY KUNAI!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                        camera.add_shake(5.0)
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
                            if cinematic_director:
                                death_style = _get_death_style_for_attacker(proj.owner)
                                cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))

            # Se for SHURIKEN (Não mata! Apenas aplica stun!)
            elif isinstance(proj, ShurikenProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1

                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.45 + target.radius):
                    if target.state == STATE_PARRY:
                        for _ in range(8):
                            particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                        banners.append(FloatingBanner("PARRY!", target.wx, target.wy, wz=1.6, color=(100, 200, 255)))
                    else:
                        target.stun(0.24)  # Atordoamento tático calibrado!
                        camera.add_shake(4.0)
                        banners.append(FloatingBanner("STUNNED!", target.wx, target.wy, wz=1.7, color=(200, 220, 255)))
                        for _ in range(8):
                            particles.append(SparkParticle(target.wx, target.wy, 0.6))
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

                    # Efeito de fogo e cinzas em área
                    for _ in range(30):
                        particles.append(SparkParticle(proj.wx, proj.wy, 0.5))

                    # Destruir bambus ao redor
                    for b in game_map.bamboos:
                        if not b.is_cut and world_distance(proj.wx, proj.wy, b.wx, b.wy) < proj.explosion_radius:
                            slice_part = b.cut((1.0, 0.0))
                            if slice_part:
                                particles.append(slice_part)

                    # Dano em área (com 50% de redução de dano para Kasumi contra sua própria bomba)
                    p1_in_range = p1.is_alive and world_distance(proj.wx, proj.wy, p1.wx, p1.wy) < proj.explosion_radius
                    p2_in_range = p2.is_alive and world_distance(proj.wx, proj.wy, p2.wx, p2.wy) < proj.explosion_radius

                    p1_dmg = 1 if (proj.owner == p1 and getattr(p1, "char_type", "") == "kasumi") else 2
                    p2_dmg = 1 if (proj.owner == p2 and getattr(p2, "char_type", "") == "kasumi") else 2

                    p1_dead = False
                    p2_dead = False

                    if p1_in_range:
                        _, p1_dead = p1.take_hit((0, 0), damage=p1_dmg)
                        for _ in range(25 if p1_dead else 10):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        if p1_dead and cinematic_director:
                            cinematic_director.trigger_fatal_strike(proj.owner, p1, "KASUMI_EXPLODE", (0, 0))

                    if p2_in_range:
                        _, p2_dead = p2.take_hit((0, 0), damage=p2_dmg)
                        for _ in range(25 if p2_dead else 10):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        if p2_dead and cinematic_director:
                            cinematic_director.trigger_fatal_strike(proj.owner, p2, "KASUMI_EXPLODE", (0, 0))

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
                    proj.is_active = False
                    if target.state == STATE_PARRY:
                        banners.append(FloatingBanner("PARRY BULLET!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                        for _ in range(14):
                            particles.append(SparkParticle(proj.wx, proj.wy, 0.7))
                    else:
                        hit, dead = target.take_hit((proj.vx, proj.vy), damage=2)
                        if dead:
                            camera.add_shake(16.0)
                            banners.append(FloatingBanner("TANEGASHIMA HEADSHOT!", target.wx, target.wy, wz=1.8, color=(255, 180, 50)))
                            for _ in range(30):
                                particles.append(BloodParticle(target.wx, target.wy, 0.6))
                            self.hitstop_timer = 0.14
                            winner = winner_id
                            if cinematic_director:
                                cinematic_director.trigger_fatal_strike(proj.owner, target, "HEADSHOT_EXPLODE", (proj.vx, proj.vy))

            # Se for NUVEM DE VENENO (PoisonCloudProjectile)
            elif isinstance(proj, PoisonCloudProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (proj.radius + target.radius):
                    if not getattr(target, "is_poisoned", False):
                        proj.is_active = False
                        target.is_poisoned = True
                        target.poison_timer = 4.0
                        target.speed *= 1.08  # Leve boost de adrenalina sem torná-lo invencível
                        if hasattr(proj.owner, "on_poison_inflicted"):
                            proj.owner.on_poison_inflicted(target)
                        camera.add_shake(7.0)
                        banners.append(FloatingBanner("POISONED! 4s TO SURVIVE!", target.wx, target.wy, wz=1.8, color=(80, 225, 120), duration=3.5))
                        for _ in range(16):
                            particles.append(SparkParticle(target.wx, target.wy, 0.5))

            # Se for FLECHA DE KYUDO (KyudoArrowProjectile)
            elif isinstance(proj, KyudoArrowProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.50 + target.radius):
                    proj.is_active = False
                    if target.state == STATE_PARRY:
                        banners.append(FloatingBanner("PARRY ARROW!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                        for _ in range(10):
                            particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                    else:
                        hit, dead = target.take_hit((proj.vx, proj.vy), damage=2)
                        if dead:
                            camera.add_shake(15.0)
                            banners.append(FloatingBanner("YUMI HEART SHOT!", target.wx, target.wy, wz=1.8, color=(100, 220, 140)))
                            for _ in range(25):
                                particles.append(BloodParticle(target.wx, target.wy, 0.6))
                            self.hitstop_timer = 0.12
                            winner = winner_id
                            if cinematic_director:
                                cinematic_director.trigger_fatal_strike(proj.owner, target, "SAITOU_IMPALE", (proj.vx, proj.vy))

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
                        else:
                            proj.state = "HOOKED_PULLING"
                            proj.target = target
                            target.stun(0.35)
                            camera.add_shake(6.0)
                            banners.append(FloatingBanner("KUSARIGAMA HOOK!", target.wx, target.wy, wz=1.8, color=(195, 120, 255)))
                            for _ in range(12):
                                particles.append(SparkParticle(target.wx, target.wy, 0.4))

            if proj.is_active:
                active_projectiles.append(proj)

        projectiles.clear()
        projectiles.extend(active_projectiles)

        # Atualizar cronômetro de veneno dos combatentes
        for fighter, other_id in ((p1, "P2_WINS"), (p2, "P1_WINS")):
            if fighter.is_alive and getattr(fighter, "is_poisoned", False):
                fighter.poison_timer -= dt
                if fighter.poison_timer <= 0:
                    fighter.is_poisoned = False
                    fighter.take_hit((0, 0), damage=99)
                    banners.append(FloatingBanner("POISON DEATH!", fighter.wx, fighter.wy, wz=1.8, color=(80, 225, 120)))
                    for _ in range(30):
                        particles.append(BloodParticle(fighter.wx, fighter.wy, 0.6))
                    if winner is None:
                        winner = other_id
                    if cinematic_director:
                        cinematic_director.trigger_fatal_strike(None, fighter, "OKUNI_MELT", (0, 0))

        # -------------------------------------------------------------
        # 2. COMBATE DO CÃO DOBERMAN (SE HOUVER AMERICAN NINJA)
        # -------------------------------------------------------------
        # Cão do Jogador 1 contra Jogador 2
        if hasattr(p1, "dog") and p1.dog and p1.dog.state == STATE_DOG_CHARGE and p2.is_alive:
            dog = p1.dog
            # Verificar se o Jogador 2 acertou o cão durante o ataque!
            if p2.hitbox_active and world_distance(p2.hitbox_center[0], p2.hitbox_center[1], dog.wx, dog.wy) < (p2.hitbox_radius + dog.radius):
                # O oponente acertou o cachorro! Nocauteado por 4.5s!
                dog.knock_out(4.5)
                for _ in range(12):
                    particles.append(SparkParticle(dog.wx, dog.wy, 0.4))
                camera.add_shake(6.0)
                banners.append(FloatingBanner("DOG INJURED! (4.5s)", dog.wx, dog.wy, wz=1.4, color=(255, 80, 80)))
            elif world_distance(dog.wx, dog.wy, p2.wx, p2.wy) < (dog.hitbox_radius + p2.radius):
                # O cão atingiu o oponente!
                if p2.state == STATE_PARRY:
                    dog.knock_out(2.0)
                    camera.add_shake(7.0)
                    banners.append(FloatingBanner("PARRY DOG!", p2.wx, p2.wy, wz=1.7, color=(100, 200, 255)))
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
                            cinematic_director.trigger_fatal_strike(p1, p2, "CLEAN_DECAP", (dog.facing_x, dog.facing_y))

        # Cão do Jogador 2 contra Jogador 1
        if hasattr(p2, "dog") and p2.dog and p2.dog.state == STATE_DOG_CHARGE and p1.is_alive and winner is None:
            dog = p2.dog
            if p1.hitbox_active and world_distance(p1.hitbox_center[0], p1.hitbox_center[1], dog.wx, dog.wy) < (p1.hitbox_radius + dog.radius):
                dog.knock_out(4.5)
                for _ in range(12):
                    particles.append(SparkParticle(dog.wx, dog.wy, 0.4))
                camera.add_shake(6.0)
                banners.append(FloatingBanner("DOG INJURED! (4.5s)", dog.wx, dog.wy, wz=1.4, color=(255, 80, 80)))
            elif world_distance(dog.wx, dog.wy, p1.wx, p1.wy) < (dog.hitbox_radius + p1.radius):
                if p1.state == STATE_PARRY:
                    dog.knock_out(2.0)
                    camera.add_shake(7.0)
                    banners.append(FloatingBanner("PARRY DOG!", p1.wx, p1.wy, wz=1.7, color=(100, 200, 255)))
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
                            cinematic_director.trigger_fatal_strike(p2, p1, "CLEAN_DECAP", (dog.facing_x, dog.facing_y))

        # -------------------------------------------------------------
        # 3. CORTE DE BAMBUS E FAÍSCAS EM ROCHAS
        # -------------------------------------------------------------
        self._check_bamboo_cuts(p1, game_map, particles)
        self._check_bamboo_cuts(p2, game_map, particles)
        self._check_obstacle_sparks(p1, game_map, particles, camera)
        self._check_obstacle_sparks(p2, game_map, particles, camera)

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
                    if cinematic_director:
                        cinematic_director.trigger_fatal_strike(p2, p1, "MURASAKI_DECAP", p2.slash_dir)
                    return "P2_WINS"

                else:
                    # Ambos têm mesma prioridade -> Choque de Lâminas (CLASH!)
                    mid_x = (hx1 + hx2) / 2
                    mid_y = (hy1 + hy2) / 2
                    for _ in range(15):
                        particles.append(SparkParticle(mid_x, mid_y, 0.6))
                    banners.append(FloatingBanner("CLASH!", mid_x, mid_y, wz=1.6, color=(255, 230, 80)))
                    camera.add_shake(7.0)
                    p1.stun(0.4)
                    p2.stun(0.4)
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
            if world_distance(hx, hy, p2.wx, p2.wy) < (p1.hitbox_radius + p2.radius):
                p1.hitbox_active = False

                if p2.state == STATE_PARRY:
                    for _ in range(12):
                        particles.append(SparkParticle(p2.wx, p2.wy, 0.7))
                    parry_msg = "PARRY GATOTSU!" if p1.state == "GATOTSU_CHARGE" else "PARRY!"
                    banners.append(FloatingBanner(parry_msg, p2.wx, p2.wy, wz=1.7, color=(100, 200, 255)))
                    camera.add_shake(8.0)
                    p1.stun(0.85)
                elif getattr(p1, "is_rifle_butt", False):
                    # Coronhada agressiva do Teppo: causa 1 de dano, afasta 1.6m e atordoa o adversário
                    hit, dead = p2.take_hit(p1.slash_dir, damage=1)
                    p2.stun(0.50)
                    p2.wx = max(1.0, min(game_map.cols - 1.0, p2.wx + p1.facing_x * 1.6))
                    p2.wy = max(1.0, min(game_map.rows - 1.0, p2.wy + p1.facing_y * 1.6))
                    camera.add_shake(8.0)
                    banners.append(FloatingBanner("RIFLE BUTT - 1 DMG!", p2.wx, p2.wy, wz=1.7, color=(210, 210, 230)))
                    for _ in range(12):
                        particles.append(SparkParticle(p2.wx, p2.wy, 0.5))
                    if dead:
                        winner = "P1_WINS"
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p1, p2, "HEADSHOT_EXPLODE", p1.slash_dir)
                else:
                    damage = 1 if hasattr(p1, "has_kunai") else 2
                    hit, dead = p2.take_hit(p1.slash_dir, damage=damage)
                    if dead:
                        camera.add_shake(14.0)
                        kill_msg = "GATOTSU - 1 HIT KILL!" if p1.state == "GATOTSU_CHARGE" else "FATAL STRIKE!"
                        banners.append(FloatingBanner(kill_msg, p2.wx, p2.wy, wz=1.8, color=(120, 210, 255) if p1.state == "GATOTSU_CHARGE" else (255, 60, 60)))
                        for _ in range(25):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        self.hitstop_timer = 0.12
                        winner = "P1_WINS"
                        if cinematic_director:
                            death_style = _get_death_style_for_attacker(p1)
                            cinematic_director.trigger_fatal_strike(p1, p2, death_style, p1.slash_dir)
                    elif hit:
                        camera.add_shake(7.0)
                        banners.append(FloatingBanner("KUNAI STAB (1/2)!", p2.wx, p2.wy, wz=1.7, color=(255, 200, 50)))
                        for _ in range(12):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))

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
            if world_distance(hx, hy, p1.wx, p1.wy) < (p2.hitbox_radius + p1.radius):
                p2.hitbox_active = False

                if p1.state == STATE_PARRY:
                    for _ in range(12):
                        particles.append(SparkParticle(p1.wx, p1.wy, 0.7))
                    parry_msg = "PARRY GATOTSU!" if p2.state == "GATOTSU_CHARGE" else "PARRY!"
                    banners.append(FloatingBanner(parry_msg, p1.wx, p1.wy, wz=1.7, color=(100, 200, 255)))
                    camera.add_shake(8.0)
                    p2.stun(0.85)
                elif getattr(p2, "is_rifle_butt", False):
                    # Coronhada agressiva do Teppo: causa 1 de dano, afasta 1.6m e atordoa o adversário
                    hit, dead = p1.take_hit(p2.slash_dir, damage=1)
                    p1.stun(0.50)
                    p1.wx = max(1.0, min(game_map.cols - 1.0, p1.wx + p2.facing_x * 1.6))
                    p1.wy = max(1.0, min(game_map.rows - 1.0, p1.wy + p2.facing_y * 1.6))
                    camera.add_shake(8.0)
                    banners.append(FloatingBanner("RIFLE BUTT - 1 DMG!", p1.wx, p1.wy, wz=1.7, color=(210, 210, 230)))
                    for _ in range(12):
                        particles.append(SparkParticle(p1.wx, p1.wy, 0.5))
                    if dead:
                        winner = "P2_WINS"
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p2, p1, "HEADSHOT_EXPLODE", p2.slash_dir)
                else:
                    damage = 1 if hasattr(p2, "has_kunai") else 2
                    hit, dead = p1.take_hit(p2.slash_dir, damage=damage)
                    if dead:
                        camera.add_shake(14.0)
                        kill_msg = "GATOTSU - 1 HIT KILL!" if p2.state == "GATOTSU_CHARGE" else "FATAL STRIKE!"
                        banners.append(FloatingBanner(kill_msg, p1.wx, p1.wy, wz=1.8, color=(120, 210, 255) if p2.state == "GATOTSU_CHARGE" else (70, 150, 255)))
                        for _ in range(25):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        self.hitstop_timer = 0.12
                        winner = "P2_WINS"
                        if cinematic_director:
                            death_style = _get_death_style_for_attacker(p2)
                            cinematic_director.trigger_fatal_strike(p2, p1, death_style, p2.slash_dir)
                    elif hit:
                        camera.add_shake(7.0)
                        banners.append(FloatingBanner("KUNAI STAB (1/2)!", p1.wx, p1.wy, wz=1.7, color=(255, 200, 50)))
                        for _ in range(12):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))

        # -------------------------------------------------------------
        # 7. ATUALIZAR E REMOVER DECOYS EXPIRADOS
        # -------------------------------------------------------------
        if decoys:
            for d in decoys:
                d.update(dt)
            decoys[:] = [d for d in decoys if d.is_active]

        return winner

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

    def _check_obstacle_sparks(self, fighter, game_map, particles: list, camera):
        if not fighter.hitbox_active:
            return
        hx, hy = fighter.hitbox_center

        for rock in game_map.rocks:
            if world_distance(hx, hy, rock.wx, rock.wy) < (fighter.hitbox_radius * 0.7 + rock.radius):
                for _ in range(4):
                    particles.append(SparkParticle(hx, hy, 0.5))
                camera.add_shake(2.0)

        if game_map.well:
            if world_distance(hx, hy, game_map.well.wx, game_map.well.wy) < (fighter.hitbox_radius * 0.7 + game_map.well.radius):
                for _ in range(4):
                    particles.append(SparkParticle(hx, hy, 0.6))
                camera.add_shake(2.0)
