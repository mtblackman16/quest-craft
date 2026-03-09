"""
SPLIT — Enemy entities and projectile/hazard classes.
SmallSanitizerBottle, SanitizerWarrior, JellyArcher + all projectiles and ground hazards.
"""
import pygame
import math
import random
import enum
from game.engine.settings import (
    SMALL_BOTTLE_HP, SANITIZER_WARRIOR_HP, JELLY_ARCHER_HP,
    BOTTLE_TRAIL_DAMAGE, WARRIOR_GLOB_DAMAGE, ARCHER_ARROW_DAMAGE,
    GRAVITY, SANITIZER_BLUE, SANITIZER_TRAIL, SANITIZER_PUDDLE,
    EnemyType, GameEvent,
)


# ── Enemy States ──

class EnemyState(enum.Enum):
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    HIT = "hit"
    DEAD = "dead"


# ── Projectile / Hazard Classes ──

class SanitizerTrail:
    """Static puddle hazard left behind by SmallSanitizerBottle.
    Deals BOTTLE_TRAIL_DAMAGE per tick while the player stands in it.
    Fades and dies after 300 frames (~5 seconds).
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 16
        self.h = 6
        self.damage = BOTTLE_TRAIL_DAMAGE
        self.lifetime = 300
        self.max_lifetime = 300
        self.alive = True

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive:
            return
        ox, oy = camera_offset
        fade = max(0.0, self.lifetime / self.max_lifetime)
        alpha = int(80 * fade)
        puddle = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.ellipse(puddle, (120, 200, 240, alpha), (0, 0, self.w, self.h))
        surf.blit(puddle, (int(self.x + ox), int(self.y + oy)))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


class SanitizerGlob:
    """Arcing projectile fired by SanitizerWarrior.
    Creates a SanitizerPuddle when it lands (hits ground_y).
    """

    def __init__(self, x, y, target_x, target_y, ground_y):
        self.x = float(x)
        self.y = float(y)
        self.w = 10
        self.h = 10
        self.damage = WARRIOR_GLOB_DAMAGE
        self.alive = True
        self.ground_y = ground_y

        # Calculate arc trajectory to reach target
        dx = target_x - x
        dist = max(1, abs(dx))
        self.vx = dx / 60  # travel time ~60 frames
        # Launch upward with enough height for a nice arc
        self.vy = -8.0
        self.gravity = 0.25

        # Trail effect
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.x += self.vx
        self.vy += self.gravity
        self.y += self.vy

        # Hit the ground
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.alive = False

        return self.alive

    def create_puddle(self):
        """Called when the glob lands — returns a SanitizerPuddle."""
        return SanitizerPuddle(self.x - 12, self.y - 3)

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive:
            return
        ox, oy = camera_offset
        # Trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(60 * (i / max(1, len(self.trail))))
            s = max(1, 3 + i)
            ts = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (100, 180, 220, alpha), (s, s), s)
            surf.blit(ts, (int(tx + ox) - s, int(ty + oy) - s))
        # Main glob
        pygame.draw.circle(surf, SANITIZER_BLUE,
                           (int(self.x + ox), int(self.y + oy)), 5)
        # Highlight
        pygame.draw.circle(surf, (180, 220, 240),
                           (int(self.x + ox) - 1, int(self.y + oy) - 2), 2)

    def get_rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h // 2),
                           self.w, self.h)


class SanitizerPuddle:
    """Ground hazard created when a SanitizerGlob lands.
    Deals BOTTLE_TRAIL_DAMAGE per tick. Fades over 240 frames (~4 seconds).
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 24
        self.h = 8
        self.damage = BOTTLE_TRAIL_DAMAGE
        self.lifetime = 240
        self.max_lifetime = 240
        self.alive = True

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive:
            return
        ox, oy = camera_offset
        fade = max(0.0, self.lifetime / self.max_lifetime)
        alpha = int(100 * fade)
        puddle = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.ellipse(puddle, (100, 180, 220, alpha), (0, 0, self.w, self.h))
        # Slight sheen on top
        if self.w > 8:
            pygame.draw.ellipse(puddle, (160, 220, 240, alpha // 2),
                                (4, 1, self.w - 8, self.h // 2))
        surf.blit(puddle, (int(self.x + ox), int(self.y + oy)))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


class SanitizerArrow:
    """Fast straight-line projectile fired by JellyArcher.
    No trail. Deals ARCHER_ARROW_DAMAGE on hit.
    """

    def __init__(self, x, y, target_x, target_y):
        self.x = float(x)
        self.y = float(y)
        self.w = 14
        self.h = 4
        self.damage = ARCHER_ARROW_DAMAGE
        self.speed = 7.0
        self.lifetime = 120  # 2 seconds max
        self.alive = True

        # Direction toward target
        dx = target_x - x
        dy = target_y - y
        dist = max(1.0, math.hypot(dx, dy))
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed

        # Angle for drawing
        self.angle = math.atan2(dy, dx)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
        return self.alive

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive:
            return
        ox, oy = camera_offset
        cx = int(self.x + ox)
        cy = int(self.y + oy)

        # Arrow body — a rotated thin rectangle
        length = 14
        tip_x = cx + int(math.cos(self.angle) * length / 2)
        tip_y = cy + int(math.sin(self.angle) * length / 2)
        tail_x = cx - int(math.cos(self.angle) * length / 2)
        tail_y = cy - int(math.sin(self.angle) * length / 2)

        # Shaft
        pygame.draw.line(surf, (60, 80, 140), (tail_x, tail_y), (tip_x, tip_y), 3)
        # Tip (brighter)
        pygame.draw.line(surf, (120, 160, 220), (cx, cy), (tip_x, tip_y), 2)

    def get_rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h // 2),
                           self.w, self.h)


# ── Enemy Base Class ──

class Enemy:
    """Base enemy with state machine, patrol, damage, and drawing."""

    def __init__(self, x, y, w, h, health, enemy_type):
        self.x = float(x)
        self.y = float(y)
        self.w = w
        self.h = h
        self.health = health
        self.max_health = health
        self.enemy_type = enemy_type
        self.alive = True

        # State machine
        self.state = EnemyState.PATROL

        # Patrol
        self.patrol_path = []
        self.patrol_index = 0
        self.patrol_speed = 1.0

        # Facing direction: 1 = right, -1 = left
        self.facing = 1

        # Hit flash timer
        self.hit_timer = 0

        # Frame counter for per-enemy timing
        self.frame_count = 0

        # Stun timer (electricity pill effect)
        self.stun_timer = 0

    def update(self, player):
        """Run the state machine. Subclasses override specific states."""
        self.frame_count += 1

        if self.stun_timer > 0:
            self.stun_timer -= 1
            return  # stunned by electricity — skip all logic

        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0 and self.state == EnemyState.HIT:
                self.state = EnemyState.PATROL

        if self.state == EnemyState.DEAD:
            return

        if self.state == EnemyState.HIT:
            return  # stunned briefly

        if self.state == EnemyState.PATROL:
            self._do_patrol()
        elif self.state == EnemyState.CHASE:
            self._do_chase(player)
        elif self.state == EnemyState.ATTACK:
            self._do_attack(player)

    def _do_patrol(self):
        """Walk between patrol points."""
        if not self.patrol_path or len(self.patrol_path) < 2:
            return

        target_x, target_y = self.patrol_path[self.patrol_index]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 4:
            # Reached waypoint, advance to next
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_path)
        else:
            # Move toward waypoint
            self.x += (dx / dist) * self.patrol_speed
            self.y += (dy / dist) * self.patrol_speed
            self.facing = 1 if dx > 0 else -1

    def _do_chase(self, player):
        """Move toward the player. Subclasses may override."""
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1.0, math.hypot(dx, dy))
        self.x += (dx / dist) * self.patrol_speed * 1.5
        self.facing = 1 if dx > 0 else -1

    def _do_attack(self, player):
        """Attack logic — subclasses override."""
        pass

    def take_damage(self, amount):
        """Reduce health. Returns True if this blow killed the enemy."""
        if not self.alive:
            return False
        self.health -= amount
        self.hit_timer = 12  # brief stun / flash
        self.state = EnemyState.HIT
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.state = EnemyState.DEAD
            return True
        return False

    def draw(self, surf, camera_offset=(0, 0)):
        """Fallback draw — red rectangle. Subclasses override."""
        if not self.alive:
            return
        ox, oy = camera_offset
        color = (220, 50, 50) if self.hit_timer <= 0 else (255, 255, 255)
        pygame.draw.rect(surf, color,
                         (int(self.x + ox), int(self.y + oy), self.w, self.h))

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


