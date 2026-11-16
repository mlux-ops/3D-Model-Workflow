"""Phase 7, review: one sheet per station with both surroundings options, the earlier render and the photograph panel.

    python -B tools/phase7_review_sheets.py <folder with S*_r15.png, S*_p4.png, S*_r15_leafoff.png> <output folder>

Panels, left to right:
  1. the scene with the option "Earlier detailed buildings" (the default view), leaves on
  2. the same view with the option "Phase 4 survey massing"
  3. the earlier production level's render of October 2026 where a comparable one exists, else a panel that says so
  4. the owner's photograph; none exists, so a labelled empty panel, so that the gap is not mistaken for a comparison
For S2 to S5 a second sheet shows leaves on, leaves off and the photograph panel.
"""

import os
import sys

from PIL import Image, ImageDraw

from station_sheets import font

PANEL = (960, 540)
MARGIN = 20
EARLIER = "E:/Games/Claude/1527 Wieland/fbx_walkthrough/qa/unreal_r15"
# station: (earlier render, what it shows against the station view)
COMPARABLE = {
    "S2": (EARLIER + "/final_release_clean_01/front_context.jpg",
           "front_context (October 2026), lot still empty"),
    "X1_1525": (EARLIER + "/final_r15_visual_01/W1525_front.jpg", "W1525_front (October 2026): the 1525 house from the street"),
}
WHAT = {
    "S1": "S1: square on to the lot from the far sidewalk", "S2": "S2: from the south-west on the far sidewalk",
    "S3": "S3: from the north-west on the far sidewalk", "S4": "S4: from 50 m south on the far sidewalk",
    "S5": "S5: from 60 m north on the far sidewalk", "S6": "S6: on the near sidewalk north of the lot, looking south",
    "S8": "S8: straight down from 80 m", "S9": "S9: from the lot's own sidewalk, looking west across the street",
    "X1_1525": "Extra view: the earlier 1525 house from the far side of Wieland (audit finding A5)",
}
NOTES = [
    "Renders: Unreal 5.9 editor viewport, Lumen, view mode Lit, named quality Epic, 1,920 by 1,080, automatic exposure, review daylight (sun 45 degrees high; lighting proper is Phase 8).",
    "Stand-ins tagged W1529.Placeholder: every Phase 4 building's walls, windows and roof (by rule, from data), the trees (place and size from the 2022 laser scan; species unknown), the lawn, the far city.",
    "Not modelled: street furniture (hydrant, street lights, utility pole, signs), road markings, fences other than those of the earlier level, planting. S7 does not exist: there is no alley.",
    "No photograph exists, so nothing here is verified against the built street.",
]


def panel(path, label, big, small, missing_text=None):
    image = Image.new("RGB", PANEL, (236, 236, 236))
    draw = ImageDraw.Draw(image)
    if path and os.path.exists(path):
        source = Image.open(path).convert("RGB")
        scale = min(PANEL[0] / source.width, PANEL[1] / source.height)
        size = (int(source.width * scale), int(source.height * scale))
        image.paste(source.resize(size, Image.LANCZOS), ((PANEL[0] - size[0]) // 2, (PANEL[1] - size[1]) // 2))
    else:
        draw.rectangle([4, 4, PANEL[0] - 5, PANEL[1] - 5], outline=(160, 0, 0), width=3)
        for number, line in enumerate(missing_text or ["missing"]):
            draw.text((30, 30 + number * 40), line, fill=(160, 0, 0), font=big if number == 0 else small)
    return image, label


def sheet(title, panels, notes, out_path, big, small):
    width = PANEL[0] * len(panels) + MARGIN * (len(panels) + 1)
    top = MARGIN + 50
    height = top + PANEL[1] + 40 + len(notes) * 28 + MARGIN
    page = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(page)
    draw.text((MARGIN, MARGIN), title, fill=(0, 0, 0), font=big)
    for index, (image, label) in enumerate(panels):
        x = MARGIN + index * (PANEL[0] + MARGIN)
        page.paste(image, (x, top))
        draw.text((x, top + PANEL[1] + 6), label, fill=(0, 0, 0), font=small)
    for number, line in enumerate(notes):
        draw.text((MARGIN, top + PANEL[1] + 40 + number * 28), line, fill=(60, 60, 60), font=small)
    page.save(out_path, quality=88)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    renders, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    big, small = font(28), font(19)
    photo = ["PLACEHOLDER: no photograph.", "No photograph of this view exists.", "The site visit and its photographs are the owner's.",
             "Nothing was taken from Street View or map imagery."]
    made = []
    for station in ("S1", "S2", "S3", "S4", "S5", "S6", "S8", "S9", "X1_1525"):
        earlier = COMPARABLE.get(station)
        panels = [
            panel("%s/%s_r15.png" % (renders, station), "Phase 7, option \"Earlier detailed buildings\" (default), leaves on", big, small),
            panel("%s/%s_p4.png" % (renders, station), "Phase 7, option \"Phase 4 survey massing\", leaves on", big, small),
            panel(earlier[0] if earlier else None, ("Earlier production level: " + earlier[1]) if earlier else "Earlier production level", big, small,
                  ["No comparable earlier render.", "The earlier level's renders on disk do not show this view."]),
            panel(None, "Owner's photograph", big, small, photo),
        ]
        path = "%s/%s_review.jpg" % (out, station)
        sheet("1529 N. Wieland, Phase 7 review. " + WHAT[station], panels, NOTES, path, big, small)
        made.append(path)
    for station in ("S2", "S3", "S4", "S5"):
        panels = [
            panel("%s/%s_r15.png" % (renders, station), "Leaves on (the saved state)", big, small),
            panel("%s/%s_r15_leafoff.png" % (renders, station), "Leaves off (list \"Season\", option \"Leaf-off (November)\")", big, small),
            panel(None, "Owner's November photograph", big, small, photo),
        ]
        notes = [NOTES[0], "Trees: 34 stand-ins from the 2022 laser scan (crown top, height, crown width); trunk positions, species and trunk sizes are not known.",
                 "The plan's line (trunk bases within 1.5 percent of image width against the photograph) cannot be measured: there is no photograph.", NOTES[3]]
        path = "%s/%s_leaf_off.jpg" % (out, station)
        sheet("1529 N. Wieland, Phase 7 leaf-off sheet. " + WHAT[station], panels, notes, path, big, small)
        made.append(path)
    print(len(made))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
