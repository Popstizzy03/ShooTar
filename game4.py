import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultimate Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Load Assets
player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 40))

bullet_img = pygame.image.load("bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (5, 10))

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (30, 30))

enemy2_img = pygame.image.load("enemy2.png").convert_alpha()  # New enemy type
enemy2_img = pygame.transform.scale(enemy2_img, (35, 35))

boss_img = pygame.image.load("boss.png").convert_alpha()
boss_img = pygame.transform.scale(boss_img, (100, 80))

boss2_img = pygame.image.load("boss.png").convert_alpha()  # Assuming second boss image
boss2_img = pygame.transform.scale(boss2_img, (120, 100))

powerup_img = pygame.image.load("powerup.png").convert_alpha()
powerup_img = pygame.transform.scale(powerup_img, (20, 20))

shield_img = pygame.Surface((60, 60), pygame.SRCALPHA)
pygame.draw.circle(shield_img, (0, 100, 255, 100), (30, 30), 30)

enemy_bullet_img = pygame.Surface((5, 10), pygame.SRCALPHA)
pygame.draw.rect(enemy_bullet_img, RED, (0, 0, 5, 10))

background_img = pygame.image.load("background.png").convert()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Second level background
background2_img = pygame.image.load("background.png").convert()  # Assuming same image but we'll tint it
background2_img = pygame.transform.scale(background2_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
# Tint the second background (apply a light blue overlay)
blue_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
blue_overlay.fill((0, 0, 100))
background2_img.blit(blue_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

# Load sounds
shoot_sound = pygame.mixer.Sound("shoot.mp3")
explosion_sound = pygame.mixer.Sound("explosion.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")
ultrakill_sound = pygame.mixer.Sound("ultrakill.wav")
boss_hit_sound = pygame.mixer.Sound("explosion.wav")  # Reusing explosion sound
player_hit_sound = pygame.mixer.Sound("explosion.wav")  # Reusing explosion sound
pygame.mixer.music.load("background.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed_x = 0
        self.health = 100
        self.lives = 3
        self.protected = False
        self.protected_timer = 0
        self.acceleration = 0.5
        self.max_speed = 8
        self.friction = 0.1
        self.shield = False
        self.shield_timer = 0
        self.gun_level = 1  # Track gun upgrades
        self.gun_timer = 0  # Timer for temporary gun upgrades
        self.fire_rate = 500  # Milliseconds between shots
        self.last_shot = 0

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Movement with acceleration and friction
        if keys[pygame.K_LEFT]:
            self.speed_x -= self.acceleration
        elif keys[pygame.K_RIGHT]:
            self.speed_x += self.acceleration
        else:
            # Apply friction when not pressing movement keys
            if self.speed_x > 0:
                self.speed_x -= self.friction
                if self.speed_x < 0:
                    self.speed_x = 0
            elif self.speed_x < 0:
                self.speed_x += self.friction
                if self.speed_x > 0:
                    self.speed_x = 0

        # Limit maximum speed
        if self.speed_x > self.max_speed:
            self.speed_x = self.max_speed
        elif self.speed_x < -self.max_speed:
            self.speed_x = -self.max_speed

        self.rect.x += self.speed_x

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Auto-fire if space is held down
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.fire_rate:
                self.shoot()
                self.last_shot = now

        # Protected status timeout
        if self.protected and pygame.time.get_ticks() - self.protected_timer > 1000:
            self.protected = False

        # Shield timeout
        if self.shield and pygame.time.get_ticks() - self.shield_timer > 5000:
            self.shield = False  # Shield lasts 5 seconds

        # Gun upgrade timeout if temporary
        if self.gun_level > 1 and pygame.time.get_ticks() - self.gun_timer > 10000:
            self.gun_level = 1  # Gun upgrades last 10 seconds

    def shoot(self):
        if self.gun_level == 1:
            # Basic single shot
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
        elif self.gun_level == 2:
            # Double shot
            bullet1 = Bullet(self.rect.left + 10, self.rect.top)
            bullet2 = Bullet(self.rect.right - 10, self.rect.top)
            all_sprites.add(bullet1, bullet2)
            bullets.add(bullet1, bullet2)
            shoot_sound.play()
        elif self.gun_level == 3:
            # Triple shot with spread
            bullet1 = Bullet(self.rect.centerx, self.rect.top)
            bullet2 = Bullet(self.rect.centerx - 15, self.rect.top + 5)
            bullet2.speed_y = -9
            bullet2.speed_x = -1
            bullet3 = Bullet(self.rect.centerx + 15, self.rect.top + 5)
            bullet3.speed_y = -9
            bullet3.speed_x = 1
            all_sprites.add(bullet1, bullet2, bullet3)
            bullets.add(bullet1, bullet2, bullet3)
            shoot_sound.play()
        elif self.gun_level >= 4:
            # Mega shot - 5 bullets in spread formation
            self.mega_shoot()

    def mega_shoot(self):
        # Fires multiple bullets in spread formation
        for i in range(-2, 3):
            bullet = Bullet(self.rect.centerx + i * 10, self.rect.top)
            bullet.speed_x = i * 0.5  # Add some spread
            all_sprites.add(bullet)
            bullets.add(bullet)
        shoot_sound.play()

    def damage(self, amount):
        if self.shield:
            return False  # No damage if shield is active

        if not self.protected:
            player_hit_sound.play()
            self.health -= amount
            self.protected = True
            self.protected_timer = pygame.time.get_ticks()
            if self.health <= 0:
                self.lives -= 1
                self.health = 100
                if self.lives <= 0:
                    return True

        return False

    def upgrade_gun(self, permanent=False):
        self.gun_level = min(self.gun_level + 1, 5)  # Max level 5
        self.gun_timer = pygame.time.get_ticks()
        # If permanent is True, we don't need to worry about downgrade timer
        
        # Improve fire rate with upgrades
        self.fire_rate = max(500 - (self.gun_level * 50), 200)  # Faster firing with better guns

# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10
        self.speed_x = 0  # For diagonal shots

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# Enemy Bullet Class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, speed=5):
        super().__init__()
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        
        # Calculate direction vector towards player
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:  # Avoid division by zero
            self.speed_x = 0
            self.speed_y = speed
        else:
            self.speed_x = dx/dist * speed
            self.speed_y = dy/dist * speed

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if (self.rect.bottom > SCREEN_HEIGHT or self.rect.top < 0 or 
            self.rect.left > SCREEN_WIDTH or self.rect.right < 0):
            self.kill()

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -40)
        self.speed_y = random.randrange(1, 3) * (1 + level * 0.1)  # Faster in higher levels
        self.speed_x = random.randrange(-2, 2)
        self.health = 2 + level // 2  # More health in higher levels
        self.target = None  # Will be set to player
        self.shoot_delay = random.randrange(2000, 5000)  # Time between shots
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        if self.target:
            # Simple AI to move toward player
            if self.rect.centerx < self.target.rect.centerx:
                self.speed_x = 1
            elif self.rect.centerx > self.target.rect.centerx:
                self.speed_x = -1
            else:
                self.speed_x = 0

        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1

        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -40)
            self.speed_y = random.randrange(1, 3)

        # Random shooting
        now = pygame.time.get_ticks()
        if self.target and now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now
            self.shoot_delay = random.randrange(2000, 5000)
            
        if self.health <= 0:
            self.kill()

    def shoot(self):
        if self.target:
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, 
                               self.target.rect.centerx, self.target.rect.centery, 3)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            explosion_sound.play()
            return True
        return False

