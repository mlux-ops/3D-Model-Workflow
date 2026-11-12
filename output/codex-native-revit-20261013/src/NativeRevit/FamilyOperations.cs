using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

namespace CodexNativeRevit;

/// <summary>Family document lifecycle and conventional-family authoring. Called only in ExternalEvent context.</summary>
public static class FamilyOperations
{
    private static readonly HashSet<string> Ops = new(StringComparer.Ordinal)
    {
        "family.create", "family.open", "family.edit", "family.inspect", "family.save", "family.close",
        "family.load", "family.reload", "family.geometry.inspect", "family.extrusion.create", "family.extrusion.modify",
        "family.revolution.create", "family.blend.create", "family.sweep.create", "family.reference_plane.create",
        "family.dimension.create", "family.alignment.create", "family.parameter.add", "family.parameter.set",
        "family.parameter.formula", "family.parameter.associate", "family.type.create", "family.type.set", "family.type.flex"
    };
    public static IReadOnlyCollection<string> Names => Ops;
    public static bool Handles(string op) => Ops.Contains(op);

    public static object Execute(UIApplication app, Document? doc, string op, JsonElement a)
    {
        if (!Handles(op)) throw new NotSupportedException(op);
        if (op == "family.create")
        {
            string template = ExistingPath(a, "template", ".rft");
            Document created = app.Application.NewFamilyDocument(template)
                ?? throw new InvalidOperationException("Revit did not create a family document.");
            DocumentRegistry.Id(created);
            return new { session_id = DocumentRegistry.Id(created), document = DocumentRegistry.Describe(created), template, transaction_status = "not_applicable", saved = false };
        }
        if (op == "family.open")
        {
            string path = ExistingPath(a, "path", ".rfa");
            var alreadyOpen = app.Application.Documents.Cast<Document>().FirstOrDefault(d =>
                !string.IsNullOrEmpty(d.PathName) && string.Equals(Path.GetFullPath(d.PathName), path, StringComparison.OrdinalIgnoreCase));
            if (alreadyOpen != null)
                return new { session_id = DocumentRegistry.Id(alreadyOpen), document = DocumentRegistry.Describe(alreadyOpen), opened = false, transaction_status = "not_applicable" };
            var opened = app.Application.OpenDocumentFile(path);
            DocumentRegistry.Id(opened);
            if (!opened.IsFamilyDocument) throw new InvalidOperationException("Opened document is not a family document.");
            return new { session_id = DocumentRegistry.Id(opened), document = DocumentRegistry.Describe(opened), opened = true, transaction_status = "not_applicable" };
        }
        Document d = doc ?? throw new ArgumentException("An explicit document target is required.");
        if (!d.IsValidObject) throw new InvalidOperationException("Document is no longer open.");
        if (op == "family.edit")
        {
            if (d.IsModifiable || d.IsReadOnly) throw new InvalidOperationException("EditFamily requires a writable document with no open transaction.");
            var family = Util.Element(d, a.GetProperty("family")) as Family ?? throw new ArgumentException("family must identify a loadable Family.");
            if (!family.IsEditable || family.IsInPlace) throw new NotSupportedException("Family is in-place or not editable.");
            Document edited = d.EditFamily(family);
            DocumentRegistry.Id(edited);
            return new { session_id = DocumentRegistry.Id(edited), document = DocumentRegistry.Describe(edited), source_family = Util.Describe(family), transaction_status = "not_applicable", saved = false };
        }
        if (op == "family.load") return LoadFile(d, a);
        if (op == "family.reload")
        {
            var source = DocumentRegistry.Resolve(Required(a, "source_document_id"));
            RequireFamily(source);
            if (source == d) throw new ArgumentException("Source and target documents must differ.");
            if (source.IsModifiable || d.IsModifiable || d.IsReadOnly)
                throw new InvalidOperationException("Reload requires documents outside transactions and a writable target.");
            var policy = new LoadPolicy(Required(a, "replacement_policy"));
            if (policy.Name == "reject" && new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>()
                .Any(f => f.Name == source.OwnerFamily.Name))
                throw new InvalidOperationException("Replacement rejected: target already contains this family name.");
            try
            {
                Family loaded = source.LoadFamily(d, policy) ?? throw new InvalidOperationException("Revit declined family reload.");
                return new { source_document = DocumentRegistry.Describe(source), target_document = DocumentRegistry.Describe(d),
                    family = Util.Describe(loaded), replacement_policy = policy.Name,
                    transaction_status = "revit_managed", saved = false, external_boundary = "Target family load cannot be rolled back by a source-family transaction." };
            }
            catch (Exception ex)
            {
                throw new UnknownCompletionException("Family reload entered its native multi-document call; reconcile target family state before retrying. " + ex.Message, ex);
            }
        }
        RequireFamily(d);
        if (op == "family.inspect") return Inspect(d);
        if (op == "family.geometry.inspect") return Geometry(d);
        if (op == "family.save") return Save(d, a);
        if (op == "family.close")
        {
            if (d.IsModifiable) throw new InvalidOperationException("Cannot close with an open transaction.");
            if (app.ActiveUIDocument?.Document == d) throw new NotSupportedException("The active UI document cannot be closed by Document.Close; activate another document first.");
            if (!a.TryGetProperty("discard_changes", out var discard) || discard.ValueKind != JsonValueKind.True)
                throw new ArgumentException("family.close requires discard_changes:true. Save explicitly first if needed.");
            string identity = DocumentRegistry.Id(d);
            bool closed = d.Close(false);
            if (!closed) throw new InvalidOperationException("Revit declined document close.");
            return new { document_id = identity, closed, saved = false, transaction_status = "not_applicable" };
        }
        if (op == "family.type.flex") return Flex(d, a);
        return Mutate(d, op, () => Author(app, d, op, a));
    }

