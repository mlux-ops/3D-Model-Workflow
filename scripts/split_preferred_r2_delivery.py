from pathlib import Path
import json, zipfile, hashlib
ROOT=Path(__file__).resolve().parents[1]
base='651_Belmont_Preferred_Tiles_R2025_R2_Corrected_Review'
full=ROOT/'output'/f'{base}.zip'
note='''DOWNLOAD AND EXTRACT BOTH ZIP FILES

The Drive connector has a 512 MiB per-file upload limit. The full-resolution
package is distributed as TWO ordinary ZIP files, not binary split volumes.

1. Download both Part_1_of_2 and Part_2_of_2.
2. Extract both into the SAME destination directory. Merge their shared
   belmont_preferred_bath2_bath3_r2 folder.
3. Part 1 supplies the native RVT, Bath 2, and project notes/review evidence.
   Part 2 supplies Bath 3 textures, references, layout and preview files.
4. Open the RVT only after both ZIPs have been extracted. If this is a new
   location, relink maps as directed in START_HERE.md.

The single complete ZIP is also preserved locally in the project output folder.
This is R2 corrected review material; full optical render acceptance is pending.
'''
reports=[];members=[]
with zipfile.ZipFile(full) as src:
    all_names=src.namelist()
    for part in (1,2):
        path=ROOT/'output'/f'{base}_Part_{part}_of_2.zip'
        selected=[n for n in all_names if ('/B3-' in n)==(part==2)]
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as dst:
            for n in selected:
                with src.open(n) as r,dst.open(n,'w',force_zip64=True) as w:
                    while block:=r.read(1024*1024):w.write(block)
            dst.writestr('belmont_preferred_bath2_bath3_r2/DOWNLOAD_AND_EXTRACT_BOTH.txt',note)
        with zipfile.ZipFile(path) as z:assert z.testzip() is None
        assert path.stat().st_size<536870912
        members+=selected
        reports.append({'part':part,'file':str(path),'bytes':path.stat().st_size,
            'md5':hashlib.file_digest(path.open('rb'),'md5').hexdigest(),
            'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()})
assert sorted(members)==sorted(all_names)
(ROOT/'output/belmont_preferred_r2_drive_parts.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
