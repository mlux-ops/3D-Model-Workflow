"""Controlled R022 FIX1 for store-variable Riviera Oat price. No predecessor writes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
receipt=R/"state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json"
d=json.loads(receipt.read_text(encoding="utf-8"))
assert "FIX1" not in d
changes=[]
for rel,old in d["files"].items():
 p=R/rel
 raw=p.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==old["sha256"] and len(raw)==old["bytes"]
 s=raw.decode("utf-8")
 t=s
 if rel.startswith("research/"):
  t=t.replace("Store-dependent posted **$3.99/SF; $63.84/box;", "Store-dependent verified current Camelback listing **$4.39/SF; $70.24/box**; another recent storefront snapshot showed **$3.99/SF; $63.84/box**, so neither price is a Chicago quote;")
  t=t.replace("**$3.99/SF; $63.84/box;", "**$4.39/SF; $70.24/box** (Camelback current), previously **$3.99/SF; $63.84/box** from another store;")
 else:
  if "Riviera Oat" in t:
   t=t.replace("current online $3.99/SF", "store-dependent observed $3.99–$4.39/SF (Camelback current $4.39; not Chicago)")
   t=t.replace("current online $3.99", "store-dependent $3.99–$4.39 (Camelback $4.39)")
   t=t.replace("current online $3.99/SF", "store-dependent $3.99–$4.39/SF")
   t=t.replace("current online $3.99/SF", "store-dependent $3.99–$4.39/SF")
   t=t.replace("current online $3.99", "store-dependent $3.99–$4.39")
   t=t.replace("online $3.99/SF", "online $3.99–$4.39/SF (store dependent)")
   t=t.replace("The brand's online box rate $63.84", "The Camelback online box rate $70.24 (earlier other-store $63.84)")
   # Old gross example is specifically based on 3.99; label historical storefront, no invented new shopping total.
   t=t.replace("illustrative old combined gross x posted rate", "illustrative old combined gross x earlier $3.99/SF storefront rate, NOT current Camelback price")
 if t!=s:
  p.write_text(t,encoding="utf-8",newline="\n")
  b=p.read_bytes()
  new={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
  d["files"][rel]=new
  changes.append({"path":rel,"before":old,"after":new})
d["FIX1"]={"reason":"Floor & Decor Riviera Oat 24x48 price varies across seller stores; 2026-11-06 Camelback page shows $4.39/SF $70.24/box, earlier different storefront showed $3.99/SF $63.84/box; neither Chicago stock/price","changes":changes}
receipt.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8",newline="\n")
print("R022 FIX1",len(changes),"signed price-clarification changes; all signed R018-R021 parents untouched")
