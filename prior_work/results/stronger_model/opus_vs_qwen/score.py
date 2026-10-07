"""First room right by window, paired question by question, for every answers_* cell present.
Qwen-on-Qwen-notes is the original cell's own first room (cell_first_room), Qwen's answer on exactly those prompts.
    python3 results/stronger_model/opus_vs_qwen/score.py"""
import json, pathlib, statistics as st
D = pathlib.Path(__file__).parent
HH = ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]
WIN = ["settled", "onset 1", "return 1", "onset 2", "return 2"]
def load(cell, h):
    p = D / cell / f"{h}.jsonl"
    return {r["question_id"]: r for r in map(json.loads, open(p))} if p.exists() else None
cells = {"Opus, Opus notes": "answers_opus_notes_by_opus", "Opus, Qwen notes": "answers_qwen_notes_by_opus",
         "Qwen, Opus notes": "answers_opus_notes_by_qwen"}
base = {}
for h in HH:
    rows = [json.loads(l) for l in open(D / "memory_qwen" / f"prompts_{h}.jsonl")]
    base[h] = {r["question_id"]: r for r in rows}
W = {12:"settled",13:"settled",14:"onset 1",15:"onset 1",16:"onset 1",24:"return 1",25:"return 1",26:"return 1",
     32:"onset 2",33:"onset 2",34:"onset 2",42:"return 2",43:"return 2",44:"return 2"}
def acc_qwen_own(h, w):
    rs = [r for r in base[h].values() if W.get(r["day"]) == w]
    return 100 * sum(r["rooms_opened"][0] == r["true_room"] for r in rs) / len(rs), {r["question_id"] for r in rs}
print("first room right, %; diff = cell minus Qwen on its own notes (the original cell), paired; mean over homes (2 SE over homes)")
for name, cell in cells.items():
    got = {h: load(cell, h) for h in HH}
    if not any(got.values()): print(f"\n{name}: not run"); continue
    print(f"\n{name}  vs  Qwen, Qwen notes")
    for w in WIN + ["all"]:
        diffs, line = [], []
        for h in HH:
            if not got[h]: line.append(f"{h[:6]} -"); continue
            rs = [r for r in got[h].values() if w == "all" or r["window"] == w]
            a = 100 * sum(r["right"] for r in rs) / len(rs)
            q = 100 * sum(base[h][r["question_id"]]["rooms_opened"][0] == r["true_room"] for r in rs) / len(rs)
            diffs.append(a - q); line.append(f"{h[:6]} {a:5.1f} vs {q:5.1f} ({a-q:+5.1f})")
        se = (2 * st.stdev(diffs) / len(diffs) ** 0.5) if len(diffs) > 1 else float("nan")
        print(f"  {w:9s} " + " | ".join(line) + f" || mean {st.mean(diffs):+5.1f} (2SE {se:4.1f})")