# ── SmallSanitizerBottle ──

class SmallSanitizerBottle(Enemy):
    """Small sanitizer bottle — 30 HP, slow patrol, leaves trail puddles.
    Killed by jelly shot to back OR ground pound.
    """

    def __init__(self, x, y, patrol_points=None):
        super().__init__(x, y, w=24, h=30,
                         health=SMALL_BOTTLE_HP,
                         enemy_type=EnemyType.SANITIZER_BOTTLE)
        self.patrol_speed = 0.8
        self.color = (100, 180, 220)  # light blue

        if patrol_points:
            self.patrol_path = patrol_points
        else:
            # Default: back and forth 80px
            self.patrol_path = [(x - 40, y), (x + 40, y)]

        # Trail spawning
        self.trail_timer = 0
        self.trail_interval = 30  # frames between trail drops

    def update(self, player):
        super().update(player)
        if self.state == EnemyState.DEAD:
            return

        # Spawn trail periodically during patrol or chase
        if self.state in (EnemyState.PATROL, EnemyState.CHASE):
            self.trail_timer += 1

    def should_spawn_trail(self):
        """Returns True (and resets timer) when it is time to drop a trail."""
        if self.trail_timer >= self.trail_interval:
            self.trail_timer = 0
            return True
        return False

    def spawn_trail(self):
        """Create a SanitizerTrail at the bottle's feet."""
        return SanitizerTrail(self.x + self.w // 2 - 8,
                              self.y + self.h - 3)

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive:
            return
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        # Hit flash
        color = (255, 255, 255) if self.hit_timer > 0 else self.color
        cap_color = (255, 255, 255) if self.hit_timer > 0 else (200, 200, 210)
        label_color = (255, 255, 255) if self.hit_timer > 0 else (60, 140, 180)

        # Bottle body — rectangle with rounded bottom
        body_rect = (bx + 2, by + 8, self.w - 4, self.h - 8)
        pygame.draw.rect(surf, color, body_rect, border_radius=4)

        # Rounded top / neck
        neck_rect = (bx + 6, by + 3, self.w - 12, 8)
        pygame.draw.rect(surf, color, neck_rect, border_radius=3)

        # Cap
        cap_rect = (bx + 7, by, self.w - 14, 5)
        pygame.draw.rect(surf, cap_color, cap_rect, border_radius=2)

        # Label stripe
        if self.w > 12:
            pygame.draw.rect(surf, label_color,
                             (bx + 4, by + 14, self.w - 8, 8), border_radius=2)

        # Outline
        pygame.draw.rect(surf, (60, 120, 160),
                         (bx + 2, by + 8, self.w - 4, self.h - 8), 1, border_radius=4)

        # Health bar (only if damaged)
        if self.health < self.max_health:
            self._draw_health_bar(surf, bx, by - 6, self.w)

    def _draw_health_bar(self, surf, x, y, w):
        bar_w = w
        bar_h = 3
        ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(surf, (60, 60, 60), (x, y, bar_w, bar_h))
        pygame.draw.rect(surf, (80, 200, 80), (x, y, int(bar_w * ratio), bar_h))


