import pygame
import random
import math
from settings import WIDTH, HEIGHT, COLORS

class Player:
    """Player with neon glow effect and trail"""
    def __init__(self):
        self.width = 50
        self.height = 70
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 120
        self.speed = 7
        self.trail = []
        self.glow_intensity = 0
        self.has_shield = False
        self.shield_timer = 0
        self.slow_timer = 0
        self.double_points_timer = 0
    
    def move(self, keys):
        base_speed = self.speed
        if self.slow_timer > 0:
            base_speed = self.speed * 0.6
            self.slow_timer -= 1
        
        if keys[pygame.K_LEFT]:
            self.x -= base_speed
        if keys[pygame.K_RIGHT]:
            self.x += base_speed
        
        self.x = max(0, min(self.x, WIDTH - self.width))
        
        # Add trail
        self.trail.append((self.x + self.width//2, self.y + self.height//2))
        if len(self.trail) > 15:
            self.trail.pop(0)
    
    def update_timers(self):
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.has_shield = False
        if self.double_points_timer > 0:
            self.double_points_timer -= 1
    
    def draw(self, surface):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = int(10 * (i / len(self.trail)))
            if size > 0:
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                color = (*COLORS['NEON_BLUE'], alpha//3)
                pygame.draw.circle(s, color, (size, size), size)
                surface.blit(s, (pos[0]-size, pos[1]-size))
        
        # Draw player with glow
        glow_color = COLORS['NEON_BLUE']
        if self.has_shield:
            glow_color = COLORS['NEON_GREEN']
        
        # Glow layers
        for i in range(3, 0, -1):
            glow_size = i * 8
            alpha = 50 - i * 15
            s = pygame.Surface((self.width + glow_size*2, self.height + glow_size*2), pygame.SRCALPHA)
            pygame.draw.rect(s, (*glow_color, alpha), 
                           (glow_size, glow_size, self.width, self.height), 
                           border_radius=10)
            surface.blit(s, (self.x - glow_size, self.y - glow_size))
        
        # Main player
        pygame.draw.rect(surface, glow_color, 
                        (self.x, self.y, self.width, self.height), 
                        border_radius=8)
        pygame.draw.rect(surface, COLORS['BG_DARK'], 
                        (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 
                        border_radius=6)
        
        # Shield effect
        if self.has_shield:
            shield_size = max(self.width, self.height) + 20 + math.sin(pygame.time.get_ticks() * 0.01) * 5
            pygame.draw.circle(surface, (*COLORS['NEON_GREEN'], 100), 
                             (self.x + self.width//2, self.y + self.height//2), 
                             int(shield_size), 2)
