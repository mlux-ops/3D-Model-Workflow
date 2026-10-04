"""Record the actually inspected native preview findings without granting design approval."""
import datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
observations={
 'lg_wm4000hba':'Black Steel body, left detergent drawer/service panel, closed dark round door and right display are visible. Control legends, glass optics and local molded profiles remain simplified.',
 'lg_dlgx4001b':'Black Steel dryer has the round dark door and right display without a washer detergent/service panel. Reversible door is depicted with the documented right hinge assumption.',
 'ge_gfw550ssnww':'Corrected preview shows a white cabinet, metallic vented UltraFresh door ring and detergent drawer; unsupported LG service hatch was removed. Control graphics and glass optics remain simplified.',
 'ge_gfd55gssnww':'White dryer body and dark round door are visible; detergent/service drawer is absent. Fixed published size is verified, while molded fascia details remain image-derived.',
 'miele_km3054_1g':'Five burners are asymmetric: large wok burner at left, four smaller burners to the right, one left knob and four right knobs. Grate cross sections and elevation are inferred; full-height approval is withheld.',
 'tradewind_i32363rc':'Underside view shows two baffle filters and controls/light in a stainless insert body. Collar extension and small filter/control details are inferred.',
 'summit_sdhwc98pnr':'Revised native view shows two zones, sixteen wire shelves, metallic shelf fronts, transparent door and vertical lower grille. Customer overlay and pull remain absent; exact interior spacing and optical appearance are inferred.',
 'miele_h7280bp':'Black full-height oven fascia and handle profile are visible. Shaded front details are dark; source model is a nested manufacturer assembly and exact render optics are not approved.',
 'miele_h7270bm':'Black compact oven fascia and handle profile are visible. Nested manufacturer materials and the published-depth discrepancy remain unresolved.',
 'miele_g5051scvi':'Closed integrated dishwasher body, top control edge and toe recess are visible. Customer overlay finish is not selected; native 805 mm height differs from the current 815 mm specification.',
 'miele_kwt6722is':'Tall wine-unit shelves and glazing are visible, but a conspicuous blue internal source component remains. This is a finish-review hold; the manufacturer model is not visually release-ready.',
 'miele_kwtus7172f':'Undercounter wine cabinet, slatted shelves and glazing are visible. Nested materials and native front projections remain subject to fit/finish review.',
 'miele_kfmc3858fd':'Closed black factory assembly with mounting hardware is visible. The shaded facade does not clearly show all French-door/freezer seams; customer panels and closed-front configuration require visual confirmation.',
 'thermador_t18iw905sp':'Tall wine-column exterior and long handle are visible, but the glass/interior reads opaque in the native source preview. Treat as an exterior proxy until glazing/interior finish is resolved.',
 'thermador_t42it100np':'After the category-filter correction, imported French doors, two freezer drawers and assembly edges are visible. Black imported shading and oversized full envelope remain fit/finish holds.',
 'thermador_t24ur905rp':'After the category-filter correction, the undercounter unit and glass-door outline are visible. Brown source panel and blue glazing are placeholder appearances; project finish is unapproved.',
 'thermador_mc30wp':'Compact oven, two control knobs and horizontal pull match the manufacturer type. Source depth is shorter than the published overall reference; do not accept the fit silently.',
 'thermador_podmc301w':'Stacked speed and full-size ovens with separate controls/pulls are visible. Native source has one warning and a larger full-depth envelope.',
 'thermador_pcg486wd':'Six burners and the central griddle are visible. Source dimensions differ from the current cut sheet; grates/controls are manufacturer model geometry rather than accepted fabrication dimensions.',
 'thermador_prd48wisgu':'Six gas burners plus the far-right induction surface and three lower compartments agree with the current manufacturer sheet. Native overall height/depth still exceed the specified appliance reference.',
 'thermador_wd30w':'Single warming-drawer front and horizontal pull are visible. This is not the Zephyr hood described in the conflicting row; customer panel/handle configuration remains an assumption.'
}
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
records=[]
for slug,observation in observations.items():
    p=ROOT/slug/'validation.json'
    r=json.loads(p.read_text(encoding='utf-8'))
    images=[]
    for path in r['previews']:
        image=Path(path)
        images.append({'path':str(image.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(image.read_bytes()).hexdigest()})
    review={'reviewed_utc':stamp,'reviewer':'worker-1','method':'Direct visual inspection of native images and manufacturer reference imagery; manufacturer batch contact sheets used for overview.',
            'images':images,'observation':observation,'design_or_photographic_approval':False}
    r['visual_review']=review
    r['all_acceptance_gates_pass']=False
    p.write_text(json.dumps(r,indent=2),encoding='utf-8')
    records.append({'slug':slug,**review})
(ROOT/'visual_review.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Recorded direct native preview findings for %d models.'%len(records))
