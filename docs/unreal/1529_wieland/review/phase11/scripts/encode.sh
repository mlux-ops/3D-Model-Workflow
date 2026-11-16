#!/bin/bash
# Phase 11, step 11.3: encode the animation with ffmpeg 9.0.2 (already installed, nothing new).
# Each move: frames 0000 to 0899 (PNG, 3,840 by 2,160, 8-bit sRGB) -> H.264, 30 pictures a second, quality CRF 16,
# colour standard BT.709 (limited range, 4:2:0), the form most players and Google Drive's own player show.
# Then the 60-second film: the two moves joined end to end (triplex first) without encoding again.
# Each file is read back with ffprobe: picture count, size, length. Output: D:\Wieland1529_delivery\video\.
set -u
FF=/c/Users/cowey/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin
IN=D:/Wieland1529_delivery/animation_frames
OUT=D:/Wieland1529_delivery/video
mkdir -p "$OUT"
for move in triplex penthouse; do
  name=$( [ $move = triplex ] && echo Triplex || echo Penthouse )
  "$FF/ffmpeg" -hide_banner -loglevel error -y -framerate 30 -start_number 0 -i "$IN/$move/$move.%04d.png" -frames:v 900 \
    -vf "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p" \
    -c:v libx264 -preset slow -crf 16 -profile:v high -level:v 5.2 \
    -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv -movflags +faststart \
    "$OUT/W1529_${name}_30s_3840x2160.mp4" || { echo "encode $move failed"; exit 1; }
done
printf "file 'W1529_Triplex_30s_3840x2160.mp4'\nfile 'W1529_Penthouse_30s_3840x2160.mp4'\n" > "$OUT/concat.txt"
( cd "$OUT" && "$FF/ffmpeg" -hide_banner -loglevel error -y -f concat -safe 0 -i concat.txt -c copy -movflags +faststart W1529_Animation_60s_3840x2160.mp4 ) || { echo "join failed"; exit 1; }
rm -f "$OUT/concat.txt"
for f in "$OUT"/W1529_*.mp4; do
  frames=$("$FF/ffprobe" -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames,width,height,r_frame_rate -show_entries format=duration,size -of compact=p=0:nk=0 "$f" | tr '\n' ' ')
  echo "$(basename "$f"): $frames"
done
