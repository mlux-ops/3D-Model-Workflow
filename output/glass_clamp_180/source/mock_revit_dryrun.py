# -*- coding: utf-8 -*-
"""Logic dry-run of build_glass_clamp.py against a MOCK Revit API (CPython 3).

Purpose: catch Python-level and modelling-logic defects in the builder, the verifier and the
gate arithmetic before the native run: typos, calls made outside a transaction, saves or
exports made inside one, planes created in a view that cannot see them, dimensions and
alignments Revit would refuse, profiles that cross a revolve axis, flex rows that cannot pass.

The mock solves the family the way the builder declares it: reference planes are positioned by
labelled dimensions (and EQ chains) from the pinned planes, profile edges follow the planes they
were aligned to, sketch planes bound to a reference plane follow it, and START/END offsets follow
their associated parameters. Solids are then built from that solved state, so every measured gate
runs on geometry the builder really declared. Cap X-position only follows Cap_Spacing when the
sketch plane was bound to the reference plane, exactly as the builder's fallback path documents.

It proves NOTHING about Revit itself: API signatures, overload binding, whether a bound sketch
plane or an EQ dimension is accepted, appearance behaviour, warnings and file validity are only
established by the native run. Writes only to a temporary directory OUTSIDE the repository.

    python mock_revit_dryrun.py            run 1: everything available; expects verifier exit 0
                                           run 2: SketchPlane.Create(Document, Reference) absent;
                                                  expects the cap-spacing flex to FAIL, exit 1
                                           then tampered reports, each expected to exit 1
"""
import copy
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import types
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
AXES = ('x', 'y', 'z')


class MockRevitError(Exception):
    pass


