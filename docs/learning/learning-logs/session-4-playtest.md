# Session 4 Learning Log -- March 15, 2026

## Topics Covered

### Game Development
- First full playthroughs of SPLIT on the Raspberry Pi with Pro Controller
- Bug identification during live gameplay
- Using Wispr Flow voice dictation to report bugs to Claude in real time
- /bughunt command for batch bug collection and fix rounds

### AI and Engineering Concepts

**PRDs (Product Requirements Documents)**
- What PRDs are and why they exist
- How Claude reads PRDs to understand what the game should do
- How the team's design decisions from Session 2 became the PRDs that guided all the code Claude wrote

**File and Folder Structure**
- How the quest-craft project is organized (game/, docs/, assets/, memory/)
- File types and what they mean: .py (code), .md (documentation), .json (data/level layouts)
- Why organization matters when working with AI -- Claude needs to find things fast

**AI Memory**
- How memory/MEMORY.md works as Claude's brain across sessions
- How memory/lessons.md captures repeated mistakes so Claude stops making them
- Why memory matters: without it, Claude starts every conversation from zero

**Context Windows**
- What a context window is -- the amount of text Claude can see at once
- How PRDs, memories, and code all compete for space in the context window
- Why loading the right information matters more than loading everything
- Trade-offs: more context = better answers, but there's a limit

**Sub-Agents and Parallel Processing**
- How to spawn sub-agents from a team leader agent
- Creating specialized agents focused on specific tasks (one for bugs, one for art, one for sound)
- The benefit of agents working independently and reporting back to a team leader
- Using a validator agent to check work before it merges
- Why this preserves the context window -- each agent only holds what it needs
- Parallel processing -- multiple agents working at the same time instead of one doing everything sequentially

**Diffs and Code Review**
- What a diff is -- showing exactly what changed between two versions of code
- Why diffs matter: you can see what Claude changed without reading the whole file
- How diffs prevent mistakes -- review small changes instead of trusting blindly

**Learning Logs**
- How lessons.md documents repeated issues across sessions
- Loading lessons into context at the start of each session
- Adding new lessons during sessions to improve future development

---

## Team Interviews -- Session 4 Reflections (March 15, 2026)

### Andrew (11) -- Artist & Visual Designer

**Favorite moment:** Finding bugs. Andrew gravitated toward the QA side -- discovering things that were broken and calling them out.

**Hardest part of reporting bugs:** Knowing the right words. The technical vocabulary to describe what went wrong didn't come naturally -- he had to learn to be specific about what he saw vs. what should have happened.

**Exhibition pitch -- How did you build this?:** We tested and fixed. Andrew sees the iterative loop as the core story -- play, find problems, fix, repeat.

**Sub-agents / parallel processing:** Would split 20 bugs across multiple agents working at the same time. Understands parallel processing makes things faster.

### Ethan (9) -- Co-creator & Game Designer

**Biggest surprise:** How many bugs there were. Didn't expect a game to need so much fixing after it was built.

**Context windows -- which file to load first?:** CLAUDE.md (the Constitution). Understands that the foundation document is the most important thing for Claude to read -- everything else builds on it.

**What's a diff?:** Shows what changed -- exactly which lines were added, removed, or modified.

**How is game dev different from expected?:** It takes a team. Ethan recognizes that nobody builds anything real alone -- everyone has a role to play.

### Eins (11) -- Co-creator & Game Designer

**Why lessons.md matters:** Without it, Claude repeats the same mistakes. Eins understands that AI has no memory between sessions unless you give it one.

**Why sub-agents are better:** All three reasons -- faster (parallel work), saves context window (each agent only knows its task), and better quality (specialists beat generalists). Strong conceptual grasp.

**Exhibition response to Did AI just make it for you?:** We designed, AI built. Every decision came from the team -- characters, levels, how it feels. AI wrote the code. Clear, honest, exhibition-ready answer.

**One thing he'll remember a year from now:** AI needs context. Without the right information loaded upfront, AI can't do good work. A deep insight that most adults working with AI haven't internalized yet.

---

## Key Themes Across All Three Interviews

1. **Communication is the skill** -- finding the right words to describe bugs, designs, and ideas is the hardest and most important part
2. **Iteration is the process** -- building is only half the job; testing and fixing is the other half
3. **AI is a tool, not a replacement** -- the team designed everything; AI was the engineer executing their vision
4. **Context matters** -- AI only works well when given the right information (CLAUDE.md, lessons, PRDs)
5. **Parallel processing works** -- splitting work across specialized agents is faster and better than one agent doing everything
