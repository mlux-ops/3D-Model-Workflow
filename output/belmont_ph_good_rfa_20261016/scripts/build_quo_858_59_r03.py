# -*- coding: utf-8 -*-
"""Quorum Veno 858-59 R03 PHOTO-INTERPRETED native Revit 2025 candidate.
Unexecuted, unapproved. Requires APP, DB, TARGET_RFA, progress, result.
"""
import os, sys, math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from System.Collections.Generic import List
from belmont_fixture_core import NativeBuild, xyz

MODEL='858-59'
SOURCE='https://quoruminternational.com/products/858-59'
CUTSHEET='https://images.junipercdn.com/3206/application-assets/juniper-web/product%20cut%20sheets/858-59.pdf'
PHOTO='https://cdn11.bigcommerce.com/s-c1csojjx4j/images/stencil/494x536/products/4597273/5799746/1302095__38680.1750748034.jpg?c=1'
CANOPY_H=.75
STEM_H=24.0
BODY_H=19.0
SHADE_H=11.25
SHADE_BASE=CANOPY_H+STEM_H+BODY_H-SHADE_H
WALL=.125
# Interpreted photo silhouette (height above bottom, outer radius in inches).
# The OEM documents only shade height 11.25in and body diameter max 11in.
PROFILE=[(0.,4.65),(.7,4.8),(1.7,5.15),(3.2,5.5),
         (4.7,5.42),(6.25,4.95),(7.75,4.12),
         (9.1,3.05),(10.25,2.22),(11.25,1.72)]
NOTES=('R03 continuous native revolved glass bell; photo-interpreted contour, '
       'not OEM-measured. OEM D11 x H19 body, shade H11.25. Profile station '
       'radii, shell thickness .125in, socket details and placement of glass '
       'within body are inferred. 24in selected rods = two supplied 12in '
       'stems. No verified IES or MEP connector; native/visual QA pending.')

def bell_solid(DB):
    """Single closed annular XZ section revolved 360 degrees about Z."""
    outer=[(r,SHADE_BASE+z) for z,r in PROFILE]
    inner=[(r-WALL,z) for r,z in reversed(outer)]
    if min(r for r,z in inner)<=0 or max(r for r,z in outer)>5.500001:
        raise ValueError('Glass radial envelope invalid')
    if abs(outer[-1][1]-outer[0][1]-SHADE_H)>1e-8:
        raise ValueError('Glass height does not match OEM shade height')
    vertices=outer+inner
    loop=DB.CurveLoop()
    tol=APP.ShortCurveTolerance
    for i,point in enumerate(vertices):
        nextpoint=vertices[(i+1)%len(vertices)]
        a=xyz(DB,point[0],0,point[1])
        b=xyz(DB,nextpoint[0],0,nextpoint[1])
        if a.DistanceTo(b)<=tol:
            raise ValueError('Profile segment shorter than Revit ShortCurveTolerance')
        loop.Append(DB.Line.CreateBound(a,b))
    frame=DB.Frame(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ)
    return DB.GeometryCreationUtilities.CreateRevolvedGeometry(
        frame,List[DB.CurveLoop]([loop]),0.0,2.0*math.pi)

progress('preflight',{'model':MODEL,'revision':'R03_PHOTO_INTERPRETED'})
f=None
try:
    f=NativeBuild(APP,DB,TARGET_RFA,MODEL,'Quorum',
                  'Matte Black / Clear - R03 photo interpreted',
                  'ceiling',SOURCE,NOTES)
    f.text('Lightology SKU','QUO1249827')
    f.text('Official Cut Sheet',CUTSHEET)
    f.text('Photo Reference',PHOTO)
    f.text('Geometry Provenance','Photo-interpreted; not dimensioned OEM section')
    f.text('Light Source','One E26 medium base, 100W maximum; not supplied')
    f.text('OEM Suspension Parts','2x8in 2x12in 2x16in rods, 12in chain')
    f.size('OEM Fixture Diameter',11)
    f.size('OEM Fixture Body Height',BODY_H)
    f.size('OEM Shade Height',SHADE_H)
    f.size('OEM Canopy Diameter',4.75)
    f.size('OEM Canopy Height',CANOPY_H)
    f.size('Selected Rod Drop',STEM_H)
    black=f.material('Matte Black',(23,23,23))
    glass=f.material('Clear Glass',(229,232,232),90)
    f.cylinder('Canopy',0,0,0,2.375,CANOPY_H,black)
    f.cylinder('Two representative 12in rods',0,0,CANOPY_H,.2,STEM_H,black)
    body_top=CANOPY_H+STEM_H
    f.cylinder('Upper coupling - inferred',0,0,body_top,.75,.5,black)
    f.cylinder('Center support - inferred',0,0,body_top+.5,.32,
               SHADE_BASE-(body_top+.5)+.25,black)
    f.cylinder('E26 socket - inferred',0,0,SHADE_BASE+.25,.58,1.,black)
    f.part('Continuous clear glass photo-interpreted bell',bell_solid(DB),glass)
    info=f.finish()
    info['revision']='R03_PHOTO_INTERPRETED_UNAPPROVED'
    info['photo_url']=PHOTO
    info['cut_sheet_url']=CUTSHEET
    info['profile_height_radius_in']=PROFILE
    info['assumed_wall_in']=WALL
    info['manufacturer_body_dimensions_in']=[11.,11.,19.]
    info['manufacturer_shade_height_in']=11.25
    info['selected_total_drop_in']=CANOPY_H+STEM_H+BODY_H
    info['visual_source_review']='PENDING'
    result.update(info)
    progress('saved',info)
finally:
    if f is not None:f.close()
