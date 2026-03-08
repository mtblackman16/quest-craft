# Quest Craft Memory

> Claude reads this file at the start of every session. Keep it updated with key decisions and progress.

---

## Team

| Name | Age | Role |
|------|-----|------|
| Ethan | 9 | Co-creator & Game Designer |
| Eins | 11 | Co-creator & Game Designer |
| Andrew | 11 | Artist & Visual Designer |
| Nathan | 9 | Co-creator & Game Designer |
| Mark | — | Team Advisor |

**Exhibition:** LASD Illuminate — March 15, 2026

---

## Project Status

**Current Phase:** Session 2 — Design (Blocks 1-2 complete, Design Sprint next)
**Game Name:** Split
**Game Type:** 2D side-scrolling platformer with puzzles and stealth
**Core Word:** Survival
**Players:** Single player

---

## Key Decisions

| Date | Decision | By |
|------|----------|---|
| 2026-02-28 | 2D side-scrolling platformer (like Mario/Dead Cells) | Team |
| 2026-02-28 | Player = jello cube with eyeballs, trapped in dark castle dungeon | Team |
| 2026-02-28 | Jello splitting mechanic — split into fourths, squeeze through gaps | Team |
| 2026-02-28 | Health: jello powder + water + cooking pots = more health/size | Team |
| 2026-02-28 | Combat: jello shot (costs mass), ground pound (stun), jello dodge | Team |
| 2026-02-28 | Death = restart from beginning (roguelike tension) | Team |
| 2026-02-28 | BotW-style stealth (? and ! indicators), hidden puzzles in-world | Team |
| 2026-02-28 | Simple/Advanced control toggle for exhibition accessibility | Team |
| 2026-02-28 | School-appropriate: no weapons, jello powers only | Team |
| 2026-02-28 | Items stored visibly inside the transparent jello body | Team |
| 2026-02-28 | Sound: real foley sounds, royalty-free or classical music | Team |
| 2026-02-28 | Game title: **Split** | Team |
| 2026-03-08 | **ART DIRECTION SHIFT:** From pixel art to Andrew's hand-drawn illustration style — detailed, rich digital illustrations with realistic shading, translucent surfaces, and fine detail. Major upgrade from original Dead Cells pixel art plan. | Team |

---

## Game Concept Summary

**Premise:** You are a jello cube trapped in a castle dungeon in the desert. Fight and puzzle your way UP through floors to the rooftop final boss.

**Core Mechanics:** 2D platformer (run, jump, fight) + hidden puzzles (levers, pressure plates) + jello crafting (powder + water + heat = grow/heal) + splitting into fourths + size-based passage restrictions + BotW-style stealth

**Combat:** Jello shot (costs body mass), ground pound (stun), jello dodge (liquid briefly, confuses enemies), ancient shield artifact (light energy shield). Items stored visibly inside transparent body.

