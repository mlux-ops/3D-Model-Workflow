# ELM Surfaces Vivid Ligne Noir 3x10 — seamless colour + bump (Revit)

| Map | File | Format |
|---|---|---|
| Colour | `textures/ELM_Ligne_Noir_3x10_Color.png` | 8-bit sRGB, 3600 × 4000 |
| Bump | `textures/ELM_Ligne_Noir_3x10_Bump16.png` | 16-bit grey, 3600 × 4000, same layout |

**Revit Sample Size: 3'-0" wide × 3'-4" high (36 × 40 in)** for both maps, scale lock on (pixel aspect 0.9 = 36/40).

- Layout: 12 columns × 4 rows of the 3 × 10 in module = 48 tiles, **tiles vertical (flutes vertical), straight stack**, 1/16 in joint, half a joint on every outer edge → both maps wrap seamlessly. For horizontal tiles rotate both maps 90°.
- Bump amount: start at 0.4 (0.3–0.5); relief must read under grazing light.
- Relief (mm above the grout floor): rib tops 1.90, channel floor 0.50 → **pattern relief 1.40 mm, grout step 1.90 mm, clearance 0.50 mm** (channel floor stays above the grout floor). Rib 4.10 mm wide, channel 3.36 mm; 1.2 mm rounded tile edges.
- Colour: 100 % real swatch pixels (photo-based, standing instruction 2026-09-20). Studio lighting removed (length vignette 1.35×, per-flute shading 7.6×); channels 8 % darker, tied to the relief; per-tile tone spread σ = 0.049 (sRGB log) measured from 15 tiles in ELM's installed photo; grout sRGB 220/214/216 from the same photo. Face mean sRGB 48.6/40.9/41.7 vs swatch 46.5/38.6/39.4.

## Evidence (opened and reviewed before delivery)

`textures/_REVIEW_source_ligne_noir.jpg` (swatch → de-lit → strip cuts), `_PREVIEW_tiling_ligne_noir.jpg` (2×2 wrap), `_PREVIEW_corner_wrap_ligne_noir.jpg` (four-way corner, 2×), `_PREVIEW_grazing_light_ligne_noir.jpg`, `_PREVIEW_flute_profile_closeup.jpg`, `_PREVIEW_bump_tiling_ligne_noir.jpg`, `_PREVIEW_room_scale_8ft_ligne_noir.jpg` (8 × 8 ft wall, 2.7 × 2.4 atlas repeats).

`python source/verify_maps.py` (independent, reads the PNGs from disk): PASS — IHDR 8-bit RGB / 16-bit grey, aspect = Sample Size, colour wrap step ≤ noise, bump wrap exact, 10 ribs in all 48 tiles, channel floor 0.263 of range above the grout, 48 distinct faces. Build report: `textures/ligne_noir_build_report.json`. Rebuild: `python source/build_ligne_noir.py` (seed 2026092501).

## Limitations (not defects)

- Sources: `SOURCE_SELECTION.md`. One straight-on swatch exists; all tiles re-sequence its ~9 flute strips, so face-to-face variety is limited (flutes and uniform matte glaze keep it unobtrusive at room scale). A second swatch photo would remove the ceiling.
- Photos give a module aspect of 3.48–3.50 against the stated 3 × 10 (3.33); maps follow the stated nominal.
- Relief depths are inferred from the photos (no manufacturer section); no roughness/gloss map (matte per the product page).
- No Revit render or material validation was performed; the native appearance check is pending.
- Separate from the Belmont B3-02 R2 maps (`output/belmont_preferred_bath2_bath3_r2/B3-02`), which were built from an image-generated glaze field and are not modified here.
