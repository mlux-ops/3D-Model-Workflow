"""Phase 5: make the small images that the parent materials and a few candidates need.

Usage:
    python -B phase5_make_textures.py <output folder>

Everything here is computed, not photographed, so it is this project's own
work and needs no licence. Every image wraps exactly (it is built from
periodic functions), so its opposite edges match.

    T_W1529_White.png        8 x 8 white, the default colour image
    T_W1529_WhiteLinear.png  8 x 8 white, the default roughness image
    T_W1529_FlatNormal.png   8 x 8 flat relief, the default relief image
    T_W1529_Noise.png        256 x 256, three unrelated cloud patterns in red,
                             green and blue; the parents read it at a size of
                             several metres to vary colour and to place dirt
    T_W1529_Siding_N.png     relief of one course of lap siding
    T_W1529_Reed_N.png       relief of one reed of reeded glass
    T_W1529_Tile24x12_C.png  colour of one 24 by 12 inch tile with its joint
    T_W1529_Tile24x12_N.png  relief of the same tile
    T_W1529_Tile24x12_R.png  roughness of the same tile
    T_W1529_CMU_C/N/R.png    colour, relief and roughness of concrete block

A table of what each image is, with its physical size, is written beside
them as generated_textures.csv.
"""

import csv
import os
import sys

import numpy as np
from PIL import Image

INCH = 0.0254


def cloud(size, cutoff, seed):
    """A wrapping cloud pattern with an even spread of values from 0 to 1."""
    rng = np.random.default_rng(seed)
    spectrum = np.fft.fft2(rng.standard_normal((size, size)))
    fx = np.fft.fftfreq(size) * size
    radius = np.sqrt(fx[None, :] ** 2 + fx[:, None] ** 2)
    spectrum *= np.exp(-(radius / cutoff) ** 2)
    field = np.real(np.fft.ifft2(spectrum))
    ranks = field.ravel().argsort().argsort().reshape(field.shape)
    return ranks / float(size * size - 1)


