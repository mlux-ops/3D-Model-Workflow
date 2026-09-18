# Model-transfer run scorecard — P01 `candidate-20260918-01`

Run-local copy. Blank fields mean not recorded. Allowed outcomes: PASS, FAIL,
BLOCKED, NOT RUN. Nothing below is inferred where the kit says not to invent it.

| Run metadata | Value |
|---|---|
| Run ID / test ID | `candidate-20260918-01` / P01 pendant |
| Exact model identifier / provider | Preparation session: recorded only as the `Co-Authored-By: Claude Opus 5` trailer on commit `035841c`; not confirmed from client metadata. Repair session: Claude Opus 5, `claude-opus-5`, Anthropic |
| Client / version / reasoning settings | Preparation: remote cloud session, settings not exposed. Repairs: Claude Code desktop app; reasoning setting not exposed to the session |
| OS / Revit / pyRevit / Python / V-Ray versions | Windows 11 10.0.22631 · Revit 2025, running build 25.4.41.14 (pyRevit registration shows FCS 25.0.2.419) · pyRevit 6.5.5.26237+2044 · IronPython 2 engine IPY2712PR (2712) for the build; CPython 3.12.3 bundled with pyRevit for verification · V-Ray N/A for the pendant test |
| Available shell, image, native UI and Drive tools | Shell, filesystem, image viewing and native Revit access available to the repair session. Drive MCP tools present but unused — no upload was made. The preparation session had no Windows volume, Revit, pyRevit or .NET |
| Source manifest hash / source deviations | 18 of 20 entries verify. `AGENTS.md` drifted after kit commit `0a34a61` (manifest 2848 B matches that blob; working tree 4349 B). `WORKFLOW.md` unverifiable — manifest records 13538 B and no committed revision has ever been that size. Both independently confirmed during this run |
| Started / finished / elapsed minutes | Native runs 2026-09-18T06:04:59Z → 06:15:32Z, ≈10.5 min of run time across three attempts. Kit preparation preceded this on the same date and is not included |
| Active human assistance minutes | Not recorded. Operator installed pyRevit and attached it to Revit 2025 between preparation and attempt 1 |
| Attempts / repair cycles | 1 initial + 2 repair cycles, the full allowance. No attempt was reset or discarded |
| Input/output tokens if reported | unknown — not exposed to either session |
| Actual billed model cost and currency, or unknown | unknown |
| Additional reviewer/model cost, or unknown | unknown |

## Attempt history

| Attempt | Trigger / error | Change / assistance | Evidence path | Outcome |
|---|---|---|---|---|
| Initial | `AttributeError: Name` / `MissingMemberException` at `build_pendant.py:607`, `project.GetElement(floor.GetTypeId()).Name`, during host placement. `pyrevit run` still exited 0 | none — first execution of the builder as delivered | `logs/pyrevit-attempt1.log`, `logs/validation-20260918T060524073000Z.json`, `logs/build_pendant.attempt1.py` | FAIL |
| Repair 1 | Gate `measured_flex_tests` FAIL for both configurations while every flex row passed. `pyrevit run` exited 0 | Operator session added `element_name()`, reading `Element.Name` through the property descriptor with a `SYMBOL_NAME_PARAM` fallback | `logs/build_pendant.attempt2.py` | FAIL |
| Repair 2 | — | Operator session replaced the body-stability measurement: parent-instance bbox height recorded as `instance_height_in`, gate moved to `body_span_in` = measured drop − cord length, required constant at 30.55 | `validation.json`, `evidence/`, `verify_run.py` exit 0 | PASS (technical) |

## Pendant gates — reproduction and variation recorded separately

