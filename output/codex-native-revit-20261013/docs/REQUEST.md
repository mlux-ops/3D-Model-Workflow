Build a comprehensive native Revit connection for Codex and GPT-6 Astra

Objective

Create a reliable connection that lets Codex inspect, create, place, modify and verify native Revit elements, author families, and complete drawing sheets. Support both predefined operations and extensible Revit API execution so the system is not limited to a fixed connector’s command list.

Deliver a working implementation, installation package, documentation and evidence from native Revit tests. Do not describe unimplemented capabilities as complete.

Existing findings

The previous read-only investigation established:

- Revit 2025 is installed and running.
- The installed pyRevit library reports version 6.4.0.26100+0515.
- The active pyRevit installation is under:
  C:\Users\cowey\AppData\Roaming\pyRevit-Master
- The separate OakPlank RevitMCP extension is under:
  C:\Users\cowey\AppData\Roaming\pyRevit\Extensions\RevitMCP.extension
- Connector logs are under:
  C:\Users\cowey\Documents\RevitMCP\server_logs
- The connector supports inspection, parameter changes, selection, deletion, drafting content and basic sheet placement.
- Its sheet-placement tool has no placement coordinates and places views at the sheet center.
- No general viewport-moving, family-placement, element-transform or family-geometry creation implementation was found in the inspected connector.
- October 13 kitchen work successfully placed drafting views on sheets ID1.0 and ID1.1, but this did not prove correct sheet composition.
- A later workflow continued through 32 text-note requests against an invalid view ID and ended with all 33 steps failed.
- Later view-activation and connection failures were separate problems.
- These findings were reconstructed from logs and source; the complete kitchen-chat transcript was not located.

Revalidate these facts before choosing implementation details. Historical element IDs and connection ports must not be treated as current.

Scope and operating boundaries

Build and test the connection. Initial discovery is read-only. Keep existing extensions, configuration and production models intact.

Use an isolated implementation folder and disposable project/family documents for native tests. Do not modify the production Wieland model as an installation or test step.

Never save, synchronize, publish, overwrite an RFA or replace a production model implicitly. Provide explicit operations for those actions.

Read applicable AGENTS.md and repository instructions before editing. Record implementation decisions, verification evidence and unresolved limitations in the project.

Phase 1 — Discover and select the execution foundation

Inspect:

- Exact Revit version/build and installed API assemblies.
- Existing add-ins, pyRevit engines, connector configuration and active listeners.
- Existing source and logs relevant to supported operations.
- Available Revit templates and representative cabinet families.
- Current official Autodesk API documentation and OpenAI integration documentation.
- Current pyRevit agent-runtime availability, compatibility and execution restrictions.

Evaluate whether the current pyRevit agent runtime can satisfy project editing, background family documents, family save/reload and reliable job tracking. Test uncertain capabilities rather than relying solely on release notes.

Preferred architecture:

Codex MCP client
↔ local bridge/controller
↔ C# add-in running inside Revit
↔ native Revit project and family documents

Use the same underlying operation service for an optional standalone GPT-6 Astra application. Verify current model availability and API requirements before implementing that application.

Keep model-provider logic outside the Revit add-in. Codex should be able to use the bridge without the add-in making its own OpenAI requests.

Write a capability matrix identifying:

- Supported by the native Revit API.
- Implemented and tested.
- Implemented but untested.
- Requires a Revit interface operation.
- Restricted by family/model conditions.
- Unsupported.

Deliver an architecture decision explaining whether to reuse, extend or supplement pyRevit. A custom C# bridge is preferred where the existing runtime cannot satisfy the required lifecycle.

Phase 2 — Build the reliable execution core

Implement a Revit add-in and local controller with:

- Authenticated local communication, bound to loopback by default.
- Versioned request and response schemas.
- Capability discovery.
- Persistent operation IDs and job-status queries.
- Structured errors and diagnostic logs.
- A single serialized execution queue for Revit API operations.
- ExternalEvent dispatch into a valid Revit API context.
- Explicit document targeting and document identity verification.
- Transactions, rollback and understandable undo entries.
- Cancellation at safe boundaries and honest timeout reporting.

