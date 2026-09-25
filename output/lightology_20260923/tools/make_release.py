"""Create reviewed deliverables without touching source RFAs or unrelated files."""
import argparse,datetime,hashlib,json,math,os,re,shutil,textwrap,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'release'
PRIMARY=OUT/'Lightology_14_Face_Based_RFAs_R2025_Rev1'
META={
'f01':('Maverick II LED fan','Matte black','52 in sweep; 13.8 in manufacturer overall height','816712&option_id=816709','build_f01_816712.py','The exact manufacturer specification overrides the retailer 19.8 in height. Supplied 6 in downrod, 6 in canopy, 6.8 in housing and 6.88 x 1.62 in glass informed the model. Blade camber, sweep, thickness, edge shape and recessed trim details are inferred from photographs. Rotor geometry is fixed; materials are editable.'),
'f02':('FLOS IC C/W1','Brass / opal','7.9 W x 8.5 H x 11 D in','231180','build_ic_cw1.py','Printed overall dimensions govern. The opal sphere, narrow supporting arm and circular brass mount were compared with the product photograph and dimension drawing. Undimensioned arm, collar and glass wall details are reconstructed.'),
'f03':('AERIN Brenta','Bronze / white and clear glass','3.5 W x 18.5 H x 3.75 D in','1241670&option_id=1241668','build_brenta.py','Bronze option resolves the finish override in the request. Slightly flared hollow glass shells and inner diffusers follow the official photograph and source-RFA dimensions. Printed nominal envelope overrides slight reference-model differences. The backplate depth and small radii remain inferred.'),
'f04':('Forked Shade pendant','Brass; medium 9.8 in selection','9.84 dia; 18.8 body height; 37.82 installed drop in','1149899','build_forked.py','Manufacturer medium drawing gives 9.84 in shade diameter, 5.9 in shade height and 12.9 in upper assembly. The default 18 in visible cord is a chosen installation, giving 37.82 in total drop including canopy. The shade is open and hollow; fork, machined flutes and shoulder contours are photo-derived. Current retailer and legacy drawing SKUs differ; the medium size is consistent.'),
'f05':('RBW Dimple','Black anodized; amber and white-interior variants','5 dia x 3.3 projection in; 3000 K','1441643&option_id=1441619','build_dimple.py','Two RFAs cover S1 white interior and S3 amber cast glass, both black anodized, IP65 configuration and 3000 K. Concave face, rolled edge, cast-glass wall thickness and internal optics are reconstructed from the product photographs. The source color choices are retained separately.'),
'f06':('Minka Vantage','Coal; 11 in','11 dia x 1.5 H in; 3000 K','1418164&option_id=1418168','build_vantage.py','The 11 in Coal option 759-2-66A-L replaces the generic linked smaller option. The model retains the shallow coal canopy, clear acrylic rim and luminous white diffuser. Unspecified edge rounds and internal diffuser depth are inferred.'),
'f07':('Nodes Angled sconce','Burnished brass and midnight black / milk','8 W x 7.63 H x 5.5 D in','833919&option_id=833918','build_nodes_payload_expanded.py','Two RFAs cover KW1041BBS and KW1041MBK. Published backplate is 5.25 dia x .125 in; milk shade is 3.5 dia x 3.25 H in. Reflector tilt/thickness, body profile and socket details are photo/drawing-derived. Readable expanded source is authoritative; older encoded launch files are historical.'),
'f08':('Alora Cassia linear pendant','Aged gold / opal matte','48 W x 13.375 D x 6 body H in; 15.875 installed drop','1104949','build_cassia.py','Four 6 in opal globes and 11.125 x 4.375 x .875 in canopy follow the manufacturer drawing. The installed default uses one included 12 in rod per support; support spacing, bar diameters and socket collars are inferred. The 46 in maximum suspension is not the default modeled installation.'),
'f09':('Il Fanale Madame','Brass','16.33 H x 14.17 D in; 2.36 in shade diameter','1254269&option_id=1254270','build_madame.py','The dimension graphic identifies 2.36 in as the cylindrical shade diameter. Its hemispherical wall cover is larger: modeled at 4 in diameter by drawing/photo proportion, so actual overall model width is 4 in. This is disclosed inference, not a manufacturer canopy dimension. Arch, joints, bell shoulder and hollow shade follow the reference.'),
'f10':('Kelly Wearstler Covet','Antique-burnished brass / alabaster','18.25 square x 2.75 H in; 2700 K','1242580&option_id=1242586','build_covet.py','The exact linked option governs. Stone is widest at its ceiling edge and tapers inward toward the exposed underside. Two opposite-side brass retainers follow the photograph and reference solids. The companion alabaster image is cropped from the exact product image and bound to diffuse and luminous color. Natural-stone variation and material luminance are visual approximations.'),
'f11':('Terzani Mizu three-light pendant','Gold crystal; 8.7 in selection','8.66 W; 8.3 canopy dia; 19.7 installed drop in; 3000 K','1476233&option_id=1476232','build_mizu.py','The LED 3000 K option 0R03SE8A4ATE replaces the linked Xenon option. Three independently varied cast-crystal profiles and etched inner cores follow the gold reference images. Crystal contours, 3.6 in modeled width, cable locations and stagger are inferred. The fixed default uses the documented 19.7 in minimum overall installation.'),
'f12':('Visual Comfort Orbel','Natural brass / white glass','5 W x 12.9 H x 6.7 D in','813073&option_id=1279684','build_f12_orbel.py','Natural-brass 700WSOBLNB resolves the requested finish rather than the original aged-brass default. The rectangular backplate, perpendicular fin and opal globe match the source silhouette. Plate .7 in depth is published; remaining small transition and globe details are inferred.')}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size)
def load_rgb(path):
    im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);return bg.convert('RGB')
