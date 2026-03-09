"""
SPLIT — Awareness / Stealth System
Manages per-enemy awareness states (IDLE → SUSPICIOUS → ALERT → HUNTING → LOST),
vision cones, line-of-sight checks, sound detection, and indicator drawing.
"""
import pygame
import math
import enum
from game.engine.settings import (
    EnemyType, GameEvent,
    WHITE, RED,
    FONT_DAMAGE,
)
from game.entities.enemies import EnemyState


# ── Awareness States ──

class AwarenessState(enum.Enum):
    IDLE = "idle"
    SUSPICIOUS = "suspicious"
    ALERT = "alert"
    HUNTING = "hunting"
    LOST = "lost"


# ── Timing constants (frames at 60 fps) ──
SUSPICIOUS_DURATION = 90       # frames before SUSPICIOUS → ALERT
HUNTING_DURATION = 300         # frames before HUNTING → LOST
LOST_RETURN_DURATION = 60      # frames in LOST before resetting to IDLE

# ── Detection ranges ──
VISION_RANGE = 200             # pixels
VISION_HALF_ANGLE = math.pi / 4  # 45° each side = 90° total cone
SOUND_DETECTION_RANGE = 300    # ground pound alert radius

# ── Indicator animation ──
INDICATOR_FADE_FRAMES = 15     # frames for ? or ! to fade in


class _EnemyAwareness:
    """Internal per-enemy awareness tracking data."""

    def __init__(self):
        self.state = AwarenessState.IDLE
        self.timer = 0          # general state timer
        self.alert_timer = 0    # how long in ALERT (for draw pulsing)
        self.indicator_fade = 0  # 0..INDICATOR_FADE_FRAMES for fade-in


