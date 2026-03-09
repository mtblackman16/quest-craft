# Split — Secret Upgrade Master Plan

> **FOR MARK'S EYES ONLY.** This is the blueprint for upgrading Split from a spark demo into a polished, mind-blowing game — built entirely on the kids' design decisions, elevated beyond what they imagined was possible.

> **Core Principle:** *"The reaction should not be 'wow, the AI added cool stuff.' It should be 'wait — that's MY idea, but it's even better than I imagined.'"*

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Engine & Performance](#2-engine--performance)
3. [Visual Effects System](#3-visual-effects-system)
4. [Audio System](#4-audio-system)
5. [Game Design: Bosses & Enemies](#5-game-design-bosses--enemies)
6. [Family Characters](#6-family-characters)
7. [Mark's Role: The Keymaker + The Narrator](#7-marks-role-the-keymaker--the-narrator)
8. [Easter Eggs & Secrets](#8-easter-eggs--secrets)
9. [Interactive Credits](#9-interactive-credits)
10. [Exhibition Hardening](#10-exhibition-hardening)
11. [Implementation Phases](#11-implementation-phases)
12. [Asset Requirements](#12-asset-requirements)

---

## 1. Architecture Overview

### Current State: `spark.py` (1043 lines, monolithic)

The spark demo is a single file with everything inline — title screen, player, particles, platforms, background, HUD. It works but cannot scale to a real game.

### Target Architecture: Modular Game Engine

```
game/
├── main.py              # Entry point, state machine (title/gameplay/credits/attract)
├── engine/
│   ├── __init__.py
│   ├── camera.py        # Scrolling camera with look-ahead, shake, zoom
│   ├── settings.py      # Constants, quality levels, Pi 5 tuning
│   └── assets.py        # Asset loader (pre-scale, convert_alpha, cache)
├── entities/
│   ├── __init__.py
│   ├── player.py        # JelloCube class (from spark.py, upgraded)
│   ├── enemies.py       # Enemy base + RolyPoly, SprayBottle, SanitizerWarrior
│   ├── bosses.py        # Boss base + FireTalus, MamaSloth, Gracie, WarriorCaptain
│   └── npc.py           # BarrelShopkeeper (Claude), The Keymaker
├── world/
│   ├── __init__.py
│   ├── level.py         # Level loader, tile-based rooms
│   ├── platforms.py     # Platform types (stone, crumbling, moving)
│   └── interactables.py # CookingPot, Chest, Lever, PressurePlate, Door
├── systems/
│   ├── __init__.py
│   ├── vfx.py           # VFXManager, ParticlePool, lighting, shockwaves
│   ├── sound.py         # SFXManager, spatial audio, sound pools
│   ├── music.py         # AdaptiveMusicManager, mood states, crossfade
│   ├── combat.py        # Hit detection, damage, hit-stop, knockback
│   ├── crafting.py      # CookingPot recipes, jello powder + water
│   ├── stealth.py       # Enemy awareness (? and !), detection zones
│   ├── narrator.py      # Mark's narrator messages, trigger system
│   └── hud.py           # Health bar, score, split indicator, minimap
├── ui/
│   ├── __init__.py
│   ├── title_screen.py  # Animated title, attract mode, Konami code
│   ├── pause_menu.py    # Pause overlay
│   ├── death_screen.py  # Death animation, run counter, "try again"
│   └── credits.py       # Interactive walkable credits sequence
└── data/
    ├── levels/          # Level definitions (JSON or simple text maps)
    └── dialogue/        # NPC dialogue, narrator lines
```

### Key Engine Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Resolution | 1280x720 | 10ms headroom at 60fps, SDL2 hardware upscales to display |
| Rendering | `pygame.SCALED \| FULLSCREEN` | Already working, GPU-accelerated final blit |
| Sprites | `pygame.sprite.LayeredUpdates` | C-level draw, automatic z-ordering |
| Particles | Pre-allocated pool (300 slots) | Zero allocation during gameplay |
| Backgrounds | Pre-rendered to cached Surface | Saves 5-8ms/frame vs current approach |
| Art assets | Pre-scaled + `.convert_alpha()` at load | 3-10x faster blitting |
| Audio init | `44100Hz, 16-bit, stereo, buffer=512` | ~11ms latency, responsive feel |
| Channels | 32 total (0-7 music, 8-15 SFX, 16-31 ambient) | No channel starvation |

---

## 2. Engine & Performance

### Pi 5 Performance Budget (16.67ms per frame at 60fps)

| System | Budget | Notes |
|--------|--------|-------|
| Background blit | 1.0ms | Pre-rendered cache, single opaque blit |
| Lighting overlay | 1.2ms | Half-res darkness + light cutouts |
| Fog/parallax | 0.5ms | 3 pre-rendered scrolling layers |
| Entity updates | 1.5ms | Player + 15-20 enemies + projectiles |
| Entity draws | 2.0ms | Pre-scaled sprites, LayeredUpdates.draw() |
| Particles (300) | 1.5ms | Cached surfaces, batch draw |
| Combat/VFX | 1.0ms | Shockwaves, hit effects, flashes |
| HUD | 0.5ms | Cached text, jello health bar |
| Camera + shake | 0.2ms | Offset calculation |
| Sound triggers | 0.2ms | Channel play calls |
| Music management | 0.1ms | Volume interpolation |
| SDL2 flip | 1.5ms | Final blit to display |
| **Total** | **11.2ms** | |
| **Headroom** | **5.5ms** | Safety margin for exhibition |

### Performance Safety Systems

**ThermalManager:** Reads `/sys/class/thermal/thermal_zone0/temp`. If CPU > 75°C, auto-reduce particle count and fog layers. If > 80°C, drop to minimum quality. Pi 5 throttles at 85°C.

**QualityManager:** 4 tiers (ultra/high/medium/low). Monitors rolling average FPS. If < 55fps for 30 frames, step down one tier. If > 59fps for 120 frames, step up. Hysteresis prevents oscillation.

**PerformanceGovernor:** Hard cap on particle count (300), active enemy count (20), projectile count (30). Drop oldest particles first.

### Camera System

```
- Look-ahead: 50px in movement direction (more visible space ahead)
- Vertical bias: Camera sits slightly above center (see more above = matches "climbing castle" theme)
- Smooth follow: Lerp toward target position (0.08 per frame)
- Shake: Damped sine wave (multiply by 0.85 each frame)
- Impact zoom: 5% zoom for 6 frames on big hits, ease back
- Death zoom: Slow zoom out over 2 seconds revealing surroundings
- Bounds: Clamp to level edges (no seeing void)
```

---

## 3. Visual Effects System

### 34 Effects, 7 Categories

**Atmosphere (pre-rendered, cheap):**
- Castle darkness overlay with torch light cutouts (radial gradients)
- Torch flame flicker (8-frame pre-rendered animation, sine-wave brightness)
- Fog/mist scrolling layers (3 parallax layers)
- Water drips (state machine: form → fall → splash)
- Dust motes in light beams
- Glowing door for level transitions

**Jello Character (the star):**
- Sine-wave edge deformation (wobbly outline, 20-point polygon)
- Enhanced squash-stretch (jump anticipation, apex hang, landing impact)
- Split stretching with gooey string connections
- Items visible floating inside transparent body
- Torch tint (amber highlight on side facing nearest torch)
- Damage ripple (sine wave through body)
- Idle dance (after 30s no input)

**Combat (juice):**
- Hit-stop: 2-frame pause on impact (player + enemy freeze, particles continue)
- Screen shake: micro (1-2px, every shot), medium (3-5px, enemy kill), heavy (6-10px, ground pound/boss)
- Directional shake on taking damage (shake FROM the hit direction)
- Enemy hit flash (3-frame white strobe)
- Enemy death burst (15-20 particles in enemy's color palette)
- Sanitizer Warrior death → purple goo + equipment scatter
- Ground pound: expanding ring + dust + center flash
- Stealth ? (fade in, grow) and ! (slam in, red glow, screen shake)

**Projectiles:**
- Jello shot: gooey trail particles, green glow
- Wall splats: permanent green marks for the run (Jello Graveyard easter egg)
- Fireball: orange particle trail, grows as it approaches

**Transitions:**
- Fade (general room changes)
- Iris wipe (secret room reveals)
- Shatter (death screen)
- Floor ascension (gravity well pulls particles into door, white-out, floor number title)

**HUD:**
- Jello health bar (wobbles with sine waves, jiggles on hit)
- Collection popup (scale pop: 1.0→1.3→1.0 in 12 frames)
- Run counter (unobtrusive corner display)
- Damage numbers (float up, fade out)

**Wow Moments (scripted sequences):**
1. First ground pound kill — slow-mo, zoom, extra particles, title text
2. Boss death — 10-frame hit-stop, 50+ particles, equipment scatter, title slam
3. First split — slow-mo stretching, green flash, ghost trails
4. Secret room reveal — rumble, debris, iris wipe, unique blue lighting
5. Floor ascension — gravity well, white-out, floor number

---

## 4. Audio System

### Adaptive Music (12 Mood States)

| State | Mood | Trigger |
|-------|------|---------|
| TITLE_SCREEN | Mysterious, inviting | Main menu |
| EXPLORE_CALM | Curious, playful | No enemies nearby |
| EXPLORE_MYSTERIOUS | Wonder, discovery | New/unexplored areas |
| STEALTH | Tense, careful | Enemy nearby, undetected |
| COMBAT_NORMAL | Energetic, urgent | Fighting regular enemies |
| COMBAT_BOSS | Epic, escalating | Boss fight |
| DANGER_LOW_HEALTH | Heartbeat overlay | Health < 25% (layers on top) |
| VICTORY_LEVEL | Heroic, triumphant | Completed a floor |
| VICTORY_BOSS | Epic triumph | Defeated a boss |
| DEATH | Somber, brief | Player died |
| CREDITS | Warm, emotional | Credits sequence |
| SECRET_ROOM | Magical, ethereal | Hidden area found |

**Architecture:** 4-layer system (base pad, melody, rhythm, intensity) on dedicated `pygame.mixer.Channel` instances. Layers fade in/out independently for smooth transitions. `pygame.mixer.music` is NOT used (only supports one stream).

**Key decision:** Music does NOT restart on death. Borrowed from Celeste — prevents hearing the same opening bars hundreds of times in a roguelike.

**Sourcing:** Classical public domain (Grieg "Hall of the Mountain King" for boss, Saint-Saens "Aquarium" for secrets), Kevin MacLeod royalty-free, Musopen orchestral recordings.

### Sound Effects (69 SFX, 8-sound exhibition minimum)

**Phase 1 — Exhibition Minimum (8 sounds):**
1. Jello land/squish
2. Jello shot fire
3. Jello shot impact
4. Jump
5. Enemy hit
6. Enemy death
7. Item collect
8. Ground pound impact

**Implementation:** `SFXManager` with 8 dedicated channels (8-15), `SoundPool` for variant cycling (3-4 variants per sound to avoid repetition), spatial stereo panning based on source position.

**DIY Foley the kids could do:**
- Squeeze dish soap bottle = jello shot fire
- Drop real jello on plate = landing squish
- Pop bubble wrap = enemy hit
- Slap wet sponge = ground pound

---

## 5. Game Design: Bosses & Enemies

### Regular Enemies (from kids' design)

| Enemy | Behavior | Difficulty |
|-------|----------|------------|
| Roly-polys | Swarm bugs, patrol in groups of 3-5, chase on sight | Easy |
| Spray Bottles | Stationary, fire slow arcing shots, telegraphed | Medium |
| Sanitizer Warriors | Patrol, ? and ! detection, melee + spray attack | Hard |

### Boss Progression (castle floors, bottom to top)

| Floor | Boss | Difficulty | Notes |
|-------|------|------------|-------|
| Floor 2 | **Gracie** | Medium-Hard | Fast, chaotic, copies player moves |
| Floor 3 | **Fire Talus** | Hard | 3-phase fight (furnace → chase → bullet hell) |
| Floor 4 | **Mama Sloth (Linda)** | Very Hard | Slow but devastating, tanky, relentless |
| Floor 5 | **Sanitizer Warrior Captain** | Very Hard | Uses Andrew's art, hose weak point |
| Rooftop | **The Castle Itself** | Final Boss | Walls close in, stone hands, ground-pound descent |

---

## 6. Family Characters

### Mama Sloth (Linda — Ethan's Mom)

**Reference photo:** `assets/images/bosses/mama-sloth-reference.jpg` — Athletic, powerful, flexing pose with huge smile. Radiates strength and confidence.

**Character Design:**
- Visually recognizable as Linda — her face, athletic build, long brown hair, that flexing pose
- Styled to fit the game: wearing a battle apron over athletic gear, armed with cleaning supplies (spray bottles, mops, rubber gloves)
- She's the germ-hating queen of the castle. Jello is sticky, squishy, MESSY — everything she despises. She wants to sanitize you out of existence
- The "Sloth" name is ironic — she's anything but slow. The name is her taunt: she calls herself Mama Sloth because she thinks beating you will be so easy she can do it half-asleep
- Her arena is the Living Quarters (Floor 4) — spotlessly clean, gleaming tiles, everything organized. Your jello trail DISGUSTS her
- She's allied with the Sanitizer Warriors (they worship her as their leader — she's the source of all the cleaning product enemies)
- Entrance cinematic: She's casually doing bicep curls with a giant sanitizer bottle. Notices the jello cube. Puts down the bottle. Flexes (recreating the exact pose from the photo). Cracks her knuckles. "You tracked JELLO into MY castle?!"

**Moveset:**
| Attack | Description | Tells |
|--------|-------------|-------|
| **"Homework Time!"** | Slams a giant textbook on the ground — shockwave radiates outward that slows the player to 50% speed for 3 seconds (you're "stuck doing homework"). Floating math equations and spelling words orbit the player during the debuff | She pulls out an enormous textbook and raises it overhead |
| **"Clean Your Room!"** | Massive shockwave that pushes everything to room edges, dealing damage on wall impact. Leaves gleaming clean floor behind (slippery zone, reduced traction for jello cube) | She stomps foot, floor cracks radiate outward |
| **"Mom Look"** | Freezes the player in place for 2 seconds (the real "don't you dare" stare). Her eyes literally glow. Unblockable, unavoidable — you MUST break line of sight by hiding behind an object | Her eyes start glowing, she turns to face you |
| **"Sanitize!"** | Dual-wields giant spray bottles. Sprays a wide cone of cleaning mist that dissolves jello on contact (high damage). The mist lingers as a damage zone | She pulls out spray bottles and winds up |
| **"Snack Time"** | Throws protein shakes that heal her if they land (player must intercept/shoot them). Each one heals 10% HP | She reaches into her battle apron |
| **"Flex Zone"** | Power-up move — she flexes (the photo pose!) and gains a temporary damage shield. While flexing, she's immobile but invulnerable. She does this to taunt you | She strikes the flexing pose |

**3 Phases:**
1. (100-60%) "Let me show you how it's done" — Confident, almost lazy. "Homework Time!" and "Clean Your Room!" on rotation. Uses "Flex Zone" to taunt. Beatable pattern if you learn timing
2. (60-30%) "Okay, you're tougher than you look" — Adds "Mom Look" and "Sanitize!" spray. Gets faster. Room floor starts gleaming (she's cleaning as she fights — slippery zones accumulate)
3. (30-0%) "I'm not angry, I'm disappointed" — All attacks speed up, "Snack Time" self-healing creates urgency. She stops taunting. No more flex poses. Dead serious. The smile is gone. This phase is HARD because she heals and the floor is mostly slippery

**Why she's hard:** She's tanky (lots of HP), her attacks control space and movement, and she heals. But she's not the fastest — patient players who learn patterns can beat her.

**Defeat animation:** She sits down, sighs contentedly, and falls asleep. A tiny "zzz" floats up. She drops a rare item: "Mom's Home Cooking" — a permanent max HP upgrade.

### Gracie (Ethan's Sister)

**Reference photos:**
- `assets/images/bosses/gracie-battle-face.jpg` — The serious stare, furrowed brow. This IS her battle stance. Use for combat sprite and Phase 2
- `assets/images/bosses/gracie-happy-face.jpg` — Big smile, pure joy. Use for intro, taunts, and defeat animation

**Character Design:**
- Visually recognizable as Gracie — her face, brown hair with lighter tips, that fierce expression
- Styled to fit the game: wearing a sporty battle outfit (runner's gear + swim goggles pushed up on forehead — nods to her real athleticism)
- She's the FASTEST character in the game. Not the strongest, but you cannot catch her, and she WILL catch you
- She's Ethan's OLDER sister — fiesty, loves to fight, not scared of anything, and thinks this is FUN
- She's a voracious reader who uses big words she barely understands in battle taunts: "Your gelatinous form is INCONSEQUENTIAL!" / "I find your strategy absolutely PEDESTRIAN!" / "That was EGREGIOUSLY predictable!"
- She has a TEMPER — when you land a good hit, she gets mad. Red-faced. Her attacks get faster but sloppier. Exploitable if you can bait her rage
- Her arena is the Cellars (Floor 2) — has water features (flooded sections, water channels) because she's a swimmer. She moves FASTER in water, you move SLOWER
- Entrance cinematic: She's doing sprints back and forth across the room, training. Spots the jello cube. Skids to a stop. Gives the big smile (happy-face photo). Cracks her knuckles. Gets the serious stare (battle-face photo). "Finally, someone to race. Try to keep up."
- The expression switch from smile to battle-face should be its own frame — the contrast is the whole character

**Moveset:**
| Attack | Description | Tells |
|--------|-------------|-------|
| **"Copy Cat!"** | Mirrors the player's last 3 actions back at them (if you shot, she shoots; if you jumped, she jumps into you). She does it FASTER than you did | She giggles and sparkles appear around her |
| **"Tag, You're It!"** | Sprints at the player at insane speed. If she touches you, controls reverse for 2 seconds. She's SO fast this is hard to dodge — use split to shrink and duck under | She points, gets low in a sprinter's stance |
| **"Cannonball!"** | Leaps into a water section and creates a massive splash wave that travels across the floor. The wave carries debris | She jumps high (swimmer's dive pose) |
| **"Look What I Found!"** | Picks up random objects (barrels, loose stones) and throws them wildly. Her throws are fast but inaccurate — chaos everywhere | She bends down to pick something up |
| **"I'm Telling Mom!"** | Runs to one edge and screams, spawning 3-4 roly-polys. In Phase 2, this also buffs nearby enemies with speed boost | She runs to the wall and cups her hands |

**2 Phases:**
1. (100-50%) Playful — big smile on her face the whole time. "Copy Cat" and "Tag." She's having the time of her life. Uses water sections to her advantage (she's fast in water, you're not). Beatable if you stay on dry ground
2. (50-0%) The smile drops. Battle-face comes out. Dialogue shifts from playful to angry: "That was ABSOLUTELY UNACCEPTABLE!" / "You are INFURIATING!" She starts using hit-and-run combos. "I'm Telling Mom!" adds minion pressure. "Cannonball!" floods more arena. BUT — her temper is her weakness. Every time you land 3 hits in a row, she throws a tantrum (stomps feet, face goes red, 1.5 second vulnerability window). Smart players bait her rage and punish the tantrum openings

**Why she's hard (but not as hard as Linda):** She's the fastest thing in the game. "Copy Cat" turns your own attacks against you. The water mechanic gives her a terrain advantage. But she has less HP, her patterns are reactable if you're quick, and she doesn't heal like Linda does.

**Defeat animation:** The battle-face holds for a beat... then breaks into the huge smile. She laughs, gives the jello cube a high-five (her hand squishes into the jello — splat sound), does a victory lap around the room at full speed just because she can, then cartwheels out. She drops "Gracie's Goggles" — a cosmetic item that makes the jello cube's eyes look like swim goggles and grants +20% speed in water for the rest of the run.

---

## 7. Mark's Role: The Keymaker + The Narrator

### The Keymaker (Opening Moment)

The game begins. The jello cube sits in a dark jail cell. Silence. Then:

1. A shadow moves on the other side of the bars (2 seconds)
2. A hand slides a stone key under the cell door (key glows faintly)
3. The lock clicks. The door creaks open
4. The shadow turns and walks away into darkness — never to be seen again
5. The jello cube's eyes open. Gameplay begins

**The hand is never explained.** No name. No face. Just someone who opened the door.

**In the Architect's Room** (Easter Egg 1 — the hidden room with the kids' pedestals), there is a 5th element: not a pedestal with a name, but a stone key mounted on the wall. Touching it plays a quiet resonant tone and displays:

> *"Every adventure needs someone to open the first door."*

No name. The kids will know.

### The Narrator (Throughout the Game)

At key moments, text appears in a unique font — monospace, slightly transparent, positioned at the top of the screen like someone watching from outside the game. The text fades in, holds for 3 seconds, fades out. No sound effect (silence makes it feel different from everything else).

**Trigger Points and Lines:**

| Trigger | Line | Tone |
|---------|------|------|
| First death | *"That's okay. They always get back up."* | Warm, encouraging |
| First enemy kill | *"They figured it out faster than I expected."* | Proud |
| First secret found | *"I knew they'd find that one."* | Knowing |
| First split used | *"Now they're thinking like jello."* | Amused |
| First boss encounter | *"This is the part where it gets real."* | Anticipation |
| First boss defeated | *"They're ready for what comes next."* | Confidence |
| Mama Sloth defeated | *"She'll be fine. She's tougher than she looks."* | Knowing wink |
| Gracie defeated | *"She's already planning a rematch. She always does."* | Affection |
| Reaching final boss | *"I always knew they could do it."* | Deep pride |
| Finding Architect's Room | *"They found the room. Of course they did."* | Quiet satisfaction |
| Post-credits | *"This was always their game. I just opened the door."* | The final line |

**Design Rules:**
- Never identified. Never named. Third person ("they" not "you")
- Appears in a different visual style from all game text
- Cannot be paused or replayed — ephemeral, like a passing thought
- Maximum 12 appearances across the full game — scarcity makes each one powerful
- The kids will piece together that someone is watching. By the 3rd or 4th message, they'll start wondering WHO. By the Mama Sloth line, they'll know

---

## 8. Easter Eggs & Secrets

### Complete List (8 Secrets)

| # | Name | How to Find | What Happens |
|---|------|-------------|-------------|
| 1 | **The Architect's Room** | Ground-pound cracked tile in starting cell | Hidden room with 4 colored jello cubes named ETHAN, EINS, ANDREW, NATHAN + wall-mounted key |
| 2 | **Konami Jello** | Konami Code on title screen | Jello explodes, reforms, "Secrets: 1/?" counter appears |
| 3 | **Andrew's Gallery** | Follow purple-tinted torches | Corridor with Andrew's original artwork as framed paintings on castle walls |
| 4 | **Fourth-Wall Fracture** | Die exactly 4 times | Screen "glitches", reboots, golden jello powder appears in starting cell |
| 5 | **Claude the Shopkeeper** | Find hidden barrel, interact 5 times | Shopkeeper reveals "My name is Claude. Yes, THAT Claude." |
| 6 | **Jello Graveyard** | Automatic — miss shots | Missed jello shots leave permanent green splats on walls, stats at run end |
| 7 | **The Idle Dance** | Stand still 30 seconds | Jello cube dances, music notes float up, cooking pots bubble in rhythm |
| 8 | **Exhibition Day Mode** | Play on March 15, 2026 | Golden border, first enemy drops "Exhibited" trophy, appears inside jello body |

### Hint System — Visual Language

| Hint Type | What It Looks Like | What It Means |
|-----------|-------------------|---------------|
| Reactive vines | Vines grow FROM wall (horizontal), retract when player is near | Hidden passage behind this wall |
| Fast-flicker torch | Torch flickers faster than normal | Draft from hidden opening nearby |
| Green-flame torch | Rare torch with green fire | Major secret (matches jello color = "left here for YOU") |
| Extinguished torch | Empty bracket, no flame | Danger ahead / high enemy density |
| Jello wobble | Player wobbles more than usual | Near a hidden interactive element |
| Sound shift | Subtle low hum | Within 3 tiles of a hidden room |

---

## 9. Interactive Credits

### The Walkable Ending

After defeating the final boss, the castle crumbles. The jello cube lands in a peaceful torch-lit corridor. No enemies. Walk right.

**Section 1 — "Created By":**
Four stone pedestals, each with a colored jello cube and the creator's name:
```
ETHAN (9)         EINS (11)        ANDREW (11)       NATHAN (9)
Game Designer     Game Designer     Artist            Game Designer
```
Each is interactive — walk up, press interact, speech bubble shows a real quote from that kid captured during sessions.

**Section 2 — "Built With":**
```
Engineered with Claude AI
Runs on Raspberry Pi 5
Python + Pygame

LASD Illuminate Inquiry Exhibition
March 15, 2026
```

**Section 3 — "The Journey":**
Timeline on the wall:
```
Session 1: Dream — "What game are we making?"
Session 2: Design — "Every detail matters"
Session 3: Blueprint — "The technical plan"
Session 4: Build — "Claude builds, we direct"
Session 5: Polish — "Make it feel great"
```

**Section 4 — "Thank You":**
```
Special Thanks: Mark — Team Advisor

Thank you for playing Split.
```

Glowing exit door. Walk through → white light flood.

### Post-Credits Surprise

3-second white screen. Then: the desert OUTSIDE the castle. New color palette — warm oranges, blue sky, golden sand. The jello cube stands in sunlight for the first time.

Text appears: **"HARD MODE UNLOCKED"**

The jello cube turns to face the camera (breaking side-scroll convention for the first and only time). Eyes blink. ? indicator appears above its head. Behind it on the horizon: a second, LARGER castle rises from the sand.

Fade to black. Title screen now has: **"HARD MODE"** option.

Narrator's final line appears: *"This was always their game. I just opened the door."*

---

## 10. Exhibition Hardening

### Auto-Start & Recovery

| System | Implementation |
|--------|---------------|
| Boot to game | systemd service, auto-starts on Pi power-on |
| Crash recovery | `watchdog.sh` — detects crash, restarts game (max 5 per minute) |
| Attract mode | After 2 min no input → auto-demo sequence on title screen |
| Session isolation | All state is local to gameplay function, no leaks between players |
| Controller disconnect | On-screen "Reconnecting..." message, auto-reconnect, keyboard fallback |
| Thermal protection | Auto quality reduction at 75°C, minimum quality at 80°C |

### Day-Of Checklist (for the kids)

| Problem | Fix |
|---------|-----|
| Game won't start | Unplug Pi, wait 10 seconds, plug back in |
| Game crashed | It should auto-restart. If not, hold power button 5 seconds |
| Controller not working | Turn controller off (hold home 3s), turn on, press any button |
| No sound | Check HDMI cable. Check volume on monitor |
| Stuttering | Touch Pi case — if hot, point a fan at it |

### Pre-Exhibition Test Protocol

- [ ] 4-hour soak test (continuous play, monitor temp/memory/FPS)
- [ ] Controller disconnect/reconnect 10 times
- [ ] Play through every floor
- [ ] Trigger every boss fight
- [ ] Find at least 3 easter eggs
- [ ] Verify attract mode activates
- [ ] Verify crash recovery
- [ ] Test on actual exhibition display
- [ ] Verify audio on exhibition display speakers
- [ ] Full playthrough with Pro Controller (no keyboard)

---

## 11. Implementation Phases

### Phase 0: Branch & Engine Skeleton (Now — while kids design)

**Branch:** `feature/surprise-upgrade`

**Tasks:**
- [ ] Create module structure (game/engine/, entities/, systems/, etc.)
- [ ] Extract player from spark.py into entities/player.py
- [ ] Build camera system (camera.py)
- [ ] Build asset loader with pre-scaling + convert_alpha (assets.py)
- [ ] Build ParticlePool (pre-allocated, cached surfaces)
- [ ] Build VFXManager skeleton
- [ ] Cache background rendering (biggest perf win)
- [ ] Init mixer properly (44100Hz, buffer=512, 32 channels)
- [ ] Build game state machine (title → gameplay → death → credits)

### Phase 1: Core Upgrades (After Session 2 — tonight/tomorrow)

**Integrate kids' design decisions from today's sprint into:**
- [ ] Level system — multi-floor castle with scrolling camera
- [ ] Enemy AI framework — patrol, detect (?/!), attack patterns
- [ ] Andrew's art integrated — jello cube + sanitizer warriors as real sprites
- [ ] Crafting system — cooking pots with jello powder + water
- [ ] Basic sound effects (8-sound minimum)
- [ ] Simple music (2-channel crossfade with 4 tracks)
- [ ] Basic lighting (darkness + torch cutouts)

### Phase 2: Bosses & Combat Polish (Session 3-4 timeframe)

- [ ] Fire Talus boss (3-phase fight)
- [ ] Mama Sloth boss (photo → sprite, 3-phase fight)
- [ ] Gracie boss (photo → sprite, 2-phase fight)
- [ ] Sanitizer Warrior Captain (uses Andrew's art)
- [ ] Hit-stop, enhanced screen shake, directional shake
- [ ] Combat particles (enemy death bursts, purple goo, equipment scatter)
- [ ] Stealth ? and ! indicators
- [ ] Jello physics overhaul (wobble, squash-stretch, split stretching)

### Phase 3: Secrets & Personality (Session 4-5 timeframe)

- [ ] The Keymaker opening sequence
- [ ] Narrator system (12 trigger points)
- [ ] Architect's Room (4 kid pedestals + key)
- [ ] Andrew's Gallery (original art as paintings)
- [ ] Konami Code on title screen
- [ ] Fourth-Wall Fracture (4th death glitch)
- [ ] Claude the Shopkeeper
- [ ] Jello Graveyard (persistent wall splats)
- [ ] Idle dance animation
- [ ] Exhibition Day Mode (date-triggered)
- [ ] Hint system (reactive vines, torch tells, jello wobble)

### Phase 4: Music & Audio Polish (Session 4-5)

- [ ] Adaptive music manager (4-layer system)
- [ ] All 12 mood states with sourced tracks
- [ ] Musical stingers (item collect, secret found, boss entrance, death, level up)
- [ ] Full SFX implementation (69 sounds, phased)
- [ ] Spatial audio panning
- [ ] Music survives death (Celeste approach)

### Phase 5: Credits & Endgame (Session 5 — Polish)

- [ ] Interactive walkable credits
- [ ] Kid pedestals with real quotes
- [ ] Post-credits desert reveal
- [ ] Hard Mode unlock
- [ ] Narrator final line
- [ ] Final boss: The Castle Itself (if time allows)

### Phase 6: Exhibition Prep (Day before)

- [ ] Watchdog script
- [ ] Kiosk mode (systemd auto-start)
- [ ] Attract mode
- [ ] Thermal/quality manager
- [ ] 4-hour soak test
- [ ] Day-of troubleshooting guide printed
- [ ] Controller charged, spare batteries ready

---

## 12. Asset Requirements

### Photos Needed from Mark

| Asset | For | Status |
|-------|-----|--------|
| Linda photo | Mama Sloth boss sprite | Pending upload |
| Gracie photo | Gracie boss sprite | Pending upload |
| Mark photo/silhouette (optional) | Keymaker shadow + Narrator (if any visual) | Optional — shadow only works too |

### Art Assets (Andrew's — already processed)

| Asset | Use |
|-------|-----|
| jello-cube-front.png | Player sprite (front view, menus) |
| jello-cube-three-quarter.png | Player sprite (gameplay) |
| sanitizer-warrior-side-view.png | Enemy sprite (gameplay) |
| sanitizer-warrior-front-view.png | Boss entrance cinematic |
| sanitizer-warrior-equipment-spread.png | Boss death scatter |
| jelly-powder-bag.png | Collectible item |
| hand-sanitizer-front.png | Enemy drop item |
| dropped-items-in-puddle.png | Boss death aftermath |

### Sound Assets Needed

| Category | Count | Source |
|----------|-------|--------|
| SFX Phase 1 (minimum) | 8 | Freesound.org + Python synthesis |
| SFX Phase 2 | 8 more | Freesound.org |
| Music tracks | 4-6 | Musopen (classical), Kevin MacLeod |
| Stingers | 5 | Freesound.org + synthesis |
| Ambient loops | 3 | Freesound.org |

### Level Data

| Floor | Theme | Boss | Enemies |
|-------|-------|------|---------|
| 1 (Dungeon) | Jail cells, damp stone, dripping water | None (tutorial) | Roly-polys only |
| 2 (Cellars) | Storage rooms, barrels, cooking pots | Gracie | Roly-polys + Spray Bottles |
| 3 (Great Hall) | Open chambers, high ceilings, torches | Fire Talus | All regular enemies |
| 4 (Living Quarters) | Bedrooms, corridors, cleaning supplies | Mama Sloth (Linda) | Heavy Sanitizer Warriors |
| 5 (Armory) | Weapons, armor, war room | Sanitizer Warrior Captain | Elite enemies |
| Rooftop | Open sky, crumbling battlements | The Castle Itself | Environmental hazards |

---

## When to Reveal

**Recommended reveal moment:** Opening of Session 4 (Build).

The kids expect Session 4 to be "Claude starts building from our blueprints." Instead, they sit down, Mark says "let's see where we are," launches the game, and... it's already real. Their jello cube — Andrew's actual art — is walking through a torch-lit dungeon, fighting enemies they designed, collecting items they invented. The music shifts as they explore. They find a secret room. The narrator speaks.

They will lose their minds.

---

*Last updated: 2026-03-08*
*Status: Planning complete. Awaiting photo assets for Linda and Gracie. Ready for Phase 0 execution.*
