"""
SPLIT — Combat System
Handles collision detection between player projectiles, enemy projectiles/hazards,
ground pound radius, and all damage application with difficulty scaling.
"""
import math
import pygame
from game.engine.settings import (
    GameEvent, Difficulty, EnemyType,
    DIFFICULTY_SETTINGS, HARD_DAMAGE_MULTIPLIER,
    GROUND_POUND_SPEED, ENEMY_CONTACT_DAMAGE,
)
from game.entities.enemies import (
    SanitizerTrail, SanitizerGlob, SanitizerPuddle, SanitizerArrow,
    SanitizerWarrior,
)


# Ground pound kill radius in pixels
GROUND_POUND_RADIUS = 80

# Jelly shot damage against warriors (armored — reduced from normal)
WARRIOR_JELLY_DAMAGE = 2

# Default jelly shot damage (projectile has no explicit damage — derived from HP cost)
JELLY_SHOT_DAMAGE = 10


class CombatSystem:
    """Per-frame combat resolution: projectile hits, hazard damage, ground pound."""

    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.missed_shots = 0  # track for Jello Graveyard easter egg

    def _emit(self, event, **kwargs):
        """Safe event_bus emit -- no-op if bus is None."""
        if self.event_bus:
            self.event_bus.emit(event, **kwargs)

    def check_hits(self, player, enemies, projectiles, difficulty=Difficulty.NORMAL, platforms=None):
        """Main per-frame collision check.

        Args:
            player:      JelloCube instance.
            enemies:     List of alive Enemy instances.
            projectiles: Dict with keys:
                         'player'  -> list of JelloProjectile
                         'enemy'   -> list of enemy projectiles (SanitizerGlob, SanitizerArrow)
                         'hazards' -> list of ground hazards (SanitizerTrail, SanitizerPuddle)
            difficulty:  Current Difficulty enum.

        Returns:
            List of event dicts suitable for VFX / sound triggers.
        """
        events = []
        active_pill = getattr(player, 'active_pill', None)

        player_projs = projectiles.get('player', [])
        enemy_projs = projectiles.get('enemy', [])
        hazards = projectiles.get('hazards', [])

        # ── 1. Player projectiles → enemies ──
        events += self._player_vs_enemies(player, player_projs, enemies, active_pill)

        # ── 2. Enemy projectiles → player ──
        events += self._enemy_projs_vs_player(player, enemy_projs, difficulty, active_pill, platforms)

        # ── 3. Hazards → player ──
        events += self._hazards_vs_player(player, hazards, difficulty, active_pill)

        # ── 4. Ground pound → enemies in radius ──
        events += self._ground_pound_vs_enemies(player, enemies, active_pill)

        # ── 5. Enemy body contact → player ──
        events += self._enemy_contact_vs_player(player, enemies, difficulty, active_pill)

        return events

    # ── Internal collision methods ──

    def _player_vs_enemies(self, player, player_projs, enemies, active_pill=None):
        """Check each player projectile against each alive enemy."""
        events = []
        # Pill damage multiplier
        pill_mult = 1.0
        if active_pill == 'fire':
            pill_mult = 1.5
        elif active_pill == 'attack_up':
            pill_mult = 2.0

        for proj in player_projs:
            if not proj.alive:
                continue
            proj_rect = proj.get_rect()
            hit_something = False

            for enemy in enemies:
                if not enemy.alive:
                    continue
                enemy_hr = enemy.get_hit_rect() if hasattr(enemy, 'get_hit_rect') else enemy.get_rect()
                if proj_rect.colliderect(enemy_hr):
                    hit_something = True

                    # Warriors have armor — jelly shots only deal 2 damage
                    if enemy.enemy_type == EnemyType.SANITIZER_WARRIOR:
                        damage = int(WARRIOR_JELLY_DAMAGE * pill_mult)
                    else:
                        damage = int(JELLY_SHOT_DAMAGE * pill_mult)

                    killed = enemy.take_damage(damage)
                    proj.alive = False

                    # Electricity pill: stun enemy briefly
                    if active_pill == 'electricity' and hasattr(enemy, 'stun_timer'):
                        enemy.stun_timer = 30  # 0.5 sec stun

                    # Water pill: heal player on kill
                    if active_pill == 'water' and killed and player:
                        heal = 5
                        player.health = min(player.max_health, player.health + heal)

                    # Build event
                    evt = {
                        'event': GameEvent.ENEMY_HIT,
                        'x': enemy.x + enemy.w / 2,
                        'y': enemy.y + enemy.h / 2,
                        'damage': damage,
                        'enemy_type': enemy.enemy_type,
                    }
                    events.append(evt)
                    self._emit(GameEvent.ENEMY_HIT,
                                       x=evt['x'], y=evt['y'],
                                       damage=damage)

                    if killed:
                        kill_evt = {
                            'event': GameEvent.ENEMY_DIED,
                            'x': enemy.x + enemy.w / 2,
                            'y': enemy.y + enemy.h / 2,
                            'enemy_type': enemy.enemy_type,
                        }
                        events.append(kill_evt)
                        self._emit(GameEvent.ENEMY_DIED,
                                           x=kill_evt['x'], y=kill_evt['y'])

                    break  # projectile can only hit one enemy

            if not hit_something and not proj.alive:
                # Projectile expired without hitting — count as miss
                self.missed_shots += 1

        # Also count projectiles that went off-screen or timed out this frame
        for proj in player_projs:
            if not proj.alive:
                # Already handled above or about to be cleaned up
                pass

        return events

    def _enemy_projs_vs_player(self, player, enemy_projs, difficulty, active_pill=None, platforms=None):
        """Check enemy projectiles against the player."""
        events = []
        if not hasattr(player, 'health') or player.health <= 0:
            return events

        player_rect = player.get_hit_rect() if hasattr(player, 'get_hit_rect') else player.get_rect()
        dmg_mult = DIFFICULTY_SETTINGS[difficulty]['damage_multiplier']
        # Ice pill: 50% incoming damage reduction
        if active_pill == 'ice':
            dmg_mult *= 0.5

        for proj in enemy_projs:
            if not proj.alive:
                continue
            if player_rect.colliderect(proj.get_rect()):
                # Check if a platform blocks the projectile's path to the player
                if platforms:
                    proj_cx = proj.x
                    proj_cy = proj.y
                    player_cx = player.x + player.w / 2
                    player_cy = player.y + player.h / 2
                    blocked = False
                    for plat in platforms:
                        pr = plat.get_rect() if hasattr(plat, 'get_rect') else pygame.Rect(0, 0, 0, 0)
                        if pr.clipline(proj_cx, proj_cy, player_cx, player_cy):
                            blocked = True
                            break
                    if blocked:
                        proj.alive = False
                        continue
                raw_damage = proj.damage
                scaled_damage = max(1, int(raw_damage * dmg_mult))
                actual = player.take_damage(scaled_damage, difficulty)
                proj.alive = False

                if actual > 0:
                    evt = {
                        'event': GameEvent.PLAYER_HIT,
                        'x': player.x + player.w / 2,
                        'y': player.y + player.h / 2,
                        'damage': actual,
                        'source': type(proj).__name__,
                    }
                    events.append(evt)

        return events

    def _hazards_vs_player(self, player, hazards, difficulty, active_pill=None):
        """Check ground hazards (trails, puddles) against the player."""
        events = []
        if not hasattr(player, 'health') or player.health <= 0:
            return events

        player_rect = player.get_rect()
        dmg_mult = DIFFICULTY_SETTINGS[difficulty]['damage_multiplier']
        # Ice pill: 50% incoming damage reduction
        if active_pill == 'ice':
            dmg_mult *= 0.5

        for hazard in hazards:
            if not hazard.alive:
                continue
            if player_rect.colliderect(hazard.get_rect()):
                raw_damage = hazard.damage
                scaled_damage = max(1, int(raw_damage * dmg_mult))
                actual = player.take_damage(scaled_damage, difficulty)

                if actual > 0:
                    evt = {
                        'event': GameEvent.PLAYER_HIT,
                        'x': player.x + player.w / 2,
                        'y': player.y + player.h / 2,
                        'damage': actual,
                        'source': type(hazard).__name__,
                    }
                    events.append(evt)

        return events

    def _ground_pound_vs_enemies(self, player, enemies, active_pill=None):
        """If the player just landed a ground pound, damage nearby enemies."""
        events = []
        if not getattr(player, 'just_landed_pound', False):
            return events

        pound_cx = player.x + player.w / 2
        pound_cy = player.y + player.h  # bottom of player = impact point

        # Pill damage multiplier for ground pound
        pill_mult = 1.0
        if active_pill == 'fire':
            pill_mult = 1.5
        elif active_pill == 'attack_up':
            pill_mult = 2.0

        for enemy in enemies:
            if not enemy.alive:
                continue
            ecx = enemy.x + enemy.w / 2
            ecy = enemy.y + enemy.h / 2
            dist = math.hypot(ecx - pound_cx, ecy - pound_cy)

            if dist <= GROUND_POUND_RADIUS:
                # Ground pound damage scales inversely with distance
                base_damage = 25
                scale = 1.0 - (dist / GROUND_POUND_RADIUS) * 0.5  # 100%-50%
                damage = int(base_damage * scale * pill_mult)

                killed = enemy.take_damage(damage)

                # Electricity pill: stun enemy
                if active_pill == 'electricity' and hasattr(enemy, 'stun_timer'):
                    enemy.stun_timer = 30

                evt = {
                    'event': GameEvent.ENEMY_HIT,
                    'x': ecx,
                    'y': ecy,
                    'damage': damage,
                    'enemy_type': enemy.enemy_type,
                    'source': 'ground_pound',
                }
                events.append(evt)
                self._emit(GameEvent.ENEMY_HIT,
                                   x=ecx, y=ecy, damage=damage)

                if killed:
                    kill_evt = {
                        'event': GameEvent.ENEMY_DIED,
                        'x': ecx,
                        'y': ecy,
                        'enemy_type': enemy.enemy_type,
                    }
                    events.append(kill_evt)
                    self._emit(GameEvent.ENEMY_DIED, x=ecx, y=ecy)

        return events

    def _enemy_contact_vs_player(self, player, enemies, difficulty, active_pill=None):
        """Check enemy bodies touching the player for contact damage."""
        events = []
        if not hasattr(player, 'health') or player.health <= 0:
            return events

        player_rect = player.get_hit_rect() if hasattr(player, 'get_hit_rect') else player.get_rect()
        dmg_mult = DIFFICULTY_SETTINGS[difficulty]['damage_multiplier']
        if active_pill == 'ice':
            dmg_mult *= 0.5

        for enemy in enemies:
            if not enemy.alive:
                continue
            enemy_hr = enemy.get_hit_rect() if hasattr(enemy, 'get_hit_rect') else enemy.get_rect()
            if player_rect.colliderect(enemy_hr):
                scaled = max(1, int(ENEMY_CONTACT_DAMAGE * dmg_mult))
                actual = player.take_damage(scaled, difficulty)
                if actual > 0:
                    events.append({
                        'event': GameEvent.PLAYER_HIT,
                        'x': player.x + player.w / 2,
                        'y': player.y + player.h / 2,
                        'damage': actual,
                        'source': 'contact',
                    })
                    break  # only take contact damage from one enemy per frame

        return events
