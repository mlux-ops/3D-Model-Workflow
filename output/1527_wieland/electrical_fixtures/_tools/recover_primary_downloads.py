"""Retrieve observed public resources using their product-page referrers."""
from pathlib import Path
from urllib.request import Request, urlopen
import datetime, json, hashlib, zipfile, sys
sys.stdout.reconfigure(errors='replace')
ROOT=Path(__file__).resolve().parents[1]
groups={g['key']:g for g in json.loads((ROOT/'GROUPS.json').read_text())['groups']}
jobs=[('4BEMW_SWW5_90CRI_M6','https://img.acuitybrands.com/public-assets/catalog/1897044/4be_4se-sww5.pdf','Juno_4BE_4SE_manufacturer_spec.pdf','https://www.acuitybrands.com/products/detail/1897044/juno/e-series-led-trim-kit/4in-5-and-6in-switchable-white-led-downlights-in-smooth-or-baffle-trim-styles'),
      ('MFR918914','https://modernforms.com/images/products/REVIT/FR-W2006-52_REVIT.zip','Zephyr52_manufacturer_Revit_browser_headers.zip','https://modernforms.com/product/zephyr-52/')]
results=[]
for key,url,name,ref in jobs:
    path=ROOT/groups[key]['canonical_item']/'source'/name
    if path.exists():raise RuntimeError('Preserve existing resource '+str(path))
    record={'url':url,'linked_from':ref,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'terms_note':'Anonymous manufacturer download. No authentication, account, or license acceptance.'}
    try:
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36','Referer':ref,'Accept':'*/*'}
        with urlopen(Request(url,headers=headers),timeout=45) as r:
            data=r.read(80*1024*1024);record.update(content_type=r.headers.get('Content-Type'),final_url=r.geturl())
        path.write_bytes(data);record.update(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),signature_hex=data[:12].hex())
        if path.suffix=='.zip':
            with zipfile.ZipFile(path) as z:
                record['zip_members']=z.namelist();record['zip_crc_error']=z.testzip()
                dest=path.with_suffix('');dest.mkdir()
                for info in z.infolist():
                    if not (dest/info.filename).resolve().is_relative_to(dest.resolve()):raise ValueError('ZIP path escapes source folder')
                    z.extract(info,dest)
    except Exception as exc:record['error']=str(exc)
    path.with_suffix(path.suffix+'.acquisition.json').write_text(json.dumps(record,indent=2))
    results.append(record)
    print(json.dumps(record,indent=2))
(ROOT/'RECOVERED_PRIMARY_DOWNLOADS.json').write_text(json.dumps(results,indent=2))
