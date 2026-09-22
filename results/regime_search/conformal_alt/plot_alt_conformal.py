#!/usr/bin/env python3
"""alt_conformal.png: set size (top) and coverage (bottom) per day, one spell (left) / two spells (right)."""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = pathlib.Path("/home/oliver/robot/dynamic_home_eqa/results/regime_search/conformal_alt")
D = json.load(open(OUT / "alt_conformal.json"))
# dataviz reference palette, categorical slots 1-5 in fixed order (light mode)
COL = {"ocp_base": "#2a78d6", "fix_eta05": "#eb6834", "fix_eta02": "#1baf7a",
       "wq_tau24": "#eda100", "wq_tau12": "#e87ba4"}
LAB = {"ocp_base": "DecayingStep, shipped (eta_min .005)", "fix_eta05": "Fixed step eta = 0.05",
       "fix_eta02": "Fixed step eta = 0.02", "wq_tau24": "Weighted quantile, tau_w = 24 h",
       "wq_tau12": "Weighted quantile, tau_w = 12 h"}
ORDER = ["ocp_base", "fix_eta05", "fix_eta02", "wq_tau24", "wq_tau12"]
REG = [("sick10_owner", "One spell (days 14-23)", [(14, 23)]),
       ("sick2x_owner", "Two spells (days 14-20, 28-34)", [(14, 20), (28, 34)])]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#dedcd4"
HOUSE = 37.63   # mean number of spots = the whole house

fig, axes = plt.subplots(2, 2, figsize=(13.5, 7.4), sharex="col")
fig.patch.set_facecolor("#fcfcfb")
for c, (reg, title, spells) in enumerate(REG):
    days = sorted(int(x) for x in D[reg]["n_per_day"])
    for r in (0, 1):
        ax = axes[r][c]
        ax.set_facecolor("#fcfcfb")
        for a, b in spells:
            ax.axvspan(a - 0.5, b + 0.5, color="#9a9890", alpha=0.13, lw=0, zorder=0)
        for m in ORDER:
            s = D[reg]["series"][m]
            y = [(s[str(d)][2] / s[str(d)][0]) if r == 0 else (100 * s[str(d)][1] / s[str(d)][0]) for d in days]
            ax.plot(days, y, color=COL[m], lw=2.4 if m == "ocp_base" else 1.8,
                    marker="o", ms=3.2, label=LAB[m], zorder=3 if m == "ocp_base" else 2)
        ax.grid(True, color=GRID, lw=0.7, zorder=0)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=9)
        if r == 0:
            ax.set_yscale("log")
            ax.axhline(HOUSE, color=INK2, ls=":", lw=1.0, zorder=1)
            ax.text(days[-1], HOUSE * 1.03, "whole house", ha="right", va="bottom", fontsize=8, color=INK2)
            ax.set_yticks([1, 2, 5, 10, 20, 38])
            ax.set_yticklabels(["1", "2", "5", "10", "20", "38"])
            ax.set_ylim(1.1, 55)
            ax.set_title(title, fontsize=11.5, color=INK, pad=8)
            if c == 0:
                ax.set_ylabel("mean set size  (log scale)", fontsize=10, color=INK2)
        else:
            ax.axhline(90, color=INK2, ls="--", lw=1.0, zorder=1)
            ax.text(days[0], 90.6, "90% target", ha="left", va="bottom", fontsize=8, color=INK2)
            ax.set_ylim(60, 101)
            ax.set_xlabel("day", fontsize=10, color=INK2)
            if c == 0:
                ax.set_ylabel("coverage (%)", fontsize=10, color=INK2)
axes[1][0].legend(loc="lower right", fontsize=9, frameon=False, labelcolor=INK2, ncol=1,
                  title="conformal wrapper", title_fontsize=9)
axes[1][0].get_legend().get_title().set_color(INK)
fig.suptitle("Conformal wrappers on the same never-forgets timetable, same questions, 90% target",
             fontsize=13, color=INK, y=0.985)
fig.text(0.5, 0.005, "shaded = the sick spell.  Pooled over 10 households; identical question set for every method.",
         ha="center", fontsize=8.5, color=INK2)
fig.tight_layout(rect=(0, 0.02, 1, 0.965))
fig.savefig(OUT / "alt_conformal.png", dpi=150, facecolor=fig.get_facecolor())
print("wrote", OUT / "alt_conformal.png")
