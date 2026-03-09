"""
SPLIT — Narrator System
An unseen voice that comments on key moments, once per playthrough.
Messages appear at the top of the screen with fade-in/hold/fade-out animation.
"""

import pygame
from game.engine.settings import (
    GameEvent, EventBus, NARRATOR_LINES,
    FONT_NARRATOR, SCREEN_W,
)


# ── Animation phase constants ──
_FADE_IN_FRAMES = 30
_HOLD_FRAMES = 180
_FADE_OUT_FRAMES = 30
_TOTAL_FRAMES = _FADE_IN_FRAMES + _HOLD_FRAMES + _FADE_OUT_FRAMES

# Text color: warm off-white
_TEXT_COLOR = (220, 215, 200)

# Background behind text
_BG_COLOR = (15, 12, 10)
_BG_ALPHA = 160
_BG_PAD_X = 24
_BG_PAD_Y = 10
_BG_RADIUS = 8
_BG_Y_OFFSET = 28  # distance from top of screen

# Mapping: gameplay events → narrator trigger events
# When we hear the left side from the EventBus, we fire the right side as a
# narrator one-shot (if it hasn't been shown yet).
_GAMEPLAY_TO_NARRATOR = {
    GameEvent.PLAYER_DIED: GameEvent.FIRST_DEATH,
    GameEvent.ENEMY_DIED: GameEvent.FIRST_ENEMY_KILL,
    GameEvent.SECRET_FOUND: GameEvent.FIRST_SECRET,
    GameEvent.PLAYER_SPLIT: GameEvent.FIRST_SPLIT,
    GameEvent.BOSS_ENTERED: GameEvent.FIRST_BOSS_ENCOUNTER,
    GameEvent.BOSS_DEFEATED: GameEvent.FIRST_BOSS_DEFEAT,
}

# These narrator events are emitted directly (no mapping needed)
_DIRECT_NARRATOR_EVENTS = [
    GameEvent.MAMA_SLOTH_DEFEAT,
    GameEvent.GRACIE_DEFEAT,
    GameEvent.FINAL_BOSS_REACH,
    GameEvent.ARCHITECT_ROOM,
    GameEvent.POST_CREDITS,
]


class NarratorSystem:
    """Displays one-shot narrator messages triggered by game events."""

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._shown: set = set()       # narrator event types already shown
        self._queue: list = []          # list of GameEvent keys waiting to display
        self._timer: int = 0            # frame counter for current message
        self._font = None               # lazy-init on first draw
        self._text_surface = None       # cached rendered text
        self._bg_surface = None         # cached semi-transparent background

        # Subscribe to gameplay events that map to narrator triggers
        for gameplay_event, narrator_event in _GAMEPLAY_TO_NARRATOR.items():
            # Use default-arg trick to capture narrator_event in the closure
            self._event_bus.subscribe(
                gameplay_event,
                lambda ne=narrator_event, **kw: self.trigger(ne),
            )

        # Subscribe to direct narrator events
        for narrator_event in _DIRECT_NARRATOR_EVENTS:
            self._event_bus.subscribe(
                narrator_event,
                lambda ne=narrator_event, **kw: self.trigger(ne),
            )

    # ── Public API ──

    def trigger(self, event_type: GameEvent):
        """Queue a narrator line if it hasn't been shown this playthrough."""
        if event_type in self._shown:
            return
        if event_type not in NARRATOR_LINES:
            return
        self._shown.add(event_type)
        self._queue.append(event_type)
        # If nothing is currently displaying, kick off the first message
        if len(self._queue) == 1:
            self._start_message()

    def update(self):
        """Advance animation timer. Call once per frame."""
        if not self._queue:
            return

        self._timer += 1

        if self._timer >= _TOTAL_FRAMES:
            # Current message finished — advance to next
            self._queue.pop(0)
            self._timer = 0
            self._text_surface = None
            self._bg_surface = None
            if self._queue:
                self._start_message()

    def draw(self, surf: pygame.Surface):
        """Render the current narrator message with fade animation."""
        if not self._queue:
            return

        self._ensure_font()

        # Build text + background surfaces on first frame of this message
        if self._text_surface is None:
            self._build_surfaces()

        # Compute alpha based on animation phase
        alpha = self._current_alpha()

        # Draw background
        bg = self._bg_surface.copy()
        bg.set_alpha(int(alpha * _BG_ALPHA / 255))
        bg_rect = bg.get_rect(centerx=SCREEN_W // 2, top=_BG_Y_OFFSET)
        surf.blit(bg, bg_rect)

        # Draw text
        txt = self._text_surface.copy()
        txt.set_alpha(alpha)
        txt_rect = txt.get_rect(centerx=SCREEN_W // 2,
                                top=_BG_Y_OFFSET + _BG_PAD_Y)
        surf.blit(txt, txt_rect)

    def reset(self):
        """Clear all state for a new playthrough."""
        self._shown.clear()
        self._queue.clear()
        self._timer = 0
        self._text_surface = None
        self._bg_surface = None

    # ── Internal helpers ──

    def _ensure_font(self):
        """Lazy-init the font (pygame must be initialised first)."""
        if self._font is None:
            try:
                self._font = pygame.font.SysFont("monospace", FONT_NARRATOR)
            except Exception:
                self._font = pygame.font.Font(None, FONT_NARRATOR)

    def _start_message(self):
        """Reset timer and surfaces for the message at the front of the queue."""
        self._timer = 0
        self._text_surface = None
        self._bg_surface = None

    def _build_surfaces(self):
        """Render the text and its background rectangle."""
        event_type = self._queue[0]
        line = NARRATOR_LINES.get(event_type, "")

        self._ensure_font()
        self._text_surface = self._font.render(line, True, _TEXT_COLOR)

        # Semi-transparent rounded-rect background
        tw, th = self._text_surface.get_size()
        bw = tw + _BG_PAD_X * 2
        bh = th + _BG_PAD_Y * 2
        self._bg_surface = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(
            self._bg_surface,
            (*_BG_COLOR, _BG_ALPHA),
            (0, 0, bw, bh),
            border_radius=_BG_RADIUS,
        )

    def _current_alpha(self) -> int:
        """Return 0-255 alpha for the current animation frame."""
        t = self._timer

        if t < _FADE_IN_FRAMES:
            # Fade in
            return int(255 * t / _FADE_IN_FRAMES)
        elif t < _FADE_IN_FRAMES + _HOLD_FRAMES:
            # Hold
            return 255
        else:
            # Fade out
            elapsed = t - _FADE_IN_FRAMES - _HOLD_FRAMES
            return int(255 * (1 - elapsed / _FADE_OUT_FRAMES))
