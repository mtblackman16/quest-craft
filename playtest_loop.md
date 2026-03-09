# SPLIT — Autonomous Playtest Loop

Run this as a Claude Code prompt to have Claude continuously playtest, analyze, fix, and re-test the game.

## How to start

```bash
claude "$(cat playtest_loop.md)"
```

Or paste the prompt below directly into Claude Code.

---

## The Prompt

Run the automated playtest harness to exercise the game across all 15 floors:

```bash
cd ~/quest-craft
python3 -m game.testing.playtest_harness --floors 1-15 --duration 30
```

Read `playtest_logs/` for the latest run. Open `summary.json` first to check for crashes
and stuck states.

Then examine screenshots — focus on:
- `start.png` and `end.png` for each floor (did the floor load correctly?)
- Any `crash_*.png` or `stuck_*.png` files (what went wrong?)
- Periodic `frame_*.png` screenshots (visual glitches, overlapping sprites, HUD issues)

Read `state_log.jsonl` and look for:
- Floors where FPS dropped below 30
- Player health going negative or enemies_alive staying at 0 suspiciously early
- Floor transitions that didn't happen (player stuck on same floor)

Look for these specific issues:
- Visual glitches (overlapping sprites, rendering errors)
- Unreachable platforms or doors
- Stuck states (player trapped with no way out)
- Crashes or unhandled exceptions
- HUD elements drawn offscreen or overlapping
- Enemy spawning problems (too many, too few, wrong position)
- Boss floors loading correctly with boss health bar visible

Fix any issues you find in the game code. After each fix, commit with a clear message
describing what was wrong and how you fixed it.

Then run the test harness again. Compare the new run's summary to the previous one:
- Are crash counts lower?
- Are stuck states resolved?
- Do all 15 floors load without errors?

If all 15 floors complete without crashes and no stuck states are detected, output:
**PLAYTEST_COMPLETE**

Otherwise, continue the fix-test loop.
