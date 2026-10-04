<!-- worker5 completion -->
# Plumbing fixture row 4890632493006724

**Final status: AVAILABLE_LOGIN_REQUIRED+BUILT**

## Identity and scope

- Row ID: `4890632493006724`; item key: `650110LF-BNX__4890632493006724`.
- Scheduled product: Brizo / 650110LF-BNX.
- Scheduled description: Brizo   Roccesco Single-Handle Bathroom Faucet with Arc Spout - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Penthouse; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: None recorded.

## Source and last verified stage

Shared product group: `650110LF-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [650110LF-BNX/Brizo_650110LF-BNX_R2025.rfa](<../650110LF-BNX/Brizo_650110LF-BNX_R2025.rfa>).
RFA SHA-256: `d10d0518b47b773fc1ac79d6ceb314925de5a1a90b4cde83d32f88094d811102`.
Validation: [validation.json](<../650110LF-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:26:59.737000Z.
Source RFA input version: Native custom build.
RFA search result: AVAILABLE_LOGIN_REQUIRED. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "AVAILABLE_LOGIN_REQUIRED", "note": "Revit download led to Sign in to continue. Chrome listing would also need finish adaptation; no login used.", "url": "https://market.bimsmith.com/product/Brizo/revit-bim-ROCCESCO-SingleHandle-Lavatory-Faucet-with-Arc-Spout--650110LFPC-62969"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-L-650110LF Rev B: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/650110LF-BL_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 76.2 | 76.2 | 0 | PASS |
| Y | 188.9122 | 188.9125 | -0.0003 | PASS |
| Z | 231.775 | 231.775 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall height 9.125 in, outlet height 5.75 in, reach 6.1875 in and base diameter 2 in: manufacturer drawing.
- Overall width derives from the 2.5625 in body-to-handle dimension plus the larger base; tube section thickness is drawing-derived.
- Native anchor/path: Base diameter, measured 50.8 mm; nominal 50.8 mm; PASS.
- Native anchor/path: Overall height, measured 231.775 mm; nominal 231.775 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 650110LF-BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3698", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3698", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [650110LF-BNX/source/build.py](<../650110LF-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Front.png](<../650110LF-BNX/evidence/Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Material.png](<../650110LF-BNX/evidence/Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../650110LF-BNX/evidence/Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Side.png](<../650110LF-BNX/evidence/Brizo_650110LF-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Above-deck visualization only; below-deck mounting shank and supply hoses are omitted.
- Oval tube section and lever height are derived from the drawing, not separately dimensioned.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
