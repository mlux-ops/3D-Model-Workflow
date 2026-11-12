"""Phase 8, step 8.4: the building's light fixtures at their real output.

Runs inside the Unreal editor's Python. The lights came with the Revit model; since Phase 6 they sit in
the four unit levels, which are this project's own copies (not assets that Datasmith created). What each
light is set to is kept in two tables in the repository and applied from there, so the model can be
imported again and the lights set again by Revit element id:

    review/phase8/fixture_table.csv    one row per fixture kind (Revit family and type): maker, lumens,
                                       colour temperature, photometric file, and the source of each number
    review/phase8/fixture_lights.csv   one row per light: which kind, which Revit element, and what was set

Words: a fixture is one Revit lighting-fixture element; a light is one light source inside it (some
fixtures carry two or three); a photometric file (IES) describes in which directions a fixture sends
its light, in candela.
"""
import csv
import os

import unreal

TOOLS = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.join(os.path.dirname(TOOLS), "review", "phase8").replace(os.sep, "/")
TABLE = REVIEW + "/fixture_table.csv"
LIGHTS = REVIEW + "/fixture_lights.csv"
PROFILE_FOLDER = "/Game/Wieland1529/Lighting/Photometric"
UNIT_LEVEL_MARK = "/Game/Wieland1529/Interiors/"


def _actors():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()


def _level_of(actor):
    return actor.get_outer().get_outermost().get_name()


def _revit_id(actor):
    for tag in actor.tags:
        text = str(tag)
        if text.startswith("Revit.Element.Id."):
            return text[len("Revit.Element.Id."):]
    return None


def _metadata(actor):
    data = unreal.DatasmithContentLibrary.get_datasmith_user_data(actor)
    if data is None:
        return {}
    values = data.get_editor_property("metadata") or {}
    return {str(key): str(value) for key, value in values.items()}


def _enum(value):
    return str(value).split(".")[-1].rstrip(">").split(":")[0]


def light_rows():
    """Every light of the building that is loaded now, with its fixture and its present settings."""
    rows = []
    for actor in _actors():
        components = actor.get_components_by_class(unreal.LocalLightComponent)
        if not components:
            continue
        parent = actor.get_attach_parent_actor()
        fixture = parent if parent is not None and parent.get_class().get_name() != "DatasmithSceneActor" else actor
        meta = _metadata(fixture)
        for component in components:
            ies = component.get_editor_property("ies_texture")
            location = component.get_world_location()
            forward = component.get_forward_vector()
            up = component.get_up_vector()
            rows.append({
                "level": _level_of(actor), "light_actor": actor.get_name(), "light_label": actor.get_actor_label(),
                "light_class": component.get_class().get_name(),
                "fixture_label": fixture.get_actor_label(),
                "fixture_revit_element_id": _revit_id(fixture) or _revit_id(actor) or "",
                "fixture_family": meta.get("Element*Family", ""), "fixture_type": meta.get("Element*Type", ""),
                "intensity": round(component.intensity, 3), "intensity_units": _enum(component.get_editor_property("intensity_units")),
                "use_temperature": bool(component.get_editor_property("use_temperature")),
                "temperature_k": round(component.get_editor_property("temperature"), 0),
                "photometric_asset": ies.get_path_name().split(".")[0] if ies else "",
                "use_file_brightness": bool(component.get_editor_property("use_ies_brightness")),
                "file_brightness_scale": round(component.get_editor_property("ies_brightness_scale"), 4),
                "attenuation_radius_cm": round(component.get_editor_property("attenuation_radius"), 1),
                "source_radius_cm": round(component.get_editor_property("source_radius"), 2) if hasattr(component, "source_radius") else "",
                "mobility": _enum(component.get_editor_property("mobility")),
                "visible": bool(component.get_editor_property("visible")),
                "cast_shadows": bool(component.get_editor_property("cast_shadows")),
                "x_cm": round(location.x, 1), "y_cm": round(location.y, 1), "z_cm": round(location.z, 1),
                "forward": "%.3f %.3f %.3f" % (forward.x, forward.y, forward.z),
                "up": "%.3f %.3f %.3f" % (up.x, up.y, up.z),
            })
    return rows


def read_table(path=TABLE):
    """The fixture table as a dictionary keyed by (family, type)."""
    with open(path, "r", newline="", encoding="utf-8") as handle:
        return {(row["family"], row["type"]): row for row in csv.DictReader(handle)}


