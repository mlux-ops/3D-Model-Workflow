"""Local review page for the owner's material decisions (1529 N. Wieland).

Serves owner_review/index.html on http://127.0.0.1:8765 and writes each answer straight into
the place the agents read it:

- material_audit.csv, column `decision` (keep / candidate / rebuild, blank = not decided)
  and column `owner_note` (free text), both in docs/unreal/1529_wieland/;
- owner_review/decisions_log.csv, one appended line per saved answer, with the time.

Standard library only. Listens on 127.0.0.1 only. Run: python -I review_server.py
"""

import csv
import datetime
import http.server
import json
import os
import re
import sys
import tempfile
import threading
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN_DIR = os.path.dirname(HERE)
AUDIT = os.path.join(PLAN_DIR, "material_audit.csv")
ALTERNATIVES = os.path.join(PLAN_DIR, "material_alternatives.csv")
CANDIDATES = os.path.join(PLAN_DIR, "material_candidates.csv")
SHEETS = os.path.join(PLAN_DIR, "review", "phase5", "swatches", "sheets")
LOG = os.path.join(HERE, "decisions_log.csv")
PAGE = os.path.join(HERE, "index.html")

HOST, PORT = "127.0.0.1", 8765
DECISIONS = {"", "keep", "candidate", "rebuild"}
NOTE_MAX = 2000
LOCK = threading.Lock()


def norm(name):
    """Match a material name to a sheet file name; scripts replaced odd characters with '_'."""
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def sheet_index():
    out = {}
    for fn in os.listdir(SHEETS):
        stem, ext = os.path.splitext(fn)
        if ext.lower() in (".jpg", ".jpeg", ".png"):
            out[norm(stem)] = fn
    return out


def load_materials():
    _, rows = read_csv(AUDIT)
    _, alts = read_csv(ALTERNATIVES)
    _, cands = read_csv(CANDIDATES)
    alt_by = {r["material"]: r for r in alts}
    cand_by = {r["material"]: r for r in cands}
    sheets = sheet_index()
    out = []
    for r in rows:
        name = r["material"]
        c = cand_by.get(name, {})
        out.append({
            "material": name,
            "family": r.get("family", ""),
            "confidence": int(r["confidence"]) if r.get("confidence", "").isdigit() else None,
            "reason": r.get("confidence_reason", ""),
            "objects": r.get("objects_using_it", ""),
            "categories": r.get("categories", ""),
            "decision": r.get("decision", ""),
            "note": r.get("owner_note", ""),
            "has_candidate": name in alt_by,
            "candidate_rests_on": c.get("what_it_rests_on", ""),
            "candidate_for_owner": c.get("for_the_owner", ""),
            "sheet": sheets.get(norm(name), ""),
        })
    return out


def save_decision(material, decision, note):
    if decision not in DECISIONS:
        raise ValueError("decision must be keep, candidate, rebuild or blank")
    note = note.replace("\r", " ").replace("\n", " ").strip()[:NOTE_MAX]
    with LOCK:
        fields, rows = read_csv(AUDIT)
        if "owner_note" not in fields:
            fields = fields + ["owner_note"]
        hit = [r for r in rows if r["material"] == material]
        if len(hit) != 1:
            raise KeyError("unknown material: " + material)
        _, alts = read_csv(ALTERNATIVES)
        if decision == "candidate" and material not in {a["material"] for a in alts}:
            raise ValueError("this material has no Unreal candidate; choose keep or rebuild")
        hit[0]["decision"] = decision
        hit[0]["owner_note"] = note
        fd, tmp = tempfile.mkstemp(dir=PLAN_DIR, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in fields})
        os.replace(tmp, AUDIT)
        new_log = not os.path.exists(LOG)
        with open(LOG, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            if new_log:
                w.writerow(["time", "material", "decision", "owner_note"])
            w.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), material, decision, note])


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
        if path == "/api/materials":
            return self._json(200, {"materials": load_materials(), "audit_file": AUDIT})
        if path.startswith("/sheet/"):
            wanted = urllib.parse.unquote(path[len("/sheet/"):])
            allowed = set(sheet_index().values())
            if wanted not in allowed:  # only exact sheet file names, no paths
                return self._send(404, "not found", "text/plain")
            ctype = "image/png" if wanted.lower().endswith(".png") else "image/jpeg"
            with open(os.path.join(SHEETS, wanted), "rb") as f:
                return self._send(200, f.read(), ctype)
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/api/decision":
            return self._send(404, "not found", "text/plain")
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 10000:
                raise ValueError("bad request size")
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            save_decision(str(body["material"]), str(body.get("decision", "")), str(body.get("note", "")))
            self._json(200, {"ok": True})
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            self._json(400, {"ok": False, "error": str(e)})
        except OSError as e:
            self._json(500, {"ok": False, "error": "could not write the file: " + str(e)})

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), fmt % args))


if __name__ == "__main__":
    srv = http.server.ThreadingHTTPServer((HOST, PORT), Handler)
    print("Material review running at http://%s:%d  (writes to %s)" % (HOST, PORT, AUDIT), flush=True)
    srv.serve_forever()
