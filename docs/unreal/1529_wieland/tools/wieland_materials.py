"""Editor-side helpers for Phase 5 (materials) of the 1529 N. Wieland scene.

Runs inside the Unreal editor's Python interpreter. Usage from the agent
server's Python tool:

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_materials as wm

Nothing here edits an asset that Datasmith created. Candidates are new
material instances under /Game/Wieland1529/Materials/, and they reach the
scene only as component overrides that alternatives_on() sets and
alternatives_off() clears (see material_alternatives.csv).
"""

import csv
import json
import os

import unreal

MEL = unreal.MaterialEditingLibrary
DATASMITH_MATERIALS = "/Game/Wieland1529/Building/Datasmith"
MATERIALS = "/Game/Wieland1529/Materials"


def _world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def _texture_info(texture):
    if texture is None:
        return None
    info = {"path": texture.get_path_name(), "class": texture.get_class().get_name()}
    try:
        info["x"] = texture.blueprint_get_size_x()
        info["y"] = texture.blueprint_get_size_y()
    except Exception:
        pass
    for prop in ("srgb", "compression_settings", "virtual_texture_streaming", "lod_group"):
        try:
            info[prop] = str(texture.get_editor_property(prop))
        except Exception:
            pass
    try:
        data = texture.get_editor_property("asset_import_data")
        info["source_file"] = data.get_first_filename() if data else None
    except Exception:
        info["source_file"] = None
    return info


def material_params(material):
    """All parameters of a material instance, with the values in force."""
    out = {"path": material.get_path_name(), "class": material.get_class().get_name()}
    parent = material.get_editor_property("parent") if isinstance(material, unreal.MaterialInstance) else None
    out["parent"] = parent.get_path_name() if parent else None
    base = material.get_base_material()
    out["base"] = base.get_path_name() if base else None
    try:
        out["blend_mode"] = str(material.get_blend_mode())
    except Exception:
        out["blend_mode"] = None
    scalars, vectors, textures, switches = {}, {}, {}, {}
    if isinstance(material, unreal.MaterialInstanceConstant):
        for name in MEL.get_scalar_parameter_names(material):
            scalars[str(name)] = MEL.get_material_instance_scalar_parameter_value(material, name)
        for name in MEL.get_vector_parameter_names(material):
            value = MEL.get_material_instance_vector_parameter_value(material, name)
            vectors[str(name)] = [round(value.r, 5), round(value.g, 5), round(value.b, 5), round(value.a, 5)]
        for name in MEL.get_texture_parameter_names(material):
            textures[str(name)] = _texture_info(MEL.get_material_instance_texture_parameter_value(material, name))
        for name in MEL.get_static_switch_parameter_names(material):
            switches[str(name)] = MEL.get_material_instance_static_switch_parameter_value(material, name)
        out["overridden_scalars"] = [str(p.parameter_info.name) for p in material.get_editor_property("scalar_parameter_values")]
        out["overridden_vectors"] = [str(p.parameter_info.name) for p in material.get_editor_property("vector_parameter_values")]
        out["overridden_textures"] = [str(p.parameter_info.name) for p in material.get_editor_property("texture_parameter_values")]
    out["scalars"], out["vectors"], out["textures"], out["switches"] = scalars, vectors, textures, switches
    return out


def dump_params(audit_csv, out_json):
    """Step 5.0: read every audited material's parameters into a JSON file."""
    rows = list(csv.DictReader(open(audit_csv, encoding="utf-8")))
    result, missing = {}, []
    for row in rows:
        path = row["asset_path"]
        material = unreal.load_asset(path) if path.startswith("/") else None
        if material is None:
            missing.append(row["material"])
            continue
        result[row["material"]] = material_params(material)
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump({"materials": result, "missing": missing}, handle, indent=1)
    parents = {}
    for item in result.values():
        parents[item["parent"]] = parents.get(item["parent"], 0) + 1
    return {"read": len(result), "missing": missing, "parents": parents}
