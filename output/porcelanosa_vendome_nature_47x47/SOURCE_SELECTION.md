# Source selection: Porcelanosa Vendome Nature 120x120 (47x47), code 100348304

Built 2026-09-27. All sources are in `references/`. They were copied read-only from the user's download
`H:/Downloads/20260926/ZIP_20260926_094705_1221206420/`, and the SHA-256 hashes match the originals
(`_work/references_sha256.txt`).

## Candidates

| file | size | content | decision |
|---|---|---|---|
| `100348304_001.jpg` … `_008.jpg` | 1417 x 1417, 300 dpi tag, **Adobe RGB (1998)** ICC, "PORCELANOSA LIBRARY" EXIF | flat, straight-on full faces of the 8 printed pieces (graphics); no perspective, no room, no joints | **accepted**: pieces 1–8 |
| `100348304_IMGCOM_940.jpg` | 709 x 709, Adobe RGB | the same image as piece 1: NCC 0.976 against a downscaled face 1 (best orientation), 0.04–0.22 against faces 2–8. It is not a layout image | **rejected**: duplicate of piece 1 |
| `Porcelanosa_FTEC_100348304_EN.pdf` | 2 pages | official technical data sheet (pdfgenerator.porcelanosagrupo.com) | **accepted** for facts: size, thickness, joint |

The 8 faces are the full tile face at 1417 px across 1200 mm, which is 29.99 px/in. The build keeps the whole
photo and resamples it into the drawn face at 32 px/in (x1.0656). It is not cropped.

## Product facts

From the FTEC sheet and the Porcelanosa product finder, `productfinder.porcelanosagrupo.com/en/large_format/vendome_nat_pv6_120x120.html`:

- Model VENDOME NAT.PV6 120X120(A), code 100348304.
- Length 1200 mm, width 1200 mm, thickness 6 mm (XLIGHT).
- Tolerance ±0.3 %. 1.440092 m² per piece, which confirms 1.2 x 1.2 m.
- Finish Nature: unglazed / standard, matte. Rectified: yes.
- Product finder: **"Relief: NO"**. The "Eclipse relief effect" paragraph on the FTEC sheet is generic feature text, contradicted by that field. The bump therefore has no designed relief, only photo micro-relief.
- Shade variation V3. LRV 46.32.
- Joint: FTEC says "It is recommended to fix tiles with a minimum joint of 1,5 mm. Do not fix without joint." **Used 1/16 in (1.5875 mm).**
- Grout: the product finder recommends Butech **Colorstuk Rapid PERLA**. No sRGB is published. I used a light pearl grey, sRGB 200/199/195, set about 10 % darker (linear) than the face mean of 209.8/209.0/206.3. This is a design choice.
- Product finder: **"Continuous design: NO"**. No composition, despiece, bookmatch or layout image was found for this SKU, and no direction arrows or rotation guidance.
  - XTONE's Vendome is a different product: a 160x320 slab, bookmatch to order. Its rules were not transferred.

## Layout, measured from the faces

Script: `source/a01_edges.py`, results in `_work/edges.json`.

The test is a band-passed luminance profile of the 3 px strip along one face's edge against the facing strip of
another face. It covers all 8 faces, all 8 dihedral orientations of the neighbour, and all 4 sides, at full
resolution. Two baselines:

- Interior: two strips 3 px apart inside a face, mean 0.39.
- Random: strips from anywhere, p99 0.17.

| joint (right edge -> left edge, both as supplied) | NCC | best along-edge shift |
|---|---|---|
| 1 -> 6 | 0.514 | 0 |
| 6 -> 7 | 0.685 | 0 |
| 7 -> 8 | 0.719 | −1 |
| 8 -> 1 | 0.661 | −1 |
| 2 -> 3 | 0.649 | 0 |
| 3 -> 4 | 0.646 | −1 |
| 4 -> 5 | 0.742 | 0 |
| 5 -> 2 | 0.748 | −1 |

- **Strip A = 1-6-7-8 and strip B = 2-3-4-5.** Each strip loops seamlessly (8 -> 1, 5 -> 2), with all pieces as supplied (r0).
- The two strips are not linked to each other.
- The next-best horizontal match is 0.49, and it needs a mirrored piece.
- At full resolution, 1 -> 6 is visibly continuous: `_work/joints_src/_VIEW_1_6.jpg` shows 1:1 veins crossing. Its lower score comes from a quieter, low-contrast edge, not from a break.

Vertical relationships:

- Among physically possible placements (rotations only), no bottom-to-top continuity scores above 0.24. So **the horizontal joints are ordinary joints**; rows repeat A/B/A/B.
- Higher vertical scores exist only for mirrored pieces (bottom 6 = bottom 8 mirrored, 0.65; top 7 = top 1 mirrored, 0.62). These are traces of how the print file was assembled.
- A printed tile cannot be mirrored, so these placements were not used.

The measured strips and "Continuous design: NO" disagree. The files show that the graphics were made to join
edge to edge in two strips of 4. Porcelanosa does not advertise a continuous layout. The designed set follows the
files; the free-mix set follows the "not continuous" listing.

## Lighting and colour

Script: `source/a02_lighting_joints.py`, results in `_work/lighting.json`.

- **No de-lighting was applied.** There is no measurable baked lighting.
  - A common gradient or vignette across the 8 faces has an sd of 0.042 log, against a content standard error of 0.047.
  - Plane gradients are 0.5 % and −0.7 %, edge to edge.
- Edge tone is continuous across every designed joint. The RMS log difference is 0.036–0.133, against 0.106 for two strips 48 px apart inside a face.
- **Colour:** decoded as Adobe RGB (1998) to linear sRGB in float64. The verifier cross-checks this against a LittleCMS decode: mean |dRGB| ≤ 0.67 levels.
- Out-of-sRGB-gamut pixels are < 0.1 % per face, clipped.
