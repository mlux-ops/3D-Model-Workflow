"""Phase 12, step 12.4: writes review/phase12/state.json ({material: state}) from the table of overrides.

    python -P -B write_state.py <applied_slots.csv> <recipes.json> <state.json> <time read>
"""
import collections
import csv
import json
import sys


def main(table, recipes_json, out_json, when):
    with open(table, encoding="utf-8", newline="") as handle:
        counts = collections.Counter(row["revit_material"] for row in csv.DictReader(handle))
    with open(recipes_json, encoding="utf-8") as handle:
        data = json.load(handle)
    state = {}
    for kind, items in (("rebuilt material", data["rebuild"]), ("Phase 5 candidate", data["candidates"])):
        for item in items:
            name = item["revit"].rsplit("/", 1)[-1]
            shown = counts.get(name, 0)
            if shown:
                state[item["material"]] = ("%s active by override on %d surfaces, levels saved; in the Variant Manager list, "
                                           "switch to the Revit material and back tested %s" % (kind, shown, when))
            else:
                state[item["material"]] = "%s made; no placed surface of the building shows this material (%s)" % (kind, when)
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=1, sort_keys=True)
    print("%d materials: %d on surfaces, %d on none; %d surfaces" % (
        len(state), sum(1 for v in state.values() if "active by" in v), sum(1 for v in state.values() if "no placed" in v),
        sum(counts.values())))


if __name__ == "__main__":
    main(*sys.argv[1:5])
