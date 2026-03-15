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
    SANITIZER_BLUE,
    TORCH_AMBER,
    EMBER,
    WHITE,
    BLACK,
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
# Color constants for VFX (not exported to settings -- internal only)
# ---------------------------------------------------------------------------

_GOLD = (255, 215, 60)
_GOLD_BRIGHT = (255, 240, 120)
_STONE_GRAY = (140, 130, 120)
_STONE_BROWN = (110, 95, 80)
_DUST_TAN = (170, 155, 130)
_HEAL_GREEN = (100, 230, 90)
_HEAL_GREEN_LIGHT = (160, 255, 140)
_RIPPLE_CYAN = (180, 220, 255)
_RIPPLE_WHITE = (220, 235, 255)


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
        self.gravity = [0.0] * POOL_SIZE  # per-particle gravity (0 = float, >0 = fall)
        self.color = [WHITE] * POOL_SIZE
        self.size = [2] * POOL_SIZE
        self.start_size = [2] * POOL_SIZE  # for shrink-over-lifetime effects
        self.shrink = [False] * POOL_SIZE  # whether particle shrinks as it dies
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

    def emit(self, x, y, color, size=3, speed=2.0, lifetime=30, drift_x=0.0,
             gravity=0.0, shrink_flag=False):
        """Activate one particle in the pool."""
        idx = self._grab_slot()
        angle = random.uniform(0, math.tau)
        spd = random.uniform(speed * 0.4, speed)

        self.x[idx] = float(x)
        self.y[idx] = float(y)
        self.vx[idx] = math.cos(angle) * spd + drift_x
        self.vy[idx] = math.sin(angle) * spd
        self.gravity[idx] = float(gravity)
        self.color[idx] = color[:3]  # strip alpha if present
        self.size[idx] = max(int(size), 1)
        self.start_size[idx] = max(int(size), 1)
        self.shrink[idx] = shrink_flag
        self.lifetime[idx] = int(lifetime)
        self.max_lifetime[idx] = int(lifetime)
        self.alive[idx] = True

    def emit_directed(self, x, y, vx, vy, color, size=3, lifetime=30,
                      gravity=0.0, shrink_flag=False):
        """Activate one particle with explicit velocity (no random angle)."""
        idx = self._grab_slot()
        self.x[idx] = float(x)
        self.y[idx] = float(y)
        self.vx[idx] = float(vx)
        self.vy[idx] = float(vy)
        self.gravity[idx] = float(gravity)
        self.color[idx] = color[:3]
        self.size[idx] = max(int(size), 1)
        self.start_size[idx] = max(int(size), 1)
        self.shrink[idx] = shrink_flag
        self.lifetime[idx] = int(lifetime)
        self.max_lifetime[idx] = int(lifetime)
        self.alive[idx] = True

    def burst(self, preset, x, y, **kwargs):
        """Emit a group of particles based on a named preset."""
        handler = self._BURST_TABLE.get(preset)
        if handler is not None:
            handler(self, x, y, **kwargs)

    # -- presets -------------------------------------------------------------

    def _burst_death(self, x, y, **kwargs):
        """Explosion of colored particles that shrink and fade.

        Pass color=(r,g,b) for enemy-colored death; defaults to jello green.
        """
        color = kwargs.get("color", JELLO_GREEN)
        # 30 particles: mix of sizes for visual variety
        for _ in range(20):
            self.emit(x, y, color, size=5, speed=5.0, lifetime=40, shrink_flag=True)
        # Smaller sparkle debris
        for _ in range(10):
            self.emit(x, y, color, size=2, speed=6.5, lifetime=25, shrink_flag=True)

    def _burst_collect(self, x, y, **kwargs):
        """15 amber/colored particles floating upward."""
        colors = [TORCH_AMBER, EMBER, JELLO_GREEN]
        for _ in range(15):
            idx = self._grab_slot()
            c = random.choice(colors)
            self.x[idx] = float(x) + random.uniform(-6, 6)
            self.y[idx] = float(y)
            self.vx[idx] = random.uniform(-0.5, 0.5)
            self.vy[idx] = random.uniform(-3.0, -1.0)
            self.gravity[idx] = 0.0
            self.color[idx] = c[:3]
            self.size[idx] = 3
            self.start_size[idx] = 3
            self.shrink[idx] = False
            self.lifetime[idx] = 35
            self.max_lifetime[idx] = 35
            self.alive[idx] = True

    def _burst_ground_pound(self, x, y, **kwargs):
        """HEAVY impact: debris arcing outward + dust cloud.

        Impact ring handled by VFXManager (shockwave).
        15 rock/dust particles arc outward and fall with gravity.
        10 dust puff particles spread low along the ground.
        """
        rock_colors = [_STONE_GRAY, _STONE_BROWN, _DUST_TAN]

        # Rock debris arcing outward and falling
        for _ in range(15):
            idx = self._grab_slot()
            # Horizontal spread, upward launch
            angle = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            spd = random.uniform(3.0, 7.0)
            self.x[idx] = float(x) + random.uniform(-8, 8)
            self.y[idx] = float(y)
            self.vx[idx] = math.cos(angle) * spd
            self.vy[idx] = math.sin(angle) * spd - random.uniform(1.0, 3.0)
            self.gravity[idx] = 0.35  # fall back down
            self.color[idx] = random.choice(rock_colors)
            self.size[idx] = random.choice([2, 3, 4])
            self.start_size[idx] = self.size[idx]
            self.shrink[idx] = False
            self.lifetime[idx] = 35
            self.max_lifetime[idx] = 35
            self.alive[idx] = True

        # Low dust puffs spreading horizontally
        for _ in range(10):
            idx = self._grab_slot()
            direction = random.choice([-1, 1])
            self.x[idx] = float(x) + random.uniform(-4, 4)
            self.y[idx] = float(y) + random.uniform(-2, 2)
            self.vx[idx] = direction * random.uniform(2.0, 5.0)
            self.vy[idx] = random.uniform(-1.5, 0.0)
            self.gravity[idx] = 0.0
            self.color[idx] = _DUST_TAN
            self.size[idx] = 3
            self.start_size[idx] = 3
            self.shrink[idx] = True
            self.lifetime[idx] = 20
            self.max_lifetime[idx] = 20
            self.alive[idx] = True

    def _burst_split(self, x, y, **kwargs):
        """Jello glob separation: 4 large blobs fly outward briefly, plus
        16 small drip particles for a wet, physical feel."""
        # 4 large jello blobs at cardinal-ish directions
        for i in range(4):
            idx = self._grab_slot()
            angle = (math.tau / 4) * i + random.uniform(-0.3, 0.3)
            spd = random.uniform(3.0, 5.0)
            self.x[idx] = float(x)
            self.y[idx] = float(y)
            self.vx[idx] = math.cos(angle) * spd
            self.vy[idx] = math.sin(angle) * spd
            self.gravity[idx] = 0.15  # settle down
            self.color[idx] = JELLO_GREEN[:3]
            self.size[idx] = 6
            self.start_size[idx] = 6
            self.shrink[idx] = True
            self.lifetime[idx] = 22
            self.max_lifetime[idx] = 22
            self.alive[idx] = True

        # Smaller drip/splash particles
        for _ in range(16):
            idx = self._grab_slot()
            angle = random.uniform(0, math.tau)
            spd = random.uniform(1.5, 4.0)
            self.x[idx] = float(x) + random.uniform(-4, 4)
            self.y[idx] = float(y) + random.uniform(-4, 4)
            self.vx[idx] = math.cos(angle) * spd
            self.vy[idx] = math.sin(angle) * spd
            self.gravity[idx] = 0.1
            self.color[idx] = JELLO_GREEN[:3]
            self.size[idx] = 2
            self.start_size[idx] = 2
            self.shrink[idx] = False
            self.lifetime[idx] = 18
            self.max_lifetime[idx] = 18
            self.alive[idx] = True

    def _burst_dodge(self, x, y, **kwargs):
        """8 white particles in a horizontal streak."""
        for _ in range(8):
            idx = self._grab_slot()
            self.x[idx] = float(x) + random.uniform(-10, 10)
            self.y[idx] = float(y) + random.uniform(-4, 4)
            self.vx[idx] = random.uniform(-4.0, 4.0)
            self.vy[idx] = random.uniform(-0.3, 0.3)
            self.gravity[idx] = 0.0
            self.color[idx] = WHITE[:3]
            self.size[idx] = 2
            self.start_size[idx] = 2
            self.shrink[idx] = False
            self.lifetime[idx] = 12
            self.max_lifetime[idx] = 12
            self.alive[idx] = True

    def _burst_dodge_slow_mo(self, x, y, **kwargs):
        """Concentric ripple particles for successful dodge slow-mo.

        Creates a brief visual ripple/distortion feel using rings of particles
        that expand outward and fade over 3-4 frames of visual.
        """
        colors = [_RIPPLE_CYAN, _RIPPLE_WHITE, WHITE]
        # Two concentric ring waves
        for ring in range(2):
            ring_delay_offset = ring * 4  # stagger timing
            num_points = 10
            base_radius = 12 + ring * 10
            for i in range(num_points):
                idx = self._grab_slot()
                angle = (math.tau / num_points) * i + random.uniform(-0.1, 0.1)
                spd = 3.5 + ring * 1.5
                self.x[idx] = float(x) + math.cos(angle) * base_radius
                self.y[idx] = float(y) + math.sin(angle) * base_radius
                self.vx[idx] = math.cos(angle) * spd
                self.vy[idx] = math.sin(angle) * spd
                self.gravity[idx] = 0.0
                self.color[idx] = random.choice(colors)
                self.size[idx] = 3 - ring
                self.start_size[idx] = self.size[idx]
                self.shrink[idx] = True
                lt = 10 - ring_delay_offset
                self.lifetime[idx] = max(lt, 4)
                self.max_lifetime[idx] = max(lt, 4)
                self.alive[idx] = True

    def _burst_crumble_particles(self, x, y, **kwargs):
        """Stone/dust particles when a crumbling platform breaks.

        Gray/brown colored, 12 particles, fall with gravity, short lifetime.
        """
        colors = [_STONE_GRAY, _STONE_BROWN, _DUST_TAN]
        for _ in range(12):
            idx = self._grab_slot()
            self.x[idx] = float(x) + random.uniform(-20, 20)
            self.y[idx] = float(y) + random.uniform(-4, 4)
            self.vx[idx] = random.uniform(-1.5, 1.5)
            self.vy[idx] = random.uniform(-2.0, 0.5)
            self.gravity[idx] = 0.25
            self.color[idx] = random.choice(colors)
            self.size[idx] = random.choice([2, 3])
            self.start_size[idx] = self.size[idx]
            self.shrink[idx] = False
            self.lifetime[idx] = 28
            self.max_lifetime[idx] = 28
            self.alive[idx] = True

    def _burst_collect_sparkle(self, x, y, **kwargs):
        """Golden sparkle particles floating upward on item collect.

        5-8 golden/yellow particles that drift upward and fade.
        """
        colors = [_GOLD, _GOLD_BRIGHT, TORCH_AMBER]
        count = random.randint(5, 8)
        for _ in range(count):
            idx = self._grab_slot()
            self.x[idx] = float(x) + random.uniform(-8, 8)
            self.y[idx] = float(y) + random.uniform(-4, 4)
            self.vx[idx] = random.uniform(-0.8, 0.8)
            self.vy[idx] = random.uniform(-2.5, -1.0)
            self.gravity[idx] = -0.02  # gentle upward drift
            self.color[idx] = random.choice(colors)
            self.size[idx] = random.choice([2, 3])
            self.start_size[idx] = self.size[idx]
            self.shrink[idx] = False
            self.lifetime[idx] = 30
            self.max_lifetime[idx] = 30
            self.alive[idx] = True

    def _burst_boss_entrance(self, x, y, **kwargs):
        """Dramatic boss entrance: burst of large particles outward.

        The big shockwave ring + screen flash are handled by VFXManager.
        This emits 25 particles to fill the space.
        """
        colors = [EMBER, (180, 40, 40), TORCH_AMBER]
        for _ in range(25):
            idx = self._grab_slot()
            angle = random.uniform(0, math.tau)
            spd = random.uniform(3.0, 8.0)
            self.x[idx] = float(x)
            self.y[idx] = float(y)
            self.vx[idx] = math.cos(angle) * spd
            self.vy[idx] = math.sin(angle) * spd
            self.gravity[idx] = 0.05
            self.color[idx] = random.choice(colors)
            self.size[idx] = random.choice([3, 4, 5])
            self.start_size[idx] = self.size[idx]
            self.shrink[idx] = True
            self.lifetime[idx] = 35
            self.max_lifetime[idx] = 35
            self.alive[idx] = True

    def _burst_checkpoint_save(self, x, y, **kwargs):
        """Golden glow burst when checkpoint is reached.

        Warm yellow/gold particles rising upward, nurturing feel.
        """
        colors = [_GOLD, _GOLD_BRIGHT, TORCH_AMBER]
        for _ in range(15):
            idx = self._grab_slot()
            self.x[idx] = float(x) + random.uniform(-12, 12)
            self.y[idx] = float(y) + random.uniform(-6, 6)
            self.vx[idx] = random.uniform(-0.6, 0.6)
            self.vy[idx] = random.uniform(-2.8, -0.8)
            self.gravity[idx] = -0.03  # float upward
            self.color[idx] = random.choice(colors)
            self.size[idx] = random.choice([2, 3, 4])
            self.start_size[idx] = self.size[idx]
            self.shrink[idx] = False
            self.lifetime[idx] = 40
            self.max_lifetime[idx] = 40
            self.alive[idx] = True

    def _burst_heal_effect(self, x, y, **kwargs):
        """Green particles rising from the player when eating cooked jelly.

        Gentle, nurturing feel. Particles drift upward slowly.
        """
        colors = [_HEAL_GREEN, _HEAL_GREEN_LIGHT, JELLO_GREEN]
        for _ in range(12):
            idx = self._grab_slot()
            self.x[idx] = float(x) + random.uniform(-16, 16)
            self.y[idx] = float(y) + random.uniform(0, 10)
            self.vx[idx] = random.uniform(-0.4, 0.4)
            self.vy[idx] = random.uniform(-2.0, -0.6)
            self.gravity[idx] = -0.02
            self.color[idx] = random.choice(colors)
            self.size[idx] = random.choice([2, 3])
            self.start_size[idx] = self.size[idx]
            self.shrink[idx] = False
            self.lifetime[idx] = 35
            self.max_lifetime[idx] = 35
            self.alive[idx] = True

    # -- preset dispatch table (avoids long if/elif chains) ------------------
    _BURST_TABLE: dict = {}  # populated after class body

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
            # Apply per-particle gravity
            self.vy[i] += self.gravity[i]
            # Gentle drag
            self.vx[i] *= 0.96
            self.vy[i] *= 0.96
            # Shrink over lifetime
            if self.shrink[i]:
                t = self.lifetime[i] / self.max_lifetime[i]
                self.size[i] = max(int(self.start_size[i] * t), 1)

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

            # Alpha based on remaining lifetime (quantize to 8 levels to reduce cache)
            t = self.lifetime[i] / self.max_lifetime[i]
            alpha_bucket = max(1, int(t * 8)) * 32 - 1  # 31,63,95,...,255

            circle = self._get_cached_surface(r, self.color[i])
            if alpha_bucket < 255:
                # Cache faded versions by (radius, color, alpha_bucket)
                alpha_key = (r, self.color[i][0], self.color[i][1],
                             self.color[i][2], alpha_bucket)
                faded = self._cache.get(alpha_key)
                if faded is None:
                    faded = circle.copy()
                    faded.set_alpha(alpha_bucket)
                    self._cache[alpha_key] = faded
                surf.blit(faded, (int(sx) - r, int(sy) - r))
            else:
                surf.blit(circle, (int(sx) - r, int(sy) - r))


