import pygame
import math
import random
from typing import Tuple, Optional, List
from config import *
from asset_manager import asset_manager
from sound_manager import sound_manager
from effects import effect_manager
from sprite_groups import sprite_groups
from utils import *

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], 
                 damage: int = 1, owner: str = "player", projectile_type: str = "basic"):
        super().__init__()
        self.x = x
        self.y = y
        self.velocity_x, self.velocity_y = velocity
        self.damage = damage
        self.owner = owner
        self.projectile_type = projectile_type
        self.penetration = 1
        self.lifetime = 300  # frames
        self.homing = False
        self.homing_strength = 0.1
        self.target = None
        
        self.setup_sprite()
        self.create_trail = False
        self.trail_color = YELLOW
        
    def setup_sprite(self):
        if self.owner == "player":
            self.image = asset_manager.get_image("bullet") or asset_manager.create_placeholder_image("bullet")
        else:
            self.image = asset_manager.get_image("enemy_bullet") or asset_manager.create_placeholder_image("enemy_bullet")
        
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.x), int(self.y))
        
        # Scale based on projectile type
        if self.projectile_type == "laser":
            self.image = pygame.transform.scale(self.image, (3, 15))
        elif self.projectile_type == "heavy":
            self.image = pygame.transform.scale(self.image, (8, 12))
    
    def update(self):
        if self.homing and self.target:
            self.apply_homing()
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        self.rect.center = (int(self.x), int(self.y))
        
        if self.create_trail:
            effect_manager.create_bullet_trail(self.x, self.y, 
                                             (self.velocity_x, self.velocity_y), 
                                             self.trail_color)
        
        self.lifetime -= 1
        if self.lifetime <= 0 or self.is_offscreen():
            self.kill()
    
    def apply_homing(self):
        if self.target and hasattr(self.target, 'rect'):
            target_pos = self.target.rect.center
            current_pos = (self.x, self.y)
            
            direction = get_direction_vector(current_pos, target_pos)
            
            # Blend current velocity with homing direction
            self.velocity_x = lerp(self.velocity_x, direction[0] * BULLET_SPEED, self.homing_strength)
            self.velocity_y = lerp(self.velocity_y, direction[1] * BULLET_SPEED, self.homing_strength)
    
    def is_offscreen(self) -> bool:
        return (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or 
                self.rect.right < 0 or self.rect.left > SCREEN_WIDTH)
    
    def on_hit(self, target):
        effect_manager.create_hit_effect(self.rect.centerx, self.rect.centery)
        
        self.penetration -= 1
        if self.penetration <= 0:
            self.kill()

class Bullet(Projectile):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float] = (0, -BULLET_SPEED), 
                 damage: int = 1):
        super().__init__(x, y, velocity, damage, "player", "basic")
        self.trail_color = YELLOW
        self.create_trail = True

class LaserBullet(Projectile):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float] = (0, -BULLET_SPEED * 1.5), 
                 damage: int = 2):
        super().__init__(x, y, velocity, damage, "player", "laser")
        self.trail_color = RED
        self.create_trail = True
        self.penetration = 3

class HeavyBullet(Projectile):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float] = (0, -BULLET_SPEED * 0.8), 
                 damage: int = 3):
        super().__init__(x, y, velocity, damage, "player", "heavy")
        self.trail_color = ORANGE
        self.create_trail = True
        self.penetration = 2

class HomingMissile(Projectile):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float] = (0, -BULLET_SPEED * 0.7), 
                 damage: int = 4):
        super().__init__(x, y, velocity, damage, "player", "homing")
        self.homing = True
        self.homing_strength = 0.05
        self.trail_color = CYAN
        self.create_trail = True
        self.find_target()
    
    def find_target(self):
        # Find closest enemy
        enemies = sprite_groups.get_group("enemies")
        closest_enemy = None
        closest_distance = float('inf')
        
        for enemy in enemies:
            dist = distance((self.x, self.y), enemy.rect.center)
            if dist < closest_distance:
                closest_distance = dist
                closest_enemy = enemy
        
        self.target = closest_enemy
    
    def update(self):
        if not self.target or self.target not in sprite_groups.get_group("enemies"):
            self.find_target()
        
        super().update()

class EnemyBullet(Projectile):
    def __init__(self, x: float, y: float, target_pos: Tuple[float, float], 
                 speed: float = 5, damage: int = 10):
        # Calculate direction to target
        direction = get_direction_vector((x, y), target_pos)
        velocity = (direction[0] * speed, direction[1] * speed)
        
        super().__init__(x, y, velocity, damage, "enemy", "basic")
        self.trail_color = RED
        self.create_trail = True

