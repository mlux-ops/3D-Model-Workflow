# Inference disclosure — P01 `candidate-20260918-01`

`PENDANT.md` requires that inferred values be disclosed rather than presented as
sourced. Everything below is stated as either **drawn** (on the Lightology sheet
MMK661292 / `references/mila/PRODUCT 661292 - Mila Pendant.pdf`), **inferred**, or
**user-directed**.

## Dimensions

| Value | in | Status | Basis |
|---|---|---|---|
| Loop outer width | 8.2 | drawn | Specifications block, `8.2"W x 29.1"H` |
| Loop outer height | 29.1 | drawn | same |
| Frame / strap thickness | 0.5 | drawn | elevation callout; photo-measured 0.528 |
| Canopy diameter | 7.1 | drawn | canopy detail |
| Canopy height | 1.1 | drawn | canopy detail |
| Globe diameter | 6.7 | **inferred** | not dimensioned. Photo-measured 6.64 scaled on the 8.2 loop; inner loop is 8.2 − 2(0.5) = 7.2, so the globe nearly fills it as the photograph shows |
| Band depth | 0.5 | **inferred** | not dimensioned; taken equal to strap thickness |
| Globe centre, body-local Z | 25.20 | **inferred** | 3.9 above loop bottom. Photo places it ≈4.2; the 0.3 difference is recorded, not corrected |
| Socket radius / top / bottom | 0.23 / −0.35 / 0.1 | **inferred** | cable entry detail not dimensioned |
| Seat radius / top / bottom | 0.35 / 28.5 / 28.65 | **inferred** | globe seat not dimensioned |
| Drop constant | 30.55 | derived | canopy 1.1 + socket 0.35 + loop 29.1 |

## A drawing reading that must not be repeated

Both elevations carry **stacked dimension pairs** — `21.7"` over `29.1"`, and
`6.8"` over `8.2"`. The `6.8` and `21.7` belong to a **second product size**, not
to the globe diameter or the inner loop width. The Specifications block pins
MMK661292 to `8.2"W x 29.1"H`, and the photograph's measured aspect ratio 3.569
matches 29.1/8.2 = 3.549, not 21.7/6.8 = 3.191.

This was reported by the P01 preparation session from its own photo measurements
and has not been independently re-measured here. It is recorded because a reader
who takes `6.8"` as the globe diameter will build the wrong family, and
`PENDANT.md` does not currently warn about it.

The two drawing elevations also show the globe at opposite ends of the loop. The
photograph and `PENDANT.md` both place it at the **lower** end; the build follows
the photograph.

## Appearance

Baseline (A) is **user-directed**: dark metal and dark canopy with warm opal
glass, chosen by the user over the brass/white combination shown on the PDF, per
the 2026-09-15 Mila entry in `PROJECT_MEMORY.md`. Metal diffuse `(53, 50, 44)`,
gloss 0.42.

Variant (B) satin brass is **inferred from pixels**: sampled from the
manufacturer render's brass region — median RGB `(194, 175, 122)`, mean
`(196, 179, 131)`, p10 `(178, 158, 106)`, p90 `(226, 208, 147)`. The build uses
diffuse `(186, 166, 112)`, deliberately below the median, because sampled render
pixels already carry specular lift and would otherwise be double-counted. Gloss
0.50.

**No SKU is asserted for the variant.** It is an independent visual variation
required by the test, not a claim that Lightology offers this finish at a 72 in
drop.

Glass for both configurations: `(247, 244, 230)`, gloss 0.65, transparency 0.08,
reflectivity 0.08 → 0.85, self-illumination 100. Self-illumination is an
appearance setting; **no photometric or rendered validation is claimed** — the
exported views are shaded Revit views, not renders.
