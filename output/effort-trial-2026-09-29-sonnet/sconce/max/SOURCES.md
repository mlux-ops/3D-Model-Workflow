# Sources

What I took from each input, what I rejected and why. All inputs are in `../inputs/` and were only read. Nothing came from the web.

## Inputs

| Input | Used for | Rejected or not used |
|---|---|---|
| `833918_lightology_spec_sheet.pdf` | **Published facts.** Text extracted with `pdftotext`: 8" W x 7.63" H x 5.5" D; backplate "Round, 5.25" Dia x 0.125"D"; shade "3.5" Dia x 3.25"H"; materials glass and steel; 1 x JCD/G9/3W/120V LED, bulb not included; total 3 W; standard 120 V dimmer; damp location; Milk / Midnight Black; product weight 1.80 lb; "Can be used with or without the disc". The embedded images were extracted with pypdf (Poppler's `pdftoppm` and `pdfinfo` are not installed, `ERRORS.md` item 1). | The six embedded images are a logo, two ETL marks, the DAMP mark, a QR code and one 650 x 650 product picture in the brass finish. The product picture was looked at only as a same-geometry cross-check; nothing was measured from it. Weight is not modelled. |
| `KW1041_install_instructions_20230426.pdf` | **Assembly and part list.** The exploded drawing is vector graphics, rendered with the Windows PDF renderer (`_work/render_pdf.ps1`, `_work/pdf/inst-p1.png`, `inst-p2.png`). It gives the order: mounting plate on the junction box, body, socket, a plate that screws onto the socket (the disc), lamp, shade that screws onto the socket. That fixed the five parts, the shade as a separate piece on the socket, the disc hole matching the socket, and the disc being optional. | No dimensions were taken from it. |
| `833919_midnight_black.jpg` (1779 x 1779) | **Hero photo, disc on.** Ellipse fit to the disc outline (view direction and tilt cross-check), rim band width on the upper-left arc (disc thickness about 0.03 in, `_work/disc_rim_measure.json`), globe size, and the angled comparison (`_REVIEW_compare.jpg` row 3, `_work/overlays/overlay_angled.png`). | Absolute sizes read from this photo, because it has strong perspective; only ratios (globe to disc 0.46) were used. The globe's offset from the disc centre in this photo (0.20 disc heights against 0.165 modelled) is unresolved and did not change the geometry. |
| `833919_additional.jpg` (1137 x 1137) | **Qualitative check only.** A small lifestyle photo with the disc nearly edge-on and the glowing globe in front of it and low on the disc. I viewed an enlarged crop (190, 300, 300, 410). | Not measured: the disc and globe are a few dozen pixels across, the camera is unknown and the perspective is strong. |
| `833918_burnished_brass.jpg` (1779 x 1779) | Viewed once as a thumbnail to confirm the brass version has the same geometry as the Midnight Black photo. | Nothing measured. The finish is out of scope. |
| `KW1041_MWT_side_reference.jpg` (2400 x 2400) | **Main measurement source.** Matte white, no disc, side view. Registered on the plate height (5.25 in = 241.7 px/in). Gave body diameter (4.26 to 4.31 in), the cut-face position and edge angles (15.6 and 19.0 degrees), the globe circle (diameter 3.47 in, centre 0.445 in below the plate centre, 1.72 in along the axis from the cut face), and the plate thickness and depth comparison. `_work/side_metrics.py`, `side_metrics.json`, `overlays/overlay_side.png`. | Its plate thickness (0.257 in) and depth from the back face (5.63 in): they disagree with the published 0.125 in and 5.50 in. Published values govern. The 0.124 in excess is the plate thickness; registered on the plate front the depths agree. I cannot tell whether the photographed plate includes a gasket or the reference is a different revision. |
| `KW1041_MWT_oblique_reference.jpg` (2400 x 2400) | Front and oblique comparison of the body, cut face and globe without the disc (`_work/overlays/overlay_front.png`, the front and side rows of `_REVIEW_compare.jpg`); the photo's roughly 4 to 5 degree pitch. | Not used for the disc (there is none) or for absolute sizes. |
| `lightology_833919_midnight_black.html` | Data only. Text extracted with an HTML parser as a cross-check of the published facts. Every value matched the spec sheet. It held no instruction-like content. | Not a source of geometry. |
| `lightology_833918_burnished_brass.html`, `lightology_brass_page_view.png`, `lightology_midnight_black_page_view.png` | Not opened. The brass finish is out of scope, and the page-view images duplicate the page text. | |

## Other material read

- `output/house_of_troy_usledz15_76/source/build_house_of_troy_usledz15.py`: an allowed precedent, read for pyRevit family-build patterns (transactions, parameter association, failure handling).
- `_harness/revit_run.py` and `_harness/revit_runs.log`: read-only, for the runner's mechanics and the queue wait times in `ERRORS.md`.
- Autodesk's local `RevitAPI.xml` documentation and the member names in `RevitAPI.dll`, for API discovery. Each API behaviour used was then confirmed by running it.
- The project instructions (`AGENTS.md`, the global `CLAUDE.md`) and the memory index, which load with the session.
- The Revit family template `Generic Model face based.rft` and the project template `Default-Multi-discipline.rte` from the local Revit 2025 install.

## Not consulted

Earlier builds of this fixture, `output/lightology_20260923/`, `PROJECT_MEMORY.md`, claude-mem memories, `WORKFLOW.md`, the `gola_setback` precedent files, and the `../high/` and `../xhigh/` run folders. No sub-agent or MCP tool was used.
