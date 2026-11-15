"""Phase 20: labelled contact sheets of the reference photographs, for looking at them in one go.

Usage: python -B -P phase20_sheets.py <commons_index.csv> <out folder> <title substring or file list ...>
       python -B -P phase20_sheets.py <commons_index.csv> <out folder> --building <county id> [...]

Each sheet holds up to 6 photographs (3 by 2, 760 px wide tiles) with a caption: a number, the file title, licence and
author. Sheets are written as JPEG into <out folder> (outside the repository: they are made of other people's
photographs and are reference only).
"""

import csv
import os
import sys

from PIL import Image, ImageDraw

TILE_W, TILE_H, CAP = 760, 500, 34


def sheet(items, path):
    cols = 3
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (cols * TILE_W, rows * (TILE_H + CAP)), "white")
    d = ImageDraw.Draw(im)
    for k, it in enumerate(items):
        x, y = (k % cols) * TILE_W, (k // cols) * (TILE_H + CAP)
        try:
            ph = Image.open(it["file"]).convert("RGB")
            ph.thumbnail((TILE_W - 6, TILE_H - 4))
            im.paste(ph, (x + 3, y + CAP))
        except Exception as exc:
            d.text((x + 6, y + CAP + 6), "unreadable: %s" % exc, fill="red")
        cap = "%d. %s" % (k + 1, it["title"].replace("File:", "")[:70])
        d.text((x + 4, y + 2), cap, fill="black")
        d.text((x + 4, y + 17), ("%s | %s | %s" % (it["licence"], it["author"][:40], it.get("how", "")[:40])), fill="#444")
    im.save(path, quality=82)


def main(argv):
    index, out = argv[1], argv[2]
    os.makedirs(out, exist_ok=True)
    rows = list(csv.DictReader(open(index, encoding="utf-8")))
    if argv[3] == "--building":
        for bid in argv[4:]:
            items = [r for r in rows if bid in r["buildings"].split()]
            for k in range(0, len(items), 6):
                sheet(items[k:k + 6], os.path.join(out, "b%s_%d.jpg" % (bid, k // 6 + 1)))
            print(bid, len(items))
    else:
        keys = argv[3:]
        items = [r for r in rows if any(key in r["title"] or key == os.path.basename(r["file"]) for key in keys)]
        for k in range(0, len(items), 6):
            sheet(items[k:k + 6], os.path.join(out, "set_%d.jpg" % (k // 6 + 1)))
        print(len(items))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
