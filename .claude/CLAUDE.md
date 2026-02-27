# Quest Craft Constitution

> This is our team's rulebook. Claude reads this every session.

---

## Who We Are

We are a team of young game developers building a real, playable video game on a Raspberry Pi 5.

**Team Members:**
- **Ethan** (9) — Co-creator
- **Eins** (11) — Co-creator
- **Andrew** (11) — Co-creator
- **Nathan** (9) — Co-creator
- **Mark** — Team advisor (Ethan's dad)

**Exhibition:** LASD Illuminate Inquiry Exhibition — **March 15, 2026**

**Our Mission:** Design, build, and ship a game we're proud to show at the exhibition.

---

## Tech Stack

| Tool | What It Does |
|------|-------------|
| Python 3.13 | The programming language we write our game in |
| Pygame 2.6 | The library that draws graphics, plays sounds, reads controllers |
| Raspberry Pi 5 | Our game computer — it runs the game at the exhibition |
| Nintendo Controllers | Joy-Cons or Pro Controller — how players play the game |
| VS Code + Remote SSH | Our code editor — runs on your laptop, edits code on the Pi |
| Claude Code | Our AI coding partner — helps us write code, fix bugs, learn |
| Wispr Flow | Lets you talk to Claude with your voice instead of typing |
| Git + GitHub | Saves every version of our code so nothing gets lost |

---

## The Golden Rule

### PRDs First, Then Code. No Exceptions.

A **PRD** (Product Requirements Document) is a plan that describes what we're building BEFORE we build it.

**The workflow:**
1. Brainstorm the idea
2. Write a PRD (use `/design-prd`)
3. Review the PRD (use `/review-prd`)
4. Get it approved by the team
5. THEN start coding (use `/start-coding`)

Why? Because building without a plan means tearing things apart and starting over. A 30-minute PRD saves hours of confusion.

---

## Team Roles (Rotate Weekly)

| Role | What You Do |
|------|------------|
| **Producer / QA** | Keeps the team on track. Tests the game. Files bugs. |
| **Gameplay Engineer** | Writes the core game code. Makes things move and interact. |
| **Art & UX Lead** | Designs how the game looks and feels. Creates sprites and UI. |

Everyone codes. Everyone contributes ideas. Roles just mean who LEADS that area for the week.

---

## How to Use Claude

### Slash Commands (type these in Claude Code)
| Command | What It Does |
|---------|-------------|
| `/brainstorm` | Start a creative brainstorming session |
| `/design-prd` | Create a new PRD with Claude's help |
| `/review-prd` | Have Claude review a PRD for completeness |
| `/start-coding` | Start coding (Claude checks PRDs are approved first) |
| `/learn` | Learn a new concept with simple examples |
| `/log-today` | Write your daily learning log |

### Tips for Talking to Claude
- **Be specific:** "Make the player jump higher" is better than "fix the jumping"
- **Ask why:** "Why does this code work?" helps you learn
- **Say what you see:** "The player goes through walls" helps Claude find the bug
- **Use voice:** Wispr Flow lets you just talk — no typing needed

---

## Boundaries

### Claude CAN help with:
- Writing game code (Python / Pygame)
- Creating and editing art assets
- Writing and reviewing PRDs
- Explaining how code works
- Fixing bugs
- Git commits and branches

### Claude should NOT touch:
- Pi system settings (sudo, apt, network config)
- User accounts or passwords
- Tailscale or security settings
- Files outside the quest-craft folder
- Anything Mark hasn't approved

---

## Git Rules

1. **Never push directly to `main`** — always use a branch
2. **Branch names:** `feature/what-you-are-adding` (e.g., `feature/player-jump`)
3. **Commit messages:** Say WHAT changed and WHY (e.g., "Add player jump — holds A button to jump higher")
4. **Pull before you push:** Always `git pull` before starting work
5. **Ask Claude for help:** `/commit` will help you write good commit messages

---

## Memory

Claude remembers things across sessions using the `memory/` folder:
- **MEMORY.md** — Key facts, decisions, team preferences
- **patterns.md** — Code patterns that work well in our game
- **lessons.md** — Mistakes we made and how we fixed them

If you want Claude to remember something, just say: "Remember that we decided to use top-down view."

---

## Schedule

| Week | Focus |
|------|-------|
| Week 1 (Days 1-4) | Team formation, brainstorming, PRDs for concept/characters/story/gameplay |
| Week 2 (Days 5-9) | Finish all PRDs, learn Python basics, first game window + controller input |
| Week 3 (Days 10-14) | Build the game — core mechanics, art, sound, levels |
| Week 4 (Days 15-17) | Polish, bug fixes, exhibition prep |

---

## Project Structure

```
quest-craft/
├── .claude/          # Claude's configuration (don't edit manually)
├── docs/
│   ├── onboarding/   # Getting started guides
│   ├── prds/         # Product Requirements Documents
│   ├── plans/        # Master plan and weekly goals
│   ├── learning/     # Learning logs and build records
│   └── reference/    # Tech guides and cheatsheets
├── game/             # All game code goes here
├── assets/           # Images, sounds, fonts
└── memory/           # Claude's memory across sessions
```
