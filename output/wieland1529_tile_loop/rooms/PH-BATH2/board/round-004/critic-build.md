# Round 004 | PH-BATH2 | Independent critic-build

**Seat:** Tile installer / GC (weight **0.25**). Exactly five **integer 1–5** criterion scores per candidate; **overall seat score is their arithmetic mean to one decimal**. Sources: [round's blind packets](candidates/), [geometry](../../geometry.json), [current plumbing](../../plumbing.json), [board gates](../../../../board/BOARD.md), linked manufacturer records. The prior-drawing tub alcove has **4.958-ft (59.496-in.) rear W1**, two **2.55-ft (30.60-in.) returns**, assumed **7.75-ft (93-in.) tiled height from tub rim**, **35-SF** bathroom floor; nothing has been surveyed/verified in the 1529 Revit model. [Plumbing](../../plumbing.json) carries the **Duravit Starck 59-in built-in tub 700332000000090** and **Hansgrohe Matte White** Ecostat, Rainfinity, spout, Vivenis fittings. **No shower-floor pan is scheduled**; bath **level floor DCOF remains mandatory**.

## Candidate A — Sapphire wet tub walls, Sandstone niche, Cortar Grey floor

| Exactly five installer/GC criteria | Score (1–5) | Evidence and constructability reason |
|---|---:|---|
| **1. Product wet listing / waterproofing** | **4** | The [individual ELM Sapphire 2×20 Glossy page](https://www.elmsurfaces.com/product/sapphire-tones) **explicitly lists Wet Areas**; [Sandstone niche](https://www.elmsurfaces.com/product/sandstone-tones) also does. Tub-flange membrane continuity, control penetrations and niche waterproofing still need a measured section ([Sapphire evidence](../../../../research/products/elm-tones-sapphire-2x20-wet-approved.md); [candidate A](candidates/A.md)). |
| **2. Cuts / layout** | **3** | On [W1 59.496 in and returns 30.60 in](../../geometry.json), full nominal 20-in. sticks must be balanced around actual grout joints (not automatically assume three exact 20-in. pieces fit W1); 93-in. course height, valve/arm holes and niche edges are unmeasured ([candidate A](candidates/A.md)). |
| **3. Pan / geometry / plumbing** | **4** | A [Duravit 59-in built-in tub](../../plumbing.json) is coherent with the [tub-alcove geometry](../../geometry.json), and there is **no separate tile shower pan or sloped tile-to-point-drain design** to prove; real tub rim, overflow, apron, door clearance and tile terminations remain conditional. |
| **4. Tile substrate / installation** | **3** | Tub wall backer/membrane, movement sealants at changes of plane, pitched niche sill and trim profiles are unspecified; the [Cortar Grey Soft 12×24](candidates/A.md) level floor can be laid in zero-offset modules after actual substrate flatness, edge thickness and threshold checks. |
| **5. Documented manufacturer approvals** | **2** | **Sapphire Wet Areas PASS** is established by the [product-specific maker record](../../../../research/products/elm-tones-sapphire-2x20-wet-approved.md), not merely a collection claim; **Sandstone niche Wet Areas PASS**, but the **exact published measured wet DCOF ≥0.42 for Cortar Grey 12×24 Soft is `null`**, thus floor FAIL ([candidate A](candidates/A.md); [board gate 2](../../../../board/BOARD.md)). |

**Overall seat mean: (4+3+4+3+2)/5 = 3.2/5.0.**

**top_fix:** Obtain a **maker-published exact wet DCOF ≥0.42 for Cortar Grey 12×24 Soft**, or specify a separately tested compliant **level** bathroom floor without altering the manufacturer-approved Sapphire/Sandstone tub wall scheme.

**gate_flags:**
- **PASS — SAPPHIRE_WET_WALL:** The individual manufacturer [Sapphire page](https://www.elmsurfaces.com/product/sapphire-tones) explicitly includes **Wet Areas** for **Tones Sapphire 2×20 Glossy**; do **not** mark Sapphire wet-wall unapproved ([source audit](../../../../research/products/elm-tones-sapphire-2x20-wet-approved.md)). [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) also Wet Areas-listed for niche.
- **FAIL — BATH_FLOOR_EXACT_DCOF:** [Cortar Grey 12×24 Soft floor](candidates/A.md) has **no verified maker-published exact measured wet DCOF ≥0.42**. Floor application or a historical supplier quote does not pass the numerical [board gate](../../../../board/BOARD.md).
- **N/A — SHOWER_PAN:** Tub assembly with 59-in Duravit; [candidate A](candidates/A.md) does **not** propose a tiled shower pan. Do not invent a pan SF or separate shower-pan DCOF failure.
- **HOLD — FIELD_DIMENSIONS / NETTING:** W1/returns, actual niche back/returns, tub rim/valve locations and membrane details are unverified; original **89.7 SF wet-field +3.67 SF niche** are **gross and already 15%-waste-adjusted**, and the recessed niche's overlap must be audited rather than silently added or fully deducted ([candidate A](candidates/A.md); [geometry](../../geometry.json)).
- **OPEN — SUPPLY / BUDGET:** [Candidate A](candidates/A.md) carries dated ELM prices, not current Chicago lot/ETA. The [owner feedback](../../../../state/OWNER_FEEDBACK.md) gives **no room cap**; no >125% budget failure can be declared. [Hansgrohe arm 04186703](../../plumbing.json) has a **channel-specific possible discontinuation note** for fixture coordination, not proof of discontinued **tile**.

**confidence:** **medium** on individual wet-wall approval; **low** on floor DCOF, cuts and takeoff until verified; overall **medium**.

## Candidate B — Copper/Sandstone wet walls, PF05 Ash Grey level floor

| Exactly five installer/GC criteria | Score (1–5) | Evidence and constructability reason |
|---|---:|---|
| **1. Product wet listing / waterproofing** | **4** | [Tones Copper 2×20 Glossy](https://www.elmsurfaces.com/product/copper-tones) is recorded **Wet Areas YES** in the [project product audit](../../../../research/products/elm-tones-copper-2x20.md), and [Sandstone](https://www.elmsurfaces.com/product/sandstone-tones) niche has individual Wet Areas listing; tub flange, membrane and sill still require detailing ([candidate B](candidates/B.md)). |
| **2. Cuts / layout** | **3** | [Candidate B](candidates/B.md) proposes **vertical zero-offset 20-in. sticks** through a nominal **93-in. tiled height** (four 20-in. lengths plus remainder before joints); balance height starts and cuts to matte-white controls and verify 59.496-in. back / 30.60-in. returns to avoid focal slivers ([geometry](../../geometry.json)). |
| **3. Pan / geometry / plumbing** | **4** | The specified [Duravit built-in tub + Hansgrohe Matte White](../../plumbing.json) matches the [tub-alcove room classification](../../geometry.json); no sloped tile shower pan is added, although tub rim, door opening and actual niche position are not surveyed ([candidate B](candidates/B.md)). |
| **4. Tile substrate / installation** | **3** | [PF05 Ash Grey 12×24 Matte](../../../../research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md) proposes a feasible zero-offset **level** floor with maker-recommended trial **1/8-in joints**; water-rated tub backer, resilient corner sealants, threshold elevation and niche edge/trim remain unverified ([candidate B](candidates/B.md)). |
| **5. Documented manufacturer approvals** | **2** | Copper/Sandstone wall wet listings are documented at maker/project-audit level, but [Daltile PF05 12×24 Matte](https://www.daltile.com/products/concrete-look/portfolio/ash-grey) publishes **Wet & Level Interior Floor suitable / Target Wet DCOF ≥0.42**, **NOT an actual measured exact PF05 SKU wet DCOF**, so the strict floor gate fails ([PF05 evidence](../../../../research/products/daltile-portfolio-ash-grey-pf05-12x24-matte.md)). |

**Overall seat mean: (4+3+4+3+2)/5 = 3.2/5.0.**

**top_fix:** Obtain the **published measured wet DCOF for exact PF05 Ash Grey 12×24 Matte** from the manufacturer, or change the proposed bath floor to a test-verified wet-level product.

**gate_flags:**
- **PASS — WET_WALL_PRODUCT_USE:** Maker/project audit records [Copper](../../../../research/products/elm-tones-copper-2x20.md) **Wet Areas YES**; the [Sandstone niche](https://www.elmsurfaces.com/product/sandstone-tones) also qualifies for the wet tub surround. Preserve their actual individual product/finish documentation before release.
- **FAIL — BATH_FLOOR_EXACT_DCOF:** [Daltile Portfolio Ash Grey PF05 12×24](https://www.daltile.com/products/concrete-look/portfolio/ash-grey) maker **Target DCOF ≥0.42** is an **application target**, not a **measured exact PF05 12×24 Matte** value; measured DCOF and test report `null`, [gate 2](../../../../board/BOARD.md) FAIL.
- **N/A — SHOWER_PAN:** [Candidate B](candidates/B.md) retains the 59-in Duravit tub. No separate shower-pan tile or pan takeoff is authorized.
- **HOLD — SOURCE_GEOMETRY / NICHE_NETTING:** The **89.7-SF gross field** and **3.67-SF gross niche** each already include 15% waste; B's provisional 86.03/3.67 split is only a **field-overlap assumption**, not a surveyed recess quantity. Verify W1/returns, 20-in vertical cutting, niche returns/sill, tub flange and trim location ([candidate B](candidates/B.md); [geometry](../../geometry.json)).
- **OPEN — QUOTE / AVAILABILITY / BUDGET:** [Copper's $6.95/SF](../../../../research/products/elm-tones-copper-2x20.md) is from another **same-project** room, **not a refreshed PH-BATH2 quote**; PF05 project rate, carton/Chicago inventory/arrival and owner room budget `null`. No unsupported 125% budget or tile discontinuation failure ([candidate B](candidates/B.md); [owner feedback](../../../../state/OWNER_FEEDBACK.md)).

**confidence:** **medium** on wet-wall use and tub geometry classification; **low** on measured PF05 floor performance and 1529 cut data; overall **medium**.
