"""Read-only authoritative R018-R022 and R021 source inspection.
Never mutate source, source receipts, roles, room state or owner feedback.
"""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
room_state = json.loads((ROOT / "state/ROOMS.json").read_text(encoding="utf-8"))
rooms = room_state["rooms"]
print("ROOMS", len(rooms), "COPIES", sum(r["unit_count"] for r in rooms))
print("STATUS", dict(collections.Counter(r["status"] for r in rooms)))
print("ROWS", sum(len(r["carried_tile_rows"]) for r in rooms))
print("FOUR_UNIT_ORIGINAL", round(sum(r["unit_count"] * (r.get("carried_quote_material_subtotal_usd_per_unit") or 0) for r in rooms), 2))
print("OWNER_MODEL_IDENTITY", room_state["revit_project_check"]["status"])
print("TRADE_QUOTE_EXPORT_PRESENT", (ROOT / "inputs/TRADE_QUOTES.md").exists())
print("ROOM_STATUS_DETAIL", [(r["id"], r["status"], r["champion_id"], r["champion_score"]) for r in rooms])

names = [
    "state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json",
    "state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json",
    "state/ROUND020_PRIMARY_TILE_SOURCE_PREPARED_NOT_SUBMITTED.json",
    "state/ROUND020_13_PROVISIONAL_OWNER_PREVIEW_MANIFEST.json",
    "state/ROUND021_POWDER_TILE_PRELIMINARY_SOURCE_NOT_SUBMITTED.json",
    "state/ROUND021_ALLOWED_VENDOR_POLICY_AND_EXTRA_CHALLENGERS_PRELIMINARY.json",
    "state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json",
    "state/ROUND022_13_OWNER_UPDATED_NOT_APPROVED_SHA_MANIFEST.json",
]
for rel in names:
    receipt = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    manifest = next(
        (receipt[key] for key in ("files", "draft_files", "source_files", "new_file_hashes") if isinstance(receipt.get(key), dict)),
        None,
    )
    assert manifest, rel + " missing manifest"
    passed = 0
    for path, expected in manifest.items():
        payload = (ROOT / path).read_bytes()
        assert len(payload) == expected["bytes"], path + " length drift"
        assert hashlib.sha256(payload).hexdigest() == expected["sha256"], path + " SHA drift"
        passed += 1
    print("SIGNED_RECEIPT", rel, passed, "/", len(manifest), "PASS")
    for key in ("immutable_parents", "parent_receipts", "prior_receipt_snapshot", "immutable_parent_receipts"):
        for path, expected in receipt.get(key, {}).items():
            payload = (ROOT / path).read_bytes()
            assert hashlib.sha256(payload).hexdigest() == expected["sha256"], path + " PARENT SHA drift"
            assert len(payload) == expected["bytes"], path + " PARENT bytes drift"

for roundnum in ("018", "019", "020", "021", "022"):
    crit = list(ROOT.glob(f"rooms/*/board/round-{roundnum}/critic-*.md"))
    print("CURRENT_CRITIC_FILES", roundnum, len(crit))
for room in ("PH-POWDER", "TX-POWDER", "TX-POWDER2"):
    candidates = sorted((ROOT / "rooms" / room / "board/round-021/candidates").glob("*.md"))
    print("POWDER_CANDIDATES", room, [p.name for p in candidates])

assert len(rooms) == 13 and sum(r["unit_count"] for r in rooms) == 26
assert sum(len(r["carried_tile_rows"]) for r in rooms) == 27
assert abs(sum(r["unit_count"] * (r.get("carried_quote_material_subtotal_usd_per_unit") or 0) for r in rooms) - 23572.44) < 0.01
print("GOVERNANCE_READONLY_PASS")
