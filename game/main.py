"""
SPLIT — Main Game
State machine: TITLE → GAMEPLAY → DEATH → CREDITS
All systems initialized and wired here.
"""
import pygame
import sys
import os
import math

# Ensure game package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.engine.settings import (
    SCREEN_W, SCREEN_H, FPS, GameState, Difficulty, GameEvent, EventBus, MusicZone,
    CTRL_A, CTRL_B, CTRL_X, CTRL_Y, CTRL_L, CTRL_ZL, CTRL_ZR,
    CTRL_MINUS, CTRL_PLUS, AXIS_LY, STICK_DEADZONE, FLOOR_PALETTES,
    KEY_JUMP, KEY_SHOOT, KEY_EAT, KEY_INTERACT, KEY_SPLIT, KEY_DODGE,
    KEY_SWITCH_SPLIT, KEY_INVENTORY, KEY_PAUSE,
    JELLO_GREEN, TORCH_AMBER, TORCH_GLOW,
)
from game.engine.camera import Camera
from game.entities.player import JelloCube, JelloProjectile

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

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("SPLIT")
        self.clock = pygame.time.Clock()

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

    def _init_controller(self):
        """Initialize first available controller."""
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
            except Exception:
                self.joystick = None

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
                enemies.append(SmallSanitizerBottle(x, y, patrol_points))
            elif etype == 'sanitizer_warrior':
                enemies.append(SanitizerWarrior(x, y, patrol_points))
            elif etype == 'jelly_archer':
                enemies.append(JellyArcher(x, y, patrol_points))
        return enemies

    def _start_gameplay(self):
        """Reset for a new gameplay session."""
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

        # Load floor
        self._load_floor(self.current_floor)

        # Music
        if self.music:
            self.music.set_zone(MusicZone.FLOORS_1_4)

    def _load_floor(self, floor_num):
        """Load a floor from level data and spawn entities."""
        self.current_floor = floor_num
        self.enemy_projectiles = []
        self.hazards = []

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

        # Spawn boss on boss floors
        if BOSSES_AVAILABLE:
            level_w = self._get_level_width()
            arena_r = max(1180, level_w - 100)
            boss = None
            if floor_num == 4:
                boss = BigBottle(level_w // 2, 400, arena_left=100, arena_right=arena_r)
            elif floor_num == 8:
                boss = TheCleanser(level_w // 2, 400, arena_left=100, arena_right=arena_r)
            elif floor_num == 15:
                boss = TheLastGuard(level_w // 2, 400, arena_left=100, arena_right=arena_r)
            if boss:
                self._boss = boss
                self.enemies.append(boss)
                if self.music:
                    self.music.set_zone(MusicZone.BOSS)
                    self.music.play_stinger('boss_entrance')
                if not self._first_boss_triggered:
                    self._first_boss_triggered = True
                    self.event_bus.emit(GameEvent.FIRST_BOSS_ENCOUNTER)

        # Camera bounds
        level_w = self._get_level_width()
        level_h = self._get_level_height()
        self.camera.set_bounds(0, 0, max(SCREEN_W, level_w), max(SCREEN_H, level_h))
        if self.player:
            self.camera.reset(self.player.x, self.player.y)

        # Update music zone based on floor
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

        # Stinger for floor change
        if self.music and floor_num > 1:
            self.music.play_stinger('floor_change')

        # Clear bg cache
        self._bg_cache_floor = -1

    def _setup_fallback_level(self):
        """Basic level when LevelManager isn't available."""
        self.platforms = [
            FallbackPlatform(0, 500, 2560, 220),
            FallbackPlatform(180, 400, 120, 16),
            FallbackPlatform(380, 330, 140, 16),
            FallbackPlatform(560, 400, 100, 16),
            FallbackPlatform(280, 240, 100, 16),
            FallbackPlatform(500, 180, 130, 16),
            FallbackPlatform(750, 350, 120, 16),
            FallbackPlatform(950, 280, 140, 16),
            FallbackPlatform(1150, 400, 100, 16),
            FallbackPlatform(1350, 320, 130, 16),
            FallbackPlatform(1550, 250, 100, 16),
            FallbackPlatform(1750, 400, 120, 16),
            FallbackPlatform(1950, 350, 140, 16),
            FallbackPlatform(2150, 280, 100, 16),
            FallbackPlatform(2350, 400, 160, 16),
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
        """Title screen."""
        try:
            from game.ui.title_screen import run_title_screen
            result = run_title_screen(self.screen, self.clock, self.joystick)
            if result is None:
                self._quit()
            self.difficulty = result
        except Exception:
            result = self._fallback_title()
            if result is None:
                self._quit()
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
            self.player.update(keys, self.platforms, self.joystick)

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
            from game.entities.enemies import SmallSanitizerBottle, SanitizerWarrior, JellyArcher
            for enemy in self.enemies[:]:
                if not enemy.alive:
                    continue
                enemy.update(self.player)

                # Collect enemy-spawned projectiles/hazards
                if isinstance(enemy, SmallSanitizerBottle):
                    if enemy.should_spawn_trail():
                        self.hazards.append(enemy.spawn_trail())
                elif isinstance(enemy, SanitizerWarrior):
                    # Get ground_y from nearest ground platform
                    ground_y = 500
                    for plat in self.platforms:
                        pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(0, 0, 0, 0)
                        if pr.y > enemy.y and pr.h > 50:
                            ground_y = pr.y
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

            # ── Boss special effects (MamaSloth spray cone, freeze) ──
            if BOSSES_AVAILABLE and self._boss and self._boss.alive:
                if hasattr(self._boss, 'player_freeze_request') and self._boss.player_freeze_request:
                    self._boss.player_freeze_request = False
                    # Freeze player for 2 seconds (120 frames)
                    if self.player and hasattr(self.player, 'freeze_timer'):
                        self.player.freeze_timer = 120
                if hasattr(self._boss, 'active_spray_cone') and self._boss.active_spray_cone:
                    cx, cy, angle, half_arc, spray_range, damage = self._boss.active_spray_cone
                    # Check if player is in the cone
                    if self.player:
                        px = self.player.x + self.player.w / 2
                        py = self.player.y + self.player.h / 2
                        dx = px - cx
                        dy = py - cy
                        dist = math.hypot(dx, dy)
                        if dist < spray_range:
                            player_angle = math.atan2(dy, dx)
                            angle_diff = abs(player_angle - angle)
                            if angle_diff > math.pi:
                                angle_diff = 2 * math.pi - angle_diff
                            if angle_diff < half_arc:
                                self.player.take_damage(damage, self.difficulty)

            # ── Update enemy projectiles ──
            for proj in self.enemy_projectiles[:]:
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
                # Crumbling platform: detect player standing
                if hasattr(plat, 'stand_on') and self.player.on_ground:
                    pr = plat.get_rect()
                    player_rect = self.player.get_rect()
                    if (player_rect.bottom >= pr.top and player_rect.bottom <= pr.top + 8 and
                            player_rect.right > pr.left and player_rect.left < pr.right):
                        plat.stand_on()

            # ── Update interactables ──
            for obj in self.interactables:
                if hasattr(obj, 'update'):
                    obj.update(1)

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

    def _check_floor_transitions(self):
        """Check if player reached an elevator/transition to next floor."""
        if not self.level_manager:
            return
        transitions = self.level_manager.get_transitions()
        player_rect = self.player.get_rect()
        for t in transitions:
            t_rect = pygame.Rect(t['x'], t['y'], t.get('w', 80), t.get('h', 150))
            if player_rect.colliderect(t_rect):
                target = t.get('target_floor', self.current_floor + 1)
                if target != self.current_floor:
                    # Transition! Place player at start of new floor
                    self.player.x = 100
                    self.player.y = 400
                    self.player.vx = 0
                    self.player.vy = 0
                    self._load_floor(target)
                    self.event_bus.emit(GameEvent.FLOOR_CHANGE,
                                        floor=target, player=self.player)
                    break

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

        # HUD (screen-space, no camera offset)
        if self.hud and self.player:
            self.hud.draw(self.screen, self.player, self.current_floor,
                          self.run_count, self.difficulty, cam_offset,
                          self.frame_count)

        # Narrator
        if self.narrator:
            self.narrator.draw(self.screen)

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

            # Stone wall pattern (static, no random per-frame)
            import random as rng
            rng.seed(floor_num * 1000)  # deterministic per floor
            for row in range(0, 500, 40):
                offset = 20 if (row // 40) % 2 == 0 else 0
                for col in range(-40 + offset, SCREEN_W + 40, 80):
                    brick_color = (
                        min(255, warm[0] + rng.randint(-3, 3)),
                        min(255, warm[1] + rng.randint(-3, 3)),
                        min(255, warm[2] + rng.randint(-3, 3)),
                    )
                    pygame.draw.rect(self._bg_surface, brick_color, (col, row, 78, 38))
                    pygame.draw.rect(self._bg_surface, deep, (col, row, 78, 38), 1)
            rng.seed()  # reset

            # Floor tiles
            pygame.draw.rect(self._bg_surface, floor_color,
                             (0, 500, SCREEN_W, SCREEN_H - 500))
            pygame.draw.line(self._bg_surface, accent,
                             (0, 500), (SCREEN_W, 500), 2)

            self._bg_cache_floor = floor_num

        self.screen.blit(self._bg_surface, (0, 0))

        # Animated torch glow (needs to update each frame)
        t = pygame.time.get_ticks()
        palette = FLOOR_PALETTES.get(floor_num, FLOOR_PALETTES[1])
        _, _, _, accent = palette
        torches = [200, 500, 800, 1100]
        for tx in torches:
            flame_h = 12 + math.sin(t * 0.008 + tx) * 4
            glow = pygame.Surface((100, 100), pygame.SRCALPHA)
            glow_a = int(18 + math.sin(t * 0.005 + tx * 0.3) * 6)
            pygame.draw.circle(glow, (TORCH_AMBER[0], TORCH_AMBER[1], TORCH_AMBER[2], glow_a),
                               (50, 50), 50)
            self.screen.blit(glow, (tx - 50, 140))
            # Flame
            points = [(tx - 4, 180), (tx, int(180 - flame_h)), (tx + 4, 180)]
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
            self.player.split()
        elif button == CTRL_ZR:
            self.player.perfect_dodge()
        elif button == CTRL_L:
            self.player.switch_split_piece()
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
        try:
            from game.ui.death_screen import run_death_screen
            result = run_death_screen(self.screen, self.clock, self.run_count, self.joystick)
        except Exception:
            result = self._fallback_death()
        if result == "retry":
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


class FallbackPlatform:
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
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
