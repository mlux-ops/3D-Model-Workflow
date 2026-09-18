# -*- coding: utf-8 -*-
"""Generate the two M01 pendant-native-run .adsklib deliverables.

Both are CONTAINER-DERIVED GENERATIONS produced by adsklib_gen.py, not native
Revit Material Browser creations -- disclosed per the task brief. All
scalars other than name/description/paths/scale are taken verbatim from the
MSI Adella Viso White reference library (output/adella/...), which this
script treats as read-only.
"""
import io
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adsklib_gen as G

MATERIAL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def make_thumbnail(basecolor_png_path, size=(256, 256)):
    im = Image.open(basecolor_png_path).convert('RGB')
    im = im.resize(size, Image.LANCZOS)
    im = im.convert('RGBA')
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    return buf.getvalue()


def common_kwargs():
    ref = G.extract_params(G.ADELLA_PATH)
    return dict(
        manufacturer=ref['manufacturer'], model=ref['model'], url=ref['url'],
        color_rgb=(239, 240, 239), material_class='Ceramic',
        glossiness=.60, refl0=.04, refl90=1.0, transparency=0.0,
        refraction_index=1.5, bump_amount=.15,
    )


def build_baseline():
    base = os.path.join(MATERIAL_ROOT, 'baseline')
    out_path = os.path.join(base, 'MSI_Adella_Viso_White_1-16_Grout_R2025.adsklib')
    kwargs = common_kwargs()
    kwargs.update(
        material_name='MSI Adella Viso White - 12x24 Satin - Stacked',
        description=('Adella Viso White 12x24 satin ceramic wall tile; approximate indented '
                      'relief; 1/16 inch light grout'),
        diffuse_path=os.path.join(base, 'textures', 'Adella_BaseColor.png'),
        bump_path=os.path.join(base, 'textures', 'Adella_Bump.png'),
        real_world_scale_in=(24.0625, 12.0625),
        thumbnail_png_bytes=make_thumbnail(os.path.join(base, 'textures', 'Adella_BaseColor.png')),
    )
    G.build_library(out_path, **kwargs)
    return out_path


def build_variant():
    base = os.path.join(MATERIAL_ROOT, 'variant')
    out_path = os.path.join(base, 'MSI_Adella_Viso_White_1-8_Grout_R2025.adsklib')
    kwargs = common_kwargs()
    kwargs.update(
        material_name='MSI Adella Viso White - 12x24 Satin - Stacked - 1-8 Grout',
        description=('Adella Viso White 12x24 satin ceramic wall tile; approximate indented '
                      'relief; 1/8 inch light grout'),
        diffuse_path=os.path.join(base, 'textures', 'Adella_BaseColor.png'),
        bump_path=os.path.join(base, 'textures', 'Adella_Bump.png'),
        real_world_scale_in=(24.125, 12.125),
        thumbnail_png_bytes=make_thumbnail(os.path.join(base, 'textures', 'Adella_BaseColor.png')),
    )
    G.build_library(out_path, **kwargs)
    return out_path


if __name__ == '__main__':
    b = build_baseline()
    v = build_variant()
    print('baseline:', b)
    print('variant:', v)
