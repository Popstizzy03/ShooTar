import pygame

# Dictionary of sounds to pre-load
sounds = {
    "shoot": pygame.mixer.Sound("shoot.wav"),
    "explosion": pygame.mixer.Sound("explosion.wav"),
    "powerup": pygame.mixer.Sound("powerup.wav"),
    "game_over": pygame.mixer.Sound("game_over.wav")
}

def play_sound(sound_name):
    """Plays a sound from the pre-loaded sounds."""
    sound = sounds.get(sound_name)
    if sound:
        sound.play()

def play_music(music_file, volume=0.5):
    """Plays background music."""
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1) # Loop indefinitely