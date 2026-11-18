"""Phase 11, step 11.2: turn a planned route into one 30-second camera move, frame by frame. Runs outside the editor.

    python -B review/phase11/scripts/move_build.py <name>

Reads review/phase11/paths/<name>_route.json (points [x, y, height of the walking surface]) and
review/phase11/paths/<name>_move_job.json:
    {"door": [x, y, z],            the point on the route where the camera passes outdoors
     "outdoor_seconds": 10.0,      how long the move stays outdoors at its end
     "outdoor_ev": 14.644,         exposure outdoors (the default is the lighting level's; a shaded patio needs less)
     "end_look": [x, y, z] or null, a point the camera turns to in its last seconds (null: keeps looking ahead)
     "end_look_seconds": 4.0,
     "low_ev": [[eye height, ev100], ...] or null   exposure by eye height inside (for the dark lower level)}
Writes review/phase11/paths/<name>_move.json = {"fps": 30, "frames": [{"f", "loc", "rot" (pitch, yaw, roll), "ev"}]}
and prints the speeds and the fastest turn. The camera's eye is EYE cm above the walking surface. It looks at the
point LOOK_AHEAD cm further along its own path.
"""
import json
import math
import sys

PATHS = "review/phase11/paths/"
FPS = 30
FRAMES = 900
EYE = 160.0
STEP = 2.0            # cm between samples of the path
SMOOTH_PATH = 22.0    # cm, width (sigma) of the smoothing of the path
LOOK_AHEAD = 250.0    # cm
SMOOTH_TURN = 0.40    # s, width (sigma) of the smoothing of the camera's turning
PITCH_SHARE = 0.6     # the camera tilts this share of the slope it looks along
PITCH_LIMIT = 22.0    # degrees
EV_INSIDE = 9.0
EV_OUTSIDE = 14.644
EV_BEFORE, EV_AFTER = 0.4, 1.2   # s before and after the door over which the exposure changes


def smoothstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3.0 - 2.0 * u)


def gauss(values, sigma, pin_ends=True):
    """Gaussian smoothing of a list of numbers; sigma in samples. The ends are held by mirroring about them."""
    reach = int(math.ceil(sigma * 3.0))
    weights = [math.exp(-0.5 * (k / sigma) ** 2) for k in range(-reach, reach + 1)]
    total = sum(weights)
    n = len(values)
    out = []
    for i in range(n):
        acc = 0.0
        for k in range(-reach, reach + 1):
            j = i + k
            if j < 0:
                v = 2.0 * values[0] - values[min(n - 1, -j)] if pin_ends else values[0]
            elif j >= n:
                v = 2.0 * values[n - 1] - values[max(0, 2 * (n - 1) - j)] if pin_ends else values[n - 1]
            else:
                v = values[j]
            acc += weights[k + reach] * v
        out.append(acc / total)
    return out


def clean(points):
    """Drop points that sit on top of the one before, and 5 cm there-and-back spikes left by the planner."""
    kept = []
    for p in points:
        if kept and math.dist(kept[-1], p) < 12.0:
            continue
        kept.append(list(p))
    changed = True
    while changed:
        changed = False
        for i in range(1, len(kept) - 1):
            a, b, c = kept[i - 1], kept[i], kept[i + 1]
            u = [b[k] - a[k] for k in range(3)]
            v = [c[k] - b[k] for k in range(3)]
            lu, lv = math.hypot(*u), math.hypot(*v)
            cosine = sum(u[k] * v[k] for k in range(3)) / (lu * lv)
            if cosine < -0.5 and min(lu, lv) < 40.0:
                del kept[i]
                changed = True
                break
    return kept


def resample(points):
    out = [list(points[0])]
    carry = 0.0
    for a, b in zip(points[:-1], points[1:]):
        length = math.dist(a, b)
        d = STEP - carry
        while d <= length:
            f = d / length
            out.append([a[k] + (b[k] - a[k]) * f for k in range(3)])
            d += STEP
        carry = length - (d - STEP)
    if math.dist(out[-1], points[-1]) > 0.5:
        out.append(list(points[-1]))
    return out


def at(path, cumulative, s):
    """The point of the path at distance s; beyond the end it goes on straight along the last direction."""
    total = cumulative[-1]
    if s >= total:
        a, b = path[-40], path[-1]
        length = math.dist(a, b)
        return [b[k] + (b[k] - a[k]) / length * (s - total) for k in range(3)]
    i = min(len(path) - 2, int(s / total * (len(path) - 1)))
    while cumulative[i] > s and i > 0:
        i -= 1
    while cumulative[i + 1] < s and i < len(path) - 2:
        i += 1
    span = cumulative[i + 1] - cumulative[i]
    f = 0.0 if span <= 0 else (s - cumulative[i]) / span
    return [path[i][k] + (path[i + 1][k] - path[i][k]) * f for k in range(3)]


