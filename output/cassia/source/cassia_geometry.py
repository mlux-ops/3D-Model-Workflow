# -*- coding: utf-8 -*-
"""Geometry specification for the Alora Mood Cassia SF549315 semi-flush fixture.

Single source of truth for two consumers:
  * build_cassia.py      - IronPython 2.7 inside Revit 2025 (pyRevit), builds the RFA
  * preview_geometry.py  - CPython 3, offline mesh preview and gate dry-run
Pure Python, standard library only, Python 2.7 and 3 compatible.

Units are inches. Family-local frame: origin at the centre of the canopy's
mounting face, +Z pointing away from the host face (downward once the family is
hosted on a ceiling), arms at azimuth 0, 120 and 240 degrees about +Z.

Every revolved part is described by a closed profile in (r, a) coordinates:
r is the distance from the revolve axis (>= 0) and a is the position along it.
A profile item is either a point (r, a) - a straight edge to that point - or
('arc', (r_mid, a_mid), (r_end, a_end)) - a circular arc through the middle
point. The loop closes back to its first point with a straight edge.

Provenance of each value is stated beside it and summarised in INFERENCES.md:
PUBLISHED = Alora Mood spec sheet SF549315 (and the identical supplied drawing),
DRAWING   = measured on the supplied drawing, 22.03 px/in (7-5/8 in and Ø6 in),
RENDER    = measured on the supplied renders relative to the canopy,
INFERRED  = not visible or not measurable; chosen for plausibility.
"""
from __future__ import division
import math

# ---------------------------------------------------------------- published
OVERALL_DIAMETER = 17.75      # PUBLISHED  Ø17-3/4"
OVERALL_HEIGHT = 7.625        # PUBLISHED  7-5/8", ceiling to globe bottom
CANOPY_DIAMETER = 4.75        # PUBLISHED  Ø4-3/4"
CANOPY_HEIGHT = 0.875         # PUBLISHED  7/8"
GLOBE_DIAMETER = 6.0          # PUBLISHED  Ø6"

# Derived from published values only. The drawing itself places the globe
# centres at 5.945 in (globe-circle scale); printed dimensions govern.
GLOBE_RADIUS = GLOBE_DIAMETER / 2.0
GLOBE_CENTRE_RADIUS = OVERALL_DIAMETER / 2.0 - GLOBE_RADIUS      # 5.875
GLOBE_CENTRE_Z = OVERALL_HEIGHT - GLOBE_RADIUS                   # 4.625

# ---------------------------------------------------------------- measured
ARM_AZIMUTHS_DEG = (0.0, 120.0, 240.0)   # DRAWING plan: 119.7-120.3 deg spacing
ARM_ANGLE_DEG = 30.0          # DRAWING elevation: 29.9-30.8 deg below horizontal;
                              #   the arm axis passes through the globe centre (<1 px)
HUB_DIAMETER = 1.16           # DRAWING 1.18 elev / 1.235 plan; RENDER 1.12-1.16
HUB_HEIGHT = 1.18             # DRAWING 26 px below the canopy
ARM_DIAMETER = 0.50           # DRAWING 0.556-0.567 (line centres); RENDER 0.45-0.49
SCREW_AZIMUTHS_DEG = (90.0, 270.0)   # DRAWING/RENDER: one head faces the elevation
                                     #   viewer, 30 deg off an arm; pair INFERRED
SCREW_HEAD_DIAMETER = 0.22    # DRAWING 0.23, RENDER 0.23
SCREW_HEAD_HEIGHT = 0.07      # INFERRED dome height
SCREW_Z = 0.36                # DRAWING 42 %, RENDER 34 % of canopy height from ceiling

# Stations along each arm axis, measured from the globe centre toward the hub.
GLASS_CUT_A = 2.81            # DRAWING fitter inner face 2.82; glass opening plane
GLASS_WALL = 0.10             # INFERRED opal shell thickness
FLANGE_A = (2.81, 2.92)       # DRAWING/RENDER stepped fitter disk
FLANGE_RADIUS = 1.08          # DRAWING Ø2.06, RENDER Ø2.12-2.24; covers glass edge
DISK_A = (2.92, 3.04)         # DRAWING outer face 3.05
DISK_RADIUS = 0.93            # RENDER step ring ~0.87 of flange
COLLAR_A = (3.04, 3.44)       # RENDER sleeve where the arm enters the fitter
COLLAR_RADIUS = 0.31          # RENDER 1.17-1.24 x arm
ARM_START_A = 3.35            # arm ends inside the collar
SLEEVE_A = (1.45, 2.95)       # INFERRED candelabra socket cover (clear-glass SKU render)
SLEEVE_RADIUS = 0.37
LAMP_PROFILE = [(0.0, 1.50), (0.0, -1.05),                          # INFERRED E12 candle
                ('arc', (0.26, -0.55), (0.44, 0.15)),
                ('arc', (0.48, 0.70), (0.30, 1.30)), (0.30, 1.50)]

