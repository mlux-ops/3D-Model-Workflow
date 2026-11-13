"""Phase 11, step 11.2: draw the floor maps made by map_probe.py, with a route laid over them when given.

    python -B review/phase11/scripts/map_draw.py <floor> [<route name> ...]

Black: something blocks a camera at eye height. Red: that something is a door. Brown: casework, furniture or
a plumbing fixture. White: free, walking surface at floor height. Blue to yellow: free, walking surface below
or above the floor (stairs). Grey: free, no surface found under it. Writes review/phase11/paths/map_<floor>.png.
"""
import json
import sys

from PIL import Image, ImageDraw

PATHS = "review/phase11/paths/"
SCALE = 8  # pixels per 10 cm cell


def colour(block, height, labels):
    if block >= 0:
        label = labels[block]
        if label.startswith("Doors"):
            return (230, 30, 30)
        if label.startswith(("Casework", "Furniture", "Plumbing", "Specialty", "Generic")):
            return (150, 110, 60)
        if label.startswith(("Railings", "Stairs")):
            return (0, 130, 60)
        if label.startswith("Windows") or label.startswith("Curtain"):
            return (60, 160, 255)
        return (20, 20, 20)
    if height is None:
        return (200, 200, 200)
    if abs(height) <= 4.0:
        return (255, 255, 255)
    if height > 0:
        f = min(1.0, height / 90.0)
        return (255, int(255 - 120 * f), int(200 - 200 * f))
    f = min(1.0, -height / 190.0)
    return (int(200 - 200 * f), int(230 - 130 * f), 255)


def main():
    floor = sys.argv[1]
    data = json.load(open(PATHS + "map_%s.json" % floor))
    nx, ny, labels = data["nx"], data["ny"], data["labels"]
    x0, y0, cell, z = data["x0"], data["y0"], data["cell"], data["z"]
    margin = 40
    image = Image.new("RGB", (ny * SCALE + margin, nx * SCALE + margin), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    def px(x, y):
        # north (-X) up, east (-Y) right
        return (margin + (y0 + ny * cell - y) / cell * SCALE, margin + (x - x0) / cell * SCALE)

    for i in range(nx):
        for j in range(ny):
            block, height = data["cells"][i][j]
            a = px(x0 + i * cell, y0 + (j + 1) * cell)
            draw.rectangle([a[0], a[1], a[0] + SCALE - 1, a[1] + SCALE - 1], fill=colour(block, height, labels))
    for gx in range(int(x0 // 100) * 100, int(x0 + nx * cell) + 1, 100):
        p = px(gx, y0 + ny * cell)
        draw.line([margin, p[1], image.width, p[1]], fill=(255, 170, 170))
        draw.text((2, p[1] - 5), str(gx), fill=(160, 0, 0))
    for gy in range(int(y0 // 100) * 100, int(y0 + ny * cell) + 1, 100):
        p = px(x0, gy)
        draw.line([p[0], margin, p[0], image.height], fill=(255, 170, 170))
        draw.text((p[0] - 14, 4 + (12 if (gy // 100) % 2 else 0)), str(gy), fill=(160, 0, 0))
    for name in sys.argv[2:]:
        probe = json.load(open(PATHS + name + "_probe.json"))
        near = [s for s in probe["samples"] if abs(s["eye"] - 160.0 - z) < 170.0]
        last = None
        for s in near:
            p = px(s["x"], s["y"])
            if last is not None and abs(s["d"] - last[2]) < 25.0:
                draw.line([last[0], last[1], p[0], p[1]], fill=(255, 0, 255) if "hit" not in s else (0, 255, 255), width=3)
            last = (p[0], p[1], s["d"])
        route = json.load(open(PATHS + name + "_route.json"))
        for n, point in enumerate(route["points"]):
            if abs(point[2] - z) < 170.0:
                p = px(point[0], point[1])
                draw.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], outline=(120, 0, 200), width=2)
                draw.text((p[0] + 6, p[1] - 12), str(n), fill=(120, 0, 200))
    out = PATHS + "map_%s.png" % floor
    image.save(out)
    print(out, image.size)


main()
