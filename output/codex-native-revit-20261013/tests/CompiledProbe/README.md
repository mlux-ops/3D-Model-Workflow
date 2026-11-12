# Trusted compiled API probe

This small source module demonstrates the bridge's explicit compiled C# operation interface against Revit 2025 / .NET 8. Compilation proves reference compatibility only. Native execution and state readbacks require a separate native test receipt.

Build the main bridge in Release first, then run:

```powershell
dotnet build .\CompiledProbe.csproj --configuration Release
```

The module uses a direct DLL reference to `../../src/NativeRevit/bin/Release/net8.0-windows/CodexNativeRevit.dll`; it does not rebuild or edit the main bridge. `BridgeAssemblyPath` and `RevitPath` are MSBuild overrides if explicit alternate locations are needed. Output is `bin/Release/net8.0-windows/CodexNativeRevit.CompiledProbe.dll`. The captured Release build has zero errors and two MSB3277 warnings from Autodesk transitive Microsoft.VisualBasic/System.Drawing reference versions. Native loading/execution is a separate verification boundary.

Set `CODEX_REVIT_PLUGIN_DIR` in the Revit launch environment to a directory containing this DLL. The bridge's compiled pathway is disabled unless this directory is explicitly configured. Do not copy Revit API assemblies or a second bridge assembly into the plugin directory. The query and modification classes contain no file, network, save, close or synchronization calls. They create no transaction: query uses the bridge's query guard; modification relies on the bridge's outer transaction and rollback policy. Trusted compiled plugins are not securely sandboxed.

## Query class

Full type: `CodexNativeRevit.CompiledProbe.ProbeQuery`.

Submit `compiled.query` with an explicit document target and these arguments:

```json
{
  "assembly": "ABSOLUTE_PATH_TO_CodexNativeRevit.CompiledProbe.dll",
  "type": "CodexNativeRevit.CompiledProbe.ProbeQuery",
  "purpose": "Read native API metadata and disposable-document view visibility",
  "expected_changes": [],
  "arguments": {
    "document_session_id": "CURRENT_DISPOSABLE_DOCUMENT_SESSION_ID",
    "view_unique_id": "CURRENT_VIEW_UNIQUE_ID",
    "category_id": -2000011
  }
}
```

The `view_unique_id` and `category_id` fields are optional. A category ID requires a view. Obtain current category IDs from `categories.query`; the example numeric ID is the Revit built-in Walls category and is not an element identifier. `document_session_id`, when supplied to the query, must match the target. Result includes detached document identity, total element count including types, installed API reflection signatures for `GetCategoryHidden`, `SetCategoryHidden`, `CanCategoryBeHidden`, display/native units, and optional view/category-hidden readbacks. It changes no view visibility.

## Modification class

Full type: `CodexNativeRevit.CompiledProbe.ProbeModify`.

Submit `compiled.modify` to the **disposable target document** with:

```json
{
  "assembly": "ABSOLUTE_PATH_TO_CodexNativeRevit.CompiledProbe.dll",
  "type": "CodexNativeRevit.CompiledProbe.ProbeModify",
  "purpose": "Set one disposable instance's Comments and verify the result",
  "expected_changes": ["Only the explicitly identified instance's ALL_MODEL_INSTANCE_COMMENTS string"],
  "arguments": {
    "document_session_id": "CURRENT_DISPOSABLE_DOCUMENT_SESSION_ID",
    "element_unique_id": "CURRENT_INSTANCE_UNIQUE_ID",
    "comment": "Codex compiled API disposable test",
    "expected_before": null
  }
}
```

`document_session_id`, `element_unique_id`, and `comment` are required for `action: "instance_comments"` (the default). `expected_before` is optional and accepts a string or null; obtain the actual existing value before including it. The module rejects stale identities, types, pinned/grouped/owned elements and unwritable or missing built-in Comments parameters. It sets exactly that parameter, regenerates and returns actual before/after values and identifiers. The bridge owns commit, rollback, job status and persistence. No model is saved by this operation.

The same `ProbeModify` class provides three additional explicit actions. All require the matching `document_session_id` and an active outer target-document transaction. These actions demonstrate native API extensions; they do not create unrestricted interface access.

For `action: "view_orientation"`, pass `view_unique_id`, `eye`, `up`, and `forward`. Each vector is a finite three-number array; eye coordinates are internal feet, and direction vectors are normalized. Up and forward must be perpendicular. The action rejects template/locked views and does not unlock them. It calls `View3D.SetOrientation`, regenerates, and returns actual `GetOrientation` values before and after. It performs no save or orientation-lock operation. Set an eye on positive Y and a forward direction toward negative Y when the explicit disposable-scene layout requires that camera side; choose coordinates from actual scene bounds.

```json
{
  "document_session_id": "CURRENT_DISPOSABLE_DOCUMENT_SESSION_ID",
  "action": "view_orientation",
  "view_unique_id": "CURRENT_3D_VIEW_UNIQUE_ID",
  "eye": [10, 20, 8],
  "up": [0, 0, 1],
  "forward": [0, -1, 0]
}
```

For `action: "schedule_widths"`, pass `schedule_unique_id` and `widths`, containing a finite positive internal-feet value for every field in the current schedule field order. The action verifies that the installed `ScheduleField` API has public `SheetColumnWidth` and `GridColumnWidth` setters, sets both, regenerates, and compares actual numeric readbacks to the request. It changes only this schedule's field widths. It does not reposition schedule instances, alter field definitions, or imply that a sheet is visually approved.

```json
{
  "document_session_id": "CURRENT_DISPOSABLE_DOCUMENT_SESSION_ID",
  "action": "schedule_widths",
  "schedule_unique_id": "CURRENT_TWO_FIELD_SCHEDULE_UNIQUE_ID",
  "widths": [1.0, 0.3]
}
```

Wrap either action inside the compiled.modify envelope's `arguments` field and declare its actual intended changes in `expected_changes`. The dimensions shown are disposable test inputs, not production design requirements.

For `action: "create_elevation"`, provide `elevation_type_unique_id` (a native `ViewFamilyType` with `ViewFamily.Elevation`), `plan_view_unique_id` (an existing non-template level-associated native `ViewPlan`), `point` in internal feet, `index` from 0 through 3, an explicit `name`, and `scale`. Optional `marker_rotation_radians` rotates the new marker about a vertical axis through the supplied point. The action creates one native `ElevationMarker` and one native elevation; it rotates the populated marker so the actual elevation participates, regenerates, and returns qualified marker/view/plan references, actual view direction, scale and crop-box bounds/transform. It does not auto-create a plan, select a design direction, place the view on a sheet or save a document.

```json
{
  "document_session_id": "CURRENT_DISPOSABLE_DOCUMENT_SESSION_ID",
  "action": "create_elevation",
  "elevation_type_unique_id": "CURRENT_ELEVATION_VIEW_FAMILY_TYPE_UNIQUE_ID",
  "plan_view_unique_id": "CURRENT_PLAN_VIEW_UNIQUE_ID",
  "point": [10, 10, 0],
  "index": 0,
  "name": "Disposable Kitchen Native Elevation",
  "scale": 24,
  "marker_rotation_radians": 0.0
}
```

Use the actual returned direction to verify that the elevation faces the required scene; the index and example point do not establish a suitable production direction. A failure remains within the outer transaction and leaves no committed marker/elevation.

API references required: `RevitAPI.dll`, `RevitAPIUI.dll`, the version-matched `CodexNativeRevit.dll`, and .NET 8 runtime/framework references. The source uses `ICompiledOperation`, `DocumentRegistry`, and `Util.Editable` from the bridge.
