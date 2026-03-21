import pygame
import random
import math
from settings import WIDTH, HEIGHT, COLORS

class Particle:
    "Floating particles for background effect"
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed_y = random.uniform(0.3, 1.0)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.color = random.choice([
            COLORS['NEON_BLUE'], 
            COLORS['NEON_PINK'], 
            COLORS['NEON_PURPLE']
        ])
        self.alpha = random.randint(50, 150)
    
    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
        if self.x < 0:
            self.x = WIDTH
        if self.x > WIDTH:
            self.x = 0
    
    def draw(self, surface):
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.size, self.size), self.size)
        surface.blit(s, (self.x - self.size, self.y - self.size))

class StarParticle:
    "Background stars"
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.5, 2)
        self.brightness = random.randint(100, 255)
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surface):
        pygame.draw.circle(surface, (self.brightness, self.brightness, self.brightness),
                          (self.x, int(self.y)), self.size)

def screen_shake(intensity):
    "Apply screen shake effect"
    if intensity > 0:
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        return offset_x, offset_y
    return 0, 0
