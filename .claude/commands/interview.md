# /interview -- "Behind the Game" Session 5 Interview

You are running an interactive interview with 4 kids (ages 9-11) who built SPLIT, a video game, with AI. The kids answer via Wispr Flow. You ask questions directly on screen, respond conversationally, follow up when answers are thin, and capture everything.

This interview collects Inquiry Exhibition evidence (reflections on learning and process) and prepares the kids for their exhibition demo. No writing from the kids -- just talking.

## Team
- **Ethan** (9) -- Co-creator & Game Designer
- **Eins** (11) -- Co-creator & Game Designer
- **Andrew** (11) -- Artist & Visual Designer
- **Nathan** (9) -- Co-creator & Game Designer (missed Session 4)

## What We Already Have (Don't Re-Ask)
- Session 2: Eins said process was more fun than expected. Ethan learned commit/push. Nathan said ideas matter. Andrew said committing is important.
- Session 4: Eins said "AI needs context." Andrew gravitated to QA, hardest part was "the right words." Ethan surprised by bug count, said "it takes a team."
- All PRDs and game design decisions already captured. Don't rehash design details.

## Format

Run through 4 acts. Ask questions one at a time. Wait for Wispr dictation between each. Respond naturally -- react to what they say, ask follow-ups, make connections. Tag every answer internally with the kid's name and which Illuminate phase it covers.

When a kid gives a short answer, follow up: "Tell me more about that" or "Give me an example" or "Why was that hard?" Don't accept one-word answers for the hot seat questions.

---

## ACT 1: "THE PITCH" -- Team Warm-Up (10 min)

Whole team, anyone can jump in.

**Q1:** "Pretend I just walked up to your booth and I've never heard of your game. What do you tell me?"
- Let them workshop together. If rambling: "Love it -- now shorter." Repeat until punchy. This becomes the elevator pitch.

**Q2:** "Why a jello cube? Out of everything in the world, why jello?"
- Fun warm-up. Connect back to Session 1 origin.

**Q3:** "What's the ONE thing in the game you'd show someone first?"
- Go around the circle, each kid picks one. No repeats.

**Q4:** "You built this game across 5 sessions. Describe each session in one word."
- Dream, Design, Build, Playtest, today. Each kid picks a word for whichever session they want.

---

## ACT 2: "THE STORY OF SPLIT" -- Origin + AI Collab (15 min)

Directed -- one kid leads each question, others add.

**Q5 [EINS leads]:** "Take me back to Session 1. You walked in not knowing what you were going to make. What happened that day?"
- Others can jump in after Eins starts.

**Q6 [NATHAN leads]:** "Nathan, you missed the playtesting session. What did the other guys tell you about it? And when you played the game after, was it what you expected?"
- Then to the group: "What was the wildest bug you found that day?"

**Q7 [ANDREW leads]:** "Andrew, your actual drawings are in the game. What's it like seeing your art move around on screen?"

**Q8 [ETHAN leads]:** "Ethan, give me a real example of how you told Claude what to build. Like, what did you actually say to it?"

**Q9 [WHOLE TEAM]:** "Did Claude ever get it totally wrong? What happened?"

**Q10 [WHOLE TEAM]:** "In Session 2, the hardest decision was level design. Looking back now, what was ACTUALLY the hardest decision of the whole project?"

---

## ACT 3: "PLAYER PROFILES" -- Individual Hot Seats (25 min)

One kid at a time, ~6 min each. Order: Eins, Andrew, Ethan, Nathan.
Other kids can play the game on the Pi while waiting.

**For EACH kid, ask these questions:**

**Q11:** "Your team's big question was 'What can kids create when they have AI as an engineering partner?' What's YOUR answer to that?"
- [Illuminate Phase 1]

**Q12:** "What did you learn from this project that you didn't know before? Not just about games -- about anything."
- [Illuminate Phase 2]. If surface-level: "What else?" or "Tell me more."

**Q13:** "HOW did you learn that? Was it from talking, building, breaking stuff, arguing about designs...?"
- [Illuminate Phase 3]

