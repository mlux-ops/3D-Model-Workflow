"""Phase 13: side-by-side sheets, each published rendering (left) against the model from about the same viewpoint (right).

Runs outside the editor (needs Pillow). The renderings are read from E:\\Wieland1529_site_data\\proposed_hotel\\ as
reference only; the sheets are review pictures and stay out of the Unreal project.

Usage, from the plan folder: python -B review/phase13/scripts/side_by_side.py
Writes review/phase13/compare_*.jpg and review/phase13/compare_all.jpg.
"""
import os

from PIL import Image, ImageDraw, ImageFont

REFS = "E:/Wieland1529_site_data/proposed_hotel"
VIEWS = "review/phase13/model_views"
OUT = "review/phase13"
HEIGHT = 900
LABEL = ("PROPOSED, modelled from published renderings and records, not a survey. "
         "Model: real-time renderer, Nanite ray tracing off (r.RayTracing.Nanite.Mode 0).")

PAIRS = [
    ("r1", "yimby_1528NWells-1.jpg", "m1_wells_from_southeast.png", "Wells Street from the south-east, street level"),
    ("r2", "yimby_1528NWells-2.jpg", "m2_air_from_southeast.png", "Air view from the south-east"),
    ("r3", "yimby_1528NWells-3.jpg", "m3_wells_street.png", "Ground floor on Wells Street"),
    ("r4", "yimby_1528NWells-4.jpg", "m4_air_from_northwest.png", "Air view from the north-west (garage roof, homes)"),
    ("r5", "yimby_1528NWells-5.jpg", "m5_air_from_southwest.png", "Air view from the west (homes in front of the tower)"),
    ("r6", "yimby_1528NWells-6.jpg", "m6_west_face.png", "From Wieland Street: tower above the homes"),
    ("r7", "yimby_1528NWells-7.jpg", "m7_wieland_street.png", "The homes on Wieland Street, close"),
    ("r8", "yimby_1528NWells-8.jpg", "m8_wells_face.png", "Flat Wells Street elevation"),
    ("r11", "urbanize_lead_1528NWells_2022-10.jpg", "m3_wells_street.png", "Urbanize 2022 lead picture: Wells Street"),
    ("r12", "pappageorgehaymes_152331_medium-1.jpg", "m2_air_from_southeast.png", "Architect's page: air view from the south-east"),
]


def font(size):
    for name in ("arial.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(path, height):
    image = Image.open(path).convert("RGB")
    return image.resize((max(1, round(image.width * height / image.height)), height), Image.LANCZOS)


def sheet(key, ref, view, title):
    left, right = fit(os.path.join(REFS, ref), HEIGHT), fit(os.path.join(VIEWS, view), HEIGHT)
    gap, head, foot = 20, 60, 70
    page = Image.new("RGB", (left.width + right.width + gap, HEIGHT + head + foot), (255, 255, 255))
    page.paste(left, (0, head))
    page.paste(right, (left.width + gap, head))
    draw = ImageDraw.Draw(page)
    draw.text((10, 8), f"{key}: {title}", fill=(0, 0, 0), font=font(26))
    draw.text((10, HEIGHT + head + 6), f"Left: published rendering {ref} (reference only, copyright of its publisher)",
              fill=(0, 0, 0), font=font(18))
    draw.text((left.width + gap + 10, HEIGHT + head + 6), f"Right: model view {view}", fill=(0, 0, 0), font=font(18))
    draw.text((10, HEIGHT + head + 36), LABEL, fill=(160, 0, 0), font=font(18))
    out = os.path.join(OUT, f"compare_{key}.jpg")
    page.save(out, quality=88)
    return out


def main():
    outs = [sheet(*pair) for pair in PAIRS]
    thumbs = [Image.open(path) for path in outs]
    width = 1800
    thumbs = [t.resize((width, round(t.height * width / t.width)), Image.LANCZOS) for t in thumbs]
    page = Image.new("RGB", (width, sum(t.height for t in thumbs)), (255, 255, 255))
    y = 0
    for t in thumbs:
        page.paste(t, (0, y))
        y += t.height
    page.save(os.path.join(OUT, "compare_all.jpg"), quality=80)
    print("\n".join(outs))


if __name__ == "__main__":
    main()
