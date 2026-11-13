#!/bin/bash
# Phase 12, step 12.6: the path-traced ground truth, one view at a time.
#   bash truth_all.sh <view> [<view> ...]
# For each view without a picture: waits until 30 GB of commit memory is free, renders the one view, waits for
# its file when the agent server stays silent, then puts the ray tracing settings back and reads them back.
# Stops at the first view that leaves no picture. Every step is written to ground_truth/driver.log.
DOCS="E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland"
OUT="$DOCS/review/phase12/ground_truth"
LOG="$OUT/driver.log"
cd "$DOCS" || exit 1
free_gb() {
    powershell -NoProfile -Command "[math]::Floor((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory/1MB)" | tr -d '\r'
}
for VIEW in "$@"; do
    FILE="$OUT/${VIEW}_pathtraced.0000.png"
    if [ -s "$FILE" ]; then
        echo "$(date +%H:%M:%S) $VIEW has a picture already" >> "$LOG"
        continue
    fi
    TRIES=0
    FREE=$(free_gb)
    while [ "$FREE" -lt 30 ] && [ "$TRIES" -lt 20 ]; do
        echo "$(date +%H:%M:%S) $VIEW waits: $FREE GB of commit memory free" >> "$LOG"
        sleep 30
        TRIES=$((TRIES + 1))
        FREE=$(free_gb)
    done
    if [ "$FREE" -lt 30 ]; then
        echo "$(date +%H:%M:%S) $VIEW STOP: $FREE GB free after 10 minutes" >> "$LOG"
        exit 2
    fi
    echo "{\"views\": [\"$VIEW\"], \"tier\": \"pt\", \"samples\": 1024}" > "$OUT/job.json"
    echo "$(date +%H:%M:%S) $VIEW starts, $FREE GB free" >> "$LOG"
    START=$(date +%s)
    python -B tools/ue_call.py py review/phase12/scripts/truth_one.py 1500 2>&1 | cut -c1-600 >> "$LOG"
    while [ ! -s "$FILE" ] && [ $(( $(date +%s) - START )) -lt 1800 ]; do
        sleep 20
    done
    sleep 5
    echo "$(date +%H:%M:%S) $VIEW settings put back:" >> "$LOG"
    python -B tools/ue_call.py py review/phase12/scripts/truth_end.py 120 2>&1 | cut -c1-400 >> "$LOG"
    if [ ! -s "$FILE" ]; then
        echo "$(date +%H:%M:%S) $VIEW STOP: no picture after $(( $(date +%s) - START )) s" >> "$LOG"
        exit 3
    fi
    echo "$(date +%H:%M:%S) $VIEW done in $(( $(date +%s) - START )) s, $(stat -c %s "$FILE") bytes" >> "$LOG"
done
echo "$(date +%H:%M:%S) ALL DONE" >> "$LOG"
