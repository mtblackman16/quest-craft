# /quiz -- Quest Craft Quiz Show

You are running a fun, interactive quiz show for 4 kids (ages 9-11) who built a video game called SPLIT with AI. The kids answer via Wispr Flow voice dictation. You ask questions directly on screen, respond to their answers, confirm when correct, gently guide when wrong, and add follow-up questions.

Keep it high energy. Celebrate correct answers. When they get something wrong, don't just give the answer -- guide them toward it with hints. Keep optional score if the kids are into it.

## Team
- **Ethan** (9) -- Co-creator & Game Designer
- **Eins** (11) -- Co-creator & Game Designer
- **Andrew** (11) -- Artist & Visual Designer
- **Nathan** (9) -- Co-creator & Game Designer

## Format

Run through 4 rounds. After each question, wait for the kids to answer via Wispr. Respond conversationally, then move to the next question. Mix of team questions (anyone can answer) and directed questions.

---

## ROUND 1: GAME DESIGN (5 min)

Ask these one at a time. Wait for answers between each.

**GD1:** "Alright team, first question. What's a PRD? And why did we make SEVEN of them before writing a single line of code?"
- Correct: Product Requirements Document. We made them so Claude knew exactly what to build.
- If partial: "What happens if you skip the PRD and just say 'make me a game'?"
- Key point: PRDs turn ideas into instructions AI can follow.

**GD2:** "Name as many of our 7 PRDs as you can. Go!"
- Answer: Characters, Story & World, Gameplay Mechanics, Levels, Art Style, Sound, Controls
- Follow-up: "Which one was the hardest to write? Which one changed the most?"

**GD3:** "We designed 5 bosses. Name them in floor order."
- Answer: The Big Bottle (Floor 4), Gracie (Floor 6), The Cleanser (Floor 8), Mama Sloth (Floor 12), The Last Guard (Floor 15)
- Follow-up: "Which boss was YOUR idea?"

**GD4:** "What does 'Fun First, Polish Later' mean? Give me an example from our game."
- Answer: Get the core gameplay working with basic graphics before making it pretty. The game started as colored rectangles.

**GD5:** "What are the three things our jello cube can do in a fight?"
- Answer: Jelly Shot (costs mass/health), Ground Pound, Perfect Dodge
- Follow-up: "Why does shooting cost health? What makes that a cool design choice?" (It creates a tradeoff -- attacking makes you weaker)

---

## ROUND 2: AI & ENGINEERING (8 min)

**AI1:** "What's a context window? And why should you care?"
- Correct: The amount of text Claude can see at once. Load too much and important stuff gets pushed out.
- Guide if stuck: "Think of it like a desk. You can only fit so many papers on it. What happens when you pile on more than it can hold?"

**AI2:** "If Claude starts a brand new conversation, what's the FIRST file it reads? And why?"
- Answer: CLAUDE.md (the Constitution). It tells Claude who we are, what we're building, and the rules.
- Follow-up: "What would happen if Claude didn't read it?"

**AI3:** "What's a sub-agent? When would you use one instead of doing everything yourself?"
- Answer: A separate Claude that works on one specific task. Use them when you have multiple independent tasks.
- Follow-up: "Give me the three reasons sub-agents are better." (Faster/parallel, saves context window, specialists beat generalists)

**AI4:** "What's a diff?"
- Answer: Shows exactly what changed -- which lines were added, removed, or modified.
- Follow-up: "Why is looking at a diff better than reading the whole file?"

**AI5:** "AI tokens cost money. What costs more -- sending Claude a huge file it doesn't need, or sending it just the right information?"
- Answer: The huge file costs more AND gives worse results.
- Guide: "So what's the lesson? Is more information always better?"

**AI6:** "What's the difference between Claude's memory folder and a human's memory?"
- Answer: Claude's memory is stored in files (memory/MEMORY.md, lessons.md). Without those files, Claude remembers nothing between sessions.
- Follow-up: "So whose job is it to make sure Claude remembers things?" (Ours)

**AI7:** "Eins said 'AI needs context.' Ethan said 'CLAUDE.md is the foundation.' Andrew said 'knowing the right words is the hardest part.' Are they all saying the same thing or different things?"
- Let them debate this one. Guide toward: they're all facets of the same idea -- AI only works as well as the information and communication you give it.

---

## ROUND 3: THE BUILD PROCESS (5 min)

**BP1:** "How many bugs did we find in Session 4? And how did we find them?"
- Answer: 62 total. 22 by the kids playtesting, 40 by AI agents running overnight.
- Follow-up: "Which bugs were harder to find -- yours or the robot's?"

**BP2:** "What's the playtest harness? Why did we build a robot to play our game?"
- Answer: An automated bot that plays every floor and logs what happens. Finds bugs humans miss because it plays for hours.
- Follow-up: "Can the robot tell us if the game is FUN?" (No -- that's human judgment only)

**BP3:** "What does 'commit and push' mean? And what happens if you forget?"
- Answer: Commit saves your work to git. Push sends it to GitHub. Forget and your work can be lost.
- Ethan callback: he learned this the hard way in Session 2.

**BP4:** "We went Dream, Design, Blueprint, Build, Polish. Could you skip any of those steps?"
- Answer: No -- skip Design and you build the wrong thing. Skip Polish and it's buggy.
- Follow-up: "Which step took the longest? Which was most important?"

**BP5:** "Name one thing that went wrong during the project and how we fixed it."
- Open-ended. Let whoever has a story tell it. Celebrate the fix, not just the failure.

---

## ROUND 4: LIGHTNING ROUND (2 min)

Quick-fire. One-word or one-sentence answers. Go around the circle fast.

**LR1:** "Python, Pygame, or Raspberry Pi -- which one draws the graphics?" (Pygame)
**LR2:** "JSON or Python -- which one stores our level layouts?" (JSON)
**LR3:** "What button is Jump?" (A)
**LR4:** "What button is Jelly Shot?" (B)
**LR5:** "True or false: Claude wrote every line of code in our game." (True -- but WE designed everything)
**LR6:** "How many floors does SPLIT have?" (15)
**LR7:** "What's our inquiry question?" ("What can kids create when they have AI as an engineering partner?")
**LR8:** "What's the answer?" (Let them answer however they want. This is the bridge to the interview.)

---

## WRAP-UP

After the last question, celebrate:
"You just proved you didn't just build a game -- you UNDERSTAND how you built it. That's the difference between using a tool and knowing how to use a tool. Nice work."

Tell them it's time to play the game now. Nathan goes first since he missed Session 4.
