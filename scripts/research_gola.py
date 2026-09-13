"""Preserve public Richelieu accessory source pages and linked drawings."""
import json, re, urllib.request
from pathlib import Path
from html import unescape
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'references'/'gola'
base = 'https://www.richelieu.com/us/en/category/moldings-corbels-and-components/metal-and-pvc-moldings-profiles-and-rails/gola-cabinet-profiles/'
pages = {
 'closed_c':'gola-left-right-closed-end-caps-for-profile-non-led/1299414',
 'closed_l':'gola-left-right-closed-end-caps-for-profile-non-led/1299413',
 'open_l':'gola-open-left-and-right-end-caps-for-profile/1182713',
 'open_c':'gola-open-right-and-left-end-caps-for-profile/1182702',
 'internal_l':'gola-internal-90-joint-for-profile/1182715',
 'external_l':'gola-external-90-joint-for-profile/1182714/sku-7001015E10',
 'internal_c':'gola-internal-90-joint-for-profile/1182720/sku-7001016I10',
 'external_c':'gola-external-90-joint-for-profile/1182719/sku-7001016E10',
}
results={}
for key, tail in pages.items():
 try:
  data=urllib.request.urlopen(base+tail,timeout=25).read()
  (OUT/(key+'.html')).write_bytes(data)
  html=data.decode('utf-8','replace')
  cleaned=re.sub(r'<(script|style)\b.*?</\1>', '', html, flags=re.S|re.I)
  content='\n'.join(s.strip() for s in unescape(re.sub(r'<[^>]+>','\n',cleaned)).splitlines() if s.strip())
  at=content.find('TECHNICAL SPECIFICATIONS')
  selected=content[max(0,at-2000):at+2800] if at>=0 else content[-5000:]
  pdfs=sorted(set(unescape(s) for s in re.findall(r'href=[\"\x27]([^\"\x27]+\.pdf[^\"\x27]*)',html)))
  results[key]={'url':base+tail,'text':selected,'pdfs':pdfs}
 except Exception as e: results[key]={'error':str(e)}
(OUT/'accessory_sources.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
