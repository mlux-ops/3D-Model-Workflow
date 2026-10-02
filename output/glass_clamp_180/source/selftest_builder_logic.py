"""Run the REAL builder functions against a geometric stand-in of the Revit API (CPython 3, no Revit).

What it executes from build_clamp.py, unmodified: reference_planes() (all planes and dimensions),
make_plate(), make_cap(), lock_sides(), dimension(), new_plane(), polygon_profile().

What the stand-in enforces, as Revit does:
  * NewReferencePlane: plane through the bubble/free line containing the cut vector; Flip() reverses it.
  * NewDimension: every reference is a reference plane seen edge-on in that view (plan: vertical planes;
    Front/Back elevation: planes normal to X or Z), every plane is perpendicular to the dimension line,
    no two planes coincide, the line lies in the view plane.
  * NewAlignment: the face is planar, parallel to the target plane and ALREADY lies on it (tolerance 1e-9 ft),
    and both are visible in that view.
  * NewExtrusion: closed profile, every edge longer than Revit's short-curve tolerance (0.00256 ft), profile
    in the sketch plane; side faces and end faces are derived from the profile and the extrusion depth.

What it cannot prove: Revit's constraint solver during a flex, regeneration, labels driving geometry,
or any behaviour of the real API beyond the rules above. Exit 0 when every check holds.
"""
import math
import os
import sys
import types

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clamp_spec as S  # noqa: E402

SHORT_CURVE_FT = 0.00256
TOL_FT = 1e-9


# ----------------------------------------------------------------- geometry stand-ins
class XYZ(object):
    def __init__(self, x, y, z):
        self.X, self.Y, self.Z = float(x), float(y), float(z)

    def Add(self, o):
        return XYZ(self.X + o.X, self.Y + o.Y, self.Z + o.Z)

    def Subtract(self, o):
        return XYZ(self.X - o.X, self.Y - o.Y, self.Z - o.Z)

    def Multiply(self, k):
        return XYZ(self.X * k, self.Y * k, self.Z * k)

    def DotProduct(self, o):
        return self.X * o.X + self.Y * o.Y + self.Z * o.Z

    def CrossProduct(self, o):
        return XYZ(self.Y * o.Z - self.Z * o.Y, self.Z * o.X - self.X * o.Z, self.X * o.Y - self.Y * o.X)

    def GetLength(self):
        return math.sqrt(self.DotProduct(self))

    def Normalize(self):
        n = self.GetLength()
        return XYZ(self.X / n, self.Y / n, self.Z / n)

    def __repr__(self):
        return 'XYZ(%.6g, %.6g, %.6g)' % (self.X * 12, self.Y * 12, self.Z * 12)


XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ, XYZ.Zero = XYZ(1, 0, 0), XYZ(0, 1, 0), XYZ(0, 0, 1), XYZ(0, 0, 0)


class Line(object):
    def __init__(self, a, b):
        self.a, self.b = a, b

    @staticmethod
    def CreateBound(a, b):
        if b.Subtract(a).GetLength() < SHORT_CURVE_FT:
            raise Exception('Curve length is too small for Revit\'s tolerance')
        return Line(a, b)

    def GetEndPoint(self, i):
        return self.a if i == 0 else self.b


class Arr(object):
    def __init__(self):
        self.items = []

    def Append(self, x):
        self.items.append(x)


class Id(object):
    _next = [1000]

    def __init__(self):
        Id._next[0] += 1
        self.Value = Id._next[0]


class Ref(object):
    def __init__(self, kind, target):
        self.kind, self.target = kind, target
        self.ElementReferenceType = 'REFERENCE_TYPE_SURFACE'


class Param(object):
    def __init__(self, name):
        self.name, self.IsReadOnly, self.v = name, False, 'Not a Reference'

    def AsValueString(self):
        return self.v

    def SetValueString(self, t):
        self.v = t
        return True

    def Set(self, value):
        self.v = value


class RefPlane(object):
    def __init__(self, name, origin, normal):
        self.Id, self.Name, self.origin, self.Normal = Id(), name, origin, normal.Normalize()
        self.Pinned = False
        self._p = Param('Is Reference')

    def Flip(self):
        self.Normal = self.Normal.Multiply(-1)

    def GetPlane(self):
        return types.SimpleNamespace(Origin=self.origin, Normal=self.Normal)

    def GetReference(self):
        return Ref('plane', self)

    def get_Parameter(self, bip):
        return self._p

    def distance(self, p):
        return p.Subtract(self.origin).DotProduct(self.Normal)


