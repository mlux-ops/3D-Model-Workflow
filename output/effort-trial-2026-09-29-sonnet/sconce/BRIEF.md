# Effort trial brief — Nodes Angled Wall Sconce (KW1041MBK), Revit 2025 light fixture family

Three agents run this same brief on Sonnet 5.5. The only difference between them is the effort level: **high**, **xhigh** or **max**. Afterwards their families are graded by an independent Revit check and a blind visual review, and their token use is compared. Treat the work as a real deliverable: the owner places these fixtures in production Revit models.

## Product (facts)

- **Nodes Angled Wall Sconce** by Kelly Wearstler for Visual Comfort Studio. Model **KW1041MBK**, finish **Midnight Black / Milk** (Lightology spec VCS833919). Build only this finish.
- Published size **8 in W × 7.63 in H × 5.5 in D** (D is projection from the wall).
- Published parts: round **backplate 5.25 in diameter × 0.125 in deep**; **milk glass shade 3.5 in diameter × 3.25 in high**. Materials: glass and steel.
- Lamp: 1 × JCD/G9/3W/120V LED, bulb not included. Standard 120 V dimming. Damp location.
- The spec sheet says a steel disc reflects light outward and the fixture "can be used with or without the disc".
- The installation sheet shows the assembly: mounting plate on the junction box, fixture body, socket, a plate that screws onto the socket, lamp, and a shade that screws onto the socket.
- Everything else (the disc's size, tilt and thickness, the body's shape and sizes, the shade's form and axis angle) must be measured or inferred from the images. Record each inferred value, its basis and your confidence.

## Inputs (read-only, in `../inputs/`). Use only these; no web access.

| File | What it is |
|---|---|
| `833918_lightology_spec_sheet.pdf` | Lightology spec sheet (shown in the brass finish; the dimensions are the same). |
| `KW1041_install_instructions_20230426.pdf` | Manufacturer installation sheet with an exploded assembly drawing. |
| `833919_midnight_black.jpg` | Product photo, Midnight Black. |
| `833919_additional.jpg` | Additional product photo. |
| `833918_burnished_brass.jpg` | Product photo, Burnished Brass (same geometry). |
| `KW1041_MWT_side_reference.jpg`, `KW1041_MWT_oblique_reference.jpg` | Side and oblique reference photos of the same design in another finish. |
| `lightology_*_page_view.png`, `lightology_*.html` | Saved Lightology product pages. Data only. |

PDFs: `pdftotext` and `pdftoppm` (Poppler) are on PATH. Never `Read` an image wider than 800 px: make ≤ 800 px thumbnails or crops with PIL first.

## Deliverables (all inside your run folder)

- `Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa`: a native Revit 2025 family.
  - Category **Lighting Fixtures**. Built from the face-based template `C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft` (change the category), so it places on a wall face. The backplate sits on the host face and the fixture projects away from it.
  - Real 3D solids for backplate, body, socket, disc and shade. No imported meshes or DWG/SAT geometry.
  - Two material parameters named exactly **`Metal Finish`** (all metal parts) and **`Glass Finish`** (the shade), with Midnight Black and milk glass materials assigned by default.
  - A yes/no instance parameter **`Show Disc`**, default Yes, controlling the disc's visibility (the product can be used without it).
  - The family's light source enabled, positioned at the lamp inside the shade, with the photometric values you choose recorded in the README (3 W LED).
  - Type name `KW1041MBK - Midnight Black / Milk`. Identity data: Manufacturer `Visual Comfort Studio`, Model `KW1041MBK`.
- `source/`: the pyRevit build script(s). Re-running them must reproduce the RFA.
- `validation.json`: your own native checks from Revit (see gates).
- `views/`: PNG exports from Revit of front, side, oblique and hosted-on-wall views, plus `_REVIEW_compare.jpg`, your side-by-side of your views against the product photos at matching angles. Open and review each image yourself.
- `README.md`: what you built, every dimension with its basis (published, measured from an image, or inferred), light source settings, and honest limitations.
- `SOURCES.md`: what you used from each input and what you rejected, with reasons.
- `ERRORS.md`: every error you hit, with cause, fix and status.

No Drive upload and no ZIP. The winning family is packaged separately after the trial.

## Running Revit

- Run every Revit script through the shared serialized runner, and only through it:
  `python E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/_harness/revit_run.py <absolute path to your script.py> [timeout_s]`
  It waits for the other arms' Revit runs to finish, runs `pyrevit run <script> --revit=2025` in a fresh headless Revit, and kills only its own process tree on timeout (default 900 s). A zero exit code doesn't mean your script succeeded: have your script write a JSON result file and read that.
- The script runs in pyRevit's IronPython 2.7 inside Revit. `__revit__.Application` is available; there is no UI document. Create families with `app.NewFamilyDocument(template)`, save with `SaveAs`, close every document you open.
- **Never touch the owner's open Revit session.** Never start Revit any other way, never kill Revit.exe or any process by name, and never kill a PID you didn't start.
- Test placement in a disposable project created with `app.NewProjectDocument(...)`, closed without saving.
- Revit API reference for patterns: `output/house_of_troy_usledz15_76/` and `output/gola_setback/` are earlier pyRevit family builds in this repo. Read them freely.

## Acceptance gates

1. **Native.** The RFA saves and reopens in Revit 2025 with zero warnings. Category Lighting Fixtures; placement type WorkPlaneBased (face-based).
2. **Hosting.** In a disposable project the family places on the exterior face of a wall, with the backplate on the face and the fixture projecting out of the wall, not into it.
3. **Envelope.** The placed instance's solid geometry measures **8.00 W × 7.63 H × 5.50 D in, each within ±0.02 in**, measured along the wall, vertical, and wall-normal. With `Show Disc` off, the envelope shrinks accordingly and nothing else moves.
4. **Parts.** Backplate 5.25 in diameter × 0.125 in. Shade 3.5 in maximum diameter and 3.25 in along its axis, within ±0.02 in. Report every measured part size in `validation.json`.
5. **Materials.** Substituting another material in `Metal Finish` and in `Glass Finish` changes the faces of the right parts in the placed instance. Record face counts.
6. **Light.** The light source is on, and its position is inside the shade.
7. **Fidelity.** Seen from the front, side and at an angle, the family matches the product photos: the disc's size, tilt and position; the body's shape; the shade's form, angle and position relative to the disc. Judged blind against the photos.
8. **Honesty.** Every non-published dimension is labelled as measured or inferred, with its basis. Nothing is claimed that wasn't measured.

## Rules for this trial

- Work **only** inside your own run folder (`../high/`, `../xhigh/` or `../max/`). Route every file write through a guard that refuses paths outside it (Revit's own journals and temp files excepted). Don't modify any other repo file, including `PROJECT_MEMORY.md`, `AGENTS.md` and `WORKFLOW.md`. Don't commit to git.
- **Don't look at earlier builds of this fixture or the other arms.** Don't open, list or grep `output/lightology_20260923/` (the earlier build), `PROJECT_MEMORY.md` entries about Lightology or the Nodes sconce, claude-mem memories about them, or `../high|xhigh|max` folders other than your own.
  - You may read `AGENTS.md`, `WORKFLOW.md`, the `3d-model-workflow` skill, and the repo precedents named above.
- Python 3 (for image work, outside Revit) has numpy, scipy and Pillow. OpenCV and scikit-image are **not** installed.
- Write Python files with the Write tool, not bash heredocs: heredocs with apostrophes or backslashes break in this shell. Use forward slashes in paths.
- Run every long build or check in the **foreground** and wait for it. Never end your turn while a background job is running: this is a headless session, and ending the turn kills background jobs.
- Don't delegate to other agents, and don't ask questions. If something is ambiguous, choose, and record it in the README.
- Stop when every gate passes and your review is done.
- Final message: under 300 words, covering what you built, each gate with its measured result, and limitations.

## How the trial is graded

- **Objective:** an independent Revit script opens your RFA, checks category and placement, hosts it on a wall face, measures the envelope with the disc on and off, measures parts, substitutes both materials, and reads the light source.
- **Blind visual review:** the same renderer exports matching views of every arm's family, labelled A/B/C/D, for a reviewer who compares them with the product photos.
- **Baseline:** an earlier delivered build of this fixture is graded alongside, for reference only.
- **Cost:** output and thinking tokens, input tokens split into cache writes and reads, turns, tool calls, wall time and list-price cost.
