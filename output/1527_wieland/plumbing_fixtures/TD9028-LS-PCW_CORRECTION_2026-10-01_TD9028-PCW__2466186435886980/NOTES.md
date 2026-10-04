<!-- worker5 completion -->
# Plumbing fixture row 2466186435886980

**Final status: BUILT_WITH_LIMITATIONS**

## Identity and scope

- Row ID: `2466186435886980`; item key: `TD9028-LS-PCW_CORRECTION_2026-10-01_TD9028-PCW__2466186435886980`.
- Scheduled product: Westbrass / TD9028-LS-PCW \| CORRECTION 2026-10-01: TD9028-PCW.
- Scheduled description: Westbrass Round Tip-Toe Bathtub   Drain Trim Set - White.
- Scheduled finish: White; unit: Triplex; room: Bath 4.
- Original agent_ignore: `false`. Coverage does not reinstate an ignored or descoped product.

Original source note: BRAND MISMATCH - VERIFY BEFORE ORDERING (2026-08-21). This row is named as a WESTBRASS part, but Studio 41's quote S2478380 (07/17/26) lists this item as "Wet Style TD9028PCW" at $35.00 each, Special Order, 30 on-hand. WETSTYLE and Westbrass are different manufacturers. The audit was previously unable to verify the "-LS-PCW" finish suffix on any Westbrass listing, which fits with the part actually being a WETSTYLE item. Confirm with Edwin Colon which brand and exact model is being supplied, then correct the SKU and product name on this row. Not changed here because the vendor quote and the sheet disagree and only the vendor can settle which is right. | BRAND/SKU CORRECTION VERIFIED 2026-10-01: Westbrass manufacturer product page confirms TD9028 is the Tip-Toe Tub Trim Set with Floating Faceplate, and current authorized-supplier evidence identifies the Powder Coat White model as TD9028-PCW. Studio41 S2478380 line describing "Wet Style TD9028PCW" is a vendor brand misattribution; WETSTYLE does not use this TD9028 model family. Preserve the $35 quoted net price, but order against Westbrass TD9028-PCW / exact thread compatibility. Original TD9028-LS-PCW text is retained for history.

## Source and last verified stage

Shared product group: `TD9028-PCW`. The same exact scheduled product reuses one validated family across its inventory rows.
RFA: [TD9028-PCW/Westbrass_TD9028-PCW_R2025.rfa](<../TD9028-PCW/Westbrass_TD9028-PCW_R2025.rfa>).
RFA SHA-256: `aa855da36959f655f5f63de387d58d7c654f6912557edb40e995542a7b981408`.
Validation: [validation.json](<../TD9028-PCW/validation.json>); last verified stage: `complete`.
Saved Revit version: 2025; build: 25.4.50.35; native evidence finished: 2026-10-02T15:55:22.372000Z.
Source RFA input version: Native custom build.
RFA search result: No acceptable no-account RFA recovered. This records recovered evidence, not a claim that no other family exists.
Search evidence: {"result": "No acceptable no-account RFA recovered", "evidence": "_research/TD9028-PCW/sources.json"}.
Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.

Source/spec references:
- Westbrass TD9028 manufacturer thread and finish description: https://westbrass.com/product/tip-toe-tub-trim-set-with-floating-faceplate/; page 1.

## Dimensions checked

Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.

| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |
|---|---:|---:|---:|---|
| X | 229.87 | 229.87 | 0 | PASS |
| Y | 81.28 | 81.28 | 0 | PASS |
| Z | 45.9782 | 45.72 | 0.2582 | PASS |

All overall dimensions have manufacturer authority: **false**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.

- Manufacturer specifies 1.5-inch NPSM coarse drain thread with 1.875-inch nominal external diameter.
- Native anchor/path: Thread exterior diameter, measured 47.625 mm; nominal 47.625 mm; PASS.

## Native gates and parameters

Native gate result: **PASS**. Category: Plumbing Fixtures; selected type: TD9028-PCW - White; placement: WorkPlaneBased.
Gate details: {"actual_face_host": true, "category": true, "cct": true, "diffuse_bitmaps": true, "dimensions": true, "materials": true, "orientation": true, "reopen_geometry_equal": true, "reopened": true, "views": true, "warnings": true}.
Host evidence: {"host_id": "3703", "host_kind": "floor", "hostface_present": true, "instance_host_id": "3703", "normal_dot": 1.0}.
Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.

| Material parameter | Writable | Substitution reaches faces |
|---|---|---|
| Detail | True | True |
| Finish | True | True |
| Gray | True | True |

Warnings (family / reopened / placed project): [[], [], []].
Build/inspection script: [TD9028-PCW/source/build.py](<../TD9028-PCW/source/build.py>).
Visual review: PENDING_ORCHESTRATOR_VISUAL_REVIEW. Final release is pending orchestrator review.

- [Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Front.png](<../TD9028-PCW/evidence/Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Front.png>)
- [Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Material.png](<../TD9028-PCW/evidence/Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Material.png>)
- [Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Oblique.png](<../TD9028-PCW/evidence/Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Oblique.png>)
- [Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Side.png](<../TD9028-PCW/evidence/Westbrass_TD9028-PCW_R2025_Isolated - 3D View - Native Side.png>)

## Assumptions and limitations

- The two trim components are displayed side-by-side, not in a tub installation pose.
- ASSUMPTION: stopper cap 2.9 in and overflow plate 3.2 in are inferred from the product photo; no exact trim dimensional drawing was recovered.
- The legacy -LS-PCW row uses the corrected TD9028-PCW geometry based on the other matching project rows; vendor confirmation remains required.
- Independent visualization reconstruction with fixed product dimensions and editable native materials.
- Small fillets, seams, nozzle details and optical material response are inferred where the manufacturer does not dimension them.
- No internal hydraulic performance, MEP connectors, fabrication tolerances or procurement substitutions are implied.

## Blockers and release

No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.

Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.
