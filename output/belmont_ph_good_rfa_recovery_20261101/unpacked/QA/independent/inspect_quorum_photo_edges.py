"""Measure candidate glass edges in a saved OEM product photograph.

Read-only diagnostic. No Revit import and no artificial model approvals.
Execute with local CPython 3 and Pillow; inspect the image independently.
"""
from pathlib import Path
from PIL import Image


HERE = Path(__file__).resolve().parent
PHOTO = HERE.parent / "sources" / "oem" / "quorum_veno_858_59" / "quorum_858-59_shade_closeup.jpg"


def candidates(im, y, threshold):
    pix = im.load()
    # White-balance deviation (the studio background is white).
    def delta(x):
        r, g, b = pix[x, y][:3]
        return max(255-r, 255-g, 255-b)

    def run(from_x, stop_x, step):
        for x in range(from_x, stop_x, step):
            if all(delta(xx) >= threshold for xx in (x, x+step, x+2*step)):
                return x
        return None

    return run(100, 349, 1), run(600, 351, -1)


if __name__ == "__main__":
    img = Image.open(PHOTO).convert("RGB")
    print("PHOTO", PHOTO, "size", img.size)
    for y in (210, 225, 240, 260, 285, 310, 335, 365, 400, 440, 480, 520, 560, 585, 610, 618):
        print("row", y, "candidates", [(t, candidates(img, y, t)) for t in (5, 10, 15, 25, 35)])
