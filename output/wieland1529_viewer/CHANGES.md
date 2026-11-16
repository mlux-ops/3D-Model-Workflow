# 1529 Wieland bathroom viewer — Material Collager release

November 9, 2026. Continues `1529-Wieland-HTML-HANDOFF.md`.

Open `dist/index.html` in Chrome or Edge. It is one self-contained file (16.3 MB); it needs no server and makes no network requests.

## What changed

**One correction to what is drawn.** The released viewer's script had been through an encoding round-trip (UTF-8 saved as Windows-1252 and back). Apart from garbled punctuation in labels (`Â·`, `Ã—`), this broke the tile-size parser: it could no longer read the `×` in the frozen size strings, so every tile except one fell back to a generic 12×24 in. The Elm 2×20, La Belle 3×12, Vera Forma 6×6 and 2×10, and the 24×24 and 24×48 porcelains were all drawn at the wrong size. The rebuild repairs the 92 corrupted sequences, and tiles now render at their nominal size. No pick, product, size string or quantity was edited.

**Look.** The page now uses the Material Collager design system (Monochrome Glass): off-white paper, black ink, hairline rules, Inter (embedded), uppercase micro-labels, inverted ink for the active state, pine green for verified status, and the frosted navigation bar. The 3D stage sits on paper instead of dark navy.

**New**

- **Material board** (`M`): the palette of all ten products in use, the full room schedule with native areas, SKU, size, vendor and observed price, and the Floor & Decor SKU list with one-click copy. Rows and tiles jump to that surface in 3D. It can be copied as tab-separated text for Sheets, or printed.
- **Room schedule**: grouped Penthouse / Triplex, with room numbers, native area and pick swatches.
- **Headings in plain language**: "Penthouse · Bath 4", with the room number, native area and mode above it. Where the viewer label differs from the native room (PH WC 314 = native 313) both are shown.
- **Save view** (`S`): a captioned PNG of the current view.
- **Keyboard**: `↑` `↓` rooms, `R` reset, `Enter` focus view, `G` gallery, `?` the full list. The existing keys (`A` `B` `1` `2` `3` `F` `P` `I` `K` `V` `C`) are unchanged.
- A loading screen while the native geometry unpacks (about 6–8 s), with a readable message if WebGL is unavailable.

## Tile audit (second pass, November 9)

Every tiled surface in the 3D scene was measured against the frozen record: 16 rooms (8 tiled types, A and B), 41 surfaces. Open the viewer with `?audit=1` on the address to re-run it; it reports the product on each surface, wall versus floor, the tile size actually drawn, and that wall tile sits on a native Revit wall face.

Result on this build: **0 mismatches**. Three display faults were found and fixed on the way:

- **Cutaway squashed the tile.** When a tiled wall faced the camera the viewer shortened it by scaling, which compressed the pattern to about 30% (a 20 in tile drawn 6 in tall; 48 in drawn 14.5 in; 12 in drawn 3.6 in). The cut now crops the wall and the tile keeps its size.
- **The default view hid the main tiled wall.** In several rooms the opening camera sat behind the wet wall, so the cutaway removed the very wall under review. Rooms now open looking at their tiled walls.
- **Penthouse Bath 2 showed its back wall at full height only in the "Wet wall" camera.** It now shows at full height whenever you are looking at it from inside the room.

Each pick in the inspector now states whether it is drawn and where ("Drawn on 3 wall faces at 2×20 in") or why it is not.

**Picks that are not drawn (18 across the 16 rooms), by design of the evidence rules:**

- Niche tile in all six tub and shower room types (12): niche size and position are not in the model.
- The conditional walk-in pan in Penthouse and Triplex Bath 3 (4): it applies only if the walk-in option is chosen; the same product is already on the floor.
- **Triplex Bath 4 wall tile, Luxe Sand Matte 24×48 (2): the Revit model has no tub or shower in rooms 007A/B, so there is no wall to put it on.** Only the floor is tiled in the viewer.

**Checked against the architect's drawings.** Sheet A7.0 (Triplex bathroom plans and interior elevations): the wet end, toilet and vanity positions of Triplex Bath 2 and Bath 3 match where the viewer puts tile. Penthouse baths were checked against the model's own fixtures only; there is no penthouse elevation sheet in the Drive folder.

**For the owner to confirm**

