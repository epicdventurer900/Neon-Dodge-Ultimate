import pygame
import random
import math
from settings import WIDTH, HEIGHT, COLORS

class PowerUp:
    """Power-up items"""
    def __init__(self):
        self.types = ["shield", "slow", "double"]
        self.type = random.choice(self.types)
        self.size = 30
        self.x = random.randint(30, WIDTH - 30)
        self.y = -30
        self.speed = 3
        
        if self.type == "shield":
            self.color = COLORS['NEON_GREEN']
            self.symbol = "S"
        elif self.type == "slow":
            self.color = COLORS['NEON_BLUE']
            self.symbol = "T"
        else:
            self.color = COLORS['NEON_YELLOW']
            self.symbol = "2X"
        
        self.angle = 0
    
    def update(self, delta_scale=1.0):
        self.y += self.speed * delta_scale
        self.angle += 0.1 * delta_scale
    
    def draw(self, surface, font_small):
        # Pulsing effect
        pulse = math.sin(self.angle) * 3
        
        # Glow
        pygame.draw.circle(surface, (*self.color, 100), 
                         (self.x, self.y), self.size + pulse + 5)
        
        # Main circle
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)
        pygame.draw.circle(surface, COLORS['BG_DARK'], (self.x, self.y), self.size - 5)
        
        # Symbol
        symbol_surf = font_small.render(self.symbol, True, self.color)
        surface.blit(symbol_surf, 
                    (self.x - symbol_surf.get_width()//2, 
                     self.y - symbol_surf.get_height()//2))
