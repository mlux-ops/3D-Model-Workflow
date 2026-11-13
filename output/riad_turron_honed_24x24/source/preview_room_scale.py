"""3 x 3 repetition of the colour atlas (24'-0" x 12'-0" surface) for the WORKFLOW.md room-scale
non-repetition check, plus a 1:1 strip of 8 ft for close viewing."""
import os

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
col = Image.open(os.path.join(RUN_DIR, "textures", "Riad_Turron_Honed_24x24_Color.png")).convert("RGB")
small = col.resize((col.width // 4, col.height // 4), Image.LANCZOS)      # 16 px/in
a = np.asarray(small)
big = np.tile(a, (3, 3, 1))                                                # 288 x 144 in
im = Image.fromarray(big)
im.thumbnail((1800, 1800), Image.LANCZOS)
im.save(os.path.join(RUN_DIR, "source", "_PREVIEW_room_scale_3x3_24ft_x_12ft.jpg"), quality=90)
print(im.size)
