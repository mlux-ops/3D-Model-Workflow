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
- the profile's front face sits **3/4" behind the clicked face** (**Wall Setback**, the same set-back as the base-cabinet Gola channels);
- the recess void cuts a band 20 mm high (plus a 1 mm overlap below the line). It runs from the face back to **Cut Depth** behind the set-back profile, so the recess is always open to the face.

If you draw right to left, the profile ends up below the box. Tick **Flip Profile**, and the cut moves with it.

| Instance parameter | Default | Effect |
|---|---|---|
| Wall Setback | 19.05 mm (3/4") | distance from the clicked face to the profile's front face. 0 puts it flush. |
| Cut Depth | 20 mm | how far the recess goes behind the profile's front face. 20 mm clears the profile and its finger space. Set it to the cabinet depth to open the whole band underneath, as a real door overhanging the carcass does. |
| Flip Profile | off | mirrors the profile and its cut above or below the line |
| Placement Offset, Recess Front, Recess Start Above / Below | formulas | internal; don't edit |

**The cut is applied by the GolaAutoCut pyRevit extension**, the same add-in as the base-cabinet channels. It has been extended from walls to **Casework, Generic Models, Furniture, Furniture Systems and Specialty Equipment**.
- It cuts automatically when you place, stretch, move, flip or change the depth.
- The **Cut Gola Recesses** button is the backup.
- The updated add-in is installed at `E:\pyRevit Extensions\GolaAutoCut.extension`. Click **pyRevit → Reload** once in open sessions.

In the test, a Casework cabinet family with "Cut with Voids When Loaded" **off** was still cut, so your cabinet families shouldn't need that setting changed. If Revit refuses to cut an element anyway, it's listed in `%TEMP%\gola_autocut.log` and in the button's output.

### If Revit reports "a circular chain of references" (2026-09-29)

This happens when a channel sits on a face of the element it cuts, and that element's own geometry makes the cut feed back into the face the channel hangs on. It was seen on *Countertop81* in the Belmont model. A plain box cabinet cut this way works (tested). The add-in now:

- tries each cut separately, so one refused cut no longer blocks the others;
- keeps a cut only if it actually removes material, so walls, vanities or fixtures that merely touch the channel are no longer cut;
- shows a short message naming any element Revit refused, with Revit's reason (the button lists them too).

**Workaround for an element that refuses:**
1. Draw a **Reference Plane** on the cabinet face.
2. Place the channel with **Place on Work Plane → Pick a plane**, picking that reference plane.

The channel then doesn't depend on the cabinet, and the cut goes through.

**Profile Material** (type) is *Gola - Brushed Stainless Finish*, the same finish as the other Gola channels.

## Verification

Revit 2025, headless. `validation.json` holds the results, re-derived by `verify_wall_unit.py`; all 28 gates pass (rebuilt with the 3/4" setback, 2026-09-28).

- **Placement:**
  - two clicks give a location line exactly from click to click;
  - the run follows the clicks and an end-grip drag to 2400 mm;
  - volume equals the drawn section area × length;
  - on a face, drawn left to right, it spans 0 to 26.9 mm up from the line;
  - its front face is 19.05 mm behind the clicked face and its back 39.05 mm, on a level and on a real face;
  - Wall Setback 0 and 1" move it to exactly 0 and 25.4 mm;
  - Flip Profile behaves as described.
- **Cutting**, a 1500 mm run on a solid 2000 × 400 × 700 mm Casework box:

  | Setting | Wall/box material removed |
  |---|---|
  | Cut Depth 20 | 1,171,500 mm³ (20 mm high × 39.05 mm deep, exact) |
  | Cut Depth 300 | 9,571,500 mm³ (exact) |
  | Flipped | 478,575 mm³, only the 1 mm overlap left in the box, so the cut follows the profile |
  | Casework box with "Cut with Voids When Loaded" off | 1,171,500 mm³, cut as well |
  | Wall face | 1,230,075 mm³ (21 × 39.05 mm, exact) |

- **The void never cuts the profile itself.**
- **Regression:** the four base-cabinet Gola channels' auto-cut tests pass again with the extended add-in.

The profile view is in `preview/`.
