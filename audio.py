import pygame
import random
import math
import array
import threading
import time

pygame.mixer.init()

# Global sounds
boom_sound = None
powerup_sound = None
combo_sound = None
ambient_music = None

def create_procedural_sound(frequency, duration, volume=0.3):
    "Create a simple sound using array module (no numpy needed)"
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

class AmbientMusic:
    "Procedural ambient background music"
    def __init__(self):
        self.running = False
        self.thread = None
        self.notes = [220, 277, 330, 440, 554, 659]  # A3, C#4, E4, A4, C#5, E5
        self.current_note = 0
        self.note_duration = 0.5
        self.last_change = 0
    
    def play_note(self, freq, duration):
        "Play a single ambient note"
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
        while self.running:
            if pygame.mixer.get_init():
                # Play ambient chord
                note = self.notes[self.current_note]
                self.play_note(note, 1.5)
                self.play_note(note * 1.5, 1.5)  # Fifth
                
                self.current_note = (self.current_note + 1) % len(self.notes)
                time.sleep(1.5)

def init_audio():
    """Initialize all audio"""
    global boom_sound, powerup_sound, combo_sound, ambient_music
    boom_sound = create_procedural_sound(80, 0.3, 0.5)
    powerup_sound = create_procedural_sound(880, 0.15, 0.3)
    combo_sound = create_procedural_sound(660, 0.1, 0.2)
    ambient_music = AmbientMusic()