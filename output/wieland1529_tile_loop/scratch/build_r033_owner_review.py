from pathlib import Path
from html import escape
import re
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables'/'r033-13-owner-review-PROVISIONAL'
OUT.mkdir(parents=True,exist_ok=True)
def T(n,size,price,url,gate): return (n,size,price,url,gate)
U = {
 'bone':'https://www.elmsurfaces.com/product/cortar-bone',
 'clay':'https://www.elmsurfaces.com/product/cortar-clay',
 'charcoal':'https://www.elmsurfaces.com/product/cortar-charcoal',
 'sapphire':'https://www.elmsurfaces.com/product/sapphire-tones',
 'copper':'https://www.elmsurfaces.com/product/copper-tones',
 'sandstone':'https://www.elmsurfaces.com/product/sandstone-tones',
 'earth':'https://www.elmsurfaces.com/product/earth-lines-vera-forma',
 'indigo':'https://www.elmsurfaces.com/product/indigo-edge-vera-forma',
 'haze':'https://www.elmsurfaces.com/product/haze-camel',
 'luxe':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html',
 'riviera':'https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html',
 'perimeter':'https://www.flooranddecor.com/porcelain-tile/perimeter-gray-matte-porcelain-tile-101239218.html',
 'purity':'https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html',
 'antique':'https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html'}
I={
 'bone':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/67a65cdcd1f746f987b20f0a_cortar-bone.jpg',
 'clay':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/6658985c9e1b3e8a3f7c7c26_CUIT_CLAY_60X60_P48_%2072PP.jpg',
 'charcoal':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/67a65dfc47bc7a0bcc14c56b_Cortar%20Charcoal%20INSTALL%201.png',
 'sapphire':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/69a9eb9aeb2555e9a41bf4cd_sapphire.png',
 'copper':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/69a9eb9b6023e655882a059e_copper.png',
 'sandstone':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/69a9eb9a0f3540cc7a6ca13d_sandstone-copper.png',
 'earth':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/6a79185711b5a04473ec0c84_earth-lines-glossy-pressed.webp',
 'indigo':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/6a791995962c0290fc88e787_edge_collection_901258_901257_901256_90125.webp',
 'haze':'https://cdn.prod.website-files.com/6508c8490fee3dfe75080d5e/691fa3ed5568333a534ef0fc_0005_Amb07_CAMEL.jpg',
 'luxe':'https://i8.amplience.net/i/flooranddecor/101317949_luxe-sand-matte-porcelain-tile_display?fmt=auto&qlt=85&w=551&sm=aspect&aspect=1:1',
 'riviera':'https://i8.amplience.net/i/flooranddecor/101487775_riviera-oat-matte-porcelain-tile_display?fmt=auto&qlt=85&w=551&sm=aspect&aspect=1:1',
 'perimeter':'https://i8.amplience.net/i/flooranddecor/101239218_perimeter-gray-matte-porcelain-tile_display?fmt=auto&qlt=85&w=551&sm=aspect&aspect=1:1',
 'purity':'https://i8.amplience.net/i/flooranddecor/100507722_la-belle-purity-ceramic-polished-tile_display?fmt=auto&qlt=85&w=551&sm=aspect&aspect=1:1',
 'antique':'https://i8.amplience.net/i/flooranddecor/100507706_la-belle-antique-blue-ceramic-polished-tile_display?fmt=auto&qlt=85&w=551&sm=aspect&aspect=1:1',
}
IMG_BY_URL={U[k]:v for k,v in I.items()}
LOCAL_IMAGE_KEY={U[k]:k for k in I}
ASSET_DIR=ROOT/'deliverables'/'assets'/'tile_thumbs'
wall=lambda n,u,price: T(n,'2×20 wet wall',price,U[u],'Maker Wet Areas/Walls YES')
luxe=T('F&D Luxe Sand Matte 101317949','24×24, 8 mm rectified','$3.49/SF GA public',U['luxe'],'wet DCOF ≥0.42, Bathroom + Shower Floor YES')
riviera=T('F&D Riviera Oat Matte 101487775','24×48, 8 mm rectified','$3.99/SF GA public',U['riviera'],'wet DCOF ≥0.42, Bathroom + Shower Floor YES')
perimeter=T('F&D Perimeter Gray Matte 101239218','24×48 nominal, 9 mm rectified','$3.99/SF GA public',U['perimeter'],'Shower Walls/Floor + Bath Floor YES; wet DCOF ≥0.42; actual calibrated size unknown')
bone=T('Elm Cortar Bone FLAT Soft','24×48, 9 mm','$8.14/SF same-job',U['bone'],'Individual maker Wet Areas WALL only; not Reed/Ribbed or ceiling')
clay=T('Elm Cortar Clay FLAT Soft','24×48, 9 mm','$8.14/SF same-job',U['clay'],'Individual maker Wet Areas WALL only; not Reed/Ribbed or ceiling')
charcoal=T('Elm Cortar Charcoal FLAT Soft','24×48, 9 mm','$8.14/SF same-job',U['charcoal'],'Individual maker Wet Areas WALL only; not relief')
sapphire=wall('Elm Tones Sapphire Glossy','sapphire','$6.95/SF same-job')
copper=wall('Elm Tones Copper Glossy','copper','$6.95/SF same-job')
sandstone=wall('Elm Tones Sandstone Glossy','sandstone','$6.95/SF same-job')
purity=T('F&D La Belle Purity 100507722','3×12 glossy ceramic','$5.56/SF GA public',U['purity'],'Exact Shower Walls YES, Shower Floor NO; niche material only')
antique=T('F&D La Belle Antique Blue 100507706','3×12 glossy ceramic','$5.56/SF GA public',U['antique'],'Exact Shower Walls YES, Shower Floor NO')
earth=T('Elm Vera Forma Earth Lines Glossy','2×10 relief','$8.20/SF same-job',U['earth'],'DRY vanity wall; wall finish, not wet floor')
indigo=T('Elm Vera Forma Indigo Edge Glossy','6×6 relief','$8.20/SF same-job',U['indigo'],'DRY vanity wall only')
haze=T('Elm Haze Camel/Wheat matte blend','1.6×5','$11.93/SF same-job',U['haze'],'DRY vanity wall; proposed 70/30 split, not owner accepted')
R=[]
def add(id,title,status,score,plumbing,surfaces,cost,alts,holds,market='OT04 photographs green gloss wet shower tile in #4S; OT01 only dry powder layering.'):
  R.append(dict(id=id,title=title,status=status,score=score,plumbing=plumbing,surfaces=surfaces,cost=cost,alts=alts,holds=holds,market=market))