| Gate | Reproduction | Variation | Evidence / measured result |
|---|---|---|---|
| Fresh native RFA, 2025 reopen, category | PASS | PASS | Both saved and reopened; category `Lighting Fixtures`; `rfa_mtime_utc` 06:15:03Z and 06:15:19Z match disk. Built from shared construction code, no RFA copied |
| Native overhead hosting and downward orientation | PASS | PASS | Hosted on `Floor 1` bottom face at Z 228 in; `hangs_below_host` true; instance min Z 168 in (A) and 156 in (B) |
| Loop/canopy dimensions, inference disclosure | PASS | PASS | 11 dimensions within 0.01 in: loop 8.2 × 29.1, straps 0.500/0.500, inner width 7.2, globe 6.7, canopy 7.1 (bbox and ray) × 1.1, band 0.5. Inferences disclosed in `INFERENCES.md` |
| Saved default total drop | PASS | PASS | 60.0 in (A) and 72.0 in (B), verified three times each: reopened RFA type, placed instance, and RFA reopened after the flex battery |
| All measured flex tests | PASS | PASS | Cords 8 / 18.1496 / 48 / 118 in (A) and 12 / 60 in (B); formula and measured drop agree at every step; `body_span_in` held at 30.55 across all six |
| Both materials reach nested geometry | PASS | PASS | 34 faces inspected per configuration; Glass substitute on 2 faces, Metal on 32; originals restored |
| Warning review | PASS | PASS | `family_warnings` and `project_warnings` both empty for both configurations |
| Front/side/oblique and hosted visual review | PASS | PASS | Eight exports in `evidence/`, reviewed against `references/mila/661293.jpg` and the Lightology sheet. Reviewer passed both configurations 2026-09-18. `validation.json` still reads `PENDING REVIEWER` and is left exactly as the script wrote it: machine evidence is not edited to carry a human verdict |

## Material gates

N/A — this scorecard covers P01 only. M01 has not been run.

## Shared delivery and integrity

| Gate | Status | Evidence |
|---|---|---|
| Existing production files preserved | PASS | Every write routed through `out_path()`; audit in `PATH_AUDIT.md`. `output/mila/` and `scripts/` unmodified |
| Errors and resolutions recorded in project memory | PASS | Root `PROJECT_MEMORY.md`, entry "P01 pendant transfer-test run attempt — 2026-09-18", including both errors, causes, fixes and the assistance disclosure |
| Native files, sources, textures, notes and logs packaged | PASS | `output/BENCHMARK_TEST_P01_Mila_candidate-20260918-01_R2025.zip`, 37 entries: four RFAs, all notes, builder, verifier, runner, `validation.json`, eight exports, six per-attempt log artifacts and four references. Six `*.000N.rfa` files, one per earlier attempt and each with distinct content, retained as evidence under `logs/attempt-rfas/` rather than shipped as deliverables |
| ZIP integrity / final file hashes | PASS | `zipfile.testzip()` read back from the written file reports no corrupt entries. SHA-256 `159d2a2cb5405ac856336a6b6615d47ff7acb9953fb8d79b295fb508f5c282b2`, 7,632,744 bytes |
| Drive deduplication, upload metadata and link | BLOCKED | Deduplication done: no P01, benchmark or `candidate-20260918-01` package exists in **3D Models** (`1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W`); the production `Mila_Pendant_Dark_R2025.zip` is retained untouched. Upload itself is blocked by tooling, not authorisation: the Drive connector accepts only inline base64, and 4.6 MB encodes to ~6.4M characters. No Drive for Desktop sync folder and no `rclone`/`gdrive`/`gcloud` on this machine. **Upload pending; delivery is not complete** |

## Reviewer verdict

- Reviewer and date: Operator (repository owner), 2026-09-18.
- Technical result: PASS for both configurations, confirmed by `verify_run.py` exit 0 independently of the builder's own gate map.
- Visual result: PASS for both configurations, on the reviewer's own inspection of the eight exports against the reference photograph and the product sheet. Known deviations were disclosed before review and accepted: globe centre 3.9 in above the loop bottom against ~4.2 in measured from the photograph, and an inferred 6.7 in globe diameter.
- Infrastructure/tool blocks: preparation session had no Windows/Revit/pyRevit/.NET and could not execute anything native. No CPython is installed on the workstation outside pyRevit's bundled engine; `numpy` and `PIL` are absent, which `ENVIRONMENT.md` expects.
- Artifact acceptance: ACCEPTED — every applicable artifact gate passes for both configurations, technical and visual.
- Delivery status: BLOCKED — package built and verified locally, Drive upload pending for want of a transfer mechanism. Per `AGENTS.md`, local creation is not evidence of upload and none is claimed.
- Newly created library capability demonstrated: N/A for P01.
- Unassisted success or assisted success: **assisted**. The candidate preparation session's unaided result was the attempt-1 failure; both repairs were diagnosed and applied by the operator's local session. Do not score this as an unassisted candidate pass.
- Corrections still needed: visual review; the six packaging/delivery rows above; and two kit defects this run confirmed — `SOURCE_MANIFEST.csv` drift plus its mixed line-ending hashing, and the repository root named in `PROMPT_PENDANT.md` / `ENVIRONMENT.md` not existing on this workstation.
