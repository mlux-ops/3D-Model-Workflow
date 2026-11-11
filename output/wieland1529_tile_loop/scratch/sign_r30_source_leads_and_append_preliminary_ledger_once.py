"""Source-only R30 additive continuation after signed R29, not a new scored board."""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1]
S=R/'state'
P=R/'research/products'
names=['R30_CAVIAR_SOHO_IVORY_TWO_BATH_WET_NICHE_FORMAT_INTERFACE_LEADS_20261106.md',
 'R30_PH4_TX4_24_NICHE_2X8_VS_2X10_WET_AND_TRIM_FORMAT_SCENARIOS.csv']
def fp(p):
 data=p.read_bytes()
 return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
assert all((P/n).is_file() for n in names)
with (P/names[1]).open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==24 and {r['room'] for r in rows}=={'PH-BATH4','TX-BATH4'}
assert all(r['purchase_authorized']=='FALSE' and r['owner_wet_wall_and_niche_selected']=='FALSE' for r in rows)
prev=fp(R/'deliverables/integrated-r29-sandstone-niche-shared-cutstock/MANIFEST.json')['sha256']
assert prev=='d3cf560c43c970e172cb2ebec187ebbc1b25472a2de86398a807cfca8300ef70'
receipt=S/'ROUND030_NEXT_SOURCE_ONLY_CAVIAR_VS_SOHO_EVIDENCE_PREPARED_NOT_REVIEWED.json'
assert not receipt.exists()
data=dict(round=30,phase='PRELIMINARY_SOURCE_ONLY_NOT_FORMAL_BLIND_BOARD',date='2026-11-06',
 focus_rooms=['PH-BATH4','TX-BATH4'],source_records=2,conditional_nominal_format_thickness_cut_cases=24,
 published_original_Clara_Caviar_nominal_thickness_mm='13',conditional_Soho_Ivory_wet_listed_nominal_thickness_mm='9.5',
 illustrative_body_difference_mm='3.5',individual_Clara_Caviar_niche_wet_authorization=None,
 Soho_Ivory_individual_wet_wall_application_listed=True,actual_Soho_orderable_SKU_stock_caliber_verified=False,
 owner_current_PH4_walkin_POINT_preserved=True,owner_TX4_tub_NO_pan_preserved=True,
 actual_verified_1529_niche_geometry=False,actual_raw_original_level_pan_numeric_labs_received=False,
 actual_1to1_maker_sample_or_mockup_created=False,owner_selection=False,
 board_neutral_candidate_source_frozen=False,critic_dispatch=False,weighted_scoring=None,pre_dispatch_reviewer_verdict=None,
 standing_original_reviewer_15='FINISHED_NONREVIVABLE',original_DESIGN_9='FAILED',
 owner_approval=False,architect_release=False,GC_release=False,supplier_reservation=False,purchasing_authorized=False,
 R29_predecessor_sha256=prev,files={n:fp(P/n) for n in names},full_13room_global_DONE=False)
receipt.write_bytes((json.dumps(data,indent=2)+'\n').encode('utf-8'))
L=S/'LEDGER.md'
old=L.read_text(encoding='utf-8')
mark='## R30 substantive next-source initiation: PH4/TX4 unlisted Caviar NICHE versus maker wet Soho format — 2026-11-06'
assert mark not in old
entry="""

## R30 substantive next-source initiation: PH4/TX4 unlisted Caviar NICHE versus maker wet Soho format — 2026-11-06

- Immediately after signed R29 local PASS, started genuinely distinct next design/GC procurement maker investigation PH-BATH4 selected WALK-IN Brizo BNX 4in square POINT / TX-BATH4 selected Duravit TUB Hansgrohe Matte White NO PAN, originally **Clara Tierra Madre Caviar 2x8 ceramic 13mm** wet niche reference with **no individual source-specific Wet Areas approval**. Official ARTO/Traditions generic wall/wet installation spec cannot independently clear specific Caviar individual maker permission. Conditional **ELM Surfaces Soho Ivory 2x10 Glossy 9.5mm** item individually lists Wet Areas; maker item/current precise orderable SKU/caliber/case/stock and owner color selection remain UNVERIFIED. Nominal body/edge difference **3.5mm** is not an installed finished height difference; waterproof/mortar/substrate/transition and owner color approval necessary.
- Created ADDITIVE maker research/products/R30_CAVIAR_SOHO_IVORY_TWO_BATH_WET_NICHE_FORMAT_INTERFACE_LEADS_20261106.md and source-linked 24 study cases in R30_PH4_TX4_24_NICHE_2X8_VS_2X10_WET_AND_TRIM_FORMAT_SCENARIOS.csv: two actual programs x original Caviar/conditional Soho x 12/16/24in hypothetical aperture widths x illustrative 1/8/3/16in grout, with prior W3 30.48in PH 111in high and TX 93in high, single displaced wall opening, back/two side/top/sill NET, side-pier and no fabricated niche counts/actual trim/caliber. New receipt state/ROUND030_NEXT_SOURCE_ONLY_CAVIAR_VS_SOHO_EVIDENCE_PREPARED_NOT_REVIEWED.json SHA+bytes refers to immutable R29 manifest d3cf560c43c970e172cb2ebec187ebbc1b25472a2de86398a807cfca8300ef70. These are preliminary true next manufacturer-specific technical material/edge studies, NOT an independently accepted neutral board, score, champion, actual 1529 model/field, test, supplier offer or PO.
- R29 original 15 signed outputs, history 13/27/25/65 and $23,572.44 original four-unit 15% inclusive, one original Caviar historic group 34.52SF/$1,163.32 two-copy PH4+TX4, no added procurement. PH4 original 35/27SF and 214.4 vendor total issue, relief wet WALL unlisted, distinct POINT four-plane PAN/raw numeric and TX4 tub flange remain open. Reviewer15 FINISHED/nonrevivable, worker9 DESIGN FAILED, source R014–R017 unscored and owner/GC/purchasing approvals FALSE. Entire global project OPEN; no field model change, vendor contact, samples ordered or Git operation.
"""
L.write_text(old+entry,encoding='utf-8')
print('PASS R30 preliminary SOURCE ONLY signed study receipt SHA',fp(receipt)['sha256'])
print('PASS R29 immutable predecessor retained',prev)