add('PH-PRIMARY','Penthouse Primary','ROOM BLOCKED — ceiling technical', 'A 3.840','Brizo BNX 48-in solid LINEAR + independent BR73480 rough; Duravit tub; no niche',
 [('Wet WALL',bone),('LEVEL + BNX LINEAR PAN',luxe),('PH-WC inherited LEVEL',luxe)],
 '$1,637.26/copy historic-gross tile-only rate; $3,274.53 for two before actual cartons. 15% waste once.',
 'B: Perimeter Gray 101239218 24×48 throughout WALL/LEVEL/PAN, $3.99/SF GA public; B scored 3.450.',
 'Scheduled SHOWER CEILING tile NOT independently maker/overhead qualified; no ceiling tile selected. Native cut/drain, Chicago lot/ETA, landed and owner budget FILL IN. No entire-room champion.')
add('PH-BATH2','Penthouse Bath 2','PROVISIONAL CHAMPION','A 3.880','Duravit tub; Hansgrohe Matte White; no tiled PAN',
 [('Tub WALL',sapphire),('Niche faces',sandstone),('Bath LEVEL',luxe)],
 'A $789.22/copy gross material-rate, $839.87/copy separate carton screen; two copies, 15% already included.',
 'B: Copper Tones glossy WALL + La Belle Purity niche + Luxe Sand LEVEL; $784.12/copy gross screen.',
 'Exact niche return/sill waterproof detail, tub flange, measured floor/wall cuts, Chicago lot/landed and owner tile budget remain OPEN.')
