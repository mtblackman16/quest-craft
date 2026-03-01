# Quest Craft Memory

> Claude reads this file at the start of every session. Keep it updated with key decisions and progress.

---

## Team

| Name | Age | Username on Pi |
|------|-----|---------------|
| Ethan | 9 | ethan |
| Eins | 11 | eins |
| Andrew | 11 | andrew (Artist) |
| Nathan | 9 | nathan |
| Mark | — | mark (Team Advisor) |

**Exhibition:** LASD Illuminate — March 15, 2026

---

## Project Status

**Current Phase:** Session 1 — Dream (COMPLETE)
**Current Session:** Day 1 Dream — concept brainstorm DONE
**Game Name:** Split
**Game Type:** 2D side-scrolling platformer with puzzles and stealth
**Core Word:** Survival
**Players:** Single player

---

## Approach: AI-First

Kids are the game designers. Claude is the engineer. The process:
1. Dream (Session 1) — game concept via conversation
2. Design (Session 2) — deep dive on all 7 topics
3. Blueprint (Session 3) — technical plan + controller test
4. Build (Session 4) — Claude codes, kids playtest and direct
5. Polish (Session 5) — bugs, controllers, exhibition prep

Voice-first via Wispr Flow. Slash commands drive each phase.

---

## Key Decisions

| Date | Decision | Decided By |
|------|----------|-----------|
| — | AI-first approach: kids design, Claude builds | Mark |
| — | Using Python 3.13 + Pygame 2.6 | Mark |
| — | Nintendo Switch controllers for input | Mark |
| — | Raspberry Pi 5 is the target platform | Mark |
| — | 5 sessions to complete the game | Mark |
| 2026-02-28 | 2D side-scrolling platformer (like Mario/Dead Cells) | Team |
| 2026-02-28 | Player character is a jello cube with eyeballs | Team |
| 2026-02-28 | Setting: dark castle in a desert, escape from dungeon to rooftop | Team |
| 2026-02-28 | Puzzles hidden in-world (levers, pressure plates) not separate rooms | Team |
| 2026-02-28 | Jello splitting mechanic — split into fourths, squeeze through gaps | Team |
| 2026-02-28 | Health system: jello powder + water + cooking pots = more health/size | Team |
| 2026-02-28 | Death = restart from beginning (roguelike tension) | Team |
| 2026-02-28 | Beat final boss = unlock hard mode | Team |
| 2026-02-28 | Dead Cells pixel art style | Team |
| 2026-02-28 | BotW-style enemy awareness (? and ! indicators, stealth) | Team |
| 2026-02-28 | Simple/Advanced control toggle for exhibition accessibility | Team |
| 2026-02-28 | Game title: **Split** | Team |
| 2026-02-28 | Single player game | Team |
| 2026-02-28 | School-appropriate: no weapons, jello powers and attacks only | Team |
| 2026-02-28 | Combat: jello shot (costs body mass), ground pound (stun), jello dodge | Team |
| 2026-02-28 | Items stored visibly inside the jello body | Team |
| 2026-02-28 | Ancient shield artifacts project light shields | Team |
| 2026-02-28 | Tutorial: starts in jail cell, contextual teaching like Zelda | Team |
| 2026-02-28 | Top 3 for exhibition: attacks/combat, crafting at pots, enemies | Team |
| 2026-02-28 | Sound: record real foley sounds, royalty-free or classical music | Team |
| 2026-02-28 | Pick up jello by rolling over it; too much = explode | Team |
| 2026-02-28 | Controllers: keyboard for now, Nintendo Pro Controller + Joy-Cons pairing in Session 2 | Mark |
| 2026-02-28 | Keyboard controls: Up=jump, SPACE=shoot, Z=split, Down(air)=ground pound | Team |
| 2026-02-28 | GitHub Pages enabled for parent summaries at mtblackman16.github.io/quest-craft/ | Mark |
| 2026-02-28 | Headless Pi display via wayvnc + noVNC (browser access on port 6080) | Mark |

---

## Game Concept Summary

**Premise:** You are a jello cube trapped in the dungeon of a castle in the desert. Fight and puzzle your way UP through the floors to the rooftop where the final boss waits.

**Core Mechanics:**
- 2D side-scrolling platformer (run, jump, fight)
- Hidden puzzles in the world (levers, pressure plates) reward jello powder
- Jello crafting: powder + water + heat at cooking pots = grow bigger, more health
- Splitting: divide into fourths to fit through small spaces (risk losing pieces)
- Size matters: too big = can't fit through some passages
- Stealth: sneak past enemies, BotW-style awareness (? and !)

