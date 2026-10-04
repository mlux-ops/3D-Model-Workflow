import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.dirname(HERE)
TARGETS = os.path.join(REVIEW, "review_targets.json")
BATCH_DIR = os.path.join(REVIEW, "batches")
SPECIAL = "R35000-WS"
BATCH_SIZE = 14

with open(TARGETS, "r", encoding="utf-8") as f:
    targets = json.load(f)

os.makedirs(BATCH_DIR, exist_ok=True)
normal = [t for t in targets if t.get("group_key") != SPECIAL]
special = [t for t in targets if t.get("group_key") == SPECIAL]

manifest = {"batches": [], "special": []}
for i in range(0, len(normal), BATCH_SIZE):
    batch = normal[i:i+BATCH_SIZE]
    name = "targets_%02d.json" % (i // BATCH_SIZE + 1)
    path = os.path.join(BATCH_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2)
    manifest["batches"].append({
        "name": name,
        "count": len(batch),
        "sections": sorted(set(t["section"] for t in batch)),
        "groups": [t.get("group_key") for t in batch],
    })

for t in special:
    path = os.path.join(BATCH_DIR, "special_R35000-WS.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([t], f, indent=2)
    manifest["special"].append({
        "name": os.path.basename(path),
        "count": 1,
        "group": SPECIAL,
    })

with open(os.path.join(BATCH_DIR, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(json.dumps({
    "normal_targets": len(normal),
    "special_targets": len(special),
    "batch_count": len(manifest["batches"]),
    "batch_size": BATCH_SIZE,
}, indent=2))

