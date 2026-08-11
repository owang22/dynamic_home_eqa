"""Golden-file test: the run log for a fixed (bank, config, seed) must match
the checked-in snapshot byte for byte, so any behavioural change — however
innocent-looking — surfaces in review as a diff to this file.

To regenerate after an INTENTIONAL behaviour change:

    python -m tests.test_baselines_golden

which rewrites tests/fixtures/baselines_golden_run_log.jsonl; commit the
diff together with the change that caused it.
"""

from __future__ import annotations

import json
import pathlib
import tempfile

from baselines.cli import build_agent
from baselines.bank import write_synthetic_bank
from baselines.harness import run_episode

GOLDEN_PATH = (pathlib.Path(__file__).parent
               / "fixtures" / "baselines_golden_run_log.jsonl")
GOLDEN_SEED = 20260809


def _golden_run_log() -> str:
    """The canonical run: last-observation belief + sequential search on
    the synthetic bank. Chosen because it exercises exclusion bookkeeping,
    multi-sense search, sensing, and budget accounting in one pass."""
    with tempfile.TemporaryDirectory() as tmp:
        bank = write_synthetic_bank(pathlib.Path(tmp) / "bank.jsonl")
        episode = next(bank.episodes())
    agent = build_agent({"name": "last_observation"},
                        {"name": "sequential_search"}, seed=GOLDEN_SEED,
                        episode_id=episode.episode_id)
    records = [r.to_json_dict() for r in run_episode(agent, episode)]
    return "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n"


def test_run_log_matches_golden_snapshot() -> None:
    assert GOLDEN_PATH.exists(), (
        f"golden snapshot missing: {GOLDEN_PATH}; generate it with "
        f"`python -m tests.test_baselines_golden`")
    assert _golden_run_log() == GOLDEN_PATH.read_text(), (
        "run log diverged from the golden snapshot. If the behaviour change "
        "is intentional, regenerate via `python -m tests.test_baselines_golden` "
        "and commit the diff; otherwise this is a regression.")


if __name__ == "__main__":
    GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN_PATH.write_text(_golden_run_log())
    print(f"wrote {GOLDEN_PATH}")
