"""Audit of the final Raw quilt (what the README may claim about reuse).

From the final label maps (visible pixels only: need mask, primary label) it counts, per
source pixel in the source face's own frame:
  - uses within one atlas face (same-face repeats),
  - uses across faces and whether any two uses are related by an exact hexagon symmetry
    (which a symmetry-aware search could detect) or differ by a non-symmetry rotation,
  - whether any reuse lands in neighbouring atlas faces,
and checks the Matte low-band reuse rule (rotation >= 120 deg apart, other mirror state).
Writes _work/quilt_audit.json.
"""

import json
import sys

import numpy as np

from common import out_path
from b02_layout import neighbours
from b03_quilt_raw import orientations, build_versions, is_hex_symmetry


def main():
    src = json.load(open(out_path("_work", "sources.json")))
    lay = json.load(open(out_path("_work", "layout.json")))
    meta = json.load(open(out_path("_work", "raw_quilt.json")))
    q = np.load(out_path("_work", "raw_quilt.npz"))
    rel = np.load(out_path("_work", "src_rel.npy")).astype(np.float64)
    owner = np.load(out_path("_work", "src_owner.npy"))
    clean = np.load(out_path("_work", "src_clean.npy"))
    ors = orientations()
    faces, versions, N = build_versions(src, rel, owner, clean, ors)
    vkey = {(v["src"], v["tau"], v["jit"]): v for v in versions}
    uses = {}          # (src, idx) -> list of (face, orientation index)
    same_face_dup = 0
    total_px = 0
    for k, fm in meta["faces"].items():
        k = int(k)
        L1 = q["L1_%d" % k]
        G_h, G_w = fm["G"]
        gy, gx = np.mgrid[0:G_h, 0:G_w]
        from common import hex_edge_distance_local
        e = hex_edge_distance_local(gx + 0.5 - G_w / 2.0, gy + 0.5 - G_h / 2.0, 5.0 * src["ppi_render"])
        need = e >= 0
        yy, xx = np.nonzero(need)
        seen = {}
        for pid in np.unique(L1[yy, xx]):
            p = fm["patches"][pid]
            v = vkey[(p["src"], p["tau"], p["jit"])]
            sel = L1[yy, xx] == pid
            ay = yy[sel] - p["py0"] + p["ay"]
            ax = xx[sel] - p["px0"] + p["ax"]
            idx = v["idx"][ay, ax]
            idx = idx[idx >= 0]
            for ii in np.unique(idx):          # unique within a patch: resampling repeats ignored
                key = (p["src"], int(ii))
                if key in seen and seen[key] != pid:
                    same_face_dup += 1         # same source pixel shown by two different patches
                seen[key] = pid
                uses.setdefault(key, []).append((k, v["oi"]))
            total_px += len(np.unique(idx))
    nb = {}
    for c in lay["cells"]:
        nb[c["index"]] = {cc["index"] for cc in lay["cells"] if (cc["i"], cc["j"]) in neighbours(c["i"], c["j"])}
    multi = [u for u in uses.values() if len({f for f, _ in u}) > 1]
    hexrel = 0
    nbr = 0
    for u in multi:
        bad = False
        for a in range(len(u)):
            for b in range(a + 1, len(u)):
                if u[a][0] == u[b][0]:
                    continue
                D = ors[u[a][1]][2].T @ ors[u[b][1]][2]
                if is_hex_symmetry(D):
                    bad = True
                if u[b][0] in nb[u[a][0]]:
                    nbr += 1
        hexrel += bad
    out = {"source_pixels_used": len(uses), "visible_samples": total_px,
           "same_face_duplicate_source_pixels": same_face_dup,
           "source_pixels_in_more_than_one_face": len(multi),
           "of_which_any_two_uses_related_by_exact_hex_symmetry": hexrel,
           "share_hex_related_of_reused": hexrel / max(1, len(multi)),
           "reuse_pairs_in_neighbouring_faces": nbr}
    # matte low-band reuse rule
    m = [c for c in lay["cells"] if c["type"] == "matte"]
    by = {}
    for c in m:
        by.setdefault(c["low_src"], []).append(c)
    viol = []
    for s, cs in by.items():
        if len(cs) == 2:
            a, b = cs
            d = abs(a["low_rot"] - b["low_rot"]) % 360
            d = min(d, 360 - d)
            if d < 120 or a["low_mirror"] == b["low_mirror"]:
                viol.append((s, a["index"], b["index"], d, a["low_mirror"], b["low_mirror"]))
    out["matte_low_band_reused_sources"] = sum(1 for cs in by.values() if len(cs) == 2)
    out["matte_low_band_rule_violations"] = viol
    print(json.dumps(out, indent=1))
    json.dump(out, open(out_path("_work", "quilt_audit.json"), "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
