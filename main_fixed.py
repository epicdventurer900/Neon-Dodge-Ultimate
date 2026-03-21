import pygame
import random
import math
import sys
from settings import WIDTH, HEIGHT, init_fonts, COLORS
from audio import init_audio, boom_sound, powerup_sound, combo_sound, ambient_music
from player import Player
from enemy import Enemy
from powerup import PowerUp
from particles import Particle, StarParticle, screen_shake
from ui import draw_gradient_background, draw_text_with_glow, draw_score_with_effects, draw_health_bar, draw_powerup_indicators

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Dodge - Ultimate")
clock = pygame.time.Clock()

init_fonts()
init_audio()

def main():
    # Force font initialization
    from settings import font_large, font_medium, font_small
    print('Fonts loaded:', font_large is not None, font_medium is not None, font_small is not None)
    
    # Game state
    game_state = "START"  # START, PLAYING, PAUSED, GAME_OVER
    
    # Initialize game objects
    player = Player()
    enemies = []
    powerups = []
    particles = [Particle() for _ in range(30)]
    stars = [StarParticle() for _ in range(50)]
    
    # Game variables
    score = 0
    high_score = 0
    lives = 3
    combo = 0
    combo_timer = 0
    difficulty = 1.0
    enemy_timer = 0
    powerup_timer = 0
    
    # Screen shake
    shake_intensity = 0
    
    # Explosion effect
    explosion = None
    explosion_size = 0
    
    # Music started flag
    music_started = False
    
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if game_state == "START":
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        game_state = "PLAYING"
                        if not music_started:
                            ambient_music.start()
                            music_started = True
                
                elif game_state == "PLAYING":
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        game_state = "PAUSED"
                
                elif game_state == "PAUSED":
                    if event.key == pygame.K_p:
                        game_state = "PLAYING"
                    if event.key == pygame.K_ESCAPE:
                        game_state = "START"
                
                elif game_state == "GAME_OVER":
                    if event.key == pygame.K_r:
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
                        explosion = None
                        explosion_size = 0
                        game_state = "PLAYING"
        
        # Get keys
        keys = pygame.key.get_pressed()
        
        # Apply screen shake
        shake_offset = screen_shake(shake_intensity)
        if shake_intensity > 0:
            shake_intensity = max(0, shake_intensity - 1)
        
        # Draw background
        draw_gradient_background(screen)
        
        # Draw stars
        for star in stars:
            star.update()
            star.draw(screen)
        
        # Draw particles
        for particle in particles:
            particle.update()
            particle.draw(screen)
        
        # Game logic and drawing
        if game_state == "START":
            draw_text_with_glow(screen, "NEON DODGE", font_large, COLORS['NEON_BLUE'], 
                              WIDTH // 2 - 160, HEIGHT // 3, COLORS['NEON_PINK'])
            
            draw_text_with_glow(screen, "ULTIMATE", font_large, COLORS['NEON_PINK'], 
                              WIDTH // 2 - 100, HEIGHT // 3 + 60, COLORS['NEON_BLUE'])
            
            inst1 = font_medium.render("Use LEFT/RIGHT arrows to move", True, COLORS['WHITE'])
            inst2 = font_medium.render("Collect power-ups for advantages", True, COLORS['WHITE'])
            inst3 = font_medium.render("Avoid the falling enemies!", True, COLORS['WHITE'])
            
            screen.blit(inst1, (WIDTH // 2 - inst1.get_width() // 2, HEIGHT // 2 + 20))
            screen.blit(inst2, (WIDTH // 2 - inst2.get_width() // 2, HEIGHT // 2 + 60))
            screen.blit(inst3, (WIDTH // 2 - inst3.get_width() // 2, HEIGHT // 2 + 100))
            
            if pygame.time.get_ticks() % 1000 < 500:
                start_text = font_medium.render("Use LEFT/RIGHT Arrows to Start", True, COLORS['NEON_YELLOW'])
                screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 100))
            
            dev_text = font_small.render("Developed by Shetty", True, COLORS['NEON_GREEN'])
            screen.blit(dev_text, (WIDTH // 2 - dev_text.get_width() // 2, HEIGHT - 50))
            
            if high_score > 0:
                hs_text = font_small.render(f"High Score: {high_score}", True, COLORS['NEON_PURPLE'])
                screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 2 + 160))
        
        elif game_state == "PLAYING":
            player.move(keys)
            player.update_timers()
            
            enemy_timer += 1
            spawn_rate = max(20, 50 - int(difficulty * 10))
            if enemy_timer > spawn_rate:
                enemy_timer = 0
                enemy_type = "basic"
                if difficulty > 1.5 and random.random() < 0.2:
                    enemy_type = "big"
                elif difficulty > 1.0 and random.random() < 0.3:
                    enemy_type = "fast"
                enemies.append(Enemy(enemy_type))
            
            powerup_timer += 1
            if powerup_timer > 500:
                powerup_timer = 0
                if random.random() < 0.3:
                    powerups.append(PowerUp())
            
            difficulty = 1.0 + (score // 50) * 0.2
            
            if combo_timer > 0:
                combo_timer -= 1
            else:
                combo = 0
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.update(difficulty)
                
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                
                if player_rect.colliderect(enemy_rect):
                    if player.has_shield:
                        player.has_shield = False
                        player.shield_timer = 0
                        enemies.remove(enemy)
                        powerup_sound.play()
                        continue
                    
                    boom_sound.play()
                    explosion = (enemy.x + enemy.width // 2, enemy.y + enemy.height // 2)
                    explosion_size = 10
                    shake_intensity = 15
                    
                    enemies.remove(enemy)
                    lives -= 1
                    combo = 0
                    
                    if lives <= 0:
                        if score > high_score:
                            high_score = score
                        game_state = "GAME_OVER"
                    continue
                
                if enemy.y > HEIGHT:
                    enemies.remove(enemy)
                    points = enemy.points
                    if player.double_points_timer > 0:
                        points *= 2
                    score += points
                    combo += 1
                    combo_timer = 120
                    
                    if combo > 1:
                        combo_sound.play()
            
            # Update powerups
            for powerup in powerups[:]:
                powerup.update()
                
                powerup_rect = pygame.Rect(powerup.x - powerup.size, powerup.y - powerup.size, powerup.size * 2, powerup.size * 2)
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
                    
                    powerup_sound.play()
                    continue
                
                if powerup.y > HEIGHT:
                    powerups.remove(powerup)
            
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen)
            
            # Draw powerups
            for powerup in powerups:
                powerup.draw(screen, font_small)
            
            # Draw player
            player.draw(screen)
            
            # Explosion effect
            if explosion:
                if explosion_size < 120:
                    alpha = int(255 * (1 - explosion_size / 120))
                    pygame.draw.circle(screen, (*COLORS['NEON_ORANGE'], alpha), explosion, explosion_size)
                    pygame.draw.circle(screen, (*COLORS['NEON_YELLOW'], alpha // 2), explosion, explosion_size // 2)
                    explosion_size += 8
                else:
                    explosion = None
            
            # UI
            draw_score_with_effects(screen, score, high_score, combo, font_medium, font_small)
            draw_health_bar(screen, lives, font_small=font_small)
            draw_powerup_indicators(screen, player, font_small)
        
        elif game_state == "PAUSED":
            for enemy in enemies:
                enemy.draw(screen)
            player.draw(screen)
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            draw_text_with_glow(screen, "PAUSED", font_large, COLORS['NEON_BLUE'],
                              WIDTH // 2 - 100, HEIGHT // 2 - 30)
            
            resume_text = font_medium.render("Press P to Resume", True, COLORS['WHITE'])
            screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 40))
        
        elif game_state == "GAME_OVER":
            for enemy in enemies:
                enemy.draw(screen)
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text_with_glow(screen, "GAME OVER", font_large, COLORS['NEON_PINK'],
                              WIDTH // 2 - 140, HEIGHT // 3)
            
            final_score = font_medium.render(f"Final Score: {score}", True, COLORS['NEON_BLUE'])
            best_score = font_medium.render(f"Best Score: {high_score}", True, COLORS['NEON_YELLOW'])
            
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
            screen.blit(best_score, (WIDTH // 2 - best_score.get_width() // 2, HEIGHT // 2 + 40))
            
            if pygame.time.get_ticks() % 800 < 400:
                restart_text = font_medium.render("Press R to Restart", True, COLORS['WHITE'])
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
        
        if shake_offset != (0, 0):
            temp_surface = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(temp_surface, shake_offset)
        
        pygame.display.update()
        clock.tick(60)
    
    ambient_music.stop()
    pygame.quit()

if __name__ == '__main__':
    main()
