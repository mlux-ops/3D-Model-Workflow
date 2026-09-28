"""Copy the deliverables to the Google Drive for Desktop mount (standing authorisation, AGENTS.md).

Never overwrites: refuses if a same-name file already exists at the destination (unless byte-identical, which is
reported as already delivered). Verifies size and SHA-256 of each copy on the mount and writes _work/delivery.json.
Placement in the sync folder is NOT proof of upload; the Drive API check follows separately."""
import hashlib
import json
import os
import shutil

from guard import RUN_DIR, out_path

MAPS = "F:/My Drive/Revit Material Maps - 25-012 651 Belmont"
PKGS = "F:/My Drive/3D Model Workflow/Material Packages"
S1 = "11'-10.000in x 11'-10.500in"
S2 = "4'-0.000in x 4'-0.000in"
T1, T2 = "ELM Jute Vein-Cut 24x48", "ELM Jute Vein-Cut 1x3 Mosaic"
PLAN = [
    ("veincut_24x48/Color.png", MAPS, "%s - %s.png" % (T1, S1)),
    ("veincut_24x48/Bump16.png", MAPS, "%s - %s - Bump 60.png" % (T1, S1)),
    ("veincut_24x48/ELM_Jute_Vein_Cut_24x48_Model.pat", MAPS, "%s - Model Pattern - %s.pat" % (T1, S1)),
    ("mosaic_1x3/Color.png", MAPS, "%s - %s.png" % (T2, S2)),
    ("mosaic_1x3/Bump16.png", MAPS, "%s - %s - Bump 50.png" % (T2, S2)),
    ("mosaic_1x3/ELM_Jute_Vein_Cut_1x3_Mosaic_Model.pat", MAPS, "%s - Model Pattern - %s.pat" % (T2, S2)),
    ("ELM_Jute_Vein_Cut_24x48_Package.zip", PKGS, "ELM_Jute_Vein_Cut_24x48_Package.zip"),
    ("ELM_Jute_Vein_Cut_1x3_Mosaic_Package.zip", PKGS, "ELM_Jute_Vein_Cut_1x3_Mosaic_Package.zip"),
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    out = []
    for src_rel, dst_dir, name in PLAN:
        src = os.path.join(RUN_DIR, src_rel)
        dst = os.path.join(dst_dir, name)
        s_sha, s_size = sha(src), os.path.getsize(src)
        if not os.path.isdir(dst_dir):
            raise FileNotFoundError(dst_dir)
        if os.path.exists(dst):
            if sha(dst) == s_sha:
                out.append({"file": name, "status": "already present, identical", "bytes": s_size, "sha256": s_sha})
                continue
            raise FileExistsError("refusing to overwrite a different file: %s" % dst)
        shutil.copyfile(src, dst)
        d_sha, d_size = sha(dst), os.path.getsize(dst)
        if (d_sha, d_size) != (s_sha, s_size):
            raise RuntimeError("copy mismatch: %s" % dst)
        out.append({"file": name, "dest": dst_dir, "status": "copied, byte-identical", "bytes": d_size, "sha256": d_sha})
    json.dump(out, open(out_path("_work/delivery.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
