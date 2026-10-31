"""
Gerenciador de regras de combate: lâminas, kunais, shurikens com stun,
botes letais do cão Doberman e contra-ataques que nocauteiam o cão.
"""
import math
from src.isometric.iso_math import world_distance
from src.combat.hitboxes import check_fighter_melee_hit, align_finisher_pair
from src.effects.particles import (
    SparkParticle, BloodParticle, FloatingBanner
)
from src.entities.samurai import STATE_PARRY, STATE_RECOVERY, STATE_STUNNED, STATE_ROLL
from src.entities.projectile import (
    KunaiProjectile, ShurikenProjectile, TimedBombEntity, SmokeCloudEntity,
    KusarigamaChainEntity, MusketBulletProjectile, PoisonCloudProjectile,
    KyudoArrowProjectile, RopeArrowProjectile, CannonballProjectile,
    RemoteMineEntity, HamayaArrowProjectile, MusashiWaveProjectile,
    SacredArrowVolleyProjectile, NaginataProjectile, KamaitachiProjectile,
    SpiralResonanceProjectile, OfudaProjectile, TalismanWard, BearTrapProjectile,
    AlchemicFlaskProjectile, ChemicalPoolHazard
)
from src.entities.doberman import STATE_DOG_CHARGE, STATE_DOG_KNOCKED_OUT, STATE_DOG_BARK
from src.i18n import t

def _get_death_style_for_attacker(attacker, weapon: str | None = None, victim=None):
    """Estilo de morte contextual pelo golpe recebido: reflete a natureza do ataque que gerou a morte."""
    char_type = getattr(attacker, "char_type", "").lower()
    state = getattr(attacker, "state", "")

    if weapon in ("kunai", "shuriken"):
        if "ninja" in char_type or "hanzo" in char_type:
            return "FOREHEAD_PIN"
        if "joe" in char_type or "american" in char_type:
            return "TRIPLE_SHURIKEN_DISMEMBER"
        return "KUNAI_PIN"
    if weapon == "arrow":
        return "PINNED_TO_EARTH"

    # 1. Kenshi: Iai Flash (KENSHIN_SPLIT) vs Ryuu Tsui Sen (VERTICAL_BISECTION)
    if "kenshin" in char_type or "kenshi" in char_type or "red" in char_type:
        if state == "RYUU_TSUI_SEN":
            return "VERTICAL_BISECTION"
        return "KENSHIN_SPLIT"

    # 2. Musashi: Combo de 3 cortes (DUAL_IMPALE_X_SPREAD) vs Parry/Onda refletida (CROSS_VACUUM_SLICER)
    elif "musashi" in char_type or "blue" in char_type:
        if state in ("PARRY", "REFLECT", "DEFENSE", "CROSS_SHOCKWAVE") or weapon in ("wave", "shockwave", "cross_wave"):
            return "CROSS_VACUUM_SLICER"
        return "DUAL_IMPALE_X_SPREAD"

    # 3. Ren (Shaolin): Combo Marcial (HYAKURETSU_BODY_EXPLOSION) vs Kiai (WALL_SMASH_FATAL)
    elif "ren" in char_type or "shaolin" in char_type:
        if state in ("KIAI", "KIAI_SHOUT"):
            return "WALL_SMASH_FATAL"
        return "HYAKURETSU_BODY_EXPLOSION"

    # 4. Chiyo (Kunoichi 2 Kodachi): Tesoura Dupla (TRIPLE_SCISSOR_CLEAVE) vs Dança Mai (MAI_X_CLEAVE)
    elif "chiyo" in char_type or "kodachi" in char_type or "nodachi" in char_type:
        if state in ("MAI_DANCE", "MAI_RIPOSTE"):
            return "MAI_X_CLEAVE"
        return "TRIPLE_SCISSOR_CLEAVE"

    # 5. Goro (Ciclo 3): Clivagem da Kuwa vs Pisotão Sísmico
    elif "goro" in char_type or "farmer" in char_type:
        if state in ("EARTH_STOMP", "STOMP") or weapon in ("shockwave", "stomp"):
            return "EARTH_STOMP_CRUSH"
        return "KUWA_SKULL_CLEAVE"

    # 6. Ichi (Ciclo 3): Gyaku-Iai Carotídeo vs Contra-ataque de Escuta Perfurante
    elif "ichi" in char_type or "blind" in char_type:
        if state in ("COUNTER_THRUST", "LISTEN", "COUNTER") or weapon == "counter":
            return "BLIND_SPINE_PIERCE"
        return "BLIND_CAROTID_SLICE"

    # 7. Saitou (Veterano Ciclo 3): Gatotsu Empalamento vs Zeroshiki Explosão
    elif "saitou" in char_type or state == "GATOTSU_CHARGE":
        if state in ("ZEROSHIKI", "ZERO_THRUST") or weapon == "zeroshiki":
            return "TORSO_BLAST_THRUST"
        return "HEART_IMPALE_LUNGE"

    # 8. Hanzo (Veterano Ciclo 3): Kunai na Testa vs Estocada Garganta/Coração
    elif "ninja" in char_type or "hanzo" in char_type:
        if weapon in ("kunai", "shuriken"):
            return "FOREHEAD_PIN"
        return "HEART_THROAT_STAB"

    elif "murasaki" in char_type or "purple" in char_type:
        return "MURASAKI_DECAP"
    elif "pirate" in char_type or "anne" in char_type:
        return "PIRATE_CLEAVE"
    elif "musketeer" in char_type or "julie" in char_type:
        return "RAPIER_FLURRY_POINTBLANK"
    elif "joe" in char_type or "american" in char_type:
        if weapon in ("dog", "yamato") or state in ("DOG_ATTACK", "YAMATO"):
            return "WINDMILL_SHURIKEN_DECAP"
        return "TRIPLE_SHURIKEN_DISMEMBER"
    elif "gray" in char_type or "kasumi" in char_type or "kemuri" in char_type:
        return "STAB_FALL"
    elif "rifle" in char_type or "teppo" in char_type:
        return "BLUNT_FALL"
    elif "tomoe" in char_type or "archer" in char_type:
        if weapon in ("hamaya", "sacred_volley"):
            return "HAMAYA_HOLY_PIERCE"
        return "PINNED_TO_EARTH"
    elif "benkei" in char_type or "sohei" in char_type:
        if weapon == "naginata_throw" or state == "THROW_NAGINATA":
            return "SKEWERED_LANCE_FLAG"
        return "NAGINATA_HOIST_SLAM"
    elif "orin" in char_type or "minstrel" in char_type:
        if weapon in ("resonance", "deadly_chord") or state in ("RESONANCE", "ACOUSTIC_RESONANCE"):
            return "RESONANCE_WIND_GALE"
        return "KAMAITACHI_MINCE"
    elif "valerius" in char_type or "necromancer" in char_type:
        if weapon in ("summon", "undead", "skeleton") or state in ("SUMMON", "SKELETON_SUMMON"):
            return "DRAGGED_TO_GRAVE"
        return "SOUL_REAP"
    elif "seimei" in char_type or "onmyoji" in char_type:
        if weapon in ("ward", "fire_pillar", "purification") or state in ("SACRED_WARD", "WARD"):
            return "OFUDA_PURIFICATION_PILLAR"
        return "SEAL_STASIS_COLLAPSE"
    elif "kabuki" in char_type or "okuni" in char_type:
        if weapon == "poison":
            return "DOKUKIRI_MELT"
        return "TESSEN_DECAP"
    elif "daiki" in char_type or "pilgrim" in char_type:
        if state == "POLE_VAULT" or weapon == "vault":
            return "METEOR_STAFF_CRUSH"
        return "THROAT_TEMPLE_CRUSH"
    elif "aoi" in char_type or "huntress" in char_type:
        if weapon == "trap" or (victim is not None and (getattr(victim, "state", "") == STATE_STUNNED or getattr(victim, "slow_timer", 0.0) > 0)):
            return "TRAP_AND_EXECUTE"
        return "SPEAR_HEART_SLIDE"
    elif "raiden" in char_type or "sumo" in char_type:
        if state == "TACHIAI_TACKLE" or weapon == "tackle":
            return "TACHIAI_SHATTER_SLAM"
        return "TSUPPARI_SONIC_DECAP"
    elif "hendrika" in char_type or "alchemist" in char_type:
        if weapon in ("flask", "acid", "fire", "ether", "frost", "miasma") or state in ("FLASK_THROW", "ALCHEMIC_FLASK"):
            flask_type = getattr(attacker, "active_reagent", "acid")
            if flask_type == "fire":
                return "ALCHEMIC_FIRE_ASH"
            elif flask_type == "ether":
                return "ALCHEMIC_ETHER_SUFFOCATION"
            elif flask_type == "frost":
                return "ALCHEMIC_FROST_SHATTER"
            elif flask_type == "miasma":
                return "ALCHEMIC_MIASMA_MELT"
            return "ALCHEMIC_ACID_DISSOLVE"
        return "STILETTO_CAROTID_VITRIOL"
    if weapon in ("kunai", "shuriken"):
        return "KUNAI_PIN"
    if weapon == "arrow":
        return "PINNED_TO_EARTH"
    return "KENSHIN_SPLIT"


