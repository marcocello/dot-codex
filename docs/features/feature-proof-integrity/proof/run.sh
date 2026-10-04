#!/usr/bin/env bash
set -euo pipefail
proof_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$proof_dir/../../../.."
python3 "$root/docs/features/shared-journey-verification/proof/acceptance.py"
python3 "$root/scripts/tests/test_reusable_proof_inputs.py"
python3 "$root/scripts/tests/test_completion_attribution.py"
python3 "$root/scripts/tests/test_feature_proof_integrity.py"
