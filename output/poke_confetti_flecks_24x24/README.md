# Poke — Confetti Flecks, 24x24 Matte (Terrazzo-look)

Scope: minimal Revit texture-map deliverable only — ONE color map, ONE bump map, and a
Sample Size. No ADSKLIB, RVT, V-Ray material, ZIP, or Drive upload was produced or
attempted (explicitly out of scope for this task).

## 2026-09-18 correction — see SOURCE_SELECTION.md and PROJECT_MEMORY.md

This deliverable was rebuilt after two errors were found in the original version:

1. **Wrong source image.** The original color/bump maps were built from
   `DAL_Poke_PK23_24x24_RES_03`, a full bathroom room render (shower, mirror, vanity,
   fixtures, floor in perspective) — not a tile face. Fixed by switching to the flat,
   straight-on `DAL_PK23_24x24_ConfettiFlecks_MT_Silo_01` swatch. See
   `SOURCE_SELECTION.md` for the full candidate list and accept/reject reasoning, per
   WORKFLOW.md line 30 ("Correct photographic perspective and baked lighting while
   preserving the product's actual color and character").
2. **Sample Size double-counted the joint.** Daltile's nominal size is already the
   installed module (tile + joint); the original Sample Size added the joint on top of
   the nominal (24 + 3/16 = 24.1875 in), and the image's pixel aspect did not represent
   a stated physical extent at all. Fixed per the rule below.

## Sample Size rule (2026-09-18)

**The Sample Size equals the real-world extent of everything the colour image actually
depicts — nothing else.** The colour image here is a 3x3 grid of Daltile's nominal 24x24 in
installed module (module = 23.81 in actual tile + the joint, not tile + joint added again on
top of nominal). Image pixel aspect is 1:1, matching the 1:1 physical aspect of a 3x3 square
grid.

- Modules: **3 tiles across x 3 tiles down**, grid/stack bond.
- Module (nominal, installed): 24 x 24 in = actual tile 23.81 x 23.81 in + joint 0.19 in
  (matches the product page's stated ~3/16 in grout joint recommendation).
- Sample Size = 3 x 24 in = 3 x 24 in = **72 x 72 in = 6'-0" x 6'-0"**.
- Image pixels: 2100 x 2100 (700 px per module), aspect 1:1 = matches 72:72 exactly.

## Source

- Product page: https://www.daltile.com/products/terrazzo-look/poke/confetti-flecks-square-24x24-matte
- **Accepted** reference image: `references/poke_confetti_flecks_24x24_silo_3000x3000.jpg`
  (`DAL_PK23_24x24_ConfettiFlecks_MT_Silo_01`, flat single-tile swatch, no scene, no
  perspective, no baked lighting), 3000 x 3000 px.
- Rejected candidates and reasons: see `SOURCE_SELECTION.md`.
- `textures/_REVIEW_source_poke.jpg` — the exact swatch crop used.

## Deliverables (`textures/`)

- `poke_confetti_flecks_24x24_Color.png` — 2100x2100, 8-bit sRGB PNG (verified via PNG header:
  bit depth 8, colour type 2 / RGB).
- `poke_confetti_flecks_24x24_Bump16.png` — 2100x2100, 16-bit grayscale PNG (verified via PNG
  header: bit depth 16, colour type 0 / grayscale).
- `_PREVIEW_tiling_poke.jpg` — ILLUSTRATIVE 2x2 wrap/seam check of the whole 3x3 atlas.
- `_PREVIEW_grazing_light_poke.jpg` — ILLUSTRATIVE raking-light shaded preview.
- `_REVIEW_source_poke.jpg` — the accepted source swatch, for visual confirmation.

Each of the 9 modules in the atlas uses an independently-cropped region of the swatch plus a
small per-module tone jitter, so the atlas is non-repeating (AGENTS.md 2026-09-17
seamless/non-repeating instruction) while every module still shows the same real product
colourway. Tile is FLAT (matte terrazzo-look field tile): the bump map carries only subtle
photo-derived surface micro-variation (+/- 0.06 of the 0..1 range) plus the grout-joint
recess. No sculpted pattern/relief was added, since this product has none.

## Bump amplitude / depth

- Working precision: float64 throughout; quantized only at final 16-bit export.
- Height full range: 0.35 mm (subtle, appropriate to a flat matte tile).
- Grout floor: 0.10 of the 0..1 normalized range -> grout recess depth approx 0.315 mm.
- No pattern/flute component (not applicable to this flat product).

## What was inferred vs. sourced

- Sourced directly: nominal 24x24 in module, actual 23.81 in tile dimension, matte finish,
  terrazzo-look fleck coloring, ~3/16 in grout joint recommendation — all from the product page.
- Inferred: exact micro-surface roughness/relief amplitude (0.35 mm range) is an estimate, not
  a measured value, since no manufacturer height spec or scan was available; the specific 9
  crop regions used for the atlas modules are arbitrary (chosen for visual variety only).

## Limitations

- Built from a single marketing swatch photo; no orthographic reference or physical scan.
- No Revit validation was performed (out of scope for this task).
- The tiling/grazing previews are illustrative only, not rendered/native application checks.
