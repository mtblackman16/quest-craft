"""
SPLIT — Main Game
State machine: TITLE → GAMEPLAY → DEATH → CREDITS
All systems initialized and wired here.
"""
import pygame
import sys
import os
import math
import argparse
import json
import time as _time

# Ensure game package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.engine.settings import (
    SCREEN_W, SCREEN_H, FPS, GameState, Difficulty, GameEvent, EventBus, MusicZone,
    CTRL_A, CTRL_B, CTRL_X, CTRL_Y, CTRL_L, CTRL_R, CTRL_ZL, CTRL_ZR,
    CTRL_MINUS, CTRL_PLUS, AXIS_LY, STICK_DEADZONE, FLOOR_PALETTES,
    KEY_JUMP, KEY_SHOOT, KEY_EAT, KEY_INTERACT, KEY_SPLIT, KEY_DODGE,
    KEY_SWITCH_SPLIT, KEY_INVENTORY, KEY_PAUSE,
    JELLO_GREEN, TORCH_AMBER, TORCH_GLOW,
)
from game.engine.camera import Camera
from game.entities.player import JelloCube, JelloProjectile
from game.world.platforms import SolidPlatform

# Boss imports
try:
    from game.entities.bosses import Boss, BigBottle, TheCleanser, TheLastGuard, Gracie, MamaSloth
    BOSSES_AVAILABLE = True
except ImportError:
    BOSSES_AVAILABLE = False
    Boss = None

# Secrets import
try:
    from game.systems.secrets import SecretsManager
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False


