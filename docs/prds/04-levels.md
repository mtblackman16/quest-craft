# PRD 04: Levels & World Design

| Field | Value |
|-------|-------|
| **Status** | In Progress |
| **Author** | Team (Ethan, Eins, Andrew, Nathan) |
| **Date** | 2026-03-08 |
| **Reviewed by** | — |
| **Depends on** | [00-game-concept.md](00-game-concept.md), [02-story-world.md](02-story-world.md), [03-gameplay.md](03-gameplay.md) |

---

## Castle Structure

**15 floors total.** The game takes place inside an ancient castle. Each floor is a level with its own look, enemies, and challenges. The player climbs from the bottom to the top.

**Camera:** Side-scrolling, follows the player.

---

## Color Progression

The castle gets lighter as you climb — a visual story of rising out of darkness.

| Floors | Color Palette | Mood |
|--------|--------------|------|
| 1–3 | Dark bluish-brown | Oppressive, damp, dungeon-like |
| 4–6 | Shifting to red and green | Warming up, more varied |
| 7–8 | Transitioning lighter | Building tension |
| 9–11 | Getting noticeably brighter | Fast-paced, adrenaline |
| 12–14 | Light but ominous | Slow, deadly, memorable |
| 15 | Lightest | The top — final confrontation |

---

## Floor Layout

### Room-Based Structure
- Each floor is a series of **connected rooms** (not one long hallway)
- Rooms include hallways, chambers, open areas, and vertical shafts
- **Partly randomized:** Some rooms/sections are fixed every playthrough (boss arenas, shrines, story moments), other sections randomize (enemy placement, room connections, platform layouts)
- This means every playthrough feels different — major replay value

### Transitions Between Floors
- **Normal floors:** Elevator platform carries you up to the next floor
- **Boss floors:** A tube sucks you up and carries you to the boss — feels tense and dramatic, no turning back

---

## Floor Zones

### Floors 1–8: The Climb (Combat & Exploration)

**General feel:** Learning curve. Each floor introduces new enemies, mechanics, and hazards gradually.

**Features:**
- Rooms with enemies (Small Sanitizer Bottles, Sanitizer Warriors, Jelly Archers)
- Cooking pots with water sources for healing
- Sun patches through broken walls/roofs (drying hazard)
- Shrines with puzzles/parkour for pills and upgrades
- Mix of combat rooms, exploration rooms, and puzzle rooms

**Boss 1: The Big Bottle** (Floor 4)
- Tutorial boss, oversized Small Sanitizer Bottle
- Teaches dodge, attack, and pattern reading

**Boss 2: The Cleanser** (floor 8–10)
- 5-phase platform fight with breaking platforms
- Reward: permanent speed upgrade

---

### Floors 9–11: The Crumbling Floors (Parkour Zone)

**General feel:** Speed and survival. A dramatic mid-game shift from combat to parkour.

**Features:**
- Platforms are ancient and **collapse under you** — keep moving or fall
- **Lasers** block paths, forcing creative routing
- No safe spots to stop and think — constant forward momentum
- Speed upgrade from The Cleanser pays off here
- Splitting mechanic can reveal secret routes and hidden shrines

**Platform behavior:**
- Crumbling platforms break when stepped on
- On Easy/Normal/Hard: platforms eventually respawn
- On Earthquake Mode: platforms NEVER respawn + timer + castle collapse effects

**Enemies:** Reduced — the floor itself is the enemy. Some enemies may appear but the focus is platforming.

---

### Floors 12–14: The Gauntlet (Slow & Deadly)

**General feel:** Slow-paced but brutally hard. The floors players remember and warn their friends about. Dark Souls / Hollow Knight design philosophy.

**Features:**
- **Hidden traps** — learn by dying and remembering
- **Strong enemies in tight corridors** — hard to fight in cramped spaces
- **Running is always an option** but not always safe — sprinting past an enemy might lead straight into a trap
- Trial-and-death learning — memorize the dangers, execute precisely
- Every step matters — no rushing

**Design philosophy:** These floors test mastery of EVERYTHING learned so far. Combat, dodging, platforming, resource management.

---

### Floor 15: The Last Guard (Final Boss)

**General feel:** The lightest, brightest floor. The top of the castle.

**The Last Guard — Three-Phase Fight:**

**Phase 1: The Chase**
- The Guard spots you — RUN
- Dodge his hands grabbing at you
- Tests speed and reflexes

**Phase 2: Hand-to-Hand**
- Stand your ground and fight
- Dodge attacks, find openings, strike
- Tests combat mastery

**Phase 3: The Arrows**
- Large-scale vertical battle
- Jump high, dodge arrows raining down
- Tests platforming mastery

**Difficulty:** Radiance-level (Hollow Knight final boss). Every phase tests a different skill. Demands mastery of the entire game.

**Ending:** The Guard gives up. The Jello Cube wins.

---

## Difficulty & Checkpoints

| Difficulty | Checkpoints | Parkour Floors (9–11) | Special |
|------------|------------|----------------------|---------|
| Easy | Generous | Platforms respawn | — |
| Normal | Standard | Platforms respawn | — |
| Hard | None | Platforms respawn | — |
| Earthquake Mode | None | Platforms NEVER respawn, TIMED, castle collapsing | Achievement + Captain's Hat + secret cutscene |

---

## 8 Shrines (Distributed Across Floors)

- Contain puzzles or small parkour challenges
- Rewards: Jello Powder, elemental pills (Fire, Water, Ice, Electricity, Attack Up), permanent upgrades
- Some are hidden — discoverable via Split mechanic (camera angle change)
- Distribution across floors: TBD (should be spread so players find them regularly)

---

## Platform Types

| Platform | Behavior | Where |
|----------|----------|-------|
| Solid | Always there | All floors |
| Moving | Travels along a path | All floors |
| Crumbling | Breaks when stood on | Primarily floors 9–11, some elsewhere |
| Elevator | Moves vertically between areas | Various floors |

---

## Open Questions

- [ ] Detailed room-by-room design for floors 1–8 (discover during build)
- [ ] Exact shrine placement across 15 floors (discover during build)
- [ ] How many rooms per floor? (discover during build)
- [ ] What fixed vs randomized elements per floor? (discover during build)
- [ ] Are there any secret/bonus floors?
- [ ] Specific enemy placement per floor (discover during build)
- [ ] Laser types on parkour floors (test during build)
