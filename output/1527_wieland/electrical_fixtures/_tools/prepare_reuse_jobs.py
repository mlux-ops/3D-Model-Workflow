"""Stage exact-variant rebuilds from inspected native source geometry."""
from pathlib import Path
from PIL import Image
import json
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
groups = {g['key']: g for g in json.loads((ROOT / 'GROUPS.json').read_text())['groups']}

def mat(name, rgb, gloss=.25, transparency=0, reflectivity=.08, material_class='Metal'):
    return dict(label=name, rgb=rgb, gloss=gloss, transparency=transparency,
                reflectivity=reflectivity, material_class=material_class)
black = mat('Black Metal Finish', [24, 24, 24])
white = mat('Diffuser Finish', [244, 244, 240], .16, 0, .03, 'Plastic')
glass = mat('Clear Glass Finish', [245, 247, 248], .96, .88, .10, 'Glass')
jobs = [
 dict(key='HNM1353351', model='OSTRsconce-BSS-FR', name='Hollis_Morris_Oyster_BSS_FR_R2025', manufacturer='hollis+morris', host='wall', dimensions=[5.24, 12, 3],
      source_rfa=str(REPO / 'output/oyster/Hollis_Morris_Oyster_Visualization_R2025_v2.rfa'),
      category_material={'Capsule Frame': 'Frame Finish', 'Smooth Diffuser': 'Diffuser Finish'},
      materials=[mat('Frame Finish', [174, 179, 182], .40, 0, .40), white],
      notes='Current exact SKU is brushed stainless steel with frosted diffuser. Geometry rebuilt from inspected prior native family; source file preserved. Small frame edge radius and uniform brushed-metal approximation are visual inferences.',
      rfa_search='Manufacturer offers Request 3D models, without a direct anonymous RFA link on the inspected page.',
      source_url='https://hollisandmorris.com/products/oyster-sconce2'),
 dict(key='DVP27002GR-CL', model='DVP27002GR-CL', name='DVI_Courcelette_DVP27002GR_CL_R2025', manufacturer='DVI Lighting', host='ceiling', dimensions=[46.6, 21.59, 50.5],
      source_rfa=str(REPO / 'output/courcelette/DVI_Courcelette_873039_Graphite_Clear_Glow_R2025.rfa'),
      category_material={'Canopy and Suspension': 'Graphite Finish', 'Graphite Framework': 'Graphite Finish', 'Visible Bulbs': 'Bulb Finish', 'Clear Globes': 'Clear Glass Finish'},
      materials=[mat('Graphite Finish', [51, 53, 55], .28), mat('Bulb Finish', [249, 246, 237], .20, .1, .03, 'Glass'), glass],
      notes='Manufacturer body envelope 46.6 x 21.59 x 12.95 inches. ASSUMPTION: 50.5-inch installed drop. Arm centers, globe diameter, canopy and internal lamps remain photo/drawing-derived details from inspected prior native geometry. Fixed geometry; editable material finishes.',
      rfa_search='No native RFA link in current public product technical resources inspected; prior native reconstruction retained as geometry source.',
      source_url='https://www.lightology.com/index.php?module=prod_detail&prod_id=873039'),
 dict(key='AST1561665', model='1184057+5048001', name='Astro_Duo_1184057_5048001_R2025', manufacturer='Astro Lighting', host='ceiling', dimensions=[210/25.4, 210/25.4, 1000/25.4],
      source_rfa=str(REPO / 'output/duo/Astro_Duo_1561665_White_Opal_Glow_R2025.rfa'),
      category_material={'Upper Shade': 'Metal Finish', 'Lower Glass': 'Opal Glass Finish', 'Canopy and Stem': 'Metal Finish', 'Suspension Cord': 'Cord Finish'},
      materials=[mat('Metal Finish', [243, 243, 239], .18), mat('Opal Glass Finish', [249, 249, 244], .38, .08, .03, 'Glass'), mat('Cord Finish', [238, 238, 235], .10, 0, .02, 'Plastic')],
      skip_ids=['3224'], replacement_canopy={'diameter':4.3,'height':1.0,'material':'Metal Finish'},
      notes='210 mm diameter/height shade rebuilt from inspected prior native geometry. Canopy corrected from prior 96 mm to current scheduled 4.3-inch diameter. ASSUMPTION: 1-inch canopy height and 1000 mm installed drop; source does not fully dimension those installed details. Finishes matte white and opal; material parameters editable.',
      rfa_search='Public product resources inspected; no exact anonymous native RFA located. Prior native shade geometry is the documented rebuild source.',
      source_url='https://www.lightology.com/index.php?module=prod_detail&prod_id=1561665'),
 dict(key='KZC1009570', model='PD62014-BK/SM', name='Kuzco_Trinity_PD62014_BK_SM_R2025', manufacturer='Kuzco Lighting', host='ceiling', dimensions=[14.25,14.25,48],
      source_rfa=str(REPO / 'output/trinity/Kuzco_Trinity_Low_PD62014_BKSM_Glow_R2025.rfa'),
      category_material={'Canopy and Suspension': 'Black Metal Finish', 'Smoke Glass Shade': 'Shade Glass Finish', 'Recessed Housing': 'Black Metal Finish', 'Warm Diffuser': 'Diffuser Finish'},
      materials=[black, mat('Shade Glass Finish', [116,121,127], .95,.64,.18,'Glass'), white],
      row_ids=['4773108898267012','516427135713156'],
      notes='14.25-inch diameter and 6.125-inch body height; 4.75-inch canopy. ASSUMPTION: fixed 48-inch installed drop. Smoke glass applies only to rows retaining the exact Lightology KZC1009570 variant. Internal socket and edge details are prior photo-derived inferences.',
      rfa_search='Public manufacturer/dealer technical resources inspected; no exact current RFA located. Rebuilt from inspected native BK/SM source.',
      source_url='https://www.lightology.com/index.php?module=prod_detail&prod_id=1009570'),
 dict(key='KZC1009570_CH', group_key='KZC1009570', model='PD62014-BK/CH', name='Kuzco_Trinity_PD62014_BK_CH_R2025', manufacturer='Kuzco Lighting', host='ceiling', dimensions=[14.25,14.25,48],
      source_rfa=str(REPO / 'output/trinity/Kuzco_Trinity_Low_PD62014_BKSM_Glow_R2025.rfa'),
      category_material={'Canopy and Suspension': 'Black Metal Finish', 'Smoke Glass Shade': 'Shade Glass Finish', 'Recessed Housing': 'Black Metal Finish', 'Warm Diffuser': 'Diffuser Finish'},
      materials=[black, mat('Shade Glass Finish', [190,195,200], .96,.22,.72,'Glass'), white],
      row_ids=['8353463272013700'],
      notes='Exact chrome-glass PD62014-BK/CH follows the explicit 2026-10-01 Lightopia quote correction in this row, overriding its stale smoke Lightology identifier. Shared body geometry is 14.25-inch diameter by 6.125-inch height. ASSUMPTION: 48-inch installed drop and visualization approximation of the partially reflective chrome glass.',
      rfa_search='Public product resources inspected; native BK/SM reconstruction provides shared body geometry. Chrome appearance is a separate explicit variant.',
      source_url='https://www.lightology.com/index.php?module=prod_detail&prod_id=1009570'),
 dict(key='DP-WS-S1-AA04-30-10_TRIAC_120V-IP65', model='DP-WS-S1-AA04-30-10_TRIAC_120V-IP65', name='RBW_Dimple_S1_AA04_White_Interior_R2025', manufacturer='RBW', host='wall', dimensions=[5,5,3.3],
      source_rfa=str(ROOT / groups['DP-WS-S1-AA04-30-10_TRIAC_120V-IP65']['canonical_item'] / 'source/RBW_Dimple_manufacturer_download.rfa'),
      id_material={'3121':'Black Backplate Finish','3522':'Clear Glass Finish','9479':'White Interior Finish'},
      source_parameter_inches={'Diameter':5.0,'Depth':3.3},
      materials=[mat('Black Backplate Finish',[24,24,24],.25),glass,mat('White Interior Finish',[249,249,245],.20,0,.02,'Plastic')],
      notes='Rebuilt from manufacturer-published 2014 305-D-FM RFA after setting its Diameter and Depth to current 5 x 3.3-inch specification. Original 5.375-inch/orange-glass file was rejected as an exact match. Black anodized backplate, clear outer cast glass and white interior are explicit S1/AA04 finishes. Source is retained unchanged; curved internal glass detail remains derived from the older manufacturer model.',
      rfa_search='Anonymous manufacturer RFA downloaded and natively inspected; older dimensions/finish prevent release as an unchanged exact current download.',
      source_url='https://rbw.com/products/dimple-sconce/dimple-sconce'),
]
for job in jobs:
    group = groups[job.get('group_key',job['key'])]
    rows = [r for r in group['rows'] if not job.get('row_ids') or r['row_id'] in job['row_ids']]
    job['rows'] = rows
    job['out'] = str(ROOT / rows[0]['item_key'])
    folder = Path(job['out']) / 'source'
    texture = folder / 'textures'
    texture.mkdir(parents=True, exist_ok=True)
    for m in job['materials']:
        Image.new('RGB',(32,32),tuple(m['rgb'])).save(texture / (m['label'].replace(' ','_')+'.png'))
    (folder / 'build_family.py').write_text("# -*- coding: utf-8 -*-\nimport os, sys\nOUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\nsys.path.insert(0,os.path.join(os.path.dirname(OUT),'_tools'))\nfrom rebuild_from_source import run_one\nrun_one(__revit__.Application, %r)\n" % job['key'], encoding='utf-8')
(ROOT / 'REUSE_JOBS.json').write_text(json.dumps(jobs,indent=2),encoding='utf-8')
print('Prepared %d native rebuilds for %d rows' % (len(jobs),sum(len(j['rows']) for j in jobs)))
