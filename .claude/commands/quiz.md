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

## ROUND 5: SECRET HUNTERS (5 min)

**This round is different.** You're not testing knowledge -- you're giving them a treasure map. The game has 8 hidden secrets and easter eggs. Drop these hints so they go hunting during playtime.

**SH1:** "Okay, bonus round. Your game has 8 hidden secrets built into it. You've probably never found any of them. Let's see if you can figure some out from clues."

**SH2:** "Secret #1 -- This one's a classic. Every great game has this cheat code. It starts with Up, Up, Down, Down... does anyone know what comes next?"
- Answer: Left, Right, Left, Right, B, A -- the Konami Code. "Try it on the title screen when you play."

**SH3:** "Secret #2 -- There's a barrel on Floor 3 that looks like it's just decoration. But if you walk up to it and press the interact button... nothing happens. Try again. Still nothing. What if you keep trying?"
- Answer: Interact with it 5 times. "It has something to say to you. Something about someone you know pretty well."

**SH4:** "Secret #3 -- Floor 1 has a suspicious spot around the middle of the level. What happens when you ground pound there?"
- Hint: "Around x position 1650. Slam the ground and see what opens up."

**SH5:** "Secret #4 -- Andrew, this one's for you. Floor 7 has a torch that looks a little different from the others. What color is it?"
- Hint: "It's purple. Walk up to it and press interact. It's your gallery."

**SH6:** "Secret #5 -- This one's creepy. If you die exactly 4 times, the game starts glitching out. The screen goes crazy with static and color shifts. Don't panic -- it's on purpose. It's called the Fourth-Wall Fracture."

**SH7:** "Secret #6 -- Put the controller down and don't touch anything for 30 seconds. Just wait. Watch what happens to your jello cube."
- Answer: Music notes float up -- the idle dance.

**SH8:** "Secret #7 -- Every time you miss a jelly shot, it splats on the wall and stays there. Miss enough of them and something happens. How many do you think it takes?"
- Answer: 50 missed shots. The walls become a jello graveyard.

**SH9:** "Secret #8 -- This one you CAN'T trigger today. It only works on one specific date. March 27th. Exhibition day. When you play the game at the exhibition, something special will happen that nobody has ever seen. You'll know it when you see it."
- Don't reveal what it is. Let them discover the gold border on exhibition day.

After this round: "That's 8 secrets. See how many you can find when you play. First person to find all 8 is the Secret Hunter champion."

---

## WRAP-UP

After the last question, celebrate:
"You just proved you didn't just build a game -- you UNDERSTAND how you built it. That's the difference between using a tool and knowing how to use a tool. Nice work. Oh, and your game has 8 secrets hidden in it that you've never found. Let's see who can find the most."

Tell them it's time to play the game now. Nathan goes first since he missed Session 4.