CANOPY_EDGE_ROUND = 0.04      # INFERRED; RENDER shows a crisp but softened edge
HUB_EDGE_ROUND = 0.03         # INFERRED

# Revit ShortCurveTolerance is 1/32 in (0.00260 ft); keep a margin above it.
MIN_EDGE_LENGTH = 0.035

THETA = math.radians(ARM_ANGLE_DEG)
ARM_HUB_Z = GLOBE_CENTRE_Z - GLOBE_CENTRE_RADIUS * math.tan(THETA)   # 1.2331
ARM_AXIS_LENGTH = GLOBE_CENTRE_RADIUS / math.cos(THETA)              # 6.7839

MATERIAL_PARAMETERS = {'metal': 'Metal Finish', 'glass': 'Glass Finish', 'lamp': 'Lamp Finish'}
SUBCATEGORIES = ('Canopy and Hub', 'Arms and Fitters', 'Glass Globes', 'Lamps and Sockets')

# Measurement tolerances used by the builder's gates and the offline dry-run.
DIM_TOL = 0.01
ANGLE_TOL_DEG = 0.25
HOSTED_TOL = 0.02


# ----------------------------------------------------------------- vectors
def _add(p, q):
    return (p[0] + q[0], p[1] + q[1], p[2] + q[2])


def _mul(p, s):
    return (p[0] * s, p[1] * s, p[2] * s)


def _unit(p):
    n = math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])
    return (p[0] / n, p[1] / n, p[2] / n)


def arm_frame(azimuth_deg):
    """Globe centre, unit axis toward the hub, outward radial and tangential unit
    vectors for the arm at this azimuth (family-local, inches)."""
    phi = math.radians(azimuth_deg)
    radial = (math.cos(phi), math.sin(phi), 0.0)
    tangential = (-math.sin(phi), math.cos(phi), 0.0)
    centre = (GLOBE_CENTRE_RADIUS * radial[0], GLOBE_CENTRE_RADIUS * radial[1], GLOBE_CENTRE_Z)
    # From the hub the arm runs outward and away from the ceiling (+Z).
    outward = _unit((math.cos(THETA) * radial[0], math.cos(THETA) * radial[1], math.sin(THETA)))
    to_hub = _mul(outward, -1.0)
    return centre, to_hub, radial, tangential


def point_on_axis(origin, axis, a):
    return _add(origin, _mul(axis, a))


# --------------------------------------------------------------- profiles
def _rounded_end(r, a0, a1, e):
    """Cylinder profile (r, a0..a1) whose far edge (at a1) carries a round e."""
    k = 1.0 - math.sqrt(0.5)
    return [(0.0, a0), (r, a0), (r, a1 - e), ('arc', (r - e * k, a1 - e * k), (r - e, a1)), (0.0, a1)]


def _cylinder(r, a0, a1):
    return [(0.0, a0), (r, a0), (r, a1), (0.0, a1)]


def _dome(radius, height, embed):
    """Domed screw head on a short embedded shank; arc centre lies on the axis."""
    c = (height * height - radius * radius) / (2.0 * height)
    rho = height - c
    # Angles are measured from the +a axis toward +r; the apex (0, height) is 0.
    mid = 0.5 * math.atan2(radius, -c)
    mid_pt = (rho * math.sin(mid), c + rho * math.cos(mid))
    return [(0.0, -embed), (radius, -embed), (radius, 0.0), ('arc', mid_pt, (0.0, height))]


def globe_profile():
    r_out = math.sqrt(GLOBE_RADIUS ** 2 - GLASS_CUT_A ** 2)
    inner = GLOBE_RADIUS - GLASS_WALL
    r_in = math.sqrt(inner ** 2 - GLASS_CUT_A ** 2)
    return [(r_in, GLASS_CUT_A), ('arc', (inner, 0.0), (0.0, -inner)), (0.0, -GLOBE_RADIUS),
            ('arc', (GLOBE_RADIUS, 0.0), (r_out, GLASS_CUT_A))]


