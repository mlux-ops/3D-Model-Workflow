using System.Reflection;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using CodexNativeRevit;

namespace CodexNativeRevit.CompiledProbe;

/// <summary>A detached, read-only sample for the installed Revit 2025 API.</summary>
public sealed class ProbeQuery : ICompiledOperation
{
    public object Execute(UIApplication app, Document document, JsonElement arguments)
    {
        if (!document.IsValidObject) throw new ArgumentException("Target document is invalid.");
        var session = DocumentRegistry.Id(document);
        if (arguments.TryGetProperty("document_session_id", out var requested) && requested.GetString() != session)
            throw new ArgumentException("Probe document_session_id does not match the explicit target.");

        object? viewSummary = null;
        if (arguments.TryGetProperty("view_unique_id", out var uid))
        {
            var view = document.GetElement(uid.GetString()) as View
                ?? throw new ArgumentException("view_unique_id must resolve to a native View in the target document.");
            object? categorySummary = null;
            if (arguments.TryGetProperty("category_id", out var categoryId))
            {
                var id = new ElementId(categoryId.GetInt64());
                var category = Category.GetCategory(document, id)
                    ?? throw new ArgumentException("category_id must resolve in the target document.");
                var canHide = view.CanCategoryBeHidden(id);
                categorySummary = new
                {
                    id = id.Value, name = category.Name, can_be_hidden = canHide,
                    hidden = canHide ? (bool?)view.GetCategoryHidden(id) : null
                };
            }
            viewSummary = new
            {
                document_session_id = session, id = view.Id.Value, unique_id = view.UniqueId,
                name = view.Name, view_type = view.ViewType.ToString(), is_template = view.IsTemplate,
                category = categorySummary
            };
        }
        else if (arguments.TryGetProperty("category_id", out _))
            throw new ArgumentException("category_id readback requires view_unique_id.");

        var units = document.GetUnits();
        // Materialize every result inside this API callback. No native wrappers or deferred LINQ escape.
        return new
        {
            probe = "read_only_native_api", document = DocumentRegistry.Describe(document),
            element_count_including_types = new FilteredElementCollector(document).GetElementCount(),
            api = new
            {
                revit_version = app.Application.VersionNumber, build = app.Application.VersionBuild,
                view_category_methods = typeof(View).GetMethods(BindingFlags.Instance | BindingFlags.Public)
                    .Where(method => method.Name is "GetCategoryHidden" or "SetCategoryHidden" or "CanCategoryBeHidden")
                    .Select(method => method.ToString()).ToArray()
            },
            units = new
            {
                native_length_unit = "feet", native_angle_unit = "radians",
                display_length_unit = units.GetFormatOptions(SpecTypeId.Length).GetUnitTypeId().TypeId,
                display_angle_unit = units.GetFormatOptions(SpecTypeId.Angle).GetUnitTypeId().TypeId
            },
            view = viewSummary, declared_model_effect = "none"
        };
    }
}

/// <summary>Performs one declared native modification in the bridge's outer transaction.</summary>
public sealed class ProbeModify : ICompiledOperation
{
    public object Execute(UIApplication app, Document document, JsonElement arguments)
    {
        if (!document.IsValidObject || !document.IsModifiable)
            throw new ArgumentException("ProbeModify requires the bridge's active target-document transaction.");
        var session = DocumentRegistry.Id(document);
        if (!arguments.TryGetProperty("document_session_id", out var requested) || requested.GetString() != session)
            throw new ArgumentException("A matching document_session_id is required.");
        var action = arguments.TryGetProperty("action", out var selector) ? selector.GetString() : "instance_comments";
        if (action == "view_orientation") return SetOrientation(document, arguments, session);
        if (action == "schedule_widths") return SetScheduleWidths(document, arguments, session);
        if (action == "create_elevation") return CreateElevation(document, arguments, session);
        if (action != "instance_comments") throw new ArgumentException("Unknown probe action.");
        var uid = arguments.GetProperty("element_unique_id").GetString();
        if (string.IsNullOrWhiteSpace(uid)) throw new ArgumentException("element_unique_id is required.");
        var element = document.GetElement(uid)
            ?? throw new ArgumentException("element_unique_id is missing or stale in the explicit target document.");
        if (element is ElementType) throw new ArgumentException("ProbeModify permits one instance only, not a shared type.");
        Util.Editable(element);
        var parameter = element.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
            ?? throw new ArgumentException("Element has no built-in instance Comments parameter.");
        if (parameter.IsReadOnly || parameter.StorageType != StorageType.String)
            throw new ArgumentException("Built-in instance Comments must be a writable string parameter.");
        var value = arguments.GetProperty("comment");
        if (value.ValueKind != JsonValueKind.String) throw new ArgumentException("comment must be a string.");
        var comment = value.GetString()!;
        var before = parameter.AsString();
        if (arguments.TryGetProperty("expected_before", out var expected))
        {
            if (expected.ValueKind is not JsonValueKind.String and not JsonValueKind.Null)
                throw new ArgumentException("expected_before must be a string or null.");
            if (before != expected.GetString()) throw new ArgumentException("Comments expected_before precondition failed.");
        }
        if (!parameter.Set(comment)) throw new InvalidOperationException("Native Comments setter returned false.");
        document.Regenerate();
        var after = parameter.AsString();
        if (after != comment) throw new InvalidOperationException("Native Comments readback did not match the requested string.");
        return new
        {
            probe = "one_instance_comment_update", document_session_id = session,
            element_id = element.Id.Value, element_unique_id = element.UniqueId,
            built_in_parameter = nameof(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS),
            parameter_id = parameter.Id.Value, before, after,
            declared_model_effect = "Only this instance's built-in Comments parameter is explicitly set."
        };
    }

