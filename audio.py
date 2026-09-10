import pygame
import random
import math
import array
import threading
import time

try:
    pygame.mixer.init(channels=1)
except pygame.error:
    pass

boom_sound = None
powerup_sound = None
combo_sound = None
ambient_music = None


def create_procedural_sound(frequency, duration, volume=0.3):
    """Create a simple procedural sound without external audio files."""
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        audio_data = array.array("h", [0] * num_samples)

        for i in range(num_samples):
            t = i / sample_rate
            wave = math.sin(2 * math.pi * frequency * t)
            wave += 0.3 * math.sin(2 * math.pi * frequency * 2 * t)
            wave += 0.1 * math.sin(2 * math.pi * frequency * 3 * t)
            fade = 1.0 - (i / num_samples) if duration > 0.1 else 1.0
            sample = int(wave * volume * fade * 32767)
            audio_data[i] = max(-32768, min(32767, sample))

        return pygame.mixer.Sound(buffer=audio_data)
    except (pygame.error, ValueError, OverflowError):
        return None


class AmbientMusic:
    """Lightweight procedural ambient background music."""

    def __init__(self):
        self.running = False
        self.thread = None
        self.notes = [220, 277, 330, 440, 554, 659]
        self.current_note = 0
        self.lock = threading.Lock()

    def play_note(self, freq, duration):
        if not pygame.mixer.get_init():
            return
        try:
            sample_rate = 22050
            num_samples = int(sample_rate * duration)
            audio_data = array.array("h", [0] * num_samples)

            for i in range(num_samples):
                t = i / sample_rate
                wave = math.sin(2 * math.pi * freq * t)
                wave += 0.5 * math.sin(2 * math.pi * freq * 2 * t)
                attack = min(i / (sample_rate * 0.05), 1.0)
                release = 1.0 - min(max(i - num_samples * 0.7, 0) / (sample_rate * 0.3), 1.0)
                sample = int(wave * attack * release * 0.15 * 32767)
                audio_data[i] = max(-32768, min(32767, sample))

            pygame.mixer.Sound(buffer=audio_data).play()
        except pygame.error:
            pass

    def start(self):
        """Start ambient music once; safe to call repeatedly."""
        with self.lock:
            if self.running:
                return
            self.running = True
            self.thread = threading.Thread(target=self._music_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop ambient music and wait briefly for the worker to exit."""
        with self.lock:
            self.running = False
            thread = self.thread
            self.thread = None
        if thread and thread.is_alive():
            thread.join(timeout=1.0)

    def _music_loop(self):
        while self.running:
            if pygame.mixer.get_init():
                note = self.notes[self.current_note]
                self.play_note(note, 1.5)
                self.play_note(note * 1.5, 1.5)
                self.current_note = (self.current_note + 1) % len(self.notes)
            time.sleep(1.5)


def init_audio():
    """Initialize procedural sound effects and ambient music."""
    global boom_sound, powerup_sound, combo_sound, ambient_music

    if not pygame.mixer.get_init():
        return

    boom_sound = create_procedural_sound(80, 0.3, 0.5)
    powerup_sound = create_procedural_sound(880, 0.15, 0.3)
    combo_sound = create_procedural_sound(660, 0.1, 0.2)
    ambient_music = AmbientMusic()


def stop_ambient():
    """Stop ambient music during application shutdown."""
    if ambient_music:
        ambient_music.stop()
