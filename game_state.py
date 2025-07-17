import pygame
import json
import os
from typing import Dict, Any, Optional, List
from config import *
from utils import save_json, load_json

class GameStateManager:
    def __init__(self):
        self.state = GameState.MENU
        self.previous_state = None
        self.paused = False
        self.game_over = False
        self.score = 0
        self.high_score = 0
        self.lives = PLAYER_LIVES
        self.level = 1
        self.time_played = 0
        self.start_time = 0
        
        # Game statistics
        self.stats = {
            "total_score": 0,
            "total_time_played": 0,
            "games_played": 0,
            "enemies_killed": 0,
            "bosses_defeated": 0,
            "powerups_collected": 0,
            "levels_completed": 0,
            "highest_level": 1,
            "perfect_levels": 0,
            "total_shots_fired": 0,
            "shots_hit": 0,
            "damage_taken": 0,
            "continues_used": 0
        }
        
        # Settings
        self.settings = {
            "music_volume": MUSIC_VOLUME,
            "sfx_volume": SFX_VOLUME,
            "music_enabled": True,
            "sfx_enabled": True,
            "fullscreen": False,
            "show_fps": False,
            "difficulty": "normal",
            "controls": CONTROLS.copy()
        }
        
        # Achievement system
        self.achievements = {
            "first_kill": {"unlocked": False, "name": "First Blood", "description": "Kill your first enemy"},
            "first_boss": {"unlocked": False, "name": "Boss Hunter", "description": "Defeat your first boss"},
            "level_5": {"unlocked": False, "name": "Veteran", "description": "Reach level 5"},
            "level_10": {"unlocked": False, "name": "Expert", "description": "Reach level 10"},
            "score_10k": {"unlocked": False, "name": "Score Master", "description": "Reach 10,000 points"},
            "score_50k": {"unlocked": False, "name": "High Scorer", "description": "Reach 50,000 points"},
            "score_100k": {"unlocked": False, "name": "Legend", "description": "Reach 100,000 points"},
            "perfect_level": {"unlocked": False, "name": "Flawless", "description": "Complete a level without taking damage"},
            "collect_100_powerups": {"unlocked": False, "name": "Collector", "description": "Collect 100 power-ups"},
            "survive_5_minutes": {"unlocked": False, "name": "Survivor", "description": "Survive for 5 minutes"},
            "kill_1000_enemies": {"unlocked": False, "name": "Exterminator", "description": "Kill 1,000 enemies"},
            "defeat_10_bosses": {"unlocked": False, "name": "Boss Slayer", "description": "Defeat 10 bosses"},
            "no_continues": {"unlocked": False, "name": "Iron Will", "description": "Complete 5 levels without using continues"},
            "speed_demon": {"unlocked": False, "name": "Speed Demon", "description": "Complete a level in under 1 minute"},
            "sharpshooter": {"unlocked": False, "name": "Sharpshooter", "description": "Achieve 90% accuracy in a level"}
        }
        
        # Session data
        self.session_data = {
            "level_start_time": 0,
            "level_score": 0,
            "level_enemies_killed": 0,
            "level_damage_taken": 0,
            "level_shots_fired": 0,
            "level_shots_hit": 0,
            "level_powerups_collected": 0,
            "continues_this_session": 0,
            "levels_completed_no_continues": 0
        }
        
        # Load saved data
        self.load_all_data()
        
    def change_state(self, new_state: GameState):
        self.previous_state = self.state
        self.state = new_state
        
    def toggle_pause(self):
        if self.state == GameState.PLAYING:
            self.paused = not self.paused
            
    def start_new_game(self):
        self.state = GameState.PLAYING
        self.game_over = False
        self.score = 0
        self.lives = PLAYER_LIVES
        self.level = 1
        self.start_time = pygame.time.get_ticks()
        self.time_played = 0
        self.paused = False
        
        # Reset session data
        self.session_data = {
            "level_start_time": pygame.time.get_ticks(),
            "level_score": 0,
            "level_enemies_killed": 0,
            "level_damage_taken": 0,
            "level_shots_fired": 0,
            "level_shots_hit": 0,
            "level_powerups_collected": 0,
            "continues_this_session": 0,
            "levels_completed_no_continues": 0
        }
        
        self.stats["games_played"] += 1
        
    def game_over_state(self):
        self.game_over = True
        self.state = GameState.GAME_OVER
        
        # Update statistics
        self.time_played = (pygame.time.get_ticks() - self.start_time) / 1000
        self.stats["total_time_played"] += self.time_played
        self.stats["total_score"] += self.score
        
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
            
        # Check achievements
        self.check_achievements()
        
        # Save data
        self.save_all_data()
        
    def continue_game(self):
        if self.lives <= 0:
            self.lives = 1
            self.stats["continues_used"] += 1
            self.session_data["continues_this_session"] += 1
            self.state = GameState.PLAYING
            self.game_over = False
            
    def level_complete(self, level_score: int, level_data: Dict):
        self.score += level_score
        self.level += 1
        
        # Update level statistics
        self.stats["levels_completed"] += 1
        self.stats["highest_level"] = max(self.stats["highest_level"], self.level)
        
        # Update session data
        self.session_data["level_score"] += level_score
        self.session_data["level_enemies_killed"] += level_data.get("enemies_killed", 0)
        self.session_data["level_damage_taken"] += level_data.get("damage_taken", 0)
        self.session_data["level_powerups_collected"] += level_data.get("powerups_collected", 0)
        
        # Check for perfect level
        if level_data.get("damage_taken", 0) == 0:
            self.stats["perfect_levels"] += 1
            self.unlock_achievement("perfect_level")
            
        # Check for no continues achievement
        if self.session_data["continues_this_session"] == 0:
            self.session_data["levels_completed_no_continues"] += 1
            if self.session_data["levels_completed_no_continues"] >= 5:
                self.unlock_achievement("no_continues")
                
        # Check for speed demon achievement
        level_duration = level_data.get("duration", 0)
        if level_duration < 60:
            self.unlock_achievement("speed_demon")
            
        # Check for sharpshooter achievement
        if (self.session_data["level_shots_fired"] > 0 and 
            self.session_data["level_shots_hit"] / self.session_data["level_shots_fired"] >= 0.9):
            self.unlock_achievement("sharpshooter")
            
        # Reset level session data
        self.session_data["level_start_time"] = pygame.time.get_ticks()
        self.session_data["level_shots_fired"] = 0
        self.session_data["level_shots_hit"] = 0
        
        # Check other achievements
        self.check_achievements()
        
    def enemy_killed(self, enemy_score: int):
        self.score += enemy_score
        self.stats["enemies_killed"] += 1
        self.session_data["level_enemies_killed"] += 1
        
        # Check achievements
        if self.stats["enemies_killed"] == 1:
            self.unlock_achievement("first_kill")
        elif self.stats["enemies_killed"] >= 1000:
            self.unlock_achievement("kill_1000_enemies")
            
    def boss_defeated(self, boss_score: int):
        self.score += boss_score
        self.stats["bosses_defeated"] += 1
        
        # Check achievements
        if self.stats["bosses_defeated"] == 1:
            self.unlock_achievement("first_boss")
        elif self.stats["bosses_defeated"] >= 10:
            self.unlock_achievement("defeat_10_bosses")
            
    def powerup_collected(self, powerup_score: int = 0):
        self.score += powerup_score
        self.stats["powerups_collected"] += 1
        self.session_data["level_powerups_collected"] += 1
        
        # Check achievements
        if self.stats["powerups_collected"] >= 100:
            self.unlock_achievement("collect_100_powerups")
            
    def shot_fired(self):
        self.stats["total_shots_fired"] += 1
        self.session_data["level_shots_fired"] += 1
        
    def shot_hit(self):
        self.stats["shots_hit"] += 1
        self.session_data["level_shots_hit"] += 1
        
    def damage_taken(self, damage: int):
        self.stats["damage_taken"] += damage
        self.session_data["level_damage_taken"] += damage
        
    def life_lost(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over_state()
            
    def add_life(self):
        self.lives += 1
        
    def update(self):
        if self.state == GameState.PLAYING and not self.paused:
            # Update time played
            current_time = pygame.time.get_ticks()
            self.time_played = (current_time - self.start_time) / 1000
            
            # Check time-based achievements
            if self.time_played >= 300:  # 5 minutes
                self.unlock_achievement("survive_5_minutes")
                
    def check_achievements(self):
        # Score-based achievements
        if self.score >= 10000:
            self.unlock_achievement("score_10k")
        if self.score >= 50000:
            self.unlock_achievement("score_50k")
        if self.score >= 100000:
            self.unlock_achievement("score_100k")
            
        # Level-based achievements
        if self.level >= 5:
            self.unlock_achievement("level_5")
        if self.level >= 10:
            self.unlock_achievement("level_10")
            
    def unlock_achievement(self, achievement_id: str):
        if achievement_id in self.achievements and not self.achievements[achievement_id]["unlocked"]:
            self.achievements[achievement_id]["unlocked"] = True
            return True
        return False
        
    def get_unlocked_achievements(self) -> List[Dict]:
        return [achievement for achievement in self.achievements.values() if achievement["unlocked"]]
        
    def get_achievement_progress(self) -> Dict[str, float]:
        progress = {}
        
        # Calculate progress for various achievements
        progress["kill_1000_enemies"] = min(1.0, self.stats["enemies_killed"] / 1000)
        progress["defeat_10_bosses"] = min(1.0, self.stats["bosses_defeated"] / 10)
        progress["collect_100_powerups"] = min(1.0, self.stats["powerups_collected"] / 100)
        progress["score_10k"] = min(1.0, self.score / 10000)
        progress["score_50k"] = min(1.0, self.score / 50000)
        progress["score_100k"] = min(1.0, self.score / 100000)
        progress["survive_5_minutes"] = min(1.0, self.time_played / 300)
        
        return progress
        
    def get_accuracy(self) -> float:
        if self.stats["total_shots_fired"] == 0:
            return 0.0
        return self.stats["shots_hit"] / self.stats["total_shots_fired"]
        
    def get_level_accuracy(self) -> float:
        if self.session_data["level_shots_fired"] == 0:
            return 0.0
        return self.session_data["level_shots_hit"] / self.session_data["level_shots_fired"]
        
    def get_play_time_formatted(self) -> str:
        total_seconds = int(self.stats["total_time_played"])
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    def get_current_session_time(self) -> str:
        if self.start_time == 0:
            return "00:00"
        
        seconds = int(self.time_played)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def update_setting(self, key: str, value: Any):
        if key in self.settings:
            self.settings[key] = value
            self.save_settings()
            
    def get_setting(self, key: str) -> Any:
        return self.settings.get(key)
        
    def reset_statistics(self):
        self.stats = {
            "total_score": 0,
            "total_time_played": 0,
            "games_played": 0,
            "enemies_killed": 0,
            "bosses_defeated": 0,
            "powerups_collected": 0,
            "levels_completed": 0,
            "highest_level": 1,
            "perfect_levels": 0,
            "total_shots_fired": 0,
            "shots_hit": 0,
            "damage_taken": 0,
            "continues_used": 0
        }
        
    def reset_achievements(self):
        for achievement in self.achievements.values():
            achievement["unlocked"] = False
            
    def save_all_data(self):
        self.save_statistics()
        self.save_settings()
        self.save_achievements()
        self.save_high_score()
        
    def load_all_data(self):
        self.load_statistics()
        self.load_settings()
        self.load_achievements()
        self.load_high_score()
        
    def save_statistics(self):
        save_json(self.stats, SAVE_PATHS["progress"])
        
    def load_statistics(self):
        data = load_json(SAVE_PATHS["progress"])
        if data:
            self.stats.update(data)
            
    def save_settings(self):
        save_json(self.settings, SAVE_PATHS["settings"])
        
    def load_settings(self):
        data = load_json(SAVE_PATHS["settings"])
        if data:
            self.settings.update(data)
            
    def save_achievements(self):
        save_json(self.achievements, SAVE_PATHS["achievements"])
        
    def load_achievements(self):
        data = load_json(SAVE_PATHS["achievements"])
        if data:
            self.achievements.update(data)
            
    def save_high_score(self):
        try:
            data = load_json(SAVE_PATHS["highscores"]) or []
            
            # Add current score if it's high enough
            if self.score > 0:
                data.append(self.score)
                
            # Sort and keep top 10
            data.sort(reverse=True)
            data = data[:10]
            
            save_json(data, SAVE_PATHS["highscores"])
            
            # Update high score
            if data:
                self.high_score = data[0]
                
        except Exception as e:
            print(f"Error saving high score: {e}")
            
    def load_high_score(self):
        try:
            data = load_json(SAVE_PATHS["highscores"])
            if data and len(data) > 0:
                self.high_score = data[0]
        except Exception as e:
            print(f"Error loading high score: {e}")
            
    def get_high_scores(self) -> List[int]:
        data = load_json(SAVE_PATHS["highscores"])
        return data if data else []
        
    def is_new_high_score(self) -> bool:
        return self.score > self.high_score
        
    def get_statistics_summary(self) -> Dict:
        return {
            "total_score": self.stats["total_score"],
            "high_score": self.high_score,
            "total_time_played": self.get_play_time_formatted(),
            "games_played": self.stats["games_played"],
            "enemies_killed": self.stats["enemies_killed"],
            "bosses_defeated": self.stats["bosses_defeated"],
            "powerups_collected": self.stats["powerups_collected"],
            "levels_completed": self.stats["levels_completed"],
            "highest_level": self.stats["highest_level"],
            "perfect_levels": self.stats["perfect_levels"],
            "accuracy": f"{self.get_accuracy() * 100:.1f}%",
            "continues_used": self.stats["continues_used"],
            "achievements_unlocked": len(self.get_unlocked_achievements()),
            "total_achievements": len(self.achievements)
        }
        
    def export_save_data(self, filename: str) -> bool:
        try:
            export_data = {
                "statistics": self.stats,
                "settings": self.settings,
                "achievements": self.achievements,
                "high_scores": self.get_high_scores()
            }
            return save_json(export_data, filename)
        except Exception as e:
            print(f"Error exporting save data: {e}")
            return False
            
    def import_save_data(self, filename: str) -> bool:
        try:
            data = load_json(filename)
            if data:
                if "statistics" in data:
                    self.stats.update(data["statistics"])
                if "settings" in data:
                    self.settings.update(data["settings"])
                if "achievements" in data:
                    self.achievements.update(data["achievements"])
                if "high_scores" in data:
                    save_json(data["high_scores"], SAVE_PATHS["highscores"])
                    self.load_high_score()
                    
                self.save_all_data()
                return True
        except Exception as e:
            print(f"Error importing save data: {e}")
        return False