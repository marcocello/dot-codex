# Independent acceptance freeze

Author: completion_proof, acting separately from the implementation owner. Authored before production implementation on 2026-09-24. FEATURE and shared proof rules supplied the behavioral oracle; the implementation owner supplied only the proposed public CLI and evidence format. No production script was edited by this author.

Fixed SHA-256 inputs:

| Path relative to the feature | SHA-256 |
| --- | --- |
| FEATURE.md | 0dc662f18f1406bc4f692fc256d34670ce8a8e7f06b303958c546c95648e6648 |
| PROOF.md | 5f6e4217c82aac61fa54d35dc3c5a0d0f38b1eaeca1d7ec3bb51e8b433bd33f4 |
| proof/run.sh | 02f87695e98ee3dc769f4ab5337cd56e10460c5d5e4873f17d101f06f5138dd4 |
| proof/acceptance.py | f34c2a60f618409c971c7f4c3f2ad91d2797e6aabbd056c6911b68cc533043c1 |

Initial syntax readiness passed with Python 3.13. The first official run is `proof/runs/20260924T191548523508Z`, retained as FAIL. Its stderr shows the expected missing receipt/target functionality, FEATURE-only draft rejection, zero-exit application/helper mutation incorrectly passing capture, and unsupported new completion being accepted. Existing timeout, interruption, separate output, and ordinary child cleanup behavior passed. These are implementation gaps under the accepted outcomes, not reasons to weaken the oracle.

Command: `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/current-completion-evidence --timeout-seconds 180 --note "independent acceptance red before current-evidence implementation"`.

Runtime: local macOS arm64, Python 3.13.3, disposable Git repositories. No network or secrets used. Tests do not import production modules. The initial run captures the former three selected input snapshots; this note retains the determining test digest because the new full candidate evidence does not exist in the baseline implementation.
