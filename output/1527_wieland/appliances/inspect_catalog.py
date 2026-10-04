"""Summarize public resource references in preserved catalog HTML."""
from pathlib import Path
import re
import html
import json
ROOT = Path(__file__).resolve().parent
for path in ROOT.glob('*/source/official_page.html'):
    text = html.unescape(path.read_text(encoding='utf-8')).replace('\\u002F','/').replace('\\/','/')
    snippets = []
    for match in re.finditer(r'\.zip|CAD File|Product Specification|\.rfa', text, re.I):
        snippet = text[max(0,match.start()-180):match.end()+220]
        if snippet not in snippets:
            snippets.append(snippet)
    print(json.dumps({'item':path.parent.parent.name,'bytes':path.stat().st_size,'snippets':snippets[:24]}))
