# Session 5: Showcase — Interview & Quiz Transcript
**Date:** March 22, 2026
**Present:** Ethan (9), Eins (11), Andrew (12), Nathan (9), Mark (facilitator)

---

## Quiz Show Highlights

### Round 1: Game Design
- Team correctly defined PRD (Product Requirements Document) and listed all 7
- Named all 5 bosses in order: Big Bottle, Gracie, Cleanser, Mama Sloth, The Last Guard
- Gracie and Mama Sloth were Ethan's ideas; rest were collaborative
- "Fun First, Polish Later" = get core gameplay working before adding polish
- Knew Jelly Shot and Ground Pound; learned Perfect Dodge is the third combat move
- Understood risk/reward tradeoff of Jelly Shot costing health

### Round 2: AI & Engineering
- Defined context window correctly — where you store info so AI understands you
- Learned CLAUDE.md is the first file Claude reads every session ("the Constitution")
- Excellent sub-agent explanation: "like making somebody else do a task so you focus on the main thing"
- Understood diffs, token costs, and that quality > quantity for AI input
- Eins: "AI needs context." Ethan: "CLAUDE.md is the foundation." Andrew: "knowing the right words is the hardest part." Team agreed these are related but different facets of the same idea.

### Round 3: Build Process
- Recalled 62 bugs found in Session 4 (22 human, 40 automated)
- Understood playtest harness purpose; agreed robots can't judge fun
- Knew commit = save, push = send to GitHub
- Agreed no step in Dream→Design→Blueprint→Build→Polish can be skipped
- Bug stories: platform clipping death, controller disconnects, random crashes

### Round 4: Lightning Round
- All answers correct: Pygame, JSON, A=jump, B=shoot, 15 floors, True (Claude wrote all code)
- Inquiry question: "What can kids create when they have AI as an engineering partner?"

### Round 5: Secret Hunters
- Knew the Konami Code immediately
- Given hints for all 8 easter eggs to discover during playtime

---

## Interview — ACT 1: "The Pitch"

### Q1: Elevator Pitch
**Team:** "This is a game that we made over the past month or so, where you are playing as a squishy jelly cube and are trying to escape a castle. It is a 2D platformer and has some hidden easter eggs, and we hope you enjoy."

### Q2: Why Jello?
**Team:** "Jello feels kid-friendly and fun, and we were thinking about something that would be simple to create and yet be kind of memorable." [Illuminate Phase 1]

### Q3: One Thing to Show First
- **Eins:** The final boss
- **Andrew:** The level design
- **Ethan:** The hidden easter eggs
- **Nathan:** How to play and how to heal yourself

### Q4: Each Session in One Word
- Dream = Planning
- Design = Creating
- Build = Building
- Playtest = Checking
- Showcase = Showing

---

## Interview — ACT 2: "The Story of SPLIT"

### Q5: Session 1 Origin (Eins led)
**Team:** Had discussed the game at school beforehand — knew the jello concept and basic art style. Came in with hand-drawn plans on paper. The seed was there but all the details got figured out in the sessions. [Illuminate Phase 1]

### Q6: Nathan's Perspective
**Nathan:** The game was bigger than expected, the jello cube looked different, and it was harder than expected. [Illuminate Phase 2]

**Team (wildest bug):** Standing under a platform where you couldn't unsplit would clip you out and kill you or restart the level.

### Q7: Andrew's Art in the Game
**Andrew:** "It's pretty nice, but I wish I could have animated it a bit more and made it look more interesting. I would have made the enemies face different directions when they walk in different ways and finish creating the other enemies, because I did not have time to finish their designs." [Illuminate Phase 2]

### Q8: How Ethan Directed Claude
**Ethan:** "I said to make a jelly shot and make it shoot and make the jelly cube motion." Had to go back and forth to get it right. [Illuminate Phase 3]

### Q9: Did Claude Get It Wrong?
**Team:** "Some of the enemy designs are kind of wonky, and the game turned out pretty different from what we originally thought, but in a good way." [Illuminate Phase 2]

### Q10: Hardest Decision
**Team:** "The character." — How bouncy, how it moves, eyes or no eyes, how it represents things, deciding on different characters and monsters. [Illuminate Phase 2]

---

## Interview — ACT 3: "Player Profiles"

### EINS (age 11)

**Q11 — Inquiry Answer:** "Kids can design a game that can be extremely successful since kids play games themselves and have great taste in games." [Phase 1]

**Q12 — What Learned:** "A lot about AI and how this whole system works and how to use GitHub in VS Code Advanced." Specifically: "It doesn't remember every single little thing that you say to it and all the other little details." [Phase 2]

**Q13 — How Learned:** "We told Claude many, many things, and when it actually made the game, it didn't make all the little details. I would have made the little details first before doing the big stuff. I think for AI, it should be a little more perfect." [Phase 3]

**Q14 — Surprised By:** "How fast the AI can develop a single entire game, like all the music and stuff, without us asking it too hard." [Phase 2]

