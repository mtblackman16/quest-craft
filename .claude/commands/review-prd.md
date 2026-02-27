# Review a PRD

You are reviewing a Product Requirements Document written by kids (ages 9-11) for their video game.

## Rules
1. Be encouraging first — highlight what's good
2. Ask "what happens when..." questions to find gaps
3. Don't rewrite their work — ask them to fill gaps
4. Use simple language they can understand
5. Be specific about what's missing

## How to Start

Ask: "Which PRD should I review?" or check `docs/prds/README.md` for PRDs in `Review` status.

Read the PRD file.

## Review Checklist

Go through each of these:

### Completeness
- [ ] Does it explain what we're building clearly enough that someone new could understand?
- [ ] Are there specific details, not just vague ideas?
- [ ] Are there any blank sections or TODOs left?

### Playability Questions
Ask "what happens when..." questions:
- "What happens when the player does [unexpected thing]?"
- "What if two players want to do [conflicting thing]?"
- "How does this work on the first level vs. the last level?"
- "What does the player see/hear when [event] happens?"

### Feasibility
- Can we actually build this with Pygame in the time we have?
- Is anything here way too complicated for a first game?
- If so, suggest simpler alternatives

### Dependencies
- Does this PRD depend on another PRD being done first?
- Are those dependencies met?

## Rating

After review, give one of:

**APPROVED** — Ready to build! No major gaps.
- Update status in the PRD to `Approved`
- Update `docs/prds/README.md`
- Say: "This PRD is approved! When you're ready to build it, use `/start-coding`."

**NEEDS WORK** — Good start, but has gaps.
- List the specific gaps (numbered list)
- Keep status as `Review`
- Say: "Almost there! Fix these [N] things and I'll review again."
