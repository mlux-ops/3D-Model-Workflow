"""Compare two Datasmith exports (.udatasmith) of the same Revit view.

Usage:
    python compare_udatasmith.py <first.udatasmith> <second.udatasmith>
        [--assignments <reimport_assignments.json>] [--out <result.json>]

Reads both files and reports, by the element names Datasmith itself uses to
match a reimport against what is already in the project:

    static meshes      removed, added, and those with the same name whose
                       content hash differs (these are the meshes a reimport
                       has to replace)
    placed objects     ActorMesh elements removed, added, and changed
                       (transform, mesh reference, label, layer or tags)
    lights             removed, added, changed
    materials          MaterialInstance elements removed, added, changed
    textures           removed, added, changed

With --assignments, each of the Unreal-side material assignments recorded in
that table is looked up in both files by its Revit element id, to say before
a reimport whether its object and its mesh are still in the second file and
whether the mesh is one of those the reimport replaces.

The files are not strict XML (some texture paths hold a bare "&"), so bare
ampersands are escaped in memory before parsing. Nothing is written except
the --out file.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET

BARE_AMPERSAND = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)")


def load(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    return ET.fromstring(BARE_AMPERSAND.sub("&amp;", text))


def own_content(element):
    """The element's attributes and direct children, leaving out nested actors."""
    parts = [json.dumps(sorted(element.attrib.items()))]
    for child in element:
        if child.tag == "children":
            continue
        parts.append(ET.tostring(child, encoding="unicode").strip())
    return "\n".join(parts)


def revit_id(element):
    for tag in element.findall("tag"):
        value = tag.get("value", "")
        if value.startswith("Revit.Element.Id."):
            return value
    return None


def index(root, tag):
    found = {}
    duplicates = 0
    for element in root.iter(tag):
        name = element.get("name")
        if name in found:
            duplicates += 1
        found[name] = element
    return found, duplicates


def describe(element):
    record = {"name": element.get("name"), "label": element.get("label")}
    rid = revit_id(element)
    if rid:
        record["revit_element_id"] = rid
    mesh = element.find("mesh")
    if mesh is not None:
        record["mesh"] = mesh.get("name")
    return record


def what_changed(a, b):
    changes = []
    if a.get("label") != b.get("label"):
        changes.append("label")
    if a.get("layer") != b.get("layer"):
        changes.append("layer")
    for child_tag, word in (("Transform", "transform"), ("mesh", "mesh reference")):
        ca, cb = a.find(child_tag), b.find(child_tag)
        sa = ET.tostring(ca, encoding="unicode").strip() if ca is not None else None
        sb = ET.tostring(cb, encoding="unicode").strip() if cb is not None else None
        if sa != sb:
            changes.append(word)
    if not changes:
        changes.append("other content")
    return changes


def compare_kind(root_a, root_b, tag, mesh_hash=False):
    a, dup_a = index(root_a, tag)
    b, dup_b = index(root_b, tag)
    removed = [describe(a[n]) for n in a if n not in b]
    added = [describe(b[n]) for n in b if n not in a]
    changed = []
    for name in a:
        if name not in b:
            continue
        if mesh_hash:
            ha = a[name].find("Hash")
            hb = b[name].find("Hash")
            ha = ha.get("value") if ha is not None else None
            hb = hb.get("value") if hb is not None else None
            if ha != hb:
                record = describe(a[name])
                record["hash_first"] = ha
                record["hash_second"] = hb
                changed.append(record)
        elif own_content(a[name]) != own_content(b[name]):
            record = describe(a[name])
            record["changed"] = what_changed(a[name], b[name])
            changed.append(record)
    return {
        "count_first": len(a),
        "count_second": len(b),
        "duplicate_names_first": dup_a,
        "duplicate_names_second": dup_b,
        "removed": removed,
        "added": added,
        "changed": changed,
    }


def check_assignments(path, root_a, root_b, meshes):
    with open(path, encoding="utf-8") as handle:
        table = json.load(handle)
    changed_meshes = {m["name"] for m in meshes["changed"]}
    removed_meshes = {m["name"] for m in meshes["removed"]}

    def by_revit_id(root):
        found = {}
        for element in root.iter("ActorMesh"):
            rid = revit_id(element)
            if rid:
                found.setdefault(rid, []).append(element)
        return found

    ids_a, ids_b = by_revit_id(root_a), by_revit_id(root_b)
    rows = []
    number = 0
    for kind, key, id_key in (("on object", "on_objects", "revit_element_id"), ("on mesh", "on_meshes", "revit_element_id_of_that_object")):
        for entry in table.get(key, []):
            number += 1
            rid = entry.get(id_key)
            in_a = ids_a.get(rid, [])
            in_b = ids_b.get(rid, [])
            mesh_names_a = sorted({e.find("mesh").get("name") for e in in_a if e.find("mesh") is not None})
            mesh_names_b = sorted({e.find("mesh").get("name") for e in in_b if e.find("mesh") is not None})
            rows.append({
                "no": number,
                "kind": kind,
                "category": entry.get("category"),
                "what": entry.get("actor") or entry.get("mesh", "").rsplit(".", 1)[-1],
                "revit_element_id": rid,
                "objects_with_that_id_first": len(in_a),
                "objects_with_that_id_second": len(in_b),
                "object_still_in_second_file": bool(in_b),
                "same_object_names": sorted(e.get("name") for e in in_a) == sorted(e.get("name") for e in in_b),
                "same_mesh_reference": mesh_names_a == mesh_names_b,
                "mesh_content_changed": any(m in changed_meshes for m in mesh_names_a),
                "mesh_removed_from_second_file": any(m in removed_meshes for m in mesh_names_a),
            })
    return rows


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    path_a, path_b = argv[1], argv[2]
    root_a, root_b = load(path_a), load(path_b)
    result = {
        "first": path_a,
        "second": path_b,
        "static_meshes": compare_kind(root_a, root_b, "StaticMesh", mesh_hash=True),
        "placed_objects": compare_kind(root_a, root_b, "ActorMesh"),
        "lights": compare_kind(root_a, root_b, "Light"),
        "materials": compare_kind(root_a, root_b, "MaterialInstance"),
        "textures": compare_kind(root_a, root_b, "Texture"),
    }
    if "--assignments" in argv:
        result["assignments"] = check_assignments(argv[argv.index("--assignments") + 1], root_a, root_b, result["static_meshes"])
    for key in ("static_meshes", "placed_objects", "lights", "materials", "textures"):
        part = result[key]
        print("%-15s first %5d  second %5d  removed %4d  added %4d  changed %4d" % (
            key, part["count_first"], part["count_second"], len(part["removed"]), len(part["added"]), len(part["changed"])))
    for row in result.get("assignments", []):
        print("assignment %2d  %-9s %-20s in second file: %-5s same mesh: %-5s mesh content changed: %-5s  %s" % (
            row["no"], row["kind"], row["category"], row["object_still_in_second_file"], row["same_mesh_reference"],
            row["mesh_content_changed"], row["what"][:60]))
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=1)
        print("written:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
