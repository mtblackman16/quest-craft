# PRD 06b: Sound Effects — Complete SFX Catalog

| Field | Value |
|-------|-------|
| **Status** | Design Complete |
| **Author** | Claude (Sound Effects Expert) |
| **Date** | 2026-03-08 |
| **Reviewed by** | Pending team review |
| **Depends on** | [06-sound.md](06-sound.md) (music system), [00-game-concept.md](00-game-concept.md) |

---

## Companion to PRD 06

PRD 06 covers the **adaptive music system** -- mood states, layered architecture, crossfades, sourcing music tracks. This document covers the **sound effects** -- every individual foley sound, how it should feel, where to find it, and how to implement it in code.

The team decided: **"real foley sounds, royalty-free or classical music."** This means sound effects should feel physical and tactile, not 8-bit or synthetic.

### The Core Sound Identity

Split is a **jello game in a stone castle**. Every sound reinforces that contrast:
- **SOFT** (jello) vs **HARD** (stone) -- squishy organic sounds against cold echoing surfaces
- **WET** (jello body) vs **DRY** (castle dust, crackling torches)
- **LIGHT** (playful jello movement) vs **HEAVY** (dungeon atmosphere, enemy threats)

---

## 1. JELLO CHARACTER SOUNDS

The player IS jello. Every sound they make should remind you of that. These sounds should feel satisfying, slightly comical, and physically grounded.

### 1.1 Movement: Squishy Footsteps

**What it sounds like:** A small, wet suction-cup sound on each step -- like pressing a finger into firm gelatin and lifting it off a smooth plate. Quick rhythm, two alternating pitches (left-right). Subtle but present.

**Emotional feel:** Playful, bouncy, alive. The player should smile every time they run.

**Freesound search terms:** `gelatin squish`, `suction cup small`, `wet footstep`, `slime step`, `sticky footstep`

**Foley recording option:** Press a thumb firmly into a block of store-bought Jello on a ceramic plate, then lift. Record several at different pressures. Speed them up slightly in post.

**Technical notes:**
- Need 3-4 variations to avoid repetition (SoundPool pattern from 06-sound.md)
- Pitch-shift randomly between 0.9x and 1.1x on each play
- Trigger when `abs(vx) > 0` and `on_ground` is True
- Cadence: one sound every 8-10 frames while moving (about 6-8 steps per second)
- Volume: 0.15 (subtle background texture, never annoying)
- Channel: `CH_SFX + 0` (player movement, dedicated channel, interruptible by next step)

| Variant | File Name | Description |
|---------|-----------|-------------|
| Step 1 | `player/step_squish_01.ogg` | Quick light suction |
| Step 2 | `player/step_squish_02.ogg` | Slightly wetter, different pitch |
| Step 3 | `player/step_squish_03.ogg` | Quick with tiny release pop |
| Step 4 | `player/step_squish_04.ogg` | Softest variant for variety |

---

### 1.2 Jump: Stretchy Launch

**What it sounds like:** A rubbery stretch followed by a soft *bwoing* -- like pulling a thick rubber band and releasing it, combined with a wet membrane stretching. Short and punchy (0.2-0.3 seconds). Rising pitch suggests upward motion.

**Emotional feel:** Springy, energetic, satisfying. Should make jumping feel powerful.

**Freesound search terms:** `rubber stretch snap`, `gelatin bounce`, `spring boing wet`, `slime stretch`, `rubber band release`

**Foley recording option:** Stretch a water balloon without popping it, then let it snap back. Layer with a quick finger-flick on a taut cling-wrap membrane over a bowl.

**Technical notes:**
- Single sound, pitch-shifted up slightly for small jello (when split -- smaller body = higher pitch)
- Trigger on the frame `vy` is set to `jump_power` (the frame the jump starts)
- Volume: 0.35
- Channel: `CH_SFX + 1` (player action)
- File: `player/jump_launch.ogg`

---

### 1.3 Land: Splat/Squish with Weight

**What it sounds like:** A meaty, wet *splat* -- like dropping a handful of wet clay onto a countertop. Brief (0.15-0.25 seconds). Lower pitch suggests weight. The harder the fall, the louder and deeper.

**Emotional feel:** Weighty, grounded. Reassuring "I'm back on solid ground."

**Freesound search terms:** `wet splat`, `gelatin drop`, `slime impact`, `clay drop`, `wet thud soft`

**Foley recording option:** Drop a block of Jello from 6 inches onto a cutting board. Record at various heights for different intensities.

**Technical notes:**
- Two intensity levels based on the existing squish animation code:
  - **Soft land** (`player/land_soft.ogg`): when `vy > 4` on landing, volume 0.2
  - **Hard land** (`player/land_hard.ogg`): when `vy > 10` or from high platform, volume 0.4, lower pitch
- Trigger when `on_ground` transitions from False to True and previous `vy` exceeds threshold
- The existing code sets `self.squish = 0.4` for normal landings -- this is the sync point
- Channel: `CH_SFX + 1` (player action, same as jump -- you can never jump and land on the same frame)

---

### 1.4 Jello Shot: Wet Projectile Launch + Impact

**Launch sound:** A quick, pressurized *SPLURT* -- like squeezing a nearly-empty shampoo bottle, or a water gun firing. Wet, sharp, directional. Short (0.15 seconds).

**Impact sound:** A small wet *splat* -- like a paintball hitting a wall. Quick, high-pitched, with a tiny splatter tail.

**Emotional feel:** Satisfying "pew" but organic. Should reward shooting.

**Freesound search terms:**
- Launch: `water squirt`, `shampoo bottle squeeze`, `wet projectile`, `slime shoot`, `water gun fire`
- Impact: `paintball impact`, `small wet splat`, `slime hit wall`, `wet impact small`

**Foley recording:**
- Launch: Squeeze a nearly-empty dish soap bottle sharply
- Impact: Flick a spoonful of yogurt at a tile wall (this actually works perfectly)

**Technical notes:**
- Launch (`player/jello_shot_fire.ogg`): trigger in `shoot()` method, volume 0.4
- Impact (`player/jello_shot_hit.ogg`): trigger when projectile lifetime expires or collides, volume 0.25
- The recoil squish (`self.squish = -0.15`) is the visual sync point for launch sound
- Since shooting costs body mass, consider a subtle pitch increase as the player gets smaller (higher pitch = smaller, lighter body)
- Need 2 variants of the fire sound for rapid shooting without machine-gun repetition
- Channel: `CH_SFX + 1` (player action) for launch; any available channel for impact

| Sound | File | Volume |
|-------|------|--------|
| Shot fire 1 | `player/jello_shot_fire_01.ogg` | 0.4 |
| Shot fire 2 | `player/jello_shot_fire_02.ogg` | 0.4 |
| Shot impact | `player/jello_shot_hit.ogg` | 0.25 |

---

### 1.5 Ground Pound: Heavy Slam + Ripple

**Descent sound (optional):** A brief falling whoosh -- wind rushing downward. (0.3 seconds). Can be skipped for simplicity since the descent is very fast (`vy = 20`).

**Impact sound:** A deep, thunderous *THWUMP* combined with a wet reverberating splat. This is the biggest, most dramatic player sound in the game. Like dropping a watermelon from a table onto concrete. Deep bass thud + wet surface ripple. (0.4-0.5 seconds)

**Emotional feel:** POWERFUL. The screen shakes (`screen_shake = 8`), the sound should shake you too.

**Freesound search terms:**
- Impact: `heavy wet impact`, `watermelon drop`, `bass thud reverb`, `body slam mat`, `earthquake rumble short`

**Foley recording:** Drop a sealed ziplock bag of water onto a hard floor from waist height. Layer with a deep bass drum hit or a stomp on a wooden floor.

**Technical notes:**
- Impact (`player/ground_pound_impact.ogg`): trigger on `just_landed_pound`, volume 0.7 (loudest player sound)
- Must sync with the Shockwave visual effect and the `screen_shake = 8` in current code
- Play on a dedicated high-priority channel so it never gets cut off by other sounds
- Priority: CRITICAL (see priority system in 06-sound.md)
- Channel: `CH_SFX + 2` (player hurt/critical, reserved for high-priority player sounds)

---

### 1.6 Split: Tearing/Stretching Goo

**What it sounds like:** A viscous stretching and tearing -- like slowly pulling apart two surfaces stuck together with thick honey, then a wet *POP* as the pieces separate. Think stretching mozzarella cheese until it breaks. (0.4 seconds)

