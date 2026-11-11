"""Source-linked visual neutral A/B architecture comparison, three bathroom programs.

Owner-facing comparative study only; not a scored or owner-approved selection.
"""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
from html import escape
import ast

ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'scratch'/'r036_prepare_three_wet_baths.py').read_text(encoding='utf-8')
P=ast.literal_eval(src[src.index('P={')+2:src.index('\nR={',src.index('P={'))])
R=ast.literal_eval(src[src.index('R={')+2:src.index('\nINTRO=',src.index('R={'))])
OUT=ROOT/'deliverables'/'r036-3-wet-bath-comparison-UNSCORED'
OUT.mkdir(exist_ok=True,parents=True)
IMAGES={'pienza':'pienza','derossi':'derossi','luxe':'luxe',
        'riviera':'riviera','perimeter':'perimeter',
        'sapphire':'sapphire','emerald':'emerald','antique':'antique',
        'sandstone':'sandstone','purity':'purity'}
Q=lambda x:x.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
HEADER='''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>1529 Wieland R036 neutral bathroom alternatives</title><style>
@page{size:letter landscape;margin:.33in}*{box-sizing:border-box}
body{font-family:Arial,Helvetica,sans-serif;color:#25231f;font-size:9pt;line-height:1.28;margin:0}
.page{page-break-after:always;break-after:page}.page:last-child{page-break-after:auto;break-after:auto}
.eyebrow{font-size:8pt;color:#766650;letter-spacing:.085em;margin-bottom:3px}
h1{font-size:17pt;margin:0 0 4px}h2{font-size:11.5pt;margin:0 0 5px}
p{margin:3px 0 7px}.context{font-size:8.2pt;color:#61594f;margin-bottom:9px}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.option{border:1px solid #d8d0c2;padding:9px;border-radius:2px}
.tile{display:grid;grid-template-columns:82px 1fr;gap:9px;padding:6px 0;border-top:1px solid #e6dfd4}
.tile img{width:82px;height:67px;object-fit:cover;border:1px solid #ded8cf}
.tile .label{font-size:7.5pt;font-weight:bold;text-transform:uppercase;color:#655849}
.tile .name{font-size:8.7pt;font-weight:bold}.tile .spec{font-size:7.7pt;color:#625c50}
a{color:#245367;text-decoration:none}.price{font-size:12pt;font-weight:bold;margin:5px 0}
.idea{font-size:8pt;color:#59534b}.hold{font-size:8pt;background:#f5f1eb;border-left:3px solid #ad9579;padding:7px;margin-top:8px}
.foot{font-size:7.5pt;border-top:1px solid #d7cfc3;margin-top:8px;padding-top:5px;color:#655b50}
@media screen{body{background:#e7e5e0;padding:20px}.page{width:11in;min-height:8.5in;padding:.45in;margin:0 auto 25px;background:white}}
@media print{.page{min-height:0;margin:0;padding:0}}
</style></head><body>'''
def tile_cell(kind,key):
    p=P[key];img=ROOT/'deliverables'/'assets'/'tile_thumbs'/(IMAGES[key]+'.jpg')
    assert img.is_file() and img.stat().st_size>4000
    gate=p['level'] if kind=='LEVEL' else p['wall']
    return ('<div class="tile"><img src="../assets/tile_thumbs/'+escape(IMAGES[key])+'.jpg" alt="Exact maker product image for '+escape(p['sku'],quote=True)+'">'
            '<div><div class="label">'+kind+'</div><div class="name"><a href="'+escape(p['url'],quote=True)+'">'+escape(p['name'])+'</a></div>'
            '<div class="spec">'+escape(p['size'])+' / '+escape(p['finish'])+' / SKU '+escape(p['sku'])+'</div>'
            '<div class="spec">'+escape(gate)+'; '+escape(p['box'])+'</div>'
            '<div class="spec">$'+escape(p['rate'])+'/SF: '+escape(p['source'])+'</div></div></div>')
def option(r,c,letter):
    w,n,l=c['cases'][letter]
    qty=[Decimal(v) for v in c['qty']]
    vals=[qty[i]*Decimal(P[k]['rate']) for i,k in enumerate((w,n,l))]
    total=Q(sum(vals))
    out='<div class="option"><h2>Neutral candidate '+letter+'</h2>'
    out+=tile_cell('WET WALL',w)+tile_cell('NICHE MATERIAL — all faces combined',n)+tile_cell('LEVEL / conditional POINT PAN',l)
    out+='<p class="price">$'+str(total)+'/copy original gross material-rate screen</p>'
    out+='<p class="idea">'+escape(c['design'][letter])+'</p>'
    out+='</div>'
    return out
pages=[]
for rid,c in R.items():
    p='<section class="page"><div class="eyebrow">SHB STUDIO / 1529 WIELAND / 07 NOV 2026 / NEW R036 ARCHITECTURAL OPTIONS</div>'
    p+='<h1>'+rid+' — two independently reviewable tile schemes</h1>'
    p+='<p class="context">'+escape(c['program'])+' / Physical copies '+escape(c['instances'])+'.</p>'
    p+='<div class="compare">'+option(rid,c,'A')+option(rid,c,'B')+'</div>'
    p+='<div class="hold"><b>UNRELEASED technical and owner holds:</b> '+escape(c['pool'])+'. '+escape(c['holds'])+'</div>'
    p+='<div class="foot">UNSCORED R036 DESIGN COMPARISON, not accepted, approved, purchased or installation-cleared. Images are original maker/retailer digital product depictions, NOT actual lot samples or mockups. Exact Floor & Decor selected-store prices are GA/IA/AZ public retail, NOT Chicago matching lot/landed costs. Historic gross includes 15% waste ONCE; owner room budgets FILL IN. Floor DCOF >=0.42 and separate Shower Floor use do not certify installer-cut four-plane POINT PAN. Existing tub-only branches have NO tiled PAN; hypothetical WALK-IN pans have independent NULL SF/cost. Old Town OT01 dry powder and OT04 wet green glossy wall are separate units in SAME 405 W Armitage development, not actual selected tile identifications; OT05 bath photo unverified.</div></section>'
    pages.append(p)
    (OUT/(rid+'_A_B_UNSCORED.html')).write_text(HEADER+p+'</body></html>',encoding='utf-8')
combined=OUT/'R036_THREE_WET_BATHS_SIDE_BY_SIDE_UNSCORED.html'
combined.write_text(HEADER+''.join(pages)+'</body></html>',encoding='utf-8')
assert len(pages)==3
print('PASS 3 independent original-maker-image R036 uns cored neutral design sheets / 6 candidates',combined)
