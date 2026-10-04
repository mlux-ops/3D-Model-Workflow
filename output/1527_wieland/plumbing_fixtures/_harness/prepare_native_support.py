"""Prepare a section-local adaptation of the proven native family helper."""
from pathlib import Path
import ast
import hashlib
import json

SECTION = Path(__file__).resolve().parents[1]
REPO = SECTION.parents[2]
source = REPO / 'output/lightology_20260923/tools/native_fixture_support.py'
target = SECTION / '_harness/native_plumbing_support.py'
text = source.read_text(encoding='utf-8')
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
replacements = [
    ('recovered Lightology fixture builds', '1527 Wieland plumbing fixture builds'),
    ('OST_LightingFixtures', 'OST_PlumbingFixtures'),
    ("=='Lighting Fixtures'", "=='Plumbing Fixtures'"),
    ("os.path.join(out,basename+'_validation.json')", "os.path.join(out,'validation.json')"),
    ("else DB.XYZ(0,0,-1)", "else DB.XYZ.BasisZ"),
    ('reference=DB.HostObjectUtils.GetBottomFaces(host)[0]', "reference=(DB.HostObjectUtils.GetBottomFaces(host) if self.host=='ceiling' else DB.HostObjectUtils.GetTopFaces(host))[0]"),
    ('options.PixelSize=1800', 'options.PixelSize=1200'),
    ('    def _export(self,doc,views,prefix):\n', "    def _export(self,doc,views,prefix):\n        prefix=prefix.replace('.','_')\n"),
    ('n.startswith(self.basename)', "n.startswith(self.basename.replace('.','_'))"),
    ('self.doc.SaveAs(self.path,so);self._export(self.doc,views,self.basename)', 'self.doc.SaveAs(self.path,so)'),
    ("self._export(project,[hosted],self.basename+'_Hosted');self._export(project,native_views,self.basename+'_Isolated')", "self._export(project,native_views,self.basename+'_Isolated')"),
    ("len(self.report['evidence_files'])>=5", "len(self.report['evidence_files'])>=4"),
    ('abs(a-b)<.025', 'abs(a-b)<=1.0/25.4'),
]
for old, new in replacements:
    if old not in text:
        raise RuntimeError('Source adaptation anchor missing: ' + old)
    text = text.replace(old, new)

old = "        color('generic_diffuse',rgb)\n"
new = """        color('generic_diffuse',rgb)
        texture_path=os.path.join(self.out,'textures',label.replace(' ','_')+'.png')
        if not os.path.isfile(texture_path):raise RuntimeError('Missing material bitmap: '+texture_path)
        diffuse=asset.FindByName('generic_diffuse');diffuse.AddConnectedAsset('UnifiedBitmap')
        bitmap=diffuse.GetSingleConnectedAsset();bitmap.FindByName('unifiedbitmap_Bitmap').Value=texture_path
"""
assert old in text
text = text.replace(old, new)
old = "        self.report['reopened_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]\n"
new = """        self.report['reopened_warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
        reopened_forms=[doc.GetElement(DB.ElementId(int(part['id']))) for part in self.parts]
        reopened_bounds=measured_geometry_bounds(reopened_forms)
        self.report['reopened_bounds_in']=reopened_bounds
        self.report['actual_dimensions_after_reopen_mm']=[(reopened_bounds[i+3]-reopened_bounds[i])*25.4 for i in range(3)]
        self.report['reopen_geometry_equal']=all(abs(a-b)<1e-6 for a,b in zip(bounds,reopened_bounds))
        self.report['appearance_bindings']={}
        for label,material_id in self.report['material_ids'].items():
            material=doc.GetElement(DB.ElementId(int(material_id)))
            appearance=doc.GetElement(material.AppearanceAssetId).GetRenderingAsset()
            bitmap=appearance.FindByName('generic_diffuse').GetSingleConnectedAsset()
            path=bitmap.FindByName('unifiedbitmap_Bitmap').Value
            self.report['appearance_bindings'][label]={'path':path,'exists':os.path.isfile(path),'material_id':str(material.Id.Value)}
"""
assert old in text
text = text.replace(old, new)
old = "        self.parameters[label]=param;self.materials[label]=mat\n"
new = "        self.parameters[label]=param;self.materials[label]=mat\n        self.report.setdefault('material_ids',{})[label]=str(mat.Id.Value)\n"
assert old in text
text = text.replace(old, new)
old = "        self.report['gates']=gates;self.report['technical_pass']=all(gates.values());"
new = """        gates['reopen_geometry_equal']=self.report['reopen_geometry_equal']
        gates['diffuse_bitmaps']=all(v['exists'] for v in self.report['appearance_bindings'].values())
        self.report['gates']=gates;self.report['technical_pass']=all(gates.values());"""
assert old in text
text = text.replace(old, new)
ast.parse(text)
target.write_text(text, encoding='utf-8')
receipt = {'source': str(source), 'source_sha256': source_hash, 'target': str(target),
           'target_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
           'changes': ['Plumbing category', 'Floor top-face placement', 'Four native project previews',
                       '1 mm measured tolerance', 'Saved/reopened geometry comparison', 'Bitmap appearance binding']}
(SECTION / '_harness/native_support_receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(receipt))
