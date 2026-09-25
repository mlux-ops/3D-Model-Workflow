from pathlib import Path
p = Path(r"output\lightology_20260923\f10_1242580\build_covet.py")
s = p.read_text(encoding="utf-8-sig")
marker = "app = __revit__.Application\n"
insert = """def inspect_saved_alabaster_texture(app, rfa_path):
    doc = app.OpenDocumentFile(rfa_path)
    try:
        target = None
        for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
            try:
                name = DB.Element.Name.GetValue(mat)
            except Exception:
                name = ''
            if name.endswith(' Natural Alabaster'):
                target = mat
                break
        if target is None:
            return {'material_found':False,'texture_path':None,'texture_exists':False}
        appearance = doc.GetElement(target.AppearanceAssetId)
        asset = appearance.GetRenderingAsset()
        diffuse = asset.FindByName('generic_diffuse')
        texture_path = None
        if diffuse is not None and diffuse.NumberOfConnectedProperties:
            bitmap = diffuse.GetSingleConnectedAsset()
            if bitmap is not None:
                prop = bitmap.FindByName('unifiedbitmap_Bitmap')
                if prop is not None:
                    texture_path = str(prop.Value)
        return {'material_found':True,'material_name':DB.Element.Name.GetValue(target),
                'texture_path':texture_path,'texture_exists':bool(texture_path and os.path.isfile(texture_path))}
    finally:
        doc.Close(False)

"""
if insert not in s:
    s = s.replace(marker, insert + marker)
old = """    report = f.finish()
    if not report.get('technical_pass'):
        raise RuntimeError('Native support returned technical_pass false')"""
new = """    report = f.finish()
    if not report.get('technical_pass'):
        raise RuntimeError('Native support returned technical_pass false')
    report['saved_alabaster_texture_readback'] = inspect_saved_alabaster_texture(app, report['rfa_path'])
    if not report['saved_alabaster_texture_readback'].get('texture_exists'):
        report['technical_pass'] = False
        with open(os.path.join(OUT, BASENAME+'_validation.json'),'w') as stream:
            json.dump(report,stream,indent=2,default=str)
        raise RuntimeError('Saved alabaster diffuse texture did not resolve on RFA reopen')
    with open(os.path.join(OUT, BASENAME+'_validation.json'),'w') as stream:
        json.dump(report,stream,indent=2,default=str)"""
if old not in s:
    raise SystemExit("finish block not found")
s = s.replace(old,new)
p.write_text(s, encoding="utf-8")
