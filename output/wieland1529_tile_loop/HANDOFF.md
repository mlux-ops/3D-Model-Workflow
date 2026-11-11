# 1529 Wieland Bathroom Viewer — Standalone Technical and Architectural Handoff

**Transfer date:** 2026-11-08  
**Working project root:** E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop  
**Principal existing deliverable:** E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\index.html  
**Transfer condition:** The project owner ordered STOP AND HAND OFF on 2026-11-08. All previous instructions to continue viewer rounds, run checks, obtain review verdicts, or begin more development were superseded. This document conveys the work to a standalone coding agent. Its potential improvements are a future backlog, not authorization to keep modifying the viewer during this stopped transfer.

This document is intentionally self-contained. The recipient has an ordinary Windows coding environment, PowerShell or another shell, Python, Node.js and Chrome. No special chat tooling, delegated reviewers, automated workers, agent loop or historical ledger protocol is required. The existing standalone viewer is the artifact to preserve. Do not treat inferred architectural geometry as native Revit room solids, or illustrative fixtures as verified manufacturer installations.

## 1. Project goal and owner priorities

Build and maintain an interactive, offline, source-defensible 3D bathroom viewer for the **same building identified as 1527 and 1529 N Wieland**. The native Revit source document is **25-006 1527 N Wieland**. The viewer covers **13 bathroom types and 26 distinct physical A/B instances**, preserving their different room/adjacency relationships. It is intended to show convincing high-end residential interiors rather than isolated tile swatches, wireframes, detached product proxies or a collection of unconnected source boxes. The owner cited approximate residence price contexts of **$2.8 million penthouse** and **$2.7 million triplex**; these are presentation context, not trade pricing.

Required design and technical principles:

- Authentic source-derived plan boundaries, native wall positions, heights and thicknesses; preserve hosted doors and windows, and distinguish native wall boxes from derived wall-face footprints.
- Correct source-attributed A/B rooms and adjacent context; do not merge physically separate rooms to simplify display.
- Source-supported fixture positions only. When a selected or diagrammatic fixture cannot be installed defensibly, retain an explicitly labeled **UNLOCATED** 2D locator or neutral study rather than inventing a drain, basin, niche, pedestal, support, clearance, rough-in or wall-carrier height.
- Preserve all frozen tile, stone, product, fixture-program, SKU, price, quantity, score and champion selections. Match nominal tile sizes and show plausible grout, relief, light response and retained wood where applicable.
- Visually credible porcelain, metals, plaster, stone, timber, reflection/contact and architectural lighting, without claiming that generic meshes represent actual Revit family solids or manufacturer geometry.
- Usable **Full Bathroom**, **Wet Zone Study**, **Revit Context** and **Focus View** modes, with framing that makes source geometry and selected finishes legible.
- Room and A/B selectors, orbit/pan/zoom/reset, material and provenance inspectors, source-trace overlays, section/cutaway controls, image gallery and deep links.
- A fully self-contained HTML viewer that opens in Chrome from a local file path without a web server.

**Product-selection freeze:** The owner ended tile-selection rounds on 2026-11-07; subsequent work was viewer-only before the newer STOP order. Do not reopen product research, vendor comparison, approval, board scoring, sample orders, procurement or correspondence. The frozen data lives at:

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\picks.json

## 2. Current viewer: room-by-room state, functionality and visual quality

The current HTML contains source-based wall enclosures and source-registered studies for all 13 types, but it is **not a construction-complete, manufacturer-validated or fully photorealistic as-built model**. The room descriptions below distinguish what is visually present from what remains unverified.

