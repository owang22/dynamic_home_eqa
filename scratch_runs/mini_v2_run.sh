#!/bin/bash
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source env.sh
"$PY" scratch_runs/mini_v2_bank.py > scratch_runs/mini_v2.log 2>&1
echo "MINI_V2_DONE $(date)" > scratch_runs/MINI_V2_DONE.marker
