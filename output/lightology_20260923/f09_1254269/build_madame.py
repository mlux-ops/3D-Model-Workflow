# -*- coding: utf-8 -*-
"""Il Fanale Madame wall light A.288.10.ON, Brass.
Native Revit 2025 face-based Lighting Fixtures visualization family.
"""
import os, sys, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from native_fixture_support import NativeFixture, DB, xyz, revolve_solid, cylinder_solid, sphere_solid
from System.Collections.Generic import List

OUT = os.path.dirname(os.path.abspath(__file__))
f = None

try:
    # Installed envelope uses the separately published 3.94 in US backplate diameter.
    # Lightology's 2.36 in published width is the cylindrical head diameter.
    f = NativeFixture(
        __revit__.Application,
        OUT,
        'Il_Fanale_Madame_A28810ON_Brass_R2025',
        'Il Fanale',
        'A.288.10.ON',
        'Brass',
        'wall',
        [3.94, 16.33, 14.17]
    )

    brass = f.material('Brass Finish', (166, 128, 67), .46, 0, .28, material_class='Metal')
    lamp = f.material('Lamp / Interior Finish', (248, 235, 205), .18, .05, .03, 35, 2700, 'Glass')

    f.length('Published Head Diameter', 2.36)
    f.length('Published Overall Height', 16.33)
    f.length('Published Projection', 14.17)
    f.length('US Junction Canopy Diameter', 3.94)
    f.note(
        'Exact linked selection: Il Fanale Madame A.288.10.ON / IFA1254270, Brass. '
        'Lightology publishes 2.36 W x 16.33 H x 14.17 D and separately answers that the '
        'backplate is 3.94 in diameter. The 2.36 in width is therefore modeled as the '
        'cylindrical head diameter, while the installed envelope is 3.94 in wide because '
        'the US junction canopy is larger. Product photography and the preserved printed '
        'diagram govern silhouette: cylindrical open-bottom shade, spherical shoulder, '
        'thin U-shaped bent brass arm, small lower spherical joint and convex round canopy. '
        'Arm tube diameter, canopy projection/profile, shoulder/joint sphere diameters, '
        'shade wall thickness and internal lamp size are image-derived inferences.'
    )

    # Convex US canopy/backplate: 3.94 in diameter, wall face at local Z=0.
    canopy_profile = [
        (0.0, 0.0),
        (1.97, 0.0),
        ('arc', (1.95, .28), (1.82, .58)),
        ('arc', (1.60, 1.02), (1.22, 1.34)),
        ('arc', (.90, 1.56), (.46, 1.65)),
        ('arc', (.22, 1.68), (0.0, 1.68))
    ]
    f.revolve('3.94 inch convex US junction canopy', xyz(0, 1.97, 0), DB.XYZ.BasisZ, canopy_profile, brass)

    # Lower decorative ball and U-shaped arm.
    f.add('Lower spherical arm joint', DB.GeometryCreationUtilities.CreateSphere if False else
          __import__('native_fixture_support').sphere_solid(xyz(0, 2.45, 2.05), .48), brass)

    tube_r = .15
    z_left = 2.50
    z_right = 12.99
    arch_center_top = 16.33 - tube_r
    arch_radius = (z_right - z_left) / 2.0
    arch_base_y = arch_center_top - arch_radius

    p0 = xyz(0, 2.45, z_left)
    p1 = xyz(0, arch_base_y, z_left)
    p2 = xyz(0, arch_base_y, z_right)
    p3 = xyz(0, 7.50, z_right)

    path = DB.CurveLoop()
    first = DB.Line.CreateBound(p0, p1)
    path.Append(first)
    path.Append(DB.Arc.Create(p1, p2, xyz(0, arch_center_top, (z_left + z_right) / 2.0)))
    path.Append(DB.Line.CreateBound(p2, p3))

    rr = tube_r / 12.0
    ring = DB.CurveLoop()
    ring.Append(DB.Arc.Create(p0.Add(DB.XYZ(rr, 0, 0)), p0.Subtract(DB.XYZ(rr, 0, 0)), p0.Add(DB.XYZ(0, 0, rr))))
    ring.Append(DB.Arc.Create(p0.Subtract(DB.XYZ(rr, 0, 0)), p0.Add(DB.XYZ(rr, 0, 0)), p0.Add(DB.XYZ(0, 0, -rr))))
    arm = DB.GeometryCreationUtilities.CreateSweptGeometry(path, 0, first.GetEndParameter(0), List[DB.CurveLoop]([ring]))
    f.add('Bent brass U arm', arm, brass)

    # Spherical shoulder between arm and cylindrical head.
    from native_fixture_support import sphere_solid
    f.add('Spherical shade shoulder', sphere_solid(xyz(0, 7.05, z_right), .45), brass)

    # Open-bottom cylindrical shade with rounded upper shoulder, exact 2.36 in OD.
    shade_origin = xyz(0, 0, z_right)
    outer_profile = [
        (0.0, 2.01),
        (1.18, 2.01),
        (1.18, 5.82),
        ('arc', (1.17, 6.13), (.95, 6.42)),
        ('arc', (.78, 6.58), (.50, 6.60)),
        (0.0, 6.60)
    ]
    outer = revolve_solid(shade_origin, DB.XYZ.BasisY, outer_profile)
    inner = cylinder_solid(shade_origin, DB.XYZ.BasisY, 1.02, 1.86, 5.92)
    shade = DB.BooleanOperationsUtils.ExecuteBooleanOperation(outer, inner, DB.BooleanOperationsType.Difference)
    f.add('2.36 inch open-bottom cylindrical brass shade', shade, brass)

    # A recessed warm lamp/interior cue, kept inside the open shade.
    f.cylinder('Recessed lamp / interior', shade_origin, DB.XYZ.BasisY, .70, 2.24, 4.20, lamp, .05)

    f.report['source_page'] = 'https://www.lightology.com/index.php?module=prod_detail&prod_id=1254269&option_id=1254270'
    f.report['source_specification'] = 'https://www.lightology.com/index.php?module=pdf_specification_sheet&prod_id=1254270'
    f.report['source_installation'] = 'https://www.lightology.com/img/prod/pdf/IF-IM_288.10_R02-092723.pdf'
    f.report['published_dimensions_in'] = {
        'head_diameter_width': 2.36,
        'overall_height': 16.33,
        'projection': 14.17,
        'us_junction_canopy_diameter': 3.94
    }
    f.report['installed_envelope_expected_in'] = [3.94, 16.33, 14.17]
    f.report['inferred_geometry_in'] = {
        'arm_tube_diameter': tube_r * 2.0,
        'lower_joint_sphere_diameter': .96,
        'upper_shoulder_sphere_diameter': .90,
        'canopy_projection': 1.68,
        'shade_wall_nominal': .16
    }

    report = f.finish()
    with open(os.path.join(OUT, 'validation.json'), 'w') as stream:
        json.dump(report, stream, indent=2, default=str)
except Exception:
    if f is not None:
        f.fail()
    raise