| Room type | A/B physical instances | Current visible representation | Open hold / caveat |
| --- | --- | --- | --- |
| **PH-PRIMARY** | 304A / 304B | Drawing-registered enclosure, source wall/hosted-opening and native Countertop-category context, neutral primary wet studies; selected linear drain *type* in metadata | Shower installation, primary basin and drain coordinates are not independently located; major drawing/envelope area conflict |
| **PH-BATH2** | 305A / 305B | Source-based enclosure, frozen wet wall/floor finish, source-bounded countertop, nominal selected Duravit tub study with improved generic hollow porcelain | Tub is a visualization, not actual manufacturer family solid; exact drain, flange, depth and installation elevations unverified |
| **PH-BATH3** | 307A / 307B | Enclosure and frozen wet-finish surfaces; source drawing tub references and wet zone presentation | Tub versus walk-in is **UNSELECTED**; do not construct an installed tub/shower on that basis |
| **PH-BATH4** | 311A / 311B | Source-based shower/floor/selected wet finish and distinct adjacent 310 context, source-bounded countertop presentations | 311/310 attribution and 26.98/27.08/35 SF conflict; preserve one historic shared 40.2 SF LEVEL/POINT pool without double-counting |
| **PH-POWDER** | 405A / 405B | Retained source-registered wood floor, selected dry vanity accent, native bounded countertop, modeled plaster/corner depth and lighting | Both basin 3D bodies intentionally **UNLOCATED** after native countertop containment failure; preserve native insertion ring, do not move the sink |
| **PH-WC** | 314A / 314B | Source-based WC enclosure, inherited neutral floor, source-gated generic porcelain toilet and more legible exterior Focus camera | No independent wet wall/floor pick or certified bowl support, actual installation height or manufacturer geometry |
| **TX-PRIMARY** | 202A / 202B | Source-enclosed primary with neutral unresolved wet program, native category countertop surfaces and generic WC where supported | Basin unsupported and suppressed; primary shower not installed; major drawing/envelope area conflict |
| **TX-BATH2** | 205A / 205B | Source-based wall and floor finishes, nominal selected Duravit tub and new porcelain inner surface, native category vanity/countertop | Generic tub is illustrative and not a certified family or drain/rough-in location |
| **TX-BATH3** | 207A / 207B | Source-enclosed room, frozen wet finish on source-appropriate tub-side wall, source-supported fixture studies | Tub-versus-walk-in program **UNSELECTED**; diagrammatic bathing reference is not approval for installed fixture geometry |
| **TX-BATH4** | 007A / 007B | Source enclosure, selected tile context, native toilet/countertop context | Selected nominal Duravit **59 × 29.5 in** tub must remain **2D UNLOCATED**; no unsupported installed 3D tub |
| **TX-POWDER** | 102A / 102B | Retained wood, authentic native **0.125 ft** countertop slab and neutral room lighting/plaster | Wall is **NO PICK**; no invented cabinet, faucet, basin or selected accent wall |
| **TX-POWDER2** | 010A / 010B | Retained wood, frozen selected accent wall and native-bounded countertop; selected Hansgrohe deck faucet appears as metadata | Basin **UNSELECTED**; faucet has no verified installation point; do not create installed tap/basin |
| **TX-WC** | 203A / 203B | Native WC enclosure, inherited neutral floor, same shared source-gated generic porcelain and exterior Focus treatment as PH-WC | No verified toilet manufacturer body, wall carrier, mounting height or rough-ins |

**Current interactive functions:** 13-room selector; physical A/B switch; Full Bathroom, Wet Zone Study, Revit Context and Focus View; overview and finish-focused cameras; orbit, pan, zoom, reset; reversible native-wall cutaway/section and supported ghost ceiling; source evidence/inspector; material/product info; A/B comparison; gallery, deep links and standalone offline Chrome operation. Revit Context may show registered **inferred wall-face polygons**, never certified native OST_Rooms solids.

**Visual assessment:** Architectural and source fidelity is substantially better than a generic technical diagram: hosted openings, sided wet finishes, optically credible wood, tile atlases, plaster and native-bounded countertops now read as coherent enclosures. Some WC and powder spaces have stronger depth and more visible ceramic forms following the latest improvements. However, large undecorated neutral surfaces still dominate some primaries and WCs, generic sanitary meshes lack independently proven contact/support or family detail, and deliberately unselected or unlocated bathing fixtures leave some rooms sparse. Vendor images and rendering shaders are **digital proxies**, not physical sample approval. The model is suitable for interactive design review with explicit uncertainty labels, **not** manufacturer-certified construction coordination or final buyer photorealism.

### Recent architectural integrity correction

