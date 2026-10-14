"""
Diretor Cinematográfico de Combate (Estilo Cinema de Samurai / Kurosawa Noir).
Gerencia congelamento dramático (freeze hitstop), flash preto e branco com sangue vermelho isolado,
e atraso na consumação fatal do golpe (delayed death).
"""
import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT

class CinematicDirector:
    def __init__(self):
        self.is_active = False
        self.freeze_timer = 0.0
        self.bw_flash_timer = 0.0
        self.bw_flash_duration = 0.45
        self.delayed_death_timer = 0.0
        self.pending_corpse = None
        self.pending_boss = None  # chefe cujos ossos desabam depois do congelamento fatal (8.2.5)
        self.corpses = []  # Lista de corpos voxel persistentes na partida

        self.cached_kanji_surf: pygame.Surface | None = None
        self.current_kanji_text: str = ""
        self.current_kanji_subtitle: str = ""
        self.hyakuretsu_attacker = None
        self.hyakuretsu_victim = None
        self.hyakuretsu_victim_origin: tuple[float, float] = (0.0, 0.0)
        self.hyakuretsu_flurry_timer = 0.0
        self.hyakuretsu_pause_timer = 0.0
        self.hyakuretsu_spark_accum = 0.0

        # Benkei: Hoist & Slam
        self.hoist_attacker = None
        self.hoist_victim = None
        self.hoist_timer = 0.0
        self.hoist_slam_timer = 0.0

        # O-Rin: Kamaitachi Mince & Resonance Wind Gale
        self.sonic_attacker = None
        self.sonic_victim = None
        self.sonic_flash_timer = 0.0
        self.sonic_silence_timer = 0.0
        self.sonic_spark_accum = 0.0
        self.sonic_style = ""

        # Joe & Yamato: Windmill Shuriken Decap
        self.joe_attacker = None
        self.joe_victim = None
        self.joe_pin_timer = 0.0
        self.joe_throw_timer = 0.0
        self.shuriken_proj_x = 0.0
        self.shuriken_proj_y = 0.0
        self.shuriken_active = False

        # Julie: Rapier Flurry & Point-blank Flintlock
        self.julie_attacker = None
        self.julie_victim = None
        self.julie_flurry_timer = 0.0
        self.julie_spin_timer = 0.0
        self.julie_bang_timer = 0.0
        self.julie_spark_accum = 0.0

        # Câmera e Enquadramento Anamórfico (CinemaScope 2.39:1)
        self.camera_focus_target: tuple[float, float] = (10.5, 10.5)
        self.cinematic_zoom: float = 1.0
        self.cinematic_zoom_target: float = 1.0
        self.letterbox_prog: float = 0.0
        self.letterbox_target: float = 0.0

        # Animação Dinâmica Sumi-E (Pincelada de Nanquim e Carimbo)
        self.sumie_anim_timer: float = 0.0
        self.inkan_stamped: bool = False

    def _build_kanji_overlay(self, attacker=None, victim=None, death_style: str = "", phrase: tuple | None = None):
        """Gera e cacheia a textura de caligrafia Sumi-E dos kanjis de corte fatal."""
        import random
        from src.ui.fonts import get_text_font

        # Expressões exclusivas por estilo de Fatality (Ciclo 1 + Clássicos)
        style_phrases = {
            "HEADSHOT_EXPLODE": ("一発必中", "IPPATSU HITCHUU — DISPARO MORTAL"),
            "PIRATE_CLEAVE": ("荒波両断", "ARANAMI RYOUDAN — CORTE DO CORSÁRIO"),
            "HYAKURETSU_BODY_EXPLOSION": ("百烈拳", "HYAKURETSU KEN — CEM PUNHOS DE LÓTUS"),
            "WALL_SMASH_FATAL": ("気合衝撃", "KIAI SHOUGEKI — RUGIDO DE CHI"),
            "TRIPLE_SCISSOR_CLEAVE": ("双刃十字", "SOUJIN JUUJI — TESOURA CARMIM"),
            "MAI_X_CLEAVE": ("紅舞必殺", "BENIMAI HISSATSU — DANÇA DA MORTE"),
            "VERTICAL_BISECTION": ("龍槌閃", "RYUU TSUI SEN — FENDA DO DRAGÃO"),
            "DUAL_IMPALE_X_SPREAD": ("二天一流", "NITEN ICHI-RYUU — DUAS LÂMINAS"),
            "ARMORED_HEART_IMPALE": ("金剛貫通", "KONGOU KANTSUU — EMPALAMENTO DE FERRO"),
            "NAGINATA_HOIST_SLAM": ("金剛叩落", "KONGOU TATAKI-OTOSHI — ESMAGAMENTO ADAMANTINO"),
            "SKEWERED_LANCE_FLAG": ("薙刀槍旗", "NAGINATA SOUKI — ESTANDARTE DE GUERRA"),
            "KAMAITACHI_MINCE": ("三弦微塵", "SANGEN MIJIN — RETALHAMENTO DE VÁCUO"),
            "SONIC_SLICER": ("三弦微塵", "SANGEN MIJIN — RETALHAMENTO DE VÁCUO"),
            "RESONANCE_WIND_GALE": ("突風両断", "TOPPUU RYOUDAN — VENTO DECAPITADOR"),
            "RESONANCE_BURST": ("突風両断", "TOPPUU RYOUDAN — VENTO DECAPITADOR"),
            "WINDMILL_SHURIKEN_DECAP": ("風車斬首", "FUUSHA ZANSHU — DECAPITAÇÃO DA FUMAÇA"),
            "RAPIER_FLURRY_POINTBLANK": ("零距離乱撃", "REIKYORI RANGEKI — DISPARO À QUEIMA-ROUPA"),
        }
        # Pool de expressões clássicas de cinema samurai
        phrases = [
            ("一刀両断", "ITTOU RYOUDAN — CORTE CERTEIRO"),
            ("決闘終焉", "KETTOU SHUUEN — FIM DO DUELO"),
            ("神速必殺", "SHINSOKU HISSATSU — GOLPE DIVINO"),
            ("生死一瞬", "SEISHI ISSHUN — VIDA E MORTE"),
        ]
        kanji_str, sub_str = phrase or style_phrases.get(death_style) or random.choice(phrases)
        self.current_kanji_text = kanji_str
        self.current_kanji_subtitle = sub_str

        font_kanji = get_text_font(72)
        font_sub = get_text_font(18)

        # Renderizar textos
        kanji_shadow = font_kanji.render(kanji_str, True, (12, 12, 16))
        kanji_main = font_kanji.render(kanji_str, True, (245, 245, 240))
        sub_shadow = font_sub.render(sub_str, True, (12, 12, 16))
        sub_main = font_sub.render(sub_str, True, (225, 60, 50))

        kw = max(kanji_main.get_width() + 40, sub_main.get_width() + 50)
        kh = kanji_main.get_height() + sub_main.get_height() + 24

        overlay = pygame.Surface((kw, kh), pygame.SRCALPHA)

        # Selo tradicional de nanquim (Inkan estilizado vermelho à esquerda)
        seal_rect = pygame.Rect(4, 12, 6, kh - 24)
        pygame.draw.rect(overlay, (190, 40, 40, 220), seal_rect, border_radius=2)

        # Desenhar kanjis com sombra de alto contraste
        kx = (kw - kanji_main.get_width()) // 2
        overlay.blit(kanji_shadow, (kx + 3, 6))
        overlay.blit(kanji_main, (kx, 4))

        # Desenhar subtítulo
        sx = (kw - sub_main.get_width()) // 2
        sy = kanji_main.get_height() + 8
        overlay.blit(sub_shadow, (sx + 2, sy + 2))
        overlay.blit(sub_main, (sx, sy))

        self.cached_kanji_surf = overlay

    def trigger_fatal_strike(self, attacker, victim, death_style: str, slash_dir: tuple[float, float]):
        """Dispara a sequência de cinema samurai no golpe letal."""
        from src.audio.sound_manager import get_sound_manager
        get_sound_manager().play_death_music(fadeout_ms=350)

        if getattr(victim, "is_boss", False):
            from src.i18n import t
            from src.audio.sound_events import SoundEvent
            self.is_active = True
            self.freeze_timer = 0.5
            self.bw_flash_timer = 0.7
            self.delayed_death_timer = 0.6
            victim.is_alive = False
            victim.state = "DYING_FREEZE"
            victim.state_timer = 0.5
            self._build_kanji_overlay(attacker, victim, death_style, phrase=("餓者髑髏", t("boss_defeated")))
            self.pending_corpse = None
            self.pending_boss = victim
            if attacker is not None and victim is not None:
                self.camera_focus_target = ((attacker.wx + victim.wx) / 2.0, (attacker.wy + victim.wy) / 2.0)
            elif victim is not None:
                self.camera_focus_target = (victim.wx, victim.wy)
            self.cinematic_zoom_target = 1.45
            self.letterbox_target = 1.0
            self.sumie_anim_timer = 0.0
            self.inkan_stamped = False
            get_sound_manager().play(SoundEvent.HEARTBEAT, volume_scale=1.0)
            return

        self.is_active = True

        # Configurar enquadramento dinâmico, zoom e batimento cardíaco
        if attacker is not None and victim is not None:
            self.camera_focus_target = ((attacker.wx + victim.wx) / 2.0, (attacker.wy + victim.wy) / 2.0)
        elif victim is not None:
            self.camera_focus_target = (victim.wx, victim.wy)
        else:
            self.camera_focus_target = (10.5, 10.5)

        self.cinematic_zoom_target = 1.65
        self.letterbox_target = 1.0
        self.sumie_anim_timer = 0.0
        self.inkan_stamped = False

        from src.audio.sound_manager import get_sound_manager
        from src.audio.sound_events import SoundEvent
        get_sound_manager().play(SoundEvent.HEARTBEAT, volume_scale=1.0)

        # Reset timers
        self.hyakuretsu_attacker = None
        self.hyakuretsu_victim = None
        self.hoist_attacker = None
        self.hoist_victim = None
        self.sonic_attacker = None
        self.sonic_victim = None
        self.joe_attacker = None
        self.joe_victim = None
        self.julie_attacker = None
        self.julie_victim = None

        if death_style == "HYAKURETSU_BODY_EXPLOSION":
            self.hyakuretsu_attacker = attacker
            self.hyakuretsu_victim = victim
            self.hyakuretsu_victim_origin = (victim.wx, victim.wy)
            self.hyakuretsu_flurry_timer = 1.05
            self.hyakuretsu_pause_timer = 0.65
            self.hyakuretsu_spark_accum = 0.0
            self.freeze_timer = 1.70
            self.bw_flash_duration = 2.15
            self.bw_flash_timer = 2.15
            self.delayed_death_timer = 1.70
            if attacker is not None:
                attacker.hyakuretsu_phase = "FLURRY"
                attacker.hyakuretsu_clock = 0.0
                attacker.hyakuretsu_punch_count = 0
                attacker.set_facing(victim.wx, victim.wy)

        elif death_style == "NAGINATA_HOIST_SLAM":
            # Benkei: empala, ergue no ar pela haste da naginata em arco monumental, e esmaga violentamente no chão!
            self.hoist_attacker = attacker
            self.hoist_victim = victim
            self.hoist_timer = 0.70
            self.hoist_slam_timer = 0.35
            self.freeze_timer = 1.05
            self.bw_flash_duration = 1.50
            self.bw_flash_timer = 1.50
            self.delayed_death_timer = 1.05
            if attacker is not None:
                attacker.set_facing(victim.wx, victim.wy)
                attacker.state = "ATTACK"
                attacker.state_timer = 1.05

        elif death_style in ("KAMAITACHI_MINCE", "SONIC_SLICER", "RESONANCE_WIND_GALE", "RESONANCE_BURST"):
            # O-Rin:
            # Primário (KAMAITACHI_MINCE): Primeiro impacto sangra o tórax, depois rajada de Kamaitachis retalha em pedaços minúsculos!
            # Secundário (RESONANCE_WIND_GALE): Lâmina sônica de vento corta em dois e leva a metade superior embora em alta velocidade!
            self.sonic_attacker = attacker
            self.sonic_victim = victim
            self.sonic_style = death_style
            self.sonic_flash_timer = 0.28
            self.sonic_silence_timer = 0.77
            self.sonic_spark_accum = 0.0
            self.freeze_timer = 1.05
            self.bw_flash_duration = 1.50
            self.bw_flash_timer = 1.50
            self.delayed_death_timer = 1.05
            if attacker is not None:
                attacker.set_facing(victim.wx, victim.wy)
                attacker.state = "ATTACK"
                attacker.state_timer = 1.05

        elif death_style == "WINDMILL_SHURIKEN_DECAP":
            # Joe & Yamato: Yamato imobiliza a vítima, Joe prepara e arremessa a shuriken moinho gigante!
            self.joe_attacker = attacker
            self.joe_victim = victim
            self.joe_pin_timer = 0.70
            self.joe_throw_timer = 0.45
            self.freeze_timer = 1.15
            self.bw_flash_duration = 1.55
            self.bw_flash_timer = 1.55
            self.delayed_death_timer = 1.15
            self.shuriken_active = False
            if attacker is not None:
                attacker.set_facing(victim.wx, victim.wy)

        elif death_style == "RAPIER_FLURRY_POINTBLANK":
            # Julie: 24 estocadas de rapieira, pirueta elegante e disparo de pistola à queima-roupa!
            self.julie_attacker = attacker
            self.julie_victim = victim
            self.julie_flurry_timer = 0.85
            self.julie_spin_timer = 0.35
            self.julie_bang_timer = 0.28
            self.julie_spark_accum = 0.0
            self.freeze_timer = 1.48
            self.bw_flash_duration = 1.90
            self.bw_flash_timer = 1.90
            self.delayed_death_timer = 1.48
            if attacker is not None:
                attacker.set_facing(victim.wx, victim.wy)
                attacker.state = "ATTACK"
                attacker.state_timer = 0.85

        else:
            self.bw_flash_duration = 0.45
            self.freeze_timer = 0.38
            self.bw_flash_timer = 0.50
            self.delayed_death_timer = 0.42

        # Deixar a vítima no estado congelado de morte iminente
        victim.is_alive = False
        victim.state = "DYING_FREEZE"
        victim.state_timer = self.delayed_death_timer + 0.08

        # Gerar o banner de Kanji Kurosawa Sumi-E em cache
        self._build_kanji_overlay(attacker, victim, death_style)

        # Preparar o corpo voxel que se manifestará após o atraso
        from src.entities.voxel_corpse import VoxelCorpse
        self.pending_corpse = VoxelCorpse(victim, death_style, slash_dir)

    def update(self, dt: float, game_map, particles: list = None):
        """Atualiza os temporizadores cinematográficos e a física dos corpos."""
        import random
        if self.freeze_timer > 0:
            self.freeze_timer = max(0.0, self.freeze_timer - dt)

        if self.bw_flash_timer > 0:
            self.bw_flash_timer = max(0.0, self.bw_flash_timer - dt)

        self.sumie_anim_timer += dt

        # Suavização da barra anamórfica e zoom
        self.letterbox_prog += (self.letterbox_target - self.letterbox_prog) * min(1.0, dt * 5.0)
        self.cinematic_zoom += (self.cinematic_zoom_target - self.cinematic_zoom) * min(1.0, dt * 4.5)

        # Impacto do carimbo Inkan com poeira carmim
        if self.sumie_anim_timer >= 0.18 and not self.inkan_stamped:
            self.inkan_stamped = True
            if particles is not None:
                from src.effects.particles import SparkParticle
                fx, fy = self.camera_focus_target
                for _ in range(6):
                    particles.append(SparkParticle(
                        fx + random.uniform(-0.16, 0.16),
                        fy + random.uniform(-0.16, 0.16),
                        random.uniform(0.6, 1.1),
                        color=random.choice([(220, 40, 40), (255, 60, 50), (180, 20, 20)])
                    ))

        # 1. Hyakuretsu Ken (Ren)
        if self.hyakuretsu_flurry_timer > 0:
            self.hyakuretsu_flurry_timer = max(0.0, self.hyakuretsu_flurry_timer - dt)
            atk = self.hyakuretsu_attacker
            vic = self.hyakuretsu_victim
            if atk is not None:
                atk.hyakuretsu_phase = "FLURRY"
                atk.hyakuretsu_clock = getattr(atk, "hyakuretsu_clock", 0.0) + dt
            if vic is not None:
                ox, oy = self.hyakuretsu_victim_origin
                vic.wx = ox + random.uniform(-0.06, 0.06)
                vic.wy = oy + random.uniform(-0.06, 0.06)
            self.hyakuretsu_spark_accum += dt
            while self.hyakuretsu_spark_accum >= 0.025:
                self.hyakuretsu_spark_accum -= 0.025
                if atk is not None:
                    atk.hyakuretsu_punch_count = getattr(atk, "hyakuretsu_punch_count", 0) + 1
                if particles is not None and vic is not None:
                    from src.effects.particles import SparkParticle, BloodParticle
                    ox, oy = self.hyakuretsu_victim_origin
                    px = ox + random.uniform(-0.22, 0.22)
                    py = oy + random.uniform(-0.22, 0.22)
                    pz = random.uniform(0.28, 0.92)
                    particles.append(SparkParticle(px, py, pz, color=random.choice([(255, 225, 90), (255, 165, 40), (255, 250, 190)])))
                    if random.random() < 0.55:
                        particles.append(BloodParticle(px, py, pz))
            if self.hyakuretsu_flurry_timer <= 0 and atk is not None:
                atk.hyakuretsu_phase = "PAUSE"
                if vic is not None:
                    vic.wx, vic.wy = self.hyakuretsu_victim_origin

        elif self.hyakuretsu_pause_timer > 0:
            self.hyakuretsu_pause_timer = max(0.0, self.hyakuretsu_pause_timer - dt)
            atk = self.hyakuretsu_attacker
            vic = self.hyakuretsu_victim
            if atk is not None:
                atk.hyakuretsu_phase = "PAUSE"
                atk.hyakuretsu_clock = getattr(atk, "hyakuretsu_clock", 0.0) + dt
            if vic is not None:
                ox, oy = self.hyakuretsu_victim_origin
                vic.wx = ox + random.uniform(-0.025, 0.025)
                vic.wy = oy + random.uniform(-0.025, 0.025)
                if particles is not None and random.random() < 0.45:
                    from src.effects.particles import SparkParticle
                    particles.append(SparkParticle(
                        ox + random.uniform(-0.14, 0.14),
                        oy + random.uniform(-0.14, 0.14),
                        random.uniform(0.35, 0.85),
                        color=(255, 80, 50)
                    ))
            if self.hyakuretsu_pause_timer <= 0 and atk is not None:
                atk.hyakuretsu_phase = None

        # 2. Benkei Hoist & Slam
        if self.hoist_timer > 0:
            self.hoist_timer = max(0.0, self.hoist_timer - dt)
            atk = self.hoist_attacker
            vic = self.hoist_victim
            if atk is not None and vic is not None:
                t = 1.0 - (self.hoist_timer / 0.70)
                # Benkei empala e ergue no ar em arco monumental
                atk.state = "ATTACK"
                atk.state_timer = 0.30
                vic.wx = atk.wx + atk.facing_x * (1.1 - 0.45 * t)
                vic.wy = atk.wy + atk.facing_y * (1.1 - 0.45 * t)
                vic.wz = 0.25 + 1.85 * math.sin(t * math.pi * 0.5)
                if particles is not None and random.random() < 0.70:
                    from src.effects.particles import BloodParticle
                    particles.append(BloodParticle(vic.wx, vic.wy, max(0.2, vic.wz - 0.15)))

        elif self.hoist_slam_timer > 0:
            self.hoist_slam_timer = max(0.0, self.hoist_slam_timer - dt)
            atk = self.hoist_attacker
            vic = self.hoist_victim
            if atk is not None and vic is not None:
                s = 1.0 - (self.hoist_slam_timer / 0.35)
                # Benkei desce a naginata com força sísmica
                atk.state = "ATTACK"
                atk.state_timer = 0.05
                vic.wx = atk.wx + atk.facing_x * (0.65 + 0.95 * s)
                vic.wy = atk.wy + atk.facing_y * (0.65 + 0.95 * s)
                vic.wz = max(0.0, 2.10 * ((1.0 - s) ** 2))
                if vic.wz <= 0.05 and particles is not None:
                    from src.effects.particles import BloodParticle, SparkParticle
                    for _ in range(12):
                        particles.append(BloodParticle(vic.wx, vic.wy, 0.25))
                    for _ in range(6):
                        particles.append(SparkParticle(vic.wx, vic.wy, 0.1, color=(255, 200, 100)))

        # 3. O-Rin (Kamaitachi Mince & Resonance Wind Gale)
        if self.sonic_flash_timer > 0:
            self.sonic_flash_timer = max(0.0, self.sonic_flash_timer - dt)
            vic = self.sonic_victim
            # Impacto inicial: sangramento do tórax
            if vic is not None and particles is not None:
                from src.effects.particles import BloodParticle, SparkParticle
                particles.append(BloodParticle(vic.wx, vic.wy, 0.65))
                particles.append(SparkParticle(vic.wx + random.uniform(-0.15, 0.15),
                                               vic.wy + random.uniform(-0.15, 0.15),
                                               0.65, color=(120, 240, 255)))
        elif self.sonic_silence_timer > 0:
            self.sonic_silence_timer = max(0.0, self.sonic_silence_timer - dt)
            atk = self.sonic_attacker
            vic = self.sonic_victim
            if atk is not None:
                atk.state = "ATTACK"
                atk.state_timer = 0.12
            if vic is not None and particles is not None:
                from src.effects.particles import SparkParticle, BloodParticle
                # Rajada contínua de lâminas Kamaitachi cortando o rival
                if random.random() < 0.75:
                    particles.append(SparkParticle(
                        vic.wx + random.uniform(-0.35, 0.35),
                        vic.wy + random.uniform(-0.35, 0.35),
                        random.uniform(0.25, 0.85),
                        color=random.choice([(90, 235, 255), (255, 120, 180), (220, 255, 255)])
                    ))
                    particles.append(BloodParticle(vic.wx + random.uniform(-0.15, 0.15),
                                                   vic.wy + random.uniform(-0.15, 0.15),
                                                   random.uniform(0.3, 0.75)))

        # 4. Joe & Yamato Windmill Shuriken
        if self.joe_pin_timer > 0:
            self.joe_pin_timer = max(0.0, self.joe_pin_timer - dt)
            atk = self.joe_attacker
            vic = self.joe_victim
            if atk is not None and hasattr(atk, "dog") and atk.dog is not None and vic is not None:
                # Yamato morde e imobiliza o adversário no solo
                atk.dog.wx = vic.wx - atk.facing_x * 0.28
                atk.dog.wy = vic.wy - atk.facing_y * 0.28
                atk.dog.state = "CHARGE"
                if particles is not None and random.random() < 0.50:
                    from src.effects.particles import BloodParticle
                    particles.append(BloodParticle(vic.wx, vic.wy, 0.35))
            if atk is not None:
                atk.state = "IDLE"
                atk.set_facing(vic.wx, vic.wy)

        elif self.joe_throw_timer > 0:
            self.joe_throw_timer = max(0.0, self.joe_throw_timer - dt)
            atk = self.joe_attacker
            vic = self.joe_victim
            tp = 1.0 - (self.joe_throw_timer / 0.45)
            if atk is not None and vic is not None:
                atk.state = "ATTACK"
                atk.state_timer = 0.20
                self.shuriken_active = True
                # Trajetória da shuriken gigante de Joe até a vítima
                self.shuriken_proj_x = atk.wx + (vic.wx - atk.wx) * min(1.0, tp * 1.4)
                self.shuriken_proj_y = atk.wy + (vic.wy - atk.wy) * min(1.0, tp * 1.4)

                # Shuriken moinho girando com 4 pás em faíscas de aço
                if particles is not None:
                    from src.effects.particles import SparkParticle
                    for ang in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
                        cur_ang = self.sumie_anim_timer * 32.0 + ang
                        sx = self.shuriken_proj_x + math.cos(cur_ang) * 0.32
                        sy = self.shuriken_proj_y + math.sin(cur_ang) * 0.32
                        particles.append(SparkParticle(sx, sy, 0.72, color=(225, 235, 245)))

                # Yamato salta para o lado antes do golpe decapitar
                if hasattr(atk, "dog") and atk.dog is not None and tp > 0.45:
                    atk.dog.wx += -atk.facing_y * 1.6 * dt
                    atk.dog.wy += atk.facing_x * 1.6 * dt
                    atk.dog.state = "FOLLOW"

        # 5. Julie Rapier Flurry & Point-blank
        if self.julie_flurry_timer > 0:
            self.julie_flurry_timer = max(0.0, self.julie_flurry_timer - dt)
            atk = self.julie_attacker
            vic = self.julie_victim
            if atk is not None:
                # Animação ativa contínua de estocada (16Hz)
                atk.state = "ATTACK"
                atk.state_timer = 0.06
            self.julie_spark_accum += dt
            while self.julie_spark_accum >= 0.032:
                self.julie_spark_accum -= 0.032
                if vic is not None and particles is not None:
                    from src.effects.particles import SparkParticle, BloodParticle
                    particles.append(SparkParticle(
                        vic.wx + random.uniform(-0.16, 0.16),
                        vic.wy + random.uniform(-0.16, 0.16),
                        random.uniform(0.40, 0.85),
                        color=(190, 230, 255)
                    ))
                    if random.random() < 0.65:
                        particles.append(BloodParticle(vic.wx, vic.wy, random.uniform(0.4, 0.75)))

        elif self.julie_spin_timer > 0:
            self.julie_spin_timer = max(0.0, self.julie_spin_timer - dt)
            atk = self.julie_attacker
            vic = self.julie_victim
            if atk is not None and vic is not None:
                sp = 1.0 - (self.julie_spin_timer / 0.35)
                # Pirueta elegante de capa girando 360° para as costas do oponente
                atk.state = "CAPE_FLOURISH"
                atk.state_timer = 0.20
                target_x = vic.wx - vic.facing_x * 0.45
                target_y = vic.wy - vic.facing_y * 0.45
                atk.wx += (target_x - atk.wx) * min(1.0, dt * 8.0)
                atk.wy += (target_y - atk.wy) * min(1.0, dt * 8.0)
                atk.set_facing(vic.wx, vic.wy)

        elif self.julie_bang_timer > 0:
            first_frame = (self.julie_bang_timer >= 0.27)
            self.julie_bang_timer = max(0.0, self.julie_bang_timer - dt)
            atk = self.julie_attacker
            vic = self.julie_victim
            if atk is not None and vic is not None:
                atk.state = "IDLE"
                atk.set_facing(vic.wx, vic.wy)
                if first_frame:
                    from src.audio.sound_manager import get_sound_manager
                    from src.audio.sound_events import SoundEvent
                    get_sound_manager().play(SoundEvent.SWORD_CLASH, volume_scale=1.0)
                    if particles is not None:
                        from src.effects.particles import SmokeParticle, SparkParticle
                        for _ in range(5):
                            particles.append(SmokeParticle(atk.wx + atk.facing_x * 0.25,
                                                           atk.wy + atk.facing_y * 0.25,
                                                           wz=0.72, color=(225, 225, 235), radius=0.75))
                        for _ in range(8):
                            particles.append(SparkParticle(vic.wx, vic.wy, 0.72, color=(255, 195, 60)))

        if self.delayed_death_timer > 0:
            self.delayed_death_timer = max(0.0, self.delayed_death_timer - dt)
            if self.delayed_death_timer <= 0 and self.pending_boss is not None:
                self.pending_boss.begin_collapse()
                self.pending_boss = None
                self.cinematic_zoom_target = 1.0
                self.letterbox_target = 0.0
            if self.delayed_death_timer <= 0 and self.pending_corpse:
                # O suspense acabou: O corpo se parte e o geiser explode!
                if self.pending_corpse.victim:
                    if self.hyakuretsu_victim is not None:
                        self.pending_corpse.victim.wx, self.pending_corpse.victim.wy = self.hyakuretsu_victim_origin
                    self.pending_corpse.victim.state = "CORPSE_SLICED"
                if self.hyakuretsu_attacker is not None:
                    self.hyakuretsu_attacker.hyakuretsu_phase = None
                self.corpses.append(self.pending_corpse)
                self.pending_corpse = None
                self.cinematic_zoom_target = 1.0
                self.letterbox_target = 0.0

        # Transição e encerramento do diretor cinematográfico
        if self.delayed_death_timer <= 0 and self.freeze_timer <= 0 and self.bw_flash_timer <= 0 and self.letterbox_prog <= 0.02:
            self.is_active = False
            self.letterbox_prog = 0.0
            self.cinematic_zoom = 1.0

        # Atualizar todos os corpos fatiados existentes
        for corpse in self.corpses:
            corpse.update(dt, game_map, particles)

    def is_frozen(self) -> bool:
        """Verifica se a simulação normal deve congelar no frame dramático."""
        return (
            self.freeze_timer > 0
            or self.delayed_death_timer > 0
            or self.hyakuretsu_flurry_timer > 0
            or self.hoist_timer > 0
            or self.sonic_silence_timer > 0
            or self.joe_pin_timer > 0
            or self.julie_flurry_timer > 0
        )

    def apply_camera(self, camera, dt: float):
        """Aplica enquadramento cinematográfico, zoom dramático e rotação suave de azimute."""
        # Suavização contínua do zoom
        self.cinematic_zoom += (self.cinematic_zoom_target - self.cinematic_zoom) * min(1.0, dt * 4.5)
        camera.zoom = self.cinematic_zoom

        # Suavização da barra anamórfica
        self.letterbox_prog += (self.letterbox_target - self.letterbox_prog) * min(1.0, dt * 5.0)

        # Foco dinâmico no ponto de ação fatal
        camera.update(self.camera_focus_target[0], self.camera_focus_target[1], dt)

        # Rotação lenta de azimute durante o congelamento dramático (0.18 rad/s)
        if self.is_frozen():
            camera.rotate(0.18 * dt)

    def render_letterbox(self, surface: pygame.Surface):
        """Desenha barras pretas CinemaScope 2.39:1 (1280x540) com filete dourado sutil."""
        if self.letterbox_prog <= 0.005:
            return
        bar_h = int(SCREEN_HEIGHT * 0.125 * self.letterbox_prog)
        if bar_h > 0:
            pygame.draw.rect(surface, (4, 4, 6), (0, 0, SCREEN_WIDTH, bar_h))
            pygame.draw.rect(surface, (4, 4, 6), (0, SCREEN_HEIGHT - bar_h, SCREEN_WIDTH, bar_h))
            border_alpha = int(min(255, self.letterbox_prog * 150))
            if border_alpha > 0:
                edge_line = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
                edge_line.fill((180, 150, 90, border_alpha))
                surface.blit(edge_line, (0, bar_h - 1))
                surface.blit(edge_line, (0, SCREEN_HEIGHT - bar_h))

    def apply_cinematic_filter(self, surface: pygame.Surface):
        """
        Aplica o efeito Kurosawa Noir e CinemaScope Anamórfico (2.39:1):
        - Desatura a tela para preto e branco de alto contraste mantendo os tons vermelhos vivos (sangue).
        - Vinheta cinematográfica periférica.
        - Pincelada dinâmica Sumi-E em nanquim diagonal.
        - Ideogramas Kanji com impacto de escala.
        - Barras pretas anamórficas 2.39:1.
        """
        if self.bw_flash_timer > 0:
            alpha = int(min(255, (self.bw_flash_timer / self.bw_flash_duration) * 220))
            if alpha > 0:
                # Máscara monocromática estilizada
                bw_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                bw_overlay.fill((30, 30, 35, alpha))
                surface.blit(bw_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

                # Vinheta escura nas bordas estilo película clássica
                vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(vignette, (10, 10, 15, int(alpha * 0.45)), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), width=35)
                surface.blit(vignette, (0, 0))

        # Pincelada e Kanjis Sumi-E (desenhados durante o flash)
        if self.bw_flash_timer > 0 and self.cached_kanji_surf is not None:
            kanji_alpha = int(min(255, (self.bw_flash_timer / self.bw_flash_duration) * 255))
            self.cached_kanji_surf.set_alpha(kanji_alpha)
            cx = SCREEN_WIDTH // 2
            cy = 104

            # Traço de pincelada rápida (diagonal slash) enquanto timer < 0.28s
            if self.sumie_anim_timer < 0.28:
                slash_prog = min(1.0, self.sumie_anim_timer / 0.18)
                sw = int(680 * slash_prog)
                if sw > 10:
                    start_x = cx - 340
                    start_y = cy - 24
                    end_x = start_x + sw
                    end_y = start_y + int(sw * 0.08)

                    brush_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    pygame.draw.line(brush_surf, (14, 14, 18, int(kanji_alpha * 0.85)), (start_x, start_y), (end_x, end_y), 18)
                    pygame.draw.line(brush_surf, (24, 24, 28, int(kanji_alpha * 0.95)), (start_x + 8, start_y - 3), (end_x, end_y - 3), 8)
                    pygame.draw.line(brush_surf, (190, 35, 35, int(kanji_alpha * 0.65)), (start_x + 16, start_y + 4), (end_x, end_y + 4), 3)
                    surface.blit(brush_surf, (0, 0))

            # Kanji com impacto de escala (1.30x -> 1.0x)
            kanji_drop_t = min(1.0, self.sumie_anim_timer / 0.16)
            scale = 1.0 + 0.30 * ((1.0 - kanji_drop_t) ** 2)

            orig_w, orig_h = self.cached_kanji_surf.get_size()
            target_w = max(1, int(orig_w * scale))
            target_h = max(1, int(orig_h * scale))

            if scale > 1.01:
                scaled_surf = pygame.transform.smoothscale(self.cached_kanji_surf, (target_w, target_h))
            else:
                scaled_surf = self.cached_kanji_surf

            scaled_surf.set_alpha(kanji_alpha)
            kx = cx - target_w // 2
            ky = cy - target_h // 2
            surface.blit(scaled_surf, (kx, ky))

        # Barras de Letterbox CinemaScope Anamórfico 2.39:1
        self.render_letterbox(surface)

    def reset_round(self):
        """Limpa estados transitórios mantendo manchas de sangue se desejado."""
        if self.hyakuretsu_attacker is not None:
            self.hyakuretsu_attacker.hyakuretsu_phase = None
        self.is_active = False
        self.freeze_timer = 0.0
        self.bw_flash_timer = 0.0
        self.delayed_death_timer = 0.0
        self.hyakuretsu_attacker = None
        self.hyakuretsu_victim = None
        self.hyakuretsu_flurry_timer = 0.0
        self.hyakuretsu_pause_timer = 0.0
        self.hoist_attacker = None
        self.hoist_victim = None
        self.hoist_timer = 0.0
        self.hoist_slam_timer = 0.0
        self.sonic_attacker = None
        self.sonic_victim = None
        self.sonic_flash_timer = 0.0
        self.sonic_silence_timer = 0.0
        self.sonic_spark_accum = 0.0
        self.sonic_style = ""
        self.joe_attacker = None
        self.joe_victim = None
        self.joe_pin_timer = 0.0
        self.joe_throw_timer = 0.0
        self.shuriken_proj_x = 0.0
        self.shuriken_proj_y = 0.0
        self.shuriken_active = False
        self.julie_attacker = None
        self.julie_victim = None
        self.julie_flurry_timer = 0.0
        self.julie_spin_timer = 0.0
        self.julie_bang_timer = 0.0
        self.julie_spark_accum = 0.0
        self.pending_corpse = None
        self.pending_boss = None
        self.corpses.clear()
        self.cached_kanji_surf = None
        self.current_kanji_text = ""
        self.current_kanji_subtitle = ""
        self.camera_focus_target = (10.5, 10.5)
        self.cinematic_zoom = 1.0
        self.cinematic_zoom_target = 1.0
        self.letterbox_prog = 0.0
        self.letterbox_target = 0.0
        self.sumie_anim_timer = 0.0
        self.inkan_stamped = False
