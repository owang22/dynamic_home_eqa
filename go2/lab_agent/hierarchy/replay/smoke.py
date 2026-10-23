import json, sys, glob
sys.path.insert(0, '/home/oliver/robot/dynamic_home_eqa/go2/lab_agent/hierarchy')
from llm import LLM
from memtools import Memory
from small_agent import SmallAgent, MemEnv, MEMORY_TOOLS
idx = sorted(glob.glob('/home/oliver/robot/dynamic_home_eqa/go2/lab_agent/hierarchy/replay/data/index_snapshot_*.jsonl'))[0]
cases = {c['id']: c for c in json.load(open('/home/oliver/robot/dynamic_home_eqa/go2/lab_agent/hierarchy/replay/cases_logged.json'))}
c = cases[sys.argv[1]]
url = sys.argv[2] if len(sys.argv) > 2 else 'http://127.0.0.1:8301/v1'
m = Memory.from_index(idx, c['K'], c['t'])
ag = SmallAgent(LLM(url), MemEnv(m), MEMORY_TOOLS, place_ids=list(m.P), places_text=m.list_places(), now=c['t'])
tr = ag.run(c['text'], c['history'])
for s in tr['steps']:
    print(s['t'], s.get('secs'), s['tool'], json.dumps(s.get('args'))[:200], '|', s.get('thought','')[:120])
print('opened', tr['opened']); print('ANSWER', json.dumps(tr['answer'])[:1500]); print('secs', tr['secs'])