In PH-BATH4 / 311B, a separate adjacent **310B Bath4** native Countertop-category element **16438253** (Revit receipt **9aed5e0a-8a96-41f2-a3bc-4ffb1b305d48**) previously received an illustrative top extending 0.095 ft (1.14 in) above its native category vertical bounds. The revised top caps its thickness within the native bounds and its Chrome receipt reports **0.0 ft** above category maximum; category **ARCH_R070_310B_NATIVE_BOUNDED_LID**. Do not regress the distinction between 311B and 310B or stretch any decorative surface beyond its native category AABB.

PH-POWDER R056 contained a separate source-position issue: countertop element **16018680** at 405A and **16019018** at 405B cannot contain the full illustrative generic basin footprint at the actual plumbing insertion. The viewer leaves a small category **ARCH_NATIVE_BASIN_UNLOCATED_LOCATOR** and suppresses fictitious 3D basins rather than moving the native plumbing points.

### Latest targeted rendering work

The most recent builder retains previous wall/door/camera/source-geometry work and adds dry-room plaster face/corner light studies, retained wood microrelief, only native-bounded countertop optical highlights, a tighter source-oriented WC Focus camera, a continuous neutral generic WC ceramic shell, selected Bath2 generic tub inner porcelain and a source-registered Context locator. Important internal categories or functions in the authoring JavaScript include:

- **ARCH_R070_PLASTER_FACE_STUDY**, **ARCH_R070_CORNER_DEPTH_STUDY**; r070DryPhotoMaterial.
- **ARCH_R070_WOOD_FLOOR_MICRORELIEF**; makeRetainedWoodStudy and drawR070RetainedWoodOptical.
- **ARCH_R070_NATIVE_COUNTER_SURFACE_STUDY**; drawR070NativeCounterSurfacePhoto.
- **ARCH_R070_CONTEXT_REGISTERED_LOCATOR**.
- **R070_CONTINUOUS_CERAMIC_SHELL** (nonmanufacturer WC body) and **R070_GENERIC_TUB_INNER_PORCELAIN** (nonmanufacturer tub inner surface).

These are identifiable source/visualization categories, not evidence that their physical dimensions or attachments were installed as manufactured components.

## 3. File map: authoritative inputs, editable sources and generated outputs

**Root:** E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop

| Absolute Windows path | Classification and purpose |
| --- | --- |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\index.html | **Generated principal deliverable**; bundled offline HTML, not the primary place for source edits |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\viewer3d_scene_v2.js | **Editable authoring source** for current Three.js scene, presentation, camera, geometry and source/selection labels |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\build_viewer3d_index.py | **Build-script source** assembling current offline index.html |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\picks.json | **Generated, frozen input/output dataset** for 13 room types and 26 instances; DO NOT edit selections or program decisions |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\ACCURACY.md | **Maintained source-fidelity/provenance document**; distinguishes native, derived, illustrative, UNLOCATED and retained states |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\assets\ | Offline viewer JS/textures; **folder to inspect**, exact item-by-item inventory was not verified in this transfer |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\vendor\ | Vendor/manufacturer reference images; **folder to inspect**, exact per-image inventory not verified |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\viewer3d_architecture_r043.py | Historical **geometry-generation script**, not edited in latest pass; confirm existence before reuse |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\state\ROOMS.json | Room/program tracking data; do not recalculate or rewrite frozen selection state |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\rooms\<ROOM-ID>\geometry.json | **Per-room derived/registered geometry** convention; exact coverage of all individual files was not re-enumerated |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\rooms\<ROOM-ID>\plumbing.json | Per-room plumbing evidence/program convention; preserve native/illustrative classification |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\rooms\<ROOM-ID>\champion.md | **Frozen historic owner/product selection** for each room, where present; not an editable approval queue |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\inputs\TRADE_QUOTES.md | Historic procurement/pricing reference; no vendor or purchasing round is authorized |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\REVIT.md | **Access instructions** for the read-only Revit interface, supported commands and secure token reference |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\tools\revit_read.py | **Read-only Revit wrapper** (use only approved read operations) |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\AGENTS.md | Prior workspace conventions; any obsolete agent/round instructions are superseded by this standalone handoff |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\state\OWNER_FEEDBACK.md | Owner decisions and **2026-11-08 STOP AND HAND OFF** order; preserve unchanged |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\board\BOARD.md | Historical board research/selection decisions; frozen, not a current review process |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\state\LEDGER.md | Historical activity record; **not a required dependency for continuing this project** |
| E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r066_focus\protected_before.json | Historical protected-original comparison receipt only; do not recreate periodic SHA manifests |

