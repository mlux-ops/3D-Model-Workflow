"""Write guard: every output of this build must land inside output/msi_soreno_ivory_24x48."""
import os

RUN_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT_DIR = os.path.join(RUN_DIR, "references")


def out_path(rel):
    p = os.path.normpath(os.path.join(RUN_DIR, rel))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise PermissionError("write outside run dir refused: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def ref(name):
    return os.path.join(INPUT_DIR, name)
