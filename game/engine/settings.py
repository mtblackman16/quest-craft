"""
SPLIT — Game Settings & Constants
All shared constants, enums, event bus, controller maps, gameplay values.
"""
import enum

# ── Screen ──
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TILE_SIZE = 32

# ── Physics ──
GRAVITY = 0.6
MAX_FALL_SPEED = 15
GROUND_POUND_SPEED = 20
PLAYER_SPEED = 4.5
PLAYER_JUMP_POWER = -12
PLAYER_BASE_SIZE = 40

# ── Gameplay Values ──
PLAYER_MAX_HEALTH = 100
JELLY_SHOT_COST = 5
JELLO_POWDER_HEAL = 25
PERFECT_DODGE_FRAMES = 10  # ~167ms at 60fps
SPLIT_DURATION = 180  # 3 seconds at 60fps

# Enemy HP
SMALL_BOTTLE_HP = 30
SANITIZER_WARRIOR_HP = 60
JELLY_ARCHER_HP = 20

# Enemy damage
BOTTLE_TRAIL_DAMAGE = 2  # per tick
WARRIOR_GLOB_DAMAGE = 15
ARCHER_ARROW_DAMAGE = 20
HARD_DAMAGE_MULTIPLIER = 1.25

# Boss HP
BIG_BOTTLE_HP = 200
CLEANSER_HP = 400
LAST_GUARD_HP = 500
GRACIE_HP = 250
MAMA_SLOTH_HP = 600

# ── Pill Durations (frames at 60fps) ──
PILL_DURATIONS = {
    'fire': 75 * 60,       # 75 seconds
    'water': 75 * 60,
    'ice': 60 * 60,        # 60 seconds
    'electricity': 90 * 60, # 90 seconds
    'attack_up': 60 * 60,
}

# ── Enums ──

class GameState(enum.Enum):
    TITLE = "title"
    GAMEPLAY = "gameplay"
    DEATH = "death"
    CREDITS = "credits"
    ATTRACT = "attract"
    PAUSE = "pause"
    OPENING = "opening"
    INVENTORY = "inventory"


