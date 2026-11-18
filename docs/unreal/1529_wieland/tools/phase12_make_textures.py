"""Phase 12: the images this phase makes itself (outside the editor; needs numpy and Pillow).

Every image made here repeats without a seam by construction (it is built from waves that fit the
image a whole number of times, or from noise filtered in a way that wraps around the edges).

    import phase12_make_textures as mk
    mk.flat_colour((239, 238, 229), folder)        # a plain colour with a faint, slow unevenness
    mk.eggshell_normal(folder)                     # the stipple a paint roller leaves
    mk.brushed(folder)                             # brushed metal: relief and roughness, streaks along U
    mk.seamless_crop(source, folder, name, band)   # an export image made to repeat without a seam
    mk.limestone_blend(folder)                     # large soft zones of buff and grey, for the stone parent
    mk.resample(source, folder, name, size)        # an export image at a finer pixel grid
    mk.contrast(source, folder, name, gain)        # a colour image with a stronger figure

Each function returns [file, asset name, kind, physical field in metres or None, note] and skips
the work when the file is already there.
"""
import hashlib
import os

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def _to_srgb(linear):
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(linear <= 0.0031308, linear * 12.92, 1.055 * linear ** (1 / 2.4) - 0.055)


def _to_linear(srgb):
    srgb = np.asarray(srgb, dtype=np.float64)
    return np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4)


def _seed(text):
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def _filtered_noise(size, seed, along_u_px, along_v_px, band=False):
    """Noise that wraps around the edges, with features about along_u_px by along_v_px pixels.
    With band, the slowest changes are taken out as well, so that only features of that size stay."""
    height, width = size
    random = np.random.default_rng(seed)
    spectrum = np.fft.fft2(random.standard_normal((height, width)))
    fu = np.fft.fftfreq(width)[None, :] * along_u_px
    fv = np.fft.fftfreq(height)[:, None] * along_v_px
    radius = fu * fu + fv * fv
    keep = np.exp(-radius * 2.0)
    if band:
        keep = keep * (1.0 - np.exp(-radius * 12.0))
    result = np.real(np.fft.ifft2(spectrum * keep))
    result -= result.mean()
    return result / (result.std() + 1e-12)


