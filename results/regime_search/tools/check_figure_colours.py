#!/usr/bin/env python3
"""Check the colours the paper figures ACTUALLY RENDER, pair by pair, under every colour deficiency.

    python3 tools/check_figure_colours.py            (from results/regime_search)

Three rules, each of which exists because breaking it hid a real failure:

  AS RENDERED, not as declared. F6 draws its "handed over" bars as the series colour at 42% opacity. Checking
  the base hues says they are far apart; the bars a reader sees are two pale tints composited over white and
  they collapse to dE 9.0. A check on source colours cannot see that, so this one reads the SVG the figure
  actually produced and composites every alpha itself.

  PAIRS THAT CO-OCCUR, not the palette's own ordering. The validator's default walks adjacent entries in the
  list it was handed. Two colours that never appear together are not a problem; two that share a figure are,
  wherever they sit in the list. Retrieval against the 3-day timetable was dE 2.5 under deuteranopia and got
  through because they were not adjacent.

  ALL THREE DEFICIENCIES. Perpetua* against the never-forgets blue was fine under both red-green forms and
  5.5 under tritanopia. A red-green-only check would have passed it, and would have missed F6 entirely.

Reference lines count as series: F4's red promise line has to be distinguishable from the green it crosses.
"""
import collections
import glob
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "figures")
VP = "/tmp/claude-1027/bundled-skills/2.1.278/c703a287f8b9a0fa9c4421b925f3d298/dataviz/scripts/validate_palette.py"
FLOOR, NORMAL_FLOOR = 8.0, 15.0
# chrome: axes, gridlines, text, the plot ground. Not data, and not something a reader must tell apart.
CHROME = {"#ffffff", "#444444", "#555555", "#dddddd", "#cccccc", "#141413", "#666666", "#333333", "#e0e0e0"}


def load_validator():
    spec = importlib.util.spec_from_file_location("vp", VP)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def over_white(hexc, alpha):
    """Composite a colour at alpha over white -- what the eye receives, which is what must be separable."""
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(c * alpha + 255 * (1 - alpha)) for c in (r, g, b))


def rendered_colours(svg_path):
    """Every distinct colour a reader sees as DATA in one figure, alphas composited."""
    s = open(svg_path).read()
    out = collections.Counter()
    for style in re.findall(r'style="([^"]*)"', s):
        if "font-size" in style:                       # text is ink, not a series
            continue
        col = re.search(r'(?:fill|stroke):\s*(#[0-9a-fA-F]{6})', style)
        if not col:
            continue
        c = col.group(1).lower()
        if c in CHROME:
            continue
        op = re.search(r'opacity:\s*([\d.]+)', style)
        a = float(op.group(1)) if op else 1.0
        if a < 0.2:                                    # a whisper of a band, not something to tell apart
            continue
        out[over_white(c, a)] += 1
    return out


def main():
    vp = load_validator()
    modes = ("protan", "deutan", "tritan")
    worst_overall, problems = [], []
    for folder in sorted(os.listdir(FIGS)):
        svgs = glob.glob(os.path.join(FIGS, folder, "*.svg"))
        if not svgs:
            continue
        cols = rendered_colours(svgs[0])
        keys = sorted(cols)
        print(f"\n{folder}  ({len(keys)} rendered data colours)")
        rows = []
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                cvd = {m: vp.deltaE(a, b, m) for m in modes}
                rows.append((min(cvd.values()), vp.deltaE(a, b), a, b, cvd))
        rows.sort()
        for w, n, a, b, cvd in rows[:3]:
            bad = w < FLOOR or n < NORMAL_FLOOR
            tag = "  FAIL" if bad else ""
            print(f"   {a} vs {b}  worst {w:5.1f} (" +
                  " ".join(f"{m[:4]} {cvd[m]:.1f}" for m in modes) + f")  normal {n:5.1f}{tag}")
            if bad:
                problems.append((folder, a, b, w, n))
        if rows:
            worst_overall.append((rows[0][0], folder))
    print("\n" + "=" * 78)
    if problems:
        print(f"{len(problems)} FAILING PAIR(S):")
        for folder, a, b, w, n in problems:
            print(f"   {folder}: {a} vs {b}  worst CVD {w:.1f}  normal {n:.1f}")
    else:
        print("every rendered pair in every figure clears the floor under all three deficiencies")
    worst_overall.sort()
    print(f"tightest figure: {worst_overall[0][1]} at dE {worst_overall[0][0]:.1f}" if worst_overall else "")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
