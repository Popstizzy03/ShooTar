import random
from sprites import Enemy, Enemy2, Boss

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.waves = self.define_waves()
        self.current_wave = 1
        self.total_waves = len(self.waves)

    def define_waves(self):
        # Define waves of enemies for the current level
        if self.level_number == 1:
            return [
                {"enemy_type": Enemy, "count": 5},
                {"enemy_type": Enemy2, "count": 3},
                {"enemy_type": Enemy, "count": 7}
            ]
        elif self.level_number == 2:
            return [
                {"enemy_type": Enemy, "count": 8},
                {"enemy_type": Enemy2, "count": 5},
                {"enemy_type": Enemy, "count": 10}
            ]
        # Add more levels and wave definitions here
        return [{"enemy_type": Enemy, "count": 10}] # Default wave definition

    def advance_wave(self):
        self.current_wave += 1

def load_level(level, enemies, all_sprites):
    # First, remove all existing enemies
    for enemy in enemies:
        enemy.kill()

    # Check if the current wave exceeds the total waves in the level
    if level.current_wave > len(level.waves):
        print("Level Complete!")
        return  # Level is completed

    # Load the specified wave
    wave = level.waves[level.current_wave - 1] # adjust index
    for _ in range(wave["count"]):
        enemy = wave["enemy_type"](random.randint(0, 750), random.randint(-150, -50))
        all_sprites.add(enemy)
        enemies.add(enemy)