"""One-time SAME-R020/R021 independent Reviewer exact original-source and room-specific witness FIX.

Retain published contradictory 8 pieces/17.49SF as evidence, NOT orderable case.
R21 156 scopes become room-specific for all 13 without changing original program,
applicability/status, or original prior signed R014-R019 sources and scores.
"""
from pathlib import Path
import csv,json,hashlib
from decimal import Decimal

R=Path(__file__).resolve().parents[1];S=R/"state"
R20=R/"deliverables/integrated-r20-tx-tub-public-retail-and-carton-holds"
R21=R/"deliverables/integrated-r21-install-witness-sequence"
M20=R20/"MANIFEST.json";M21=R21/"MANIFEST.json"
REC=S/"ROUND020_R021_REVIEWER_EXACT_CASE_SCOPE_FIX1.json"
assert not REC.exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
old20=fp(M20);old21=fp(M21)
assert old20["sha256"] in (
 "c298f924085b22873b88e2a19850a0b7f2a3f2fcf85757b009ed607c13159fd0",
 "9559680c13f602d22fdf32ff5c3eac42e3ead515f6fcff0d2d34aa231dd676ae"
), "Only original or already-intermediate corrected R20 manifest permitted"
assert old21["sha256"]=="c277d5f8eec635150d069b73feefad040e885ebc7a2e7d5d369bcba56bb6c202"
o20=json.loads(M20.read_text(encoding="utf-8"))
o21=json.loads(M21.read_text(encoding="utf-8"))
assert all(fp(R20/n)==v for n,v in o20["outputs"].items())
assert all(fp(R21/n)==v for n,v in o21["outputs"].items())
old20_outputs={n:fp(R20/n) for n in o20["outputs"]}
old21_outputs={n:fp(R21/n) for n in o21["outputs"]}
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()

# 1: retain literally what retailer says, but explicitly mark the case data
# mutually inconsistent. An 8-piece nominal 12x24 order should have about
# 16SF at nominal full dimensions, not 17.49SF (2.18625SF/piece).
c20=R20/"R20_7_PUBLIC_MAKER_VS_RETAIL_CODE_ORIGIN_JOINT_CARTON_PRICE_SOURCES.csv"
with c20.open("r",encoding="utf-8",newline="") as f:
 rd=csv.DictReader(f);hd20=rd.fieldnames;rows20=list(rd)
assert len(rows20)==7
found=0
for row in rows20:
 if row["public_or_exact_SKU"]=="EL301224J1PV":
  assert row["published_pieces_case"]=="8" and row["published_case_sf"]=="17.49"
  assert Decimal(row["published_case_sf"])/Decimal(row["published_pieces_case"])==Decimal("2.18625")
  row["size_specific_to_current_project"]="12x24 order code shown, BUT conflicting retailer 8 pieces/17.49 SF case cannot be order basis; exact factory pack/lot documentation mandatory"
  row["source_reliability"]="RETAILER SELF-CONTRADICTION: 8 nominal 12x24 pieces total at most 16.00 SF nominal; 17.49 SF/8 = 2.18625 SF EACH > nominal 2.00 SF, physically inconsistent. Preserve both quoted source figures but SUPPRESS any use as case yield or orderable carton count pending exact factory packing/lot; older USA/3/16 also conflicts official maker Mexico/1/8."
  found+=1
assert found==1
with c20.open("w",encoding="utf-8",newline="") as f:
 wr=csv.DictWriter(f,fieldnames=hd20);wr.writeheader();wr.writerows(rows20)

book20=R20/"R20_PUBLIC_ORDER_CODE_CARTON_ORIGIN_AND_RETAIL_VARIANT_CAVEATS.md"
t=book20.read_text(encoding="utf-8")
old="- **TX-BATH2** [Sutherlands White Elect 12×24]"
assert t.count(old)==1
text=("- **MANDATORY PACKAGING HARD HOLD — exact EL301224J1PV Sutherlands entry is internally inconsistent:** "
 "The retailer publishes **8 pieces** AND **17.49 SF/carton** for nominal **12×24**. "
 "Eight nominal 12×24 pieces can occupy at most **16.00 SF** before actual-size trimming, "
 "whereas **17.49/8 = 2.18625 SF per tile**, larger than nominal 2.00 SF. "
 "**NEITHER 8 pieces NOR 17.49 SF can be adopted as confirmed orderable case yield for this exact production SKU/lot** without primary manufacturer packing specification and actual supplier allocation. "
 "Retain both contradictory source statements for audit; do not silently change the piece count to nine or calculate purchase cartons from either figure.\n"
)
if "MANDATORY PACKAGING HARD HOLD" not in t:
 t=t.replace(old,text+old)
