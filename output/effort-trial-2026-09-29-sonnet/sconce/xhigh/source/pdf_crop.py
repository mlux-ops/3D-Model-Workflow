import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_path
from PIL import Image
OUT = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/work/pdf/'
im = Image.open(OUT + 'install_page1_full.png')
# page points -> px (scale 3): x*3, (792-y)*3
def crop(name, x0, y0, x1, y1, s):
    b = (int(x0 * 3), int((792 - y1) * 3), int(x1 * 3), int((792 - y0) * 3))
    c = im.crop(b)
    c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS)
    c.save(safe_path(OUT + name)); print(name, c.size)
crop('inst_a.png', 100, 500, 450, 740, 0.75)
crop('inst_b.png', 100, 300, 450, 520, 0.75)
crop('inst_c.png', 230, 150, 520, 400, 0.85)
crop('inst_d.png', 40, 150, 330, 400, 0.85)
