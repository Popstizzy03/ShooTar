import pygame
import random
import sys
from sprites import Player, Enemy, Enemy2, Boss, Bullet, PowerUp
from ai import enemy_ai
from powerups import apply_powerup
from ui import draw_text, draw_health_bar, draw_powerup_icons
from audio import play_sound, play_music
from levels import load_level, Level

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultimate Enhanced Shooter")

# --- Constants ---
FPS = 60
SPAWN_EVENT = pygame.USEREVENT + 1  # Custom event for enemy spawning
POWERUP_EVENT = pygame.USEREVENT + 2 # Custom event for powerup spawning
GAME_OVER_EVENT = pygame.USEREVENT + 3 # Custom event for game over

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

# --- Asset Loading (Moved to sprites.py but needed here) ---
background_img = pygame.image.load("background.png").convert()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Game Setup ---
clock = pygame.time.Clock()
scroll_y = 0

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# --- Player Setup ---
player = Player()
all_sprites.add(player)

# --- Level Setup ---
current_level = Level(1)  # Initialize with level 1
load_level(current_level, enemies, all_sprites)  # Load the initial level's enemies

# --- Game Variables ---
score = 0
level_number = 1
game_over = False
paused = False
currency = 0 # Starting currency
wave = 0 # Start at wave 0
font_name = pygame.font.match_font('arial')

# --- Event Timers ---
pygame.time.set_timer(SPAWN_EVENT, 2000)  # Initial spawn interval
pygame.time.set_timer(POWERUP_EVENT, 10000) # Initial Powerup Spawn
# --- Game Loop ---
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
            if event.key == pygame.K_p:
                paused = not paused # Pause game
        if event.type == SPAWN_EVENT and not paused and not game_over:
            enemy_ai.spawn_enemy(enemies, all_sprites, player, current_level) # Use the AI to spawn
        if event.type == POWERUP_EVENT and not paused and not game_over:
            PowerUp.spawn_powerup(powerups, all_sprites) # Use powerup spawning mechanism
        # Process Power Up related events
        if event.type == pygame.USEREVENT and event.code == "speed_boost_end": # Example
            player.max_speed /= 1.5 # Revert speed boost
            print("Speed Boost ended")

    # --- Update ---
    if not paused and not game_over:
        all_sprites.update() # Update all sprites

        # --- Collision Detection ---
        # Bullets and Enemies
        collisions = pygame.sprite.groupcollide(enemies, bullets, False, True) # Don't kill enemy initially
        for enemy, bullet_list in collisions.items():
            for bullet in bullet_list:
                if enemy.damage(bullet.damage): # Call enemy's damage function
                    play_sound("explosion")
                    score += enemy.score_value # Increase score
                    currency += enemy.currency_drop  # increase currency
                    enemy.kill()  # Remove enemy
                    # Spawn new enemies
                    enemy_ai.spawn_enemy(enemies, all_sprites, player, current_level)

        # Player and Enemies
        player_hits = pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask) # Use mask for collision
        for enemy in player_hits:
            if player.damage(enemy.damage_value):
                play_sound("game_over") # Can change for hit sound
                game_over = True  # Game Over

        # Powerups and Player
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            play_sound("powerup")
            apply_powerup(player, powerup, all_sprites, bullets)

        # Check level progress
        if len(enemies) == 0: # Check if all enemies have been defeated
            current_level.advance_wave() # advance to the next wave
            if current_level.current_wave > current_level.total_waves:
                level_number += 1  # increase the level
                current_level = Level(level_number) # reset level
            # Reload the level
            load_level(current_level, enemies, all_sprites)

    # --- Draw / Render ---
    # Scrolling Background
    rel_y = scroll_y % background_img.get_rect().height
    screen.blit(background_img, (0, rel_y - background_img.get_rect().height))
    if rel_y < SCREEN_HEIGHT:
        screen.blit(background_img, (0, rel_y))
    scroll_y += 1

    all_sprites.draw(screen) # Draw all sprites

    # UI Elements
    draw_text(screen, f"Score: {score}", 18, SCREEN_WIDTH // 2, 10, WHITE, font_name)
    draw_text(screen, f"Level: {level_number}", 18, SCREEN_WIDTH // 4, 10, WHITE, font_name)
    draw_health_bar(screen, SCREEN_WIDTH * 3 // 4 - 50, 10, player.health, WHITE, GREEN) # Health Bar
    draw_text(screen, f"Lives: {player.lives}", 18, SCREEN_WIDTH // 8, 10, WHITE, font_name)
    draw_text(screen, f"Wave: {current_level.current_wave}/{current_level.total_waves}", 18, SCREEN_WIDTH * 5 // 8, 10, WHITE, font_name)
    draw_powerup_icons(screen, player.active_powerups, 5, 40, 20) # Draw powerups
    # Pause message
    if paused:
        draw_text(screen, "PAUSED", 48, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE, font_name)
    if game_over:
        draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, RED, font_name)
        draw_text(screen, "Press any key to restart", 22, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE, font_name)

        # Reset everything after key is pressed
        waiting = True
        while waiting:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                if event.type == pygame.KEYUP: # Reset game
                    game_over = False
                    paused = False
                    waiting = False
                    score = 0 # reset score
                    level_number = 1 # Reset Level Number
                    current_level = Level(1)
                    currency = 0
                    # Remove all Sprites and recreate them
                    for sprite in all_sprites:
                        sprite.kill()
                    # Reset player
                    player = Player()
                    all_sprites.add(player)
                    # Reload level
                    load_level(current_level, enemies, all_sprites) # Load the initial level's enemies
                    break

    # --- Update Display ---
    pygame.display.flip()

    # --- Limit Frame Rate ---
    clock.tick(FPS)

# --- Quit Pygame ---
pygame.quit()
sys.exit()