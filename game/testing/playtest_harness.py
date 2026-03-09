"""
SPLIT — Automated Playtest Harness

Runs the REAL game loop in test mode across floors, captures screenshots and state logs.
The game's own _run_gameplay() handles everything — this is just a thin wrapper.

Usage:
    python3 -m game.testing.playtest_harness [--floors 1-15] [--duration 30]
"""
import os
import sys
import json
import time
import argparse
import traceback
from datetime import datetime

# Ensure game package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def parse_floor_range(floor_str):
    """Parse '1-15' or '3' into a list of floor numbers."""
    if '-' in floor_str:
        start, end = floor_str.split('-', 1)
        return list(range(int(start), int(end) + 1))
    return [int(floor_str)]


def run_harness(floors, duration_per_floor):
    """Run the automated playtest across specified floors using the real game loop."""

    # Set up output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = os.path.join('playtest_logs', f'run_{timestamp}')
    os.makedirs(run_dir, exist_ok=True)

    # Suppress audio in headless mode
    if os.environ.get('SDL_VIDEODRIVER') == 'dummy':
        os.environ['SDL_AUDIODRIVER'] = 'dummy'

    print(f"=== SPLIT Playtest Harness ===")
    print(f"Output: {run_dir}")
    print(f"Floors: {floors}")
    print(f"Duration per floor: {duration_per_floor}s")
    print()

    start_floor = floors[0]
    max_floor = floors[-1]

    state_log_path = os.path.join(run_dir, 'state_log.jsonl')
    log_file = open(state_log_path, 'w')

    crashed = False
    crash_info = None

    try:
        from game.main import Game

        game = Game(
            test_mode=True,
            test_floor=start_floor,
            test_duration=duration_per_floor,
        )

        # Wire up test logging — the real game loop reads these
        game._test_run_dir = run_dir
        game._test_log_file = log_file
        game._test_max_floor = max_floor
        game._test_floor_start = time.time()

        # Run the real game — this calls _init_systems, _run_title (auto-skip),
        # then _run_gameplay with AI input, screenshots, logging, and floor
        # auto-advance all handled inside the real loop.
        game.run()

    except SystemExit:
        # Normal exit — game._quit() calls sys.exit()
        pass
    except Exception as e:
        crashed = True
        crash_info = {
            'error': str(e),
            'traceback': traceback.format_exc(),
        }
        print(f"CRASH: {e}")
        traceback.print_exc()

    log_file.close()

    # Build summary from state log
    summary = _build_summary(run_dir, timestamp, floors, crashed, crash_info)
    _write_summary(run_dir, summary)
    _print_summary(summary)
    return summary


def _build_summary(run_dir, timestamp, requested_floors, crashed, crash_info):
    """Build summary from state log and screenshot counts."""
    summary = {
        'run_id': timestamp,
        'requested_floors': requested_floors,
        'floors_visited': [],
        'crashes': [],
        'screenshots': 0,
        'total_frames': 0,
    }

    if crash_info:
        summary['crashes'].append(crash_info)

    # Count screenshots across floor dirs
    for entry in os.listdir(run_dir):
        floor_path = os.path.join(run_dir, entry)
        if os.path.isdir(floor_path) and entry.startswith('floor_'):
            floor_num = int(entry.split('_')[1])
            summary['floors_visited'].append(floor_num)
            for f in os.listdir(floor_path):
                if f.endswith('.png'):
                    summary['screenshots'] += 1

    summary['floors_visited'].sort()

    # Parse state log for frame count
    state_log_path = os.path.join(run_dir, 'state_log.jsonl')
    if os.path.exists(state_log_path):
        with open(state_log_path) as f:
            lines = f.readlines()
            if lines:
                try:
                    last = json.loads(lines[-1])
                    summary['total_frames'] = last.get('frame', 0)
                except json.JSONDecodeError:
                    pass

    return summary


def _write_summary(run_dir, summary):
    """Write summary JSON to run directory."""
    with open(os.path.join(run_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2, default=str)


def _print_summary(summary):
    """Print human-readable summary."""
    print()
    print("=== Playtest Summary ===")
    print(f"Floors visited: {summary['floors_visited']}")
    print(f"Total frames: {summary['total_frames']}")
    print(f"Screenshots: {summary['screenshots']}")
    print(f"Crashes: {len(summary['crashes'])}")

    if summary['crashes']:
        print("\nCrash details:")
        for crash in summary['crashes']:
            print(f"  {crash.get('error', 'unknown')}")


def main():
    parser = argparse.ArgumentParser(description="SPLIT Automated Playtest Harness")
    parser.add_argument('--floors', type=str, default='1-3',
                        help='Floor range to test, e.g. "1-15" or "3" (default: 1-3)')
    parser.add_argument('--duration', type=int, default=30,
                        help='Seconds per floor (default: 30)')
    args = parser.parse_args()

    floors = parse_floor_range(args.floors)
    run_harness(floors, args.duration)


if __name__ == '__main__':
    main()
