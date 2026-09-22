# 10 in dimensional hexagon tile — colour + bump

Seamless, non-repeating texture pair for Revit, built 2026-09-19 from two user-supplied
reference images. Manufacturer and series were not supplied.

## Deliverable

| file | format | size |
|---|---|---|
| `textures/Hex10_Dimensional_Color.png` | 8-bit sRGB, PNG colour-type 2 | 4489 × 4536 px |
| `textures/Hex10_Dimensional_Bump16.png` | 16-bit greyscale, PNG colour-type 0 | 4489 × 4536 px |

Bit depths verified from the PNG IHDR bytes, not from a library report.

### Revit Sample Size

**70.148 in × 70.875 in**  —  5′-10 5/32″ × 5′-10 7/8″

That is the real-world extent of everything in the image: 8 hexagon columns at 8.7685 in
column pitch by 7 rows at 10.125 in row pitch. The image pixel aspect (4489 / 4536 =
0.98964) matches the physical aspect (70.148 / 70.875 = 0.98975) to 0.011 %, well inside
Revit's scale lock.

Set **Repeat: On** in both directions. Suggested **bump amount 0.40** — this is a
dimensional tile and wants more than the ≈ 0.2 a flat tile takes.

## Geometry

| | |
|---|---|
| hexagon orientation | flat-top (horizontal top and bottom edges, vertices left and right) |
| across flats | 10.000 in |
| across corners | 11.547 in |
| joint | 1/8 in, drawn at half-width on every outer edge so the image wraps |
| module, flats direction | 10.125 in |
| atlas | 8 columns × 7 rows = 56 hexagons |
| resolution | 64 px/in |

### The nominal-size assumption — read this before using the map

A regular hexagon cannot be 10 in × 10 in. "10 × 10" was taken to mean **10 in across the
flats**, which makes the piece 11.547 in point to point. If the product is actually 10 in
*point to point* (8.66 in across flats), every dimension here scales by 0.866 and the
Sample Size becomes **60.75 in × 61.38 in**. Nothing else in the build changes — set
`FLATS_IN = 8.660` in `source/build_maps.py` and re-run, or just enter the smaller Sample
Size in Revit, since the image is the same picture at a different scale. Confirm which
one the manufacturer means.

## Faces and how the non-repetition is built

Three face types, all present in both references:

| face | count of 56 | relief |
|---|---|---|
| plain | 22 (39 %) | matte micro-relief only |
| stipple | 17 (30 %) | coarse pitting, 2 mm and 5 mm wavelengths |
| comb | 17 (30 %) | parallel striations at 3.61 mm pitch (measured), in 3 directions 60° apart |

The proportions were read off `source/_REVIEW_reference_mask.png` by eye; the comb pitch
and directions were measured (see SOURCE_SELECTION.md).

Every hexagon independently draws its face type, comb direction, mottle crop offset,
mottle rotation, stipple field offset and rotation, and tone jitter from a hash of its
wrapped (column, row). A repair pass then removes every adjacency where two combed faces
share a joint with their lines running the same way — the case that reads as a repeat —
while leaving the face mix exactly as specified. 0 such adjacencies remain; 4 pairs of
touching stipple faces remain, which the reference also shows and which is not a repeat.

**Seamlessness is structural, not faded.** The hexagon field is the Voronoi diagram of a
triangular lattice of centres, and those centres are enumerated on a torus, so the
pattern continues across the image border rather than being blended there. The measured
wrap step is *below* the typical step between two adjacent interior pixels:

```
colour left/right    wrap step 4.31   typical neighbour step 8.30
colour top/bottom    wrap step 4.21   typical neighbour step 8.30
bump   left/right    wrap step 0.052  typical neighbour step 0.102   (mm)
bump   top/bottom    wrap step 0.046  typical neighbour step 0.102   (mm)
```

A finite bitmap is periodic; this is not a claim of mathematical non-repetition. The
atlas covers 70 in, so a 20 ft wall shows 3.4 repeats horizontally — checked in
`textures/_PREVIEW_wall_scale_hex10.jpg`, where no atlas boundary or repeated cluster is
identifiable.

## Relief, in millimetres

The bump map's full 0–65535 range is **2.00 mm**.

| | mm |
|---|---|
| grout floor | 0.00 |
| tile base plane | 1.50 |
| **grout step** | **1.50** |
| comb crest / valley | +0.10 / −0.35 (0.45 peak to peak) |
| stipple crest / pit | +0.05 / −0.50 (0.55 peak to peak) |
| matte micro-relief, all faces | ±0.030 |
| chamfer at the tile edge | 0.30 drop over a 2.0 mm band |
| deepest pattern point below the tile plane | −0.575 |
| **lowest face point above the grout floor** | **+0.825 — clearance, > 0** |