The <ROOM-ID> placeholder above is one of: PH-PRIMARY, PH-BATH2, PH-BATH3, PH-BATH4, PH-POWDER, PH-WC, TX-PRIMARY, TX-BATH2, TX-BATH3, TX-BATH4, TX-POWDER, TX-POWDER2, TX-WC. A/B physical instance identifiers are listed in Section 2. Revit-native identifiers, family-category bounding boxes and receipts are **source facts**; floor polygons derived from wall faces, camera staging, optical slabs, ceiling ghosts and generic fixtures are **derived presentation layers**. Preserve and label that distinction.

**Change discipline for a future authorized edit:** normally edit the scene authoring JavaScript and any specifically related nonfrozen source; rebuild HTML with the existing builder; use a narrow Chrome inspection for affected rooms. Do not hand-edit generated HTML as the only change, or regenerate frozen pick/quantity data as an incidental consequence. There is no verified complete inventory for the asset/vendor folders, nor proof that every historical source-generation file still exists; inspect only when needed.

## 4. Rebuild, offline Chrome testing and known receipts

**Do not execute these procedures as part of the stopped 2026-11-08 handoff.** They describe the known working procedure for the future coding agent once separately authorized to change the viewer.

### Environment

- Windows and **PowerShell 5.1** were used in the last workflow. PowerShell 5.1 does not implement modern shell **&&** / **||** separators; use one command per line or semicolons.
- Python **3.12** is documented at **C:\Users\mlux\AppData\Local\Programs\Python\Python312\python.exe**. Historical successful scripts used the command **python -B**, but the precise PATH-resolved Python executable was not independently recorded for every run.
- Python package dependencies observed: **playwright** (automated Chrome) and **Pillow/PIL** (image comparisons). Standard library modules include json, pathlib and hashlib. No authoritative installed package-version list was recorded; do not invent one.
- **Node.js** is used for the JavaScript syntax check. The final HTML bundles its required local Three.js/texture assets; a running HTTP server is **not** required.
- Chrome executable historically used: **C:\Program Files\Google\Chrome\Application\chrome.exe**. Targeted Playwright runs used flags **--enable-unsafe-swiftshader --use-angle=swiftshader --no-sandbox** (software rendering), a **1480 × 900** viewport and device scale factor **1**.

### Rebuild: exact previously working PowerShell commands

~~~powershell
Set-Location 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop'
node --check 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\viewer3d_scene_v2.js'
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\build_viewer3d_index.py'
~~~

Output overwrites the generated offline deliverable at:

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\index.html

Latest recorded successful build output: **PASS HTML viewer; 5,619,798 characters; 13 rooms**. Open the full Windows HTML path in Chrome; the expected operational URL is a local **file://** address, not localhost. Do not assume a new server, build framework, package install or deployment is needed.

### Targeted Chrome evidence scripts (historical, run only for relevant future changes)

**Dry powder/WC focus (A/B):**

~~~powershell
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_dry_baths_browser.py' before
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_dry_baths_browser.py' after
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_source_receipt_finalize.py'
~~~

Results and physically captured images were stored at:

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_focus\before\
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_focus\after\
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_focus\after\RESULT.json

**PH4 310B source bounded lid and shared TX-WC:**

~~~powershell
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_310b_source_lid.py'
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_tx_wc_smoke.py'
~~~

Receipts:

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_focus\after\REVIEWER97_310B_FIX.json
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_focus\after\PH-BATH4_311B_310B_LID_R070.png
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_focus\after\TX_WC_R070_SHARED_RESULT.json

**Shared generic WC and selected PH/TX Bath2 porcelain:**

