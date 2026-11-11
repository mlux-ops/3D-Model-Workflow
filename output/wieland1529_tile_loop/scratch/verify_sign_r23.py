"""Sign or verify additive R23 against historic immutable fingerprints; no old writes."""
from pathlib import Path
from decimal import Decimal
import csv, json, hashlib, re

R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc'
names=[
 'START_HERE_R23.md',
 'R23_FOUR_WET_BATH_CONDITIONAL_ASSEMBLY_SECTIONS.md',
 'R23_ALL_13_ROOM_GOOD_BETTER_BEST_OWNER_DECISION_BOOK.md',
 'R23_13_ROOM_1TO1_SAMPLE_RENDER_SHOP_AND_PRICE_ORIGINS.md',
 'R23_13_ROOM_SKU_WET_WALL_NICHE_LEVEL_PAN_RELEASE_MATRIX.csv',
 'R23_25_W1_W3_PROVISIONAL_ELEVATIONS_NET_TRIM_MOVEMENT_CUT_SHOP.csv',
 'R23_27_HISTORICAL_ROWS_TO_NET_CARTON_COST_PROVENANCE_CONTROL.csv',
 'R23_8_WET_UNIT_INSTANCE_OWNER_TRADE_WITNESS_CHECKPOINTS.csv',
 'R23_65_ROOM_TRADE_ACTIONS_REVIEW_BRIDGE_NEW_COPY.csv',
]
def sig(p):
 b=p.read_bytes();return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def csvrows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def checkhash(path,sha): assert sig(R/path)['sha256']==sha,(path,'SHA changed')

checkhash('state/ROUND016_SUBMISSION.json','dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a')
checkhash('state/ROUND016_REVIEWER_NEUTRAL_LANGUAGE_FIX2.json','ee9ae680c4abb05c5e0e2b0407a155aa7cdd02de8bbdc3357fbd9a3a7494e38a')
checkhash('deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json','32e5ceb807e33e642680dec47aa378d21d5ba9f7b05462214277cb89e7d76df1')
checkhash('deliverables/integrated-r21-install-witness-sequence/MANIFEST.json','a212a902fcf61433cbcf165c05b07681abffcb3f70ae9f8deeb8e0756989ad66')
sub=json.loads((R/'state/ROUND016_SUBMISSION.json').read_text(encoding='utf-8'))
for room,vs in sub['candidate_source'].items():
 for letter,x in vs.items():
  assert sig(R/x['path'])==dict(sha256=x['sha256'],bytes=x['bytes']),(room,letter)
assert sub['critic_dispatch']=='NOT_DISPATCHED' and sub['all_critic_scores'] is None

