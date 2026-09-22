#!/usr/bin/env python3
"""Live extractor for in-progress and finished LLM-strategy arms: while an arm is still running,
baselines.patrol.llm only has calls.jsonl (streamed, one line per LLM call) — run_log.jsonl is written once at the
very end. This script reads whichever is on disk right now for every known arm directory, joins each answered
question back to the bank's truth (by question_id, exact match — the same id the arm used as its own "where" tag
on every question call, so the join needs no guessing), and writes per-day [n, ok, sum_raw, sum_leadcal] per
household per arm into story_extra.json under "llm_live", one block per population this study has LLM arms on:
"household" (sick10_all, this session's own runs), "partial" (sick10_partial, this session's wide/chain runs and
the workshop session's partial/partial_told runs), and "person" (sick10_owner, the workshop session's one-person-
sick runs: run1 "no message", run2_told "start message" (told on the first sick day), run3_toldret "start + end
messages" (also told on the first return day)). All bank files an arm was actually run against were confirmed
byte-identical (or, for run3_toldret, identical apart from the header's hint_messages list) to this study's own
regime banks before wiring the join, so questions/truth need no separate loading per source. On-disk run
directory names (run1/run2_told/run3_toldret, this session's own chain_person/{nottold,told_entry,
told_entryreturn}) are kept as they are -- only the user-facing labels and the keys below are "no message" /
"start message" / "start + end messages", per Oliver's naming decision; msg_tag() below is the one place that maps
between the two.

sum_leadcal is a real lead-day (days 1-13) calibration fit, same method as gap_extra.py (bin by confidence, then
pool-adjacent-violators over the ordered bins so the map is monotone), applied per arm pooled across whatever
households currently have lead-day data for it — reused from gap_extra.py rather than re-implemented.

Safe to re-run at any point, including while arms are still writing: run_log.jsonl is preferred when present
(clean, authoritative); calls.jsonl is parsed and filtered to rows whose "where" matches a real question_id
otherwise (notes/noticing calls use different where-tags and are skipped automatically by the join failing).

    python3 tools/llm_live_extra.py  (run from results/regime_search)
"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import load  # noqa
from gap_extra import fit_lead_map, apply_map, LEAD_DAYS  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LLM_DIR = os.path.join(os.path.dirname(ROOT), "confidence_shift_2026-09-20", "uq", "llm_strategies")
FM = "/home/oliver/robot/dynamic_home_eqa_fm/results/fm_memory"
LABEL = "t03"
ARM_RE = re.compile(r"^(hh_s\d+)_(t\d+)_([a-z0-9]+)_(nottold|told)_look(on|off)$")

MEM_NAME = {"naive": "LLM, naive memory (buffer)", "recent": "LLM, recent-K memory", "summary": "LLM, nightly summary",
            "routine": "LLM, routine notes", "routine7": "LLM, 7-day routine notes", "retrieval": "LLM, retrieval memory",
            "longcontext": "LLM, long-context memory", "reflect": "LLM, reflection notes"}
# Oliver's naming decision: the three told-status arms of every memory kind are "no message" / "start message"
# (told on the first sick day) / "start + end messages" (also told on the first return day) -- everywhere
# user-facing (page, tables, EXPECTATIONS/STATUS/REPORT/problems_found, and these story_extra.json keys). On-disk
# run directory names keep their old "told"/"nottold"/"entry"/"entryreturn" spelling (5a's layout, this session's
# own chain_person/*); msg_tag() is the one place that maps a (told, key_tag) pair from a directory name to the
# new key/label vocabulary.
MSG_LABEL = {"nomsg": " · no message", "startmsg": " · start message", "startend": " · start + end messages"}


# Households whose data exists on disk but is deliberately NOT used, so the page shows a clean household count
# rather than something half-finished. Long-context costs ~10x the compute per question of the other memories; its
# told arms were only ever run on hh_s0-s2, so finishing the other seven no-message households could not improve any
# comparison and the server time went to the two-spells arms instead (coordinator, 05:20).
ABANDONED = {("person", "longcontext", "nomsg"): {f"hh_s{i}" for i in range(3, 10)}}


def msg_tag(told: bool, key_tag) -> str:
    if not told:
        return "nomsg"
    return "startend" if key_tag == "entryreturn" else "startmsg"
# 5-window report used to validate a join against a partner's own numbers, mirroring gap_extra.py's 3-window
# REPORT_WINDOWS but split further (14-16 vs the rest of the sick spell; 24-26 vs the rest of the return). "lead"
# here is the last 5 lead days (9-13, the workshop's and this study's own "last5lead" convention elsewhere, e.g.
# uq_windows.py/shared_state_extra.py) -- the saturated end of the ramp-up, not the full 1-13 climb; averaging in
# days 1-8 pulls a ~78% figure down to ~74% and was the one mismatch found while validating this against 5a's
# numbers (see PROBLEMS/EXPECTATIONS notes for the check).
WINDOWS5 = {"lead": set(range(9, 14)), "d14_16": {14, 15, 16}, "d17_23": set(range(17, 24)),
            "d24_26": {24, 25, 26}, "d27_31": set(range(27, 32))}
WINDOWS5_LABEL = {"lead": "lead (9–13)", "d14_16": "14–16", "d17_23": "17–23", "d24_26": "24–26", "d27_31": "27–31"}
# the two-spells regime (sick2x_owner: lead 0-13, sick 14-20, back 21-27, sick 28-34, back 35-41): first three days and
# the rest of every stage, so the second break/re-learning can be read against the first
WINDOWS2X = {"lead": set(range(9, 14)), "s1a": {14, 15, 16}, "s1b": set(range(17, 21)), "r1a": {21, 22, 23}, "r1b": set(range(24, 28)),
             "s2a": {28, 29, 30}, "s2b": set(range(31, 35)), "r2a": {35, 36, 37}, "r2b": set(range(38, 42))}
WINDOWS2X_LABEL = {"lead": "lead (9–13)", "s1a": "sick 14–16", "s1b": "sick 17–20", "r1a": "back 21–23", "r1b": "back 24–27",
                   "s2a": "sick again 28–30", "s2b": "sick again 31–34", "r2a": "back again 35–37", "r2b": "back again 38–41"}


def windows_for(pop):
    return (WINDOWS2X, WINDOWS2X_LABEL) if pop == "person2x" else (WINDOWS5, WINDOWS5_LABEL)

# (glob pattern for arm dirs, population key, bank dir, key tag [None = plain mem_kind_told key], mem_kind allow-list
# [None = all]) -- population determines which bank file (and so which truth) an arm's answers are checked against.
SOURCES = [
    # the sick10_all ("household") LLM arms were stopped at ~100-120/744 when Oliver redirected this session to
    # get the one-person suite clean first (see STATUS.md); removed from the page entirely rather than shown as
    # stale/stopped lines -- the raw logs are untouched on disk (wide/, chain/sick10_all/) if resumed later.
    (f"{LLM_DIR}/chain/sick10_partial/*", "partial", f"{ROOT}/sick10_partial/banks", None, None),
    (f"{FM}/partial/*", "partial", f"{ROOT}/sick10_partial/banks", None, None),
    (f"{FM}/partial_told/*", "partial", f"{ROOT}/sick10_partial/banks", None, None),
    # one-person-sick population: run1 = "no message"; run2_told = "start message" (told when the person gets
    # sick, day 14 hint, only); run3_toldret = "start + end messages" (also told on the return, day 24) --
    # distinct conditions, kept as distinct arms rather than pooled, since an end message should change exactly
    # the return-window numbers.
    (f"{FM}/run1/*", "person", f"{ROOT}/sick10_owner/banks", None, {"naive", "routine7"}),
    (f"{FM}/run2_told/*", "person", f"{ROOT}/sick10_owner/banks", "entry", {"naive", "routine7"}),
    (f"{FM}/run3_toldret/*", "person", f"{ROOT}/sick10_owner/banks", "entryreturn", {"naive", "routine7"}),
    # this session's own person-regime chain (retrieval/longcontext/reflect), same bank/cache-reuse pattern as
    # run1/run2_told/run3_toldret above -- separate --out dirs per told-status, see run_chain_person.sh
    (f"{LLM_DIR}/chain_person/nottold/*", "person", f"{ROOT}/sick10_owner/banks", None, None),
    (f"{LLM_DIR}/chain_person/told_entry/*", "person", f"{ROOT}/sick10_owner/banks", "entry", None),
    (f"{LLM_DIR}/chain_person/told_entryreturn/*", "person", f"{ROOT}/sick10_owner/banks", "entryreturn", None),
    # the two-spells regime: no message and start message (the bank puts a "home sick today" hint on every sick day of
    # BOTH spells, so the start-message arm is told at both breaks)
    (f"{LLM_DIR}/chain_person2x/nottold/*", "person2x", f"{ROOT}/sick2x_owner/banks", None, None),
    (f"{LLM_DIR}/chain_person2x/told_entry/*", "person2x", f"{ROOT}/sick2x_owner/banks", "entry", None),
]


def arm_answers(arm_dir):
    """-> {question_id: (location, confidence)}, from run_log.jsonl if finished, else calls.jsonl."""
    rl = os.path.join(arm_dir, "run_log.jsonl")
    if os.path.exists(rl):
        out = {}
        for l in open(rl):
            r = json.loads(l)
            out[r["question_id"]] = (r.get("answer"), r.get("top_prob"))
        return out
    cp = os.path.join(arm_dir, "calls.jsonl")
    if not os.path.exists(cp):
        return {}
    out = {}
    for l in open(cp):
        try:
            r = json.loads(l)
        except ValueError:
            continue  # a partially-flushed last line while the arm is mid-write
        qid = r.get("where")
        if not qid or qid in out:
            continue
        try:
            c = json.loads(r["completion"])
        except (ValueError, TypeError, KeyError):
            continue
        loc = c.get("location")
        conf = c.get("confidence")
        if loc is None:
            continue
        out[qid] = (loc, float(conf) if isinstance(conf, (int, float)) else 0.0)
    return out


class AskGate:
    """Adaptive-conformal answer-or-ask gate on a model's OWN stated confidence (Gibbs & Candes-style decaying-step
    online control, same math as DecayingStepConformal in uq_agents.py, but re-derived for a scalar confidence
    rather than a candidate set — see uq/problems_found.md for why the two need opposite update signs). q is the
    MINIMUM confidence required to trust the model's own answer instead of asking the resident; asking always
    succeeds (found-it feedback gives the truth either way), so a "miss" only exists among answered questions.
    Target: among questions the gate lets through, roughly `alpha` should be wrong.
    """

    def __init__(self, alpha: float = 0.10, eta0: float = 0.05, eps: float = 0.1, eta_min: float = 0.005, warm: int = 20):
        self.alpha, self.eta0, self.eps, self.eta_min, self.warm = alpha, eta0, eps, eta_min, warm
        self.q = 0.5
        self.t = 0
        self._first: list = []

    def decide(self, confidence: float) -> str:
        return "answer" if confidence >= self.q else "ask"

    def update(self, confidence: float, correct: bool):
        decided_answer = confidence >= self.q
        missed = decided_answer and not correct
        if len(self._first) < self.warm:
            self._first.append(confidence)
            if len(self._first) == self.warm:
                cs = sorted(self._first)
                self.q = cs[max(0, min(self.warm - 1, int(self.alpha * (self.warm - 1))))]
            return decided_answer, missed
        self.t += 1
        eta = max(self.eta_min, self.eta0 * self.t ** (-0.5 - self.eps))
        self.q += eta * ((1.0 if missed else 0.0) - self.alpha)
        self.q = min(max(self.q, 0.0), 1.0)
        return decided_answer, missed


def run_askgate(rows_chrono, alpha=0.10, windows=None):
    """rows_chrono: [(day, conf, ok), ...] roughly in time order (sorted by day; households interleaved within a
    day, which the gate does not need to get exactly right). -> per-window {n, n_answered, ask_rate, miss_rate,
    q_mean} plus q_before/q_after around day 14 (the "does it tighten at the shift" check)."""
    gate = AskGate(alpha=alpha)
    decisions = []  # (day, answered, missed, q_before_decision)
    for day, conf, ok in rows_chrono:
        q_before = gate.q
        answered, missed = gate.update(conf, bool(ok))
        decisions.append((day, answered, missed, q_before))
    out = {}
    for w, days in (windows or WINDOWS5).items():
        sel = [d for d in decisions if d[0] in days]
        n = len(sel)
        if not n:
            out[w] = None
            continue
        n_ans = sum(1 for d in sel if d[1])
        n_miss = sum(1 for d in sel if d[1] and d[2])
        out[w] = {"n": n, "ask_rate": round(100 * (n - n_ans) / n, 1),
                   "miss_rate": round(100 * n_miss / n_ans, 1) if n_ans else None,
                   "q_mean": round(sum(d[3] for d in sel) / n, 3)}
    pre = [d for d in decisions if d[0] in LEAD_DAYS]
    post = [d for d in decisions if d[0] in {14, 15, 16}]
    q_pre = sum(d[3] for d in pre) / len(pre) if pre else None
    q_post = sum(d[3] for d in post) / len(post) if post else None
    out["_tighten_at_shift"] = {"q_lead": round(q_pre, 3) if q_pre is not None else None,
                                 "q_shift": round(q_post, 3) if q_post is not None else None,
                                 "tightened": bool(q_pre is not None and q_post is not None and q_post > q_pre + 0.01)}
    return out


MIN_N_FOR_SE = 6   # below this the standard error is unreliable, so the old heterogeneity floor still applies


def verdict(mean, sd, n_hh, per_hh=None):
    """The bar as of 07:25, changed by this session and NOT by Oliver (he set the 1-sd rule below and has not ruled on
    this replacement; the page says so in its method note): report mean +- STANDARD ERROR with n as the primary form, keep the sd separately as
    a measure of how much households disagree, and call an effect DETECTED at |mean| >= 2 se. The earlier bar --
    |mean| > sd -- asked whether an effect exceeds household-to-household variation, which is a different question
    from whether it exists; at 18 households a 3.1-se effect was failing it. Below MIN_N_FOR_SE households the se is
    too unreliable to trust and the old floor is what governs (that is the bar that caught the interference claim)."""
    se = sd / (n_hh ** 0.5) if n_hh else float("inf")
    clears_1sd = bool(abs(mean) > sd)
    detected_2se = bool(se > 0 and abs(mean) >= 2 * se)
    small_n = n_hh < MIN_N_FOR_SE
    return {"mean": round(mean, 1), "sd": round(sd, 1), "se": round(se, 2), "n_hh": n_hh,
            "clears_1sd": clears_1sd, "detected_2se": detected_2se, "small_n": small_n,
            # the verdict the page uses: 2 se normally, the old heterogeneity floor when n is too small for a se
            "detected": bool(clears_1sd if small_n else detected_2se),
            "bars_disagree": bool((not small_n) and (detected_2se != clears_1sd)),
            "se_ratio": round(abs(mean) / se, 1) if se else None,
            "per_hh": per_hh}


def window_stats(rows, days):
    """rows: list of (day, conf, ok, leadcal, cold). -> n, acc%, conf%, leadcal_conf%, plus the same on cold questions
    only (first question about an object that day, before that day's feedback), over the given day set; or None."""
    sel = [r for r in rows if r[0] in days]
    n = len(sel)
    if not n:
        return None
    ok = sum(r[2] for r in sel)
    conf = sum(r[1] for r in sel)
    lc = sum(r[3] for r in sel)
    cold = [r for r in sel if r[4]]
    nc = len(cold)
    return {"n": n, "acc": round(100 * ok / n, 1), "conf": round(100 * conf / n, 1), "leadcal_conf": round(100 * lc / n, 1),
            "n_cold": nc, "acc_cold": round(100 * sum(r[2] for r in cold) / nc, 1) if nc else None,
            "conf_cold": round(100 * sum(r[1] for r in cold) / nc, 1) if nc else None}


def main():
    bank_cache = {}
    populations = {"household": {}, "partial": {}, "person": {}, "person2x": {}}
    all_rows = {}  # (pop, key) -> hh -> [(day, conf, ok, moved), ...] -- kept for the lead-fit and the 5-window report
    n_days_by_hh = {}  # (pop, key, hh) -> bank's own n_days, so cell arrays are sized correctly (not guessed from data)
    for pattern, pop, bank_dir, key_tag, mem_allow in SOURCES:
        for arm_dir in sorted(glob.glob(pattern)):
            base = os.path.basename(arm_dir)
            m = ARM_RE.match(base)
            if not m or not os.path.isdir(arm_dir):
                continue
            hh, label, mem_kind, told, look = m.groups()
            if label != LABEL or (mem_allow and mem_kind not in mem_allow):
                continue
            bank_path = f"{bank_dir}/{hh}_{label}.jsonl"
            if not os.path.exists(bank_path):
                continue
            if bank_path not in bank_cache:
                bank_cache[bank_path] = load(bank_path, 2)
            h, qs = bank_cache[bank_path]
            n_days = h["n_days"]
            answers = arm_answers(arm_dir)
            if not answers:
                continue
            mtag = msg_tag(told == "told", key_tag)
            if hh in ABANDONED.get((pop, mem_kind, mtag), ()):
                continue   # on disk, deliberately unused (see ABANDONED)
            key = f"llm_{mem_kind}_{mtag}"
            arm = populations[pop].setdefault(key, {"mem_kind": mem_kind, "told": told, "key_tag": key_tag, "msg_tag": mtag, "n_total_hh": len(qs), "n_hh_done": {}, "n_hh_total": {}})
            arm["n_hh_total"][hh] = len(qs)   # banks differ in size (287-496 questions per household); "finished" is per household
            rows = all_rows.setdefault((pop, key), {}).setdefault(hh, [])
            n_days_by_hh[(pop, key, hh)] = n_days
            n_hh_done = 0
            seen_cold = set()
            for qid, (loc, conf) in answers.items():
                q = qs.get(qid)
                if not q or loc is None:
                    continue
                n_hh_done += 1
                ok = int(loc == q["truth"])
                cold = (q["day"], q["obj"]) not in seen_cold   # first question about that object that day (file order = time order)
                seen_cold.add((q["day"], q["obj"]))
                rows.append((q["day"], float(conf or 0.0), ok, q["moved"], cold))
            arm["n_hh_done"][hh] = n_hh_done

    out = {}
    lines = []
    for pop, arms in populations.items():
        pop_out = {}
        pop_rows = {}   # key -> hh -> rows, used for the matched-household pass below
        for key, arm in arms.items():
            by_hh = all_rows[(pop, key)]
            lead_pts = [(c, ok) for hh, rows in by_hh.items() for (d, c, ok, mv, cold) in rows if d in LEAD_DAYS]
            knots = fit_lead_map(lead_pts)
            cells = {}
            pooled_rows = []  # (day, conf, ok, leadcal, cold) pooled over households, for the 5-window report
            rows_by_hh = {}   # hh -> the same tuples, so a told-vs-untold comparison can be restricted to the
                              # households BOTH arms actually ran on (the banks differ in size and the per-household
                              # spread is several points, so an unmatched comparison is not a result)
            for hh, rows in by_hh.items():
                nd = n_days_by_hh[(pop, key, hh)]
                arr_all = [[0, 0, 0.0, 0.0] for _ in range(nd)]
                arr_mv = [[0, 0, 0.0, 0.0] for _ in range(nd)]
                arr_cold = [[0, 0, 0.0, 0.0] for _ in range(nd)]   # per-day cold, for the panel split
                hh_rows = rows_by_hh.setdefault(hh, [])
                for d, c, ok, mv, cold in rows:
                    if d >= nd:
                        continue
                    lc = apply_map(knots, c)
                    pooled_rows.append((d, c, ok, lc, cold))
                    hh_rows.append((d, c, ok, lc, cold))
                    cell = arr_all[d]
                    cell[0] += 1; cell[1] += ok; cell[2] += c; cell[3] += lc
                    if mv:
                        cell2 = arr_mv[d]
                        cell2[0] += 1; cell2[1] += ok; cell2[2] += c; cell2[3] += lc
                    if cold:
                        cell3 = arr_cold[d]
                        cell3[0] += 1; cell3[1] += ok; cell3[2] += c; cell3[3] += lc
                cells[hh] = {"all": arr_all, "moved": arr_mv, "cold": arr_cold}

            n_hh = len(arm["n_hh_done"])
            done_sum = sum(arm["n_hh_done"].values())
            total_sum = sum(arm["n_hh_total"].values())
            hh_sorted = sorted(arm["n_hh_done"], key=lambda h: int(h.split("_s")[1]))
            complete = n_hh > 0 and all(arm["n_hh_done"][h] >= arm["n_hh_total"][h] for h in arm["n_hh_done"])
            nums = [int(h.split("_s")[1]) + 1 for h in hh_sorted]
            runs = []
            for n in nums:
                if runs and n == runs[-1][1] + 1:
                    runs[-1][1] = n
                else:
                    runs.append([n, n])
            hh_label = "hh " + ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)
            progress = (f"(finished, {done_sum} questions, " if complete else f"(in progress, {done_sum} of {total_sum} questions, ") + hh_label + ")"
            mean_done = round(done_sum / n_hh) if n_hh else 0
            WIN, WLAB = windows_for(pop)
            windows = {w: window_stats(pooled_rows, days) for w, days in WIN.items()}
            gate_rows = sorted(((d, c, ok) for d, c, ok, lc, cold in pooled_rows), key=lambda r: r[0])
            askgate = run_askgate(gate_rows, windows=WIN) if gate_rows else None
            pop_out[key] = {"name": MEM_NAME.get(arm["mem_kind"], arm["mem_kind"]) + MSG_LABEL[arm["msg_tag"]],
                             "mem_kind": arm["mem_kind"], "msg_tag": arm["msg_tag"], "cells": cells,
                             "n_total_hh": arm["n_total_hh"], "n_hh_done": arm["n_hh_done"], "progress": progress,
                             "complete": complete, "has_leadcal": bool(knots), "windows": windows, "window_labels": WLAB, "askgate": askgate,
                             "households": [int(h.split("_s")[1]) + 1 for h in hh_sorted],
                             "abandoned_hh": sorted(int(h.split("_s")[1]) + 1 for h in ABANDONED.get((pop, arm["mem_kind"], arm["msg_tag"]), ()))}
            pop_rows[key] = rows_by_hh
            wtxt = "  ".join(f"{w}: acc {windows[w]['acc'] if windows[w] else 'NA'} conf {windows[w]['conf'] if windows[w] else 'NA'}" for w in WIN)
            if askgate:
                gtxt = "  ".join(f"{w}: ask {askgate[w]['ask_rate'] if askgate[w] else 'NA'}% miss {askgate[w]['miss_rate'] if askgate[w] else 'NA'}%" for w in WIN)
                tt = askgate["_tighten_at_shift"]
                lines.append(f"{pop}/{key}: {n_hh} households, mean {mean_done}/{arm['n_total_hh']} answered — {progress}\n    {wtxt}\n    askgate {gtxt}  tightened_at_shift={tt['tightened']} (q_lead={tt['q_lead']} q_shift={tt['q_shift']})")
            else:
                lines.append(f"{pop}/{key}: {n_hh} households, mean {mean_done}/{arm['n_total_hh']} answered — {progress}\n    {wtxt}")
        # paired told-vs-untold contrasts: per household, (told arm's accuracy on that household) minus (the
        # no-message arm's), then mean +- sd of that difference ACROSS households. Oliver's rule was that an
        # effect must clear one standard deviation (still reported, and still the bar below n=6), and for a paired design the sd of the DIFFERENCES is the right
        # one -- the per-arm sds are dominated by how hard each household is, which cancels in the pairing.
        def hh_window(rows, days, cold_only=False):
            sel = [r for r in rows if r[0] in days and (not cold_only or r[4])]
            return (len(sel), 100 * sum(r[2] for r in sel) / len(sel)) if sel else (0, None)

        def paired(base_key, other_key, days, cold_only=False):
            diffs = []
            for h in sorted(set(pop_rows.get(base_key, {})) & set(pop_rows.get(other_key, {}))):
                nb, ab = hh_window(pop_rows[base_key][h], days, cold_only)
                no, ao = hh_window(pop_rows[other_key][h], days, cold_only)
                if nb >= 5 and no >= 5:
                    diffs.append(ao - ab)
            if len(diffs) < 2:
                return None
            m = sum(diffs) / len(diffs)
            sd = (sum((d - m) ** 2 for d in diffs) / (len(diffs) - 1)) ** 0.5
            return verdict(m, sd, len(diffs), [round(d, 1) for d in diffs])

        # matched-household pass: within each memory kind, restrict every arm to the households present in ALL of
        # that kind's message arms, and store those window stats as windows_matched. A told-vs-untold difference must
        # be read off these, never off the full-household numbers, because the arms do not always cover the same set.
        WIN_p, _ = windows_for(pop)
        by_mem = {}
        for key, arm in pop_out.items():
            by_mem.setdefault(arm["mem_kind"], []).append(key)
        for mem, keys in by_mem.items():
            common = set.intersection(*(set(pop_rows[k]) for k in keys)) if keys else set()
            hh_list = sorted(common, key=lambda h: int(h.split("_s")[1]))
            for k in keys:
                rows = [r for h in common for r in pop_rows[k][h]]
                pop_out[k]["windows_matched"] = {w: window_stats(rows, days) for w, days in WIN_p.items()}
                pop_out[k]["hh_matched"] = [int(h.split("_s")[1]) + 1 for h in hh_list]
                pop_out[k]["matched_is_full"] = len(common) == len(pop_rows[k])
            # two-spells: the reuse question is a paired WITHIN-arm contrast (second spell's first three days minus
            # the first spell's, per household), and it faces the same 1-sd bar as everything else
            if pop == "person2x":
                for k in keys:
                    diffs = []
                    for h, rws in pop_rows.get(k, {}).items():
                        n1, a1 = hh_window(rws, WIN_p["s1a"])
                        n2, a2 = hh_window(rws, WIN_p["s2a"])
                        if n1 >= 5 and n2 >= 5:
                            diffs.append(a2 - a1)
                    if len(diffs) >= 2:
                        m = sum(diffs) / len(diffs)
                        sd = (sum((d - m) ** 2 for d in diffs) / (len(diffs) - 1)) ** 0.5
                        pop_out[k]["reuse_paired"] = verdict(m, sd, len(diffs), [round(d, 1) for d in diffs])
                        lines.append(f"reuse {pop}/{k}: second spell's first three days minus the first spell's = "
                                     f"{m:+.1f} +- {sd:.1f} pp across {len(diffs)} households -> "
                                     f"{'CLEARS 1 sd' if abs(m) > sd else 'does NOT clear 1 sd (say: beyond what three households can tell us)'}")
            # the retraction's OWN effect: start+end versus start-only, the contrast that answers "does telling the
            # robot the disruption is over repair the damage" -- distinct from either arm against never being told
            se, sm = f"llm_{mem}_startend", f"llm_{mem}_startmsg"
            if se in pop_out and sm in pop_out:
                pop_out[se]["paired_vs_startmsg"] = {
                    w: {"all": paired(sm, se, WIN_p[w]), "cold": paired(sm, se, WIN_p[w], True)} for w in WIN_p}
                for w in ("d24_26", "d27_31"):
                    pr = pop_out[se]["paired_vs_startmsg"].get(w) or {}
                    for split in ("all", "cold"):
                        v = pr.get(split)
                        if v:
                            lines.append(f"retraction {pop}/{mem}, {w} {split}: telling again on the first day back vs telling once = "
                                         f"{v['mean']:+.1f} +- {v['sd']:.1f} pp across {v['n_hh']} households -> "
                                         f"{'CLEARS 1 sd' if v['clears_1sd'] else 'does NOT clear 1 sd (undecided)'}")
            base = f"llm_{mem}_nomsg"
            if base in pop_out:
                for k in keys:
                    if k == base:
                        continue
                    pop_out[k]["paired_vs_nomsg"] = {
                        w: {"all": paired(base, k, WIN_p[w]), "cold": paired(base, k, WIN_p[w], True)}
                        for w in WIN_p}   # every window we make a claim about, not just the two headline ones
                    for w, pr in pop_out[k]["paired_vs_nomsg"].items():
                        if w not in ("d14_16", "d17_23", "d24_26", "d27_31"):
                            continue
                        for split in ("all", "cold"):
                            v = pr[split]
                            if v:
                                lines.append(f"paired {pop}/{k} vs no message, {w} {split}: {v['mean']:+.1f} +- {v['sd']:.1f} pp "
                                             f"across {v['n_hh']} households -> {'CLEARS 1 sd' if v['clears_1sd'] else 'does NOT clear 1 sd (report as no measurable difference)'}")
            if len(keys) > 1:
                lines.append(f"matched {pop}/{mem}: {len(keys)} message arms compared on households "
                             f"{', '.join(str(int(h.split('_s')[1]) + 1) for h in hh_list)} "
                             f"({'same set as each arm ran on' if all(pop_out[k]['matched_is_full'] for k in keys) else 'INTERSECTION — full-household numbers are not comparable across these arms'})")
        out[pop] = pop_out
    if not any(out.values()):
        lines.append("no live LLM arm directories found yet under any known source")

    # Contrasts measured on households we did not run (the workshop session's fresh replications), dropped in as
    # JSON so an outside figure can be swapped in without touching page code. Each entry carries its own n_hh and
    # REPLACES our figure for that arm/window/split; our own number is kept alongside as "ours" so the page can say
    # what changed. Format: {pop: {arm_key: {"paired_vs_nomsg"|"paired_vs_startmsg": {window: {split: {...}}}}}}
    pooled_path = f"{ROOT}/pooled_contrasts.json"
    if os.path.exists(pooled_path):
        pooled = json.load(open(pooled_path))
        n_sub = 0
        for pop, arms in pooled.items():
            if pop.startswith("_") or not isinstance(arms, dict):
                continue   # comment keys
            for key, blocks in arms.items():
                arm = out.get(pop, {}).get(key)
                if not arm:
                    continue
                for block, wins in blocks.items():
                    tgt = arm.get(block) or {}
                    for w, splits in wins.items():
                        for split, v in splits.items():
                            v = dict(v)
                            vv = verdict(v["mean"], v["sd"], v["n_hh"])
                            if "se" in v:
                                vv["se"] = v["se"]   # trust the source's own se if it gave one
                                vv["detected_2se"] = bool(abs(v["mean"]) >= 2 * v["se"])
                                vv["detected"] = bool(vv["clears_1sd"] if vv["small_n"] else vv["detected_2se"])
                                vv["se_ratio"] = round(abs(v["mean"]) / v["se"], 1) if v["se"] else None
                                vv["bars_disagree"] = bool((not vv["small_n"]) and (vv["detected_2se"] != vv["clears_1sd"]))
                            vv.update({k2: v[k2] for k2 in ("source",) if k2 in v})
                            v = vv
                            v["pooled"] = True
                            prev = (tgt.get(w) or {}).get(split)
                            if prev:
                                v["ours"] = {k2: prev[k2] for k2 in ("mean", "sd", "n_hh") if k2 in prev}
                            tgt.setdefault(w, {})[split] = v
                            n_sub += 1
                    arm[block] = tgt
        if n_sub:
            lines.append(f"pooled_contrasts.json: {n_sub} figure(s) replaced by outside measurements (see 'ours' for what they replaced)")

    knowno = knowno_block(lines)
    owner_split = owner_split_block(bank_cache, lines)

    cgate = classical_askgate_block()
    for k, v in sorted(cgate.items()):
        g = v["askgate"]
        lines.append(f"classical ask gate {k} ({v['n_hh']} hh): " + "  ".join(
            f"{w} ask {g[w]['ask_rate']:.0f}% miss {g[w]['miss_rate']:.0f}%" for w in WINDOWS5 if g.get(w) and g[w]["miss_rate"] is not None))
    from extra_store import write_keys
    lines.append(write_keys("llm_live_extra", {"llm_live": out, "knowno_live": knowno,
                                               "owner_split_live": owner_split, "classical_askgate": cgate}))
    print("\n".join(lines))