~~~powershell
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_fixture_continuity_browser.py' before
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_fixture_continuity_browser.py' after
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_fixture_continuity_finalize.py'
python -B 'E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\qa_r070_fixture_cross_program_smoke.py'
~~~

Receipts and screenshots:

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_fixture_continuity\before\
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_fixture_continuity\after\
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_fixture_continuity\after\RESULT.json
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\r070_fixture_continuity\after\R070_CROSS_PROGRAM_RESULT.json

### Latest actual check results and limitations

- Eight A/B physical dry-room cases and **26** final dry-room after images: targeted source-aware **PASS**.
- PH4 311B/310B native Countertop-category test: **PASS, 0.0 ft category overrun**.
- TX-WC 203A/B shared-code review: **PASS**, four physical images.
- Eight A/B generic WC/selected Bath2 instances and **18** after images: targeted **PASS**; **16** fixture-region comparisons **PASS**.
- Three-instance generic-source-suppression cross-program smoke: **PASS**.
- Final targeted reports contained **status=PASS** and **errors=[]**, with no reported final JavaScript runtime errors.
- A complete **26 × 3 / 78-view** regression was **not** run after the last rendering changes. No independent all-room construction-readiness acceptance was established.
- Some initial screenshot tests were **false negatives**: they incorrectly expected selected wet wall imagery in PH-WC (no independent pick) and TX-POWDER (NO PICK), or averaged overwhelmingly empty background pixels so that small porcelain updates appeared invisible. Source-aware expectations and actual fixture-region comparisons resolved those false negatives **without inventing images or fixture geometry**.
- No reliable, repeatable end-to-end wall-clock durations were recorded. Actual time varies with local Chrome startup and software rendering. **Do not claim a fixed run time in minutes** and do not rerun a full suite simply to create a timing estimate.

These receipts are provenance, not a standing command to repeat every test. For any later small, authorized change, prefer one accurate affected-room A/B visual/source check over full historical manifest, hash or image-comparison cycles.

## 5. Read-only Revit access and source-of-truth policy

**Correct open model:** **25-006 1527 N Wieland**. Owner confirmed **1527 and 1529 Wieland are the same building**. A differently named/active Revit document must not silently be used to establish this viewer's dimensions.

**Read-only wrapper:**

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\tools\revit_read.py

**Access, supported CLI arguments and authentication documentation:**

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\REVIT.md

From the workspace root, the established invocation pattern was **python tools\revit_read.py ...**; supported arguments and the actual authenticated endpoint/token configuration must be taken from the wrapper's current documented usage. **The exact subcommand flags are not reproduced here because they were not verified in this transfer. Do not invent them.** The authorized credential/token storage or reference is described by **REVIT.md** and the wrapper's secure environment/configuration; inspect that documentation locally if access is needed. **Never print, log, paste into this document, publish or transmit credential/token values.** Do not assume the secret lives in the workspace.

Permitted future activities only when explicitly needed for an authorized architectural correction: read element geometry/IDs/levels/parameters, wall and floor data, door/window hosts and openings, category bounding boxes, room-number/name parameters and schedules. Retain stable Revit element identifiers and read receipts in the evidence trail. Known integration fault: **OST_Rooms elements.query fails**. The workaround is to correlate room numbers/names, schedules, walls/floors by level, native wall-face evidence and drawing-registered polygons. **Never label the reconstructed wall-face polygon as a certified native OST_Rooms object.** An AABB from Plumbing Fixtures, Countertops or another Revit category **does not establish a manufacturer family's complete solid, exact sink cutout, actual mounting or installation geometry**.

Prohibited actions: Revit transactions, element/model changes, family imports, save/sync, live-model restart or disruptive intervention. No fresh Revit read was necessary or performed in the last rendering pass. Respect room evidence uncertainty when room membership or openings cannot be established; do not alter native walls to make an area appear to agree with a selected drawing.

## 6. Data truths, UNLOCATED conditions and unresolved architectural problems

### Unresolved primary room-area attribution — highest architectural priority

