# -*- coding: utf-8 -*-
r"""Revit 2025 IronPython: conservative per-face Bolla finish candidate.

Prime-only execution in isolated pyRevit 2025:
 D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\build_bolla_bg_r03_face_finish_fix01.py" --revit=2025

R03 PARTIAL FINISH ONLY. Unknown cord-entry collar faces 2..5 on element
7721 remain unassigned. Never approve as an exact complete manufacturer finish.
No source file is saved. Distinct output guarded against overwrite.

FIX01: the source already has intentional painted glass (4435:1742,
5101:8722). Preserve each original IsPainted and GetPaintedMaterial result,
and require source-unpainted state on every metal face to be painted.
No blanket zero-paint assumption.
"""
import os
import sys
import json
import hashlib
import math
import traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

B = r'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016'
SOURCE = os.path.join(B, 'candidates', 'Kuzco_Bolla_PD3106_BG_R2025_IES_R02.rfa')
MAP = os.path.join(B, 'qa', 'bolla_bg_r03_face_signatures_fix02.json')
IES = os.path.join(B, 'sources', 'photometry', 'PD3106-BG - Bolla.IES')
OUT = os.path.join(B, 'candidates', 'Kuzco_Bolla_PD3106_BG_R2025_IES_FINISH_R03_PARTIAL.rfa')
RECEIPT = os.path.join(B, 'qa', 'bolla_bg_r03_partial_finish_receipt.json')
SOURCE_HASH = '1d107108de7cf0a40562e764e5e73c8a4ae935861b1a3fc86f0e60a481b86c5d'
IES_HASH = '9e9f70e2eecc3b1c4130bea2f3fcb3c5a1798fb61363185348b635cd71737ce4'
MAP_HASH = '1530f9eebf4823cbafed732eeae83f2a0919b58b023109a2a3b6f0b437416ebf'

# ID 7721: steel canopy 6-11; black cord 0,1,12,13.
# 2-5 are unverified grommet/cord-entry fitting and remain untouched.
PLAN = {4715: {'gold': list(range(8))},
        7721: {'black': [0,1,12,13], 'gold': [6,7,8,9,10,11]}}
PRESERVE = {4435: (6,1742), 5101: (16,8722)}
GOLD = 'PHGood_Bolla_BG_Steel_APPROX'
BLACK = 'PHGood_Bolla_Black_Cord_APPROX'

def req(v,msg):
    if not v: raise RuntimeError(msg)

