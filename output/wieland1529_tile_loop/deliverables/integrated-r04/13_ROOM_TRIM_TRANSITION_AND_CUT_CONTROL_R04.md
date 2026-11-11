# 1529 Wieland | R04 trim, transition, and cut-control schedule

**Status: preliminary coordination only, not a takeoff for ordering.** Source: `13_ROOM_PROVISIONAL_DIMENSIONED_ELEVATIONS.md` and each room's `geometry.json`/`plumbing.json`. Current native Revit documents.list shows **1527 N Wieland**, not a verified 1529 session. Field dimensions, fixture penetrations, glazed openings, tile thickness, trim manufacturer/SKU, finish, 10-ft/8-ft stock lengths, and return/butt conditions are not confirmed. **Approved linear feet = null; order pieces = null.** Existing ELM source SF already includes 15% waste; this edge schedule does not introduce a second SF waste factor.

## Provisional wall extents and edge-count field controls

Widths/heights are in inches, carried directly from the existing preliminary elevation schedule. `n/a` denotes no standalone wall field. Widths are not automatically exposed-edge lengths. One run at a wall's full tiled height is a **possible vertical exposed edge**, not an authorized trim piece.

| Room | Provisional tiled extents | Likely transitions to field-verify | Drain and special cuts | Trim LF/order |
|---|---|---|---|---|
| PH-PRIMARY | W1 70.25 x 111; W2 55.75 x 111 | Shower glass returns, corner tile-to-paint edge, floor/WC threshold | Selected Brizo 48-in linear BR73480/BT0734816-BNX; no niche, no accent addition | null |
| PH-BATH2 | W1 59.50 x 93; W2/W3 30.60 x 93 | Alcove wall ends, tub-flange-to-tile and outer paint returns | Tub, not a fabricated shower pan; Matte White Hansgrohe and Duravit retained; existing Sapphire wet-wall listing PASS | null |
| PH-BATH3 | W1 60.00 x 93; W2/W3 27.96 x 93 | Tub wall ends and deck edges; confirm actual basin/mirror | Source shows tub alcove but Delta DT062412 square point drain; stop for conflict and unselected basin | null |
| PH-BATH4 | W1 60.00 x 111; W2/W3 30.48 x 111 | Walk-in glass/curb, point-drain pan perimeter, niche returns if owner confirms | Brizo BT062415-BNX square drain; 35 SF owner vs 27 SF old source; Soft/Anti-Slip unresolved | null |
| PH-POWDER | W1 50.69 x 111 | Vanity splash to painted return, mirror perimeter only where exposed | Dry Earth Lines relief wall; Luxe Gold wall-faucet alignment | null |
| PH-WC | No independently quoted tile wall | Shared Primary floor threshold/perimeter; verify boundaries | WC floor material INCLUDED in Primary; no duplicate purchase | null |
| TX-PRIMARY | W1 62.25 x 111; W2 57.25 x 111 | Shower glass returns and WC shared-floor threshold | Brizo 48-in linear BT0734816-BNX/BR73480; **no niche**; pan pitch not certified | null |
| TX-BATH2 | W1 62.48 x 93; W2/W3 31.20 x 93 | Tub ends and countertop-to-wall splash transitions | Basin owner-unselected; no fabricated tile opening | null |
| TX-BATH3 | W1 61.20 x 93; W2/W3 31.20 x 93 | Tub ends **or** shower curb, not both | Tub alcove conflicts with Brizo BT062415-BNX square point drain; quantities held pending owner choice | null |
| TX-BATH4 | W1 60.00 x 93; W2/W3 30.48 x 93 | Alcove outside returns, finish-to-paint and niche edges | Clara Caviar wet listing unresolved; do not procure relief finish by inheriting flat approval | null |
| TX-POWDER | W1 35.88 x 111 | Dry feature field-to-paint, mirrored wall-faucet escutcheon | 70/30 Camel/Wheat source quote is **blended**, no independently priced cartons | null |
| TX-POWDER2 | W1 45.67 x 111 | Dry Indigo relief to mirror/splash landing; optional flat insert not selected | Hansgrohe 73072341 is **deck mounted**, sink owner-unselected | null |
| TX-WC | No independently quoted tile wall | Shared Primary floor threshold/perimeter; verify boundaries | WC floor material INCLUDED in Primary; no duplicate purchase | null |

