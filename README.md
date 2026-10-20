# dynamic_home_eqa

Research on long-horizon memory for a robot in a changing home or lab: what it should remember, how it looks
back, and how it answers questions about things that moved. The current work runs on the lab's Unitree Go2 and
on simulated households rendered in 3D. (Updated 2026-10-19.)

## What is where

| path | what | status |
|---|---|---|
| `go2/` | the lab's Go2: clients of the control PC's console (patrol rounds, viewpoints, object anchors, logger), and two memory studies (`evidence_memory/`, `lab_routine_sim/`) | **active**; start at `go2/README.md` |
| `robot_brain/` | HTTP service that plans where to look and judges pictures for a search, for the ROS-side controller | built 2026-10-13/14 by the other session; `robot_brain/README.md` |
| `3d_rendering/` | the lived-home generator (LLM residents live in an HSSD home; objects move only when someone carries them), renders of it, the vision-model question trials, the render-methods trial | active; `3d_rendering/README.md` |
| `src/dynamic_home_eqa/` | shared code the above reuse: the model client, response cache, hosted-API spend cap (`generation/hosted_rates.yaml`), HSSD scene and room utilities | kept up to date only where used |
| `data/` | datasets of the earlier symbolic simulator (`situation_sim/`, `household_dataset.jsonl`) and the HSSD anchor census `src/` reads | historical, still read by `src/` |
| `prior_work/` | every earlier strand (belief models, symbolic households, routine studies, the workshop papers), moved here on 2026-10-07 under the same relative paths | finished; not on the import path |
| `ARCHIVE_MANIFEST.md` | what was moved out of the repository (to `/home/oliver/robot/dynamic_home_eqa_archive/`) and out of the top level, and why | reference |

Not in git, on cheetah only: `llm_prior_cache/` (model-response cache, about 180,000 files), `third_party/`
(HSSD, habitat and other clones), robot data under `go2/data/` and `robot_brain/data/`, and the model caches of
the go2 studies.

## Machine setup

- `.env` (copy `.env.example`) holds this machine's paths and endpoints; `src/dynamic_home_eqa/paths.py` reads it.
  Shell scripts `source env.sh`.
- Python: `pip install -e .` puts `src/` on the path. The rendering code runs in the `dynamic_eqa` conda
  environment (has habitat_sim); the local models run in `vllm_q` (vLLM).
- Local models are served on `127.0.0.1:8300` (Qwen3.8-27B; `go2/evidence_memory/serve_vlm.sh` for the vision
  model). Paid models go through the spend cap in `src/dynamic_home_eqa/generation/hosted_spend.py`, or through
  `claude -p` on Oliver's Max plan for the go2 studies.

## Where the results are

- Robot memory: `go2/evidence_memory/RESULTS.md` (keep the important scenes and look back; Opus answering from
  Qwen-written notes plus every picture: 89% vs 53% with no memory), `go2/lab_routine_sim/RESULTS.md` (routine
  learning: no model-written rule beat "same weekday as last time").
- Lived-home generator and renders: the write-ups under `3d_rendering/results/` (see its README).
- Earlier strands: `prior_work/` (each strand keeps its own reports).
