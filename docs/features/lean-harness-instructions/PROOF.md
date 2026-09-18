# Lean harness proof

## Done

Current instruction consumption matches FEATURE.md: central routing, focused owners, four redundant documents removed, only three justified shorter shared references, valid current navigation, and preserved earlier history and decision safeguards.

## Command

Run `docs/features/lean-harness-instructions/proof/run.sh` from the repository. Official runs use the shared `proof_run_capture.py` against this feature directory. No foreign feature proof runner is executed here.

## Scenarios and dedicated tests

`proof/check.py` reads actual AGENTS, README, current harness Markdown and coding skills. It checks required removals, the exact shared-reference set, at least two actual lifecycle callers per retained reference, >=25% aggregate reduction of the former core instruction surface and >=35% reduction of the three shared references. These reductions operationalize material/shorter, without pretending word count measures semantic quality. It resolves current inline local Markdown links and heading fragments. `proof/protected.json` pins existing scripts, skills.toml, and all earlier feature files except the mutable shared status index; these must remain byte-identical.

The independent proof author reads baseline and candidate instructions against the complete FEATURE invariants and the eight concrete requests in `proof/cases.json`. It records reasoned decisions, ownership/readership findings, limitations, and verdicts in `evidence/semantic-assessment.json`, pinning candidate hashes. The runner requires every case and the invariant review to pass on exactly the assessed files. This is an independent semantic inspection of the actual instruction boundary, not a live agent replay or keyword-based behavioral assertion.

Producer: current user request and applicable on-disk instructions. Activation: read AGENTS routing, then follow the appropriate focused skill and conditional mechanics. Consumers: agents choosing a route/procedure and humans entering through README. Read-back: actual file/fragment resolution, retained byte identities, reduced reachable text, and separately authored reasoning for each route. Fakes: none. Unsafe external edge: no external operations are performed. Central breaks caught: old mandatory guide remains, retained reference has no genuine callers, navigation points to removed owners, protected history changes, semantics drop a safeguard, or candidate changes after assessment.

## Proves / does not prove

Proves the accepted organization and independently assessed preservation at the current source/consumption boundary. Does not prove universal future model compliance, actual application implementation behavior, remote installation state, or efficacy from live reruns. The reference-use conditions and routing completeness require semantic inspection; link/word checks alone do not establish them.

## False-green risks

An assessor can miss meaning despite reviewing all declared invariants. Hash matching protects the reviewed snapshot, not trusted access control. Markdown validation covers explicit inline local links and ATX heading anchors, not arbitrary prose paths or runtime tool availability. Multiple textual callers require the independent review to determine they are justified and conditional. No test claims process wording deterministically controls a model.

## Evidence and environment

Baseline inputs are recorded in `evidence/baseline.json` and `/tmp/lean-harness-instructions-baseline`; protected histories are frozen in the proof fixture. Retain red attempt, semantic review, exact input hashes and final official capture. Python 3 and bash run locally in the shared checkout. Frozen acceptance inputs: FEATURE.md, this document, proof/run.sh, proof/check.py, proof/protected.json, proof/cases.json, and evidence/baseline.json. The later semantic assessment is authored outcome evidence, not an implementer-editable fixture. Gate and any affected script regressions remain separate supporting checks.
