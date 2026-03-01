# PRD 00: Game Concept

| Field | Value |
|-------|-------|
| **Status** | Dream Complete |
| **Author** | Ethan, Eins, Andrew, Nathan |
| **Date** | 2026-02-28 |
| **Reviewed by** | Mark (Team Advisor) |

---

## What Game Are We Making?

> **Split** — A 2D side-scrolling platformer where you play as a jello cube with eyeballs, trapped in the dungeon of a dark castle in the desert. Fight monsters with your own jello body, solve hidden puzzles, craft health from jello ingredients, and escape floor by floor to the rooftop where the final boss waits. Single player. School-appropriate — no weapons, just jello powers.
>
> **The game in one word: Survival.**

---

## Back of the Box

> You're a jello cube. You're trapped. And the only way out is UP. Fight, split, and craft your way through a monster-filled castle — upgrading your skills floor by floor until you're strong enough to face what waits at the top. In Split, every piece of you matters.

---

## The Big Questions

### What type of game is it?
- [x] Platformer (run, jump, avoid obstacles — like Mario)
- Combined with puzzle elements hidden in the world (like Zelda shrines but integrated into the level)
- Stealth elements (like Breath of the Wild enemy awareness)
- Art style: Dead Cells pixel art — small pixels, clean readable shapes

### What makes it special?
**The Jello Splitting Mechanic.** Since you're made of jello, you can split into fourths to squeeze through small passages. But you can only control one piece at a time — and you might lose the other pieces. Growing bigger (from crafting health) makes you stronger but blocks some passages. Players constantly decide: big and strong, or small and nimble?

**Everything ties to being jello.** Your health system is jello powder + water + cooking pots. Your pills change your jello flavor/color. Your disguise costume jiggles like a bug. The whole game is built around what you ARE.

### Who is the player?
A jello cube with little eyeballs. Lovable, jiggly, determined to escape.

### What does the player DO?
- Run left/right, jump in a 2D side-scrolling world
- Fight monsters (roly-polys, alcohol spray bottles, fire talus bosses)
- Find and solve hidden puzzles (levers, pressure plates) for jello powder
- Craft health at cooking pots (jello powder + water + heat)
- Split into smaller pieces to reach secret areas
- Sneak past enemies using stealth or disguises
- Collect pills, armor, and items
- Shop at hidden barrel shops

### What's the goal?
Escape the castle. Start in the dungeon, fight up through each floor, reach the rooftop, defeat the final boss. Then unlock hard mode.

### How does the player lose?
Die = restart from the very beginning. This creates high tension — every encounter matters. Players must be strategic about when to fight, when to sneak, and when to run.

---

## Imagine You're Playing...

**What do you see on the title screen?**
Pixel art style. A detailed background showing the castle with the desert behind it, more detailed than the gameplay itself (like Minecraft's 3D menu or Zelda's title screen). The jello cube character doing a pose. Big pixely title at the top. Buttons: Play, Settings, Controls. Controls page has a Simple/Advanced toggle.

**You press Play. What happens first?**
You wake up in a jail cell in the dungeon. You move forward, escape the cell, and the game teaches you as you go — the first time you encounter something new (a monster, a lever, a cooking pot), the game pauses and shows you what to do, like Zelda. Dark stone walls, creeping vines, torches flickering. The music is calm but mysterious.

**You're playing the game now. What are you doing?**
Running through castle corridors, jumping on platforms, spotting a lever half-hidden behind vines. Pulling it opens a secret alcove with jello powder. Fighting off roly-polys that swarm you. Finding a cooking pot, mixing water and powder to grow bigger. Approaching a dark area where the torches run out and the music gets intense...

**Something goes wrong! What happened?**
Too many roly-polys swarmed you in a dark corridor. Or an alcohol spray bottle landed a devastating slow shot you didn't dodge. Or you split to reach a secret area and lost a piece of yourself.

**You beat the level! What happens next?**
A glowing door appears. You touch it, get pulled through, and arrive on the next floor of the castle. Higher up. Harder enemies. Less light. More gloom. The music shifts.

---

## Enemies

| Enemy | Type | Behavior | Drops |
|-------|------|----------|-------|
| Roly-poly | Common | Small bugs, swarm in groups, can overwhelm | Water, rarely shrink pills |
| Alcohol spray bottle | Common | Slow but deadly shots, must dodge | TBD |
| Fire talus | Mini-boss | Shoots fireballs, like a Zelda talus | Fire pills |
| Big bosses | Boss (per floor) | TBD | TBD |
| Final boss | Final | At the top of the castle | Game completion |

**Enemy awareness:** Breath of the Wild style — question mark (?) when suspicious, exclamation mark (!) when they spot you. You can sneak past enemies.

---

## Combat System

**School-appropriate: no weapons. All attacks are jello powers.**

