"""Logic dry-run of build_cassia.py against a MOCK Revit API (CPython 3 + numpy).

Purpose: catch Python-level and geometric-mapping defects in the builder before the
native run - typos, wrong frame/profile mapping, modifications outside a transaction,
exports or saves inside one, gate logic that cannot pass - without Revit.

The mock revolves the builder's actual CurveLoops about the actual Frame, meshes them,
and answers Solid.IntersectWithCurve by ray/mesh intersection, so every measured gate
runs on geometry the builder really constructed. It enforces a few Revit rules the
builder depends on: curve loops must be contiguous and closed, revolve profiles must
lie in the frame's XZ half-plane (x >= 0), curves must exceed ShortCurveTolerance,
view up/forward must be perpendicular, and modifications need an open transaction
while SaveAs/ExportImage/LoadFamily need none.

It proves NOTHING about Revit itself: API signatures, overload binding, appearance
behaviour, warnings and file validity are only established by the native run.

Writes only to a temporary directory OUTSIDE the repository, then runs verify_cassia.py
there (expects exit 0) and against two tampered reports (expects exit 1).

    python mock_revit_dryrun.py
"""
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import types
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
SHORT_CURVE_FT = 0.00256
SEGMENTS_AROUND = 96
ARC_SAMPLES_PER_RAD = 24


class MockRevitError(Exception):
    pass


# --------------------------------------------------------------- geometry
class XYZ(object):
    __slots__ = ('X', 'Y', 'Z')

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.X, self.Y, self.Z = float(x), float(y), float(z)

    def Add(self, o):
        return XYZ(self.X + o.X, self.Y + o.Y, self.Z + o.Z)

    def Subtract(self, o):
        return XYZ(self.X - o.X, self.Y - o.Y, self.Z - o.Z)

    def Multiply(self, s):
        return XYZ(self.X * s, self.Y * s, self.Z * s)

    def Negate(self):
        return XYZ(-self.X, -self.Y, -self.Z)

    def DotProduct(self, o):
        return self.X * o.X + self.Y * o.Y + self.Z * o.Z

    def CrossProduct(self, o):
        return XYZ(self.Y * o.Z - self.Z * o.Y, self.Z * o.X - self.X * o.Z, self.X * o.Y - self.Y * o.X)

    def GetLength(self):
        return math.sqrt(self.DotProduct(self))

    def Normalize(self):
        n = self.GetLength()
        if n < 1e-12:
            raise MockRevitError('Normalize of a zero-length vector')
        return XYZ(self.X / n, self.Y / n, self.Z / n)

    def arr(self):
        return np.array([self.X, self.Y, self.Z])


XYZ.BasisX = XYZ(1, 0, 0)
XYZ.BasisY = XYZ(0, 1, 0)
XYZ.BasisZ = XYZ(0, 0, 1)
XYZ.Zero = XYZ(0, 0, 0)


def xyz_of(a):
    return XYZ(a[0], a[1], a[2])


class Line(object):
    @staticmethod
    def CreateBound(p, q):
        if p.Subtract(q).GetLength() < SHORT_CURVE_FT:
            raise MockRevitError('Curve length is too small for Revit\'s tolerance')
        line = Line()
        line.p, line.q = p, q
        return line

    def GetEndPoint(self, i):
        return self.p if i == 0 else self.q

    @property
    def Length(self):
        return self.p.Subtract(self.q).GetLength()

    def samples(self):
        return [self.p.arr(), self.q.arr()]