**Emotional feel:** Dramatic, slightly uncomfortable (you are tearing yourself apart), but cool.

**Freesound search terms:** `sticky stretch tear`, `slime pull apart`, `viscous liquid stretch`, `cheese stretch break`, `goo separate`, `tape peel slow`

**Foley recording:** Pull two surfaces apart that are stuck together with honey or thick syrup. Start slow, end with a snap.

**Technical notes:**
- `player/split_tear.ogg`: trigger on `split()` call, volume 0.5
- Sync with the 20-particle burst effect in the current code
- The `split_activate` musical stinger from 06-sound.md can play simultaneously for extra drama
- Channel: `CH_SFX + 1` (player action)

---

### 1.7 Merge Back Together: Slurping/Reforming

**What it sounds like:** The reverse of the split -- a slurping, sucking sound like a thick smoothie being pulled through a straw, ending with a satisfying wet *PLOP* as the pieces merge. (0.3 seconds)

**Emotional feel:** Satisfying, complete, "back to full strength."

**Freesound search terms:** `slurp thick liquid`, `smoothie straw`, `liquid merge`, `slime combine`, `suction reform`, `wet plop`

**Foley recording:** Suck a thick milkshake through a wide straw, ending with the straw lifting out of the liquid.

**Technical notes:**
- `player/merge_reform.ogg`: trigger on `unsplit()`, volume 0.45
- The `self.squish = 0.3` in unsplit() is the visual sync point
- Channel: `CH_SFX + 1` (player action)

---

### 1.8 Taking Damage: Wobble/Destabilize

**What it sounds like:** A quick, wobbly vibration -- like flicking a sheet of flexible metal (a saw blade wobble) but wet. Combined with a brief dissonant "ouch" tone. The jello wobbles violently when hit. (0.25 seconds)

**Emotional feel:** Alarming, jarring. "Something bad just happened."

**Freesound search terms:** `wobble plate`, `jello shake`, `spring doorstop boing`, `rubber vibrate`, `wet wobble`, `thunder sheet short`

**Foley recording:** Flick a flexible cutting board while it is resting on a wet surface. Or shake a bowl of Jello sharply and record the wobble.

**Technical notes:**
- `player/damage_wobble.ogg`: volume 0.5
- Play simultaneously with any damage flash/blink visual
- Brief invincibility frames (if implemented) should suppress re-triggering
- Channel: `CH_SFX + 2` (player hurt/critical -- high priority, never interrupted by normal sounds)

---

### 1.9 Death: Dramatic Splat/Dissolve

**What it sounds like:** A long, exaggerated *SPLAAAAT* -- like dropping an entire bucket of slime on the ground. Wet, messy, final. Followed by a brief sad dissolve (tiny bubbles popping, fizzing away). Total duration: 0.8-1.0 seconds.

**Emotional feel:** Dramatic, a little funny, but also "oh no." Since death means restart from the very beginning, this sound should carry weight.

**Freesound search terms:** `large splat`, `slime bucket drop`, `wet explosion soft`, `dissolve fizz`, `bubble pop cascade`, `liquid splash large`

**Foley recording:** Drop a full bowl of Jello onto the kitchen floor (put down a tarp first). Record the initial impact and the secondary settling sounds separately.

**Technical notes:**
- `player/death_splat.ogg`: volume 0.7, CRITICAL priority
- Should override all other player sounds
- Per 06-sound.md: the death musical stinger plays simultaneously, and background music does NOT restart
- Consider a brief (200ms) volume dip of the background music during the death splat
- Channel: `CH_SFX + 2` (player hurt/critical)

---

### 1.10 Collecting Items: Satisfying Absorption

**What it sounds like:** A soft, bubbly *SHLORP* -- like a thick liquid absorbing a small object. Think: dropping a marble into a bowl of thick pudding. Brief rising pitch at the end for satisfaction. (0.2 seconds)

**Emotional feel:** Rewarding, almost addictive. The "I want to collect more" sound.

**Freesound search terms:** `liquid absorb`, `bubble pop ascending`, `item pickup wet`, `water drop plop`, `slime absorb object`

**Foley recording:** Drop small objects (marbles, coins) into a bowl of thick pudding or yogurt. The initial "shlorp" is the sound you want.

**Technical notes:**
- Need 2 variants to avoid repetition when collecting several in sequence
- Trigger when `c.alive` goes False in the collectible check loop
- Pitch-shift slightly based on item color/type for variety
- Must sync with the `player.grow(3)` call and the 15-particle burst
- The `jello_powder_collect` stinger from 06-sound.md plays simultaneously for a combined effect
- Currently 7 collectibles in the Spark demo, so this will be heard frequently -- it MUST not be annoying
- Volume: 0.3
- Channel: any available (not critical priority)

| Sound | File | Volume |
|-------|------|--------|
| Collect 1 | `player/collect_absorb_01.ogg` | 0.3 |
| Collect 2 | `player/collect_absorb_02.ogg` | 0.3 |

---

### 1.11 Growing Bigger: Expanding/Inflating

**What it sounds like:** A low, pressurized inflation -- like slowly blowing up a latex glove, or air being pumped into a water bed. Soft, stretchy, with a satisfying "fullness" at the end. (0.4 seconds)

**Emotional feel:** Power-up. Getting stronger. Growing.

**Freesound search terms:** `inflate rubber`, `balloon inflate slow`, `air pump cushion`, `pressurize soft`, `expand stretch`

**Foley recording:** Slowly blow up a rubber glove or balloon, recording only the first 2 seconds of stretching (before it gets too thin-sounding).

**Technical notes:**
- `player/grow_inflate.ogg`: volume 0.3
- Trigger when crafting health at a cooking pot (jello powder + water = grow/heal)
- This is for significant growth events, NOT every small `grow(3)` call from collectibles
- Channel: `CH_SFX + 1` (player action)

---

### 1.12 Shrinking: Deflating

**What it sounds like:** The reverse of growing -- a quick, descending deflation. Like letting air out of a pool float, or a sad little balloon deflation. Brief and slightly comical. (0.2 seconds)

**Emotional feel:** "I'm getting weaker" but not punishing.

**Freesound search terms:** `deflate balloon`, `air release slow`, `tire deflate`, `shrink sound effect`, `descending pitch whoosh`

**Foley recording:** Let air out of a partially-inflated balloon slowly.

**Technical notes:**
- `player/shrink_deflate.ogg`: volume 0.25
- Trigger on shrink pill use
- Optional: play at very low volume (0.08) as a subconscious layer on every jello shot (since shooting costs mass)
- Channel: any available

---

## 2. ENEMY SOUNDS

### 2.1 Roly-Polys (Common Bugs)

These are small swarming bugs (pill bugs / woodlice). Their sounds should be insectoid, slightly creepy, but also a little cute since they are real bugs.

**Idle/ambient -- Chittering:** Soft chittering -- tiny legs clicking on stone. Like a handful of dry rice being slowly shaken in a paper cup. Very quiet, only audible when close.

**Movement -- Skittering:** Quick, dry scratching -- like a cockroach scurrying across paper. Fast tempo matches their small, rapid movement.

**Swarm buzzing (3+ together):** Layered chittering that builds into a low, unsettling hum. Not like bees -- more like a vibrating pile of dry leaves.

**Attack:** Sharp, quick click-snap -- like a stapler being fired. Brief and surprising.

**Death:** A crunchy *squish* -- like stepping on a dry leaf that was sitting on wet ground. Crunch + tiny wet pop. Satisfying to kill.

| Sound | File | Search Terms | Volume | Notes |
|-------|------|-------------|--------|-------|
| Chitter idle 1 | `enemies/rolypoly_chitter_01.ogg` | `insect chitter`, `beetle click`, `small bug sound` | 0.1 | 3 variants |
| Chitter idle 2 | `enemies/rolypoly_chitter_02.ogg` | | 0.1 | |
| Chitter idle 3 | `enemies/rolypoly_chitter_03.ogg` | | 0.1 | |
| Skitter move 1 | `enemies/rolypoly_skitter_01.ogg` | `cockroach scurry`, `insect legs scratching`, `bug running` | 0.15 | 3 variants |
| Skitter move 2 | `enemies/rolypoly_skitter_02.ogg` | | 0.15 | |
| Skitter move 3 | `enemies/rolypoly_skitter_03.ogg` | | 0.15 | |
| Swarm hum | `enemies/rolypoly_swarm.ogg` | `insect swarm low`, `bug cluster hum`, `cicada group quiet` | 0.2 | Loop, fades in when 3+ nearby |
| Attack snap | `enemies/rolypoly_attack.ogg` | `stapler snap`, `small click attack`, `beetle mandible` | 0.3 | |
| Death crunch | `enemies/rolypoly_death.ogg` | `bug crunch`, `leaf crush wet`, `shell crack small` | 0.35 | Satisfying! |

