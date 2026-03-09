# Exhibition Checklist — LASD Illuminate

**Date:** March 27, 2026 (4:00–7:00 PM, setup 3:30 PM)

**What:** Showcase your game AND the story of how you learned to build it (Illuminate Inquiry Exhibition).

> "The focus is sharing not only what you discovered or made, but HOW you learned."

---

## The Demo Station

### Hardware
- [ ] Raspberry Pi 5 with power supply
- [ ] Monitor (HDMI connected to Pi)
- [ ] 2 Nintendo Switch controllers (charged to 100%!)
- [ ] USB keyboard (backup)
- [ ] Extension cord / power strip
- [ ] Table for setup

### Software
- [ ] Game launches correctly: `python3 -m game.main`
- [ ] Controllers paired and working
- [ ] Game runs without crashes for 30+ minutes of play
- [ ] Sound works (speakers or monitor audio)
- [ ] Exhibition launch script tested: `scripts/exhibition.sh`

### Backup Plan
- [ ] Backup SD card (full disk image)
- [ ] Game copied to USB drive
- [ ] Keyboard controls work if controllers fail
- [ ] Mark's phone as hotspot (if WiFi needed)

---

## The Display Board (Tri-fold)

### Printed Exhibition Pages (10 total)
- [ ] **01 — Title Card** (`docs/exhibition/01-title-card.html`)
- [ ] **02 — Inquiry Question** (`docs/exhibition/02-inquiry-question.html`)
- [ ] **03 — Our Process** (`docs/exhibition/03-our-process.html`)
- [ ] **04 — The Game** (`docs/exhibition/04-the-game.html`) — needs real screenshot
- [ ] **05 — The Team** (`docs/exhibition/05-the-team.html`) — needs team photo
- [ ] **06 — Reflections** (`docs/exhibition/06-reflections.html`) — updated with Session 4+5 quotes
- [ ] **07 — How to Play** (`docs/exhibition/07-how-to-play.html`)
- [ ] **08 — Controller Diagram** (`docs/exhibition/08-controller-diagram.html`)
- [ ] **09 — Supply List** (internal — don't display)
- [ ] **10 — Learning Journey** (`docs/exhibition/10-learning-journey.html`) — Illuminate phases

### Kid-Generated Artifacts (Display These)
- [ ] Completed Experiment/Build Record sheets from Session 4 (1 per kid)
- [ ] Learning Story reflections from Session 5 (1 per kid)
- [ ] Andrew's artwork (jello cube, sanitizer warrior, etc.)
- [ ] Character drawings (player, enemies, friendlies)
- [ ] Level maps (graph paper, if any)

### Photos (Print 2-3 Large)
- [ ] Team photo from Session 2 (couch coding shot)
- [ ] Process photos from Session 4 (kids playtesting, talking to Claude)
- [ ] Gameplay screenshots (captured between sessions)

### Board Layout
```
┌─────────────────────────────────────────────────────────┐
│  LEFT PANEL       │  CENTER PANEL      │  RIGHT PANEL   │
│                   │                    │                │
│  Our Process      │  Title Card        │  Reflections   │
│  (03)             │  (01)              │  (06)          │
│                   │                    │                │
│  The Team         │  Game Screenshot   │  Learning      │
│  (05) + photo     │  (04)              │  Journey (10)  │
│                   │                    │                │
│  Inquiry Question │  How to Play       │  Build Records │
│  (02)             │  (07)              │  (kids' sheets)│
│                   │                    │                │
│  Process photos   │  Andrew's artwork  │  Session photos│
└─────────────────────────────────────────────────────────┘
```

---

## Illuminate Evidence Checklist

The exhibition expects evidence across all 4 Illuminate phases:

### Phase 1: What did we investigate and why?
- [ ] Inquiry question displayed (02-inquiry-question.html)
- [ ] Game concept & design docs available to reference

### Phase 2: What did we learn?
- [ ] Build Record sheets from Session 4 playtesting (kids filled these in)
- [ ] Process photos showing iterative development
- [ ] "By the Numbers" stats on our-process page

### Phase 3: How did we learn it?
- [ ] Learning Story reflections from Session 5 (PMI, Bridge, or Freeze Frame)
- [ ] Deeper reflection quotes in 06-reflections.html
- [ ] 10-learning-journey.html connecting our process to Illuminate phases

### Phase 4: Exhibition of Learning
- [ ] Live playable game demo on Pi
- [ ] Display board assembled with all materials
- [ ] Each kid can answer: "How did you build this?" and "What did you learn?"
- [ ] Demo script practiced

---

## The Demo Script

Practice this flow:

1. **Greeting:** "Hi! We built a game called SPLIT!"
2. **The Pitch:** "It's a platformer where you play as a jello cube fighting through a monster-filled castle. The coolest part is the jello can split apart to dodge and shoot pieces of itself."
3. **How We Built It:** "We designed the whole game by talking to an AI called Claude. We told it what we wanted — characters, levels, bosses, everything — and it wrote the code. We're the game designers, Claude is the engineer."
4. **The Learning:** "The biggest thing we learned is that YOUR WORDS change the code. When we said 'the jump feels too floaty,' Claude changed one number and it was fixed. Communication IS the skill."
5. **Invite to Play:** "Want to try it? D-pad to move, A to jump, B to shoot. Try to get past Floor 3!"
6. **While They Play:** Stand by to help. Point out cool features. Be proud!
7. **The Closer:** "The hardest part was describing bugs clearly. The thing we're most proud of is that 4 kids and an AI built a real game with 15 levels and 5 bosses."

### Who Does What
- [ ] **Person 1:** Greets visitors, gives the pitch
- [ ] **Person 2:** Explains how the game was built (points to display board)
- [ ] **Person 3:** Hands controllers to visitors, explains controls
- [ ] **Person 4:** Points to Build Records and reflections, answers "how did you learn?"
- Rotate roles every 30 minutes!

---

## Exhibition Day Timeline

| Time | What |
|------|------|
| 3:00 PM | Load car: Pi, monitor, power strip, display board, controllers, backup USB |
| 3:30 PM | Arrive at school, set up table |
| 3:35 PM | Set up Pi + monitor + controller, boot game |
| 3:40 PM | Set up display board behind demo station |
| 3:50 PM | Sound check, controller check, full test run |
| 3:55 PM | Team huddle — assign first rotation roles |
| 4:00 PM | Exhibition opens! |
| 5:00 PM | Rotate roles |
| 6:00 PM | Rotate roles |
| 7:00 PM | Exhibition ends |
| 7:30 PM | Pack up everything |

---

## Last-Minute Checks (Day Before)

- [ ] 3+ hour soak test passed (game runs without crash)
- [ ] Controllers charged to 100%
- [ ] All display materials printed and trimmed
- [ ] Display board assembled (or ready to assemble at setup)
- [ ] Backup SD card created
- [ ] Everything packed in one bag (use this checklist!)
- [ ] Each kid has practiced the demo at least once

## Day-Of Checks

- [ ] Pi powered on and game runs via `scripts/exhibition.sh`
- [ ] Sound is working and at good volume
- [ ] Controllers paired and responsive
- [ ] Display board standing and stable
- [ ] Each team member knows their first role
- [ ] Backup USB drive in Mark's pocket
- [ ] HAVE FUN!
