"""Phase 14: burn the caption into the 240 frames of one video and join them into an H.264 MP4 with ffmpeg.
Usage: python -B make_video.py <deck> <day>     (deck: roofdeck | reardeck, day: summer | winter)
Reads review/phase14/frames/<deck>_<day>/f000..f239.png and meta.json; writes the captioned frames to
frames/<deck>_<day>_cap/ and the video to review/phase14/timelapse_<deck>_<day>.mp4."""
import sys, os, json, subprocess
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
DECK_NAMES = {"roofdeck": "Penthouse roof deck", "reardeck": "Rear patio deck (ground level)"}
FFMPEG = "ffmpeg"


def clock(hour, zone):
    total = int(round(hour * 60))
    return "%02d:%02d %s" % (total // 60, total % 60, zone)


def main(deck, day):
    folder = "%s/frames/%s_%s" % (OUT, deck, day)
    cap = folder + "_cap"
    os.makedirs(cap, exist_ok=True)
    meta = json.load(open(folder + "/meta.json"))
    sr, ss = meta["sun_times_hours"]["sunrise"], meta["sun_times_hours"]["sunset"]
    zone, date = meta["date"]["zone"], meta["date"]["label"]
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    for i in range(240):
        hour = sr + i * (ss - sr) / 239.0
        img = Image.open("%s/f%03d.png" % (folder, i)).convert("RGBA")
        if img.size != (1920, 1080):
            img = img.resize((1920, 1080))
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.rectangle([16, 1080 - 126, 640, 1080 - 16], fill=(0, 0, 0, 150))
        d.text((30, 1080 - 118), "%s  |  %s" % (DECK_NAMES[deck], date), font=small, fill=(255, 255, 255, 255))
        d.text((30, 1080 - 88), clock(hour, zone), font=font, fill=(255, 220, 90, 255))
        d.text((30, 1080 - 46), "proposed hotel shown", font=small, fill=(255, 255, 255, 255))
        Image.alpha_composite(img, layer).convert("RGB").save("%s/f%03d.jpg" % (cap, i), quality=95)
    target = "%s/timelapse_%s_%s.mp4" % (OUT, deck, day)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-framerate", "24", "-i", cap + "/f%03d.jpg", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "20", "-r", "24", "-movflags", "+faststart", target]
    subprocess.run(cmd, check=True)
    probe = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                            "stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration", "-of", "json", target],
                           capture_output=True, text=True, check=True)
    print(target, os.path.getsize(target), probe.stdout.replace("\n", " "))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
