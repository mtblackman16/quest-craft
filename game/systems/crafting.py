"""
SPLIT — Crafting System & Banana Slug
Pill inventory, cooking pot interaction, active pill effects,
and the helpful Banana Slug hint companion.
"""

import math
import pygame
from game.engine.settings import (
    PillType, PILL_DURATIONS,
    SLUG_APPEAR_DELAY, SLUG_SPEED,
    JELLO_POWDER_HEAL,
)


# ── CraftingSystem ──

class CraftingSystem:
    """Manages pill inventory, active pill effects, and cooking-pot interaction."""

    def __init__(self):
        self.pill_inventory: dict[PillType, int] = {}
        self.active_pill: PillType | None = None
        self.pill_timer: int = 0
        self.has_water: bool = False

    # ── Pot interaction ──

    def interact_with_pot(self, player) -> str:
        """
        State-machine for the cooking pot.

        Returns a status string the caller can use for UI/sound:
            "need_water"   — player has no water yet
            "need_powder"  — water deposited but no powder to cook
            "cooking"      — cooked a pill from powder + water
            "healed"       — healed from jello powder at the pot
            "nothing"      — nothing useful happened
        """
        # Sync water flag from the player object
        self.has_water = getattr(player, "has_water", self.has_water)

        if not self.has_water:
            return "need_water"

        # Player has water — check for powder to cook
        has_powder = getattr(player, "has_powder", False)
        powder_type = getattr(player, "powder_type", None)

        if has_powder and powder_type is not None:
            # Cook the powder into a pill
            pill = self._powder_to_pill(powder_type)
            if pill is not None:
                self.add_pill(pill)
                player.has_powder = False
                player.powder_type = None
                self.has_water = False
                if hasattr(player, "has_water"):
                    player.has_water = False
                return "cooking"

        # Check if player can heal with plain jello powder
        has_jello = getattr(player, "has_jello_powder", False)
        if has_jello:
            hp = getattr(player, "health", 0)
            max_hp = getattr(player, "max_health", 100)
            if hp < max_hp:
                player.health = min(hp + JELLO_POWDER_HEAL, max_hp)
                player.has_jello_powder = False
                self.has_water = False
                if hasattr(player, "has_water"):
                    player.has_water = False
                return "healed"

        return "need_powder"

    # ── Pill management ──

    def add_pill(self, pill_type: PillType):
        """Add a pill to the inventory."""
        self.pill_inventory[pill_type] = self.pill_inventory.get(pill_type, 0) + 1

    def use_pill(self, pill_type: PillType) -> bool:
        """
        Activate a pill from inventory.
        Returns True if successful, False if not available.
        """
        count = self.pill_inventory.get(pill_type, 0)
        if count <= 0:
            return False

        # Consume from inventory
        self.pill_inventory[pill_type] = count - 1
        if self.pill_inventory[pill_type] <= 0:
            del self.pill_inventory[pill_type]

        # Activate effect
        self.active_pill = pill_type
        duration_key = pill_type.value  # e.g. "fire", "water"
        self.pill_timer = PILL_DURATIONS.get(duration_key, 60 * 60)
        return True

    def get_pill_effect(self) -> PillType | None:
        """Return the active PillType, or None. For combat/movement queries."""
        return self.active_pill

    def update(self):
        """Tick per frame. Counts down active pill timer."""
        if self.active_pill is not None:
            self.pill_timer -= 1
            if self.pill_timer <= 0:
                self.active_pill = None
                self.pill_timer = 0

    # ── Internal ──

    @staticmethod
    def _powder_to_pill(powder_type) -> PillType | None:
        """Convert a powder-type identifier to the matching PillType enum."""
        if isinstance(powder_type, PillType):
            return powder_type
        # Try matching by string value
        try:
            return PillType(str(powder_type).lower())
        except (ValueError, KeyError):
            return None


# ── BananaSlug ──

# Drawing constants
_SLUG_W = 16
_SLUG_H = 8
_SLUG_BODY_COLOR = (180, 150, 60)
_SLUG_ANTENNA_COLOR = (140, 115, 45)
_SLUG_FADE_FRAMES = 30
_SLUG_WIGGLE_RANGE = 3  # pixels of wiggle displacement
_SLUG_POUND_RANGE = 60  # proximity for ground-pound reaction


