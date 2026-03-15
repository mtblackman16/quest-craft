"""
SPLIT — Interactable Objects
Everything the player can interact with by pressing Y:
cooking pots, water sources, chests, doors, shrines, and sun zones.
"""
import math
import random
import pygame
from game.engine.settings import (
    SCREEN_W, SCREEN_H, JELLO_GREEN, JELLO_GREEN_DIM,
    TORCH_AMBER, TORCH_GLOW, WHITE, BLACK,
    JELLO_POWDER_HEAL,
)

__all__ = [
    "Interactable", "CookingPot", "WaterSource",
    "Chest", "Door", "Shrine", "SunZone",
]

# ── Cooking pot states ──
POT_EMPTY = 0
POT_NEEDS_WATER = 1
POT_NEEDS_POWDER = 2
POT_COOKING = 3
POT_DONE = 4

# ── Chest states ──
CHEST_CLOSED = 0
CHEST_OPENING = 1
CHEST_OPEN = 2


# ──────────────────────────────────────────────
#  Base Interactable
# ──────────────────────────────────────────────
class Interactable:
    """Base for every interactable object in a room."""

    def __init__(self, x, y, w, h, interactable_type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.interactable_type = interactable_type
        self._tick = 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt=1):
        self._tick += 1

    def draw(self, surf, camera_offset):
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy
        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return
        rect = pygame.Rect(int(sx), int(sy), self.w, self.h)
        pygame.draw.rect(surf, (180, 180, 60), rect, 1)

    def interact(self, player, crafting_system=None):
        """Override in subclasses. Returns True if something happened."""
        return False


# ──────────────────────────────────────────────
#  Cooking Pot
# ──────────────────────────────────────────────
class CookingPot(Interactable):
    """
    Y to interact.  Flow:
      EMPTY -> player adds water -> NEEDS_POWDER
      NEEDS_POWDER -> player adds jello powder -> COOKING
      COOKING (60 frames) -> DONE -> heals player -> resets to EMPTY
    """

    def __init__(self, x, y):
        super().__init__(x, y, 40, 32, "cooking_pot")
        self.state = POT_EMPTY
        self.cook_timer = 0
        self._bubble_offsets = []

    def interact(self, player, crafting_system=None):
        if self.state == POT_EMPTY:
            # Check if player has water
            if getattr(player, "has_water", False):
                player.has_water = False
                self.state = POT_NEEDS_POWDER
                return True
            # Prompt: needs water first
            return False

        elif self.state == POT_NEEDS_POWDER:
            powder = getattr(player, "jello_powder_count", 0)
            if powder > 0:
                player.jello_powder_count = powder - 1
                self.state = POT_COOKING
                self.cook_timer = 60
                return True
            return False

        elif self.state == POT_DONE:
            # Give the player cooked jelly (heals when eaten via X button)
            cooked = getattr(player, "cooked_jelly_count", 0)
            player.cooked_jelly_count = cooked + 1
            self.state = POT_EMPTY
            return True

        return False

    def update(self, dt=1):
        super().update(dt)
        if self.state == POT_COOKING:
            self.cook_timer -= 1
            # Generate bubble offsets for animation
            if self._tick % 6 == 0:
                self._bubble_offsets.append(
                    (random.randint(6, self.w - 6), 0)
                )
            # Rise and expire bubbles
            new_bubbles = []
            for bx, by in self._bubble_offsets:
                by -= 1
                if by > -12:
                    new_bubbles.append((bx, by))
            self._bubble_offsets = new_bubbles

            if self.cook_timer <= 0:
                self.state = POT_DONE
                self._bubble_offsets.clear()

    def draw(self, surf, camera_offset):
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy
        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        # Pot body — dark grey rounded rect
        pot_color = (60, 58, 62)
        pot_rect = pygame.Rect(int(sx) + 4, int(sy) + 8, self.w - 8, self.h - 8)
        pygame.draw.rect(surf, pot_color, pot_rect, border_radius=4)

        # Rim
        rim_rect = pygame.Rect(int(sx) + 2, int(sy) + 6, self.w - 4, 4)
        pygame.draw.rect(surf, (90, 88, 92), rim_rect)

        # Legs
        pygame.draw.rect(surf, pot_color,
                         pygame.Rect(int(sx) + 6, int(sy) + self.h - 4, 4, 4))
        pygame.draw.rect(surf, pot_color,
                         pygame.Rect(int(sx) + self.w - 10, int(sy) + self.h - 4, 4, 4))

        # State-based contents
        if self.state == POT_NEEDS_POWDER:
            # Blue water inside
            water = pygame.Rect(int(sx) + 6, int(sy) + 14, self.w - 12, 8)
            pygame.draw.rect(surf, (80, 140, 200), water)

        elif self.state == POT_COOKING:
            # Green bubbling liquid
            liquid = pygame.Rect(int(sx) + 6, int(sy) + 12, self.w - 12, 10)
            pygame.draw.rect(surf, JELLO_GREEN_DIM, liquid)
            # Bubbles
            for bx, by in self._bubble_offsets:
                bsx = int(sx) + bx
                bsy = int(sy) + 12 + by
                pygame.draw.circle(surf, JELLO_GREEN, (bsx, bsy), 2)

        elif self.state == POT_DONE:
            # Glowing green — ready to eat
            liquid = pygame.Rect(int(sx) + 6, int(sy) + 12, self.w - 12, 10)
            pygame.draw.rect(surf, JELLO_GREEN, liquid)
            # Pulsing glow
            pulse = int(abs(math.sin(self._tick * 0.08)) * 30)
            glow_surf = pygame.Surface((self.w, 6), pygame.SRCALPHA)
            glow_surf.fill((125, 223, 100, 40 + pulse))
            surf.blit(glow_surf, (int(sx), int(sy) + 10))


