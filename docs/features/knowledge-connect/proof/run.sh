#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
python3 docs/features/knowledge-connect/proof/test_acceptance.py
