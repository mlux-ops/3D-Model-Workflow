"""Phase 10, steps 10.3 to 10.6: one sheet per station S1 to S9 and the score of every tolerance that applies
at each station.

    python -B review/phase10/scripts/station_sheets.py <site data folder> [station ...]

Run from the plan folder. Without station names every sheet is made. Nothing in Unreal is touched.

Street stations (S1 to S6, S9), four panels: "PLACEHOLDER: no photograph", the path-traced picture of Phase 12,
the real-time picture of this phase (run R1), and the difference between the two (white = same, red = real-time
brighter, blue = real-time darker, full colour at two stops; picture luminance with the sRGB curve undone, as
in review/phase8/scripts/compare_tiers.py). Under them: the score of each tolerance that applies.
S7: a sheet that says why the station cannot exist.
S8: the plan picture, and the same picture with the lot (red), the county's 2022 building outlines (cyan) and
the 34 tree data points (green) drawn over it from data, at ground level. The camera stands 2 km up, so a
roof 12 m high at the picture's edge is drawn 0.36 m further out than its foot; outlines are drawn at their
foot. The county's aerial photograph is never written into the repository: the sheet that lays it beside the
plan picture is written to <site data folder>/phase10/S8_plan_beside_aerial.jpg. Nothing is traced from the
aerial photograph and no colour is taken from it.

Writes review/phase10/sheets/<station>_sheet.jpg and review/phase10/station_scores.csv.
"""
import csv
import json
import math
import os
import sys
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
sys.path.insert(0, "tools")
import site_analysis  # noqa: E402
import wieland_geo  # noqa: E402

PANEL = (1280, 720)
MARGIN = 24
TITLE = 64
LINE = 25
WRAP = 235
RED = (160, 0, 0)
OUT = "review/phase10/sheets"
TRUTH = "review/phase12/ground_truth/%s_pathtraced.0000.png"
REAL = "review/phase10/realtime/R1/%s_realtime.0000.png"
PLAN = "review/phase10/realtime/S8/S8_realtime.0000.png"
STREET = ("S1", "S2", "S3", "S4", "S5", "S6", "S9")
PLAN_CENTRE = (-754.4, -1557.5)
PLAN_HALF_CM = 6000.0
PLAN_YAW = 181.18
LOT = ((0.0, 0.0), (-1508.8, 0.0), (-1508.8, -3115.0), (0.0, -3115.0))


def font(size):
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


BIG, MID, SMALL = font(30), font(22), font(19)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def luminance(picture):
    c = np.asarray(picture.convert("RGB"), dtype=np.float32) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def difference(truth, real):
    stops = np.log2((luminance(real) + 0.003) / (luminance(truth) + 0.003))
    v = np.clip(stops / 2.0, -1.0, 1.0)
    out = np.ones(v.shape + (3,), dtype=np.float32)
    brighter, darker = np.clip(v, 0, 1), np.clip(-v, 0, 1)
    out[..., 1] -= brighter + darker
    out[..., 2] -= brighter
    out[..., 0] -= darker
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def placeholder(draw, box, lines):
    draw.rectangle(box, fill=(235, 235, 235), outline=RED, width=3)
    draw.text((box[0] + 30, box[1] + 30), lines[0], fill=RED, font=BIG)
    y = box[1] + 84
    for line in lines[1:]:
        draw.text((box[0] + 30, y), line, fill=(60, 60, 60), font=MID)
        y += 30


def label(draw, box, text):
    width = draw.textlength(text, font=MID) + 16
    draw.rectangle((box[0], box[1], box[0] + width, box[1] + 32), fill=(255, 255, 255))
    draw.text((box[0] + 8, box[1] + 3), text, fill=(0, 0, 0), font=MID)


def foot_lines(scores):
    lines = []
    for tolerance, measured, verdict, missing in scores:
        text = "%s: %s  VERDICT: %s." % (tolerance, measured, verdict)
        if missing:
            text += "  Missing evidence: " + missing
        wrapped = textwrap.wrap(text, WRAP)
        lines.append(wrapped[0])
        lines.extend("      " + more for more in wrapped[1:])
    return lines


