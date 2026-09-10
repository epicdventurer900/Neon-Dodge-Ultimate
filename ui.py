import pygame
import math
from settings import WIDTH, HEIGHT, COLORS

_gradient_surface = None


def _build_gradient():
    """Pre-render the static background gradient once."""
    global _gradient_surface
    _gradient_surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT - 1)
        r = int(COLORS["BG_DARK"][0] + (COLORS["BG_LIGHT"][0] - COLORS["BG_DARK"][0]) * ratio)
        g = int(COLORS["BG_DARK"][1] + (COLORS["BG_LIGHT"][1] - COLORS["BG_DARK"][1]) * ratio)
        b = int(COLORS["BG_DARK"][2] + (COLORS["BG_LIGHT"][2] - COLORS["BG_DARK"][2]) * ratio)
        pygame.draw.line(_gradient_surface, (r, g, b), (0, y), (WIDTH, y))


def draw_gradient_background(surface):
    """Draw the pre-rendered gradient background."""
    global _gradient_surface
    if _gradient_surface is None:
        _build_gradient()
    surface.blit(_gradient_surface, (0, 0))


def draw_text_with_glow(surface, text, font, color, x, y, glow_color=None):
    """Draw text with a compact neon glow effect."""
    if glow_color is None:
        glow_color = color

    glow_surf = font.render(text, True, (*glow_color, 50))
    for offset in range(3, 0, -1):
        surface.blit(glow_surf, (x - offset, y - offset))
        surface.blit(glow_surf, (x + offset, y - offset))
        surface.blit(glow_surf, (x - offset, y + offset))
        surface.blit(glow_surf, (x + offset, y + offset))

    surface.blit(font.render(text, True, color), (x, y))


def draw_health_bar(surface, lives, max_lives=3, font_small=None):
    """Draw the player's remaining lives."""
    bar_width = 150
    bar_height = 20
    x = WIDTH - bar_width - 10
    y = 10

    pygame.draw.rect(surface, (30, 30, 50), (x, y, bar_width, bar_height), border_radius=10)

    health_width = max(0, min(lives, max_lives)) / max_lives * (bar_width - 4)
    for i in range(int(health_width)):
        ratio = i / max(1, bar_width - 4)
        color = tuple(
            int(COLORS["NEON_GREEN"][channel] * ratio + COLORS["NEON_ORANGE"][channel] * (1 - ratio))
            for channel in range(3)
        )
        pygame.draw.line(surface, color, (x + 2 + i, y + 2), (x + 2 + i, y + bar_height - 2))

    pygame.draw.rect(surface, COLORS["NEON_BLUE"], (x, y, bar_width, bar_height), 2, border_radius=10)

    if font_small:
        lives_text = font_small.render(f"Lives: {lives}", True, COLORS["WHITE"])
        surface.blit(lives_text, (x + 5, y + 25))


def draw_score_with_effects(surface, score, high_score, combo, font_medium=None, font_small=None):
    """Draw score, best score, and active combo."""
    if font_medium:
        surface.blit(font_medium.render(f"Score: {score}", True, COLORS["NEON_BLUE"]), (10, 10))

    if font_small:
        surface.blit(font_small.render(f"Best: {high_score}", True, COLORS["NEON_PINK"]), (10, 45))

    if combo > 1 and font_medium:
        combo_surf = font_medium.render(f"Combo x{combo}!", True, COLORS["NEON_YELLOW"])
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5
        surface.blit(combo_surf, (WIDTH // 2 - combo_surf.get_width() // 2, int(10 + pulse)))


def draw_powerup_indicators(surface, player, font_small=None):
    """Show currently active power-ups."""
    if not font_small:
        return

    y_pos = 80
    if player.shield_timer > 0:
        surface.blit(font_small.render("SHIELD", True, COLORS["NEON_GREEN"]), (10, y_pos))
    if player.slow_timer > 0:
        surface.blit(font_small.render("SLOW", True, COLORS["NEON_BLUE"]), (10, y_pos + 25))
    if player.double_points_timer > 0:
        surface.blit(font_small.render("2X", True, COLORS["NEON_YELLOW"]), (10, y_pos + 50))
