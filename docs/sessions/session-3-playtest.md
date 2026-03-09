# Session 3: PLAYTEST — The Bug Hunt

**Goal:** Kids play the real game, find every bug, and watch Claude fix them in real time. This is the human+AI feedback loop in action.

**Time:** ~2-3 hours

**What you need:** Pi 5 connected to TV/monitor, Pro Controller charged, laptop with Claude Code open, Wispr Flow for voice input

**Who:** Full team — Ethan, Eins, Andrew, Nathan + Mark facilitating

---

## Before the Kids Arrive (Mark — 30 min)

Do all of this BEFORE the session starts. The kids should walk in to a game that's already running on screen.

### 1. Pull Latest Code

```bash
cd ~/quest-craft
git pull origin main
```

### 2. Set Display to 720p

The Pi defaults to 4K after reboot, which runs at 20fps. You must force 720p:

```bash
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/$(id -u)
wlr-randr --output HDMI-A-1 --mode 1280x720@60
```

Verify: the screen resolution should change visibly. If it doesn't, try `wlr-randr` alone to list available outputs/modes.

### 3. Pair the Pro Controller

If it's already paired from last session:
```bash
bluetoothctl connect 60:1A:C7:B7:72:9F
```

If not, press SYNC on the back of the controller, then:
```bash
bluetoothctl
> scan on
> pair 60:1A:C7:B7:72:9F
> connect 60:1A:C7:B7:72:9F
> trust 60:1A:C7:B7:72:9F
> quit
```

Or just plug in via USB-C — it works immediately.

### 4. Test Launch the Game

```bash
cd ~/quest-craft
export SDL_AUDIODRIVER=alsa
export AUDIODEV=plughw:0
python3 -m game.main
```

**What you should see:** Title screen with "SPLIT" text, animated jello cube, difficulty menu. If the controller is working, D-pad/stick should move the menu selection and A should confirm.

Play through Floor 1 quickly to verify:
- Player moves and jumps ✓
- Enemies appear ✓
- Jelly shot works (B button) ✓
- Music plays ✓
- No crash ✓

If anything is broken, fix it with Claude before the kids arrive.

### 5. Open Claude Code on Laptop

