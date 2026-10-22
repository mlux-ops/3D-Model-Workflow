# -*- coding: utf-8 -*-
"""Miele KM 3054-1 gas cooktop: pure-stdlib geometry specification.

Shared by build_km3054.py (IronPython 2.7 inside Revit), verify_km3054.py (CPython)
and the offline sanity check (`python km3054_geometry.py`). Python 2.7 and 3 compatible.

Units: every value here is MILLIMETRES; inches() converts for the Revit builder.
Family frame: origin at the plan centre of the top plate, on the countertop surface
(the host face). +X runs left to right seen from the front, +Y runs from the front edge
to the rear edge, +Z follows the host face normal (up, out of the countertop).

Provenance tags (SKILL.md "Before touching geometry", item 4):
  PUBLISHED  Miele product page / product sheet FS_11766750 (printed value)
  DRAWING    printed value on installation drawing 20000085158 / manual page 45
  PHOTO      measured on the orthographic top view 20000084693 (2775 px = 942 mm,
             1550 px = 526 mm; 0.33946 mm/px both axes)
  INFERRED   not published and not measurable; see INFERENCES.md
"""
import math

MM_PER_IN = 25.4
MIN_EDGE_IN = 0.035          # repo floor; Revit ShortCurveTolerance is 1/32 in
DIM_TOL_IN = 0.025           # acceptance tolerance against published values

PROV = {}


def spec(name, value, provenance, note):
    PROV[name] = {'value_mm': value, 'provenance': provenance, 'note': note}
    return value


# ---------------------------------------------------------------- published envelope
WIDTH = spec('WIDTH', 942.0, 'PUBLISHED', 'Width 37 1/8 (942) in (mm); drawing 942')
DEPTH = spec('DEPTH', 526.0, 'PUBLISHED', 'Depth 20 3/4 (526); drawing 526')
OVERALL_HEIGHT = spec('OVERALL_HEIGHT', 53.0, 'PUBLISHED',
                      'Height 2 1/8 (53); drawing 7 above + 46 below the countertop')
ABOVE_COUNTER = spec('ABOVE_COUNTER', 7.0, 'DRAWING', 'drawing: 7 mm above the countertop surface')
CASING_DEPTH = spec('CASING_DEPTH', 46.0, 'DRAWING', 'drawing item 2 "Casing depth" 46 mm below the countertop')
BUILT_IN_HEIGHT = spec('BUILT_IN_HEIGHT', 78.0, 'PUBLISHED',
                       'Built-in height with mains connection box 3 1/8 (78), measured from the top')
CUTOUT_W = spec('CUTOUT_W', 916.0, 'PUBLISHED', 'cut-out width 36 1/8 (916) +1')
CUTOUT_D_MIN = spec('CUTOUT_D_MIN', 490.0, 'DRAWING', 'drawing cut-out depth 490-500')
CUTOUT_D_MAX = spec('CUTOUT_D_MAX', 500.0, 'PUBLISHED', 'cut-out depth 19 3/4 (500)')

# ---------------------------------------------------------------- top plate and frame
FRAME_BAND = spec('FRAME_BAND', 7.5, 'PHOTO', 'stainless edge band 22 px left/right, 24 px top')
TOP_Z = ABOVE_COUNTER

# ---------------------------------------------------------------- casing (below counter)
CASING_INSET_X = spec('CASING_INSET_X', 14.0, 'DRAWING', 'drawing "14" casing inset each side')
CASING_INSET_FRONT = spec('CASING_INSET_FRONT', 16.0, 'DRAWING', 'drawing "16" casing inset at the front')
CASING_D = spec('CASING_D', 490.0, 'INFERRED', 'casing depth not printed; set to the minimum cut-out depth')
CASING_W = WIDTH - 2 * CASING_INSET_X
EHOUSING = {'x0': spec('EH_X0', 379.0, 'DRAWING', 'electronics housing 379 from the left edge') - WIDTH / 2,
            'len_x': spec('EH_LX', 207.0, 'INFERRED', 'drawing value 207 read as the housing length'),
            'y0_from_front': spec('EH_Y0', 226.0, 'INFERRED', 'drawing value 226 read as the front offset'),
            'len_y': spec('EH_LY', 86.0, 'DRAWING', 'drawing "86" housing width')}
