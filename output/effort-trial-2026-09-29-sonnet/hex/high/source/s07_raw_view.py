from srcs import *

d = load_or_build(force=True)
print({k: len(v) for k, v in d.items()})
raws = d["raw"]
allsfs = np.concatenate([r["sfs"][r["mask"]] for r in raws])
alllbp = np.concatenate([r["lbp"][r["mask"]] for r in raws])
print("sfs std %.4f  lbp std %.3f  corr %.3f" % (allsfs.std(), alllbp.std(), np.corrcoef(allsfs, alllbp)[0, 1]))


def norm(a, m, lo=-2.5, hi=2.5):
    z = (a - a[m].mean()) / a[m].std()
    return (np.clip((z - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)


def shade(h, m, az_deg, el_deg=20, gain=1.0):
    gy, gx = np.gradient(h)
    z = (h - h[m].mean()) / h[m].std()
    gy, gx = np.gradient(ndimage.gaussian_filter(z, 0.7))
    a = np.deg2rad(az_deg)
    lx, ly = np.cos(a), np.sin(a)
    s = -(gx * lx + gy * ly) * gain
    return (np.clip(128 + 60 * s / np.std(s[m]) , 0, 255)).astype(np.uint8)


for r in raws[:2]:
    m = r["mask"]
    comb = (r["sfs"] / r["sfs"][m].std()) * 0.6 + (r["lbp"] / r["lbp"][m].std()) * 0.4
    panels = [norm(r["lum"], m, -3, 3), norm(r["sfs"], m), norm(r["lbp"], m), shade(comb, m, 180)]
    H_, W_ = panels[0].shape
    canvas = Image.new("L", (W_ * 2, H_ * 2))
    for k, p in enumerate(panels):
        p = p.copy()
        p[~m] = 0
        canvas.paste(Image.fromarray(p), ((k % 2) * W_, (k // 2) * H_))
    save_img(canvas, RUN + "/work/rawview_i%d_j%d.png" % (r["i"], r["j"]))
