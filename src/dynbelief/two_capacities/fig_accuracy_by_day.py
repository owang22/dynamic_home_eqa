import json, numpy as np
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dynbelief.answer_or_resense.run_aor import OUT as AOR_OUT
OUT = AOR_OUT.parent / "two_capacities"

ARMS = [("classical","classical_conf_frozen","#2e6f95","-"),
        ("llm_scaffold (ours)","llm_scaffold_conf_frozen","#e8890c","-"),
        ("scaffold_fusion","scaffold_fusion_conf_frozen_deepseek","#2a9d8f","-")]

def load(f):
    p = AOR_OUT / f"rows_{f}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []

def day_ci(rows, kind=None, field="cf_correct", nb=800):
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if kind and r["kind"] != kind: continue
        by[r["day"]][r["hh"]].append(r[field])
    days = sorted(by); mean=[]; lo=[]; hi=[]
    rng = np.random.default_rng(4)
    for d in days:
        clus=list(by[d]); vals=[v for c in clus for v in by[d][c]]
        mean.append(np.mean(vals))
        m=[np.mean([v for i in rng.integers(0,len(clus),len(clus)) for v in by[d][clus[i]]]) for _ in range(nb)]
        lo.append(np.percentile(m,2.5)); hi.append(np.percentile(m,97.5))
    return days, np.array(mean), np.array(lo), np.array(hi)

fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.4), sharey=True)
for ax, kind, title in zip(axes, [None,"typical","atypical"],
                           ["ALL queries","TYPICAL objects (prior is right)",
                            "ATYPICAL objects (prior is wrong)"]):
    for lab, f, col, ls in ARMS:
        rows = load(f)
        if not rows: continue
        d, m, lo, hi = day_ci(rows, kind)
        lw = 2.8 if "scaffold" in lab else 1.9
        ax.plot(d, m, ls, color=col, marker="o", ms=4, lw=lw, label=lab,
                zorder=5 if "ours" in lab else 3)
        ax.fill_between(d, lo, hi, color=col, alpha=0.10)
    ax.set_title(title, fontsize=11); ax.set_xlabel("day"); ax.grid(alpha=0.25)
    ax.set_ylim(0, 1.0)
axes[0].set_ylabel("answer accuracy (counterfactual — every query scored)")
axes[0].legend(fontsize=9, loc="lower right")
fig.suptitle("Accuracy by day in the scarce-sensing loop — fusion reaches competence fastest\n"
             "DeepSeek · 24 households · staggered starts · household-clustered 95% CI",
             fontsize=12, y=0.99)
fig.tight_layout(rect=(0,0,1,0.86))
p = OUT / "F7_accuracy_by_day.png"
fig.savefig(p, dpi=140); print("wrote", p)

# print the underlying numbers
print(f"\n{'arm':22s}" + "".join(f"d{d:<4d}" for d in range(0,14,2)))
for lab, f, _c, _l in ARMS:
    rows = load(f)
    if not rows: continue
    d, m, lo, hi = day_ci(rows)
    print(f"{lab:22s}" + "".join(f"{m[i]:<5.2f}" for i in range(0,14,2)))
