# Phase 4 results: surroundings

Companion to [PLAN.md](PLAN.md). Written as each step finishes, so a new session can resume from it. Earlier records: `phase1_results.md`, `phase2_results.md`, `phase3_results.md`.

**Status at 17:50 Central on 2026-11-11: begun.** The owner wrote "continue, do not stop unless absolutely neccessary" after Phase 3 was reported complete.

**What this phase can and cannot be without the site visit.** The plan builds Zone 1 (everything a station sees within 40 m) from the owner's photographs and measurements. There are none: the site visit of Phase 2 was not made. So this phase builds what the evidence in hand supports, which the plan's own risk list foresees: every neighbouring building as its own object with its 2022 footprint, height and roof form, and the ground with its kerbs, all from the 2022 laser scan and the county's footprints. Facade detail, street furniture and the side-by-side sheets against photographs stay as gaps.

## How to resume, if this chat ends

Read the journal below. A line that still reads PENDING marks the step that was running. Every call in `tools\wieland_surroundings.py` skips what already exists, so a batch can be run again.

## Journal

| No. | Time | What is done | Outcome |
|---|---|---|---|
| K1 | 17:50 on 2026-11-11 | Steps 4.1, 4.2 and 4.5. The meshes were generated outside the editor at 17:45 by `tools\build_surroundings.py` from the files in `E:\Wieland1529_site_data\`: 144 buildings (23 within 40 m of the lot, 121 further off; 90,041 triangles) and 36 ground tiles (564,783 triangles; the nine around the lot at 1 ft cells, the rest at 4 ft; the lot cut out). Left out: the two houses that stood on the lot in 2022, and 24 footprints cut by the edge of the 300 m data square. Now: make a new level `/Game/Wieland1529/Surroundings/L_Surroundings`, turn each mesh file into a Nanite static mesh under `/Game/Wieland1529/Surroundings/Meshes` and an object in the level, in batches, with a plain grey material; then save the level and the 180 new assets by name. Free commit 29.4 GB at 17:36, editor at 23.0 GB. | PHASE4_K1_PENDING |
