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

### Template:

```
### [What Went Wrong]
**Date:** [date]
**Who found it:** [name]
**What happened:** [description]
**How we fixed it:** [solution]
**How to prevent it:** [prevention]
```
