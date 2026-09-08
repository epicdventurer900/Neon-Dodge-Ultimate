# Neon Dodge Ultimate

A neon-style survival dodge game built with Python and Pygame.

## Run

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The game supports systems without an audio device. The high score is saved to
`high_score.json` and ignored by Git.

## Controls

- **Left/Right arrows**: Move and start the game
- **P**: Pause/resume
- **R**: Restart after game over
- **M**: Toggle audio
- **F11**: Toggle fullscreen
- **Esc**: Exit

## Features

- Three enemy types and responsive difficulty scaling
- Shield, slow-motion, and double-points power-ups
- Procedural sound effects and ambient music
- Neon glow, particles, screen shake, combos, and persistent high scores
- Frame-rate-independent gameplay
