# PRD 01: Characters

| Field | Value |
|-------|-------|
| **Status** | In Progress |
| **Author** | Team (Ethan, Eins, Andrew, Nathan) |
| **Date** | 2026-03-08 |
| **Reviewed by** | — |
| **Depends on** | [00-game-concept.md](00-game-concept.md) |

---

## The Player Character

### Jello Cube

**Appearance:** A small green jelly cube with wobbly jelly physics. Eyes are bubbles inside the jelly that can form shapes — question marks (?), exclamation marks (!), and other expressions. No dialogue needed; emotions show through the bubble eyes.

**Art:** Andrew's hand-drawn illustrations (`assets/images/player/`)
- Front view: `jello-cube-front.png`
- Three-quarter view: `jello-cube-three-quarter.png`

### Moveset

| Move | How It Works | Notes |
|------|-------------|-------|
| **Jelly Shot** (basic attack) | Shoots a glob of jelly at enemies | Costs mass/health — every shot is a risk/reward decision |
| **Ground Pound** | Must be airborne (jump or fall). Smashes down and damages enemies below | Higher fall = bigger impact damage |
| **Perfect Dodge** | Briefly become invulnerable to dodge through an attack | Brief slow-mo effect on success. Confuses dumb enemies (not smart bosses) |
| **Split** | Split into multiple pieces, switch between which piece you control | Changes camera angle, reveals hidden paths, secret shrines, and secrets. Other pieces stay as anchors |
| **Water Absorb** | Temporarily absorb water from sources | Can squirt water into cooking pots, at fire enemies, or to solve puzzles |

### Mass / Health System

- **Health = Mass.** Taking damage and shooting jelly both reduce mass.
- **Visual feedback:** The Jello Cube visually shrinks at ~25% thresholds. A health bar is also displayed at the top of the screen.
- **When mass is low:** The cube is noticeably smaller — players can SEE the danger.

### Healing: Jello Cooking

- **Jello Powder** drops from defeated enemies and puzzle/shrine rewards.
- **Cooking Pots** are scattered around castle floors, each with a small water source nearby.
- **Process:** Absorb water → squirt into pot → add Jello Powder → cook → eat to restore mass.
- **Simmered Water** — rare consumable, no cooking pot needed, also grants heat resistance (prevents drying out).

### Items Stored Inside Body

Items are stored visibly inside the transparent jello body (decided Session 1).

---

## Enemies

### Small Sanitizer Bottle (Basic Enemy)

**Appearance:** A tiny hand sanitizer bottle with little legs.

**Behavior:**
- Walks around on patrol, leaving sanitizer trails on the ground
- Dumb — doesn't actively target the player, just patrols
- Always appears in **pairs on opposite sides** of a room — can't take both out at once
- Sanitizer trails cause damage (mass loss) on contact

**How to Beat:**
- Jelly shot to the back OR ground pound
- When defeated, its sanitizer trails slowly fade away

**Design Role:** Zone control nuisance. Easy to kill individually, but ignoring them lets sanitizer build up across the floor.

---

### Sanitizer Warrior (Medium Enemy)

**Appearance:** Small/medium humanoid enemy. Metal spiked hat. Sanitizer bottle strapped to back, connected via tube to a hand-held launcher with a lever mechanism.

**Art:** Andrew's hand-drawn illustrations (`assets/images/enemies/`)
- Front, side, rear views and equipment spread available

**Behavior:**
- Patrols side-to-side in hallways and rooms
- Pulls lever to fire sanitizer globs that arc through the air at decent range
- Globs that land on the ground create **sanitizer puddles** that damage the player on contact
- Puddles build up over time, controlling space

**How to Beat:**
- **During firing animation**, the spiked hat tips down — exposing the top
- This is the ground pound window — jump above and slam down
- Jelly shots barely damage it and waste mass — a trap for impatient players
- **Smart play:** dodge globs → wait for firing animation → ground pound

**Design Role:** Mid-range tactical enemy. Teaches dodge-and-punish pattern that scales to bosses.

---

### Jelly Archer (Ranged Enemy)

**Appearance:** Dark blue jelly humanoid. No armor — relies on distance. Open sanitizer bottle on back; dips arrows in sanitizer before firing.

**Behavior:**
- Sniper role — stays far back, takes long-range shots
- Sanitizer-tipped arrows cause extra mass loss on hit
- Fragile — no armor, goes down fast if you reach it

**How to Beat:**
- Close the distance and hit with jelly shots or ground pound
- Glass cannon — deadly at range, weak up close