- Triplex Bath 4: where the tub goes. The February 2026 floor plan shows two lower-level tub baths labelled Bath 4 and Bath 5, which does not match the model's L-shaped room 007 and Powder 2 (010, which the model shows with a washer and dryer).
- Triplex Bath 3, room 207B: tile is on two faces, not three. The room is about 4.5 in wider than 207A and the model has no wall at the open end of the alcove.
- Penthouse Bath 4: tile is on the back wall of the shower only, not the two sides.
- Wall tile is drawn stacked vertically (2×20 and 3×12 standing up, 24×48 standing up). No layout direction has been chosen; this is the viewer's convention.

## Owner direction and latest floor plans (third pass, November 9)

**Owner direction: three tiled walls in Triplex Bath 3 and Penthouse Bath 4.** Done for both A and B rooms.

- Triplex Bath 3 (207A/B): 207A already had three faces. In 207B the back wall now spans the full room width and the missing side wall is tiled. Antique Blue 3×12, 7.75 ft high as before.
- Penthouse Bath 4 (310A/B): both side walls of the shower end are now tiled as well as the back wall. Pienza Terra 24×48, full height. The plan does not draw the shower, so the side walls run 2.54 ft from the back wall, which is the wet-zone depth in the frozen record.

These are display changes. The frozen quantity pools were not recalculated; Penthouse Bath 4 in particular now shows about 46 SF more wall tile per room than the single back wall did.

Audit on this build: 16 rooms, 46 tiled surfaces, 0 mismatches.

**What the latest plans say** (`25-006 1527 N Wieland_FP.pdf`, sheets A2.1 and A2.2, Issue for Construction, plotted November 9, 2026):

- Room names and numbers match the viewer: Bath 4 = 007, Powder 2 = 010, Bath 2 = 205, Bath 3 = 207, Penthouse Bath 2/3/4 = 305/307/310, WIC 4 = 311.
- **Triplex Bath 4 (007) has a toilet and a sink only. No tub or shower is drawn**, and the room is the same L shape as the model. The frozen wall-tile pick, the niche pick and the Duravit tub for this room therefore have nowhere to go on the current plan.
- Triplex Bath 3 (207): the shower fills the end of the room between three walls in both units; 207B is 5 ft 4 1/2 in wide against 5 ft 0 in for 207A, which is why the model's B room came out different.
- Penthouse Bath 4 (310): sink and toilet on one side, open floor at the WIC end; no shower enclosure, pan or drain is drawn.

## Triplex Bath 4 shower and layout controls (fourth pass, November 9)

**Owner direction: Triplex Bath 4 has no bathtub. It has a 3 ft 5 1/4 in x 3 ft 1 3/4 in shower.** The frozen wall tile (Luxe Sand Matte 24×48) is now drawn on the three shower walls in 007A and 007B.

- Neither the plan nor the model draws the shower, so its position is inferred: the only place in the room those dimensions fit is the corner between the chase, the exterior end wall and the opposite side wall. In 007A that corner is 3 ft 2 1/8 in between walls, so the 3 ft 1 3/4 in side runs across and 3 ft 5 1/4 in runs along the room; in 007B the model has 3 ft 5 1/4 in between walls, so it is the other way round. **Please confirm the corner.**
- Tile runs the full height of the native walls (the model gives no shower tile height).
- The frozen record still calls this pick "Wet tub WALL" and still lists the Duravit tub as the program; those records were not edited. The niche tile is still not drawn (no niche position).
- Display only: frozen quantities were not recalculated.

**New: layout direction and pattern shift, per room and per tile.** Under every drawn pick in the inspector:

- **Turn 90°** runs that tile the other way in that room (for example 24 across × 48 up becomes 48 across × 24 up).
- **Shift** arrows slide the pattern 1 in at a time (Shift-click: half a tile) left, right, up or down, to choose where grout lines and cuts land. **Reset** returns to the default.
- The choice applies to both the A and B room of that type and is remembered in this browser only. It does not edit the frozen picks, and it is not carried to another computer or into the material board.

Audit on this build: 16 rooms, 52 tiled surfaces, 0 mismatches, 16 picks not drawn (12 niche, 4 conditional walk-in pan). The audit accepts a turned tile and reports it as turned.

## Penthouse Bath 3 picks and niches (fifth pass, November 9)

