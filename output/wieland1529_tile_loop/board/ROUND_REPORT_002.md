# 1529 Wieland — Round 002 final board report

**Scored November 6, 2026, after separate Round 002 submission.** Focus: TX-BATH2, TX-BATH3, TX-BATH4, each duplicated across the two Triplex dwellings. All twelve original blind critiques are present and complete (four seats per room); submitted six candidate SHA-256 files match `state/ROUND002_PREFLIGHT.json`. The private `_key.json` files were opened by prime **only after** critic completion. Independent critic seat weights: market **0.30**, design **0.25**, installer/build **0.25**, procurement/cost **0.20**. No owner selection or procurement release is implied.

## Four-seat board

| Room | Scheme | Market | Design | Build | Cost | Weighted | Challenger margin | Hard gate and decision |
|---|---|---:|---:|---:|---:|---:|---:|---|
| TX-BATH2 | C — v4 Copper/Sandstone with Cortar Clay floor | 3.9 | 3.6 | 3.0 | 3.0 | **3.42** | — | FAIL exact Clay floor wet DCOF; v4 **demoted** |
| TX-BATH2 | B — Copper/Sandstone with PF07 Cream floor | 4.1 | 4.0 | 3.2 | 2.8 | **3.59** | **+0.17** | FAIL exact PF07 floor DCOF; cost critic 2.8 and below +0.25 improvement; **not accepted** |
| TX-BATH3 | A — v4 Emerald/Sandstone with Cortar Grey floor | 3.9 | 3.2 | 2.4 | 2.0 | **2.97** | — | FAIL exact Grey floor DCOF; tub/walk-in contradiction and missing pan; v4 **demoted** |
| TX-BATH3 | B — Emerald/Sandstone with PF05 Ash Grey 12×24 + conditional 2×2 pan | 4.1 | 4.0 | 2.8 | 2.2 | **3.37** | **+0.40** | FAIL exact PF05 field/pan DCOF; build 2.8/cost 2.2; actual shower geometry/pan quantity null; **not accepted** |
| TX-BATH4 | B — v4 Charcoal/Bone Ribbed/Clara niche with Bone Soft floor | 3.7 | 3.0 | 1.8 | 2.4 | **2.79** | — | FAIL Clara wet-niche, Ribbed wet-wall and exact Bone floor DCOF; v4 **demoted** |
| TX-BATH4 | A — flat Charcoal/Soho Black niche with Bone Soft floor | 4.1 | 3.6 | 3.2 | 2.4 | **3.41** | **+0.62** | FAIL exact Bone Soft floor DCOF; cost critic 2.4; **not accepted** |

The +0.25 margin test is **necessary but not sufficient**. TX Bath2 does not reach the margin; TX Bath3 and Bath4 do but still fail mandatory gates and minimum-critic-score test. **All three rooms become `blocked`, with no accepted champion**, while preserving the v4 schemes as historical records and the higher-scoring alternatives as conditional design directions, not approved selections.

## Hard-gate audit and evidence

- Exact floor wet DCOF threshold ≥0.42 is mandatory for every bath floor. Manufacturer product sheets for [Daltile PF07 Cream](https://www.daltile.com/products/concrete-look/portfolio/cream) and [PF05 Ash Grey](https://www.daltile.com/products/concrete-look/portfolio/ash-grey) list **Target DCOF Wet ≥0.42** and appropriate wet-level floor application; **no exact measured value for PF07/PF05 12×24 Matte or PF05 2×2 Matte** was obtained. Target/application suitability does not establish tested SKU performance under this strict board rubric. The carried ELM Cortar Clay, Grey and Bone **Soft** floor variants likewise lack an exact published wet DCOF. Unknown is a **failure**, not an assumption of compliance.
- Wet-wall finish: Tones Copper, Emerald and Sandstone, flat Cortar Charcoal and Soho Black 2×10 have manufacturer Wet Areas listings for their designated tub/shower walls/niches. **Clara Caviar and Cortar Bone Ribbed** do not have product-specific Wet Areas approval for the v4 TX Bath4 wet-zone uses. Optional dry-only Ribbed in the alternate does not itself cause a wet-wall failure and is not a selected extra tile area.
- **TX Bath3:** governing tile takeoff calls a tub alcove; current plumbing lists **walk-in shower, Brizo BT062415-BNX 4-in tile-in square point drain**. True shower pan size, pitch, waterproofing, threshold and main/pan floor quantity split = `null`; the 12×24 field cannot be assumed to form the required four-way point-drain slope. No fixture or layout change is authorized.
- **TX Bath2:** the sink/basin remains **unselected**. Do not create a fixture selection. Copper/Sandstone wall/niche quantities require measured non-overlap. Both proposed floor colors need physical grout and fixture mock-ups.
- Current manufacturer distribution and Chicago showroom existence are **not dated lot or lead commitments**. PF07 and PF05 floor area quoted at public retail **$6.27/SF**, 17.02 SF/carton; 3 cartons = $320.16 per unit as an illustration, not a project supplier quote. TX Bath4 Soho new project quote = `null`; Cortar historical 300-SF import minimum and 10–12-week note are not current guarantees. The owner's per-room material budgets and upgrade stance remain `null`; the >125% budget gate is **unassessable**, not automatically passed or failed.
- Previously carried room takeoffs include **15% waste**. The provisional niche face displaces field tile and must not be added twice; TX Bath3 conditional 2×2 pan area is `null` until a correct model/field measurement. Model document name/path still say **1527 N Wieland**, not the **1529** scope; no live room measurements have been adopted.

## Next fixes

1. **TX Bath2:** procure only information, not goods: verify an exact manufacturer-measured wet DCOF for PF07 or identify a compliant alternate; reconcile Copper/Sandstone recess, wall, tub, threshold and gutter cuts, then obtain project Chicago quote and physical sample. Leave basin owner-unselected.
2. **TX Bath3:** confirm project address and tub/shower scope first; model actual shower perimeter, drain coordinate, slope, full-height wall, level floor/pan tile split and all related quantities. Verify separate exact DCOF values and quote for PF05 12×24 and 2×2 (or documented substitutes).
3. **TX Bath4:** preserve wet-listed flat Charcoal/Soho direction only as conditional. Verify actual niche/wall/cut and Matte White hardware coordination; prove numeric Bone floor DCOF or select a tested alternate, replace wet-use Ribbed/Clara, and quote complete niche/trim/Chicago supply.

Sources: `rooms/TX-BATH{2,3,4}/board/round-002/critic-{market,design,build,cost}.md`, `research/products/`, `research/comps/`, `inputs/`, original room geometry/plumbing, and source-field quote lines in `state/ROOMS.json`. Full machine-auditable scores and gate notes: `state/ROUND002_SCORING.json`.
