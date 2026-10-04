"""Assemble source / native outline / native shaded review comparisons."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
groups=json.loads((ROOT/'GROUPS.json').read_text())['groups']
rows=[]
for g in groups+[dict(key='KZC1009570_CH',canonical_item='K1-1__8353463272013700')]:
    folder=ROOT/g['canonical_item'];vp=folder/'validation.json'
    if not vp.exists():continue
    v=json.loads(vp.read_text())
    if not v.get('technical_pass'):continue
    diagnostic=folder/'evidence'/'GeometryReview - 3D View - Geometry Oblique.png'
    native=list((folder/'evidence').glob('*_Isolated - 3D View - Native Oblique.png'))
    reference=folder/'source'/'reference_product.jpg'
    if g['key']=='KZC1009570_CH':reference=ROOT/'K1-2__4773108898267012/source/reference_product.jpg'
    replacements={'AMB-MB-56-EB-870-CC':'Ambit_current_cutsheet/page_01.png','ORION_TUBE_UNSPECIFIED':'Orion_Tube_current_spec/page_02.png','4BEMW_SWW5_90CRI_M6':'Juno_4BE_current_spec/page_01.png','SKL924074':'SkLO_Hold12_current_spec_review/page_01.png','QC4_J6':'QC4_manufacturer_spec_review/page_01.png','54654241-4PK':'Commercial_Electric_current_spec.png'}
    if g['key'] in replacements:reference=folder/'source'/replacements[g['key']]
    rows.append(dict(key=g['key'],model=v['model'],folder=str(folder),source=str(reference) if reference.exists() else None,outline=str(diagnostic) if diagnostic.exists() else None,native=str(max(native,key=lambda p:p.stat().st_mtime)) if native else None,rfa_sha256=hashlib.sha256(Path(v['rfa_path']).read_bytes()).hexdigest(),dims=v['measured_saved_dimensions_in']))
try:font=ImageFont.truetype('arial.ttf',22)
except OSError:font=ImageFont.load_default()
out=ROOT/'_review'/'final';out.mkdir(exist_ok=True)
for start in range(0,len(rows),4):
    page=Image.new('RGB',(1800,1840),'white');draw=ImageDraw.Draw(page)
    for i,row in enumerate(rows[start:start+4]):
        top=i*460
        draw.text((12,top+4),row['key']+'  |  '+row['model'][:95],font=font,fill='black')
        for col,field in enumerate(['source','outline','native']):
            value=row[field]
            if value:
                image=Image.open(value).convert('RGB')
                if field!='source':
                    box=ImageChops.difference(image,Image.new('RGB',image.size,'white')).point(lambda p:255 if p>18 else 0).getbbox()
                    if box:image=image.crop(box)
                image.thumbnail((570,373))
                page.paste(image,(col*600+(600-image.width)//2,top+39+(373-image.height)//2))
            elif field=='source':
                draw.multiline_text((20,top+150),'Specification retained in row source folder.\nSee NOTES.md for dimensions and evidence.\nNo paired product photograph.',font=font,fill='black',spacing=10)
            caption={'source':'SOURCE','outline':'SAVED RFA: OPAQUE OUTLINE','native':'SAVED RFA: SHADED'}[field]
            if field=='source' and row['key']=='KZC1009570_CH':caption='SMOKE VARIANT: SHAPE REFERENCE ONLY'
            if field=='source' and row['key']=='54654241-4PK':caption='CURRENT SPECIFICATION THUMBNAIL'
            draw.text((col*600+12,top+420),caption,font=font,fill='black')
        row['review_page']='final_%02d.jpg'%(start//4+1)
    page.save(out/('final_%02d.jpg'%(start//4+1)),quality=94)
(out/'manifest.json').write_text(json.dumps(rows,indent=2))
print('Prepared',len(rows),'families on',(len(rows)+3)//4,'review sheets')