class Dim(object):
    def __init__(self, refs):
        self.refs, self.AreSegmentsEqual, self.FamilyLabel, self.IsLocked = refs, False, None, False


class PlanarFace(object):
    def __init__(self, normal, origin):
        self.FaceNormal, self.Origin = normal, origin
        self.Reference = Ref('face', self)


class Solid(object):
    def __init__(self, faces):
        self.Faces, self.Volume = faces, 1.0


class GeometryInstance(object):
    pass


class Extrusion(object):
    def __init__(self, profile, sketch, depth):
        self.Id, self.profile, self.sketch, self.depth = Id(), profile, sketch, depth
        self.params = {}
        self.Subcategory, self.visibility = None, None

    def get_Parameter(self, bip):
        return self.params.setdefault(bip, Param(bip))

    def SetVisibility(self, vis):
        self.visibility = vis

    def get_Geometry(self, options):
        n = self.sketch.normal
        pts = [c.a for c in self.profile.items[0].items]
        centre = XYZ(sum(p.X for p in pts) / len(pts), sum(p.Y for p in pts) / len(pts), sum(p.Z for p in pts) / len(pts))
        faces = []
        for c in self.profile.items[0].items:
            edge = c.b.Subtract(c.a)
            out = edge.CrossProduct(n).Normalize()
            mid = c.a.Add(edge.Multiply(0.5))
            if mid.Subtract(centre).DotProduct(out) < 0:
                out = out.Multiply(-1)
            faces.append(PlanarFace(out, mid.Add(n.Multiply(self.depth / 2.0))))
        faces.append(PlanarFace(n.Multiply(-1), centre))
        faces.append(PlanarFace(n, centre.Add(n.Multiply(self.depth))))
        return [Solid(faces)]


class SketchPlane(object):
    def __init__(self, plane):
        self.plane, self.normal = plane, plane.Normal

    @staticmethod
    def Create(doc, plane_id):
        return SketchPlane(doc.by_id[plane_id.Value])

    def GetPlane(self):
        return self.plane.GetPlane()


class View(object):
    def __init__(self, name, sees):
        self.Name, self.sees = name, sees      # sees: axis the view looks along ('Z' plan, 'Y' elevation)

    def edge_on(self, normal):
        axis = {'Z': XYZ.BasisZ, 'Y': XYZ.BasisY}[self.sees]
        return abs(normal.DotProduct(axis)) < 1e-9


class Violation(Exception):
    pass


class FamilyCreate(object):
    def __init__(self, doc):
        self.doc = doc

    def NewReferencePlane(self, bubble, free, cut, view):
        normal = free.Subtract(bubble).CrossProduct(cut)
        plane = RefPlane('Reference Plane', bubble, normal)
        self.doc.add(plane)
        return plane

    def NewDimension(self, view, line, array):
        refs = array.items
        if len(refs) < 2:
            raise Violation('NewDimension needs two references')
        d = line.b.Subtract(line.a).Normalize()
        coord = 'Z' if view.sees == 'Z' else 'Y'
        if abs(getattr(line.a, coord)) > 1e-12 or abs(getattr(line.b, coord)) > 1e-12:
            raise Violation('dimension line not in the view plane of %s' % view.Name)
        seen = []
        for r in refs:
            if r.kind != 'plane':
                raise Violation('NewDimension reference is not a reference plane')
            p = r.target
            if not getattr(p, 'regenerated', True):
                raise Violation('The references are not geometric references.')
            if not view.edge_on(p.Normal):
                raise Violation('plane %s is not edge-on in %s' % (p.Name, view.Name))
            if abs(abs(p.Normal.DotProduct(d)) - 1.0) > 1e-9:
                raise Violation('plane %s is not perpendicular to the dimension line' % p.Name)
            pos = p.origin.DotProduct(d)
            if any(abs(pos - q) < 1e-9 for q in seen):
                raise Violation('coincident planes in one dimension (%s)' % p.Name)
            seen.append(pos)
        dim = Dim(refs)
        self.doc.dims.append(dim)
        return dim

    def NewAlignment(self, view, r1, r2):
        plane, face = r1.target, r2.target
        if r1.kind != 'plane' or r2.kind != 'face':
            raise Violation('alignment expects (plane, face)')
        if not view.edge_on(plane.Normal):
            raise Violation('plane %s not edge-on in %s' % (plane.Name, view.Name))
        if abs(abs(plane.Normal.DotProduct(face.FaceNormal)) - 1.0) > 1e-9:
            raise Violation('face not parallel to %s' % plane.Name)
        gap = plane.distance(face.Origin)
        if abs(gap) > TOL_FT:
            raise Violation('face is %.6g in off plane %s' % (gap * 12, plane.Name))
        dim = Dim([r1, r2])
        self.doc.alignments.append((plane.Name, face))
        return dim

    def NewExtrusion(self, solid, profile, sketch, depth):
        loop = profile.items[0].items
        for i, c in enumerate(loop):
            if c.b.Subtract(c.a).GetLength() < SHORT_CURVE_FT:
                raise Violation('profile edge shorter than tolerance')
            if c.b.Subtract(loop[(i + 1) % len(loop)].a).GetLength() > 1e-9:
                raise Violation('profile loop not closed')
            for p in (c.a, c.b):
                if abs(sketch.plane.distance(p)) > TOL_FT:
                    raise Violation('profile point off the sketch plane')
        ext = Extrusion(profile, sketch, depth)
        self.doc.add(ext)
        return ext


