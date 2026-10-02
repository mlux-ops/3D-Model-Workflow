# Sonnet 5.5 effort trial, 2026-09-29/30: high vs xhigh vs max, compared with Opus 5.5

**Result:**
- **Material:** Sonnet does not replace Opus.
  - Sonnet high came last in the blind review.
  - Sonnet max came second to Opus max, but cost about 70 % as much and was still unfinished when it was stopped.
- **Light fixture:** Sonnet high is enough. All three Sonnet efforts pass every measured gate. Max cost 5× high and rendered the worst-looking shade.

This was one run per arm (n = 1).

## Prices

These are list prices per million tokens, from the claude-api skill (cached 2026-09-25).

| | Input | Output | Cache write (1 h) | Cache read |
|---|---|---|---|---|
| Sonnet 5.5 | $2 | $10 | $4 | $0.20 |
| Opus 5.5 | $4 | $20 | $8 | $0.20 |

- Cache reads cost the same on both models, and they are 30–45 % of every agent run's bill. That is why Sonnet is not half Opus's price per task.
- `claude -p` does not recognise `claude-sonnet-5-5` (`costBasis: "unknown"`), and it reports Opus-rate costs. Every Sonnet cost below is computed from token counts.

## Material: ELM Formed Hexagon Sand

- **Brief:** the 2026-09-26 Opus brief, unchanged except for the model name, a ban on reading the earlier trial, and foreground and PID rules (`hex/_harness/make_brief.py`).
- **Grader:** the same one as the Opus trial (`hex/_harness/grade_hex.py`; only its paths changed).

| | Sonnet high | Sonnet xhigh | Sonnet max* | Opus high | Opus xhigh | Opus max |
|---|---|---|---|---|---|---|
| Wall time | 37 min | 68 min | 138 min (stopped) | 69 min | 96 min | 133 min |
| Cost | **$5.04** | $8.75 | ≥ $18.45 | $6.88 | $16.62 | $26.59 |
| Output tokens | 164k | 340k | ≥ 786k | 127k | 269k | 379k |
| All objective gates | pass | pass | pass | pass | pass | pass |
| Raw 3 in patch-search max | 0.50 | 0.26 | 0.37 | 0.57 | 0.27 | 0.28 |
| Clearance (fraction of range) | 0.40 | 0.47 | 0.54 | 0.19 | 0.35 | 0.30 |
| **Blind rank (of 6)** | **6** (17/35) | 4 (24) | **2** (26) | 3 (26) | 5 (23) | **1** (27) |

\* The owner stopped Sonnet max at 00:11. Its maps come from a last rebuild that was never self-verified, and it has no README or `SOURCE_SELECTION.md`. Its cost comes from the transcript. The transcript under-counts output by about 13 % against the result JSON, so the cost is a lower bound.

**Blind review:** by an Opus reviewer, with the key revealed afterwards. The images were made with the same renderer as the Opus trial (`hex/_harness/build_blind6.py`; key in `blind_key6.json`).
- **Sonnet high:**
  - Shading is baked into the Chiseled colour.
  - The Raw colour is blurry, with swirl blotches.
  - One Raw motif repeats visibly.
  - The Matte faces are not flat.
- **Sonnet xhigh:**
  - Its colour is closest to the render.
  - Its grooves are weak, and one face is crosshatched.
- **Sonnet max:**
  - It has the best Raw relief and the flattest Matte.
  - It invented speckle in the Raw colour.
  - Its ridges are wavy.
- **Opus max:** it has the cleanest grooves and the best colour. Its Raw faces are slightly spiky. It ranks first again, as in the 2026-09-26 review.

## Light fixture: Nodes Angled Wall Sconce, KW1041MBK, Revit 2025

- **Brief:** new, in `sconce/BRIEF.md`.
- **Baseline:** the family delivered 2026-09-23 (`lightology_20260923/f07_833919`), logged as model "5.6"/xhigh. No Opus effort trial of a light fixture exists.
- **Grader:** an independent headless-Revit grader (`sconce/_harness/grade_sconce.py`, report in `grade_report.json`).

| | Sonnet high | Sonnet xhigh | Sonnet max | Baseline |
|---|---|---|---|---|
| Wall time | 44 min | 86 min | 145 min | — |
| Cost | **$4.76** | $13.02 | $24.16 | — |
| Output tokens | 159k | 451k | 1.04M | — |
| Envelope, W × H × D in (target 8 × 7.63 × 5.5, ±0.02) | 8.000 × 7.630 × 5.4995 | 8.000 × 7.630 × 5.4998 | 8.000 × 7.630 × 5.4996 | 8.000 × 7.633 × **5.537** ✗ |
| Shade axial / diameter (3.25 / 3.5) | 3.2500 / 3.5000 | 3.2500 / 3.5000 | 3.2500 / 3.4999 | 3.2500 / 3.4999 |
| Backplate (5.25 × 0.125) | ✓ | ✓ | ✓ | ✓ |
| Show Disc: shrinks the envelope, nothing else moves | ✓ | ✓ | ✓ | no parameter |
| Materials reach the right faces | ✓ 24 metal / 6 glass | ✓ 18 / 6 | ✓ 18 / 6 | ✓ 32 / 4 |
| Light source inside the shade | ✓ | ✓ | ✓ | **none** (not a light family) |
| Warnings, hosting | 0, wall face | 0, wall face | 0, wall face | 0, wall face |
| Look against the photos | angled-cut drum, milk shade | same; also fitted a camera to the photo | same body, **but the shade renders as clear glass**, not milk | tapered-cone body (wrong) |

- **xhigh:** the only extra value was its camera-fit comparison with the photo. The photo differs from the published numbers: the shade apex is at about 5.66 in, not 5.50, and the cut face is about 15.6°, not 18°. The family kept the published values.
- **max:** it produced nothing measurably better. Its glass material regressed.

## Decision guide

| Job | Use | Why |
|---|---|---|
| Revit family builds (light fixtures and similar) | **Sonnet 5.5 at high** | Every gate passes for $4.76 in 44 min. xhigh and max cost 2.7× and 5.1× with no gain. |
| Production textures from poor sources | **Opus 5.5 at max** (on request, as now) | It ranked first in both reviews. Sonnet max is close, but it is not cheaper per finished result: $18+ unfinished, against $26.59 finished. |
| Routine textures | **Opus 5.5 at high** | Sonnet high ranked last. Opus high ranked third for $6.88. |
| xhigh on either model | Skip | It ranked mid-pack on both models and never paid off. |

## Harness notes and errors

These are logged in `PROJECT_MEMORY.md`.
- The auto-mode classifier blocked two launches until the owner added an allow rule.
- The brief wrongly said `pdftoppm` was installed. This affected all sconce arms equally.
- **Grader fixes, each made before the final grades:**
  - chord error from face triangulation;
  - the 24 in light proxy solid;
  - the coarse caliper grid;
  - an open transaction that hung Revit (killed by PID);
  - framing thrown off by the proxy.
- To keep the owner's Revit responsive, the arm processes and the headless Revit were set to below-normal priority. Their Revit runs were serialized through `sconce/_harness/revit_run.py`.
- The runs overlapped: six arms ran at once. Wall times are therefore not directly comparable with the Opus trial, which ran three at once.
