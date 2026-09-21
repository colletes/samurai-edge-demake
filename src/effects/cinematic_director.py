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
        self.corpses = []  # Lista de corpos voxel persistentes na partida

    def trigger_fatal_strike(self, attacker, victim, death_style: str, slash_dir: tuple[float, float]):
        """Dispara a sequência de cinema samurai no golpe letal."""
        self.is_active = True
        self.freeze_timer = 0.38          # Tempo de congelamento inicial
        self.bw_flash_timer = 0.50        # Duração do filtro preto e branco
        self.delayed_death_timer = 0.42   # Atraso dramático antes do corpo se partir!

        # Deixar a vítima no estado congelado de morte iminente
        victim.is_alive = False
        victim.state = "DYING_FREEZE"
        victim.state_timer = 0.50

        # Preparar o corpo voxel que se manifestará após o atraso
        from src.entities.voxel_corpse import VoxelCorpse
        self.pending_corpse = VoxelCorpse(victim, death_style, slash_dir)

    def update(self, dt: float, game_map, particles: list = None):
        """Atualiza os temporizadores cinematográficos e a física dos corpos."""
        if self.freeze_timer > 0:
            self.freeze_timer -= dt

        if self.bw_flash_timer > 0:
            self.bw_flash_timer -= dt

        if self.delayed_death_timer > 0:
            self.delayed_death_timer -= dt
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

    def reset_round(self):
        """Limpa estados transitórios mantendo manchas de sangue se desejado."""
        self.is_active = False
        self.freeze_timer = 0.0
        self.bw_flash_timer = 0.0
        self.delayed_death_timer = 0.0
        self.pending_corpse = None
        self.corpses.clear()