class Arc(object):
    @staticmethod
    def Create(p0, p1, pm):
        a, b, c = p0.arr(), pm.arr(), p1.arr()
        n = np.cross(b - a, c - b)
        if np.linalg.norm(n) < 1e-14:
            raise MockRevitError('Arc points are collinear')
        n /= np.linalg.norm(n)
        # circumcentre in 3-D
        ab, ac = b - a, c - a
        w = np.cross(ab, ac)
        centre = a + (np.cross(w, ab) * ac.dot(ac) + np.cross(ac, w) * ab.dot(ab)) / (2.0 * w.dot(w))
        r = np.linalg.norm(a - centre)
        e1 = (a - centre) / r
        e2 = np.cross(n, e1)

        def ang(p):
            v = p - centre
            return math.atan2(v.dot(e2), v.dot(e1)) % (2 * math.pi)
        sweep = ang(c)
        if not (0 < ang(b) < sweep):
            raise MockRevitError('Arc mid point does not lie between its ends')
        arc = Arc()
        arc.p, arc.q = p0, p1
        arc.centre, arc.r, arc.e1, arc.e2, arc.sweep = centre, r, e1, e2, sweep
        if r * sweep < SHORT_CURVE_FT:
            raise MockRevitError('Arc length is too small for Revit\'s tolerance')
        return arc

    def GetEndPoint(self, i):
        return self.p if i == 0 else self.q

    @property
    def Length(self):
        return self.r * self.sweep

    def samples(self):
        k = max(4, int(math.ceil(self.sweep * ARC_SAMPLES_PER_RAD)))
        t = np.linspace(0.0, self.sweep, k + 1)
        return [self.centre + self.r * (math.cos(x) * self.e1 + math.sin(x) * self.e2) for x in t]


class CurveLoop(object):
    def __init__(self):
        self.curves = []

    def Append(self, curve):
        if self.curves:
            gap = self.curves[-1].GetEndPoint(1).Subtract(curve.GetEndPoint(0)).GetLength()
            if gap > 1e-9:
                raise MockRevitError('CurveLoop.Append: curve is not contiguous (gap %.3g ft)' % gap)
        self.curves.append(curve)

    def closed(self):
        return self.curves and self.curves[-1].GetEndPoint(1).Subtract(
            self.curves[0].GetEndPoint(0)).GetLength() < 1e-9


class Frame(object):
    def __init__(self, origin, bx, by, bz):
        for u, v in ((bx, by), (by, bz), (bx, bz)):
            if abs(u.DotProduct(v)) > 1e-9:
                raise MockRevitError('Frame axes are not orthogonal')
        if bx.CrossProduct(by).Subtract(bz).GetLength() > 1e-9:
            raise MockRevitError('Frame is not right-handed')
        self.Origin, self.BasisX, self.BasisY, self.BasisZ = origin, bx, by, bz


class Face(object):
    def __init__(self, resolver):
        self._resolver = resolver

    @property
    def MaterialElementId(self):
        return self._resolver()


class Solid(object):
    def __init__(self, tris, groups):
        self.tris = tris            # (M,3,3) feet
        self.groups = groups        # profile-curve index per triangle
        self.owner = None           # FreeFormElement, set on creation
        self.material_resolver = lambda: ElementId(-1)
        v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
        self.Volume = abs(np.einsum('ij,ij->i', v0, np.cross(v1, v2)).sum() / 6.0)

    @property
    def Faces(self):
        return [Face(self.material_resolver) for _ in range(int(self.groups.max()) + 1)]

    def transformed(self, t):
        R = np.array([t.BasisX.arr(), t.BasisY.arr(), t.BasisZ.arr()]).T
        s = Solid(self.tris @ R.T + t.Origin.arr(), self.groups)
        s.owner = self.owner
        s.material_resolver = self.material_resolver
        return s

    def IntersectWithCurve(self, line, options):
        p0, p1 = line.p.arr(), line.q.arr()
        d = p1 - p0
        v0, v1, v2 = self.tris[:, 0], self.tris[:, 1], self.tris[:, 2]
        e1, e2 = v1 - v0, v2 - v0
        h = np.cross(d, e2)
        a = np.einsum('ij,ij->i', e1, h)
        ok = np.abs(a) > 1e-18
        f = np.zeros_like(a)
        f[ok] = 1.0 / a[ok]
        s = p0 - v0
        u = f * np.einsum('ij,ij->i', s, h)
        q = np.cross(s, e1)
        v = f * (q @ d)
        t = f * np.einsum('ij,ij->i', e2, q)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t >= 0) & (t <= 1)
        ts = []
        for x in np.sort(t[hit]):
            if not ts or x - ts[-1] > 1e-9:
                ts.append(float(x))
        if len(ts) % 2:
            ts = [0.0] + ts
        segs = [Line.CreateBound(xyz_of(p0 + d * ts[i]), xyz_of(p0 + d * ts[i + 1]))
                for i in range(0, len(ts), 2) if (ts[i + 1] - ts[i]) * np.linalg.norm(d) > SHORT_CURVE_FT]
        return types.SimpleNamespace(SegmentCount=len(segs), GetCurveSegment=lambda i: segs[i])


