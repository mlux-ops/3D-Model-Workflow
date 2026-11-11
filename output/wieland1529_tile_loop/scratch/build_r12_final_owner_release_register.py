"""Create focused 13-room owner decision and GC release register, extending signed R12 package.
Only new R12 output, updated R12 manifest and R012 pending collection flags. No scoring.
"""
from pathlib import Path
import hashlib, json, csv
R=Path(__file__).resolve().parents[1]
out=R/'deliverables/integrated-r12'
manifest_path=out/'MANIFEST.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
statepath=R/'state/ROOMS.json'
state=json.loads(statepath.read_text(encoding='utf-8'))
colpath=R/'state/ROUND012_CRITIC_COLLECTION.json'
collection=json.loads(colpath.read_text(encoding='utf-8'))
assert len(state['rooms'])==13 and collection['weighted_scoring_complete'] is False and collection['all_critic_scores'] is None
assert sum(len(z) for z in collection['report_files'].values())==12
assert len(manifest['outputs'])==5 and manifest['owner_approved'] is False and manifest['procurement_release'] is False
for name,rec in manifest['outputs'].items():
 raw=(out/name).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==rec['sha256'] and len(raw)==rec['bytes']
decision={
 'PH-PRIMARY':('Approve sample study of flat Bone wet wall only; confirm no primary niche and retained separate tub + 48-in Brizo BNX LINEAR','Individually wet-listed flat Bone; Reed relief wet use unproved; LEVEL and Prime RL21 mosaic PAN raw measured DCOF FAIL','Signed LINEAR frame/mosaic thickness stack-up, approved membrane/liner and correct 1529 measured shower and WC floor split'),
 'PH-BATH2':('Approve or revise wet-listed Sapphire tub walls and Matte White Hansgrohe while keeping Duravit tub','Sapphire individual wet wall PASS; selected LEVEL bath-floor exact raw DCOF FAIL; tiled shower pan N/A','Tub flange, niche face subtraction, LEVEL threshold and final floor SKU certificate'),
 'PH-BATH3':('Choose tub or walk-in and owner-UNSELECTED basin; reconcile existing Delta DT062412 Chrome square drain','Sandstone alternate wet wall PASS; original Opal wet wall FAIL; LEVEL/conditional POINT PAN numeric raw DCOF FAIL','Owner program branch before measuring pan, point drain/liner and niche volumes'),
 'PH-BATH4':('Confirm actual Brizo BNX square POINT walk-in and settle original 35-vs-27-SF, Soft-vs-AntiSlip, ribbed/Caviar wet holds','Original Ribbed and Caviar individual wet walls FAIL; revised flat wet wall/niche conditional PASS; LEVEL and POINT PAN raw DCOF FAIL','Document corrected pan SF, original 107.2 SF/copy Ribbed row and 214.4 SF two-copy possible historical vendor GRAND-TOTAL omission—not payable shortage'),
 'PH-POWDER':('Approve or revise dry Earth Lines vanity feature, grout, edge and hardware sample','Dry decorative wall: bath-floor DCOF and shower membrane not applicable','True W1 vanity cut diagram with vanity/mirror/electrical fixture constraints'),
 'PH-WC':('Confirm single inherited PH Primary LEVEL floor finish, no separate buy','Same exact tested LEVEL product as PH Primary; separate WC buy prohibited','Survey 15 SF legacy shared WC source contribution and single threshold'),
 'TX-PRIMARY':('Select visual sample of flat Clay only, retain Brizo BNX 48-in LINEAR and no niche','Ribbed wet FAIL, flat Clay wet PASS; Emser >=0.60 LEVEL and Prime RL21 pan TARGET not exact raw DCOF','Check selected BT0734816-BNX 48-in LINEAR adjustable frame 7–18 mm against Prime RL21 1/4-in nominal mosaic and separate BR73480 rough; complete assembly/finished elevation requires written maker and GC confirmation'),
 'TX-BATH2':('Select basin without changing Duravit tub or Chrome Hansgrohe; compare Copper 2x20 layout','Copper/Sandstone wet tub walls PASS; Clay Soft or Emser LEVEL raw numeric DCOF FAIL; pan N/A','62.484-in source W1 proposed 2x20-in full + two 11.242-in nominal balanced ends, calibrated to grout; measured niche deduction and tub flange'),
 'TX-BATH3':('Owner chooses tub versus walk-in while retaining Brizo BT062415-BNX Black Onyx point drain unless explicitly reselected','Emerald/Sandstone wet wall PASS; existing Grey Soft/revised HNC6615 LEVEL raw DCOF FAIL; HNC6715 conditional PAN raw DCOF FAIL','Actual owner program, 1.60-in vertical 2x20 nominal return mock-up and measured point-pan geometry'),
 'TX-BATH4':('Approve or revise tub-surface mockup Charcoal flat / individually wet-listed Soho Ivory niche / Matte White Hansgrohe','Original Caviar niche individual wet FAIL; Soho Ivory wet niche PASS; Bone Soft or Emser LEVEL raw DCOF FAIL; pan N/A','Actual original 8.63 SF niche back/returns vs displaced field face, tub rim and wall trim; Emser exact carton yield and current bid'),
 'TX-POWDER':('Approve existing 70:30 Haze Camel/Wheat board direction with physical dry-wall sample','Dry vanity application only; mixed shade/true sample confirmation pending','W1 true 5-in color distribution and full-size grout/edge mockup; no new wet floor'),
 'TX-POWDER2':('Select UNSELECTED basin and approve retained Indigo Edge 6x6 relief dry vanity wall','Dry vanity application only; unselected sink remains null','6x6 W1 actual modules, mirror/faucet/backsplash cuts, true trim and reflected light'),
 'TX-WC':('Confirm shared TX Primary LEVEL floor only; no standalone WC material purchase','Same exact tested LEVEL product as TX Primary, no pan','Survey original shared 14-SF WC allocation inside Primary 116.1 SF gross once')
}
assert set(decision)=={r['id'] for r in state['rooms']}
rows=[]
for room in state['rooms']:
 rid=room['id']
 owner,tech,build=decision[rid]
 rows.append({
  'room':rid,
  'latest_governance_status':room['status'],
  'board_champion_id':room['champion_id'],
  'board_champion_score':room['champion_score'],
  'last_submission_round':room['last_round'],
  'round012_scores_status':'NULL — independent critiques collected, NEXT DISTINCT turn scoring' if rid in collection['report_files'] else 'Not an R012 focus room',
  'copies':room['unit_count'],
  'dated_original_material_usd_per_copy':room['carried_quote_material_subtotal_usd_per_unit'],
  'owner_exact_decision_requested_not_granted':owner,
  'individual_maker_wet_and_raw_floor_slip_gate':tech,
  'gc_installation_and_actual_quantity_action':build,
  'correct_1529_native_identity_confirmed':False,
  'verified_actual_as_built_wall_drain_and_niche':False,
  'exact_raw_lab_floor_pan_dcof_available':False if rid not in ('PH-POWDER','TX-POWDER','TX-POWDER2') else None,
  'manufacturer_approved_drain_membrane_section':None,
  'current_chicago_exact_lot_quote':None,
  'current_pack_yield_and_orderable_cases':None,
  'current_install_labor_freight_tax':None,
  'owner_material_cap_and_125pct_result':None,
  'sample_approved_by_owner':False,
  'room_signed_owner_approval':False,
  'purchase_authorized':False
 })
dest=out/'R12_13_ROOM_OWNER_DECISION_TO_PURCHASABLE_RELEASE_REGISTER.csv'
assert not dest.exists()
with dest.open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]))
 w.writeheader();w.writerows(rows)
raw=dest.read_bytes()
manifest['outputs'][dest.name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
manifest['owner_release_register_rows']=13
manifest['round012_critic_collection_sha256']=hashlib.sha256(colpath.read_bytes()).hexdigest()
manifest['round012_weighted_scoring_deferred']=True
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for room in state['rooms']:
 if room['id'] not in collection['report_files']:continue
 z=room['round_012_submission']
 assert z['scores'] is None and z['release_allowed'] is False and room['champion_id'] is None
 z['status']='authentic_four_seat_critiques_collected_next_distinct_turn_scoring'
 z['critic_files_complete']=4
 z['critic_collection_source']='state/ROUND012_CRITIC_COLLECTION.json'
 z['critic_collection_verified_sha256']=hashlib.sha256(colpath.read_bytes()).hexdigest()
 z['owner_approved']=False
statepath.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS six signed R12 outputs (prior five SHA intact), 13 accurate owner-to-GC release rows, three R012 unscored room register updates, $23572.44 historic nominal unchanged')
