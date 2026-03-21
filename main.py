import pygame
import random
import math
import sys
from settings import WIDTH, HEIGHT, init_fonts, font_large, font_medium, font_small, COLORS
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
                        # Start ambient music when game begins
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
                        # Reset game
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
        
        # ============= START SCREEN =============
        if game_state == "START":
            # Title
            draw_text_with_glow(screen, "NEON DODGE", font_large, COLORS['NEON_BLUE'], 
                              WIDTH // 2 - 160, HEIGHT // 3, COLORS['NEON_PINK'])
            
            draw_text_with_glow(screen, "ULTIMATE", font_large, COLORS['NEON_PINK'], 
                              WIDTH // 2 - 100, HEIGHT // 3 + 60, COLORS['NEON_BLUE'])
            
            # Instructions
            inst1 = font_medium.render("Use LEFT/RIGHT arrows to move", True, COLORS['WHITE'])
            inst2 = font_medium.render("Collect power-ups for advantages", True, COLORS['WHITE'])
            inst3 = font_medium.render("Avoid the falling enemies!", True, COLORS['WHITE'])
            
            screen.blit(inst1, (WIDTH // 2 - inst1.get_width() // 2, HEIGHT // 2 + 20))
            screen.blit(inst2, (WIDTH // 2 - inst2.get_width() // 2, HEIGHT // 2 + 60))
            screen.blit(inst3, (WIDTH // 2 - inst3.get_width() // 2, HEIGHT // 2 + 100))
            
            # Start prompt
            if pygame.time.get_ticks() % 1000 < 500:
                start_text = font_medium.render("Use LEFT/RIGHT Arrows to Start", True, COLORS['NEON_YELLOW'])
                screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 100))
            
            # Developer Credits
            dev_text = font_small.render("Developed by Shetty", True, COLORS['NEON_GREEN'])
            screen.blit(dev_text, (WIDTH // 2 - dev_text.get_width() // 2, HEIGHT - 50))
            
            # High score
            if high_score > 0:
                hs_text = font_small.render(f"High Score: {high_score}", True, COLORS['NEON_PURPLE'])
                screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 2 + 160))
        
        # ============= PLAYING STATE =============
        elif game_state == "PLAYING":
            # Player movement
            player.move(keys)
            player.update_timers()
            
            # Spawn enemies
            enemy_timer += 1
            spawn_rate = max(20, 50 - int(difficulty * 10))
            if enemy_timer > spawn_rate:
                enemy_timer = 0
                # Random enemy type based on difficulty
                if difficulty > 1.5 and random.random() < 0.2:
                    enemy_type = "big"
                elif difficulty > 1.0 and random.random() < 0.3:
                    enemy_type = "fast"
                else:
                    enemy_type = "basic"
                enemies.append(Enemy(enemy_type))
            
            # Spawn powerups
            powerup_timer += 1
            if powerup_timer > 500:
                powerup_timer = 0
                if random.random() < 0.3:
                    powerups.append(PowerUp())
            
            # Update difficulty
            difficulty = 1.0 + (score // 50) * 0.2
            
            # Combo timer
            if combo_timer > 0:
                combo_timer -= 1
            else:
                combo = 0
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.update(difficulty)
                
                # Check collision with player
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                
                if player_rect.colliderect(enemy_rect):
                    if player.has_shield:
                        # Shield protects once
                        player.has_shield = False
                        player.shield_timer = 0
                        enemies.remove(enemy)
                        if powerup_sound:
                            powerup_sound.play()
                        continue
                    
                    # Hit!
                    if boom_sound:
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
                
                # Enemy passed bottom
                if enemy.y > HEIGHT:
                    enemies.remove(enemy)
                    points = enemy.points
                    if player.double_points_timer > 0:
                        points *= 2
                    score += points
                    combo += 1
                    combo_timer = 120
                    
                    if combo_sound and combo > 1:
                        combo_sound.play()
            
            # Update powerups
            for powerup in powerups[:]:
                powerup.update()
                
                # Check collision
                powerup_rect = pygame.Rect(powerup.x - powerup.size, powerup.y - powerup.size,
                                          powerup.size * 2, powerup.size * 2)
                player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                
                if player_rect.colliderect(powerup_rect):
                    powerups.remove(powerup)
                    
                    if powerup.type == "shield":
                        player.has_shield = True
                        player.shield_timer = 600  # 10 seconds at 60 FPS
                    elif powerup.type == "slow":
                        player.slow_timer = 300  # 5 seconds
                    elif powerup.type == "double":
                        player.double_points_timer = 480  # 8 seconds
                    
                    if powerup_sound:
                        powerup_sound.play()
                    
                    continue
                
                if powerup.y > HEIGHT:
                    powerups.remove(powerup)
            
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen)
            
            # Draw powerups (pass font_small)
            for powerup in powerups:
                powerup.draw(screen, font_small)
            
            # Draw player
            player.draw(screen)
            
            # Explosion effect
            if explosion:
                if explosion_size < 120:
                    alpha = int(255 * (1 - explosion_size / 120))
                    pygame.draw.circle(screen, (*COLORS['NEON_ORANGE'], alpha),
                                      explosion, explosion_size)
                    pygame.draw.circle(screen, (*COLORS['NEON_YELLOW'], alpha // 2),
                                      explosion, explosion_size // 2)
                    explosion_size += 8
                else:
                    explosion = None
            
            # UI
            draw_score_with_effects(screen, score, high_score, combo, font_medium, font_small)
            draw_health_bar(screen, lives, font_small=font_small)
            draw_powerup_indicators(screen, player, font_small)
        
        # ============= PAUSED STATE =============
        elif game_state == "PAUSED":
            # Draw game behind
            for enemy in enemies:
                enemy.draw(screen)
            player.draw(screen)
            
            # Pause overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            draw_text_with_glow(screen, "PAUSED", font_large, COLORS['NEON_BLUE'],
                              WIDTH // 2 - 100, HEIGHT // 2 - 30)
            
            resume_text = font_medium.render("Press P to Resume", True, COLORS['WHITE'])
            screen.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 40))
        
        # ============= GAME OVER STATE =============
        elif game_state == "GAME_OVER":
            # Draw game behind
            for enemy in enemies:
                enemy.draw(screen)
            
            # Game over overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text_with_glow(screen, "GAME OVER", font_large, COLORS['NEON_PINK'],
                              WIDTH // 2 - 140, HEIGHT // 3)
            
            # Stats
            final_score = font_medium.render(f"Final Score: {score}", True, COLORS['NEON_BLUE'])
            best_score = font_medium.render(f"Best Score: {high_score}", True, COLORS['NEON_YELLOW'])
            
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
            screen.blit(best_score, (WIDTH // 2 - best_score.get_width() // 2, HEIGHT // 2 + 40))
            
            # Restart prompt
            if pygame.time.get_ticks() % 800 < 400:
                restart_text = font_medium.render("Press R to Restart", True, COLORS['WHITE'])
                screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
        
        # Apply screen shake (post-draw)
        if shake_offset != (0, 0):
            temp_surface = screen.copy()
            screen.fill((0, 0, 0))
            screen.blit(temp_surface, shake_offset)
        
        # Update display
        pygame.display.update()
        clock.tick(60)
    
    # Clean up
    ambient_music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
