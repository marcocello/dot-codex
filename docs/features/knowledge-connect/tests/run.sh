#!/usr/bin/env bash
set -euo pipefail
python3 docs/features/knowledge-connect/tests/check_edges.py
python3 docs/features/knowledge-clickup-api/tests/check_redirect.py
python3 docs/features/knowledge-profiles/tests/check_edge_cases.py
python3 skills/knowledge-connect/scripts/clickup_api.py --help >/dev/null
python3 skills/knowledge-connect/scripts/notion_api.py --help >/dev/null
python3 skills/.system/skill-creator/scripts/quick_validate.py skills/knowledge-connect
python3 skills/.system/skill-creator/scripts/quick_validate.py skills/knowledge-config