**Q14:** "What surprised you the most?"
- Don't reference their Session 2 answers. Ask fresh. We'll compare later to show growth.

**Q15:** "What was the hardest moment for YOU -- not the team, just you personally?"

**Q16:** "What are you most proud of?"
- Give them a beat. Don't rush.

**Q17:** "If you could go back to Session 1 and whisper one piece of advice to yourself, what would it be?"

**Then ask their personal bonus question:**

- **EINS:** "In Session 4 you said 'AI needs context.' Is that still the biggest thing you learned, or has something else taken over?"
- **ANDREW:** "You started as the artist but you ended up being one of the best bug finders. How did that happen?"
- **ETHAN:** "You said you were surprised by how many bugs there were. We fixed all of them. Was all that bug-fixing worth it?"
- **NATHAN:** "You said in Session 2 that everybody's ideas are important. Did missing a session change how you feel about that?"

---

## ACT 4: "SHOWTIME" -- Demo Rehearsal (15 min)

**Q18: Role Assignment (3 min)**
Present the 4 exhibition roles and let kids self-select:
- **Greeter**: "Hi! We built a game called SPLIT!" (opens conversation)
- **Builder**: "We designed it and an AI called Claude wrote the code" (points to board)
- **Demo Guide**: Hands controller to visitor, explains controls
- **Learner**: Points to reflections, explains what team learned

They rotate every 30 min at exhibition. Everyone gets every role.

**Q19: Practice Run 1 (5 min)**
Tell Mark to play visitor and walk up cold. Claude captures the kids' natural language.

**Q20: Hard Questions Round (5 min)**
Tell Mark to play skeptical visitor and ask:
- "So the AI did all the work?"
- "Did you actually write any code?"
- "What did YOU learn from this?"
- "How is this different from just using ChatGPT?"

Claude captures their answers for the demo cheat sheet.

**Q21: The Closer (2 min)**
Go around the circle. Each kid fills in:
**"Before this project, I thought ____. Now I know ____."**
One shot each. These become the closing quotes on the display board.

---

## AFTER THE INTERVIEW -- Generate Outputs

Once all 4 acts are complete, generate these files:

### 1. Game Box Cover
- File: `docs/exhibition/game-box-cover.html`
- Large "SPLIT" title + jello cube graphic (use `assets/images/player/jello-cube-three-quarter.png` as base64-embedded image)
- Tagline from the polished elevator pitch (Q1)
- Subtitle: "A Jello Cube Adventure"
- Style: bold, eye-catching, like a real game box cover. Dark background, bright green jello cube, large white text.
- Full page, landscape orientation for center-top of tri-fold board

### 2. Individual Reflection Cards (4 files)
- Files: `docs/exhibition/reflection-ethan.html`, `reflection-eins.html`, `reflection-andrew.html`, `reflection-nathan.html`
- Each card: kid's name, age, role, and their Q11-Q17 answers in their own words
- Half-page format for mounting on board
- Style: match existing exhibition CSS (green accent on dark background)

### 3. Updated Reflections Page
- File: `docs/exhibition/06-reflections.html`
- Update with Session 5 quotes alongside existing Session 2 quotes
- Add "Before/After" section with Q21 closing quotes
- Print-ready

### 4. Team Quotes Sheet
- File: `docs/exhibition/team-quotes-board.html`
- Elevator pitch, "How we worked with AI" narrative, each kid's "one thing," best bug story
- Cut-out format for mounting

### 5. Demo Cheat Sheet
- File: `docs/exhibition/demo-cheat-sheet.html`
- Role assignments, elevator pitch, hard question answers
- One page for back of display board

### 6. Session 5 Learning Log
- File: `docs/learning/learning-logs/session-5-showcase.md`
- Full transcript organized by act, all answers tagged by kid and Illuminate phase

### 7. Parent Summary
- File: `docs/parent-summaries/session-5-showcase.html`
- Summary of the session with best quotes and key moments
- Mark will add photos after the session

After generating, tell Mark: "All outputs generated. Here's what's ready to print: [list files]. You can add Session 5 photos to the parent summary whenever you're ready."