# ──────────────────────────────────────────────
#  Water Source
# ──────────────────────────────────────────────
class WaterSource(Interactable):
    """Y to absorb water. Draws dripping blue drops."""

    def __init__(self, x, y):
        super().__init__(x, y, 24, 48, "water_source")
        self._drops = []  # list of (dx, dy, speed)

    def interact(self, player, crafting_system=None):
        player.has_water = True
        return True

    def update(self, dt=1):
        super().update(dt)
        # Spawn a drip every ~20 frames
        if self._tick % 20 == 0:
            self._drops.append((
                random.randint(2, self.w - 2),
                0,
                random.uniform(1.0, 2.0),
            ))
        # Move drops
        new_drops = []
        for dx, dy, spd in self._drops:
            dy += spd
            if dy < self.h + 8:
                new_drops.append((dx, dy, spd))
        self._drops = new_drops

    def draw(self, surf, camera_offset):
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy
        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        # Pipe / source — small grey block at the top
        pipe_rect = pygame.Rect(int(sx) + 4, int(sy), self.w - 8, 8)
        pygame.draw.rect(surf, (70, 75, 80), pipe_rect)

        # Water drops
        blue = (80, 160, 230)
        for dx, dy, _ in self._drops:
            drop_x = int(sx) + dx
            drop_y = int(sy) + int(dy)
            pygame.draw.circle(surf, blue, (drop_x, drop_y), 2)

        # Small puddle at bottom
        puddle = pygame.Rect(int(sx) - 2, int(sy) + self.h - 4,
                             self.w + 4, 4)
        puddle_surf = pygame.Surface((self.w + 4, 4), pygame.SRCALPHA)
        puddle_surf.fill((80, 160, 230, 90))
        surf.blit(puddle_surf, (int(sx) - 2, int(sy) + self.h - 4))


