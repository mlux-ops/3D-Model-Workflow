"""Phase 18: build the plan images, check images and manifest for the owner's path-drawing page.

Runs inside the Unreal Editor's Python. Uses phase18_capture for the depth captures.
make_plan(id) writes plans/<id>.png; check_plan(id) writes plans/check_<id>.png and returns the
measured marker errors; write_manifest() writes plans/manifest.json.

Orientation (forced by the page's formula X = left + u/w (right-left), Y = top + v/h (bottom-top)):
world +X (south) to the right, world +Y (west, the street) down. North (-X) is to the LEFT; the
rear of the lot (east, -Y) is at the top. Each image carries a north arrow.
"""

import json
import math
import os

import cv2
import numpy as np
import unreal
from PIL import Image, ImageDraw, ImageFont

import phase18_capture as pc

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS = os.path.join(HERE, "owner_review", "paths", "plans")
SIZE = pc.SIZE

# Lot (record rectangle) in level cm: origin at the south-west corner, north -X, east -Y.
LOT_X_N, LOT_Y_E = -1508.8, -3115.1
LOT_CORNERS = {"SW": (0.0, 0.0), "NW": (LOT_X_N, 0.0), "NE": (LOT_X_N, LOT_Y_E), "SE": (0.0, LOT_Y_E)}
KERB_E, CROWN, KERB_W = 361.0, 762.0, 1173.0  # Y of the east kerb, road crown, west kerb (west of the front lot line)
LEVEL_NORTH_WEST_OF_TRUE_DEG = 1.18

# Floor plans share one square window: 1.75 cm per pixel, 3,584 cm across.
FLOOR_W = 3584.0
FLOOR_C = (-754.4, -1557.6)
SITE_W = 10000.0
SITE_C = (-754.4, -1000.0)

LIFT = (-880.0, -1665.0, -628.0, -1477.0)  # x0, y0, x1, y1 of the shared lift shaft

PLAN_DEFS = [
    # id, label, floor_z, stair centre used for labelling and the check (centre of a stair run)
    ("site", "Site plan (roofs)", 0.0, (-1055.5, -3069.0)),
    ("lower_level", "Lower level (-1.50 m)", -150.0, (-629.0, -1981.0)),
    ("entry", "Entry hall and grade (+0.10 m)", 10.0, (-703.0, -770.0)),
    ("first_floor", "1st floor (+2.03 m)", 203.0, (-694.5, -2635.0)),
    ("rear_deck", "Rear deck (+2.03 m, over the garages)", 203.0, (-694.5, -2635.0)),
    ("second_floor", "2nd floor (+5.28 m)", 528.0, (-703.0, -888.0)),
    ("third_floor", "3rd floor (+8.53 m)", 853.0, (-816.5, -2365.0)),
    ("fourth_floor", "4th floor and rear terrace (+11.79 m)", 1179.0, (-816.5, -2365.0)),
    ("roof_deck", "Penthouse roof deck (+15.23 m)", 1523.0, (-692.0, -2363.5)),
]
DEFS = {d[0]: d for d in PLAN_DEFS}


def window(pid):
    c, w = (SITE_C, SITE_W) if pid == "site" else (FLOOR_C, FLOOR_W)
    return {"left": c[0] - w / 2, "right": c[0] + w / 2, "top": c[1] - w / 2, "bottom": c[1] + w / 2, "w": w, "c": c}


def to_px(win, x, y):
    """The page's own formula, inverted: world (x, y) -> pixel (u, v)."""
    return ((x - win["left"]) / (win["right"] - win["left"]) * SIZE,
            (y - win["top"]) / (win["bottom"] - win["top"]) * SIZE)


def _actors(prefixes):
    out = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if not a.get_level().get_outer().get_name().startswith("L_W1529"):
            continue
        if a.get_actor_label().startswith(prefixes):
            o, e = a.get_actor_bounds(False, True)
            if e.z > 0:
                out.append((a, o.z - e.z, o.z + e.z))
    return out


def _font(n):
    for f in ("arialbd.ttf", "arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", f), n)
        except OSError:
            pass
    return ImageFont.load_default()


def _shade(h, lo, hi, a, b):
    t = np.clip((h - lo) / (hi - lo), 0, 1)
    return a + (b - a) * t


def _edges(h, thresh):
    gx = cv2.Sobel(h.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3) / 8.0
    gy = cv2.Sobel(h.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3) / 8.0
    return np.hypot(gx, gy) > thresh


