"""Phase 12: seam figure, large-scale unevenness and mean colour of image files (read-only).

    python -P -B measure_image.py <tools folder> <image> [<image> ...]
"""
import sys

sys.path.insert(0, sys.argv[1])
import phase5_material_tests as tests
from phase5_candidates import mean_linear

for path in sys.argv[2:]:
    lum, image = tests.luminance(path)
    print(path.replace("\\", "/").rsplit("/", 1)[-1], image.size, "seam %.2f" % tests.seam_figure(lum),
          "uneven %.3f" % tests.unevenness(lum), "mean linear", [round(v, 3) for v in mean_linear(path)])
