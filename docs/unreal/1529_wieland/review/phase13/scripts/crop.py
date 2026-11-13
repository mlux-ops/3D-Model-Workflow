"""Phase 13, off line: cut a rectangle out of a reference picture and save it enlarged, for reading drawings.

The source pictures are downloads and stay untrusted: this script lives in the plan folder and is given paths.
Usage: python -P -B crop.py <source picture> <result picture> <left> <top> <right> <bottom> [enlargement]
"""
import sys

from PIL import Image

sys.dont_write_bytecode = True
source, result = sys.argv[1], sys.argv[2]
box = tuple(int(v) for v in sys.argv[3:7])
factor = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
image = Image.open(source).convert("RGB").crop(box)
if factor != 1.0:
    image = image.resize((int(image.width * factor), int(image.height * factor)), Image.LANCZOS)
image.save(result)
print(image.size)
