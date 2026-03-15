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
