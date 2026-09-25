# -*- coding: utf-8 -*-
"""Buster + Punch Forked Shade pendant, brass, nominal 9.8 inch medium."""
import os,sys,math,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'tools'))
from native_fixture_support import NativeFixture, DB, xyz, loop
from System.Collections.Generic import List
OUT=os.path.dirname(os.path.abspath(__file__))
f=None
try:
    body_start=19.02
    total=body_start+18.8
    f=NativeFixture(__revit__.Application,OUT,'BusterPunch_Forked_Shade_Brass_9_84_R2025','Buster + Punch','NFP-813167','Brass - Medium 9.84 in - 37.82 in installed drop','ceiling',[9.84,9.84,total],2700)
    brass=f.material('Brass Finish',(177,137,76),.48,0,.3)
    cord=f.material('Black Cord Finish',(19,19,20),.10,0,.02,material_class='Plastic')
    lamp=f.material('Lamp Diffuser Finish',(250,245,232),.18,0,.02,40,2700,'Glass')
    f.length('Shade Diameter',9.84);f.length('Shade Height',5.9);f.length('Fixture Body Height',18.8);f.length('Installed Cord Length',18.)
    f.note('Lightology9.84in medium and manufacturer May2022 dimension sheet: shade9.84dia x5.9H, upper assembly12.9H, canopy4.9dia x1.02H; total fixture body18.8H. Current Lightology SKU NFP-813167 differs from legacy drawing NFP-493172; dimensions/medium selection agree. Default18in visible cord is an installation choice. Dome curvature, fork bend/tube diameter, machined sleeve2.22dia and96-flute spacing are photo-derived inferences. Native hollow open shade and swept open fork; no manufacturing-tolerance claim.')
    f.cylinder('Canopy',xyz(),DB.XYZ.BasisZ,2.45,0,1.02,brass,.06)
    f.cylinder('Black pendant cable',xyz(),DB.XYZ.BasisZ,.12,1.02,body_start,cord)
    f.cylinder('Long cast brass stem',xyz(0,0,body_start),DB.XYZ.BasisZ,.28,0,8.45,brass,.04)
    path=DB.CurveLoop()
    a=xyz(-.57,0,body_start+9.8);b=xyz(-.57,0,body_start+8.9);c=xyz(.57,0,body_start+8.9);d=xyz(.57,0,body_start+9.8)
    first=DB.Line.CreateBound(a,b);path.Append(first)
    path.Append(DB.Arc.Create(b,c,xyz(0,0,body_start+8.33)))
    path.Append(DB.Line.CreateBound(c,d))
    r=.26/12.
    ring=DB.CurveLoop()
    ring.Append(DB.Arc.Create(a+DB.XYZ(r,0,0),a-DB.XYZ(r,0,0),a+DB.XYZ(0,r,0)))
    ring.Append(DB.Arc.Create(a-DB.XYZ(r,0,0),a+DB.XYZ(r,0,0),a-DB.XYZ(0,r,0)))
    swept=DB.GeometryCreationUtilities.CreateSweptGeometry(path,0,first.GetEndParameter(0),List[DB.CurveLoop]([ring]))
    f.add('Open rounded cast fork',swept,brass)
    f.cylinder('Socket upper rim',xyz(0,0,body_start),DB.XYZ.BasisZ,1.13,9.75,9.88,brass,.035)
    teeth=[]
    for i in range(192):
        angle=2*math.pi*i/192.;radius=1.11 if i%2==0 else 1.102
        teeth.append((radius*math.cos(angle),radius*math.sin(angle)))
    prof=loop(xyz(0,0,body_start+9.88),DB.XYZ.BasisX,DB.XYZ.BasisY,teeth)
    f.add('96 linear machined flutes',DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([prof]),DB.XYZ.BasisZ,2.42/12.),brass)
    f.cylinder('Socket bottom rim',xyz(0,0,body_start),DB.XYZ.BasisZ,1.13,12.30,12.43,brass,.035)
    f.cylinder('Shade neck',xyz(0,0,body_start),DB.XYZ.BasisZ,1.07,12.43,13.0,brass)
    # Elliptical spun-metal dome, open below, with a real inner surface.
    zc=body_start+16.65;outer_r=4.92;inner_r=4.84;neck_r=1.04
    outer_theta=-math.acos(neck_r/outer_r)
    outer_ry=3.75/(-math.sin(outer_theta))
    outer_arc=DB.Ellipse.CreateCurve(xyz(0,0,zc),outer_r/12,outer_ry/12,DB.XYZ.BasisX,DB.XYZ.BasisZ,outer_theta,0)
    inner_theta=-math.acos(neck_r/inner_r);inner_ry=outer_ry-.08
    inner_arc=DB.Ellipse.CreateCurve(xyz(0,0,zc),inner_r/12,inner_ry/12,DB.XYZ.BasisX,DB.XYZ.BasisZ,inner_theta,0).CreateReversed()
    section=DB.CurveLoop();section.Append(outer_arc)
    section.Append(DB.Line.CreateBound(outer_arc.GetEndPoint(1),xyz(outer_r,0,total)))
    section.Append(DB.Line.CreateBound(xyz(outer_r,0,total),xyz(inner_r,0,total)))
    section.Append(DB.Line.CreateBound(xyz(inner_r,0,total),inner_arc.GetEndPoint(0)))
    section.Append(inner_arc)
    section.Append(DB.Line.CreateBound(inner_arc.GetEndPoint(1),outer_arc.GetEndPoint(0)))
    frame=DB.Frame(DB.XYZ.Zero,DB.XYZ.BasisX,DB.XYZ.BasisY,DB.XYZ.BasisZ)
    shade=DB.GeometryCreationUtilities.CreateRevolvedGeometry(frame,List[DB.CurveLoop]([section]),0,math.pi*2)
    f.add('Hollow spun brass dome with open underside',shade,brass)
    f.cylinder('Recessed lamp optic',xyz(0,0,body_start),DB.XYZ.BasisZ,.88,13.10,13.85,lamp,.07)
    f.report['source_page']='https://www.lightology.com/index.php?module=prod_detail&prod_id=1149899'
    f.report['derived_dimensions']={'shade_diameter_in':9.84,'shade_height_in':5.9,'upper_assembly_height_in':12.9,'installed_cord_in':18.,'body_height_in':18.8,'fork_open':True,'shade_open':True,'knurl_count':96}
    report=f.finish()
    with open(os.path.join(OUT,'validation.json'),'w') as stream:json.dump(report,stream,indent=2,default=str)
except Exception:
    if f is not None:f.fail()
    raise