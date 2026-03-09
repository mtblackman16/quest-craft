#!/bin/bash
# Quest Craft — Exhibition Day Launch Script
# Sets display to 720p, configures audio, launches game with auto-restart.
# Usage: bash ~/quest-craft/scripts/exhibition.sh

set -e

GAME_DIR="$HOME/quest-craft"
RESTART_DELAY=2
MAX_CRASHES=50  # safety limit

echo "=== SPLIT — Exhibition Mode ==="
echo ""

# ── Display: force 720p for 60fps ──
echo "[1/4] Setting display to 720p..."
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/$(id -u)
export DISPLAY=:0

if command -v wlr-randr &>/dev/null; then
    wlr-randr --output HDMI-A-1 --mode 1280x720@60 2>/dev/null && \
        echo "  Display set to 1280x720@60Hz" || \
        echo "  WARN: Could not set 720p (may already be set or not HDMI)"
else
    echo "  WARN: wlr-randr not found, display resolution unchanged"
fi
echo ""

# ── Audio: force ALSA to avoid PipeWire dummy output ──
echo "[2/4] Configuring audio..."
export SDL_AUDIODRIVER=alsa
export AUDIODEV=plughw:0
echo "  SDL_AUDIODRIVER=alsa  AUDIODEV=plughw:0"
echo ""

# ── Controller check ──
echo "[3/4] Checking controller..."
python3 -c "
import pygame
pygame.init()
count = pygame.joystick.get_count()
if count > 0:
    j = pygame.joystick.Joystick(0)
    print(f'  Controller: {j.get_name()} ({j.get_numbuttons()} buttons)')
else:
    print('  WARNING: No controller detected! Plug in or pair via Bluetooth.')
pygame.quit()
" 2>/dev/null || echo "  Could not check controller"
echo ""

# ── Launch game in restart loop ──
echo "[4/4] Launching SPLIT..."
echo "  Press Ctrl+C to stop."
echo ""

crash_count=0
while [ $crash_count -lt $MAX_CRASHES ]; do
    cd "$GAME_DIR"
    python3 -m game.main
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo ""
        echo "Game exited cleanly."
        break
    fi

    crash_count=$((crash_count + 1))
    echo ""
    echo "=== Game crashed (exit $exit_code) — restart #$crash_count in ${RESTART_DELAY}s ==="
    echo ""
    sleep $RESTART_DELAY
done

if [ $crash_count -ge $MAX_CRASHES ]; then
    echo "FATAL: Game crashed $MAX_CRASHES times. Stopping."
    exit 1
fi
