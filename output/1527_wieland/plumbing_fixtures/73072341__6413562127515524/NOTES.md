<!-- worker5 completion -->
# Plumbing fixture row 6413562127515524

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `6413562127515524`; item key: `73072341__6413562127515524`.
- Scheduled product: Hansgrohe / 73072341.
- Scheduled description: Hansgrohe Tecturis E 1.2 GPM Single Hole Bathroom Faucet - Less Drain Assembly.
- Scheduled finish: -; unit: Triplex; room: Powder 2.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: SKU applied 2026-08-04. Verified: Hansgrohe 73072 = Tecturis E Single-Hole Fine 240, 1.2 GPM; finish 341 = Brushed Black Chrome. Was briefly mis-entered on the Rainfinity hand shower row and corrected. | ROOM CONVERTED 2026-08-23: Bath 5 is now Powder 2 (toilet + sink only). Faucet kept as the sink faucet.

## Source and last verified stage

Shared product group: `73072341`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [73072341/Hansgrohe_73072341_R2025.rfa](<../73072341/Hansgrohe_73072341_R2025.rfa>).
RFA SHA-256: `fd89b918b6f28815945af40fcc732e373b2ddf76512e4483ae7969501a0a3ac2`.
Validation: [validation.json](<../73072341/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:37:55.923000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/73072341/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 62.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 66.675 | 66.675 | 0 | PASS |
| Y | 228.6 | 228.6 | 0 | PASS |
| Z | 260.35 | 260.35 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Overall height 10.25 in; base width 1.75 in; nominal outlet height 9.625 in; outlet reach 7.75 in.
- Native anchor/path: Overall height, measured 260.35 mm; nominal 260.35 mm; PASS.
- Native anchor/path: Base width, measured 44.45 mm; nominal 44.45 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 73072341 - black_chrome; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3699", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3699", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [73072341/source/build.py](<../73072341/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_73072341_R2025_Isolated - 3D View - Native Front.png](<../73072341/evidence/Hansgrohe_73072341_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_73072341_R2025_Isolated - 3D View - Native Material.png](<../73072341/evidence/Hansgrohe_73072341_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_73072341_R2025_Isolated - 3D View - Native Oblique.png](<../73072341/evidence/Hansgrohe_73072341_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_73072341_R2025_Isolated - 3D View - Native Side.png](<../73072341/evidence/Hansgrohe_73072341_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Body/spout section dimensions and side paddle thickness are drawing-derived.
- Above-counter geometry only. Control shown closed; open-handle envelope is not modeled.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
