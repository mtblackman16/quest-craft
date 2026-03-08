# PRD 05: Art Style

| Field | Value |
|-------|-------|
| **Status** | In Progress |
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

**Parallax scrolling:** TBD — parallax would add depth but needs testing on Pi 5.

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

**Font style:** TBD

---

## Menus

**Title screen:**
- Game title: **Split**
- Background: The desert with the well
- Music: Hollow Knight-style piano (Dirtmouth vibe)
- "Press Start" or similar prompt

**Pause screen:** TBD

**Game Over screen:** TBD

**Difficulty select:** Shown at game start — Easy, Normal, Hard, Earthquake Mode

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

---

## Open Questions

- [ ] Exact character sprite sizes on screen
- [ ] HUD layout details — pill inventory placement
- [ ] Font choice
- [ ] Parallax scrolling — test on Pi 5
- [ ] Pause and Game Over screen designs
- [ ] Menu art style — does it match gameplay or have its own look?
- [ ] How much pixel processing on Andrew's art — need to test and get team approval
