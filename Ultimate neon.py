import pygame
import random
import math
import array
import threading
import time

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH = 600
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Dodge - Ultimate")
clock = pygame.time.Clock()

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

# ============ PROCEDURAL AUDIO SYSTEM ============

def create_procedural_sound(frequency, duration, volume=0.3):
    """Create a simple sound using array module (no numpy needed)"""
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        audio_data = array.array('h', [0] * num_samples)
        
        for i in range(num_samples):
            t = i / sample_rate
            # Create a sound with envelope
            wave = math.sin(2 * math.pi * frequency * t)
            
            # Add harmonics for richer sound
            wave += 0.3 * math.sin(2 * math.pi * frequency * 2 * t)
            wave += 0.1 * math.sin(2 * math.pi * frequency * 3 * t)
            
            # Fade out
            if duration > 0.1:
                fade = 1.0 - (i / num_samples)
                wave *= fade
            
            # Convert to 16-bit integer
            sample = int(wave * volume * 32767)
            audio_data[i] = max(-32768, min(32767, sample))
        
        return pygame.mixer.Sound(buffer=audio_data)
    except Exception as e:
        print(f"Sound creation failed: {e}")
        return None

# Create sound effects
boom_sound = create_procedural_sound(80, 0.3, 0.5)
powerup_sound = create_procedural_sound(880, 0.15, 0.3)
combo_sound = create_procedural_sound(660, 0.1, 0.2)

# ============ BACKGROUND MUSIC THREAD ============

