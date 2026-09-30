# The chain watcher was stopped, 2026-09-29

`chain_watch.sh` had been running for 7 days 23 hours: a `while true` loop calling
`chain_watch.py` every 300 seconds and appending a line to `chain_progress.log`. Both that log and
`chain_watch_state.json` are tracked, so every sample left the working tree dirty and the noise sat
on top of every `git status` in this repository.

**Nothing was lost by stopping it.** The last 10 minutes of its own output, repeated for days:

    23:39 watch: 10 arms running, 98 finished, 0 paused, 0 abandoned,
          aggregate 0 calls/min over last 10 min (10 arms with history, 0 moving)

"10 arms running" is read off the directories, not off the process table - an arm counts as running
while it has no finished marker. There were no arm processes alive, and there had been none since
the vLLM server was killed, so the aggregate had been 0 calls/min with 0 arms moving for the whole
of that window. The watcher was sampling ten directories that could not change.

The ten stranded arms are listed in `chain_watch_state.json`, each with a call count that has not
moved. Nothing here is deleted: to pick the work back up, start the server, then the arms, then
`nohup ./chain_watch.sh &` from this directory.

This work is superseded in any case - see the note on the UQ strand in the session memory. It is
kept so its measurements reproduce, not because it is expected to finish.
