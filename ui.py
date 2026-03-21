import pygame
import math
import random
from settings import WIDTH, HEIGHT, COLORS

def draw_gradient_background(surface):
    "Draw animated gradient background"
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(COLORS['BG_DARK'][0] + (COLORS['BG_LIGHT'][0] - COLORS['BG_DARK'][0]) * ratio)
        g = int(COLORS['BG_DARK'][1] + (COLORS['BG_LIGHT'][1] - COLORS['BG_DARK'][1]) * ratio)
        b = int(COLORS['BG_DARK'][2] + (COLORS['BG_LIGHT'][2] - COLORS['BG_DARK'][2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_text_with_glow(surface, text, font, color, x, y, glow_color=None):
    "Draw text with neon glow effect"
    if glow_color is None:
        glow_color = color
    
    # Glow layers
    for i in range(3, 0, -1):
        glow_surf = font.render(text, True, (*glow_color, 50))
        surface.blit(glow_surf, (x - i, y - i))
        surface.blit(glow_surf, (x + i, y - i))
        surface.blit(glow_surf, (x - i, y + i))
        surface.blit(glow_surf, (x + i, y + i))
    
    # Main text
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, (x, y))

def draw_health_bar(surface, lives, max_lives=3, font_small=None):
    "Draw lives/health indicator"
    bar_width = 150
    bar_height = 20
    x = WIDTH - bar_width - 10
    y = 10
    
    # Background
    pygame.draw.rect(surface, (30, 30, 50), (x, y, bar_width, bar_height), border_radius=10)
    
    # Health
    health_width = (lives / max_lives) * (bar_width - 4)
    for i in range(int(health_width)):
        ratio = i / bar_width
        color = (
            int(COLORS['NEON_GREEN'][0] * ratio + COLORS['NEON_ORANGE'][0] * (1 - ratio)),
            int(COLORS['NEON_GREEN'][1] * ratio + COLORS['NEON_ORANGE'][1] * (1 - ratio)),
            int(COLORS['NEON_GREEN'][2] * ratio + COLORS['NEON_ORANGE'][2] * (1 - ratio))
        )
        pygame.draw.line(surface, color, (x + 2 + i, y + 2), (x + 2 + i, y + bar_height - 2))
    
    # Border
    pygame.draw.rect(surface, COLORS['NEON_BLUE'], (x, y, bar_width, bar_height), 2, border_radius=10)
    
    # Lives text
    if font_small:
        lives_text = font_small.render(f"Lives: {lives}", True, COLORS['WHITE'])
        surface.blit(lives_text, (x + 5, y + 25))

def draw_score_with_effects(surface, score, high_score, combo, font_medium=None, font_small=None):
    "Draw score with effects"
    # Main score
    if font_medium:
        score_surf = font_medium.render(f"Score: {score}", True, COLORS['NEON_BLUE'])
        surface.blit(score_surf, (10, 10))
    
    # High score
    if font_small:
        hs_surf = font_small.render(f"Best: {high_score}", True, COLORS['NEON_PINK'])
        surface.blit(hs_surf, (10, 45))
    
    # Combo
    if combo > 1 and font_medium:
        combo_surf = font_medium.render(f"Combo x{combo}!", True, COLORS['NEON_YELLOW'])
        # Pulsing effect
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5
        surface.blit(combo_surf, (WIDTH // 2 - combo_surf.get_width() // 2, 10 + pulse))

def draw_powerup_indicators(surface, player, font_small=None):
    "Show active power-ups"
    y_pos = 80
    
    if player.shield_timer > 0:
        if font_small:
            shield_surf = font_small.render("SHIELD", True, COLORS['NEON_GREEN'])
            alpha = min(255, player.shield_timer * 5)
            s = pygame.Surface(shield_surf.get_size(), pygame.SRCALPHA)
            s.blit(shield_surf, (0, 0))
            s.fill((0, 0, 0, 255 - alpha), special_flags=pygame.BLEND_RGBA_SUB)
            surface.blit(s, (10, y_pos))
    
    if player.slow_timer > 0 and font_small:
        slow_surf = font_small.render("SLOW", True, COLORS['NEON_BLUE'])
        surface.blit(slow_surf, (10, y_pos + 25))
    
    if player.double_points_timer > 0 and font_small:
        double_surf = font_small.render("2X", True, COLORS['NEON_YELLOW'])
        surface.blit(double_surf, (10, y_pos + 50))
