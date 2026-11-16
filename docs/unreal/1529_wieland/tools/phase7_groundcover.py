"""Phase 7, step 7.2: the ground-cover map of the Phase 4 ground area, worked out off line.

Reads   E:/Wieland1529_site_data/county_ortho_2025.tif      aerial photograph, 0.5 ft pixels (looked at, never shown in a render)
        E:/Wieland1529_site_data/county_parcels_2025.json   parcel outlines (what is not a parcel is public way)
        E:/Wieland1529_site_data/county_footprints_2022.json
        review/phase2/level_frame.json                      the tie between map coordinates and the level
        review/phase7/heights/combined.npz                  grid of the Phase 4 ground area (0.5 m cells)
        review/phase7/fit/raw/*.npz                         the earlier parts, for the outlines of their own ground
Writes  review/phase7/ground/sources.npz                    the sources on one 12.5 cm grid in the level frame
        review/phase7/ground/ortho_level.png                the photograph turned into the level frame (north up, east right)
        review/phase7/ground/sources_look.png               photograph, earlier ground and parcels side by side
        review/phase7/ground/cover.npz                      the classes on the 12.5 cm grid, and the grid's place
        review/phase7/ground/cover_preview.png              the classes in colour beside the photograph
        review/phase7/ground/cover_summary.json             areas per class and the rules used

Grid: cell (i, j) has its centre at (X0 + (i + 0.5) * STEP, Y0 + (j + 0.5) * STEP) in level cm; i runs along
level x (south is +x), j along level y (west is +y). Pictures are written north up, east right.

Run from the plan folder:  python -B tools/phase7_groundcover.py sources    (slow part, once)
                           python -B tools/phase7_groundcover.py cover      (the classes, from sources.npz)
Nothing in Unreal is touched.
"""

import glob
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wieland_geo  # noqa: E402

DATA = "E:/Wieland1529_site_data"
ROOT = "review/phase7"
OUT = ROOT + "/ground"
STEP = 12.5
CELL = 50.0
SHIFT = np.array([15482.32, 5053.7, 0.0])
FT = wieland_geo.CM_PER_US_SURVEY_FOOT

ROADWAY, WALK, PAVING, LAWN, SOIL, BUILDING = 1, 2, 3, 4, 5, 6
NAMES = {0: "not decided", ROADWAY: "roadway (asphalt)", WALK: "public sidewalk (concrete)", PAVING: "private paving (concrete)",
         LAWN: "lawn", SOIL: "planting bed or bare soil", BUILDING: "under a building"}
COLOURS = {0: (255, 0, 255), ROADWAY: (70, 70, 75), WALK: (190, 190, 185), PAVING: (150, 145, 135), LAWN: (80, 140, 60),
           SOIL: (120, 90, 60), BUILDING: (200, 80, 60)}
EARLIER = {"MI_R15_asphalt_03_World": ROADWAY, "MI_R15_concrete_floor_03_World": WALK, "MI_R15_concrete_floor_03_UV": WALK,
           "MI_R15_turf_World": LAWN, "MI_R15_dirt_floor_World": SOIL, "MI_R15_wood_chips_World": SOIL,
           "B_MAT_Limestone_gravel": SOIL, "SS_R01_FadedParkingPaint_001": ROADWAY}


def grid():
    data = np.load(ROOT + "/heights/combined.npz")
    i0, j0 = int(data["i0"]), int(data["j0"])
    n_i, n_j = data["ground_p4"].shape
    scale = int(CELL / STEP)
    return i0 * CELL, j0 * CELL, n_i * scale, n_j * scale, data


def frame():
    return wieland_geo.LevelFrame.load("review/phase2/level_frame.json")


def to_picture(array):
    """Array indexed [i, j] to a picture with north up and east right (north is -x, east is -y)."""
    return array[:, ::-1]


def ortho_in_level(x0, y0, n_i, n_j):
    Image.MAX_IMAGE_PIXELS = None
    image = Image.open(DATA + "/county_ortho_2025.tif")
    tie = image.tag_v2[33922]
    pixel = image.tag_v2[33550]
    bands = np.asarray(image, dtype=np.float32)
    fr = frame()
    xs = x0 + (np.arange(n_i) + 0.5) * STEP
    ys = y0 + (np.arange(n_j) + 0.5) * STEP
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    theta = math.radians(fr.north_grid_bearing_deg)
    along_north = -(gx - fr.origin_x_cm) / FT
    along_east = -(gy - fr.origin_y_cm) / FT
    east = fr.origin_east_ft + along_north * math.sin(theta) + along_east * math.cos(theta)
    north = fr.origin_north_ft + along_north * math.cos(theta) - along_east * math.sin(theta)
    col = (east - tie[3]) / pixel[0] - 0.5
    row = (tie[4] - north) / pixel[1] - 0.5
    inside = (col >= 0) & (col <= bands.shape[1] - 1) & (row >= 0) & (row <= bands.shape[0] - 1)
    out = np.zeros((n_i, n_j, bands.shape[2]), dtype=np.float32)
    for band in range(bands.shape[2]):
        out[:, :, band] = ndimage.map_coordinates(bands[:, :, band], [row, col], order=1, mode="nearest")
    out[~inside] = 0
    return out, inside