class SpreadBullet(Projectile):
    def __init__(self, x: float, y: float, angle: float, speed: float = BULLET_SPEED, 
                 damage: int = 1, owner: str = "player"):
        velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        super().__init__(x, y, velocity, damage, owner, "spread")
        self.trail_color = GREEN if owner == "player" else RED
        self.create_trail = True

class PlasmaBall(Projectile):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], 
                 damage: int = 5, owner: str = "player"):
        super().__init__(x, y, velocity, damage, owner, "plasma")
        self.size = 12
        self.create_plasma_sprite()
        self.trail_color = PURPLE
        self.create_trail = True
        self.penetration = 5
    
    def create_plasma_sprite(self):
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        center = (self.size, self.size)
        
        # Draw plasma ball with glow effect
        for i in range(3):
            radius = self.size - i * 2
            alpha = 200 - i * 50
            color = (*PURPLE, alpha)
            pygame.draw.circle(self.image, color, center, radius)
        
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.x), int(self.y))
    
    def on_hit(self, target):
        # Create plasma explosion on hit
        effect_manager.create_explosion(self.rect.centerx, self.rect.centery, 25, "plasma")
        super().on_hit(target)

class RocketMissile(Projectile):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], 
                 damage: int = 8, owner: str = "player"):
        super().__init__(x, y, velocity, damage, owner, "rocket")
        self.explosion_radius = 40
        self.trail_color = ORANGE
        self.create_trail = True
        self.engine_trail_timer = 0
    
    def update(self):
        super().update()
        
        # Create engine trail
        self.engine_trail_timer += 1
        if self.engine_trail_timer >= 3:
            self.engine_trail_timer = 0
            effect_manager.create_engine_trail(
                self.x - self.velocity_x * 0.3, 
                self.y - self.velocity_y * 0.3, 
                ORANGE
            )
    
    def on_hit(self, target):
        # Create explosion damage in radius
        self.create_explosion_damage()
        effect_manager.create_explosion(self.rect.centerx, self.rect.centery, 
                                      self.explosion_radius, "rocket")
        sound_manager.play_explosion_sound("large")
        self.kill()
    
    def create_explosion_damage(self):
        # Damage all enemies in explosion radius
        enemies = sprite_groups.get_group("enemies")
        for enemy in enemies:
            if distance(self.rect.center, enemy.rect.center) <= self.explosion_radius:
                if hasattr(enemy, 'damage'):
                    enemy.damage(self.damage)

class WeaponSystem:
    def __init__(self, owner):
        self.owner = owner
        self.weapon_type = WeaponType.BASIC
        self.fire_rate = FIRE_RATE_BASE
        self.last_shot = 0
        self.ammo = -1  # -1 means unlimited
        self.upgrade_level = 1
        self.spread_angle = 0.2
        self.burst_count = 1
        self.burst_delay = 100
        self.current_burst = 0
        self.burst_timer = 0
    
    def can_fire(self) -> bool:
        current_time = pygame.time.get_ticks()
        if self.current_burst > 0:
            return current_time - self.last_shot >= self.burst_delay
        return current_time - self.last_shot >= self.fire_rate
    
    def fire(self, x: float, y: float, target_pos: Optional[Tuple[float, float]] = None) -> List[Projectile]:
        if not self.can_fire():
            return []
        
        if self.ammo == 0:
            return []
        
        projectiles = []
        
        if self.weapon_type == WeaponType.BASIC:
            projectiles = self.fire_basic(x, y)
        elif self.weapon_type == WeaponType.DOUBLE:
            projectiles = self.fire_double(x, y)
        elif self.weapon_type == WeaponType.TRIPLE:
            projectiles = self.fire_triple(x, y)
        elif self.weapon_type == WeaponType.SPREAD:
            projectiles = self.fire_spread(x, y)
        elif self.weapon_type == WeaponType.LASER:
            projectiles = self.fire_laser(x, y)
        elif self.weapon_type == WeaponType.HOMING:
            projectiles = self.fire_homing(x, y)
        
        if projectiles:
            self.last_shot = pygame.time.get_ticks()
            if self.ammo > 0:
                self.ammo -= 1
            
            # Handle burst firing
            if self.current_burst > 0:
                self.current_burst -= 1
            else:
                self.current_burst = self.burst_count - 1
            
            # Play appropriate sound
            sound_manager.play_shoot_sound(self.weapon_type.name.lower())
            
            # Add muzzle flash
            effect_manager.create_muzzle_flash(x, y)
        
        return projectiles
    
    def fire_basic(self, x: float, y: float) -> List[Projectile]:
        bullet = Bullet(x, y)
        return [bullet]
    
    def fire_double(self, x: float, y: float) -> List[Projectile]:
        bullet1 = Bullet(x - 10, y)
        bullet2 = Bullet(x + 10, y)
        return [bullet1, bullet2]
    
    def fire_triple(self, x: float, y: float) -> List[Projectile]:
        bullet1 = Bullet(x, y)
        bullet2 = SpreadBullet(x, y, -math.pi/2 - self.spread_angle)
        bullet3 = SpreadBullet(x, y, -math.pi/2 + self.spread_angle)
        return [bullet1, bullet2, bullet3]
    
    def fire_spread(self, x: float, y: float) -> List[Projectile]:
        projectiles = []
        bullet_count = 5 + self.upgrade_level
        angle_step = self.spread_angle * 2 / (bullet_count - 1)
        
        for i in range(bullet_count):
            angle = -math.pi/2 - self.spread_angle + i * angle_step
            bullet = SpreadBullet(x, y, angle)
            projectiles.append(bullet)
        
        return projectiles
    
    def fire_laser(self, x: float, y: float) -> List[Projectile]:
        laser = LaserBullet(x, y)
        return [laser]
    
    def fire_homing(self, x: float, y: float) -> List[Projectile]:
        missile = HomingMissile(x, y)
        return [missile]
    
    def upgrade_weapon(self, new_type: WeaponType):
        self.weapon_type = new_type
        self.upgrade_level += 1
        
        # Adjust stats based on weapon type
        if new_type == WeaponType.LASER:
            self.fire_rate = int(FIRE_RATE_BASE * 0.8)
        elif new_type == WeaponType.SPREAD:
            self.fire_rate = int(FIRE_RATE_BASE * 1.2)
        elif new_type == WeaponType.HOMING:
            self.fire_rate = int(FIRE_RATE_BASE * 1.5)
    
    def set_ammo(self, amount: int):
        self.ammo = amount
    
    def get_ammo(self) -> int:
        return self.ammo
    
    def has_unlimited_ammo(self) -> bool:
        return self.ammo == -1