**Technical notes:**
- Chitter and skitter use SoundPool for random variant selection
- Swarm hum is a looping sound that fades in when 3+ roly-polys are within 200px of the player
- Pitch-shift each individual roly-poly's sounds by a random factor (0.85-1.15x) at spawn time so groups sound varied
- All roly-poly sounds use spatial panning (pan left/right based on enemy x-position relative to player)
- Channel: enemy channels from 06-sound.md (CH_SFX + 5/6/7 for nearest three enemies)

---

### 2.2 Alcohol Spray Bottles (Common Ranged Enemy)

These enemies fire slow but deadly shots. Their sounds should be mechanical/pressurized and clinical -- cleaning products turned hostile.

**Idle:** A subtle pressurized hiss -- like a bottle under pressure that occasionally vents. Periodic, not constant.

**Charge-up (before firing):** Building pressure hiss -- like a pressure cooker slowly building steam. This is a critical gameplay audio cue: it tells the player "DODGE NOW."

**Spray attack:** A sharp *PSSSHHT* -- the unmistakable sound of a spray bottle trigger being pulled. Quick burst of pressurized liquid. This is a real-world sound everyone recognizes instantly.

**Spray impact (on player):** A wet sizzle -- like water hitting a hot pan. The alcohol is damaging the jello.

**Death:** Pressurized release + liquid spill -- like a bottle cracking open and fizzing out. Deflating.

| Sound | File | Search Terms | Volume | Notes |
|-------|------|-------------|--------|-------|
| Idle hiss | `enemies/spray_idle.ogg` | `pressure valve hiss`, `bottle pressure release`, `gas leak quiet` | 0.1 | Loop, spatial |
| Charge up | `enemies/spray_charge.ogg` | `pressure build`, `air compressor start`, `steam building` | 0.25 | Gameplay cue! |
| Spray fire | `enemies/spray_fire.ogg` | `spray bottle trigger`, `aerosol spray`, `water mist spray` | 0.4 | |
| Spray impact | `enemies/spray_impact.ogg` | `water on hot pan sizzle`, `acid sizzle`, `liquid hiss surface` | 0.3 | |
| Death | `enemies/spray_death.ogg` | `bottle crack fizz`, `soda bottle open`, `pressure release deflate` | 0.35 | |

**Technical notes:**
- The charge-up sound is the most important sound for this enemy -- it is the player's only warning to dodge
- Charge-up should be clearly audible over ambient and music (volume 0.25 is pre-mix; it should be one of the louder enemy sounds)
- Spray fire should be spatially panned based on enemy position
- The spray bottle sound is so recognizable from daily life that it will immediately communicate "spray bottle" to players

**Foley shortcut:** Buy a dollar-store spray bottle. Record it. That IS the sound. No library needed.

---

### 2.3 Sanitizer Warriors (Heavy Enemies)

These are Andrew's designed characters: purple-skinned warriors with syringe weapons and backpack sanitizer bottles. They are larger, more humanoid, and more threatening. Their sounds should be deep, military, and chemical.

**Footsteps:** Heavy, armored boots on stone. Rhythmic, deliberate. Like a soldier marching. Each step has weight. Much slower cadence than the player's squishy steps.

**Battle cry (spotting player):** A distorted, guttural shout -- not a human voice, but something close. Like a voice processed through liquid. Aggressive but not scary (school-appropriate). Think: a grunt pitched down and run through reverb.

**Syringe attack:** A sharp pneumatic hiss + mechanical click -- like a staple gun or nail gun, but wetter. The syringe injecting.

**Backpack slosh:** When they move, the sanitizer bottles on their back slosh. Subtle liquid-in-container sound. A nice detail that makes them feel physically present.

**Death:** Heavy body fall + liquid spill + armor clatter. Dramatic. These are tough enemies so their death should feel earned.

| Sound | File | Search Terms | Volume | Notes |
|-------|------|-------------|--------|-------|
| Footstep | `enemies/warrior_step.ogg` | `heavy boot stone`, `armored footstep`, `soldier march echo` | 0.25 | Spatial, 2 variants |
| Battle cry | `enemies/warrior_cry.ogg` | `distorted shout`, `monster alert grunt`, `warrior battle cry low` | 0.5 | Triggers with ! alert |
| Syringe attack | `enemies/warrior_attack.ogg` | `pneumatic hiss click`, `nail gun fire`, `syringe inject` | 0.45 | |
| Backpack slosh | `enemies/warrior_slosh.ogg` | `water bottle slosh`, `liquid container shake`, `canteen slosh` | 0.1 | Subtle, spatial |
| Death | `enemies/warrior_death.ogg` | `armor body fall`, `heavy thud liquid spill`, `knight fall clatter` | 0.5 | |

