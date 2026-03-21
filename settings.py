import pygame

# Screen dimensions
WIDTH = 600
HEIGHT = 700

# Colors - Neon aesthetic
COLORS = {
    'BG_DARK': (10, 10, 20),
    'BG_LIGHT': (20, 20, 40),
    'NEON_BLUE': (0, 255, 255),
    'NEON_PINK': (255, 0, 128),
    'NEON_GREEN': (0, 255, 128),
    'NEON_PURPLE': (180, 0, 255),
    'NEON_ORANGE': (255, 128, 0),
    'NEON_YELLOW': (255, 255, 0),
    'WHITE': (255, 255, 255),
    'GRAY': (100, 100, 100)
}

# Global fonts
font_large = None
font_medium = None
font_small = None

def init_fonts():
    """Initialize fonts after pygame.init()"""
    global font_large, font_medium, font_small
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
