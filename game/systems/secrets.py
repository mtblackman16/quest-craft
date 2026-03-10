"""
SPLIT — Secrets & Easter Egg System
Tracks and triggers all 8 hidden secrets in the game.
"""

import datetime
import math
import random

import pygame

from game.engine.settings import (
    SCREEN_W, SCREEN_H,
    JELLO_GREEN, JELLO_GREEN_DIM, WHITE, BLACK,
    FONT_SMALL, FONT_SUBTITLE,
    GameEvent,
)


class SecretsManager:
    """Manages all 8 easter eggs / secrets in SPLIT."""

    total_secrets = 8

    def __init__(self):
        # ── Global tracking ──
        self.secrets_found: set[str] = set()

        # 1. Konami Code (input handled in title_screen)
        self.konami_activated: bool = False

        # 2. Architect's Room
        self.architect_room_found: bool = False

        # 3. Andrew's Gallery
        self.gallery_found: bool = False

        # 4. Fourth-Wall Fracture
        self.death_count: int = 0
        self._fourth_wall_triggered: bool = False
        self.glitch_active: bool = False
        self.glitch_timer: int = 0

        # 5. Claude the Shopkeeper
        self.barrel_interact_count: int = 0
        self._claude_revealed: bool = False

        # 6. Jello Graveyard
        self.wall_splats: list[tuple[int, int, int, tuple]] = []
        self._total_missed_shots: int = 0

        # 7. Idle Dance
        self.idle_dance_active: bool = False
        self._idle_notes: list[dict] = []

        # 8. Exhibition Day Mode
        self.exhibition_mode: bool = False
        self._exhibition_checked: bool = False
        self._exhibition_trophy_awarded: bool = False

        # ── Cached fonts (created lazily) ──
        self._font_small: pygame.font.Font | None = None
        self._font_subtitle: pygame.font.Font | None = None

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    def _get_font_small(self) -> pygame.font.Font:
        if self._font_small is None:
            self._font_small = pygame.font.Font(None, FONT_SMALL)
        return self._font_small

    def _get_font_subtitle(self) -> pygame.font.Font:
        if self._font_subtitle is None:
            self._font_subtitle = pygame.font.Font(None, FONT_SUBTITLE)
        return self._font_subtitle

    def get_count(self) -> tuple[int, int]:
        """Return (found, total) secrets."""
        return len(self.secrets_found), self.total_secrets

    def _discover(self, secret_name: str, event_bus=None, event_type=None):
        """Mark a secret as found if not already discovered."""
        if secret_name not in self.secrets_found:
            self.secrets_found.add(secret_name)
            if event_bus is not None:
                event_bus.emit(GameEvent.SECRET_FOUND, secret=secret_name)
                if event_type is not None:
                    event_bus.emit(event_type)

    # ──────────────────────────────────────────────
    # 1. Konami Code
    # ──────────────────────────────────────────────

    def activate_konami(self, event_bus=None):
        """Called from title screen when the Konami code is entered."""
        if not self.konami_activated:
            self.konami_activated = True
            self._discover("konami_code", event_bus)

    # ──────────────────────────────────────────────
    # 2. Architect's Room
    # ──────────────────────────────────────────────

    def check_architect_room(self, player_x: float, player_y: float,
                             just_ground_pounded: bool,
                             event_bus=None) -> bool:
        """Check if player ground-pounded the secret tile on Floor 1.

        Returns True on the frame the secret is first triggered.
        """
        if self.architect_room_found:
            return False

        if not just_ground_pounded:
            return False

        # Secret tile region on Floor 1
        if 1600 <= player_x <= 1700 and 480 <= player_y <= 500:
            self.architect_room_found = True
            self._discover("architect_room", event_bus, GameEvent.ARCHITECT_ROOM)
            return True

        return False

    # ──────────────────────────────────────────────
    # 3. Andrew's Gallery
    # ──────────────────────────────────────────────

    def check_gallery(self, floor_num: int, interact_x: float,
                      interact_y: float, event_bus=None) -> bool:
        """Check if the player interacted with the purple torch on Floor 7.

        Returns True on the frame the secret is first triggered.
        """
        if self.gallery_found:
            return False

        # Purple-tinted torch position on Floor 7
        if floor_num == 7 and 960 <= interact_x <= 1000 and 400 <= interact_y <= 440:
            self.gallery_found = True
            self._discover("andrews_gallery", event_bus)
            return True

        return False

    # ──────────────────────────────────────────────
    # 4. Fourth-Wall Fracture
    # ──────────────────────────────────────────────

    def _on_player_died(self, **kwargs):
        """Event callback when player dies."""
        self.death_count += 1

    def check_fourth_wall(self) -> bool:
        """Returns True the first frame death_count hits exactly 4."""
        if self._fourth_wall_triggered:
            return False

        if self.death_count == 4:
            self._fourth_wall_triggered = True
            self.glitch_active = True
            self.glitch_timer = 180
            self._discover("fourth_wall_fracture")
            return True

        return False

    def draw_glitch(self, surf: pygame.Surface):
        """Draw the fourth-wall glitch effect if active."""
        if not self.glitch_active:
            return

        self.glitch_timer -= 1
        w, h = surf.get_size()

        if self.glitch_timer <= 0:
            # Effect done — show brief golden indicator
            self.glitch_active = False
            return

        # Phase 1 (frames 180-60): visual chaos
        if self.glitch_timer > 60:
            # Horizontal line displacement — shift random rows
            num_slices = random.randint(3, 8)
            for _ in range(num_slices):
                row_y = random.randint(0, h - 1)
                row_h = random.randint(2, 12)
                shift = random.randint(-20, 20)
                if shift == 0:
                    shift = 5

                # Grab a strip and blit it offset
                strip_rect = pygame.Rect(0, row_y, w, row_h)
                strip_rect.clamp_ip(surf.get_rect())
                try:
                    strip = surf.subsurface(strip_rect).copy()
                    surf.blit(strip, (shift, row_y))
                except ValueError:
                    pass

            # Color channel separation (red/blue offset)
            if random.random() < 0.4:
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                # Red channel shifted right
                overlay.fill((255, 0, 0, 25))
                surf.blit(overlay, (random.randint(2, 6), 0))
                # Blue channel shifted left
                overlay.fill((0, 0, 255, 25))
                surf.blit(overlay, (random.randint(-6, -2), 0))

            # Random static rectangles
            for _ in range(random.randint(2, 6)):
                rx = random.randint(0, w - 1)
                ry = random.randint(0, h - 1)
                rw = random.randint(10, 80)
                rh = random.randint(4, 20)
                gray = random.randint(0, 255)
                static_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
                static_surf.fill((gray, gray, gray, random.randint(60, 140)))
                surf.blit(static_surf, (rx, ry))

        # Phase 2 (frames 60-0): "REBOOTING..." text
        if self.glitch_timer <= 60:
            font = self._get_font_subtitle()
            # Flicker the text
            if self.glitch_timer % 8 < 5:
                dots = "." * ((60 - self.glitch_timer) // 15 % 4)
                text = font.render(f"REBOOTING{dots}", True, JELLO_GREEN)
                text_rect = text.get_rect(center=(w // 2, h // 2))
                # Dark backdrop
                backdrop = pygame.Surface((w, 60), pygame.SRCALPHA)
                backdrop.fill((0, 0, 0, 180))
                surf.blit(backdrop, (0, h // 2 - 30))
                surf.blit(text, text_rect)

    # ──────────────────────────────────────────────
    # 5. Claude the Shopkeeper
    # ──────────────────────────────────────────────

    _BARREL_DIALOGUE = {
        1: "...",
        2: "...",
        3: "You're persistent.",
        4: "Fine. I'll talk.",
        5: "My name is Claude. Yes, THAT Claude.",
    }

    def check_barrel_npc(self, interact_x: float, interact_y: float,
                         floor_num: int, event_bus=None) -> str | None:
        """Interact with the barrel NPC on Floor 3.

        Returns the dialogue string if in range, or None.
        """
        if floor_num != 3:
            return None

        # Barrel NPC hitbox
        if not (1180 <= interact_x <= 1240 and 440 <= interact_y <= 480):
            return None

        self.barrel_interact_count += 1
        count = min(self.barrel_interact_count, 5)
        dialogue = self._BARREL_DIALOGUE.get(count)

        if self.barrel_interact_count >= 5 and not self._claude_revealed:
            self._claude_revealed = True
            self._discover("claude_shopkeeper", event_bus)

        return dialogue

    # ──────────────────────────────────────────────
    # 6. Jello Graveyard
    # ──────────────────────────────────────────────

    def add_wall_splat(self, x: int, y: int):
        """Add a permanent green splat where a jelly shot hit a wall."""
        size = random.randint(6, 16)
        # Slight color variation
        r = max(0, min(255, JELLO_GREEN[0] + random.randint(-20, 20)))
        g = max(0, min(255, JELLO_GREEN[1] + random.randint(-30, 10)))
        b = max(0, min(255, JELLO_GREEN[2] + random.randint(-15, 15)))
        color = (r, g, b)
        self.wall_splats.append((x, y, size, color))
        self._total_missed_shots += 1

        # Secret triggers when you have enough splats
        if self._total_missed_shots >= 50 and "jello_graveyard" not in self.secrets_found:
            self._discover("jello_graveyard")

    def draw_wall_splats(self, surf: pygame.Surface,
                         camera_offset: tuple[int, int]):
        """Draw all permanent jello splats on walls."""
        cam_x, cam_y = camera_offset
        screen_rect = surf.get_rect()

        for wx, wy, size, color in self.wall_splats:
            sx = wx - cam_x
            sy = wy - cam_y

            # Cull off-screen splats
            if not (-size <= sx <= screen_rect.width + size and
                    -size <= sy <= screen_rect.height + size):
                continue

            # Draw a blobby splat (circle + smaller drip circles)
            splat_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            alpha_color = (*color, 160)
            pygame.draw.circle(splat_surf, alpha_color, (size, size), size)
            # Small drip
            drip_size = max(2, size // 3)
            pygame.draw.circle(
                splat_surf, alpha_color,
                (size + random.randint(-2, 2), size + size - 1),
                drip_size,
            )
            surf.blit(splat_surf, (sx - size, sy - size))

    def get_graveyard_stats(self) -> dict:
        """Return graveyard statistics."""
        return {
            "total_missed": self._total_missed_shots,
            "total_splats": len(self.wall_splats),
        }

    # ──────────────────────────────────────────────
    # 7. Idle Dance
    # ──────────────────────────────────────────────

    def check_idle_dance(self, player_idle_timer: int) -> bool:
        """Returns True when the player has been idle for 30+ seconds."""
        if player_idle_timer > 1800:
            if not self.idle_dance_active:
                self.idle_dance_active = True
                self._idle_notes.clear()
                if "idle_dance" not in self.secrets_found:
                    self._discover("idle_dance")
            return True

        # Player moved — deactivate
        if self.idle_dance_active:
            self.idle_dance_active = False
            self._idle_notes.clear()
        return False

    def draw_idle_dance(self, surf: pygame.Surface, player_x: float,
                        player_y: float, camera_offset: tuple[int, int]):
        """Draw music note particles floating up from the player."""
        if not self.idle_dance_active:
            return

        cam_x, cam_y = camera_offset
        screen_x = player_x - cam_x
        screen_y = player_y - cam_y

        font = self._get_font_small()

        # Spawn new notes periodically
        if random.random() < 0.15:
            note_char = random.choice(["♪", "♫"])
            note_size = random.randint(14, 24)
            self._idle_notes.append({
                "char": note_char,
                "x": screen_x + random.randint(-15, 15),
                "y": screen_y - 10,
                "size": note_size,
                "drift_phase": random.uniform(0, math.pi * 2),
                "drift_speed": random.uniform(0.03, 0.07),
                "rise_speed": random.uniform(0.6, 1.2),
                "life": 0,
                "max_life": random.randint(80, 140),
                "color": random.choice([
                    JELLO_GREEN,
                    (180, 255, 150),
                    (100, 230, 180),
                    (200, 220, 100),
                ]),
            })

        # Update and draw existing notes
        surviving_notes = []
        for note in self._idle_notes:
            note["life"] += 1
            if note["life"] >= note["max_life"]:
                continue

            note["y"] -= note["rise_speed"]
            note["x"] += math.sin(note["life"] * note["drift_speed"]
                                  + note["drift_phase"]) * 0.8

            # Fade out near end of life
            life_ratio = note["life"] / note["max_life"]
            alpha = int(255 * (1.0 - life_ratio))
            alpha = max(0, min(255, alpha))

            note_font = pygame.font.Font(None, note["size"])
            try:
                text_surf = note_font.render(note["char"], True, note["color"])
                text_surf.set_alpha(alpha)
                surf.blit(text_surf, (int(note["x"]), int(note["y"])))
            except pygame.error:
                pass

            surviving_notes.append(note)

        self._idle_notes = surviving_notes

    # ──────────────────────────────────────────────
    # 8. Exhibition Day Mode
    # ──────────────────────────────────────────────

    def check_exhibition_day(self) -> bool:
        """Returns True if today is the exhibition: March 15, 2026."""
        today = datetime.date.today()
        is_exhibition = today == datetime.date(2026, 3, 15)
        if is_exhibition and not self._exhibition_checked:
            self._exhibition_checked = True
            self.exhibition_mode = True
            self._discover("exhibition_day")
        return is_exhibition

    def draw_golden_border(self, surf: pygame.Surface):
        """Draw a thin gold border around the screen on exhibition day."""
        if not self.exhibition_mode:
            return

        gold = (255, 215, 0)
        w, h = surf.get_size()
        thickness = 3

        pygame.draw.rect(surf, gold, (0, 0, w, h), thickness)
        # Inner glow line
        inner_gold = (255, 225, 80)
        pygame.draw.rect(surf, inner_gold,
                         (thickness, thickness,
                          w - thickness * 2, h - thickness * 2), 1)

    def award_exhibition_trophy(self, event_bus=None) -> bool:
        """Call when the first enemy is killed on exhibition day.

        Returns True if the trophy was awarded this call.
        """
        if not self.exhibition_mode:
            return False
        if self._exhibition_trophy_awarded:
            return False

        self._exhibition_trophy_awarded = True
        if event_bus is not None:
            event_bus.emit(GameEvent.ITEM_COLLECT, item="exhibited_trophy")
        return True

    # ──────────────────────────────────────────────
    # Integration: subscribe / on_event / update / draw
    # ──────────────────────────────────────────────

    def reset(self):
        """Reset session-specific state between playthroughs."""
        self.death_count = 0
        self._fourth_wall_triggered = False
        self.glitch_active = False
        self.glitch_timer = 0
        self.barrel_interact_count = 0
        self._claude_revealed = False
        self.wall_splats.clear()
        self._total_missed_shots = 0
        self.idle_dance_active = False
        self._idle_notes.clear()

    def subscribe(self, event_bus):
        """Subscribe to relevant game events."""
        event_bus.subscribe(GameEvent.PLAYER_DIED, self._on_player_died)

    def on_event(self, event_type: GameEvent, **kwargs):
        """Handle events forwarded from the EventBus.

        This is an alternative to subscribe() — the main loop can call
        this directly when events fire.
        """
        if event_type == GameEvent.PLAYER_DIED:
            self._on_player_died(**kwargs)

        elif event_type == GameEvent.PLAYER_INTERACT:
            # Check barrel NPC
            floor_num = kwargs.get("floor_num", 0)
            x = kwargs.get("x", 0)
            y = kwargs.get("y", 0)
            event_bus = kwargs.get("event_bus")
            self.check_barrel_npc(x, y, floor_num, event_bus)
            self.check_gallery(floor_num, x, y, event_bus)

        elif event_type == GameEvent.PLAYER_GROUND_POUND:
            x = kwargs.get("x", 0)
            y = kwargs.get("y", 0)
            floor_num = kwargs.get("floor_num", 1)
            event_bus = kwargs.get("event_bus")
            if floor_num == 1:
                self.check_architect_room(x, y, True, event_bus)

        elif event_type == GameEvent.ENEMY_DIED:
            event_bus = kwargs.get("event_bus")
            self.award_exhibition_trophy(event_bus)

    def update(self, player, floor_num: int, frame_count: int):
        """Called each frame from the main game loop.

        Args:
            player: Player object (needs .x, .y, .idle_timer attributes).
            floor_num: Current floor number.
            frame_count: Global frame counter.
        """
        # Exhibition day check (only once)
        if not self._exhibition_checked:
            self.check_exhibition_day()

        # Fourth-wall fracture
        self.check_fourth_wall()

        # Idle dance
        idle_timer = getattr(player, "idle_timer", 0)
        self.check_idle_dance(idle_timer)

    def draw(self, surf: pygame.Surface, camera_offset: tuple[int, int]):
        """Draw all secret visual effects.

        Called each frame after game entities are drawn.
        """
        # Wall splats (below other effects)
        self.draw_wall_splats(surf, camera_offset)

        # Idle dance particles
        if self.idle_dance_active:
            # We need player screen position — notes track their own coords
            # so just draw existing notes (they were positioned in update)
            # draw_idle_dance needs to be called separately with player pos
            pass

        # Glitch effect (overlays everything)
        self.draw_glitch(surf)

        # Golden border on exhibition day (always on top)
        self.draw_golden_border(surf)
