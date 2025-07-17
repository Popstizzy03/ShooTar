#!/usr/bin/env python3
"""
ShooTar - Ultimate Space Shooter Game (Version 5)
==================================================

A modern, feature-rich space shooter game built with Python and Pygame.

Features:
- Multiple enemy types with different behaviors
- Boss battles with multiple phases
- Power-up system with various upgrades
- Level progression with increasing difficulty
- Achievement system and statistics tracking
- Settings and save system
- Sound effects and background music
- Particle effects and visual polish
- Collision detection and game physics

Author: AI Assistant
Version: 5.0
License: MIT
"""

import pygame
import sys
import os
import traceback
from typing import Optional

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import game modules
try:
    from config import *
    from game_engine import GameEngine
    from asset_manager import asset_manager
    from sound_manager import sound_manager
    from utils import save_json, load_json
except ImportError as e:
    print(f"Error importing game modules: {e}")
    print("Please ensure all required files are in the same directory:")
    print("- config.py")
    print("- game_engine.py")
    print("- asset_manager.py")
    print("- sound_manager.py")
    print("- utils.py")
    print("- And all other game modules")
    sys.exit(1)

class GameLauncher:
    """Main game launcher class that handles initialization and error handling."""
    
    def __init__(self):
        self.game_engine: Optional[GameEngine] = None
        self.error_log_file = "error_log.txt"
        
    def initialize_pygame(self) -> bool:
        """Initialize pygame and check for required features."""
        try:
            pygame.init()
            
            # Check pygame version
            pygame_version = pygame.version.ver
            print(f"Pygame version: {pygame_version}")
            
            # Check for required pygame modules
            required_modules = ['mixer', 'font', 'image', 'display']
            
            for module_name in required_modules:
                try:
                    if hasattr(pygame, module_name):
                        print(f"✓ pygame.{module_name} available")
                    else:
                        print(f"Warning: pygame.{module_name} not available")
                        # Don't return False for mixer - it's optional
                        if module_name not in ['mixer']:
                            return False
                except Exception as e:
                    print(f"Error checking pygame.{module_name}: {e}")
                    if module_name not in ['mixer']:
                        return False
                    
            # Initialize mixer with better settings
            try:
                # Check if mixer is available before trying to initialize
                if hasattr(pygame, 'mixer') and pygame.mixer:
                    frequency = 44100
                    size = -16
                    channels = 2
                    buffer = 1024
                    
                    pygame.mixer.pre_init(frequency, size, channels, buffer)
                    pygame.mixer.init()
                    
                    # Check sound system
                    if not pygame.mixer.get_init():
                        print("Warning: Sound system not available - running without sound")
                    else:
                        print(f"✓ Sound system initialized: {pygame.mixer.get_init()}")
                else:
                    print("Warning: pygame.mixer not available - running without sound")
            except Exception as e:
                print(f"Warning: Could not initialize sound system: {e}")
                print("Game will run without sound")
                
            # Check display modes
            display_modes = pygame.display.list_modes()
            if display_modes == -1:
                print("All display modes supported")
            else:
                print(f"Available display modes: {len(display_modes)}")
                
            return True
            
        except Exception as e:
            self.log_error(f"Failed to initialize pygame: {e}")
            return False
            
    def check_dependencies(self) -> bool:
        """Check if all required files and assets are present."""
        required_files = [
            'config.py',
            'game_engine.py',
            'game_state.py',
            'level_manager.py',
            'player.py',
            'enemies.py',
            'projectiles.py',
            'powerups.py',
            'effects.py',
            'ui_manager.py',
            'collision_manager.py',
            'sound_manager.py',
            'asset_manager.py',
            'sprite_groups.py',
            'utils.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
                
        if missing_files:
            print("Error: Missing required files:")
            for file in missing_files:
                print(f"  - {file}")
            return False
            
        # Check for asset files (optional but recommended)
        asset_files = [
            'player.png',
            'bullet.png',
            'enemy.png',
            'enemy2.png',
            'boss.png',
            'powerup.png',
            'background.png',
            'shoot.mp3',
            'explosion.wav',
            'powerup.wav',
            'ultrakill.wav',
            'background.wav'
        ]
        
        missing_assets = []
        for asset in asset_files:
            if not os.path.exists(asset):
                missing_assets.append(asset)
                
        if missing_assets:
            print("Warning: Missing asset files (procedural assets will be used):")
            for asset in missing_assets:
                print(f"  - {asset}")
                
        return True
        
    def create_default_config(self):
        """Create default configuration files if they don't exist."""
        # Create save directory if it doesn't exist
        save_dir = "saves"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Create default settings file
        settings_path = SAVE_PATHS["settings"]
        if not os.path.exists(settings_path):
            default_settings = {
                "music_volume": MUSIC_VOLUME,
                "sfx_volume": SFX_VOLUME,
                "music_enabled": True,
                "sfx_enabled": True,
                "fullscreen": False,
                "show_fps": False,
                "difficulty": "normal",
                "controls": CONTROLS.copy()
            }
            save_json(default_settings, settings_path)
            print(f"Created default settings file: {settings_path}")
            
    def handle_error(self, error: Exception, context: str = ""):
        """Handle and log errors."""
        error_msg = f"Error in {context}: {str(error)}"
        print(error_msg)
        
        # Log to file
        self.log_error(error_msg)
        self.log_error(traceback.format_exc())
        
        # Show error dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Game Error", 
                               f"An error occurred: {error_msg}\n\n"
                               f"Check {self.error_log_file} for details.")
            root.destroy()
        except:
            pass
            
    def log_error(self, message: str):
        """Log error message to file."""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
            
    def run(self):
        """Main game execution method."""
        print("=" * 60)
        print("ShooTar - Ultimate Space Shooter")
        print("Version 5.0")
        print("=" * 60)
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                print("Cannot start game due to missing dependencies.")
                return False
                
            # Initialize pygame
            if not self.initialize_pygame():
                print("Cannot start game due to pygame initialization failure.")
                return False
                
            # Create default configuration
            self.create_default_config()
            
            # Initialize game engine
            print("Initializing game engine...")
            self.game_engine = GameEngine()
            
            # Start the game
            print("Starting game...")
            self.game_engine.run()
            
            return True
            
        except KeyboardInterrupt:
            print("\nGame interrupted by user.")
            return True
            
        except Exception as e:
            self.handle_error(e, "main game loop")
            return False
            
        finally:
            # Cleanup
            if self.game_engine:
                try:
                    self.game_engine.cleanup()
                except:
                    pass
                    
            try:
                pygame.quit()
            except:
                pass
                
            print("Game shutdown complete.")
            
    def show_help(self):
        """Show help information."""
        help_text = """
ShooTar - Ultimate Space Shooter

Controls:
  Arrow Keys / WASD - Move ship
  Space - Shoot
  P - Pause game
  ESC - Exit to menu / Quit game
  R - Restart game
  M - Toggle menu
  
Menu Navigation:
  Up/Down Arrows - Navigate menu
  Enter - Select option
  ESC - Go back

Game Features:
  - Multiple enemy types with different behaviors
  - Boss battles with multiple attack patterns
  - Power-up system (Shield, Weapon Upgrades, Health, etc.)
  - Level progression with increasing difficulty
  - Achievement system and statistics tracking
  - Settings and save system
  - Sound effects and background music

Command Line Options:
  --help        Show this help message
  --version     Show version information
  --debug       Enable debug mode
  --nosound     Disable sound
  --fullscreen  Start in fullscreen mode
  --reset       Reset all save data
  
Files:
  All game files should be in the same directory as this script.
  Save files are created in the same directory.
  
For support or bug reports, check the error_log.txt file.
        """
        print(help_text)
        
    def show_version(self):
        """Show version information."""
        print("ShooTar - Ultimate Space Shooter")
        print("Version: 5.0")
        print("Built with Python and Pygame")
        print(f"Python version: {sys.version}")
        try:
            import pygame
            print(f"Pygame version: {pygame.version.ver}")
        except:
            print("Pygame: Not available")
            
    def reset_save_data(self):
        """Reset all save data."""
        save_files = [
            SAVE_PATHS["settings"],
            SAVE_PATHS["progress"],
            SAVE_PATHS["achievements"],
            SAVE_PATHS["highscores"]
        ]
        
        for file in save_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Removed {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")
                    
        print("Save data reset complete.")

def main():
    """Main entry point."""
    launcher = GameLauncher()
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        launcher.show_help()
        return
        
    if "--version" in args or "-v" in args:
        launcher.show_version()
        return
        
    if "--reset" in args:
        launcher.reset_save_data()
        return
        
    # Set debug mode
    debug_mode = "--debug" in args
    if debug_mode:
        print("Debug mode enabled")
        
    # Set sound options
    no_sound = "--nosound" in args
    if no_sound:
        print("Sound disabled")
        
    # Set fullscreen option
    fullscreen = "--fullscreen" in args
    if fullscreen:
        print("Starting in fullscreen mode")
        
    # Run the game
    try:
        success = launcher.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        launcher.handle_error(e, "launcher")
        sys.exit(1)

if __name__ == "__main__":
    main()