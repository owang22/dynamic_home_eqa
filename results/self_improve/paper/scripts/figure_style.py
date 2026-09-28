#!/usr/bin/env python3
r"""One place for the paper's figure style: the text width, the type sizes and the method colours.

THE TEXT WIDTH IS A GUESS AND MUST BE CHECKED. `corl_2026.sty` is not in this repository and is
not anywhere under the home directory, so the number below could not be read from it. Put
`\showthe\textwidth` (or `\the\textwidth`) in the draft, or pass the real value:

    CORL_TEXTWIDTH_IN=5.87 python3 results/self_improve/paper/scripts/make_figures.py

If the width is wrong, LaTeX rescales the figure and the type stops being 8 to 9 pt, which is the
one thing the brief asked for, so nothing here sets a width per figure - every figure is drawn at
the width below and never scaled in the document (use \includegraphics without a width).

THE COLOURS WERE VALIDATED, NOT EYEBALLED, with the dataviz skill's checker:

    validate_palette.py "#0072B2,#D55E00,#009E73,#785EF0,#E69F00,#56B4E9,#CC79A7" --mode light
      lightness band PASS, chroma floor PASS, CVD separation PASS (worst adjacent dE 9.6 deutan),
      normal-vision floor PASS (worst adjacent dE 20.0), contrast WARN on three of them

The first four - the methods that share an axis in Figures 2 and 3 - also pass with `--pairs all`
and no warning at all, which is the stricter test and the one that matters when four lines are on
top of each other. The contrast warning on the other three obliges visible labels rather than a
legend box alone, so every line in every figure here is labelled directly.
"""
import os

TEXT_WIDTH_IN = float(os.environ.get("CORL_TEXTWIDTH_IN", "5.5"))
TEXT_WIDTH_WAS_GIVEN = "CORL_TEXTWIDTH_IN" in os.environ

# 8 to 9 pt at final size, and the figures are never rescaled, so these ARE the final sizes.
SIZES = {"font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
         "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
         "figure.titlesize": 9}

COLOUR = {"LastSeen": "#0072B2",
          "log and notes": "#D55E00",
          "claim store": "#009E73",
          "ACE": "#785EF0",
          "reduced ACE": "#E69F00",
          "small working memory": "#56B4E9",
          "notes hidden": "#CC79A7"}

ILLNESS_SHADE = "#e8e8e6"        # light grey, the same for every illness spell
GRID = "#d8d8d4"
INK = "#1a1a1a"
MUTED = "#6b6b68"


def apply(plt):
    plt.rcParams.update({
        **SIZES,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "dejavuserif",
        "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False,
        "pdf.fonttype": 42, "ps.fonttype": 42,     # real text in the PDF, not outlines
        # NOT "tight". A tight box crops each figure to its own content, so four figures drawn
        # at one width come out 343 to 351 pt wide and each is rescaled by a different factor in
        # the document - which silently undoes the 8-to-9 pt type this file exists to fix.
        # Every figure is laid out inside a fixed canvas instead, and included with no width.
        "savefig.bbox": "standard", "savefig.pad_inches": 0.01,
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.h_pad": 0.02, "figure.constrained_layout.w_pad": 0.02,
        "figure.dpi": 150,
    })
