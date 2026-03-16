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

**Exhibition:** LASD Illuminate Inquiry Exhibition — March 27, 2026

---

## Project Status

**Current Phase:** Session 4 — Playtest — COMPLETE (tagged v0.9-playtested)
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
| 2026-02-28 | Jello splitting mechanic — split into pieces, switch control between them | Team |
| 2026-02-28 | Health: jello powder + water + cooking pots = more health/size | Team |
| 2026-02-28 | Combat: jello shot (costs mass), ground pound (stun), jello dodge | Team |
| 2026-02-28 | Death = restart from beginning (roguelike tension) | Team |
| 2026-02-28 | BotW-style stealth (? and ! indicators), hidden puzzles in-world | Team |
| 2026-02-28 | Simple/Advanced control toggle for exhibition accessibility | Team |
| 2026-02-28 | School-appropriate: no weapons, jello powers only | Team |
| 2026-02-28 | Items stored visibly inside the transparent jello body | Team |
| 2026-02-28 | Sound: real foley sounds, royalty-free or classical music | Team |
| 2026-02-28 | Game title: **Split** | Team |
| 2026-03-08 | **ART DIRECTION SHIFT:** From pixel art to Andrew's hand-drawn illustration style | Team |
| 2026-03-08 | 15 castle floors, dark-to-light color progression | Team |
| 2026-03-08 | 4 difficulty modes: Easy, Normal, Hard, Earthquake Mode | Team |
| 2026-03-08 | Earthquake Mode: timed, no checkpoints, crumbling platforms never respawn, secret ending | Team |
| 2026-03-08 | Captain's Hat = only cosmetic, Earthquake Mode reward | Team |
| 2026-03-08 | 5 pills: Fire (75s), Water (75s), Ice (60s), Electricity (90s), Attack Up (60s) | Team |
| 2026-03-08 | 8 shrines with puzzles/parkour, pills, permanent upgrades | Team |
| 2026-03-08 | Floors 9-11 = parkour zone, crumbling platforms + lasers | Team |
| 2026-03-08 | Floors 12-14 = slow/deadly gauntlet, hidden traps, trial-and-death | Team |
| 2026-03-08 | Floor 15 final boss: The Last Guard (human, 3 phases, Radiance difficulty) | Team |
| 2026-03-08 | Boss: The Cleanser (floor 8-10), 5-phase platform fight, speed upgrade reward | Team |
| 2026-03-08 | Banana Slug hint system — appears when player is stuck, crawls toward objective | Team |
| 2026-03-08 | Sun/drying mechanic: broken walls let sun in, 2s grace, fire on head, red screen edges | Team |
| 2026-03-08 | Partly randomized floor layouts (fixed boss/shrine rooms, random enemy/room configs) | Team |

---

## Game Concept Summary

**Premise:** You are a jello cube trapped in a castle dungeon in the desert. Fight and puzzle your way UP through floors to the rooftop final boss.

**Core Mechanics:** 2D platformer (run, jump, fight) + jello crafting (powder + water + cooking pots = heal) + splitting into pieces (switch control, reveals secrets) + mass = health = ammo

**Combat:** Jelly Shot (costs body mass), Ground Pound (airborne, higher fall = more damage), Perfect Dodge (ZR, brief slow-mo, confuses dumb enemies). Items stored visibly inside transparent body.

**Enemies:** Small Sanitizer Bottles (basic patrol, zone control, pairs), Sanitizer Warriors (mid-range tactical, dodge-and-punish), Jelly Archers (dark blue jelly sniper, glass cannon, sanitizer-tipped arrows)

**Bosses:** The Big Bottle (tutorial boss, early floor), The Cleanser (floor 8-10, 5-phase platform fight), The Last Guard (floor 15, human, 3-phase, Radiance difficulty)

**Items:** Jello Powder (healing ingredient), Simmered Water (rare, heat resistance), Elemental Pills (Fire 75s, Water 75s, Ice 60s, Electricity 90s, Attack Up 60s), Captain's Hat (cosmetic, Earthquake Mode only)

