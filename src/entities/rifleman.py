"""
Rifleman (Tanegashima): Mestre atirador armado com arcabuz feudal de mecha.
Tiro fatal de longo alcance (1-Hit Kill). Requer dosar a pólvora e socar a munição
segurando a ação secundária, com salto evasivo de fumaça para reposicionamento.
"""
import math
import random
import pygame
from src.config import (
    COLOR_RIFLE_COAT, COLOR_RIFLE_HAT, COLOR_RIFLE_AURA, COLOR_STEEL, COLOR_WHITE, COLOR_GOLD
)
from src.entities.samurai import (
    Samurai, STATE_IDLE, STATE_WALK, STATE_ATTACK, STATE_RECOVERY, STATE_STUNNED, STATE_DEAD
)
from src.entities.projectile import MusketBulletProjectile
from src.entities.voxel_models import render_voxel_humanoid
from src.effects.particles import SparkParticle

STATE_BACKSTEP = "BACKSTEP"
STATE_RIFLE_ROLL = "RIFLE_ROLL"

class PowderTrap:
    """Trilha de pólvora negra deixada por Teppo no solo que incendeia ao contato."""
    def __init__(self, wx: float, wy: float, owner):
        self.wx = wx
        self.wy = wy
        self.wz = 0.05
        self.owner = owner
        self.radius = 0.85
        self.lifetime = 10.0
        self.is_ignited = False
        self.fire_timer = 2.0
        self.is_active = True

    def ignite(self, particles: list = None):
        if not self.is_ignited:
            self.is_ignited = True
            if particles is not None:
                from src.effects.particles import SparkParticle
                for _ in range(15):
                    particles.append(SparkParticle(self.wx, self.wy, 0.5))

    def update(self, dt: float, fighters: list = None, particles: list = None, banners: list = None, cinematic_director = None) -> bool:
        if not self.is_ignited:
            self.lifetime -= dt
            if self.lifetime <= 0:
                self.is_active = False
                return False
            # Se alguém pisar na pólvora, incendeia!
            if fighters:
                for f in fighters:
                    if getattr(f, "is_alive", False):
                        if math.hypot(f.wx - self.wx, f.wy - self.wy) < (self.radius + f.radius):
                            self.ignite(particles)
                            break
        else:
            # Em chamas
            self.fire_timer -= dt
            if particles is not None and random.random() < 0.4:
                from src.effects.particles import SparkParticle
                particles.append(SparkParticle(self.wx, self.wy, 0.4))
            if fighters:
                for f in fighters:
                    if f is not self.owner and getattr(f, "is_alive", False):
                        if math.hypot(f.wx - self.wx, f.wy - self.wy) < (self.radius + f.radius):
                            hit, dead = f.take_hit((0.0, 0.0), damage=2)
                            if dead:
                                if banners is not None:
                                    from src.effects.particles import FloatingBanner
                                    banners.append(FloatingBanner("POWDER TRAP EXPLOSION!", f.wx, f.wy, wz=1.8, color=(255, 140, 20)))
                                if cinematic_director:
                                    cinematic_director.trigger_fatal_strike(self.owner, f, "HEADSHOT_EXPLODE", (0, 0))
            if self.fire_timer <= 0:
                self.is_active = False
                return False
        return self.is_active

    def render(self, surface: pygame.Surface, camera):
        if not self.is_active:
            return
        from src.isometric.voxel_renderer import draw_voxel_box

        if not self.is_ignited:
            # Sombra circular discreta no piso
            base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
            pygame.draw.ellipse(surface, (14, 16, 15), (base_sx - 10, base_sy - 5, 20, 10))

            # Modelo Voxel 3D: Mina Canister / Sticky Bomb de ferro escuro (Item 11)
            # 1. Base da mina em ferro fundido escuro
            draw_voxel_box(surface, camera, self.wx - 0.12, self.wy - 0.12, 0.0, 0.24, 0.24, 0.10, (36, 38, 42))
            # 2. Tampa central / flange
            draw_voxel_box(surface, camera, self.wx - 0.09, self.wy - 0.09, 0.09, 0.18, 0.18, 0.06, (26, 28, 30))
            # 3. Cordão do pavio trançado enrolado
            draw_voxel_box(surface, camera, self.wx - 0.03, self.wy - 0.03, 0.15, 0.06, 0.06, 0.08, (160, 125, 70))
            # 4. Brasa de fagulha fumegante na ponta do pavio
            ember_p = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.012)
            ember_c = (255, int(130 + ember_p * 90), 30)
            draw_voxel_box(surface, camera, self.wx - 0.02, self.wy - 0.02, 0.22, 0.04, 0.04, 0.04, ember_c, outline=False)

            # Sutil fumaça do pavio
            fsx, fsy = camera.apply(self.wx, self.wy, 0.32)
            pygame.draw.circle(surface, (80, 80, 85), (fsx, int(fsy - ember_p * 3)), 2)
        else:
            # Em chamas: área chamuscada no solo com labaredas dinâmicas (sem "pequeno sol" opaco - Item 11)
            base_sx, base_sy = camera.apply(self.wx, self.wy, 0.0)
            r_px = int(self.radius * 22)
            glow_surf = pygame.Surface((r_px * 2, r_px * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (220, 85, 20, 130), (0, r_px // 2, r_px * 2, r_px))
            pygame.draw.ellipse(glow_surf, (255, 180, 40, 160), (r_px // 4, r_px * 3 // 4, r_px, r_px // 2))
            surface.blit(glow_surf, (base_sx - r_px, base_sy - r_px // 2))


class Rifleman(Samurai):
    def __init__(self, wx: float, wy: float):
        super().__init__(wx, wy, name="Teppo")
        self.char_type = "teppo"
        self.speed = 4.3  # Velocidade ágil para caçar pólvora na arena

        # Mecânica de Munição e Pólvora
        self.has_ammo = True           # Inicia CARREGADO com munição
        self.cocking_timer = 0.0
        self.reload_time = 0.0
        self.is_reloading = False
        self.reload_progress = 0.0

        # Subterfúgio Evasivo
        self.backstep_cooldown = 0.60   # Calibrado: reposicionamento ágil
        self.backstep_timer = 0.0
        self.backstep_duration = 0.20

        # Ação Secundária: Armadilha de Pólvora
        self.trap_cooldown = 3.0
        self.trap_timer = 0.0

        # Terceira Ação: Rolamento com Recarga (Tumble Roll)
        self.roll_speed = 10.8
        self.roll_duration = 0.22
        self.roll_dir_x = 1.0
        self.roll_dir_y = 0.0

    def trigger_powder_trap(self, target_wx: float = 0.0, target_wy: float = 0.0, traps: list = None, particles: list = None):
        """Ação Secundária: Black Powder Ground Trap — arma sticky bomb no solo (gasta 1 carga de pólvora - Item 11)."""
        if not self.can_act() or self.trap_timer > 0 or not self.has_ammo:
            return
        self.trap_timer = self.trap_cooldown
        self.has_ammo = False  # Gasta 1 carga de pólvora!

        # Suporte a chamada posicional flexível (ex: trigger_powder_trap(traps_list))
        trap_list = traps
        if isinstance(target_wx, list):
            trap_list = target_wx
        elif isinstance(target_wy, list):
            trap_list = target_wy

        if trap_list is not None:
            trap_list.append(PowderTrap(self.wx, self.wy, owner=self))
        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.35))

    def trigger_roll(self, dir_x: float, dir_y: float, particles: list = None):
        """Terceira Ação: Tumble & Reload Roll — rolamento evasivo com recarga tática ao concluir."""
        if not self.is_alive or self.state in (STATE_RIFLE_ROLL, STATE_STUNNED, STATE_DEAD, STATE_ATTACK) or self.dash_recovery_timer > 0:
            return

        if dir_x == 0 and dir_y == 0:
            dir_x, dir_y = -self.facing_x, -self.facing_y
        else:
            mag = math.hypot(dir_x, dir_y)
            if mag > 0.001:
                dir_x /= mag
                dir_y /= mag

        self.state = STATE_RIFLE_ROLL
        self.state_timer = self.roll_duration
        self.roll_dir_x = dir_x
        self.roll_dir_y = dir_y
        self.facing_x = dir_x
        self.facing_y = dir_y
        self.is_invulnerable_dodge = True
        self.hitbox_active = False

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.35))

    def trigger_tumble_roll(self, dir_x: float, dir_y: float, particles: list = None):
        self.trigger_roll(dir_x, dir_y, particles)

    def check_powder_pickup(self, pouches: list, particles: list = None) -> bool:
        """Verifica se Teppo passou por cima de um saquinho de pólvora para carregar o arcabuz."""
        if self.has_ammo or not self.is_alive:
            return False
        for pouch in pouches:
            if getattr(pouch, "is_active", False):
                if math.hypot(self.wx - pouch.wx, self.wy - pouch.wy) < (pouch.radius + self.radius + 0.25):
                    pouch.is_active = False
                    pouch.wx = -999.0
                    pouch.wy = -999.0
                    pouch.respawn_timer = 10.0
                    self.has_ammo = True
                    self.cocking_timer = 0.40
                    if particles is not None:
                        for _ in range(14):
                            particles.append(SparkParticle(self.wx, self.wy, 0.6))
                    return True
        return False

    def can_act(self) -> bool:
        return self.is_alive and self.state not in (STATE_RECOVERY, STATE_STUNNED, STATE_DEAD) and self.dash_recovery_timer <= 0

    def trigger_shoot(self, target_wx: float, target_wy: float, projectiles: list, particles: list = None):
        """Ataque Primário: Disparo fatal de arcabuz se tiver munição e engatilhado, ou coronhada defensiva se descarregado."""
        if not self.can_act():
            return

        if not self.has_ammo or self.cocking_timer > 0:
            # Se descarregado, desfere coronhada tática; se ainda engatilhando, aguarda
            if not self.has_ammo:
                self.trigger_rifle_butt(target_wx, target_wy, particles)
            return

        self.set_facing(target_wx, target_wy)
        self.has_ammo = False
        self.is_reloading = False
        self.reload_progress = 0.0

        self.state = STATE_RECOVERY
        self.state_timer = 0.38

        # Recuo da pólvora
        self.wx -= self.facing_x * 0.4
        self.wy -= self.facing_y * 0.4

        # Criar projétil
        bx = self.wx + self.facing_x * 0.65
        by = self.wy + self.facing_y * 0.65
        bullet = MusketBulletProjectile(bx, by, wz=0.55, dir_x=self.facing_x, dir_y=self.facing_y, owner=self)
        projectiles.append(bullet)

        if particles is not None:
            for _ in range(14):
                particles.append(SparkParticle(bx, by, 0.55))

    def trigger_rifle_butt(self, target_wx: float, target_wy: float, particles: list = None):
        """Coronhada Defensiva: Golpe de madeira de curto alcance que atordoa e afasta o adversário."""
        if not self.can_act():
            return
        self.set_facing(target_wx, target_wy)
        self.state = STATE_ATTACK
        self.state_timer = 0.20
        self.hitbox_active = True
        self.hitbox_radius = 1.15
        self.is_rifle_butt = True
        self.hitbox_center = (self.wx + self.facing_x * 0.75, self.wy + self.facing_y * 0.75)
        self.slash_dir = (self.facing_x, self.facing_y)
        if particles is not None:
            for _ in range(6):
                particles.append(SparkParticle(self.hitbox_center[0], self.hitbox_center[1], 0.3))

    def trigger_reload_hold(self):
        """Ativado enquanto o jogador mantém pressionado o botão de ação secundária."""
        if not self.can_act() or self.has_ammo:
            return
        self.is_reloading = True

    def trigger_evasive_backstep(self, particles: list = None):
        """Subterfúgio: Salto tático para trás com fumaça sem cancelar a recarga."""
        if not self.is_alive or self.backstep_timer > 0:
            return

        self.backstep_timer = self.backstep_cooldown
        self.state = STATE_BACKSTEP
        self.state_timer = self.backstep_duration

        if particles is not None:
            for _ in range(8):
                particles.append(SparkParticle(self.wx, self.wy, 0.3))

    def update(self, dt: float, game_map, particles: list = None):
        if not self.is_alive:
            return

        self.update_stealth(game_map)

        if self.dash_recovery_timer > 0:
            self.dash_recovery_timer -= dt

        if self.backstep_timer > 0:
            self.backstep_timer -= dt

        if self.trap_timer > 0:
            self.trap_timer -= dt

        if self.cocking_timer > 0:
            self.cocking_timer -= dt

        if self.state == STATE_ATTACK:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.hitbox_active = False
                self.is_rifle_butt = False

        elif self.state == STATE_RIFLE_ROLL:
            self.state_timer -= dt
            step = self.roll_speed * dt
            new_wx = self.wx + self.roll_dir_x * step
            new_wy = self.wy + self.roll_dir_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            if self.state_timer <= 0:
                self.state = STATE_IDLE
                self.is_invulnerable_dodge = False
                self.dash_recovery_timer = self.dash_recovery_duration
                # Rolamento tático conclui recarga de emergência!
                if not self.has_ammo:
                    self.has_ammo = True
                    self.cocking_timer = 0.30
                    if particles is not None:
                        for _ in range(12):
                            particles.append(SparkParticle(self.wx, self.wy, 0.45))

        elif self.state == STATE_BACKSTEP:
            self.state_timer -= dt
            # Recuo evasivo na direção oposta ao olhar
            step = 7.5 * dt
            new_wx = self.wx - self.facing_x * step
            new_wy = self.wy - self.facing_y * step

            hit_col = False
            for r in game_map.rocks:
                if r.check_collision(new_wx, new_wy, self.radius)[0]:
                    hit_col = True; break
            if game_map.well and game_map.well.check_collision(new_wx, new_wy, self.radius)[0]:
                hit_col = True

            if not hit_col:
                self.wx = max(1.0, min(game_map.cols - 1.0, new_wx))
                self.wy = max(1.0, min(game_map.rows - 1.0, new_wy))

            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_RECOVERY:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

        elif self.state == STATE_STUNNED:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = STATE_IDLE

    def render(self, surface: pygame.Surface, camera):
        """Renderiza o Rifleman e indicador de munição/pólvora."""
        if self.is_hidden:
            sx, sy = camera.apply(self.wx, self.wy, 1.4)
            pygame.draw.circle(surface, (120, 220, 100), (sx, sy), 3)

        render_voxel_humanoid(
            surface, camera,
            self.wx, self.wy, self.wz,
            self.facing_x, self.facing_y,
            self.state, self.state_timer, self.is_alive,
            char_type="rifleman",
            walk_timer=self.walk_cycle,
            alpha=self.alpha,
            is_moving=self.is_moving,
            extra_props={"has_ammo": self.has_ammo, "is_reloading": False}
        )

        # Indicador de Munição na cabeça do Teppo
        bx, by = camera.apply(self.wx, self.wy, 1.45)
        if self.has_ammo:
            # Bala de chumbo dourada carregada
            pygame.draw.circle(surface, COLOR_GOLD, (bx, by), 5)
            pygame.draw.circle(surface, (255, 255, 200), (bx - 1, by - 1), 2)
        else:
            # Silhueta vazia cinza/vermelha indicando necessidade de coletar pólvora
            pygame.draw.circle(surface, (140, 50, 50), (bx, by), 4, 1)
