"""One-time exact worker-14 R014 blind research and R16 signed source/gate FIX2."""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1]
sub=R/'state/ROUND014_SUBMISSION.json'
research=R/'research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md'
d=R/'deliverables/integrated-r16'
book=d/'R16_13_ROOM_DESIGN_CONSTRUCTION_PROCUREMENT_BOOK.md'
sourcecsv=d/'R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv'
manifest=d/'MANIFEST.json'
audit=R/'state/ROUND014_R16_REVIEWER_FIX2.json'
assert not audit.exists()
def fp(p):
    b=p.read_bytes()
    return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
old_sub=fp(sub); old_research=fp(research)
old_book=fp(book);old_csv=fp(sourcecsv);old_manifest=fp(manifest)
assert old_sub['sha256']=='b34729bd7b975406deb120915f05dcf8b8b3ee1155527c1bd76e58ba5067d11d'
assert old_manifest['sha256']=='ac53b5a2f622eeb8f03df868026a5e30f3fa15a5497633e2e2b732978087c6b0'
s=json.loads(sub.read_text(encoding='utf-8'))
m=json.loads(manifest.read_text(encoding='utf-8'))
assert s['all_critic_scores'] is None and s['critic_dispatch']=='NOT DISPATCHED'
for rid in s['rooms']:
    assert not list((R/'rooms'/rid/'board/round-014').glob('critic-*.md'))
assert m['outputs'][book.name]==old_book and m['outputs'][sourcecsv.name]==old_csv
other={k:v for k,v in m['outputs'].items() if k not in (book.name,sourcecsv.name)}
assert len(other)==2 and all(fp(d/name)==ref for name,ref in other.items())

# Critic-readable maker note lists maker evidence without describing hidden
# historical/revised roles. The dated source quotation table remains common
# evidence for BOTH neutral candidates, never a private-key hint.
t=research.read_text(encoding='utf-8')
replace={
 'Revised PH wet tub/shower wall; fresh palette variation with Chrome Hansgrohe':
    'PH applicable wet tub/shower wall color option beside selected Chrome Hansgrohe (no source-role implication)',
 'Proposed PH Sapphire is conditional and requires current exact-suffix sample, field layout and supplier quote':
    'Sapphire requires current exact-suffix sample, field layout and supplier quote before any use',
 'Original PH/TX wet niche/back/returns and possible revised PH contrasting band':
    'PH/TX wet niche/back/returns maker wet permission; potential matching field accents pending owner signature',
 'Original quoted niche gross already separately loaded; deduct actual field opening once':
    'Dated quoted niche gross already separately loaded; deduct actual field opening once',
 'TX wet field retained with selected Black Onyx Brizo set':
    'TX wet field application beside selected Black Onyx Brizo shower fixtures',
 'preserve selected color while changing verified LEVEL/PAN system':
    'independently verify wall color with any LEVEL/PAN system',
 '| Original PH wet field | Individual maker Wet Areas **NOT established**; source historical design **FAIL** for wet shower/tub walls.':
    '| PH wet wall application listing NOT established | Individual maker Wet Areas **NOT established**; this finish **FAILS** wet shower/tub use until a SKU-specific maker approval is produced.',
 'Earlier R011 alternate LEVEL floor, NOT part of new R014 revised scheme':
    'Separate comparable HNC6615 LEVEL maker evidence; no R014 candidate proposes it',
 'Independent R011 options already studied; not proposed again as a novel design':
    'This product has already been studied as a separate non-Prime material and is not part of the two R014 candidate LEVEL specifications',
 'Earlier R011 conditional POINT PAN':
    'Separate comparable HNC6715 POINT PAN maker evidence, not a specified R014 product',
 '**The proposed Sapphire PH wall, Prime RL21 LEVEL and conditional RL21 POINT PAN are NOT current supplier-order substitutions**.':
    '**Tones Sapphire, Prime RL21 LEVEL and conditional RL21 POINT PAN are separately evaluated materials, NOT current supplier-order substitutions**.'
}
for old,new in replace.items():
    assert t.count(old)==1,(old,t.count(old))
    t=t.replace(old,new)
research.write_text(t,encoding='utf-8')
assert not any(x in t.lower() for x in ('revised ph','original ph wet field','source historical design','new r014 revised scheme'))

