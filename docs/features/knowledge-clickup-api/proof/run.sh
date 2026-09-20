#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
printf '%s\n' 'Acceptance target: real Python CLI; synthetic HTTPS boundary; no live account.'
python3 -m unittest discover -s . -p test_acceptance.py -v
