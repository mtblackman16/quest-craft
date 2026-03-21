# SPLIT -- Negative Test Inventory
## Consolidated from 3 Expert QA Audits (2026-03-20)
## Total: 500+ edge cases identified, prioritized below

---

## TIER 1: CRASH RISKS (fix before exhibition)

| # | System | Issue | File:Line | Status |
|---|--------|-------|-----------|--------|
| 1 | Combat | event_bus.emit() called without None check -- crash if event_bus is None | combat.py:120 | CRASH RISK |
| 2 | VFX | Particle cache never evicted -- ~60MB leak over 3hrs (6000 Surface objects) | vfx.py:101 | MEMORY LEAK |
| 3 | Levels | Floor 15 elevator target_floor=-1 -- may crash on floor load | floor_15.json:59 | CRASH RISK |
| 4 | Exhibition | exhibition.sh has no timeout for hung game process -- blocks forever | exhibition.sh:71 | HANG RISK |
| 5 | Player | Forced unsplit() with no collision check -- player phases through walls | player.py:379 | BUG |

## TIER 2: GAMEPLAY BUGS (fix if time allows)

| # | System | Issue | File:Line | Status |
|---|--------|-------|-----------|--------|
| 6 | Enemy | Arrow passes through platforms (no platform collision during flight) | enemies.py:276-284 | BUG |
| 7 | Enemy | Warrior hat polygon not reflected when facing left | enemies.py:294-295 | BUG |
| 8 | Enemy | Glob lands in air if boss/platform moves after trajectory calc | bosses.py:575 | BUG |
| 9 | Enemy | Health bar negative width if damage exceeds max_health | enemies.py:286 | BUG |
| 10 | Enemy | Stun timer not cleared on re-damage -- bottle locked in HIT state | enemies.py:157 | BUG |
| 11 | Boss | BigBottle sprite: verify fix actually prevents flip | bosses.py:633 | VERIFY |
| 12 | Boss | TheCleanser stun state could get stuck if timer logic off by 1 | bosses.py:530 | VERIFY |
| 13 | Boss | TheLastGuard phase transition during active grab -- grab orphaned | bosses.py:760 | VERIFY |
| 14 | Sound | Channel exhaustion during boss fights (8+ simultaneous SFX) | sound.py | BUG |
| 15 | Camera | Split pieces -- camera follows player.x not centroid of pieces | camera.py | BUG |

## TIER 3: VISUAL/AUDIO POLISH (nice to fix)

| # | System | Issue | File:Line | Status |
|---|--------|-------|-----------|--------|
| 16 | VFX | Particle pool (300) can exhaust during heavy combat -- silent drops | vfx.py:57 | BUG |
| 17 | VFX | Heavy particle load at boss entrance (175+ blits/frame) | vfx.py | PERF |
| 18 | Music | Same 3-sec loops repeat 3600+ times over 3hrs -- listener fatigue | music.py | DESIGN |
| 19 | Music | Crossfade not aligned to loop boundary -- potential silence gap | music.py | VERIFY |
| 20 | HUD | Health bar disappears at 0 HP (should show red sliver?) | hud.py | VERIFY |
| 21 | HUD | Pill timer jerky at 1 frame remaining (full->empty in 1 frame) | hud.py | BUG |
| 22 | Camera | Screen shake at level boundary can push view out of bounds | camera.py | BUG |
| 23 | Camera | Look-ahead at boundary pushes camera past clamp | camera.py | BUG |
| 24 | Sound | ALSA underruns increase over 2+ hours = audio pops/clicks | Pi hardware | VERIFY |
| 25 | Sound | Landing sound may repeat every frame if no flag prevents it | sound.py | VERIFY |
| 26 | Platform | Crumbling platform edge-case: 50/50 overlap may not trigger break | platforms.py | VERIFY |
| 27 | VFX | Alpha bucket mapping uneven (t=0.5 -> alpha 95 not 128) | vfx.py:330 | MINOR |

## TIER 4: EDGE CASES (monitor in harness, fix only if observed)

### Player Mechanics
- Split at 1 HP -- pieces may be invisible (6-12px at low health)
- Split timer expiry while wedged in narrow corridor
- Dodge into wall -- player teleports through?
- Ground pound from max height -- damage calculation overflow?
- Eat jello powder at 0 powder -- verify no negative count
- Shoot while split -- which piece fires?
- Die during split -- ghost pieces cleaned up?
- Die during dodge invuln -- death still triggers?
- Respawn momentum preserved from before death?
- Movement during hitstop frames -- should be frozen?

### Enemy Behavior
- Sanitizer trail accumulation (10 bottles x 30 frame interval = 200+ puddles)
- Multiple warriors firing simultaneously -- projectile memory
- Archer flee at x=0 boundary -- clamped or wraps?
- Enemy spawned inside platform -- falls through?
- Kill enemy same frame it fires projectile -- orphan projectile?
- Dead enemy contact damage during death animation
- Patrol path with <2 points -- vector calc division by zero?

### Boss Fights
- BigBottle charge into arena wall -- stuck?
- TheCleanser 5-phase puddle accumulation -- 100+ hazards?
- TheLastGuard Phase 1 chase speed (6.5) > player speed (5.0) -- escapable?
- TheLastGuard Phase 3 arrow rate (4/sec for 90 sec) -- 360 arrows?
- Gracie Copy Cat mirror -- player inputs reversed correctly?
- MamaSloth sleep wave -- hitbox coverage?
- Boss death during attack animation -- projectiles cleaned?
- Player dies during boss intro sequence

### Levels & World
- Transition zone accidental trigger (player walks over it)
- Missing transitions on any floor (trapped?)
- Spawn point inside wall
- Floor with 0 platforms (instant death loop)
- Cooking pot with no water/powder -- UI feedback?
- Chest already opened -- re-interact behavior
- Sun zone visual effect with player in it

### Performance (RPi5)
- FPS at 0/5/10/20 enemies on screen
- FPS with 100+ particles + 50+ projectiles
- Memory after 30/60/90/120/180 min
- Surface cache size growth over time
- GC pause causing frame drops
- Thermal throttling after 2+ hours
- CPU governor stays in performance mode?

### Exhibition Reliability
- Game crash -> restart timing (is 2 sec enough?)
- 50 consecutive crashes -> script stops (correct?)
- HDMI disconnect -> reconnect behavior
- Controller paired to wrong device
- Controller disconnect mid-boss fight
- Pause during boss intro
- Resume after 30+ min pause -- state intact?

---

## HARNESS VALIDATION TARGETS

The running harness (5 min/floor, 15 floors) should detect:
1. Any CRASH (harness catches these automatically)
2. FPS drops below 30 (logged in state_log.jsonl)
3. Player below screen anomaly (logged as anomaly flag)
4. Enemy count anomalies (0 enemies on combat floors)
5. Boss state (health, phase) on boss floors
6. Projectile/hazard accumulation over time
7. Health going to 0 -> death transition works

After harness completes, analyze state_log.jsonl for:
- Min FPS per floor
- Max concurrent enemies, projectiles, hazards
- Any anomaly flags triggered
- Boss encounter data (health depletion, phase changes)
- Player death count per floor
- Time spent below 50% HP

