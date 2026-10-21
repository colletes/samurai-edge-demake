"""
Fase 5 - Entregável 5.1: Clash de Espadas Tsubazeriai (QTE "STRIKE!").

Quando dois ataques de mesma prioridade colidem simultaneamente, em vez do
simples atordoamento mútuo antigo, os dois lutadores entram em um choque de
força (Tsubazeriai) congelado: a câmera aproxima-se dramaticamente e um botão
arcade pulsante com o texto "STRIKE!" aparece sobre o ponto de impacto.
O primeiro jogador a apertar o botão de ataque vence o choque, empurra o
oponente e o deixa atordoado; se nenhum apertar a tempo (ou ambos apertarem
no mesmo quadro), o choque termina em empate.
"""
import math
import pygame

from src.effects.particles import SparkParticle, FloatingBanner
from src.i18n import t

# Estado temporário aplicado aos dois lutadores durante o choque.
STATE_CLASH_QTE = "CLASH_QTE"

QTE_WINDOW = 1.1      # Duração total da janela de disputa, em segundos
PULSE_SPEED = 9.0     # Velocidade de pulsação do texto "STRIKE!"
ZOOM_AMOUNT = 0.14    # Zoom dramático máximo aplicado à câmera durante o choque


class ClashSystem:
    """Gerencia o duelo de lâminas Tsubazeriai disparado quando dois ataques
    de mesma prioridade colidem simultaneamente (QTE "STRIKE!")."""

    def __init__(self):
        self.is_active = False
        self.timer = 0.0
        self.p1 = None
        self.p2 = None
        self.mid_x = 0.0
        self.mid_y = 0.0
        self.p1_pressed = False
        self.p2_pressed = False
        self.pulse_phase = 0.0
        # Oponente controlado pela IA: índice do jogador (0/1) e função que sorteia o tempo de reação (None = não aperta)
        self.ai_player: int | None = None
        self.ai_reaction_fn = None
        self._ai_timer: float | None = None
        # Rótulos das teclas de ataque de P1 e P2, mostrados no botão
        self.key_hints: tuple[str, str] = ("", "")

    @staticmethod
    def _play(event_name: str):
        try:
            from src.audio.sound_events import SoundEvent
            from src.audio.sound_manager import SoundManager
            SoundManager.get_instance().play(getattr(SoundEvent, event_name))
        except Exception:
            pass

    def trigger(self, p1, p2, mid_x: float, mid_y: float, camera=None, particles: list = None, banners: list = None, ctrl_mgr=None):
        """Congela os dois lutadores em disputa de força e abre a janela de QTE."""
        self.is_active = True
        self.timer = QTE_WINDOW
        self.p1 = p1
        self.p2 = p2
        self.mid_x = mid_x
        self.mid_y = mid_y
        self.p1_pressed = False
        self.p2_pressed = False
        self.pulse_phase = 0.0
        self._ai_timer = None
        if self.ai_player is not None and self.ai_reaction_fn is not None:
            self._ai_timer = self.ai_reaction_fn()
        self._play("SWORD_CLASH")

        for fighter in (p1, p2):
            fighter.state = STATE_CLASH_QTE
            fighter.state_timer = QTE_WINDOW
            fighter.hitbox_active = False
            fighter.wz = 0.0

        if particles is not None:
            for _ in range(15):
                particles.append(SparkParticle(mid_x, mid_y, 0.6))
        if camera is not None:
            camera.add_shake(6.0)
            camera.zoom = 1.0
        if ctrl_mgr is not None:
            ctrl_mgr.rumble_player(0, 0.4, 0.6, 140)
            ctrl_mgr.rumble_player(1, 0.4, 0.6, 140)

    def register_press(self, player_index: int):
        """Registra o aperto do botão de ataque/confirmação de um jogador durante o choque."""
        if not self.is_active:
            return
        if player_index == 0:
            self.p1_pressed = True
        elif player_index == 1:
            self.p2_pressed = True

    def is_frozen(self) -> bool:
        """Retorna True enquanto o choque de espadas estiver congelando o duelo."""
        return self.is_active

    def update(self, dt: float, camera=None, particles: list = None, banners: list = None, ctrl_mgr=None, game_map=None) -> str | None:
        """Avança o cronômetro do QTE e resolve o vencedor quando aplicável.
        Retorna 'P1_WINS_CLASH', 'P2_WINS_CLASH', 'DRAW_CLASH' ou None se o choque
        ainda estiver em curso (ou inativo)."""
        if not self.is_active:
            return None

        self.pulse_phase += dt * PULSE_SPEED
        self.timer -= dt
        if self._ai_timer is not None:
            self._ai_timer -= dt
            if self._ai_timer <= 0.0:
                self.register_press(self.ai_player)
                self._ai_timer = None
        progress = 1.0 - max(0.0, self.timer) / QTE_WINDOW
        if camera is not None:
            camera.zoom = 1.0 + ZOOM_AMOUNT * progress

        result = None
        if self.p1_pressed and self.p2_pressed:
            result = "DRAW"
        elif self.p1_pressed:
            result = "P1"
        elif self.p2_pressed:
            result = "P2"
        elif self.timer <= 0.0:
            result = "DRAW"

        if result is None:
            return None

        return self._resolve(result, camera, particles, banners, ctrl_mgr, game_map)

    def _resolve(self, result: str, camera, particles, banners, ctrl_mgr, game_map=None) -> str:
        p1, p2 = self.p1, self.p2

        for fighter in (p1, p2):
            fighter.state_timer = 0.0
            fighter.wz = 0.0

        if result == "DRAW":
            p1.state = "IDLE"
            p2.state = "IDLE"
            if banners is not None:
                banners.append(FloatingBanner(t("clash_draw"), self.mid_x, self.mid_y, wz=1.6, color=(255, 230, 80)))
            p1.stun(0.35)
            p2.stun(0.35)
            event_name = "DRAW_CLASH"
        elif result == "P1":
            p1.state = "IDLE"
            if banners is not None:
                banners.append(FloatingBanner(t("clash_win", player=1), self.mid_x, self.mid_y, wz=1.7, color=(255, 215, 60)))
            p2.stun(0.9)
            self._push_back(p2, p1, game_map)
            self._play("PARRY")
            if camera is not None:
                camera.add_shake(10.0)
            if ctrl_mgr is not None:
                ctrl_mgr.rumble_player(1, 0.7, 0.9, 220)
            event_name = "P1_WINS_CLASH"
        else:
            p2.state = "IDLE"
            if banners is not None:
                banners.append(FloatingBanner(t("clash_win", player=2), self.mid_x, self.mid_y, wz=1.7, color=(255, 215, 60)))
            p1.stun(0.9)
            self._push_back(p1, p2, game_map)
            self._play("PARRY")
            if camera is not None:
                camera.add_shake(10.0)
            if ctrl_mgr is not None:
                ctrl_mgr.rumble_player(0, 0.7, 0.9, 220)
            event_name = "P2_WINS_CLASH"

        if camera is not None:
            camera.zoom = 1.0

        self.is_active = False
        self.timer = 0.0
        self.p1 = None
        self.p2 = None
        return event_name

    def _push_back(self, loser, winner, game_map=None):
        """Empurra o perdedor do choque para longe do vencedor (respeita limites e sólidos; pode jogá-lo em um buraco)."""
        dx = loser.wx - winner.wx
        dy = loser.wy - winner.wy
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            dx, dy = -winner.facing_x, -winner.facing_y
            dist = math.hypot(dx, dy) or 1.0
        if game_map is not None:
            loser.apply_forced_displacement((dx / dist) * 0.9, (dy / dist) * 0.9, game_map)
        else:
            loser.wx += (dx / dist) * 0.9
            loser.wy += (dy / dist) * 0.9

    def render(self, surface, camera):
        """
        Desenha o prompt cinematográfico de Tsubazeriai (choque de espadas):
        Lâminas cruzadas em aço e ouro, anel radial de tensão temporal e selo Kanji de impacto.
        """
        if not self.is_active:
            return
        from src.ui.fonts import get_title_font, get_text_font

        sx, sy = camera.apply(self.mid_x, self.mid_y, 1.9)
        pulse = 1.0 + 0.14 * math.sin(self.pulse_phase)
        cx, cy = sx, sy - 82

        pct = max(0.0, min(1.0, self.timer / QTE_WINDOW))

        # 1. Halo de Brilho & Tensão Mística
        glow_r = int(58 * pulse)
        glow_surf = pygame.Surface((glow_r * 2 + 8, glow_r * 2 + 8), pygame.SRCALPHA)
        center_g = glow_r + 4
        # Cor esquenta de ouro para carmesim conforme o tempo esgota
        glow_col = (
            int(255),
            int(215 * pct + 40 * (1.0 - pct)),
            int(60 * pct + 30 * (1.0 - pct)),
        )
        for r, a in ((glow_r, 35), (int(glow_r * 0.72), 55), (int(glow_r * 0.45), 80)):
            pygame.draw.circle(glow_surf, (*glow_col, a), (center_g, center_g), r)
        surface.blit(glow_surf, (cx - center_g, cy - center_g))

        # 2. Anel Radial de Tensão (circunferência decrescente com a contagem)
        ring_r = int(42 * pulse)
        pygame.draw.circle(surface, (18, 20, 24), (cx, cy), ring_r + 4, width=4)
        pygame.draw.circle(surface, (50, 44, 36), (cx, cy), ring_r, width=2)

        # Segmentos do anel de tensão desenhados como arcos angulares
        num_segs = 32
        active_segs = int(num_segs * pct)
        for i in range(active_segs):
            theta = -math.pi / 2 + (i / num_segs) * math.pi * 2
            px = cx + int(math.cos(theta) * ring_r)
            py = cy + int(math.sin(theta) * ring_r)
            pygame.draw.circle(surface, glow_col, (px, py), 3)

        # 3. Lâminas de Aço Cruzadas (✕) com Gume Metálico e Guarda Dourada (Tsuba)
        blade_len = int(36 * pulse)
        for sign_x in (-1, 1):
            p_start = (cx - sign_x * blade_len, cy - blade_len)
            p_end = (cx + sign_x * blade_len, cy + blade_len)
            # Corpo de aço escuro
            pygame.draw.line(surface, (20, 22, 26), p_start, p_end, 5)
            # Gume de aço brilhante temperado
            pygame.draw.line(surface, (230, 240, 255), p_start, p_end, 2)
            # Destaque de reflexo
            p_mid1 = (cx - sign_x * (blade_len // 3), cy - (blade_len // 3))
            p_mid2 = (cx + sign_x * (blade_len // 3), cy + (blade_len // 3))
            pygame.draw.line(surface, (255, 255, 255), p_mid1, p_mid2, 3)

        # 4. Ponto Central de Fricção: Selo Kanji Carmesim (斬 - ZAN / STRIKE)
        seal_size = int(28 * pulse)
        seal_rect = pygame.Rect(cx - seal_size // 2, cy - seal_size // 2, seal_size, seal_size)
        pygame.draw.rect(surface, (180, 28, 32), seal_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 225, 110), seal_rect, width=2, border_radius=4)

        kanji_font = get_title_font(max(14, int(18 * pulse)))
        kanji_txt = kanji_font.render("斬", True, (255, 245, 225))
        surface.blit(kanji_txt, (seal_rect.centerx - kanji_txt.get_width() // 2, seal_rect.centery - kanji_txt.get_height() // 2))

        # 5. Título de Ação "STRIKE!" com caligrafia em folha de ouro
        title_font = get_title_font(max(18, int(26 * pulse)))
        callout_txt = title_font.render("STRIKE!", True, (255, 225, 95))
        shadow_txt = title_font.render("STRIKE!", True, (16, 12, 10))
        title_rect = callout_txt.get_rect(center=(cx, cy - ring_r - 20))
        surface.blit(shadow_txt, (title_rect.x + 2, title_rect.y + 2))
        surface.blit(callout_txt, title_rect)

        # 6. Prompts de Tecla dos Jogadores (P1 / P2) em laca estilizada
        hint_font = get_text_font(13)
        hints_y = cy + ring_r + 18
        if any(self.key_hints):
            p1_active = self.p1_pressed
            p2_active = self.p2_pressed
            p1_str = f"P1 [{self.key_hints[0]}]" if len(self.key_hints) > 0 and self.key_hints[0] else ""
            p2_str = f"P2 [{self.key_hints[1]}]" if len(self.key_hints) > 1 and self.key_hints[1] else ""

            combined_str = f"{p1_str}   {p2_str}".strip()
            if combined_str:
                h_surf = hint_font.render(combined_str, True, (255, 240, 200))
                h_w = h_surf.get_width() + 20
                h_h = h_surf.get_height() + 8
                h_rect = pygame.Rect(cx - h_w // 2, hints_y - 2, h_w, h_h)
                pygame.draw.rect(surface, (14, 16, 18, 220), h_rect, border_radius=4)
                pygame.draw.rect(surface, (180, 145, 60), h_rect, width=1, border_radius=4)
                surface.blit(h_surf, (h_rect.centerx - h_surf.get_width() // 2, h_rect.centery - h_surf.get_height() // 2))
