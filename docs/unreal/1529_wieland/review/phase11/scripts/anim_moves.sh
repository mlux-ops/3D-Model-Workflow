#!/bin/bash
# Phase 11, J7 (from 05:17): render both camera moves, each as one run of 900 frames with 1,024 warm-up frames, so that
# Lumen's bounced light has settled before frame 0 and no run joins sit inside a move. One copy only (checked by the
# caller). An interruption resumes from the first missing frame (anim_driver.py). Started detached from the plan folder.
cd "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland" || exit 1
OUT="D:/Wieland1529_delivery/animation_frames"
COMMON="--run 900 --samples 16 --quality 3,4,4 --warm-up 1024 --min-free 30"
echo "$(date +%H:%M:%S) anim_moves start (pid $$): $COMMON" >> review/phase11/anim_driver.log
python -B review/phase11/scripts/anim_driver.py triplex SEQ_W1529_Triplex "$OUT/triplex" $COMMON
t=$?
echo "$(date +%H:%M:%S) anim_moves: triplex driver ended with $t" >> review/phase11/anim_driver.log
[ $t -eq 0 ] || { echo "$(date +%H:%M:%S) anim_moves: penthouse not started; END" >> review/phase11/anim_driver.log; exit $t; }
python -B review/phase11/scripts/anim_driver.py penthouse SEQ_W1529_Penthouse "$OUT/penthouse" $COMMON
p=$?
echo "$(date +%H:%M:%S) anim_moves: penthouse driver ended with $p; END" >> review/phase11/anim_driver.log
