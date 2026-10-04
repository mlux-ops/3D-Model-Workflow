<!-- worker5 completion -->
# Plumbing fixture row 1575190468951940

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `1575190468951940`; item key: `04186703__1575190468951940`.
- Scheduled product: Hansgrohe / 04186703.
- Scheduled description: Hansgrohe 9" Shower Arm with   Escutcheon - Matte White.
- Scheduled finish: White; unit: Penthouse; room: Bath 2.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: POSSIBLY DISCONTINUED - VERIFY BEFORE ORDERING (found 2026-08-20): SupplyHouse lists Hansgrohe 04186703 (Showerarm Standard 9", Matte White) as "Discontinued November 8, 2025". Other dealers (AF Supply, Splashes, Amazon, Ferguson) still show stock, so this may be a channel-specific delisting rather than a full end-of-life - but confirm availability with the vendor before this goes into a bid, and identify a Matte White substitute if it is genuinely dead. This SKU appears on 2 rows (Penthouse Bath 2 and Triplex Bath 2). |

## Source and last verified stage

Shared product group: `04186703`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [04186703/Hansgrohe_04186703_R2025.rfa](<../04186703/Hansgrohe_04186703_R2025.rfa>).
RFA SHA-256: `34700cc812dc6e8997471972002387161d1526048197be5e70d5e56093072266`.
Validation: [validation.json](<../04186703/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T14:37:35.769000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"evidence": "_research/04186703/sources.json", "result": "No acceptable no-account RFA recovered"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Hansgrohe 2026 US Price Book: https://assets.hansgrohe.com/celum/emailmarketing/hansgrohe_2026_Price_Book_en_US.pdf; page 204.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 63.5 | 63.5 | 0 | PASS |
| Y | 95.25 | 95.25 | 0 | PASS |
| Z | 234.95 | 234.95 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Flange diameter 2.5 in; total projection 9.25 in; connection drop 2.5 in below axis.
- Native anchor/path: Flange diameter, measured 63.5 mm; nominal 63.5 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: 04186703 - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3689", "host_kind": "wall", "hostface_present": true, "instance_host_id": "3689", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [04186703/source/build.py](<../04186703/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Hansgrohe_04186703_R2025_Isolated - 3D View - Native Front.png](<../04186703/evidence/Hansgrohe_04186703_R2025_Isolated - 3D View - Native Front.png>)
- [Hansgrohe_04186703_R2025_Isolated - 3D View - Native Material.png](<../04186703/evidence/Hansgrohe_04186703_R2025_Isolated - 3D View - Native Material.png>)
- [Hansgrohe_04186703_R2025_Isolated - 3D View - Native Oblique.png](<../04186703/evidence/Hansgrohe_04186703_R2025_Isolated - 3D View - Native Oblique.png>)
- [Hansgrohe_04186703_R2025_Isolated - 3D View - Native Side.png](<../04186703/evidence/Hansgrohe_04186703_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- Pipe radius and bend radius are drawing-derived. Threads omitted. Matte-white scheduled legacy variant retained.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
