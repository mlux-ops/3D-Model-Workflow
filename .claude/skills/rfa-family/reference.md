# RFA family reference: catalogue of what the repo learned

Companion to `SKILL.md`. Compiled 2026-10-22 from every family build recorded in the repo,
its git history and the claude-mem session store. Each entry names where the evidence is.
Status words: proven (artifact or memory entry shows it worked end to end), partial (worked
with caveats), failed, untested.

## 1. Timeline of generations

| Date | Generation | How Revit was driven | Outcome |
|---|---|---|---|
| 2026-09-04 | Purist pilot, Tris | `pyrevit run` absolute path, `scripts/build_*.py` | Technical pass. User screenshot comparison found neck, cap, plate and lever-ratio gaps (`WORKFLOW.md:71-80`). No rebuild requested. |
| 2026-09-04..09 | Duo, Courcelette, Trinity, Oyster, Vera, AXOR v1/v2, Air Switch, beverage faucet, Focus X3, Gola, window | same | All `stage: complete`, zero warnings. Oyster rebuilt as v2 after user correction (full-depth diffuser, not a dome). Realistic view dropped from several packages. |
| 2026-09-13 | Malibu II RF | `prepare_malibu.py` derives builder; run stalled at Autodesk Device limit (E018) | Resolved after E019 (bowl underside) and E020 (loft overshoot). |
| 2026-09-15 | 700LSESF60, Kamden, Mila, Edge x3, KW2222 | `prepare_*.py` string-substitution from a sibling builder | All pass after Regenerate-before-bounds fix (Mila, 700LSESF60) and dropping a 0.018 in fillet (KW2222). `build_kamden.py`, `build_mila.py` later called proven. |
| 2026-09-17 | Cinch, Linear24, Preferred Tiles | C# `IExternalApplication` compiled with Roslyn, Idling trigger file, because pyRevit was absent on that checkout | Pass. Compile errors CS0009, CS1701, DLL lock. Route not used since. |
| 2026-09-18 | P01 pendant transfer test | Cloud kit (BLOCKED), then native `pyrevit run` 6.5.5; 3 attempts in 10.5 min | Attempt 1 `Element.Name` crash, repair 1 gate-logic bug, repair 2 pass. Visual ACCEPTED by reviewer. Drive verified. Defined the measured-gates builder shape. |
| 2026-09-22/23 | House of Troy USLEDZ15-76 | `pyrevit run` crashed at Revit startup (`0xe06d7363`, nothing written, ~9 min); then pyRevit pushbutton in the open Revit | Native pass after three API fixes. Visual miss: junction box mirrored to both arms. User declined fix. |
| 2026-09-23 | Cassia SF549315AGOP kit | Cloud session: geometry module, mock Revit API dry run, runner, verifier, packager, in-Revit button. Commit 823b0d5 fixed root resolution | **Never run natively.** `output/cassia/README.md:3` says RFA NOT YET BUILT. Do not cite as a native example. |
| 2026-09-23/24 | Lightology 12 fixtures, 14 RFAs | 8 xhigh workers planned; handoffs timed out; prime ran batched `execfile` sessions on `D:\Games\pyRevit-Master` at root `E:\Claude\3D-Model-Workflow` | 14/14 accepted and delivered (`output/lightology_20260923/ORCHESTRATION.md`, `release/drive_delivery.json`). All native work under one hour. |
| 2026-09-29..10-02 | Glass Clamp 180 (two duplicate kits on two branches) | `run_clamp.ps1` on PC MAXSPC, 3 native runs | 20/22 gates; `SketchEditScope` is project-only; formula ordering bug; flex dragged unlocked geometry. Not on main. |
| 2026-10-19 | Roccesco T609110 / T600110 Rev1..Rev4 | `run_roccesco.ps1` in an E: worktree; verifier exit code authoritative | Rev4 technical pass, 33 rays. Not in git; on Drive only. Overlay and photo-comparison sheets added as gates. |
| 2026-10-22 | Miele KM 3054-1 gas cooktop (first build under this skill) | One Opus agent at medium effort, `run_km3054.ps1` CLI route on this PC, 2 attempts of ~50 s each | Native pass, verifier exit 0, 32 parts, 25 family rays + 7 hosted rays, countertop top-face host. Attempt 1 passed its gates while exports still showed the template host; fixed by exporting from the project and pixel-checking. Visual verdict pending. `output/miele_km3054_1/`. |

