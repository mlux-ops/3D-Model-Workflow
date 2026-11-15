#!/bin/bash
# Phase 20 round 2: stills of the stations and design views with the laser-scan surroundings (r.RayTracing.Nanite.Mode 0),
# one view at a time, after review/phase11/scripts/stills_all.sh (no memory floor: owner, 2026-11-14).
#   bash stills_all.sh <tier rt|pt> <samples> <view> [<view> ...]
# Writes review/phase20/stills/<view>_realtime.0000.png or <view>_pathtraced.0000.png; log in review/phase20/round2/stills_driver.log.
DOCS="E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland"
OUT="$DOCS/review/phase20/round2/stills"
LOG="$DOCS/review/phase20/round2/stills_driver.log"
cd "$DOCS" || exit 1
TIER=$1; SAMPLES=$2; shift 2
KIND=realtime; [ "$TIER" = "pt" ] && KIND=pathtraced
for VIEW in "$@"; do
    FILE="$OUT/${VIEW}_${KIND}.0000.png"
    if [ -s "$FILE" ]; then
        echo "$(date +%H:%M:%S) $VIEW has a picture already" >> "$LOG"
        continue
    fi
    echo "{\"views\": [\"$VIEW\"], \"tier\": \"$TIER\", \"samples\": $SAMPLES, \"warm_up_frames\": 64, \"settle\": 30.0}" > "$DOCS/review/phase20/round2/stills_job.json"
    echo "$(date +%H:%M:%S) $VIEW $TIER starts" >> "$LOG"
    START=$(date +%s)
    python -B tools/ue_call.py py review/phase20/round2/scripts/stills_one.py 1500 2>&1 | cut -c1-600 >> "$LOG"
    while [ ! -s "$FILE" ] && [ $(( $(date +%s) - START )) -lt 1800 ]; do
        sleep 20
    done
    sleep 5
    echo "$(date +%H:%M:%S) $VIEW settings put back:" >> "$LOG"
    python -B tools/ue_call.py py review/phase20/round2/scripts/stills_end.py 120 2>&1 | cut -c1-400 >> "$LOG"
    if [ ! -s "$FILE" ]; then
        echo "$(date +%H:%M:%S) $VIEW STOP: no picture after $(( $(date +%s) - START )) s" >> "$LOG"
        exit 3
    fi
    echo "$(date +%H:%M:%S) $VIEW done in $(( $(date +%s) - START )) s, $(stat -c %s "$FILE") bytes" >> "$LOG"
done
echo "$(date +%H:%M:%S) ALL DONE $TIER" >> "$LOG"
