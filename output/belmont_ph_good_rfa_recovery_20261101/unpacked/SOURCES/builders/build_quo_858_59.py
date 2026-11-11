# -*- coding: utf-8 -*-
"""QUO1249827, Quorum Veno 858-59, native Revit 2025 ceiling face-based pendant.

Runner globals: APP, DB, JOB, TARGET_RFA, SOURCE_RFA, progress(stage, detail), result.
11-inch fixture diameter and 19-inch body height. Default rod/drop is a modeling choice.
"""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from belmont_fixture_core import NativeBuild

MODEL='858-59'
SOURCE='https://www.lightology.com/index.php?module=prod_detail&prod_id=1249827'
NOTES=('Ceiling-mounted Veno one-light pendant, Matte Black metal / clear glass, E26 lamp. '
       'Published fixture width 11 inches, body height 19 inches; round canopy diameter '
       '4.75 inches and canopy thickness 0.75 inches. '
       '24-inch modeled suspension is a visualization selection, not manufacturer total drop. '
       'Clear glass geometry is a reconstructed open-sided vessel and mounting collars are inferred; '
       'manufacturer cut sheet needed to verify assembly, exact profile and installed minimum drop. '
       'No manufacturer IES or circuit connector.')
progress('preflight',{'model':MODEL,'source':SOURCE})
f=None
try:
    f=NativeBuild(APP,DB,TARGET_RFA,MODEL,'Quorum','Matte Black / Clear','ceiling',SOURCE,NOTES)
    f.text('Lightology SKU','QUO1249827')
    f.text('Light Source','1 x E26 replaceable lamp; lamp not included')
    f.size('Fixture Diameter',11)
    f.size('Fixture Body Height',19)
    f.size('Canopy Diameter',4.75)
    f.size('Nominal Suspension (representative)',24)
    black=f.material('Matte Black',(23,23,23))
    clear=f.material('Clear Glass',(229,232,232),85)
    f.cylinder('Round ceiling canopy',0,0,0,2.375,.75,black)
    f.cylinder('Pendant downrod representative installation',0,0,.75,.20,23.25,black)
    # Fixture body starts below selected 24 inch suspension and extends to 43 in.
    # Native solids and editable materials only; no imported CAD / DirectShape.
    f.cylinder('Upper glass suspension cap',0,0,24.0,1.25,.45,black)
    f.cylinder('Top structure spacer',0,0,24.45,.21,2.0,black)
    f.cylinder('Black center body support',0,0,26.0,.40,16.4,black)
    f.cylinder('Bottom central lamp cradle',0,0,41.6,.78,.55,black)
    # Faceted/open drum interpretation: the clear panels span nominal diameter 11 in;
    # glass sheet edges are bounded by the 19 in published fixture-body height.
    panel_width=1.85
    radius=5.36
    for i in range(12):
        a=2.0*3.141592653589793*i/12.0
        x=radius*__import__('math').cos(a)
        y=radius*__import__('math').sin(a)
        # Thin vertical facets are a placeholder pending manufacturer-sourced glass outline.
        f.box('Clear glass vertical facet %02d'%i,(x-.105,y-.105,26.5,x+.105,y+.105,42.5),clear)
    f.cylinder('Upper shade perimeter ring',0,0,26.3,5.5,.16,black)
    f.cylinder('Lower shade perimeter ring',0,0,42.84,5.5,.16,black)
    info=f.finish()
    info['source_url']=SOURCE
    info['retailer_sku']='QUO1249827'
    info['expected_nominal_body_in']=[11.0,11.0,19.0]
    info['representative_overall_drop_in']=43.0
    info['material_approximations']=NOTES
    result.update(info)
    progress('saved',info)
finally:
    if f is not None:f.close()
