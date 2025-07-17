import pygame
import random
import math
from config import *
from projectiles import EnemyBullet
from effects import Explosion, HitEffect

class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type=EnemyType.BASIC, level=1, x=None, y=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.level = level
        
        # Load appropriate image based on enemy type
        if enemy_type == EnemyType.BASIC:
            self.image = pygame.image.load(ASSET_PATHS["enemy"]).convert_alpha()
            self.image = pygame.transform.scale(self.image, (30, 30))
            self.health = ENEMY_HEALTH_BASE + level // 2
            self.speed = ENEMY_SPEED_BASE * (1 + level * 0.1)
            self.score_value = SCORE_VALUES["enemy_basic"]
            self.shoot_delay = random.randrange(3000, 6000)
            
        elif enemy_type == EnemyType.FAST:
            self.image = pygame.image.load(ASSET_PATHS["enemy2"]).convert_alpha()
            self.image = pygame.transform.scale(self.image, (25, 25))
            self.health = max(1, ENEMY_HEALTH_BASE // 2 + level // 3)
            self.speed = ENEMY_SPEED_BASE * 1.8 * (1 + level * 0.1)
            self.score_value = SCORE_VALUES["enemy_fast"]
            self.shoot_delay = random.randrange(2000, 4000)
            
        elif enemy_type == EnemyType.HEAVY:
            self.image = pygame.image.load(ASSET_PATHS["enemy"]).convert_alpha()
            self.image = pygame.transform.scale(self.image, (45, 45))
            self.health = ENEMY_HEALTH_BASE * 3 + level
            self.speed = ENEMY_SPEED_BASE * 0.6 * (1 + level * 0.05)
            self.score_value = SCORE_VALUES["enemy_heavy"]
            self.shoot_delay = random.randrange(4000, 7000)
            
        elif enemy_type == EnemyType.SHOOTER:
            self.image = pygame.image.load(ASSET_PATHS["enemy2"]).convert_alpha()
            self.image = pygame.transform.scale(self.image, (35, 35))
            self.health = ENEMY_HEALTH_BASE + level // 2
            self.speed = ENEMY_SPEED_BASE * 1.2 * (1 + level * 0.1)
            self.score_value = SCORE_VALUES["enemy_shooter"]
            self.shoot_delay = random.randrange(1500, 3000)
            
        elif enemy_type == EnemyType.KAMIKAZE:
            self.image = pygame.image.load(ASSET_PATHS["enemy"]).convert_alpha()
            self.image = pygame.transform.scale(self.image, (28, 28))
            self.health = 1
            self.speed = ENEMY_SPEED_BASE * 2.5 * (1 + level * 0.15)
            self.score_value = SCORE_VALUES["enemy_kamikaze"]
            self.shoot_delay = float('inf')  # Kamikaze enemies don't shoot
            
        self.rect = self.image.get_rect()
        
        # Position
        if x is None:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        else:
            self.rect.x = x
            
        if y is None:
            self.rect.y = random.randrange(-150, -40)
        else:
            self.rect.y = y
            
        # Movement
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = self.speed
        self.direction_change_timer = 0
        
        # AI and behavior
        self.target = None
        self.last_shot = pygame.time.get_ticks()
        self.ai_timer = 0
        self.ai_state = "descending"
        
        # Visual effects
        self.hit_flash = False
        self.hit_flash_timer = 0
        
        # Kamikaze specific
        self.homing_activated = False
        self.homing_threshold = SCREEN_HEIGHT // 2
        
    def update(self):
        self.update_ai()
        self.update_movement()
        self.update_shooting()
        self.update_visual_effects()
        self.check_bounds()
        
    def update_ai(self):
        if not self.target:
            return
            
        now = pygame.time.get_ticks()
        
        if self.enemy_type == EnemyType.BASIC:
            # Simple tracking behavior
            if now - self.direction_change_timer > 2000:
                if self.rect.centerx < self.target.rect.centerx:
                    self.speed_x = abs(self.speed_x)
                else:
                    self.speed_x = -abs(self.speed_x)
                self.direction_change_timer = now
                
        elif self.enemy_type == EnemyType.FAST:
            # Erratic movement
            if now - self.direction_change_timer > 1000:
                self.speed_x = random.uniform(-2, 2)
                self.direction_change_timer = now
                
        elif self.enemy_type == EnemyType.HEAVY:
            # Slow, steady movement toward player
            if self.rect.centerx < self.target.rect.centerx:
                self.speed_x = min(self.speed_x + 0.1, 1)
            else:
                self.speed_x = max(self.speed_x - 0.1, -1)
                
        elif self.enemy_type == EnemyType.SHOOTER:
            # Maintain distance and position for shooting
            distance_to_player = math.hypot(
                self.rect.centerx - self.target.rect.centerx,
                self.rect.centery - self.target.rect.centery
            )
            
            if distance_to_player < 200:
                # Move away from player
                if self.rect.centerx < self.target.rect.centerx:
                    self.speed_x = -1
                else:
                    self.speed_x = 1
            else:
                # Move toward player
                if self.rect.centerx < self.target.rect.centerx:
                    self.speed_x = 0.5
                else:
                    self.speed_x = -0.5
                    
        elif self.enemy_type == EnemyType.KAMIKAZE:
            # Activate homing when close to player
            if self.rect.centery > self.homing_threshold and not self.homing_activated:
                self.homing_activated = True
                self.speed_y *= 1.5
                
            if self.homing_activated:
                # Direct movement toward player
                dx = self.target.rect.centerx - self.rect.centerx
                dy = self.target.rect.centery - self.rect.centery
                distance = math.hypot(dx, dy)
                
                if distance > 0:
                    self.speed_x = (dx / distance) * self.speed
                    self.speed_y = (dy / distance) * self.speed
                    
    def update_movement(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Bounce off screen edges
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1
            
    def update_shooting(self):
        if self.enemy_type == EnemyType.KAMIKAZE:
            return
            
        now = pygame.time.get_ticks()
        if self.target and now - self.last_shot > self.shoot_delay:
            bullets = self.shoot()
            self.last_shot = now
            self.shoot_delay = random.randrange(
                int(self.shoot_delay * 0.8),
                int(self.shoot_delay * 1.2)
            )
            return bullets
        return []
        
    def shoot(self):
        if not self.target:
            return []
            
        bullets = []
        
        if self.enemy_type == EnemyType.BASIC:
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.bottom,
                (self.target.rect.centerx, self.target.rect.centery),
                speed=3
            )
            bullets.append(bullet)
            
        elif self.enemy_type == EnemyType.FAST:
            # Shoots a single fast bullet
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.bottom,
                (self.target.rect.centerx, self.target.rect.centery),
                speed=5
            )
            bullets.append(bullet)
            
        elif self.enemy_type == EnemyType.HEAVY:
            # Shoots 3 bullets in a spread
            for i in range(-1, 2):
                bullet = EnemyBullet(
                    self.rect.centerx, self.rect.bottom,
                    (self.target.rect.centerx + i * 60, self.target.rect.centery),
                    speed=2
                )
                bullets.append(bullet)
                
        elif self.enemy_type == EnemyType.SHOOTER:
            # Shoots 5 bullets in a fan pattern
            for i in range(-2, 3):
                angle_offset = i * 15  # 15 degrees between bullets
                target_x = self.target.rect.centerx + math.sin(math.radians(angle_offset)) * 100
                target_y = self.target.rect.centery + math.cos(math.radians(angle_offset)) * 100
                
                bullet = EnemyBullet(
                    self.rect.centerx, self.rect.bottom,
                    (target_x, target_y),
                    speed=4
                )
                bullets.append(bullet)
                
        return bullets
        
    def update_visual_effects(self):
        now = pygame.time.get_ticks()
        if self.hit_flash and now - self.hit_flash_timer > 100:
            self.hit_flash = False
            
    def check_bounds(self):
        if self.rect.top > SCREEN_HEIGHT:
            if self.enemy_type != EnemyType.KAMIKAZE:
                # Reset position for non-kamikaze enemies
                self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
                self.rect.y = random.randrange(-150, -40)
                self.speed_y = self.speed
                self.homing_activated = False
            else:
                # Kamikaze enemies are destroyed when they leave screen
                self.kill()
                
    def damage(self, amount):
        self.health -= amount
        self.hit_flash = True
        self.hit_flash_timer = pygame.time.get_ticks()
        
        if self.health <= 0:
            # Play explosion sound
            try:
                explosion_sound = pygame.mixer.Sound(ASSET_PATHS["explosion"])
                explosion_sound.set_volume(SFX_VOLUME)
                explosion_sound.play()
            except:
                pass
            return True
        return False
        
    def draw(self, screen):
        if self.hit_flash:
            # Create hit flash effect
            flash_surface = self.image.copy()
            flash_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash_surface, self.rect)
        else:
            screen.blit(self.image, self.rect)
            
        # Draw health bar for heavy enemies
        if self.enemy_type == EnemyType.HEAVY and self.health > 0:
            bar_width = 30
            bar_height = 4
            bar_x = self.rect.centerx - bar_width // 2
            bar_y = self.rect.top - 8
            
            # Background
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            
            # Health fill
            health_percent = self.health / (ENEMY_HEALTH_BASE * 3 + self.level)
            fill_width = int(bar_width * health_percent)
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_width, bar_height))