**PH-PRIMARY 304A/B**
- Drawing dimensions: **11.583 × 8.900 ft**, approximately **103.09 SF**.
- Derived/inferred wall-face envelope: **11.240 × 12.406 ft**, approximately **122.0562 SF**; discrepancy approximately **+18.4%**.
- Neither inferred 122 SF envelope nor 103 SF drawing dimension has been reconciled to a verified native OST_Rooms membership. Preserve original native walls and note the disputed attribution; do not scale walls to force the target area.

**TX-PRIMARY 202A/B**
- Drawing: **10.25 × 8.49 ft**, approximately **87.02 SF**.
- Derived wall-face envelope: **8.333 × 14.677 ft**, approximately **104.4577 SF**; discrepancy approximately **+20.0%**.
- Same unresolved room/adjacency attribution. Do not silently choose 104 SF over 87 SF as certified area.

### PH-BATH4 room/quantity separation

- **311A/B** are PH-BATH4 wet rooms; **310A** is **WIC4**; adjacent **310B** is separate **Bath4 context**. Do not collapse 311, 310A and 310B into one room or borrow elements without provenance.
- Competing PH4 area figures: **26.9792 SF inferred native wall-face**, **27.08 SF drawing**, **35 SF frozen historic**.
- Existing **40.2 SF Pienza LEVEL/POINT PAN gross material pool** was a single combined historic material pool. Do not duplicate it or change purchase quantities absent new owner authorization.

### Fixture, finish and physical-assembly holds

- **PH-POWDER 405A/B:** source basin points are retained; complete illustrative basin footprints failed native Countertop AABB containment. Keep only the small **3D UNLOCATED** locator, no moved/fabricated basin or cutout.
- **TX-PRIMARY 202A/B:** generic basin suppressed because adequate native placement/containment was not proven. Primary wet installation and drain point still unresolved.
- **PH-PRIMARY and TX-PRIMARY:** **48-inch LINEAR drain type selected**, not certified installed drain location, tile slope or shower/glass coordinates. No invented shower niches.
- **PH-BATH3 307A/B and TX-BATH3 207A/B:** **tub vs. walk-in UNSELECTED**. A drawing tub marker or wet tile study does not constitute a choice.
- **TX-BATH4 007A/B:** nominal **Duravit 59 × 29.5 in** tub is a selected product but **2D UNLOCATED**. Do not show it as installed 3D geometry.
- **TX-POWDER 102A/B:** **NO PICK** wall; no selected basin or faucet. The native **0.125 ft** Countertop-category slab is not evidence of a complete fabricated vanity.
- **TX-POWDER2 010A/B:** selected accent and Hansgrohe deck faucet metadata; basin **UNSELECTED**, installation location for faucet unknown. No speculative integrated fixture.
- **PH-WC 314A/B and TX-WC 203A/B:** floors are inherited and neutral, not independently selected tile. Generic porcelain WC body is intentionally source-gated but manufacturer geometry, bowl height, carrier/support, mounting, cistern, outlet, trap and rough-ins are **not** validated. Avoid visual suggestion of engineered support.
- **PH/TX Bath2:** nominal selected Duravit tub body and inner porcelain are a generic appearance study, not certified manufacturer part or verified drain, overflow, flange or rim elevation.
- Other room-specific native source limitations, finish provenance, locators and data receipts should be read from the source classifications in **E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\ACCURACY.md** and frozen picks rather than assumed away.

### Source evidence availability

- Native **OST_Rooms elements.query** access is known broken; do not repeatedly retry this exact failure without evidence of a wrapper fix.
- Some native category AABBs are obtainable but their full family solids are not. A dimension derived from an AABB is a **category bound**, not an installation survey.
- The original **2026-11-07 source PDF** was unavailable locally in the historical workflow. Repeated attempts to fetch it did not provide the missing facts; do not consume another iteration chasing the identical unavailable source without a new supplied file or access change.
- Open area and program conflicts are intentionally **not closed** by cosmetics. Carry clear source/derived/unknown qualifiers into views and inspectors.

## 7. Hard boundaries, frozen decisions and release controls

