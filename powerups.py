import pygame
import random
import math
from typing import Optional
from config import *
from asset_manager import asset_manager

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, powerup_type: PowerUpType, x: Optional[float] = None, y: Optional[float] = None):
        super().__init__()
        self.type = powerup_type
        self.speed_y = 3
        self.lifetime = 10000  # 10 seconds
        self.spawn_time = pygame.time.get_ticks()
        
        # Load appropriate image
        image_name = f"powerup_{powerup_type.value}"
        self.image = asset_manager.get_image(image_name)
        if not self.image:
            self.image = asset_manager.get_image("powerup")
        if not self.image:
            self.image = asset_manager.create_placeholder_image("powerup")
            
        self.rect = self.image.get_rect()
        
        # Set position
        if x is None:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        else:
            self.rect.x = x
            
        if y is None:
            self.rect.y = random.randrange(-150, -40)
        else:
            self.rect.y = y
            
        # Visual effects
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.glow_alpha = 128
        self.glow_direction = 1
        
    def update(self):
        # Move downward
        self.rect.y += self.speed_y
        
        # Bob up and down
        self.bob_offset += self.bob_speed
        bob_y = math.sin(self.bob_offset) * 2
        self.rect.y += bob_y
        
        # Glow effect
        self.glow_alpha += self.glow_direction * 3
        if self.glow_alpha >= 255:
            self.glow_alpha = 255
            self.glow_direction = -1
        elif self.glow_alpha <= 50:
            self.glow_alpha = 50
            self.glow_direction = 1
            
        # Check lifetime
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
            
        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            
    def draw(self, screen):
        # Draw glow effect
        glow_surface = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
        glow_color = self.get_glow_color()
        pygame.draw.circle(glow_surface, (*glow_color, self.glow_alpha), 
                         (glow_surface.get_width() // 2, glow_surface.get_height() // 2), 
                         self.rect.width // 2 + 5)
        
        screen.blit(glow_surface, (self.rect.x - 5, self.rect.y - 5))
        
        # Draw the powerup
        screen.blit(self.image, self.rect)
        
    def get_glow_color(self):
        color_map = {
            PowerUpType.SHIELD: BLUE,
            PowerUpType.GUN_UPGRADE: GREEN,
            PowerUpType.ULTRAKILL: RED,
            PowerUpType.HEALTH: (0, 255, 0),
            PowerUpType.LIFE: YELLOW,
            PowerUpType.SPEED: CYAN,
            PowerUpType.RAPID_FIRE: ORANGE
        }
        return color_map.get(self.type, WHITE)
        
    def get_description(self) -> str:
        descriptions = {
            PowerUpType.SHIELD: "Temporary invincibility shield",
            PowerUpType.GUN_UPGRADE: "Upgrade your weapon",
            PowerUpType.ULTRAKILL: "Destroy all enemies on screen",
            PowerUpType.HEALTH: "Restore health",
            PowerUpType.LIFE: "Gain an extra life",
            PowerUpType.SPEED: "Increase movement speed",
            PowerUpType.RAPID_FIRE: "Increase fire rate"
        }
        return descriptions.get(self.type, "Unknown power-up")
        
    def get_duration(self) -> int:
        durations = {
            PowerUpType.SHIELD: SHIELD_DURATION,
            PowerUpType.GUN_UPGRADE: GUN_UPGRADE_DURATION,
            PowerUpType.SPEED: 10000,
            PowerUpType.RAPID_FIRE: 8000
        }
        return durations.get(self.type, 0)

# Legacy functions for backward compatibility
def apply_powerup(player, powerup, all_sprites, bullets):
    if powerup.type == PowerUpType.HEALTH:
        player.health = min(player.health + 50, 100)
    elif powerup.type == PowerUpType.GUN_UPGRADE:
        player.upgrade_weapon(duration=GUN_UPGRADE_DURATION)
    elif powerup.type == PowerUpType.SHIELD:
        player.activate_shield(SHIELD_DURATION)
    elif powerup.type == PowerUpType.SPEED:
        player.speed_boost(1.5, 10000)
    elif powerup.type == PowerUpType.RAPID_FIRE:
        player.rapid_fire(8000)
    elif powerup.type == PowerUpType.LIFE:
        player.add_life()
    elif powerup.type == PowerUpType.ULTRAKILL:
        # Kill all enemies
        from sprite_groups import sprite_groups
        enemies = sprite_groups.get_group("enemies")
        for enemy in enemies:
            enemy.kill()

def increase_damage(player, damage_increase, duration, all_sprites, bullets):
    # Add damage increase to bullets
    for bullet in bullets:
        if hasattr(bullet, 'damage'):
            bullet.damage += damage_increase
    
    # Set timer for removal
    pygame.time.set_timer(pygame.USEREVENT, duration)

def activate_shield(player, duration):
    player.activate_shield(duration)

def activate_speed_boost(player):
    player.speed_boost(1.5, 5000)

def create_random_powerup(x: Optional[float] = None, y: Optional[float] = None) -> PowerUp:
    """Create a random powerup with weighted probability."""
    powerup_weights = [
        (PowerUpType.HEALTH, 0.3),
        (PowerUpType.GUN_UPGRADE, 0.25),
        (PowerUpType.SHIELD, 0.2),
        (PowerUpType.SPEED, 0.1),
        (PowerUpType.RAPID_FIRE, 0.1),
        (PowerUpType.LIFE, 0.03),
        (PowerUpType.ULTRAKILL, 0.02)
    ]
    
    from utils import weighted_choice
    powerup_type = weighted_choice(powerup_weights)
    
    return PowerUp(powerup_type, x, y)