class AwarenessSystem:
    """Manages stealth / awareness for all enemies in the current room."""

    def __init__(self):
        # Map from enemy id() → _EnemyAwareness
        self._data = {}

    def _get(self, enemy):
        """Get or create awareness data for an enemy."""
        eid = id(enemy)
        if eid not in self._data:
            self._data[eid] = _EnemyAwareness()
        return self._data[eid]

    def get_awareness_state(self, enemy):
        """Public accessor — returns AwarenessState for the given enemy."""
        return self._get(enemy).state

    def update(self, player, enemies, platforms=None):
        """Per-frame update of awareness for every enemy.

        Args:
            player:    JelloCube instance.
            enemies:   List of Enemy instances (alive or dead).
            platforms: List of platform rects (for line-of-sight blocking).
                       Each entry should be a pygame.Rect or have get_rect().
        """
        if platforms is None:
            platforms = []

        # Check if player just ground-pounded (sound event)
        player_pounded = getattr(player, 'just_landed_pound', False)
        player_dodging = getattr(player, 'dodge_invulnerable', False)

        player_cx = player.x + player.w / 2
        player_cy = player.y + player.h / 2

        for enemy in enemies:
            if not enemy.alive:
                continue

            aw = self._get(enemy)

            # ── Sound detection: ground pound alerts within range ──
            if player_pounded:
                ecx = enemy.x + enemy.w / 2
                ecy = enemy.y + enemy.h / 2
                dist = math.hypot(ecx - player_cx, ecy - player_cy)
                if dist <= SOUND_DETECTION_RANGE:
                    aw.state = AwarenessState.ALERT
                    aw.timer = 0
                    aw.indicator_fade = 0

            # ── Perfect dodge near SmallSanitizerBottle → reset to IDLE ──
            if player_dodging and enemy.enemy_type == EnemyType.SANITIZER_BOTTLE:
                ecx = enemy.x + enemy.w / 2
                ecy = enemy.y + enemy.h / 2
                dist = math.hypot(ecx - player_cx, ecy - player_cy)
                if dist <= 80:
                    aw.state = AwarenessState.IDLE
                    aw.timer = 0
                    aw.indicator_fade = 0
                    enemy.state = EnemyState.PATROL
                    continue

            # ── Vision check ──
            can_see = self._check_vision(enemy, player, platforms)

            # ── State machine ──
            if aw.state == AwarenessState.IDLE:
                aw.indicator_fade = 0
                if can_see:
                    aw.state = AwarenessState.SUSPICIOUS
                    aw.timer = 0
                    aw.indicator_fade = 0

            elif aw.state == AwarenessState.SUSPICIOUS:
                aw.timer += 1
                aw.indicator_fade = min(INDICATOR_FADE_FRAMES,
                                        aw.indicator_fade + 1)
                if not can_see:
                    # Lost sight — back to idle
                    aw.state = AwarenessState.IDLE
                    aw.timer = 0
                elif aw.timer >= SUSPICIOUS_DURATION:
                    aw.state = AwarenessState.ALERT
                    aw.timer = 0
                    aw.indicator_fade = 0

            elif aw.state == AwarenessState.ALERT:
                aw.alert_timer += 1
                aw.indicator_fade = min(INDICATOR_FADE_FRAMES,
                                        aw.indicator_fade + 1)
                # Transition enemy behavior to CHASE
                if enemy.state == EnemyState.PATROL:
                    enemy.state = EnemyState.CHASE
                # After a beat, enter hunting mode
                aw.timer += 1
                if aw.timer >= 30:
                    aw.state = AwarenessState.HUNTING
                    aw.timer = 0

            elif aw.state == AwarenessState.HUNTING:
                aw.timer += 1
                aw.indicator_fade = INDICATOR_FADE_FRAMES  # stay visible
                # Keep chasing
                if enemy.state == EnemyState.PATROL:
                    enemy.state = EnemyState.CHASE
                if can_see:
                    # Reset hunting timer — still tracking
                    aw.timer = 0
                elif aw.timer >= HUNTING_DURATION:
                    aw.state = AwarenessState.LOST
                    aw.timer = 0

            elif aw.state == AwarenessState.LOST:
                aw.timer += 1
                aw.indicator_fade = max(0, aw.indicator_fade - 1)
                # Return to patrol
                if enemy.state != EnemyState.PATROL:
                    enemy.state = EnemyState.PATROL
                if aw.timer >= LOST_RETURN_DURATION:
                    aw.state = AwarenessState.IDLE
                    aw.timer = 0
                    aw.alert_timer = 0

    def _check_vision(self, enemy, player, platforms):
        """Return True if the enemy can see the player (within cone + LOS)."""
        ecx = enemy.x + enemy.w / 2
        ecy = enemy.y + enemy.h / 2
        pcx = player.x + player.w / 2
        pcy = player.y + player.h / 2

        dx = pcx - ecx
        dy = pcy - ecy
        dist = math.hypot(dx, dy)

        # Out of range
        if dist > VISION_RANGE:
            return False

        # Angle check — facing direction
        facing_angle = 0.0 if enemy.facing == 1 else math.pi
        angle_to_player = math.atan2(dy, dx)
        angle_diff = abs(self._angle_diff(facing_angle, angle_to_player))

        if angle_diff > VISION_HALF_ANGLE:
            return False

        # Line of sight — check if any platform blocks the view
        if self._los_blocked(ecx, ecy, pcx, pcy, platforms):
            return False

        return True

    @staticmethod
    def _angle_diff(a, b):
        """Shortest signed angle difference, normalized to [-pi, pi]."""
        diff = b - a
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        return diff

    @staticmethod
    def _los_blocked(x1, y1, x2, y2, platforms):
        """Simple line-of-sight raycast: returns True if any platform rect
        intersects the line segment from (x1,y1) to (x2,y2).
        Uses a sampling approach (check points along the line).
        """
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist < 1:
            return False

        steps = max(1, int(dist / 16))  # sample every ~16 px
        for i in range(1, steps):
            t = i / steps
            sx = x1 + dx * t
            sy = y1 + dy * t
            point = pygame.Rect(int(sx) - 1, int(sy) - 1, 2, 2)
            for plat in platforms:
                pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(*plat)
                if pr.colliderect(point):
                    return True
        return False

    # ── Drawing ──

    def draw_indicators(self, surf, enemies, camera_offset=(0, 0)):
        """Draw ? and ! awareness indicators above enemies."""
        ox, oy = camera_offset

        for enemy in enemies:
            if not enemy.alive:
                continue
            aw = self._get(enemy)

            if aw.state == AwarenessState.IDLE:
                continue  # no indicator
            if aw.state == AwarenessState.LOST and aw.indicator_fade <= 0:
                continue

            # Position above enemy head
            ind_x = int(enemy.x + enemy.w / 2 + ox)
            ind_y = int(enemy.y + oy) - 14

            # Fade-in alpha
            fade = aw.indicator_fade / max(1, INDICATOR_FADE_FRAMES)
            alpha = int(255 * fade)

            if aw.state == AwarenessState.SUSPICIOUS:
                self._draw_question_mark(surf, ind_x, ind_y, alpha)

            elif aw.state in (AwarenessState.ALERT, AwarenessState.HUNTING):
                self._draw_exclamation(surf, ind_x, ind_y, alpha)
                # Red tint overlay on the enemy body
                self._draw_alert_tint(surf, enemy, ox, oy, alpha)

    @staticmethod
    def _draw_question_mark(surf, cx, cy, alpha):
        """Draw a yellow '?' indicator."""
        alpha = max(0, min(255, alpha))
        # Background circle
        bg = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(bg, (40, 40, 40, alpha // 2), (9, 9), 9)
        surf.blit(bg, (cx - 9, cy - 9))
        # '?' character
        try:
            font = pygame.font.Font(None, 20)
        except Exception:
            font = pygame.font.SysFont(None, 20)
        text = font.render("?", True, (255, 220, 60))
        text.set_alpha(alpha)
        tr = text.get_rect(center=(cx, cy))
        surf.blit(text, tr)

    @staticmethod
    def _draw_exclamation(surf, cx, cy, alpha):
        """Draw a red '!' indicator."""
        alpha = max(0, min(255, alpha))
        bg = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(bg, (80, 20, 20, alpha // 2), (9, 9), 9)
        surf.blit(bg, (cx - 9, cy - 9))
        try:
            font = pygame.font.Font(None, 22)
        except Exception:
            font = pygame.font.SysFont(None, 22)
        text = font.render("!", True, (255, 60, 60))
        text.set_alpha(alpha)
        tr = text.get_rect(center=(cx, cy))
        surf.blit(text, tr)

    @staticmethod
    def _draw_alert_tint(surf, enemy, ox, oy, alpha):
        """Draw a subtle red tint overlay on an alerted enemy."""
        tint_alpha = max(0, min(60, alpha // 4))
        tint = pygame.Surface((enemy.w, enemy.h), pygame.SRCALPHA)
        tint.fill((220, 40, 40, tint_alpha))
        surf.blit(tint, (int(enemy.x + ox), int(enemy.y + oy)))