def new_sheet(title, rows_of_panels, lines):
    width = PANEL[0] * 2 + MARGIN * 3
    height = MARGIN + TITLE + rows_of_panels * (PANEL[1] + MARGIN) + len(lines) * LINE + MARGIN
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.text((MARGIN, MARGIN), title, fill=(0, 0, 0), font=BIG)
    y = MARGIN + TITLE + rows_of_panels * (PANEL[1] + MARGIN)
    for line in lines:
        draw.text((MARGIN, y), line, fill=(0, 0, 0), font=SMALL)
        y += LINE
    return sheet, draw


def box(row, column, size=PANEL):
    left = MARGIN + column * (PANEL[0] + MARGIN)
    top = MARGIN + TITLE + row * (PANEL[1] + MARGIN)
    return (left, top, left + size[0], top + size[1])


# ---- numbers measured in this phase
stations = {row["station"].split(" ")[0]: row for row in read_csv("review/phase2/stations.csv")}
cameras = {row["station"]: row for row in read_csv("review/phase10/stations_check.csv")}
tiers = {row["view"]: row for row in read_csv("review/phase10/compare/R1/compare.csv")}
ties = [float(row["corner_distance_cm"]) for row in read_csv("review/phase10/survey_ties_now.csv")]
trees = read_csv("review/phase10/trees_check.csv")
tree_data = read_csv("review/phase7/vegetation/tree_positions.csv")
with open("review/phase10/neighbours_now.json", encoding="utf-8") as handle:
    neighbours = json.load(handle)
with open("review/phase10/ground_now.json", encoding="utf-8") as handle:
    ground = json.load(handle)
z1 = neighbours["zone_1"]
at_point = sum(1 for row in trees if float(row["trunk_from_data_point_m"]) <= 0.3)

WALLS = ("Neighbours' street walls (0.3 m)",
         "today's walls stand %.0f to %.0f cm from the five points the plat of survey ties to them; against the "
         "county's 2022 outlines %d of %d building sides within 40 m are within 0.5 m, largest %.1f m (same figure "
         "at every station)" % (min(ties), max(ties), z1["sides"]["within_0.5_m"], z1["sides"]["measured"],
                                z1["sides"]["largest_m"]),
         "pass at the surveyed points; %d sides fail against the county outline"
         % (z1["sides"]["measured"] - z1["sides"]["within_0.5_m"]),
         "a tape from the lot corners to each neighbour's wall.")
HEIGHTS = ("Neighbours' heights (0.3 m)",
           "%d of %d buildings within 40 m are within 0.3 m of the 2022 laser scan, middle value %.2f m, largest "
           "%.2f m; number 1533 +1.10 m, number 1525 -1.02 m, rear building -1.30 m (same figure at every station)"
           % (z1["roof"]["within_0.3_m"], z1["roof"]["measured"], z1["roof"]["median_m"], z1["roof"]["largest_m"]),
           "fail", "")
GROUND = ("Ground, kerb and sidewalk levels (0.1 m to the lot, 0.2 m absolute)",
          "against the 2022 laser ground: pavements in front of the lot all within 0.1 m (largest %.1f cm); the "
          "roadway lies %.1f cm lower; %.1f%% of all ground within 0.2 m (same figure at every station)"
          % (ground["pavements_in_front_of_the_lot"]["largest_cm"], -ground["roadway_pieces"]["median_cm"],
             ground["everything_measured"]["share_within_20_cm"] * 100),
          "pass for 0.2 m; pass for 0.1 m on pavements; fail for 0.1 m on the roadway", "survey spot levels.")
TREES = ("Trees (trunk 0.3 m, diameter 2 cm, height and crown 1.0 m, species named)",
         "height: %d of %d at the height of the 2022 laser scan; trunk: %d of %d at the scan's crown-top point, %d "
         "moved 1.1 to 3.6 m off a roadway or out of a building; diameter and species not measured"
         % (len(trees), len(trees), at_point, len(trees), len(trees) - at_point),
         "height passes against the scan; trunk position, diameter and species could not be checked",
         "a tape to each trunk, a girth tape, and bark, buds or leaves seen on site.")
FURNITURE = ("Poles, hydrant, signs, fences, stoops (0.3 m)",
             "this plan placed none; the earlier detailed model of the neighbours carries its own stoops, railings, "
             "fences and a utility pole with wires inside its merged meshes, compared with nothing",
             "could not be checked", "each item taped on site.")
