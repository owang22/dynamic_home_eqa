# Faults in shared code that this study works around rather than fixes

> Carried up out of `results/self_improve/` on 2026-09-24 by the coordinating session so that the
> owner of `src/baselines/` will actually see it. The copy under `results/self_improve/` is left in
> place rather than deleted.

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

## 2026-09-25 — `baselines/patrol/llm.py`: the socket gave up before the watchdog

**Changed, and it affects every caller.** `_post` built its connection with
`timeout=min(600.0, self.DEADLINE_S)` while `DEADLINE_S` is 900. So the socket timed out
three hundred seconds before the watchdog that exists to bound the call — two limits on one
quantity, where the smaller one was the real one and nobody chose it.

**What it cost, measured.** In an overnight run of 61 cells, 24 calls failed and **every
single one was `TimeoutError: timed out` at exactly 600 seconds, on both attempts.** The
calls were not lost; the server was still generating. Five cells were held back by a
completeness gate because of it, three of them in one arm, and the arms affected were the
ones whose nightly generation is longest — so the loss was not random across arms.

**Now:** `timeout=self.DEADLINE_S`. The watchdog still kills the socket at 900 seconds, so
nothing waits longer than it could before; a genuinely lost request is still bounded. For
callers whose generations are short nothing changes at all. For callers whose generations
are long, a call that was being cut off mid-flight now returns.

**If you were seeing lost calls on long generations, this was why**, and any run of yours
that reported "the model call failed" on a slow arm is worth re-reading in that light.

**The same line is still live in `baselines/patrol/uq_llm.py`** (`Client._post`, line 58:
`timeout=min(600.0, self.DEADLINE_S)` with `DEADLINE_S = 900`). Not changed here, because that
file belongs to the UQ strand and may have a run against it right now — flagging rather than
editing. Whoever owns it: the same one-word change applies, and any UQ run that logged a lost
call on a long generation was probably hit by this.

**One thing to check if you audit your own run for this.** A per-night or per-step "the model
call failed" flag will not find all of it. Of the five cells affected in our wave, one
(`claim store told if it was right / hh_s2_t03`) lost an **answer-step** call rather than a
nightly write, so it carried no failed-night flag anywhere and an audit of that flag reported
it clean; the loss existed only as `LOST after 2 attempts` in the run log. Grep the logs, not
the summaries.