def normal_from_height(height_m, pixel_u_m, pixel_v_m):
    """Relief image (red right, green down, blue out) from heights in metres; wraps."""
    du = (np.roll(height_m, -1, axis=1) - np.roll(height_m, 1, axis=1)) / (2.0 * pixel_u_m)
    dv = (np.roll(height_m, -1, axis=0) - np.roll(height_m, 1, axis=0)) / (2.0 * pixel_v_m)
    normal = np.dstack([-du, -dv, np.ones_like(height_m)])
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    return np.clip(np.round((normal * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)


def save(folder, name, array):
    Image.fromarray(array).save(os.path.join(folder, name))


def main(folder):
    os.makedirs(folder, exist_ok=True)
    rows = []

    def note(name, pixels, field, what):
        rows.append({"image": name, "pixels": pixels, "physical_size_of_the_field": field, "what_it_is": what})

    save(folder, "T_W1529_White.png", np.full((8, 8, 3), 255, np.uint8))
    note("T_W1529_White.png", "8 x 8", "none", "Plain white; the colour image a parent uses when an instance names none.")
    save(folder, "T_W1529_WhiteLinear.png", np.full((8, 8, 3), 255, np.uint8))
    note("T_W1529_WhiteLinear.png", "8 x 8", "none",
         "Plain white read as numbers, not as colour; the roughness image a parent uses when an instance names none.")
    flat = np.zeros((8, 8, 3), np.uint8)
    flat[..., 0], flat[..., 1], flat[..., 2] = 128, 128, 255
    save(folder, "T_W1529_FlatNormal.png", flat)
    note("T_W1529_FlatNormal.png", "8 x 8", "none", "Flat relief; the relief image a parent uses when an instance names none.")

    noise = np.dstack([cloud(256, 5.0, 11), cloud(256, 9.0, 23), cloud(256, 40.0, 37)])
    save(folder, "T_W1529_Noise.png", np.round(noise * 255.0).astype(np.uint8))
    note("T_W1529_Noise.png", "256 x 256", "set by each use, several metres",
         "Three unrelated wrapping cloud patterns (coarse, medium, fine) in red, green and blue.")

    # Lap siding: one course. The board leans out towards its lower edge by
    # its own thickness, then steps back to the board below.
    exposure, thickness, step = 7.0 * INCH, 0.3125 * INCH, 0.004
    rows_px = 256
    v = (np.arange(rows_px) + 0.5) / rows_px * exposure
    lean = v / (exposure - step) * thickness
    drop = thickness * (1.0 - (v - (exposure - step)) / step)
    profile = np.where(v < exposure - step, lean, drop)
    height = np.repeat(profile[:, None], 16, axis=1)
    save(folder, "T_W1529_Siding_N.png", normal_from_height(height, exposure / rows_px, exposure / rows_px))
    note("T_W1529_Siding_N.png", "16 x 256", "any width by %.4f m (7 in, assumed exposure)" % exposure,
         "Relief of one course of lap siding: a board 5/16 in thick leaning out to a 4 mm shadow step.")

    # Reeded glass: one half-inch reed, a half-round rib 2 mm proud.
    reed, proud = 0.5 * INCH, 0.002
    u = (np.arange(64) + 0.5) / 64.0
    rib = proud * np.sin(np.pi * u) ** 0.8
    height = np.repeat(rib[None, :], 16, axis=0)
    save(folder, "T_W1529_Reed_N.png", normal_from_height(height, reed / 64.0, reed / 64.0))
    note("T_W1529_Reed_N.png", "64 x 16", "%.4f m (0.5 in, from the material's name) by any height" % reed,
         "Relief of one vertical reed of reeded glass, 2 mm proud (assumed).")

    # One 24 by 12 inch tile with half a joint on every side.
    width_m, height_m, joint, recess, bevel = 24.0 * INCH, 12.0 * INCH, 0.003, 0.001, 0.0015
    px_u, px_v = 1024, 512
    pixel = width_m / px_u
    x = (np.arange(px_u) + 0.5) * pixel
    y = (np.arange(px_v) + 0.5) * (height_m / px_v)
    edge_x = np.minimum(x, width_m - x)[None, :]
    edge_y = np.minimum(y, height_m - y)[:, None]
    edge = np.minimum(np.broadcast_to(edge_x, (px_v, px_u)), np.broadcast_to(edge_y, (px_v, px_u)))
    face = np.clip((edge - joint / 2.0) / bevel, 0.0, 1.0)
    save(folder, "T_W1529_Tile24x12_N.png", normal_from_height(face * recess, pixel, height_m / px_v))
    in_joint = (edge < joint / 2.0)
    colour = np.where(in_joint[..., None], 150, 255).astype(np.uint8).repeat(3, axis=2)
    save(folder, "T_W1529_Tile24x12_C.png", colour)
    rough = np.where(in_joint[..., None], 230, 64).astype(np.uint8).repeat(3, axis=2)
    save(folder, "T_W1529_Tile24x12_R.png", rough)
    for suffix, what in (("C", "Colour: white tile face, grey joint; the instance tints it."),
                         ("N", "Relief: the joint lies 1 mm below the face behind a 1.5 mm bevel."),
                         ("R", "Roughness: face 0.25, joint 0.90.")):
        note("T_W1529_Tile24x12_%s.png" % suffix, "1024 x 512", "%.4f by %.4f m (24 by 12 in, from the material's name)" % (
            width_m, height_m), "One tile with a 3 mm joint (assumed), stacked bond (assumed). " + what)

    # Concrete block: two courses of 16 by 8 inch blocks (nominal, joint included)
    # in running bond, so that the field is 16 by 16 inches and wraps.
    block_w, block_h, joint, recess = 16.0 * INCH, 8.0 * INCH, 0.010, 0.003
    px = 512
    pixel = block_w / px
    x = ((np.arange(px) + 0.5) * pixel)[None, :]
    y = ((np.arange(px) + 0.5) * pixel)[:, None]
    course = np.floor(y / block_h)
    in_course = y - course * block_h
    shifted = np.mod(x + course * block_w / 2.0, block_w)
    edge = np.minimum(np.minimum(shifted, block_w - shifted), np.minimum(in_course, block_h - in_course))
    face = np.clip((edge - joint / 2.0) / 0.003, 0.0, 1.0)
    grain = (cloud(px, 120.0, 51) - 0.5) * 0.0006 * face
    save(folder, "T_W1529_CMU_N.png", normal_from_height(face * recess + grain, pixel, pixel))
    in_joint = edge < joint / 2.0
    speckle = 225.0 + 30.0 * cloud(px, 150.0, 52)
    colour = np.where(in_joint, 190.0, speckle)
    save(folder, "T_W1529_CMU_C.png", np.round(colour).astype(np.uint8)[..., None].repeat(3, axis=2))
    rough = np.where(in_joint, 235, 225).astype(np.uint8)
    save(folder, "T_W1529_CMU_R.png", rough[..., None].repeat(3, axis=2))
    for suffix, what in (("C", "Colour: near-white speckled block face, slightly darker joint; the instance tints it."),
                         ("N", "Relief: the joint lies 3 mm below the face; fine grain on the face."),
                         ("R", "Roughness: face 0.88, joint 0.92.")):
        note("T_W1529_CMU_%s.png" % suffix, "512 x 512", "%.4f by %.4f m (two courses of 16 by 8 in blocks)" % (
            block_w, block_w), "Concrete block, 10 mm joint, running bond (all assumed: the nominal block). " + what)

    with open(os.path.join(folder, "generated_textures.csv"), "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("%d images written to %s" % (len(rows), folder))


if __name__ == "__main__":
    main(sys.argv[1])
