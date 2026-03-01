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

### Template:

```
### [What Went Wrong]
**Date:** [date]
**Who found it:** [name]
**What happened:** [description]
**How we fixed it:** [solution]
**How to prevent it:** [prevention]
```