# Maior que o alcance do combo de Musashi (hitbox 0.9 + 2.06 + raio), para o ferido não contra-atacar na hora.
HIT_KNOCKBACK_DISTANCE = 3.6

def is_fighter_evading(target) -> bool:
    """
    Retorna True se o combatente estiver em estado de esquiva ativa com i-frames.
    (Roll universal, dash, floreio de capa, shukuchi, kawarimi roll, esquiva ágil).
    """
    if not getattr(target, "is_alive", False):
        return False
    return (
        getattr(target, "state", None) in (
            "ROLL", "DASH", "CAPE_FLOURISH", "SHUKUCHI", "KAWARIMI_ROLL", "DODGE", "PARRY_BACKHOP"
        )
        and getattr(target, "is_invulnerable_dodge", False)
    )

def _is_vertical_hit(attacker, defender) -> bool:
    """
    Checagem de altura 3D para combate melee:
    Golpes executados no solo (att_wz < 0.30m) NÃO acertam alvos no ar (def_wz >= 0.40m),
    passando por baixo do salto acrobático do ninja.
    Se o defensor estiver em salto acrobático ('JUMP'), apenas ataques aéreos
    (Ryuu Tsui Sen, Pole Vault ou atacante no ar com wz >= 0.40m) conseguem atingi-lo.
    """
    att_wz = getattr(attacker, "wz", 0.0)
    def_wz = getattr(defender, "wz", 0.0)
    is_aerial_atk = getattr(attacker, "state", "") in ("RYUU_TSUI_SEN", "POLE_VAULT") or getattr(attacker, "is_aerial_attack", False)
    if getattr(defender, "state", "") == "JUMP":
        return bool(is_aerial_atk or att_wz >= 0.40)
    if att_wz < 0.30 and not is_aerial_atk:
        return def_wz < 0.40
    return abs(att_wz - def_wz) < 0.65