**Enemies:** Roly-polys (swarm bugs), alcohol spray bottles (slow deadly shots), Sanitizer Warriors (Andrew's design — purple-skinned warriors with syringe weapons + backpack sanitizer bottles), fire talus (mini-boss, fireballs)

**Items:** Jello powder, water (4 types), fire pill, shrink pill, incense pill, mighty pill, jello armor, jello costume (disguise), hand sanitizer bottles (enemy drops)

**World:** Castle interior — stone walls, vines, torches, creeping gloom. Chests, barrels, hidden barrel shops. Glowing door = next floor up. Desert outside (title screen only).

**Tutorial:** Start in jail cell, contextual teaching like Zelda.

**Controls (Keyboard):** Arrows=move/jump, SPACE=jello shot, Z=split, Down(air)=ground pound, ESC=pause

**Exhibition Top 3:** (1) Core movement + all attacks, (2) Crafting at cooking pots, (3) Enemies to fight

---

## Session 1: Dream (Feb 28) — COMPLETE

All Dream questions answered. Full game concept defined. Spark demo built (`game/spark.py`).

## Session 2 Prep (March 6) — COMPLETE

- Pi readiness verified (Pygame 2.6.1, Pillow 11.1.0, Bluetooth, hid_nintendo)
- Pro Controller paired (MAC: 60:1A:C7:B7:72:9F), button mapping verified via evtest
- Session files created: day2-runbook.md, session-2-claude-guide.md, test_controller.py, controller worksheet
- Asset directories created, Andrew integration plan ready
- startup.sh one-command boot script created

**Controller Button Mapping (VERIFIED — Pi 5 + hid_nintendo + SDL2 2.32.4):**
```
Pygame  0 = B (bottom)       BTN_SOUTH (304)
Pygame  1 = A (right)        BTN_EAST (305)
Pygame  2 = X (top)          BTN_NORTH (307)
Pygame  3 = Y (left)         BTN_WEST (308)
Pygame  4 = Capture          BTN_Z (309)
Pygame  5 = L Bumper         BTN_TL (310)
Pygame  6 = R Bumper         BTN_TR (311)
Pygame  7 = ZL               BTN_TL2 (312)
Pygame  8 = ZR               BTN_TR2 (313)
Pygame  9 = Minus (-)        BTN_SELECT (314)
Pygame 10 = Plus (+)         BTN_START (315)
Pygame 11 = Home             BTN_MODE (316)
Pygame 12 = L Stick Click    BTN_THUMBL (317)
Pygame 13 = R Stick Click    BTN_THUMBR (318)
Axes 0-3 = LStickX, LStickY, RStickX, RStickY
D-pad = Hat 0 (tuple, NOT buttons)
```
NOTE: Online references are WRONG for this setup — always use this verified mapping.

## Session 2 Progress (March 8) — IN PROGRESS

### Block 1: Feedback & Welcome — COMPLETE
- Spark demo played on Pi with Pro Controller
- Every kid had a turn, feedback captured

### Block 2: Photo-to-Sprite Workshop — COMPLETE
- Andrew's artwork uploaded (7 original images in `assets/images/Upload/`)
- Claude analyzed all artwork, split into individual assets, applied transparent backgrounds
- **10 final processed images** organized into folders:

**Player (2):**
- `assets/images/player/jello-cube-front.png` — Front view, translucent emerald green cube (724x722)
- `assets/images/player/jello-cube-three-quarter.png` — 3/4 perspective, shows depth (917x800)

**Enemies (4):**
- `assets/images/enemies/sanitizer-warrior-front-view.png` — Purple warrior, front (1195x1011)
- `assets/images/enemies/sanitizer-warrior-rear-view.png` — Rear view showing backpack bottle (999x940)
- `assets/images/enemies/sanitizer-warrior-side-view.png` — Side profile, primary gameplay sprite (999x940)
- `assets/images/enemies/sanitizer-warrior-equipment-spread.png` — Weapon, hat, bottle spread (1258x490)

**Items (4):**
- `assets/images/items/jelly-powder-bag.png` — "Eins and Ethans" brand jelly powder (492x691)
- `assets/images/items/hand-sanitizer-front.png` — "Germ B Gone" sanitizer bottle (396x975)
- `assets/images/items/hand-sanitizer-back.png` — Back label with detailed fine print (384x938)
- `assets/images/items/dropped-items-in-puddle.png` — Sanitizer + powder in purple puddle (1012x246)

**Asset catalog:** `asset-catalog.txt` — Full natural-language descriptions + hex color references

### Art Direction Shift
Andrew's art is NOT pixel art. It's detailed, rich hand-drawn illustrations with realistic shading, translucent surfaces, and fine detail. The team is shifting AWAY from "Dead Cells pixel art" toward Andrew's higher-resolution illustration style. This is a major creative upgrade that changes the game's visual identity.

### Remaining Session 2 Priorities (in order):
1. **Design Sprint** — Characters, Art Style, Controls, Gameplay (minimum 4 topics via /design)
2. **Level Expansion** — Design multiple castle floors beyond the single demo scene
3. **Higher Resolution Art** — Integrate Andrew's illustrations into the game, replace placeholder rectangles
4. **Music** — Find or create background music for full audio by end of day
5. **Showcase & Wrap** — Learning reflections, git commit, parent summary

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
| 2026-02-28 | Spark demo — title screen + playable jello cube platformer | `game/spark.py` |
| 2026-03-06 | Full Pro Controller support added to Spark | `game/spark.py` |
| 2026-03-08 | Andrew's artwork processed — 10 assets in player/enemies/items | `assets/images/` |

---

## End-of-Session Checklist

Every session ends with:
1. Save all decisions to `memory/MEMORY.md`
2. Update relevant PRDs in `docs/prds/`
3. Git commit + push
4. Generate parent summary HTML in `docs/parent-summaries/session-N-name.html`
5. Mark records Loom video, adds link to summary
6. Email summary to parents

---

## See Also

- `patterns.md` — Code patterns that work
- `lessons.md` — Mistakes and fixes
- `asset-catalog.txt` — Full descriptions of all 10 artwork assets with hex colors
- `docs/andrew-artist-brief.md` — Andrew's original artist brief
- `docs/parent-summaries/TEMPLATE.html` — Reusable parent email template
