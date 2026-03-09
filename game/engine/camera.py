"""
Camera system — follow player, look-ahead, shake, right-stick shift, bounds, death zoom.
"""
import random
from game.engine.settings import SCREEN_W, SCREEN_H, STICK_DEADZONE


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        # Smoothing
        self.lerp_speed = 0.08
        # Look-ahead
        self.look_ahead_x = 0.0
        self.look_ahead_amount = 60
        # Right-stick shift
        self.stick_shift_x = 0.0
        self.stick_shift_y = 0.0
        self.stick_shift_max = 80
        # Screen shake
        self.shake_amount = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
        # Death zoom (unused for now, placeholder)
        self.zoom = 1.0
        # Bounds
        self.bounds_left = 0
        self.bounds_right = SCREEN_W
        self.bounds_top = 0
        self.bounds_bottom = SCREEN_H

    def set_bounds(self, left, top, right, bottom):
        self.bounds_left = left
        self.bounds_top = top
        self.bounds_right = right
        self.bounds_bottom = bottom

    def update(self, player_x, player_y, player_facing, joystick=None):
        # Look-ahead in movement direction
        target_look = player_facing * self.look_ahead_amount
        self.look_ahead_x += (target_look - self.look_ahead_x) * 0.05

        # Right-stick camera shift
        if joystick:
            try:
                rx = joystick.get_axis(2)
                ry = joystick.get_axis(3)
                if abs(rx) > STICK_DEADZONE:
                    self.stick_shift_x = rx * self.stick_shift_max
                else:
                    self.stick_shift_x *= 0.85
                if abs(ry) > STICK_DEADZONE:
                    self.stick_shift_y = ry * self.stick_shift_max
                else:
                    self.stick_shift_y *= 0.85
            except Exception:
                self.stick_shift_x *= 0.85
                self.stick_shift_y *= 0.85
        else:
            self.stick_shift_x *= 0.85
            self.stick_shift_y *= 0.85

        # Target position: center player on screen
        self.target_x = player_x - SCREEN_W // 2 + self.look_ahead_x + self.stick_shift_x
        self.target_y = player_y - SCREEN_H // 2 + 80 + self.stick_shift_y  # offset down a bit

        # Smooth follow
        self.x += (self.target_x - self.x) * self.lerp_speed
        self.y += (self.target_y - self.y) * self.lerp_speed

        # Clamp to bounds
        self.x = max(self.bounds_left, min(self.x, self.bounds_right - SCREEN_W))
        self.y = max(self.bounds_top, min(self.y, self.bounds_bottom - SCREEN_H))

        # Screen shake decay
        if self.shake_amount > 0:
            self.shake_offset_x = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_offset_y = random.uniform(-self.shake_amount, self.shake_amount)
            self.shake_amount *= 0.85
            if self.shake_amount < 0.5:
                self.shake_amount = 0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

    def shake(self, amount):
        """Trigger screen shake. Micro=1-2, medium=3-5, heavy=6-10."""
        self.shake_amount = max(self.shake_amount, amount)

    def get_offset(self):
        """Return (offset_x, offset_y) for drawing world objects."""
        return (
            -int(self.x + self.shake_offset_x),
            -int(self.y + self.shake_offset_y),
        )

    def reset(self, player_x, player_y):
        """Snap camera to player position (no lerp)."""
        self.x = player_x - SCREEN_W // 2
        self.y = player_y - SCREEN_H // 2 + 80
        self.target_x = self.x
        self.target_y = self.y
        self.shake_amount = 0
