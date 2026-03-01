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

**Current Phase:** Session 1 — Dream (in progress)
**Current Session:** Day 1 Dream — concept brainstorm
**Game Name:** TBD (team still deciding)
**Game Type:** 2D side-scrolling platformer with puzzles and stealth

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

**Title Screen:**
- Pixel art style, detailed background (castle + desert, more detailed than gameplay)
- Jello cube character posing
- Play, Settings, Controls buttons
- Controls page has Simple/Advanced toggle

---

## Dream Session Progress (Feb 28)

| # | Question | Status |
|---|----------|--------|
| 1 | Opening — what game would you play? | Done |
| 2 | Genre — what type of game? | Done |
| 3 | The Hook — what makes it unique? | Done — jello splitting |
| 4 | Experience — what do friends say? | Not yet |
| 5 | Feeling — how should players feel? | Done |
| 6 | Win/Lose — how do you win/lose? | Done |
| 7 | Inspiration — what inspired this? | Partial — Zelda, Dead Cells, BotW, Minecraft |
| 8 | The Pitch — summary and confirm | Done |
| 9 | Title — what's it called? | Not yet |
| 10 | Scope — top 3 for 2 weeks? | Not yet |
| 11 | Music/Soundtrack/SFX | Not yet (brief mentions so far) |
| 12 | Attacks & Defenses detail | Not yet |

---

## Design Document Status

| Document | Status |
|----------|--------|
| 00-game-concept | In Progress (Dream session) |
| 01-characters | Not Started |
| 02-story-world | Not Started |
| 03-gameplay | Not Started |
| 04-levels | Not Started |
| 05-art-style | Not Started |
| 06-sound | Not Started |
| 07-controls | Not Started |

---

## Build Progress

*Updated during Sessions 3-5 as features are built.*

---

## See Also

- `patterns.md` — Code patterns that work
- `lessons.md` — Mistakes and fixes
