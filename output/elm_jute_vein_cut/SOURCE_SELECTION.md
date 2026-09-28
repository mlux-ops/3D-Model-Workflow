# ELM Jute Vein-Cut: source selection (24x48 and 1x3 mosaic), 2026-09-26

ELM Surfaces ElmStone Jute Vein-Cut is the same product as MILE stone (Florim USA) EcoStone Vein-Cut Jute. The ElmStone
catalog and the EcoStone brochure share SKUs: 24x48 = 1104304, 1x3 mosaic = 1104340.

Rule applied: colour comes only from flat, straight-on photos of the tile face. Room renders, angled shots and installed
shots are never colour sources. Identity was tested by NCC on band-passed luminance at 8 px/in, with 6 patch templates,
scales 0.92 to 1.08, and 4 orientations (`source/a03_dupes.py`, `_work/dupes*.json`). Where one image contains another, it
was located by `source/a04_locate.py` (`_work/locate.json`). Phase-randomised surrogate baseline: 0.14 to 0.17.
Recompressed copies of the same photo score 0.99 or more.

## Candidates

| id | file | what it is | decision | reason |
|---|---|---|---|---|
| u09 | `references/user_supplied/u09_flat_veincut_swatch.webp` (1890x945) | flat straight-on 24x48 face | **ACCEPT: face A** | Prime source. NCC 0.995 with `references/belmont_tiles/jute_original.jpg` and `PrimaryBath_Wall_...jpg`, 0.995 with ELM w01, and 0.991 with MILE w04 (w04 is the same photo, flipped). All of these are one photo. |
| old05 | `output/belmont_tiles/ElmStone_Jute_24x48/references/05_new_flat_veincut.jpg` | flat straight-on face | **ACCEPT, re-toned: face B** | This is a different face from u09 (NCC 0.34 to 0.37). Its colour is much paler (mean sRGB 239/233/219, against 218/207/188 for the Jute swatch). The MILE Jute 24x48 panel w05 contains its two halves in the Jute colour (NCC 0.91 and 0.94, rotated 180°). So old05 was re-toned by per-channel quantile mapping onto those registered halves: result 216.7/204.7/186.2, halves 216.2/204.4/185.9. |
| manufacturer_03 | `.../references/manufacturer_03_flat_swatch.webp` | cross-cut face | REJECT | Same photo as 06 (NCC 0.998). It is the cross-cut finish, not the vein-cut. It is not the same photo as u09 (0.24). |
| 06 | `.../references/06_new_fluted_crosscut.webp` | ridged cross-cut | REJECT | Different finish (cross-cut, with ridges). Used only as the positive control for the ridge test. |
| manufacturer_04 | `.../references/manufacturer_04_installed_ridged.jpg` | installed, ridged cross-cut | REJECT | Installed room shot of a different finish. |
| w01 | `references/web/w01_elm_jute_veincut_24x48_01.jpg` (ELM) | 24x48 swatch | duplicate of A | Byte size is identical to `jute_original.jpg` (623748), NCC 1.000. |
| w02 | `references/web/w02_elm_jute_crosscut_24x48_03.jpg` (ELM) | cross-cut 24x48 | REJECT | Wrong finish (cross-cut). |
| w04 | `references/web/w04_ms_ecostone_jute_veincut_24x48_01.jpg` (MILE) | 24x48 swatch | duplicate of A | NCC 0.991 to 0.997 (flipped copy). |
| w05 | `references/web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg` (MILE, 3600x2400, 50 px/in) | flat half-offset layout mock-up | colour reference for B; layout cue | Its two full tiles are A (NCC 0.93 and 0.97) and its two half tiles are B's halves. It adds no new face. Joint drawn at about 2.8 px, roughly 1/16 in; this is a rendering, not installation guidance. |
| w11 | `references/web/w11_ms_jute_veincut_12x24_03.jpg` | 12x24 swatch | duplicate (crop of A) | NCC 0.98, contained in A. |
| w12 | `references/web/w12_ms_jute_veincut_panel_12x24.jpg` (25 px/in) | 12x24 layout mock-up | REJECT | Low resolution. Its tiles are crops of A and B (partial matches 0.51 and 0.59). |
| w14 | `references/web/w14_ms_jute_veincut_48x110_04.jpg` (2039x4660) | flat straight-on 48x110 slab | **ACCEPT: faces W1 to W4 and the mosaic chip pool** | Same Jute Vein-Cut print, larger format. Rotated 90° so the veins run horizontally. It contains A (flipped, 9/9 templates, NCC 0.74, box x 1425-3383 / y 499-1478 px); everything outside that box is new content. Exposure is darker (206/191/172), so it was re-toned to u09 by quantile mapping over its A region. Effective 41.44 px/in on the swatch scale. |
| w15 | `references/web/w15_ms_veincut_jute_48x110_panel.jpg` (20.8 px/in) | four-slab layout mock-up | REJECT | Half the resolution needed. Slab 0 is B above A, slab 1 contains B, and slab 3 is w14. It would give soft cells. |
| w06, w17 | MILE room renders (48x110 wall, 24x48 floor) | room scene | REJECT | Room render rule. |
| w13 | MILE 12x24 room scene | room scene | REJECT | Room render rule. |
| w16 | MILE 24x48 Grip, outdoor pool render | room scene, different finish (Grip) | REJECT | Room render, and a different finish. |
| u10 | `references/user_supplied/u10_floor_room_shot.png` | floor room shot with sun patches and perspective | REJECT | Room shot rule. |
| w07 | `references/web/w07_ms_jute_veincut_1x3mosaic_01.jpg` (414x414, 34.5 px/in) | straight-on 1x3 sheet | layout, joint and tone reference only | Shows 4 x 12 chips in a straight stack with the columns aligned. Chip pitch ratio 2.99, joint about 0.06 in (FWHM 2.07 px). Chip mean-tone sd 0.039 (log). Too small to use as a colour source. |
| w10 | `references/web/w10_ms_jute_1x3mosaic_wall.jpg` | kitchen room render | layout cue only | Straight stack, columns aligned. Room render, not a colour source. |
| u11 | `references/user_supplied/u11_mosaic_1x3_installed.png` (638x344) | installed 1x3 wall, near-frontal | layout and tone statistics only | Straight stack, columns aligned (column-mean profile shows dips only at the chip pitch, 46.83 px, and none at half pitch). Local chip-tone sd 0.087 (log linear luminance, after a 5x5-chip median high-pass). Grout sits close to the face tone. Too low-res to be a colour source. |
| PDFs | `w03` ElmStone catalog (21 pp), `w08` EcoStone brochure 2026 (23 pp), `w09` MILE tech specs | specs | facts | Sizes, SKUs, 8 mm thickness (6 mm for 48x110), rectified, V3 moderate shade variation. Neither actual size nor grout joint is published. The ELM product page lists its spec sheet as "UNAVAILABLE". |

## Result

Six distinct real vein-cut faces were available at 40 to 50 px/in: A, B and W1 to W4. The W windows are the four corners of
the w14 slab, and each overlaps w14's copy of A in one corner only: W1 13.3 %, W2 11.6 %, W3 17.1 %, W4 14.9 % of the face.
The mosaic draws chips from A, B, and w14 with its A box excluded.

## Finish (ridge) check, `source/a05_ridges.py`

Method: the across-vein power spectrum was taken at pitches of 0.05 to 0.25 in. Peak prominence of the ridged cross-cut 06:
75.8, at a 0.091 in pitch. Vein-cut u09: 1.09. w05: 1.09. w14: 1.07. old05: 1.08. That is no periodic ridge structure. The
product finish is listed only as Matte, with Grip as a separate MILE finish. **No ridges are modelled.** The 2026-09-20
ridged bump variant was derived from a cross-cut photo, and it does not apply to the vein-cut.
