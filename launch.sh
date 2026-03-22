#!/bin/bash
# Launch SPLIT with correct display + audio environment
export WAYLAND_DISPLAY=wayland-0
export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export SDL_VIDEODRIVER=wayland
export SDL_AUDIODRIVER=pipewire

cd /home/mark/quest-craft
exec python3 -m game.main "$@"
