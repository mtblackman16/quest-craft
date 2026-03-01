# Tech Stack Reference

## Overview

Here's every tool we use and what it does.

---

## The Computer: Raspberry Pi 5

**What it is:** A small, credit-card-sized computer.
**What it does:** Runs our game. Sits at the exhibition with a monitor and controller.
**Specs:** 8GB RAM, ARM processor, WiFi, Bluetooth, HDMI output.

You don't code ON the Pi directly. You code from your laptop using VS Code Remote SSH — your laptop sends commands to the Pi over WiFi.

---

## The Language: Python 3.13

**What it is:** A programming language — instructions for the computer.
**Why Python:** It's the easiest language to learn, reads like English, and works great with Pygame.
**Version:** 3.13.5 (already installed on the Pi)

To run a Python file:
```bash
python3 game/main.py
```

---

## The Game Library: Pygame 2.6

**What it is:** A Python library that handles everything a game needs.
**What it does:**
- Opens a game window
- Draws shapes, images, and text on screen
- Plays sounds and music
- Reads controller/keyboard input
- Runs the game at 60 frames per second

**Version:** 2.6.1 (already installed on the Pi)

**Key Pygame modules we'll use:**
| Module | What It Does |
|--------|-------------|
| `pygame.display` | Create and update the game window |
| `pygame.draw` | Draw shapes (rectangles, circles, lines) |
| `pygame.image` | Load and display images (sprites) |
| `pygame.mixer` | Play sound effects and music |
| `pygame.joystick` | Read Nintendo controller input |
| `pygame.font` | Display text on screen |
| `pygame.time` | Control game speed (FPS) |

---

## The Editor: VS Code + Remote SSH

**What it is:** A code editor that runs on your laptop.
**The trick:** Remote SSH lets VS Code edit files on the Pi, even though it runs on your laptop.
**Why:** You get a nice editor with colors, autocomplete, and easy file browsing.

---

## The AI Partner: Claude Code

**What it is:** An AI that lives in the terminal and helps you write code.
**How to use it:** Type `claude` in the VS Code terminal.
**Version:** 2.1.62 (already installed on the Pi)

Claude can:
- Write code for you (with explanations)
- Fix bugs
- Explain what code does
- Help design game features
- Remember things across sessions

---

## Voice Input: Wispr Flow

**What it is:** A tool that converts your speech to text.
**Why:** Talking is faster than typing, especially if you're not a fast typer.
**How:** Install it on your laptop, activate it, then just talk.

---

## Controllers: Nintendo Switch

**What we have:** Nintendo Switch Pro Controller and/or Joy-Cons
**Connection:** Bluetooth (already enabled on the Pi)
**In code:** `pygame.joystick` reads button presses and stick positions

To pair a controller:
1. Hold the sync button on the controller until the lights flash
2. On the Pi, it should auto-pair (Bluetooth is set up)
3. Test with `python3 -c "import pygame; pygame.init(); j = pygame.joystick.Joystick(0); j.init(); print(j.get_name())"`

---

## Version Control: Git + GitHub

**Git** saves every version of your code locally.
**GitHub** stores it in the cloud so it's backed up and everyone can share.

Key commands (Claude handles most of this for you):
```bash
git pull            # Get the latest code
git add .           # Stage your changes
git commit -m "..."  # Save a snapshot
git push            # Upload to GitHub
git branch feature/x # Create a new branch
git checkout feature/x # Switch to a branch
```

---

## File Formats

| File Type | Extension | Used For |
|-----------|-----------|----------|
| Python code | `.py` | Game logic |
| Images | `.png` | Sprites, backgrounds (PNG supports transparency) |
| Sounds | `.wav` or `.ogg` | Sound effects and music |
| Fonts | `.ttf` | Custom text fonts |
| Markdown | `.md` | Documentation (like this file) |

---

## Headless Display: wayvnc

**What it is:** A VNC server for Wayland compositors.
**What it does:** Exposes the Pi's Wayland desktop over VNC so you can view it from another device — essential when the Pi has no monitor connected (headless).
**Usage:**
```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
wayvnc 0.0.0.0 5900 &
```

---

## Browser VNC: noVNC + websockify

**What it is:** A browser-based VNC client (noVNC) paired with a WebSocket-to-TCP bridge (websockify).
**What it does:** Lets you view the Pi's display from any device with a web browser — no VNC app needed. websockify bridges the browser's WebSocket connection to wayvnc's VNC port.
**Usage:**
```bash
websockify --web /usr/share/novnc 6080 localhost:5900 &
```
Then open `http://<PI_IP>:6080/vnc.html` in any browser.

---

## Static Hosting: GitHub Pages

**What it is:** Free static website hosting from GitHub.
**What it does:** Serves parent summaries and artist briefs directly from our repository at `mtblackman16.github.io/quest-craft/`.
**How it works:** Any HTML file pushed to the `docs/` folder on the `main` branch is automatically published. Parent summaries live at `docs/parent-summaries/` and are accessible via `https://mtblackman16.github.io/quest-craft/parent-summaries/`.
