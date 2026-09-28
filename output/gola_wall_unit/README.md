# Richelieu Gola Wall Unit Profile — upper cabinet door pull, cuts solid cabinets (Revit 2025)

`Richelieu_Gola_Wall_Unit_Upper_Cabinet_2025.rfa`: a line-based Generic Model with one type, *Wall Unit - Upper Cabinet Door Pull*.

## Product (researched 2026-09-28)

| | |
|---|---|
| Product | Gola Wall Unit Profile, Richelieu model 1182685, manufacturer ART. 268. Application: upper cabinets. |
| SKU modelled | **70026804170**, stainless look (anodized). Also sold: 7002680410 aluminium satin; 70026804900 black matte (powder coat). |
| Section | 20 × 20 mm; 6.5 mm curled grip lip |
| Length | 4000 mm (a 2400 mm length, 7002680240, is also in the Gola catalogue) |
| LED version | 7002700400, 20 × 20 mm, 4100 mm (not modelled) |
| Door machining | groove 3 mm wide × 8 mm deep, centred in the bottom edge of an 18 mm door (the tongue presses into it) |

Sources are in `references/gola/`: `wall_unit.html` (product page), `wall_unit_1344403.pdf` (data sheet, section), `wall_unit_1344404.pdf` (how to cut) and their PNG renders.

The overall 20 × 20 mm envelope and the 6.5 mm curl are manufacturer dimensions. The ~1.1 mm walls, the ~7 mm tongue with its ~3 mm barb, the scoop and the teardrop curves were measured from the drawing. They are close approximations; the section is 82.25 mm².

## Placing (two clicks) — on solid cabinet boxes

Your cabinets are solid boxes; the door isn't a separate panel. So the family cuts its own recess into the box.

1. Start placing the family.
2. Use **Place on Face** on the cabinet's front face, or **Place on Work Plane** with that face picked.
3. Click the start and end of the cabinet's **bottom front edge**, **left to right as you face the cabinet**.

The result:
- the profile sits in the bottom 20 mm of the box: the leg foot is on the line, the curl is at the bottom, and the web is 20 mm up, where the door's bottom edge would be;
- the front leg is 1 mm proud of the face, like the real part;
- the recess void cuts the box band the profile occupies, 20 mm high (plus a 1 mm overlap below the line), **Cut Depth** deep.

If you draw right to left, the profile ends up below the box. Tick **Flip Profile**, and the cut moves with it.

| Instance parameter | Default | Effect |
|---|---|---|
| Cut Depth | 20 mm | how far the recess goes behind the face. 20 mm clears the profile and its finger space. Set it to the cabinet depth to open the whole band underneath, as a real door overhanging the carcass does. |
| Door Face Offset | 0 | moves the profile out of (+) or into (−) the clicked face |
| Flip Profile | off | mirrors the profile and its cut above or below the line |
| Placement Offset, Recess Start Above / Below | formulas | internal; don't edit |

**The cut is applied by the GolaAutoCut pyRevit extension**, the same add-in as the base-cabinet channels. It has been extended from walls to **Casework, Generic Models, Furniture, Furniture Systems and Specialty Equipment**.
- It cuts automatically when you place, stretch, move, flip or change the depth.
- The **Cut Gola Recesses** button is the backup.
- The updated add-in is installed at `E:\pyRevit Extensions\GolaAutoCut.extension`. Click **pyRevit → Reload** once in open sessions.

In the test, a Casework cabinet family with "Cut with Voids When Loaded" **off** was still cut, so your cabinet families shouldn't need that setting changed. If Revit refuses to cut an element anyway, it's listed in `%TEMP%\gola_autocut.log` and in the button's output.

**Profile Material** (type) is *Gola - Brushed Stainless Finish*, the same finish as the other Gola channels.

## Verification

Revit 2025, headless. `validation.json` holds the results, re-derived by `verify_wall_unit.py`; all 23 gates pass.

- **Placement:**
  - two clicks give a location line exactly from click to click;
  - the run follows the clicks and an end-grip drag to 2400 mm;
  - volume equals the drawn section area × length;
  - on a face, drawn left to right, it spans 0 to 26.9 mm up from the line and −19 to +1 mm through the face;
  - Flip Profile and Door Face Offset both behave as described.
- **Cutting**, a 1500 mm run on a solid 2000 × 400 × 700 mm Casework box:

  | Setting | Wall/box material removed |
  |---|---|
  | Cut Depth 20 | 600,000 mm³ (20 × 20 mm, exact) |
  | Cut Depth 300 | 9,000,000 mm³ (exact) |
  | Flipped | 450,000 mm³, only the 1 mm overlap left in the box, so the cut follows the profile |
  | Casework box with "Cut with Voids When Loaded" off | 600,000 mm³, cut as well |
  | Wall face | 630,000 mm³ (21 × 20 mm, exact) |

- **The void never cuts the profile itself.**
- **Regression:** the four base-cabinet Gola channels' auto-cut tests pass again with the extended add-in.

The profile view is in `preview/`.
