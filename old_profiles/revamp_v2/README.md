# revamp_v2 — household generation

`storyfirst/` holds the **current dataset**. See
`storyfirst/README.md` for what it contains and
`docs/dataset_pipeline.md` for how it is generated.

    control.yaml        the 10 household slots: id, type, resident count,
                        bedrooms, and the closed object vocabulary
    storyfirst/         CURRENT — one directory per model, then per household
    rule_based/         superseded
    story_calendar/     superseded
    _archive/           earlier slot sets

## Code

Everything lives in `src/revamp_v2/`.

| current | |
|---|---|
| `generate_dataset.py` | the pipeline: persona, story, movement, realization |
| `export_dataset.py` | consolidates a built set into one JSONL file |
| `prompts.py` | every LLM-facing string, content-hash versioned |
| `schemas.py` | the guided-JSON contracts |
| `validate.py` | the gates an accepted household must pass |
| `expand_calendar.py` | program to simulator input |
| `simulate.py` | seeded realization |
| `realization_params.yaml` | jitter, skip and fragmentation bounds |
| `realism_panel.py` | compares a set against real activity data |
| `make_viewer_configs.py` | grounds a household in a scene for the viewer |

| superseded | |
|---|---|
| `generate.py`, `story_calendar.py`, `story_driven.py`, `build.sh` | earlier pipelines that produced `rule_based/` and `story_calendar/` |
| `freeform_motion.py`, `expand_calendar.py` helpers, `acceptance_report.py`, `factorial_report.py` | reporting and variants for those sets |

The superseded pipelines are kept because the sets they produced are
still on disk and referenced by earlier reports. New work should use
`generate_dataset.py`.

## Household slots

`control.yaml` fixes what each household IS — type, how many people, how
many bedrooms — and the 35-word object vocabulary every inventory draws
from. Changing a slot changes the persona prompt for every household,
because each one is shown the other types for contrast.
