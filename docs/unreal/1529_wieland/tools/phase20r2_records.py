"""Phase 20 round 2: the photographs used, into asset_downloads.csv (rows "Phase 20 round 2 reference photograph")
and one group row into asset_licence_groups.csv, as round 1's tools/phase20_records.py did. Run once; a row whose
name is already there is not added again.

Usage:  python -B phase20r2_records.py
"""
import csv
import os

DOCS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USED = os.path.join(DOCS, 'review', 'phase20', 'round2', 'photographs_used_r2.csv')
INDEXES = [r'E:/Wieland1529_site_data/phase20/round2/round2_index.csv',
           os.path.join(DOCS, 'review', 'phase20', 'commons_index.csv')]
DOWNLOADS = os.path.join(DOCS, 'asset_downloads.csv')
GROUPS = os.path.join(DOCS, 'asset_licence_groups.csv')


def norm(t):
    t = (t or '').strip()
    return t[5:] if t.startswith('File:') else t


def main():
    index = {}
    for path in INDEXES:
        if not os.path.exists(path):
            continue
        for r in csv.DictReader(open(path, encoding='utf-8')):
            index.setdefault(norm(r.get('title')), r)
    used = list(csv.DictReader(open(USED, encoding='utf-8')))
    existing = {r['name'] for r in csv.DictReader(open(DOWNLOADS, encoding='utf-8'))}
    rows, total_bytes = [], 0
    for u in used:
        title = norm(u['title'])
        name = 'Phase 20 round 2 reference photograph: ' + title
        if name in existing:
            continue
        ix = index.get(title, {})
        size = int(ix.get('bytes') or 0)
        total_bytes += size
        lic = u['licence'] or ix.get('licence', '')
        url = ix.get('licence_url', '')
        sa = 'BY-SA' in lic
        rows.append({
            'name': name, 'files': 1, 'size_mb': round(size / 1e6, 2),
            'what_it_is': 'Photograph used to judge cladding, colour, window grid or crown (%s); reference only, never shipped or traced' % (u.get('use') or 'facade'),
            'source': 'Wikimedia Commons, %s, gathered 2026-11-14 and 15 for round 2' % (u['page_url'] or ix.get('page_url', '')),
            'licence': '%s (%s)' % (lic, url) if url else lic,
            'evidence_or_note': 'Author: %s. Attribution kept here%s' % (u['author'] or ix.get('author', 'not given'),
                                 '; share-alike does not attach because nothing is shipped or adapted.' if sa else '.'),
            'kept_at': (ix.get('file') or '').replace('\\', '/') or 'not kept locally (looked at on its file page)'})
    if rows:
        with open(DOWNLOADS, 'a', newline='', encoding='utf-8') as h:
            w = csv.DictWriter(h, fieldnames=['name', 'files', 'size_mb', 'what_it_is', 'source', 'licence', 'evidence_or_note', 'kept_at'], lineterminator='\n')
            w.writerows(rows)
    groups = list(csv.DictReader(open(GROUPS, encoding='utf-8')))
    gname = 'Phase 20 round 2 reference photographs (Wikimedia Commons)'
    if not any(g['group'] == gname for g in groups):
        with open(GROUPS, 'a', newline='', encoding='utf-8') as h:
            w = csv.DictWriter(h, fieldnames=list(groups[0].keys()), lineterminator='\n')
            w.writerow({'group': gname, 'status': 'reference only, not shipped', 'files': len(used),
                        'size_mb': round(total_bytes / 1e6, 1),
                        'what_it_is': 'Photographs of the 27 sightline-sheet landmarks, the skyline towers and Old Town, looked at to set material colours, window grids and crowns (round 2)',
                        'source': 'Wikimedia Commons, gathered 2026-11-14 and 15 (review/phase20/round2/photographs_used_r2.csv)',
                        'licence': 'CC0, public domain, CC BY, CC BY-SA (per file)',
                        'evidence_or_note': 'CC BY and CC BY-SA need attribution: author and file page are listed per file in asset_downloads.csv. No photograph is used as a texture or traced, so share-alike does not reach the delivery.',
                        'example': norm(used[0]['title']) if used else ''})
    print('rows added', len(rows), 'of', len(used), 'bytes', total_bytes)


if __name__ == '__main__':
    main()
