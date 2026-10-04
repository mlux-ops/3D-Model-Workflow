<!-- worker5 completion -->
# Plumbing fixture row 1712751433088900

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `1712751433088900`; item key: `15758001__1712751433088900`.
- Scheduled product: Hansgrohe / 15758001.
- Scheduled description: Hansgrohe Ecostat S Thermostatic Trim with Volume Control and Diverter - Chrome.
- Scheduled finish: Chrome; unit: Penthouse; room: Bath 3.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: ADDED 2026-08-21 - closes Studio 41's 17 Jul query "for the bath 3, no controls were selected". Penthouse Bath 3 had a showerhead, a wallbar handshower set, a wall outlet and a lav faucet but NO valve trim and NO rough-in of any kind - nothing to operate the shower. Selected to match this project's own Bath 2 solution: the identical Ecostat S trim + iBox rough pairing is already used in Penthouse Bath 2 and Triplex Bath 2, so the installer sees one Hansgrohe valve platform across three bathrooms. Volume control + diverter is correct for this room's two outlets (overhead 04925000 + handshower on the 04790000 wallbar). Chrome matches the rest of the room (04790000, 04925000, 27458003, 72530001 are all Chrome). Verified on hansgrohe-usa.com: 15758001, Finish Chrome, list $771.00. COST IS DERIVED, CONFIRM WITH EDWIN: $427.75 = $771.00 list x 0.5548, the exact Hansgrohe multiplier on quote S2478380 (verified across 15758701, 04186703, 04388700, 26866701, 26843701, 28276703). This part is not on that quote - it postdates it - so ask Edwin Colon to add it and replace this figure with his quoted price. Alternative considered and rejected: Edwin's GROHE placeholder (29137000 + 35601000) saved only about $65 building-wide and would have put a GROHE valve in an all-Hansgrohe Chrome shower.

## Source and last verified stage

Shared product group: `15758001`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [15758001/Hansgrohe_15758001_R2025.rfa](<../15758001/Hansgrohe_15758001_R2025.rfa>).
RFA SHA-256: `576bf1da718f3e16376b18335dc7b44168ad9e8adf9a67df92c4f62dfe489b09`.
Validation: [validation.json](<../15758001/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:23:03.982000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/15758001/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 302.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 149.225 | 149.225 | 0 | PASS |
| Y | 174.625 | 174.625 | 0 | PASS |
| Z | 79.375 | 79.375 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Escutcheon diameter 5.875 in; centers 2.875 in; lower control diameter 1.75 in; lower lever reach 2.5 in.
- Projection configured at the published 3.125 in maximum; overall height derives from the down-pointing lower lever and plate.
- Native anchor/path: Escutcheon diameter, measured 149.225 mm; nominal 149.225 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 15758001 - Chrome; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3699", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3699", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Graphite | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [15758001/source/build.py](<../15758001/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_15758001_R2025_Isolated - 3D View - Native Front.png](<../15758001/evidence/Hansgrohe_15758001_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_15758001_R2025_Isolated - 3D View - Native Material.png](<../15758001/evidence/Hansgrohe_15758001_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_15758001_R2025_Isolated - 3D View - Native Oblique.png](<../15758001/evidence/Hansgrohe_15758001_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_15758001_R2025_Isolated - 3D View - Native Side.png](<../15758001/evidence/Hansgrohe_15758001_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Installation-depth range is fixed at its outer limit for this visualization.
- Temperature markings and small internal collars are simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
