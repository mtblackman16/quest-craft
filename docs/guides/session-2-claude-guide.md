# Session 2: DESIGN — Claude's Internal Guide

> Claude reads this at the start of Session 2. It contains the full context, goals, and workflow for the session.

---

## Session Context

**Date:** Sunday, March 8, 2026
**Session:** 2 of 5 — DESIGN (The Deep Dive)
**Time:** ~2.5-3 hours
**Days until exhibition:** 7 (March 15, 2026)
**Previous session:** Session 1 — Dream (Feb 28, 2026) — COMPLETE

**Who's here:**
- Ethan (9) — Co-creator & Game Designer
- Eins (11) — Co-creator & Game Designer
- Andrew (11) — Artist & Visual Designer (NEW — first session with the team)
- Nathan (9) — Co-creator & Game Designer
- Mark — Team Advisor (facilitator)

---

## What Happened in Session 1

The team (minus Andrew) brainstormed and designed the full game concept for **Split**:

- **Game:** Split — 2D side-scrolling platformer where you play as a jello cube with eyeballs, trapped in a dark castle dungeon, fighting upward floor by floor
- **Core mechanic:** Jello splitting — divide into fourths to squeeze through gaps, risk losing pieces
- **Combat:** Jello shot (costs body mass), ground pound (stun), jello dodge (flurry rush)
- **Health system:** Jello powder + water + cooking pots = grow bigger/heal
- **Enemies:** Roly-polys (swarm bugs), alcohol spray bottles (slow deadly shots), fire talus (mini-boss)
- **World:** Dark castle interior — stone walls, vines, torches, creeping gloom
- **Art style:** Dead Cells pixel art
- **Stealth:** BotW-style enemy awareness (? and !)
- **Controls:** Keyboard temporary; controller mapping deferred to this session
- **Spark demo:** Built and running in `game/spark.py` — title screen + playable jello cube with jello shot, ground pound, and split mechanics

**Andrew's status:** Received the artist brief (`docs/andrew-artist-brief.md`) after Session 1. Has been working on artwork independently. This is his first time with the team and with Claude.

**Feedback noted:** The boys had immediate reactions when they saw the Spark demo running. Session 2 should start by capturing that feedback.

---

## Session 2 Goals

### Completed Goals:
1. ~~**Capture feedback** from Session 1~~ — DONE (Block 1)
2. ~~**Welcome Andrew** — get him oriented, show him the game~~ — DONE (Block 1)
3. ~~**Andrew's art workflow** — photo-to-sprite pipeline~~ — DONE (Block 2: 7 images uploaded, 10 assets processed)
4. ~~**Controller test** — Pro Controller works with Spark demo~~ — DONE (pre-session prep)

### Remaining Goals (MUST complete today):
5. **Design at least 4 of 7 topics** — Characters, Art Style, Controls, Gameplay (minimum)
6. **Level expansion** — Design multiple castle floors beyond the single demo scene
7. **Higher resolution art** — Integrate Andrew's illustrations into the game, replacing placeholder rectangles
8. **Music integration** — Find or create background music so the game has full audio by end of day

### Stretch Goals (if time permits):
9. Complete all 7 design topics (World, Levels, Sound)

### Exhibition Learning Goals:
- **AI-assisted art pipeline** — taking hand-drawn art, using AI to analyze and convert to game assets (DEMONSTRATED in Block 2)
- **Hardware integration** — pairing game controllers with a custom-built game (DONE in prep)
- **Collaborative design** — 4 kids with different strengths making decisions together
- **Art direction evolution** — how a team adapts its creative vision when new talent joins

---

## Session Flow

### Block 1: Opening — Feedback & Welcome (20 min) — COMPLETE

> Boys played the Spark demo with Pro Controller. Everyone had a turn.
> Andrew was welcomed and shown the game concept. Feedback captured.

~~**1a. Play the Spark Demo (10 min)**~~
~~**1b. Welcome Andrew (5 min)**~~
~~**1c. Andrew's Art Show & Tell (5 min)**~~

### Block 2: Photo-to-Sprite Workshop (20 min) — COMPLETE

> Andrew's artwork was uploaded (7 images), analyzed by Claude, split into individual assets
> (10 total), organized into player/enemies/items folders, transparent backgrounds applied,
> and `asset-catalog.txt` created with detailed descriptions and hex color references.

**What Andrew drew:**
- Jello cube player character (2 angles: front view + three-quarter view)
- Sanitizer Warrior enemy (3 poses: front, rear, side + equipment spread)
- Jelly powder bag item ("Eins and Ethans" brand)
- Hand sanitizer bottles (front + back with detailed fine-print label)
- Dropped items scene (sanitizer + powder in purple puddle)

**10 processed assets now in:**
- `assets/images/player/` (2 images)
- `assets/images/enemies/` (4 images)
- `assets/images/items/` (4 images)
- Full catalog: `asset-catalog.txt`

**KEY ART DIRECTION SHIFT DISCOVERED:**
Andrew's art is NOT pixel art. It's detailed, rich hand-drawn illustrations with realistic
shading, translucent surfaces, and fine detail. The team is shifting AWAY from "Dead Cells
pixel art" toward Andrew's higher-resolution illustration style. This is a major creative
upgrade that changes the game's visual identity. All remaining design decisions should
reflect this new art direction.

