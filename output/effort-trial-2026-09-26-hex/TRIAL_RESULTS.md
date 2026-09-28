# Effort trial results: high vs xhigh vs max, ELM Formed Hexagon Sand, 2026-09-26

**Result: max ranked first in the blind review, but it is not production-ready as delivered.** high and xhigh ranked close behind and close to each other. All three clearly beat the 2026-09-19 baseline, which ranked last. Every arm passed every objective gate.

**Cost:** xhigh cost 2.4× high and max cost 3.9× high. Wall time was 1.4× and 1.9×.

This was one run per arm (n = 1), with one blind reviewer.

## Setup

- **Brief:** [BRIEF.md](BRIEF.md). Colour, 16-bit bump and face IDs for the 8 × 7 hex atlas, from two sources only: a 31 px/in CG layout render and an angled lifestyle image.
  - The brief named the three real finishes (Matte, Raw, Chiseled).
  - It said grooves must never be filtered out as noise.
  - It fixed the geometry, so all arms are comparable.
- **Arms:** headless `claude -p` on Opus 5.5 at `--effort high`, `xhigh` and `max`.
  - Prompts were identical apart from the folder name.
  - Each run had a $60 cap, hooks off, and was isolated from the earlier build and from the other arms.
- **Baseline:** `output/hex_10in_dimensional/` (2026-09-19), which was made from the same two images. It was graded alongside for reference.

## Cost

These figures are from the `claude -p` results and transcripts.

| | high | xhigh | max |
|---|---|---|---|
| Wall time | 69 min (60 + 10 resume) | 96 min | 133 min |
| Cost (list price) | **$6.88** | $16.62 | $26.59 |
| ÷ high | 1.0× | 2.4× | 3.9× |
| API calls | 77 | 148 | 196 |
| Tool calls | 99 | 207 | 253 |
| Output tokens | 127k | 269k | 379k |
| of which thinking | 56k | 145k | 223k |
| Cache reads | 11.9M | 40.2M | 73.3M |
| Cache writes | 244k | 399k | 543k |
| Final context | 244k | 428k | 571k |

These are the three `/usage` checks:

1. **Cache share:** 98 % for high, 99 % for xhigh, 99.3 % for max. All healthy.
2. **Output against input:** 1.05 %, 0.66 % and 0.51 %.
3. **Total input against final context:** 50×, 95× and 129×. The higher efforts did more build-check-fix loops over a larger context. Cache reads dominate their cost.

**Notes on the high run:**
- It ended its first session while a background check was still running, and headless mode killed the check. It was resumed once with a factual note, which added $0.38 and 10 min.
- A resumed session's `total_cost_usd` is cumulative. $6.88 is the total for the arm.
- The high arm also ran `Stop-Process` on every python.exe at 00:24. From the transcripts, neither of the other arms had Python running at that moment. The details are logged in `PROJECT_MEMORY.md`.

## Objective gates

These come from `_harness/grade_hex.py` and `_harness/grade_report.json`.

| Check | high | xhigh | max | baseline |
|---|---|---|---|---|
| Format (PNG header), 4489 × 4536 | ✓ | ✓ | ✓ | ✓ |
| Faces found | 56 | 56 | 56 | 56 |
| Wrap step, colour L/R and T/B (interior ≈ 1.0–1.3) | 1.23 / 0.75 | 1.39 / 0.46 | 1.68 / 0.48 | 4.31 / 4.21 (interior 4.5) |
| Mix, Matte/Raw/Chiseled (render 22/8/9 complete faces) | 32/11/13 | 32/11/13 | 32/11/13 | 22/17/17 |
| Own labels vs independent classifier | 56/56 | 56/56 | 56/56 | — |
| Chiseled groove normals | −61 / 0 / +60° | −60 / 0 / +59° | −60 / 0 / +60° | −59 / 0 / +59° |
| Clearance, deepest face point above joint floor (fraction of range) | 0.19 | 0.35 | 0.30 | 0.37 |
| Arm's own figure | 0.45 mm | 0.84 mm | 0.65 mm | — |
| Raw whole-face NCC, max over 12 symmetries | 0.045 | 0.045 | 0.045 | 0.037 |
| Raw 3 in patch search, max / median | 0.57 / 0.20 | **0.27** / 0.21 | **0.28** / 0.20 | 0.71 / 0.64 |
| Suggested Revit bump amount | 1.0 | 0.5 | 0.5 | — |

- All three arms independently measured the same Chiseled design: a 5.01–5.06 mm pitch at 90°, 30° and 150°.
- All three also calibrated Chiseled depth down to 0.60–0.70 mm against the lifestyle image.

## Blind visual review

The reviewer was Opus, given the correct product facts. Labels were randomised; the key was revealed afterwards: A = baseline, B = xhigh, C = max, D = high.

One shared renderer made every grazing image, at 15° light and the same bump height.