**Owner direction: Penthouse Bath 3 uses the Triplex Bath 3 picks.** Rooms 307A/B now show La Belle Antique Blue 3×12 on the walls, La Belle Purity 3×12 in the niche and Luxe Sand Matte 24×24 on the floor (and on the conditional walk-in pan). The material board and schedule follow. The swap is applied when the viewer runs; the embedded frozen record still holds the earlier picks (Pienza Terra, Elm Tones Sandstone, De Rossi Ivory) and **the frozen quantities for this room were not recalculated**.

**Owner direction: a niche in every tub and shower room.** All 12 rooms (six room types, A and B) now have a recessed niche:

- The back, both sides and the top carry the room's niche tile.
- The bottom is a stone sill, 3/4 in thick, projecting 3/4 in past the tile face.
- The niche is a real recess: the wall tile is opened and the native wall is cut back behind it.

What is assumed, because neither the model nor the plans give it:

- **Size: 12 in wide × 24 in high × 3 1/2 in deep** (one stud bay).
- **Position: sill top 48 in above the floor, centred on the largest tiled wall** that is thick enough for the recess and not interrupted by an opening. In Triplex Bath 4 (007B) the largest wall is only about 2 in thick in the model, so the niche went to the next wall.
- **Stone: not chosen.** The sill is shown in a neutral light stone.
- Valve and plumbing positions were not checked against the niche position.

Under the niche pick in the inspector: **Next wall** moves the niche to another tiled wall, and the arrows move it 1 in at a time (Shift-click: 6 in). Positions are remembered in this browser only. The niche tile also has the Turn 90° and Shift controls.

Audit on this build: 16 rooms, 100 tiled surfaces (48 of them niche faces), 0 mismatches. The only picks not drawn are the 4 conditional walk-in pans.

## Full-length niches and generated tile textures (sixth pass, November 9)

**Owner direction: every niche runs the full length of the wall it is on, its bottom is 4 ft above the floor, and it is 1 ft 6 in tall.** Done in all 12 rooms. This replaces the 12 × 24 in placeholder of the fifth pass.

- The finished bottom (top of the stone sill) is at 48 in and the clear height above it is 18 in.
- Depth is still my placeholder (3 1/2 in), and so is the choice of wall. The niche goes on the largest tiled wall that is thick enough and has no door, window or other gap in that band; where the largest wall fails that test it goes on the next one (Penthouse Bath 2 B, Penthouse Bath 4 B, Triplex Bath 2 B, Triplex Bath 4 B). **Next wall** in the inspector moves it.
- Lengths as built: 30 to 65 in depending on the wall.

**Owner direction: tile textures must show the individual tile as installed, not the vendor preview image.** The viewer used to draw a flat colour per tile with the vendor photo blended over it, so room scenes and mixed layouts (the Elm Tones chevron) ghosted into every tile. Now every pick has a generated texture: a small field of separately generated tiles, one tile per cell, so neighbouring pieces differ the way real ones do. No vendor photo is used as a tile image anywhere. The photos were used once, offline, only to measure each product's body colour.

Audit of the picks (vendor pages read November 9; what each texture is built from):

| Pick | Vendor facts | How it is drawn | Confidence |
|---|---|---|---|
| F&D La Belle Antique Blue 3×12 | Ceramic, high gloss, pressed edge, 8.5 mm, 1/16 in joint | Deep teal-blue glazed pieces, each its own tone, soft mottling, lighter at the cushioned edge | Good: colour from a flat product layout |
| F&D La Belle Purity 3×12 | Ceramic, high gloss | Off-white glazed pieces, very slight variation | Good |
| Elm Tones Sapphire 2×20 | Hand-made-look ceramic, glossy, 8.5 mm | Deep blue glazed sticks with tone variation | **Lowest: the only vendor image is a dim restaurant scene** |
| Elm Tones Sandstone 2×20 | Hand-made-look ceramic, glossy, 8.5 mm | Warm beige glazed sticks with tone variation | Fair: colour from the beige pieces of a mixed chevron photo |
| F&D Luxe Sand Matte 24×48 and 24×24 | Porcelain, matte, concrete look, rectified, 8 mm, colour listed as Ivory | Near-white ivory with soft concrete clouds | Good |
| F&D Pienza Terra 24×48 | Porcelain, matte, travertine look, rectified, 9 mm, colour listed as Beige | Grey-beige with soft travertine clouding and small filled pits | Good |
| F&D De Rossi Ivory 24×24 | Porcelain, matte, terrazzo look, rectified, 10.5 mm | Ivory field with light and warm-grey chips | Good (no longer used in a room after the Penthouse Bath 3 change) |
| F&D Perimeter Gray 24×48 | Historic unselected alternative | Uniform warm grey | Good |
| Elm Vera Forma Earth Lines 2×10 | Hand-made 3D ceramic, glossy, 8.6 mm | Brown ribbed relief with glaze on the crests | Fair: ribs assumed to run along the tile length |
| Elm Vera Forma Indigo Edge 6×6 | Hand-made 3D ceramic, glossy, 8.6 mm | Blue-grey ribs following two edges and meeting on the diagonal | Fair: vendor photo is in direct sun |

