"""
SPLIT -- Visual Effects System
Particle pool, shockwaves, screen flash, hitstop, slow-mo, darkness, fog.
All particles use pre-cached circle surfaces. Fixed-size pool, zero allocations
during gameplay.
"""

import math
import random

import pygame

from game.engine.settings import (
    SCREEN_W,
    SCREEN_H,
    JELLO_GREEN,
    TORCH_AMBER,
    EMBER,
    WHITE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ease_out_quad(t):
    """Deceleration curve: fast start, gentle stop."""
    return 1.0 - (1.0 - t) * (1.0 - t)


def _make_circle_surface(radius, color):
    """Create a circle surface with per-pixel alpha."""
    size = max(radius * 2, 2)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius, radius), radius)
    return surf


# ---------------------------------------------------------------------------
# ParticlePool
# ---------------------------------------------------------------------------

POOL_SIZE = 300


class ParticlePool:
    """Fixed-size particle pool. No allocations during gameplay."""

    def __init__(self):
        # Parallel arrays -- faster than list-of-dicts on large counts.
        self.x = [0.0] * POOL_SIZE
        self.y = [0.0] * POOL_SIZE
        self.vx = [0.0] * POOL_SIZE
        self.vy = [0.0] * POOL_SIZE
        self.color = [WHITE] * POOL_SIZE
        self.size = [2] * POOL_SIZE
        self.lifetime = [0] * POOL_SIZE
        self.max_lifetime = [1] * POOL_SIZE
        self.alive = [False] * POOL_SIZE

        # Ring-buffer index for fast allocation.
        self._next = 0

        # Surface cache: (radius, r, g, b) -> Surface
        self._cache: dict[tuple, pygame.Surface] = {}

    # -- allocation ----------------------------------------------------------

    def _grab_slot(self) -> int:
        """Return the index of the next dead slot (round-robin)."""
        start = self._next
        for _ in range(POOL_SIZE):
            idx = self._next
            self._next = (self._next + 1) % POOL_SIZE
            if not self.alive[idx]:
                return idx
        # Pool full -- recycle oldest (the one we started at).
        return start

    # -- public API ----------------------------------------------------------

    def emit(self, x, y, color, size=3, speed=2.0, lifetime=30, drift_x=0.0):
        """Activate one particle in the pool."""
        idx = self._grab_slot()
        angle = random.uniform(0, math.tau)
        spd = random.uniform(speed * 0.4, speed)

        self.x[idx] = float(x)
        self.y[idx] = float(y)
        self.vx[idx] = math.cos(angle) * spd + drift_x
        self.vy[idx] = math.sin(angle) * spd
        self.color[idx] = color[:3]  # strip alpha if present
        self.size[idx] = max(int(size), 1)
        self.lifetime[idx] = int(lifetime)
        self.max_lifetime[idx] = int(lifetime)
        self.alive[idx] = True

    def burst(self, preset, x, y):
        """Emit a group of particles based on a named preset."""
        if preset == "death":
            self._burst_death(x, y)
        elif preset == "collect":
            self._burst_collect(x, y)
        elif preset == "ground_pound":
            self._burst_ground_pound(x, y)
        elif preset == "split":
            self._burst_split(x, y)
        elif preset == "dodge":
            self._burst_dodge(x, y)

    # -- presets -------------------------------------------------------------

    def _burst_death(self, x, y):
        """30 green particles bursting outward, large."""
        for _ in range(30):
            self.emit(x, y, JELLO_GREEN, size=5, speed=5.0, lifetime=40)

    def _burst_collect(self, x, y):
        """15 amber/colored particles floating upward."""
        colors = [TORCH_AMBER, EMBER, JELLO_GREEN]
        for _ in range(15):
            idx = self._grab_slot()
            c = random.choice(colors)
            self.x[idx] = float(x) + random.uniform(-6, 6)
            self.y[idx] = float(y)
            self.vx[idx] = random.uniform(-0.5, 0.5)
            self.vy[idx] = random.uniform(-3.0, -1.0)
            self.color[idx] = c[:3]
            self.size[idx] = 3
            self.lifetime[idx] = 35
            self.max_lifetime[idx] = 35
            self.alive[idx] = True

    def _burst_ground_pound(self, x, y):
        """25 amber particles in an upward half-circle."""
        for _ in range(25):
            angle = random.uniform(-math.pi, 0)  # upper half-circle
            spd = random.uniform(2.0, 5.0)
            idx = self._grab_slot()
            self.x[idx] = float(x)
            self.y[idx] = float(y)
            self.vx[idx] = math.cos(angle) * spd
            self.vy[idx] = math.sin(angle) * spd
            self.color[idx] = TORCH_AMBER[:3]
            self.size[idx] = 4
            self.lifetime[idx] = 30
            self.max_lifetime[idx] = 30
            self.alive[idx] = True

    def _burst_split(self, x, y):
        """20 green particles in a radial burst."""
        for i in range(20):
            angle = (math.tau / 20) * i + random.uniform(-0.15, 0.15)
            spd = random.uniform(2.5, 4.5)
            idx = self._grab_slot()
            self.x[idx] = float(x)
            self.y[idx] = float(y)
            self.vx[idx] = math.cos(angle) * spd
            self.vy[idx] = math.sin(angle) * spd
            self.color[idx] = JELLO_GREEN[:3]
            self.size[idx] = 3
            self.lifetime[idx] = 25
            self.max_lifetime[idx] = 25
            self.alive[idx] = True

    def _burst_dodge(self, x, y):
        """8 white particles in a horizontal streak."""
        for _ in range(8):
            idx = self._grab_slot()
            self.x[idx] = float(x) + random.uniform(-10, 10)
            self.y[idx] = float(y) + random.uniform(-4, 4)
            self.vx[idx] = random.uniform(-4.0, 4.0)
            self.vy[idx] = random.uniform(-0.3, 0.3)
            self.color[idx] = WHITE[:3]
            self.size[idx] = 2
            self.lifetime[idx] = 12
            self.max_lifetime[idx] = 12
            self.alive[idx] = True

    # -- simulation ----------------------------------------------------------

    def update(self):
        """Tick every living particle."""
        for i in range(POOL_SIZE):
            if not self.alive[i]:
                continue
            self.lifetime[i] -= 1
            if self.lifetime[i] <= 0:
                self.alive[i] = False
                continue
            self.x[i] += self.vx[i]
            self.y[i] += self.vy[i]
            # Gentle drag
            self.vx[i] *= 0.96
            self.vy[i] *= 0.96

    # -- rendering -----------------------------------------------------------

    def _get_cached_surface(self, radius, color):
        """Return a cached circle surface, creating it if needed."""
        key = (radius, color[0], color[1], color[2])
        surf = self._cache.get(key)
        if surf is None:
            surf = _make_circle_surface(radius, color)
            self._cache[key] = surf
        return surf

    def draw(self, surf, camera_offset):
        """Draw all living particles. Culls off-screen particles."""
        ox, oy = camera_offset
        sw, sh = surf.get_size()

        for i in range(POOL_SIZE):
            if not self.alive[i]:
                continue

            sx = self.x[i] + ox
            sy = self.y[i] + oy
            r = self.size[i]

            # Off-screen culling
            if sx < -r or sx > sw + r or sy < -r or sy > sh + r:
                continue

            # Alpha based on remaining lifetime
            t = self.lifetime[i] / self.max_lifetime[i]
            alpha = int(255 * t)

            circle = self._get_cached_surface(r, self.color[i])
            if alpha < 255:
                faded = circle.copy()
                faded.set_alpha(alpha)
                surf.blit(faded, (int(sx) - r, int(sy) - r))
            else:
                surf.blit(circle, (int(sx) - r, int(sy) - r))


