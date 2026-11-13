"""Phase 13: the images the proposed hotel's materials use, made here from numbers alone (numpy and Pillow).
No downloaded picture is read. Every image wraps around its edges, so it is seamless.

Brick: modular brick, 8 in by 2 2/3 in with the joint, in running bond. One image holds 32 bricks by 64 courses
(2,048 different bricks), so it covers 6.5024 m by 4.3349 m before it repeats.

Usage: python -B review/phase13/scripts/make_textures.py <output folder>
"""
import os
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
BRICKS, COURSES = 32, 64
SIZE = 4096
BRICK_PX, COURSE_PX = SIZE // BRICKS, SIZE // COURSES      # 128 by 64 pixels
JOINT_U, JOINT_V = 6, 9                                    # 3/8 in at 16 and 24 pixels per inch


def to_srgb(linear):
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(linear <= 0.0031308, linear * 12.92, 1.055 * np.power(linear, 1.0 / 2.4) - 0.055)


def to_linear(srgb):
    srgb = np.asarray(srgb, dtype=np.float64) / 255.0
    return np.where(srgb <= 0.04045, srgb / 12.92, np.power((srgb + 0.055) / 1.055, 2.4))


def noise(shape, seed, feature_px):
    """Noise that wraps around the edges, with features about feature_px pixels across."""
    height, width = shape
    random = np.random.default_rng(seed)
    spectrum = np.fft.fft2(random.standard_normal((height, width)))
    fu = np.fft.fftfreq(width)[None, :] * feature_px
    fv = np.fft.fftfreq(height)[:, None] * feature_px
    result = np.real(np.fft.ifft2(spectrum * np.exp(-(fu * fu + fv * fv) * 2.0)))
    result -= result.mean()
    return result / (result.std() + 1e-12)


