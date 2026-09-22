"""make_report.py [regime ...]: headline table + per-regime sections from <regime>/check.md -> report_auto.md"""
import re, sys, pathlib
U = pathlib.Path(__file__).parent
regimes = sys.argv[1:] or ["sick_owner", "sick_all", "sick_spell", "holiday_to_work"]
def rows(regime, agents):
    t = (U / regime / "check.md").read_text().split("\n")
    hdr = [l for l in t if l.startswith("| agent | hh |")][0]
    out = [hdr, "|---|---|" + "---|" * (hdr.count("|") - 3)]
    for ag in agents:
        out += [l for l in t if l.startswith(f"| {ag} | ")][:1]
    return "\n".join(out)
def section(regime, title):
    t = (U / regime / "check.md").read_text()
    m = re.search(rf"## {re.escape(title)}.*?(?=\n## |\Z)", t, re.S)
    return m.group(0) if m else ""
def checks(regime):
    return (U / regime / "check.md").read_text().split("## expectation checks (uq/regime/EXPECTATIONS.md)")[1].strip()
md = [f"# UQ roster on the regime banks — auto tables ({', '.join(regimes)})", "",
      "| regime | stages | e-detector (mon_tt): lead false alarms; fires on the first two shift days; return fires | mon_tt72 same | ocp coverage per stage (set before -> after) | nexcp_tt coverage (set) | reset gain shift days 3-5 (mart_tt vs none_tt) | bma short-hl weight before -> after |",
      "|---|---|---|---|---|---|---|---|"]
for R in regimes:
    c = checks(R)
    g = lambda pat: (re.search(pat, c).group(1) if re.search(pat, c) else "?")
    st = (U / R / "check.md").read_text().split("\n")[2]
    md.append(f"| {R} | {st.replace('stages: ', '')} | {g(r'E3/E4/E5 mon_tt: (.*)')} | {g(r'E3/E4/E5 mon_tt72: (.*)')} | "
              f"{g(r'E2 ocp_tt coverage per stage (.*?) ->')} ({g(r'E2 ocp_tt set size days [0-9-]+: ([0-9.]+ -> days [0-9-]+: [0-9.]+)')}) | "
              f"{g(r'E2 nexcp_tt coverage per stage (.*?) ->')} ({g(r'E2 nexcp_tt set size days [0-9-]+: ([0-9.]+ -> days [0-9-]+: [0-9.]+)')}) | "
              f"{g(r'E5 mart_tt vs none_tt: days [0-9-]+ ([0-9.]+ vs [0-9.]+ \([+-][0-9.]+)')}) | {g(r'short-hl weight day [0-9]+ ([0-9.]+ -> days [0-9-]+ [0-9.]+)')} |")
for R in regimes:
    md += ["", f"## {R}", "", rows(R, ["none_mf", "none_tt", "none_tt72", "none_tt24", "mart_tt", "mart_tt72", "bma_tt"]), ""]
    for ag in ["ocp_tt", "nexcp_tt"]:
        md += [section(R, f"{ag}: coverage"), ""]
    for ag in ["mon_tt", "mon_tt72", "mon_tt24", "mart_tt"]:
        s = section(R, f"{ag}: fire days")
        if s:
            md += [s, ""]
    md += [section(R, "bma_tt: mean weight"), "", "expectation checks:", "", checks(R)]
(U / "report_auto.md").write_text("\n".join(md) + "\n")
print("\n".join(md[:4 + len(regimes)]))