def revolve(frame, loops, a0, a1):
    if len(loops) != 1:
        raise MockRevitError('mock supports one profile loop')
    loop = loops[0]
    if not loop.closed():
        raise MockRevitError('CreateRevolvedGeometry: profile loop is not closed')
    o = frame.Origin.arr()
    X, Y, Z = frame.BasisX.arr(), frame.BasisY.arr(), frame.BasisZ.arr()
    th = (np.arange(SEGMENTS_AROUND) + 0.5) * (a1 - a0) / SEGMENTS_AROUND + a0
    tris, groups = [], []
    for gi, curve in enumerate(loop.curves):
        pts = curve.samples()
        ra = []
        for p in pts:
            v = p - o
            x, y, z = v.dot(X), v.dot(Y), v.dot(Z)
            if abs(y) > 1e-9:
                raise MockRevitError('Revolve profile is not in the frame XZ plane (y=%.3g ft)' % y)
            if x < -1e-9:
                raise MockRevitError('Revolve profile crosses the axis (x=%.3g ft)' % x)
            ra.append((max(x, 0.0), z))
        for (r0, z0), (r1, z1) in zip(ra[:-1], ra[1:]):
            for j in range(SEGMENTS_AROUND):
                c0, s0 = math.cos(th[j]), math.sin(th[j])
                c1, s1 = math.cos(th[(j + 1) % SEGMENTS_AROUND]), math.sin(th[(j + 1) % SEGMENTS_AROUND])
                A = o + r0 * (c0 * X + s0 * Y) + z0 * Z
                B = o + r0 * (c1 * X + s1 * Y) + z0 * Z
                C = o + r1 * (c1 * X + s1 * Y) + z1 * Z
                D = o + r1 * (c0 * X + s0 * Y) + z1 * Z
                for tri in ((A, B, C), (A, C, D)):
                    if np.linalg.norm(np.cross(tri[1] - tri[0], tri[2] - tri[0])) > 1e-16:
                        tris.append(tri)
                        groups.append(gi)
    return Solid(np.array(tris), np.array(groups))


class GeometryInstance(object):
    def __init__(self, transform, solids_):
        self.t, self.solids = transform, solids_

    def GetInstanceGeometry(self):
        return [s.transformed(self.t) for s in self.solids]


class Transform(object):
    def __init__(self, origin, bx, by, bz):
        self.Origin, self.BasisX, self.BasisY, self.BasisZ = origin, bx, by, bz

    def OfPoint(self, p):
        return self.Origin.Add(self.BasisX.Multiply(p.X)).Add(self.BasisY.Multiply(p.Y)).Add(self.BasisZ.Multiply(p.Z))


class BoundingBoxXYZ(object):
    def __init__(self):
        self.Min, self.Max = XYZ(), XYZ()


# --------------------------------------------------------------- elements
class ElementId(object):
    def __init__(self, v):
        self.Value = int(v)

    def __eq__(self, o):
        return isinstance(o, ElementId) and o.Value == self.Value

    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        return hash(self.Value)


_NEXT = [1000]


def new_id():
    _NEXT[0] += 1
    return ElementId(_NEXT[0])


class Element(object):
    def __init__(self, doc):
        self.Document = doc
        self.Id = new_id()
        doc.elements[self.Id.Value] = self


class NameDescriptor(object):
    @staticmethod
    def GetValue(element):
        return element.Name


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
    def __init__(self, owner, key):
        self.owner, self.key = owner, key
        self.IsReadOnly = False

    def Set(self, value):
        self.owner.Document.require_tx('Parameter.Set')
        self.owner.values[self.key] = value
        return True


