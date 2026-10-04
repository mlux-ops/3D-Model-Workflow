<!-- worker5 completion -->
# Plumbing fixture row 4302499802185604

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `4302499802185604`; item key: `50001141__4302499802185604`.
- Scheduled product: Hansgrohe / 50001141.
- Scheduled description: Hansgrohe Accessories 1-1/4" Non-Closing Drain Assembly - Less Overflow.
- Scheduled finish: -; unit: Triplex; room: Powder Room.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `50001141`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [50001141/Hansgrohe_50001141_R2025.rfa](<../50001141/Hansgrohe_50001141_R2025.rfa>).
RFA SHA-256: `ee7e668f001e88ed1d22ec4627d1ad1e860366b7c80cdaf2cfd69382a209e35a`.
Validation: [validation.json](<../50001141/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:38:11.025000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/50001141/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 386.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 63.5 | 63.5 | 0 | PASS |
| Y | 63.5 | 63.5 | 0 | PASS |
| Z | 135.4076 | 135.128 | 0.2796 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Cap diameter 2.5 in; tailpiece outside diameter 1.25 in.
- Native anchor/path: Cap diameter, measured 63.5 mm; nominal 63.5 mm; PASS.
- Native anchor/path: Tailpiece diameter, measured 31.75 mm; nominal 31.75 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 50001141 - bronze; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3699", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3699", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [50001141/source/build.py](<../50001141/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_50001141_R2025_Isolated - 3D View - Native Front.png](<../50001141/evidence/Hansgrohe_50001141_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_50001141_R2025_Isolated - 3D View - Native Material.png](<../50001141/evidence/Hansgrohe_50001141_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_50001141_R2025_Isolated - 3D View - Native Oblique.png](<../50001141/evidence/Hansgrohe_50001141_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_50001141_R2025_Isolated - 3D View - Native Side.png](<../50001141/evidence/Hansgrohe_50001141_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- ASSUMPTION: tailpiece cut length and assembled underside stack are modeled for visualization; the source is an exploded diagram.
- Open cap gap is fixed. It is not a functioning drain or plumbing clearance model.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
