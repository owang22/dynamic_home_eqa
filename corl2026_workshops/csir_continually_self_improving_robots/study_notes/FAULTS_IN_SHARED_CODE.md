# Faults in shared code that this study works around rather than fixes

This file is a message to whoever owns the files named below. Nothing here has
been changed by this study: these are notes, not patches. They are written down
because each one costs an evening to rediscover.

This study is only permitted to write under `src/self_improve/` and
`results/self_improve/`, so **this note is not where the owner of the file will
look.** It needs to reach them as a comment in the file itself or as a tracked
issue. Someone with write access to `src/baselines/` should move it.

---

## 1. `src/baselines/patrol/bank.py` loads activities from a hard-coded path

Found by the scenario-generation work on 2026-09-24, verified here by reading the
two functions.

`src/baselines/patrol/bank.py:233`

```python
def load_activities() -> Dict[str, dict]:
    path = pathlib.Path(__file__).resolve().parents[2] / "situation_sim" / "activities.yaml"
    return yaml.safe_load(path.read_text())["activities"]
```

It takes **no path argument**, so it always reads the shared
`src/situation_sim/activities.yaml`. The simulator's own loader, by contrast, does
take one:

`src/situation_sim/schedule.py:25` — `def load_activities(path: Optional[pathlib.Path] = None) -> dict:`
`src/situation_sim/situation.py:56` — `def load_events(path: Optional[pathlib.Path] = None) -> Dict[str, dict]:`

**The failure this causes.** A scenario that ships its own `activities.yaml` — the
supported pattern, since the simulator loaders accept a path — simulates against
its own activities and then builds its question bank against the *shared* ones.
Where the two disagree about which activity uses which object class, the bank
silently ends up with no questions, or with questions about objects the scenario
never moves. It fails quietly: the bank is written, it is just empty or wrong, and
nothing warns you.

**The one-line fix**, for whoever owns the file: give `load_activities` the same
optional path parameter its counterpart in `situation_sim` already has, and thread
the scenario directory through from the caller. Until then, a caller building a
bank for a scenario with its own activities has to point the shared file at the
scenario's copy, which is what "working around it" means here.

**How to notice it has bitten you:** a freshly built bank whose question rows are
absent, or whose `question_classes` do not match the classes the scenario's own
`activities.yaml` says are used.