def polygons_mask(path, x0, y0, n_i, n_j):
    fr = frame()
    with open(path, encoding="utf-8") as handle:
        features = json.load(handle)["features"]
    picture = Image.new("L", (n_j, n_i), 0)
    draw = ImageDraw.Draw(picture)
    for feature in features:
        for ring in feature["geometry"]["rings"]:
            points = []
            for east, north in ring:
                x, y = fr.level_from_map(east, north)
                points.append(((y - y0) / STEP, (x - x0) / STEP))
            draw.polygon(points, fill=1)
    return np.asarray(picture, dtype=bool)


def earlier_ground(x0, y0, n_i, n_j):
    """The ground of the earlier parts, drawn triangle by triangle: class per cell, 0 where they have none."""
    picture = Image.new("L", (n_j, n_i), 0)
    draw = ImageDraw.Draw(picture)
    order = (SOIL, LAWN, WALK, ROADWAY)   # drawn in this order; the later one wins where they overlap
    jobs = {k: [] for k in order}
    for path in sorted(glob.glob(ROOT + "/fit/raw/R15_PART_opaque_*.npz")):
        raw = np.load(path)
        p = raw["positions"] + SHIFT
        t = raw["triangles"]
        names = [str(x).split("/")[-1] for x in raw["slot_materials"]]
        z_top = p[t][:, :, 2].max(axis=1)
        normal = np.cross(p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]])
        flat = np.abs(normal[:, 2]) > 0.7 * np.linalg.norm(normal, axis=1).clip(1e-9)
        for k, name in enumerate(names):
            if name not in EARLIER:
                continue
            chosen = (raw["material_ids"] == k) & (z_top <= 25.0) & flat
            jobs[EARLIER[name]].append(p[t[chosen]][:, :, :2])
    for cls in order:
        for block in jobs[cls]:
            for tri in block:
                draw.polygon([((y - y0) / STEP, (x - x0) / STEP) for x, y in tri], fill=cls)
    return np.asarray(picture, dtype=np.uint8)


def colour(classes):
    out = np.zeros(classes.shape + (3,), dtype=np.uint8)
    for k, c in COLOURS.items():
        out[classes == k] = c
    return out


