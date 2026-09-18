# Coding harness verification — 2026-09-15

## Skill-wiring clarification

The user clarified that the central question was whether AGENTS.md selects the correct coding skills. The follow-up made this explicit: AGENTS.md points to [one domain-skill table](../../skills/coding-workflow/SKILL.md#select-domain-skills), covering all nine specialized skills with conditional triggers. All ten coding skills are available for implicit selection in the active checkout, with no disabled overrides. Nine targeted skill-selection scenarios and the original six workflow cases passed independent assessment; current official proof passed all eight groups and fresh reviewer `/root/final_routing_review` returned PASS. Latest proof: `docs/features/coding-harness-alignment/proof/runs/20260915T145815445821Z`. See [routing evidence](../features/coding-harness-alignment/evidence/2026-09-15-skill-routing.md). The earlier setup audit below remains retained context.

## Outcome

The current installed harness passes revised, independently authored proof: all eight groups and all six independently assessed decision cases pass. Four setup defects were repaired; five setup regression tests, nine capture integration tests, the inventory doctor, and the repository gate pass. Fresh final reviewer `/root/final_harness_review` returned PASS on unchanged inputs, and current alignment verification is recorded complete.

Scope: the installed dot-codex checkout, starting at commit `325f5baea600c997371a03230cb969be843e5f6c`. Native task: `01a0a570-1b40-7a61-bc79-4c8e8bd7fd6d`. The user explicitly authorized using the current five modes and current inventory when repairing old proof. The current alignment feature was reopened, its prior acceptance archived, and its proof independently revised. No Goal, deployment, commit, or push was performed. Detailed command outputs and initial failures are retained in the native task history.

## Repairs

- Preserve shared VS Code task settings, including `inputs`, `options`, and platform overrides, when replacing generated task labels.
- Launch the default Python backend with a process task and separate arguments, so workspace paths containing spaces work. Explicit command overrides retain shell execution.
- Read task files containing comments and trailing commas, preserve string values, and reject malformed files without overwriting them. Generated output is formatted JSON and does not retain comments.
- Correct the documented Python executable path when running FastAPI from `backend/app`.

Implementation and regression tests live in [coding-prepare-environment](../../skills/coding-prepare-environment/SKILL.md). The task file format and process task behavior were checked against the [official VS Code task documentation](https://code.visualstudio.com/docs/debugtest/tasks).

## Verification

| Boundary | Result | What was exercised |
| --- | --- | --- |
| Repository gate | PASS | Structure, skill metadata/references, feature status validation, runtime availability, and diff hygiene; the gate does not run the test suite |
| Skill inventory doctor | PASS | 36 declared dependencies healthy |
| Setup generator regressions | 5 tests PASS | Existing shared configuration, repeated generation, actual backend launch in a workspace with spaces, FastAPI command selection, custom shell override, JSONC strings/comments/trailing commas, and malformed-file preservation |
| Capture CLI integration | 9 tests PASS | Proof/regression separation, command arguments, working directory, retained output, failures, timeout, interruption, containment, guarded input changes, and completion evidence |
| Alignment diagnostic checks | References and supporting journey PASS | Current Markdown links and real claim → proof → completion → reopen → failure journey, including rejection of an old PASS after a later failure |
| Additional status CLI diagnostics | 5 checks PASS | Concurrent independent claims, foreign-owner rejection, stale-state rejection, rejection of unsupported completion, and one active feature per task |
| Independent instruction review | 6 cases consistent | Ambiguous feature, ready feature without Goal authorization, typo fix, delivered-feature defect, analysis-only request, and deployed outage |
| Independent final setup review | PASS | Fresh read-only review by `/root/workflow_review` after the final parser correction |
| Revised current harness official proof | 8 groups PASS | Discovery, references, real lifecycle journey, concurrency, unfinished-attempt rejection, regression/proof separation, assessment validation, and fresh assessed behavior |
| Fresh decision exercise and assessment | 6 cases PASS | `/root/workflow_exercise` received prompts without rubrics or inherited history; `/root/current_proof_author` independently assessed responses against frozen criteria and the unchanged candidate |
| Current harness final review | PASS | Fresh `/root/final_harness_review`, distinct from implementer, proof author/assessor, and exercise agent; all 64 broader review-input hashes and 13 instruction-input hashes unchanged |

Reproducible focused commands:

```bash
python3 skills/coding-prepare-environment/tests/test_generate_tasks.py
bash docs/features/feature-verification-capture/proof/run.sh
"${CODEX_HOME:-$HOME/.codex}/scripts/skill_inventory.py" doctor
"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root "$PWD"
git diff --check
```

The initial checks were diagnostics. After the user's acceptance decision, revised official proof and supporting regressions were captured under the alignment feature. The new regression suite first failed on the reproduced setup defects. Review then caught a parser case that incorrectly accepted comma-only containers; that was repaired and the complete focused suite rerun before final setup review.

Retained current verification:

- [Official PASS](../features/coding-harness-alignment/proof/runs/20260915T143642958906Z/result.json), following [honest incomplete-evidence FAIL](../features/coding-harness-alignment/proof/runs/20260915T143431962953Z/result.json).
- [Setup regression PASS](../features/coding-harness-alignment/tests/runs/20260915T143431972447Z/result.json), [capture integration PASS](../features/coding-harness-alignment/tests/runs/20260915T143431980503Z/result.json), and [gate PASS](../features/coding-harness-alignment/tests/runs/20260915T143431990206Z/result.json).
- [Full exercise transcript](../features/coding-harness-alignment/proof/runs/20260915-verification-exercise/transcript.md), [independent assessment](../features/coding-harness-alignment/proof/runs/20260915-verification-exercise/assessment.json), and [restoration rationale](../features/coding-harness-alignment/evidence/2026-09-15-proof-restoration.md).

## Historical proof and scope

1. **Twenty historical runners reference missing `tests/unit/*.py` files.** Two of those packages are still marked `done`: `four-mode-coding-workflow` and `interaction-capture-integrity`. The core workflow runner exits 4 with `tests/unit/test_feature_status.py` missing. No history for the missing core test paths was found in the available Git log. The other 18 affected runners already have blocked status.
2. **Older portfolio acceptance is stale.** Portfolio checks require former names, an old inventory set, and old content hashes. The current alignment proof now verifies the accepted ten coding capabilities and five-mode behavior. This does not restore removed capabilities or recertify every historical feature package.
3. **Alignment behavioral evidence was renewed.** Its initial missing-assessment failure is retained; a fresh, independently assessed six-case transcript now binds to the current candidate. Old semantic results were not reused.
4. **Current alignment acceptance data is deliverable.** Exact Git ignore exceptions now include its cases/schema and archived original JSON inputs. Private run evidence remains ignored. Older portfolio JSON inputs remain ignored and that historical proof is outside current recertification.

The user's explicit decision governs the revised [current alignment contract](../features/coding-harness-alignment/FEATURE.md). The separate proof author retained the original inputs and strengthened current command checks. The six semantic prompts and rubrics remained unchanged; frozen revised inputs were unchanged through official proof.

## Limits

This audit did not execute a new material application feature through native Goal continuation, a fresh-session skill reload, VS Code UI task invocation, or deployment. Process execution used the generated command, arguments, and working directory in an isolated local fixture. The six routing cases are an independent instruction assessment, not six executed application scenarios. Current capture still provides the limited input protection documented by the workflow; this audit does not claim a stronger write boundary or complete automatic dialogue capture.
