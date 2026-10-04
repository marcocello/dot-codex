# Independent proof correction: timestamp representation

Author: independent acceptance author `/root/secondbrain_proof`. Date: 2026-09-21. This correction changes no implementation, specification, scenario, intended outcome, selection or boundary.

The unchanged FEATURE requires timezone-aware ISO-8601 normalized to UTC, without prescribing fractional-second precision. The original acceptance incorrectly allowed only two literal strings for the UTC instant. The captured failure in `proof/runs/20260921T093814743735Z/stderr.txt` demonstrates that `2031-01-01T10:00:00.000000Z`, a valid UTC representation of the required instant, failed this accidental string-spelling constraint.

The independent author replaced that one lexical membership assertion with parsing plus explicit checks for zero UTC offset and the exact expected instant. This retains timezone normalization, exact time correctness, and malformed/naive input rejection; it broadens no semantic outcome. A non-UTC offset still fails even if it denotes the same instant. The original input is retained in `acceptance-before-timestamp-correction.py`; the exact edit is in `timestamp-proof-correction.diff`; original/revised acceptance and full revised freeze hashes are in `timestamp-proof-correction-hashes.json`. FEATURE.md, PROOF.md and runner were not edited.

The retained official failure remains history. The independent author reruns the affected scenario and the complete unchanged scenario selection; root then records a new full official capture. This is an assertion-format/setup repair under the written contract, not adaptation to a weaker implementation.
