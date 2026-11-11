# Floor-plan and native geometry verification - November 9, 2026

This release supersedes the November 8 mapping of PH Bath 4 to rooms 311A/B and the wall-derived TX WC descriptions.

## Completed corrections

- TX WC 203A/B: repaired the existing native Room records in their correct enclosures, preserving IDs and UniqueIDs. Each enclosure is 13.782986 SF. Corrected upper-level constraints.
- PH Bath 4: rooms 310A/B, each 5 ft 0 in by 7 ft 0 1/4 in clear, 35.104167 SF. The neighboring printed 5 ft 5 in dimension belongs to the closet stack; bathroom walls were not stretched to that dimension.
- Native 310A renamed BATH 4; 311A/B renamed WIC 4. 310B was already BATH 4. Viewer excludes the closets; old 311 links redirect to the correct bathroom.
- PH Bath 2 full-height tile returns resolve to actual parallel side-wall faces. No unsupported finish-face previews remain in the checked views.
- Plan cameras fit current native room geometry; obsolete PH4 311 shower controls are removed.
- Legacy bed/nightstands in TX Bath4 A and view-specific filled regions remain available as optional source artifacts. They were not deleted from Revit.

## Verification

All 26 bathroom/WC instances were checked in Full and Native modes, with plan screenshots compared against A2.1/A2.2. Native Room IDs, areas, triangle sets and vertex bounds were checked. Final native readback verifies 338 source elements, 26 Room boundaries and all five repaired records with zero changes from the captured post-repair state. Desktop, phone, offline use, section and ceiling controls, A/B switching, material inspection and gallery checks passed. No browser runtime errors or external requests.

| Viewer room | Native Room | Area SF | Boundary / plan review |
|---|---|---:|---|
| PH-PRIMARY/304A | 304A | 122.017 | Verified / reviewed |
| PH-PRIMARY/304B | 304B | 122.017 | Verified / reviewed |
| PH-BATH2/305A | 305A | 35.099 | Verified / reviewed |
| PH-BATH2/305B | 305B | 35.099 | Verified / reviewed |
| PH-BATH3/307A | 307A | 34.927 | Verified / reviewed |
| PH-BATH3/307B | 307B | 34.927 | Verified / reviewed |
| PH-BATH4/310A | 310A | 35.104 | Verified / reviewed |
| PH-BATH4/310B | 310B | 35.104 | Verified / reviewed |
| PH-POWDER/405A | 405A | 27.986 | Verified / reviewed |
| PH-POWDER/405B | 405B | 27.552 | Verified / reviewed |
| PH-WC/314A | 313A | 14.639 | Verified / reviewed |
| PH-WC/314B | 313B | 14.639 | Verified / reviewed |
| TX-PRIMARY/202A | 202A | 105.093 | Verified / reviewed |
| TX-PRIMARY/202B | 202B | 105.093 | Verified / reviewed |
| TX-BATH2/205A | 205A | 37.512 | Verified / reviewed |
| TX-BATH2/205B | 205B | 39.509 | Verified / reviewed |
| TX-BATH3/207A | 207A | 36.979 | Verified / reviewed |
| TX-BATH3/207B | 207B | 39.753 | Verified / reviewed |
| TX-BATH4/007A | 007A | 34.907 | Verified / reviewed |
| TX-BATH4/007B | 007B | 35.770 | Verified / reviewed |
| TX-POWDER/102A | 102A | 22.745 | Verified / reviewed |
| TX-POWDER/102B | 102B | 22.204 | Verified / reviewed |
| TX-POWDER2/010A | 010A | 27.286 | Verified / reviewed |
| TX-POWDER2/010B | 010B | 27.286 | Verified / reviewed |
| TX-WC/203A | 203A | 13.783 | Verified / reviewed |
| TX-WC/203B | 203B | 13.783 | Verified / reviewed |

## Evidence limits

Native room displays existing project geometry, not approval of every source product or its installation. Full mode preserves frozen finish/program studies. Primary walk-in/linear-drain installation remains unverified; Bath3 tub versus walk-in remains unselected; the selected TX Bath4 tub remains unlocated. TX Bath4 B has no matched finish ceiling; overhead structure is labeled separately. Source fixtures and accessories can differ from simplified PDF symbols. Conflicting bedroom furniture is flagged and inspectable, not silently treated as bathroom equipment.

PH WC viewer identifiers 314A/B remain aliases for native 313A/B. PDF oval 314 labels are door tags; native rooms were not renumbered from those tags. Frozen product selections, SKUs and quantities in picks.json are unchanged; historical room labels in that frozen record are overridden by current runtime mapping.

## Model state and traceability

The Room edits passed live native readback before Revit closed. No save or synchronize was performed by this agent. Revit was no longer running at publication preparation on November 9; persistence after reopening remains to be confirmed. No physical walls, fixtures or furniture were modified, and no new Revit geometry was created.

Commit: `675dbe05-db95-43a9-8684-1ad3f6fa86ea`. Final readback: `40a89212-c2b5-4914-9c49-0100c66587b9`. Model: `Autodesk Docs://25-006 1527 N Wieland St/25-006 1527 N Wieland.rvt`.

Source: `C:\Users\cowey\OneDrive\Documents\25-006 1527 N Wieland fp.pdf`, sheets A2.1/A2.2. Per-room comparison images and operation receipts are retained in `scratch/floorplan_geometry_corrections_20261108/evidence`.
