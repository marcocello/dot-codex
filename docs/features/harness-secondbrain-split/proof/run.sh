#!/bin/sh
set -eu
exec python3 -m unittest discover -s docs/features/harness-secondbrain-split/proof -p 'test_*.py' -v