class FreeFormElement(Element):
    @staticmethod
    def Create(doc, solid):
        doc.require_tx('FreeFormElement.Create')
        if not doc.IsFamilyDocument:
            raise MockRevitError('FreeFormElement.Create needs a family document')
        e = FreeFormElement(doc)
        e.solid, e.Subcategory, e.values = solid, None, {}
        solid.owner = e
        e._mat_param = ElemParam(e, 'material')
        return e

    def get_Parameter(self, bip):
        if bip == 'MATERIAL_ID_PARAM':
            return self._mat_param
        return None

    def get_Geometry(self, options):
        doc = self.Document
        fp = doc.FamilyManager.assoc.get(id(self._mat_param))
        self.solid.material_resolver = lambda: doc.FamilyManager.type_value(fp) if fp else ElementId(-1)
        return [self.solid]


class Color(object):
    def __init__(self, r, g, b):
        for v in (r, g, b):
            if not (0 <= int(v) <= 255) or int(v) != v:
                raise MockRevitError('Color channel out of byte range')
        self.Red, self.Green, self.Blue = int(r), int(g), int(b)


class AssetProperty(object):
    def __init__(self, name, value, connected=0):
        self.Name, self.Value, self.NumberOfConnectedProperties = name, value, connected

    def RemoveConnectedAsset(self):
        if not self.NumberOfConnectedProperties:
            raise MockRevitError('No connected asset on ' + self.Name)
        self.NumberOfConnectedProperties = 0

    def SetValueAsColor(self, c):
        self.Value = (c.Red, c.Green, c.Blue)

    def GetValueAsColor(self):
        return Color(*self.Value)


class Asset(object):
    def __init__(self, name, props):
        self.Name = name
        self._props = props

    @property
    def Size(self):
        return len(self._props)

    def __getitem__(self, i):
        return self._props[i]

    def FindByName(self, name):
        return next((p for p in self._props if p.Name == name), None)

    def copy(self, name):
        return Asset(name, [AssetProperty(p.Name, p.Value, p.NumberOfConnectedProperties) for p in self._props])


def library_assets():
    # a Generic library asset that deliberately carries connected maps, as a real one may
    return [Asset('Generic - mock library', [
        AssetProperty('BaseSchema', 'GenericSchema'), AssetProperty('generic_diffuse', (80, 80, 80), 1),
        AssetProperty('generic_bump_map', 0.0, 1), AssetProperty('generic_glossiness', 0.5),
        AssetProperty('generic_transparency', 0.0), AssetProperty('generic_reflectivity_at_0deg', 0.1),
        AssetProperty('generic_reflectivity_at_90deg', 0.5), AssetProperty('generic_self_illum_luminance', 0.0),
        AssetProperty('generic_refraction_index', 1.0), AssetProperty('generic_is_metal', False)])]


class AppearanceAssetElement(Element):
    @staticmethod
    def Create(doc, name, asset):
        doc.require_tx('AppearanceAssetElement.Create')
        e = AppearanceAssetElement(doc)
        e.Name, e.asset = name, asset.copy(name)
        return e

    def GetRenderingAsset(self):
        return self.asset


class Material(Element):
    @staticmethod
    def Create(doc, name):
        doc.require_tx('Material.Create')
        if any(isinstance(e, Material) and e.Name == name for e in doc.elements.values()):
            raise MockRevitError('Material name exists: ' + name)
        m = Material(doc)
        m.Name, m.Color, m.Transparency, m.MaterialClass = name, Color(127, 127, 127), 0, ''
        m.AppearanceAssetId = ElementId(-1)
        return m.Id


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


class ViewFamilyType(Element):
    pass


class View3D(Element):
    @staticmethod
    def CreateIsometric(doc, type_id):
        doc.require_tx('View3D.CreateIsometric')
        v = View3D(doc)
        v.Name, v.hidden, v.box, v.IsSectionBoxActive = None, set(), None, False
        return v

    def SetOrientation(self, o):
        self.Document.require_tx('SetOrientation')
        if abs(o.up.DotProduct(o.forward)) > 1e-9 or abs(o.up.GetLength() - 1) > 1e-9 \
                or abs(o.forward.GetLength() - 1) > 1e-9:
            raise MockRevitError('View orientation: up and forward must be perpendicular unit vectors')
        self.orientation = o

    def CanCategoryBeHidden(self, cid):
        return True

    def SetCategoryHidden(self, cid, flag):
        self.hidden.add(cid.Value)

    def SetSectionBox(self, box):
        if not (box.Min.X < box.Max.X and box.Min.Y < box.Max.Y and box.Min.Z < box.Max.Z):
            raise MockRevitError('Section box min must be below max')
        self.box = box