    private static object Author(UIApplication app, Document d, string op, JsonElement a)
    {
        FamilyManager fm = d.FamilyManager;
        switch (op)
        {
            case "family.extrusion.create":
            {
                Feet(a);
                var plane = Sketch(d, a);
                double end = Util.Num(a, "end", 0);
                if (Math.Abs(end) < app.Application.ShortCurveTolerance) throw new ArgumentException("end must exceed Revit's short-curve tolerance.");
                var e = d.FamilyCreate.NewExtrusion(Util.Bool(a, "solid", true), Loops(a.GetProperty("profile")), plane, end);
                if (a.TryGetProperty("start", out var start)) e.StartOffset = start.GetDouble();
                d.Regenerate();
                return new { element = Util.Describe(e), sketch_plane = Util.Describe(plane), is_solid = e.IsSolid, start = e.StartOffset, end = e.EndOffset, geometry = GeometryElement(e), units = "feet" };
            }
            case "family.extrusion.modify":
            {
                Feet(a);
                var e = Util.Element(d, a.GetProperty("element")) as Extrusion ?? throw new ArgumentException("element is not an extrusion.");
                Util.Editable(e);
                var before = new { start = e.StartOffset, end = e.EndOffset };
                if (a.TryGetProperty("start", out var start)) e.StartOffset = start.GetDouble();
                if (a.TryGetProperty("end", out var end)) e.EndOffset = end.GetDouble();
                d.Regenerate();
                return new { element = Util.Describe(e), before, after = new { start = e.StartOffset, end = e.EndOffset }, units = "feet" };
            }
            case "family.revolution.create":
            {
                Feet(a);
                var plane = Sketch(d, a);
                var axis = a.GetProperty("axis");
                var e = d.FamilyCreate.NewRevolution(Util.Bool(a, "solid", true), Loops(a.GetProperty("profile")), plane,
                    Line.CreateBound(Util.Point(axis[0]), Util.Point(axis[1])), Util.Num(a, "start_angle", 0), Util.Num(a, "end_angle", Math.PI * 2));
                d.Regenerate();
                return new { element = Util.Describe(e), sketch_plane = Util.Describe(plane), is_solid = e.IsSolid, geometry = GeometryElement(e), angle_units = "radians", units = "feet" };
            }
            case "family.blend.create":
            {
                Feet(a);
                var plane = Sketch(d, a);
                var e = d.FamilyCreate.NewBlend(Util.Bool(a, "solid", true), Loop(a.GetProperty("profile1")), Loop(a.GetProperty("profile2")), plane);
                d.Regenerate();
                return new { element = Util.Describe(e), sketch_plane = Util.Describe(plane), is_solid = e.IsSolid, bottom = e.BottomOffset, top = e.TopOffset, geometry = GeometryElement(e), units = "feet" };
            }
            case "family.sweep.create":
            {
                Feet(a);
                var pathPlane = Sketch(d, a);
                var path = Curves(a.GetProperty("path"), false);
                SweepProfile profile = app.Application.Create.NewCurveLoopsProfile(Loops(a.GetProperty("profile")));
                string placement = Util.Get(a, "profile_location", "Start");
                if (!Enum.TryParse<ProfilePlaneLocation>(placement, false, out var location))
                    throw new ArgumentException("profile_location must be Start or End.");
                var e = d.FamilyCreate.NewSweep(Util.Bool(a, "solid", true), path, pathPlane, profile,
                    checked((int)Util.Num(a, "profile_curve_index", 0)), location);
                d.Regenerate();
                return new { element = Util.Describe(e), sketch_plane = Util.Describe(pathPlane), is_solid = e.IsSolid, geometry = GeometryElement(e), units = "feet" };
            }
            case "family.reference_plane.create":
            {
                Feet(a);
                View view = Util.Element(d, a.GetProperty("view")) as View ?? throw new ArgumentException("view must identify a family view.");
                var rp = d.FamilyCreate.NewReferencePlane(Util.Point(a.GetProperty("bubble_end")), Util.Point(a.GetProperty("free_end")), Util.Point(a.GetProperty("cut_vector")), view);
                if (a.TryGetProperty("name", out var name)) rp.Name = name.GetString() ?? "";
                d.Regenerate();
                return new { element = Util.Describe(rp), reference = rp.GetReference().ConvertToStableRepresentation(d), normal = Xyz(rp.Normal), bubble_end = Xyz(rp.BubbleEnd), free_end = Xyz(rp.FreeEnd), units = "feet" };
            }
            case "family.dimension.create":
            {
                Feet(a);
                View view = Util.Element(d, a.GetProperty("view")) as View ?? throw new ArgumentException("view must identify a family view.");
                var refs = new ReferenceArray();
                foreach (var r in a.GetProperty("references").EnumerateArray()) refs.Append(Ref(d, r));
                var line = a.GetProperty("line");
                Dimension dim = d.FamilyCreate.NewLinearDimension(view, Line.CreateBound(Util.Point(line[0]), Util.Point(line[1])), refs);
                if (a.TryGetProperty("label_parameter", out var label)) dim.FamilyLabel = Parameter(fm, label.GetString() ?? "");
                if (Util.Bool(a, "locked", false)) dim.IsLocked = true;
                d.Regenerate();
                return new { element = Util.Describe(dim), value = dim.Value, label = dim.FamilyLabel?.Definition.Name, locked = dim.IsLocked, units = "feet" };
            }
            case "family.alignment.create":
            {
                View view = Util.Element(d, a.GetProperty("view")) as View ?? throw new ArgumentException("view must identify a family view.");
                var dim = d.FamilyCreate.NewAlignment(view, Ref(d, a.GetProperty("reference1")), Ref(d, a.GetProperty("reference2")));
                d.Regenerate();
                return new { element = Util.Describe(dim), locked = dim.IsLocked };
            }
            case "family.parameter.add":
            {
                var p = fm.AddParameter(Required(a, "name"), Forge(a, "group", true), Forge(a, "data_type", false), Util.Bool(a, "instance", false));
                return ParameterInfo(p);
            }
            case "family.parameter.set":
            {
                FamilyType current = SelectType(fm, a);
                var p = Parameter(fm, Required(a, "parameter"));
                object? before = Value(current, p);
                Set(fm, p, a.GetProperty("value"), Util.Bool(a, "value_string", false));
                d.Regenerate();
                return new { parameter = ParameterInfo(p), type = fm.CurrentType.Name, before, after = Value(fm.CurrentType, p), numeric_units = "Revit internal units for data_type" };
            }
            case "family.parameter.formula":
            {
                var p = Parameter(fm, Required(a, "parameter"));
                string? before = p.Formula;
                string? formula = a.GetProperty("formula").ValueKind == JsonValueKind.Null ? null : a.GetProperty("formula").GetString();
                fm.SetFormula(p, formula);
                d.Regenerate();
                return new { parameter = ParameterInfo(p), before, after = p.Formula };
            }
            case "family.parameter.associate":
            {
                Element e = Util.Element(d, a.GetProperty("element"));
                Util.Editable(e);
                Parameter? ep;
                if (a.TryGetProperty("element_parameter_builtin", out var builtIn))
                    ep = e.get_Parameter(Enum.Parse<BuiltInParameter>(builtIn.GetString()!, false));
                else if (a.TryGetProperty("element_parameter_id", out var id))
                    ep = e.Parameters.Cast<Parameter>().FirstOrDefault(p => p.Id.Value == id.GetInt64());
                else
                {
                    string name = Required(a, "element_parameter");
                    var matches = e.GetParameters(name);
                    if (matches.Count != 1) throw new ArgumentException("Element parameter name is missing or ambiguous; supply element_parameter_id.");
                    ep = matches[0];
                }
                if (ep == null) throw new ArgumentException("Element parameter not found.");
                FamilyParameter? fp = a.GetProperty("family_parameter").ValueKind == JsonValueKind.Null ? null : Parameter(fm, a.GetProperty("family_parameter").GetString() ?? "");
                if (!fm.CanElementParameterBeAssociated(ep)) throw new NotSupportedException("This element parameter cannot be associated with a family parameter.");
                fm.AssociateElementParameterToFamilyParameter(ep, fp);
                var actual = fm.GetAssociatedFamilyParameter(ep);
                return new { element = Util.Describe(e), element_parameter_id = ep.Id.Value, associated_family_parameter = actual == null ? null : ParameterInfo(actual) };
            }
            case "family.type.create":
            {
                FamilyType type = fm.NewType(Required(a, "name"));
                ApplyValues(fm, a);
                d.Regenerate();
                return TypeInfo(fm, type);
            }
            case "family.type.set":
            {
                Required(a, "name");
                var before = fm.CurrentType?.Name;
                FamilyType type = SelectType(fm, a, "name");
                ApplyValues(fm, a);
                d.Regenerate();
                return new { before, after = TypeInfo(fm, type), geometry = Geometry(d) };
            }
            default: throw new NotSupportedException(op);
        }
    }

