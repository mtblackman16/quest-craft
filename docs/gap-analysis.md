# SPLIT -- Design vs. Implementation Gap Analysis

> **Purpose:** Compare everything the team designed in the PRDs (Sessions 1-2) against what actually exists in the game code. This helps the team decide what to prioritize adding, fixing, or accepting as "good enough" for the exhibition.
>
> **Date:** 2026-03-15
>
> **Legend:**
> - IMPLEMENTED = fully in the code and working
> - PARTIAL = exists but incomplete or different from the design
> - MISSING = not in the code at all
> - EXTRA = in the code but not in the original design (Claude added it)

---

## 1. Player Mechanics (Movement, Combat, Abilities)

### Designed (PRD 00, 01, 03, 07)

The Jello Cube has these moves: Move (left stick), Jump (A), Jelly Shot (B, costs mass/health), Ground Pound (down while airborne), Perfect Dodge (ZR, brief invulnerability with slow-mo), Split (ZL, break into pieces, switch with L), Water Absorb (near water sources), Eat Jello Powder (X, heal/restore mass).

The cube visually shrinks at ~25% health thresholds (4 visible size stages). Items are stored visibly inside the transparent jello body. Health = Mass = Ammo (every jelly shot costs body mass).

### Implemented

- **Move**: IMPLEMENTED -- left stick and keyboard arrows (`game/entities/player.py` line 156+)
- **Jump**: IMPLEMENTED -- A button / Space, with coyote time frames
- **Jelly Shot**: IMPLEMENTED -- B button / Z key, fires `JelloProjectile`, costs `JELLY_SHOT_COST` (5) from powder count, NOT health/mass
- **Ground Pound**: IMPLEMENTED -- stick down while airborne, `GROUND_POUND_SPEED = 20`
- **Perfect Dodge**: IMPLEMENTED -- ZR / E key, `PERFECT_DODGE_FRAMES = 10` (~167ms), `dodge_invulnerable` flag
- **Split**: IMPLEMENTED -- ZL / Q key, `SPLIT_DURATION = 180` (3 seconds), switch with L/Tab
- **Water Absorb**: IMPLEMENTED -- interact with `WaterSource`, sets `player.has_water = True`
- **Eat Jello Powder**: IMPLEMENTED -- X button / X key, heals from powder count
- **Speed Multiplier**: IMPLEMENTED -- `speed_multiplier` attribute for Cleanser reward
- **Freeze**: IMPLEMENTED -- `freeze_timer` for MamaSloth Mom Look effect

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Jelly Shot costs mass/health** | **HIGH** | PRD says "costs mass -- ammo = health." Code uses `jello_powder_count` as ammo instead of reducing health. This was a CORE design decision: "every shot is a risk/reward decision." The current system separates ammo from health, which changes the entire tension. |
| **Visual size shrinking at 25% thresholds** | **HIGH** | PRD says the cube visually shrinks at ~25% health thresholds (4 size stages). The code has a fixed `base_w` / `base_h` of `PLAYER_BASE_SIZE (96)` that never changes based on health. The player looks the same at 100 HP and 10 HP. |
| **Items visible inside body** | **MEDIUM** | PRD says items stored visibly inside the transparent jello body. Code does not draw items inside the cube. |
| **Perfect Dodge slow-mo** | **MEDIUM** | PRD says "brief slow-mo effect on success." Code has the invulnerability frames but no slow-motion effect on successful dodge. The VFX system has a hitstop mechanism but no slow-mo toggle. |
| **Perfect Dodge confuses enemies** | **LOW** | PRD says dodge "confuses dumb enemies (not smart bosses)." The stealth system resets sanitizer bottles to IDLE on dodge within 80px (`game/systems/stealth.py` line 104-114). This IS implemented. |
| **Ground pound damage scales with height** | **LOW** | PRD says "higher fall = bigger impact damage." Unclear if the code scales damage with fall distance or uses a fixed value. |
| **Jelly wobble physics on body** | **LOW** | Code has squash/stretch (`squish`, `squish_v`, `jiggle_phase`) but not the sine-wave edge deformation described in PRD 08 VFX. The simpler squash-stretch is fine for exhibition. |

---

## 2. Items & Inventory

### Designed (PRD 00, 01, 03)

**Water Types:** Small (1 use), Normal (2 uses), Big Tank (5 uses), Simmered Water (already hot, no pot needed, grants heat resistance).

**Pills:** Fire (extra damage vs sanitizer), Water (waters down jelly enemies), Ice (heat resistance), Electricity (stuns enemies), Attack Up (damage boost). Found at 8 shrines.

