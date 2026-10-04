<!-- worker5 completion -->
# Plumbing fixture row 8488981737635716

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `8488981737635716`; item key: `BT062415-BNX__8488981737635716`.
- Scheduled product: Brizo / BT062415-BNX.
- Scheduled description: Brizo 4" Tile-In Square Shower Drain - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Bath 3.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: ADDED 2026-09-03. Triplex Bath 3 is a walk-in shower with no tub, and had no shower drain after the Bath 3 / Bath 4 room swap. The Delta DT062412 that previously sat here was overwritten by the re-spec. Matched to the Brilliance Black Onyx package using the same drain Penthouse Bath 4 uses (row 85).

## Source and last verified stage

Shared product group: `BT062415-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [BT062415-BNX/Brizo_BT062415-BNX_R2025.rfa](<../BT062415-BNX/Brizo_BT062415-BNX_R2025.rfa>).
RFA SHA-256: `a7fb8782758ad4f965d503c48b33868eb3fef6a0b272d93092838c6eeb2f51c6`.
Validation: [validation.json](<../BT062415-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:12:44.976000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/BT062415-BNX/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-A-BT062415 Rev C: https://media.brizo.com/SpecSheet/BSP-A-BT062415%20Rev%20C.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 155.575 | 155.575 | 0 | PASS |
| Y | 155.575 | 155.575 | 0 | PASS |
| Z | 103.1875 | 103.1875 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Flange diameter 6.125 in; grate width/depth 4.5625 in; overall height 4.0625 in; socket OD 2.6875 in.
- Native anchor/path: Flange diameter, measured 155.575 mm; nominal 155.575 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: BT062415-BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3716", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3716", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [BT062415-BNX/source/build.py](<../BT062415-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Front.png](<../BT062415-BNX/evidence/Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Material.png](<../BT062415-BNX/evidence/Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../BT062415-BNX/evidence/Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Side.png](<../BT062415-BNX/evidence/Brizo_BT062415-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- SOURCE CONFLICT: current manufacturer calls BT062415 Tile-In but Rev C depicts a slotted grate. This model follows the dimensioned Rev C drawing and must be reviewed against the purchased part.
- Adjustable grate is set at the drawing minimum; detailed screw fittings omitted.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

- NEEDS_USER_BT062415_GRATE_IDENTITY: The current manufacturer description calls BT062415 Tile-In, while the dimensioned Rev C sheet depicts a slotted grate. The family follows Rev C. Confirm the purchased grate/trim configuration.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