    private static object Mutate(Document d, string name, Func<object> action)
    {
        if (d.IsReadOnly || d.IsModifiable) throw new InvalidOperationException("Family authoring requires a writable document with no open transaction.");
        using var tx = new Transaction(d, "Codex " + name);
        if (tx.Start() != TransactionStatus.Started) throw new InvalidOperationException("Family transaction did not start.");
        var failures = new RollBackErrors();
        tx.SetFailureHandlingOptions(tx.GetFailureHandlingOptions().SetFailuresPreprocessor(failures).SetClearAfterRollback(true));
        try
        {
            object result = action();
            TransactionStatus status = tx.Commit();
            if (status != TransactionStatus.Committed) throw new InvalidOperationException("Family transaction status: " + status + ". " + string.Join("; ", failures.Messages));
            return new { result, transaction_status = "committed", saved = false, document = DocumentRegistry.Describe(d), warnings = Warnings(d) };
        }
        catch (Exception ex)
        {
            TransactionStatus status;
            try
            {
                status = tx.GetStatus();
                if (status == TransactionStatus.Started) status = tx.RollBack();
            }
            catch (Exception rollbackError)
            {
                throw new UnknownCompletionException("Family transaction rollback/status could not be confirmed. Reconcile native state. " + rollbackError.Message, ex);
            }
            if (status == TransactionStatus.RolledBack) throw new RolledBackException("Family operation rolled back: " + ex.Message, ex);
            throw new UnknownCompletionException("Family operation raised an exception with transaction status " + status + "; native changes may persist. Reconcile native state. " + ex.Message, ex);
        }
    }

