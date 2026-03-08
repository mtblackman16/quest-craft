# Session 2: DESIGN — The Deep Dive

**Goal:** Design every aspect of your game in enough detail that it could be built.

**Time:** ~2-3 hours

**What you need:** Voice (Wispr Flow), paper, pencils/markers, colored pencils, graph paper (for level maps)

**Slash command:** `/design [topic]`

Topics: characters, world, gameplay, levels, art, sound, controls

---

## Session Status — March 8, 2026

| Block | What | Status |
|-------|------|--------|
| 1. Feedback & Welcome | Spark playtest, team feedback | COMPLETE |
| 2. Art Workshop | Andrew's artwork processed, organized, cataloged | COMPLETE — 10 images processed into `assets/images/` |
| 3. Design Sprint | Deep dive on characters, world, levels, sound | STARTING NOW |
| 4. Controller Test | Playtest with Pro Controller | Controller already paired and working |
| 5. Showcase | Learning reflections | End of session |

**Where we are:** The Spark demo (`game/spark.py`) proved the concept — a title screen and character moving on screen. Now we need to design the FULL game so Claude can build it. That means going beyond the demo into real levels, real enemies, real gameplay — all using Andrew's hand-drawn artwork as the visual foundation.

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

## Topic 4: Levels — PRIORITY TOPIC

The game takes place in a castle. We need to design MULTIPLE FLOORS, not just one scene. Each floor is a level with its own look, enemies, and challenges. Think of it like climbing a tower — each floor gets harder and introduces something new.

### Questions Claude Will Ask:
- "How many floors does the castle have? What's at the very top?"
- "Walk me through Floor 1 — what does the player see when they enter the castle?"
- "What enemies are on Floor 1? Where are they? How many?"
- "What obstacles are there? Pits? Walls? Moving platforms? Traps?"
- "What changes on Floor 2? New enemies? New obstacles? Different look?"
- "What about Floor 3? What makes it different from the first two?"
- "Is there a boss on each floor, or just one big boss at the top?"
- "What makes each boss fight special and different from regular enemies?"
- "How does the player get from one floor to the next? Stairs? Elevator? Portal?"
- "What's the final ending? What happens when you reach the top of the castle?"

### Game Design Wisdom:
**Difficulty Curves** — "Level 1 should be easy enough that nobody gets frustrated and quits. Each level adds ONE new thing. By the final level, everything combines into the ultimate challenge."

**Think in Floors** — "Each castle floor should feel like a different world. Maybe Floor 1 is the dungeon (dark, damp), Floor 2 is the armory (traps, weapons), Floor 3 is the throne room (the big boss). What story does your castle tell as you climb?"

### Creative Activity:
Draw level maps on graph paper. Show where the player starts on each floor, where enemies are, where obstacles go, and where the stairs/exit to the next floor is. Design at least 3 castle floors.

---

## Topic 5: Art Style

### ART DIRECTION SHIFT

**Original plan:** Dead Cells-style pixel art.
**New direction:** Andrew's detailed hand-drawn illustration style.

Andrew has already created artwork that sets the visual standard for the entire game. His drawings are higher resolution, more realistic, and more detailed than pixel art. This is our art style now — hand-drawn illustrations by Andrew.

**What Andrew has drawn so far (organized in `assets/images/`):**
- **Player:** Jello cube — front view, three-quarter view (`assets/images/player/`)
- **Enemy:** Sanitizer warrior — front view, side view, rear view, equipment spread (`assets/images/enemies/`)
- **Items:** Jelly powder bag, hand sanitizer (front and back), dropped items in puddle (`assets/images/items/`)

These aren't placeholders. These ARE the game's art. The game should be built around this style.

### Creating New Characters from Andrew's Style

Andrew is the visual design lead. When designing new characters and assets:

