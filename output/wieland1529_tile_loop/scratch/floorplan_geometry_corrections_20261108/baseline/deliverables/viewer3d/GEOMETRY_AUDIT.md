# Bathroom viewer: native room geometry audit and refinement

Completed November 8, 2026. This report covers all 13 bathroom types / 26 physical A/B instances in the standalone HTML viewer. Revit was the read-only source; no model transaction, save or synchronization was performed.

## Verified result

- Replaced architectural boxes, abstract opening leaves and generic WC bodies with the actual current Revit instance geometry. Full Bathroom retains the frozen finish studies; Native room exposes current source-model fixtures independently of selected products.
- 24 physical instances use exact native Room finish boundaries. The two TX WC enclosures use current native wall faces because their Room records are invalid. 310A/310B remain separately identified adjacent rooms.
- Used actual native ceiling surfaces and hosted openings. Sectioning is reversible view clipping; the source vertices are not scaled. Removed misleading basin/faucet proxies and six objects belonging above bathroom ceilings.
- Aligned finish studies to supporting native wall faces and clipped them around source openings. Two unsupported PH Bath 2 overlays are withheld, with their frozen material samples retained in Wet-zone detail.
- Final live readback: 347 source elements matched by existence, UniqueId, VersionGuid and native bounds; 26 Room records (24 bathroom records plus two separate adjacent records) matched by identity, area and finish-boundary vertices. Zero changes. Native document IsModified=false.
- Browser verification: all 26 instances in Full and Native room (52 checks), actual triangle sets and vertex bounds, source/area identity, section/ceiling controls in both modes, A/B comparison, source/material inspectors, Wet study, archived context, gallery, phone layout and isolated offline loading passed. No JavaScript errors or network requests. The two contact sheets were visually reviewed, including corrected above-ceiling filtering.
- Frozen picks, SKUs, programs and quantities remain byte-for-byte unchanged. Source-family geometry is not approval of the selected product or its installation.

## Room-by-room source geometry

Areas below are geometry evidence, not replacement takeoff quantities. A/B geometry is independent. Ceiling heights are measured from the actual occupied level to the native ceiling underside.

| Physical instance | Native Room / ID | Area SF | Historical study SF | Ceiling height ft | Source elements |
| --- | --- | ---: | ---: | ---: | ---: |
| PH-PRIMARY/304A | 304A / 15921408 | 122.017 | 103.09 | 9.156 | 16 |
| PH-PRIMARY/304B | 304B / 15921405 | 122.017 | 103.09 | 9.156 | 28 |
| PH-BATH2/305A | 305A / 15921411 | 35.099 | 35.00 | 9.156 | 14 |
| PH-BATH2/305B | 305B / 15921414 | 35.099 | 35.00 | 9.156 | 18 |
| PH-BATH3/307A | 307A / 15921429 | 34.927 | 35.00 | 9.156 | 12 |
| PH-BATH3/307B | 307B / 15921432 | 34.927 | 35.00 | 9.156 | 15 |
| PH-BATH4/311A | 311A / 15921450 | 26.979 | 27.08 | 9.156 | 18 |
| PH-BATH4/311B | 311B / 15921447 | 26.979 | 27.08 | 9.156 | 22 |
| PH-POWDER/405A | 405A / 15925464 | 27.986 | 27.95 | 9.083 | 15 |
| PH-POWDER/405B | 405B / 15925461 | 27.552 | 27.95 | 9.083 | 15 |
| PH-WC/314A | 313A / 15926307 | 14.639 | 14.64 | 9.156 | 9 |
| PH-WC/314B | 313B / 15926310 | 14.639 | 14.64 | 9.156 | 10 |
| TX-PRIMARY/202A | 202A / 10540416 | 105.093 | 87.02 | 9.302 | 23 |
| TX-PRIMARY/202B | 202B / 15882851 | 105.093 | 87.02 | 9.250 | 19 |
| TX-BATH2/205A | 205A / 15883581 | 37.512 | 38.35 | 9.250 | 16 |
| TX-BATH2/205B | 205B / 15883772 | 39.509 | 38.35 | 9.250 | 16 |
| TX-BATH3/207A | 207A / 15883594 | 36.979 | 36.98 | 9.250 | 15 |
| TX-BATH3/207B | 207B / 15883784 | 39.753 | 36.98 | 9.250 | 20 |
| TX-BATH4/007A | 007A / 15879005 | 34.907 | 38.89 | 10.083 | 17 |
| TX-BATH4/007B | 007B / 15879020 | 35.770 | 38.89 | No matched finish ceiling | 12 |
| TX-POWDER/102A | 102A / 15881991 | 22.745 | 22.17 | 9.240 | 13 |
| TX-POWDER/102B | 102B / 15881451 | 22.204 | 22.17 | 9.240 | 14 |
| TX-POWDER2/010A | 010A / 15879414 | 27.286 | 26.69 | 10.083 | 17 |
| TX-POWDER2/010B | 010B / 15879411 | 27.286 | 26.69 | 10.083 | 12 |
| TX-WC/203A | Wall-derived; Room invalid | 13.783 | 14.00 | 9.302 | 9 |
| TX-WC/203B | Wall-derived; Room invalid | 13.783 | 14.00 | 9.302 | 9 |