Do not call Revit API methods from network/background threads. Perform external computation on detached data.

Each request should include the intended document and relevant operation preconditions. Resolve elements using document-qualified identifiers; support UniqueId where appropriate. Revalidate identifiers immediately before execution.

Return actual results, including created/changed/deleted identifiers, before/after values, warnings, failures and transaction status.

Distinguish:

- Queued.
- Running.
- Completed.
- Failed.
- Rolled back.
- Cancelled.
- Unknown completion.

A timeout does not prove rollback. Reconcile job receipts and native state before retrying a mutation. Do not replay placement, deletion, save or synchronization blindly.

Phase 3 — Implement model inspection

Provide efficient queries for:

- Open documents and active document.
- Active view and selection.
- Categories, families, types and instances.
- Parameters, including identity, storage type, units, instance/type ownership and writability.
- Levels, offsets, phases, design options and worksets.
- Hosts, references, dependent elements and relationships.
- Locations, transforms, bounding boxes and relevant geometry.
- Linked-model instances and coordinate transforms.
- Views, sheets, viewports and placed schedules.
- Relevant warnings and editability restrictions.

Use filtered, paginated and batched queries. Return summaries first and detailed geometry only when needed.

Make units and coordinate systems explicit. Support conversions between project, shared, linked-instance and sheet coordinates where applicable.

Provide version-correct API lookup and runtime type inspection so generated code can verify methods before using them.

Phase 4 — Implement native 3D placement and modification

Family placement:

- Load an RFA with an explicit conflict/overwrite policy.
- Discover and activate family types.
- Identify placement type before choosing a creation method.
- Support level-based, unhosted, wall-hosted, face-based, work-plane-based and curve-based placement where supported.
- Support batch placement with coordinates, units, orientation, levels, offsets and hosts.
- Return the actual resulting location and host after regeneration.
- Report unsupported placement types explicitly.

Element modification:

- Move, rotate, copy and mirror supported elements.
- Change family types.
- Set writable instance/type parameters.
- Duplicate types before modification when requested.
- Flip facing/hand orientation where supported.
- Edit supported location curves and level/offset properties.
- Delete with dependency reporting.
- Handle pinned elements, groups, ownership and constraints explicitly.

Do not unpin elements or change group/type definitions as a hidden side effect.

System elements:

Implement native creation and editing for prioritized categories, including walls and floors, then extend according to the capability matrix. Support additional roof, ceiling, opening, structural or MEP operations only when implemented and tested.

Do not use generic mesh or DirectShape objects as silent substitutes for native walls, cabinets, floors or parametric families. Offer such representations only as an explicit alternative.

Kitchen acceptance workflow:

Using representative families in a disposable project:

1. Inspect a selected wall and cabinet types.
2. Place a cabinet run with explicit dimensions and orientation.
3. Modify supported width, height and depth parameters.
4. Place representative appliances or fixtures with correct hosting.
5. Move, rotate, copy and change types.
6. Verify positions, dimensions, hosts and clearances against supplied requirements.
7. Confirm unrelated elements and types were not changed.

Do not invent design clearances or manufacturer dimensions.

Phase 5 — Implement family authoring

Treat family editing as a separate document lifecycle.

Support:

- Create a family from an explicit template.
- Open or edit an existing editable family.
- Inspect category, placement type, types and parameters.
- Create and modify supported extrusions, revolutions, sweeps, blends and voids.
- Create reference planes and supported dimensions/constraints.
- Add parameters and formulas.
- Associate supported geometry/material parameters.
- Manage nested families where supported.
- Validate geometry and flex types.
- Save to an explicit new path.
- Reload into a test project with an explicit replacement policy.

Family documents require their own transactions and lifecycle handling. Do not imply that a project transaction can roll back a saved family file or a multi-document workflow.

Distinguish true parametric authoring from resizing an instance through existing parameters.

Never assume host changes, category changes or constraint reconstruction can be performed universally. Report family-specific restrictions.

Phase 6 — Implement 2D documentation and sheet composition

Inspection:

- Enumerate sheets, titleblocks, viewports and schedule instances.
- Read viewport centers, view bounds and label bounds.
- Read sheet-coordinate extents and relevant titleblock information.
- Identify pinned elements and existing placements.
- Support configurable printable/content regions; do not assume every titleblock defines them identically.