SUN = ("Sun direction (0.5 degree)", "0.05 degree off the NOAA calculator in bearing and 0.05 in height", "pass", "")
SHADOW = ("Shadow edges on the ground (0.3 m)",
          "not measured; in its place the shadow of a 3.00 m test pole is 4.6 cm longer than calculated (Phase 8)",
          "could not be checked", "a photograph with its time of capture.")
COLOUR = ("Colour of principal materials (colour difference 5)", "not measured", "could not be checked",
          "a photograph of each material with a grey card in it.")
SIDEWALK = ("Brightness of sunlit sidewalk (one third of a stop)",
            "not measured; in its place the sunlit sidewalk reads 0.09 stop over middle grey (Phase 8)",
            "could not be checked", "a photograph of the sunlit sidewalk with a grey card in it.")


def street_scores(station):
    camera, tier = cameras[station], tiers[station]
    regions = tier["failing_regions"]
    return [
        ("Camera station (0.1 m, 0.05 m eye height, 0.5 degree)",
         "%.1f cm and %.2f degree from the surveyed station list; eye %.1f cm over today's ground (target 160); "
         "tilted up %.0f degrees, lens %.1f degrees across"
         % (float(camera["position_difference_cm"]), abs(float(camera["heading_difference_deg"])),
            float(camera["eye_height_cm"]), float(camera["camera_upward_tilt_deg"]), float(camera["lens_deg_across"])),
         "matches the list; against reality could not be checked",
         "the station taped on site and the lens read from the photograph's file."),
        ("Photograph and render overlay (1.5 percent of image width)", "not measured", "could not be checked",
         "the owner's photograph at this station."),
        ("Real-time against path-traced (mean 10 percent; no region over 2 percent of frame off by a stop)",
         "mean brightness %+.1f percent; largest region off by over one stop %.2f percent of the frame%s"
         % (float(tier["mean_difference_percent"]), float(tier["largest_region_percent"]),
            (" (" + regions + ")") if regions else ""),
         "pass" if tier["passes"] == "True" else "fail", ""),
        WALLS, HEIGHTS, GROUND, TREES, FURNITURE, SUN, SHADOW, COLOUR, SIDEWALK,
    ]


S7_SCORES = [("Every tolerance", "no picture can be made: the station cannot be stood on", "does not apply",
              "none; a rear view is a design view taken from the building's own rear decks.")]
S8_SCORES = [
    ("The lot in the world (1.0 m)",
     "lot corners convert between map and level with 0.000 m; the red outline in the right panel is drawn from the "
     "same conversion (Phase 2)", "pass", ""),
    ("True north (0.2 degree)",
     "street grid 1.17 degrees off true north by parcel lines and 1.14 by building walls; the picture's up is true "
     "north by the camera's heading (Phase 2)", "pass", "the survey carries no bearing."),
    ("The building on its lot (0.05 m)", "street corners 0.1 to 0.3 mm from the lot's lines plus setbacks (Phase 3)",
     "pass", "the owner's decision 7 (which frontage governs) is open."),
    WALLS, HEIGHTS,
    ("Tree trunk position (0.3 m; 1.0 m from scan and aerial alone)",
     "%d of %d trunks at the scan's crown-top point (green rings), %d moved 1.1 to 3.6 m"
     % (at_point, len(trees), len(trees) - at_point), "could not be checked", "a tape to each trunk."),
    FURNITURE,
    ("Plan picture against the county's aerial photograph (1.5 percent of image width = 1.8 m)",
     "laid side by side outside the repository and looked at; no number, because nothing may be traced from the "
     "aerial photograph in these sessions", "could not be checked by number",
     "the owner's look at the side-by-side sheet, or the owner's leave to measure on the aerial photograph."),
]


