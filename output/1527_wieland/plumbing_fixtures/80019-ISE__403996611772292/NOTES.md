<!-- worker5 completion -->
# Plumbing fixture row 403996611772292

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `403996611772292`; item key: `80019-ISE__403996611772292`.
- Scheduled product: - / 80019-ISE.
- Scheduled description: InSinkErator Power Series 0.75   HP Continuous-Feed Garbage Disposal.
- Scheduled finish: -; unit: Penthouse; room: Kitchen.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `80019-ISE`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [80019-ISE/Fixture_80019-ISE_R2025.rfa](<../80019-ISE/Fixture_80019-ISE_R2025.rfa>).
RFA SHA-256: `b708e235242b5094073f728e74bbe0a85538b004119d7d7417b1764f76f368da`.
Validation: [validation.json](<../80019-ISE/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:09.483000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/80019-ISE/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- InSinkErator Power .75 HP manufacturer product specifications: https://www.insinkerator.com/en-us/shop/insinkerator/products/garbage-disposals/insinkerator-pwr-75hp; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 209.55 | 209.55 | 0 | PASS |
| Y | 209.55 | 209.55 | 0 | PASS |
| Z | 311.15 | 311.15 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Current manufacturer body specification is 12.25 in high and 8.25 in wide.
- Native anchor/path: Overall body height, measured 311.15 mm; nominal 311.15 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 80019-ISE - gray; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3698", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3698", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [80019-ISE/source/build.py](<../80019-ISE/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Fixture_80019-ISE_R2025_Isolated - 3D View - Native Front.png](<../80019-ISE/evidence/Fixture_80019-ISE_R2025_Isolated - 3D View - Native Front.png>)
- [Fixture_80019-ISE_R2025_Isolated - 3D View - Native Material.png](<../80019-ISE/evidence/Fixture_80019-ISE_R2025_Isolated - 3D View - Native Material.png>)
- [Fixture_80019-ISE_R2025_Isolated - 3D View - Native Oblique.png](<../80019-ISE/evidence/Fixture_80019-ISE_R2025_Isolated - 3D View - Native Oblique.png>)
- [Fixture_80019-ISE_R2025_Isolated - 3D View - Native Side.png](<../80019-ISE/evidence/Fixture_80019-ISE_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- IDENTITY HOLD: the current manufacturer page redirects the Power .75 product to package SKU 81222K; schedule 80019-ISE is retained as the requested legacy package identity.
- ASSUMPTION: the motor body is shared; cord, adapter and discharge elbow are excluded.
- Housing profile and band proportions are photo-derived.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

- NEEDS_USER_80019_ISE_PACKAGE: The preserved current manufacturer page redirects Power .75 to package SKU 81222K. The family retains scheduled legacy package 80019-ISE. Confirm the intended package identity before release.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