add('PH-BATH3','Penthouse Bath 3','PROVISIONAL CHAMPION','A 3.780','Hansgrohe Chrome; Delta DT062412 Chrome POINT drain WALK-IN only; tub/walk-in and basin UNSELECTED',
 [('Wet WALL',sapphire),('Conditional niche faces',sandstone),('Bath LEVEL',luxe),('WALK-IN POINT PAN only',luxe)],
 'TUB branch $799.37/copy rate-only historical gross. WALK-IN extra PAN quantity & cost NULL; original 15% once.',
 'B: Copper Tones wall + La Belle Purity niche + Perimeter Gray LEVEL/optional POINT PAN, scored 3.600.',
 'OWNER must choose TUB vs WALK-IN and basin. If TUB: tiled PAN N/A; if WALK-IN: independently measured POINT PAN, sill/trim, Delta rough. Chicago lot/landed and tile budget FILL IN.')
add('PH-BATH4','Penthouse Bath 4','PROVISIONAL CHAMPION','B 3.550','Owner-selected WALK-IN; Brizo BNX BT062415-BNX 4-in square POINT; no tub/ceiling',
 [('Wet WALL',perimeter),('Niche back/returns/top/sill',purity),('LEVEL + BNX POINT PAN',luxe)],
 '$616.01/copy original-gross rate-only screen, $1,232.02/two; no landed freight/tax/labor; 15% once.',
 'A: Cortar Bone FLAT WALL + Tones Sandstone niche + Riviera Oat LEVEL/POINT PAN; COST seat 2.8 FAIL (A weighted 3.570).',
 'W3 niche opening/positive-sill fall/membrane/trim hold, 35 vs 27 SF disputed, point slope/3-in cut/BNX rough, Chicago lots, budget FILL IN, final owner approval.')
add('PH-POWDER','Penthouse Powder','PROVISIONAL CHAMPION — defended incumbent','R032 A 3.860','Brizo Luxe Gold; dry vanity WALL only; wood floor retained',
 [('Dry vanity WALL',earth)],
 'Area-rate $368.18/copy; illustrative carton $408.03/copy, from R030 source. No separate tiled floor.',
 'A Elm Earth Lines and B La Belle Purity each scored 3.860 in current blind R032; B does not exceed accepted incumbent by +0.25; retain existing Earth Lines.',
 'Mirror/trim/grout setout, Chicago supply, owner tile budget FILL IN; incumbent +0.25 rule only when real board compares.')
add('PH-WC','Penthouse WC','BLOCKED — scored inherited LEVEL conditional','R033 A 4.100 (B 3.600)','Dry WC floor MUST match PH-PRIMARY exact LEVEL SKU/lot; no tiled walls, niche, PAN, ceiling or WC drain',
 [('Inherited floor / no separate order',luxe)],
 'Independent WC material purchase 0 SF / $0; parent LEVEL + LINEAR PAN + WC original gross includes 15% waste ONCE.',
 'R033 four specialist seats A 4.3/4.4/3.8/3.8 weighted 4.100; B Perimeter Gray 101239218 3.600. A is only conditional parent-matching preference; no genuine accepted standalone WC incumbent.',
 'PH-PRIMARY scheduled wet shower ceiling remains unqualified, so NO committed parent or WC champion. PH-WC geometry room IDs 313A/B disagree with R033 candidate 304A/B; verify identity/threshold/cuts, Chicago lot, owner budget FILL IN.')
add('TX-PRIMARY','Triplex Primary','ROOM BLOCKED — ceiling technical','A 3.810','Brizo BNX 48-in solid LINEAR plus independent rough per shower; no niche',
 [('Wet WALL',clay),('LEVEL + BNX LINEAR PAN',riviera),('TX-WC inherited LEVEL',riviera)],
 '$1,557.26/copy original-gross rate screen; two copies, original 15% once; carton/live supply unverified.',
 'B Clay WALL with bounded Tones Copper feature + Perimeter Gray LEVEL/PAN; B COST seat 2.8 FAIL, weighted 3.360.',
 'Shower tiled CEILING unselected/not maker overhead qualified. Actual linear channel cuts, field layout, Chicago lot/ETA, landed and owner budget FILL IN.')
