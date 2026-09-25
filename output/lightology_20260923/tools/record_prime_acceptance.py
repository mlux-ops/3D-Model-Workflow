import json,hashlib,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
review=json.loads((root/'release_native_validation.json').read_text())
index={r['name']:r for r in json.loads((root/'native_mesh_index.json').read_text())}
notes={
'f01':'The manufacturer-height correction, three swept/twisted blades, compact motor and recessed opal disk were compared with the exact-SKU product photographs and drawing.',
'f02':'The opal sphere, slender bent brass support and round backplate match the reference silhouette and proportions.',
'f03':'The clear tubes flare toward their ends and remain hollow around the warm inner diffusers; bronze sleeve and raised plate match the source comparison.',
'f04':'The open spun shade, cast fork and linear-machined sleeve match the medium brass product; installation cord length is explicitly chosen.',
'f05':'Concave cast-glass face, rolled rim, black backplate and separate amber/white interior selections were inspected against both source images.',
'f06':'The shallow Coal cap, clear acrylic rim and white luminous disk match the 11-inch selected variant.',
'f07':'The angled reflector, milk-glass shade, pivot and backplate were reviewed in front, side and studio views for each requested finish.',
'f08':'Four opal globes, the crossing linear body, aged-gold collars and paired suspension rods follow the source drawing and photo.',
'f09':'The continuous arch, ball joints, domed wall cover and open cylindrical shade match the source. The 4-inch canopy diameter remains a disclosed proportional inference.',
'f10':'The inward-beveled slab, opposed brass retainers and exact product-derived stone bitmap are accepted. The catalog view isolates the saved luminous-color bitmap with normalized emission; native texture persistence passed, but calibrated optical equivalence is not claimed.',
'f11':'Three independently varied crystal forms, internal cores, staggered cables and white canopy follow the selected gold LED product; handmade contour and stagger details remain inferred.',
'f12':'The natural-brass plate, perpendicular fin and opal sphere match the selected option and native silhouette views.'}
rows=[]
for r in review['files']:
    assert r['pass'] and hashlib.sha256(Path(r['rfa']).read_bytes()).hexdigest()==r['sha256']
    image=Path(index[r['name']]['mesh']).parent/(r['name']+'_Studio.png')
    assert image.is_file()
    rows.append({'fixture':r['fixture'],'name':r['name'],'pass':True,'rfa_sha256':r['sha256'],'studio_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'notes':notes[r['fixture']]})
report={'all_pass':len(rows)==14,'reviewer':'Prime agent','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Source-photo/drawing comparison, clean native front/side/oblique/hosted views, actual-RFA mesh studio proofs and native technical review. Acceptance for the requested visualization use; manufacturing and photometric equivalence are not asserted.','files':rows}
(root/'prime_visual_review.json').write_text(json.dumps(report,indent=2))
p=root/'tools'/'make_release.py';s=p.read_text()
s=s.replace('Revit Realistic viewport lighting may differ from these studio images.','Revit Realistic viewport lighting may differ from these studio images. Covet\'s catalog view isolates its saved luminous-color bitmap under normalized emission to show the natural pattern; this is an appearance review, not a calibrated luminance claim.')
p.write_text(s)
(root/'ERRORS_AND_RECOVERY.md').write_text('''# Task error and recovery record

The central project memory retains the full chronology. This task archive preserves per-fixture error logs, failed/superseded validation and the final passing reports.

Resolved native issues: invalid fan angle formula; circular display-box underestimation replaced by measured native surfaces/analytic edges; tiny decorative curves below Revit tolerance; periodic crystal-loft profiles replaced by matched arc sections; face-template host obscuring exports corrected with clean isolated project views; material substitution and actual face-host checks verified independently.

Resolved preview issues: native mesh vertex API corrected; Blender custom-normal setter removed after repeat crashes; one model per render process; corrected landscape framing; fan trim, Brenta flare and Covet taper/texture refinements. Covet luminous-color preview uses normalized emission, with renderer differences explicitly disclosed.

Worker browser handoffs repeatedly timed out. Existing work was recovered; prime assistance completed stalled tasks. At the user's request no further worker wakeups, repeated instruction handoffs or new agents were used for final delivery. Exact prompt-steering warning cause is unconfirmed; no safety settings were changed.

All14 current RFAs passed the independent native review and prime visual acceptance. Main-package hashes identify final files; historical files are not delivery candidates.
''')
print('PRIME_ACCEPTANCE_RECORDED 14/14')