# ---------------------------------------------------------------------------
# Shockwave
# ---------------------------------------------------------------------------

class Shockwave:
    """Expanding elliptical ring with amber color and alpha fade."""

    def __init__(self, x, y, radius=5, max_radius=80, lifetime=15):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.start_radius = float(radius)
        self.max_radius = float(max_radius)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alive = True

    def update(self):
        if not self.alive:
            return
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            return
        # Eased expansion
        progress = 1.0 - (self.lifetime / self.max_lifetime)
        t = _ease_out_quad(progress)
        self.radius = self.start_radius + (self.max_radius - self.start_radius) * t

    def draw(self, surf, camera_offset):
        if not self.alive:
            return
        ox, oy = camera_offset
        sx = int(self.x + ox)
        sy = int(self.y + oy)
        r = int(self.radius)

        # Off-screen cull
        sw, sh = surf.get_size()
        if sx + r < 0 or sx - r > sw or sy + r < 0 or sy - r > sh:
            return

        # Alpha fades out
        t = self.lifetime / self.max_lifetime
        alpha = int(200 * t)
        if alpha <= 0:
            return

        # Elliptical ring: wider than tall (draw directly, no temp surface)
        rx = r
        ry = max(int(r * 0.5), 1)
        ring_width = max(int(3 * t), 1)
        rect = pygame.Rect(sx - rx, sy - ry, rx * 2, ry * 2)
        pygame.draw.ellipse(surf, TORCH_AMBER, rect, ring_width)


# ---------------------------------------------------------------------------
# VFXManager
# ---------------------------------------------------------------------------

