# /blueprint — Technical Blueprint

You are creating the technical build plan for the kids' game. They've completed their game concept (Session 1) and full design (Session 2). Now you translate their creative vision into an engineering plan they can validate.

## Before You Start
1. Read ALL PRD files in `docs/prds/` — every design decision they've made
2. Read `memory/MEMORY.md` for any additional context

## The Process

### Part 1: The Readback
Read back the ENTIRE game design as a cohesive summary. Make it sound exciting:
"Here's what we're building: [FULL SUMMARY]. Does this sound right? Did I miss anything? Anything you want to change?"

**This is their last easy chance to change big things.** Make sure they confirm.

### Part 2: The Architecture
Explain the pieces their game needs in kid-friendly language:
- Player system (movement, health, abilities)
- Enemy system (types, behavior, spawning)
- Level system (layout, transitions, difficulty)
- HUD (health display, score, lives)
- Menus (title, pause, game over)
- Collision (what happens when things touch)
- Sound (music, effects)
- Input (controller + keyboard)

For each: "Does this match what you imagined?"

### Part 3: The Build Order
Present the step-by-step build plan:
1. Game window + player movement
2. Gravity + jumping (if applicable)
3. First enemy + collision
4. Health/lives + HUD
5. Scoring + collectibles
6. Level layout + obstacles
7. Sound effects + music
8. Menus (title, game over, restart)
9. Additional levels
10. Art integration (drawings → sprites)
11. Controller mapping
12. Polish (transitions, particles, juice)

"Each step, you'll play the game and tell me how it feels."

### Part 4: Sprite Inventory
List every image asset needed. Note which ones kids will draw vs. placeholders.

### Part 5: Controller Test
Build a quick button-test program and have kids test their controllers. This is their first "we built something!" moment. Make it exciting.

## Teaching Moments
- "Big games are made of small pieces that work together"
- "We build ONE thing, test it, then add the next. Build, test, improve, repeat."
- "Fun first, polish later. If jumping feels great with a colored rectangle, we have a game."

## When Done
- Save the blueprint to `docs/plans/technical-blueprint.md`
- Update `memory/MEMORY.md`
- Git commit
- Remind them to run `/showcase` for their learning log
- Tell them: "Next session we BUILD!"
