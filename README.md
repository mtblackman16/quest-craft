# Quest Craft

A video game designed and built by kids — on a Raspberry Pi 5.

## About

This game is being created by a team of young game designers (ages 9-11) for the **LASD Illuminate Inquiry Exhibition** on **March 15, 2026**.

The kids are the creative directors — they design every aspect of the game, from characters and story to gameplay mechanics and art direction. They use AI tools to help with engineering, while they drive all creative decisions through voice-first collaboration.

**Built with:**
- Python 3.13 + Pygame 2.6
- Raspberry Pi 5 + Nintendo Switch controllers
- AI-assisted development
- Wispr Flow (voice-to-text)

## Team

- Ethan (9) — Co-creator & Game Designer
- Eins (11) — Co-creator & Game Designer
- Andrew (11) — Artist & Visual Designer
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

This is a school project. Made with love by Ethan, Eins, Andrew & Nathan.
