"""Phase 19, step 19.4: the delivery revision on D: and on Google Drive, checked by size and SHA-256.

Usage: python -B -P phase19_package.py <package name> [--dry-run]

Builds D:/Wieland1529_delivery/package/<name>/ from the project's newest pictures, videos and notes (FILES below),
writes MANIFEST_SHA256.txt (size and SHA-256 of every file), copies the folder to Google Drive
(F:/My Drive/Folders/3D Model Workflow/3D Models/<name>/), reads every copied file back and compares size and SHA-256,
and puts a SUPERSEDED.md note into the earlier package's folder in both places. Nothing is deleted or overwritten:
a file that already exists with the same checksum is left; one that exists with a different checksum stops the run.
"""

import glob
import hashlib
import json
import os
import shutil
import sys

DOCS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace(os.sep, "/")
D_ROOT = "D:/Wieland1529_delivery/package"
G_ROOT = "F:/My Drive/Folders/3D Model Workflow/3D Models"
EARLIER = "1529_Wieland_UE5.9_Delivery_2026-11-14"
VIEWS = ["S1", "S2", "S3", "S4", "S5", "S6", "S9", "D1", "D2", "D3", "D4", "D5"]


def files():
    """(source, destination relative to the package)"""
    out = [(DOCS + "/delivery/DELIVERY_NOTES_2026-11-14_r2.md", "DELIVERY_NOTES.md"),
           (DOCS + "/owner_review/paths/RENDER_HOW.md", "RENDER_HOW.md"),
           (D_ROOT + "/" + EARLIER + "/LICENCES.csv", "LICENCES.csv")]
    for v in VIEWS:
        out.append((DOCS + "/review/phase20/stills/%s_realtime.0000.png" % v, "stills/%s_realtime.png" % v))
        out.append((DOCS + "/review/phase17/stills/compare_%s_realtime.jpg" % v, "comparison/p11_vs_p17_%s.jpg" % v))
        out.append((DOCS + "/review/phase20/stills/compare_%s_realtime.jpg" % v, "comparison/p17_vs_p20_%s.jpg" % v))
    out.append((DOCS + "/review/phase20/stills/D1_pathtraced.0000.png", "stills/D1_pathtraced.png"))
    out.append((DOCS + "/review/phase17/stills/compare_D1_pathtraced.jpg", "comparison/p11_vs_p17_D1_pathtraced.jpg"))
    out.append((DOCS + "/review/phase20/stills/compare_D1_pathtraced.jpg", "comparison/p17_vs_p20_D1_pathtraced.jpg"))
    for deck in ("D1S", "D1"):
        out.append((DOCS + "/review/phase20/panorama/%s_panorama_sheet_p20.png" % deck, "skyline/%s_skyline_labelled.png" % deck))
        out.append((DOCS + "/review/phase20/panorama/%s_panorama_sheet_p20_labels.json" % deck, "skyline/%s_skyline_labels.json" % deck))
        out.append((DOCS + "/review/phase20/panorama/compare_%s_p17_p20.jpg" % deck, "comparison/skyline_p17_vs_p20_%s.jpg" % deck))
    for f in sorted(glob.glob(DOCS + "/delivery/video_paths/*.mp4")) + sorted(glob.glob(DOCS + "/delivery/video_paths/*.json")):
        out.append((f.replace(os.sep, "/"), "video_paths/" + os.path.basename(f)))
    return out


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def put(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    s = sha(src)
    if os.path.exists(dst):
        if sha(dst) != s:
            raise RuntimeError("exists with other content, not overwritten: " + dst)
        return s, "kept"
    shutil.copy2(src, dst)
    if sha(dst) != s or os.path.getsize(dst) != os.path.getsize(src):
        raise RuntimeError("copy does not match: " + dst)
    return s, "copied"


def superseded_note(folder, name):
    path = folder + "/SUPERSEDED.md"
    if os.path.exists(path):
        return "kept"
    text = ("# Superseded\n\nThis package (%s) is superseded by **%s** (same folder level), made later on 2026-11-14.\n\n"
            "What the newer revision replaces: the surroundings and the downtown skyline (rebuilt from the 2022 Illinois laser "
            "scan, Phase 17, materials refined from photographs, Phase 20), the stills of every station and design view, and "
            "the walking-path videos (Phase 19).\n\nWhat stays valid here until it is made again: the packaged build (the "
            "walk-through program), the 60-second animation and the build's profile. They show the earlier surroundings "
            "(generic far-city blocks and the earlier neighbour massing).\n\nNothing in this folder was changed or deleted; "
            "only this note was added.\n" % (EARLIER, name))
    with open(path, "w", encoding="utf-8", newline="\n") as h:
        h.write(text)
    return "written"


def main(argv):
    name = argv[1]
    dry = "--dry-run" in argv
    plan = files()
    missing = [s for s, _ in plan if not os.path.exists(s)]
    if missing:
        print(json.dumps({"missing": missing}, indent=1))
        return 2
    if dry:
        print(json.dumps({"files": len(plan), "megabytes": round(sum(os.path.getsize(s) for s, _ in plan) / 1e6, 1)}))
        return 0
    d_dir, g_dir = D_ROOT + "/" + name, G_ROOT + "/" + name
    rows = []
    for src, rel in plan:
        s, how = put(src, d_dir + "/" + rel)
        rows.append((rel, os.path.getsize(src), s, how))
    manifest = d_dir + "/MANIFEST_SHA256.txt"
    with open(manifest, "w", encoding="utf-8", newline="\n") as h:
        h.write("# %s: size in bytes and SHA-256 of every file (this manifest itself excepted)\n" % name)
        for rel, size, s, _ in rows:
            h.write("%s  %12d  %s\n" % (s, size, rel))
    checked = 0
    for rel, size, s, _ in rows + [("MANIFEST_SHA256.txt", os.path.getsize(manifest), sha(manifest), "")]:
        s2, how = put(d_dir + "/" + rel, g_dir + "/" + rel)
        g = g_dir + "/" + rel
        if os.path.getsize(g) != os.path.getsize(d_dir + "/" + rel) or sha(g) != s2:
            raise RuntimeError("Drive copy does not match: " + g)
        checked += 1
    notes = {"D": superseded_note(D_ROOT + "/" + EARLIER, name), "Drive": superseded_note(G_ROOT + "/" + EARLIER, name)}
    total = sum(r[1] for r in rows)
    print(json.dumps({"package": name, "files": len(rows) + 1, "megabytes": round(total / 1e6, 1), "drive_checked": checked,
                      "superseded_notes": notes, "D": d_dir, "Drive": g_dir}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