def hashfile(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        while True:
            b=f.read(1024*1024)
            if not b: break
            h.update(b)
    return h.hexdigest()

def iid(value):
    try: return int(value.Value)
    except: return int(value.IntegerValue)

def faces(doc,elem_id):
    elem=doc.GetElement(DB.ElementId(elem_id))
    req(isinstance(elem,DB.Revolution),'Original Revolution absent: '+str(elem_id))
    opt=DB.Options()
    opt.DetailLevel=DB.ViewDetailLevel.Fine
    opt.IncludeNonVisibleObjects=False
    opt.ComputeReferences=True
    solids=[o for o in elem.get_Geometry(opt) if isinstance(o,DB.Solid) and o.Volume>1e-12]
    req(len(solids)==1,'Solid count mismatch: '+str(elem_id))
    return elem,list(solids[0].Faces)

def edge_bounds(face):
    zs=[];rs=[]
    for loop in face.EdgeLoops:
        for edge in loop:
            c=edge.AsCurve()
            if c is None: continue
            n=1 if isinstance(c,DB.Line) else 48
            for i in range(n+1):
                p=c.Evaluate(float(i)/n,True)
                zs.append(p.Z*304.8)
                rs.append(math.sqrt(p.X*p.X+p.Y*p.Y)*304.8)
    req(len(zs)>0,'No analytic face edges')
    return (min(zs),max(zs),min(rs),max(rs))

def checkface(face,record,allowed_new_face_material=None):
    bounds=edge_bounds(face)
    published=record['analytic_edge_bounds']
    expected=[published['z_min_mm'],published['z_max_mm'],
              published['radius_min_mm'],published['radius_max_mm']]
    # Same analytical edge sampling as fix02; 0.15mm accounts for serialized
    # roundoff and subdivision differences, not changed solid geometry.
    req(max(abs(a-b) for a,b in zip(bounds,expected))<=0.15,
        'Native per-face surface geometry differs from fix02: '+str(bounds)+' vs '+str(expected))
    req(face.GetType().FullName==record['surface_class'],
        'Face surface class changed')
    req(abs(face.Area*304.8*304.8-record['area_mm2'])<=0.15,
        'Face area changed')
    # Painting may change the returned Face.MaterialElementId. For painted
    # target metal faces only, accept the precise newly assigned material ID
    # OR the original underlying ID. All other faces must match the source
    # material exactly, including both manufacturer-painted glass materials.
    original = record['original_face_material_id']
    actual = iid(face.MaterialElementId)
    permitted = [original] if allowed_new_face_material is None else [
        original, allowed_new_face_material]
    req(actual in permitted,
        'Face underlying material changed beyond authorized paint %s -> %s'
        % (str(original), str(actual)))
    if record.get('stable_reference'):
        req(face.Reference is not None and
            face.Reference.ConvertToStableRepresentation(_doc)==record['stable_reference'],
            'Stable face reference changed')

def make_material(doc,name,rgb):
    mid=DB.Material.Create(doc,name)
    mat=doc.GetElement(mid)
    mat.Color=DB.Color(*rgb)
    mat.Transparency=0
    return mat

def original_paint_state(record):
    # The fix02 read-only probe recorded these API results on the exact
    # saved IES R02 source, before any candidate edit.
    req('paint_query_error' not in record,
        'Source paint API did not resolve reliably for face %s'
        % record.get('face_index'))
    req(type(record.get('is_painted')) is bool,
        'Source IsPainted flag missing or ambiguous')
    material_id = record.get('painted_material_id')
    req(isinstance(material_id, (int, long)),
        'Source painted material ID missing or ambiguous')
    if record['is_painted']:
        req(material_id >= 0, 'Source painted face has no material')
    else:
        req(material_id == -1, 'Source unpainted face has unexpected paint ID')
    return bool(record['is_painted']), int(material_id)

def source_paint_evidence(maps):
    # Unambiguous OEM-protected glass is genuinely PAINTED; its material
    # must persist exactly. Other faces must be UNPAINTED before modification.
    for eid, count, matid in ((4435, 6, 1742), (5101, 16, 8722)):
        req(len(maps[eid]['faces']) == count,
            'Original glass face count changed')
        for row in maps[eid]['faces']:
            req(original_paint_state(row) == (True, matid) and
                row['original_face_material_id'] == matid,
                'Original OEM painted-glass identity changed: %d:%d'
                % (eid, row['face_index']))
    for eid, count in ((4715, 8), (7721, 14)):
        req(len(maps[eid]['faces']) == count,
            'Original unpainted metal face count changed')
        for row in maps[eid]['faces']:
            req(original_paint_state(row) == (False, -1) and
                row['original_face_material_id'] == -1,
                'Original bare-metal face state changed: %d:%d'
                % (eid, row['face_index']))

def verify(doc,maps,expected_painted):
    for eid in (4435,5101,4715,7721):
        elem,fs=faces(doc,eid)
        recorded=maps[eid]['faces']
        req(len(fs)==len(recorded),'Face count changed ID '+str(eid))
        for i,face in enumerate(fs):
            record=recorded[i]
            req(record['face_index']==i,
                'Recorded stable face ordering changed '+str((eid,i)))
            key=(eid,i)
            planned_material=expected_painted.get(key)
            checkface(face,record,planned_material)
            source_is_painted,source_paint_material=original_paint_state(record)
            is_painted=bool(doc.IsPainted(elem.Id,face))
            painted_material=iid(doc.GetPaintedMaterial(elem.Id,face))
            if key in expected_painted:
                req(not source_is_painted and source_paint_material==-1,
                    'Refusing to replace a pre-existing OEM face paint '+str(key))
                req(is_painted and painted_material==planned_material,
                    'Target face paint not present after edit '+str(key)+
                    ' actual '+str((is_painted,painted_material)))
            else:
                # Most importantly: original glass faces 4435/5101 are
                # PAINTED with manufacturer materials 1742/8722. Match both
                # the boolean and ID exactly; no -1 expectation on glass.
                req(is_painted==source_is_painted and
                    painted_material==source_paint_material,
                    'Protected face paint state changed '+str(key)+
                    ' from '+str((source_is_painted,source_paint_material))+
                    ' to '+str((is_painted,painted_material)))
        if eid in PRESERVE:
            req(len(fs)==PRESERVE[eid][0] and
                all(iid(f.MaterialElementId)==PRESERVE[eid][1] for f in fs),
                'Glass original material changed')

def main():
    req(sys.version_info[0]==2,'Revit IronPython 2.7 required')
    app=__revit__.Application
    req(str(app.VersionNumber)=='2025','Revit 2025 required')
    req(getattr(__revit__,'ActiveUIDocument',None) is None,'No user RVT may be open')
    for p in (SOURCE,MAP,IES):req(os.path.isfile(p),'Missing input '+p)
    req(hashfile(SOURCE)==SOURCE_HASH,'Native IES candidate SHA changed')
    req(hashfile(IES)==IES_HASH,'Official BG IES SHA changed')
    req(hashfile(MAP)==MAP_HASH,'Source face signature receipt SHA changed')
    req(not os.path.lexists(OUT) and not os.path.lexists(RECEIPT),
        'Existing output; no overwrite')
    with open(MAP,'rb') as f: ledger=json.load(f)
    req(ledger.get('schema_version')==1 and len(ledger.get('family_parts',[]))==4,
        'Unexpected face map schema')
    req(ledger.get('source_sha256')==SOURCE_HASH,'Face map input family differs')
    maps=dict((p['native_element_id'],p) for p in ledger['family_parts'])
    req(set(maps)==set([4435,5101,4715,7721]),'Face map lacks expected native IDs')
    req(len(maps[7721]['faces'])==14 and len(maps[4715]['faces'])==8,'Face groups changed')
    source_paint_evidence(maps)
    map_before=hashfile(MAP)
    doc=None; saved=None; tx=None
    try:
        doc=app.OpenDocumentFile(SOURCE)
        req(doc.IsFamilyDocument,'Source is not native family')
        req(len(list(doc.FamilyManager.Types))==1 and
            str(doc.FamilyManager.CurrentType.Name)=='Type 1','Bolla type mismatch')
        global _doc
        _doc=doc
        verify(doc,maps,{})
        tx=DB.Transaction(doc,'Bolla R03 bounded face finish')
        req(tx.Start()==DB.TransactionStatus.Started,'Cannot start transaction')
        gold=make_material(doc,GOLD,(199,164,108))
        black=make_material(doc,BLACK,(21,21,21))
        assignments={}
        for eid,roles in PLAN.items():
            elem,fs=faces(doc,eid)
            for role,ids in roles.items():
                mat=gold if role=='gold' else black
                for i in ids:
                    doc.Paint(elem.Id,fs[i],mat.Id)
                    assignments[(eid,i)]=iid(mat.Id)
        doc.Regenerate()
        # Verify original solids/materials and exact paint assignments.
        # Revit face painting should not alter topology or IES.
        verify(doc,maps,assignments)
        req(len(list(doc.GetWarnings()))==0,'Candidate Revit warnings')
        req(tx.Commit()==DB.TransactionStatus.Committed,'Transaction commit failed')
        tx=None
        opts=DB.SaveAsOptions()
        opts.MaximumBackups=1
        opts.OverwriteExistingFile=False
        req(not os.path.lexists(OUT),'Candidate appeared before SaveAs')
        doc.SaveAs(OUT,opts)
        doc.Close(False);doc=None
        saved=app.OpenDocumentFile(OUT)
        _doc=saved
        ids={}
        for mat in DB.FilteredElementCollector(saved).OfClass(DB.Material):
            if mat.Name==GOLD:ids['gold']=iid(mat.Id)
            if mat.Name==BLACK:ids['black']=iid(mat.Id)
        req(len(ids)==2,'Saved gold/black materials missing')
        expected={}
        for eid,roles in PLAN.items():
            for role,idxs in roles.items():
                for i in idxs:expected[(eid,i)]=ids[role]
        verify(saved,maps,expected)
        saved.Close(False);saved=None
        req(hashfile(SOURCE)==SOURCE_HASH and hashfile(MAP)==map_before,
            'Original input bytes changed')
        receipt={'status':'PARTIAL_FINISH_CANDIDATE_REOPENED_UNAPPROVED',
                 'release_ready':False,'source_rfa':SOURCE,'source_sha256':SOURCE_HASH,
                 'source_faces_sha256':map_before,'candidate_rfa':OUT,
                 'candidate_sha256':hashfile(OUT),
                 'gold_faces':{'4715':list(range(8)),'7721':[6,7,8,9,10,11]},
                 'black_faces':{'7721':[0,1,12,13]},
                 'unresolved_grommet_faces':{'7721':[2,3,4,5]},
                 'preserved_glass_materials':{'4435':1742,'5101':8722},
                 'preserved_source_glass_paint':{
                   '4435':{'is_painted':True,'material_id':1742,'faces':6},
                   '5101':{'is_painted':True,'material_id':8722,'faces':16}},
                 'source_paint_guard':'source IsPainted and GetPaintedMaterial matched exactly for all 44 native faces',
                 'known_limitations':['Gold/black RGB approximate, no OEM calibrated asset',
                   'Faces 2-5 of mixed Revolution have unverified cord-entry finish',
                   'Photometric web portability and appearance render not verified']}
        fd=os.open(RECEIPT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644)
        with os.fdopen(fd,'wb') as f:f.write(json.dumps(receipt,sort_keys=True,indent=2))
        print('R03_PARTIAL_FINISH '+OUT)
    finally:
        if tx is not None:
            try:tx.RollBack()
            except:pass
        if saved is not None:saved.Close(False)
        if doc is not None:doc.Close(False)

if __name__=='__main__':
    try:main()
    except Exception:
        print('BOLLA_R03_FINISH_FAILED '+traceback.format_exc())
        raise