**World:** Ancient castle buried under desert sand. 15 floors, dark-to-light color progression. Jello Cube falls through a well, climbs to escape. Environmental storytelling — no dialogue. Unknown substance mutated into sanitizer creatures.

**Tutorial:** Fall through well → pipe → storage room. First enemy teaches controls.

**Controls (Pro Controller):** A=jump, B=jelly shot, X=eat jello, Y=interact, ZL=split/combine toggle, ZR=perfect dodge, L Bumper=switch split piece, Plus=pause, Minus=inventory. Dead Cells weighty feel.

**Difficulty:** Easy/Normal/Hard/Earthquake Mode. Hard+ adds ~25% enemy damage. Earthquake Mode: timed, no checkpoints, platforms never respawn, secret ending.

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

## Session 2 (March 8) — COMPLETE

### Block 1: Feedback & Welcome — COMPLETE
- Spark demo played on Pi with Pro Controller, every kid had a turn

### Block 2: Photo-to-Sprite Workshop — COMPLETE
- Andrew's artwork: 10 processed images in `assets/images/` (player/, enemies/, items/)

### Block 3: Design Sprint — COMPLETE
All 7 design topics completed, all PRDs written:
- Characters: Jello Cube moveset, 3 enemies, 3 bosses, banana slug guide
- Story/World: Castle buried under desert, well opening, environmental storytelling
- Gameplay: Mass system, cooking, 5 pills, 8 shrines, 4 difficulty modes
- Levels: 15 floors, parkour zone (9-11), gauntlet (12-14), 3-phase final boss
- Art Style: Dead Cells cutscene hybrid, subtle pixel texture on Andrew's illustrations
- Sound: Hollow Knight style (Dirtmouth/City of Tears), realistic foley SFX
- Controls: Full Pro Controller mapping, ZL=split toggle, ZR=perfect dodge, Dead Cells weight

### Block 4: Showcase — COMPLETE
- Learning reflections from all 4 team members
- Parent summary generated

### Session 3 TODO:
- Design the inventory screen (Minus button)

## Session 3: Blueprint — COMPLETE

Blueprint session completed. Controller test, technical plan established.

## Session 4: Playtest (March 15) — IN PROGRESS

### Completed:
- Game launched on Pi, Pro Controller paired, all kids played the game
- First full playthroughs completed by all team members
- PRDs covered in depth -- what they are, how Claude uses them
- File and folder structure -- how the project is organized, file types (.py, .md, .json)
- AI Memory -- how memory/MEMORY.md and memory/lessons.md work, why they matter
- Context windows -- how Claude loads PRDs and memories into context, token limits
- Learning logs -- how lessons.md documents repeated issues and improves dev over sessions
- Multiple bugs identified during gameplay

### Completed (continued):
- Bug dictation via Wispr Flow + /bughunt command
- Bug fix rounds -- 22 bugs squashed across gameplay, combat, music, SFX, VFX, levels
- Build Record sheets completed by all 4 kids (physical sheets collected)
- AI Engineer block -- kids watched automated playtest harness run all 15 floors on big screen
- Harness report: 15 floors, 0 crashes, 8 additional bugs identified, 154 screenshots captured
- Victory Lap -- clean playthrough with all fixes applied (did not complete all 15 floors, will continue Session 5)
- HUD pill crash fix (hud.py active_pill was string not dict)
- Controller fixes: Bluetooth ERTM disable, joydev udev rule, USB fallback
- Commits: ed72207 (22 bugs), 3858161 (HUD fixes), 921a6a3 (harness report)

### Session 4 Wrap-Up:
- Kid interviews completed (Andrew, Ethan, Eins) -- saved to learning log
- Tagged v0.9-playtested
- Parent summary live on GitHub Pages
- Nathan missed (brother birthday) -- team will catch him up at school

## Session 5: Showcase -- UPCOMING (March 22, 2026)

