"""Make one side-by-side sheet per station: the grey render on the left, the photograph on the right.

    python -B station_sheets.py <folder with S*_grey.png> <stations.csv> <output folder> [<folder with photographs>]

A photograph is looked for as <station>_photo.jpg or <station>_photo.png in the photograph folder. Where
there is none, the right half is a labelled empty panel that says so, so that the gap is visible in the
sheet and is not mistaken for a comparison. Each sheet also carries the notes given in NOTES below.
"""

import csv
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PANEL = (1280, 720)
MARGIN = 24
FOOT = 150

NOTES = [
    "Grey render: view mode Lighting Only, 24 mm lens, eye 160 cm over the ground, placeholder daylight.",
    "Neighbours and ground: 2022 laser scan and county footprints only. No facade detail, no openings (gap).",
    "Not built, no evidence: light poles, hydrant, utility pole, signs, fences, trees (gaps).",
    "Placeholders: flat ground over the lot (SG_lot_placeholder); sun, sky atmosphere and sky light.",
]


def font(size):
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def find_photo(folder, station):
    if not folder:
        return None
    for extension in (".jpg", ".jpeg", ".png"):
        path = os.path.join(folder, station + "_photo" + extension)
        if os.path.exists(path):
            return path
    return None


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    render_folder, stations_csv, output_folder = argv[1], argv[2], argv[3]
    photo_folder = argv[4] if len(argv) > 4 else None
    os.makedirs(output_folder, exist_ok=True)
    with open(stations_csv, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    big, small = font(30), font(20)
    made = []
    for row in rows:
        station = row["station"].split(" ")[0]
        render_path = os.path.join(render_folder, station + "_grey.png")
        width = PANEL[0] * 2 + MARGIN * 3
        height = PANEL[1] + MARGIN * 2 + 60 + FOOT
        sheet = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)
        draw.text((MARGIN, MARGIN), "1529 N. Wieland, Phase 4, station " + row["station"] + ": " + row["note"], fill=(0, 0, 0), font=big)
        top = MARGIN + 60
        left_box = (MARGIN, top, MARGIN + PANEL[0], top + PANEL[1])
        right_box = (MARGIN * 2 + PANEL[0], top, MARGIN * 2 + PANEL[0] * 2, top + PANEL[1])
        if os.path.exists(render_path):
            sheet.paste(Image.open(render_path).convert("RGB").resize(PANEL, Image.LANCZOS), left_box[:2])
        else:
            draw.rectangle(left_box, outline=(160, 0, 0), width=3)
            draw.text((left_box[0] + 30, left_box[1] + 30), "NO RENDER: this station cannot be stood on (see its note above).", fill=(160, 0, 0), font=big)
        photo = find_photo(photo_folder, station)
        if photo:
            sheet.paste(Image.open(photo).convert("RGB").resize(PANEL, Image.LANCZOS), right_box[:2])
        else:
            draw.rectangle(right_box, fill=(235, 235, 235), outline=(160, 0, 0), width=3)
            draw.text((right_box[0] + 30, right_box[1] + 30), "PLACEHOLDER: no photograph.", fill=(160, 0, 0), font=big)
            draw.text((right_box[0] + 30, right_box[1] + 80), "The site visit of Phase 2 was not made, so there is nothing", fill=(60, 60, 60), font=small)
            draw.text((right_box[0] + 30, right_box[1] + 108), "to compare this render with and no camera was solved.", fill=(60, 60, 60), font=small)
        y = top + PANEL[1] + 12
        for note in NOTES:
            draw.text((MARGIN, y), note, fill=(0, 0, 0), font=small)
            y += 30
        target = os.path.join(output_folder, station + "_sheet.jpg")
        sheet.save(target, quality=88)
        made.append(target)
    for path in made:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