GAS_STUB = {'x': WIDTH / 2 - 86.0, 'y': DEPTH / 2 - 61.0,
            'r': spec('GAS_R', 10.5, 'PUBLISHED', 'R 1/2 in (ISO 7-1) gas connection, outside diameter ~21 mm'),
            'bottom': spec('GAS_BOTTOM', 71.0, 'DRAWING', 'drawing "71" at the gas connection, read from the top')}

# ---------------------------------------------------------------- knobs
KNOB_R = spec('KNOB_R', 18.35, 'PHOTO', 'four knobs 36.7 mm wide on the top view')
KNOB_Y = spec('KNOB_Y', DEPTH / 2 - 479.0, 'PHOTO', 'knob centres 479 mm from the rear edge')
KNOB_XS = [spec('KNOB_X_WOK', 236.5 - WIDTH / 2, 'PHOTO', 'wok knob under the wok burner'),
           spec('KNOB_X_1', 525.5 - WIDTH / 2, 'PHOTO', 'knob group, 60 mm pitch'),
           spec('KNOB_X_2', 586.2 - WIDTH / 2, 'PHOTO', ''),
           spec('KNOB_X_3', 646.3 - WIDTH / 2, 'PHOTO', ''),
           spec('KNOB_X_4', 706.6 - WIDTH / 2, 'PHOTO', '')]
KNOB_SKIRT_TOP = spec('KNOB_SKIRT_TOP', TOP_Z + 15.0, 'INFERRED', 'knob body 15 mm tall')
KNOB_TOP = spec('KNOB_TOP', TOP_Z + 23.0, 'INFERRED', 'grip fin 8 mm above the body')
KNOB_FIN_W = spec('KNOB_FIN_W', 10.0, 'PHOTO', 'centre grip stripe ~30 px')
KNOB_FIN_L = 2 * KNOB_R - 3.0

# ---------------------------------------------------------------- burners
# (key, label, centre x, centre y, cap r, head r, bowl r) in the family frame.
BURNERS = [
    ('wok', 'Dual wok burner (left centre)', 153.0 - WIDTH / 2, DEPTH / 2 - 196.0, 22.0, 33.0, 82.0),
    ('economy', 'Economy burner (rear centre)', 487.8 - WIDTH / 2, DEPTH / 2 - 124.0, 28.5, 31.5, 52.0),
    ('normal_rear', 'Standard burner (rear right)', 749.6 - WIDTH / 2, DEPTH / 2 - 124.0, 37.0, 40.0, 58.0),
    ('power', 'High-speed burner (front centre)', 422.0 - WIDTH / 2, DEPTH / 2 - 349.0, 54.5, 57.5, 64.0),
    ('normal_front', 'Standard burner (front right)', 815.0 - WIDTH / 2, DEPTH / 2 - 349.0, 35.0, 38.0, 58.0),
]
for _b in BURNERS:
    spec('BURNER_' + _b[0], [_b[2], _b[3], _b[4]], 'PHOTO',
         _b[1] + ': centre and cap radius from the top view; head and bowl radii INFERRED')
BOWL_TOP = TOP_Z + 4.0       # INFERRED
HEAD_TOP = TOP_Z + 12.0      # INFERRED
CAP_TOP = TOP_Z + 17.0       # INFERRED
WOK_OUTER_HEAD = (36.0, 72.0)  # INFERRED radii of the outer flame ring
WOK_OUTER_CAP = (38.0, 70.0)

