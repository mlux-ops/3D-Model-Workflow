"""Preserve the exact linked brass product and locate its image/resources."""
from pathlib import Path
from urllib.parse import urljoin
import hashlib
import json
import re
import shutil
import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[1]
REF = OUT / 'references'
REF.mkdir(exist_ok=True)
OLD = ROOT / 'output' / 'lightology_20260923' / 'f03_1241670'
URL = 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241669'
session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0'
response = session.get(URL, timeout=45)
response.raise_for_status()
html = response.text
(REF / 'lightology_brass.html').write_text(html, encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text(' ', strip=True)
assert 'ARN 2473HAB-CG' in text and 'Hand-Rubbed Antique Brass' in text
(REF / 'lightology_brass.txt').write_text(text, encoding='utf-8')
images = sorted(set(urljoin(URL, v) for node in soup.find_all(['img', 'a'])
                    for key, v in node.attrs.items()
                    if key in ('src', 'href', 'data-src', 'data-zoom-image') and isinstance(v, str)
                    and any(t in v.lower() for t in ('1241669', 'arn2473', 'arn_2473'))))
links = sorted(set(urljoin(URL, a['href']) for a in soup.find_all('a', href=True)
                   if any(t in a['href'].lower() for t in ('.pdf', 'spec_sheet', 'install_guide'))))
for filename in ('lightology_line_reference.jpg', 'lightology_additional_reference.jpg',
                 'visualcomfort_arn2473_reference.rfa', 'visualcomfort_cb_arn2473.dwg'):
    shutil.copy2(OLD / 'source' / filename, REF / filename)
shutil.copy2(OLD / 'source_geometry_measurements.json', REF / 'manufacturer_component_measurements.json')
helper = ROOT / 'output' / 'lightology_20260923' / 'tools' / 'native_fixture_support.py'
shutil.copy2(helper, OUT / 'source' / 'native_fixture_support.py')
manifest = {'url': URL, 'sku': 'ARN 2473HAB-CG', 'finish': 'Hand-Rubbed Antique Brass',
            'image_candidates': images, 'technical_candidates': links,
            'source_html_sha256': hashlib.sha256(response.content).hexdigest(),
            'geometry_helper_source': str(helper)}
(REF / 'source_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest, indent=2))
