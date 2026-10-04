"""Preserve public product pages and their explicitly linked technical resources.

No authentication, browser cookies, account creation, or license acceptance.
Only page content is downloaded here. Native files are handled separately.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import hashlib
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines, self.links, self.images = [], [], []
        self.anchor = None
        self.ignore = 0
        self.title, self.in_title = '', False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style'):
            self.ignore += 1
        if tag == 'title':
            self.in_title = True
        if tag == 'a' and attrs.get('href'):
            self.anchor = {'url': attrs['href'], 'label': ''}
        if tag == 'img':
            self.images.append({k: v for k, v in attrs.items() if k in ('src', 'data-src', 'alt')})
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.ignore = max(0, self.ignore - 1)
        if tag == 'title':
            self.in_title = False
        if tag == 'a' and self.anchor:
            self.links.append(self.anchor)
            self.anchor = None
    def handle_data(self, data):
        if self.ignore:
            return
        text = ' '.join(data.split())
        if self.in_title:
            self.title += text
        if text:
            self.lines.append(text)
            if self.anchor:
                self.anchor['label'] += text + ' '

def fetch(job):
    key, item_key, index, url = job
    folder = ROOT / item_key / 'source'
    folder.mkdir(parents=True, exist_ok=True)
    record = {'group': key, 'url': url, 'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(request, timeout=35) as response:
            content = response.read(8 * 1024 * 1024)
            record.update({'final_url': response.geturl(), 'content_type': response.headers.get('Content-Type', ''), 'http_status': response.status})
        text = content.decode('utf-8', errors='replace')
        parser = PageParser()
        parser.feed(text)
        stem = 'page_%02d' % index
        (folder / (stem + '.html')).write_bytes(content)
        (folder / (stem + '.txt')).write_text('\n'.join(parser.lines), encoding='utf-8')
        links = []
        for link in parser.links:
            target = urljoin(record['final_url'], html.unescape(link['url']))
            if re.search(r'revit|\.rfa(?:$|\?)|\.zip(?:$|\?)|\.pdf(?:$|\?)|spec.?sheet|installation|technical|cad|3d.file', target + ' ' + link['label'], re.I):
                entry = {'url': target, 'label': link['label'].strip()}
                if entry not in links:
                    links.append(entry)
        # Some first-party sites place their download URLs inside JSON values.
        for target in re.findall(r'https?[^\s\x22<>]+?\.(?:rfa|zip|pdf)(?:\?[^\s\x22<>]*)?', text, re.I):
            target = html.unescape(target.replace('\\/', '/'))
            if not any(x['url'] == target for x in links):
                links.append({'url': target, 'label': 'Embedded public download URL'})
        record.update({'title': parser.title, 'sha256': hashlib.sha256(content).hexdigest(),
                       'html_path': str(folder / (stem + '.html')), 'text_path': str(folder / (stem + '.txt')),
                       'technical_links': links, 'images': parser.images})
        (folder / (stem + '_resources.json')).write_text(json.dumps(record, indent=2), encoding='utf-8')
    except Exception as exc:
        record['error'] = str(exc)
        (folder / ('page_%02d_error.json' % index)).write_text(json.dumps(record, indent=2), encoding='utf-8')
    return record

def main():
    groups = json.loads((ROOT / 'GROUPS.json').read_text(encoding='utf-8'))['groups']
    selected = set(sys.argv[1:])
    jobs = []
    for group in groups:
        if selected and group['key'] not in selected:
            continue
        urls = group['urls'][:2]
        if not urls and re.fullmatch(r'[A-Z]{3}\d+', group['model']):
            urls = ['https://www.lightology.com/index.php?module=prod_detail&prod_id=' + re.sub('[^0-9]', '', group['model'])]
        for index, url in enumerate(urls):
            jobs.append((group['key'], group['canonical_item'], index, url))
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch, job) for job in jobs]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print('%s | %s | %s technical links' % (result['group'], result.get('error') or result.get('title', '')[:130], len(result.get('technical_links', []))), flush=True)
    (ROOT / 'SOURCE_COLLECTION.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print('Downloaded %d/%d pages' % (sum('error' not in r for r in results), len(results)))

if __name__ == '__main__':
    main()
