"""
Diretor Cinematográfico de Combate (Estilo Cinema de Samurai / Kurosawa Noir).
Gerencia congelamento dramático (freeze hitstop), flash preto e branco com sangue vermelho isolado,
e atraso na consumação fatal do golpe (delayed death).
"""
import math
import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT

class CinematicDirector:
    IMPACT_FREEZE_DURATION = 0.18  # Passo 1: pausa dramática de impacto congelado no contato fatal
    CAMERA_SWOOP_DURATION = 0.42   # Passo 2: zoom-in e giro/roll para o melhor ângulo enquanto o tempo segue congelado
    CAMERA_SETUP_DURATION = IMPACT_FREEZE_DURATION + CAMERA_SWOOP_DURATION  # 0.60s totais de tempo congelado antes do golpe
    FINISHER_SPEED_SCALE = 0.85    # Passo 3 & 4: descongelamento e execução do finisher no ângulo fechado

    def __init__(self):
        self.is_active = False
        self.camera_setup_timer = 0.0
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
        self.joe_sound_played = False
        self.joe_throw_sound_played = False

        # Julie: Rapier Flurry & Point-blank Flintlock
        self.julie_attacker = None
        self.julie_victim = None
        self.julie_flurry_timer = 0.0
        self.julie_spin_timer = 0.0
        self.julie_bang_timer = 0.0
        self.julie_spark_accum = 0.0

        # Goro: Kuwa Skull Cleave
        self.goro_attacker = None
        self.goro_victim = None
        self.goro_windup_timer = 0.0
        self.goro_cleaved_timer = 0.0
        self.goro_sound_played = False

        # Coreografia universal de golpe final no ângulo fechado (após descongelar o tempo)
        self.finisher_attacker = None
        self.finisher_victim = None
        self.finisher_style: str = ""
        self.finisher_strike_timer: float = 0.0
        self.finisher_strike_duration: float = 0.52
        self.finisher_impact_played: bool = False

        # Câmera 3-Fases e Enquadramento Anamórfico (CinemaScope 2.39:1)
        self.camera_focus_target: tuple[float, float] = (10.5, 10.5)
        self.cinematic_zoom: float = 1.0
        self.cinematic_zoom_target: float = 1.0
        self.letterbox_prog: float = 0.0
        self.letterbox_target: float = 0.0
        self.optimal_azimuth: float = 0.55
        self.orbit_dir: float = 1.0
        self.camera_roll_deg: float = 0.0
        self._cam_start_captured: bool = False
        self._cam_start_wx: float = 10.5
        self._cam_start_wy: float = 10.5
        self._cam_start_zoom: float = 1.0
        self._cam_start_azimuth: float = 0.0
        self._cam_setup_elapsed: float = 0.0

        # Animação Dinâmica Sumi-E (Pincelada de Nanquim e Carimbo)
        self.sumie_anim_timer: float = 0.0
        self.inkan_stamped: bool = False

        # Pool de superfícies reutilizáveis (zero-alloc durante o filtro cinematográfico)
        self._bw_overlay: pygame.Surface | None = None
        self._vignette_surf: pygame.Surface | None = None
        self._brush_surf: pygame.Surface | None = None
        self._edge_line: pygame.Surface | None = None
        self._last_vignette_alpha: int = -1

    @staticmethod
    def compute_optimal_finisher_azimuth(attacker, victim, slash_dir: tuple[float, float] = (1.0, 0.0)) -> float:
        """
        Calcula o melhor ângulo 3/4 lateral (em radianos positivos) para enquadrar o golpe fatal
        sem que um combatente oclua o outro na projeção isométrica.
        """
        if attacker is not None and victim is not None:
            dx = victim.wx - attacker.wx
            dy = victim.wy - attacker.wy
        else:
            dx, dy = slash_dir
        if math.hypot(dx, dy) < 1e-4:
            dx, dy = 1.0, 0.0
        # Avalia candidatos de azimute entre 22° e 62° e escolhe o que maximiza a separação horizontal na tela
        best_az = 0.52
        best_score = -1.0
        for deg in (24, 32, 40, 48, 56, 64):
            az = math.radians(deg)
            c, s = math.cos(az), math.sin(az)
            rx = dx * c - dy * s
            ry = dx * s + dy * c
            horiz_sep = abs(rx - ry)
            depth_sep = abs(rx + ry)
            # Equilíbrio ideal 3/4: forte separação horizontal (~80%) com leve profundidade (~20%)
            score = horiz_sep - 0.35 * abs(depth_sep - 0.35 * horiz_sep)
            if score > best_score:
                best_score = score
                best_az = az
        return best_az

    def get_finisher_phase(self) -> str:
        """Retorna a fase atual da câmera de finalização (Pilar 8): IMPACT_FREEZE, CAMERA_SWOOP, EXECUTION ou INACTIVE."""
        if not self.is_active:
            return "INACTIVE"
        if self.camera_setup_timer > self.CAMERA_SWOOP_DURATION:
            return "IMPACT_FREEZE"
        if self.camera_setup_timer > 0.0:
            return "CAMERA_SWOOP"
        return "EXECUTION"

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
            "WINDMILL_SHURIKEN_DECAP": ("風車斬首", "FUUSHA ZANSHU — DECAPITAÇÃO DA SHURIKEN MOINHO"),
            "RAPIER_FLURRY_POINTBLANK": ("零距離乱撃", "REIKYORI RANGEKI — DISPARO À QUEIMA-ROUPA"),
            # Ciclo 3 Fatalities
            "KUWA_SKULL_CLEAVE": ("鍬頭砕断", "KUWA TOUSAIDAN — CLIVAGEM CRANIANA DA ENXADA"),
            "EARTH_STOMP_CRUSH": ("地鳴踏潰", "JINARI FUMITSUBUSHI — PISOTÃO ESMAGADOR DA TERRA"),
            "BLIND_CAROTID_SLICE": ("盲刃頚断", "MOUJIN KEIDAN — CORTE CEGO DA CARÓTIDA"),
            "BLIND_SPINE_PIERCE": ("盲背心貫", "MOUHAI SHINKAN — PERFURAÇÃO CEGA DA ESPINHA"),
            "HEART_IMPALE_LUNGE": ("牙突心貫", "GATOTSU SHINKAN — ESTOCADA DO LOBO DE MIBU"),
            "TORSO_BLAST_THRUST": ("零式爆突", "ZEROSHIKI BAKUTOTSU — EXPLOSÃO DE TRONCO À QUEIMA-ROUPA"),
            "FOREHEAD_PIN": ("苦無眉間", "KUNAI MIKEN — KUNAI FINCADA NA TESTA"),
            "HEART_THROAT_STAB": ("短刀急所", "TANTOU KYUUSHO — GOLPE MORTAL NA GARGANTA"),
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
            self.camera_setup_timer = self.CAMERA_SETUP_DURATION
            self.freeze_timer = 0.5
            self.bw_flash_timer = 0.7
            self.delayed_death_timer = 0.6
            victim.is_alive = False
            victim.state = "DYING_FREEZE"
            victim.state_timer = (0.5 / self.FINISHER_SPEED_SCALE) + self.camera_setup_timer
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
        self.camera_setup_timer = 0.25 if attacker is None else self.CAMERA_SETUP_DURATION

        # Configurar enquadramento dinâmico, zoom e batimento cardíaco
        if attacker is not None and victim is not None:
            self.camera_focus_target = ((attacker.wx + victim.wx) / 2.0, (attacker.wy + victim.wy) / 2.0)
        elif victim is not None:
            self.camera_focus_target = (victim.wx, victim.wy)
        else:
            self.camera_focus_target = (10.5, 10.5)

        self.cinematic_zoom_target = 1.65
        self.letterbox_target = 1.0
        self.optimal_azimuth = self.compute_optimal_finisher_azimuth(attacker, victim, slash_dir)
        self.orbit_dir = 1.0
        self.camera_roll_deg = 0.0
        self._cam_start_captured = False
        self._cam_setup_elapsed = 0.0
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
        self.goro_attacker = None
        self.goro_victim = None
        self.goro_windup_timer = 0.0
        self.goro_cleaved_timer = 0.0
        self.goro_sound_played = False
        self.finisher_attacker = None
        self.finisher_victim = None
        self.finisher_style = death_style
        self.finisher_strike_timer = 0.0
        self.finisher_strike_duration = 0.0
        self.finisher_impact_played = False

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
            self.joe_pin_timer = 0.75
            self.joe_throw_timer = 0.50
            self.freeze_timer = 1.25
            self.bw_flash_duration = 1.65
            self.bw_flash_timer = 1.65
            self.delayed_death_timer = 1.25
            self.shuriken_active = False
            self.joe_sound_played = False
            self.joe_throw_sound_played = False
            if attacker is not None:
                attacker.set_facing(victim.wx, victim.wy)
                attacker.state = "IDLE"

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

        elif death_style in ("DUAL_IMPALE_X_SPREAD", "REFLECTED_TORSO_CLEAVE"):
            # Musashi: Niten Ichi-ryuu - Duas espadas cruzadas rasgam o torso em 'X' com corte duplo simultâneo
            self.freeze_timer = 1.10
            self.bw_flash_duration = 1.50
            self.bw_flash_timer = 1.50
            self.delayed_death_timer = 1.10
            self._arm_closeup_finisher_strike(attacker, victim, duration=1.10)

        elif death_style == "KUWA_SKULL_CLEAVE":
            # Goro: Avanço pesado, elevação colossal da Kuwa e clivagem partindo o crânio da vítima
            self.goro_attacker = attacker
            self.goro_victim = victim
            self.goro_windup_timer = 0.35
            self.goro_cleaved_timer = 0.80
            self.goro_sound_played = False
            self.freeze_timer = 1.15
            self.bw_flash_duration = 1.55
            self.bw_flash_timer = 1.55
            self.delayed_death_timer = 1.15
            if attacker is not None:
                attacker.set_facing(victim.wx, victim.wy)
                attacker.state = "ATTACK"
                attacker.state_timer = 0.26

        elif death_style == "EARTH_STOMP_CRUSH":
            # Goro Pisotão Sísmico
            self.freeze_timer = 1.15
            self.bw_flash_duration = 1.55
            self.bw_flash_timer = 1.55
            self.delayed_death_timer = 1.15
            self._arm_closeup_finisher_strike(attacker, victim, duration=1.15)

        elif death_style in ("BLIND_CAROTID_SLICE", "BLIND_SPINE_PIERCE"):
            # Ichi: Gyaku-Iai Carotídeo imperceptível e corte carotídeo com tensão silenciosa de Chambara
            self.freeze_timer = 1.20
            self.bw_flash_duration = 1.60
            self.bw_flash_timer = 1.60
            self.delayed_death_timer = 1.20
            self._arm_closeup_finisher_strike(attacker, victim, duration=1.20)

        else:
            dur = 0.38 if attacker is None else 0.48
            self.bw_flash_duration = dur + 0.06
            self.freeze_timer = dur
            self.bw_flash_timer = dur + 0.06
            self.delayed_death_timer = dur
            self._arm_closeup_finisher_strike(attacker, victim, duration=dur)

        # Deixar a vítima no estado congelado de morte iminente (ou caída no solo imobilizada por Yamato)
        victim.is_alive = False
        if death_style == "WINDMILL_SHURIKEN_DECAP":
            victim.state = "PINNED_DOWN"
        else:
            victim.state = "DYING_FREEZE"
        victim.state_timer = (self.delayed_death_timer / self.FINISHER_SPEED_SCALE) + self.camera_setup_timer + 0.15

        # Gerar o banner de Kanji Kurosawa Sumi-E em cache
        self._build_kanji_overlay(attacker, victim, death_style)

        # Preparar o corpo voxel que se manifestará após o atraso
        from src.entities.voxel_corpse import VoxelCorpse
        self.pending_corpse = VoxelCorpse(victim, death_style, slash_dir)

    def _arm_closeup_finisher_strike(self, attacker, victim, duration: float):
        """
        Prepara o atacante na postura de preparação congelada (windup) durante o zoom/roll da câmera,
        para que o golpe fatal seja desferido DEPOIS que o tempo descongela no ângulo fechado.
        """
        if attacker is None or victim is None:
            return
        self.finisher_attacker = attacker
        self.finisher_victim = victim
        self.finisher_strike_duration = max(0.25, duration)
        self.finisher_strike_timer = self.finisher_strike_duration
        self.finisher_impact_played = False
        attacker.set_facing(victim.wx, victim.wy)
        if hasattr(victim, "set_facing"):
            victim.set_facing(attacker.wx, attacker.wy)
        dist = math.hypot(victim.wx - attacker.wx, victim.wy - attacker.wy)
        if dist < 2.8 and self.finisher_style != "HEADSHOT_EXPLODE":
            atk_dur = getattr(attacker, "attack_duration", 0.25) or 0.25
            attacker.state = "ATTACK"
            # Pose inicial engatilhada (atk_progress = 0.10) enquanto a câmera faz o zoom & roll no tempo congelado
            attacker.state_timer = atk_dur * 0.90

    def update(self, dt: float, game_map, particles: list = None):
        """Atualiza os temporizadores cinematográficos e a física dos corpos."""
        import random

        # 0. Pausa dramática inicial (Passos 1 e 2):
        # O tempo permanece 100% congelado enquanto a câmera dá zoom e gira para o melhor ângulo.
        if self.camera_setup_timer > 0:
            if self.finisher_attacker is not None and self.finisher_victim is not None:
                dist = math.hypot(self.finisher_victim.wx - self.finisher_attacker.wx,
                                  self.finisher_victim.wy - self.finisher_attacker.wy)
                if dist < 2.8 and self.finisher_style != "HEADSHOT_EXPLODE":
                    atk_dur = getattr(self.finisher_attacker, "attack_duration", 0.25) or 0.25
                    self.finisher_attacker.state = "ATTACK"
                    self.finisher_attacker.state_timer = atk_dur * 0.90
            if dt <= self.camera_setup_timer:
                self.camera_setup_timer -= dt
                self._cam_setup_elapsed = self.CAMERA_SETUP_DURATION - self.camera_setup_timer
                return
            else:
                dt -= self.camera_setup_timer
                self.camera_setup_timer = 0.0
                self._cam_setup_elapsed = self.CAMERA_SETUP_DURATION

        effective_dt = dt * self.FINISHER_SPEED_SCALE

        if self.freeze_timer > 0:
            self.freeze_timer = max(0.0, self.freeze_timer - effective_dt)

        if self.bw_flash_timer > 0:
            self.bw_flash_timer = max(0.0, self.bw_flash_timer - effective_dt)

        self.sumie_anim_timer += effective_dt

        # Suavização da barra anamórfica e zoom
        self.letterbox_prog += (self.letterbox_target - self.letterbox_prog) * min(1.0, effective_dt * 5.0)
        self.cinematic_zoom += (self.cinematic_zoom_target - self.cinematic_zoom) * min(1.0, effective_dt * 4.5)

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
            self.hyakuretsu_flurry_timer = max(0.0, self.hyakuretsu_flurry_timer - effective_dt)
            atk = self.hyakuretsu_attacker
            vic = self.hyakuretsu_victim
            if atk is not None:
                atk.hyakuretsu_phase = "FLURRY"
                atk.hyakuretsu_clock = getattr(atk, "hyakuretsu_clock", 0.0) + effective_dt
            if vic is not None:
                ox, oy = self.hyakuretsu_victim_origin
                vic.wx = ox + random.uniform(-0.06, 0.06)
                vic.wy = oy + random.uniform(-0.06, 0.06)
            self.hyakuretsu_spark_accum += effective_dt
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
            self.hyakuretsu_pause_timer = max(0.0, self.hyakuretsu_pause_timer - effective_dt)
            atk = self.hyakuretsu_attacker
            vic = self.hyakuretsu_victim
            if atk is not None:
                atk.hyakuretsu_phase = "PAUSE"
                atk.hyakuretsu_clock = getattr(atk, "hyakuretsu_clock", 0.0) + effective_dt
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
            self.hoist_timer = max(0.0, self.hoist_timer - effective_dt)
            atk = self.hoist_attacker
            vic = self.hoist_victim
            if atk is not None and vic is not None:
                t = 1.0 - (self.hoist_timer / 0.70)
                # Benkei empala e ergue no ar em arco monumental
                atk.state = "ATTACK"
                atk.hoist_slam_phase = "HOIST"
                atk.hoist_slam_prog = t
                atk.state_timer = 0.28
                vic.wx = atk.wx + atk.facing_x * (1.1 - 0.45 * t)
                vic.wy = atk.wy + atk.facing_y * (1.1 - 0.45 * t)
                vic.wz = 0.25 + 1.85 * math.sin(t * math.pi * 0.5)
                if particles is not None and random.random() < 0.70:
                    from src.effects.particles import BloodParticle
                    particles.append(BloodParticle(vic.wx, vic.wy, max(0.2, vic.wz - 0.15)))

        if self.hoist_timer <= 0 and self.hoist_slam_timer > 0:
            self.hoist_slam_timer = max(0.0, self.hoist_slam_timer - effective_dt)
            atk = self.hoist_attacker
            vic = self.hoist_victim
            if atk is not None and vic is not None:
                s = 1.0 - (self.hoist_slam_timer / 0.35)
                # Benkei desce a naginata com força sísmica
                atk.state = "ATTACK"
                atk.hoist_slam_phase = "SLAM"
                atk.hoist_slam_prog = s
                atk.state_timer = 0.28
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
            self.sonic_flash_timer = max(0.0, self.sonic_flash_timer - effective_dt)
            vic = self.sonic_victim
            # Impacto inicial: sangramento do tórax
            if vic is not None and particles is not None:
                from src.effects.particles import BloodParticle, SparkParticle
                particles.append(BloodParticle(vic.wx, vic.wy, 0.65))
                particles.append(SparkParticle(vic.wx + random.uniform(-0.15, 0.15),
                                               vic.wy + random.uniform(-0.15, 0.15),
                                               0.65, color=(120, 240, 255)))
        elif self.sonic_silence_timer > 0:
            self.sonic_silence_timer = max(0.0, self.sonic_silence_timer - effective_dt)
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
            first_frame_pin = not getattr(self, "joe_sound_played", False)
            self.joe_pin_timer = max(0.0, self.joe_pin_timer - effective_dt)
            atk = self.joe_attacker
            vic = self.joe_victim
            if first_frame_pin:
                self.joe_sound_played = True
                try:
                    from src.audio.sound_manager import get_sound_manager
                    from src.audio.sound_events import SoundEvent
                    get_sound_manager().play(SoundEvent.DOG_BARK, volume_scale=1.0)
                except Exception:
                    pass
            if atk is not None and hasattr(atk, "dog") and atk.dog is not None and vic is not None:
                # Yamato morde e imobiliza o adversário caído no solo
                atk.dog.wx = vic.wx - atk.facing_x * 0.15
                atk.dog.wy = vic.wy - atk.facing_y * 0.15
                atk.dog.facing_x = atk.facing_x
                atk.dog.facing_y = atk.facing_y
                atk.dog.state = "CHARGE"
                if particles is not None and random.random() < 0.60:
                    from src.effects.particles import BloodParticle
                    particles.append(BloodParticle(vic.wx, vic.wy, 0.35))
            if atk is not None and vic is not None:
                atk.state = "IDLE"
                atk.set_facing(vic.wx, vic.wy)

        elif self.joe_throw_timer > 0:
            first_frame_throw = not getattr(self, "joe_throw_sound_played", False)
            self.joe_throw_timer = max(0.0, self.joe_throw_timer - effective_dt)
            atk = self.joe_attacker
            vic = self.joe_victim
            tp = 1.0 - (self.joe_throw_timer / 0.50)
            if first_frame_throw:
                self.joe_throw_sound_played = True
                try:
                    from src.audio.sound_manager import get_sound_manager
                    from src.audio.sound_events import SoundEvent
                    get_sound_manager().play(SoundEvent.SHURIKEN_THROW, volume_scale=1.0)
                except Exception:
                    pass
            if atk is not None and vic is not None:
                atk.state = "ATTACK"
                atk.state_timer = 0.25
                atk.set_facing(vic.wx, vic.wy)
                self.shuriken_active = True
                # Trajetória da shuriken gigante de Joe até a vítima
                self.shuriken_proj_x = atk.wx + (vic.wx - atk.wx) * min(1.0, tp * 1.35)
                self.shuriken_proj_y = atk.wy + (vic.wy - atk.wy) * min(1.0, tp * 1.35)

                # Shuriken moinho girando com 4 pás em faíscas de aço
                if particles is not None:
                    from src.effects.particles import SparkParticle
                    for ang in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
                        cur_ang = self.sumie_anim_timer * 36.0 + ang
                        sx = self.shuriken_proj_x + math.cos(cur_ang) * 0.36
                        sy = self.shuriken_proj_y + math.sin(cur_ang) * 0.36
                        particles.append(SparkParticle(sx, sy, 0.68, color=(225, 235, 245)))

                # Yamato salta para o lado antes do golpe decapitar
                if hasattr(atk, "dog") and atk.dog is not None and tp > 0.22:
                    atk.dog.wx += -atk.facing_y * 2.2 * effective_dt
                    atk.dog.wy += atk.facing_x * 2.2 * effective_dt
                    atk.dog.state = "FOLLOW"

        # 5. Julie Rapier Flurry & Point-blank
        if self.julie_flurry_timer > 0:
            self.julie_flurry_timer = max(0.0, self.julie_flurry_timer - effective_dt)
            atk = self.julie_attacker
            vic = self.julie_victim
            if atk is not None:
                # Animação ativa contínua de estocada (16Hz)
                atk.state = "ATTACK"
                atk.state_timer = 0.06
            self.julie_spark_accum += effective_dt
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
            self.julie_spin_timer = max(0.0, self.julie_spin_timer - effective_dt)
            atk = self.julie_attacker
            vic = self.julie_victim
            if atk is not None and vic is not None:
                sp = 1.0 - (self.julie_spin_timer / 0.35)
                # Pirueta elegante de capa girando 360° para as costas do oponente
                atk.state = "CAPE_FLOURISH"
                atk.state_timer = 0.20
                target_x = vic.wx - vic.facing_x * 0.45
                target_y = vic.wy - vic.facing_y * 0.45
                atk.wx += (target_x - atk.wx) * min(1.0, effective_dt * 8.0)
                atk.wy += (target_y - atk.wy) * min(1.0, effective_dt * 8.0)
                atk.set_facing(vic.wx, vic.wy)

        elif self.julie_bang_timer > 0:
            first_frame = (self.julie_bang_timer >= 0.27)
            self.julie_bang_timer = max(0.0, self.julie_bang_timer - effective_dt)
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

        # 5. Goro (Kuwa Skull Cleave)
        if self.goro_windup_timer > 0:
            self.goro_windup_timer = max(0.0, self.goro_windup_timer - effective_dt)
            atk = self.goro_attacker
            vic = self.goro_victim
            if atk is not None and vic is not None:
                w_prog = 1.0 - (self.goro_windup_timer / 0.35)
                # Goro dá passo firme à frente e ergue a Kuwa no ápice acima da cabeça com as duas mãos
                atk.set_facing(vic.wx, vic.wy)
                target_dist = 0.50
                target_x = vic.wx - atk.facing_x * target_dist
                target_y = vic.wy - atk.facing_y * target_dist
                atk.wx += (target_x - atk.wx) * min(1.0, effective_dt * 6.0)
                atk.wy += (target_y - atk.wy) * min(1.0, effective_dt * 6.0)
                atk.state = "ATTACK"
                # atk_progress cresce suavemente de 0.0 a 0.34 (elevação colossal de duas mãos)
                atk.state_timer = (1.0 - w_prog * 0.34) * 0.26

        if self.goro_windup_timer <= 0 and self.goro_cleaved_timer > 0:
            self.goro_cleaved_timer = max(0.0, self.goro_cleaved_timer - effective_dt)
            atk = self.goro_attacker
            vic = self.goro_victim
            if atk is not None and vic is not None:
                atk.set_facing(vic.wx, vic.wy)
                atk.state = "ATTACK"
                # Mantém a pose de impacto (Kuwa cravada no crânio / ombro a prog=0.62)
                atk.state_timer = (1.0 - 0.62) * 0.26
                if not self.goro_sound_played:
                    self.goro_sound_played = True
                    from src.audio.sound_manager import get_sound_manager
                    from src.audio.sound_events import SoundEvent
                    get_sound_manager().play(SoundEvent.OBSTACLE_HIT, volume_scale=1.0)
                    get_sound_manager().play(SoundEvent.SWORD_SLASH, volume_scale=0.9)
                    if particles is not None:
                        from src.effects.particles import SparkParticle, BloodParticle, SmokeParticle
                        for _ in range(8):
                            particles.append(SparkParticle(vic.wx, vic.wy, 0.82, color=(255, 230, 150)))
                        for _ in range(10):
                            particles.append(BloodParticle(vic.wx, vic.wy, 0.82))
                        for _ in range(4):
                            particles.append(SmokeParticle(vic.wx, vic.wy, 0.82, color=(160, 140, 120), radius=0.6))
                # Vítima treme e ajoelha sob o peso colossal da enxada
                c_prog = 1.0 - (self.goro_cleaved_timer / 0.80)
                vic.wz = max(-0.10, -0.10 * c_prog)
                if particles is not None and random.random() < 0.40:
                    from src.effects.particles import BloodParticle
                    particles.append(BloodParticle(vic.wx + random.uniform(-0.08, 0.08),
                                                   vic.wy + random.uniform(-0.08, 0.08),
                                                   0.75 - c_prog * 0.10))

        # 6. Coreografia universal de golpe final no ângulo fechado (após descongelar o tempo)
        if self.finisher_strike_timer > 0:
            self.finisher_strike_timer = max(0.0, self.finisher_strike_timer - effective_dt)
            atk = self.finisher_attacker
            vic = self.finisher_victim
            if atk is not None and vic is not None:
                prog = 1.0 - (self.finisher_strike_timer / max(0.001, self.finisher_strike_duration))
                atk.set_facing(vic.wx, vic.wy)
                dist = math.hypot(vic.wx - atk.wx, vic.wy - atk.wy)
                if dist < 2.8 and self.finisher_style != "HEADSHOT_EXPLODE":
                    atk_dur = getattr(atk, "attack_duration", 0.25) or 0.25
                    atk.state = "ATTACK"
                    # Aproximar suavemente para distância ideal de golpe em close-up (~0.82 tiles)
                    if dist > 0.85:
                        target_x = vic.wx - atk.facing_x * 0.82
                        target_y = vic.wy - atk.facing_y * 0.82
                        atk.wx += (target_x - atk.wx) * min(1.0, effective_dt * 9.0)
                        atk.wy += (target_y - atk.wy) * min(1.0, effective_dt * 9.0)
                    if prog < 0.28:
                        # Fase A: Tensão e preparação da lâmina no close-up (atk_progress: 0.10 -> 0.22)
                        u = prog / 0.28
                        anim_p = 0.10 + 0.12 * (u * u)
                    elif prog < 0.74:
                        # Fase B: Desfere o corte/estocada fatal através do alvo (atk_progress: 0.22 -> 0.92)
                        u = (prog - 0.28) / 0.46
                        smooth_u = u * u * (3.0 - 2.0 * u)
                        anim_p = 0.22 + 0.70 * smooth_u
                        if prog >= 0.46 and not self.finisher_impact_played:
                            self.finisher_impact_played = True
                            try:
                                from src.audio.sound_manager import get_sound_manager
                                from src.audio.sound_events import SoundEvent
                                get_sound_manager().play(SoundEvent.SWORD_SLASH, volume_scale=1.0)
                                get_sound_manager().play(SoundEvent.FATAL_STRIKE, volume_scale=0.95)
                            except Exception:
                                pass
                            if particles is not None:
                                from src.effects.particles import SparkParticle, BloodParticle
                                for _ in range(10):
                                    particles.append(SparkParticle(
                                        vic.wx + random.uniform(-0.15, 0.15),
                                        vic.wy + random.uniform(-0.15, 0.15),
                                        random.uniform(0.45, 0.85),
                                        color=(255, 235, 180)
                                    ))
                                for _ in range(16):
                                    particles.append(BloodParticle(
                                        vic.wx + random.uniform(-0.12, 0.12),
                                        vic.wy + random.uniform(-0.12, 0.12),
                                        random.uniform(0.45, 0.85)
                                    ))
                    else:
                        # Fase C: Follow-through dramático (Zanshin) enquanto o corpo se parte
                        anim_p = 0.94
                    atk.state_timer = max(0.01, (1.0 - anim_p) * atk_dur)

        if self.delayed_death_timer > 0:
            self.delayed_death_timer = max(0.0, self.delayed_death_timer - effective_dt)
            if self.delayed_death_timer <= 0 and self.pending_boss is not None:
                self.pending_boss.begin_collapse()
                self.pending_boss = None
                self.cinematic_zoom_target = 1.0
                self.letterbox_target = 0.0
            if self.delayed_death_timer <= 0 and self.pending_corpse:
                # O suspense acabou: O corpo se parte e o geiser explode!
                self.shuriken_active = False
                ds = getattr(self.pending_corpse, "death_style", "")
                if ds in ("WINDMILL_SHURIKEN_DECAP", "DUAL_IMPALE_X_SPREAD", "KUWA_SKULL_CLEAVE", "EARTH_STOMP_CRUSH", "BLIND_CAROTID_SLICE", "BLIND_SPINE_PIERCE", "KENSHIN_SPLIT", "VERTICAL_BISECTION"):
                    try:
                        from src.audio.sound_manager import get_sound_manager
                        from src.audio.sound_events import SoundEvent
                        get_sound_manager().play(SoundEvent.FATAL_STRIKE, volume_scale=1.0)
                    except Exception:
                        pass
                if self.pending_corpse.victim:
                    if self.hyakuretsu_victim is not None:
                        self.pending_corpse.victim.wx, self.pending_corpse.victim.wy = self.hyakuretsu_victim_origin
                    self.pending_corpse.victim.state = "CORPSE_SLICED"
                if self.hyakuretsu_attacker is not None:
                    self.hyakuretsu_attacker.hyakuretsu_phase = None
                if self.hoist_attacker is not None:
                    self.hoist_attacker.hoist_slam_phase = None
                    self.hoist_attacker.state = "IDLE"
                if self.goro_attacker is not None:
                    self.goro_attacker.state = "IDLE"
                if self.goro_victim is not None:
                    self.goro_victim.wz = 0.0
                self.finisher_attacker = None
                self.finisher_victim = None
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
            corpse.update(effective_dt if self.is_frozen() else dt, game_map, particles)

    def is_frozen(self) -> bool:
        """Verifica se a simulação normal deve congelar no frame dramático."""
        return (
            self.camera_setup_timer > 0
            or self.freeze_timer > 0
            or self.delayed_death_timer > 0
            or self.hyakuretsu_flurry_timer > 0
            or self.hoist_timer > 0
            or self.sonic_silence_timer > 0
            or self.joe_pin_timer > 0
            or self.joe_throw_timer > 0
            or self.julie_flurry_timer > 0
            or self.goro_windup_timer > 0
            or self.goro_cleaved_timer > 0
            or self.finisher_strike_timer > 0
        )

    def apply_camera(self, camera, dt: float):
        """
        Aplica a Câmera de Finalização em 4 Passos:
        1. FREEZE TIME (IMPACT_FREEZE): congela o tempo no contato fatal e inicia a trava de foco.
        2. ZOOM IN & ROLL TO BEST ANGLE (CAMERA_SWOOP): enquanto o tempo segue congelado, dá zoom fechado (1.65x)
           e gira/rola suavemente até o melhor ângulo 3/4 lateral (`optimal_azimuth`) sem oclusão.
        3. UNFREEZE TIME -> 4. FINISHER HAPPENS FROM CLOSE ANGLE (EXECUTION): mantém a câmera estacionada
           no ângulo fechado ideal enquanto o golpe fatal é desferido em close-up.
        """
        if not self._cam_start_captured:
            self._cam_start_captured = True
            self._cam_start_wx = camera.wx
            self._cam_start_wy = camera.wy
            self._cam_start_zoom = camera.zoom
            self._cam_start_azimuth = camera.azimuth

        if self.camera_setup_timer > 0:
            # Sincroniza o tempo decorrido do setup congelado (mesmo se apply_camera for chamado antes de update)
            timer_elapsed = self.CAMERA_SETUP_DURATION - self.camera_setup_timer
            self._cam_setup_elapsed = min(self.CAMERA_SETUP_DURATION, max(self._cam_setup_elapsed + dt, timer_elapsed))
            el = self._cam_setup_elapsed

            if el <= self.IMPACT_FREEZE_DURATION:
                # Passo 1: Tempo congelado — leve pulso inicial (0% -> 12%)
                u = (el / max(0.001, self.IMPACT_FREEZE_DURATION)) * 0.12
                self.camera_roll_deg = 0.0
            else:
                # Passo 2: Tempo congelado — Zoom-in + Roll orbital S-curve (12% -> 100%) até o melhor ângulo!
                raw_s = min(1.0, (el - self.IMPACT_FREEZE_DURATION) / max(0.001, self.CAMERA_SWOOP_DURATION))
                smooth_s = raw_s * raw_s * (3.0 - 2.0 * raw_s)
                u = 0.12 + 0.88 * smooth_s
                self.camera_roll_deg = math.sin(raw_s * math.pi) * 3.5

            # Interpolar foco, zoom, letterbox e azimute diretamente até o melhor ângulo fechado
            camera.wx = self._cam_start_wx + (self.camera_focus_target[0] - self._cam_start_wx) * u
            camera.wy = self._cam_start_wy + (self.camera_focus_target[1] - self._cam_start_wy) * u
            self.cinematic_zoom = self._cam_start_zoom + (self.cinematic_zoom_target - self._cam_start_zoom) * u
            camera.zoom = self.cinematic_zoom
            self.letterbox_prog = min(1.0, u * 1.15)
            target_az = self._cam_start_azimuth + (self.optimal_azimuth - self._cam_start_azimuth) * u
            camera.set_azimuth(target_az)
            camera.screen_y = SCREEN_HEIGHT // 2 + int(32 * u)
        else:
            # Passos 3 e 4: Tempo descongelado — Câmera permanece cravada no ângulo fechado enquanto o finisher acontece!
            self.camera_roll_deg = 0.0
            self.cinematic_zoom += (self.cinematic_zoom_target - self.cinematic_zoom) * min(1.0, dt * 6.0)
            camera.zoom = self.cinematic_zoom
            self.letterbox_prog += (self.letterbox_target - self.letterbox_prog) * min(1.0, dt * 6.0)
            camera.update(self.camera_focus_target[0], self.camera_focus_target[1], dt * 2.5)
            if self.is_frozen():
                # Mantém o melhor ângulo 3/4 com micro-deriva cinematográfica sutil (sem girar para longe)
                diff = self.optimal_azimuth - camera.azimuth
                if abs(diff) > 0.01:
                    camera.rotate(diff * min(1.0, dt * 8.0))
                else:
                    camera.rotate(0.03 * dt)

    def render_world_effects(self, surface: pygame.Surface, camera):
        """Desenha efeitos volumétricos 3D/isométricos no mundo gerados pelo diretor cinematográfico."""
        if self.shuriken_active:
            # Desenha a Shuriken Moinho gigante (Fuma Shuriken de 4 pás de aço giratórias)
            gx, gy = camera.apply(self.shuriken_proj_x, self.shuriken_proj_y, 0.65)
            spin_angle = self.sumie_anim_timer * 36.0
            radius = int(24 * camera.zoom)

            # Sombra dinâmica no solo
            sx, sy = camera.apply(self.shuriken_proj_x, self.shuriken_proj_y, 0.0)
            shadow_surf = pygame.Surface((radius * 2, radius), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (15, 18, 15, 110), (0, 0, radius * 2, radius))
            surface.blit(shadow_surf, (sx - radius, sy - radius // 2))

            # Shuriken de aço com 4 lâminas em cruz
            shuriken_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            cx, cy = radius + 5, radius + 5

            # 4 pás aerodinâmicas afiadas
            for i in range(4):
                blade_angle = spin_angle + i * (math.pi / 2.0)
                tip_x = cx + math.cos(blade_angle) * radius
                tip_y = cy + math.sin(blade_angle) * radius
                left_x = cx + math.cos(blade_angle + 0.35) * (radius * 0.44)
                left_y = cy + math.sin(blade_angle + 0.35) * (radius * 0.44)
                right_x = cx + math.cos(blade_angle - 0.22) * (radius * 0.30)
                right_y = cy + math.sin(blade_angle - 0.22) * (radius * 0.30)

                blade_pts = [(cx, cy), (left_x, left_y), (tip_x, tip_y), (right_x, right_y)]
                blade_col = (215, 225, 240) if i % 2 == 0 else (180, 195, 210)
                pygame.draw.polygon(shuriken_surf, blade_col, blade_pts)
                pygame.draw.polygon(shuriken_surf, (250, 255, 255), [(left_x, left_y), (tip_x, tip_y)], 1)
                pygame.draw.polygon(shuriken_surf, (90, 105, 120), blade_pts, 1)

            # Aro central de latão/bronze e rebite
            pygame.draw.circle(shuriken_surf, (55, 60, 68), (cx, cy), max(3, int(6 * camera.zoom)))
            pygame.draw.circle(shuriken_surf, (230, 190, 60), (cx, cy), max(2, int(3.5 * camera.zoom)))
            # Rastro de velocidade circular
            pygame.draw.circle(shuriken_surf, (225, 240, 255, 55), (cx, cy), int(radius * 0.92), 1)

            surface.blit(shuriken_surf, (gx - cx, gy - cy))

    def render_letterbox(self, surface: pygame.Surface):
        """Desenha barras pretas CinemaScope 2.39:1 (1280x540) com filete dourado sutil (zero-alloc)."""
        if self.letterbox_prog <= 0.005:
            return
        bar_h = int(SCREEN_HEIGHT * 0.125 * self.letterbox_prog)
        if bar_h > 0:
            pygame.draw.rect(surface, (4, 4, 6), (0, 0, SCREEN_WIDTH, bar_h))
            pygame.draw.rect(surface, (4, 4, 6), (0, SCREEN_HEIGHT - bar_h, SCREEN_WIDTH, bar_h))
            border_alpha = int(min(255, self.letterbox_prog * 150))
            if border_alpha > 0:
                if self._edge_line is None:
                    self._edge_line = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
                self._edge_line.fill((180, 150, 90, border_alpha))
                surface.blit(self._edge_line, (0, bar_h - 1))
                surface.blit(self._edge_line, (0, SCREEN_HEIGHT - bar_h))

    def apply_cinematic_filter(self, surface: pygame.Surface):
        """
        Aplica o efeito Kurosawa Noir e CinemaScope Anamórfico (2.39:1) reutilizando superfícies em pool:
        - Desatura a tela para preto e branco de alto contraste mantendo os tons vermelhos vivos (sangue).
        - Vinheta cinematográfica periférica.
        - Pincelada dinâmica Sumi-E em nanquim diagonal.
        - Ideogramas Kanji com impacto de escala.
        - Barras pretas anamórficas 2.39:1.
        """
        if self.bw_flash_timer > 0:
            alpha = int(min(255, (self.bw_flash_timer / self.bw_flash_duration) * 220))
            if alpha > 0:
                # Máscara monocromática estilizada (superfície reutilizada)
                if self._bw_overlay is None:
                    self._bw_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                self._bw_overlay.fill((30, 30, 35, alpha))
                surface.blit(self._bw_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

                # Vinheta escura nas bordas estilo película clássica (superfície reutilizada)
                vig_alpha = int(alpha * 0.45)
                if self._vignette_surf is None:
                    self._vignette_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    self._last_vignette_alpha = -1
                if vig_alpha != self._last_vignette_alpha:
                    self._vignette_surf.fill((0, 0, 0, 0))
                    pygame.draw.rect(self._vignette_surf, (10, 10, 15, vig_alpha), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), width=35)
                    self._last_vignette_alpha = vig_alpha
                surface.blit(self._vignette_surf, (0, 0))

        # Pincelada e Kanjis Sumi-E (desenhados durante o flash após o enquadramento da câmera)
        if self.camera_setup_timer <= 0 and self.bw_flash_timer > 0 and self.cached_kanji_surf is not None:
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

                    if self._brush_surf is None:
                        self._brush_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    self._brush_surf.fill((0, 0, 0, 0))
                    pygame.draw.line(self._brush_surf, (14, 14, 18, int(kanji_alpha * 0.85)), (start_x, start_y), (end_x, end_y), 18)
                    pygame.draw.line(self._brush_surf, (24, 24, 28, int(kanji_alpha * 0.95)), (start_x + 8, start_y - 3), (end_x, end_y - 3), 8)
                    pygame.draw.line(self._brush_surf, (190, 35, 35, int(kanji_alpha * 0.65)), (start_x + 16, start_y + 4), (end_x, end_y + 4), 3)
                    surface.blit(self._brush_surf, (0, 0))

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
        if self.hoist_attacker is not None:
            self.hoist_attacker.hoist_slam_phase = None
        self.is_active = False
        self.camera_setup_timer = 0.0
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
        self.joe_sound_played = False
        self.joe_throw_sound_played = False
        self.julie_attacker = None
        self.julie_victim = None
        self.julie_flurry_timer = 0.0
        self.julie_spin_timer = 0.0
        self.julie_bang_timer = 0.0
        self.julie_spark_accum = 0.0
        self.goro_attacker = None
        self.goro_victim = None
        self.goro_windup_timer = 0.0
        self.goro_cleaved_timer = 0.0
        self.goro_sound_played = False
        self.finisher_attacker = None
        self.finisher_victim = None
        self.finisher_style = ""
        self.finisher_strike_timer = 0.0
        self.finisher_strike_duration = 0.0
        self.finisher_impact_played = False
        self.camera_roll_deg = 0.0
        self._cam_start_captured = False
        self._cam_setup_elapsed = 0.0
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