class AmbientMusic:
    """Procedural ambient background music"""
    def __init__(self):
        self.running = False
        self.thread = None
        self.notes = [220, 277, 330, 440, 554, 659]  # A3, C#4, E4, A4, C#5, E5
        self.current_note = 0
        self.note_duration = 0.5
        self.last_change = 0
    
    def play_note(self, freq, duration):
        """Play a single ambient note"""
        try:
            sample_rate = 22050
            num_samples = int(sample_rate * duration)
            audio_data = array.array('h', [0] * num_samples)
            
            for i in range(num_samples):
                t = i / sample_rate
                # Soft sine wave with envelope
                wave = math.sin(2 * math.pi * freq * t)
                wave += 0.5 * math.sin(2 * math.pi * freq * 2 * t)
                
                # Smooth envelope
                attack = min(i / (sample_rate * 0.05), 1.0)
                release = 1.0 - min((i - num_samples * 0.7) / (sample_rate * 0.3), 1.0)
                wave *= attack * release * 0.15
                
                sample = int(wave * 32767)
                audio_data[i] = max(-32768, min(32767, sample))
            
            sound = pygame.mixer.Sound(buffer=audio_data)
            sound.play()
        except:
            pass
    
    def start(self):
        """Start ambient music"""
        self.running = True
        self.thread = threading.Thread(target=self._music_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop ambient music"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _music_loop(self):
        """Background music loop"""
        import time
        while self.running:
            if pygame.mixer.get_init():
                # Play ambient chord
                note = self.notes[self.current_note]
                self.play_note(note, 1.5)
                self.play_note(note * 1.5, 1.5)  # Fifth
                
                self.current_note = (self.current_note + 1) % len(self.notes)
                time.sleep(1.5)
    
    def set_volume(self, vol):
        pass

# Create and start music
ambient_music = AmbientMusic()

# Font setup
font_large = pygame.font.SysFont("arial", 60, bold=True)
font_medium = pygame.font.SysFont("arial", 32)
font_small = pygame.font.SysFont("arial", 24)

# ============= CLASSES =============

class Particle:
    """Floating particles for background effect"""
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


class Enemy:
    """Different types of enemies"""
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
        else:  # basic
            self.speed = random.randint(4, 7)
            self.color = COLORS['NEON_PINK']
            self.points = 1
        
        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height - random.randint(0, 100)
        self.glow = 0
    
    def update(self, difficulty):
        self.y += self.speed * difficulty
        self.glow = (self.glow + 0.2) % (2 * math.pi)
    
    def draw(self, surface):
        glow_size = int(5 + math.sin(self.glow) * 3)
        
        # Glow
        s = pygame.Surface((self.width + glow_size*2, self.height + glow_size*2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*self.color, 60), 
                        (glow_size, glow_size, self.width, self.height), 
                        border_radius=8)
        surface.blit(s, (self.x - glow_size, self.y - glow_size))
        
        # Main enemy
        pygame.draw.rect(surface, self.color, 
                        (self.x, self.y, self.width, self.height), 
                        border_radius=8)
        pygame.draw.rect(surface, COLORS['BG_DARK'], 
                        (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 
                        border_radius=6)


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
    
    def update(self):
        self.y += self.speed
        self.angle += 0.1
    
    def draw(self, surface):
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


class StarParticle:
    """Background stars"""
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


# ============= GAME FUNCTIONS =============

def draw_gradient_background(surface):
    """Draw animated gradient background"""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(COLORS['BG_DARK'][0] + (COLORS['BG_LIGHT'][0] - COLORS['BG_DARK'][0]) * ratio)
        g = int(COLORS['BG_DARK'][1] + (COLORS['BG_LIGHT'][1] - COLORS['BG_DARK'][1]) * ratio)
        b = int(COLORS['BG_DARK'][2] + (COLORS['BG_LIGHT'][2] - COLORS['BG_DARK'][2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_text_with_glow(surface, text, font, color, x, y, glow_color=None):
    """Draw text with neon glow effect"""
    if glow_color is None:
        glow_color = color
    
    # Glow layers
    for i in range(3, 0, -1):
        glow_surf = font.render(text, True, (*glow_color, 50))
        surface.blit(glow_surf, (x - i, y - i))
        surface.blit(glow_surf, (x + i, y - i))
        surface.blit(glow_surf, (x - i, y + i))
        surface.blit(glow_surf, (x + i, y + i))
    
    # Main text
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, (x, y))


def draw_health_bar(surface, lives, max_lives=3):
    """Draw lives/health indicator"""
    bar_width = 150
    bar_height = 20
    x = WIDTH - bar_width - 10
    y = 10
    
    # Background
    pygame.draw.rect(surface, (30, 30, 50), (x, y, bar_width, bar_height), border_radius=10)
    
    # Health
    health_width = (lives / max_lives) * (bar_width - 4)
    for i in range(int(health_width)):
        ratio = i / bar_width
        color = (
            int(COLORS['NEON_GREEN'][0] * ratio + COLORS['NEON_ORANGE'][0] * (1 - ratio)),
            int(COLORS['NEON_GREEN'][1] * ratio + COLORS['NEON_ORANGE'][1] * (1 - ratio)),
            int(COLORS['NEON_GREEN'][2] * ratio + COLORS['NEON_ORANGE'][2] * (1 - ratio))
        )
        pygame.draw.line(surface, color, (x + 2 + i, y + 2), (x + 2 + i, y + bar_height - 2))
    
    # Border
    pygame.draw.rect(surface, COLORS['NEON_BLUE'], (x, y, bar_width, bar_height), 2, border_radius=10)
    
    # Lives text
    lives_text = font_small.render(f"Lives: {lives}", True, COLORS['WHITE'])
    surface.blit(lives_text, (x + 5, y + 25))


def draw_score_with_effects(surface, score, high_score, combo):
    """Draw score with effects"""
    # Main score
    score_surf = font_medium.render(f"Score: {score}", True, COLORS['NEON_BLUE'])
    surface.blit(score_surf, (10, 10))
    
    # High score
    hs_surf = font_small.render(f"Best: {high_score}", True, COLORS['NEON_PINK'])
    surface.blit(hs_surf, (10, 45))
    
    # Combo
    if combo > 1:
        combo_surf = font_medium.render(f"Combo x{combo}!", True, COLORS['NEON_YELLOW'])
        # Pulsing effect
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5
        surface.blit(combo_surf, (WIDTH // 2 - combo_surf.get_width() // 2, 10 + pulse))


def draw_powerup_indicators(surface, player):
    """Show active power-ups"""
    y_pos = 80
    
    if player.shield_timer > 0:
        shield_surf = font_small.render("SHIELD", True, COLORS['NEON_GREEN'])
        alpha = min(255, player.shield_timer * 5)
        s = pygame.Surface(shield_surf.get_size(), pygame.SRCALPHA)
        s.blit(shield_surf, (0, 0))
        s.fill((0, 0, 0, 255 - alpha), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(s, (10, y_pos))
    
    if player.slow_timer > 0:
        slow_surf = font_small.render("SLOW", True, COLORS['NEON_BLUE'])
        surface.blit(slow_surf, (10, y_pos + 25))
    
    if player.double_points_timer > 0:
        double_surf = font_small.render("2X", True, COLORS['NEON_YELLOW'])
        surface.blit(double_surf, (10, y_pos + 50))


def screen_shake(intensity):
    """Apply screen shake effect"""
    if intensity > 0:
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        return offset_x, offset_y
    return 0, 0


# ============= MAIN GAME =============

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
        shake_offset = (0, 0)
        if shake_intensity > 0:
            shake_offset = screen_shake(shake_intensity)
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
                            try:
                                powerup_sound.play()
                            except:
                                pass
                        continue
                    
                    # Hit!
                    if boom_sound:
                        try:
                            boom_sound.play()
                        except:
                            pass
                    
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
                        try:
                            combo_sound.play()
                        except:
                            pass
            
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
                        try:
                            powerup_sound.play()
                        except:
                            pass
                    
                    continue
                
                if powerup.y > HEIGHT:
                    powerups.remove(powerup)
            
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen)
            
            # Draw powerups
            for powerup in powerups:
                powerup.draw(screen)
            
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
            draw_score_with_effects(screen, score, high_score, combo)
            draw_health_bar(screen, lives)
            draw_powerup_indicators(screen, player)
        
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
        
        # Apply screen shake
        if shake_offset != (0, 0):
            # Create a temporary surface for shake effect
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