# New Enemy Type
class Enemy2(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.image = enemy2_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -40)
        self.speed_y = random.randrange(2, 4) * (1 + level * 0.1)  # Slightly faster
        self.speed_x = 0  # Moves straight down
        self.health = 1 + level // 3  # Less health
        self.target = None  # Will be set to player
        self.shoot_delay = random.randrange(1500, 3000)  # Shoots more frequently
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed_y

        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -40)
            self.speed_y = random.randrange(2, 4)
            
        # Random shooting
        now = pygame.time.get_ticks()
        if self.target and now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now
            self.shoot_delay = random.randrange(1500, 3000)

        if self.health <= 0:
            self.kill()

    def shoot(self):
        if self.target:
            # This enemy shoots 3 bullets in a spread
            for i in range(-1, 2):
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, 
                                  self.target.rect.centerx + i*50, self.target.rect.centery, 2)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            explosion_sound.play()
            return True
        return False

# Boss Class
class Boss(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        if level == 1:
            self.image = boss_img
        else:
            self.image = boss2_img  # Different image for level 2 boss
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = -100  # Start offscreen
        self.speed_y = 1  # Move down slowly
        self.speed_x = 2
        self.health = 50 * level  # Much higher health, scales with level
        self.active = False  # Boss only appears at a certain level
        self.target = None  # Will be set to player
        self.shoot_delay = 1000  # Time between shots
        self.last_shot = pygame.time.get_ticks()
        self.pattern = 0  # Attack pattern
        self.pattern_timer = 0
        self.level = level
        self.max_health = 50 * level  # Store max health for UI

    def update(self):
        if not self.active:
            return  # Don't update if not active

        now = pygame.time.get_ticks()
        
        # Move to position if just activated
        if self.rect.y < 50:
            self.rect.y += self.speed_y
        else:
            # Change attack pattern every 5 seconds
            if now - self.pattern_timer > 5000:
                self.pattern = (self.pattern + 1) % 3
                self.pattern_timer = now
            
            # Different movement patterns
            if self.pattern == 0:
                # Move side to side
                self.rect.x += self.speed_x
                if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                    self.speed_x *= -1
            elif self.pattern == 1:
                # Track player
                if self.target and self.rect.centerx < self.target.rect.centerx:
                    self.rect.x += 1
                elif self.target:
                    self.rect.x -= 1
            elif self.pattern == 2:
                # Move in a figure-8 pattern
                self.rect.x = SCREEN_WIDTH//2 + math.sin(now/1000) * (SCREEN_WIDTH//3)
                self.rect.y = 100 + math.sin(now/500) * 50
        
        # Shooting
        if now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now

        if self.health <= 0:
            self.kill()

    def shoot(self):
        if not self.target:
            return
            
        if self.pattern == 0:
            # Shoot 3 bullets downward
            for i in range(-1, 2):
                bullet = EnemyBullet(self.rect.centerx + i*30, self.rect.bottom, 
                                   self.rect.centerx + i*30, SCREEN_HEIGHT, 3)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)
        elif self.pattern == 1:
            # Aim at player
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom,
                               self.target.rect.centerx, self.target.rect.centery, 4)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
        elif self.pattern == 2:
            # Spray in all directions
            for angle in range(0, 360, 45):
                dx = math.cos(math.radians(angle)) * SCREEN_WIDTH
                dy = math.sin(math.radians(angle)) * SCREEN_HEIGHT
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                                   self.rect.centerx + dx, self.rect.centery + dy, 3)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)

        # Level 2 boss has additional attacks
        if self.level >= 2 and random.random() < 0.3:  # 30% chance for special attack
            # Spawn minions
            enemy = Enemy(self.level)
            enemy.rect.x = self.rect.x
            enemy.rect.y = self.rect.bottom
            enemy.target = self.target
            all_sprites.add(enemy)
            enemies.add(enemy)

    def damage(self, amount):
        self.health -= amount
        boss_hit_sound.play()
        if self.health <= 0:
            explosion_sound.play()
            return True
        return False

