# Session 2: DESIGN — The Deep Dive

**Goal:** Design every aspect of your game in enough detail that it could be built.

**Time:** ~2-3 hours

**What you need:** Voice (Wispr Flow), paper, pencils/markers, colored pencils, graph paper (for level maps)

**Slash command:** `/design [topic]`

Topics: characters, world, gameplay, levels, art, sound, controls

---

## How This Session Works

You'll go through 7 design topics with Claude. For each topic, Claude asks deep questions — and keeps going deeper until every detail is nailed down. You can tackle topics in any order, and come back to revisit any topic later.

**Pro tip:** Use `/design characters` to start a topic, `/design levels` to switch to another, etc.

---

## Topic 1: Characters

### Questions Claude Will Ask:

**The Player:**
- "Describe your main character like you're telling a friend about a movie hero."
- "What can they do? Walk, run, jump, attack, fly, something special?"
- "What's their special move or ability that nobody else has?"
- "What makes them cool? What's their personality?"
- "What do they look like? Tall, short, human, animal, robot?"

**The Enemies:**
- "Now the bad guys — who or what is trying to stop the player?"
- For each enemy:
  - "What does it do? How does it move?"
  - "How does the player beat it?"
  - "What makes it challenging?"
  - "What does it look like?"

**Other Characters:**
- "Are there any friendly characters? Shopkeepers? Guides? Someone who gives quests?"

### Creative Activity:
Draw each character on paper — player, every enemy type, any friendly characters. Label their abilities.

---

## Topic 2: World

### Questions Claude Will Ask:
- "Where does this game take place? Describe it like you're writing a movie script."
- "What does the world look like? What colors dominate?"
- "Is there more than one area? What's different about each?"
- "What's the mood? Dark and spooky? Bright and cheerful? Epic and adventurous?"
- "What time period? Future? Medieval? Modern? Made-up?"
- "What are the rules of this world? Is there gravity? Magic? Technology?"
- "What's in the background? Mountains? Stars? A city? Trees?"

### Creative Activity:
Draw a world map or scene. Show the different areas and what makes each one unique.

---

## Topic 3: Gameplay Mechanics

### Questions Claude Will Ask:
- "What's the MAIN thing the player does 90% of the time? Jump? Fight? Solve puzzles? Explore?"
- "Walk me through 30 seconds of gameplay — what does the player DO?"
- "How does the player get hurt? Touching enemies? Falling? Traps?"
- "How do they heal? Health pickups? Time? They don't?"
- "Is there a score? Lives? Health bar? What matters to the player?"
- "What power-ups or special items exist? What do they do?"
- "What happens when the player dies? Restart level? Lose a life? Game over?"
- "What makes the game get harder as you play?"

### Game Design Wisdom:
**The Core Loop** — "Every great game has a loop: do something (action) → get rewarded → face a harder challenge → repeat. Yours is: [ACTION] → [REWARD] → [CHALLENGE] → repeat."

---

## Topic 4: Levels

### Questions Claude Will Ask:
- "How many levels are in your game? Or is it endless?"
- "Walk me through Level 1 — what does the player see when it starts?"
- "What enemies are in Level 1? Where are they?"
- "What obstacles are there? Pits? Walls? Moving platforms?"
- "What changes in Level 2? New enemies? New obstacles? Faster speed?"
- "What about Level 3?"
- "Is there a boss? What makes the boss fight special and different from regular enemies?"
- "How does the player know they finished a level? A door? A flag? Defeating the boss?"
- "Is there a final ending? What happens when you beat the whole game?"

### Game Design Wisdom:
**Difficulty Curves** — "Level 1 should be easy enough that nobody gets frustrated and quits. Each level adds ONE new thing. By the final level, everything combines into the ultimate challenge."

### Creative Activity:
Draw level maps on graph paper. Show where the player starts, where enemies are, where obstacles go, and where the level ends.

---

## Topic 5: Art Style

