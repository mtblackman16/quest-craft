"""
SPLIT — Sprite Loader & Cache
Loads and caches Andrew's artwork for use throughout the game.
All sprites are loaded once and cached by (path, width, height) key.
"""
import os
import pygame

# Resolve assets/images relative to the project root
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_IMAGES_DIR = os.path.join(_PROJECT_ROOT, "assets", "images")

# Cache: (path, w, h) -> pygame.Surface
_sprite_cache: dict[tuple, pygame.Surface] = {}

# Cache for portraits: (path, size) -> pygame.Surface
_portrait_cache: dict[tuple, pygame.Surface] = {}


def load_sprite(rel_path, width, height):
    """Load and scale a sprite from assets/images/.

    Parameters
    ----------
    rel_path : str
        Path relative to assets/images/ (e.g. 'player/jello-cube-front.png').
    width : int
        Target width in pixels.
    height : int
        Target height in pixels.

    Returns
    -------
    pygame.Surface or None
        The loaded sprite with per-pixel alpha, or None if the file doesn't exist.
    """
    key = (rel_path, width, height)
    cached = _sprite_cache.get(key)
    if cached is not None:
        return cached

    full_path = os.path.join(_IMAGES_DIR, rel_path)
    if not os.path.isfile(full_path):
        return None

    try:
        raw = pygame.image.load(full_path).convert_alpha()
        scaled = pygame.transform.scale(raw, (width, height))
        _sprite_cache[key] = scaled
        return scaled
    except (pygame.error, FileNotFoundError):
        return None


def load_portrait(rel_path, size):
    """Load an image and crop it into a circular portrait.

    Parameters
    ----------
    rel_path : str
        Path relative to assets/images/ (e.g. 'bosses/gracie-happy-face.jpg').
    size : int
        Diameter of the circular portrait in pixels.

    Returns
    -------
    pygame.Surface or None
        Circular portrait with per-pixel alpha, or None if file doesn't exist.
    """
    key = (rel_path, size)
    cached = _portrait_cache.get(key)
    if cached is not None:
        return cached

    full_path = os.path.join(_IMAGES_DIR, rel_path)
    if not os.path.isfile(full_path):
        return None

    try:
        raw = pygame.image.load(full_path).convert_alpha()
        # Scale to fill the circle
        scaled = pygame.transform.scale(raw, (size, size))
        # Create circular mask
        portrait = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(portrait, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
        # Use the circle as a mask
        scaled.blit(portrait, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Draw border ring
        pygame.draw.circle(scaled, (200, 180, 140), (size // 2, size // 2), size // 2, 2)

        _portrait_cache[key] = scaled
        return scaled
    except (pygame.error, FileNotFoundError):
        return None


def flip_h(surface):
    """Return a horizontally flipped copy of a surface."""
    if surface is None:
        return None
    return pygame.transform.flip(surface, True, False)
