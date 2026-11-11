"""Verify and fingerprint separate R11 owner work without touching R10."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
out = root / "deliverables/integrated-r11"
files = sorted(out.glob("*.md"))
assert files and len(files) == 1
r10 = json.loads((root / "deliverables/integrated-r10/MANIFEST.json").read_text(encoding="utf-8"))
for rid in ("PH-BATH3", "TX-BATH3"):
    source = json.loads((root / "rooms" / rid / "geometry.json").read_text(encoding="utf-8"))
    assert source["model_identity_verified"] is False
score = json.loads((root / "state/ROUND011_SUBMISSION.json").read_text(encoding="utf-8"))
assert score["all_critic_scores"] is None
assert score["phase"] == "2-board"
for f in files:
    body = f.read_text(encoding="utf-8")
    for required in ("DT062412", "BT062415-BNX", "$930.42", "$958.88", "15%", "null", "N/A", "false / false", "9.69", "4.85"):
        assert required in body, (f.name, required)
manifest = {
    "as_of": "2026-11-06",
    "round": 11,
    "scope": "separate owner/GC decision and measurement package; no scored board decision",
    "owner_approval": False,
    "procurement_release": False,
    "all_critic_scores": None,
    "r10_manifest_retained": True,
    "candidate_sources": score["candidate_files"],
    "outputs": {
        f.name: {
            "bytes": len(f.read_bytes()),
            "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
        } for f in files
    },
}
dest = out / "MANIFEST.json"
dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
assert r10 == json.loads((root / "deliverables/integrated-r10/MANIFEST.json").read_text(encoding="utf-8"))
print(f"PASS R11 owner package signed {len(files)} new deliverable; 4 frozen candidate SHA referenced, no R010 modification or owner release")
