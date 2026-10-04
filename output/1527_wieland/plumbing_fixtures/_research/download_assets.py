"""Download explicit public manufacturer assets, preserving hashes and origin."""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
MAX_BYTES = 100 * 1024 * 1024
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36'


def download(task):
    url = task['url'].replace(' ', '%20')
    target_folder = ROOT / task['key'] / 'downloads'
    target_folder.mkdir(parents=True, exist_ok=True)
    filename = re.sub(r'[^A-Za-z0-9_.-]+', '_', task.get('filename') or urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit('/', 1)[-1]))
    filename = filename[:150] or 'download.bin'
    target = target_folder / filename
    receipt = target_folder / (filename + '.receipt.json')
    if receipt.exists():
        previous = json.loads(receipt.read_text(encoding='utf-8'))
        if previous.get('sha256') and target.exists():
            return previous
    result = dict(task, requested_url=url, fetched_at=time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=45) as response:
            payload = response.read(MAX_BYTES + 1)
            if len(payload) > MAX_BYTES:
                raise ValueError('Asset exceeds 100 MB bound')
            result.update(final_url=response.url, http_status=response.status, content_type=response.headers.get('Content-Type'))
        magic = payload[:8]
        kind = 'PDF' if magic.startswith(b'%PDF') else 'ZIP' if magic.startswith(b'PK\x03\x04') else 'COMPOUND_DOCUMENT' if magic == bytes.fromhex('d0cf11e0a1b11ae1') else 'OTHER'
        if b'<html' in payload[:4096].lower() or b'<!doctype html' in payload[:4096].lower():
            raise ValueError('HTML response instead of requested asset')
        target.write_bytes(payload)
        result.update(path=str(target), bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest(), detected_kind=kind,
                      terms_note='Public asset linked by manufacturer. No login, account creation, or terms acceptance performed; manufacturer intellectual-property rights retained.')
        if kind == 'ZIP':
            extracted = []
            with zipfile.ZipFile(target) as archive:
                result['archive_members'] = archive.namelist()
                for member in archive.infolist():
                    if member.is_dir() or member.file_size > MAX_BYTES:
                        continue
                    name = Path(member.filename.replace('\\', '/')).name
                    if Path(name).suffix.lower() not in ['.rfa', '.txt', '.pdf', '.dwg', '.dxf', '.stp', '.step', '.sat']:
                        continue
                    safe = re.sub(r'[^A-Za-z0-9_.-]+', '_', name)
                    output = target_folder / (target.stem + '_files') / safe
                    output.parent.mkdir(exist_ok=True)
                    file_data = archive.read(member)
                    output.write_bytes(file_data)
                    extracted.append({'path': str(output), 'bytes': len(file_data), 'sha256': hashlib.sha256(file_data).hexdigest(), 'member': member.filename})
            result['extracted'] = extracted
    except Exception as exc:
        result['error'] = type(exc).__name__ + ': ' + str(exc)
    receipt.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue', default=str(ROOT / 'asset_queue.json'))
    args = parser.parse_args()
    tasks = json.loads(Path(args.queue).read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(download, tasks):
            print(json.dumps({k: result.get(k) for k in ['key', 'path', 'detected_kind', 'bytes', 'error', 'archive_members']}), flush=True)


if __name__ == '__main__':
    main()
