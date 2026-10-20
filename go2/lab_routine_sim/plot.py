"""First look right by lab week, one line per method (labs 0-9 unless the method ran on fewer). python plot.py"""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, ".")
import score
import world as W

STYLE = {"rules_known": ("rules known (ceiling)", "#888888", "--", "s"),
         "same_weekday": ("same weekday (rule)", "#1b9e77", "-", "o"),
         "full_log": ("full log (Qwen)", "#7570b3", "-", "^"),
         "hypotheses": ("hypotheses (Qwen)", "#d95f02", "-", "D"),
         "notes": ("notes (Qwen)", "#e7298a", "-", "v")}
runs = score.load_runs()
fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=150)
weeks = range(1, 7)
for m, (label, col, ls, mk) in STYLE.items():
    if m not in runs:
        continue
    ys = []
    for wk in weeks:
        days = range(5 * wk - 4, 5 * wk + 1)
        per = []
        for s, r in runs[m].items():
            rows = [x for x in score.per_lab(r) if x["day"] in days and x["first_right"] is not None]
            per.append(sum(x["first_right"] for x in rows) / len(rows))
        ys.append(sum(per) / len(per))
    ax.plot(list(weeks), ys, ls=ls, marker=mk, color=col, label=label, lw=2)
ax.axvline(3.5 + 0.5 * 0, color="#444", lw=1, ls=":")
ax.text(3.55, 0.88, "rules change\n(start of week 4)", fontsize=8, va="top")
ax.set_xlabel("lab week (5 lab days each)")
ax.set_ylabel("first place checked was right")
ax.set_xticks(list(weeks))
ax.set_ylim(0.15, 0.9)
ax.set_title("Simulated lab, 10 labs x 30 days, Qwen3.8-27B without thinking", fontsize=10)
ax.legend(fontsize=8, loc="lower right", ncol=2)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("first_look_by_week.png")
print("wrote first_look_by_week.png")