**Q15 — Hardest Moment:** "When the deadline was close, before I thought it was March 15th, not 27th, and I got really, really nervous that we wouldn't be able to finish this thing. There was no backing out of the submission." [Phase 2]

**Q16 — Most Proud Of:** "I think kids would be very, very impressed." [Phase 2]

**Q17 — Advice to Session 1 Self:** "We could take it step by step and not give the AI everything. Otherwise, once it forgets, it's also hard for us to re-tell it." [Phase 3]

**Bonus — "AI needs context" still biggest lesson?** "I think the structure, the folder structure." — Understanding that project organization is what gives AI its context. [Phase 3]

---

### ANDREW (age 12)

**Q11 — Inquiry Answer:** "They can create a memorable and fun game." [Phase 1]

**Q12 — What Learned:** "The basics of a Raspberry Pi and overall game design, as well as how to prompt AI so that it understands you." Learned through "practice and coaching by Mark." [Phase 2]

**Q13 — How Learned:** "Mark showing us and times when Claude did not really understand us." [Phase 3]

**Q14 — Surprised By:** "How quickly Claude could understand us and do what we wanted to and create a functioning game, even if it isn't perfect." [Phase 2]

**Q15 — Hardest Moment:** "Actually getting the game to run smoothly without any glitches that don't let you play." [Phase 2]

**Q16 — Most Proud Of:** "The artwork that got into the game and how many things worked out well." [Phase 2]

**Q17 — Advice to Session 1 Self:** "I should not worry so much about how the designs that I make turn out, and that I should just go with the flow." [Phase 3]

**Bonus — Artist to bug finder?** "Maybe because in some other games I play very thoroughly and try to make everything work well without any bugs." — Brought gamer instincts to QA testing. [Phase 3]

---

### ETHAN (age 9)

**Q11 — Inquiry Answer:** Kids "can't create that much code that AI can do in a few days." AI unlocks building things that would take way longer without it. [Phase 1]

**Q12 — What Learned:** "About assets and folders and how to prompt AI." Specifically: "You need context. If you just say 'make a game', then it wouldn't know what game to make or how to make it." [Phase 2]

**Q13 — How Learned:** "Talking." — To Claude, to each other, to Mark. [Phase 3]

**Q14 — Surprised By:** "How the game turned out" — in a good way. Exceeded expectations. [Phase 2]

**Q15 — Hardest Moment:** "Prompting Claude to do the thing that you actually want it to do." [Phase 2]

**Q16 — Most Proud Of:** "The levels of the game." [Phase 2]

**Q17 — Advice to Session 1 Self:** "To prompt better so Claude understands." [Phase 3]

**Bonus — Was bug-fixing worth it?** "Yes. You can't go through levels because there are too many glitches." Without fixes, the game is unplayable. [Phase 2]

---

### NATHAN (age 9)

**Q11 — Inquiry Answer:** Designed "where to put the checkpoints in certain places so you could rest where there's not a lot of bad guys." AI made the level design ideas real. [Phase 1]

**Q12 — What Learned:** "Even if the Raspberry Pi breaks, you can use GitHub to still have the code." — Backups and version control. [Phase 2]

**Q13 — How Learned:** "Talking with Mark." [Phase 3]

**Q14 — Surprised By:** "We can create a game without having to go through that many processes, and Claude can do the coding for us." [Phase 2]

**Q15 — Hardest Moment:** "Designing how to build and design the game." — The blank page problem. [Phase 2]

**Q16 — Most Proud Of:** "Being able to create the game and show it to the people at Illuminate." [Phase 2]

**Q17 — Advice to Session 1 Self:** "To remember to add more bosses." [Phase 3]

**Bonus — Did missing Session 4 change "everyone's ideas matter"?** "No." Still believes it. [Phase 2]

---

## Key Themes Across All Four Kids

1. **AI speed is shocking** — All four mentioned how fast Claude builds things
2. **Prompting is the real skill** — Ethan, Andrew, and Eins all identified communication with AI as the hardest and most important thing they learned
3. **AI forgets** — Eins and Ethan both learned that AI doesn't remember everything; you have to manage it
4. **Design is harder than coding** — The creative decisions (character, levels, enemies) were harder than the technical implementation
5. **Bug-fixing matters** — Andrew and Ethan both emphasized that a broken game is worse than an unfinished one
6. **Kids as designers** — Eins's insight that kids have great game taste because they ARE the audience

## Before/After Quotes (ACT 4)

**Q21 — "Before this project I thought ___. Now I know ___."**

**Eins:** "Before this project, I thought AI does all the work. Now I know you have to direct it carefully." [Phase 3]

**Andrew:** "Before this project, I thought you need to know how to code to make a game. Now I know you need to know what you want and how to prompt AI to do it with you." [Phase 3]

**Ethan:** "Before this project, I thought making games requires coding skills. Now I know you need ideas and clear communication." [Phase 3]

**Nathan:** "Before this project, I thought making games requires coding skills. Now I know kids can do it with AI." [Phase 3]

---

## ACT 4: Before/After + Demo Rehearsal
Before/After quotes captured above. Role assignments and final practice TBD for exhibition day.
