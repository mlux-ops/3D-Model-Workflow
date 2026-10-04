<!-- worker5 completion -->
# Plumbing fixture row 784062593302404

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `784062593302404`; item key: `443306__784062593302404`.
- Scheduled product: Blanco / 443306.
- Scheduled description: BLANCO   INTEOS 30" Undermount Single-Bowl SILGRANIT Kitchen Sink - Black.
- Scheduled finish: Black; unit: Triplex; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `443306`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [443306/Blanco_443306_R2025.rfa](<../443306/Blanco_443306_R2025.rfa>).
RFA SHA-256: `d9f82558076576eaaecde7cfb9481ac661417d9ed110c916b3eafb2619e7d67e`.
Validation: [validation.json](<../443306/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:03.592000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/443306/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BLANCO INTEOS 30 top drawing: https://cdn.blanco.com/assets/hlr-system/svg/841/205841.svg; page 1.
- BLANCO INTEOS 30 side drawing: https://cdn.blanco.com/assets/hlr-system/svg/824/205824.svg; page 1.
- Exact 443306 product page: https://www.blanco.com/us/sinks/inteos/blancointeos30-u_276.724/443306; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 762 | 762 | 0 | PASS |
| Y | 495.3 | 495.3 | 0 | PASS |
| Z | 241.3 | 241.3 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- External 30 x 19.5 x 9.5 in; nominal bowl opening 26.75 x 15.75 in; bowl depth 9 in; drain 3.5 in.
- Native anchor/path: External width, measured 762 mm; nominal 762 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 443306 - Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3691", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3691", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [443306/source/build.py](<../443306/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Blanco_443306_R2025_Isolated - 3D View - Native Front.png](<../443306/evidence/Blanco_443306_R2025_Isolated - 3D View - Native Front.png>)
- [Blanco_443306_R2025_Isolated - 3D View - Native Material.png](<../443306/evidence/Blanco_443306_R2025_Isolated - 3D View - Native Material.png>)
- [Blanco_443306_R2025_Isolated - 3D View - Native Oblique.png](<../443306/evidence/Blanco_443306_R2025_Isolated - 3D View - Native Oblique.png>)
- [Blanco_443306_R2025_Isolated - 3D View - Native Side.png](<../443306/evidence/Blanco_443306_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- IDENTITY HOLD: exact manufacturer SKU 443306 is White, while the schedule requests Black. Black is retained only as the requested visual variant; no replacement SKU is asserted.
- Internal floor taper, bowl wall thickness and ledge transitions are drawing-derived; no fabrication template is implied.
- The 28.25 x 18 inch supplied cutout is a separate countertop opening, not the sink envelope.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

- NEEDS_USER_BLANCO_443306_FINISH: Exact manufacturer SKU 443306 is White; the inventory requests Black. The saved Black family is an explicitly unresolved visual variant. Confirm finish/SKU; no replacement identity has been selected.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
