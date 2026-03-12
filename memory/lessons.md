# Lessons Learned

> Record mistakes, bugs, and how we fixed them.
> This helps us avoid making the same mistake twice.

---

## Lessons

## Headless Pi Display (Feb 28, 2026)
**Problem:** Pi was set up headless (no monitor). Kids couldn't see the Spark demo.
**Solution:** wayvnc + noVNC. wayvnc exposes the Wayland desktop over VNC, websockify/noVNC wraps it for browser access.
**Key commands:**
- `wayvnc 0.0.0.0 5900 &` — start VNC server
- `websockify --web /usr/share/novnc 6080 localhost:5900 &` — start browser bridge
- Browser: `http://<ip>:6080/vnc.html`
**Lesson:** Always have the headless display ready BEFORE the Spark moment. Set up VNC as part of session prep, not scrambling during the demo.

---

## GitHub Pages Images Broken — raw.githubusercontent.com (Mar 8, 2026)
**Problem:** All 4 images in `docs/parent-summaries/session-2-design.html` failed to load on GitHub Pages. The `<img>` tags used `https://raw.githubusercontent.com/...` URLs pointing to files in the `assets/` directory.
**Root cause:** GitHub rate-limits `raw.githubusercontent.com`. When a page loads multiple images simultaneously from that domain, it can trigger HTTP 429 (Too Many Requests) errors, causing broken images. The URLs work individually (HTTP 200) but fail when loaded together in a browser.
**Solution:** Copied the images into a subdirectory under `docs/` (which GitHub Pages serves directly) and changed all `<img src>` attributes to use relative paths:
- `src="images/player/jello-cube-three-quarter.png"` instead of the raw GitHub URL
- Images now served from `mtblackman16.github.io` domain with no rate limiting
**File structure:**
```
docs/parent-summaries/
  session-2-design.html
  images/
    player/jello-cube-three-quarter.png
    enemies/sanitizer-warrior-front-view.png
    team-photos/session-2-controller-mapping-2026-03-08.jpg
    team-photos/session-2-beastmode-break-2026-03-08.jpg
```
**Rule for future HTML pages:** NEVER use `raw.githubusercontent.com` URLs for images in GitHub Pages HTML. Always copy images into the `docs/` tree and use relative paths. GitHub Pages serves files from `docs/` on the `github.io` domain with no rate limiting or CSP issues.

---

## wayvnc Crashes When Fullscreen Game Exits (Mar 11, 2026)
**Problem:** Killing a fullscreen Pygame game (`pygame.FULLSCREEN`) causes the HDMI output to momentarily disappear. wayvnc sees "Output HDMI-A-1 went away", finds no fallback outputs, and exits with a fatal error.
**Solution:** After killing a fullscreen game, always restart wayvnc before trying to connect via VNC:
```bash
# Kill old VNC processes
kill $(pgrep wayvnc) $(pgrep websockify) 2>/dev/null
sleep 1
# Restart both
export WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000
wayvnc 0.0.0.0 5900 &
sleep 2
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &
```
**Lesson:** Start VNC BEFORE launching the game, and expect to restart wayvnc if the game is force-killed. A graceful game exit (ESC/quit) may avoid the HDMI glitch.

---

## Duplicate Game Instances Cause Controller Issues (Mar 11, 2026)
**Problem:** Two instances of `python3 -m game.main` were running simultaneously. The Pro Controller was "connected" (showed up in `/proc/bus/input/devices`) but wasn't functioning in-game — likely because both processes were competing for joystick input via Pygame.
**Solution:** Always check for and kill existing instances before launching:
```bash
# Check for running instances
ps aux | grep "game.main" | grep -v grep
# Kill all instances
pkill -9 -f "game.main"
sleep 1
# Then launch ONE instance
cd /home/mark/quest-craft
WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 python3 -m game.main &
```
**Lesson:** Before debugging controller issues, first check `ps aux | grep game.main`. Multiple instances = the likely culprit. Only one game process should ever be running. Use `kill -9` (not plain `kill`) since fullscreen Pygame may not respond to SIGTERM.

---

## Recommended Startup Order (Mar 11, 2026)
When setting up the Game Pi for a session:
1. Kill any existing game instances: `pkill -9 -f "game.main" 2>/dev/null`
2. Start wayvnc: `WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 wayvnc 0.0.0.0 5900 &`
3. Start noVNC: `websockify --web=/usr/share/novnc/ 6080 localhost:5900 &`
4. Verify VNC works in browser: `http://192.168.1.230:6080/vnc.html`
5. Launch game (single instance): `cd /home/mark/quest-craft && WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 python3 -m game.main &`

---

### Template:

```
### [What Went Wrong]
**Date:** [date]
**Who found it:** [name]
**What happened:** [description]
**How we fixed it:** [solution]
**How to prevent it:** [prevention]
```
