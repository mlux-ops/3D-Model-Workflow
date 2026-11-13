import unreal, json
names = [n for n in dir(unreal) if n.startswith("GeometryScript_")]
out = {"libs": names}
for lib in names:
    obj = getattr(unreal, lib)
    fns = [n for n in dir(obj) if not n.startswith("_") and n not in dir(unreal.Object)]
    hit = [n for n in fns if any(k in n for k in ("slice", "plane", "boolean", "select", "delete", "copy_mesh", "box", "triangle_count"))]
    if hit:
        out[lib] = hit
json.dumps(out)