def normal_image(height_map, slope):
    """Relief image in the engine's convention (green points down the image); typical slope `slope`."""
    du = (np.roll(height_map, -1, axis=1) - np.roll(height_map, 1, axis=1)) * 0.5
    dv = (np.roll(height_map, -1, axis=0) - np.roll(height_map, 1, axis=0)) * 0.5
    scale = slope / (np.sqrt((du * du + dv * dv).mean()) + 1e-12)
    du, dv = du * scale, dv * scale
    length = np.sqrt(du * du + dv * dv + 1.0)
    normal = np.stack([-du / length, -dv / length, 1.0 / length], axis=2)
    return Image.fromarray(np.round((normal * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")


def save_colour(linear, path):
    Image.fromarray(np.round(to_srgb(linear) * 255).astype(np.uint8), "RGB").save(path)


def save_grey(values, path):
    grey = np.round(np.clip(values, 0.0, 1.0) * 255).astype(np.uint8)
    Image.fromarray(np.stack([grey, grey, grey], axis=2), "RGB").save(path)


def brick_layout():
    """Per pixel: which brick it belongs to (course, brick), and how far it is inside the brick face (0 in the
    joint, 1 well inside), for a running bond that wraps."""
    rows, columns = np.mgrid[0:SIZE, 0:SIZE]
    course = rows // COURSE_PX
    shifted = (columns + (course % 2) * (BRICK_PX // 2)) % SIZE
    brick = shifted // BRICK_PX
    in_u = shifted % BRICK_PX
    in_v = rows % COURSE_PX
    edge_u = np.minimum(in_u - JOINT_U / 2.0, BRICK_PX - JOINT_U / 2.0 - in_u)
    edge_v = np.minimum(in_v - JOINT_V / 2.0, COURSE_PX - JOINT_V / 2.0 - in_v)
    inside = np.clip(np.minimum(edge_u / 3.0, edge_v / 3.0), 0.0, 1.0)      # 3 pixel soft edge
    return course, brick, inside


def brick_set(folder, course, brick, inside):
    random = np.random.default_rng(1335)
    fine = noise((SIZE, SIZE), 11, 5.0)
    medium = noise((SIZE, SIZE), 12, 40.0)
    # one value per brick: brightness, warmth, and a few fired darker
    brightness = random.normal(0.0, 1.0, (COURSES, BRICKS))[course, brick]
    warmth = random.normal(0.0, 1.0, (COURSES, BRICKS))[course, brick]
    flashed = (random.random((COURSES, BRICKS)) < 0.12)[course, brick]
    face = inside[:, :, None]
    palettes = {
        # name: brick colour, darker fired brick, mortar (sRGB 0-255), how much bricks differ
        "RedBrick": ((142, 66, 50), (96, 46, 40), (150, 140, 128), 0.16),
        "DarkBrick": ((66, 64, 66), (44, 43, 46), (52, 51, 52), 0.12),
    }
    for name, (base, dark, mortar, spread) in palettes.items():
        base_l, dark_l, mortar_l = to_linear(base), to_linear(dark), to_linear(mortar)
        colour = np.where(flashed[:, :, None], dark_l[None, None, :], base_l[None, None, :])
        gain = 1.0 + spread * brightness + 0.05 * fine + 0.05 * medium
        colour = colour * gain[:, :, None]
        colour[:, :, 0] *= 1.0 + 0.05 * warmth
        colour[:, :, 2] *= 1.0 - 0.05 * warmth
        mortar_colour = mortar_l[None, None, :] * (1.0 + 0.08 * fine + 0.04 * medium)[:, :, None]
        save_colour(colour * face + mortar_colour * (1.0 - face), os.path.join(folder, "T_W1529_PH_%s_C.png" % name))
    # relief and roughness are shared by both bricks: the joint lies back, the face is slightly uneven
    tilt = random.normal(0.0, 1.0, (COURSES, BRICKS))[course, brick]
    height = inside * (1.0 + 0.04 * tilt) + 0.035 * fine * inside + 0.05 * fine * (1.0 - inside) + 0.02 * medium
    normal_image(height, 0.20).save(os.path.join(folder, "T_W1529_PH_Brick_N.png"))
    roughness = 0.80 + 0.05 * fine * inside + 0.12 * (1.0 - inside) + 0.03 * tilt * inside
    save_grey(roughness, os.path.join(folder, "T_W1529_PH_Brick_R.png"))


def green_roof(folder, size=2048):
    """Planted roof (sedum): patches of green, olive and red-brown. The image covers 4 m."""
    patch = noise((size, size), 21, 220.0)
    clump = noise((size, size), 22, 28.0)
    leaf = noise((size, size), 23, 3.0)
    green, olive, red = to_linear((74, 96, 48)), to_linear((112, 112, 58)), to_linear((120, 70, 56))
    w_olive = np.clip(0.5 + 0.6 * patch + 0.3 * clump, 0.0, 1.0)[:, :, None]
    w_red = np.clip(-0.9 + 0.7 * clump - 0.5 * patch, 0.0, 1.0)[:, :, None]
    colour = green[None, None, :] * (1.0 - w_olive) + olive[None, None, :] * w_olive
    colour = colour * (1.0 - w_red) + red[None, None, :] * w_red
    colour = colour * (1.0 + 0.22 * leaf + 0.10 * clump)[:, :, None]
    save_colour(colour, os.path.join(folder, "T_W1529_PH_GreenRoof_C.png"))
    normal_image(leaf + 0.6 * clump, 0.45).save(os.path.join(folder, "T_W1529_PH_GreenRoof_N.png"))


def metal_panel(folder, size=1024):
    """Flat metal wall panels, dark grey, 0.6 m wide and 1.2 m high with a recessed joint. The image covers 1.2 m by 1.2 m
    (two panels across)."""
    rows, columns = np.mgrid[0:size, 0:size]
    half = size // 2
    in_u = columns % half
    joint = (np.minimum(in_u, half - in_u) < 4) | (np.minimum(rows, size - rows) < 4)
    soft = noise((size, size), 31, 300.0)
    grain = noise((size, size), 32, 2.0)
    base = to_linear((70, 72, 76))
    colour = base[None, None, :] * (1.0 + 0.03 * soft + 0.015 * grain)[:, :, None]
    colour = np.where(joint[:, :, None], colour * 0.45, colour)
    save_colour(colour, os.path.join(folder, "T_W1529_PH_MetalPanel_C.png"))
    height = np.where(joint, 0.0, 1.0) + 0.01 * soft
    height = (height + np.roll(height, 1, 0) + np.roll(height, -1, 0) + np.roll(height, 1, 1) + np.roll(height, -1, 1)) / 5.0
    normal_image(height, 0.10).save(os.path.join(folder, "T_W1529_PH_MetalPanel_N.png"))


def main():
    folder = sys.argv[1]
    os.makedirs(folder, exist_ok=True)
    course, brick, inside = brick_layout()
    brick_set(folder, course, brick, inside)
    green_roof(folder)
    metal_panel(folder)
    for name in sorted(os.listdir(folder)):
        picture = Image.open(os.path.join(folder, name))
        print(name, picture.size, round(os.path.getsize(os.path.join(folder, name)) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
