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

### Primary Goals (MUST complete):
1. **Capture feedback** from Session 1 — what the boys loved, what they want changed
2. **Welcome Andrew** — get him oriented, show him the game, hear his ideas
3. **Andrew's art workflow** — teach the photo → Claude → sprite pipeline (this is also an Illuminate learning moment)
4. **Design at least 4 of 7 topics** — Characters, Art Style, Controls, Gameplay (minimum)
5. **Controller test** — pair Pro Controller, verify it works with Pygame

### Stretch Goals (if time permits):
6. Complete all 7 design topics (World, Levels, Sound)
7. Convert one of Andrew's drawings into an actual game sprite
8. Update the Spark demo with controller support

### Exhibition Learning Goals:
- **AI-assisted art pipeline** — taking hand-drawn art, using AI to analyze and convert to game assets
- **Hardware integration** — pairing game controllers with a custom-built game
- **Collaborative design** — 4 kids with different strengths making decisions together

---

## Session Flow

### Block 1: Opening — Feedback & Welcome (20 min)

**1a. Play the Spark Demo (10 min)**
- Run `python3 game/spark.py` on the Pi display
- Every kid gets a turn — including Andrew seeing it for the first time
- Each kid shares: "What's the coolest part?" and "What would you change?"
- Claude captures all feedback in a list

**1b. Welcome Andrew (5 min)**
- Quick introductions (Andrew may not know the other boys well)
- Show Andrew the game concept doc — the one-liner and back-of-the-box blurb
- "You're the artist and creative director. Your job is to make this game look amazing."

**1c. Andrew's Art Show & Tell (5 min)**
- Andrew shows whatever artwork he's brought
- Team reacts — what they love, what matches their vision, what might need adjusting
- Claude describes what it sees (builds trust in AI analysis)

### Block 2: Photo-to-Sprite Workshop (20 min)

> This is a key Illuminate learning moment — document it well.

**The capability being taught:** Taking a real-world drawing, photographing it, and using AI to analyze and convert it into a game asset.

**Step-by-step workflow:**

1. **Andrew draws** (or shows existing drawing) — character, enemy, or item on white paper with bold markers
2. **Take the photo** — phone straight above, no flash, good lighting, paper taped flat
3. **Transfer to Pi** — AirDrop/email photo to laptop → VS Code "Upload..." to `assets/images/`
4. **Claude analyzes** — kids say: "Read `assets/images/andrew-jello-drawing.jpg` — describe what you see"
5. **Claude generates sprite** — kids direct Claude to create a pixel art version (32x32 PNG via Pillow script)
6. **Iterate** — "Make the eyes bigger" / "The green should be brighter" / "Add a darker outline"
7. **Integrate** — Load the sprite in the game and see it running

**Important:** Andrew should feel ownership. HIS drawing becomes THE character. The AI translates his vision — it doesn't replace it.

**Files involved:**
- Input photo: `assets/images/drawings/` (create this directory)
- Output sprites: `assets/images/player/`, `assets/images/enemies/`, etc.
- Conversion script: Claude writes on the fly using Pillow
- Pillow must be installed: `pip install Pillow` (Mark should do this pre-session)

### Block 3: Design Sprint (60-90 min)

Run `/design [topic]` for each topic. Prioritize by importance and Andrew's involvement.

**Recommended order:**

**Priority 1 — Characters (15-20 min)**
- Andrew leads visual descriptions
- Define: player (jello cube details), all enemy types, friendly NPCs (shopkeepers?)
- Flesh out: boss designs (fire talus, floor bosses, final boss)
- Open questions to resolve: final boss design, what alcohol bottles drop
- Andrew draws character sheets during/after discussion
- Output: `docs/prds/01-characters.md`

**Priority 2 — Art Style (15 min)**
- Andrew leads — he's the creative director for visuals
- Finalize: pixel art size (32x32 player?), color palette, sprite style
- Define: backgrounds, HUD layout, menu designs, visual effects (screen shake, particles)
- How Andrew's hand-drawn style translates to pixel art
- Output: `docs/prds/05-art-style.md`

**Priority 3 — Controls (15 min)**
- Map every Pro Controller button to a game action
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