# ---------------------------------------------------------------- grates
GRATE_T = spec('GRATE_T', 8.0, 'PHOTO', 'cast bars 22-25 px wide')
GRATE_TOP = spec('GRATE_TOP', TOP_Z + 30.0, 'INFERRED', 'pan support plane 30 mm above the glass')
RING_TOP = TOP_Z + 20.0      # INFERRED
FINGER_BOTTOM = RING_TOP - 1.0
BAR_TOP_OFF = spec('BAR_TOP_OFF', 78.0, 'PHOTO', 'outer bars 78 mm behind the burner centre')
BAR_BOT_OFF = spec('BAR_BOT_OFF', 72.0, 'PHOTO', 'outer bars 72 mm in front of the burner centre')
STUB_TOP = 100.0             # PHOTO, vertical finger reach behind the centre
STUB_BOT = 90.0              # PHOTO
# (key, burner key, x min, x max, ring outer radius) - four right-hand grates, PHOTO.
GRATES = [
    ('grate_rear_left', 'economy', 322.0 - WIDTH / 2, 611.0 - WIDTH / 2, 74.0),
    ('grate_rear_right', 'normal_rear', 622.0 - WIDTH / 2, 912.0 - WIDTH / 2, 74.0),
    ('grate_front_left', 'power', 322.0 - WIDTH / 2, 614.0 - WIDTH / 2, 76.0),
    ('grate_front_right', 'normal_front', 619.0 - WIDTH / 2, 912.0 - WIDTH / 2, 74.0),
]
WOK_RING_R = spec('WOK_RING_R', 118.0, 'PHOTO', 'wok support ring outer diameter 236 mm')
WOK_ARM_X = spec('WOK_ARM_X', 124.0, 'PHOTO', 'wok grate arm reach left/right')
WOK_ARM_Y = spec('WOK_ARM_Y', 151.0, 'PHOTO', 'wok grate arm reach front/back')

MATERIAL_PARAMETERS = {
    'top': 'Top Finish', 'frame': 'Frame Finish', 'grate': 'Grate Finish',
    'burner': 'Burner Finish', 'ring': 'Burner Ring Finish', 'knob': 'Knob Finish',
    'housing': 'Housing Finish',
}
SUBCATEGORIES = {
    'top': 'Cooktop Glass', 'frame': 'Cooktop Frame', 'grate': 'Grates', 'burner': 'Burner Caps',
    'ring': 'Burner Heads', 'knob': 'Control Knobs', 'housing': 'Housing',
}


def burner(key):
    for b in BURNERS:
        if b[0] == key:
            return b
    raise KeyError(key)


