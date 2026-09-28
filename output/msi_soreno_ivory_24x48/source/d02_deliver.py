"""Copy the deliverables to the Google Drive for Desktop mount (standing authorisation, AGENTS.md).

Never overwrites: refuses if a same-name file already exists at the destination (unless it is byte-identical,
in which case it is reported as already delivered). Verifies size and SHA-256 of each copy on the mount and
writes _work/delivery.json. Placement in the sync folder is NOT proof of upload; the Drive API check follows.
"""
import hashlib
import json
import os
import shutil

from guard import RUN_DIR, out_path

SIZE = "11'-10.000in x 11'-10.500in"
MAPS = "F:/My Drive/Revit Material Maps - 25-012 651 Belmont"
PKGS = "F:/My Drive/3D Model Workflow/Material Packages"
PLAN = [
    ("textures/Color.png", MAPS, "MSI Soreno Ivory 24x48 - %s.png" % SIZE),
    ("textures/Bump16.png", MAPS, "MSI Soreno Ivory 24x48 - %s - Bump 60.png" % SIZE),
    ("textures/MSI_Soreno_Ivory_24x48_Model.pat", MAPS, "MSI Soreno Ivory 24x48 - Model Pattern - %s.pat" % SIZE),
    ("MSI_Soreno_Ivory_24x48_Package.zip", PKGS, "MSI_Soreno_Ivory_24x48_Package.zip"),
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
        out.append({"file": name, "dest": dst_dir, "status": "copied", "bytes": d_size, "sha256": d_sha})
    json.dump(out, open(out_path("_work/delivery.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