class BananaSlug:
    """
    A tiny helpful companion that appears when the player is stuck.
    Crawls toward the next objective. Disappears when the player
    starts making progress. Wiggles when ground-pounded nearby.
    """

    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.target_x: float = 0.0
        self.target_y: float = 0.0
        self.visible: bool = False
        self.speed: float = SLUG_SPEED
        self.wiggle_timer: int = 0
        self.crawl_phase: float = 0.0

        # Fade tracking
        self._fade_alpha: int = 0       # 0-255
        self._fading_in: bool = False
        self._fading_out: bool = False

        # Previous distance to player (to detect player moving toward slug)
        self._prev_player_dist: float = 0.0

    # ── Update ──

    def update(self, player, nearest_objective_x: float,
               nearest_objective_y: float, no_progress_timer: int):
        """
        Call once per frame.

        Args:
            player:               the player object (needs .x, .y)
            nearest_objective_x:  world x of the next goal
            nearest_objective_y:  world y of the next goal
            no_progress_timer:    frames since player last made progress
        """
        self.target_x = nearest_objective_x
        self.target_y = nearest_objective_y

        px = getattr(player, "x", 0.0)
        py = getattr(player, "y", 0.0)

        # Should we spawn?
        if not self.visible and not self._fading_out:
            if no_progress_timer > SLUG_APPEAR_DELAY:
                self._spawn_near_player(px, py)

        # Movement while visible
        if self.visible or self._fading_in or self._fading_out:
            # Crawl toward objective
            if self.visible:
                dx = self.target_x - self.x
                dy = self.target_y - self.y
                dist = math.hypot(dx, dy)
                if dist > 1.0:
                    self.x += (dx / dist) * self.speed
                    self.y += (dy / dist) * self.speed

            # Crawl animation
            self.crawl_phase = (self.crawl_phase + 0.15) % (2 * math.pi)

            # Wiggle countdown
            if self.wiggle_timer > 0:
                self.wiggle_timer -= 1

            # Check if player is moving toward us → hide
            player_dist = math.hypot(px - self.x, py - self.y)
            if (self._prev_player_dist > 0 and
                    player_dist < self._prev_player_dist - 0.5 and
                    not self._fading_out):
                self._begin_fade_out()
            self._prev_player_dist = player_dist

            # Process fade in/out
            self._tick_fade()

    # ── Ground pound reaction ──

    def on_ground_pound(self, pound_x: float, pound_y: float):
        """If a ground-pound lands near the slug, do a charming wiggle."""
        if not self.visible:
            return
        dist = math.hypot(pound_x - self.x, pound_y - self.y)
        if dist <= _SLUG_POUND_RANGE:
            self.wiggle_timer = 30

    # ── Drawing ──

    def draw(self, surf: pygame.Surface, camera_offset: tuple[float, float]):
        """Render the slug with crawl + wiggle animation."""
        if self._fade_alpha <= 0 and not self.visible:
            return

        alpha = self._fade_alpha
        if alpha <= 0:
            return

        cx = self.x - camera_offset[0]
        cy = self.y - camera_offset[1]

        # Wiggle displacement
        wiggle_dx = 0.0
        if self.wiggle_timer > 0:
            wiggle_dx = math.sin(self.wiggle_timer * 1.2) * _SLUG_WIGGLE_RANGE

        # Crawl animation: body squish / stretch
        stretch = 1.0 + 0.15 * math.sin(self.crawl_phase)
        squish = 1.0 - 0.10 * math.sin(self.crawl_phase)

        draw_w = int(_SLUG_W * stretch)
        draw_h = int(_SLUG_H * squish)

        # Build a small surface for the slug
        slug_surf = pygame.Surface((draw_w + 6, draw_h + 6), pygame.SRCALPHA)

        # Body: warm brown oval
        body_rect = pygame.Rect(3, 3 + (draw_h - _SLUG_H), draw_w, draw_h)
        pygame.draw.ellipse(slug_surf, (*_SLUG_BODY_COLOR, alpha), body_rect)

        # Two tiny antennae lines from the front of the body
        ant_base_x = body_rect.right - 2
        ant_base_y = body_rect.top + 1
        ant_color = (*_SLUG_ANTENNA_COLOR, alpha)
        # Right antenna (slightly up-right)
        pygame.draw.line(slug_surf, ant_color,
                         (ant_base_x, ant_base_y),
                         (ant_base_x + 3, ant_base_y - 4), 1)
        # Left antenna (slightly up-left-ish)
        pygame.draw.line(slug_surf, ant_color,
                         (ant_base_x, ant_base_y + 1),
                         (ant_base_x + 3, ant_base_y - 1), 1)

        # Blit onto the main surface
        blit_x = cx + wiggle_dx - draw_w // 2
        blit_y = cy - draw_h // 2
        surf.blit(slug_surf, (blit_x, blit_y))

    # ── Internal ──

    def _spawn_near_player(self, px: float, py: float):
        """Place the slug just off-screen to the right of the player."""
        self.x = px + 320  # one quarter-screen to the right
        self.y = py
        self.visible = True
        self._fading_in = True
        self._fading_out = False
        self._fade_alpha = 0
        self._prev_player_dist = 0.0

    def _begin_fade_out(self):
        """Start the fade-out sequence."""
        self._fading_out = True
        self._fading_in = False

    def _tick_fade(self):
        """Advance fade-in or fade-out by one frame."""
        if self._fading_in:
            self._fade_alpha = min(255, self._fade_alpha + (255 // _SLUG_FADE_FRAMES))
            if self._fade_alpha >= 255:
                self._fade_alpha = 255
                self._fading_in = False
        elif self._fading_out:
            self._fade_alpha = max(0, self._fade_alpha - (255 // _SLUG_FADE_FRAMES))
            if self._fade_alpha <= 0:
                self._fade_alpha = 0
                self._fading_out = False
                self.visible = False
