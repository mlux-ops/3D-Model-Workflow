"""Phase 10, step 10.8, the part that does not need the owner: the list of failures, each with its cause and a
proposed fix, and an empty column for the owner's mark ("fix" or "accept").

    python -B review/phase10/scripts/owner_marks.py

Run from the plan folder. Writes review/phase10/owner_marks.csv. If the file already holds marks, they are
kept: a row whose "id" exists keeps its "owner_mark" and "owner_note".
"""
import csv
import os

PATH = "review/phase10/owner_marks.csv"
FIELDS = ["id", "where", "what_fails", "measured", "limit", "cause", "proposed_fix", "phase_that_owns_the_fix",
          "sheet_or_file", "owner_mark", "owner_note"]
ROWS = [
    ("F1", "All street stations; S8",
     "Neighbours' heights",
     "Within 40 m of the lot 3 of 19 buildings are within 0.3 m of the 2022 laser scan; middle value 1.02 m too low, "
     "largest 2.83 m. Number 1533 is 1.10 m too high, number 1525 1.02 m too low, the rear building 1.30 m too low. "
     "Over all 50 measured buildings 37 are off by more than 1 m, the largest by 12.07 m (SB_780909).",
     "0.3 m",
     "Phase 7 kept the earlier detailed models of the neighbours as they were modelled and fitted them to the "
     "ground only. The plain blocks of Phase 4, which have the laser scan's heights, are the hidden option.",
     "For each building off by more than 0.3 m: stretch the earlier model in height to the laser scan's roof level "
     "where the difference is under about 1 m; where it is larger, show the Phase 4 block with its Phase 7 material "
     "instead. Numbers 1533 and 1525 first, after a laser reading on site if the owner makes the visit.",
     "Phase 7", "review/phase10/neighbours_now.csv"),
    ("F2", "All street stations; S8",
     "Neighbours' walls in plan, away from the surveyed points",
     "Within 40 m of the lot 26 of 76 building sides stand more than 0.5 m from the county's 2022 outline (17 more "
     "than 1.0 m, largest 3.0 m). At the five points the plat of survey ties to neighbours' walls the walls are "
     "within 0 to 30 cm: those pass.",
     "0.3 m (0.5 m from the laser scan alone)",
     "Same as F1: the earlier models were not built to the county outlines. The county outline is itself a roof "
     "outline read from the air, good to about 0.5 m, and includes eaves and porches.",
     "Look at the worst sides in the S8 sheet (cyan outline against the drawn building); move or replace only the "
     "buildings that are seen from a station. Accept the rest.",
     "Phase 7", "review/phase10/sheets/S8_sheet.jpg; review/phase10/neighbours_now.csv"),
    ("F3", "All street stations",
     "Roadway level",
     "The roadway lies 13.1 cm below the 2022 laser ground (middle value; 10.5 percent of it within 0.1 m). "
     "Pavements and yards are within 0.1 m (99.5 percent).",
     "0.1 m relative to the lot (0.2 m absolute is met)",
     "Phase 7 made the kerb by lowering the whole roadway 13 cm under the laser ground (an assumed kerb height), "
     "although the laser ground already is the real roadway.",
     "Raise the roadway pieces to the laser ground and give the kerb the height the laser scan shows between "
     "sidewalk and gutter (or the height taped on site).",
     "Phase 7", "review/phase10/ground_now.json"),
    ("F4", "S9",
     "Real-time picture against path-traced picture",
     "Mean brightness +26.2 percent; two regions of 2.1 and 2.0 percent of the frame about four stops brighter: the "
     "upper windows of the buildings across the street.",
     "mean 10 percent; no region over 2 percent of the frame off by more than one stop",
     "The real-time picture shows the bright sky mirrored in the neighbours' window glass; the path-traced picture "
     "shows the same glass dark. Which is right is not known without a photograph.",
     "Find out why the Path Tracer draws no sky reflection in that glass (the glass material of the earlier model, "
     "or what stands behind it), correct the one that is wrong, and repeat S9 in both tiers.",
     "Phase 8 (lighting and ground truth)", "review/phase10/sheets/S9_sheet.jpg"),
    ("F5", "D3",
     "Real-time picture against path-traced picture",
     "Mean brightness +18.0 percent (+19.5 on repeat); one region of 3.3 percent of the frame two stops brighter: "
     "the glass shade of the pendant lamp.",
     "mean 10 percent; no region over 2 percent of the frame off by more than one stop",
     "The lamp's glass shade is drawn glowing in the real-time picture and clear in the path-traced one; the "
     "bounced light of the lamps is also higher in real time.",
     "Give the shade a material that both renderers draw alike (thin translucent glass without its own glow), then "
     "repeat D3 in both tiers.",
     "Phase 8 (interior lamps); Phase 5 (material)", "review/phase10/sheets/D3_sheet.jpg"),
    ("F6", "D4",
     "Real-time picture against path-traced picture",
     "Mean brightness -42.4 percent (-42.3 on repeat); a quarter of the frame 1.2 stops darker.",
     "mean 10 percent; no region over 2 percent of the frame off by more than one stop",
     "The bath has no window. The real-time method (Lumen) carries less bounced lamp light in a small closed room "
     "than the Path Tracer.",
     "Trial, one change at a time: higher Lumen final-gather quality in this room's post-process volume; if that "
     "does not close it, a weak fill lamp for the real-time tier only, recorded as such. Or accept: the walk-through "
     "shows the bath darker than the stills.",
     "Phase 9 (real-time settings)", "review/phase10/sheets/D4_sheet.jpg"),
    ("F7", "D5",
     "Real-time picture against path-traced picture",
     "Mean brightness -11.9 percent (-11.6 on repeat); no region off by a stop.",
     "mean 10 percent",
     "Less bounced daylight under the covered patio in the real-time picture.",
     "Same trial as F6 for the patio; or accept (1.9 percent over the limit, nothing visible as a region).",
     "Phase 9 (real-time settings)", "review/phase10/sheets/D5_sheet.jpg"),
    ("F8", "D2, D3, D4",
     "Sharp, unrounded edges within 2 m of the camera (Phase 6's own acceptance line)",
     "D2 569, D3 451, D4 328 edges left (from 4,018, 5,905 and 1,670).",
     "zero",
     "What is left is detail finer than the 2 mm rounding inside fixtures (sink, sconces, pendant, faucet, "
     "pocket-door hardware).",
     "Replace those fixtures with remodelled ones, or accept.",
     "Phase 6", "phase6_results.md"),
    ("F9", "S8",
     "Real-time plan picture against path-traced plan picture",
     "Mean brightness +38.5 percent; two regions of 11.4 and 9.1 percent of the frame 2.5 and 1.9 stops brighter in "
     "the real-time picture (roofs and ground in shadow). The path-traced picture was made with Nanite ray tracing "
     "off (mode 0), so it traced the meshes' simplified fallback copies.",
     "mean 10 percent; no region over 2 percent of the frame off by more than one stop",
     "Seen in the two pictures, not proven by a trial: the camera stands 2 km above the lot. At that distance the "
     "real-time renderer draws its far, simplified shadows (soft blots that do not follow the roofs' edges) and "
     "lights the shadowed sides more; the Path Tracer draws every shadow sharp and deep at any distance. The "
     "walk-through never shows the scene from this distance.",
     "Accept, and use the path-traced picture as the plan picture of S8: it is the truer of the two for a plan. "
     "Its trees are drawn as coarse triangles (fallback copies); a plan picture with full-detail trees needs "
     "Nanite ray tracing mode 2, which is switched off because it hangs the graphics card in Unreal 5.9.",
     "Phase 8 (lighting and ground truth)", "review/phase10/sheets/S8_sheet.jpg"),
]


def main():
    kept = {}
    if os.path.exists(PATH):
        with open(PATH, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                kept[row["id"]] = (row.get("owner_mark", ""), row.get("owner_note", ""))
    with open(PATH, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        for row in ROWS:
            mark, note = kept.get(row[0], ("", ""))
            writer.writerow(list(row) + [mark, note])
    print(len(ROWS), "failures written;", sum(1 for m, _ in kept.values() if m), "marks kept")


if __name__ == "__main__":
    main()
