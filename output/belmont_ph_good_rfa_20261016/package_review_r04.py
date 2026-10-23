"""Create a revisioned seven-family REVIEW package; preserve native originals.

The package explicitly retains all pending appearance/finish/photometry holds.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
F = ROOT / 'families'
C = ROOT / 'candidates'
R = ROOT / 'release'
WORKFLOW = Path(r'E:\Claude\3D-Model-Workflow\docs\REVIT_RFA_AGENT_WORKFLOW_20261016.md')
NODES = Path(r'E:\Claude\3D-Model-Workflow\output\lightology_20260923\release\Lightology_14_Face_Based_RFAs_R2025_Rev1\RFAs\Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa')

SELECTED = [
 ('ALR1280090','LP549448MBCL','Alora Cassia, Matte Black/Clear',C/'Alora_Cassia_LP549448MBCL_R2025_R02.rfa','Native clear-glass type verified; source appearance and project QA pending'),
 ('HIN990485','53860BK','Hinkley Eos, Black/Etched',C/'Hinkley_Eos_53860BK_R2025_R03_UNAPPROVED.rfa','Native host and actual 25x5.5x3 OEM envelope pass; photo-inferred details and IES/MEP remain HOLD'),
 ('KZC1353667','PD3106-BG','Kuzco Bolla, Brushed Gold/Clear',C/'Kuzco_Bolla_PD3106_BG_R2025_IES_FINISH_R03_PARTIAL.rfa','Exact BG IES, glass preserved, canopy/cord faces differentiated; 4 entry-collar faces/portability/optical appearance hold'),
 ('MFR1415595','FR-W2502-52L-SB/MB','Modern Forms Smooth fan, Soft Brass/Matte Black',C/'ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa','52in sweep and distinct matte-black blades/soft-brass housing native PASS; unidentified imported CAD components require review'),
 ('MFR201959','WS-3127-CH','Modern Forms Vogue, Chrome',C/'ModernForms_Vogue_WS-3127_CH_R2025_R02.rfa','Chrome/opal native material revision; optical appearance and photo QA pending, IES vintage mismatch'),
 ('QUO1249827','858-59','Quorum Veno, Matte Black/Clear',C/'Quorum_Veno_858-59_R2025_R04_UNAPPROVED.rfa','Corrected narrow-top/wide-mid/open-bottom contour, 11in/43.75in native PASS; OEM glass profile/IES still source-unverified'),
 ('VCS833918','KW1041BBS','Visual Comfort Nodes, Burnished Brass',NODES,'Pre-existing accepted visualization RFA; current project installation QA pending'),
]

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def main():
 R.mkdir(exist_ok=True)
 zip_path=R/'Belmont_PH_GOOD_Lighting_RFA_REVIEW_20261016_r04.zip'
 if zip_path.exists():raise FileExistsError(zip_path)
 included={}
 def add(z,src,dst):
  if not src.is_file():raise FileNotFoundError(src)
  if dst in included:raise ValueError('Duplicate archive member '+dst)
  z.write(str(src),dst)
  included[dst]={'sha256':digest(src),'bytes':src.stat().st_size,'local_source':str(src)}
 summary=[]
 with ZipFile(zip_path,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
  for sku,model,title,source,status in SELECTED:
   arc='REVIEW_RFAs/'+source.name
   add(z,source,arc)
   summary.append({'smartsheet_sku':sku,'manufacturer_model':model,'selection':title,
                   'rfa_archive_member':arc,'sha256':included[arc]['sha256'],
                   'status':'REVIEW_NOT_FINAL','evidence_and_holds':status})
  # Explicit source / quality traceability, including first-run failures.
  for folder,archive in [('runner/receipts','QA/native_receipts'),('qa','QA/independent'),
                         ('sources/photometry','SOURCES/IES'),('scripts','SOURCES/builders')]:
   d=ROOT/folder
   if not d.is_dir():continue
   for p in d.iterdir():
    if p.is_file() and p.suffix.lower() in ('.json','.md','.ies','.py'):
     add(z,p,archive+'/'+p.name)
  for p in (ROOT/'qa'/'previews_r05').glob('*.png'):
   add(z,p,'QA/latest_previews/'+p.name)
  add(z,ROOT/'sources'/'oem'/'manifest.json','SOURCES/oem_manifest.json')
  add(z,WORKFLOW,'WORKFLOW.md')
  text=('651 Belmont Penthouse GOOD - Revit 2025 family REVIEW, 2026-10-16 r04\n\n'
        'Seven exact Smartsheet selections represented. This is an engineering review package, NOT installation approval.\n'
        'Native Revit save/reopen/placement and material corrections have been attempted and documented in QA.\n'
        'The original manufacturer BIM sources remain separate in the local sources/oem archive and are unchanged.\n'
        'Current blocks: Bolla entry-collar finish, portable IES cache and glass appearance; '
        'Smooth numeric CAD import appearance; Hinkley optical/IES/electrical details; '
        'Quorum glass body contour interpreted from OEM photograph and lamp/suspension; '
        'Vogue current photometry version (manufacturer 2017 IES differs from current specs); '
        'final project installation and calibrated optical rendering.\n'
        'See INDEX.json and accompanying receipts; do not approve by filename or technical PASS alone.\n')
  z.writestr('README.txt',text)
  z.writestr('INDEX.json',json.dumps(summary,indent=2))
 with ZipFile(zip_path) as z:
  assert z.testzip() is None
 manifest={'archive':str(zip_path),'archive_sha256':digest(zip_path),'archive_bytes':zip_path.stat().st_size,
           'status':'REVIEW_NOT_RELEASED','selections':summary,'members':included}
 (R/'REVIEW_R04_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
 print(json.dumps({'archive':str(zip_path),'sha256':digest(zip_path),'bytes':zip_path.stat().st_size,
                   'rfa_count':len(summary),'status':'REVIEW_NOT_RELEASED'},indent=2))

if __name__=='__main__':main()