**Equipment:** Ancient Shield (light energy shield), Jello Armor (defense up), Jello Costume (disguise as roly-poly, fools bottles not bosses).

**Earthquake Mode Rewards:** Captain's Hat cosmetic, secret cutscene (sinkhole sequel tease).

### Implemented

- **Water**: PARTIAL -- `has_water` is a boolean flag (True/False), no multiple water types
- **Pills**: IMPLEMENTED -- All 5 pill types exist in `PillType` enum with durations in `PILL_DURATIONS` (`game/engine/settings.py` lines 48-54). Inventory system in `game/systems/crafting.py`. UI in `game/ui/inventory.py`.
- **Jello Powder**: IMPLEMENTED -- `jello_powder_count` on player, drops from chests
- **Inventory Screen**: IMPLEMENTED -- Opens with Minus button, shows powder, pills, water status (`game/ui/inventory.py`)

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Multiple water types** | **LOW** | PRD designed Small/Normal/Big/Simmered water. Code has a single boolean `has_water`. For exhibition, a single water type is fine. |
| **Simmered Water (no pot needed, heat resist)** | **LOW** | Not implemented. Would need a new consumable item type. |
| **Ancient Shield** | **MEDIUM** | PRD 00 describes an "Ancient Shield -- square artifact, projects a light energy shield." Not in the code at all. No shield mechanic exists. |
| **Jello Armor** | **MEDIUM** | PRD 00 describes "Jello Armor -- defense up, absorbs damage." Not implemented. No armor/defense stat. |
| **Jello Costume / Disguise** | **LOW** | PRD 00 describes disguise as roly-poly that fools bottles. Not implemented. Fun idea but complex. |
| **Pill effects in combat** | **MEDIUM** | Pills exist in inventory but their actual combat effects (fire = extra damage, water = enemy mass loss, electricity = stun, etc.) need verification that the combat system applies them. The `crafting.get_pill_effect()` method returns the active pill but it's unclear if `game/systems/combat.py` uses it. |
| **Captain's Hat (Earthquake reward)** | **LOW** | Not implemented. Only cosmetic in the game per design. Low priority for exhibition. |
| **Secret sinkhole cutscene** | **LOW** | The Earthquake Mode ending with the sequel-teasing sinkhole is not implemented. Credits exist but no special ending variant. |
| **Shrines give pills/upgrades** | **MEDIUM** | Shrine class exists in `game/world/interactables.py` but `interact()` just returns True -- no actual puzzle, reward, or pill-granting logic. Shrines are placeholders. |

---

## 3. Enemies

### Designed (PRD 01)

Three enemy types:
1. **Small Sanitizer Bottle** -- Patrols, leaves sanitizer trails, always in pairs, dumb, beat by jelly shot to back or ground pound
2. **Sanitizer Warrior** -- Patrols, fires sanitizer globs that create puddles, beat by ground-pounding during firing animation when spiked hat tips down exposing top
3. **Jelly Archer** -- Sniper, stays far back, sanitizer-tipped arrows, fragile glass cannon, dark blue jelly

### Implemented (`game/entities/enemies.py`)

- **SmallSanitizerBottle**: IMPLEMENTED -- Patrols, leaves `SanitizerTrail`, has `SMALL_BOTTLE_HP = 30`
- **SanitizerWarrior**: IMPLEMENTED -- Patrols, fires `SanitizerGlob` that creates `SanitizerPuddle`, has `SANITIZER_WARRIOR_HP = 60`
- **JellyArcher**: IMPLEMENTED -- Fires `SanitizerArrow`, has `JELLY_ARCHER_HP = 20`

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Bottles always in pairs** | **LOW** | PRD says bottles "always appear in pairs on opposite sides of a room." Level JSONs sometimes have single bottles. This is a level design detail, not a code issue. |
| **Warrior vulnerable window** | **MEDIUM** | PRD says "during firing animation, the spiked hat tips down -- exposing the top. This is the ground pound window." Code does not seem to have a specific vulnerable state during firing. Warriors take damage from any source at any time. The designed dodge-and-punish pattern is not enforced. |
| **Warrior: jelly shots barely damage** | **LOW** | PRD says "jelly shots barely damage it and waste mass -- a trap for impatient players." Code does not differentiate damage from jelly shots vs ground pounds on warriors. |
| **Archer fleeing behavior** | **LOW** | PRD left as open question: "Does it run away when you get close?" Unknown if implemented. |
| **Trails fade after bottle death** | **LOW** | PRD says "when defeated, its sanitizer trails slowly fade away." Unclear if trails are cleared on bottle death. |
| **Stealth awareness indicators** | **IMPLEMENTED** | The ? and ! indicators from BotW are fully implemented in `game/systems/stealth.py` with IDLE, SUSPICIOUS, ALERT, HUNTING, LOST states. |

