import pygame
import os
from typing import Dict, Optional, List
from config import MUSIC_VOLUME, SFX_VOLUME, ASSET_PATHS
from asset_manager import asset_manager

class SoundManager:
    def __init__(self):
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.music_enabled = True
        self.sfx_enabled = True
        self.current_music = None
        self.sound_channels: Dict[str, pygame.mixer.Channel] = {}
        
        # Initialize mixer if not already done
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"Warning: Could not initialize mixer in sound manager: {e}")
            self.sfx_enabled = False
            self.music_enabled = False
        
        # Reserve channels for different types of sounds
        try:
            pygame.mixer.set_num_channels(16)
            self.ui_channel = pygame.mixer.Channel(0)
            self.player_channel = pygame.mixer.Channel(1)
            self.enemy_channel = pygame.mixer.Channel(2)
            self.explosion_channel = pygame.mixer.Channel(3)
            self.powerup_channel = pygame.mixer.Channel(4)
            self.ambient_channel = pygame.mixer.Channel(5)
        except Exception as e:
            print(f"Warning: Could not create sound channels: {e}")
            # Create dummy channels that do nothing
            self.ui_channel = None
            self.player_channel = None
            self.enemy_channel = None
            self.explosion_channel = None
            self.powerup_channel = None
            self.ambient_channel = None
    
    def play_sound(self, sound_name: str, volume: Optional[float] = None, channel: Optional[str] = None):
        if not self.sfx_enabled:
            return
        
        sound = asset_manager.get_sound(sound_name)
        if sound:
            if volume is None:
                volume = self.sfx_volume
            else:
                volume = min(1.0, volume * self.sfx_volume)
            
            sound.set_volume(volume)
            
            if channel:
                self.play_on_channel(sound, channel)
            else:
                sound.play()
    
    def play_on_channel(self, sound: pygame.mixer.Sound, channel_name: str):
        channel_map = {
            "ui": self.ui_channel,
            "player": self.player_channel,
            "enemy": self.enemy_channel,
            "explosion": self.explosion_channel,
            "powerup": self.powerup_channel,
            "ambient": self.ambient_channel
        }
        
        channel = channel_map.get(channel_name)
        if channel:
            channel.play(sound)
    
    def play_music(self, music_name: str, loops: int = -1, fade_in: float = 0):
        if not self.music_enabled:
            return
        
        music_path = ASSET_PATHS.get(music_name, music_name)
        
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                
                if fade_in > 0:
                    pygame.mixer.music.play(loops, fade_ms=int(fade_in * 1000))
                else:
                    pygame.mixer.music.play(loops)
                
                self.current_music = music_name
            except Exception as e:
                print(f"Error playing music {music_name}: {e}")
    
    def stop_music(self, fade_out: float = 0):
        if fade_out > 0:
            pygame.mixer.music.fadeout(int(fade_out * 1000))
        else:
            pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self):
        pygame.mixer.music.pause()
    
    def resume_music(self):
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        elif self.current_music:
            self.play_music(self.current_music)
    
    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
        if not self.sfx_enabled:
            self.stop_all_sounds()
    
    def stop_all_sounds(self):
        pygame.mixer.stop()
    
    def stop_channel(self, channel_name: str):
        channel_map = {
            "ui": self.ui_channel,
            "player": self.player_channel,
            "enemy": self.enemy_channel,
            "explosion": self.explosion_channel,
            "powerup": self.powerup_channel,
            "ambient": self.ambient_channel
        }
        
        channel = channel_map.get(channel_name)
        if channel:
            channel.stop()
    
    def is_music_playing(self) -> bool:
        return pygame.mixer.music.get_busy()
    
    def is_channel_busy(self, channel_name: str) -> bool:
        channel_map = {
            "ui": self.ui_channel,
            "player": self.player_channel,
            "enemy": self.enemy_channel,
            "explosion": self.explosion_channel,
            "powerup": self.powerup_channel,
            "ambient": self.ambient_channel
        }
        
        channel = channel_map.get(channel_name)
        return channel.get_busy() if channel else False
    
    def play_shoot_sound(self, weapon_type: str = "basic"):
        sound_variations = {
            "basic": "shoot",
            "laser": "shoot",
            "rapid": "shoot",
            "spread": "shoot"
        }
        
        sound_name = sound_variations.get(weapon_type, "shoot")
        self.play_sound(sound_name, channel="player")
    
    def play_explosion_sound(self, size: str = "normal"):
        volume_variations = {
            "small": 0.5,
            "normal": 0.8,
            "large": 1.0,
            "boss": 1.0
        }
        
        volume = volume_variations.get(size, 0.8)
        self.play_sound("explosion", volume=volume, channel="explosion")
    
    def play_powerup_sound(self, powerup_type: str):
        sound_variations = {
            "shield": "powerup_sound",
            "gun_upgrade": "powerup_sound",
            "ultrakill": "ultrakill",
            "health": "powerup_sound",
            "life": "powerup_sound",
            "speed": "powerup_sound",
            "rapid_fire": "powerup_sound"
        }
        
        sound_name = sound_variations.get(powerup_type, "powerup_sound")
        self.play_sound(sound_name, channel="powerup")
    
    def play_ui_sound(self, ui_action: str):
        # For UI sounds, we'll use the basic sounds for now
        ui_sounds = {
            "select": "shoot",
            "confirm": "powerup_sound",
            "back": "explosion",
            "error": "explosion"
        }
        
        sound_name = ui_sounds.get(ui_action, "shoot")
        self.play_sound(sound_name, volume=0.3, channel="ui")
    
    def play_ambient_sound(self, ambient_type: str):
        # Ambient sounds for different level themes
        ambient_sounds = {
            "space": "background_music",
            "nebula": "background_music",
            "asteroid": "background_music",
            "cyber": "background_music",
            "solar": "background_music"
        }
        
        sound_name = ambient_sounds.get(ambient_type, "background_music")
        self.play_sound(sound_name, volume=0.2, channel="ambient")
    
    def play_enemy_sound(self, enemy_type: str, action: str):
        # Different sounds for different enemy types and actions
        if action == "shoot":
            self.play_sound("shoot", volume=0.6, channel="enemy")
        elif action == "death":
            self.play_explosion_sound("small")
        elif action == "spawn":
            self.play_sound("powerup_sound", volume=0.4, channel="enemy")
    
    def play_boss_sound(self, action: str):
        if action == "spawn":
            self.play_sound("explosion", volume=0.8, channel="enemy")
        elif action == "shoot":
            self.play_sound("shoot", volume=0.9, channel="enemy")
        elif action == "death":
            self.play_explosion_sound("boss")
        elif action == "hit":
            self.play_sound("explosion", volume=0.6, channel="enemy")
    
    def play_player_sound(self, action: str):
        if action == "hit":
            self.play_sound("explosion", volume=0.7, channel="player")
        elif action == "death":
            self.play_explosion_sound("large")
        elif action == "level_up":
            self.play_sound("powerup_sound", volume=0.8, channel="player")
    
    def create_sound_sequence(self, sounds: List[tuple], delay: float = 0.1):
        # For playing multiple sounds in sequence
        # sounds: List of (sound_name, volume, channel) tuples
        current_time = pygame.time.get_ticks()
        
        for i, (sound_name, volume, channel) in enumerate(sounds):
            # Schedule sound to play after delay
            def play_delayed_sound():
                self.play_sound(sound_name, volume, channel)
            
            # For simplicity, we'll just play them immediately
            # In a real implementation, you'd use pygame.time.set_timer
            play_delayed_sound()
    
    def get_music_position(self) -> float:
        return pygame.mixer.music.get_pos() / 1000.0 if self.is_music_playing() else 0.0
    
    def fade_music(self, target_volume: float, duration: float):
        # Simple fade implementation
        current_volume = self.music_volume
        steps = int(duration * 60)  # Assuming 60 FPS
        volume_step = (target_volume - current_volume) / steps
        
        # In a real implementation, you'd use a timer or coroutine
        # For now, just set the target volume
        self.set_music_volume(target_volume)
    
    def save_settings(self) -> dict:
        return {
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "music_enabled": self.music_enabled,
            "sfx_enabled": self.sfx_enabled
        }
    
    def load_settings(self, settings: dict):
        self.music_volume = settings.get("music_volume", MUSIC_VOLUME)
        self.sfx_volume = settings.get("sfx_volume", SFX_VOLUME)
        self.music_enabled = settings.get("music_enabled", True)
        self.sfx_enabled = settings.get("sfx_enabled", True)
        
        self.set_music_volume(self.music_volume)
    
    def cleanup(self):
        self.stop_all_sounds()
        self.stop_music()
        pygame.mixer.quit()

# Global sound manager instance
sound_manager = SoundManager()