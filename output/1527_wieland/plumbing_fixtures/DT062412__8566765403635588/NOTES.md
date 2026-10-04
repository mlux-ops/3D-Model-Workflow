<!-- worker5 completion -->
# Plumbing fixture row 8566765403635588

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `8566765403635588`; item key: `DT062412__8566765403635588`.
- Scheduled product: Delta / DT062412.
- Scheduled description: Delta 4" Tile-In Square Shower Drain - Chrome.
- Scheduled finish: Chrome; unit: Penthouse; room: Bath 3.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: ADDED 2026-08-21. Shower drain was missing from this bath entirely. Direction: primaries get linear drains, all other baths get a square drain in matching metal finish. Bath 3 finish is plain chrome, so brand is open. Price comparison for a 4 in. square tile-in point drain in chrome: Delta DT062412 $107 list; Hansgrohe RainDrain Brilliance 4x4 set $828 list; GROHE has no US 4 in. square point drain. Delta selected on price. COST IS AN ESTIMATE at Delta x 0.55 ($58.85 from $107 list). The Delta multiplier is not on the Wieland quote S2478380 - it was back-calculated from the 3754 Claremont Studio 41 proposal S2343240 (04 Nov 2025, Edwin Colon), which has 9 Delta lines. Observed multipliers ran 0.4935 to 0.5704, median 0.5306, mean 0.5305; 0.55 chosen because current list prices are ~9 months newer than that proposal, which depresses the calculated figure, and because Studio 41's verified Brizo multiplier is 0.5496 and Delta Faucet Company owns Brizo. EDWIN MUST STILL QUOTE THIS. Note: T3559LF-WL appears twice on that proposal at two different net prices ($198.48 and $176.17), so Studio 41 Delta pricing is not perfectly uniform.

## Source and last verified stage

Shared product group: `DT062412`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [DT062412/Delta_DT062412_R2025.rfa](<../DT062412/Delta_DT062412_R2025.rfa>).
RFA SHA-256: `f20f4f5632b66a01a6bddd55a8bb84a398d1f748e5434ba42fb0f4c7d270a52b`.
Validation: [validation.json](<../DT062412/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:54:57.577000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/DT062412/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Delta DSP-A-DT062412 Rev B: https://media.deltafaucet.com/SpecSheet/DSP-A-DT062412%20Rev%20B.pdf; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 155.575 | 155.575 | 0 | PASS |
| Y | 155.575 | 155.575 | 0 | PASS |
| Z | 103.1875 | 103.1875 | 0 | PASS |

All overall dimensions have manufacturer authority: **true**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Grate 4.5625 in square; flange 6.125 in diameter; minimum assembly height 4.0625 in; socket OD 2.6875 in.
- Native anchor/path: Flange diameter, measured 155.575 mm; nominal 155.575 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: DT062412 - Chrome; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3716", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3716", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [DT062412/source/build.py](<../DT062412/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Delta_DT062412_R2025_Isolated - 3D View - Native Front.png](<../DT062412/evidence/Delta_DT062412_R2025_Isolated - 3D View - Native Front.png>)
- [Delta_DT062412_R2025_Isolated - 3D View - Native Material.png](<../DT062412/evidence/Delta_DT062412_R2025_Isolated - 3D View - Native Material.png>)
- [Delta_DT062412_R2025_Isolated - 3D View - Native Oblique.png](<../DT062412/evidence/Delta_DT062412_R2025_Isolated - 3D View - Native Oblique.png>)
- [Delta_DT062412_R2025_Isolated - 3D View - Native Side.png](<../DT062412/evidence/Delta_DT062412_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- The manufacturer drawing shows a slotted grate although the product title says Tile-in. This model follows the inspected Rev B geometry.
- Minimum adjustment setting represented; thread and screw details simplified.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