## Edge-length and carton calculation method — pending verified measurements

1. On a correctly identified **1529** as-built or confirmed drawing, record each tiled face as length, height, thickness, open/closed ends and penetrations. Capture door returns, window reveals, shower glass, curb/sill, niche backing and side returns as distinct segments. Avoid adding buried inside-corner legs as exposed trims.
2. For each actually exposed edge, `net exposed LF = sum(measured linear edge lengths in inches) / 12`. Keep separate detail tags for metal profiles, glazed ceramic bullnose, field-to-wood thresholds, glass/curb and movement joints. No length can be authorized solely from the W1–W3 wall widths.
3. `profile sticks = ceil((net exposed LF + cutting allowance LF) / confirmed stock LF)` **by exact trim SKU and finish**. Stock length, cutting allowance and substitutions are presently `null`; 15% tile **area** waste is not the profile allowance.
4. Verify manufacturer tile/caliber/actual thickness against chosen profile reveal, compatible finish, grout width, inside/outside corners, movement sealant, waterproof continuity and tolerances; assign a shop-drawing detail number before purchase.
5. For tile cartons: `cartons = ceil(net required SF including the documented SINGLE allowance / confirmed exact SKU SF-per-carton)`. If the source gross SF already includes 15% waste, use that gross basis directly without adding 15% again; adjust only after surveyed field and niche-face corrections.
6. For pan mosaics: verify level-floor/pan boundary, pan dimensions, plane geometry, drain flange height and the chosen format's **documented wet DCOF**. Manufacturer `Target ≥0.42` is not a measured SKU value; Glazzio HNC6715's reported `>0.50` is a maker lower bound, not an exact test certificate.

## Mandatory elevation legend / detail register

| Detail | Required measured annotation | Current release gate |
|---|---|---|
| E-01 outside tile-to-paint stop | Face, tile thickness, grout, finished profile and each actual exposed edge length | Dimensions/profile null |
| E-02 tub-flange waterproof termination | Tub make/model, flange, backer overlap, membrane continuity, tile setback and sealant | As-built flange null |
| E-03 shower glass / curb / threshold | Opening, slope, finished curb height, glass bracket, transition material and fastening/waterproof detail | Drain/pan/geometry unresolved |
| E-04 niche (non-primary rooms ONLY if retained) | Overall cutout, actual back and return areas, field-face deduction, sill drainage and waterproof return | Niche dimensions/approvals null |
| E-05 linear-drain shower | Verified actual 48-in assembly, slope direction, screen/flange, tile-plane transitions, mosaic/large-format boundary | PH/TX Primary drain placement, exact floor DCOF null |
| E-06 square point-drain shower | Measured 4-plane slope, 2x2 mosaic sheet orientation, frame/flange elevations and curb | PH4 conditional; PH3/TX3 geometry conflicts |
| E-07 tile-to-wood powder/WC threshold | Finished floor build-up, movement joint, threshold height and room boundary | Actual tile elevation/wood thickness null |
| E-08 vanity/splash/mirror | Basin/faucet centerline, mirror limits, outlet/escutcheon cuts, relief backing flatness | Three owner-unselected basins and measured elevations null |

**Procurement release:** no exposed-edge LF, trim sticks, tile cartons, niche extensions, attic stock or supplier ETA are approved from this preliminary register. Only carry product-specific sourced carton values as references; release quantities follow valid 1529 identity, measured dimensions, owner decisions, specific wet/DCOF approvals, current quote and signed finish schedule.