# -- Wire up burst dispatch table after all methods are defined --------------
ParticlePool._BURST_TABLE = {
    "death": ParticlePool._burst_death,
    "collect": ParticlePool._burst_collect,
    "ground_pound": ParticlePool._burst_ground_pound,
    "split": ParticlePool._burst_split,
    "dodge": ParticlePool._burst_dodge,
    "dodge_slow_mo": ParticlePool._burst_dodge_slow_mo,
    "crumble_particles": ParticlePool._burst_crumble_particles,
    "collect_sparkle": ParticlePool._burst_collect_sparkle,
    "boss_entrance": ParticlePool._burst_boss_entrance,
    "checkpoint_save": ParticlePool._burst_checkpoint_save,
    "heal_effect": ParticlePool._burst_heal_effect,
}


# ---------------------------------------------------------------------------
# Shockwave
# ---------------------------------------------------------------------------

class Shockwave:
    """Expanding elliptical ring with configurable color and alpha fade."""

    def __init__(self, x, y, radius=5, max_radius=80, lifetime=15,
                 color=None, circular=False):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.start_radius = float(radius)
        self.max_radius = float(max_radius)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color if color is not None else TORCH_AMBER
        self.circular = circular  # True = perfect circle, False = ellipse
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

        ring_width = max(int(3 * t), 1)
        color = self.color[:3]

        if self.circular:
            # Perfect circle ring
            pygame.draw.circle(surf, color, (sx, sy), r, ring_width)
        else:
            # Elliptical ring: wider than tall (ground-hugging impact)
            rx = r
            ry = max(int(r * 0.5), 1)
            rect = pygame.Rect(sx - rx, sy - ry, rx * 2, ry * 2)
            pygame.draw.ellipse(surf, color, rect, ring_width)


