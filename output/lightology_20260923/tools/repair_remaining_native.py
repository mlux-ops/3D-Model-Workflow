from pathlib import Path
import ast
root=Path(__file__).resolve().parents[1]
f=root/'f01_816712'/'build_f01_816712.py';s=f.read_text()
a=s.index('def geometry_points(');b=s.index('def measured_extents(',a)
s=s[:a]+'''def geometry_points(element):
    opts=DB.Options();opts.DetailLevel=DB.ViewDetailLevel.Fine
    points=[]
    def visit(geometry):
        for obj in geometry:
            if isinstance(obj,DB.Solid) and obj.Volume>1e-12:
                for face in obj.Faces:points.extend(list(face.Triangulate(1.).Vertices))
                for edge in obj.Edges:
                    curve=edge.AsCurve();count=1 if isinstance(curve,DB.Line) else 128
                    points.extend(curve.Evaluate(float(i)/count,True) for i in range(count+1))
            elif isinstance(obj,DB.GeometryInstance):visit(obj.GetInstanceGeometry())
    visit(element.get_Geometry(opts))
    return points

'''+s[b:]
s=s.replace("    finish_report()\nexcept Exception as ex:","    finish_report()\n    if not REPORT.get('technical_pass'):raise RuntimeError('Native validation gates failed; see validation_latest.json')\nexcept Exception as ex:")
ast.parse(s);f.write_text(s)
n=root/'f07_833919'/'build_nodes_payload_expanded.py';s=n.read_text()
s=s.replace('import os\n','import os\nimport sys\nsys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"tools"))\nfrom native_fixture_support import measured_geometry_bounds\n',1)
a=s.index('def elem_bounds(');b=s.index('def ',s.index('def bbox_inches(',a)+4)
s=s[:a]+'''def elem_bounds(elements):
    return measured_geometry_bounds(elements)


def bbox_inches(element):
    b=measured_geometry_bounds([element])
    return {'min':b[:3],'max':b[3:],'size':[b[i+3]-b[i] for i in range(3)]}


'''+s[b:]
s=s.replace('PIVOT_Z = 1.82','PIVOT_Z = 1.77073885847')
s=s.replace("    box = inst.get_BoundingBox(None)\n    world_dims = [(box.Max.X - box.Min.X) * 12, (box.Max.Y - box.Min.Y) * 12, (box.Max.Z - box.Min.Z) * 12]","    box = inst.get_BoundingBox(None)\n    measured=measured_geometry_bounds([inst])\n    world_dims = [measured[i+3]-measured[i] for i in range(3)]")
s=s.replace("base, milk_rgb, 12)","base, milk_rgb, 0)").replace("scalar(a, 'generic_transparency', .12)","scalar(a, 'generic_transparency', 0.0)")
s=s.replace('bounding boxes','native surface/analytic-edge measurements').replace('bounding extent','native surface extent')
ast.parse(s);n.write_text(s)
p=root/'f09_1254269'/'build_madame.py';s=p.read_text().replace('1.03,.11,.20,optic,.035)','1.03,.11,.20,optic,0)');ast.parse(s);p.write_text(s)
p=root/'f11_1476233'/'build_mizu.py';s=p.read_text()
a=s.index('        points=[];t=z/3.9');b=s.index('    return DB.GeometryCreationUtilities.CreateLoftGeometry',a)
s=s[:a]+'''        t=z/3.9
        def point(a):
            variation=1+.028*math.cos(3*a+seed)+.015*math.sin(5*a+seed*.7)
            x=(r*variation*math.cos(a)+.075*math.sin(math.pi*t)*math.sin(seed))*scale-offset
            y=(r*variation*math.sin(a)*(.92+.025*math.sin(seed))+.055*math.sin(math.pi*t)*math.cos(seed))*scale
            return xyz(x,y,z)
        profile=DB.CurveLoop()
        for j in range(16):
            a=2*math.pi*j/16.;b=2*math.pi*(j+1)/16.
            profile.Append(DB.Arc.Create(point(a),point(b),point((a+b)*.5)))
        loops.append(profile)
'''+s[b:]
ast.parse(s);p.write_text(s)
print('TARGETED_NATIVE_REPAIRS_READY')