"""Comparison sheets for the visual review (C:/Python314/python.exe, pillow).

Product photo beside the matching native Revit export, each cropped to content and
scaled to the same height (idea of Roccesco compare_photos.py, reference.md section 4).
Compare proportions and layout only; the verdict belongs to the reviewer (REVIEW.md).
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.normpath(os.path.join(HERE, '..'))
REF = os.path.normpath(os.path.join(RUN, '..', '..', 'references', 'miele_km3054_1'))
EV = os.path.join(RUN, 'evidence')
H = 900


def content(im, bg=(255, 255, 255), tol=12):
    im = im.convert('RGBA')
    flat = Image.new('RGB', im.size, bg)
    flat.paste(im, mask=im.split()[3])
    diff = ImageChops.difference(flat, Image.new('RGB', im.size, bg)).convert('L').point(lambda v: 255 if v > tol else 0)
    box = diff.getbbox()
    return flat.crop(box) if box else flat


def scaled(im):
    return im.resize((max(1, round(im.width * H / im.height)), H), Image.LANCZOS)


def sheet(name, left, right, ltitle, rtitle, crop_left=True):
    a = scaled(content(left) if crop_left else left.convert('RGB'))
    b = scaled(content(right))
    pad, top = 30, 60
    out = Image.new('RGB', (a.width + b.width + pad * 3, H + top + pad), 'white')
    out.paste(a, (pad, top))
    out.paste(b, (pad * 2 + a.width, top))
    d = ImageDraw.Draw(out)
    try:
        f = ImageFont.truetype('arial.ttf', 26)
    except Exception:
        f = ImageFont.load_default()
    d.text((pad, 15), ltitle, fill='black', font=f)
    d.text((pad * 2 + a.width, 15), rtitle, fill='black', font=f)
    path = os.path.join(EV, name)
    out.save(path)
    print(path, out.size)
    return path


def overlay(name, photo, export):
    a = content(photo)
    b = content(export).resize(a.size, Image.LANCZOS)
    out = Image.blend(a, b, 0.5)
    path = os.path.join(EV, name)
    out.save(path)
    print(path, out.size)


if __name__ == '__main__':
    top_photo = Image.open(os.path.join(REF, 'img_01_20000084693.png'))
    top_model = Image.open(os.path.join(EV, 'KM3054_Isolated - 3D View - Isolated Top.png'))
    sheet('COMPARE_top_photo_vs_revit.png', top_photo, top_model,
          'Miele 20000084693 (top view, product photo)', 'Revit 2025 native export: Isolated Top (shaded)')
    overlay('COMPARE_top_overlay_50pct.png', top_photo, top_model)
    obl_photo = Image.open(os.path.join(REF, 'img_03_20000146968.png'))
    obl_model = Image.open(os.path.join(EV, 'KM3054_Isolated - 3D View - Isolated Oblique Realistic.png'))
    sheet('COMPARE_oblique_photo_vs_revit.png', obl_photo, obl_model,
          'Miele 20000146968 (in-situ oblique photo, uncropped)', 'Revit 2025 native export: Isolated Oblique Realistic',
          crop_left=False)
