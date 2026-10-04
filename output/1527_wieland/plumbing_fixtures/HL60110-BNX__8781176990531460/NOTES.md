<!-- worker5 completion -->
# Plumbing fixture row 8781176990531460

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `8781176990531460`; item key: `HL60110-BNX__8781176990531460`.
- Scheduled product: Brizo / HL60110-BNX.
- Scheduled description: Brizo Roccesco TempAssure Thermostatic Valve Trim Lever Handle Kit - Brilliance Black Onyx.
- Scheduled finish: Brilliance Black Onyx; Black; unit: Triplex; room: Primary Bathroom.
- Original agent_ignore: `true`. Coverage does not reinstate an ignored or descoped product.

Original source note: PRICING - EXPECTED $111.57, CONFIRM WITH EDWIN BEFORE RELYING ON IT (2026-08-21). This row still carries $100.00 inherited from T600110-BNXLHP, the valve trim it replaced. It has NOT been re-quoted. Derivation of the expected figure: Studio 41 quote S2478380 (07/17/26) prices every Brizo line at exactly 54.96% of list. Verified on 7 lines - 899110-12-BNX $878 list/$482.53, 813110-BNX-2.5 $743/$408.34, HL75110-BNX $304/$167.07, HL704110-BNX $473/$259.95, R70400 $299/$164.33, HL53110-BNX $203/$111.57, 653110LF-BNXLHP $675/$370.97. HL60110-BNX lists at $203.00 on brizo.com, the same list price as HL53110-BNX, which that quote priced at $111.57. So $111.57 is the expected Studio 41 cost. This is DERIVED from the discount pattern, not a quoted line - HL60110-BNX does not appear on quote S2478380 because this row was still T600110 when the quote was issued. Ask Edwin Colon at Studio 41 to add HL60110-BNX to the quote, then enter the confirmed figure. | HL60110-BNX confirmed on brizo.com as the correct lever handle kit for the T600110-BNXLHP trim (HL60111-BNX is the bent-lever alternative). The row's old Reference pointed at HL66110, which belongs to the different T66T0110 Sensori trim - two near-identical SKUs had been crossed.

## Source and last verified stage

Shared product group: `HL60110-BNX`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [HL60110-BNX/Brizo_HL60110-BNX_R2025.rfa](<../HL60110-BNX/Brizo_HL60110-BNX_R2025.rfa>).
RFA SHA-256: `800ed6324c0b0e715b22d4190a4b712beae589db33bbad1d1c622a55a732f38a`.
Validation: [validation.json](<../HL60110-BNX/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:43:08.371000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/HL60110-BNX/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Brizo BSP-B-T600110-LHP Rev A: https://media.brizo.com/SpecSheet/BSP-B-T600110-LHP%20Rev%20A.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 88.9 | 88.9 | 0 | PASS |
| Y | 63.5 | 63.5 | 0 | PASS |
| Z | 104.775 | 104.775 | 0 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Lever width 3.5 in and total handle projection 4.125 in: exact manufacturer handle detail.
- Native anchor/path: Handle projection, measured 104.775 mm; nominal 104.775 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: HL60110-BNX - Brilliance Black Onyx -  Black; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3691", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3691", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [HL60110-BNX/source/build.py](<../HL60110-BNX/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Front.png](<../HL60110-BNX/evidence/Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Front.png>)
- [Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Material.png](<../HL60110-BNX/evidence/Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Material.png>)
- [Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Oblique.png](<../HL60110-BNX/evidence/Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Oblique.png>)
- [Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Side.png](<../HL60110-BNX/evidence/Brizo_HL60110-BNX_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Sleeve diameter, control ring separation and relative temperature-lever depth are drawing-derived.
- This is the handle kit only; separate trim and rough families are not incorporated.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
