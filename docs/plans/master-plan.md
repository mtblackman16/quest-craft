# Master Plan — Quest Craft

**Exhibition Date: March 27, 2026** (4:00–7:00 PM, setup 3:30 PM)
**Approach: AI-First Game Development**

---

## Pre-Session (Mark) — DONE

- [x] Raspberry Pi set up with all tools
- [x] 5 user accounts created and Claude Code authenticated
- [x] GitHub repo cloned to Pi with group permissions
- [x] Tailscale configured for remote admin
- [x] Send prerequisites doc to parents
- [x] Verify each kid's laptop can SSH to Pi
- [x] Set up Pi with monitor + keyboard for first session

---

## Session 1: DREAM (February 28) — DONE

**Goal:** Crystal clear game vision that everyone agrees on.

- [x] Welcome — introduce the team, the project, the tools
- [x] Connect everyone's laptop to the Pi via VS Code Remote SSH
- [x] Test Wispr Flow — everyone practices talking to Claude
- [x] `/dream` — Full game concept conversation
- [x] Vote on the game name → **SPLIT**
- [x] Creative: Each person wrote the "back of the box" pitch
- [x] `/showcase` — First learning log
- [x] `/spark` — The reveal: game concept comes to life on screen
- [x] Kids played the spark demo with controllers

**Result:** Game concept locked — jello cube platformer, castle setting, 15 floors, split/eat/craft mechanics.

---

## Session 2: DESIGN (March 8) — DONE

**Goal:** Every aspect of the game designed in depth.

- [x] Characters deep dive — JelloCube, enemies, bosses, friendlies
- [x] World building — castle atmosphere, floor themes
- [x] Core mechanics — shoot, split, eat, ground pound, dodge, craft
- [x] Level structure — 15 floors with boss fights at 4, 8, 15
- [x] Art direction — Andrew assigned sprite work
- [x] Sound design — synthesized audio, 10 music zones
- [x] Controller mapping — Pro Controller button layout
- [x] Learning log captured

**Result:** Complete game design docs. All PRDs filled out. Andrew's artist brief created.

---

## Between Sessions 2 & 4: Claude Builds the Game — DONE

Claude built the entire game between sessions:
- 15 floors with unique level data
- 5 bosses (Big Bottle, TheCleanser, TheLastGuard, Gracie, MamaSloth)
- 3 enemy types + 4 projectile/hazard classes
- Full sound system (12 types × 3 variants, synthesized)
- Adaptive music (10 zones)
- HUD, narrator, crafting, stealth, VFX systems
- Title screen, death screen, pause menu, inventory, opening cinematic, credits
- Exhibition hardening (kiosk mode, controller disconnect handling, attract mode)
- Automated playtest harness for overnight testing

---

## Session 4: PLAYTEST (March 14 or 15) — UPCOMING

**Goal:** Kids play the real game, find bugs, watch Claude fix them, gather Illuminate evidence.

**Guide:** `docs/sessions/session-4-playtest.md`

- [ ] First playthrough — uninterrupted, capture reactions and photos
- [ ] Bug fix loop — play → report → Claude fixes → verify → rotate roles
- [ ] Kids fill in Experiment/Build Record sheets (Illuminate Phase 2)
- [ ] Tuning session — jump height, speed, difficulty, feel
- [ ] Reflections captured (Illuminate Phase 3)
- [ ] Block 4: The AI Engineer — watch robot play, set up overnight loop
- [ ] Code committed and tagged `v0.9-playtested`
- [ ] 10+ process photos captured
- [ ] All Build Record sheets collected

**Done when:** Game is fun and stable on Floors 1-3+, all kids have Build Records and reflections.

---

## Between Sessions 4 & 5: Mark Solo Work

- [ ] Fix all bugs from Session 4 bug list
- [ ] Fix anything overnight harness found
- [ ] Update 06-reflections.html with Session 4 quotes
- [ ] Insert real screenshots into display HTML files
- [ ] Insert team/process photos into display HTML files
- [ ] Art integration (Andrew's sprites, if available)
- [ ] Print ALL exhibition materials (10 display board pages)
- [ ] Print gameplay screenshots, artwork, team photos
- [ ] Buy tri-fold board if parents haven't
- [ ] 2-hour soak test on Pi

---

## Session 5: SHOWCASE (March 21 or 22) — UPCOMING

**Goal:** Assemble display board, capture deep reflections, practice demo.

**Guide:** `docs/sessions/session-5-showcase.md`

- [ ] Quick bug fixes + final polish (30 min)
- [ ] Build the display board — physical assembly with printed materials (45 min)
- [ ] Learning Story reflections — each kid picks PMI, Bridge, or Freeze Frame (30 min)
- [ ] Demo rehearsal — practice the exhibition script (15 min)
- [ ] Code freeze: `git tag v1.0-exhibition`
- [ ] Backup SD card

**Done when:** Board assembled, reflections captured, demo practiced, code frozen.

---

## Final Prep (March 23-26): Mark Solo

- [ ] Any last-minute fixes from Session 5
- [ ] Update reflections HTML with Session 5 quotes
- [ ] Re-print any updated pages
- [ ] Full dress rehearsal at home
- [ ] Soak test: 3+ hours without crash
- [ ] Charge all controllers to 100%
- [ ] Back up SD card (full disk image)
- [ ] Prepare backup SD card
- [ ] Pack everything (exhibition-checklist.md)

---

## Exhibition Day (March 27)

- 3:00 PM — Load car
- 3:30 PM — Arrive, set up table, Pi, monitor, display board
- 3:50 PM — Boot game, pair controller, sound check
- 4:00–7:00 PM — Exhibition! Kids rotate roles every 30 min.
- 7:30 PM — Pack up

---

## Illuminate Evidence Summary

| Phase | What Illuminate Asks | What We Have |
|-------|---------------------|--------------|
| **Phase 1:** Investigate | Inquiry question + plan | Inquiry question, PRDs, design docs |
| **Phase 2:** Discover | Evidence of learning process | Build Records from Session 4, bug lists, process photos, "By the Numbers" |
| **Phase 3:** Reflect | Structured reflections | Session 4 reflections, Session 5 Learning Stories (PMI/Bridge/Freeze Frame) |
| **Phase 4:** Share | Exhibition artifact + ability to discuss | Live game demo, display board, practiced demo script |

---

## Display Board Materials (10 pages)

| # | File | Content |
|---|------|---------|
| 01 | `docs/exhibition/01-title-card.html` | SPLIT title + tagline |
| 02 | `docs/exhibition/02-inquiry-question.html` | Our driving question |
| 03 | `docs/exhibition/03-our-process.html` | How We Built It + tools + stats |
| 04 | `docs/exhibition/04-the-game.html` | Game description + screenshot |
| 05 | `docs/exhibition/05-the-team.html` | Team bio + photo |
| 06 | `docs/exhibition/06-reflections.html` | What We Learned — kid quotes |
| 07 | `docs/exhibition/07-how-to-play.html` | Controls for visitors |
| 08 | `docs/exhibition/08-controller-diagram.html` | Controller diagram |
| 09 | `docs/exhibition/09-supply-list.html` | Internal supply checklist |
| 10 | `docs/exhibition/10-learning-journey.html` | Illuminate 4-phase learning story |
