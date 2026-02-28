# /spark — Bring the Dream to Life

You are creating the FIRST playable moment of the kids' game. They just finished their Dream session and have a complete game concept in `docs/prds/00-game-concept.md`. Now you make it REAL — a title screen and a playable character demo that runs on the Pi's HDMI display with Nintendo Switch controller support.

## Before You Start
1. Read `docs/prds/00-game-concept.md` — this is your source of truth
2. Read `memory/MEMORY.md` for any additional context from the session

## What You Extract From the Concept Doc
- **Game title** — for the title screen
- **Genre** — determines movement style (platformer = side view with gravity, top-down = 4-directional, etc.)
- **Player character description** — shape, color, personality (rendered as colored shapes with personality, NOT stick figures)
- **World mood/atmosphere** — determines color palette and background
- **What makes it special** — the hook, reflected in any visual flair

## What You Generate

### File: `game/spark.py`

A single, self-contained Pygame file (~250-300 lines) that creates:

#### 1. Title Screen
- Game title rendered large and animated (pulse, glow, or letter-by-letter reveal)
- Background color that matches their world's mood
- Particle effects or atmospheric animation (floating dots, falling leaves, stars, rain — whatever fits the mood)
- "Press A to Play" prompt that pulses
- Smooth transition when A is pressed

#### 2. Playable Scene
- Their character as a colored shape with personality (a rectangle with eyes, a circle with a trail, etc. — NOT complex sprites, but more than a bare rectangle)
- Movement via left stick (smooth, responsive)
- Jump via A button (if platformer/side-scroller — with gravity and ground)
- Genre-appropriate movement (top-down 4-way for adventure, side-scroll with gravity for platformer, etc.)
- A simple ground/floor or world boundary
- Background that reflects their world (color gradient, simple shapes suggesting their setting)
- 3-5 floating collectibles or interactive elements that respond to the character (particles when touched, etc.)

#### 3. Controller Support
- Nintendo Switch Pro Controller via pygame.joystick
- Fallback to keyboard (arrow keys + space) for testing without controller
- Left stick for movement
- A button (button 0 on Switch Pro Controller) for jump/action
- B button (button 1) to return to title screen
- Handle controller hot-plug — don't crash if no controller

#### 4. Visual Polish (the "wow" factor)
- Smooth 60 FPS
- The character leaves a subtle trail or has a shadow
- Collectibles/particles have gentle animation (bob, spin, glow)
- Screen transitions (fade in/out)
- The title screen has at least one "ooh" moment (letter animation, particle burst, etc.)
- Colors are vibrant but matched to their world mood

### What NOT to Include
- No enemies (that comes in Build)
- No health/lives system
- No scoring
- No complex level design
- No external asset files (everything procedural/drawn with pygame.draw)
- No sound files (no .wav assets exist yet)

## How You Present It

### Narrate the build:
As you write the code, explain what you are doing in excited, kid-friendly language:
- "Okay, I'm creating the game window — 800 by 600 pixels, perfect for the Pi's display..."
- "Now I'm painting your world's sky... [COLOR] to match that [MOOD] feeling you described..."
- "Here comes [CHARACTER NAME]! I'm giving them [VISUAL DETAIL]..."
- "Adding controller support — the moment you pick up that Switch controller, you're playing YOUR game..."

### The reveal:
When the code is written, say:

"YOUR GAME IS READY. Run this in the terminal:

    python3 game/spark.py

Grab that controller. [CHARACTER NAME] is waiting for you."

### After they play:
Let them enjoy it for a few minutes. Then say:
"This is just the SPARK. The seed. In our next sessions, we'll design every detail — enemies, levels, music, art — and then we'll build the REAL version. But right now? You're playing a game that didn't exist 2 hours ago. YOU designed it. Show your parents."

## Genre-Specific Behavior

### Platformer (like Mario)
- Side view, gravity enabled
- Character on a ground plane, can jump with A
- 2-3 floating platforms above ground
- Collectibles hovering at different heights

### Top-Down Adventure (like Zelda)
- Top-down view, no gravity
- Character moves in 4/8 directions
- A few scattered objects as colored rectangles
- Collectibles spread around the area

### Side-Scroller Shooter (like Mega Man)
- Side view, gravity enabled
- A button fires a projectile (simple circle) to the right
- Collectibles that burst when hit

### Something Else
- Default to platformer mechanics (most intuitive for kids)
- Adjust colors and atmosphere to match their description

## Code Requirements
- Single file: `game/spark.py`
- No external dependencies beyond `pygame`, `sys`, `math`, `random`
- Must run on Raspberry Pi 5 (ARM, Python 3.13, Pygame 2.6.1)
- 60 FPS target
- 800x600 windowed mode (NOT fullscreen — safer on Pi HDMI)
- Graceful exit on window close or Escape key
- Use `pygame.font.Font(None, size)` for default font — never rely on system fonts

## After Generation
- Save the code to `game/spark.py`
- Git commit with message: "The spark — [GAME TITLE] comes to life"
- Update `memory/MEMORY.md`: note that the spark demo was created, record game title and genre
- DO NOT modify any PRD files or other docs
