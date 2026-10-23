import sys

path = sys.argv[1]
s = open(path, encoding="utf-8").read()
rep = [
    ('''        "swatch": dict(img=lp8(src.sw8), valid=src.sw8_valid, D=src.sw8_D, far=np.zeros(src.sw8.shape[:2]),
                       orients=ORIENTS_SW),''', '''        "swatch": dict(img=lp8(src.sw8), valid=src.sw8_valid, D=src.sw8_D, far=np.zeros(src.sw8.shape[:2]),
                       orients=ORIENTS_ALL),'''),
    ('''                                    r=np.ascontiguousarray(orient(p["idx_r"], t)),
                                    c=np.ascontiguousarray(orient(p["idx_c"], t)))
''', '''                                    r=np.ascontiguousarray(orient(p["idx_r"], t)),
                                    c=np.ascontiguousarray(orient(p["idx_c"], t)))
            ro, co = p["oriented"][t]["r"], p["oriented"][t]["c"]
            # oriented (row, col) -> original (row, col):  s = A o + b
            p["oriented"][t]["A"] = np.array([[ro[1, 0] - ro[0, 0], ro[0, 1] - ro[0, 0]],
                                              [co[1, 0] - co[0, 0], co[0, 1] - co[0, 0]]], float)
            p["oriented"][t]["b"] = np.array([ro[0, 0], co[0, 0]], float)
        p["records"] = []
'''),
    ('''                ci, i0, j0 = pick[int(rng.integers(len(pick)))]
''', '''                pick = coincidence_filter(pick, cands, pools, fi, np.array([y0 / S, x0 / S]), h8, w8)
                ci, i0, j0 = pick[int(rng.integers(len(pick)))]
'''),
    ('''                r0o, c0o = int(rr.min()), int(cc_.min())
                # ---- 64 px/in content
''', '''                r0o, c0o = int(rr.min()), int(cc_.min())
                At, bt = o["A"], o["b"]
                p["records"].append({"face": fi, "M": At.T, "c": np.array([y0 / S, x0 / S]) - np.array([i0, j0])
                                     - At.T @ bt, "rect": (r0o, c0o, int(rr.max()) + 1, int(cc_.max()) + 1)})
                # ---- 64 px/in content
'''),
    ('''                if name == "swatch":
                    oimg = orient(src.sw64, t)
                    phi_src = src.phi0 if not vflipped(t) else -(src.omega * (src.sw64.shape[0] - 1) + src.phi0)
                    rho, perr = aligned_row(i0 * S, y0, phi_src, phi_f, src.P, src.omega, 0,
                                            oimg.shape[0] - BH)
                    col0 = j0 * S
                    blk = oimg[rho:rho + BH, col0:col0 + BW]
                    # original 64 px/in rectangle
                    rI, cI = np.meshgrid(np.arange(src.sw64.shape[0]), np.arange(src.sw64.shape[1]), indexing="ij")
                    rO, cO = orient(rI, t)[rho:rho + BH, col0:col0 + BW], orient(cI, t)[rho:rho + BH, col0:col0 + BW]
                    rec.update({"src_rect_64ppi_xywh": [int(cO.min()), int(rO.min()), BW, BH],
                                "src_rect_native_px_xywh": [round(cO.min() * SW_PPI / PPI, 1),
                                                            round(rO.min() * SW_PPI / PPI, 1),
                                                            round(BW * SW_PPI / PPI, 1), round(BH * SW_PPI / PPI, 1)],
                                "stripe_phase_err_rad": round(perr, 3)})
                else:
                    blk = src.floor_block64(r0o, c0o, rr.max() - r0o + 1, cc_.max() - c0o + 1, t)
                    blk = blk[:BH, :BW]
                    # donor grain from a bland swatch window, phase aligned
                    dt = ORIENTS_SW[int(rng.integers(4))]
                    ok_d = src.donor_ok[dt]
                    fine_o = orient(src.sw_fine, dt)
                    dr, dc = np.nonzero(ok_d)
                    q = int(rng.integers(len(dr)))
                    phi_src = src.phi0 if not vflipped(dt) else -(src.omega * (src.sw64.shape[0] - 1) + src.phi0)
                    rho, perr = aligned_row(int(dr[q]), y0, phi_src, phi_f, src.P, src.omega, 0,
                                            fine_o.shape[0] - BH)
                    blk = blk + fine_o[rho:rho + BH, int(dc[q]):int(dc[q]) + BW]
                    Xa = FX0 + c0o / S''', '''                if name == "swatch":
                    oimg = orient(src.sw64 if t[0] % 2 == 0 else src.sw_lp, t)
                    if t[0] % 2 == 0:
                        # unrotated or flipped: keep the swatch grain itself, stripe phase aligned
                        phi_src = src.phi0 if not vflipped(t) else -(src.omega * (src.sw64.shape[0] - 1) + src.phi0)
                        rho, perr = aligned_row(i0 * S, y0, phi_src, phi_f, src.P, src.omega, 0,
                                                oimg.shape[0] - BH)
                        rec["stripe_phase_err_rad"] = round(perr, 3)
                    else:
                        # quarter-turned: structure above the grain band only; grain from a donor,
                        # so the striation stays horizontal
                        rho = i0 * S
                    col0 = j0 * S
                    blk = oimg[rho:rho + BH, col0:col0 + BW]
                    if t[0] % 2 == 1:
                        fine, drec = donor_fine(src, rng, y0, phi_f)
                        blk = blk + fine
                        rec["grain_donor"] = drec
                    # original 64 px/in rectangle
                    rI, cI = np.meshgrid(np.arange(src.sw64.shape[0]), np.arange(src.sw64.shape[1]), indexing="ij")
                    rO, cO = orient(rI, t)[rho:rho + BH, col0:col0 + BW], orient(cI, t)[rho:rho + BH, col0:col0 + BW]
                    wO, hO = int(cO.max() - cO.min() + 1), int(rO.max() - rO.min() + 1)
                    rec.update({"src_rect_64ppi_xywh": [int(cO.min()), int(rO.min()), wO, hO],
                                "src_rect_native_px_xywh": [round(cO.min() * SW_PPI / PPI, 1),
                                                            round(rO.min() * SW_PPI / PPI, 1),
                                                            round(wO * SW_PPI / PPI, 1), round(hO * SW_PPI / PPI, 1)]})
                else:
                    blk = src.floor_block64(r0o, c0o, rr.max() - r0o + 1, cc_.max() - c0o + 1, t)
                    blk = blk[:BH, :BW]
                    fine, drec = donor_fine(src, rng, y0, phi_f)
                    blk = blk + fine
                    Xa = FX0 + c0o / S'''),
    ('''                                "grain_donor": {"orient_rot90": int(dt[0]), "orient_fliplr": int(dt[1]),
                                                "oriented_row": int(rho), "oriented_col": int(dc[q]),
                                                "stripe_phase_err_rad": round(perr, 3)}})''', '''                                "grain_donor": drec})'''),
    ('''def main():
    t_start = time.time()''', '''def donor_fine(src, rng, y0, phi_f):
    """Grain band (below ~0.06 in) of a bland swatch window, flipped at random, stripe phase aligned."""
    dt = ORIENTS_SW[int(rng.integers(4))]
    fine_o = orient(src.sw_fine, dt)
    dr, dc = np.nonzero(src.donor_ok[dt])
    q = int(rng.integers(len(dr)))
    phi_src = src.phi0 if not vflipped(dt) else -(src.omega * (src.sw64.shape[0] - 1) + src.phi0)
    rho, perr = aligned_row(int(dr[q]), y0, phi_src, phi_f, src.P, src.omega, 0, fine_o.shape[0] - BH)
    return (fine_o[rho:rho + BH, int(dc[q]):int(dc[q]) + BW],
            {"orient_rot90": int(dt[0]), "orient_fliplr": int(dt[1]), "oriented_row": int(rho),
             "oriented_col": int(dc[q]), "stripe_phase_err_rad": round(perr, 3)})


COINCIDE_IN = 10.0      # reject a reuse that lands within this distance of a flip-mirror of an earlier use
COINCIDE_OVERLAP = 0.15
_filter_stats = {"blocks": 0, "candidates_rejected": 0, "fallbacks": 0}


def coincidence_filter(pick, cands, pools, fi, d0, h8, w8):
    """Drop candidates whose source overlaps an earlier block of another face AND whose content would
    sit at the same place in that face under one of the four cell flips (a book-match or mirror repeat
    that also raises whole-cell correlation)."""
    H8, W8 = FACE_H // S, FACE_W // S
    keep = np.ones(len(pick), bool)
    arr = np.array(pick)
    for ci in np.unique(arr[:, 0]):
        name, t = cands[ci][0], cands[ci][1]
        p = pools[name]
        recs = [r for r in p["records"] if r["face"] != fi]
        if not recs:
            continue
        o = p["oriented"][t]
        A, b = o["A"], o["b"]
        sel = np.nonzero(arr[:, 0] == ci)[0]
        I0 = arr[sel, 1].astype(float)
        J0 = arr[sel, 2].astype(float)
        s1 = (A @ np.vstack([I0, J0])).T + b
        s2 = (A @ np.vstack([I0 + h8 - 1, J0 + w8 - 1])).T + b
        rmin, rmax = np.minimum(s1[:, 0], s2[:, 0]), np.maximum(s1[:, 0], s2[:, 0]) + 1
        cmin, cmax = np.minimum(s1[:, 1], s2[:, 1]), np.maximum(s1[:, 1], s2[:, 1]) + 1
        c_cand = d0[None, :] - np.column_stack([I0, J0]) - (A.T @ b)[None, :]
        for rb in recs:
            G = rb["M"] @ A
            if abs(G[0, 1]) > 0.5:          # quarter-turn relation: never a cell flip
                continue
            gy, gx = G[0, 0], G[1, 1]
            tF = np.array([H8 - 1 if gy < 0 else 0, W8 - 1 if gx < 0 else 0], float)
            T = rb["c"][None, :] - c_cand @ G.T
            dist = np.hypot(*(T - tF[None, :]).T)
            r0, c0, r1, c1 = rb["rect"]
            ov = (np.clip(np.minimum(rmax, r1) - np.maximum(rmin, r0), 0, None)
                  * np.clip(np.minimum(cmax, c1) - np.maximum(cmin, c0), 0, None)) / (h8 * w8)
            keep[sel[(ov > COINCIDE_OVERLAP) & (dist < COINCIDE_IN * S)]] = False
    _filter_stats["blocks"] += 1
    _filter_stats["candidates_rejected"] += int((~keep).sum())
    if not keep.any():
        _filter_stats["fallbacks"] += 1
        return pick
    return [pk for pk, k in zip(pick, keep) if k]


def main():
    t_start = time.time()'''),
    ('''        "png_save_retries": retries,''', '''        "coincidence_filter": dict(_filter_stats, distance_in=COINCIDE_IN, min_overlap=COINCIDE_OVERLAP),
        "png_save_retries": retries,'''),
    ('''        self.sw_fine = self.sw64 - ndi.gaussian_filter(self.sw64, (FINE_SIGMA, FINE_SIGMA, 0))
''', '''        self.sw_lp = ndi.gaussian_filter(self.sw64, (FINE_SIGMA, FINE_SIGMA, 0))
        self.sw_fine = self.sw64 - self.sw_lp
'''),
]
for a, b in rep:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(path, "w", encoding="utf-8").write(s)
print("patched")