---

## 4. Bosses

### Designed (PRD 01, 04)

Three bosses were designed:
1. **The Big Bottle** (Floor 4) -- Tutorial boss, oversized sanitizer bottle
2. **The Cleanser** (Floor 8-10) -- 5-phase platform fight, blue flame helmet, elbow nerve weak point
3. **The Last Guard** (Floor 15) -- Human guard, 3-phase fight (Chase, Hand-to-Hand, Arrows)

PRD 01 explicitly says: "3 bosses total. No additional bosses needed."

### Implemented (`game/entities/bosses.py`)

- **BigBottle**: IMPLEMENTED -- `BIG_BOTTLE_HP = 200`, boss on a floor
- **TheCleanser**: IMPLEMENTED -- `CLEANSER_HP = 400`, 5 phases, elbow nerve hitbox, helmet blocks head damage, glob + puddle attacks, stun mechanic
- **TheLastGuard**: IMPLEMENTED -- `LAST_GUARD_HP = 500`, 3 phases (Chase with grab attack, Hand-to-Hand with 3-hit combo + slam, Arrows with rain + aimed arrows)
- **Gracie**: EXTRA -- `GRACIE_HP = 250`, "Secret Floor 2 Boss", 2-phase fight with Copy Cat, Tag You're It, Cannonball mechanics
- **MamaSloth**: EXTRA -- `MAMA_SLOTH_HP = 600`, "Secret Floor 4 Boss", 3-phase fight with Homework Time, Clean Your Room, Mom Look, Snack Time heal

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Gracie and MamaSloth are EXTRA** | **NOTE** | These 2 bosses were NOT in the kids' design. Claude added them. They're fully implemented and playable. The kids should know these exist and decide if they want to keep/modify them. |
| **Big Bottle attack patterns** | **MEDIUM** | PRD says "details to be tuned during build -- core pattern is dodge sanitizer, find opening, attack." Needs playtest verification that the Big Bottle fight feels like a proper tutorial boss. |
| **Cleanser permanent speed upgrade reward** | **MEDIUM** | PRD says "Reward: permanent speed upgrade." Player has `speed_multiplier` attribute. Need to verify this is actually granted on Cleanser defeat. |
| **Last Guard ending (gives up, not killed)** | **MEDIUM** | PRD says "The Guard gives up. No killing." The boss has a `DEFEATED` state with a sitting-down animation in the draw method. This appears implemented but needs playtest verification. |
| **Boss floor placement** | **MEDIUM** | PRD says Big Bottle on Floor 4, Cleanser on Floor 8-10, Last Guard on Floor 15. Need to verify the level JSONs and main.py spawn bosses on the correct floors. No boss data appears in the level JSON files -- boss spawning must be handled elsewhere in `game/main.py`. |

---

## 5. World & Environment

### Designed (PRD 02, 04, 05)

**15 floors** with distinct visual zones:
- Floors 1-3: Storage rooms, dark bluish-brown, moss, dripping water
- Floors 4-6: Dining halls, shifting red/green, tables, chairs, broken dining areas
- Floors 7-8: Ornate chambers, lighter, paintings, grand architecture
- Floors 9-11: Parkour zone, crumbling architecture, lasers, speed challenge
- Floors 12-14: The gauntlet, light but ominous, hidden traps, sand through cracks
- Floor 15: The top, lightest, final boss

**Environmental details:** Old torches flickering, broken furniture, vines/moss, paintings, sand leaking through cracks (floors 12-15).

**Room-based structure** with partly randomized layouts per playthrough.

**Sun exposure zones** through broken walls/roofs: 2-second grace, then slow damage, fire on head, red screen edges.

### Implemented

