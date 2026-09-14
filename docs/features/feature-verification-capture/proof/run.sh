#!/usr/bin/env bash
set -euo pipefail
printf 'Feature verification capture: installed CLI, isolated Git repositories\n'
python3 "$(cd "$(dirname "$0")" && pwd)/acceptance.py"
