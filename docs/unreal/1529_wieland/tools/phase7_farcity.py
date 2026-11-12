"""Phase 7, audit finding A10: the layout of the distant-city stand-in.

Run from the plan folder:  python -B tools/phase7_farcity.py

Writes review/phase7/farcity/plan.json: a list of plain blocks (centre, size, height, kind) around the
modelled area, and the size of a ground apron under them. NOTHING here is from a survey or a photograph:
the blocks follow a regular street grid of Chicago's block size, and the tall groups stand roughly where
the city's tall buildings are known to stand as seen from Old Town (south-east and south). It is a
labelled stand-in so that the world no longer ends in view; it is fixed by a seed so that it can be remade.

Level frame: centimetres, origin at the lot's south-west corner, north = -X, east = -Y.
"""

import json
import os
import random

OUT = "review/phase7/farcity"
SEED = 1529

# The modelled area (Phase 4 buildings and ground) with a margin; no stand-in block inside it.
MODEL = {"x0": -17500.0, "x1": 16000.0, "y0": -18500.0, "y1": 15000.0}
REACH = 130000.0          # the low blocks reach 1.3 km from the lot
LAKE_Y = -100000.0        # no low blocks further east than 1 km (the lake shore)
APRON = 500000.0          # half the side of the ground apron: 10 km square
APRON_TOP = -40.0         # the apron's top, 40 cm under the lot's datum
BASE = -150.0             # every block starts 1.5 m under the datum

BLOCK_X, BLOCK_Y = 20100.0, 10000.0   # one city block with its streets: 201 m north-south, 100 m east-west
STREET = 2000.0
ALLEY = 500.0
WIELAND_Y = 785.0                     # centre line of Wieland; the grid of north-south streets is hung on it


def low_blocks(rng):
    boxes = []
    row_depth = (BLOCK_Y - STREET - ALLEY) / 2.0
    j0 = int((-REACH - WIELAND_Y) // BLOCK_Y) - 1
    i0 = int(-REACH // BLOCK_X) - 1
    for i in range(i0, -i0 + 1):
        for j in range(j0, -j0 + 1):
            x_start = MODEL["x0"] + i * BLOCK_X + STREET / 2.0
            y_street = WIELAND_Y + j * BLOCK_Y
            for row in range(2):
                y_low = y_street + STREET / 2.0 + row * (row_depth + ALLEY)
                x = x_start
                x_end = x_start + BLOCK_X - STREET
                while x < x_end - 900.0:
                    length = min(rng.uniform(1200.0, 4500.0), x_end - x)
                    gap = rng.choice((0.0, 0.0, 100.0, 300.0))
                    draw = rng.random()
                    if draw < 0.70:
                        height = rng.uniform(900.0, 1400.0)
                    elif draw < 0.95:
                        height = rng.uniform(1400.0, 2500.0)
                    else:
                        height = rng.uniform(2500.0, 6000.0)
                    depth = row_depth * rng.uniform(0.7, 1.0)
                    cx, cy = x + length / 2.0, y_low + row_depth / 2.0
                    x += length + gap
                    if rng.random() < 0.12:
                        continue          # a yard or a car park
                    if abs(cx) > REACH or abs(cy) > REACH or cy < LAKE_Y:
                        continue
                    half_x, half_y = length / 2.0, depth / 2.0
                    if (cx + half_x > MODEL["x0"] and cx - half_x < MODEL["x1"]
                            and cy + half_y > MODEL["y0"] and cy - half_y < MODEL["y1"]):
                        continue
                    boxes.append({"x": round(cx, 1), "y": round(cy, 1), "sx": round(length, 1), "sy": round(depth, 1),
                                  "h": round(height, 1), "kind": 0 if rng.random() < 0.7 else 2})
    return boxes


def tall_group(rng, centre, spread, count, low, high, name):
    boxes = []
    for _ in range(count):
        cx = rng.gauss(centre[0], spread[0])
        cy = rng.gauss(centre[1], spread[1])
        height = low + (high - low) * rng.random() ** 2.2
        side_x, side_y = rng.uniform(2500.0, 5500.0), rng.uniform(2500.0, 5500.0)
        boxes.append({"x": round(cx, 1), "y": round(cy, 1), "sx": round(side_x, 1), "sy": round(side_y, 1),
                      "h": round(height, 1), "kind": 1 if rng.random() < 0.65 else 2, "group": name})
    return boxes


def main():
    rng = random.Random(SEED)
    boxes = low_blocks(rng)
    low_count = len(boxes)
    # Tall groups, roughly where they are known to stand as seen from Old Town. Heights in cm.
    boxes += tall_group(rng, (90000.0, -90000.0), (35000.0, 25000.0), 40, 6000.0, 22000.0, "south-east, 1.3 km (towards the lake shore)")
    boxes += [{"x": 85000.0, "y": -95000.0, "sx": 6000.0, "sy": 4500.0, "h": 34000.0, "kind": 1, "group": "south-east, one very tall tower"}]
    boxes += tall_group(rng, (300000.0, -60000.0), (60000.0, 50000.0), 70, 9000.0, 36000.0, "south, 3 km (the city centre)")
    boxes += tall_group(rng, (-10000.0, -85000.0), (60000.0, 9000.0), 25, 4000.0, 13000.0, "east, 850 m (along the lake shore)")
    plan = {"seed": SEED, "note": "stand-in, not from a survey or a photograph", "base_cm": BASE,
            "apron": {"half_side_cm": APRON, "top_cm": APRON_TOP}, "model_area_left_free": MODEL, "boxes": boxes}
    os.makedirs(OUT, exist_ok=True)
    with open(OUT + "/plan.json", "w", encoding="utf-8") as handle:
        json.dump(plan, handle)
    print(json.dumps({"low_blocks": low_count, "tall": len(boxes) - low_count, "tallest_m": max(b["h"] for b in boxes) / 100.0}))


if __name__ == "__main__":
    main()
