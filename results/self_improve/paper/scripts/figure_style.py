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

# ONE COLOUR AND ONE MARKER PER METHOD, IN EVERY FIGURE OF THE PAPER. A reader who learns that
# orange-with-a-circle is our arm in Figure 2 must not have to relearn it in Figure 4.
MARKER = {"LastSeen": "o", "log and notes": "s", "claim store": "^", "ACE": "D",
          "reduced ACE": "v", "small working memory": "P", "notes hidden": "X",
          "household mode": "*", "room first": "o", "reason first": "s"}

COLOUR = {"LastSeen": "#0072B2",
          "log and notes": "#D55E00",
          "claim store": "#009E73",
          "ACE": "#785EF0",
          "reduced ACE": "#E69F00",
          "small working memory": "#56B4E9",
          "notes hidden": "#CC79A7",
          "household mode": "#117733",
          "room first": "#6b6b68", "reason first": "#D55E00"}

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


def regimes(ax, spans, top=None, letters=True):
    """Name the regimes inside the axes and mark each transition, as F2_relearning does.

    `spans` is [(first_day, last_day, "normal"|"sick"), ...] in order. The words go above the
    stretch they describe, each change of regime gets a dotted vertical line, and the lines are
    lettered A, B, C so a caption can point at one. Nothing is shaded: with two or three lines and
    a zoomed y axis the words carry it, and shading competes with the data.
    """
    # ABOVE THE AXES, NOT INSIDE THEM. Written inside, the word "sick" lands on whichever line
    # happens to be high that week - it did, on the first draft.
    names = "ABCDEFG"
    edge = 0
    for i, (first, last, name) in enumerate(spans):
        ax.annotate(name, xy=((first + last) / 2, 1.015), xycoords=("data", "axes fraction"),
                    ha="center", va="bottom", fontsize=8.5, color=MUTED,
                    fontweight="bold" if name == "sick" else "normal", annotation_clip=False)
        if i:
            ax.axvline(first - 0.5, color=INK, lw=0.9, ls=(0, (1.5, 1.8)), zorder=1)
            if letters:
                # INSIDE the axes, at the top, beside its own line. Above the axes they sat on the
                # regime words: with four transitions the words and the letters ran together into
                # "normalC" and "B normal".
                ax.annotate(names[edge], xy=(first - 0.5, 0.985),
                            xycoords=("data", "axes fraction"), ha="left", va="top",
                            fontsize=8.5, color="#b03020", fontweight="bold",
                            xytext=(2, 0), textcoords="offset points")
            edge += 1


def legend_below(fig, ax, entries, ncol=None):
    """One legend under the plot: a line-and-marker swatch and bold text, per method."""
    handles = [ax.plot([], [], color=COLOUR[name], marker=MARKER[name], lw=2.0, ms=5,
                       markeredgecolor="white", markeredgewidth=0.6, label=name)[0]
               for name in entries]
    leg = fig.legend(handles=handles, loc="lower center", ncol=ncol or len(entries),
                     fontsize=8.5, frameon=False, handlelength=1.8,
                     columnspacing=1.4, borderpad=0.0, handletextpad=0.5)
    for text in leg.get_texts():
        text.set_fontweight("bold")
    return leg


def line(ax, x, y, name, lw=2.0):
    """One method's average line, drawn the same way everywhere."""
    return ax.plot(x, y, color=COLOUR[name], marker=MARKER[name], lw=lw, ms=4.2,
                   markeredgecolor="white", markeredgewidth=0.6, zorder=4, label=name)[0]
