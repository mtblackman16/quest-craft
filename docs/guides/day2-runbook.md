# Day 2 Runbook — The Design Session

> Mark's facilitator cheat sheet. Keep this open on your laptop and walk through it step by step.

---

## Quick Reference

| Item | Value |
|------|-------|
| Pi IP | `100.118.252.70` (Tailscale) |
| Pi user / pass | `mark` / `quest2026` |
| VS Code host | `mark@100.118.252.70` → select **Linux** |
| Claude command | `cd ~/quest-craft && claude` |
| Spark demo | `python3 game/spark.py` |
| Controller test | `python3 game/test_controller.py` |

---

## Pre-Session Prep (Mark does this BEFORE the boys arrive)

### The Night Before (Saturday)

- [ ] **Pull latest code** on the Pi: `cd ~/quest-craft && git pull`
- [ ] **Install Pillow** (needed for art-to-sprite conversion): `pip install Pillow`
- [ ] **Print controller diagrams** — print a blank Pro Controller layout diagram for each kid to label with game actions (search "Nintendo Switch Pro Controller button layout" and print)
- [ ] **Print Andrew's artist brief** if he hasn't seen it: `docs/andrew-artist-brief.md`
- [ ] **Prep art supplies** — white paper, black markers/Sharpies, colored markers, pencils, graph paper
- [ ] **Confirm Andrew has his artwork** — text his parents to remind him to bring his drawings
- [ ] **Review Session 1 game concept** — re-read `docs/prds/00-game-concept.md` so you're fresh

### Sunday Morning (1-2 hours before)

- [ ] **Power on the Pi**, HDMI display connected
- [ ] **Verify Pi on Tailscale:** `ssh mark@100.118.252.70`
- [ ] **Start headless display** (if no monitor):
  ```bash
  export XDG_RUNTIME_DIR=/run/user/$(id -u)
  wayvnc 0.0.0.0 5900 &>/dev/null &
  websockify --web /usr/share/novnc 6080 localhost:5900 &>/dev/null &
  ```
- [ ] **Verify Spark demo runs:** `cd ~/quest-craft && python3 game/spark.py` (ESC to quit)
- [ ] **Pygame test:** `python3 -c "import pygame; pygame.init(); print('OK')"`
- [ ] **Pillow test:** `python3 -c "from PIL import Image; print('OK')"`

### Controller Pairing (DO THIS BEFORE THE KIDS ARRIVE)

This is the most important prep step. If controllers don't work, you can fall back to keyboard.

**Step 1: Check Bluetooth packages**
```bash
# These should already be installed
sudo apt install bluetooth bluez joystick evtest
```

**Step 2: Check the hid-nintendo driver**
```bash
# Should return module info — this is the Nintendo controller driver
modinfo hid_nintendo

# If it's not loaded, load it
sudo modprobe hid_nintendo
```

**Step 3: Edit Bluetooth config (one-time)**
```bash
sudo nano /etc/bluetooth/input.conf
# Find: #ClassicBondedOnly=true
# Change to: ClassicBondedOnly=false
# Save and exit (Ctrl+X, Y, Enter)
sudo systemctl restart bluetooth
```

**Step 4: Pair the Pro Controller**
```bash
bluetoothctl
```
Then inside bluetoothctl:
```
power on
agent on
default-agent
scan on
```
Now **press and hold the SYNC button** on the top of the Pro Controller (small button near USB-C port) for 2 seconds. The player LEDs will flash.

Watch for "Pro Controller" to appear with a MAC address like `XX:XX:XX:XX:XX:XX`. Then:
```
scan off
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit
```

**Step 5: Verify**
```bash
ls /dev/input/js*
# Should show /dev/input/js0
```

**Step 6: Test in Pygame**
```bash
cd ~/quest-craft && python3 game/test_controller.py
```
Press buttons on the controller — you should see them light up on screen. Press ESC to exit.

**Fallback:** If Bluetooth won't pair, connect the Pro Controller via **USB-C cable**. It works instantly with zero configuration.

**If Joy-Cons are also being used:**
```bash
# Install joycond (handles Joy-Con sideways mode)
sudo apt install libevdev-dev libudev-dev cmake build-essential
cd /tmp && git clone https://github.com/DanielOgorchock/joycond.git
cd joycond && cmake . && sudo make install
sudo systemctl enable --now joycond
```
Then pair each Joy-Con separately via bluetoothctl using the SYNC button on the Joy-Con rail.

