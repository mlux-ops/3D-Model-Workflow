"""Phase 6, step 6.9: one sheet per design view with the grey render, the material render and the Revit panel.

    python -B phase6_view_sheets.py <folder with D*_grey.png and D*_material.png> <output folder> [<Revit view folder>]

Left: the view in plain grey (every surface the same matte grey), to judge shapes.
Middle: the same view with the materials as saved in the project (Revit's own materials, the active default).
Right: the Revit view of the same camera, looked for as <view>_revit.jpg or .png; where there is none, a
labelled empty panel that says so, so that the gap is not mistaken for a comparison.
"""
import os
import sys

from PIL import Image, ImageDraw

from station_sheets import font

PANEL = (960, 540)
MARGIN = 20
VIEWS = (
    ("D1", "north penthouse roof deck, under the pergola"),
    ("D2", "north penthouse, 4th floor, street-facing kitchen room"),
    ("D3", "north triplex, 1st floor kitchen"),
    ("D4", "north triplex, 2nd floor hall bath"),
    ("D5", "north triplex, covered rear patio, 1st floor"),
)
NOTES = [
    "Camera positions are provisional (REFERENCE_VIEWS.md), north half, 24 mm lens, eye 160 cm over the finished floor.",
    "Light: a temporary 150-candela work lamp above the camera; the rooms have no lighting of their own before Phase 7.",
    "Grey: view mode Lighting Only. Material: view mode Lit, named quality Epic, Revit materials as exported.",
    "Furniture: grey blocks are stand-ins for the proposed furniture, which the owner has not approved.",
]


def find_revit(folder, view):
    if not folder:
        return None
    for extension in ("jpg", "jpeg", "png"):
        path = os.path.join(folder, "%s_revit.%s" % (view, extension))
        if os.path.exists(path):
            return path
    return None


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    render_folder, output_folder = argv[1], argv[2]
    revit_folder = argv[3] if len(argv) > 3 else None
    os.makedirs(output_folder, exist_ok=True)
    big, small = font(28), font(19)
    made = 0
    for view, title in VIEWS:
        width = PANEL[0] * 3 + MARGIN * 4
        top = MARGIN + 50
        height = top + PANEL[1] + 40 + len(NOTES) * 28 + MARGIN
        sheet = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)
        draw.text((MARGIN, MARGIN), "1529 N. Wieland, Phase 6, design view %s: %s" % (view, title), fill=(0, 0, 0),
                  font=big)
        for index, (suffix, label) in enumerate((("grey", "Plain grey"),
                                                 ("material", "Materials as saved (Revit as exported)"))):
            x = MARGIN + index * (PANEL[0] + MARGIN)
            path = os.path.join(render_folder, "%s_%s.png" % (view, suffix))
            if os.path.exists(path):
                sheet.paste(Image.open(path).convert("RGB").resize(PANEL, Image.LANCZOS), (x, top))
            else:
                draw.rectangle((x, top, x + PANEL[0], top + PANEL[1]), outline=(160, 0, 0), width=3)
                draw.text((x + 30, top + 30), "NO RENDER.", fill=(160, 0, 0), font=big)
            draw.text((x, top + PANEL[1] + 6), label, fill=(0, 0, 0), font=small)
        x = MARGIN + 2 * (PANEL[0] + MARGIN)
        revit = find_revit(revit_folder, view)
        if revit:
            sheet.paste(Image.open(revit).convert("RGB").resize(PANEL, Image.LANCZOS), (x, top))
        else:
            draw.rectangle((x, top, x + PANEL[0], top + PANEL[1]), fill=(235, 235, 235), outline=(160, 0, 0), width=3)
            draw.text((x + 30, top + 30), "PLACEHOLDER: no Revit view.", fill=(160, 0, 0), font=big)
            draw.text((x + 30, top + 80), "No Revit view from this camera has been exported, so there is", fill=(60, 60, 60),
                      font=small)
            draw.text((x + 30, top + 108), "nothing to compare these renders with (step 6.9 as written).",
                      fill=(60, 60, 60), font=small)
        draw.text((x, top + PANEL[1] + 6), "Revit view of the same camera", fill=(0, 0, 0), font=small)
        y = top + PANEL[1] + 40
        for note in NOTES:
            draw.text((MARGIN, y), note, fill=(0, 0, 0), font=small)
            y += 28
        sheet.save(os.path.join(output_folder, "%s_sheet.png" % view))
        made += 1
    print("sheets written: %d" % made)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
