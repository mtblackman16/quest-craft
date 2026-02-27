# Quest Craft

A video game designed by kids, built with AI — on a Raspberry Pi 5.

## About

This game is being created by a team of young game designers (ages 9-11) for the **LASD Illuminate Inquiry Exhibition** on **March 15, 2026**.

The team uses an **AI-first approach**: they design the game through voice conversations with Claude (AI), while Claude handles the engineering. The kids are the creative directors. Claude is the engineer.

**Built with:**
- Python 3.13 + Pygame 2.6
- Raspberry Pi 5 + Nintendo Switch controllers
- Claude Code (AI engineering partner)
- Wispr Flow (voice-to-text)

## Team

- Ethan (9) — Co-creator & Game Designer
- Eins (11) — Co-creator & Game Designer
- Andrew (11) — Co-creator & Game Designer
- Nathan (9) — Co-creator & Game Designer

## Getting Started

1. See `docs/guides/prerequisites.md` for what to install
2. See `docs/onboarding/getting-started.md` for connecting to the Pi
3. See `docs/sessions/session-1-dream.md` for the first session guide

## Project Structure

```
quest-craft/
├── game/              # Game code (Python + Pygame)
├── assets/            # Images, sounds, fonts
├── docs/
│   ├── sessions/      # 5 session guides (Dream → Design → Blueprint → Build → Polish)
│   ├── guides/        # Prerequisites, voice prompting, exhibition checklist
│   ├── onboarding/    # Getting started, team info, how games work
│   ├── prds/          # Game design documents
│   ├── plans/         # Master plan
│   ├── learning/      # Learning logs, build records, research
│   └── reference/     # Tech stack, Python cheatsheet
└── memory/            # Project memory for Claude
```

## How to Run

```bash
cd /home/mark/quest-craft/game
python3 main.py
```

## Controls

*To be determined — see `docs/prds/07-controls.md`*

## License

This is a school project. Made with love and AI.