def street_sheet(station):
    row = stations[station]
    scores = street_scores(station)
    title = "1529 N. Wieland, Phase 10, station %s: %s" % (row["station"], row["note"])
    sheet, draw = new_sheet(title, 2, foot_lines(scores))
    truth = Image.open(TRUTH % station).convert("RGB").resize(PANEL, Image.LANCZOS)
    real = Image.open(REAL % station).convert("RGB").resize(PANEL, Image.LANCZOS)
    placeholder(draw, box(0, 0), ["PLACEHOLDER: no photograph.",
                                   "No site visit has been made and the owner has taken no photograph,",
                                   "so there is nothing to compare these pictures with at this station",
                                   "and no camera was solved from a photograph.",
                                   "Street imagery was not opened, saved, traced or sampled."])
    sheet.paste(truth, box(0, 1)[:2])
    label(draw, box(0, 1), "Path-traced picture (Phase 12), summer afternoon")
    sheet.paste(real, box(1, 0)[:2])
    label(draw, box(1, 0), "Real-time picture (today, after a fresh start of the editor)")
    sheet.paste(difference(truth, real), box(1, 1)[:2])
    label(draw, box(1, 1), "Difference: red = real-time brighter, blue = darker, full colour at two stops")
    return sheet, scores


def s7_sheet():
    row = stations["S7"]
    title = "1529 N. Wieland, Phase 10, station %s" % row["station"]
    sheet, draw = new_sheet(title, 1, foot_lines(S7_SCORES))
    placeholder(draw, box(0, 0), ["NO PICTURE: this station cannot exist.",
                                   "There is no alley behind the lot. The rear lot line meets the",
                                   "neighbours' lots, with a four-storey building 0.2 to 0.3 ft beyond it.",
                                   "The point the plan had chosen lies inside the rear neighbour's lot",
                                   "and cannot be stood on (review/phase2/stations.csv)."])
    placeholder(draw, box(0, 1), ["PLACEHOLDER: no photograph.",
                                   "None can be taken from this point either.",
                                   "The rear of the building is shown by design view D5,",
                                   "taken from the building's own rear deck."])
    return sheet, S7_SCORES


def plan_pixel(x, y, size):
    yaw = math.radians(PLAN_YAW)
    up = (math.cos(yaw), math.sin(yaw))
    right = (-math.sin(yaw), math.cos(yaw))
    dx, dy = x - PLAN_CENTRE[0], y - PLAN_CENTRE[1]
    scale = size / (2.0 * PLAN_HALF_CM)
    return (size / 2.0 + (dx * right[0] + dy * right[1]) * scale, size / 2.0 - (dx * up[0] + dy * up[1]) * scale)


def level_of_pixel(px, py, size):
    yaw = math.radians(PLAN_YAW)
    up = (math.cos(yaw), math.sin(yaw))
    right = (-math.sin(yaw), math.cos(yaw))
    u = (px - size / 2.0) * (2.0 * PLAN_HALF_CM) / size
    v = (size / 2.0 - py) * (2.0 * PLAN_HALF_CM) / size
    return PLAN_CENTRE[0] + u * right[0] + v * up[0], PLAN_CENTRE[1] + u * right[1] + v * up[1]