    private static object LoadFile(Document target, JsonElement a)
    {
        string path = ExistingPath(a, "path", ".rfa");
        var options = new LoadPolicy(Required(a, "replacement_policy"));
        return Mutate(target, "family.load", () =>
        {
            bool loaded = target.LoadFamily(path, options, out var family);
            return new { loaded, family = family == null ? null : Util.Describe(family), path, replacement_policy = options.Name,
                outcome = loaded ? "loaded" : "unchanged_or_rejected", callback_decisions = options.Decisions.ToArray() };
        });
    }

    private static object Save(Document d, JsonElement a)
    {
        if (d.IsModifiable || d.IsReadOnly) throw new InvalidOperationException("Save requires a writable family outside transactions.");
        string raw = Required(a, "path");
        if (!Path.IsPathFullyQualified(raw)) throw new ArgumentException("Save path must be absolute.");
        string path = Path.GetFullPath(raw);
        if (!path.EndsWith(".rfa", StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Save path must end in .rfa.");
        if (File.Exists(path)) throw new IOException("Family save is new-path only. Existing files are never overwritten.");
        if (!Directory.Exists(Path.GetDirectoryName(path))) throw new DirectoryNotFoundException("Destination directory must already exist.");
        var options = new SaveAsOptions { OverwriteExistingFile = false, Compact = Util.Bool(a, "compact", false) };
        try
        {
            d.SaveAs(path, options);
            var file = new FileInfo(path);
            if (!file.Exists || file.Length == 0) throw new IOException("SaveAs returned without a nonempty file at the requested path.");
            return new { document = DocumentRegistry.Describe(d), path, bytes = file.Length, saved = true, transaction_status = "not_applicable",
                external_boundary = "Saved file is durable and is not undone by a document transaction rollback." };
        }
        catch (Exception ex)
        {
            throw new UnknownCompletionException("Family SaveAs entered its native file call; reconcile the requested file and document path before retrying. " + ex.Message, ex);
        }
    }

    private static object Flex(Document d, JsonElement a)
    {
        if (d.IsReadOnly || d.IsModifiable) throw new InvalidOperationException("Flex requires a writable family outside transactions.");
        var scenarios = a.GetProperty("types").EnumerateArray().ToArray();
        if (scenarios.Length == 0 || scenarios.Length > 100) throw new ArgumentException("Flex requires between 1 and 100 explicit type scenarios.");
        foreach (var scenario in scenarios) Required(scenario, "name");
        var snapshots = new List<object>();
        using var group = new TransactionGroup(d, "Codex family flex (reversible validation)");
        if (group.Start() != TransactionStatus.Started) throw new InvalidOperationException("Flex transaction group did not start.");
        try
        {
            foreach (var item in scenarios)
            {
                object snapshot = Mutate(d, "family.type.flex", () =>
                {
                    FamilyType type = SelectType(d.FamilyManager, item, "name");
                    ApplyValues(d.FamilyManager, item);
                    d.Regenerate();
                    return new { type = TypeInfo(d.FamilyManager, type), geometry = Geometry(d), warnings = Warnings(d) };
                });
                snapshots.Add(snapshot);
            }
            if (group.RollBack() != TransactionStatus.RolledBack) throw new InvalidOperationException("Flex rollback did not finish.");
            return new { snapshots, transaction_status = "rolled_back", original_state_restored = true, saved = false,
                validation_scope = "Parameter readbacks and native form solid bounds/volumes after regeneration. No visual or hosted-placement acceptance." };
        }
        catch (Exception ex)
        {
            TransactionStatus status;
            try
            {
                status = group.GetStatus();
                if (status == TransactionStatus.Started) status = group.RollBack();
            }
            catch (Exception rollbackError)
            {
                throw new UnknownCompletionException("Family flex group rollback/status could not be confirmed. " + rollbackError.Message, ex);
            }
            if (status == TransactionStatus.RolledBack) throw new RolledBackException("Family flex failed and group rollback was confirmed: " + ex.Message, ex);
            throw new UnknownCompletionException("Family flex failed with group status " + status + "; original-state restoration is unconfirmed.", ex);
        }
    }

    private static object Inspect(Document d)
    {
        Family family = d.OwnerFamily;
        FamilyManager fm = d.FamilyManager;
        return new { document = DocumentRegistry.Describe(d), family = Util.Describe(family), category = family.FamilyCategory?.Name,
            category_id = family.FamilyCategory?.Id.Value, placement_type = family.FamilyPlacementType.ToString(), family.IsEditable,
            current_type = fm.CurrentType?.Name, parameters = fm.Parameters.Cast<FamilyParameter>().Select(ParameterInfo).ToArray(),
            types = fm.Types.Cast<FamilyType>().Select(t => TypeInfo(fm, t)).ToArray(),
            nested_families = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().Where(f => f.Id != family.Id).Select(Util.Describe).ToArray(),
            views = new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate)
                .Select(v => new { element = Util.Describe(v), view_type = v.ViewType.ToString() }).ToArray(), warnings = Warnings(d) };
    }

