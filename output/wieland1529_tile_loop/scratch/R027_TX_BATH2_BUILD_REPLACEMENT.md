# TX-BATH2 — R027 independent BUILD critique (replacement)

Scope: installer / general-contractor buildability review of neutral candidates A and B. Source room geometry remains drawing-derived / assumed, not live-Revit or field verified. Both candidates retain the Duravit Starck tub, Hansgrohe Chrome, basin UNSELECTED, and NO tiled shower pan.

## Candidate A

| Build criterion | Score / 5 | Evidence and reason |
|---|---:|---|
| Substrate and flatness demand | 4.0 | The 24x24 Floor & Decor Luxe Sand Matte is 8 mm rectified and a moderate large-format panel; it still requires a flat substrate, but is less sensitive to local plane variation than a 24x48 panel. Exact product page: https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html; R022 evidence, lines 5 and 9. |
| Lippage and joint control | 4.0 | Rectified 23.70x23.70 actual size permits a consistent 1/8-in proposed joint; verify tile-to-tile caliber and substrate plane before setting. The seller lists 1/16, 1/8 and 3/16 joint options (R022, line 5). |
| Floor layout and perimeter cuts | 4.0 | 38 SF prior floor area with 43.70 SF gross (15% already included) is a practical square-format takeoff; 24-in modules give more opportunities to balance cuts around the tub and entry than B's 24x48. Actual entry/tub offsets and focal cuts are unknown (geometry.json, floor_area and tiled-wall records; candidate A, line 13). |
| Wet-zone and drain interface | 5.0 | This is a tub alcove with no tiled shower pan; linear and point pans are explicitly N/A. The exact Luxe Sand item is listed for bathroom floors and shower floors with published wet DCOF >=0.42, so the proposed bath floor clears its applicable floor gate (R022, lines 5 and 9; R027_TX_BATH2_BLIND_PRODUCT_EVIDENCE, line 13). |
| Edges, transitions and niche execution | 3.5 | The 2x20 Copper wall and Sandstone niche products are individually Wet Areas wall-listed, but trim, return terminations, grout specification and niche opening remain unmeasured / unselected. Candidate A, lines 6-7 and 14; product evidence for Copper and Sandstone. |
| Quantity, cartons and sequencing | 4.0 | Floor gross is 43.70 SF, already including 15% waste once. At 15.52 SF/box, three full boxes yield 46.56 SF; this leaves modest cutting reserve. F&D public price is $3.49/SF, non-Chicago, with local stock and delivery unknown (R022, line 5; candidate A, lines 8 and 12). |

**Arithmetic mean:** (4.0 + 4.0 + 4.0 + 5.0 + 3.5 + 4.0) / 6 = **4.1 / 5**.

**top_fix:** Obtain a field-verified floor plan and tub/door offsets, then produce a dry layout proving balanced perimeter cuts and no visible slivers before setting.

**gate_flags:** `geometry_verification_pending` — live Revit IDs, entry/tub offsets, wall openings, actual niche dimensions and field plane are absent; the assumed drawing geometry cannot prove cut feasibility. Wet-wall listing: PASS for Copper and Sandstone. Floor wet-use / DCOF: PASS for exact Luxe Sand 101317949. Shower-pan gate: N/A (tub; no tiled pan). Availability / Chicago lot: UNKNOWN, not a confirmed failure.

**confidence:** medium-low — product application and nominal takeoff evidence are clear; field geometry and local supply remain unverified.

## Candidate B

| Build criterion | Score / 5 | Evidence and reason |
|---|---:|---|
| Substrate and flatness demand | 3.0 | The 23.58x47.28 actual 24x48 Riviera Oat is 8 mm rectified; its longer span is more sensitive to substrate waviness and requires tighter plane preparation than A. Exact product page: https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html; R022, lines 7 and 9. |
| Lippage and joint control | 3.0 | Long 24x48 panels need careful handling, consistent bedding and lippage control. The seller lists 1/16, 1/8 and 3/16 joints; the proposed 1/8-in joint is reasonable but does not remove the need to check the substrate and panel bow (R022, line 7). |
| Floor layout and perimeter cuts | 3.0 | The 38 SF prior floor area is small relative to a 24x48 module; with only drawing-derived room dimensions and unknown door/tub offsets, a long-panel layout may create narrow perimeter cuts. No actual cut map can be confirmed from geometry.json (candidate B, line 13). |
| Wet-zone and drain interface | 5.0 | The room is a tub alcove, so no tiled shower pan or drain-slope layout is required. The exact Riviera Oat 101487775 item is listed for bathroom and shower floors with published wet DCOF >=0.42; the applicable bath-floor gate passes (R022, lines 7 and 9; R027_TX_BATH2_BLIND_PRODUCT_EVIDENCE, line 14). |
| Edges, transitions and niche execution | 3.5 | Wet wall and niche details are identical to A: 2x20 Copper and Sandstone are wet-wall listed, but trim, return terminations, grout, niche size and opening are unresolved. Candidate B, lines 6-7 and 14; product evidence for Copper and Sandstone. |
| Quantity, cartons and sequencing | 3.5 | Floor gross is 43.70 SF including the original 15% waste once. Three 16-SF cartons provide 48 SF; workable, but B has a larger per-panel handling and breakage exposure. Public observed price is $3.99-$4.39/SF, non-Chicago and not a local quote; current lot and ETA are unknown (R022, line 7; candidate B, lines 8 and 12). |

**Arithmetic mean:** (3.0 + 3.0 + 3.0 + 5.0 + 3.5 + 3.5) / 6 = **3.5 / 5**.

**top_fix:** Confirm substrate flatness and entry/tub dimensions, then lay out the 24x48 panels to demonstrate acceptable perimeter cuts before committing to this longer format.

**gate_flags:** `geometry_verification_pending` — live Revit IDs, entry/tub offsets, wall openings, actual niche dimensions and field plane are absent; the assumed drawing geometry cannot prove cut feasibility. Wet-wall listing: PASS for Copper and Sandstone. Floor wet-use / DCOF: PASS for exact Riviera Oat 101487775. Shower-pan gate: N/A (tub; no tiled pan). Availability / Chicago lot: UNKNOWN, not a confirmed failure.

**confidence:** medium-low — product application and nominal takeoff evidence are clear; field geometry and local supply remain unverified.
