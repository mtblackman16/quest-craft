# Session 3: BLUEPRINT — The Technical Plan

**Goal:** Claude translates your game design into a build plan. You validate it. Then you get your first hands-on moment: testing controllers.

**Time:** ~1.5 hours

**What you need:** Voice (Wispr Flow), Nintendo Switch controllers, paper for notes

**Slash command:** `/blueprint`

---

## How This Session Works

This is where your game goes from "ideas on paper" to "ready to build." Claude reads everything you designed in Sessions 1 and 2, then explains HOW it will all be built. Your job: make sure Claude understood everything correctly.

---

## The Conversation

### Part 1: The Readback

Claude reads back your ENTIRE game design — everything from Sessions 1 and 2:

"Here's what we're building: [FULL SUMMARY]. Does this sound right? Did I miss anything? Is there anything you want to change before we start building?"

**This is your last chance to change big things easily.** Once we start building, changes are harder (but still possible).

---

### Part 2: The Architecture

Claude explains the pieces your game needs:

"Your game is made up of these connected systems:"
- **Player System** — Movement, health, abilities, animations
- **Enemy System** — Types, behavior patterns, spawning rules
- **Level System** — Layout, transitions, difficulty progression
- **HUD** — Health display, score counter, lives indicator
- **Menus** — Title screen, pause menu, game over screen
- **Collision System** — What happens when things touch each other
- **Sound System** — Music playback, sound effect triggers
- **Input System** — Controller buttons and keyboard backup

For each system, Claude asks: "Does this match what you imagined?"

---

### Part 3: The Build Order

Claude presents the order things will be built:

"We'll build your game step by step, testing each piece before adding the next:"

1. Game window + player movement
2. Gravity + jumping (if your game has it)
3. First enemy + collision detection
4. Health/lives + HUD display
5. Scoring + collectibles
6. Level layout + obstacles
7. Sound effects + music
8. Menus (title screen, game over, restart)
9. Additional levels
10. Your hand-drawn art integrated as sprites
11. Controller mapping finalized
12. Polish (screen transitions, particles, juice)

"Each step, you'll play the game and tell me how it feels. We adjust until it's right, then move on."

---

### Part 4: Sprite Inventory

Claude lists every image the game needs:

"We need sprites (pictures) for these things: [LIST]. Some of these you'll draw and we'll scan in. Others we'll start with colored rectangles and replace with real art later. Which ones do you want to draw first?"

---

### Part 5: Controller Test (Hands-On!)

This is the exciting part — your FIRST time running real code!

Claude builds a simple controller test program. You:
1. Connect your Nintendo Switch controller via Bluetooth
2. Run the program
3. Press every button and see it light up on screen
4. Move the joysticks and see the response
5. Verify every button is working correctly

This is your first "we built something!" moment.

---

## Game Design Wisdom

Three principles Claude teaches during this session:

1. **Software Architecture** — "Big games are made of small pieces that talk to each other. Your player doesn't know about scoring. Your scoring doesn't know about enemies. Each piece does ONE job and does it well."

2. **Iterative Development** — "We don't build the whole game and then test it. We build ONE thing, test it, fix it, then add the next thing. Build, test, improve, repeat. Every professional game studio works this way."

3. **MVP (Minimum Viable Product)** — "Get the core FUN working first. If jumping feels great, you have a game. If jumping feels boring, no amount of pretty art or cool music will save it. Fun first, polish later."

---

## What Claude Creates for You

- **Technical Blueprint** (`docs/plans/technical-blueprint.md`) — Full architecture and build order
- **Sprite Inventory** — List of all art assets needed
- **Controller Test Program** — First runnable code!

---

## You're Done When...

- [ ] Claude's readback matches your vision (or you've corrected it)
- [ ] You understand the build order
- [ ] Sprite inventory is finalized
- [ ] Controllers are connected and tested
- [ ] Every button on the controller works
- [ ] You're excited to start building next session!
- [ ] `/showcase` learning log filled out

---

## Talking Tips

- "Wait, that's not what we meant by [X]. Let me explain again..."
- "Can you show me how [SYSTEM] connects to [OTHER SYSTEM]?"
- "What happens if we skip [STEP]? Can we add it later?"
- "The controller feels [weird/good/laggy]. Is that normal?"
- "When do we get to see our game running?"
