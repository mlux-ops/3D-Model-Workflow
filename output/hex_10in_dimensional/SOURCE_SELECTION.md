# Source selection — 10 in dimensional hexagon tile

Two images were supplied by the user on 2026-09-19. No manufacturer, series name or
product page was given, so no further candidates could be gathered: the usual step of
enumerating a manufacturer's Scene7 assets and rejecting room renders in favour of a
`_Silo_` swatch was not available here. Both supplied images were used, each only for
what it can honestly support.

| # | file | px | view type | verdict | reason |
|---|------|----|-----------|---------|--------|
| 01 | `references/user_supplied_01_flat_layout_variation.webp` | 2000 × 1888 | flat, straight-on layout art of an installed field | **ACCEPTED — geometry and mottle** | Orthographic and evenly lit. It is the only source with no perspective and no baked directional light, so every spatial measurement comes from it: hexagon orientation, lattice pitch, joint width, comb line pitch, the set of face textures and their rough proportions. Its plain tile interiors also supply the glaze mottling. |
| 02 | `references/user_supplied_02_installed_photo_tone_depth.webp` | 1414 × 2000 | installed wall photograph, raking light, props in frame | **ACCEPTED — tone and micro-texture only** | The user identified this as the accurate record of tone and depth, and it is the only source showing the real matte surface. Used for the base albedo and for the fine sandy grain (extracted by high-pass, which discards the lighting gradient). **Rejected for geometry**: the wall is in perspective, the light is a hard raking spot, and roughly 40 % of the frame is mirror, counter, faucet, towel and plant. No dimension, angle or pitch is taken from it. |

## What each accepted source actually contributed

**Reference 01 → geometry.** In this image the joints and the sculpted face textures are
drawn in a slightly cooler grey than the cream glaze, so `(R − B) < 31` isolates them
cleanly (see `source/_REVIEW_reference_mask.png`). From that mask: flat-top hexagons,
column pitch 378 px, across-flats 436.5 px, three face types — plain, coarse stipple and
fine parallel comb — and comb lines running perpendicular to an edge pair, in three
directions 60° apart. Three separate combed faces each measured a 6.21 px line pitch by
FFT, which is 3.61 mm on a 10 in across-flats hexagon.

**Reference 01 → mottle.** Four 200 px squares (4.58 in of real tile) lying wholly inside
plain hexagons, clear of every joint. Joints were found as *long straight dark lines* at
0°/±60°, because a brightness or chroma threshold alone also fires on the field's own
noise and let a joint clip a patch corner — which put a black streak through the first
mottle tile and was caught on review. See `source/_REVIEW_source_crop.jpg`.

**Reference 02 → tone.** Well-lit, prop-free plain faces read (224, 209, 187) and
(215, 201, 178) at the 70th percentile. Reference 01 reads (244, 231, 207), which is
lighter than the product. The build uses (220, 206, 184), between the two and leaning to
the photograph as instructed.

**Reference 02 → micro-texture.** One 200 px plain-face patch, high-passed at σ = 10 px to
strip the lighting falloff, leaving albedo-scale grain at 1.9 % RMS.

## Limitations carried into the deliverable

- Neither image is a scan or a flat product swatch of a single tile. Reference 01 is
  drawn artwork of a field, not a photograph of the glaze; reference 02 is a marketing
  photograph. Fine glaze character beyond what those two carry is not recoverable.
- The nominal size "10 in × 10 in" is ambiguous for a hexagon. See README.md.
- The relief depths are not measured from the product. They are set to read correctly
  under grazing light against the references and are recorded in millimetres so they can
  be corrected if the real figures become available.
- Stipple and comb proportions were read off `source/_REVIEW_reference_mask.png` by eye.
  Automatic blob counting was attempted and abandoned: adjacent textured hexagons merge
  across their shared joint and the counts were unstable.
