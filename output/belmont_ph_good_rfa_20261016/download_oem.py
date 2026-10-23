import hashlib, json, pathlib, urllib.request, zipfile, shutil

BASE=pathlib.Path(__file__).resolve().parent/'sources'/'oem'
BASE.mkdir(parents=True,exist_ok=True)
SOURCES={
 'ALR1280090_LP549448_Cassia_Revit.zip':'https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-LP549448-Cassia.zip',
 'KZC1353667_PD3106_Bolla_Revit.zip':'https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-PD3106-Bolla.zip',
 'MFR1415595_FR-W2502_Smooth_Revit.zip':'https://modernforms.com/images/products/REVIT/FR-W2502_REVIT.zip',
 'MFR201959_WS-3120_Vogue_family_Revit.zip':'https://modernforms.com/images/products/REVIT/WS-3120_REVIT.zip',
 'ALR1280090_LP549448_Cassia_spec.pdf':'https://s3-us-west-2.amazonaws.com/catsy.870/LP549448_Spec_Sheet.pdf',
 'KZC1353667_PD3106_Bolla_spec.pdf':'https://s3-us-west-2.amazonaws.com/catsy.870/PD3106%2BSpec%2BSheet.pdf',
 'MFR1415595_FR-W2502_Smooth_spec.pdf':'https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2502_SPSHT.pdf',
 'MFR201959_WS-3127_Vogue_spec.pdf':'https://modernforms.com/dynamic-specsheet/?download=specs5&ppid=1546',
}
results=[]
for name,url in SOURCES.items():
 p=BASE/name
 row={'name':name,'url':url,'intended_sku':name.split('_')[0]}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=35) as resp,open(p,'wb') as out:
   row['http_status']=resp.status
   shutil.copyfileobj(resp,out)
  data=p.read_bytes()
  row['size_bytes']=len(data)
  row['sha256']=hashlib.sha256(data).hexdigest()
  row['signature_valid']=data[:4]==b'PK\x03\x04' if name.endswith('.zip') else data[:5]==b'%PDF-'
  if name.endswith('.zip') and row['signature_valid']:
   with zipfile.ZipFile(p) as archive:
    row['zip_test']=archive.testzip() is None
    row['members']=[{'name':x.filename,'size_bytes':x.file_size} for x in archive.infolist() if not x.is_dir()]
    selected=[]
    for x in archive.infolist():
     if x.is_dir() or not x.filename.lower().endswith('.rfa'): continue
     path=pathlib.PurePosixPath(x.filename.replace('\\','/'))
     if '..' in path.parts or path.is_absolute(): continue
     dest=BASE/'extracted'/name.replace('.zip','')/path
     dest.parent.mkdir(parents=True,exist_ok=True)
     with archive.open(x) as source,open(dest,'wb') as target: shutil.copyfileobj(source,target)
     selected.append({'path':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    row['extracted_rfa']=selected
 except Exception as exc:
  row['error']=str(exc)
 results.append(row)
 print(name, row.get('http_status'), row.get('signature_valid'), len(row.get('extracted_rfa',[])),row.get('error',''),flush=True)
(BASE/'manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