def main():
    name = sys.argv[1]
    route = json.load(open(PATHS + name + "_route.json"))["points"]
    job = json.load(open(PATHS + name + "_move_job.json"))
    points = clean([[p[0], p[1], p[2] + EYE] for p in route])
    path = resample(points)
    sigma = SMOOTH_PATH / STEP
    path = [list(p) for p in zip(*[gauss([p[k] for p in path], sigma) for k in range(3)])]
    cumulative = [0.0]
    for a, b in zip(path[:-1], path[1:]):
        cumulative.append(cumulative[-1] + math.dist(a, b))
    total = cumulative[-1]
    door = [job["door"][0], job["door"][1], job["door"][2] + EYE]
    start = int(len(path) * 0.5)
    door_index = min(range(start, len(path)), key=lambda i: math.dist(path[i], door))
    s_door = cumulative[door_index]

    # speed: v1 inside and v2 outside, eased in at the start, blended around the door, eased out at the end
    seconds = FRAMES / float(FPS)
    t_door = seconds - job.get("outdoor_seconds", 10.0)
    fine = 20  # steps per frame for the integration
    dt = 1.0 / (FPS * fine)
    shape1, shape2 = [], []
    steps = FRAMES * fine
    for n in range(steps):
        t = (n + 0.5) * dt
        ease_in = smoothstep(t / 1.0)
        blend = smoothstep((t - (t_door - 1.0)) / 2.0)
        ease_out = 1.0 - smoothstep((t - (seconds - 2.0)) / 2.0) * 0.85
        shape1.append(ease_in * (1.0 - blend))
        shape2.append(blend * ease_out)
    door_step = int(round(t_door / dt))
    a11, a12 = sum(shape1[:door_step]) * dt, sum(shape2[:door_step]) * dt
    a21, a22 = sum(shape1) * dt, sum(shape2) * dt
    det = a11 * a22 - a12 * a21
    v1 = (s_door * a22 - a12 * total) / det
    v2 = (a11 * total - a21 * s_door) / det
    distance = [0.0]
    for n in range(steps):
        distance.append(distance[-1] + (v1 * shape1[n] + v2 * shape2[n]) * dt)
    s_frames = [min(total, distance[f * fine]) for f in range(FRAMES)]

    locations = [at(path, cumulative, s) for s in s_frames]
    yaws, pitches = [], []
    for s, here in zip(s_frames, locations):
        ahead = at(path, cumulative, s + LOOK_AHEAD)
        dx, dy, dz = ahead[0] - here[0], ahead[1] - here[1], ahead[2] - here[2]
        yaw = math.degrees(math.atan2(dy, dx))
        if yaws:
            while yaw - yaws[-1] > 180.0:
                yaw -= 360.0
            while yaw - yaws[-1] < -180.0:
                yaw += 360.0
        yaws.append(yaw)
        pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy))) * PITCH_SHARE
        pitches.append(max(-PITCH_LIMIT, min(PITCH_LIMIT, pitch)))
    end_look = job.get("end_look")
    if end_look:
        span = job.get("end_look_seconds", 4.0) * FPS
        for f in range(FRAMES):
            w = smoothstep((f - (FRAMES - span)) / (span * 0.75))
            if w <= 0.0:
                continue
            here = locations[f]
            dx, dy, dz = end_look[0] - here[0], end_look[1] - here[1], end_look[2] - here[2]
            yaw = math.degrees(math.atan2(dy, dx))
            while yaw - yaws[f] > 180.0:
                yaw -= 360.0
            while yaw - yaws[f] < -180.0:
                yaw += 360.0
            yaws[f] += (yaw - yaws[f]) * w
            pitch = max(-PITCH_LIMIT, min(PITCH_LIMIT, math.degrees(math.atan2(dz, math.hypot(dx, dy)))))
            pitches[f] += (pitch - pitches[f]) * w
    yaws = gauss(yaws, SMOOTH_TURN * FPS)
    pitches = gauss(pitches, SMOOTH_TURN * FPS)

    low = job.get("low_ev")
    frames = []
    for f in range(FRAMES):
        t = f / float(FPS)
        inside = EV_INSIDE
        if low:
            z = locations[f][2]
            table = sorted(low)
            if z <= table[0][0]:
                inside = table[0][1]
            elif z >= table[-1][0]:
                inside = table[-1][1]
            else:
                for (z0, e0), (z1, e1) in zip(table[:-1], table[1:]):
                    if z0 <= z <= z1:
                        inside = e0 + (e1 - e0) * smoothstep((z - z0) / (z1 - z0))
        w = smoothstep((t - (t_door - EV_BEFORE)) / (EV_BEFORE + EV_AFTER))
        frames.append({"f": f, "loc": [round(v, 2) for v in locations[f]],
                       "rot": [round(pitches[f], 3), round(yaws[f], 3), 0.0],
                       "ev": round(inside + (job.get("outdoor_ev", EV_OUTSIDE) - inside) * w, 3), "s": round(s_frames[f], 1)})
    if low:
        smooth = gauss([fr["ev"] for fr in frames], 0.3 * FPS)
        for fr, ev in zip(frames, smooth):
            fr["ev"] = round(ev, 3)
    turn = max(abs(b["rot"][1] - a["rot"][1]) * FPS for a, b in zip(frames[:-1], frames[1:]))
    step = max(math.dist(a["loc"], b["loc"]) for a, b in zip(frames[:-1], frames[1:]))
    still = sum(1 for a, b in zip(frames[:-1], frames[1:]) if math.dist(a["loc"], b["loc"]) < 0.05 and abs(a["rot"][1] - b["rot"][1]) < 0.002)
    stats = {"route_points": len(route), "kept_points": len(points), "length_m": round(total / 100.0, 2),
             "door_at_m": round(s_door / 100.0, 2), "door_at_s": t_door, "speed_inside_m_s": round(v1 / 100.0, 3),
             "speed_outside_m_s": round(v2 / 100.0, 3), "fastest_turn_deg_s": round(turn, 1),
             "largest_step_cm": round(step, 2), "frame_pairs_without_motion": still,
             "door_frame": min(range(FRAMES), key=lambda f: abs(s_frames[f] - s_door))}
    json.dump({"fps": FPS, "stats": stats, "job": job, "frames": frames}, open(PATHS + name + "_move.json", "w"))
    print(name, json.dumps(stats))


main()
