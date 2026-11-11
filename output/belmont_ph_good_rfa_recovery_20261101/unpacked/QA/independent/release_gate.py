"""Evaluate Belmont Penthouse Good native RFA release readiness from evidence.

Python 3, read-only. Never equates existence, filename or basic Revit load PASS
with manufacturer-accurate finish, photometry or installation approval.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa'
R=ROOT/'runner'/'receipts'

def read(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError,ValueError):
        return None

def gate(status, evidence, reason):
    return {'pass': bool(status), 'evidence': str(evidence), 'reason': reason}

def run():
    batch=read(R/'batch_final.json') or {}
    oem=read(QA/'oem_qa_r03.json') or {}
    native=read(QA/'cassia_mbcl_r02_native_qa_fix03.json') or {}
    bolla=read(QA/'bolla_bg_ies_r02_native_receipt.json') or {}
    photometry=read(ROOT/'sources'/'photometry'/'photometry_manifest.json') or {}
    by_id={x.get('id'):x for x in oem.get('results',[])}
    base=gate(bool(batch.get('all_pass') or batch.get('complete_count')==6),R/'batch_final.json','Six native save/reopen checks')
    families={
        'ALR1280090':{
            'native':gate(native.get('status')=='TECHNICAL_PASS_VISUAL_REVIEW_PENDING',QA/'cassia_mbcl_r02_native_qa_fix03.json','MBCL type and level placement'),
            'visual':gate(False,QA/'previews','Detached meshes and manufacturer appearance not approved'),
            'photometry':gate(False,QA/'previews','Four E12 sockets, lamp output is owner/selectable; electrical/photometry unverified')},
        'HIN990485':{
            'native':gate(bool((read(QA/'hin_r03_native_qa.json') or {}).get('native_qa_pass')),QA/'hin_r03_native_qa.json','R03 wall-host and measured OEM geometry'),
            'geometry':gate(bool((read(QA/'hin_r03_native_qa.json') or {}).get('dimension_within_1mm')),QA/'hin_r03_native_qa.json','R03 modeled 25 x5.5 x3 in published envelope'),
            'exact_ies_source':gate((ROOT/'sources'/'photometry'/'HIN53860BK_53860_official.ies').is_file(),ROOT/'sources'/'photometry'/'HIN53860BK_IES_VERIFICATION.json','Verified official 2024 Hinkley 53860BK IES companion'),
            'native_light_source':gate(False,QA/'hin_r04_ies_native_qa.json','R03 generic family template lacks native LightFamily; exact IES cannot yet drive a Revit emitter'),
            'photometry':gate(False,QA/'hin_r03_native_qa.json','Source-specific IES/LED lumens and electrical connector unverified')},
        'KZC1353667':{
            'native':gate(by_id.get('kzc1353667',{}).get('qa_pass'),QA/'oem_qa_r03.json','OEM source/placement geometry'),
            'ies':gate(bolla.get('status')=='REOPEN_VERIFIED_IES_BINDING_PENDING_RENDER_AND_PORTABILITY_QA',QA/'bolla_bg_ies_r02_native_receipt.json','Exact BG IES Revit readback; companion IES path required'),
            'ies_portability':gate(False,QA/'bolla_bg_ies_r02_native_receipt.json','Native IES cache absent; external companion path must be relocated/readback in target machine'),
            'material':gate(bool((read(QA/'bolla_bg_r03_partial_finish_receipt.json') or {}).get('status')),QA/'bolla_bg_r03_partial_finish_receipt.json','Identified canopy/black cable/neck face material revision saved; four tiny collar faces left neutral'),
            'visual':gate(False,QA/'previews_r05','Clear glass Shaded view hue, grommet and metallic PBR require realistic product acceptance')},
        'MFR1415595':{
            'native':gate(by_id.get('mfr1415595',{}).get('qa_pass'),QA/'oem_qa_r03.json','52-inch blade radial sweep'),
            'material':gate(bool((read(QA/'smooth_sbmb_r02_native_qa.json') or {}).get('status')=='NATIVE_MATERIAL_AND_SWEEP_PASS_VISUAL_HOLD'),QA/'smooth_sbmb_r02_native_qa.json','Identified Soft Brass and Matte Black native FreeFormElement surfaces checked'),
            'visual':gate(False,QA/'previews_r05','Unclassified imports/lens and surface appearance remain optical hold'),
            'electrical':gate(False,QA/'inspect_oem_material_parts.json','Smart fan voltage/controller/LED ratings and wiring connectors require QA')},
        'MFR201959':{
            'native':gate(by_id.get('mfr201959',{}).get('qa_pass'),QA/'oem_qa_r03.json','Original OEM placement/geometry'),
            'material':gate(bool((read(R/'vogue_ch_r02_build.json') or {}).get('status')=='SAVED_AND_REOPENED_REVIEW_CANDIDATE'),R/'vogue_ch_r02_build.json','Chrome and opal material parameters saved/reopened'),
            'preliminary_visualization':gate((read(QA/'vogue_ws3127_r03_noies_independent_qa.json') or {}).get('status','').startswith('INDEPENDENT_') or (ROOT/'candidates'/'ModernForms_Vogue_WS-3127_CH_R2025_R03.rfa').is_file(),QA/'vogue_ws3127_r03_noies_independent_qa.json','R03 2993lm/3000K generic non-OEM spherical light, no obsolete 2017 IES'),
            'photometry':gate(False,ROOT/'sources'/'photometry'/'photometry_manifest.json','Official 2017 IES differs from current published lumen/wattage')},
        'QUO1249827':{
            'native':gate(bool((read(R/'quo_r04_native_qa.json') or {}).get('native_qa_pass')),R/'quo_r04_native_qa.json','R04 ceiling face hosted and 11in envelope'),
            'visual':gate(False,QA/'previews','Clear bell silhouette is photo-interpreted, no OEM CAD surface authority'),
            'photometry':gate(False,R/'quo_r04_native_qa.json','E26 lamp/IES and electrical connector not verified')},
        'VCS833918':{
            'rfa':gate((Path(r'E:\Claude\3D-Model-Workflow\output\lightology_20260923\release\Lightology_14_Face_Based_RFAs_R2025_Rev1\RFAs\Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa')).is_file(),ROOT/'release','Reused existing accepted visualization RFA'),
            'project':gate(False,ROOT/'release','Current Penthouse installation and wiring not independently verified')},
    }
    result={'base_batch':base,'families':families,'ready_for_construction':all(all(g['pass'] for g in checks.values()) for checks in families.values()),
            'held_gates':[{ 'sku':sku,'gate':name,'reason':v['reason']} for sku,checks in families.items() for name,v in checks.items() if not v['pass']]}
    target=QA/'release_gate_latest.json'
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('CONSTRUCTION_READY:',result['ready_for_construction'],'HELD_GATES:',len(result['held_gates']))
    for row in result['held_gates']:
        print(row['sku'],row['gate'],row['reason'])

if __name__=='__main__':run()