# R016 written owner/GC rows: form-related exact evidence instead of one
# generic FLOOR/PAN requirement copied onto TUB, DRY and inherited-WC rooms.
text=book.read_text(encoding='utf-8')
lines=text.splitlines()
changed=[]
for i,line in enumerate(lines):
    if not line.startswith('| ') or '| Retain dated original row as provenance only;' not in line:
        continue
    cells=[c.strip() for c in line.strip('|').split('|')]
    assert len(cells)==4,cells
    rid=cells[0]
    if rid in ('PH-BATH2','TX-BATH2','TX-BATH4'):
        best='Retain selected Duravit TUB and individual wall wet permission; obtain only exact LEVEL bath-floor raw numeric wet DCOF, true tub flange, clear rough dimension, verified 1529 room, 1:1 samples and current Chicago installed bid. Shower PAN N/A; owner/GC signoffs required.'
    elif rid in ('PH-POWDER','TX-POWDER','TX-POWDER2'):
        best='DRY vanity wall on WOOD floor; actual basin/faucet/escutcheon, wall edge/caliber/grout/backer, 1:1 finish sample, verified 1529 face, actual carton and installed Chicago bid with owner/GC signatures. Wet shower LEVEL/PAN raw tests N/A for scheduled dry tile/wood floor.'
    elif rid in ('PH-WC','TX-WC'):
        best='Keep WC LEVEL tile within corresponding Primary gross, exact maker raw numeric LEVEL wet DCOF and measured threshold/joint; no separate WC tile purchase and NO shower PAN. Verify source only once, approved owner/GC installation and installed price allocation.'
    elif rid in ('PH-BATH3','TX-BATH3'):
        best='Owner first signs TUB or WALK-IN (and PH basin). Require exact numeric LEVEL wet DCOF in either branch; POINT PAN maker raw numeric wet DCOF, slope/membrane/flood ONLY if owner elects WALK-IN; TUB branch PAN N/A. Approve true 1529 geometry, current installed Chicago quote and GC release.'
    else:
        best='Maker exact wet WALL/NICHE and raw numeric wet LEVEL and, for selected real shower, separate LINEAR/POINT PAN raw wet DCOF, compatible drain/membrane/flood, verified 1529 geometry, measured carton LF, current Chicago installed bid and owner/GC signatures before release.'
    cells[3]=best
    if rid=='TX-BATH2':
        cells[2]='Retain selected Duravit TUB with Hansgrohe CHROME, NO PAN; individual wet wall/LEVEL approval and owner-unselected TX Bath2 basin remain held.'
    if rid=='TX-BATH4':
        cells[2]='Retain selected Duravit TUB with Hansgrohe MATTE WHITE, NO PAN; separate individual wet NICHE vs original Caviar, LEVEL test and tub flange; no TX Bath2 basin issue.'
    lines[i]='| '+' | '.join(cells)+' |'
    changed.append(rid)
assert len(changed)==13 and set(changed)=={r['id'] for r in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
book.write_text('\n'.join(lines)+'\n',encoding='utf-8')
assert 'Hansgrohe Chrome/Matte White' not in book.read_text(encoding='utf-8')

with sourcecsv.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
changed_floors=[]
for row in rows:
    if row['room'] in ('PH-BATH2','TX-BATH2','TX-BATH4') and 'floor' in row['source_surface'].lower():
        old=row['next_possible_order_formula_not_current_quantity']
        assert 'if walk-in/linear' in old
        row['next_possible_order_formula_not_current_quantity']='TUB ONLY, NO TILED PAN: ceil(verified bath LEVEL gross SF with original waste included once / exact manufacturer LEVEL carton SF), after verified 1529 floor net and exact raw measured wet DCOF; no secondary PAN cases'
        changed_floors.append(row['room'])
assert sorted(changed_floors)==['PH-BATH2','TX-BATH2','TX-BATH4']
with sourcecsv.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
assert sum(float(x['two_copy_historic_material_usd']) for x in rows if x['two_copy_historic_material_usd'])==23572.44
assert len(rows)==27 and all(x['gc_purchase_release']=='FALSE' for x in rows)

# Re-sign submission RESEARCH fingerprint without changing 4 candidate bytes.
s['maker_research_sha256']=fp(research)['sha256']
s['research_role_language_fix']='independent worker-14 FIX2: shared critic-readable R014 research has neutral material descriptions without private source/alternative role labels'
s['reviewer_preflight_verdict']=None
sub.write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert sum(len(v) for v in s['candidate_files'].values())==4
for rid,items in s['candidate_files'].items():
    for letter,info in items.items():
        assert fp(R/info['file'])['sha256']==info['sha256'] and fp(R/info['file'])['bytes']==info['bytes']
m['r014_source_sha256']=fp(sub)['sha256']
m['outputs'][book.name]=fp(book)
m['outputs'][sourcecsv.name]=fp(sourcecsv)
manifest.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
assert all(fp(d/name)==ref for name,ref in m['outputs'].items())
receipt={
 'as_of':'2026-11-06','round':14,'reviewer':'worker-14',
 'fix':'Remove source/revised private role hints from shared R014 maker research; R16 individual tub/dry/shared WC and two Bath3 conditional raw LEVEL/PAN gates; TX2 Chrome TX4 Matte White; three TUB floor carton rows have no point/linear PAN',
 'maker_research_before_after':{'old':old_research,'new':fp(research)},
 'source_submission_before_after':{'old':old_sub,'new':fp(sub)},
 'r16_book_before_after':{'old':old_book,'new':fp(book)},
 'r16_source_csv_before_after':{'old':old_csv,'new':fp(sourcecsv)},
 'r16_manifest_before_after':{'old':old_manifest,'new':fp(manifest)},
 'r16_other_two_files_unchanged':other,
 'neutral_candidate_sha_and_bytes_unchanged':True,
 'R013_original_and_scored_unchanged':True,
 'R014_critic_files':0,'all_critic_scores':None,'weighted_scoring':None,
 'owner_approval':False,'procurement_release':False
}
audit.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS exact R014 blind shared research role FIX2 and R16 maker/gate/tub source FIX; 4 source candidate SHA unchanged, 0 critics')
print('R014_SUBMISSION_SHA',fp(sub)['sha256'])
print('R16_MANIFEST_SHA',fp(manifest)['sha256'])
