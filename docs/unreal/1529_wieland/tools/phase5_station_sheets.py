"""Phase 5, step 5.9: one sheet per station with the material renders and the photograph panel.

    python -B phase5_station_sheets.py <folder with S*_revit.png and S*_alternatives.png> <output folder> [<photo folder>]

Left: the scene with the Revit materials as exported (the active default).
Middle: the same view with the switchable alternatives turned on.
Right: the owner's photograph, looked for as <station>_photo.jpg or .png; where there is none, a labelled
empty panel that says so, as in Phase 4, so that the gap is not mistaken for a comparison.
"""

import os
import sys

from PIL import Image, ImageDraw

from station_sheets import find_photo, font

PANEL = (960, 540)
MARGIN = 20
NOTES = [
    "Material renders: view mode Lit, 24 mm lens, eye 160 cm over the ground, placeholder daylight (lighting proper is Phase 8).",
    "Alternatives: candidates for the materials scored 3 or lower, set as overrides in the editor only and removed again; nothing saved.",
    "Neighbours and ground: laser scan and county footprints with a plain grey surface; no facade materials (Phase 4 gap).",
    "No photograph or sample exists, so no colour was matched and nothing here is verified against the built street.",
]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    render_folder, output_folder = argv[1], argv[2]
    photo_folder = argv[3] if len(argv) > 3 else None
    os.makedirs(output_folder, exist_ok=True)
    big, small = font(28), font(19)
    for station in ("S1", "S3", "S6"):
        width = PANEL[0] * 3 + MARGIN * 4
        top = MARGIN + 50
        height = top + PANEL[1] + 40 + len(NOTES) * 28 + MARGIN
        sheet = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)
        draw.text((MARGIN, MARGIN), "1529 N. Wieland, Phase 5, station %s: material renders" % station, fill=(0, 0, 0),
                  font=big)
        for index, (suffix, label) in enumerate((("revit", "Revit materials as exported (active default)"),
                                                 ("alternatives", "Switchable alternatives turned on"))):
            x = MARGIN + index * (PANEL[0] + MARGIN)
            path = os.path.join(render_folder, "%s_%s.png" % (station, suffix))
            if os.path.exists(path):
                sheet.paste(Image.open(path).convert("RGB").resize(PANEL, Image.LANCZOS), (x, top))
            else:
                draw.rectangle((x, top, x + PANEL[0], top + PANEL[1]), outline=(160, 0, 0), width=3)
                draw.text((x + 30, top + 30), "NO RENDER.", fill=(160, 0, 0), font=big)
            draw.text((x, top + PANEL[1] + 6), label, fill=(0, 0, 0), font=small)
        x = MARGIN + 2 * (PANEL[0] + MARGIN)
        photo = find_photo(photo_folder, station)
        if photo:
            sheet.paste(Image.open(photo).convert("RGB").resize(PANEL, Image.LANCZOS), (x, top))
        else:
            draw.rectangle((x, top, x + PANEL[0], top + PANEL[1]), fill=(235, 235, 235), outline=(160, 0, 0), width=3)
            draw.text((x + 30, top + 30), "PLACEHOLDER: no photograph.", fill=(160, 0, 0), font=big)
            draw.text((x + 30, top + 80), "No owner photograph of this view exists, so there is nothing", fill=(60, 60, 60),
                      font=small)
            draw.text((x + 30, top + 108), "to compare these renders with (steps 5.3 and 5.9 as written).",
                      fill=(60, 60, 60), font=small)
        draw.text((x, top + PANEL[1] + 6), "Photograph", fill=(0, 0, 0), font=small)
        y = top + PANEL[1] + 40
        for note in NOTES:
            draw.text((MARGIN, y), note, fill=(0, 0, 0), font=small)
            y += 28
        target = os.path.join(output_folder, station + "_materials_sheet.jpg")
        sheet.save(target, quality=88)
        print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
