# Native family API

Implementation: `src/NativeRevit/FamilyOperations.cs`, compiled against the installed Revit 2025 assemblies. All calls execute on Revit's ExternalEvent thread. Compile validation is separate from native execution; the operations below are implemented, with native validation status recorded by the project's test evidence. This document does not establish visual, hosted-placement, manufacturer-fidelity, or delivery acceptance.

Every operation except `family.create` and `family.open` requires the bridge's explicit document target and normal document identity checks. Element references use UniqueId strings, or document-qualified objects containing `document_session_id`, `id` and `expected_unique_id`. Naked numeric ElementIds are rejected. Stable references are resolved within the targeted document. A project document is a valid target for `family.edit`, `family.load`, and `family.reload`; other authoring operations require a native family document. Lifecycle methods are independent boundaries; no project transaction encloses them.

## Document lifecycle

| Operation | Arguments | Result and restrictions |
| --- | --- | --- |
| `family.create` | `template`: absolute existing `.rft` path | Creates background family, registers and returns its document identity; no save. Uses exactly the requested template. |
| `family.open` | `path`: absolute existing `.rfa` path | Opens background family, or returns an already open matching-path document. No active UI activation or save. |
| `family.edit` | `family`: Family UniqueId or document-qualified identity in targeted project | Returns newly edited family document identity. Rejects in-place/non-editable families and read-only/modifiable source documents. |
| `family.inspect` | none | Native category, placement type, editability, family types, parameter definitions/values, family views, nested families and warnings. |
| `family.save` | `path`: absolute NEW `.rfa` path; optional `compact` | Calls `SaveAs` with `OverwriteExistingFile=false`, verifies nonempty file, returns path/bytes/document identity. Destination directory must exist. Existing files are always rejected. |
| `family.load` | `path`: absolute existing `.rfa`; REQUIRED `replacement_policy` | Loads into target project or family inside its own target transaction; returns actual family ID, `loaded`, and callback decisions. `loaded:false` means unchanged or rejected. |
| `family.reload` | `source_document_id`: open family identity; REQUIRED `replacement_policy` | Calls source family's native `LoadFamily(target, options)` outside open transactions. Revit manages target transaction. Source and target must differ. No save or close. |
| `family.close` | REQUIRED `discard_changes:true` | Closes background family with `Close(false)`. Active UI family is rejected. Explicit save must be a previous request if needed. |

The three replacement policies are `reject`, `preserve_parameters`, and `overwrite_parameters`. Revit invokes conflict callbacks only for changed existing families. `preserve_parameters` accepts incoming family content and retains target parameter values; `overwrite_parameters` accepts incoming content and overwrites parameter values. Shared-family conflicts use the incoming family under either accepting policy, with the decision returned. `reject` declines callbacks; reload additionally checks for an existing target family with the source family's exact name before loading. Type names, content identity and family-specific native restrictions still govern outcomes. No callback occurrence is proof that no target content changed.

Saving creates a durable external file. Loading/reloading changes another document. An authoring transaction on the source cannot undo either boundary. After a timeout, inspect the job receipt and targeted native state/file before retrying.

## Geometry and references

All geometry operations require `units:"feet"`. Coordinates are native family document coordinates; angles are radians. No implicit conversion from millimeters/inches or project/shared coordinates occurs. The caller converts measurements explicitly before submitting.

`plane` is `{ "origin":[x,y,z], "normal":[nx,ny,nz] }`. Alternatively, `sketch_plane` identifies an existing SketchPlane in the targeted family. A new plane is created in the same authoring transaction, and is returned along with the form. Geometry is accepted/rejected by Revit's native conditions and tolerances.

`profile` is an array of closed loops. Each loop is either an ordered point array, with the closing edge supplied automatically, or an ordered array of curve objects. Curves are `{ "kind":"line", "start":[...], "end":[...] }` or `{ "kind":"arc", "start":[...], "end":[...], "point_on_arc":[...] }`. Mixed point/curve loops are unsupported. An explicitly repeated closing point is removed from point loops. Holes use additional disjoint closed loops where the corresponding native API permits them. Plane membership, ordering, intersections and validity remain native checks.

