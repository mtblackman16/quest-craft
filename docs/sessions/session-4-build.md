> **OBSOLETE** — This guide was written before the game was built. Claude built the full game between Sessions 2 and 4. See `session-4-playtest.md` for the actual Session 4 guide (playtesting + exhibition evidence gathering).

# Session 4: BUILD — The Sprint (ARCHIVED)

**Goal:** Build the actual game! Claude codes, you playtest and direct.

**Time:** ~3-4 hours (longest session — can split across 2 days)

**What you need:** Voice (Wispr Flow), controllers, your character drawings (to scan), excitement

**Slash command:** `/build`

---

## How This Session Works

This is where the magic happens. Claude builds your game piece by piece, following the Blueprint build order. After EVERY addition, you play the game and tell Claude how it feels. You're the directors — Claude is the engineer who makes your vision real.

**The rhythm:**
1. Claude builds something new
2. Claude says: "I just added [X]. Run the game and try it!"
3. You play it: `python game/main.py`
4. You tell Claude: "It feels [too fast / too slow / awesome / weird / broken]"
5. Claude adjusts until you're happy
6. Next piece!

---

## What You'll Say (Example Voice Prompts)

You don't need to know code. Just tell Claude what you want:

### Movement & Feel
- "Make the jump higher"
- "The player moves too slow, speed it up"
- "I want the movement to feel snappier"
- "When I stop moving, the player should stop immediately, not slide"
- "Can the player double jump?"

### Enemies & Combat
- "The enemy should move faster"
- "This enemy is too easy, make it harder"
- "Add a second type of enemy that flies"
- "When you hit an enemy, there should be a flash"
- "The boss needs more health"

### Items & Scoring
- "Add a sound when we collect a coin"
- "The score should show up bigger"
- "Add a power-up that makes you invincible for 5 seconds"
- "When you get a high score, something special should happen"

### Visuals & Polish
- "The player should face the direction they're moving"
- "When you die, there should be a cool explosion"
- "The background should scroll when you move"
- "Add some particles when the player lands"
- "The screen should shake when you get hit"

### Sound & Music
- "The music should get more intense in later levels"
- "Add a victory sound when you finish a level"
- "The jump sound is too loud"
- "This needs spookier music"

### Levels
- "Level 2 needs more enemies"
- "The gap between those platforms is too wide"
- "Add a checkpoint so we don't restart from the beginning"
- "The level is too short, make it longer"

---

## The Build Order

Claude follows this order (from the Blueprint). After each step, YOU playtest:

### Step 1: Game Window + Player Movement
You'll see a colored rectangle moving around the screen. This IS your player (art comes later).
- Test: Does movement feel right? Too fast? Too slow? Too floaty?

### Step 2: Gravity + Jumping
The player falls and can jump (if your game has jumping).
- Test: Does the jump feel good? How high? How floaty?

### Step 3: First Enemy + Collision
An enemy appears! When you touch it, something happens.
- Test: Is the enemy too easy? Too hard? Does collision feel fair?

### Step 4: Health + HUD
Health bar, lives counter, and score appear on screen.
- Test: Can you read everything? Is it in the right spot?

### Step 5: Scoring + Collectibles
Items appear that you can collect for points.
- Test: Is collecting satisfying? Good sound? Good visual feedback?

### Step 6: Level Layout + Obstacles
Platforms, walls, pits — the actual level takes shape.
- Test: Is the level fun to navigate? Too hard? Too easy?

### Step 7: Sound Effects + Music
Background music and sound effects for every action.
- Test: Does the audio match the mood? Any sounds missing?

### Step 8: Menus
Title screen with "Press Start." Game over screen with score. Restart option.
- Test: Does the flow make sense? Start → Play → Die → Game Over → Restart?

### Step 9: Additional Levels
Level 2, Level 3, boss fights.
- Test: Does difficulty increase properly? Are new levels different enough?

### Step 10: Art Integration
Your hand-drawn characters and backgrounds replace the colored rectangles.
- Test: Does everything look right? Right size? Right position?

### Step 11: Controller Mapping
Finalize which button does what.
- Test: Does every button work? Feels natural?

### Step 12: Polish
Screen transitions, particles, screen shake, extra juice.
- Test: Does the game feel GOOD? Professional? Fun?

---

## Game Design Wisdom (Claude teaches during building)

Claude will drop knowledge while building. Things like:

- "I just added gravity. See how the player falls? Every frame, I add a little downward speed. Games have done this since Donkey Kong in 1981."

- "This collision detection checks if two rectangles overlap. It's called AABB collision — one of the oldest tricks in game programming."

- "Notice how the enemy patrols back and forth? That's the simplest game AI. Real enemies in Zelda and Mario use the exact same idea, just with more patterns."

- "We're running at 60 frames per second. The game redraws EVERYTHING 60 times a second — like a flip book, but really, really fast."

- "See that screen shake when you get hit? That 3 pixels of camera movement is the difference between 'I got hit' and 'OUCH I got hit!' Juice makes games feel alive."

---

## Creative Activities During Build

- **Art Import:** Photograph your character drawings. Claude helps turn them into game sprites.
- **Sound Hunting:** Find or create sound effects (free sound websites or make your own).
- **Screenshot Timeline:** Take a screenshot after each major addition. These become exhibition materials.
- **Bug Hunting:** Play the game and try to break it. "What happens if I jump here? What if I go off screen?"

---

## You're Done When...

- [ ] Player moves and feels good
- [ ] At least 1 enemy type works
- [ ] Collision and health work
- [ ] Scoring/collectibles work
- [ ] At least 1 complete level is playable
- [ ] Sound effects and music are in
- [ ] Title screen and game over screen work
- [ ] The game is FUN to play
- [ ] Screenshot timeline captured
- [ ] `/showcase` learning log filled out

---

## Talking Tips

- "That's close but not quite right. The jump needs to be [higher/faster/slower]"
- "I love that! Don't change it."
- "Can you show me the code that controls [X]? I want to understand it."
- "Save this version before we make more changes"
- "Let's take a break and playtest the whole thing from the start"
- "This is the best part of the game so far"
