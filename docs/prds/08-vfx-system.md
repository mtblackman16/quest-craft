# PRD 08: VFX System — Split

| Field | Value |
|-------|-------|
| **Status** | Design Complete |
| **Author** | Claude (VFX Specialist) |
| **Date** | 2026-03-08 |
| **Reviewed by** | Pending team review |
| **Depends on** | [00-game-concept.md](00-game-concept.md), [05-art-style.md](05-art-style.md) |

---

## Overview

This document defines every visual effect in Split, with exact Pygame implementation techniques. Every effect is designed to run at 60fps on Raspberry Pi 5 (Broadcom BCM2712, VideoCore VII GPU, 8GB RAM). The current codebase (`game/spark.py`) already has a working Particle class, Shockwave, JelloProjectile, squash-and-stretch, and screen shake. This PRD extends that foundation into a full production VFX system.

**Design philosophy:** Effects should feel *gooey, wobbly, and alive* — matching the jello theme. The castle should feel *dark, atmospheric, and dangerous*. Every effect serves gameplay readability first, spectacle second.

---

## Table of Contents

1. [Architecture: VFX Manager](#1-architecture-vfx-manager)
2. [Jello Physics and Visual Effects](#2-jello-physics-and-visual-effects)
3. [Environmental Effects](#3-environmental-effects)
4. [Combat VFX](#4-combat-vfx)
5. [UI/HUD Effects](#5-uihud-effects)
6. [Performance Budget](#6-performance-budget)
7. [Wow Moments](#7-wow-moments)
8. [Implementation Priority](#8-implementation-priority)

---

## 1. Architecture: VFX Manager

All effects funnel through a single `VFXManager` class that owns the particle pool, manages surface caches, and enforces the performance budget.

### Particle Pool Pattern

The current `spark.py` creates a new `pygame.Surface` for every particle every frame. That is the single biggest performance cost. The fix: pre-allocate a pool of reusable particle surfaces and recycle them.

```python
class ParticlePool:
    """Pre-allocated pool of particle surfaces. Zero allocation during gameplay."""

    def __init__(self, max_particles=300):
        self.max = max_particles
        # Pre-create surfaces for common sizes (radius 1-8)
        self.surface_cache = {}
        for r in range(1, 9):
            size = r * 2
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            self.surface_cache[r] = surf

        # Pool of particle data (struct-of-arrays for cache friendliness)
        self.x = [0.0] * max_particles
        self.y = [0.0] * max_particles
        self.vx = [0.0] * max_particles
        self.vy = [0.0] * max_particles
        self.life = [0] * max_particles      # 0 = dead/available
        self.max_life = [0] * max_particles
        self.r = [0] * max_particles          # radius
        self.color = [(0,0,0)] * max_particles
        self.alive_count = 0

    def emit(self, x, y, vx, vy, color, radius, lifetime):
        """Grab a dead particle and activate it. O(1) amortized."""
        for i in range(self.max):
            if self.life[i] <= 0:
                self.x[i] = x
                self.y[i] = y
                self.vx[i] = vx
                self.vy[i] = vy
                self.color[i] = color
                self.r[i] = min(radius, 8)
                self.life[i] = lifetime
                self.max_life[i] = lifetime
                self.alive_count += 1
                return i
        return -1  # pool exhausted — silently drop

    def update(self):
        """Tick all alive particles. Single tight loop."""
        for i in range(self.max):
            if self.life[i] > 0:
                self.x[i] += self.vx[i]
                self.y[i] += self.vy[i]
                self.life[i] -= 1
                if self.life[i] <= 0:
                    self.alive_count -= 1

    def draw(self, target_surface, camera_x=0, camera_y=0):
        """Draw all alive particles using cached surfaces."""
        for i in range(self.max):
            if self.life[i] > 0:
                fade = self.life[i] / self.max_life[i]
                r = max(1, int(self.r[i] * fade))
                alpha = int(200 * fade)
                # Reuse cached surface
                surf = self.surface_cache.get(r)
                if surf is None:
                    continue
                surf.fill((0, 0, 0, 0))
                color = (*self.color[i][:3], alpha)
                pygame.draw.circle(surf, color, (r, r), r)
                target_surface.blit(
                    surf,
                    (int(self.x[i]) - r - camera_x,
                     int(self.y[i]) - r - camera_y)
                )
```

**Why this is faster:** No `pygame.Surface()` allocation per particle per frame. The cache holds 8 surfaces total, rewritten in-place with `fill()` + `draw.circle()`. On Pi 5, this cuts particle rendering cost by roughly 70%.

### VFX Manager

```python
class VFXManager:
    """Central hub for all visual effects."""

    def __init__(self):
        self.particles = ParticlePool(max_particles=300)
        self.shockwaves = []          # list of active Shockwave objects
        self.screen_shake = 0.0       # current shake magnitude
        self.screen_flash = None      # (color, duration, timer) or None
        self.camera_zoom = 1.0        # for boss entrances
        self.camera_zoom_target = 1.0

        # Pre-rendered surface cache
        self._glow_cache = {}         # {(radius, color_key): Surface}
        self._ring_cache = {}

    def shake(self, magnitude):
        self.screen_shake = max(self.screen_shake, magnitude)

    def flash(self, color, duration=6):
        self.screen_flash = (color, duration, duration)

    def zoom_to(self, target, speed=0.05):
        self.camera_zoom_target = target
        # zoom lerps each frame

    def update(self):
        self.particles.update()
        self.shockwaves = [s for s in self.shockwaves if s.update()]

        # Shake decay
        if self.screen_shake > 0:
            self.screen_shake *= 0.8
            if self.screen_shake < 0.5:
                self.screen_shake = 0

        # Flash decay
        if self.screen_flash:
            color, dur, timer = self.screen_flash
            timer -= 1
            if timer <= 0:
                self.screen_flash = None
            else:
                self.screen_flash = (color, dur, timer)

        # Zoom lerp
        self.camera_zoom += (self.camera_zoom_target - self.camera_zoom) * 0.08

    def get_shake_offset(self):
        if self.screen_shake > 0:
            import random
            return (random.uniform(-self.screen_shake, self.screen_shake),
                    random.uniform(-self.screen_shake, self.screen_shake))
        return (0, 0)

    def draw_flash(self, screen):
        if self.screen_flash:
            color, dur, timer = self.screen_flash
            alpha = int(120 * (timer / dur))
            flash_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            flash_surf.fill((*color[:3], alpha))
            screen.blit(flash_surf, (0, 0))

    def get_glow(self, radius, color, alpha=30):
        """Return a cached glow surface. Only creates once per unique (radius, color)."""
        key = (radius, color[:3])
        if key not in self._glow_cache:
            size = radius * 2
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color[:3], alpha), (radius, radius), radius)
            self._glow_cache[key] = surf
        return self._glow_cache[key]
```

**Performance note:** The `_glow_cache` dictionary means glow circles are drawn once and reused forever. A torch glow that currently costs `pygame.draw.circle` every frame becomes a single `blit` after the first frame.

---

## 2. Jello Physics and Visual Effects

### 2.1 Jiggle/Wobble Animation

**What it looks like:** The jello cube's outline wobbles like real gelatin. When standing still, a slow breathing wobble. When moving, a faster jiggle synced to footsteps. When landing, a dramatic bounce oscillation.

**Current state:** `spark.py` already has `jiggle_phase` and basic squash-stretch. The upgrade is to make the body outline itself deform, not just scale uniformly.

**Implementation — Sine-Wave Edge Deformation:**

```python
def draw_jello_body(self, surf, draw_x, draw_y, draw_w, draw_h, t):
    """Draw the jello body with wobbly edges using sine-wave vertex displacement."""
    body = pygame.Surface((draw_w + 8, draw_h + 8), pygame.SRCALPHA)

    # Generate deformed rectangle outline with 4 control points per edge
    # Each vertex gets a sine offset based on time and its index
    points = []
    num_points_per_edge = 6
    wobble_amount = 2.0  # pixels of wobble (subtle)

    # If moving, increase wobble
    if abs(self.vx) > 0:
        wobble_amount = 3.0

    # Top edge (left to right)
    for i in range(num_points_per_edge):
        frac = i / (num_points_per_edge - 1)
        px = 4 + frac * draw_w
        py = 4 + math.sin(t * 0.008 + i * 1.2 + self.jiggle_phase) * wobble_amount
        points.append((px, py))

    # Right edge (top to bottom)
    for i in range(1, num_points_per_edge):
        frac = i / (num_points_per_edge - 1)
        px = 4 + draw_w + math.sin(t * 0.009 + i * 1.5 + self.jiggle_phase) * wobble_amount
        py = 4 + frac * draw_h
        points.append((px, py))

    # Bottom edge (right to left)
    for i in range(1, num_points_per_edge):
        frac = 1.0 - i / (num_points_per_edge - 1)
        px = 4 + frac * draw_w
        py = 4 + draw_h + math.sin(t * 0.007 + i * 1.3 + self.jiggle_phase) * wobble_amount
        points.append((px, py))

    # Left edge (bottom to top)
    for i in range(1, num_points_per_edge - 1):
        frac = 1.0 - i / (num_points_per_edge - 1)
        px = 4 + math.sin(t * 0.01 + i * 1.1 + self.jiggle_phase) * wobble_amount
        py = 4 + frac * draw_h
        points.append((px, py))

    # Fill with translucent green
    pygame.draw.polygon(body, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 140), points)

    # Inner highlight (upper half, slightly inset)
    highlight_points = points[:num_points_per_edge + 2]  # top + part of right
    # ... simplified — use a rect for the highlight, it reads fine at game scale
    hl_rect = (8, 8, draw_w - 8, draw_h // 2 - 4)
    pygame.draw.rect(body, (180, 240, 160, 60), hl_rect, border_radius=4)

    # Edge outline
    pygame.draw.polygon(body, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 200), points, 2)

    surf.blit(body, (draw_x - 4, draw_y - 4))
```

**Performance cost:** ~20 points in a polygon = negligible. `pygame.draw.polygon` is a single C call in SDL2. **Budget: 0.1ms/frame.**

**Alternative for sprite-based art:** Once Andrew draws the jello cube sprite sheets, wobble can be done by applying a per-row horizontal offset to the sprite image:

```python
def draw_wobbling_sprite(surf, sprite, x, y, t, wobble_amp=2.0):
    """Draw a sprite with per-row sine wobble (jello jiggle effect)."""
    h = sprite.get_height()
    w = sprite.get_width()
    for row in range(h):
        offset = int(math.sin(t * 0.008 + row * 0.15) * wobble_amp)
        # blit one row at a time with horizontal shift
        surf.blit(sprite, (x + offset, y + row),
                  area=pygame.Rect(0, row, w, 1))
```

**Performance cost:** For a 64px tall sprite, that is 64 blits per frame for the player. On Pi 5, each small blit is ~0.005ms, so ~0.3ms total. Acceptable for one character. **Do NOT use this on every enemy** -- only the player. For enemies, use uniform squash-stretch (what spark.py already does).

### 2.2 Translucency and Light Interaction

**What it looks like:** The jello cube is see-through. You can faintly see the dungeon background through its body. Nearby torch light creates a warm highlight on its surface. The cube has an internal glow.

**Pygame technique — SRCALPHA surfaces:**

The current spark.py already draws the jello body on an SRCALPHA surface with alpha=140. This is correct. To make it feel more like real translucent jello:

```python
# Layer 1: Shadow/dark core (drawn first, darkens the background beneath)
core = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
pygame.draw.rect(core, (20, 80, 15, 80), (4, 4, draw_w - 8, draw_h - 8),
                 border_radius=6)
surf.blit(core, (draw_x, draw_y))

# Layer 2: Main body (translucent green)
body = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
pygame.draw.rect(body, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 130),
                 (0, 0, draw_w, draw_h), border_radius=6)
surf.blit(body, (draw_x, draw_y))

# Layer 3: Specular highlight (top-left, simulates overhead torch)
highlight = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
# Gradient highlight from top-left corner
for i in range(draw_h // 2):
    alpha = int(70 * (1 - i / (draw_h // 2)))
    pygame.draw.line(highlight, (255, 255, 255, alpha),
                     (0, i), (draw_w, i))
# Mask to body shape
pygame.draw.rect(highlight, (0, 0, 0, 0), (0, 0, draw_w, draw_h),
                 border_radius=6)
surf.blit(highlight, (draw_x, draw_y))

# Layer 4: Edge refraction rim (bright green outline, varies with angle)
pygame.draw.rect(surf, (140, 255, 120, 180),
                 (draw_x, draw_y, draw_w, draw_h), 2, border_radius=6)
```

**Dynamic torch interaction:** When the player is near a torch (within 150px), add an amber tint overlay on the side facing the torch:

```python
def apply_torch_highlight(surf, player_x, player_y, player_w, player_h,
                          torch_positions, t):
    """Add warm amber highlight to the jello body side facing a nearby torch."""
    for tx, ty in torch_positions:
        dist = math.hypot(player_x + player_w/2 - tx, player_y + player_h/2 - ty)
        if dist < 200:
            intensity = int(40 * (1 - dist / 200))
            flicker = int(math.sin(t * 0.008 + tx) * 8)
            intensity = max(0, intensity + flicker)
            # Determine which side the torch is on
            glow_surf = pygame.Surface((player_w, player_h), pygame.SRCALPHA)
            if tx < player_x + player_w / 2:
                # Torch is to the left — highlight left edge
                for col in range(player_w // 3):
                    a = int(intensity * (1 - col / (player_w // 3)))
                    pygame.draw.line(glow_surf, (TORCH_AMBER[0], TORCH_AMBER[1],
                                     TORCH_AMBER[2], a), (col, 0), (col, player_h))
            else:
                # Torch is to the right — highlight right edge
                for col in range(player_w // 3):
                    a = int(intensity * (1 - col / (player_w // 3)))
                    x = player_w - 1 - col
                    pygame.draw.line(glow_surf, (TORCH_AMBER[0], TORCH_AMBER[1],
                                     TORCH_AMBER[2], a), (x, 0), (x, player_h))
            surf.blit(glow_surf, (int(player_x), int(player_y)))
```

**Performance cost:** Only triggers when near a torch (usually 0-2 torches in range). ~13 draw.line calls per torch = **0.1ms.** Acceptable.

### 2.3 Squash and Stretch (Enhanced)

**Current state:** spark.py already has spring-based squash (`self.squish` + `self.squish_v`). This works well. Enhancements:

| Trigger | Squash Value | Visual | Already in spark.py? |
|---------|-------------|--------|---------------------|
| Landing from fall | 0.4 | Wide and flat briefly | Yes |
| Ground pound landing | 0.6 | Very flat, dramatic | Yes |
| Jump takeoff | -0.3 | Tall and thin | Yes |
| Jello shot recoil | -0.15 | Slight backward stretch | Yes |
| Walking cycle | +/-0.05 | Subtle bob | No (add) |
| Taking damage | 0.3 rapid oscillation | Shake/ripple | No (add) |
| Collecting item | 0.2 (brief pop) | Satisfaction pop | No (add) |

**Add walking bob:**
```python
# In JelloCube.update(), after movement:
if self.on_ground and abs(self.vx) > 0:
    # Subtle vertical bob synced to movement
    walk_bob = math.sin(self.jiggle_phase * 2) * 0.05
    self.squish += walk_bob * 0.3  # very gentle, spring system handles smoothing
```

**Add damage ripple:**
```python
def take_damage(self, amount):
    self.health -= amount
    # Rapid oscillation: set squish to alternate positive/negative
    self.squish = 0.35
    self.squish_v = -0.8  # high velocity = multiple bounces before settling
    self.damage_flash_timer = 12  # frames of white flash
```

**Performance cost:** Zero additional cost -- just tuning the existing spring values. **Budget: 0.0ms.**

### 2.4 Split Effect (Gooey Stretching Animation)

**What it looks like:** When the player presses Split, the cube stretches into a cross shape, then snaps apart into 4 smaller cubes with gooey strings connecting them that thin out and break. The pieces orbit briefly, then the player controls the main piece while ghost pieces follow.

**Current state:** spark.py has split working with instant appearance of 3 ghost pieces. The upgrade is to add the stretching transition.

**Implementation — Split Animation State Machine:**

```python
# Add to JelloCube.__init__:
self.split_anim_state = "idle"  # "idle", "stretching", "snapping", "split", "reforming"
self.split_anim_timer = 0
SPLIT_STRETCH_FRAMES = 12    # 0.2 seconds
SPLIT_SNAP_FRAMES = 6        # 0.1 seconds
SPLIT_REFORM_FRAMES = 10     # ~0.17 seconds

def split(self):
    if self.split_anim_state != "idle":
        if self.is_split:
            self.split_anim_state = "reforming"
            self.split_anim_timer = SPLIT_REFORM_FRAMES
        return
    self.split_anim_state = "stretching"
    self.split_anim_timer = SPLIT_STRETCH_FRAMES

def update_split_animation(self, vfx):
    if self.split_anim_state == "stretching":
        self.split_anim_timer -= 1
        # Progress 0..1
        progress = 1.0 - (self.split_anim_timer / SPLIT_STRETCH_FRAMES)
        # Draw cross-shaped stretch: widen horizontally and vertically
        self.stretch_x = progress * 20  # pixels of horizontal stretch
        self.stretch_y = progress * 15
        if self.split_anim_timer <= 0:
            self.split_anim_state = "snapping"
            self.split_anim_timer = SPLIT_SNAP_FRAMES
            # Burst particles at the snap point
            cx, cy = self.x + self.w / 2, self.y + self.h / 2
            for _ in range(25):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 5)
                vfx.particles.emit(
                    cx, cy,
                    math.cos(angle) * speed, math.sin(angle) * speed,
                    JELLO_GREEN, 3, 30
                )
            vfx.shake(5)

    elif self.split_anim_state == "snapping":
        self.split_anim_timer -= 1
        if self.split_anim_timer <= 0:
            # Actually split now
            self._do_split()
            self.split_anim_state = "split"

    elif self.split_anim_state == "reforming":
        self.split_anim_timer -= 1
        progress = 1.0 - (self.split_anim_timer / SPLIT_REFORM_FRAMES)
        # Ghost pieces lerp toward main body
        # (draw code uses progress to position pieces)
        if self.split_anim_timer <= 0:
            self._do_unsplit()
            self.split_anim_state = "idle"
            vfx.shake(3)

def draw_split_strings(self, surf, t):
    """Draw gooey strings between pieces during split animation."""
    if self.split_anim_state not in ("stretching", "snapping"):
        return
    cx = self.x + self.w / 2
    cy = self.y + self.h / 2

    if self.split_anim_state == "stretching":
        progress = 1.0 - (self.split_anim_timer / SPLIT_STRETCH_FRAMES)
        offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        for dx, dy in offsets:
            end_x = cx + dx * self.stretch_x * progress
            end_y = cy + dy * self.stretch_y * progress
            # Gooey string: draw a tapered line (thick at center, thin at end)
            mid_x = (cx + end_x) / 2 + math.sin(t * 0.01) * 3
            mid_y = (cy + end_y) / 2 + math.cos(t * 0.012) * 2
            thickness = max(1, int(4 * (1 - progress)))
            color = (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 160)
            # Draw as two line segments through midpoint (creates curve illusion)
            string_surf = pygame.Surface(
                (abs(int(end_x - cx)) + 20, abs(int(end_y - cy)) + 20),
                pygame.SRCALPHA
            )
            # Simplified: just draw direct line with alpha
            pygame.draw.line(surf, color,
                             (int(cx), int(cy)), (int(end_x), int(end_y)),
                             thickness)
```

**Performance cost:** 12-18 frames of 4 lines + 1 particle burst. **Budget: 0.2ms peak, then 0.0ms.**

### 2.5 Items Floating Inside Transparent Body

**What it looks like:** Collected items (jello powder bags, pills, water bottles) are visible floating gently inside the jello cube's translucent body. They bob and rotate slowly.

**Implementation:**

```python
class VisibleInventory:
    """Manages items visible inside the jello body."""

    def __init__(self):
        self.items = []  # list of (sprite_small, phase_offset)

    def add_item(self, item_type):
        """Add an item to the visible inventory."""
        # Use a tiny (12x12 or 16x16) pre-scaled version of the item sprite
        phase = random.uniform(0, math.pi * 2)
        self.items.append((item_type, phase))

    def draw(self, surf, body_x, body_y, body_w, body_h, t):
        """Draw items floating inside the jello body bounds."""
        if not self.items:
            return

        # Distribute items evenly within the body area (inset by 6px)
        count = len(self.items)
        for i, (item_type, phase) in enumerate(self.items):
            # Position: spread across body interior
            slot_x = body_x + 8 + ((body_w - 16) * (i + 0.5) / max(count, 1))
            slot_y = body_y + body_h * 0.5

            # Gentle bob
            bob_y = math.sin(t * 0.003 + phase) * 3
            bob_x = math.cos(t * 0.002 + phase * 1.3) * 2

            # Draw item as a simple colored shape (tiny at body scale)
            # When real sprites exist, blit the pre-scaled 12x12 sprite instead
            item_colors = {
                "jello_powder": (180, 200, 60),
                "water": (100, 160, 255),
                "fire_pill": (255, 120, 40),
                "shrink_pill": (200, 100, 255),
            }
            color = item_colors.get(item_type, (200, 200, 200))
            pos = (int(slot_x + bob_x), int(slot_y + bob_y))

            # Tiny item icon (4x6 rect for powder bag, 3x5 for bottles, etc.)
            pygame.draw.rect(surf, (*color, 180),
                             (pos[0] - 3, pos[1] - 4, 6, 8),
                             border_radius=1)
            # When item sprites are ready, replace with:
            # surf.blit(item_sprite_small, (pos[0] - 6, pos[1] - 6))
```

**Performance cost:** 1-6 tiny rects per frame. **Budget: 0.05ms.**

### 2.6 Jello Shot Projectile Trail (Enhanced)

**Current state:** spark.py has a trail of fading circles behind the projectile. The upgrade adds a gooey, glowing quality.

```python
class JelloProjectile:
    # ... existing code ...

    def draw(self, surf, t):
        # === GOOEY TRAIL ===
        # Draw a connected trail (not just disconnected circles)
        if len(self.trail) >= 2:
            for i in range(1, len(self.trail)):
                x1, y1, _ = self.trail[i - 1]
                x2, y2, _ = self.trail[i]
                progress = i / len(self.trail)
                alpha = int(100 * progress)
                thickness = max(1, int(self.radius * 0.6 * progress))
                pygame.draw.line(surf,
                    (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], alpha),
                    (int(x1), int(y1)), (int(x2), int(y2)),
                    thickness)

        # === GLOW (use cached surface from VFXManager) ===
        fade = self.lifetime / self.max_lifetime
        glow_r = int(self.radius * 2.5)
        # Instead of creating a new surface, use the manager's cached glow
        # vfx.get_glow(glow_r, JELLO_GREEN, int(35 * fade))
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow,
            (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], int(35 * fade)),
            (glow_r, glow_r), glow_r)
        surf.blit(glow, (int(self.x) - glow_r, int(self.y) - glow_r))

        # === MAIN BALL ===
        r = max(3, int(self.radius * fade) + 2)
        pygame.draw.circle(surf, JELLO_GREEN, (int(self.x), int(self.y)), r)

        # === SPECULAR HIGHLIGHT ===
        pygame.draw.circle(surf, (200, 255, 180),
            (int(self.x) - 1, int(self.y) - 2), max(1, r // 3))

        # === DRIPPING PARTICLES (gooey feel) ===
        # Emit 1 drip particle every few frames
        # (handled by caller: vfx.particles.emit(...) with downward vy)
```

**Performance cost:** Replaces existing code with similar cost. The connected line trail is cheaper than multiple circle blits. **Budget: 0.15ms per active projectile.**

### 2.7 Damage Feedback

**What it looks like:** When the jello cube takes a hit: (1) the entire body flashes white for 3 frames, (2) the body oscillates rapidly (squish spring), (3) a ripple wave passes through the body, (4) hit particles spray out.

```python
# In JelloCube:
def take_damage(self, amount, hit_direction=0):
    """React to taking damage. hit_direction: -1=left, 0=center, 1=right."""
    self.health -= amount
    self.damage_flash = 10        # frames of flash
    self.squish = 0.35
    self.squish_v = -0.9          # violent oscillation
    self.hit_stun = 8             # frames of no player input
    self.ripple_timer = 15
    self.ripple_origin = 0.0 if hit_direction == 0 else (0.0 if hit_direction < 0 else 1.0)

    # Knockback
    self.vx = -hit_direction * 6
    self.vy = -4

    # Request screen effects from VFX manager
    # vfx.shake(6)
    # vfx.flash((255, 50, 50), duration=4)  # brief red flash

def draw_damage_flash(self, surf, draw_x, draw_y, draw_w, draw_h):
    """Overlay white flash on the jello body."""
    if self.damage_flash > 0:
        self.damage_flash -= 1
        # Every other frame = strobe effect
        if self.damage_flash % 2 == 0:
            flash = pygame.Surface((draw_w, draw_h), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 160))
            surf.blit(flash, (draw_x, draw_y))

def draw_ripple(self, surf, draw_x, draw_y, draw_w, draw_h, t):
    """A horizontal ripple wave that passes through the body after damage."""
    if self.ripple_timer > 0:
        self.ripple_timer -= 1
        progress = 1.0 - (self.ripple_timer / 15)
        ripple_y = draw_y + int(draw_h * progress)
        # Draw a bright horizontal line that moves downward through the body
        alpha = int(120 * (1 - progress))
        pygame.draw.line(surf,
            (255, 255, 255, alpha),
            (draw_x, ripple_y), (draw_x + draw_w, ripple_y), 2)
```

**Performance cost:** Only during damage (rare, brief). **Budget: 0.05ms for ~10 frames.**

---

## 3. Environmental Effects

### 3.1 Dynamic Torchlight with Flickering and Light Cones

**What it looks like:** Each wall torch casts a warm cone of light downward and outward. The light flickers irregularly (not a smooth sine wave). The area outside torch light is significantly darker, creating pools of safety and danger.

**Current state:** spark.py draws a small circular glow behind each torch. The upgrade is (a) cone-shaped light, (b) irregular flicker, and (c) darkness masking.

**Implementation — Darkness Overlay with Light Cutouts:**

This is the single most impactful environmental effect. The technique: draw the entire scene normally, then overlay a near-black surface with holes punched where the lights are.

```python
class LightingSystem:
    """Subtractive darkness with additive light sources."""

    def __init__(self, screen_w, screen_h):
        # The darkness layer — drawn OVER the scene
        self.darkness = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        # Ambient darkness level (0=bright, 255=pitch black)
        self.ambient = 180  # quite dark — dungeon feel
        # Light sources
        self.lights = []  # list of (x, y, radius, color, flicker_seed)

        # Pre-render radial gradient for light circles (one per radius tier)
        self.light_textures = {}

    def _get_light_texture(self, radius):
        """Get or create a pre-rendered radial gradient light texture."""
        # Quantize radius to nearest 10 to limit cache entries
        r_key = (radius // 10) * 10 + 10
        if r_key not in self.light_textures:
            size = r_key * 2
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            # Radial gradient: bright center fading to transparent edge
            for ring in range(r_key, 0, -2):
                alpha = int(255 * (ring / r_key))
                pygame.draw.circle(surf, (0, 0, 0, alpha),
                                   (r_key, r_key), ring)
            self.light_textures[r_key] = surf
        return self.light_textures[r_key], (radius // 10) * 10 + 10

    def update(self, t):
        """Update flicker values for all lights."""
        for i, (x, y, radius, color, seed) in enumerate(self.lights):
            # Irregular flicker: combine two sine waves at different frequencies
            flicker = (math.sin(t * 0.007 + seed * 3.7) * 0.3 +
                       math.sin(t * 0.013 + seed * 2.1) * 0.15 +
                       math.sin(t * 0.031 + seed * 5.3) * 0.1)
            # Occasional bigger dip (simulating wind)
            if math.sin(t * 0.002 + seed * 7.1) > 0.85:
                flicker -= 0.3
            self.lights[i] = (x, y, radius, color, seed, flicker)

    def draw(self, target, camera_x=0, camera_y=0):
        """Draw the darkness overlay with light holes."""
        self.darkness.fill((0, 0, 0, self.ambient))

        for light in self.lights:
            x, y, radius, color, seed = light[:5]
            flicker = light[5] if len(light) > 5 else 0

            # Adjust radius by flicker
            r = int(radius * (1.0 + flicker * 0.15))

            # Get cached light texture
            tex, r_key = self._get_light_texture(r)

            # Blit the light texture onto the darkness layer using BLEND_RGBA_SUB
            # This "subtracts" darkness where the light is
            screen_x = int(x - r_key - camera_x)
            screen_y = int(y - r_key - camera_y)
            self.darkness.blit(tex, (screen_x, screen_y),
                               special_flags=pygame.BLEND_RGBA_SUB)

        # Also punch a small light around the player (jello glow)
        # Player light is added by the caller

        target.blit(self.darkness, (0, 0))
```

**CRITICAL PERFORMANCE NOTE:** This creates ONE full-screen SRCALPHA surface. On Pi 5 at 1280x720, a full-screen alpha blit costs approximately **1.5-2ms**. This is the most expensive single operation in the entire VFX system. It is worth it -- the darkness/light effect transforms the game from "colored rectangles on a background" to "atmospheric dungeon."

**Optimization:** Only rebuild the darkness surface when lights change (which is every frame due to flicker). However, the fill + blit pattern is already quite efficient. If it becomes too slow, reduce the darkness surface to half resolution (640x360) and scale up with `pygame.transform.scale` -- this halves the cost.

```python
# Half-resolution fallback:
self.darkness_half = pygame.Surface((screen_w // 2, screen_h // 2), pygame.SRCALPHA)
# ... do all light operations at half size ...
scaled = pygame.transform.scale(self.darkness_half, (screen_w, screen_h))
target.blit(scaled, (0, 0))
```

**Budget: 2.0ms full resolution, 1.2ms half resolution.**

### 3.2 Particle Dust Motes in Light Beams

**What it looks like:** Tiny golden specks float lazily in the air where torchlight reaches. They drift slowly, catch the light, and fade. Outside the light, they are invisible.

**Implementation:** Already partially in spark.py as ambient particles. The upgrade: only show particles that are within a light source's radius.

```python
def emit_dust_motes(vfx, light_positions, t):
    """Spawn dust motes near light sources."""
    if random.random() < 0.08:  # ~5 per second
        # Pick a random light
        if not light_positions:
            return
        lx, ly, lr = random.choice(light_positions)
        # Spawn within the light radius
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(0, lr * 0.7)
        px = lx + math.cos(angle) * dist
        py = ly + math.sin(angle) * dist
        vfx.particles.emit(
            px, py,
            random.uniform(-0.15, 0.15),   # very slow horizontal drift
            random.uniform(-0.3, -0.1),     # slow upward float
            TORCH_AMBER,
            random.randint(1, 2),
            random.randint(90, 160)
        )
```

**Performance cost:** Uses the existing particle pool. 5 new particles/second, ~15 alive at once. **Budget: included in particle pool draw cost.**

### 3.3 Dripping Water from Castle Ceilings

**What it looks like:** At specific points on the ceiling, a water droplet slowly forms (grows), then falls as a fast streak, and splashes on the ground with a tiny ring of droplets.

```python
class WaterDrip:
    """A single drip point on the ceiling."""

    def __init__(self, x, ceiling_y, ground_y):
        self.x = x
        self.ceiling_y = ceiling_y
        self.ground_y = ground_y
        self.state = "forming"      # "forming", "falling", "splash", "idle"
        self.timer = random.randint(60, 180)  # random delay before first drip
        self.drop_y = ceiling_y
        self.drop_size = 0
        self.splash_timer = 0

    def update(self, vfx):
        if self.state == "idle":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "forming"
                self.timer = 45  # ~0.75 seconds to form

        elif self.state == "forming":
            self.timer -= 1
            self.drop_size = 3 * (1 - self.timer / 45)
            self.drop_y = self.ceiling_y + self.drop_size
            if self.timer <= 0:
                self.state = "falling"
                self.drop_size = 3

        elif self.state == "falling":
            self.drop_y += 8  # fast fall
            if self.drop_y >= self.ground_y:
                self.state = "splash"
                self.splash_timer = 10
                # Splash particles
                for _ in range(4):
                    vfx.particles.emit(
                        self.x + random.uniform(-3, 3),
                        self.ground_y,
                        random.uniform(-1.5, 1.5),
                        random.uniform(-2, -0.5),
                        (120, 160, 220),  # pale blue
                        1, 15
                    )

        elif self.state == "splash":
            self.splash_timer -= 1
            if self.splash_timer <= 0:
                self.state = "idle"
                self.timer = random.randint(120, 300)  # 2-5 sec before next drip

    def draw(self, surf):
        if self.state == "forming":
            # Growing droplet hanging from ceiling
            r = max(1, int(self.drop_size))
            pygame.draw.circle(surf, (100, 150, 220),
                               (int(self.x), int(self.drop_y)), r)
            # Thin line connecting to ceiling
            pygame.draw.line(surf, (80, 130, 200),
                             (int(self.x), self.ceiling_y),
                             (int(self.x), int(self.drop_y) - r), 1)

        elif self.state == "falling":
            # Streak
            pygame.draw.line(surf, (120, 170, 240),
                             (int(self.x), int(self.drop_y)),
                             (int(self.x), int(self.drop_y) - 12), 2)

        elif self.state == "splash":
            # Small expanding ring on ground
            r = int(6 * (1 - self.splash_timer / 10))
            alpha = int(150 * (self.splash_timer / 10))
            splash_s = pygame.Surface((r * 2 + 4, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(splash_s, (120, 170, 240, alpha),
                                (0, 0, r * 2 + 4, 6), 1)
            surf.blit(splash_s, (int(self.x) - r - 2, self.ground_y - 3))
```

**Performance cost:** 1 circle or 1 line per drip point per frame. Maybe 3-5 drip points per level. **Budget: 0.05ms.**

### 3.4 Fog/Mist Layers with Parallax

**What it looks like:** Semi-transparent white-gray wisps drift slowly across the lower portion of the screen, in front of the background but behind the player. Multiple layers at different speeds create depth.

**Implementation — Scrolling Pre-Rendered Fog Strips:**

```python
class FogLayer:
    """A single horizontal fog strip that scrolls continuously."""

    def __init__(self, y, screen_w, height=60, alpha=25, speed=0.3, color=(200, 200, 220)):
        self.y = y
        self.speed = speed
        self.offset = random.uniform(0, screen_w)
        self.color = color
        self.alpha = alpha

        # Pre-render a wide fog strip (2x screen width for seamless scroll)
        self.strip = pygame.Surface((screen_w * 2, height), pygame.SRCALPHA)
        # Draw soft blobs across the strip
        for bx in range(0, screen_w * 2, 30):
            blob_w = random.randint(40, 100)
            blob_h = random.randint(15, height - 5)
            blob_y = random.randint(0, height - blob_h)
            blob_alpha = random.randint(alpha // 2, alpha)
            blob_surf = pygame.Surface((blob_w, blob_h), pygame.SRCALPHA)
            pygame.draw.ellipse(blob_surf,
                (*color[:3], blob_alpha), (0, 0, blob_w, blob_h))
            self.strip.blit(blob_surf, (bx, blob_y))

    def update(self):
        self.offset += self.speed
        if self.offset > self.strip.get_width() // 2:
            self.offset -= self.strip.get_width() // 2

    def draw(self, surf, camera_x=0):
        # Blit the strip, offset for scrolling (wraps seamlessly)
        x = int(-self.offset - camera_x * self.speed * 0.3)
        surf.blit(self.strip, (x, self.y))


# Usage: create 2-3 fog layers at different depths
fog_layers = [
    FogLayer(y=GROUND_Y - 40, screen_w=SCREEN_W, height=50, alpha=20, speed=0.2),
    FogLayer(y=GROUND_Y - 80, screen_w=SCREEN_W, height=40, alpha=15, speed=0.4),
    FogLayer(y=GROUND_Y - 20, screen_w=SCREEN_W, height=30, alpha=30, speed=0.1),
]
```

**Performance cost:** Each fog layer is a single blit of a pre-rendered surface. **Budget: 0.3ms for 3 layers.** The pre-render happens once at level load.

### 3.5 Vine/Moss Growth Animation

**What it looks like:** Vines slowly creep down from the ceiling over time (purely cosmetic). When the player walks past a vine, it sways briefly.

**Current state:** spark.py draws static vines with small sine offsets. The upgrade adds sway-on-proximity.

```python
class Vine:
    def __init__(self, x, max_length=200):
        self.x = x
        self.max_length = max_length
        self.sway = 0.0         # current sway offset
        self.sway_v = 0.0       # sway velocity
        self.segments = max_length // 12

    def disturb(self, intensity=2.0):
        """Called when player passes nearby."""
        self.sway_v += intensity

    def update(self, player_x, player_dist_threshold=60):
        # Spring physics for sway
        self.sway_v += (-self.sway) * 0.08
        self.sway_v *= 0.92
        self.sway += self.sway_v

        # Auto-disturb when player is close
        if abs(player_x - self.x) < player_dist_threshold:
            self.sway_v += random.uniform(-0.3, 0.3)

    def draw(self, surf, t):
        for i in range(self.segments):
            vy = i * 12
            # Each segment sways more than the one above (pendulum)
            sway_factor = (i / self.segments) ** 1.5
            vx_offset = (self.sway * sway_factor +
                         math.sin(vy * 0.08 + t * 0.001) * 3)
            pygame.draw.circle(surf, VINE_GREEN,
                               (int(self.x + vx_offset), vy), 3)
            # Occasional leaf
            if i % 3 == 0:
                leaf_side = 1 if i % 2 == 0 else -1
                pygame.draw.circle(surf, (50, 120, 40),
                    (int(self.x + vx_offset + leaf_side * 5), vy), 2)
```

**Performance cost:** ~16 circles per vine, ~4 vines visible = 64 circles. **Budget: 0.1ms.**

### 3.6 Glowing Door Effect (Level Transitions)

**What it looks like:** The exit door pulses with warm golden light. Light rays emanate outward. Particles drift upward from the door frame. As the player approaches, the glow intensifies.

```python
class GlowingDoor:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.base_glow_radius = 80

        # Pre-render the door frame
        self.frame_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
        pygame.draw.rect(self.frame_surf, (TORCH_AMBER[0], TORCH_AMBER[1],
                         TORCH_AMBER[2], 100), (10, 10, w, h), border_radius=4)
        pygame.draw.rect(self.frame_surf, (255, 220, 120, 180),
                         (10, 10, w, h), 3, border_radius=4)

    def draw(self, surf, player_x, player_y, t, vfx):
        # Distance-based intensity
        dist = math.hypot(player_x - (self.x + self.w/2),
                          player_y - (self.y + self.h/2))
        proximity = max(0, 1 - dist / 300)  # 0 at 300px away, 1 at door

        # Pulsing glow
        pulse = 0.8 + math.sin(t * 0.004) * 0.2
        glow_r = int(self.base_glow_radius * pulse * (1 + proximity * 0.5))

        # Outer glow (cached)
        glow = vfx.get_glow(glow_r, TORCH_AMBER, int(25 + proximity * 30))
        surf.blit(glow, (int(self.x + self.w/2 - glow_r),
                         int(self.y + self.h/2 - glow_r)))

        # Door frame
        surf.blit(self.frame_surf, (self.x - 10, self.y - 10))

        # Interior light (bright rectangle)
        interior_alpha = int(60 + math.sin(t * 0.005) * 20 + proximity * 80)
        interior = pygame.Surface((self.w - 6, self.h - 6), pygame.SRCALPHA)
        interior.fill((255, 240, 200, interior_alpha))
        surf.blit(interior, (self.x + 3, self.y + 3))

        # Light rays (4 diagonal lines emanating from center)
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        for i in range(4):
            angle = t * 0.001 + i * (math.pi / 2)
            ray_len = 30 + math.sin(t * 0.006 + i) * 10
            ex = cx + math.cos(angle) * ray_len
            ey = cy + math.sin(angle) * ray_len
            alpha = int(60 * pulse)
            pygame.draw.line(surf, (255, 240, 200, alpha),
                             (int(cx), int(cy)), (int(ex), int(ey)), 1)

        # Upward particles (spawn a few per second)
        if random.random() < 0.06 + proximity * 0.08:
            vfx.particles.emit(
                self.x + random.uniform(0, self.w),
                self.y + self.h,
                random.uniform(-0.3, 0.3),
                random.uniform(-1.5, -0.5),
                (255, 220, 120),
                random.randint(1, 2),
                random.randint(30, 60)
            )
```

**Performance cost:** 1 cached glow blit + 1 rect + 4 lines + occasional particles. **Budget: 0.2ms.**

### 3.7 Crumbling/Falling Debris

**What it looks like:** When the player ground-pounds, nearby loose stone chunks shake, then fall. Small stone fragments scatter during screen shake events.

```python
class DebrisChunk:
    """A small stone fragment that falls with gravity and bounces once."""

    def __init__(self, x, y, size=None):
        self.x = x
        self.y = y
        self.size = size or random.randint(3, 7)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1)
        self.gravity = 0.4
        self.lifetime = 60
        self.bounced = False
        self.color = (
            WARM_STONE[0] + random.randint(-10, 10),
            WARM_STONE[1] + random.randint(-10, 10),
            WARM_STONE[2] + random.randint(-10, 10),
        )
        self.rotation = random.uniform(0, math.pi * 2)
        self.rot_speed = random.uniform(-0.2, 0.2)

    def update(self, ground_y):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed
        self.lifetime -= 1

        # Bounce on ground
        if self.y > ground_y and not self.bounced:
            self.y = ground_y
            self.vy = -self.vy * 0.3
            self.vx *= 0.5
            self.bounced = True

        return self.lifetime > 0

    def draw(self, surf):
        fade = min(1.0, self.lifetime / 20)  # fade in last 20 frames
        alpha = int(255 * fade)
        # Draw as a small rotated rectangle
        s = self.size
        points = []
        for corner_angle in [0.5, 1.8, 3.5, 5.0]:  # irregular quadrilateral
            a = self.rotation + corner_angle
            px = self.x + math.cos(a) * s
            py = self.y + math.sin(a) * s
            points.append((int(px), int(py)))
        pygame.draw.polygon(surf, (*self.color, alpha), points)
```

**Performance cost:** Spawned in bursts of 5-10, last ~1 second. **Budget: 0.1ms peak.**

---

## 4. Combat VFX

### 4.1 Ground Pound Shockwave (Enhanced)

**Current state:** spark.py already has a Shockwave class (expanding ellipse ring) + screen shake + dust particles. This is solid. Enhancements:

```python
class Shockwave:
    """Expanding ring from ground pound impact. Enhanced with dust wave."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 100    # slightly larger than current 80
        self.lifetime = 18
        self.max_lifetime = 18
        # Dust wave — secondary expanding ring at ground level
        self.dust_radius = 0
        self.dust_max = 120

    def update(self):
        self.radius += (self.max_radius - self.radius) * 0.22
        self.dust_radius += (self.dust_max - self.dust_radius) * 0.18
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surf):
        fade = self.lifetime / self.max_lifetime

        # === PRIMARY RING (bright amber) ===
        alpha = int(200 * fade)
        width = max(1, int(3 * fade))
        ring_w = int(self.radius * 2) + 4
        ring_h = int(self.radius * 0.4) + 4
        ring = pygame.Surface((ring_w, ring_h), pygame.SRCALPHA)
        pygame.draw.ellipse(ring,
            (TORCH_AMBER[0], TORCH_AMBER[1], TORCH_AMBER[2], alpha),
            (0, 0, ring_w, ring_h), width)
        surf.blit(ring, (int(self.x - ring_w / 2), int(self.y - ring_h / 2)))

        # === SECONDARY DUST RING (wider, fainter, brown) ===
        if fade > 0.3:
            dust_alpha = int(80 * (fade - 0.3) / 0.7)
            dust_w = int(self.dust_radius * 2) + 4
            dust_h = int(self.dust_radius * 0.25) + 4
            dust = pygame.Surface((dust_w, dust_h), pygame.SRCALPHA)
            pygame.draw.ellipse(dust, (120, 100, 80, dust_alpha),
                                (0, 0, dust_w, dust_h), 2)
            surf.blit(dust, (int(self.x - dust_w / 2),
                             int(self.y - dust_h / 2 + 4)))

        # === CENTER FLASH (first 4 frames only) ===
        if fade > 0.75:
            flash_r = int(12 * (fade - 0.75) / 0.25)
            flash = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash, (255, 255, 220, int(120 * fade)),
                               (flash_r, flash_r), flash_r)
            surf.blit(flash, (int(self.x - flash_r), int(self.y - flash_r)))
```

**Also trigger on impact:**
- `vfx.shake(8)` -- screen shake
- 25 particles (already in spark.py)
- 5-8 `DebrisChunk` objects from nearby ceiling
- Camera freeze-frame: pause game for 2 frames (hit-stop) for dramatic impact

**Hit-stop implementation:**
```python
# In main game loop:
if self.hitstop_frames > 0:
    self.hitstop_frames -= 1
    # Skip update, still draw (gives a freeze-frame effect)
    pygame.display.flip()
    continue
```

**Performance cost:** Same as current shockwave + 1 extra ellipse. **Budget: 0.15ms for ~18 frames.**

### 4.2 Enemy Hit Reactions

**What it looks like:** When an enemy is hit by a jello shot: (1) flash white for 4 frames, (2) knockback slide, (3) tiny particle burst from the impact point, (4) brief hit-stop (1-2 frames).

```python
class EnemyHitReaction:
    """Mixin or component for enemy hit visual feedback."""

    def on_hit(self, damage, hit_x, hit_y, knockback_dir, vfx):
        self.flash_timer = 6
        self.knockback_vx = knockback_dir * 5
        self.hit_stun = 10

        # Particle burst from impact point
        for _ in range(8):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            vfx.particles.emit(
                hit_x, hit_y,
                math.cos(angle) * speed + knockback_dir * 2,
                math.sin(angle) * speed,
                self.hit_particle_color,  # e.g. (200, 100, 255) for purple warriors
                2, 20
            )

        # Hit-stop
        vfx.hitstop(2)

    def draw_flash_overlay(self, surf, sprite_rect):
        """Draw white overlay on enemy sprite during flash."""
        if self.flash_timer > 0:
            self.flash_timer -= 1
            if self.flash_timer % 2 == 0:
                flash = pygame.Surface(
                    (sprite_rect.width, sprite_rect.height), pygame.SRCALPHA)
                flash.fill((255, 255, 255, 180))
                surf.blit(flash, sprite_rect)
```

**Performance cost:** Only during hits (burst of 8 particles, brief flash). **Budget: 0.05ms peak.**

### 4.3 Enemy Death Animations

**Sanitizer Warrior Death (Purple Goo Explosion):**

When a Sanitizer Warrior dies, they should explode into purple goo with their equipment scattering.

```python
def sanitizer_warrior_death(x, y, w, h, vfx):
    """Trigger the Sanitizer Warrior death effect."""
    cx, cy = x + w / 2, y + h / 2

    # === PHASE 1: Flash white (4 frames) ===
    vfx.flash((200, 100, 255), duration=4)

    # === PHASE 2: Purple goo explosion (30+ particles) ===
    for _ in range(35):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 7)
        # Purple goo colors
        purple = random.choice([
            (122, 31, 162),   # dark purple
            (156, 39, 176),   # medium purple
            (206, 147, 216),  # light purple
        ])
        vfx.particles.emit(
            cx + random.uniform(-w/3, w/3),
            cy + random.uniform(-h/3, h/3),
            math.cos(angle) * speed,
            math.sin(angle) * speed - 2,  # bias upward
            purple,
            random.randint(3, 6),
            random.randint(30, 60)
        )

    # === PHASE 3: Equipment scatter ===
    # Spawn 3 physics objects: hat, weapon, bottle
    # These are small sprites that fly out, bounce, then fade
    equipment = [
        {"name": "hat",    "vx": -3, "vy": -8, "rot_speed": 0.15},
        {"name": "weapon", "vx":  4, "vy": -5, "rot_speed": 0.08},
        {"name": "bottle", "vx":  1, "vy": -9, "rot_speed": 0.12},
    ]
    # Return these as ScatterItem objects for the level to track
    return [ScatterItem(cx, cy, eq) for eq in equipment]

    # === PHASE 4: Purple puddle (persistent) ===
    # After particles settle (~1 second), spawn a purple puddle decal
    # on the ground at the death location. This uses dropped-items-in-puddle.png
    # reference art, or a simple purple ellipse:
    # puddle = PurplePuddle(cx, ground_y, w * 1.5)

    vfx.shake(4)
    vfx.hitstop(3)


class ScatterItem:
    """Equipment piece that flies out from a dead enemy."""

    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.vx = config["vx"] + random.uniform(-1, 1)
        self.vy = config["vy"]
        self.rotation = 0
        self.rot_speed = config["rot_speed"]
        self.gravity = 0.5
        self.lifetime = 90  # 1.5 seconds
        self.name = config["name"]
        self.bounced = False
        # Placeholder colors until real sprites
        self.colors = {
            "hat": (158, 158, 158),
            "weapon": (117, 117, 117),
            "bottle": (176, 190, 197),
        }

    def update(self, ground_y):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rot_speed
        self.lifetime -= 1
        if self.y > ground_y and not self.bounced:
            self.y = ground_y
            self.vy = -self.vy * 0.25
            self.vx *= 0.4
            self.rot_speed *= 0.3
            self.bounced = True
        return self.lifetime > 0

    def draw(self, surf):
        fade = min(1.0, self.lifetime / 30)
        alpha = int(255 * fade)
        color = self.colors.get(self.name, (150, 150, 150))
        # Simple rotating rectangle placeholder
        size = 8 if self.name == "hat" else 12
        points = []
        for i in range(4):
            a = self.rotation + i * (math.pi / 2)
            points.append((
                int(self.x + math.cos(a) * size),
                int(self.y + math.sin(a) * size)
            ))
        pygame.draw.polygon(surf, (*color, alpha), points)
```

**Performance cost:** 35 particles (from pool) + 3 scatter items for ~90 frames. **Budget: 0.3ms peak, decays to 0.**

### 4.4 Boss Entrance Effects

**What it looks like:** The screen darkens. The camera slowly zooms in. Two glowing eyes appear in the darkness. Then dramatic lighting reveals the boss. Title text slams onto the screen.

```python
class BossIntro:
    """Scripted sequence for boss entrance. Takes control of camera and lighting."""

    def __init__(self, boss_x, boss_y, boss_name, duration=180):
        self.boss_x = boss_x
        self.boss_y = boss_y
        self.boss_name = boss_name
        self.duration = duration
        self.timer = duration
        self.active = True

    def update(self, vfx, lighting):
        if not self.active:
            return
        self.timer -= 1
        progress = 1 - (self.timer / self.duration)

        if progress < 0.3:
            # Phase 1: Darken the screen
            lighting.ambient = int(180 + (255 - 180) * (progress / 0.3))
            vfx.zoom_to(1.15, speed=0.02)  # slow zoom in

        elif progress < 0.5:
            # Phase 2: Two glowing eyes appear
            pass  # draw code handles this based on progress

        elif progress < 0.8:
            # Phase 3: Dramatic light reveal — new light source on boss
            local_progress = (progress - 0.5) / 0.3
            lighting.ambient = int(255 - (255 - 160) * local_progress)
            # Add boss light
            boss_light_radius = int(120 * local_progress)
            # lighting.add_temp_light(self.boss_x, self.boss_y, boss_light_radius)

        else:
            # Phase 4: Title slam + camera returns to normal
            vfx.zoom_to(1.0, speed=0.06)
            if self.timer <= 0:
                self.active = False

    def draw(self, surf, t):
        if not self.active:
            return
        progress = 1 - (self.timer / self.duration)

        # Glowing eyes (phase 2+)
        if 0.2 < progress < 0.7:
            eye_alpha = int(255 * min(1, (progress - 0.2) / 0.15))
            eye_size = 6
            eye_spacing = 20
            ey = self.boss_y - 10
            for ex_off in [-eye_spacing / 2, eye_spacing / 2]:
                # Glow
                glow = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 50, 50, eye_alpha // 3), (15, 15), 15)
                surf.blit(glow, (int(self.boss_x + ex_off - 15), int(ey - 15)))
                # Eye
                pygame.draw.circle(surf, (255, 50 + int(50 * math.sin(t * 0.01)), 50),
                                   (int(self.boss_x + ex_off), int(ey)), eye_size)

        # Boss name title (phase 4)
        if progress > 0.75:
            title_progress = (progress - 0.75) / 0.25
            # Slam effect: starts large, snaps to final size
            scale = 2.0 - title_progress * 1.0  # 2x -> 1x
            font_size = int(48 * scale)
            font = pygame.font.Font(None, max(20, font_size))
            text = font.render(self.boss_name, True, (255, 220, 120))
            rect = text.get_rect(center=(surf.get_width() // 2,
                                         surf.get_height() // 2 + 80))
            # Background bar
            if title_progress > 0.3:
                bar_alpha = int(180 * min(1, (title_progress - 0.3) / 0.3))
                bar = pygame.Surface((rect.width + 40, rect.height + 16), pygame.SRCALPHA)
                bar.fill((0, 0, 0, bar_alpha))
                surf.blit(bar, (rect.x - 20, rect.y - 8))
            surf.blit(text, rect)
```

**Performance cost:** Scripted sequence, max 3 seconds. Most cost is in the lighting ambient change (already part of lighting system). **Budget: 0.3ms during intro.**

### 4.5 Damage Numbers

**What it looks like:** When the player or an enemy takes damage, a number pops up, floats upward, and fades. Color indicates type: red for damage taken, green for healing, amber for jello powder collected.

```python
class DamageNumber:
    """A floating damage/heal number that pops up and fades."""

    # Class-level font cache
    _font = None

    def __init__(self, x, y, value, color=(255, 80, 80)):
        self.x = x + random.uniform(-10, 10)
        self.y = y
        self.vy = -3  # initial upward velocity
        self.value = value
        self.color = color
        self.lifetime = 40
        self.max_lifetime = 40
        self.scale = 1.5  # starts bigger, shrinks to 1.0

        if DamageNumber._font is None:
            DamageNumber._font = pygame.font.Font(None, 24)

        # Pre-render the text
        self.text_surf = DamageNumber._font.render(
            str(value), True, color)

    def update(self):
        self.y += self.vy
        self.vy *= 0.92  # decelerate
        self.lifetime -= 1
        self.scale = max(1.0, self.scale - 0.03)
        return self.lifetime > 0

    def draw(self, surf):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.text_surf.set_alpha(alpha)
        rect = self.text_surf.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(self.text_surf, rect)
```

**Performance cost:** Pre-rendered text, single blit. **Budget: 0.02ms per active number.**

### 4.6 Stealth Detection Indicators (? and !)

**What it looks like:** When an enemy becomes suspicious, a "?" fades in above their head, growing from small to full size. When they spot the player, the "?" snaps to a "!" with a brief dramatic zoom pulse and the screen edges briefly tint red.

```python
class DetectionIndicator:
    """BotW-style ? and ! enemy awareness indicators."""

    _font = None

    def __init__(self):
        if DetectionIndicator._font is None:
            DetectionIndicator._font = pygame.font.Font(None, 36)
        self.state = "unaware"   # "unaware", "suspicious", "alert"
        self.timer = 0
        self.alert_flash = 0

    def set_suspicious(self):
        if self.state == "unaware":
            self.state = "suspicious"
            self.timer = 0

    def set_alert(self, vfx):
        if self.state != "alert":
            self.state = "alert"
            self.timer = 0
            self.alert_flash = 12
            vfx.shake(3)
            # Brief red edge vignette
            vfx.flash((255, 50, 50), duration=6)

    def set_unaware(self):
        self.state = "unaware"
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.alert_flash > 0:
            self.alert_flash -= 1

    def draw(self, surf, enemy_x, enemy_y):
        if self.state == "unaware":
            return

        above_y = enemy_y - 30

        if self.state == "suspicious":
            # "?" fades in and bobs
            progress = min(1.0, self.timer / 20)
            alpha = int(200 * progress)
            scale = 0.5 + 0.5 * progress
            bob = math.sin(self.timer * 0.1) * 3

            text = self._font.render("?", True, (255, 255, 100))
            if scale != 1.0:
                w = int(text.get_width() * scale)
                h = int(text.get_height() * scale)
                text = pygame.transform.scale(text, (max(1, w), max(1, h)))
            text.set_alpha(alpha)
            rect = text.get_rect(center=(int(enemy_x), int(above_y + bob)))
            surf.blit(text, rect)

        elif self.state == "alert":
            # "!" with slam effect
            if self.timer < 6:
                # Slam: starts 2x size, snaps to 1x
                scale = 2.0 - (self.timer / 6)
            else:
                scale = 1.0

            text = self._font.render("!", True, (255, 60, 60))
            w = int(text.get_width() * scale)
            h = int(text.get_height() * scale)
            text = pygame.transform.scale(text, (max(1, w), max(1, h)))
            rect = text.get_rect(center=(int(enemy_x), int(above_y)))

            # Red glow behind !
            if self.alert_flash > 0:
                glow = pygame.Surface((40, 40), pygame.SRCALPHA)
                ga = int(100 * (self.alert_flash / 12))
                pygame.draw.circle(glow, (255, 50, 50, ga), (20, 20), 20)
                surf.blit(glow, (int(enemy_x) - 20, int(above_y) - 20))

            surf.blit(text, rect)
```

**Performance cost:** 1 text render + optional glow per aware enemy. **Budget: 0.05ms per enemy.**

---

## 5. UI/HUD Effects

### 5.1 Jello Health Bar

**What it looks like:** The health bar itself looks like a strip of jello. Its surface wobbles. When health drops, the lost portion jiggles away. When health is gained, it bulges momentarily.

```python
class JelloHealthBar:
    """A health bar that wobbles and jiggles like jello."""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.display_health = 1.0   # what is visually shown (lerps to target)
        self.target_health = 1.0    # actual health ratio
        self.wobble_phase = 0
        self.jiggle_v = 0           # velocity for jiggle spring
        self.jiggle = 0             # current jiggle offset

    def set_health(self, ratio):
        old = self.target_health
        self.target_health = max(0, min(1, ratio))
        if self.target_health < old:
            self.jiggle_v = 3       # losing health = big jiggle
        elif self.target_health > old:
            self.jiggle_v = -2      # gaining health = pop outward

    def update(self):
        # Smooth lerp toward target
        self.display_health += (self.target_health - self.display_health) * 0.08
        # Wobble
        self.wobble_phase += 0.06
        # Jiggle spring
        self.jiggle_v += (-self.jiggle) * 0.2
        self.jiggle_v *= 0.75
        self.jiggle += self.jiggle_v

    def draw(self, surf, t):
        # Background (dark)
        pygame.draw.rect(surf, (30, 30, 50),
                         (self.x - 1, self.y - 1, self.width + 2, self.height + 2),
                         border_radius=4)

        # Health fill with wobbly top edge
        fill_w = int(self.width * self.display_health)
        if fill_w > 2:
            fill_surf = pygame.Surface((fill_w, self.height + 6), pygame.SRCALPHA)

            # Build wobbly polygon for the fill
            points = []
            # Bottom edge (flat)
            points.append((0, self.height + 3))
            points.append((fill_w, self.height + 3))
            # Top edge (wobbly)
            num_top_points = max(3, fill_w // 8)
            for i in range(num_top_points, -1, -1):
                px = fill_w * (i / num_top_points)
                wobble = math.sin(self.wobble_phase + i * 0.8) * 1.5
                wobble += self.jiggle * (1 - abs(i / num_top_points - 0.5) * 2)
                py = 3 + wobble
                points.append((px, py))

            # Color based on health level
            if self.display_health > 0.5:
                color = JELLO_GREEN
            elif self.display_health > 0.25:
                color = TORCH_AMBER
            else:
                color = EMBER

            pygame.draw.polygon(fill_surf, (*color[:3], 180), points)

            # Highlight on top edge
            for i in range(num_top_points):
                px = fill_w * (i / num_top_points)
                wobble = math.sin(self.wobble_phase + i * 0.8) * 1.5
                py = 3 + wobble + self.jiggle * (1 - abs(i / num_top_points - 0.5) * 2)
                next_px = fill_w * ((i + 1) / num_top_points)
                next_wobble = math.sin(self.wobble_phase + (i + 1) * 0.8) * 1.5
                next_py = 3 + next_wobble
                pygame.draw.line(fill_surf, (200, 255, 180, 140),
                                 (int(px), int(py)), (int(next_px), int(next_py)), 1)

            surf.blit(fill_surf, (self.x, self.y - 3))

        # Border
        pygame.draw.rect(surf, (80, 80, 100),
                         (self.x - 1, self.y - 1, self.width + 2, self.height + 2),
                         1, border_radius=4)

        # Label
        label_font = pygame.font.Font(None, 18)
        label = label_font.render("BODY MASS", True, (168, 158, 138))
        surf.blit(label, (self.x, self.y - 16))
```

**Performance cost:** 1 polygon + ~10 line segments. **Budget: 0.1ms.**

### 5.2 Score/Collection Popups

**What it looks like:** When you collect jello powder, a "+1" pops up with the item's color, scales up briefly (juice!), then floats up and fades.

```python
class CollectionPopup:
    """Juicy "+N" popup when collecting items."""

    _font = None

    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.timer = 0
        self.lifetime = 45
        self.vy = -2

        if CollectionPopup._font is None:
            CollectionPopup._font = pygame.font.Font(None, 28)

        self.rendered = CollectionPopup._font.render(text, True, color)

    def update(self):
        self.timer += 1
        self.y += self.vy
        self.vy *= 0.95
        return self.timer < self.lifetime

    def draw(self, surf):
        progress = self.timer / self.lifetime
        alpha = int(255 * (1 - progress))

        # Scale: pop up to 1.3x in first 6 frames, then settle to 1.0
        if self.timer < 6:
            scale = 1.0 + 0.3 * (self.timer / 6)
        elif self.timer < 12:
            scale = 1.3 - 0.3 * ((self.timer - 6) / 6)
        else:
            scale = 1.0

        w = int(self.rendered.get_width() * scale)
        h = int(self.rendered.get_height() * scale)
        scaled = pygame.transform.scale(self.rendered, (max(1, w), max(1, h)))
        scaled.set_alpha(alpha)
        rect = scaled.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(scaled, rect)
```

**Performance cost:** 1 scale + 1 blit per popup. Max 2-3 active at once. **Budget: 0.1ms.**

### 5.3 Screen Transitions

Three transition types for different contexts:

**A) Fade to Black (floor transitions, death):**
```python
class FadeTransition:
    def __init__(self, duration=30, color=(0, 0, 0)):
        self.duration = duration
        self.timer = 0
        self.color = color
        self.state = "out"  # "out" = fading to black, "in" = fading from black
        self.overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        self.overlay.fill(color)
        self.callback = None  # called at midpoint

    def start(self, callback=None):
        self.timer = 0
        self.state = "out"
        self.callback = callback

    def update(self):
        self.timer += 1
        if self.state == "out" and self.timer >= self.duration:
            self.state = "in"
            self.timer = 0
            if self.callback:
                self.callback()  # load next level at midpoint
        elif self.state == "in" and self.timer >= self.duration:
            return False  # transition complete
        return True

    def draw(self, surf):
        if self.state == "out":
            alpha = int(255 * (self.timer / self.duration))
        else:
            alpha = int(255 * (1 - self.timer / self.duration))
        self.overlay.set_alpha(alpha)
        surf.blit(self.overlay, (0, 0))
```

**B) Iris Wipe (entering a secret room):**
```python
class IrisWipe:
    """Circle that shrinks/expands from a focal point, like classic cartoons."""

    def __init__(self, focus_x, focus_y, duration=30):
        self.cx = focus_x
        self.cy = focus_y
        self.duration = duration
        self.timer = 0
        self.state = "close"  # "close" then "open"
        self.max_radius = int(math.hypot(SCREEN_W, SCREEN_H))
        self.mask = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self.callback = None

    def start(self, callback=None):
        self.timer = 0
        self.state = "close"
        self.callback = callback

    def update(self):
        self.timer += 1
        if self.state == "close" and self.timer >= self.duration:
            self.state = "open"
            self.timer = 0
            if self.callback:
                self.callback()
        elif self.state == "open" and self.timer >= self.duration:
            return False
        return True

    def draw(self, surf):
        if self.state == "close":
            progress = self.timer / self.duration
            radius = int(self.max_radius * (1 - progress))
        else:
            progress = self.timer / self.duration
            radius = int(self.max_radius * progress)

        # Fill black, then cut a circle
        self.mask.fill((0, 0, 0, 255))
        pygame.draw.circle(self.mask, (0, 0, 0, 0),
                           (int(self.cx), int(self.cy)), max(1, radius))
        surf.blit(self.mask, (0, 0))
```

**C) Shatter (death screen):**
```python
class ShatterTransition:
    """Screen breaks into pieces that fall away (dramatic death transition)."""

    def __init__(self):
        self.pieces = []
        self.active = False

    def start(self, screen_capture):
        """Pass in a copy of the current screen to shatter."""
        self.active = True
        self.pieces = []
        # Divide screen into a grid of chunks
        chunk_w, chunk_h = 80, 60
        for y in range(0, SCREEN_H, chunk_h):
            for x in range(0, SCREEN_W, chunk_w):
                w = min(chunk_w, SCREEN_W - x)
                h = min(chunk_h, SCREEN_H - y)
                piece = screen_capture.subsurface(pygame.Rect(x, y, w, h)).copy()
                self.pieces.append({
                    "surf": piece,
                    "x": float(x),
                    "y": float(y),
                    "vx": random.uniform(-3, 3),
                    "vy": random.uniform(-8, -2),
                    "rot": 0,
                    "rot_v": random.uniform(-0.1, 0.1),
                    "gravity": 0.4,
                    "lifetime": random.randint(40, 80),
                })

    def update(self):
        if not self.active:
            return False
        all_dead = True
        for p in self.pieces:
            if p["lifetime"] > 0:
                p["vy"] += p["gravity"]
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["rot"] += p["rot_v"]
                p["lifetime"] -= 1
                all_dead = False
        if all_dead:
            self.active = False
        return self.active

    def draw(self, surf):
        for p in self.pieces:
            if p["lifetime"] > 0:
                alpha = int(255 * min(1, p["lifetime"] / 20))
                p["surf"].set_alpha(alpha)
                surf.blit(p["surf"], (int(p["x"]), int(p["y"])))
```

**Performance cost:** Fade = 1 full-screen blit (cheap). Iris = 1 full-screen fill + 1 circle. Shatter = ~150 small blits (heavier, but only during transitions when gameplay is paused). **Budget: 0.5ms for fade, 0.8ms for iris, 2.0ms for shatter.**

### 5.4 Pause Menu Effects

**What it looks like:** When paused, the game darkens and blurs slightly. The word "PAUSED" drops in from above with a gentle bounce.

```python
class PauseOverlay:
    def __init__(self):
        self.darken = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 140))
        self.font = pygame.font.Font(None, 64)
        self.text = self.font.render("PAUSED", True, (255, 255, 255))
        self.text_y = -50  # starts above screen
        self.target_y = SCREEN_H // 2 - 20
        self.y_velocity = 0

    def update(self):
        # Spring animation to target position
        self.y_velocity += (self.target_y - self.text_y) * 0.08
        self.y_velocity *= 0.8
        self.text_y += self.y_velocity

    def draw(self, surf):
        surf.blit(self.darken, (0, 0))
        rect = self.text.get_rect(center=(SCREEN_W // 2, int(self.text_y)))
        surf.blit(self.text, rect)
        # Subtitle
        sub_font = pygame.font.Font(None, 24)
        sub = sub_font.render("Press ESC or Plus (+) to resume", True, (180, 170, 150))
        sub_rect = sub.get_rect(center=(SCREEN_W // 2, int(self.text_y) + 40))
        surf.blit(sub, sub_rect)
```

**Performance cost:** Static overlay. **Budget: 0.3ms (one-time darken blit).**

### 5.5 Death Screen

**What it looks like:** Screen shatters (see ShatterTransition above). Then fades to a dark red-tinted screen. "DEFEATED" appears with a dramatic slam. Below it: "The dungeon claims another..." and a jello cube silhouette melting. Then "Try Again?" pulses invitingly.

```python
class DeathScreen:
    def __init__(self):
        self.timer = 0
        self.active = False
        self.title_font = pygame.font.Font(None, 72)
        self.sub_font = pygame.font.Font(None, 28)
        self.prompt_font = pygame.font.Font(None, 32)

    def start(self):
        self.active = True
        self.timer = 0

    def update(self):
        if self.active:
            self.timer += 1

    def draw(self, surf, t):
        if not self.active:
            return

        # Background: dark red
        bg = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        bg.fill((30, 10, 15, min(220, self.timer * 4)))
        surf.blit(bg, (0, 0))

        if self.timer > 30:
            # "DEFEATED" title with slam
            if self.timer < 40:
                scale = 2.0 - ((self.timer - 30) / 10)
            else:
                scale = 1.0
            title = self.title_font.render("DEFEATED", True, EMBER)
            w = int(title.get_width() * scale)
            h = int(title.get_height() * scale)
            scaled = pygame.transform.scale(title, (max(1, w), max(1, h)))
            rect = scaled.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60))
            surf.blit(scaled, rect)

        if self.timer > 60:
            # Flavor text
            sub = self.sub_font.render("The dungeon claims another...", True, (160, 120, 120))
            rect = sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
            surf.blit(sub, rect)

        if self.timer > 90:
            # Melting jello silhouette
            melt_progress = min(1.0, (self.timer - 90) / 60)
            jello_y = SCREEN_H // 2 + 40
            jello_w = int(30 + melt_progress * 20)
            jello_h = int(30 - melt_progress * 15)
            jello_surf = pygame.Surface((jello_w, jello_h + 10), pygame.SRCALPHA)
            pygame.draw.ellipse(jello_surf,
                (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 100),
                (0, 0, jello_w, jello_h))
            # Puddle underneath
            puddle_w = int(jello_w * (1 + melt_progress))
            pygame.draw.ellipse(jello_surf,
                (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 60),
                ((jello_w - puddle_w) // 2, jello_h - 3, puddle_w, 10))
            surf.blit(jello_surf,
                (SCREEN_W // 2 - jello_w // 2, jello_y))

        if self.timer > 120:
            # "Try Again?" with pulse
            pulse = int(180 + math.sin(t * 0.005) * 75)
            prompt = self.prompt_font.render("Press SPACE or A to try again",
                                             True, TORCH_GLOW)
            prompt.set_alpha(pulse)
            rect = prompt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 120))
            surf.blit(prompt, rect)
```

**Performance cost:** Only active on death screen (no gameplay running). **Budget: irrelevant (no game logic competing).**

---

## 6. Performance Budget

**Target:** Consistent 60fps (16.67ms per frame) on Raspberry Pi 5.

### Frame Budget Breakdown

| System | Budget | Notes |
|--------|--------|-------|
| Game logic (physics, AI, collision) | 3.0ms | |
| Background draw | 2.0ms | Stone walls, floor tiles |
| Lighting system | 2.0ms | Full-screen darkness overlay |
| Particle pool draw (300 max) | 1.5ms | ~100-150 alive typical |
| Fog layers (3) | 0.5ms | Pre-rendered, single blit each |
| Player draw (jello body + wobble) | 0.5ms | Polygon + overlays |
| Enemy draw (3-5 on screen) | 1.0ms | Sprite blit + flash overlay |
| Shockwaves + debris | 0.3ms | Only during events |
| HUD (health bar, popups, text) | 0.3ms | |
| pygame.display.flip() | 2.5ms | GPU page flip at 1280x720 |
| **TOTAL** | **~13.6ms** | **3ms headroom** |

### Optimization Strategies

**1. Surface Caching (most important):**
Every glow circle, every pre-rendered texture that does not change frame-to-frame should be created once and stored. The VFXManager's `_glow_cache` handles this.

**2. Particle Pool (already described):**
Pre-allocate 300 particle slots. Never create or destroy `pygame.Surface` objects during gameplay. Reuse 8 cached circle surfaces.

**3. Dirty Rectangle Rendering (optional, advanced):**
If performance is still tight, only redraw the portions of the screen that changed. Pygame supports `pygame.display.update(rect_list)` instead of `flip()`. This is complex to implement with full-screen effects like lighting, so treat it as a last resort.

**4. Half-Resolution Effects:**
The lighting darkness overlay and fog layers can be rendered at half resolution (640x360) and scaled up. This halves their pixel cost. The quality loss is invisible for these soft, blurry effects.

**5. Effect LOD (Level of Detail):**
If the particle pool is more than 80% full, reduce new emission rates. If frame time exceeds 14ms, skip ambient dust motes and reduce fog layers to 1.

```python
class PerformanceGovernor:
    """Monitors frame time and reduces VFX quality if needed."""

    def __init__(self):
        self.frame_times = []
        self.quality = 1.0  # 1.0 = full, 0.5 = reduced

    def tick(self, dt_ms):
        self.frame_times.append(dt_ms)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)

        avg = sum(self.frame_times) / len(self.frame_times)
        if avg > 15.0:
            self.quality = max(0.3, self.quality - 0.05)
        elif avg < 12.0:
            self.quality = min(1.0, self.quality + 0.02)

    @property
    def should_draw_fog(self):
        return self.quality > 0.4

    @property
    def max_ambient_particles(self):
        return int(20 * self.quality)

    @property
    def should_draw_dust_motes(self):
        return self.quality > 0.6
```

### Pre-Render vs Real-Time Decision Matrix

| Effect | Pre-Render? | Why |
|--------|------------|-----|
| Glow circles (all sizes) | YES | Static shape, used hundreds of times |
| Fog strips | YES | Generated once at level load |
| Light gradient textures | YES | Quantized by radius, cached |
| Stone wall background | PARTIALLY | Redraw per frame (randomized brick color flicker) -- should be cached as static image |
| Torch flames | REAL-TIME | Small, changes every frame, only 3-5 on screen |
| Particle circles | CACHE BY SIZE | 8 sizes pre-allocated, overwritten in-place |
| Jello body polygon | REAL-TIME | Changes shape every frame (wobble) |
| Enemy sprites | PRE-SCALE | Scale Andrew's art once at load, blit from cache |
| Shockwave rings | REAL-TIME | Expanding, short-lived, only 0-2 active |
| HUD text | PRE-RENDER | Font.render() is slow; cache all static text strings |

**Critical fix for spark.py:** The current `draw_castle_bg()` function redraws the entire stone wall pattern every frame with `random.randint` calls -- this means the walls flicker randomly, and it costs ~2ms of unnecessary work. Fix: render the background once to a surface at level load, then blit that surface every frame.

```python
# At level load:
bg_surface = pygame.Surface((SCREEN_W, SCREEN_H))
draw_castle_bg(bg_surface)  # draw once

# Every frame:
screen.blit(bg_surface, (0, 0))  # ~0.3ms instead of ~2ms
```

This alone saves ~1.7ms/frame -- enough to fund the entire lighting system.

---

## 7. Wow Moments

These are the 5 specific moments where VFX should go over the top. Budget extra performance headroom for these because they are brief and memorable.

### Wow Moment 1: First Ground Pound Kill

**When:** The player uses ground pound for the first time and it kills a roly-poly.

**What happens:**
- Normal ground pound shockwave (expanded ring + screen shake + debris)
- Hit-stop: 4 frames (longer than normal)
- Camera zooms in slightly (1.1x) for 0.5 seconds
- The roly-poly pops with an extra-large particle burst (20 particles instead of 8)
- Brief slow-motion: game runs at 30fps for 15 frames (quarter second), then snaps back to 60
- Text popup: "GROUND POUND!" in bold amber, drops in from top with bounce

**Implementation:**
```python
def trigger_first_ground_pound_kill(vfx, enemy_x, enemy_y):
    vfx.hitstop(4)
    vfx.zoom_to(1.1)
    vfx.slow_motion(frames=15, target_fps=30)
    vfx.shake(10)
    # Extra particles
    for _ in range(20):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        vfx.particles.emit(enemy_x, enemy_y,
            math.cos(angle) * speed, math.sin(angle) * speed,
            (180, 120, 80), 4, 40)
    # Achievement popup
    vfx.popup("GROUND POUND!", TORCH_AMBER, duration=90)
```

### Wow Moment 2: Boss Death Sequence

**When:** The floor boss dies.

**What happens:**
1. Time freezes (hit-stop 10 frames)
2. Boss flashes white rapidly
3. Screen goes white briefly (full-screen flash, 6 frames)
4. Boss explodes into 50+ particles matching their color palette
5. Equipment scatters (hat, weapon, bottle for Sanitizer Warriors)
6. Camera slowly zooms out to 0.9x revealing the whole arena
7. Purple puddle spreads on the ground (persistent)
8. Dramatic pause (1 second of silence)
9. "BOSS DEFEATED" title slams onto screen
10. Jello powder rains from above (reward particles, 5-10 collectibles spawn)
11. Triumphant jingle plays

**Performance note:** This is the heaviest moment. 50 particles + 3 scatter items + full-screen flash + zoom. Expected cost: ~3ms peak for 1-2 seconds. Acceptable because only the boss death animation is playing (no enemies, no player input).

### Wow Moment 3: Split for the First Time

**When:** The player activates split for the first time in the game.

**What happens:**
1. Brief slow-motion (8 frames at 30fps)
2. The stretching animation plays (cross-shape stretch, see section 2.4)
3. At the snap point: 30 particles burst outward in green
4. Screen shake (6 magnitude)
5. Brief green screen flash
6. Text: "SPLIT!" pulses at center of screen (already in spark.py, enhance with scale-slam)
7. The 3 ghost pieces orbit with trailing particles for the first 2 seconds

### Wow Moment 4: Secret Room Reveal

**When:** The player solves a hidden puzzle (pulls a lever behind vines, steps on hidden pressure plate) and a secret room opens.

**What happens:**
1. Puzzle-solve sound effect + brief hit-stop (2 frames)
2. Camera pans to the secret door/wall
3. Rumble: heavy screen shake (magnitude 6) for 30 frames as the wall crumbles
4. 30+ stone DebrisChunk objects fall from the crumbling wall
5. Dust particle cloud billows from the opening (gray/brown particles)
6. Iris wipe transition as the secret room is revealed
7. The secret room has a unique lighting color (e.g., blue-tinted light instead of amber)
8. Reveal jingle + sparkle particles around the treasure/reward inside
9. Text: "SECRET FOUND!" in gold

### Wow Moment 5: Level Completion (Floor Ascension)

**When:** The player reaches the glowing door and transitions to the next floor.

**What happens:**
1. Player walks into the glowing door
2. The door's glow expands to fill the screen (white/gold radial expansion)
3. All particles on screen are pulled toward the door (gravity well effect)
4. Screen goes fully white
5. Brief "FLOOR 2" (or floor number) text appears centered
6. Fade from white into the new floor's environment
7. The new floor starts darker than the previous one (ambient darkness increases per floor)
8. Music crossfades to the new floor's track

**Gravity well particle effect:**
```python
def pull_particles_to_point(vfx, target_x, target_y, strength=0.5):
    """Attract all alive particles toward a point (gravity well)."""
    pool = vfx.particles
    for i in range(pool.max):
        if pool.life[i] > 0:
            dx = target_x - pool.x[i]
            dy = target_y - pool.y[i]
            dist = max(1, math.hypot(dx, dy))
            force = strength / dist
            pool.vx[i] += dx * force
            pool.vy[i] += dy * force
```

---

## 8. Implementation Priority

Ordered by impact-to-effort ratio. Build these in this order:

### Phase 1: Foundation (Build Session, Day 1)

| Priority | Effect | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Cache the background surface (stop re-drawing every frame) | 15 min | Saves 1.7ms/frame |
| 2 | ParticlePool (replace per-frame Surface allocation) | 30 min | Saves ~1ms/frame |
| 3 | VFXManager shell (shake, flash, hitstop) | 20 min | Organizes all effects |
| 4 | Pre-scale Andrew's sprites at load time | 15 min | Enables sprite art |

### Phase 2: Atmosphere (Build Session, Day 1-2)

| Priority | Effect | Effort | Impact |
|----------|--------|--------|--------|
| 5 | Lighting system (darkness overlay + torch light cutouts) | 45 min | Transforms the mood |
| 6 | Fog layers (pre-rendered scrolling strips) | 20 min | Depth and atmosphere |
| 7 | Enhanced torch flicker (irregular sine waves) | 10 min | Realism |
| 8 | Water drips | 20 min | Environmental life |

### Phase 3: Jello Juice (Build Session, Day 2)

| Priority | Effect | Effort | Impact |
|----------|--------|--------|--------|
| 9 | Wobbly jello body (sine-wave edge deformation) | 25 min | Character identity |
| 10 | Enhanced squash-stretch (walk bob, damage ripple) | 10 min | Game feel |
| 11 | Jello health bar | 20 min | UI polish |
| 12 | Collection popups with juice | 15 min | Feedback |

### Phase 4: Combat Polish (Build Session, Day 2-3)

| Priority | Effect | Effort | Impact |
|----------|--------|--------|--------|
| 13 | Enemy hit reactions (flash + knockback + particles) | 20 min | Combat feel |
| 14 | Enemy death (purple goo explosion + equipment scatter) | 30 min | Satisfaction |
| 15 | Enhanced shockwave (dust ring + center flash + hitstop) | 15 min | Ground pound feel |
| 16 | Detection indicators (? and !) | 20 min | Stealth system |
| 17 | Damage numbers | 15 min | Feedback clarity |

### Phase 5: Transitions and UI (Build Session, Day 3)

| Priority | Effect | Effort | Impact |
|----------|--------|--------|--------|
| 18 | Fade transition | 10 min | Level flow |
| 19 | Death screen | 20 min | Emotional beat |
| 20 | Glowing door effect | 15 min | Navigation clarity |
| 21 | Pause overlay | 10 min | Polish |
| 22 | Iris wipe (secret rooms) | 15 min | Wow moment |

### Phase 6: Wow Moments (Polish Session)

| Priority | Effect | Effort | Impact |
|----------|--------|--------|--------|
| 23 | Boss intro sequence | 30 min | Drama |
| 24 | Boss death sequence | 25 min | Payoff |
| 25 | First ground pound kill moment | 15 min | Discovery |
| 26 | Floor ascension (gravity well + white-out) | 20 min | Progression |
| 27 | Secret room reveal | 20 min | Exploration reward |

### Phase 7: Advanced (If Time Allows)

| Priority | Effect | Effort | Impact |
|----------|--------|--------|--------|
| 28 | Split stretching animation | 30 min | Visual polish |
| 29 | Items visible inside body | 20 min | Charming detail |
| 30 | Vine sway on proximity | 15 min | World reactivity |
| 31 | Torch dynamic highlight on player | 15 min | Lighting detail |
| 32 | PerformanceGovernor (auto quality scaling) | 20 min | Stability |
| 33 | Shatter transition (death) | 20 min | Dramatic |
| 34 | Crumbling debris from ceiling | 15 min | Environmental |

---

## Appendix: Color Reference for VFX

All colors from the existing spark.py palette and Andrew's asset catalog:

```python
# Castle environment
DEEP_STONE       = (26, 26, 46)       # darkest background
WARM_STONE        = (45, 45, 68)       # brick/wall color
STONE_HIGHLIGHT   = (55, 55, 80)       # edge highlights on stone
DARK_FLOOR        = (35, 30, 50)       # dungeon floor
VINE_GREEN        = (60, 100, 50)      # vine/moss
TORCH_AMBER       = (232, 168, 56)     # primary light color
TORCH_GLOW        = (245, 230, 200)    # soft warm white

# Player (jello cube)
JELLO_GREEN       = (125, 223, 100)    # primary body color
JELLO_GREEN_DIM   = (80, 160, 60)      # shadow/darker areas
JELLO_BODY_ALPHA  = (100, 210, 80, 140)  # translucent fill
JELLO_HIGHLIGHT   = (180, 240, 160)    # specular highlight
JELLO_EDGE        = (140, 255, 120)    # refraction rim

# Enemy (Sanitizer Warrior) — from Andrew's art
WARRIOR_PURPLE    = (106, 27, 154)     # skin
WARRIOR_PURPLE_LT = (156, 39, 176)     # lighter skin
WARRIOR_GOO       = (206, 147, 216)    # purple goo splatter
WARRIOR_BROWN     = (93, 64, 55)       # tunic
WARRIOR_GRAY      = (158, 158, 158)    # hat/weapon metal
SANITIZER_TEAL    = (0, 150, 136)      # bottle label
PROHIBITION_RED   = (244, 67, 54)      # red circle on bottle

# Combat
EMBER             = (196, 75, 43)       # fire/damage color
DAMAGE_RED        = (255, 80, 80)       # damage numbers
HEAL_GREEN        = (100, 255, 120)     # healing numbers

# Water drips
WATER_BLUE        = (120, 170, 240)
WATER_BLUE_PALE   = (160, 200, 240)

# Items — from Andrew's art
JELLO_POWDER_OLIVE = (158, 157, 36)    # powder bag color
PUDDLE_PURPLE      = (123, 31, 162)    # dropped items puddle
```

---

## Summary

This VFX system provides 34 distinct visual effects organized into 7 implementation phases. The architecture centers on three performance-critical patterns:

1. **Particle Pool** — 300 pre-allocated particles, zero runtime allocation, cached circle surfaces
2. **Surface Caching** — glow textures, background, fog strips, scaled sprites all rendered once
3. **Performance Governor** — automatic quality scaling if frame time exceeds budget

The most impactful effects to implement first are the background caching fix (saves 1.7ms), the particle pool (saves 1ms), and the lighting system (transforms the game's atmosphere). With those three in place, the game will look and feel dramatically different from the current spark.py demo.

Every effect has been designed to run within the 16.67ms frame budget on Raspberry Pi 5 at 1280x720. The total VFX cost in a typical gameplay frame is estimated at 5-6ms, leaving 8ms of headroom for game logic, collision detection, and AI — which is more than sufficient for a 2D platformer.
