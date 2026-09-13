"""Create a repeatable approximation of the fine etched dots in the reference.
This creates new mathematical texture maps; it does not alter source photos.
"""
from pathlib import Path
from PIL import Image, ImageDraw

out = Path(__file__).resolve().parents[1] / 'output/tris/textures'
out.mkdir(parents=True, exist_ok=True)
size = 1024
for name, background, dot in [
    ('Tris_Microdots_Color.png', (222, 225, 221), (250, 251, 247)),
    ('Tris_Microdots_Transmission.png', (180, 180, 180), (65, 65, 65)),
]:
    im = Image.new('RGB', (size, size), background)
    draw = ImageDraw.Draw(im)
    for row in range(-1, 9):
        for col in range(-1, 9):
            x = col * 128 + (64 if row % 2 else 0)
            y = row * 128
            r = 39
            draw.ellipse((x-r, y-r, x+r, y+r), fill=dot)
    im.resize((512,512), Image.Resampling.LANCZOS).save(out / name)
print(out)
