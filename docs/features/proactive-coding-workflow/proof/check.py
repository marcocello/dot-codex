#!/usr/bin/env python3
"""Verify independently assessed forward-response evidence against fixed acceptance."""
import hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[4]
feature=root/'docs/features/proactive-coding-workflow'
p=feature/'proof'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok,why):
    if not ok: raise AssertionError(why)
try:
    frozen=json.loads((p/'acceptance-sha256.json').read_text())
    for name,value in frozen.items(): require(digest(root/name)==value, f'Frozen acceptance changed: {name}')
    evidence=feature/'evidence'
    candidate=json.loads((evidence/'candidate-sha256.json').read_text())
    required={'AGENTS.md','docs/harness/workflow.md','docs/harness/coding/rules.md','skills/coding-shape/SKILL.md','skills/coding-ship/SKILL.md','skills/coding-fix/SKILL.md','skills/coding-operate/SKILL.md'}
    require(required<=candidate.keys(),'Missing required candidate instruction hashes')
    for name,value in candidate.items(): require(digest(root/name)==value,f'Candidate changed since exercise: {name}')
    oracle=json.loads((p/'oracle.json').read_text())
    observed={}; executors=set(); response_hashes={}
    for path in sorted(evidence.glob('executor-*.json')):
        result=json.loads(path.read_text()); executors.add(result['executor'])
        require(result['candidate_sha256']==candidate, 'Executor candidate mismatch')
        response_hashes[str(path.relative_to(root))]=digest(path)
        for case in result['cases']:
            require(case['id'] not in observed,'Duplicate exercise case')
            require(bool(case['response'].strip()) and bool(case['actions']) and bool(case['stop_condition'].strip()),'Empty forward response/action trace')
            observed[case['id']]=case
    require(len(executors)>=2,'Need two independently dispatched blind executors')
    require(set(observed)==set(oracle),'Missing or unknown behavioral cases')
    assessment=json.loads((evidence/'assessment.json').read_text())
    require(assessment['author']=='/root/proactive_proof','Assessment must be independent proof author')
    require(assessment['candidate_sha256']==candidate,'Assessment candidate mismatch')
    require(assessment['response_sha256']==response_hashes,'Response changed since independent assessment')
    require(set(assessment['cases'])==set(oracle),'Incomplete assessment')
    for case,expectations in oracle.items():
        judgments=assessment['cases'][case]
        require(len(judgments)==len(expectations),f'Incomplete assertions: {case}')
        for expectation,judgment in zip(expectations,judgments):
            require(judgment['expectation']==expectation,'Oracle altered in assessment')
            require(judgment['pass'] is True and bool(judgment['evidence'].strip()), f'FAIL {case}: {expectation}')
        print(f'PASS {case}: {len(expectations)} independently assessed outcomes')
    print('PASS bounded blind forward-response exercises; not a live project rerun')
except (AssertionError,FileNotFoundError,KeyError,ValueError) as error:
    print(f'FAIL: {error}',file=sys.stderr); sys.exit(1)