def s8_sheet(data_folder):
    side = PANEL[0]
    frame = wieland_geo.LevelFrame.load("review/phase2/level_frame.json")
    plan = Image.open(PLAN).convert("RGB").resize((side, side), Image.LANCZOS)
    marked = plan.copy()
    draw = ImageDraw.Draw(marked)
    _, footprints = site_analysis.load_polygons(os.path.join(data_folder, "county_footprints_2022.json"))
    drawn = 0
    for _, shape in footprints:
        polygons = [shape] if shape.geom_type == "Polygon" else list(getattr(shape, "geoms", []))
        for polygon in polygons:
            points = [plan_pixel(*frame.level_from_map(east, north), side) for east, north in polygon.exterior.coords]
            if any(0 <= px < side and 0 <= py < side for px, py in points):
                draw.line(points, fill=(0, 255, 255), width=2)
                drawn += 1
    for item in tree_data:
        px, py = plan_pixel(float(item["data_x_cm"]), float(item["data_y_cm"]), side)
        draw.ellipse((px - 6, py - 6, px + 6, py + 6), outline=(0, 255, 0), width=2)
    corners = [plan_pixel(x, y, side) for x, y in LOT]
    draw.line(corners + corners[:1], fill=(255, 0, 0), width=3)

    title = "1529 N. Wieland, Phase 10, station S8 Plan: straight down over the lot centre, 120 m by 120 m, true north up"
    lines = foot_lines(S8_SCORES)
    width = side * 2 + MARGIN * 3
    height = MARGIN + TITLE + side + MARGIN + len(lines) * LINE + MARGIN
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    sdraw = ImageDraw.Draw(sheet)
    sdraw.text((MARGIN, MARGIN), title, fill=(0, 0, 0), font=BIG)
    left = (MARGIN, MARGIN + TITLE)
    right = (MARGIN * 2 + side, MARGIN + TITLE)
    sheet.paste(plan, left)
    label(sdraw, left + left, "Real-time plan picture (today). The aerial photograph is kept outside the repository.")
    sheet.paste(marked, right)
    label(sdraw, right + right, "Same, with the lot (red), county 2022 building outlines (cyan), tree data points (green)")
    y = MARGIN + TITLE + side + MARGIN
    for line in lines:
        sdraw.text((MARGIN, y), line, fill=(0, 0, 0), font=SMALL)
        y += LINE

    # The aerial photograph beside the plan picture: outside the repository only.
    with open(os.path.join(data_folder, "fetch_record.json"), encoding="utf-8") as handle:
        record = json.load(handle)["results"]
    ortho = site_analysis.Raster(os.path.join(data_folder, "county_ortho_2025.tif"), record["county_ortho_2025.tif"]["box"])
    aerial = np.zeros((side, side, 3), dtype=np.uint8)
    for py in range(side):
        for px in range(side):
            east, north = frame.map_from_level(*level_of_pixel(px + 0.5, py + 0.5, side))
            col, row_ = ortho.pixel(east, north)
            if 0 <= int(col) < ortho.cols and 0 <= int(row_) < ortho.rows:
                aerial[py, px] = ortho.data[int(row_), int(col), :3]
    outside = Image.new("RGB", (width, MARGIN + TITLE + side + MARGIN + 3 * LINE), (255, 255, 255))
    odraw = ImageDraw.Draw(outside)
    odraw.text((MARGIN, MARGIN), "1529 N. Wieland, Phase 10, station S8: county aerial photograph (2025 edition) beside the plan picture", fill=(0, 0, 0), font=BIG)
    outside.paste(Image.fromarray(aerial), left)
    label(odraw, left + left, "County aerial photograph, same 120 m square, true north up")
    outside.paste(plan, right)
    label(odraw, right + right, "Real-time plan picture (today)")
    y = MARGIN + TITLE + side + MARGIN
    for line in ("Kept outside the repository. For looking at only: nothing is traced from the aerial photograph and no colour is taken from it.",
                 "The plan camera stands 2 km up: a roof 12 m high at the picture's edge is drawn 0.36 m further out than its foot. The aerial photograph has its own lean of tall buildings.",
                 "The aerial photograph was flown with leaves off or on as the county flew it; the plan picture is a summer afternoon."):
        odraw.text((MARGIN, y), line, fill=(0, 0, 0), font=SMALL)
        y += LINE
    os.makedirs(os.path.join(data_folder, "phase10"), exist_ok=True)
    target = os.path.join(data_folder, "phase10", "S8_plan_beside_aerial.jpg")
    outside.save(target, quality=90)
    print(target, "(outside the repository);", drawn, "county outlines drawn in the repository's sheet")
    return sheet, S8_SCORES


def main(argv):
    data_folder = argv[1]
    wanted = argv[2:] or list(STREET) + ["S7", "S8"]
    os.makedirs(OUT, exist_ok=True)
    all_scores = {}
    for station in list(STREET) + ["S7", "S8"]:
        if station in STREET:
            scores = street_scores(station)
        else:
            scores = S7_SCORES if station == "S7" else S8_SCORES
        all_scores[station] = scores
        if station not in wanted:
            continue
        if station in STREET:
            sheet, _ = street_sheet(station)
        elif station == "S7":
            sheet, _ = s7_sheet()
        else:
            sheet, _ = s8_sheet(data_folder)
        target = os.path.join(OUT, station + "_sheet.jpg")
        sheet.save(target, quality=88)
        print(target, sheet.size)
    with open("review/phase10/station_scores.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["station", "sheet", "tolerance_and_limit", "measured", "verdict", "missing_evidence"])
        for station in sorted(all_scores):
            for tolerance, measured, verdict, missing in all_scores[station]:
                writer.writerow([station, "review/phase10/sheets/%s_sheet.jpg" % station, tolerance, measured, verdict, missing])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
