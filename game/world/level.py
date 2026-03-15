"""
SPLIT — Level / Floor / Room Management
Loads floors from JSON, creates platform and interactable instances,
and provides the main LevelManager interface used by the game loop.
"""
import json
import os
import pygame
from game.engine.settings import (
    PlatformType, EnemyType, Difficulty,
    FLOOR_PALETTES, SCREEN_W, SCREEN_H,
)
from game.world.platforms import (
    SolidPlatform, MovingPlatform, CrumblingPlatform, ElevatorPlatform,
)
from game.world.interactables import (
    CookingPot, WaterSource, Chest, Door, Shrine, SunZone,
)

__all__ = ["Room", "Floor", "LevelManager"]

# Path to the level JSON files (relative to project root)
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "levels")


# ──────────────────────────────────────────────
#  Room
# ──────────────────────────────────────────────
class Room:
    """
    One contiguous area inside a floor.
    Most floors have a single room, but the schema supports multiple.
    """

    def __init__(self, data, floor_num, difficulty=Difficulty.NORMAL):
        self.width = data.get("width", 2560)
        self.height = data.get("height", 720)
        self.background_type = data.get("background", "default")

        # ── Build platforms ──
        self.platforms = []
        for p in data.get("platforms", []):
            plat = _make_platform(p, difficulty)
            plat.floor_num = floor_num
            self.platforms.append(plat)

        # ── Enemy spawn configs (we return dicts, not instances) ──
        self.enemy_spawns = []
        for e in data.get("enemies", []):
            self.enemy_spawns.append({
                "type": e.get("type", "sanitizer_bottle"),
                "x": e.get("x", 0),
                "y": e.get("y", 0),
                "patrol": e.get("patrol", []),
            })

        # ── Interactable configs ──
        self.interactable_positions = []
        for obj in data.get("interactables", []):
            self.interactable_positions.append({
                "type": obj.get("type", "chest"),
                "x": obj.get("x", 0),
                "y": obj.get("y", 0),
            })

        # ── Transition zones (elevators / tubes to other floors) ──
        self.transitions = []
        for t in data.get("transitions", []):
            self.transitions.append({
                "type": t.get("type", "elevator"),
                "x": t.get("x", 0),
                "y": t.get("y", 0),
                "w": t.get("w", 80),
                "h": t.get("h", 150),
                "target_floor": t.get("target_floor", 1),
            })


# ──────────────────────────────────────────────
#  Floor
# ──────────────────────────────────────────────
class Floor:
    """
    A full game floor (e.g. Floor 1 — Storage Rooms).
    Contains one or more Rooms and references the colour palette.
    """

    def __init__(self, floor_number, name, rooms, transition_type="elevator"):
        self.floor_number = floor_number
        self.name = name
        self.rooms = rooms                       # list[Room]
        self.transition_type = transition_type   # "elevator" or "tube"
        self.color_palette = FLOOR_PALETTES.get(floor_number,
                                                 FLOOR_PALETTES[1])
        self._current_room_index = 0

    def get_current_room(self):
        """Return the room the player is currently in."""
        if 0 <= self._current_room_index < len(self.rooms):
            return self.rooms[self._current_room_index]
        return self.rooms[0] if self.rooms else None

    def set_room(self, index):
        if 0 <= index < len(self.rooms):
            self._current_room_index = index


