"""Blind review set for Sonnet 5.5 vs Opus 5.5 hex atlases (high / xhigh / max of each model).

Reuses the 2026-09-26 renderer (build_blind.build_one: same grazing light, height scale and crops) so the
Opus and Sonnet images are made identically. Six atlases are relabelled A-F at random; the key goes to
blind_key6.json. The 2026-09-19 baseline is left out (it ranked last in the Opus review).

Usage: python build_blind6.py [seed]
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OPUS_H = os.path.abspath(os.path.join(HERE, "..", "..", "..", "effort-trial-2026-09-26-hex", "_harness"))
SONNET = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, OPUS_H)
import build_blind as bb  # noqa: E402

bb.OUT = os.path.join(HERE, "blind6")


def main(seed=None):
    os.makedirs(bb.OUT, exist_ok=True)
    items = {f"opus_{e}": os.path.join(os.path.dirname(OPUS_H), e, "textures") for e in ("high", "xhigh", "max")}
    items.update({f"sonnet_{e}": os.path.join(SONNET, e, "textures") for e in ("high", "xhigh", "max")})
    rng = random.Random(seed if seed is not None else int.from_bytes(os.urandom(8), "big"))
    labels = list("ABCDEF")
    rng.shuffle(labels)
    key = dict(zip(labels, items.keys()))
    json.dump(key, open(os.path.join(HERE, "blind_key6.json"), "w", encoding="utf-8"), indent=1)
    bb.sources()
    info = {}
    for lab in sorted(key):
        info[lab] = bb.build_one(lab, items[key[lab]], False)
        print(lab, "done", flush=True)
    json.dump(info, open(bb.out_path("blind_info.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
