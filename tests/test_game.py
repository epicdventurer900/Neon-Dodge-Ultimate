import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from enemy import Enemy
from player import Player
from powerup import PowerUp
from settings import HEIGHT, WIDTH, init_fonts


class GameComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_fonts()

    def test_player_stays_inside_screen(self):
        player = Player()
        player.x = -100
        player.move(pygame.key.get_pressed(), 1.0)
        self.assertGreaterEqual(player.x, 0)

        player.x = WIDTH + 100
        player.move(pygame.key.get_pressed(), 1.0)
        self.assertLessEqual(player.x, WIDTH - player.width)

    def test_enemy_updates_with_slow_multiplier(self):
        enemy = Enemy("basic")
        start_y = enemy.y
        enemy.update(1.0, 1.0, 0.5)
        self.assertGreater(enemy.y, start_y)

    def test_enemy_types_have_expected_points(self):
        self.assertEqual(Enemy("basic").points, 1)
        self.assertEqual(Enemy("fast").points, 2)
        self.assertEqual(Enemy("big").points, 3)

    def test_powerup_spawns_above_screen(self):
        powerup = PowerUp()
        self.assertEqual(powerup.y, -30)
        self.assertTrue(powerup.type in {"shield", "slow", "double"})

    def test_headless_surface_can_render(self):
        surface = pygame.Surface((WIDTH, HEIGHT))
        player = Player()
        player.draw(surface)
        enemy = Enemy("basic")
        enemy.draw(surface)


if __name__ == "__main__":
    unittest.main()
