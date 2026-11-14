#!/bin/bash
# Phase 11, J7: render both camera moves, one after the other, with the settings of the J7 journal line.
# One copy only (checked by the caller). Run from the plan folder; started detached so it outlives a tool call.
# Each move resumes from the frames already on disk (anim_driver.py). Output: D:\Wieland1529_delivery\animation_frames\.
cd "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland" || exit 1
OUT="D:/Wieland1529_delivery/animation_frames"
COMMON="--run 150 --samples 16 --quality 3,4,4 --warm-up 64 --min-free 30"
echo "$(date +%H:%M:%S) anim_both start (pid $$)" >> review/phase11/anim_driver.log
python -B review/phase11/scripts/anim_driver.py triplex SEQ_W1529_Triplex "$OUT/triplex" $COMMON
t=$?
echo "$(date +%H:%M:%S) anim_both: triplex driver ended with $t" >> review/phase11/anim_driver.log
python -B review/phase11/scripts/anim_driver.py penthouse SEQ_W1529_Penthouse "$OUT/penthouse" $COMMON
p=$?
echo "$(date +%H:%M:%S) anim_both: penthouse driver ended with $p; END" >> review/phase11/anim_driver.log