---

## Session Agenda (~2.5-3 hours)

### 1. Feedback & Welcome (20 min) — START HERE

**Why start here:** The boys had immediate reactions when they saw the game in Session 1. Capture that energy. Also, Andrew needs to see the game and feel welcome.

**Step 1: Everyone plays the Spark demo (10 min)**
1. Run on the Pi: `python3 game/spark.py`
2. Hand the keyboard to each kid for 1-2 minutes
3. As they play, ask each one: **"What's the coolest part?"** and **"What would you change?"**
4. Let them be loud and excited — this is their game!

**Step 2: Welcome Andrew (5 min)**
- "Andrew, you're our artist and creative director. Here's what the team designed in Session 1..."
- Show him the one-liner: *"You're a jello cube trapped in a castle dungeon, fighting your way up to the rooftop."*
- Show him the Spark demo: "This is the prototype. Your art will replace all of this."

**Step 3: Andrew's Art Show & Tell (5 min)**
- Andrew shows whatever artwork he's brought
- Everyone reacts — be encouraging, find what works
- Tell Claude: "Read this image and describe what you see" (builds trust in AI art analysis)

---

### 2. Photo-to-Sprite Workshop (20 min) — THE NEW CAPABILITY

> **Illuminate moment!** This is where physical art becomes digital game assets via AI. Document this for the exhibition.

**Walk the kids through this step by step:**

1. **Andrew picks one drawing** to convert (start with the jello cube character)

2. **Take the photo:**
   - Tape the drawing flat on a table
   - Position good lighting (lamp or window, NO flash)
   - Hold phone straight above, fill the frame
   - Take 2-3 shots, pick the sharpest

3. **Transfer to the Pi:**
   - Send photo to laptop (AirDrop, email, or USB)
   - In VS Code (connected to Pi), right-click `assets/images/` → "Upload..."
   - Upload the photo

4. **Claude analyzes it:**
   - Tell Claude: *"Read `assets/images/andrew-jello-drawing.jpg`. This is Andrew's hand-drawn character sketch. Describe what you see."*
   - Claude describes it — Andrew confirms or corrects
   - This is magical for the kids — AI "seeing" their drawing

5. **Claude generates the sprite:**
   - Tell Claude: *"Convert this to a 32x32 pixel art sprite. Make the background transparent. Save it as a PNG."*
   - Claude writes a Python script using Pillow
   - Run the script on the Pi
   - View the result in VS Code

6. **Iterate:**
   - "Make the eyes bigger" / "The green is too dark" / "Add more detail"
   - Claude adjusts the script, kids re-run
   - 2-3 iterations is usually enough

7. **Celebrate:**
   - "Andrew's drawing is now IN THE GAME. That's how game art works."

**Important for Mark:** Let Andrew drive this. He should feel like his art is the star. The other boys can contribute ideas but Andrew makes the visual calls.

---

### 3. Design Sprint (60-90 min)

> Use `/design [topic]` slash command to start each topic. Claude guides the conversation.

**How to facilitate:**
- One kid types the `/design` command
- Claude asks deep questions — everyone answers
- If one kid dominates, directly ask the quiet ones: "Nathan, what do you think?"
- Let them disagree — Claude helps find consensus
- After each topic, Claude writes the PRD automatically

**Recommended topic order (prioritized for time):**

| Order | Topic | Time | Who Leads | Command |
|-------|-------|------|-----------|---------|
| 1 | Characters | 15-20 min | Andrew (visuals) + all (behavior) | `/design characters` |
| 2 | Art Style | 15 min | Andrew leads | `/design art` |
| 3 | Controls | 15 min | Everyone (they all play) | `/design controls` |
| 4 | Gameplay | 15-20 min | Ethan + Eins (they designed the mechanics) | `/design gameplay` |
| — | BREAK | 10 min | Snacks! | — |
| 5 | Levels | 15 min | Everyone | `/design levels` |
| 6 | World | 10 min | Everyone | `/design world` |
| 7 | Sound | 10 min | Everyone | `/design sound` |

**Minimum to complete:** Topics 1-4 (Characters, Art, Controls, Gameplay). Topics 5-7 are stretch goals. If time is tight, World and Sound have enough from Session 1 to move forward.