def floor_base(pid):
    """Grey plan of one floor: cut 120 cm above the floor, walls, doors, windows."""
    _, _, fz, _ = DEFS[pid]
    win = window(pid)
    cx, cy = win["c"]
    cut = fz + 120.0
    d = pc.capture_depth(cx, cy, cut, win["w"], near_cm=0.0, name=pid + "_cut")
    hit = d < 1e5
    h = np.where(hit, cut - d, -1000.0) - fz  # height above this floor
    g = np.full(h.shape, 0.92)
    g = np.where(h < -25, _shade(h, -450, -25, 0.62, 0.84), g)                # below the floor: stairs down, yards
    g = np.where(h > 25, _shade(h, 25, 120, 0.80, 0.60), g)                    # furniture, counters, rails
    g = np.where(~hit, 0.97, g)
    e = _edges(np.where(hit, h, -1000.0), 6.0)
    g = np.where(e, 0.38, g)
    rgb = np.dstack([g, g, g])

    walls = _actors(("Walls_", "Structural_"))
    near_floor = [a for a, z0, z1 in walls if fz - 60 <= z0 <= cut and z1 > cut]
    through = [a for a, z0, z1 in walls if z0 < fz - 60 and z1 > cut]
    wall = np.zeros(h.shape, bool)
    if near_floor:
        cam = fz - 40.0
        du = pc.capture_depth(cx, cy, cam, win["w"], 0.0, near_floor, look_up=True, name=pid + "_wall_up")
        wall |= (du < 1e5) & (cam + du <= cut)
    if through:
        dd = pc.capture_depth(cx, cy, 6000.0, win["w"], 0.0, through, name=pid + "_wall_thru")
        wall |= dd < 1e5
    rgb[wall] = (0.22, 0.22, 0.24)

    for prefixes, colour in ((("Windows_",), (0.47, 0.67, 0.85)), (("Doors_",), (0.82, 0.62, 0.40))):
        acts = [a for a, z0, z1 in _actors(prefixes) if z0 <= cut and z1 > cut]
        if acts:
            dm = pc.capture_depth(cx, cy, 6000.0, win["w"], 0.0, acts, name=pid + "_" + prefixes[0].strip("_"))
            m = dm < 1e5
            rgb[m] = colour
            rgb[_edges(m.astype(np.float32) * 100, 10) & m] = (0.35, 0.25, 0.15)
    return rgb


def site_base():
    win = window("site")
    cx, cy = win["c"]
    top = 6000.0
    d = pc.capture_depth(cx, cy, top, win["w"], 0.0, name="site_top")
    hit = d < 1e5
    h = np.where(hit, top - d, -1000.0)
    g = np.where(h < 60, _shade(h, -100, 60, 0.86, 0.92), _shade(h, 60, 2400, 0.80, 0.50))
    g = np.where(~hit, 0.97, g)
    g = np.where(_edges(np.where(hit, h, -1000.0), 25.0), 0.35, g)
    return np.dstack([g, g, g])


def _dashed(dr, p, q, colour, width, dash=18, gap=10):
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    n = int(L // (dash + gap)) + 1
    for i in range(n):
        a, b = i * (dash + gap) / L, min(1.0, (i * (dash + gap) + dash) / L)
        dr.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=colour, width=width)


