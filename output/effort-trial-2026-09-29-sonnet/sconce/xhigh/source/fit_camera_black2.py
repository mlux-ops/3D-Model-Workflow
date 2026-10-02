# -*- coding: utf-8 -*-
"""CPython 3: black-photo registration with the cut angle and cut-plane centre depth also free (sphere centre pinned at depth 3.75 in,
which is what the published 5.50 in depth requires). Compares level-camera (roll 0) and free-roll fits."""
import os
import sys

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util  # noqa: E402

# reuse the data extraction of fit_camera_black.py without re-running its fit: exec only the data part
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fit_camera_black.py'), encoding='utf-8').read()
head = src.split('best = None')[0]
ns = {'__file__': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fit_camera_black.py')}
exec(compile(head, 'fit_camera_black_head', 'exec'), ns)
rim_pts, plate_pts, sph_pts = ns['rim_pts'], ns['plate_pts'], ns['sph_pts']
PHI = ns['PHI']
camera = ns['camera']
YV = np.array([0, 1.0, 0])
R_SPH = 1.75
ZS = 3.75


def geom(theta_deg, zc):
    th = np.radians(theta_deg)
    N = np.array([0, -np.sin(th), np.cos(th)])
    EY = np.array([0, np.cos(th), np.sin(th)])
    C0 = np.array([0, 0, zc])
    CD = C0 + N * 0.047
    L = (ZS - zc) / np.cos(th)
    S = C0 + N * L
    disc = CD + 4.0 * (np.cos(PHI)[:, None] * np.array([1.0, 0, 0]) + np.sin(PHI)[:, None] * EY)
    return disc, S


PLATE = np.c_[2.625 * np.cos(PHI), 2.625 * np.sin(PHI), np.full_like(PHI, 0.125)]
PLATE_B = np.c_[2.625 * np.cos(PHI), 2.625 * np.sin(PHI), np.zeros_like(PHI)]
PL = np.r_[PLATE, PLATE_B]


def project(P, az, el, roll, s, tx, ty, k):
    d, r, u = camera(az, el, roll)
    P = np.atleast_2d(P)
    w = P @ d
    sc = s * (1 + k * w)
    return np.c_[sc * (P @ r) + tx, -sc * (P @ u) + ty], sc


def make_res(fix_roll):
    def res(q):
        if fix_roll is None:
            az, el, roll, s, tx, ty, k, th, zc = q
        else:
            az, el, s, tx, ty, k, th, zc = q
            roll = fix_roll
        disc, S = geom(th, zc)
        dp, _ = project(disc, az, el, roll, s, tx, ty, k)
        pp, _ = project(PL, az, el, roll, s, tx, ty, k)
        sp, sc = project(S, az, el, roll, s, tx, ty, k)
        return np.concatenate([
            cKDTree(dp[::4]).query(rim_pts)[0],
            0.5 * np.minimum(cKDTree(pp[::4]).query(plate_pts)[0], 40),
            np.abs(np.hypot(sph_pts[:, 0] - sp[0, 0], sph_pts[:, 1] - sp[0, 1]) - R_SPH * sc[0])])
    return res


def run(fix_roll, fix_th=None, fix_zc=None):
    best = None
    for az0 in (45, 55):
        for el0 in (-10, 10):
            for th0 in (16.0, 18.2):
                if fix_roll is None:
                    q0 = [az0, el0, -10, 99, 250, 410, 0.01, th0, 2.1]
                    lo = [0, -40, -45, 60, 100, 100, -0.05, 8, 1.2]
                    hi = [90, 60, 45, 140, 560, 560, 0.08, 26, 3.0]
                else:
                    q0 = [az0, el0, 99, 250, 410, 0.01, th0, 2.1]
                    lo = [0, -40, 60, 100, 100, -0.05, 8, 1.2]
                    hi = [90, 60, 140, 560, 560, 0.08, 26, 3.0]
                if fix_th is not None:
                    lo[-2] = fix_th - 1e-6
                    hi[-2] = fix_th + 1e-6
                    q0[-2] = fix_th
                if fix_zc is not None:
                    lo[-1] = fix_zc - 1e-6
                    hi[-1] = fix_zc + 1e-6
                    q0[-1] = fix_zc
                r = least_squares(make_res(fix_roll), q0, bounds=(lo, hi), loss='soft_l1', f_scale=3.0)
                if best is None or r.cost < best.cost:
                    best = r
    return best


def report(tag, r, fix_roll):
    res = make_res(fix_roll)(r.x)
    nd, npl = len(rim_pts), len(plate_pts)
    print('%-34s cost %8.1f | rms disc %.2f plate %.2f sphere %.2f | x=%s' % (
        tag, r.cost, np.sqrt(np.mean(res[:nd] ** 2)), np.sqrt(np.mean((2 * res[nd:nd + npl]) ** 2)), np.sqrt(np.mean(res[nd + npl:] ** 2)),
        np.round(r.x, 3).tolist()))


report('A roll free, theta+zc free', run(None), None)
report('B roll 0,    theta+zc free', run(0.0), 0.0)
report('C roll free, theta 18.18 zc 1.975', run(None, 18.1794, 1.975), None)
report('D roll 0,    theta 18.18 zc 1.975', run(0.0, 18.1794, 1.975), 0.0)
report('E roll free, theta 15.6 zc 2.33', run(None, 15.6, 2.33), None)
report('F roll 0,    theta 15.6 zc 2.33', run(0.0, 15.6, 2.33), 0.0)
report('G roll free, theta 18.18 zc 2.33', run(None, 18.1794, 2.33), None)
