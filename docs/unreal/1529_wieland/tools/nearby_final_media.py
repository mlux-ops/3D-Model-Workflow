"""Label final native panoramas and compare final renders with the earlier round2 captures."""
import json
from pathlib import Path
from PIL import Image, ImageDraw
import phase20r2_panorama_sheet as sheets
import phase20r2_compare_stills as compare

ROOT=Path(__file__).resolve().parent.parent
FINAL=ROOT/'review/phase20/final_extension'
EARLIER=ROOT/'review/phase20/round2'

def main():
    sheets.PANO=str(FINAL/'panorama')
    compare.R1=str(EARLIER/'stills');compare.R2=str(FINAL/'stills')
    changes={}
    for view in compare.VIEWS:changes[view]=compare.one(view+'_realtime')
    changes['D1_pathtraced']=compare.one('D1_pathtraced')
    for deck in ('D1','D1S'):
        sheets.main(deck)
        filename=deck+'_panorama_sheet_r2.png'
        labels=json.loads((FINAL/'panorama'/(deck+'_panorama_sheet_r2_labels.json')).read_text())
        if len(labels)!=27 or any(not x.get('frame') for x in labels):raise RuntimeError('Incomplete landmark labels '+deck)
        old=Image.open(EARLIER/'panorama'/filename).convert('RGB')
        new=Image.open(FINAL/'panorama'/filename).convert('RGB')
        width=2400
        old=old.resize((width,round(old.height*width/old.width)))
        new=new.resize((width,round(new.height*width/new.width)))
        result=Image.new('RGB',(width,old.height+new.height+70),'white')
        draw=ImageDraw.Draw(result)
        draw.text((12,8),'Earlier round2 capture - saved vegetation may differ',fill='black')
        result.paste(old,(0,30))
        draw.text((12,old.height+40),'Final model - earlier local detail plus four-block refinement',fill='black')
        result.paste(new,(0,old.height+70))
        result.save(FINAL/'panorama'/('compare_'+deck+'_r1_r2.jpg'),quality=90)
    (FINAL/'comparison_metrics.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')

if __name__=='__main__':main()
