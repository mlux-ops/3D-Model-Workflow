# Gola Revit Family Implementation Plan

**Goal:** Deliver the approved Revit 2025 family with four manufacturer profiles, editable finish, optional compatible accessories and adjustable endpoints.

**Architecture:** Run the installed pyRevit generator in a separate Revit 2025 process. Use the native line-based template and native extrusions associated with its instance Length. Every type follows the placed line; vertical installation is achieved by placing on a vertical work plane. Accessories at the end use formula-driven extrusion start/end positions to follow length edits.

**Tech Stack:** Revit 2025 API, pyRevit IronPython, manufacturer PDF drawings, Python acceptance-report checks.

**Spec:** docs/superpowers/specs/2026-09-07-gola-channel-profile-family-design.md

## Global constraints

- Preserve other fixtures and user projects. Output only to output/gola and new Gola-specific scripts/reference files.
- Revit 2025; four selectable types; stainless appearance by default.
- Cross-section dimensions and grip surfaces derive from the drawings. Document undimensioned details as inferred.
- Revit internal units are feet; convert published mm using 304.8 mm/ft.
- Each type follows local X and the selected placement line. Do not rotate vertical geometry away from its length controls.

## Tasks

- [x] Preserve and visually inspect the four profile drawings, mounting sheets and accessory compatibility evidence in references/gola. Correct preliminary section dimensions and stock metadata against these drawings.
- [x] Probe the native line-based template in tmp/gola/probe.py: report Length parameter, reference planes, placement type and available appearance assets to tmp/gola/probe.json.
- [x] Write scripts/build_gola.py with native extrusions, family parameter associations, four mutually exclusive type visibility controls, end-dependent accessory positions, manufacturer metadata and material assets. Save output/gola/Richelieu_Gola_Channel_Profiles_2025.rfa.
- [x] Reopen in Revit; load into a new sample project; place each type on horizontal planes and the vertical types on a vertical face; set line length to 600 and 2400 mm; move each location-curve endpoint separately; measure actual resulting solid extents and end-cap locations.
- [x] Toggle accessories and confirm visible geometry responds; disable incompatible horizontal hardware for vertical types. Change material, verify solid face material IDs, and restore stainless.
- [x] Save sample project and export profile/assembly previews. Inspect against drawings. Native desktop endpoint controls were observed and dragged independently on the C profile; see output/gola/UI_CHECK.md.
- [x] Run tests/test_gola.py against the real saved/reopened validation report. Prepare RFA, sample RVT, previews and instructions with exact source/inference limitations.

## Acceptance values

- Exactly four family symbols; Generic Models; curve-based placement.
- Numeric placement-line length and either-endpoint edits must change measured channel length within 0.1 mm. Native project Length is read-only; use temporary dimensions for numeric UI edits.
- Caps stay at the moving endpoint within 0.1 mm.
- Material parameter changes the visible profile faces.
- No unresolved Revit failure or warning in delivered family/sample project.
- Native cross-sections retain open grip recesses; all applicable accessory options are accessible from instance Properties.
