<!-- worker5 completion -->
# Plumbing fixture row 2332174965211012

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2332174965211012`; item key: `700332000000090__2332174965211012`.
- Scheduled product: Duravit / 700332000000090.
- Scheduled description: Duravit Starck 59" x 29-1/2" Built-In Acrylic Bathtub with Support Frame - White.
- Scheduled finish: White; unit: Triplex; room: Bath 2.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `700332000000090`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [700332000000090/Duravit_700332000000090_R2025.rfa](<../700332000000090/Duravit_700332000000090_R2025.rfa>).
RFA SHA-256: `14454a856c1927cb6510705e31de08ca1446efc9390c08b70bc02df31d932637`.
Validation: [validation.json](<../700332000000090/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:12.604000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/700332000000090/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Duravit 700332000000090 official product dimensions: https://pro.duravit.us/pro/content/homepage/series/series/overview/products~402880943a1b6e1b013a1bd20b39003d.us-en.html?nser=1110&product=3169419&ncat=bathtubs; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 1498.6 | 1498.6 | 0 | PASS |
| Y | 749.3 | 749.3 | 0 | PASS |
| Z | 479.425 | 479.425 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Official body dimensions 59 x 29.5 x 18.875 in.
- Native anchor/path: Rim length, measured 1498.6 mm; nominal 1498.6 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 700332000000090 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3691", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3691", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [700332000000090/source/build.py](<../700332000000090/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Duravit_700332000000090_R2025_Isolated - 3D View - Native Front.png](<../700332000000090/evidence/Duravit_700332000000090_R2025_Isolated - 3D View - Native Front.png>)
- [Duravit_700332000000090_R2025_Isolated - 3D View - Native Material.png](<../700332000000090/evidence/Duravit_700332000000090_R2025_Isolated - 3D View - Native Material.png>)
- [Duravit_700332000000090_R2025_Isolated - 3D View - Native Oblique.png](<../700332000000090/evidence/Duravit_700332000000090_R2025_Isolated - 3D View - Native Oblique.png>)
- [Duravit_700332000000090_R2025_Isolated - 3D View - Native Side.png](<../700332000000090/evidence/Duravit_700332000000090_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- The scheduled SKU includes a support frame; its concealed, installation-dependent frame is omitted from this visible tub-body family.
- Interior slopes, floor profile, drain location and overflow diameter are drawing-derived.
- Manufacturer lists STEP/DWG/DXF for this exact model but no public RFA on the inspected page.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
