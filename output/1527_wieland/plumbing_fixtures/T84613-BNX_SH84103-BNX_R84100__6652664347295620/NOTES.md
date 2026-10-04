<!-- worker5 completion -->
# Plumbing fixture row 6652664347295620

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6652664347295620`; item key: `T84613-BNX_SH84103-BNX_R84100__6652664347295620`.
- Scheduled product: Brizo / T84613-BNX, SH84103-BNX , R84100.
- Scheduled description: Brizo HydraChoice Body Spray with Full Spray Touch Clean Spray Head - Round Trm - Rough-In Valve.
- Scheduled finish: -; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `true`. Coverage does not reinstate an ignored or descoped product.

Original source note: DESCOPED 2026-08-04 — body spray removed from scope. Excluded from the plumbing install schedule issued to the bidder. This row covered the HydraChoice body spray trim, escutcheon and rough-in valve together (T84613-BNX / SH84103-BNX / R84100), qty 3. Row and SKUs retained for history; do not price.

## Source and last verified stage

Shared product group: `T84613-BNX_SH84103-BNX_R84100`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [T84613-BNX_SH84103-BNX_R84100/Brizo_T84613-BNX_SH84103-BNX_R84100_R2025.rfa](<../T84613-BNX_SH84103-BNX_R84100/Brizo_T84613-BNX_SH84103-BNX_R84100_R2025.rfa>).
RFA SHA-256: `cb2ba1c2cf8afb987860d5e60680ed30bbdcb71c16c34671bf697cde1d86b0e8`.
Validation: [validation.json](<../T84613-BNX_SH84103-BNX_R84100/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:33.383000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/T84613-BNX_SH84103-BNX_R84100/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo HydraChoice T84613 Rev D: https://media.brizo.com/SpecSheet/BSP-B-T84613%20Rev%20D.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 88.9 | 88.9 | 0 | PASS |
| Y | 88.9 | 88.9 | 0 | PASS |
| Z | 95.758 | 95.758 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Trim diameter 3.5 in and face projection 0.40625 in: manufacturer trim drawing.
- Native anchor/path: Trim diameter, measured 88.9 mm; nominal 88.9 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: T84613-BNX, SH84103-BNX , R84100 - onyx; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3734", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3734", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [T84613-BNX_SH84103-BNX_R84100/source/build.py](<../T84613-BNX_SH84103-BNX_R84100/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Front.png](<../T84613-BNX_SH84103-BNX_R84100/evidence/Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Material.png](<../T84613-BNX_SH84103-BNX_R84100/evidence/Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Oblique.png](<../T84613-BNX_SH84103-BNX_R84100/evidence/Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Side.png](<../T84613-BNX_SH84103-BNX_R84100/evidence/Brizo_T84613-BNX_SH84103-BNX_R84100_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Historical body-spray row remains descoped; modeling does not restore procurement scope.
- SH84103 spray face and R84100 concealed housing are simplified inferred geometry; only trim dimensions are independently verified.
- Spray is shown in a neutral fixed pose; dynamic pop-out motion is not modeled.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