# ---------------------------------------------------------------------------
# VFXManager
# ---------------------------------------------------------------------------

# Slow-mo ramp duration (frames to transition in/out)
_SLOW_MO_RAMP = 3


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

        # -- slow-mo (with smooth ramp) -------------------------------------
        self._slow_mo_target_frames = 0  # total slow-mo frames requested
        self._slow_mo_elapsed = 0        # frames since slow-mo started
        self._slow_mo_total = 0          # target + ramp out
        self._slow_mo_active = False
        self._slow_mo_base_scale = 0.3   # deepest slow-mo value
        self._current_time_scale = 1.0   # smoothly interpolated

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

    def burst(self, preset, x, y, **kwargs):
        """Emit a preset burst. Some presets also spawn a shockwave.

        Supported presets:
            death, collect, ground_pound, split, dodge,
            dodge_slow_mo, crumble_particles, collect_sparkle,
            boss_entrance, checkpoint_save, heal_effect
        """
        self.particles.burst(preset, x, y, **kwargs)

        # Certain presets get a shockwave too
        if preset == "death":
            self.shockwaves.append(
                Shockwave(x, y, radius=5, max_radius=90, lifetime=18))
        elif preset == "ground_pound":
            self.shockwaves.append(
                Shockwave(x, y, radius=5, max_radius=80, lifetime=15))
        elif preset == "split":
            self.shockwaves.append(
                Shockwave(x, y, radius=5, max_radius=60, lifetime=12,
                          color=JELLO_GREEN, circular=True))
        elif preset == "dodge_slow_mo":
            self.shockwaves.append(
                Shockwave(x, y, radius=8, max_radius=50, lifetime=8,
                          color=_RIPPLE_CYAN, circular=True))
        elif preset == "boss_entrance":
            # Large dramatic shockwave
            self.shockwaves.append(
                Shockwave(x, y, radius=10, max_radius=160, lifetime=25,
                          color=EMBER, circular=True))
            # Trigger a white screen flash for the dramatic entrance
            self.trigger_flash("white")

    def trigger_flash(self, flash_type="white"):
        """Start a screen flash.

        Parameters
        ----------
        flash_type : str
            'white' -- enemy hit confirmation (4 frames, semi-transparent)
            'red'   -- damage taken (5 frames)
            'gold'  -- item collected (4 frames)
        """
        if flash_type == "white":
            self._flash_color = WHITE
            self._flash_timer = 4
            self._flash_max = 4
        elif flash_type == "red":
            self._flash_color = (220, 50, 50)
            self._flash_timer = 5
            self._flash_max = 5
        elif flash_type == "gold":
            self._flash_color = _GOLD
            self._flash_timer = 4
            self._flash_max = 4

    def trigger_hitstop(self, frames=2):
        """Pause the game for *frames* to sell impact."""
        self.hitstop_frames = frames

    def trigger_slow_mo(self, frames=6):
        """Slow time for a perfect-dodge effect.

        Ramps smoothly: 3 frames ramp-in to 0.3x, hold, 3 frames ramp-out.
        """
        self._slow_mo_target_frames = frames
        self._slow_mo_elapsed = 0
        self._slow_mo_total = frames + _SLOW_MO_RAMP  # ramp-in happens during frames
        self._slow_mo_active = True

    def trigger_shake(self, amount):
        """Signal the camera to shake. Camera reads ``vfx.shake_amount``."""
        self.shake_amount = float(amount)

    def get_time_scale(self):
        """Return current time multiplier (1.0 = normal, <1.0 = slow-mo).

        Smoothly ramps over 3 frames in and out of slow-mo.
        """
        return self._current_time_scale

    # Legacy attribute access for code that reads slow_mo_timer directly
    @property
    def slow_mo_timer(self):
        """Backwards-compatible: returns frames remaining in slow-mo."""
        if self._slow_mo_active:
            remaining = self._slow_mo_total - self._slow_mo_elapsed
            return max(remaining, 0)
        return 0

    @slow_mo_timer.setter
    def slow_mo_timer(self, value):
        """Backwards-compatible setter: starts slow-mo with the given frames."""
        if value > 0:
            self.trigger_slow_mo(value)
        else:
            self._slow_mo_active = False
            self._current_time_scale = 1.0

    # -----------------------------------------------------------------------
    # Update
    # -----------------------------------------------------------------------

    def _update_slow_mo(self):
        """Update slow-mo with smooth ramp in/out."""
        if not self._slow_mo_active:
            self._current_time_scale = 1.0
            return

        self._slow_mo_elapsed += 1
        base = self._slow_mo_base_scale
        target_frames = self._slow_mo_target_frames

        if self._slow_mo_elapsed > self._slow_mo_total:
            # Done
            self._slow_mo_active = False
            self._current_time_scale = 1.0
            return

        # Ramp-in phase (first _SLOW_MO_RAMP frames)
        if self._slow_mo_elapsed <= _SLOW_MO_RAMP:
            t = self._slow_mo_elapsed / _SLOW_MO_RAMP
            self._current_time_scale = 1.0 - (1.0 - base) * t
        # Hold phase
        elif self._slow_mo_elapsed <= target_frames:
            self._current_time_scale = base
        # Ramp-out phase (last _SLOW_MO_RAMP frames)
        else:
            frames_into_rampout = self._slow_mo_elapsed - target_frames
            t = frames_into_rampout / _SLOW_MO_RAMP
            t = min(t, 1.0)
            self._current_time_scale = base + (1.0 - base) * t

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

        # Slow-mo with smooth ramp
        self._update_slow_mo()

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
            alpha = int(100 * t)  # semi-transparent, brief
            self._flash_surface.fill((*self._flash_color[:3], alpha))
            surf.blit(self._flash_surface, (0, 0))