# ------------------------------------------------------------------ KnowNo / three confidence channels --

KNOWNO_SOURCES = [(f"{LLM_DIR}/knowno_person/*", "person")]
KNOWNO_RE = re.compile(r"^([a-z0-9]+)_(hh_s\d+)$")


def knowno_block(lines):
    """uq_llm.py channel logs (3 calls/question: verbalized, sample-agreement, MCQ token probability) on a bounded
    day list, plus a KnowNo conformal set per household built post-hoc from the letter probabilities (same
    machinery as uq_llm_conformal.py: score = 1 - P(option), decaying-step online quantile, alpha 0.1, one
    conformal stream per household in file order = time order). Pooled per day over households."""
    from baselines.patrol.uq_agents import DecayingStepConformal  # src/ is on sys.path via analyze
    letters = "ABCDEFGHIJ"
    out = {}
    for pattern, pop in KNOWNO_SOURCES:
        pop_out = out.setdefault(pop, {})
        per_mem = {}
        for d in sorted(glob.glob(pattern)):
            m = KNOWNO_RE.match(os.path.basename(d))
            if not m or not os.path.isdir(d):
                continue
            mem, hh = m.groups()
            logf = os.path.join(d, f"{hh}.jsonl")
            if not os.path.exists(logf):
                continue
            rows = []
            for l in open(logf):
                try:
                    rows.append(json.loads(l))
                except ValueError:
                    continue
            if not rows:
                continue
            conformal = DecayingStepConformal(alpha=0.1)
            days = per_mem.setdefault(mem, {"days": {}, "hh": set(), "n": 0})
            days["hh"].add(hh)
            for r in rows:
                options = list(r.get("mcq_options") or []) + ["other"]
                lps = r.get("letter_probs") or {}
                scores = {opt: 1.0 - lps.get(letters[i], 0.0) for i, opt in enumerate(options) if i < len(letters)}
                cset = conformal.set_of(scores)
                truth_opt = r["truth"] if r["truth"] in (r.get("mcq_options") or []) else "other"
                covered = truth_opt in cset
                conformal.update(not covered, scores.get(truth_opt, 1.0))
                dd = days["days"].setdefault(str(r["day_index"]), {"n": 0, "ok": 0, "verbal": 0.0, "agree": 0.0, "token": 0.0,
                                                                     "mcq_ok": 0, "covered": 0, "set_size": 0.0})
                dd["n"] += 1; dd["ok"] += int(bool(r.get("correct")))
                dd["verbal"] += float(r.get("top_prob") or 0.0); dd["agree"] += float(r.get("conf_agree") or 0.0)
                dd["token"] += float(r.get("conf_token") or 0.0); dd["mcq_ok"] += int(bool(r.get("mcq_correct")))
                dd["covered"] += int(covered); dd["set_size"] += len(cset)
                days["n"] += 1
        for mem, agg in per_mem.items():
            key = f"llm_{mem}_nomsg"
            day_rows = {}
            for dstr, dd in agg["days"].items():
                n = dd["n"]
                day_rows[dstr] = {"n": n, "acc": round(100 * dd["ok"] / n, 1), "verbal": round(100 * dd["verbal"] / n, 1),
                                   "agree": round(100 * dd["agree"] / n, 1), "token": round(100 * dd["token"] / n, 1),
                                   "mcq_acc": round(100 * dd["mcq_ok"] / n, 1), "coverage": round(100 * dd["covered"] / n, 1),
                                   "set_size": round(dd["set_size"] / n, 2)}
            pop_out[key] = {"name": MEM_NAME.get(mem, mem) + MSG_LABEL["nomsg"], "mem_kind": mem, "days": day_rows,
                             "n_hh": len(agg["hh"]), "n": agg["n"], "households": sorted(agg["hh"])}
            lines.append(f"knowno {pop}/{key}: {len(agg['hh'])} hh, {agg['n']} q; " +
                         "  ".join(f"d{d}: acc {v['acc']} verbal {v['verbal']} agree {v['agree']} token {v['token']} cov {v['coverage']} set {v['set_size']}"
                                   for d, v in sorted(day_rows.items(), key=lambda kv: int(kv[0]))))
    return out


