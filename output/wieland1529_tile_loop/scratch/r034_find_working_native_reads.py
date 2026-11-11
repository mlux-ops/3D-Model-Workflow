"""Read previous Revit bridge request shapes only; no Revit operations executed."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
receipts=ROOT/'state'/'revit_receipts'
matches=[]
for p in receipts.glob('*.json'):
 try:d=json.loads(p.read_text(encoding='utf-8'))
 except Exception:continue
 op=d.get('request',{}).get('operation')
 if op not in ('parameters.query','view.inspect','elements.inspect','elements.query'):continue
 if d.get('status')!='completed':continue
 args=d.get('request',{}).get('arguments',{})
 if op=='elements.query' and args.get('category')!='OST_Rooms':continue
 result=d.get('result')
 keys=list(result) if isinstance(result,dict) else type(result).__name__
 matches.append((op,p.name,args,keys))
for op,name,args,keys in matches[-35:]:
 print(op,name,'ARGS',str(args)[:400],'RESULT_KEYS',str(keys)[:150])
print('PASS completed candidate request patterns',len(matches))