def fitter_profile():
    return [(0.0, FLANGE_A[0]), (FLANGE_RADIUS, FLANGE_A[0]), (FLANGE_RADIUS, FLANGE_A[1]),
            (DISK_RADIUS, DISK_A[0]), (DISK_RADIUS, DISK_A[1]),
            (COLLAR_RADIUS, COLLAR_A[0]), (COLLAR_RADIUS, COLLAR_A[1]), (0.0, COLLAR_A[1])]


def parts():
    """Every solid in the family, in creation order."""
    out = []
    z = (0.0, 0.0, 1.0)
    out.append({'key': 'canopy', 'name': 'Canopy', 'origin': (0.0, 0.0, 0.0), 'axis': z,
                'profile': _rounded_end(CANOPY_DIAMETER / 2.0, 0.0, CANOPY_HEIGHT, CANOPY_EDGE_ROUND),
                'material': 'metal', 'subcategory': 'Canopy and Hub'})
    for i, psi in enumerate(SCREW_AZIMUTHS_DEG):
        d = (math.cos(math.radians(psi)), math.sin(math.radians(psi)), 0.0)
        origin = (d[0] * CANOPY_DIAMETER / 2.0, d[1] * CANOPY_DIAMETER / 2.0, SCREW_Z)
        out.append({'key': 'screw_%d' % i, 'name': 'Canopy screw %d' % (i + 1), 'origin': origin,
                    'axis': d, 'profile': _dome(SCREW_HEAD_DIAMETER / 2.0, SCREW_HEAD_HEIGHT, 0.04),
                    'material': 'metal', 'subcategory': 'Canopy and Hub'})
    out.append({'key': 'hub', 'name': 'Hub', 'origin': (0.0, 0.0, 0.0), 'axis': z,
                'profile': _rounded_end(HUB_DIAMETER / 2.0, CANOPY_HEIGHT, CANOPY_HEIGHT + HUB_HEIGHT,
                                        HUB_EDGE_ROUND),
                'material': 'metal', 'subcategory': 'Canopy and Hub'})
    for i, phi in enumerate(ARM_AZIMUTHS_DEG):
        c, u, radial, tangential = arm_frame(phi)
        common = {'origin': c, 'axis': u, 'azimuth_deg': phi, 'arm': i}
        for key, name, profile, material, sub in [
                ('arm', 'Arm', _cylinder(ARM_DIAMETER / 2.0, ARM_START_A, ARM_AXIS_LENGTH),
                 'metal', 'Arms and Fitters'),
                ('fitter', 'Stepped fitter', fitter_profile(), 'metal', 'Arms and Fitters'),
                ('globe', 'Opal globe', globe_profile(), 'glass', 'Glass Globes'),
                ('sleeve', 'Socket sleeve', _cylinder(SLEEVE_RADIUS, SLEEVE_A[0], SLEEVE_A[1]),
                 'metal', 'Lamps and Sockets'),
                ('lamp', 'Candle lamp', list(LAMP_PROFILE), 'lamp', 'Lamps and Sockets')]:
            part = dict(common)
            part.update({'key': '%s_%d' % (key, i), 'name': '%s %d' % (name, i + 1),
                         'profile': profile, 'material': material, 'subcategory': sub})
            out.append(part)
    return out


# ------------------------------------------------------ profile utilities
def circle_through(p0, pm, p1):
    """Centre and radius of the circle through three 2-D points."""
    ax, ay = p0
    bx, by = pm
    cx, cy = p1
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        raise ValueError('collinear arc points %r %r %r' % (p0, pm, p1))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def _arc_angles(p0, pm, p1):
    (ux, uy), rho = circle_through(p0, pm, p1)
    t0 = math.atan2(p0[1] - uy, p0[0] - ux)
    tm = math.atan2(pm[1] - uy, pm[0] - ux)
    t1 = math.atan2(p1[1] - uy, p1[0] - ux)

    def ccw(a, b):
        return (b - a) % (2.0 * math.pi)
    if ccw(t0, tm) <= ccw(t0, t1):      # counter-clockwise from p0 through pm to p1
        return (ux, uy), rho, t0, ccw(t0, t1)
    return (ux, uy), rho, t0, -ccw(t1, t0)