add('TX-BATH2','Triplex Bath 2','PROVISIONAL CHAMPION','B 3.850','Hansgrohe Chrome; Duravit tub; basin OWNER UNSELECTED; PAN N/A',
 [('Wet tub WALL',sapphire),('Niche faces',purity),('Bath LEVEL',luxe)],
 'B $845.46/copy gross rate-only/$888.52 carton screen; two copies, 15% waste once.',
 'A Copper Tones + Sandstone niche + Luxe Sand LEVEL: $857.45/copy gross rate-only; A scored 3.630.',
 'Tub flange and trim, NICHE sill/profile, native cuts, basin unselected, Chicago lot/landed and owner budget FILL IN.')
add('TX-BATH3','Triplex Bath 3','PROVISIONAL CHAMPION','B 3.830','Brizo BNX 4-in square POINT only if owner chooses WALK-IN; TUB/WALK-IN UNSELECTED',
 [('Wet WALL',antique),('Niche faces',purity),('Bath LEVEL',luxe),('WALK-IN-only POINT PAN',luxe)],
 'B $685.92/copy gross rate-only excluding PAN, $701.56 carton; WALK-IN PAN SF and price NULL.',
 'A Copper Tones + Sandstone niche + Luxe Sand LEVEL/PAN scored equally 3.830, but costs $820.32/copy gross; B selected by material-cost tie-break.',
 'OWNER tub-vs-walk-in OPEN. Tub PAN N/A, walk-in BNX POINT actual pan cuts/scope, niche/trim, Chicago lots/landed and owner tile budget FILL IN.')
add('TX-BATH4','Triplex Bath 4','PROVISIONAL CHAMPION','B 3.650','Duravit tub, Hansgrohe Matte White, no tiled PAN',
 [('Wet tub WALL',perimeter),('Niche faces',purity),('Bath LEVEL',riviera)],
 'B $583.04/copy gross rate screen/$611.21 carton. Historical gross 15% once.',
 'A Cortar Charcoal FLAT + Sandstone niche + Luxe Sand LEVEL scored 3.590 but COST 2.8 fails specialist minimum.',
 'Maker Cortar FLAT only. Verify NICHE sill/trim, Duravit flange, 24×48 field cuts, Chicago lot/landed and owner tile budget FILL IN.')
add('TX-POWDER','Triplex Powder','PROVISIONAL CHAMPION — defended incumbent','R032 A 3.640','Hansgrohe faucet actual visible finish unconfirmed; DRY vanity WALL; wood floor',
 [('Proposed option A dry vanity WALL',haze)],
 'A $379.37/copy gross rate and $439.50/copy separate carton screen (70/30 proposed), no tiled LEVEL.',
 'B La Belle Purity $176.81/copy rate screen scored 3.730 vs A Haze 3.640; +0.090 is below authentic +0.25 incumbent rule. Retain Elm Haze.',
 'Owner/fixture actual visible metal finish UNKNOWN, mirror/edge setout, Chicago matching lot, budget FILL IN.')
add('TX-POWDER2','Triplex Powder 2','PROVISIONAL CHAMPION — defended incumbent','R032 A 3.780','Hansgrohe 73072341, source-verified 341 Brushed Black Chrome, structured finish null; basin UNSELECTED; wood floor',
 [('Dry vanity WALL',indigo)],
 'A $332.10/copy gross tile-only rate, $361.13/copy carton. No separate tile floor.',
 'B F&D La Belle Antique Blue $225.18/copy screen scored 3.860 vs incumbent Indigo 3.780; delta +0.080 below +0.25 displacement rule, retain incumbent.',
 'Basin UNSELECTED; verify 341 trim/order and faucet reach, dry-wall edge/mirror setout, Chicago lot/landed and owner tile budget FILL IN.')