class FamilyManager(object):
    def __init__(self):
        self.assoc = []

    def get_Parameter(self, name):
        return types.SimpleNamespace(Definition=types.SimpleNamespace(Name=name))

    def AssociateElementParameterToFamilyParameter(self, p, fp):
        self.assoc.append((p.name, fp))


class Doc(object):
    strict_regen = False      # mutation mode: a plane's reference is non-geometric until the next Regenerate

    def __init__(self):
        self.by_id, self.dims, self.alignments, self.elements = {}, [], [], []
        self.FamilyCreate, self.FamilyManager = FamilyCreate(self), FamilyManager()
        self.level = types.SimpleNamespace(Name='Ref. Level', GetPlaneReference=lambda: Ref('level', None))
        self.add(RefPlane('Center (Left/Right)', XYZ.Zero, XYZ.BasisX))
        self.add(RefPlane('Center (Front/Back)', XYZ.Zero, XYZ.BasisY))

    def add(self, e):
        self.by_id[e.Id.Value] = e
        self.elements.append(e)
        if isinstance(e, RefPlane):
            e.regenerated = not Doc.strict_regen

    def Regenerate(self):
        for e in self.elements:
            if isinstance(e, RefPlane):
                e.regenerated = True


class Collector(object):
    def __init__(self, doc):
        self.doc = doc

    def OfClass(self, cls):
        if cls is RefPlane:
            return [e for e in self.doc.elements if isinstance(e, RefPlane)]
        if cls == 'Level':
            return [self.doc.level]
        return []


def fake_db():
    db = types.SimpleNamespace()
    db.XYZ, db.Line, db.ReferenceArray, db.CurveArray, db.CurveArrArray = XYZ, Line, Arr, Arr, Arr
    db.ReferencePlane, db.Level, db.Solid, db.PlanarFace, db.GeometryInstance = RefPlane, 'Level', Solid, PlanarFace, GeometryInstance
    db.Reference, db.SketchPlane = Ref, SketchPlane
    db.FilteredElementCollector = Collector
    db.BuiltInParameter = types.SimpleNamespace(EXTRUSION_END_PARAM='EXTRUSION_END_PARAM',
                                                MATERIAL_ID_PARAM='MATERIAL_ID_PARAM',
                                                ELEM_REFERENCE_NAME='ELEM_REFERENCE_NAME')
    db.FamilyElementVisibilityType = types.SimpleNamespace(Model='Model')
    db.FamilyElementVisibility = lambda kind: types.SimpleNamespace()
    db.Options = lambda: types.SimpleNamespace()
    db.Element = types.SimpleNamespace(Name=types.SimpleNamespace(GetValue=lambda e: e.Name))
    db.IFailuresPreprocessor = object                # only subclassed at load time
    return db


