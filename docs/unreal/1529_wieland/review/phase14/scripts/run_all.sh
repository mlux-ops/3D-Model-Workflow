#!/bin/bash
# Phase 14 (run once at a time: a second copy running at the same time corrupts the frames and the MP4s): shoot the other three videos in chunks of 80 frames, then caption and encode each.
cd "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland"
for pair in "roofdeck summer" "reardeck summer" "reardeck winter"; do
  set -- $pair
  for s in 0 80 160; do
    echo "{\"deck\": \"$1\", \"day\": \"$2\", \"start\": $s, \"count\": 80, \"settle\": 1.0}" > review/phase14/scripts/job.json
    python -B tools/ue_call.py py review/phase14/scripts/run_chunk.py 400 2>&1 | tail -1 | cut -c1-260
  done
  python -B review/phase14/scripts/make_video.py $1 $2 2>&1 | tail -1 | cut -c1-400
done
echo ALLDONE
