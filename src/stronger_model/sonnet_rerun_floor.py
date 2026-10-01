"""Sonnet's rerun floor on the first room choice: re-ask Sonnet its OWN recorded first-choice prompts (days 8-23)
with a fresh cache, and compare with the room it chose in the run. Sonnet has no temperature-0 setting, so this is
the noise a same-record comparison involving fresh Sonnet answers carries.
    PYTHONPATH=src python3 -m stronger_model.sonnet_rerun_floor hh_s2_t03"""
import json, pathlib, sys
from stronger_model.clients import ClaudeClient
hh = sys.argv[1]
S = pathlib.Path("results/stronger_model/swap")
c = ClaudeClient(pathlib.Path("llm_prior_cache/stronger_model/claude_sonnet_rerun"), model="sonnet")
out = open(S / f"rerun_sonnet_on_sonnet_{hh}.jsonl", "w")
for r in map(json.loads, open(S / f"prompts_from_sonnet_{hh}.jsonl")):
    if not 8 <= r["day"] <= 23:
        continue
    t, _ = c.complete(r["messages"], r["schema"], r["max_tokens"])
    out.write(json.dumps({k: r[k] for k in ("question_id", "day", "is_a_mover", "true_room", "own_first_room")}
                         | {"room": json.loads(t)["room"] if t else None}) + "\n")
    out.flush()
print(hh, c.stats)
