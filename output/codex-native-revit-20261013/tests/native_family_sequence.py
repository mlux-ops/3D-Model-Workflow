"""Disposable native-family acceptance smoke; run only against the isolated test Revit.

No production-document fallback. Existing operation UUIDs are reconciled, never replayed.
Authoring proves a synthetic extrusion with a real height association; this is not
manufacturer cabinet fidelity or width/depth-parametric acceptance.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "controller"))
from native_revit import Client


def payload(receipt):
    value = receipt["result"]
    if isinstance(value, dict) and "transaction_status" in value:
        return value.get("data", value.get("result", value))
    return value


def atomic_write(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


class Sequence:
    def __init__(self, client, destination):
        self.client, self.destination = client, destination
        self.path = destination / "family-native-report.json"
        if self.path.exists():
            self.report = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.report = {"run_id": str(uuid.uuid4()), "status": "incomplete", "native": True,
                           "scope": "synthetic-family lifecycle and height association", "steps": {}, "checks": {}}
            atomic_write(self.path, self.report)

    def call(self, name, operation, doc, arguments=None):
        oid = str(uuid.uuid5(uuid.UUID(self.report["run_id"]), name))
        prior = self.report["steps"].get(name)
        if prior is not None and prior.get("status") == "completed":
            return payload(prior)
        # Client.submit reconciles an existing UUID rather than reposting mutations.
        receipt = self.client.submit(operation, doc, arguments or {}, operation_id_value=oid)
        self.report["steps"][name] = receipt
        atomic_write(self.path, self.report)
        if receipt["status"] in {"queued", "running", "unknown_completion"}:
            receipt = self.client.wait(oid, timeout_seconds=60)
            self.report["steps"][name] = receipt
            atomic_write(self.path, self.report)
        if receipt["status"] != "completed":
            raise RuntimeError(f"{name}: {receipt['status']}; reconcile operation {oid}. Dependent steps stopped.")
        return payload(receipt)

    def check(self, name, actual, expected, tolerance=1e-6):
        ok = math.isclose(actual, expected, abs_tol=tolerance, rel_tol=1e-8)
        self.report["checks"][name] = {"actual": actual, "expected": expected, "tolerance": tolerance, "pass": ok}
        atomic_write(self.path, self.report)
        if not ok:
            raise AssertionError(f"{name}: expected {expected}; actual {actual}")


def form_height(geometry, element_id):
    form = next(f for f in geometry["forms"] if f["element"]["id"] == element_id)
    bounds = form["geometry"]["bounds"]
    return bounds["max"][2] - bounds["min"][2]


def run(options):
    destination = Path(options.output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    client = Client(base_url=options.url, token_file=options.token_file,
                    receipt_dir=destination / "controller-receipts")
    seq = Sequence(client, destination)
    try:
        created = seq.call("create", "family.create", {}, {"template": str(Path(options.family_template).resolve())})
        doc = {"session_id": created["session_id"]}
        inspection = seq.call("inspect-created", "family.inspect", doc)
        seq.report["category"] = inspection["category"]
        seq.report["placement_type"] = inspection["placement_type"]
        seq.call("type", "family.type.create", doc, {"name": "Codex_Disposable_Box"})
        seq.call("height-parameter", "family.parameter.add", doc,
                 {"name": "Codex_Test_Height", "group": "Geometry", "data_type": "Length", "instance": False})
        seq.call("height-value", "family.parameter.set", doc, {"parameter": "Codex_Test_Height", "value": 3.0})
        extrusion = seq.call("extrusion", "family.extrusion.create", doc,
                             {"units": "feet", "plane": {"origin": [0, 0, 0], "normal": [0, 0, 1]},
                              "profile": [[[0, 0, 0], [2, 0, 0], [2, 1.5, 0], [0, 1.5, 0]]],
                              "start": 0, "end": 3, "solid": True})
        eid = extrusion["element"]["id"]
        seq.call("height-association", "family.parameter.associate", doc,
                 {"element": extrusion["element"]["unique_id"], "element_parameter_builtin": "EXTRUSION_END_PARAM", "family_parameter": "Codex_Test_Height"})
        flex = seq.call("flex", "family.type.flex", doc,
                        {"types": [{"name": "Codex_Disposable_Box", "values": {"Codex_Test_Height": 4.0}},
                                   {"name": "Codex_Disposable_Box", "values": {"Codex_Test_Height": 2.0}}]})
        for index, expected in enumerate((4.0, 2.0)):
            snapshot = flex["snapshots"][index]["result"]
            seq.check(f"height-flex-{index}", form_height(snapshot["geometry"], eid), expected)
        restored = seq.call("geometry-restored", "family.geometry.inspect", doc)
        seq.check("height-restored-after-flex", form_height(restored, eid), 3.0)
        save_path = destination / ("Codex_Disposable_Box_" + seq.report["run_id"] + ".rfa")
        seq.call("save-new-path", "family.save", doc, {"path": str(save_path)})
        seq.call("close-saved", "family.close", doc, {"discard_changes": True})
        reopened = seq.call("reopen-saved", "family.open", {}, {"path": str(save_path)})
        reopened_doc = {"session_id": reopened["session_id"]}
        readback = seq.call("inspect-reopened", "family.inspect", reopened_doc)
        type_info = next(t for t in readback["types"] if t["name"] == "Codex_Disposable_Box")
        value = next(v["value"] for v in type_info["values"] if v["parameter"]["name"] == "Codex_Test_Height")
        seq.check("saved-reopened-height-parameter", value, 3.0)
        geometry = seq.call("geometry-reopened", "family.geometry.inspect", reopened_doc)
        seq.check("saved-reopened-height-geometry", form_height(geometry, eid), 3.0)
        project = seq.call("create-project", "document.create", {}, {"template": str(Path(options.project_template).resolve())})
        project_doc = {"session_id": project["session_id"]}
        loaded = seq.call("load-into-project", "family.load", project_doc,
                          {"path": str(save_path), "replacement_policy": "reject"})
        if not loaded["loaded"]:
            raise AssertionError("Saved synthetic family was not loaded into the disposable project.")
        seq.report["loaded_family"] = loaded["family"]
        symbols = seq.call("discover-loaded-symbol", "elements.query", project_doc,
                           {"class": "FamilySymbol", "types": True, "name_contains": "Codex_Disposable_Box", "limit": 500})
        if len(symbols["items"]) != 1:
            raise AssertionError("Expected one uniquely named synthetic family symbol.")
        symbol = symbols["items"][0]
        levels = seq.call("discover-level", "elements.query", project_doc, {"class": "Level", "limit": 500})
        if not levels["items"]:
            raise AssertionError("Disposable template contains no Level.")
        if symbol["placement_type"] != "OneLevelBased":
            seq.report["placement"] = {"status": "not_tested", "reason": "Use an unhosted OneLevelBased family template for this smoke; no hosting guessed."}
        else:
            placed = seq.call("place-native-instance", "family.place", project_doc,
                              {"type": symbol["unique_id"], "level": levels["items"][0]["unique_id"], "point": [5, 7, 0]})
            seq.report["placement"] = {"status": "tested", "readback": placed}
            actual = placed["instances"][0]["location"]["point"]
            seq.check("placed-x", actual[0], 5.0)
            seq.check("placed-y", actual[1], 7.0)
        seq.report["status"] = "passed"
        seq.report["saved_family"] = str(save_path)
        seq.report["limitations"] = ["Width/depth are fixed sketch dimensions; only height is truly parametric in this smoke.",
                                     "No visual, production cabinet, clearance, multi-document atomicity or hosting acceptance.",
                                     "Disposable project/family remain open; no implicit save or close."]
    except Exception as exc:
        seq.report["status"] = "failed_or_unresolved"
        seq.report["error"] = {"type": type(exc).__name__, "message": str(exc)}
        atomic_write(seq.path, seq.report)
        raise
    atomic_write(seq.path, seq.report)
    return seq.path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--token-file", required=True)
    parser.add_argument("--family-template", required=True)
    parser.add_argument("--project-template", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(run(args))