1. **Look at what exists** — Study Andrew's sanitizer warrior and jello cube. Notice the detail level, the line work, the color choices. New characters should match this quality.
2. **Andrew draws, everyone contributes ideas** — The whole team can describe what a new enemy or item should DO and how it BEHAVES, but Andrew decides what it LOOKS LIKE and draws it.
3. **Use existing art as templates** — When Andrew draws a new enemy, aim for the same level of detail as the sanitizer warrior (multiple views, equipment/ability details).
4. **Design for the game** — Each new character needs: a front-facing view (minimum), an attack/action pose, and enough detail for the team to describe its behavior.

### Questions Claude Will Ask:
- "Andrew's art is detailed and hand-drawn. How big should characters be on screen? Big enough to see the detail?"
- "What's the main color palette? Andrew's drawings have specific colors — what dominates?"
- "What does the castle background look like on each floor? Dark stone? Torchlit? Crumbling?"
- "What does the HUD look like? Where's the health bar? Score? Lives?"
- "What do the menus look like? Should they use Andrew's art style too?"
- "Are there visual effects? Explosions? Particles? Screen shake?"
- "What new characters or items does Andrew want to draw next?"

### Game Design Wisdom:
**Juice** — "The little touches that make games FEEL good. Screen shake when you get hit. Particles when you collect a coin. A flash when you land a hit. These tiny details are what separate 'okay' games from 'WOW' games."

### Creative Activity:
Andrew: sketch new enemies and items in your style. Everyone else: describe what the castle floors look like, design the HUD layout, and pick colors for backgrounds and UI.

---

## Topic 6: Sound — PRIORITY TOPIC

By the end of today, the team needs a music direction decided and at least one track picked out or described. Music sets the mood for the whole game — don't skip this.

### Questions Claude Will Ask:

**Music (decide TODAY):**
- "What kind of music plays while exploring the castle? Dark and mysterious? Epic and adventurous? Creepy? Orchestral?"
- "Does the music change on different floors? What about boss fights?"
- "Name a game, movie, or song that has the VIBE you want. That helps Claude find the right direction."
- "Where will music come from? Free music libraries? AI-generated? Royalty-free tracks?"
- "Do you want one track that loops, or different music per floor?"

**Sound Effects:**
- "List every sound effect you can think of:"
  - Player: jump, land, attack, get hit, die, heal, collect item
  - Enemy: appear, attack, get hit, die
  - World: door open, switch activate, explosion, ambient castle sounds (dripping, wind, torches)
  - UI: menu select, menu confirm, menu cancel, game start, game over
- "Where will sounds come from? Free sound websites? Make your own? 8-bit generated?"

### Creative Activity:
Make a sound list — every single sound the game needs, organized by category. Most importantly: pick the music vibe. Hum it, reference a game, or describe the feeling. Claude can help find or generate tracks that match.

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

## Moving Beyond the Spark Demo

The current `game/spark.py` is a proof of concept — a title screen and a character that moves. It showed that the tech works. Now the goal is to design the REAL game:

- **Real levels** — Multiple castle floors with platforms, enemies, and obstacles
- **Real art** — Andrew's hand-drawn characters and items replace the placeholder graphics
- **Real gameplay** — Combat, items, progression, bosses
- **Real sound** — Music and sound effects that match the mood

Everything you design today feeds directly into what Claude builds in Sessions 3-5. The more detail you give, the better the game will be.

---

## You're Done When...

- [ ] All 7 topics have been discussed in depth
- [ ] Character sketches are drawn (player + all enemies + new characters in Andrew's style)
- [ ] At least 3 castle floors are designed with maps on graph paper
- [ ] HUD layout is designed
- [ ] Controller mapping is decided
- [ ] Music direction is chosen (vibe, reference tracks, or specific songs)
- [ ] Sound effect list is complete
- [ ] Art style confirmed as Andrew's hand-drawn illustration style
- [ ] Claude has written all 7 PRD documents
- [ ] `/showcase` learning log filled out

---

## Talking Tips

- "Let me think about that for a second..."
- "Actually, can we change what we said about [TOPIC]?"
- "Show me what we've decided so far for [TOPIC]"
- "I like [KID'S NAME]'s idea about the enemies, let's go with that"
- "What would YOU suggest, Claude? What would make this more fun?"
