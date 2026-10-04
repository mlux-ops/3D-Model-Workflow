<!-- worker5 completion -->
# Plumbing fixture row 2860140157599620

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2860140157599620`; item key: `04925000__2860140157599620`.
- Scheduled product: Hansgrohe / 04925000.
- Scheduled description: Hansgrohe Croma Select E Showerhead 180 2-Jet, 2.5 GPM - Chrome.
- Scheduled finish: Chrome; unit: Triplex; room: Bath 2.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: FINISH CORRECTED 2026-08-21: this row was briefly renamed "- Matte White" during the audit. That was an audit error. hansgrohe-usa.com lists 04925000 as Finish: Chrome, list $449.00. Chrome is also consistent with the rest of this room - 04790000, 27458003 and 72530001 are all Chrome. Name corrected to Chrome. | Earlier history: the row originally read "Croma Select E Shower Only Trim Package with 2 GPM Multi Function Shower Head and Rough In Valve" with reference to the 04911 package. 04925000 is the SHOWERHEAD ONLY - no valve, no trim, no rough. The 04911 package is discontinued and never existed in Matte White, so the head-only reading was kept. IMPORTANT: this room has NO thermostatic valve trim and NO rough-in valve of any kind - see Studio 41's 17 Jul query about Bath 3 controls. Controls still need to be selected and added.

## Source and last verified stage

Shared product group: `04925000`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [04925000/Hansgrohe_04925000_R2025.rfa](<../04925000/Hansgrohe_04925000_R2025.rfa>).
RFA SHA-256: `bdead00d606b8da2e79b23567be5c5dd3938035caded5a9e3ded16fe729b7a20`.
Validation: [validation.json](<../04925000/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:37:32.532000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/04925000/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 190.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 187.325 | 187.325 | 0 | PASS |
| Y | 187.325 | 187.325 | 0 | PASS |
| Z | 85.725 | 85.725 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Width and depth 7.375 in; total head height 3.375 in; 147 spray nozzles.
- Native anchor/path: Head overall width, measured 187.325 mm; nominal 187.325 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 04925000 - Chrome; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3848", "host_kind": "ceiling", "hostface_present": true, "instance_host_id": "3848", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [04925000/source/build.py](<../04925000/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_04925000_R2025_Isolated - 3D View - Native Front.png](<../04925000/evidence/Hansgrohe_04925000_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_04925000_R2025_Isolated - 3D View - Native Material.png](<../04925000/evidence/Hansgrohe_04925000_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_04925000_R2025_Isolated - 3D View - Native Oblique.png](<../04925000/evidence/Hansgrohe_04925000_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_04925000_R2025_Isolated - 3D View - Native Side.png](<../04925000/evidence/Hansgrohe_04925000_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Ball joint shown in the neutral vertical position. Nozzle distribution and shoulder profile follow the drawing approximately.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