- **15 Floors**: IMPLEMENTED -- `game/data/levels/floor_01.json` through `floor_15.json`
- **Color palettes per floor**: IMPLEMENTED -- `FLOOR_PALETTES` in `game/engine/settings.py` (lines 222-244) with unique 4-color tuples per floor
- **Platform types**: IMPLEMENTED -- Solid, Moving, Crumbling, Elevator in `game/world/platforms.py`
- **Transitions**: IMPLEMENTED -- Elevator and tube types in level JSONs
- **Level loader**: IMPLEMENTED -- `game/world/level.py` parses JSON, creates platforms, enemies, interactables
- **Interactables**: IMPLEMENTED -- CookingPot, WaterSource, Chest, Door, Shrine, SunZone in `game/world/interactables.py`
- **Torch glow**: PARTIAL -- Background gradient cached per floor, torch glow cache mentioned in `game/main.py`
- **Floor names**: IMPLEMENTED -- e.g. "Storage Rooms" (Floor 1), "Dining Halls" (Floor 4), "Ornate Chambers" (Floor 7), "Parkour Zone I" (Floor 9), "The Top" (Floor 15)

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Randomized room layouts** | **LOW** | PRD says "partly randomized -- some rooms/sections are fixed every playthrough, other sections randomize." Code has fixed JSON level files with no randomization. Each playthrough is identical. This is fine for exhibition -- randomization adds complexity. |
| **Sun exposure / drying hazard** | **MEDIUM** | PRD describes sun patches through broken walls (2-second grace, fire on head, red screen edges). `SunZone` class EXISTS in `game/world/interactables.py` with the 120-frame grace period and damage-per-tick. However, NO level JSON files contain sun_zone entries. The mechanic is coded but never placed in any level. |
| **Lasers on parkour floors (9-11)** | **MEDIUM** | PRD says "Lasers block paths, forcing creative routing" on floors 9-11. No laser class or mechanic exists in the code at all. |
| **Environmental storytelling details** | **LOW** | PRD describes broken furniture, paintings, vines/moss, armor on walls, sand through cracks. Code draws stone platforms with procedural moss patches and stone-block grooves (`SolidPlatform._build_cache`). Background decorations (furniture, paintings, sand) are NOT rendered. |
| **Torches on castle walls** | **PARTIAL** | Torch glow is referenced in `game/main.py` (cached torch glow surface). Background has a gradient. But individual wall-mounted torches with flickering light are not visible as interactive/decorative objects in levels. |
| **Opening sequence (well + pipe)** | **PARTIAL** | PRD describes falling down a well, through a pipe, into the storage room. `game/ui/opening.py` exists as a cinematic intro (~9 seconds, shape-based animation). Need to verify it matches the well/pipe/storage room narrative. |
| **Crumbling floors 9-11 emphasis** | **IMPLEMENTED** | Floor 9 JSON has many crumbling platforms as designed. The parkour zone works. |

---

## 6. Crafting & Cooking

### Designed (PRD 01, 03)

Process: Collect Jello Powder (from enemies/shrines) -> Find Cooking Pot -> Absorb Water -> Squirt into Pot -> Add Powder & Cook -> Eat to restore mass.

Cooking pots scattered around castle floors with water sources nearby.

### Implemented

- **Cooking Pot**: IMPLEMENTED -- `CookingPot` class in `game/world/interactables.py` with state machine: EMPTY -> NEEDS_WATER -> NEEDS_POWDER -> COOKING -> DONE -> heals player
- **Water Source**: IMPLEMENTED -- `WaterSource` class, sets `player.has_water = True`
- **Crafting System**: IMPLEMENTED -- `game/systems/crafting.py` manages pill inventory, active pill effects, cooking pot interaction
- **Pot placement**: IMPLEMENTED -- Level JSONs include cooking pots and water sources on multiple floors

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Powder drops from enemies** | **MEDIUM** | PRD says jello powder drops from defeated enemies. `Chest.on_opened()` grants 1 powder. Need to verify enemies also drop powder on death. If they don't, the only powder source is chests, which limits healing. |
| **Cooking animation/feedback** | **LOW** | The pot has bubble animations during cooking state. The 60-frame cook time provides feedback. This works. |
| **Pill cooking from pot** | **PARTIAL** | `CraftingSystem.interact_with_pot()` has logic for cooking powder into pills, but `CookingPot.interact()` directly heals the player without going through the crafting system's pill logic. There appear to be two parallel systems. |

---

## 7. Sound & Music

### Designed (PRD 05, 06b)

**Music:** Hollow Knight-inspired orchestral. Piano + strings. Adaptive per zone:
- Floors 1-4: Dirtmouth-like quiet piano
- Floors 5-8: City of Tears-like piano + strings
- Floors 9-11: Tempo picks up, urgency
- Floors 12-14: Stripped back, tense, minimal
- Floor 15: Full orchestra, emotional peak
- Boss fights: Intensity spike, percussion added

**Sound Effects (PRD 06b extensive catalog):** 12+ categories of foley sounds -- squishy footsteps, wet boing jump, wet splat landing, squelchy jelly shot, heavy wet SLAM ground pound, liquid whoosh dodge, wet tearing split, and many more. Real foley feel, not 8-bit.

### Implemented

