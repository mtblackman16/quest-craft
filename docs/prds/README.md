# PRD Index — Quest Craft

## What's a PRD?

A **Product Requirements Document** describes what we're building BEFORE we build it. Every feature gets a PRD. No PRD = no coding.

## Status Key

| Status | Meaning |
|--------|---------|
| **Draft** | Being written — not ready yet |
| **Review** | Written, needs team review |
| **Approved** | Reviewed and ready to build! |

---

## PRD Tracker

| # | PRD | Status | Author | Last Updated |
|---|-----|--------|--------|-------------|
| 00 | [Game Concept](00-game-concept.md) | Draft | — | — |
| 01 | [Characters](01-characters.md) | Draft | — | — |
| 02 | [Story & World](02-story-world.md) | Draft | — | — |
| 03 | [Gameplay](03-gameplay.md) | Draft | — | — |
| 04 | [Levels](04-levels.md) | Draft | — | — |
| 05 | [Art Style](05-art-style.md) | Draft | — | — |
| 06 | [Sound](06-sound.md) | Draft | — | — |
| 07 | [Controls](07-controls.md) | Draft | — | — |

---

## How to Write a PRD

1. Run `/design-prd` in Claude Code
2. Claude will ask you questions one at a time
3. Answer honestly — there are no wrong answers
4. Claude saves the PRD when you're done
5. Run `/review-prd` to check it

## How to Get a PRD Approved

1. Status must be `Review`
2. Run `/review-prd` — Claude checks for gaps
3. Fix any issues Claude finds
4. When Claude says `APPROVED`, the status changes
5. Now you can code that feature!
