"""Phase 10, step 10.7: one sheet per design view D1 to D5 and the scores that apply at each.

    python -B review/phase10/scripts/design_sheets.py [view ...]

Run from the plan folder. Four panels: "PLACEHOLDER: no Revit view", the path-traced picture of Phase 12, the
real-time picture of this phase (run R1) and their difference (as in station_sheets.py). Under them: the
Revit-transfer numbers of Phases 3 and 6, the real-time score of this phase and what waits on the owner.
Writes review/phase10/sheets/<view>_sheet.jpg and review/phase10/design_scores.csv. Nothing in Unreal is touched.
"""
import csv
import importlib.util
import os
import sys

from PIL import Image

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("phase10_station_sheets",
                                              os.path.join(os.path.dirname(os.path.abspath(__file__)), "station_sheets.py"))
ss = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ss)

VIEWS = {
    "D1": ("Penthouse roof deck", "north penthouse roof deck, under the pergola, looking south-east"),
    "D2": ("Penthouse living space", "north penthouse, 4th floor, street-facing kitchen room, looking toward the windows"),
    "D3": ("Triplex kitchen", "north triplex, 1st floor kitchen, along the counter toward the street window"),
    "D4": ("Triplex bathroom", "north triplex, 2nd floor hall bath (tub, toilet, basin, wall light)"),
    "D5": ("Triplex rear patios", "north triplex, 1st floor covered rear patio, looking out to the rear"),
}
EDGES = {"D2": (569, 4018), "D3": (451, 5905), "D4": (328, 1670)}
NOTES = {
    "D1": "The far city behind the deck is a stand-in (Phase 7), not the real skyline.",
    "D2": "The furniture is labelled stand-in furniture; the owner has not chosen furniture.",
    "D3": "The real-time picture draws the glass shade of the pendant lamp about two stops brighter than the "
          "path-traced picture. The finish alternatives of the kitchen carry working names until the owner names them.",
    "D4": "The room has no window. The real-time picture is 1.2 stops darker over a quarter of the frame: the "
          "real-time method (Lumen) carries less bounced lamp light in a closed room than the Path Tracer. In the "
          "Revit model the bath's walls carry gypsum board and no tile, so tile relief shows only through a tile "
          "alternative.",
    "D5": "The real-time picture is 12 percent darker overall, with no single region off by a stop: less bounced "
          "daylight under the covered patio.",
}
REVIT = ("Revit view from the same camera", "not compared", "could not be checked",
         "a view exported from Revit at this camera (Revit is not opened by these sessions; none was exported).")
TRANSFER = ("Transfer from Revit to Unreal (1 mm known dimension, 5 mm floor levels, 10 mm fixtures)",
            "known dimension 0.1 to 0.3 mm; floor levels 0.4 mm at most; all 2,585 placed objects within 0.5 mm of "
            "their Datasmith place (Phases 3 and 6; same figure at every view)", "pass",
            "a Revit view, to see fixture by fixture that nothing is missing.")
COLOUR = ("Colour of principal materials (colour difference 5)", "not measured", "could not be checked",
          "a photograph or manufacturer's sample of each finish with a grey card; the owner's keep-or-rebuild "
          "decision per material is open.")


def scores(view):
    tier = ss.tiers[view]
    regions = tier["failing_regions"]
    out = [REVIT, TRANSFER]
    if view in EDGES:
        left, before = EDGES[view]
        out.append(("Sharp edges within 2 m of the camera (Phase 6 acceptance: zero)",
                    "%d left of %d; what is left is detail finer than the 2 mm rounding inside fixtures" % (left, before),
                    "fail (reduced by %d percent)" % round(100 - 100.0 * left / before),
                    ""))
    out.append(("Real-time against path-traced (mean 10 percent; no region over 2 percent of frame off by a stop)",
                "mean brightness %+.1f percent; largest region off by over one stop %.2f percent of the frame%s"
                % (float(tier["mean_difference_percent"]), float(tier["largest_region_percent"]),
                   (" (" + regions + ")") if regions else ""),
                "pass" if tier["passes"] == "True" else "fail", ""))
    out.append(COLOUR)
    out.append(("Note", NOTES[view], "for the owner", ""))
    return out


def sheet(view):
    name, where = VIEWS[view]
    rows = scores(view)
    title = "1529 N. Wieland, Phase 10, design view %s %s: %s" % (view, name, where)
    picture, draw = ss.new_sheet(title, 2, ss.foot_lines(rows))
    truth = Image.open(ss.TRUTH % view).convert("RGB").resize(ss.PANEL, Image.LANCZOS)
    real = Image.open(ss.REAL % view).convert("RGB").resize(ss.PANEL, Image.LANCZOS)
    ss.placeholder(draw, ss.box(0, 0), ["PLACEHOLDER: no Revit view.",
                                        "No view was exported from Revit at this camera, and these sessions",
                                        "do not open the Revit model. So the check that every fixture of the",
                                        "Revit view is present in the render was not made by picture;",
                                        "the object counts and positions of Phase 6 stand in its place."])
    picture.paste(truth, ss.box(0, 1)[:2])
    ss.label(draw, ss.box(0, 1), "Path-traced picture (Phase 12)")
    picture.paste(real, ss.box(1, 0)[:2])
    ss.label(draw, ss.box(1, 0), "Real-time picture (today, after a fresh start of the editor)")
    picture.paste(ss.difference(truth, real), ss.box(1, 1)[:2])
    ss.label(draw, ss.box(1, 1), "Difference: red = real-time brighter, blue = darker, full colour at two stops")
    return picture


def main(argv):
    wanted = argv[1:] or list(VIEWS)
    os.makedirs(ss.OUT, exist_ok=True)
    for view in wanted:
        target = os.path.join(ss.OUT, view + "_sheet.jpg")
        picture = sheet(view)
        picture.save(target, quality=88)
        print(target, picture.size)
    with open("review/phase10/design_scores.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["view", "sheet", "check_and_limit", "measured", "verdict", "missing_evidence"])
        for view in VIEWS:
            for check, measured, verdict, missing in scores(view):
                writer.writerow([view, "review/phase10/sheets/%s_sheet.jpg" % view, check, measured, verdict, missing])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
