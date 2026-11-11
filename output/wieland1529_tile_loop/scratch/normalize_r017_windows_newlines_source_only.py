"""Repair Windows double-CR introduced by same-round pre-review candidate rewrite. No critics dispatched."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
S=R/'state/ROUND017_SUBMISSION.json'
def sig(b):return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
old=S.read_bytes();sub=json.loads(old)
assert sig(old)['sha256']=='025d15e30da9a9246aa9031f886e43346676d223b49739e1e6aeecf73aadbd77'
changes=[]
for room,opts in sub['blind_source_candidates'].items():
 for letter,item in opts.items():
  path=R/item['path'];raw=path.read_bytes()
  assert sig(raw)=={k:item[k] for k in ['sha256','bytes']}
  assert b'\r\r\n' in raw,(room,letter,'expected transport artifact absent')
  good=raw.replace(b'\r\r\n',b'\n')
  lines=good.decode('utf-8').splitlines()
  assert lines[1]=='' and lines[2].startswith('This option is submitted for independent blind technical review ONLY;')
  path.write_bytes(good)
  new=sig(good)
  changes.append({'room':room,'letter':letter,'before':sig(raw),'after':new})
  item.update(new)
sub['source_revision']='same-R017 pre-review room-specific fixture paragraph AND Windows double-CR newline normalization, without changes to maker claims, private mapping, original costs, scoring or dispatch'
S.write_bytes((json.dumps(sub,indent=2)+'\n').encode('utf-8'))
after=sig(S.read_bytes())
rcpt={'round':17,'classification':'LOCAL SOURCE PRE-REVIEW HYGIENE FIX, not Reviewer FIX and no specialist exposure','old_source_sha256':sig(old)['sha256'],'new_source_sha256':after['sha256'],'eight_packet_old_new_sha_byte':changes,'private_keys_unchanged':True,'common_maker_research_unchanged':True,'no_critic_dispatched':True,'weighted_scores':None,'owner_approved':False,'purchase_release':False}
path=R/'state/ROUND017_WINDOWS_NEWLINE_NORMALIZATION_FIX.json'
assert not path.exists()
path.write_bytes((json.dumps(rcpt,indent=2)+'\n').encode('utf-8'))
print('PASS 8 R017 exact packet double-CRLF corrected into LF with old/new SHA/bytes, unchanged same-round source choices, no dispatch')
print('R017_FINAL_SHA',after['sha256'])
print('FIX_RECEIPT_SHA',sig(path.read_bytes())['sha256'])