    private static object ParameterInfo(FamilyParameter p) => new
    {
        id = p.Id.Value, name = p.Definition.Name, storage_type = p.StorageType.ToString(),
        data_type = p.Definition.GetDataType().TypeId, group = p.Definition.GetGroupTypeId().TypeId,
        instance = p.IsInstance, read_only = p.IsReadOnly, shared = p.IsShared, reporting = p.IsReporting, formula = p.Formula
    };

    private static object TypeInfo(FamilyManager fm, FamilyType type) => new
    {
        name = type.Name,
        values = fm.Parameters.Cast<FamilyParameter>().Select(p => new { parameter = ParameterInfo(p), value = Value(type, p) }).ToArray()
    };

    private static object? Value(FamilyType type, FamilyParameter p)
    {
        if (!type.HasValue(p)) return null;
        return p.StorageType switch
        {
            StorageType.Double => type.AsDouble(p), StorageType.Integer => type.AsInteger(p),
            StorageType.String => type.AsString(p), StorageType.ElementId => type.AsElementId(p)?.Value, _ => null
        };
    }

    private static FamilyParameter Parameter(FamilyManager fm, string key)
    {
        var matches = fm.Parameters.Cast<FamilyParameter>().Where(p => p.Definition.Name == key || p.Id.Value.ToString(System.Globalization.CultureInfo.InvariantCulture) == key).ToArray();
        if (matches.Length != 1) throw new ArgumentException("Family parameter is missing or ambiguous: " + key);
        return matches[0];
    }

