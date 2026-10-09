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

        # Cache de Kanjis de corte fatal Kurosawa (Entregável 3.2)
        self.cached_kanji_surf: pygame.Surface | None = None
        self.current_kanji_text: str = ""
        self.current_kanji_subtitle: str = ""

    def _build_kanji_overlay(self, attacker=None, victim=None, death_style: str = "", phrase: tuple | None = None):
        """Gera e cacheia a textura de caligrafia Sumi-E dos kanjis de corte fatal."""
        import random
        from src.ui.fonts import get_text_font

        # Pool de expressões clássicas de cinema samurai
        phrases = [
            ("一刀両断", "ITTOU RYOUDAN — CORTE CERTEIRO"),
            ("決闘終焉", "KETTOU SHUUEN — FIM DO DUELO"),
            ("神速必殺", "SHINSOKU HISSATSU — GOLPE DIVINO"),
            ("生死一瞬", "SEISHI ISSHUN — VIDA E MORTE"),
        ]
        kanji_str, sub_str = phrase or random.choice(phrases)
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
            return

        self.is_active = True
        self.freeze_timer = 0.38          # Tempo de congelamento inicial
        self.bw_flash_timer = 0.50        # Duração do filtro preto e branco
        self.delayed_death_timer = 0.42   # Atraso dramático antes do corpo se partir!

        # Deixar a vítima no estado congelado de morte iminente
        victim.is_alive = False
        victim.state = "DYING_FREEZE"
        victim.state_timer = 0.50

        # Gerar o banner de Kanji Kurosawa Sumi-E em cache
        self._build_kanji_overlay(attacker, victim, death_style)

        # Preparar o corpo voxel que se manifestará após o atraso
        from src.entities.voxel_corpse import VoxelCorpse
        self.pending_corpse = VoxelCorpse(victim, death_style, slash_dir)

    def update(self, dt: float, game_map, particles: list = None):
        """Atualiza os temporizadores cinematográficos e a física dos corpos."""
        if self.freeze_timer > 0:
            self.freeze_timer = max(0.0, self.freeze_timer - dt)

        if self.bw_flash_timer > 0:
            self.bw_flash_timer = max(0.0, self.bw_flash_timer - dt)

        if self.delayed_death_timer > 0:
            self.delayed_death_timer = max(0.0, self.delayed_death_timer - dt)
            if self.delayed_death_timer <= 0 and self.pending_boss is not None:
                self.pending_boss.begin_collapse()
                self.pending_boss = None
            if self.delayed_death_timer <= 0 and self.pending_corpse:
                # O suspense acabou: O corpo se parte e o geiser explode!
                if self.pending_corpse.victim:
                    self.pending_corpse.victim.state = "CORPSE_SLICED"
                self.corpses.append(self.pending_corpse)
                self.pending_corpse = None

        # Atualizar todos os corpos fatiados existentes
        for corpse in self.corpses:
            corpse.update(dt, game_map, particles)

    def is_frozen(self) -> bool:
        """Verifica se a simulação normal deve congelar no frame dramático."""
        return self.freeze_timer > 0

    def apply_cinematic_filter(self, surface: pygame.Surface):
        """
        Aplica o efeito Kurosawa Noir:
        Desatura a tela para preto e branco de alto contraste mantendo os tons vermelhos vivos (sangue).
        """
        if self.bw_flash_timer <= 0:
            return

        alpha = int(min(255, (self.bw_flash_timer / self.bw_flash_duration) * 220))
        if alpha <= 0:
            return

        # Camada de saturação/desaturação estilizada usando blend modes nativos de alto desempenho
        # Criar máscara monocromática rápida
        bw_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Tom cinza ardósia escuro com blend SUBTRACT / MULTIPLY que preserva luminosidade
        bw_overlay.fill((30, 30, 35, alpha))
        surface.blit(bw_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        # Adicionar vinheta escura nas bordas estilo película clássica
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (10, 10, 15, int(alpha * 0.45)), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), width=35)
        surface.blit(vignette, (0, 0))

        # Renderizar kanjis Kurosawa Sumi-E sobrepostos no topo central da tela
        if self.cached_kanji_surf is not None:
            kanji_alpha = int(min(255, (self.bw_flash_timer / self.bw_flash_duration) * 255))
            self.cached_kanji_surf.set_alpha(kanji_alpha)
            kx = (SCREEN_WIDTH - self.cached_kanji_surf.get_width()) // 2
            ky = 55
            surface.blit(self.cached_kanji_surf, (kx, ky))

    def reset_round(self):
        """Limpa estados transitórios mantendo manchas de sangue se desejado."""
        self.is_active = False
        self.freeze_timer = 0.0
        self.bw_flash_timer = 0.0
        self.delayed_death_timer = 0.0
        self.pending_corpse = None
        self.pending_boss = None
        self.corpses.clear()
        self.cached_kanji_surf = None
        self.current_kanji_text = ""
        self.current_kanji_subtitle = ""
