import random
from sprites import Enemy, Enemy2, Boss

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.waves = self.define_waves()
        self.current_wave = 1
        self.total_waves = len(self.waves)
        self.boss_defeated = False
        self.difficulty_multiplier = 1.0 + (self.level_number - 1) * 0.2  # Increases difficulty by 20% per level
        
    def define_waves(self):
        if self.level_number == 1:
            return [
                {"enemy_type": Enemy, "count": 5, "pattern": "random"},
                {"enemy_type": Enemy2, "count": 3, "pattern": "v_formation"},
                {"enemy_type": Enemy, "count": 7, "pattern": "random"},
                {"enemy_type": Boss, "count": 1, "pattern": "center", "health_multiplier": 1.0}
            ]
        elif self.level_number == 2:
            return [
                {"enemy_type": Enemy, "count": 8, "pattern": "random"},
                {"enemy_type": Enemy2, "count": 5, "pattern": "horizontal_line"},
                {"enemy_type": Enemy, "count": 6, "pattern": "v_formation"},
                {"enemy_type": Enemy2, "count": 4, "pattern": "circle"},
                {"enemy_type": Boss, "count": 1, "pattern": "center", "health_multiplier": 1.5}
            ]
        elif self.level_number == 3:
            return [
                {"enemy_type": Enemy2, "count": 10, "pattern": "random"},
                {"enemy_type": Enemy, "count": 12, "pattern": "horizontal_line"},
                {"enemy_type": Enemy2, "count": 8, "pattern": "v_formation"},
                {"enemy_type": Boss, "count": 2, "pattern": "sides", "health_multiplier": 1.2}
            ]
        elif self.level_number == 4:
            return [
                {"enemy_type": Enemy, "count": 15, "pattern": "random"},
                {"enemy_type": Enemy2, "count": 12, "pattern": "circle"},
                {"enemy_type": Enemy, "count": 10, "pattern": "v_formation"},
                {"enemy_type": Enemy2, "count": 8, "pattern": "horizontal_line"},
                {"enemy_type": Boss, "count": 1, "pattern": "center", "health_multiplier": 2.0}
            ]
        elif self.level_number == 5:
            return [
                {"enemy_type": Enemy2, "count": 15, "pattern": "random"},
                {"enemy_type": Enemy, "count": 18, "pattern": "circle"},
                {"enemy_type": Enemy2, "count": 12, "pattern": "v_formation"},
                {"enemy_type": Boss, "count": 3, "pattern": "triangle", "health_multiplier": 1.8}
            ]
        # Default wave for higher levels - scales with level number
        return [
            {"enemy_type": Enemy, "count": 10 + self.level_number * 2, "pattern": "random"},
            {"enemy_type": Enemy2, "count": 8 + self.level_number, "pattern": "v_formation"},
            {"enemy_type": Enemy, "count": 12 + self.level_number, "pattern": "horizontal_line"},
            {"enemy_type": Boss, "count": 1 + (self.level_number // 3), "pattern": "random", "health_multiplier": 1.0 + (self.level_number * 0.3)}
        ]

    def advance_wave(self):
        self.current_wave += 1
        
    def is_boss_wave(self):
        if self.current_wave <= len(self.waves):
            return self.waves[self.current_wave - 1]["enemy_type"] == Boss
        return False

def spawn_enemy_in_pattern(enemy_type, pattern, count, screen_width=800, all_sprites=None, enemies=None, health_multiplier=1.0, difficulty=1.0):
    spawned_enemies = []
    
    if pattern == "random":
        for _ in range(count):
            enemy = enemy_type(random.randint(50, screen_width-50), random.randint(-150, -50))
            enemy.health *= health_multiplier * difficulty
            enemy.speed *= difficulty
            spawned_enemies.append(enemy)
            
    elif pattern == "horizontal_line":
        spacing = screen_width // (count + 1)
        for i in range(count):
            enemy = enemy_type(spacing * (i + 1), -100)
            enemy.health *= health_multiplier * difficulty
            enemy.speed *= difficulty
            spawned_enemies.append(enemy)
            
    elif pattern == "v_formation":
        center_x = screen_width // 2
        for i in range(count):
            # Alternate enemies to create V pattern
            offset = (i // 2) * 60
            if i % 2 == 0:
                x = center_x - offset
            else:
                x = center_x + offset
            enemy = enemy_type(x, -100 - (i * 30))
            enemy.health *= health_multiplier * difficulty
            enemy.speed *= difficulty
            spawned_enemies.append(enemy)
            
    elif pattern == "circle":
        center_x = screen_width // 2
        radius = 100
        for i in range(count):
            angle = (i / count) * 2 * 3.14159  # Convert to radians
            x = center_x + int(radius * math.cos(angle))
            y = -100 + int(radius * math.sin(angle))
            enemy = enemy_type(x, y)
            enemy.health *= health_multiplier * difficulty
            enemy.speed *= difficulty
            spawned_enemies.append(enemy)
            
    elif pattern == "center":
        for i in range(count):
            enemy = enemy_type(screen_width // 2, -150)
            enemy.health *= health_multiplier * difficulty
            enemy.speed *= 0.8 * difficulty  # Bosses move slower
            spawned_enemies.append(enemy)
            
    elif pattern == "sides":
        spacing = screen_width // (count + 1)
        for i in range(count):
            enemy = enemy_type(spacing * (i + 1), -150)
            enemy.health *= health_multiplier * difficulty
            enemy.speed *= 0.8 * difficulty
            spawned_enemies.append(enemy)
            
    elif pattern == "triangle":
        center_x = screen_width // 2
        if count == 3:
            positions = [
                (center_x, -150),
                (center_x - 100, -100),
                (center_x + 100, -100)
            ]
        else:
            positions = [(random.randint(50, screen_width-50), random.randint(-150, -50)) for _ in range(count)]
            
        for i, (x, y) in enumerate(positions):
            if i < count:
                enemy = enemy_type(x, y)
                enemy.health *= health_multiplier * difficulty
                enemy.speed *= 0.8 * difficulty
                spawned_enemies.append(enemy)
    
    # Add spawned enemies to sprite groups
    if all_sprites and enemies:
        for enemy in spawned_enemies:
            all_sprites.add(enemy)
            enemies.add(enemy)
    
    return spawned_enemies

def load_level(level, enemies, all_sprites):
    # First, remove all existing enemies
    for enemy in enemies:
        enemy.kill()

    # Check if the current wave exceeds the total waves in the level
    if level.current_wave > len(level.waves):
        print(f"Level {level.level_number} Complete!")
        return True  # Level is completed

    # Load the specified wave
    wave = level.waves[level.current_wave - 1]  # adjust index
    
    # Get pattern and optional health multiplier
    pattern = wave.get("pattern", "random")
    health_multiplier = wave.get("health_multiplier", 1.0)
    
    # Spawn enemies according to the pattern
    spawn_enemy_in_pattern(
        wave["enemy_type"], 
        pattern, 
        wave["count"], 
        all_sprites=all_sprites, 
        enemies=enemies,
        health_multiplier=health_multiplier,
        difficulty=level.difficulty_multiplier
    )
    
    # Announce boss waves
    if level.is_boss_wave():
        print(f"BOSS WAVE! Level {level.level_number}, Wave {level.current_wave}")
    else:
        print(f"Level {level.level_number}, Wave {level.current_wave} of {level.total_waves}")
        
    return False  # Level is not completed yet
