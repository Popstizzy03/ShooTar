import pygame
import math
import random
import json
import os
from typing import Tuple, List, Optional, Dict, Any
from config import *

def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))

def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t

def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
    if magnitude == 0:
        return (0, 0)
    return (vector[0] / magnitude, vector[1] / magnitude)

def angle_between_points(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    return math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])

def rotate_point(point: Tuple[float, float], angle: float, origin: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    
    translated_x = point[0] - origin[0]
    translated_y = point[1] - origin[1]
    
    rotated_x = translated_x * cos_angle - translated_y * sin_angle
    rotated_y = translated_x * sin_angle + translated_y * cos_angle
    
    return (rotated_x + origin[0], rotated_y + origin[1])

def point_in_circle(point: Tuple[float, float], center: Tuple[float, float], radius: float) -> bool:
    return distance(point, center) <= radius

def point_in_rect(point: Tuple[float, float], rect: pygame.Rect) -> bool:
    return rect.collidepoint(point)

def random_color() -> Tuple[int, int, int]:
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def random_position_in_rect(rect: pygame.Rect) -> Tuple[int, int]:
    return (random.randint(rect.left, rect.right), random.randint(rect.top, rect.bottom))

def random_position_offscreen(screen_width: int, screen_height: int, margin: int = 50) -> Tuple[int, int]:
    side = random.randint(0, 3)
    if side == 0:  # Top
        return (random.randint(0, screen_width), -margin)
    elif side == 1:  # Right
        return (screen_width + margin, random.randint(0, screen_height))
    elif side == 2:  # Bottom
        return (random.randint(0, screen_width), screen_height + margin)
    else:  # Left
        return (-margin, random.randint(0, screen_height))

def wrap_position(pos: Tuple[float, float], screen_width: int, screen_height: int) -> Tuple[float, float]:
    x, y = pos
    x = x % screen_width
    y = y % screen_height
    return (x, y)

def ease_in_out(t: float) -> float:
    if t < 0.5:
        return 2 * t * t
    else:
        return -1 + (4 - 2 * t) * t

def ease_in(t: float) -> float:
    return t * t

def ease_out(t: float) -> float:
    return 1 - (1 - t) * (1 - t)

def oscillate(time: float, amplitude: float, frequency: float, phase: float = 0) -> float:
    return amplitude * math.sin(frequency * time + phase)

def create_surface_with_alpha(width: int, height: int, color: Tuple[int, int, int], alpha: int) -> pygame.Surface:
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((*color, alpha))
    return surface

def scale_image(image: pygame.Surface, scale_factor: float) -> pygame.Surface:
    new_width = int(image.get_width() * scale_factor)
    new_height = int(image.get_height() * scale_factor)
    return pygame.transform.scale(image, (new_width, new_height))

def rotate_image(image: pygame.Surface, angle: float) -> pygame.Surface:
    return pygame.transform.rotate(image, math.degrees(angle))

def tint_image(image: pygame.Surface, color: Tuple[int, int, int]) -> pygame.Surface:
    tinted = image.copy()
    tinted.fill(color, special_flags=pygame.BLEND_MULT)
    return tinted

def create_gradient_surface(width: int, height: int, color1: Tuple[int, int, int], color2: Tuple[int, int, int], vertical: bool = True) -> pygame.Surface:
    surface = pygame.Surface((width, height))
    
    if vertical:
        for y in range(height):
            t = y / height
            color = (
                int(lerp(color1[0], color2[0], t)),
                int(lerp(color1[1], color2[1], t)),
                int(lerp(color1[2], color2[2], t))
            )
            pygame.draw.line(surface, color, (0, y), (width, y))
    else:
        for x in range(width):
            t = x / width
            color = (
                int(lerp(color1[0], color2[0], t)),
                int(lerp(color1[1], color2[1], t)),
                int(lerp(color1[2], color2[2], t))
            )
            pygame.draw.line(surface, color, (x, 0), (x, height))
    
    return surface

def save_json(data: Dict[str, Any], filename: str) -> bool:
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON to {filename}: {e}")
        return False

def load_json(filename: str) -> Optional[Dict[str, Any]]:
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {filename}: {e}")
    return None

def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_score(score: int) -> str:
    if score >= 1000000:
        return f"{score // 1000000}M"
    elif score >= 1000:
        return f"{score // 1000}K"
    else:
        return str(score)

def get_font_size_for_text(text: str, font: pygame.font.Font, max_width: int) -> int:
    size = font.get_height()
    while font.size(text)[0] > max_width and size > 10:
        size -= 1
        font = pygame.font.Font(font.get_fontname(), size)
    return size

def create_text_surface(text: str, font: pygame.font.Font, color: Tuple[int, int, int], background: Optional[Tuple[int, int, int]] = None) -> pygame.Surface:
    if background:
        return font.render(text, True, color, background)
    else:
        return font.render(text, True, color)

def create_outlined_text(text: str, font: pygame.font.Font, color: Tuple[int, int, int], outline_color: Tuple[int, int, int], outline_width: int = 1) -> pygame.Surface:
    text_surface = font.render(text, True, color)
    outline_surface = font.render(text, True, outline_color)
    
    width = text_surface.get_width() + 2 * outline_width
    height = text_surface.get_height() + 2 * outline_width
    
    combined_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                combined_surface.blit(outline_surface, (outline_width + dx, outline_width + dy))
    
    # Draw main text
    combined_surface.blit(text_surface, (outline_width, outline_width))
    
    return combined_surface

def screen_shake(intensity: int, duration: int) -> Tuple[int, int]:
    if duration > 0:
        return (random.randint(-intensity, intensity), random.randint(-intensity, intensity))
    return (0, 0)

def calculate_level_multiplier(level: int) -> float:
    return 1.0 + (level - 1) * LEVEL_DIFFICULTY_INCREASE

def calculate_spawn_rate(base_rate: int, level: int) -> int:
    return max(500, int(base_rate * (1.0 - (level - 1) * 0.1)))

def weighted_choice(choices: List[Tuple[Any, float]]) -> Any:
    total_weight = sum(weight for _, weight in choices)
    r = random.uniform(0, total_weight)
    
    current_weight = 0
    for choice, weight in choices:
        current_weight += weight
        if r <= current_weight:
            return choice
    
    return choices[0][0]  # Fallback

def circular_position(center: Tuple[float, float], radius: float, angle: float) -> Tuple[float, float]:
    return (
        center[0] + radius * math.cos(angle),
        center[1] + radius * math.sin(angle)
    )

def spiral_position(center: Tuple[float, float], radius: float, angle: float, spiral_rate: float) -> Tuple[float, float]:
    spiral_radius = radius * (1 + spiral_rate * angle)
    return (
        center[0] + spiral_radius * math.cos(angle),
        center[1] + spiral_radius * math.sin(angle)
    )

def get_direction_vector(from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> Tuple[float, float]:
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return normalize_vector((dx, dy))

def move_towards(current_pos: Tuple[float, float], target_pos: Tuple[float, float], speed: float) -> Tuple[float, float]:
    direction = get_direction_vector(current_pos, target_pos)
    return (
        current_pos[0] + direction[0] * speed,
        current_pos[1] + direction[1] * speed
    )

def is_offscreen(pos: Tuple[float, float], size: Tuple[float, float], margin: int = 50) -> bool:
    x, y = pos
    w, h = size
    return (x + w < -margin or x > SCREEN_WIDTH + margin or 
            y + h < -margin or y > SCREEN_HEIGHT + margin)

def constrain_to_screen(pos: Tuple[float, float], size: Tuple[float, float]) -> Tuple[float, float]:
    x, y = pos
    w, h = size
    x = clamp(x, 0, SCREEN_WIDTH - w)
    y = clamp(y, 0, SCREEN_HEIGHT - h)
    return (x, y)

class Timer:
    def __init__(self, duration: float, callback=None):
        self.duration = duration
        self.callback = callback
        self.start_time = pygame.time.get_ticks()
        self.is_active = True
    
    def update(self):
        if self.is_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.duration:
                self.is_active = False
                if self.callback:
                    self.callback()
                return True
        return False
    
    def reset(self):
        self.start_time = pygame.time.get_ticks()
        self.is_active = True
    
    def get_remaining_time(self) -> float:
        if not self.is_active:
            return 0
        elapsed = pygame.time.get_ticks() - self.start_time
        return max(0, self.duration - elapsed)
    
    def get_progress(self) -> float:
        if not self.is_active:
            return 1.0
        elapsed = pygame.time.get_ticks() - self.start_time
        return min(1.0, elapsed / self.duration)

class Cooldown:
    def __init__(self, duration: float):
        self.duration = duration
        self.last_use = 0
    
    def can_use(self) -> bool:
        return pygame.time.get_ticks() - self.last_use >= self.duration
    
    def use(self):
        self.last_use = pygame.time.get_ticks()
    
    def get_remaining_time(self) -> float:
        elapsed = pygame.time.get_ticks() - self.last_use
        return max(0, self.duration - elapsed)
    
    def get_progress(self) -> float:
        elapsed = pygame.time.get_ticks() - self.last_use
        return min(1.0, elapsed / self.duration)