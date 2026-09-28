# Richelieu Gola profiles — two-click, 3/4" wall setback (Revit 2025)

| Family | Built from |
|---|---|
| `Richelieu_Gola_L_Channel_Horizontal_Setback_2025.rfa` | `Richelieu_Gola_L_Channel_Horizontal_2025.rfa` (your line-based file) |
| `Richelieu_Gola_Vertical_Double_Grip_Setback_2025.rfa` | `Richelieu_Gola_Vertical_Double_Grip_2025.rfa` (your line-based file) |

## Placing

1. Load the family and start placing it.
2. On the ribbon choose **Place on Work Plane**. Use **Set Work Plane → Pick a plane** and click the wall face.
3. Click once for the start and once for the end.

To bind the channel to the wall instead, choose **Place on Face**. It then moves with the wall.

- **Horizontal:** draw the line horizontally.
- **Vertical:** draw the line vertically.
- If the grip faces the wrong way, flip or rotate it with the usual controls, or reverse the click order.

## Setback

- **Wall Setback** (instance parameter, default 19.05 mm = 3/4") is the distance from the clicked plane or face to the channel profile's **front face**. The rest of the profile goes deeper:
  - horizontal back at 3/4" + 27 mm;
  - vertical back at 3/4" + 36.6 mm.
- Change it per instance. 0 puts the front face flush with the face you clicked.
- **Front Face Depth** (type) and **Placement Offset** (instance, formula) drive the origin-defining **Placement Plane**. Don't edit them; change Wall Setback instead.
- Placed on a level or other horizontal work plane, the same rule holds: the front face ends up 3/4" below that plane.

## What changed from your files

- **Added:** Wall Setback, Front Face Depth and Placement Offset.
- **Horizontal:** your Placement Plane is now dimensioned and moved from 48.05 mm to 46.05 mm, which puts the front face at 3/4". Before, it was 21.05 mm behind the face.
- **Vertical:** a new "Placement Plane" was added and now defines the origin. The template's unnamed plane no longer does; it is constrained to the level and couldn't move.
- **Unchanged:** all geometry, formulas, sketch constraints, types, materials and recess dimensions. The solid volume is identical to your files, and the solids are identical apart from the depth shift.

## Automatic recess cut (GolaAutoCut pyRevit extension)

Revit won't let a two-click (line-based) family cut a wall on its own; it only does that for face- and wall-based families. The **GolaAutoCut** extension does it instead.

**What it does**
- When a Gola channel is placed, stretched, moved or has its Wall Setback changed, the channel's recess void cuts every wall it touches. This works with Place on Face and with a picked work plane.
- Walls it no longer touches are uncut.
- It is the same cut as Modify → Cut Geometry.
- Each cut appears as its own **Gola Auto Cut** step in the undo list, right after your action.

**Install and loading**
- Installed at `E:\pyRevit Extensions\GolaAutoCut.extension`. The source is in `pyrevit/` here.
- It loads with pyRevit. In an already open Revit, click **pyRevit → Reload** once.
- A **GolaAutoCut** tab appears with a **Cut Gola Recesses** button. Run it on models edited without the extension, or after moving walls into channels; it syncs every channel in the model at once.

**Other machines and troubleshooting**
- The updater is optional. Models open normally on machines without the extension, but cuts there need the button or Cut Geometry.
- Activity and errors are logged to `%TEMP%\gola_autocut.log`.

**Scope**
- Only walls are cut.
- Other elements (for example cabinets) need their family's "Cut with Voids When Loaded" setting on, plus a code change.

## Verification

Revit 2025, headless, `validation.json`, re-derived by `verify_setback.py`. All gates pass for both families:

- still line based after save and reopen;
- two clicks on a level at an off-axis angle: the location line runs exactly from the first click to the second, and the channel spans exactly that 1500 mm;
- dragging the end grip to 2400 mm, the channel follows;
- front face below the clicked plane equals Wall Setback at 0, 19.05 and 25.4 mm;
- **Place on Face** on a real wall: front face 19.05 mm inside the face, back at 19.05 mm + depth, run equal to the clicked 1500 mm;
- auto-cut, from `test_autocut.py` → `validation_autocut.json`, re-derived by `verify_autocut.py` (all gates pass). This uses the real extension module and updater. Removed wall volume equalled the void's in-wall cross-section × length:
  - horizontal on face: 2,988,601 of 2,988,599 mm³;
  - vertical on face: exact;
  - re-gripped to 2400 mm: the cut grew to match;
  - unhosted work-plane channel inside a wall: cut;
  - channel moved off the wall: cut removed;
  - button with the updater off: cut applied.
  - Headless Revit never idles, so the test flushes the queue the ExternalEvent would flush. The event firing in a live session is the one step verified only by use;
- same solid volume as your originals, with extents shifted only by the change in setback.

The cut-through views are in `preview/`.
