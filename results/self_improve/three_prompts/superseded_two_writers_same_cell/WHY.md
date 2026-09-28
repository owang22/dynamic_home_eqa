# Superseded: control_wholesale cells that had TWO processes writing them

My launcher wrapped each cell in `( ... ) &`, so `$!` recorded the SUBSHELL's pid and not
python's. Killing the recorded pid therefore orphaned the python child instead of stopping
it. When I relaunched the wholesale arm at 20:12 after lifting the schema ceiling, the four
pre-patch processes from 20:03 were still alive and still writing - so five of these cells
had two processes appending to the same `looks.jsonl` and `searches.jsonl` and overwriting
the same `notes.json`, one of them under the old 2400-character ceiling.

Nothing from this directory may be used. Two fixes went in:
  * the launcher `exec`s python, so the recorded pid IS the python process;
  * `run_one_arm` takes a lock in the cell directory and REFUSES to start if a live
    process already holds it, so two writers cannot happen again whatever the launcher does.