def segments(profile):
    """Expand a profile into ('line', p0, p1) and ('arc', p0, pm, p1) segments."""
    out = []
    current = profile[0]
    for item in profile[1:]:
        if len(item) == 3 and item[0] == 'arc':
            out.append(('arc', current, item[1], item[2]))
            current = item[2]
        else:
            out.append(('line', current, item))
            current = item
    if (abs(current[0] - profile[0][0]) > 1e-12) or (abs(current[1] - profile[0][1]) > 1e-12):
        out.append(('line', current, profile[0]))
    return out


def segment_length(seg):
    if seg[0] == 'line':
        return math.hypot(seg[2][0] - seg[1][0], seg[2][1] - seg[1][1])
    _, rho, _, sweep = _arc_angles(seg[1], seg[2], seg[3])
    return abs(rho * sweep)


def sample_profile(profile, step_deg=3.0):
    """Closed polyline through the profile (arcs sampled every step_deg)."""
    pts = []
    for seg in segments(profile):
        if seg[0] == 'line':
            pts.append(seg[1])
        else:
            (ux, uy), rho, t0, sweep = _arc_angles(seg[1], seg[2], seg[3])
            n = max(2, int(math.ceil(abs(math.degrees(sweep)) / step_deg)))
            for i in range(n):
                t = t0 + sweep * i / float(n)
                pts.append((ux + rho * math.cos(t), uy + rho * math.sin(t)))
    return pts


def signed_area(profile):
    """Shoelace area of the sampled profile in (r, a); positive = counter-clockwise."""
    pts = sample_profile(profile, 1.0)
    area = 0.0
    for i in range(len(pts)):
        r0, a0 = pts[i]
        r1, a1 = pts[(i + 1) % len(pts)]
        area += r0 * a1 - r1 * a0
    return 0.5 * area


def check_profiles():
    """Pre-flight checks the Revit build depends on. Returns a list of problems."""
    problems = []
    if not (ARM_START_A > GLASS_CUT_A and FLANGE_A[0] >= GLASS_CUT_A and SLEEVE_A[1] > GLASS_CUT_A):
        problems.append('arm, fitter or sleeve stations do not clear the glass opening plane')
    if FLANGE_RADIUS <= math.sqrt(GLOBE_RADIUS ** 2 - GLASS_CUT_A ** 2):
        problems.append('fitter flange does not cover the glass opening')
    for part in parts():
        prof = part['profile']
        if signed_area(prof) <= 0:
            problems.append('%s: profile is not counter-clockwise in (r, a)' % part['key'])
        for seg in segments(prof):
            length = segment_length(seg)
            if length < MIN_EDGE_LENGTH:
                problems.append('%s: edge %s of %.4f in is below %.3f in'
                                % (part['key'], seg[0], length, MIN_EDGE_LENGTH))
        for r, a in sample_profile(prof, 1.0):
            if r < -1e-9:
                problems.append('%s: profile crosses the revolve axis (r=%.4f at a=%.4f)'
                                % (part['key'], r, a))
                break
    return problems