| | Fidelity | Relief | Albedo | Non-repetition | Artifacts | Sharpness | Mix |
|---|---|---|---|---|---|---|---|
| **max (C)** | **4** | **4** | **4** | **4** | **4** | **4** | **4** |
| high (D) | 4 | 3 | 3 | 4 | 3 | 3 | 4 |
| xhigh (B) | 3 | 3 | 3 | 4 | 3 | 3 | 4 |
| baseline (A) | 1 | 2 | 2 | 2 | 3 | 3 | 2 |

**Ranking:** max, then high and xhigh (about equal), then the baseline. The reviewer was fairly confident about first and last, and not confident about the order of high and xhigh.

- **max:**
  - Raw has organic lumps at about 0.25–0.5 in, matching the lifestyle scale.
  - Its Chiseled grooves are the crispest, and its Matte is the flattest.
  - Its Raw colour is clean albedo.
- **high:**
  - It has the most render-like Matte cloudiness and the most stone-like Raw sculpting.
  - It has the weakest relief at an equal bump amount.
    - Caveat: high suggests bump amount 1.0 where the others suggest 0.5, so at its own setting its relief reads about twice as strong.
  - Its Raw colour still tracks its relief (r = 0.47). high derived Raw height from the render's shading, so some shading stays baked into the colour.
  - Its grooves are wobbly and broken.
- **xhigh:**
  - Its Raw is harsh "crinkled foil" with near-black shadows.
  - One Chiseled face is smeared into fibrous speckle.
  - It has patchy tone in its Chiseled colour.
- **baseline:**
  - Its colour is grey-taupe (209/196/175) against the render's Sand (243/231/207).
  - Its Raw is a uniform fine sandpaper speckle, the same on every face.
  - Matte shows orange-peel relief, grooves are baked into the colour, and there are too many Raw faces (30 %).
  - This also explains its high patch-search score.

**My own check of max against the lifestyle image confirms two gaps:**
- Its grooves are cleaner and more regular than the lifestyle's ragged, chipped ridges.
- Faint groove stripes remain in its Chiseled colour.

**The reviewer's fixes before production** (max's map already records clearance, 0.648 mm):

1. Remove the leftover groove stripes from the Chiseled colour and keep tone only.
2. Add roughness and breaks along the grooves.
3. Even out the relief strength inside the one Chiseled face that fades mid-face.

## Why the arms differed

- **high** built Raw height by integrating the render's own shading. That gives stone-like forms but leaves shading in the colour. It stopped once the gates passed; its first session ended before its final check.
- **xhigh** quilted Raw and Matte from render pixels. It calibrated the frequency band against the lifestyle image, and it rebuilt Chiseled texture from orientation-aligned pools of the render's own groove faces. It also did a clean, byte-identical rebuild.
- **max** did the deepest measurement and self-audit:
  - It measured the groove profile's asymmetry from its harmonics, and found the skew is groove shape, not lighting.
  - It quilted Raw from all 12 render Raw faces, with FFT-computed reuse admissibility.
  - It audited source-pixel reuse (about 2 % of Raw pixels are symmetry-related copies, which it disclosed).
  - It fixed its own preview's shadow bug, and rebuilt reproducibly.

## Comparison with the 2026-09-25 ElmStone trial

| | ElmStone (high vs xhigh) | Hex (high vs xhigh vs max) |
|---|---|---|
| xhigh cost ÷ high | 3.7× | 2.4× |
| xhigh time ÷ high | 5.2× | 1.4× |
| Quality winner | xhigh, on product fidelity, after correcting a brief error | max; high ≈ xhigh |

- **The brief did its job.** This time the brief named the finishes and banned filtering grooves out, so no arm removed real product features. That was the fix proposed after the ElmStone trial.
- **Where effort paid off:** the gain was in measurement depth and self-review (max), not in avoiding a gross error.

## Owner's decision, 2026-09-26

**high is the default effort. max is used for challenging textures, and only when the owner requests it.** xhigh is not used. This is recorded in `AGENTS.md`.

## Recommendation (made before the decision)

- **Routine work:** keep **medium** as the default and **high** as the escalation. high produced a usable, gate-passing atlas for a quarter of max's cost, and the reviewer could not separate it from xhigh.
- **Production textures from poor sources:** max's result was measurably better. max was worth $27 here because the owner needs this texture for production.
- **Skip xhigh for texture work:** on this evidence it gave no clear gain over high, at 2.4× the cost.
- **Next step for this tile:** take max's atlas, apply fixes 1–3, then package the ADSKLIB, validate it in Revit and deliver to Drive.

## Files

- Arms: `high/`, `xhigh/`, `max/`. Each has `textures/` (the maps, `report.json` and previews), `README.md`, `SOURCE_SELECTION.md`, `ERRORS.md` and `source/`.
- Harness: `_harness/` holds:
  - `prompt-*.txt` and `result-*.json`;
  - `grade_hex.py`, `grade_report.json` and `grade_stdout.txt`;
  - `build_blind.py`, `blind/`, `blind_key.json` and `blind_info.json`.
