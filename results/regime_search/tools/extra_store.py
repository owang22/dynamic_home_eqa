#!/usr/bin/env python3
"""The one writer of story_extra.json, so that no extractor can drop another's work.

story_extra.json is built by five separate scripts. On 22 Sept `story_extra.py` wrote it from a fresh dict and
silently destroyed the other four extractors' keys; nothing errored, and it was caught only because the rebuilt
page happened to halve in size. A merge that depends on the author remembering to merge is the same trap waiting
for the next person, so writing now goes through here and the shape enforces the rule:

  * an extractor declares the keys it OWNS and passes exactly those;
  * passing a key owned by someone else is refused;
  * a key that exists on disk and is not being rewritten is always carried over;
  * the result is refused if the key set or the file would shrink (the cheap alarm that was missing).

    from extra_store import write_keys
    write_keys("llm_live_extra", {"llm_live": out, "knowno_live": knowno, "owner_split_live": owner_split})
"""
import glob
import json
import os
import shutil
import time

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "story_extra.json")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".story_extra_backups")
KEEP_BACKUPS = 8

# NOTE FOR ANYONE TESTING THIS MODULE: a destructive test runs against a SANDBOX COPY with extra_store.PATH
# redirected, never against the live file. On 22 Sept the first version of the guard test below was pointed at the
# real story_extra.json; its very first case -- the one that was meant to FAIL to be caught -- wrote an empty
# "sweep" and "affected" over the real values, and the next run then reported "not caught" for the wrong reason,
# because nothing non-empty was left to protect. A test that passes by not catching something can do exactly the
# damage it exists to prevent. Hence the automatic backup below: recovery should not depend on whoever is at the
# keyboard having thought to take one.


def _backup(note):
    """Copy the current file aside before it is replaced. Returns the backup path, or None if there was nothing
    to copy. Keeps the most recent KEEP_BACKUPS and deletes the rest."""
    if not os.path.exists(PATH):
        return None
    os.makedirs(BACKUP_DIR, exist_ok=True)
    dest = os.path.join(BACKUP_DIR, f"story_extra.{time.strftime('%Y%m%d-%H%M%S')}.{note}.json")
    shutil.copy2(PATH, dest)
    old = sorted(glob.glob(os.path.join(BACKUP_DIR, "story_extra.*.json")))[:-KEEP_BACKUPS]
    for f in old:
        try:
            os.remove(f)
        except OSError:
            pass
    return dest

# who is allowed to write what. A key missing from here is unowned and may be written by anyone (but still never
# dropped); a key listed here may only be written by its owner.
OWNERS = {
    "story_extra":            ("sweep", "affected", "planning", "planning_matched"),
    "llm_live_extra":         ("llm_live", "knowno_live", "owner_split_live", "classical_askgate"),
    "gap_extra":              ("gap",),
    "shared_state_extra":     ("shared_state",),
    "affected_windows_extra": ("affected_windows",),
    "deferral_extra":         ("deferral_live",),
    "samples_extra":          ("samples_live",),
}


class ExtraStoreError(RuntimeError):
    pass


def write_keys(owner, new, allow_shrink=False):
    """Merge `new` into story_extra.json on behalf of `owner`. Returns a one-line report to print."""
    owned = OWNERS.get(owner)
    if owned is None:
        raise ExtraStoreError(f"unknown extractor {owner!r}; add it to OWNERS in tools/extra_store.py")
    stolen = [k for k in new if any(k in ks for o, ks in OWNERS.items() if o != owner)]
    if stolen:
        raise ExtraStoreError(f"{owner} tried to write keys it does not own: {stolen}")

    prev, prev_size = {}, 0
    if os.path.exists(PATH):
        prev_size = os.path.getsize(PATH)
        try:
            prev = json.load(open(PATH))
        except ValueError as e:                      # a half-written file is a reason to stop, not to overwrite
            raise ExtraStoreError(f"{PATH} is not valid JSON ({e}); refusing to write over it") from e

    # The merge means a key can no longer VANISH -- but an extractor run against missing inputs will happily write
    # an empty value over a full one, which loses the content just as completely and shrinks the file too little
    # for a size check to notice. That is the failure this guard is really for.
    def empty(v):
        return v is None or (isinstance(v, (dict, list, str)) and len(v) == 0)
    emptied = [k for k, v in new.items() if empty(v) and k in prev and not empty(prev[k])]
    if emptied and not allow_shrink:
        raise ExtraStoreError(
            f"{owner} would overwrite non-empty {emptied} with empty values. That usually means it ran against "
            f"missing inputs. Fix the inputs, or pass allow_shrink=True if the emptying is genuinely intended.")

    missing = [k for k in owned if k not in new and k in prev]
    merged = dict(prev)
    merged.update(new)
    dropped = sorted(set(prev) - set(merged))
    if dropped:                                      # cannot happen via update(), but assert the invariant anyway
        raise ExtraStoreError(f"{owner} would drop keys: {dropped}")

    body = json.dumps(merged, separators=(",", ":"))
    if not allow_shrink and prev and len(body) < prev_size * 0.9:
        raise ExtraStoreError(
            f"{owner} would shrink story_extra.json from {prev_size//1024} KB to {len(body)//1024} KB. "
            f"That usually means an extractor ran against missing inputs. Re-run it with its data in place, or "
            f"pass allow_shrink=True if the shrink is genuinely intended.")
    backup = _backup(owner)
    with open(PATH, "w") as fh:
        fh.write(body)
    note = ""
    if missing:
        note = f" | NOT rewritten this run (kept from disk): {missing}"
    return (f"{owner}: wrote {sorted(new)}{note} | kept from other extractors: "
            f"{sorted(k for k in merged if k not in new)} | {len(body)//1024} KB "
            f"({len(body)-prev_size:+d} bytes)"
            + (f" | previous copy: {os.path.relpath(backup, os.path.dirname(BACKUP_DIR))}" if backup else ""))