add('TX-WC','Triplex WC','BLOCKED — scored inherited LEVEL conditional','R033 A 3.860 (B 3.560)','Dry WC floor MUST inherit exact TX-PRIMARY LEVEL SKU/lot; no tiled walls, niche, PAN, ceiling or WC drain',
 [('Inherited floor / no separate order',riviera)],
 'Independent WC material purchase 0 SF / $0; parent LEVEL + LINEAR PAN + WC original gross counts 15% waste ONCE.',
 'R033 specialist seats A 4.3/4.0/3.4/3.6 weighted 3.860; B Perimeter Gray 101239218 3.560. No independent WC tile decision/accepted incumbent.',
 'TX-PRIMARY scheduled tiled wet shower ceiling remains unqualified; WC not accepted. WC geometry 203A/B conflicts candidate 202A/B and 203A is unplaced; verify thresholds/cuts, Chicago lot and owner budget FILL IN.')
assert len(R)==13 and len(set(x['id'] for x in R))==13
def link(p):
  return '<a target="_blank" rel="noopener" href="'+escape(p[3],quote=True)+'">'+escape(p[0])+'</a>'
def surface_table(r):
  return '<table><thead><tr><th>Surface</th><th>Exact selected / proposed tile</th><th>Published use / cost</th></tr></thead><tbody>'+''.join('<tr><td>'+escape(name)+'</td><td>'+link(t)+'<small>'+escape(t[1])+'</small></td><td>'+escape(t[2])+'<small>'+escape(t[4])+'</small></td></tr>' for name,t in r['surfaces'])+'</tbody></table>'
def source_tile_strip(r):
 seen=set()
 parts=[]
 for surface,t in r['surfaces']:
  key=LOCAL_IMAGE_KEY.get(t[3])
  if not key or key in seen:continue
  seen.add(key)
  assert (ASSET_DIR/(key+'.jpg')).is_file(),(r['id'],key,'missing product image')
  parts.append('<div class="tile-thumb"><img src="../assets/tile_thumbs/'+escape(key)+'.jpg" alt="Vendor product illustration '+escape(t[0],quote=True)+'"><span>'+escape(t[0])+'</span></div>')
  if len(parts)>=4:break
 return '<div class="tile-strip">'+''.join(parts)+'</div><p class="image-caveat">Maker/retailer illustrations only; verify exact size/finish/lot against project sample, not an approved physical mockup.</p>'