### Pre-Session (Mark solo):
- Fix any remaining bugs from Session 4 list + harness findings
- Run 30+ minute soak test
- Print all exhibition materials (10 display board pages, photos, artwork)
- Buy tri-fold display board if not done
- Update 06-reflections.html with Session 4 quotes
- Insert real screenshots and team photos into display HTML files
- Capture 3-5 gameplay screenshots for boards

### Session 5 Plan:
- Quick bug fix pass + final polish (30 min)
- Build the physical display board (45 min)
- Learning Story reflections from each kid (30 min)
- Demo rehearsal -- practice the exhibition pitch (15 min)
- Nathan interview / catch-up
- Full 15-floor playthrough attempt
- Commit and tag v1.0-exhibition
- Final team photo with completed board

### Exhibition: March 27, 2026 (4:00-7:00 PM, setup 3:30)

### RPi5 Performance Optimizations Applied (March 15):
- CPU governor set to performance (persisted via systemd)
- Audio buffer 1024 (from 512), channels 16 (from 32)
- Display: FULLSCREEN | DOUBLEBUF
- Sprite loading: scale instead of smoothscale
- VFX particle alpha caching (8 quantized levels)
- Projectile trail surface caching
- Launcher script: /home/mark/quest-craft/start-game.sh
- VNC (wayvnc) must be killed before gameplay

---

## Design Document Status

| Document | Status |
|----------|--------|
| 00-game-concept | Dream Complete |
| 01-characters | **Complete** |
| 02-story-world | **Complete** |
| 03-gameplay | **Complete** |
| 04-levels | **Complete** |
| 05-art-style | **Complete** (includes sound/music direction) |
| 06-sound | **Complete** (adaptive music system) |
| 07-controls | **Complete** |

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

## Secret Upgrade Plan (Mark's Eyes Only)

**Master Plan:** `docs/plans/secret-upgrade-master-plan.md`
**Branch:** `feature/surprise-upgrade` (to be created)
**Reveal Target:** Session 4 opening

**Family Characters:**
- **Mama Sloth (Linda)** — Hard boss, Floor 4. Slow but devastating. "Bedtime!" sleep wave, "Clean Your Room!" shockwave, "Mom Look" freeze. Photo pending.
- **Gracie** — Medium-hard boss, Floor 2. Fast, chaotic. "Copy Cat!" mirrors player moves, "Tag You're It!" reverses controls. Photo pending.
- **Mark — The Keymaker + The Narrator.** Opens the jail cell door at game start (hand slides key, shadow walks away). Narrator text appears at 12 key moments in a unique font ("They figured it out faster than I expected."). Never named. Never identified. The final line: "This was always their game. I just opened the door."

**6 Expert Reports Filed:**
- Hardware: Pi 5 handles 500+ particles, 20 enemies, 32-ch audio at 60fps/720p
- Game Design: 8 easter eggs, boss fights, interactive credits, hint system
- VFX: 34 effects, 13.6ms budget, 3ms headroom, PerformanceGovernor
- Sound: 69 SFX, 8-sound minimum, SFXManager with spatial panning
- Music: 12 mood states, 4-layer adaptive system, classical sourcing
- Validation: Watchdog, kiosk mode, thermal manager, 15 automated tests

---

## See Also

- `patterns.md` — Code patterns that work
- `lessons.md` — Mistakes and fixes
- `asset-catalog.txt` — Full descriptions of all 10 artwork assets with hex colors
- `docs/andrew-artist-brief.md` — Andrew's original artist brief
- `docs/parent-summaries/TEMPLATE.html` — Reusable parent email template
- `docs/plans/secret-upgrade-master-plan.md` — Full secret upgrade blueprint
- `docs/prds/06-sound.md` — Adaptive music system design
- `docs/prds/06b-sound-effects.md` — Complete SFX catalog
- `docs/prds/08-vfx-system.md` — Visual effects system design
- `docs/plans/validation-qa-strategy.md` — QA & exhibition testing strategy
