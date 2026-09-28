"""Write guard: every file written by the build scripts goes through here.

Refuses any path that resolves outside the xhigh run folder.
"""
import os
import time

RUN_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT_DIR = os.path.realpath(os.path.join(RUN_DIR, "..", "inputs"))
TEX_DIR = os.path.join(RUN_DIR, "textures")
WORK_DIR = os.path.join(RUN_DIR, "_work")


def safe(path):
    """Return an absolute path inside RUN_DIR or raise."""
    p = os.path.realpath(os.path.abspath(path))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise PermissionError("write refused, outside run folder: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def save_image(img, path, retries=3, **kw):
    """PIL save through the guard; retries the known errno-22 OSError quirk."""
    p = safe(path)
    for attempt in range(retries):
        try:
            img.save(p, **kw)
            return p
        except OSError as e:
            if getattr(e, "errno", None) == 22 and attempt < retries - 1:
                print("  save retry after errno 22:", p)
                time.sleep(0.5)
                continue
            raise


def write_text(path, text):
    p = safe(path)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p


def inp(name):
    return os.path.join(INPUT_DIR, name)
