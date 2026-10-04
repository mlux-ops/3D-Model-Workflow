"""Capture public manufacturer source evidence for every inventory SKU.

No credentials, form submissions, terms acceptance, or account endpoints are used.
The files are source evidence; discovering a link does not validate its model.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

SECTION = Path(__file__).resolve().parents[1]
RESEARCH = SECTION / '_research'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.texts = []
        self.title = ''
        self.in_title = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.in_title = True
        for key in ['href', 'src', 'data-url', 'data-src', 'data-download-url']:
            if attrs.get(key):
                self.links.append({'tag': tag, 'attribute': key, 'url': attrs[key],
                                   'label': attrs.get('title', attrs.get('alt', ''))})
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
    def handle_data(self, text):
        if self.in_title:
            self.title += text
        if text.strip():
            self.texts.append(text.strip())


def canonical_sku(row):
    model = (row.get('model_number') or '').strip()
    if 'CORRECTION 2026-10-01:' in model:
        model = model.split('CORRECTION 2026-10-01:', 1)[1].strip()
    return re.sub(r'\s+', ' ', model)


def slug(value):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', value).strip('_')[:110]


def inventory():
    data = json.loads((SECTION / 'ITEMS.json').read_text(encoding='utf-8-sig'))
    groups = {}
    for row in data['items']:
        sku = canonical_sku(row)
        key = sku or 'ROW_' + str(row['row_id'])
        if key not in groups:
            groups[key] = {'sku': sku, 'key': slug(key), 'rows': []}
        groups[key]['rows'].append(row)
    result = list(groups.values())
    (RESEARCH / 'groups.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    return result


def candidate_urls(group):
    row = group['rows'][0]
    sku = group['sku']
    if not sku:
        return []
    brand = (row.get('manufacturer') or '').lower()
    urls = []
    if brand == 'brizo':
        for part in re.split(r'[, ]+', sku):
            if not part:
                continue
            section = 'kitchen' if row.get('room_type') == 'Kitchen' else 'bath'
            urls.append('https://www.brizo.com/' + section + '/product/' + urllib.parse.quote(part))
    elif brand in ['hansgrohe', 'axor']:
        domain = 'www.axor-design.com/us' if brand == 'axor' else 'pro.hansgrohe-usa.com'
        # The manufacturer's documented compact product URL redirects to the full title.
        urls.append('https://' + domain + '/articledetail--' + sku)
    for source in group['rows']:
        for url in source.get('product_urls', []):
            host = urllib.parse.urlsplit(url).hostname or ''
            if not any(bad in host for bad in ['ferguson', 'faucetdirect']):
                urls.append(url)
    return list(dict.fromkeys(urls))


def fetch(url, folder, label):
    record = {'url': url, 'fetched_at': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(request, timeout=35) as response:
            payload = response.read(16 * 1024 * 1024)
            record.update(final_url=response.url, status=response.status,
                          content_type=response.headers.get('Content-Type', ''), bytes=len(payload))
        suffix = '.pdf' if payload.startswith(b'%PDF') else '.html'
        target = folder / (label + suffix)
        target.write_bytes(payload)
        record.update(path=str(target), sha256=hashlib.sha256(payload).hexdigest())
        if suffix == '.html':
            parser = Links()
            parser.feed(payload.decode('utf-8', 'replace'))
            text = '\n'.join(parser.texts)
            (folder / (label + '.txt')).write_text(text, encoding='utf-8')
            links = []
            seen = set()
            for link in parser.links:
                resolved = urllib.parse.urljoin(record['final_url'], html.unescape(link['url']))
                if resolved in seen:
                    continue
                seen.add(resolved)
                links.append(dict(link, url=resolved))
            record['title'] = parser.title
            record['links'] = links
            record['asset_links'] = [link for link in links if re.search(r'(?i)\.rfa|\.zip|\.pdf|\.dwg|\.dxf|bimsmith|bimobject|cad|download|celum', link['url'])]
    except Exception as exc:
        record.update(error=type(exc).__name__ + ': ' + str(exc))
    (folder / (label + '.json')).write_text(json.dumps(record, indent=2), encoding='utf-8')
    return record


def discover_group(group):
    folder = RESEARCH / group['key']
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for i, url in enumerate(candidate_urls(group)):
        label = 'page_%02d' % i
        existing = folder / (label + '.json')
        if existing.exists():
            record = json.loads(existing.read_text(encoding='utf-8'))
        else:
            record = fetch(url, folder, label)
        records.append(record)
    result = {'sku': group['sku'], 'key': group['key'], 'row_ids': [str(r['row_id']) for r in group['rows']], 'pages': records}
    (folder / 'sources.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--only', default='')
    args = parser.parse_args()
    RESEARCH.mkdir(exist_ok=True)
    groups = inventory()
    if args.only:
        groups = [g for g in groups if g['sku'] in args.only.split('|')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for result in executor.map(discover_group, groups):
            counts = sum(len(page.get('asset_links', [])) for page in result['pages'])
            failures = [page.get('error') for page in result['pages'] if page.get('error')]
            print(json.dumps({'sku': result['sku'], 'rows': len(result['row_ids']), 'asset_links': counts, 'errors': failures}), flush=True)
    print('Source discovery complete: %s groups' % len(groups), flush=True)


if __name__ == '__main__':
    main()
