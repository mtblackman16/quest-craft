"""Analyze harness state_log.jsonl against negative test inventory."""
import json
import sys
import os
from collections import defaultdict

def analyze(run_dir):
    log_path = os.path.join(run_dir, 'state_log.jsonl')
    if not os.path.exists(log_path):
        print(f'No state_log.jsonl in {run_dir}')
        return

    entries = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    if not entries:
        print('Empty log')
        return

    print(f'=== HARNESS ANALYSIS REPORT ===')
    print(f'Entries: {len(entries)}')
    print(f'Floors visited: {sorted(set(e["floor"] for e in entries))}')
    print(f'Total frames: {entries[-1]["frame"]}')
    print()

    # Per-floor analysis
    floors = defaultdict(list)
    for e in entries:
        floors[e['floor']].append(e)

    print('=== PER-FLOOR SUMMARY ===')
    print(f'{"Floor":<6} {"Frames":<8} {"MinFPS":<8} {"MaxFPS":<8} {"AvgFPS":<8} {"MinHP":<7} {"Deaths":<7} {"MaxEnemies":<11} {"MaxProj":<9} {"MaxHaz":<8} {"Anomalies":<10} {"Boss":<6}')
    print('-' * 110)

    total_anomalies = []
    for floor_num in sorted(floors.keys()):
        fl = floors[floor_num]
        fps_vals = [e['fps'] for e in fl if e.get('fps', 0) > 0]
        hp_vals = [e.get('player_health', 100) for e in fl]
        enemy_counts = [e.get('enemies_alive', 0) for e in fl]
        proj_counts = [e.get('player_projectiles', 0) + e.get('enemy_projectiles', 0) for e in fl]
        haz_counts = [e.get('hazards', 0) for e in fl]
        anomalies = [a for e in fl if 'anomalies' in e for a in e['anomalies']]
        deaths = sum(1 for i in range(1, len(fl)) if fl[i].get('player_health', 100) == 100 and fl[i-1].get('player_health', 100) < 50)
        has_boss = any('boss' in e for e in fl)

        min_fps = min(fps_vals) if fps_vals else 0
        max_fps = max(fps_vals) if fps_vals else 0
        avg_fps = sum(fps_vals) // len(fps_vals) if fps_vals else 0
        min_hp = min(hp_vals) if hp_vals else 0

        total_anomalies.extend(anomalies)

        print(f'{floor_num:<6} {len(fl):<8} {min_fps:<8} {max_fps:<8} {avg_fps:<8} {min_hp:<7} {deaths:<7} {max(enemy_counts):<11} {max(proj_counts):<9} {max(haz_counts):<8} {len(anomalies):<10} {"YES" if has_boss else "no":<6}')

    print()

    # Boss encounters
    print('=== BOSS ENCOUNTERS ===')
    for floor_num in sorted(floors.keys()):
        fl = floors[floor_num]
        boss_entries = [e for e in fl if 'boss' in e]
        if boss_entries:
            first = boss_entries[0]['boss']
            last = boss_entries[-1]['boss']
            hp_start = first.get('health', '?')
            hp_end = last.get('health', '?')
            phases_seen = sorted(set(e['boss'].get('phase', 0) for e in boss_entries))
            alive_end = last.get('alive', True)
            print(f'  Floor {floor_num}: {first.get("type","?")} | HP {hp_start}->{hp_end} | Phases: {phases_seen} | Alive at end: {alive_end}')

    print()

    # Anomalies
    if total_anomalies:
        print('=== ANOMALIES DETECTED ===')
        from collections import Counter
        for anomaly, count in Counter(total_anomalies).most_common():
            print(f'  {anomaly}: {count} occurrences')
    else:
        print('=== NO ANOMALIES DETECTED ===')

    print()

    # Performance warnings
    print('=== PERFORMANCE WARNINGS ===')
    low_fps = [(e['floor'], e['frame'], e['fps']) for e in entries if e.get('fps', 60) < 45]
    if low_fps:
        for floor, frame, fps in low_fps[:20]:
            print(f'  Floor {floor}, Frame {frame}: {fps} FPS')
        if len(low_fps) > 20:
            print(f'  ... and {len(low_fps) - 20} more')
    else:
        print('  None (all frames >= 45 FPS)')

    print()

    # Hazard/projectile accumulation
    print('=== ACCUMULATION CHECK ===')
    max_proj = max((e.get('player_projectiles', 0) + e.get('enemy_projectiles', 0) for e in entries), default=0)
    max_haz = max((e.get('hazards', 0) for e in entries), default=0)
    max_plat = max((e.get('platforms', 0) for e in entries), default=0)
    print(f'  Max concurrent projectiles: {max_proj}')
    print(f'  Max concurrent hazards: {max_haz}')
    print(f'  Max platforms on any floor: {max_plat}')

    # Player state anomalies
    print()
    print('=== PLAYER STATE CHECKS ===')
    split_count = sum(1 for e in entries if e.get('player_is_split', False))
    dodge_count = sum(1 for e in entries if e.get('player_dodge_active', False))
    below_screen = sum(1 for e in entries if e.get('player_y', 0) > 720)
    neg_health = sum(1 for e in entries if (e.get('player_health') or 0) < 0)
    print(f'  Frames in split state: {split_count}')
    print(f'  Frames in dodge state: {dodge_count}')
    print(f'  Frames below screen (y>720): {below_screen}')
    print(f'  Frames with negative health: {neg_health}')

    print()
    print('=== DONE ===')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        analyze(sys.argv[1])
    else:
        # Find latest run
        logs_dir = 'playtest_logs'
        runs = sorted(os.listdir(logs_dir))
        if runs:
            analyze(os.path.join(logs_dir, runs[-1]))
        else:
            print('No runs found')
