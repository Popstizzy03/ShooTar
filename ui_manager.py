import pygame
import json
from config import *

class UIManager:
    def __init__(self):
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        self.font_title = pygame.font.Font(None, 72)
        
        self.screen_shake_offset = (0, 0)
        self.shake_timer = 0
        self.shake_intensity = 0
        
        # Menu state
        self.menu_selection = 0
        self.menu_options = []
        
        # Achievement notifications
        self.achievement_notifications = []
        
    def draw_text(self, surface, text, size, x, y, color=WHITE, center=True):
        if size == "small":
            font = self.font_small
        elif size == "medium":
            font = self.font_medium
        elif size == "large":
            font = self.font_large
        elif size == "title":
            font = self.font_title
        else:
            font = pygame.font.Font(None, size)
            
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect()
        
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
            
        surface.blit(text_surface, text_rect)
        return text_rect
        
    def draw_health_bar(self, surface, x, y, current, maximum, width=100, height=10, color=GREEN):
        if current < 0:
            current = 0
            
        # Calculate fill percentage
        fill_percentage = current / maximum if maximum > 0 else 0
        fill_width = int(width * fill_percentage)
        
        # Background
        background_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, DARK_RED, background_rect)
        
        # Fill
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y, fill_width, height)
            pygame.draw.rect(surface, color, fill_rect)
            
        # Border
        pygame.draw.rect(surface, WHITE, background_rect, 2)
        
    def draw_hud(self, surface, player, level=1, score=0):
        # Apply screen shake
        shake_x, shake_y = self.get_screen_shake()
        
        # Player stats
        self.draw_text(surface, f"Score: {score}", "small", 10 + shake_x, 10 + shake_y, WHITE, False)
        self.draw_text(surface, f"Level: {level}", "small", 10 + shake_x, 30 + shake_y, WHITE, False)
        self.draw_text(surface, f"Lives: {player.lives}", "small", 10 + shake_x, 50 + shake_y, WHITE, False)
        
        # Health bar
        self.draw_health_bar(surface, 10 + shake_x, 70 + shake_y, player.health, player.max_health, 150, 12)
        
        # Weapon info
        weapon_text = f"Weapon: {player.weapon_type.name}"
        self.draw_text(surface, weapon_text, "small", 10 + shake_x, 90 + shake_y, WHITE, False)
        
        # Active power-ups
        y_offset = 110
        for powerup in player.active_powerups:
            self.draw_text(surface, f"{powerup.upper()}", "small", 10 + shake_x, y_offset + shake_y, YELLOW, False)
            y_offset += 20
            
        # Shield indicator
        if player.shield:
            self.draw_text(surface, "SHIELD ACTIVE", "medium", SCREEN_WIDTH // 2 + shake_x, 50 + shake_y, BLUE)
            
        # Achievement notifications
        self.draw_achievement_notifications(surface)
        
    def draw_boss_hud(self, surface, boss):
        if not boss.active:
            return
            
        shake_x, shake_y = self.get_screen_shake()
        
        # Boss name and phase
        boss_name = f"BOSS - Phase {boss.phase}"
        self.draw_text(surface, boss_name, "medium", SCREEN_WIDTH // 2 + shake_x, 30 + shake_y, RED)
        
        # Boss health bar
        bar_width = 300
        bar_height = 15
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 50
        
        self.draw_health_bar(surface, bar_x + shake_x, bar_y + shake_y, 
                           boss.health, boss.max_health, bar_width, bar_height, RED)
        
    def draw_menu(self, surface, title, options, selected_index=0):
        surface.fill(BLACK)
        
        # Title
        self.draw_text(surface, title, "title", SCREEN_WIDTH // 2, 100, GOLD)
        
        # Options
        for i, option in enumerate(options):
            color = YELLOW if i == selected_index else WHITE
            y_pos = 300 + i * 50
            self.draw_text(surface, option, "large", SCREEN_WIDTH // 2, y_pos, color)
            
        # Instructions
        self.draw_text(surface, "Use UP/DOWN arrows to navigate, ENTER to select", "small", 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, GREY)
        
    def draw_game_over_screen(self, surface, score, high_score=0):
        surface.fill(BLACK)
        
        # Game Over text
        self.draw_text(surface, "GAME OVER", "title", SCREEN_WIDTH // 2, 200, RED)
        
        # Score
        self.draw_text(surface, f"Final Score: {score}", "large", SCREEN_WIDTH // 2, 300, WHITE)
        
        if score > high_score:
            self.draw_text(surface, "NEW HIGH SCORE!", "medium", SCREEN_WIDTH // 2, 350, GOLD)
        else:
            self.draw_text(surface, f"High Score: {high_score}", "medium", SCREEN_WIDTH // 2, 350, YELLOW)
            
        # Instructions
        self.draw_text(surface, "Press ENTER to play again", "medium", SCREEN_WIDTH // 2, 450, WHITE)
        self.draw_text(surface, "Press ESC to return to menu", "medium", SCREEN_WIDTH // 2, 500, WHITE)
        
    def draw_pause_screen(self, surface):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Pause text
        self.draw_text(surface, "PAUSED", "title", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        self.draw_text(surface, "Press P to resume", "medium", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, GREY)
        
    def draw_level_complete_screen(self, surface, level, score, bonus=0):
        surface.fill(BLACK)
        
        # Level complete text
        self.draw_text(surface, f"LEVEL {level} COMPLETE!", "title", SCREEN_WIDTH // 2, 200, GREEN)
        
        # Score breakdown
        self.draw_text(surface, f"Score: {score}", "large", SCREEN_WIDTH // 2, 300, WHITE)
        if bonus > 0:
            self.draw_text(surface, f"Bonus: +{bonus}", "large", SCREEN_WIDTH // 2, 350, YELLOW)
            
        # Instructions
        self.draw_text(surface, "Press ENTER to continue", "medium", SCREEN_WIDTH // 2, 450, WHITE)
        
    def draw_settings_screen(self, surface, settings):
        surface.fill(BLACK)
        
        # Title
        self.draw_text(surface, "SETTINGS", "title", SCREEN_WIDTH // 2, 100, GOLD)
        
        # Settings options
        y_pos = 200
        for setting, value in settings.items():
            setting_text = f"{setting.replace('_', ' ').title()}: {value}"
            self.draw_text(surface, setting_text, "medium", SCREEN_WIDTH // 2, y_pos, WHITE)
            y_pos += 50
            
        # Instructions
        self.draw_text(surface, "Use LEFT/RIGHT arrows to adjust, ESC to return", "small", 
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, GREY)
        
    def draw_achievements_screen(self, surface, achievements):
        surface.fill(BLACK)
        
        # Title
        self.draw_text(surface, "ACHIEVEMENTS", "title", SCREEN_WIDTH // 2, 100, GOLD)
        
        # Achievement list
        y_pos = 200
        for achievement in achievements:
            color = GREEN if achievement['unlocked'] else GREY
            self.draw_text(surface, achievement['name'], "medium", SCREEN_WIDTH // 4, y_pos, color, False)
            self.draw_text(surface, achievement['description'], "small", SCREEN_WIDTH // 4, y_pos + 25, WHITE, False)
            y_pos += 70
            
        # Instructions
        self.draw_text(surface, "Press ESC to return", "small", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, GREY)
        
    def draw_loading_screen(self, surface, progress, message="Loading..."):
        surface.fill(BLACK)
        
        # Loading message
        self.draw_text(surface, message, "large", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, WHITE)
        
        # Progress bar
        bar_width = 400
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT // 2
        
        # Background
        pygame.draw.rect(surface, GREY, (bar_x, bar_y, bar_width, bar_height))
        
        # Progress fill
        fill_width = int(bar_width * progress)
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Percentage
        percent_text = f"{int(progress * 100)}%"
        self.draw_text(surface, percent_text, "medium", SCREEN_WIDTH // 2, bar_y + 40, WHITE)
        
    def screen_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_timer = pygame.time.get_ticks() + duration
        
    def get_screen_shake(self):
        if pygame.time.get_ticks() < self.shake_timer:
            import random
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            return offset_x, offset_y
        return 0, 0
        
    def add_achievement_notification(self, achievement_name, description):
        notification = {
            'name': achievement_name,
            'description': description,
            'timer': pygame.time.get_ticks() + 3000,  # Show for 3 seconds
            'y_pos': len(self.achievement_notifications) * 60
        }
        self.achievement_notifications.append(notification)
        
    def draw_achievement_notifications(self, surface):
        current_time = pygame.time.get_ticks()
        
        for notification in self.achievement_notifications[:]:
            if current_time > notification['timer']:
                self.achievement_notifications.remove(notification)
                continue
                
            # Notification background
            notification_rect = pygame.Rect(SCREEN_WIDTH - 320, notification['y_pos'], 300, 50)
            pygame.draw.rect(surface, (0, 0, 0, 180), notification_rect)
            pygame.draw.rect(surface, GOLD, notification_rect, 2)
            
            # Notification text
            self.draw_text(surface, "Achievement Unlocked!", "small", 
                          SCREEN_WIDTH - 170, notification['y_pos'] + 10, GOLD, False)
            self.draw_text(surface, notification['name'], "small", 
                          SCREEN_WIDTH - 170, notification['y_pos'] + 30, WHITE, False)
                          
    def draw_mini_map(self, surface, player, enemies, powerups):
        # Mini-map in top-right corner
        map_size = 150
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = 10
        
        # Background
        map_rect = pygame.Rect(map_x, map_y, map_size, map_size)
        pygame.draw.rect(surface, (0, 0, 0, 100), map_rect)
        pygame.draw.rect(surface, WHITE, map_rect, 2)
        
        # Scale factor
        scale_x = map_size / SCREEN_WIDTH
        scale_y = map_size / SCREEN_HEIGHT
        
        # Draw player
        player_x = map_x + int(player.rect.centerx * scale_x)
        player_y = map_y + int(player.rect.centery * scale_y)
        pygame.draw.circle(surface, GREEN, (player_x, player_y), 3)
        
        # Draw enemies
        for enemy in enemies:
            enemy_x = map_x + int(enemy.rect.centerx * scale_x)
            enemy_y = map_y + int(enemy.rect.centery * scale_y)
            pygame.draw.circle(surface, RED, (enemy_x, enemy_y), 2)
            
        # Draw power-ups
        for powerup in powerups:
            powerup_x = map_x + int(powerup.rect.centerx * scale_x)
            powerup_y = map_y + int(powerup.rect.centery * scale_y)
            pygame.draw.circle(surface, YELLOW, (powerup_x, powerup_y), 2)
            
    def draw_fps_counter(self, surface, clock):
        fps = int(clock.get_fps())
        color = GREEN if fps >= 50 else YELLOW if fps >= 30 else RED
        self.draw_text(surface, f"FPS: {fps}", "small", SCREEN_WIDTH - 60, SCREEN_HEIGHT - 20, color, False)
        
    def create_button(self, surface, text, x, y, width, height, color=GREY, text_color=WHITE, border_color=WHITE):
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, color, button_rect)
        pygame.draw.rect(surface, border_color, button_rect, 2)
        
        # Center text in button
        text_x = x + width // 2
        text_y = y + height // 2
        self.draw_text(surface, text, "medium", text_x, text_y, text_color)
        
        return button_rect
        
    def draw_explosion_effect(self, surface, x, y, radius, color=ORANGE):
        # Draw expanding circle effect
        pygame.draw.circle(surface, color, (int(x), int(y)), radius, 3)
        
    def draw_power_up_indicator(self, surface, powerup_type, x, y):
        # Draw power-up type indicator
        color_map = {
            "shield": BLUE,
            "weapon": GREEN,
            "health": RED,
            "speed": YELLOW,
            "life": PURPLE
        }
        
        color = color_map.get(powerup_type, WHITE)
        pygame.draw.circle(surface, color, (x, y), 8)
        pygame.draw.circle(surface, WHITE, (x, y), 8, 2)
        
    def handle_menu_input(self, event, options):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(options)
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(options)
            elif event.key == pygame.K_RETURN:
                return self.menu_selection
        return None
        
    def save_high_score(self, score):
        try:
            with open(SAVE_PATHS["highscores"], 'r') as f:
                scores = json.load(f)
        except:
            scores = []
            
        scores.append(score)
        scores.sort(reverse=True)
        scores = scores[:10]  # Keep top 10
        
        try:
            with open(SAVE_PATHS["highscores"], 'w') as f:
                json.dump(scores, f)
        except:
            pass
            
    def load_high_scores(self):
        try:
            with open(SAVE_PATHS["highscores"], 'r') as f:
                return json.load(f)
        except:
            return []
            
    def draw_high_scores(self, surface):
        surface.fill(BLACK)
        
        # Title
        self.draw_text(surface, "HIGH SCORES", "title", SCREEN_WIDTH // 2, 100, GOLD)
        
        # High scores
        scores = self.load_high_scores()
        y_pos = 200
        
        for i, score in enumerate(scores[:10]):
            rank_text = f"{i+1}. {score}"
            self.draw_text(surface, rank_text, "medium", SCREEN_WIDTH // 2, y_pos, WHITE)
            y_pos += 40
            
        if not scores:
            self.draw_text(surface, "No scores yet!", "medium", SCREEN_WIDTH // 2, y_pos, GREY)
            
        # Instructions
        self.draw_text(surface, "Press ESC to return", "small", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, GREY)