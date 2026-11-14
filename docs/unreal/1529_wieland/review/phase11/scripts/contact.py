"""Phase 11: contact sheet of chosen frames of a move. python -B contact.py <folder> <name> <out.jpg> <frame,frame,...> [cols]"""
import sys
from PIL import Image, ImageDraw
folder, name, out, frames = sys.argv[1], sys.argv[2], sys.argv[3], [int(f) for f in sys.argv[4].split(",")]
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 4
w, h = 480, 270
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), "black")
draw = ImageDraw.Draw(sheet)
for i, f in enumerate(frames):
    with Image.open("%s/%s.%04d.png" % (folder, name, f)) as im:
        tile = im.convert("RGB").resize((w, h), Image.BILINEAR)
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(tile, (x, y))
    draw.text((x + 6, y + 4), "%s %04d" % (name, f), fill="yellow")
sheet.save(out, quality=85)
print(out)
