"""Preserve exact Thermador CAD packages exposed in public product pages."""
import concurrent.futures
import json
import re
import sys
import urllib.request
from source_fetch import ROOT, fetch

PAGES = {
    'thermador_t18iw905sp': 'https://www.thermador.com/us/en/mkt-product/refrigeration/wine-refrigeration/T18IW905SP',
    'thermador_t42it100np': 'https://www.thermador.com/us/en/mkt-product/refrigeration/bottom-freezer-refrigerators/T42IT100NP',
    'thermador_t24ur905rp': 'https://www.thermador.com/us/en/mkt-product/refrigeration/refrigerationrefrigerationcolumns/T24UR905RP',
    'thermador_mc30wp': 'https://www.thermador.com/us/en/mkt-product/ovens/speed-ovens/MC30WP',
    'thermador_podmc301w': 'https://www.thermador.com/us/en/mkt-product/ovens/double-ovens/PODMC301W',
    'thermador_pcg486wd': 'https://www.thermador.com/us/en/mkt-product/cooktops-rangetops/rangetops/PCG486WD',
    'thermador_prd48wisgu': 'https://www.thermador.com/us/en/mkt-product/ranges/48-ranges/PRD48WISGU',
    'thermador_wd30w': 'https://www.thermador.com/us/en/mkt-product/ovens/warming-drawers/WD30W',
}

def collect(pair):
    slug, url = pair
    folder = ROOT / slug / 'source'
    folder.mkdir(parents=True, exist_ok=True)
    record = dict(slug=slug, url=url, resources=[])
    try:
        cached = folder / 'official_page.html'
        if cached.exists():
            data = cached.read_text(encoding='utf-8')
        else:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=45) as response:
                data = response.read().decode('utf-8', errors='replace')
            cached.write_text(data, encoding='utf-8')
        seen = set()
        for match in re.finditer(r'https://media3\.bsh-group\.com/(?:Documents|3D_Asset)/[^\s\"\\<>]+\.(?:zip|pdf)', data):
            target = match.group(0)
            context = data[max(0,match.start()-700):match.end()]
            if target in seen:
                continue
            seen.add(target)
            if target.lower().endswith('.zip'):
                name = 'cad_' + target.rsplit('/', 1)[-1]
            elif 'bsh:category.product-specification' in context:
                name = 'product_sheet.pdf'
            else:
                continue
            resource = fetch((slug, name, target))
            record['resources'].append(resource)
        record['ok'] = True
        (folder / 'download_evidence.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    except Exception as exc:
        record.update(ok=False,error=str(exc))
    return record

if __name__ == '__main__':
    chosen = [p for p in PAGES.items() if not sys.argv[1:] or p[0] in sys.argv[1:]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(collect, chosen))
    output = 'thermador_downloads_extra.json' if sys.argv[1:] else 'thermador_downloads.json'
    (ROOT / output).write_text(json.dumps(records, indent=2), encoding='utf-8')
    for record in records:
        print(json.dumps({'slug':record['slug'],'ok':record['ok'],'error':record.get('error'),
                          'resources':[{k:v for k,v in r.items() if k in ('url','size','ok','error','entries')} for r in record['resources']]}))