class ViewOrientation3D(object):
    def __init__(self, eye, up, forward):
        self.eye, self.up, self.forward = eye, up, forward


class Level(Element):
    @staticmethod
    def Create(doc, elevation):
        lv = Level(doc)
        lv.Elevation = elevation
        return lv


class FloorType(Element):
    pass


class PlanarFace(object):
    def __init__(self, z):
        self.z = z

    def Project(self, p):
        return types.SimpleNamespace(XYZPoint=XYZ(p.X, p.Y, self.z))


class Floor(Element):
    @staticmethod
    def GetDefaultFloorType(doc, structural):
        return next(e for e in doc.elements.values() if isinstance(e, FloorType)).Id

    @staticmethod
    def Create(doc, loops, type_id, level_id):
        doc.require_tx('Floor.Create')
        f = Floor(doc)
        f.type_id, f.values, f.thickness_ft = type_id, {'height': 0.0}, 1.0
        f._height = ElemParam(f, 'height')
        return f

    def get_Parameter(self, bip):
        return self._height if bip == 'FLOOR_HEIGHTABOVELEVEL_PARAM' else None

    def GetTypeId(self):
        return self.type_id

    def GetGeometryObjectFromReference(self, ref):
        return PlanarFace(self.values['height'] - self.thickness_ft)


class HostObjectUtils(object):
    @staticmethod
    def GetBottomFaces(floor):
        return [types.SimpleNamespace(element=floor, side='bottom')]


class FamilySymbolParam(object):
    def __init__(self, symbol, name, value):
        self.symbol, self.name, self.value = symbol, name, value
        self.IsReadOnly = False

    def AsElementId(self):
        return self.value

    def Set(self, value):
        self.symbol.Document.require_tx('FamilySymbol parameter Set')
        self.value = value
        return True


class FamilySymbol(Element):
    def Activate(self):
        self.Document.require_tx('FamilySymbol.Activate')

    def LookupParameter(self, name):
        return self.params.get(name)


class Family(Element):
    def GetFamilySymbolIds(self):
        return [self.symbol.Id]


class FamilyInstance(Element):
    def get_Geometry(self, options):
        fam = self.symbol.family_doc
        solids_ = []
        for e in fam.elements.values():
            if isinstance(e, FreeFormElement):
                fp = fam.FamilyManager.assoc.get(id(e._mat_param))
                pname = fp.Definition.Name
                s = e.solid
                s.material_resolver = (lambda n=pname: self.symbol.params[n].value)
                solids_.append(s)
        return [GeometryInstance(self.transform, solids_)]

    def GetTransform(self):
        return self.transform

    def get_BoundingBox(self, view):
        pts = np.concatenate([s.tris.reshape(-1, 3) for g in self.get_Geometry(None)
                              for s in g.GetInstanceGeometry()])
        box = BoundingBoxXYZ()
        box.Min, box.Max = xyz_of(pts.min(axis=0)), xyz_of(pts.max(axis=0))
        return box


class Creator(object):
    def __init__(self, doc):
        self.doc = doc

    def NewFamilyInstance(self, ref, point, ref_dir, symbol):
        self.doc.require_tx('NewFamilyInstance')
        inst = FamilyInstance(self.doc)
        inst.symbol, inst.Host = symbol, ref.element
        bz = XYZ(0, 0, -1)                   # normal of a floor's bottom face
        bx = ref_dir.Normalize()
        inst.transform = Transform(point, bx, bz.CrossProduct(bx), bz)
        return inst


class Warning_(object):
    def __init__(self, text):
        self.text = text

    def GetDescriptionText(self):
        return self.text


# --------------------------------------------------------------- family manager
class FamilyParameter(object):
    def __init__(self, name, spec, builtin=False):
        self.Definition = types.SimpleNamespace(Name=name)
        self.spec, self.builtin = spec, builtin


