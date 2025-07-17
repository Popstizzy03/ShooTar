import pygame
from typing import Dict, List, Optional

class SpriteGroups:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.ui_elements = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        
        # Dictionary for easy access
        self.groups = {
            "all": self.all_sprites,
            "player": self.player_group,
            "enemies": self.enemies,
            "bullets": self.bullets,
            "enemy_bullets": self.enemy_bullets,
            "powerups": self.powerups,
            "bosses": self.bosses,
            "effects": self.effects,
            "particles": self.particles,
            "ui": self.ui_elements,
            "obstacles": self.obstacles,
            "collectibles": self.collectibles
        }
    
    def add_sprite(self, sprite: pygame.sprite.Sprite, group_names: List[str]):
        for group_name in group_names:
            if group_name in self.groups:
                self.groups[group_name].add(sprite)
    
    def remove_sprite(self, sprite: pygame.sprite.Sprite, group_names: Optional[List[str]] = None):
        if group_names is None:
            group_names = list(self.groups.keys())
        
        for group_name in group_names:
            if group_name in self.groups:
                self.groups[group_name].remove(sprite)
    
    def get_group(self, group_name: str) -> pygame.sprite.Group:
        return self.groups.get(group_name, pygame.sprite.Group())
    
    def clear_group(self, group_name: str):
        if group_name in self.groups:
            self.groups[group_name].empty()
    
    def clear_all_except(self, exceptions: List[str]):
        for group_name, group in self.groups.items():
            if group_name not in exceptions:
                group.empty()
    
    def update_all(self):
        self.all_sprites.update()
    
    def update_group(self, group_name: str):
        if group_name in self.groups:
            self.groups[group_name].update()
    
    def draw_group(self, surface: pygame.Surface, group_name: str):
        if group_name in self.groups:
            self.groups[group_name].draw(surface)
    
    def draw_all(self, surface: pygame.Surface):
        self.all_sprites.draw(surface)
    
    def get_sprite_count(self, group_name: str) -> int:
        if group_name in self.groups:
            return len(self.groups[group_name])
        return 0
    
    def get_sprites_by_type(self, group_name: str, sprite_type: type) -> List[pygame.sprite.Sprite]:
        if group_name in self.groups:
            return [sprite for sprite in self.groups[group_name] if isinstance(sprite, sprite_type)]
        return []
    
    def reset_all(self):
        for group in self.groups.values():
            group.empty()
    
    def get_collision_candidates(self, sprite: pygame.sprite.Sprite, group_name: str) -> List[pygame.sprite.Sprite]:
        if group_name in self.groups:
            return pygame.sprite.spritecollide(sprite, self.groups[group_name], False)
        return []
    
    def check_collision(self, group1_name: str, group2_name: str, dokill1: bool = False, dokill2: bool = False) -> Dict:
        if group1_name in self.groups and group2_name in self.groups:
            return pygame.sprite.groupcollide(
                self.groups[group1_name], 
                self.groups[group2_name], 
                dokill1, 
                dokill2
            )
        return {}

# Global sprite groups instance
sprite_groups = SpriteGroups()