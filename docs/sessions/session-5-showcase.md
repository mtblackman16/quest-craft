# Session 5: SHOWCASE — Display Board + Reflections + Demo Rehearsal

**Goal:** Assemble the physical display board, capture deep exhibition reflections, practice the exhibition demo. This is the LAST session before March 27.

**Time:** ~2 hours

**What you need:** Pi 5 connected to TV/monitor, Pro Controller, laptop with Claude Code, ALL printed exhibition materials, tri-fold display board, glue/tape, scissors, markers, kids' Build Record sheets from Session 4, blank Learning Story reflection sheets, camera/phone

**Who:** Full team — Ethan, Eins, Andrew, Nathan + Mark facilitating

---

## Before the Kids Arrive (Mark — 45 min)

### 1. Apply All Fixes

Between Session 4 and today, you should have already:
- Fixed all bugs from Session 4 bug list
- Fixed anything the overnight harness found
- Run a 30+ minute soak test (game stable)

Pull latest and verify:
```bash
cd ~/quest-craft
git pull origin main
export SDL_AUDIODRIVER=alsa
export AUDIODEV=plughw:0
python3 -m game.main
```

Quick playthrough of Floors 1-3 to confirm everything works.

### 2. Print All Exhibition Materials

You should have these already printed. Double-check the stack:

**Display board pages (print in color):**
- [ ] 01-title-card.html
- [ ] 02-inquiry-question.html
- [ ] 03-our-process.html
- [ ] 04-the-game.html (with real screenshot inserted)
- [ ] 05-the-team.html (with team photo inserted)
- [ ] 06-reflections.html (updated with Session 4 quotes)
- [ ] 07-how-to-play.html
- [ ] 08-the-world.html
- [ ] 10-learning-journey.html

**Photos (print 2-3 large):**
- [ ] Gameplay screenshots (captured between sessions)
- [ ] Team photos from Sessions 2 and 4
- [ ] Process photos from Session 4 (kids + Claude)

**Artwork:**
- [ ] Andrew's drawings (jello cube, sanitizer warrior, etc.) — print large

**Kids' work:**
- [ ] Build Record sheets from Session 4 (already filled in — bring them!)
- [ ] Blank Learning Story / reflection sheets (4 copies) — PMI, Bridge, or Freeze Frame format

### 3. Prepare the Space

- Tri-fold display board flat on a table (kids will assemble it)
- All printed materials organized in stacks
- Glue sticks, tape, scissors, markers laid out
- Pi + monitor set up for final testing
- Controller charged and paired
- Snacks for the team

---

## Session Flow

### Opening (5 min)

**Mark says:**

> "Last session you were game testers — you found bugs, told Claude how to fix them, and watched them get fixed in real time. Between sessions, Claude and I fixed everything on your list plus ran the robot overnight to catch more bugs. The game is solid. Today we do TWO things: finish the game polish AND build your exhibition display. March 27 is coming up — that's when you show this to the whole school."

---

### Block 1: Quick Bug Fixes + Final Polish (30 min)

**This is NOT a long bug-fix session.** The goal is a quick verification pass and any final tuning.

#### Quick Playthrough (15 min)

One full playthrough, each kid gets 3-4 minutes:
- Verify all Session 4 bugs are actually fixed
- Any new issues from overnight harness fixes?
- Final tuning if something still feels off

#### Final Fixes (15 min)

Fix any remaining critical issues. If it's just minor stuff, note it but move on. The display board is more important today.

> "The game doesn't have to be perfect — it has to be FUN and STABLE. If it runs for 3 hours without crashing and kids at the exhibition can figure out the controls, we're golden."

**Commit the final game state:**
```bash
git add -A
git commit -m "Session 5: Final polish before exhibition"
```

---

### Block 2: Build the Display Board (45 min)

**This is the main event.** Physical, hands-on, collaborative. Kids love this part — it's arts and crafts meets tech showcase.

**Mark says:**

> "Time to build your exhibition booth! This board tells visitors the story of your game AND how you made it. You're not just showing a game — you're showing what you LEARNED. That's what the exhibition is about."

#### Layout Guide

Show the kids the layout plan:

```
┌─────────────────────────────────────────────────────────┐
│  LEFT PANEL       │  CENTER PANEL      │  RIGHT PANEL   │
│                   │                    │                │
│  Our Process      │  SPLIT             │  What We       │
│                   │  (Title Card)      │  Learned       │
│                   │                    │  (Reflections) │
│  The Team +       │  Game Screenshot   │                │
│  team photo       │                    │  Our Learning  │
│                   │  How to Play       │  Journey       │
│  Our Question     │                    │                │
│                   │  Andrew's          │  Build Records │
│  Process photos   │  Artwork           │  (kids' sheets)│
│  from sessions    │                    │                │
└─────────────────────────────────────────────────────────┘
```

