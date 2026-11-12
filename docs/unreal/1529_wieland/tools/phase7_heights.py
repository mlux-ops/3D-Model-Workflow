"""Phase 7, step 7.0: compare the earlier detailed buildings with the Phase 4 survey massing.

Reads the height maps written by wieland_site.height_jobs (review/phase7/heights/<group>/<name>.json
and .f32; one value per 0.5 m cell, level coordinates, cm) and writes:

    review/phase7/buildings_compare.csv   one line per Phase 4 building
    review/phase7/r15_only_buildings.csv  earlier buildings with no Phase 4 building under them
    review/phase7/ground_compare.json     the earlier parts' own ground against the Phase 4 ground
    review/phase7/heights/overview.png    a plan picture of the three height maps

Run from the plan folder:  python -B tools/phase7_heights.py
Nothing in Unreal is touched.
"""

import csv
import glob
import json
import os

import numpy as np
from scipy import ndimage

ROOT = "review/phase7"
HEIGHTS = ROOT + "/heights"
NONE = -99999.0
BUILDING_OVER_GROUND_CM = 250.0   # an earlier-part cell this far above the earlier ground counts as building
COVERED_SHARE = 0.5               # a Phase 4 building counts as covered at this share of its cells


def load_group(group):
    items = {}
    for header_path in sorted(glob.glob(HEIGHTS + "/" + group + "/*.json")):
        with open(header_path, "r", encoding="utf-8") as handle:
            header = json.load(handle)
        values = np.fromfile(header_path[:-5] + ".f32", dtype=np.float32).reshape(header["ni"], header["nj"])
        items[os.path.basename(header_path)[:-5]] = (header, values)
    return items


def extent(groups):
    i0 = min(h["i0"] for g in groups for h, _ in g.values())
    j0 = min(h["j0"] for g in groups for h, _ in g.values())
    i1 = max(h["i0"] + h["ni"] for g in groups for h, _ in g.values())
    j1 = max(h["j0"] + h["nj"] for g in groups for h, _ in g.values())
    return i0, j0, i1 - i0, j1 - j0


def paste_max(target, header, values, i0, j0):
    a = header["i0"] - i0
    b = header["j0"] - j0
    view = target[a:a + header["ni"], b:b + header["nj"]]
    np.maximum(view, values, out=view)


