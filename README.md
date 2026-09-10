# Neon Dodge Ultimate

A neon-style survival dodge game built with **Python + Pygame**, focused on responsive gameplay, visual effects, procedural audio, and clean modular design.

## ✨ Features

- 🎮 Responsive left/right survival gameplay
- 👾 Three enemy types: Basic, Fast, and Big
- 📈 Dynamic difficulty scaling as the score increases
- 🛡️ Shield power-up that absorbs one collision
- 🐌 Slow-motion power-up that temporarily slows enemies
- ✨ Double-points power-up
- 🔊 Procedural sound effects and ambient music — no external audio files required
- 🌌 Neon glow, stars, particles, player trail, and screen shake
- 🔥 Combo system for consecutive successful dodges
- 🏆 Persistent high score stored locally
- ⏱️ Frame-rate-independent movement and timers
- 🖥️ Fullscreen toggle and graceful operation without an audio device

## 🧱 Project Structure

```text
Neon-Dodge-Ultimate/
├── main.py              # Game loop and state management
├── player.py            # Player movement, trail, and power-up timers
├── enemy.py             # Enemy types, movement, scoring, and rendering
├── powerup.py           # Power-up generation and rendering
├── particles.py         # Background particles, stars, and screen shake
├── audio.py             # Procedural sound and ambient music
├── ui.py                # HUD, gradient background, and text effects
├── settings.py          # Display, colors, and fonts
├── tests/               # Automated smoke/unit tests
├── requirements.txt     # Python dependencies
└── .github/workflows/   # Continuous validation with GitHub Actions
```

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/epicdventurer900/Neon-Dodge-Ultimate.git
cd Neon-Dodge-Ultimate
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the game

```bash
python main.py
```

## 🎮 Controls

| Key | Action |
|---|---|
| **Left / Right** | Move / start game |
| **P** | Pause / resume |
| **R** | Restart after game over |
| **M** | Toggle audio |
| **F11** | Toggle fullscreen |
| **Esc** | Exit |

## ⚙️ Technical Highlights

### Frame-rate-independent gameplay
Movement, enemy updates, particles, power-up timers, and effects use a frame-time scale so gameplay remains consistent across different frame rates.

### Procedural audio
Sound effects are generated at runtime using Python's `array` module and Pygame's mixer. The project therefore does not depend on downloaded sound assets.

### Modular architecture
The original game was organized into a large monolithic Python file and then separated into focused modules for the player, enemies, power-ups, particles, audio, UI, and settings.

### Automated validation
GitHub Actions compiles the Python modules and runs headless smoke tests so common import, construction, and gameplay-component regressions can be detected automatically.

## 🧪 Testing

Run the local smoke tests with:

```bash
python -m unittest discover -s tests -v
```

The CI workflow also runs these tests automatically on pushes and pull requests targeting `main`.

## 📌 Development Status

**Release candidate / portfolio project.** The core gameplay is complete and the codebase is maintained as a modular Pygame project.

## 👨‍💻 Author

**Prayukth Shetty**

Built as a practical Python game-development project while learning software engineering, modular design, and GitHub-based development.
