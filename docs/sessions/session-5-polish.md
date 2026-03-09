> **OBSOLETE** — This guide has been replaced by `session-5-showcase.md` which focuses on Illuminate exhibition prep: display board assembly, deep reflections, and demo rehearsal.

# Session 5: POLISH & SHOWCASE — The Final Push (ARCHIVED)

**Goal:** Polish the game, get controllers working perfectly, prepare everything for the exhibition.

**Time:** ~2 hours

**What you need:** Voice (Wispr Flow), Nintendo Switch controllers, printed design docs, character sketches, markers for the exhibition display

**Slash command:** `/showcase`

---

## How This Session Works

Your game is built! Now we make it great and get ready to show it off. This session has three parts: polish the game, fix the bugs, and prepare the exhibition.

---

## Part 1: Controller Setup & Full Playthrough (~30 min)

### Controller Pairing
1. Put your Nintendo Switch Pro Controller in pairing mode (hold the sync button)
2. Claude walks you through Bluetooth pairing on the Pi
3. Run the controller test to verify all buttons work
4. If buttons are mapped wrong, tell Claude and it'll fix the mapping

### Full Playthrough
Everyone plays the COMPLETE game from title screen to the end:
- Start at the title screen
- Play through every level
- Try to trigger every enemy, collect every item
- See the game over screen
- Restart and play again

### Bug List
While playing, write down EVERYTHING that's broken or weird:
- "The player gets stuck on this wall"
- "If I jump and attack at the same time, it glitches"
- "The score doesn't reset when I restart"
- "This enemy spawns inside a wall"
- "The music keeps playing on the game over screen"
- "Level 2 is way harder than Level 3"

---

## Part 2: Bug Fixes & Polish (~45 min)

### Bug Fix Sprint
Read your bug list to Claude, one at a time. Claude fixes each one, you re-test.

### Polish Pass
After bugs are fixed, add the final touches:
- [ ] Title screen looks good with game name and "Press Start"
- [ ] Game over screen shows final score and "Press [Button] to Play Again"
- [ ] Screen transitions between levels (fade, slide, etc.)
- [ ] Any missing sound effects
- [ ] Any missing visual effects (juice!)
- [ ] Difficulty feels right across all levels
- [ ] Controller feels responsive and natural

### The Quality Check
Play the game ONE MORE TIME, start to finish, pretending you've never seen it before. Ask yourself:
- Would I show this to my friends?
- Is it fun?
- Does anything confuse me?
- Am I proud of this?

---

## Part 3: Exhibition Prep (~45 min)

### Materials to Prepare

**Physical Display:**
- [ ] Print the Game Concept Document (Session 1 output)
- [ ] Print the Game Design Document highlights (Session 2 output)
- [ ] Display character sketches (from Session 2 drawing activities)
- [ ] Display level maps (from Session 2 graph paper)
- [ ] Display controller mapping diagram
- [ ] Print the "How We Engineered It" technical blueprint (Session 3)
- [ ] Print build timeline screenshots (from Session 4)

**The Inquiry Question:**
Write your inquiry question and what you learned. Something like:
- "How do people make video games?" → Here's what we learned...
- "Can kids build a real video game with AI?" → Yes, and here's how...
- "What goes into making a fun game?" → Way more than we thought...

**Learning Reflections:**
Each team member writes a short reflection:
- What did you learn?
- What was the hardest part?
- What are you most proud of?
- What would you do differently next time?
- How did AI help you build this?

### Demo Setup
- [ ] Raspberry Pi connected to monitor
- [ ] Controllers charged and paired
- [ ] Game launches correctly from boot
- [ ] "How to Play" card written for exhibition visitors
- [ ] Each team member knows their part of the demo

### Practice the Demo
Rehearse showing the game to someone who's never seen it:
1. "Hi! We built a game called [NAME]."
2. "It's a [GENRE] game where you [MAIN ACTION]."
3. "We designed it ourselves and built it with AI."
4. "Want to try it? Here's how to play: [CONTROLS]."
5. "The thing we're most proud of is [HIGHLIGHT]."

---

## Code Freeze

When everything is ready:
- Claude commits the final version: `git tag v1.0`
- No more changes after this (unless something is truly broken)
- Backup the game to a USB drive (just in case)

---

## You're Done When...

- [ ] Game runs perfectly with controllers
- [ ] All bugs from the bug list are fixed
- [ ] Polish pass is complete
- [ ] Exhibition materials are printed/displayed
- [ ] Inquiry question and reflections are written
- [ ] Demo station is set up and working
- [ ] Demo is practiced
- [ ] Code freeze — v1.0 tagged
- [ ] `/showcase` final learning reflection filled out
- [ ] THE GAME IS DONE AND YOU'RE PROUD OF IT!

---

## Talking Tips

- "This bug happens when I [EXACT STEPS]. Can you fix it?"
- "The game is ready. Let's freeze the code."
- "Read back our inquiry findings for the exhibition"
- "Help me write a 'How to Play' card for visitors"
- "What should we say when someone asks how we built this?"