## Remaining source and placement issues

These issues are displayed in the viewer and remain distinct from corrected viewer geometry. No model alteration or product assumption was used to conceal them.

### PH-PRIMARY/304A

- Current area differs from historical takeoff. Selected walk-in/drain installation remains unlocated; source-model tub is a separate reference.
- Native Room-property conflicts on 16428737: position/level used; family associations are not repaired in Revit.
- Above-ceiling adjacent-storey object excluded: 12070458.

### PH-PRIMARY/304B

- Current area differs from historical takeoff. Selected walk-in/drain installation remains unlocated; source-model tub is a separate reference.
- Native Room-property conflicts on 15957325: position/level used; family associations are not repaired in Revit.
- Above-ceiling adjacent-storey object excluded: 18375050.

### PH-BATH2/305A

- One unsupported wall-study rectangle withheld; material retained in Wet-zone detail. Selected tub remains a nominal study.

### PH-BATH2/305B

- One unsupported wall-study rectangle withheld; material retained in Wet-zone detail. Selected tub remains a nominal study.

### PH-BATH3/307A

- Tub versus walk-in remains UNSELECTED.

### PH-BATH3/307B

- Tub versus walk-in remains UNSELECTED.
- Above-ceiling adjacent-storey object excluded: 17460872.

### PH-BATH4/311A

- 311 main space and 310 adjacency remain separate. 310A is WIC 4; 310B is Bath 4. Frozen combined material pool unchanged.

### PH-BATH4/311B

- 311 main space and 310 adjacency remain separate. 310A is WIC 4; 310B is Bath 4. Frozen combined material pool unchanged.

### PH-POWDER/405A

- Prior basin locator was a wall faucet; removed that misleading basin proxy. Selected basin installation remains unlocated.
- Native Room-property conflicts on 16951723: position/level used; family associations are not repaired in Revit.

### PH-POWDER/405B

- Prior basin locator was a wall faucet; removed that misleading basin proxy. Selected basin installation remains unlocated.
- Native Room-property conflicts on 16951721: position/level used; family associations are not repaired in Revit.

### PH-WC/314A

- Viewer 314A maps to native 313A.
- Above-ceiling adjacent-storey object excluded: 12070455.

### PH-WC/314B

- Viewer 314B maps to native 313B.
- Above-ceiling adjacent-storey object excluded: 18375051.

### TX-PRIMARY/202A

- Current area differs from historical takeoff. Selected walk-in/drain installation remains unlocated; source-model tub is a separate reference.
- Native Room-property conflicts on 15997703, 16437657, 16437668, 16437700, 16437701, 17114616, 17114618, 17180004, 17180006, 18006284: position/level used; family associations are not repaired in Revit.

### TX-PRIMARY/202B

- Current area differs from historical takeoff. Selected walk-in/drain installation remains unlocated; source-model tub is a separate reference.
- Native Room-property conflicts on 18055984: position/level used; family associations are not repaired in Revit.

### TX-BATH2/205A

- Selected tub remains a nominal study; native bathtub shown separately in Native room.
- Native Room-property conflicts on 16437617, 16437622, 16437672, 17180989: position/level used; family associations are not repaired in Revit.

### TX-BATH2/205B

- Selected tub remains a nominal study; native bathtub shown separately in Native room.

### TX-BATH3/207A

- Tub versus walk-in remains UNSELECTED.
- Native Room-property conflicts on 16437695: position/level used; family associations are not repaired in Revit.
- Above-ceiling adjacent-storey object excluded: 16438318.

### TX-BATH3/207B

- Tub versus walk-in remains UNSELECTED.
- Native Room-property conflicts on 15282474: position/level used; family associations are not repaired in Revit.
- Above-ceiling adjacent-storey object excluded: 16438253.

### TX-BATH4/007A

- Selected tub remains UNLOCATED; no tub installation invented.