else:
 assert t.count("MANDATORY PACKAGING HARD HOLD")==1
book20.write_text(t,encoding="utf-8")
o20["outputs"][c20.name]=fp(c20)
o20["outputs"][book20.name]=fp(book20)
M20.write_text(json.dumps(o20,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(R20/n)==v for n,v in o20["outputs"].items())
assert not o20["procurement_release"] and not o20["GC_release"] and not o20["owner_approval"]

# 2: all physical witness request text must match the room's actual program;
# change specific_evidence_scope only, keeping 156 row keys and hold status,
# source data, inspector trade and release fields byte-equivalent as values.
c21=R21/"R21_156_FIELD_INSPECTION_AND_TRADE_WITNESS_HOLD_POINTS.csv"
with c21.open("r",encoding="utf-8",newline="") as f:
 rd=csv.DictReader(f);hd21=rd.fieldnames;rows21=list(rd)
assert len(rows21)==156
old21_values={ (r["room"],r["sequence_step"]):dict(r) for r in rows21}
dry={"PH-POWDER","TX-POWDER","TX-POWDER2"}
wc={"PH-WC","TX-WC"}
linear={"PH-PRIMARY","TX-PRIMARY"}
tub={"PH-BATH2","TX-BATH2","TX-BATH4"}
conditional={"PH-BATH3","TX-BATH3"}
point={"PH-BATH4"}
assert {r["room"] for r in rows21}==dry|wc|linear|tub|conditional|point

def source_text(rid,number):
    isdry=rid in dry;iswc=rid in wc
    if number==2:
        if isdry:return "N/A — DRY vanity decorative wall only; no manufacturer wet tub/shower WALL certificate. Verify selected dry-wall tile caliber, wall/faucet backing and finish under 09/11."
        if iswc:return "N/A — WC has inherited parent Primary LEVEL floor, no tub/shower wet WALL; no wet wall listing requested."
        return "Require individual exact selected tub/shower wet WALL product SKU/color/format/finish manufacturer Wet Areas permission; flat listing cannot authorize Ribbed/Reed relief and Sapphire cannot authorize Opal."
    if number==3:
        if isdry:return "N/A — DRY vanity wall and wood floor, NO shower/tub NICHE. Confirm dry edge/mirror backing only under 09, not a wet niche certificate."
        if iswc:return "N/A — inherited Primary WC LEVEL floor, NO wet shower NICHE and no separate niche field-face order."
        if rid in linear:return "N/A — owner explicitly selected NO EXTRA PRIMARY SHOWER NICHE; two original unpriced references NO SCOPE/NO ORDER. Do not schedule wet niche maker certificate or tile."
        return "Require individual actual wet NICHE SKU/color/format/finish Wet Areas maker permission; survey niche aperture displacement ONCE, separately returns/back/sill and positive sill fall; Caviar not inherited from Soho."
    if number==4:
        if isdry:return "N/A — WOOD floor under dry powder vanity; no scheduled tiled bath LEVEL wet DCOF request."
        if iswc:
            parent=rid[:2]+"-PRIMARY"
            return "INHERITED "+parent+" bath LEVEL tile; obtain exact original maker raw measured wet LEVEL DCOF evidence with parent floor ONCE, no second WC-specific material/test/carton/PO."
        if rid in linear:return "Require exact selected Primary bath LEVEL SKU/color/size/finish original raw measured numeric wet ANSI A326.3 certificate; same evidence covers corresponding shared WC LEVEL ONCE; not proof of separate LINEAR pan."
        return "Require exact individual selected bath LEVEL tile SKU/color/size/finish original raw measured wet ANSI A326.3 lab result with sample/date/treatment; no test inherited from another room."
    if number==5:
        if rid in linear:return "Require distinct exact small-format tile original measured wet DCOF for owner-selected Brizo 48-inch LINEAR PAN separately from bath LEVEL; verify actual grate/membrane/slope and 7–18mm insert setting."
        if rid in point:return "Require independent exact small-format four-plane square POINT PAN original raw wet DCOF for selected Brizo BT062415-BNX WALK-IN; separate bath LEVEL and approved point drain/membrane."
        if rid in conditional:return "ONLY IF OWNER ELECTS WALK-IN: exact small-format four-plane square POINT PAN raw numerical measured wet lab and site-specific approved drain/liner slope; if TUB, tiled shower PAN N/A."
        if rid in tub:return "N/A — owner already selected actual Duravit TUB; NO tiled shower PAN, no POINT or LINEAR pan DCOF."
        if isdry:return "N/A — dry vanity wall and WOOD floor, no shower pan or tiled bath LEVEL floor."
        if iswc:return "N/A — WC shares parent Primary LEVEL tile, has no separately ordered shower PAN."
    if number==6:
        return {
            "PH-PRIMARY":"Confirm selected Brizo BT0734816-BNX Black Onyx 48in LINEAR with separate BR73480 rough, correct drain/grate/membrane and separate selected Duravit tub; NO added Primary niche; never a 4in square point drain.",
            "TX-PRIMARY":"Confirm selected Brizo BT0734816-BNX Black Onyx 48in LINEAR with separate BR73480 rough, correct drain/grate/membrane and separate selected Duravit tub; NO added Primary niche; never a 4in square point drain.",
            "PH-BATH4":"Confirm owner-selected WALK-IN Brizo BT062415-BNX Black Onyx 4in SQUARE POINT drain, actual four-plane slope/liner/rough; no tub or 48in linear drain.",
            "PH-BATH3":"OWNER TUB versus WALK-IN NOT SELECTED. If WALK-IN preserve selected Delta DT062412 Chrome 4in SQUARE POINT shower drain/actual rough; if TUB require future owner-selected bathtub and separate waste/overflow; Delta shower point drain never tub waste; PH basin unselected.",
            "TX-BATH3":"OWNER TUB versus WALK-IN NOT SELECTED. If WALK-IN preserve selected Brizo BT062415-BNX Black Onyx 4in SQUARE POINT shower drain; if TUB require future owner-selected bathtub and separate waste/overflow; Brizo shower point drain never tub waste.",
            "PH-BATH2":"Selected Duravit TUB and Hansgrohe MATTE WHITE, dedicated tub waste/overflow and actual flange/rough survey; no tiled shower PAN. Check source 59in tub versus 59.496in nominal W1 rough.",
            "TX-BATH2":"Selected Duravit TUB and Hansgrohe CHROME with dedicated tub waste/overflow and flange; owner BASIN UNSELECTED; no tiled shower PAN or copied Matte White TX4.",
            "TX-BATH4":"Selected Duravit TUB and Hansgrohe MATTE WHITE with dedicated tub waste/overflow and flange; no tiled PAN or TX2 CHROME/basin issue.",
            "PH-POWDER":"DRY vanity WALL: verify selected Luxe Gold WALL-mounted faucet/escutcheon flat backing and wood-floor transition; NO shower drain/rough or tiled PAN.",
            "TX-POWDER":"DRY vanity WALL: verify Haze Camel/Wheat conditional wall backing, actual selected basin/faucet rough and wood-floor junction; NO shower rough or tiled PAN.",
            "TX-POWDER2":"DRY vanity WALL: Hansgrohe Tecturis 73072341 is DECK-mounted, NOT wall-mounted; owner sink/basin UNSELECTED, hold countertop/holes and backer; wood floor, NO shower rough.",
            "PH-WC":"Shared PH-PRIMARY LEVEL tile only, toilet/flange and threshold field survey, no independently purchasable shower/tub rough, no second floor case order.",
            "TX-WC":"Shared TX-PRIMARY LEVEL tile only, toilet/flange and threshold field survey, no independently purchasable shower/tub rough, no second floor case order."
        }[rid]
    if number==7:
        if isdry:return "N/A — dry powder vanity decorative wall and wood floor, no shower/tub membrane/shop. Complete separate wall faucet/backing and dry tile setting inspection at 06/09."
        if iswc:return "N/A — WC has shared parent LEVEL floor and no tiled shower membrane or pan; inspect toilet flange and dry floor edge only."
        if rid in tub:return "Owner-selected Duravit TUB ONLY: signed exact tub waste-and-overflow/flange-to-backer waterproof wall/sill/penetration detail; do NOT design a tiled shower pan."
        if rid in conditional:return "UNSELECTED owner program: if TUB, dedicated selected tub waste/flange waterproof detail and NO pan; if WALK-IN, Delta PH or Brizo TX 4in POINT actual compatible preslope/clamped liner/weep/curb/flood shop; no cross-family substitution."
        if rid in linear:return "Selected Brizo 48in LINEAR/BR73480 rough with actual compatible manufacturer membrane, slope, curb/glass and tile-in insert/grate shop; no extra niche; no 4in square point substitution."
        return "Selected Brizo 4in SQUARE POINT WALK-IN: actual measured four-plane slope and point center, manufacturer-matched lower body/clamp/liner/weeps, curb/glass, niche waterproof and flood shop."
    if number==8:
        if isdry:return "N/A — no tub/shower fixture or membrane flood test in dry powder; inspect completed dry tile and wood-floor perimeter only."
        if iswc:return "N/A — no tub/shower membrane flood test in inherited WC floor; inspect flange/threshold and applicable plumbing separately."
        if rid in tub:return "Owner-selected Duravit TUB: witness locally required actual dedicated tub waste/overflow leak and tub flange/wet surround waterproof inspection; NO shower PAN flood test."
        if rid in conditional:return "Owner branch CONDITIONAL: if signed WALK-IN witness exact selected Delta PH or Brizo TX point-drain/liner/curb flood test under applicable manufacturer/Chicago inspector, no invented duration; if TUB witness future approved tub waste/flange leak test, no shower pan."
        if rid in linear:return "Selected Brizo 48in LINEAR: witness authorized shower drain/membrane/curb water test and document inspector/manufacturer test duration, no inferred universal Chicago time; separately verify existing selected tub waste if present."
        return "Selected PH4 Brizo 4in SQUARE POINT WALK-IN: witness approved point-drain/liner/curb flood test and record actual manufacturer/inspector duration; no tub test."
    if number==10:
        if isdry:return "Measure only dry vanity WALL net field, actual trim/cuts and wood-floor junction; source original 15% waste ONCE, actual same-SKU carton/lot after signoff; no bath floor or PAN order."
        if iswc:return "WC inherits parent Primary LEVEL gross already in material once; measure threshold joint/flange only and do NOT create WC independent tile case/order or PAN."
        if rid in tub:return "Measure wet WALL/NICHE back/returns/sill plus actual bath LEVEL net only around selected Duravit TUB; N/A PAN, actual carton/lot after approval, source old gross 15% included ONCE."
        if rid in conditional:return "Owner branch unresolved: measure wet WALL/NICHE and actual bath LEVEL; only after signed WALK-IN separately survey four-plane POINT PAN footprint and subtract from LEVEL before full-case calculation, no duplicate original total floor; TUB PAN N/A."
        if rid in linear:return "Measure wet WALL and bath LEVEL including shared WC ONCE plus separate actual 48in LINEAR PAN net, actual caliber/trim and maker case; no added Primary niche, no double floor or waste factor."
        return "Measure PH4 wet WALL/NICHE and LEVEL plus distinct actual 4-plane POINT PAN after reconciling owner 35 vs drawing 27SF; old source gross 15% once, no double floor/pan material order."
    return None

changed=[]
for row in rows21:
 rid=row["room"];n=int(row["sequence_step"][:2])
 new=source_text(rid,n)
 if new is None:continue
 before=row["specific_evidence_scope"]
 assert before
 if new!=before:
  row["specific_evidence_scope"]=new
  changed.append((rid,row["sequence_step"]))
assert len(changed)>=70,len(changed)
assert {r["room"] for r in rows21}==dry|wc|linear|tub|conditional|point
for row in rows21:
 key=(row["room"],row["sequence_step"])
 old=old21_values[key]
 assert all(row[k]==old[k] for k in hd21 if k!="specific_evidence_scope"),key
 assert row["completed"] in ("FALSE","N/A")
 assert row["procurement_release"]=="FALSE"
 assert row["original_lab_certificate_or_test_ID"]==""
 assert row["actual_1529_verified_dimension_record"]==""
 assert row["purchase_order_ID"]==""
 if row["sequence_step"].startswith("02") and row["room"] in dry|wc:
  assert "N/A" in row["specific_evidence_scope"]
 if row["sequence_step"].startswith("04") and row["room"] in tub|conditional|point:
  assert "WC" not in row["specific_evidence_scope"],key
 if row["sequence_step"].startswith("06") and row["room"]=="TX-POWDER2":
  assert "DECK-mounted" in row["specific_evidence_scope"] and "UNSELECTED" in row["specific_evidence_scope"]
with c21.open("w",encoding="utf-8",newline="") as f:
 wr=csv.DictWriter(f,fieldnames=hd21)
 wr.writeheader();wr.writerows(rows21)
o21["outputs"][c21.name]=fp(c21)
o21["original_R20_sha"]=fp(M20)["sha256"]
M21.write_text(json.dumps(o21,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(R21/n)==v for n,v in o21["outputs"].items())
assert all(fp(R21/n)==old21_outputs[n] for n in old21_outputs if n!=c21.name)
assert all(fp(R20/n)==old20_outputs[n] for n in old20_outputs if n not in (c20.name,book20.name))
assert not o21["owner_approval"] and not o21["GC_release"] and not o21["procurement_release"]
assert o21["R014_scoring"] is None and o21["R015_scoring"] is None
for rel,sha in [
 ("deliverables/integrated-r17/MANIFEST.json",o21["original_R17_sha"]),
 ("deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json",o21["original_R18_sha"]),
 ("deliverables/integrated-r19-manufacturer-wet-evidence-grades/MANIFEST.json",o21["original_R19_sha"]),
 ("state/ROUND014_SUBMISSION.json",o21["original_R014_source_sha"]),
 ("state/ROUND015_SUBMISSION.json",o21["original_R015_source_sha"])]:
 assert fp(R/rel)["sha256"]==sha,rel

receipt={
 "round":"020/021","as_of":"2026-11-06","independent_non_pro_reviewer":"worker-15",
 "original_reviewer_verdict":"FIX — R20 contradictory retailer 8 pieces versus 17.49SF for 12x24 and R21 generic inapplicable witness text",
 "R20_original_initial_manifest_sha256_before_first_stage":"c298f924085b22873b88e2a19850a0b7f2a3f2fcf85757b009ed607c13159fd0",
 "R20_manifest_before_resumed_stage":old20,"R20_manifest_after":fp(M20),
 "first_R20_retailer_conflict_correction_committed_before_R21_scope_validation_failure":old20["sha256"]=="9559680c13f602d22fdf32ff5c3eac42e3ead515f6fcff0d2d34aa231dd676ae",
 "R21_manifest_before":old21,"R21_manifest_after":fp(M21),
 "R20_outputs_before":old20_outputs,
 "R20_outputs_after":{n:fp(R20/n) for n in o20["outputs"]},
 "R21_outputs_before":old21_outputs,
 "R21_outputs_after":{n:fp(R21/n) for n in o21["outputs"]},
 "retailer_original_conflicting_piece_count":"8",
 "retailer_original_conflicting_case_sf":"17.49",
 "calculated_impossible_sf_per_nominal_12x24_piece":"2.18625",
 "supplier_confirmed_EL30_carton_yield":None,
 "retailer_case_metrics_available_to_order":False,
 "specific_scope_cells_changed":len(changed),
 "specific_scope_changed_room_steps": [{"room":rid,"step":name} for rid,name in changed],
 "non_description_156_row_keys_quantities_release_flags_unchanged":True,
 "R21_predecessor_R20_parent_sha_relinked":True,
 "older_signed_R014_R015_R017_R018_R019_unchanged":True,
 "R014_scoring":None,"R015_scoring":None,
 "owner_approval":False,"GC_release":False,"procurement_release":False,
 "global_13_room_done":False
}
REC.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS exact R20 retail 8 pieces/17.49SF impossible stated and suppressed; R21 156 witness original fields retained, "+str(len(changed))+" room-specific scope descriptions corrected; manifest predecessor SHA links and original project releases preserved")
print("R20_MANIFEST_SHA",fp(M20)["sha256"])
print("R21_MANIFEST_SHA",fp(M21)["sha256"])
print("FIX_RECEIPT_SHA",fp(REC)["sha256"])