    static object Orientation(ViewOrientation3D orientation) => new
    {
        eye = Util.Xyz(orientation.EyePosition), up = Util.Xyz(orientation.UpDirection),
        forward = Util.Xyz(orientation.ForwardDirection)
    };

    static object SetOrientation(Document document, JsonElement arguments, string session)
    {
        var uid = arguments.GetProperty("view_unique_id").GetString();
        if (string.IsNullOrWhiteSpace(uid)) throw new ArgumentException("view_unique_id is required.");
        var view = document.GetElement(uid) as View3D
            ?? throw new ArgumentException("view_unique_id must resolve to a native View3D in the explicit target.");
        Util.Editable(view);
        if (view.IsTemplate || view.IsLocked) throw new ArgumentException("View must be a non-template unlocked View3D. No implicit unlock.");
        var eye = Util.Point(arguments.GetProperty("eye"));
        var up = Util.Point(arguments.GetProperty("up"));
        var forward = Util.Point(arguments.GetProperty("forward"));
        if (up.GetLength() < 1e-9 || forward.GetLength() < 1e-9)
            throw new ArgumentException("Camera up and forward vectors must be nonzero.");
        up = up.Normalize();
        forward = forward.Normalize();
        if (Math.Abs(up.DotProduct(forward)) > 1e-6)
            throw new ArgumentException("Camera up and forward vectors must be perpendicular.");
        var before = Orientation(view.GetOrientation());
        view.SetOrientation(new ViewOrientation3D(eye, up, forward));
        document.Regenerate();
        return new
        {
            probe = "native_view_orientation", document_session_id = session,
            view_id = view.Id.Value, view_unique_id = view.UniqueId, before,
            after = Orientation(view.GetOrientation()), view.IsPerspective,
            declared_model_effect = "Only the explicitly identified unlocked 3D view's orientation is set."
        };
    }

    static object SetScheduleWidths(Document document, JsonElement arguments, string session)
    {
        var uid = arguments.GetProperty("schedule_unique_id").GetString();
        if (string.IsNullOrWhiteSpace(uid)) throw new ArgumentException("schedule_unique_id is required.");
        var schedule = document.GetElement(uid) as ViewSchedule
            ?? throw new ArgumentException("schedule_unique_id must resolve to a native ViewSchedule in the explicit target.");
        Util.Editable(schedule);
        if (schedule.IsTemplate) throw new ArgumentException("Schedule templates are not modified by the probe.");
        var widths = arguments.GetProperty("widths").EnumerateArray().Select(value => value.GetDouble()).ToArray();
        var order = schedule.Definition.GetFieldOrder().ToArray();
        if (widths.Length != order.Length || widths.Any(width => !double.IsFinite(width) || width <= 0))
            throw new ArgumentException("widths must give a finite positive internal-feet width for every schedule field in current field order.");
        foreach (var propertyName in new[] { "SheetColumnWidth", "GridColumnWidth" })
        {
            var property = typeof(ScheduleField).GetProperty(propertyName, BindingFlags.Instance | BindingFlags.Public);
            if (property?.SetMethod is not { IsPublic: true })
                throw new NotSupportedException("Installed Revit API has no public native setter: ScheduleField." + propertyName);
        }
        object Readback() => order.Select(id =>
        {
            var field = schedule.Definition.GetField(id);
            return new { field_id = id.IntegerValue, name = field.GetName(), grid_column_width = field.GridColumnWidth,
                sheet_column_width = field.SheetColumnWidth };
        }).ToArray();
        var before = Readback();
        for (var index = 0; index < order.Length; index++)
        {
            var field = schedule.Definition.GetField(order[index]);
            field.GridColumnWidth = widths[index];
            field.SheetColumnWidth = widths[index];
        }
        document.Regenerate();
        for (var index = 0; index < order.Length; index++)
        {
            var field = schedule.Definition.GetField(order[index]);
            if (Math.Abs(field.GridColumnWidth - widths[index]) > 1e-8 || Math.Abs(field.SheetColumnWidth - widths[index]) > 1e-8)
                throw new InvalidOperationException("Native schedule width readback did not match requested values.");
        }
        return new
        {
            probe = "native_schedule_field_widths", document_session_id = session,
            schedule_id = schedule.Id.Value, schedule_unique_id = schedule.UniqueId, before, after = Readback(),
            unit = "internal feet", declared_model_effect = "Sheet and grid widths of this explicitly identified native schedule's fields."
        };
    }

