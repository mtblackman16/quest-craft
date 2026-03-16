# Session 4 — Automated Playtest Harness Bug Report

**Date:** March 15, 2026
**Run ID:** 20260315_174328
**Floors tested:** 1–15 (all)
**Duration per floor:** 20 seconds
**Total frames:** 16,890
**Screenshots captured:** 154
**Crashes:** 0

## How It Works

The kids spent 2+ hours doing manual QA — finding bugs, reporting them to Claude, watching fixes happen in real time. Then we showed them the automated playtest harness: an AI bot that plays the game by itself, captures screenshots every 2 seconds, logs game state, and detects when it gets stuck.

The kids watched the robot play all 15 floors on the big screen. No controller. No human. The game playing itself.

## State Log Summary

| Floor | Min HP | Max Enemies | FPS Drops (<45) | Stuck Frames | Notes |
|-------|--------|-------------|-----------------|--------------|-------|
| 1     | 15     | 2           | 0               | 0            | Working well |
| 2     | 10     | 4           | 0               | 0            | Working well |
| 3     | 10     | 5           | 1               | 1            | Working well |
| 4     | 10     | 6           | 2               | 0            | Boss floor |
| 5     | 10     | 6           | 1               | 0            | Stealth section |
| 6     | 5      | 10          | 3               | 0            | Boss floor |
| 7     | 10     | 6           | 0               | 1            | Working well |
| 8     | 5      | 6           | 1               | 0            | Boss floor |
| 9     | 30     | 2           | 3               | 1            | Fewer enemies |
| 10    | 100    | 1           | 2               | 0            | **Never took damage** |
| 11    | 100    | 0           | 0               | 0            | **No enemies, fell off screen** |
| 12    | 10     | 9           | 0               | 1            | Boss floor |
| 13    | 10     | 9           | 0               | 0            | Working well |
| 14    | 10     | 12          | 1               | 0            | Heavy combat |
| 15    | 100    | 1           | 1               | 0            | **Final boss not attacking** |

## Bugs Found

### HIGH PRIORITY

1. **Floor 4 — Boss sprite mirrored.** The Big Bottle's "Hand Sanitizer" / "Germ B Gone" text renders backwards/mirror-reversed. Very noticeable.

2. **Floor 11 — Player falls off bottom of screen.** No floor catch or death zone at the left edge of the level. Player goes off-screen with no respawn trigger. Also zero enemies spawned on this floor.

3. **Floors 10, 11, 15 — Player never takes damage.** Enemies aren't attacking or are absent entirely. Floor 15 is the final boss (The Last Guard) — not dealing any damage to the player.

### MEDIUM PRIORITY

4. **Floors 9-15 — Player turns olive/dark green** instead of bright jello green. The biome palette appears to be tinting the player sprite. Looks washed out compared to early floors.

5. **Boss floors (4, 6, 8, 12) — Harsh vertical blue line** across the screen as the arena boundary. Looks like a debug line, not a styled wall.

6. **Floors 12-13 — Damage numbers render green** instead of white for enemy-received damage. Minor color inconsistency in HUD.

### LOW PRIORITY / COSMETIC

7. **All floors — Torch decorations peek at top edge of screen.** Orange triangles and white brackets barely visible at the very top. Torches placed a few pixels too high.

8. **Floor 15 — Final boss visually plain.** "The Last Guard" is a large brown rectangle. Other bosses have more character.

## What This Proves

- The automated harness can find bugs humans miss (floor 11 death zone, bosses not attacking)
- The harness ran all 15 floors with zero crashes — the game is stable
- State logging caught damage/enemy anomalies that wouldn't be obvious from just watching
- Screenshots let Claude analyze visual bugs without anyone playing

## Files

- Screenshots: `playtest_logs/run_20260315_174328/floor_XX/`
- State log: `playtest_logs/run_20260315_174328/state_log.jsonl`
- Summary: `playtest_logs/run_20260315_174328/summary.json`