    private static FamilyType SelectType(FamilyManager fm, JsonElement a, string key = "type")
    {
        string name = Util.Get(a, key, "");
        if (name.Length > 0)
            fm.CurrentType = fm.Types.Cast<FamilyType>().SingleOrDefault(t => t.Name == name)
                ?? throw new ArgumentException("Family type not found: " + name);
        return fm.CurrentType ?? throw new InvalidOperationException("Create a family type before setting values.");
    }

    private static void ApplyValues(FamilyManager fm, JsonElement a)
    {
        if (!a.TryGetProperty("values", out var values)) return;
        foreach (var item in values.EnumerateObject()) Set(fm, Parameter(fm, item.Name), item.Value, false);
    }

    private static void Set(FamilyManager fm, FamilyParameter p, JsonElement value, bool displayString)
    {
        if (p.IsReadOnly || p.IsDeterminedByFormula || p.IsReporting) throw new InvalidOperationException("Parameter is read-only, reporting, or determined by formula: " + p.Definition.Name);
        if (displayString)
        {
            if (value.ValueKind != JsonValueKind.String) throw new ArgumentException("value_string requires a string.");
            fm.SetValueString(p, value.GetString()!);
            return;
        }
        switch (p.StorageType)
        {
            case StorageType.Double: fm.Set(p, value.GetDouble()); break;
            case StorageType.Integer: fm.Set(p, value.GetInt32()); break;
            case StorageType.String: fm.Set(p, value.GetString() ?? ""); break;
            case StorageType.ElementId: fm.Set(p, new ElementId(value.GetInt64())); break;
            default: throw new NotSupportedException("Parameter storage type cannot be assigned.");
        }
    }