class FamilyType(object):
    def __init__(self, name):
        self.Name = name
        self.values = {}

    def AsDouble(self, p):
        v = self.values.get(p.Definition.Name)
        return v if isinstance(v, float) else None


class FamilyManager(object):
    def __init__(self, doc):
        self.doc = doc
        self.Parameters = []
        self.Types = []
        self.CurrentType = None
        self.assoc = {}
        self._builtins = {}

    def NewType(self, name):
        self.doc.require_tx('NewType')
        t = FamilyType(name)
        self.Types.append(t)
        self.CurrentType = t
        return t

    def AddParameter(self, name, group, spec, is_instance):
        self.doc.require_tx('AddParameter')
        if any(p.Definition.Name == name for p in self.Parameters):
            raise MockRevitError('Parameter exists: ' + name)
        p = FamilyParameter(name, spec)
        self.Parameters.append(p)
        return p

    def Set(self, p, value):
        self.doc.require_tx('FamilyManager.Set')
        if self.CurrentType is None:
            raise MockRevitError('FamilyManager.Set without a current type')
        if p.spec == 'material' and not isinstance(value, ElementId):
            raise MockRevitError('material parameter needs an ElementId')
        self.CurrentType.values[p.Definition.Name] = value

    def SetFormula(self, p, formula):
        self.doc.require_tx('SetFormula')
        if p.spec != 'length' or not formula.endswith('"'):
            raise MockRevitError('mock only parses inch-constant length formulas: %r' % formula)
        self.CurrentType.values[p.Definition.Name] = float(formula[:-1]) / 12.0

    def get_Parameter(self, bip):
        if bip not in self._builtins:
            self._builtins[bip] = FamilyParameter(bip, 'text', builtin=True)
        return self._builtins[bip]

    def AssociateElementParameterToFamilyParameter(self, elem_param, fam_param):
        self.doc.require_tx('Associate')
        if fam_param.spec != 'material':
            raise MockRevitError('mock: material binding expected')
        self.assoc[id(elem_param)] = fam_param

    def GetAssociatedFamilyParameter(self, elem_param):
        return self.assoc.get(id(elem_param))

    def type_value(self, fp):
        return self.CurrentType.values.get(fp.Definition.Name)


# --------------------------------------------------------------- documents
class Document(object):
    def __init__(self, app, family):
        self.app = app
        self.IsFamilyDocument = family
        self.elements = {}
        self.tx_open = False
        self.closed = False
        self.Settings = types.SimpleNamespace(Categories=Categories([
            Category('Generic Models'), Category('Lighting Fixtures'), Category('Reference Planes')]))
        ViewFamilyType(self).ViewFamily = 'ThreeDimensional'
        if family:
            self.FamilyManager = FamilyManager(self)
            self.OwnerFamily = types.SimpleNamespace(
                FamilyCategory=self.Settings.Categories[0], FamilyPlacementType='WorkPlaneBased',
                get_Parameter=lambda bip: ElemParam(types.SimpleNamespace(Document=self, values={}), bip))
        else:
            Level(self).Elevation = 0.0
            ft = FloorType(self)
            ft.Name = 'Generic 12"'
            self.Create = Creator(self)

    def require_tx(self, what):
        if self.closed:
            raise MockRevitError(what + ' on a closed document')
        if not self.tx_open:
            raise MockRevitError(what + ' outside a transaction')

    def GetElement(self, eid):
        return self.elements.get(eid.Value)

    def Regenerate(self):
        self.require_tx('Regenerate')

    def GetWarnings(self):
        return []

    def SaveAs(self, path, options):
        if self.tx_open:
            raise MockRevitError('SaveAs with an open transaction')
        with open(path, 'wb') as fh:
            fh.write(b'MOCK RFA - not a Revit file\n')
        self.app.saved[os.path.normpath(path)] = self
        self.path = path

    def ExportImage(self, options):
        if self.tx_open:
            raise MockRevitError('ExportImage with an open transaction')
        for vid in options.views:
            view = self.GetElement(vid)
            write_png(options.FilePath + ' - 3D View - ' + view.Name + '.png')

    def LoadFamily(self, target):
        if target.tx_open:
            raise MockRevitError('LoadFamily into a document with an open transaction')
        fam = Family(target)
        sym = FamilySymbol(target)
        sym.family_doc = self
        sym.params = {}
        for p in self.FamilyManager.Parameters:
            v = self.FamilyManager.CurrentType.values.get(p.Definition.Name)
            if p.spec == 'material':
                sym.params[p.Definition.Name] = FamilySymbolParam(sym, p.Definition.Name, v)
        fam.symbol = sym
        return fam

    def Close(self, save):
        self.closed = True


