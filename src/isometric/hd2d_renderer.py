"""
Módulo de Renderização de Sprites HD-2D Isométricos (Billboards 2.5D).
Projeta combatentes com sprites em pixel art de alta definição ancorados no solo,
com sombras elípticas dinâmicas, espelhamento horizontal, controle de animações por estado,
translucidez para camuflagem e suporte a pós-imagens (Zanzou).
"""
import os
import pygame
from src.config import ENABLE_HD2D_SPRITES, HD2D_SPRITE_TARGET_HEIGHT, HD2D_SHADOW_COLOR

# Mapeamento de identificadores de personagens para diretórios em assets/sprites/
CHAR_SPRITE_MAP = {
    "kenshin": "kenshi",
    "kenshi": "kenshi",
    "red": "kenshi",
    "purple": "murasaki",
    "murasaki": "murasaki",
}

# Cache de superfícies carregadas: (char_dir, state, flipped, alpha) -> pygame.Surface
_HD2D_CACHE: dict[tuple, pygame.Surface] = {}
_SHADOW_CACHE: pygame.Surface | None = None

def get_hd2d_shadow_surface() -> pygame.Surface:
    """Retorna superfície em cache da sombra elíptica de contato com o solo."""
    global _SHADOW_CACHE
    if _SHADOW_CACHE is None:
        sw, sh = 46, 20
        _SHADOW_CACHE = pygame.Surface((sw, sh), pygame.SRCALPHA)
        color = HD2D_SHADOW_COLOR if len(HD2D_SHADOW_COLOR) == 4 else (*HD2D_SHADOW_COLOR[:3], 130)
        pygame.draw.ellipse(_SHADOW_CACHE, color, (0, 0, sw, sh))
    return _SHADOW_CACHE

