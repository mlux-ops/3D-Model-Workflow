"""Write guard and shared paths for the max arm of the 2026-09-26 hexagon effort trial.

Every file this build writes goes through out_path(), which refuses any path that
resolves outside the run folder (output/effort-trial-2026-09-26-hex/max/).
Inputs are read-only and live in ../inputs/.
"""

import os
import time

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# inputs sit beside the run folder; HEX_INPUT_DIR overrides it (used only for the
# reproducibility check, which runs a copy of source/ in a scratch folder)
INPUT_DIR = os.environ.get("HEX_INPUT_DIR") or os.path.abspath(os.path.join(RUN_DIR, "..", "inputs"))
RENDER_PATH = os.path.join(INPUT_DIR, "elm_formed_hex_sand_layout_render.webp")
LIFESTYLE_PATH = os.path.join(INPUT_DIR, "elm_formed_hex_sand_lifestyle_angled.webp")


def out_path(*parts):
    """Absolute path inside the run folder; raises if it would escape it."""
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run folder: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def save_image(img, *parts, **kw):
    """PIL save through the guard, with the known errno-22 retry for large PNGs."""
    p = out_path(*parts)
    for attempt in range(4):
        try:
            img.save(p, **kw)
            return p
        except OSError as e:
            if getattr(e, "errno", None) != 22 or attempt == 3:
                raise
            print("  errno 22 on save of %s, retry %d" % (os.path.basename(p), attempt + 1))
            time.sleep(0.5)
    return p


def write_text(text, *parts):
    p = out_path(*parts)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p