- **Adaptive Music**: IMPLEMENTED -- `game/systems/music.py` with `MusicZone` enum (TITLE, FLOORS_1_4, FLOORS_5_8, FLOORS_9_11, FLOORS_12_14, FLOOR_15, BOSS, DEATH, VICTORY, SECRET). Synthesized ambient drones with crossfading.
- **Sound Effects**: IMPLEMENTED -- `game/systems/sound.py` generates all SFX via numpy synthesis at startup. No .wav files needed. Falls back gracefully if numpy unavailable.
- **Audio channels**: IMPLEMENTED -- 16 channels split: 0-3 music, 5-7 stingers, 8-15 SFX

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Synthesized vs real foley** | **MEDIUM** | PRD 06b extensively describes real foley sounds (wet, physical, tactile). The code generates all sounds via numpy sine waves, noise, and envelopes. These are synthetic bleeps/bloops, NOT the wet squishy jello sounds described. For exhibition polish, even basic WAV recordings placed in `assets/sounds/effects/` would massively improve the game feel. The code supports WAV fallback. |
| **Hollow Knight-style orchestral music** | **MEDIUM** | The code synthesizes ambient drones per zone. These are not the "piano + strings" orchestral tracks described in the design. Real music tracks (royalty-free or AI-generated) placed in `assets/sounds/music/` would dramatically improve atmosphere. |
| **Volume controls** | **LOW** | PRD asks about player-adjustable volume. No volume settings exist in the UI. |
| **Laser sounds** | **N/A** | PRD lists "lasers -- low electric hum." Lasers don't exist, so this is moot. |
| **Sand falling sounds (floors 12-15)** | **LOW** | Not implemented since sand hazard visuals don't exist either. |

---

## 8. Story & Narrator

### Designed (PRD 02)

Story told through environment, not dialogue. An unseen narrator voice comments on key moments. Post-game reveal: microorganisms eating the unknown substance. Earthquake Mode secret ending: sinkhole.

### Implemented

- **Narrator System**: IMPLEMENTED -- `game/systems/narrator.py` with one-shot messages triggered by game events. 11 narrator lines defined in `NARRATOR_LINES` (`game/engine/settings.py` lines 267-279).
- **Event triggers**: IMPLEMENTED -- First death, first kill, first secret, first split, first boss encounter, first boss defeat, Mama Sloth defeat, Gracie defeat, final boss reach, architect room, post-credits.
- **Opening cinematic**: IMPLEMENTED -- `game/ui/opening.py`, ~9 seconds, shape-based animation, skip with A/Space.
- **Credits**: IMPLEMENTED -- `game/ui/credits.py`, interactive walkable corridor with team pedestals, tools, timeline, thank-you door, post-credits scene.

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Environmental storytelling details** | **LOW** | PRD describes visual storytelling (broken furniture, paintings, armor). Code has functional levels but minimal background decoration. |
| **Post-game microorganism reveal** | **LOW** | PRD describes tiny creatures eating the substance. Not implemented. |
| **Earthquake Mode sinkhole ending** | **LOW** | Not implemented. Credits are the same for all difficulties. |
| **Story progression through floor themes** | **PARTIAL** | Floor names hint at progression (Storage Rooms -> Dining Halls -> Ornate Chambers -> Parkour -> The Top). Color palettes progress from dark to light. But the rich environmental details described in PRD 02 are not visually present. |

---

## 9. UI & HUD

### Designed (PRD 05)

On-screen during gameplay: Health bar (top), jello cube visually shrinks, pill inventory, no mini-map, timer in Earthquake Mode.

Title screen: Game title, desert background with well, difficulty select (Easy/Normal/Hard/Earthquake).

### Implemented

- **HUD**: IMPLEMENTED -- `game/systems/hud.py` with health bar (jiggle on damage), powder count (diamond icon), floor number, split indicator, pill timer, run counter, damage numbers, earthquake timer
- **Title Screen**: IMPLEMENTED -- `game/ui/title_screen.py` with animated jello cube, difficulty selection, particles, torch glow, Konami code, controller hot-plug, attract mode
- **Death Screen**: IMPLEMENTED -- `game/ui/death_screen.py`
- **Pause Menu**: IMPLEMENTED -- `game/ui/pause_menu.py`
- **Inventory Screen**: IMPLEMENTED -- `game/ui/inventory.py` with powder count, pills, active pill timer, water status
- **Credits**: IMPLEMENTED -- `game/ui/credits.py`, interactive walkable corridor

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Visual cube shrinking in HUD** | **HIGH** | PRD says the jello cube itself visually shrinks at ~25% thresholds. The HUD has a health bar but the player character stays the same size regardless of health. This was a signature visual feature of the design. |
| **Title screen background** | **LOW** | PRD describes "desert with the well" background. Code has an animated jello cube with dungeon aesthetic and particles. Different from spec but probably looks good. |
| **Settings/Controls page on title** | **LOW** | PRD mentions "Buttons: Play, Settings, Controls. Controls page has a Simple/Advanced toggle." Title screen has difficulty selection but no settings or controls page. |