**Combat System:**
- Jello Shot (main attack): shoot bits of yourself, lose body mass, roll over spare jello to reload, explode if too much
- Ground Pound: jump + slam, stuns enemies, kills small ones
- Jello Dodge: perfect-dodge timing, body goes liquid briefly and reforms, confuses lower enemies, creates attack window
- Ancient Shield: artifact that projects a light energy shield for defense
- Items stored visibly inside transparent jello body

**Tutorial Flow:**
- Start in a jail cell, move forward to escape
- Contextual teaching: game pauses on first encounter with new mechanic (like Zelda)

**Character:** Jello cube with little eyeballs

**Enemies:**
- Roly-polys — common swarming bugs, can overwhelm in groups
- Alcohol spray bottles — slow but deadly shots, must dodge
- Fire talus — mini-boss, shoots fireballs (drops fire pills)
- Big bosses — TBD

**Items & Resources:**
- Jello powder — from puzzles, used to craft health
- Water (4 types): small (1 use), normal (2 uses), big tank (5 uses), simmered (no pot needed)
- Fire pill — from fire talus, turns you orange, extra damage vs alcohol & bugs
- Shrink pill — rare drop from roly-polys, shrink without splitting
- Incense pill — keeps small monsters away (maybe from shops)
- Mighty pill — attack and energy up
- Jello armor — defense up
- Jello costume — disguise as roly-poly, fools alcohol bottles but not bosses
- Alcohol bottle drop — TBD

**World:**
- Castle interior: stone walls with vines, torches, occasional windows (can't see out)
- Gloom creeping through castle — less light = more monsters
- Chests to open, barrels to break
- Hidden barrel shops run by little shopkeeper guys
- Glowing door at end of each level = next floor up
- Desert outside (seen from title screen but not during gameplay)

**Music/Mood:**
- Peaceful during exploration and puzzles
- Intense/scary as darkness increases and monsters appear
- Music gets more dense approaching bosses or dark areas

**Back of the Box:**
> You're a jello cube. You're trapped. And the only way out is UP. Fight, split, and craft your way through a monster-filled castle — upgrading your skills floor by floor until you're strong enough to face what waits at the top. In Split, every piece of you matters.

**Title Screen:**
- Pixel art style, detailed background (castle + desert, more detailed than gameplay)
- Jello cube character posing
- Play, Settings, Controls buttons
- Controls page has Simple/Advanced toggle

**Keyboard Controls (Session 1 final):**
- Up Arrow = Jump
- Left/Right Arrows = Move
- SPACE = Jello Shot (costs body mass)
- Z = Split into 4 pieces
- Down Arrow (airborne) = Ground Pound
- ESC = Pause / Back to title

**Andrew's Artist Brief:** `docs/andrew-artist-brief.md` (+ HTML for printing)

---

## Dream Session Progress (Feb 28) — COMPLETE

All Dream questions answered. Ready for Session 2 (Design).

**Session 2 TODO:** Full controller mapping discussion (Pro Controller + Joy-Cons), Simple vs Advanced toggle design, hardware pairing

**Exhibition Scope (top 3 priorities):**
1. Core movement + all attacks (jello shot, ground pound, jello dodge)
2. Crafting at cooking pots (jello powder + water = grow/heal)
3. Enemies to fight (roly-polys, alcohol bottles if far enough)

Hidden puzzles are a "nice to have" after core is solid.

---

## Design Document Status

| Document | Status |
|----------|--------|
| 00-game-concept | Dream Complete |
| 01-characters | Not Started |
| 02-story-world | Not Started |
| 03-gameplay | Not Started |
| 04-levels | Not Started |
| 05-art-style | Not Started |
| 06-sound | Not Started |
| 07-controls | Not Started |

---

## Build Progress

| Date | What | File |
|------|------|------|
| 2026-02-28 | Spark demo created — title screen + playable jello cube platformer | `game/spark.py` |

**Spark demo features:** Animated title screen with glowing "SPLIT" letters, bobbing jello cube preview, dungeon dust particles. Gameplay scene with translucent jello cube (eyeballs, squish physics, trail), 5 stone platforms, 7 collectible jello powder diamonds, torchlit castle background with vines and flickering torches. Three new mechanics added: jello shot (SPACE, costs body mass), ground pound (Down while airborne), and split into 4 pieces (Z). Arrow keys to move/jump, ESC to return to title.

---

## End-of-Session Checklist

Every session ends with:
1. Save all decisions to `memory/MEMORY.md`
2. Update relevant PRDs in `docs/prds/`
3. Git commit + push
4. Generate parent summary HTML in `docs/parent-summaries/session-N-name.html` (use TEMPLATE.html)
5. Mark records Loom video of the day's output, adds link to the summary
6. Email summary to parents

---

## See Also

- `patterns.md` — Code patterns that work
- `lessons.md` — Mistakes and fixes
- `docs/parent-summaries/TEMPLATE.html` — Reusable parent email template