Placement and layout:

- Place views at explicit sheet coordinates.
- Move existing viewports using native Revit methods.
- Place and reposition real schedule instances.
- Apply supported viewport rotation and type changes.
- Align views and distribute spacing.
- Position supported viewport labels.
- Detect overlaps among views, labels, schedules and reserved regions.
- Provide a proposed layout before applying it.
- Return actual post-regeneration bounds and positions.

Views and annotations:

- Create/duplicate supported views.
- Set supported scales, crop regions, section boxes and templates.
- Create supported dimensions, tags, text notes, detail lines and filled regions.
- Modify or recreate annotations where the API requires it.
- Manage supported schedule fields, filters, sorting and formatting.

Distinguish a real ViewSchedule from a drafting view containing manually drawn table content.

Kitchen sheet acceptance workflow:

In a disposable project, arrange representative plans, elevations and schedules on test equivalents of ID1.0 and ID1.1. Verify coordinates, alignment, labels, overlaps and content-region boundaries numerically and visually.

Phase 7 — Add flexible API execution

Provide an extensible execution path for operations not yet covered by predefined tools.

Preferred approach:

- Python execution against the supported Revit API, if a compatible host provides the required lifecycle.
- Otherwise, an explicit compiled C# operation mechanism with version-matched references.

Expose separate query and modification operations, with declared document scope, purpose and expected changes.

Generated code must use version-correct API lookup, return structured results and report actual changes. Established production workflows should migrate into tested operations rather than repeatedly regenerate code.

Do not claim arbitrary in-process Python or C# is securely sandboxed. Transaction rollback protects model changes within its scope; it does not undo filesystem, network or other process effects. Document the trust boundary and execution policy.

Keep saving, synchronization and external publication explicit.

Phase 8 — Improve orchestration and efficiency

Implement task-level batches so cabinet runs and sheet layouts do not require one model round trip per element.

Workflows must support:

- Explicit dependency relationships.
- Prerequisite checks.
- Stop-on-failure for dependent steps.
- Clear partial-completion reporting.
- Optional atomic transactions where technically possible.
- Refreshing identifiers after recreation, deletion or document changes.
- Operation receipts and recovery queries.

Support independent computation outside Revit while serializing native API operations.

Measure elapsed time, tool round trips and relevant payload sizes for representative workflows. Report measured results without invented speed claims.

Phase 9 — Verify in native Revit

Static compilation or mocked tests do not prove native execution.

Run targeted native tests in disposable documents for:

- Model queries.
- Family loading and several placement types.
- Movement, rotation, copying and parameter changes.
- Supported system-element creation.
- Family authoring, save, reopen, reload and placement.
- Viewport and schedule positioning.
- Sheet-layout verification.
- Invalid/stale element identifiers.
- Pinned or constrained elements.
- Dependent-step failure handling.
- Disconnects, timeouts and unknown-completion recovery.

Verify that successful edits produce the intended native state and failed operations respect the declared rollback boundary.

Include representative numerical readbacks and unaltered view captures. Keep technical correctness separate from visual/design acceptance.

Phase 10 — Deliver and install

Provide:

- Source code.
- Revit-version-specific build artifacts.
- MCP/controller configuration.
- Installer or installation script.
- Backup and uninstall instructions.
- User operating guide.
- Tool/API reference.
- Capability matrix.
- Native test report and evidence.
- Known limitations and unresolved blockers.

Preserve the existing RevitMCP installation. Make connector identity clear so Codex does not accidentally call the older server.

If installation requires restarting Revit, prepare the package and explain the requirement without closing an unsaved session.

Completion standard

The project is complete only when Codex can demonstrate the supported 3D and 2D workflows through the new connection in native Revit, with verified results and recoverable failures.

Report exactly what works, what remains conditional and what is unsupported. Do not claim unrestricted access to every Revit interface command.

Begin with discovery and the architecture decision, then implement the execution core and a vertical slice: inspect a cabinet type, place it, modify it, verify it, and position its view on a test sheet. Expand from that proven foundation until the agreed capability matrix is satisfied.