class VFXManager:
    """Owns all visual effects. The game loop calls update() and draw()."""

    def __init__(self):
        self.particles = ParticlePool()
        self.shockwaves: list[Shockwave] = []

        # -- screen shake (amount only; Camera applies the offset) ----------
        self.shake_amount = 0.0

        # -- screen flash ---------------------------------------------------
        self._flash_timer = 0
        self._flash_max = 0
        self._flash_color = WHITE

        # -- hitstop --------------------------------------------------------
        self.hitstop_frames = 0

        # -- slow-mo --------------------------------------------------------
        self.slow_mo_timer = 0
        self._slow_mo_scale = 0.3

        # -- darkness overlay -----------------------------------------------
        self._dark_surf: pygame.Surface | None = None
        self._dark_w = SCREEN_W
        self._dark_h = SCREEN_H
        self._torch_positions: list[tuple[float, float]] = []
        self._torch_gradient: pygame.Surface | None = None
        self._torch_radius = 180  # full-res pixels

        # -- pre-allocated screen flash surface --------------------------------
        self._flash_surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        # -- fog layers -----------------------------------------------------
        self._fog_layers: list[dict] = []
        self._fog_initialized = False

    # -----------------------------------------------------------------------
    # Darkness
    # -----------------------------------------------------------------------

    def _ensure_darkness_surfaces(self):
        """Lazy-init the half-res darkness surface and radial gradient."""
        if self._dark_surf is None:
            self._dark_surf = pygame.Surface(
                (self._dark_w, self._dark_h), pygame.SRCALPHA
            )
        if self._torch_gradient is None:
            d = self._torch_radius * 2
            self._torch_gradient = pygame.Surface((d, d), pygame.SRCALPHA)
            # Radial gradient: center transparent, edges opaque black
            for r in range(self._torch_radius, 0, -1):
                alpha = int(255 * (1.0 - (r / self._torch_radius) ** 2))
                alpha = max(0, min(255, 255 - alpha))
                # We draw concentric circles from outside in; inner ones are
                # more transparent.
                # Actually we want the center clear and edges dark, but we
                # will blit this with BLEND_RGBA_MIN to "cut" the darkness.
                # So the gradient stores alpha=0 in the center (clear) and
                # alpha=255 at edges (don't cut).
                # Simplest: draw from outside-in, center = (0,0,0,0).
                pass
            # Rebuild properly: gradient where center is (0,0,0,0) and
            # edges are (0,0,0,255).
            self._torch_gradient.fill((0, 0, 0, 255))
            for r in range(self._torch_radius, 0, -1):
                t = r / self._torch_radius
                # 0 at center, 255 at edge
                a = int(255 * (t * t))
                pygame.draw.circle(
                    self._torch_gradient,
                    (0, 0, 0, a),
                    (self._torch_radius, self._torch_radius),
                    r,
                )

    def set_torch_positions(self, positions):
        """Set world-space positions of torches for the darkness overlay.

        Parameters
        ----------
        positions : list of (x, y) tuples
            World-space coordinates of each torch/light source.
        """
        self._torch_positions = list(positions)

    def _draw_darkness(self, surf, camera_offset):
        """Draw a darkness overlay with radial cutouts at torch positions.
        Renders at full resolution to avoid expensive scaling."""
        if not self._torch_positions:
            return

        self._ensure_darkness_surfaces()
        dark = self._dark_surf
        dark.fill((0, 0, 0, 180))

        ox, oy = camera_offset
        grad = self._torch_gradient
        tr = self._torch_radius

        for tx, ty in self._torch_positions:
            hx = int(tx + ox) - tr
            hy = int(ty + oy) - tr
            dark.blit(grad, (hx, hy), special_flags=pygame.BLEND_RGBA_MIN)

        surf.blit(dark, (0, 0))

    # -----------------------------------------------------------------------
    # Fog
    # -----------------------------------------------------------------------

    def _ensure_fog(self):
        """Lazy-init three parallax fog strips."""
        if self._fog_initialized:
            return
        self._fog_initialized = True

        # Each layer: surface, scroll speed, current x offset
        configs = [
            {"alpha": 18, "speed": 0.3, "height": 120, "y_offset": 0.7},
            {"alpha": 12, "speed": 0.5, "height": 80, "y_offset": 0.5},
            {"alpha": 8, "speed": 0.8, "height": 60, "y_offset": 0.85},
        ]
        for cfg in configs:
            # Double-wide for seamless scrolling
            w = SCREEN_W * 2
            h = cfg["height"]
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            # Semi-transparent horizontal band with soft edges
            for row in range(h):
                # Fade at top and bottom of strip
                edge = min(row, h - 1 - row) / max(h * 0.3, 1)
                edge = min(edge, 1.0)
                a = int(cfg["alpha"] * edge)
                pygame.draw.line(s, (200, 200, 220, a), (0, row), (w - 1, row))
            self._fog_layers.append({
                "surf": s,
                "speed": cfg["speed"],
                "x": 0.0,
                "y_ratio": cfg["y_offset"],
                "width": w,
            })

    def _draw_fog(self, surf):
        """Draw parallax fog layers on screen."""
        self._ensure_fog()
        for layer in self._fog_layers:
            layer["x"] -= layer["speed"]
            if layer["x"] <= -SCREEN_W:
                layer["x"] += SCREEN_W
            y = int(SCREEN_H * layer["y_ratio"])
            surf.blit(layer["surf"], (int(layer["x"]), y))

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def emit(self, x, y, color, size=3, speed=2.0, lifetime=30, drift_x=0.0):
        """Emit a single particle (delegates to the pool)."""
        self.particles.emit(x, y, color, size, speed, lifetime, drift_x)

    def burst(self, preset, x, y):
        """Emit a preset burst. Some presets also spawn a shockwave."""
        self.particles.burst(preset, x, y)

        # Certain presets get a shockwave too
        if preset == "death":
            self.shockwaves.append(Shockwave(x, y, radius=5, max_radius=90, lifetime=18))
        elif preset == "ground_pound":
            self.shockwaves.append(Shockwave(x, y, radius=5, max_radius=80, lifetime=15))
        elif preset == "split":
            self.shockwaves.append(Shockwave(x, y, radius=5, max_radius=60, lifetime=12))

    def trigger_flash(self, flash_type="white"):
        """Start a screen flash.

        Parameters
        ----------
        flash_type : str
            'white' for hit flash (8 frames) or 'red' for damage flash (12 frames).
        """
        if flash_type == "white":
            self._flash_color = WHITE
            self._flash_timer = 8
            self._flash_max = 8
        elif flash_type == "red":
            self._flash_color = (220, 50, 50)
            self._flash_timer = 12
            self._flash_max = 12

    def trigger_hitstop(self, frames=2):
        """Pause the game for *frames* to sell impact."""
        self.hitstop_frames = frames

    def trigger_slow_mo(self, frames=6):
        """Slow time for a perfect-dodge effect."""
        self.slow_mo_timer = frames

    def trigger_shake(self, amount):
        """Signal the camera to shake. Camera reads ``vfx.shake_amount``."""
        self.shake_amount = float(amount)

    def get_time_scale(self):
        """Return current time multiplier (1.0 = normal, <1.0 = slow-mo)."""
        if self.slow_mo_timer > 0:
            return self._slow_mo_scale
        return 1.0

    # -----------------------------------------------------------------------
    # Update
    # -----------------------------------------------------------------------

    def update(self):
        """Tick all VFX subsystems. Call once per frame."""
        # Particles
        self.particles.update()

        # Shockwaves
        for sw in self.shockwaves:
            sw.update()
        # Remove dead shockwaves
        self.shockwaves = [sw for sw in self.shockwaves if sw.alive]

        # Flash timer
        if self._flash_timer > 0:
            self._flash_timer -= 1

        # Hitstop (game loop should skip physics when > 0)
        if self.hitstop_frames > 0:
            self.hitstop_frames -= 1

        # Slow-mo countdown
        if self.slow_mo_timer > 0:
            self.slow_mo_timer -= 1

        # Shake decay
        if self.shake_amount > 0:
            self.shake_amount *= 0.8
            if self.shake_amount < 0.5:
                self.shake_amount = 0.0

    # -----------------------------------------------------------------------
    # Draw
    # -----------------------------------------------------------------------

    def draw(self, surf, camera_offset=(0, 0)):
        """Render all visual effects onto *surf*.

        Parameters
        ----------
        surf : pygame.Surface
            The target surface (usually the screen).
        camera_offset : tuple of (int, int)
            World-to-screen offset provided by the Camera.
        """
        # Particles (world-space, needs camera offset)
        self.particles.draw(surf, camera_offset)

        # Shockwaves (world-space)
        for sw in self.shockwaves:
            sw.draw(surf, camera_offset)

        # Fog (screen-space, no camera offset)
        self._draw_fog(surf)

        # Darkness overlay (world-space torch positions)
        self._draw_darkness(surf, camera_offset)

        # Screen flash (screen-space, drawn last so it overlays everything)
        if self._flash_timer > 0:
            t = self._flash_timer / self._flash_max
            alpha = int(120 * t)
            self._flash_surface.fill((*self._flash_color[:3], alpha))
            surf.blit(self._flash_surface, (0, 0))