def annotate(pid, rgb):
    win = window(pid)
    _, label, fz, stair = DEFS[pid]
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    dr = ImageDraw.Draw(img)
    P = lambda x, y: to_px(win, x, y)
    s = SIZE / win["w"]  # pixels per cm

    # Street: kerbs and crown (Wieland, west of the front lot line = +Y).
    for yk, txt in ((KERB_E, "east kerb"), (KERB_W, "west kerb")):
        if win["top"] < yk < win["bottom"]:
            dr.line([P(win["left"], yk), P(win["right"], yk)], fill=(90, 90, 90), width=4)
    if win["top"] < CROWN < win["bottom"]:
        _dashed(dr, P(win["left"], CROWN), P(win["right"], CROWN), (230, 190, 40), 4, 30, 20)
    sy = min(win["bottom"] - 60 / s, (KERB_E + KERB_W) / 2) if pid == "site" else win["bottom"] - 70 / s
    dr.text(P(-754.4, sy), "N. WIELAND ST (street)" if pid == "site" else "toward N. Wieland St (street)",
            fill=(60, 60, 60), font=_font(40), anchor="mm")

    # Lot line.
    c = LOT_CORNERS
    for a, b in (("SW", "NW"), ("NW", "NE"), ("NE", "SE"), ("SE", "SW")):
        _dashed(dr, P(*c[a]), P(*c[b]), (210, 30, 30), 5)
    dr.text((P(*c["SW"])[0] + 8, P(*c["SW"])[1] + 8), "lot line", fill=(210, 30, 30), font=_font(28))

    # Lift and stair labels (floor plans).
    if pid != "site":
        x0, y0, x1, y1 = LIFT
        a, b = P(x0, y0), P(x1, y1)
        dr.rectangle([a, b], outline=(20, 90, 160), width=4)
        dr.line([a, b], fill=(20, 90, 160), width=3)
        dr.line([(a[0], b[1]), (b[0], a[1])], fill=(20, 90, 160), width=3)
        dr.text(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), "LIFT", fill=(20, 90, 160), font=_font(30), anchor="mm",
                stroke_width=4, stroke_fill=(255, 255, 255))
        u, v = P(*stair)
        dr.text((u, v), "STAIR", fill=(150, 40, 120), font=_font(28), anchor="mm", stroke_width=4, stroke_fill=(255, 255, 255))
    if pid == "rear_deck":
        a, b = P(-1415.0, -3016.0), P(-94.0, -2486.0)
        dr.rectangle([a, b], outline=(30, 150, 60), width=8)
        dr.text(((a[0] + b[0]) / 2, a[1] - 30), "REAR DECK", fill=(30, 150, 60), font=_font(40), anchor="mm",
                stroke_width=5, stroke_fill=(255, 255, 255))

    # Title block, north arrow, scale bar.
    dr.rectangle([20, 20, 1180, 150], fill=(255, 255, 255), outline=(80, 80, 80), width=2)
    dr.text((40, 32), "1529 N. Wieland - " + label, fill=(20, 20, 20), font=_font(44))
    sub = "Cut 1.2 m above the floor" if pid != "site" else "Roofs on"
    dr.text((40, 92), sub + ".  Street at the bottom, NORTH IS TO THE LEFT.", fill=(60, 60, 60), font=_font(30))
    # north arrow: level north is -X (left); true north is 1.18 deg clockwise of level north... drawn as level north.
    ax, ay = 1930, 140
    dr.ellipse([ax - 85, ay - 85, ax + 85, ay + 85], fill=(255, 255, 255), outline=(40, 40, 40), width=3)
    dr.polygon([(ax - 70, ay), (ax + 30, ay - 28), (ax + 10, ay), (ax + 30, ay + 28)], fill=(20, 20, 20))
    dr.text((ax - 112, ay), "N", fill=(20, 20, 20), font=_font(54), anchor="rm")
    dr.text((ax, ay + 110), "north = level -X", fill=(40, 40, 40), font=_font(24), anchor="mm")
    m = 10.0 if pid == "site" else 5.0
    L = m * 100 * s
    x0, y0 = 40, SIZE - 60
    dr.rectangle([x0 - 10, y0 - 60, x0 + L + 120, y0 + 30], fill=(255, 255, 255))
    for i in range(int(m)):
        dr.rectangle([x0 + i * L / m, y0 - 12, x0 + (i + 1) * L / m, y0], fill=(20, 20, 20) if i % 2 == 0 else (255, 255, 255), outline=(20, 20, 20))
    dr.text((x0, y0 - 18), "0", fill=(20, 20, 20), font=_font(26), anchor="ms")
    dr.text((x0 + L, y0 - 18), "%d m" % m, fill=(20, 20, 20), font=_font(26), anchor="ms")
    return img


def make_plan(pid):
    os.makedirs(PLANS, exist_ok=True)
    if pid == "site":
        rgb = site_base()
    elif pid == "rear_deck":
        rgb = np.asarray(Image.open(os.path.join(pc.SCRATCH, "first_floor_base.png"))).astype(np.float64) / 255.0
    else:
        rgb = floor_base(pid)
    if pid == "first_floor":
        Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(os.path.join(pc.SCRATCH, "first_floor_base.png"))
    img = annotate(pid, rgb)
    path = os.path.join(PLANS, pid + ".png")
    img.save(path)
    return path


def _marker(x, y, z):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0))
    a.tags = [unreal.Name(pc.TAG)]
    a.static_mesh_component.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube.Cube"))
    a.set_actor_scale3d(unreal.Vector(0.24, 0.24, 0.24))  # 24 cm cube
    return a


