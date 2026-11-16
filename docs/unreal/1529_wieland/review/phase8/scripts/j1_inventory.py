import unreal, json, collections

w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
out = {"actors": len(actors)}

KINDS = (unreal.DirectionalLight, unreal.SkyLight, unreal.SkyAtmosphere, unreal.ExponentialHeightFog,
         unreal.VolumetricCloud, unreal.PostProcessVolume)
env = []
for a in actors:
    cn = a.get_class().get_name()
    if isinstance(a, KINDS) or "SunSky" in cn or "SkySphere" in cn or "Sky" in cn:
        d = {"label": a.get_actor_label(), "class": cn, "level": a.get_outer().get_outermost().get_name(),
             "hidden": a.is_temporarily_hidden_in_editor(), "tags": [str(t) for t in a.tags]}
        if isinstance(a, unreal.DirectionalLight):
            c = a.light_component
            r = a.get_actor_rotation()
            d.update(intensity=c.intensity, rot=[r.pitch, r.yaw, r.roll], visible=c.is_visible(),
                     temp=c.temperature, use_temp=c.use_temperature)
        if isinstance(a, unreal.SkyLight):
            c = a.light_component
            d.update(intensity=c.intensity, real_time=c.real_time_capture, visible=c.is_visible())
        if isinstance(a, unreal.PostProcessVolume):
            s = a.settings
            d.update(unbound=a.unbound, enabled=a.enabled,
                     ov_method=s.override_auto_exposure_method, method=str(s.auto_exposure_method),
                     ov_bias=s.override_auto_exposure_bias, bias=s.auto_exposure_bias,
                     ov_min=s.override_auto_exposure_min_brightness, mn=s.auto_exposure_min_brightness,
                     mx=s.auto_exposure_max_brightness)
        env.append(d)
out["environment"] = env

lights = collections.Counter()
ies = collections.Counter()
levels = collections.Counter()
n_light_actors = 0
for a in actors:
    comps = a.get_components_by_class(unreal.LocalLightComponent)
    if not comps:
        continue
    n_light_actors += 1
    for c in comps:
        key = (c.get_class().get_name(), str(c.intensity_units), bool(c.is_visible()), bool(c.affects_world),
               str(c.mobility), bool(c.cast_shadows))
        lights[key] += 1
        p = c.ies_texture
        ies[p.get_path_name() if p else "none"] += 1
        levels[a.get_outer().get_outermost().get_name()] += 1
out["light_actors"] = n_light_actors
out["light_components"] = [[list(k), v] for k, v in lights.items()]
out["ies_use"] = dict(ies)
out["light_levels"] = dict(levels)

ar = unreal.AssetRegistryHelpers.get_asset_registry()
prof = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "TextureLightProfile"), True)
out["ies_assets"] = [str(x.package_name) for x in prof]
json.dumps(out)