class HD2DSpriteRenderer:
    """Gerenciador de renderização HD-2D de combatentes."""

    @staticmethod
    def has_sprite(char_type: str) -> bool:
        """Verifica se o personagem possui conjunto de sprites HD-2D disponíveis."""
        if not ENABLE_HD2D_SPRITES:
            return False
        char_key = CHAR_SPRITE_MAP.get(char_type.lower())
        if not char_key:
            return False
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sprite_dir = os.path.join(base_dir, "assets", "sprites", char_key)
        return os.path.exists(os.path.join(sprite_dir, "idle.png"))

    @staticmethod
    def load_frame(char_key: str, frame_name: str, flip: bool = False, alpha: int = 255) -> pygame.Surface | None:
        """Carrega e retorna o frame com cache automático, espelhamento e alfa."""
        cache_key = (char_key, frame_name, flip, alpha)
        if cache_key in _HD2D_CACHE:
            return _HD2D_CACHE[cache_key]

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base_dir, "assets", "sprites", char_key, f"{frame_name}.png")

        if not os.path.exists(path):
            # Fallback inteligente para variações de frame
            if frame_name.startswith("back_"):
                # Tenta versão frontal correspondente ou back_idle
                front_equiv = frame_name.replace("back_", "front_")
                res = HD2DSpriteRenderer.load_frame(char_key, front_equiv, flip, alpha)
                if res is not None:
                    return res
                if frame_name != "back_idle":
                    res = HD2DSpriteRenderer.load_frame(char_key, "back_idle", flip, alpha)
                    if res is not None:
                        return res
            elif frame_name.startswith("front_"):
                base_equiv = frame_name.replace("front_", "")
                res = HD2DSpriteRenderer.load_frame(char_key, base_equiv, flip, alpha)
                if res is not None:
                    return res

            if frame_name != "idle":
                return HD2DSpriteRenderer.load_frame(char_key, "idle", flip, alpha)
            return None

        try:
            raw = pygame.image.load(path)
            if pygame.display.get_surface() is not None:
                try:
                    raw = raw.convert_alpha()
                except Exception:
                    pass

            # Redimensionamento se necessário baseado na altura alvo
            if HD2D_SPRITE_TARGET_HEIGHT > 0 and raw.get_height() != HD2D_SPRITE_TARGET_HEIGHT and frame_name == "idle":
                target_h = HD2D_SPRITE_TARGET_HEIGHT
                ratio = target_h / float(raw.get_height())
                target_w = max(1, int(round(raw.get_width() * ratio)))
                surf = pygame.transform.smoothscale(raw, (target_w, target_h))
            else:
                surf = raw

            if flip:
                surf = pygame.transform.flip(surf, True, False)

            if alpha < 255:
                alpha_surf = surf.copy()
                alpha_surf.set_alpha(alpha)
                surf = alpha_surf

            _HD2D_CACHE[cache_key] = surf
            return surf
        except Exception as e:
            print(f"[HD2D] Erro ao carregar frame {path}: {e}")
            return None

    @staticmethod
    def render_fighter(
        surface: pygame.Surface,
        camera,
        fighter,
        char_type: str,
        alpha: int = 255,
        custom_wx: float = None,
        custom_wy: float = None,
        custom_state: str = None,
        custom_facing_x: float = None,
        custom_facing_y: float = None
    ) -> bool:
        """
        Renderiza um guerreiro utilizando sprites HD-2D.
        Retorna True se renderizou com sucesso, ou False caso deva recorrer ao fallback de Voxel.
        """
        if not ENABLE_HD2D_SPRITES:
            return False

        char_key = CHAR_SPRITE_MAP.get(char_type.lower())
        if not char_key or not HD2DSpriteRenderer.has_sprite(char_type):
            return False

        wx = fighter.wx if custom_wx is None else custom_wx
        wy = fighter.wy if custom_wy is None else custom_wy
        wz = getattr(fighter, "wz", 0.0)
        facing_x = fighter.facing_x if custom_facing_x is None else custom_facing_x
        facing_y = fighter.facing_y if custom_facing_y is None else custom_facing_y
        state = fighter.state if custom_state is None else custom_state
        is_alive = getattr(fighter, "is_alive", True)
        walk_timer = getattr(fighter, "walk_cycle", 0.0)

        # 1. Determinar quadrante isométrico com histerese (evita trepidação/jitter)
        # No plano isométrico 2:1:
        # screen_dx = facing_x - facing_y (Positivo = Direita, Negativo = Esquerda)
        # screen_dy = facing_x + facing_y (Positivo = Frente/Sul, Negativo = Costas/Norte)
        screen_dx = facing_x - facing_y
        screen_dy = facing_x + facing_y

        prev_flip = getattr(fighter, "_hd2d_flip", False)
        if screen_dx < -0.15:
            flip = True
        elif screen_dx > 0.15:
            flip = False
        else:
            flip = prev_flip
        fighter._hd2d_flip = flip

        prev_back = getattr(fighter, "_hd2d_is_back", False)
        if screen_dy < -0.20:
            is_back = True
        elif screen_dy > 0.10:
            is_back = False
        else:
            is_back = prev_back
        fighter._hd2d_is_back = is_back
        dir_prefix = "back_" if is_back else "front_"

        # 2. Determinar o frame do sprite com base no estado e na direção
        if not is_alive or state == "DEAD":
            frame_name = "dead"
        elif state == "STUNNED":
            frame_name = "stunned"
        elif state in ("ATTACK", "SHUKUCHI", "DASH"):
            frame_name = f"{dir_prefix}attack"
        elif state == "RECOVERY":
            frame_name = "recovery"
        elif state == "WALK" or getattr(fighter, "is_moving", False):
            # Cadência suave de caminhada (8 FPS, 125ms por passada)
            frame_idx = int(walk_timer * 0.8) % 4
            frame_name = f"{dir_prefix}walk_{frame_idx}"
        else:
            frame_name = f"{dir_prefix}idle"

        # 3. Carregar o sprite (com fallback automático se necessário)
        sprite = HD2DSpriteRenderer.load_frame(char_key, frame_name, flip=flip, alpha=alpha)
        if sprite is None:
            # Fallback para o frame frontal básico
            sprite = HD2DSpriteRenderer.load_frame(char_key, "idle", flip=flip, alpha=alpha)
        if sprite is None:
            return False

        # 4. Ponto na tela relativo à câmera
        fx, fy = camera.apply(wx, wy, wz)
        sw, sh = sprite.get_size()

        # 5. Sombra de solo elíptica (ground contact shadow)
        if wz <= 0.2 and state != "DEAD":
            gx, gy = camera.apply(wx, wy, 0.0)
            shadow = get_hd2d_shadow_surface()
            surface.blit(shadow, (gx - shadow.get_width() // 2, gy - shadow.get_height() // 2))

        # 6. Blit do sprite ancorado pelos pés no solo
        foot_offset_y = 6
        dest_x = fx - sw // 2
        dest_y = fy - sh + foot_offset_y
        surface.blit(sprite, (dest_x, dest_y))

        return True
