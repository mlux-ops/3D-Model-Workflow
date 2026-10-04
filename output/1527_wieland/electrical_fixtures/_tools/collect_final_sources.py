"""Archive the last explicitly discovered manufacturer resources without authentication."""
from pathlib import Path
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
import datetime, hashlib, json, sys, zipfile
sys.dont_write_bytecode=True
sys.stdout.reconfigure(errors='replace')
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
sys.path.insert(0,str(REPO/'output/lightology_20260923/tools/pdf_runtime'))
import pymupdf
GROUPS={g['key']:g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups']}
JOBS=[
('AMB-MB-56-EB-870-CC','https://modernfan.com/wp-content/uploads/AMB-Cutsheet.pdf','Ambit_current_cutsheet.pdf','https://modernfan.com/ceiling-fans/ambit-dc-56/'),
('ORION_TUBE_UNSPECIFIED','https://leebroom.com/wp-content/uploads/2026/06/Orion-Tube-Light_0626REV21.pdf','Orion_Tube_current_spec.pdf','https://leebroom.com/lighting/orion-tube-light-polished-gold/'),
('ORION_TUBE_UNSPECIFIED','https://leebroom.com/wp-content/uploads/2025/07/Orion-1.zip','Orion_manufacturer_3D_Revit.zip','https://leebroom.com/lighting/orion-tube-light-polished-gold/'),
('4BEMW_SWW5_90CRI_M6','https://media.distributordatasolutions.com/326/auto_mfr_template/134763e8823704c00d6820e833bb6f9a6caede5a.pdf','Juno_4BE_current_spec.pdf','https://www.mayerelectric.com/Product/LITHONIA-The-4BEMW-Baffle-4-Inch-Round-120-Volts-LED-Recessed-Downlight-2700K-3000K-35000K-4000K-5000K-10-Volt-Dimming-194994160519')]

def run(entry):
    key,url,name,ref=entry
    path=ROOT/GROUPS[key]['canonical_item']/'source'/name
    receipt=path.with_suffix(path.suffix+'.acquisition.json')
    if receipt.exists():return json.loads(receipt.read_text())
    row={'key':key,'url':url,'linked_from':ref,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terms_note':'Anonymous public manufacturer resource; no account, credentials, or license acceptance. Manufacturer copyright retained.'}
    try:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36','Referer':ref,'Accept':'*/*'}
        with urlopen(Request(url,headers=headers),timeout=45) as r:
            data=r.read(120*1024*1024)
            row.update(final_url=r.geturl(),content_type=r.headers.get('Content-Type'),content_length=r.headers.get('Content-Length'))
        if path.exists():raise RuntimeError('Existing resource preserved')
        path.write_bytes(data)
        row.update(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),signature_hex=data[:12].hex())
        if name.endswith('.zip'):
            with zipfile.ZipFile(path) as z:
                row.update(zip_members=z.namelist(),zip_crc_error=z.testzip())
                dest=path.with_suffix('');dest.mkdir(exist_ok=True)
                extracted=[]
                for member in z.infolist():
                    if not member.filename.lower().endswith(('.rfa','.txt','.pdf')):continue
                    target=(dest/member.filename).resolve()
                    if not target.is_relative_to(dest.resolve()):raise ValueError('ZIP member escapes source folder')
                    if not target.exists():z.extract(member,dest)
                    extracted.append(str(target))
                row['extracted_files']=extracted
        elif name.endswith('.pdf'):
            doc=pymupdf.open(path);out=path.with_suffix('');out.mkdir(exist_ok=True)
            row['pages']=len(doc)
            texts=[p.get_text() for p in doc]
            (out/'pages.txt').write_text('\n\n'.join('PAGE %d\n%s'%(i+1,t) for i,t in enumerate(texts)),encoding='utf-8')
            row['text_path']=str(out/'pages.txt')
            for i in range(min(3,len(doc))):doc[i].get_pixmap(matrix=pymupdf.Matrix(1.6,1.6)).save(out/('page_%02d.png'%(i+1)))
            row['review_folder']=str(out)
    except Exception as exc:row['error']=str(exc)
    receipt.write_text(json.dumps(row,indent=2),encoding='utf-8')
    return row

with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(run,JOBS))
(ROOT/'FINAL_SOURCE_RECEIPTS.json').write_text(json.dumps(rows,indent=2))
for row in rows:
    print(row['key'],row.get('bytes'),row.get('error','ARCHIVED'))
    if row.get('zip_members'):print('ZIP MEMBERS:',row['zip_members'])
    if row.get('text_path'):print(Path(row['text_path']).read_text(encoding='utf-8')[:6500])
