"""
SPLIT -- Heads-Up Display
Health bar with jello wobble, powder count, floor number, split indicator,
pill timer, run counter, damage numbers, earthquake timer.
"""

import math
import random

import pygame

from game.engine.settings import (
    SCREEN_W,
    SCREEN_H,
    FPS,
    FONT_HUD,
    FONT_SMALL,
    FONT_DAMAGE,
    WHITE,
    BLACK,
    RED,
    HEALTH_GREEN,
    HEALTH_AMBER,
    HEALTH_RED,
    JELLO_GREEN,
    TORCH_AMBER,
    Difficulty,
)


# ---------------------------------------------------------------------------
# DamageNumber
# ---------------------------------------------------------------------------

class DamageNumber:
    """A floating damage number that drifts up and fades out."""

    __slots__ = ("x", "y", "amount", "timer", "max_timer", "is_player_damage",
                 "vx", "vy")

    def __init__(self, x, y, amount, is_player_damage=True):
        self.x = float(x)
        self.y = float(y)
        self.amount = int(amount)
        self.timer = 30
        self.max_timer = 30
        self.is_player_damage = is_player_damage
        # Slight random horizontal drift
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = -1.5  # float upward


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

class HUD:
    """Draws all in-game HUD elements."""

    def __init__(self):
        pygame.font.init()

        # Fonts
        self._font_hud = pygame.font.Font(None, FONT_HUD)
        self._font_small = pygame.font.Font(None, FONT_SMALL)
        self._font_damage = pygame.font.Font(None, FONT_DAMAGE)

        # ── Health bar geometry ──
        self._bar_x = 16
        self._bar_y = 16
        self._bar_w = 120
        self._bar_h = 10

        # Jiggle state (on-damage shake)
        self._jiggle_timer = 0
        self._jiggle_max = 15

        # ── Cached text renders ──
        self._floor_cache_num = -1
        self._floor_cache_surf = None

        self._run_cache_num = -1
        self._run_cache_surf = None

        self._split_phase = 0  # for pulsing alpha

        # ── Damage numbers ──
        self._damage_numbers: list[DamageNumber] = []

        # ── Powder diamond icon (small amber diamond, pre-rendered) ──
        self._diamond_icon = pygame.Surface((10, 10), pygame.SRCALPHA)
        pts = [(5, 0), (10, 5), (5, 10), (0, 5)]
        pygame.draw.polygon(self._diamond_icon, TORCH_AMBER, pts)

        # ── Earthquake timer ──
        self._eq_timer_frames = 0

    # -- public helpers ------------------------------------------------------

    def trigger_jiggle(self):
        """Call when the player takes damage to jiggle the health bar."""
        self._jiggle_timer = self._jiggle_max

    def add_damage_number(self, x, y, amount, is_player_damage=True):
        """Queue a floating damage number at world position (x, y)."""
        self._damage_numbers.append(
            DamageNumber(x, y, amount, is_player_damage)
        )

    def set_earthquake_timer(self, frames_remaining):
        """Set the earthquake countdown (in frames)."""
        self._eq_timer_frames = max(0, int(frames_remaining))

    # -- internal rendering --------------------------------------------------

    def _health_color(self, ratio):
        """Return bar color based on health ratio."""
        if ratio > 0.6:
            return HEALTH_GREEN
        elif ratio > 0.3:
            return HEALTH_AMBER
        return HEALTH_RED

    def _draw_health_bar(self, surf, health, max_health, frame_count):
        """Jello health bar with sine wobble and damage jiggle."""
        ratio = max(0.0, min(1.0, health / max(max_health, 1)))
        color = self._health_color(ratio)

        bx = self._bar_x
        by = self._bar_y

        # Jiggle offset on damage
        jiggle_ox = 0
        jiggle_oy = 0
        if self._jiggle_timer > 0:
            intensity = self._jiggle_timer / self._jiggle_max
            jiggle_ox = int(random.uniform(-3, 3) * intensity)
            jiggle_oy = int(random.uniform(-2, 2) * intensity)
            self._jiggle_timer -= 1

        bx += jiggle_ox
        by += jiggle_oy

        # Background (dark)
        bg_rect = pygame.Rect(bx - 1, by - 1, self._bar_w + 2, self._bar_h + 2)
        pygame.draw.rect(surf, (30, 30, 30), bg_rect)

        # Filled portion with sine wobble on trailing edge
        fill_w = int(self._bar_w * ratio)
        if fill_w > 0:
            bar_surf = pygame.Surface((fill_w, self._bar_h), pygame.SRCALPHA)
            bar_surf.fill(color)

            # Sine wobble on the right edge (jelly feel)
            wobble_amp = 2
            for row in range(self._bar_h):
                offset = math.sin(frame_count * 0.1 + row * 0.5) * wobble_amp
                # Shift the rightmost pixels with a tiny wobble
                edge_x = fill_w - 1 + int(offset)
                edge_x = max(0, min(fill_w - 1, edge_x))
                bar_surf.set_at((edge_x, row), (*color, 200))

            surf.blit(bar_surf, (bx, by))

        # Border
        border_rect = pygame.Rect(bx - 1, by - 1, self._bar_w + 2, self._bar_h + 2)
        pygame.draw.rect(surf, WHITE, border_rect, 1)

        # HP text
        hp_text = self._font_hud.render(
            f"HP: {int(health)}/{int(max_health)}", True, WHITE
        )
        surf.blit(hp_text, (bx + self._bar_w + 8, by - 2))

    def _draw_powder_count(self, surf, count):
        """Small diamond icon + powder count below health bar."""
        x = self._bar_x
        y = self._bar_y + self._bar_h + 8
        surf.blit(self._diamond_icon, (x, y))
        txt = self._font_hud.render(f" {count}", True, TORCH_AMBER)
        surf.blit(txt, (x + 12, y - 1))

    def _draw_floor_number(self, surf, floor_num):
        """Floor number centered at top of screen. Cached."""
        if floor_num != self._floor_cache_num or self._floor_cache_surf is None:
            self._floor_cache_num = floor_num
            self._floor_cache_surf = self._font_small.render(
                f"Floor {floor_num}", True, WHITE
            )
        fw = self._floor_cache_surf.get_width()
        surf.blit(self._floor_cache_surf, (SCREEN_W // 2 - fw // 2, 12))

    def _draw_split_indicator(self, surf, frame_count):
        """Pulsing green 'SPLIT!' text at center-top."""
        self._split_phase += 0.08
        alpha = int(155 + 100 * math.sin(self._split_phase))
        alpha = max(50, min(255, alpha))

        text_surf = self._font_small.render("SPLIT!", True, JELLO_GREEN)
        faded = text_surf.copy()
        faded.set_alpha(alpha)
        tw = faded.get_width()
        surf.blit(faded, (SCREEN_W // 2 - tw // 2, 36))

    def _draw_pill_timer(self, surf, pill_name, frames_left, max_frames):
        """Active pill name + countdown bar below floor text."""
        cx = SCREEN_W // 2
        y = 56

        # Pill name
        label = self._font_hud.render(pill_name.upper(), True, WHITE)
        lw = label.get_width()
        surf.blit(label, (cx - lw // 2, y))

        # Timer bar
        bar_w = 80
        bar_h = 6
        bx = cx - bar_w // 2
        by = y + 18
        ratio = max(0.0, min(1.0, frames_left / max(max_frames, 1)))

        pygame.draw.rect(surf, (40, 40, 40), (bx, by, bar_w, bar_h))
        fill = int(bar_w * ratio)
        if fill > 0:
            pygame.draw.rect(surf, TORCH_AMBER, (bx, by, fill, bar_h))
        pygame.draw.rect(surf, WHITE, (bx, by, bar_w, bar_h), 1)

    def _draw_run_counter(self, surf, run_count):
        """Small 'Run #N' text at bottom-right. Cached."""
        if run_count != self._run_cache_num or self._run_cache_surf is None:
            self._run_cache_num = run_count
            self._run_cache_surf = self._font_hud.render(
                f"Run #{run_count}", True, WHITE
            )
        rw = self._run_cache_surf.get_width()
        rh = self._run_cache_surf.get_height()
        surf.blit(self._run_cache_surf, (SCREEN_W - rw - 16, SCREEN_H - rh - 12))

    def _draw_damage_numbers(self, surf, camera_offset):
        """Update and draw floating damage numbers (world-space)."""
        ox, oy = camera_offset
        still_alive = []
        for dn in self._damage_numbers:
            dn.timer -= 1
            if dn.timer <= 0:
                continue
            dn.x += dn.vx
            dn.y += dn.vy

            # Screen position
            sx = int(dn.x + ox)
            sy = int(dn.y + oy)

            # Alpha fade
            t = dn.timer / dn.max_timer
            alpha = int(255 * t)

            color = RED if dn.is_player_damage else WHITE
            text_surf = self._font_damage.render(str(dn.amount), True, color)
            if alpha < 255:
                text_surf.set_alpha(alpha)
            surf.blit(text_surf, (sx - text_surf.get_width() // 2, sy))

            still_alive.append(dn)
        self._damage_numbers = still_alive

    def _draw_earthquake_timer(self, surf):
        """Red countdown timer at top-right (Earthquake Mode only)."""
        secs = self._eq_timer_frames / FPS
        minutes = int(secs) // 60
        seconds = int(secs) % 60
        time_str = f"{minutes}:{seconds:02d}"
        txt = self._font_small.render(time_str, True, RED)
        tw = txt.get_width()
        surf.blit(txt, (SCREEN_W - tw - 16, 12))

    # -- main draw -----------------------------------------------------------

    def draw(self, surf, player, current_floor, run_count,
             difficulty=None, camera_offset=(0, 0), frame_count=0):
        """Draw all HUD elements.

        Parameters
        ----------
        surf : pygame.Surface
            The screen surface.
        player : object
            Must have .health, .max_health, .jello_powder_count attributes.
            Optionally .is_split (bool), .active_pill (dict or None with
            'name', 'frames_left', 'max_frames').
        current_floor : int
            Current floor number (1-15).
        run_count : int
            Current run number.
        difficulty : Difficulty or None
            Current difficulty setting.
        camera_offset : tuple
            (ox, oy) for world-space elements.
        frame_count : int
            Global frame counter for animations.
        """
        # Health bar
        health = getattr(player, "health", 0)
        max_health = getattr(player, "max_health", 100)
        self._draw_health_bar(surf, health, max_health, frame_count)

        # Powder count
        powder = getattr(player, "jello_powder_count", 0)
        self._draw_powder_count(surf, powder)

        # Floor number
        self._draw_floor_number(surf, current_floor)

        # Split indicator
        is_split = getattr(player, "is_split", False)
        if is_split:
            self._draw_split_indicator(surf, frame_count)
        else:
            self._split_phase = 0

        # Pill timer
        active_pill = getattr(player, "active_pill", None)
        if active_pill is not None:
            pill_name = active_pill.get("name", "Pill")
            frames_left = active_pill.get("frames_left", 0)
            max_frames = active_pill.get("max_frames", 1)
            if frames_left > 0:
                self._draw_pill_timer(surf, pill_name, frames_left, max_frames)

        # Run counter
        self._draw_run_counter(surf, run_count)

        # Damage numbers (world-space)
        self._draw_damage_numbers(surf, camera_offset)

        # Earthquake timer (only in Earthquake Mode)
        if difficulty == Difficulty.EARTHQUAKE and self._eq_timer_frames > 0:
            self._draw_earthquake_timer(surf)