# ──────────────────────────────────────────────
#  Chest
# ──────────────────────────────────────────────
class Chest(Interactable):
    """Y to open. Drops jello powder (and sometimes other items) for the player."""

    # Possible rare drops on later floors (floor >= 8)
    RARE_DROPS = ['water', 'pill_fire', 'pill_water', 'pill_ice']

    def __init__(self, x, y, floor_num=1):
        super().__init__(x, y, 32, 24, "chest")
        self.state = CHEST_CLOSED
        self._open_timer = 0
        self._loot_given = False
        self.floor_num = floor_num

    def interact(self, player, crafting_system=None):
        if self.state == CHEST_CLOSED:
            self.state = CHEST_OPENING
            self._open_timer = 20
            return True
        return False

    def update(self, dt=1):
        super().update(dt)
        if self.state == CHEST_OPENING:
            self._open_timer -= 1
            if self._open_timer <= 0:
                self.state = CHEST_OPEN

    def grant_loot(self, player):
        """Grant loot when chest finishes opening. Called by game loop."""
        if self._loot_given:
            return
        self._loot_given = True
        import random
        # Always give 2 jelly powder
        powder = getattr(player, "jello_powder_count", 0)
        player.jello_powder_count = powder + 2
        # On later floors, chance for a bonus item
        if self.floor_num >= 8 and random.random() < 0.4:
            drop = random.choice(self.RARE_DROPS)
            if drop == 'water':
                player.has_water = True
            elif drop.startswith('pill_'):
                # Give a pill if player doesn't already have one
                if not getattr(player, 'active_pill', None):
                    from game.engine.settings import PILL_DURATIONS
                    pill_type = drop.replace('pill_', '')
                    player.active_pill = pill_type
                    player.pill_timer = PILL_DURATIONS.get(pill_type, 60 * 60)

    def draw(self, surf, camera_offset):
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy
        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        if self.state == CHEST_CLOSED:
            # Closed box — brown/wooden
            body = pygame.Rect(int(sx), int(sy) + 6, self.w, self.h - 6)
            pygame.draw.rect(surf, (100, 65, 30), body)
            # Lid
            lid = pygame.Rect(int(sx) - 1, int(sy) + 4, self.w + 2, 6)
            pygame.draw.rect(surf, (120, 80, 40), lid)
            # Clasp
            pygame.draw.rect(surf, (200, 180, 50),
                             pygame.Rect(int(sx) + self.w // 2 - 2,
                                         int(sy) + 6, 4, 4))

        elif self.state == CHEST_OPENING:
            # Lid tilting open
            body = pygame.Rect(int(sx), int(sy) + 6, self.w, self.h - 6)
            pygame.draw.rect(surf, (100, 65, 30), body)
            # Lid angled up
            lid = pygame.Rect(int(sx) - 1, int(sy), self.w + 2, 5)
            pygame.draw.rect(surf, (120, 80, 40), lid)
            # Glow from inside
            glow_surf = pygame.Surface((self.w - 4, 6), pygame.SRCALPHA)
            glow_surf.fill((125, 223, 100, 100))
            surf.blit(glow_surf, (int(sx) + 2, int(sy) + 8))

        else:  # CHEST_OPEN
            # Open box
            body = pygame.Rect(int(sx), int(sy) + 8, self.w, self.h - 8)
            pygame.draw.rect(surf, (80, 50, 25), body)
            # Lid fully open (behind)
            lid = pygame.Rect(int(sx) - 1, int(sy) - 2, self.w + 2, 5)
            pygame.draw.rect(surf, (100, 65, 30), lid)


# ──────────────────────────────────────────────
#  Door
# ──────────────────────────────────────────────
class Door(Interactable):
    """Glowing door for room/floor transitions."""

    def __init__(self, x, y, target_floor=None):
        super().__init__(x, y, 48, 64, "door")
        self.target_floor = target_floor

    def interact(self, player, crafting_system=None):
        # Transition handled by game state manager
        return True

    def draw(self, surf, camera_offset):
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy
        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        # Door frame — dark stone
        frame = pygame.Rect(int(sx), int(sy), self.w, self.h)
        pygame.draw.rect(surf, (40, 38, 50), frame)

        # Inner door — slightly lighter
        inner = pygame.Rect(int(sx) + 4, int(sy) + 4, self.w - 8, self.h - 4)
        pygame.draw.rect(surf, (55, 52, 65), inner)

        # Glow effect — pulsing amber around the edges
        pulse = int(abs(math.sin(self._tick * 0.04)) * 50)
        glow_alpha = 30 + pulse
        glow_surf = pygame.Surface((self.w + 8, self.h + 4), pygame.SRCALPHA)
        glow_surf.fill((232, 168, 56, min(glow_alpha, 120)))
        surf.blit(glow_surf, (int(sx) - 4, int(sy) - 2))

        # Redraw the door on top of glow
        pygame.draw.rect(surf, (40, 38, 50), frame)
        pygame.draw.rect(surf, (55, 52, 65), inner)

        # Handle
        handle_y = int(sy) + self.h // 2
        pygame.draw.circle(surf, TORCH_AMBER,
                           (int(sx) + self.w - 10, handle_y), 3)


