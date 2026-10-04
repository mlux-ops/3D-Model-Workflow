"""Create source-family validation targets without deriving them from RFA bounds."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
# Width, depth, height. Published nominal product dimensions, not a promise that the
# downloaded family includes the same accessory/panel configuration.
DATA=[
 ('miele_h7280bp','Miele','H 7280 BP',[757,626,727],'Published body dimensions; native handle projection must be reported separately.'),
 ('miele_h7270bm','Miele','H 7270 BM',[757,573,479],'Current product-sheet page 2 explicitly states 757 W x 479 H x 573 D mm. Native projections are measured separately.'),
 ('miele_g5051scvi','Miele','G 5051 SCVi ADA',[598,550,815],'Current product sheet states 598 W x 815 H x 550 D mm. The downloaded ADA model is 805 mm high; this difference is not accepted silently.'),
 ('miele_kwt6722is','Miele','KWT 6722 iS',[557,553,1770],'Appliance body dimensions; installation flanges/projections may enlarge native envelope.'),
 ('miele_kwtus7172f','Miele','KWTUS 7172 F',[597,563,859],'Appliance body dimensions; installed door projections are reported separately.'),
 ('miele_kfmc3858fd','Miele','KFMC 3858 FD',[1048,608,2125],'Appliance body; 1067 mm installation width is not appliance body width.'),
 ('thermador_t18iw905sp','Thermador','T18IW905SP',[450.85,609.6,2127.25],'17 3/4 x 24 x 83 3/4 in; foot setting and handle/panel inclusion need comparison.'),
 ('thermador_t42it100np','Thermador','T42IT100NP',[1048,608,2123],'Published metric appliance dimensions, excluding customer panels.'),
 ('thermador_t24ur905rp','Thermador','T24UR905RP',[606.425,600.075,873.125],'23 7/8 x 23 5/8 x 34 3/8 in; source handle projection differs from appliance depth.'),
 ('thermador_mc30wp','Thermador','MC30WP',[755.65,568.325,498.475],'29 3/4 x 22 3/8 x 19 5/8 in; verify cut-sheet depth convention.'),
 ('thermador_podmc301w','Thermador','PODMC301W',[755.65,622.3,1244.6],'29 3/4 x 24 1/2 x 49 in appliance body; handle projection additional.'),
 ('thermador_pcg486wd','Thermador','PCG486WD',[1217.6125,655.6375,206.375],'47 15/16 x 25 13/16 x 8 1/8 in published appliance dimensions; native grate/knob configuration is compared explicitly.'),
 ('thermador_prd48wisgu','Thermador','PRD48WISGU',[1217.6125,708.025,908.05],'47 15/16 x 27 7/8 x 35 3/4 in minimum height; adjustable to 36 3/4 in. Current 9/26 cut sheet.'),
 ('thermador_wd30w','Thermador','WD30W',[755.65,622.3,239.7125],'29 3/4 x 24 1/2 x 9 7/16 in with 3/4-inch customer panel; handle projection additional.')
]
models=[]
for slug,brand,model,target,basis in DATA:
    models.append(dict(slug=slug,brand=brand,model=model,target_xyz_mm=target,dimension_basis=basis))
(ROOT/'downloaded_models.json').write_text(json.dumps(models,indent=2),encoding='utf-8')
print('Prepared %d downloaded-family targets.'%len(models))
