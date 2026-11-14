"""Local page for drawing walk-through paths (1529 N. Wieland, Phases 18 and 19).

Serves index.html on http://127.0.0.1:8766 and reads/writes, in this folder:
- plans/manifest.json and the plan images (written by the Phase 18 agent; read only here);
- <name>.json, one per path (the Phase 19 path tool turns each into a video);
- RENDER_REQUEST, written when the owner presses "Request videos" (the watcher reacts to it);
- last_render.json, written by the path tool (read only here).
Deleted paths are moved to _trash/, never removed.

Standard library only. Listens on 127.0.0.1 only. Run: python -I path_server.py
"""

import datetime
import http.server
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
PLANS = os.path.join(HERE, "plans")
MANIFEST = os.path.join(PLANS, "manifest.json")
PAGE = os.path.join(HERE, "index.html")
TRASH = os.path.join(HERE, "_trash")
REQUEST = os.path.join(HERE, "RENDER_REQUEST")
LAST_RENDER = os.path.join(HERE, "last_render.json")
HOST, PORT = "127.0.0.1", 8766
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _-]{0,59}$")
MAX_BODY = 200_000
MAX_POINTS = 500
LOCK = threading.Lock()


def file_for(name):
    if not NAME_RE.match(name):
        raise ValueError("path names use letters, digits, spaces, hyphens and underscores only (up to 60)")
    return os.path.join(HERE, name.strip() + ".json")


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def write_json_atomic(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)


def manifest():
    m = read_json(MANIFEST)
    if not m or not isinstance(m.get("plans"), list):
        return {"plans": [], "missing": True}
    return m


def num(v, lo, hi, field):
    if not isinstance(v, (int, float)) or v != v or v < lo or v > hi:
        raise ValueError("%s must be a number between %s and %s" % (field, lo, hi))
    return float(v)


def clean_path(body):
    """Validate a path sent by the page and return the object to store."""
    name = str(body.get("name", "")).strip()
    file_for(name)
    plan_ids = {p["id"] for p in manifest()["plans"]}
    pts = body.get("points")
    if not isinstance(pts, list) or len(pts) < 2 or len(pts) > MAX_POINTS:
        raise ValueError("a path needs 2 to %d points" % MAX_POINTS)
    out_pts = []
    for i, p in enumerate(pts):
        if not isinstance(p, dict) or p.get("plan") not in plan_ids:
            raise ValueError("point %d is on an unknown plan" % (i + 1))
        q = {"plan": p["plan"],
             "x_cm": num(p.get("x_cm"), -1e7, 1e7, "x"), "y_cm": num(p.get("y_cm"), -1e7, 1e7, "y"),
             "z_cm": num(p.get("z_cm"), -1e6, 1e6, "z"),
             "pause_s": num(p.get("pause_s", 0), 0, 60, "pause")}
        seg = p.get("segment", "walk")
        if seg not in ("walk", "stair", "lift"):
            raise ValueError("point %d: segment must be walk, stair or lift" % (i + 1))
        if seg != "walk":
            q["segment"] = seg
        look = p.get("look") or {"mode": "forward"}
        mode = look.get("mode")
        if mode == "forward":
            q["look"] = {"mode": "forward"}
        elif mode == "target":
            q["look"] = {"mode": "target", "x_cm": num(look.get("x_cm"), -1e7, 1e7, "target x"),
                         "y_cm": num(look.get("y_cm"), -1e7, 1e7, "target y"),
                         "z_cm": num(look.get("z_cm"), -1e6, 1e6, "target z")}
        elif mode == "yaw":
            q["look"] = {"mode": "yaw", "yaw_deg": num(look.get("yaw_deg"), -360, 360, "yaw"),
                         "pitch_deg": num(look.get("pitch_deg", 0), -60, 60, "pitch")}
        else:
            raise ValueError("point %d: look mode must be forward, target or yaw" % (i + 1))
        out_pts.append(q)
    res = body.get("resolution", [1920, 1080])
    if res not in ([1920, 1080], [2560, 1440], [3840, 2160]):
        raise ValueError("resolution must be 1920x1080, 2560x1440 or 3840x2160")
    quality = body.get("quality", "realtime")
    if quality not in ("realtime", "pathtraced"):
        raise ValueError("quality must be realtime or pathtraced")
    fps = body.get("fps", 30)
    if fps not in (24, 30, 60):
        raise ValueError("fps must be 24, 30 or 60")
    old = read_json(file_for(name), {}) or {}
    return {"name": name, "version": 1,
            "speed_m_per_s": num(body.get("speed_m_per_s", 1.2), 0.2, 5, "speed"),
            "fps": fps, "resolution": res, "quality": quality, "points": out_pts,
            "render_requested_at": old.get("render_requested_at"),
            "saved_at": datetime.datetime.now().isoformat(timespec="seconds")}


