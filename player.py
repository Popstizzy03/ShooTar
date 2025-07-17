import pygame
import math
from config import *
from projectiles import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, ship_type=ShipType.FIGHTER):
        super().__init__()
        self.ship_type = ship_type
        self.ship_stats = ship_type.value
        
        # Load and scale player image
        self.image = pygame.image.load(ASSET_PATHS["player"]).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 40))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        
        # Movement attributes
        self.speed_x = 0
        self.speed_y = 0
        self.acceleration = PLAYER_ACCELERATION
        self.max_speed = self.ship_stats["speed"]
        self.friction = PLAYER_FRICTION
        
        # Health and lives
        self.health = self.ship_stats["health"]
        self.max_health = self.ship_stats["health"]
        self.lives = PLAYER_LIVES
        
        # Protection and shield
        self.protected = False
        self.protected_timer = 0
        self.protection_duration = 1000
        self.shield = False
        self.shield_timer = 0
        
        # Weapon system
        self.weapon_type = WeaponType.BASIC
        self.weapon_timer = 0
        self.fire_rate = self.ship_stats["fire_rate"]
        self.last_shot = 0
        self.bullet_damage = 1
        
        # Power-up tracking
        self.active_powerups = {}
        self.powerup_timers = {}
        
        # Score and stats
        self.score = 0
        self.enemies_killed = 0
        self.bosses_killed = 0
        self.powerups_collected = 0
        
        # Visual effects
        self.hit_flash = False
        self.hit_flash_timer = 0
        
        # Engine trail particles
        self.engine_particles = []
        
    def update(self):
        self.handle_input()
        self.update_movement()
        self.update_powerups()
        self.update_visual_effects()
        self.update_engine_trail()
        self.constrain_to_screen()
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Movement input
        if keys[CONTROLS["move_left"]]:
            self.speed_x -= self.acceleration
        if keys[CONTROLS["move_right"]]:
            self.speed_x += self.acceleration
        if keys[CONTROLS["move_up"]]:
            self.speed_y -= self.acceleration
        if keys[CONTROLS["move_down"]]:
            self.speed_y += self.acceleration
            
        # Shooting input
        if keys[CONTROLS["shoot"]]:
            self.try_shoot()
            
    def update_movement(self):
        # Apply friction when not moving
        if not pygame.key.get_pressed()[CONTROLS["move_left"]] and not pygame.key.get_pressed()[CONTROLS["move_right"]]:
            self.speed_x *= (1 - self.friction)
        if not pygame.key.get_pressed()[CONTROLS["move_up"]] and not pygame.key.get_pressed()[CONTROLS["move_down"]]:
            self.speed_y *= (1 - self.friction)
            
        # Limit speed
        self.speed_x = max(-self.max_speed, min(self.max_speed, self.speed_x))
        self.speed_y = max(-self.max_speed, min(self.max_speed, self.speed_y))
        
        # Update position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
    def constrain_to_screen(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed_x = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.speed_x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed_y = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.speed_y = 0
            
    def try_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            self.shoot()
            self.last_shot = now
            
    def shoot(self):
        bullets = []
        
        if self.weapon_type == WeaponType.BASIC:
            bullet = Bullet(self.rect.centerx, self.rect.top, damage=self.bullet_damage)
            bullets.append(bullet)
            
        elif self.weapon_type == WeaponType.DOUBLE:
            bullet1 = Bullet(self.rect.left + 10, self.rect.top, damage=self.bullet_damage)
            bullet2 = Bullet(self.rect.right - 10, self.rect.top, damage=self.bullet_damage)
            bullets.extend([bullet1, bullet2])
            
        elif self.weapon_type == WeaponType.TRIPLE:
            bullet1 = Bullet(self.rect.centerx, self.rect.top, damage=self.bullet_damage)
            bullet2 = Bullet(self.rect.centerx - 15, self.rect.top + 5, damage=self.bullet_damage)
            bullet2.speed_x = -1
            bullet3 = Bullet(self.rect.centerx + 15, self.rect.top + 5, damage=self.bullet_damage)
            bullet3.speed_x = 1
            bullets.extend([bullet1, bullet2, bullet3])
            
        elif self.weapon_type == WeaponType.SPREAD:
            for i in range(-2, 3):
                bullet = Bullet(self.rect.centerx + i * 10, self.rect.top, damage=self.bullet_damage)
                bullet.speed_x = i * 0.5
                bullets.append(bullet)
                
        # Play shoot sound
        try:
            shoot_sound = pygame.mixer.Sound(ASSET_PATHS["shoot"])
            shoot_sound.set_volume(SFX_VOLUME)
            shoot_sound.play()
        except:
            pass
            
        return bullets
        
    def damage(self, amount):
        if self.shield or self.protected:
            return False
            
        self.health -= amount
        self.protected = True
        self.protected_timer = pygame.time.get_ticks()
        self.hit_flash = True
        self.hit_flash_timer = pygame.time.get_ticks()
        
        # Play hit sound
        try:
            hit_sound = pygame.mixer.Sound(ASSET_PATHS["explosion"])
            hit_sound.set_volume(SFX_VOLUME * 0.5)
            hit_sound.play()
        except:
            pass
            
        if self.health <= 0:
            self.lives -= 1
            self.health = self.max_health
            if self.lives <= 0:
                return True
                
        return False
        
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        
    def add_life(self):
        self.lives += 1
        
    def upgrade_weapon(self, weapon_type, duration=None):
        self.weapon_type = weapon_type
        if duration:
            self.weapon_timer = pygame.time.get_ticks()
            self.powerup_timers["weapon"] = duration
            
    def activate_shield(self, duration):
        self.shield = True
        self.shield_timer = pygame.time.get_ticks()
        self.powerup_timers["shield"] = duration
        
    def speed_boost(self, multiplier, duration):
        self.max_speed *= multiplier
        self.powerup_timers["speed"] = duration
        self.active_powerups["speed"] = {"multiplier": multiplier, "start_time": pygame.time.get_ticks()}
        
    def rapid_fire(self, duration):
        self.fire_rate = max(self.fire_rate // 2, 100)
        self.powerup_timers["rapid_fire"] = duration
        self.active_powerups["rapid_fire"] = {"original_rate": self.fire_rate * 2, "start_time": pygame.time.get_ticks()}
        
    def update_powerups(self):
        now = pygame.time.get_ticks()
        
        # Update protection
        if self.protected and now - self.protected_timer > self.protection_duration:
            self.protected = False
            
        # Update shield
        if self.shield and "shield" in self.powerup_timers:
            if now - self.shield_timer > self.powerup_timers["shield"]:
                self.shield = False
                del self.powerup_timers["shield"]
                
        # Update weapon upgrade
        if self.weapon_type != WeaponType.BASIC and "weapon" in self.powerup_timers:
            if now - self.weapon_timer > self.powerup_timers["weapon"]:
                self.weapon_type = WeaponType.BASIC
                del self.powerup_timers["weapon"]
                
        # Update speed boost
        if "speed" in self.powerup_timers and "speed" in self.active_powerups:
            if now - self.active_powerups["speed"]["start_time"] > self.powerup_timers["speed"]:
                self.max_speed /= self.active_powerups["speed"]["multiplier"]
                del self.powerup_timers["speed"]
                del self.active_powerups["speed"]
                
        # Update rapid fire
        if "rapid_fire" in self.powerup_timers and "rapid_fire" in self.active_powerups:
            if now - self.active_powerups["rapid_fire"]["start_time"] > self.powerup_timers["rapid_fire"]:
                self.fire_rate = self.active_powerups["rapid_fire"]["original_rate"]
                del self.powerup_timers["rapid_fire"]
                del self.active_powerups["rapid_fire"]
                
    def update_visual_effects(self):
        now = pygame.time.get_ticks()
        
        # Update hit flash
        if self.hit_flash and now - self.hit_flash_timer > 100:
            self.hit_flash = False
            
    def update_engine_trail(self):
        # Add new engine particles
        if len(self.engine_particles) < PARTICLE_SETTINGS["engine_trail"]["count"]:
            particle = {
                "x": self.rect.centerx + ((-5 + pygame.time.get_ticks() % 10) if self.speed_x == 0 else 0),
                "y": self.rect.bottom,
                "speed_x": self.speed_x * -0.1,
                "speed_y": PARTICLE_SETTINGS["engine_trail"]["speed"],
                "lifetime": PARTICLE_SETTINGS["engine_trail"]["lifetime"],
                "age": 0,
                "color": PARTICLE_SETTINGS["engine_trail"]["colors"][0]
            }
            self.engine_particles.append(particle)
            
        # Update existing particles
        for particle in self.engine_particles[:]:
            particle["x"] += particle["speed_x"]
            particle["y"] += particle["speed_y"]
            particle["age"] += 1
            
            if particle["age"] >= particle["lifetime"]:
                self.engine_particles.remove(particle)
                
    def draw_shield(self, screen):
        if self.shield:
            shield_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (*BLUE[:3], 100), (40, 40), 40)
            screen.blit(shield_surface, (self.rect.centerx - 40, self.rect.centery - 40))
            
    def draw_engine_trail(self, screen):
        for particle in self.engine_particles:
            alpha = int(255 * (1 - particle["age"] / particle["lifetime"]))
            color = (*particle["color"][:3], alpha)
            size = max(1, int(3 * (1 - particle["age"] / particle["lifetime"])))
            
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            screen.blit(particle_surface, (particle["x"] - size, particle["y"] - size))
            
    def draw(self, screen):
        # Draw engine trail
        self.draw_engine_trail(screen)
        
        # Draw shield
        self.draw_shield(screen)
        
        # Draw player with hit flash effect
        if self.hit_flash:
            # Create a white flash effect
            flash_surface = self.image.copy()
            flash_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash_surface, self.rect)
        else:
            screen.blit(self.image, self.rect)
            
    def get_stats(self):
        return {
            "health": self.health,
            "max_health": self.max_health,
            "lives": self.lives,
            "score": self.score,
            "enemies_killed": self.enemies_killed,
            "bosses_killed": self.bosses_killed,
            "powerups_collected": self.powerups_collected,
            "weapon_type": self.weapon_type.name,
            "shield_active": self.shield,
            "active_powerups": list(self.active_powerups.keys())
        }
        
    def reset(self):
        self.health = self.max_health
        self.lives = PLAYER_LIVES
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed_x = 0
        self.speed_y = 0
        self.protected = False
        self.shield = False
        self.weapon_type = WeaponType.BASIC
        self.active_powerups.clear()
        self.powerup_timers.clear()
        self.engine_particles.clear()
        self.hit_flash = False