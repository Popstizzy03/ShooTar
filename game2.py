import pygame
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Load Assets
player_img = pygame.image.load("player.png").convert_alpha()  # Replace with your image
player_img = pygame.transform.scale(player_img, (50, 40))  # Scale it

bullet_img = pygame.image.load("bullet.png").convert_alpha() # Replace with your image
bullet_img = pygame.transform.scale(bullet_img, (5, 10))

enemy_img = pygame.image.load("enemy.png").convert_alpha() # Replace with your image
enemy_img = pygame.transform.scale(enemy_img, (30, 30))

powerup_img = pygame.image.load("powerup.png").convert_alpha() # Replace with your image
powerup_img = pygame.transform.scale(powerup_img, (20, 20))


shoot_sound = pygame.mixer.Sound("shoot.wav") # Replace with your sound file
explosion_sound = pygame.mixer.Sound("explosion.wav") # Replace with your sound file
powerup_sound = pygame.mixer.Sound("powerup.wav") # Replace with your sound file
pygame.mixer.music.load("background.wav") # Replace with your background music
pygame.mixer.music.set_volume(0.5) # Adjust the volume as needed
pygame.mixer.music.play(-1)  # Play indefinitely

# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img #pygame.Surface([50, 40])  # Placeholder
        #self.image.fill(GREEN)  # Green rectangle
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.speed_x = 0
        self.health = 100
        self.lives = 3
        self.protected = False  # Invulnerability after being hit
        self.protected_timer = 0

    def update(self):
        self.speed_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x

        # Keep player within screen boundaries
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
                self.health = 100  # Reset health, but decrease lives
                if self.lives <= 0:
                    return True  # Game Over

        return False # Not game over

# Bullet Class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img #pygame.Surface([5, 10])
        #self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        # Kill the bullet if it goes offscreen
        if self.rect.bottom < 0:
            self.kill()


# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img #pygame.Surface([30, 30])
        #self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -40) # Start offscreen
        self.speed_y = random.randrange(1, 3)
        self.speed_x = random.randrange(-2, 2)  # Add horizontal movement
        self.health = 2 # Basic enemy health

    def update(self):
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
        self.image = powerup_img #pygame.Surface([20, 20])
        #self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill() # Remove when off screen

# Sprite Groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Player instantiation
player = Player()
all_sprites.add(player)

# Enemy instantiation (create a few enemies)
for _ in range(8):  #Create 8 enemies
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Score
score = 0
font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def new_powerup():
    powerup = PowerUp()
    all_sprites.add(powerup)
    powerups.add(powerup)

# Game Loop
running = True
clock = pygame.time.Clock()
level = 1
spawn_timer = 0
powerup_timer = 0
game_over = False

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

    # Spawn Enemies based on level
    if pygame.time.get_ticks() - spawn_timer > 2000 - (level * 100) and len(enemies) < 10:
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        spawn_timer = pygame.time.get_ticks()

    # Spawn Powerups Randomly
    if random.randint(0, 5000) < 5 and pygame.time.get_ticks() - powerup_timer > 5000:
        new_powerup()
        powerup_timer = pygame.time.get_ticks()

    # Check for collisions between bullets and enemies
    collisions = pygame.sprite.groupcollide(enemies, bullets, False, True)  # Kill bullet
    for enemy, bullet_list in collisions.items():
        for bullet in bullet_list:
            if enemy.damage(1):  # Damage the enemy
                explosion_sound.play()
                score += 10
                enemy = Enemy() # Replace destroyed enemy
                all_sprites.add(enemy)
                enemies.add(enemy)

    # Check for collisions between player and enemies
    player_hits = pygame.sprite.spritecollide(player, enemies, False) # Don't kill enemy

    for enemy in player_hits:
        if player.damage(20): # Take Damage
            game_over = True # Game over

    # Powerup collision
    powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
    for powerup in powerup_hits:
        player.health = min(player.health + 50, 100) # Heal player
        powerup_sound.play()

    # Increase level if score is high enough
    if score >= level * 100:
        level += 1

    # Game Over Handling
    if game_over:
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(screen, "Press any key to restart", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        pygame.display.flip()
        waiting = True
        while waiting:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                if event.type == pygame.KEYUP:
                    # Reset Game
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
    screen.fill(BLACK)  # Background

    all_sprites.draw(screen)  # Draw all sprites

    # Draw UI
    draw_text(screen, "Score: " + str(score), 18, SCREEN_WIDTH / 2, 10)
    draw_text(screen, "Level: " + str(level), 18, SCREEN_WIDTH / 4, 10)
    draw_text(screen, "Health: " + str(player.health), 18, SCREEN_WIDTH / 4 * 3, 10)
    draw_text(screen, "Lives: " + str(player.lives), 18, SCREEN_WIDTH / 8 , 10)

    pygame.display.flip()  # Update the display

    # Limit frame rate
    clock.tick(60)  # 60 frames per second

pygame.quit()
sys.exit()
