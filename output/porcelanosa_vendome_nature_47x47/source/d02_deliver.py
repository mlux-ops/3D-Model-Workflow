"""Copy the deliverables to the Google Drive for Desktop mount (standing authorisation, AGENTS.md).

Never overwrites: refuses if a same-name file already exists at the destination (unless byte-identical, which is
reported as already delivered). Verifies size and SHA-256 of each copy on the mount and writes _work/delivery.json.
Placement in the sync folder is NOT proof of upload; the Drive API check follows separately.
Usage: python d02_deliver.py [--maps-only | --zip-only]"""
import hashlib
import json
import os
import shutil
import sys

from guard import RUN_DIR, out_path

MAPS = "F:/My Drive/Revit Material Maps - 25-012 651 Belmont"
PKGS = "F:/My Drive/3D Model Workflow/Material Packages"
T = "Porcelanosa Vendome Nature 47x47"
SD, SF, SP = "15'-9.000in x 7'-10.500in", "15'-9.000in x 15'-9.000in", "3'-11.250in x 3'-11.250in"
BUMP = 60
MAP_PLAN = [
    ("designed/Color.png", MAPS, "%s - Designed - %s.png" % (T, SD)),
    ("designed/Bump16.png", MAPS, "%s - Designed - %s - Bump %d.png" % (T, SD, BUMP)),
    ("free_mix/Color.png", MAPS, "%s - Free Mix - %s.png" % (T, SF)),
    ("free_mix/Bump16.png", MAPS, "%s - Free Mix - %s - Bump %d.png" % (T, SF, BUMP)),
] + [x for k in range(1, 9) for x in (
    ("pieces/Piece_%d_Color.png" % k, MAPS, "%s - Piece %d - %s.png" % (T, k, SP)),
    ("pieces/Piece_%d_Bump16.png" % k, MAPS, "%s - Piece %d - %s - Bump %d.png" % (T, k, SP, BUMP)))] + [
    ("_work/Porcelanosa_Vendome_Nature_47x47_Model.pat", MAPS, "%s - Model Pattern - 3'-11.250in.pat" % T),
]
ZIP_PLAN = [("Porcelanosa_Vendome_Nature_47x47_Package.zip", PKGS, "Porcelanosa_Vendome_Nature_47x47_Package.zip")]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    plan = MAP_PLAN if "--maps-only" in sys.argv else ZIP_PLAN if "--zip-only" in sys.argv else MAP_PLAN + ZIP_PLAN
    logp = out_path("_work/delivery.json")
    out = json.load(open(logp)) if os.path.exists(logp) else []
    for src_rel, dst_dir, name in plan:
        src = os.path.join(RUN_DIR, src_rel)
        dst = os.path.join(dst_dir, name)
        s_sha, s_size = sha(src), os.path.getsize(src)
        if not os.path.isdir(dst_dir):
            raise FileNotFoundError(dst_dir)
        if os.path.exists(dst):
            if sha(dst) == s_sha:
                out.append({"file": name, "dest": dst_dir, "status": "already present, identical", "bytes": s_size, "sha256": s_sha})
                continue
            raise FileExistsError("refusing to overwrite a different file: %s" % dst)
        shutil.copyfile(src, dst)
        d_sha, d_size = sha(dst), os.path.getsize(dst)
        if (d_sha, d_size) != (s_sha, s_size):
            raise RuntimeError("copy mismatch: %s" % dst)
        out.append({"file": name, "dest": dst_dir, "status": "copied, byte-identical", "bytes": d_size, "sha256": d_sha})
    json.dump(out, open(logp, "w"), indent=1)
    for o in out:
        print(o["bytes"], o["status"], o["file"])


if __name__ == "__main__":
    main()
