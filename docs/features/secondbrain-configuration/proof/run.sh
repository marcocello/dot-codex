#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
printf '%s\n' 'Second-brain configuration acceptance: isolated YAML, real CLI/SQLite registry, native payload boundary only.'
.venv/bin/python docs/features/secondbrain-configuration/proof/acceptance.py
