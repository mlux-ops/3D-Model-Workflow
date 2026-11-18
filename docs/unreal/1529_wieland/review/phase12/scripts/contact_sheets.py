"""Phase 12: contact sheets of the rebuilt swatch pictures, for looking through all of them quickly.

    python -P -B contact_sheets.py <material_rebuild.csv> <rebuilt swatch folder> <output folder> [per page]

Each cell is one swatch picture (wall piece lit from the front, wall piece lit at a grazing angle, ball)
with the material's name and its parent above it.
"""
import csv
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

CELL = (520, 260)
LABEL = 22
COLUMNS = 3


def main(table, folder, out, per_page=15):
    os.makedirs(out, exist_ok=True)
    with open(table, encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["action"] == "rebuilt"]
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    pages = [rows[i:i + per_page] for i in range(0, len(rows), per_page)]
    for number, page in enumerate(pages, 1):
        lines = (len(page) + COLUMNS - 1) // COLUMNS
        sheet = Image.new("RGB", (CELL[0] * COLUMNS, (CELL[1] + LABEL) * lines), (24, 24, 24))
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(page):
            x, y = (index % COLUMNS) * CELL[0], (index // COLUMNS) * (CELL[1] + LABEL)
            path = os.path.join(folder, re.sub(r"[^A-Za-z0-9_-]", "_", row["material"]) + ".png")
            draw.text((x + 4, y + 2), ("%s  [%s]" % (row["material"], row["parent"].rsplit("_", 1)[-1]))[:68],
                      fill=(255, 255, 255), font=font)
            if os.path.exists(path):
                sheet.paste(Image.open(path).convert("RGB").resize(CELL, Image.LANCZOS), (x, y + LABEL))
        sheet.save(os.path.join(out, "contact_%02d.jpg" % number), quality=80)
    print("%d pages for %d materials in %s" % (len(pages), len(rows), out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 15)
