"""Phase 10: one row per tolerance of REFERENCE_VIEWS.md ("Tolerances proposed") with what was measured, against
what, the verdict, and the evidence that is missing where the verdict is "could not be checked".
Numbers measured in this phase are read from this phase's files; numbers of earlier phases are quoted with
their source. Writes review/phase10/tolerances.csv. Run from the plan folder."""
import csv
import json

with open("review/phase10/neighbours_now.json", encoding="utf-8") as handle:
    nb = json.load(handle)
with open("review/phase10/ground_now.json", encoding="utf-8") as handle:
    gr = json.load(handle)
with open("review/phase10/sun_now.json", encoding="utf-8") as handle:
    sun = [s for s in json.load(handle) if s["label"] == "LGT_Sun"][0]
with open("review/phase10/survey_ties_now.csv", encoding="utf-8") as handle:
    ties = [float(r["corner_distance_cm"]) for r in csv.DictReader(handle)]
with open("review/phase10/stations_check.csv", encoding="utf-8") as handle:
    st = list(csv.DictReader(handle))
with open("review/phase10/trees_check.csv", encoding="utf-8") as handle:
    tr = [r for r in csv.DictReader(handle) if r["in_level_today"] == "yes"]
with open("review/phase10/compare/R1/compare.csv", encoding="utf-8") as handle:
    rt = list(csv.DictReader(handle))

z1, allb = nb["zone_1"], nb["all"]
trunk = [float(r["trunk_from_data_point_m"]) for r in tr]
moved = [t for t in trunk if t > 0.3]
height = [abs(float(r["height_difference_m"])) for r in tr]
eye = max(abs(float(r["eye_height_difference_cm"])) for r in st)
place = max(float(r["position_difference_cm"]) for r in st)
heading = max(abs(float(r["heading_difference_deg"])) for r in st)
passed = [r["view"] for r in rt if r["passes"] == "True"]
failed = ["%s %+.1f%%" % (r["view"], float(r["mean_difference_percent"])) for r in rt if r["passes"] != "True"]
NOAA_BEARING, NOAA_HEIGHT = 241.67, 46.34
every = gr["everything_measured"]
rest = gr["everything_but_roadway"]
road = gr["roadway_pieces"]
front = gr["pavements_in_front_of_the_lot"]