| Operation | Additional arguments | Implemented behavior |
| --- | --- | --- |
| `family.extrusion.create` | `profile`, plane, `end`; optional `start`, `solid:true` | Native Extrusion. Explicit `solid:false` creates native void form. Returns ID, sketch plane, actual offsets and geometry readback. |
| `family.extrusion.modify` | `element`, optional `start`, `end` | Changes native offsets; before/after readback. Does not rebuild profile sketches. |
| `family.revolution.create` | `profile`, plane, `axis:[[...],[...]]`; optional `start_angle:0`, `end_angle:2*pi`, `solid:true` | Native Revolution. Axis and profile must be compatible with the requested sketch plane. Returns native geometry readback. |
| `family.blend.create` | `profile1` and `profile2` single loops; plane; optional `solid:true` | Native Blend. Profiles must be parallel and valid; native vertex correspondence is used. Returns actual top/bottom offsets and geometry. No claim of controlled custom vertex mapping. |
| `family.sweep.create` | `path`, `profile`, path plane; optional `profile_curve_index:0`, `profile_location:"Start"`, `solid:true` | Native Sweep using curve-loop profile. `path` is open ordered points/curves. `profile_location` is exact enum name `Start` or `End`. Profile coordinates must meet native orientation/path constraints. |
| `family.geometry.inspect` | none | Every native GenericForm: ID, solid/void flag, bounds and transform, native Solid volumes/faces/edges. Numbers are feet and cubic feet. Empty solid data is returned honestly. |
| `family.reference_plane.create` | `view`, `bubble_end`, `free_end`, `cut_vector`; optional `name` | Native reference plane; returns ID, ends, normal and stable reference. |
| `family.dimension.create` | `view`, `line:[[...],[...]]`, `references`; optional `label_parameter`, `locked:false` | Native family linear dimension, optionally labeled or locked. Label/lock constraints must satisfy the native API. |
| `family.alignment.create` | `view`, `reference1`, `reference2` | Native alignment constraint between compatible already aligned references; no hidden geometry movement. |

A reference argument is a native stable reference string or `{ "reference_plane": "native-reference-plane-UniqueId" }`; the nested element reference also accepts a document-qualified object with its expected UniqueId. Stable references belong to the target document; do not transplant them from another family or saved revision without checking.

Conventional form creation is restricted by template/category. Conceptual/adaptive mass forms, 2D-only templates, imported geometry, custom spline profiles, arbitrary sketch reconstruction, universal host/category conversion, explicit void cutting/combining, custom blend vertex mapping and sweep sketch editing are not implemented here. Native void creation does not establish that a specific solid or project host has been cut. Existing parameter-driven forms may be modified through native parameter association/flex; offsets are the only dedicated existing-form edit in this module. Generic meshes/DirectShape are not substitutes for these operations.

Example extrusion arguments (1-foot square, 2-foot extrusion):

```json
{
  "units":"feet",
  "plane":{"origin":[0,0,0],"normal":[0,0,1]},
  "profile":[[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]],
  "start":0,
  "end":2,
  "solid":true
}
```

## Parameters and types

