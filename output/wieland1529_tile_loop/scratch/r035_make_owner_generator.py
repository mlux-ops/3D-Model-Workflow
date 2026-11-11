"""Create a round-specific owner packet generator from the tested R034 layout.

Only substitutions for authentically updated R035 room summaries and new TX4
wall SKU. R034 source remains unchanged for historical reproducibility.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'scratch'/'build_r034_owner_review.py'
dst=ROOT/'scratch'/'build_r035_owner_review.py'
assert not dst.exists()
t=src.read_text(encoding='utf-8')
t=t.replace('r034-13-owner-review-PROVISIONAL','r035-13-owner-review-PROVISIONAL')
t=t.replace('R034_13_ROOM_OWNER_REVIEW_PAGES','R035_13_ROOM_OWNER_REVIEW_PAGES')
t=t.replace('R034 provisional','R035 provisional').replace('individual R034','individual R035')
t=t.replace(" 'luxe':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html',",
            " 'luxe':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html',\n 'luxe48':'https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317865.html',")
t=t.replace("luxe=T('F&D Luxe Sand Matte 101317949'",
            "luxe48=T('F&D Luxe Sand Matte 101317865','24x48 wet tub WALL','$3.99/SF GA public',U['luxe48'],'Exact Shower Walls YES; own 24x48 SKU, distinct from floor 101317949')\nluxe=T('F&D Luxe Sand Matte 101317949'")
# The existing F&D 24x24 photo is retained ONLY as a same-family color image,
# never falsely asserted to show the exact 24x48 maker product or module.
t=t.replace("LOCAL_IMAGE_KEY={U[k]:k for k in I}",
            "LOCAL_IMAGE_KEY={U[k]:k for k in I}\nLOCAL_IMAGE_KEY[U['luxe48']]='luxe'  # related series image only, not exact 24x48 SKU illustration")
t=t.replace("key=LOCAL_IMAGE_KEY.get(t[3])\n  if not key or key in seen:continue",
            "key=LOCAL_IMAGE_KEY.get(t[3])\n  if not key or key in seen:continue")
t=t.replace("'<span>'+escape(t[0])+'</span></div>'",
            "'<span>'+escape(t[0])+(' (24x24 family photo, NOT exact 24x48)' if t[3]==U['luxe48'] else '')+'</span></div>'")
t=t.replace("'Vendor page image; verify actual chosen finish/lot on sample. '",
            "('Family-color image from 24x24 SKU101317949, NOT the 24x48 SKU101317865 module. ' if t[3]==U['luxe48'] else 'Vendor page image; verify actual chosen finish/lot on sample. ')")
old="""add('PH-BATH2','Penthouse Bath 2','PROVISIONAL CHAMPION','A 3.880','Duravit tub; Hansgrohe Matte White; no tiled PAN',
 [('Tub WALL',sapphire),('Niche faces',sandstone),('Bath LEVEL',luxe)],
 'A $789.22/copy gross material-rate, $839.87/copy separate carton screen; two copies, 15% already included.',
 'B: Copper Tones glossy WALL + La Belle Purity niche + Luxe Sand LEVEL; $784.12/copy gross screen.',
 'Exact niche return/sill waterproof detail, tub flange, measured floor/wall cuts, Chicago lot/landed and owner tile budget remain OPEN.')"""
new="""add('PH-BATH2','Penthouse Bath 2','PROVISIONAL CHAMPION — R035 defended','R035 incumbent A 3.670; prior R031 3.880','Duravit 59-in tub; Hansgrohe Matte White; no tiled PAN / shower point drain',
 [('Tub WALL',sapphire),('Niche faces',sandstone),('Bath LEVEL',luxe)],
 'A $789.23/copy per-line cent-sum gross material rate ($789.22 full-precision grand); $839.87/copy prior carton illustration. Two copies; 15% already included ONCE.',
 'R035 B La Belle Antique Blue 100507706 tub WALL + La Belle Purity 100507722 niche + Riviera Oat 101487775 LEVEL $679.54/copy scored 3.600. B lost to A 3.670; existing R031 remains.',
 'R035 product exact wet-wall/LEVEL DCOF gates pass; 59-in tub vs ~59.496-in assumed alcove, niche sill positive-fall waterproofing, flange, cuts, substrate, Chicago lot/landed and owner tile budget FILL IN remain OPEN.')"""
assert old in t;t=t.replace(old,new)
old="""add('TX-BATH2','Triplex Bath 2','PROVISIONAL CHAMPION','B 3.850','Hansgrohe Chrome; Duravit tub; basin OWNER UNSELECTED; PAN N/A',
 [('Wet tub WALL',sapphire),('Niche faces',purity),('Bath LEVEL',luxe)],
 'B $845.46/copy gross rate-only/$888.52 carton screen; two copies, 15% waste once.',
 'A Copper Tones + Sandstone niche + Luxe Sand LEVEL: $857.45/copy gross rate-only; A scored 3.630.',
 'Tub flange and trim, NICHE sill/profile, native cuts, basin unselected, Chicago lot/landed and owner budget FILL IN.')"""
new="""add('TX-BATH2','Triplex Bath 2','PROVISIONAL CHAMPION — R035 defended','R035 incumbent B 3.590; prior R031 3.850','Hansgrohe Chrome; selected Duravit 59-in tub; basin OWNER UNSELECTED; tiled PAN N/A',
 [('Wet tub WALL',sapphire),('Niche faces',purity),('Bath LEVEL',luxe)],
 'B $845.46/copy full-precision-to-cents gross rate-only ($845.45 displayed row-sum); $888.52 previous carton screen. Two copies; original 15% waste once.',
 'R035 A Elm Tones Copper 2x20 WALL + Sandstone niche + Riviera Oat 24x48 LEVEL: $879.30/copy scored 3.470 vs B 3.590, no replacement.',
 'Two conflicting drawing-width sources (~62.484-in W1, ~59.496-in tub opening) vs nominal 59-in Duravit; actual fit, flange, waterproof niche sill, edge cuts, basin UNSELECTED, Chicago lot/landed and owner budget FILL IN.')"""
assert old in t;t=t.replace(old,new)
old="""add('TX-BATH4','Triplex Bath 4','PROVISIONAL CHAMPION','B 3.650','Duravit tub, Hansgrohe Matte White, no tiled PAN',
 [('Wet tub WALL',perimeter),('Niche faces',purity),('Bath LEVEL',riviera)],
 'B $583.04/copy gross rate screen/$611.21 carton. Historical gross 15% once.',
 'A Cortar Charcoal FLAT + Sandstone niche + Luxe Sand LEVEL scored 3.590 but COST 2.8 fails specialist minimum.',
 'Maker Cortar FLAT only. Verify NICHE sill/trim, Duravit flange, 24×48 field cuts, Chicago lot/landed and owner tile budget FILL IN.')"""
new="""add('TX-BATH4','Triplex Bath 4','PROVISIONAL CHAMPION — R035 NEW TILE SCHEME','R035 new B 3.630; old R031 3.650','Duravit 59-in tub; Hansgrohe Matte White; tub waste preserved, no tiled PAN or point drain',
 [('Wet tub WALL',luxe48),('Niche faces',sandstone),('Bath LEVEL',luxe)],
 'New B $572.89/copy gross-rate ($1,145.78/two). Original 15% waste once. Two dedicated-carton packs ~$623.63 each vs pooled two-room lot ~$1,202.09 illustrative ONLY; Chicago landed UNKNOWN.',
 'R035 A former Perimeter Gray 24x48/Purity/Riviera Oat 24x48 $583.04/copy scored 3.350; B 3.630 yields +0.280 > +0.250 threshold. Wall/floor Luxe Sand are DISTINCT SKU101317865/101317949.',
 'Original tile takeoff 89.8 gross WALL + 8.63 combined NICHE + 44.3 LEVEL per copy. Tub flange/waste, wet niche sill waterproof, ~60-in assumed alcove/59-in tub, 24x48 edge cuts, local matching lots, freight/installed, signed budget FILL IN, owner approval OPEN.')"""
assert old in t;t=t.replace(old,new)
assert 'R034_13_ROOM_OWNER_REVIEW_PAGES' not in t
assert 'r034-13-owner-review-PROVISIONAL' not in t
assert 'luxe48' in t and 'R035 NEW TILE SCHEME' in t
dst.write_text(t,encoding='utf-8')
print('PASS new R035 generator created',len(t),'bytes; original R034 untouched')