# ------------------------------------------------------------ owner split (shared-memory interference) --

OWNER_SPLIT_SOURCES = [(f"{FM}/partial/*", "partial", f"{ROOT}/sick10_partial/banks", None),
                       (f"{FM}/partial_told/*", "partial", f"{ROOT}/sick10_partial/banks", None),
                       (f"{LLM_DIR}/chain/sick10_partial/*", "partial", f"{ROOT}/sick10_partial/banks", None)]


def bank_owner_info(bank_path):
    """-> (sick_resident_id, {object_id: owner_id or 'shared'}, {question_id: object_id}) from the bank file."""
    h = json.loads(open(bank_path).readline())
    names = {c["name"].lower(): c["resident_id"] for c in h["protocol"]["residents"]}
    sick = None
    for causes in (h.get("day_causes") or {}).values():
        for c in causes:
            if c.startswith("sick_day:"):
                sick = c.split(":", 1)[1]
                break
        if sick:
            break
    owners = {}
    q_obj = {}
    for l in open(bank_path):
        if '"question"' not in l:
            continue
        r = json.loads(l)
        if r.get("kind") != "question":
            continue
        o = r["object_id"]
        q_obj[r["question_id"]] = o
        owners[o] = names.get(o.rsplit("_", 1)[-1].lower(), "shared")
    return sick, owners, q_obj


