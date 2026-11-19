from pathlib import Path
import csv,json,shutil
p=Path(__file__).parent;out=p/'belmont_revf';out.mkdir(exist_ok=True)
for f in (p/'belmont_reve').rglob('*'):
 if f.is_file() and not f.name.endswith(('.xlsx','.ndjson')) and not f.name.startswith('preview_'):
  dst=out/f.relative_to(p/'belmont_reve');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dst)
g=list(csv.DictReader((out/'Belmont_model_longpoint_groups.csv').open(encoding='utf-8-sig')))
(p/'revf_groups.json').write_text(json.dumps(g))
shutil.copy2(p/'belmont_scoped_geometry_check/verify_prismatic_longpoints.py',out/'verify_prismatic_longpoints.py')
s=(p/'build_reve.mjs').read_text().replace('RevE','RevF').replace('belmont_reve','belmont_revf')
s=s.replace("'Added dining scope']","'Added dining scope','Long-point review','Long-point groups']")
s=s.replace('w.recalculate();',(p/'revf_addition.mjs').read_text()+'\nw.recalculate();')
s=s.replace("['Added dining scope','A1:D33']","['Added dining scope','A1:D33'],['Long-point review','A1:E25'],['Long-point groups','A1:I11']")
s=s.replace('Sources: existing live plan views4948502','Sources: existing live plan views4948502')
s=s.replace('row(sh,4,[\'DRAFT. Not order-ready.',"row(sh,3,['New qualified modeled long-point audit: see Long-point review. Do not add to baseline quantities.']);row(sh,4,['DRAFT. Not order-ready.")
(p/'build_revf.mjs').write_text(s)
notes='''BELMONT RevF | CURRENT CONSOLIDATED PRIVATE REVIEW | 17 NOVEMBER 2026
RevF supersedes RevE as the current review workbook. RevE owner directions and added-wall measurement holds remain applicable. Historical readmes and evidence retained. Not construction, cut or order release.

NEW MEASURED SUBSET:84 individual base simple solids=520.7418339469 LF;158 individual crown solids=1183.3287144422 LF. Split groups add14 base runs in7 elements=35.4200769232 LF and30 crown runs in13 elements=96.6433403633 LF. All qualified totals:98 base runs/91 elements=556.1619108701 LF;188 crown runs/171 elements=1279.9720548055 LF. Grouped split runs have no individually located lengths and must not be represented as individually measured cuts.

OVERLAPS:12 crown pieces/six same-line axial-overlap pairs; their FULL piece lengths total71.2708333333 LF. This is not the overlapped length to subtract. Unflagged qualified crown subset=1208.7012214722 LF. No identical boxes, no same-line overlap among qualified base only. Unqualified model scope may overlap these. Do not present screened subset as whole-project net or purchase quantity.

METHOD:V/(h*t)+t/2*sum(abs(n_cross/n_axis)) across end planes. Require all faces, full projected ends, top/bottom area versus V/h, side areas/full vertical section and cross-sectional bbox checks. Single piece independently agrees with axial bbox. Script reproduced from saved receipts, not fresh model queries. The CSV retains source receipt IDs, element IDs, individual/group classes and flags. Script supplied unchanged; its relative input paths refer to source workspace output/trim_takeoffs_20261117/belmont_scoped_geometry_check. Equivalent inputs are in Prior_RevC_Evidence/Evidence in this package.

DO NOT ADD qualified long points to baseline volume equivalents, duplex dining draft outlines, or closure strips. Different bases overlap. Owner8in base/3in crown, new Simplex dining and Penthouse entry-right same-style instruction, missing selected face/limits/heights and all prior geometry/room/stock/waste holds remain. See Added dining scope tab and START_HERE_RevE.txt. No additional-wall LF invented.
'''
(out/'START_HERE_RevF.txt').write_text(notes)
