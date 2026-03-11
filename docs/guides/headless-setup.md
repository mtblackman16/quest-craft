# Headless Pi Setup — Remote Game Display

> Run and view Pygame games on the Pi without a monitor. Open this guide at the start of any session where you don't have an HDMI display connected.

---

## Quick Reference

| Item | Value |
|------|-------|
| Pi local IP | `192.168.1.230` |
| Pi Tailscale IP | `100.118.252.70` |
| SSH user | `mark` |
| VNC port | `5900` |
| noVNC (browser) port | `6080` |
| Browser URL (local) | `http://192.168.1.230:6080/vnc.html` |
| Browser URL (Tailscale) | `http://100.118.252.70:6080/vnc.html` |

---

## How It Works

The Pi runs a **Wayland desktop** (labwc compositor) even when no monitor is plugged in. Three pieces work together to let you see and interact with Pygame games remotely:

1. **labwc** — The Wayland compositor. It manages the desktop and windows on the Pi.
2. **wayvnc** — Exposes the Wayland desktop as a VNC stream on port 5900.
3. **noVNC + websockify** — Wraps the VNC stream in a browser-friendly WebSocket so you can view it from any device with a web browser. Runs on port 6080.

**The flow:** Pygame draws to the Wayland display → wayvnc captures it → noVNC serves it to your browser.

---

## One-Time Setup (Already Done)

These packages are already installed on the Pi. You don't need to run this unless you're setting up a fresh Pi.

```bash
sudo apt-get install -y novnc wayvnc
```

---

## Start the Remote Display (Every Session)

Run these commands on the Pi via SSH before launching a game.

### Step 1 — Start wayvnc

```bash
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/$(id -u)
wayvnc --render-cursor 0.0.0.0 5900 &
```

This starts the VNC server, listening on all interfaces on port 5900. The `--render-cursor` flag ensures the mouse cursor is visible in the VNC stream.

### Step 2 — Start noVNC (browser bridge)

```bash
websockify --web /usr/share/novnc 6080 localhost:5900 &
```

This bridges VNC (port 5900) to a WebSocket (port 6080) and serves the noVNC web client.

### Step 3 — Launch your game

```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export WAYLAND_DISPLAY=wayland-0
python3 /home/mark/quest-craft/game/spark.py
```

The game runs on the Pi's Wayland display. You'll see it in your browser.

### Or: Use the script

```bash
/home/mark/quest-craft/scripts/start-vnc.sh
```

This starts both wayvnc and noVNC in one step. See [scripts/start-vnc.sh](../../scripts/start-vnc.sh).

---

## Connect from Windows

1. Open Chrome (or Edge, or Firefox)
2. Go to:
   ```
   http://192.168.1.230:6080/vnc.html
   ```
3. Click **Connect**
4. Done. You should see the Pi's desktop and your game.

If you're connecting over **Tailscale** from outside the local network:
```
http://100.118.252.70:6080/vnc.html
```

---

## Connect from macOS

### Option A — Browser (same as Windows)

Open any browser and go to:
```
http://192.168.1.230:6080/vnc.html
```

### Option B — Built-in VNC viewer (no install needed)

1. In Finder, press **Cmd+K** (or Go → Connect to Server)
2. Type: `vnc://192.168.1.230:5900`
3. Click **Connect**

The native macOS VNC viewer gives a slightly smoother experience than the browser.

---

## Connect from iPhone / iPad / Android

The same browser URL works on mobile devices:
```
http://192.168.1.230:6080/vnc.html
```

Open it in Safari, Chrome, or any mobile browser. Tap **Connect**. The game display will appear and you can interact with it via touch.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Connection refused" on port 5900 | wayvnc isn't running. Start it (Step 1 above). |
| "Connection refused" on port 6080 | websockify/noVNC isn't running. Start it (Step 2 above). |
| Black screen in VNC | The Wayland compositor may not have a virtual display. Try: `export WLR_BACKENDS=headless` before starting labwc. |
| Game doesn't appear in VNC | Make sure `WAYLAND_DISPLAY=wayland-0` is set before launching the game. Check with `ls /run/user/1000/wayland-*` to confirm. |
| Laggy or slow display | You're likely on WiFi. Try ethernet or a Tailscale direct connection for better performance. |
| Need to kill VNC and start over | `pkill wayvnc && pkill websockify` |

---

## Quick Copy-Paste Block

Paste this entire block into an SSH session to start everything at once:

```bash
/home/mark/quest-craft/scripts/start-vnc.sh
```

Or manually:

```bash
# Start remote display access
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/$(id -u)
pkill wayvnc 2>/dev/null; pkill websockify 2>/dev/null
sleep 0.5
wayvnc --render-cursor 0.0.0.0 5900 &>/dev/null &
websockify --web /usr/share/novnc 6080 localhost:5900 &>/dev/null &
echo "Browser: http://$(hostname -I | awk '{print $1}'):6080/vnc.html"
```

Then launch your game in a separate terminal:

```bash
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export WAYLAND_DISPLAY=wayland-0
python3 /home/mark/quest-craft/game/spark.py
```
