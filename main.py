import pygame
import random
import json
import os

from settings import WIDTH, HEIGHT, init_fonts, COLORS
import audio
from player import Player
from enemy import Enemy
from powerup import PowerUp
from particles import Particle, StarParticle, screen_shake
from ui import (
    draw_gradient_background,
    draw_text_with_glow,
    draw_score_with_effects,
    draw_health_bar,
    draw_powerup_indicators,
)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Dodge - Ultimate")
clock = pygame.time.Clock()
HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_score.json")
FRAME_RATE = 60

init_fonts()
from settings import font_large, font_medium, font_small  # noqa: E402

audio.init_audio()


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as score_file:
            return max(0, int(json.load(score_file).get("high_score", 0)))
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as score_file:
            json.dump({"high_score": max(0, int(score))}, score_file)
    except (OSError, TypeError, ValueError) as error:
        print(f"High score could not be saved: {error}")


def main():
    global screen

    game_state = "START"
    player = Player()
    enemies = []
    powerups = []
    particles = [Particle() for _ in range(30)]
    stars = [StarParticle() for _ in range(50)]

    score = 0
    high_score = load_high_score()
    lives = 3
    combo = 0
    combo_timer = 0
    difficulty = 1.0
    enemy_timer = 0
    powerup_timer = 0
    shake_intensity = 0
    explosion = None
    explosion_size = 0
    music_started = False
    audio_enabled = pygame.mixer.get_init() is not None
    running = True

    while running:
        delta_scale = min(clock.tick(FRAME_RATE) / (1000 / FRAME_RATE), 3.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_m:
                    audio_enabled = not audio_enabled
                    if not audio_enabled and pygame.mixer.get_init():
                        pygame.mixer.stop()
                    elif audio_enabled and music_started and audio.ambient_music:
                        audio.ambient_music.start()

                elif event.key == pygame.K_F11:
                    if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

                elif game_state == "START" and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    game_state = "PLAYING"
                    if not music_started:
                        if audio_enabled and audio.ambient_music:
                            audio.ambient_music.start()
                        music_started = True

                elif game_state == "PLAYING" and event.key == pygame.K_p:
                    game_state = "PAUSED"

                elif game_state == "PAUSED" and event.key == pygame.K_p:
                    game_state = "PLAYING"

                elif game_state == "GAME_OVER" and event.key == pygame.K_r:
                    player = Player()
                    enemies.clear()
                    powerups.clear()
                    particles = [Particle() for _ in range(30)]
                    stars = [StarParticle() for _ in range(50)]
                    score = 0
                    lives = 3
                    combo = 0
                    combo_timer = 0
                    difficulty = 1.0
                    enemy_timer = 0
                    powerup_timer = 0
                    shake_intensity = 0
                    explosion = None
                    explosion_size = 0
                    game_state = "PLAYING"

        keys = pygame.key.get_pressed()
        shake_offset = screen_shake(shake_intensity)
        if shake_intensity > 0:
            shake_intensity = max(0, shake_intensity - 1)

        draw_gradient_background(screen)

        for star in stars:
            star.update(delta_scale)
            star.draw(screen)

        for particle in particles:
            particle.update(delta_scale)
            particle.draw(screen)

        if game_state == "START":
            draw_text_with_glow(screen, "NEON DODGE", font_large, COLORS["NEON_BLUE"],
                                WIDTH // 2 - 160, HEIGHT // 3, COLORS["NEON_PINK"])
            draw_text_with_glow(screen, "ULTIMATE", font_large, COLORS["NEON_PINK"],
                                WIDTH // 2 - 100, HEIGHT // 3 + 60, COLORS["NEON_BLUE"])

            inst1 = font_medium.render("Use LEFT/RIGHT arrows to move", True, COLORS["WHITE"])
            inst2 = font_medium.render("Collect power-ups for advantages", True, COLORS["WHITE"])
            inst3 = font_medium.render("Avoid the falling enemies!", True, COLORS["WHITE"])
            screen.blit(inst1, (WIDTH // 2 - inst1.get_width() // 2, HEIGHT // 2 + 20))
            screen.blit(inst2, (WIDTH // 2 - inst2.get_width() // 2, HEIGHT // 2 + 60))
            screen.blit(inst3, (WIDTH // 2 - inst3.get_width() // 2, HEIGHT // 2 + 100))

            if pygame.time.get_ticks() % 1000 < 500:
                start_text = font_medium.render("Use LEFT/RIGHT Arrows to Start", True, COLORS["NEON_YELLOW"])
                screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 100))

            dev_text = font_small.render("Developed by Shetty", True, COLORS["NEON_GREEN"])
            screen.blit(dev_text, (WIDTH // 2 - dev_text.get_width() // 2, HEIGHT - 50))

            if high_score > 0:
                hs_text = font_small.render(f"High Score: {high_score}", True, COLORS["NEON_PURPLE"])
                screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 2 + 160))

        elif game_state == "PLAYING":
            player.move(keys, delta_scale)
            player.update_timers(delta_scale)

            enemy_timer += delta_scale
            spawn_rate = max(20, 50 - int(difficulty * 10))
            if enemy_timer > spawn_rate:
                enemy_timer = 0
                if difficulty > 1.5 and random.random() < 0.2:
                    enemy_type = "big"
                elif difficulty > 1.0 and random.random() < 0.3:
                    enemy_type = "fast"
                else:
                    enemy_type = "basic"
                enemies.append(Enemy(enemy_type))

            powerup_timer += delta_scale
            if powerup_timer > 500:
                powerup_timer = 0
                if random.random() < 0.3:
                    powerups.append(PowerUp())

            difficulty = 1.0 + (score // 50) * 0.2

            if combo_timer > 0:
                combo_timer = max(0, combo_timer - delta_scale)
            else:
                combo = 0

            enemy_speed_multiplier = 0.55 if player.slow_timer > 0 else 1.0

            for enemy in enemies[:]:
                enemy.update(difficulty, delta_scale, enemy_speed_multiplier)

                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

                if player_rect.colliderect(enemy_rect):
                    if player.has_shield:
                        player.has_shield = False
                        player.shield_timer = 0
                        enemies.remove(enemy)
                        if audio_enabled and audio.powerup_sound:
                            audio.powerup_sound.play()
                        continue

                    if audio_enabled and audio.boom_sound:
                        audio.boom_sound.play()

                    explosion = (enemy.x + enemy.width // 2, enemy.y + enemy.height // 2)
                    explosion_size = 10
                    shake_intensity = 15
                    enemies.remove(enemy)
                    lives -= 1
                    combo = 0

                    if lives <= 0:
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                        game_state = "GAME_OVER"
                    continue

                if enemy.y > HEIGHT:
                    enemies.remove(enemy)
                    points = enemy.points * (2 if player.double_points_timer > 0 else 1)
                    score += points
                    combo += 1
                    combo_timer = 120
                    if audio_enabled and audio.combo_sound and combo > 1:
                        audio.combo_sound.play()

            for powerup in powerups[:]:
                powerup.update(delta_scale)
                powerup_rect = pygame.Rect(
                    powerup.x - powerup.size,
                    powerup.y - powerup.size,
                    powerup.size * 2,
                    powerup.size * 2,
                )
                player_rect = pygame.Rect(player.x, player.y, player.width, player.height)

                if player_rect.colliderect(powerup_rect):
                    powerups.remove(powerup)
                    if powerup.type == "shield":
                        player.has_shield = True
                        player.shield_timer = 600
                    elif powerup.type == "slow":
                        player.slow_timer = 300
                    elif powerup.type == "double":
                        player.double_points_timer = 480

                    if audio_enabled and audio.powerup_sound:
                        audio.powerup_sound.play()
                    continue

                if powerup.y > HEIGHT:
                    powerups.remove(powerup)

            for enemy in enemies:
                enemy.draw(screen)
            for powerup in powerups:
                powerup.draw(screen, font_small)
            player.draw(screen)

            if explosion:
                if explosion_size < 120:
                    alpha = int(255 * (1 - explosion_size / 120))
                    pygame.draw.circle(screen, (*COLORS["NEON_ORANGE"], alpha), explosion, int(explosion_size))
                    pygame.draw.circle(screen, (*COLORS["NEON_YELLOW"], alpha // 2), explosion,
                                       max(1, int(explosion_size // 2)))
                    explosion_size += 8 * delta_scale
                else:
                    explosion = None

            draw_score_with_effects(screen, score, high_score, combo, font_medium, font_small)
            draw_health_bar(screen, lives, font_small=font_small)
            draw_powerup_indicators(screen, player, font_small)

        elif game_state == "PAUSED":
            for enemy in enemies:
                enemy.draw(screen)
            for powerup in powerups:
                powerup.draw(screen, font_small)
            player.draw(screen)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text_with_glow(screen, "PAUSED", font_large, COLORS["NEON_BLUE"],
                                WIDTH // 2 - 100, HEIGHT // 2 - 30)
            resume_text = font_medium.render("Press P to Resume", True, COLORS["WHITE"])
            screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 40))

        elif game_state == "GAME_OVER":
            for enemy in enemies:
                enemy.draw(screen)
            player.draw(screen)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text_with_glow(screen, "GAME OVER", font_large, COLORS["NEON_PINK"],
                                WIDTH // 2 - 140, HEIGHT // 3)

            final_score = font_medium.render(f"Final Score: {score}", True, COLORS["NEON_BLUE"])
            best_score = font_medium.render(f"Best Score: {high_score}", True, COLORS["NEON_YELLOW"])
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
            screen.blit(best_score, (WIDTH // 2 - best_score.get_width() // 2, HEIGHT // 2 + 40))

            if pygame.time.get_ticks() % 800 < 400:
                restart_text = font_medium.render("Press R to Restart", True, COLORS["WHITE"])
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))

        if shake_offset != (0, 0):
            temp_surface = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(temp_surface, shake_offset)

        pygame.display.flip()

    if score > high_score:
        save_high_score(score)

    audio.stop_ambient()
    pygame.quit()


if __name__ == "__main__":
    main()