## 2. Environment facts, by machine

Discover at run time; print what was found; exit 2 BLOCKED when absent.

| Fact | found workstation (this PC) | E: / MAXSPC workstation (cowey) | Notes |
|---|---|---|---|
| Checkout | `C:\Users\found\Documents\3\3D-Model-Workflow` | `E:\Claude\3D-Model-Workflow` (+ `.claude\worktrees\...`) | Dead roots still in files: `C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow` (every `scripts/build_*.py`), `C:\Users\mlux\Documents\GitHub\3D-Model-Workflow` (C# builders), `C:\Users\cowey\GitHub\...`. |
| pyRevit CLI | `C:\Program Files\pyRevit-Master\bin\pyrevit.exe` (6.5.5) | `D:\Games\pyRevit-Master\bin\pyrevit.exe` (6.4.0), fallback `%APPDATA%\pyRevit-Master\bin` | Engine IronPython 2.7.12 (`IPY2712PR`, .NET Core). |
| pyRevit CPython | `C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe` | same layout | stdlib only, no pip, no numpy or PIL. Use for verifiers. |
| System Python | `C:\Python314\python.exe` (numpy, pillow; no scipy, no fitz/pypdf) | same | `python` may be the Store alias. The `mlux\...Python312` path in the org skill does not exist. No PDF rasteriser on this PC; `pdftotext` exists. |
| Product pages | `curl` got HTTP 403 from mieleusa.com; Nimble Extract worked. Lightology pages fetched with the CoS fetch tools. | | Save every page, PDF and image under `references/<product>/` with a `SOURCE_MANIFEST.md`. |
| Revit | `C:\Program Files\Autodesk\Revit 2025\Revit.exe` | same | Builders assert `app.VersionNumber == '2025'`. |
| Template | `C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial\Generic Model face based.rft` | same | Also `Generic Model.rft` (nested bodies), `Generic Model line based.rft` (Gola), `Window.rft`. |
| pyRevit config | `C:\ProgramData\pyRevit\pyRevit_config.ini` | `C:\Users\cowey\AppData\Roaming\pyRevit\...` | `extensions paths add` writes here; needed elevation once. |
| Drive mount | `F:\My Drive\Folders\3D Model Workflow\3D Models` | `F:\My Drive\3D Model Workflow\3D Models` | Find with `Get-PSDrive -PSProvider FileSystem`; pick the one holding existing packages. Folder id `1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W` under `1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD`. |

## 3. API and IronPython gotchas (all hit in this repo)

1. `Document.GetElement(id).Name` raises `MissingMemberException: Name` on the .NET Core
   IronPython engine. Use `DB.Element.Name.GetValue(elem)` with a `SYMBOL_NAME_PARAM`
   fallback. Concrete types (`Material`, `Category`, `View`) bind fine. P01 attempt 1.
2. `FamilyParameter` has no `.Set`; use `FamilyManager.Set(param, value)`. House of Troy.
3. Angle parameters: `SetFormula(p, '30 deg')` is rejected as an invalid formula; use
   `fm.Set(p, math.radians(30))`. Length formulas `str(v) + ' in'` work. Lightology F01.
4. Edges below `Application.ShortCurveTolerance` (1/32 in) throw
   `Curve length is too small for Revit's tolerance`. Floor 0.035 in. House of Troy lens
   0.025 in, KW2222 fillet 0.018 in, Lightology F07 disc and F09 rounding.
5. `get_BoundingBox(None)` returns None on fresh `FreeFormElement`s until `doc.Regenerate()`.
   `HostObjectUtils.GetSideFaces(wall)` is empty until `project.Regenerate()`. Regenerate
   outside a transaction raises `Modification of the document is forbidden`.
6. Display bounding boxes understate revolved and circular parts. Measure with
   `Solid.IntersectWithCurve` rays or triangulated faces plus sampled analytic edges
   (`output/lightology_20260923/tools/native_fixture_support.py:70-84`).
7. Loft through uneven or near-duplicate sections overshoots the inputs (Malibu E020).
   Periodic profiles self-intersect (`CreateLoftGeometry` error, Lightology F11). Use
   monotonic or symmetric sections, or matched arc sections.
8. Revolve profiles: every revolve that built here was counter-clockwise in (r, z).
   Clockwise behaviour is untested.
9. Parent-instance bounding box of a nested pendant grows with cord length by design.
   Gate on measured drop minus cord (body span), not instance height. P01 repair 1.
10. Face-based family on a downward face: local +Z points down in world. Body local z=0
    is the top.
11. `System.Byte` colour channels and numpy scalars are not JSON serialisable; cast.
12. `SketchEditScope` only works in project documents, not family extrusions. Glass Clamp.
13. Formulas set from an unordered dict evaluate against stale dependents; make locked
    parameters constant formulas with no inter-formula dependency. Glass Clamp run 3.
14. Flex tests drag unconstrained geometry with the nearest moving reference; lock fixed
    parts to stationary references. Glass Clamp run 3.
15. `doc.Paint` inside a family is baked into loaded face material ids; check face
    `MaterialElementId`s in the loaded geometry, not project `GetMaterialIds`. Tris.
16. `Revit writes NAME.0001.rfa` backups on re-save even with `MaximumBackups = 1`; they
    are distinct content per attempt, not duplicates (SHA-256 checked on P01).
17. `OpenAndActivateDocument` inside an `Idling` handler fails: switching active documents
    is not allowed during API events. C# route only.
18. `validation.json` shape traps: `configs` is a dict keyed by configuration; an empty
    `failed_gates` is still a truthy dict. Test emptiness per configuration.

## 4. Gate catalogue (copy the set that fits the fixture)

**NativeFixture helper** (`output/lightology_20260923/tools/native_fixture_support.py`,
used for 14 accepted RFAs): reopened; category Lighting Fixtures; `actual_face_host`
(`instance.Host.Id == host.Id` and `HostFace` set); orientation normal dot 1; dimensions
within 0.025 in of expected; every material parameter substitution reaches faces; CCT
parameter; zero family, reopened and project warnings; at least 5 exported views. Raises
`Failed native gates: [...]` on failure.

**P01 pendant** (`output/model-transfer-tests/candidate-20260918-01/pendant/build_pendant.py:729-766`,
8 gates, two configurations in one run): fresh RFA reopen and category; native overhead
hosting and orientation (hangs below floor bottom face); 9 named dimensions by ray within
0.01 in; saved default Total Drop in reopened type, placed instance and after flex;
measured flex rows (formula within 0.01, measured within 0.1, body span constant);
materials reach nested geometry (faces counted); zero unexplained warnings; visual exports
present. `verify_run.py` re-derives all of it and exits non-zero.

**Independent final review** (`output/lightology_20260923/tools/final_native_review.py`):
fresh host project per RFA, `FAMILY_HOSTING_BEHAVIOR == 5`, mount plane within -0.01..0.02,
appearance values identical in family scope and after `LoadFamily`, texture files on disk,
SHA-256 of the RFA equals the reviewed hash. Every release step re-asserts the hash
(`verify_release_native.py`, `make_release.py`).

**Roccesco Rev4** (claude-mem 20770, 20915; Drive folder only): 16 gates including hosted
wall placement with +Z leaving the wall and family +Y world up, projection, lever ray
probes, Luxe Gold RGB (196,165,120), plus `overlay_check.py` (model silhouette over the
spec-sheet vector outline extracted with PyMuPDF) and `compare_photos.py` (product photo
beside the Revit export, cropped to content, same height; compare proportions only).

**Cassia** (`output/cassia/README.md:41-56`, mock-proven only): 37 measurement rays,
3 arm angles, 27 clearance rays, fitter covers glass opening, hosted drop and spread. The
verifier also refuses a stale report (`logs/run-start.txt` newer than `started_utc`).

## 5. Geometry techniques by fixture (copyable)

| Need | Look at |
|---|---|
| Wall light, single file, cleanest template | `scripts/build_kamden.py` (rewrite `ROOT`) |
| Nested body plus adjustable cord with formula parameters | `scripts/build_mila.py`, `build_pendant.py` (`Assembly Offset = Cord Length + 1.45 in`) |
| Shared helper with gates, views, materials, CCT | `output/lightology_20260923/tools/native_fixture_support.py`; tiny builders `f03..f06` (23-64 lines) |
| Fan blade loft through 3D stations | `output/lightology_20260923/f01_816712/build_f01_816712.py` |
| Hollow flared glass revolve with inner diffuser | `f03_1241670/build_brenta.py` |
| Swept cord, arch arm, Boolean shade | `f04_1149899/build_forked.py`, `f09_1254269/build_madame.py` |
| Bound bitmap that must resolve on reopen, self-illum filter map | `f10_1242580/build_covet.py:92-111, 189-202` |
| Loft minus loft hollow crystals | `f11_1476233/build_mizu.py` |
| Hollow sphere by two Boolean differences | `f12_813073/build_f12_orbel.py` (RFA is under `native/`) |
| Two finishes from one script | `f05_1441643/build_dimple.py`, `f07_833919` |
| Copying manufacturer solids from a supplied RFA | `scripts/build_axor_angled_v2.py` (`SolidUtils.CreateTransformed`) |
| Line-based family with void cut | `scripts/build_gola.py`, `add_gola_cutting.py` |
| Window with wall-cut volume check | `scripts/build_window.py` |
| Appliance on a countertop top face: parts above and below the face, open grate lattice as unioned plates with an "opening exists" ray, Specialty Equipment category, pixel-checked exports, line-anchored packager check | `output/miele_km3054_1/source/` (`build_km3054.py`, `km3054_geometry.py`, `verify_km3054.py`, `compare_km3054.py`) |
| Geometry module shared by builder, dry run and verifier | `output/cassia/source/cassia_geometry.py` |
| Mock Revit API dry run (what it proves and does not) | `output/cassia/source/mock_revit_dryrun.py` |
| Runner with preflight, stale guard, RFA written line | `output/cassia/run_cassia.ps1`, `run_pendant.ps1` |
| In-Revit pushbutton that finds its builder | `output/cassia/pyrevit/Cassia.extension/.../BuildCassia.pushbutton/script.py` |
| Batched native runs in one session | `output/lightology_20260923/tools/run_completion_batch_v5.py` |
| Mesh export for off-Revit rendering | `tools/export_native_meshes.py`, `render_native_studio.py` (Blender Cycles) |
| Release manifest, catalogue, hash chain | `tools/make_release.py`, `release/MANIFEST.json`, `PRIME_REVIEW.md`, `FIXTURE_CATALOG.md` |
| Handoff from a session without Revit | `.../pendant/HANDOFF.md`, `SCORECARD.md` |

Material conventions: GenericSchema clone; `generic_diffuse` from render pixels set below
the median (P01 brass 186,166,112; Cassia Aged Gold p60); glossiness ~0.3-0.45;
reflectivity 0.08 / 0.12 at 0 and 90 deg; glow luminance observed 35-100 on diffusers (one
Mizu emitter at 1200), CCT 2700-3000 K; `generic_is_metal` usually false. Chrome uses the
library `Chrome - mirror` asset; refuse a grey substitute.

## 6. Run-state clues

| Clue | Meaning |
|---|---|
| pyrevit log `Working Directory: ...\Temp\<guid>` and no script output | Relative script path; nothing ran (E026). |
| Revit journal `0xe06d7363` after licence init, before the pyRevit command | CLI startup crash; use the in-Revit button. |
| Revit window shows Device limit reached or Sign in | Licence concurrency; user must clear it. Low CPU, no journal progress. |
| `validation.json` absent after ~2 min | Script never started. |
| `stage` other than `complete` | Where it died; `error` holds the traceback. |
| `technical_pass: false` with `gates` map | Which gate; do not hand-edit. |
| Verifier exit 2 | Prerequisite or report missing: BLOCKED. |
| `STALE report` from verifier | Old JSON older than `run-start.txt`. |
| `*.000N.rfa` present | Re-save over an earlier attempt. |
| Realistic export washed out or black chrome | Viewport limitation, not geometry. |
| Drive connector search shows nothing after Desktop upload | Index lag; fetch metadata by file id (v3 field `name`, no md5). |

## 7. Orchestration lessons (Lightology, 2026-09-23/24)

- Planned: one xhigh worker per fixture, eight concurrent, prime grants one serial native
  Revit slot, protocol READY_REVIT then VISUAL_REVIEW then RESULT / CHANGES / VALIDATION /
  BLOCKERS. Actual: worker messaging returned `No sub-agent run is active` and
  `AGENTS_BUSY`, browser handoffs timed out, one worker moved a 30 KB builder through 22
  base64 segments and corrupted it. The user ended it with "no further worker wakeups,
  message handoffs, or new agents".
- What then worked: prime wrote tiny builders on a shared helper, ran them as batches
  (`execfile` per builder with try/except and incremental JSON) in one Revit session,
  18 s to 35 s per fixture, all native work in under an hour, then an independent review
  pass over all 14 files, hash-chained release, Drive verification by id.
- Keep: disjoint output folders per fixture, append-only error logs, technical and visual
  gates independent, resolved option ids in the catalogue, read-only manufacturer RFAs.
- Residue to know about: `ACCEPTANCE.json` still says IN_PROGRESS (stale; real records are
  `prime_visual_review.json`, `release_native_validation.json`, `release/drive_delivery.json`);
  the checked-in `f09` builder does not match the shipped RFA name or width; the batch
  error chronology was appended to the E: copy of `PROJECT_MEMORY.md`, not main.
- Cost evidence: `origin/docs/agents-memory-2026-09-26:AGENTS.md` records the effort
  trial (Sonnet 5.5 high passed every native gate; xhigh 2.7x, max 5x, no gain) and the
  grep-not-read rule for project memory. Not merged to main as of 2026-10-22.

## 7a. Writing files on this workstation

- Never pass Python that contains backslashes through a Bash heredoc: the double
  backslashes collapse, `\3` becomes a 0x03 byte and `\c` a control character. It bit the
  Adella memory edit (sed) and the Miele delivery record (heredoc, 2026-10-22). Write a
  `.py` file with the Write tool and run it; rescan for bytes below 0x20 afterwards.
- Bash mangles `$ps` and `$_` in inline PowerShell; use the PowerShell tool for process
  work. `PROJECT_MEMORY.md` is CRLF; append in binary mode.
- A complete `validation.json` with a Revit process still alive means the exit hung, not
  the build (Miele attempt 3). Verify the artifacts, then stop only the PIDs whose start
  time matches the run.

## 8. Untested or open

- Cause of `0xe06d7363` on `pyrevit run` startup. Unknown; not reproduced on purpose.
- Clockwise revolve profiles; `FamilyManager.GetAssociatedFamilyParameter` and
  `Application.ShortCurveTolerance` reads (Cassia uses them, mock only).
- Cassia SF549315AGOP native run. The similar LP549448AGOP in Lightology f08 did run.
- Whether `F:\My Drive\3D Model Workflow` on this PC (a repo mirror) is stale.
- Glass Clamp final native result; two kits unreconciled on two branches.
- Roccesco sources exist only in an E: worktree and on Drive; not in git.
