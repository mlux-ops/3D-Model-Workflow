# Purist Visualization Family Implementation Plan

**Goal:** Create and verify an independent Revit 2025 polished-chrome visualization RFA.

**Architecture:** Use installed pyRevit to run a scoped generator in a separate Revit process. Create a family from the installed face-based template with native analytic solid geometry, assign a Revit chrome appearance asset, save into output, then reopen and test in a disposable project. Keep the user's active project and source files untouched.

**Tech stack:** Revit 2025 API, installed pyRevit IronPython, Python unittest for acceptance-report checks.

**Spec:** WORKFLOW.md, including nominal dimensions and inference boundaries.

## Tasks

- [x] Inspect the PDF drawing and product image; identify source dimensions and assumptions.
- [x] Probe local Revit automation and inspect available appearance assets.
- [x] Write acceptance checks for actual saved/reopened/placed output and run them before generation.
- [x] Generate plate and two handle assemblies as smooth analytic solids, material parameter, fixed nominal dimensions, and preview views.
- [x] Save/reopen the family and load/place in a new disposable project; export measured bounds and material-change test results.
- [x] Inspect exported views and run acceptance checks; correct failures.
- [x] Prepare the RFA, preview, and concise limitations for delivery. Benchmark comparison remains pending until the supplied RFA is accessible.