def sources():
    os.makedirs(OUT, exist_ok=True)
    x0, y0, n_i, n_j, data = grid()
    ortho, inside = ortho_in_level(x0, y0, n_i, n_j)
    Image.fromarray(to_picture(ortho[:, :, :3]).astype(np.uint8)).save(OUT + "/ortho_level.png")
    parcels = polygons_mask(DATA + "/county_parcels_2025.json", x0, y0, n_i, n_j)
    footprints = polygons_mask(DATA + "/county_footprints_2022.json", x0, y0, n_i, n_j)
    earlier = earlier_ground(x0, y0, n_i, n_j)
    np.savez_compressed(OUT + "/sources.npz", ortho=ortho.astype(np.uint8), inside=inside, parcels=parcels,
                        footprints=footprints, earlier=earlier, x0=x0, y0=y0, step=STEP)
    look = np.concatenate([to_picture(ortho[:, :, :3]).astype(np.uint8), to_picture(colour(earlier)),
                           to_picture(np.stack([parcels * 200, footprints * 200, inside * 60], axis=2).astype(np.uint8))], axis=1)
    Image.fromarray(look).resize((look.shape[1] // 2, look.shape[0] // 2), Image.LANCZOS).save(OUT + "/sources_look.png")
    a = ortho[:, :, 3]
    print(json.dumps({"grid": [x0, y0, n_i, n_j, STEP], "ortho_inside_share": round(float(inside.mean()), 3),
                      "band4_min_max_mean": [float(a[inside].min()), float(a[inside].max()), round(float(a[inside].mean()), 1)],
                      "parcels_share": round(float(parcels.mean()), 3), "footprints_share": round(float(footprints.mean()), 3),
                      "earlier_cells_by_class": {NAMES[k]: int((earlier == k).sum()) for k in NAMES if k}}))


SIDEWALK_CM = 362.0      # parcel line to kerb face on Wieland, measured on the earlier parts' roadway (1st percentile)
CORNER_CM = 300.0        # radius of the kerb at street corners
ALLEY_CM = 760.0         # a public way narrower than this is an alley: paved wall to wall, no kerb
GREEN = 0.35             # vegetation index (near infrared against red) above which the photograph shows plants
LOW_M = 0.6              # plants lower than this above the ground are lawn or beds, not shrubs or tree crowns
LAWN_MIN_WIDTH_CM = 150.0   # a strip of low plants narrower than this is not counted as lawn
LAWN_MIN_AREA_M2 = 4.0      # nor is a patch smaller than this
LOT_RECT = (-1508.76, 0.0, -3115.1, 0.0)   # x_min, x_max, y_min, y_max of the lot of 1529


def height_above_ground(x0, y0, n_i, n_j):
    """Laser scan 2022: first-return surface minus ground, metres, on the grid."""
    fr = frame()
    xs = x0 + (np.arange(n_i) + 0.5) * STEP
    ys = y0 + (np.arange(n_j) + 0.5) * STEP
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    theta = math.radians(fr.north_grid_bearing_deg)
    along_north = -(gx - fr.origin_x_cm) / FT
    along_east = -(gy - fr.origin_y_cm) / FT
    east = fr.origin_east_ft + along_north * math.sin(theta) + along_east * math.cos(theta)
    north = fr.origin_north_ft + along_north * math.cos(theta) - along_east * math.sin(theta)
    out = []
    for name in ("isgs_dsm_2022.tif", "isgs_dtm_2022.tif"):
        image = Image.open(DATA + "/" + name)
        tie = image.tag_v2[33922]
        pixel = image.tag_v2[33550]
        values = np.asarray(image, dtype=np.float32)
        col = (east - tie[3]) / pixel[0] - 0.5
        row = (tie[4] - north) / pixel[1] - 0.5
        out.append(ndimage.map_coordinates(values, [row, col], order=1, mode="nearest"))
    return (out[0] - out[1]) * 0.3048006


def parcel_shapes():
    from shapely.geometry import Polygon
    fr = frame()
    with open(DATA + "/county_parcels_2025.json", encoding="utf-8") as handle:
        features = json.load(handle)["features"]
    shapes = []
    for feature in features:
        for ring in feature["geometry"]["rings"]:
            shape = Polygon([fr.level_from_map(east, north) for east, north in ring])
            if not shape.is_valid:
                shape = shape.buffer(0)
            if shape.area > 1e4:
                shapes.append(shape)
    return shapes


def draw_shape(draw, shape, x0, y0, value):
    parts = getattr(shape, "geoms", [shape])
    for part in parts:
        if part.is_empty or part.geom_type != "Polygon":
            continue
        draw.polygon([((y - y0) / STEP, (x - x0) / STEP) for x, y in part.exterior.coords], fill=value)
        for hole in part.interiors:
            draw.polygon([((y - y0) / STEP, (x - x0) / STEP) for x, y in hole.coords], fill=0)


def cover():
    from shapely.geometry import box
    from shapely.ops import unary_union
    src = np.load(OUT + "/sources.npz")
    x0, y0 = float(src["x0"]), float(src["y0"])
    n_i, n_j = src["parcels"].shape
    ortho = src["ortho"].astype(np.float32)
    inside, footprints, earlier = src["inside"], src["footprints"], src["earlier"]
    shapes = parcel_shapes()
    # The parcel data ends before the grid does; the public way is worked out where parcels are known.
    known = box(x0, y0, x0 + n_i * STEP, y0 + n_j * STEP)
    parcels = unary_union(shapes).buffer(15).buffer(-15)     # close the slivers between neighbours
    public = known.difference(parcels)
    wide = public.buffer(-ALLEY_CM / 2).buffer(ALLEY_CM / 2 + 5)
    alleys = public.difference(wide).buffer(-20).buffer(20)
    streets = public.difference(alleys.buffer(1))
    roadway = streets.buffer(-(SIDEWALK_CM + CORNER_CM)).buffer(CORNER_CM)
    # Alley mouths: the alley's paving runs through the sidewalk to the roadway.
    mouths = alleys.buffer(SIDEWALK_CM + 60).intersection(streets).difference(roadway)
    mouths = mouths.buffer(-150).buffer(150)

    def mask(shape):
        picture = Image.new("L", (n_j, n_i), 0)
        draw_shape(ImageDraw.Draw(picture), shape, x0, y0, 1)
        return np.asarray(picture, dtype=bool)

    m_public, m_alley, m_road, m_mouth = mask(public), mask(alleys), mask(roadway), mask(mouths)
    red, near = ortho[:, :, 0], ortho[:, :, 3]
    green = ((near - red) / (near + red + 1e-6) > GREEN) & inside
    low = height_above_ground(x0, y0, n_i, n_j) < LOW_M
    # Strips narrower than LAWN_MIN_WIDTH_CM and patches smaller than LAWN_MIN_AREA_M2 are dropped: the edge of a
    # tree crown reads as "green and low" in a thin ring, which showed as dark outlines on the paving.
    reach = int(round(LAWN_MIN_WIDTH_CM / 2.0 / STEP))
    grid_i, grid_j = np.ogrid[-reach:reach + 1, -reach:reach + 1]
    plants = ndimage.binary_opening(green & low, structure=(grid_i ** 2 + grid_j ** 2) <= reach ** 2)
    labels, count = ndimage.label(plants)
    if count:
        sizes = ndimage.sum(plants, labels, index=np.arange(1, count + 1))
        small = np.concatenate([[False], sizes < LAWN_MIN_AREA_M2 * 1e4 / (STEP * STEP)])
        plants &= ~small[labels]

    # Parcels that hold no building are car parks: asphalt.
    car_park = np.zeros((n_i, n_j), dtype=bool)
    for shape in shapes:
        if shape.area < 300e4:
            continue
        b = shape.bounds
        i_a, i_b = max(int((b[0] - x0) / STEP), 0), min(int((b[2] - x0) / STEP) + 1, n_i)
        j_a, j_b = max(int((b[1] - y0) / STEP), 0), min(int((b[3] - y0) / STEP) + 1, n_j)
        if i_b <= i_a or j_b <= j_a:
            continue
        picture = Image.new("L", (j_b - j_a, i_b - i_a), 0)
        draw_shape(ImageDraw.Draw(picture), shape, x0 + i_a * STEP, y0 + j_a * STEP, 1)
        local = np.asarray(picture, dtype=bool)
        if local.sum() and footprints[i_a:i_b, j_a:j_b][local].mean() < 0.05:
            car_park[i_a:i_b, j_a:j_b] |= local

    classes = np.full((n_i, n_j), PAVING, dtype=np.uint8)
    classes[car_park] = ROADWAY
    # The earlier parts' asphalt on private land, without strips narrower than 2 m: the rims of the earlier
    # parts' pads and beds drew thin asphalt outlines on the paving.
    grid_i, grid_j = np.ogrid[-8:9, -8:9]
    classes[ndimage.binary_opening((earlier == ROADWAY) & ~m_public, structure=(grid_i ** 2 + grid_j ** 2) <= 64)] = ROADWAY
    classes[plants & ~m_public] = LAWN
    classes[footprints & ~m_public] = BUILDING
    classes[m_public] = WALK
    classes[m_public & plants & ~m_road] = LAWN
    classes[m_public & (earlier == SOIL) & ~m_road] = SOIL
    classes[m_public & (earlier == LAWN) & ~m_road] = LAWN
    classes[m_alley | m_mouth] = ROADWAY
    classes[m_road] = ROADWAY
    i_a, i_b = int((LOT_RECT[0] - x0) / STEP), int((LOT_RECT[1] - x0) / STEP)
    j_a, j_b = int((LOT_RECT[2] - y0) / STEP), int((LOT_RECT[3] - y0) / STEP)
    classes[i_a:i_b, j_a:j_b] = PAVING       # the lot of 1529: its own paving is the house model's; placeholder below it

    # Kerb lines: the edge of the roadway, without the alley mouths and without the rim of the grid.
    rim = known.buffer(-100).boundary.buffer(150)
    lines = roadway.boundary.difference(mouths.buffer(40)).difference(alleys.buffer(40)).difference(rim)
    kerbs = []
    for line in getattr(lines, "geoms", [lines]):
        if line.length > 200:
            kerbs.append([[round(x, 1), round(y, 1)] for x, y in line.simplify(2.0).coords])
    with open(OUT + "/kerb_lines.json", "w", encoding="utf-8") as handle:
        json.dump({"unit": "level cm", "lines": kerbs}, handle)

    with open(OUT + "/shapes.json", "w", encoding="utf-8") as handle:
        json.dump({"unit": "level cm", "roadway": roadway.wkt, "alleys": alleys.wkt, "mouths": mouths.wkt}, handle)

    # The picture the ground material reads: red asphalt, green lawn, blue soil, alpha private paving; what is
    # left is public sidewalk. The street's roadway is its own mesh with its own asphalt, so here it counts as
    # sidewalk: the soft edge of this picture then cannot put asphalt on the sidewalk beside the kerb.
    flush = m_alley | m_mouth
    asphalt = (classes == ROADWAY) & (~m_road | flush)
    layers = [asphalt, classes == LAWN, classes == SOIL, (classes == PAVING) | (classes == BUILDING)]
    picture = np.stack([np.clip(ndimage.gaussian_filter(layer.astype(np.float32), 0.6) * 255.0 + 0.5, 0, 255).astype(np.uint8)
                        for layer in layers], axis=2)
    # row = cell along x, column = cell along y: the material reads U along level y and V along level x
    # 4096 pixels over the same ground (7.5 cm each): a power of two, so that Unreal can make the smaller copies it shows far away
    # Each channel is resized on its own: resizing the four together lets the fourth (as transparency) wipe the
    # other three wherever it is zero, which took the asphalt off the car parks and most of the lawn away.
    # The fourth channel is stored upside down (255 = not private paving) so that it is never zero where another
    # channel has something to say; the material turns it back.
    picture[:, :, 3] = 255 - picture[:, :, 3]
    channels = [Image.fromarray(np.ascontiguousarray(picture[:, :, k]), "L").resize((4096, 4096), Image.BILINEAR) for k in range(4)]
    Image.merge("RGBA", channels).save(OUT + "/T_W1529_SiteCover.tga")
    np.savez_compressed(OUT + "/cover.npz", classes=classes, flush=flush, road=m_road, x0=x0, y0=y0, step=STEP)
    cell_m2 = (STEP / 100.0) ** 2
    summary = {"grid_origin_cm": [x0, y0], "cells": [n_i, n_j], "cell_cm": STEP,
               "area_m2": {NAMES[k]: round(float((classes == k).sum()) * cell_m2) for k in NAMES},
               "kerb_lines": len(kerbs), "kerb_length_m": round(sum(l.length for l in getattr(lines, "geoms", [lines])) / 100.0),
               "rules": {"public way": "what is not a county parcel (2025)",
                         "roadway": "public way further than %.0f cm from a parcel, corners rounded at %.0f cm; the distance is the 1st percentile measured on the earlier parts' roadway on Wieland" % (SIDEWALK_CM, CORNER_CM),
                         "alley": "public way narrower than %.0f cm: paved wall to wall, no kerb, and through the sidewalk at its mouth" % ALLEY_CM,
                         "lawn": "the 2025 photograph shows plants (near infrared against red above %.2f) and the 2022 laser scan shows them lower than %.1f m; strips narrower than %.0f cm and patches under %.0f m2 are dropped (rings at the edge of tree crowns)" % (GREEN, LOW_M, LAWN_MIN_WIDTH_CM, LAWN_MIN_AREA_M2),
                         "tree pits and beds in the sidewalk": "taken from the earlier parts' own ground where they have it",
                         "car park": "a parcel over 300 m2 of which under 5 percent is building, and the earlier parts' asphalt",
                         "private paving": "everything else inside a parcel that is not building"}}
    with open(OUT + "/cover_summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=1)
    preview = to_picture(colour(classes)).copy()
    picture = Image.fromarray(preview)
    draw = ImageDraw.Draw(picture)
    for line in kerbs:
        draw.line([(n_j - 1 - (y - y0) / STEP, (x - x0) / STEP) for x, y in line], fill=(255, 255, 0), width=2)
    both = np.concatenate([to_picture(ortho[:, :, :3]).astype(np.uint8), np.asarray(picture)], axis=1)
    Image.fromarray(both).resize((both.shape[1] // 2, both.shape[0] // 2), Image.LANCZOS).save(OUT + "/cover_preview.png")
    half = 320
    c_i, c_j = int((-750 - x0) / STEP), int((300 - y0) / STEP)
    crop = np.concatenate([ortho[c_i - half:c_i + half, c_j - half:c_j + half, :3].astype(np.uint8)[:, ::-1],
                           np.asarray(picture)[c_i - half:c_i + half, n_j - c_j - half:n_j - c_j + half]], axis=1)
    Image.fromarray(crop).resize((crop.shape[1] * 3 // 2, crop.shape[0] * 3 // 2), Image.LANCZOS).save(OUT + "/cover_preview_lot.png")
    print(json.dumps(summary["area_m2"]), summary["kerb_lines"], summary["kerb_length_m"])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sources":
        sources()
    elif len(sys.argv) > 1 and sys.argv[1] == "cover":
        cover()
    else:
        print(__doc__)
