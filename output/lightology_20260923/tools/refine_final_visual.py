from pathlib import Path
import ast,shutil
root=Path(__file__).resolve().parents[1]
fan=root/'f01_816712'/'build_f01_816712.py'
covet=root/'f10_1242580'/'build_covet.py'
for source in [fan,covet]:
    history=source.parent/'history';history.mkdir(exist_ok=True)
    keep=history/(source.stem+'_before_final_visual.py')
    if not keep.exists():shutil.copy2(source,keep)
s=fan.read_text()
s=s.replace('(2.65, 0.00, 4.00, .50, 11.88, 20.0)','(2.35,-0.20, 4.20, .50, 11.88, 20.0)')
s=s.replace('(12.5,-1.05, 4.45','(12.5,-1.45, 4.45').replace('(17.0,-1.55, 5.20','(17.0,-2.10, 5.20').replace('(21.0,-1.83, 5.70','(21.0,-2.60, 5.70').replace('(24.2,-2.08, 5.35','(24.2,-2.90, 5.35').replace('(25.6,-2.17, 3.80','(25.6,-3.00, 3.80').replace('(26.0,-2.20, 0.80','(26.0,-3.03, 0.80')
old="""    elems.append(revolve(doc,'Slim integrated light bezel',[(0,12.48),(3.40,12.48),
        (3.44,12.65),(3.44,13.18),(3.34,13.26),(0,13.26)],p_metal,body_cat))
    elems.append(revolve(doc,'Shallow opal light disk',[(0,12.18),(3.34,12.18),
        ('arc',(3.4107,12.2093),(3.44,12.28)),(3.44,13.35),
        ('arc',(3.35,13.69),(3.0,13.80)),(0,13.80)],p_glow,diff_cat))"""
new="""    elems.append(revolve(doc,'Recessed black light bezel',[(3.30,12.48),(3.54,12.48),
        (3.54,13.60),(3.46,13.74),(3.30,13.74)],p_metal,body_cat))
    elems.append(revolve(doc,'Recessed opal light disk',[(0,12.18),(3.20,12.18),
        (3.20,13.52),(3.44,13.60),(3.44,13.75),
        ('arc',(3.42536,13.78536),(3.39,13.80)),(0,13.80)],p_glow,diff_cat))"""
if old not in s:raise RuntimeError('Fan bezel changed; inspect before edit')
s=s.replace(old,new).replace("'aft_sweep_at_tip_in': 2.20","'aft_sweep_at_tip_in': 3.03")
ast.parse(s);fan.write_text(s)
s=covet.read_text().replace('emission=350, cct=2700','emission=35, cct=2700')
old='''    scope.Commit(True)
    scope.Dispose()

def inspect_saved_alabaster_texture'''
new='''    glow=asset.FindByName('generic_self_illum_filter_map')
    if glow.NumberOfConnectedProperties:glow.RemoveConnectedAsset()
    glow.AddConnectedAsset('UnifiedBitmap')
    luminous=glow.GetSingleConnectedAsset()
    luminous.FindByName('unifiedbitmap_Bitmap').Value=path
    for key in ['texture_RealWorldScaleX','texture_RealWorldScaleY']:
        prop=luminous.FindByName(key)
        if prop is not None:prop.Value=18.25/12.0
    scope.Commit(True)
    scope.Dispose()

def inspect_saved_alabaster_texture'''
if old not in s:raise RuntimeError('Covet bitmap function boundary changed')
s=s.replace(old,new);ast.parse(s);covet.write_text(s)
p=root/'tools'/'export_native_meshes.py';s=p.read_text()
old="if name=='generic_diffuse' and p.NumberOfConnectedProperties:"
new="if name in ['generic_diffuse','generic_self_illum_filter_map'] and p.NumberOfConnectedProperties:"
if old not in s:raise RuntimeError('Native mesh appearance context changed')
s=s.replace(old,new)
s=s.replace("if bp is not None:data['bitmap']=bp.Value;data['bitmap_exists']=os.path.isfile(bp.Value)","if bp is not None:\n                data['bitmap' if name=='generic_diffuse' else 'emission_bitmap']=bp.Value\n                data['bitmap_exists' if name=='generic_diffuse' else 'emission_bitmap_exists']=os.path.isfile(bp.Value)")
ast.parse(s);p.write_text(s)
p=root/'tools'/'render_native_studio.py';s=p.read_text()
s=s.replace("    return m\n","    if info.get('emission_bitmap') and os.path.isfile(info['emission_bitmap']):\n        glow=nt.nodes.new('ShaderNodeTexImage');glow.image=bpy.data.images.load(info['emission_bitmap'],check_existing=True)\n        nt.links.new(glow.outputs['Color'],shader.inputs['Emission Color'])\n    return m\n",1)
ast.parse(s);p.write_text(s)
p=root/'tools'/'final_native_review.py';s=p.read_text()
s=s.replace("COUNT=dict((k,2 if k in ['f05','f07'] else 1) for k in EXPECTED)","REVIEW_KEYS=globals().get('REVIEW_KEYS')\nREPORT_STEM='native_final_review_patch' if REVIEW_KEYS else 'native_final_review'\nCOUNT=dict((k,2 if k in ['f05','f07'] else 1) for k in EXPECTED if not REVIEW_KEYS or k in REVIEW_KEYS)")
s=s.replace("for source in index:\n","for source in index:\n    if REVIEW_KEYS and source['folder'][:3] not in REVIEW_KEYS:continue\n")
s=s.replace("'generic_self_illum_luminance']:","'generic_self_illum_luminance','generic_self_illum_filter_map']:")
s=s.replace("'native_final_review_progress.json'","REPORT_STEM+'_progress.json'").replace("'native_final_review.json'","REPORT_STEM+'.json'")
ast.parse(s);p.write_text(s)
print('FINAL_VISUAL_REFINEMENTS_PREPARED')