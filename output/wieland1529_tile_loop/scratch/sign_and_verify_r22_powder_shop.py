"""Sign additive R22 owner/GC evidence requests without mutating prior signed packages."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables/integrated-r22-three-powder-faucet-and-shop-release"
FILES = [
    "START_HERE_R22.md",
    "R22_POWDER_FIXTURE_CONFLICT_AND_SIX_UNIT_TRADE_SIGNOFF.md",
    "R22_W1_WALL_ELEVATIONS_NET_CASE_AND_ONE_TO_ONE_MOCKUP.md",
    "R22_ALL_13_ROOM_GATE_AND_RELEASE_BRIDGE.md",
]


def digest(p: Path):
    b = p.read_bytes()
    return {"sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b)}


submission = ROOT / "state/ROUND016_SUBMISSION.json"
assert digest(submission)["sha256"] == "dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a"
fix2 = ROOT / "state/ROUND016_REVIEWER_NEUTRAL_LANGUAGE_FIX2.json"
assert digest(fix2)["sha256"] == "ee9ae680c4abb05c5e0e2b0407a155aa7cdd02de8bbdc3357fbd9a3a7494e38a"
source = json.loads(submission.read_text(encoding="utf-8"))
for room, opts in source["candidate_source"].items():
    for letter, meta in opts.items():
        assert digest(ROOT / meta["path"]) == {"sha256": meta["sha256"], "bytes": meta["bytes"]}, (room, letter)
assert source["critic_dispatch"] == "NOT_DISPATCHED"
assert source["all_critic_scores"] is None and source["R016_weighted_scoring"] is None

room_state = json.loads((ROOT / "state/ROOMS.json").read_text(encoding="utf-8"))
assert len(room_state["rooms"]) == 13
assert {x["id"] for x in room_state["rooms"]} == {
    "PH-PRIMARY", "PH-BATH2", "PH-BATH3", "PH-BATH4", "PH-POWDER", "PH-WC",
    "TX-PRIMARY", "TX-BATH2", "TX-BATH3", "TX-BATH4", "TX-POWDER", "TX-POWDER2", "TX-WC",
}
for file in FILES:
    assert (OUT / file).is_file(), file

manifest = {
    "version": "R22",
    "date": "2026-11-06",
    "kind": "ADDENDUM ONLY: six powder-unit actual fixture source conflict, provisional wall shop mathematics, and complete 13-room release hold bridge",
    "scope_room_ids": ["PH-POWDER", "TX-POWDER", "TX-POWDER2"],
    "physical_unit_instance_count": 6,
    "global_rooms_preserved": 13,
    "historical_original_source_rows": 27,
    "historical_unpriced_primary_niche_rows_excluded": 2,
    "historical_trade_actions_preserved": 65,
    "drawing_provisional_wall_studies_preserved": 25,
    "R21_original_field_witness_request_rows_preserved": 156,
    "historical_four_unit_material_only_usd": "23572.44",
    "historical_three_powders_two_copies_subset_usd": "2159.30",
    "historical_source_gross_includes_15pct_once": True,
    "source_references": {
        "R014_source_sha256": "946b3eda0a097961e28e76823607fd7d52b82209156e5bb59cdeb9c36450c8ed",
        "R015_source_sha256": "cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8",
        "R016_source_sha256": digest(submission)["sha256"],
        "R016_FIX2_sha256": digest(fix2)["sha256"],
        "R021_manifest_sha256": "a212a902fcf61433cbcf165c05b07681abffcb3f70ae9f8deeb8e0756989ad66",
    },
    "independent_R016_FIX2_reviewer_verdict": "CONTINUE_SOURCE_ONLY",
    "original_design_worker9_state": "FAILED",
    "R014_authentic_critic_count": 6,
    "R014_required_critic_count": 8,
    "R015_dispatch": "HOLD",
    "R016_dispatch": "NOT_DISPATCHED",
    "R014_scoring": None,
    "R015_scoring": None,
    "R016_scoring": None,
    "TX_POWDER_faucet_trim_choice_and_rough": None,
    "TX_POWDER2_basin": None,
    "verified_native_1529_geometry": False,
    "actual_site_inspections": False,
    "actual_samples_or_renders": False,
    "verified_current_chicago_cases_or_installed_bid": False,
    "owner_approval": False,
    "architect_release": False,
    "GC_release": False,
    "procurement_release": False,
    "global_13_room_DONE": False,
    "outputs": {file: digest(OUT / file) for file in FILES},
}
path = OUT / "MANIFEST.json"
if path.exists():
    assert json.loads(path.read_text(encoding="utf-8")) == manifest, "Signed manifest differs; preserve old, investigate"
else:
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
assert json.loads(path.read_text(encoding="utf-8")) == manifest
for file, signature in manifest["outputs"].items():
    assert digest(OUT / file) == signature
print("PASS additive R22 signed 4 technical docs; 6 unit-instance trade holds, 13-room bridge, source R016 exact SHA and 6 frozen candidates preserved")
print("R22_MANIFEST_SHA", digest(path)["sha256"])
