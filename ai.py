import random
from sprites import Enemy, Enemy2

class EnemyAI:
    def __init__(self):
        self.enemy_spawn_rate = 2000 # Milliseconds between spawns
        self.last_spawn_time = 0

    def spawn_enemy(self, enemy_group, all_sprites, player, level):
        # Get current time
        current_time = pygame.time.get_ticks()
        # Only spawn after the required time has passed
        if current_time - self.last_spawn_time >= self.enemy_spawn_rate:
            enemy_type = random.choice([Enemy, Enemy2]) # choose a type of enemy
            # New enemy
            enemy = enemy_type(random.randint(0, 750), random.randint(-150, -50)) # Create new enemy with X and Y
            all_sprites.add(enemy) # add to all sprites
            enemy_group.add(enemy) # add to enemies group
            # set last spawn time
            self.last_spawn_time = current_time
            # Reduce the time between spawning by 5%
            self.enemy_spawn_rate *= 0.95
            # Limit the minimum spawn rate to 500 milliseconds
            if self.enemy_spawn_rate < 500:
                self.enemy_spawn_rate = 500

enemy_ai = EnemyAI() # Create an instance