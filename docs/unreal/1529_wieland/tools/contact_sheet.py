"""Lay images out in a labelled grid. Runs outside the editor (needs Pillow).

Usage:
    python -B contact_sheet.py OUT.png COLUMNS CELL_WIDTH label=path [label=path ...]

A path that does not exist, or the word NONE, gives a grey panel carrying the label and the
words "not available", so a sheet can show honestly that a panel is missing.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont


def _font(size):
    for name in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sheet(out_path, columns, cell_width, items):
    cell_height = int(cell_width * 9 / 16)
    label_height = max(22, cell_width // 28)
    rows = (len(items) + columns - 1) // columns
    page = Image.new("RGB", (columns * cell_width, rows * (cell_height + label_height)), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    font = _font(label_height - 6)
    for index, (label, path) in enumerate(items):
        x = (index % columns) * cell_width
        y = (index // columns) * (cell_height + label_height)
        if path != "NONE" and os.path.isfile(path):
            image = Image.open(path).convert("RGB").resize((cell_width, cell_height), Image.LANCZOS)
            page.paste(image, (x, y + label_height))
        else:
            draw.rectangle([x, y + label_height, x + cell_width - 1, y + label_height + cell_height - 1],
                           fill=(205, 205, 205), outline=(120, 120, 120))
            draw.text((x + 12, y + label_height + cell_height // 2 - 10), "not available", fill=(60, 60, 60), font=font)
        draw.text((x + 6, y + 2), label, fill=(0, 0, 0), font=font)
    page.save(out_path)
    return page.size


if __name__ == "__main__":
    out = sys.argv[1]
    cols = int(sys.argv[2])
    width = int(sys.argv[3])
    pairs = [tuple(arg.split("=", 1)) for arg in sys.argv[4:]]
    print(sheet(out, cols, width, pairs))
