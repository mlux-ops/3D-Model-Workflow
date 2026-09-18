from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'scripts/build_vera.py').read_text()
s=s.replace("'vera'","'kamden'").replace('Kuzco_Vera_22_87_Black_Glow_R2025','Visual_Comfort_Kamden_1279641_R2025').replace('Vera','Kamden')
s=s.replace('22.9 inch - Black - Warm Glow','22.5 inch - Nightshade Black - Clear')
s=s.replace('22.87', '22.5').replace('4.75','4.3').replace('3.25','4.7').replace('Kuzco Lighting','Visual Comfort Modern')
s=s.replace('White Polycarbonate Warm Glow','White Inner Diffuser').replace('350.)','0.)')
s=s.replace("    return {'Frame Finish':steel,'Diffuser Finish':mat}","""    glass,appearance=clone_material(doc,'Kamden - Clear Glass',source,(226,237,240),85)
    glass.MaterialClass='Glass'
    scope=DB.Visual.AppearanceAssetEditScope(doc); a=scope.Start(appearance.Id)
    set_color(a,'generic_diffuse',(245,250,252))
    scalar(a,'generic_glossiness',.95); scalar(a,'generic_transparency',.94)
    scalar(a,'generic_refraction_index',1.52)
    scalar(a,'generic_reflectivity_at_0deg',.04); scalar(a,'generic_reflectivity_at_90deg',.9)
    scalar(a,'generic_self_illum_luminance',0.)
    scope.Commit(True); scope.Dispose()
    return {'Frame Finish':steel,'Diffuser Finish':mat,'Glass Finish':glass}""")
s=s.replace("['Housing','Diffusers','Mount']","['Housing','Diffusers','Mount','Glass']")
a=s.index("    box('Square backplate'")
b=s.index('    doc.Regenerate()',a)
s=s[:a]+"""    # Local X width, Y vertical, Z projects away from native wall face.
    box('Backplate',-2.5,-2.15,0,2.5,2.15,.3,metal,cats['Mount'])
    box('Continuous rear rail',-10.9,-.39,.30,10.9,.39,.66,metal,cats['Housing'])
    glass=params['Glass Finish']
    for x in [-9.05,0,9.05]:
        # Three open rectangular metal collars; maximum total width 22.5.
        outer=profile_loop(xyz(x,-.39,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,rounded_rect(-2.2,.48,2.2,4.7,.025))
        inner=profile_loop(xyz(x,-.39,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,rounded_rect(-1.99,.70,1.99,4.48,.025))
        solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([outer,inner]),DB.XYZ.BasisY,.78/12.)
        e=DB.FreeFormElement.Create(doc,solid);e.Subcategory=cats['Housing']
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),metal)
        # Clear thick-walled rectangular shade, open at top and bottom.
        outer=profile_loop(xyz(x,-1.30,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,rounded_rect(-2.06,1.55,2.06,4.55,.06))
        inner=profile_loop(xyz(x,-1.30,0),DB.XYZ.BasisX,DB.XYZ.BasisZ,rounded_rect(-1.90,1.71,1.90,4.39,.06))
        solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([outer,inner]),DB.XYZ.BasisY,2.60/12.)
        e=DB.FreeFormElement.Create(doc,solid);e.Subcategory=cats['Glass']
        fm.AssociateElementParameterToFamilyParameter(e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM),glass)
        form(doc,'White inner diffuser',xyz(x,0,1.87),DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ,
            rounded_rect(-1.69,-1.01,1.69,1.01,.12),2.35,glow,cats['Diffusers'])
"""+s[b:]
s=s.replace("xyz(12,3,3.6)","xyz(12,3,4.8)")
s=s.replace('22.5 x 4.3 x 4.7 inch overall; 4.3 square x 0.5 inch backplate from drawing. Bar height, curved cross-section, diffuser recess and cap seams inferred from photos. Dual diffusers; no photometric source.', '22.5 x 4.3 x 4.7 inch overall and 5 inch backplate width from supplied PDF. Shade dimensions, glass thickness, rail/collar sizes and inner diffuser geometry inferred. Fixed visualization geometry; no photometric source.')
s=s.replace('black housing and dual warm white diffusers','black frame, three clear glass shades and white inner diffusers')
s=s.replace("    checkpoint('complete')","""    assert report['reopened'] and report['loaded_and_face_placed']
    assert all(report['material_tests'].values())
    assert report['diffuser_count']==3
    assert all(abs(a-b)<.01 for a,b in zip(report['dimensions_inches'],[22.5,4.3,4.7]))
    checkpoint('complete')""")
(root/'scripts/build_kamden.py').write_text(s)