On your laptop (SSH'd into the Pi or running locally):
```bash
cd ~/quest-craft
claude
```

Have Claude ready and waiting. The kids will talk to Claude through Wispr Flow to report bugs. You'll help translate when needed.

### 6. Set Up the Room

- Pi connected to the biggest screen available (TV preferred over monitor)
- Controller on the couch/table where kids will sit
- Laptop nearby with Claude Code open
- Paper + markers for the Logger role (optional)
- Snacks if you've got them — this is a 2-3 hour session

---

## Session Flow

### Opening — "Your Game Is Real" (10 min)

**Mark says:**

> "Last time you designed every detail of this game — characters, levels, bosses, controls, everything. Between sessions, Claude built ALL of it. There are 15 floors, 5 bosses, sound, music, crafting — it's a real game. But here's the thing: first versions always have bugs. That's normal. Today YOUR job is to find every bug, tell Claude what's wrong, and watch it get fixed in real time. This is how real game studios work — you're the QA team."

**Key message:** They are not just playing. They are professional game testers. Their words directly change the code.

**Introduce the roles:**

| Role | What You Do |
|------|-------------|
| **Player** | Plays the game with the controller |
| **Bug Caller** | Watches the Player and calls out anything weird — "that didn't look right!" |
| **Feedback Lead** | Talks to Claude through Wispr Flow — describes the bug clearly |
| **Logger** | Writes down each bug on paper and checks it off when fixed (optional — give to the kid who likes writing) |

> "You'll rotate every 10-15 minutes so everyone gets to play, everyone gets to report bugs, and everyone gets to talk to Claude."

---

### Block 1: First Playthrough — No Interruptions (15-20 min)

**Who plays first:** Let the kids decide, or pick the kid who's been most patient. Eins or Ethan are natural first picks since they were most vocal during design.

**Mark says:**
> "First round — just play. Don't stop for bugs yet. We want to see the whole game flow. Everyone watch. After this, we'll start hunting."

**What to watch for (Mark's mental checklist):**
- Does the title screen work? Can they select a difficulty?
- Does the opening cinematic play? (It should show once on first run)
- Can they move on Floor 1? Jump? Shoot?
- Do they figure out the controls without help? If not, which controls confuse them?
- Do enemies appear? Do they fight back?
- Can they find the door to Floor 2?
- How far do they get before dying?
- What's their emotional reaction? Frustrated? Excited? Confused? Bored?

**DO NOT HELP with controls unless they're stuck for 30+ seconds.** Let them figure it out — this IS the playtest data.

**After the first run, ask:**
> "Okay — first impressions. What was cool? What felt weird? What didn't work?"

Write down everything they say. These are your bug priorities.

---

### Block 2: The Bug Fix Loop (90-120 min)

This is the core of the session. You'll run this loop over and over:

```
KID PLAYS (3-5 min)
    ↓
KID REPORTS BUG (out loud)
    ↓
FEEDBACK LEAD TELLS CLAUDE (via Wispr or typing)
    ↓
CLAUDE FIXES THE CODE
    ↓
MARK RESTARTS THE GAME
    ↓
KID VERIFIES THE FIX
    ↓
NEXT BUG (or rotate roles)
```

**Rotate roles every 10-15 minutes.** Use a timer on your phone. When it goes off:
> "Rotate! Player becomes Bug Caller, Bug Caller becomes Feedback Lead, Feedback Lead becomes Logger, Logger becomes Player."

#### How to Report Bugs to Claude

Teach the Feedback Lead to say things like:

**Good bug reports (specific):**
- "When I jump near the edge of a platform, I fall through it"
- "The ground pound doesn't seem to hurt enemies — I landed right on one and nothing happened"
- "I can't figure out how to get to Floor 2 — there's no door"
- "The B button shoots but it doesn't seem to do any damage"
- "The music stopped after I died"

**Bad bug reports (vague):**
- "It's broken" → Ask: "What's broken? What did you expect to happen?"
- "It doesn't work" → Ask: "What doesn't work? Show me."
- "It's too hard" → Ask: "What part is too hard? The enemies? The jumps? The controls?"

**Mark's role during this loop:**
1. Translate kid feedback into clearer bug reports if needed
2. Tell Claude which file to look at if you know (you can say "that's probably in player.py" or let Claude figure it out)
3. Restart the game after each fix: `python3 -m game.main`
4. Keep energy up — celebrate each fix: "Bug squashed! That's 7 down!"
5. Take photos of the kids testing

#### Known Issues the Kids Will Probably Find

Here's what to expect. Some of these are already fixed, some will surface:

**Controls:**
- A/B buttons might feel swapped to the kids — this is a known issue. If they say "jump and shoot are backwards," tell Claude to swap CTRL_A and CTRL_B
- D-pad might feel more natural than stick for some kids
- Ground pound (stick down or D-pad down while in air) might not be intuitive

**Gameplay feel:**
- Jump might feel too floaty or too heavy — Claude can adjust `PLAYER_JUMP_POWER` and `GRAVITY` in `game/engine/settings.py`
- Player might feel too fast or too slow — `PLAYER_SPEED` in settings
- Ground pound radius might be too small to feel satisfying — `GROUND_POUND_RADIUS` in `game/systems/combat.py`
- Enemies might be too hard or too easy — adjust HP values in `game/engine/settings.py`

**Collision / movement:**
- Getting stuck on edges of platforms — common platformer issue
- Falling through thin platforms
- Can't tell where to go / door to next floor is hard to find

**Visual:**
- Everything is colored rectangles, not Andrew's art — this is expected, will be addressed later
- Text might be too small on the TV
- Hard to tell enemies from platforms (both rectangles)

**Sound:**
- Music might not play (audio driver issue — verify `SDL_AUDIODRIVER=alsa`)
- Sounds might be too loud/quiet
- Some sounds might be missing

**Crashes:**
- If the game crashes, DON'T PANIC. Read the error message, paste it to Claude, fix, restart. The kids will think this is cool, not bad.

#### Tuning Session — This Is Where the Magic Happens

At some point, the bugs will be fixed and the session shifts from "fix broken things" to "make it feel better." This is game tuning, and it's where the kids have the most creative power.

**Things to tune:**
- "The jump should be higher" → `PLAYER_JUMP_POWER = -13` (more negative = higher)
- "Gravity feels too strong" → `GRAVITY = 0.6` (lower = floatier)
- "I want to move faster" → `PLAYER_SPEED = 5` (higher = faster)
- "Enemies are too easy" → increase enemy HP values
- "Enemies are too hard" → decrease enemy HP or damage values
- "Ground pound should hit more enemies" → increase `GROUND_POUND_RADIUS`
- "I want more health" → `PLAYER_MAX_HEALTH = 120`

Let the kids argue about these values. Different kids will want different things. Default to the team consensus. If they can't agree, go with Normal difficulty defaults and tell them "we have Easy mode for a reason."

---

### Block 3: Final Run + Showcase (20-30 min)

#### The Victory Lap (10 min)

> "Okay, let's do one clean playthrough with all the fixes. Everyone watch — is this fun? Is this ready to show people?"

Let the most confident player do the run. Everyone else watches. Play through as many floors as possible.

After the run:
> "How many bugs did we fix today? [Count them.] That's professional QA. Real game studios do exactly this."

#### Commit and Tag (5 min)

```bash
cd ~/quest-craft
git add -A
git commit -m "Session 3: Playtest fixes from team QA testing"
git tag v0.9-playtested
git push origin main --tags
```

> "Everything we fixed today is now saved forever. If anything goes wrong, we can always come back to this version."

#### Showcase — Learning Reflections (15 min)

Each kid answers these questions (use Wispr Flow, Mark types, or they write on paper):

**1. "What was the hardest bug you found today?"**

**2. "How did you describe it to Claude so it could fix it?"**

**3. "What surprised you about playtesting?"**

**4. "What's one thing you want to change before the exhibition?"**

Claude saves these to `docs/learning/learning-logs/session-3-playtest.md`

---

### Block 4: The AI Engineer (15-20 min)

> This block happens AFTER Block 3's showcase. The kids have just spent 2+ hours doing manual QA — finding bugs, reporting them, watching Claude fix them. Now you show them the next level.

#### The Big Reveal (5 min)

**Mark says:**

> "You just spent two hours finding bugs and telling Claude how to fix them. That's exactly how game studios work — humans play, humans report, engineers fix. But here's the thing: what if Claude could do the WHOLE thing by itself? Play the game, take screenshots, find bugs, fix them, test again — over and over, all night long while you sleep?"

Let that sink in. Then:

> "You know how you told Claude 'the jump feels too floaty' or 'I fell through the floor'? Claude can learn to spot those things in screenshots. And we already built a robot that plays the game — it walks right, jumps over gaps, shoots enemies, goes through doors. Not perfectly, but enough to find crashes and weird stuff."

#### Watch the Robot Play (3 min)

Run the test harness on the big screen so the kids can watch:

```bash
cd ~/quest-craft
python3 -m game.testing.playtest_harness --floors 1-3 --duration 15
```

The kids will see:
- The game playing itself (jello cube walking, jumping, shooting)
- No title screen, no death screen — it just keeps going
- Screenshots being captured in the terminal output

> "See that? Nobody's touching the controller. The game is playing itself. It jumps every second or so, shoots when enemies are nearby, walks through doors. It's not smart — it's just exercising the game enough to find problems."

#### See What It Captures (3 min)

Open the screenshot folder:

```bash
ls playtest_logs/run_*/floor_01/
```

Show them the screenshots on the laptop. Open a few:
- `start.png` — what the floor looks like when it loads
- A mid-run `frame_*.png` — the AI playing
- `end.png` — where it ended up

Open the state log:
```bash
tail -5 playtest_logs/run_*/state_log.jsonl
```

> "Every half-second, it records where the player is, how much health they have, how many enemies are alive, what floor they're on. If anything goes wrong, we can see exactly when and where."

#### Claude Analyzes a Screenshot (5 min)

This is the magic moment. Open Claude Code on the laptop and say:

> "Claude, look at the screenshots from the latest playtest run. Check floor 1's screenshots. Are there any visual issues — things overlapping, stuff drawn in the wrong place, anything weird?"

Claude will read the screenshots and analyze them. Even if it doesn't find issues, the kids see that Claude can LOOK at the game and understand what it sees.

If it does find something:
> "See? Claude found that bug just by looking at a screenshot. No human had to play. No human had to report it. The AI did the whole loop."

#### Set Up the Overnight Loop (2 min)

> "Now here's the really cool part. We can tell Claude to keep doing this — play, screenshot, analyze, fix, repeat — over and over. By the time you wake up tomorrow, it might have found and fixed bugs you never would have seen."

Show them the command:
```bash
cat playtest_loop.md
```

> "This is a set of instructions for Claude. It says: run the game, look at the screenshots, find bugs, fix them, run again. And keep going until everything works."

If you want to actually start it:
```bash
claude "$(cat playtest_loop.md)"
```

> "We'll let that run tonight. Tomorrow we'll check how many bugs it found and fixed while you were sleeping."

#### The Lesson (2 min)

**Mark says:**

> "Think about what just happened. You started today as game testers — YOU played, YOU found bugs, YOU told Claude what to fix. That's how it's been done for 40 years. But now you built something different. You built a system that tests ITSELF. The game plays itself, takes its own screenshots, finds its own bugs, and fixes its own code. That's not game testing anymore. That's AI engineering."

> "You didn't just test a game today. You learned how to build systems that improve themselves. That's the future of how software gets made. And you're 9, 10, and 11 years old. Remember this day."

---

## Mark's Cheat Sheet — Quick Fixes

If you need to fix something yourself without waiting for Claude:

| Problem | Quick Fix |
|---------|-----------|
| Game won't launch | Check error message. Usually a missing import or syntax error. |
| No sound | `export SDL_AUDIODRIVER=alsa && export AUDIODEV=plughw:0` before launching |
| 20fps (laggy) | `wlr-randr --output HDMI-A-1 --mode 1280x720@60` |
| Controller not detected | `bluetoothctl connect 60:1A:C7:B7:72:9F` or plug USB-C |
| Controller disconnects mid-game | Game will show "Reconnect Controller" overlay — just reconnect and it resumes |
| Game crashes | Read the traceback, tell Claude, restart with `python3 -m game.main` |
| Game stuck on title | Make sure controller A button works. Or press Space/Enter on keyboard. |
| Jump too floaty | Edit `game/engine/settings.py` → `GRAVITY` (increase = heavier) |
| Jump too weak | Edit `game/engine/settings.py` → `PLAYER_JUMP_POWER` (more negative = higher) |
| Want to restart from title | Quit with Ctrl+C or close window, re-launch |

---

## Energy Management

This is a long session. Kids WILL lose focus. Plan for it:

- **Hour 1:** High energy. First playthrough excitement. Rapid bug reporting.
- **90 min mark:** Take a 10-minute break. Let them run around, get snacks, wrestle, whatever.
- **Hour 2:** Tuning mode. This is where it gets creative and they re-engage.
- **If energy drops:** Switch to "who can find the weirdest bug?" competition. Or let someone try Earthquake Mode.
- **If a kid gets bored with their role:** Let them swap early. The rotation is a guideline, not a rule.
- **If one kid dominates:** Gently enforce rotation. "Your turn as Bug Caller now — what do you see?"

---

## What Success Looks Like

By the end of Session 3:

- [ ] Every kid has played at least 2 full rotations (played, reported, talked to Claude)
- [ ] At least 10 bugs have been found and fixed
- [ ] The game runs for 10+ minutes without crashing on the Pi with controller
- [ ] The title → play → die → restart loop works cleanly
- [ ] At least Floors 1-3 are playable and fun
- [ ] Controls feel good to the kids (not just "working" — actually good)
- [ ] Learning reflections captured from all 4 kids
- [ ] Code committed and tagged `v0.9-playtested`
- [ ] Test harness ran successfully on at least floors 1-3 (kids watched it)
- [ ] Kids understand the concept: human QA loop → automated AI loop
- [ ] Autonomous playtest loop started (runs overnight)
- [ ] A list of remaining issues exists for Mark to fix before exhibition

---

## After Session 3 — Mark Solo Work

Between Session 3 and the exhibition, Mark and Claude handle:

1. **Check overnight playtest results** — look at `playtest_logs/` for the latest run. Read `summary.json`, check for crashes, review screenshots for visual issues
2. **Fix remaining bugs** from the Session 3 bug list + anything the automated loop found
3. **Art integration** — get Andrew's sprites rendering if possible (replace colored rectangles)
4. **Print all exhibition materials** — 9 HTML files already generated in `docs/exhibition/`
5. **30-minute soak test** — game runs continuously without crash (or use the harness: `--floors 1-15 --duration 120`)
6. **Exhibition launch script** — `scripts/exhibition.sh` handles 720p + audio + auto-restart (already built)
7. **Capture screenshots** for display board

---

## Facilitation Notes (Mark Only)

### The Real Goal

Yes, we're fixing bugs. But the ACTUAL lesson is:

**"Your words change the code."**

Every kid should have at least one moment where they say something to Claude, the code changes, they re-launch the game, and their fix is RIGHT THERE. That's the magic moment. That's what we're exhibiting. Protect that moment — make sure every kid gets it, not just the loudest one.

### If Everything Is Broken

If the game has a ton of bugs and it's overwhelming:

1. Start with the MOST VISIBLE bug (usually controls or movement)
2. Fix it, celebrate
3. Move to the next most visible
4. Don't try to fix everything — fix what matters for the EXPERIENCE

A game that moves and jumps well on 3 floors is better than a game that has 15 floors of jank.

### If Everything Works Great

If there aren't many bugs (unlikely but possible):

1. Shift to tuning — "How should the jump feel? Higher? Faster?"
2. Try harder difficulties
3. Try to reach a boss
4. Have kids design one new thing live — a new enemy behavior, a new floor layout, a new sound
5. Challenge: "Can you beat Floor 5? Can you find the secret boss?"

### The Parent Photo Moment

Take photos of:
- A kid playing on the big screen (game visible behind them)
- A kid talking to Claude through Wispr (the AI collaboration shot)
- The whole team watching a playthrough
- The moment after a bug fix when they cheer
- A kid pointing at the screen saying "THAT'S the bug!"

These photos go on the exhibition display board and in the parent summary.