# Power-up Class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.image = powerup_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = 3
        self.type = type  # Type of power-up ("shield", "gun_upgrade", "ultrakill", "health", "life")
        
        # Color the power-up based on type
        color_overlay = pygame.Surface((20, 20), pygame.SRCALPHA)
        if self.type == "shield":
            color_overlay.fill(BLUE)
        elif self.type == "gun_upgrade":
            color_overlay.fill(GREEN)
        elif self.type == "ultrakill":
            color_overlay.fill(RED)
        elif self.type == "health":
            color_overlay.fill(GREEN)
        elif self.type == "life":
            color_overlay.fill(YELLOW)
            
        self.image.blit(color_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Explosion animation
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.alpha = 255
        self.draw_explosion()

    def draw_explosion(self):
        # Draw explosion as expanding circle
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        radius = int(self.frame * self.size / 10)
        pygame.draw.circle(self.image, (255, 200, 50, self.alpha), 
                          (self.size//2, self.size//2), radius)
        pygame.draw.circle(self.image, (255, 120, 0, self.alpha), 
                          (self.size//2, self.size//2), int(radius * 0.8))
        pygame.draw.circle(self.image, (255, 50, 0, self.alpha), 
                          (self.size//2, self.size//2), int(radius * 0.6))

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame > 10:
                self.kill()
            else:
                self.alpha = max(0, self.alpha - 25)
                self.draw_explosion()

# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
bosses = pygame.sprite.Group()

# Player instantiation
player = Player()
all_sprites.add(player)

# Score and game state
score = 0
font_name = pygame.font.match_font('arial')
level = 1
game_level = 1  # Different from level - this is the major game stage

def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_health_bar(surf, x, y, pct, max_pct=100, color=GREEN):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / max_pct) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def new_powerup():
    # Choose power-up type with different probabilities
    roll = random.random()
    if roll < 0.3:
        powerup_type = "shield"
    elif roll < 0.6:
        powerup_type = "gun_upgrade"
    elif roll < 0.7:
        powerup_type = "ultrakill"
    elif roll < 0.9:
        powerup_type = "health"
    else:
        powerup_type = "life"
        
    powerup = PowerUp(powerup_type)
    all_sprites.add(powerup)
    powerups.add(powerup)

def spawn_enemies(count, level_num):
    for _ in range(count):
        enemy_type = random.choice([Enemy, Enemy2])
        enemy = enemy_type(level_num)
        enemy.target = player
        all_sprites.add(enemy)
        enemies.add(enemy)

def show_game_over_screen():
    screen.fill(BLACK)
    draw_text(screen, "ULTIMATE SHOOTER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, YELLOW)
    draw_text(screen, f"Final Score: {score}", 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, WHITE)
    draw_text(screen, "Press ENTER to play again", 24, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, WHITE)
    draw_text(screen, "Press ESCAPE to quit", 24, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, WHITE)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def show_level_screen(level_num):
    screen.fill(BLACK)
    draw_text(screen, f"LEVEL {level_num}", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, YELLOW)
    
    # Different messages for different levels
    if level_num == 1:
        draw_text(screen, "Destroy the enemies and collect power-ups!", 24, 
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
    elif level_num == 2:
        draw_text(screen, "Watch out for more aggressive enemies!", 24, 
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
        draw_text(screen, "The boss is stronger this time!", 24, 
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, WHITE)
                
    draw_text(screen, "Press any key to start", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 3, WHITE)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def reset_level(level_num):
    # Clear all sprites
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    bosses.empty()
    
    # Respawn player
    player = Player()
    all_sprites.add(player)
    
    # Create boss for this level
    boss = Boss(level_num)
    boss.target = player
    all_sprites.add(boss)
    bosses.add(boss)
    
    # Spawn initial enemies
    spawn_enemies(5 + level_num * 3, level_num)
    
    return player, boss

# Game Loop
running = True
clock = pygame.time.Clock()
game_level = 1
level = 1
spawn_timer = 0
powerup_timer = 0
game_over = False
pause = False
scroll_y = 0

# Initialize boss
boss = Boss(game_level)
boss.target = player
all_sprites.add(boss)
bosses.add(boss)

# Initial enemy spawn
spawn_enemies(8, game_level)

# Show level screen
show_level_screen(game_level)

while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = not pause
            if event.key == pygame.K_ESCAPE:
                running = False

    if pause:
        draw_text(screen, "PAUSED", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
        pygame.display.flip()
        continue

    if game_over:
        show_game_over_screen()
        game_over = False
        score = 0
        game_level = 1
        level = 1
        player, boss = reset_level(game_level)
        continue
        
    # Update
    all_sprites.update()
    
    now = pygame.time.get_ticks()

    # Spawn Enemies
    if (now - spawn_timer > 2000 - (level * 100) and 
        len(enemies) < 10 + level and 
        not boss.active):
        enemy_type = random.choice([Enemy, Enemy2])
        enemy = enemy_type(game_level)
        enemy.target = player
        all_sprites.add(enemy)
        enemies.add(enemy)
        spawn_timer = now

    # Spawn Powerups
    if random.randint(0, 5000) < 5 + level and now - powerup_timer > 5000:
        new_powerup()
        powerup_timer = now

    # Check for bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullet_list in hits.items():
        for bullet in bullet_list:
            if enemy.damage(1):
                # Create explosion
                explosion = Explosion(enemy.rect.center[0], enemy.rect.center[1], 30)
                all_sprites.add(explosion)
                
                # Add score
                score += 10 * game_level
                
                # Random chance for power-up
                if random.random() < 0.1:  # 10% chance
                    new_powerup()

    # Check for bullet-boss collisions
    boss_hits = pygame.sprite.groupcollide(bosses, bullets, False, True)
    for boss, bullet_list in boss_hits.items():
        for bullet in bullet_list:
            if boss.damage(1):
                # Create big explosion
                for _ in range(5):
                    explosion = Explosion(
                        boss.rect.centerx + random.randint(-40, 40),
                        boss.rect.centery + random.randint(-30, 30),
                        50)
                    all_sprites.add(explosion)
                
                # Add score
                score += 100 * game_level
                
                # Level completed
                if game_level == 1:
                    # Move to level 2
                    game_level = 2
                    level = 1
                    show_level_screen(game_level)
                    player, boss = reset_level(game_level)
                else:
                    # Game completed
                    draw_text(screen, "CONGRATULATIONS!", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, YELLOW)
                    draw_text(screen, "You've completed the game!", 36, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
                    draw_text(screen, f"Final Score: {score}", 24, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50, WHITE)
                    draw_text(screen, "Press any key to play again", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 3, WHITE)
                    pygame.display.flip()
                    
                    # Wait for key press
                    waiting = True
                    while waiting:
                        clock.tick(60)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                waiting = False
                    
                    # Reset game
                    game_level = 1
                    level = 1
                    score = 0
                    player, boss = reset_level(game_level)
                    show_level_screen(game_level)

    # Check for enemy bullets hitting player
    player_shot = pygame.sprite.spritecollide(player, enemy_bullets, True)
    if player_shot:
        for bullet in player_shot:
            if player.damage(10):
                game_over = True

    # Check for enemies hitting player
    player_hits = pygame.sprite.spritecollide(player, enemies, False)
    for enemy in player_hits:
        if player.damage(20):
            game_over = True
        # Create a small explosion
        explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 20)
        all_sprites.add(explosion)
        enemy.kill()

    # Check for powerup collection
    powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
    for powerup in powerup_hits:
        powerup_sound.play()
        if powerup.type == "shield":
            player.shield = True
            player.shield_timer = pygame.time.get_ticks()
        elif powerup.type == "gun_upgrade":
            player.upgrade_gun()
        elif powerup.type == "ultrakill":
            ultrakill_sound.play()
            for enemy in enemies:
                # Create explosions for all enemies
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 30)
                all_sprites.add(explosion)
                enemy.kill()
                score += 20 * game_level
        elif powerup.type == "health":
            player.health = min(player.health + 25, 100)
        elif powerup.type == "life":
            player.lives += 1

    # Increase level
    if score >= level * 100:
        level += 1
        if level == 5 and not boss.active:
            boss.active = True
            boss.rect.centerx = SCREEN_WIDTH // 2
            boss.rect.y = -100  # Start offscreen
            
    # Draw / Render
    # Select appropriate background based on game level
    current_bg = background_img if game_level == 1 else background2_img
    
    # Scrolling Background
    rel_y = scroll_y % current_bg.get_rect().height
    screen.blit(current_bg, (0, rel_y - current_bg.get_rect().height))
    if rel_y < SCREEN_HEIGHT:
        screen.blit(current_bg, (0, rel_y))
    scroll_y += 2  # Speed up scrolling

    # Draw shield if active
    if player.shield:
        screen.blit(shield_img, (player.rect.centerx - 30, player.rect.centery - 30))

    all_sprites.draw(screen)

    # Draw UI
    draw_text(screen, f"Score: {score}", 18, SCREEN_WIDTH / 2, 10)
    draw_text(screen, f"Level: {level}", 18, SCREEN_WIDTH / 4, 10)
    draw_health_bar(screen, SCREEN_WIDTH / 4 * 3 - 50, 10, player.health)
    draw_text(screen, f"Lives: {player.lives}", 18, SCREEN_WIDTH / 8, 10)
    
    # Show gun level
    draw_text(screen, f"Gun: {player.gun_level}", 18, SCREEN_WIDTH / 8, 30)

    if player.shield:
        draw_text(screen, "SHIELD ACTIVE", 24, SCREEN_WIDTH / 2, 40, BLUE)

    # Display boss health when active
    for boss in bosses:
        if boss.active:
            boss_health_pct = boss.health / boss.max_health * 100
            draw_text(screen, f"BOSS", 24, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50, RED)
            draw_health_bar(screen, SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT - 30, 
                          boss.health, boss.max_health, RED)

    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

pygame.quit()
sys.exit()