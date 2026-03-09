# PRD 05: Art Style

| Field | Value |
|-------|-------|
| **Status** | Complete |
| **Author** | Team (Ethan, Eins, Andrew, Nathan) |
| **Date** | 2026-03-08 |
| **Reviewed by** | — |
| **Depends on** | [00-game-concept.md](00-game-concept.md), [01-characters.md](01-characters.md) |

---

## Visual Style

**Direction:** Hybrid — detailed hand-drawn illustrations with a subtle pixel texture. Dead Cells cutscene quality. The pixels are present but not easily noticeable at a glance.

**Art Lead:** Andrew — all character and item illustrations are hand-drawn by Andrew, then lightly pixelized for the game.

**Why this style?** Andrew's detailed illustrations are the game's visual identity. Adding subtle pixel texture gives it a game feel without losing the richness of his artwork. It's a look that's uniquely ours.

**Reference:** Dead Cells cutscenes — detailed, realistic-feeling art with pixel texture underneath. Not chunky retro pixels.

### Processing Pipeline
1. Andrew draws characters/items by hand (detailed illustrations)
2. Artwork is photographed/scanned and cleaned up
3. Subtle pixel processing applied — maintains detail and shading
4. Result: looks like Andrew's art but feels like a game

### Pixel Variation
- Pixel level can **vary across enemies and floors** — keeps things visually interesting
- Not a dramatic change, just subtle variation
- Some elements slightly more pixelated, some less

---

## Color Progression

The castle gets lighter as you climb — visual storytelling through color.

| Floors | Color Palette | Mood |
|--------|--------------|------|
| 1–3 | Dark bluish-brown | Oppressive, damp, underground |
| 4–6 | Shifting to red and green | Warming up, more varied |
| 7–8 | Transitioning lighter | Building tension |
| 9–11 | Noticeably brighter | Fast-paced, adrenaline |
| 12–14 | Light but ominous | Slow, deadly, memorable |
| 15 | Lightest | The top — final confrontation |

---

## Backgrounds

**Castle interior elements (visible in background, not interactive):**
- Stone walls, old torches (flickering light)
- Broken furniture — tables, chairs, fallen armor stands
- Paintings on walls showing the castle's former life
- Vines and moss (especially lower floors)
- Floors 13-15: Sand leaking through cracks in walls and ceilings

---

## Character Art

**Existing artwork (by Andrew, in `assets/images/`):**

| Character | Art Available | Location |
|-----------|-------------|----------|
| Jello Cube | Front view, 3/4 view | `assets/images/player/` |
| Sanitizer Warrior | Front, side, rear, equipment spread | `assets/images/enemies/` |
| Items | Jelly powder bag, hand sanitizer (front/back), dropped items | `assets/images/items/` |

**Still needed:**
- Small Sanitizer Bottle (basic enemy)
- Jelly Archer (dark blue jelly)
- The Big Bottle (boss 1)
- The Cleanser (boss 2)
- The Last Guard (final boss)
- Banana Slug (hint guide)
- Elemental pills
- Cooking pot
- Shrine designs

---

## UI (HUD)

**On-screen during gameplay:**
- Health bar — top of screen (shows mass level)
- Jello Cube visually shrinks at ~25% thresholds (4 size stages)
- Pill inventory — TBD placement
- No mini-map (exploration and getting lost is part of the design)
- Timer visible in Earthquake Mode only

---

## Menus

**Title screen:**
- Game title: **Split**
- Background: The desert with the well
- Music: Hollow Knight-style piano (Dirtmouth vibe)
- "Press Start" or similar prompt
- Difficulty select: Easy, Normal, Hard, Earthquake Mode

---

## Visual Effects (Juice)

| Effect | When |
|--------|------|
| Screen shake | Ground pound impact, boss attacks, Earthquake Mode |
| Fire on Jello's head | Standing in sunlight too long |
| Red screen edges | Prolonged sun exposure, closing in over time |
| Slow-motion | Perfect dodge (brief) |
| Crumble particles | Platforms breaking |
| Sanitizer splash | Globs landing, puddle formation |
| Sand particles | Floors 13-15, sand leaking through cracks |
| Castle collapse debris | Earthquake Mode |
| Jelly wobble | Constant — the Jello Cube is always wobbly |
| Bubble eye expressions | Question marks, exclamation marks showing emotion |

---

## Sound Design Integration

**Music style:** Hollow Knight-inspired orchestral. Piano + strings. Dirtmouth and City of Tears are the reference tracks.

| Zone | Music Vibe |
|------|-----------|
| Floors 1-4 | Dirtmouth-like. Quiet piano, loneliness |
| Floors 5-8 | City of Tears-like. Piano + strings, more layered |
| Floors 9-11 (parkour) | Tempo picks up, urgency with beauty |
| Floors 12-14 (gauntlet) | Stripped back, tense, minimal |
| Floor 15 (final boss) | Full orchestra, emotional peak |
| Boss fights | Intensity spike, percussion added |

**Music source:** Royalty-free orchestral + AI-generated custom tracks.

**Sound effects:** Realistic, foley-based. Organic and tactile. Reference: Dead Cells homunculus crawling sound for Jello Cube movement. Everything should sound WET and PHYSICAL.

**Full SFX list:**

| Category | Sound | Feel |
|----------|-------|------|
| **Player** | | |
| Move/crawl | Quiet squishy squelch | Dead Cells homunculus reference |
| Jump | Soft wet boing, jelly stretching | |
| Land | Wet splat, weight depends on height | |
| Jelly shot | Squelchy launch, wet impact on hit | |
| Ground pound | Heavy wet SLAM, impact reverb | |
| Perfect dodge | Quick liquid whoosh | |
| Split | Wet tearing/separating sound | |
| Merge | Reverse of split — blobs rejoining | |
| Take damage | Wet splatter, lose a chunk | |
| Die | Sad dissolve/deflate | |
| Absorb water | Slurping/soaking in | |
| Squirt water | Water stream into pot | |
| Cooking | Bubbling, simmering | |
| Eat jello | Satisfying slurp/gulp | |
| Pop pill | Small gulp/swallow | |
| **Enemies** | | |
| Bottle walking | Tiny plastic footsteps | |
| Sanitizer spray/fire | Pump action + spray hiss | |
| Archer arrow | Wet twang + whoosh | |
| Sanitizer glob landing | Chemical splash | |
| Enemy hit | Satisfying impact | |
| Enemy death | Pop/burst/dissolve | |
| **World** | | |
| Torches | Soft crackling, flickering | |
| Dripping water | Echoing drips (cave feel) | |
| Platform crumble | Stone cracking, falling | |
| Lasers | Low electric hum | |
| Sand falling (13-15) | Soft hissing grain sound | |
| Cooking pot | Ambient bubbling | |
| Door/transition | Stone grinding | |
| Elevator | Mechanical rising | |
| Tube (boss transition) | Suction whoosh | |
| **UI** | | |
| Menu select | Soft blip | |
| Menu confirm | Satisfying click | |
| Pause | Muted dampening | |
| Achievement unlock | Chime | |
| **Bosses** | | |
| The Cleanser weapon | Heavy mechanical launcher | |
| The Last Guard grunts | Primal, intimidating | |
| Arrow rain (phase 3) | Whistling + impacts | |
