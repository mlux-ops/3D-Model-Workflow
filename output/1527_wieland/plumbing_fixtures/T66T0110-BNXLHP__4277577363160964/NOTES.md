<!-- worker5 completion -->
# Plumbing fixture row 4277577363160964

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `4277577363160964`; item key: `T66T0110-BNXLHP__4277577363160964`.
- Scheduled product: Brizo / T66T0110-BNXLHP.
- Scheduled description: Brizo Roccesco Sensori Thermostatic Mixing Valve Trim and Cartridge - Less Handle and Valve.
- Scheduled finish: -; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `true`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `T66T0110-BNXLHP`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [T66T0110-BNXLHP/Brizo_T66T0110-BNXLHP_R2025.rfa](<../T66T0110-BNXLHP/Brizo_T66T0110-BNXLHP_R2025.rfa>).
RFA SHA-256: `341377e9a8d4b81318fa9bee25f576bd4390f56508113758a22c24c524766a27`.
Validation: [validation.json](<../T66T0110-BNXLHP/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:48:59.898000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/T66T0110-BNXLHP/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-T66T0110-LHP Rev A: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T66T0110-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 177.8 | 177.8 | 0 | PASS |
| Y | 177.8 | 177.8 | 0 | PASS |
| Z | 79.375 | 79.375 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Escutcheon diameter 7 in; projection 3.125 in; collar diameter 2.25 in.
- Native anchor/path: Plate diameter, measured 177.8 mm; nominal 177.8 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: T66T0110-BNXLHP - onyx; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3695", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3695", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Brass | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [T66T0110-BNXLHP/source/build.py](<../T66T0110-BNXLHP/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Front.png](<../T66T0110-BNXLHP/evidence/Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Material.png](<../T66T0110-BNXLHP/evidence/Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Oblique.png](<../T66T0110-BNXLHP/evidence/Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Side.png](<../T66T0110-BNXLHP/evidence/Brizo_T66T0110-BNXLHP_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Handle is separately supplied as HL66110. Cartridge sleeve steps are simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
