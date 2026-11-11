from pathlib import Path
import json,math
R=Path(__file__).resolve().parents[1]
reg={x["id"]:x for x in json.loads((R/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]}
letters={"PH-PRIMARY":"C","PH-BATH2":"A","PH-BATH4":"C"}
terms={
 "PH-PRIMARY":("corner shower plus freestanding/built-in tub as separately scheduled","Flat Cortar Bone plus Bone Reed/Ribbed original wet-wall relief and original PF07/ELM floor/pan blend","Brizo 48-in linear BT0734816-BNX/BR73480; Brilliance Black Onyx; NO PRIMARY NICHE","Individual Bone Reed relief lacks product-specific Wet Areas listing; PF07 floor and mosaic lack actual measured DCOF, linear format manufacturer applicability not confirmed"),
 "PH-BATH2":("actual built-in Duravit bathtub alcove","Tones Sapphire 2x20 Glossy tub wall and historical Cortar Grey Soft 12x24 level bath floor","Duravit 700332000000090; Hansgrohe Matte White; no tiled shower pan","Sapphire 2x20 Glossy maker Wet Areas PASS; Grey Soft bath floor exact measured SKU DCOF unknown FAIL"),
 "PH-BATH4":("actual WALK-IN SHOWER with selected 4-in square point drain","Flat Cortar Bone wet field and unapproved Bone Ribbed relief / Clara Caviar niche; historical Cortar quoted level/pan floor","Brizo BT062415-BNX 4-in square tile-in shower drain and Black Onyx Roccesco trim/rainhead, NOT a tub","Wet Bone Ribbed and Clara Caviar product-specific approvals absent; source 35 vs27 SF and Soft vs Anti-Slip discrepancy; no exact level/pan wet test")}
neutral="This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
for rid,letter in letters.items():
 d=R/"rooms"/rid/"board/round-010/candidates";d.mkdir(parents=True,exist_ok=True)
 f=d/(letter+".md")
 assert not f.exists(),f
 x=reg[rid];g=json.loads((R/"rooms"/rid/"geometry.json").read_text(encoding="utf-8"))
 program,original,fixtures,gates=terms[rid]
 t=["# "+rid+" — Candidate "+letter+" — complete tile design option","",neutral,"",
 "## Exact historical material/fixture scope as a neutral design alternative","",
 "Room use: "+program+". Two unit copies. Full scope: "+original+". Selected plumbing: "+fixtures+". A finish schedule does not confer owner approval or wet construction release. Historical ELM/Smartsheet source is September 3, 2026, material-only. No new finishes or replacement fixture selected.",
 "","| Surface / original source row | Tile/finish/format and current intent | Historical gross SF per one unit (15% waste included) | Original actual historic material USD; alternate USD | Technical manufacturer/slope/cost/owner gate |","|---|---|---|---|---|"]
 for z in x["carried_tile_rows"]:
  exclude=rid.endswith("PRIMARY") and z["surface"]=="accent"
  title=z["carried_description"].replace("|","/")
  gross=z["qty_sf_per_unit"];rate=z["quoted_rate_usd_per_sf"];usd=z["extended_quote_cost_usd_per_unit"]
  t.append("| "+z["surface"]+" / source "+z["smartsheet_row_id"]+" | "+title+" | "+format(gross,".2f")+" SF gross, implied pre-waste "+format(gross/1.15,".2f")+" SF arithmetic only"+(" EXCLUDED HISTORICAL NO NICHE" if exclude else "")+" | historical "+("null" if usd is None else format(usd,".2f"))+" USD/unit at "+("null" if rate is None else format(rate,".2f"))+" USD/SF; substitutes null | "+("NO PURCHASE historic unselected Primary niche" if exclude else "Specific finish wet approval / exact floor DCOF / new quote / Chicago lot and ETA HELD")+" |")
 t.append("| Grout / field perimeter / tub or curb / membrane | Actual approved material/color/profile and finish-to-metal joint NOT selected | exposed-edge LF, trim sticks, niche back and waterproofer all null | historic pricing null; current quote null | Requires real surveyed face, substrate, selected membrane/drain manufacturer compatibility, final owner choice |")
 t+=["","## Drawing-origin W elevations and cut/stick control","",
 "| Wall source tag | Provisional width × tiled height | Initial zero-offset panel study | Measurement and build risks |",
 "|---|---:|---|---|"]
 for w in g["tiled_walls"]:
  w_in=w["length"]["value"]*12;h=w["tiled_height"]["value"]*12
  mod=20 if rid=="PH-BATH2" else 24
  n=max(0,math.floor((w_in-6)/mod));end=(w_in-mod*n)/2
  t.append("| "+w["id"]+" | "+format(w_in,".2f")+" in × "+format(h,".2f")+" in | "+str(n)+" full nominal "+str(mod)+"-in horizontal modules, two "+format(end,".2f")+"-in theoretical equal edges BEFORE grout; zero-offset / horizontal tub tile or vertical primary flat | True actual tile caliber, opening, valve, window, corner/waterproof trim and neck cut null; 1529 model NOT identity verified |")
 t+=["","## Test and manufacture evidence (not released)","",
 "- Original wet-wall truth: "+gates+". Flat-finish maker wet approval does not transfer to an individual relief SKU or unlisted niche finish.",
 "- ELM Tones Sapphire Glossy individual manufacturer Wet Areas PASS for PH Bath2 only; floor slip test is independent of wall application. Exact floor raw tested DCOF value/ANSI method/test ID null and strict board criterion FAIL for every tiled bath level/pan.",
 "- Daltile Portfolio PF07/09 manufacturer Target DCOF statements are not SKU-specific actually measured values. Portfolio mosaic center-drain listed vs linear-drain unmarked in maker matrix; do not treat 2x2 as automatically linear compatible. Original large floor tile on selected 48-in Brizo linear drain cannot be presumed to slope.",
 "- Source floor gross contains shared WC in Primary and one existing 15% waste. PH Primary historic extra unpriced 7.41 SF accent/niche is expressly excluded and cannot add to wall or pan. Actual shower pan vs level/wet WC split cannot be derived from original blended floor SF. PH4 owner 35 SF vs older 27 SF and original Soft vs Anti-Slip mismatch remain owner/quote conflict.",
 "- No current Chicago exact-lot stock, dated replacement bid, lead, carton yields for original tile, installation material allowance, room budget cap, accepted wet test certificate, or owner sample and signed choice. Cost 125% >budget test NOT evaluable without actual approved per-room budget. No procurement release.",
 "","## Independent market and owner decision context","",
 "Comp evidence: 14 listings/nine distinct buildings, Old Town OT01–OT05 preferred in previous 24 months; OT01–OT04 four sales at 405 W Armitage are ONE independent design precedent, Lincoln Park and Gold Coast adjacent secondary, PH buyer target $2.8M, TX $2.7M, $2.4M–$3.2M comparator range. Listings establish amenity category, NOT actual bath tile color, finish, width or niche.", 
 "Owner decision remains null. No owner basin selection or fixture program change. Room-specific mockup: source v4 wall tile with selected Brizo BNX/Matte White reference, one grout color chip, level-floor finish and applicable pan sample. Show exact fixture locations only where plumbing provides them; openings/glass, niche returns, trim and drains whose coordinates are unverified dashed.",
 "","## Public manufacturer and local evidence source anchors","",
 "- [ELM Cortar Bone individual flat](https://www.elmsurfaces.com/product/cortar-bone), [ELM Cortar Bone Reed wet hold](../../../../research/products/elm-cortar-bone-reed-wet-hold.md), [ELM Tones Sapphire 2x20 individual](https://www.elmsurfaces.com/product/sapphire-tones), [ELM Soho wet niche collection](https://www.elmsurfaces.com/product-collection/soho).",
 "- [Daltile Portfolio source/mosaic application](../../../../research/products/R06_DALTILE_PORTFOLIO_MAKER_SALES_SHEET_APPLICATION_AND_PACKAGING.md), [versioned Prime linear alternatives](../../../../research/products/R07_DALTILE_PRIME_LINEAR_DRAIN_ALTERNATIVE_VERSIONED_EVIDENCE.md), [maker wet wall/floor research](../../../../research/products/R05_WET_LISTINGS_DCOF_INSTALLATION_EVIDENCE.md).",
 "- [Independent 14-comparable listing set](../../../../research/comps/COMPS.md) and [PH $2.8M / TX $2.7M owner price authority](../../../../state/OWNER_FEEDBACK.md).",
 "","**Design option not released.** No inventoried product can claim exact numeric measured wet DCOF or actual Chicago stock without independent test/documentation. Source dimensions remain provisional pending corrected 1529 Revit session/title/path."]
 f.write_text("\n".join(t)+"\n",encoding="utf-8")
 assert f.read_text(encoding="utf-8").splitlines()[2]==neutral
 print(rid,letter,f.stat().st_size)
