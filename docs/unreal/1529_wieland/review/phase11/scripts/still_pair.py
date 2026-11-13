"""Phase 11: lay a final still (r.RayTracing.Nanite.Mode 0) beside the Phase 12 picture of the same view (mode 2)
and print the mean brightness difference. Usage: python -B still_pair.py <view> [<crop x0 y0 x1 y1 in 0..1>]"""
import sys
import numpy as np
from PIL import Image, ImageDraw

view = sys.argv[1]
new = Image.open("delivery/stills/%s_pathtraced.0000.png" % view).convert("RGB")
old = Image.open("review/phase12/ground_truth/%s_pathtraced.0000.png" % view).convert("RGB")
a = np.asarray(new, dtype=np.float32)
b = np.asarray(old, dtype=np.float32)
lum = lambda x: (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])
la, lb = lum(a), lum(b)
diff = np.abs(la - lb)
print(view, "mean luma new %.2f old %.2f (%.1f percent), mean abs diff %.2f, share of pixels differing by more than 25 levels: %.2f percent"
      % (la.mean(), lb.mean(), 100.0 * (la.mean() - lb.mean()) / lb.mean(), diff.mean(), 100.0 * (diff > 25).mean()))
if len(sys.argv) > 2:
    x0, y0, x1, y1 = [float(v) for v in sys.argv[2:6]]
    box = (int(x0 * new.width), int(y0 * new.height), int(x1 * new.width), int(y1 * new.height))
    new, old = new.crop(box), old.crop(box)
    tag = "_crop"
else:
    tag = ""
w = 1600
h = int(w * new.height / new.width)
sheet = Image.new("RGB", (w * 2 + 10, h + 40), "white")
sheet.paste(new.resize((w, h), Image.LANCZOS), (0, 40))
sheet.paste(old.resize((w, h), Image.LANCZOS), (w + 10, 40))
draw = ImageDraw.Draw(sheet)
draw.text((10, 12), "%s Phase 11 final still, Nanite ray tracing off (fallback copies of the meshes traced)" % view, fill="black")
draw.text((w + 20, 12), "%s Phase 12 picture, Nanite ray tracing mode 2" % view, fill="black")
out = "review/phase11/scratch/%s_pair%s.jpg" % (view, tag)
sheet.save(out, quality=88)
print(out)
