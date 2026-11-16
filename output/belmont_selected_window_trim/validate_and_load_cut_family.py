import json
import native_query as native
from apply_casing import run

document=json.loads((native.TASK/'cut_family_document.json').read_text())
pre={'is_family':True,'allow_existing_document':True}
geometry=run('cut_family_geometry','family.geometry.inspect',{},document=document,preconditions=pre)
inspection=run('cut_family_inspect','family.inspect',{},document=document,preconditions=pre)
depth=json.loads((native.TASK/'cut_family_arguments.json').read_text())['depth']
flex=run('cut_family_flex','family.type.flex',{'types':[{'name':'Fourth-floor primary bedroom window adaptation','values':{'Panel Molding Thickness':depth+1/96}}]},document=document,preconditions=pre)
if not flex.get('original_state_restored'):
    raise RuntimeError('Flex did not confirm restoration')
path=native.TASK/'SHB_Primary_Bedroom_Window_Trim_Adaptation_R2025.rfa'
saved=run('cut_family_save','family.save',{'path':str(path)},document=document,preconditions=pre)
loaded=run('cut_family_load','family.load',{'path':str(path),'replacement_policy':'reject'})
print(json.dumps({'native_family_saved':str(path),'flex_restored':True,'loaded':loaded}))
