# Lightology Face-Based RFA Implementation Plan

Goal: Finish only after all 12 fixtures and all 14 requested configurations are accurate, usable Revit 2025 face-based RFAs, pass prime visual and final review, and every output is verified in Google Drive.

Architecture: One 5.6 Sol extra-high worker per fixture. Eight concurrent slots, separate fixture directories, serial native Revit execution granted by prime. Prime performs fixture work only for stuck-worker help, required visual review, and final review. No commits, merges, pushes, or approval pauses. Use CoS Plugins fetch for all linked product research.

Spec: User's original Lightology request and selections below; repository AGENTS.md, WORKFLOW.md and PROJECT_MEMORY.md apply. Native project root verified E:\Claude\3D-Model-Workflow. Do not copy historical ROOT constants from older builders.

## Owned tasks
Each owns output/lightology_20260923/<folder>/ including sources, builder, native RFA(s), validation, and review images.
01 f01_816712: https://www.lightology.com/index.php?module=prod_detail&prod_id=816712&option_id=816709 ; matte black.
02 f02_231180: https://www.lightology.com/index.php?module=prod_detail&prod_id=231180 ; brass.
03 f03_1241670: https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241669 ; bronze.
04 f04_1149899: https://www.lightology.com/index.php?module=prod_detail&prod_id=1149899 ; brass, 9.8-inch size.
05 f05_1441643: https://www.lightology.com/index.php?module=prod_detail&prod_id=1441643&option_id=1441619 ; black anodized exterior, amber AND white interiors, both 3000 K; two RFAs.
06 f06_1418164: https://www.lightology.com/index.php?module=prod_detail&prod_id=1418164&cat_id=9 ; coal, 11-inch width.
07 f07_833919: https://www.lightology.com/index.php?module=prod_detail&prod_id=833919&option_id=833918 ; brass AND midnight black; two RFAs.
08 f08_1104949: https://www.lightology.com/index.php?module=prod_detail&prod_id=1104949 ; aged gold, opal matte.
09 f09_1254269: https://www.lightology.com/index.php?module=prod_detail&prod_id=1254269&option_id=1254270 ; brass.
10 f10_1242580: https://www.lightology.com/index.php?module=prod_detail&prod_id=1242580&option_id=1242586 ; exact linked option, no override.
11 f11_1476233: https://www.lightology.com/index.php?module=prod_detail&prod_id=1476233&option_id=1476230 ; gold, 8.7-inch width, 3000 K.
12 f12_813073: https://www.lightology.com/index.php?module=prod_detail&prod_id=813073 ; natural brass.

## Per-fixture workflow
- [ ] Fetch exact product/option through CoS fetch; save source photos, dimension drawings, SKU/finish/dimension manifest; visually inspect before modeling. Separate measured, drawing-derived, and inferred details. Best judgment is authorized when exact variant is not pictured.
- [ ] Build native solids using actual face-based template and Lighting Fixtures category, editable appearance materials, faithful silhouette, openings, smooth profiles, connections and proportions.
- [ ] Send READY_REVIT with exact command; wait for prime's native slot grant while finishing research/notes. Do not alter user's existing documents or unrelated processes.
- [ ] Save and reopen every RFA. Test actual native host-face reference, host identity and mounting normal, dimensions from geometry, all requested variants, and material substitution reaching faces. Record warnings and timestamped validation JSON. CLI exit zero is not success evidence.
- [ ] Export native front, side, oblique, material and hosted views. Inspect source and candidate images, produce comparison, submit VISUAL_REVIEW with paths, correct every rejection.
- [ ] Complete README, sources, inferences, builder, RFAs, textures, technical and visual evidence. Finish with RESULT / CHANGES / VALIDATION / BLOCKERS; prime acceptance is separate.

## Prior lessons and interface checks
Proven builders: scripts/build_kamden.py; scripts/build_mila.py; output/model-transfer-tests/candidate-20260918-01/pendant/build_pendant.py and verify_run.py. Prevent old ROOT paths, missing regenerate before bounds, IronPython Element.Name descriptor failures, tiny curves below ShortCurveTolerance, loft overshoot, body bounds mixing cord/canopy, and falsely accepting washed-out Realistic exports. Native face-based usability and visual fidelity are independent gates.
All task output directories are disjoint. Shared native Revit slot and final package are prime-owned. Error entries are append-only in PROJECT_MEMORY.md, also local per-task notes. No shared builder modifications. Review focus for every task: exact selected option; printed dimensions; true face host; real shell openings; material/CCT settings across variants.

## Final acceptance
- [ ] Prime visually accepts all 14 configurations and verifies saved native technical evidence, with no failed or pending required gate.
- [ ] Package ALL outputs under explicit paths, separate final RFAs from attempts, include references, builders, textures, README, QA and inference records. Verify ZIP readback, contents and SHA-256.
- [ ] Check duplicates, upload under Google Drive 3D Model Workflow (1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD) / 3D Models, verify remote parent, filename and byte size. Sync copy is insufficient.
- [ ] session_finish only when implementation is complete and final verification remains. Goal stays CONTINUE until every gate and upload verification passes.