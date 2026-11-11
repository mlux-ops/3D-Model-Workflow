"""Apply independent R004 factual Sapphire correction and strict blind-source repairs."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
manifest=R/"state/ROUND004_SUBMISSION.json"
receipt=json.loads(manifest.read_text(encoding="utf-8"))
def change(room,letter,old,new):
 p=R/"rooms"/room/"board/round-004/candidates"/(letter+".md")
 t=p.read_text(encoding="utf-8")
 assert old in t,(room,letter,old[:130])
 p.write_text(t.replace(old,new),encoding="utf-8")
change("PH-BATH2","A","ELM Tones Sapphire 2×20 Glossy stacked; maker listing requires exact product confirmation",
 "ELM Tones Sapphire 2×20 Glossy stacked; [individual manufacturer page](https://www.elmsurfaces.com/product/sapphire-tones) lists Wet Areas; [product evidence](../../../../../research/products/elm-tones-sapphire-2x20-wet-approved.md)")
change("PH-BATH2","A","Wet Areas for Sapphire exact product not established in this packet; fail pending product-specific listing",
 "Exact Sapphire 2×20 Glossy Wet Areas manufacturer application listed: PASS for wet tub walls; installation details held")
change("PH-BATH2","A","For the source Tones Sapphire wet wall, a product-specific **Wet Areas** listing is not established in reviewed evidence; being a ceramic Walls product is insufficient in this tub enclosure.",
 "For the source **Tones Sapphire 2×20 Glossy** wet wall, [the individual ELM manufacturer page](https://www.elmsurfaces.com/product/sapphire-tones) explicitly lists **Wet Areas**, Walls and Backsplashes. This finish is **manufacturer wet-wall listed**; substrate, membrane and cuts remain unverified.")
change("PH-BATH3","C","The older Round001 three-line cost **$930.42/unit**",
 "The historical quoted three-line subtotal **$930.42/unit**")
change("PH-BATH3","B","The proposed replacement composition is a separate alternative, not an implied owner choice.",
 "No alternative finish or owner substitution is included in this specific material scheme.")
change("PH-BATH4","A","A separately [Wet Areas-listed Soho Black 2x10](../../../../../research/products/elm-soho-black-2x10.md) could be studied only as a **future substitution**, not a historic selected owner fixture.",
 "No alternate niche tile is included in this particular wall/niche composition; additional products require separate manufacturer documentation and owner review.")
change("PH-PRIMARY","C","Bone Soft plus Reed and historic two-format floor",
 "Bone Soft plus Reed and a combined Soft/Anti-Slip floor")
change("PH-PRIMARY","A","**OT01–OT04** advertise steam/rain/soaking program",
 "**OT01–OT04** advertise rain shower and soaking-bath program")
# historic blind source citations cannot tell critics to read forbidden state/ROOMS.json
for room,letter in (("PH-PRIMARY","C"),("PH-BATH2","A"),("PH-BATH3","B"),("PH-BATH4","A")):
 p=R/"rooms"/room/"board/round-004/candidates"/(letter+".md")
 t=p.read_text(encoding="utf-8")
 assert "state/ROOMS.json" in t,(room,letter)
 t=t.replace("state/ROOMS.json", "original Smartsheet quote row references above")
 p.write_text(t,encoding="utf-8")
for room,arr in receipt["candidate_files"].items():
 for letter in arr:
  p=R/"rooms"/room/"board/round-004/candidates"/(letter+".md")
  data=p.read_bytes()
  assert data
  arr[letter]={"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
manifest.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
print("PASS source wet-wall Sapphire correction, neutral role language, four historic source pointers; eight fresh SHA")