def import_profile(ies_path, name):
    """Bring one photometric file into the project as a new asset of its own and save that asset by name."""
    path = PROFILE_FOLDER + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        return path
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", ies_path)
    task.set_editor_property("destination_path", PROFILE_FOLDER)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", False)
    task.set_editor_property("save", False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError("photometric file was not imported: " + ies_path)
    unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
    return path


def _number(text, default=None):
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _groups():
    """Loaded lights grouped by fixture: {(level, fixture actor name): [(actor, component, fixture, meta)]}."""
    groups = {}
    for actor in _actors():
        if UNIT_LEVEL_MARK not in _level_of(actor):
            continue
        components = actor.get_components_by_class(unreal.LocalLightComponent)
        if not components:
            continue
        parent = actor.get_attach_parent_actor()
        fixture = parent if parent is not None and parent.get_class().get_name() != "DatasmithSceneActor" else actor
        meta = _metadata(fixture)
        for component in components:
            groups.setdefault((_level_of(actor), fixture.get_name()), []).append((actor, component, fixture, meta))
    return groups


def apply(model_csv, only_revit_ids=None, dry_run=False):
    """Set every loaded light of the building from the fixture table.

    model_csv is the table of the lights as the Revit model delivered them (fixture_lights_before.csv);
    the value each light had there decides which light of a fixture is its main one, so the result is the
    same however often this runs. only_revit_ids limits the run to some fixtures (try one first).
    Returns counts and the list of fixtures whose kind is not in the table.
    """
    table = read_table()
    with open(model_csv, "r", newline="", encoding="utf-8") as handle:
        model = {(row["level"], row["light_actor"]): _number(row["intensity"], 0.0) for row in csv.DictReader(handle)}
    profiles = {}
    done = {"lights_on": 0, "lights_off": 0, "aimed_down": 0, "fixtures": 0, "unknown_kinds": [], "missing_in_model_table": 0,
            "levels": set()}
    for (level, _name), members in sorted(_groups().items()):
        fixture, meta = members[0][2], members[0][3]
        revit_id = _revit_id(fixture) or ""
        if only_revit_ids is not None and revit_id not in only_revit_ids:
            continue
        kind = table.get((meta.get("Element*Family", ""), meta.get("Element*Type", "")))
        if kind is None:
            done["unknown_kinds"].append("%s | %s | %s" % (meta.get("Element*Family", ""), meta.get("Element*Type", ""), revit_id))
            continue
        done["fixtures"] += 1
        done["levels"].add(level)
        values = []
        for actor, component, _fixture, _meta in members:
            key = (level, actor.get_name())
            if key not in model:
                done["missing_in_model_table"] += 1
            values.append(model.get(key, component.intensity))
        largest = max(range(len(members)), key=lambda i: (values[i], members[i][0].get_name()))
        for index, (actor, component, _fixture, _meta) in enumerate(members):
            rule = kind["lights_on"]
            on = rule == "all" or (rule == "largest" and index == largest)
            if dry_run:
                done["lights_on" if on else "lights_off"] += 1
                continue
            actor.modify()
            component.modify()
            component.set_mobility(unreal.ComponentMobility.MOVABLE)
            component.set_editor_property("visible", on)
            actor.set_actor_hidden_in_game(not on)
            if not on:
                done["lights_off"] += 1
                continue
            file_asset = None
            if kind["profile_asset"]:
                if kind["profile_asset"] not in profiles:
                    profiles[kind["profile_asset"]] = unreal.load_asset(kind["profile_asset"])
                file_asset = profiles[kind["profile_asset"]]
                if file_asset is None:
                    raise RuntimeError("photometric asset is missing: " + kind["profile_asset"])
            component.set_editor_property("ies_texture", file_asset)
            component.set_editor_property("use_ies_brightness", False)
            component.set_editor_property("ies_brightness_scale", 1.0)
            units = unreal.LightUnits.CANDELAS if kind["set_units"] == "candela" else unreal.LightUnits.LUMENS
            component.set_editor_property("intensity_units", units)
            share = 1.0
            if rule == "all" and kind["value_is"] == "per fixture, shared by the model's values":
                total = sum(values)
                share = values[index] / total if total > 0 else 1.0 / len(members)
            component.set_editor_property("intensity", _number(kind["set_value"], 0.0) * share)
            component.set_editor_property("use_temperature", True)
            component.set_editor_property("temperature", _number(kind["kelvin"], 3000.0))
            component.set_editor_property("attenuation_radius", _number(kind["reach_cm"], 1000.0))
            component.set_editor_property("source_radius", _number(kind["source_radius_cm"], 0.0))
            component.set_editor_property("cast_shadows", True)
            if kind["aim"] == "down":
                actor.set_actor_rotation(unreal.Rotator(pitch=-90.0, yaw=0.0, roll=0.0), False)
                done["aimed_down"] += 1
            done["lights_on"] += 1
    done["levels"] = sorted(done["levels"])
    return done


def inventory(out_csv):
    """Write the present state of every loaded light to a table. Changes nothing."""
    rows = light_rows()
    if not rows:
        return {"error": "no lights are loaded"}
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    by_level = {}
    for row in rows:
        by_level[row["level"]] = by_level.get(row["level"], 0) + 1
    return {"lights": len(rows), "fixtures": len(set(r["fixture_revit_element_id"] for r in rows)),
            "kinds": len(set((r["fixture_family"], r["fixture_type"]) for r in rows)), "by_level": by_level,
            "visible": sum(1 for r in rows if r["visible"]), "movable": sum(1 for r in rows if r["mobility"] == "MOVABLE"),
            "without_revit_id": sum(1 for r in rows if not r["fixture_revit_element_id"]),
            "forward_kinds": sorted(set(r["forward"] for r in rows))[:12],
            "radius_kinds": sorted(set(r["attenuation_radius_cm"] for r in rows))[:12],
            "file_brightness": sorted(set((r["use_file_brightness"], r["file_brightness_scale"]) for r in rows))}
