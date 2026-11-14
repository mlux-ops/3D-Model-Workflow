"""Phase 15: close phase15_results.md (status line, J6 outcome, findings, owner items, file list). Run from the plan folder."""
p = "phase15_results.md"
s = open(p, encoding="utf-8").read()
s = s.replace("Status: IN PROGRESS since 23:41 on 2026-11-13 (Central).",
              "Status: DONE at 23:59 on 2026-11-13 (Central). The withdrawn hotel is gone from the project: its level, its 71 assets, "
              "its Variant Manager list and its hiding of three existing objects. The existing buildings and the empty lot on its land "
              "show again, as surveyed, and three check views plus one more agree with the pictures made before Phase 13. Nothing is pushed. "
              "Phase 11 resumes next.")
old = "compared with the Phase 12 ground truth in `review/phase12/` | PENDING |"
new = ("compared with the Phase 12 ground truth in `review/phase12/` | DONE 23:58. Four real-time pictures at 3840 x 2160, one at a time, "
       "with the same 24 mm camera and fixed exposure as Phases 8, 10 and 12 (script `j6_view.py`, record `views/runs.jsonl`): "
       "S2 (Wieland Street from the south-west, Phase 8's station camera) 12.4 s, D1 (roof deck, Phase 8's design-view camera) 7.7 s, "
       "AIR (aerial from the south-east over Wells Street) 6.2 s, RDE (1529's roof deck looking east over the rear) 6.1 s. "
       "`r.RayTracing.Nanite.Mode` read 0 before, during and after each. The level had been open 13 minutes before the first. "
       "Comparison under Findings. Free commit read 30.1 to 33.2 GB before each render. During each render it dipped to 25.0 to 25.5 GB "
       "for a few seconds, below the 30 GB line, with the editor at up to 25.0 GB (`memory_log_phase15.csv`, 50 lines, 23:54 to 23:58). |")
assert old in s
s = s.replace(old, new)
s += open("review/phase15/scripts/close_results_body.md", encoding="utf-8").read()
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