Pattern depth and joint depth are separate terms. The pattern was deepened on its own;
the grout step was not raised to compensate and no global bump multiplier was used. The
pattern's deepest point still sits 0.825 mm clear of the grout floor, so the face never
reads as punctured.

Judged under grazing light at 12–15° elevation in
`textures/_PREVIEW_grazing_light_hex10.jpg` and `_PREVIEW_face_closeup_hex10.jpg`: the
comb reads as distinct ridges and the stipple as pitting, neither needs squinting, and
both stay clearly shallower than the joint.

## Colour

Base albedo **(220, 206, 184)** — a warm greige. It sits between the installed
photograph's well-lit plain faces (215–224, 201–209, 178–187) and the flat layout art
(244, 231, 207), leaning to the photograph as instructed. Grout **(188, 178, 164)**.

On top of the base:

- glaze mottling from the flat reference's own plain tile faces, ×1.6, on a 4.58 in tile
- fine matte grain from the photograph's plain faces, ×0.8, on a 2.12 in tile
- per-hexagon tone jitter ±1.4 % and warm/cool jitter ±0.8 %, kept subtle because both
  references show a fairly uniform shade
- local cavity darkening from the relief, gain 0.18
- whole-face cavity occlusion: plain 1.000, comb 0.970, stipple 0.952, so the textured
  faces stay legible at room distance the way they do in the references

No directional room shading is carried through: the photograph's raking light and falloff
were removed by high-pass before its grain was used, and nothing else was taken from it
spatially.

## Facts sourced vs inferred

**Measured from reference 01:** flat-top orientation; lattice pitch; three face types;
comb line pitch 3.61 mm (three independent faces, all 6.21 px); comb directions 60° apart;
glaze mottling amplitude.

**Measured from reference 02:** base albedo; fine grain amplitude.

**Read by eye from reference 01:** the plain / stipple / comb proportions.

**Inferred, not measured — correct these if real figures appear:** the 1/8 in joint
(standard for a large-format hexagon; neither image gives a dimension); every relief depth
in millimetres; the chamfer; the grout colour; the 2 mm and 5 mm stipple wavelengths; the
2.12 in physical scale assigned to the photograph-derived grain tile, which is estimated
from the apparent hexagon size in that frame and is therefore uncertain.

## Limitations

- Marketing artwork and a marketing photograph, not scans. Neither is a flat swatch of a
  single tile face.
- No manufacturer, series, SKU, actual size, or recommended joint width was available.
- The 10 in across-flats reading of the nominal size is an assumption. See above.
- Relief depths are art-directed to match the references' appearance, not measured off
  the product.
- **No Revit validation was performed.** The maps have not been loaded into a material,
  rendered, or checked on a surface in Revit. The optical acceptance gate is therefore
  **pending**; seamlessness and non-repetition passed on the preview evidence listed below.
- Upscaling adds no detail: the references are 2000 px and 1414 px, and the 4489 px atlas
  gets its sharpness from procedural relief, not from the sources.

## Review evidence

| file | what it shows |
|---|---|
| `source/_REVIEW_reference_mask.png` | the reference's joints and textured faces isolated |
| `source/_REVIEW_source_crop.jpg` | the exact source patches used, and the mottle and grain tiles |
| `textures/_PREVIEW_tiling_hex10.jpg` | 2 × 2 wrap of the colour map |
| `textures/_REVIEW_wrap_seam_hex10.jpg` | the four-way corner, magnified, colour and grazing |
| `textures/_PREVIEW_grazing_light_hex10.jpg` | the whole atlas at 15° light |
| `textures/_PREVIEW_face_closeup_hex10.jpg` | one plain, one stipple and one comb face at 12° light |
| `textures/_PREVIEW_wall_scale_hex10.jpg` | a 20 ft × 12 ft wall at true scale, 3.4 × 2.0 repeats |

Every one of these was opened and inspected before delivery. Two defects were found and
fixed that way: a joint line captured inside the first mottle tile, and a first build in
which the stipple came out as 40 mm camouflage blobs (a units error in the noise
band-pass) with the comb lines running parallel to the tile's top edge instead of
perpendicular to it.

## Rebuilding

```bash
python source/extract_source.py     # mottle + grain tiles from the references
python source/measure_reference.py  # lattice, comb pitch, textured-area fraction
python source/build_maps.py         # the two delivered maps
python source/make_previews.py      # review images + numeric seam check
```

Python: `C:\Python314\python.exe` on this machine (numpy 2.5.0, pillow 12.2.0). Seed
20260919; the build is deterministic. Every write goes through an `out_path()` guard that
raises outside `output/hex_10in_dimensional/`.