HEAD='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1529 Wieland owner tile review</title><style>@page{size:letter;margin:.45in}*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;color:#211f1b;font-size:10.5pt;line-height:1.32}main{max-width:920px;margin:auto}.sheet{page-break-after:always;break-after:page;page-break-inside:avoid;min-height:9.4in;padding:.05in .08in}.sheet:last-child{page-break-after:auto;break-after:auto}.eyebrow{font-size:8pt;letter-spacing:.09em;text-transform:uppercase;color:#665d4d;margin-bottom:6px}h1{font-size:19pt;line-height:1.1;margin:0 0 4px}h2{font-size:10pt;margin:11px 0 4px;text-transform:uppercase;letter-spacing:.06em;color:#6a593f}.sub{margin:0 0 10px;font-size:9pt;color:#6a625a}table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:9pt}th,td{padding:6px 7px;vertical-align:top;border-bottom:1px solid #e4e0d9;word-break:normal;overflow-wrap:break-word}th{text-align:left;background:#f4f1ec;font-size:8pt}th:nth-child(1){width:18%}th:nth-child(2){width:41%}th:nth-child(3){width:41%}small{display:block;color:#69625a;font-size:7.8pt;margin-top:2px}p{margin:4px 0 8px}a{color:#285264;text-decoration:none}footer{font-size:8pt;color:#655d52;border-top:1px solid #c9c2b8;padding-top:6px;margin-top:10px}.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}.status{display:inline-block;font-size:8pt;background:#eee9df;padding:4px 8px;border-radius:3px;font-weight:bold;margin:5px 0 10px}.hold{color:#734a28}.market{background:#f7f5f1;padding:7px 9px;border-left:3px solid #b6a485} @media screen{body{background:#e9e6df;padding:18px}.sheet{background:white;max-width:8.5in;min-height:11in;margin:0 auto 20px;padding:.5in;box-shadow:0 3px 13px #aaa}} @media print{.sheet{margin:0;padding:0;min-height:0}a{text-decoration:none}}</style></head><body><main>'''
HEAD=HEAD.replace('</style>','''.tile-strip{display:flex;gap:8px;align-items:flex-start;margin:6px 0 2px}.tile-thumb{width:100px;display:flex;flex-direction:column;gap:3px}.tile-thumb img{height:70px;width:100px;object-fit:cover;border:1px solid #dedbd4}.tile-thumb span{font-size:7.3pt;color:#635c52}.image-caveat{font-size:7pt;color:#756c60;margin:2px 0 4px}</style>''')
def sheet(r):
 id=escape(r['id']); s='<section class="sheet" id="'+id+'"><div class="eyebrow">SHB STUDIO | 1529 WIELAND | 07 NOV 2026 | OWNER TILE REVIEW</div><h1>'+id+' — '+escape(r['title'])+'</h1><span class="status">'+escape(r['status'])+'</span><p class="sub">Board: '+escape(r['score'])+' • Two physical copies • No owner approval or procurement release</p>'
 s+='<h2>Proposed tile by actual surface</h2>'+surface_table(r)+source_tile_strip(r)
 s+='<h2>Selected plumbing / actual room program</h2><p>'+escape(r['plumbing'])+'</p>'
 s+='<div class="two"><div><h2>Material-only cost basis</h2><p>'+escape(r['cost'])+'</p></div><div><h2>Alternative / choice</h2><p>'+escape(r['alts'])+'</p></div></div>'
 s+='<h2>Attributable Old Town comparable</h2><p class="market">'+escape(r['market'])+' OT04 and OT01 are in the same 405 W Armitage development; neither image certifies a tile SKU, product DCOF or Chicago availability. Adjacent Lincoln Park/Gold Coast sales are secondary, not Old Town. <a href="https://www.movoto.com/chicago-il/405-w-armitage-ave-apt-4s-chicago-il-60614-461_12597470/">OT04 #4S gallery</a> · <a href="https://ap.rdcpix.com/6fa2fa9ed3fdbed3a5ac09ef8b339200l-m2050986137rd-w480_h360.webp">OT01 #2N dry-bath photograph</a> (actual image links; no inferred SKU or material).</p>'
 if 'POWDER' in r['id'] and (ROOT/'research/comps/img/OT01_405_W_Armitage_2N_realtor_bath_20261106.webp').is_file():
  s+='<figure style="margin:3px 0 6px"><img src="../../research/comps/img/OT01_405_W_Armitage_2N_realtor_bath_20261106.webp" alt="OT01 #2N attributable dry powder-style bathroom photograph, not proof of wet tile" style="display:block;width:200px;height:145px;object-fit:cover"><figcaption style="font-size:8pt;color:#6b6258">OT01 #2N, authentic dry-bath visual precedent only. Not this project’s selected tile.</figcaption></figure>'
 s+='<h2>Unresolved owner / technical / commercial holds</h2><p class="hold">'+escape(r['holds'])+'</p>'
 s+='<footer>Allowed vendors: Elm Surfaces, MSI Surfaces, Porcelanosa and Floor & Decor. Source links above open original maker/retailer pages. F&D prices are out-of-state retail, not Chicago matching-lot quotes. The historical 13-room/26-copy/27-row tile-only basis is $23,572.44 with original 15% waste counted once; room quantities remain provisional and owner budget is FILL IN. This is not a final approved selection.</footer></section>'
 return s
HTML=HEAD+''.join(sheet(r) for r in R)+'</main></body></html>'
(OUT/'R033_13_ROOM_OWNER_REVIEW_PAGES.html').write_text(HTML,encoding='utf-8')
for r in R:
 (OUT/(r['id']+'.html')).write_text(HEAD+sheet(r)+'</main></body></html>',encoding='utf-8')
