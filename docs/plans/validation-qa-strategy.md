# Split -- Comprehensive Validation & QA Strategy

> **Target:** Inquiry Exhibition, March 15, 2026
> **Platform:** Raspberry Pi 5 (8GB RAM, VideoCore VII GPU), Python 3.13, Pygame 2.6.1
> **Input:** Nintendo Switch Pro Controller (Bluetooth, hid_nintendo driver, SDL2 2.32.4)
> **Requirement:** Zero crashes, zero stutter, 4+ hours continuous operation

---

## Table of Contents

1. [Pi 5 Performance Testing](#1-pi-5-performance-testing)
2. [Controller Reliability](#2-controller-reliability)
3. [Audio Validation](#3-audio-validation)
4. [Visual Validation](#4-visual-validation)
5. [Exhibition-Specific Testing](#5-exhibition-specific-testing)
6. [Automated Test Framework](#6-automated-test-framework)
7. [Validation Checklist](#7-validation-checklist)
8. [Crash Prevention](#8-crash-prevention)

---

## 1. Pi 5 Performance Testing

### 1.1 Real-Time FPS Counter

Add an FPS overlay to the game that can be toggled on/off. This should be present during ALL development and testing, then hidden (but still logging) during exhibition.

**Implementation — `game/perf_monitor.py`:**

```python
"""
Performance monitor for Split.
Tracks FPS, frame times, CPU temp, and memory usage.
Toggle overlay with F3 key during development.
"""
import pygame
import time
import os
import resource

class PerfMonitor:
    def __init__(self, log_to_file=False, log_path="logs/perf.csv"):
        self.frame_times = []       # last 300 frame times (5 seconds at 60fps)
        self.max_samples = 300
        self.last_time = time.perf_counter()
        self.visible = False        # Toggle with F3
        self.font = pygame.font.Font(None, 20)
        self.log_to_file = log_to_file
        self.log_interval = 60      # Log summary every 60 frames (1 second)
        self.frame_count = 0
        self.start_time = time.perf_counter()

        if log_to_file:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            self.log_file = open(log_path, "w")
            self.log_file.write("timestamp,fps_avg,fps_1pct_low,frame_ms_avg,frame_ms_max,"
                                "cpu_temp_c,mem_rss_mb,particle_count\n")
        else:
            self.log_file = None

    def tick(self, particle_count=0):
        """Call once per frame, AFTER clock.tick()."""
        now = time.perf_counter()
        dt = now - self.last_time
        self.last_time = now
        self.frame_times.append(dt)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)
        self.frame_count += 1

        # Periodic logging
        if self.log_to_file and self.frame_count % self.log_interval == 0:
            self._log_snapshot(particle_count)

    def get_fps(self):
        """Current average FPS over the sample window."""
        if not self.frame_times:
            return 0.0
        avg_dt = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_dt if avg_dt > 0 else 0.0

    def get_fps_1pct_low(self):
        """1% low FPS -- worst 1% of frames. This is the 'stutter' metric."""
        if len(self.frame_times) < 10:
            return 0.0
        sorted_times = sorted(self.frame_times, reverse=True)
        worst_count = max(1, len(sorted_times) // 100)
        worst_avg = sum(sorted_times[:worst_count]) / worst_count
        return 1.0 / worst_avg if worst_avg > 0 else 0.0

    def get_frame_ms(self):
        """Average frame time in milliseconds."""
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000.0

    def get_frame_ms_max(self):
        """Worst frame time in the sample window."""
        if not self.frame_times:
            return 0.0
        return max(self.frame_times) * 1000.0

    def get_cpu_temp(self):
        """Read Pi 5 CPU temperature from sysfs. Returns float or None."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return int(f.read().strip()) / 1000.0
        except (FileNotFoundError, ValueError, PermissionError):
            return None

    def get_mem_rss_mb(self):
        """Current process RSS memory in MB."""
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            return usage.ru_maxrss / 1024.0  # Linux reports in KB
        except Exception:
            return 0.0

    def get_throttle_status(self):
        """Check if the Pi is throttling. Returns dict or None."""
        try:
            # vcgencmd get_throttled returns a hex bitmask
            result = os.popen("vcgencmd get_throttled").read().strip()
            # Format: throttled=0x50000
            hex_val = int(result.split("=")[1], 16)
            return {
                "under_voltage_now": bool(hex_val & 0x1),
                "freq_capped_now": bool(hex_val & 0x2),
                "throttled_now": bool(hex_val & 0x4),
                "soft_temp_limit_now": bool(hex_val & 0x8),
                "under_voltage_occurred": bool(hex_val & 0x10000),
                "freq_capped_occurred": bool(hex_val & 0x20000),
                "throttled_occurred": bool(hex_val & 0x40000),
                "soft_temp_limit_occurred": bool(hex_val & 0x80000),
            }
        except Exception:
            return None

    def draw(self, surface):
        """Draw the overlay if visible."""
        if not self.visible:
            return

        fps = self.get_fps()
        fps_1pct = self.get_fps_1pct_low()
        frame_ms = self.get_frame_ms()
        frame_ms_max = self.get_frame_ms_max()
        temp = self.get_cpu_temp()
        mem = self.get_mem_rss_mb()

        # Color coding: green = good, yellow = warning, red = bad
        def fps_color(val):
            if val >= 58:
                return (100, 255, 100)
            elif val >= 45:
                return (255, 255, 100)
            else:
                return (255, 100, 100)

        def temp_color(val):
            if val is None:
                return (180, 180, 180)
            if val < 60:
                return (100, 255, 100)
            elif val < 75:
                return (255, 255, 100)
            else:
                return (255, 100, 100)

        lines = [
            (f"FPS: {fps:.0f}", fps_color(fps)),
            (f"1% Low: {fps_1pct:.0f}", fps_color(fps_1pct)),
            (f"Frame: {frame_ms:.1f}ms (max {frame_ms_max:.1f}ms)",
             fps_color(60.0 if frame_ms < 17 else 30.0)),
            (f"Temp: {temp:.0f}C" if temp else "Temp: N/A", temp_color(temp)),
            (f"RAM: {mem:.0f}MB", (180, 180, 180)),
        ]

        # Background panel
        panel_w = 200
        panel_h = len(lines) * 18 + 8
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        surface.blit(panel, (surface.get_width() - panel_w - 4, 4))

        for i, (text, color) in enumerate(lines):
            rendered = self.font.render(text, True, color)
            surface.blit(rendered, (surface.get_width() - panel_w, 8 + i * 18))

    def _log_snapshot(self, particle_count=0):
        """Write one line to the CSV log."""
        if not self.log_file:
            return
        elapsed = time.perf_counter() - self.start_time
        temp = self.get_cpu_temp()
        self.log_file.write(
            f"{elapsed:.1f},{self.get_fps():.1f},{self.get_fps_1pct_low():.1f},"
            f"{self.get_frame_ms():.2f},{self.get_frame_ms_max():.2f},"
            f"{temp if temp else ''},"
            f"{self.get_mem_rss_mb():.1f},{particle_count}\n"
        )
        self.log_file.flush()

    def close(self):
        if self.log_file:
            self.log_file.close()
```

**Integration into `spark.py` (and eventually `main.py`):**

```python
# At top of gameplay() or main loop:
from perf_monitor import PerfMonitor
perf = PerfMonitor(log_to_file=True)

# In the game loop, after clock.tick(FPS):
perf.tick(particle_count=len(particles))

# Handle F3 toggle in event loop:
if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
    perf.visible = not perf.visible

# Before pygame.display.flip():
perf.draw(screen)

# On quit:
perf.close()
```

### 1.2 CPU and GPU Profiling on Pi 5

**Thermal monitoring commands (run in a separate terminal during testing):**

```bash
# Watch CPU temperature every 2 seconds
watch -n 2 vcgencmd measure_temp

# Full throttle status (CRITICAL for exhibition)
vcgencmd get_throttled
# Returns hex bitmask:
#   0x0     = all clear
#   Bit 0   = under-voltage detected NOW
#   Bit 1   = ARM frequency capped NOW
#   Bit 2   = currently throttled NOW
#   Bit 3   = soft temperature limit active NOW
#   Bits 16-19 = same flags but "has occurred since boot"

# GPU memory and clock
vcgencmd get_mem gpu
vcgencmd measure_clock arm
vcgencmd measure_clock core

# Real-time system monitor
htop

# Continuous thermal + throttle log (run during 4-hour soak test)
while true; do
    echo "$(date +%H:%M:%S) temp=$(vcgencmd measure_temp) throttle=$(vcgencmd get_throttled)"
    sleep 5
done >> ~/quest-craft/logs/thermal.log
```

**Python-side CPU profiling:**

```python
import cProfile
import pstats

# Profile one gameplay session
cProfile.run('gameplay()', 'logs/gameplay_profile.prof')

# Then analyze:
stats = pstats.Stats('logs/gameplay_profile.prof')
stats.sort_stats('cumulative')
stats.print_stats(30)  # Top 30 slowest functions
```

**Per-frame timing breakdown:**

```python
import time

class FrameProfiler:
    """Measures time spent in each phase of the game loop."""
    def __init__(self):
        self.sections = {}
        self.current = None
        self.current_start = 0

    def begin(self, name):
        self.current = name
        self.current_start = time.perf_counter()

    def end(self):
        if self.current:
            elapsed = (time.perf_counter() - self.current_start) * 1000
            if self.current not in self.sections:
                self.sections[self.current] = []
            self.sections[self.current].append(elapsed)
            if len(self.sections[self.current]) > 300:
                self.sections[self.current].pop(0)
            self.current = None

    def report(self):
        """Returns dict of section_name -> avg_ms."""
        result = {}
        for name, times in self.sections.items():
            result[name] = sum(times) / len(times) if times else 0
        return result

# Usage in game loop:
profiler = FrameProfiler()

profiler.begin("events")
# ... event handling ...
profiler.end()

profiler.begin("update")
# ... game logic ...
profiler.end()

profiler.begin("draw_bg")
# ... background drawing ...
profiler.end()

profiler.begin("draw_entities")
# ... sprites, particles ...
profiler.end()

profiler.begin("flip")
pygame.display.flip()
profiler.end()
```

### 1.3 Memory Leak Detection

Pygame games are prone to memory leaks from Surface creation inside game loops. The current `spark.py` creates a NEW `pygame.Surface` in `Particle.draw()` on every frame for every particle -- this is the number one memory leak risk.

**Detection script -- `tests/test_memory_leak.py`:**

```python
"""
Memory leak detector for Split.
Runs the game logic in a headless-like mode, tracking memory over time.
A leak shows as continuously rising RSS memory.
"""
import tracemalloc
import resource
import time
import gc

def get_rss_mb():
    """Get current RSS in MB."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def test_particle_memory():
    """
    Simulate creating and destroying thousands of particles.
    If memory does not stabilize, there is a leak.
    """
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((100, 100))  # Minimal window

    tracemalloc.start()

    from game.spark import Particle, JELLO_GREEN

    particles = []
    readings = []

    for cycle in range(100):
        # Spawn 50 particles (simulates heavy gameplay)
        for _ in range(50):
            particles.append(Particle(100, 100, JELLO_GREEN, size=3,
                                      speed=0.5, lifetime=30))

        # Simulate 30 frames
        for _ in range(30):
            alive = []
            for p in particles:
                if p.update():
                    p.draw(screen)
                    alive.append(p)
            particles = alive

        # Force garbage collection
        gc.collect()

        current, peak = tracemalloc.get_traced_memory()
        rss = get_rss_mb()
        readings.append((cycle, current / 1024 / 1024, peak / 1024 / 1024, rss))

        if cycle % 20 == 0:
            print(f"Cycle {cycle}: current={current/1024/1024:.1f}MB "
                  f"peak={peak/1024/1024:.1f}MB RSS={rss:.0f}MB "
                  f"particles={len(particles)}")

    tracemalloc.stop()
    pygame.quit()

    # Analyze: compare first 10 readings to last 10
    early = [r[3] for r in readings[:10]]
    late = [r[3] for r in readings[-10:]]
    early_avg = sum(early) / len(early)
    late_avg = sum(late) / len(late)
    growth = late_avg - early_avg

    print(f"\nMemory growth over test: {growth:.1f}MB")
    if growth > 10:
        print("WARNING: Significant memory growth detected -- possible leak!")
        return False
    else:
        print("OK: Memory appears stable.")
        return True

if __name__ == "__main__":
    test_particle_memory()
```

**Known leak pattern in current `spark.py`:**

```python
# PROBLEM: This creates a new Surface EVERY FRAME for EVERY PARTICLE
def draw(self, surf):
    # ...
    ps = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)  # NEW ALLOC EVERY CALL
    pygame.draw.circle(ps, color, (s, s), s)
    surf.blit(ps, (...))
```

**FIX: Pre-allocate or cache surfaces:**

```python
# Option A: Surface pool (reuse surfaces by size)
_surface_cache = {}

def get_cached_surface(size):
    """Return a cached SRCALPHA surface, cleared for reuse."""
    key = (size, size)
    if key not in _surface_cache:
        _surface_cache[key] = pygame.Surface(key, pygame.SRCALPHA)
    surf = _surface_cache[key]
    surf.fill((0, 0, 0, 0))
    return surf

# Option B: Use pygame.gfxdraw for direct alpha circles (no Surface needed)
import pygame.gfxdraw

def draw_alpha_circle(target, x, y, radius, color_with_alpha):
    """Draw a filled circle with alpha directly, no temp Surface."""
    r, g, b, a = color_with_alpha
    pygame.gfxdraw.filled_circle(target, int(x), int(y), int(radius), (r, g, b, a))
    pygame.gfxdraw.aacircle(target, int(x), int(y), int(radius), (r, g, b, a))
```

### 1.4 Thermal Monitoring and Prevention

The Pi 5 throttles at 85C and will reduce clock speed, causing visible stutter. The exhibition hall may be warm with many people.

**Prevention checklist:**

1. **Active cooling is MANDATORY.** Use the official Raspberry Pi Active Cooler or a case with a fan. Without it, the Pi 5 will thermal throttle under sustained Pygame load within 10-15 minutes.

2. **Thermal monitoring script -- `scripts/thermal_watchdog.sh`:**

```bash
#!/bin/bash
# Run alongside the game to monitor thermals
# Usage: bash scripts/thermal_watchdog.sh &

LOG=~/quest-craft/logs/thermal.log
WARN_TEMP=75
CRIT_TEMP=82

mkdir -p ~/quest-craft/logs

echo "=== Thermal Watchdog Started $(date) ===" >> "$LOG"

while true; do
    TEMP=$(vcgencmd measure_temp | grep -oP '[0-9]+\.[0-9]+')
    THROTTLE=$(vcgencmd get_throttled | cut -d= -f2)
    TIMESTAMP=$(date +"%H:%M:%S")

    echo "$TIMESTAMP temp=${TEMP}C throttle=$THROTTLE" >> "$LOG"

    # Integer comparison
    TEMP_INT=${TEMP%.*}

    if [ "$TEMP_INT" -ge "$CRIT_TEMP" ]; then
        echo "$TIMESTAMP CRITICAL: ${TEMP}C -- THROTTLING LIKELY" >> "$LOG"
        # Could trigger quality reduction via a signal/file flag
        touch /tmp/split_reduce_quality
    elif [ "$TEMP_INT" -ge "$WARN_TEMP" ]; then
        echo "$TIMESTAMP WARNING: ${TEMP}C -- getting hot" >> "$LOG"
    fi

    if [ "$THROTTLE" != "0x0" ]; then
        echo "$TIMESTAMP THROTTLE FLAG: $THROTTLE" >> "$LOG"
    fi

    sleep 5
done
```

3. **In-game thermal response:**

```python
import os

class ThermalManager:
    """Reads Pi 5 thermal state and adjusts quality settings."""

    def __init__(self):
        self.check_interval = 300  # Check every 300 frames (5 seconds)
        self.frame_counter = 0
        self.quality_level = "high"  # high, medium, low
        self.max_particles = {"high": 200, "medium": 80, "low": 30}
        self.bg_detail = {"high": True, "medium": True, "low": False}

    def update(self):
        self.frame_counter += 1
        if self.frame_counter < self.check_interval:
            return

        self.frame_counter = 0

        # Check if watchdog flagged critical temp
        if os.path.exists("/tmp/split_reduce_quality"):
            if self.quality_level == "high":
                self.quality_level = "medium"
            elif self.quality_level == "medium":
                self.quality_level = "low"
            os.remove("/tmp/split_reduce_quality")

        # Also read temp directly
        temp = self._read_temp()
        if temp and temp < 65 and self.quality_level != "high":
            self.quality_level = "high"  # Recover quality when cool

    def get_max_particles(self):
        return self.max_particles[self.quality_level]

    def should_draw_bg_detail(self):
        return self.bg_detail[self.quality_level]

    def _read_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                return int(f.read().strip()) / 1000.0
        except Exception:
            return None
```

### 1.5 Stress Testing

**`tests/stress_test.py` -- Push the Pi 5 to its limits:**

```python
"""
Stress test for Split on Pi 5.
Spawns maximum particles, projectiles, and effects simultaneously
to find the performance floor.
"""
import pygame
import sys
import time
import random
import math

# Import game classes
sys.path.insert(0, "game")
from spark import (Particle, Collectible, JelloProjectile, Shockwave,
                   JelloCube, JELLO_GREEN, TORCH_AMBER, EMBER,
                   SCREEN_W, SCREEN_H, GROUND_Y, FPS)

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED | pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Test parameters
MAX_PARTICLES_TO_TEST = 500
PARTICLE_SPAWN_RATE = 10  # per frame
MAX_PROJECTILES = 50
MAX_SHOCKWAVES = 10

particles = []
projectiles = []
shockwaves = []
frame_data = []

running = True
frame = 0

print("=== STRESS TEST ===")
print("Spawning particles and effects. Watching FPS...")
print("Press ESC to stop.\n")

while running and frame < 3600:  # Run for 60 seconds
    dt = clock.tick(FPS)
    frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Spawn particles aggressively
    if len(particles) < MAX_PARTICLES_TO_TEST:
        for _ in range(PARTICLE_SPAWN_RATE):
            particles.append(Particle(
                random.uniform(0, SCREEN_W),
                random.uniform(0, SCREEN_H),
                random.choice([JELLO_GREEN, TORCH_AMBER, EMBER]),
                size=random.uniform(2, 5),
                speed=random.uniform(0.3, 1.0),
                lifetime=random.randint(60, 180)
            ))

    # Spawn projectiles
    if len(projectiles) < MAX_PROJECTILES and frame % 10 == 0:
        projectiles.append(JelloProjectile(
            random.uniform(100, SCREEN_W - 100),
            random.uniform(100, GROUND_Y),
            random.choice([-1, 1])
        ))

    # Spawn shockwaves
    if len(shockwaves) < MAX_SHOCKWAVES and frame % 30 == 0:
        shockwaves.append(Shockwave(
            random.uniform(100, SCREEN_W - 100),
            GROUND_Y
        ))

    # Update
    particles = [p for p in particles if p.update()]
    projectiles = [p for p in projectiles if p.update()]
    shockwaves = [s for s in shockwaves if s.update()]

    # Draw
    screen.fill((26, 26, 46))

    for p in particles:
        p.draw(screen)
    for p in projectiles:
        p.draw(screen)
    for s in shockwaves:
        s.draw(screen)

    # HUD
    actual_fps = clock.get_fps()
    count_text = (f"Particles: {len(particles)}  Projectiles: {len(projectiles)}  "
                  f"Shockwaves: {len(shockwaves)}  FPS: {actual_fps:.0f}")
    text_surf = font.render(count_text, True, (255, 255, 255))
    screen.blit(text_surf, (10, 10))

    pygame.display.flip()

    # Log
    frame_data.append({
        "frame": frame,
        "particles": len(particles),
        "projectiles": len(projectiles),
        "fps": actual_fps,
        "dt_ms": dt,
    })

    if frame % 60 == 0:
        print(f"Frame {frame}: {len(particles)} particles, "
              f"{len(projectiles)} proj, FPS={actual_fps:.0f}")

# Summary
pygame.quit()

if frame_data:
    fps_values = [d["fps"] for d in frame_data if d["fps"] > 0]
    if fps_values:
        print(f"\n=== RESULTS ===")
        print(f"Frames rendered: {frame}")
        print(f"FPS avg: {sum(fps_values)/len(fps_values):.1f}")
        print(f"FPS min: {min(fps_values):.1f}")
        print(f"FPS 1% low: {sorted(fps_values)[len(fps_values)//100]:.1f}")
        print(f"Max particles reached: {max(d['particles'] for d in frame_data)}")

        # Find the particle count where FPS drops below 55
        for d in frame_data:
            if d["fps"] > 0 and d["fps"] < 55:
                print(f"FPS dropped below 55 at {d['particles']} particles "
                      f"(frame {d['frame']})")
                break
        else:
            print("FPS never dropped below 55 -- Pi 5 can handle the load!")
```

### 1.6 Automated Performance Regression Tests

```python
"""
tests/test_performance.py
Run after every code change to catch performance regressions.

Usage: python3 -m pytest tests/test_performance.py -v
"""
import pytest
import time
import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "game"))


@pytest.fixture(scope="module")
def pygame_env():
    """Initialize pygame once for all perf tests."""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    yield screen
    pygame.quit()


def benchmark_frames(screen, setup_fn, frame_fn, num_frames=120):
    """Run frame_fn for num_frames, return avg frame time in ms."""
    state = setup_fn()
    clock = pygame.time.Clock()
    times = []

    for _ in range(num_frames):
        start = time.perf_counter()
        frame_fn(screen, state)
        pygame.display.flip()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        clock.tick(60)
        # Drain event queue
        pygame.event.pump()

    return {
        "avg_ms": sum(times) / len(times),
        "max_ms": max(times),
        "p99_ms": sorted(times)[int(len(times) * 0.99)],
    }


def test_empty_frame_under_1ms(pygame_env):
    """An empty frame should take less than 1ms."""
    def setup():
        return None

    def frame(screen, state):
        screen.fill((0, 0, 0))

    result = benchmark_frames(pygame_env, setup, frame)
    assert result["avg_ms"] < 1.0, f"Empty frame too slow: {result['avg_ms']:.2f}ms"


def test_100_particles_under_8ms(pygame_env):
    """100 particles should render under 8ms per frame (leaving headroom for 60fps)."""
    from spark import Particle, JELLO_GREEN
    import random

    def setup():
        return [Particle(random.uniform(0, 1280), random.uniform(0, 720),
                         JELLO_GREEN, size=3, speed=0.5, lifetime=999)
                for _ in range(100)]

    def frame(screen, state):
        screen.fill((0, 0, 0))
        for p in state:
            p.update()
            p.draw(screen)

    result = benchmark_frames(pygame_env, setup, frame)
    assert result["avg_ms"] < 8.0, f"100 particles too slow: {result['avg_ms']:.2f}ms"


def test_background_draw_under_10ms(pygame_env):
    """Castle background should render under 10ms."""
    from spark import draw_castle_bg

    def setup():
        return None

    def frame(screen, state):
        draw_castle_bg(screen)

    result = benchmark_frames(pygame_env, setup, frame)
    assert result["avg_ms"] < 10.0, f"Background too slow: {result['avg_ms']:.2f}ms"


def test_full_scene_under_16ms(pygame_env):
    """Full gameplay scene must stay under 16.67ms to hit 60fps."""
    from spark import (Particle, Collectible, JelloCube, JelloProjectile,
                       draw_castle_bg, draw_platforms, JELLO_GREEN,
                       TORCH_AMBER, GROUND_Y)
    import random

    def setup():
        return {
            "player": JelloCube(100, GROUND_Y - 50),
            "particles": [Particle(random.uniform(0, 1280),
                                   random.uniform(0, 720),
                                   JELLO_GREEN) for _ in range(50)],
            "platforms": [(180, 400, 120, 16), (380, 330, 140, 16),
                          (560, 400, 100, 16)],
            "collectibles": [Collectible(300, 300) for _ in range(7)],
            "projectiles": [JelloProjectile(400, 300, 1) for _ in range(5)],
        }

    def frame(screen, state):
        draw_castle_bg(screen)
        draw_platforms(screen, state["platforms"])
        for c in state["collectibles"]:
            c.update()
            c.draw(screen)
        for p in state["particles"]:
            p.update()
            p.draw(screen)
        for p in state["projectiles"]:
            p.update()
            p.draw(screen)
        state["player"].draw(screen)

    result = benchmark_frames(pygame_env, setup, frame)
    assert result["avg_ms"] < 16.67, (
        f"Full scene too slow for 60fps: {result['avg_ms']:.2f}ms avg, "
        f"{result['max_ms']:.2f}ms max"
    )
```

---

## 2. Controller Reliability

### 2.1 Bluetooth Connection Stability Testing

The Pro Controller uses Bluetooth Classic (not BLE) via the `hid_nintendo` kernel driver. Known issues:

- The controller can disconnect after ~15 minutes of idle
- Bluetooth can drop if Wi-Fi is on the same 2.4GHz band (Pi 5 shares the antenna)
- The `hid_nintendo` driver occasionally misreports calibration data

**Long-session stability test -- `tests/test_controller_stability.py`:**

```python
"""
Controller stability test.
Keeps the controller active and logs any disconnections over a long period.
Run for 1+ hours before the exhibition.

Usage: python3 tests/test_controller_stability.py
"""
import pygame
import time
import sys
import os

pygame.init()
screen = pygame.display.set_mode((640, 200))
pygame.display.set_caption("Controller Stability Test")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

os.makedirs("logs", exist_ok=True)
log = open("logs/controller_stability.log", "w")

joystick = None
connected = False
disconnects = 0
reconnects = 0
last_input_time = time.time()
start_time = time.time()
input_count = 0

def log_event(msg):
    elapsed = time.time() - start_time
    line = f"[{elapsed:.0f}s] {msg}"
    print(line)
    log.write(line + "\n")
    log.flush()

log_event("Controller stability test started")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.JOYDEVICEADDED:
            try:
                joystick = pygame.joystick.Joystick(event.device_index)
                joystick.init()
                connected = True
                reconnects += 1
                log_event(f"CONNECTED: {joystick.get_name()} "
                          f"(buttons={joystick.get_numbuttons()}, "
                          f"axes={joystick.get_numaxes()}, "
                          f"hats={joystick.get_numhats()})")
            except Exception as e:
                log_event(f"CONNECTION FAILED: {e}")

        if event.type == pygame.JOYDEVICEREMOVED:
            connected = False
            disconnects += 1
            log_event(f"DISCONNECTED (total disconnects: {disconnects})")

        if event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP,
                          pygame.JOYAXISMOTION, pygame.JOYHATMOTION):
            last_input_time = time.time()
            input_count += 1

    # Check for input timeout (controller might be "connected" but unresponsive)
    idle_seconds = time.time() - last_input_time
    if connected and idle_seconds > 30:
        log_event(f"WARNING: No input for {idle_seconds:.0f}s -- controller may be unresponsive")
        last_input_time = time.time()  # Reset to avoid spam

    # Draw status
    elapsed = time.time() - start_time
    screen.fill((26, 26, 46))

    lines = [
        f"Elapsed: {elapsed/60:.0f} min",
        f"Status: {'CONNECTED' if connected else 'DISCONNECTED'}",
        f"Disconnects: {disconnects}  Reconnects: {reconnects}",
        f"Total inputs: {input_count}  Idle: {idle_seconds:.0f}s",
    ]
    for i, text in enumerate(lines):
        color = (100, 255, 100) if connected else (255, 100, 100)
        surf = font.render(text, True, color)
        screen.blit(surf, (20, 20 + i * 30))

    pygame.display.flip()
    clock.tick(30)

log_event(f"Test ended. Duration: {(time.time()-start_time)/60:.1f} min, "
          f"Disconnects: {disconnects}, Inputs: {input_count}")
log.close()
pygame.quit()
```

### 2.2 Controller Disconnect/Reconnect Handling

The current `spark.py` already has `JOYDEVICEADDED` handling, which is good. But it needs a **visible on-screen indicator** and **graceful fallback to keyboard**:

```python
class ControllerManager:
    """
    Manages Pro Controller connection with visible status and auto-reconnect.
    """
    def __init__(self):
        self.joystick = None
        self.connected = False
        self.disconnect_time = None
        self.reconnect_flash = 0
        self.font = pygame.font.Font(None, 22)

        # Try to connect on startup
        self._scan_controllers()

    def _scan_controllers(self):
        """Scan for any connected joystick."""
        for i in range(pygame.joystick.get_count()):
            try:
                joy = pygame.joystick.Joystick(i)
                joy.init()
                self.joystick = joy
                self.connected = True
                return
            except Exception:
                continue

    def handle_event(self, event):
        """Call from the event loop."""
        if event.type == pygame.JOYDEVICEADDED:
            try:
                self.joystick = pygame.joystick.Joystick(event.device_index)
                self.joystick.init()
                self.connected = True
                self.reconnect_flash = 120  # Show "reconnected" for 2 seconds
            except Exception:
                pass

        if event.type == pygame.JOYDEVICEREMOVED:
            self.connected = False
            self.disconnect_time = pygame.time.get_ticks()
            self.joystick = None

    def get_joystick(self):
        """Returns the joystick or None if disconnected."""
        return self.joystick if self.connected else None

    def draw_status(self, surface):
        """Draw connection status indicator."""
        if self.reconnect_flash > 0:
            self.reconnect_flash -= 1
            text = self.font.render("Controller reconnected!", True, (100, 255, 100))
            rect = text.get_rect(center=(surface.get_width() // 2, 40))
            surface.blit(text, rect)
            return

        if not self.connected:
            # Pulsing warning
            t = pygame.time.get_ticks()
            alpha = int(180 + 75 * math.sin(t * 0.005))
            text = self.font.render("Controller disconnected -- use keyboard",
                                    True, (255, 180, 60))
            text.set_alpha(alpha)
            rect = text.get_rect(center=(surface.get_width() // 2, 40))
            surface.blit(text, rect)
```

### 2.3 Input Lag Measurement

Input lag on Pi 5 Bluetooth is typically 8-16ms (one frame). To measure it:

```python
"""
tests/test_input_lag.py
Measures the time from button press event to screen response.
Uses visual flash -- point a slow-motion camera at the screen and controller
for ground truth, or use this software measurement.
"""
import pygame
import time

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

measurements = []
flash_until = 0
last_press_time = 0

print("Press any button on the controller. The screen will flash.")
print("This measures software-level event-to-render latency.")
print("Press ESC to finish and see results.\n")

running = True
while running:
    frame_start = time.perf_counter()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.JOYBUTTONDOWN:
            last_press_time = time.perf_counter()
            flash_until = pygame.time.get_ticks() + 200

    # The "response" is drawing the flash
    now_ticks = pygame.time.get_ticks()
    if now_ticks < flash_until and last_press_time > 0:
        screen.fill((255, 255, 255))  # Flash white
        render_time = time.perf_counter()
        latency_ms = (render_time - last_press_time) * 1000
        if latency_ms < 50:  # Ignore stale
            measurements.append(latency_ms)
            last_press_time = 0  # Consume
    else:
        screen.fill((26, 26, 46))

    text = font.render(f"Measurements: {len(measurements)}", True, (200, 200, 200))
    screen.blit(text, (20, 20))
    if measurements:
        avg = sum(measurements) / len(measurements)
        text2 = font.render(f"Avg latency: {avg:.1f}ms", True, (100, 255, 100))
        screen.blit(text2, (20, 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

if measurements:
    print(f"\n=== Input Lag Results ===")
    print(f"Samples: {len(measurements)}")
    print(f"Average: {sum(measurements)/len(measurements):.1f}ms")
    print(f"Min: {min(measurements):.1f}ms")
    print(f"Max: {max(measurements):.1f}ms")
    print(f"P95: {sorted(measurements)[int(len(measurements)*0.95)]:.1f}ms")
```

### 2.4 Button Mapping Verification Script

The existing `game/test_controller.py` is excellent. Extend it with an automated verification mode:

```python
"""
tests/test_button_mapping.py
Automated verification that button mappings match the expected Split controls.
This catches changes in SDL2 or hid_nintendo driver behavior.
"""
import pygame
import sys

EXPECTED_MAPPING = {
    # button_index: (expected_name, game_action)
    0: ("B", "Jello Shot"),
    1: ("A", "Jump"),
    2: ("X", "Split"),
    3: ("Y", "unused"),
    9: ("Minus", "unused"),
    10: ("Plus", "Quit/Menu"),
}

EXPECTED_AXES = 4     # LStickX, LStickY, RStickX, RStickY
EXPECTED_HATS = 1     # D-pad
EXPECTED_BUTTONS = 14

def verify_controller():
    pygame.init()

    if pygame.joystick.get_count() == 0:
        print("FAIL: No controller detected")
        pygame.quit()
        return False

    joy = pygame.joystick.Joystick(0)
    joy.init()

    print(f"Controller: {joy.get_name()}")
    print(f"Buttons: {joy.get_numbuttons()} (expected {EXPECTED_BUTTONS})")
    print(f"Axes: {joy.get_numaxes()} (expected {EXPECTED_AXES})")
    print(f"Hats: {joy.get_numhats()} (expected {EXPECTED_HATS})")

    passed = True

    if joy.get_numbuttons() != EXPECTED_BUTTONS:
        print(f"WARNING: Button count mismatch! Got {joy.get_numbuttons()}, "
              f"expected {EXPECTED_BUTTONS}")
        print("The button mapping may have changed -- verify manually with "
              "test_controller.py")
        passed = False

    if joy.get_numaxes() != EXPECTED_AXES:
        print(f"WARNING: Axis count mismatch! Got {joy.get_numaxes()}, "
              f"expected {EXPECTED_AXES}")
        passed = False

    if joy.get_numhats() != EXPECTED_HATS:
        print(f"WARNING: Hat count mismatch! Got {joy.get_numhats()}, "
              f"expected {EXPECTED_HATS}")
        passed = False

    # Check deadzone on all axes
    for a in range(min(joy.get_numaxes(), EXPECTED_AXES)):
        val = joy.get_axis(a)
        if abs(val) > 0.15:
            print(f"WARNING: Axis {a} has resting value {val:.3f} "
                  f"(outside deadzone 0.15)")
            print("Stick calibration may be off.")

    if passed:
        print("\nPASS: Controller configuration matches expected Split mapping")
    else:
        print("\nWARNING: Controller configuration has differences -- "
              "test manually before exhibition")

    pygame.quit()
    return passed

if __name__ == "__main__":
    success = verify_controller()
    sys.exit(0 if success else 1)
```

### 2.5 Dead Zone Calibration

The current `spark.py` uses a dead zone of 0.3 for stick movement. The `test_controller.py` uses 0.15. These should be consistent and tunable:

```python
# Recommended dead zone values for Pro Controller on Pi 5:
DEADZONE_MOVEMENT = 0.25   # Left stick movement -- slightly generous to avoid drift
DEADZONE_GROUND_POUND = 0.5  # Down-stick for ground pound -- already in spark.py, good

def apply_deadzone(value, threshold=DEADZONE_MOVEMENT):
    """Apply deadzone with smooth ramp (no sudden jump)."""
    if abs(value) < threshold:
        return 0.0
    # Rescale so the output goes from 0 to 1 starting at the deadzone edge
    sign = 1 if value > 0 else -1
    return sign * (abs(value) - threshold) / (1.0 - threshold)
```

### 2.6 Hot-Plug Testing Procedure

Manual test procedure to run before the exhibition:

```
HOT-PLUG TEST CHECKLIST
========================
Run the game (spark.py). For each step, verify the game continues without crash.

[ ] 1. Start game with controller connected -- verify controls work
[ ] 2. Turn controller off (hold Home 3 seconds) -- verify keyboard still works
[ ] 3. Turn controller back on (press Home) -- verify controller reconnects
[ ] 4. Disconnect Bluetooth (from Pi's bluetoothctl) -- verify no crash
[ ] 5. Reconnect via bluetoothctl connect <MAC> -- verify controls return
[ ] 6. Start game with NO controller -- verify keyboard works
[ ] 7. Connect controller while on title screen -- verify it works
[ ] 8. Connect controller during gameplay -- verify it works
[ ] 9. USB-C fallback: plug in controller via USB-C cable -- verify it works
```

---

## 3. Audio Validation

### 3.1 Simultaneous Sound Playback

Pygame's mixer has a limited number of channels (default 8). When you exceed the channel count, sounds are silently dropped.

```python
"""
tests/test_audio.py
Audio system validation for Split.
"""
import pygame
import time
import os
import sys

def test_mixer_channels():
    """Verify we have enough mixer channels for gameplay."""
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Split needs: jump sound + shoot sound + land sound + collect sound
    #              + ambient + enemy sounds + music
    # Recommend at least 16 channels
    REQUIRED_CHANNELS = 16
    pygame.mixer.set_num_channels(REQUIRED_CHANNELS)

    actual = pygame.mixer.get_num_channels()
    print(f"Mixer channels: {actual} (required: {REQUIRED_CHANNELS})")
    assert actual >= REQUIRED_CHANNELS, f"Not enough channels: {actual}"

    # Test simultaneous playback
    # Create a simple test tone
    import array
    sample_rate = 44100
    duration = 0.1  # 100ms test tone
    frequency = 440
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        import math
        buf[i] = int(16000 * math.sin(2 * math.pi * frequency * i / sample_rate))

    sound = pygame.mixer.Sound(buffer=buf)

    # Play on all channels simultaneously
    channels_used = 0
    for i in range(REQUIRED_CHANNELS):
        ch = sound.play()
        if ch:
            channels_used += 1

    print(f"Simultaneous sounds playing: {channels_used}/{REQUIRED_CHANNELS}")
    time.sleep(0.2)

    pygame.mixer.quit()
    pygame.quit()
    print("PASS: Audio channel test")


def test_mixer_init_settings():
    """Verify mixer initializes with optimal settings for Pi 5."""
    pygame.init()

    # Optimal settings for Pi 5:
    # - 44100 Hz sample rate (standard, good quality)
    # - 16-bit signed samples
    # - Stereo
    # - Buffer 512 samples (lower = less latency, but risk of crackling)
    #   If crackling occurs, increase to 1024 or 2048
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    freq, size, channels = pygame.mixer.get_init()
    print(f"Mixer: {freq}Hz, {size}-bit, {'stereo' if channels == 2 else 'mono'}")

    assert freq == 44100, f"Unexpected sample rate: {freq}"
    assert channels == 2, f"Expected stereo, got channels={channels}"

    pygame.mixer.quit()
    pygame.quit()
    print("PASS: Mixer init settings")


def test_long_running_audio():
    """
    Play music and sounds for 10 minutes to check for degradation.
    Monitor memory usage during playback.
    """
    import resource

    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Create a looping test tone for "music"
    import array
    import math
    sample_rate = 44100
    duration = 2.0
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples * 2)  # stereo
    for i in range(n_samples):
        val = int(8000 * math.sin(2 * math.pi * 220 * i / sample_rate))
        buf[i * 2] = val
        buf[i * 2 + 1] = val

    music_sound = pygame.mixer.Sound(buffer=buf)
    sfx_sound = pygame.mixer.Sound(buffer=buf[:sample_rate])  # 0.5s effect

    music_channel = music_sound.play(-1)  # Loop forever
    start_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    print("Playing audio for 10 minutes. Monitoring memory...")
    start = time.time()
    readings = []

    while time.time() - start < 600:  # 10 minutes
        # Play a sound effect every 2 seconds
        sfx_sound.play()
        time.sleep(2)

        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        elapsed = time.time() - start
        readings.append((elapsed, mem / 1024.0))

        if int(elapsed) % 60 == 0:
            print(f"  {elapsed/60:.0f}min: RSS={mem/1024:.0f}MB")

    end_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    growth = (end_mem - start_mem) / 1024.0

    music_channel.stop()
    pygame.mixer.quit()
    pygame.quit()

    print(f"\nMemory growth over 10 min: {growth:.1f}MB")
    if growth > 20:
        print("WARNING: Significant memory growth during audio playback")
    else:
        print("PASS: Audio memory stable")


if __name__ == "__main__":
    test_mixer_init_settings()
    test_mixer_channels()
    print("\nFor long-running test, run: python3 tests/test_audio.py --long")
    if "--long" in sys.argv:
        test_long_running_audio()
```

### 3.2 Audio Latency Measurement

```python
# Optimal mixer buffer sizes for Pi 5 (trades latency vs. stability):
#
# Buffer 256:  ~5.8ms latency  -- may crackle on Pi 5 under load
# Buffer 512:  ~11.6ms latency -- RECOMMENDED: good balance
# Buffer 1024: ~23.2ms latency -- safe fallback if crackling occurs
# Buffer 2048: ~46.4ms latency -- very safe but noticeable lag
#
# Formula: latency_ms = buffer_size / sample_rate * 1000
#
# To test: run the game with each buffer size and listen for crackles
# during heavy particle/effect scenes. Start at 512, go up if needed.

# In game init:
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
```

### 3.3 Music Crossfade

```python
class MusicManager:
    """
    Handles background music with smooth crossfading.
    Uses pygame.mixer.music for the main track and a Sound channel for crossfade.
    """
    def __init__(self):
        self.current_track = None
        self.fade_duration = 1000  # ms

    def play(self, track_path, loops=-1):
        """Start playing a track, crossfading from current."""
        if self.current_track == track_path:
            return

        if self.current_track:
            pygame.mixer.music.fadeout(self.fade_duration)
            pygame.time.wait(self.fade_duration // 2)  # Overlap

        pygame.mixer.music.load(track_path)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(loops, fade_ms=self.fade_duration)
        self.current_track = track_path

    def stop(self, fade_ms=1000):
        pygame.mixer.music.fadeout(fade_ms)
        self.current_track = None
```

---

## 4. Visual Validation

### 4.1 Frame Rate Consistency and Drop Detection

```python
class FrameDropDetector:
    """
    Detects frame drops and logs them.
    A "drop" is any frame that takes more than 1.5x the target frame time.
    """
    def __init__(self, target_fps=60, log_path="logs/frame_drops.log"):
        self.target_ms = 1000.0 / target_fps
        self.threshold_ms = self.target_ms * 1.5  # 25ms for 60fps
        self.drops = []
        self.total_frames = 0
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def check(self, dt_ms):
        """Call with the actual frame time in ms. Returns True if dropped."""
        self.total_frames += 1
        if dt_ms > self.threshold_ms:
            drop = {
                "frame": self.total_frames,
                "dt_ms": dt_ms,
                "severity": dt_ms / self.target_ms,
            }
            self.drops.append(drop)
            return True
        return False

    def get_summary(self):
        """Returns a summary of frame drop statistics."""
        if self.total_frames == 0:
            return "No frames recorded"
        drop_rate = len(self.drops) / self.total_frames * 100
        return (f"Total frames: {self.total_frames}, "
                f"Drops: {len(self.drops)} ({drop_rate:.1f}%), "
                f"Worst: {max(d['dt_ms'] for d in self.drops):.1f}ms"
                if self.drops else
                f"Total frames: {self.total_frames}, Drops: 0 (0.0%)")

    def save_log(self):
        with open(self.log_path, "w") as f:
            f.write(f"Frame Drop Report\n")
            f.write(f"Total frames: {self.total_frames}\n")
            f.write(f"Drops: {len(self.drops)}\n\n")
            for d in self.drops:
                f.write(f"Frame {d['frame']}: {d['dt_ms']:.1f}ms "
                        f"({d['severity']:.1f}x target)\n")
```

### 4.2 Alpha Blending Performance

The current `spark.py` is VERY heavy on alpha blending. Every particle creates a temporary `SRCALPHA` surface every frame. On the Pi 5's VideoCore VII GPU, this is CPU-bound (Pygame does alpha blending in software, not GPU).

**Critical optimization for the jello character + particles:**

```python
# PROBLEM in current spark.py draw_castle_bg():
# Lines 487-492 draw a per-pixel gradient using pygame.draw.line() for EVERY
# scanline (720 lines). This is extremely expensive.

# FIX: Pre-render the background gradient ONCE and cache it:
class CachedBackground:
    """Pre-renders the static parts of the background."""
    def __init__(self):
        self.static_bg = pygame.Surface((SCREEN_W, SCREEN_H))
        self._render_gradient()
        self._render_stone_wall()
        self._render_floor()
        # Torches, vines, and particles are dynamic -- draw each frame

    def _render_gradient(self):
        for y in range(SCREEN_H):
            ratio = y / SCREEN_H
            r = int(DEEP_STONE[0] + (WARM_STONE[0] - DEEP_STONE[0]) * ratio * 0.5)
            g = int(DEEP_STONE[1] + (WARM_STONE[1] - DEEP_STONE[1]) * ratio * 0.5)
            b = int(DEEP_STONE[2] + (WARM_STONE[2] - DEEP_STONE[2]) * ratio * 0.5)
            pygame.draw.line(self.static_bg, (r, g, b), (0, y), (SCREEN_W, y))

    def _render_stone_wall(self):
        # Render the brick pattern once (without random variation)
        for row in range(0, GROUND_Y, 40):
            offset = 20 if (row // 40) % 2 == 0 else 0
            for col in range(-40 + offset, SCREEN_W + 40, 80):
                pygame.draw.rect(self.static_bg, WARM_STONE, (col, row, 78, 38))
                pygame.draw.rect(self.static_bg, DEEP_STONE, (col, row, 78, 38), 1)

    def _render_floor(self):
        pygame.draw.rect(self.static_bg, DARK_FLOOR,
                         (0, GROUND_Y, SCREEN_W, SCREEN_H - GROUND_Y))
        pygame.draw.line(self.static_bg, STONE_HIGHLIGHT,
                         (0, GROUND_Y), (SCREEN_W, GROUND_Y), 2)
        for fx in range(0, SCREEN_W, 60):
            pygame.draw.line(self.static_bg, (30, 25, 45),
                             (fx, GROUND_Y), (fx, SCREEN_H), 1)

    def draw(self, target):
        target.blit(self.static_bg, (0, 0))
        # Then draw dynamic elements (torches, vines) on top
```

### 4.3 Screen Tearing

Pygame on Pi 5 with Wayland:

```python
# Screen tearing prevention:
# Option 1: Use pygame.SCALED flag (already in spark.py -- good!)
# This uses SDL2's built-in scaling renderer which can use vsync.

# Option 2: Force vsync via SDL hints BEFORE pygame.init():
import os
os.environ["SDL_RENDER_VSYNC"] = "1"
os.environ["SDL_HINT_RENDER_VSYNC"] = "1"

# Option 3: Use DOUBLEBUF flag
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H),
                                  pygame.SCALED | pygame.FULLSCREEN | pygame.DOUBLEBUF)

# Note: On Pi 5 with Wayland, the compositor typically handles vsync.
# If tearing is visible, try:
# 1. Set SDL_VIDEODRIVER=wayland (or x11 as fallback)
# 2. Ensure the Pi 5 display refresh rate matches 60Hz in raspi-config
```

### 4.4 HDMI Output Validation

```
HDMI TEST CHECKLIST (do this with the ACTUAL exhibition TV/monitor)
==================================================================

[ ] 1. Connect Pi 5 to exhibition monitor via HDMI
[ ] 2. Boot Pi -- verify display appears (no black screen)
[ ] 3. Run: python3 game/spark.py
[ ] 4. Verify fullscreen fills the entire screen (no black bars)
[ ] 5. Verify colors look correct (not washed out, not oversaturated)
[ ] 6. Verify text is readable from 3 feet away
[ ] 7. Verify no screen tearing during fast movement
[ ] 8. Test HDMI hot-plug: unplug HDMI, plug back in -- does game survive?
[ ] 9. Check resolution: raspi-config -> Display -> Resolution
       (should match monitor's native resolution or 1920x1080)
[ ] 10. If game renders at 1280x720, the SCALED flag will upscale --
        verify it looks sharp, not blurry

If the monitor is 1080p and game is 720p:
- pygame.SCALED handles upscaling automatically via SDL2
- Should look clean since 720p scales to 1080p with integer-ish ratio
- If blurry, consider rendering at 1080p natively (test FPS impact first)
```

---

## 5. Exhibition-Specific Testing

### 5.1 Idle Timeout / Attract Mode

If nobody plays for several minutes, the game should reset to the title screen with an eye-catching attract mode.

```python
class AttractMode:
    """
    After IDLE_TIMEOUT seconds of no input, return to title screen
    and run an auto-demo that shows off the game.
    """
    IDLE_TIMEOUT = 120  # 2 minutes of no input

    def __init__(self):
        self.last_input_time = time.time()
        self.attract_active = False

    def register_input(self):
        """Call whenever any input is received."""
        self.last_input_time = time.time()
        self.attract_active = False

    def check_idle(self):
        """Returns True if we should switch to attract mode."""
        idle = time.time() - self.last_input_time
        if idle > self.IDLE_TIMEOUT:
            self.attract_active = True
            return True
        return False

    def get_idle_seconds(self):
        return time.time() - self.last_input_time
```

### 5.2 Auto-Restart on Crash (Watchdog Script)

This is CRITICAL for the exhibition. If the game crashes for any reason, it should restart automatically within seconds.

**`scripts/watchdog.sh`:**

```bash
#!/bin/bash
# Split Game Watchdog
# Keeps the game running. If it crashes, restarts it automatically.
# Usage: bash scripts/watchdog.sh
#
# This should be the ONLY thing that runs at exhibition.

GAME_DIR="$HOME/quest-craft"
GAME_CMD="python3 $GAME_DIR/game/spark.py"
LOG_DIR="$GAME_DIR/logs"
RESTART_DELAY=3
MAX_RAPID_RESTARTS=5
RAPID_WINDOW=60  # seconds

mkdir -p "$LOG_DIR"

declare -a restart_times

echo "=== Split Watchdog Started $(date) ===" | tee -a "$LOG_DIR/watchdog.log"

while true; do
    echo "[$(date +%H:%M:%S)] Starting game..." | tee -a "$LOG_DIR/watchdog.log"

    # Run the game, capture stderr to crash log
    $GAME_CMD 2>> "$LOG_DIR/crash.log"
    EXIT_CODE=$?

    echo "[$(date +%H:%M:%S)] Game exited with code $EXIT_CODE" | tee -a "$LOG_DIR/watchdog.log"

    # Check if this was a clean exit (ESC pressed / quit button)
    # Exit code 0 = clean exit, restart anyway for exhibition
    # Exit code non-0 = crash

    if [ $EXIT_CODE -ne 0 ]; then
        echo "[$(date +%H:%M:%S)] CRASH DETECTED (exit code $EXIT_CODE)" | tee -a "$LOG_DIR/watchdog.log"
        echo "--- Last 20 lines of crash.log ---" >> "$LOG_DIR/watchdog.log"
        tail -20 "$LOG_DIR/crash.log" >> "$LOG_DIR/watchdog.log"
        echo "---" >> "$LOG_DIR/watchdog.log"
    fi

    # Rapid restart protection
    NOW=$(date +%s)
    restart_times+=($NOW)

    # Count restarts in the last RAPID_WINDOW seconds
    recent=0
    for t in "${restart_times[@]}"; do
        if [ $((NOW - t)) -lt $RAPID_WINDOW ]; then
            recent=$((recent + 1))
        fi
    done

    if [ $recent -ge $MAX_RAPID_RESTARTS ]; then
        echo "[$(date +%H:%M:%S)] TOO MANY RAPID RESTARTS ($recent in ${RAPID_WINDOW}s)" \
            | tee -a "$LOG_DIR/watchdog.log"
        echo "Waiting 30 seconds before trying again..." | tee -a "$LOG_DIR/watchdog.log"
        sleep 30
        restart_times=()  # Reset
    fi

    echo "[$(date +%H:%M:%S)] Restarting in ${RESTART_DELAY}s..." | tee -a "$LOG_DIR/watchdog.log"
    sleep $RESTART_DELAY
done
```

### 5.3 Kiosk Mode Setup

Prevent accidental escape to the desktop. The game should be the ONLY thing visible.

**`scripts/kiosk_setup.sh`:**

```bash
#!/bin/bash
# Kiosk mode for Split at the exhibition
# Sets up the Pi to boot directly into the game with no desktop visible.

echo "=== Split Kiosk Setup ==="
echo ""
echo "This will configure the Pi to:"
echo "  1. Auto-start the game on boot"
echo "  2. Disable screen blanking"
echo "  3. Hide the desktop taskbar"
echo ""

# 1. Create systemd service for auto-start
WATCHDOG_SERVICE="[Unit]
Description=Split Game Watchdog
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=mark
Environment=DISPLAY=:0
Environment=XDG_RUNTIME_DIR=/run/user/1000
WorkingDirectory=/home/mark/quest-craft
ExecStart=/bin/bash /home/mark/quest-craft/scripts/watchdog.sh
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target"

echo "Creating systemd service file..."
echo "NOTE: Run these commands manually (requires sudo):"
echo ""
echo "sudo tee /etc/systemd/user/split-game.service << 'EOF'"
echo "$WATCHDOG_SERVICE"
echo "EOF"
echo ""
echo "systemctl --user enable split-game.service"
echo "systemctl --user start split-game.service"
echo ""

# 2. Disable screen blanking
echo "To disable screen blanking:"
echo "  xset s off"
echo "  xset -dpms"
echo "  xset s noblank"
echo ""

# 3. Alternative: use .bashrc auto-start for simpler setup
echo "SIMPLER OPTION: Add to ~/.bashrc or ~/.profile:"
echo '  if [ "$(tty)" = "/dev/tty1" ]; then'
echo '    bash ~/quest-craft/scripts/watchdog.sh'
echo '  fi'
echo ""

echo "=== Kiosk setup instructions complete ==="
```

### 5.4 Power Cycle Recovery

**Test procedure:**

```
POWER CYCLE TEST
================
[ ] 1. Pi is running the game via watchdog.sh
[ ] 2. Pull the power cable (simulate power failure)
[ ] 3. Wait 10 seconds
[ ] 4. Plug power back in
[ ] 5. VERIFY: Pi boots to desktop (auto-login should be on)
[ ] 6. VERIFY: Game starts automatically (if kiosk mode is set up)
         OR manually: bash ~/quest-craft/scripts/watchdog.sh
[ ] 7. VERIFY: Controller reconnects (may need to press Home button)
[ ] 8. VERIFY: Game is fully playable
[ ] 9. Check logs for corruption: ls -la ~/quest-craft/logs/

IMPORTANT: The Pi 5 uses an SD card. Sudden power loss CAN corrupt the
filesystem. To reduce risk:
- Use a quality SD card (SanDisk Extreme or Samsung EVO)
- Enable filesystem journal: (already default on ext4)
- Consider making the SD card read-only for exhibition day
  (mount -o remount,ro /) -- but this prevents logging
- Keep a backup SD card ready with the game pre-loaded
```

### 5.5 Extended Play Testing (4-Hour Soak Test)

```bash
#!/bin/bash
# scripts/soak_test.sh
# Run the game for 4+ hours while monitoring system health.
# Run this at least once before exhibition day.

LOG_DIR="$HOME/quest-craft/logs"
mkdir -p "$LOG_DIR"
SOAK_LOG="$LOG_DIR/soak_test_$(date +%Y%m%d_%H%M%S).log"

echo "=== 4-Hour Soak Test Started $(date) ===" | tee "$SOAK_LOG"

# Start thermal monitoring in background
(
    while true; do
        TEMP=$(vcgencmd measure_temp 2>/dev/null | grep -oP '[0-9]+\.[0-9]+' || echo "N/A")
        THROTTLE=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2 || echo "N/A")
        MEM_FREE=$(free -m | awk '/Mem:/{print $4}')
        echo "[$(date +%H:%M:%S)] temp=${TEMP}C throttle=$THROTTLE free_mem=${MEM_FREE}MB"
        sleep 30
    done
) >> "$SOAK_LOG" &
MONITOR_PID=$!

# Start the game
echo "Starting game..." | tee -a "$SOAK_LOG"
python3 "$HOME/quest-craft/game/spark.py" 2>> "$SOAK_LOG"
GAME_EXIT=$?

# Stop monitoring
kill $MONITOR_PID 2>/dev/null

echo "=== Soak Test Complete $(date) ===" | tee -a "$SOAK_LOG"
echo "Game exit code: $GAME_EXIT" | tee -a "$SOAK_LOG"

# Analyze results
echo ""
echo "=== Analysis ==="
if grep -q "CRITICAL" "$SOAK_LOG"; then
    echo "CRITICAL thermal events detected!"
    grep "CRITICAL" "$SOAK_LOG"
fi

if grep -q "THROTTLE FLAG" "$SOAK_LOG"; then
    echo "Throttling occurred!"
    grep "THROTTLE FLAG" "$SOAK_LOG"
fi

echo "Log saved to: $SOAK_LOG"
```

### 5.6 State Leak Between Players

When one player finishes and another starts, the game must be completely fresh:

```python
def gameplay():
    """
    Each call to gameplay() is a fresh play session.
    ALL state must be created fresh here -- never use global mutable state.
    """
    # GOOD: Fresh state every time
    player = JelloCube(100, GROUND_Y - 50)
    particles = []         # Fresh list
    projectiles = []       # Fresh list
    shockwaves = []        # Fresh list
    score = 0              # Fresh score
    collectibles = [...]   # Fresh collectibles

    # BAD: Using global lists that persist between calls
    # global particles  <-- NEVER DO THIS

    # VERIFY: When gameplay() returns (ESC/Plus pressed), everything
    # is garbage collected. Title screen runs. New gameplay() = new state.
```

**The current `spark.py` structure is CORRECT for this** -- `gameplay()` creates all state locally, and when it returns, Python garbage collects everything. The `while True` loop in `main()` then calls `title_screen()` and a fresh `gameplay()`. This is the right pattern.

---

## 6. Automated Test Framework

### 6.1 Project Test Structure

```
quest-craft/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared pytest fixtures
│   ├── test_performance.py      # FPS benchmarks (Section 1.6)
│   ├── test_memory_leak.py      # Memory leak detection (Section 1.3)
│   ├── test_audio.py            # Audio validation (Section 3)
│   ├── test_button_mapping.py   # Controller verification (Section 2.4)
│   ├── test_controller_stability.py  # Long-running controller test (Section 2.1)
│   ├── test_input_lag.py        # Input latency measurement (Section 2.3)
│   ├── test_gameplay.py         # Automated gameplay tests
│   ├── test_state_reset.py      # State leak detection
│   └── test_visual_regression.py # Screenshot comparison
├── logs/                        # Test output (gitignored)
│   ├── perf.csv
│   ├── frame_drops.log
│   ├── thermal.log
│   ├── crash.log
│   └── watchdog.log
```

### 6.2 Shared Test Fixtures -- `tests/conftest.py`

```python
"""
Shared pytest fixtures for Split game tests.
"""
import pytest
import pygame
import sys
import os

# Add game directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "game"))


@pytest.fixture(scope="session")
def pygame_init():
    """Initialize pygame once for the entire test session."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"  # Headless mode for CI
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def screen(pygame_init):
    """Provide a display surface."""
    # Try real display first, fall back to dummy
    try:
        s = pygame.display.set_mode((1280, 720))
    except pygame.error:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        s = pygame.display.set_mode((1280, 720))
    return s


@pytest.fixture
def clock():
    return pygame.time.Clock()
```

### 6.3 Headless Testing on Pi 5

Pygame CAN run headless using the SDL2 "dummy" video driver:

```bash
# Run tests without a display (works over SSH):
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -m pytest tests/ -v

# However, this disables:
# - Actual rendering (blitting still works, just not displayed)
# - Hardware acceleration
# - HDMI output testing
#
# For full visual testing, you need a display (real or virtual):
# Option 1: Use the Pi's connected monitor
# Option 2: Use Xvfb (X Virtual Framebuffer):
#   sudo apt install xvfb
#   xvfb-run python3 -m pytest tests/ -v
# Option 3: Use wayvnc (already set up for this project)
```

### 6.4 Automated Gameplay Tests

```python
"""
tests/test_gameplay.py
Simulated gameplay tests -- verify game mechanics work correctly.
"""
import pygame
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "game"))


class FakeKeys:
    """Simulates pygame.key.get_pressed() return value."""
    def __init__(self):
        self._pressed = {}

    def press(self, key):
        self._pressed[key] = True

    def release(self, key):
        self._pressed[key] = False

    def __getitem__(self, key):
        return self._pressed.get(key, False)


@pytest.fixture
def player():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from spark import JelloCube, GROUND_Y
    p = JelloCube(100, GROUND_Y - 50)
    yield p
    pygame.quit()


def test_player_starts_on_ground(player):
    """Player should start at ground level."""
    from spark import GROUND_Y
    keys = FakeKeys()
    platforms = []
    player.update(keys, platforms)
    # After one frame of gravity, player should land on ground
    for _ in range(60):  # Simulate 1 second
        player.update(keys, platforms)
    assert player.on_ground, "Player should be on ground after settling"
    assert player.y + player.h == GROUND_Y, "Player bottom should be at GROUND_Y"


def test_player_jump(player):
    """Player should be able to jump."""
    from spark import GROUND_Y
    keys = FakeKeys()
    platforms = []

    # Let player settle on ground
    for _ in range(60):
        player.update(keys, platforms)

    assert player.on_ground

    # Press jump
    initial_y = player.y
    keys.press(pygame.K_UP)
    player.update(keys, platforms)
    keys.release(pygame.K_UP)

    # Player should have negative vy (going up)
    assert player.vy < 0, "Jump should give negative vertical velocity"
    assert not player.on_ground, "Player should leave ground after jump"


def test_player_move_right(player):
    keys = FakeKeys()
    platforms = []

    initial_x = player.x
    keys.press(pygame.K_RIGHT)
    for _ in range(10):
        player.update(keys, platforms)

    assert player.x > initial_x, "Player should move right"
    assert player.facing == 1, "Player should face right"


def test_player_move_left(player):
    keys = FakeKeys()
    platforms = []
    player.x = 200  # Start away from left wall

    initial_x = player.x
    keys.press(pygame.K_LEFT)
    for _ in range(10):
        player.update(keys, platforms)

    assert player.x < initial_x, "Player should move left"
    assert player.facing == -1, "Player should face left"


def test_player_wall_clamp(player):
    keys = FakeKeys()
    platforms = []

    # Push against left wall
    player.x = 0
    keys.press(pygame.K_LEFT)
    for _ in range(60):
        player.update(keys, platforms)

    assert player.x >= 0, "Player should not go past left wall"


def test_jello_shot(player):
    """Shooting should create a projectile and shrink the player."""
    initial_w = player.w
    proj = player.shoot()

    assert proj is not None, "Should create a projectile"
    assert proj.direction == player.facing, "Projectile should face same direction"
    assert player.w < initial_w, "Shooting should shrink the player"


def test_jello_shot_minimum_size(player):
    """Player should not shoot when too small."""
    player.w = 15
    player.h = 15
    proj = player.shoot()
    assert proj is None, "Should not shoot when too small"


def test_split_mechanic(player):
    """Split should halve the player and create ghost pieces."""
    initial_w = player.w
    result = player.split()

    assert result is True
    assert player.is_split is True
    assert player.w < initial_w, "Player should be smaller when split"
    assert len(player.split_pieces) == 3, "Should have 3 ghost pieces"


def test_unsplit(player):
    """Unsplitting should restore original size."""
    original_w = player.w
    player.split()
    player.unsplit()

    assert player.is_split is False
    assert player.w == original_w
    assert len(player.split_pieces) == 0


def test_split_timer_expires(player):
    """Split should auto-expire after split_duration frames."""
    from spark import GROUND_Y
    keys = FakeKeys()
    platforms = []

    player.split()
    assert player.is_split

    # Run for split_duration + 1 frames
    for _ in range(player.split_duration + 1):
        player.update(keys, platforms)

    assert not player.is_split, "Split should expire after duration"


def test_ground_pound(player):
    """Ground pound should only work while airborne."""
    # On ground: should not work
    player.on_ground = True
    player.start_ground_pound()
    assert not player.ground_pounding, "Ground pound should not work on ground"

    # In air: should work
    player.on_ground = False
    player.start_ground_pound()
    assert player.ground_pounding, "Ground pound should work in air"
    assert player.vy == 20, "Ground pound should set fast downward velocity"


def test_collectible_pickup(player):
    from spark import Collectible
    c = Collectible(player.x + player.w // 2, player.y + player.h // 2)

    assert c.check_collect(player.x, player.y, player.w, player.h), \
        "Collectible at player position should be collected"


def test_collectible_not_collected_when_far():
    from spark import Collectible
    c = Collectible(1000, 100)
    assert not c.check_collect(100, 400, 40, 40), \
        "Far away collectible should not be collected"


def test_grow_after_collect(player):
    """Collecting jello powder should grow the player."""
    player.w = 30
    player.h = 30
    player.grow(3)
    assert player.w == 33
    assert player.h == 33


def test_grow_capped_at_base_size(player):
    """Growth should cap at base size."""
    player.grow(100)
    assert player.w == player.base_w
    assert player.h == player.base_h
```

### 6.5 State Reset Test

```python
"""
tests/test_state_reset.py
Verify that multiple gameplay sessions do not leak state.
"""
import pygame
import sys
import os
import gc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "game"))


def test_no_global_state_leak():
    """
    Run gameplay initialization twice. Memory should not grow significantly.
    This catches global lists, caches, or singletons that accumulate.
    """
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.set_mode((1280, 720))

    import resource
    from spark import JelloCube, Particle, Collectible, GROUND_Y, JELLO_GREEN

    # Simulate 10 "play sessions"
    mem_readings = []

    for session in range(10):
        # Create fresh state (like gameplay() does)
        player = JelloCube(100, GROUND_Y - 50)
        particles = [Particle(100, 100, JELLO_GREEN) for _ in range(100)]
        collectibles = [Collectible(200, 200) for _ in range(7)]
        projectiles = []
        shockwaves = []

        # Simulate a few frames
        keys = type('FakeKeys', (), {'__getitem__': lambda self, k: False})()
        for _ in range(120):
            player.update(keys, [])
            particles = [p for p in particles if p.update()]
            for c in collectibles:
                c.update()

        # "End session" - clear references
        del player, particles, collectibles, projectiles, shockwaves
        gc.collect()

        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        mem_readings.append(mem)

    pygame.quit()

    # Memory should be roughly flat
    growth = mem_readings[-1] - mem_readings[0]
    print(f"Memory readings (MB): {[f'{m:.0f}' for m in mem_readings]}")
    print(f"Growth over 10 sessions: {growth:.1f}MB")
    assert growth < 20, f"Memory grew {growth:.1f}MB over 10 sessions -- possible leak"
```

### 6.6 Visual Regression Testing (Screenshot Comparison)

```python
"""
tests/test_visual_regression.py
Take screenshots of specific game states and compare to baselines.
"""
import pygame
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "game"))

BASELINE_DIR = os.path.join(os.path.dirname(__file__), "baselines")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "logs", "screenshots")


def capture_screenshot(setup_fn, name):
    """Run setup_fn, capture the screen, save to OUTPUT_DIR."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))

    setup_fn(screen)
    pygame.display.flip()

    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    pygame.image.save(screen, path)
    pygame.quit()
    return path


def compare_screenshots(baseline_path, current_path, threshold=0.02):
    """
    Compare two screenshots. Returns True if they are similar enough.
    threshold = max allowed percentage of different pixels.
    """
    pygame.init()
    baseline = pygame.image.load(baseline_path)
    current = pygame.image.load(current_path)

    if baseline.get_size() != current.get_size():
        pygame.quit()
        return False

    w, h = baseline.get_size()
    diff_count = 0
    total = w * h

    for x in range(0, w, 4):  # Sample every 4th pixel for speed
        for y in range(0, h, 4):
            c1 = baseline.get_at((x, y))
            c2 = current.get_at((x, y))
            # Allow small color differences (anti-aliasing, timing)
            if (abs(c1[0] - c2[0]) > 10 or
                abs(c1[1] - c2[1]) > 10 or
                abs(c1[2] - c2[2]) > 10):
                diff_count += 1

    sampled_total = (w // 4) * (h // 4)
    diff_ratio = diff_count / sampled_total if sampled_total > 0 else 0

    pygame.quit()
    return diff_ratio < threshold


def save_baseline(name):
    """Promote a current screenshot to baseline. Run manually."""
    src = os.path.join(OUTPUT_DIR, f"{name}.png")
    dst = os.path.join(BASELINE_DIR, f"{name}.png")
    os.makedirs(BASELINE_DIR, exist_ok=True)
    if os.path.exists(src):
        import shutil
        shutil.copy2(src, dst)
        print(f"Baseline saved: {dst}")
```

### 6.7 Test Runner Script

```bash
#!/bin/bash
# scripts/run_tests.sh
# Run the full test suite.
# Usage: bash scripts/run_tests.sh

set -e

echo "=== Split Test Suite ==="
echo ""

# Ensure we are in the project root
cd ~/quest-craft

# Create logs directory
mkdir -p logs

# 1. Unit & gameplay tests (headless)
echo "[1/4] Running unit tests..."
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -m pytest tests/test_gameplay.py -v 2>&1 | tee logs/test_unit.log
echo ""

# 2. State reset tests
echo "[2/4] Running state reset tests..."
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -m pytest tests/test_state_reset.py -v 2>&1 | tee logs/test_state.log
echo ""

# 3. Performance tests (needs display)
echo "[3/4] Running performance tests..."
python3 -m pytest tests/test_performance.py -v 2>&1 | tee logs/test_perf.log
echo ""

# 4. Controller check (needs connected controller)
echo "[4/4] Running controller verification..."
python3 tests/test_button_mapping.py 2>&1 | tee logs/test_controller.log
echo ""

echo "=== All Tests Complete ==="
echo "Logs saved to logs/"
```

---

## 7. Validation Checklist

### 7.1 Pre-Exhibition Checklist (T minus 7 days)

```
WEEK BEFORE EXHIBITION
======================

HARDWARE
[ ] Pi 5 has active cooler installed and fan working
[ ] Pi 5 power supply is official 27W USB-C (not a phone charger)
[ ] SD card is backed up (full disk image with dd or rpi-imager)
[ ] Spare SD card with game pre-loaded
[ ] HDMI cable tested with exhibition monitor (or same model)
[ ] Pro Controller fully charged (USB-C charge overnight)
[ ] Spare Pro Controller or Joy-Cons as backup
[ ] USB keyboard as emergency backup input
[ ] Extension cord / power strip for exhibition table
[ ] Cable ties / tape to secure cables

SOFTWARE
[ ] Run full test suite: bash scripts/run_tests.sh
[ ] Run 4-hour soak test: bash scripts/soak_test.sh
[ ] Run controller stability test for 1+ hours
[ ] Run stress test: python3 tests/stress_test.py
[ ] Verify watchdog auto-restart works (kill the game, watch it restart)
[ ] Verify power cycle recovery (unplug Pi, plug back in)
[ ] Verify kiosk mode / auto-start
[ ] Game runs at 60fps with no drops during normal gameplay
[ ] Temperature stays under 75C during extended play
[ ] Memory stays stable over 4 hours (no growth > 50MB)
[ ] All controller buttons mapped correctly
[ ] Sound works and is at appropriate volume

GAME QUALITY
[ ] Title screen loads and looks correct
[ ] "Press A to play" works with controller AND keyboard
[ ] All movement works: left, right, jump
[ ] Jello shot works (B button and SPACE)
[ ] Split mechanic works (X button and Z key)
[ ] Ground pound works (stick down, d-pad down, arrow down)
[ ] All collectibles can be picked up
[ ] Score displays correctly
[ ] Plus button / ESC returns to title screen
[ ] Multiple consecutive play sessions work (no state leak)
[ ] Controller disconnect shows warning, keyboard still works
[ ] Controller reconnect works mid-game
```

### 7.2 Day-Before Checklist (T minus 1 day)

```
DAY BEFORE EXHIBITION
=====================

[ ] Git pull to get latest code on the Pi
[ ] Run the full test suite one more time
[ ] Charge the Pro Controller to 100%
[ ] Charge backup controller to 100%
[ ] Pack everything in a bag:
    [ ] Pi 5 (in case, with power supply)
    [ ] HDMI cable
    [ ] Pro Controller
    [ ] Backup controller
    [ ] USB keyboard
    [ ] Extension cord
    [ ] Cable ties / tape
    [ ] SD card backup (in case)
    [ ] This checklist (printed)
[ ] Set Pi to auto-start game on boot
[ ] Test the full setup at home with a TV (simulate exhibition)
[ ] Run the game for 30 minutes while doing other things
[ ] Make sure the exhibition monitor/TV specs are known:
    - Resolution? (1080p, 4K?)
    - HDMI port number?
    - Does it have speakers? Or need external?
```

### 7.3 Exhibition Morning Checklist (Day of)

```
EXHIBITION MORNING (arrive 30+ minutes early)
==============================================

SETUP (in order)
[ ] Set up table
[ ] Place Pi 5 where it won't be knocked over (behind monitor if possible)
[ ] Connect HDMI to monitor
[ ] Connect power to Pi
[ ] Connect power to monitor
[ ] Turn on monitor -- verify HDMI input is correct
[ ] Boot Pi -- wait for desktop to appear (30 seconds)
[ ] Connect Pro Controller: press Home button, wait for LED to go solid
[ ] Start the game: bash ~/quest-craft/scripts/watchdog.sh
[ ] Verify: game displays on monitor
[ ] Verify: controller works (move around, jump, shoot)
[ ] Verify: sound works and volume is good (not too loud for exhibition hall)
[ ] Secure cables with tape so visitors don't trip

QUICK PLAY TEST
[ ] Play for 2 minutes
[ ] Jump, shoot, split, ground pound -- all work?
[ ] Collect some items
[ ] Press Plus to return to title
[ ] New game starts fresh?
[ ] Disconnect controller briefly -- warning shows?
[ ] Reconnect controller -- works again?

YOU ARE READY!
```

### 7.4 Day-Of Troubleshooting Guide

```
TROUBLESHOOTING GUIDE -- Keep This Printed at the Exhibition Table
==================================================================

GAME WON'T START
  1. Is the Pi powered on? (green LED on board)
  2. Is the monitor on the right HDMI input?
  3. Try: Open terminal (Ctrl+Alt+T), type:
     python3 ~/quest-craft/game/spark.py
  4. If error, read the error message and tell Mark

GAME CRASHED / FROZEN
  1. If watchdog.sh is running, wait 5 seconds -- it auto-restarts
  2. If not, open terminal and run:
     bash ~/quest-craft/scripts/watchdog.sh
  3. If the whole Pi is frozen (no response to keyboard), hold the
     power button for 10 seconds, then turn back on

CONTROLLER NOT WORKING
  1. Press the Home button on the controller
  2. If lights keep flashing (not connecting):
     a. Try pressing SYNC (small button on top near USB-C)
     b. Or plug in USB-C cable temporarily
  3. If controller connects but buttons do wrong things:
     Run: python3 ~/quest-craft/game/test_controller.py
  4. Emergency: use the USB keyboard (arrow keys + SPACE + Z)

NO SOUND
  1. Check monitor/speaker volume
  2. Check HDMI audio: right-click volume icon on Pi desktop
  3. Check Pi volume: amixer set Master 80%

SCREEN IS BLACK
  1. Check HDMI cable on both ends
  2. Try different HDMI port on the monitor
  3. Try rebooting the Pi (unplug power, wait 5 seconds, plug back in)
  4. If Pi shows desktop but game window is black:
     Press ESC, then restart the game

GAME IS STUTTERING / SLOW
  1. Check if Pi is hot (touch the case)
  2. Is the fan running? (listen/look)
  3. Check: vcgencmd measure_temp (should be under 75C)
  4. Close any other programs (browser, file manager)
  5. If still slow, reduce particle effects (if quality toggle is built)

VISITORS KEEP PRESSING ESC / HOME
  1. Remind visitors that Plus = back to menu
  2. If someone exits to desktop, just restart the game:
     bash ~/quest-craft/scripts/watchdog.sh
  3. Consider disabling ESC in the game code before exhibition

EVERYTHING IS BROKEN
  1. Don't panic
  2. Swap SD card with the backup
  3. Reboot the Pi
  4. If nothing works, demonstrate from a laptop via VNC
```

---

## 8. Crash Prevention

### 8.1 Common Pygame Crash Causes on Pi 5

| Crash Cause | Symptom | Prevention |
|---|---|---|
| **Surface too large** | `pygame.error: Out of memory` | Cap surface sizes. Never create a surface larger than screen. |
| **Division by zero in physics** | `ZeroDivisionError` | Guard all divisions: `x / max(1, divisor)` |
| **Accessing dead joystick** | `pygame.error: Invalid joystick` | Always check `self.connected` before `joystick.get_*()` |
| **Mixer not initialized** | `pygame.error: mixer not initialized` | Call `pygame.mixer.init()` with error handling |
| **Too many surfaces** | OOM after hours | Cache/pool surfaces, limit particle count |
| **HDMI disconnect** | `pygame.error: No available video device` | Wrap `display.flip()` in try/except |
| **Unhandled exception in event loop** | Game exits | Wrap entire game loop in try/except |
| **Font rendering with bad characters** | `UnicodeError` | Use ASCII only for game text |
| **File not found (missing assets)** | `FileNotFoundError` | Check all paths at startup, use fallbacks |
| **Bluetooth HID crash** | Kernel log errors | Use stable hid_nintendo driver, avoid rapid connect/disconnect |

### 8.2 Exception Handling Strategy

**Principle: NEVER let the game crash during the exhibition. Catch, log, and recover.**

```python
import logging
import traceback
import os

# Set up logging FIRST
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/split_game.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("split")


def safe_main():
    """
    Top-level exception handler. Catches EVERYTHING and restarts.
    This is the outermost wrapper -- the watchdog.sh script is the
    outer-outermost layer.
    """
    while True:
        try:
            pygame.init()
            # ... game initialization ...
            main()  # The actual game loop
        except SystemExit:
            # Clean exit (sys.exit()) -- let it through
            logger.info("Clean exit")
            break
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt")
            break
        except Exception as e:
            logger.critical(f"UNHANDLED EXCEPTION: {e}")
            logger.critical(traceback.format_exc())
            # Try to clean up pygame
            try:
                pygame.quit()
            except Exception:
                pass
            # Wait a moment then restart
            import time
            time.sleep(2)
            logger.info("Attempting restart after crash...")
            continue
        finally:
            try:
                pygame.quit()
            except Exception:
                pass


def safe_draw(func, *args, **kwargs):
    """Wrapper for draw calls that might fail (e.g., if display is lost)."""
    try:
        func(*args, **kwargs)
    except pygame.error as e:
        logger.warning(f"Draw error (non-fatal): {e}")
    except Exception as e:
        logger.warning(f"Unexpected draw error: {e}")
```

### 8.3 Logging Strategy

```python
# LOG LEVELS:
# DEBUG   -- Frame-by-frame data (only enable during profiling)
# INFO    -- State changes (new game, controller connect, collect item)
# WARNING -- Recoverable issues (frame drop, controller disconnect, draw error)
# ERROR   -- Serious issues that were recovered (exception caught)
# CRITICAL -- Game-ending issues (crash, out of memory)

# In-game logging examples:
logger.info("Game started")
logger.info(f"Controller connected: {joystick.get_name()}")
logger.warning(f"Controller disconnected")
logger.warning(f"Frame drop: {dt_ms:.0f}ms (target 16.67ms)")
logger.info(f"Player collected jello powder (score: {score})")
logger.error(f"Failed to load sound: {e}")
logger.critical(f"Out of memory: {e}")

# Rotate logs to prevent filling the SD card:
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(
    "logs/split_game.log",
    maxBytes=5 * 1024 * 1024,  # 5MB per file
    backupCount=3,              # Keep 3 old files
)
```

### 8.4 Graceful Degradation

When the Pi 5 gets hot or the game is running too many effects, automatically reduce quality instead of dropping frames:

```python
class QualityManager:
    """
    Automatically adjusts visual quality to maintain 60fps.
    Monitors FPS and steps down quality when it drops.
    """
    LEVELS = {
        "ultra": {
            "max_particles": 200,
            "draw_bg_bricks": True,
            "draw_bg_vines": True,
            "draw_trails": True,
            "draw_glow": True,
            "draw_shadows": True,
        },
        "high": {
            "max_particles": 100,
            "draw_bg_bricks": True,
            "draw_bg_vines": True,
            "draw_trails": True,
            "draw_glow": True,
            "draw_shadows": True,
        },
        "medium": {
            "max_particles": 50,
            "draw_bg_bricks": True,
            "draw_bg_vines": False,
            "draw_trails": True,
            "draw_glow": False,
            "draw_shadows": False,
        },
        "low": {
            "max_particles": 20,
            "draw_bg_bricks": False,
            "draw_bg_vines": False,
            "draw_trails": False,
            "draw_glow": False,
            "draw_shadows": True,
        },
    }
    LEVEL_ORDER = ["ultra", "high", "medium", "low"]

    def __init__(self):
        self.current_index = 0  # Start at ultra
        self.fps_history = []
        self.check_interval = 120  # Check every 2 seconds
        self.frame_counter = 0
        self.downgrade_threshold = 50   # FPS below this = downgrade
        self.upgrade_threshold = 58     # FPS above this = upgrade (cautious)
        self.stable_frames_needed = 300 # 5 seconds of stable FPS to upgrade

    @property
    def level(self):
        return self.LEVEL_ORDER[self.current_index]

    @property
    def settings(self):
        return self.LEVELS[self.level]

    def update(self, current_fps):
        self.frame_counter += 1
        self.fps_history.append(current_fps)
        if len(self.fps_history) > 600:
            self.fps_history.pop(0)

        if self.frame_counter < self.check_interval:
            return

        self.frame_counter = 0
        recent = self.fps_history[-self.check_interval:]
        avg_fps = sum(recent) / len(recent) if recent else 60

        if avg_fps < self.downgrade_threshold:
            self._downgrade()
        elif (avg_fps > self.upgrade_threshold and
              len(self.fps_history) >= self.stable_frames_needed):
            # Only upgrade if FPS has been stable for a while
            stable = self.fps_history[-self.stable_frames_needed:]
            if min(stable) > self.upgrade_threshold:
                self._upgrade()

    def _downgrade(self):
        if self.current_index < len(self.LEVEL_ORDER) - 1:
            self.current_index += 1
            logger.warning(f"Quality downgraded to: {self.level}")

    def _upgrade(self):
        if self.current_index > 0:
            self.current_index -= 1
            logger.info(f"Quality upgraded to: {self.level}")
```

---

## 9. Performance Optimization Quick Wins

These are specific optimizations for the CURRENT `spark.py` code that should be applied before the exhibition:

### 9.1 Background Rendering (BIGGEST WIN)

The `draw_castle_bg()` function in `spark.py` (lines 484-548) redraws 720 gradient lines, hundreds of brick rectangles, and vine decorations EVERY SINGLE FRAME. On Pi 5 this is extremely wasteful.

**Fix: Pre-render the static background once, blit it each frame, then draw only dynamic elements (torch flames, vine sway) on top.**

Estimated speedup: 3-5ms per frame (20-30% of the frame budget).

### 9.2 Particle Surface Allocation

Every `Particle.draw()` call (line 70-72) creates a new `pygame.Surface`. With 100 particles, that is 100 Surface allocations per frame.

**Fix: Use a size-bucketed surface cache, or use `pygame.gfxdraw` for direct alpha drawing.**

Estimated speedup: 1-3ms per frame depending on particle count.

### 9.3 Stone Wall Random Noise

Lines 499-503 call `random.randint()` for EVERY brick on EVERY frame, creating subtle color variation. This is invisible to players and wastes time.

**Fix: Pre-render the brick pattern once.**

### 9.4 Vine Random Leaves

Lines 539-541 use `random.random()` for vine leaf placement EVERY frame, making them appear to flicker randomly. This is likely a bug (probably meant to be static).

**Fix: Pre-render vines or use a seeded random for consistent placement.**

---

## 10. Recommended Testing Timeline

| Date | Activity | Duration |
|---|---|---|
| March 9-10 | Integrate PerfMonitor, fix background caching, fix particle allocation | 2-3 hours |
| March 10 | Run automated test suite, fix any failures | 1 hour |
| March 11 | Run stress test on Pi 5, find particle limit | 30 min |
| March 12 | Run 4-hour soak test overnight | 4 hours (unattended) |
| March 12 | Test with actual exhibition monitor/TV | 30 min |
| March 13 | Run full pre-exhibition checklist | 1 hour |
| March 13 | Set up watchdog and kiosk mode | 30 min |
| March 14 | Final soak test + controller stability test | 2 hours |
| March 14 | Back up SD card (full disk image) | 30 min |
| March 15 | Exhibition morning checklist | 30 min |

---

## Summary of Deliverables

| File | Purpose |
|---|---|
| `game/perf_monitor.py` | Real-time FPS/temp/memory overlay |
| `tests/conftest.py` | Shared pytest fixtures |
| `tests/test_gameplay.py` | Automated gameplay mechanics tests |
| `tests/test_performance.py` | Performance regression benchmarks |
| `tests/test_memory_leak.py` | Memory leak detection |
| `tests/test_audio.py` | Audio system validation |
| `tests/test_button_mapping.py` | Controller mapping verification |
| `tests/test_controller_stability.py` | Long-running controller test |
| `tests/test_input_lag.py` | Input latency measurement |
| `tests/test_state_reset.py` | State leak detection between sessions |
| `tests/test_visual_regression.py` | Screenshot comparison |
| `tests/stress_test.py` | Maximum load stress test |
| `scripts/watchdog.sh` | Auto-restart on crash |
| `scripts/thermal_watchdog.sh` | Temperature monitoring |
| `scripts/soak_test.sh` | 4-hour extended test |
| `scripts/run_tests.sh` | Full test suite runner |
| `scripts/kiosk_setup.sh` | Exhibition kiosk configuration |
