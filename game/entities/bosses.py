"""
SPLIT — Boss entities.
All bosses extend Enemy with phase logic, cinematic intros, and unique health bars.
Big Bottle, The Cleanser, The Last Guard, Gracie, Mama Sloth / Linda.
"""
import pygame
import math
import random
from game.engine.settings import (
    BIG_BOTTLE_HP, CLEANSER_HP, LAST_GUARD_HP, GRACIE_HP, MAMA_SLOTH_HP,
    SCREEN_W, SCREEN_H,
    BossType, GameEvent,
    SANITIZER_BLUE, WHITE, BLACK,
    HEALTH_GREEN, HEALTH_AMBER, HEALTH_RED,
    FONT_SMALL, FONT_HUD,
)
from game.entities.enemies import (
    Enemy, EnemyState,
    SanitizerTrail, SanitizerGlob, SanitizerPuddle, SanitizerArrow,
)
from game.engine.sprites import load_sprite, load_portrait, flip_h


# ── Boss States (extends EnemyState where needed) ──

class BossState:
    """Extra states used by bosses beyond EnemyState."""
    INTRO = "intro"
    PATROL = "patrol"
    ATTACK = "attack"
    CHARGE = "charge"
    STUNNED = "stunned"
    RECOVERING = "recovering"
    VULNERABLE = "vulnerable"
    CHASE = "chase"
    COMBO = "combo"
    SLAM = "slam"
    ARROW_RAIN = "arrow_rain"
    DEFEATED = "defeated"


# ── Boss Base Class ──

class Boss(Enemy):
    """Base class for all bosses. Extends Enemy with phase management,
    cinematic intro, arena bounds, and a full-width health bar."""

    def __init__(self, x, y, w, h, health, boss_type):
        # Pass a placeholder enemy_type — bosses use boss_type instead
        super().__init__(x, y, w, h, health, enemy_type=None)
        self.boss_type = boss_type

        # Phase management
        self.phase = 1
        self.max_phases = 1
        self.phase_thresholds = []  # HP percentages that trigger transitions

        # Intro cinematic
        self.intro_timer = 120  # 2 seconds at 60fps
        self.intro_active = True

        # Arena boundaries (x-coordinates)
        self.arena_bounds = (0, SCREEN_W)

        # Boss name for health bar display
        self.boss_name = "BOSS"

        # Animated health bar fill for smooth lerp
        self._display_health = float(health)

        # Boss-specific state (string, not EnemyState enum)
        self.boss_state = BossState.INTRO

        # Invulnerability flag
        self.invulnerable = False

    def get_health_ratio(self):
        """Return current health as a float from 0.0 to 1.0."""
        if self.max_health <= 0:
            return 0.0
        return max(0.0, min(1.0, self.health / self.max_health))

    def emit_boss_event(self, event_bus, event_type):
        """Helper to emit a boss event through the event bus."""
        if event_bus is not None:
            event_bus.emit(event_type, boss_type=self.boss_type, phase=self.phase)

    def _check_phase_transition(self):
        """Check if HP has crossed a phase threshold and advance phase.
        Returns True if a phase change occurred."""
        ratio = self.get_health_ratio()
        # phase_thresholds is ordered descending, e.g. [0.5] or [0.6, 0.3]
        new_phase = 1
        for i, threshold in enumerate(self.phase_thresholds):
            if ratio <= threshold:
                new_phase = i + 2  # phase 2 at first threshold, etc.
        if new_phase != self.phase and new_phase <= self.max_phases:
            self.phase = new_phase
            return True
        return False

    def update(self, player):
        """Boss update loop — handles intro, then delegates to subclass logic."""
        self.frame_count += 1

        # Animate health bar lerp
        lerp_speed = 2.0
        if self._display_health > self.health:
            self._display_health = max(self.health,
                                       self._display_health - lerp_speed)
        elif self._display_health < self.health:
            self._display_health = min(self.health,
                                       self._display_health + lerp_speed)

        # Intro countdown
        if self.intro_active:
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.intro_active = False
                self.boss_state = BossState.PATROL
            return

        if not self.alive:
            return

        # Phase transition check
        old_phase = self.phase
        if self._check_phase_transition():
            self._on_phase_change(old_phase, self.phase)

        # Hit timer (flash)
        if self.hit_timer > 0:
            self.hit_timer -= 1

    def _on_phase_change(self, old_phase, new_phase):
        """Called when the boss transitions to a new phase. Override in subclasses."""
        pass

    def take_damage(self, amount):
        """Override to respect invulnerability."""
        if self.invulnerable or not self.alive:
            return False
        if self.intro_active:
            return False
        self.health -= amount
        self.hit_timer = 12
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.boss_state = BossState.DEFEATED
            return True
        return False

    def _clamp_to_arena(self):
        """Keep boss within arena bounds."""
        left, right = self.arena_bounds
        if self.x < left:
            self.x = float(left)
        if self.x + self.w > right:
            self.x = float(right - self.w)

    def draw_boss_health_bar(self, surf):
        """Draw the boss health bar at the bottom of the screen.
        600px wide, 12px tall, centered, phase-colored, with name above."""
        if not self.alive and self.boss_state != BossState.DEFEATED:
            return

        bar_w = 600
        bar_h = 12
        bar_x = (SCREEN_W - bar_w) // 2
        bar_y = SCREEN_H - 40

        # Phase-dependent color
        if self.phase <= 1:
            bar_color = HEALTH_GREEN
        elif self.phase <= self.max_phases // 2 + 1:
            bar_color = HEALTH_AMBER
        else:
            bar_color = HEALTH_RED

        # Background
        bg_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4)
        pygame.draw.rect(surf, (20, 20, 20), bg_rect, border_radius=3)
        pygame.draw.rect(surf, (60, 60, 60),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=2)

        # Animated fill
        display_ratio = max(0.0, self._display_health / self.max_health)
        fill_w = int(bar_w * display_ratio)
        if fill_w > 0:
            pygame.draw.rect(surf, bar_color,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=2)

        # Border
        pygame.draw.rect(surf, (180, 180, 180),
                         (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4),
                         1, border_radius=3)

        # Phase tick marks
        for threshold in self.phase_thresholds:
            tick_x = bar_x + int(bar_w * threshold)
            pygame.draw.line(surf, WHITE,
                             (tick_x, bar_y - 1), (tick_x, bar_y + bar_h + 1), 2)

        # Boss name text above bar
        try:
            font = pygame.font.Font(None, FONT_SMALL)
        except Exception:
            font = pygame.font.SysFont(None, FONT_SMALL)
        name_surf = font.render(self.boss_name, True, WHITE)
        name_rect = name_surf.get_rect(centerx=SCREEN_W // 2, bottom=bar_y - 6)
        # Drop shadow
        shadow_surf = font.render(self.boss_name, True, BLACK)
        surf.blit(shadow_surf, (name_rect.x + 1, name_rect.y + 1))
        surf.blit(name_surf, name_rect)

    def draw(self, surf, camera_offset=(0, 0)):
        """Default boss draw — subclasses override."""
        if not self.alive and self.boss_state != BossState.DEFEATED:
            return
        ox, oy = camera_offset
        color = (255, 255, 255) if self.hit_timer > 0 else (200, 50, 50)
        pygame.draw.rect(surf, color,
                         (int(self.x + ox), int(self.y + oy), self.w, self.h))


# ═══════════════════════════════════════════════════════════════════════
# THE BIG BOTTLE — Floor 4 Tutorial Boss
# ═══════════════════════════════════════════════════════════════════════

class BigBottle(Boss):
    """Giant sanitizer bottle boss. 2 phases with spread and charge attacks."""

    def __init__(self, x, y, arena_left=100, arena_right=1180):
        super().__init__(x, y, w=150, h=200,
                         health=BIG_BOTTLE_HP,
                         boss_type=BossType.BIG_BOTTLE)
        self.boss_name = "THE BIG BOTTLE"
        self.max_phases = 2
        self.phase_thresholds = [0.5]  # phase 2 at 50%
        self.color = (100, 180, 220)
        self.arena_bounds = (arena_left, arena_right)

        # Sprite (oversized hand sanitizer bottle — front-facing, never flipped)
        self._sprite = load_sprite('items/hand-sanitizer-front.png', 120, 160)

        # Movement
        self.patrol_speed = 1.2
        self.patrol_dir = 1  # 1=right, -1=left

        # Spread attack timer
        self.spread_timer = 0
        self.spread_cooldown = 90

        # Charge attack
        self.charge_timer = 0
        self.charge_cooldown = 180
        self.charge_state = None  # None, "telegraph", "dash", "vulnerable"
        self.charge_telegraph_timer = 0
        self.charge_dash_timer = 0
        self.charge_vulnerable_timer = 0
        self.charge_target_x = 0.0
        self.charge_speed = 10.0

        # Pending projectiles for the combat system to collect
        self.pending_trails = []

    def update(self, player):
        super().update(player)
        if self.intro_active or not self.alive:
            return

        # Phase-dependent values
        speed_mult = 1.5 if self.phase >= 2 else 1.0
        spread_count = 8 if self.phase >= 2 else 5
        telegraph_duration = 20 if self.phase >= 2 else 30

        # Handle charge state machine
        if self.charge_state is not None:
            self._update_charge(player, telegraph_duration, speed_mult)
            return

        # Patrol: side-to-side
        self.x += self.patrol_dir * self.patrol_speed * speed_mult
        left, right = self.arena_bounds
        if self.x <= left:
            self.patrol_dir = 1
        elif self.x + self.w >= right:
            self.patrol_dir = -1
        self._clamp_to_arena()

        # Face player
        self.facing = 1 if player.x > self.x else -1

        # Spread attack
        self.spread_timer += 1
        cooldown = self.spread_cooldown if self.phase == 1 else 70
        if self.spread_timer >= cooldown:
            self.spread_timer = 0
            self._do_spread_attack(player, spread_count)

        # Charge attack
        self.charge_timer += 1
        cd = self.charge_cooldown if self.phase == 1 else 140
        if self.charge_timer >= cd:
            self.charge_timer = 0
            self.charge_state = "telegraph"
            self.charge_telegraph_timer = telegraph_duration
            self.charge_target_x = player.x

    def _update_charge(self, player, telegraph_duration, speed_mult):
        """Manage the charge attack state machine."""
        if self.charge_state == "telegraph":
            self.charge_telegraph_timer -= 1
            if self.charge_telegraph_timer <= 0:
                self.charge_state = "dash"
                self.charge_dash_timer = 60
                self.charge_target_x = player.x
        elif self.charge_state == "dash":
            # Dash toward target
            dx = self.charge_target_x - self.x
            direction = 1 if dx > 0 else -1
            dash_speed = self.charge_speed * speed_mult
            self.x += direction * dash_speed
            self._clamp_to_arena()

            # Leave continuous trail in phase 2
            if self.phase >= 2 and self.frame_count % 4 == 0:
                trail = SanitizerTrail(self.x + self.w // 2 - 8,
                                       self.y + self.h - 3)
                self.pending_trails.append(trail)

            self.charge_dash_timer -= 1
            if self.charge_dash_timer <= 0 or abs(dx) < 10:
                self.charge_state = "vulnerable"
                self.charge_vulnerable_timer = 60
        elif self.charge_state == "vulnerable":
            # Standing still, catchable
            self.charge_vulnerable_timer -= 1
            if self.charge_vulnerable_timer <= 0:
                self.charge_state = None

    def _do_spread_attack(self, player, count):
        """Fire a fan of SanitizerTrails in front of the boss."""
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        # Base angle toward player
        base_angle = math.atan2(player.y - cy, player.x - cx)
        arc = math.pi / 3 if self.phase == 1 else math.pi / 2.5
        for i in range(count):
            if count > 1:
                angle = base_angle - arc / 2 + arc * (i / (count - 1))
            else:
                angle = base_angle
            dist = 50 + random.randint(0, 40)
            tx = cx + math.cos(angle) * dist
            ty = cy + math.sin(angle) * dist
            trail = SanitizerTrail(tx - 8, ty - 3)
            trail.lifetime = 180  # slightly shorter
            trail.max_lifetime = 180
            self.pending_trails.append(trail)

    def consume_pending_trails(self):
        """Return list of pending trails and clear the buffer."""
        trails = self.pending_trails[:]
        self.pending_trails.clear()
        return trails

    def _on_phase_change(self, old_phase, new_phase):
        """Phase transition effect — reset timers."""
        self.spread_timer = 0
        self.charge_timer = 0
        self.charge_state = None

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive and self.boss_state != BossState.DEFEATED:
            return
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        # Charging shake
        if self.charge_state == "telegraph":
            bx += random.randint(-3, 3)
            by += random.randint(-3, 3)

        if self._sprite:
            # Front-facing bottle sprite — never flip (text would appear mirrored)
            sprite = self._sprite
            # Hit flash: white tint
            if self.hit_timer > 0:
                flash = sprite.copy()
                flash.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MAX)
                surf.blit(flash, (bx, by))
            elif self.phase >= 2:
                # Phase 2: red tint overlay
                tinted = sprite.copy()
                tint = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
                tint.fill((120, 0, 0, 50))
                tinted.blit(tint, (0, 0))
                surf.blit(tinted, (bx, by))
            else:
                surf.blit(sprite, (bx, by))
            # Angry eyes in phase 2
            if self.phase >= 2:
                eye_y = by + 50
                for ex_off in [30, self.w - 45]:
                    pygame.draw.line(surf, (220, 40, 40),
                                     (bx + ex_off, eye_y - 3),
                                     (bx + ex_off + 16, eye_y + 3), 3)
            # Tiny legs
            leg_y = by + self.h - 12
            pygame.draw.rect(surf, self.color, (bx + 25, leg_y, 14, 12))
            pygame.draw.rect(surf, self.color, (bx + self.w - 39, leg_y, 14, 12))
        else:
            # Programmatic fallback
            color = (255, 255, 255) if self.hit_timer > 0 else self.color
            body_rect = (bx + 10, by + 40, self.w - 20, self.h - 40)
            pygame.draw.rect(surf, color, body_rect, border_radius=16)
            neck_rect = (bx + 30, by + 15, self.w - 60, 40)
            pygame.draw.rect(surf, color, neck_rect, border_radius=12)
            cap_rect = (bx + 35, by, self.w - 70, 25)
            pygame.draw.rect(surf, (200, 200, 210), cap_rect, border_radius=8)
            pygame.draw.rect(surf, (60, 120, 160), body_rect, 2, border_radius=16)

        # Vulnerable state dizzy stars
        if self.charge_state == "vulnerable":
            t = self.frame_count * 0.1
            for i in range(3):
                angle = t + i * (2 * math.pi / 3)
                sx = bx + self.w // 2 + int(math.cos(angle) * 30)
                sy = by - 15 + int(math.sin(angle) * 8)
                pygame.draw.circle(surf, (255, 255, 100), (sx, sy), 5)


