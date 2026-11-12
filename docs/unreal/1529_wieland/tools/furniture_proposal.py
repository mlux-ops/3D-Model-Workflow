"""Write furniture_proposal.csv for Phase 6, step 6.4 (a proposal only; nothing is downloaded).

Run with:  python -B furniture_proposal.py <catalogue extract json> <output csv>

The catalogue extract holds, for each public-domain model named below, the size and the file
sizes that the Poly Haven catalogue listed on 2026-11-11:
    {"<id>": {"dimensions_mm": [x, y, z], "polycount": n, "condition": "...", "files_mb": {"fbx_4k": n, ...}}}
"""

import csv
import json
import sys

PH = "Poly Haven (polyhaven.com/a/%s)"
CC0 = ("CC0 (public domain); a 3D model, so not covered by the standing approval, "
       "which is for textures only")
FAB = "Fab marketplace (fab.com), a licensed interior furniture pack to be chosen by the owner"
FAB_LICENCE = "Fab Standard License (paid); needs the owner's approval and a purchase on the owner's Epic account"
NO_MODERN = ("No modern piece of this kind exists in the public-domain catalogue "
             "(its sofas, beds and dining tables are antique or worn).")
MADE_HERE = ("Can be made here as simple geometry with a public-domain fabric texture once approved, "
             "at no cost.")

HEAD = ["room_type", "item", "quantity_per_room", "stand_in_size_cm_width_depth_height", "source",
        "licence", "size_on_disk_mb", "cost_usd", "size_basis", "note"]


