from pathlib import Path
R=Path(__file__).resolve().parents[1]
for rid in ('PH-BATH3','TX-BATH3'):
 for p in (R/'rooms'/rid/'board/round-011/candidates').glob('*.md'):
  t=p.read_text(encoding='utf-8')
  t=t.replace('individually maker Wet Areas-listed wet field and niche, replacing unlisted Opal','individually maker Wet Areas-listed wet field and niche; separate Opal source wet listing is absent')
  t=t.replace('individually maker Wet Areas-listed retained wet field','individually maker Wet Areas-listed wet field')
  t=t.replace('[Tones Opal](https://www.elmsurfaces.com/product/opal-tones)','[Tones collection](https://www.elmsurfaces.com/product-collection/tones) (individual Opal wet approval unverified)')
  p.write_text(t,encoding='utf-8')
  print(rid,p.name,p.stat().st_size)
print('PASS draft normalized before freezing; no private keys/receipts created')