def load_builder_functions():
    src = open(os.path.join(HERE, 'build_clamp.py')).read()
    start = src.index('def element_name(element):')
    end = src.index('# --------------------------------------------------------------------- views')
    ns = {'DB': fake_db(), 'S': S, 'traceback': __import__('traceback'), 'math': math, 'os': os,
          'REPORT': {}, 'CAPTURED': []}
    exec(src[start:end], ns)
    return ns


def main():
    failures = []
    ns = load_builder_functions()
    v = S.resolve()
    doc = Doc()
    plan, front, back = View('Ref. Level', 'Z'), View('Front', 'Y'), View('Back', 'Y')
    rec = {}
    planes = ns['reference_planes'](doc, plan, front, v, rec)

    # planes: names, positions, normals
    want = {'Joint CL': ('X', 0.0), 'Glass Face Front': ('Y', v['Glass_Thickness'] / 2),
            'Glass Face Back': ('Y', -v['Glass_Thickness'] / 2),
            'Plate Outer Front': ('Y', v['Glass_Thickness'] / 2 + v['Plate_Thickness']),
            'Plate Outer Back': ('Y', -v['Glass_Thickness'] / 2 - v['Plate_Thickness']),
            'Clamp Left': ('X', -v['Clamp_Width'] / 2), 'Clamp Right': ('X', v['Clamp_Width'] / 2),
            'Glass Mid': ('Z', 0.0), 'Clamp Top': ('Z', v['Clamp_Height'] / 2), 'Clamp Bottom': ('Z', -v['Clamp_Height'] / 2),
            'Screw L CL': ('X', -v['Cap_Offset']), 'Screw R CL': ('X', v['Cap_Offset']),
            'Screw L Left': ('X', -v['Cap_Offset'] - v['Cap_Diameter'] / 2),
            'Screw L Right': ('X', -v['Cap_Offset'] + v['Cap_Diameter'] / 2),
            'Screw R Left': ('X', v['Cap_Offset'] - v['Cap_Diameter'] / 2),
            'Screw R Right': ('X', v['Cap_Offset'] + v['Cap_Diameter'] / 2),
            'Screw Top': ('Z', v['Cap_Diameter'] / 2), 'Screw Bottom': ('Z', -v['Cap_Diameter'] / 2)}
    for name in S.SPEC_PLANES + S.EXTRA_PLANES + S.SCREW_PLANES:
        if name not in planes:
            failures.append('plane %s not created' % name)
            continue
        axis, pos = want[name]
        p = planes[name]
        n = getattr(p.Normal, axis)
        if abs(abs(n) - 1) > 1e-9 or abs(p.origin.DotProduct(p.Normal) * 12 / n - pos) > 1e-9:
            failures.append('plane %s at %r normal %r, wanted %s = %r' % (name, p.origin, p.Normal, axis, pos))
    for name, sign in (('Glass Face Front', 1), ('Plate Outer Front', 1), ('Glass Face Back', -1), ('Plate Outer Back', -1)):
        if planes[name].Normal.Y * sign < 0.999:
            failures.append('plane %s normal %r does not point away from the glass' % (name, planes[name].Normal))

    # dimensions: all created, each with the right label / EQ
    created = sorted(rec.get('dimensions_created') or [k for k in rec.get('dimension_attempts', {})
                                                       if any(a.get('created') for a in rec['dimension_attempts'][k])])
    errs = rec.get('dimension_errors') or []
    attempts = rec.get('dimension_attempts', {})
    made = sorted(k for k, a in attempts.items() if any(x.get('created') for x in a))
    if made != S.DIMENSION_KEYS:
        failures.append('dimensions created %r, expected %r' % (made, S.DIMENSION_KEYS))
    if errs:
        failures.append('dimension errors %r' % errs)
    for k, a in attempts.items():
        if not a[0].get('created'):
            failures.append('dimension %s needed a retry: %r' % (k, a[0].get('error')))
    labels = {}
    for d in doc.dims:
        if d.FamilyLabel is not None:
            labels[d.FamilyLabel.Definition.Name] = labels.get(d.FamilyLabel.Definition.Name, 0) + 1
    if labels != S.LABELLED_DIMENSIONS:
        failures.append('labels %r, expected %r' % (labels, S.LABELLED_DIMENSIONS))
    eq = sum(1 for d in doc.dims if d.AreSegmentsEqual)
    if eq != S.EQ_DIMENSIONS:
        failures.append('EQ dimensions %d, expected %d' % (eq, S.EQ_DIMENSIONS))

    # parts and their face locks
    params = dict((n, n) for n in ('Plate_Thickness', 'Cap_Height', 'Clamp_Material'))
    subcats = {'Clamp Plate': 'Clamp Plate', 'Clamp Cap': 'Clamp Cap'}
    part_rec = {}
    elements = {}
    for key, fn in (
            ('plate_front', lambda: ns['make_plate'](doc, 'plate_front', planes['Glass Face Front'], v, [back, front],
                                                     planes, params, subcats, part_rec)),
            ('plate_back', lambda: ns['make_plate'](doc, 'plate_back', planes['Glass Face Back'], v, [front, back],
                                                    planes, params, subcats, part_rec)),
            ('cap_left', lambda: ns['make_cap'](doc, 'cap_left', -1.0, planes['Plate Outer Back'], v, [front, back],
                                                planes, params, subcats, part_rec)),
            ('cap_right', lambda: ns['make_cap'](doc, 'cap_right', 1.0, planes['Plate Outer Back'], v, [front, back],
                                                 planes, params, subcats, part_rec))):
        try:
            elements[key] = fn()
        except Exception as exc:
            failures.append('%s raised %s: %s' % (key, type(exc).__name__, exc))
    expected_targets = {
        'plate_front': {'Clamp Left', 'Clamp Right', 'Clamp Top', 'Clamp Bottom'},
        'plate_back': {'Clamp Left', 'Clamp Right', 'Clamp Top', 'Clamp Bottom'},
        'cap_left': {'Screw L Left', 'Screw L Right', 'Screw Top', 'Screw Bottom'},
        'cap_right': {'Screw R Left', 'Screw R Right', 'Screw Top', 'Screw Bottom'}}
    for key, targets in expected_targets.items():
        locks = part_rec.get(key, {}).get('side_locks', [])
        got = set(r['plane'] for r in locks if r.get('locked'))
        bad = [r for r in locks if not r.get('locked')]
        if got != targets or bad:
            failures.append('%s locks %r (failed: %r), expected %r' % (key, sorted(got), bad, sorted(targets)))
        first_view = {'plate_front': 'Back'}.get(key, 'Front')
        if any(r.get('view') != first_view for r in locks if r.get('locked')):
            failures.append('%s locked in %r, expected the %s elevation' % (key, [r.get('view') for r in locks], first_view))
    # extrusion depth binding and sketch planes
    for key, plane, depth_param in (('plate_front', 'Glass Face Front', 'Plate_Thickness'),
                                    ('plate_back', 'Glass Face Back', 'Plate_Thickness'),
                                    ('cap_left', 'Plate Outer Back', 'Cap_Height'),
                                    ('cap_right', 'Plate Outer Back', 'Cap_Height')):
        e = elements.get(key)
        if e is None:
            continue
        if e.sketch.plane.Name != plane:
            failures.append('%s sketched on %s, expected %s' % (key, e.sketch.plane.Name, plane))
        if ('EXTRUSION_END_PARAM', depth_param) not in doc.FamilyManager.assoc:
            failures.append('%s depth not bound to %s' % (key, depth_param))
        # solid extends AWAY from the glass: the far end face lies beyond the sketch plane, outward
        far = e.get_Geometry(None)[0].Faces[-1].Origin
        outward = 1 if 'Front' in plane else -1
        if (far.Y - e.sketch.plane.origin.Y) * outward <= 0:
            failures.append('%s extrudes toward the glass' % key)
    # heads: prism flats where the rays expect them
    for key, sign in (('cap_left', -1), ('cap_right', 1)):
        e = elements.get(key)
        if e is None:
            continue
        xs = [c.a.X * 12 for c in e.profile.items[0].items]
        zs = [c.a.Z * 12 for c in e.profile.items[0].items]
        cx = sign * v['Cap_Offset']
        a = v['Cap_Diameter'] / 2
        if abs(min(xs) - (cx - a)) > 1e-9 or abs(max(xs) - (cx + a)) > 1e-9 or abs(max(zs) - a) > 1e-9:
            failures.append('%s prism extents x %r..%r z ..%r' % (key, min(xs), max(xs), max(zs)))

    if ns['REPORT'].get('build_errors'):
        failures.append('build_errors %r' % ns['REPORT']['build_errors'])
    print('planes %d, dimensions %d (labels %r, EQ %d), alignments %d' % (
        len([e for e in doc.elements if isinstance(e, RefPlane)]), len(doc.dims), labels, eq, len(doc.alignments)))
    for f in failures:
        print('  FAIL ' + f)
    print('BUILDER LOGIC PASS' if not failures else 'BUILDER LOGIC FAIL')
    return 0 if not failures else 1


