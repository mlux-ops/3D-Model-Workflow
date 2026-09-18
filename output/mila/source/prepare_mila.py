from pathlib import Path
root = Path(__file__).resolve().parents[1]
s = (root/'scripts/build_focus.py').read_text()
s = s.replace("'focus'", "'mila'").replace('DCW_Focus_X3_Black_Adjustable_R2025','Matthew_McCormick_Mila_Dark_Adjustable_R2025').replace('Focus X3','Mila').replace('Focus_X3_Mobile','Mila_Body').replace('Disc Finish','Glass Finish')
s = s.replace("('Metal Finish',(25,26,28),.35,.08),('Glass Finish',(242,235,221),.8,.18)", "('Metal Finish',(53,50,44),.42,.22),('Glass Finish',(247,244,230),.65,.08)")
s = s.replace(".50 if name=='Glass Finish'", ".08 if name=='Glass Finish'").replace("50 if name=='Glass Finish'", "8 if name=='Glass Finish'")
s = s.replace("mat.MaterialClass='Metal' if name=='Metal Finish' else 'Plastic'", "mat.MaterialClass='Metal' if name=='Metal Finish' else 'Glass'")
a = s.index('    # Drawing elevation')
b = s.index('    tx.Commit();tx=None', a)
s = s[:a]+'''    # Inches from supplied PDF. Loop thickness .5; globe diameter 6.7 inferred from photo.
    unit=1/25.4
    outer=profile_loop(xyz(0,-.25,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,
        [(4.1,4.1),(4.1,25.),('arc',(0,29.1),(-4.1,25.)),(-4.1,4.1),('arc',(0,0),(4.1,4.1))])
    inner=profile_loop(xyz(0,-.25,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,
        [(3.6,4.1),(3.6,25.),('arc',(0,28.6),(-3.6,25.)),(-3.6,4.1),('arc',(0,.5),(3.6,4.1))])
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([outer,inner]),DB.XYZ.BasisY,.5/12.)
    e=DB.FreeFormElement.Create(child,solid);e.Subcategory=cat
    fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),m)
    revolved(child,'Opal globe',xyz(0,0,25.20),DB.XYZ.BasisZ,
        [(0,-3.35),('arc',(3.35,0),(0,3.35))],g,disc)
    cylinder(child,'Upper cable socket',DB.XYZ.Zero,DB.XYZ.BasisZ,.23,-.35,.1,m,cat)
    cylinder(child,'Globe seat',DB.XYZ.Zero,DB.XYZ.BasisZ,.35,28.5,28.65,m,cat)
    child.Regenerate()
    report['body_bounds_inches']=bounds(list(DB.FilteredElementCollector(child).OfClass(DB.FreeFormElement)))
''' + s[b:]
s=s.replace('1063/25.4','30.55').replace('1063 mm','30.55 in').replace('26 mm','1.45 in').replace('60-1037*unit','60-29.1').replace('115*unit,0,26*unit','3.55,0,1.1').replace('26/304.8','1.1/12.')
s=s.replace("xyz(-25,-25,.001)","xyz(-6,-6,.001)").replace("xyz(25,25,65)","xyz(6,6,61)")
s=s.replace("checkpoint('complete')", "assert report['reopened'] and report['loaded_and_face_placed']\n    assert all(t['pass'] for t in report['flex_tests'])\n    assert all(report['material_tests'].values())\n    checkpoint('complete')")
(root/'scripts/build_mila.py').write_text(s)
