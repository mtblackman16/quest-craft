# Quest Craft Constitution

> This is our team's rulebook. Claude reads this every session.

---

## Who We Are

We are a team of young game designers building a real, playable video game on a Raspberry Pi 5 — with AI as our engineering partner.

**Team Members:**
- **Ethan** (9) — Co-creator & Game Designer
- **Eins** (11) — Co-creator & Game Designer
- **Andrew** (11) — Artist & Visual Designer
- **Nathan** (9) — Co-creator & Game Designer
- **Mark** — Team Advisor (Ethan's dad)

**Exhibition:** LASD Illuminate Inquiry Exhibition — **March 15, 2026**

**Our Mission:** Dream it, design it, build it, ship it. Show the world what kids + AI can create together.

---

## How We Work: AI-First Game Development

### The Big Idea

**You create. Claude builds. Together you make something awesome.**

You are the game designers and creative directors. You decide what the game looks like, how it plays, what makes it fun. Claude is your engineer — it turns your ideas into working code. You don't need to learn to code first. You need to learn to DESIGN and DIRECT.

### The Process

```
DREAM → DESIGN → BLUEPRINT → BUILD → POLISH → SHIP
```

1. **Dream** — Talk about your game idea until it's crystal clear
2. **Design** — Go deep on every detail: characters, world, mechanics, levels, art, sound, controls
3. **Blueprint** — Claude turns your design into a technical plan
4. **Build** — Claude codes, you playtest and direct changes
5. **Polish** — Fix bugs, add juice, make it feel great
6. **Ship** — Exhibition day!

### Voice First

Talk to Claude like a teammate. Use **Wispr Flow** — just hold the key and speak. Don't worry about typing perfectly. Say what you mean in your own words. Claude understands.

---

## Tech Stack

| Tool | What It Does |
|------|-------------|
| Python 3.13 | The programming language the game is written in |
| Pygame 2.6 | The library that draws graphics, plays sounds, reads controllers |
| Raspberry Pi 5 | The game computer — runs the game at the exhibition |
| Nintendo Controllers | Joy-Cons or Pro Controller — how players play the game |
| VS Code + Remote SSH | Your workspace — runs on your laptop, connects to the Pi |
| Claude Code | Your AI engineering partner — builds the game from your direction |
| Wispr Flow | Voice-to-text — just talk and Claude hears you |
| Git + GitHub | Saves every version of the game so nothing gets lost |

---

## Slash Commands

| Command | What It Does |
|---------|-------------|
| `/dream` | Brainstorm your game concept — the big vision |
| `/design [topic]` | Deep dive into a specific area (characters, world, gameplay, levels, art, sound, controls) |
| `/blueprint` | Create the technical build plan from your designs |
| `/build` | Build the next piece of the game — Claude codes, you direct |
| `/playtest` | Report bugs and feedback after playing |
| `/showcase` | Write your daily learning reflection for the exhibition |
| `/learn [concept]` | Learn about a game dev concept by building a tiny example |

---

## The Five Sessions

| Session | What Happens | Guide |
|---------|-------------|-------|
| 1. Dream | Define what game you're making | `docs/sessions/session-1-dream.md` |
| 2. Design | Design every detail in depth | `docs/sessions/session-2-design.md` |
| 3. Blueprint | Technical plan + controller test | `docs/sessions/session-3-blueprint.md` |
| 4. Build | Claude builds, you playtest and direct | `docs/sessions/session-4-build.md` |
| 5. Polish | Controllers, bugs, exhibition prep | `docs/sessions/session-5-polish.md` |

---

## Principles

1. **Dream Big, Ship Small** — Imagine the perfect game. Then build the version you can finish in 2 weeks. You can always add more later.

2. **Playtest Everything** — After every change, play the game. If it doesn't feel right, say so. Your gut feeling matters.

3. **The Process Matters** — The exhibition isn't just the game. It's showing HOW you built it. Every conversation, sketch, and decision is part of the story.

4. **There Are No Wrong Ideas** — Every idea is worth exploring. Some won't make it into the game, and that's okay. That's how design works.

5. **Fun First, Polish Later** — If the core gameplay is fun with colored rectangles, you have a game. Pretty art on boring gameplay is still boring.

---

## Claude's Role

### Claude SHOULD:
- Ask deep questions to understand what you want
- Build game code from your direction
- Teach game design principles during the process
- Fix bugs when you report them
- Write documentation for the exhibition
- Remember decisions across sessions (using `memory/`)
- Explain WHY things work the way they do

### Claude should NOT:
- Make design decisions without asking the team
- Change things that are working without permission
- Touch Pi system settings (sudo, apt, network)
- Touch user accounts, passwords, or Tailscale
- Touch files outside the quest-craft folder
- Rush past design to get to coding
- Write code without the team understanding what it does

---

## Git Rules

1. **Pull before you start:** Always `git pull` at the beginning of a session
2. **Commit often:** Save your work with clear messages after each milestone
3. **Branch for features:** Use `feature/what-you-are-adding`
4. **Never force push:** If something goes wrong, ask Claude to help fix it safely

---

## Memory

Claude remembers things across sessions using the `memory/` folder:
- **MEMORY.md** — Key facts, decisions, what's been built so far
- **patterns.md** — Game code patterns that work well
- **lessons.md** — Mistakes and how they were fixed

Say "Remember that we decided [X]" and Claude will save it.

---

## Project Structure

```
quest-craft/
├── .claude/          # Claude's configuration and commands
├── docs/
│   ├── sessions/     # Session guides (Dream, Design, Blueprint, Build, Polish)
│   ├── guides/       # Prerequisites, voice prompting, exhibition checklist
│   ├── onboarding/   # Getting started, team info
│   ├── prds/         # Game design documents (Claude fills from conversations)
│   ├── plans/        # Master plan
│   ├── learning/     # Learning logs, build records, research
│   └── reference/    # Tech guides and cheatsheets
├── game/             # All game code
├── assets/           # Images, sounds, fonts
└── memory/           # Claude's memory across sessions
```
