"""One-time auditable R19 original manufacturer color numeric lab-summary source action."""
from pathlib import Path
import hashlib,json,csv
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
H="## R19 new manufacturer third-party ANSI A326.3 color numeric report lead and original lab/specimen distinction — 2026-11-06"
assert H not in L.read_text(encoding="utf-8")
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
D=R/"deliverables/integrated-r19-manufacturer-wet-evidence-grades"
M=D/"MANIFEST.json"
assert h(M)=="8de01474d0c681ee61ba8d69ea7d4ef50aa2b3d76cbb819b77867eb9f58187a8"
m=json.loads(M.read_text(encoding="utf-8"))
assert len(m["outputs"])==4 and m["new_maker_color_numeric_records"]==7
assert m["room_technical_lab_closure_requests"]==13
assert not m["source_primary_raw_lab_report_available"]
assert m["Zia_is_selected_for_current_1529_room"] is False
assert m["historical_four_unit_tile_material_usd"]=="23572.44"
assert m["original_15pct_waste_embedded_once"]
assert not m["owner_approval"] and not m["GC_release"] and not m["procurement_release"]
assert not (S/"ROUND014_SCORING.json").exists() and not (S/"ROUND015_SCORING.json").exists()
body=chr(10)+H+chr(10)+chr(10)
body+="- Advanced manufacturer numeric slip evidence beyond mere bounds: independently located and visually inspected the original Zia Tile Cantera installation/specification PDF (https://support.ziatile.com/hc/en-us/article_attachments/25221619136148) manufacturer table. It reports seven color-specific ANSI A326.3 decimal DCOF values Acacia .54, Badlands .54, Black Rock .55, Mesa .63, Sierra .57, Volcan .58, Yuma .53, and credits third-party **SGS TEC Services**. Unlike brochure Target >=.42 or merchant 0.66, this has maker color identity and laboratory attribution. However it still does **not** include original SGS specimen certificate ID, exact tested product SKU/size/finish/date, wet tested liquid/service treatment, sealer and final installed state, so it does **NOT** satisfy the project's strict raw individual wet LEVEL/PAN lab release gate. No Cantera tile selected or substituted.\n"
body+="- The same original maker PDF documents nominal 0.75in-thick 24x12 cantera in 9.70 SF/72 lb cases, natural lava-stone field sealing/patina requirements, a separate natural stone 15–20% cut/breakage overage and challenging GC thresholds/load/finish floor elevations; slope shower PAN geometry and 48in LINEAR drains not verified for heavy large tile. New material can only be evaluated against measured new net field and once-approved waste, never original $23,572.44 historic 15%-included gross multiplied twice. This is no Chicago installed bid or stock confirmation.\n"
body+="- Signed additive R19 four-file evidence package, manifest SHA "+h(M)+" has seven source-specific exact-color DCOF vs raw-laboratory HOLD rows and thirteen room-by-room manufacturer original raw lab/specimen/wet WALL/NICHE/LEVEL/PAN request rows. Read-only verifier PASS all SHA/bytes, 7 actual public manufacturer numbers and 13 room applicability, TUB PAN N/A, dry powders N/A, inherited WCs, Primary LINEAR separate, PH4 POINT and Bath3 conditional owner WALK-IN. All raw report/quote/procurement fields NULL/FALSE. R17/R18 signed output, R014/R015 frozen candidate source SHA preserved.\n"
body+="- Reviewer succession trigger: last standing independent non-Pro worker-14 returned actual R18 CONTINUE then its state became FINISHED / revivable=false. To preserve **one** independent live non-Pro Reviewer rather than create a duplicate, a single successor worker-15 GPT-6 Thinking xhigh was invited and is independently auditing previous source and worker-9 failure; successor verdict not yet recorded at this checkpoint. Original DESIGN worker-9 remains FAILED after two unclaimed browser revivals and explicit further message returned no longer listening. Do not invent or dispatch alternative R014 DESIGN files without explicit governance authorization. Entire 13-room goal OPEN.\n"
with L.open("a",encoding="utf-8",newline="") as f:f.write(body)
print("PASS R19 manufacturer 7 color/13 raw lab request actual source signed, predecessor SHA preserved, independent successor preflight pending, historic $23572.44 and zero approvals logged")