# ── Shrine pill types (matches PillType enum values) ──
SHRINE_PILL_TYPES = ['fire', 'water', 'ice', 'electricity', 'attack_up']


# ──────────────────────────────────────────────
#  Shrine
# ──────────────────────────────────────────────
class Shrine(Interactable):
    """Y to interact — grants a random pill on first use."""

    def __init__(self, x, y):
        super().__init__(x, y, 40, 48, "shrine")
        self.used = False  # True after the shrine has been activated

    def interact(self, player, crafting_system=None):
        if self.used:
            return False  # already used — no further interaction

        # Only grant a pill if the player doesn't already have one active
        if getattr(player, 'active_pill', None) is not None:
            return False  # player already has an active pill

        # Pick a random pill type and grant it
        pill_type = random.choice(SHRINE_PILL_TYPES)
        player.active_pill = pill_type
        from game.engine.settings import PILL_DURATIONS
        player.pill_timer = PILL_DURATIONS.get(pill_type, 60 * 60)

        # Mark shrine as used
        self.used = True
        return True

    def draw(self, surf, camera_offset):
        ox, oy = camera_offset
        sx = self.x + ox
        sy = self.y + oy
        if (sx + self.w < 0 or sx > SCREEN_W
                or sy + self.h < 0 or sy > SCREEN_H):
            return

        # Stone pedestal base
        base_color = (70, 68, 78)
        base = pygame.Rect(int(sx), int(sy) + 32, self.w, 16)
        pygame.draw.rect(surf, base_color, base)

        # Pillar
        pillar = pygame.Rect(int(sx) + 10, int(sy) + 8, 20, 28)
        pygame.draw.rect(surf, (80, 78, 90), pillar)

        # Top cap
        cap = pygame.Rect(int(sx) + 6, int(sy) + 4, 28, 6)
        pygame.draw.rect(surf, (90, 88, 100), cap)

        # Glow orb on top — dimmer if used
        if self.used:
            # Used shrine: dim grey-green glow, no pulse
            glow_color = (80, 100, 80)
            orb_x = int(sx) + self.w // 2
            orb_y = int(sy) + 4
            pygame.draw.circle(surf, glow_color, (orb_x, orb_y), 4)
        else:
            # Active shrine: pulsing bright green glow
            pulse = int(abs(math.sin(self._tick * 0.05)) * 40)
            glow_color = (140 + pulse, 200, 140 + pulse)
            orb_x = int(sx) + self.w // 2
            orb_y = int(sy) + 4
            pygame.draw.circle(surf, glow_color, (orb_x, orb_y), 5)

            # Faint glow aura (only on active shrines)
            aura_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (140, 220, 140, 25 + pulse // 2),
                               (10, 10), 10)
            surf.blit(aura_surf, (orb_x - 10, orb_y - 10))


# ──────────────────────────────────────────────
#  Sun Zone
# ──────────────────────────────────────────────
class SunZone(Interactable):
    """
    Invisible trigger area — damages the player after 2 seconds (120 frames)
    of continuous exposure.  No visual representation (environmental hazard).
    """

    def __init__(self, x, y, w, h, damage_per_tick=1):
        super().__init__(x, y, w, h, "sun_zone")
        self.damage_per_tick = damage_per_tick
        # Track sun exposure per-player (keyed by id)
        self._sun_timers = {}

    def player_inside(self, player):
        """Call every frame a player overlaps this zone."""
        pid = id(player)
        self._sun_timers[pid] = self._sun_timers.get(pid, 0) + 1
        if self._sun_timers[pid] > 120:
            # Grace period expired — apply damage
            hp = getattr(player, "health", 100)
            player.health = max(0, hp - self.damage_per_tick)

    def player_left(self, player):
        """Reset timer when a player leaves the zone."""
        pid = id(player)
        self._sun_timers.pop(pid, None)

    def interact(self, player, crafting_system=None):
        # Sun zones are not interacted with via Y
        return False

    def draw(self, surf, camera_offset):
        # Invisible — no visual. This is purely environmental.
        pass
