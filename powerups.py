import pygame

def apply_powerup(player, powerup, all_sprites, bullets):
    if powerup.type == "health":
        player.health = min(player.health + 50, 100) # cap health at 100
    elif powerup.type == "damage":
        # Increase bullet damage temporarily
        increase_damage(player, 5, 5000, all_sprites, bullets) # duration ms, and bullet list
    elif powerup.type == "shield":
        # Activate shield for a duration
        activate_shield(player, 5000)
    elif powerup.type == "speed":
        activate_speed_boost(player)

def increase_damage(player, damage_increase, duration, all_sprites, bullets):
    # Add the damage increase to the player and store the original damage
    player.active_powerups["damage"] = damage_increase

    # Set the new damage value
    for bullet in bullets:
        bullet.damage += damage_increase

    # Set a timer to remove the damage increase after a set time
    pygame.time.set_timer(pygame.USEREVENT, duration)

def activate_shield(player, duration):
    # The shield is activated for a set duration of time
    player.protected = True
    player.protected_timer = pygame.time.get_ticks()

def activate_speed_boost(player):
    # Change the speed and set a timer
    player.max_speed *= 1.5  # Increase max speed

    # Set a timer to end the speed boost after a set time
    end_event = pygame.event.Event(pygame.USEREVENT, code="speed_boost_end")
    pygame.time.set_timer(pygame.USEREVENT, 5000) # 5 seconds
    pygame.event.post(end_event)