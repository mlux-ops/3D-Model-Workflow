# Request and operation reference

HTTP is a private bridge transport, bound to IPv4 loopback. Every request requires `Authorization: Bearer <token>`; the token is stored in the user-restricted state directory, never in Codex TOML or model prompts. Maximum JSON body is 2 MB. MCP stdio exposes six tools documented in controller/README.md.

`GET /v1/capabilities` returns detached transport identity and implemented operation names. It is not proof that every listed operation passed native testing. Native reads are submitted as jobs too.

```json
{
  "schema_version": 1,
  "operation_id": "00000000-0000-4000-8000-000000000001",
  "operation": "element.move",
  "document": {"session_id": "fresh-session-uuid", "path": "C:/explicit/model.rvt"},
  "preconditions": {"expected_title": "model", "is_family": false, "allow_existing_document": true},
  "arguments": {"element": "native-UniqueId", "vector": [1,0,0]}
}
```

`POST /v1/jobs` persists acceptance before enqueueing; `GET /v1/jobs/<UUID>` reconciles; `POST /v1/jobs/<UUID>/cancel` requests cancellation. Receipt states are queued, running, completed, failed, rolled_back, cancelled, unknown_completion. Reusing an ID retrieves the previous identical envelope; differing envelopes conflict. Use the controller to preserve canonical envelopes across restarts.

Project mutation result is `{data,transaction_status,actual_elements,warnings}`. Family mutation result is `{result,transaction_status,document,warnings,saved:false}`. Queries return the requested data directly. Receipts include elapsed milliseconds and UTC timestamps. Postcommit readback errors preserve committed/unknown state, never a fictitious rollback. File/save/reload call-boundary errors may be unknown even when no project transaction is open.

| Group | Operations and required argument concepts |
|---|---|
| Discovery | `documents.list` document `{}`; `context.query` selected document; `categories.query`; `warnings.query`; `api.lookup` `type` full Autodesk class name and optional `member` |
| Elements | `elements.query` class/category, types flag, name_contains, offset, limit 1–500; `elements.inspect` element, optional geometry; `parameters.query` element, includes separate type values |
| Coordinates | `links.query` includes instance transform and linked document identity; `coordinates.convert` point, system project/shared/link, link reference where needed, inverse flag; explicit direction in result |
| Placement | `family.place` type and one point/level/host or batch instances; OneLevelBased, OneLevelBasedHosted, WorkPlaneBased face_reference+reference_direction, CurveBased start/end supported; unsupported placement enum rejected |
| Transforms | `element.move` vector; rotate axis_start/axis_end/radians; copy vector; mirror origin/normal/copy; flip kind hand/facing; type explicit type reference; curve start/end |
| Parameters | `parameter.set` element, value and parameter_id/parameter_guid/built_in or unique name; optional Forge unit; type targets require allow_type_change; `type.duplicate` type/name |
| Delete | `element.delete_preview` element rolls back native deletion; `element.delete` element and exact expected_deleted_ids from fresh preview; pinned/grouped/owned objects rejected |
| Native system elements | wall.create start/end/type/level/height/offset/flip/structural; floor.create closed profile/type/level; general curve and parameter modifications support eligible existing elements |
| Views | view.create type/kind/name; 3d/drafting or plan+level; view.duplicate view/option/name; view.settings view/scale/template/crop/section_box where native view supports it |
| Sheets | sheet.create number/name/optional titleblock_type; sheet.inspect sheet, returns titleblocks, viewport bounds/labels, schedules and sheet outline |
| Viewports | viewport.place sheet/view/center; viewport.move viewport/center; viewport.settings viewport and explicit rotation/type/label_offset/label_line_length |
| Real schedules | schedule.create category/name/fields by unique native field name; schedule.place sheet/schedule/point; schedule.move instance/point; schedule.settings schedule/filters/sort/itemized |
| Annotations | annotation.text view/type/point/text; annotation.lines view/segments; dimension view/start/end/references; tag type/view/reference/orientation/point/leader; filled_region type/view/profile |
| Layout | layout.propose content_region [xmin,ymin,xmax,ymax], moves element/point, optional reserved_regions; layout.apply same request performs native movement then validates regenerated bounds. Include all existing content; arbitrary sheet annotations are not automatically discovered as collision rectangles |
| Lifecycle | document.create explicit project template; document.save_as explicit nonexisting absolute path (nonworkshared only); document.close discard_changes:true (background only); capture.export view/path_prefix/pixels, no existing prefix |
| Batches | batch.atomic steps consisting solely of operation/arguments, predefined mutations in one target document; controller dependency batch handles IDs, dependencies, prerequisites and result placeholders with individual receipts |
| Extensible API | compiled.query / compiled.modify assembly/type/purpose/expected_changes/arguments, trusted ICompiledOperation module in explicit CODEX_REVIT_PLUGIN_DIR; disabled by default |

See family-api.md for all family lifecycle and authoring arguments. Native schedule field/filter names and annotation references are document-specific and must be inspected, never guessed. Model/system restrictions propagate native errors and confirmed rollback boundaries.

## Trusted compiled execution

Build a .NET 8 Windows library referencing the installed Revit 2025 API assemblies and this package's DLL. Implement `CodexNativeRevit.ICompiledOperation.Execute(UIApplication, Document, JsonElement)` and return a JSON-serializable result. Put the compiled module under the explicitly enabled plugin directory. The add-in loads only paths within that directory and serializes calls in ExternalEvent context. `compiled.modify` receives the outer project transaction; the plugin must not start a conflicting project transaction. `compiled.query` receives a rollback TransactionGroup to undo same-document transactions the plugin opens.

This is full-trust in-process code, not a security sandbox. Query declarations do not prevent filesystem/network/process effects or operations on other documents. Rollback cannot reverse external side effects. Compilation uses installed/version-matched references; use api.lookup before choosing methods. Reusable established operations should become predefined reviewed code. Save/sync/publication must not be hidden inside normal compiled query or modification workflows; the trusted plugin author must observe that policy.

Capture prefixes must be absolute and contain no dot/extension in the filename component; use underscores. Revit truncates dotted prefixes. The service rejects both dotted and existing prefixes before export and requires actual nonempty output files. Project-created element snapshots in `data` may precede final regeneration; `actual_elements` is the authoritative post-regeneration project readback.

The optional standalone API client has not been implemented or tested: the signed-in Codex model catalog is not evidence of API-project Astra access. The native service and controller have no provider dependency.
