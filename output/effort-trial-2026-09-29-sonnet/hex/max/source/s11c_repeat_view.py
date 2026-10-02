"""Step 11c: side-by-side of a searched window and its best match (colour atlas, both aligned).

python s11c_repeat_view.py <colour|bump> <null|d6> [rank]
Reads work/repetition.json (written by s11b_repetition.py) and writes work/thumbs/repeat_<map>_<group>_<rank>.png
(<= 800 px wide): left the 256 px window after the searched transform, right the matching region."""

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path, save_image, load_gray16  # noqa: E402
from design import FULL_SCALE_MM  # noqa: E402
from s11b_repetition import transform  # noqa: E402

SIZE = 256


def crop(arr, cx, cy):
    ys = (cy - SIZE // 2 + np.arange(SIZE)) % arr.shape[0]
    xs = (cx - SIZE // 2 + np.arange(SIZE)) % arr.shape[1]
    return arr[np.ix_(ys, xs)]


def main():
    which, group = sys.argv[1], sys.argv[2]
    rank = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rep = json.load(open(out_path("work", "repetition.json")))["raw_patch_search_" + ("colour" if which == "colour" else "bump")]
    key = "top4_null_windows" if group == "null" else "top4_windows"
    w = rep[key][rank]
    tk = "null_transform" if group == "null" else "d6_transform"
    mk = "null_match_at_atlas_xy" if group == "null" else "d6_match_at_atlas_xy"
    ncc = w["null_best_ncc"] if group == "null" else w["d6_best_ncc"]
    mir, ang = w[tk]
    if which == "colour":
        arr = np.asarray(Image.open(out_path("textures", "Color.png")).convert("RGB")).astype(np.float32)
    else:
        arr = load_gray16(out_path("textures", "Bump16.png")).astype(np.float32) * (FULL_SCALE_MM / 65535.0)
    a = crop(arr, *w["window_at_atlas_xy"])
    b = crop(arr, *w[mk])
    if a.ndim == 3:
        a = np.stack([transform(a[..., c], mir, float(ang)) for c in range(3)], axis=2)
        lo, hi = 0, 255
    else:
        a = transform(a, mir, float(ang))
        lo, hi = np.percentile(np.concatenate([a.ravel(), b.ravel()]), [1, 99])
    pair = []
    for p in (a, b):
        q = np.clip((p - lo) / (hi - lo + 1e-9), 0, 1) * 255
        if q.ndim == 2:
            q = np.repeat(q[..., None], 3, axis=2)
        pair.append(q.astype(np.uint8))
    im = Image.fromarray(np.hstack(pair))
    im = im.resize((int(im.width * 1.5), int(im.height * 1.5)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.text((4, 4), "face %d window at %s, transform mirror=%d rot=%d, NCC %.3f" % (w["face_index"], w["window_at_atlas_xy"], mir, ang, ncc),
           fill=(255, 0, 0))
    d.text((4, im.height - 14), "best match at %s (right)" % (w[mk],), fill=(255, 0, 0))
    name = "repeat_%s_%s_%d.png" % (which, group, rank)
    save_image(im, "work", "thumbs", name)
    print(name, im.size)


if __name__ == "__main__":
    main()
