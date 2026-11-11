# PH-BATH4 — Round 001 — critic-cost (procurement, weight 0.20)

**Basis:** Two Penthouse copies (311A and 311B). All wall **107.2 SF/unit**, floor **40.2 SF/unit** and niche **8.63 SF/unit** quantities are **gross with 15% waste included**, from the previous tile takeoff; no extra 15% has been applied here. Geometry lists a provisional 10.08 LF × 9.25 ft wet-wall run (≈93.24 net SF, ≈107.2 gross SF), and **35 SF owner floor area vs 27 SF prior Revit**, still unresolved. ELM quote lineage is 2026-09-03 and the Smartsheet rows cited below; these are neither current inventory confirmations nor fully loaded installed prices. No carried room budget/owner upgrade allowance is stated in `state/OWNER_FEEDBACK.md`; the **125% budget gate is not actionable**.

## Candidate A — Cortar Bone Ribbed / Charcoal Anti-Slip / Clara Caviar

| Procurement criterion | 1–5 | Evidence-based reason |
|---|---:|---|
| Rate and quote lineage | 2 | Ribbed **$7.37/SF** (Smartsheet **6976633752321924**) and Clara **$33.70/SF** (**6092702458445700**) are identifiable; vendor quote total reportedly omitted the two-unit **214.4 SF Ribbed** quantity, and the **$6.75/SF** floor row **1347134218108804** prices **Soft**, not specified Anti-Slip (`candidates/A.md`, lines 5–15; `research/products/elm-cortar-bone-flat-24x48.md`, line 14). |
| Extended material economics | 2 | **$1,352.24/unit** at carried rates; the 8.63 SF niche alone is **$290.83/unit** (≈21.5% of nominal tile cost), while exact required floor-finish pricing is unconfirmed (`candidates/A.md`, lines 9–15). |
| Measured quantity / 15% waste | 3 | The approximate wet-wall calculation reproduces 107.2 SF including waste, but niche displacement, shower pan floor coverage, opening deductions and the 35/27 SF area discrepancy remain unmeasured (`geometry.json`; `candidates/A.md`, line 15). |
| Distribution, stock and lead | 2 | Cortar Bone Ribbed remains manufacturer-listed, but specific project stock, Ribbed order inclusion, Clara lot and actual lead dates are not confirmed (<https://www.elmsurfaces.com/product/bone-ribbed-cortar>, `candidates/A.md`, line 19). |
| Trim, setting, labor and freight | 2 | Ribbed 24×48 walls and a zellige niche require priced specialty installation/termination and waterproofing, all absent; floor anti-slip rate and labor remain open (`candidates/A.md`, lines 13–19). |

**Extended material check (15% waste included):** Ribbed walls **107.2 × $7.37 = $790.06/unit**; Charcoal floor **40.2 × $6.75 Soft-price reference = $271.35/unit** (**not a confirmed Anti-Slip price**); Clara Caviar niche **8.63 × $33.70 = $290.83/unit**. **Indicative $1,352.24/unit, $2,704.49 for two units**, before finish correction, niche-field deduction, box rounding, freight, tax, trim, setting or labor. The Ribbed wall value for two units is **$1,580.13** at the referenced rate, but the vendor's carried total must be reconciled because it reportedly excluded that quantity.

**seat_score: 2.2 / 5.0** (unweighted mean of the five criteria above).

**top_fix:** Obtain ELM's corrected two-unit vendor quote explicitly including **214.4 SF Ribbed**, the exact **12×24 Charcoal Anti-Slip** SKU/rate and niche quantity, together with box counts, delivery and an installation allowance.

**gate_flags:**
- **FAIL — BONE_RIBBED_WET_WALL:** Individual ELM Bone Ribbed product lists **Walls / Back Splashes** and lacks **Wet Areas** (<https://www.elmsurfaces.com/product/bone-ribbed-cortar>, checked 2026-11-06; `board/BOARD.md`, gate 1).
- **FAIL — CLARA_NICHE_WET_WALL:** Clara Tierra Madre Caviar wet-wall approval is missing in the cited manufacturer audit; niche is in shower (`candidates/A.md`, lines 10 and 19).
- **FAIL — FLOOR_DCOF_UNKNOWN:** No published ≥0.42 wet DCOF for the **specified Anti-Slip** Charcoal bath/shower-floor finish; the current Soft quote cannot prove the performance or rate (<https://www.elmsurfaces.com/product/cortar-charcoal>, `candidates/A.md`, lines 9 and 19). The 12×24 point-drain slope remains a geometry verification issue.
- **NOT A FAIL — BUDGET_UNTESTABLE:** The room budget is not allocated; nominal cost alone cannot establish a >125% breach.

**confidence: low** — line prices are carried, but floor finish, wet approvals, actual vendor inclusion, inventory and installation costs are not verified.

## Candidate B — Cortar Bone flat / Charcoal Anti-Slip / Soho Black

| Procurement criterion | 1–5 | Evidence-based reason |
|---|---:|---|
| Rate and quote lineage | 2 | Flat Bone **$8.14/SF** derives from a **different same-project PH Primary row 4302621473570692**, not a PH-BATH4 revised quote; Charcoal Anti-Slip has only a **Soft** price reference; Soho Black rate is **null** (`candidates/B.md`, lines 7–9; `research/products/elm-soho-black-2x10.md`, lines 10–14). |
| Extended material economics | 2 | **$1,143.96/unit + unpriced Soho niche + Anti-Slip upcharge (if any)** at historic flat-wall and Soft-floor reference rates; no defensible complete material total or comparison to the $1,352.24 A allowance yet (`candidates/B.md`, line 18). |
| Measured quantity / 15% waste | 3 | **107.2 SF gross walls** is consistent with 10.08 LF × 9.25 ft × 1.15; the 8.63 SF niche is provisional and must displace field SF, and box rounding/floor coverage are unresolved (`geometry.json`, `research/products/elm-soho-black-2x10.md`, line 14). |
| Distribution, stock and lead | 1 | Flat Bone's 2026-09-03 quote records **10–12 weeks, 50% deposit, 300 SF import minimum**; two-room wall need is **214.4 SF, 85.6 SF below minimum**. Soho current project stock/lead unknown (`research/products/elm-cortar-bone-flat-24x48.md`, lines 13–15; <https://www.elmsurfaces.com/product/soho-black>). |
| Trim, setting, labor and freight | 2 | New 24×48 wall setting/termination, black niche edge, waterproofed returns and floor-point-drain detailing lack labor, trim, mortar, grout and freight pricing (`candidates/B.md`, lines 14–20). |

**Extended material check (15% waste included):** Flat wall **107.2 × $8.14 = $872.61/unit** (**+$82.54/unit** vs Ribbed at $7.37); Charcoal floor **40.2 × $6.75 Soft-only reference = $271.35/unit**; Soho niche **8.63 SF × $null/SF = unpriced**. Thus the **partial illustrated subtotal is $1,143.96/unit excluding Soho and any corrected Anti-Slip floor price**, not a complete bid. The two-unit flat wall gross need **214.4 SF** would nominally require **14 × 15.39 SF cartons** (215.46 SF). **Conditional only:** if ELM enforces its historic 300 SF flat Bone *per-SKU import minimum* with no project-wide consolidation, at least **20 cartons = 307.80 SF**, **$2,505.49 at $8.14/SF**, versus **$1,745.22** for the nominal 214.4 SF: a potential **$760.27 incremental wall purchase** across two units. Confirm whether existing PH Primary Bone demand can meet/pool the minimum; never treat this conditional cost as an approved PO.

**seat_score: 2.0 / 5.0** (unweighted mean of the five criteria above).

**top_fix:** Get one current consolidated ELM PH-BATH4 quote for **Bone flat + Charcoal Anti-Slip + Soho Black**, explicitly resolving the **300 SF minimum**, box rounding, measured niche-field deduction, stock, freight and installed trims.

**gate_flags:**
- **FAIL — FLOOR_DCOF_UNKNOWN:** The manufacturer's Cortar Charcoal page lists Anti-Slip and Wet Areas but does **not publish a numeric DCOF ≥0.42** in the reviewed evidence. Wet bath and shower floors fail this board requirement until a manufacturer document supplies it (<https://www.elmsurfaces.com/product/cortar-charcoal>, `board/BOARD.md`, gate 2). The 12×24 point-drain slope must also be proven before approval.
- **WET-WALL PASS IN SCOPE:** Flat Bone and Soho Black individual product pages expressly list Wet Areas (<https://www.elmsurfaces.com/product/cortar-bone>, <https://www.elmsurfaces.com/product/soho-black>, checked 2026-11-06); this does not resolve the floor gate.
- **NOT A FAIL — BUDGET_UNTESTABLE:** No actual carried room budget, no 125% breach determination.

**confidence: low** — manufacturer wall suitability is strong, but one niche price, the correct floor price, live availability and enforceability of the import minimum are unknown.