#### Assembly Steps

1. **Center panel first** — Title card goes at the top center. This is the first thing people see.
2. **Game screenshot** below the title — the one that shows actual gameplay
3. **How to Play card** below that — visitors need this
4. **Andrew's artwork** featured prominently — this is original kid art, judges love it
5. **Left panel** — Our Process + The Team + Inquiry Question + process photos
6. **Right panel** — Reflections + Learning Journey + Build Record sheets from Session 4
7. **Hand-lettered labels** — Let kids write section headers with markers if they want. Hand-written elements show it's genuinely kid-made.

#### Let the Kids Own It

- Let them decide exact placement
- Let them add hand-drawn decorations or labels
- If they want to rearrange, let them (within reason)
- Andrew should decide where his artwork goes
- Everyone should see their Build Record sheet and quotes on the board

**📸 PHOTOS: Capture the board-building process.** Kids gluing, arranging, debating layout — this IS the process.

---

### Block 3: Learning Story + Deep Reflections (30 min)

**Mark says:**

> "The exhibition isn't just 'look at our game.' It's about what you LEARNED making it. Each of you is going to tell your learning story — and these go right on the display board."

#### Choose a Reflection Format (2 min)

Each kid picks ONE format that feels right to them:

**Option A: PMI (Plus, Minus, Idea)** — Simple and works great for 9-year-olds
- **Plus:** What went well? What was the best part?
- **Minus:** What was hard? What didn't work at first?
- **Idea:** What would you do differently? What's your big takeaway?

**Option B: The Bridge** — Good for showing growth
- **First thoughts:** "Before we started, I thought game-making was..."
- **What changed my thinking:** "But then..."
- **Revised thinking:** "Now I think..."

**Option C: Freeze Frame** — Good for visual/creative thinkers
- Draw or describe 3 important moments as "photo frames":
  - Frame 1: The beginning (dreaming up the game)
  - Frame 2: The turning point (a breakthrough or challenge)
  - Frame 3: Today (what you know now)

#### Learning Story Questions (20 min)

After completing their chosen format, each kid answers these questions (via Wispr Flow, or writing on paper, or Mark types as they talk):

1. **What did you investigate and why?**
   - "We wanted to find out if kids could build a real video game with AI..."

2. **What did you discover?**
   - What did they learn about game design? About AI? About teamwork?

3. **What surprised you?**
   - Something they didn't expect about the process

4. **What challenged you?**
   - The hardest moment, the biggest frustration

5. **What decisions did you make along the way?**
   - Game design choices, what to include/cut, how to prioritize

6. **How has your thinking changed?**
   - What did they think before vs. now about games, AI, or creating things?

7. **What would you do differently if you could?**
   - Hindsight wisdom

8. **What are you still wondering about?**
   - Open questions, curiosity — this shows ongoing learning

**Claude saves all reflections to `docs/learning/learning-logs/session-5-showcase.md`**

> "There's no wrong answer. Just be honest about what you experienced. The people at the exhibition want to hear YOUR voice, not a perfect essay."

**📝 Print or write these on paper** — they go on the display board! If using Wispr/digital, Mark prints them before the exhibition.

---

### Block 4: Demo Rehearsal (15 min)

**Mark says:**

> "Okay — the board is built, the game works, your stories are written. Now let's practice. In 2 weeks, people are going to walk up to your booth and say 'What's this?' You need to be ready."

#### Assign Roles

| Role | Who (decide now) | What You Say |
|------|-------------------|--------------|
| **The Greeter** | _____ | "Hi! We built a game called SPLIT!" + the pitch |
| **The Builder** | _____ | "We designed it and an AI called Claude wrote the code" + points to process board |
| **The Demo Guide** | _____ | Hands controller to visitor, explains controls, helps them play |
| **The Learner** | _____ | Points to reflections and Build Records, explains what you learned |

**They rotate every 30 minutes during the actual exhibition.**

#### Practice Run (10 min)

Mark plays "visitor" — walks up to the booth cold:

> Mark: "Oh cool, what's this?"

Kids run through the demo script:
1. Greeting + game name
2. What the game is (genre, hook, what makes it special)
3. How they built it (designed by talking to AI)
4. Invite to play + controller instructions
5. While "visitor" plays: point out cool features, stand by to help
6. When they're done: "The thing we're most proud of is [X]. The biggest thing we learned is [Y]."

