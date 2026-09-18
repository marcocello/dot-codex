#!/usr/bin/env python3
"""Current instruction-boundary checks; semantic verdict is separate authored evidence."""
import hashlib,json,re,sys,unicodedata
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
FEATURE=HERE.parent
failures=[]
def check(ok,message):
 print(('PASS ' if ok else 'FAIL ')+message)
 if not ok: failures.append(message)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def active_files():
 return sorted(set([ROOT/'AGENTS.md',ROOT/'README.md']+list((ROOT/'docs/harness').rglob('*.md'))+list((ROOT/'skills').glob('coding-*/**/*.md'))))
def candidate_hashes():
 return {str(p.relative_to(ROOT)):digest(p) for p in active_files()}
def anchors(text):
 result=set(); counts={}
 for line in text.splitlines():
  m=re.match(r'^#{1,6}\s+(.+?)\s*#*$',line)
  if m:
   title=re.sub(r'[^\w\- ]','',m[1].lower()).replace(' ','-')
   n=counts.get(title,0); counts[title]=n+1
   result.add(title+(f'-{n}' if n else ''))
 result.update(re.findall(r'(?:id|name)=["\']([^"\']+)',text))
 return result
if '--hashes' in sys.argv:
 print(json.dumps(candidate_hashes(),indent=2));sys.exit()
removed=['docs/harness/workflow.md','docs/harness/coding/rules.md','docs/harness/coding/research.md','docs/harness/safety.md']
check(all(not (ROOT/x).exists() for x in removed),'four redundant instruction files removed')
refs=list((ROOT/'docs/harness/coding').glob('*.md'))
check({p.name for p in refs}=={'proof.md','status.md','evidence.md'},'exactly three shared coding references')
lifecycle=[ROOT/f'skills/coding-{s}/SKILL.md' for s in ['shape','ship','fix','operate']]
for ref in refs:
 callers=[p for p in lifecycle if f'coding/{ref.name}' in p.read_text()]
 check(len(callers)>=2,f'{ref.name} has multiple actual lifecycle callers ({len(callers)})')
baseline=json.loads((FEATURE/'evidence/baseline.json').read_text())
core=['AGENTS.md']+removed+[str(p.relative_to(ROOT)) for p in lifecycle]+['docs/harness/coding/'+s+'.md' for s in ['proof','status','evidence']]
old=sum(baseline['word_counts'][p] for p in core)
new=sum(len((ROOT/p).read_text().split()) for p in core if (ROOT/p).exists())
check(new<=old*.75,f'core instruction words reduced at least 25% ({old} -> {new})')
oldref=sum(baseline['word_counts'][str(p.relative_to(ROOT))] for p in refs)
newref=sum(len(p.read_text().split()) for p in refs)
check(newref<=oldref*.65,f'shared reference words reduced at least 35% ({oldref} -> {newref})')
protected=json.loads((HERE/'protected.json').read_text())
changed=[s for s,h in protected.items() if not (ROOT/s).is_file() or digest(ROOT/s)!=h]
check(not changed,'scripts, inventory and earlier feature evidence unchanged'+(': '+', '.join(changed[:8]) if changed else ''))
link_errors=[]
for p in active_files():
 txt=p.read_text()
 for target in re.findall(r'\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)',txt):
  target=target.strip('<>')
  if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('/') or any(c in target for c in ['{','}']):continue
  path,sep,frag=unquote(target).partition('#'); dest=(p.parent/path).resolve() if path else p
  if not dest.exists():link_errors.append(f'{p.relative_to(ROOT)} -> {target}')
  elif sep and frag and dest.suffix=='.md' and frag not in anchors(dest.read_text()):link_errors.append(f'{p.relative_to(ROOT)} -> absent #{frag} in {path}')
check(not link_errors,'current local Markdown links and fragments resolve'+(': '+ '; '.join(link_errors[:12]) if link_errors else ''))
assessment=FEATURE/'evidence/semantic-assessment.json'
if assessment.exists():
 data=json.loads(assessment.read_text())
 check(data.get('candidate_sha256')==candidate_hashes(),'independent semantic assessment matches current instruction inputs')
 cases=json.loads((HERE/'cases.json').read_text())
 results=data.get('cases',[])
 check({c['id'] for c in results}=={c['id'] for c in cases} and all(c.get('verdict')=='PASS' and c.get('reason') for c in results),'eight independent semantic cases have reasoned PASS verdicts')
 check(data.get('author')=='/root/lean_proof' and data.get('invariant_review',{}).get('verdict')=='PASS','separate proof author reviewed complete accepted invariant preservation')
else:check(False,'independent candidate semantic assessment required')
print(f'{len(failures)} failure(s)')
sys.exit(bool(failures))