---

## 10. Controls & Input

### Designed (PRD 07)

Full Pro Controller mapping with all buttons assigned. D-pad unused. Keyboard backup.

### Implemented

- **Pro Controller**: IMPLEMENTED -- Full mapping in `game/engine/settings.py` lines 183-206, verified on Pi 5 hardware
- **Keyboard**: IMPLEMENTED -- Full keyboard backup mapping lines 209-218
- **D-pad**: Used for movement (Hat 0), despite PRD saying unused. The memory file says "D-pad is Hat 0 for movement."
- **Ground Pound**: IMPLEMENTED -- Stick down while airborne (edge detection in `game/main.py`)
- **Right Stick camera shift**: Referenced in camera system
- **Controller disconnect handling**: IMPLEMENTED -- Reconnect overlay in `game/main.py`

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Controls feel ("Dead Cells weight")** | **MEDIUM** | PRD emphasizes weighty, physical feel with "satisfying impact" and brief settle/wobble on stop. The code has squash-stretch physics. Needs playtesting to verify it feels heavy enough. |
| **A/B button swap concern** | **NOTE** | Memory notes: "Controller A/B buttons may feel swapped -- needs playtesting with kids." This is a known issue for Session 4. |

---

## 11. Stealth System

### Designed (PRD 00)

Breath of the Wild-style enemy awareness: ? when suspicious, ! when they spot you. Can sneak past enemies.

### Implemented

- **Awareness System**: FULLY IMPLEMENTED -- `game/systems/stealth.py` with 5 states (IDLE, SUSPICIOUS, ALERT, HUNTING, LOST)
- **Vision cones**: IMPLEMENTED -- 200px range, 90-degree cone, line-of-sight checks with platform blocking
- **Sound detection**: IMPLEMENTED -- Ground pound alerts enemies within 300px
- **Visual indicators**: IMPLEMENTED -- Yellow ? for SUSPICIOUS, Red ! for ALERT/HUNTING, with fade-in animation
- **Perfect dodge interaction**: IMPLEMENTED -- Dodge near sanitizer bottle resets to IDLE

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **None significant** | -- | The stealth system closely matches the BotW-style design. One of the most faithfully implemented systems. |

---

## 12. Easter Eggs & Secrets

### Designed (PRD 00)

PRD mentions hidden puzzles and secret areas discoverable via split mechanic. Barrel shopkeeper. No detailed easter egg design in the PRDs.

### Implemented (EXTRA -- all Claude additions)

`game/systems/secrets.py` implements 8 easter eggs:
1. **Konami Code** -- Classic code on title screen
2. **Architect's Room** -- Ground pound secret tile on Floor 1
3. **Andrew's Gallery** -- Interact with purple torch on Floor 7
4. **Fourth-Wall Fracture** -- Triggers on exactly 4 deaths (screen glitch effect)
5. **Claude the Shopkeeper** -- Interact with barrel on Floor 3, 5 times for dialogue
6. **Jello Graveyard** -- 50 missed shots create permanent wall splats
7. **Idle Dance** -- 30 seconds idle triggers music notes
8. **Exhibition Day Mode** -- Golden border on March 15, 2026

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **All 8 secrets are EXTRA** | **NOTE** | None of these were in the kids' design. Claude added them all. They're fun additions but the kids should know about them and approve/modify. |
| **Exhibition Day date is wrong** | **HIGH** | `secrets.py` line 416 checks for `datetime.date(2026, 3, 15)`. But the exhibition is **March 27, 2026** per CLAUDE.md. The date needs to be fixed to March 27. |
| **Hidden puzzles (levers, pressure plates)** | **MEDIUM** | PRD 00 mentions "levers, pressure plates" as hidden puzzle elements. These do not exist in the code. No lever or pressure plate classes. |
| **Secret areas via split** | **MEDIUM** | PRD says splitting "changes camera angle, reveals hidden paths, secret shrines, and secrets." Split IS implemented, but there are no level-design secret areas that require splitting to discover. |

---

## 13. Checkpoints & Progression

### Designed (PRD 03, 04)

