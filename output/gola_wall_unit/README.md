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

## Placing (two clicks) — on the cabinet underside

Your cabinets are solid boxes; the door isn't a separate panel. So the family cuts its own recess into the box.

**Rebuilt 2026-10-02 for underside placement.** The 2026-09-28 version expected the cabinet's front face. Placed on the underside, its profile and void came out turned 90°, lying inside the cabinet.

1. Start placing the family and choose **Place on Face**.
2. Pick the **underside** of the upper cabinet.
3. Click the start and end of the **front edge** of the underside, **left to right as you face the cabinet**.

The result:
- the profile sits inside the box at its front bottom corner. The curl is on the underside, and the web is 20 mm up, where the door's bottom edge would be. The tongue rises into the box above it;
- the profile's front face sits **3/4" behind the cabinet front** (**Wall Setback**, the same set-back as the base-cabinet Gola channels);
- the recess void cuts a band 20 mm high above the underside, plus a 1 mm overlap below it. It runs from the cabinet front back to **Cut Depth** behind the set-back profile, so the recess is always open to the front.

If you draw right to left, the profile lands in front of the cabinet instead of inside it. Tick **Flip Profile**, and the cut moves with it.

**Already placed with the old version?** Load this file and choose **Overwrite the existing version**. Channels already on a cabinet underside then correct themselves in place. Tick Flip Profile on any that land in front of the cabinet.

| Instance parameter | Default | Effect |
|---|---|---|
| Wall Setback | 19.05 mm (3/4") | distance from the cabinet front (the clicked edge) to the profile's front face. 0 puts it flush. |
| Cut Depth | 20 mm | how far the recess goes behind the profile's front face. 20 mm clears the profile and its finger space. Set it to the cabinet depth to open the whole band, as a real door overhanging the carcass does. |
| Flip Profile | off | mirrors the profile and its cut to the other side of the clicked edge |
| Plane Faces Up | off | set by the add-in for channels moved off in-place cabinets; tick it only when placing on a level by hand |
| Placement Offset, Recess Start / End, Recess Up Start / End, Show Profile ... | formulas | internal; don't edit |

**The cut is applied by the GolaAutoCut pyRevit extension**, the same add-in as the base-cabinet channels. It has been extended from walls to **Casework, Generic Models, Furniture, Furniture Systems and Specialty Equipment**.
- It cuts automatically when you place, stretch, move, flip or change the depth.
- The **Cut Gola Recesses** button is the backup.
- The updated add-in is installed at `E:\pyRevit Extensions\GolaAutoCut.extension`. Click **pyRevit → Reload** once in open sessions.

In the test, a Casework cabinet family with "Cut with Voids When Loaded" **off** was still cut, so your cabinet families shouldn't need that setting changed. If Revit refuses to cut an element anyway, it's listed in `%TEMP%\gola_autocut.log` and in the button's output.

### In-place cabinets and "a circular chain of references" (2026-10-02)

**Cause (found on the Belmont model):** *Countertop80* is an **in-place family**, a Model In-Place of category Casework. Revit can't cut an in-place element with a channel that sits on a face of that same element. The cut changes the face the channel hangs on, and Revit reports "a circular chain of references", listing the in-place type, the instance, its extrusion and the channel.

A channel that isn't attached to the element cuts it without error. This was tested on Countertop80 itself, in a transaction that was undone afterwards.

**What the add-in does now:** when a channel sits on an in-place element it has to cut, the add-in replaces it with an identical copy on the level below, before cutting:
- the copy has the same line, profile, setback, Cut Depth and comments;
- its Flip Profile and **Plane Faces Up** are set so that it doesn't move;
- the copy is checked against the original, and if it isn't identical within 0.05 mm the channel is left as it was.

You keep using **Place on Face** on the underside. The channel gets a new element id, and it no longer moves with the cabinet. Loadable cabinet families keep the channel hosted, because they cut fine that way.

**Plane Faces Up** (instance, off): mirrors the profile and cut for a work plane facing up, such as a level, so the profile rises above the plane. The add-in sets it; you only need it to place a channel on a level by hand. In that case, set Offset from Host to the cabinet underside and tick it.

The add-in also:
- tries each cut separately, so one refused cut no longer blocks the others;
- keeps a cut only if it actually removes material, so walls, vanities or fixtures that merely touch the channel are left alone;
- shows a short message naming any element Revit refused, with Revit's reason. The **Cut Gola Recesses** button lists refused cuts and replacements.

**Profile Material** (type) is *Gola - Brushed Stainless Finish*, the same finish as the other Gola channels.

## Verification

Revit 2025, headless. `validation.json` holds the results, re-derived by `verify_wall_unit.py`; all 43 gates pass (underside rebuild with Plane Faces Up, 2026-10-02).

- **Placement**, Place on Face on the underside of a solid 2000 × 400 × 700 mm Casework box, along its front edge:
  - two clicks give a location line exactly from click to click, on the front edge, hosted by the cabinet;
  - the run follows the clicks and an end-grip drag to 2400 mm;
  - volume equals the drawn section area × length;
  - drawn left to right, the profile's front face is 19.05 mm behind the cabinet front and its back 39.05 mm. It rises 0 to 26.9 mm above the underside;
  - Wall Setback 0 and 1" move it to exactly 0 and 25.4 mm;
  - drawn right to left, it lands in front of the cabinet, and Flip Profile puts it back inside.
- **Cutting**, a 1500 mm run hosted on the box's underside:

  | Setting | Box material removed |
  |---|---|
  | Cut Depth 20 | 1,171,500 mm³ (20 mm high × 39.05 mm deep, exact) |
  | Cut Depth 300 | 9,571,500 mm³ (exact) |
  | Flipped | 90,000 mm³, only the 3 mm lead-in left in the box, so the cut follows the profile |
  | Back to Cut Depth 20, unflipped | 1,171,500 mm³ |
  | Casework box with "Cut with Voids When Loaded" off | 1,171,500 mm³, cut as well |

- **The channel stays hosted on the cabinet it cuts.** Revit reported no circular chain or other failure.
- **The void never cuts the profile itself.**
- **Plane Faces Up**: on a level the profile rises 0 to 26.9 mm above the plane, and mirrors with Flip Profile.
- **Move off the face** (forced on a plain box, because the API can't create in-place families), for both click directions:
  - the channel is replaced by an unhosted copy on the level, identical to within 0.000000000004 mm;
  - Cut Depth 30 and the comments carry over;
  - the following cut is exact: 1,471,500 mm³.
- **Real in-place Countertop80**, Belmont model, in a transaction undone afterwards: an unhosted channel cuts it with no failures; the countertop volume is unchanged afterwards.
- **`test_circular.py` checks** (`validation_circular.json`, underside placement):
  - a cut into the cabinet the channel sits on commits;
  - runs past the cabinet end cut the neighbouring cabinet exactly;
  - the automatic updater path cuts exactly 1,171,500 mm³;
  - a box that only touches the channel isn't cut.

The profile view is in `preview/`.