**Creative activities during the sprint:**
- Andrew draws character sheets (player, enemies, items)
- Someone draws the HUD layout
- Everyone draws on the printed controller diagram
- Someone draws Level 1 map on graph paper

---

### 4. Controller Test with the Kids (15-20 min)

**This is both technical AND a design activity.**

1. Run `python3 game/test_controller.py`
2. Pass the controller around — every kid presses every button
3. On screen they see which button index maps to which physical button
4. **The design question:** "Okay team, which button should be JUMP? Which should be SHOOT? Which should be SPLIT?"
5. Kids fill out the printed controller diagrams with their decisions
6. Claude writes down the mapping in the Controls PRD

**Suggested mapping to offer (they can change anything):**

| Action | Pro Controller Button | Why |
|--------|----------------------|-----|
| Jump | A (right, button 1) | Standard platformer convention |
| Jello Shot | B (bottom, button 0) | Easy to reach while moving |
| Split | X (top, button 2) | Special move, separate from combat |
| Interact/Shield | Y (left, button 3) | Context-sensitive |
| Jello Dodge | L Bumper (button 5) | Quick access, defensive |
| Pause | Plus (button 10) | Standard |
| Movement | Left Stick (axis 0,1) | Standard |

**If time:** Claude adds controller support to `spark.py` live and kids test with the actual controller.

---

### 5. Showcase & Wrap (15 min)

1. Type: `/showcase`
2. Claude summarizes everything designed today
3. Go around the room — each kid shares their favorite design decision
4. **Andrew's moment:** Show his drawings and the sprite that came from them
5. Preview Session 3: "Next time, Claude takes all your designs and starts building the REAL game. Come with more art, Andrew!"
6. Claude commits everything to Git

**After the kids leave:**
- Claude generates the parent summary HTML
- Mark records a quick Loom video of the Spark demo and any new sprites
- Push to GitHub, share link with parents

---

## Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Controller not pairing | Hold SYNC button for 3 full seconds. Make sure Bluetooth is on: `sudo systemctl start bluetooth` |
| Controller paired but no input | Check `ls /dev/input/js*`. If empty, `sudo modprobe hid_nintendo`. Restart the test script. |
| Controller disconnects randomly | Move closer to the Pi. Disable rumble. Use USB-C cable as fallback. |
| Photo upload fails in VS Code | Make sure VS Code is connected via Remote SSH. Try dragging the file into the file explorer panel. |
| Pillow not installed | `pip install Pillow` on the Pi |
| Spark demo crashes | Check terminal for error. Common: missing asset file. Re-run. |
| Kid's laptop can't connect | Check Tailscale, try password `quest2026`, see Day 1 troubleshooting |
| Claude not responding | Check internet on Pi. `source ~/.bashrc` then `claude` |
| VNC not showing game | Make sure game is running on the Pi's display, not through SSH. Export `DISPLAY=:0` before running. |

---

## Files Created / Updated This Session

| File | Purpose |
|------|---------|
| `docs/prds/01-characters.md` | Character designs |
| `docs/prds/02-story-world.md` | World details |
| `docs/prds/03-gameplay.md` | Gameplay mechanics |
| `docs/prds/04-levels.md` | Level designs |
| `docs/prds/05-art-style.md` | Art style decisions |
| `docs/prds/06-sound.md` | Sound list |
| `docs/prds/07-controls.md` | Controller mapping |
| `assets/images/drawings/` | Andrew's original photos |
| `assets/images/player/` | Converted sprite PNGs |
| `game/test_controller.py` | Controller test utility |
| `memory/MEMORY.md` | Updated with all decisions |
| `docs/parent-summaries/session-2-design.html` | Parent recap page |

---

## Key Reminders

1. **Andrew is new** — make him feel important from minute one. He's the artist. Defer to him on visuals.
2. **Feedback first** — let the boys voice what they loved and what they'd change before diving into design.
3. **Photo workflow is an Illuminate story** — document the journey from paper drawing to game sprite.
4. **Controllers can wait** — if pairing is a headache, use keyboard. Controllers are fully needed by Session 3, not today.
5. **Don't rush the design** — it's better to do 4 topics really well than 7 topics superficially. The remaining topics can be covered at the start of Session 3.
6. **Everything is exhibition material** — the drawings, the controller diagrams, the design conversations. Save it all.
