import pygame
import math
from settings import WIDTH, HEIGHT, COLORS


class Player:
    """Player with neon glow, trail, and temporary power-ups."""

    def __init__(self):
        self.width = 50
        self.height = 70
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 120
        self.speed = 7
        self.trail = []
        self.has_shield = False
        self.shield_timer = 0
        self.slow_timer = 0
        self.double_points_timer = 0

    def move(self, keys, delta_scale=1.0):
        """Move the player. The SLOW power-up affects enemies, not the player."""
        if keys[pygame.K_LEFT]:
            self.x -= self.speed * delta_scale
        if keys[pygame.K_RIGHT]:
            self.x += self.speed * delta_scale

        self.x = max(0, min(self.x, WIDTH - self.width))

        self.trail.append((self.x + self.width // 2, self.y + self.height // 2))
        if len(self.trail) > 15:
            self.trail.pop(0)

    def update_timers(self, delta_scale=1.0):
        if self.shield_timer > 0:
            self.shield_timer = max(0, self.shield_timer - delta_scale)
            if self.shield_timer == 0:
                self.has_shield = False

        if self.slow_timer > 0:
            self.slow_timer = max(0, self.slow_timer - delta_scale)

        if self.double_points_timer > 0:
            self.double_points_timer = max(0, self.double_points_timer - delta_scale)

    def draw(self, surface):
        # Draw trail
        trail_length = len(self.trail)
        for i, pos in enumerate(self.trail):
            alpha = int(255 * ((i + 1) / max(1, trail_length)))
            size = int(10 * ((i + 1) / max(1, trail_length)))
            if size > 0:
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color = (*COLORS['NEON_BLUE'], alpha // 3)
                pygame.draw.circle(s, color, (size, size), size)
                surface.blit(s, (pos[0] - size, pos[1] - size))

        glow_color = COLORS['NEON_GREEN'] if self.has_shield else COLORS['NEON_BLUE']

        # Glow layers
        for i in range(3, 0, -1):
            glow_size = i * 8
            alpha = 50 - i * 15
            s = pygame.Surface(
                (self.width + glow_size * 2, self.height + glow_size * 2),
                pygame.SRCALPHA,
            )
            pygame.draw.rect(
                s,
                (*glow_color, alpha),
                (glow_size, glow_size, self.width, self.height),
                border_radius=10,
            )
            surface.blit(s, (self.x - glow_size, self.y - glow_size))

        pygame.draw.rect(
            surface,
            glow_color,
            (self.x, self.y, self.width, self.height),
            border_radius=8,
        )
        pygame.draw.rect(
            surface,
            COLORS['BG_DARK'],
            (self.x + 5, self.y + 5, self.width - 10, self.height - 10),
            border_radius=6,
        )

        if self.has_shield:
            shield_size = max(self.width, self.height) + 20 + math.sin(
                pygame.time.get_ticks() * 0.01
            ) * 5
            pygame.draw.circle(
                surface,
                (*COLORS['NEON_GREEN'], 100),
                (self.x + self.width // 2, self.y + self.height // 2),
                int(shield_size),
                2,
            )
