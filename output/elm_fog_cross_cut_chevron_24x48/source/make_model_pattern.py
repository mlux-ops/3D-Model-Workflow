"""Revit model fill pattern (.pat) for a tile texture, plus an independent check.

Standing user instruction, 2026-09-23: every tile ships with a Revit *model*
pattern whose lines are the grout-joint centrelines of its texture, so the
pattern can be tied to the material (Graphics > Surface Pattern, then Texture
Alignment) and its grout lines grabbed and moved in the model.

Reusable for later tiles: import this module and call write_pat() with
stacked() or running_bond(). Hexagon / herringbone layouts need their own
family function, validated by the same rasteriser (check_against_joints).

PAT line descriptor: angle, x-origin, y-origin, delta-x, delta-y [, dashes...]
(delta-x along the line, delta-y perpendicular to it, in the line's rotated
frame; positive dash = drawn, negative = gap). Units: inches (;%UNITS=INCH).
Pattern Y is up; image rows run down, so image row = (height_in - Y) * ppi.
"""
import json
import math
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw


def _num(v):
    s = ("%.6f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def stacked(w, h):
    """Grid / stack bond: continuous bed and head joints."""
    return [(0.0, 0.0, 0.0, 0.0, h, []), (90.0, 0.0, 0.0, 0.0, w, [])]


def running_bond(w, h, q):
    """Rows offset by w/q (q = 2 half bond, 3 third bond ...)."""
    return [(0.0, 0.0, 0.0, 0.0, h, []), (90.0, 0.0, 0.0, h, w / q, [h, -(q - 1) * h])]


def write_pat(path, name, desc, families, header_notes=()):
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", name):
        raise ValueError("pattern name must be plain ASCII without spaces: " + name)
    lines = [";%UNITS=INCH", ";"]
    lines += ["; " + n for n in header_notes]
    lines += [";", "*%s, %s" % (name, desc), ";%TYPE=MODEL"]
    for ang, x0, y0, dx, dy, dashes in families:
        vals = [ang, x0, y0, dx, dy] + list(dashes)
        lines.append(", ".join(_num(v) for v in vals))
    for ln in lines:
        if len(ln) > 80 or any(ord(ch) > 126 for ch in ln):
            raise ValueError("PAT line too long or non-ASCII: " + ln)
    with open(path, "w", newline="\r\n") as fh:      # CRLF: Windows tools expect it
        fh.write("\n".join(lines) + "\n")
    return lines


def parse_pat(path):
    """Minimal independent reader: returns (units, type, name, desc, families)."""
    units = typ = name = desc = None
    fams = []
    with open(path, "r", encoding="ascii") as fh:
        for raw in fh:
            ln = raw.strip()
            if not ln:
                continue
            m = re.match(r";%UNITS=(\w+)", ln)
            if m:
                units = m.group(1)
                continue
            m = re.match(r";%TYPE=(\w+)", ln)
            if m:
                typ = m.group(1)
                continue
            if ln.startswith(";"):
                continue
            if ln.startswith("*"):
                if name is not None:
                    break                      # first pattern only
                name, _, desc = ln[1:].partition(",")
                name, desc = name.strip(), desc.strip()
                continue
            vals = [float(v) for v in ln.split(",")]
            fams.append((vals[0], vals[1], vals[2], vals[3], vals[4], vals[5:]))
    return units, typ, name, desc, fams


def rasterise(fams, width_in, height_in, ppi, step_in=None):
    """Mark every pixel a pattern line passes through (inches, Y up)."""
    W, H = int(round(width_in * ppi)), int(round(height_in * ppi))
    mask = np.zeros((H, W), bool)
    step = step_in or 0.25 / ppi
    diag = math.hypot(width_in, height_in)
    for ang, x0, y0, dx, dy, dashes in fams:
        a = math.radians(ang)
        d = np.array([math.cos(a), math.sin(a)])
        p = np.array([-math.sin(a), math.cos(a)])
        off = dx * d + dy * p
        period = sum(abs(v) for v in dashes) if dashes else None
        nmax = int(diag / max(abs(dy), 1e-9)) + 4
        t = np.arange(-diag, diag, step)
        for n in range(-nmax, nmax + 1):
            o = np.array([x0, y0]) + n * off
            # keep the line's dash phase anchored at its own origin
            if period:
                ph = np.mod(t, period)
                on = np.zeros_like(t, bool)
                acc = 0.0
                for v in dashes:
                    if v > 0:
                        on |= (ph >= acc) & (ph < acc + v)
                    acc += abs(v)
                tt = t[on]
            else:
                tt = t
            X = o[0] + tt * d[0]
            Y = o[1] + tt * d[1]
            k = (X >= 0) & (X < width_in) & (Y > 0) & (Y <= height_in)
            if not k.any():
                continue
            cols = np.clip((X[k] * ppi).astype(int), 0, W - 1)
            rows = np.clip(((height_in - Y[k]) * ppi).astype(int), 0, H - 1)
            mask[rows, cols] = True
    return mask


def check_against_joints(pat_path, bump_png, width_in, height_in, grout_level=0):
    """Every pattern pixel must lie in a joint; every joint centreline must be drawn."""
    units, typ, name, desc, fams = parse_pat(pat_path)
    b = np.asarray(Image.open(bump_png))
    H, W = b.shape
    ppi = W / width_in
    assert abs(H / height_in - ppi) < 1e-6, "image aspect does not match the stated extent"
    joint = b <= grout_level
    from scipy import ndimage as ndi
    near = ndi.binary_dilation(joint, iterations=1)
    pm = rasterise(fams, width_in, height_in, ppi)
    on_joint = float(near[pm].mean()) if pm.any() else 0.0
    # joint columns / rows must each have a pattern line within 1 px. The window
    # wraps: the last column/row of a seamless atlas is the other half of the
    # joint whose line sits at x = 0 / y = 0.
    colfrac = joint.mean(0)
    rowfrac = joint.mean(1)
    cov = []
    for x in np.where(colfrac > 0.5)[0]:
        win = np.take(pm, [x - 1, x, x + 1], axis=1, mode="wrap")
        cov.append(win.any(1)[joint[:, x]].mean())
    for y in np.where(rowfrac > 0.5)[0]:
        win = np.take(pm, [y - 1, y, y + 1], axis=0, mode="wrap")
        cov.append(win.any(0)[joint[y, :]].mean())
    return {
        "units": units, "type": typ, "name": name, "description": desc, "families": fams,
        "pattern_pixels": int(pm.sum()),
        "pattern_pixels_on_joint_frac": on_joint,
        "joint_lines_found": len(cov),
        "joint_line_coverage_min": float(min(cov)) if cov else 0.0,
        "pass": bool(units == "INCH" and typ == "MODEL" and on_joint > 0.995 and cov and min(cov) > 0.98),
    }, pm


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    prod = os.path.dirname(here)
    sys.path.insert(0, here)
    import chevron_common as cc
    rep = json.load(open(os.path.join(prod, "textures", "build_report.json")))
    w, h = cc.MODULE_IN
    name = "ELM_Fog_CrossCut_Chevron_24x48_Landscape"
    pat = os.path.join(prod, "pattern", name + ".pat")
    os.makedirs(os.path.dirname(pat), exist_ok=True)
    notes = [
        "ELM ElmStone Fog Cross-Cut Chevron, 24 x 48 in, stacked grid",
        "Revit MODEL pattern: grout-joint centrelines of the texture set",
        "ELM_Fog_CrossCut_Chevron_24x48_Color/_Bump16/_Roughness.png",
        "Module 48 x 24 in = 47-15/16 x 23-15/16 in tile + 1/16 in joint",
        "Long side horizontal. Texture Sample Size 12'-0\" x 8'-0\".",
        "Import: Manage > Additional Settings > Fill Patterns > Model >",
        "New > Custom > Import, import scale 1.00.",
    ]
    lines = write_pat(pat, name, "ELM Fog Chevron 48x24 landscape", stacked(w, h), notes)
    print("\n".join(lines))
    # portrait variant: tile long side vertical (as in ELM's own room scene); use with
    # the texture rotated 90 deg in Revit and Sample Size 8'-0" x 12'-0"
    name_p = "ELM_Fog_CrossCut_Chevron_24x48_Portrait"
    pat_p = os.path.join(prod, "pattern", name_p + ".pat")
    notes_p = notes[:3] + ["Portrait: module 24 wide x 48 tall, long side vertical.",
                           "Use with the texture rotated 90 deg, Sample Size 8'-0\" x 12'-0\"."] + notes[5:]
    write_pat(pat_p, name_p, "ELM Fog Chevron 24x48 portrait", stacked(h, w), notes_p)
    W_in, H_in = rep["atlas_in"]
    bump = os.path.join(prod, "textures", "ELM_Fog_CrossCut_Chevron_24x48_Bump16.png")
    res, pm = check_against_joints(pat, bump, W_in, H_in)
    rot = os.path.join(here, "_analysis", "_bump_rot90_check.png")
    Image.fromarray(np.rot90(np.asarray(Image.open(bump)))).save(rot)
    res_p, _ = check_against_joints(pat_p, rot, H_in, W_in)
    os.remove(rot)
    res["families"] = [list(f[:5]) + [list(f[5])] for f in res["families"]]
    res_p["families"] = [list(f[:5]) + [list(f[5])] for f in res_p["families"]]
    with open(os.path.join(prod, "pattern", "pattern_check.json"), "w") as fh:
        json.dump({"landscape": res, "portrait_vs_texture_rotated_90": res_p}, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "families"}, indent=1))
    print("portrait pass:", res_p["pass"], res_p["pattern_pixels_on_joint_frac"], res_p["joint_line_coverage_min"])
    if not res_p["pass"]:
        raise SystemExit("portrait model pattern does not register with the rotated texture joints")
    # overlay preview: pattern lines (red) over the colour map, one atlas + wrap margin
    col = Image.open(os.path.join(prod, "textures", "ELM_Fog_CrossCut_Chevron_24x48_Color.png")).convert("RGB")
    sc = 1800 / col.size[0]
    small = col.resize((1800, int(col.size[1] * sc)), Image.LANCZOS)
    ov = small.copy()
    d = ImageDraw.Draw(ov)
    ys, xs = np.where(pm)
    for x, y in zip((xs * sc).astype(int)[::7], (ys * sc).astype(int)[::7]):
        d.point((x, y), fill=(220, 0, 0))
    ov.save(os.path.join(prod, "pattern", "_PREVIEW_model_pattern_overlay.jpg"), quality=90)
    zoom = col.crop((2048 - 150, 1024 - 100, 2048 + 150, 1024 + 100)).resize((1200, 800), Image.NEAREST)
    dz = ImageDraw.Draw(zoom)
    sub = pm[1024 - 100:1024 + 100, 2048 - 150:2048 + 150]
    for y, x in zip(*np.where(sub)):
        dz.rectangle([x * 4 + 1, y * 4 + 1, x * 4 + 2, y * 4 + 2], fill=(220, 0, 0))
    zoom.save(os.path.join(prod, "pattern", "_REVIEW_model_pattern_joint_zoom.jpg"), quality=90)
    if not res["pass"]:
        raise SystemExit("model pattern does not register with the texture joints")


if __name__ == "__main__":
    main()
