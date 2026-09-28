"""Finish check: does the vein-cut face carry fine linear ridges (as the ridged cross-cut 06 swatch does)?

For each image (veins/ridges horizontal), the luminance is high-passed, and the 1-D power spectrum across
the ridge direction (along image y, averaged over all columns) is computed. A ridged face shows a narrow
spectral peak at its pitch (06: ~0.09 in) standing well above the smooth background; a flat face does not.
Peak prominence = max(power in 0.05-0.25 in pitch band) / median(power in the same band). Writes
_work/ridges.json."""
import json

import numpy as np
from PIL import Image

from guard import out_path, ref

B = "E:/Claude/3D-Model-Workflow/"
IMGS = {
    "06_ridged_crosscut_REFERENCE": (B + "output/belmont_tiles/ElmStone_Jute_24x48/references/06_new_fluted_crosscut.webp", 0, 2000 / 48.0),
    "u09_veincut": (ref("user_supplied/u09_flat_veincut_swatch.webp"), 0, 1890 / 48.0),
    "w05_veincut_panel": (ref("web/w05_ms_ecostone_veincut_jute_24x48_panel.jpg"), 0, 49.96),
    "w14_veincut_48x110": (ref("web/w14_ms_jute_veincut_48x110_04.jpg"), 1, 2039 / 48.0),
    "old05_veincut": (B + "output/belmont_tiles/ElmStone_Jute_24x48/references/05_new_flat_veincut.jpg", 0, 1890 / 48.0),
}


def main():
    out = {}
    for n, (p, rot, ppi) in IMGS.items():
        a = np.asarray(Image.open(p).convert("L")).astype(np.float64)
        a = np.rot90(a, rot)
        a = a - a.mean(0, keepdims=True)
        win = np.hanning(a.shape[0])[:, None]
        P = (np.abs(np.fft.rfft(a * win, axis=0)) ** 2).mean(1)
        f = np.fft.rfftfreq(a.shape[0], d=1.0 / ppi)          # cycles per inch
        pitch = 1.0 / np.maximum(f, 1e-9)
        band = (pitch >= 0.05) & (pitch <= 0.25)
        # detrend the spectrum by a running median (log domain)
        lp = np.log(P + 1e-12)
        k = 15
        med = np.array([np.median(lp[max(0, i - k):i + k + 1]) for i in range(len(lp))])
        prom = np.exp(lp - med)
        i = np.flatnonzero(band)[np.argmax(prom[band])]
        out[n] = {"ppi": ppi, "peak_pitch_in": float(pitch[i]), "peak_prominence": float(prom[i]),
                  "band_median_prominence": float(np.median(prom[band]))}
        print(n, out[n])
    json.dump(out, open(out_path("_work/ridges.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