MUTATIONS = [
    # (label, text in build_clamp.py, replacement, spec override) - each must make the check fail
    ('screw plane 0.01 in off', "('Screw L Left', -s - d / 2.0)", "('Screw L Left', -s - d / 2.0 - 0.01)", None),
    ('Z planes dimensioned in plan view', "dims['screw_z_dia'] = dimension(doc, front,",
     "dims['screw_z_dia'] = dimension(doc, plan,", None),
    ('head flats locked to swapped planes', "{'+X': 'Screw %s Right' % side, '-X': 'Screw %s Left' % side",
     "{'+X': 'Screw %s Left' % side, '-X': 'Screw %s Right' % side", None),
    ('26-sided head (no X/Z flats)', None, None, {'CAP_SIDES': 26}),
    ('head profile off its sketch plane', "profile = polygon_profile(S.cap_polygon(sign * v['Cap_Offset'], y, v))",
     "profile = polygon_profile(S.cap_polygon(sign * v['Cap_Offset'], y + 0.01, v))", None),
    ('head centred on the wrong side', "profile = polygon_profile(S.cap_polygon(sign * v['Cap_Offset'], y, v))",
     "profile = polygon_profile(S.cap_polygon(-sign * v['Cap_Offset'], y, v))", None),
    ('no Flip of reference planes', "        plane.Flip()\n", "        pass\n", None),
    ('Cap_Spacing label dropped', "label=fm.get_Parameter('Cap_Spacing'))", "label=None)", None),
    ('plate depth not bound', "params['Plate_Thickness'])\n    bind_common", "params['Cap_Height'])\n    bind_common", None),
    ('every Regenerate removed (run-1 code)', 'doc.Regenerate()', 'None', 'regen-all'),
]


