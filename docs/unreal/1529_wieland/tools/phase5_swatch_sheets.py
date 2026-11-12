"""Phase 5: one swatch sheet per material.

    python -B phase5_swatch_sheets.py <material_audit.csv> <material_candidates.csv> <folder of Revit swatches>
                                      <folder of candidate swatches> <output folder>

Each sheet shows the Revit material as exported on the left and, where a
candidate was built (confidence 3 or lower), the candidate on the right; where
none was built the right half is a labelled empty panel. Every swatch picture
shows the same stage: a wall piece lit from the front, a wall piece lit at a
grazing angle, and a ball. Under the pictures: the material's family, its
confidence figure with the reason, and what the candidate rests on.
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
FOOT = 190


def font(size):
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def slug(name):
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def panel(path, label, empty_text, small):
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
    return image


def main(audit_csv, candidates_csv, revit_folder, candidate_folder, out_folder):
    os.makedirs(out_folder, exist_ok=True)
    with open(audit_csv, encoding="utf-8", newline="") as handle:
        audit = list(csv.DictReader(handle))
    with open(candidates_csv, encoding="utf-8", newline="") as handle:
        candidates = {row["material"]: row for row in csv.DictReader(handle)}
    big, small = font(24), font(17)
    width = PANEL[0] * 2 + MARGIN * 3
    height = HEAD + PANEL[1] + FOOT
    made, missing = 0, []
    for item in audit:
        name = item["material"]
        candidate = candidates.get(name)
        sheet = Image.new("RGB", (width, height), (24, 24, 24))
        draw = ImageDraw.Draw(sheet)
        draw.text((MARGIN, 8), name[:95], fill=(255, 255, 255), font=big)
        draw.text((MARGIN, 38), "Family: %s.   Confidence %s of 5.   Used on %s objects.   Owner's decision: %s" % (
            item["family"], item["confidence"], item["objects_using_it"], item["decision"] or "open (keep or rebuild)"),
            fill=(200, 200, 200), font=small)
        revit_path = os.path.join(revit_folder, slug(name) + ".png")
        if not os.path.exists(revit_path):
            missing.append(name)
        sheet.paste(panel(revit_path, "Revit material as exported (the active default)",
                          "No picture of the Revit material.", small), (MARGIN, HEAD))
        if candidate:
            right = panel(os.path.join(candidate_folder, slug(name) + ".png"),
                          "Native Unreal candidate (switchable alternative, off by default)",
                          "No picture of the candidate.", small)
        else:
            right = panel(None, "No candidate",
                          "No candidate was built: the confidence is 4 or 5, so the Revit material stays as exported "
                          "unless the owner decides otherwise.", small)
        sheet.paste(right, (MARGIN * 2 + PANEL[0], HEAD))
        lines = textwrap.wrap("Why this confidence: " + item["confidence_reason"], 175)[:3]
        if candidate:
            lines += textwrap.wrap("Candidate rests on: %s Image: %s. Field: %s." % (
                candidate["what_it_rests_on"], candidate["source_and_licence"], candidate["physical_field_size"]),
                175)[:3]
            lines += textwrap.wrap("For the owner: " + candidate["for_the_owner"], 175)[:2]
        lines.append("Each picture: wall piece lit from the front, wall piece lit at a grazing angle, ball. "
                     "No photograph or sample exists; colour is not verified.")
        for index, line in enumerate(lines[:9]):
            draw.text((MARGIN, HEAD + PANEL[1] + 8 + index * 20), line, fill=(215, 215, 215), font=small)
        sheet.save(os.path.join(out_folder, slug(name) + ".jpg"), quality=82)
        made += 1
    print("%d sheets written to %s; %d without a Revit picture: %s" % (made, out_folder, len(missing), missing[:5]))


if __name__ == "__main__":
    main(*sys.argv[1:6])
