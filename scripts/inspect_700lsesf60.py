import clr, json
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
root=r'C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow\output\700lsesf60'
doc=__revit__.Application.OpenDocumentFile(root+r'\700LSESF60_Black_Adjustable_R2025.rfa')
data={}
for m in DB.FilteredElementCollector(doc).OfClass(DB.Material):
    if '700LSESF60' not in m.Name:continue
    a=doc.GetElement(m.AppearanceAssetId).GetRenderingAsset()
    props=[]
    for i in range(a.Size):
        p=a.Get(i)
        try:val=str(p.Value)
        except:val=str(p.Type)
        if isinstance(p,DB.Visual.AssetPropertyDoubleArray4d):
            c=p.GetValueAsColor();val=[int(c.Red),int(c.Green),int(c.Blue)]
        props.append([p.Name,val,p.NumberOfConnectedProperties])
    data[m.Name]=props
with open(root+r'\appearance_audit.json','w') as f:json.dump(data,f,indent=2,default=str)
doc.Close(False)