def list_paths():
    out = []
    for fn in sorted(os.listdir(HERE)):
        if fn.endswith(".json") and not fn.startswith("_") and fn not in ("last_render.json",):
            d = read_json(os.path.join(HERE, fn), {}) or {}
            if isinstance(d.get("points"), list):
                out.append({"name": d.get("name", fn[:-5]), "points": len(d["points"]),
                            "saved_at": d.get("saved_at"), "render_requested_at": d.get("render_requested_at")})
    return out


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj), "application/json; charset=utf-8")

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(PAGE, "rb") as f:
                return self._send(200, f.read(), "text/html; charset=utf-8")
        if path == "/api/plans":
            return self._json(200, manifest())
        if path == "/api/paths":
            return self._json(200, {"paths": list_paths(), "last_render": read_json(LAST_RENDER),
                                    "request_pending": os.path.exists(REQUEST)})
        if path.startswith("/api/path/"):
            name = urllib.parse.unquote(path[len("/api/path/"):])
            try:
                d = read_json(file_for(name))
            except ValueError as e:
                return self._json(400, {"ok": False, "error": str(e)})
            return self._json(200, d) if d else self._json(404, {"ok": False, "error": "no such path"})
        if path.startswith("/plan/"):
            wanted = urllib.parse.unquote(path[len("/plan/"):])
            allowed = {p.get("image") for p in manifest()["plans"]}
            if wanted not in allowed or "/" in wanted or "\\" in wanted:
                return self._send(404, "not found", "text/plain")
            ctype = "image/png" if wanted.lower().endswith(".png") else "image/jpeg"
            with open(os.path.join(PLANS, wanted), "rb") as f:
                return self._send(200, f.read(), ctype)
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        ctype = self.headers.get("Content-Type", "")
        host = self.headers.get("Host", "")
        if not ctype.lower().startswith("application/json") or host not in ("127.0.0.1:%d" % PORT, "localhost:%d" % PORT):
            return self._json(403, {"ok": False, "error": "refused: not from the path page"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("bad request size")
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            route = urllib.parse.urlparse(self.path).path
            with LOCK:
                if route == "/api/save":
                    obj = clean_path(body)
                    write_json_atomic(file_for(obj["name"]), obj)
                    return self._json(200, {"ok": True, "saved_at": obj["saved_at"]})
                if route == "/api/delete":
                    src = file_for(str(body.get("name", "")).strip())
                    if not os.path.exists(src):
                        raise ValueError("no such path")
                    os.makedirs(TRASH, exist_ok=True)
                    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.move(src, os.path.join(TRASH, os.path.basename(src)[:-5] + "_" + stamp + ".json"))
                    return self._json(200, {"ok": True})
                if route == "/api/request":
                    names = body.get("names")
                    if not isinstance(names, list) or not names:
                        raise ValueError("choose at least one path")
                    now = datetime.datetime.now().isoformat(timespec="seconds")
                    for n in names:
                        f = file_for(str(n).strip())
                        d = read_json(f)
                        if not d:
                            raise ValueError("no such path: %s" % n)
                        d["render_requested_at"] = now
                        write_json_atomic(f, d)
                    write_json_atomic(REQUEST, {"requested_at": now, "names": [str(n).strip() for n in names]})
                    return self._json(200, {"ok": True, "requested_at": now})
            return self._json(404, {"ok": False, "error": "unknown action"})
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
            self._json(400, {"ok": False, "error": str(e)})
        except OSError as e:
            self._json(500, {"ok": False, "error": "could not write the file: " + str(e)})

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), fmt % args))


if __name__ == "__main__":
    os.makedirs(PLANS, exist_ok=True)
    srv = http.server.ThreadingHTTPServer((HOST, PORT), Handler)
    print("Path editor running at http://%s:%d" % (HOST, PORT), flush=True)
    srv.serve_forever()
