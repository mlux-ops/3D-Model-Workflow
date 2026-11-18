"""Phase 6, step 6.6: how far the two halves of 1529 N. Wieland are mirror images of each other.

Read-only in the editor; it writes one CSV. The south half was not made by mirroring: both halves came
from the Revit model as drawn. So this tool measures. An object of one unit has a partner when the
partner unit holds an object of the same Revit family and type (the label without its running number)
whose bounding box, mirrored at the party line, has the same middle and the same size within the
tolerance. Objects that this project generated (baseboards, stand-ins) are counted separately.

    import wieland_mirror
    wieland_mirror.compare(r"...\\mirror_differences.csv")
"""
import collections
import csv
import re

import wieland_levels
import wieland_standins
import wieland_trim

TOLERANCE = 1.0  # cm, that is 10 mm
PAIRS = (("NorthTriplex", "SouthTriplex"), ("NorthPenthouse", "SouthPenthouse"))
TAG_GENERATED = "W1529.Generated"
HEAD = ["unit", "partner_unit", "object", "category", "storey", "room_side", "x", "y", "z",
        "size_x", "size_y", "size_z", "nearest_same_kind_cm", "finding"]


def _kind(label):
    return re.sub(r"_\d+$", "", label)


def _storey(z):
    """The storey whose floor lies at or below the middle of the box."""
    name = wieland_standins.STOREYS["L"][0]
    for code in ("L", "1", "2", "3", "4", "R"):
        if z >= wieland_standins.STOREYS[code][1] - 30.0:
            name = wieland_standins.STOREYS[code][0]
    return name


def _unit_of(actor):
    name = actor.get_outer().get_outer().get_name()
    return name[len("L_W1529_"):] if name.startswith("L_W1529_") else name


def objects():
    """{unit: [(label, category, box)]} of the imported objects, and {unit: {kind: count}} of the generated."""
    imported = collections.defaultdict(list)
    generated = collections.defaultdict(collections.Counter)
    seen = set()
    for actor, component, category in wieland_trim._building_components():
        key = actor.get_path_name()
        if key in seen:
            continue
        seen.add(key)
        origin, extent = actor.get_actor_bounds(False)
        box = (origin.x - extent.x, origin.y - extent.y, origin.z - extent.z,
               origin.x + extent.x, origin.y + extent.y, origin.z + extent.z)
        imported[_unit_of(actor)].append((actor.get_actor_label(), category, box))
    for actor in wieland_levels._actors():
        tags = [str(tag) for tag in actor.tags]
        if TAG_GENERATED in tags:
            kind = "stand-in" if wieland_standins.TAG_PLACEHOLDER in tags else "baseboard"
            generated[_unit_of(actor)][kind] += 1
    return imported, generated


def _mirrored(box):
    party = wieland_levels.PARTY_X
    return (2.0 * party - box[3], box[1], box[2], 2.0 * party - box[0], box[4], box[5])


def _match(source, target):
    """Pairs the objects of two units. Returns (matched, source only [(entry, nearest)], target only)."""
    by_kind = collections.defaultdict(list)
    for index, (label, category, box) in enumerate(target):
        by_kind[_kind(label)].append(index)
    used = set()
    matched = 0
    alone = []
    for label, category, box in source:
        want = _mirrored(box)
        best = None
        for index in by_kind.get(_kind(label), ()):
            if index in used:
                continue
            other = target[index][2]
            off = max(abs(want[n] - other[n]) for n in range(6))
            if best is None or off < best[0]:
                best = (off, index)
        if best is not None and best[0] <= TOLERANCE:
            used.add(best[1])
            matched += 1
        else:
            alone.append(((label, category, box), None if best is None else best[0]))
    rest = [(target[index], None) for index in range(len(target)) if index not in used]
    return matched, alone, rest


def compare(csv_path):
    """Writes the objects without a mirror partner to csv_path and returns the counts."""
    imported, generated = objects()
    result = {"tolerance_mm": TOLERANCE * 10.0, "pairs": []}
    rows = []
    for north, south in PAIRS:
        matched, north_only, south_only = _match(imported[north], imported[south])
        # For the south-only objects, the distance to the nearest object of the same kind in the north.
        _, south_alone, _ = _match(imported[south], imported[north])
        nearest_south = {entry[0]: nearest for entry, nearest in south_alone}
        by_category = collections.Counter()
        by_storey = collections.Counter()
        for unit, partner, alone in ((north, south, north_only), (south, north, south_only)):
            for (label, category, box), nearest in alone:
                if unit == south:
                    nearest = nearest_south.get(label)
                storey = _storey((box[2] + box[5]) / 2.0)
                by_category[category] += 1
                by_storey[storey] += 1
                if nearest is None:
                    finding = "the partner unit has no free object of this kind"
                elif nearest <= 5.0:
                    finding = "a partner of this kind is within 50 mm: placed or sized slightly differently"
                else:
                    finding = "the nearest free partner of this kind is elsewhere"
                rows.append([unit, partner, label, category, storey,
                             "front" if (box[1] + box[4]) / 2.0 > -1700.0 else "rear",
                             round((box[0] + box[3]) / 2.0, 1), round((box[1] + box[4]) / 2.0, 1),
                             round((box[2] + box[5]) / 2.0, 1), round(box[3] - box[0], 1),
                             round(box[4] - box[1], 1), round(box[5] - box[2], 1),
                             "" if nearest is None else round(nearest, 1), finding])
        result["pairs"].append({
            "north": north, "south": south,
            "imported_north": len(imported[north]), "imported_south": len(imported[south]),
            "matched": matched, "north_only": len(north_only), "south_only": len(south_only),
            "generated_north": dict(generated[north]), "generated_south": dict(generated[south]),
            "unmatched_by_category": dict(by_category.most_common()),
            "unmatched_by_storey": dict(by_storey),
            "within_50_mm": sum(1 for row in rows if row[0] in (north, south) and row[13].startswith("a partner")),
        })
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEAD)
        writer.writerows(sorted(rows, key=lambda row: (row[0], row[4], row[3], row[2])))
    result["rows"] = len(rows)
    return result
