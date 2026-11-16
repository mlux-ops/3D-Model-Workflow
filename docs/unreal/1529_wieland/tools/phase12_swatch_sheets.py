"""Phase 12: one swatch sheet per rebuilt material, Revit beside rebuilt, in the style of Phase 5.

    python -P -B phase12_swatch_sheets.py <material_rebuild.csv> <folder of Revit swatches>
                                          <folder of rebuilt swatches> <output folder> [material ...]

Each sheet shows the Revit material as exported on the left and the rebuilt material on the right.
Every swatch picture shows the same stage: a wall piece lit from the front, a wall piece lit at a
grazing angle, and a ball. Under the pictures: what the finish rests on, the image and its field,
the confidence figure with its reason, and the test results. A finish that rests on an inference
carries the word ASSUMPTION on its picture and the assumption in words below.
"""

import csv
import os
import re
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

PANEL = (760, 380)
MARGIN = 16
HEAD = 64
FOOT = 250


def font(size):
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def slug(name):
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def panel(path, label, empty_text, small, flag=""):
    image = Image.new("RGB", PANEL, (58, 58, 58))
    if path and os.path.exists(path):
        image = Image.open(path).convert("RGB").resize(PANEL, Image.LANCZOS)
    else:
        draw = ImageDraw.Draw(image)
        draw.rectangle([4, 4, PANEL[0] - 5, PANEL[1] - 5], outline=(120, 120, 120), width=2)
        for index, line in enumerate(textwrap.wrap(empty_text, 60)):
            draw.text((30, PANEL[1] // 2 - 30 + index * 26), line, fill=(220, 220, 220), font=small)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, PANEL[0], 26], fill=(0, 0, 0))
    draw.text((8, 3), label, fill=(255, 255, 255), font=small)
    if flag:
        width = int(draw.textlength(flag, font=small)) + 16
        draw.rectangle([PANEL[0] - width, 0, PANEL[0], 26], fill=(190, 110, 0))
        draw.text((PANEL[0] - width + 8, 3), flag, fill=(255, 255, 255), font=small)
    return image


def main(rebuild_csv, revit_folder, rebuilt_folder, out_folder, only):
    os.makedirs(out_folder, exist_ok=True)
    with open(rebuild_csv, encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["action"] == "rebuilt"]
    big, small = font(24), font(17)
    width = PANEL[0] * 2 + MARGIN * 3
    height = HEAD + PANEL[1] + FOOT
    made, missing = 0, []
    for row in rows:
        name = row["material"]
        if only and name not in only:
            continue
        sheet = Image.new("RGB", (width, height), (24, 24, 24))
        draw = ImageDraw.Draw(sheet)
        draw.text((MARGIN, 8), name[:95], fill=(255, 255, 255), font=big)
        draw.text((MARGIN, 38), "Family: %s.   Confidence after rebuild %s of 5.   Used on %s surfaces.   Owner's decision: %s" % (
            row["family"], row["confidence"], row["surfaces_using_it"], row["decision_read"] or "blank"),
            fill=(200, 200, 200), font=small)
        revit_path = os.path.join(revit_folder, slug(name) + ".png")
        rebuilt_path = os.path.join(rebuilt_folder, slug(name) + ".png")
        if not os.path.exists(rebuilt_path):
            missing.append(name)
        sheet.paste(panel(revit_path, "Revit material as exported (one action switches back to it)",
                          "No picture of the Revit material.", small), (MARGIN, HEAD))
        sheet.paste(panel(rebuilt_path, "Rebuilt material (active)", "No picture of the rebuilt material.", small,
                          "ASSUMPTION" if row["assumption"] else ""), (MARGIN * 2 + PANEL[0], HEAD))
        lines = []
        if row["owner_note_read"]:
            lines += textwrap.wrap("Owner's note: " + row["owner_note_read"], 175)[:2]
        lines += textwrap.wrap("Rests on: " + row["what_the_finish_rests_on"], 175)[:4]
        if row["assumption"]:
            lines += textwrap.wrap("ASSUMPTION: " + row["assumption"], 175)[:2]
        lines += textwrap.wrap("Image: %s. Field: %s." % (row["source_and_licence"], row["physical_field_size"]), 175)[:2]
        lines += textwrap.wrap("Why confidence %s: %s" % (row["confidence"], row["confidence_reason"]), 175)[:2]
        if row["passes"]:
            lines += textwrap.wrap("Tests: repeat %s; grazing light %s; passes: %s." % (
                row["tiling_result"], row["grazing_light_result"], row["passes"]), 175)[:2]
        lines.append("Each picture: wall piece lit from the front, wall piece lit at a grazing angle, ball. "
                     "No photograph or sample of the real finish exists; colour is not verified against one.")
        for index, line in enumerate(lines[:12]):
            draw.text((MARGIN, HEAD + PANEL[1] + 8 + index * 20), line, fill=(215, 215, 215), font=small)
        sheet.save(os.path.join(out_folder, slug(name) + ".jpg"), quality=82)
        made += 1
    print("%d sheets written to %s; %d without a rebuilt picture: %s" % (made, out_folder, len(missing), missing[:8]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], set(sys.argv[5:]))