# Counters put through the SAME answer-or-ask gate as the LLM arms, so the page can show the comparison it has
# been asserting in prose ("the counting methods, for all their simplicity, do better on this score") instead of
# only stating it. Conditions are deliberately identical and not flattering: same AskGate procedure, same alpha,
# same five windows, and the counter's confidence read the same way it is read everywhere else on this page --
# the top probability of its own distribution over places.
CLASSICAL_GATE_BELIEFS = {
    "TimetableLookup(bin=2h,days=all,hl=72h)": ("tt3d", "3-day timetable"),
    "TimetableLookup(bin=2h,days=all)": ("ttfrozen", "never-forgets timetable"),
}


def classical_askgate_block(regime_dir="sick10_owner"):
    """-> {key: {name, n_hh, askgate}} for the counters, on the same population as the LLM person arms."""
    rows_by_key = collections.defaultdict(list)   # key -> [(t_query, day, conf, ok)]
    hh_by_key = collections.defaultdict(set)
    for cp in sorted(glob.glob(f"{ROOT}/{regime_dir}/classical/hh_s*_{LABEL}.jsonl")):
        hh = os.path.basename(cp).split("_" + LABEL)[0]
        for line in open(cp):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            ent = CLASSICAL_GATE_BELIEFS.get(r.get("belief"))
            if not ent:
                continue
            key, _ = ent
            rows_by_key[key].append((r.get("t_query", 0), r["day_index"], float(r.get("top_prob") or 0.0), int(bool(r["correct"]))))
            hh_by_key[key].add(hh)
    out = {}
    for key, rows in rows_by_key.items():
        rows.sort()                                   # chronological, households interleaved -- as for the LLM arms
        gate = run_askgate([(d, c, ok) for _, d, c, ok in rows])
        out[key] = {"name": CLASSICAL_GATE_BELIEFS[[k for k, v in CLASSICAL_GATE_BELIEFS.items() if v[0] == key][0]][1],
                    "n_hh": len(hh_by_key[key]), "askgate": gate}
    return out


