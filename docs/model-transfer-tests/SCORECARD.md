# Model-transfer run scorecard

Copy into the candidate run folder. Blank fields mean not recorded; all checks start NOT RUN. Allowed outcomes: PASS, FAIL, BLOCKED, NOT RUN. Use N/A only for the other test's section.

| Run metadata | Value |
|---|---|
| Run ID / test ID | |
| Exact model identifier / provider | |
| Client / version / reasoning settings | |
| OS / Revit / pyRevit / Python / V-Ray versions | |
| Available shell, image, native UI and Drive tools | |
| Source manifest hash / source deviations | |
| Started / finished / elapsed minutes | |
| Active human assistance minutes | |
| Attempts / repair cycles | |
| Input/output tokens if reported | |
| Actual billed model cost and currency, or unknown | |
| Additional reviewer/model cost, or unknown | |

## Attempt history

| Attempt | Trigger / error | Change / assistance | Evidence path | Outcome |
|---|---|---|---|---|
| Initial | | | | NOT RUN |
| Repair 1 | | | | NOT RUN |
| Repair 2 | | | | NOT RUN |

## Pendant gates — record reproduction and variation separately

| Gate | Reproduction | Variation | Evidence / measured result |
|---|---|---|---|
| Fresh native RFA, 2025 reopen, category | NOT RUN | NOT RUN | |
| Native overhead hosting and downward orientation | NOT RUN | NOT RUN | |
| Loop/canopy dimensions, inference disclosure | NOT RUN | NOT RUN | |
| Saved default total drop | NOT RUN | NOT RUN | |
| All measured flex tests | NOT RUN | NOT RUN | |
| Both materials reach nested geometry | NOT RUN | NOT RUN | |
| Warning review | NOT RUN | NOT RUN | |
| Front/side/oblique and hosted visual review | NOT RUN | NOT RUN | |

## Material gates — record reproduction and variation separately

| Gate | Reproduction | Variation | Evidence / measured result |
|---|---|---|---|
| Fresh photographic maps and source resolution | NOT RUN | NOT RUN | |
| Float pipeline / PNG depth / height precision | NOT RUN | NOT RUN | |
| Physical repeat, grout core and seamless tiling | NOT RUN | NOT RUN | |
| Normal convention / color versus data decoding | NOT RUN | NOT RUN | |
| RVT reopen, map paths and scales | NOT RUN | NOT RUN | |
| ADSKLIB second-project import | NOT RUN | NOT RUN | |
| ADSKLIB newly created or container reused (state which) | NOT RUN | NOT RUN | |
| V-Ray native import and texture resolution | NOT RUN | NOT RUN | |
| Native frontal/grazing render and visual review | NOT RUN | NOT RUN | |
| Relocation/repath verification | NOT RUN | NOT RUN | |

## Shared delivery and integrity

| Gate | Status | Evidence |
|---|---|---|
| Existing production files preserved | NOT RUN | |
| Errors and resolutions recorded in project memory | NOT RUN | |
| Native files, sources, textures, notes and logs packaged | NOT RUN | |
| ZIP integrity / final file hashes | NOT RUN | |
| Drive deduplication, upload metadata and link | NOT RUN | |

## Reviewer verdict

- Reviewer and date:
- Technical result:
- Visual result:
- Infrastructure/tool blocks:
- Artifact acceptance: NOT RUN (use ACCEPTED only when all applicable artifact gates pass; otherwise PARTIAL or FAILED).
- Delivery status: NOT RUN (independent of artifact acceptance).
- Newly created library capability demonstrated: NOT RUN.
- Unassisted success or assisted success:
- Corrections still needed:

Do not average away a failed mandatory gate with a numerical score. A blocked renderer produces a partial material result, even if every map check passes. A candidate's own verdict requires reviewer verification against actual artifacts.

For multiple runs: cost per accepted deliverable = total known model/review-model cost of all attempts, including failed attempts, divided by accepted deliverables. If none are accepted, report no accepted result and total spend; do not divide by zero. Track human time separately, unless a stated hourly rate is intentionally included. If cost is unavailable, report it as unknown. Compare only like-for-like environment and assistance policies.