class Transaction(object):
    def __init__(self, doc, name):
        self.doc = doc

    def Start(self):
        if self.doc.tx_open:
            raise MockRevitError('nested transaction')
        self.doc.tx_open = True

    def Commit(self):
        self.doc.tx_open = False

    def RollBack(self):
        self.doc.tx_open = False


class FilteredElementCollector(object):
    def __init__(self, doc):
        self.doc = doc

    def OfClass(self, cls):
        return [e for e in list(self.doc.elements.values()) if isinstance(e, cls)]


class Application(object):
    VersionNumber = '2025'
    VersionBuild = 'MOCK'
    ShortCurveTolerance = SHORT_CURVE_FT

    def __init__(self):
        self.saved = {}

    def NewFamilyDocument(self, template):
        return Document(self, True)

    def NewProjectDocument(self, units):
        return Document(self, False)

    def OpenDocumentFile(self, path):
        doc = self.saved[os.path.normpath(path)]
        doc.closed = False                  # the mock "reopens" the saved state
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


class GenericList(object):
    def __getitem__(self, t):
        return lambda items: list(items)


def make_db():
    DB = types.ModuleType('Autodesk.Revit.DB')
    ns = types.SimpleNamespace
    DB.XYZ, DB.Line, DB.Arc, DB.CurveLoop, DB.Frame = XYZ, Line, Arc, CurveLoop, Frame
    DB.Solid, DB.GeometryInstance, DB.BoundingBoxXYZ = Solid, GeometryInstance, BoundingBoxXYZ
    DB.GeometryCreationUtilities = ns(CreateRevolvedGeometry=revolve)
    DB.FreeFormElement, DB.ElementId, DB.Element, DB.Color = FreeFormElement, ElementId, ElementNS, Color
    DB.Material, DB.AppearanceAssetElement = Material, AppearanceAssetElement
    DB.Visual = ns(AssetType=ns(Appearance='appearance'), AppearanceAssetEditScope=AppearanceAssetEditScope)
    DB.FilteredElementCollector, DB.Transaction = FilteredElementCollector, Transaction
    DB.ViewFamilyType, DB.View3D, DB.ViewOrientation3D = ViewFamilyType, View3D, ViewOrientation3D
    DB.ViewFamily = ns(ThreeDimensional='ThreeDimensional')
    DB.ViewDetailLevel = ns(Fine='Fine')
    DB.DisplayStyle = ns(Shading='Shading', Realistic='Realistic')
    DB.Level, DB.Floor, DB.HostObjectUtils = Level, Floor, HostObjectUtils
    DB.Options = lambda: ns(ComputeReferences=True)
    DB.SolidCurveIntersectionOptions = lambda: ns()
    DB.SaveAsOptions = lambda: ns()
    DB.ImageExportOptions = ImageExportOptions
    DB.ExportRange = ns(SetOfViews='SetOfViews')
    DB.ImageFileType = ns(PNG='PNG')
    DB.ImageResolution = ns(DPI_150='DPI_150')
    DB.ZoomFitType = ns(FitToPage='FitToPage')
    DB.UnitSystem = ns(Imperial='Imperial')
    DB.GroupTypeId = ns(Materials='materials', Geometry='geometry', IdentityData='identity')
    DB.SpecTypeId = ns(Reference=ns(Material='material'), Length='length', String=ns(Text='text'))
    DB.BuiltInCategory = ns(OST_LightingFixtures='OST_LightingFixtures')

    def get_category(doc, bic):
        return next(c for c in doc.Settings.Categories if c.Name == 'Lighting Fixtures')
    DB.Category = ns(GetCategory=get_category)
    names = ['ALL_MODEL_MANUFACTURER', 'ALL_MODEL_MODEL', 'ALL_MODEL_DESCRIPTION', 'ALL_MODEL_URL',
             'SYMBOL_NAME_PARAM', 'FAMILY_ALWAYS_VERTICAL', 'MATERIAL_ID_PARAM', 'FLOOR_HEIGHTABOVELEVEL_PARAM']
    DB.BuiltInParameter = ns(**dict((n, n) for n in names))
    return DB


