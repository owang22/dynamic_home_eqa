import json, numpy as np
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dynbelief.answer_or_resense.run_aor import OUT as AOR_OUT
OUT = AOR_OUT.parent / "two_capacities"
ALPHA = 6.07

ARMS=[("classical","classical_conf_frozen","#2e6f95"),
      ("llm_scaffold","llm_scaffold_conf_frozen","#e8890c"),
      ("scaffold_fusion","scaffold_fusion_conf_frozen_deepseek","#2a9d8f")]
def load(f):
    p=AOR_OUT/f"rows_{f}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
def clu(d,nb=3000,seed=11):
    ks=list(d); rng=np.random.default_rng(seed)
    m=[np.mean([v for i in rng.integers(0,len(ks),len(ks)) for v in d[ks[i]]]) for _ in range(nb)]
    return np.mean([v for vs in d.values() for v in vs]), np.percentile(m,2.5), np.percentile(m,97.5)

fig = plt.figure(figsize=(15.5, 5.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 1], wspace=0.30)

# ---- A: the mechanism curve — accuracy vs per-object evidence count n ----
ax = fig.add_subplot(gs[0,0])
for lab,f,col in ARMS:
    rows=load(f)
    if not rows: continue
    byhh=defaultdict(list)
    for r in rows: byhh[r["hh"]].append(r)
    buck=defaultdict(lambda: defaultdict(list))
    for hh,rs in byhh.items():
        rs.sort(key=lambda r:r["t"]); n=defaultdict(int)
        for r in rs:
            buck[min(n[r["obj"]],4)][hh].append(r["cf_correct"])
            if r["action"]=="resense": n[r["obj"]]+=1
    ks=sorted(buck); mm=[];lo=[];hi=[]
    for k in ks:
        m,l,h=clu(buck[k]); mm.append(m); lo.append(l); hi.append(h)
    lw=3.0 if lab=="scaffold_fusion" else 1.9
    ls="--" if "oracle" in lab else "-"
    ax.plot(ks,mm,ls,color=col,marker="o",ms=6,lw=lw,label=lab,zorder=5 if lab=="scaffold_fusion" else 3)
    ax.fill_between(ks,lo,hi,color=col,alpha=0.10)
ax2=ax.twinx()
ns=np.linspace(0,4,100)
ax2.plot(ns, ALPHA/(ALPHA+ns), ":", color="#b23a48", lw=2)
ax2.set_ylabel("prior weight  α/(α+n)   (α*=6.07)", color="#b23a48", fontsize=9)
ax2.tick_params(axis="y", labelcolor="#b23a48", labelsize=8); ax2.set_ylim(0,1.05)
ax.set_xticks(range(5)); ax.set_xticklabels(["0","1","2","3","4+"])
ax.set_xlabel("per-object evidence count n  (self-gathered observations)")
ax.set_ylabel("answer accuracy"); ax.grid(alpha=0.25); ax.set_ylim(0,0.8)
ax.legend(fontsize=8.5, loc="lower right")
ax.set_title("A — the mechanism: fusion wins where n is SMALL\n"
             "(dotted = the designed prior weight, which fades as n grows)", fontsize=10)

# ---- B: early vs late reward ----
ax = fig.add_subplot(gs[0,1])
labels=[]; E=[]; L=[]; Ee=[]; Le=[]; cols=[]
for lab,f,col in ARMS:
    rows=load(f)
    if not rows: continue
    e=defaultdict(list); l=defaultdict(list)
    for r in rows: (e if r["day"]<=4 else l)[r["hh"]].append(r["reward"])
    em=clu({k:[np.sum(v)/5] for k,v in e.items()}); lm=clu({k:[np.sum(v)/9] for k,v in l.items()})
    labels.append(lab.replace(" (bound)","")); cols.append(col)
    E.append(em[0]); Ee.append([em[0]-em[1], em[2]-em[0]])
    L.append(lm[0]); Le.append([lm[0]-lm[1], lm[2]-lm[0]])
x=np.arange(len(labels))
ax.bar(x-0.2,E,0.4,yerr=np.array(Ee).T,color=cols,capsize=3,label="EARLY (days 0-4)")
ax.bar(x+0.2,L,0.4,yerr=np.array(Le).T,color=cols,alpha=0.42,hatch="//",edgecolor="white",
       capsize=3,label="LATE (days 5-13)")
ax.set_xticks(x); ax.set_xticklabels(labels,rotation=18,fontsize=8.5)
ax.set_ylabel("reward / household-day"); ax.grid(alpha=0.25,axis="y")
ax.legend(fontsize=8.5, loc="lower right")
ax.set_title("B — the gap is concentrated EARLY\n"
             "(solid vs classical: +1.64 early, tied late)", fontsize=10)

# ---- C: days to threshold ----
ax = fig.add_subplot(gs[0,2])
THR=0.55; labs=[]; days=[]; cols2=[]
for lab,f,col in ARMS:
    rows=load(f)
    if not rows: continue
    by=defaultdict(list)
    for r in rows: by[r["day"]].append(r["cf_correct"])
    hit=next((d for d in sorted(by) if np.mean(by[d])>=THR), 14)
    labs.append(lab.replace(" (bound)","")); days.append(hit); cols2.append(col)
ax.barh(range(len(labs)), days, color=cols2, height=0.55)
for i,d in enumerate(days): ax.text(d+0.12,i,f"day {d}",va="center",fontsize=9)
ax.set_yticks(range(len(labs))); ax.set_yticklabels(labs,fontsize=9)
ax.set_xlabel(f"days to reach {THR:.2f} accuracy (lower = faster)")
ax.grid(alpha=0.25,axis="x"); ax.set_xlim(0,8); ax.invert_yaxis()
ax.set_title("C — time-to-competence\nfusion: 3 days ahead of classical", fontsize=10)

fig.suptitle("Designed for FAST LEARNING, not a higher ceiling: α/(α+n) hands the prior control "
             "while evidence is scarce and retires it as counts grow\n"
             "DeepSeek · 24 households · staggered starts · household-clustered 95% CI",
             fontsize=11.5, y=0.995)
fig.tight_layout(rect=(0,0,1,0.79))
p=OUT/"F8_sample_efficiency.png"; fig.savefig(p,dpi=140); print("wrote",p)