def main():
    r15 = load_group("r15")
    p4b = load_group("p4b")
    p4g = load_group("p4g")
    i0, j0, ni, nj = extent([r15, p4b, p4g])
    cell = 50.0
    cell_sq_m = (cell / 100.0) ** 2

    top_r15 = np.full((ni, nj), NONE, dtype=np.float32)
    for header, values in r15.values():
        paste_max(top_r15, header, values, i0, j0)
    ground_p4 = np.full((ni, nj), NONE, dtype=np.float32)
    for header, values in p4g.values():
        paste_max(ground_p4, header, values, i0, j0)
    top_p4b = np.full((ni, nj), NONE, dtype=np.float32)
    owner = np.full((ni, nj), -1, dtype=np.int32)
    names = sorted(p4b.keys())
    for index, name in enumerate(names):
        header, values = p4b[name]
        a = header["i0"] - i0
        b = header["j0"] - j0
        view = top_p4b[a:a + header["ni"], b:b + header["nj"]]
        own = owner[a:a + header["ni"], b:b + header["nj"]]
        better = values > view
        view[better] = values[better]
        own[better] = index

    has_r15 = top_r15 > NONE / 2
    has_ground = ground_p4 > NONE / 2
    has_p4b = top_p4b > NONE / 2

    # The earlier parts' own ground: the low cells. Its level near each place is the median of the low cells
    # within 10 m, so that "building" means "well above the earlier ground here".
    low = has_r15 & (top_r15 < 150.0)
    low_values = np.where(low, top_r15, 0.0).astype(np.float64)
    size = 41
    summed = ndimage.uniform_filter(low_values, size=size, mode="constant") * size * size
    counted = ndimage.uniform_filter(low.astype(np.float64), size=size, mode="constant") * size * size
    old_ground = np.where(counted > 0.5, summed / np.maximum(counted, 1.0), 0.0)
    r15_building = has_r15 & (top_r15 - old_ground > BUILDING_OVER_GROUND_CM)

    labels, label_count = ndimage.label(r15_building)

    # Each cell's nearest Phase 4 building, so that a row of attached earlier buildings is divided between
    # the Phase 4 buildings it stands on.
    distance, nearest = ndimage.distance_transform_edt(owner < 0, return_indices=True)
    nearest_owner = owner[nearest[0], nearest[1]]

    with open("review/phase4/acceptance_measurements.json", "r", encoding="utf-8") as handle:
        accept = {b["name"]: b for b in json.load(handle)["buildings"]}
    with open("review/phase4/surroundings_manifest.json", "r", encoding="utf-8") as handle:
        manifest = {b["name"]: b for b in json.load(handle)["buildings"]}

    xs = (np.arange(ni) + i0 + 0.5) * cell
    ys = (np.arange(nj) + j0 + 0.5) * cell

    rows = []
    covered_labels = set()
    for index, name in enumerate(names):
        mine = owner == index
        cells = int(mine.sum())
        if cells == 0:
            continue
        both = mine & r15_building
        overlap = int(both.sum())
        share = overlap / cells
        info = manifest.get(name, {})
        measured = accept.get(name, {})
        ii, jj = np.nonzero(mine)
        row = {
            "phase4_building": name,
            "zone": info.get("zone", ""),
            "distance_from_lot_m": info.get("distance_from_lot_m", ""),
            "centre_x_cm": round(float(xs[ii].mean()), 0),
            "centre_y_cm": round(float(ys[jj].mean()), 0),
            "phase4_footprint_sq_m": round(cells * cell_sq_m, 1),
            "covered_by_earlier_sq_m": round(overlap * cell_sq_m, 1),
            "covered_share": round(share, 3),
            "covered": "yes" if share >= COVERED_SHARE else ("partly" if share >= 0.1 else "no"),
            "phase4_ground_cm": info.get("ground_cm", ""),
            "phase4_roof_typical_cm": measured.get("typical_object_cm", info.get("roof_typical_cm", "")),
            "laser_scan_roof_typical_cm": measured.get("typical_lidar_cm", ""),
        }
        if overlap > 0:
            roof = float(np.median(top_r15[both]))
            ground_here = float(np.median(old_ground[both]))
            touching = [int(v) for v in np.unique(labels[both]) if v > 0]
            covered_labels.update(touching)
            # The earlier building's footprint: the earlier building cells that touch this Phase 4 building's
            # shape, lie within 3 m of its outline and are nearer to it than to any other Phase 4 building.
            earlier_shape = r15_building & (nearest_owner == index) & (distance <= 6.0) & np.isin(labels, touching)
            ei, ej = np.nonzero(earlier_shape)
            # Edges of the two outlines; a positive number means the earlier building reaches further out.
            row["north_edge_earlier_further_m"] = round((float(xs[ii].min()) - float(xs[ei].min())) / 100.0, 1)
            row["south_edge_earlier_further_m"] = round((float(xs[ei].max()) - float(xs[ii].max())) / 100.0, 1)
            row["east_edge_earlier_further_m"] = round((float(ys[jj].min()) - float(ys[ej].min())) / 100.0, 1)
            row["west_edge_earlier_further_m"] = round((float(ys[ej].max()) - float(ys[jj].max())) / 100.0, 1)
            row.update({
                "earlier_roof_typical_cm": round(roof, 1),
                "earlier_ground_cm": round(ground_here, 1),
                "earlier_height_above_its_ground_m": round((roof - ground_here) / 100.0, 2),
                "earlier_footprint_within_3m_sq_m": round(int(earlier_shape.sum()) * cell_sq_m, 1),
                "earlier_centre_x_cm": round(float(xs[ei].mean()), 0),
                "earlier_centre_y_cm": round(float(ys[ej].mean()), 0),
            })
            p4_ground = info.get("ground_cm")
            lidar = measured.get("typical_lidar_cm")
            p4_roof = measured.get("typical_object_cm", info.get("roof_typical_cm"))
            if p4_ground is not None and p4_roof is not None:
                row["phase4_height_above_its_ground_m"] = round((p4_roof - p4_ground) / 100.0, 2)
                row["height_difference_earlier_minus_phase4_m"] = round(((roof - ground_here) - (p4_roof - p4_ground)) / 100.0, 2)
            if p4_ground is not None and lidar is not None:
                row["height_difference_earlier_minus_laser_scan_m"] = round(((roof - ground_here) - (lidar - p4_ground)) / 100.0, 2)
            row["footprint_difference_earlier_minus_phase4_sq_m"] = round((int(earlier_shape.sum()) - cells) * cell_sq_m, 1)
        rows.append(row)

    fields = ["phase4_building", "zone", "distance_from_lot_m", "centre_x_cm", "centre_y_cm", "phase4_footprint_sq_m",
              "covered_by_earlier_sq_m", "covered_share", "covered", "earlier_footprint_within_3m_sq_m",
              "footprint_difference_earlier_minus_phase4_sq_m", "north_edge_earlier_further_m", "south_edge_earlier_further_m",
              "east_edge_earlier_further_m", "west_edge_earlier_further_m", "earlier_centre_x_cm", "earlier_centre_y_cm",
              "phase4_ground_cm", "phase4_roof_typical_cm", "laser_scan_roof_typical_cm", "phase4_height_above_its_ground_m",
              "earlier_ground_cm", "earlier_roof_typical_cm", "earlier_height_above_its_ground_m",
              "height_difference_earlier_minus_phase4_m", "height_difference_earlier_minus_laser_scan_m"]
    with open(ROOT + "/buildings_compare.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (-r["covered_share"], r["phase4_building"])):
            writer.writerow(row)

    # Earlier buildings that stand where Phase 4 has none (or mostly none).
    only = []
    for label in range(1, label_count + 1):
        shape = labels == label
        cells = int(shape.sum())
        if cells * cell_sq_m < 10.0:
            continue
        on_p4 = int((shape & has_p4b).sum())
        if on_p4 / cells < 0.2:
            ii, jj = np.nonzero(shape)
            only.append({
                "centre_x_cm": round(float(xs[ii].mean()), 0),
                "centre_y_cm": round(float(ys[jj].mean()), 0),
                "footprint_sq_m": round(cells * cell_sq_m, 1),
                "share_over_a_phase4_building": round(on_p4 / cells, 3),
                "roof_typical_cm": round(float(np.median(top_r15[shape])), 1),
                "phase4_ground_here_cm": round(float(np.median(ground_p4[shape & has_ground])), 1) if (shape & has_ground).any() else "",
            })
    with open(ROOT + "/r15_only_buildings.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["centre_x_cm", "centre_y_cm", "footprint_sq_m", "share_over_a_phase4_building",
                                                    "roof_typical_cm", "phase4_ground_here_cm"])
        writer.writeheader()
        for row in sorted(only, key=lambda r: -r["footprint_sq_m"]):
            writer.writerow(row)

    # Ground against ground.
    both_ground = has_r15 & ~r15_building & has_ground & ~has_p4b
    difference = (top_r15 - ground_p4)[both_ground]
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    near_frontage = both_ground & (np.abs(gx + 754.4) < 3000.0) & (gy > -500.0) & (gy < 2500.0)
    d_near = (top_r15 - ground_p4)[near_frontage]

    def stats(values):
        if values.size == 0:
            return {}
        q = np.percentile(values, [1, 5, 25, 50, 75, 95, 99])
        return {"cells": int(values.size), "p01": round(float(q[0]), 1), "p05": round(float(q[1]), 1), "p25": round(float(q[2]), 1),
                "median": round(float(q[3]), 1), "p75": round(float(q[4]), 1), "p95": round(float(q[5]), 1), "p99": round(float(q[6]), 1),
                "share_earlier_above_phase4": round(float((values > 0).mean()), 3),
                "share_earlier_above_by_5cm": round(float((values > 5).mean()), 3)}

    covered = [r for r in rows if r["covered"] == "yes"]
    partly = [r for r in rows if r["covered"] == "partly"]
    summary = {
        "grid": {"i0": i0, "j0": j0, "ni": ni, "nj": nj, "cell_cm": cell},
        "earlier_parts_extent_cm": {"x": [float(xs[np.nonzero(has_r15.any(axis=1))[0][0]]), float(xs[np.nonzero(has_r15.any(axis=1))[0][-1]])],
                                    "y": [float(ys[np.nonzero(has_r15.any(axis=0))[0][0]]), float(ys[np.nonzero(has_r15.any(axis=0))[0][-1]])]},
        "earlier_area_sq_m": round(float(has_r15.sum()) * cell_sq_m, 0),
        "earlier_building_area_sq_m": round(float(r15_building.sum()) * cell_sq_m, 0),
        "earlier_building_shapes": int(label_count),
        "phase4_buildings": len(rows),
        "phase4_buildings_covered": len(covered),
        "phase4_buildings_partly_covered": len(partly),
        "phase4_buildings_not_covered": len(rows) - len(covered) - len(partly),
        "earlier_ground_minus_phase4_ground_cm_all": stats(difference),
        "earlier_ground_minus_phase4_ground_cm_near_frontage": stats(d_near),
        "earlier_own_ground_level_cm": stats(top_r15[has_r15 & ~r15_building]),
        "earlier_buildings_without_phase4": len(only),
    }
    with open(ROOT + "/ground_compare.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=1)

    np.savez_compressed(HEIGHTS + "/combined.npz", top_r15=top_r15, ground_p4=ground_p4, top_p4b=top_p4b, owner=owner,
                        r15_building=r15_building, old_ground=old_ground.astype(np.float32), i0=i0, j0=j0)

    try:
        from PIL import Image
        picture = np.zeros((ni, nj, 3), dtype=np.uint8)
        picture[has_ground] = (60, 60, 60)
        picture[has_r15 & ~r15_building] = (90, 110, 90)
        picture[has_p4b & ~r15_building] = (200, 60, 60)       # Phase 4 building only: red
        picture[r15_building & ~has_p4b] = (60, 120, 230)      # earlier building only: blue
        picture[r15_building & has_p4b] = (230, 230, 230)      # both: white
        # North is -X and east is -Y: north up and east right means rows by x ascending, columns by y descending.
        Image.fromarray(picture[:, ::-1, :]).resize((nj * 2, ni * 2), Image.NEAREST).save(HEIGHTS + "/overview.png")
    except ImportError:
        pass

    print(json.dumps(summary, indent=1))
    print("covered:", " ".join(r["phase4_building"] for r in covered))
    print("partly:", " ".join("%s(%.2f)" % (r["phase4_building"], r["covered_share"]) for r in partly))


if __name__ == "__main__":
    main()