Practice answering these questions (judges/visitors WILL ask):
- **"How did you build this?"** → "We told an AI called Claude what we wanted — the characters, the levels, the controls — and it wrote the code. We're the game designers."
- **"What did you learn?"** → [Each kid has their own answer from the reflections]
- **"What was the hardest part?"** → "Describing bugs to Claude in a way it could understand. You have to be really specific."
- **"Did you write the code?"** → "No — we designed the game and Claude wrote the code from our designs. We told it what to build and then we tested everything."

#### Exhibition Logistics (3 min)

> "On March 27: arrive at 3:30, we set up the Pi and the board, sound check at 3:50. Exhibition runs 4:00 to 7:00. You'll rotate roles every 30 minutes. After 7:00, we pack up. Easy."

---

### Commit, Tag, Celebrate (10 min)

#### Code Freeze

```bash
cd ~/quest-craft
git add -A
git commit -m "Session 5: Exhibition prep complete - reflections, display ready"
git tag v1.0-exhibition
git push origin main --tags
```

> "v1.0. That's the version number for a finished product. Your game is officially version 1.0. No more changes unless something is truly broken."

#### 📸 FINAL TEAM PHOTO

Group photo with:
- The completed display board
- The game running on screen
- All four kids + the controller
- Big smiles

#### The Celebration

> "You started with an idea — a jello cube trapped in a castle. Over 5 sessions, you designed every detail, watched an AI build it from your words, tested it, fixed it, and now you're ready to show the world. You built a real game. 15 floors, 5 bosses, sound, music, everything. You're game designers. Remember that."

---

## What Success Looks Like

By the end of Session 5:

- [ ] Game runs stable — no critical bugs remaining
- [ ] Display board fully assembled with all materials mounted
- [ ] Each kid has a completed Learning Story reflection (printed or on paper)
- [ ] Each kid's Build Record sheets from Session 4 are on the board
- [ ] Andrew's artwork is featured prominently on the board
- [ ] Team and process photos are on the board
- [ ] All 4 kids have practiced the demo at least once
- [ ] Each kid knows their starting role for exhibition day
- [ ] Each kid can answer "How did you build this?" and "What did you learn?"
- [ ] Code committed and tagged `v1.0-exhibition`
- [ ] All reflections saved to `docs/learning/learning-logs/session-5-showcase.md`
- [ ] Mark has final photos of the completed setup
- [ ] EVERYONE IS PROUD OF WHAT THEY BUILT

---

## After Session 5 — Mark Final Prep (March 23-26)

1. **Last-minute fixes** if Session 5 revealed any issues
2. **Update 06-reflections.html** with Session 5 quotes
3. **Re-print any updated pages** if reflections were captured digitally
4. **Full dress rehearsal** at home: set up complete station, verify everything
5. **Soak test:** game runs 3+ hours without crash
6. **Charge all controllers** to 100%
7. **Back up SD card** (full disk image)
8. **Prepare backup SD card** (clone)
9. **Pack everything** (use exhibition-checklist.md)
10. **Confirm with other parents:** arrival time, who's bringing what

---

## Exhibition Day Quick Reference (March 27)

| Time | What |
|------|------|
| 3:00 PM | Load car: Pi, monitor, power strip, board, controllers, USB backup |
| 3:30 PM | Arrive at school, set up table |
| 3:35 PM | Pi + monitor + controller, boot game via `scripts/exhibition.sh` |
| 3:40 PM | Display board behind station |
| 3:50 PM | Sound check, controller check, full test run |
| 3:55 PM | Team huddle — assign first roles |
| 4:00 PM | Exhibition opens! Rotate every 30 min. |
| 7:00 PM | Exhibition ends |
| 7:30 PM | Pack up everything |

---

## Facilitation Notes (Mark Only)

### The Balance

Session 5 is half tech (game polish) and half arts & crafts (display board). Don't let the tech half eat the crafts half. The display board IS the exhibition deliverable — it's what judges evaluate. Set a hard time limit on bug fixes and move to the board.

### The Real Exhibition Goal

The exhibition wants to see evidence of learning, not just a finished product. The board should answer:
- **What did they investigate?** → "Can kids build a real game with AI?"
- **What did they learn?** → Reflections, quotes, Build Records
- **How did they learn it?** → Process photos, Build Records showing iteration, the learning journey page
- **Can they share it?** → The demo, the ability to answer questions

### If The Board Feels Overwhelming

Keep it simple:
1. Title card in the center
2. Game screenshot and How to Play below it
3. Process description on the left
4. Reflections on the right
5. Photos wherever they fit
6. Done. A clean, simple board beats a cluttered one.

### If Kids Don't Want to Write Reflections

Use Wispr Flow — let them TALK their reflections. Mark types or Claude transcribes. The kids just need to say the words; they don't need to write essays. Even 2-3 sentences per question is enough.
