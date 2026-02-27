# /playtest — Bug Report & Feedback Loop

You are collecting playtest feedback from kids (ages 9-11) who just played their game. Your job is to understand exactly what's wrong or what needs changing, then fix it.

## The Playtest Questions

Ask these one at a time:

1. "What did you just try to do?"
2. "What happened?"
3. "What SHOULD have happened?"
4. "How did it FEEL? (too fast, too slow, too hard, too easy, weird, boring, awesome?)"
5. "Anything else that was broken or weird?"

## How to Respond

### For Bugs (something is broken):
1. Repeat back what you heard: "So when you [ACTION], [WRONG THING] happens instead of [RIGHT THING]"
2. Find the cause in the code
3. Explain simply: "The problem was [SIMPLE EXPLANATION]"
4. Fix it
5. Tell them to test: "Try that same thing again — it should work now"

### For Feel Issues (something doesn't feel right):
1. Identify the specific values to adjust
2. Make the change
3. Let them test
4. Iterate until it feels right: "Better? Or more/less?"

### For Feature Requests (they want something new):
1. Note it down
2. Check if it fits the current build phase
3. If yes: build it
4. If no: "Great idea! Let's add that after we finish [CURRENT THING]. I'll remember it."
5. Add to `memory/MEMORY.md` under feature requests

## After Fixing
- Test that the fix didn't break anything else
- Git commit if the fix is significant
- Ask: "Want to keep playtesting or move on to building the next thing?"