# ──────────────────────────────────────────────
#  LevelManager
# ──────────────────────────────────────────────
class LevelManager:
    """
    Central interface the game loop uses to access level data.
    Call `load_floor(n)` to swap to a new floor; then query platforms,
    enemies, and interactables for the current room.
    """

    def __init__(self, difficulty=Difficulty.NORMAL):
        self._floor = None              # current Floor object
        self._interactable_objs = []    # live Interactable instances
        self._difficulty = difficulty
        self._bg_floor_cache = None     # floor number last rendered

    # ── properties ──
    @property
    def current_floor(self):
        return self._floor

    # ── loading ──
    def load_floor(self, floor_num):
        """
        Load a floor from game/data/levels/floor_XX.json.
        Creates the Floor and Room objects, instantiates platforms,
        and prepares interactable instances.
        """
        filename = f"floor_{floor_num:02d}.json"
        filepath = os.path.normpath(os.path.join(_DATA_DIR, filename))

        with open(filepath, "r") as f:
            data = json.load(f)

        floor_number = data.get("floor", floor_num)
        name = data.get("name", f"Floor {floor_number}")
        transition = data.get("transition", "elevator")

        rooms = []
        for room_data in data.get("rooms", []):
            rooms.append(Room(room_data, floor_number, self._difficulty))

        self._floor = Floor(floor_number, name, rooms, transition)

        # Build live interactable objects for the current room
        self._build_interactables()

        # Cache floor number for background rendering
        self._bg_floor_cache = floor_number

    # ── queries ──
    def get_platforms(self):
        """Return the list of Platform objects for the current room."""
        room = self._current_room()
        return room.platforms if room else []

    def get_enemies(self):
        """Return list of enemy config dicts (type, x, y, patrol)."""
        room = self._current_room()
        return room.enemy_spawns if room else []

    def get_interactables(self):
        """Return list of live Interactable instances for the current room."""
        return self._interactable_objs

    def get_interactable_configs(self):
        """Return raw config dicts (type, x, y) for the current room."""
        room = self._current_room()
        return room.interactable_positions if room else []

    def get_transitions(self):
        """Return transition zone dicts for the current room."""
        room = self._current_room()
        return room.transitions if room else []

    def get_room_width(self):
        """Width in pixels of the current room (for camera bounds)."""
        room = self._current_room()
        return room.width if room else SCREEN_W

    def get_room_height(self):
        """Height in pixels of the current room."""
        room = self._current_room()
        return room.height if room else SCREEN_H

    # ── internal helpers ──
    def _current_room(self):
        if self._floor:
            return self._floor.get_current_room()
        return None

    def _build_interactables(self):
        """Instantiate Interactable objects from room config data."""
        self._interactable_objs = []
        room = self._current_room()
        if not room:
            return

        floor_num = self._floor.floor_number if self._floor else 1
        for cfg in room.interactable_positions:
            obj = _make_interactable(cfg, floor_num=floor_num)
            if obj:
                self._interactable_objs.append(obj)

        # Also create Door objects from transition data
        for t in room.transitions:
            door = Door(t["x"], t["y"], target_floor=t.get("target_floor"))
            door.w = t.get("w", 48)
            door.h = t.get("h", 64)
            self._interactable_objs.append(door)


# ──────────────────────────────────────────────
#  Factory helpers
# ──────────────────────────────────────────────
def _make_platform(data, difficulty=Difficulty.NORMAL):
    """Create the correct Platform subclass from a JSON dict."""
    ptype = data.get("type", "solid")
    x = data.get("x", 0)
    y = data.get("y", 0)
    w = data.get("w", 100)
    h = data.get("h", 16)

    if ptype == "solid":
        return SolidPlatform(x, y, w, h)

    elif ptype == "moving":
        path = data.get("path", [[x, y], [x + 100, y]])
        speed = data.get("speed", 1.5)
        return MovingPlatform(x, y, w, h, path, speed)

    elif ptype == "crumbling":
        return CrumblingPlatform(x, y, w, h, difficulty)

    elif ptype == "elevator":
        origin_y = data.get("origin_y", y)
        target_y = data.get("target_y", y - 200)
        speed = data.get("speed", 2)
        return ElevatorPlatform(x, y, w, h, origin_y, target_y, speed)

    # Fallback — solid
    return SolidPlatform(x, y, w, h)


def _make_interactable(cfg, floor_num=1):
    """Create the correct Interactable subclass from a config dict."""
    itype = cfg.get("type", "chest")
    x = cfg.get("x", 0)
    y = cfg.get("y", 0)

    if itype == "cooking_pot":
        return CookingPot(x, y)
    elif itype == "water_source":
        return WaterSource(x, y)
    elif itype == "chest":
        return Chest(x, y, floor_num=floor_num)
    elif itype == "door":
        return Door(x, y, target_floor=cfg.get("target_floor"))
    elif itype == "shrine":
        return Shrine(x, y)
    elif itype == "sun_zone":
        w = cfg.get("w", 200)
        h = cfg.get("h", 200)
        return SunZone(x, y, w, h)

    return None