**Andrew's existing artwork serves as templates for creating more characters/items.** His
style guide is now established through these 10 images — any new assets should match his
illustration approach (rich shading, translucent surfaces, hand-drawn feel).

### Block 3: Design Sprint (60-90 min) — NEXT UP

Run `/design [topic]` for each topic. Minimum 4 topics required.

**IMPORTANT — Art Direction Context for ALL Design Topics:**
Andrew's artwork has established a NEW art direction — detailed hand-drawn illustrations,
NOT pixel art. Every design topic discussion should reference this shift. When discussing
visuals, use Andrew's existing 10 images as the style baseline. His Sanitizer Warrior
is the template for how ALL enemies should look. His jello cube is THE player character.

**Recommended order:**

**Priority 1 — Characters (15-20 min)**
- Andrew leads visual descriptions — his existing artwork IS the character designs
- Use Sanitizer Warrior as the template: "Andrew, what should the roly-poly enemies look like in YOUR style?"
- Define: player details (eyeballs? expressions?), all enemy types, friendly NPCs (shopkeepers?)
- Flesh out: boss designs (fire talus, floor bosses, final boss)
- Open questions: final boss design, what alcohol bottles drop, new enemy types inspired by Andrew's sanitizer theme
- Andrew can draw MORE characters during/after discussion — same illustration style
- Output: `docs/prds/01-characters.md`

**Priority 2 — Art Style (15 min)**
- Andrew leads — he IS the creative director for visuals
- **UPDATED:** No longer pixel art. Discuss Andrew's illustration style as the game's look
- Define: sprite resolution (his images are 400-1200px, need in-game scaling strategy)
- Color palette is established (see `asset-catalog.txt` hex colors section)
- Backgrounds: should they match Andrew's detailed style or be simpler to let characters pop?
- HUD layout, menu designs, visual effects (screen shake, particles)
- How to scale Andrew's high-res art for Pygame performance on Pi 5
- Output: `docs/prds/05-art-style.md`

**Priority 3 — Controls (15 min)**
- Map every Pro Controller button to a game action
- Current Spark mapping: A=jump, B=shoot, X=split, stick/dpad=move, Plus=menu
- Design Simple vs Advanced toggle (exhibition accessibility)
- Single Joy-Con sideways support?
- Movement feel: snappy like Mario? How much air control?
- Output: `docs/prds/07-controls.md`

**Priority 4 — Gameplay (15-20 min)**
- Much of this was covered in Session 1 — fill gaps
- Solidify: core loop, difficulty curve, crafting details, power-up interactions
- Resolve: how many floors? What changes per floor?
- Output: `docs/prds/03-gameplay.md`

**If time permits:**

**Priority 5 — Levels (15 min)** — ELEVATED PRIORITY (see Block 4)
- Level 1 design (tutorial jail cell -> first combat -> first cooking pot)
- Level 2 and 3 sketches — expand beyond single demo scene
- Camera system (scrolling direction)
- Output: `docs/prds/04-levels.md`

**Priority 6 — World (10 min)**
- Mostly covered in Session 1 — expand and formalize
- Output: `docs/prds/02-story-world.md`

**Priority 7 — Sound (10 min)** — ELEVATED PRIORITY (see Block 4)
- Direction set in Session 1 (foley + royalty-free)
- Create the full sound effect list
- **Music integration is a session goal** — need at least background music tracks identified/created
- Output: `docs/prds/06-sound.md`

### Block 4: Build Priorities — Levels, Art Integration, Music (30-45 min)

> Controller pairing and testing is ALREADY DONE (Block 1 used Pro Controller with Spark demo).
> This block replaces the original controller pairing plan with the team's updated priorities.

**Priority 4a — Level Expansion (15-20 min)**
- The Spark demo currently has ONE scene — expand to multiple castle floors
- Design at least 2-3 levels with different layouts, enemy placements, and puzzle elements
- Each floor should feel different: lighting, enemy types, platform density
- Kids direct the level design; Claude builds the layouts
- This connects to the Levels design topic from Block 3

**Priority 4b — Higher Resolution Art Integration (10-15 min)**
- Replace placeholder colored rectangles in Spark demo with Andrew's actual illustrations
- Load Andrew's PNGs via Pygame's `pygame.image.load()` and scale to game resolution
- Start with the player character (jello-cube-front.png or jello-cube-three-quarter.png)
- Then enemies (sanitizer-warrior-side-view.png is the primary gameplay sprite)
- Then items (jelly-powder-bag.png as collectible)
- Performance note: Andrew's images are 400-1200px originals — pre-scale at load time, not every frame

**Priority 4c — Music Integration (10 min)**
- Goal: game has background music by end of session
- Options: royalty-free tracks, classical music (public domain), or simple generated loops
- Need at least: title screen music, exploration/puzzle music, combat/tension music
- Pygame mixer can handle OGG/MP3 — place files in `assets/sounds/music/`
- Volume should be lower than sound effects

