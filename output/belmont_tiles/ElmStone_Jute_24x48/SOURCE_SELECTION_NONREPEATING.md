# Source selection — corrected flat/vein-cut colour atlas

One image was supplied by the user on 2026-09-20 for this correction, alongside the
instruction to make the colour maps genuinely tileable and non-repeating.

| # | file | px | view type | verdict | reason |
|---|------|----|-----------|---------|--------|
| 05 | `references/05_new_flat_veincut.jpg` | 1890 × 945 | flat, straight-on, matches this product's documented native source resolution exactly | **ACCEPTED** | Same vein-cut character as the shipped `Color.png`, at a resolution matching `SPEC.json`'s recorded native detail (1890, 945) exactly, i.e. this is (a clean copy of, or the same as) the original panel photograph. |

No other candidates existed for this correction; this is a revision of an already-shipped
material, not a fresh source search.

## Three approaches, in order, and why two were rejected

1. **Direct re-tile** (the original shipped `Color.png`): one photo, edge-matched for an
   exact wrap. Passes seamlessness, fails non-repetition — the same vein streaks would
   appear identically in every panel across a wall.
2. **Roll + flip + tone jitter** (first correction attempt): cyclically shifted and
   mirrored copies of the same photo, with mild independent brightness/warmth jitter per
   cell. Self-reviewed and rejected at the time: the same two dominant streaks were still
   recognizable in every cell, just repositioned — the specific failure WORKFLOW.md names
   ("rotating one face, adding random tint, blurring detail... is not sufficient
   variation").
3. **Procedural vein synthesis** (second attempt): replaced the streak layer with
   procedurally generated veins statistically matched to the real photo's measured
   spacing, waviness and colour, independently seeded per cell — never copying the
   photo's specific streak shapes. This genuinely stopped the literal repeat (confirmed
   by review), but the **user rejected the result** on inspection: it read as visibly
   synthetic/CG rather than photographic. Attempts to fix that by tuning the
   accompanying fine-grain layer's amplitude either left it looking near-flat (low gain)
   or introduced harsh digital-noise artifacts (high gain) — neither matched the real
   photo's organic, multi-scale texture. **User instruction: "it needs to be the photo
   based version, anything close to the deliverable is bad looking."**

## What is delivered: approach 2, restored

Per that direction, the delivered `Color_NonRepeating.png` uses approach 2 (roll + flip
+ tone jitter of 100% real photo pixels), accepting its known non-repetition limitation
in exchange for full photographic authenticity. This matches WORKFLOW.md's own guidance
for a source that cannot support full convincing variation: document the limitation
rather than inventing content. See `README.md` for the exact limitation statement and
`textures/nonrepeating_flat_report.json` for every cell's specific roll/flip/jitter
values (reproducible from the source photo alone).

**The only way to remove the residual repeat entirely is a second real photograph** of a
different area of this stone, which does not currently exist for this product.
