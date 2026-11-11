# 1529 Wieland bathroom tile loop — runbook

## How it works

```
             owner (you) ──► state/OWNER_FEEDBACK.md, chat messages
                                  │
Loop helper ──next prompt──► PRIME chat (ChatGPT via CoS) ──writes──► workspace files
 (sees only chat text        │   │  reads Revit (plugin, read-only), plumbing, tile v4
  + STATUS block)            │   │
                             │   ├─ comps worker   → research/comps (Old Town market baseline)
                             │   ├─ designer       → challengers per room, product evidence
                             │   └─ critique board (blind, scored, gated)
                             │        critic-market · critic-design · critic-build · critic-cost
                             ▼
                 champion / challenger decision → ROOMS.json, LEDGER.md, STATUS block
```

- One round = one board cycle over 2-4 rooms. Champions change only when a challenger passes
  every hard gate and wins by >= 0.25 weighted. Rooms that hold for 3 rounds at >= 4.0 lock as
  `stable` and reopen only on new evidence. Once rooms are stable the loop moves to owner
  packets and deepening work (tiers, takeoffs, elevations, renders, sample list, re-checks), so it
  keeps producing value instead of reshuffling tile.
- The Loop helper never sees tool results, only chat text. The STATUS block at the end of each
  prime reply is what lets it write a good next prompt; keep it.
- All state is on disk, so a 30-minute turn rotation, Compact & Resume, or a restart loses
  nothing: the next round re-reads `state/`.

## One-time setup

1. Inputs (see `inputs/README.md`):
   - Fill the price band in `state/OWNER_FEEDBACK.md` (or `inputs/PRICE_BAND.md`). This is the one
     thing only you can give; without it the market critic works against "band unconfirmed".
   - Put the plumbing selections (Smartsheet export and/or `1529_Wieland_Fixtures_v3_2.pdf`) in
     `inputs/plumbing/`, and `HANDOFF_1529_Wieland_Tile.md` in `inputs/tile/`. If ChatGPT can read
     them through your Google Drive / Smartsheet connectors instead, note that in `inputs/README.md`.
2. Revit: keep Revit open with `25-006 1527 N Wieland` and the codex-native-revit add-in loaded.
   No CoS plugin is needed: the loop runs `tools/revit_read.py` (read-only wrapper around the
   native bridge on 127.0.0.1:49327) through exec_command. See `REVIT.md`.

## Overnight checklist

- Leave the PC on and plugged in; CoS "keep awake" is on. Leave Revit open (no modal dialogs:
  a dialog makes bridge jobs queue). Do not close the prime chat's browser tab.
- ChatGPT usage limits: if two chats hit the limit within 10 minutes CoS pauses automatic sends
  and resumes later on its own; nothing to do.
- A 2-minute silence reload can interrupt a turn early in a chat (seen 2026-11-06 10:28 UTC,
  before CoS had read the chat's model). CoS resent the Continue itself and the loop recovered.
- Health watch: a Claude Code session runs `tools/loop_health.py` every 15 minutes (a Haiku
  scout runs it; the main model only wakes up to fix an UNHEALTHY result). It checks that CoS is
  writing its log, the prime chat's Loop switch is on, a tool call happened in the last 25
  minutes, no stuck/pause markers appeared, and the Revit bridge answers. The schedule lives only
  in that session: it ends when the session closes and expires after 7 days.
- In the morning: read the last STATUS block in the chat and `state/LEDGER.md`.
3. CoS settings for this chat:
   - Mode: **Loop**. Objective: paste PROMPTS.md section A.
   - Settings -> Loop prompt: **leave at default** (it is global, shared by every Loop chat).
   - When to continue: "Also after the turn" (simplest), or "Session Finish only" for Pro.
   - Sub-agents on; workers per family **6** (default 2 is too low for comps + designer + 4 critics);
     **wait for sub-agents on**, so the next round only starts after the board reports.
   - Note: workers per family, wait for sub-agents and chats at once are app-wide settings, not
     per chat, so they also apply to your other prime chats while this loop runs.
   - Chats at once: 5 or lower. ChatGPT access limits are shared; if two chats hit the limit
     within 10 minutes CoS pauses all automatic sends. Do not use workers to get around limits.
4. Start a new chat in the CoS project **3d-model-workflow** (`E:\Claude\3D-Model-Workflow`) and
   send PROMPTS.md section B. The repo's root AGENTS.md points every chat in that project here.

## Steering while it runs

- Add verdicts to `state/OWNER_FEEDBACK.md` (approve / reject / revise / do-not-use /
  question-answer). It is read first every round and outranks everything.
- Or type straight into the prime chat; a human message is authority for the helper too.
- To pause: switch Loop off. To end: switch Loop off and archive the workers.
- Look at `state/LEDGER.md` for the round history and `deliverables/` for owner packets.

## What to expect per phase

| Phase | Output | Typical rounds |
|---|---|---|
| 0 setup | Revit identity check, room list, geometry/plumbing per room, seeded champions | 1-2 |
| 1 comps | `research/comps/COMPS.md` + `comps.json` (12-20 cited comps) | runs alongside 0 |
| 2 board | challengers, critiques, champion changes, gate failures resolved | ~3-6 per room group |
| 3 packets | per-room owner packet: scheme, rationale vs comps and plumbing, cost, risks | as rooms go stable |
| 4 deepen | good/better/best, takeoffs, layout elevations, concept renders, sample kit, re-checks | ongoing |

## Known starting gaps (from the 2026-10-01 audit)

- Clara Caviar (PH/TX Bath 4 niche bands): manufacturer page lists Floors/Outdoor/Walls, not Wet Areas.
- Tones Opal (PH Bath 3 tub walls): no product-specific wet-area approval found.
- Cortar Bone Ribbed and Clay Ribbed/flat: order quantities not confirmed.
- Sinks unselected in PH Bath 3, TX Bath 2, TX Powder 2: tile there stays provisional; the loop
  will not pick basins.

## Address note

Older Revit/Unreal tooling on this workstation is named "1527 Wieland" while the finish documents
are 1529 Wieland. Round 0 records the Revit model's project info and stops Revit work if the
model is not 1529.
