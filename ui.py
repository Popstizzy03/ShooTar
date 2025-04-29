import pygame

def draw_text(surf, text, size, x, y, color, font_name):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_health_bar(surf, x, y, pct, outline_color, fill_color):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, fill_color, fill_rect)
    pygame.draw.rect(surf, outline_color, outline_rect, 2)

def draw_powerup_icons(surf, powerups, x, y, size):
    """Draws icons for active powerups."""
    icon_x = x
    for powerup_name, remaining_time in powerups.items():
        # Replace with your actual power-up icons
        icon = pygame.Surface((size, size)) # Placeholder
        icon.fill((255, 255, 255)) # White placeholder
        surf.blit(icon, (icon_x, y))
        icon_x += size + 5