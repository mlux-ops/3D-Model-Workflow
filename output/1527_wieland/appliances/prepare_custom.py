"""Define traceable appliance construction inputs and portable uniform finish maps."""
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
COMMON_LIMITS=['Visualization geometry; no MEP connectors, operating mechanisms or fabrication tolerances.',
              'Overall dimensions are manufacturer dimensions. Undimensioned seams, controls, edge radii and optical properties are inferred from product imagery.',
              'Fixed product dimensions; editable finish parameters are the intended flex controls.']
MODELS=[
 {'slug':'lg_wm4000hba','brand':'LG','model':'WM4000HBA','kind':'washer','width':685.8,'height':990.6,'depth':768.35,'finish':'Black Steel',
  'spec_url':'https://media.us.lg.com/m/1c4e8c8e7a284ef2/original/WM4000H_A-LG-Builder-Spec-Sheet.pdf',
  'dimension_basis':'27 x 39 x 30 1/4 in, W x H x D; LG builder specification page 2.',
  'assumptions':['Black Steel selected by B suffix. Washer left hinge; closed-door visualization. Pedestal and stacking kit excluded.']},
 {'slug':'lg_dlgx4001b','brand':'LG','model':'DLGX4001B','kind':'dryer','width':685.8,'height':990.6,'depth':765.175,'finish':'Black Steel',
  'spec_url':'https://content.abt.com/documents/129668/SpecificationSheet-DLXX400X-1.pdf',
  'dimension_basis':'27 x 39 x 30 1/8 in, W x H x D; LG manufacturer specification, gas section.',
  'assumptions':['Black Steel selected by B suffix. Reversible dryer door depicted right-hinged; no pedestal.']},
 {'slug':'ge_gfw550ssnww','brand':'GE','model':'GFW550SSNWW','kind':'washer','width':711.2,'height':1009.65,'depth':812.8,'finish':'White',
  'spec_url':'https://www.geappliances.com/appliance/GE-ENERGY-STAR-4-8-cu-ft-Capacity-Smart-Front-Load-Washer-with-UltraFresh-Vent-System-with-OdorBlock-and-Sanitize-w-Oxi-GFW550SSNWW',
  'dimension_basis':'28 x 39 3/4 x 32 in, W x H x D; official GE product dimensions.',
  'assumptions':['White WW finish. Closed door shown left-hinged; GE permits reversal. Pedestal excluded.']},
 {'slug':'ge_gfd55gssnww','brand':'GE','model':'GFD55GSSNWW','kind':'dryer','width':711.2,'height':1009.65,'depth':812.8,'finish':'White',
  'spec_url':'https://www.geappliances.com/appliance/GE-ENERGY-STAR-7-8-cu-ft-Capacity-Smart-Front-Load-Gas-Dryer-with-Sanitize-Cycle-GFD55GSSNWW',
  'dimension_basis':'28 x 39 3/4 x 32 in, W x H x D; official GE product dimensions.',
  'assumptions':['Corrected gas dryer GFD55GSSNWW governs; obsolete electric-model row text is not the model authority. Reversible door depicted right-hinged.']},
 {'slug':'miele_km3054_1g','brand':'Miele','model':'KM 3054-1 G','kind':'cooktop','width':942.0,'height':53.0,'depth':526.0,'finish':'Black Glass / Stainless Controls',
  'spec_url':'https://media.miele.com/downloads/n-/us/FS_11766750_USE_US-en-US.pdf',
  'dimension_basis':'942 x 526 mm glass outline. 46 mm casing below + 7 mm glass above countertop = 53 mm casing height; installation drawing page 3.',
  'dimension_scope':'body','assumptions':['KM3054-1 replaces KM2355G per provided item correction. Wok burner is left-center, not centered.',
   'Grate height 35 mm above glass is inferred, not covered by the 53 mm casing dimension. Gas and electrical projections under the casing are omitted.'],
  'extra_limitations':['Full height including grate is not dimensioned in the recovered sheet. Only the defined casing-height gate can pass; overall-height acceptance remains limited.']},
 {'slug':'tradewind_i32363rc','brand':'Trade-Wind','model':'I32363RC','kind':'hood','width':873.125,'height':330.2,'depth':266.7,'finish':'Stainless Steel',
  'spec_url':'https://linqcdn.avbportal.com/documents/3512c644-ff49-413e-aaf5-5805aa9aad84.pdf',
  'dimension_basis':'34 3/8 x 13 x 10 1/2 in body W x H x D; I3236-model drawing page 2; 7-inch round collar for I32363RC.',
  'dimension_scope':'body','assumptions':['Specified Trade-Wind model governs conflicting Zephyr vendor text. Two filters and one LED light.',
   'Duct collar extension is inferred as 25.4 mm above the 13-inch body. Filter blade pitch and light/control recess details are image-derived.'],
  'extra_limitations':['Overall height with collar is reported separately; the manufacturer body-height dimension does not establish collar extension.']},
 {'slug':'summit_sdhwc98pnr','brand':'Summit','model':'SDHWC98PNR','kind':'wine','width':596.9,'height':1822.45,'depth':457.2,'finish':'Panel Ready / Black Cabinet',
  'spec_url':'https://www.summitappliance.com/catalog/model/SDHWC98PNR',
  'dimension_basis':'23.5 x 71.75 x 18 in, W x H x D, factory appliance envelope without optional customer panel.',
  'assumptions':['Panel-ready appliance represented before customer panel/pull installation; no cabinet finish has been selected.',
   'Two temperature zones and 16 shelves represented; exact shelf spacing, internal clearances and glass tint inferred.'],
  'extra_limitations':['Customer overlay panel and pull excluded; their thickness and projections would change installed envelope.']}
]
FINISHES={
 'Black Steel':([57,57,58],0.42,0), 'White':([235,235,232],0.4,0),
 'Stainless Steel':([166,166,164],0.6,0), 'Black Glass':([23,27,30],0.9,0),
 'Black Plastic':([27,28,30],0.2,0), 'Clear Glass':([126,150,152],0.95,0.68),
 'Bronze Rim':([152,132,122],0.65,0), 'Gray Interior':([84,88,89],0.3,0),
 'Indicator':([188,207,208],0.5,0), 'Panel Ready':([100,100,98],0.22,0)
}
for model in MODELS:
    model['limitations']=COMMON_LIMITS+model.get('extra_limitations',[])
    folder=ROOT/model['slug']/'source'
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'geometry_config.json').write_text(json.dumps(model,indent=2),encoding='utf-8')
    (folder/'build.py').write_text("# Run this absolute script path through the shared revit_run.py only.\nimport os,sys\nsection=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nsys.path.insert(0,section)\nfrom build_custom import build_one\nbuild_one(%r, __revit__.Application)\n"%model['slug'],encoding='utf-8')
    for name,(rgb,gloss,transparency) in FINISHES.items():
        Image.new('RGB',(32,32),tuple(rgb)).save(folder/(name.replace(' ','_')+'_diffuse.png'))
(ROOT/'custom_models.json').write_text(json.dumps(MODELS,indent=2),encoding='utf-8')
(ROOT/'finish_definitions.json').write_text(json.dumps(FINISHES,indent=2),encoding='utf-8')
print('Prepared %d model configurations and their source/build.py entrypoints.'%len(MODELS))
