# R059 — Integrated architectural completeness / interior viewer fidelity

**Scope:** viewer-only. The standalone offline deliverable is `E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\index.html`. The 13 bathroom types / 26 A-B physical instances, provisional product programs, manufacturer photo-based materials, historical prices and technical holds are unchanged. No owner approval was granted.

## What changed upstream

- **PH-PRIMARY 304A/B:** retained the exact 9.1771-ft-long native Countertop-category study and source wall polygons but did not invent missing lavatory sinks, fittings or a verified family solid. All other source-fitted countertop fronts across the 26 instances now remain vertically inside their Revit **category AABBs** rather than implying unverified cabinetry extending to the floor.
- **PH-BATH2 305A/B:** preserved the selected, source-face-fitted **59 × 29.5 in Duravit 700332000000090** with R058's clearly generic hollow tub. The original .72-ft Full Bathroom presentation cutaway remains; the new **Wet wall** view shows the unchanged W1/W2/W3 finish at its full drawing-derived height using mutually exclusive visualization layers, **not** new purchased tile or a permanent construction wall.
- **PH-BATH3 307A/B:** maintained the 2D drawing-plan tub-reference footprint, unselected TUB/WALK-IN program, nullable conditional pan and related selected/provisional finish overlays. No fabricated tub, point drain, niche or slope.
- **PH-BATH4 311A/B with independent 310A/B:** November 7 A2.2 says **310A WIC4** and **310B BATH4**. Native 310A nearby toilet/countertop-category elements cannot by themselves prove closet fixture membership, so no longer appear as constructed toilet/cabinet in WIC4. Source AABB, element ID and receipt remain accessible via optional **Source traces**. 310B retains a qualified illustrative bathroom context, separate from the 311 shower's 40.2-SF combined LEVEL/POINT PAN pool. New **311 shower** and **310 context** exterior cameras frame each source-walled compartment separately. A reversible full-height W3 finish presentation counterpart is available in Wet wall mode.
- **Whole-viewer, 26-instance reusable changes:** readable but explicitly generic porcelain WC silhouettes within the pre-existing source wall/door/counter containment gate; a reversible **Ceiling OFF/ON** faint canopy using the independently matched GWB AABB **underside elevation** and only drawing-derived wall-face footprint. There is **no** canopy where source GWB matching is absent (310B). Studio lighting and camera framing have less overexposure and more legible material contrast. Existing orbit/pan/zoom/reset, wall/edge toggles, R057 cutaways, mirrored A/B comparison, R058 fixture focus, material/source inspectors, deep links and file:// offline access remain.

## Actual physical Chrome / Playwright verification

| Test | Result |
|---|---|
| Current R059 source/provenance and PH-specific renderer gate | **PASS 26/26**, zero errors |
| Dedicated PH Full and Wet wall screenshot captures | **8/8 each** plus PH4 311/310 compartment focus |
| Ceiling preview gating and reversible source-wall cutaway | **8/8 each** |
| Full viewer modes and in-app gallery | **78/78** room/mode probes; **13/13** gallery captures, zero errors |
| Native wall-face / hosted-opening physical verification | **26/26** instances, **30/30** door AABBs, **6/6** window AABBs, **36/36** opening-depth wire spans |
| Prior R057 cutaways / PH mirrored comparisons | **PASS 26/26**, 8/8 focus and 8/8 reversible + A/B checks |
| Prior R058 TX reconstruction and material/fixture focus | **PASS 26/26**, 8 TX focus screenshots, eight reversible + A/B checks |
| Generated data and protected originals | **26/26** R059 records, one R059 ACCURACY section, **43/43** original protected hashes unchanged, 5 no-pick, 0 approvals |

Evidence: `scratch/r059_ph_browser_result.json`, `scratch/r043_arch_browser_result.json`, `scratch/r043_inapp_qa_result.json`, `scratch/r057_interior_qa_result.json`, `scratch/r058_tx_browser_result.json`. Photos: `scratch/r059_ph_gallery/R059_PH_8_AB_FULL.png`, `scratch/r059_ph_gallery/R059_PH_8_AB_WET.png`, and four PH4 311/310 focus images. Captures were opened and physically inspected; archived pre-R059 camera images had different framing, so no false pixel-identical before/after certification is claimed.

## Continuing limitations (not approved, not visually fabricated)

The live Revit title **1527 N Wieland** versus 1529 project naming remains unresolved. Registered room contours derive from native wall location/thickness plus drawing inference, **not OST_Rooms boundaries**. No native toilet/tub/lavatory solid meshes, exact ceiling trim profiles, installed vanity joinery, rough openings, swings, clearances, plumbing fixture rough-ins, shower glazing, niches or shower slopes are proved. R056 PH-POWDER 405A/B basin 3D UNLOCATED gates remain; R058 TX-PRIMARY sinks are not invented and TX-BATH4 007A/B selected tubs remain 2D UNLOCATED; PH-BATH3 and TX-BATH3 TUB/WALK-IN choices remain unselected. PH4 wall-face 26.9792 SF versus drawing 27.08 SF versus historical owner 35 SF remains unreconciled. The entire viewer remains a carefully source-qualified architectural study rather than certified manufacturer-solid photoreal BIM.

**Independent review blocker:** the sole authentic Reviewer96 ended `finished` with `revivable=false`. A new R059 independent result cannot be truthfully claimed and no replacement reviewer was spawned. Implementation/Chrome QA is not independent approval; **no global DONE**. No Git operations, deployment, email, Revit/Smartsheet writes, procurement or purchases.

STATUS round=059 phase=4-deepen
rooms: PH-PRIMARY=blocked null null | PH-BATH2=provisional round-031-A 3.480 | PH-BATH3=provisional round-036-A 3.630 | PH-BATH4=provisional round-036-B 3.860 | PH-POWDER=provisional v4-PH-POWDER 3.860 | PH-WC=blocked null null | TX-PRIMARY=blocked null null | TX-BATH2=provisional round-031-B 3.200 | TX-BATH3=provisional round-031-B 3.400 | TX-BATH4=provisional round-035-B 3.490 | TX-POWDER=blocked null null | TX-POWDER2=provisional v4-TX-POWDER2 3.660 | TX-WC=blocked null null
changed: viewer-only architectural PH/310 accuracy, WC/casework source gating, ceiling/finishes, material cameras; no selection changes
blockers: Reviewer96 finished/non-revivable (no independent R059 acceptance); native Room IDs/family solids unavailable; PH4 areas 26.9792/27.08/35 unresolved; TX4 tubs and PH powder basins 3D UNLOCATED
next: further source-supported whole-viewer architectural finishing if new read-only geometry arrives; keep frozen programs and avoid unsupported solids or a global DONE