1. **Revit read-only and Smartsheet read-only.** No model transaction, save, sync, element change, family import or schedule/sheet overwrite.
2. **No owner or vendor contact, email, price solicitation, procurement, sample order or approval process.** No tile board, product choice or SKU revision.
3. **Preserve frozen picks and scope.** Do not alter selected tiles, finish champions, scores, products, pricing, quantities, technical statuses, unit types or A/B program; treat all 13 × 2 physical instances distinctly.
4. **No fabricated facts:** dimensional evidence, sanitary installation, shower fixtures, drain locations, niches, cabinet support, doors, windows, rough-ins, manufacturer family bodies or prices must be source-supported. Derived geometry must remain visibly/semantically labeled.
5. **Preserve validated native geometry and hosted openings.** Keep illustrative countertop faces within corresponding native AABBs; do not move native plumbing insertion points to make generic solids fit.
6. **Offline viewer and source features remain intact:** orbit/pan/zoom, reset, modes, inspectors, galleries, deep links, source-trace and reversible cutaways.
7. **No Git/release assumptions.** Current branch, uncommitted status and repository state were not checked during the latest passes because Git commands were prohibited. No push, pull, merge, rebase, commit, deployment, external hosting or public release was performed or authorized.
8. **Immediate stop transfer:** The owner ordered no additional features, browser QA, hashes, Revit reads, reviewer workflow or loop during handoff. The future backlog below does not retroactively authorize work in the stopped session.

## 8. Five prioritized improvements for a separately authorized future continuation

**1. Reconcile primary bathroom enclosure/room attribution from source evidence.** This is the **single most consequential** architectural fidelity issue. Resolve PH-PRIMARY **122.0562 vs. 103.09 SF** and TX-PRIMARY **104.4577 vs. 87.02 SF**, and associated native wall-face vs. drawing attribution, through permitted read-only evidence. Preserve actual wall coordinates/hosted openings and document uncertainties if native room membership cannot be proven. Do not force an area via geometric rescaling.

**2. Resolve physical fixture/program placement with evidence, then model only justified installations.** Focus on PH/TX primary basin/shower/drain references; PH-POWDER native basin containment; TX-POWDER2 basin/faucet point; selected-but-UNLOCATED TX-BATH4 tub; and still-UNSELECTED PH/TX Bath3 tub-vs-walk-in programs. Do not silently convert a historic selected SKU into an installed fixture or invent new owner selections.

**3. Improve coherent whole-room high-end photorealism.** Target primary, neutral WC and powder continuity, wall/ceiling relationships, real material scale/roughness/normal response, corner/contact depth, source-controlled openings and camera compositions. Preserve source-trace and UNLOCATED visibility so beauty does not conceal uncertainty.

**4. Improve explicitly illustrative sanitary model readability and contact behavior.** The latest generic WC continuous ceramic shell and Bath2 hollow porcelain offer a basis, but should not imply verified manufacturer dimensions or engineering. Avoid floating/detached appearances and unrealistic fixture-to-floor/wall relationships; where source support is inadequate, prefer clearly identified neutral or analytical representations.

**5. Run narrowly scoped buyer-centered Chrome QA for changed A/B rooms.** Validate actual source placement, available camera modes, legible whole-room appearance, selections, labels, cutaways and offline operation. Use existing focused scripts and receipts only when applicable. Do not reconstitute historical universal regression, review rounds or repetitive screenshot/hash manifests.

These are priorities for the **next coding agent's planning after new instruction**, not a current work order or product approval.

## 9. Things not to repeat

