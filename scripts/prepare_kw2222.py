from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'output/kw2222'; out.mkdir(exist_ok=True)
refs=root/'references/kw2222'; refs.mkdir(exist_ok=True)
for p in [Path('C:/Users/found/AppData/Local/Temp/codex-clipboard-90dba391-2172-4c3a-b9d3-26856b9d0168.png'),*[Path('C:/Users/found/Downloads')/n for n in ['1242270.jpg','vcsign-KW2222ABWG-add2.jpg','vcsign-KW2222ABWG-add1.jpg']]]:
    shutil.copy2(p,refs/p.name)
s=(root/'scripts/build_edge.py').read_text()
s=s.replace('edge_txw2a','kw2222').replace('Edge_TXW2A_18_Chrome_R2025','KW2222_ABWG_28_R2025').replace('Edge','KW2222').replace('18 nominal - 19.1 inch metal - Chrome','28 inch - Antique Brass and White Glass')
s=s.replace("('Overall Width',19.1),('Overall Height',4.62),('Projection',2.49)","('Overall Width',4.25),('Overall Height',28),('Projection',2.75)")
s=s.replace("box.Min=xyz(-12,-3,.001); box.Max=xyz(12,3,4.8)","box.Min=xyz(-3,-15,.001); box.Max=xyz(3,15,3)")
s=s.replace("'KW2222 - Polished Chrome',chrome_source,(190,195,200)","'KW2222 - Antique Brass',source,(157,119,57)")
s=s.replace("steel,_=clone_material", "steel,brassapp=clone_material")
s=s.replace("steel.MaterialClass='Metal'; steel.Shininess=128; steel.Smoothness=100", """steel.MaterialClass='Metal'; steel.Shininess=45; steel.Smoothness=70
    scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(brassapp.Id)
    set_color(a,'generic_diffuse',(157,119,57))
    scalar(a,'generic_glossiness',.55); scalar(a,'generic_transparency',0.)
    scalar(a,'generic_reflectivity_at_0deg',.35); scalar(a,'generic_reflectivity_at_90deg',.6)
    scalar(a,'generic_self_illum_luminance',0.)
    scope.Commit(True); scope.Dispose()""")
a=s.index("    fm.Set(note,"); b=s.index('    cats={}',a)
s=s[:a]+'''    fm.Set(note,'28 inch height, 2 inch glass diameter, 2.75 inch projection and 4.25 inch square mounting plate from drawing. Sleeve length, thickness, perforations and hardware inferred from photos. Fixed visualization geometry; no photometric source.')
'''+s[b:]
a=s.index('    # X horizontal'); b=s.index('    doc.Regenerate()',a)
s=s[:a]+'''    # X horizontal, Y vertical, Z away from wall. Origin at mounting center.
    form(doc,'Rounded square backplate',DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,rounded_rect(-2.125,-2.125,2.125,2.125,.06),.16,metal,cats['Mount'])
    box('Central standoff',-.60,-.65,.16,.60,.65,.78,metal,cats['Mount'])
    for x in [-1.67,1.67]:
        cylinder(doc,'Mount screw',xyz(x,0,.16),DB.XYZ.BasisZ,.115,0,.075,metal,cats['Mount'])
    # Hollow glass tube; actual open ends as seen in the supplied photo.
    revolved(doc,'White glass tube',xyz(0,0,1.75),DB.XYZ.BasisY,
             [(.91,-14),(1,-14),(1,14),(.91,14)],glow,cats['Diffusers'])
    # Rear half-cylinder brass sleeve, with true radial perforations.
    origin=xyz(0,-9.3,1.75)
    loop=profile_loop(origin,DB.XYZ.BasisX,DB.XYZ.BasisZ,
        [(-1.065,0),('arc',(0,-1.065),(1.065,0)),(1.015,0),('arc',(0,-1.015),(-1.015,0))])
    sleeve=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]),DB.XYZ.BasisY,18.6/12.)
    holes=0
    for row in range(49):
        y=-9.0+row*.375
        for col in range(9):
            theta=math.radians(12+col*19.5+(3 if row%2 else 0))
            radial=DB.XYZ(math.cos(theta),0,-math.sin(theta))
            center=xyz(0,y,1.75).Add(radial.Multiply(.95/12.))
            circle=DB.CurveLoop()
            u=DB.XYZ.BasisY; v=radial.CrossProduct(u)
            circle.Append(DB.Arc.Create(center,.0625/12.,0,math.pi,u,v))
            circle.Append(DB.Arc.Create(center,.0625/12.,math.pi,2*math.pi,u,v))
            cutter=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([circle]),radial,.2/12.)
            sleeve=DB.BooleanOperationsUtils.ExecuteBooleanOperation(sleeve,cutter,DB.BooleanOperationsType.Difference)
            holes+=1
    e=DB.FreeFormElement.Create(doc,sleeve); e.Subcategory=cats['Housing']
    fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),metal)
    report['real_perforations']=holes
'''+s[b:]
s=s.replace("assert report['diffuser_count']==2","assert report['diffuser_count']==1").replace('[19.1,4.62,2.49]','[4.25,28,2.75]')
s=s.replace('KW2222 TXW2A - 18 nominal metal channel','KW2222 ABWG reference reconstruction').replace('chrome linear housing and white front diffuser','antique brass perforated rear sleeve and hollow white glass tube')
(root/'scripts/build_kw2222.py').write_text(s)

