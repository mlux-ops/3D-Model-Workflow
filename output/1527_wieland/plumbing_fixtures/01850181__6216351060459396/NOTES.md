<!-- worker5 completion -->
# Plumbing fixture row 6216351060459396

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6216351060459396`; item key: `01850181__6216351060459396`.
- Scheduled product: Hansgrohe / 01850181.
- Scheduled description: Hansgrohe iBox Universal Plus Rough-In Valve, 3/4" and 1/2" with Service Stops.
- Scheduled finish: -; unit: Penthouse; room: Bath 3.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: ADDED 2026-08-21 - closes Studio 41's 17 Jul query about Bath 3 controls. This room had no rough-in valve at all. The 15758001 Ecostat S trim above mounts on this iBox, the same pairing already used in Penthouse Bath 2 and Triplex Bath 2. Finish-neutral part - identical in every room regardless of trim finish. COST IS AN ACTUAL QUOTED PRICE, not derived: $71.23 is the price Studio 41 quoted for 01850181 on quote S2478380 (list $228.00). Note roughs on that quote are discounted far more deeply and irregularly than trims, which is why this uses the quoted figure directly rather than a multiplier.

## Source and last verified stage

Shared product group: `01850181`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [01850181/Hansgrohe_01850181_R2025.rfa](<../01850181/Hansgrohe_01850181_R2025.rfa>).
RFA SHA-256: `58d30c0d6f9eb969176cee08a5baa0dd7525be00cc46818ec6af0580cc9b0ad1`.
Validation: [validation.json](<../01850181/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:37:39.570000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/01850181/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 374.
- Manufacturer reference: https://www.bimobject.com/en-us/hansgrohe/product/01850181.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 149.225 | 149.225 | 0 | PASS |
| Y | 149.225 | 149.225 | 0 | PASS |
| Z | 107.95 | 107.95 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Port-to-port envelope 5.875 in in both directions; body depth 4.25 in; shell diameter 4.75 in.
- Native anchor/path: Shell diameter, measured 120.65 mm; nominal 120.65 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 01850181 - green; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3702", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3702", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Green | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [01850181/source/build.py](<../01850181/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_01850181_R2025_Isolated - 3D View - Native Front.png](<../01850181/evidence/Hansgrohe_01850181_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_01850181_R2025_Isolated - 3D View - Native Material.png](<../01850181/evidence/Hansgrohe_01850181_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_01850181_R2025_Isolated - 3D View - Native Oblique.png](<../01850181/evidence/Hansgrohe_01850181_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_01850181_R2025_Isolated - 3D View - Native Side.png](<../01850181/evidence/Hansgrohe_01850181_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Protective shell and brass valve are a coordination visualization. Internal cartridges, support ribs, mounting holes and threads are simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
