# Design critique board

The board is four critic workers spawned by the prime with the `agents` tool. They persist
across rounds: after the first spawn, reuse each sleeping critic with `action=message`. They are
read-only: they read the room packet and evidence, write only their own critique file, and
report with `action=finish`.

## The critics

| Label | Seat | Judges | Weight |
|---|---|---|---|
| `critic-market` | Old Town listing broker for this price band | Does this bath read as at or above the comps a buyer will tour the same weekend? Is it dated, generic, or over-designed for the band? Uses `research/comps/`. | 0.30 |
| `critic-design` | Interior designer | Cohesion with the room's plumbing finish and fixture forms, with the other baths in the same unit, scale vs. room size, light, grout color/width, layout (stack/offset/herringbone), transitions, niche and curb details. | 0.25 |
| `critic-build` | Tile installer + GC | Substrate and flatness for large format, lippage/offset limits (1/3 offset max for long tiles), slope to drain with the chosen format, cut layout vs. Revit wall lengths/heights/openings, edge and trim profiles, waste factor, schedule risk. | 0.25 |
| `critic-cost` | Procurement | $/SF vs. carried budget, total room material cost incl. waste/trim/setting materials, lead time, stocking depth in Chicago, discontinuation risk, attic stock. | 0.20 |

Optional fifth seat when the owner asks for it: `critic-buyer` (target buyer persona at this
price band, e.g. move-up family vs. downsizer). Keep at most 4 critics active per round unless
the owner raises it; parallel chats share ChatGPT limits.

## Blind review

The prime writes a neutral copy of the current champion into the round's candidate set
(`rooms/<ROOM_ID>/board/round-NNN/candidates/<letter>.md`) with status, scores, round history
and any "champion" wording removed, next to the challengers. Every candidate gets a random letter
for the round (`A`, `B`, `C`); the mapping is stored only in `round-NNN/_key.json`.

Critics may read only: `board/BOARD.md`, `state/OWNER_FEEDBACK.md`, the room's `geometry.json`
and `plumbing.json`, the round's `candidates/` folder, `research/`, `inputs/` and manufacturer
pages. They must not read `_key.json`, `champion.md`, `history.md`, earlier round folders,
`state/ROOMS.json` or `state/LEDGER.md`.

## Scoring (each critic, each candidate)

Score 1-5 on each criterion in the critic's seat, then one overall seat score 1-5 with
one decimal. Each score needs a one-line reason that points to evidence (a comp id, a Revit
dimension, a manufacturer URL, a plumbing item). Then:

- `top_fix`: the single change that would most raise this candidate's score.
- `gate_flags`: any hard-gate failure below, with evidence.
- `confidence`: low / medium / high.

Critique file: `rooms/<ROOM_ID>/board/round-NNN/<critic-label>.md`. Finish report to the prime
(under 1,500 characters): scores per letter, gate flags, top fixes.

## Hard gates (any one fails the candidate, regardless of score)

1. Wet-area rating: wall tile in a shower/tub surround and floor tile in a shower must be listed
   by the manufacturer for wet areas (walls) or wet floors. "Floors/Walls" without "Wet Areas" =
   fail until a manufacturer document says otherwise.
2. Slip resistance: shower floors and bath floors need a published DCOF >= 0.42 (wet). Unknown =
   fail for floors.
3. Availability: discontinued, "while supplies last", or no current US distribution = fail.
4. Plumbing clash: `critic-design` severity HIGH on finish/form conflict with the room's
   selected plumbing (e.g. warm brass tones fighting brushed black chrome without intent).
5. Budget: room tile material cost > 125% of the carried room budget without an owner-approved
   upgrade note = fail. (If no carried budget exists, cost is scored, not gated.)
6. Geometry: a layout that cannot work with the Revit dimensions (e.g. 24x48 field with an
   unavoidable sliver cut under 3 in. at a focal wall, or a format that cannot slope to the
   drain type) = fail unless the candidate states the fix.
7. Owner veto: anything listed under "Do not use" in `state/OWNER_FEEDBACK.md`.

## Acceptance rule (champion vs. challenger)

- Weighted score = sum(seat score x weight), averaged over the round.
- A challenger replaces the champion only if it passes every gate AND beats the champion's
  weighted score in the same round by >= 0.25, AND no critic scores it below 3.0.
- Ties or small wins: keep the champion; record the challenger's best idea as a `top_fix`
  candidate for the next round.
- A champion that fails a gate is demoted immediately; the best gate-passing candidate takes
  over, or the room goes to `blocked` with the reason.

## Room status

- `seeded` — champion = current tile schedule v4 selection, not yet boarded.
- `active` — in board rounds.
- `stable` — champion defended in 3 consecutive rounds with weighted score >= 4.0. Stable rooms
  are reopened only by new evidence: owner feedback, a price or availability change, a new comp
  that shifts the market baseline, a Revit or plumbing change. Note the trigger in the ledger.
- `owner-review` — packet in `deliverables/`, waiting for the owner.
- `approved` / `rejected` — set only from `state/OWNER_FEEDBACK.md`.
- `blocked` — cannot proceed without an owner answer or missing input; say exactly what.

## Round protocol (prime)

1. Read `state/OWNER_FEEDBACK.md`, `state/ROOMS.json`, last ledger entry.
2. Pick focus: rooms with owner feedback first, then `blocked` rooms whose blocker can now be
   cleared, then `seeded`, then `active` rooms with the lowest score or oldest round. Batch
   2-4 rooms per round, preferably all baths of one unit type so cohesion can be judged.
3. Designer work (prime or a designer worker): for each focus room, write 1-2 challengers that
   each answer the previous round's `top_fix` items. Every product must have a
   `research/products/` evidence file (manufacturer URL, size, finish, wet-area listing, DCOF,
   price source and date, lead time if known). Quantities come from `rooms/<ROOM_ID>/geometry.json`.
   Write the neutral champion copy and `_key.json` (see Blind review).
4. Board: message the four critics with the round folder path, then end the turn: append a
   ledger entry, and in STATUS write `phase=2-board` and `blockers: board pending <rooms>`.
   Do not score with partial critiques. (With "wait for sub-agents" on, the next turn starts
   after the critics stop.)
5. Next turn, first: `agents action=status` once to collect reports. If any critique file is
   still missing, re-message only that critic and end the turn again as in step 4. When all four
   are in: score, apply gates and the acceptance rule, update `champion.md`, `history.md`,
   `state/ROOMS.json`, append the ledger entry, then continue with the next focus rooms in the
   same turn (back to step 1).
6. End every reply with the STATUS block.

## STATUS block (last thing in every prime reply)

```
STATUS round=NNN phase=<0-setup|1-comps|2-board|3-package|4-deepen>
rooms: <ROOM_ID>=<status> <champion id> <score> | ...
changed: <room: old -> new, why in <=10 words> | none
blockers: <owner questions, missing inputs> | none
next: <what the next round should take on, largest useful body of work>
```
