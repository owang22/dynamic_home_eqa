#!/bin/bash
cd "$(dirname "$0")/.."
/home/oliver/miniconda3/envs/dynamic_eqa/bin/python - <<'PY' > scratch_runs/kernel_elicit.log 2>&1
import pathlib
from dynbelief.e2.elicit_kernel import elicit_all
from dynbelief.e2.run import BASE_DESCRIPTORS
elicit_all(None, ["gpt-5.4-mini","gpt-5.5"], pathlib.Path("profiles/manual"),
           pathlib.Path("results/e2/kernel_priors"), BASE_DESCRIPTORS)
PY
touch results/e2/KERNEL_ELICIT_DONE.marker
