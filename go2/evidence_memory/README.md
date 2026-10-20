# Evidence memory (2026-10-19)

Which memory lets a patrolling robot keep the important scenes and later look back at them to answer questions
nobody planned ("did someone forget their keys, and when?", "were there screws next to the screwdrivers?").
Tested in simulation on household A, then turned into a tool for the real Go2.

- **Results:** `RESULTS.md`. In short: Opus answering from change notes (written by the local Qwen) plus every
  kept picture got 89% of the clean questions, against 53% for a fixed answer sheet with no memory.
- **Design, arms and the predictions made before the run:** `DESIGN.md`.
- **The in-person trial script:** `IN_PERSON.md`.
- **Results page:** built by `page.py` into `out/page.html`; published as a private artifact,
  https://claude.ai/artifact/9q9DwmpJTzPf31EXDDrTtL

## Files, in the order they run

| file | does |
|---|---|
| `serve_vlm.sh` | starts the local Qwen3.8-27B with vision (vLLM, port 8300) |
| `common.py` | paths, the 16-place patrol, the people sheet, the cached model client |
| `questions.py` | 122 questions from household A's truth -> `out/questions.json` |
| `write_memory.py` | per-visit captions and change notes, at 1.0 m or 0.4 m -> `out/memory_<h>.json` |
| `answer.py` | the memory arms (A-F, O, fresh look, random pairs) answer -> `out/answers_<h>_<arm>.json` |
| `opus.py`, `opus_write.py` | the same answer step, and the note writer, with Opus via `claude -p` (Max plan) |
| `fixed_answers.py` | the no-memory answer sheet (arm Z) |
| `validity.py` | flags questions that do not test what they claim -> `out/question_flags.json` |
| `score.py` | scores an arm; `--clean` uses only the questions validity.py keeps |
| `analyze.py` | extra cuts (look-back yes/no, the oracle-right subset) |
| `page.py` | the results page |
| `lab.py` | the method on real Go2 pictures: `update` after each round, `ask` a question |

The exact commands of every run are the frozen scripts in `logs/` (`run_*_frozen*.sh`), with their logs.

## Not in git

`cache*/` (model responses, about 47 MB, regenerable but slow), `out/page.html` (8 MB, published), `lab/`
(real-lab memory, made on the day). The 0.4 m pictures are under
`/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_0p4/` (renderer: `3d_rendering/results/vlm_night/render/*_0p4.py`).
