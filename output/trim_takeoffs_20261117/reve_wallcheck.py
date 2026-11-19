exec(open('output/trim_takeoffs_20261117/reve_read.py').read().split("for name in")[0])
walls=json.loads((out/'walls0.json').read_text())['result']['items']
for id in [4881744,4881642,4958400]:
 uid=next(x['unique_id'] for x in walls if x['id']==id)
 for op,key,args in [('elements.inspect','inspect',{'element':uid,'geometry':True}),('parameters.query','params',{'element':uid})]:
  rr=call(op,doc,args,f'{key}_{id}',pre);print(id,key,rr.get('status'))
print(call('context.query',doc,{},'final_context',pre).get('status'))