def _normal_from_height(height_map, slope):
    """Relief image in the engine's convention (green points down the image). The heights are
    scaled so that the typical (root mean square) slope of the surface is `slope`."""
    du = (np.roll(height_map, -1, axis=1) - np.roll(height_map, 1, axis=1)) * 0.5
    dv = (np.roll(height_map, -1, axis=0) - np.roll(height_map, 1, axis=0)) * 0.5
    scale = slope / (np.sqrt((du * du + dv * dv).mean()) + 1e-12)
    du, dv = du * scale, dv * scale
    length = np.sqrt(du * du + dv * dv + 1.0)
    normal = np.stack([-du / length, -dv / length, 1.0 / length], axis=2)
    return Image.fromarray(np.round((normal * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")


def flat_name(rgb):
    return "T_W1529_P12_Flat_%02X%02X%02X_C" % tuple(rgb)


def flat_colour(rgb, folder, size=1024):
    """A plain colour (sRGB 0-255) with a slow unevenness of about 1 % and a grain of about 0.5 %,
    so that a painted or coated face is not one dead value. Field 1 m, 1,024 pixels per metre."""
    name = flat_name(rgb)
    path = os.path.join(folder, name + ".png")
    note = "plain colour sRGB %d,%d,%d with 1 %% slow unevenness and 0.5 %% grain" % tuple(rgb)
    if not os.path.exists(path):
        seed = _seed(name)
        slow = _filtered_noise((size, size), seed, size / 3.0, size / 3.0)
        grain = _filtered_noise((size, size), seed + 1, 1.5, 1.5)
        factor = 1.0 + 0.010 * slow + 0.005 * grain
        linear = _to_linear(np.array(rgb, dtype=np.float64) / 255.0)[None, None, :] * factor[:, :, None]
        Image.fromarray(np.round(_to_srgb(linear) * 255).astype(np.uint8), "RGB").save(path)
    return [path, name, "colour", (1.0, 1.0), note]


def eggshell_normal(folder, size=1024):
    """The fine stipple of rolled wall paint: bumps of about 3 mm, over a field of 0.5 m."""
    name = "T_W1529_P12_Eggshell_N"
    path = os.path.join(folder, name + ".png")
    if not os.path.exists(path):
        height_map = _filtered_noise((size, size), 1201, 6.0, 6.0, band=True)
        _normal_from_height(height_map, 0.10).save(path)
    return [path, name, "normal", (0.5, 0.5), "roller stipple, bumps of about 3 mm, made by this phase"]


def brushed(folder, size=1024):
    """Brushed metal over a field of 0.25 m: fine scratches that run along U. Returns the relief
    image and the roughness image (red, between 0.80 and 1.0, to be multiplied by RoughnessScale)."""
    names = ("T_W1529_P12_Brushed_N", "T_W1529_P12_Brushed_R")
    paths = [os.path.join(folder, n + ".png") for n in names]
    if not all(os.path.exists(p) for p in paths):
        scratches = _filtered_noise((size, size), 1202, 220.0, 1.2)
        long_waves = _filtered_noise((size, size), 1203, 500.0, 6.0)
        height_map = 0.8 * scratches + 0.2 * long_waves
        _normal_from_height(height_map, 0.12).save(paths[0])
        rough = np.clip(0.90 + 0.045 * scratches + 0.02 * long_waves, 0.78, 1.0)
        grey = np.round(rough * 255).astype(np.uint8)
        Image.fromarray(np.stack([grey, grey, grey], axis=2), "RGB").save(paths[1])
    note = "brushed scratches along U, made by this phase"
    return [[paths[0], names[0], "normal", (0.25, 0.25), note], [paths[1], names[1], "mask", (0.25, 0.25), note]]


def seamless_crop(source, folder, name, band=0.12, out_size=(2048, 2048)):
    """Makes a photograph repeat without a seam: a strip along the right and the bottom edge is
    faded over the opposite edge, and the image becomes smaller by that strip. Returns the item and
    the share of the source that one repeat now covers (1 - band, in both directions)."""
    path = os.path.join(folder, name + ".png")
    if not os.path.exists(path):
        image = np.asarray(Image.open(source).convert("RGB"), dtype=np.float64)
        height, width = image.shape[:2]
        bu, bv = int(round(width * band)), int(round(height * band))
        ramp = (np.arange(bu) + 0.5) / bu
        ramp = ramp * ramp * (3.0 - 2.0 * ramp)
        body = image[:, :width - bu].copy()
        body[:, :bu] = image[:, width - bu:] * (1.0 - ramp)[None, :, None] + image[:, :bu] * ramp[None, :, None]
        ramp = (np.arange(bv) + 0.5) / bv
        ramp = ramp * ramp * (3.0 - 2.0 * ramp)
        result = body[:height - bv].copy()
        result[:bv] = body[height - bv:] * (1.0 - ramp)[:, None, None] + body[:bv] * ramp[:, None, None]
        picture = Image.fromarray(np.round(result).astype(np.uint8), "RGB").resize(out_size, Image.LANCZOS)
        picture.save(path)
    return [path, name, "colour", None, "the Revit export's image, edges faded into each other over %d %%" % round(band * 100)]


def limestone_blend(folder, size=2048):
    """Large soft zones for Indiana Limestone Full Color Blend ("warm buff colors and medium gray
    tones", Polycor). A ratio image: grey 0.5 means no change; the stone parent multiplies the fine
    image by twice this value. Zones lie flat, as quarry beds do, and are about 2 to 6 m long over a
    field of 24.4 m, larger than any wall of the building."""
    name = "T_W1529_P12_LimestoneBlend_M"
    path = os.path.join(folder, name + ".png")
    if not os.path.exists(path):
        zone = _filtered_noise((size, size), 1204, size / 7.0, size / 22.0)
        fine = _filtered_noise((size, size), 1205, size / 40.0, size / 90.0)
        shade = _filtered_noise((size, size), 1206, size / 10.0, size / 30.0)
        mix = 1.0 / (1.0 + np.exp(-(zone + 0.35 * fine) * 2.2))        # 0 = buff, 1 = grey
        buff = np.array([1.045, 1.000, 0.930])
        grey = np.array([0.930, 0.955, 0.985])
        ratio = buff[None, None, :] * (1.0 - mix)[:, :, None] + grey[None, None, :] * mix[:, :, None]
        ratio = ratio * (1.0 + 0.035 * shade)[:, :, None]
        Image.fromarray(np.round(np.clip(ratio * 0.5, 0.0, 1.0) * 255).astype(np.uint8), "RGB").save(path)
    return [path, name, "mask", (24.4, 24.4), "buff and grey zones, made by this phase from Polycor's description"]


def resample(source, folder, name, size):
    path = os.path.join(folder, name + ".png")
    if not os.path.exists(path):
        Image.open(source).convert("RGB").resize(size, Image.LANCZOS).save(path)
    return [path, name, "colour", None, "the Revit export's own image at a finer pixel grid"]


def contrast(source, folder, name, gain):
    """A colour image with its light-and-dark figure made `gain` times stronger around its own mean
    colour (the mean colour stays). For wood whose grain is too faint to read at room distance."""
    path = os.path.join(folder, name + ".png")
    if not os.path.exists(path):
        linear = _to_linear(np.asarray(Image.open(source).convert("RGB"), dtype=np.float64) / 255.0)
        mean = linear.reshape(-1, 3).mean(axis=0)
        result = mean[None, None, :] * np.clip(1.0 + gain * (linear / mean[None, None, :] - 1.0), 0.05, 4.0)
        Image.fromarray(np.round(_to_srgb(result) * 255).astype(np.uint8), "RGB").save(path)
    return [path, name, "colour", None, "figure made %.1f times stronger around the mean colour" % gain]


def mean_linear(path, limit=512):
    image = Image.open(path).convert("RGB")
    image.thumbnail((limit, limit))
    return _to_linear(np.asarray(image, dtype=np.float64) / 255.0).reshape(-1, 3).mean(axis=0).tolist()