def check_plan(pid):
    """Render three temporary marker cubes from the plan's own camera, find their centres in the
    image, and compare with where the page's formula puts them."""
    _, _, fz, stair = DEFS[pid]
    win = window(pid)
    pts = {"lot corner SW": LOT_CORNERS["SW"], "lot corner NE": LOT_CORNERS["NE"], "stair centre": stair}
    z = fz + 40.0
    markers = {k: _marker(x, y, z) for k, (x, y) in pts.items()}
    try:
        cam = 6000.0
        d = pc.capture_depth(win["c"][0], win["c"][1], cam, win["w"], 0.0, list(markers.values()), name=pid + "_markers")
    finally:
        removed = pc.cleanup()
    hit = (d < 1e5).astype(np.uint8)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(hit, 8)
    found = [(cent[i][0] + 0.5, cent[i][1] + 0.5) for i in range(1, n)]  # pixel centres: index + 0.5
    img = Image.open(os.path.join(PLANS, pid + ".png")).convert("RGB")
    dr = ImageDraw.Draw(img)
    res = []
    for k, (x, y) in pts.items():
        u, v = to_px(win, x, y)
        best = min(found, key=lambda f: math.hypot(f[0] - u, f[1] - v)) if found else (float("nan"),) * 2
        err = math.hypot(best[0] - u, best[1] - v)
        res.append({"point": k, "world_x_cm": x, "world_y_cm": y, "expected_u": round(u, 2), "expected_v": round(v, 2),
                    "rendered_u": round(best[0], 2), "rendered_v": round(best[1], 2), "error_px": round(err, 2),
                    "pass": bool(err <= 3.0)})
        dr.ellipse([u - 22, v - 22, u + 22, v + 22], outline=(255, 0, 255), width=4)
        dr.line([(u - 32, v), (u + 32, v)], fill=(255, 0, 255), width=2)
        dr.line([(u, v - 32), (u, v + 32)], fill=(255, 0, 255), width=2)
        bu, bv = best
        dr.rectangle([bu - 4, bv - 4, bu + 4, bv + 4], fill=(0, 200, 0))
        dr.text((u + 30, v - 50), "%s  %.1f px" % (k, err), fill=(160, 0, 160), font=_font(28), stroke_width=4, stroke_fill=(255, 255, 255))
    dr.rectangle([20, 160, 1180, 210], fill=(255, 255, 255))
    dr.text((40, 168), "CHECK: magenta cross = formula, green square = rendered marker", fill=(160, 0, 160), font=_font(28))
    img.save(os.path.join(PLANS, "check_" + pid + ".png"))
    return {"id": pid, "markers_found": len(found), "temp_actors_removed": removed, "points": res}


def write_manifest():
    plans = []
    for pid, label, fz, _ in PLAN_DEFS:
        w = window(pid)
        plans.append({"id": pid, "label": label, "image": pid + ".png", "width_px": SIZE, "height_px": SIZE,
                      "world_x_at_left_cm": round(w["left"], 2), "world_x_at_right_cm": round(w["right"], 2),
                      "world_y_at_top_cm": round(w["top"], 2), "world_y_at_bottom_cm": round(w["bottom"], 2),
                      "floor_z_cm": fz, "default_eye_height_cm": 160,
                      "cm_per_px": round(w["w"] / SIZE, 6),
                      "cut_height_cm": None if pid == "site" else fz + 120.0})
    m = {"plans": plans, "north_up": False, "units": "Unreal centimetres, level axes",
         "up_axis": "-Y (east, the rear of the lot)", "right_axis": "+X (south)", "north_direction_on_image": "left (-X)",
         "orientation_note": ("The page's formula ties world X to the horizontal pixel axis, and this level's north is -X, "
                              "so north cannot point up without breaking the formula. The formula is kept exact; north points "
                              "LEFT on every image (arrow drawn), the street is at the bottom. Level north is %.2f degrees west "
                              "of true north." % LEVEL_NORTH_WEST_OF_TRUE_DEG),
         "page_yaw_note": ("index.html draws a 'Hold a direction' arrow with yaw_deg 0 pointing to the TOP of the image, "
                           "clockwise on screen. On these images the top is east (-Y), so the drawn arrow means "
                           "Unreal yaw = yaw_deg - 90 (0 = east/-Y, 90 = south/+X, 180 = west/street/+Y, 270 = north/-X). "
                           "The page's label 'from north' does not fit these images; level north is 270 on that dial."),
         "pixel_convention": "u, v measured from the top-left corner of the top-left pixel; pixel i covers u in [i, i+1).",
         "made_by": "Phase 18, tools/phase18_plans.py"}
    with open(os.path.join(PLANS, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1)
    return m
