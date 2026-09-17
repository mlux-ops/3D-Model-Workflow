from pathlib import Path
import json,zipfile,hashlib
root=Path(__file__).resolve().parents[1]
full=root/'output/651_Belmont_Preferred_Tiles_R2025_R2_Corrected_Review.zip'
reports=[]
with zipfile.ZipFile(full) as src:
    names=src.namelist()
    for group in ['B2-01','B2-02','B2-03','B3-01','B3-02','B3-03','Project_and_Review']:
        selected=[n for n in names if ('/'+group+'/') in n] if group!='Project_and_Review' else [n for n in names if '/B2-' not in n and '/B3-' not in n]
        path=root/'output'/f'651_Belmont_R2_{group}.zip'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as dst:
            for n in selected:
                with src.open(n) as r,dst.open(n,'w',force_zip64=True) as w:
                    while b:=r.read(1024*1024):w.write(b)
            dst.writestr('belmont_preferred_bath2_bath3_r2/EXTRACT_ALL_SEVEN.txt','Download and extract all seven 651_Belmont_R2 ZIPs into the SAME directory: B2-01, B2-02, B2-03, B3-01, B3-02, B3-03 and Project_and_Review. Merge the shared belmont_preferred_bath2_bath3_r2 folder. The RVT requires all six material texture folders. See START_HERE.md for repathing on another machine. Full optical render acceptance remains pending.\n')
        with zipfile.ZipFile(path) as z:assert z.testzip() is None
        reports.append({'group':group,'file':str(path),'bytes':path.stat().st_size,'md5':hashlib.file_digest(path.open('rb'),'md5').hexdigest()})
(root/'output/belmont_preferred_r2_modular.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