**Button mapping reference (already working in Spark demo):**

| Button | Pygame Index | Current Action |
|--------|-------------|----------------|
| A (east) | Button 1 | Jump |
| B (south) | Button 0 | Jello Shot |
| X (north) | Button 2 | Split |
| Plus | Button 10 | Menu/Pause |
| Left Stick / D-pad | Axis 0,1 / Hat 0 | Movement |

> **Note:** Full mapping finalization happens during the Controls design topic in Block 3.
> Let the KIDS decide any changes. The current mapping came from pre-session testing.

### Block 5: Showcase & Wrap (15 min)

1. Run `/showcase` — Claude summarizes everything designed today
2. Each kid shares their favorite design decision
3. Andrew shows his drawings — these ARE the game's art now (not just exhibition material)
4. Review what got built: new levels? Andrew's art in the game? Music playing?
5. Preview Session 3: "Next time, Claude builds the REAL game from YOUR designs"
6. Commit everything to Git
7. Generate parent summary highlighting: Andrew's art becoming the game's visual identity, the art direction shift, design decisions made, any new levels/music added

---

## Key Files to Update During Session

| File | What to Update |
|------|---------------|
| `docs/prds/01-characters.md` | Full character designs |
| `docs/prds/02-story-world.md` | World details (if covered) |
| `docs/prds/03-gameplay.md` | Gameplay mechanics |
| `docs/prds/04-levels.md` | Level designs (if covered) |
| `docs/prds/05-art-style.md` | Art style decisions |
| `docs/prds/06-sound.md` | Sound list (if covered) |
| `docs/prds/07-controls.md` | Controller mapping |
| `memory/MEMORY.md` | All new decisions, status update |
| `memory/patterns.md` | Sprite loading pattern, controller input pattern |
| `memory/lessons.md` | Any new lessons learned |
| `game/test_controller.py` | Controller test script (create if not exists) |

---

## Andrew-Specific Considerations

Andrew has now contributed 10 game assets and his art style has become the game's visual identity. He is fully integrated as the art lead.

**Do:**
- Defer to Andrew on ALL visual questions — "Andrew, you're the artist. What do you think?"
- Reference his EXISTING artwork when discussing new characters/enemies: "Andrew, you drew the Sanitizer Warrior — what should the roly-poly look like in your style?"
- Use his art as the baseline for all art style decisions (resolution, color palette, detail level)
- Encourage him to draw MORE characters/items during the design sprint
- When integrating his art into the game, show him the result immediately — seeing his drawings come alive in the game is a powerful moment

**Don't:**
- Let the other boys override his visual decisions (he's the art lead)
- Default back to "pixel art" language — the art direction has shifted to Andrew's illustration style
- Scale or crop his artwork without discussing it with the team first
- Forget to credit his work prominently in the exhibition materials

---

## Illuminate Documentation

### Key Learning Moments to Capture:
1. **AI-Assisted Art Pipeline** — CAPTURED (Block 2). Andrew drew on paper, photos were uploaded, AI analyzed and processed them into 10 game-ready assets with transparent backgrounds. This bridges physical art and digital game development.
2. **Art Direction Evolution** — NEW. The team started with "Dead Cells pixel art" as their vision, but when Andrew's rich illustration style arrived, they pivoted to embrace it. This is real creative leadership — adapting the vision when better ideas emerge.
3. **Hardware Integration** — CAPTURED (Block 1 + prep). Pro Controller working with custom game. Kids played the Spark demo with real controllers.
4. **Collaborative Design** — IN PROGRESS. 4 kids with different strengths (artist, designers) making consensus decisions during the design sprint.
5. **Design Thinking** — IN PROGRESS. Breaking a complex system (a game) into 7 designable components.

### For the Parent Summary:
- Highlight Andrew's art becoming THE game's visual identity (not just illustrations — the actual game art)
- The art direction shift as a story of creative evolution and teamwork
- Show the photo-to-sprite pipeline as a "wow" moment (7 photos in, 10 processed assets out)
- Controller already working — kids played the game with Pro Controller
- List the design decisions made during the sprint
- Any new levels, music, or art integration accomplished

---

## End-of-Session Checklist

- [x] All feedback from Session 1 captured (Block 1)
- [x] Andrew oriented and contributing (Block 1)
- [x] Andrew's drawings converted to game assets — 10 images processed (Block 2)
- [x] Controller paired and tested — Pro Controller working with Spark (pre-session + Block 1)
- [x] Art direction shift documented — from pixel art to Andrew's illustration style
- [ ] At least 4 design topics completed with PRDs written (Block 3)
- [ ] Controller mapping finalized by the team (Block 3 — Controls topic)
- [ ] Level expansion — multiple castle floors designed/built (Block 4)
- [ ] Andrew's art integrated into the game — replacing placeholder rectangles (Block 4)
- [ ] Music added — at least background music tracks (Block 4)
- [ ] All decisions saved to `memory/MEMORY.md`
- [ ] PRDs updated in `docs/prds/`
- [ ] Git commit + push
- [ ] Parent summary HTML generated: `docs/parent-summaries/session-2-design.html`
- [ ] `/showcase` learning log filled