- Easy/Normal: Generous/Standard checkpoints
- Hard: No checkpoints, restart the floor
- Earthquake: No checkpoints, timed, crumbling platforms never respawn, enemies +25% damage

### Implemented

- **Difficulty Selection**: IMPLEMENTED -- 4 difficulties in `Difficulty` enum
- **Difficulty Settings**: IMPLEMENTED -- `DIFFICULTY_SETTINGS` dict with damage multiplier, checkpoint flag, crumble respawn, timed flag (`game/engine/settings.py` lines 299-324)
- **Crumbling platform behavior**: IMPLEMENTED -- Respawn check uses `difficulty` setting
- **Earthquake timer**: IMPLEMENTED -- HUD earthquake timer display

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Actual checkpoint system** | **MEDIUM** | `CHECKPOINT_REACHED` event exists in `GameEvent` enum, and difficulty settings include a `checkpoint` flag. But there's no visible checkpoint mechanic in the code -- no checkpoint objects in levels, no save/restore point logic. On death, behavior needs playtesting. |
| **Restart behavior per difficulty** | **MEDIUM** | PRD says Hard = restart the floor, Easy/Normal = checkpoint restart. The death screen exists but the actual restart logic needs verification. |
| **Earthquake Mode timer** | **MEDIUM** | The HUD can display an earthquake timer. Need to verify the timer is actually running and counting down during Earthquake Mode gameplay, and what happens when it reaches zero. |
| **Cannot go back to previous floors** | **IMPLEMENTED** | Transitions in level JSONs only go forward (target_floor is always higher). This matches "linear -- climb from Floor 1 to Floor 15." |

---

## 14. Difficulty System

### Designed (PRD 03)

| Difficulty | Checkpoints | Damage | Special |
|------------|------------|--------|---------|
| Easy | Generous | Normal | Learn at your pace |
| Normal | Standard | Normal | Intended experience |
| Hard | None | +25% | Restart floor |
| Earthquake | None | +25% | Timed, platforms never respawn |

### Implemented

- **4 Difficulties**: IMPLEMENTED
- **Damage multiplier**: IMPLEMENTED -- Hard/Earthquake use `HARD_DAMAGE_MULTIPLIER = 1.25`
- **Crumble respawn**: IMPLEMENTED -- Easy/Normal/Hard = True, Earthquake = False
- **Timed flag**: IMPLEMENTED in settings, PARTIAL in gameplay

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Easy vs Normal difference** | **LOW** | Both have identical settings in the code (same damage, checkpoints, respawn). PRD says Easy has "generous" checkpoints vs Normal "standard" but there's no distinction implemented. |
| **Earthquake Mode castle collapse effects** | **LOW** | PRD describes visual castle collapse. Code has the timer and non-respawning platforms but no screen-shake debris or visual collapse effects tied to the timer. |

---

## 15. Visual Effects (VFX)

### Designed (PRD 05, 08)

Screen shake, fire on head (sun exposure), red screen edges (sun), slow-mo (dodge), crumble particles, sanitizer splash, sand particles (floors 12-15), castle collapse debris (Earthquake), jelly wobble, bubble eye expressions.

### Implemented (`game/systems/vfx.py`)

- **Particle Pool**: IMPLEMENTED -- Fixed-size pool (300 particles), zero allocation during gameplay
- **Screen Shake**: IMPLEMENTED -- VFX manager with shake magnitude and decay
- **Screen Flash**: IMPLEMENTED -- Color flash overlay
- **Shockwave**: IMPLEMENTED -- Expanding ring effect
- **Hitstop**: Referenced in code
- **Darkness/Fog**: Referenced in module docstring

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Fire on head (sun exposure)** | **MEDIUM** | PRD describes fire starting on the jello's head in sunlight. SunZone applies damage but no fire visual exists. Also, no SunZones are placed in any level. |
| **Red screen edges (sun)** | **MEDIUM** | PRD says screen edges turn red and close in during sun exposure. Not implemented. |
| **Sand particles (floors 12-15)** | **LOW** | Not implemented. No sand visual effects. |
| **Crumble particles** | **PARTIAL** | Crumbling platforms shake and blink red but don't emit particles when breaking. |
| **Bubble eye expressions** | **LOW** | PRD describes bubble eyes forming ? and ! shapes. The jello cube's eyes are drawn as simple circles (when using sprite fallback), no expression system. |
| **Jello translucency** | **PARTIAL** | PRD 08 describes a 3-layer translucency effect (shadow core, main body, highlight). Code uses simpler rendering. |

---

## 16. Banana Slug (Hint Guide)

### Designed (PRD 01)

