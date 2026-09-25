# F02 preparation self-review

Status: READY FOR PRIME NATIVE SERIALIZED RUN. Revit was not launched by this worker.

Source visual inspection:
- Exact Brass product image inspected: spherical opal globe; L-shaped brass tube; rounded elbow; shallow bell wall plate; small globe contact cap.
- Lightology line drawing inspected: small option explicitly shows 11 in projection, 8.5 in overall height, globe dia 7.9 in, wall plate dia 4.3 in.
- Application image inspected: equivalent rotated wall installation is shown; face-based family may be rotated on host face.

Builder static checks:
- Python 3.14 py_compile: PASS.
- sources_and_inferences.json parse: PASS.
- Expected analytic model envelope from staged constants: width 7.9 in, height 8.5 in, projection 11.0 in.
- Backplate corrected before native build from initial photo estimate to drawing-derived dia 4.3 in.
- Editable family material parameters staged: Brass Finish; Opal Glass Finish.
- Native QA code staged for RFA save/reopen, Lighting Fixtures category, actual wall-face Host/HostFace, mounting normal, placed dimensions, material substitution reaching geometry, warnings, and 5 review exports.

Pending gates:
- Native Revit 2025 execution by prime.
- Fresh validation.json timestamp/content.
- RFA save/reopen and technical pass.
- Native visual export self/prime review and any corrections.
