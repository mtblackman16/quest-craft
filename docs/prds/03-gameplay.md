# PRD 03: Gameplay Mechanics

| Field | Value |
|-------|-------|
| **Status** | In Progress |
| **Author** | Team (Ethan, Eins, Andrew, Nathan) |
| **Date** | 2026-03-08 |
| **Reviewed by** | — |
| **Depends on** | [00-game-concept.md](00-game-concept.md), [01-characters.md](01-characters.md) |

---

## Core Mechanic

**Our core mechanic is:** Mass management — your health IS your ammo. Every jelly shot costs body mass, so every attack is a risk/reward decision.

**Why is it fun?** Players constantly choose between offense and survival. Aggressive players burn through mass fast and need to find cooking pots. Careful players conserve mass but fights take longer.

---

## Player Actions

| Action | How It Works | Notes |
|--------|-------------|-------|
| Move | Left stick / arrows | Standard movement with jelly physics (wobbly) |
| Jump | A button | Needed for ground pound and platforming |
| Jelly Shot | Basic attack button | Costs mass — ammo = health |
| Ground Pound | Down + attack in air | Must be airborne. Higher fall = more damage |
| Perfect Dodge | Timed dodge button | Brief invulnerability. Slow-mo on success. Confuses dumb enemies |
| Split | Split button | Break into pieces, switch control between them. Reveals secrets via camera change |
| Water Absorb | Near water source | Temporarily hold water. Squirt into cooking pots or at enemies/fires |

---

## Health & Lives

**Health = Mass.** The Jello Cube's body mass is its health pool.

**Visual feedback:**
- Health bar displayed at top of screen
- Jello Cube visually shrinks at ~25% thresholds (4 visible size stages)
- Players can SEE how much health they have just by looking at their character

**What happens when the player takes damage?**
- Mass decreases, cube shrinks at thresholds
- Sanitizer contact causes slow mass loss over time
- Sun exposure starts a fire on the jello's head, screen edges turn red and close in

**What happens when the player dies?**
- Depends on difficulty setting (see Difficulty section)

---

## Healing: Jello Cooking System

| Step | What Happens |
|------|-------------|
| 1. Collect Jello Powder | Dropped by enemies, found in shrines/puzzles |
| 2. Find a Cooking Pot | Scattered around castle floors with water source nearby |
| 3. Absorb Water | Walk to water source, absorb it into your body |
| 4. Squirt into Pot | Deposit water into the cooking pot |
| 5. Add Powder & Cook | Combine and cook to create jello |
| 6. Eat | Restore mass/health |

**Simmered Water:** Rare consumable. No pot needed. Also grants heat resistance.

---

## Elemental Pills (Shrine Rewards)

Found at the 8 shrines scattered across the castle. Stored as pills you can swallow whenever you choose.

| Pill | Effect | Duration | Rarity |
|------|--------|----------|--------|
| **Fire** | Extra damage, especially vs sanitizer enemies | 75 seconds | Medium |
| **Water** | Waters down jelly-based enemies, forcing them to regather mass | 75 seconds | Medium |
| **Ice** | Protects from hot/fire areas (heat resistance) | 60 seconds | Rare |
| **Electricity** | Shocks and stuns enemies, giving a free attack window | 90 seconds | Common |
| **Attack Up** | Straight damage boost | 60 seconds | Rare |

**Strategy:** Rare pills (Attack Up, Ice) are shorter — when you pop one, you feel pressure to make it count. Common pills (Electricity) last longer for sustained use.

---

## 8 Shrines

- Scattered across all 15 castle floors
- Each contains a **puzzle or parkour challenge**
- Rewards: Jello Powder, elemental pills, permanent upgrades
- **Permanent upgrades include:** Jelly shot costs less mass, ability improvements
- Some shrines are hidden — discoverable via the Split mechanic (camera angle change)

---

## Environmental Hazards

### Sun / Drying Out
- Broken walls and roofs in hallways let sunshine through
- **2-second grace period** before heat damage starts
- Damage is small but accumulates
- **Visual:** Fire starts on the Jello Cube's head
- **Screen effect:** Edges turn red and slowly close in, blocking view
- **Counters:** Simmered Water, Ice pill, or just move through quickly

### Sanitizer Puddles
- Left by Small Sanitizer Bottles (patrol trails) and Sanitizer Warrior globs
- Contact causes mass loss
- Puddles from defeated bottles slowly fade away

---

## Difficulty Settings

Chosen at game start. Cannot be changed mid-playthrough.

| Difficulty | Checkpoints | Special |
|------------|------------|---------|
| **Easy** | Generous | Learn at your pace |
| **Normal** | Standard | The intended experience |
| **Hard** | None | Fall and restart the floor |
| **Earthquake Mode** | None + TIMED | Castle collapses around you. Crumbling platforms never respawn. Screen shaking, debris falling. |

### Earthquake Mode Rewards
- **Special achievement**
- **Captain's Hat** — equipable cosmetic (the ONLY cosmetic in the game)
- **Secret cutscene** — Jello Cube escapes the castle, falls into a sinkhole, teasing a sequel

---

## Win & Lose Conditions

**How do you WIN:** Defeat The Last Guard on Floor 15.

**How do you LOSE:** Run out of mass (health reaches zero). Restart depends on difficulty setting.

**After winning:**
- Normal ending for Easy/Normal/Hard
- Secret sinkhole cutscene + Captain's Hat for Earthquake Mode

---

## Platform Types

| Platform | Behavior |
|----------|----------|
| **Solid** | Normal, always there |
| **Moving** | Travels along a path, time your jumps |
| **Crumbling** | Breaks when you stand on it. Respawns on Easy/Normal/Hard. NEVER respawns in Earthquake Mode |
| **Elevator** | Moves vertically between areas |

---

## Open Questions

- [ ] Is there a score system?
- [ ] Are there collectibles beyond Jello Powder and pills?
- [ ] Exact button mapping for all actions
- [ ] Can you change difficulty mid-game, or locked in?
- [ ] Does difficulty affect enemy health/damage, or purely checkpoints/timers?
