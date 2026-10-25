#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$ROOT/scripts/setup_bootstrap.sh"
secondbrain_main "$ROOT" "$@"
