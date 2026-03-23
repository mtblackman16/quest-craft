"""
SPLIT — Platform Classes
All platform types: solid, moving, crumbling, elevator.
Each platform knows how to update itself and draw with camera offset.
"""
import math
import random
import pygame
from game.engine.settings import (
    PlatformType, Difficulty, DIFFICULTY_SETTINGS,
    SCREEN_W, SCREEN_H, FLOOR_PALETTES, TILE_SIZE,
)

__all__ = [
    "Platform", "SolidPlatform", "MovingPlatform",
    "CrumblingPlatform", "ElevatorPlatform",
]


# ── Crumbling platform states ──
CRUMBLE_STABLE = 0
CRUMBLE_SHAKING = 1
CRUMBLE_BROKEN = 2
CRUMBLE_RESPAWNING = 3

SHAKE_DURATION = 30         # frames before it breaks
RESPAWN_DURATION = 180      # frames before it comes back


# ──────────────────────────────────────────────
#  Base Platform
# ──────────────────────────────────────────────
class Platform:
    """Base class for every platform in the game."""

    def __init__(self, x, y, w, h, platform_type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.platform_type = platform_type
        self.floor_num = 1          # set by LevelManager after creation
        self.visible = True         # can be set False for invisible collision walls

    # ── helpers ──
    def get_rect(self):
        """Return a pygame.Rect for collision checks."""
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def collides(self, rect):
        """True when *rect* overlaps this platform."""
        return self.get_rect().colliderect(rect)

    # ── palette shortcut ──
    def _palette(self):
        return FLOOR_PALETTES.get(self.floor_num, FLOOR_PALETTES[1])

    # ── interface (override in subclasses) ──
    def update(self, dt=1):
        pass

    def draw(self, surf, camera_offset):
        """Default draw — subclasses override for visuals."""
        ox, oy = camera_offset
        screen_x = self.x + ox
        screen_y = self.y + oy

        # Off-screen culling: skip if completely outside the viewport
        if (screen_x + self.w < 0 or screen_x > SCREEN_W
                or screen_y + self.h < 0 or screen_y > SCREEN_H):
            return

        rect = pygame.Rect(int(screen_x), int(screen_y), self.w, self.h)
        pygame.draw.rect(surf, (80, 80, 80), rect)


# ──────────────────────────────────────────────
#  Solid Platform  — static, always visible
# ──────────────────────────────────────────────
class SolidPlatform(Platform):
    """Static stone platform. The bread and butter of every floor."""

    def __init__(self, x, y, w, h, visible=True):
        super().__init__(x, y, w, h, PlatformType.SOLID)
        self.visible = visible
        self._cached_surf = None
        self._cached_floor = -1

    def _build_cache(self):
        """Pre-render the platform to a cached surface."""
        deep, warm, floor_c, accent = self._palette()
        self._cached_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        s = self._cached_surf

        # Main body — dark stone
        pygame.draw.rect(s, deep, (0, 0, self.w, self.h))

        # Top-edge highlight
        pygame.draw.rect(s, warm, (0, 0, self.w, min(2, self.h)))

        # Moss patches
        moss_color = (45, 80, 40)
        rng = random.Random(int(self.x * 7 + self.y * 13))
        moss_count = max(1, self.w // 80)
        for _ in range(moss_count):
            mx = rng.randint(0, max(0, self.w - 12))
            mw = rng.randint(6, 14)
            pygame.draw.rect(s, moss_color, (mx, 0, mw, 2))

        # Stone-block lines
        if self.h >= 8:
            groove_color = (max(deep[0] - 8, 0),
                            max(deep[1] - 8, 0),
                            max(deep[2] - 8, 0))
            start_x = TILE_SIZE - (int(self.x) % TILE_SIZE)
            gx = start_x
            while gx < self.w:
                pygame.draw.line(s, groove_color, (gx, 2), (gx, self.h - 1))
                gx += TILE_SIZE
        self._cached_floor = self.floor_num

    def draw(self, surf, camera_offset):
        if not self.visible:
            return
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy

        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        if self._cached_surf is None or self._cached_floor != self.floor_num:
            self._build_cache()

        surf.blit(self._cached_surf, (int(sx), int(sy)))


# ──────────────────────────────────────────────
#  Moving Platform
# ──────────────────────────────────────────────
class MovingPlatform(Platform):
    """Moves between a list of path points, then bounces back."""

    def __init__(self, x, y, w, h, path_points, speed=1.5):
        super().__init__(x, y, w, h, PlatformType.MOVING)
        # path_points: list of (x, y) tuples — at least 2
        self.path_points = [tuple(p) for p in path_points]
        self.speed = speed
        self.current_index = 0
        self.moving_forward = True
        self._prev_x = float(x)
        self._anim_tick = 0

    # ── velocity for carrying the player ──
    @property
    def carry_vx(self):
        return self.x - self._prev_x

    # ── logic ──
    def update(self, dt=1):
        self._prev_x = self.x
        self._anim_tick += 1

        # Target point
        if self.moving_forward:
            target_idx = self.current_index + 1
        else:
            target_idx = self.current_index - 1

        if target_idx < 0 or target_idx >= len(self.path_points):
            self.moving_forward = not self.moving_forward
            return

        tx, ty = self.path_points[target_idx]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.x = float(tx)
            self.y = float(ty)
            self.current_index = target_idx
            # Bounce at endpoints
            if (self.current_index == 0
                    or self.current_index == len(self.path_points) - 1):
                self.moving_forward = not self.moving_forward
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    # ── draw ──
    def draw(self, surf, camera_offset):
        if not self.visible:
            return
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy

        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        deep, warm, floor_c, accent = self._palette()

        # Lighter stone body
        lighter = (min(warm[0] + 15, 255),
                   min(warm[1] + 15, 255),
                   min(warm[2] + 15, 255))
        body = pygame.Rect(int(sx), int(sy), self.w, self.h)
        pygame.draw.rect(surf, lighter, body)

        # Highlight on top
        hl = pygame.Rect(int(sx), int(sy), self.w, min(2, self.h))
        pygame.draw.rect(surf, accent, hl)

        # Subtle border to distinguish from static platforms
        pygame.draw.rect(surf, accent, body, 1)


# ──────────────────────────────────────────────
#  Crumbling Platform
# ──────────────────────────────────────────────
class CrumblingPlatform(Platform):
    """Breaks after the player stands on it, then (maybe) respawns."""

    def __init__(self, x, y, w, h, difficulty=Difficulty.NORMAL):
        super().__init__(x, y, w, h, PlatformType.CRUMBLING)
        self.state = CRUMBLE_STABLE
        self.shake_timer = 0
        self.respawn_timer = 0
        self.difficulty = difficulty
        self._crack_seed = random.randint(0, 9999)

    # ── called by collision system when the player is standing on it ──
    def stand_on(self):
        if self.state == CRUMBLE_STABLE:
            self.state = CRUMBLE_SHAKING
            self.shake_timer = SHAKE_DURATION

    # ── logic ──
    def update(self, dt=1):
        if self.state == CRUMBLE_SHAKING:
            self.shake_timer -= 1
            if self.shake_timer <= 0:
                self.state = CRUMBLE_BROKEN
                # In Earthquake difficulty, platforms never come back
                settings = DIFFICULTY_SETTINGS.get(self.difficulty,
                                                   DIFFICULTY_SETTINGS[Difficulty.NORMAL])
                if settings['crumble_respawn']:
                    self.respawn_timer = RESPAWN_DURATION
                else:
                    self.respawn_timer = -1  # never respawns

        elif self.state == CRUMBLE_BROKEN:
            if self.respawn_timer > 0:
                self.respawn_timer -= 1
                if self.respawn_timer <= 0:
                    self.state = CRUMBLE_RESPAWNING

        elif self.state == CRUMBLE_RESPAWNING:
            # Instantly return to stable
            self.state = CRUMBLE_STABLE

    def get_rect(self):
        """Broken platforms have no collision."""
        if self.state == CRUMBLE_BROKEN:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def collides(self, rect):
        if self.state == CRUMBLE_BROKEN:
            return False
        return self.get_rect().colliderect(rect)

    # ── draw ──
    def draw(self, surf, camera_offset):
        if self.state == CRUMBLE_BROKEN:
            return  # invisible when broken

        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy

        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        # Shake offset
        shake_ox = 0
        shake_oy = 0
        if self.state == CRUMBLE_SHAKING:
            shake_ox = random.randint(-2, 2)
            shake_oy = random.randint(-1, 1)

        deep, warm, floor_c, accent = self._palette()

        # Cracked stone — slightly reddish tint
        crack_color = (min(deep[0] + 20, 255),
                       max(deep[1] - 5, 0),
                       max(deep[2] - 5, 0))
        body = pygame.Rect(int(sx) + shake_ox, int(sy) + shake_oy,
                           self.w, self.h)
        pygame.draw.rect(surf, crack_color, body)

        # Top highlight
        hl = pygame.Rect(int(sx) + shake_ox, int(sy) + shake_oy,
                         self.w, min(2, self.h))
        pygame.draw.rect(surf, warm, hl)

        # Crack lines (deterministic from seed so they look consistent)
        rng = random.Random(self._crack_seed)
        line_color = (max(deep[0] - 15, 0),
                      max(deep[1] - 15, 0),
                      max(deep[2] - 15, 0))
        for _ in range(3):
            cx1 = int(sx) + shake_ox + rng.randint(4, max(5, self.w // 2))
            cy1 = int(sy) + shake_oy + rng.randint(2, max(3, self.h - 2))
            cx2 = cx1 + rng.randint(8, max(9, self.w // 3))
            cy2 = cy1 + rng.randint(-3, 3)
            pygame.draw.line(surf, line_color, (cx1, cy1), (cx2, cy2), 1)

        # Blinking warning when about to break
        if self.state == CRUMBLE_SHAKING and self.shake_timer < 10:
            if self.shake_timer % 4 < 2:
                warn = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                warn.fill((255, 60, 60, 50))
                surf.blit(warn, (int(sx) + shake_ox, int(sy) + shake_oy))


# ──────────────────────────────────────────────
#  Elevator Platform
# ──────────────────────────────────────────────
class ElevatorPlatform(Platform):
    """Vertical-moving platform activated by the player pressing interact."""

    def __init__(self, x, y, w, h, origin_y, target_y, speed=2):
        super().__init__(x, y, w, h, PlatformType.ELEVATOR)
        self.origin_y = float(origin_y)
        self.target_y = float(target_y)
        self.speed = speed
        self.activated = False
        self._going_to_target = True
        self._glow_tick = 0

    @property
    def carry_vx(self):
        return 0

    def activate(self):
        """Called when the player presses interact while standing on it."""
        self.activated = True

    # ── logic ──
    def update(self, dt=1):
        self._glow_tick += 1

        if not self.activated:
            return

        if self._going_to_target:
            dest = self.target_y
        else:
            dest = self.origin_y

        diff = dest - self.y
        if abs(diff) < self.speed:
            self.y = dest
            self.activated = False
            self._going_to_target = not self._going_to_target
        else:
            direction = 1 if diff > 0 else -1
            self.y += direction * self.speed

    # ── draw ──
    def draw(self, surf, camera_offset):
        if not self.visible:
            return
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy

        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        deep, warm, floor_c, accent = self._palette()

        # Metal/stone body
        metal = (min(warm[0] + 25, 255),
                 min(warm[1] + 25, 255),
                 min(warm[2] + 30, 255))
        body = pygame.Rect(int(sx), int(sy), self.w, self.h)
        pygame.draw.rect(surf, metal, body)

        # Border
        pygame.draw.rect(surf, accent, body, 1)

        # Glow indicators — two pulsing circles on the edges
        pulse = int(abs(math.sin(self._glow_tick * 0.06)) * 40)
        glow_color = (min(accent[0] + pulse, 255),
                      min(accent[1] + pulse, 255),
                      min(accent[2] + pulse, 255))
        cx_left = int(sx) + 8
        cx_right = int(sx) + self.w - 8
        cy = int(sy) + self.h // 2
        pygame.draw.circle(surf, glow_color, (cx_left, cy), 3)
        pygame.draw.circle(surf, glow_color, (cx_right, cy), 3)

        # Arrow indicator showing direction
        arrow_color = (200, 200, 220)
        mid_x = int(sx) + self.w // 2
        if self._going_to_target:
            # Down arrow (target is usually below)
            if self.target_y > self.origin_y:
                pts = [(mid_x, int(sy) + self.h - 3),
                       (mid_x - 4, int(sy) + self.h - 7),
                       (mid_x + 4, int(sy) + self.h - 7)]
            else:
                pts = [(mid_x, int(sy) + 3),
                       (mid_x - 4, int(sy) + 7),
                       (mid_x + 4, int(sy) + 7)]
        else:
            pts = [(mid_x, int(sy) + 3),
                   (mid_x - 4, int(sy) + 7),
                   (mid_x + 4, int(sy) + 7)]
        if self.h >= 10:
            pygame.draw.polygon(surf, arrow_color, pts)