roomstate=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))
ids={x['id'] for x in roomstate['rooms']};assert len(ids)==13
g=csvrows(O/names[4]); w=csvrows(O/names[5]); old=csvrows(O/names[6]); u=csvrows(O/names[7]); actions=csvrows(O/names[8])
assert len(g)==13 and {r['room'] for r in g}==ids
assert len(w)==25 and len(old)==27 and len(u)==8 and len(actions)==65
assert len({r['room']+'/'+r['wall'] for r in w})==25
assert len({r['room']+'/'+r['source_row_id'] for r in old})==27
assert len({r['room']+'/'+r['workstream'] for r in actions})==65
assert len({r['room']+'/'+r['unit'] for r in u})==8
assert sum(Decimal(r['historic_usd_two_copies']) for r in old if r['historic_usd_two_copies'])==Decimal('23572.44')
assert sum(1 for r in old if r['historic_niche_excluded_no_scope']=='TRUE')==2
assert all(r['source_15pct_waste_already_once']=='TRUE' and r['procurement_release']=='FALSE' for r in old)
assert all(r['purchase_release']=='FALSE' and r['owner_signed']=='FALSE' and r['GC_signed']=='FALSE' for r in g)
assert all(r['purchase_release']=='FALSE' and r['architect_approval']=='FALSE' for r in w)
assert all(r['purchase_release']=='FALSE' and r['owner_program_signed']=='FALSE' for r in u)
assert all(r['procurement_release']=='FALSE' and r['approved']=='FALSE' for r in actions)
assert not any(r['exact_raw_numeric_LEVEL_DCOF'] or r['exact_raw_numeric_LINEAR_or_POINT_PAN_DCOF'] for r in g)
assert {r['room'] for r in g if r['LEVEL_test_applicability']=='N/A'}=={'PH-POWDER','TX-POWDER','TX-POWDER2'}
assert {r['room'] for r in g if r['LEVEL_test_applicability']=='PARENT LEVEL ONLY'}=={'PH-WC','TX-WC'}
assert {r['room'] for r in g if r['PAN_test_applicability'].startswith('CONDITIONAL')}=={'PH-BATH3','TX-BATH3'}
assert {r['room'] for r in g if r['PAN_test_applicability'].startswith('SEPARATE')}=={'PH-PRIMARY','TX-PRIMARY','PH-BATH4'}
assert all(r['PAN_test_applicability']=='N/A' for r in g if r['room'] in {'PH-BATH2','TX-BATH2','TX-BATH4'})
assert {r['room'] for r in u}=={'PH-BATH3','TX-BATH3','PH-BATH4','PH-PRIMARY'}
check=csvrows(R/'deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv')
assert [(r['room'],r['source_row_id'],r['historic_usd_two_copies']) for r in check]==[(r['room'],r['source_row_id'],r['historic_usd_two_copies']) for r in old]
checkwalls=csvrows(R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv')
assert [(r['room'],r['wall'],r['source_width_in_UNVERIFIED']) for r in checkwalls]==[(r['room'],r['wall'],r['source_width_in_UNVERIFIED']) for r in w]

for file in names:
 assert (O/file).is_file()
 if file.endswith('.md'):
  data=(O/file).read_text(encoding='utf-8')
  assert ('FALSE' in data or 'UNSIGNED' in data or 'NO ' in data) and '1529' in data
  for link in re.findall(r'\]\(([^)]+)\)',data):
   if link.startswith('http'):continue
   target=(O/file).parent/link
   assert target.exists(),(file,link)

metadata={
 'version':'R23','as_of':'2026-11-06',
 'kind':'ADDITIVE high consequence wet bath conditional assemblies and signed 13-room owner/GC evidence requests, not a new approved board/PO',
 'focus_rooms':['PH-BATH3','TX-BATH3','PH-BATH4','PH-PRIMARY'],
 'focus_actual_unit_instances':8,'global_room_ids':13,'original_material_rows':27,
 'original_primary_niche_references_NO_SCOPE_NO_ORDER':2,
 'original_25_provisional_W_studies':25,'original_65_trade_actions':65,
 'R21_existing_field_witness_holds':156,
 'R23_individual_new_trade_actions':65,
 'source_historic_four_unit_material_only_usd':'23572.44',
 'source_historic_focus_eight_units_material_only_usd':'10931.90',
 'source_original_15pct_gross_waste_once':True,
 'source_chain_sha256':{
   'R014_submission':'946b3eda0a097961e28e76823607fd7d52b82209156e5bb59cdeb9c36450c8ed',
   'R015_submission':'cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8',
   'R016_submission':sig(R/'state/ROUND016_SUBMISSION.json')['sha256'],
   'R016_FIX2':sig(R/'state/ROUND016_REVIEWER_NEUTRAL_LANGUAGE_FIX2.json')['sha256'],
   'R021_manifest':sig(R/'deliverables/integrated-r21-install-witness-sequence/MANIFEST.json')['sha256'],
   'R022_manifest':sig(R/'deliverables/integrated-r22-three-powder-faucet-and-shop-release/MANIFEST.json')['sha256'],
 },
 'R22_independent_nonPro_reviewer_verdict':'CONTINUE_OWNER_GC_INTERNAL_EVIDENCE_ONLY',
 'R23_independent_reviewer_verdict':None,
 'original_DESIGN_worker9':'FAILED','R014_original_critic_files':6,'R014_required':8,
 'R014_formal_scoring':None,'R015_critic_dispatch':'HOLD','R015_formal_scoring':None,
 'R016_critic_dispatch':'NOT_DISPATCHED','R016_formal_scoring':None,
 'R23_critic_dispatch':'NOT_DISPATCHED','R23_weighted_scoring':None,
 'PH_TX_BATH3_program_owner_unselected':True,
 'PH_BATH4_walkin_POINT_preserved':True,
 'PH_PRIMARY_48in_LINEAR_BR73480_no_new_niche_preserved':True,
 'actual_1529_native_model_verified':False,
 'raw_numeric_individual_LEVEL_PAN_wet_labs_verified':False,
 'current_chicago_supplier_and_installed_offer_verified':False,
 'physical_sample_or_source_true_1529_render_generated':False,
 'field_inspection_performed':False,
 'owner_approval':False,'architect_release':False,'GC_release':False,
 'procurement_release':False,'global_13_room_DONE':False,
 'outputs':{n:sig(O/n) for n in names},
}
manifest=O/'MANIFEST.json'
if manifest.exists():
 assert json.loads(manifest.read_text(encoding='utf-8'))==metadata,'Existing signed R23 manifest differs; inspect before re-signing'
else:
 manifest.write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert json.loads(manifest.read_text(encoding='utf-8'))==metadata
print('PASS signed R23 9 outputs, 13 wet room gate rows, 25 original source width wall rows, 27 original source row IDs, 8 unit wet witnesses, 65 trade actions, 2 excluded primary niche rows and exact $23572.44; 6 R016 SHA unchanged; no purchase')
print('R23_SHA',sig(manifest)['sha256'])
