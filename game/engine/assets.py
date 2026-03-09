"""
AssetLoader — pre-scale, convert_alpha, cache.
Graceful fallback: returns colored rectangles if image files don't exist.
"""
import os
import pygame


class AssetLoader:
    """Loads and caches game assets (images, sounds)."""

    def __init__(self, base_path=None):
        if base_path is None:
            # Default to quest-craft/assets/
            base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')
        self.base_path = base_path
        self._image_cache = {}
        self._sound_cache = {}

    def load_image(self, path, scale=None, convert_alpha=True):
        """Load an image, cache it. Returns Surface."""
        key = (path, scale)
        if key in self._image_cache:
            return self._image_cache[key]

        full_path = os.path.join(self.base_path, 'images', path)
        try:
            img = pygame.image.load(full_path)
            if convert_alpha:
                img = img.convert_alpha()
            else:
                img = img.convert()
            if scale:
                img = pygame.transform.scale(img, scale)
        except (pygame.error, FileNotFoundError):
            # Fallback: colored rectangle
            w, h = scale if scale else (32, 32)
            img = pygame.Surface((w, h), pygame.SRCALPHA)
            img.fill((255, 0, 255, 128))  # magenta = missing

        self._image_cache[key] = img
        return img

    def load_sound(self, path):
        """Load a sound file, cache it. Returns Sound or None."""
        if path in self._sound_cache:
            return self._sound_cache[path]

        full_path = os.path.join(self.base_path, 'sounds', path)
        try:
            snd = pygame.mixer.Sound(full_path)
            self._sound_cache[path] = snd
            return snd
        except (pygame.error, FileNotFoundError):
            self._sound_cache[path] = None
            return None

    def clear_cache(self):
        self._image_cache.clear()
        self._sound_cache.clear()
