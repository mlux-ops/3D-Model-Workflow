#!/bin/bash
# Phase 11, J7: one path-traced frame of a move, for comparison with the real-time frame of the same number.
#   bash review/phase11/scripts/pt_frame.sh <sequence asset> <move name> <frame> [samples]
# Path Tracer, 3,840 by 2,160, 1,024 samples unless given, 64 warm-up frames as the stills, r.RayTracing.Nanite.Mode 0
# (checked by seq_render.py, never changed). Waits for the file (the editor does not answer while it renders) and logs
# the time. Output: D:\Wieland1529_delivery\animation_frames\pathtraced\<move>_pathtraced.<frame>.png. Run from the plan folder.
set -u
asset=$1; move=$2; frame=$3; samples=${4:-1024}
OUT=D:/Wieland1529_delivery/animation_frames/pathtraced
LOG=review/phase11/anim_driver.log
file=$(printf "%s/%s_pathtraced.%04d.png" "$OUT" "$move" "$frame")
mkdir -p "$OUT"
[ -f "$file" ] && { echo "$file exists; nothing to do"; exit 0; }
free=$(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreeVirtualMemory/1MB,1)")
printf '{"asset": "%s", "name": "%s_pathtraced", "folder": "%s", "start": %d, "end": %d, "tier": "pt", "samples": %d, "warm_up_frames": 64, "anti_aliasing": null}' \
  "$asset" "$move" "$OUT" "$frame" $((frame + 1)) "$samples" > review/phase11/seq_render_job.json
start=$(date +%s)
reply=$(python -B tools/ue_call.py py review/phase11/scripts/seq_render.py 300)
echo "$(date +%H:%M:%S) $move frame $frame path-traced ($samples samples) start, $free GB free: ${reply:0:300}" >> "$LOG"
for i in $(seq 1 270); do [ -f "$file" ] && break; sleep 10; done
sleep 5
if [ -f "$file" ]; then
  echo "$(date +%H:%M:%S) $move frame $frame path-traced: file after $(( $(date +%s) - start )) s" >> "$LOG"
else
  echo "$(date +%H:%M:%S) $move frame $frame path-traced: NO file after $(( $(date +%s) - start )) s" >> "$LOG"; exit 1
fi
for i in $(seq 1 60); do
  s=$(python -B tools/ue_call.py py review/phase11/scripts/state.py 60 2>/dev/null)
  case "$s" in *'\"rendering\": false'*) break;; esac
  sleep 10
done
echo "$(date +%H:%M:%S) $move frame $frame path-traced: editor reports the render ended" >> "$LOG"
