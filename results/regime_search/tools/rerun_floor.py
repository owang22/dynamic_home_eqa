"""How much of a difference is just the run being run again -- ONE source, read by every artifact that quotes it.

The figure folders and the page both state this floor. If each typed it beside the measurement they would drift,
which is the fault this project hit three times in one night at three levels: a table recomputed beside a line
instead of from it, prose typed beside a table instead of read from it, and a number quoted from another strand
instead of imported from it. Same rule each time -- the quote is computed from the source.

Measured by the memory strand by re-running an arm over the same data with byte-identical prompts. When a new
measurement lands, edit VALUES and nothing else.

The one thing not to do with these numbers: apply one arm's floor to another arm, or the all-days floor to a
single window. See PER_ARM and the note on window_worst.
"""

# Per arm, because no arm inherits another's floor. The counting methods are in here too, with zero, because
# their exemption is a measurement now and not an argument from their implementation.
PER_ARM = {
    "the recent-sightings list": {"households": 3, "answers_changed_pct": 3},
    "the whole-log-in-the-prompt memory": {"households": 3, "answers_changed_pct": 5,
                                           "by_hh": [4, 6, 4]},
}

VALUES = {
    "households": 3,
    "alldays_points": "0 to 2",
    # The number that matters most, and the one a reader will otherwise get wrong. Across all days the floor is
    # small; inside ONE window of ONE household it reached ten points -- hh_s2's last two days went 78 to 88.
    # Our headline message result is stated per window, so quoting the all-days figure beside it misleads.
    "window_worst": 10,
    "window_worst_where": "one household's last two days, 78 to 88",
    "window_worst_other": "another household's lead-up, 66 to 62",
    "pooled_mean": 0.0, "pooled_mean_abs": 1.2, "pooled_spread": 1.8,
    "by_window": {"lead-up": 1.8, "first sick days": -0.7, "later spell": 0.0,
                  "first days back": 0.7, "days 27-28": -2.1},
    # Written as unresolved rather than as either prediction winning. The coordinator predicted the longer
    # prompt would have the larger floor and it points that way; the strand's own estimate sits inside the
    # noise. At three households neither is a result.
    "longer_prompt_verdict": ("Whether the longer prompt carries a genuinely larger floor is unresolved: "
                              "slightly larger on average, carried by one household, and not distinguishable "
                              "at three households"),
    "classical_reproduced": ("were re-run and reproduced exactly: one household's whole classical arm, all "
                             "nine beliefs and 4464 rows, came back byte-identical to the stored log, as did "
                             "the question bank it was scored on"),
}


def by_window_text():
    return ", ".join(f"{k} {v:+.1f}" if v else f"{k} {v:.1f}" for k, v in VALUES["by_window"].items())


def per_arm_text():
    return "; ".join(f"{name} about {d['answers_changed_pct']}%"
                     + (" (" + ", ".join(f"{v}%" for v in d["by_hh"]) + " by household)" if d.get("by_hh") else "")
                     for name, d in PER_ARM.items())


def biggest_window_floor():
    """The largest by-window MEAN across households -- not the worst single household-window, which is
    VALUES["window_worst"] and is five times larger. Anything comparing an effect to "the floor" has to say
    which of the two it means."""
    return max(abs(v) for v in VALUES["by_window"].values())
