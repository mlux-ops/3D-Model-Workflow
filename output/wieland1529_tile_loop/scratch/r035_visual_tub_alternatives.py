"""Create visual, source-linked A/B comparison boards for three tub rooms.

Prepared design research ONLY; not scored, selected, purchased, or approved.
Print 3 landscape US Letter pages, one per room, preserving all historical rooms.
"""
from pathlib import Path
from html import escape
from decimal import Decimal, ROUND_HALF_UP
import ast

ROOT=Path(__file__).resolve().parents[1]
t=(ROOT/'scratch'/'r035_prepare_three_tub_room_board.py').read_text(encoding='utf-8')
maker=(ROOT/'scratch'/'r034_prepare_three_wet_bath_board.py').read_text(encoding='utf-8')
P=ast.literal_eval(maker[maker.index('P={')+2:maker.index('\nR={',maker.index('P={'))])
begin=t.index('\nR={')+len('\nR=')
R=ast.literal_eval(t[begin:t.index('\ndef mk_ref',begin)])
OUT=ROOT/'deliverables'/'r035-3-duravit-tub-comparison-PREPARED'
OUT.mkdir(parents=True,exist_ok=True)
Q=lambda x:x.quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
image_map={'sapphire':'sapphire','sandstone':'sandstone','copper':'copper',
           'antique':'antique','purity':'purity','riviera':'riviera',
           'perimeter':'perimeter','luxe24':'luxe','luxe48':'luxe'}
head='''<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>1529 Wieland R035 prepared tub-room design comparison</title>
<style>
@page{size:letter landscape;margin:.35in}
*{box-sizing:border-box}body{font-family:Arial,sans-serif;color:#29251e;font-size:9pt;line-height:1.28;margin:0}
.sheet{page-break-after:always;break-after:page}.sheet:last-child{page-break-after:auto;break-after:auto}
h1{font-size:20pt;letter-spacing:-.03em;margin:0 0 6px}h2{font-size:12pt;margin:0 0 6px}
.eyebrow{font-size:8pt;letter-spacing:.09em;color:#756957;margin-bottom:4px}
.leadin{font-size:9pt;color:#5e554b;margin:0 0 9px}.dual{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.option{border:1px solid #d9d0c3;padding:10px;min-height:380px}
.tile{display:flex;gap:8px;margin:7px 0;padding:5px 0;border-top:1px solid #e7e3da}
.tile img{width:85px;height:70px;object-fit:cover;background:#eee}
.tile-content{flex:1}.tile-content strong{display:block;font-size:8pt}.tile-content small{display:block;font-size:7.7pt;color:#615c53}
.cost{font-size:11pt;font-weight:bold;margin-top:10px;color:#56432d}.note{color:#6a6157;font-size:8pt}
.hold{padding:8px;background:#f3f0ea;font-size:8pt;border-left:3px solid #aa9272;margin-top:10px}
.foot{font-size:7.8pt;color:#685e52;border-top:1px solid #ddd4c8;padding-top:6px;margin-top:10px}
a{color:#244e5c;text-decoration:none}
@media screen{body{background:#e9e6df;padding:20px}.sheet{width:11in;min-height:8.5in;margin:0 auto 24px;background:white;padding:.45in}}
@media print{.sheet{margin:0;padding:0;min-height:0}}
</style></head><body>'''
def option(room,meta,letter):
 c=meta[letter]
 gw,gn,gl=map(Decimal,meta['gross'])
 cost=Q(gw*Decimal(P[c['w']]['price'])+gn*Decimal(P[c['n']]['price'])+gl*Decimal(P[c['l']]['price']))
 out='<section class="option"><h2>Neutral option '+letter+'</h2>'
 for name,k in [('WET TUB WALL','w'),('WET NICHE — ALL FACES','n'),('LEVEL FLOOR — NO SHOWER PAN','l')]:
  spec=P[c[k]]
  key=image_map[c[k]]
  assert (ROOT/'deliverables'/'assets'/'tile_thumbs'/(key+'.jpg')).is_file()
  out+='<div class="tile"><img src="../assets/tile_thumbs/'+key+'.jpg" alt="Maker product or family illustration">'
  out+='<div class="tile-content"><strong>'+name+'</strong><a href="'+escape(spec['url'],quote=True)+'">'+escape(spec['name'])+'</a>'
  out+='<small>'+escape(spec['size'])+'; '+escape(spec['thick'])+'; SKU '+escape(spec['sku'])+'</small>'
  out+='<small>'+escape(spec['use'])+'; '+escape('$'+spec['price']+'/SF')+'</small></div></div>'
 out+='<p class="note">'+escape(c['idea'])+'</p>'
 out+='<p class="cost">Historical source-gross material rate: $'+str(cost)+'/copy</p></section>'
 return out
pages=[]
for id,meta in R.items():
 p='<section class="sheet"><div class="eyebrow">SHB STUDIO | 1529 WIELAND | R035 NEW PRODUCT ALTERNATIVE STUDY | 07 NOV 2026</div>'
 p+='<h1>'+id+' — Duravit tub bathroom</h1><p class="leadin">'+escape(meta['plumbing'])+'</p>'
 p+='<div class="dual">'+option(id,meta,'A')+option(id,meta,'B')+'</div>'
 p+='<div class="hold"><strong>Physical / technical / owner holds:</strong> '+escape(meta['holds'])+'</div>'
 p+='<div class="foot">PREPARED DESIGN COMPARISON ONLY; NOT YET INDEPENDENTLY BOARDED, SELECTED OR OWNER APPROVED. Maker/retailer thumbnail is color/collection illustration, not certified selected size/lot or a physical sample; for Luxe Sand 24x48, displayed image may depict another size in the family. Distinct wet WALL permission, LEVEL wet DCOF >=0.42 and tub flange assembly remain separate. Prices: dated Sep 4 Elm same-job versus Nov 7 Floor & Decor Kirkwood Atlanta public; Chicago matching lots, ETA, tax/freight/labor and owner budgets FILL IN. Original 15% gross waste ONCE, niche all faces included as ONE pool, two copies. NO tiled PAN in these three Duravit TUB bathrooms. Old Town OT01 #2N dry powder and OT04 #4S wet green shower are units in same 405 W Armitage development, neither verifies a named product. OT05 bathroom imagery unverified.</div>'
 p+='</section>'
 pages.append(p)
 (OUT/(id+'_A_B_PREPARED.html')).write_text(head+p+'</body></html>',encoding='utf-8')
(OUT/'R035_THREE_TUB_ROOMS_SIDE_BY_SIDE_PREPARED.html').write_text(head+''.join(pages)+'</body></html>',encoding='utf-8')
assert len(pages)==3
print('PREPARED three independently source-linked two-option visual comparison sheets; NOT scored, selected or approved')
