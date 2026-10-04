# Input coverage assertion repair

Independent repair author: `input_scope_proof` (`/root/input_scope_proof`), 2026-09-25. Original acceptance author remains `completion_proof`. The author changed no FEATURE, runner, production code, implementation regressions, or status.

This is a missing-assertion repair under the existing accepted requirement to reject mismatched supporting evidence and the evidence contract requiring the same includes and target for proof and selected regressions. It adds no product policy or workflow stage. The previous proof checked freshness and target per run but did not demonstrate that passing runs covered the same determining inputs.

The retained actual CLI reproduction in `baseline-reproduction.json` captured a regression reading an ignored file without including it, changed that file, and captured a fresh proof explicitly including it. Before implementation changed, PASS review and done both returned zero, although the same regression then failed. `baseline-pass-review.json` is the actual pre-fix receipt. Its referenced disposable paths are historical and are not reused as current evidence.

The focused command and exit status are in `focused-red.json`; its unchanged-implementation failures are retained in `focused-red.stderr.txt` and `focused-red.stdout.txt`. The new review test rejected neither direction of differing include coverage. The new legacy completion test also failed because done was incorrectly accepted. The control for normalized equal includes and diagnostic FAIL review passed. No assertion was weakened in response.

The executable legacy scenario uses fresh real captures and public diagnostic-review output, then restores the historical PASS verdict and recomputes the documented canonical SHA-256. This supplies a historically valid input format to the actual status consumer; it does not claim cryptographic tamper resistance or seed the completion result. Its successful done transition against the unchanged implementation is retained in the focused red.

`prior-inputs/` preserves all four original fixed inputs. `acceptance.diff` is the exact change to PROOF and acceptance.py; FEATURE and runner remain unchanged. Parent owns the full official rerun and separate final review after implementation. All fixture contents are synthetic; no network, credentials, or external service is required.

Revised freeze:

| Path relative to feature | Prior SHA-256 | Revised SHA-256 |
| --- | --- | --- |
| FEATURE.md | `0dc662f18f1406bc4f692fc256d34670ce8a8e7f06b303958c546c95648e6648` | `0dc662f18f1406bc4f692fc256d34670ce8a8e7f06b303958c546c95648e6648` |
| PROOF.md | `5f6e4217c82aac61fa54d35dc3c5a0d0f38b1eaeca1d7ec3bb51e8b433bd33f4` | `1e2dbdb3d1889cea09d399fb4d64222e4ee227f45bf2bf71b2f64fb472d12498` |
| proof/run.sh | `02f87695e98ee3dc769f4ab5337cd56e10460c5d5e4873f17d101f06f5138dd4` | `02f87695e98ee3dc769f4ab5337cd56e10460c5d5e4873f17d101f06f5138dd4` |
| proof/acceptance.py | `f34c2a60f618409c971c7f4c3f2ad91d2797e6aabbd056c6911b68cc533043c1` | `a8ea3710347c4ac64bb86a90457a516932e215f8a861ef6a34a2ab98eb559079` |