# ---------------------------------------------------------------- geometry
class XYZ(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.X, self.Y, self.Z = float(x), float(y), float(z)

    def Add(self, o):
        return XYZ(self.X + o.X, self.Y + o.Y, self.Z + o.Z)

    def Subtract(self, o):
        return XYZ(self.X - o.X, self.Y - o.Y, self.Z - o.Z)

    def Multiply(self, s):
        return XYZ(self.X * s, self.Y * s, self.Z * s)

    def DotProduct(self, o):
        return self.X * o.X + self.Y * o.Y + self.Z * o.Z

    def CrossProduct(self, o):
        return XYZ(self.Y * o.Z - self.Z * o.Y, self.Z * o.X - self.X * o.Z, self.X * o.Y - self.Y * o.X)

    def GetLength(self):
        return math.sqrt(self.DotProduct(self))

    def Normalize(self):
        n = self.GetLength()
        if n < 1e-12:
            raise MockRevitError('cannot normalise a zero vector')
        return XYZ(self.X / n, self.Y / n, self.Z / n)

    def comp(self, axis):
        return {'x': self.X, 'y': self.Y, 'z': self.Z}[axis]


XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ, XYZ.Zero = XYZ(1, 0, 0), XYZ(0, 1, 0), XYZ(0, 0, 1), XYZ(0, 0, 0)
SHORT_CURVE_FT = 0.00256


class Line(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
        self.Reference = None

    @staticmethod
    def CreateBound(p, q):
        if q.Subtract(p).GetLength() < SHORT_CURVE_FT:
            raise MockRevitError('curve shorter than ShortCurveTolerance')
        return Line(p, q)

    @property
    def Direction(self):
        return self.q.Subtract(self.p).Normalize()

    def Evaluate(self, t, normalized):
        return self.p.Add(self.q.Subtract(self.p).Multiply(t))

    def GetEndPoint(self, i):
        return self.p if i == 0 else self.q


class Plane(object):
    def __init__(self, normal, origin):
        self.Normal, self.Origin = normal, origin

    @staticmethod
    def CreateByNormalAndOrigin(normal, origin):
        return Plane(normal.Normalize(), origin)


class GenList(list):
    def Append(self, x):
        self.append(x)

    def Add(self, x):
        self.append(x)

    @property
    def Size(self):
        return len(self)


class CurveArray(GenList):
    pass


class CurveArrArray(GenList):
    pass


class ReferenceArray(GenList):
    pass


class Reference(object):
    def __init__(self, target):
        self.target = target


def axis_of(vec, tol=1e-6):
    hits = [a for a in AXES if abs(abs(vec.comp(a)) - 1.0) < tol]
    if len(hits) != 1:
        raise MockRevitError('mock supports axis-aligned vectors only')
    return hits[0]


# ---------------------------------------------------------------- elements
class ElementId(object):
    def __init__(self, v):
        self.Value = int(v)

    def __eq__(self, o):
        return isinstance(o, ElementId) and o.Value == self.Value

    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        return hash(self.Value)


ElementId.InvalidElementId = ElementId(-1)
_NEXT = [2000]


def new_id():
    _NEXT[0] += 1
    return ElementId(_NEXT[0])


class Element(object):
    def __init__(self, doc):
        self.Document = doc
        self.Id = new_id()
        self._name = None
        doc.elements[self.Id.Value] = self
        self.Pinned = False

    @property
    def Name(self):
        return self._name

    @Name.setter
    def Name(self, value):
        self.Document.require_tx('rename')
        self._name = value

    def GetType(self):
        return types.SimpleNamespace(Name=type(self).__name__)

    def get_Parameter(self, bip):
        return None


class NameDescriptor(object):
    @staticmethod
    def GetValue(element):
        if not isinstance(element, Element):
            raise TypeError('Element.Name.GetValue needs an Element, got %s' % type(element).__name__)
        return element._name

    @staticmethod
    def SetValue(element, name):
        element._name = name


class ElementNS(object):
    Name = NameDescriptor()


class Category(object):
    def __init__(self, name, parent=None):
        self.Name, self.Parent = name, parent
        self.Id = new_id()
        self.SubCategories = []


class Categories(list):
    def NewSubcategory(self, parent, name):
        if any(c.Name == name for c in parent.SubCategories):
            raise MockRevitError('Subcategory exists: ' + name)
        sub = Category(name, parent)
        parent.SubCategories.append(sub)
        return sub


class ElemParam(object):
    """Parameter of an element (forms, family, views)."""

    def __init__(self, owner, key, value=0, read_only=False):
        self.owner, self.key, self.IsReadOnly, self._value = owner, key, read_only, value
        self.Definition = types.SimpleNamespace(Name=key)

    def Set(self, value):
        self.owner.Document.require_tx('Parameter.Set')
        if self.IsReadOnly:
            raise MockRevitError('read-only parameter ' + str(self.key))
        self._value = value
        self.owner.param_values[self.key] = value
        return True

    def AsInteger(self):
        return int(self._value)

    def AsElementId(self):
        return self._value


class Color(object):
    def __init__(self, r, g, b):
        self.Red, self.Green, self.Blue = int(r), int(g), int(b)


class AssetProperty(object):
    def __init__(self, name, value, connected=0):
        self.Name, self.Value, self.NumberOfConnectedProperties = name, value, connected

    def RemoveConnectedAsset(self):
        self.NumberOfConnectedProperties = 0

    def SetValueAsColor(self, c):
        self.Value = (c.Red, c.Green, c.Blue)

    def GetValueAsColor(self):
        return Color(*self.Value)


class Asset(object):
    def __init__(self, name, props):
        self.Name, self._props = name, props

    def FindByName(self, name):
        return next((p for p in self._props if p.Name == name), None)

    def copy(self, name):
        return Asset(name, [AssetProperty(p.Name, p.Value, p.NumberOfConnectedProperties) for p in self._props])


def library_assets():
    return [Asset('Generic - mock library', [
        AssetProperty('BaseSchema', 'GenericSchema'), AssetProperty('generic_diffuse', (80, 80, 80), 1),
        AssetProperty('generic_glossiness', 0.5), AssetProperty('generic_reflectivity_at_0deg', 0.1),
        AssetProperty('generic_reflectivity_at_90deg', 0.5), AssetProperty('generic_self_illum_luminance', 0.0),
        AssetProperty('generic_is_metal', False)])]


class AppearanceAssetElement(Element):
    @staticmethod
    def Create(doc, name, asset):
        doc.require_tx('AppearanceAssetElement.Create')
        e = AppearanceAssetElement(doc)
        e._name, e.asset = name, asset.copy(name)
        return e

    def GetRenderingAsset(self):
        return self.asset


class Material(Element):
    @staticmethod
    def Create(doc, name):
        doc.require_tx('Material.Create')
        if any(isinstance(e, Material) and e._name == name for e in doc.elements.values()):
            raise MockRevitError('Material name exists: ' + name)
        m = Material(doc)
        m._name, m.Color, m.Transparency, m.MaterialClass = name, Color(127, 127, 127), 0, ''
        m.AppearanceAssetId = ElementId(-1)
        m.SurfaceForegroundPatternId = ElementId(77)
        m.SurfaceBackgroundPatternId = ElementId(77)
        return m.Id

    @property
    def Name(self):
        return self._name


class AppearanceAssetEditScope(object):
    def __init__(self, doc):
        self.doc = doc

    def Start(self, eid):
        self.doc.require_tx('AppearanceAssetEditScope.Start')
        return self.doc.GetElement(eid).asset

    def Commit(self, flag):
        pass

    def Dispose(self):
        pass


# ---------------------------------------------------------------- views
class View(Element):
    IsTemplate = False

    def __init__(self, doc, name, view_type, axis):
        Element.__init__(self, doc)
        self._name, self.ViewType, self.axis = name, view_type, axis
        self.param_values = {}
        self.DetailLevel = 'Fine'
        self.Parameters = [ElemParam(self, 'Sun Path', 1)]


class ViewPlan(View):
    pass


class ViewSection(View):
    pass


class ViewFamilyType(Element):
    pass


class View3D(View):
    @staticmethod
    def CreateIsometric(doc, type_id):
        doc.require_tx('CreateIsometric')
        v = View3D(doc, '{3D}', '3D', None)
        return v

    def SetOrientation(self, o):
        self.Document.require_tx('SetOrientation')
        if abs(o.up.DotProduct(o.forward)) > 1e-6:
            raise MockRevitError('view up and forward vectors must be perpendicular')

    def SetSectionBox(self, box):
        self.Document.require_tx('SetSectionBox')

    IsSectionBoxActive = False
    DisplayStyle = None


class ViewOrientation3D(object):
    def __init__(self, eye, up, forward):
        self.eye, self.up, self.forward = eye, up, forward


class BoundingBoxXYZ(object):
    Min = Max = None


class Level(Element):
    pass


# ---------------------------------------------------------------- reference planes, dimensions
class ReferencePlane(Element):
    def __init__(self, doc, axis, pos, name):
        Element.__init__(self, doc)
        self.axis, self.pos, self.init_pos, self._name = axis, pos, pos, name
        self.pinned_by_template = False

    @property
    def Name(self):
        return self._name

    @Name.setter
    def Name(self, value):
        self.Document.require_tx('rename plane')
        if any(isinstance(e, ReferencePlane) and e is not self and e._name == value
               for e in self.Document.elements.values()):
            raise MockRevitError('reference plane name exists: ' + value)
        self._name = value

    def GetReference(self):
        return Reference(self)

    def GetPlane(self):
        c = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        c[self.axis] = self.Document.solve()[0][self]          # the solved position, as Revit reports it
        return types.SimpleNamespace(Origin=XYZ(c['x'], c['y'], c['z']))

    @property
    def IsPinned(self):
        return self.pinned_by_template or self.Pinned


class Dimension(Element):
    def __init__(self, doc, view, refs):
        Element.__init__(self, doc)
        self.view, self.refs, self.label, self.eq = view, refs, None, False
        self.sign = 1 if refs[-1].init_pos >= refs[0].init_pos else -1

    @property
    def FamilyLabel(self):
        return self.label

    @FamilyLabel.setter
    def FamilyLabel(self, param):
        self.Document.require_tx('FamilyLabel')
        if param.spec != 'length':
            raise MockRevitError('only a length parameter can label a linear dimension')
        self.label = param

    @property
    def AreSegmentsEqual(self):
        return self.eq

    @AreSegmentsEqual.setter
    def AreSegmentsEqual(self, value):
        self.Document.require_tx('AreSegmentsEqual')
        if len(self.refs) < 3:
            raise MockRevitError('EQ needs a dimension with at least three references')
        if not self.Document.app.allow_eq:
            raise MockRevitError('mock: Dimension.AreSegmentsEqual is not settable')
        self.eq = bool(value)


class SketchPlane(Element):
    @staticmethod
    def Create(doc, target):
        doc.require_tx('SketchPlane.Create')
        if isinstance(target, Plane):
            sp = SketchPlane(doc)
            sp.axis, sp.pos, sp.bound = axis_of(target.Normal), target.Origin.comp(axis_of(target.Normal)), None
            return sp
        if isinstance(target, Reference):
            if not doc.app.allow_bound_sketch_plane:
                raise TypeError('mock: SketchPlane.Create(Document, Reference) overload not available')
            if not isinstance(target.target, ReferencePlane):
                raise MockRevitError('a plane reference is required')
            sp = SketchPlane(doc)
            sp.axis, sp.pos, sp.bound = target.target.axis, target.target.pos, target.target
            return sp
        raise TypeError('no SketchPlane.Create overload for %s' % type(target).__name__)


class EdgeRef(object):
    def __init__(self, form, key):
        self.form, self.key = form, key


# ---------------------------------------------------------------- forms and solids
class MockFace(object):
    def __init__(self, material_id):
        self.MaterialElementId = material_id


class MockEdge(object):
    def __init__(self, points):
        self._points = points

    def Tessellate(self):
        return list(self._points)


class MockSolid(object):
    def __init__(self, kind, spec, material_id, shift=(0.0, 0.0, 0.0)):
        self.kind, self.spec, self.shift = kind, spec, shift
        self.Faces = GenList(MockFace(material_id) for _ in range(6 if kind == 'box' else 3))
        sx, sy, sz = shift
        pts = []
        if kind == 'box':
            x0, x1, y0, y1, z0, z1 = spec
            c = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
            edges = [[XYZ(a[0] + sx, a[1] + sy, a[2] + sz), XYZ(b[0] + sx, b[1] + sy, b[2] + sz)]
                     for a in c for b in c if sum(1 for i in range(3) if a[i] != b[i]) == 1 and a < b]
            self.Volume = (x1 - x0) * (y1 - y0) * (z1 - z0)
            self.centroid = XYZ((x0 + x1) / 2 + sx, (y0 + y1) / 2 + sy, (z0 + z1) / 2 + sz)
        else:
            cx, cz, r, y0, y1 = spec
            edges = []
            for y in (y0, y1):
                ring = [XYZ(cx + r * math.cos(2 * math.pi * i / 72) + sx, y + sy, cz + r * math.sin(2 * math.pi * i / 72) + sz)
                        for i in range(72)]
                edges.append(ring + [ring[0]])
            edges.append([XYZ(cx + r + sx, y0 + sy, cz + sz), XYZ(cx + r + sx, y1 + sy, cz + sz)])
            self.Volume = math.pi * r * r * (y1 - y0)
            self.centroid = XYZ(cx + sx, (y0 + y1) / 2 + sy, cz + sz)
        self.Edges = GenList(MockEdge(e) for e in edges)

    def ComputeCentroid(self):
        return self.centroid


class Form(Element):
    """Extrusion or Revolution declared by the builder."""

    def __init__(self, doc, sketch, keys):
        Element.__init__(self, doc)
        self.sketch, self.keys = sketch, keys
        self.aligned = {}
        self.assoc = {}
        self.param_values = {}
        self.Subcategory = None
        self.vis = None

    def get_Parameter(self, bip):
        return ElemParam(self, bip)

    @property
    def Sketch(self):
        return types.SimpleNamespace(Profile=self.profile_loops)

    def SetVisibility(self, vis):
        self.Document.require_tx('SetVisibility')
        self.vis = copy.copy(vis)

    def GetVisibility(self):
        return self.vis

    def get_Geometry(self, options):
        return [self.build(self.Document.solve(), self.Document.family_material())]


class Extrusion(Form):
    def build(self, solved, material_id, shift=(0.0, 0.0, 0.0)):
        planes, values = solved
        v = dict(self.init)
        for key, plane in self.aligned.items():
            v[key] = planes[plane]
        start, end = self.start_init, self.end_init
        for bip, name in self.assoc_lengths().items():
            if bip == 'EXTRUSION_START_PARAM':
                start = values[name]
            if bip == 'EXTRUSION_END_PARAM':
                end = values[name]
        lo, hi = min(start, end), max(start, end)
        return MockSolid('box', (v['xmin'], v['xmax'], lo, hi, v['zmin'], v['zmax']), material_id, shift)

    def assoc_lengths(self):
        return dict((bip, p.Definition.Name) for bip, p in self.assoc.items() if p.spec == 'length')


class Revolution(Form):
    def build(self, solved, material_id, shift=(0.0, 0.0, 0.0)):
        planes, values = solved
        cx = planes[self.sketch.bound] if self.sketch.bound is not None else self.sketch.pos
        v = dict(self.init)
        for key, plane in self.aligned.items():
            v[key] = planes[plane]
        return MockSolid('cyl', (cx, 0.0, v['r'], v['y0'], v['y1']), material_id, shift)

    def assoc_lengths(self):
        return {}


# ---------------------------------------------------------------- family manager
class FamilyParameter(object):
    def __init__(self, name, spec, is_instance=False, builtin=False):
        self.Definition = types.SimpleNamespace(Name=name, GetDataType=lambda: types.SimpleNamespace(TypeId='mock:' + spec))
        self.spec, self.IsInstance, self.builtin = spec, is_instance, builtin
        self.Formula = None


class FamilyType(object):
    def __init__(self, fm, name):
        self.fm, self.Name, self.values = fm, name, {}

    def AsDouble(self, p):
        return self.fm.value_of(self, p.Definition.Name)

    def AsElementId(self, p):
        return self.values.get(p.Definition.Name)

    def AsString(self, p):
        return self.values.get(p.Definition.Name)


class FamilyManager(object):
    def __init__(self, doc):
        self.doc = doc
        self.Parameters = GenList()
        self.Types = GenList()
        self._current = None
        self._builtins = {}

    @property
    def CurrentType(self):
        return self._current

    @CurrentType.setter
    def CurrentType(self, t):
        self.doc.require_tx('CurrentType')
        self._current = t

    def NewType(self, name):
        self.doc.require_tx('NewType')
        t = FamilyType(self, name)
        if self._current is not None:
            t.values = dict(self._current.values)
        self.Types.append(t)
        self._current = t
        return t

    def DeleteCurrentType(self):
        self.doc.require_tx('DeleteCurrentType')
        if len(self.Types) < 2:
            raise MockRevitError('cannot delete the only type')
        self.Types.remove(self._current)
        self._current = self.Types[0]

    def AddParameter(self, name, group, spec, is_instance):
        self.doc.require_tx('AddParameter')
        if any(p.Definition.Name == name for p in self.Parameters) or name in ('Manufacturer', 'Model', 'Description'):
            raise MockRevitError('Parameter exists: ' + name)
        p = FamilyParameter(name, spec, is_instance)
        self.Parameters.append(p)
        return p

    def Set(self, p, value):
        self.doc.require_tx('FamilyManager.Set')
        if self._current is None:
            raise MockRevitError('FamilyManager.Set without a current type')
        if p.Formula:
            raise MockRevitError('parameter %s is driven by a formula' % p.Definition.Name)
        if p.spec == 'material' and not isinstance(value, ElementId):
            raise MockRevitError('material parameter needs an ElementId')
        if p.spec == 'length' and not isinstance(value, float):
            raise MockRevitError('length parameter needs a float (feet)')
        self._current.values[p.Definition.Name] = value

    def SetFormula(self, p, formula):
        self.doc.require_tx('SetFormula')
        self.evaluate(formula, dict((q.Definition.Name, 1.0) for q in self.Parameters))    # parse check
        p.Formula = formula

    def get_Parameter(self, bip):
        if bip not in self._builtins:
            self._builtins[bip] = FamilyParameter(bip, 'text', builtin=True)
            self._builtins[bip].Definition.Name = bip
        return self._builtins[bip]

    def AssociateElementParameterToFamilyParameter(self, elem_param, fam_param):
        self.doc.require_tx('Associate')
        elem_param.owner.assoc[elem_param.key] = fam_param

    def GetAssociatedFamilyParameter(self, elem_param):
        return elem_param.owner.assoc.get(elem_param.key)

    @staticmethod
    def evaluate(formula, values):
        expr = formula.replace('"', ' in')
        expr = re.sub(r'(\d+(?:\.\d+)?)\s*in\b', r'(\1/12.0)', expr)

        def name(m):
            if m.group(0) not in values:
                raise MockRevitError('formula refers to unknown parameter ' + m.group(0))
            return "V['%s']" % m.group(0)
        expr = re.sub(r'[A-Za-z_][A-Za-z_0-9]*', name, expr)
        return eval(expr, {'__builtins__': {}}, {'V': values})

    def values_of(self, t):
        """All length values of type t in feet, formulas resolved (parameters in creation order)."""
        out = dict((k, v) for k, v in t.values.items() if isinstance(v, float))
        for _ in range(4):
            for p in self.Parameters:
                if p.Formula:
                    try:
                        out[p.Definition.Name] = self.evaluate(p.Formula, out)
                    except (KeyError, MockRevitError):
                        pass
        return out

    def value_of(self, t, name):
        return self.values_of(t)[name]


# ---------------------------------------------------------------- family item factory
class FamilyItemFactory(object):
    def __init__(self, doc):
        self.doc = doc

    def NewReferencePlane(self, bubble, free, cut, view):
        self.doc.require_tx('NewReferencePlane')
        normal = free.Subtract(bubble).CrossProduct(cut)
        axis = axis_of(normal.Normalize())
        if axis == view.axis:
            raise MockRevitError('plane normal %s is along the viewing axis of view %s' % (axis, view.Name))
        plane = ReferencePlane(self.doc, axis, bubble.comp(axis), None)
        return plane

    def NewLinearDimension(self, view, line, refs):
        self.doc.require_tx('NewLinearDimension')
        planes = [r.target for r in refs]
        axes = set(p.axis for p in planes)
        if len(axes) != 1 or any(not isinstance(p, ReferencePlane) for p in planes):
            raise MockRevitError('dimension references must be parallel reference planes')
        axis = axes.pop()
        if axis == view.axis:
            raise MockRevitError('planes are not visible in view ' + view.Name)
        if abs(line.Direction.comp(axis)) < 0.999:
            raise MockRevitError('dimension line is not parallel to the measured direction')
        return Dimension(self.doc, view, planes)

    def NewAlignment(self, view, ref_a, ref_b):
        self.doc.require_tx('NewAlignment')
        plane, edge = ref_a.target, ref_b.target
        if not isinstance(plane, ReferencePlane) or not isinstance(edge, EdgeRef):
            raise MockRevitError('alignment needs a plane reference and a geometry reference')
        if plane.axis == view.axis:
            raise MockRevitError('plane not visible in view ' + view.Name)
        if edge.form.sketch.axis != view.axis:
            raise MockRevitError('sketch edge is not seen true-length in view %s' % view.Name)
        if edge.form.edge_axis[edge.key] != plane.axis:
            raise MockRevitError('edge %s cannot be aligned to a plane normal to %s' % (edge.key, plane.axis))
        edge.form.aligned[edge.key] = plane
        return object()

    def NewExtrusion(self, is_solid, profile, sketch, end):
        self.doc.require_tx('NewExtrusion')
        if len(profile) != 1 or len(profile[0]) != 4:
            raise MockRevitError('mock expects one four-line loop')
        pts = [c.p for c in profile[0]]
        if sketch.axis != 'y' or any(abs(p.Y - sketch.pos) > 1e-9 for p in pts):
            raise MockRevitError('extrusion profile is not in the sketch plane')
        for i in range(4):
            if profile[0][i].q.Subtract(profile[0][(i + 1) % 4].p).GetLength() > 1e-9:
                raise MockRevitError('profile loop is not contiguous')
        form = Extrusion(self.doc, sketch, None)
        form.init = {'xmin': min(p.X for p in pts), 'xmax': max(p.X for p in pts),
                     'zmin': min(p.Z for p in pts), 'zmax': max(p.Z for p in pts)}
        form.start_init, form.end_init = 0.0, end
        form.edge_axis = {'xmin': 'x', 'xmax': 'x', 'zmin': 'z', 'zmax': 'z'}
        loops = CurveArrArray()
        loop = CurveArray()
        for c in profile[0]:
            line = Line(c.p, c.q)
            d, mid = line.Direction, line.Evaluate(0.5, True)
            key = ('zmax' if mid.Z > 0 else 'zmin') if abs(d.X) > 0.9 else ('xmax' if mid.X > 0 else 'xmin')
            line.Reference = Reference(EdgeRef(form, key))
            loop.append(line)
        loops.append(loop)
        form.profile_loops = loops
        return form

    def NewRevolution(self, is_solid, profile, sketch, axis, a0, a1):
        self.doc.require_tx('NewRevolution')
        if not (0.0 <= a0 < a1 <= 2 * math.pi + 1e-9):
            raise MockRevitError('bad revolve angles')
        pts = [c.p for c in profile[0]]
        if sketch.axis != 'x' or any(abs(p.X - sketch.pos) > 1e-9 for p in pts):
            raise MockRevitError('revolve profile is not in the sketch plane')
        if abs(axis.p.X - sketch.pos) > 1e-9 or abs(axis.q.X - sketch.pos) > 1e-9 or abs(axis.Direction.Y) < 0.999:
            raise MockRevitError('revolve axis must lie in the sketch plane along Y in this mock')
        if any(p.Z < -1e-9 for p in pts) or max(p.Z for p in pts) < 1e-6:
            raise MockRevitError('profile crosses or misses the revolve axis')
        area = sum(pts[i].Y * pts[(i + 1) % 4].Z - pts[(i + 1) % 4].Y * pts[i].Z for i in range(4)) / 2.0
        if area <= 0:
            raise MockRevitError('revolve profile must be counter-clockwise (untested in Revit)')
        form = Revolution(self.doc, sketch, None)
        y_mid = sum(p.Y for p in pts) / 4.0
        r = max(p.Z for p in pts)
        form.init = {'y0': min(p.Y for p in pts), 'y1': max(p.Y for p in pts), 'r': r}
        form.edge_axis = {'y0': 'y', 'y1': 'y', 'r': 'z'}
        loop = CurveArray()
        for c in profile[0]:
            line = Line(c.p, c.q)
            d, mid = line.Direction, line.Evaluate(0.5, True)
            if abs(d.Y) > 0.9:
                key = 'r' if mid.Z > r / 2 else 'axis'
            else:
                key = 'y1' if mid.Y > y_mid else 'y0'
            line.Reference = Reference(EdgeRef(form, key))
            form.edge_axis.setdefault('axis', 'z')
            loop.append(line)
        loops = CurveArrArray()
        loops.append(loop)
        form.profile_loops = loops
        return form


# ---------------------------------------------------------------- documents
class Warning_(object):
    def __init__(self, text):
        self.text = text

    def GetDescriptionText(self):
        return self.text


class FamilySymbolParam(object):
    def __init__(self, symbol, name):
        self.symbol, self.Definition = symbol, types.SimpleNamespace(Name=name)
        self.IsReadOnly = False

    def AsElementId(self):
        return self.symbol.material_id

    def Set(self, value):
        self.symbol.Document.require_tx('symbol parameter')
        self.symbol.material_id = value


class FamilySymbol(Element):
    def Activate(self):
        pass

    def LookupParameter(self, name):
        return FamilySymbolParam(self, name) if name == 'Clamp_Material' else None

    def get_Parameter(self, bip):
        if bip == 'SYMBOL_NAME_PARAM':
            return types.SimpleNamespace(AsString=lambda: self._name)
        return None


class Family(Element):
    def GetFamilySymbolIds(self):
        return GenList(s.Id for s in self.symbols)


class FamilyInstance(Element):
    def __init__(self, doc, symbol, origin):
        Element.__init__(self, doc)
        self.symbol, self.origin = symbol, origin

    def get_Geometry(self, options):
        view = getattr(options, 'View', None)
        detail = view.DetailLevel if view is not None else getattr(options, 'DetailLevel', 'Fine')
        fam_doc = self.symbol.family_doc
        solved = fam_doc.solve(self.symbol.values)
        solids = []
        for form in fam_doc.forms():
            vis = form.vis
            if vis is not None and not getattr(vis, 'IsShownIn' + detail):
                continue
            shift = (self.origin.X, self.origin.Y, self.origin.Z)
            solids.append(form.build(solved, self.symbol.material_id, shift))
        return [GeometryInstance(solids)]


class GeometryInstance(object):
    def __init__(self, solids):
        self._solids = solids

    def GetInstanceGeometry(self):
        return self._solids


class Creator(object):
    def __init__(self, doc):
        self.doc = doc

    def NewFamilyInstance(self, point, symbol, level, structural):
        self.doc.require_tx('NewFamilyInstance')
        return FamilyInstance(self.doc, symbol, point)


class Document(object):
    def __init__(self, app, family):
        self.app = app
        self.IsFamilyDocument = family
        self.elements = {}
        self.tx_open = False
        self.group_open = False
        self.closed = False
        self.injected_warnings = []
        gm = Category('Generic Models')
        self.Settings = types.SimpleNamespace(Categories=Categories([gm, Category('Lighting Fixtures')]))
        ViewFamilyType(self).ViewFamily = 'ThreeDimensional'
        if family:
            self.FamilyManager = FamilyManager(self)
            self.FamilyCreate = FamilyItemFactory(self)
            self.category = gm
            self.family_params = {}
            self.OwnerFamily = types.SimpleNamespace(
                get_Parameter=self._family_param, FamilyCategory=gm)
            self.OwnerFamily = FamilyProxy(self)
            for name, view_type, axis in [('Ref. Level', 'FloorPlan', 'z')]:
                ViewPlan(self, name, view_type, axis)
            for name, axis in [('Front', 'y'), ('Back', 'y'), ('Left', 'x'), ('Right', 'x')]:
                ViewSection(self, name, 'Elevation', axis)
            for axis, name in (('x', 'Center (Left/Right)'), ('y', 'Center (Front/Back)')):
                p = ReferencePlane(self, axis, 0.0, name)
                p.pinned_by_template = True
            self.material_default = None
        else:
            upper = Level(self)              # created first, so 'first level' is NOT the lowest one
            upper.Elevation = 10.0
            lower = Level(self)
            lower.Elevation = 0.0
            self.Create = Creator(self)

    def _family_param(self, bip):
        return self.family_params.get(bip)

    def require_tx(self, what):
        if self.closed:
            raise MockRevitError(what + ' on a closed document')
        if not self.tx_open:
            raise MockRevitError(what + ' outside a transaction')

    def GetElement(self, eid):
        return self.elements.get(eid.Value)

    def Regenerate(self):
        self.require_tx('Regenerate')
        if self.IsFamilyDocument:
            self.solve()

    def GetWarnings(self):
        return [Warning_(t) for t in self.injected_warnings]

    def forms(self):
        return [e for e in self.elements.values() if isinstance(e, (Extrusion, Revolution))]

    def family_material(self):
        p = self.FamilyManager.get_Parameter  # noqa: F841
        cur = self.FamilyManager.CurrentType
        return cur.values.get('Clamp_Material') if cur is not None else ElementId(-1)

    def solve(self, values_override=None):
        """(plane positions, length values in feet) from the pinned planes and the labelled dimensions."""
        fm = self.FamilyManager
        values = values_override if values_override is not None else fm.values_of(fm.CurrentType)
        if values_override is not None and not isinstance(values, dict):
            raise MockRevitError('bad override')
        planes_list = [e for e in self.elements.values() if isinstance(e, ReferencePlane)]
        dims = [e for e in self.elements.values() if isinstance(e, Dimension)]
        pos = dict((p, 0.0) for p in planes_list if p.IsPinned)
        changed = True
        while changed:
            changed = False
            for d in dims:
                if d.label is not None and len(d.refs) == 2:
                    v = values[d.label.Definition.Name]
                    a, b = d.refs
                    if a in pos and b not in pos:
                        pos[b], changed = pos[a] + d.sign * v, True
                    elif b in pos and a not in pos:
                        pos[a], changed = pos[b] - d.sign * v, True
                elif d.eq and len(d.refs) == 3:
                    a, c, b = d.refs
                    overall = next((o for o in dims if o.label is not None and len(o.refs) == 2
                                    and set(o.refs) == set([a, b])), None)
                    if overall is not None and c in pos:
                        v = values[overall.label.Definition.Name]
                        for p in (a, b):
                            if p not in pos:
                                s = 1 if p.init_pos >= c.init_pos else -1
                                pos[p], changed = pos[c] + s * v / 2.0, True
        for p in planes_list:
            if p not in pos:
                pos[p] = p.pos            # unconstrained: stays where it was created
        return pos, values


class FamilyProxy(object):
    def __init__(self, doc):
        self.doc = doc

    @property
    def FamilyCategory(self):
        return self.doc.category

    @FamilyCategory.setter
    def FamilyCategory(self, value):
        self.doc.require_tx('FamilyCategory')
        self.doc.category = value

    def get_Parameter(self, bip):
        return self.doc.family_params.setdefault(bip, ElemParam(types.SimpleNamespace(
            Document=self.doc, param_values={}), bip, 0, read_only=bip == 'FAMILY_WORK_PLANE_BASED_RO'))


def _doc_save(self, path, options):
    if self.tx_open:
        raise MockRevitError('SaveAs with an open transaction')
    self.app.saved_options = options
    with open(path, 'wb') as fh:
        fh.write(b'MOCK RFA - not a Revit file\n' + b'\0' * 310000)
    self.app.saved[os.path.normpath(path)] = self


def _doc_export(self, options):
    if self.tx_open:
        raise MockRevitError('ExportImage with an open transaction')
    for vid in options.views:
        write_png(options.FilePath + ' - 3D View - ' + self.GetElement(vid)._name + '.png')


def _doc_load(self, target):
    if target.tx_open:
        raise MockRevitError('LoadFamily into a document with an open transaction')
    fam = Family(target)
    fam.symbols = []
    material = self.GetElement(next(t for t in self.FamilyManager.Types).values['Clamp_Material'])
    existing = [e for e in target.elements.values() if isinstance(e, Material) and e._name == material._name]
    if existing:
        project_material = existing[0]
    else:
        project_material = Material(target)
        project_material._name = material._name
    for t in self.FamilyManager.Types:
        sym = FamilySymbol(target)
        sym._name = t.Name
        sym.family_doc, sym.values, sym.material_id = self, self.FamilyManager.values_of(t), project_material.Id
        fam.symbols.append(sym)
    return fam


def _doc_close(self, save):
    self.closed = True


def _doc_unused(self, grouped):
    return GenList(e.Id for e in self.elements.values() if isinstance(e, Material) and e._name == 'Unused template material')


def _doc_delete(self, eid):
    self.require_tx('Delete')
    if eid.Value not in self.elements:
        raise MockRevitError('element already deleted')
    del self.elements[eid.Value]
    return GenList([eid])


Document.SaveAs, Document.ExportImage, Document.LoadFamily = _doc_save, _doc_export, _doc_load
Document.Close, Document.GetUnusedElements, Document.Delete = _doc_close, _doc_unused, _doc_delete


class Transaction(object):
    def __init__(self, doc, name):
        self.doc = doc

    def Start(self):
        if self.doc.tx_open:
            raise MockRevitError('nested transaction')
        self.doc.tx_open = True

    def Commit(self):
        if not self.doc.tx_open:
            raise MockRevitError('commit without start')
        self.doc.tx_open = False
        return 'Committed'

    def RollBack(self):
        self.doc.tx_open = False
        return 'RolledBack'


class TransactionGroup(object):
    def __init__(self, doc, name):
        self.doc = doc

    def Start(self):
        if self.doc.tx_open:
            raise MockRevitError('group started inside a transaction')
        fm = self.doc.FamilyManager
        self.snapshot = ([(t, dict(t.values)) for t in fm.Types], fm.CurrentType)

    def RollBack(self):
        if self.doc.tx_open:
            raise MockRevitError('group rolled back with an open transaction')
        fm = self.doc.FamilyManager
        for t, values in self.snapshot[0]:
            t.values = values
        fm._current = self.snapshot[1]


class FilteredElementCollector(object):
    def __init__(self, doc):
        self.doc = doc

    def OfClass(self, cls):
        return [e for e in list(self.doc.elements.values()) if isinstance(e, cls)]


class Application(object):
    VersionNumber = '2025'
    ShortCurveTolerance = SHORT_CURVE_FT

    def __init__(self, allow_bound_sketch_plane=True, allow_eq=True):
        self.saved = {}
        self.allow_bound_sketch_plane = allow_bound_sketch_plane
        self.allow_eq = allow_eq

    def NewFamilyDocument(self, template):
        return Document(self, True)

    def NewProjectDocument(self, units):
        return Document(self, False)

    def OpenDocumentFile(self, path):
        doc = self.saved[os.path.normpath(path)]
        doc.closed = False
        return doc

    def GetAssets(self, kind):
        return library_assets()


class ImageExportOptions(object):
    def SetViewsAndSheets(self, ids):
        self.views = list(ids)


def write_png(path):
    raw = b'\x00\xff\xff\xff'
    body = b''.join(struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
                    for t, d in [(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)),
                                 (b'IDAT', zlib.compress(raw)), (b'IEND', b'')])
    with open(path, 'wb') as fh:
        fh.write(b'\x89PNG\r\n\x1a\n' + body)


class Options(object):
    def __init__(self):
        self.DetailLevel, self.View = 'Fine', None


class FamilyElementVisibility(object):
    def __init__(self, vis_type):
        for n in ('IsShownInFrontBack', 'IsShownInLeftRight', 'IsShownInPlanRCPCut', 'IsShownInTopBottom',
                  'IsShownInCoarse', 'IsShownInMedium', 'IsShownInFine'):
            setattr(self, n, False)


class GenericList(object):
    def __getitem__(self, t):
        return lambda *a: GenList()


def make_db():
    DB = types.ModuleType('Autodesk.Revit.DB')
    ns = types.SimpleNamespace
    for cls in (XYZ, Line, Plane, CurveArray, CurveArrArray, ReferenceArray, ElementId, Color, Material,
                AppearanceAssetElement, FilteredElementCollector, Transaction, TransactionGroup, ViewPlan,
                ViewSection, ViewFamilyType, View3D, ViewOrientation3D, BoundingBoxXYZ, Level, ReferencePlane,
                Dimension, SketchPlane, Extrusion, Revolution, FamilyInstance, ImageExportOptions, Options,
                FamilyElementVisibility, MockSolid, GeometryInstance):
        setattr(DB, cls.__name__, cls)
    DB.Solid = MockSolid
    DB.View = View
    DB.Element = ElementNS
    DB.ImportInstance = type('ImportInstance', (Element,), {})
    DB.Document = Document
    DB.SaveAsOptions = lambda: types.SimpleNamespace()
    DB.FamilyElementVisibilityType = ns(Model='Model')
    DB.Visual = ns(AssetType=ns(Appearance='appearance'), AppearanceAssetEditScope=AppearanceAssetEditScope)
    DB.ViewType = ns(FloorPlan='FloorPlan', Elevation='Elevation')
    DB.ViewFamily = ns(ThreeDimensional='ThreeDimensional')
    DB.ViewDetailLevel = ns(Coarse='Coarse', Medium='Medium', Fine='Fine')
    DB.DisplayStyle = ns(ShadingWithEdges='ShadingWithEdges')
    DB.Structure = ns(StructuralType=ns(NonStructural='NonStructural'))
    DB.ZoomFitType = ns(FitToPage='FitToPage')
    DB.FitDirectionType = ns(Horizontal='Horizontal')
    DB.ImageFileType = ns(PNG='PNG')
    DB.ImageResolution = ns(DPI_150='DPI_150')
    DB.ExportRange = ns(SetOfViews='SetOfViews')
    DB.UnitSystem = ns(Imperial='Imperial')
    DB.GroupTypeId = ns(Geometry='geometry', Materials='materials')
    DB.SpecTypeId = ns(Length='length', Reference=ns(Material='material'))
    DB.BuiltInCategory = ns(OST_GenericModel='OST_GenericModel')
    DB.Category = ns(GetCategory=lambda doc, bic: doc.Settings.Categories[0])
    names = ['SYMBOL_NAME_PARAM', 'FAMILY_ALWAYS_VERTICAL', 'FAMILY_WORK_PLANE_BASED', 'ALL_MODEL_MANUFACTURER',
             'ALL_MODEL_MODEL', 'ALL_MODEL_DESCRIPTION', 'ALL_MODEL_TYPE_COMMENTS', 'EXTRUSION_START_PARAM',
             'EXTRUSION_END_PARAM', 'MATERIAL_ID_PARAM', 'VIEW_NAME']
    DB.BuiltInParameter = ns(**dict((n, n) for n in names))
    return DB


# ---------------------------------------------------------------- harness
def run_verifier(root):
    env = dict(os.environ, GLASS_CLAMP_RUN_DIR=os.path.join(root, 'output', 'glass_clamp_180'))
    p = subprocess.run([sys.executable, os.path.join(root, 'output', 'glass_clamp_180', 'source', 'verify_glass_clamp.py')],
                       capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def run_builder(tmp, allow_bound, allow_eq=True, via_button=False):
    DB = make_db()
    clr = types.SimpleNamespace(AddReference=lambda n: None,
                                GetClrType=lambda cls: (_ for _ in ()).throw(RuntimeError('mock: no reflection')))
    generic = types.ModuleType('System.Collections.Generic')
    generic.List = GenericList()
    generic.HashSet = GenericList()
    mods = {'clr': clr, 'Autodesk': types.ModuleType('Autodesk'), 'Autodesk.Revit': types.ModuleType('Autodesk.Revit'),
            'Autodesk.Revit.DB': DB, 'System': types.ModuleType('System'),
            'System.Collections': types.ModuleType('System.Collections'), 'System.Collections.Generic': generic}
    mods['Autodesk.Revit'].DB = DB
    mods['Autodesk'].Revit = mods['Autodesk.Revit']
    saved = dict((k, sys.modules.get(k)) for k in mods)
    sys.modules.update(mods)
    real_isfile = os.path.isfile
    os.path.isfile = lambda p: True if str(p).startswith('C:\\ProgramData') else real_isfile(p)
    sys.dont_write_bytecode = True
    builder = os.path.join(tmp, 'output', 'glass_clamp_180', 'source', 'build_glass_clamp.py')
    if via_button:            # exercise the in-Revit pushbutton entry point instead of the builder
        builder = os.path.join(tmp, 'output', 'glass_clamp_180', 'pyrevit', 'GlassClamp.extension', 'GlassClamp.tab',
                               'Build.panel', 'BuildGlassClamp.pushbutton', 'script.py')
    g = {'__file__': builder, '__name__': '__main__',
         '__revit__': types.SimpleNamespace(Application=Application(allow_bound, allow_eq))}
    error = None
    try:
        exec(compile(open(builder, encoding='utf-8').read(), builder, 'exec'), g)
    except Exception as exc:
        error = exc
    finally:
        os.path.isfile = real_isfile
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        sys.modules.pop('clamp_geometry', None)
    return error


def fresh_tree():
    tmp = tempfile.mkdtemp(prefix='clamp-mock-')
    if os.path.normpath(tmp).startswith(REPO + os.sep):
        raise SystemExit('refusing to write inside the repository')
    src = os.path.join(tmp, 'output', 'glass_clamp_180', 'source')
    os.makedirs(src)
    open(os.path.join(tmp, 'AGENTS.md'), 'w').write('mock root\n')
    for name in ('build_glass_clamp.py', 'clamp_geometry.py', 'verify_glass_clamp.py'):
        shutil.copy(os.path.join(HERE, name), os.path.join(src, name))
    shutil.copytree(os.path.join(HERE, '..', 'pyrevit'), os.path.join(tmp, 'output', 'glass_clamp_180', 'pyrevit'))
    return tmp


def report_of(tmp):
    path = os.path.join(tmp, 'output', 'glass_clamp_180', 'validation.json')
    return (json.load(open(path)), path) if os.path.isfile(path) else ({}, path)


def main():
    ok = True
    # ---- run 1: everything available
    tmp = fresh_tree()
    err = run_builder(tmp, True)
    rep, path = report_of(tmp)
    print('run 1 (all APIs present): stage=%s technical_pass=%s builder exception=%r' % (
        rep.get('stage'), rep.get('technical_pass'), err))
    print('  failed gates: %s | soft-failed: %s' % (rep.get('failed_gates'), rep.get('soft_failed_gates')))
    if rep.get('error'):
        print(rep['error'])
    code, out = run_verifier(tmp)
    print('  verifier -> exit %d' % code)
    print('\n'.join('    ' + line for line in out.strip().splitlines()[:45]))
    ok = ok and err is None and rep.get('technical_pass') is True and code == 0

    # ---- tampered reports and files: the verifier must reject every one
    base = json.dumps(rep)

    def tamper(label, mutate, files=None):
        bad = json.loads(base)
        mutate(bad)
        json.dump(bad, open(path, 'w'))
        code_bad, out_bad = run_verifier(tmp)
        print('  tamper [%s] -> exit %d' % (label, code_bad))
        return code_bad == 1

    def flex_row(r, bucket, name, value):
        return next(x for x in r['flex'][bucket] if x['parameter'] == name and x['value_in'] == value)

    tests = [
        ('plate 0.02 in off after Glass_Thickness flex',
         lambda r: flex_row(r, 'required', 'Glass_Thickness', 0.375)['solids']['plate_front']['bounds_in']['y'].__setitem__(1, 9.0)),
        ('caps not following Clamp_Width',
         lambda r: flex_row(r, 'required', 'Clamp_Width', 6.0)['solids']['cap_front_right']['centre_xz_in'].__setitem__(0, 1.5)),
        ('project warning', lambda r: r['project'].__setitem__('warnings', ['mock warning'])),
        ('material swap misses a face',
         lambda r: r['project']['material_swap'].__setitem__('swapped_face_material_ids', ['1', '2'])),
        ('builder claims visual pass', lambda r: r.__setitem__('visual_verdict', 'ACCEPTED')),
        ('gate flag flipped', lambda r: r['gates']['G10_default_geometry_matches_analytic_model'].__setitem__('pass', False)),
    ]
    for label, mutate in tests:
        ok = tamper(label, mutate) and ok
    json.dump(json.loads(base), open(path, 'w'), indent=2)
    rfa = rep.get('rfa_path')
    if rfa and os.path.isfile(rfa):
        with open(rfa, 'ab') as fh:
            fh.write(b'\0' * 300000)
        code_big, _ = run_verifier(tmp)
        print('  tamper [RFA grown past 500 KB] -> exit %d' % code_big)
        ok = ok and code_big == 1
        os.remove(rfa)
        code_gone, _ = run_verifier(tmp)
        print('  tamper [RFA deleted] -> exit %d' % code_gone)
        ok = ok and code_gone == 1

    # ---- run 2: no bound sketch plane -> the cap-spacing flex must fail, honestly
    tmp2 = fresh_tree()
    err2 = run_builder(tmp2, False)
    rep2, _ = report_of(tmp2)
    code2, out2 = run_verifier(tmp2)
    fails = [g for g in (rep2.get('failed_gates') or [])]
    print('run 2 (SketchPlane.Create(Document, Reference) absent): stage=%s failed=%s verifier exit %d' % (
        rep2.get('stage'), fails, code2))
    ok = ok and err2 is None and rep2.get('technical_pass') is False and code2 == 1 and any(
        g.startswith('G16') for g in fails) and not any(g.startswith('G15') for g in fails)
    print('  sketch plane modes: %s' % (rep2.get('family', {}).get('sketch_plane_modes'),))

    # ---- run 3: EQ dimensions refused -> the build still completes and the plane gates fail
    tmp3 = fresh_tree()
    err3 = run_builder(tmp3, True, allow_eq=False)
    rep3, _ = report_of(tmp3)
    code3, _out3 = run_verifier(tmp3)
    fails3 = rep3.get('failed_gates') or []
    print('run 3 (Dimension.AreSegmentsEqual refused): stage=%s failed=%s verifier exit %d' % (
        rep3.get('stage'), fails3, code3))
    ok = ok and err3 is None and rep3.get('stage') == 'complete' and rep3.get('technical_pass') is False and code3 == 1

    # ---- run 4: the in-Revit pushbutton resolves the builder from its own location
    tmp4 = fresh_tree()
    err4 = run_builder(tmp4, True, via_button=True)
    rep4, _ = report_of(tmp4)
    code4, _out4 = run_verifier(tmp4)
    inside = os.path.normpath(rep4.get('rfa_path', '')).startswith(os.path.join(tmp4, 'output', 'glass_clamp_180'))
    print('run 4 (via pushbutton): stage=%s technical_pass=%s verifier exit %d, RFA inside that checkout: %s' % (
        rep4.get('stage'), rep4.get('technical_pass'), code4, inside))
    ok = ok and err4 is None and rep4.get('technical_pass') is True and code4 == 0 and inside
    print('MOCK DRY-RUN %s' % ('PASS' if ok else 'FAIL'))
    print('mock run dirs: %s | %s | %s | %s' % (tmp, tmp2, tmp3, tmp4))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