### Attacks
| Attack | How It Works | Notes |
|--------|-------------|-------|
| Jello Shot | Shoot bits of yourself at enemies | Main attack. Costs body mass — you shrink as you shoot. Roll over spare jello to reload. Pick up too much = explode! |
| Ground Pound | Jump up, slam down | Stuns enemies around you. Kills small roly-polys. No damage to big enemies. |
| Jello Dodge | Perfect-dodge when enemy attacks | Body goes liquid briefly and reforms. Confuses lower enemies, creates attack window. Like BotW Flurry Rush. |

### Defense
| Defense | How It Works |
|---------|-------------|
| Ancient Shield | Square artifact found in castle. Activate to project a light energy shield around you. |
| Jello Armor | Defense up — absorbs damage |
| Jello Costume | Disguise as roly-poly. Fools alcohol bottles, not bosses. |

### Keyboard Controls (Temporary)

Keyboard is the primary input during development. Nintendo Pro Controller + Joy-Con mapping will be finalized in Session 2.

| Action | Key |
|--------|-----|
| Move Left | A or Left Arrow |
| Move Right | D or Right Arrow |
| Jump | W or Up Arrow or Space |
| Jello Shot | J |
| Ground Pound | S or Down Arrow (while airborne) |
| Jello Dodge | K |
| Interact | E |
| Shield | L |
| Pause | ESC |

### Inventory
Items are stored **visibly inside the transparent jello body**. Players can see water bottles, pills, and shields floating inside the cube. Functional AND hilarious.

---

## Items & Resources

### Water Types
| Type | Uses for Jello Crafting |
|------|------------------------|
| Small water | 1 use |
| Normal water | 2 uses |
| Big water tank | 5 uses |
| Simmered water | Already hot — no cooking pot needed |

### Pills
| Pill | Effect | Source |
|------|--------|--------|
| Fire pill | Turns you orange, extra damage vs alcohol & bugs | Fire talus drop |
| Shrink pill | Shrink without splitting | Rare roly-poly drop |
| Incense pill | Keeps small monsters away | Shops (maybe) |
| Mighty pill | Attack and energy up | TBD |

### Equipment
| Item | Effect |
|------|--------|
| Jello armor | Defense up |
| Jello costume | Disguise as roly-poly — fools alcohol bottles, not bosses |

### World Objects
- Chests — open for loot
- Barrels — break them, occasionally find a shopkeeper inside
- Cooking pots — craft jello powder + water into health
- Levers and pressure plates — hidden puzzle elements

---

## Inspiration

1. **Zelda: Breath of the Wild** — shrine puzzles, enemy awareness system (? and !), gloom mechanic, title screen style
2. **Dead Cells** — pixel art style, difficulty, side-scrolling combat
3. **Mario** — 2D side-scrolling platformer movement, level progression
4. **Minecraft** — menu screen style (detailed background), pixel aesthetic

---

## The Feeling

The game BREATHES between two moods:
- **Peaceful** — exploring, solving puzzles, discovering secrets, calm music, torchlit corridors
- **Intense** — darkness closing in, music building, monsters swarming, one death = restart everything

---

## Sound Direction

- **Foley:** Record real sounds (smack jello for landing, real clicks for levers)
- **Music:** Royalty-free game music or classical music (public domain). NO copyrighted game music (Zelda, Minecraft, etc.)
- **Dynamic music:** Peaceful during exploration, intense/scary in dark areas and near bosses

---

## Exhibition Scope (2-Week Build)

**If we had a year, the game would have:** All floors, all bosses, all items, full story, hard mode, hidden puzzles everywhere.

**The 3 most important things for the exhibition version:**
1. **Core movement + all attacks** (jello shot, ground pound, jello dodge)
2. **Crafting at cooking pots** (jello powder + water = grow/heal)
3. **Enemies to fight** (roly-polys for sure, alcohol bottles if players get far enough)

Hidden puzzles are a "nice to have" once the core feels great.

---

## Open Questions (for Design sessions)

- [x] ~~Game title~~ — **Split**
- [ ] Final boss design
- [ ] Big boss designs for each floor
- [ ] What the alcohol bottle enemy drops
- [x] ~~Detailed attack/defense mechanics~~ — jello shot, ground pound, jello dodge, ancient shield
- [ ] Music and sound effects specifics (direction set, details TBD)
- [ ] How many floors/levels?
- [ ] What does hard mode change?
- [x] ~~Top 3 features to build first~~ — attacks, crafting, enemies
- [ ] Full controller mapping (Pro Controller + Joy-Cons) — Session 2
- [ ] Simple vs Advanced control toggle details — Session 2
- [ ] Single Joy-Con sideways vs two Joy-Cons — Session 2

---

## Dependencies

This PRD should be completed FIRST. All other PRDs build on the game concept.
