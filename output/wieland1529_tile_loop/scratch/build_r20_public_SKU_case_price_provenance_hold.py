"""Additive R20 public manufacturer-versus-retailer SKU/lot/carton price research.
No current SHB bid, no vendor communications, no original R015 candidate mutation.
"""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json
R=Path(__file__).resolve().parents[1]
S=R/"state"
D=R/"deliverables/integrated-r20-tx-tub-public-retail-and-carton-holds"
assert not D.exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
R17=R/"deliverables/integrated-r17/MANIFEST.json"
R18=R/"deliverables/integrated-r18-owner-sample-visual-and-shop/MANIFEST.json"
R19=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades/MANIFEST.json"
assert fp(R17)["sha256"]=="78c0849c14a83dba65023d7ede812181d7360d2c7cd00eaa2f8cc0e33927aac1"
assert fp(R18)["sha256"]=="c958b49e76f8f5b12b0aca267a8dfc1870527b04b12fd3714751fd024a565ebe"
assert fp(R19)["sha256"]=="145523cf3a6953a8349e49d32d1eade41df3e723737237a7119ff4f508d8cde1"
src=S/"ROUND015_SUBMISSION.json"
assert fp(src)["sha256"]=="cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8"
D.mkdir(parents=True)

rows=[
 dict(room="TX-BATH2",maker_item="Daltile White Elect EL30 12x24 Matte",brand_code="EL30",public_or_exact_SKU="EL30",
   source_type="CURRENT OFFICIAL MAKER CATALOG, NOT SALE",source_date_checked="2026-11-06",source_url="https://www.daltile.com/products/stone-look/prime/white-elect",
   published_price_per_sf_usd="",published_case_price_usd="",published_case_sf="",published_pieces_case="",
   published_country_of_origin="Mexico (maker current page)",published_grout_recommendation="1/8in (maker current page)",
   size_specific_to_current_project="YES maker catalog includes 12x24, still no exact lot or original raw lab",
   source_reliability="Maker technical identity only; Raw wet DCOF Target >=0.42 NOT exact test",
   quote_is_current_Chicagoland_supplier_bid="FALSE",verified_stock_lot_eta="FALSE",actual_1529_job_carton_confirmed="FALSE"),
 dict(room="TX-BATH2",maker_item="Daltile White Elect 12x24 Matte",brand_code="EL30",public_or_exact_SKU="EL301224J1PV",
   source_type="RETAIL PRODUCT SKU/CARTON REFERENCE; NO CURRENT PRICE",source_date_checked="2026-11-06",source_url="https://sutherlands.com/products/item/3063906/daltile-12inch-x-24-inch-white-elect-glazed-ceramic-tile-8-pieces-per-carton",
   published_price_per_sf_usd="",published_case_price_usd="",published_case_sf="17.49",published_pieces_case="8",
   published_country_of_origin="USA (retailer claims; CONFLICTS current maker Mexico)",published_grout_recommendation="3/16in (retailer claims; CONFLICTS current maker 1/8in)",
   size_specific_to_current_project="EXACT manufacturer order code visible, no current SHB lot",
   source_reliability="Retails SKU information; inventory dated 2026-10-02, stale and location non-Chicago; manufacturer version mismatch HOLD",
   quote_is_current_Chicagoland_supplier_bid="FALSE",verified_stock_lot_eta="FALSE",actual_1529_job_carton_confirmed="FALSE"),
 dict(room="TX-BATH2",maker_item="Daltile White Elect Matte 12x24",brand_code="EL30",public_or_exact_SKU="none on public listing",
   source_type="PUBLIC TRADE LIST PRICE ONLY",source_date_checked="2026-11-06",source_url="https://www.prosourcewholesale.com/products/tile/daltile/white-elect-matte_11810020755242_49623721?expandColors=true",
   published_price_per_sf_usd="4.83",published_case_price_usd="",published_case_sf="",published_pieces_case="",
   published_country_of_origin="USA (retailer catalog; maker Mexico current)",published_grout_recommendation="",
   size_specific_to_current_project="12x24 listed; not verified exact current carton/lot",
   source_reliability="Displayed ProSource list reference, NOT a confirmed project offer, NOT wholesale/net installed bid",
   quote_is_current_Chicagoland_supplier_bid="FALSE",verified_stock_lot_eta="FALSE",actual_1529_job_carton_confirmed="FALSE"),
 dict(room="TX-BATH4",maker_item="Daltile Grey Koncrete KC04 12x24 Matte",brand_code="KC04",public_or_exact_SKU="KC04 12x24",
   source_type="CURRENT OFFICIAL MAKER CATALOG, NOT SALE",source_date_checked="2026-11-06",source_url="https://www.daltile.com/products/stone-look/prime/grey-koncrete",
   published_price_per_sf_usd="",published_case_price_usd="",published_case_sf="",published_pieces_case="",
   published_country_of_origin="USA for 12x24; Mexico for separate 2x2 mosaic",published_grout_recommendation="3/16in (maker current page)",
   size_specific_to_current_project="YES manufacturer format, 3/8in nominal, no SKU lot/RAW lab",
   source_reliability="Maker Target >=0.42 is NOT actual measured raw individual lab",
   quote_is_current_Chicagoland_supplier_bid="FALSE",verified_stock_lot_eta="FALSE",actual_1529_job_carton_confirmed="FALSE"),
 dict(room="TX-BATH4",maker_item="Dal-Tile Koncrete Gray 12x24 Ceramic Matte",brand_code="KC04",public_or_exact_SKU="KC041224J1PV",
   source_type="PUBLIC RETAIL PRODUCT SPECIFIC SIZE/CODE PRICE, NON-CHICAGO",source_date_checked="2026-11-06",source_url="https://www.nfm.com/dal-tile-koncrete-gray-12-x-24-ceramic-tile-5881596/5881596.html?pview=PDP",
   published_price_per_sf_usd="3.39",published_case_price_usd="59.29",published_case_sf="17.49",published_pieces_case="",
   published_country_of_origin="",published_grout_recommendation="",
   size_specific_to_current_project="Exact order code and 12x24 matching hypothetical alternative; not current SHB quote",
   source_reliability="NFM product page Dallas-Fort Worth estimated arrival in past 2026-10-31; NOT a verified Chicago lot/ETA",
   quote_is_current_Chicagoland_supplier_bid="FALSE",verified_stock_lot_eta="FALSE",actual_1529_job_carton_confirmed="FALSE"),
 dict(room="TX-BATH4",maker_item="Daltile KC04 Grey Matte size options",brand_code="KC04",public_or_exact_SKU="KC0410X14 default displayed",
   source_type="PUBLIC RETAIL SIZE-SELECTOR PRICE NOT MATCHED TO 12x24",source_date_checked="2026-11-06",source_url="https://stoneandtileshoppe.com/products/core-fundamentals-prime-kc04-grey-matte-ceramic-tile",
   published_price_per_sf_usd="3.09",published_case_price_usd="",published_case_sf="14.25 (default 10x14 only)",published_pieces_case="15 (default 10x14 only)",
   published_country_of_origin="",published_grout_recommendation="",
   size_specific_to_current_project="NO; shown price applies to default selector, not verified selected 12x24 variant",
   source_reliability="Merchant says generic stock but cannot prove actual 12x24 selected/case or Chicago job allocation",
   quote_is_current_Chicagoland_supplier_bid="FALSE",verified_stock_lot_eta="FALSE",actual_1529_job_carton_confirmed="FALSE"),
 dict(room="TX-BATH2/TX-BATH4",maker_item="Daltile Prime Matte 12x24 multi-color selector",brand_code="BA30 default, EL30/KC04 selectable",public_or_exact_SKU="BA301224J1PV default",
   source_type="PUBLIC RETAIL DEFAULT PRODUCT PRICE NOT EXACT ALTERNATIVE",source_date_checked="2026-11-06",source_url="https://allseasonamericanflooring.com/collections/daltile/products/daltile-prime-12-x-24-matte",
   published_price_per_sf_usd="3.08 (default BA30, NOT proven EL30/KC04)",published_case_price_usd="53.87 (default BA30)",published_case_sf="17.49 (default BA30)",published_pieces_case="9 (default BA30)",
   published_country_of_origin="",published_grout_recommendation="",
   size_specific_to_current_project="NO; price and case listing may change on color selection",
   source_reliability="Cannot call $3.08 an EL30/KC04 quote; separate product SKU and color confirmation needed",
   quote_is_current_Chicagoland_supplier_bid="FALSE",verified_stock_lot_eta="FALSE",actual_1529_job_carton_confirmed="FALSE")
]
assert len(rows)==7
assert all(x["quote_is_current_Chicagoland_supplier_bid"]=="FALSE" and x["actual_1529_job_carton_confirmed"]=="FALSE" for x in rows)
with (D/"R20_7_PUBLIC_MAKER_VS_RETAIL_CODE_ORIGIN_JOINT_CARTON_PRICE_SOURCES.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]))
 w.writeheader();w.writerows(rows)
historical=list(csv.DictReader((R/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8",newline="")))
floors=[x for x in historical if x["room"] in ("TX-BATH2","TX-BATH4") and x["source_surface"]=="floor"]
assert len(floors)==2
assert {x["room"]:x["source_gross_sf_one_copy_waste_15pct_once"] for x in floors}=={"TX-BATH2":"43.7","TX-BATH4":"44.3"}
hold=[]
for f in floors:
 rid=f["room"]
 hold.append({
 "room":rid,"actual_selected_fixture":"Duravit TUB; NO tiled shower PAN; TX2 CHROME and basin UNSELECTED" if rid=="TX-BATH2" else "Duravit TUB; NO tiled shower PAN; TX4 Hansgrohe MATTE WHITE",
 "original_2026_09_03_floor_row_id":f["source_row_id"],
 "original_quote_floor_gross_SF_per_copy_with_15pct_once":f["source_gross_sf_one_copy_waste_15pct_once"],
 "original_material_floor_usd_per_copy":f["historic_usd_one_copy"],
 "conditional_NEW_floor_option":"Daltile Prime White Elect EL30 12x24 Matte Mexico" if rid=="TX-BATH2" else "Daltile Prime Grey Koncrete KC04 12x24 Matte USA grout 3/16",
 "current_exact_maker_lot_and_color_revision":"",
 "current_manufacturer_supported_RAW_wet_LEVEL_DCOF_report_id":"",
 "actual_verified_1529_net_LEVEL_floor_SF":"",
 "current_actual_approved_one_time_cut_waste_SF":"",
 "actual_vendor_confirmed_exact_SF_per_case":"",
 "actual_ORDERABLE_full_case_quantity":"",
 "current_Chicago_supplier_material_bid_ID":"",
 "current_complete_installed_waterproof_labor_GC_bid_ID":"",
 "current_shade_ETA_and_carton_allocation":"",
 "signed_owner_room_cap":"",
 "historical_source_gross_is_NOT_order_calculation":"TRUE; old source gross already includes 15%, do not double factor",
 "conditional_new_full_case_formula":"ceil((verified new NET LEVEL SF plus explicitly approved new cut waste SF)/supplier-confirmed exact alternative SKU carton SF); 0 now",
 "owner_signature":"FALSE","GC_signature":"FALSE","procurement_release":"FALSE"})
assert all(x["procurement_release"]=="FALSE" and x["actual_ORDERABLE_full_case_quantity"]=="" for x in hold)
with (D/"R20_TX2_TX4_CONDITIONAL_LEVEL_FLOOR_NET_CASE_AND_GC_BID_GATES.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(hold[0]))
 w.writeheader();w.writerows(hold)
note=[
 "# R20 — exact-size public SKU and retailer variant audit, NOT a current Chicago procurement quote",
 "",
 "**2026-11-06. PUBLIC DESK EVIDENCE ONLY.** R015 four blind candidates remain immutable and source-cleared but no four-seat critique dispatch due original DESIGN worker failure. This research does NOT change buyer selections, LAB gates, score, budget or order.",
 "",
 "## Actual product-specific retailer and manufacturer findings",
 "",
 "- **TX-BATH4** optional [NFM Dal-Tile Koncrete Gray 12×24 Matte](https://www.nfm.com/dal-tile-koncrete-gray-12-x-24-ceramic-tile-5881596/5881596.html?pview=PDP) explicitly displays manufacturer code KC041224J1PV, $3.39/SF, $59.29/carton and 17.49 SF/carton. Arithmetic $59.29/17.49 SF = $3.39/SF to displayed precision. The NFM page references a Dallas/Fort Worth expected arrival dated October 31, 2026, not a verified current Chicago job lot; do not convert to owner-installed quote or lead.",
 "- **TX-BATH2** [Sutherlands White Elect 12×24](https://sutherlands.com/products/item/3063906/daltile-12inch-x-24-inch-white-elect-glazed-ceramic-tile-8-pieces-per-carton) explicitly displays EL301224J1PV with 8 pieces and 17.49 SF/carton; maker-country and joint in that retailer listing are **USA/3/16**, which conflict with [current individual official Daltile White Elect EL30](https://www.daltile.com/products/stone-look/prime/white-elect) **Mexico/1/8**. Dated Sutherlands stock 2026-10-02 is stale and must not be treated as current Chicago stock or even the same factory revision. This is a real provenance discrepancy, not license to overwrite the source-cleared maker latest specification.",
 "- [ProSource White Elect Matte 12×24](https://www.prosourcewholesale.com/products/tile/daltile/white-elect-matte_11810020755242_49623721?expandColors=true) lists public $4.83/SF and USA but does not identify a current approved EL301224J1PV job lot/carton or local trade bid. A displayed list price is not an installed or landed price.",
 "- [Stone & Tile Shoppe KC04 Grey](https://stoneandtileshoppe.com/products/core-fundamentals-prime-kc04-grey-matte-ceramic-tile) shows $3.09/SF in a **size selector**, while the accessible page's detailed defaults and 14.25 SF carton are **KC0410X14 / 10×14**. Do not apply $3.09 or 14.25 SF to a separately selected KC041224J1PV 12×24 without actual SKU-size checkout/quote. Generic merchant In Stock wording does not prove the requested 12x24 lot or Chicago allocation.",
 "- [All Season American Flooring Daltile Prime](https://allseasonamericanflooring.com/collections/daltile/products/daltile-prime-12-x-24-matte) displays $3.08/SF and 17.49 SF/9pc case under **default BA301224J1PV**, while EL30 and KC04 are dropdown color options. This is **NOT a verified EL30 or KC04 price or carton piece count**. Do not collapse 8-vs-9 pieces without the exact factory-lot packing slip.",
 "- [Daltile official Grey Koncrete KC04](https://www.daltile.com/products/stone-look/prime/grey-koncrete) confirms current 12x24 Matte USA, 3/8 nominal and 3/16 grout, independently from Mexico 2x2 mosaic. The official page displays only **Target wet >=0.42**, NOT the actual raw measured SKU wet result; same strict hold for EL30.",
 "",
 "## Practical two-tub GC release use",
 "",
 "The original TX2 bath FLOOR row 7539583705743236 carries 43.7 GROSS SF/room and $294.98 per copy; TX4 FLOOR row 5006308915347332 carries 44.3 GROSS SF and $299.02 per copy. Both old gross quantities **already include original 15% waste ONCE**. If a NEW floor maker is eventually selected, survey actual 1529 NET LEVEL floor for the Duravit tub arrangement, add one independently approved cut allowance on that new NET only, and divide by an **actual vendor-confirmed alternative SKU/carton yield**. No old gross SF to be automatically repeated, no full shower PAN (both tubs), no new case count or delta price projected from current noncomparable retailer pages.",
 "",
 "Original four-unit total is $23,572.44 dated material ONLY; no current allowed owner room upgrade or complete installed allowance exists. R17/R18 signed 13-room project schedules and R019 third-party numeric lab research continue independently. No vendor calls, emails, accounts, carts, samples or purchase actions performed.",
 "",
 "## Required exact live dealer/factory proof to replace blank",
 "",
 "Actual current order code, color and finish, factory lot/plant/version; approved grout joint and size/caliber; individual original raw wet LEVEL DCOF lab report; exact case piece count/SF; current Chicago local supplier allocated lot/stock/ETA; quoted freight/tax; separately complete waterproof/trim/set/tub interface and labor installed GC bid; owner cap/signature and final GC/PO release. Without all these, this is public pricing RESEARCH ONLY."
]
(D/"R20_PUBLIC_ORDER_CODE_CARTON_ORIGIN_AND_RETAIL_VARIANT_CAVEATS.md").write_text("\n".join(note)+"\n",encoding="utf-8")
(D/"START_HERE_R20.md").write_text("# R20 public SKU versus checkout variant evidence\n\nTwo selected Duravit tub rooms, exact dated source SF and public SKU/variant leads only. This is NOT a current Chicago quote, seller confirmation, installed GC offer, actual source/raw wet test, owner approval or PO. Frozen R015 board and signed R17-R19 remain untouched. Verify exact factory carton and all raw LEVEL tests before estimating full cases.\n",encoding="utf-8")
files=sorted(x for x in D.iterdir() if x.is_file())
assert len(files)==4
m={
 "as_of":"2026-11-06","kind":"additive public precise code vs retailer default variant pricing case and maker country/grout provenance",
 "public_data_rows":len(rows),"two_tub_floor_conditional_release_rows":len(hold),
 "source_material_four_unit_usd":"23572.44","original_source_15pct_gross_once":True,
 "maker_EL30_current_country":"Mexico, contrasted with older retailer USA; exact lot unknown",
 "maker_KC04_current_grout":"3/16in, other older snapshots conflicting",
 "current_verified_Chicago_exact_stock":False,"actual_install_bid":False,
 "actual_RAW_measured_wet_LEVEL_lab_available":False,
 "R015_original_frozen_submission_sha":fp(src)["sha256"],
 "R17_signed_manifest_sha":fp(R17)["sha256"],
 "R18_signed_manifest_sha":fp(R18)["sha256"],
 "R19_signed_manifest_sha":fp(R19)["sha256"],
 "owner_approval":False,"GC_release":False,"procurement_release":False,
 "R014_scoring":None,"R015_scoring":None,
 "outputs":{p.name:fp(p) for p in files}}
(D/"MANIFEST.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/k)==v for k,v in m["outputs"].items())
print("PASS R20 seven maker/public SKU variant source records + two Duravit tub conditional floor case/GC bid gates, 4 outputs signed; no historic double waste/current Chicago bidder/raw lab claims")
print("R20_MANIFEST_SHA",fp(D/"MANIFEST.json")["sha256"])