class EnemyWeaponSystem:
    def __init__(self, owner):
        self.owner = owner
        self.weapon_type = "basic"
        self.fire_rate = 2000
        self.last_shot = 0
        self.burst_count = 1
        self.accuracy = 0.9
    
    def can_fire(self) -> bool:
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot >= self.fire_rate
    
    def fire(self, x: float, y: float, target_pos: Tuple[float, float]) -> List[Projectile]:
        if not self.can_fire():
            return []
        
        projectiles = []
        
        if self.weapon_type == "basic":
            projectiles = self.fire_basic(x, y, target_pos)
        elif self.weapon_type == "spread":
            projectiles = self.fire_spread(x, y, target_pos)
        elif self.weapon_type == "burst":
            projectiles = self.fire_burst(x, y, target_pos)
        
        if projectiles:
            self.last_shot = pygame.time.get_ticks()
            sound_manager.play_enemy_sound(self.owner.__class__.__name__.lower(), "shoot")
        
        return projectiles
    
    def fire_basic(self, x: float, y: float, target_pos: Tuple[float, float]) -> List[Projectile]:
        # Add inaccuracy
        offset_x = random.uniform(-20, 20) * (1 - self.accuracy)
        offset_y = random.uniform(-20, 20) * (1 - self.accuracy)
        
        adjusted_target = (target_pos[0] + offset_x, target_pos[1] + offset_y)
        bullet = EnemyBullet(x, y, adjusted_target)
        return [bullet]
    
    def fire_spread(self, x: float, y: float, target_pos: Tuple[float, float]) -> List[Projectile]:
        projectiles = []
        for i in range(3):
            offset_x = (i - 1) * 30
            target = (target_pos[0] + offset_x, target_pos[1])
            bullet = EnemyBullet(x, y, target)
            projectiles.append(bullet)
        return projectiles
    
    def fire_burst(self, x: float, y: float, target_pos: Tuple[float, float]) -> List[Projectile]:
        projectiles = []
        for i in range(self.burst_count):
            bullet = EnemyBullet(x, y, target_pos, speed=6)
            projectiles.append(bullet)
        return projectiles

def create_bullet_for_weapon(weapon_type: WeaponType, x: float, y: float, **kwargs) -> Projectile:
    if weapon_type == WeaponType.BASIC:
        return Bullet(x, y, **kwargs)
    elif weapon_type == WeaponType.LASER:
        return LaserBullet(x, y, **kwargs)
    elif weapon_type == WeaponType.HOMING:
        return HomingMissile(x, y, **kwargs)
    else:
        return Bullet(x, y, **kwargs)

def add_projectile_to_game(projectile: Projectile):
    sprite_groups.add_sprite(projectile, ["all"])
    
    if projectile.owner == "player":
        sprite_groups.add_sprite(projectile, ["bullets"])
    else:
        sprite_groups.add_sprite(projectile, ["enemy_bullets"])