# Step 6.1: what the Revit geometry lacks at camera distance

Written 2026-11-11. Source unit pair: the north half (north triplex and north penthouse).
This is the agent's proposal. The owner prioritizes; until then the work follows the order
below, which is the agent's own order of what shows most at camera distance in D1 to D5.

## How this list was made

- Counts come from `review\phase3\building_groups.csv` (2,585 objects of the Revit export,
  grouped by unit in Phase 3) and from reading object names and materials in the editor.
- Pictures: `review\phase6\rooms_north_grey_a.png` (triplex rooms) and
  `review\phase6\rooms_north_grey_b.png` (penthouse rooms and D1 to D5); single images in
  `review\phase6\views\`. Floor plans drawn from the objects' bounding boxes are in
  `review\phase6\views\plan_*.png`.
- Conditions of the grey pictures: editor view mode "Lighting Only" (every surface shown
  in the same neutral grey so that only shape and shadow read), 1280 by 720, 24 mm lens,
  eye at 1.60 m. The rooms have no lighting of their own until the lighting phase, so a
  temporary 150-candela work lamp was placed 30 cm above each camera. The lamp and the
  cameras were removed afterwards; nothing was saved in the Unreal project.

## What the export already holds (so it is not rebuilt)

| Kind of object | North triplex | North penthouse | South triplex | South penthouse |
|---|---|---|---|---|
| All objects | 713 | 518 | 722 | 372 |
| Casework (cabinets, counters, panels) | 114 | 49 | 112 | 49 |
| Furniture | 50 | 29 | 38 | 31 |
| Plumbing fixtures | 30 | 27 | 26 | 23 |
| Lighting fixtures | 136 | 143 | 175 | 73 |
| Doors | 34 | 23 | 33 | 23 |
| Windows | 18 | 13 | 18 | 13 |
| Generic models (shower fittings, fireplaces, planters and others) | 62 | 28 | 50 | 23 |

The export is already furnished in part: beds with night stands in every bedroom, sofas,
armchairs and a coffee table in the living rooms, dining tables with chairs, bar stools,
eight rugs, a television, and outdoor tables and chairs on the patio and roof deck. The
kitchens are modelled in detail (handle-less channel fronts, reveal strips, side panels,
taps, cooktops, ovens, pendant lights).

## Gaps, in the order they will be worked

| Order | Gap | Where it shows | Measured or counted | Proposed fix (step) |
|---|---|---|---|---|
| 1 | Sharp, unrounded edges on fit-out objects: counters, island, cabinet fronts and panels, tub, basin and vanity edges | D2, D3, D4 at under 2 m; every kitchen and bath | Counted per view before and after in step 6.2 | New rounded copies of the meshes as new assets; recorded in `mesh_swaps.csv` (6.2) |
| 2 | No baseboards anywhere | Every room with a visible wall foot: D2, D3, all bedrooms, living rooms, halls | 0 baseboard objects in 2,585 (the 28 names containing "base" are base cabinets) | Generated baseboard runs along wall feet, new assets (6.2) |
| 3 | No tile on bath walls and no grout joints; bath walls carry the gypsum-board material | D4; all baths | In the D4 bath every wall uses `09_23_00_Gypsum_Wall_Board`; one wall object in the whole model uses `Tile__Porcelain__24x12` | A tile alternative for bath walls with recorded relief, switchable; not applied as a replacement, because the owner has not marked any material "rebuild" (6.3, 6.7) |
| 4 | Switch plates and outlets missing | Beside every door; kitchen splashbacks | 5 light switches in the model, all in the north penthouse; 1 object named "outlet"; none elsewhere | Generated switch plates beside door openings, new assets (6.2) |
| 5 | No door casings or reveals at door frames by name; cabinet door gaps exist in the kitchens but not on vanities and wardrobes | D2, D3, halls | 0 objects named "casing"; the 19 names containing "trim" are window and kitchen trim | Shadow-gap reveals at cabinet fronts that lack them; door trim left as Revit modelled it, recorded (6.2) |
| 6 | Soft furnishings and loose items missing: no window treatments, bedding detail, towels (2 only), books, tableware, plants | D2, D3, bedrooms, baths | 0 curtains, shades or blinds; 2 towels | Proposal only in `furniture_proposal.csv`; grey stand-in blocks until the owner approves (6.4, 6.5) |
| 7 | Rooms with no furniture at all | Triplex lower level: family room, both rear bedrooms, garage; triplex 2nd floor primary bedroom and laundry; penthouse 3rd floor hall | Seen empty in the grey pictures | Stand-in blocks of the proposed set (6.5) |
| 8 | Hardware: door handles present on few doors; cabinet pulls absent by design (channel fronts) | Doors at under 2 m | 6 objects named "handle" | Listed for the owner; door hardware belongs to the door families in Revit and is not invented here |
| 9 | Mirrors over basins not modelled as mirrors in several baths | Baths | No object named "mirror"; mirror material exists in the audit | Listed for the owner; stand-in where a bath has none (6.5) |

## Things that are fine as exported and stay untouched

- Kitchen fronts: the gaps between doors, the handle channels and the reveal strips are
  modelled and read in D2 and D3.
- Plumbing fittings (taps, shower heads, valves, toilets) are detailed enough at 1 to 2 m.
- Pendant and wall lights are modelled; their light is set in the lighting phase.
- Stairs, railings, pergola and patio structure.

## Questions for the owner (the work does not wait for the answers)

1. Which half and which rooms are D2, D3 and D4? The north half was used; positions are
   in `REFERENCE_VIEWS.md`.
2. Should bath walls be tiled, and with which tile and how high? The Revit model shows
   painted board.
3. Do you want baseboards, and of what height and profile? A flat 100 mm by 12 mm board
   is generated as the default so the wall foot does not read as a knife edge.
4. Door casings: flush frameless doors (as modelled) or cased openings?
