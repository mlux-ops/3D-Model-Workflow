# Round 001 — PH-BATH3 — critic-build

**Seat:** Tile installer / GC (**weight 0.25**). Scores are 1–5; **seat scores use one decimal**. This is a blind constructability critique, not a quantity release. Current Revit model identity and dimensions are **unverified**: the [room geometry](../../geometry.json) contains a prior drawing-derived 5.00-ft tub back wall, two 2.33-ft returns, 7.75-ft tiled height, 9.67-LF wall run and 35-SF bath; openings, niches, substrate and fixture positions are unknown. The [plumbing schedule](../../plumbing.json) lists a Delta **DT062412 4-in. square shower drain** although the geometry identifies a **tub alcove**; reconcile this scope discrepancy before preparing any shower pan.

## Candidate A — seat score **3.4 / 5.0**

| Installation criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet-wall suitability and substrate | **4 / 5** | [Tones Sandstone 2 x 20](https://www.elmsurfaces.com/product/sandstone-tones) expressly lists **Wet Areas**, and a small ceramic wall format is practicable on a properly waterproofed tub surround; substrate layers and niche waterproofing remain unverified in [geometry](../../geometry.json). |
| Wall lengths, cuts, lippage and offset | **3 / 5** | At [5.00 ft + two 2.33-ft returns and 93-in. tiled height](../../geometry.json), nominal 20-in. vertical sticks require a controlled top/bottom cut (four full lengths leave roughly 13 in. before joints), while opening and valve cuts cannot yet be planned. |
| Bathroom floor / drain coordination | **3 / 5** | [Cortar Bone 12 x 24 Soft](candidates/A.md) is proposed on the bath floor, with no published wet DCOF >=0.42; [Delta DT062412](../../plumbing.json) is listed despite a tub-alcove plan, so slope/drain applicability is unresolved. |
| Niche, trim and plumbing penetrations | **3 / 5** | A [same-product Sandstone niche](candidates/A.md) avoids an accent-material junction, but niche size/reveals, tub-tile termination, Hansgrohe control cutouts and trim profiles have no verified elevations or field details. |
| Waste, procurement and installation sequence | **4 / 5** | [86.2 SF wall + 8.63 SF provisional niche](candidates/A.md) comes from an approximately 74.9-SF net wall with 15% allowance; same-tile consolidation simplifies sequencing, but the niche opening must be deducted once and the wall quote/lot confirmed ([product evidence](../../../../research/products/elm-tones-sandstone-2x20.md)). |

**top_fix:** Submit the exact **Cortar Bone Soft 12 x 24 wet-floor DCOF report** for this bath before floor approval; if it cannot meet the published >=0.42 threshold, select a separately approved floor product.

**gate_flags:**
- **FAIL — FLOOR_DCOF_UNPROVEN:** No published DCOF >=0.42 has been provided for the proposed Cortar Bone Soft bathroom floor ([candidate](candidates/A.md); [board gate 2](../../../../board/BOARD.md)).
- **OPEN — GEOMETRY/PLUMBING:** Existing tub-alcove geometry disagrees with the 4-in. shower-drain schedule; opening/niche dimensions and wet-wall waterproofing details require model and field verification ([geometry](../../geometry.json); [plumbing](../../plumbing.json)). This is a coordination hold, **not proof of an impossible tile layout**.

**confidence:** **medium** — product wall approval is documented, but current model and floor test are not.

## Candidate B — seat score **2.8 / 5.0**

| Installation criterion | Score | One-line evidence-based reason |
|---|---:|---|
| Wet-wall suitability and substrate | **2 / 5** | [Tones Opal 2 x 20](candidates/B.md) lacks a product-specific **Wet Areas** confirmation in the supplied source audit, so tub-wall setting remains unapproved despite the [Tones collection](https://www.elmsurfaces.com/product-collection/tones) listing wet areas generally. |
| Wall lengths, cuts, lippage and offset | **3 / 5** | The same [60-in. back wall, two approximately 28-in. returns and 93-in. tiled height](../../geometry.json) support a nominal vertical stack, but courses, openings and niche cuts are unverified and must be set out before ordering. |
| Bathroom floor / drain coordination | **3 / 5** | [12 x 24 Cortar Bone Soft floor](candidates/B.md) has no verified wet DCOF >=0.42, and the [tub-versus-square-drain conflict](../../plumbing.json) makes any assumed shower-floor slope unsupported. |
| Niche, trim and plumbing penetrations | **3 / 5** | A [contrasting Sandstone 2 x 20 niche](candidates/B.md) adds a color/grout junction and wrapped returns at an unmeasured recess, with chrome valve, bar and showerhead penetration locations still unknown ([plumbing](../../plumbing.json)). |
| Waste, procurement and installation sequence | **3 / 5** | [86.2-SF Opal field plus estimated 8.63-SF Sandstone niche](candidates/B.md) requires two controlled tile lots, niche-field deduction and special cuts; the niche has no measured perimeter or trim count. |

**top_fix:** Obtain **product-specific written Wet Areas approval for Opal 2 x 20**, or replace that wet-wall tile with a manufacturer-listed alternative.

**gate_flags:**
- **FAIL — OPAL_WET_WALL_UNPROVEN:** No color/product-specific Wet Areas listing for this shower/tub wall is established in the candidate packet; collection-level wording does not resolve the contrary product audit ([candidate](candidates/B.md); [board gate 1](../../../../board/BOARD.md)).
- **FAIL — FLOOR_DCOF_UNPROVEN:** Cortar Bone Soft bathroom-floor DCOF >=0.42 is undocumented ([candidate](candidates/B.md); [board gate 2](../../../../board/BOARD.md)).
- **OPEN — GEOMETRY/PLUMBING:** Unmeasured niche and valve locations plus a listed square drain in a tub-alcove room require coordination ([geometry](../../geometry.json); [plumbing](../../plumbing.json)).

**confidence:** **medium-low** — layout is buildable in principle, but two product gates and the live-room verification are outstanding.
