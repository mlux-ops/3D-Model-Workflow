"""Download the exact brass photo and create portable, uniform appearance maps."""
from pathlib import Path
import json
import hashlib
import requests
from PIL import Image

OUT = Path(__file__).resolve().parents[1]
REF = OUT / 'references'
TEXTURES = OUT / 'textures'
TEXTURES.mkdir(exist_ok=True)
sources = {
    'lightology_brass_original.jpg': 'https://www.lightology.com/img/prod/original/1241669.jpg',
    'lightology_brass_spec.pdf': 'https://www.lightology.com/index.php?module=pdf_specification_sheet&prod_id=1241669',
    'lightology_installation.pdf': 'https://www.lightology.com/img/prod/pdf/09052023-ig_arn2473pncg.pdf',
}
records = []
for name, url in sources.items():
    response = requests.get(url, timeout=45, headers={'User-Agent':'Mozilla/5.0'})
    response.raise_for_status()
    data = response.content
    if name.endswith('.pdf') and not data.startswith(b'%PDF-'):
        raise RuntimeError('Expected PDF bytes: ' + url)
    destination = REF / name
    destination.write_bytes(data)
    if name.endswith('.jpg'):
        with Image.open(destination) as image:
            image.verify()
    records.append({'file':str(destination), 'url':url, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()})
colors = {'Brenta_Hand_Rubbed_Antique_Brass_Color.png': (174,143,91),
          'Brenta_Clear_Glass_Color.png': (246,248,246),
          'Brenta_White_Diffuser_Color.png': (248,244,234)}
for name, rgb in colors.items():
    Image.new('RGB', (64,64), rgb).save(TEXTURES / name)
(REF / 'download_receipt.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
(TEXTURES / 'appearance_values.json').write_text(json.dumps(colors,indent=2),encoding='utf-8')
print(json.dumps({'downloaded': records,'maps':list(colors)},indent=2))