def owner_split_block(bank_cache, lines):
    """Per arm on the partial-shift population: accuracy and stated confidence on the SICK resident's things vs
    everyone else's (others = not owned by the sick resident, shared objects included), per 5-window, all
    questions and cold only (first question about an object each day, in file = time order). This is the
    "does a message about one person leak into the other person's things through a shared memory" number."""
    info_cache = {}
    per_arm = {}
    for pattern, pop, bank_dir, _ in OWNER_SPLIT_SOURCES:
        for arm_dir in sorted(glob.glob(pattern)):
            m = ARM_RE.match(os.path.basename(arm_dir))
            if not m or not os.path.isdir(arm_dir):
                continue
            hh, label, mem_kind, told, look = m.groups()
            if label != LABEL:
                continue
            bank_path = f"{bank_dir}/{hh}_{label}.jsonl"
            if not os.path.exists(bank_path):
                continue
            if bank_path not in bank_cache:
                bank_cache[bank_path] = load(bank_path, 2)
            if bank_path not in info_cache:
                info_cache[bank_path] = bank_owner_info(bank_path)
            h, qs = bank_cache[bank_path]
            sick, owners, q_obj = info_cache[bank_path]
            answers = arm_answers(arm_dir)
            if not answers or not sick:
                continue
            key = f"llm_{mem_kind}_{msg_tag(told == 'told', None)}"
            arm = per_arm.setdefault((pop, key), {"mem_kind": mem_kind, "msg_tag": msg_tag(told == "told", None), "hh": set(), "rows": []})
            arm["hh"].add(hh)
            seen = set()
            for qid, (loc, conf) in answers.items():
                q = qs.get(qid)
                if not q or loc is None:
                    continue
                obj = q_obj.get(qid, q["obj"])
                cold = (q["day"], obj) not in seen
                seen.add((q["day"], obj))
                group = "sick" if owners.get(obj) == sick else "others"
                arm["rows"].append((q["day"], group, cold, int(loc == q["truth"]), float(conf or 0.0), hh))
    # paired owner-split contrasts: per household, (start message - no message) on the sick resident's things and on
    # everyone else's, then mean +- sd across households. The 3-household version of this comparison was published as
    # an interference finding and retracted at 05:10 when all six households made it a wash; nothing here is stated
    # without its spread again.
    def owner_paired(pop, mem, w, group, split):
        base, told = f"llm_{mem}_nomsg", f"llm_{mem}_startmsg"
        A, B = per_arm.get((pop, base)), per_arm.get((pop, told))
        if not (A and B):
            return None
        diffs, base_lv, told_lv = [], [], []
        for h in sorted(set(A["hh"]) & set(B["hh"])):
            vals = []
            for arm in (A, B):
                sel = [r for r in arm["rows"] if r[0] in WINDOWS5[w] and r[1] == group and r[5] == h and (split == "all" or r[2])]
                vals.append((len(sel), 100 * sum(r[3] for r in sel) / len(sel)) if sel else (0, None))
            if vals[0][0] >= 5 and vals[1][0] >= 5:
                diffs.append(vals[1][1] - vals[0][1])
                base_lv.append(vals[0][1])
                told_lv.append(vals[1][1])
        if len(diffs) < 2:
            return None
        m = sum(diffs) / len(diffs)
        sd = (sum((d - m) ** 2 for d in diffs) / (len(diffs) - 1)) ** 0.5
        v = verdict(m, sd, len(diffs), [round(d, 1) for d in diffs])
        # Levels beside the contrast, on EXACTLY the households the contrast is computed from and with each household
        # weighted equally (coordinator, 07:45): pooling over questions instead would let a talkative household move a
        # level one way while the paired contrast moves the other, which is the thing a reader cannot be asked to spot.
        # By construction told - base == mean here, so the two numbers can never disagree.
        v["base"] = round(sum(base_lv) / len(base_lv), 1)
        v["told"] = round(sum(told_lv) / len(told_lv), 1)
        return v

    out = {}
    for (pop, key), arm in per_arm.items():
        windows = {}
        for w, days in WINDOWS5.items():
            ww = {}
            for group in ("sick", "others"):
                for split in ("all", "cold"):
                    sel = [r for r in arm["rows"] if r[0] in days and r[1] == group and (split == "all" or r[2])]
                    n = len(sel)
                    ww[f"{group}_{split}"] = {"n": n, "acc": round(100 * sum(r[3] for r in sel) / n, 1),
                                             "conf": round(100 * sum(r[4] for r in sel) / n, 1)} if n else None
            windows[w] = ww
        paired = None
        if arm["msg_tag"] == "startmsg":
            paired = {w: {f"{g}_{sp}": owner_paired(pop, arm["mem_kind"], w, g, sp)
                          for g in ("sick", "others") for sp in ("all", "cold")} for w in WINDOWS5}
        # Per-DAY cells split by whose things the question was about, so the owner split can be drawn as a line
        # chart (panel H) rather than only read off the five-window table. Same shape as the other arms' cells --
        # {household: {split: [ [n, ok, sum_conf] per day ]}} -- one set per group. Rows are
        # (day, group, cold, correct, conf, hh).
        nd = max((r[0] for r in arm["rows"]), default=-1) + 1
        cells_by_group = {}
        for group in ("sick", "others"):
            g_cells = {}
            for r in arm["rows"]:
                if r[1] != group:
                    continue
                hh_cells = g_cells.setdefault(r[5], {sp: [[0, 0, 0.0] for _ in range(nd)] for sp in ("all", "cold")})
                for sp in (("all", "cold") if r[2] else ("all",)):
                    c = hh_cells[sp][r[0]]
                    c[0] += 1; c[1] += r[3]; c[2] += r[4]
            cells_by_group[group] = g_cells
        out.setdefault(pop, {})[key] = {"paired_vs_nomsg": paired,
                                        "name": MEM_NAME.get(arm["mem_kind"], arm["mem_kind"]) + MSG_LABEL[arm["msg_tag"]],
                                        "mem_kind": arm["mem_kind"], "msg_tag": arm["msg_tag"], "n_hh": len(arm["hh"]),
                                        "households": sorted(arm["hh"]), "windows": windows,
                                        "n_days": nd, "cells_by_group": cells_by_group}
        f = lambda w, g: (f"{windows[w][g]['acc']:.0f}" if windows[w][g] else "–")
        lines.append(f"owner-split {pop}/{key} ({len(arm['hh'])} hh): sick person's things " + " | ".join(f(w, "sick_all") for w in WINDOWS5) +
                     "   others " + " | ".join(f(w, "others_all") for w in WINDOWS5) +
                     "   others COLD " + " | ".join(f(w, "others_cold") for w in WINDOWS5))
    return out


if __name__ == "__main__":
    main()