A banana slug crawls through the scene when the player is stuck, heading toward where they need to go. Completely optional. Part of the castle's world. Reacts to ground pounds.

### Implemented

- **BananaSlug**: FULLY IMPLEMENTED -- `game/systems/crafting.py` (lines 129-310)
- **Appears after 30 seconds of no progress** (`SLUG_APPEAR_DELAY = 30 * 60`)
- **Crawls toward next objective**
- **Fades in/out** with 30-frame transitions
- **Ground pound reaction**: Wiggles when pounded within 60px
- **Disappears when player moves toward it**
- **Visual**: Warm brown oval with antennae, crawl animation

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **None significant** | -- | The Banana Slug is faithfully implemented. Great match to the design. |

---

## 17. Sprite Art & Assets

### Designed (PRD 05)

Andrew's hand-drawn illustrations with subtle pixel texture. Dead Cells cutscene quality.

### Available Assets (`assets/images/`)

- **Player**: `jello-cube-front.png`, `jello-cube-three-quarter.png`
- **Enemies**: Sanitizer Warrior -- front, side, rear, equipment spread (4 files)
- **Items**: Jelly powder bag, hand sanitizer front/back, dropped items
- **Bosses**: Gracie happy/battle faces, Mama Sloth reference photo
- **Andrew's originals**: 7 original drawings (image0-6.png)

### Gaps

| Gap | Priority | Notes |
|-----|----------|-------|
| **Sprites not used in gameplay** | **HIGH** | The code has a sprite loading system (`game/engine/sprites.py`) that tries to load sprites, but falls back to programmatic drawing (colored rectangles/shapes) when sprites don't match expected filenames. Most entities render as colored shapes, not Andrew's art. |
| **Missing sprites needed** | **HIGH** | PRD 05 lists: Small Sanitizer Bottle, Jelly Archer, The Big Bottle, The Cleanser, The Last Guard, Banana Slug, elemental pills, cooking pot, shrine designs -- all still needed from Andrew. |
| **Sprite integration pipeline** | **MEDIUM** | The code supports sprites via `load_sprite()` but the actual sprite filenames expected vs available need to be checked and aligned. |

---

## Summary: Top Priorities for Session 4+ Playtest

### Must-Fix (HIGH Priority)

1. **Exhibition Day Mode date**: Change from March 15 to March 27 in `game/systems/secrets.py`
2. **Visual size shrinking**: The jello cube should visibly shrink as health drops -- this was a core design feature
3. **Jelly Shot cost model**: PRD says shots cost health/mass. Code uses separate ammo. Team should decide which they prefer.
4. **Sprite integration**: Andrew's art exists but isn't showing in-game. Most things render as colored shapes.

### Should-Fix (MEDIUM Priority)

5. **Sun Zones placed in levels**: The SunZone code works but no levels use it
6. **Shrine rewards**: Shrines are placeholders with no puzzles or pill rewards
7. **Pill combat effects**: Verify pills actually affect combat (fire = more damage, etc.)
8. **Checkpoint system**: Verify death/restart behavior matches difficulty design
9. **Sound quality**: Swap synthesized bleeps for real foley WAV files where possible
10. **Music quality**: Add royalty-free orchestral tracks to replace synthesized drones
11. **Hidden puzzles (levers, pressure plates)**: Designed but not implemented
12. **Perfect Dodge slow-mo**: Designed but not implemented
13. **Boss floor spawning**: Verify bosses spawn on correct floors
14. **Powder drops from enemies**: Verify enemies drop jello powder on death
15. **Shield/Armor items**: Designed in PRD 00 but not implemented

### Nice-to-Have (LOW Priority)

16. Multiple water types (Small/Normal/Big/Simmered)
17. Jello Costume/Disguise mechanic
18. Captain's Hat cosmetic reward
19. Earthquake Mode sinkhole ending
20. Environmental decoration (furniture, paintings, sand)
21. Laser hazards on parkour floors
22. Bubble eye expressions
23. Randomized room layouts
24. Volume controls in settings

### EXTRA Features (Not in Design, Added by Claude)

The team should review these additions and decide if they want to keep them:
- **Gracie boss** (Secret Floor 2)
- **Mama Sloth boss** (Secret Floor 4)
- **8 Easter Eggs** (Konami Code, Architect's Room, Andrew's Gallery, Fourth-Wall Fracture, Claude Shopkeeper, Jello Graveyard, Idle Dance, Exhibition Day Mode)
- **Interactive walkable credits corridor** with team pedestals
- **Attract mode** timer on title screen
- **Controller disconnect overlay**
- **Automated playtest harness**
