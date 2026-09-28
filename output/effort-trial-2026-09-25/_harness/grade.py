"""Objective grading and cost extraction for the 2026-09-25 effort trial.

Usage: python grade.py            -> writes grade_report.json next to this file and prints a summary.
Compares the high and xhigh arms, plus the previously accepted atlas as a reference point.
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(TRIAL, "..", ".."))
TRANSCRIPTS = os.path.expanduser(r"~/.claude/projects/E--Claude-3D-Model-Workflow")

EXPECTED_SIZE = (9228, 4620)
GRID = (3, 3)
JOINT_RGB = np.array([209, 209, 209], dtype=np.float32)
JOINT_TOL = 6.0

ATLASES = {
    "high": os.path.join(TRIAL, "high", "textures", "Color.png"),
    "xhigh": os.path.join(TRIAL, "xhigh", "textures", "Color.png"),
    "accepted_reference": os.path.join(REPO, "output", "belmont_tiles", "ElmStone_Jute_CrossCut_24x48", "textures", "Color.png"),
}


def joint_lines(arr, axis):
    """Indices of full rows/columns whose pixels are all within JOINT_TOL of the joint colour."""
    dev = np.abs(arr.astype(np.float32) - JOINT_RGB).max(axis=2)
    within = dev <= JOINT_TOL
    frac = within.mean(axis=axis)  # axis=0 -> per column, axis=1 -> per row
    return np.where(frac > 0.98)[0].tolist()


def runs(idx):
    out = []
    for i in idx:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [(a, b, b - a + 1) for a, b in out]


def wrap_steps(arr):
    a = arr.astype(np.float32)
    lr = np.abs(a[:, 0] - a[:, -1]).mean()
    tb = np.abs(a[0, :] - a[-1, :]).mean()
    interior_x = np.abs(np.diff(a[:, 1:-1], axis=1)).mean()
    interior_y = np.abs(np.diff(a[1:-1, :], axis=0)).mean()
    return {"lr": round(float(lr), 3), "tb": round(float(tb), 3),
            "interior_x": round(float(interior_x), 3), "interior_y": round(float(interior_y), 3)}


def cell_stack(arr, margin=12, size=(384, 192)):
    """Nine cells, joint margin removed, grey, downsampled, high-passed, unit-normalised."""
    h, w = arr.shape[:2]
    ch, cw = h // GRID[1], w // GRID[0]
    cells = []
    for r in range(GRID[1]):
        for c in range(GRID[0]):
            crop = arr[r * ch + margin:(r + 1) * ch - margin, c * cw + margin:(c + 1) * cw - margin]
            g = Image.fromarray(crop).convert("L").resize(size, Image.BILINEAR)
            g = np.asarray(g, dtype=np.float32)
            blur = np.asarray(Image.fromarray(g.astype(np.uint8)).resize((size[0] // 16, size[1] // 16), Image.BILINEAR)
                              .resize(size, Image.BILINEAR), dtype=np.float32)
            hp = g - blur
            hp -= hp.mean()
            n = np.linalg.norm(hp)
            cells.append(hp / n if n > 0 else hp)
    return cells


def max_circular_ncc(a, b):
    """Max normalised circular cross-correlation over all shifts (catches rolled copies)."""
    fa, fb = np.fft.rfft2(a), np.fft.rfft2(b)
    return float(np.fft.irfft2(fa * np.conj(fb), s=a.shape).max())


def repetition(arr):
    cells = cell_stack(arr)
    pairs = []
    for i in range(9):
        for j in range(i + 1, 9):
            best = 0.0
            for flip in (lambda x: x, np.fliplr, np.flipud, lambda x: np.flipud(np.fliplr(x))):
                best = max(best, max_circular_ncc(cells[i], flip(cells[j])))
            pairs.append({"cells": [i, j], "max_ncc": round(best, 3)})
    pairs.sort(key=lambda p: -p["max_ncc"])
    vals = [p["max_ncc"] for p in pairs]
    return {"max_pair": pairs[0], "top3": pairs[:3], "median_pair_ncc": round(float(np.median(vals)), 3),
            "pairs_over_0.5": sum(v > 0.5 for v in vals)}


def grade_atlas(path):
    if not os.path.exists(path):
        return {"present": False}
    im = Image.open(path)
    info = {"present": True, "size": list(im.size), "mode": im.mode, "size_ok": im.size == EXPECTED_SIZE,
            "mode_ok": im.mode == "RGB", "bytes": os.path.getsize(path)}
    arr = np.asarray(im.convert("RGB"))
    info["joint_columns"] = runs(joint_lines(arr, axis=0))
    info["joint_rows"] = runs(joint_lines(arr, axis=1))
    info["wrap"] = wrap_steps(arr)
    info["repetition"] = repetition(arr)
    return info


def arm_session(arm):
    """Find the headless transcript for an arm and summarise its token use."""
    res_path = os.path.join(HERE, f"result-{arm}.json")
    result = None
    if os.path.exists(res_path) and os.path.getsize(res_path) > 0:
        try:
            result = json.load(open(res_path, encoding="utf-8"))
        except json.JSONDecodeError:
            result = None
    sid = result.get("session_id") if result else None
    tpath = os.path.join(TRANSCRIPTS, f"{sid}.jsonl") if sid else None
    if not tpath or not os.path.exists(tpath):
        marker = f"effort-trial-2026-09-25/{arm}/"
        for f in sorted(os.listdir(TRANSCRIPTS)):
            p = os.path.join(TRANSCRIPTS, f)
            if f.endswith(".jsonl"):
                with open(p, encoding="utf-8", errors="ignore") as fh:
                    head = fh.read(200000)
                if marker in head and "one arm of a controlled effort-level trial" in head:
                    tpath = p
    tot = {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0}
    turns = tools = 0
    last_ctx = 0
    seen = set()
    if tpath and os.path.exists(tpath):
        for line in open(tpath, encoding="utf-8", errors="ignore"):
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = o.get("message") or {}
            if o.get("type") != "assistant" or not isinstance(msg, dict):
                continue
            mid = msg.get("id")
            for b in msg.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools += 1
            if mid in seen:
                continue
            seen.add(mid)
            u = msg.get("usage") or {}
            turns += 1
            tot["input"] += u.get("input_tokens", 0)
            tot["cache_write"] += u.get("cache_creation_input_tokens", 0)
            tot["cache_read"] += u.get("cache_read_input_tokens", 0)
            tot["output"] += u.get("output_tokens", 0)
            last_ctx = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    all_in = tot["input"] + tot["cache_write"] + tot["cache_read"]
    out = {"transcript": tpath, "api_calls": turns, "tool_calls": tools, "tokens": tot,
           "cache_share": round(tot["cache_read"] / all_in, 3) if all_in else None,
           "output_to_input": round(tot["output"] / all_in, 4) if all_in else None,
           "final_context": last_ctx,
           "total_input_over_final_context": round(all_in / last_ctx, 1) if last_ctx else None}
    if result:
        out["result"] = {k: result.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms", "total_cost_usd", "terminal_reason")}
        mu = result.get("modelUsage") or {}
        out["result"]["models"] = {m: {"thinkingTokens": v.get("thinkingTokens"), "outputTokens": v.get("outputTokens"), "costUSD": v.get("costUSD")} for m, v in mu.items()}
        out["final_message"] = result.get("result")
    return out


def main():
    report = {"atlases": {k: grade_atlas(p) for k, p in ATLASES.items()},
              "sessions": {arm: arm_session(arm) for arm in ("high", "xhigh")}}
    with open(os.path.join(HERE, "grade_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    for k, a in report["atlases"].items():
        if not a.get("present"):
            print(f"{k}: MISSING")
            continue
        r = a["repetition"]
        print(f"{k}: size_ok={a['size_ok']} mode={a['mode']} joints cols={[(x[0], x[2]) for x in a['joint_columns']]} "
              f"rows={[(x[0], x[2]) for x in a['joint_rows']]} wrap={a['wrap']} max_pair_ncc={r['max_pair']} "
              f"median={r['median_pair_ncc']} pairs>0.5={r['pairs_over_0.5']}")
    for arm, s in report["sessions"].items():
        print(f"{arm}: {json.dumps({k: v for k, v in s.items() if k != 'final_message'})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