def place(canvas,path,box):
    im=ImageOps.contain(load_rgb(path),(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
    canvas.paste(im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2))
def current_rows():
    report=json.loads((ROOT/'release_native_validation.json').read_text())
    assert report['all_pass'] and len(report['files'])==14
    index={r['name']:r for r in json.loads((ROOT/'native_mesh_index.json').read_text())}
    proofs=[]
    for path in ROOT.glob('studio_render_results*.json'):
        try:proofs.extend(json.loads(path.read_text()))
        except (ValueError,TypeError):continue
    result=[]
    for r in report['files']:
        assert r['pass'] and sha(r['rfa'])==r['sha256'],r['name']+' changed after native review'
        item=index[r['name']];image=Path(item['mesh']).parent/(r['name']+'_Studio.png')
        assert image.is_file(),str(image)
        good=[p for p in proofs if p.get('rfa_sha256')==r['sha256'] and p.get('status')=='rendered' and Path(p['image'])==image]
        assert good,'No current native-mesh render proof for '+r['name']
        r=dict(r);r['folder']=item['folder'];r['studio']=str(image);r['studio_sha256']=sha(image);r['studio_proof']=good[-1]
        title,finish,dims,url,builder,notes=META[r['fixture']]
        if r['fixture']=='f05':finish='Black anodized / '+('amber' if '_Amber_' in r['name'] else 'white interior')+' / 3000 K'
        if r['fixture']=='f07':finish=('Midnight black' if 'Midnight' in r['name'] else 'Burnished brass')+' / milk glass'
        r.update(title=title,finish=finish,nominal_dimensions=dims,source_url='https://www.lightology.com/index.php?module=prod_detail&prod_id='+url,builder=builder,notes=notes)
        result.append(r)
    return result

def prepare():
    OUT.mkdir(exist_ok=True);rows=current_rows();boards=OUT/'Review_Boards';boards.mkdir(exist_ok=True)
    for first in range(0,len(rows),4):
        group=rows[first:first+4];canvas=Image.new('RGB',(1860,100+460*len(group)),'white');draw=ImageDraw.Draw(canvas)
        draw.text((30,24),'FINAL NATIVE VIEWS AND STUDIO PROOF',font=font(28,True),fill='#20252b')
        for i,row in enumerate(group):
            y=90+i*460;draw.text((30,y),row['fixture'].upper()+' | '+row['title']+' | '+row['finish'],font=font(22,True),fill='#20252b')
            native=Path(row['review_directory'])
            for j,(label,path) in enumerate([('Native front',native/(row['name']+' - 3D View - Final Front.png')),('Native side',native/(row['name']+' - 3D View - Final Side.png')),('Actual-RFA studio proof',Path(row['studio']))]):
                assert path.is_file(),str(path);place(canvas,path,(30+j*610,y+50,610+j*610,y+412));draw.text((30+j*610,y+420),label,font=font(16),fill='#555555')
        canvas.save(boards/('Prime_Review_%02d.jpg'%(first//4+1)),quality=93)
    (OUT/'catalog_metadata.json').write_text(json.dumps(rows,indent=2))
    print('REVIEW_BOARDS_READY',len(rows),'current RFA hashes and studio proofs verified')

def package():
    rows=current_rows();approval=json.loads((ROOT/'prime_visual_review.json').read_text())
    assert approval['all_pass'] and len(approval['files'])==14
    approvals={r['name']:r for r in approval['files']}
    for row in rows:
        a=approvals[row['name']];assert a['pass'] and a['rfa_sha256']==row['sha256'] and a['studio_sha256']==row['studio_sha256']
    for d in ['RFAs','Textures','Previews','QA']:(PRIMARY/d).mkdir(parents=True,exist_ok=True)
    for row in rows:
        shutil.copy2(row['rfa'],PRIMARY/'RFAs'/Path(row['rfa']).name)
        im=ImageOps.contain(load_rgb(row['studio']),(1400,1400),Image.Resampling.LANCZOS);im.save(PRIMARY/'Previews'/(row['name']+'.jpg'),quality=93)
    texture=ROOT/'f10_1242580'/'source'/'covet_alabaster_diffuse.jpg';shutil.copy2(texture,PRIMARY/'Textures'/texture.name)
    for name in ['release_native_validation.json','prime_visual_review.json']:shutil.copy2(ROOT/name,PRIMARY/'QA'/name)
    w,h=2400,2460;board=Image.new('RGB',(w,h),'white');draw=ImageDraw.Draw(board)
    draw.text((50,35),'LIGHTOLOGY | 14 FACE-BASED REVIT FAMILIES',font=font(42,True),fill='#1f2933')
    draw.text((50,97),'Revit 2025  /  Twelve fixtures  /  Fourteen selected configurations',font=font(23),fill='#58636d')
    for i,row in enumerate(rows):
        x=40+(i%4)*590;y=165+(i//4)*565
        place(board,row['studio'],(x,y,x+560,y+445))
        lines=textwrap.wrap(row['title'],31)
        for j,line in enumerate(lines[:2]):draw.text((x+10,y+451+j*28),line,font=font(23,True),fill='#20252b')
        for j,line in enumerate(textwrap.wrap(row['finish'],39)[:2]):draw.text((x+10,y+510+j*22),line,font=font(18),fill='#555555')
    draw.text((50,h-35),'Studio views use the actual saved RFA geometry. Material/light translation to Cycles is approximate.',font=font(17),fill='#666666')
    overview=OUT/'Lightology_14_Family_Visual_Catalog.png';board.save(overview);shutil.copy2(overview,PRIMARY/overview.name)
    readme='''# Lightology: 12 fixtures / 14 face-based RFAs

Release: Revit 2025, revision 1, 2026-09-23 task.

## Load and place

Extract the ZIP before use. Load the 14 files in `RFAs` with Revit's Load Family command. Place a component using **Place on Face**, selecting the wall face for sconces or the underside of a native ceiling/floor face for overhead fixtures. These are genuine face-based Lighting Fixtures families; they report WorkPlaneBased in the API and have face-hosting behavior 5. Rotate the placed instance as needed. Materials are editable through the named family type parameters.

For Covet, add the extracted `Textures` folder under **File > Options > Rendering > Additional render appearance paths**. Its alabaster image is used by both diffuse and luminous color. Revit first checks the original bound path, then its additional render-appearance search folders. Keep the companion image with the family package. The final native review verified the bound image, its hash and material persistence in a fresh project on this workstation. Autodesk instructions: https://help.autodesk.com/cloudhelp/2022/ENU/Revit-Customize/files/GUID-232814AE-2B53-4452-B6ED-379A5C721706.htm

## What is included

Fourteen final RFAs, the required alabaster texture, a visual catalog, individual preview images, a fixture/variant catalog and independent native/prime review records. The separate Source and Review archive preserves source references, native views, readable build scripts, mesh-based render evidence and historical working records. Only the RFAs in this main package are the approved release.

## Accuracy and use

All 14 current files passed native reopening, Lighting Fixtures category, face-template behavior, actual face hosting and orientation, measured geometry, every associated material parameter affecting all its assigned faces, family-to-project appearance persistence, required CCT/texture checks and zero family/project warnings. The review records identify the exact SHA-256 of each RFA. Nominal dimensions and source/inference decisions are in `FIXTURE_CATALOG.md`.

These are fixed-geometry visualization families. Suspension lengths and fan blade placement are not user-flexible dimensions; editable numeric labels do not imply a geometry flex feature. The delivered installation choices are stated in the catalog. There are no MEP connectors, electrical circuits or IES photometric sources. Material glow/CCT provides appearance, not a lighting calculation.

Product photographs, drawings and available manufacturer models guided silhouettes, proportions, openings and finish selection. Undimensioned contours, hidden details, glass thickness and exact optical response are documented reconstructions. Stone veining and handcrafted crystal forms naturally vary. Studio proofs were rendered from the actual saved RFA meshes and saved appearance inputs using Cycles; shader translation is approximate and is not a native Revit photometric-render claim. Revit Realistic viewport lighting may differ from these studio images. Covet's catalog view isolates its saved luminous-color bitmap under normalized emission to show the natural pattern; this is an appearance review, not a calibrated luminance claim.

## Important selection decisions

The exact Maverick manufacturer specification gives a 52 in sweep and 13.8 in height with the included 6 in downrod; it overrides the retailer's conflicting 19.8 in listing. Madame's listed 2.36 in width refers to the shade; the modeled larger wall canopy is 4 in by drawing proportion, explicitly inferred. Mizu uses the requested 3000 K LED option rather than the linked Xenon default. Vantage uses the 11 in Coal option; Orbel uses Natural Brass rather than the linked Aged Brass default.

The Forked default visible cord is 18 in (37.82 in total drop); Cassia uses 12 in rods (15.875 in total drop); Mizu uses its 19.7 in minimum overall installation.

## Production record

One worker was assigned to each fixture. The connector exposed model `5.6` with `xhigh`; an exact `Sol` suffix was not verifiable. Stalled-worker and review corrections were completed by the prime. No commits, merges or pushes were performed.
'''
    (PRIMARY/'README.md').write_text(readme)
    lines=['# Fixture catalog','', '| Fixture | Selected configuration | Nominal dimensions / installation | Final RFA |','|---|---|---|---|']
    for r in rows:lines.append('| '+r['title']+' | '+r['finish']+' | '+r['nominal_dimensions']+' | `'+Path(r['rfa']).name+'` |')
    for key in META:
        r=next(r for r in rows if r['fixture']==key)
        lines.extend(['','## '+key.upper()+' - '+r['title'],'',r['notes'],'','Source: '+r['source_url'],'','Builder: `'+r['folder']+'/'+r['builder']+'`'])
        (ROOT/r['folder']/'FINAL_NOTES.md').write_text('# Final release notes\n\n'+r['title']+' - '+r['finish']+'\n\n'+r['notes']+'\n\nThe current release is identified by release_native_validation.json and prime_visual_review.json. Earlier PENDING/FAIL statements in working files refer to superseded attempts. Source and history are preserved; the main release RFAs are authoritative.\n')
    (PRIMARY/'FIXTURE_CATALOG.md').write_text('\n'.join(lines)+'\n')
    review_md='# Prime acceptance\n\nAll fourteen configurations are accepted for the requested face-based visualization use. Native technical and source-image visual review are separate gates; both pass for the exact released RFA hashes.\n\nThe native review report was consolidated from the original full-set review and targeted fresh review of the final F01/F10 revisions. No superseded hash is accepted.\n\n'+ '\n'.join('- '+r['title']+' / '+r['finish']+': PASS. '+approvals[r['name']]['notes'] for r in rows)+'\n'
    (PRIMARY/'PRIME_REVIEW.md').write_text(review_md)
    manifest={'release':'Rev1','revit_version':'2025','fixture_count':12,'rfa_count':14,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[]}
    for p in sorted(PRIMARY.rglob('*')):
        if p.is_file():manifest['files'].append({'path':p.relative_to(PRIMARY).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    (PRIMARY/'MANIFEST.json').write_text(json.dumps(manifest,indent=2))
    primary_zip=OUT/'Lightology_12_Fixtures_14_Face_Based_RFAs_R2025_Rev1.zip'
    assert not primary_zip.exists(),'Release ZIP already exists; verify instead of silently replacing'
    with zipfile.ZipFile(primary_zip,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(PRIMARY.rglob('*')):
            if p.is_file():z.write(p,PRIMARY.name+'/'+p.relative_to(PRIMARY).as_posix())
    with zipfile.ZipFile(primary_zip) as z:
        assert z.testzip() is None
        assert sum(n.lower().endswith('.rfa') for n in z.namelist())==14
        for r in rows:
            data=z.read(PRIMARY.name+'/RFAs/'+Path(r['rfa']).name)
            assert hashlib.sha256(data).hexdigest()==r['sha256']
    audit_zip=OUT/'Lightology_12_Fixtures_Source_and_Review_R2025_Rev1.zip'
    assert not audit_zip.exists(),'Audit release already exists'
    audit_files=[]
    for p in ROOT.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if any(x in ['release','pdf_runtime','__pycache__'] for x in rel.parts):continue
        if p.suffix.lower() in ['.rvt','.rvt1','.pyc','.dmp','.lock','.tmp']:continue
        audit_files.append((p,'Source_and_Review/'+rel.as_posix()))
    with zipfile.ZipFile(audit_zip,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('Source_and_Review/READ_FIRST.md','# Source and review archive\n\nThis archive is the auditable working record, including manufacturer reference RFAs, superseded attempts, earlier failed validation and historical notes. **Do not load these historical/reference families as the final release.** The approved fourteen RFAs are in the separate main ZIP and are identified by release_native_validation.json and prime_visual_review.json.\n\nRuntime dependencies, caches and disposable Revit projects are excluded; all final models, source photographs/drawings, builders, native review views and studio proof records are preserved. Scripts may contain original workstation paths; they are reproducibility sources, not a click-to-run installer. Execute native builders only in a disposable task context after adjusting root paths.\n')
        for p,name in audit_files:z.write(p,name)
    with zipfile.ZipFile(audit_zip) as z:assert z.testzip() is None
    files=[]
    for p in [primary_zip,audit_zip,overview]:
        files.append({'path':str(p),'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'md5':hashlib.md5(p.read_bytes()).hexdigest()})
    result={'rfa_count':14,'all_rfa_hashes_match_native_review':True,'zip_integrity_pass':True,'files':files,'upload_status':'not yet uploaded'}
    (OUT/'package_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','package']);args=parser.parse_args()
prepare() if args.stage=='prepare' else package()