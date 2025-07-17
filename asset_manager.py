import pygame
import os
import math
from typing import Dict, Optional, Tuple
from config import ASSET_PATHS, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, CYAN

class AssetManager:
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.backgrounds: Dict[str, pygame.Surface] = {}
        self.loaded = False
    
    def load_all_assets(self):
        if self.loaded:
            return
        
        self.load_images()
        self.load_sounds()
        self.load_fonts()
        self.create_procedural_assets()
        self.loaded = True
    
    def load_images(self):
        for name, path in ASSET_PATHS.items():
            if path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.load_image(name, path)
    
    def load_image(self, name: str, path: str, scale: Optional[Tuple[int, int]] = None) -> bool:
        try:
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                if scale:
                    image = pygame.transform.scale(image, scale)
                self.images[name] = image
                return True
            else:
                self.create_placeholder_image(name)
                return False
        except Exception as e:
            print(f"Error loading image {name}: {e}")
            self.create_placeholder_image(name)
            return False
    
    def create_placeholder_image(self, name: str):
        if name == "player":
            self.images[name] = self.create_ship_image(50, 40, GREEN)
        elif name == "bullet":
            self.images[name] = self.create_bullet_image(5, 10, YELLOW)
        elif name == "enemy":
            self.images[name] = self.create_ship_image(30, 30, RED)
        elif name == "enemy2":
            self.images[name] = self.create_ship_image(35, 35, ORANGE)
        elif name == "boss":
            self.images[name] = self.create_ship_image(100, 80, PURPLE)
        elif name == "powerup":
            self.images[name] = self.create_powerup_image(20, 20, BLUE)
        elif name == "background":
            self.images[name] = self.create_background_image()
        else:
            self.images[name] = self.create_generic_placeholder(32, 32)
    
    def create_ship_image(self, width: int, height: int, color: Tuple[int, int, int]) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw ship body
        pygame.draw.polygon(surface, color, [
            (width // 2, 0),
            (width - 5, height - 10),
            (width // 2, height - 5),
            (5, height - 10)
        ])
        
        # Draw engine glow
        engine_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        pygame.draw.circle(surface, engine_color, (width // 2, height - 3), 3)
        
        return surface
    
    def create_bullet_image(self, width: int, height: int, color: Tuple[int, int, int]) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, color, (0, 0, width, height))
        return surface
    
    def create_powerup_image(self, width: int, height: int, color: Tuple[int, int, int]) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (width // 2, height // 2), width // 2)
        pygame.draw.circle(surface, WHITE, (width // 2, height // 2), width // 2, 2)
        return surface
    
    def create_background_image(self) -> pygame.Surface:
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill(BLACK)
        
        # Add stars
        for _ in range(100):
            import random
            star_x = random.randint(0, SCREEN_WIDTH)
            star_y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(surface, WHITE, (star_x, star_y), 1)
        
        return surface
    
    def create_generic_placeholder(self, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, WHITE, (0, 0, width, height), 2)
        return surface
    
    def load_sounds(self):
        for name, path in ASSET_PATHS.items():
            if path.endswith(('.wav', '.mp3', '.ogg')):
                self.load_sound(name, path)
    
    def load_sound(self, name: str, path: str) -> bool:
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
                return True
            else:
                self.create_placeholder_sound(name)
                return False
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            self.create_placeholder_sound(name)
            return False
    
    def create_placeholder_sound(self, name: str):
        # Create a simple beep sound
        sample_rate = 22050
        duration = 0.1
        frames = int(duration * sample_rate)
        
        arr = []
        for i in range(frames):
            time = float(i) / sample_rate
            wave = 4096 * math.sin(2 * math.pi * 440 * time)
            arr.append([int(wave), int(wave)])
        
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        self.sounds[name] = sound
    
    def load_fonts(self):
        font_sizes = [12, 16, 18, 24, 32, 48, 64]
        for size in font_sizes:
            try:
                font = pygame.font.Font(None, size)
                self.fonts[f"default_{size}"] = font
            except:
                pass
        
        # Try to load Arial font
        try:
            arial_font = pygame.font.match_font('arial')
            for size in font_sizes:
                font = pygame.font.Font(arial_font, size)
                self.fonts[f"arial_{size}"] = font
        except:
            pass
    
    def create_procedural_assets(self):
        # Create shield effect
        shield_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(shield_surface, (0, 100, 255, 100), (30, 30), 30)
        self.images["shield"] = shield_surface
        
        # Create enemy bullet
        enemy_bullet_surface = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.rect(enemy_bullet_surface, RED, (0, 0, 5, 10))
        self.images["enemy_bullet"] = enemy_bullet_surface
        
        # Create different background variations
        self.create_background_variations()
        
        # Create powerup variations
        self.create_powerup_variations()
    
    def create_background_variations(self):
        themes = {
            "space": (BLACK, WHITE),
            "nebula": (PURPLE, CYAN),
            "asteroid": ((50, 50, 50), (150, 150, 150)),
            "cyber": ((0, 50, 0), GREEN),
            "solar": (ORANGE, YELLOW)
        }
        
        for theme_name, (bg_color, star_color) in themes.items():
            surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.fill(bg_color)
            
            # Add themed stars/particles
            for _ in range(80):
                import random
                star_x = random.randint(0, SCREEN_WIDTH)
                star_y = random.randint(0, SCREEN_HEIGHT)
                size = pygame.math.Vector2(1, 3).length()
                pygame.draw.circle(surface, star_color, (star_x, star_y), int(size))
            
            self.backgrounds[theme_name] = surface
    
    def create_powerup_variations(self):
        powerup_colors = {
            "shield": BLUE,
            "gun_upgrade": GREEN,
            "ultrakill": RED,
            "health": (0, 255, 0),
            "life": YELLOW,
            "speed": CYAN,
            "rapid_fire": ORANGE
        }
        
        for powerup_type, color in powerup_colors.items():
            surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (10, 10), 10)
            pygame.draw.circle(surface, WHITE, (10, 10), 10, 2)
            
            # Add type-specific symbol
            if powerup_type == "shield":
                pygame.draw.circle(surface, WHITE, (10, 10), 6, 2)
            elif powerup_type == "gun_upgrade":
                pygame.draw.rect(surface, WHITE, (8, 6, 4, 8))
            elif powerup_type == "ultrakill":
                pygame.draw.polygon(surface, WHITE, [(10, 5), (15, 15), (5, 15)])
            elif powerup_type == "health":
                pygame.draw.rect(surface, WHITE, (8, 10, 4, 6))
                pygame.draw.rect(surface, WHITE, (6, 8, 8, 4))
            elif powerup_type == "life":
                pygame.draw.polygon(surface, WHITE, [(10, 6), (13, 10), (10, 14), (7, 10)])
            elif powerup_type == "speed":
                pygame.draw.polygon(surface, WHITE, [(6, 10), (10, 6), (14, 10), (10, 14)])
            elif powerup_type == "rapid_fire":
                for i in range(3):
                    pygame.draw.circle(surface, WHITE, (6 + i * 4, 10), 1)
            
            self.images[f"powerup_{powerup_type}"] = surface
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        return self.images.get(name)
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        return self.sounds.get(name)
    
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        return self.fonts.get(name)
    
    def get_background(self, name: str) -> Optional[pygame.Surface]:
        return self.backgrounds.get(name, self.backgrounds.get("space"))
    
    def reload_image(self, name: str, path: str, scale: Optional[Tuple[int, int]] = None):
        self.load_image(name, path, scale)
    
    def create_scaled_image(self, name: str, scale: Tuple[int, int]) -> Optional[pygame.Surface]:
        if name in self.images:
            return pygame.transform.scale(self.images[name], scale)
        return None
    
    def create_rotated_image(self, name: str, angle: float) -> Optional[pygame.Surface]:
        if name in self.images:
            return pygame.transform.rotate(self.images[name], angle)
        return None
    
    def create_tinted_image(self, name: str, color: Tuple[int, int, int]) -> Optional[pygame.Surface]:
        if name in self.images:
            tinted = self.images[name].copy()
            tinted.fill(color, special_flags=pygame.BLEND_MULT)
            return tinted
        return None
    
    def get_image_size(self, name: str) -> Tuple[int, int]:
        if name in self.images:
            return self.images[name].get_size()
        return (0, 0)
    
    def preload_scaled_images(self):
        # Preload commonly used scaled versions
        if "player" in self.images:
            self.images["player_small"] = pygame.transform.scale(self.images["player"], (25, 20))
            self.images["player_large"] = pygame.transform.scale(self.images["player"], (75, 60))
        
        if "enemy" in self.images:
            self.images["enemy_small"] = pygame.transform.scale(self.images["enemy"], (20, 20))
            self.images["enemy_large"] = pygame.transform.scale(self.images["enemy"], (40, 40))

# Global asset manager instance
asset_manager = AssetManager()