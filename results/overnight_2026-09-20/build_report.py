"""Assemble report.md from narrative.md (hand-written) plus selected tables of the summary files."""
import pathlib, re
R = pathlib.Path(__file__).parent


def section(md: str, start: str, end_level: int) -> str:
    """The text from the heading that starts with ``start`` up to the next heading of level <= end_level."""
    lines = md.splitlines()
    out, on = [], False
    for l in lines:
        if l.startswith("#") and l.lstrip("#").strip().startswith(start):
            on = True
        elif on and l.startswith("#") and len(l) - len(l.lstrip("#")) <= end_level:
            break
        if on:
            out.append(l)
    return "\n".join(out).strip() + "\n"


classical = (R / "classical_summary.md").read_text()
llm = (R / "llm_summary_p4.md").read_text() if (R / "llm_summary_p4.md").exists() else ""
dens = (R / "llm_summary_density.md").read_text() if (R / "llm_summary_density.md").exists() else ""
narr = (R / "narrative.md").read_text()

parts = [narr, "", "---", "", "# Tables", "",
         "All numbers pool every household listed in each table's header (per-household record counts are in the summary files). "
         "Day columns: `*` = every household shifts that day (weekend), `°` = some households shift (guests or illness).", ""]
parts += ["## A. Classical agents, 20 households", "", "Source: `classical_summary.md` (every density and look mode).", ""]
parts += ["### A1. Accuracy per day, patrol every 4 h, look off", "", section(classical, "patrol every 4 h, look off", 3)]
parts += ["### A2. Accuracy per day, patrol every 4 h, look voi (the brief's look rule)", "", section(classical, "patrol every 4 h, look voi", 3)]
parts += ["### A3. Accuracy per day, patrol every 4 h, look top (look at the belief's argmax room)", "", section(classical, "patrol every 4 h, look top", 3)]
parts += ["### A4. Accuracy vs patrol density", "", section(classical, "2. Accuracy vs patrol density", 2)]
parts += ["### A5. What the free look is worth", "", section(classical, "3. What the free look is worth", 2)]
parts += ["### A6. Abstain rate and answered accuracy per day", "", section(classical, "4. Abstain rate", 2)]
if llm:
    parts += ["## B. LLM agents (Qwen3.8-27B, local) next to the classical agents on the same 4 h banks", "", "Source: `llm_summary_p4.md`.", ""]
    parts += ["### B1. Accuracy per day, look off", "", section(llm, "patrol every 4 h, look off", 3)]
    parts += ["### B2. Accuracy per day, LLM with the look on (`look llm`) and classical `look voi`", "", section(llm, "patrol every 4 h, look llm", 3), section(llm, "patrol every 4 h, look voi", 3)]
    parts += ["### B3. Told vs not told", "", section(llm, "5. Told vs not told", 2)]
    parts += ["### B4. Abstain: outright ABSTAIN answers and confidence thresholds", "", section(llm, "4. Abstain rate", 2)]
if dens:
    parts += ["## C. LLM agents vs patrol density (look on)", "", "Source: `llm_summary_density.md`.", "", section(dens, "2. Accuracy vs patrol density", 2)]
(R / "report.md").write_text("\n".join(parts))
print("wrote report.md")
