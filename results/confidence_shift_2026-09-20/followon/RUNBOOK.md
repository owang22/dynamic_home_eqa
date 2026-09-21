# Follow-on runbook (Shift Baselines)

All commands from `~/robot/dynamic_home_eqa/src`. R = `../results/confidence_shift_2026-09-20`.
Artifact: https://claude.ai/artifact/PMxnzQYbCmFtAFm22hPb4G , published from `$R/followon/page.html`
(pass that url to the Artifact tool when publishing from another session).

## When new mixture logs land (heldout_p8/hyp/logs/hh_s<N>_p8_longleaf_{told,not_told}.jsonl)

    S=<seed>; T=p8; H=$R/heldout_p8
    LIVE=$H/hyp/study/hh_s${S}_p2__bank0/arms/passive/passive__longleaf__longleaf_named__told/live.jsonl   # check the exact study dir name under $H/hyp/study
    python3 -m baselines.patrol.mixture_reset --log $LIVE --bank $H/banks/hh_s${S}_${T}.jsonl --lists $R/followon/affected_llm/lists.jsonl --out $R/followon/$T/mixture_reset/hh_s${S}_told_reset.jsonl
    python3 -m baselines.patrol.aci --log $LIVE --out $R/followon/$T/aci/hh_s${S}_mix_aci.jsonl --gamma 0.05

The told / not-told mixture lines themselves are read straight from $H/hyp/logs by followon_figs (no step needed).

## Regenerate and publish (any time)

    for T in p8 p2; do
      python3 -m baselines.patrol.followon_figs   --root $R --out $R/followon/$T/figs --tag $T     # PNGs + tables.md + collect() data
      python3 -m baselines.patrol.followon_checks --root $R --tag $T                                # -> followon/$T/checks.md
    done
    python3 -m baselines.patrol.followon_page --root $R --out $R/followon/page.html                 # live chart page
    # then publish $R/followon/page.html to the artifact url above

## A new patrol density / protocol (e.g. nightly + found-it feedback)

1. Labels are per density because "fresh" = placement made after the last observation pass before the question.
   `affected.py` takes the pass times from the bank's `room_visit` rows only. If the new protocol adds other
   observation rows (look results, found-it feedback), extend `read`/`patrol_ts` in `label_bank` to include them.
       python3 -m baselines.patrol.affected --banks $R/heldout_<tag>/banks --sim-dir ../data/situation_sim/confshift/ev10 --out $R/followon/affected --suffix <tag>
2. Counter lines (seconds):
       for S in $(seq 10 29); do b=$R/heldout_<tag>/banks/hh_s${S}_<tag>.jsonl
         for v in none detect told; do python3 -m baselines.patrol.bocpd --bank $b --out $R/followon/<tag>/bocpd/hh_s${S}_${v}.jsonl --variant $v; done
         python3 -m baselines.patrol.bocpd --bank $b --out $R/followon/<tag>/bocpd/hh_s${S}_listed.jsonl --variant listed --lists $R/followon/affected_llm/lists.jsonl
         python3 -m baselines.patrol.bocpd --bank $b --out $R/followon/<tag>/bocpd/hh_s${S}_none_hl24.jsonl --variant none --half-life 24
         python3 -m baselines.patrol.aci --log $R/followon/<tag>/bocpd/hh_s${S}_none.jsonl --out $R/followon/<tag>/aci/hh_s${S}_mf_aci.jsonl --gamma 0.05
       done
   `bocpd.py` replays the bank's evidence stream through the base belief machinery, so any observation kind the
   JsonlBank exposes is consumed; the detector's surprise uses positive sightings only.
3. Affected lists: the prompt depends only on the bank header (residents, rooms, objects, messages), so if
   those are unchanged the calls hit the cache (`affected_llm/cache`); rerun `patrol.affected_llm` with the
   new banks dir and `--labels $R/followon/affected/labels_<tag>.jsonl` to rescore.
4. Add the tag to `followon_figs.collect`/`followon_page` (`--tag`; the page currently hard-codes p8 and p2 in
   `data = {tag: collect(...) for tag in ("p8", "p2")}` and the radio buttons).

## Tuning (already done; only if the density changes)
- detector grid: scratchpad script `tune_bocpd_p8.py` logic = `bocpd.run` over tuning/frozen_<tag>/banks, score shift-day vs non-shift-day firing.
- conformal gamma 0.05: chosen on seeds 0-9 by share of non-shift household-days with coverage in [0.85, 0.95].
- half-life 24 h: accuracy / log-loss on tuning/frozen_p8 seeds 0-9.

## Do not
- write under heldout*/ (the other agent's), or overwrite anything under followon/ — move to *_v1 instead.
