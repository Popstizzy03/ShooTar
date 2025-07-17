import pygame
import sys
from typing import Optional, Dict, Any
from config import *
from game_state import GameStateManager
from level_manager import LevelManager
from player import Player
from ui_manager import UIManager
from collision_manager import CollisionManager
from sound_manager import sound_manager
from asset_manager import asset_manager
from effects import effect_manager
from sprite_groups import sprite_groups
from powerups import PowerUp
from utils import Timer
import random

class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Initialize display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ShooTar - Ultimate Space Shooter")
        
        # Initialize game systems
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameStateManager()
        self.level_manager = LevelManager()
        self.ui_manager = UIManager()
        self.collision_manager = CollisionManager(sound_manager, self.ui_manager)
        
        # Initialize player
        self.player = None
        self.background_scroll_y = 0
        self.background_speed = 2
        
        # Game timers
        self.powerup_spawn_timer = Timer(POWERUP_SPAWN_RATE)
        self.auto_save_timer = Timer(30000)  # Auto-save every 30 seconds
        
        # Load all assets
        asset_manager.load_all_assets()
        
        # Start background music
        sound_manager.play_music("background_music", loops=-1)
        
        # Initialize game state
        self.game_state.change_state(GameState.MENU)
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
            
        self.cleanup()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event.key)
                
            elif event.type == pygame.KEYUP:
                self.handle_key_up(event.key)
                
            # Handle UI events
            if self.game_state.state == GameState.MENU:
                selection = self.ui_manager.handle_menu_input(event, self.get_menu_options())
                if selection is not None:
                    self.handle_menu_selection(selection)
                    
    def handle_key_down(self, key):
        if key == CONTROLS["quit"]:
            if self.game_state.state == GameState.PLAYING:
                self.game_state.change_state(GameState.MENU)
            else:
                self.running = False
                
        elif key == CONTROLS["pause"]:
            if self.game_state.state == GameState.PLAYING:
                self.game_state.toggle_pause()
                
        elif key == CONTROLS["restart"]:
            if self.game_state.state in [GameState.GAME_OVER, GameState.PLAYING]:
                self.start_new_game()
                
        elif key == pygame.K_RETURN:
            if self.game_state.state == GameState.GAME_OVER:
                self.start_new_game()
            elif self.game_state.state == GameState.LEVEL_COMPLETE:
                self.advance_to_next_level()
                
    def handle_key_up(self, key):
        pass
        
    def handle_menu_selection(self, selection):
        options = self.get_menu_options()
        if selection < len(options):
            option = options[selection]
            
            if option == "New Game":
                self.start_new_game()
            elif option == "Continue":
                if self.game_state.state == GameState.PAUSED:
                    self.game_state.toggle_pause()
                else:
                    self.game_state.change_state(GameState.PLAYING)
            elif option == "Settings":
                self.game_state.change_state(GameState.SETTINGS)
            elif option == "Achievements":
                self.game_state.change_state(GameState.ACHIEVEMENTS)
            elif option == "Quit":
                self.running = False
                
    def get_menu_options(self):
        if self.game_state.state == GameState.MENU:
            options = ["New Game"]
            if self.game_state.state == GameState.PAUSED:
                options.append("Continue")
            options.extend(["Settings", "Achievements", "Quit"])
            return options
        return []
        
    def start_new_game(self):
        self.game_state.start_new_game()
        self.level_manager.start_level(1)
        
        # Initialize player
        self.player = Player()
        sprite_groups.clear_all_except(["effects", "particles"])
        sprite_groups.add_sprite(self.player, ["all", "player"])
        
        # Initialize collision manager
        self.collision_manager.update_groups(
            player=sprite_groups.get_group("player"),
            enemies=sprite_groups.get_group("enemies"),
            bosses=sprite_groups.get_group("bosses"),
            player_bullets=sprite_groups.get_group("bullets"),
            enemy_bullets=sprite_groups.get_group("enemy_bullets"),
            powerups=sprite_groups.get_group("powerups"),
            effects=sprite_groups.get_group("effects")
        )
        
        # Reset timers
        self.powerup_spawn_timer.reset()
        self.auto_save_timer.reset()
        
        # Play game start sound
        sound_manager.play_ui_sound("confirm")
        
    def advance_to_next_level(self):
        if self.level_manager.advance_to_next_level():
            self.game_state.level = self.level_manager.current_level
            self.game_state.change_state(GameState.PLAYING)
            
            # Reset player position and clear some power-ups
            if self.player:
                self.player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
                
            # Play level start sound
            sound_manager.play_ui_sound("confirm")
        else:
            # Game completed
            self.game_state.game_over_state()
            
    def update(self):
        if not self.running:
            return
            
        # Update game state
        self.game_state.update()
        
        # Update based on current state
        if self.game_state.state == GameState.PLAYING and not self.game_state.paused:
            self.update_gameplay()
        elif self.game_state.state == GameState.MENU:
            self.update_menu()
        elif self.game_state.state == GameState.GAME_OVER:
            self.update_game_over()
            
        # Update effects and sound
        effect_manager.update()
        
        # Auto-save
        if self.auto_save_timer.update():
            self.game_state.save_all_data()
            self.auto_save_timer.reset()
            
    def update_gameplay(self):
        # Update level manager
        self.level_manager.update(self.player)
        
        # Update all sprites
        sprite_groups.update_all()
        
        # Update player weapon system
        if self.player:
            keys = pygame.key.get_pressed()
            if keys[CONTROLS["shoot"]]:
                bullets = self.player.shoot()
                for bullet in bullets:
                    sprite_groups.add_sprite(bullet, ["all", "bullets"])
                    
                # Track shots fired
                if bullets:
                    self.game_state.shot_fired()
                    
        # Update enemy shooting
        enemies = sprite_groups.get_group("enemies")
        for enemy in enemies:
            if hasattr(enemy, 'update_shooting'):
                enemy_bullets = enemy.update_shooting()
                for bullet in enemy_bullets:
                    sprite_groups.add_sprite(bullet, ["all", "enemy_bullets"])
                    
        # Update boss shooting
        bosses = sprite_groups.get_group("bosses")
        for boss in bosses:
            if hasattr(boss, 'update_shooting'):
                boss_bullets = boss.update_shooting()
                for bullet in boss_bullets:
                    sprite_groups.add_sprite(bullet, ["all", "enemy_bullets"])
                    
        # Spawn power-ups
        if self.powerup_spawn_timer.update():
            if self.level_manager.can_spawn_powerup():
                self.spawn_powerup()
            self.powerup_spawn_timer.reset()
            
        # Check collisions
        collision_results = self.collision_manager.check_all_collisions(self.player)
        
        # Process collision results
        self.process_collision_results(collision_results)
        
        # Update background scroll
        self.background_scroll_y += self.background_speed
        if self.background_scroll_y >= SCREEN_HEIGHT:
            self.background_scroll_y = 0
            
        # Check level completion
        if self.level_manager.is_level_complete():
            self.complete_level()
            
        # Check game over conditions
        if self.player and self.player.lives <= 0:
            self.game_state.game_over_state()
            
    def update_menu(self):
        # Update menu animations/effects
        pass
        
    def update_game_over(self):
        # Update game over screen
        pass
        
    def process_collision_results(self, results):
        # Process enemy kills
        for enemy in results['enemies_killed']:
            self.game_state.enemy_killed(enemy.score_value)
            self.level_manager.enemy_killed(enemy)
            
        # Process boss kills
        for boss in results['bosses_killed']:
            self.game_state.boss_defeated(boss.get_score_value())
            self.level_manager.boss_killed(boss)
            
        # Process power-up collection
        for powerup in results['powerups_collected']:
            self.game_state.powerup_collected(SCORE_VALUES["powerup"])
            self.level_manager.powerup_collected(powerup)
            
        # Process player damage
        if results['player_damaged']:
            self.game_state.life_lost()
            
        # Add effects
        for effect in results['effects_to_add']:
            sprite_groups.add_sprite(effect, ["all", "effects"])
            
        # Track shot hits
        if results['enemies_killed'] or results['bosses_killed']:
            self.game_state.shot_hit()
            
    def spawn_powerup(self):
        # Determine powerup type
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
        
        # Create powerup
        powerup = PowerUp(powerup_type)
        sprite_groups.add_sprite(powerup, ["all", "powerups"])
        
    def complete_level(self):
        level_stats = self.level_manager.get_level_stats()
        level_summary = self.level_manager.get_level_summary()
        
        # Update game state
        self.game_state.level_complete(level_stats["level_score"], level_summary)
        
        # Change to level complete state
        self.game_state.change_state(GameState.LEVEL_COMPLETE)
        
        # Play level complete sound
        sound_manager.play_player_sound("level_up")
        
        # Screen shake for completion
        self.ui_manager.screen_shake(10, 500)
        
    def render(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        # Render based on current state
        if self.game_state.state == GameState.PLAYING:
            self.render_gameplay()
        elif self.game_state.state == GameState.MENU:
            self.render_menu()
        elif self.game_state.state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.game_state.state == GameState.PAUSED:
            self.render_gameplay()
            self.render_pause_overlay()
        elif self.game_state.state == GameState.LEVEL_COMPLETE:
            self.render_level_complete()
        elif self.game_state.state == GameState.SETTINGS:
            self.render_settings()
        elif self.game_state.state == GameState.ACHIEVEMENTS:
            self.render_achievements()
            
        # Apply screen shake
        shake_offset = effect_manager.update()
        if shake_offset != (0, 0):
            # Create a temporary surface for shake effect
            temp_surface = self.screen.copy()
            self.screen.fill(BLACK)
            self.screen.blit(temp_surface, shake_offset)
            
        pygame.display.flip()
        
    def render_gameplay(self):
        # Get current theme background
        background = asset_manager.get_background(self.level_manager.theme.name.lower())
        if background:
            # Scrolling background
            self.screen.blit(background, (0, self.background_scroll_y - SCREEN_HEIGHT))
            self.screen.blit(background, (0, self.background_scroll_y))
        
        # Draw all sprites
        sprite_groups.draw_all(self.screen)
        
        # Draw custom sprite effects
        if self.player:
            self.player.draw(self.screen)
            
        # Draw UI elements
        if self.player:
            self.ui_manager.draw_hud(self.screen, self.player, 
                                   self.level_manager.current_level, 
                                   self.game_state.score)
            
        # Draw boss UI if active
        if self.level_manager.is_boss_active():
            bosses = sprite_groups.get_group("bosses")
            if bosses:
                boss = list(bosses)[0]
                self.ui_manager.draw_boss_hud(self.screen, boss)
                
        # Draw level progress
        progress = self.level_manager.get_level_progress()
        if progress < 1.0:
            bar_width = 200
            bar_height = 10
            bar_x = SCREEN_WIDTH - bar_width - 20
            bar_y = 100
            
            # Background
            pygame.draw.rect(self.screen, GREY, (bar_x, bar_y, bar_width, bar_height))
            
            # Progress fill
            fill_width = int(bar_width * progress)
            pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, fill_width, bar_height))
            
            # Border
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Label
            self.ui_manager.draw_text(self.screen, f"Progress: {int(progress * 100)}%", 
                                    "small", bar_x + bar_width // 2, bar_y - 15, WHITE)
                                    
        # Draw FPS counter if enabled
        if self.game_state.get_setting("show_fps"):
            self.ui_manager.draw_fps_counter(self.screen, self.clock)
            
    def render_menu(self):
        options = self.get_menu_options()
        self.ui_manager.draw_menu(self.screen, "SHOOTAR", options, 
                                self.ui_manager.menu_selection)
        
        # Draw additional menu info
        self.ui_manager.draw_text(self.screen, f"High Score: {self.game_state.high_score}", 
                                "medium", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, GOLD)
        self.ui_manager.draw_text(self.screen, f"Level: {self.game_state.stats['highest_level']}", 
                                "medium", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120, WHITE)
                                
    def render_game_over(self):
        high_scores = self.game_state.get_high_scores()
        high_score = high_scores[0] if high_scores else 0
        
        self.ui_manager.draw_game_over_screen(self.screen, self.game_state.score, high_score)
        
        # Draw statistics
        stats = self.game_state.get_statistics_summary()
        y_offset = 550
        
        stats_to_show = [
            f"Enemies Killed: {stats['enemies_killed']}",
            f"Bosses Defeated: {stats['bosses_defeated']}",
            f"Level Reached: {stats['highest_level']}",
            f"Accuracy: {stats['accuracy']}",
            f"Time Played: {self.game_state.get_current_session_time()}"
        ]
        
        for stat in stats_to_show:
            self.ui_manager.draw_text(self.screen, stat, "small", 
                                    SCREEN_WIDTH // 2, y_offset, WHITE)
            y_offset += 25
            
    def render_pause_overlay(self):
        self.ui_manager.draw_pause_screen(self.screen)
        
    def render_level_complete(self):
        level_summary = self.level_manager.get_level_summary()
        
        self.ui_manager.draw_level_complete_screen(
            self.screen, 
            self.level_manager.current_level, 
            self.game_state.score,
            level_summary.get("score", 0)
        )
        
        # Draw level statistics
        y_offset = 400
        stats_to_show = [
            f"Enemies Killed: {level_summary['enemies_killed']}",
            f"Damage Taken: {level_summary['damage_taken']}",
            f"Power-ups Collected: {level_summary['powerups_collected']}",
            f"Time: {level_summary['duration']:.1f}s",
            f"Difficulty: {level_summary['difficulty']}"
        ]
        
        for stat in stats_to_show:
            self.ui_manager.draw_text(self.screen, stat, "small", 
                                    SCREEN_WIDTH // 2, y_offset, WHITE)
            y_offset += 25
            
        if level_summary.get("perfect_level", False):
            self.ui_manager.draw_text(self.screen, "PERFECT LEVEL!", 
                                    "large", SCREEN_WIDTH // 2, y_offset + 20, GOLD)
                                    
    def render_settings(self):
        settings = {
            "Music Volume": f"{int(self.game_state.settings['music_volume'] * 100)}%",
            "SFX Volume": f"{int(self.game_state.settings['sfx_volume'] * 100)}%",
            "Music": "ON" if self.game_state.settings['music_enabled'] else "OFF",
            "SFX": "ON" if self.game_state.settings['sfx_enabled'] else "OFF",
            "Show FPS": "ON" if self.game_state.settings['show_fps'] else "OFF",
            "Difficulty": self.game_state.settings['difficulty'].upper()
        }
        
        self.ui_manager.draw_settings_screen(self.screen, settings)
        
    def render_achievements(self):
        achievements = list(self.game_state.achievements.values())
        self.ui_manager.draw_achievements_screen(self.screen, achievements)
        
    def cleanup(self):
        # Save game data
        self.game_state.save_all_data()
        
        # Cleanup sound
        sound_manager.cleanup()
        
        # Quit pygame
        pygame.quit()
        sys.exit()
        
    def get_frame_rate(self) -> int:
        return int(self.clock.get_fps())
        
    def get_game_time(self) -> float:
        return pygame.time.get_ticks() / 1000.0
        
    def toggle_fullscreen(self):
        if self.game_state.settings['fullscreen']:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.game_state.settings['fullscreen'] = False
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            self.game_state.settings['fullscreen'] = True
            
        self.game_state.save_settings()
        
    def screenshot(self, filename: str = None):
        if filename is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved as {filename}")
        
    def debug_info(self) -> Dict[str, Any]:
        return {
            "fps": self.get_frame_rate(),
            "game_time": self.get_game_time(),
            "game_state": self.game_state.state.name,
            "level": self.level_manager.current_level,
            "score": self.game_state.score,
            "lives": self.game_state.lives,
            "sprites": {
                "all": sprite_groups.get_sprite_count("all"),
                "enemies": sprite_groups.get_sprite_count("enemies"),
                "bullets": sprite_groups.get_sprite_count("bullets"),
                "enemy_bullets": sprite_groups.get_sprite_count("enemy_bullets"),
                "powerups": sprite_groups.get_sprite_count("powerups"),
                "effects": sprite_groups.get_sprite_count("effects")
            },
            "level_progress": self.level_manager.get_level_progress(),
            "boss_active": self.level_manager.is_boss_active(),
            "paused": self.game_state.paused
        }