import pygame
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)

# Load Assets
player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 40))

bullet_img = pygame.image.load("bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (5, 10))

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (30, 30))

powerup_img = pygame.image.load("powerup.png").convert_alpha()
powerup_img = pygame.transform.scale(powerup_img, (20, 20))

background_img = pygame.image.load("background.png").convert()  # Static background
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))


shoot_sound = pygame.mixer.Sound("shoot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
powerup_sound = pygame.mixer.Sound("powerup.wav")
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


    def update(self):
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
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        if self.protected and pygame.time.get_ticks() - self.protected_timer > 1000:
            self.protected = False

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

    def damage(self, amount):
        if not self.protected:
            self.health -= amount
            self.protected = True
            self.protected_timer = pygame.time.get_ticks()
            if self.health <= 0:
                self.lives -= 1
                self.health = 100
                if self.lives <= 0:
                    return True

        return False

# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -40)
        self.speed_y = random.randrange(1, 3)
        self.speed_x = random.randrange(-2, 2)
        self.health = 2
        self.target = player  # Target the player for AI

    def update(self):
        # Basic AI: Try to move towards the player's x position
        if self.rect.centerx < self.target.rect.centerx:
            self.speed_x = 1  # Move right
        elif self.rect.centerx > self.target.rect.centerx:
            self.speed_x = -1  # Move left
        else:
            self.speed_x = 0 # Stop if aligned

        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        # Bounce off the sides
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1

        # Reset enemy if it goes off the bottom
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -40)
            self.speed_y = random.randrange(1, 3)

        if self.health <= 0:
            self.kill()

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            explosion_sound.play()
            return True
        return False

# Power-up Class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = powerup_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Player instantiation
player = Player()
all_sprites.add(player)

# Enemy instantiation
for _ in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Score
score = 0
font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def new_powerup():
    powerup = PowerUp()
    all_sprites.add(powerup)
    powerups.add(powerup)

def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# Game Loop
running = True
clock = pygame.time.Clock()
level = 1
spawn_timer = 0
powerup_timer = 0
game_over = False
scroll_y = 0  # For background scrolling


while running:
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update
    all_sprites.update()

    # Spawn Enemies
    if pygame.time.get_ticks() - spawn_timer > 2000 - (level * 100) and len(enemies) < 10:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        spawn_timer = pygame.time.get_ticks()

    # Spawn Powerups
    if random.randint(0, 5000) < 5 and pygame.time.get_ticks() - powerup_timer > 5000:
        new_powerup()
        powerup_timer = pygame.time.get_ticks()

    # Check for collisions
    collisions = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullet_list in collisions.items():
        for bullet in bullet_list:
            if enemy.damage(1):
                explosion_sound.play()
                score += 10
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)

    player_hits = pygame.sprite.spritecollide(player, enemies, False)
    for enemy in player_hits:
        if player.damage(20):
            game_over = True

    powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
    for powerup in powerup_hits:
        player.health = min(player.health + 50, 100)
        powerup_sound.play()

    # Increase level
    if score >= level * 100:
        level += 1

    # Game Over Handling
    if game_over:
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, RED)
        draw_text(screen, "Press any key to restart", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
        pygame.display.flip()
        waiting = True
        while waiting:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                if event.type == pygame.KEYUP:
                    game_over = False
                    waiting = False
                    score = 0
                    level = 1
                    player = Player()
                    all_sprites = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    powerups = pygame.sprite.Group()
                    all_sprites.add(player)
                    for _ in range(8):
                        enemy = Enemy()
                        all_sprites.add(enemy)
                        enemies.add(enemy)

    # Draw / Render
    # Scrolling Background
    rel_y = scroll_y % background_img.get_rect().height
    screen.blit(background_img, (0, rel_y - background_img.get_rect().height))
    if rel_y < SCREEN_HEIGHT:
        screen.blit(background_img, (0, rel_y))
    scroll_y += 1

    all_sprites.draw(screen)

    # Draw UI
    draw_text(screen, "Score: " + str(score), 18, SCREEN_WIDTH / 2, 10, WHITE)
    draw_text(screen, "Level: " + str(level), 18, SCREEN_WIDTH / 4, 10, WHITE)
    draw_health_bar(screen, SCREEN_WIDTH / 4 * 3 - 50, 10, player.health)
    draw_text(screen, "Lives: " + str(player.lives), 18, SCREEN_WIDTH / 8 , 10, WHITE)

    pygame.display.flip()

    # Limit frame rate
    clock.tick(60)

pygame.quit()
sys.exit()