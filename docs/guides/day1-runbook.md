# Day 1 Runbook — The Dream Session

> Mark’s facilitator cheat sheet. Keep this open on your laptop and click through.

---

## Quick Reference

| Item | Value |
|------|-------|
| Pi IP | `100.118.252.70` (Tailscale) |
| Pi user / pass | `mark` / `quest2026` |
| VS Code host | `mark@100.118.252.70` → select **Linux** |
| Claude command | `cd ~/quest-craft && claude` |
| Tailscale auth key | See [local-credentials.md](../onboarding/local-credentials.md) |

---

## Pre-Session Checklist (30 min before)

- [ ] Pi powered on, HDMI display connected
- [ ] Verify Pi on Tailscale: `ssh mark@100.118.252.70`
- [ ] Switch Pro Controller paired via Bluetooth
- [ ] Pygame test: `python3 -c "import pygame; pygame.init(); print('OK')"`
- [ ] Each kid’s laptop: Tailscale connected, VS Code opens Pi
- [ ] Print [local-credentials.md](../onboarding/local-credentials.md)

---

## Agenda

### 1. Welcome & Setup (15 min)

1. Kids sit down, open laptops
2. Connect to **guest WiFi** (see printed credentials sheet)
3. Open **Tailscale** → should auto-connect (auth key pre-installed)
4. Open **VS Code** → Remote-SSH → type `mark@100.118.252.70` → password: `quest2026` → select **Linux**
5. Open terminal in VS Code → `cd ~/quest-craft && claude`
6. Reference: [Getting Started](../onboarding/getting-started.md)

### 2. The Dream — `/dream` (90 min)

1. One kid types: `/dream`
2. Claude guides the conversation through 10 creative phases
3. Mark facilitates — make sure **every kid** contributes
4. Reference: [Session 1 Guide](../sessions/session-1-dream.md)
5. Output: `docs/prds/00-game-concept.md`

**Facilitator tips:**
- If one kid dominates, ask the quiet ones directly: "What do YOU think the world should look like?"
- Let them disagree — Claude will help them find consensus
- Keep energy up: "This is YOUR game, every idea matters"

### 3. Break (10 min)

- Snacks, bathroom, stretch
- Let them talk about their game — excitement builds naturally

### 4. Showcase — `/showcase` (15 min)

1. Type: `/showcase`
2. Claude summarizes everything they created
3. Kids reflect on their favorite parts
4. "You just designed an entire game. But we’re not done yet..."

### 5. The Spark — `/spark` (15 min) ← THE BIG MOMENT

> Mark decides the timing. This is YOUR call.

1. Type: `/spark`
2. Claude narrates as it builds the demo (~5 min)
3. Run: `python3 game/spark.py`
4. Kid grabs Switch controller → plays THEIR game
5. Everyone gets a turn
6. Reference: [Spark details](../sessions/session-1-dream.md#the-spark-last-15-minutes)

**The moment:** Their eyes light up. Their character is on screen. THEY control it. This is why we’re here.

### 6. Parents Arrive (10 min)

1. Kids show parents the game running on screen
2. Show the concept doc: "We designed all of this"
3. Tease Session 2: "Next time we design the REAL version — enemies, levels, everything"

---

## Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| VS Code can’t connect | Check Tailscale is running on kid’s laptop, try password `quest2026` |
| "Connection refused" | Pi may need reboot: `ssh mark@100.118.252.70 "sudo reboot"`, wait 30s |
| Controller not working | Re-pair Bluetooth on Pi, restart `spark.py` |
| Claude not responding | Check internet on Pi, restart: `claude` |
| Kid’s Tailscale won’t connect | Re-enter auth key from credentials sheet |
| Spark crashes | Check terminal for error, re-run `python3 game/spark.py` |
| Claude auth error / "please login" | Verify API key: `echo $ANTHROPIC_API_KEY` — if empty, run `source ~/.bashrc` |

---

## Session Files Quick Links

| Document | Purpose |
|----------|---------|
| [Getting Started](../onboarding/getting-started.md) | Connection setup for kids |
| [Prerequisites](../guides/prerequisites.md) | What parents install beforehand |
| [Session 1 Guide](../sessions/session-1-dream.md) | Full dream session breakdown |
| [Master Plan](../plans/master-plan.md) | 5-session roadmap |
| [Local Credentials](../onboarding/local-credentials.md) | Passwords and IPs (print this) |

---

## Headless Display Setup

If the Pi is running headless (no monitor connected), you need to start VNC **before** the Spark demo so kids can see the game. See [headless-setup.md](headless-setup.md) for full instructions.

**Quick version:**

```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
wayvnc 0.0.0.0 5900 &>/dev/null &
websockify --web /usr/share/novnc 6080 localhost:5900 &>/dev/null &
```

Then open a browser on any device and go to `http://<PI_IP>:6080/vnc.html`

> **Tip:** Do this as part of session prep (Pre-Session Checklist), not scrambling during the Spark moment.

---

## Parent Summary Distribution

After the session, the parent summary HTML is auto-hosted via GitHub Pages. To publish:

1. Push the HTML file to `docs/parent-summaries/` on the `main` branch
2. Share the link with parents: `https://mtblackman16.github.io/quest-craft/parent-summaries/session-N-name.html`

GitHub Pages serves from the `docs/` folder, so any HTML pushed there is live within a few minutes.