    private static ForgeTypeId Forge(JsonElement a, string key, bool group)
    {
        string s = Required(a, key);
        if (s.Contains(':')) return new ForgeTypeId(s);
        Type owner = group ? typeof(GroupTypeId) : typeof(SpecTypeId);
        if (!group && s == "Text") return SpecTypeId.String.Text;
        if (!group && s == "YesNo") return SpecTypeId.Boolean.YesNo;
        var property = owner.GetProperty(s, System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static);
        if (property?.GetValue(null) is ForgeTypeId id) return id;
        throw new ArgumentException("Use a full ForgeTypeId or a known " + owner.Name + " property: " + s);
    }

    private static object Geometry(Document d) => new
    {
        units = "feet", volume_units = "cubic_feet",
        forms = new FilteredElementCollector(d).OfClass(typeof(GenericForm)).Cast<GenericForm>()
            .Select(e => new { element = Util.Describe(e), is_solid = e.IsSolid, geometry = GeometryElement(e) }).ToArray()
    };

    private static object GeometryElement(Element e)
    {
        BoundingBoxXYZ? box = e.get_BoundingBox(null);
        var solids = new List<object>();
        var geometry = e.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine });
        if (geometry != null) CollectSolids(geometry, solids);
        return new { bounds = box == null ? null : new { min = Xyz(box.Min), max = Xyz(box.Max), transform_origin = Xyz(box.Transform.Origin),
            transform_x = Xyz(box.Transform.BasisX), transform_y = Xyz(box.Transform.BasisY), transform_z = Xyz(box.Transform.BasisZ) }, solids };
    }

    private static void CollectSolids(GeometryElement geometry, List<object> solids)
    {
        foreach (GeometryObject g in geometry)
            if (g is Solid s) solids.Add(new { volume = s.Volume, faces = s.Faces.Size, edges = s.Edges.Size });
            else if (g is GeometryInstance instance) CollectSolids(instance.GetInstanceGeometry(), solids);
    }

    private static object[] Warnings(Document d) => d.GetWarnings().Select(w => (object)new
    {
        description = w.GetDescriptionText(), severity = w.GetSeverity().ToString(), elements = w.GetFailingElements().Select(id => id.Value).ToArray()
    }).ToArray();

    private static SketchPlane Sketch(Document d, JsonElement a)
    {
        if (a.TryGetProperty("sketch_plane", out var existing))
            return Util.Element(d, existing) as SketchPlane ?? throw new ArgumentException("sketch_plane must identify a SketchPlane.");
        var plane = a.GetProperty("plane");
        return SketchPlane.Create(d, Plane.CreateByNormalAndOrigin(Util.Point(plane.GetProperty("normal")), Util.Point(plane.GetProperty("origin"))));
    }

    // Profiles are arrays of loops; a loop is points or explicit ordered line/arc descriptions.
    private static CurveArrArray Loops(JsonElement profile)
    {
        var loops = new CurveArrArray();
        foreach (var loop in profile.EnumerateArray()) loops.Append(Loop(loop));
        if (loops.Size == 0) throw new ArgumentException("At least one profile loop is required.");
        return loops;
    }

    private static CurveArray Loop(JsonElement loop) => Curves(loop, true);
    private static CurveArray Curves(JsonElement input, bool closed)
    {
        var result = new CurveArray();
        var items = input.EnumerateArray().ToArray();
        if (items.Length == 0) throw new ArgumentException("Curve input is empty.");
        if (items[0].ValueKind == JsonValueKind.Array)
        {
            XYZ[] points = items.Select(Util.Point).ToArray();
            if (closed && points.Length > 1 && points[0].IsAlmostEqualTo(points[^1])) points = points[..^1];
            if (points.Length < (closed ? 3 : 2)) throw new ArgumentException("Insufficient points.");
            int count = closed ? points.Length : points.Length - 1;
            for (int i = 0; i < count; i++) result.Append(Line.CreateBound(points[i], points[(i + 1) % points.Length]));
        }
        else foreach (var curve in items)
        {
            string kind = Util.Get(curve, "kind", "line");
            XYZ start = Util.Point(curve.GetProperty("start")), end = Util.Point(curve.GetProperty("end"));
            result.Append(kind switch
            {
                "line" => (Curve)Line.CreateBound(start, end),
                "arc" => Arc.Create(start, end, Util.Point(curve.GetProperty("point_on_arc"))),
                _ => throw new NotSupportedException("Supported curve kinds: line, arc.")
            });
        }
        return result;
    }

    private static Reference Ref(Document d, JsonElement value)
    {
        if (value.ValueKind == JsonValueKind.String) return Reference.ParseFromStableRepresentation(d, value.GetString()!);
        if (value.TryGetProperty("reference_plane", out var id))
            return (Util.Element(d, id) as ReferencePlane ?? throw new ArgumentException("Not a ReferencePlane.")).GetReference();
        throw new ArgumentException("Reference must be a stable reference string or {reference_plane: element identifier}.");
    }

    private static void RequireFamily(Document d)
    {
        if (!d.IsValidObject || !d.IsFamilyDocument) throw new ArgumentException("Target must be an open native family document.");
    }
    private static void Feet(JsonElement a)
    {
        if (Required(a, "units") != "feet") throw new NotSupportedException("Family geometry requires explicit units:'feet' in native family coordinates.");
    }
    private static string Required(JsonElement a, string key)
    {
        string value = Util.Get(a, key, "");
        if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException("Required argument: " + key);
        return value;
    }
    private static string ExistingPath(JsonElement a, string key, string extension)
    {
        string raw = Required(a, key);
        if (!Path.IsPathFullyQualified(raw)) throw new ArgumentException(key + " must be an absolute path.");
        string path = Path.GetFullPath(raw);
        if (!path.EndsWith(extension, StringComparison.OrdinalIgnoreCase)) throw new ArgumentException(key + " must end in " + extension);
        if (!File.Exists(path)) throw new FileNotFoundException("Source file does not exist.", path);
        return path;
    }
    private static double[] Xyz(XYZ p) => new[] { p.X, p.Y, p.Z };

    private sealed class RollBackErrors : IFailuresPreprocessor
    {
        public List<string> Messages { get; } = new();
        public FailureProcessingResult PreprocessFailures(FailuresAccessor failures)
        {
            var messages = failures.GetFailureMessages();
            Messages.AddRange(messages.Select(f => f.GetSeverity() + ": " + f.GetDescriptionText()));
            return messages.Any(f => f.GetSeverity() == FailureSeverity.Error || f.GetSeverity() == FailureSeverity.DocumentCorruption)
                ? FailureProcessingResult.ProceedWithRollBack : FailureProcessingResult.Continue;
        }
    }

    private sealed class LoadPolicy : IFamilyLoadOptions
    {
        public string Name { get; }
        public List<object> Decisions { get; } = new();
        public LoadPolicy(string name)
        {
            if (name is not ("reject" or "preserve_parameters" or "overwrite_parameters"))
                throw new ArgumentException("replacement_policy must be reject, preserve_parameters, or overwrite_parameters.");
            Name = name;
        }
        public bool OnFamilyFound(bool familyInUse, out bool overwriteParameterValues)
        {
            overwriteParameterValues = Name == "overwrite_parameters";
            Decisions.Add(new { kind = "family", family_in_use = familyInUse, accept = Name != "reject", overwrite_parameters = overwriteParameterValues });
            return Name != "reject";
        }
        public bool OnSharedFamilyFound(Family sharedFamily, bool familyInUse, out FamilySource source, out bool overwriteParameterValues)
        {
            source = Name == "reject" ? FamilySource.Project : FamilySource.Family;
            overwriteParameterValues = Name == "overwrite_parameters";
            Decisions.Add(new { kind = "shared_family", name = sharedFamily.Name, family_in_use = familyInUse, source = source.ToString(), accept = Name != "reject", overwrite_parameters = overwriteParameterValues });
            return Name != "reject";
        }
    }
}