# ------------------------------------------------------- gate definitions
def measurement_rays():
    """Ray probes shared by the native gates and the offline dry-run.

    Each ray names the part it is fired at, two end points in family-local
    inches and the reduction applied to the solid segments it returns.
    """
    rays = []
    add = rays.append
    add({'key': 'canopy_diameter', 'part': 'canopy', 'p0': (-4.0, 0.0, CANOPY_HEIGHT / 2.0),
         'p1': (4.0, 0.0, CANOPY_HEIGHT / 2.0), 'reduce': 'total_length',
         'target': CANOPY_DIAMETER, 'tol': DIM_TOL, 'source': 'PUBLISHED'})
    add({'key': 'canopy_height', 'part': 'canopy', 'p0': (1.3, 0.4, -1.0), 'p1': (1.3, 0.4, 2.0),
         'reduce': 'total_length', 'target': CANOPY_HEIGHT, 'tol': DIM_TOL, 'source': 'PUBLISHED'})
    mid_hub = CANOPY_HEIGHT + HUB_HEIGHT / 2.0
    add({'key': 'hub_diameter', 'part': 'hub', 'p0': (0.0, -2.0, mid_hub), 'p1': (0.0, 2.0, mid_hub),
         'reduce': 'total_length', 'target': HUB_DIAMETER, 'tol': DIM_TOL, 'source': 'DRAWING'})
    add({'key': 'hub_height', 'part': 'hub', 'p0': (0.25, 0.1, -1.0), 'p1': (0.25, 0.1, 4.0),
         'reduce': 'total_length', 'target': HUB_HEIGHT, 'tol': DIM_TOL, 'source': 'DRAWING'})
    for i, phi in enumerate(ARM_AZIMUTHS_DEG):
        c, u, radial, t = arm_frame(phi)
        add({'key': 'globe_%d_overall_height' % i, 'part': 'globe_%d' % i,
             'p0': (c[0], c[1], -1.0), 'p1': (c[0], c[1], OVERALL_HEIGHT + 2.0),
             'reduce': 'max_z', 'target': OVERALL_HEIGHT, 'tol': DIM_TOL, 'source': 'PUBLISHED'})
        add({'key': 'globe_%d_vertical_diameter' % i, 'part': 'globe_%d' % i,
             'p0': (c[0], c[1], -1.0), 'p1': (c[0], c[1], OVERALL_HEIGHT + 2.0),
             'reduce': 'span', 'target': GLOBE_DIAMETER, 'tol': DIM_TOL, 'source': 'PUBLISHED'})
        add({'key': 'globe_%d_wall' % i, 'part': 'globe_%d' % i,
             'p0': (c[0], c[1], -1.0), 'p1': (c[0], c[1], OVERALL_HEIGHT + 2.0),
             'reduce': 'max_segment', 'target': GLASS_WALL, 'tol': DIM_TOL, 'source': 'INFERRED'})
        far = OVERALL_DIAMETER / 2.0 + 2.0
        add({'key': 'globe_%d_outer_radius' % i, 'part': 'globe_%d' % i,
             'p0': (0.0, 0.0, GLOBE_CENTRE_Z), 'p1': (radial[0] * far, radial[1] * far, GLOBE_CENTRE_Z),
             'reduce': 'max_radial', 'target': OVERALL_DIAMETER / 2.0, 'tol': DIM_TOL, 'source': 'PUBLISHED'})
        add({'key': 'globe_%d_centre_radius' % i, 'part': 'globe_%d' % i,
             'p0': (0.0, 0.0, GLOBE_CENTRE_Z), 'p1': (radial[0] * far, radial[1] * far, GLOBE_CENTRE_Z),
             'reduce': 'mid_radial', 'target': GLOBE_CENTRE_RADIUS, 'tol': DIM_TOL, 'source': 'PUBLISHED'})
        add({'key': 'globe_%d_tangential_diameter' % i, 'part': 'globe_%d' % i,
             'p0': _add(c, _mul(t, -5.0)), 'p1': _add(c, _mul(t, 5.0)),
             'reduce': 'span', 'target': GLOBE_DIAMETER, 'tol': DIM_TOL, 'source': 'PUBLISHED'})
        a_mid = 0.5 * (ARM_START_A + ARM_AXIS_LENGTH)
        m = point_on_axis(c, u, a_mid)
        add({'key': 'arm_%d_diameter' % i, 'part': 'arm_%d' % i,
             'p0': _add(m, _mul(t, -1.0)), 'p1': _add(m, _mul(t, 1.0)),
             'reduce': 'total_length', 'target': ARM_DIAMETER, 'tol': DIM_TOL, 'source': 'DRAWING'})
        for j, rr in enumerate((1.5, 2.5)):
            add({'key': 'arm_%d_section_%d' % (i, j), 'part': 'arm_%d' % i,
                 'p0': (radial[0] * rr, radial[1] * rr, -1.0), 'p1': (radial[0] * rr, radial[1] * rr, 6.0),
                 'reduce': 'mid_z', 'target': ARM_HUB_Z + rr * math.tan(THETA), 'tol': DIM_TOL,
                 'source': 'DRAWING', 'radius': rr})
        f = point_on_axis(c, u, 0.5 * (FLANGE_A[0] + FLANGE_A[1]))
        add({'key': 'fitter_%d_flange_diameter' % i, 'part': 'fitter_%d' % i,
             'p0': _add(f, _mul(t, -2.0)), 'p1': _add(f, _mul(t, 2.0)),
             'reduce': 'total_length', 'target': 2.0 * FLANGE_RADIUS, 'tol': DIM_TOL, 'source': 'DRAWING'})
        g = point_on_axis(c, u, GLASS_CUT_A - 0.002)
        add({'key': 'globe_%d_opening_radius' % i, 'part': 'globe_%d' % i,
             'p0': g, 'p1': _add(g, _mul(t, 2.0)), 'reduce': 'max_distance_from_p0',
             'target': math.sqrt(GLOBE_RADIUS ** 2 - (GLASS_CUT_A - 0.002) ** 2), 'tol': DIM_TOL,
             'source': 'DERIVED'})
    return rays


