"""R022 controlled precision FIX2. Append exact old/new hashes, do not touch earlier rounds."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json"
d=json.loads(p.read_text(encoding="utf-8"))
assert "FIX1" in d and "FIX2" not in d
changes=[]
for rel,old in d["files"].items():
 q=ROOT/rel
 b=q.read_bytes()
 assert hashlib.sha256(b).hexdigest()==old["sha256"] and len(b)==old["bytes"]
 s=b.decode("utf-8")
 t=s
 if rel.startswith("research/"):
  t=t.replace("two pieces x 8.00 SF = 16 SF/box**.", "**two pieces x 8.00 SF = 16 SF/box**.")
 else:
  if "Riviera Oat" in t:
   t=t.replace("$3.99/SF is site/default online product rate, not Chicago store on-hand or project fixed quote.", "Riviera Oat vendor price is storefront-dependent: earlier $3.99/SF, latest inspected Camelback $4.39/SF; neither proves Chicago availability or a fixed project quote.")
   t=t.replace("theoretical old combined gross x earlier $3.99/SF storefront rate, NOT current Camelback price", "theoretical old combined gross × earlier $3.99/SF storefront rate (not the current inspected Camelback $4.39/SF)")
 if t!=s:
  q.write_text(t,encoding="utf-8",newline="\n")
  bb=q.read_bytes()
  after={"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
  d["files"][rel]=after
  changes.append(dict(path=rel,before=old,after=after))
d["FIX2"]={"reason":"Correct residual Riviera Oat site-default $3.99 claim and malformed source formatting; price is storefront-dependent $3.99 to $4.39","changes":changes}
p.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8",newline="\n")
print("FIX2",len(changes),"files re-signed; R018-R021 unchanged")
