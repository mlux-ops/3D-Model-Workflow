import sys
sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/vanity_oak_from_photo/source")
import numpy as np
from scipy import ndimage as ndi
from scipy.signal import find_peaks
from common import load_rgb, lum
from guard import SOURCE_PHOTO

L = lum(load_rgb(SOURCE_PHOTO))
R = ndi.gaussian_filter(L, 5) - ndi.gaussian_filter(L, 1)
# vertical reveals: average R over row bands
for y0, y1 in [(480, 560), (750, 830), (1000, 1040)]:
    p = R[y0:y1].mean(0)
    pk, pr = find_peaks(p, prominence=3)
    print("rows", y0, y1, [(int(x), round(p[x], 1)) for x in pk if p[x] > 4])
# horizontal reveals: average R over column bands
for x0, x1 in [(450, 480), (560, 620), (780, 880), (1050, 1150), (1300, 1400), (1440, 1460)]:
    p = R[:, x0:x1].mean(1)
    pk, pr = find_peaks(p, prominence=3)
    print("cols", x0, x1, [(int(y), round(p[y], 1)) for y in pk if p[y] > 4])