**Design Role:** Forces players to push forward aggressively instead of playing safe. Pairs well with Sanitizer Warriors who punish rushing.

**Open Questions:**
- [ ] Does it run away when you get close?
- [ ] Does the water pill work on it (jelly-based enemy)?
- [ ] Where does it position itself — platforms, hallway ends, behind other enemies?

---

## Bosses

### Boss 1: The Big Bottle (Floor TBD — early)

**Appearance:** Oversized version of the Small Sanitizer Bottle.

**Purpose:** Tutorial boss. Teaches players to:
- Dodge hazards (spreads way more sanitizer than small bottles)
- Use basic attacks on a big target
- Read patterns (watch → learn → punish loop)

**How to Beat:** TBD — needs further design.

**Reward:** TBD (likely health/mass upgrade).

**Open Questions:**
- [ ] How does it attack differently from the small version?
- [ ] What's the weak spot?
- [ ] How many hits to defeat?
- [ ] What floor is it on?
- [ ] Final name?

---

### Boss 2: The Cleanser (Floor 8–10)

**Appearance:** Larger version of the Sanitizer Warrior. Full-sized flask on back instead of a small bottle. Helmet glows with blue flames (can't ground pound the head).

**Arena:** Room with elevated platforms around the edges.

**How to Beat (5-Phase Fight):**
1. Get on a platform around the arena
2. Hit the **elbow nerve** with a precise jelly shot from a platform
3. Elbow locks up → The Cleanser drops its weapon
4. Jump down and ground pound while vulnerable
5. Repeat 5 times total

**Escalation:**
- Phases 1–2: Platforms are stable. Learn the pattern.
- Phases 3–4: Some platforms start **breaking** after you stand on them.
- Phase 5: Platforms become **temporary** — crumble quickly, forcing fast execution.

**Reward:** Permanent **speed upgrade**.

---

### Final Boss: The Last Guard (Floor 15)

**Appearance:** A human guard — the last living person in the castle. Survived by finding a secret food stash. Not evil, just territorial. Only makes grunting noises (no dialogue).

**Three-Phase Fight (Radiance-level difficulty):**

**Phase 1: The Chase**
- The Guard spots you and you RUN
- Dodge his hands grabbing at you
- Tests speed and reflexes (everything parkour floors taught)

**Phase 2: Hand-to-Hand**
- Stop running, fight back
- Dodge attacks, find openings, strike when you can
- Tests combat skills (everything Warrior/Cleanser fights taught)

**Phase 3: The Arrows**
- Large-scale vertical battle — jump high up
- Dodge arrows raining down
- Tests platforming mastery (everything the crumbling floors taught)

**Ending:** The Guard gives up. No killing — he accepts the Jello Cube can't be stopped. You win.

**Earthquake Mode Secret Ending:** After escaping the castle, the Jello Cube falls into a sinkhole — teasing a sequel. Only Earthquake Mode players see this.

---

## Friendly Characters

### Banana Slug (Hint Guide)

**Appearance:** A banana slug that crawls through the scene.

**Behavior:**
- The game detects if the player hasn't made progress for a while
- A slug crawls by, heading toward where the player needs to go
- Completely optional — follow it or ignore it
- Feels like part of the castle's world, not a UI element
- Just a funny, charming detail — no lore reason, just fun

**Interaction:** TBD — may react to ground pounds or jelly shots with a wiggle.

---

## Character Roster Summary

| Character | Type | Role |
|-----------|------|------|
| Jello Cube | Player | Jelly physics, mass-based combat and health |
| Small Sanitizer Bottle | Basic Enemy | Patrol, zone control, pairs |
| Sanitizer Warrior | Medium Enemy | Ranged, tactical, dodge-and-punish |
| Jelly Archer | Ranged Enemy | Sniper, glass cannon, dark blue jelly |
| The Big Bottle | Boss 1 | Tutorial boss, oversized bottle |
| The Cleanser | Boss 2 | 5-phase platform fight, blue flame helmet |
| The Last Guard | Final Boss | Human, 3-phase fight, Radiance difficulty |
| Banana Slug | Friendly | Hint guide, appears when stuck |

---

## Open Questions

- [ ] Are there more enemy types for mid/late castle floors?
- [ ] More bosses between The Big Bottle and The Cleanser?
- [ ] Can the Jello Cube interact with the Banana Slug?
- [ ] Does the Jelly Archer flee when approached?
- [ ] Full details for The Big Bottle boss fight
- [ ] Jelly Archer positioning and water pill interaction
