#!/usr/bin/env python3
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
FEATURE=ROOT/'docs/features/proactive-outcome-discovery'
CANDIDATES=['AGENTS.md','README.md','skills/coding-shape/SKILL.md','skills/coding-ship/SKILL.md','docs/harness/coding/proof.md']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,message):
 if not ok: raise AssertionError(message)
def anchors(text):
 return {re.sub(r'[^\w\- ]','',m.lower()).replace(' ','-') for m in re.findall(r'^#{1,6} +(.+?) *#*$',text,re.M)}
def main():
 frozen=json.loads((FEATURE/'evidence/frozen-proof-inputs.json').read_text())
 for rel,h in frozen.items(): require(digest(ROOT/rel)==h,'frozen input changed: '+rel)
 protected=json.loads((FEATURE/'proof/protected.json').read_text())
 for rel,h in protected.items(): require((ROOT/rel).is_file() and digest(ROOT/rel)==h,'protected input changed: '+rel)
 print('PASS frozen acceptance and earlier history/scripts/inventory')
 for rel in CANDIDATES:
  file=ROOT/rel
  for link in re.findall(r'(?<!!)\[[^]\n]*\]\(([^)]+)\)',file.read_text()):
   link=link.split(' ',1)[0].strip('<>')
   if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',link): continue
   path,sep,fragment=link.partition('#'); target=(file.parent/path).resolve() if path else file
   require(target.exists(),'missing link '+rel+': '+link)
   if fragment and target.suffix=='.md': require(fragment in anchors(target.read_text()),'missing anchor '+rel+': '+link)
 print('PASS candidate navigation')
 assessment=json.loads((FEATURE/'evidence/semantic-assessment.json').read_text())
 require(assessment['author']=='/root/outcome_proof','independent author identity')
 require(assessment['method']=='blind source-conditioned response exercise with independent assessment; not app replay','honest target')
 require(assessment['candidate_hashes']=={x:digest(ROOT/x) for x in CANDIDATES},'candidate differs from assessed snapshot')
 expected={x['id'] for x in json.loads((FEATURE/'proof/cases.json').read_text())}
 require({x['id'] for x in assessment['cases']}==expected,'scenario set mismatch')
 for case in assessment['cases']:
  require(case['verdict']=='PASS','semantic case failed: '+case['id'])
  for field in ['proposed_response','reasoning','instruction_evidence','limitations']:
   require(bool(case.get(field)),'missing reasoned evidence '+case['id']+': '+field)
 responses=FEATURE/'evidence/blind-responses.json'
 require(digest(responses)==assessment['blind_responses_sha256'],'blind response evidence changed')
 require(assessment['invariants']['verdict']=='PASS' and assessment['invariants']['reasoning'],'invariant review')
 print('PASS six independent semantic cases and invariant preservation on pinned candidate')
if __name__=='__main__':
 try: main()
 except (AssertionError,FileNotFoundError,KeyError,ValueError) as e:
  print('FAIL:',e,file=sys.stderr);sys.exit(1)
