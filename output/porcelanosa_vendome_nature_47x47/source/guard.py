"""Write guard: every output of this build must land inside output/porcelanosa_vendome_nature_47x47."""
import os

RUN_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT_DIR = os.path.join(RUN_DIR, "references")


def out_path(rel):
    p = os.path.normpath(os.path.join(RUN_DIR, rel))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise PermissionError("write outside run dir refused: %s" % p)
    if os.path.commonpath([p, INPUT_DIR]) == INPUT_DIR and os.path.exists(p) and not os.access(p, os.W_OK):
        raise PermissionError("reference file is read-only: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def ref(name):
    return os.path.join(INPUT_DIR, name)