class Difficulty(enum.Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EARTHQUAKE = "earthquake"


class EnemyType(enum.Enum):
    SANITIZER_BOTTLE = "sanitizer_bottle"
    SANITIZER_WARRIOR = "sanitizer_warrior"
    JELLY_ARCHER = "jelly_archer"


class BossType(enum.Enum):
    BIG_BOTTLE = "big_bottle"
    CLEANSER = "cleanser"
    LAST_GUARD = "last_guard"
    GRACIE = "gracie"
    MAMA_SLOTH = "mama_sloth"


class PlatformType(enum.Enum):
    SOLID = "solid"
    MOVING = "moving"
    CRUMBLING = "crumbling"
    ELEVATOR = "elevator"


class MusicZone(enum.Enum):
    TITLE = "title"
    FLOORS_1_4 = "floors_1_4"
    FLOORS_5_8 = "floors_5_8"
    FLOORS_9_11 = "floors_9_11"
    FLOORS_12_14 = "floors_12_14"
    FLOOR_15 = "floor_15"
    BOSS = "boss"
    DEATH = "death"
    VICTORY = "victory"
    SECRET = "secret"


class PillType(enum.Enum):
    FIRE = "fire"
    WATER = "water"
    ICE = "ice"
    ELECTRICITY = "electricity"
    ATTACK_UP = "attack_up"


class GameEvent(enum.Enum):
    # Player events
    PLAYER_JUMP = "player_jump"
    PLAYER_LAND = "player_land"
    PLAYER_SHOOT = "player_shoot"
    PLAYER_HIT = "player_hit"
    PLAYER_DIED = "player_died"
    PLAYER_GROUND_POUND = "player_ground_pound"
    PLAYER_DODGE = "player_dodge"
    PLAYER_SPLIT = "player_split"
    PLAYER_UNSPLIT = "player_unsplit"
    PLAYER_HEAL = "player_heal"
    PLAYER_INTERACT = "player_interact"

    # Enemy events
    ENEMY_HIT = "enemy_hit"
    ENEMY_DIED = "enemy_died"

    # Boss events
    BOSS_ENTERED = "boss_entered"
    BOSS_PHASE_CHANGE = "boss_phase_change"
    BOSS_DEFEATED = "boss_defeated"

    # Game events
    FLOOR_CHANGE = "floor_change"
    ITEM_COLLECT = "item_collect"
    SECRET_FOUND = "secret_found"
    CHECKPOINT_REACHED = "checkpoint_reached"

    # Narrator triggers
    FIRST_DEATH = "first_death"
    FIRST_ENEMY_KILL = "first_enemy_kill"
    FIRST_SECRET = "first_secret"
    FIRST_SPLIT = "first_split"
    FIRST_BOSS_ENCOUNTER = "first_boss_encounter"
    FIRST_BOSS_DEFEAT = "first_boss_defeat"
    MAMA_SLOTH_DEFEAT = "mama_sloth_defeat"
    GRACIE_DEFEAT = "gracie_defeat"
    FINAL_BOSS_REACH = "final_boss_reach"
    ARCHITECT_ROOM = "architect_room"
    POST_CREDITS = "post_credits"


# ── EventBus ──

class EventBus:
    """Simple pub/sub event system."""
    def __init__(self):
        self._listeners = {}

    def subscribe(self, event, callback):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def emit(self, event, **kwargs):
        for cb in self._listeners.get(event, []):
            cb(**kwargs)


# ── Controller Mapping ──
# Nintendo Switch Pro Controller (verified on Pi 5)
CTRL_B = 0       # Jelly Shot
CTRL_A = 1       # Jump
CTRL_X = 2       # Eat Jello Powder
CTRL_Y = 3       # Interact
CTRL_CAPTURE = 4  # unused
CTRL_L = 5       # Switch Split Piece
CTRL_R = 6       # unused
CTRL_ZL = 7      # Split/Combine Toggle
CTRL_ZR = 8      # Perfect Dodge
CTRL_MINUS = 9   # Inventory
CTRL_PLUS = 10   # Pause
CTRL_HOME = 11   # system
CTRL_LSTICK = 12  # unused
CTRL_RSTICK = 13  # unused

# Axes
AXIS_LX = 0
AXIS_LY = 1
AXIS_RX = 2
AXIS_RY = 3

# Deadzone
STICK_DEADZONE = 0.3

# ── Keyboard Mapping ──
import pygame
KEY_JUMP = pygame.K_SPACE
KEY_SHOOT = pygame.K_z
KEY_EAT = pygame.K_x
KEY_INTERACT = pygame.K_c
KEY_SPLIT = pygame.K_q
KEY_DODGE = pygame.K_e
KEY_SWITCH_SPLIT = pygame.K_TAB
KEY_INVENTORY = pygame.K_i
KEY_PAUSE = pygame.K_ESCAPE

# ── Colors — Castle Interior Palettes by Floor ──
# Each tuple: (deep_stone, warm_stone, floor_color, accent)
FLOOR_PALETTES = {
    # Floors 1-3: Dark bluish-brown
    1: ((26, 26, 46), (45, 45, 68), (35, 30, 50), (55, 55, 80)),
    2: ((24, 24, 44), (42, 42, 65), (33, 28, 48), (52, 52, 78)),
    3: ((22, 22, 42), (40, 40, 62), (30, 26, 45), (50, 50, 75)),
    # Floors 4-6: Red and green shifting
    4: ((35, 25, 30), (55, 40, 45), (45, 30, 35), (120, 60, 50)),
    5: ((30, 32, 28), (50, 52, 45), (40, 38, 32), (80, 110, 60)),
    6: ((35, 30, 25), (58, 48, 40), (48, 38, 30), (110, 80, 50)),
    # Floors 7-8: Lighter transition
    7: ((45, 42, 55), (70, 65, 80), (55, 50, 65), (140, 120, 160)),
    8: ((50, 48, 60), (75, 70, 85), (60, 55, 70), (150, 130, 170)),
    # Floors 9-11: Bright
    9: ((65, 60, 55), (90, 85, 78), (75, 68, 60), (180, 160, 140)),
    10: ((70, 65, 58), (95, 90, 82), (80, 72, 62), (190, 170, 145)),
    11: ((75, 70, 62), (100, 95, 86), (85, 76, 66), (200, 180, 150)),
    # Floors 12-14: Light but ominous
    12: ((80, 75, 70), (110, 105, 98), (90, 82, 75), (160, 140, 130)),
    13: ((85, 80, 75), (115, 110, 102), (95, 86, 78), (165, 145, 135)),
    14: ((90, 85, 80), (120, 115, 108), (100, 90, 82), (170, 150, 140)),
    # Floor 15: Lightest
    15: ((110, 108, 100), (145, 140, 132), (120, 115, 105), (220, 210, 195)),
}

# Named colors
JELLO_GREEN = (125, 223, 100)
JELLO_GREEN_DIM = (80, 160, 60)
JELLO_BODY_ALPHA = (100, 210, 80, 140)
TORCH_AMBER = (232, 168, 56)
TORCH_GLOW = (245, 230, 200)
EMBER = (196, 75, 43)
VINE_GREEN = (60, 100, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
HEALTH_GREEN = (80, 200, 80)
HEALTH_AMBER = (220, 180, 50)
HEALTH_RED = (220, 60, 60)

# Sanitizer colors
SANITIZER_BLUE = (100, 180, 220)
SANITIZER_TRAIL = (120, 200, 240, 80)
SANITIZER_PUDDLE = (100, 180, 220, 100)

# ── Narrator Lines ──
NARRATOR_LINES = {
    GameEvent.FIRST_DEATH: "That's okay. They always get back up.",
    GameEvent.FIRST_ENEMY_KILL: "They figured it out faster than I expected.",
    GameEvent.FIRST_SECRET: "I knew they'd find that one.",
    GameEvent.FIRST_SPLIT: "Now they're thinking like jello.",
    GameEvent.FIRST_BOSS_ENCOUNTER: "This is the part where it gets real.",
    GameEvent.FIRST_BOSS_DEFEAT: "They're ready for what comes next.",
    GameEvent.MAMA_SLOTH_DEFEAT: "She'll be fine. She's tougher than she looks.",
    GameEvent.GRACIE_DEFEAT: "She's already planning a rematch. She always does.",
    GameEvent.FINAL_BOSS_REACH: "I always knew they could do it.",
    GameEvent.ARCHITECT_ROOM: "They found the room. Of course they did.",
    GameEvent.POST_CREDITS: "This was always their game. I just opened the door.",
}

# ── Audio ──
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 32
AUDIO_BUFFER = 512
SFX_CHANNELS = range(8, 16)   # channels 8-15 for SFX
MUSIC_CHANNELS = range(0, 4)  # channels 0-3 for music layers
STINGER_CHANNELS = range(5, 8)  # channels 5-7 for stingers

# ── Font Sizes ──
FONT_TITLE = 72
FONT_SUBTITLE = 28
FONT_PROMPT = 24
FONT_SMALL = 20
FONT_HUD = 18
FONT_NARRATOR = 22
FONT_DAMAGE = 26

# ── Difficulty Scaling ──
DIFFICULTY_SETTINGS = {
    Difficulty.EASY: {
        'damage_multiplier': 1.0,
        'checkpoint': True,
        'crumble_respawn': True,
        'timed': False,
    },
    Difficulty.NORMAL: {
        'damage_multiplier': 1.0,
        'checkpoint': True,
        'crumble_respawn': True,
        'timed': False,
    },
    Difficulty.HARD: {
        'damage_multiplier': 1.25,
        'checkpoint': False,
        'crumble_respawn': True,
        'timed': False,
    },
    Difficulty.EARTHQUAKE: {
        'damage_multiplier': 1.25,
        'checkpoint': False,
        'crumble_respawn': False,
        'timed': True,
    },
}

# ── Banana Slug ──
SLUG_APPEAR_DELAY = 30 * 60  # 30 seconds at 60fps
SLUG_SPEED = 0.8
