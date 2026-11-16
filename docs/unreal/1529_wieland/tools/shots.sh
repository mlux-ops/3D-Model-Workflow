#!/bin/sh
# Station pictures from the editor: shots.sh "<'S1','S3'>" <folder under review/phase7> <suffix>
# Sets the named quality, takes the pictures, and puts every setting back even when the pictures fail.
cd "$(dirname "$0")/.." || exit 1
python -B tools/ue_call.py ws "ws.json.dumps(ws.shots_begin(3)['now']['sg.ShadowQuality'])"
python -B tools/ue_call.py ws "ws.json.dumps(await ws.shots([$1], ws.REVIEW + '/$2', '$3'))" 900
python -B tools/ue_call.py ws "r = ws.shots_end()
ws.json.dumps([r['cameras_removed'], r['now']['sg.ShadowQuality'], r['now']['t.MaxFPS'], r['now']['r.Streaming.PoolSize'], r['dirty']])"
