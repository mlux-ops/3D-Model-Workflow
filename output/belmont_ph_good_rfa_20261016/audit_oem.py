import pathlib,json,hashlib,zipfile
base=pathlib.Path(__file__).resolve().parent/'sources'/'oem'
items=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
for row in items:
    p=base/row['name']
    if not p.exists(): continue
    b=p.read_bytes()
    row['size_bytes']=len(b)
    row['sha256']=hashlib.sha256(b).hexdigest()
    row['signature_valid']=b[:4]==b'PK\x03\x04' if p.suffix=='.zip' else b[:5]==b'%PDF-'
    row['local_access']='downloaded'
    row.pop('error',None)
    if p.suffix=='.zip':
        with zipfile.ZipFile(p) as z:
            row['members']=[{'name':i.filename,'compression_type':i.compress_type,'bytes':i.file_size} for i in z.infolist() if i.filename.lower().endswith('.rfa')]
        sub=base/'extracted'/p.stem
        row['extracted_rfa']=[{'path':str(x),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in sub.rglob('*.rfa') if x.stat().st_size>0]
        row['exact_model_rfa_present']= any(('WS-3127' if 'WS-3120_Vogue' in p.name else 'LP549448' if 'Cassia' in p.name else 'PD3106' if 'Bolla' in p.name else 'FR-W2502' ) in pathlib.Path(x['path']).name for x in row['extracted_rfa'])
(base/'manifest.json').write_text(json.dumps(items,indent=2),encoding='utf-8')
for x in items:
    print(x['name'],'bytes',x.get('size_bytes'), 'RFA',[(pathlib.Path(y['path']).name,y['bytes']) for y in x.get('extracted_rfa',[])], 'error',x.get('error'))
