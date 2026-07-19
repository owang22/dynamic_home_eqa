import time
import numpy as np, pandas as pd
from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief.replay import ReplayWorld
from dynbelief.llm_agent.bank import build_bank
from dynbelief.llm_agent.prelim import run_episode, receptacle_options
from dynbelief.llm_agent.clients import OpenAIClient

MODEL = "gpt-5.4-mini-2026-03-17"
client = OpenAIClient(model=MODEL)
SCENES = [("family","logs/dynbelief_daybudget_102344049_family_with_kids",
           "a family home: two working parents, a teenage son, a toddler daughter"),
          ("roommates","logs/dynbelief_daybudget_102344022_roommates_shared_house",
           "a shared house: three adult roommates")]
rows=[]; t0=time.time()
for name, ep, desc in SCENES:
    w=ReplayWorld(REPO_ROOT/ep)
    bank=build_bank(w, seed=7)
    for variant in ("A1","A2","A3"):
        for s in bank:
            try:
                r=run_episode(client,w,s["obj"],s["t_snap"],s["t_query"],variant,desc,
                              seed=hash((name,variant,s["obj"],s["t_snap"],s["t_query"]))%(2**31))
                r.update(scene=name,component=s["component"],stratum=s["stratum"],model=MODEL)
                rows.append(r)
            except Exception as e:
                print(f"FAIL {name}/{variant}: {str(e)[:80]}",flush=True)
        print(f"{name} {variant} done (total {len(rows)}, {time.time()-t0:.0f}s)",flush=True)
pd.DataFrame(rows).to_parquet(REPO_ROOT/"reports/llm_agent/v2_mini_episodes.parquet")
print(f"MINI_V2_DONE {len(rows)} episodes in {time.time()-t0:.0f}s",flush=True)
