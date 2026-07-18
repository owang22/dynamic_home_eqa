import json
import numpy as np, pandas as pd
from dynamic_home_eqa.paths import REPO_ROOT
from dynamic_home_eqa.generation.llm_client import OpenAIHTTPClient
from dynbelief.replay import ReplayWorld
from dynbelief.llm_agent.bank import build_bank
from dynbelief.llm_agent.prelim import run_episode

client = OpenAIHTTPClient("http://127.0.0.1:8300", "Qwen/Qwen3.6-35B-A3B")
SCENES=[("family","logs/dynbelief_daybudget_102344049_family_with_kids",
         "a family home: two working parents, a teenage son, a toddler daughter"),
        ("roommates","logs/dynbelief_daybudget_102344022_roommates_shared_house",
         "a shared house: three adult roommates")]
rows=[]
for name, ep, desc in SCENES:
    w=ReplayWorld(REPO_ROOT/ep)
    bank=build_bank(w, seed=7)
    pd.DataFrame(bank).to_parquet(REPO_ROOT/f"reports/llm_agent/bank_v2_{name}.parquet")
    for variant in ("A1","A2","A3"):
        for s in bank:
            try:
                r=run_episode(client,w,s["obj"],s["t_snap"],s["t_query"],variant,desc,
                              seed=hash((name,variant,s["obj"],s["t_snap"],s["t_query"]))%(2**31))
                r.update(scene=name,component=s["component"],stratum=s["stratum"],model="qwen3.6")
                rows.append(r)
            except Exception as e:
                print(f"FAIL {name}/{variant}: {str(e)[:70]}",flush=True)
        print(f"{name} {variant} done ({len(rows)})",flush=True)
pd.DataFrame(rows).to_parquet(REPO_ROOT/"reports/llm_agent/v2_qwen_episodes.parquet")
print("V2_QWEN_DONE",flush=True)
