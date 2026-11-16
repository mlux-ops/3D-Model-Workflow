# Bathroom viewer continuation — completed HTML work

The updated standalone viewer is `E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\index.html`. Open it directly in Chrome. Its assets and data are embedded; no server or internet connection is required.

Implemented:

- Compact camera/source controls, usable phone room navigation, and a pinned Exit control in Focus view.
- Whole-room camera fitting that reserves space for actual controls; improved synthetic studio reflections and room-scaled lighting.
- Source-review cards exposing unresolved primary area comparisons and fixture-placement holds, with full provenance retained in the inspector.
- Native WC insertion XY locators as the default. Generic WC bodies remain available through **WC study** and are explicitly illustrative; no support or manufacturer installation is invented.
- Room gallery with all 13 A-instance previews, whole-image fitting, physical room labels, card navigation, and close/cancel with prior-room restoration. B instances remain separately selectable.
- Correct separate 310B context locator and original bounded countertop lid; no fixture is placed in 310A WIC.

Verified in Chrome at 1480×900 and 390×844. All 26 physical instances were checked in Full Bathroom; 10 affected A/B cases received focused rechecks. Final checks covered A/B changes, section/source toggles, material/source inspection, Full/Wet/Context modes, phone controls, and 13 offline gallery captures with room navigation and cancellation. The standalone HTML was tested from an isolated folder with network requests blocked: zero external requests and no runtime errors.

**Source limits remain open:** PH primary 122.0562 versus 103.09 SF; TX primary 104.4577 versus 87.02 SF. Native bridge access returned HTTP 401, so no fresh room membership or fixture installation could be certified. The handoff's UNLOCATED / UNSELECTED holds remain explicit. This is a source-qualified visualization, not a construction-complete or manufacturer-validated model. Frozen picks, products, programs, quantities, native coordinates and hosted openings were preserved. No Revit writes, save or synchronization occurred.

## Authoring and rebuild

- Main source: `E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\viewer3d_scene_v2.js`
- Continuation source: `E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\viewer3d_completion.js`
- Builder: `E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\build_viewer3d_index.py`
- Rebuild: `python -B "E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\build_viewer3d_index.py"`
- Baseline and QA: `E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\standalone_completion_20261108\`

The original HANDOFF.md and frozen selection files are unchanged. Verification receipts and screenshots are under the QA directory above. The initial receipt preserves resolved findings; the final verification.json states the current result and its boundaries.
