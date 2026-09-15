#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
printf 'Target: local knowledge-capture discovery, routed documents and offline RIS helper\n'
python3 docs/features/knowledge-capture-consolidation/proof/acceptance.py
