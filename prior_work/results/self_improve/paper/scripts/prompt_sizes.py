#!/usr/bin/env python3
"""Did this cell read the sighting log at search time? Measured, not inferred from a date.

Until 2026-09-26 `search_driven` tested the arm name with `==` against one name, so the five
variants built on the log-and-notes arm searched with no log (see
results/self_improve/wave_reasons_first/THE_FIVE_VARIANTS_READ_NO_LOG.md). The log is thousands
of characters, so the mean prompt size of a cell says plainly whether it was there: the parent
arm sits near 19,000 characters a call and a cell with no log near 9,500.

    python3 results/self_improve/paper/scripts/prompt_sizes.py
"""
import json
import pathlib
import statistics

CELLS = [
    ("reasons_first   log and notes          hh_s2", "wave_reasons_first/cells/the_log_and_notes_about_the_routine/hh_s2_t03"),
    ("reasons_first   told the night before  hh_s2", "wave_reasons_first/cells/ours_told_the_night_before/hh_s2_t03"),
    ("reasons_first   told on the first night hh_s2", "wave_reasons_first/cells/ours_told_on_the_first_night/hh_s2_t03"),
    ("family reads    log and notes          hh_s2", "wave_the_family_reads_the_log/cells/the_log_and_notes_about_the_routine/hh_s2_t03"),
    ("family reads    told the night before  hh_s2", "wave_the_family_reads_the_log/cells/ours_told_the_night_before/hh_s2_t03"),
    ("family reads    told and committed     hh_s2", "wave_the_family_reads_the_log/cells/ours_told_and_asked_what_changes/hh_s2_t03"),
    ("second illness  told the night before  hh_s2", "wave_the_second_illness/cells/ours_told_the_night_before/hh_s2_t03"),
    ("second illness  log and notes          hh_s2", "wave_the_second_illness/cells/the_log_and_notes_about_the_routine/hh_s2_t03"),
    ("wider homes     told the night before  hh_s32", "wave_told_on_the_wider_homes/cells/ours_told_the_night_before/hh_s32_t03"),
]


def main() -> int:
    for name, tail in CELLS:
        f = pathlib.Path("results/self_improve") / tail / "call_times.jsonl"
        if not f.exists():
            print(f"{name:44s} no call_times.jsonl")
            continue
        sizes = [json.loads(l)["n_prompt_characters"] for l in f.open()]
        print(f"{name:44s} calls {len(sizes):5d}  mean prompt characters "
              f"{round(statistics.mean(sizes)):6d}  largest {max(sizes):6d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
