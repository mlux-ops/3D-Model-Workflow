"""Stage 3: measure gates on textures/Color.png and write review images + report.json."""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.join(ROOT, '_work')
TEX = os.path.join(ROOT, 'textures')
FACE_W, FACE_H, JOINT = 3072, 1536, 4
CELL_W, CELL_H = FACE_W + JOINT, FACE_H + JOINT
JOINT_RGB = np.array([209, 209, 209])


def font(sz):
    for f in ['arialbd.ttf', 'arial.ttf', 'DejaVuSans-Bold.ttf']:
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def step(a, b):
    return float(np.abs(a.astype(np.int32) - b.astype(np.int32)).mean())


def main():
    im = Image.open(os.path.join(TEX, 'Color.png'))
    fmt = {'size': list(im.size), 'mode': im.mode, 'format': im.format,
           'bits_per_channel': 8 if im.mode == 'RGB' else None}
    a = np.asarray(im)
    H, W = a.shape[:2]
    faces = {}
    for i in range(3):
        for j in range(3):
            y, x = i * CELL_H + 2, j * CELL_W + 2
            faces[f'r{i}c{j}'] = a[y:y + FACE_H, x:x + FACE_W]

    # ---- joint check ----
    jmask = np.ones((H, W), bool)
    for i in range(3):
        for j in range(3):
            jmask[i * CELL_H + 2:i * CELL_H + 2 + FACE_H, j * CELL_W + 2:j * CELL_W + 2 + FACE_W] = False
    jpx = a[jmask]
    joint = {'joint_pixels': int(jmask.sum()),
             'all_joint_pixels_exact_209': bool((jpx == JOINT_RGB).all()),
             'joint_width_px_interior': 4, 'joint_width_px_at_wrap': '2 + 2 = 4',
             'joint_width_in': 4 / 64,
             'expected_joint_pixels': int(H * W - 9 * FACE_W * FACE_H),
             'face_pixels_equal_to_joint_colour': int(sum(((f == JOINT_RGB).all(2)).sum() for f in faces.values()))}

    # ---- wrap steps ----
    interior_h = np.mean([step(f[:, 1:], f[:, :-1]) for f in faces.values()])
    interior_v = np.mean([step(f[1:], f[:-1]) for f in faces.values()])
    wrap = {
        'LR_wrap_step_col_last_vs_col0': step(a[:, -1], a[:, 0]),
        'TB_wrap_step_row_last_vs_row0': step(a[-1], a[0]),
        'interior_face_neighbour_step_horizontal': interior_h,
        'interior_face_neighbour_step_vertical': interior_v,
        'interior_joint_internal_step_example': step(a[:, CELL_W - 1], a[:, CELL_W]),
        'across_wrap_joint_face_to_face_step_LR': step(a[2:-2, W - 3], a[2:-2, 2]),
        'across_interior_joint_face_to_face_step_LR': float(np.mean([step(a[2:-2, k * CELL_W - 3], a[2:-2, k * CELL_W + 2]) for k in (1, 2)])),
        'across_wrap_joint_face_to_face_step_TB': step(a[H - 3, 2:-2], a[2, 2:-2]),
        'across_interior_joint_face_to_face_step_TB': float(np.mean([step(a[k * CELL_H - 3, 2:-2], a[k * CELL_H + 2, 2:-2]) for k in (1, 2)])),
        'note': 'Atlas edges bisect a joint, so the wrap lands joint-to-joint (identical colour). '
                'Face-to-face steps across the wrap joint are compared with the same measure across interior joints.'}
    # tonal balance of faces near the wrap vs interior (mean luminance per face)
    lum = {k: float(v.mean()) for k, v in faces.items()}

    # ---- cross-cell similarity ----
    def small(f):
        g = np.asarray(Image.fromarray(f).convert('L').resize((384, 192), Image.BILINEAR), np.float64)
        return g
    sm = {k: small(v) for k, v in faces.items()}
    def ncc(x, y):
        x = x - x.mean(); y = y - y.mean()
        return float((x * y).sum() / np.sqrt((x * x).sum() * (y * y).sum()))
    keys = list(sm)
    pairs = []
    for ii in range(9):
        for jj in range(ii + 1, 9):
            x = sm[keys[ii]]
            best = max((ncc(x, v), n) for n, v in [('none', sm[keys[jj]]), ('fliph', sm[keys[jj]][:, ::-1]),
                                                  ('flipv', sm[keys[jj]][::-1]), ('rot180', sm[keys[jj]][::-1, ::-1])])
            pairs.append({'a': keys[ii], 'b': keys[jj], 'max_ncc': round(best[0], 4), 'variant': best[1]})
    pairs.sort(key=lambda p: -p['max_ncc'])
    # repeated-feature search: best normalized match of 5-in blocks from one face anywhere in other faces
    # (dihedral variants), sampled; uses 1/8 scale grayscale with local mean removed
    def g8(f):
        g = np.asarray(Image.fromarray(f).convert('L').resize((FACE_W // 8, FACE_H // 8), Image.BOX), np.float64)
        return g
    from scipy.signal import fftconvolve
    g = {k: g8(v) for k, v in faces.items()}
    rng = np.random.default_rng(1)
    B = 40   # 40 px at 1/8 scale = 320 px = 5 in
    rep = []
    for k in keys:
        for _ in range(6):
            y = int(rng.integers(0, g[k].shape[0] - B)); x = int(rng.integers(0, g[k].shape[1] - B))
            blk = g[k][y:y + B, x:x + B]
            blk = blk - blk.mean(); nb = np.sqrt((blk ** 2).sum())
            best = (-1, None)
            for k2 in keys:
                if k2 == k:
                    continue
                img = g[k2]
                s1 = fftconvolve(img, np.ones((B, B)), 'valid'); s2 = fftconvolve(img ** 2, np.ones((B, B)), 'valid')
                var = np.maximum(s2 - s1 ** 2 / B ** 2, 1e-6)
                for v in [blk, blk[::-1], blk[:, ::-1], blk.T, blk[::-1, ::-1], np.rot90(blk), np.rot90(blk, 3), blk[::-1].T]:
                    c = fftconvolve(img, v[::-1, ::-1], 'valid') / (nb * np.sqrt(var))
                    m = float(c.max())
                    if m > best[0]:
                        best = (m, k2)
            rep.append(round(best[0], 3))
    rep = np.array(rep)

    cells_json = json.load(open(os.path.join(WORK, 'build_cells.json')))
    src_meta = json.load(open(os.path.join(WORK, 'sources_meta.json')))
    report = {'format': fmt, 'revit_sample_size_in': [144.1875, 72.1875], 'px_per_in': 64,
              'joint': joint, 'wrap': wrap, 'face_mean_values': lum,
              'cross_cell_similarity': {'method': 'Pearson NCC of whole faces, grayscale 384x192, '
                                                  'variants none/fliph/flipv/rot180', 'max': pairs[0], 'top5': pairs[:5]},
              'block_repeat_search': {'method': '54 random 5x5 in blocks (1/8 scale, 8 dihedral variants) searched '
                                                'in every other face; best normalized cross-correlation',
                                      'max': float(rep.max()), 'median': float(np.median(rep)),
                                      'count_over_0.9': int((rep > 0.9).sum()), 'count_over_0.8': int((rep > 0.8).sum())},
              'sources': src_meta,
              'floor_perspective_validation': json.load(open(os.path.join(WORK, 'floor_validation.json'))),
              'floor_photo_usage': 'Rectified and used for scale/geometry validation only; no floor pixels in Color.png '
                                   '(native forward resolution 5.6-10.3 px/in would need 6-11x upsampling to 64 px/in).',
              'build': cells_json}
    json.dump(report, open(os.path.join(TEX, 'report.json'), 'w'), indent=1)

    # ---- review images ----
    Image.fromarray(a).resize((W // 4, H // 4), Image.LANCZOS).save(os.path.join(TEX, '_PREVIEW_atlas_full.jpg'), quality=92)
    small4 = np.asarray(Image.fromarray(a).resize((W // 6, H // 6), Image.LANCZOS))
    Image.fromarray(np.tile(small4, (2, 2, 1))).save(os.path.join(TEX, '_PREVIEW_wrap_2x2.jpg'), quality=92)
    r = 160
    corner = np.tile(a, (2, 2, 1))[H - r:H + r, W - r:W + r]
    Image.fromarray(corner).resize((r * 2 * 4, r * 2 * 4), Image.NEAREST).save(os.path.join(TEX, '_REVIEW_wrap_seam.jpg'), quality=95)
    tw, th = 1024, 512
    sheet = Image.new('RGB', (3 * tw + 4 * 16, 3 * th + 4 * 16), (60, 60, 60))
    d = ImageDraw.Draw(sheet)
    fnt = font(34)
    for i in range(3):
        for j in range(3):
            k = f'r{i}c{j}'
            sheet.paste(Image.fromarray(faces[k]).resize((tw, th), Image.LANCZOS), (16 + j * (tw + 16), 16 + i * (th + 16)))
            d.rectangle([16 + j * (tw + 16), 16 + i * (th + 16), 16 + j * (tw + 16) + 120, 16 + i * (th + 16) + 48], fill=(20, 20, 20))
            d.text((24 + j * (tw + 16), 22 + i * (th + 16)), k, fill=(255, 220, 0), font=fnt)
    sheet.save(os.path.join(TEX, '_REVIEW_cell_grid.jpg'), quality=92)
    print(json.dumps({k: report[k] for k in ['format', 'joint', 'wrap', 'cross_cell_similarity', 'block_repeat_search']}, indent=1))


if __name__ == '__main__':
    main()