| Operation | Arguments | Result and restrictions |
| --- | --- | --- |
| `family.parameter.add` | `name`, `group`, `data_type`; optional `instance:false` | Non-shared family parameter using version-correct ForgeTypeIds. Returns native definition identity/storage/flags. No implicit shared-parameter-file editing. |
| `family.parameter.set` | `parameter` exact name or numeric parameter ID string; `value`; optional `type`, `value_string:false` | Sets current or explicitly selected type. Returns before/after native value. Formula/read-only/reporting values are rejected. |
| `family.parameter.formula` | `parameter`, `formula` string or null | Sets or clears formula; returns before/after. Native formula restrictions apply. |
| `family.parameter.associate` | `element`, `element_parameter_builtin` OR `element_parameter_id` OR unambiguous `element_parameter` name, `family_parameter` exact name/ID string or null | Associates/dissociates supported native element parameters. Returns actual association. Material parameter associations use this same native mechanism. |
| `family.type.create` | `name`; optional `values` dictionary | Creates native type; sets supplied values; returns readbacks. |
| `family.type.set` | REQUIRED `name`; optional `values` dictionary | Selects existing type and regenerates; returns parameters and native forms. Changes remain in family memory until explicit save. |
| `family.type.flex` | `types:[{"name":"Type A","values":{"Width":2}},...]` | Validates 1–100 explicit scenarios. Each regenerates in a family transaction; all changes roll back through a TransactionGroup. Returns scenario readbacks/warnings/form bounds/volumes and `original_state_restored:true` only after successful rollback. Never saves. |

`group`/`data_type` accept full ForgeTypeId strings. Convenient names resolve public properties on GroupTypeId/SpecTypeId (e.g. `Geometry`, `Length`); `Text` and `YesNo` resolve the corresponding nested SpecTypeId properties. For Material use full `autodesk.spec.aec:material-1.0.0`; the root shorthand `Material` is not supported and its native rollback is retained in the extended test report. Native API rejects invalid/non-applicable definitions.

Double values use Revit internal units for that parameter's data type (length feet, angle radians, area square feet, etc.). They are not universally lengths. Integers must be integers, strings strings, and ElementId values numeric native element IDs. For a dimensioned parameter the caller may explicitly choose `value_string:true` to let native Revit parse a display string in its document unit context. Return values remain native storage values. Numeric-only IDs and name ambiguity are documented constraints; no parameter is guessed.

Flex validates native regeneration and numerical readbacks; it does not prove adequate design clearances, physical fit, intended constraints, visual quality, or supported hosted placement. Geometry regeneration alone does not prove a formula controls the desired feature. Establish those gates separately in disposable family/project tests with supplied requirements.

## Transaction and test boundaries

All family authoring and file-load operations own their document Transaction. Results expose `transaction_status:"committed"`, warnings, and `saved:false`. Failure receipts claim rollback only after the native transaction/group returns a verified RolledBack status. Errors after commit, Pending status, or unconfirmed rollback return `unknown_completion`; native changes may persist. Flex is intentionally successful verification with `transaction_status:"rolled_back"` only after group rollback succeeds. Create/open/edit/save/close are lifecycle operations with `not_applicable`; reload uses `revit_managed`. An exception after entering SaveAs or native cross-document reload also returns `unknown_completion`, including failed post-call file/element readback, because durable changes may already exist. Precondition errors before these calls remain ordinary failures. Reconcile native state and original job receipts before retrying. No operation silently saves, closes, replaces an existing file, or synchronizes.

Initial compile checked all family API signatures against installed assemblies. Native scenario execution, saved-file reopen, nested placement, formula-driven geometry response, visual comparison, and hosted project placement must appear in separate durable native test receipts before being labeled tested. A loaded DLL or successful compiler exit is not native operation acceptance.

`tests/native_family_sequence.py` runs against explicitly supplied isolated bridge URL/token and family/project templates. It creates a synthetic rectangular family, associates `EXTRUSION_END_PARAM` to a real height parameter, checks two flexed geometry heights and rollback, saves a new RFA, closes/reopens it, loads it into a disposable project, and places a level-based instance if the supplied template supports that placement. A resumable report and original operation UUIDs persist under its explicit output directory. Dependent work stops on failed, rolled-back or unresolved requests. It intentionally proves only height-driven extrusion geometry; width/depth remain fixed and no manufacturer fidelity is claimed. Family/project remain open afterward except the explicitly saved-then-closed first family document.
