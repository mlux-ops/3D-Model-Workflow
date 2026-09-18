# Pendant and material model-transfer tests

Prepared 2026-09-18. Status: **test kit prepared; candidate model has not been run**.

Purpose: determine whether another model can use this repository's experience to produce dependable native Revit families and material packages, and measure cost per accepted result. This is an open-book workflow test, not model training or proof of general modeling ability.

## Start here

1. Use an agent with filesystem/shell access on this Windows machine, permission to run Revit/pyRevit, image viewing, and native application access for material-library operations. A browser-only chat with uploaded documents is insufficient for the full test.
2. Read [environment and safety](ENVIRONMENT.md). Start a fresh session for each test, in this repository. Record the exact model identifier, client, tool access and reasoning setting in a copy of [the scorecard](SCORECARD.md).
3. Paste [the pendant prompt](PROMPT_PENDANT.md) into the first session. Paste [the material prompt](PROMPT_MATERIAL.md) into a separate session. Give both sessions access to this directory and the repository. Run sequentially when they share Revit.
4. Review the evidence against [pendant requirements](PENDANT.md) and [material requirements](MATERIAL.md). Do not accept self-reported success without opening the artifacts and reviewing the native evidence.
5. Repeat the same tests with a comparison model, using fresh output folders and the same tools. Compare accepted results, retries, assistance, time and actual billed cost. Unavailable cost data stays unknown.

Each test includes reproduction and a controlled variation. Passing shows reuse/adaptation of these two workflows; it does not establish performance on an unseen product. A later test should use a new product reference withheld from all training examples.

## Isolation and fair comparison

Outputs go only under `output/model-transfer-tests/<run-id>/pendant` or `material`. Choose a unique run ID such as `candidate-20260918-01`; never reuse a prior run's output directory. Put adapted scripts in the same run directory. Existing deliverables and source builders are read-only references.

Reuse source code openly; do not copy a completed RFA and call it a new build. For the material test, reuse of an existing ADSKLIB container is allowed only when disclosed and its material/maps are updated and natively revalidated. Report library creation as a separate capability; do not claim it from container reuse.

Use the same assistance policy for every model. Suggested pilot policy: one initial attempt and two repair cycles per test, followed by review. Record all further attempts separately rather than silently resetting failures. This is a comparison protocol, not authorization to spend on an external model API. No external model call is made by this kit.

Read only the workflow-relevant examples initially. The entire historical error log contains superseded facts and unresolved status updates; this kit selects the relevant lessons. User instructions and source dimensions remain authoritative. Historical validation records are examples, never evidence for a new run.

## What is supplied

- Exact tasks and acceptance rules, plus ready-to-paste prompts.
- Environment setup and native execution recipe.
- Worked-example walkthroughs pointing to existing builders, references and historical evidence.
- A scorecard separating technical, visual and environment outcomes.
- `SOURCE_MANIFEST.csv`: frozen file paths, byte sizes and SHA-256 hashes of the selected examples at kit preparation time. It detects source drift; it does not certify native functionality.

The kit itself contains documentation and an inventory, not a new final model/material package. When candidate runs produce final packages, the repository's standing Google Drive delivery requirement applies. Label test deliveries clearly and retain previous production packages.
