import pygame
from enum import Enum

# Screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

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
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)

# Game settings
PLAYER_SPEED = 8
PLAYER_ACCELERATION = 0.5
PLAYER_FRICTION = 0.1
PLAYER_HEALTH = 100
PLAYER_LIVES = 3

# Enemy settings
ENEMY_SPAWN_RATE = 2000  # Base spawn rate in milliseconds
MAX_ENEMIES = 15
ENEMY_HEALTH_BASE = 2
ENEMY_SPEED_BASE = 2

# Boss settings
BOSS_SPAWN_LEVEL = 5
BOSS_HEALTH_BASE = 50
BOSS_PATTERN_CHANGE_TIME = 5000

# Weapon settings
BULLET_SPEED = 10
FIRE_RATE_BASE = 500
GUN_UPGRADE_DURATION = 10000

# Power-up settings
POWERUP_SPAWN_RATE = 5000
POWERUP_CHANCE = 0.1
SHIELD_DURATION = 5000

# Level settings
LEVEL_SCORE_MULTIPLIER = 100
MAX_LEVELS = 10
LEVEL_DIFFICULTY_INCREASE = 0.2

# Effect settings
EXPLOSION_FRAME_RATE = 50
SCREEN_SHAKE_DURATION = 200
SCREEN_SHAKE_INTENSITY = 5

# Sound settings
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.7

# Asset paths
ASSET_PATHS = {
    "player": "player.png",
    "bullet": "bullet.png",
    "enemy": "enemy.png",
    "enemy2": "enemy2.png",
    "boss": "boss.png",
    "powerup": "powerup.png",
    "background": "background.png",
    "shoot": "shoot.mp3",
    "explosion": "explosion.wav",
    "powerup_sound": "powerup.wav",
    "ultrakill": "ultrakill.wav",
    "background_music": "background.wav"
}

# Weapon types
class WeaponType(Enum):
    BASIC = 1
    DOUBLE = 2
    TRIPLE = 3
    SPREAD = 4
    LASER = 5
    HOMING = 6

# Power-up types
class PowerUpType(Enum):
    SHIELD = "shield"
    GUN_UPGRADE = "gun_upgrade"
    ULTRAKILL = "ultrakill"
    HEALTH = "health"
    LIFE = "life"
    SPEED = "speed"
    RAPID_FIRE = "rapid_fire"

# Enemy types
class EnemyType(Enum):
    BASIC = 1
    FAST = 2
    HEAVY = 3
    SHOOTER = 4
    KAMIKAZE = 5

# Game states
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    LEVEL_COMPLETE = 5
    SETTINGS = 6
    ACHIEVEMENTS = 7

# Achievement types
class AchievementType(Enum):
    SCORE_MILESTONE = "score_milestone"
    ENEMY_KILLS = "enemy_kills"
    BOSS_KILLS = "boss_kills"
    POWERUP_COLLECTION = "powerup_collection"
    LEVEL_COMPLETION = "level_completion"
    PERFECT_LEVEL = "perfect_level"

# Ship types for player customization
class ShipType(Enum):
    FIGHTER = {"speed": 8, "health": 100, "fire_rate": 500}
    INTERCEPTOR = {"speed": 12, "health": 75, "fire_rate": 300}
    TANK = {"speed": 5, "health": 150, "fire_rate": 700}
    ASSAULT = {"speed": 7, "health": 120, "fire_rate": 400}

# Level themes
class LevelTheme(Enum):
    SPACE = {"bg_color": BLACK, "enemy_color": RED}
    NEBULA = {"bg_color": PURPLE, "enemy_color": ORANGE}
    ASTEROID = {"bg_color": GREY, "enemy_color": YELLOW}
    CYBER = {"bg_color": DARK_GREEN, "enemy_color": CYAN}
    SOLAR = {"bg_color": ORANGE, "enemy_color": DARK_RED}

# Input mappings
CONTROLS = {
    "move_left": pygame.K_LEFT,
    "move_right": pygame.K_RIGHT,
    "move_up": pygame.K_UP,
    "move_down": pygame.K_DOWN,
    "shoot": pygame.K_SPACE,
    "pause": pygame.K_p,
    "quit": pygame.K_ESCAPE,
    "menu": pygame.K_m,
    "restart": pygame.K_r
}

# Scoring system
SCORE_VALUES = {
    "enemy_basic": 10,
    "enemy_fast": 15,
    "enemy_heavy": 25,
    "enemy_shooter": 20,
    "enemy_kamikaze": 30,
    "boss": 500,
    "powerup": 5,
    "level_complete": 1000,
    "perfect_level": 2000
}

# Particle effects settings
PARTICLE_SETTINGS = {
    "explosion": {
        "count": 20,
        "speed": 5,
        "lifetime": 60,
        "colors": [RED, ORANGE, YELLOW]
    },
    "engine_trail": {
        "count": 5,
        "speed": 2,
        "lifetime": 30,
        "colors": [BLUE, CYAN, WHITE]
    },
    "hit_effect": {
        "count": 10,
        "speed": 3,
        "lifetime": 20,
        "colors": [WHITE, YELLOW]
    }
}

# Save file paths
SAVE_PATHS = {
    "settings": "settings.json",
    "progress": "progress.json",
    "achievements": "achievements.json",
    "highscores": "highscores.json"
}