# ---------------------------------------------------------------- profile helpers
def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def segment_poly(p0, p1, half):
    """Rectangle of half-width `half` around the segment p0->p1, CCW."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n * half, dx / n * half
    pts = [(p0[0] - nx, p0[1] - ny), (p1[0] - nx, p1[1] - ny), (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)]
    return ccw(pts)


def polyline_poly(points, half):
    """Closed outline of a 3-point polyline with mitred joint, CCW."""
    a, b, c = points

    def unit(p, q):
        d = math.hypot(q[0] - p[0], q[1] - p[1])
        return ((q[0] - p[0]) / d, (q[1] - p[1]) / d)

    u1, u2 = unit(a, b), unit(b, c)
    n1, n2 = (-u1[1], u1[0]), (-u2[1], u2[0])
    m = (n1[0] + n2[0], n1[1] + n2[1])
    ml = math.hypot(*m)
    m = (m[0] / ml, m[1] / ml)
    k = half / (m[0] * n1[0] + m[1] * n1[1])
    left = [(a[0] + n1[0] * half, a[1] + n1[1] * half), (b[0] + m[0] * k, b[1] + m[1] * k),
            (c[0] + n2[0] * half, c[1] + n2[1] * half)]
    right = [(a[0] - n1[0] * half, a[1] - n1[1] * half), (b[0] - m[0] * k, b[1] - m[1] * k),
             (c[0] - n2[0] * half, c[1] - n2[1] * half)]
    return ccw(left + list(reversed(right)))


def signed_area(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                     for i in range(len(pts)))


def ccw(pts):
    return pts if signed_area(pts) > 0 else list(reversed(pts))


def cyl_profile(r, z0, z1):
    return [(0.0, z0), (r, z0), (r, z1), (0.0, z1)]


def tube_profile(ri, ro, z0, z1):
    return [(ri, z0), (ro, z0), (ro, z1), (ri, z1)]


# ---------------------------------------------------------------- parts
def _prism(key, mat, loops, z0, z1, group=None):
    return {'key': key, 'kind': 'prism', 'material': mat, 'loops': loops, 'z0': z0, 'z1': z1,
            'group': group or key}


def _revolve(key, mat, cx, cy, profile, group=None):
    return {'key': key, 'kind': 'revolve', 'material': mat, 'centre': (cx, cy), 'profile': profile,
            'group': group or key}


def _grate_parts(gkey, bkey, xmin, xmax, rout):
    b = burner(bkey)
    cx, cy, rcap = b[2], b[3], b[4]
    h = GRATE_T / 2.0
    rin = rout - GRATE_T
    emb = rout - h               # bar ends sit mid-band in the ring
    z0, z1 = TOP_Z, GRATE_TOP
    parts = [_revolve(gkey + '_ring', 'grate', cx, cy, tube_profile(rin, rout, z0, RING_TOP), gkey)]
    tip = rcap + 6.0
    for i, (ux, uy) in enumerate([(1, 0), (0, 1), (-1, 0), (0, -1)]):
        p0 = (cx + ux * tip, cy + uy * tip)
        p1 = (cx + ux * (rout - 1.0), cy + uy * (rout - 1.0))
        parts.append(_prism('%s_finger_%d' % (gkey, i), 'grate', [segment_poly(p0, p1, h)],
                            FINGER_BOTTOM, z1, gkey))
    parts.append(_prism(gkey + '_mid_l', 'grate', [segment_poly((xmin, cy), (cx - emb, cy), h)], z0, z1, gkey))
    parts.append(_prism(gkey + '_mid_r', 'grate', [segment_poly((cx + emb, cy), (xmax, cy), h)], z0, z1, gkey))
    c45 = math.sqrt(0.5)
    for side, sx in (('l', -1), ('r', 1)):
        for edge, off in (('top', BAR_TOP_OFF), ('bot', -BAR_BOT_OFF)):
            sy = 1 if off > 0 else -1
            corner = (cx + sx * abs(off), cy + off)
            end = (xmin, cy + off) if sx < 0 else (xmax, cy + off)
            ring_pt = (cx + sx * emb * c45, cy + sy * emb * c45)
            parts.append(_prism('%s_%s_%s' % (gkey, edge, side), 'grate',
                                [polyline_poly([end, corner, ring_pt], h)], z0, z1, gkey))
    parts.append(_prism(gkey + '_stub_top', 'grate', [segment_poly((cx, cy + emb), (cx, cy + STUB_TOP), h)], z0, z1, gkey))
    parts.append(_prism(gkey + '_stub_bot', 'grate', [segment_poly((cx, cy - emb), (cx, cy - STUB_BOT), h)], z0, z1, gkey))
    return parts


def _wok_grate_parts():
    b = burner('wok')
    cx, cy = b[2], b[3]
    h = GRATE_T / 2.0
    rout, rin = WOK_RING_R, WOK_RING_R - GRATE_T
    g = 'grate_wok'
    parts = [_revolve(g + '_ring', 'grate', cx, cy, tube_profile(rin, rout, TOP_Z, RING_TOP), g)]
    for i, (ux, uy, reach) in enumerate([(1, 0, WOK_ARM_X), (0, 1, WOK_ARM_Y), (-1, 0, WOK_ARM_X), (0, -1, WOK_ARM_Y)]):
        inner0 = (cx + ux * 26.0, cy + uy * 26.0)
        inner1 = (cx + ux * (rout - h), cy + uy * (rout - h))
        outer0 = (cx + ux * (rin + h), cy + uy * (rin + h))
        outer1 = (cx + ux * reach, cy + uy * reach)
        parts.append(_prism('%s_arm_in_%d' % (g, i), 'grate', [segment_poly(inner0, inner1, h)], FINGER_BOTTOM, GRATE_TOP, g))
        parts.append(_prism('%s_arm_out_%d' % (g, i), 'grate', [segment_poly(outer0, outer1, h)], TOP_Z, GRATE_TOP, g))
    return parts


def _burner_parts(b):
    key, _, cx, cy, rcap, rhead, rbowl = b
    out = [_revolve(key + '_bowl', 'burner', cx, cy, cyl_profile(rbowl, TOP_Z, BOWL_TOP))]
    if key == 'wok':
        out.append(_revolve(key + '_outer_head', 'ring', cx, cy,
                            tube_profile(WOK_OUTER_HEAD[0], WOK_OUTER_HEAD[1], BOWL_TOP, BOWL_TOP + 5.0)))
        out.append(_revolve(key + '_outer_cap', 'burner', cx, cy,
                            tube_profile(WOK_OUTER_CAP[0], WOK_OUTER_CAP[1], BOWL_TOP + 5.0, BOWL_TOP + 9.0)))
    out.append(_revolve(key + '_head', 'ring', cx, cy, cyl_profile(rhead, BOWL_TOP, HEAD_TOP)))
    out.append(_revolve(key + '_cap', 'burner', cx, cy, cyl_profile(rcap, HEAD_TOP, CAP_TOP)))
    return out


def parts():
    hw, hd = WIDTH / 2.0, DEPTH / 2.0
    ib = FRAME_BAND
    out = [
        _prism('frame', 'frame', [rect(-hw, -hd, hw, hd), list(reversed(rect(-hw + ib, -hd + ib, hw - ib, hd - ib)))],
               0.0, TOP_Z),
        _prism('glass', 'top', [rect(-hw + ib, -hd + ib, hw - ib, hd - ib)], 0.0, TOP_Z),
        _prism('casing', 'housing', [rect(-CASING_W / 2, -hd + CASING_INSET_FRONT,
                                          CASING_W / 2, -hd + CASING_INSET_FRONT + CASING_D)], -CASING_DEPTH, 0.0),
        _prism('electronics_housing', 'housing',
               [rect(EHOUSING['x0'], -hd + EHOUSING['y0_from_front'], EHOUSING['x0'] + EHOUSING['len_x'],
                     -hd + EHOUSING['y0_from_front'] + EHOUSING['len_y'])],
               TOP_Z - BUILT_IN_HEIGHT, -CASING_DEPTH),
        _revolve('gas_connection', 'housing', GAS_STUB['x'], GAS_STUB['y'],
                 cyl_profile(GAS_STUB['r'], TOP_Z - GAS_STUB['bottom'], -CASING_DEPTH)),
    ]
    for i, x in enumerate(KNOB_XS):
        out.append(_revolve('knob_%d_body' % i, 'knob', x, KNOB_Y, cyl_profile(KNOB_R, TOP_Z, KNOB_SKIRT_TOP), 'knob_%d' % i))
        out.append(_prism('knob_%d_fin' % i, 'knob',
                          [rect(x - KNOB_FIN_W / 2, KNOB_Y - KNOB_FIN_L / 2, x + KNOB_FIN_W / 2, KNOB_Y + KNOB_FIN_L / 2)],
                          KNOB_SKIRT_TOP - 1.0, KNOB_TOP, 'knob_%d' % i))
    for b in BURNERS:
        out.extend(_burner_parts(b))
    for g in GRATES:
        out.extend(_grate_parts(*g))
    out.extend(_wok_grate_parts())
    return out


def groups():
    """Ordered group key -> (material, [part keys]). One FreeFormElement per group."""
    order, table = [], {}
    for p in parts():
        if p['group'] not in table:
            order.append(p['group'])
            table[p['group']] = (p['material'], [])
        table[p['group']][1].append(p['key'])
    return [(g, table[g][0], table[g][1]) for g in order]


def expected_groups_per_material():
    out = {}
    for _, mat, _ in groups():
        out[mat] = out.get(mat, 0) + 1
    return out


# ---------------------------------------------------------------- measurement rays
def measurement_rays():
    """Rays in mm. measure: span | first_len | count | end | start | none (see measure())."""
    hw, hd = WIDTH / 2.0, DEPTH / 2.0
    tol = DIM_TOL_IN * MM_PER_IN
    corner = (-hw + 41.0, -hd + 23.0)            # clear of every part above the glass
    eh_c = (EHOUSING['x0'] + EHOUSING['len_x'] / 2.0, -hd + EHOUSING['y0_from_front'] + EHOUSING['len_y'] / 2.0)
    rays = [
        dict(key='overall_width', a=(-hw - 50, 0, 3.5), b=(hw + 50, 0, 3.5), measure='span', target=WIDTH, prov='PUBLISHED'),
        dict(key='overall_depth', a=(-hw + 31, -hd - 50, 3.5), b=(-hw + 31, hd + 50, 3.5), measure='span', target=DEPTH, prov='PUBLISHED'),
        dict(key='frame_band', a=(-hw - 50, 0, 3.5), b=(hw + 50, 0, 3.5), measure='first_len', target=FRAME_BAND, prov='PHOTO', merge=False),
        dict(key='top_above_counter', a=(corner[0], corner[1], -200), b=(corner[0], corner[1], 200), measure='end', axis=2, target=TOP_Z, prov='DRAWING'),
        dict(key='overall_height', a=(corner[0], corner[1], -200), b=(corner[0], corner[1], 200), measure='span', target=OVERALL_HEIGHT, prov='PUBLISHED'),
        dict(key='casing_depth_below_counter', a=(corner[0], corner[1], -200), b=(corner[0], corner[1], 200), measure='start', axis=2, target=-CASING_DEPTH, prov='DRAWING'),
        dict(key='built_in_height_with_box', a=(eh_c[0], eh_c[1], -200), b=(eh_c[0], eh_c[1], 200), measure='span', target=BUILT_IN_HEIGHT, prov='PUBLISHED'),
        dict(key='casing_width', a=(-hw - 50, -100, -30), b=(hw + 50, -100, -30), measure='span', target=CASING_W, prov='DRAWING'),
        dict(key='casing_plan_depth', a=(-300, -hd - 50, -30), b=(-300, hd + 50, -30), measure='span', target=CASING_D, prov='INFERRED'),
        dict(key='knob_count', a=(-hw, KNOB_Y, TOP_Z + 6), b=(hw, KNOB_Y, TOP_Z + 6), measure='count', target=len(KNOB_XS), prov='PHOTO', tol=0),
    ]
    for i, x in enumerate(KNOB_XS):
        rays.append(dict(key='knob_%d_diameter' % i, a=(x - 40, KNOB_Y + 6, TOP_Z + 6), b=(x + 40, KNOB_Y + 6, TOP_Z + 6),
                         measure='span', target=2 * math.sqrt(KNOB_R ** 2 - 36.0), prov='PHOTO',
                         note='chord 6 mm off the centre line, clear of the fin'))
    for b in BURNERS:
        key, cx, cy, rcap = b[0], b[2], b[3], b[4]
        zc = (HEAD_TOP + CAP_TOP) / 2.0
        rays.append(dict(key='cap_%s_diameter' % key, a=(cx - rcap - 3, cy + 6, zc), b=(cx + rcap + 3, cy + 6, zc),
                         measure='span', target=2 * math.sqrt(rcap ** 2 - 36.0), prov='PHOTO',
                         note='chord 6 mm off the centre line, clear of the grate fingers'))
    bcx, bcy = burner('economy')[2], burner('economy')[3]
    gx = GRATES[0][2] + 20.0
    rays += [
        dict(key='grate_bar_count', a=(gx, bcy - 110, TOP_Z + 10), b=(gx, bcy + 110, TOP_Z + 10), measure='count', target=3, prov='PHOTO', tol=0),
        dict(key='grate_bar_thickness', a=(gx, bcy - 110, TOP_Z + 10), b=(gx, bcy + 110, TOP_Z + 10), measure='first_len', target=GRATE_T, prov='PHOTO'),
        dict(key='grate_top_above_counter', a=(gx, bcy, TOP_Z + 0.5), b=(gx, bcy, 200), measure='end', axis=2, target=GRATE_TOP, prov='INFERRED'),
        dict(key='grate_opening_is_open', a=(gx, bcy + 39, TOP_Z + 0.5), b=(gx, bcy + 39, 200), measure='none', target=0, prov='PHOTO', tol=0),
    ]
    wcx, wcy = burner('wok')[2], burner('wok')[3]
    rays.append(dict(key='wok_ring_chord', a=(wcx - 150, wcy + 50, TOP_Z + 15), b=(wcx + 150, wcy + 50, TOP_Z + 15),
                     measure='span', target=2 * math.sqrt(WOK_RING_R ** 2 - 2500.0), prov='PHOTO'))
    for r in rays:
        r.setdefault('tol', tol)
        r.setdefault('axis', None)
    return rays


def measure(ray, segments):
    """Re-derivable reduction of raw segments [(p_from, p_to)] (mm) to one number."""
    a, b = ray['a'], ray['b']
    d = [b[i] - a[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in d))
    u = [c / n for c in d]

    def t(p):
        return sum((p[i] - a[i]) * u[i] for i in range(3))
    iv = sorted(tuple(sorted((t(s[0]), t(s[1])))) for s in segments)
    merged = []
    for lo, hi in iv:
        if merged and ray.get('merge', True) and lo <= merged[-1][1] + 1e-3:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    m = ray['measure']
    if m == 'none' or m == 'count':
        return float(len(merged))
    if not merged:
        return None
    if m == 'span':
        return merged[-1][1] - merged[0][0]
    if m == 'first_len':
        return merged[0][1] - merged[0][0]
    if m == 'end':
        return a[ray['axis']] + merged[-1][1] * u[ray['axis']]
    if m == 'start':
        return a[ray['axis']] + merged[0][0] * u[ray['axis']]
    raise ValueError(m)


# ---------------------------------------------------------------- offline sanity
def check_profiles():
    """Closed, CCW, no edge below MIN_EDGE_IN. Returns a list of problems (empty = ok)."""
    problems = []
    min_mm = MIN_EDGE_IN * MM_PER_IN
    for p in parts():
        loops = p['loops'] if p['kind'] == 'prism' else [p['profile']]
        for li, pts in enumerate(loops):
            if len(pts) < 3:
                problems.append('%s loop %d: fewer than 3 points' % (p['key'], li))
                continue
            area = signed_area(pts)
            want_ccw = not (p['kind'] == 'prism' and li > 0)
            if (area > 0) != want_ccw:
                problems.append('%s loop %d: orientation %s' % (p['key'], li, 'CCW' if area > 0 else 'CW'))
            for i in range(len(pts)):
                q0, q1 = pts[i], pts[(i + 1) % len(pts)]
                e = math.hypot(q1[0] - q0[0], q1[1] - q0[1])
                if e < min_mm:
                    problems.append('%s loop %d edge %d: %.3f mm < %.3f mm' % (p['key'], li, i, e, min_mm))
        if p['kind'] == 'revolve' and min(q[0] for q in p['profile']) < 0:
            problems.append('%s: negative radius' % p['key'])
        z0 = p.get('z0', min(q[1] for q in p.get('profile', [(0, 0)])))
        z1 = p.get('z1', max(q[1] for q in p.get('profile', [(0, 0)])))
        if z1 - z0 < min_mm:
            problems.append('%s: height %.3f mm < floor' % (p['key'], z1 - z0))
    # every part above the glass must stay inside the plate outline
    hw, hd = WIDTH / 2.0, DEPTH / 2.0
    for p in parts():
        if p['kind'] == 'prism':
            xs = [q[0] for lp in p['loops'] for q in lp]
            ys = [q[1] for lp in p['loops'] for q in lp]
        else:
            r = max(q[0] for q in p['profile'])
            xs = [p['centre'][0] - r, p['centre'][0] + r]
            ys = [p['centre'][1] - r, p['centre'][1] + r]
        if min(xs) < -hw - 1e-6 or max(xs) > hw + 1e-6 or min(ys) < -hd - 1e-6 or max(ys) > hd + 1e-6:
            problems.append('%s: outside the 942 x 526 plate' % p['key'])
    if CASING_W > CUTOUT_W or not (CUTOUT_D_MIN - 1e-6 <= CASING_D <= CUTOUT_D_MAX):
        problems.append('casing does not fit the published cut-out')
    return problems


def inches(v):
    return v / MM_PER_IN


if __name__ == '__main__':
    probs = check_profiles()
    ps = parts()
    print('parts: %d, groups: %d, rays: %d' % (len(ps), len(groups()), len(measurement_rays())))
    print('groups per material: %r' % expected_groups_per_material())
    if probs:
        print('PROFILE PROBLEMS:')
        for x in probs:
            print('  ' + x)
        raise SystemExit(1)
    print('offline sanity: all profiles closed, orientation correct, every edge >= %.3f in' % MIN_EDGE_IN)
