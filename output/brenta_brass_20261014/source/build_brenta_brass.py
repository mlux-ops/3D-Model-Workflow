# -*- coding: utf-8 -*-
"""Create the brass Brenta as a native Revit 2025 face-based lighting family."""
import os
import sys
import json

SOURCE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SOURCE)
sys.path.insert(0, SOURCE)
from native_fixture_support import NativeFixture, DB, xyz

NAME = 'AERIN_Brenta_ARN2473HAB-CG_Antique_Brass_R2025'
URL = 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241669'

def configure_appearance(fixture, label, filename, metal):
    material = fixture.materials[label]
    scope = DB.Visual.AppearanceAssetEditScope(fixture.doc)
    asset = scope.Start(material.AppearanceAssetId)
    flag = asset.FindByName('generic_is_metal')
    if flag is not None:
        flag.Value = metal
    diffuse = asset.FindByName('generic_diffuse')
    if diffuse.NumberOfConnectedProperties:
        diffuse.RemoveConnectedAsset()
    diffuse.AddConnectedAsset('UnifiedBitmap')
    bitmap = diffuse.GetSingleConnectedAsset()
    path = os.path.join(OUT, 'textures', filename)
    if not os.path.isfile(path):
        raise RuntimeError('Required appearance map missing: ' + path)
    bitmap.FindByName('unifiedbitmap_Bitmap').Value = path
    for key in ('texture_RealWorldScaleX', 'texture_RealWorldScaleY'):
        p = bitmap.FindByName(key)
        if p is not None:
            p.Value = 1.0
    if metal:
        asset.FindByName('generic_reflectivity_at_90deg').Value = 0.70
    scope.Commit(True)
    scope.Dispose()
    fixture.report['appearance_defaults'][label]['is_metal'] = metal
    fixture.report['appearance_defaults'][label]['diffuse_bitmap'] = path

f = None
try:
    f = NativeFixture(__revit__.Application, OUT, NAME,
        'Visual Comfort Signature / AERIN', 'ARN 2473HAB-CG',
        'Hand-Rubbed Antique Brass - White Glass', 'wall', [3.5,18.5,3.75], 2700)
    metal = f.material('Metal Finish', (174,143,91), .50, 0, .48)
    glass = f.material('Glass Finish', (246,248,246), .94, .88, .04, 0, None, 'Glass')
    diffuser = f.material('Diffuser Finish', (248,244,234), .18, 0, .025, 100, 2700, 'Glass')
    configure_appearance(f, 'Metal Finish', 'Brenta_Hand_Rubbed_Antique_Brass_Color.png', True)
    configure_appearance(f, 'Glass Finish', 'Brenta_Clear_Glass_Color.png', False)
    configure_appearance(f, 'Diffuser Finish', 'Brenta_White_Diffuser_Color.png', False)
    p = f.fm.get_Parameter(DB.BuiltInParameter.ALL_MODEL_URL)
    if p is not None:
        f.fm.Set(p, URL)
    f.note('Published nominal envelope: 3.5 W x 18.5 H x 3.75 projection inches; backplate 3.5 x 5.25. '
        'Glass end diameter 2.024, sleeve diameter 1.914 and height 3.611, diffuser diameter 1.347 '
        'and total length 17.237 are manufacturer-model-derived. Printed overall dimensions govern '
        'over the slightly oversized source model. Glass wall .085, backplate projection .875, '
        'small edge rounds and diffuser end radius .30 are source-photo-informed approximations. '
        'Hand-Rubbed Antique Brass is an appearance approximation; no measured finish calibration. '
        'Fixed native geometry; editable material parameters; 2700K appearance glow, no photometric source. '
        'Requires the manufacturer-specified smaller 2x4-inch junction box.')
    f.length('Backplate Width', 3.5)
    f.length('Backplate Height', 5.25)
    f.box('Brass rectangular backplate', -1.75,-2.625,0, 1.75,2.625,.875, metal,.045)
    f.box('Brass mounting standoff', -.56,-1.24,.875, .56,1.24,1.87, metal,.045)
    axis_offset = 3.75 - 1.012
    f.cylinder('Brass central sleeve', xyz(0,0,axis_offset), DB.XYZ.BasisY,
               .957,-1.8055,1.8055,metal,.05)
    for label, sign in [('Upper',1),('Lower',-1)]:
        axis = DB.XYZ(0,sign,0)
        shell = [(.825,1.70),(.91,1.70),(1.012,9.215),
                 ('arc',(1.00175,9.23975),(.977,9.25)),
                 (0,9.25),(0,9.165),(.925,9.165),(.825,1.70)]
        f.revolve(label+' subtly flared clear glass shell',xyz(0,0,axis_offset),axis,shell,glass)
        core = [(0,1.68),(.56,1.68),(.6735,8.3185),
                ('arc',(.5856320344,8.5306320344),(.3735,8.6185)),(0,8.6185)]
        f.revolve(label+' rounded white diffuser',xyz(0,0,axis_offset),axis,core,diffuser)
    f.report['source_url'] = URL
    f.report['finish'] = 'Hand-Rubbed Antique Brass'
    f.report['geometry_basis'] = 'Native reconstruction using published dimensions and manufacturer component proportions'
    f.report['diffuser_end_rounding_inferred_in'] = .30
    report = f.finish()
    with open(os.path.join(OUT,'build_validation.json'),'w') as stream:
        json.dump(report,stream,indent=2,default=str)
    print('BRENTA_BRASS_BUILD_PASS ' + f.path)
except Exception:
    if f is not None:
        f.fail()
    raise
