#!/bin/bash
# SPLIT game launcher - optimized for RPi5
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/run/user/1000
cd /home/mark/quest-craft
exec python3 -m game.main
