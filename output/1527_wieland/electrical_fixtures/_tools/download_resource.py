"""Download an explicitly sourced public resource, preserving acquisition evidence."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote, urlsplit, urlunsplit
import datetime
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]

def download(group_key, url, filename, provenance):
    groups = {g['key']: g for g in json.loads((ROOT / 'GROUPS.json').read_text())['groups']}
    target = ROOT / groups[group_key]['canonical_item'] / 'source' / filename
    if target.exists():
        raise RuntimeError('Existing resource preserved: ' + str(target))
    record = {'url': url, 'linked_from': provenance, 'retrieved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'terms_note': 'Anonymous public download. No sign-in, account creation, or license acceptance submitted. Manufacturer copyright retained.'}
    try:
        parts = urlsplit(url)
        safe_url = urlunsplit((parts.scheme, parts.netloc, quote(parts.path, safe='/%:@'), parts.query, parts.fragment))
        with urlopen(Request(safe_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as response:
            data = response.read(100 * 1024 * 1024)
            record.update({'final_url': response.geturl(), 'content_type': response.headers.get('Content-Type'), 'content_disposition': response.headers.get('Content-Disposition')})
        record.update({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'signature_hex': data[:12].hex(), 'path': str(target)})
        target.write_bytes(data)
    except Exception as exc:
        record['error'] = str(exc)
    target.with_suffix(target.suffix + '.acquisition.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record, indent=2))
    return record

if __name__ == '__main__':
    download(*sys.argv[1:5])
