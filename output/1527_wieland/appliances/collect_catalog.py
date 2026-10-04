"""Collect only public manufacturer product evidence and exposed CAD links."""
import concurrent.futures
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = {
    'miele_kwt6722is': 'https://www.mieleusa.com/product/11329860/24-built-in-wine-refrigerator-kwt-6722-is',
    'miele_kwtus7172f': 'https://www.mieleusa.com/product/12519520/24-built-under-wine-refrigerator-kwtus-7172-f',
    'miele_kfmc3858fd': 'https://www.mieleusa.com/product/12489440/42-mastercool-frenchdoor-bottom-mount-unit-kfmc-3858-fd-compatible-with-furniture-fronts',
    'miele_km3054_1g': 'https://www.mieleusa.com/product/11766750/gas-cooktop-km-3054-1',
    'miele_h7280bp': 'https://www.mieleusa.com/product/11968200/30-oven-h-7280-bp-obsidian-black',
    'miele_h7270bm': 'https://www.mieleusa.com/product/11968190/30-speed-oven-h-7270-bm-obsidian-black',
    'miele_g5051scvi': 'https://www.mieleusa.com/product/11636710/fully-integrated-dishwasher-g-5051-scvi-active-stainless-steel',
    'summit_sdhwc98pnr': 'https://www.summitappliance.com/catalog/model/SDHWC98PNR',
    'thermador_t18iw905sp': 'https://www.thermador.com/us/en/mkt-product/refrigeration/wine-refrigeration/T18IW905SP',
}

def collect(pair):
    slug, url = pair
    folder = ROOT / slug / 'source'
    folder.mkdir(parents=True, exist_ok=True)
    record = dict(slug=slug, url=url)
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read().decode('utf-8', errors='replace')
            record['final_url'] = response.url
        (folder / 'official_page.html').write_text(data, encoding='utf-8')
        links = []
        for match in re.finditer(r'(?:href|url)\s*[=:]\s*[\"\x27](.*?)[\"\x27]', data):
            target = html.unescape(match.group(1))
            if any(ext in target.lower() for ext in ('.zip', '.rfa', '.pdf', 'cadfile', 'cad-file')):
                context = re.sub('<[^>]+>', ' ', data[max(0, match.start()-350):match.end()+250])
                context = re.sub(r'\s+', ' ', html.unescape(context))
                if not any(x['url'] == target for x in links):
                    links.append({'url': target, 'context': context[-700:]})
        record.update(ok=True, links=links)
        (folder / 'links.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    except Exception as exc:
        record.update(ok=False, error=str(exc))
    return record

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(collect, PAGES.items()))
    (ROOT / 'catalog_sources.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    for record in records:
        selected = [x for x in record.get('links', []) if '.zip' in x['url'] or 'FS_' in x['url'] or 'CAD' in x['context']]
        print(json.dumps(dict(slug=record['slug'], ok=record['ok'], error=record.get('error'), links=selected)))