CLEARANCE_STATIONS = (-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 2.75)
MIN_INTERNAL_CLEARANCE = 0.05


def clearance_rays():
    """Rays from each globe axis outward (tangential) at stations along the axis.

    At each station the glass inner surface must lie outside the lamp and the
    socket sleeve by at least MIN_INTERNAL_CLEARANCE.
    """
    out = []
    for i, phi in enumerate(ARM_AZIMUTHS_DEG):
        c, u, radial, t = arm_frame(phi)
        for a in CLEARANCE_STATIONS:
            p0 = point_on_axis(c, u, a)
            out.append({'key': 'clearance_%d_a%+.2f' % (i, a), 'arm': i, 'station_in': a,
                        'p0': p0, 'p1': _add(p0, _mul(t, GLOBE_RADIUS + 0.2)),
                        'glass': 'globe_%d' % i, 'inside': ['lamp_%d' % i, 'sleeve_%d' % i]})
    return out


def clearance_from_segments(p0, glass_segs, inside_segs):
    """Glass inner radius minus the outermost inside-part radius along one ray."""
    def dist(p):
        return math.sqrt(sum((p[k] - p0[k]) ** 2 for k in range(3)))
    if not glass_segs:
        return None, None, None
    glass_inner = min(min(dist(a), dist(b)) for a, b in glass_segs)
    inner = [max(dist(a), dist(b)) for a, b in inside_segs]
    outer_part = max(inner) if inner else 0.0
    return glass_inner - outer_part, glass_inner, outer_part


def expected_solids_per_material():
    counts = {}
    for p in parts():
        counts[p['material']] = counts.get(p['material'], 0) + 1
    return counts


def reduce_segments(ray, segs):
    """Reduce solid segments [(p_from, p_to), ...] (inches) to one value."""
    if not segs:
        return None
    kind = ray['reduce']
    p0 = ray['p0']

    def dist(p, q):
        return math.sqrt(sum((p[k] - q[k]) ** 2 for k in range(3)))

    def radial(p):
        return math.hypot(p[0], p[1])
    ends = [p for s in segs for p in s]
    if kind == 'total_length':
        return sum(dist(a, b) for a, b in segs)
    if kind == 'max_segment':
        return max(dist(a, b) for a, b in segs)
    if kind == 'span':
        ds = [dist(p0, p) for p in ends]
        return max(ds) - min(ds)
    if kind == 'max_z':
        return max(p[2] for p in ends)
    if kind == 'mid_z':
        zs = [p[2] for p in ends]
        return 0.5 * (max(zs) + min(zs))
    if kind == 'max_radial':
        return max(radial(p) for p in ends)
    if kind == 'mid_radial':
        rs = [radial(p) for p in ends]
        return 0.5 * (max(rs) + min(rs))
    if kind == 'max_distance_from_p0':
        return max(dist(p0, p) for p in ends)
    raise ValueError('unknown reduction ' + kind)


def arm_angle_from_sections(values):
    """Arm slope in degrees from the two vertical section midpoints of one arm."""
    (r1, z1), (r2, z2) = values
    return math.degrees(math.atan2(z2 - z1, r2 - r1))


def summary():
    return {
        'overall_diameter_in': OVERALL_DIAMETER, 'overall_height_in': OVERALL_HEIGHT,
        'canopy_in': [CANOPY_DIAMETER, CANOPY_HEIGHT], 'globe_diameter_in': GLOBE_DIAMETER,
        'globe_centre_radius_in': GLOBE_CENTRE_RADIUS, 'globe_centre_z_in': GLOBE_CENTRE_Z,
        'arm_angle_deg': ARM_ANGLE_DEG, 'arm_hub_axis_z_in': ARM_HUB_Z,
        'arm_axis_length_in': ARM_AXIS_LENGTH, 'hub_in': [HUB_DIAMETER, HUB_HEIGHT],
        'arm_diameter_in': ARM_DIAMETER, 'fitter_flange_diameter_in': 2.0 * FLANGE_RADIUS,
        'glass_wall_in': GLASS_WALL, 'glass_cut_station_in': GLASS_CUT_A,
    }
