# R2 material correction review — 2026-09-17

The prior four-tile periodic layouts have been replaced. Visual inspection of all six 3 x 3 repeated atlas previews and the 15-foot overview found no conspicuous atlas boundary, mirrored block or regular pattern of cloudy landmarks at the displayed review scale. Intentional tile joints remain. The original small atlas treatment is superseded.

| ID | Tile layout | Atlas inches | Derived faces |
|---|---|---|---|
| B2-01 | 32 x 32 | 194 x 194 | 1,024 |
| B2-02 | 40 x 20 | 202.5 x 201.25 | 800 |
| B2-03 | 8 x 8 | 188.216535 x 188.216535 | 64 |
| B3-01 | 8 x 16 | 192.5 x 193 | 128 |
| B3-02 | 64 x 20 | 196 x 201.25 | 1,280 |
| B3-03 | 8 x 16 | 192.5 x 193 | 128 |

Derived face counts are sampled variants, not counts of authentic product scans. The fields were generated using the supplied photographs as references, then sampled into constrained physical tile layouts. Product color/texture is an approximation; additional manufacturer face scans remain preferable when available. This revision does not establish exact optical matching to physical samples.

Numerical results are in map_validation.json: image decoding, 16-bit bump, map alignment, exact matching outer-edge samples, atlas extent, and exact duplicate interiors. These tests do not alone establish perceptual non-repetition.

Native results are in revit_validation.json: Revit 2025 save/reopen, six material assignments, all twelve bound texture paths, physical scales, model patterns and warning count. Native_Realistic PNGs are Revit viewport exports with neutral and grazing sun settings, not full renderer output. Texture mapping is visible; flute relief is not reliably visible in this mode. Production bump/reflection verification therefore remains pending. This is a corrected review revision, not a claim that every final optical acceptance gate has passed.

Source limitations: finite texture fields, AI-derived variation, estimated gloss and relief, and limited photographed detail for the niche tiles. Bitmap export resolution must not be described as recovered native photographic resolution. Do not enlarge physical texture scale to hide repetition; extend the tile layout while keeping physical tile size.