def build(catalogue):
    rows = []

    def ph(room, item, quantity, ident, note=""):
        entry = catalogue[ident]
        d = entry["dimensions_mm"]
        files = entry["files_mb"]
        resolution = "4K" if "fbx_4k" in files else "2K"
        size = files["fbx_4k"] if "fbx_4k" in files else files["fbx_2k"]
        rows.append([room, item, quantity, "%.0f x %.0f x %.0f" % (d[0] / 10, d[1] / 10, d[2] / 10),
                     PH % ident, CC0, "%.1f (FBX with %s images)" % (size, resolution), "0",
                     "catalogue figure, read 2026-11-11", note])

    def gap(room, item, quantity, size, note=NO_MODERN):
        rows.append([room, item, quantity, size, FAB, FAB_LICENCE, "not known until a pack is chosen",
                     "not confirmed: the price is shown on the listing and could not be read from here",
                     "typical size of the piece, used for the grey stand-in", note])

    room = "Living room"
    gap(room, "Sofa, three seats", 1, "240 x 95 x 80")
    ph(room, "Lounge chair", 2, "mid_century_lounge_chair",
       "The catalogue marks it worn (used leather); owner to accept or replace.")
    ph(room, "Coffee table", 1, "modern_coffee_table_01")
    ph(room, "Side table", 2, "side_table_01")
    ph(room, "Media cabinet, low", 1, "modern_wooden_cabinet")
    gap(room, "Television, wall hung, 65 inch", 1, "145 x 6 x 84",
        "A plain dark panel; can be made here at no cost once approved.")
    gap(room, "Rug", 1, "300 x 240 x 1.5", MADE_HERE)
    gap(room, "Window treatment: sheer curtain or roller shade, per window", 1,
        "window width x 8 x window height", MADE_HERE)
    ph(room, "Throw pillows", 1, "throw_pillows_01", "Patterned; owner to accept the pattern.")
    ph(room, "Potted plant, floor", 1, "potted_plant_01",
       "Heavy: 96,030 triangles and 267 MB at 4K; the 1K version is 25 MB.")
    ph(room, "Vase", 2, "ceramic_vase_01")
    ph(room, "Picture frame, wall", 2, "hanging_picture_frame_01",
       "The picture inside is the catalogue's; the owner may supply art.")
    ph(room, "Books, decorative set", 1, "decorative_book_set_01",
       "Heavy: 112,560 triangles and 682 MB at 4K; the 1K version is 75 MB.")

    room = "Family room (lower floor)"
    gap(room, "Sectional sofa", 1, "280 x 160 x 80")
    ph(room, "Coffee table, round", 1, "coffee_table_round_01")
    ph(room, "Shelving unit", 1, "steel_frame_shelves_03")
    gap(room, "Television, wall hung, 75 inch", 1, "168 x 6 x 96",
        "A plain dark panel; can be made here at no cost once approved.")
    gap(room, "Rug", 1, "300 x 240 x 1.5", MADE_HERE)

    room = "Dining room"
    gap(room, "Dining table for eight", 1, "240 x 105 x 75")
    ph(room, "Dining chair", 8, "dining_chair_02")
    ph(room, "Sideboard", 1, "modern_wooden_cabinet", "Same asset as the living room media cabinet.")
    ph(room, "Tableware: tea set", 1, "tea_set_01", "Ornate English style; owner to accept or replace.")
    ph(room, "Vase, tall", 1, "ceramic_vase_03")
    gap(room, "Tableware: plates, glasses and cutlery for eight", 1, "place setting 45 x 35 x 10 each",
        "The public-domain catalogue has no modern plates or glasses.")

    room = "Kitchen"
    gap(room, "Counter stool", 3, "45 x 45 x 95",
        "The Revit model already carries a tripod stool at the island; a render-quality stool "
        "of the specified make is wanted, or the Revit one stays.")
    ph(room, "Bowl on the counter", 1, "wooden_bowl_01", "The catalogue marks it worn.")
    ph(room, "Jug", 1, "jug_01")
    gap(room, "Small appliances and accessories (kettle, board, bottles)", 1, "60 x 30 x 35 group",
        "The public-domain catalogue has only vintage ones.")

    room = "Primary bedroom"
    gap(room, "Bed, king, with bedding", 1, "200 x 215 x 105")
    gap(room, "Nightstand", 2, "55 x 45 x 55",
        "side_table_01 from the public-domain catalogue (55 x 45 x 55 cm, 11.9 MB, CC0) would serve "
        "if the owner accepts an open table without a drawer.")
    ph(room, "Dresser", 1, "drawer_cabinet")
    ph(room, "Armchair", 1, "modern_arm_chair_01", "The catalogue marks it worn; 139 MB at 4K.")
    gap(room, "Rug", 1, "300 x 240 x 1.5", MADE_HERE)
    gap(room, "Window treatment, per window", 1, "window width x 8 x window height", MADE_HERE)
    ph(room, "Picture frame, standing", 1, "standing_picture_frame_01")

    room = "Bedroom (secondary)"
    gap(room, "Bed, queen, with bedding", 1, "160 x 210 x 105")
    gap(room, "Nightstand", 2, "55 x 45 x 55", "side_table_01 would serve, as in the primary bedroom.")
    ph(room, "Display shelves", 1, "wooden_display_shelves_01")
    gap(room, "Desk and chair", 1, "140 x 70 x 75",
        "The public-domain catalogue has only worn office desks.")
    gap(room, "Window treatment, per window", 1, "window width x 8 x window height", MADE_HERE)

    room = "Bathroom and powder room"
    gap(room, "Towels, folded and hung", 1, "60 x 3 x 80 hung", MADE_HERE)
    ph(room, "Small plant", 1, "potted_plant_04")
    gap(room, "Soap, bottles and tray", 1, "30 x 15 x 20 group",
        "Not in the public-domain catalogue.")

    room = "Laundry"
    gap(room, "Baskets and folded linen", 1, "60 x 40 x 35 group",
        "wicker_basket_02 from the public-domain catalogue (37 x 27 x 22 cm, CC0) would serve.")

    room = "Hall and entry"
    gap(room, "Console table", 1, "140 x 35 x 80")
    ph(room, "Picture frame, wall", 2, "hanging_picture_frame_01")
    gap(room, "Mirror, wall", 1, "80 x 3 x 120", "A framed mirror can be made here at no cost once approved.")

    room = "Garage"
    gap(room, "Car", 1, "480 x 190 x 145",
        "A car is what makes a garage read as used when its door is open; licensed vehicle models "
        "are the costliest item here. The owner may prefer the door shown closed.")

    room = "Rear patio (triplex)"
    ph(room, "Outdoor table and two folding chairs", 1, "outdoor_table_chair_set_01")
    gap(room, "Outdoor sofa", 1, "200 x 85 x 70")
    ph(room, "Planter box", 2, "planter_box_02",
       "The catalogue marks it worn timber; owner to accept or replace.")

    room = "Roof deck and rear terrace (penthouse)"
    gap(room, "Outdoor sectional sofa", 1, "280 x 200 x 70")
    gap(room, "Outdoor dining table for six, with chairs", 1, "200 x 100 x 75 table; chairs 55 x 55 x 85")
    gap(room, "Planters with shrubs", 4, "60 x 60 x 120",
        "Shrubs come with the Phase 8 planting; the planter can be made here.")
    gap(room, "Outdoor rug", 1, "300 x 240 x 1.5", MADE_HERE)
    return rows


def main(catalogue_path, out_path):
    with open(catalogue_path, encoding="utf-8") as handle:
        catalogue = json.load(handle)
    rows = build(catalogue)
    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEAD)
        writer.writerows(rows)
    distinct = {}
    for row in rows:
        if row[4].startswith("Poly Haven"):
            distinct[row[4]] = float(row[6].split()[0])
    print("rows %d; public-domain rows %d; distinct public-domain models %d, %.1f MB together"
          % (len(rows), sum(1 for r in rows if r[4].startswith("Poly Haven")), len(distinct),
             sum(distinct.values())))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