**Technical notes:**
- Footstep cadence: one step every 20-24 frames (slower than player's 8-10 frame cadence)
- Battle cry should have reverb to fill the dungeon space
- The warrior_cry plays simultaneously with the alert_detected (!) stinger for maximum impact
- These are the hardest common enemies, so their sounds should be intimidating

---

### 2.4 Fire Talus (Mini-Boss)

Inspired by Zelda talus enemies. Fire Talus is a large enemy that shoots fireballs. Their sounds should be elemental -- fire, stone, and fury.

**Idle/ambient:** Low crackling fire + shifting stone. Like a campfire inside a rock tumbler. Constant, menacing presence when you are near.

**Roar:** A deep, resonant rumble -- like thunder mixed with a furnace igniting. This plays when the battle starts. Duration: 1.0-1.5 seconds.

**Fireball charge:** Rising pitch crackle -- fire being sucked inward, building energy. Like air being pulled toward a flame. (0.5 seconds). This is the gameplay cue to dodge.

**Fireball launch:** A deep *WHOOSH* + fire crackle -- like throwing a log onto a bonfire and the flame surging upward. (0.3 seconds)

**Fireball impact:** Explosion of embers -- crackling burst + sizzle. (0.4 seconds)

**Taking damage:** Cracking stone -- like a rock being struck with a hammer. Each hit cracks them further.

**Death:** Massive crumble + fire extinguish -- rocks falling apart + the hissing of fire being doused with water. Dramatic and final. (1.0 seconds)

| Sound | File | Search Terms | Volume | Notes |
|-------|------|-------------|--------|-------|
| Ambient crackle | `enemies/talus_ambient.ogg` | `campfire crackle`, `lava bubbling`, `fire loop low` | 0.2 | Loop, spatial |
| Roar | `enemies/talus_roar.ogg` | `thunder rumble`, `furnace ignite`, `dragon roar low` | 0.6 | Battle start |
| Fireball charge | `enemies/talus_charge.ogg` | `fire whoosh reverse`, `energy charge flame`, `fire suck inward` | 0.4 | Gameplay cue |
| Fireball launch | `enemies/talus_fireball.ogg` | `fireball whoosh`, `fire throw`, `flame burst large` | 0.5 | |
| Fireball hit | `enemies/talus_impact.ogg` | `fire explosion small`, `ember burst`, `flame impact crackle` | 0.45 | |
| Stone crack | `enemies/talus_hurt.ogg` | `rock crack hammer`, `stone break`, `boulder crack` | 0.4 | |
| Death crumble | `enemies/talus_death.ogg` | `rock crumble avalanche`, `fire extinguish hiss`, `stone collapse` | 0.6 | |

**Technical notes:**
- The ambient crackle loop should be spatial and distance-based (audible from ~350px away, getting louder as you approach)
- The roar triggers simultaneously with the `boss_entrance` stinger from 06-sound.md
- The fireball charge is the player's dodge window -- it must be clearly audible over combat music
- Boss death should be the most dramatic enemy death in the game

---

### 2.5 Enemy Awareness States (BotW-style ? and !)

These two sounds are critical to the stealth gameplay. They communicate enemy AI state directly to the player.

**Suspicion (? state):** A subtle, rising two-note tone -- like plucking a guitar string with a slight upward bend. Musical but tense. Think the Metal Gear Solid alert but much quieter and shorter.

**Detected (! state):** A sharp, dramatic sting -- a single loud staccato note, like a cymbal crash or orchestral hit, but very short (0.2 seconds). Unmistakable. Every player will learn to dread this sound.

| Sound | File | Search Terms | Volume | Priority |
|-------|------|-------------|--------|----------|
| Suspicion ? | `alerts/alert_suspicion.ogg` | `stealth suspicion tone`, `question alert subtle`, `rising two note` | 0.3 | IMPORTANT |
| Detected ! | `alerts/alert_detected.ogg` | `alert sting`, `orchestral hit staccato`, `detection alarm musical` | 0.6 | CRITICAL |

**Technical notes:**
- The ! sound is one of the most important sounds in the entire game -- it creates the BotW stealth tension
- ! should interrupt/override any other enemy sounds when it plays
- ? sound should pan to the direction of the suspicious enemy (spatial)
- ! sound should be centered (not panned) because it is a UI-level alert about YOUR danger
- Both can be synthesized in Python as a fallback (see code below)
- 06-sound.md includes the `enemy_alert` stinger; the ! SFX and the stinger may be the same sound or layered

**Python synthesis fallback (from 06-sound.md):**

```python
import numpy as np
import pygame

def make_alert_detected():
    """Generate the '!' detection alert sound."""
    sample_rate = 22050
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sign(np.sin(2 * np.pi * 880 * t))  # Square wave at 880 Hz
    envelope = np.exp(-t * 15)  # Fast decay
    wave = (wave * envelope * 0.5 * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)

def make_alert_suspicion():
    """Generate the '?' suspicion tone -- rising two-note."""
    sample_rate = 22050
    duration = 0.35
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freq = np.where(t < 0.15, 659, 784)  # E5 then G5
    wave = np.sin(2 * np.pi * freq * t)
    envelope = np.minimum(t * 20, 1.0) * np.exp(-(t - 0.1) * 4)
    envelope = np.clip(envelope, 0, 1)
    wave = (wave * envelope * 0.3 * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)
```

---

## 3. ENVIRONMENTAL SOUNDS

The castle dungeon is a character itself. Its sounds should make players feel enclosed, underground, and slightly uneasy even during peaceful exploration.

### 3.1 Castle Ambiance (Background Loop)

**What it sounds like:** A layered, continuous atmosphere built from:
1. **Dripping water** -- irregular drops echoing off stone. Not constant; every 3-8 seconds a drop echoes
2. **Distant echoes** -- faint, unidentifiable reverberations. Far-off doors, distant rumbles, the castle settling
3. **Wind through corridors** -- a low, almost sub-audible moan. Not howling, just air moving through stone passages
4. **Creaking** -- very occasional old-building settling sounds

**Emotional feel:** Atmospheric, slightly eerie, but not scary. You are underground in an ancient place.

**Freesound search terms:** `dungeon ambiance`, `cave dripping water echo`, `castle interior wind`, `underground atmosphere`, `stone corridor ambient`

| Sound | File | Volume | Type |
|-------|------|--------|------|
| Full ambiance | `environment/castle_ambiance.ogg` | 0.15 | Loop, always playing |
| Water drip overlay | `environment/water_drip.ogg` | 0.08 | Random trigger every 3-8 sec |
| Wind corridor | `environment/wind_corridor.ogg` | 0.06 | Loop, layered with ambiance |

**Technical notes:**
- Castle ambiance plays ALWAYS during gameplay on a dedicated channel
- Total ambiance volume (sum of all layers) should stay under 0.3 so it never competes with gameplay sounds
- Water drip triggers randomly every 180-480 frames (3-8 seconds at 60fps) with random left/right panning
- 3 water drip variants to avoid pattern recognition

---

### 3.2 Torches: Crackling Fire

**What it sounds like:** Gentle, warm fire crackling. A small torch, not a bonfire. Pops and hisses of a well-lit torch. Comforting in the dark dungeon.

**Freesound search terms:** `torch fire crackle loop`, `small campfire loop`, `candle flame crackle`

| Sound | File | Volume | Type |
|-------|------|--------|------|
| Torch loop | `environment/torch_crackle.ogg` | 0.08 max | Loop, spatial |

**Technical notes:**
- In current `spark.py`, torches are at x=150, 400, 650
- Load ONE sound file, play it on ONE channel with dynamic panning based on nearest torch to player
- Volume increases as player approaches (inverse distance, max audible range ~200px)

```python
def update_torch_sound(player_x, torch_positions, channel, base_volume=0.08):
    """Update torch crackle volume and pan based on nearest torch."""
    nearest_dist = float('inf')
    nearest_x = player_x  # default to centered
    for tx in torch_positions:
        dist = abs(tx - player_x)
        if dist < nearest_dist:
            nearest_dist = dist
            nearest_x = tx
    if nearest_dist > 200:
        channel.set_volume(0, 0)  # out of range
    else:
        vol = base_volume * (1.0 - nearest_dist / 200.0)
        # Pan
        relative = (nearest_x - player_x) / 640  # half screen width
        relative = max(-1.0, min(1.0, relative))
        left = vol if relative <= 0 else vol * (1.0 - relative * 0.8)
        right = vol if relative >= 0 else vol * (1.0 + relative * 0.8)
        channel.set_volume(left, right)
```

---

### 3.3 Doors: Heavy Stone Grinding

**What it sounds like:** A deep, slow grinding of stone on stone -- like a heavy slab being pushed across a rough floor. This plays for the glowing door that takes you to the next floor of the castle.

**Freesound search terms:** `stone door grinding`, `heavy slab sliding`, `rock scraping rock`, `dungeon door open stone`

| Sound | File | Volume | Duration |
|-------|------|--------|----------|
| Stone door | `environment/stone_door.ogg` | 0.5 | 1.5-2.0 seconds |

**Technical notes:**
- Plays once when the floor transition door activates
- Should have reverb/echo baked into the recording to fill the dungeon space
- Triggers before the ascending whoosh transition

---

### 3.4 Crafting Pot: Bubbling/Simmering

**What it sounds like:** A cheerful bubbling -- like a pot of thick soup simmering. Gloopy bubbles, occasional louder blorp. This is a positive, safe sound: the crafting pot is where you heal.

**Freesound search terms:** `pot bubbling thick`, `cauldron simmer`, `soup boiling loop`, `thick liquid bubbling`

| Sound | File | Volume | Type |
|-------|------|--------|------|
| Pot simmer | `environment/pot_simmer.ogg` | 0.15 | Loop, spatial |
| Craft success | `environment/pot_craft.ogg` | 0.4 | One-shot |

**Technical notes:**
- Simmer loop plays continuously when the player is near a crafting pot (distance-based spatial audio)
- Craft success plays when the player combines jello powder + water: a bubbly crescendo ending in a satisfying "ding"
- The `recipe_crafted` stinger from 06-sound.md layers on top for extra satisfaction
- Search terms for craft success: `potion brew complete`, `alchemy success`, `bubbling crescendo chime`

---

### 3.5 Chest Opening

**What it sounds like:** Two parts:
1. **Creak** -- old wooden lid lifting, hinges protesting. Like an old trunk being opened. (0.5 seconds)
2. **Reward sting** -- a brief, bright musical flourish. Three ascending notes, a tiny fanfare. (0.5 seconds)

**Freesound search terms:**
- Creak: `wooden chest open creak`, `old trunk lid`, `wooden box open`
- Sting: `treasure found fanfare`, `item get jingle`, `reward sting short`

| Sound | File | Volume |
|-------|------|--------|
| Chest creak | `environment/chest_open.ogg` | 0.4 |
| Reward sting | `environment/chest_reward.ogg` | 0.45 |

---

### 3.6 Hidden Room Reveal

**What it sounds like:** A magical, shimmering discovery moment -- like wind chimes struck by a gentle breeze, combined with a reverberant ethereal tone. Should feel like uncovering an ancient secret. (0.8 seconds)

**Freesound search terms:** `magical discovery`, `secret reveal shimmer`, `wind chimes ethereal`, `hidden area found`, `mystery discovery tone`

| Sound | File | Volume |
|-------|------|--------|
| Secret reveal | `environment/secret_reveal.ogg` | 0.5 |

**Technical notes:**
- The `secret_found` stinger from 06-sound.md handles the musical component; this SFX is the physical "reveal" sound (stone shifting, shimmer)
- Can be layered with a stone grinding sound for "wall opens to reveal room"

---

### 3.7 Floor Transition

**What it sounds like:** Two phases:
1. **Ascending whoosh** -- an upward sweep, like being pulled through a wind tunnel. Rising pitch. (0.8 seconds)
2. **Arrival** -- a deep, resonant arrival tone + the new floor's ambiance fading in. Like a large bell struck once, gently. (0.5 seconds)

**Freesound search terms:**
- Whoosh: `ascending whoosh magical`, `upward wind sweep`, `rise transition`
- Arrival: `deep bell single`, `arrival tone resonant`, `floor change transition`

| Sound | File | Volume |
|-------|------|--------|
| Floor ascend | `environment/floor_ascend.ogg` | 0.5 |
| Floor arrive | `environment/floor_arrive.ogg` | 0.4 |

---

### 3.8 Lever Pull / Pressure Plate

**Lever:** A mechanical *CLUNK* + chain rattle -- like a heavy switch being thrown. Satisfying, tactile. (0.3 seconds)

**Pressure plate:** A stone *click* as it depresses under weight, followed by a subtle grinding of whatever it activates. (0.4 seconds)

| Sound | File | Search Terms | Volume |
|-------|------|-------------|--------|
| Lever pull | `environment/lever_pull.ogg` | `lever mechanical clunk`, `heavy switch pull`, `chain mechanism` | 0.4 |
| Pressure plate | `environment/pressure_plate.ogg` | `stone button press`, `plate click grind`, `pressure switch stone` | 0.35 |

---

## 4. UI SOUNDS

UI sounds should be clean, crisp, and separate from the game world. They exist in the "interface layer" -- not the dungeon.

### 4.1 Menu Navigation

**What it sounds like:** Soft, clean clicks -- like gentle tapping on glass or ceramic. Not mechanical keyboard clicks, something smoother. Different pitch for moving vs selecting.

**Freesound search terms:** `menu click soft`, `UI navigation click`, `glass tap gentle`, `interface select`

| Sound | File | Volume | Notes |
|-------|------|--------|-------|
| Menu move | `ui/menu_move.ogg` | 0.2 | Subtle, frequent |
| Menu select | `ui/menu_select.ogg` | 0.35 | Slightly more satisfying |
| Menu back | `ui/menu_back.ogg` | 0.25 | Lower pitch than select |

**Recommended source:** Kenney.nl has complete CC0 UI sound packs that are already designed for games. These are the easiest to source and sound professional out of the box.

**Python synthesis fallback:**

```python
def make_ui_click(frequency=1200, duration=0.05, volume=0.4):
    """Generate a clean UI click sound."""
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * frequency * t)
    envelope = np.exp(-t * 80)
    wave = (wave * envelope * volume * 32767).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo)

# Menu move = higher, lighter click
menu_move_sound = make_ui_click(frequency=1200, duration=0.04, volume=0.3)
# Menu select = lower, more satisfying
menu_select_sound = make_ui_click(frequency=800, duration=0.07, volume=0.5)
# Menu back = even lower
menu_back_sound = make_ui_click(frequency=600, duration=0.06, volume=0.35)
```

---

### 4.2 Pause/Unpause

**What it sounds like:** A satisfying toggle -- like a light switch with resonance. Pause = slightly lower pitch (things stopping). Unpause = slightly higher pitch (things resuming).

**Freesound search terms:** `toggle switch click`, `pause sound effect`, `interface toggle clean`

| Sound | File | Volume |
|-------|------|--------|
| Pause | `ui/pause.ogg` | 0.3 |
| Unpause | `ui/unpause.ogg` | 0.3 |

---

### 4.3 Health Low Warning

**What it sounds like:** A slow, deep pulsing -- like a heartbeat heard from inside the body. Not alarming, but persistent. Pulses every 1.5 seconds when health (body mass) is below 30%.

**Freesound search terms:** `heartbeat slow deep`, `pulse warning low`, `health warning beat`

| Sound | File | Volume |
|-------|------|--------|
| Low health pulse | `ui/health_low.ogg` | 0.2 (loop) |

**Technical notes:**
- 06-sound.md handles this as the `DANGER_LOW_HEALTH` music overlay (heartbeat on top of current music)
- As an SFX alternative, this pulsing sound triggers when `mass_ratio < 0.4` (matches the EMBER color change in the HUD code)
- Fade in/out smoothly, do not hard-start
- Can be synthesized (see synthesis code in 06-sound.md)

---

### 4.4 Level Complete

**What it sounds like:** A triumphant, ascending fanfare -- bright, warm, celebratory. Three-to-five notes climbing upward, ending on a satisfying resolve. Think Zelda item-get fanfare but shorter and with a jello wobble at the end. (1.5 seconds)

**Freesound search terms:** `level complete fanfare`, `victory jingle short`, `achievement unlock`, `triumph fanfare ascending`

| Sound | File | Volume |
|-------|------|--------|
| Level complete | `ui/level_complete.ogg` | 0.6 |

**Technical notes:**
- This is the `level_complete` stinger from 06-sound.md, but listed here for the SFX catalog
- Plays on a high-priority channel that cannot be interrupted

---

### 4.5 Game Over

**What it sounds like:** Somber but not devastating. A descending phrase -- three notes going down, with reverb trailing off. Should motivate "I want to try again" not "I feel terrible." (1.5 seconds)

**Freesound search terms:** `game over somber short`, `failure descending notes`, `lose jingle gentle`

| Sound | File | Volume |
|-------|------|--------|
| Game over | `ui/game_over.ogg` | 0.5 |

---

### 4.6 Credits

**What it sounds like:** Gentle, warm ambient tones. Like soft wind chimes or a music box winding down. This plays under the credits scroll. Not a "song" -- an atmosphere of warmth and accomplishment. (Loop)

**Freesound search terms:** `credits ambient warm`, `music box gentle`, `wind chimes peaceful loop`, `end credits calm`

| Sound | File | Volume |
|-------|------|--------|
| Credits ambiance | `ui/credits_ambiance.ogg` | 0.25 (loop) |

---

## 5. SOURCING STRATEGY

### Recommended Sound Libraries (ranked by usefulness for this project)

| Rank | Source | URL | License | Best For |
|------|--------|-----|---------|----------|
| 1 | **Freesound.org** | freesound.org | CC0 / CC BY (per sound) | Foley, ambiance, impacts -- HUGE library |
| 2 | **Kenney.nl** | kenney.nl | CC0 (public domain) | UI sounds, simple effects -- game-ready |
| 3 | **OpenGameArt.org** | opengameart.org | Various (CC0, CC BY, GPL) | Game-specific SFX and music |
| 4 | **ZapSplat** | zapsplat.com | Free with attribution | Professional foley library |
| 5 | **Sonniss GDC Bundle** | sonniss.com | Royalty-free | Professional game audio (check annual free packs) |
| 6 | **Kevin MacLeod** | incompetech.com | CC BY 3.0 | Background music (covered in 06-sound.md) |

### Search Strategy by Sound Category

**For jello/wet sounds:** Start on Freesound.org. Search: `slime`, `gelatin`, `wet squish`, `goo`, `pudding`. Also try: `water balloon`, `suction cup`, `sticky`. Freesound has a strong foley community.

**For enemy/creature sounds:** Freesound + OpenGameArt. Search: `insect`, `creature`, `monster grunt`, `spray bottle`, `hiss`. OpenGameArt often has game-ready sound packs with multiple variants.

**For environment/ambiance:** Freesound excels here. Search: `dungeon`, `cave`, `torch`, `stone`, `medieval castle`. Many contributors upload long ambient recordings that can be looped.

**For UI sounds:** Kenney.nl is the best source. Complete CC0 UI sound packs (click, hover, confirm, cancel) designed for games.

---

### DIY Foley Recording Guide

The team said they want real foley sounds. Here is a practical setup.

**Equipment needed:**
- Any smartphone (iPhone or Android) -- the built-in microphone is fine
- A quiet room (turn off fans, AC, anything humming)
- Jello (buy a box of Jell-O brand, make it the night before the session)
- Various surfaces: ceramic plate, cutting board, tile
- Water, dish soap, rubber bands, balloons, plastic wrap, spray bottle

**Recording tips:**
1. Record in the quietest room available
2. Hold the phone 6-12 inches from the sound source
3. Record at the highest quality setting available
4. Record 5-10 takes of each sound -- pick the best one later
5. Leave 1 second of silence before and after each sound
6. Use Voice Memos (iPhone) or Sound Recorder (Android)
7. Export as WAV if possible, or high-quality M4A (can convert to OGG later)

**Foley Recipes for Every Key Sound:**

| Game Sound | Kitchen Foley Recipe |
|-----------|---------------------|
| Jello footstep | Press thumb firmly into Jello on a plate, lift. Repeat rapidly at different pressures. |
| Jump launch | Stretch a water balloon slowly, release. Or stretch a rubber glove. |
| Land (soft) | Drop a handful of Jello from 3 inches onto a plate. |
| Land (hard) | Drop Jello from 12 inches onto a hard surface. |
| Jello shot fire | Squeeze a nearly-empty dish soap bottle sharply. |
| Jello shot impact | Flick a spoonful of yogurt at a tile wall. |
| Ground pound | Drop a sealed ziplock bag of water onto the floor from waist height. |
| Split apart | Pull two Jello pieces slowly apart until they separate. |
| Merge together | Push two Jello pieces together firmly. Or suck thick liquid through a straw. |
| Damage wobble | Shake a bowl of Jello sharply on a table. |
| Death splat | Drop entire Jello block onto the floor from 2+ feet. |
| Collect item | Drop a marble into a bowl of thick yogurt or pudding. |
| Growing bigger | Slowly blow up a rubber glove (record the stretching). |
| Shrinking | Slowly let air out of a balloon. |
| Bug crunch death | Step on a dry cracker sitting on a wet paper towel. |
| Spray bottle | Use an actual spray bottle. That IS the sound. |
| Stone door | Scrape two rough rocks or bricks together slowly. |
| Chest open | Open any creaky cabinet door. |
| Torch crackle | Crumple a sheet of cellophane or aluminum foil near the mic. |
| Water drip | Drop water from a faucet into a metal pot (record single drips). |
| Lever pull | Click a heavy-duty light switch or stapler. |

**Exhibition story:** A foley recording session would make a great exhibition story. "We made our game sounds with real Jello!" is memorable and demonstrates the creative process.

---

### Programmatic Sound Synthesis

Some sounds can be generated in Python code using numpy + pygame.sndarray. This is useful for:
- Simple tones (alert ?, alert !, UI clicks)
- Procedural heartbeat
- Pitch-shifted variants of recorded sounds
- Placeholder sounds during development before real sounds are sourced

**Sounds best suited for synthesis vs. sourcing:**

| Generate in Python | Source from Libraries/Foley |
|-------------------|---------------------------|
| Alert ? tone | All jello character sounds |
| Alert ! sting | All enemy character sounds |
| UI menu clicks | Environmental ambiance |
| Low health heartbeat | Torch crackling |
| Simple whooshes | Music |

The synthesis code for these is provided above (section 2.5 and section 4.1) and in 06-sound.md.

---

### Audio Format Recommendations

| Type | Format | Sample Rate | Why |
|------|--------|-------------|-----|
| Short SFX (<1 sec) | WAV, 16-bit mono | 22050 Hz | Zero loading latency, tiny file size |
| Medium SFX (1-3 sec) | WAV, 16-bit mono | 22050 Hz | Still small enough for WAV |
| Long SFX (>3 sec) | OGG Vorbis, mono | 22050 Hz | Compression saves space |
| Ambiance loops | OGG Vorbis, stereo | 22050 Hz | Compression needed for long files |
| Music | OGG Vorbis, stereo | 44100 Hz | Best quality for music, per 06-sound.md |

**Expected file sizes:**

| Category | Files | Avg Size | Total |
|----------|-------|----------|-------|
| Player SFX | ~20 | 25 KB | 500 KB |
| Enemy SFX | ~25 | 30 KB | 750 KB |
| Environment SFX | ~12 | 70 KB | 840 KB |
| UI SFX | ~10 | 10 KB | 100 KB |
| Alert SFX | 2 | 15 KB | 30 KB |
| **Total SFX** | **~69** | -- | **~2.2 MB** |

Music is separate (covered in 06-sound.md, estimated 20-30 MB).

Total audio budget: approximately 25-32 MB. The Pi 5 has 4-8 GB of RAM. This is negligible.

---

## 6. IMPLEMENTATION

### Integration with 06-sound.md Architecture

The music system in 06-sound.md uses channels 0-7 for music. SFX should use channels 8-15:

```
Channels 0-7:   Music (per 06-sound.md)
Channel  8:     Castle ambiance loop
Channel  9:     Environmental spatial (torch crackle, pot simmer)
Channel  10:    Environmental one-shots (door, chest, water drip)
Channel  11:    Player movement (footsteps)
Channel  12:    Player action (jump, shoot, split, merge)
Channel  13:    Player hurt/critical (damage, death, ground pound)
Channel  14:    Enemy sounds (nearest enemy)
Channel  15:    Alert stings (? and !)
```

### SFX Manager Class

This works alongside the AdaptiveMusicManager from 06-sound.md:

```python
import os
import math
import random
import pygame

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class SoundPool:
    """A pool of sound variations to avoid repetitive playback."""

    def __init__(self, base_volume=1.0):
        self.sounds = []
        self.base_volume = base_volume
        self.index = 0

    def add(self, sound):
        self.sounds.append(sound)

    def play(self, channel=None, volume_scale=1.0):
        if not self.sounds:
            return
        sound = self.sounds[self.index]
        self.index = (self.index + 1) % len(self.sounds)
        vol = self.base_volume * volume_scale
        sound.set_volume(vol)
        if channel is not None:
            pygame.mixer.Channel(channel).play(sound)
        else:
            sound.play()


class SFXManager:
    """
    Manages all sound effects for Split.
    Works alongside AdaptiveMusicManager from 06-sound.md.

    Usage:
        sfx = SFXManager("assets/sfx")
        sfx.load_all()

        # In game loop:
        sfx.update_footsteps(player.vx, player.on_ground)
        sfx.update_spatial(player.x, torch_positions)

        # On events:
        sfx.play("jump")
        sfx.play_spatial("rolypoly_chitter", enemy_x, player_x, SCREEN_W)
    """

    # Channel assignments (8-15, leaving 0-7 for music)
    CH_AMBIANCE = 8
    CH_ENV_SPATIAL = 9
    CH_ENV_ONESHOT = 10
    CH_PLAYER_MOVE = 11
    CH_PLAYER_ACTION = 12
    CH_PLAYER_CRITICAL = 13
    CH_ENEMY = 14
    CH_ALERT = 15

    # Priority levels
    AMBIENT = 1
    NORMAL = 2
    IMPORTANT = 3
    CRITICAL = 4

    def __init__(self, sfx_dir="assets/sfx"):
        self.sfx_dir = sfx_dir
        self.sounds = {}          # name -> pygame.Sound
        self.pools = {}           # name -> SoundPool
        self.master_volume = 0.8
        self.sfx_volume = 0.85    # matches 06-sound.md default

        # Footstep timing
        self.step_timer = 0
        self.step_interval = 9    # frames between steps

        # Water drip timing
        self.drip_timer = 0
        self.drip_interval = random.randint(180, 480)  # 3-8 sec at 60fps

        # Channel priorities
        self.channel_priority = {}

    def _load_sound(self, name, relative_path):
        """Load a single sound file."""
        path = os.path.join(self.sfx_dir, relative_path)
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.Sound(path)
                return True
            except Exception as e:
                print(f"Warning: Could not load {path}: {e}")
        return False

    def _load_pool(self, pool_name, pattern, count, base_volume):
        """Load a pool of sound variants."""
        pool = SoundPool(base_volume)
        for i in range(1, count + 1):
            for ext in (".ogg", ".wav"):
                path = os.path.join(self.sfx_dir, f"{pattern}_{i:02d}{ext}")
                if os.path.exists(path):
                    try:
                        pool.add(pygame.Sound(path))
                    except Exception:
                        pass
                    break
        if pool.sounds:
            self.pools[pool_name] = pool

    def load_all(self):
        """Load all sound effects. Call once at startup."""

        # -- Player sounds --
        player_sounds = {
            "jump":           ("player/jump_launch",         0.35),
            "land_soft":      ("player/land_soft",           0.2),
            "land_hard":      ("player/land_hard",           0.4),
            "shoot_hit":      ("player/jello_shot_hit",      0.25),
            "pound_impact":   ("player/ground_pound_impact", 0.7),
            "split":          ("player/split_tear",          0.5),
            "merge":          ("player/merge_reform",        0.45),
            "damage":         ("player/damage_wobble",       0.5),
            "death":          ("player/death_splat",         0.7),
            "grow":           ("player/grow_inflate",        0.3),
            "shrink":         ("player/shrink_deflate",      0.25),
        }

        for name, (path, vol) in player_sounds.items():
            for ext in (".ogg", ".wav"):
                if self._load_sound(name, path + ext):
                    self.sounds[name].set_volume(vol)
                    break

        # Player sound pools
        self._load_pool("step", "player/step_squish", 4, 0.15)
        self._load_pool("shoot", "player/jello_shot_fire", 2, 0.4)
        self._load_pool("collect", "player/collect_absorb", 2, 0.3)

        # -- Enemy sounds --
        enemy_sounds = {
            "rolypoly_swarm":    ("enemies/rolypoly_swarm",     0.2),
            "rolypoly_attack":   ("enemies/rolypoly_attack",    0.3),
            "rolypoly_death":    ("enemies/rolypoly_death",     0.35),
            "spray_idle":        ("enemies/spray_idle",         0.1),
            "spray_charge":      ("enemies/spray_charge",       0.25),
            "spray_fire":        ("enemies/spray_fire",         0.4),
            "spray_impact":      ("enemies/spray_impact",       0.3),
            "spray_death":       ("enemies/spray_death",        0.35),
            "warrior_cry":       ("enemies/warrior_cry",        0.5),
            "warrior_attack":    ("enemies/warrior_attack",     0.45),
            "warrior_slosh":     ("enemies/warrior_slosh",      0.1),
            "warrior_death":     ("enemies/warrior_death",      0.5),
            "talus_roar":        ("enemies/talus_roar",         0.6),
            "talus_charge":      ("enemies/talus_charge",       0.4),
            "talus_fireball":    ("enemies/talus_fireball",     0.5),
            "talus_impact":      ("enemies/talus_impact",       0.45),
            "talus_hurt":        ("enemies/talus_hurt",         0.4),
            "talus_death":       ("enemies/talus_death",        0.6),
        }

        for name, (path, vol) in enemy_sounds.items():
            for ext in (".ogg", ".wav"):
                if self._load_sound(name, path + ext):
                    self.sounds[name].set_volume(vol)
                    break

        # Enemy sound pools
        self._load_pool("rolypoly_chitter", "enemies/rolypoly_chitter", 3, 0.1)
        self._load_pool("rolypoly_skitter", "enemies/rolypoly_skitter", 3, 0.15)
        self._load_pool("warrior_step", "enemies/warrior_step", 2, 0.25)

        # -- Environment sounds --
        env_sounds = {
            "ambiance":       ("environment/castle_ambiance", 0.15),
            "wind":           ("environment/wind_corridor",   0.06),
            "torch":          ("environment/torch_crackle",   0.08),
            "stone_door":     ("environment/stone_door",      0.5),
            "pot_simmer":     ("environment/pot_simmer",      0.15),
            "pot_craft":      ("environment/pot_craft",       0.4),
            "chest_open":     ("environment/chest_open",      0.4),
            "chest_reward":   ("environment/chest_reward",    0.45),
            "secret_reveal":  ("environment/secret_reveal",   0.5),
            "floor_ascend":   ("environment/floor_ascend",    0.5),
            "floor_arrive":   ("environment/floor_arrive",    0.4),
            "lever_pull":     ("environment/lever_pull",      0.4),
            "pressure_plate": ("environment/pressure_plate",  0.35),
        }

        for name, (path, vol) in env_sounds.items():
            for ext in (".ogg", ".wav"):
                if self._load_sound(name, path + ext):
                    self.sounds[name].set_volume(vol)
                    break

        self._load_pool("water_drip", "environment/water_drip", 3, 0.08)

        # -- UI sounds --
        ui_sounds = {
            "menu_move":      ("ui/menu_move",         0.2),
            "menu_select":    ("ui/menu_select",       0.35),
            "menu_back":      ("ui/menu_back",         0.25),
            "pause":          ("ui/pause",             0.3),
            "unpause":        ("ui/unpause",           0.3),
            "health_low":     ("ui/health_low",        0.2),
            "level_complete": ("ui/level_complete",    0.6),
            "game_over":      ("ui/game_over",         0.5),
        }

        for name, (path, vol) in ui_sounds.items():
            for ext in (".ogg", ".wav"):
                if self._load_sound(name, path + ext):
                    self.sounds[name].set_volume(vol)
                    break

        # -- Alert sounds --
        alert_sounds = {
            "alert_question":  ("alerts/alert_suspicion", 0.3),
            "alert_exclaim":   ("alerts/alert_detected",  0.6),
        }

        for name, (path, vol) in alert_sounds.items():
            for ext in (".ogg", ".wav"):
                if self._load_sound(name, path + ext):
                    self.sounds[name].set_volume(vol)
                    break

        # -- Generate synthetic fallbacks --
        if HAS_NUMPY:
            self._generate_synthetic_sounds()

    def _generate_synthetic_sounds(self):
        """Generate fallback sounds for alerts and UI using numpy."""
        sr = 22050

        # Alert "!" -- sharp square wave, fast decay
        dur = 0.2
        t = np.linspace(0, dur, int(sr * dur), False)
        wave = np.sign(np.sin(2 * np.pi * 880 * t))
        env = np.exp(-t * 15)
        w = (wave * env * 0.5 * 32767).astype(np.int16)
        if "alert_exclaim" not in self.sounds:
            self.sounds["alert_exclaim"] = pygame.sndarray.make_sound(
                np.column_stack((w, w))
            )

        # Alert "?" -- rising two notes
        dur = 0.35
        t = np.linspace(0, dur, int(sr * dur), False)
        freq = np.where(t < 0.15, 659, 784)
        wave = np.sin(2 * np.pi * freq * t)
        env = np.minimum(t * 20, 1.0) * np.exp(-(t - 0.1) * 4)
        env = np.clip(env, 0, 1)
        w = (wave * env * 0.3 * 32767).astype(np.int16)
        if "alert_question" not in self.sounds:
            self.sounds["alert_question"] = pygame.sndarray.make_sound(
                np.column_stack((w, w))
            )

        # UI click
        dur = 0.05
        t = np.linspace(0, dur, int(sr * dur), False)
        wave = np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 80) * 0.4
        w = (wave * 32767).astype(np.int16)
        for ui_name in ("menu_move", "menu_select", "menu_back"):
            if ui_name not in self.sounds:
                self.sounds[ui_name] = pygame.sndarray.make_sound(
                    np.column_stack((w, w))
                )

        # Heartbeat
        dur = 0.6
        t = np.linspace(0, dur, int(sr * dur), False)
        b1 = np.exp(-((t - 0.05)**2) / 0.001) * np.sin(2 * np.pi * 60 * t)
        b2 = np.exp(-((t - 0.18)**2) / 0.002) * np.sin(2 * np.pi * 50 * t)
        wave = (b1 + b2 * 0.7) * 0.4
        w = (wave * 32767).astype(np.int16)
        if "health_low" not in self.sounds:
            self.sounds["health_low"] = pygame.sndarray.make_sound(
                np.column_stack((w, w))
            )

    def play(self, name, channel=None, priority=None):
        """Play a sound effect."""
        sound = self.sounds.get(name)
        if not sound:
            return

        if priority is None:
            priority = self.NORMAL

        effective_vol = self.master_volume * self.sfx_volume
        # Sound already has its base volume set during load

        if channel is not None:
            ch = pygame.mixer.Channel(channel)
            current_pri = self.channel_priority.get(channel, 0)
            if not ch.get_busy() or priority >= current_pri:
                ch.play(sound)
                ch.set_volume(effective_vol)
                self.channel_priority[channel] = priority
        else:
            sound.play()

    def play_spatial(self, name, source_x, listener_x, screen_width,
                     channel=None, priority=None):
        """Play a sound with stereo panning."""
        sound = self.sounds.get(name)
        if not sound:
            return

        if priority is None:
            priority = self.NORMAL

        vol = self.master_volume * self.sfx_volume

        if channel is not None:
            ch = pygame.mixer.Channel(channel)
            current_pri = self.channel_priority.get(channel, 0)
            if ch.get_busy() and priority < current_pri:
                return
            ch.play(sound)
            self.channel_priority[channel] = priority
        else:
            ch = sound.play()
            if ch is None:
                return

        # Calculate stereo panning
        relative = (source_x - listener_x) / (screen_width / 2)
        relative = max(-1.0, min(1.0, relative))
        if relative < 0:
            left = vol
            right = vol * (1.0 + relative * 0.8)
        else:
            left = vol * (1.0 - relative * 0.8)
            right = vol

        ch.set_volume(left, right)

    def update_footsteps(self, player_vx, player_on_ground):
        """Call every frame. Handles footstep sound timing."""
        if abs(player_vx) > 0 and player_on_ground:
            self.step_timer += 1
            if self.step_timer >= self.step_interval:
                self.step_timer = 0
                if "step" in self.pools:
                    self.pools["step"].play(
                        channel=self.CH_PLAYER_MOVE,
                        volume_scale=self.master_volume * self.sfx_volume
                    )
        else:
            self.step_timer = 0

    def update_ambient(self):
        """Call every frame. Handles ambient drips and random environment sounds."""
        # Random water drip
        self.drip_timer += 1
        if self.drip_timer >= self.drip_interval:
            self.drip_timer = 0
            self.drip_interval = random.randint(180, 480)
            if "water_drip" in self.pools:
                self.pools["water_drip"].play(channel=self.CH_ENV_ONESHOT)

    def start_ambiance(self):
        """Start the castle ambiance loop. Call once when gameplay begins."""
        if "ambiance" in self.sounds:
            ch = pygame.mixer.Channel(self.CH_AMBIANCE)
            ch.play(self.sounds["ambiance"], loops=-1)
            ch.set_volume(self.master_volume * self.sfx_volume * 0.15)

    def stop_ambiance(self):
        """Stop ambiance. Call when leaving gameplay (menu, etc)."""
        pygame.mixer.Channel(self.CH_AMBIANCE).fadeout(500)

    def set_master_volume(self, vol):
        self.master_volume = max(0.0, min(1.0, vol))

    def set_sfx_volume(self, vol):
        self.sfx_volume = max(0.0, min(1.0, vol))
```

---

## 7. INTEGRATION WITH spark.py

Here is how the SFXManager hooks into the existing game code in `game/spark.py`.

### Key integration points in the current code:

| Code Location | Sound to Trigger |
|--------------|-----------------|
| `JelloCube.update()`: `self.vy = self.jump_power` | `sfx.play("jump", channel=sfx.CH_PLAYER_ACTION)` |
| `JelloCube.update()`: `self.squish = 0.4` (normal landing) | `sfx.play("land_soft", channel=sfx.CH_PLAYER_ACTION)` |
| `JelloCube.update()`: `self.squish = 0.6` (ground pound land) | `sfx.play("pound_impact", channel=sfx.CH_PLAYER_CRITICAL, priority=sfx.CRITICAL)` |
| `JelloCube.shoot()` | `sfx.pools["shoot"].play(channel=sfx.CH_PLAYER_ACTION)` |
| `JelloCube.split()` | `sfx.play("split", channel=sfx.CH_PLAYER_ACTION)` |
| `JelloCube.unsplit()` | `sfx.play("merge", channel=sfx.CH_PLAYER_ACTION)` |
| `gameplay()`: collectible check `c.alive = False` | `sfx.pools["collect"].play()` |
| `gameplay()`: `player.start_ground_pound()` | (sound on impact, not on start) |
| `gameplay()`: every frame | `sfx.update_footsteps(player.vx, player.on_ground)` |
| `gameplay()`: every frame | `sfx.update_ambient()` |
| `gameplay()`: on enter | `sfx.start_ambiance()` |
| `gameplay()`: on return to title | `sfx.stop_ambiance()` |

---

## 8. BUILD ORDER (Exhibition Priority)

### Phase 1 -- Exhibition Minimum (must have for March 15)

These 8 sounds make the game feel alive:

1. Player footsteps (4 step_squish variants)
2. Jump launch
3. Land (soft)
4. Jello shot fire (2 variants)
5. Ground pound impact
6. Collect item (2 variants)
7. Castle ambiance loop
8. Alert ! detected sting

**Source:** Freesound.org for foley sounds, synthesize the alert sting.

### Phase 2 -- Good to have

9. Land (hard)
10. Split tear
11. Merge reform
12. Roly-poly death crunch
13. Alert ? suspicion tone
14. Torch crackle loop
15. UI menu clicks (synthesize)
16. Level complete fanfare

### Phase 3 -- Polish

17. All remaining enemy sounds (spray bottle, warrior, fire talus)
18. Death splat
19. Damage wobble
20. Water drip variants
21. Chest open + reward sting
22. Stone door grinding
23. Crafting pot sounds
24. Pause/unpause
25. Health low heartbeat
26. Remaining environmental sounds
27. Grow/shrink sounds

---

## 9. COMPLETE FILE LIST

Total unique sound files needed: **69 files**

### Player (20 files)
```
player/step_squish_01.ogg
player/step_squish_02.ogg
player/step_squish_03.ogg
player/step_squish_04.ogg
player/jump_launch.ogg
player/land_soft.ogg
player/land_hard.ogg
player/jello_shot_fire_01.ogg
player/jello_shot_fire_02.ogg
player/jello_shot_hit.ogg
player/ground_pound_impact.ogg
player/split_tear.ogg
player/merge_reform.ogg
player/damage_wobble.ogg
player/death_splat.ogg
player/collect_absorb_01.ogg
player/collect_absorb_02.ogg
player/grow_inflate.ogg
player/shrink_deflate.ogg
player/dodge_liquid.ogg
```

### Enemies (27 files)
```
enemies/rolypoly_chitter_01.ogg
enemies/rolypoly_chitter_02.ogg
enemies/rolypoly_chitter_03.ogg
enemies/rolypoly_skitter_01.ogg
enemies/rolypoly_skitter_02.ogg
enemies/rolypoly_skitter_03.ogg
enemies/rolypoly_swarm.ogg
enemies/rolypoly_attack.ogg
enemies/rolypoly_death.ogg
enemies/spray_idle.ogg
enemies/spray_charge.ogg
enemies/spray_fire.ogg
enemies/spray_impact.ogg
enemies/spray_death.ogg
enemies/warrior_step_01.ogg
enemies/warrior_step_02.ogg
enemies/warrior_cry.ogg
enemies/warrior_attack.ogg
enemies/warrior_slosh.ogg
enemies/warrior_death.ogg
enemies/talus_ambient.ogg
enemies/talus_roar.ogg
enemies/talus_charge.ogg
enemies/talus_fireball.ogg
enemies/talus_impact.ogg
enemies/talus_hurt.ogg
enemies/talus_death.ogg
```

### Environment (15 files)
```
environment/castle_ambiance.ogg
environment/water_drip_01.ogg
environment/water_drip_02.ogg
environment/water_drip_03.ogg
environment/wind_corridor.ogg
environment/torch_crackle.ogg
environment/stone_door.ogg
environment/pot_simmer.ogg
environment/pot_craft.ogg
environment/chest_open.ogg
environment/chest_reward.ogg
environment/secret_reveal.ogg
environment/floor_ascend.ogg
environment/floor_arrive.ogg
environment/lever_pull.ogg
```

### UI (8 files)
```
ui/menu_move.ogg
ui/menu_select.ogg
ui/menu_back.ogg
ui/pause.ogg
ui/unpause.ogg
ui/health_low.ogg
ui/level_complete.ogg
ui/game_over.ogg
```

### Alerts (2 files)
```
alerts/alert_suspicion.ogg
alerts/alert_detected.ogg
```

---

## Open Questions

- [ ] Does the team want to do a foley recording session with real Jello? (Great exhibition story!)
- [ ] Should the jello cube make voice-like sounds? (Cute wobble-speak like Hollow Knight's characters?)
- [ ] How loud should the game be at the exhibition? (Noisy gymnasium = may need higher base volumes)
- [ ] Should spatial audio use only left/right panning, or also distance-based volume falloff?
- [ ] Priority: source sounds from libraries first, or do the foley session first?
