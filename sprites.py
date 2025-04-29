import pygame
import random

# --- Asset Loading ---
player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 40))
player_mask = pygame.mask.from_surface(player_img)  # Collision mask

bullet_img = pygame.image.load("bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (5, 10))

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (30, 30))
enemy_mask = pygame.mask.from_surface(enemy_img)

enemy2_img = pygame.image.load("enemy2.png").convert_alpha()
enemy2_img = pygame.transform.scale(enemy2_img, (35, 35))
enemy2_mask = pygame.mask.from_surface(enemy2_img)

boss_img = pygame.image.load("boss.png").convert_alpha()
boss_img = pygame.transform.scale(boss_img, (100, 80))
boss_mask = pygame.mask.from_surface(boss_img)

powerup_img = pygame.image.load("powerup.png").convert_alpha()
powerup_img = pygame.transform.scale(powerup_img, (20, 20))

# --- Classes ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.mask = player_mask # Set mask
        self.rect = self.image.get_rect()
        self.rect.center = (400, 550) # Start position
        self.speed_x = 0
        self.health = 100
        self.lives = 3
        self.protected = False
        self.protected_timer = 0
        self.acceleration = 0.5
        self.max_speed = 8
        self.friction = 0.1
        self.active_powerups = {} # To keep track of active powerups

    def update(self):
        # --- Movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x -= self.acceleration
        elif keys[pygame.K_RIGHT]:
            self.speed_x += self.acceleration
        else:
            # Apply friction
            if self.speed_x > 0:
                self.speed_x -= self.friction
                if self.speed_x < 0:
                    self.speed_x = 0
            elif self.speed_x < 0:
                self.speed_x += self.friction
                if self.speed_x > 0:
                    self.speed_x = 0

        # Limit speed
        if self.speed_x > self.max_speed:
            self.speed_x = self.max_speed
        elif self.speed_x < -self.max_speed:
            self.speed_x = -self.max_speed

        self.rect.x += self.speed_x

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 800:
            self.rect.right = 800

        # --- Timers ---
        if self.protected and pygame.time.get_ticks() - self.protected_timer > 1000:
            self.protected = False

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, 10) # Base damage is 10
        all_sprites.add(bullet)
        bullets.add(bullet)
        play_sound("shoot")

    def damage(self, amount):
        if self.protected:
            return False

        self.health -= amount
        self.protected = True
        self.protected_timer = pygame.time.get_ticks()
        if self.health <= 0:
            self.lives -= 1
            self.health = 100
            if self.lives <= 0:
                return True # Game Over
        return False # Not game over yet

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10
        self.damage = damage # Assign damage value to the bullet

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y, health, score_value, damage_value, currency_drop, image=enemy_img, mask=enemy_mask):
        super().__init__()
        self.image = image
        self.mask = mask
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = speed_y
        self.health = health
        self.score_value = score_value # Points player gets for killing this enemy
        self.damage_value = damage_value # Damage this enemy does to player upon collision
        self.currency_drop = currency_drop # Currency the player gets for killing
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > 600: # Check if goes offscreen
            self.kill()
    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True
        return False

class Enemy2(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 3, 1, 20, 10, 2, enemy2_img, enemy2_mask) # Call Enemy constructor

class Boss(pygame.sprite.Sprite):
    def __init__(self, health, damage_value):
        super().__init__()
        self.image = boss_img
        self.mask = boss_mask # set mask
        self.rect = self.image.get_rect()
        self.rect.centerx = 400
        self.rect.y = -100 # Start offscreen
        self.speed_x = 2
        self.speed_y = 1 # Initial speed
        self.health = health # start health
        self.damage_value = damage_value # Damage to player
        self.phase = 1 # Initial phase of the boss
        self.attack_timer = 0 # Time between attacks
        self.score_value = 500
        self.currency_drop = 50

    def update(self):
        # Boss movement
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left < 0 or self.rect.right > 800:
            self.speed_x *= -1 # Bounce off sides

        if self.rect.top < 50 or self.rect.bottom > 200:
            self.speed_y *= -1

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True
        return False

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, type, image=powerup_img):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 750)
        self.rect.y = random.randint(-100, -50) # Start offscreen
        self.speed_y = 2
        self.type = type # "health", "damage", "shield", etc.
        self.powerup_duration = 5000 # Powerup effect duration in milliseconds

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > 600:
            self.kill() # Remove powerup

    @staticmethod # Static method
    def spawn_powerup(group, all_sprites): # Pass the sprite groups
        powerup_type = random.choice(["health", "damage", "shield", "speed"])
        powerup = PowerUp(powerup_type)
        all_sprites.add(powerup)
        group.add(powerup)