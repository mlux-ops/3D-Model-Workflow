# 1529 Wieland — Round 003 Triplex Board Submission

**2026-11-06 · Phase 2-board, scoring deferred to next turn.**

**Dispatch confirmation:** Independent non-Pro Reviewer rechecked all three previously identified FIX categories and issued **DONE**; reverified six neutral candidate documents and final SHA hashes in `state/ROUND003_SUBMISSION.json`. Four existing specialist critics (market, design, build, cost) were then messaged with strict per-room blind evidence restrictions and commissioned to write exactly 12 independent critique files. No score or acceptance is recorded here.

Three-room batch: **TX-PRIMARY (202A/202B), TX-POWDER (102A/102B), TX-POWDER2 (009A/009B)**. Two neutral and source-backed material/layout candidates per room; per-unit quantities represent the two Triplex dwellings. Comp baseline remains Old Town prioritized, 14 dated listings from nine building groups spanning roughly $2.4M–$3.2M and a TX sale target of $2.7M. Adjacent Lincoln Park and Gold Coast are secondary, and no actual comp tile photographs have been authenticated.

## Blind material comparison

| Room | Candidate files for reviewers | Design alternatives, not approved outcomes | Hard-gate and owner-input status |
|---|---|---|---|
| TX Primary | `rooms/TX-PRIMARY/board/round-003/candidates/A.md`, `B.md` | Cortar Clay 24×48 flat/Ribbed and historical blended Soft/Anti-Slip floor vs wet-listed flat Clay + Daltile Portfolio Cream PF07 12×24 field and 2×2 mosaic linear-drain pan | Clay Ribbed lacks wet-wall listing in wet shower; PF07 manufacturer only publishes target wet DCOF ≥0.42, **not an exact measured SKU result**; no approved numeric floor test, drain/slope, live geometry or project quote |
| TX Powder | `rooms/TX-POWDER/board/round-003/candidates/B.md`, `C.md` | Haze Camel/Wheat dry vanity-wall color mix with alternative intentional **70:30** Camel-dominant distribution and faucet/grout/edge arrangement | Both wall-only dry powder scope; **wood floor**, no wet-floor DCOF gate. Exact ratio, physical sample, faucet rough/escutcheon alignment, current Chicago lot, combined vs separate carton allocation pending |
| TX Powder 2 | `rooms/TX-POWDER2/board/round-003/candidates/A.md`, `B.md` | Vera Forma Indigo Edge 6×6 relief dry vanity wall versus an Indigo field with a coordinated flat mounting/backsplash landing inside the same net wall | **Wood floor**, no wet-floor gate. Hansgrohe Tecturis E 73072341 is **deck-mounted**, not wall-mounted; basin **unselected**, landing area/rate and dimensions `null`. No assumed fixture approval |

Role mapping is deliberately not revealed in this specialist submission document; private `_key.json` files are excluded from critic read paths. Before dispatch, `scratch/verify_round003.py` confirmed **six** matching candidate filenames and headings, a five-column specification/gate table in every packet, no explicit champion/challenger disclosures, no scores, correct active room-state status and comparable quotation/evidence treatment. Exact file hashes are retained in `state/ROUND003_SUBMISSION.json`.

## Historical quote and geometry evidence

- TX Primary: **134.4 SF** wall/shower-ceiling gross at **$8.14/SF = $1,094.02/unit** plus **116.1 SF** blended level floor / pan / TX WC allowance at **$905.58/unit**, historic tile-only subtotal **$1,999.60/unit**. Area contains 15% waste; original pan 28.46 SF gross is within the floor line. The historical primary niche row (8.63 SF, no SKU) is **explicitly excluded**, not a new proposed item. Brizo **BR73480 48-in linear drain rough** remains selected; verified slope and location missing.
- **Floor sub-line cost discrepancy:** the older 116.1-SF blended floor line reports **$905.58** at average $7.80/SF. Candidate B's illustrative decomposition 87.64 SF × $8.14/SF (about $713.39) plus 28.46 SF × $6.75/SF (about $192.11) totals **$905.50** at individually rounded lines—**$0.08 below** the carried extended value. These are two different historical quote representations, not a verified manufacturer rebid. Keep **$905.58** as the carried row and treat the exact sub-line cost as **unresolved** until a source-matched supplier schedule is available; do not invent a price reduction.
- TX Powder: **31.8 SF gross/unit** of Haze Camel/Wheat at **$11.93/SF = $379.37/unit**, dry vanity-only. The proposed 70/30 division remains in that total with 15% waste already embedded. A prior PH Earth Lines $8.20/SF price is an alternative **proxy**, not a refreshed TX quote.
- TX Powder2: **40.5 SF gross/unit** of Indigo Edge at **$8.20/SF = $332.10/unit**, dry vanity-only, with 15% waste already embedded. Smooth mounting-zone SF/price remain **null** until sink/mirror elevations are verified, and any approved panel must displace rather than add tile.

All rates originate from the **2026-09-03 ELM quote** carried in the read-only Smartsheet snapshot, not new supplier commitments. Chicago manufacturer/showroom presence does not establish available cartons, lead, freight or landed price. An actual approved room material budget is absent, so the 125% budget gate remains unassessable.

## What reviewers must do

Each of the four persisted critics (market 0.30, design 0.25, installer/build 0.25, procurement/cost 0.20) independently reads **only** that room's two current Round003 candidate files and its geometry/plumbing, shared research and maker evidence. No private key, current champion, prior rounds, ledger, other rooms' candidate files, emails or external contacts. Score every criterion 1–5, a one-decimal seat total, `top_fix`, `gate_flags`, `confidence`, specific manufacturer/quote/comp evidence; write exactly one `critic-{market,design,build,cost}.md` per room.

**Board cadence:** Score the six candidates **only in the next turn**, after all twelve critique files are present and the independent non-Pro Reviewer has cleared any presentation or factual FIX. No Revit/Smartsheet writes, DirectShapes, emails, forms, vendor contact, sample orders or purchases are authorized.