base='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>1529 Wieland Tile Selection Review</title><style>body{font-family:Arial,Helvetica,sans-serif;background:#f5f3ee;color:#221e19;margin:0}main{max-width:1200px;margin:30px auto;padding:0 15px}h1{margin:0 0 7px}p.lede{color:#6d655a}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:15px}.room{background:white;border:1px solid #ddd7ca;padding:17px;border-radius:8px}.room h2{font-size:17px;margin:0}.status{display:inline-block;font-size:12px;background:#eee6d7;padding:4px 7px;margin:7px 0}.item{display:flex;align-items:flex-start;gap:11px;padding:9px 0;border-top:1px solid #e8e3d9;font-size:13px}.item a{color:#285264}.item small{display:block;color:#655b4e}.item .tilephoto{height:74px;width:74px;flex:0 0 74px;object-fit:cover;border-radius:4px;background:#ece9e4;border:1px solid #e5e0d7}.item .tilecopy{flex:1;min-width:0}.price{font-weight:bold;color:#34302c}.note{font-size:12px;color:#685b4a}.photo-note{display:block;font-size:10px;color:#82786c;margin-top:3px}a{color:#285264}footer{color:#666;font-size:12px;margin:28px 0}</style></head><body><main><h1>1529 Wieland — tile selections</h1><p class="lede">13 rooms, two physical copies each. As of 7 November 2026. Provisional selections are not owner-approved, final, purchased, or installation-cleared. Click any tile name to open the official vendor product page. Images are product/collection illustrations, not 1:1 approved samples or evidence of exact finish, lot or availability.</p><div class="grid">'''
for r in R:
 base+='<article class="room"><h2>'+escape(r['id'])+' — '+escape(r['title'])+'</h2><span class="status">'+escape(r['status'])+'</span><p class="note">'+escape(r['score'])+' | '+escape(r['plumbing'])+'</p>'
 for name,t in r['surfaces']:
  key=LOCAL_IMAGE_KEY.get(t[3])
  pic=('assets/tile_thumbs/'+key+'.jpg') if key and (ASSET_DIR/(key+'.jpg')).is_file() else None
  thumb=('<a href="'+escape(t[3],quote=True)+'" target="_blank" rel="noopener"><img class="tilephoto" src="'+escape(pic,quote=True)+'" loading="lazy" alt="Vendor source illustration: '+escape(t[0],quote=True)+'"></a>' if pic else '<span class="tilephoto" role="img" aria-label="Maker tile photograph not verified"></span>')
  base+='<div class="item">'+thumb+'<div class="tilecopy"><strong>'+escape(name)+'</strong> — '+link(t)+'<small>'+escape(t[1])+'; <span class="price">'+escape(t[2])+'</span>; '+escape(t[4])+'</small><span class="photo-note">Vendor page image; verify actual chosen finish/lot on sample. '+('' if pic else 'Image source not verified.')+'</span></div></div>'
 base+='<p class="note"><strong>Open:</strong> '+escape(r['holds'])+'</p><p><a href="r033-13-owner-review-PROVISIONAL/'+escape(r['id'])+'.html">Single-room owner packet</a></p></article>'
base+='</div><footer>Pricing: same-job Elm quote 2026-09-04 or selected F&D Kirkwood (Atlanta GA) public product pages, not Chicago matched-lot offers. Thumbnail imagery is linked to exact Floor & Decor SKU pages or relevant Elm maker product/collection pages, and does not certify selected physical module/lot. Elm Clay, Cortar and Haze collection/example photography can depict other variants and is not an approved project mockup. OT01 dry powder and OT04 #4S wet shower are attributable Old Town photo precedents; OT05 bathroom imagery remains unverified. No owner contact, samples, orders or purchases.</footer></main></body></html>'
(ROOT/'deliverables'/'TILE_SELECTIONS_REVIEW.html').write_text(base,encoding='utf-8')
print('Created '+str(len(R))+' individual R033 provisional single-room HTML packets, combined print HTML, and updated 13-card TILE_SELECTIONS_REVIEW.html')
assert base.count('<article class="room">')==13
assert base.count('<img class="tilephoto"')==sum(len(r['surfaces']) for r in R)
assert HTML.count('<section class="sheet"')==13
assert 'Daltile' not in base and 'Platform Surfaces' not in base
