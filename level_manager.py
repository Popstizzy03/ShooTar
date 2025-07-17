import pygame
import random
from typing import Dict, List, Optional, Tuple
from config import *
from enemies import Enemy, Boss
from sprite_groups import sprite_groups
from utils import weighted_choice, Timer, calculate_level_multiplier, calculate_spawn_rate

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.theme = LevelTheme.SPACE
        self.enemy_spawn_timer = 0
        self.boss_spawn_threshold = BOSS_SPAWN_LEVEL
        self.boss_spawned = False
        self.level_complete = False
        self.level_score = 0
        self.enemies_spawned = 0
        self.enemies_killed = 0
        self.total_enemies_for_level = 0
        
        # Level progression
        self.level_transitions = {}
        self.level_stats = {
            "start_time": 0,
            "enemies_killed": 0,
            "damage_taken": 0,
            "powerups_collected": 0,
            "score": 0
        }
        
        # Dynamic difficulty
        self.difficulty_multiplier = 1.0
        self.spawn_rate_multiplier = 1.0
        self.enemy_health_multiplier = 1.0
        self.enemy_speed_multiplier = 1.0
        
        # Level timers
        self.level_timer = Timer(60000)  # 1 minute per level base
        self.boss_timer = Timer(30000)   # 30 seconds for boss fight
        
    def start_level(self, level_number: int):
        self.current_level = level_number
        self.theme = self.get_level_theme(level_number)
        self.boss_spawned = False
        self.level_complete = False
        self.level_score = 0
        self.enemies_spawned = 0
        self.enemies_killed = 0
        
        # Calculate level parameters
        self.difficulty_multiplier = calculate_level_multiplier(level_number)
        self.spawn_rate_multiplier = 1.0 + (level_number - 1) * 0.1
        self.enemy_health_multiplier = 1.0 + (level_number - 1) * 0.2
        self.enemy_speed_multiplier = 1.0 + (level_number - 1) * 0.1
        
        # Set total enemies for this level
        self.total_enemies_for_level = 15 + (level_number - 1) * 5
        
        # Reset timers
        self.level_timer.reset()
        self.boss_timer.reset()
        
        # Initialize level stats
        self.level_stats = {
            "start_time": pygame.time.get_ticks(),
            "enemies_killed": 0,
            "damage_taken": 0,
            "powerups_collected": 0,
            "score": 0
        }
        
        # Clear existing enemies and bullets
        sprite_groups.clear_group("enemies")
        sprite_groups.clear_group("bosses")
        sprite_groups.clear_group("enemy_bullets")
        
        print(f"Level {level_number} started - Theme: {self.theme.name}")
        
    def get_level_theme(self, level_number: int) -> LevelTheme:
        theme_cycle = [
            LevelTheme.SPACE,
            LevelTheme.NEBULA,
            LevelTheme.ASTEROID,
            LevelTheme.CYBER,
            LevelTheme.SOLAR
        ]
        return theme_cycle[(level_number - 1) % len(theme_cycle)]
        
    def update(self, player):
        self.level_timer.update()
        
        if not self.boss_spawned:
            self.update_enemy_spawning(player)
            self.check_boss_spawn_conditions()
        else:
            self.update_boss_fight()
            
        self.check_level_completion()
        
    def update_enemy_spawning(self, player):
        current_time = pygame.time.get_ticks()
        
        # Calculate spawn rate based on level
        base_spawn_rate = calculate_spawn_rate(ENEMY_SPAWN_RATE, self.current_level)
        spawn_rate = int(base_spawn_rate / self.spawn_rate_multiplier)
        
        # Spawn enemies if conditions are met
        if (current_time - self.enemy_spawn_timer > spawn_rate and
            sprite_groups.get_sprite_count("enemies") < MAX_ENEMIES and
            self.enemies_spawned < self.total_enemies_for_level):
            
            self.spawn_enemy(player)
            self.enemy_spawn_timer = current_time
            
    def spawn_enemy(self, player):
        # Determine enemy type based on level
        enemy_weights = self.get_enemy_spawn_weights()
        enemy_type = weighted_choice(enemy_weights)
        
        # Create enemy with level-based stats
        enemy = Enemy(enemy_type, self.current_level)
        enemy.target = player
        
        # Apply level modifiers
        enemy.health = int(enemy.health * self.enemy_health_multiplier)
        enemy.speed = enemy.speed * self.enemy_speed_multiplier
        
        # Add to sprite groups
        sprite_groups.add_sprite(enemy, ["all", "enemies"])
        
        self.enemies_spawned += 1
        
    def get_enemy_spawn_weights(self) -> List[Tuple[EnemyType, float]]:
        # Adjust enemy spawn weights based on level
        if self.current_level <= 2:
            return [
                (EnemyType.BASIC, 0.7),
                (EnemyType.FAST, 0.3)
            ]
        elif self.current_level <= 4:
            return [
                (EnemyType.BASIC, 0.4),
                (EnemyType.FAST, 0.3),
                (EnemyType.HEAVY, 0.2),
                (EnemyType.SHOOTER, 0.1)
            ]
        else:
            return [
                (EnemyType.BASIC, 0.3),
                (EnemyType.FAST, 0.25),
                (EnemyType.HEAVY, 0.2),
                (EnemyType.SHOOTER, 0.15),
                (EnemyType.KAMIKAZE, 0.1)
            ]
            
    def check_boss_spawn_conditions(self):
        # Boss spawns when enough enemies are killed or time runs out
        if (self.enemies_killed >= self.total_enemies_for_level * 0.8 or
            self.level_timer.get_remaining_time() <= 0):
            self.spawn_boss()
            
    def spawn_boss(self):
        if self.boss_spawned:
            return
            
        # Determine boss type based on level
        boss_type = ((self.current_level - 1) // 5) + 1
        
        # Create boss
        boss = Boss(self.current_level, boss_type)
        boss.target = sprite_groups.get_group("player").sprites()[0] if sprite_groups.get_group("player") else None
        boss.activate()
        
        # Add to sprite groups
        sprite_groups.add_sprite(boss, ["all", "bosses"])
        
        self.boss_spawned = True
        self.boss_timer.reset()
        
        # Clear remaining enemies
        sprite_groups.clear_group("enemies")
        
        print(f"Boss spawned for level {self.current_level}")
        
    def update_boss_fight(self):
        self.boss_timer.update()
        
        # Check if boss is defeated
        if sprite_groups.get_sprite_count("bosses") == 0:
            self.level_complete = True
            
    def check_level_completion(self):
        if self.level_complete:
            return
            
        # Level is complete when boss is defeated
        if self.boss_spawned and sprite_groups.get_sprite_count("bosses") == 0:
            self.complete_level()
            
    def complete_level(self):
        self.level_complete = True
        
        # Calculate level completion bonus
        time_bonus = int(self.level_timer.get_remaining_time() / 100)
        completion_bonus = SCORE_VALUES["level_complete"]
        
        # Check for perfect level (no damage taken)
        if self.level_stats["damage_taken"] == 0:
            completion_bonus += SCORE_VALUES["perfect_level"]
            
        self.level_score += completion_bonus + time_bonus
        
        # Update level stats
        self.level_stats["score"] = self.level_score
        self.level_stats["enemies_killed"] = self.enemies_killed
        
        print(f"Level {self.current_level} completed! Score: {self.level_score}")
        
    def get_next_level_number(self) -> int:
        return self.current_level + 1
        
    def advance_to_next_level(self):
        next_level = self.get_next_level_number()
        if next_level <= MAX_LEVELS:
            self.start_level(next_level)
            return True
        return False
        
    def restart_current_level(self):
        self.start_level(self.current_level)
        
    def enemy_killed(self, enemy):
        self.enemies_killed += 1
        self.level_score += enemy.score_value
        
    def boss_killed(self, boss):
        self.level_score += boss.get_score_value()
        
    def player_took_damage(self, damage):
        self.level_stats["damage_taken"] += damage
        
    def powerup_collected(self, powerup):
        self.level_stats["powerups_collected"] += 1
        
    def get_level_progress(self) -> float:
        if self.boss_spawned:
            return 1.0
        return self.enemies_killed / self.total_enemies_for_level
        
    def get_boss_progress(self) -> float:
        if not self.boss_spawned:
            return 0.0
        return 1.0 - (self.boss_timer.get_remaining_time() / 30000)
        
    def get_level_stats(self) -> Dict:
        stats = self.level_stats.copy()
        stats["level"] = self.current_level
        stats["theme"] = self.theme.name
        stats["difficulty_multiplier"] = self.difficulty_multiplier
        stats["enemies_spawned"] = self.enemies_spawned
        stats["enemies_killed"] = self.enemies_killed
        stats["total_enemies"] = self.total_enemies_for_level
        stats["boss_spawned"] = self.boss_spawned
        stats["level_complete"] = self.level_complete
        stats["level_score"] = self.level_score
        stats["progress"] = self.get_level_progress()
        return stats
        
    def get_background_color(self) -> Tuple[int, int, int]:
        return self.theme.value["bg_color"]
        
    def get_enemy_color_modifier(self) -> Tuple[int, int, int]:
        return self.theme.value["enemy_color"]
        
    def is_level_complete(self) -> bool:
        return self.level_complete
        
    def is_boss_active(self) -> bool:
        return self.boss_spawned and sprite_groups.get_sprite_count("bosses") > 0
        
    def get_remaining_enemies(self) -> int:
        return max(0, self.total_enemies_for_level - self.enemies_killed)
        
    def get_level_time_remaining(self) -> float:
        return self.level_timer.get_remaining_time()
        
    def get_boss_time_remaining(self) -> float:
        return self.boss_timer.get_remaining_time() if self.boss_spawned else 0
        
    def force_boss_spawn(self):
        if not self.boss_spawned:
            self.spawn_boss()
            
    def reset_level_stats(self):
        self.level_stats = {
            "start_time": pygame.time.get_ticks(),
            "enemies_killed": 0,
            "damage_taken": 0,
            "powerups_collected": 0,
            "score": 0
        }
        
    def get_enemy_spawn_rate(self) -> int:
        return int(ENEMY_SPAWN_RATE / self.spawn_rate_multiplier)
        
    def get_difficulty_description(self) -> str:
        if self.difficulty_multiplier <= 1.2:
            return "Easy"
        elif self.difficulty_multiplier <= 1.5:
            return "Normal"
        elif self.difficulty_multiplier <= 2.0:
            return "Hard"
        else:
            return "Extreme"
            
    def can_spawn_powerup(self) -> bool:
        # Increase powerup spawn chance in later levels
        base_chance = POWERUP_CHANCE
        level_bonus = (self.current_level - 1) * 0.02
        return random.random() < (base_chance + level_bonus)
        
    def get_level_summary(self) -> Dict:
        duration = (pygame.time.get_ticks() - self.level_stats["start_time"]) / 1000
        return {
            "level": self.current_level,
            "theme": self.theme.name,
            "duration": duration,
            "enemies_killed": self.enemies_killed,
            "damage_taken": self.level_stats["damage_taken"],
            "powerups_collected": self.level_stats["powerups_collected"],
            "score": self.level_score,
            "difficulty": self.get_difficulty_description(),
            "perfect_level": self.level_stats["damage_taken"] == 0
        }