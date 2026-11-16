#!/bin/sh
# Phase 8, step 8.9: one real-time trial. Usage: trial.sh <suffix> '<json of console variables>' '<json list of views>' [settle seconds]
# Renders the views with the console variables set for the renders only (j10_one.py puts them back), then compares.
BASE="E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland"
printf '{"views": %s, "suffix": "%s", "settle": %s, "warm_up_frames": 64, "cvars": %s}' "$3" "$1" "${4:-8.0}" "$2" > "$BASE/review/phase8/realtime/job.json"
cd "$BASE/tools" && python -B ue_call.py py ../review/phase8/scripts/j10_one.py 1500 2>&1 | tail -2 | cut -c1-900
cd "$BASE/review/phase8" && python -B scripts/compare_tiers.py ground_truth realtime compare "$1" 2>&1 | python -c "
import sys, json
for l in sys.stdin:
    try: r = json.loads(l)
    except ValueError: print(l.strip()); continue
    if 'mean_difference_percent' in r:
        print(r['view'], r['mean_difference_percent'], r['largest_region_percent'], 'PASS' if r['passes'] else 'fail', [(f['where'], f['share_of_frame_percent'], f['mean_stops']) for f in r['regions_over_2_percent']])
"
