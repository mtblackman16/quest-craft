"""
SPLIT — Jello Cube (player character) + JelloProjectile
Full moveset: move, jump, shoot, ground pound, split, perfect dodge, eat, interact, water absorb.
"""
import pygame
import math
import random
from game.engine.settings import (
    GRAVITY, MAX_FALL_SPEED, GROUND_POUND_SPEED, PLAYER_SPEED, PLAYER_JUMP_POWER,
    PLAYER_BASE_SIZE, PLAYER_MAX_HEALTH, JELLY_SHOT_COST, JELLO_POWDER_HEAL,
    PERFECT_DODGE_FRAMES, SPLIT_DURATION, HARD_DAMAGE_MULTIPLIER,
    SCREEN_H,
    JELLO_GREEN, JELLO_GREEN_DIM, TORCH_AMBER, STICK_DEADZONE,
    CTRL_A, CTRL_B, CTRL_X, CTRL_Y, CTRL_L, CTRL_ZL, CTRL_ZR,
    AXIS_LX, AXIS_LY, AXIS_RX,
    KEY_JUMP, KEY_SHOOT, KEY_EAT, KEY_INTERACT, KEY_SPLIT, KEY_DODGE, KEY_SWITCH_SPLIT,
    GameEvent, Difficulty,
)
from game.engine.sprites import load_sprite, flip_h