def run_mutations():
    """Each mutation of the real builder source must be caught. Returns the number NOT caught."""
    import builtins
    import contextlib
    import io
    original = open(os.path.join(HERE, 'build_clamp.py')).read()
    real_open = builtins.open
    missed = 0
    for label, old, new, spec in MUTATIONS:
        src = original
        if old is not None:
            if old not in original:
                print('  MUTATION TEXT NOT FOUND: %s' % label)
                missed += 1
                continue
            src = original.replace(old, new) if spec == 'regen-all' else original.replace(old, new, 1)
        saved = {}
        if isinstance(spec, dict):
            for k, val in spec.items():
                saved[k] = getattr(S, k)
                setattr(S, k, val)
        if spec in ('regen', 'regen-all'):
            Doc.strict_regen = True
        builtins.open = lambda path, *a, **k: io.StringIO(src) if str(path).endswith('build_clamp.py') else real_open(path, *a, **k)
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                code = main()
        except Exception as exc:          # the builder's own guard raising also counts as caught
            code, out = 1, io.StringIO('raised %s: %s' % (type(exc).__name__, exc))
        finally:
            builtins.open = real_open
            for k, val in saved.items():
                setattr(S, k, val)
            Doc.strict_regen = False
        caught = code != 0
        missed += 0 if caught else 1
        detail = [l.strip() for l in out.getvalue().splitlines() if 'FAIL ' in l or 'raised' in l][:1]
        print('  %-38s %s  %s' % (label, 'caught' if caught else 'NOT CAUGHT', (detail[0][:100] if detail else '')))
    return missed


if __name__ == '__main__':
    code = main()
    if '--mutations' in sys.argv:
        print('mutations:')
        missed = run_mutations()
        print('MUTATIONS: %d of %d caught' % (len(MUTATIONS) - missed, len(MUTATIONS)))
        code = code or (1 if missed else 0)
    sys.exit(code)