# --------------------------------------------------------------- harness
def run_verifier(root):
    cmd = [sys.executable, os.path.join(root, 'output', 'cassia', 'source', 'verify_cassia.py')]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    tmp = tempfile.mkdtemp(prefix='cassia-mock-')
    if os.path.normpath(tmp).startswith(REPO + os.sep):
        raise SystemExit('refusing to write inside the repository')
    src = os.path.join(tmp, 'output', 'cassia', 'source')
    os.makedirs(src)
    open(os.path.join(tmp, 'AGENTS.md'), 'w').write('mock root\n')
    for name in ('build_cassia.py', 'cassia_geometry.py', 'verify_cassia.py'):
        shutil.copy(os.path.join(HERE, name), os.path.join(src, name))

    DB = make_db()
    mods = {'clr': types.SimpleNamespace(AddReference=lambda n: None),
            'Autodesk': types.ModuleType('Autodesk'), 'Autodesk.Revit': types.ModuleType('Autodesk.Revit'),
            'Autodesk.Revit.DB': DB, 'System': types.ModuleType('System'),
            'System.Collections': types.ModuleType('System.Collections'),
            'System.Collections.Generic': types.ModuleType('System.Collections.Generic')}
    mods['Autodesk.Revit'].DB = DB
    mods['Autodesk'].Revit = mods['Autodesk.Revit']
    mods['System.Collections.Generic'].List = GenericList()
    saved_modules = dict((k, sys.modules.get(k)) for k in mods)
    sys.modules.update(mods)
    real_isfile = os.path.isfile
    os.path.isfile = lambda p: True if str(p).startswith('C:\\ProgramData') else real_isfile(p)
    sys.dont_write_bytecode = True
    builder = os.path.join(src, 'build_cassia.py')
    g = {'__file__': builder, '__name__': '__main__',
         '__revit__': types.SimpleNamespace(Application=Application())}
    error = None
    try:
        exec(compile(open(builder).read(), builder, 'exec'), g)
    except Exception as exc:                     # the builder re-raises on failure by design
        error = exc
    finally:
        os.path.isfile = real_isfile
        for k, v in saved_modules.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        sys.modules.pop('cassia_geometry', None)
    report_path = os.path.join(tmp, 'output', 'cassia', 'validation.json')
    rep = json.load(open(report_path)) if real_isfile(report_path) else {}
    print('mock run dir:', tmp)
    print('builder exception:', repr(error))
    print('stage:', rep.get('stage'), '| technical_pass:', rep.get('technical_pass'))
    print('failed gates:', rep.get('failed_gates'))
    if rep.get('error'):
        print(rep['error'])
    code, out = run_verifier(tmp)
    print('verifier on mock report -> exit %d' % code)
    print(out)
    ok = error is None and rep.get('technical_pass') is True and code == 0

    # the verifier must reject tampered reports
    for label, mutate in [
            ('ray off by 0.05 in', lambda r: r['family']['rays']['canopy_diameter'].__setitem__(
                'measured', r['family']['rays']['canopy_diameter']['measured'] + 0.05)),
            ('project warning', lambda r: r['hosted'].__setitem__('warnings', ['mock warning']))]:
        bad = json.loads(json.dumps(rep))
        mutate(bad)
        json.dump(bad, open(report_path, 'w'))
        code_bad, out_bad = run_verifier(tmp)
        print('verifier on tampered report (%s) -> exit %d' % (label, code_bad))
        print('  ' + out_bad.strip().splitlines()[1] if len(out_bad.strip().splitlines()) > 1 else out_bad)
        ok = ok and code_bad == 1
    json.dump(rep, open(report_path, 'w'), indent=2)
    print('MOCK DRY-RUN %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
