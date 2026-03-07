#!/bin/bash
# Quest Craft — Sunday Morning Startup
# Run this after powering on the Pi: bash ~/quest-craft/scripts/startup.sh

echo "=== Quest Craft Startup ==="
echo ""

# 1. Pull latest code
echo "[1/5] Pulling latest code..."
cd ~/quest-craft && git pull origin main
echo ""

# 2. Start headless display (skip if already running)
echo "[2/5] Starting headless display..."
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export WAYLAND_DISPLAY=wayland-0
if pgrep -x wayvnc > /dev/null; then
    echo "  wayvnc already running"
else
    wayvnc 0.0.0.0 5900 &>/dev/null &
    sleep 1
    echo "  wayvnc started on port 5900"
fi
if pgrep -f "websockify.*6080" > /dev/null; then
    echo "  noVNC already running"
else
    websockify --web /usr/share/novnc 6080 localhost:5900 &>/dev/null &
    sleep 1
    echo "  noVNC started on port 6080"
fi
echo ""

# 3. Reconnect Pro Controller (press SYNC if not auto-connected)
echo "[3/5] Checking Pro Controller..."
PROCTL="60:1A:C7:B7:72:9F"
if bluetoothctl info "$PROCTL" 2>/dev/null | grep -q "Connected: yes"; then
    echo "  Pro Controller connected!"
else
    echo "  Pro Controller not connected. Trying to reconnect..."
    bluetoothctl connect "$PROCTL" 2>/dev/null
    sleep 2
    if bluetoothctl info "$PROCTL" 2>/dev/null | grep -q "Connected: yes"; then
        echo "  Pro Controller reconnected!"
    else
        echo "  NOTE: Press SYNC button on controller, then run:"
        echo "    bluetoothctl connect 60:1A:C7:B7:72:9F"
        echo "  Or just plug in via USB-C cable."
    fi
fi
echo ""

# 4. Verify Pygame sees the controller
echo "[4/5] Verifying Pygame..."
python3 << 'PYEOF'
import pygame
pygame.init()
count = pygame.joystick.get_count()
print("  Pygame:", pygame.ver)
print("  Controllers:", count)
for i in range(count):
    j = pygame.joystick.Joystick(i)
    name = j.get_name()
    btns = j.get_numbuttons()
    axes = j.get_numaxes()
    print("    [%d] %s (%d buttons, %d axes)" % (i, name, btns, axes))
pygame.quit()
PYEOF
echo ""

# 5. Summary
echo "[5/5] Status check..."
echo "  Git: $(cd ~/quest-craft && git log --oneline -1)"
IP=$(hostname -I | awk '{print $1}')
echo "  VNC: http://${IP}:6080/vnc.html"
echo "  Tailscale: http://100.118.252.70:6080/vnc.html"
echo ""
echo "=== READY! ==="
echo ""
echo "Quick commands:"
echo "  python3 ~/quest-craft/game/spark.py            # Run the game"
echo "  python3 ~/quest-craft/game/test_controller.py   # Test controller"
echo "  cd ~/quest-craft && claude                      # Start Claude session"