### TX-BATH4/007B

- Selected tub remains UNLOCATED; no tub installation invented.
- No matched native finish ceiling; overhead structure is labeled separately.

### TX-POWDER/102A

- Wall finish remains NO PICK; native geometry does not choose products.

### TX-POWDER/102B

- Wall finish remains NO PICK; native geometry does not choose products.
- Native Room-property conflicts on 15802673: position/level used; family associations are not repaired in Revit.

### TX-POWDER2/010A

- Basin remains UNSELECTED; source-model basin is a reference.
- Native Room-property conflicts on 16306691: position/level used; family associations are not repaired in Revit.

### TX-POWDER2/010B

- Basin remains UNSELECTED; source-model basin is a reference.
- Native Room-property conflicts on 17133383: position/level used; family associations are not repaired in Revit.

### TX-WC/203A

- Physical enclosure verified by wall faces; native Room record invalid.

### TX-WC/203B

- Physical enclosure verified by wall faces; native Room record invalid.

## Geometric contact checks and limits

Four current-pose WC/door candidates with overlapping category boxes were checked with native solid Boolean intersections. All returned 0.0 cubic feet, with no Boolean errors: 16428736/16428737, 15957324/15957325, 16437628/16437630 and 15950765/15950822. This is a targeted current-pose contact check, not a complete swing, accessibility, code or construction-clearance certification.

Two curved Brizo elements (15517582, 15517868) have native tessellations extending about 0.00248 / 0.00394 ft beyond their category boxes. Independent GetInstanceGeometry verification confirmed the same native points within 0.00002 ft. No vertex clamping was used. Two faucet families (17074252, 17074649) each contain four native RevolvedFaces that return no triangulation, even at explicit LOD 0.5; each omitted face is below 0.00001 SF. These native-mesher omissions are retained in the source audit; no replacement surface was invented.

Browser geometry is a display tessellation of the source model. Room-only wall, floor, door and window geometry is clipped for presentation; fixture geometry retains the source instance shape and position. Native material RGB is used for the source layer; screen PBR response and frozen finish samples are visualization, not physical-material certification. No opaque family, DirectShape, mesh import or new geometry was created in Revit.

## Native identity, access and receipts

- Document: `25-006 1527 N Wieland`
- Path: `Autodesk Docs://25-006 1527 N Wieland St/25-006 1527 N Wieland.rvt`
- Current Revit process: `72064`; session: `b29598c2-76f2-40ac-b6a0-b8b3f2455a5e`.
- Authoritative documents.list operation: `195855a2-1b57-49ac-ba77-59e1be74f481`; completed receipt readback: `020e9f55-c046-49aa-aa97-f84be447ee0f`.
- Refreshed room survey: `bae16e7d-a0fc-45db-b0a5-a04205e681cb`; physical-storey inventory: `5c0b334a-990a-4493-afd0-bb4c3a3d9d2c`.
- Final source readback: `31ce786a-e66b-4969-8a09-caee0784ffba`.
- Direct external bridge calls returned HTTP 401. The existing in-process API dispatcher was used deliberately for read-only native Room/DB geometry, with the actual installed native DocumentRegistry.Resolve(session) guard. Capabilities and official document discovery were checked through the installed bridge internally. Custom geometry reads have retained route receipts; they are not represented as predefined native bridge operations.
- Revit restarted during the task. The old PID 45468 snapshot is retained as historical evidence only. All release geometry was reread from PID 72064 / the current session; final readback confirms that snapshot.

## Deliverable and reproducibility

`index.html` contains all viewer libraries, frozen data, images and compressed native geometry. It opens by itself from a local file in current Chrome; no server or network is required. `native_geometry.json` / `.json.gz` are companion source snapshots, not runtime dependencies. `GEOMETRY_AUDIT.json` provides machine-readable per-room findings.

Editable authoring files are `scratch/viewer3d_scene_v2.js`, `scratch/viewer3d_completion.js`, `scratch/native_room_geometry.js` and `scratch/build_viewer3d_index.py`. Rebuild with `python -B scratch/build_viewer3d_index.py` from the tile-task root. The frozen `picks.json` must not be regenerated. Current browser/source receipts and screen captures are retained in `scratch/native_geometry_audit_20261108/evidence/` and the H: working audit folder.

API references used for source extraction: [Autodesk Mesh API](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/bf9cd59c-03c3-9e7f-1e2b-6aaf5c425b69.htm), [Autodesk spatial-element boundaries](https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/8e0919af-6172-9d16-26d2-268e42f7e936.htm).