class Game:
    """Main game class — owns the state machine and all systems."""

    def __init__(self, test_mode=False, test_floor=1, test_duration=30):
        # Pre-init audio mixer BEFORE pygame.init() for correct sample rate
        try:
            from game.systems.sound import SFXManager
            SFXManager.pre_init()
        except Exception:
            pass
        pygame.init()
        if test_mode:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        else:
            self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        pygame.display.set_caption("SPLIT")
        self.clock = pygame.time.Clock()

        # Test mode (automated playtesting)
        self.test_mode = test_mode
        self.test_start_floor = test_floor
        self.test_duration = test_duration  # seconds per floor
        self._test_ai_tick = 0  # frame counter for AI decisions
        self._test_run_dir = None  # set by harness
        self._test_log_file = None  # JSONL file handle
        self._test_floor_start = 0  # time.time() when floor started
        self._test_last_screenshot = 0  # time of last screenshot
        self._test_screenshot_count = 0
        self._test_max_floor = 15  # stop after this floor
        self._test_prev_pos = None  # for stuck detection
        self._test_stuck_count = 0

        # Event bus
        self.event_bus = EventBus()

        # State
        self.state = GameState.TITLE
        self.difficulty = Difficulty.NORMAL
        self.run_count = 0
        self.current_floor = 1
        self.frame_count = 0

        # First-time trackers for narrator
        self._first_death_triggered = False
        self._first_kill_triggered = False
        self._first_split_triggered = False
        self._first_boss_triggered = False

        # Opening cinematic tracker
        self._opening_shown = False

        # Active boss reference (only one boss at a time)
        self._boss = None

        # Checkpoint system
        self._checkpoint = None  # dict with saved player state
        self._checkpoint_floor = -1
        self._checkpoint_text_timer = 0

        # Floor transition effect
        self._floor_transition_active = False
        self._floor_transition_frame = 0
        self._floor_transition_target = 1
        self._floor_transition_name = ""

        # Boss intro sequence
        self._boss_intro_active = False
        self._boss_intro_frame = 0
        self._boss_intro_name = ""
        self._boss_intro_boss_pos = (0, 0)

        # Controller
        self.joystick = None
        self._init_controller()

        # Stick edge detection for ground pound
        self._stick_was_down = False

        # Core game objects
        self.camera = Camera()
        self.player = None
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.hazards = []
        self.enemies = []
        self.platforms = []
        self.interactables = []

        # Systems (populated in _init_systems)
        self.vfx = None
        self.combat = None
        self.awareness = None
        self.level_manager = None
        self.sfx = None
        self.music = None
        self.hud = None
        self.narrator = None
        self.crafting = None
        self.secrets = None

        # Cached background surface (avoid per-line gradient each frame)
        self._bg_cache_floor = -1
        self._bg_surface = None

        # Cached torch glow surface (avoid per-frame SRCALPHA allocation)
        self._torch_glow_cache = None

    def _init_controller(self):
        """Initialize first available controller."""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            except Exception:
                self.joystick = None

    def _show_reconnect_overlay(self):
        """Show 'Reconnect Controller' overlay, blocking until reconnected or keyboard dismiss."""
        font = pygame.font.Font(None, 48)
        small = pygame.font.Font(None, 28)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        msg = font.render("Controller Disconnected", True, (255, 200, 80))
        hint = small.render("Reconnect controller or press SPACE to continue with keyboard", True, (200, 200, 200))
        overlay.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H // 2 - 40))
        overlay.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H // 2 + 20))

        waiting = True
        while waiting:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.JOYDEVICEADDED:
                    self._init_controller()
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()

    def _init_systems(self):
        """Initialize all game systems. Called once at startup."""
        try:
            from game.systems.vfx import VFXManager
            self.vfx = VFXManager()
        except Exception:
            self.vfx = None

        try:
            from game.systems.combat import CombatSystem
            self.combat = CombatSystem(self.event_bus)
        except Exception:
            self.combat = None

        try:
            from game.systems.stealth import AwarenessSystem
            self.awareness = AwarenessSystem()
        except Exception:
            self.awareness = None

        try:
            from game.world.level import LevelManager
            self.level_manager = LevelManager(self.difficulty)
        except Exception:
            self.level_manager = None

        try:
            from game.systems.sound import SFXManager
            self.sfx = SFXManager()
        except Exception:
            self.sfx = None

        try:
            from game.systems.music import AdaptiveMusicManager
            self.music = AdaptiveMusicManager()
        except Exception:
            self.music = None

        try:
            from game.systems.hud import HUD
            self.hud = HUD()
        except Exception:
            self.hud = None

        try:
            from game.systems.narrator import NarratorSystem
            self.narrator = NarratorSystem(self.event_bus)
        except Exception:
            self.narrator = None

        try:
            from game.systems.crafting import CraftingSystem
            self.crafting = CraftingSystem()
        except Exception:
            self.crafting = None

        if SECRETS_AVAILABLE:
            try:
                self.secrets = SecretsManager()
                self.secrets.subscribe(self.event_bus)
            except Exception:
                self.secrets = None

    def _spawn_enemies_from_data(self, enemy_configs):
        """Create enemy instances from level data configs."""
        from game.entities.enemies import SmallSanitizerBottle, SanitizerWarrior, JellyArcher
        enemies = []
        for cfg in enemy_configs:
            etype = cfg.get('type', 'sanitizer_bottle')
            x = cfg.get('x', 100)
            y = cfg.get('y', 450)
            patrol = cfg.get('patrol', [])
            # Convert patrol to list of tuples
            patrol_points = [(p[0], p[1]) for p in patrol] if patrol else None

            if etype == 'sanitizer_bottle':
                enemy = SmallSanitizerBottle(x, y, patrol_points)
            elif etype == 'sanitizer_warrior':
                enemy = SanitizerWarrior(x, y, patrol_points)
            elif etype == 'jelly_archer':
                enemy = JellyArcher(x, y, patrol_points)
            else:
                continue

            # Snap enemy to nearest platform below their spawn point
            enemy_bottom = enemy.y + enemy.h
            best_plat_y = None
            for plat in self.platforms:
                pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(0, 0, 0, 0)
                if pr.width < 60:
                    continue  # skip tiny platforms
                # Platform must be at or below enemy's feet
                if pr.top >= enemy.y - 20 and pr.left <= x <= pr.right:
                    if best_plat_y is None or pr.top < best_plat_y:
                        best_plat_y = pr.top
            if best_plat_y is not None:
                enemy.y = best_plat_y - enemy.h
                # Also snap patrol points to same Y
                if enemy.patrol_path:
                    enemy.patrol_path = [(px, best_plat_y - enemy.h)
                                         for px, py in enemy.patrol_path]
            enemies.append(enemy)
        return enemies

    def _start_gameplay(self):
        """Reset for a new gameplay session."""
        # Clear event bus to prevent listener accumulation across playthroughs
        self.event_bus.clear()

        # Re-subscribe systems that need events
        if self.secrets:
            self.secrets.reset()
            self.secrets.subscribe(self.event_bus)
        if self.narrator:
            if hasattr(self.narrator, 'subscribe'):
                self.narrator.subscribe(self.event_bus)

        self.player = JelloCube(100, 400)
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.hazards = []
        self.enemies = []
        self.run_count += 1
        self.current_floor = 1
        self.frame_count = 0

        # Reset narrator for new playthrough
        if self.narrator:
            self.narrator.reset()
        self._first_death_triggered = False
        self._first_kill_triggered = False
        self._first_split_triggered = False

        # Load floor then fix spawn Y
        self._load_floor(self.current_floor)
        spawn_y = self._calc_spawn_y()
        self.player.y = spawn_y

    def _load_floor(self, floor_num):
        """Load a floor from level data and spawn entities."""
        self.current_floor = floor_num
        self.enemy_projectiles = []
        self.hazards = []

        # Reset floor timer for test mode
        if self.test_mode:
            self._test_floor_start = _time.time()

        self._boss = None

        if self.level_manager:
            try:
                self.level_manager.load_floor(floor_num)
                self.platforms = self.level_manager.get_platforms()
                enemy_configs = self.level_manager.get_enemies()
                self.enemies = self._spawn_enemies_from_data(enemy_configs)
                self.interactables = self.level_manager.get_interactables()
            except Exception:
                self._setup_fallback_level()
        else:
            self._setup_fallback_level()

        # Camera bounds
        level_w = self._get_level_width()
        level_h = self._get_level_height()
        self.camera.set_bounds(0, 0, max(SCREEN_W, level_w), max(SCREEN_H, level_h))
        if self.player:
            self.camera.reset(self.player.x, self.player.y)

        # Set floor-based music zone FIRST (boss override comes after)
        if self.music:
            if floor_num <= 4:
                self.music.set_zone(MusicZone.FLOORS_1_4)
            elif floor_num <= 8:
                self.music.set_zone(MusicZone.FLOORS_5_8)
            elif floor_num <= 11:
                self.music.set_zone(MusicZone.FLOORS_9_11)
            elif floor_num <= 14:
                self.music.set_zone(MusicZone.FLOORS_12_14)
            else:
                self.music.set_zone(MusicZone.FLOOR_15)

        # Spawn boss on boss floors (overrides music zone)
        self._boss_arena_active = False
        self._boss_arena_walls = []
        self._boss_arena_triggered = False
        if BOSSES_AVAILABLE:
            # Boss arena spans the right 60% of the level
            arena_l = int(level_w * 0.4)
            arena_r = max(1180, level_w - 100)
            # Calculate boss spawn Y from level data
            boss_y = self._calc_ground_y(level_w * 0.7)
            boss = None
            if floor_num == 4:
                boss = BigBottle(int(level_w * 0.7), boss_y, arena_left=arena_l, arena_right=arena_r)
            elif floor_num == 6:
                boss = Gracie(int(level_w * 0.7), boss_y, arena_left=arena_l, arena_right=arena_r)
            elif floor_num == 8:
                boss = TheCleanser(int(level_w * 0.7), boss_y, arena_left=arena_l, arena_right=arena_r)
            elif floor_num == 12:
                boss = MamaSloth(int(level_w * 0.7), boss_y, arena_left=arena_l, arena_right=arena_r)
            elif floor_num == 15:
                boss = TheLastGuard(int(level_w * 0.7), boss_y, arena_left=arena_l, arena_right=arena_r)
            if boss:
                self._boss = boss
                self._boss_arena_left = arena_l
                self._boss_arena_right = arena_r
                self.enemies.append(boss)
                if not self._first_boss_triggered:
                    self._first_boss_triggered = True
                    self.event_bus.emit(GameEvent.FIRST_BOSS_ENCOUNTER)
                # Trigger boss intro sequence
                self._boss_intro_active = True
                self._boss_intro_frame = 0
                self._boss_intro_name = getattr(boss, 'name', type(boss).__name__.upper())
                self._boss_intro_boss_pos = (boss.x + boss.w / 2, boss.y + boss.h / 2)

        # Stinger for floor change
        if self.music and floor_num > 1:
            self.music.play_stinger('floor_change')

        # Clear bg cache
        self._bg_cache_floor = -1

    def _setup_fallback_level(self):
        """Basic level when LevelManager isn't available."""
        self.platforms = [
            SolidPlatform(0, 500, 2560, 220),
            SolidPlatform(180, 400, 120, 16),
            SolidPlatform(380, 330, 140, 16),
            SolidPlatform(560, 400, 100, 16),
            SolidPlatform(280, 240, 100, 16),
            SolidPlatform(500, 180, 130, 16),
            SolidPlatform(750, 350, 120, 16),
            SolidPlatform(950, 280, 140, 16),
            SolidPlatform(1150, 400, 100, 16),
            SolidPlatform(1350, 320, 130, 16),
            SolidPlatform(1550, 250, 100, 16),
            SolidPlatform(1750, 400, 120, 16),
            SolidPlatform(1950, 350, 140, 16),
            SolidPlatform(2150, 280, 100, 16),
            SolidPlatform(2350, 400, 160, 16),
        ]
        self.enemies = []
        self.interactables = []

    def _get_level_width(self):
        if self.level_manager:
            return self.level_manager.get_room_width()
        return 2560

    def _get_level_height(self):
        if self.level_manager:
            return self.level_manager.get_room_height()
        return SCREEN_H

    def _calc_spawn_y(self):
        """Calculate player spawn Y from the first wide platform.
        Places player feet on the platform surface."""
        player_h = self.player.h if self.player else 64
        for plat in self.platforms:
            pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(0, 0, 0, 0)
            if pr.width >= 200 and pr.left <= 200:
                return pr.top - player_h  # feet on platform
        return 400  # fallback

    def _calc_ground_y(self, x_pos):
        """Find the ground Y position near x_pos from platform data.
        Used to spawn bosses on solid ground instead of hardcoded 400."""
        best_y = 400  # fallback
        for plat in self.platforms:
            pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(0, 0, 0, 0)
            # Find platform that's wide enough (ground floor) and overlaps x_pos
            if pr.width >= 200 and pr.left <= x_pos <= pr.right:
                boss_y = pr.top - 160  # spawn boss above the platform
                if boss_y > 0:
                    best_y = boss_y
                    break
        return best_y

    def get_state_snapshot(self):
        """Return dict of current game state for test logging."""
        return {
            'timestamp': _time.time(),
            'frame': self.frame_count,
            'floor': self.current_floor,
            'state': self.state.value if hasattr(self.state, 'value') else str(self.state),
            'player_x': round(self.player.x, 1) if self.player else None,
            'player_y': round(self.player.y, 1) if self.player else None,
            'player_health': self.player.health if self.player else None,
            'enemies_alive': len([e for e in self.enemies if e.alive]),
            'fps': int(self.clock.get_fps()),
        }

    def capture_screenshot(self, path):
        """Save current screen to a PNG file."""
        pygame.image.save(self.screen, path)

    def run(self):
        """Main loop."""
        self._init_systems()

        while True:
            if self.state == GameState.TITLE:
                self._run_title()
            elif self.state == GameState.GAMEPLAY:
                self._run_gameplay()
            elif self.state == GameState.DEATH:
                self._run_death()
            elif self.state == GameState.PAUSE:
                self._run_pause()
            elif self.state == GameState.CREDITS:
                self._run_credits()
            else:
                self.state = GameState.TITLE

    def _run_title(self):
        """Title screen. Loops on attract timeout; quits only on window close."""
        if self.test_mode:
            # Auto-select Normal difficulty in test mode
            self.difficulty = Difficulty.NORMAL
            if self.level_manager:
                self.level_manager._difficulty = self.difficulty
            self.state = GameState.GAMEPLAY
            self._start_gameplay()
            # Override starting floor if requested
            if self.test_start_floor > 1:
                self._load_floor(self.test_start_floor)
                self.player.x = 100
                self.player.y = self._calc_spawn_y()
            return

        # Set title music
        if self.music:
            self.music.set_zone(MusicZone.TITLE)

        while True:
            # Update music during title screen loop
            if self.music:
                self.music.update()
            try:
                from game.ui.title_screen import run_title_screen
                result = run_title_screen(self.screen, self.clock, self.joystick)
            except Exception:
                result = self._fallback_title()
            if result is not None:
                break
            # Attract timeout — loop title screen again
        self.difficulty = result

        # Update level manager with new difficulty
        if self.level_manager:
            self.level_manager._difficulty = self.difficulty

        # Play opening cinematic on first run
        if not self._opening_shown:
            self._opening_shown = True
            try:
                from game.ui.opening import run_opening
                run_opening(self.screen, self.clock, self.joystick)
            except Exception:
                pass

        self.state = GameState.GAMEPLAY
        self._start_gameplay()

    def _run_gameplay(self):
        """Main gameplay loop."""
        while self.state == GameState.GAMEPLAY:
            dt = self.clock.tick(FPS)
            self.frame_count += 1

            # Floor transition effect (blocks gameplay)
            if self._floor_transition_active:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._quit()
                self._do_floor_transition()
                continue

            # Boss intro sequence (blocks gameplay)
            if self._boss_intro_active:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._quit()
                self._do_boss_intro()
                continue

            # Check hitstop (freeze physics for impact feel)
            if self.vfx and self.vfx.hitstop_frames > 0:
                # During hitstop: still process events and draw, skip physics
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._quit()
                self.vfx.update()
                cam_offset = self.camera.get_offset()
                self._draw_gameplay(cam_offset)
                pygame.display.flip()
                continue

            # ── Events ──
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.KEYDOWN:
                    self._handle_key_down(event.key)
                if event.type == pygame.JOYBUTTONDOWN:
                    self._handle_button_down(event.button)
                if event.type == pygame.JOYHATMOTION:
                    if event.value[1] == -1 and self.player:
                        self.player.start_ground_pound()
                if event.type == pygame.JOYDEVICEADDED:
                    self._init_controller()
                if event.type == pygame.JOYDEVICEREMOVED:
                    self.joystick = None
                    self._show_reconnect_overlay()
                    self._init_controller()

            # Analog stick ground pound (edge detection)
            if self.joystick and self.player:
                try:
                    stick_down = self.joystick.get_axis(AXIS_LY) > 0.5
                    if stick_down and not self._stick_was_down:
                        self.player.start_ground_pound()
                    self._stick_was_down = stick_down
                except Exception:
                    pass

            if not self.player:
                continue

            # ── Slow-mo time scale ──
            time_scale = 1.0
            if self.vfx:
                time_scale = self.vfx.get_time_scale()

            # ── Update player ──
            keys = pygame.key.get_pressed()

            # Test mode: AI drives input instead of human
            if self.test_mode:
                self._test_ai_tick += 1
                keys = self._test_ai_get_keys()
                self._test_ai_actions()

            room_w = self._get_level_width()
            room_h = self._get_level_height()
            self.player.update(keys, self.platforms, self.joystick if not self.test_mode else None,
                               room_width=room_w, room_height=room_h)

            # Process player events
            for evt in self.player.pending_events:
                self.event_bus.emit(evt, player=self.player)

                # SFX
                if self.sfx:
                    sfx_map = {
                        GameEvent.PLAYER_JUMP: 'jump',
                        GameEvent.PLAYER_LAND: 'land',
                        GameEvent.PLAYER_SHOOT: 'jelly_shot',
                        GameEvent.PLAYER_GROUND_POUND: 'ground_pound',
                        GameEvent.PLAYER_DODGE: 'dodge',
                        GameEvent.PLAYER_SPLIT: 'split',
                        GameEvent.PLAYER_HIT: 'damage',
                        GameEvent.PLAYER_HEAL: 'collect',
                    }
                    if evt in sfx_map:
                        self.sfx.play(sfx_map[evt], self.player.x)

                # VFX for specific events
                if self.vfx:
                    if evt == GameEvent.PLAYER_GROUND_POUND:
                        cx = self.player.x + self.player.w / 2
                        cy = self.player.y + self.player.h
                        self.vfx.burst('ground_pound', cx, cy)
                        self.camera.shake(8)
                    elif evt == GameEvent.PLAYER_DODGE:
                        self.vfx.trigger_slow_mo(6)
                    elif evt == GameEvent.PLAYER_SPLIT:
                        cx, cy = self.player.get_center()
                        self.vfx.burst('split', cx, cy)
                    elif evt == GameEvent.PLAYER_HIT:
                        self.vfx.trigger_flash('red')
                        self.camera.shake(3)
                        if self.hud:
                            self.hud.trigger_jiggle()

                # Death
                if evt == GameEvent.PLAYER_DIED:
                    if self.vfx:
                        cx, cy = self.player.get_center()
                        self.vfx.burst('death', cx, cy)
                    if not self._first_death_triggered:
                        self._first_death_triggered = True
                        self.event_bus.emit(GameEvent.FIRST_DEATH)
                    self.state = GameState.DEATH
                    break

            # Clear processed events so they don't re-trigger next frame
            self.player.pending_events.clear()

            if self.state != GameState.GAMEPLAY:
                # Draw one final frame with death VFX
                cam_offset = self.camera.get_offset()
                self._draw_gameplay(cam_offset)
                pygame.display.flip()
                continue

            # ── Update player projectiles ──
            for proj in self.player_projectiles[:]:
                if not proj.update():
                    self.player_projectiles.remove(proj)

            # ── Update enemies + collect their projectiles ──
            # Skip enemy updates during slow-mo (dodge effect)
            skip_enemies = (time_scale < 0.5)
            from game.entities.enemies import SmallSanitizerBottle, SanitizerWarrior, JellyArcher
            for enemy in self.enemies[:]:
                if not enemy.alive:
                    continue
                if skip_enemies:
                    continue
                enemy.update(self.player)

                # Collect enemy-spawned projectiles/hazards
                if isinstance(enemy, SmallSanitizerBottle):
                    if enemy.should_spawn_trail():
                        self.hazards.append(enemy.spawn_trail())
                elif isinstance(enemy, SanitizerWarrior):
                    # Get ground_y: find the platform below the enemy
                    ground_y = self._get_level_height()
                    for plat in self.platforms:
                        pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(0, 0, 0, 0)
                        if pr.top > enemy.y and pr.width >= 100:
                            ground_y = pr.top
                            break
                    glob = enemy.consume_pending_glob(self.player, ground_y)
                    if glob:
                        self.enemy_projectiles.append(glob)
                elif isinstance(enemy, JellyArcher):
                    if hasattr(enemy, 'consume_pending_arrow'):
                        arrow = enemy.consume_pending_arrow(self.player)
                        if arrow:
                            self.enemy_projectiles.append(arrow)

                # Collect boss-specific projectiles
                if BOSSES_AVAILABLE and isinstance(enemy, Boss):
                    if hasattr(enemy, 'consume_pending_trails'):
                        for trail in enemy.consume_pending_trails():
                            self.hazards.append(trail)
                    if hasattr(enemy, 'consume_pending_projectiles'):
                        result = enemy.consume_pending_projectiles()
                        if isinstance(result, tuple):
                            # TheCleanser returns (globs, puddles)
                            globs, puddles = result
                            self.enemy_projectiles.extend(globs)
                            self.hazards.extend(puddles)
                        elif isinstance(result, list):
                            self.enemy_projectiles.extend(result)
                    if hasattr(enemy, 'consume_pending_arrows'):
                        for arrow in enemy.consume_pending_arrows():
                            self.enemy_projectiles.append(arrow)
                    # Gracie spawns minion enemies ("I'm Telling Mom!")
                    if hasattr(enemy, 'consume_spawn_enemies'):
                        for spawn_cfg in enemy.consume_spawn_enemies():
                            minions = self._spawn_enemies_from_data([spawn_cfg])
                            self.enemies.extend(minions)

            # ── Boss arena activation ──
            if (BOSSES_AVAILABLE and self._boss and self._boss.alive
                    and self.player and not self._boss_arena_triggered):
                # Trigger arena when player walks into boss zone
                arena_l = getattr(self, '_boss_arena_left', 0)
                if self.player.x >= arena_l - 100:
                    self._boss_arena_triggered = True
                    self._boss_arena_active = True
                    # Create invisible wall at left edge of arena
                    wall_y = 0
                    wall_h = self._get_level_height()
                    self._boss_arena_walls = [
                        SolidPlatform(arena_l - 20, wall_y, 20, wall_h, visible=False),
                    ]
                    self.platforms.extend(self._boss_arena_walls)
                    # Push player into arena if they're at the edge
                    if self.player.x < arena_l:
                        self.player.x = arena_l + 10
                    # Start boss music
                    if self.music:
                        self.music.set_zone(MusicZone.BOSS)
                        self.music.play_stinger('boss_entrance')
                    if self.sfx:
                        self.sfx.play('ground_pound', self.player.x)
                    if self.camera:
                        self.camera.shake(6)

            # Remove arena walls when boss is defeated
            if self._boss_arena_active and self._boss and not self._boss.alive:
                self._boss_arena_active = False
                for wall in self._boss_arena_walls:
                    if wall in self.platforms:
                        self.platforms.remove(wall)
                self._boss_arena_walls = []

            # ── Boss special effects ──
            if BOSSES_AVAILABLE and self._boss and self._boss.alive and self.player:
                # MamaSloth freeze request
                if hasattr(self._boss, 'player_freeze_request') and self._boss.player_freeze_request:
                    self._boss.player_freeze_request = False
                    self.player.freeze_timer = 120
                # MamaSloth spray cone
                if hasattr(self._boss, 'active_spray_cone') and self._boss.active_spray_cone:
                    cx, cy, angle, half_arc, spray_range, damage = self._boss.active_spray_cone
                    px = self.player.x + self.player.w / 2
                    py = self.player.y + self.player.h / 2
                    dx, dy = px - cx, py - cy
                    dist = math.hypot(dx, dy)
                    if dist < spray_range:
                        player_angle = math.atan2(dy, dx)
                        angle_diff = abs(player_angle - angle)
                        if angle_diff > math.pi:
                            angle_diff = 2 * math.pi - angle_diff
                        if angle_diff < half_arc:
                            self.player.take_damage(damage, self.difficulty)
                # Shockwave (TheLastGuard, Gracie, MamaSloth)
                if hasattr(self._boss, 'active_shockwave') and self._boss.active_shockwave:
                    sx, sy, sr, sd = self._boss.active_shockwave
                    px = self.player.x + self.player.w / 2
                    py = self.player.y + self.player.h / 2
                    if math.hypot(px - sx, py - sy) < sr:
                        self.player.take_damage(sd, self.difficulty)
                    self._boss.active_shockwave = None  # consume
                # Grab (TheLastGuard)
                if hasattr(self._boss, 'active_grab') and self._boss.active_grab:
                    grab_rect = self._boss.active_grab
                    player_rect = self.player.get_rect()
                    if player_rect.colliderect(grab_rect):
                        self.player.take_damage(15, self.difficulty)
                    self._boss.active_grab = None  # consume

            # ── Update enemy projectiles ──
            for proj in self.enemy_projectiles[:]:
                if not skip_enemies:
                    proj.update()
                if not proj.alive:
                    # If it's a glob, spawn puddle on landing
                    if hasattr(proj, 'create_puddle'):
                        self.hazards.append(proj.create_puddle())
                    self.enemy_projectiles.remove(proj)

            # ── Update hazards ──
            for hazard in self.hazards[:]:
                hazard.update()
                if not hazard.alive:
                    self.hazards.remove(hazard)

            # ── Update platforms (moving, crumbling) ──
            for plat in self.platforms:
                if hasattr(plat, 'update'):
                    plat.update(1)
                # Crumbling platform: detect player standing (use consistent margin)
                if hasattr(plat, 'stand_on') and self.player.on_ground:
                    pr = plat.get_rect()
                    player_rect = self.player.get_rect()
                    if (player_rect.bottom >= pr.top and player_rect.bottom <= pr.top + 12 and
                            player_rect.right > pr.left and player_rect.left < pr.right):
                        plat.stand_on()

            # ── Update interactables ──
            for obj in self.interactables:
                if hasattr(obj, 'update'):
                    obj.update(1)
                # Grant chest loot when opening animation finishes
                if hasattr(obj, 'grant_loot') and hasattr(obj, 'state'):
                    from game.world.interactables import CHEST_OPEN
                    if obj.state == CHEST_OPEN:
                        obj.grant_loot(self.player)

            # ── Combat system ──
            if self.combat:
                combat_projectiles = {
                    'player': self.player_projectiles,
                    'enemy': self.enemy_projectiles,
                    'hazards': self.hazards,
                }
                events = self.combat.check_hits(
                    self.player, self.enemies, combat_projectiles, self.difficulty
                )
                for evt_data in events:
                    event_type = evt_data.get('event', GameEvent.ENEMY_HIT)

                    # VFX and SFX for combat events
                    if event_type == GameEvent.ENEMY_HIT:
                        ex = evt_data.get('x', 0)
                        ey = evt_data.get('y', 0)
                        dmg = evt_data.get('damage', 0)
                        if self.sfx:
                            self.sfx.play('enemy_hit', ex)
                        if self.vfx:
                            self.vfx.trigger_hitstop(2)
                            self.vfx.trigger_flash('white')
                            self.camera.shake(2)
                        if self.hud:
                            self.hud.add_damage_number(ex, ey, dmg, is_player_damage=False)

                    elif event_type == GameEvent.ENEMY_DIED:
                        ex = evt_data.get('x', 0)
                        ey = evt_data.get('y', 0)
                        if self.sfx:
                            self.sfx.play('enemy_death', ex)
                        if self.vfx:
                            self.vfx.burst('death', ex, ey)
                            self.camera.shake(4)
                        if not self._first_kill_triggered:
                            self._first_kill_triggered = True
                            self.event_bus.emit(GameEvent.FIRST_ENEMY_KILL)
                        # Drop jello powder
                        if self.player:
                            self.player.jello_powder_count += 1
                        # 25% chance to drop water
                        import random as _rng
                        if self.player and _rng.random() < 0.25:
                            self.player.has_water = True

                    elif event_type == GameEvent.PLAYER_HIT:
                        dmg = evt_data.get('damage', 0)
                        if self.hud and dmg > 0:
                            self.hud.add_damage_number(
                                self.player.x + self.player.w / 2,
                                self.player.y,
                                dmg, is_player_damage=True
                            )

            # Check boss defeat
            if self._boss and not self._boss.alive:
                boss_type = getattr(self._boss, 'boss_type', None)
                self.event_bus.emit(GameEvent.BOSS_DEFEATED,
                                    boss_type=boss_type)
                if self.sfx:
                    self.sfx.play('enemy_death', self._boss.x)
                if self.vfx:
                    cx = self._boss.x + self._boss.w / 2
                    cy = self._boss.y + self._boss.h / 2
                    self.vfx.burst('death', cx, cy)
                    self.camera.shake(10)

                # Cleanser defeated → grant permanent speed upgrade
                if BOSSES_AVAILABLE and isinstance(self._boss, TheCleanser):
                    if self.player:
                        from game.engine.settings import CLEANSER_SPEED_REWARD
                        self.player.speed_multiplier = CLEANSER_SPEED_REWARD

                # The Last Guard defeated → credits
                if BOSSES_AVAILABLE and isinstance(self._boss, TheLastGuard):
                    self._boss = None
                    self.state = GameState.CREDITS
                    break

                self._boss = None

            # Remove dead enemies
            self.enemies = [e for e in self.enemies if e.alive]

            # ── Awareness / stealth ──
            if self.awareness:
                self.awareness.update(self.player, self.enemies, self.platforms)

            # ── Checkpoint auto-save at midpoint ──
            self._check_checkpoint()

            # ── Checkpoint text timer ──
            if self._checkpoint_text_timer > 0:
                self._checkpoint_text_timer -= 1

            # ── Check floor transitions ──
            self._check_floor_transitions()

            # ── VFX ──
            if self.vfx:
                self.vfx.update()

            # ── Camera ──
            self.camera.update(
                self.player.x + self.player.w / 2,
                self.player.y + self.player.h / 2,
                self.player.facing,
                self.joystick
            )

            # ── Narrator ──
            if self.narrator:
                self.narrator.update()

            # ── Crafting ──
            if self.crafting:
                self.crafting.update()

            # ── Secrets ──
            if self.secrets:
                self.secrets.update(self.player, self.current_floor,
                                    self.frame_count)

            # ── Music combat layers ──
            if self.music:
                # Add combat intensity when enemies are close
                close_enemies = sum(1 for e in self.enemies
                                    if e.alive and abs(e.x - self.player.x) < 300)
                if close_enemies > 0:
                    self.music.add_layer(min(close_enemies, 3))
                else:
                    self.music.remove_layer(0)
                self.music.update()

            # ── Draw ──
            cam_offset = self.camera.get_offset()
            self._draw_gameplay(cam_offset)
            pygame.display.flip()

            # ── Test mode: screenshots, logging, floor auto-advance ──
            if self.test_mode and self._test_run_dir:
                self._test_capture_and_log()

    # ── Test mode helpers ──

    def _test_capture_and_log(self):
        """Screenshot capture, state logging, and floor auto-advance for test mode."""
        now = _time.time()
        floor_dir = os.path.join(self._test_run_dir, f'floor_{self.current_floor:02d}')
        os.makedirs(floor_dir, exist_ok=True)

        # Screenshot every ~2 seconds
        if now - self._test_last_screenshot >= 2.0:
            shot_name = f'frame_{self.frame_count:06d}.png'
            self.capture_screenshot(os.path.join(floor_dir, shot_name))
            self._test_screenshot_count += 1
            self._test_last_screenshot = now

        # State log every 30 frames (~0.5s)
        if self._test_log_file and self.frame_count % 30 == 0:
            snapshot = self.get_state_snapshot()
            self._test_log_file.write(json.dumps(snapshot) + '\n')
            self._test_log_file.flush()

        # Stuck detection every 60 frames (~1s)
        if self.player and self.frame_count % 60 == 0:
            cur = (round(self.player.x, 0), round(self.player.y, 0))
            if cur == self._test_prev_pos:
                self._test_stuck_count += 1
                if self._test_stuck_count >= 5:
                    self.capture_screenshot(
                        os.path.join(floor_dir, f'stuck_{self.frame_count:06d}.png'))
                    self._test_screenshot_count += 1
                    # Unstick: jump and reverse
                    self.player.jump()
                    self.player.facing *= -1
                    self._test_stuck_count = 0
            else:
                self._test_stuck_count = 0
            self._test_prev_pos = cur

        # Floor auto-advance after duration expires
        if now - self._test_floor_start >= self.test_duration:
            next_floor = self.current_floor + 1
            if next_floor > self._test_max_floor:
                # Done — take final screenshot and quit
                self.capture_screenshot(os.path.join(floor_dir, 'end.png'))
                self._test_screenshot_count += 1
                self._quit()
            else:
                # Take end-of-floor screenshot, advance
                self.capture_screenshot(os.path.join(floor_dir, 'end.png'))
                self._test_screenshot_count += 1
                self.player.vx = 0
                self.player.vy = 0
                self._load_floor(next_floor)
                self.player.x = 100
                self.player.y = self._calc_spawn_y()
                self._test_floor_start = now

    def _test_ai_get_keys(self):
        """Return a fake key state dict for AI-driven movement."""
        class FakeKeys:
            """Mimics pygame.key.get_pressed() with AI-chosen keys."""
            def __init__(self):
                self._pressed = set()
            def __getitem__(self, key):
                return key in self._pressed

        keys = FakeKeys()

        if not self.player:
            return keys

        # Check if there's a door/transition to walk toward
        target_x = None
        if self.level_manager:
            transitions = self.level_manager.get_transitions()
            if transitions:
                # Walk toward nearest transition
                nearest = min(transitions, key=lambda t: abs(t['x'] - self.player.x))
                target_x = nearest['x']

        if target_x is not None:
            # Walk toward the transition zone
            if self.player.x < target_x - 20:
                keys._pressed.add(pygame.K_RIGHT)
            elif self.player.x > target_x + 20:
                keys._pressed.add(pygame.K_LEFT)
            else:
                # On top of transition — interact to trigger it
                keys._pressed.add(pygame.K_RIGHT)
        else:
            # No transitions — default walk right, bounce at edges
            level_w = self._get_level_width()
            if self.player.x > level_w - 100:
                keys._pressed.add(pygame.K_LEFT)
            elif self.player.x < 10:
                keys._pressed.add(pygame.K_RIGHT)
            else:
                keys._pressed.add(pygame.K_RIGHT)

        return keys

    def _test_ai_actions(self):
        """Trigger discrete actions (jump, shoot, interact) on schedule."""
        if not self.player:
            return

        tick = self._test_ai_tick

        # Jump every ~45 frames, or when near a wall edge
        if tick % 45 == 0:
            self.player.jump()

        # Shoot when enemies are within 250px horizontally
        if tick % 15 == 0:
            for e in self.enemies:
                if e.alive and abs(e.x - self.player.x) < 250:
                    proj = self.player.shoot()
                    if proj:
                        self.player_projectiles.append(proj)
                    break

        # Try interact every ~60 frames (doors, pickups)
        if tick % 60 == 0:
            self._do_interact()

        # Ground pound occasionally when airborne
        if tick % 120 == 0 and not self.player.on_ground:
            self.player.start_ground_pound()

    _FLOOR_NAMES = {
        1: "Storage Rooms", 2: "Deeper Storage", 3: "Lower Cellars",
        4: "Dining Halls", 5: "Living Quarters", 6: "Kitchens",
        7: "Ornate Chambers", 8: "Transition Zone", 9: "Parkour Zone I",
        10: "Parkour Zone II", 11: "Parkour Zone III", 12: "Gauntlet Start",
        13: "Gauntlet Mid", 14: "Gauntlet End", 15: "The Top",
    }

    def _check_checkpoint(self):
        """Auto-save checkpoint at midpoint of each level."""
        from game.engine.settings import DIFFICULTY_SETTINGS
        if not DIFFICULTY_SETTINGS[self.difficulty].get('checkpoint', True):
            return  # no checkpoints in earthquake/hard mode
        if not self.player:
            return
        level_w = self._get_level_width()
        mid_x = level_w / 2
        # Save checkpoint when player crosses midpoint (once per floor)
        if (self.player.x >= mid_x and
                self._checkpoint_floor != self.current_floor):
            self._checkpoint_floor = self.current_floor
            self._checkpoint = {
                'floor': self.current_floor,
                'x': self.player.x,
                'y': self.player.y,
                'health': self.player.health,
                'jello_powder_count': self.player.jello_powder_count,
                'cooked_jelly_count': getattr(self.player, 'cooked_jelly_count', 0),
                'has_water': self.player.has_water,
            }
            self.event_bus.emit(GameEvent.CHECKPOINT_REACHED, player=self.player)
            if self.sfx:
                self.sfx.play('collect', self.player.x)
            self._checkpoint_text_timer = 90

    def _respawn_at_checkpoint(self):
        """Respawn the player at the last checkpoint."""
        if not self._checkpoint or not self.player:
            return False
        cp = self._checkpoint
        # Reload the floor if needed
        if cp['floor'] != self.current_floor:
            self._load_floor(cp['floor'])
        self.player.health = cp['health']
        self.player.x = cp['x']
        self.player.y = cp['y']
        self.player.jello_powder_count = cp['jello_powder_count']
        self.player.cooked_jelly_count = cp.get('cooked_jelly_count', 0)
        self.player.has_water = cp['has_water']
        self.player.vx = 0
        self.player.vy = 0
        self.player.invuln_timer = 60  # brief invuln after respawn
        self.player_projectiles.clear()
        self.enemy_projectiles.clear()
        self.hazards.clear()
        return True

    def _check_floor_transitions(self):
        """Check if player reached an elevator/transition to next floor."""
        if not self.level_manager:
            return

        # Guard: don't transition during dodge, hitstop, or death
        if self.player.dodge_timer > 0 or self.player.ground_pounding:
            return

        # Transition cooldown (prevent instant re-triggers)
        if not hasattr(self, '_transition_cooldown'):
            self._transition_cooldown = 0
        if self._transition_cooldown > 0:
            self._transition_cooldown -= 1
            return

        transitions = self.level_manager.get_transitions()
        player_rect = self.player.get_rect()
        for t in transitions:
            t_rect = pygame.Rect(t['x'], t['y'], t.get('w', 80), t.get('h', 150))
            if player_rect.colliderect(t_rect):
                target = t.get('target_floor', self.current_floor + 1)
                if target != self.current_floor:
                    self.player.vx = 0
                    self.player.vy = 0
                    # Start the floor transition effect
                    self._floor_transition_active = True
                    self._floor_transition_frame = 0
                    self._floor_transition_target = target
                    self._floor_transition_name = self._FLOOR_NAMES.get(target, f"Floor {target}")
                    self._transition_cooldown = 30
                    break

    def _do_floor_transition(self):
        """Floor transition: fade out → floor name → fade in."""
        FADE_OUT, HOLD, FADE_IN = 30, 60, 30
        f = self._floor_transition_frame
        self._floor_transition_frame += 1

        if f < FADE_OUT:
            cam_offset = self.camera.get_offset()
            self._draw_gameplay(cam_offset)
            alpha = int(255 * (f / FADE_OUT))
            fade = pygame.Surface((SCREEN_W, SCREEN_H))
            fade.fill((0, 0, 0))
            fade.set_alpha(alpha)
            self.screen.blit(fade, (0, 0))
            pygame.display.flip()
            return True
        if f == FADE_OUT:
            target = self._floor_transition_target
            self._load_floor(target)
            self.player.x = 100
            self.player.y = self._calc_spawn_y()
            self.event_bus.emit(GameEvent.FLOOR_CHANGE, floor=target, player=self.player)
        if f < FADE_OUT + HOLD:
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 64)
            font_sub = pygame.font.Font(None, 32)
            txt = font.render(f"Floor {self._floor_transition_target}", True, (255, 255, 255))
            name = font_sub.render(self._floor_transition_name, True, TORCH_AMBER)
            local_f = f - FADE_OUT
            text_alpha = min(255, int(255 * min(local_f / 15, (HOLD - local_f) / 15, 1.0)))
            txt.set_alpha(text_alpha)
            name.set_alpha(text_alpha)
            self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, SCREEN_H // 2 - 30))
            self.screen.blit(name, (SCREEN_W // 2 - name.get_width() // 2, SCREEN_H // 2 + 30))
            pygame.display.flip()
            return True
        if f < FADE_OUT + HOLD + FADE_IN:
            cam_offset = self.camera.get_offset()
            self._draw_gameplay(cam_offset)
            alpha = int(255 * (1.0 - (f - FADE_OUT - HOLD) / FADE_IN))
            fade = pygame.Surface((SCREEN_W, SCREEN_H))
            fade.fill((0, 0, 0))
            fade.set_alpha(alpha)
            self.screen.blit(fade, (0, 0))
            pygame.display.flip()
            return True
        self._floor_transition_active = False
        return False

    def _do_boss_intro(self):
        """Boss intro: camera pan to boss → name text → pan back."""
        PAN_TO, HOLD, PAN_BACK = 30, 60, 30
        TOTAL = PAN_TO + HOLD + PAN_BACK
        f = self._boss_intro_frame
        self._boss_intro_frame += 1

        boss_x, boss_y = self._boss_intro_boss_pos
        px = self.player.x + self.player.w / 2
        py = self.player.y + self.player.h / 2

        if f < PAN_TO:
            t = f / PAN_TO
            cx = px + (boss_x - px) * t
            cy = py + (boss_y - py) * t
        elif f < PAN_TO + HOLD:
            cx, cy = boss_x, boss_y
        elif f < TOTAL:
            t = (f - PAN_TO - HOLD) / PAN_BACK
            cx = boss_x + (px - boss_x) * t
            cy = boss_y + (py - boss_y) * t
        else:
            self._boss_intro_active = False
            # Sync: end the boss's own internal intro too so it attacks immediately
            if self._boss and hasattr(self._boss, 'intro_active'):
                self._boss.intro_active = False
                self._boss.intro_timer = 0
            return False

        if hasattr(self.camera, 'reset'):
            self.camera.reset(cx, cy)
        cam_offset = self.camera.get_offset()
        self._draw_gameplay(cam_offset)

        if PAN_TO <= f < PAN_TO + HOLD:
            font = pygame.font.Font(None, 64)
            name_surf = font.render(self._boss_intro_name, True, (220, 50, 50))
            local_f = f - PAN_TO
            if local_f < 15:
                name_surf.set_alpha(int(255 * (local_f / 15)))
            elif local_f > HOLD - 15:
                name_surf.set_alpha(int(255 * ((HOLD - local_f) / 15)))
            self.screen.blit(name_surf, (SCREEN_W // 2 - name_surf.get_width() // 2, SCREEN_H // 3))
            sub = pygame.font.Font(None, 28).render("Prepare yourself...", True, TORCH_AMBER)
            self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 3 + 50))

        pygame.display.flip()
        return True

    def _draw_gameplay(self, cam_offset):
        """Draw all gameplay elements."""
        # Background
        self._draw_background(self.current_floor)

        # Platforms
        for plat in self.platforms:
            if hasattr(plat, 'draw'):
                plat.draw(self.screen, cam_offset)

        # Interactables
        for obj in self.interactables:
            if hasattr(obj, 'draw'):
                obj.draw(self.screen, cam_offset)

        # Hazards (trails, puddles — behind enemies)
        for hazard in self.hazards:
            if hasattr(hazard, 'draw'):
                hazard.draw(self.screen, cam_offset)

        # Enemies
        for enemy in self.enemies:
            if hasattr(enemy, 'draw'):
                enemy.draw(self.screen, cam_offset)

        # Awareness indicators (? and !)
        if self.awareness:
            self.awareness.draw_indicators(self.screen, self.enemies, cam_offset)

        # Enemy projectiles
        for proj in self.enemy_projectiles:
            if hasattr(proj, 'draw'):
                proj.draw(self.screen, cam_offset)

        # Player projectiles
        for proj in self.player_projectiles:
            proj.draw(self.screen, cam_offset)

        # Player
        if self.player:
            self.player.draw(self.screen, cam_offset)

        # VFX (on top of everything in world space)
        if self.vfx:
            self.vfx.draw(self.screen, cam_offset)

        # Secrets (wall splats, glitch effect, golden border)
        if self.secrets:
            self.secrets.draw(self.screen, cam_offset)

        # Boss health bar (screen-space)
        if self._boss and self._boss.alive:
            self._boss.draw_boss_health_bar(self.screen)

        # "Press Y to interact" prompt near interactables
        if self.player:
            player_rect = self.player.get_rect().inflate(30, 30)
            for obj in self.interactables:
                if hasattr(obj, 'get_rect') and player_rect.colliderect(obj.get_rect()):
                    # Don't show for already-open chests or sun zones
                    if hasattr(obj, 'state'):
                        from game.world.interactables import CHEST_OPEN
                        if obj.state == CHEST_OPEN:
                            continue
                    if getattr(obj, 'interactable_type', '') == 'sun_zone':
                        continue
                    ox, oy = cam_offset
                    prompt_x = int(obj.x + obj.w / 2 + ox)
                    prompt_y = int(obj.y + oy - 20)
                    prompt_font = pygame.font.Font(None, 22)
                    prompt_surf = prompt_font.render("Press Y to interact", True, (255, 255, 200))
                    self.screen.blit(prompt_surf, (prompt_x - prompt_surf.get_width() // 2, prompt_y))
                    break  # only show one prompt

        # HUD (screen-space, no camera offset)
        if self.hud and self.player:
            self.hud.draw(self.screen, self.player, self.current_floor,
                          self.run_count, self.difficulty, cam_offset,
                          self.frame_count)

        # Narrator
        if self.narrator:
            self.narrator.draw(self.screen)

        # Checkpoint text ("CHECKPOINT" fades in then out)
        if self._checkpoint_text_timer > 0:
            cp_font = pygame.font.Font(None, 42)
            t = self._checkpoint_text_timer
            # Fade in during first 15 frames, fade out during last 30
            if t > 75:
                alpha = int(255 * (90 - t) / 15)
            elif t < 30:
                alpha = int(255 * t / 30)
            else:
                alpha = 255
            alpha = max(0, min(255, alpha))
            cp_surf = cp_font.render("CHECKPOINT", True, (180, 255, 180))
            cp_surf.set_alpha(alpha)
            self.screen.blit(cp_surf,
                             (SCREEN_W // 2 - cp_surf.get_width() // 2,
                              SCREEN_H // 2 - 60))

    def _draw_background(self, floor_num):
        """Draw castle background for current floor (cached)."""
        if self._bg_cache_floor != floor_num:
            self._bg_surface = pygame.Surface((SCREEN_W, SCREEN_H))
            palette = FLOOR_PALETTES.get(floor_num, FLOOR_PALETTES[1])
            deep, warm, floor_color, accent = palette
            for y in range(SCREEN_H):
                ratio = y / SCREEN_H
                r = int(deep[0] + (warm[0] - deep[0]) * ratio * 0.5)
                g = int(deep[1] + (warm[1] - deep[1]) * ratio * 0.5)
                b = int(deep[2] + (warm[2] - deep[2]) * ratio * 0.5)
                pygame.draw.line(self._bg_surface, (r, g, b), (0, y), (SCREEN_W, y))

            # Ceiling
            ceiling_color = (
                max(0, deep[0] - 5),
                max(0, deep[1] - 5),
                max(0, deep[2] - 5),
            )
            pygame.draw.rect(self._bg_surface, ceiling_color, (0, 0, SCREEN_W, 30))
            # Ceiling trim
            pygame.draw.line(self._bg_surface, accent, (0, 30), (SCREEN_W, 30), 2)

            # Windows with light beams
            import random as rng
            rng.seed(floor_num * 500)
            for wx in range(150, SCREEN_W, 350):
                wx += rng.randint(-30, 30)
                # Window frame
                win_w, win_h = 50, 70
                win_y = 35
                frame_color = (min(255, warm[0] + 15), min(255, warm[1] + 15),
                               min(255, warm[2] + 15))
                pygame.draw.rect(self._bg_surface, frame_color,
                                 (wx - 2, win_y - 2, win_w + 4, win_h + 4))
                # Window pane — pale sky blue
                pygame.draw.rect(self._bg_surface, (160, 190, 220),
                                 (wx, win_y, win_w, win_h))
                # Cross bars
                pygame.draw.line(self._bg_surface, frame_color,
                                 (wx + win_w // 2, win_y), (wx + win_w // 2, win_y + win_h), 2)
                pygame.draw.line(self._bg_surface, frame_color,
                                 (wx, win_y + win_h // 2), (wx + win_w, win_y + win_h // 2), 2)
                # Light beam (translucent trapezoid)
                beam = pygame.Surface((win_w + 60, 400), pygame.SRCALPHA)
                beam_points = [(10, 0), (win_w - 10, 0),
                               (win_w + 60, 400), (-30, 400)]
                pygame.draw.polygon(beam, (255, 245, 220, 12), beam_points)
                self._bg_surface.blit(beam, (wx - 15, win_y + win_h))

            # Stone wall pattern (static, no random per-frame)
            rng.seed(floor_num * 1000)  # deterministic per floor
            for row in range(30, 500, 40):
                offset = 20 if (row // 40) % 2 == 0 else 0
                for col in range(-40 + offset, SCREEN_W + 40, 80):
                    brick_color = (
                        min(255, warm[0] + rng.randint(-3, 3)),
                        min(255, warm[1] + rng.randint(-3, 3)),
                        min(255, warm[2] + rng.randint(-3, 3)),
                    )
                    pygame.draw.rect(self._bg_surface, brick_color, (col, row, 78, 38))
                    pygame.draw.rect(self._bg_surface, deep, (col, row, 78, 38), 1)

            # Floor tiles
            pygame.draw.rect(self._bg_surface, floor_color,
                             (0, 500, SCREEN_W, SCREEN_H - 500))
            pygame.draw.line(self._bg_surface, accent,
                             (0, 500), (SCREEN_W, 500), 2)

            # Decorative sand mounds on the floor
            rng.seed(floor_num * 2000)
            for _ in range(rng.randint(3, 7)):
                mx = rng.randint(50, SCREEN_W - 50)
                mw = rng.randint(30, 60)
                mh = rng.randint(6, 14)
                sand_color = (
                    min(255, floor_color[0] + rng.randint(5, 20)),
                    min(255, floor_color[1] + rng.randint(5, 15)),
                    min(255, floor_color[2] + rng.randint(0, 10)),
                )
                pygame.draw.ellipse(self._bg_surface, sand_color,
                                    (mx - mw // 2, 500 - mh, mw, mh * 2))
            rng.seed()  # reset

            self._bg_cache_floor = floor_num

        self.screen.blit(self._bg_surface, (0, 0))

        # Animated torch glow (cached surface, vary alpha per frame)
        if self._torch_glow_cache is None:
            self._torch_glow_cache = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(self._torch_glow_cache,
                               (TORCH_AMBER[0], TORCH_AMBER[1], TORCH_AMBER[2], 24),
                               (50, 50), 50)

        t = pygame.time.get_ticks()
        torches = [200, 500, 800, 1100]
        for tx in torches:
            flame_h = 12 + math.sin(t * 0.008 + tx) * 4
            glow_a = int(18 + math.sin(t * 0.005 + tx * 0.3) * 6)
            self._torch_glow_cache.set_alpha(glow_a * 255 // 24)
            self.screen.blit(self._torch_glow_cache, (tx - 50, 320))
            # Flame
            points = [(tx - 4, 360), (tx, int(360 - flame_h)), (tx + 4, 360)]
            pygame.draw.polygon(self.screen, TORCH_AMBER, points)

    # ── Input handlers ──

    def _handle_key_down(self, key):
        if not self.player:
            return
        if key == KEY_JUMP:
            self.player.jump()
        elif key == KEY_SHOOT:
            proj = self.player.shoot()
            if proj:
                self.player_projectiles.append(proj)
        elif key == KEY_EAT:
            self.player.eat_jello_powder()
        elif key == KEY_INTERACT:
            self._do_interact()
        elif key == KEY_SPLIT:
            if self.player.is_split:
                self.player.try_unsplit(self.platforms)
            else:
                self.player.split()
        elif key == KEY_DODGE:
            self.player.perfect_dodge()
        elif key == KEY_SWITCH_SPLIT:
            self.player.switch_split_piece()
        elif key == KEY_PAUSE:
            self.state = GameState.PAUSE
        elif key == KEY_INVENTORY:
            self._open_inventory()
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.player.start_ground_pound()

    def _handle_button_down(self, button):
        if not self.player:
            return
        if button == CTRL_A:
            self.player.jump()
        elif button == CTRL_B:
            proj = self.player.shoot()
            if proj:
                self.player_projectiles.append(proj)
        elif button == CTRL_X:
            self.player.eat_jello_powder()
        elif button == CTRL_Y:
            self._do_interact()
        elif button == CTRL_ZL:
            if self.player.is_split:
                self.player.try_unsplit(self.platforms)
            else:
                self.player.split()
        elif button == CTRL_ZR:
            self.player.perfect_dodge()
        elif button == CTRL_L:
            self.player.switch_split_piece(direction=1)
        elif button == CTRL_R:
            self.player.switch_split_piece(direction=-1)
        elif button == CTRL_PLUS:
            self.state = GameState.PAUSE
        elif button == CTRL_MINUS:
            self._open_inventory()

    def _do_interact(self):
        """Context-sensitive interact."""
        if not self.player:
            return
        player_rect = self.player.get_rect().inflate(30, 30)
        for obj in self.interactables:
            if hasattr(obj, 'get_rect') and player_rect.colliderect(obj.get_rect()):
                if hasattr(obj, 'interact'):
                    obj.interact(self.player, self.crafting)
                    if self.sfx:
                        self.sfx.play('collect', self.player.x)
                    break
        self.player.interact()

    def _open_inventory(self):
        """Open inventory screen (pauses gameplay)."""
        if not self.player:
            return
        try:
            from game.ui.inventory import run_inventory
            run_inventory(self.screen, self.clock, self.player,
                          self.crafting, self.joystick)
        except Exception:
            pass  # graceful fallback — no inventory screen available

    # ── Screen transitions ──

    def _run_death(self):
        if self.test_mode:
            # Auto-respawn on current floor in test mode (don't restart from floor 1)
            self.state = GameState.GAMEPLAY
            self.player.health = self.player.max_health
            self.player.vx = 0
            self.player.vy = 0
            self.player.x = 100
            self.player.y = self._calc_spawn_y()
            self.player_projectiles.clear()
            self.enemy_projectiles.clear()
            self.hazards.clear()
            # Remove boss arena walls so player can re-enter after respawn
            if self._boss_arena_active:
                for wall in self._boss_arena_walls:
                    if wall in self.platforms:
                        self.platforms.remove(wall)
                self._boss_arena_walls = []
                self._boss_arena_active = False
                self._boss_arena_triggered = False
            return

        try:
            from game.ui.death_screen import run_death_screen
            floor_name = self._FLOOR_NAMES.get(self.current_floor, f"Floor {self.current_floor}")
            has_cp = self._checkpoint is not None and self._checkpoint_floor == self.current_floor
            result = run_death_screen(self.screen, self.clock, self.run_count, self.joystick,
                                      floor_num=self.current_floor, floor_name=floor_name,
                                      has_checkpoint=has_cp)
        except Exception:
            result = self._fallback_death()
        if result == "retry":
            self.state = GameState.GAMEPLAY
            # Try checkpoint respawn first, otherwise full restart
            if self._checkpoint and self._respawn_at_checkpoint():
                pass  # respawned at checkpoint
            else:
                self._start_gameplay()
        elif result == "restart":
            # Full restart from floor 1 (no checkpoint)
            self._checkpoint = None
            self._checkpoint_floor = -1
            self.state = GameState.GAMEPLAY
            self._start_gameplay()
        else:
            self.state = GameState.TITLE

    def _run_pause(self):
        try:
            from game.ui.pause_menu import run_pause_menu
            result = run_pause_menu(self.screen, self.clock, self.joystick)
        except Exception:
            result = self._fallback_pause()
        if result == "resume":
            self.state = GameState.GAMEPLAY
        else:
            self.state = GameState.TITLE

    def _run_credits(self):
        try:
            from game.ui.credits import run_credits
            run_credits(self.screen, self.clock, self.joystick)
        except Exception:
            pass
        self.state = GameState.TITLE

    # ── Fallback screens ──

    def _fallback_title(self):
        font = pygame.font.Font(None, 72)
        prompt_font = pygame.font.Font(None, 28)
        alpha = 0
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_SPACE and alpha >= 250:
                        return Difficulty.NORMAL
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == CTRL_A and alpha >= 250:
                        return Difficulty.NORMAL
                    if event.button == CTRL_PLUS:
                        return None
                if event.type == pygame.JOYDEVICEADDED:
                    self._init_controller()
            alpha = min(255, alpha + 3)
            self.screen.fill((26, 26, 46))
            title = font.render("S P L I T", True, JELLO_GREEN)
            self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 3)))
            if alpha >= 250:
                t = pygame.time.get_ticks()
                pa = int(128 + math.sin(t * 0.005) * 127)
                prompt = prompt_font.render("Press SPACE or A to play", True, TORCH_GLOW)
                prompt.set_alpha(pa)
                self.screen.blit(prompt, prompt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 60)))
            pygame.display.flip()

    def _fallback_death(self):
        font = pygame.font.Font(None, 48)
        small = pygame.font.Font(None, 24)
        timer = 0
        while True:
            self.clock.tick(FPS)
            timer += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.KEYDOWN and timer > 30:
                    if event.key == pygame.K_SPACE:
                        return "retry"
                    if event.key == pygame.K_ESCAPE:
                        return "quit"
                if event.type == pygame.JOYBUTTONDOWN and timer > 30:
                    if event.button == CTRL_A:
                        return "retry"
                    if event.button == CTRL_PLUS:
                        return "quit"
            self.screen.fill((30, 10, 10))
            self.screen.blit(font.render("You Dissolved", True, (220, 60, 60)),
                             font.render("You Dissolved", True, (220, 60, 60)).get_rect(
                                 center=(SCREEN_W // 2, SCREEN_H // 3)))
            self.screen.blit(small.render(f"Run #{self.run_count}", True, (160, 140, 120)),
                             small.render(f"Run #{self.run_count}", True, (160, 140, 120)).get_rect(
                                 center=(SCREEN_W // 2, SCREEN_H // 2)))
            if timer > 30:
                hint = small.render("SPACE/A = Try Again   ESC/Plus = Quit", True, (120, 100, 80))
                self.screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H * 2 // 3)))
            pygame.display.flip()

    def _fallback_pause(self):
        font = pygame.font.Font(None, 48)
        small = pygame.font.Font(None, 24)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == KEY_PAUSE:
                        return "resume"
                    if event.key == pygame.K_q:
                        return "quit"
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == CTRL_PLUS:
                        return "resume"
                    if event.button == CTRL_A:
                        return "resume"
            self.screen.blit(overlay, (0, 0))
            self.screen.blit(font.render("PAUSED", True, TORCH_GLOW),
                             font.render("PAUSED", True, TORCH_GLOW).get_rect(
                                 center=(SCREEN_W // 2, SCREEN_H // 3)))
            self.screen.blit(small.render("ESC/Plus = Resume   Q = Quit", True, (160, 140, 120)),
                             small.render("ESC/Plus = Resume   Q = Quit", True, (160, 140, 120)).get_rect(
                                 center=(SCREEN_W // 2, SCREEN_H // 2)))
            pygame.display.flip()

    def _quit(self):
        pygame.quit()
        sys.exit()


class SolidPlatform:
    """Simple platform when LevelManager isn't available."""
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf, camera_offset=(0, 0)):
        ox, oy = camera_offset
        r = pygame.Rect(self.x + ox, self.y + oy, self.w, self.h)
        if r.right < 0 or r.left > SCREEN_W or r.bottom < 0 or r.top > SCREEN_H:
            return
        pygame.draw.rect(surf, (45, 45, 68), r)
        pygame.draw.rect(surf, (55, 55, 80), (r.x, r.y, r.w, 3))
        pygame.draw.rect(surf, (26, 26, 46), r, 1)


def main():
    parser = argparse.ArgumentParser(description="SPLIT — A Jello Cube Adventure")
    parser.add_argument('--test-mode', action='store_true',
                        help='Run in automated test mode (AI plays the game)')
    parser.add_argument('--floor', type=int, default=1,
                        help='Starting floor in test mode (default: 1)')
    parser.add_argument('--duration', type=int, default=30,
                        help='Seconds per floor in test mode (default: 30)')
    args, _ = parser.parse_known_args()

    game = Game(
        test_mode=args.test_mode,
        test_floor=args.floor,
        test_duration=args.duration,
    )
    game.run()


if __name__ == "__main__":
    main()
