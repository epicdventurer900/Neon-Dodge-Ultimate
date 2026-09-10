import pygame
import random
import math
from settings import WIDTH, COLORS


class Enemy:
    """Different types of falling enemies."""

    def __init__(self, enemy_type="basic"):
        self.type = enemy_type
        self.width = 50
        self.height = 70

        if enemy_type == "fast":
            self.width = 40
            self.height = 50
            self.speed = random.randint(6, 10)
            self.color = COLORS['NEON_ORANGE']
            self.points = 2
        elif enemy_type == "big":
            self.width = 80
            self.height = 90
            self.speed = random.randint(3, 5)
            self.color = COLORS['NEON_PURPLE']
            self.points = 3
        else:
            self.speed = random.randint(4, 7)
            self.color = COLORS['NEON_PINK']
            self.points = 1

        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height - random.randint(0, 100)
        self.glow = 0

    def update(self, difficulty, delta_scale=1.0, speed_multiplier=1.0):
        """Update enemy position with optional temporary speed reduction."""
        self.y += self.speed * difficulty * speed_multiplier * delta_scale
        self.glow = (self.glow + 0.2 * delta_scale) % (2 * math.pi)

    def draw(self, surface):
        glow_size = int(5 + math.sin(self.glow) * 3)

        s = pygame.Surface(
            (self.width + glow_size * 2, self.height + glow_size * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            s,
            (*self.color, 60),
            (glow_size, glow_size, self.width, self.height),
            border_radius=8,
        )
        surface.blit(s, (self.x - glow_size, self.y - glow_size))

        pygame.draw.rect(
            surface,
            self.color,
            (self.x, self.y, self.width, self.height),
            border_radius=8,
        )
        pygame.draw.rect(
            surface,
            COLORS['BG_DARK'],
            (self.x + 5, self.y + 5, self.width - 10, self.height - 10),
            border_radius=6,
        )
