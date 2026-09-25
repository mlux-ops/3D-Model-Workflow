import json, hashlib
from pathlib import Path
root = Path(r"output\lightology_20260923\f10_1242580")
manifest = root / "sources_and_inferences.json"
data = json.loads(manifest.read_text(encoding="utf-8-sig"))
files = [
    "source/lightology_1242586.jpg",
    "source/visualcomfort_ts_kw4115abalb.pdf",
    "source/visualcomfort_ig_kw4115abalb.pdf",
    "source/visualcomfort_kw4115_reference.rfa",
    "source/covet_alabaster_diffuse.jpg",
    "build_covet.py"
]
data["sha256"] = {}
for rel in files:
    p = root / rel
    data["sha256"][rel] = hashlib.sha256(p.read_bytes()).hexdigest().upper()
manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")