class JelloProjectile:
    """A glob of jelly fired by the player."""

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1=right, -1=left
        self.speed = 9
        self.radius = 6
        self.lifetime = 50
        self.max_lifetime = 50
        self.trail = []
        self.alive = True

    def update(self):
        self.x += self.speed * self.direction
        self.lifetime -= 1
        self.trail.append((self.x, self.y, self.lifetime))
        if len(self.trail) > 8:
            self.trail.pop(0)
        if self.lifetime <= 0:
            self.alive = False
        return self.alive

    # Class-level cached surfaces for trail and glow
    _trail_cache = {}  # (size, alpha) -> Surface
    _glow_cache = None  # pre-built glow surface

    def draw(self, surf, camera_offset=(0, 0)):
        ox, oy = camera_offset
        # Trail (cached surfaces)
        for i, (tx, ty, tl) in enumerate(self.trail):
            alpha = int(80 * (i / max(1, len(self.trail))))
            s = max(1, int(self.radius * 0.5 * (i / max(1, len(self.trail)))))
            key = (s, alpha)
            ts = JelloProjectile._trail_cache.get(key)
            if ts is None:
                ts = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
                pygame.draw.circle(ts, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], alpha), (s, s), s)
                JelloProjectile._trail_cache[key] = ts
            surf.blit(ts, (int(tx + ox) - s, int(ty + oy) - s))
        # Glow (cached surface with varying alpha)
        fade = self.lifetime / self.max_lifetime
        glow_s = int(self.radius * 3)
        if JelloProjectile._glow_cache is None or JelloProjectile._glow_cache.get_width() != glow_s * 2:
            JelloProjectile._glow_cache = pygame.Surface((glow_s * 2, glow_s * 2), pygame.SRCALPHA)
            pygame.draw.circle(JelloProjectile._glow_cache, (JELLO_GREEN[0], JELLO_GREEN[1], JELLO_GREEN[2], 30),
                               (glow_s, glow_s), glow_s)
        glow = JelloProjectile._glow_cache.copy()
        glow.set_alpha(int(255 * fade))
        surf.blit(glow, (int(self.x + ox) - glow_s, int(self.y + oy) - glow_s))
        # Main ball
        r = int(self.radius * fade) + 2
        pygame.draw.circle(surf, JELLO_GREEN, (int(self.x + ox), int(self.y + oy)), r)
        # Highlight
        pygame.draw.circle(surf, (180, 240, 160), (int(self.x + ox) - 1, int(self.y + oy) - 2), max(1, r // 2))

    def get_rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           self.radius * 2, self.radius * 2)


class JelloCube:
    """The player character — a wobbly jello cube with mass-based health."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.base_w = PLAYER_BASE_SIZE
        self.base_h = PLAYER_BASE_SIZE
        self.w = PLAYER_BASE_SIZE
        self.h = PLAYER_BASE_SIZE
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self._ground_frames = 0  # coyote time: frames since last on_ground
        self.speed = PLAYER_SPEED
        self.jump_power = PLAYER_JUMP_POWER
        self.facing = 1  # 1=right, -1=left

        # Jelly physics visuals
        self.squish = 0.0
        self.squish_v = 0.0
        self.jiggle_phase = 0.0
        self.trail = []

        # Health (mass-based)
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH

        # Jello powder inventory
        self.jello_powder_count = 3  # start with some

        # Ground pound
        self.ground_pounding = False
        self.just_landed_pound = False

        # Split
        self.is_split = False
        self.split_timer = 0
        self.split_pieces = []
        self.active_split_piece = 0  # which piece player controls

        # Perfect dodge
        self.dodge_timer = 0
        self.dodge_invulnerable = False
        self.dodge_cooldown = 0
        self.dodge_slow_mo = False  # True during dodge -- game loop can check for time dilation

        # Pill
        self.active_pill = None
        self.pill_timer = 0

        # Water
        self.has_water = False

        # Cooked jelly (crafted at cooking pot — this is what heals)
        self.cooked_jelly_count = 0

        # Idle timer (for banana slug + dance)
        self.idle_timer = 0

        # Events to emit (collected each frame, consumed by game loop)
        self.pending_events = []

        # Speed multiplier (for Cleanser reward)
        self.speed_multiplier = 1.0

        # Invulnerability frames after taking damage
        self.invuln_timer = 0

        # Freeze (MamaSloth Mom Look)
        self.freeze_timer = 0

        # Sprite (loaded lazily on first draw)
        self._sprite = None
        self._sprite_flipped = None
        self._sprite_loaded = False

    def update(self, keys, platforms, joystick=None, room_width=0, room_height=0):
        """Main update — called once per frame."""
        # NOTE: pending_events is NOT cleared here — the game loop clears it
        # after processing, so input-generated events (jump, shoot) survive.
        self.just_landed_pound = False

        # Tick timers
        if self.dodge_timer > 0:
            self.dodge_timer -= 1
            if self.dodge_timer <= 0:
                self.dodge_invulnerable = False
                self.dodge_slow_mo = False
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1
        if self.invuln_timer > 0:
            self.invuln_timer -= 1
        if self.pill_timer > 0:
            self.pill_timer -= 1
            if self.pill_timer <= 0:
                self.active_pill = None
        if self.freeze_timer > 0:
            self.freeze_timer -= 1

        # ── Movement ──
        frozen = self.freeze_timer > 0
        if not self.ground_pounding:
            self.vx = 0
            moved = False

            if not frozen:
                # Keyboard
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.vx = -self.speed * self.speed_multiplier
                    self.facing = -1
                    moved = True
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.vx = self.speed * self.speed_multiplier
                    self.facing = 1
                    moved = True

                # Controller left stick
                if joystick:
                    try:
                        axis_x = joystick.get_axis(AXIS_LX)
                        if axis_x < -STICK_DEADZONE:
                            self.vx = -self.speed * self.speed_multiplier * min(1.0, abs(axis_x))
                            self.facing = -1
                            moved = True
                        elif axis_x > STICK_DEADZONE:
                            self.vx = self.speed * self.speed_multiplier * min(1.0, abs(axis_x))
                            self.facing = 1
                            moved = True
                        # D-pad movement
                        hat = joystick.get_hat(0)
                        if hat[0] == -1:
                            self.vx = -self.speed * self.speed_multiplier
                            self.facing = -1
                            moved = True
                        elif hat[0] == 1:
                            self.vx = self.speed * self.speed_multiplier
                            self.facing = 1
                            moved = True
                        # Right stick facing (without moving)
                        rx = joystick.get_axis(AXIS_RX)
                        if abs(rx) > STICK_DEADZONE:
                            self.facing = 1 if rx > 0 else -1
                    except Exception:
                        pass

            # Idle tracking
            if moved or not self.on_ground:
                self.idle_timer = 0
            else:
                self.idle_timer += 1
        else:
            # During ground pound: no horizontal
            self.vx = 0

        # ── Gravity ──
        if self.ground_pounding:
            self.vy = GROUND_POUND_SPEED
        else:
            self.vy += GRAVITY
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED

        # ── Move X, then resolve horizontal collisions ──
        self.x += self.vx
        player_rect = self.get_rect()
        for plat in platforms:
            pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(*plat)
            if pr.width == 0 or pr.height == 0:
                continue
            if player_rect.colliderect(pr):
                if self.vx > 0:
                    # Moving right — push left out of platform
                    self.x = pr.left - self.w
                elif self.vx < 0:
                    # Moving left — push right out of platform
                    self.x = pr.right
                self.vx = 0
                player_rect = self.get_rect()

        # ── Move Y, then resolve vertical collisions ──
        self.y += self.vy
        self.on_ground = False
        self._ground_frames += 1
        player_rect = self.get_rect()
        for plat in platforms:
            pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(*plat)
            if pr.width == 0 or pr.height == 0:
                continue
            if player_rect.colliderect(pr):
                if self.vy >= 0:
                    # Falling — land on top
                    self.y = pr.top - self.h
                    if self.ground_pounding:
                        self.squish = 0.6
                        self.just_landed_pound = True
                        self.ground_pounding = False
                        self.pending_events.append(GameEvent.PLAYER_GROUND_POUND)
                    elif self.vy > 4:
                        self.squish = 0.4
                        # Defer land event by a few frames so sound syncs with visual squish
                        self._land_delay = 3
                    self.vy = 0
                    self.on_ground = True
                    self._ground_frames = 0
                    # Moving platform carry (both axes)
                    if hasattr(plat, 'carry_vx'):
                        self.x += plat.carry_vx
                    if hasattr(plat, 'carry_vy'):
                        self.y += plat.carry_vy
                else:
                    # Rising — bonk head on bottom
                    self.y = pr.bottom
                    self.vy = 0
                player_rect = self.get_rect()

        # ── Room boundary clamping ──
        if self.x < 0:
            self.x = 0
        if room_width > 0 and self.x > room_width - self.w:
            self.x = room_width - self.w
        if self.y < 0:
            self.y = 0
        # Fall death: fell off the bottom of the level
        kill_y = (room_height + 100) if room_height > 0 else (SCREEN_H + 100)
        if self.y > kill_y:
            self.pending_events.append(GameEvent.PLAYER_DIED)

        # ── Deferred land sound ──
        if hasattr(self, '_land_delay') and self._land_delay > 0:
            self._land_delay -= 1
            if self._land_delay <= 0:
                self.pending_events.append(GameEvent.PLAYER_LAND)

        # ── Squish spring animation ──
        self.squish_v += (-self.squish) * 0.3
        self.squish_v *= 0.7
        self.squish += self.squish_v

        # ── Jiggle ──
        self.jiggle_phase += 0.15 if abs(self.vx) > 0 else 0.05

        # ── Split timer ──
        if self.is_split:
            self.split_timer -= 1
            if self.split_timer <= 0:
                # Try safe unsplit first; if blocked, force it
                if not self.try_unsplit(platforms):
                    self.unsplit()

        # ── Trail ──
        if abs(self.vx) > 0 or not self.on_ground:
            self.trail.append((self.x + self.w // 2, self.y + self.h, pygame.time.get_ticks()))
        if len(self.trail) > 20:
            self.trail.pop(0)

    def jump(self):
        """Jump — allowed when on ground (or within 4 frames of leaving ground = coyote time)."""
        if self.freeze_timer > 0:
            return False
        can_jump = (self.on_ground or self._ground_frames <= 4) and not self.ground_pounding
        if can_jump:
            self.vy = self.jump_power
            self.on_ground = False
            self._ground_frames = 99  # consume coyote time
            self.squish = -0.3
            self.pending_events.append(GameEvent.PLAYER_JUMP)
            return True
        return False

    def shoot(self):
        """Fire a jello shot. Costs health/mass. Returns JelloProjectile or None."""
        if self.freeze_timer > 0:
            return None
        if self.health <= JELLY_SHOT_COST + 5:  # don't suicide
            return None
        self.health -= JELLY_SHOT_COST
        self._update_visual_size()
        cx = self.x + self.w / 2 + self.facing * (self.w / 2 + 8)
        cy = self.y + self.h / 2
        self.squish = -0.15
        self.pending_events.append(GameEvent.PLAYER_SHOOT)
        return JelloProjectile(cx, cy, self.facing)

    def start_ground_pound(self):
        """Initiate ground pound — only while airborne."""
        if self.freeze_timer > 0:
            return False
        if not self.on_ground and not self.ground_pounding:
            self.ground_pounding = True
            self.vy = GROUND_POUND_SPEED
            self.vx = 0
            return True
        return False

    def perfect_dodge(self):
        """Start a perfect dodge — brief invulnerability + slow-mo flag.
        Dodge window: 10 frames (~167ms). Cooldown: 30 frames (~500ms).
        """
        if self.freeze_timer > 0:
            return False
        if self.dodge_cooldown > 0:
            return False
        self.dodge_timer = PERFECT_DODGE_FRAMES
        self.dodge_invulnerable = True
        self.dodge_slow_mo = True  # signal game loop for time dilation
        self.dodge_cooldown = 30  # half second cooldown
        self.pending_events.append(GameEvent.PLAYER_DODGE)
        return True

    def eat_jello_powder(self):
        """Consume cooked jelly to heal. Raw jello powder must be cooked first."""
        if self.cooked_jelly_count <= 0:
            return False
        if self.health >= self.max_health:
            return False
        self.cooked_jelly_count -= 1
        self.health = min(self.max_health, self.health + JELLO_POWDER_HEAL)
        self._update_visual_size()
        self.squish = 0.2
        self.pending_events.append(GameEvent.PLAYER_HEAL)
        return True

    def interact(self):
        """Context-sensitive interaction. Returns True to signal intent."""
        self.pending_events.append(GameEvent.PLAYER_INTERACT)
        return True

    def absorb_water(self):
        """Absorb water from a nearby source."""
        self.has_water = True
        return True

    def squirt_water(self):
        """Squirt absorbed water."""
        if not self.has_water:
            return False
        self.has_water = False
        return True

    def split(self):
        """Split into 4 quarter-size pieces. Player controls one, R/L switches."""
        if self.is_split:
            return self.try_unsplit()
        self.is_split = True
        self.split_timer = SPLIT_DURATION
        self.active_split_piece = 0  # 0 = main body, 1-3 = ghost pieces
        self.pre_split_w = self.w
        self.pre_split_h = self.h
        self.pre_split_x = self.x
        self.pre_split_y = self.y
        # Quarter size (half width AND half height)
        self.w = max(12, self.w // 2)
        self.h = max(12, self.h // 2)
        # 3 ghost pieces left behind at the split location
        self.split_pieces = [
            {'x': self.x - 20, 'y': self.y, 'vx': 0, 'vy': 0},
            {'x': self.x + 20, 'y': self.y - 10, 'vx': 0, 'vy': 0},
            {'x': self.x, 'y': self.y - 25, 'vx': 0, 'vy': 0},
        ]
        self.pending_events.append(GameEvent.PLAYER_SPLIT)
        return True

    def try_unsplit(self, platforms=None):
        """Reform from split — only if there's room for full size."""
        if not self.is_split:
            return False
        full_w = self.pre_split_w if hasattr(self, 'pre_split_w') else self.base_w
        full_h = self.pre_split_h if hasattr(self, 'pre_split_h') else self.base_h
        # Check if full-size rect would overlap any platform
        test_rect = pygame.Rect(int(self.x), int(self.y - (full_h - self.h)),
                                full_w, full_h)
        if platforms:
            for plat in platforms:
                pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(*plat)
                if pr.width == 0 or pr.height == 0:
                    continue
                # Only block if it's a ceiling/side collision, not the floor we're on
                if test_rect.colliderect(pr):
                    overlap_y = test_rect.top < pr.bottom and test_rect.bottom > pr.top
                    overlap_x = test_rect.left < pr.right and test_rect.right > pr.left
                    if overlap_x and overlap_y:
                        # Check if it's the floor we're standing on
                        if pr.top >= self.y + self.h - 4:
                            continue  # this is the ground, that's fine
                        return False  # blocked — can't unsplit here
        self.is_split = False
        self.split_timer = 0
        self.w = full_w
        self.h = full_h
        self.split_pieces = []
        self.squish = 0.3
        self.pending_events.append(GameEvent.PLAYER_UNSPLIT)
        return True

    def unsplit(self):
        """Reform from split (no collision check — used by timer expiry)."""
        if not self.is_split:
            return False
        self.is_split = False
        self.split_timer = 0
        self.w = self.pre_split_w if hasattr(self, 'pre_split_w') else self.base_w
        self.h = self.pre_split_h if hasattr(self, 'pre_split_h') else self.base_h
        self.split_pieces = []
        self.squish = 0.3
        self.pending_events.append(GameEvent.PLAYER_UNSPLIT)
        return True

    def switch_split_piece(self, direction=1):
        """Cycle control between split pieces. direction: 1=R, -1=L."""
        if not self.is_split or len(self.split_pieces) == 0:
            return False
        old_idx = self.active_split_piece
        num_pieces = len(self.split_pieces) + 1  # +1 for main body
        self.active_split_piece = (self.active_split_piece + direction) % num_pieces
        # Swap position with the newly-controlled piece
        new_idx = self.active_split_piece
        if old_idx == 0 and new_idx > 0:
            # Switching from main body to ghost piece — swap positions
            piece = self.split_pieces[new_idx - 1]
            old_x, old_y = self.x, self.y
            self.x = piece['x']
            self.y = piece['y']
            piece['x'] = old_x
            piece['y'] = old_y
        elif old_idx > 0 and new_idx == 0:
            # Switching from ghost piece back to main body — swap back
            piece = self.split_pieces[old_idx - 1]
            old_x, old_y = self.x, self.y
            self.x = piece['x']
            self.y = piece['y']
            piece['x'] = old_x
            piece['y'] = old_y
        elif old_idx > 0 and new_idx > 0:
            # Switching between two ghost pieces
            piece_old = self.split_pieces[old_idx - 1]
            piece_new = self.split_pieces[new_idx - 1]
            old_x, old_y = self.x, self.y
            self.x = piece_new['x']
            self.y = piece_new['y']
            piece_new['x'] = old_x
            piece_new['y'] = old_y
        self.vy = 0
        self.vx = 0
        return True

    def take_damage(self, amount, difficulty=Difficulty.NORMAL):
        """Apply damage with difficulty scaling. Returns actual damage dealt."""
        if self.dodge_invulnerable or self.invuln_timer > 0:
            return 0
        if difficulty in (Difficulty.HARD, Difficulty.EARTHQUAKE):
            amount = int(amount * HARD_DAMAGE_MULTIPLIER)
        self.health -= amount
        self.invuln_timer = 30  # half second invuln after hit
        self.squish = 0.4
        self._update_visual_size()
        self.pending_events.append(GameEvent.PLAYER_HIT)
        if self.health <= 0:
            self.health = 0
            self.pending_events.append(GameEvent.PLAYER_DIED)
        return amount

    def grow(self, amount=2):
        """Restore body mass from collecting jello powder."""
        self.health = min(self.max_health, self.health + amount)
        self._update_visual_size()

    def _update_visual_size(self):
        """Update visual size based on health percentage.
        4 visible size stages at 25% health thresholds.
        When split, pieces are quarter of the current visual size (not base).
        """
        ratio = self.health / self.max_health
        # 4 size stages at 25% thresholds
        if ratio > 0.75:
            target_w = self.base_w
        elif ratio > 0.50:
            target_w = int(self.base_w * 0.85)
        elif ratio > 0.25:
            target_w = int(self.base_w * 0.70)
        else:
            target_w = int(self.base_w * 0.55)

        if self.is_split:
            # When split, pieces are half width/height of the health-based size
            self.w = max(12, target_w // 2)
            self.h = max(12, target_w // 2)
            # Also update pre_split dimensions so unsplit restores correctly
            self.pre_split_w = target_w
            self.pre_split_h = target_w
        else:
            self.w = target_w
            self.h = target_w  # keep square

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def get_center(self):
        return (self.x + self.w / 2, self.y + self.h / 2)

    def _load_sprites(self):
        """Load sprite images (called once on first draw)."""
        self._sprite_loaded = True
        base = load_sprite('player/jello-cube-front.png', self.base_w, self.base_h)
        if base:
            self._sprite = base
            self._sprite_flipped = flip_h(base)

    def draw(self, surf, camera_offset=(0, 0)):
        ox, oy = camera_offset

        # Lazy-load sprites
        if not self._sprite_loaded:
            self._load_sprites()

        # Trail glow (simple circles, no per-particle surface allocation)
        now = pygame.time.get_ticks()
        for tx, ty, t in self.trail:
            age = (now - t) / 400.0
            if age < 1:
                s = int(6 * (1 - age))
                if s > 0:
                    pygame.draw.circle(surf, JELLO_GREEN_DIM,
                                       (int(tx + ox), int(ty + oy)), s)

        # Squished dimensions
        sq = self.squish
        draw_w = int(self.w * (1 + sq * 0.5))
        draw_h = int(self.h * (1 - sq * 0.5))
        draw_x = int(self.x + ox + (self.w - draw_w) / 2)
        draw_y = int(self.y + oy + (self.h - draw_h))

        # Jiggle
        jiggle_x = math.sin(self.jiggle_phase) * 2 if abs(self.vx) > 0 else 0

        # Invuln flash
        if self.invuln_timer > 0 and self.invuln_timer % 4 < 2:
            return  # blink

        # Glow underneath
        pygame.draw.ellipse(surf, JELLO_GREEN_DIM,
                            (draw_x - 8 + int(jiggle_x), draw_y - 8,
                             draw_w + 16, draw_h + 16))

        # ── Sprite or programmatic body ──
        if self._sprite and draw_w > 0 and draw_h > 0:
            # Use Andrew's art
            sprite = self._sprite if self.facing >= 0 else self._sprite_flipped
            # Scale for squish + health-based size
            scaled = pygame.transform.scale(sprite, (max(1, draw_w), max(1, draw_h)))
            # Pill color tint
            if self.active_pill:
                pill_colors = {
                    'fire': (255, 100, 50),
                    'water': (80, 160, 255),
                    'ice': (150, 220, 255),
                    'electricity': (255, 255, 100),
                    'attack_up': (255, 80, 80),
                }
                if self.active_pill in pill_colors:
                    tint = pygame.Surface(scaled.get_size(), pygame.SRCALPHA)
                    tint.fill((*pill_colors[self.active_pill], 60))
                    scaled = scaled.copy()
                    scaled.blit(tint, (0, 0))
            surf.blit(scaled, (draw_x + int(jiggle_x), draw_y))
        else:
            # Programmatic fallback body
            body_color = JELLO_GREEN
            if self.active_pill:
                pill_colors = {
                    'fire': (255, 100, 50),
                    'water': (80, 160, 255),
                    'ice': (150, 220, 255),
                    'electricity': (255, 255, 100),
                    'attack_up': (255, 80, 80),
                }
                if self.active_pill in pill_colors:
                    pc = pill_colors[self.active_pill]
                    body_color = (
                        (JELLO_GREEN[0] + pc[0]) // 2,
                        (JELLO_GREEN[1] + pc[1]) // 2,
                        (JELLO_GREEN[2] + pc[2]) // 2,
                    )
            body = pygame.Surface((max(1, draw_w), max(1, draw_h)), pygame.SRCALPHA)
            pygame.draw.rect(body, (*body_color, 140), (0, 0, draw_w, draw_h), border_radius=6)
            if draw_w > 8 and draw_h > 4:
                pygame.draw.rect(body, (180, 240, 160, 60),
                                 (4, 4, max(1, draw_w - 8), max(1, draw_h // 2 - 4)), border_radius=4)
            pygame.draw.rect(body, (*body_color, 200), (0, 0, draw_w, draw_h), 2, border_radius=6)
            surf.blit(body, (draw_x + int(jiggle_x), draw_y))

        # Eyes (drawn on top of sprite or body)
        eye_size = max(4, int(6 * (self.w / self.base_w)))
        pupil_size = max(2, int(4 * (self.w / self.base_w)))
        eye_y = draw_y + draw_h * 0.35
        eye_spread = draw_w * 0.22
        cx = draw_x + draw_w / 2 + jiggle_x

        for ex_offset in [-eye_spread, eye_spread]:
            ex = cx + ex_offset
            pygame.draw.circle(surf, (255, 255, 255), (int(ex), int(eye_y)), eye_size)
            pupil_x = ex + self.facing * 2
            if self.ground_pounding:
                pupil_y = eye_y + 3
            elif self.dodge_invulnerable:
                pupil_y = eye_y
            else:
                pupil_y = eye_y + (1 if not self.on_ground and self.vy > 0 else 0)
            pygame.draw.circle(surf, (20, 20, 40), (int(pupil_x), int(pupil_y)), pupil_size)

        # Freeze overlay
        if self.freeze_timer > 0:
            ice = pygame.Surface((max(1, draw_w + 4), max(1, draw_h + 4)), pygame.SRCALPHA)
            alpha = min(120, 60 + self.freeze_timer)
            pygame.draw.rect(ice, (150, 220, 255, alpha), (0, 0, draw_w + 4, draw_h + 4), border_radius=8)
            surf.blit(ice, (draw_x - 2 + int(jiggle_x), draw_y - 2))

        # Water indicator
        if self.has_water:
            pygame.draw.rect(surf, (100, 180, 255),
                             (draw_x + 2 + int(jiggle_x), int(draw_y + draw_h * 0.5),
                              draw_w - 4, draw_h // 3), border_radius=3)

        # Split ghost pieces (stationary at their positions)
        if self.is_split:
            piece_w = self.w
            piece_h = self.h
            body_color = JELLO_GREEN
            for i, piece in enumerate(self.split_pieces):
                px = piece['x'] + ox
                py = piece['y'] + oy
                # Highlight the piece that would be selected next
                is_active_ghost = (i == self.active_split_piece - 1)
                alpha = 160 if is_active_ghost else 100
                ghost = pygame.Surface((piece_w, piece_h), pygame.SRCALPHA)
                pygame.draw.rect(ghost, (*body_color, alpha),
                                 (0, 0, piece_w, piece_h), border_radius=4)
                pygame.draw.rect(ghost, (*body_color, min(255, alpha + 40)),
                                 (0, 0, piece_w, piece_h), 1, border_radius=4)
                surf.blit(ghost, (int(px), int(py)))
                # Eyes on ghost pieces
                eye_cx = int(px + piece_w / 2)
                eye_cy = int(py + piece_h * 0.35)
                for eo in [-3, 3]:
                    pygame.draw.circle(surf, (255, 255, 255), (eye_cx + eo, eye_cy), 2)
                    pygame.draw.circle(surf, (20, 20, 40), (eye_cx + eo, eye_cy), 1)