rows = [
    ("The building on its lot", "0.05 m to the governing lot lines",
     "Street corners of the first-floor slab 0.1 to 0.3 mm from the lot's side lines plus setbacks and from the "
     "front setback (Phase 3). All 2,585 placed objects within 0.5 mm of their Datasmith place (Phase 6); the "
     "building has not been moved since.",
     "Revit model's lot lines and the record lot (49.50 ft wide)",
     "pass",
     "The owner has not said whether the survey's frontage (50.18 ft) or the record width (49.50 ft) governs "
     "(OPEN_DECISIONS.md, decision 7); against the survey's frontage the check is not made. The rear corners "
     "have no figure of their own in the drawings.",
     "phase3_results.md; phase6_results.md J6"),
    ("The lot in the world", "1.0 m",
     "Lot corners convert from map to level and back with 0.000 m; projection within 2.4 mm of the county's "
     "figures; east kerb within 0.3 m of the site plan (Phase 2).",
     "County parcel data, 2022 laser scan, site plan", "pass", "", "phase2_results.md"),
    ("True north", "0.2 degree",
     "Street grid 1.17 degrees west of true north by parcel lines and 1.14 by building walls: 0.03 degree "
     "apart; lot front line 1.18 (Phase 2).",
     "County parcel lines and 2022 building outlines", "pass",
     "The survey carries no bearing, so the tolerance's own evidence (survey bearings) does not exist; a second "
     "independent method stands in.",
     "phase2_results.md"),
    ("Neighbours' street walls, in plan, relative to the lot", "0.3 m (0.5 m from laser scan alone)",
     "At the five points the plat of survey ties to neighbours' walls, today's walls stand %s cm from the "
     "surveyed place (edges seen from above, 5 cm cells; largest %.0f cm). Against the county's 2022 outlines "
     "on a 0.5 m grid, Zone 1 (within 40 m): %d of %d building sides within 0.5 m, %d within 1.0 m, largest "
     "%.1f m, middle value %.1f m outside the outline."
     % (", ".join("%.0f" % t for t in ties), max(ties), z1["sides"]["within_0.5_m"], z1["sides"]["measured"],
        z1["sides"]["within_1.0_m"], z1["sides"]["largest_m"], z1["sides"]["median_m"]),
     "Plat of survey (August 2025); county outlines 2022",
     "pass at the five surveyed points; fail for %d of %d sides in Zone 1 (over 0.5 m from the county outline)"
     % (z1["sides"]["measured"] - z1["sides"]["within_0.5_m"], z1["sides"]["measured"]),
     "A tape from the lot corners to each neighbour's street wall (site visit). The county outline is a roof "
     "outline read from the air and is itself good to about 0.5 m.",
     "review/phase10/survey_ties_now.csv; review/phase10/neighbours_now.csv"),
    ("Neighbours' heights (parapet, eave, ridge)", "0.3 m",
     "Typical roof level of today's buildings against the 2022 laser scan. Zone 1 (within 40 m): %d of %d "
     "within 0.3 m, middle value %.2f m (today lower), largest %.2f m. All %d measured: %d within 0.3 m, %d off "
     "by more than 1 m, %d by more than 3 m, largest %.2f m. Number 1533 is 1.10 m higher than the scan, number "
     "1525 is 1.02 m lower, the rear building 1.30 m lower."
     % (z1["roof"]["within_0.3_m"], z1["roof"]["measured"], z1["roof"]["median_m"], z1["roof"]["largest_m"],
        allb["roof"]["measured"], allb["roof"]["within_0.3_m"], allb["roof"]["over_1_m"], allb["roof"]["over_3_m"],
        allb["roof"]["largest_m"]),
     "2022 laser scan (typical roof level per building, Phase 4)", "fail",
     "Laser readings on site would tighten the reference to 0.15 m; they are not needed to see this failure.",
     "review/phase10/neighbours_now.csv"),
    ("Ground, kerb and sidewalk levels", "0.1 m relative to the lot; 0.2 m absolute",
     "Today's ground against the 2022 laser ground over %.0f m2 outside buildings: %.1f%% within 0.2 m (largest "
     "%.0f cm). Within 0.1 m: %.1f%% of everything but the roadway (pavements in front of the lot: all, largest "
     "%.1f cm), but only %.1f%% of the roadway, which lies %.1f cm lower (middle value)."
     % (every["area_sq_m"], every["share_within_20_cm"] * 100, every["largest_cm"],
        rest["share_within_10_cm"] * 100, front["largest_cm"], road["share_within_10_cm"] * 100,
        -road["median_cm"]),
     "2022 laser scan, ground surface",
     "pass for 0.2 m absolute; pass for 0.1 m on pavements and yards; fail for 0.1 m on the roadway",
     "Survey spot levels (none exist).", "review/phase10/ground_now.json"),
    ("Tree trunk position", "0.3 m (1.0 m from laser scan and aerial alone)",
     "%d of %d trunks stand at the data point (0.0 m); %d were moved %.1f to %.1f m off a roadway or out of a "
     "building (Phase 7), read back from the level today."
     % (len(trunk) - len(moved), len(trunk), len(moved), min(moved), max(moved)),
     "Crown tops in the 2022 laser scan (not a survey of trunks)", "could not be checked",
     "A tape to each trunk from two fixed points (site visit). The data point is the crown's top, not the "
     "trunk, which is why 14 data points lie on a roadway or a building.",
     "review/phase10/trees_check.csv"),
    ("Tree trunk diameter", "2 cm at 1.37 m above ground", "Not measured.", "none", "could not be checked",
     "A girth tape on each trunk (site visit). No public record exists.", ""),
    ("Tree height and crown spread", "1.0 m",
     "%d of %d trees within 1.0 m of the data height (largest difference %.1f m); crown width set to the data "
     "width (Phase 7)." % (sum(1 for h in height if h <= 1.0), len(height), max(height)),
     "2022 laser scan, leaf-off", "pass against the laser scan",
     "Growth since 2022 is not known; a laser reading on site would show it.", "review/phase10/trees_check.csv"),
    ("Tree species", "named with a stated confidence",
     "No species is known; the %d models were chosen by shape only (%s)."
     % (len(tr), ", ".join("%d %s" % (sum(1 for r in tr if r["model"] == m), m)
                           for m in sorted({r["model"] for r in tr}))),
     "none", "could not be checked", "Bark, buds and form seen on site, or leaves in summer.",
     "phase7_results.md; review/phase10/trees_check.csv"),
    ("Poles, hydrant, signs, fences, stoops", "0.3 m in plan; 0.1 m in height under 3 m",
     "This plan placed none (street lights, hydrant, signs). The earlier detailed model of the neighbours carries "
     "its own stoops, railings, iron fences and at least one utility pole with wires (seen at S1 and S9) inside "
     "its merged meshes; they are not separate objects (review/phase10/furniture_now.json finds none) and their "
     "places were not compared with anything.",
     "none", "could not be checked",
     "Position and size of each item taped on site. No public record exists.",
     "site_gaps.md; phase7_results.md; review/phase10/furniture_now.json"),
    ("Camera station", "0.1 m in plan, 0.05 m in eye height, 0.5 degree in heading",
     "Against the surveyed station list: place %.1f cm, heading %.2f degree, eye height within %.1f cm of 1.60 m "
     "at the seven stations." % (place, heading, eye),
     "review/phase2/stations.csv (the list, not reality)", "could not be checked",
     "The station taped on site from two fixed points and the lens read from the photograph's file.",
     "review/phase10/stations_check.csv"),
    ("Photograph and render overlay", "fixed edges within 1.5 percent of image width", "Not measured.", "none",
     "could not be checked", "The owner's photograph at each station.", ""),
    ("Transfer from Revit to Unreal", "1 mm on a known dimension; 5 mm on floor levels; 10 mm on fixture positions",
     "Known dimension: 0.1 to 0.3 mm. Floor levels: 203.2, 528.3, 853.4 and 1,178.6 cm against 203.20, 528.32, "
     "853.44 and 1,178.56 (0.4 mm at most). Fixtures: all 2,585 placed objects within 0.5 mm of their Datasmith "
     "place.",
     "Drawings and the Datasmith export", "pass",
     "A Revit view from each design camera, to see fixture by fixture that nothing is missing (none exists; "
     "Revit is not opened by these sessions).",
     "phase3_results.md; phase6_results.md"),
    ("Sun direction", "0.5 degree in bearing and height against the NOAA calculator",
     "Read from the level today: bearing %.2f against %.2f (%.2f off), height %.2f against %.2f (%.2f off), "
     "15 August 2026 15:30 Central Daylight Time."
     % (sun["sun_true_bearing_deg"], NOAA_BEARING, abs(sun["sun_true_bearing_deg"] - NOAA_BEARING),
        sun["sun_height_deg"], NOAA_HEIGHT, abs(sun["sun_height_deg"] - NOAA_HEIGHT)),
     "NOAA solar calculator (figures recorded in Phase 8)", "pass", "",
     "review/phase10/sun_now.json; phase8_results.md"),
    ("Shadow edges on the ground", "0.3 m against the photograph taken at the same time",
     "No photograph. In its place (Phase 8): the shadow of a 3.00 m test pole is 4.6 cm longer than calculated.",
     "calculation only", "could not be checked", "A photograph with its time of capture.", "phase8_results.md"),
    ("Colour of principal materials", "colour difference 5 or less (CIEDE2000) on the grey card", "Not measured.",
     "none", "could not be checked", "A photograph of each principal material with a grey card in it.", ""),
    ("Brightness of sunlit sidewalk concrete", "within one third of a stop",
     "No photograph. In its place (Phase 8): the sunlit sidewalk reads 0.09 stop over middle grey at the fixed "
     "outdoor exposure; a grey card in sun reads 0.178 against 0.18.",
     "the render's own grey card", "could not be checked",
     "A photograph of the sunlit sidewalk with a grey card in it.", "phase8_results.md"),
    ("Real-time render against the path-traced render of the same view",
     "mean brightness within 10 percent; no region over 2 percent of the frame off by more than one stop",
     "After a fresh start of the editor, today: %d of 12 views pass (%s). Fail: %s."
     % (len(passed), ", ".join(passed), "; ".join(failed)),
     "Phase 12 path-traced pictures of the same twelve views",
     "pass at %d views; fail at %d" % (len(passed), 12 - len(passed)), "",
     "review/phase10/compare/R1/compare.csv"),
]
with open("review/phase10/tolerances.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["tolerance", "limit", "measured", "measured_against", "verdict",
                     "missing_evidence_or_open_point", "source"])
    writer.writerows(rows)
for row in rows:
    print(row[0], "|", row[4])
    print("   ", row[2])
