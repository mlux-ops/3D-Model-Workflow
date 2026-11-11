"""One-time evidence-quality addendum for two exact public numeral DCOF SKU leads.
Public retailer numeric display is NOT project-mandatory raw lab or supplier bid.
"""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1]
OUT=R/"deliverables/integrated-r17-numeric-product-leads"
assert not OUT.exists()
OUT.mkdir(parents=True)
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
research=R/"research/products/R17_PUBLIC_EXACT_NUMERIC_DCOF_PRODUCT_PAGE_NOT_RAW_LAB_20261106.md"
assert research.exists()
R17=R/"deliverables/integrated-r17/MANIFEST.json"
assert fp(R17)["sha256"]=="78c0849c14a83dba65023d7ede812181d7360d2c7cd00eaa2f8cc0e33927aac1"
rows=[
{"potential_room":"TX-BATH2","public_exact_sku":"TLMGAGPR12X24","public_exact_material":"TileBar New Rock Perla White 12x24 Matte","actual_item_in":"11.81 x 23.62","reported_public_DCOF":"0.66","primary_raw_lab_numeric_wet_DCOF":"","test_method":"","lab_report_id":"","item_thickness_mm":"10.5","public_case_sf":"9.68","public_retail_usd_per_sf":"9.50","public_retail_usd_per_case":"91.96","current_chicago_quoted_stock_lot":"","current_installed_GC_price":"","actual_1529_net_sf":"","approved_full_cases":"","owner_room_cap":"","source":"https://www.tilebar.com/product/new-rock-perla-white-12x24-matte-porcelain-tile.html","source_class":"PUBLIC PRODUCT PAGE ONLY, NOT RAW LAB NOR CHICAGO BID","wet_LEVEL_release":"FALSE","PAN_applicable":"N/A_DURAVIT_TUB","owner_approved":"FALSE","procurement_release":"FALSE"},
{"potential_room":"TX-BATH4","public_exact_sku":"TLMGAGFM12X24CH","public_exact_material":"TileBar New Rock Fumo Light Gray 12x24 Chiseled Matte","actual_item_in":"11.69 x 23.50","reported_public_DCOF":"0.66","primary_raw_lab_numeric_wet_DCOF":"","test_method":"","lab_report_id":"","item_thickness_mm":"10","public_case_sf":"9.68","public_retail_usd_per_sf":"9.95","public_retail_usd_per_case":"96.32","current_chicago_quoted_stock_lot":"","current_installed_GC_price":"","actual_1529_net_sf":"","approved_full_cases":"","owner_room_cap":"","source":"https://www.tilebar.com/product/new-rock-fumo-gray-12x24-chiseled-porcelain-tile.html","source_class":"PUBLIC PRODUCT PAGE ONLY, NOT RAW LAB NOR CHICAGO BID","wet_LEVEL_release":"FALSE","PAN_applicable":"N/A_DURAVIT_TUB","owner_approved":"FALSE","procurement_release":"FALSE"}
]
fn=OUT/"R17_2_EXACT_SKU_PUBLIC_NUMERIC_VS_RAW_LAB_GATES.csv"
with fn.open("w",newline="",encoding="utf-8") as h:
 w=csv.DictWriter(h,fieldnames=list(rows[0]))
 w.writeheader()
 w.writerows(rows)
for x in rows:
 assert x["reported_public_DCOF"]=="0.66" and x["primary_raw_lab_numeric_wet_DCOF"]==""
 assert x["wet_LEVEL_release"]==x["procurement_release"]=="FALSE"
 assert x["approved_full_cases"]=="" and x["current_chicago_quoted_stock_lot"]==""
 assert x["PAN_applicable"]=="N/A_DURAVIT_TUB"
start=OUT/"START_HERE_R17_NUMERIC_RESEARCH.md"
start.write_text("# R17 separate public numerical floor product leads — not certified lab\n\nRead research/products/R17_PUBLIC_EXACT_NUMERIC_DCOF_PRODUCT_PAGE_NOT_RAW_LAB_20261106.md and R17_2_EXACT_SKU_PUBLIC_NUMERIC_VS_RAW_LAB_GATES.csv. Merchant exact SKU and public displayed 0.66 are not original individual raw lab ANSI wet DCOF certificates. Both TX tub-room LEVEL floors remain blocked until raw lab method and report, exact project SKU/lot, actual 1529 geometry, vendor-verified carton, installed bid, owner and GC signatures. Frozen R015 neutral packets and entire signed R17 original are untouched. No sale or order.\n",encoding="utf-8")
files=[fn,start]
m={
 "as_of":"2026-11-06","kind":"additive two exact public SKU numeric DCOF source-quality leads not raw lab",
 "R17_signed_manifest_sha256_preserved":fp(R17)["sha256"],
 "source_research_file":str(research.relative_to(R)).replace(chr(92),"/"),
 "source_research_sha256":fp(research)["sha256"],
 "public_numeric_DCOF_indication":"0.66 each, not raw test",
 "original_raw_wet_LEVEL_lab_available":False,"PAN_applicability":"N/A_DURAVIT_TUB",
 "original_four_unit_material_usd_preserved":"23572.44",
 "frozen_round015_candidates_modified":False,"frozen_round014_candidates_modified":False,
 "owner_approval":False,"procurement_release":False,"R014_weighted_scoring":None,
 "outputs":{p.name:fp(p) for p in files}
}
(OUT/"MANIFEST.json").write_text(json.dumps(m,indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
assert all(fp(p)==m["outputs"][p.name] for p in files)
print("PASS independent exact SKU published numeric leads separate from signed R17; 2 item/price/case sources; primary raw lab/actual Chicago bid/release NULL or FALSE; R015 sources untouched")
print("LEAD_MANIFEST_SHA",fp(OUT/"MANIFEST.json")["sha256"])
