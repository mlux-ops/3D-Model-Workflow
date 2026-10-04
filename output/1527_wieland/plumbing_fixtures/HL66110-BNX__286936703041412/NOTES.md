<!-- worker5 completion -->
# Plumbing fixture row 286936703041412

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `286936703041412`; item key: `HL66110-BNX__286936703041412`.
- Scheduled product: Brizo / HL66110-BNX.
- Scheduled description: Brizo Roccesco Sensori Thermostatic Valve Trim Lever Handle Kit - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `true`. Coverage does not reinstate an ignored or descoped product.

Original source note: PRICING - EXPECTED $111.57, CONFIRM WITH EDWIN BEFORE RELYING ON IT (2026-08-21). This row has no Acutal Unit Cost, so Cost of Good Sold computes as $0.00 and the item is currently absent from the bid total. Derivation: Studio 41 quote S2478380 (07/17/26) prices every Brizo line at exactly 54.96% of list (verified across 7 lines). HL66110-BNX lists at $203.00 on brizo.com - the same list as HL53110-BNX, which that quote priced at $111.57. So $111.57 is the expected Studio 41 cost. DERIVED, not quoted: HL66110-BNX is not on quote S2478380 because this row did not exist when the quote was issued. Ask Edwin Colon at Studio 41 to add it, then enter the confirmed figure. | Added 2026-08-20 (audit fix F14): the Brizo Roccesco Sensori Thermostatic Mixing Valve Trim above (T66T0110-BNXLHP) is a Less Handle trim and had no matching handle-kit row anywhere on the sheet, so the assembly was incomplete as scheduled. brizo.com lists HL66110-BNX (lever) and HL66111-BNX (bent lever) as its compatible kits; HL66110-BNX added at qty 1 to match the trim. The trim also needs the R35000-WS rough, already on the sheet.

## Source and last verified stage

Shared product group: `HL66110-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [HL66110-BNX/Brizo_HL66110-BNX_R2025.rfa](<../HL66110-BNX/Brizo_HL66110-BNX_R2025.rfa>).
RFA SHA-256: `c5c127a9f5a4f382aa1519cfbda1ba03bb60d95a48967ac91349da290ddcf680`.
Validation: [validation.json](<../HL66110-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:49:03.012000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/HL66110-BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- BSP-B-T66T0110-LHP Rev A: https://bravo.requested-info.com/brands/BRZ/documents/specSheets/T66T0110-BLLHP_Spec.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 106.68 | 106.68 | 0 | PASS |
| Y | 50.8 | 50.8 | 0 | PASS |
| Z | 66.675 | 66.675 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Height/projection 2.625 in and lever axis-to-end reach 3 in: selected HL66110 detail.
- Native anchor/path: Handle projection, measured 66.675 mm; nominal 66.675 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: HL66110-BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3690", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3690", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [HL66110-BNX/source/build.py](<../HL66110-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Front.png](<../HL66110-BNX/evidence/Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Material.png](<../HL66110-BNX/evidence/Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../HL66110-BNX/evidence/Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Side.png](<../HL66110-BNX/evidence/Brizo_HL66110-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Base diameter and left overhang are scaled from the handle detail.
- Handle supplied alone with its installation axis at origin; do not place it as an additional escutcheon.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