- **No historical reviewer-worker cycles, agent loops, global DONE verdict chase, or per-round ledger STATUS protocol.** The recipient operates with ordinary local tools; no chat-specific tool or review infrastructure exists or is needed.
- **No annualized or per-change SHA/hash/manifest cycles** or full 26 × 3/78-view suite after every cosmetic change. The previously recorded historical frozen picks SHA-256 is **a468848af7a7390a796a1d489b9a493b991dc5d30e478ed10eb0284818f92d0d**; the last recorded standalone index HTML SHA-256 is **c291cda1ddd9ed27c494c56500b47bf015bfa48314dbf5d0ab96eddf753e8d6d**. They are provenance only, **not a demand for repeat checking**.
- **Do not call valid neutral/no-pick studies regressions** simply because Wet Zone Study does not visibly change in PH-WC or TX-POWDER. No selected independent wet feature exists there.
- **Do not treat globally tiny screenshot pixel changes as absence of a physically small fixture improvement.** Inspect actual fixture regions and category/debug evidence when scoped testing is necessary.
- **Do not re-query the same failed OST_Rooms pathway** or repeatedly chase the missing original 2026-11-07 PDF without new evidence.
- **Do not reconstruct inferred footprint polygons as certified Revit room elements**, treat Countertop/Plumbing category AABBs as detailed family solids, or infer mounting, basin holes, supports and shower slope from bounding boxes.
- **Do not restart product selection** or resolve area/schedule discrepancies by changing locked quantities.
- **Do not re-run viewer builds or browser QA merely to complete this handoff.** The current artifact was already built and checked in targeted scope; no more operations are part of the 2026-11-08 STOP order.

## 10. Known-good local deliverable, evidence and status at transfer

**Viewer to open:**

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\index.html

**Authoring source / build script:**

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\viewer3d_scene_v2.js
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\build_viewer3d_index.py

**Frozen selections and source classification:**

    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\picks.json
    E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\deliverables\viewer3d\ACCURACY.md

The last recorded standalone HTML rebuild succeeded for **13 room types** and retained all A/B instances and major offline controls. Source-aware targeted Chrome tests of dry rooms, PH4/310B bounded countertop, TX-WC, generic WC/Bath2 ceramics and suppression conditions passed within their stated scope. The viewer has **not** received an all-room construction-accuracy or whole-program photorealism sign-off. The current branch/working tree is unknown because no Git commands were run; no deployment occurred. No Revit or Smartsheet writes were performed, and no external contacts or purchases were initiated.

**Disposition:** The 2026-11-08 owner order stopped implementation and called for this technical transfer. The standalone recipient should begin from this handoff and the named existing project files when separately authorized, not from missing prior chats or a historical activity ledger. Preserve the current viewer as the handoff baseline and communicate unresolved evidence limitations rather than implying they have been solved.

## 11. Setup-assistant verification note (2026-11-08, added after the loop stopped)

- Checked on this PC: the build script `E:\Claude\3D-Model-Workflow\output\wieland1529_tile_loop\scratch\build_viewer3d_index.py`, the scene source `...\scratch\viewer3d_scene_v2.js`, the geometry script `...\scratch\viewer3d_architecture_r043.py`, `...\tools\revit_read.py` and `C:\Program Files\Google\Chrome\Application\chrome.exe` all exist.
- CORRECTION to section 4: `C:\Users\mlux\...\Python312\python.exe` does not exist on this PC. The Python on PATH is `C:\Python314\python.exe` (Python 3.14.6), and `playwright` and `PIL` both import there. Use plain `python`.
- The CoS loop is stopped and its Loop automation is off (2026-11-08 09:49 UTC). Nothing in this folder is being changed by CoS any more.


## November 9, 2026 - published floor-plan geometry correction release

Viewer: deliverables/viewer3d/index.html. Published-path browser verification PASS; all 26 native Room boundaries and 338 source elements matched the last successful live readback. PH Bath4 now uses 310A/B (5 ft by 7 ft 0 1/4 in), TX WC existing Room records repaired, PH2 finish-return host metadata corrected. Frozen picks.json unchanged. Prior release backed up in scratch/floorplan_geometry_corrections_20261108/baseline. Full evidence and GEOMETRY_AUDIT.md/json supplied.

Outstanding: Revit closed after native verification. Agent did not save/synchronize. User asked to reopen for confirmation that five Room-record repairs persisted. Do not replay the commit. Discover fresh document session and read back the five repaired records plus 26 boundaries/338 geometry elements against H:/Games/3D Modeling Workflows/3D Model Workflow/output/wieland-floorplan-corrections-20261108/final-readback-expected.json. Native commit 675dbe05-db95-43a9-8684-1ad3f6fa86ea; last successful readback 40a89212-c2b5-4914-9c49-0100c66587b9. Latest connection refresh 2c2b4131-eac6-426d-9a21-6a586be04dc3 was read-only and could not connect (no Revit process).
