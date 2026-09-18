from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'output'/'700lsesf60'
out.mkdir(parents=True,exist_ok=True)
refs=root/'references'/'700lsesf60'
refs.mkdir(parents=True,exist_ok=True)
for name in ['1130167.jpg','vcmod-700LSESF60-line.png','tech-700LSESF60B-LED927-add1.jpg','tech-700LSESF60B-LED927-add2.jpg']:
    shutil.copy2(Path('C:/Users/found/Downloads')/name,refs/name)
s=(root/'scripts/build_focus.py').read_text()
s=s.replace("'focus'","'700lsesf60'").replace('DCW_Focus_X3_Black_Adjustable_R2025','700LSESF60_Black_Adjustable_R2025').replace('Focus X3','700LSESF60').replace('Focus_X3_Mobile','700LSESF60_Body').replace('Disc Finish','Diffuser Finish')
s=s.replace("('Diffuser Finish',(242,235,221),.8,.18)","('Diffuser Finish',(250,244,224),.45,.06),('Glass Finish',(250,250,250),.96,.04)")
s=s.replace(".50 if name=='Diffuser Finish' else 0.",".92 if name=='Glass Finish' else (.12 if name=='Diffuser Finish' else 0.)")
s=s.replace("50 if name=='Diffuser Finish' else 0","92 if name=='Glass Finish' else (12 if name=='Diffuser Finish' else 0)")
s=s.replace("else 'Plastic'","else 'Glass'")
s=s.replace("scalar(a,'generic_reflectivity_at_90deg',.85)","scalar(a,'generic_reflectivity_at_90deg',.85 if name=='Glass Finish' else .12)\n        scalar(a,'generic_refraction_index',1.52)\n        p=a.FindByName('generic_is_metal')\n        if p is not None: p.Value=False")
s=s.replace("fm.NewType('700LSESF60 Black')","fm.NewType('60 inch - Black')")
s=s.replace("'Mobile Frame'","'Bar and Lamp Housings'").replace("'Luminous Acrylic'","'Glass and Diffusers'")
a=s.index('    # Drawing elevation')
b=s.index('    tx.Commit();tx=None',a)
s=s[:a]+'''    # Printed inches authoritative. Undimensioned cross sections are photo-derived.
    form(child,'60 inch bar',DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,
         rounded_rect(-30,-.40,30,.40,.035),1.4,m,cat)
    glass=params['Glass Finish']
    for i,x in enumerate([-26.,-15.6,-5.2,5.2,15.6,26.]):
        origin=xyz(x,0,0)
        cylinder(child,'Housing '+str(i+1),origin,DB.XYZ.BasisZ,1.25,.75,1.55,m,cat,.035)
        # Hollow clear sleeve with substantial clear bottom; inset frosted inner cylinder.
        revolved(child,'Clear glass '+str(i+1),origin,DB.XYZ.BasisZ,
            [(1.10,1.55),(1.25,1.55),(1.25,4.76),('arc',(1.2383,4.7883),(1.21,4.8)),
             (0,4.8),(0,4.50),(1.10,4.50)],glass,disc)
        cylinder(child,'Frosted diffuser '+str(i+1),origin,DB.XYZ.BasisZ,1.035,1.64,4.24,g,disc,.04)
    child.Regenerate()
    report['body_bounds_inches']=bounds(list(DB.FilteredElementCollector(child).OfClass(DB.FreeFormElement)))
''' +s[b:]
a=s.index("    cord=fm.AddParameter")
b=s.index("    symbol=doc.GetElement",a)
s=s[:a]+'''    total=fm.AddParameter('Total Drop',DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,True)
    fm.Set(total,48./12)
    offset=fm.AddParameter('Assembly Offset',DB.GroupTypeId.Geometry,DB.SpecTypeId.Length,True)
    fm.SetFormula(offset,'Total Drop - 4.8 in')
    cat=doc.Settings.Categories.NewSubcategory(doc.OwnerFamily.FamilyCategory,'Canopy and Suspension')
    form(doc,'Canopy',DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,
         rounded_rect(-6.75,-3.25,6.75,3.25,.06),1.4,params['Metal Finish'],cat)
    for x in [-3.8,3.8]:
        cylinder(doc,'Canopy rod socket',xyz(x,0,0),DB.XYZ.BasisZ,.65,1.4,1.75,params['Metal Finish'],cat,.035)
''' +s[b:]
s=s.replace('xyz(0,0,60-1037*unit)','xyz(0,0,48-4.8)')
a=s.index('    plane=DB.SketchPlane.Create')
b=s.index('    doc.Regenerate()\n    views=',a)
s=s[:a]+'''    plane=DB.SketchPlane.Create(doc,DB.Plane.CreateByNormalAndOrigin(DB.XYZ.BasisZ,DB.XYZ.Zero))
    for x in [-3.8,3.8]:
        ca=DB.CurveArray()
        for a,b in [(0,math.pi),(math.pi,2*math.pi)]:
            ca.Append(DB.Arc.Create(xyz(x,0,0),.24/12,a,b,DB.XYZ.BasisX,DB.XYZ.BasisY))
        arr=DB.CurveArrArray();arr.Append(ca)
        e=doc.FamilyCreate.NewExtrusion(True,arr,plane,4)
        e.Subcategory=cat
        e.get_Parameter(DB.BuiltInParameter.EXTRUSION_START_PARAM).Set(1.65/12)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.EXTRUSION_END_PARAM),offset)
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),params['Metal Finish'])
''' +s[b:]
s=s.replace('xyz(-25,-25,.001)','xyz(-31,-4,.001)').replace('xyz(25,25,65)','xyz(31,4,49)')
s=s.replace('xyz(0,0,32).Subtract(eye)','xyz(0,0,24).Subtract(eye)')
s=s.replace("xyz(0,-160,32)","xyz(0,-160,24)").replace("xyz(160,0,32)","xyz(160,0,24)")
s=s.replace("preview(doc,'Side',xyz(160,0,24))]","preview(doc,'Side',xyz(160,0,24)),preview(doc,'Appearance',xyz(70,-150,65),True)]")
s=s.replace('for length in [8.,18.1496062992,48.,118.]:','for length in [13.2,36.,48.,67.2]:')
s=s.replace("inst.LookupParameter('Cord Length')","inst.LookupParameter('Total Drop')").replace('expected=length+1063/25.4','expected=length').replace("'cord_inches'","'total_drop_inches'")
s=s.replace("    checkpoint('complete')","    assert report['reopened'] and report['loaded_and_face_placed']\n    assert all(t['pass'] for t in report['flex_tests'])\n    assert all(report['material_tests'].values())\n    assert not report['warnings'] and not report['project_warnings']\n    checkpoint('complete')")
(root/'scripts/build_700lsesf60.py').write_text(s)
compile(s,'build_700lsesf60.py','exec')
print('Prepared builder and four preserved references:',out)