**Priority 5 — Levels (15 min)**
- Level 1 design (tutorial jail cell → first combat → first cooking pot)
- Level 2 and 3 sketches
- Camera system (scrolling direction)
- Output: `docs/prds/04-levels.md`

**Priority 6 — World (10 min)**
- Mostly covered in Session 1 — expand and formalize
- Output: `docs/prds/02-story-world.md`

**Priority 7 — Sound (10 min)**
- Direction set in Session 1 (foley + royalty-free)
- Create the full sound effect list
- Output: `docs/prds/06-sound.md`

### Block 4: Controller Pairing & Test (15-20 min)

**Pre-requisite:** Mark should have already paired the Pro Controller before the session. If not, do it now.

**With the kids:**
1. Run `python3 game/test_controller.py` — see button presses on screen
2. Each kid presses every button — map what does what
3. Fill out the controller diagram on paper (creative activity)
4. If time: Claude adds controller support to `spark.py` and kids playtest with the Pro Controller

**Button mapping reference (Pro Controller in Pygame):**

| Button | Pygame Index | Proposed Action |
|--------|-------------|-----------------|
| B (south) | Button 0 | Jello Shot |
| A (east) | Button 1 | Jump |
| X (north) | Button 2 | Split |
| Y (west) | Button 3 | Interact / Shield |
| Capture | Button 4 | (TBD) |
| L Bumper | Button 5 | Jello Dodge |
| R Bumper | Button 6 | (TBD) |
| ZL | Button 7 | (TBD) |
| ZR | Button 8 | (TBD) |
| Minus | Button 9 | (TBD) |
| Plus | Button 10 | Pause |
| Home | Button 11 | — |
| L Stick Click | Button 12 | (TBD) |
| R Stick Click | Button 13 | (TBD) |
| D-pad | Hat 0 | Menu navigation / alt movement |
| Left Stick | Axis 0,1 | Movement |
| Right Stick | Axis 2,3 | (TBD) |

> **Note:** Let the KIDS decide the mapping. Show them the options and let them argue about it. This is a design decision, not a technical one.

### Block 5: Showcase & Wrap (15 min)

1. Run `/showcase` — Claude summarizes everything designed today
2. Each kid shares their favorite design decision
3. Andrew shows his drawings — these become exhibition material
4. Preview Session 3: "Next time, Claude builds the REAL game from YOUR designs"
5. Commit everything to Git

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

Andrew wasn't at Session 1. He needs to feel included and important immediately.

**Do:**
- Defer to Andrew on ALL visual questions — "Andrew, you're the artist. What do you think?"
- Show genuine interest in his artwork
- Let him see the Spark demo and react before jumping into design
- Position him as creative director for art decisions
- Make sure his artwork physically becomes part of the game (photo workflow)

**Don't:**
- Rush past his art show and tell
- Let the other boys override his visual decisions (he's the art lead)
- Assume he knows everything from the artist brief — re-explain as needed
- Skip the photo workflow — this is his moment and a key exhibition story

---

## Illuminate Documentation

### Key Learning Moments to Capture:
1. **AI-Assisted Art Pipeline** — A kid drew on paper, took a photo, and AI converted it to a game asset. This bridges physical art and digital game development.
2. **Hardware Integration** — Pairing real game controllers with a custom-built game. Understanding input devices.
3. **Collaborative Design** — 4 kids with different strengths (artist, designers) making consensus decisions.
4. **Design Thinking** — Breaking a complex system (a game) into 7 designable components.

### For the Parent Summary:
- Highlight Andrew joining and his art becoming part of the game
- Show the photo-to-sprite pipeline as a "wow" moment
- Mention controller pairing as real hardware engineering
- List the design decisions made

---

## End-of-Session Checklist

- [ ] All feedback from Session 1 captured
- [ ] Andrew oriented and contributing
- [ ] At least one drawing converted to a sprite (photo workflow demonstrated)
- [ ] At least 4 design topics completed with PRDs written
- [ ] Controller paired and tested (at least Pro Controller)
- [ ] Controller mapping decided by the team
- [ ] All decisions saved to `memory/MEMORY.md`
- [ ] PRDs updated in `docs/prds/`
- [ ] Git commit + push
- [ ] Parent summary HTML generated: `docs/parent-summaries/session-2-design.html`
- [ ] `/showcase` learning log filled