# ═══════════════════════════════════════════════════════════════════════
# THE CLEANSER — Floor 8-10 Platform Boss
# ═══════════════════════════════════════════════════════════════════════

class TheCleanser(Boss):
    """Armored warrior boss. Only vulnerable when stunned via elbow nerve hit.
    Must be struck from above with a jelly shot, then ground pounded."""

    def __init__(self, x, y, arena_left=100, arena_right=1180):
        super().__init__(x, y, w=125, h=162,
                         health=CLEANSER_HP,
                         boss_type=BossType.CLEANSER)
        self.boss_name = "THE CLEANSER"
        self.max_phases = 5
        self.phase_thresholds = [0.8, 0.6, 0.4, 0.2]
        self.color = (160, 130, 100)
        self.arena_bounds = (arena_left, arena_right)

        # Sprite (warrior art, scaled up)
        self._sprite = load_sprite('enemies/sanitizer-warrior-front-view.png', 100, 130)
        self._sprite_flipped = flip_h(self._sprite) if self._sprite else None

        # Movement
        self.patrol_speed = 1.5
        self.patrol_dir = 1

        # Attack timers
        self.glob_timer = 0
        self.glob_cooldown = 60
        self.swing_timer = 0
        self.swing_cooldown = 150
        self.swing_active = False
        self.swing_frame = 0
        self.swing_duration = 20

        # Stun mechanics
        self.stun_timer = 0
        self.stun_duration = 90  # frames, changes with phase
        self.recover_timer = 0
        self.recover_duration = 30

        # Elbow hitbox (small, positioned near arm)
        self.elbow_offset_x = 30  # relative to boss x (facing right)
        self.elbow_offset_y = 20  # relative to boss y
        self.elbow_w = 12
        self.elbow_h = 12

        # Helmet blocks head damage
        self.has_helmet = True

        # Pending projectiles
        self.pending_globs = []
        self.pending_puddles = []

        # Invulnerable by default — only take damage when stunned
        self.invulnerable = True

    def get_elbow_hitbox(self):
        """Return the elbow nerve hitbox rect."""
        if self.facing == 1:
            ex = self.x + self.elbow_offset_x
        else:
            ex = self.x + self.w - self.elbow_offset_x - self.elbow_w
        ey = self.y + self.elbow_offset_y
        return pygame.Rect(int(ex), int(ey), self.elbow_w, self.elbow_h)

    def get_head_hitbox(self):
        """Return the helmet/head hitbox rect (ground pound blocked here)."""
        return pygame.Rect(int(self.x + 8), int(self.y), self.w - 16, 14)

    def try_elbow_hit(self, projectile_y):
        """Check if a projectile came from above (platform hit).
        Returns True if the boss should be stunned."""
        if self.boss_state in (BossState.STUNNED, BossState.RECOVERING):
            return False
        # Projectile must come from above the boss
        if projectile_y < self.y:
            self._enter_stun()
            return True
        return False

    def _enter_stun(self):
        """Transition to stunned state — drop weapon, become vulnerable."""
        self.boss_state = BossState.STUNNED
        self.invulnerable = False
        self.swing_active = False
        # Phase-dependent stun duration
        if self.phase <= 2:
            self.stun_duration = 90
        elif self.phase <= 4:
            self.stun_duration = 60
        else:
            self.stun_duration = 45
        self.stun_timer = self.stun_duration

    def _enter_recover(self):
        """Transition to recovering — stand back up, become invulnerable."""
        self.boss_state = BossState.RECOVERING
        self.invulnerable = True
        self.recover_timer = self.recover_duration

    def update(self, player):
        super().update(player)
        if self.intro_active or not self.alive:
            return

        # Phase-dependent speed
        if self.phase >= 5:
            speed_mult = 2.0
        elif self.phase >= 3:
            speed_mult = 1.5
        else:
            speed_mult = 1.0

        # State machine
        if self.boss_state == BossState.STUNNED:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self._enter_recover()
            return

        if self.boss_state == BossState.RECOVERING:
            self.recover_timer -= 1
            if self.recover_timer <= 0:
                self.boss_state = BossState.PATROL
                self.invulnerable = True
            return

        # Patrol
        self.facing = 1 if player.x > self.x else -1
        self.x += self.patrol_dir * self.patrol_speed * speed_mult
        left, right = self.arena_bounds
        if self.x <= left:
            self.patrol_dir = 1
        elif self.x + self.w >= right:
            self.patrol_dir = -1
        self._clamp_to_arena()

        # Glob attack
        self.glob_timer += 1
        glob_cd = max(30, int(self.glob_cooldown / speed_mult))
        if self.glob_timer >= glob_cd:
            self.glob_timer = 0
            self._fire_glob(player)

        # Swing attack (creates puddles)
        self.swing_timer += 1
        swing_cd = max(80, int(self.swing_cooldown / speed_mult))
        if self.swing_timer >= swing_cd:
            self.swing_timer = 0
            self.swing_active = True
            self.swing_frame = 0

        if self.swing_active:
            self.swing_frame += 1
            if self.swing_frame == self.swing_duration // 2:
                # Create 3 puddles in front
                for i in range(3):
                    px = self.x + self.facing * (20 + i * 24)
                    py = self.y + self.h - 8
                    puddle = SanitizerPuddle(px, py)
                    self.pending_puddles.append(puddle)
            if self.swing_frame >= self.swing_duration:
                self.swing_active = False

    def _fire_glob(self, player):
        """Fire a sanitizer glob toward the player."""
        cx = self.x + self.w / 2 + self.facing * 20
        cy = self.y + 10
        ground_y = self.y + self.h + 100  # approximate ground
        glob = SanitizerGlob(cx, cy,
                             player.x + player.w / 2,
                             player.y + player.h / 2,
                             ground_y)
        self.pending_globs.append(glob)

    def consume_pending_projectiles(self):
        """Return (globs, puddles) and clear buffers."""
        globs = self.pending_globs[:]
        puddles = self.pending_puddles[:]
        self.pending_globs.clear()
        self.pending_puddles.clear()
        return globs, puddles

    def _on_phase_change(self, old_phase, new_phase):
        """Reset attack timers on phase change."""
        self.glob_timer = 0
        self.swing_timer = 0

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive and self.boss_state != BossState.DEFEATED:
            return
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        if self._sprite:
            # Front-facing bottle — never flip (text would appear mirrored)
            sprite = self._sprite
            if self.hit_timer > 0:
                flash = sprite.copy()
                flash.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MAX)
                surf.blit(flash, (bx, by))
            else:
                surf.blit(sprite, (bx, by))
            # Blue flame glow above helmet
            if self.has_helmet:
                flame_cx = bx + self.w // 2
                flame_base_y = by + 4
                num_pts = 7
                flame_pts = []
                for i in range(num_pts):
                    fx = flame_cx - 20 + (40 * i / (num_pts - 1))
                    flicker = math.sin(self.frame_count * 0.15 + i * 0.8) * 5
                    fy = flame_base_y - 16 - abs(i - num_pts // 2) * 3 + flicker
                    flame_pts.append((int(fx), int(fy)))
                flame_pts.append((flame_cx + 20, flame_base_y))
                flame_pts.append((flame_cx - 20, flame_base_y))
                if len(flame_pts) >= 3:
                    pygame.draw.polygon(surf, (60, 140, 255), flame_pts)
        else:
            # Programmatic fallback
            color = (255, 255, 255) if self.hit_timer > 0 else self.color
            body_rect = (bx + 8, by + 30, self.w - 16, self.h - 50)
            pygame.draw.rect(surf, color, body_rect, border_radius=6)
            head_rect = (bx + 15, by + 8, self.w - 30, 28)
            pygame.draw.rect(surf, color, head_rect, border_radius=8)

        # Stunned state visual
        if self.boss_state == BossState.STUNNED:
            t = self.frame_count * 0.12
            for i in range(4):
                angle = t + i * (math.pi / 2)
                sx = bx + self.w // 2 + int(math.cos(angle) * 30)
                sy = by - 12 + int(math.sin(angle) * 8)
                pygame.draw.circle(surf, (255, 255, 100), (sx, sy), 5)

            # Dropped weapon on ground
            wx = bx + self.facing * 30
            wy = by + self.h - 8
            pygame.draw.rect(surf, (140, 120, 100),
                             (wx, wy, 20, 6), border_radius=2)
            pygame.draw.circle(surf, (180, 160, 140), (wx + 20, wy + 3), 5)

        # Elbow hitbox debug visualization (subtle glow)
        elbow = self.get_elbow_hitbox()
        if self.boss_state not in (BossState.STUNNED, BossState.RECOVERING):
            glow = pygame.Surface((elbow.w + 4, elbow.h + 4), pygame.SRCALPHA)
            pulse = int(40 + 20 * math.sin(self.frame_count * 0.1))
            pygame.draw.rect(glow, (255, 200, 50, pulse),
                             (0, 0, elbow.w + 4, elbow.h + 4), border_radius=3)
            surf.blit(glow, (int(elbow.x + ox) - 2, int(elbow.y + oy) - 2))


# ═══════════════════════════════════════════════════════════════════════
# THE LAST GUARD — Floor 15 Final Boss
# ═══════════════════════════════════════════════════════════════════════

class TheLastGuard(Boss):
    """The final boss. 3 phases: The Chase, Hand-to-Hand, The Arrows.
    Radiance-level difficulty."""

    def __init__(self, x, y, arena_left=100, arena_right=1180):
        super().__init__(x, y, w=112, h=138,
                         health=LAST_GUARD_HP,
                         boss_type=BossType.LAST_GUARD)
        self.boss_name = "THE LAST GUARD"
        self.max_phases = 3
        self.phase_thresholds = [0.66, 0.33]
        self.color = (140, 120, 100)
        self.arena_bounds = (arena_left, arena_right)

        # Phase 1: The Chase (must be faster than PLAYER_SPEED=5.0 to catch up)
        self.chase_speed = 6.5
        self.grab_timer = 0
        self.grab_cooldown = 45
        self.grab_active = False
        self.grab_frame = 0
        self.grab_duration = 15
        self.grab_rect_w = 60
        self.grab_rect_h = 40

        # Phase 2: Hand-to-Hand
        self.combo_state = None  # None, "telegraph", "punch", "cooldown"
        self.combo_index = 0  # which punch (0, 1, 2)
        self.combo_timer = 0
        self.combo_telegraph = 20
        self.combo_cooldown_timer = 0
        self.combo_cooldown = 40
        self.slam_state = None  # None, "telegraph", "slam", "vulnerable"
        self.slam_timer = 0
        self.slam_telegraph = 40
        self.slam_damage = 30
        self.slam_radius = 80
        self.vulnerable_timer = 0
        self.vulnerable_duration = 30
        self.attack_choice_timer = 0

        # Phase 3: The Arrows
        self.arrow_timer = 0
        self.arrow_rate = 15  # frames between arrows (4/sec)
        self.aimed_arrow_timer = 0
        self.aimed_arrow_cooldown = 90
        self.retreat_position = None

        # Pending projectiles
        self.pending_arrows = []
        # Shockwave data for combat system
        self.active_shockwave = None  # (cx, cy, radius, damage) or None

        # Grab hitbox for combat system
        self.active_grab = None  # pygame.Rect or None

    def update(self, player):
        super().update(player)
        if self.intro_active or not self.alive:
            return

        # Clear transient attack data
        self.active_shockwave = None
        self.active_grab = None

        if self.phase == 1:
            self._update_phase1(player)
        elif self.phase == 2:
            self._update_phase2(player)
        elif self.phase == 3:
            self._update_phase3(player)

        self._clamp_to_arena()

    def _update_phase1(self, player):
        """The Chase — aggressive running + grabbing hand attack."""
        # Run toward player
        dx = player.x - self.x
        direction = 1 if dx > 0 else -1
        self.facing = direction
        self.x += direction * self.chase_speed
        self._clamp_to_arena()

        # Grab attack
        self.grab_timer += 1
        if self.grab_timer >= self.grab_cooldown:
            self.grab_timer = 0
            self.grab_active = True
            self.grab_frame = 0

        if self.grab_active:
            self.grab_frame += 1
            # Active grab hitbox — extends from boss center outward so it
            # connects even when the boss overlaps the player.
            if self.facing == 1:
                gx = self.x + self.w // 2
            else:
                gx = self.x - self.grab_rect_w + self.w // 2
            gy = self.y + self.h // 2 - self.grab_rect_h // 2
            self.active_grab = pygame.Rect(int(gx), int(gy),
                                           self.grab_rect_w, self.grab_rect_h)
            if self.grab_frame >= self.grab_duration:
                self.grab_active = False

    def _update_phase2(self, player):
        """Hand-to-Hand — punch combo and overhead slam."""
        # Stand ground, face player
        dx = player.x - self.x
        self.facing = 1 if dx > 0 else -1

        # Vulnerable state after combo/slam
        if self.boss_state == BossState.VULNERABLE:
            self.vulnerable_timer -= 1
            if self.vulnerable_timer <= 0:
                self.boss_state = BossState.PATROL
                self.invulnerable = False
            return

        # Combo state machine
        if self.combo_state is not None:
            self._update_combo(player)
            return

        # Slam state machine
        if self.slam_state is not None:
            self._update_slam(player)
            return

        # Choose next attack
        self.attack_choice_timer += 1
        if self.attack_choice_timer >= 60:
            self.attack_choice_timer = 0
            if random.random() < 0.6:
                self.combo_state = "telegraph"
                self.combo_index = 0
                self.combo_timer = self.combo_telegraph
            else:
                self.slam_state = "telegraph"
                self.slam_timer = self.slam_telegraph

    def _update_combo(self, player):
        """3-hit punch combo state machine."""
        if self.combo_state == "telegraph":
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_state = "punch"
                self.combo_timer = 8  # punch active frames
        elif self.combo_state == "punch":
            # Active punch hitbox
            if self.facing == 1:
                px = self.x + self.w
            else:
                px = self.x - 30
            py = self.y + 20
            self.active_grab = pygame.Rect(int(px), int(py), 30, 20)
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_index += 1
                if self.combo_index >= 3:
                    # Combo complete, vulnerable
                    self.combo_state = None
                    self.combo_index = 0
                    self._enter_vulnerable()
                else:
                    self.combo_state = "telegraph"
                    self.combo_timer = self.combo_telegraph
        elif self.combo_state == "cooldown":
            self.combo_cooldown_timer -= 1
            if self.combo_cooldown_timer <= 0:
                self.combo_state = None

    def _update_slam(self, player):
        """Overhead slam with shockwave."""
        if self.slam_state == "telegraph":
            self.slam_timer -= 1
            if self.slam_timer <= 0:
                self.slam_state = "slam"
                self.slam_timer = 10
        elif self.slam_state == "slam":
            self.slam_timer -= 1
            if self.slam_timer <= 0:
                # Create shockwave
                cx = self.x + self.w / 2
                cy = self.y + self.h
                self.active_shockwave = (cx, cy, self.slam_radius, self.slam_damage)
                self.slam_state = None
                self._enter_vulnerable()

    def _enter_vulnerable(self):
        """Boss becomes briefly vulnerable after an attack."""
        self.boss_state = BossState.VULNERABLE
        self.vulnerable_timer = self.vulnerable_duration

    def _update_phase3(self, player):
        """The Arrows — retreat and rain arrows from above."""
        # Retreat to center-top of arena
        if self.retreat_position is None:
            arena_cx = (self.arena_bounds[0] + self.arena_bounds[1]) / 2
            self.retreat_position = (arena_cx - self.w / 2, self.y - 100)

        # Move toward retreat position
        tx, ty = self.retreat_position
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 4:
            self.x += (dx / max(1, dist)) * 3.0
            self.y += (dy / max(1, dist)) * 3.0

        self.facing = 1 if player.x > self.x else -1

        # Rain arrows
        self.arrow_timer += 1
        if self.arrow_timer >= self.arrow_rate:
            self.arrow_timer = 0
            left, right = self.arena_bounds
            ax = random.uniform(left + 20, right - 20)
            ay = self.y - 50  # from above
            arrow = SanitizerArrow(ax, ay, ax, ay + 300)
            self.pending_arrows.append(arrow)

        # Aimed arrow
        self.aimed_arrow_timer += 1
        if self.aimed_arrow_timer >= self.aimed_arrow_cooldown:
            self.aimed_arrow_timer = 0
            cx = self.x + self.w / 2
            cy = self.y + self.h / 2
            arrow = SanitizerArrow(cx, cy,
                                   player.x + player.w / 2,
                                   player.y + player.h / 2)
            self.pending_arrows.append(arrow)

    def consume_pending_arrows(self):
        """Return list of pending arrows and clear buffer."""
        arrows = self.pending_arrows[:]
        self.pending_arrows.clear()
        return arrows

    def _on_phase_change(self, old_phase, new_phase):
        """Reset states on phase change."""
        self.combo_state = None
        self.slam_state = None
        self.grab_active = False
        self.boss_state = BossState.PATROL
        self.invulnerable = False
        self.attack_choice_timer = 0

    def take_damage(self, amount):
        """Last Guard takes damage normally in phases 1 and 3,
        only when vulnerable in phase 2."""
        if self.phase == 2 and self.boss_state != BossState.VULNERABLE:
            return False
        return super().take_damage(amount)

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive and self.boss_state != BossState.DEFEATED:
            return
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        color = (255, 255, 255) if self.hit_timer > 0 else self.color
        dark = (max(0, color[0] - 40), max(0, color[1] - 40),
                max(0, color[2] - 40))

        # Defeated animation — sitting down
        if self.boss_state == BossState.DEFEATED:
            # Sitting pose
            pygame.draw.rect(surf, color,
                             (bx + 4, by + 30, self.w - 8, 42), border_radius=6)
            # Head drooped
            pygame.draw.ellipse(surf, color,
                                (bx + 10, by + 20, self.w - 20, 18))
            return

        # Phase 1: Running pose
        if self.phase == 1:
            # Leaning forward body
            lean = 4
            body_points = [
                (bx + lean + 4, by + 14),
                (bx + self.w - 4 + lean, by + 14),
                (bx + self.w - 4, by + self.h - 16),
                (bx + 4, by + self.h - 16),
            ]
            pygame.draw.polygon(surf, color, body_points)

            # Running legs (animated)
            leg_anim = math.sin(self.frame_count * 0.2) * 8
            pygame.draw.line(surf, dark,
                             (bx + 14, by + self.h - 16),
                             (bx + 14 + int(leg_anim), by + self.h), 5)
            pygame.draw.line(surf, dark,
                             (bx + self.w - 14, by + self.h - 16),
                             (bx + self.w - 14 - int(leg_anim), by + self.h), 5)

            # Head
            pygame.draw.ellipse(surf, color,
                                (bx + 10 + lean, by, self.w - 20, 20))

            # Grabbing hand
            if self.grab_active:
                hand_x = bx + (self.w if self.facing == 1 else -20)
                hand_y = by + self.h // 2 - 10
                pygame.draw.rect(surf, (180, 160, 140),
                                 (hand_x, hand_y, 20, 20), border_radius=4)
                # Fingers
                for fy in range(hand_y + 2, hand_y + 18, 5):
                    fx = hand_x + (18 if self.facing == 1 else -4)
                    pygame.draw.rect(surf, (180, 160, 140),
                                     (fx, fy, 6, 3), border_radius=1)

        # Phase 2: Fighting stance
        elif self.phase == 2:
            # Wide stance body
            pygame.draw.rect(surf, color,
                             (bx + 6, by + 14, self.w - 12, self.h - 28),
                             border_radius=5)
            # Legs spread
            pygame.draw.rect(surf, dark, (bx + 2, by + self.h - 16, 12, 16))
            pygame.draw.rect(surf, dark,
                             (bx + self.w - 14, by + self.h - 16, 12, 16))
            # Fists
            fist_y = by + 24
            pygame.draw.circle(surf, (180, 160, 140),
                               (bx - 2, fist_y), 7)
            pygame.draw.circle(surf, (180, 160, 140),
                               (bx + self.w + 2, fist_y), 7)
            # Head
            pygame.draw.ellipse(surf, color,
                                (bx + 10, by, self.w - 20, 18))

            # Vulnerable glow
            if self.boss_state == BossState.VULNERABLE:
                vuln_surf = pygame.Surface((self.w + 8, self.h + 8),
                                          pygame.SRCALPHA)
                pulse = int(60 + 30 * math.sin(self.frame_count * 0.2))
                pygame.draw.rect(vuln_surf, (255, 255, 100, pulse),
                                 (0, 0, self.w + 8, self.h + 8),
                                 border_radius=8)
                surf.blit(vuln_surf, (bx - 4, by - 4))

            # Slam telegraph
            if self.slam_state == "telegraph":
                # Raised arms
                progress = 1.0 - (self.slam_timer / self.slam_telegraph)
                arm_raise = int(progress * 30)
                pygame.draw.line(surf, (180, 160, 140),
                                 (bx + self.w // 2, by + 14),
                                 (bx + self.w // 2, by - arm_raise), 6)
                # Warning circle on ground
                if self.frame_count % 10 < 5:
                    warn_surf = pygame.Surface(
                        (self.slam_radius * 2, 20), pygame.SRCALPHA)
                    pygame.draw.ellipse(warn_surf, (255, 60, 60, 60),
                                        (0, 0, self.slam_radius * 2, 20))
                    surf.blit(warn_surf,
                              (bx + self.w // 2 - self.slam_radius,
                               by + self.h - 10))

        # Phase 3: Elevated archer
        elif self.phase == 3:
            # Body
            pygame.draw.rect(surf, color,
                             (bx + 8, by + 10, self.w - 16, self.h - 24),
                             border_radius=5)
            # Legs
            pygame.draw.rect(surf, dark,
                             (bx + 10, by + self.h - 16, 10, 16))
            pygame.draw.rect(surf, dark,
                             (bx + self.w - 20, by + self.h - 16, 10, 16))
            # Head
            pygame.draw.ellipse(surf, color,
                                (bx + 12, by, self.w - 24, 16))

            # Bow
            bow_x = bx + (self.w + 4 if self.facing == 1 else -12)
            bow_y = by + 16
            pygame.draw.arc(surf, (100, 80, 60),
                            (bow_x - 4, bow_y - 10, 12, 30),
                            -1.2 if self.facing == 1 else 1.9,
                            1.2 if self.facing == 1 else 4.3, 3)
            # Arrow nocked
            if self.aimed_arrow_timer > self.aimed_arrow_cooldown - 20:
                ax = bow_x + (6 if self.facing == 1 else -6)
                pygame.draw.line(surf, (200, 180, 160),
                                 (ax, bow_y - 4), (ax, bow_y + 12), 2)

        # Eyes (all phases)
        eye_y = by + 6
        eye_lx = bx + 14
        eye_rx = bx + self.w - 20
        if self.phase == 1:
            eye_y += 2  # slight offset for running lean
            eye_lx += 4
            eye_rx += 4
        pygame.draw.circle(surf, WHITE, (eye_lx, eye_y), 3)
        pygame.draw.circle(surf, WHITE, (eye_rx, eye_y), 3)
        pupil_off = self.facing * 1
        pygame.draw.circle(surf, (20, 20, 40), (eye_lx + pupil_off, eye_y), 2)
        pygame.draw.circle(surf, (20, 20, 40), (eye_rx + pupil_off, eye_y), 2)


# ═══════════════════════════════════════════════════════════════════════
# GRACIE — Secret Floor 2 Boss
# ═══════════════════════════════════════════════════════════════════════

class Gracie(Boss):
    """Secret boss. Playful, fast, mimics player. 2 phases."""

    def __init__(self, x, y, arena_left=100, arena_right=1180):
        super().__init__(x, y, w=60, h=120,
                         health=GRACIE_HP,
                         boss_type=BossType.GRACIE)
        self.boss_name = "GRACIE"
        self.max_phases = 2
        self.phase_thresholds = [0.5]
        self.color = (60, 180, 80)
        self.arena_bounds = (arena_left, arena_right)

        # Movement
        self.speed = 4.0
        self.move_dir = 1

        # Copy Cat mechanic — mirrors player last action after delay
        self.player_last_action = None  # ("jump", "shoot", "dodge", etc.)
        self.player_action_timer = 0
        self.copy_delay = 60  # frames before copying

        # Tag You're It
        self.tag_timer = 0
        self.tag_cooldown = 180
        self.tag_sprint_speed = 7.0
        self.tag_active = False
        self.tag_sprint_timer = 0
        self.tag_sprint_duration = 40
        # Result: reverses player controls for 120 frames
        self.tag_reverse_active = False

        # Cannonball
        self.cannonball_timer = 0
        self.cannonball_cooldown = 240
        self.cannonball_state = None  # None, "jump", "fall", "shockwave"
        self.cannonball_vy = 0.0
        self.cannonball_ground_y = 0.0
        self.cannonball_shockwave_radius = 120
        self.cannonball_shockwave_damage = 10

        # Look What I Found (projectile throw)
        self.throw_timer = 0
        self.throw_cooldown = 120

        # Phase 2 extras
        self.consecutive_hits = 0
        self.tantrum_timer = 0
        self.tantrum_duration = 90
        self.tantrum_active = False
        self.dash_away_timer = 0

        # Pending effects
        self.pending_projectiles = []
        self.active_shockwave = None  # (cx, cy, radius, damage)
        self.spawn_enemies = []  # list of small enemies to spawn

        # Defeat animation
        self.defeat_timer = 0
        self.defeat_duration = 180

    def record_player_action(self, action):
        """Called by combat system when player does something — for Copy Cat."""
        self.player_last_action = action
        self.player_action_timer = 0

    def update(self, player):
        super().update(player)
        if self.intro_active or not self.alive:
            return

        # Clear transient data
        self.active_shockwave = None

        speed = 5.0 if self.phase >= 2 else self.speed

        # Phase 2 tantrum check
        if self.phase >= 2 and self.tantrum_active:
            self.tantrum_timer -= 1
            if self.tantrum_timer <= 0:
                self.tantrum_active = False
                self.consecutive_hits = 0
            return  # frozen during tantrum

        # Cannonball state machine takes priority
        if self.cannonball_state is not None:
            self._update_cannonball(player)
            return

        # Tag sprint
        if self.tag_active:
            self._update_tag(player)
            return

        # General movement — bouncy, unpredictable
        self.facing = 1 if player.x > self.x else -1
        if self.phase >= 2 and self.dash_away_timer > 0:
            # Dash away after attack (hit-and-run)
            self.x -= self.facing * speed * 1.5
            self.dash_away_timer -= 1
        else:
            # Move toward player loosely
            dx = player.x - self.x
            if abs(dx) > 60:
                self.x += self.facing * speed * 0.6
        self._clamp_to_arena()

        # Copy Cat
        if self.player_last_action is not None:
            self.player_action_timer += 1
            if self.player_action_timer >= self.copy_delay:
                self._do_copy_cat(player)
                self.player_last_action = None

        # Tag You're It
        self.tag_timer += 1
        tag_cd = self.tag_cooldown if self.phase == 1 else 120
        if self.tag_timer >= tag_cd:
            self.tag_timer = 0
            self.tag_active = True
            self.tag_sprint_timer = self.tag_sprint_duration

        # Cannonball
        self.cannonball_timer += 1
        cannon_cd = self.cannonball_cooldown if self.phase == 1 else 160
        if self.cannonball_timer >= cannon_cd:
            self.cannonball_timer = 0
            self.cannonball_state = "jump"
            self.cannonball_vy = -14.0
            self.cannonball_ground_y = self.y + self.h

        # Look What I Found
        self.throw_timer += 1
        throw_cd = self.throw_cooldown if self.phase == 1 else 80
        if self.throw_timer >= throw_cd:
            self.throw_timer = 0
            self._throw_projectile(player)

        # Phase 2: I'm Telling Mom (spawn minions)
        if self.phase >= 2 and self.frame_count % 600 == 0:
            self._spawn_minions()

    def take_damage(self, amount):
        """Track consecutive hits for tantrum."""
        result = super().take_damage(amount)
        if self.phase >= 2 and self.alive:
            self.consecutive_hits += 1
            if self.consecutive_hits >= 3:
                self.tantrum_active = True
                self.tantrum_timer = self.tantrum_duration
            # Hit-and-run dash away
            self.dash_away_timer = 20
        return result

    def _do_copy_cat(self, player):
        """Mirror the player's last action."""
        action = self.player_last_action
        if action == "jump":
            self.cannonball_state = "jump"
            self.cannonball_vy = -10.0
            self.cannonball_ground_y = self.y + self.h
        elif action == "shoot":
            self._throw_projectile(player)

    def _update_tag(self, player):
        """Sprint toward player for tag."""
        dx = player.x - self.x
        self.facing = 1 if dx > 0 else -1
        self.x += self.facing * self.tag_sprint_speed
        self._clamp_to_arena()
        self.tag_sprint_timer -= 1
        if self.tag_sprint_timer <= 0 or abs(dx) < 10:
            self.tag_active = False

    def get_tag_rect(self):
        """Return tag collision rect when tag is active."""
        if not self.tag_active:
            return None
        return self.get_rect()

    def _update_cannonball(self, player):
        """Cannonball jump state machine."""
        if self.cannonball_state == "jump":
            self.cannonball_vy += 0.8  # gravity
            self.y += self.cannonball_vy
            if self.cannonball_vy > 0 and self.y + self.h >= self.cannonball_ground_y:
                self.y = self.cannonball_ground_y - self.h
                self.cannonball_state = "shockwave"
                self.active_shockwave = (
                    self.x + self.w / 2,
                    self.y + self.h,
                    self.cannonball_shockwave_radius,
                    self.cannonball_shockwave_damage,
                )
        elif self.cannonball_state == "shockwave":
            self.cannonball_state = None

    def _throw_projectile(self, player):
        """Throw a small arcing projectile at the player."""
        cx = self.x + self.w / 2
        cy = self.y + self.h / 4
        # Use SanitizerGlob as the arcing projectile
        ground_y = player.y + player.h
        proj = SanitizerGlob(cx, cy,
                             player.x + player.w / 2,
                             player.y + player.h / 2,
                             ground_y)
        proj.damage = 10
        self.pending_projectiles.append(proj)

    def _spawn_minions(self):
        """Spawn 3 small roly-poly enemies."""
        for i in range(3):
            offset = (i - 1) * 60
            self.spawn_enemies.append({
                'x': self.x + offset,
                'y': self.y,
                'hp': 10,
            })

    def consume_pending_projectiles(self):
        """Return pending projectiles and clear."""
        projs = self.pending_projectiles[:]
        self.pending_projectiles.clear()
        return projs

    def consume_spawn_enemies(self):
        """Return list of enemy spawn dicts and clear."""
        spawns = self.spawn_enemies[:]
        self.spawn_enemies.clear()
        return spawns

    def _on_phase_change(self, old_phase, new_phase):
        """Reset on phase change."""
        self.tag_timer = 0
        self.cannonball_timer = 0
        self.throw_timer = 0
        self.consecutive_hits = 0

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive and self.boss_state != BossState.DEFEATED:
            # Defeat animation: smile, bounce, cartwheel
            self._draw_defeat(surf, camera_offset)
            return

        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        # Phase color
        if self.phase >= 2:
            base_color = (
                max(0, self.color[0] - 20),
                min(255, self.color[1] + 30),
                max(0, self.color[2] - 20),
            )
        else:
            base_color = self.color

        color = (255, 255, 255) if self.hit_timer > 0 else base_color
        outline = (30, 100, 40)

        body_cx = bx + self.w // 2
        bounce = int(math.sin(self.frame_count * 0.15) * 3)

        # ── Muscular humanoid body ──

        # Legs (thick, planted)
        leg_top = by + 76 + bounce
        leg_h = 40
        # Left leg
        pygame.draw.rect(surf, color, (bx + 6, leg_top, 16, leg_h))
        pygame.draw.rect(surf, outline, (bx + 6, leg_top, 16, leg_h), 2)
        # Right leg
        pygame.draw.rect(surf, color, (bx + self.w - 22, leg_top, 16, leg_h))
        pygame.draw.rect(surf, outline, (bx + self.w - 22, leg_top, 16, leg_h), 2)
        # Feet
        pygame.draw.ellipse(surf, color, (bx + 2, leg_top + leg_h - 4, 22, 10))
        pygame.draw.ellipse(surf, color, (bx + self.w - 24, leg_top + leg_h - 4, 22, 10))

        # Torso (tall trapezoid — broad shoulders, narrow waist)
        torso_top = by + 24 + bounce
        torso_pts = [
            (body_cx - 22, torso_top),       # top-left (shoulders)
            (body_cx + 22, torso_top),       # top-right
            (body_cx + 14, torso_top + 54),  # bottom-right (waist)
            (body_cx - 14, torso_top + 54),  # bottom-left
        ]
        pygame.draw.polygon(surf, color, torso_pts)
        pygame.draw.polygon(surf, outline, torso_pts, 2)

        # Chest definition (V shape for muscularity)
        chest_y = torso_top + 10
        pygame.draw.line(surf, outline, (body_cx, chest_y),
                         (body_cx - 12, chest_y + 18), 2)
        pygame.draw.line(surf, outline, (body_cx, chest_y),
                         (body_cx + 12, chest_y + 18), 2)

        # Arms (thick, muscular)
        arm_y = torso_top + 4
        # Left arm
        pygame.draw.rect(surf, color, (bx - 10, arm_y, 14, 36))
        pygame.draw.rect(surf, outline, (bx - 10, arm_y, 14, 36), 2)
        # Left fist
        pygame.draw.circle(surf, color, (bx - 3, arm_y + 38), 8)
        pygame.draw.circle(surf, outline, (bx - 3, arm_y + 38), 8, 2)
        # Right arm
        pygame.draw.rect(surf, color, (bx + self.w - 4, arm_y, 14, 36))
        pygame.draw.rect(surf, outline, (bx + self.w - 4, arm_y, 14, 36), 2)
        # Right fist
        pygame.draw.circle(surf, color, (bx + self.w + 3, arm_y + 38), 8)
        pygame.draw.circle(surf, outline, (bx + self.w + 3, arm_y + 38), 8, 2)

        # Head
        head_cx = body_cx
        head_cy = by + 14 + bounce
        pygame.draw.ellipse(surf, color, (head_cx - 14, head_cy - 14, 28, 28))
        pygame.draw.ellipse(surf, outline, (head_cx - 14, head_cy - 14, 28, 28), 2)

        # Eyes (narrow, menacing)
        eye_y = head_cy - 3
        eye_lx = head_cx - 9
        eye_rx = head_cx + 3
        pygame.draw.ellipse(surf, (200, 220, 200), (eye_lx, eye_y, 8, 5))
        pygame.draw.ellipse(surf, (200, 220, 200), (eye_rx, eye_y, 8, 5))
        # Pupils (red for menace)
        pupil_off = self.facing * 2
        pygame.draw.circle(surf, (180, 30, 30),
                           (eye_lx + 4 + pupil_off, eye_y + 3), 2)
        pygame.draw.circle(surf, (180, 30, 30),
                           (eye_rx + 4 + pupil_off, eye_y + 3), 2)

        # Mouth
        mouth_y = head_cy + 5
        if self.phase == 1:
            # Snarl
            pygame.draw.line(surf, outline,
                             (head_cx - 6, mouth_y), (head_cx + 6, mouth_y), 2)
            # Fangs
            pygame.draw.line(surf, WHITE,
                             (head_cx - 4, mouth_y), (head_cx - 3, mouth_y + 3), 2)
            pygame.draw.line(surf, WHITE,
                             (head_cx + 4, mouth_y), (head_cx + 3, mouth_y + 3), 2)
        else:
            # Angry open mouth with fangs
            pygame.draw.ellipse(surf, (40, 20, 20),
                                (head_cx - 7, mouth_y - 2, 14, 8))
            pygame.draw.line(surf, WHITE,
                             (head_cx - 5, mouth_y - 1), (head_cx - 3, mouth_y + 4), 2)
            pygame.draw.line(surf, WHITE,
                             (head_cx + 5, mouth_y - 1), (head_cx + 3, mouth_y + 4), 2)
            # Angry eyebrows (V shape)
            pygame.draw.line(surf, outline,
                             (eye_lx, eye_y - 1),
                             (eye_lx + 8, eye_y - 4), 2)
            pygame.draw.line(surf, outline,
                             (eye_rx + 8, eye_y - 1),
                             (eye_rx, eye_y - 4), 2)

        # Phase 2: green energy wisps
        if self.phase >= 2:
            for i in range(3):
                t = self.frame_count * 0.05 + i * 2.0
                sx = body_cx - 6 + i * 6 + int(math.sin(t) * 3)
                sy = by - 4 - i * 4 + bounce
                alpha = max(0, 120 - i * 40)
                wisp = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(wisp, (100, 255, 120, alpha), (4, 4), 4)
                surf.blit(wisp, (sx, sy))

        # Tantrum indicator
        if self.tantrum_active:
            tantrum_surf = pygame.Surface((self.w + 16, self.h + 16),
                                         pygame.SRCALPHA)
            pulse = int(80 + 40 * math.sin(self.frame_count * 0.3))
            pygame.draw.ellipse(tantrum_surf, (100, 255, 100, pulse),
                                (0, 0, self.w + 16, self.h + 16))
            surf.blit(tantrum_surf, (bx - 8, by - 8 + bounce))

        # Cannonball visual
        if self.cannonball_state == "jump":
            pygame.draw.circle(surf, color,
                               (body_cx, by + self.h // 2 + bounce),
                               self.w // 2 + 2)

        # Tag sprint visual
        if self.tag_active:
            for i in range(3):
                lx = bx - self.facing * (10 + i * 8)
                ly = by + self.h // 2 + bounce - 4 + i * 4
                pygame.draw.line(surf, (100, 255, 100, 120),
                                 (lx, ly), (lx - self.facing * 12, ly), 2)

    def _draw_defeat(self, surf, camera_offset):
        """Defeat animation: smile returns, bounces, cartwheels."""
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        self.defeat_timer += 1
        # Cartwheel animation
        angle = self.defeat_timer * 0.1
        bounce = abs(math.sin(self.defeat_timer * 0.08)) * 20

        cx = bx + self.w // 2
        cy = by + self.h // 2 - int(bounce)

        # Rotating body (muscular silhouette)
        rot_surf = pygame.Surface((self.w + 4, self.h + 4), pygame.SRCALPHA)
        # Torso
        torso_pts = [
            (self.w // 2 - 18 + 2, 20),
            (self.w // 2 + 18 + 2, 20),
            (self.w // 2 + 12 + 2, 74),
            (self.w // 2 - 12 + 2, 74),
        ]
        pygame.draw.polygon(rot_surf, self.color, torso_pts)
        # Head
        pygame.draw.circle(rot_surf, self.color,
                           (self.w // 2 + 2, 14), 12)
        # Eyes (defeated)
        pygame.draw.ellipse(rot_surf, (200, 220, 200),
                            (self.w // 2 - 7, 10, 6, 4))
        pygame.draw.ellipse(rot_surf, (200, 220, 200),
                            (self.w // 2 + 3, 10, 6, 4))

        rotated = pygame.transform.rotate(rot_surf, math.degrees(angle))
        rot_rect = rotated.get_rect(center=(cx, cy))
        surf.blit(rotated, rot_rect)


# ═══════════════════════════════════════════════════════════════════════
# MAMA SLOTH / LINDA — Secret Floor 4 Boss
# ═══════════════════════════════════════════════════════════════════════

class MamaSloth(Boss):
    """Secret boss. Slow but powerful. 3 phases with increasing danger.
    Heals in phase 3. The Mama Bear of the Sanitizer world."""

    def __init__(self, x, y, arena_left=100, arena_right=1180):
        super().__init__(x, y, w=125, h=150,
                         health=MAMA_SLOTH_HP,
                         boss_type=BossType.MAMA_SLOTH)
        self.boss_name = "MAMA SLOTH"
        self.max_phases = 3
        self.phase_thresholds = [0.6, 0.3]
        self.color = (160, 140, 120)
        self.arena_bounds = (arena_left, arena_right)

        # Photo portrait
        self._portrait = load_portrait('bosses/mama-sloth-reference.jpg', 80)

        # Movement
        self.speed = 1.5
        self.patrol_dir = 1

        # ── Phase 1 Attacks ──

        # Homework Time (textbook slam)
        self.homework_timer = 0
        self.homework_cooldown = 150
        self.homework_state = None  # None, "telegraph", "slam"
        self.homework_telegraph_timer = 0
        self.homework_slam_rect = None  # active damage rect
        self.homework_damage = 20
        # Slow effect: player speed * 0.5 for 180 frames

        # Clean Your Room (shockwave push)
        self.clean_timer = 0
        self.clean_cooldown = 200
        self.clean_active = False
        self.clean_damage = 10

        # Flex Zone (damage shield)
        self.flex_timer = 0
        self.flex_cooldown = 300
        self.flex_state = None  # None, "flex"
        self.flex_shield_timer = 0
        self.flex_shield_duration = 120

        # ── Phase 2 Attacks ──

        # Mom Look (line of sight freeze)
        self.mom_look_timer = 0
        self.mom_look_los_timer = 0  # how long player in LOS
        self.mom_look_freeze_threshold = 60
        # Freeze: player frozen 120 frames

        # Sanitize! (dual spray cone)
        self.sanitize_timer = 0
        self.sanitize_cooldown = 180
        self.sanitize_state = None  # None, "spray"
        self.sanitize_spray_timer = 0
        self.sanitize_spray_duration = 60
        self.sanitize_angle = math.pi / 4  # 45 degree cone
        self.sanitize_range = 200
        self.sanitize_damage = 5  # per tick

        # Slippery floor flag
        self.floor_slippery = False

        # ── Phase 3 Attacks ──

        # Snack Time (heal)
        self.snack_timer = 0
        self.snack_cooldown = 300
        self.snack_healing = False
        self.snack_heal_timer = 0
        self.snack_heal_amount = 60  # 10% of 600

        # Pending effects for combat system
        self.active_slam_rect = None  # damage rect
        self.active_shockwave = None  # (cx, cy, radius, damage)
        self.active_spray_cone = None  # (cx, cy, angle, half_arc, range, damage)
        self.player_slow_request = False  # True if homework slam hits
        self.player_freeze_request = False  # True if mom_look triggers

        # Idle animation
        self.curl_anim = 0.0

    def update(self, player):
        super().update(player)
        if self.intro_active or not self.alive:
            return

        # Clear transient effects
        self.active_slam_rect = None
        self.active_shockwave = None
        self.active_spray_cone = None
        self.player_slow_request = False
        self.player_freeze_request = False

        # Speed multiplier for phases
        if self.phase >= 3:
            speed_mult = 2.0
        elif self.phase >= 2:
            speed_mult = 1.5
        else:
            speed_mult = 1.0

        # Flex shield blocks damage
        if self.flex_state == "flex":
            self.invulnerable = True
            self.flex_shield_timer -= 1
            if self.flex_shield_timer <= 0:
                self.flex_state = None
                self.invulnerable = False
            # Idle animation: bicep curls during flex
            self.curl_anim += 0.15
            return  # immobile during flex

        # Snack Time (phase 3 heal)
        if self.phase >= 3 and self.snack_healing:
            self.snack_heal_timer -= 1
            if self.snack_heal_timer <= 0:
                self.snack_healing = False
                self.health = min(self.max_health,
                                  self.health + self.snack_heal_amount)
                self._display_health = min(float(self.max_health),
                                           self._display_health +
                                           self.snack_heal_amount)
            return  # stands still while healing

        # Movement
        self.facing = 1 if player.x > self.x else -1
        self.x += self.patrol_dir * self.speed * speed_mult
        left, right = self.arena_bounds
        if self.x <= left:
            self.patrol_dir = 1
        elif self.x + self.w >= right:
            self.patrol_dir = -1
        self._clamp_to_arena()

        # Idle animation (bicep curls)
        self.curl_anim += 0.05

        # ── Attack Updates ──

        # Homework Time (all phases)
        self.homework_timer += 1
        hw_cd = max(80, int(self.homework_cooldown / speed_mult))
        if self.homework_state is None and self.homework_timer >= hw_cd:
            self.homework_timer = 0
            self.homework_state = "telegraph"
            self.homework_telegraph_timer = 30

        if self.homework_state == "telegraph":
            self.homework_telegraph_timer -= 1
            if self.homework_telegraph_timer <= 0:
                self.homework_state = "slam"
                # Slam rect in front
                if self.facing == 1:
                    sx = self.x + self.w
                else:
                    sx = self.x - 40
                sy = self.y + self.h - 30
                self.active_slam_rect = pygame.Rect(int(sx), int(sy), 40, 30)
                self.homework_state = None
        elif self.homework_state == "slam":
            self.homework_state = None

        # Clean Your Room (all phases)
        self.clean_timer += 1
        clean_cd = max(100, int(self.clean_cooldown / speed_mult))
        if self.clean_timer >= clean_cd:
            self.clean_timer = 0
            cx = self.x + self.w / 2
            cy = self.y + self.h
            self.active_shockwave = (cx, cy, 150, self.clean_damage)

        # Flex Zone (phase 1-2, less in phase 3)
        if self.phase < 3:
            self.flex_timer += 1
            flex_cd = self.flex_cooldown
            if self.flex_timer >= flex_cd and random.random() < 0.3:
                self.flex_timer = 0
                self.flex_state = "flex"
                self.flex_shield_timer = self.flex_shield_duration

        # ── Phase 2+ Attacks ──

        if self.phase >= 2:
            # Mom Look (line of sight freeze)
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            # Check if player is roughly in front and in line of sight
            facing_match = (dx > 0 and self.facing == 1) or \
                          (dx < 0 and self.facing == -1)
            if facing_match and dist < 300 and abs(dy) < 80:
                self.mom_look_los_timer += 1
                if self.mom_look_los_timer >= self.mom_look_freeze_threshold:
                    self.player_freeze_request = True
                    self.mom_look_los_timer = 0
            else:
                self.mom_look_los_timer = max(0, self.mom_look_los_timer - 2)

            # Sanitize! spray
            self.sanitize_timer += 1
            san_cd = max(100, int(self.sanitize_cooldown / speed_mult))
            if self.sanitize_state is None and self.sanitize_timer >= san_cd:
                self.sanitize_timer = 0
                self.sanitize_state = "spray"
                self.sanitize_spray_timer = self.sanitize_spray_duration

            if self.sanitize_state == "spray":
                # Active spray cone
                angle = 0 if self.facing == 1 else math.pi
                cx = self.x + self.w / 2
                cy = self.y + self.h / 2
                self.active_spray_cone = (cx, cy, angle,
                                          self.sanitize_angle / 2,
                                          self.sanitize_range,
                                          self.sanitize_damage)
                self.sanitize_spray_timer -= 1
                if self.sanitize_spray_timer <= 0:
                    self.sanitize_state = None

            # Floor becomes slippery
            self.floor_slippery = True

        # ── Phase 3 Attacks ──

        if self.phase >= 3:
            self.snack_timer += 1
            if self.snack_timer >= self.snack_cooldown and not self.snack_healing:
                self.snack_timer = 0
                self.snack_healing = True
                self.snack_heal_timer = 60  # 1 second heal animation

    def _on_phase_change(self, old_phase, new_phase):
        """Reset timers on phase change."""
        self.homework_timer = 0
        self.clean_timer = 0
        self.flex_timer = 0
        self.sanitize_timer = 0
        self.snack_timer = 0
        self.homework_state = None
        self.flex_state = None
        self.sanitize_state = None
        self.invulnerable = False

    def draw(self, surf, camera_offset=(0, 0)):
        if not self.alive and self.boss_state != BossState.DEFEATED:
            self._draw_defeat(surf, camera_offset)
            return

        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        # Draw portrait in top-left during fight
        if self._portrait:
            surf.blit(self._portrait, (10, 10))

        color = (255, 255, 255) if self.hit_timer > 0 else self.color
        dark = (max(0, color[0] - 30), max(0, color[1] - 30),
                max(0, color[2] - 30))

        # Large sturdy body (scaled up for 85" TV)
        body_rect = (bx + 8, by + 24, self.w - 16, self.h - 36)
        pygame.draw.rect(surf, color, body_rect, border_radius=12)

        # Legs (thick)
        pygame.draw.rect(surf, dark,
                         (bx + 6, by + self.h - 16, 16, 16), border_radius=3)
        pygame.draw.rect(surf, dark,
                         (bx + self.w - 22, by + self.h - 16, 16, 16),
                         border_radius=3)

        # Head
        head_cx = bx + self.w // 2
        head_cy = by + 10
        pygame.draw.ellipse(surf, color,
                            (head_cx - 16, by, 32, 22))

        # Arms with bicep curl animation
        arm_y = by + 24
        curl = math.sin(self.curl_anim) * 0.4  # curl angle
        if self.flex_state == "flex":
            curl = math.sin(self.curl_anim) * 0.8  # bigger curls

        # Left arm
        la_end_x = bx - 6
        la_end_y = arm_y + int(math.sin(curl) * 12)
        pygame.draw.line(surf, color,
                         (bx + 6, arm_y + 6),
                         (la_end_x, la_end_y), 8)
        # Fist
        pygame.draw.circle(surf, dark, (la_end_x, la_end_y), 5)

        # Right arm
        ra_end_x = bx + self.w + 6
        ra_end_y = arm_y + int(math.sin(curl + math.pi) * 12)
        pygame.draw.line(surf, color,
                         (bx + self.w - 6, arm_y + 6),
                         (ra_end_x, ra_end_y), 8)
        pygame.draw.circle(surf, dark, (ra_end_x, ra_end_y), 5)

        # Face expression
        eye_y = by + 8
        eye_lx = head_cx - 8
        eye_rx = head_cx + 4

        if self.phase == 1:
            # Confident smile
            pygame.draw.ellipse(surf, WHITE, (eye_lx, eye_y, 6, 8))
            pygame.draw.ellipse(surf, WHITE, (eye_rx, eye_y, 6, 8))
            pygame.draw.circle(surf, (40, 30, 20),
                               (eye_lx + 3, eye_y + 4), 2)
            pygame.draw.circle(surf, (40, 30, 20),
                               (eye_rx + 3, eye_y + 4), 2)
            # Smile
            pygame.draw.arc(surf, (120, 80, 60),
                            (head_cx - 8, by + 14, 16, 8),
                            3.14, 6.28, 2)
        elif self.phase == 2:
            # Stern expression
            pygame.draw.ellipse(surf, WHITE, (eye_lx, eye_y, 6, 6))
            pygame.draw.ellipse(surf, WHITE, (eye_rx, eye_y, 6, 6))
            pygame.draw.circle(surf, (40, 30, 20),
                               (eye_lx + 3, eye_y + 3), 2)
            pygame.draw.circle(surf, (40, 30, 20),
                               (eye_rx + 3, eye_y + 3), 2)
            # Stern eyebrows
            pygame.draw.line(surf, (80, 50, 30),
                             (eye_lx - 1, eye_y - 2),
                             (eye_lx + 7, eye_y - 4), 2)
            pygame.draw.line(surf, (80, 50, 30),
                             (eye_rx + 7, eye_y - 2),
                             (eye_rx - 1, eye_y - 4), 2)
            # Flat mouth
            pygame.draw.line(surf, (120, 80, 60),
                             (head_cx - 6, by + 16),
                             (head_cx + 6, by + 16), 2)
        else:
            # Intense expression
            pygame.draw.ellipse(surf, WHITE, (eye_lx - 1, eye_y, 8, 6))
            pygame.draw.ellipse(surf, WHITE, (eye_rx - 1, eye_y, 8, 6))
            pygame.draw.circle(surf, (60, 20, 20),
                               (eye_lx + 3, eye_y + 3), 3)
            pygame.draw.circle(surf, (60, 20, 20),
                               (eye_rx + 3, eye_y + 3), 3)
            # Angry eyebrows
            pygame.draw.line(surf, (80, 30, 20),
                             (eye_lx - 2, eye_y - 1),
                             (eye_lx + 8, eye_y - 5), 3)
            pygame.draw.line(surf, (80, 30, 20),
                             (eye_rx + 8, eye_y - 1),
                             (eye_rx - 2, eye_y - 5), 3)
            # Gritted teeth
            pygame.draw.rect(surf, WHITE,
                             (head_cx - 6, by + 15, 12, 4), border_radius=1)
            pygame.draw.line(surf, (80, 50, 30),
                             (head_cx, by + 15), (head_cx, by + 19), 1)

        # Metallic outline
        pygame.draw.rect(surf, (120, 100, 80), body_rect, 2, border_radius=8)

        # Flex shield visual
        if self.flex_state == "flex":
            shield_surf = pygame.Surface((self.w + 24, self.h + 24),
                                         pygame.SRCALPHA)
            pulse = int(60 + 30 * math.sin(self.frame_count * 0.15))
            pygame.draw.ellipse(shield_surf, (200, 180, 100, pulse),
                                (0, 0, self.w + 24, self.h + 24))
            pygame.draw.ellipse(shield_surf, (255, 220, 140, pulse // 2),
                                (0, 0, self.w + 24, self.h + 24), 3)
            surf.blit(shield_surf, (bx - 12, by - 12))

        # Sanitize spray visual
        if self.sanitize_state == "spray" and self.active_spray_cone is not None:
            cx, cy, angle, half_arc, spray_range, _ = self.active_spray_cone
            scx = int(cx + ox)
            scy = int(cy + oy)
            spray_surf = pygame.Surface((spray_range * 2 + 20,
                                         spray_range * 2 + 20), pygame.SRCALPHA)
            center = (spray_range + 10, spray_range + 10)
            # Draw spray cone as a series of arcs
            for r in range(20, int(spray_range), 8):
                alpha = max(0, 80 - r // 3)
                for a_off in range(-15, 16, 3):
                    a = angle + math.radians(a_off)
                    px = center[0] + int(math.cos(a) * r)
                    py = center[1] + int(math.sin(a) * r)
                    pygame.draw.circle(spray_surf, (100, 180, 220, alpha),
                                       (px, py), 4)
            surf.blit(spray_surf, (scx - spray_range - 10,
                                   scy - spray_range - 10))

        # Snack healing visual
        if self.snack_healing:
            # Protein shake above head
            shake_y = by - 20 + int(math.sin(self.frame_count * 0.2) * 3)
            pygame.draw.rect(surf, (180, 220, 180),
                             (head_cx - 6, shake_y, 12, 16), border_radius=3)
            pygame.draw.rect(surf, (220, 240, 220),
                             (head_cx - 4, shake_y + 2, 8, 4), border_radius=2)
            # Heal sparkles
            for i in range(4):
                sx = head_cx + random.randint(-15, 15)
                sy = by + random.randint(-10, 10)
                pygame.draw.circle(surf, (100, 255, 100), (sx, sy), 2)

        # Homework telegraph
        if self.homework_state == "telegraph":
            # Textbook raising above head
            progress = 1.0 - (self.homework_telegraph_timer / 30.0)
            book_y = by - 5 - int(progress * 20)
            book_x = head_cx - 10 + self.facing * 8
            pygame.draw.rect(surf, (120, 80, 60),
                             (book_x, book_y, 20, 16), border_radius=2)
            pygame.draw.rect(surf, (200, 180, 140),
                             (book_x + 2, book_y + 2, 16, 12), border_radius=1)

        # Mom Look visual (phase 2+)
        if self.phase >= 2 and self.mom_look_los_timer > 20:
            # Glowing eyes
            glow_alpha = min(200, self.mom_look_los_timer * 3)
            for ex in [eye_lx + 3, eye_rx + 3]:
                glow = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 200, 50, glow_alpha), (8, 8), 8)
                surf.blit(glow, (ex - 8, eye_y + 3 - 8))

    def _draw_defeat(self, surf, camera_offset):
        """Defeat animation: falls asleep, zzz floats up."""
        ox, oy = camera_offset
        bx = int(self.x + ox)
        by = int(self.y + oy)

        color = self.color

        # Sitting/sleeping pose — wider, lower body
        body_rect = (bx + 4, by + 30, self.w - 8, self.h - 30)
        pygame.draw.rect(surf, color, body_rect, border_radius=10)

        # Head drooping
        head_cx = bx + self.w // 2
        pygame.draw.ellipse(surf, color,
                            (head_cx - 16, by + 24, 32, 20))

        # Closed eyes (peaceful)
        pygame.draw.line(surf, (80, 60, 40),
                         (head_cx - 8, by + 32),
                         (head_cx - 2, by + 34), 2)
        pygame.draw.line(surf, (80, 60, 40),
                         (head_cx + 2, by + 32),
                         (head_cx + 8, by + 34), 2)

        # "zzz" floating up
        try:
            font = pygame.font.Font(None, FONT_HUD)
        except Exception:
            font = pygame.font.SysFont(None, FONT_HUD)
        for i in range(3):
            t = (self.frame_count + i * 30) * 0.02
            zx = head_cx + 10 + i * 8
            zy = by + 20 - int(t * 20) % 60
            z_alpha = max(0, 255 - (int(t * 20) % 60) * 4)
            z_surf = font.render("z", True, (200, 200, 220))
            z_surf.set_alpha(z_alpha)
            surf.blit(z_surf, (zx, zy))
