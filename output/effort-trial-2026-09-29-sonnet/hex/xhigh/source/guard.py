"""Write guard: every write in this run goes through these helpers and is refused outside the run folder."""
import os
import time

RUN = os.path.normpath("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/xhigh")
INPUTS = os.path.normpath("E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/hex/inputs")


def safe(path):
    p = os.path.normpath(os.path.abspath(path))
    if os.path.commonpath([p, RUN]) != RUN:
        raise PermissionError("write outside run folder refused: " + p)
    d = os.path.dirname(p)
    os.makedirs(d, exist_ok=True)
    return p


def save_image(img, path, retries=4, **kw):
    """PIL save through the guard, retrying the known errno 22 large-PNG failure."""
    p = safe(path)
    for i in range(retries):
        try:
            img.save(p, **kw)
            return p
        except OSError as e:
            if getattr(e, "errno", None) != 22 or i == retries - 1:
                raise
            time.sleep(0.5)


def save_npy(arr, path):
    import numpy as np
    p = safe(path)
    np.save(p, arr)
    return p


def write_text(path, text):
    p = safe(path)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p


def inp(name):
    return os.path.join(INPUTS, name)
