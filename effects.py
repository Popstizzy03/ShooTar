import pygame
import math
import random
from typing import List, Tuple, Optional
from config import *
from sprite_groups import sprite_groups
from utils import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], color: Tuple[int, int, int], 
                 size: float, lifetime: int, gravity: float = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.velocity_x, self.velocity_y = velocity
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.gravity = gravity
        self.alpha = 255
        
        self.image = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(self.image, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
    
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += self.gravity
        
        self.rect.center = (int(self.x), int(self.y))
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.update_image()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, size: int, explosion_type: str = "normal"):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.explosion_type = explosion_type
        self.frame = 0
        self.max_frames = 15
        self.frame_rate = 2
        self.frame_counter = 0
        
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.colors = self.get_explosion_colors()
        self.create_particles()
        
        self.update_image()
    
    def get_explosion_colors(self) -> List[Tuple[int, int, int]]:
        if self.explosion_type == "boss":
            return [WHITE, YELLOW, ORANGE, RED, PURPLE]
        elif self.explosion_type == "player":
            return [CYAN, BLUE, WHITE, YELLOW]
        elif self.explosion_type == "enemy":
            return [RED, ORANGE, YELLOW, WHITE]
        else:
            return [YELLOW, ORANGE, RED, WHITE]
    
    def create_particles(self):
        particle_count = min(30, self.size // 2)
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            color = random.choice(self.colors)
            size = random.uniform(1, 4)
            lifetime = random.randint(20, 40)
            
            particle = Particle(self.x, self.y, velocity, color, size, lifetime, 0.1)
            sprite_groups.add_sprite(particle, ["all", "particles"])
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        
        if self.frame < self.max_frames:
            progress = self.frame / self.max_frames
            current_radius = int(self.size * 0.8 * ease_out(progress))
            
            # Draw multiple explosion rings
            for i, color in enumerate(self.colors):
                ring_radius = max(1, current_radius - i * 3)
                alpha = int(255 * (1 - progress) * (1 - i * 0.2))
                color_with_alpha = (*color, max(0, alpha))
                
                if ring_radius > 0:
                    pygame.draw.circle(self.image, color_with_alpha, 
                                     (self.size // 2, self.size // 2), ring_radius)
    
    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_rate:
            self.frame_counter = 0
            self.frame += 1
            
            if self.frame >= self.max_frames:
                self.kill()
            else:
                self.update_image()

class EngineTrail(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = BLUE):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 20
        self.max_lifetime = 20
        self.size = 3
        
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(self.image, color_with_alpha, (3, 3), self.size)
    
    def update(self):
        self.y += 2  # Move trail downward
        self.rect.center = (int(self.x), int(self.y))
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.update_image()

class MuzzleFlash(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, angle: float = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.angle = angle
        self.lifetime = 5
        self.max_lifetime = 5
        self.size = 10
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            
            # Draw flash as a star shape
            center = (10, 10)
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                if i % 2 == 0:
                    radius = self.size
                else:
                    radius = self.size // 2
                
                x = center[0] + math.cos(angle + self.angle) * radius
                y = center[1] + math.sin(angle + self.angle) * radius
                points.append((x, y))
            
            pygame.draw.polygon(self.image, (255, 255, 0, alpha), points)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.update_image()

class PowerUpGlow(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], size: int = 30):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.time = 0
        
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        
        # Create pulsing glow effect
        pulse = (math.sin(self.time * 0.2) + 1) * 0.5
        current_size = int(self.size * (0.8 + pulse * 0.4))
        alpha = int(100 * pulse)
        
        center = (self.size, self.size)
        color_with_alpha = (*self.color, alpha)
        
        pygame.draw.circle(self.image, color_with_alpha, center, current_size)
        pygame.draw.circle(self.image, (*self.color, alpha // 2), center, current_size + 5)
    
    def update(self):
        self.time += 1
        self.update_image()

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.original_duration = 0
    
    def start(self, intensity: int, duration: int):
        self.intensity = intensity
        self.duration = duration
        self.original_duration = duration
    
    def update(self) -> Tuple[int, int]:
        if self.duration > 0:
            self.duration -= 1
            progress = self.duration / self.original_duration
            current_intensity = int(self.intensity * progress)
            
            return (
                random.randint(-current_intensity, current_intensity),
                random.randint(-current_intensity, current_intensity)
            )
        return (0, 0)
    
    def is_active(self) -> bool:
        return self.duration > 0

class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], 
                 color: Tuple[int, int, int] = RED, width: int = 5):
        super().__init__()
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.width = width
        self.lifetime = 10
        self.max_lifetime = 10
        
        # Calculate beam dimensions
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = math.sqrt(dx * dx + dy * dy)
        
        self.image = pygame.Surface((int(length) + width, width * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
        
        self.angle = math.atan2(dy, dx)
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color, alpha)
            
            # Draw the laser beam
            length = int(math.sqrt((self.end_pos[0] - self.start_pos[0])**2 + 
                                 (self.end_pos[1] - self.start_pos[1])**2))
            
            # Draw main beam
            pygame.draw.rect(self.image, color_with_alpha, 
                           (0, self.width // 2, length, self.width))
            
            # Draw glow effect
            glow_color = (*self.color, alpha // 3)
            pygame.draw.rect(self.image, glow_color, 
                           (0, 0, length, self.width * 2))
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.update_image()

class BulletTrail(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, velocity: Tuple[float, float], 
                 color: Tuple[int, int, int] = YELLOW):
        super().__init__()
        self.x = x
        self.y = y
        self.velocity_x, self.velocity_y = velocity
        self.color = color
        self.lifetime = 15
        self.max_lifetime = 15
        self.size = 2
        
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(self.image, color_with_alpha, (2, 2), self.size)
    
    def update(self):
        self.x += self.velocity_x * 0.5
        self.y += self.velocity_y * 0.5
        self.rect.center = (int(self.x), int(self.y))
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.update_image()

class HitEffect(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = WHITE):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 8
        self.max_lifetime = 8
        self.size = 15
        
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            size = int(self.size * (1 - self.lifetime / self.max_lifetime))
            
            center = (15, 15)
            color_with_alpha = (*self.color, alpha)
            
            # Draw impact burst
            for i in range(6):
                angle = i * math.pi / 3
                end_x = center[0] + math.cos(angle) * size
                end_y = center[1] + math.sin(angle) * size
                pygame.draw.line(self.image, color_with_alpha, center, (end_x, end_y), 2)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.update_image()

class EffectManager:
    def __init__(self):
        self.screen_shake = ScreenShake()
    
    def create_explosion(self, x: float, y: float, size: int, explosion_type: str = "normal"):
        explosion = Explosion(x, y, size, explosion_type)
        sprite_groups.add_sprite(explosion, ["all", "effects"])
        
        # Add screen shake for larger explosions
        if size > 40:
            self.screen_shake.start(5, 10)
        elif size > 20:
            self.screen_shake.start(3, 6)
    
    def create_engine_trail(self, x: float, y: float, color: Tuple[int, int, int] = BLUE):
        trail = EngineTrail(x, y, color)
        sprite_groups.add_sprite(trail, ["all", "effects"])
    
    def create_muzzle_flash(self, x: float, y: float, angle: float = 0):
        flash = MuzzleFlash(x, y, angle)
        sprite_groups.add_sprite(flash, ["all", "effects"])
    
    def create_powerup_glow(self, x: float, y: float, color: Tuple[int, int, int], size: int = 30):
        glow = PowerUpGlow(x, y, color, size)
        sprite_groups.add_sprite(glow, ["all", "effects"])
        return glow
    
    def create_laser_beam(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], 
                         color: Tuple[int, int, int] = RED, width: int = 5):
        beam = LaserBeam(start_pos, end_pos, color, width)
        sprite_groups.add_sprite(beam, ["all", "effects"])
    
    def create_bullet_trail(self, x: float, y: float, velocity: Tuple[float, float], 
                           color: Tuple[int, int, int] = YELLOW):
        trail = BulletTrail(x, y, velocity, color)
        sprite_groups.add_sprite(trail, ["all", "effects"])
    
    def create_hit_effect(self, x: float, y: float, color: Tuple[int, int, int] = WHITE):
        hit = HitEffect(x, y, color)
        sprite_groups.add_sprite(hit, ["all", "effects"])
    
    def create_particle_burst(self, x: float, y: float, color: Tuple[int, int, int], 
                            count: int = 10, speed_range: Tuple[float, float] = (1, 5)):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(1, 3)
            lifetime = random.randint(15, 30)
            
            particle = Particle(x, y, velocity, color, size, lifetime)
            sprite_groups.add_sprite(particle, ["all", "particles"])
    
    def update(self):
        return self.screen_shake.update()
    
    def is_screen_shaking(self) -> bool:
        return self.screen_shake.is_active()

class PowerUpEffect(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, powerup_type: str):
        super().__init__()
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.lifetime = 60
        self.max_lifetime = 60
        self.size = 30
        
        # Set color based on powerup type
        color_map = {
            "shield": BLUE,
            "gun_upgrade": GREEN,
            "ultrakill": RED,
            "health": (0, 255, 0),
            "life": YELLOW,
            "speed": CYAN,
            "rapid_fire": ORANGE
        }
        self.color = color_map.get(powerup_type, WHITE)
        
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            progress = 1.0 - (self.lifetime / self.max_lifetime)
            current_size = int(self.size * (0.5 + progress * 0.5))
            
            center = (self.size, self.size)
            color_with_alpha = (*self.color, alpha)
            
            # Draw expanding circle
            pygame.draw.circle(self.image, color_with_alpha, center, current_size)
            
            # Draw inner glow
            inner_size = max(1, int(current_size * 0.6))
            inner_color = (*WHITE, alpha // 2)
            pygame.draw.circle(self.image, inner_color, center, inner_size)
    
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.update_image()

# Global effect manager instance
effect_manager = EffectManager()