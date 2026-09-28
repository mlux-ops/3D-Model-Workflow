# Effort trial results — high vs xhigh, 2026-09-25

## Correction, 2026-09-26: the brief was wrong, and xhigh got the product right

The owner checked the sources after the trial.
- `crosscut_swatch.webp` shows the **ridged** cross-cut ElmStone Jute. The fine horizontal lines are real shallow ridges along the tile's long length, about 0.09 in apart.
- `crosscut_floor_angled.jpg` shows the **flat** cross-cut, a different finish.

The brief called them the same finish, and that error is mine.

- **high** notch-filtered the ridges out as a "scan-line artifact". Its atlas is clean, but it shows the wrong product face (flat).
- **xhigh** kept the ridges, which is correct. Its patchiness comes largely from blending two different finishes, which the brief invited.
- **The blind reviewer** worked from the same wrong premise and scored the ridges as a line-pattern defect. Its "authenticity" verdict for high doesn't hold on product fidelity.

**Revised result:** xhigh was more faithful to the product, and high was cleaner but wrong. Cost and time are unchanged: xhigh took 3.7× the cost and 5.2× the time. **Owner's decision: use high as the escalation level anyway.**

The cheaper fix is in the inputs, not the effort level. A brief that names the finish ("ridged cross-cut; the ridges are real, keep them in colour and bump; don't mix with the flat floor photo") removes the judgment call that xhigh happened to get right. This is one run per arm (n = 1).

## Original result (superseded by the correction above)

**Result: high won.** On the same brief, xhigh cost 3.7× as much and took 5.2× as long. A blind reviewer still preferred high's atlas on the criterion the owner cares about most, photographic authenticity. xhigh's extra effort went into driving down patch repetition, and in doing so it smeared the stone, which is the failure the owner has rejected before.

This is one run per arm (n = 1), so run-to-run variance is unmeasured. It is evidence against xhigh for this kind of work, not proof.

## Setup

- **Task:** ElmStone Jute cross-cut non-repeating colour atlas ([BRIEF.md](BRIEF.md)), the hardest texture job this repo has handled offline. The native ADSKLIB and Lightology RFA builds had more errors, but both need the one live Revit session, so two arms couldn't run them in parallel.
- **Arms:** two headless `claude -p` sessions on Opus 5.5 (`claude-opus-5-5`) with `--effort high` or `--effort xhigh`. Prompt, inputs, settings and $40 cap were identical. Hooks were off so claude-mem couldn't inject the earlier ElmStone solution.
- **Why headless:** agent definitions created mid-session aren't loaded until the next session.

## Cost (from the `claude -p` JSON results and transcripts)

| | high | xhigh | xhigh ÷ high |
|---|---|---|---|
| Wall time | 13.8 min | 72.2 min | 5.2× |
| Cost (list price) | $3.11 | $11.53 | 3.7× |
| Turns (CLI count) | 51 | 113 | 2.2× |
| Tool calls | 45 | 102 | 2.3× |
| Output tokens | 60,245 | 224,882 | 3.7× |
| of which thinking | 24,413 | 137,247 | 5.6× |
| Cache reads | 3.24M | 20.41M | 6.3× |
| Cache writes | 157k | 368k | 2.3× |
| Final context | 157k | 368k | 2.3× |

These are the three `/usage` checks from the guide:

1. **Cache share:** 95.4 % for high and 98.2 % for xhigh. Both are healthy.
2. **Output against input:** 1.8 % and 1.1 %. Neither is out of line for its size. xhigh's extra output is thinking spread over twice as many turns.
3. **Total input against final context:** 21.6× and 56.4×. xhigh re-read its growing context through many build-check-fix loops. Each full rebuild took about 5.5 min.

## Objective gates (`_harness/grade.py`, `_harness/grade_report.json`)

| Check | high | xhigh | Previously accepted atlas |
|---|---|---|---|
| Size / format | 9228×4620 RGB ✓ | 9228×4620 RGB ✓ | ✓ |
| Joints | 4 px, exactly (209,209,209) ✓ | same ✓ | 2 px |
| Wrap step L/R, T/B | 0.00 / 0.00 ✓ | 0.00 / 0.00 ✓ | 0.00 / 0.00 |
| Highest whole-cell similarity (incl. flips and rolls) | 0.112 | 0.110 | **0.99** (near-duplicate cells) |
| Cell pairs above 0.5 | 0 | 0 | 4 |

Both arms beat the previously accepted atlas on whole-cell repetition. The whole-cell metric can't see patch-level reuse; the blind review covered that.

## Blind visual review (Opus; atlases labelled A/B at random, key revealed afterwards: A = xhigh, B = high)

- **Photographic authenticity: high better.** It keeps the swatch's sharp flake edges and pitting. xhigh looks "smeared and over-blended", with soft yellow blotches and blurred diagonal streaks.
- **Repetition: xhigh better.** high reuses patches across cells, with patch scores of 0.83–0.86 on three cell pairs. xhigh stayed at 0.64 or below.
- **Seams and artifacts: xhigh slightly better.** high shows one rotated patch with diagonal hatching beside a joint.
- **Sharpness and scale at 1:1: high better,** though one region is softer. xhigh is soft throughout and its features look enlarged.
- **Overall: high,** with medium confidence. Neither fully passes a strict "non-repeating" gate as delivered.

## Why the arms differed

- **high** built every face from 10 in swatch patches joined along best-matching seams. It removed the swatch's scan-line pattern, and used the floor photo only to check scale (it would have smeared at 64 px/in). It documented the patch recurrence honestly and stopped.
- **xhigh** also used 108 floor-photo blocks. To hide their streaking it blurred them row by row, and filled in fine grain from bland swatch areas. That is what the reviewer saw as smeared. It went through five build versions chasing small-scale repeats, and kept the swatch line pattern.

## Recommendation

- Keep **medium** as the default and escalate to **high** when medium stalls. On this evidence, don't use xhigh for texture work.
- If you want a stronger test, repeat each arm once more. Both agent definitions (`.claude/agents/effort-trial-*.md`) load in any new session.
- high's atlas is a candidate to replace the current cross-cut `Color.png`. It has far less whole-cell repetition, but its patch-level reuse should be fixed first. That's your call; nothing was changed in `output/belmont_tiles/`.

## Files

- Arms: `high/` (242 MB) and `xhigh/` (71 MB). Each has `textures/Color.png`, review images, `report.json`, `README.md`, `ERRORS.md` and `source/`.
- Harness: `_harness/` (prompts, result JSON, `grade.py`, `grade_report.json`, `blind/`, `blind_key.json`).
