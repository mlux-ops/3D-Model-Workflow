"""Controlled R023 fixes for N/A pan/floor scope; previous signed rounds untouched."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
rec=ROOT/"state/ROUND023_ALLROOM_UPDATED_VENDOR_OWNER_PREVIEWS_SHA.json"
d=json.loads(rec.read_text(encoding="utf8"))
assert "FIX1" not in d
powder={"PH-POWDER","TX-POWDER","TX-POWDER2"}
tub={"PH-BATH2","TX-BATH2","TX-BATH4"}
wc={"PH-WC","TX-WC"}
changes=[]
for path,meta in d["files"].items():
 p=ROOT/path;b=p.read_bytes()
 assert hashlib.sha256(b).hexdigest()==meta["sha256"] and len(b)==meta["bytes"]
 s=b.decode("utf8");t=s
 rid=path.split("/")[-1].split(".")[0]
 if path.endswith("vendor_comparison_R023_current.md") and rid in powder:
  a=t.index("## LEVEL floor options")
  c=t.index("Historic signed vendor_comparison.md",a)
  t=t[:a]+"**FLOOR:** ORIGINAL WOOD throughout. All floor tile options are NOT APPLICABLE to this powder room. Wet-floor DCOF and tiled PAN N/A.\n\n"+t[c:]
 if path.startswith("deliverables/"):
  phrase="Installer-cut PAN replacement scenario requires true native net LEVEL vs PAN area, with separate **illustrative 15% LEVEL / 25% PAN waste assumptions**, not quantities authorized for purchase."
  if rid in powder: t=t.replace(phrase,"DRY powder feature WALL only; original WOOD floor remains. No tiled LEVEL floor or shower PAN quantity.")
  if rid in tub: t=t.replace(phrase,"Selected Duravit TUB; no tiled shower PAN exists, and historical FLOOR original gross includes 15% waste once.")
  if rid in wc: t=t.replace(phrase,"WC floor inherits its PRIMARY LEVEL material exactly once and has no independent tiled PAN or floor order.")
 if t!=s:
  p.write_text(t,encoding="utf8",newline="\n");new=p.read_bytes()
  newer={"sha256":hashlib.sha256(new).hexdigest(),"bytes":len(new)}
  changes.append({"path":path,"before":meta,"after":newer})
  d["files"][path]=newer
d["FIX1"]={"reason":"Remove generic mosaic/PAN or tile-floor requirements from Duravit tub, dry powder and inherited WC owner pages; keep source-only artifacts precise","changes":changes}
rec.write_text(json.dumps(d,indent=2)+"\n",encoding="utf8",newline="\n")
print("R023 FIX1",len(changes),"corrected source-only files, previous R018–R022 originals untouched")
