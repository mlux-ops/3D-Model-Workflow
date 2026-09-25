from pathlib import Path
import re,shutil,ast
root=Path(__file__).resolve().parents[1]
fan=root/'f01_816712'/'build_f01_816712.py';text=fan.read_text(encoding='utf-8-sig')
history=fan.parent/'history';history.mkdir(exist_ok=True)
for p in [fan,fan.parent/'validation_latest.json']:
    target=history/(p.stem+'_first_failed'+p.suffix)
    if p.exists() and not target.exists():shutil.copy2(p,target)
text=text.replace('import os\n','import os\nimport sys\nsys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"tools"))\nfrom native_fixture_support import loop as smooth_profile_loop\n',1)
text=text.replace('HEIGHT = 19.8','HEIGHT = 13.8\nBLADE_PLAN_SCALE = 1.0')
a=text.index('def profile_loop(');b=text.index('def revolve(',a)
text=text[:a]+'''def profile_loop(origin, u, v, pts):
    return smooth_profile_loop(origin,u,v,pts)

'''+text[b:]
text=text.replace("fm.SetFormula(p, str(PITCH) + ' deg')","fm.Set(p, math.radians(PITCH))")
text=text.replace("pts.append(xyz(radius, y, z))","pts.append(xyz(radius*BLADE_PLAN_SCALE, y*BLADE_PLAN_SCALE, z))")
a=text.index('    stations = [',text.index('def blade_solid'))
b=text.index('    loops = ',a)
text=text[:a]+'''    stations = [
        (2.65, 0.00, 4.00, .50, 11.88, 20.0),
        (4.80,-0.18, 3.60, .47, 11.90, 18.0),
        (8.50,-0.55, 3.75, .40, 11.93, 16.0),
        (12.5,-1.05, 4.45, .35, 11.98, 14.0),
        (17.0,-1.55, 5.20, .30, 12.03, 12.0),
        (21.0,-1.83, 5.70, .25, 12.08, 10.0),
        (24.2,-2.08, 5.35, .22, 12.13, 8.5),
        (25.6,-2.17, 3.80, .18, 12.16, 7.5),
        (26.0,-2.20, 0.80, .14, 12.17, 7.0),
    ]
'''+text[b:]
text=text.replace('    global TX\n    doc = app.NewFamilyDocument(TEMPLATE)','    global TX, BLADE_PLAN_SCALE\n    doc = app.NewFamilyDocument(TEMPLATE)',1)
a=text.index('    # Photo-matched tapered canopy')
b=text.index('    for i, a in enumerate',a)
text=text[:a]+'''    # Manufacturer 13.8-inch assembled height with the supplied 6-inch rod.
    # Curved profiles retain the compact housing and shallow exposed opal disk.
    elems.append(revolve(doc,'Canopy',[(0,0),(2.93,0),('arc',(2.9795,.0205),(3,.07)),
        (3,.25),('arc',(2.8,1.1),(2.3,1.65)),('arc',(1.55,2.22),(1.15,2.6)),(0,2.6)],p_metal,body_cat))
    elems.append(cylinder(doc,'Six-inch half-inch downrod',.25,2.25,8.25,p_metal,body_cat))
    elems.append(revolve(doc,'Compact smooth motor housing',[(0,8.10),(.72,8.10),
        ('arc',(.93,8.65),(1.20,9.0)),('arc',(2.60,10.02),(3.40,11.70)),
        (3.40,12.62),(0,12.62)],p_metal,body_cat))
    elems.append(revolve(doc,'Slim integrated light bezel',[(0,12.48),(3.40,12.48),
        (3.44,12.65),(3.44,13.18),(3.34,13.26),(0,13.26)],p_metal,body_cat))
    elems.append(revolve(doc,'Shallow opal light disk',[(0,12.18),(3.34,12.18),
        ('arc',(3.4107,12.2093),(3.44,12.28)),(3.44,13.35),
        ('arc',(3.35,13.69),(3.0,13.80)),(0,13.80)],p_glow,diff_cat))
    base_blade=blade_solid()
    points=[p for face in base_blade.Faces for p in face.Triangulate(1.0).Vertices]
    raw_radius=max(math.sqrt(p.X*p.X+p.Y*p.Y) for p in points)*12.0
    BLADE_PLAN_SCALE=26.0/raw_radius
    base_blade=blade_solid()
    REPORT['blade_plan_scale_to_nominal_sweep']=BLADE_PLAN_SCALE
    REPORT['manufacturer_dimensional_authority']={'overall_height_in':13.8,'rod_length_in':6.0,
        'rod_diameter_in':.5,'canopy_diameter_in':6.0,'housing_diameter_in':6.8,
        'glass_diameter_in':6.88,'glass_height_in':1.62,'retailer_conflicting_height_in':19.8,
        'source':'sources/VisualComfort_3MAVR52BKBKD_Spec.pdf'}
'''+text[b:]
text=text.replace("(250,245,233), 0.25, 0.06, 650.0","(250,245,233), 0.18, 0.0, 160.0")
text=text.replace('height_19_8_in','height_13_8_in')
text=text.replace('52 in sweep, 19.8 in overall height, 13 deg nominal pitch, 6 in downrod and three blades from Lightology.','52 in sweep, 13.8 in overall height, 6 in x .5 in downrod, 6 in canopy, 6.8 in housing and 6.88 x 1.62 in glass from exact manufacturer specification, which supersedes retailer 19.8 in height. 13 degree nominal pitch; three blades.')
text=text.replace("up = DB.XYZ.BasisZ\n","up = DB.XYZ(0,0,-1) if doc.IsFamilyDocument else DB.XYZ.BasisZ\n",1)
text=text.replace("    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'","    REPORT['technical_pass']=REPORT['native_gate']\n    REPORT['stage']='complete' if REPORT['native_gate'] else 'failed_gates'\n    REPORT['finished_utc'] = datetime.datetime.utcnow().isoformat() + 'Z'",1)
text=text.replace("    checkpoint('FAILED')\nfinally:","    checkpoint('FAILED')\n    raise\nfinally:")
ast.parse(text);fan.write_text(text,encoding='utf8')
nodes=root/'f07_833919'/'build_nodes_payload_expanded.py';s=nodes.read_text(encoding='utf-8-sig')
h=nodes.parent/'history';h.mkdir(exist_ok=True)
if not (h/'build_nodes_first_failed.py').exists():shutil.copy2(nodes,h/'build_nodes_first_failed.py')
old="metal, cats['Reflector'], rec, .025)"
if old not in s:raise RuntimeError('Nodes reflector context changed')
s=s.replace(old,"metal, cats['Reflector'], rec, 0)")
ast.parse(s);nodes.write_text(s,encoding='utf8')
# Source-driven optical review: opaque alabaster retains its real diffuse bitmap.
covet=root/'f10_1242580'/'build_covet.py';s=covet.read_text(encoding='utf-8-sig')
print('COVET_MATERIAL_LINES')
for line in s.splitlines():
    if 'material(' in line or 'Natural Alabaster' in line:print(line)
print('FAN_AND_NODES_REPAIRS_SAVED')