# ── SanitizerWarrior ──

class SanitizerWarrior(Enemy):
    """Sanitizer warrior — 60 HP, metallic, fires arcing globs.
    Hat tips during fire animation = ground pound vulnerability window.
    Jelly shots deal only 2 damage (armored).
    """

    def __init__(self, x, y, patrol_points=None):
        super().__init__(x, y, w=32, h=40,
                         health=SANITIZER_WARRIOR_HP,
                         enemy_type=EnemyType.SANITIZER_WARRIOR)
        self.patrol_speed = 1.0
        self.color = (160, 130, 100)  # metallic brown

        if patrol_points:
            self.patrol_path = patrol_points
        else:
            self.patrol_path = [(x - 60, y), (x + 60, y)]

        # Attack state
        self.attack_timer = 0
        self.attack_cooldown = 90  # frames between glob shots
        self.fire_anim_timer = 0
        self.fire_anim_duration = 30  # hat tips down during this window
        self.pending_glob = False  # set True when it is time to fire

        # Detection range
        self.detect_range = 250

    @property
    def hat_vulnerable(self):
        """True during the fire animation — hat tips down, exposing head."""
        return self.fire_anim_timer > 0

    def update(self, player):
        super().update(player)
        if self.state == EnemyState.DEAD:
            return

        # Tick fire animation
        if self.fire_anim_timer > 0:
            self.fire_anim_timer -= 1

        # Check distance to player for attack behavior
        if self.state == EnemyState.PATROL:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            if dist < self.detect_range:
                self.state = EnemyState.ATTACK
                self.attack_timer = 0

        if self.state == EnemyState.ATTACK:
            self.facing = 1 if player.x > self.x else -1
            self.attack_timer += 1
            if self.attack_timer >= self.attack_cooldown and self.fire_anim_timer <= 0:
                # Begin fire animation
                self.fire_anim_timer = self.fire_anim_duration
                self.pending_glob = True
                self.attack_timer = 0

            # Return to patrol if player far away
            dx = player.x - self.x
            dy = player.y - self.y
            if math.hypot(dx, dy) > self.detect_range * 1.5:
                self.state = EnemyState.PATROL

    def consume_pending_glob(self, player, ground_y):
        """If a glob is ready, create and return it, otherwise None."""
        if not self.pending_glob:
            return None
        self.pending_glob = False
        cx = self.x + self.w / 2 + self.facing * 16
        cy = self.y + 8  # launch from backpack height
        return SanitizerGlob(cx, cy, player.x + player.w / 2,
                             player.y + player.h / 2, ground_y)

    def take_damage(self, amount):
        """Override — jelly shots deal only 2 damage (armor).
        Callers should use this; combat system handles the reduction.
        """
        return super().take_damage(amount)

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive:
            return
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        color = (255, 255, 255) if self.hit_timer > 0 else self.color
        hat_color = (255, 255, 255) if self.hit_timer > 0 else (120, 100, 70)
        spike_color = (255, 255, 255) if self.hit_timer > 0 else (180, 160, 120)
        pack_color = (255, 255, 255) if self.hit_timer > 0 else (80, 130, 180)

        # Legs
        leg_y = by + self.h - 10
        pygame.draw.rect(surf, color, (bx + 4, leg_y, 8, 10))
        pygame.draw.rect(surf, color, (bx + self.w - 12, leg_y, 8, 10))

        # Body (torso)
        body_rect = (bx + 2, by + 12, self.w - 4, self.h - 20)
        pygame.draw.rect(surf, color, body_rect, border_radius=3)

        # Backpack bottle (on back side)
        back_x = bx - 6 if self.facing == 1 else bx + self.w - 2
        pygame.draw.rect(surf, pack_color,
                         (back_x, by + 14, 8, 16), border_radius=2)
        pygame.draw.rect(surf, (60, 100, 150),
                         (back_x, by + 14, 8, 16), 1, border_radius=2)

        # Arms
        arm_y = by + 16
        pygame.draw.rect(surf, color, (bx - 4, arm_y, 6, 12), border_radius=2)
        pygame.draw.rect(surf, color, (bx + self.w - 2, arm_y, 6, 12), border_radius=2)

        # Head
        head_rect = (bx + 4, by + 4, self.w - 8, 12)
        pygame.draw.rect(surf, color, head_rect, border_radius=4)

        # Spiked hat — tips down when firing
        hat_y = by - 2 if not self.hat_vulnerable else by + 2
        hat_points = [
            (bx + 2, hat_y + 6),
            (bx + self.w // 2, hat_y - 6),
            (bx + self.w - 2, hat_y + 6),
        ]
        pygame.draw.polygon(surf, hat_color, hat_points)
        # Spikes on hat
        for sx in range(bx + 6, bx + self.w - 6, 8):
            pygame.draw.line(surf, spike_color,
                             (sx, hat_y + 2), (sx, hat_y - 4), 2)

        # Eyes (angry slits)
        eye_y = by + 8
        for ex_off in [8, self.w - 12]:
            pygame.draw.line(surf, (40, 20, 20),
                             (bx + ex_off, eye_y), (bx + ex_off + 4, eye_y), 2)

        # Metallic edge outline
        pygame.draw.rect(surf, (100, 80, 60), body_rect, 1, border_radius=3)

        # Health bar
        if self.health < self.max_health:
            self._draw_health_bar(surf, bx, by - 8, self.w)

    def _draw_health_bar(self, surf, x, y, w):
        bar_w = w
        bar_h = 3
        ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(surf, (60, 60, 60), (x, y, bar_w, bar_h))
        pygame.draw.rect(surf, (80, 200, 80), (x, y, int(bar_w * ratio), bar_h))


# ── JellyArcher ──

class JellyArcher(Enemy):
    """Jelly archer — 20 HP glass cannon. Stays far, fires SanitizerArrows."""

    def __init__(self, x, y, patrol_points=None):
        super().__init__(x, y, w=26, h=34,
                         health=JELLY_ARCHER_HP,
                         enemy_type=EnemyType.JELLY_ARCHER)
        self.patrol_speed = 1.2
        self.color = (60, 80, 140)  # dark blue

        if patrol_points:
            self.patrol_path = patrol_points
        else:
            self.patrol_path = [(x - 50, y), (x + 50, y)]

        # Attack state
        self.attack_timer = 0
        self.attack_cooldown = 60
        self.pending_arrow = False

        # Preferred range — backs up if player gets too close
        self.preferred_range = 180
        self.flee_range = 80
        self.detect_range = 300

    def update(self, player):
        super().update(player)
        if self.state == EnemyState.DEAD:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if self.state == EnemyState.PATROL:
            if dist < self.detect_range:
                self.state = EnemyState.ATTACK
                self.attack_timer = 0

        if self.state == EnemyState.ATTACK:
            self.facing = 1 if dx > 0 else -1

            # Back away if player is too close
            if dist < self.flee_range and dist > 0:
                flee_dx = -dx / dist
                self.x += flee_dx * self.patrol_speed * 1.5

            # Fire arrows on cooldown
            self.attack_timer += 1
            if self.attack_timer >= self.attack_cooldown:
                self.pending_arrow = True
                self.attack_timer = 0

            # Return to patrol if player is far
            if dist > self.detect_range * 1.5:
                self.state = EnemyState.PATROL

    def consume_pending_arrow(self, player):
        """If an arrow is ready, create and return it, otherwise None."""
        if not self.pending_arrow:
            return None
        self.pending_arrow = False
        cx = self.x + self.w / 2 + self.facing * 14
        cy = self.y + self.h * 0.3
        return SanitizerArrow(cx, cy,
                              player.x + player.w / 2,
                              player.y + player.h / 2)

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive:
            return
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        color = (255, 255, 255) if self.hit_timer > 0 else self.color
        dark = (255, 255, 255) if self.hit_timer > 0 else (40, 55, 100)
        bow_color = (255, 255, 255) if self.hit_timer > 0 else (100, 80, 60)

        # Slim body
        body_rect = (bx + 5, by + 10, self.w - 10, self.h - 14)
        pygame.draw.rect(surf, color, body_rect, border_radius=5)

        # Legs (thin)
        leg_y = by + self.h - 8
        pygame.draw.rect(surf, dark, (bx + 7, leg_y, 4, 8))
        pygame.draw.rect(surf, dark, (bx + self.w - 11, leg_y, 4, 8))

        # Head (small oval)
        head_cx = bx + self.w // 2
        head_cy = by + 6
        pygame.draw.ellipse(surf, color, (head_cx - 7, by, 14, 12))

        # Eyes (small, focused)
        for ex_off in [-3, 3]:
            pygame.draw.circle(surf, (255, 255, 255),
                               (head_cx + ex_off, head_cy), 3)
            pygame.draw.circle(surf, (20, 20, 60),
                               (head_cx + ex_off + self.facing, head_cy), 2)

        # Bow arm (on facing side)
        bow_x = bx + (self.w + 2) if self.facing == 1 else bx - 8
        bow_y = by + 14
        # Bow arc
        pygame.draw.arc(surf, bow_color,
                        (bow_x - 2, bow_y - 6, 8, 20),
                        -1.0 if self.facing == 1 else 2.1,
                        1.0 if self.facing == 1 else 4.2, 2)
        # String
        pygame.draw.line(surf, (180, 180, 180),
                         (bow_x + 2, bow_y - 5), (bow_x + 2, bow_y + 13), 1)

        # Outline
        pygame.draw.rect(surf, dark, body_rect, 1, border_radius=5)

        # Health bar
        if self.health < self.max_health:
            self._draw_health_bar(surf, bx, by - 6, self.w)

    def _draw_health_bar(self, surf, x, y, w):
        bar_w = w
        bar_h = 3
        ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(surf, (60, 60, 60), (x, y, bar_w, bar_h))
        pygame.draw.rect(surf, (80, 200, 80), (x, y, int(bar_w * ratio), bar_h))
