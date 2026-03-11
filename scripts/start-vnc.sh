#!/usr/bin/env bash
# Start VNC + noVNC for remote access to the Pi's Wayland desktop.
# After running, connect via browser: http://<pi-ip>:6080/vnc.html
#
# Usage:
#   ./scripts/start-vnc.sh          # start VNC + noVNC
#   ./scripts/start-vnc.sh stop     # kill both services

set -euo pipefail

export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

VNC_PORT=5900
NOVNC_PORT=6080
NOVNC_WEB="/usr/share/novnc"

stop_services() {
    pkill wayvnc 2>/dev/null && echo "Stopped wayvnc" || true
    pkill -f "websockify.*${NOVNC_PORT}" 2>/dev/null && echo "Stopped websockify" || true
}

if [[ "${1:-}" == "stop" ]]; then
    stop_services
    exit 0
fi

# Clean up any existing instances
stop_services
sleep 0.5

# Verify wayland socket exists
if [[ ! -S "${XDG_RUNTIME_DIR}/${WAYLAND_DISPLAY}" ]]; then
    echo "ERROR: Wayland socket not found at ${XDG_RUNTIME_DIR}/${WAYLAND_DISPLAY}"
    echo "Available sockets:"
    ls "${XDG_RUNTIME_DIR}"/wayland-* 2>/dev/null || echo "  (none)"
    exit 1
fi

# Start wayvnc
wayvnc --render-cursor 0.0.0.0 "${VNC_PORT}" &>/tmp/wayvnc.log &
WAYVNC_PID=$!
sleep 1

if ! kill -0 "${WAYVNC_PID}" 2>/dev/null; then
    echo "ERROR: wayvnc failed to start. Log:"
    cat /tmp/wayvnc.log
    exit 1
fi
echo "wayvnc running (PID ${WAYVNC_PID}) on port ${VNC_PORT}"

# Start noVNC websocket bridge
websockify --web "${NOVNC_WEB}" "${NOVNC_PORT}" localhost:"${VNC_PORT}" &>/tmp/novnc.log &
NOVNC_PID=$!
sleep 1

if ! kill -0 "${NOVNC_PID}" 2>/dev/null; then
    echo "ERROR: websockify failed to start. Log:"
    cat /tmp/novnc.log
    exit 1
fi
echo "noVNC running (PID ${NOVNC_PID}) on port ${NOVNC_PORT}"

PI_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "Connect via browser:"
echo "  Local:     http://${PI_IP}:${NOVNC_PORT}/vnc.html"
echo "  Tailscale: http://100.118.252.70:${NOVNC_PORT}/vnc.html"
echo ""
echo "To stop: $0 stop"
