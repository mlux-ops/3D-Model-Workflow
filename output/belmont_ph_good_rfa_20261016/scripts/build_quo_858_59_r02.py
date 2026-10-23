# -*- coding: utf-8 -*-
"""QUO1249827 - Quorum Veno 858-59 evidence-corrected, UNAPPROVED R02.

Script requires the established Revit 2025 runner globals. Do not execute until
the native and visual verification scope is explicitly approved.

OEM cut sheet:
https://images.junipercdn.com/3206/application-assets/juniper-web/product%20cut%20sheets/858-59.pdf
"""
import os,sys,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from belmont_fixture_core import NativeBuild,xyz,ring
from System.Collections.Generic import List

MODEL='858-59'
SOURCE='https://quoruminternational.com/products/858-59'
CUTSHEET='https://images.junipercdn.com/3206/application-assets/juniper-web/product%20cut%20sheets/858-59.pdf'
# Two OEM-provided 12 inch rods make this particular installation a possible
# configuration; the OEM also includes 2x8, 2x16 rods and 12 inches of chain.
ROD_DROP=24.0
SHADE_HEIGHT=11.25
BODY_HEIGHT=19.0
CANOPY_HEIGHT=.75
BODY_TOP=CANOPY_HEIGHT+ROD_DROP
BODY_BOTTOM=BODY_TOP+BODY_HEIGHT
NOTES=(
    'R02 source-informed visualization candidate; NOT visually approved. '
    'OEM: body D11 x H19 in, shade H11.25 in, canopy D4.75 x H0.75 in. '
    'The 24in installed stems represent 2 supplied 12in rods; manufacturer also '
    'supplies 2x8in, 2x16in rods and 12in chain. Actual installed drop and use '
    'of chain are project choices. Clear glass section is modeled as one '
    'continuous annular shell with assumed 0.125in wall, cylindrical profile '
    'pending source image/profile verification. Steel top structure, fitter and '
    'socket are schematic; no specific angular frame count/position is asserted. '
    'Bulb not supplied. No verified IES, connector or manufacturer CAD.'
)
progress('preflight',{'model':MODEL,'revision':'r02','source':SOURCE})
f=None
try:
    f=NativeBuild(APP,DB,TARGET_RFA,MODEL,'Quorum','Matte Black / Clear - R02',
                  'ceiling',SOURCE,NOTES)
    f.text('Lightology SKU','QUO1249827')
    f.text('OEM Cut Sheet',CUTSHEET)
    f.text('Light Source','1 x E26 medium base; 100W maximum; lamp not included')
    f.text('OEM Suspension Parts','Two 8 in rods; two 12 in rods; two 16 in rods; 12 in chain')
    f.size('OEM Fixture Diameter',11.0)
    f.size('OEM Fixture Body Height',19.0)
    f.size('OEM Shade Height',SHADE_HEIGHT)
    f.size('OEM Canopy Diameter',4.75)
    f.size('OEM Canopy Height',CANOPY_HEIGHT)
    f.size('Selected Stem Drop',ROD_DROP)
    black=f.material('Matte Black',(23,23,23))
    glass=f.material('Clear Glass',(229,232,232),90)
    f.cylinder('OEM envelope canopy',0,0,0,2.375,CANOPY_HEIGHT,black)
    f.cylinder('24in rod representation - two 12in OEM segments',
               0,0,CANOPY_HEIGHT,.20,ROD_DROP,black)
    # Body envelope is 19in; the 11.25in shade occupies its lower section.
    shade_bottom=BODY_BOTTOM-SHADE_HEIGHT
    f.cylinder('Upper structural coupler - shape inferred',
               0,0,BODY_TOP,.75,.5,black)
    f.cylinder('Central socket/stem - shape inferred',
               0,0,BODY_TOP+.5,.35,7.35,black)
    f.cylinder('E26 socket placeholder - shape inferred',
               0,0,shade_bottom,.68,1.0,black)
    # The prior 12 standalone rectangular glass facets were physically invalid.
    # Create a single thin-walled transparent shell with an open bottom.
    # This is a simple CAD proxy: the cut sheet gives HEIGHT only, not a
    # manufacturer's precise shade profile, inner diameter, or glass thickness.
    outer=ring(DB,xyz(DB,0,0,shade_bottom),5.5)
    inner=ring(DB,xyz(DB,0,0,shade_bottom),5.375)
    # Revit 2025 exposes CurveLoop.Flip(), not CreateViaReversed().
    inner.Flip()
    shell=DB.GeometryCreationUtilities.CreateExtrusionGeometry(
        List[DB.CurveLoop]([outer,inner]),DB.XYZ.BasisZ,SHADE_HEIGHT/12.0)
    f.part('Single continuous clear glass shell - inferred circular section',shell,glass)
    f.cylinder('Top glass retainer - inferred',0,0,shade_bottom,5.5,.12,black)
    info=f.finish()
    info['revision']='R02_UNAPPROVED'
    info['oem_cut_sheet']=CUTSHEET
    info['published_fixture_body_dimensions_in']=[11,11,19]
    info['published_shade_height_in']=SHADE_HEIGHT
    info['selected_installed_drop_in']=CANOPY_HEIGHT+ROD_DROP+BODY_HEIGHT
    info['visual_fidelity']='PENDING'
    info['shape_uncertainty']=NOTES
    result.update(info)
    progress('saved',info)
finally:
    if f is not None:f.close()
