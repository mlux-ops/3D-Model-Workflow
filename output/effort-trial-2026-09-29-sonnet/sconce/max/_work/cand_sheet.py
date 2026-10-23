from PIL import Image, ImageDraw

M = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
names = ['below_left', 'above_left', 'below_right', 'above_right']
cell = 400
sheet = Image.new('RGB', (cell * 2, cell * 2 + 0), (255, 255, 255))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    im = Image.open('%s/_work/candidates/family_cand_%s.png' % (M, n)).convert('RGB')
    im.thumbnail((cell, cell), Image.LANCZOS)
    x = (i % 2) * cell + (cell - im.width) // 2
    y = (i // 2) * cell + (cell - im.height) // 2
    sheet.paste(im, (x, y))
    d.text(((i % 2) * cell + 6, (i // 2) * cell + 6), n, fill=(200, 0, 0))
sheet.save('%s/_work/thumbs/cand_sheet.png' % M)
print(sheet.size)
