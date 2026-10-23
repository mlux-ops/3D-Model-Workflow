# -*- coding: utf-8 -*-
"""HIN990485, Hinkley Eos 53860BK, native Revit 2025 face-based wall vanity light.

Runner globals: APP, DB, JOB, TARGET_RFA, SOURCE_RFA, progress(stage, detail), result.
Expected geometry envelope in inches: 25 W x 5.5 H x 3 D.
"""
import os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from belmont_fixture_core import NativeBuild

MODEL='53860BK'
SOURCE='https://www.lightology.com/index.php?module=prod_detail&option_id=990485&prod_id=990486'
NOTES=('Wall-mounted horizontal vanity fixture; Black metal and etched opal optics. '
       'Published 25 W x 5.5 H x 3 D inches, integrated LED 19 W, 3000 K. '
       'Mount plate, two horizontal LED lens bars and end caps are interpreted from source silhouette; '
       'rail spacing, diffuser thickness and collar proportions require manufacturer CAD/photo approval. '
       'Fixed-shape visualization model; no circuit connector or manufacturer IES.')
progress('preflight',{'model':MODEL,'source':SOURCE})
f=None
try:
    f=NativeBuild(APP,DB,TARGET_RFA,MODEL,'Hinkley','Black / Etched', 'wall',SOURCE,NOTES)
    f.text('Lightology SKU','HIN990485')
    f.text('Light Source','Integrated LED; 19 W; 3000 K')
    f.size('Overall Width',25)
    f.size('Overall Height',5.5)
    f.size('Overall Projection',3)
    black=f.material('Black Metal',(22,23,24))
    opal=f.material('Etched Opal',(245,244,237),4)
    # Wall mount is local z=0, the fixture projects into positive local z.
    f.box('Slim centered wall mounting plate',(-2.375,-1.6,0,2.375,1.6,.28),black)
    f.box('Fixture support saddle',(-1.8,-1.2,.28,1.8,1.2,1.13),black)
    f.box('Horizontal central tie',(-11.9,-.35,1.10,11.9,.35,2.50),black)
    # Retain exact 25-inch X and 5.5-inch Y envelope and 3-inch wall projection.
    for center in (-2.22,2.22):
        f.box('Black integrated LED carrier',(-12.5,center-.53,1.52,12.5,center+.53,2.89),black)
        f.box('Etched acrylic LED diffuser',(-12.21,center-.39,2.89,12.21,center+.39,3.0),opal)
    for x0,x1 in [(-12.50,-12.24),(12.24,12.50)]:
        f.box('Black rail end closure',(x0,-2.75,1.52,x1,2.75,2.87),black)
    info=f.finish()
    info['source_url']=SOURCE
    info['retailer_sku']='HIN990485'
    info['expected_geometry_in']=[25.0,5.5,3.0]
    info['material_approximations']=NOTES
    result.update(info)
    progress('saved',info)
finally:
    if f is not None:f.close()