class CombatSystem:
    def __init__(self):
        self.hitstop_timer = 0.0

    def check_projectile_dodge_evasion(self, proj, target) -> bool:
        """
        Verifica se o alvo está em esquiva ativa com i-frames ou se já esquivou deste projétil.
        Se True, registra o alvo em proj.evaded_targets e o projétil cinético passa direto sem
        causar dano, sem ser consumido e sem re-atingir o alvo ao término dos i-frames.
        """
        evaded_set = getattr(proj, "evaded_targets", None)
        if evaded_set is not None and target in evaded_set:
            return True

        if is_fighter_evading(target):
            if evaded_set is None:
                proj.evaded_targets = set()
            proj.evaded_targets.add(target)
            return True

        return False

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
        if getattr(attacker, "char_type", "") == "ren" and getattr(attacker, "combo_step", 0) in (1, 2):
            travel = 0.45
        else:
            travel = HIT_KNOCKBACK_DISTANCE
        pit_at = getattr(game_map, "pit_at", None)
        if pit_at is not None:
            # Um buraco no caminho captura o ferido em vez de ele "pular" por cima.
            step = 0.1
            for i in range(1, int(travel / step) + 1):
                if pit_at(victim.wx + ux * step * i, victim.wy + uy * step * i) is not None:
                    travel = step * i
                    break
        victim.apply_forced_displacement(ux * travel, uy * travel, game_map)

    def _play_sound(self, event, volume: float = 1.0, weapon: str | None = None, surface: str | None = None):
        """Helper seguro para disparo de efeitos sonoros em combate com suporte a multi-camadas."""
        try:
            from src.audio import get_sound_manager, SoundEvent
            ev = getattr(SoundEvent, event.upper(), event) if isinstance(event, str) else event
            get_sound_manager().play_layered(ev, surface=surface, weapon=weapon, volume_scale=volume)
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

            # 5. Julie: Floreio de Capa (cone frontal) e Rolamento (giro completo da capa) desviam projéteis
            elif char_t == "musketeer" and def_fighter.state in ("CAPE_FLOURISH", STATE_ROLL):
                rolling = def_fighter.state == STATE_ROLL
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        dist = world_distance(def_fighter.wx, def_fighter.wy, proj.wx, proj.wy)
                        if dist < (2.1 if rolling else 1.95):
                            proj_dx = proj.wx - def_fighter.wx
                            proj_dy = proj.wy - def_fighter.wy
                            dot = (proj_dx * def_fighter.facing_x + proj_dy * def_fighter.facing_y) / max(0.001, dist)
                            if rolling or dot > 0.0:
                                proj.is_active = False
                                for _ in range(12):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.55, color=(100, 180, 255)))
                                banners.append(FloatingBanner("CAPE DEFLECTION!", def_fighter.wx, def_fighter.wy, wz=1.75, color=(100, 180, 255)))
                                camera.add_shake(4.5)
                                self._play_sound("dodge_whoosh")

            # 6. Ren: Aura Mística de Kiai (repele projéteis em 360° com expansão)
            elif (char_t == "ren" or getattr(def_fighter, "kiai_aura_active", False)) and getattr(def_fighter, "kiai_aura_active", False):
                k_rad = getattr(def_fighter, "kiai_aura_radius", 2.0)
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        dist = world_distance(def_fighter.wx, def_fighter.wy, proj.wx, proj.wy)
                        if dist <= k_rad:
                            proj.is_active = False
                            for _ in range(16):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6, color=(255, 215, 60)))
                            banners.append(FloatingBanner("KIAI REPULSION!", def_fighter.wx, def_fighter.wy, wz=1.8, color=(255, 215, 60)))
                            camera.add_shake(5.5)
                            self._play_sound("sword_clash")

            # 7. Chiyo: Dança Mai com 2 Nodachi (deflexão em vórtice circular)
            elif (char_t == "chiyo" or getattr(def_fighter, "mai_active", False)) and (def_fighter.state == "MAI_DANCE" or getattr(def_fighter, "mai_active", False)):
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter:
                        dist = world_distance(def_fighter.wx, def_fighter.wy, proj.wx, proj.wy)
                        if dist <= 1.8:
                            proj.is_active = False
                            for _ in range(14):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.55, color=(210, 40, 50)))
                            banners.append(FloatingBanner("MAI DANCE PARRY!", def_fighter.wx, def_fighter.wy, wz=1.75, color=(220, 60, 70)))
                            camera.add_shake(5.0)
                            self._play_sound("sword_clash")

            # 8. Ichi: Postura de Escuta (cone frontal) reflete projéteis com velocidade aumentada (+35%)
            elif (char_t == "ichi" or getattr(def_fighter, "is_listening", False)) and (def_fighter.state == "LISTEN" or getattr(def_fighter, "counter_active", False)):
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter and not getattr(proj, "has_been_reflected_by_ichi", False):
                        dist = world_distance(def_fighter.wx, def_fighter.wy, proj.wx, proj.wy)
                        if dist <= 1.85:
                            proj_dx = proj.wx - def_fighter.wx
                            proj_dy = proj.wy - def_fighter.wy
                            dot = (proj_dx * def_fighter.facing_x + proj_dy * def_fighter.facing_y) / max(0.001, dist)
                            if dot > 0.0:  # Cone frontal de parry direcional
                                # Inverter direção do projétil e aumentar velocidade (+35%)
                                if hasattr(proj, "dir_x") and hasattr(proj, "dir_y"):
                                    proj.dir_x = -proj.dir_x
                                    proj.dir_y = -proj.dir_y
                                if hasattr(proj, "vx") and hasattr(proj, "vy"):
                                    proj.vx = -proj.vx * 1.35
                                    proj.vy = -proj.vy * 1.35
                                if hasattr(proj, "speed"):
                                    proj.speed *= 1.35
                                proj.owner = def_fighter
                                proj.has_been_reflected_by_ichi = True
                                proj.dist_traveled = 0
                                for _ in range(16):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.6, color=(140, 200, 255)))
                                banners.append(FloatingBanner("BLIND REFLECT!", def_fighter.wx, def_fighter.wy, wz=1.8, color=(160, 215, 255)))
                                camera.add_shake(5.5)
                                self._play_sound("parry")

            # 9. Daiki: Salto com Vara (frames iniciais desviam projéteis girando o Bō)
            elif (char_t == "daiki" or getattr(def_fighter, "pole_vault_deflect_active", False)) and getattr(def_fighter, "pole_vault_deflect_active", False):
                for proj in projectiles:
                    if getattr(proj, "is_active", True) and getattr(proj, "owner", None) != def_fighter and not isinstance(proj, (TalismanWard, BearTrapProjectile, TimedBombEntity, RemoteMineEntity)):
                        dist = world_distance(def_fighter.wx, def_fighter.wy, proj.wx, proj.wy)
                        if dist <= 1.85:
                            proj.is_active = False
                            for _ in range(12):
                                particles.append(SparkParticle(proj.wx, proj.wy, 0.6, color=(235, 195, 110)))
                            banners.append(FloatingBanner("BO DEFLECT!", def_fighter.wx, def_fighter.wy, wz=1.8, color=(235, 195, 110)))
                            if camera is not None:
                                camera.add_shake(4.5)
                            self._play_sound("parry")

        active_projectiles = []
        for proj in projectiles:
            if isinstance(proj, (TalismanWard, BearTrapProjectile)):
                p1_alive_before = p1.is_alive
                p2_alive_before = p2.is_alive
                still_valid = proj.update(
                    dt, game_map, particles,
                    fighters=[p1, p2], projectiles=projectiles,
                    banners=banners, cinematic_director=cinematic_director
                )
                if p1_alive_before and not p1.is_alive and winner is None:
                    winner = "P2_WINS"
                    self.hitstop_timer = 0.14
                    self._play_sound("fatal_strike")
                elif p2_alive_before and not p2.is_alive and winner is None:
                    winner = "P1_WINS"
                    self.hitstop_timer = 0.14
                    self._play_sound("fatal_strike")
            elif isinstance(proj, AlchemicFlaskProjectile):
                p1_alive_before = p1.is_alive
                p2_alive_before = p2.is_alive
                target_pools = getattr(proj.owner, "active_pools", None)
                still_valid = proj.update(
                    dt, game_map, particles,
                    fighters=[p1, p2], projectiles=projectiles,
                    banners=banners, cinematic_director=cinematic_director,
                    chemical_pools=target_pools
                )
                if p1_alive_before and not p1.is_alive and winner is None:
                    winner = "P2_WINS"
                    self.hitstop_timer = 0.14
                    self._play_sound("fatal_strike")
                elif p2_alive_before and not p2.is_alive and winner is None:
                    winner = "P1_WINS"
                    self.hitstop_timer = 0.14
                    self._play_sound("fatal_strike")
            elif isinstance(proj, HamayaArrowProjectile) or getattr(proj, "__class__", None).__name__ == "EarthStompShockwave":
                still_valid = proj.update(dt, game_map, particles, projectiles=projectiles)
            elif isinstance(proj, KunaiProjectile):
                still_valid = proj.update(dt, game_map, particles, opponent=(p2 if getattr(proj, "owner", None) == p1 else p1))
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

            # Item 24: O lacaio esqueleto de Valerius é atingível por projéteis inimigos
            target_summon = None
            if getattr(proj, "owner", None) == p1 and getattr(p2, "summon", None) and p2.summon.is_alive:
                target_summon = p2.summon
            elif getattr(proj, "owner", None) == p2 and getattr(p1, "summon", None) and p1.summon.is_alive:
                target_summon = p1.summon

            if target_summon and not isinstance(proj, (TimedBombEntity, RemoteMineEntity)):
                proj_flying = (getattr(proj, "state", "FLYING") == "FLYING") if hasattr(proj, "state") else getattr(proj, "is_active", True)
                if proj_flying and world_distance(proj.wx, proj.wy, target_summon.wx, target_summon.wy) < (0.45 + target_summon.radius):
                    target_summon.take_hit(damage=1, particles=particles)
                    camera.add_shake(5.0)
                    if banners is not None:
                        banners.append(FloatingBanner("SUMMON DESTROYED!", target_summon.wx, target_summon.wy, wz=1.4, color=(160, 220, 255)))
                    self._play_sound("bone_crush")
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
                    if not self.check_projectile_dodge_evasion(proj, target):
                        if target.state in (STATE_PARRY, "MAI_DANCE", "LISTEN"):
                            # Musashi (primeiros 0.28s), Chiyo (Dança Mai) ou Ichi (Postura de Escuta) refletem projéteis
                            can_reflect = (
                                target.state == "MAI_DANCE" or
                                (target.__class__.__name__ == "BlueSamurai" and getattr(target, "parry_reflect_active_timer", 0) > 0) or
                                (target.state == "LISTEN" and hasattr(target, "is_facing_target") and target.is_facing_target(proj.wx, proj.wy))
                            )
                            if can_reflect and not getattr(proj, "has_been_reflected", False):
                                # REFLETE: inverte direção e muda dono
                                proj.vx = -proj.vx
                                proj.vy = -proj.vy
                                proj.dir_x = -proj.dir_x
                                proj.dir_y = -proj.dir_y
                                proj.owner = target
                                proj.has_been_reflected = True
                                proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                                if hasattr(proj, "evaded_targets"):
                                    proj.evaded_targets.clear()
                                if target.state == "MAI_DANCE" and hasattr(target, "on_mai_parry_success"):
                                    target.on_mai_parry_success()
                                    banners.append(FloatingBanner(t("banner_mai_deflect"), target.wx, target.wy, wz=1.8, color=(235, 55, 75)))
                                elif target.state == "LISTEN":
                                    banners.append(FloatingBanner("LISTEN REFLECT!", target.wx, target.wy, wz=1.8, color=(215, 140, 230)))
                                    if hasattr(target, "trigger_counter_thrust"):
                                        target.trigger_counter_thrust(proj.owner.wx, proj.owner.wy, banners=banners, particles=particles)
                                else:
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
                            # Interrompe o vôo imediatamente para não perfurar o alvo repetidamente em múltiplos frames
                            proj.state = "ON_GROUND"
                            proj.wz = 0.05
                            proj.vx = 0.0
                            proj.vy = 0.0
                            proj.vz = 0.0
                            proj.pickup_delay = 0.8
                            if dead:
                                camera.add_shake(15.0)
                                for _ in range(25):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.6))
                                self.hitstop_timer = 0.12
                                winner = winner_id
                                proj.is_active = False
                                self._play_sound("fatal_strike")
                                if cinematic_director:
                                    death_style = _get_death_style_for_attacker(proj.owner, weapon="kunai")
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))
                            else:
                                camera.add_shake(6.0)
                                for _ in range(12):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.4))
                                self._play_sound("flesh_cleave")
                                if banners is not None:
                                    banners.append(FloatingBanner("-2 HP", target.wx, target.wy, wz=1.7, color=(255, 60, 60)))

            # Se for SHURIKEN (Não mata! Apenas aplica stun!)
            elif isinstance(proj, ShurikenProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1

                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.45 + target.radius):
                    if not self.check_projectile_dodge_evasion(proj, target):
                        if target.state in (STATE_PARRY, "MAI_DANCE", "LISTEN"):
                            can_reflect = (
                                target.state == "MAI_DANCE" or
                                (target.__class__.__name__ == "BlueSamurai" and getattr(target, "parry_reflect_active_timer", 0) > 0) or
                                (target.state == "LISTEN" and hasattr(target, "is_facing_target") and target.is_facing_target(proj.wx, proj.wy))
                            )
                            if can_reflect and not getattr(proj, "has_been_reflected", False):
                                # REFLETE: inverte direção e muda dono
                                proj.vx = -proj.vx
                                proj.vy = -proj.vy
                                proj.dir_x = -proj.dir_x
                                proj.dir_y = -proj.dir_y
                                proj.owner = target
                                proj.has_been_reflected = True
                                proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                                if hasattr(proj, "evaded_targets"):
                                    proj.evaded_targets.clear()
                                if target.state == "MAI_DANCE" and hasattr(target, "on_mai_parry_success"):
                                    target.on_mai_parry_success()
                                    banners.append(FloatingBanner(t("banner_mai_deflect"), target.wx, target.wy, wz=1.8, color=(235, 55, 75)))
                                elif target.state == "LISTEN":
                                    banners.append(FloatingBanner("LISTEN REFLECT!", target.wx, target.wy, wz=1.8, color=(215, 140, 230)))
                                    if hasattr(target, "trigger_counter_thrust"):
                                        target.trigger_counter_thrust(proj.owner.wx, proj.owner.wy, banners=banners, particles=particles)
                                else:
                                    banners.append(FloatingBanner("PARRY REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                                camera.add_shake(6.0)
                                self._play_sound("parry")
                            else:
                                # Absorção normal de parry
                                for _ in range(8):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                                banners.append(FloatingBanner("PARRY!", target.wx, target.wy, wz=1.6, color=(100, 200, 255)))
                                self._play_sound("parry")
                                proj.is_active = False
                        else:
                            is_target_moving = getattr(target, "is_moving", False) or target.state in ("WALK", "RUN", "ROLL", "DASH", "SHUKUCHI")
                            # Micro-stun tático perceptível de 0.42s (interrompe ataques ativos)
                            target.stun(0.42)
                            camera.add_shake(5.5)
                            for _ in range(10):
                                particles.append(SparkParticle(target.wx, target.wy, 0.6))

                            if is_target_moving:
                                hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=1)
                                for _ in range(12):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.5))
                                if dead:
                                    winner = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                                    self._play_sound("fatal_strike")
                                    if cinematic_director:
                                        death_style = _get_death_style_for_attacker(proj.owner, weapon="shuriken")
                                        cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))
                            else:
                                if banners is not None:
                                    banners.append(FloatingBanner("MICRO-STUN!", target.wx, target.wy, wz=1.7, color=(140, 220, 255)))
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
                    if camera and hasattr(camera, "add_shake"):
                        camera.add_shake(18.0)
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

                    # Choque de ar da explosão verga bambus e agita atmosfera
                    if hasattr(game_map, "add_wind_impulse"):
                        game_map.add_wind_impulse(proj.wx, proj.wy, strength=2.2, radius=proj.explosion_radius * 1.5, duration=0.85)

                    # Destruir bambus ao redor
                    for b in game_map.bamboos:
                        if not b.is_cut and world_distance(proj.wx, proj.wy, b.wx, b.wy) < proj.explosion_radius:
                            slice_part = b.cut((1.0, 0.0))
                            if slice_part:
                                particles.append(slice_part)

                    # Destruir biombos ao redor
                    for r in getattr(game_map, "rocks", []):
                        if hasattr(r, "break_panel") and not getattr(r, "is_broken", False):
                            if world_distance(proj.wx, proj.wy, r.wx, r.wy) < (proj.explosion_radius + 0.4):
                                r.break_panel((1.0, 0.0), particles)

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
                    if not self.check_projectile_dodge_evasion(proj, target):
                        if target.state in (STATE_PARRY, "MAI_DANCE", "LISTEN"):
                            can_reflect = (
                                target.state == "MAI_DANCE" or
                                (target.__class__.__name__ == "BlueSamurai" and getattr(target, "parry_reflect_active_timer", 0) > 0) or
                                (target.state == "LISTEN" and hasattr(target, "is_facing_target") and target.is_facing_target(proj.wx, proj.wy))
                            )
                            if can_reflect and not getattr(proj, "has_been_reflected", False):
                                # REFLETE: inverte direção e muda dono
                                proj.vx = -proj.vx
                                proj.vy = -proj.vy
                                proj.dir_x = -proj.dir_x
                                proj.dir_y = -proj.dir_y
                                proj.owner = target
                                proj.has_been_reflected = True
                                proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                                if hasattr(proj, "evaded_targets"):
                                    proj.evaded_targets.clear()
                                if target.state == "MAI_DANCE" and hasattr(target, "on_mai_parry_success"):
                                    target.on_mai_parry_success()
                                    banners.append(FloatingBanner(t("banner_mai_deflect"), target.wx, target.wy, wz=1.8, color=(235, 55, 75)))
                                elif target.state == "LISTEN":
                                    banners.append(FloatingBanner("LISTEN REFLECT!", target.wx, target.wy, wz=1.8, color=(215, 140, 230)))
                                    if hasattr(target, "trigger_counter_thrust"):
                                        target.trigger_counter_thrust(proj.owner.wx, proj.owner.wy, banners=banners, particles=particles)
                                else:
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
                    if not self.check_projectile_dodge_evasion(proj, target):
                        if target.state in (STATE_PARRY, "MAI_DANCE", "LISTEN"):
                            can_reflect = (
                                target.state == "MAI_DANCE" or
                                (target.__class__.__name__ == "BlueSamurai" and getattr(target, "parry_reflect_active_timer", 0) > 0) or
                                (target.state == "LISTEN" and hasattr(target, "is_facing_target") and target.is_facing_target(proj.wx, proj.wy))
                            )
                            if can_reflect and not getattr(proj, "has_been_reflected", False):
                                # REFLETE: inverte direção e muda dono
                                proj.vx = -proj.vx
                                proj.vy = -proj.vy
                                proj.dir_x = -proj.dir_x
                                proj.dir_y = -proj.dir_y
                                proj.owner = target
                                proj.has_been_reflected = True
                                proj.dist_traveled = 0  # Reset distance to allow full range travel after reflection
                                if hasattr(proj, "evaded_targets"):
                                    proj.evaded_targets.clear()
                                if target.state == "MAI_DANCE" and hasattr(target, "on_mai_parry_success"):
                                    target.on_mai_parry_success()
                                    banners.append(FloatingBanner(t("banner_mai_deflect"), target.wx, target.wy, wz=1.8, color=(235, 55, 75)))
                                elif target.state == "LISTEN":
                                    banners.append(FloatingBanner("LISTEN REFLECT!", target.wx, target.wy, wz=1.8, color=(215, 140, 230)))
                                    if hasattr(target, "trigger_counter_thrust"):
                                        target.trigger_counter_thrust(proj.owner.wx, proj.owner.wy, banners=banners, particles=particles)
                                else:
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
                                for _ in range(25):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.6))
                                self.hitstop_timer = 0.12
                                winner = winner_id
                                self._play_sound("fatal_strike")
                                if cinematic_director:
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, "PINNED_TO_EARTH", (proj.vx, proj.vy))

            # Se for FLECHA SAGRADA DE KYUDO (HamayaArrowProjectile)
            elif isinstance(proj, HamayaArrowProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.55 + target.radius):
                    if not self.check_projectile_dodge_evasion(proj, target):
                        # Projétil sagrado perfurante: quebra parry ou atinge letalmente
                        proj.is_active = False
                        hit, dead = target.take_hit((proj.vx, proj.vy), damage=2)
                        if dead:
                            camera.add_shake(16.0)
                            for _ in range(30):
                                particles.append(BloodParticle(target.wx, target.wy, 0.6))
                            for _ in range(16):
                                particles.append(SparkParticle(target.wx, target.wy, 0.6, color=(255, 230, 100)))
                            self.hitstop_timer = 0.14
                            winner = winner_id
                            self._play_sound("fatal_strike")
                            if cinematic_director:
                                cinematic_director.trigger_fatal_strike(proj.owner, target, "HAMAYA_HOLY_PIERCE", (proj.vx, proj.vy))

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
                        if not self.check_projectile_dodge_evasion(proj, target):
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
                    if not self.check_projectile_dodge_evasion(proj, target):
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
                                if hasattr(proj, "evaded_targets"):
                                    proj.evaded_targets.clear()
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
                                    for _ in range(35):
                                        particles.append(BloodParticle(target.wx, target.wy, 0.7))
                                    self.hitstop_timer = 0.16
                                    if winner is None:
                                        winner = win_id
                                    self._play_sound("fatal_strike")
                                    if cinematic_director:
                                        cinematic_director.trigger_fatal_strike(proj.owner, target, "KASUMI_EXPLODE", (0, 0))

            # Se for CHUVA DE FLECHAS SAGRADAS EM ARCO (SacredArrowVolleyProjectile)
            elif isinstance(proj, SacredArrowVolleyProjectile) and proj.is_active:
                if proj.has_impacted and not proj.damage_dealt:
                    proj.damage_dealt = True
                    self._play_sound("arrow_hit")
                    for target, win_id in ((p1, "P2_WINS"), (p2, "P1_WINS")):
                        if target.is_alive and target != proj.owner:
                            if world_distance(proj.target_wx, proj.target_wy, target.wx, target.wy) < (proj.radius + target.radius):
                                hit, dead = target.take_hit((0, 0), damage=2)
                                if dead:
                                    camera.add_shake(20.0)
                                    for _ in range(35):
                                        particles.append(BloodParticle(target.wx, target.wy, 0.7))
                                    for _ in range(20):
                                        particles.append(SparkParticle(target.wx, target.wy, 0.6, color=(255, 230, 100)))
                                    self.hitstop_timer = 0.16
                                    if winner is None:
                                        winner = win_id
                                    self._play_sound("fatal_strike")
                                    if cinematic_director:
                                        cinematic_director.trigger_fatal_strike(proj.owner, target, "HAMAYA_HOLY_PIERCE", (0, 0))

            # Se for ARREMESSO DE NAGINATA (NaginataProjectile)
            elif isinstance(proj, NaginataProjectile) and proj.is_active and proj.state == "FLYING":
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and not proj.has_hit_fighter and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.55 + target.radius):
                    if not self.check_projectile_dodge_evasion(proj, target):
                        proj.has_hit_fighter = True
                        if target.state == STATE_PARRY:
                            banners.append(FloatingBanner("HEAVY DEFLECT!", target.wx, target.wy, wz=1.7, color=(255, 200, 100)))
                            camera.add_shake(6.0)
                            self._play_sound("parry")
                            target.stun(0.40)
                            proj._embed_into_ground(game_map, particles)
                        else:
                            hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=2)
                            if dead:
                                camera.add_shake(16.0)
                                for _ in range(25):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.6))
                                self.hitstop_timer = 0.14
                                winner = winner_id
                                self._play_sound("fatal_strike")
                                if cinematic_director:
                                    death_style = "SKEWERED_LANCE_FLAG"
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))
                                proj.is_active = False
                            else:
                                camera.add_shake(8.0)
                                for _ in range(15):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.5))
                                self._play_sound("obstacle_hit")
                                proj._embed_into_ground(game_map, particles)

            # Se for LÂMINA KAMAITACHI OU ONDA ESPIRAL (KamaitachiProjectile / SpiralResonanceProjectile)
            elif isinstance(proj, (KamaitachiProjectile, SpiralResonanceProjectile)) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.55 + target.radius):
                    if not self.check_projectile_dodge_evasion(proj, target):
                        if target.state in (STATE_PARRY, "MAI_DANCE", "LISTEN"):
                            can_reflect = (
                                target.state == "MAI_DANCE" or
                                (target.__class__.__name__ == "BlueSamurai" and getattr(target, "parry_reflect_active_timer", 0) > 0) or
                                (target.state == "LISTEN" and hasattr(target, "is_facing_target") and target.is_facing_target(proj.wx, proj.wy))
                            )
                            if can_reflect and not getattr(proj, "has_been_reflected", False):
                                proj.vx = -proj.vx
                                proj.vy = -proj.vy
                                proj.dir_x = -proj.dir_x
                                proj.dir_y = -proj.dir_y
                                proj.owner = target
                                proj.has_been_reflected = True
                                proj.dist_traveled = 0
                                if hasattr(proj, "evaded_targets"):
                                    proj.evaded_targets.clear()
                                if target.state == "MAI_DANCE" and hasattr(target, "on_mai_parry_success"):
                                    target.on_mai_parry_success()
                                    banners.append(FloatingBanner(t("banner_mai_deflect"), target.wx, target.wy, wz=1.8, color=(235, 55, 75)))
                                elif target.state == "LISTEN":
                                    banners.append(FloatingBanner("LISTEN REFLECT!", target.wx, target.wy, wz=1.8, color=(215, 140, 230)))
                                    if hasattr(target, "trigger_counter_thrust"):
                                        target.trigger_counter_thrust(proj.owner.wx, proj.owner.wy, banners=banners, particles=particles)
                                else:
                                    banners.append(FloatingBanner("PARRY REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                                camera.add_shake(6.0)
                                self._play_sound("parry")
                            else:
                                for _ in range(10):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.6))
                                banners.append(FloatingBanner("PARRY!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                                camera.add_shake(5.0)
                                self._play_sound("parry")
                                proj.is_active = False
                        else:
                            proj_damage = 1 if isinstance(proj, KamaitachiProjectile) else 2
                            hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=proj_damage)
                            if dead:
                                camera.add_shake(16.0)
                                for _ in range(25):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.6))
                                self.hitstop_timer = 0.12
                                winner = winner_id
                                self._play_sound("fatal_strike")
                                if cinematic_director:
                                    death_style = "RESONANCE_WIND_GALE" if isinstance(proj, SpiralResonanceProjectile) else "KAMAITACHI_MINCE"
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, death_style, (proj.dir_x, proj.dir_y))
                            else:
                                camera.add_shake(7.0)
                                for _ in range(12):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.5))
                                self._play_sound("sword_slash")
                            proj.is_active = False

            # Se for OFUDA CORTANTE (OfudaProjectile - Ciclo 4 Seimei)
            elif isinstance(proj, OfudaProjectile) and proj.is_active:
                target = p2 if proj.owner == p1 else p1
                winner_id = "P1_WINS" if proj.owner == p1 else "P2_WINS"
                if target.is_alive and world_distance(proj.wx, proj.wy, target.wx, target.wy) < (0.50 + target.radius):
                    if not self.check_projectile_dodge_evasion(proj, target):
                        el = getattr(proj, "element", "wood")
                        is_metal_break = (el == "metal")

                        if target.state in (STATE_PARRY, "MAI_DANCE", "LISTEN") and not is_metal_break:
                            can_reflect = (
                                target.state == "MAI_DANCE" or
                                (target.__class__.__name__ == "BlueSamurai" and getattr(target, "parry_reflect_active_timer", 0) > 0) or
                                (target.state == "LISTEN" and hasattr(target, "is_facing_target") and target.is_facing_target(proj.wx, proj.wy))
                            )
                            if can_reflect and not getattr(proj, "has_been_reflected", False):
                                proj.dir_x = -proj.dir_x
                                proj.dir_y = -proj.dir_y
                                proj.owner = target
                                proj.has_been_reflected = True
                                proj.dist_traveled = 0
                                if hasattr(proj, "evaded_targets"):
                                    proj.evaded_targets.clear()
                                banners.append(FloatingBanner("OFUDA REFLECT!", target.wx, target.wy, wz=1.8, color=(255, 100, 255)))
                                camera.add_shake(6.0)
                                self._play_sound("parry")
                            else:
                                for _ in range(10):
                                    particles.append(SparkParticle(proj.wx, proj.wy, 0.6, color=(140, 205, 255)))
                                banners.append(FloatingBanner("PARRY OFUDA!", target.wx, target.wy, wz=1.7, color=(100, 200, 255)))
                                camera.add_shake(5.0)
                                self._play_sound("parry")
                                proj.is_active = False
                        else:
                            dmg = getattr(proj, "damage", 2)
                            hit, dead = target.take_hit((proj.dir_x, proj.dir_y), damage=dmg)

                            # Efeitos especiais elementais distintos e viscerais no acerto
                            if not dead and getattr(target, "is_alive", True):
                                if el == "wood":
                                    target.root_timer = 2.0
                                    target.is_rooted = True
                                    target.stun(0.85)
                                    banners.append(FloatingBanner("KUSABI ROOT (IMMOBILIZED)!", target.wx, target.wy, wz=1.6, color=(50, 220, 120)))
                                    camera.add_shake(6.0)
                                elif el == "fire":
                                    target.burning_timer = 3.5
                                    banners.append(FloatingBanner("GUREN EXPLOSIVE BLAZE!", target.wx, target.wy, wz=1.6, color=(255, 80, 45)))
                                    camera.add_shake(12.0)
                                elif el == "water":
                                    if hasattr(target, "apply_slow"):
                                        target.apply_slow(3.8)
                                    else:
                                        target.slow_timer = 3.8
                                    target.stun(0.45)
                                    banners.append(FloatingBanner("TIDAL TORRENT (SLOW -65%)!", target.wx, target.wy, wz=1.6, color=(70, 180, 255)))
                                    camera.add_shake(8.0)
                                elif el == "earth" and game_map is not None:
                                    target.state = STATE_STUNNED
                                    target.state_timer = 1.25
                                    target.apply_forced_displacement(proj.dir_x * 1.8, proj.dir_y * 1.8, game_map)
                                    banners.append(FloatingBanner("EARTHQUAKE (KNOCKDOWN)!", target.wx, target.wy, wz=1.6, color=(235, 185, 65)))
                                    camera.add_shake(15.0)
                                elif el == "metal":
                                    target.stun(0.95)
                                    banners.append(FloatingBanner("HAGANE PIERCE (UNBLOCKABLE)!", target.wx, target.wy, wz=1.6, color=(245, 248, 255)))
                                    camera.add_shake(12.0)
                                elif el == "yinyang":
                                    target.confused_timer = 3.8
                                    banners.append(FloatingBanner("ASTRAL ECLIPSE (CONFUSED)!", target.wx, target.wy, wz=1.6, color=(225, 150, 255)))
                                    camera.add_shake(10.0)

                            if dead:
                                camera.add_shake(16.0)
                                for _ in range(25):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.6))
                                self.hitstop_timer = 0.12
                                winner = winner_id
                                self._play_sound("fatal_strike")
                                finisher_style = f"SEIMEI_FATAL_{el.upper()}" if el in ("wood", "fire", "earth", "metal", "water", "yinyang") else "SEAL_STASIS_COLLAPSE"
                                if cinematic_director:
                                    cinematic_director.trigger_fatal_strike(proj.owner, target, finisher_style, (proj.dir_x, proj.dir_y))
                            else:
                                camera.add_shake(7.0)
                                for _ in range(12):
                                    particles.append(BloodParticle(target.wx, target.wy, 0.5))
                                self._play_sound("sword_slash")
                            proj.is_active = False

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
                    "volley_cooldown_timer", "sacred_volley_cooldown_timer",
                    "flintlock_timer", "cape_timer", "trap_timer", "zeroshiki_timer",
                    "shuriken_timer", "thrust_timer", "kama_timer", "backstep_timer", "cleave_timer",
                    "vault_timer", "spear_timer"
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
                        for _ in range(30):
                            particles.append(BloodParticle(fighter.wx, fighter.wy, 0.6))
                        if winner is None:
                            winner = other_id
                        if cinematic_director:
                            other_fighter = p2 if fighter == p1 else p1
                            cinematic_director.trigger_fatal_strike(other_fighter, fighter, "DOKUKIRI_MELT", (0, 0))
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
                    # MORTE FATAL PELO DOBERMAN (1-Hit Kill letal)!
                    hit, dead = p2.take_hit((dog.facing_x, dog.facing_y), damage=3)
                    if dead:
                        camera.add_shake(16.0)
                        for _ in range(30):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        self.hitstop_timer = 0.14
                        winner = "P1_WINS"
                        dog.hitbox_active = False
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p1, p2, "WINDMILL_SHURIKEN_DECAP", (dog.facing_x, dog.facing_y))
                        else:
                            dog.state = "FOLLOW"
                    else:
                        dog.state = "FOLLOW"
                        dog.hitbox_active = False
                        dog.cooldown_timer = 2.5
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
                    # MORTE FATAL PELO DOBERMAN (1-Hit Kill letal)!
                    hit, dead = p1.take_hit((dog.facing_x, dog.facing_y), damage=3)
                    if dead:
                        camera.add_shake(16.0)
                        for _ in range(30):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        self.hitstop_timer = 0.14
                        winner = "P2_WINS"
                        dog.hitbox_active = False
                        if cinematic_director:
                            cinematic_director.trigger_fatal_strike(p2, p1, "WINDMILL_SHURIKEN_DECAP", (dog.facing_x, dog.facing_y))
                        else:
                            dog.state = "FOLLOW"
                    else:
                        dog.state = "FOLLOW"
                        dog.hitbox_active = False
                        dog.cooldown_timer = 2.5
                        if ctrl_mgr:
                            ctrl_mgr.rumble_player(1, 0.8, 1.0, 320)
                            ctrl_mgr.rumble_player(0, 1.0, 1.0, 400)

        # Esqueleto Invocado de Valerius contra ataques corpo a corpo
        for owner_p, enemy_p in ((p1, p2), (p2, p1)):
            if getattr(owner_p, "summon", None) and owner_p.summon.is_alive:
                skel = owner_p.summon
                if enemy_p.is_alive and enemy_p.hitbox_active and world_distance(enemy_p.hitbox_center[0], enemy_p.hitbox_center[1], skel.wx, skel.wy) < (enemy_p.hitbox_radius + skel.radius):
                    skel.take_hit(damage=1, particles=particles)
                    self._play_sound("bone_crush")
                    camera.add_shake(5.0)
                    banners.append(FloatingBanner("SUMMON SHATTERED!", skel.wx, skel.wy, wz=1.4, color=(235, 230, 215)))

        # -------------------------------------------------------------
        # 3. CORTE DE BAMBUS E FAÍSCAS EM ROCHAS
        # -------------------------------------------------------------
        self._check_bamboo_cuts(p1, game_map, particles)
        self._check_bamboo_cuts(p2, game_map, particles)
        self._check_obstacle_sparks(p1, game_map, particles, camera, ctrl_mgr, p_idx=0)
        self._check_obstacle_sparks(p2, game_map, particles, camera, ctrl_mgr, p_idx=1)
        if getattr(game_map, "interactives", None):
            self._check_interactives(p1, p2, game_map, projectiles)

        # Checagem de combate contra perigos da arena (ex: zumbis e mãos no cemitério gótico)
        for h in getattr(game_map, "hazards", []):
            if hasattr(h, "check_combat_interactions"):
                h.check_combat_interactions(p1, p2, projectiles, particles, banners, camera)

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
            if check_fighter_melee_hit(p1, p2.wx, p2.wy, p2.radius) and _is_vertical_hit(p1, p2):
                p1.hitbox_active = False

                if p2.state == STATE_PARRY and p1.state != "POLE_VAULT":
                    if p1.state == "ZEROSHIKI":
                        # ZEROSHIKI GUARD PIERCE: Causa 1 de dano de estilhaço mesmo contra parry!
                        for _ in range(16):
                            particles.append(SparkParticle(p2.wx, p2.wy, 0.7, color=(255, 200, 100)))
                        for _ in range(8):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.5))
                        if banners is not None:
                            banners.append(FloatingBanner("ZEROSHIKI GUARD PIERCE! -1 HP", p2.wx, p2.wy, wz=1.75, color=(255, 120, 60)))
                        camera.add_shake(10.0)
                        self._play_sound("flesh_cleave")
                        hit, dead = p2.take_hit((p1.facing_x, p1.facing_y), damage=1)
                        if dead:
                            winner = "P1_WINS"
                            self.hitstop_timer = 0.14
                            self._play_sound("fatal_strike")
                            if cinematic_director:
                                cinematic_director.trigger_fatal_strike(p1, p2, "TORSO_BLAST_THRUST", (p1.facing_x, p1.facing_y))
                        else:
                            p2.stun(0.35)
                        if ctrl_mgr:
                            ctrl_mgr.rumble_player(0, 0.6, 0.9, 220)
                            ctrl_mgr.rumble_player(1, 0.8, 1.0, 250)
                    else:
                        for _ in range(12):
                            particles.append(SparkParticle(p2.wx, p2.wy, 0.7))
                        parry_msg = "PARRY GATOTSU!" if p1.state == "GATOTSU_CHARGE" else "PARRY!"
                        banners.append(FloatingBanner(parry_msg, p2.wx, p2.wy, wz=1.7, color=(100, 200, 255)))
                        camera.add_shake(8.0)
                        if hasattr(p2, "on_parry_successful"):
                            p2.on_parry_successful(p1, particles=particles, banners=banners)
                        if hasattr(p1, "on_parried"):
                            p1.on_parried(p2, game_map=game_map, banners=banners, particles=particles)
                        else:
                            p1.stun(0.85)
                        self._play_sound("parry")
                        if ctrl_mgr:
                            ctrl_mgr.rumble_player(0, 0.5, 0.8, 200)
                            ctrl_mgr.rumble_player(1, 0.6, 0.8, 180)
                elif p2.state == "CAPE_FLOURISH":
                    for _ in range(12):
                        particles.append(SparkParticle(p2.wx, p2.wy, 0.65, color=(100, 180, 255)))
                    banners.append(FloatingBanner("CAPE RIPOSTE!", p2.wx, p2.wy, wz=1.75, color=(100, 180, 255)))
                    camera.add_shake(7.0)
                    p1.stun(0.65)
                    p1.wx = max(1.0, min(game_map.cols - 1.0, p1.wx + p2.facing_x * 1.4))
                    p1.wy = max(1.0, min(game_map.rows - 1.0, p1.wy + p2.facing_y * 1.4))
                    self._play_sound("parry")
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.5, 0.7, 180)
                        ctrl_mgr.rumble_player(1, 0.5, 0.7, 180)
                elif p2.state == "MAI_DANCE":
                    # Dança Mai da Chiyo: apara o golpe em pirueta, cancela a exaustão e aplica contra-corte de 1 HP
                    for _ in range(16):
                        particles.append(SparkParticle(p2.wx, p2.wy, 0.65, color=(225, 42, 58)))
                    banners.append(FloatingBanner("MAI CONTRA-CORTE!", p2.wx, p2.wy, wz=1.78, color=(235, 55, 75)))
                    camera.add_shake(8.0)
                    if hasattr(p2, "on_mai_parry_success"):
                        p2.on_mai_parry_success(p1, game_map)
                    p1.stun(0.48)
                    p1.wx = max(1.0, min(game_map.cols - 1.0, p1.wx - p1.facing_x * 1.25))
                    p1.wy = max(1.0, min(game_map.rows - 1.0, p1.wy - p1.facing_y * 1.25))
                    self._play_sound("parry")
                    hit_c, dead_c = p1.take_hit((p2.facing_x, p2.facing_y), damage=1)
                    if dead_c:
                        winner = "P2_WINS"
                        self.hitstop_timer = 0.12
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            align_finisher_pair(p2, p1, game_map)
                            cinematic_director.trigger_fatal_strike(p2, p1, "MAI_X_CLEAVE", (p2.facing_x, p2.facing_y))
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.5, 0.7, 180)
                        ctrl_mgr.rumble_player(1, 0.5, 0.7, 180)
                elif (p2.state == "LISTEN" or getattr(p2, "counter_active", False)) and (hasattr(p2, "is_facing_target") and p2.is_facing_target(p1.wx, p1.wy)):
                    # Postura de Escuta direcional da Ichi: bloqueio frontal perfeito e contra-ataque perfurante automático
                    for _ in range(16):
                        particles.append(SparkParticle(p2.wx, p2.wy, 0.65, color=(140, 200, 255)))
                    banners.append(FloatingBanner("BLIND COUNTER!", p2.wx, p2.wy, wz=1.80, color=(160, 215, 255)))
                    camera.add_shake(8.5)
                    p1.stun(0.40)
                    self._play_sound("parry")
                    if hasattr(p2, "trigger_counter_thrust"):
                        p2.trigger_counter_thrust(p1.wx, p1.wy, banners, particles)
                    hit_c, dead_c = p1.take_hit((p2.facing_x, p2.facing_y), damage=2)
                    if dead_c:
                        winner = "P2_WINS"
                        self.hitstop_timer = 0.14
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            align_finisher_pair(p2, p1, game_map)
                            cinematic_director.trigger_fatal_strike(p2, p1, "BLIND_SPINE_PIERCE", (p2.facing_x, p2.facing_y))
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.6, 0.8, 200)
                        ctrl_mgr.rumble_player(1, 0.6, 0.8, 200)
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
                            align_finisher_pair(p1, p2, game_map)
                            cinematic_director.trigger_fatal_strike(p1, p2, "BLUNT_FALL", p1.slash_dir)
                else:
                    if p2.state == STATE_PARRY and p1.state == "POLE_VAULT":
                        banners.append(FloatingBanner("GUARD CRUSH!", p2.wx, p2.wy, wz=1.8, color=(255, 195, 70)))
                        p2.state = STATE_STUNNED
                        p2.state_timer = 0.65
                    is_ninja = (getattr(p1, "char_type", "") == "ninja" or hasattr(p1, "has_kunai"))
                    if is_ninja:
                        # 1-Hit Kill em Contra-Ataque (adversário em recovery/stunned) ou Costas (backstab)
                        dot_facing = p1.facing_x * p2.facing_x + p1.facing_y * p2.facing_y
                        is_backstab = (dot_facing > 0.20)
                        is_punish = (p2.state in (STATE_RECOVERY, STATE_STUNNED))
                        if is_backstab or is_punish:
                            damage = 2
                        else:
                            damage = 1
                    else:
                        damage = getattr(p1, "hitbox_damage", 2)

                    hit, dead = p2.take_hit(p1.slash_dir, damage=damage)
                    if dead or hit:
                        if hasattr(p1, "on_hit_success"):
                            p1.on_hit_success()
                    if dead:
                        camera.add_shake(14.0)
                        for _ in range(25):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        self.hitstop_timer = 0.12
                        winner = "P1_WINS"
                        self._play_sound("fatal_strike", weapon=getattr(p1, "char_type", None))
                        if cinematic_director:
                            align_finisher_pair(p1, p2, game_map)
                            death_style = _get_death_style_for_attacker(p1, victim=p2)
                            cinematic_director.trigger_fatal_strike(p1, p2, death_style, p1.slash_dir)
                    elif hit:
                        camera.add_shake(7.0)
                        for _ in range(12):
                            particles.append(BloodParticle(p2.wx, p2.wy, 0.6))
                        self._play_sound("sword_slash", weapon=getattr(p1, "char_type", None))
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
            if check_fighter_melee_hit(p2, p1.wx, p1.wy, p1.radius) and _is_vertical_hit(p2, p1):
                p2.hitbox_active = False

                if p1.state == STATE_PARRY and p2.state != "POLE_VAULT":
                    if p2.state == "ZEROSHIKI":
                        # ZEROSHIKI GUARD PIERCE: Causa 1 de dano de estilhaço mesmo contra parry!
                        for _ in range(16):
                            particles.append(SparkParticle(p1.wx, p1.wy, 0.7, color=(255, 200, 100)))
                        for _ in range(8):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.5))
                        if banners is not None:
                            banners.append(FloatingBanner("ZEROSHIKI GUARD PIERCE! -1 HP", p1.wx, p1.wy, wz=1.75, color=(255, 120, 60)))
                        camera.add_shake(10.0)
                        self._play_sound("flesh_cleave")
                        hit, dead = p1.take_hit((p2.facing_x, p2.facing_y), damage=1)
                        if dead:
                            winner = "P2_WINS"
                            self.hitstop_timer = 0.14
                            self._play_sound("fatal_strike")
                            if cinematic_director:
                                cinematic_director.trigger_fatal_strike(p2, p1, "TORSO_BLAST_THRUST", (p2.facing_x, p2.facing_y))
                        else:
                            p1.stun(0.35)
                        if ctrl_mgr:
                            ctrl_mgr.rumble_player(1, 0.6, 0.9, 220)
                            ctrl_mgr.rumble_player(0, 0.8, 1.0, 250)
                    else:
                        for _ in range(12):
                            particles.append(SparkParticle(p1.wx, p1.wy, 0.7))
                        parry_msg = "PARRY GATOTSU!" if p2.state == "GATOTSU_CHARGE" else "PARRY!"
                        banners.append(FloatingBanner(parry_msg, p1.wx, p1.wy, wz=1.7, color=(100, 200, 255)))
                        camera.add_shake(8.0)
                        if hasattr(p1, "on_parry_successful"):
                            p1.on_parry_successful(p2, particles=particles, banners=banners)
                        if hasattr(p2, "on_parried"):
                            p2.on_parried(p1, game_map=game_map, banners=banners, particles=particles)
                        else:
                            p2.stun(0.85)
                        self._play_sound("parry")
                        if ctrl_mgr:
                            ctrl_mgr.rumble_player(1, 0.5, 0.8, 200)
                            ctrl_mgr.rumble_player(0, 0.6, 0.8, 180)
                elif p1.state == "CAPE_FLOURISH":
                    for _ in range(12):
                        particles.append(SparkParticle(p1.wx, p1.wy, 0.65, color=(100, 180, 255)))
                    banners.append(FloatingBanner("CAPE RIPOSTE!", p1.wx, p1.wy, wz=1.75, color=(100, 180, 255)))
                    camera.add_shake(7.0)
                    p2.stun(0.65)
                    p2.wx = max(1.0, min(game_map.cols - 1.0, p2.wx + p1.facing_x * 1.4))
                    p2.wy = max(1.0, min(game_map.rows - 1.0, p2.wy + p1.facing_y * 1.4))
                    self._play_sound("parry")
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(1, 0.5, 0.7, 180)
                        ctrl_mgr.rumble_player(0, 0.5, 0.7, 180)
                elif p1.state == "MAI_DANCE":
                    # Dança Mai da Chiyo: apara o golpe em pirueta, cancela a exaustão e aplica contra-corte de 1 HP
                    for _ in range(16):
                        particles.append(SparkParticle(p1.wx, p1.wy, 0.65, color=(225, 42, 58)))
                    banners.append(FloatingBanner("MAI CONTRA-CORTE!", p1.wx, p1.wy, wz=1.78, color=(235, 55, 75)))
                    camera.add_shake(8.0)
                    if hasattr(p1, "on_mai_parry_success"):
                        p1.on_mai_parry_success(p2, game_map)
                    p2.stun(0.48)
                    p2.wx = max(1.0, min(game_map.cols - 1.0, p2.wx - p2.facing_x * 1.25))
                    p2.wy = max(1.0, min(game_map.rows - 1.0, p2.wy - p2.facing_y * 1.25))
                    self._play_sound("parry")
                    hit_c, dead_c = p2.take_hit((p1.facing_x, p1.facing_y), damage=1)
                    if dead_c:
                        winner = "P1_WINS"
                        self.hitstop_timer = 0.12
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            align_finisher_pair(p1, p2, game_map)
                            cinematic_director.trigger_fatal_strike(p1, p2, "MAI_X_CLEAVE", (p1.facing_x, p1.facing_y))
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(1, 0.5, 0.7, 180)
                        ctrl_mgr.rumble_player(0, 0.5, 0.7, 180)
                elif (p1.state == "LISTEN" or getattr(p1, "counter_active", False)) and (hasattr(p1, "is_facing_target") and p1.is_facing_target(p2.wx, p2.wy)):
                    # Postura de Escuta direcional da Ichi: bloqueio frontal perfeito e contra-ataque perfurante automático
                    for _ in range(16):
                        particles.append(SparkParticle(p1.wx, p1.wy, 0.65, color=(140, 200, 255)))
                    banners.append(FloatingBanner("BLIND COUNTER!", p1.wx, p1.wy, wz=1.80, color=(160, 215, 255)))
                    camera.add_shake(8.5)
                    p2.stun(0.40)
                    self._play_sound("parry")
                    if hasattr(p1, "trigger_counter_thrust"):
                        p1.trigger_counter_thrust(p2.wx, p2.wy, banners, particles)
                    hit_c, dead_c = p2.take_hit((p1.facing_x, p1.facing_y), damage=2)
                    if dead_c:
                        winner = "P1_WINS"
                        self.hitstop_timer = 0.14
                        self._play_sound("fatal_strike")
                        if cinematic_director:
                            align_finisher_pair(p1, p2, game_map)
                            cinematic_director.trigger_fatal_strike(p1, p2, "BLIND_SPINE_PIERCE", (p1.facing_x, p1.facing_y))
                    if ctrl_mgr:
                        ctrl_mgr.rumble_player(0, 0.6, 0.8, 200)
                        ctrl_mgr.rumble_player(1, 0.6, 0.8, 200)
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
                            align_finisher_pair(p2, p1, game_map)
                            cinematic_director.trigger_fatal_strike(p2, p1, "BLUNT_FALL", p2.slash_dir)
                else:
                    if p1.state == STATE_PARRY and p2.state == "POLE_VAULT":
                        banners.append(FloatingBanner("GUARD CRUSH!", p1.wx, p1.wy, wz=1.8, color=(255, 195, 70)))
                        p1.state = STATE_STUNNED
                        p1.state_timer = 0.65
                    is_ninja = getattr(p2, "char_type", "") == "ninja"
                    if is_ninja:
                        dot_facing = p2.facing_x * p1.facing_x + p2.facing_y * p1.facing_y
                        is_backstab = (dot_facing > 0.20)
                        is_punish = (p1.state in (STATE_RECOVERY, STATE_STUNNED))
                        if is_backstab or is_punish:
                            damage = 2
                        else:
                            damage = 1
                    else:
                        damage = getattr(p2, "hitbox_damage", 2)

                    hit, dead = p1.take_hit(p2.slash_dir, damage=damage)
                    if dead or hit:
                        if hasattr(p2, "on_hit_success"):
                            p2.on_hit_success()
                    if dead:
                        camera.add_shake(14.0)
                        for _ in range(25):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        self.hitstop_timer = 0.12
                        winner = "P2_WINS"
                        self._play_sound("fatal_strike", weapon=getattr(p2, "char_type", None))
                        if cinematic_director:
                            align_finisher_pair(p2, p1, game_map)
                            death_style = _get_death_style_for_attacker(p2, victim=p1)
                            cinematic_director.trigger_fatal_strike(p2, p1, death_style, p2.slash_dir)
                    elif hit:
                        camera.add_shake(7.0)
                        for _ in range(12):
                            particles.append(BloodParticle(p1.wx, p1.wy, 0.6))
                        self._play_sound("sword_slash", weapon=getattr(p2, "char_type", None))
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
                    prop.ignite(*fighter.hitbox_center, fighter.hitbox_radius, striker=fighter)
            for proj in projectiles:
                if getattr(proj, "is_active", True) and hasattr(proj, "dir_x") and hasattr(proj, "wx"):
                    prop.ignite(proj.wx, proj.wy, 0.25, striker=getattr(proj, "owner", None))

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

        # Destruição de biombos (ScreenPanel)
        for rock in getattr(game_map, "rocks", []):
            if hasattr(rock, "break_panel") and not getattr(rock, "is_broken", False):
                if world_distance(hx, hy, rock.wx, rock.wy) < (hradius + 0.65):
                    rock.break_panel(fighter.slash_dir, particles)
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
            if getattr(rock, "is_broken", False):
                continue
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
                # Ignora decorações sem colisão física (como grilos, pássaros, névoa e fitas)
                if getattr(lantern, "is_solid", False) or hasattr(lantern, "check_collision") or lantern.__class__.__name__ in ("StoneLantern", "KyotoLantern"):
                    if world_distance(hx, hy, lantern.wx, lantern.wy) < (hradius + getattr(lantern, "radius", 0.45)):
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


