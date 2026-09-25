import datetime,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
release=root/'release'
package=json.loads((release/'package_validation.json').read_text())
remote=[
 {'id':'1lWQV4lrHsL1TCFjxAqUKcPw4AmaGhrhw','name':'Lightology_12_Fixtures_14_Face_Based_RFAs_R2025_Rev1.zip','size':8784866,'parent':'1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W','url':'https://drive.google.com/file/d/1lWQV4lrHsL1TCFjxAqUKcPw4AmaGhrhw/view'},
 {'id':'1FE78TWmBXNUlPPgoafrYb9uJlehNllL3','name':'Lightology_12_Fixtures_Source_and_Review_R2025_Rev1.zip','size':102063827,'parent':'1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W','url':'https://drive.google.com/file/d/1FE78TWmBXNUlPPgoafrYb9uJlehNllL3/view'},
 {'id':'1iY1q9YpTYDXjeIMbxHPcGM2hSmtkat2_','name':'Lightology_14_Family_Visual_Catalog.png','size':1304029,'parent':'1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W','url':'https://drive.google.com/file/d/1iY1q9YpTYDXjeIMbxHPcGM2hSmtkat2_/view'}]
byname={r['name']:r for r in remote}
for item in package['files']:
    path=Path(item['path']);r=byname[item['name']]
    assert path.stat().st_size==r['size']==item['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
    r['local_sha256']=item['sha256'];r['size_matches']=True;r['parent_verified']=True
native=json.loads((root/'release_native_validation.json').read_text())
visual=json.loads((root/'prime_visual_review.json').read_text())
assert native['all_pass'] and visual['all_pass'] and len(native['files'])==len(visual['files'])==14
for row in native['files']:
    assert row['pass'] and hashlib.sha256(Path(row['rfa']).read_bytes()).hexdigest()==row['sha256']
record={'status':'DELIVERED_AND_VERIFIED','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accepted_rfas':14,'native_review_pass':True,'prime_visual_review_pass':True,'verification_method':'Drive Desktop reports successful uploads; direct Google Drive file metadata confirms each returned file ID, name, parent, MIME type and exact byte size. Local archives pass SHA256 and ZIP readback. Connector metadata wrapper omits md5Checksum, so no remote-checksum equality is asserted.','files':remote}
(release/'drive_delivery.json').write_text(json.dumps(record,indent=2))
package['upload_status']='uploaded; remote IDs, names, parents and sizes verified'
package['delivery_record']='drive_delivery.json'
(release/'package_validation.json').write_text(json.dumps(package,indent=2))
ledger=root/'ORCHESTRATION.md';text=ledger.read_text(encoding='utf-8-sig')
text=text.replace('Goal IN PROGRESS. Accepted 0/14; delivered 0/14.','Goal COMPLETE. Accepted 14/14; delivered 14/14. Historical progress entries below are retained; final records supersede earlier pending statuses.')
text+='\n## Final delivery\nAll14 current RFA hashes pass independent native and prime visual review. Both ZIPs pass archive readback; uploaded files are independently confirmed by Drive metadata. See release/drive_delivery.json for IDs, URLs, exact sizes and local checksums. Native slot released; no further worker wakeups or handoffs. No commits, merges or pushes.\n'
ledger.write_text(text,encoding='utf8')
(root/'REVIT_SLOT.md').write_text('CLOSED: all14 native families reviewed and delivered. No active task-native execution.\n')
log='''\n## Lightology final Drive verification - 2026-09-23\n- Drive Desktop showed all3 files Successfully uploaded and Up to date, while connector search returned no new release files. Cause of search delay is unconfirmed. Solution: use the uploaded item Copy link action, then request metadata by exact file ID. No duplicate upload or sharing-permission change was made. Resolved: all3 metadata responses confirm expected names, exact sizes and parent1WoLM7G88CPMq-7-w_dloZiqDmk7hjd7W.\n- Metadata probe using Drive v2 field title in a v3 fields selector failed400 Invalid field selection title. Corrected selector to name; direct reads succeeded. The connector transforms name to title in its displayed wrapper. md5Checksum is omitted by that wrapper even when requested; do not claim a remote checksum match. Local ZIP/SHA256 and remote size/parent verification are recorded separately.\n- Delivery complete: mainZIP1lWQV4lrHsL1TCFjxAqUKcPw4AmaGhrhw (8784866bytes), source/reviewZIP1FE78TWmBXNUlPPgoafrYb9uJlehNllL3 (102063827bytes), catalog1iY1q9YpTYDXjeIMbxHPcGM2hSmtkat2_ (1304029bytes). All14 current RFAs match independent native approval and prime visual approval. Archive bytes were not changed after upload. The final post-upload receipt is local release/drive_delivery.json.\n'''
with (root.parents[1]/'PROJECT_MEMORY.md').open('a',encoding='utf8') as f:f.write(log)
print('DELIVERY_VERIFIED: 3 remote files; 14 current RFA hashes; native and visual acceptance pass.')
for r in remote:print(r['name']+' | '+str(r['size'])+' bytes | '+r['url'])