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
        """Desenha o botão arcade pulsante com o texto 'STRIKE!' sobre o ponto do choque."""
        if not self.is_active:
            return
        from src.ui.fonts import get_title_font, get_text_font

        sx, sy = camera.apply(self.mid_x, self.mid_y, 1.9)
        pulse = 1.0 + 0.18 * math.sin(self.pulse_phase)
        cx, cy = sx, sy - 70

        # Brilho pulsante atrás do botão
        glow_r = int(52 * pulse)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        for r, a in ((glow_r, 40), (int(glow_r * 0.75), 60), (int(glow_r * 0.5), 80)):
            pygame.draw.circle(glow, (255, 190, 60, a), (glow_r, glow_r), r)
        surface.blit(glow, (cx - glow_r, cy - glow_r))

        # Botão arcade: base escura, cúpula vermelha com reflexo e aro dourado
        base_r = int(30 * pulse)
        pygame.draw.circle(surface, (28, 18, 10), (cx, cy + 4), base_r + 4)
        pygame.draw.circle(surface, (200, 40, 36), (cx, cy), base_r)
        pygame.draw.circle(surface, (255, 96, 74), (cx, cy - 2), int(base_r * 0.78))
        pygame.draw.ellipse(surface, (255, 220, 200), (cx - int(base_r * 0.5), cy - int(base_r * 0.72), int(base_r * 0.8), int(base_r * 0.42)))
        pygame.draw.circle(surface, (255, 225, 70), (cx, cy), base_r + 4, width=3)

        size = max(18, int(34 * pulse))
        font = get_title_font(size)
        text = font.render("STRIKE!", True, (255, 225, 70))
        shadow = font.render("STRIKE!", True, (40, 20, 0))
        rect = text.get_rect(center=(cx, cy - base_r - 24))
        surface.blit(shadow, (rect.x + 3, rect.y + 3))
        surface.blit(text, rect)

        # Qual tecla cada jogador deve apertar
        hint_font = get_text_font(15)
        hints = [f"P{i + 1} [{label}]" for i, label in enumerate(self.key_hints) if label]
        if hints:
            hint = hint_font.render("   ".join(hints), True, (255, 240, 200))
            surface.blit(hint, hint.get_rect(center=(cx, cy + base_r + 20)))

        pct = max(0.0, min(1.0, self.timer / QTE_WINDOW))
        bar_w = 90
        bar_h = 6
        bx = cx - bar_w // 2
        by = cy + base_r + 36
        pygame.draw.rect(surface, (30, 24, 10), (bx, by, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(surface, (255, 200, 60), (bx, by, int(bar_w * pct), bar_h), border_radius=3)
        pygame.draw.rect(surface, (255, 240, 200), (bx, by, bar_w, bar_h), width=1, border_radius=3)
