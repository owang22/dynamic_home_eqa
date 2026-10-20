# Lab routine simulation (overnight 2026-10-17)

Can a language model that writes and maintains hypotheses learn a lab's hidden routines (a prop under desk 2 on
Tue/Thu, a cue the day before, a rotation) better than simple rules? 10 simulated labs x 30 lab days, local
Qwen3.8-27B, no robot.

- **Results:** `RESULTS.md`. Hypotheses beat free notes (+5.8 points first-look right) but not the full log or
  the plain "same weekday as last time" rule; Qwen never wrote down a rule that was not "always here".
- **Design, the task choice and the predictions:** `DESIGN.md`.
- **Experimenter sheets** to run the same scripts in the real lab: `scripts/seed_<k>.md`.

| file | does |
|---|---|
| `serve_qwen.sh` | the local model server (FP8 weights) |
| `world.py` | the simulated lab: places, props, hidden rules, misses |
| `methods.py` | simple rules and the Qwen memories (no memory, full log, notes, hypotheses) |
| `llm.py` | model client, including thinking with a 4000-token budget |
| `run.py` | runs methods through labs, saving after every day (`runs/<method>/seed_<k>.json`) |
| `score.py`, `grade.py`, `grade_summary.py`, `plot.py` | scores, graded memories, the plot |
| `progress.py` | progress while runs are going |

`runs_discarded/` holds the first days of the unbudgeted thinking runs (stopped: 15-25 minutes a call).
This line was followed by `../evidence_memory/`, which Oliver judged closer to what matters.