Limits: these are generated from published facts and measured colours, not from physical samples, and the F&D porcelains are printed tiles whose real faces I have not seen one by one. Grout is still the viewer's illustrative 1/16 in neutral grey, not a selection. The small thumbnails in the room list and material board are still the vendor's own product photos, as references.

Audit on this build: 16 rooms, 100 tiled surfaces, 0 mismatches; the audit now also fails any surface that still uses a vendor photo, and none does.

**Still for the owner**

- Tile colours: check Elm Tones Sapphire in particular against a physical sample.
- Niches: confirm the wall per room and the depth, and choose the sill stone.
- Penthouse Bath 3: quantities need recalculating for the new picks.
- Triplex Bath 4: confirm the shower corner, and whether the niche and Duravit tub come off the picks.
- Wall tile layout direction: now adjustable per room in the viewer; tell me the directions to make the default.

## Luxe Dune Linear

The substitution of Luxe Dune Linear (F&D 101492288, 18×36) for Serenity Sands is recorded on the material board and in the SKU list as **pending placement**. It is not rendered in any room: neither tile appears in the frozen picks, so the room and wall it belongs to is still unknown. It needs one answer from the owner — which room and which wall — and a vendor image.

## What was not changed

The frozen picks, the native geometry bundle, the Three.js modules and the primary plumbing metadata are byte-identical to the baseline; the build checks their hashes and fails otherwise. No geometry, room mapping, fixture, quantity or Revit record was touched. Rooms without a pick are still neutral.

## How it is built

The editable sources are on MAXSPC and were not available on this PC, so this is a post-build over the released file rather than a hand edit:

```
python -B build_restyle.py                # baseline/index.html -> dist/index.html
python -B build_restyle.py path/to/index.html
```

It needs only the Python standard library. Every hook it patches is asserted. Re-run it on the output of `scratch/build_viewer3d_index.py` after any upstream rebuild.

| File | Role |
|---|---|
| `baseline/index.html` | The November 9 release, untouched (SHA-256 `a378d90f…1841b`) |
| `src/base.css`, `src/theme.css` | Design tokens and component styles |
| `src/shell.html`, `src/loading.html` | Navigation bar and loading screen |
| `src/enhance.js` | Material board, schedule, headings, shortcuts, PNG export, tile audit, owner-directed walls, layout controls |
| `src/fonts/` | Inter variable font and its OFL licence |
| `tools/gen_tile_textures.py` | Generates the single-tile texture sheets (needs numpy and Pillow); run it before the build when a tile recipe changes |
| `src/tiles/` | Generated colour and normal sheets, their manifest, and `_preview.png` |
| `dist/index.html`, `dist/build_manifest.json` | Output and its hashes |

## Checked

In a browser at 1440×900 and 375×812, served from a local static server: all 13 room types load through the gallery with no script errors; Full / Wet-zone / Native modes, A/B switching, Compare A/B, focus view, legacy `#PH-WC/314A` link, material board, PNG export and keyboard navigation work; the page requests nothing but itself; the phone layout has no horizontal overflow. The tile-size fix was checked two ways: the parser from each file run against every frozen size string, and PH Bath 2 compared on screen before and after.

Not checked: opening by double-click (`file://`) in desktop Chrome, a real phone, and printing the board.

## Still open

- **Fix the encoding at the source.** `scratch/viewer3d_scene_v2.js` on MAXSPC should be re-saved as clean UTF-8; until then every upstream rebuild reintroduces the tile-scale bug (this post-build repairs it again).
- Delivered to the Drive viewer folder on November 9: `index.html` replaced in place (same link; the previous release remains in Drive's version history and in `baseline/` locally), with this note and the build files in `restyle-build/`.
- The evidence limits in the handoff stand: primary shower and drain positions, Bath 3 tub-versus-walk-in, the unlocated TX Bath 4 tub, and niche locations are unchanged.
