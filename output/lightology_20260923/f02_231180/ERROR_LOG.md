# F02 error log

## 2026-09-23 recovery
- The assigned F02 output directory did not exist when first inspected; the listing command failed with PathNotFound. Created the owned directory and continued from clean preparation state.
- Several Code Mode attempts to invoke deferred Chat On Steroids Core methods returned TypeError before any filesystem/native action. Retried after tool discovery exposed the live methods; Core read/exec then succeeded.

## 2026-09-23 preparation corrections
- A large Code Mode shell-write composition failed at JavaScript parse time with SyntaxError before any command executed. Solution: switched to Core apply_patch for source/doc creation and then syntax-checked the resulting Python.
- Desktop browser new-tab request timed out with BROWSER_NOT_DISPATCHED before any page operation. Solution: used the already-supported CoS fetch plus locally preserved source images and Core view_image for visual inspection.
- Initial photo-only bell backplate estimate was 3.36 in diameter. Source self-review found the Lightology line drawing explicitly specifies dia 4.3 in. Solution: builder and source notes corrected to 4.3 in before native execution; py_compile and JSON checks pass.