### Questions Claude Will Ask:
- "Pixel art (like retro games), hand-drawn (like your sketches), or simple shapes (circles, squares)?"
- "What's the main color palette? Show me or describe the colors."
- "How big should characters be on screen? Tiny and far away, or big and close up?"
- "What does the background look like in each level?"
- "What does the HUD look like? Where's the health bar? Score? Lives?"
- "What do the menus look like? Title screen? Pause menu? Game over screen?"
- "Are there visual effects? Explosions? Particles? Screen shake?"

### Game Design Wisdom:
**Juice** — "The little touches that make games FEEL good. Screen shake when you get hit. Particles when you collect a coin. A flash when you land a hit. These tiny details are what separate 'okay' games from 'WOW' games."

### Creative Activity:
Draw/color the art style. Create color swatches. Draw the HUD layout. Draw what the menus look like.

---

## Topic 6: Sound

### Questions Claude Will Ask:
- "What kind of music plays during normal gameplay? Intense? Chill? 8-bit? Orchestral?"
- "Does the music change for boss fights? Different levels?"
- "List every sound effect you can think of:"
  - Player: jump, land, attack, get hit, die, heal, collect item
  - Enemy: appear, attack, get hit, die
  - World: door open, switch activate, explosion, ambient sounds
  - UI: menu select, menu confirm, menu cancel, game start, game over
- "Where will sounds come from? Free sound websites? Make your own? 8-bit generated?"

### Creative Activity:
Make a sound list — every single sound the game needs, organized by category.

---

## Topic 7: Controls

### Questions Claude Will Ask:
- "Walk me through every button on the Nintendo Switch controller — what does each one do?"
- "Left stick moves the player. What about the right stick?"
- "Which button jumps? Which button attacks? Which button is special ability?"
- "How should movement FEEL? Fast and snappy like Mario? Floaty like Kirby? Heavy like Dark Souls?"
- "What happens when you press two buttons at the same time? Like jump + attack?"
- "What buttons work in menus? How do you start the game? Pause?"

### Reference: Nintendo Switch Controller in Pygame
```
Verified mapping: Pi 5 + hid_nintendo + SDL2 (evtest ground truth)

Button 0 = B (bottom)       Button 1 = A (right)
Button 2 = X (top)          Button 3 = Y (left)
Button 4 = Capture          Button 5 = L Bumper
Button 6 = R Bumper         Button 7 = ZL
Button 8 = ZR               Button 9 = Minus
Button 10 = Plus            Button 11 = Home
Button 12 = L Stick Click   Button 13 = R Stick Click

Axis 0 = Left Stick X       Axis 1 = Left Stick Y
Axis 2 = Right Stick X      Axis 3 = Right Stick Y

D-pad = Hat 0 (not buttons — use joy.get_hat(0))
```

### Creative Activity:
On a printed controller diagram, write what each button does in your game.

---

## What Claude Creates for You

After each topic, Claude writes up the design into the matching PRD file:
- Characters → `docs/prds/01-characters.md`
- World → `docs/prds/02-story-world.md`
- Gameplay → `docs/prds/03-gameplay.md`
- Levels → `docs/prds/04-levels.md`
- Art → `docs/prds/05-art-style.md`
- Sound → `docs/prds/06-sound.md`
- Controls → `docs/prds/07-controls.md`

---

## You're Done When...

- [ ] All 7 topics have been discussed in depth
- [ ] Character sketches are drawn (player + all enemies)
- [ ] Level maps are drawn on graph paper
- [ ] HUD layout is designed
- [ ] Controller mapping is decided
- [ ] Sound effect list is complete
- [ ] Art style/colors are chosen
- [ ] Claude has written all 7 PRD documents
- [ ] `/showcase` learning log filled out

---

## Talking Tips

- "Let me think about that for a second..."
- "Actually, can we change what we said about [TOPIC]?"
- "Show me what we've decided so far for [TOPIC]"
- "I like [KID'S NAME]'s idea about the enemies, let's go with that"
- "What would YOU suggest, Claude? What would make this more fun?"