class Boss(pygame.sprite.Sprite):
    def __init__(self, level=1, boss_type=1):
        super().__init__()
        self.level = level
        self.boss_type = boss_type
        
        # Load boss image
        self.image = pygame.image.load(ASSET_PATHS["boss"]).convert_alpha()
        if boss_type == 1:
            self.image = pygame.transform.scale(self.image, (100, 80))
        else:
            self.image = pygame.transform.scale(self.image, (120, 100))
            
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = -self.rect.height
        
        # Health and stats
        self.health = BOSS_HEALTH_BASE * level
        self.max_health = self.health
        self.speed = 2
        self.active = False
        
        # Movement
        self.speed_x = 2
        self.speed_y = 1
        
        # AI and patterns
        self.target = None
        self.pattern = 0
        self.pattern_timer = 0
        self.pattern_duration = BOSS_PATTERN_CHANGE_TIME
        self.last_shot = 0
        self.shoot_delay = 1000
        
        # Phase system
        self.phase = 1
        self.phase_transition = False
        
        # Visual effects
        self.hit_flash = False
        self.hit_flash_timer = 0
        
        # Minion spawning
        self.last_minion_spawn = 0
        self.minion_spawn_delay = 8000
        
    def update(self):
        if not self.active:
            return
            
        self.update_entry()
        self.update_patterns()
        self.update_shooting()
        self.update_phase()
        self.update_visual_effects()
        self.spawn_minions()
        
    def update_entry(self):
        if self.rect.y < 50:
            self.rect.y += self.speed_y
            return
            
    def update_patterns(self):
        if self.rect.y >= 50:
            now = pygame.time.get_ticks()
            
            if now - self.pattern_timer > self.pattern_duration:
                self.pattern = (self.pattern + 1) % 4
                self.pattern_timer = now
                
            if self.pattern == 0:
                # Side to side movement
                self.rect.x += self.speed_x
                if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                    self.speed_x *= -1
                    
            elif self.pattern == 1:
                # Track player horizontally
                if self.target:
                    if self.rect.centerx < self.target.rect.centerx:
                        self.rect.x += 2
                    elif self.rect.centerx > self.target.rect.centerx:
                        self.rect.x -= 2
                        
            elif self.pattern == 2:
                # Circular movement
                angle = now / 1000
                center_x = SCREEN_WIDTH // 2
                center_y = 100
                radius = 150
                self.rect.centerx = center_x + math.cos(angle) * radius
                self.rect.centery = center_y + math.sin(angle) * (radius // 3)
                
            elif self.pattern == 3:
                # Aggressive approach
                if self.target:
                    if self.rect.centery < SCREEN_HEIGHT // 3:
                        self.rect.y += 1
                    dx = self.target.rect.centerx - self.rect.centerx
                    self.rect.x += dx * 0.02
                    
    def update_shooting(self):
        now = pygame.time.get_ticks()
        if self.target and now - self.last_shot > self.shoot_delay:
            bullets = self.shoot()
            self.last_shot = now
            return bullets
        return []
        
    def shoot(self):
        if not self.target:
            return []
            
        bullets = []
        
        if self.pattern == 0:
            # Spray downward
            for i in range(-2, 3):
                bullet = EnemyBullet(
                    self.rect.centerx + i * 25, self.rect.bottom,
                    (self.rect.centerx + i * 25, SCREEN_HEIGHT),
                    speed=3
                )
                bullets.append(bullet)
                
        elif self.pattern == 1:
            # Aimed shots
            for i in range(-1, 2):
                bullet = EnemyBullet(
                    self.rect.centerx + i * 30, self.rect.bottom,
                    (self.target.rect.centerx + i * 50, self.target.rect.centery),
                    speed=4
                )
                bullets.append(bullet)
                
        elif self.pattern == 2:
            # Circular spray
            for angle in range(0, 360, 30):
                dx = math.cos(math.radians(angle)) * 300
                dy = math.sin(math.radians(angle)) * 300
                bullet = EnemyBullet(
                    self.rect.centerx, self.rect.centery,
                    (self.rect.centerx + dx, self.rect.centery + dy),
                    speed=3
                )
                bullets.append(bullet)
                
        elif self.pattern == 3:
            # Rapid aimed shots
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.bottom,
                (self.target.rect.centerx, self.target.rect.centery),
                speed=6
            )
            bullets.append(bullet)
            
        # Phase 2 additional attacks
        if self.phase >= 2:
            # Add spiral pattern
            for i in range(8):
                angle = (pygame.time.get_ticks() / 100 + i * 45) % 360
                dx = math.cos(math.radians(angle)) * 200
                dy = math.sin(math.radians(angle)) * 200
                bullet = EnemyBullet(
                    self.rect.centerx, self.rect.centery,
                    (self.rect.centerx + dx, self.rect.centery + dy),
                    speed=2
                )
                bullets.append(bullet)
                
        return bullets
        
    def update_phase(self):
        health_percent = self.health / self.max_health
        
        if health_percent <= 0.5 and self.phase == 1:
            self.phase = 2
            self.phase_transition = True
            self.shoot_delay = max(500, self.shoot_delay - 200)
            self.pattern_duration = max(2000, self.pattern_duration - 1000)
            
        if health_percent <= 0.25 and self.phase == 2:
            self.phase = 3
            self.phase_transition = True
            self.shoot_delay = max(300, self.shoot_delay - 200)
            self.speed_x *= 1.5
            
    def spawn_minions(self):
        if self.phase < 2:
            return
            
        now = pygame.time.get_ticks()
        if now - self.last_minion_spawn > self.minion_spawn_delay:
            minions = []
            
            # Spawn 2-3 minions
            for i in range(random.randint(2, 3)):
                enemy_type = random.choice([EnemyType.BASIC, EnemyType.FAST])
                minion = Enemy(enemy_type, self.level)
                minion.rect.x = self.rect.x + random.randint(-100, 100)
                minion.rect.y = self.rect.bottom
                minion.target = self.target
                minions.append(minion)
                
            self.last_minion_spawn = now
            return minions
        return []
        
    def update_visual_effects(self):
        now = pygame.time.get_ticks()
        if self.hit_flash and now - self.hit_flash_timer > 150:
            self.hit_flash = False
            
    def damage(self, amount):
        self.health -= amount
        self.hit_flash = True
        self.hit_flash_timer = pygame.time.get_ticks()
        
        # Play boss hit sound
        try:
            boss_hit_sound = pygame.mixer.Sound(ASSET_PATHS["explosion"])
            boss_hit_sound.set_volume(SFX_VOLUME * 0.8)
            boss_hit_sound.play()
        except:
            pass
            
        if self.health <= 0:
            # Play explosion sound
            try:
                explosion_sound = pygame.mixer.Sound(ASSET_PATHS["explosion"])
                explosion_sound.set_volume(SFX_VOLUME)
                explosion_sound.play()
            except:
                pass
            return True
        return False
        
    def draw(self, screen):
        if self.hit_flash:
            # Create hit flash effect
            flash_surface = self.image.copy()
            flash_surface.fill((255, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash_surface, self.rect)
        else:
            screen.blit(self.image, self.rect)
            
        # Draw health bar
        if self.active:
            bar_width = 200
            bar_height = 10
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = 20
            
            # Background
            pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
            
            # Health fill
            health_percent = max(0, self.health / self.max_health)
            fill_width = int(bar_width * health_percent)
            
            # Color based on health
            if health_percent > 0.6:
                color = GREEN
            elif health_percent > 0.3:
                color = YELLOW
            else:
                color = RED
                
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Phase indicator
            font = pygame.font.Font(None, 24)
            phase_text = font.render(f"BOSS - Phase {self.phase}", True, WHITE)
            screen.blit(phase_text, (bar_x, bar_y - 25))
            
    def activate(self):
        self.active = True
        self.rect.y = -self.rect.height
        
    def get_score_value(self):
        return SCORE_VALUES["boss"] * self.level