    static object CreateElevation(Document document, JsonElement arguments, string session)
    {
        var typeUid = arguments.GetProperty("elevation_type_unique_id").GetString();
        var planUid = arguments.GetProperty("plan_view_unique_id").GetString();
        if (string.IsNullOrWhiteSpace(typeUid) || string.IsNullOrWhiteSpace(planUid))
            throw new ArgumentException("Explicit elevation_type_unique_id and plan_view_unique_id are required.");
        var type = document.GetElement(typeUid) as ViewFamilyType
            ?? throw new ArgumentException("elevation_type_unique_id must resolve to a ViewFamilyType in the explicit target.");
        if (type.ViewFamily != ViewFamily.Elevation)
            throw new ArgumentException("Supplied ViewFamilyType must have ViewFamily.Elevation.");
        var plan = document.GetElement(planUid) as ViewPlan
            ?? throw new ArgumentException("plan_view_unique_id must resolve to a ViewPlan in the explicit target.");
        if (plan.IsTemplate || plan.GenLevel == null)
            throw new ArgumentException("Elevation host plan must be a non-template level-associated ViewPlan.");
        var index = arguments.GetProperty("index").GetInt32();
        if (index < 0 || index > 3) throw new ArgumentException("Elevation index must be from 0 through 3.");
        var name = arguments.GetProperty("name").GetString();
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("An explicit nonempty elevation name is required.");
        var scale = arguments.GetProperty("scale").GetInt32();
        if (scale < 1 || scale > 24000) throw new ArgumentException("Elevation scale must be from 1 through 24000.");
        var point = Util.Point(arguments.GetProperty("point"));
        var rotation = arguments.TryGetProperty("marker_rotation_radians", out var angle) ? angle.GetDouble() : 0;
        if (!double.IsFinite(rotation)) throw new ArgumentException("marker_rotation_radians must be finite.");
        var marker = ElevationMarker.CreateElevationMarker(document, type.Id, point, scale);
        if (!marker.IsAvailableIndex(index)) throw new ArgumentException("The new native elevation marker cannot use this index.");
        var view = marker.CreateElevation(document, plan.Id, index);
        // Rotate a populated native marker so the generated elevation shares its actual direction.
        if (rotation != 0)
            ElementTransformUtils.RotateElement(document, marker.Id, Line.CreateBound(point, point + XYZ.BasisZ), rotation);
        view.Name = name;
        view.Scale = scale;
        document.Regenerate();
        var crop = view.CropBox;
        return new
        {
            probe = "native_elevation_creation", document_session_id = session,
            elevation = new { document_session_id = session, id = view.Id.Value, unique_id = view.UniqueId, name = view.Name },
            marker = new { document_session_id = session, id = marker.Id.Value, unique_id = marker.UniqueId },
            host_plan = new { document_session_id = session, id = plan.Id.Value, unique_id = plan.UniqueId },
            index, requested_marker_rotation_radians = rotation,
            view_direction = Util.Xyz(view.ViewDirection), right_direction = Util.Xyz(view.RightDirection), up_direction = Util.Xyz(view.UpDirection),
            actual_scale = view.Scale, crop_box_active = view.CropBoxActive,
            crop_box = new
            {
                min = Util.Xyz(crop.Min), max = Util.Xyz(crop.Max),
                transform = new { origin = Util.Xyz(crop.Transform.Origin), basis_x = Util.Xyz(crop.Transform.BasisX),
                    basis_y = Util.Xyz(crop.Transform.BasisY), basis_z = Util.Xyz(crop.Transform.BasisZ) }
            },
            unit = "internal feet; rotation radians",
            declared_model_effect = "One native elevation marker and one native elevation view hosted by the explicitly identified plan."
        };
    }
}
