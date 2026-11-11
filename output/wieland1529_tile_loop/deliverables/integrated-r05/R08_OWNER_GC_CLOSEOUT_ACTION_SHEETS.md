# R08 | 13-room owner / GC evidence closeout and release-dependency register

**This is an operational checklist, not an approval or permit document.** Built from actual 13-room scored register, 27 historical ELM quote rows and manufacturer R05–R07 evidence. No available owner signatures, exact wet DCOF values, real Chicago inventory or native 1529 model measurements were invented. The companion machine-readable file is `R08_ROOM_EVIDENCE_CLOSEOUT_TRACKER.csv`.

## Required decision route by room

| Room | Historical tile-only $/unit | Board status | First non-inferable decision | Mandatory technical evidence before release |
|---|---:|---|---|---|
| PH-PRIMARY | $2224.41 | blocked | approve wall/field/pan palette only after testing; no niche | PF07 12x24 Target only, exact test null; PF07 2x2 Target only; linear-drain approval blank in Portfolio maker sheet; verified 1529 dimensions; actual supplier/budget signoff |
| PH-BATH2 | $920.28 | blocked | sample Sapphire vs Copper option (no required wet-fix) | Cortar Grey Soft/PF05 exact wet DCOF null; N/A retained Duravit tub; verified 1529 dimensions; actual supplier/budget signoff |
| PH-BATH3 | $930.42 | blocked | select basin and resolve tub versus selected Delta square point drain | Bone Soft/PF07 floor exact wet DCOF null; null unless shower elected; tub source is NOT pan evidence; verified 1529 dimensions; actual supplier/budget signoff |
| PH-BATH4 | $1352.24 | blocked | resolve 35 vs 27 SF and Soft vs Anti-Slip owner/source interpretation | Charcoal Soft quote vs Anti-Slip spec; PF09 field DCOF null; PF09 2x2 point-drain DCOF null, provisional 14.6 gross SF not approved; verified 1529 dimensions; actual supplier/budget signoff |
| PH-POWDER | $368.18 | active | confirm Earth Lines dry feature/metal grout/mirror | N/A historic wood floor; N/A; verified 1529 dimensions; actual supplier/budget signoff |
| PH-WC | $0.00 | seeded | confirm threshold and adopt qualified Primary level finish only | Included in PH Primary quoted floor; inherits level DCOF clearance; N/A; verified 1529 dimensions; actual supplier/budget signoff |
| TX-PRIMARY | $1999.60 | blocked | approve flat Clay field and alternate pan palette only after tested acceptance | Original mixed Soft/Anti-Slip; PF07 12x24 exact wet test null; PF07 2x2 exact DCOF null AND Portfolio linear drain suitability blank; Prime RL alternative only research; verified 1529 dimensions; actual supplier/budget signoff |
| TX-BATH2 | $999.92 | blocked | select basin and approve wet wall palette | Cortar Clay Soft/PF07 exact DCOF null; N/A retained tub; verified 1529 dimensions; actual supplier/budget signoff |
| TX-BATH3 | $958.88 | blocked | DECIDE tub versus walk-in with Brizo point drain | Grey Soft/PF05 exact DCOF null; null, DO NOT infer pan SF from tub alcove; verified 1529 dimensions; actual supplier/budget signoff |
| TX-BATH4 | $1320.82 | blocked | approve exact Charcoal/Soho wet wall/niche arrangement after samples | Cortar Bone Soft exact wet DCOF null; N/A retained tub source; verified 1529 dimensions; actual supplier/budget signoff |
| TX-POWDER | $379.37 | active | accept/revise board-selected 70% Camel/30% Wheat Haze | N/A wood floor; N/A; verified 1529 dimensions; actual supplier/budget signoff |
| TX-POWDER2 | $332.10 | active | select basin and verify deck-faucet landing | N/A wood floor; N/A; verified 1529 dimensions; actual supplier/budget signoff |
| TX-WC | $0.00 | seeded | approve primary-level threshold/finish only | Included in TX Primary floor line; numeric DCOF follows Primary; N/A; verified 1529 dimensions; actual supplier/budget signoff |

## Evidence owner vs technical reviewer (roles, not invented named people)

**OWNER ONLY:** approves/rejects proposed finishes and exact sinks; TX Bath3 tub vs walk-in; PH Bath4 35 vs 27 area interpretation, per-room material allowances and any upgrades. No assistant selects these.
**ARCHITECT/DESIGNER:** verifies an actual 1529-model document title/path/session plus field survey, selected actual drain/fixture locations, shower area and pan/level boundaries, niche face deduction and 24x48 or 2x20 cut plans, glass/curb/threshold/finish decisions, owner palette signoff. Current 1527 Revit session is not 1529 proof.
**GC/TILE INSTALLER:** validates compatible specified membrane/backer/drain flange and warranty, actual substrate flatness, point/linear pitch plane feasibility, finished field/pan elevations (Portfolio 2x2 glazed ceramic 1/4in vs 12x24 porcelain 5/16in), grout/movement, exposed trim LF and stick dimensions, physical mock-up. Approval cannot come from conceptual W1–W3 sizes.
**MANUFACTURER / TECHNICAL REPORT (future authorized channel only):** full product code/color/size/finish wet wall approval, each floor and pan measured test result with actual test method/date/certificate. PF07 linear drain maker sheet has no suitable mark; Prime RL20/21/23 maker brochure does mark mosaic linear use but has conflicting old/new targets ≥0.60/≥0.42 and no exact measured point.
**PROCUREMENT / ESTIMATOR (future authorized channel only):** dated exact-SKU Chicago stock/lot and delivery, cartons/shade/freight/trim/setting/labor current quotation, comparative historic vs new scope, owner cap and 125% check. Historical ELM four-dwelling tile-only source $23,572.44 cannot serve as current installed budget. No vendor contact performed.

## Priority closeout sequence (no implied approvals)

1. **Owner geometry/program:** actual project identity; PH Bath3 tub/Delta point-drain plus unselected basin; TX Bath3 tub vs walk-in; PH Bath4 35/27-SF and quoted Soft vs intended Anti-Slip, plus three basins (PH3, TX2, TX Powder2).
2. **Technical wet listing:** Clara Caviar 2x8 niche, Tones Opal, Bone/Clay relief finishes product-specific wet use; maintain Sapphire 2x20 Glossy confirmed wet tub wall PASS. Flat alternate approval never transfers to relief.
3. **Exact wet-floor and pan reports:** original ELM floors, PF07/PF05/PF09 12x24 fields and 2x2 pans, conditional maker listed RL20/21/23 linear options and Glazzio inequality/version research. Manufacturer Target is not measured exact result.
4. **Measured shop details and quantities:** preserve single original source 15% waste, share WC with Primary floor, no primary shower niches, avoid duplicate niche back/face. Determine field/pan split and then profile LF and per-SKU cartons.
5. **Source pricing and release:** separate 2026-09-03 original ELM amounts, online retail examples, qualified exact-SKU dated supplier bids, current Chicago availability, room material cap and signed owner schedule. `release_allowed=false` for every room until verifiable specific evidence and decisions exist.

## Validation and archive rules

The CSV is a status control and never substitutes for a signed product submittal. Every unresolved item intentionally remains `null`, FALSE, HOLD or N/A rather than an invented count, cost, test or decision. Full source trace: `state/ROOMS.json`, `state/ROUND004_SCORING.json`, R05/R06/R07 manufacturer research, original v4 source and `SURFACE_TAKEOFF_13_ROOMS.csv`. Updating any release_allowed flag requires a new document receipt, corresponding review and owner/technical authorization.
