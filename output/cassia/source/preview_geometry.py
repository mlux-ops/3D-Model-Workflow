"""Offline preview and gate dry-run for the Cassia family geometry (CPython 3).

Meshes every part defined in cassia_geometry.py, fires the same measurement rays
the native builder fires, and renders:
  preview/overlay_elevation_on_drawing.png  model edges (red) over the supplied elevation
  preview/overlay_plan_on_drawing.png       model edges (red) over the supplied plan
  preview/compare_render_view.png           shaded model beside the supplied white render
  preview/views_contact_sheet.png           front / side / oblique / plan, shaded
  preview/offline_checks.json               profile checks + ray dry-run results

This is NOT a Revit result. It checks the geometry constants and the gate logic
before the native run; every native gate still has to pass in Revit 2025.

    python preview_geometry.py        (needs numpy and pillow)
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cassia_geometry as G  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

RUN_DIR = os.path.normpath(os.path.join(HERE, '..'))
REPO = os.path.normpath(os.path.join(RUN_DIR, '..', '..'))
REF = os.path.join(REPO, 'references', 'cassia')
_RUN_NORM = os.path.normpath(RUN_DIR)


def out_path(*parts):
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if not target.startswith(_RUN_NORM + os.sep):
        raise RuntimeError('write escapes run dir: ' + target)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    return target


# ------------------------------------------------------------------ meshing
N_AROUND = 144
ARC_STEP_DEG = 2.0


def frame(axis):
    axis = np.asarray(axis, float)
    axis = axis / np.linalg.norm(axis)
    ref = np.array([0.0, 0.0, 1.0]) if abs(axis[2]) < 0.99 else np.array([1.0, 0.0, 0.0])
    e1 = ref - axis * ref.dot(axis)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    return axis, e1, e2


def segment_samples(seg):
    """Points and (nr, na) normals along one profile segment."""
    if seg[0] == 'line':
        (r0, a0), (r1, a1) = seg[1], seg[2]
        dr, da = r1 - r0, a1 - a0
        n = np.array([da, -dr]) / math.hypot(dr, da)
        return np.array([[r0, a0], [r1, a1]]), np.array([n, n])
    (ux, uy), rho, t0, sweep = G._arc_angles(seg[1], seg[2], seg[3])
    k = max(2, int(math.ceil(abs(math.degrees(sweep)) / ARC_STEP_DEG)))
    t = t0 + sweep * np.linspace(0.0, 1.0, k + 1)
    pts = np.c_[ux + rho * np.cos(t), uy + rho * np.sin(t)]
    nrm = np.c_[np.cos(t), np.sin(t)]
    return pts, nrm


def revolve_mesh(part):
    """Triangles (M,3,3) and vertex normals (M,3,3) in family-local inches."""
    axis, e1, e2 = frame(part['axis'])
    origin = np.asarray(part['origin'], float)
    th = (np.arange(N_AROUND) + 0.5) * 2 * math.pi / N_AROUND   # half-step: rays miss seams
    c, s = np.cos(th), np.sin(th)
    ring = c[:, None] * e1[None, :] + s[:, None] * e2[None, :]  # (N,3)
    tris, norms = [], []
    for seg in G.segments(part['profile']):
        pts, nrm = segment_samples(seg)
        P = origin[None, None, :] + pts[:, 1][:, None, None] * axis[None, None, :] \
            + pts[:, 0][:, None, None] * ring[None, :, :]                       # (K,N,3)
        Nn = nrm[:, 0][:, None, None] * ring[None, :, :] + nrm[:, 1][:, None, None] * axis[None, None, :]
        K = len(pts)
        for i in range(K - 1):
            for j in range(N_AROUND):
                j2 = (j + 1) % N_AROUND
                a, b, cc, d = P[i, j], P[i, j2], P[i + 1, j2], P[i + 1, j]
                na, nb, nc, nd = Nn[i, j], Nn[i, j2], Nn[i + 1, j2], Nn[i + 1, j]
                for tri, nt in (((a, b, cc), (na, nb, nc)), ((a, cc, d), (na, nc, nd))):
                    if np.linalg.norm(np.cross(tri[1] - tri[0], tri[2] - tri[0])) > 1e-12:
                        tris.append(tri)
                        norms.append(nt)
    return np.array(tris), np.array(norms)


# ------------------------------------------------------------ ray dry-run
def ray_mesh_segments(tris, p0, p1):
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    d = p1 - p0
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    h = np.cross(d, e2)
    a = np.einsum('ij,ij->i', e1, h)
    ok = np.abs(a) > 1e-14
    f = np.zeros_like(a)
    f[ok] = 1.0 / a[ok]
    s = p0 - v0
    u = f * np.einsum('ij,ij->i', s, h)
    q = np.cross(s, e1)
    v = f * (q @ d)
    t = f * np.einsum('ij,ij->i', e2, q)
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t >= 0) & (t <= 1)
    ts = np.sort(t[hit])
    dedup = []
    for x in ts:
        if not dedup or x - dedup[-1] > 1e-9:
            dedup.append(x)
    if len(dedup) % 2:
        # odd crossings: the ray starts inside a closed solid (Revit's
        # IntersectWithCurve then reports a segment beginning at p0)
        dedup = [0.0] + dedup
    segs = []
    for i in range(0, len(dedup), 2):
        segs.append((tuple(p0 + d * dedup[i]), tuple(p0 + d * dedup[i + 1])))
    return segs, len(dedup)


def dry_run(meshes):
    rows = []
    sections = {}
    for ray in G.measurement_rays():
        segs, nhits = ray_mesh_segments(meshes[ray['part']][0], ray['p0'], ray['p1'])
        value = None if segs is None else float(G.reduce_segments(ray, segs))
        row = {'key': ray['key'], 'part': ray['part'], 'target_in': ray['target'],
               'tol_in': ray['tol'], 'measured_in': value, 'hits': nhits, 'source': ray['source'],
               'pass': bool(value is not None and abs(value - ray['target']) <= ray['tol'])}
        rows.append(row)
        if 'radius' in ray and value is not None:
            sections.setdefault(ray['part'], []).append((ray['radius'], value))
    angles = {}
    for part, vals in sorted(sections.items()):
        ang = float(G.arm_angle_from_sections(sorted(vals)))
        angles[part] = {'measured_deg': ang, 'target_deg': G.ARM_ANGLE_DEG,
                        'pass': bool(abs(ang - G.ARM_ANGLE_DEG) <= G.ANGLE_TOL_DEG)}
    clear = []
    for cr in G.clearance_rays():
        gsegs, _ = ray_mesh_segments(meshes[cr['glass']][0], cr['p0'], cr['p1'])
        inside = []
        for key in cr['inside']:
            segs, _ = ray_mesh_segments(meshes[key][0], cr['p0'], cr['p1'])
            inside.extend(segs or [])
        c, gi, po = G.clearance_from_segments(cr['p0'], gsegs or [], inside)
        clear.append({'key': cr['key'], 'station_in': cr['station_in'],
                      'clearance_in': None if c is None else float(c),
                      'glass_inner_radius_in': None if gi is None else float(gi),
                      'inside_outer_radius_in': None if po is None else float(po),
                      'pass': bool(c is not None and c >= G.MIN_INTERNAL_CLEARANCE)})
    return rows, angles, clear


# --------------------------------------------------------------- render
BRASS = np.array([146, 107, 60]) / 255.0
OPAL = np.array([244, 240, 234]) / 255.0
LAMP = np.array([250, 248, 240]) / 255.0


def to_world(p):
    """Family-local inches -> hosted world inches (ceiling at Z=0, Z up)."""
    p = np.asarray(p, float)
    return p * np.array([1.0, -1.0, -1.0])


class Camera(object):
    def __init__(self, W, H, forward, up, scale=None, eye=None, focal=None, centre=(0.0, 0.0)):
        self.W, self.H = W, H
        self.d = np.asarray(forward, float) / np.linalg.norm(forward)
        r = np.cross(self.d, up)
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.d)
        self.scale, self.eye, self.focal, self.centre = scale, eye, focal, centre

    def project(self, P):
        if self.eye is None:
            x = P @ self.r
            y = P @ self.u
            z = P @ self.d
            px = self.centre[0] + x * self.scale
            py = self.centre[1] - y * self.scale
        else:
            v = P - self.eye
            z = v @ self.d
            px = self.centre[0] + self.focal * (v @ self.r) / z
            py = self.centre[1] - self.focal * (v @ self.u) / z
        return px, py, z


def rasterize(cam, tris_w, norms_w, ids):
    W, H = cam.W, cam.H
    zbuf = np.full((H, W), np.inf)
    nbuf = np.zeros((H, W, 3))
    pbuf = np.zeros((H, W, 3))
    idb = np.full((H, W), -1, int)
    flat = tris_w.reshape(-1, 3)
    px, py, pz = cam.project(flat)
    px = px.reshape(-1, 3)
    py = py.reshape(-1, 3)
    pz = pz.reshape(-1, 3)
    for i in range(len(tris_w)):
        x, y, z = px[i], py[i], pz[i]
        if cam.eye is not None and np.any(z <= 0):   # behind a perspective camera only
            continue
        x0 = max(int(math.floor(x.min())), 0)
        x1 = min(int(math.ceil(x.max())) + 1, W)
        y0 = max(int(math.floor(y.min())), 0)
        y1 = min(int(math.ceil(y.max())) + 1, H)
        if x0 >= x1 or y0 >= y1:
            continue
        area = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0])
        if abs(area) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w0 = ((x[1] - gx) * (y[2] - gy) - (x[2] - gx) * (y[1] - gy)) / area
        w1 = ((x[2] - gx) * (y[0] - gy) - (x[0] - gx) * (y[2] - gy)) / area
        w2 = 1.0 - w0 - w1
        inside = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
        if not inside.any():
            continue
        zz = w0 * z[0] + w1 * z[1] + w2 * z[2]
        sub = zbuf[y0:y1, x0:x1]
        m = inside & (zz < sub)
        if not m.any():
            continue
        sub[m] = zz[m]
        n = (w0[..., None] * norms_w[i, 0] + w1[..., None] * norms_w[i, 1] + w2[..., None] * norms_w[i, 2])
        p = (w0[..., None] * tris_w[i, 0] + w1[..., None] * tris_w[i, 1] + w2[..., None] * tris_w[i, 2])
        nbuf[y0:y1, x0:x1][m] = n[m]
        pbuf[y0:y1, x0:x1][m] = p[m]
        idb[y0:y1, x0:x1][m] = ids[i]
    return zbuf, nbuf, pbuf, idb


def shade(cam, nbuf, pbuf, idb, materials, bg=(1.0, 1.0, 1.0)):
    H, W = idb.shape
    img = np.ones((H, W, 3)) * np.asarray(bg)
    m = idb >= 0
    n = nbuf[m]
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    if cam.eye is None:
        view = np.tile(-cam.d, (len(n), 1))
    else:
        view = cam.eye[None, :] - pbuf[m]
        view /= np.linalg.norm(view, axis=1, keepdims=True)
    flip = np.einsum('ij,ij->i', n, view) < 0
    n[flip] *= -1
    # camera-relative studio lighting: key upper-left, fill right, soft top light
    lights = [(-cam.d * 0.55 + cam.u * 0.55 - cam.r * 0.60, 0.55),
              (-cam.d * 0.80 + cam.r * 0.60, 0.30),
              (np.array([0.0, 0.0, 1.0]) - cam.d * 0.3, 0.20)]
    kind = materials[idb[m]]
    base = np.where(kind[:, None] == 0, BRASS[None, :], np.where(kind[:, None] == 1, OPAL[None, :], LAMP[None, :]))
    ambient = np.where(kind == 1, 0.60, np.where(kind == 0, 0.34, 0.55))
    col = base * ambient[:, None]
    for L, k in lights:
        L = L / np.linalg.norm(L)
        diff = np.clip(n @ L, 0, None)
        col += base * k * diff[:, None]
        h = L[None, :] + view
        h /= np.maximum(np.linalg.norm(h, axis=1, keepdims=True), 1e-9)
        spec = np.clip(np.einsum('ij,ij->i', n, h), 0, None)
        is_metal = (kind == 0)[:, None]
        col += np.where(is_metal, np.array([1.0, 0.86, 0.62])[None, :] * 0.55 * k * spec[:, None] ** 24,
                        0.10 * k * spec[:, None] ** 6)
    img[m] = np.clip(col, 0, 1)
    return img


def edges_from_ids(idb):
    e = np.zeros(idb.shape, bool)
    e[:, 1:] |= idb[:, 1:] != idb[:, :-1]
    e[1:, :] |= idb[1:, :] != idb[:-1, :]
    return e


def downsample(img, k):
    H, W = img.shape[:2]
    return img[:H - H % k, :W - W % k].reshape(H // k, k, W // k, k, -1).mean(axis=(1, 3))


def main():
    problems = G.check_profiles()
    parts = G.parts()
    meshes = {}
    for p in parts:
        meshes[p['key']] = revolve_mesh(p)
    rows, angles, clear = dry_run(meshes)

    # assemble world-space triangle soup
    mat_code = {'metal': 0, 'glass': 1, 'lamp': 2}
    T, N, I, M = [], [], [], []
    for pid, p in enumerate(parts):
        tri, nrm = meshes[p['key']]
        T.append(to_world(tri))
        N.append(to_world(nrm))
        I.append(np.full(len(tri), pid))
        M.append(mat_code[p['material']])
    T = np.concatenate(T)
    N = np.concatenate(N)
    I = np.concatenate(I)
    materials = np.array(M)
    report = {'note': 'Offline CPython mesh dry-run of cassia_geometry.py; not a Revit result.',
              'triangles': int(len(T)), 'profile_problems': problems, 'rays': rows,
              'arm_angles': angles, 'clearances': clear, 'geometry': G.summary(),
              'all_clearances_pass': all(c['pass'] for c in clear),
              'all_rays_pass': all(r['pass'] for r in rows),
              'all_angles_pass': all(a['pass'] for a in angles.values())}

    PX = 22.03
    drawing = Image.open(os.path.join(REF, 'user_supplied_dimension_drawing.png')).convert('RGB')
    dw = np.asarray(drawing).astype(float) / 255.0
    SS = 4

    # elevation: world viewer to the south looking north; canopy top at drawing (316.54, 69)
    cam = Camera(drawing.width * SS, drawing.height * SS, (0, 1, 0), (0, 0, 1), scale=PX * SS,
                 centre=(316.54 * SS, 69.0 * SS))
    _, _, _, idb = rasterize(cam, T, N, I)
    edge = downsample(edges_from_ids(idb).astype(float)[..., None], SS)[..., 0] > 0.12
    over = dw.copy()
    over[edge] = [0.85, 0.05, 0.05]
    Image.fromarray((over[0:300] * 255).astype(np.uint8)).resize((1200, 600), Image.LANCZOS).save(
        out_path('preview', 'overlay_elevation_on_drawing.png'))

    # plan from below; canopy centre at drawing (316.6, 563.8)
    cam = Camera(drawing.width * SS, drawing.height * SS, (0, 0, 1), (0, -1, 0), scale=PX * SS,
                 centre=(316.6 * SS, 563.8 * SS))
    _, _, _, idb = rasterize(cam, T, N, I)
    edge = downsample(edges_from_ids(idb).astype(float)[..., None], SS)[..., 0] > 0.12
    over = dw.copy()
    over[edge] = [0.85, 0.05, 0.05]
    Image.fromarray((over[330:790] * 255).astype(np.uint8)).resize((1200, 920), Image.LANCZOS).save(
        out_path('preview', 'overlay_plan_on_drawing.png'))

    # perspective comparison with the supplied white render (camera estimated, not solved)
    photo = Image.open(os.path.join(REF, 'user_supplied_render_white.jpg')).convert('RGB')
    # Camera estimated from the render, not solved: opposite the globe at world
    # azimuth 120 deg (so the canopy screw at 270 deg shows 30 deg left of centre),
    # 63 in away, looking up 8.5 deg.
    beta = math.radians(8.5)
    az = math.radians(300.0)
    D = 63.0
    target = np.array([0.0, 0.0, -3.6])
    eye = target + D * np.array([math.cos(az) * math.cos(beta), math.sin(az) * math.cos(beta), -math.sin(beta)])
    Wp = photo.width
    cam = Camera(Wp * 2, Wp * 2, target - eye, (0, 0, 1), eye=eye, focal=3920.0 * 2,
                 centre=(Wp, Wp * 0.98))
    _, nb, pb, idb = rasterize(cam, T, N, I)
    img = downsample(shade(cam, nb, pb, idb, materials), 2)
    both = np.concatenate([np.asarray(photo).astype(float) / 255.0, img], axis=1)
    Image.fromarray((both * 255).astype(np.uint8)).resize((1600, 800), Image.LANCZOS).save(
        out_path('preview', 'compare_render_view.png'))

    # orthographic contact sheet
    tiles = []
    for name, fwd, up in [('front (drawing elevation)', (0, 1, 0), (0, 0, 1)),
                          ('side (along one arm)', (1, 0, 0), (0, 0, 1)),
                          ('oblique from below', (0.62, 0.62, 0.48), (0, 0, 1)),
                          ('plan from below', (0, 0, 1), (0, -1, 0))]:
        cam = Camera(1000, 1000, fwd, up, scale=48.0, centre=(500, 500))
        c = cam.project(np.array([[0.0, 0.0, -3.8]]))
        cam.centre = (500 - (c[0][0] - 500), 500 - (c[1][0] - 500))
        _, nb, pb, idb = rasterize(cam, T, N, I)
        tiles.append(downsample(shade(cam, nb, pb, idb, materials), 2))
    sheet = np.concatenate([np.concatenate(tiles[:2], axis=1), np.concatenate(tiles[2:], axis=1)], axis=0)
    Image.fromarray((sheet * 255).astype(np.uint8)).save(out_path('preview', 'views_contact_sheet.png'))

    with open(out_path('preview', 'offline_checks.json'), 'w') as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    bad = [r for r in rows if not r['pass']]
    print('profiles: %d problem(s)' % len(problems))
    for p in problems:
        print('  ' + p)
    print('rays: %d, failing: %d' % (len(rows), len(bad)))
    for r in rows:
        print('  %-30s %-9s target %8.4f measured %s hits %d %s' % (
            r['key'], r['source'], r['target_in'],
            'None' if r['measured_in'] is None else '%8.4f' % r['measured_in'], r['hits'],
            'PASS' if r['pass'] else 'FAIL'))
    for k, a in sorted(angles.items()):
        print('  %-30s angle %.4f deg %s' % (k, a['measured_deg'], 'PASS' if a['pass'] else 'FAIL'))
    worst = min(clear, key=lambda c: c['clearance_in'] if c['clearance_in'] is not None else -1)
    print('clearances: %d rays, min %.4f in at %s, all pass: %s' % (
        len(clear), worst['clearance_in'], worst['key'], report['all_clearances_pass']))
    ok = not problems and not bad and report['all_angles_pass'] and report['all_clearances_pass']
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
