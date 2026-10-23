# Coordination between agents

Three Claude Code agents work in this repo for Oliver. Each owns some folders, edits only those, and talks to the
others through messages committed under `coordination/`.

## Who owns what

| agent (inbox name) | machine | owns |
|---|---|---|
| `cheetah` | cheetah, GPU server (172.17.31.231); GPU shared with user gaofeng | `go2/` (lab agent, picture memory, localization studies, evidence memory, lab routine sim, console clients), `3d_rendering/`, `robot_brain/`, `src/`, `prior_work/`, top-level files |
| `z690` | control PC, `nesl-Z690-CLASSIFIED` (172.17.40.64) | `navigation/`, `planning/`: console, agent API, map and localization, markers, vision checks for navigation, planner, gait |
| `h100` | the lab's H100 machine | `simulation/` |

- Edit only your own folders. To change someone else's, send them a message with the change you want (a patch or
  the exact lines is fine) and let them make it.
- `coordination/` is shared: each agent adds files there, never edits or deletes another agent's files.
- `.gitignore` is shared: anyone may append rules for their own folders, in a block headed with the folder name.
- Oliver can change anything.

## Messages

One file per message:

```
coordination/inbox/<to>/<YYYY-MM-DD_HHMM>_<from>_<slug>.md
```

- `<to>` is `cheetah`, `z690`, `h100`, or `all`. Time is Pacific (`TZ=America/Los_Angeles date +%Y-%m-%d_%H%M`).
- `<slug>` is a few lowercase words joined by `-`, e.g. `2026-10-23_1610_cheetah_welcome.md`.
- One file per message means two agents writing at once never conflict. Never edit a message after pushing it;
  correct it with a new one.
- First lines of the file:

  ```
  # <subject>
  From: <agent> · To: <agent> · <YYYY-MM-DD HH:MM> PT
  Re: <file name of the message you answer, if any>
  ```

  Then the message: short, specific, what you tested and what you did not, paths and commands in code format.
- To reply, write a new file in the sender's inbox with `Re:` set. Nobody moves or deletes inbox files.
- To see what's new: `git pull`, then `git log --since=<last check> --name-only -- coordination/inbox/<you>/ coordination/inbox/all/`.
- Agents don't run all the time; Oliver starts them. Don't wait on an answer: say what you'll do if none comes.

## Git rules

- `git pull --rebase` before you write, and again before you push. **Never force-push.** If a push is
  rejected, pull, rebase, and push again; if that conflicts outside your own folders, stop and send a message.
- Commit only your own folders plus your new message files. Stage files by name; check `git status` first.
- **Never commit secrets** (passwords, keys, tokens, Wi-Fi keys, SSH keys) or robot data (`go2/data/`, maps,
  bags, camera frames, recordings). Never commit large or regenerable files (caches, `.npy`/`.npz`, model weights,
  server logs, anything over about 5 MB); add `.gitignore` rules for them instead.
- Commit messages: a short first line naming the folder (`navigation: ...`), a few lines of what and why, and end
  with the trailer lines your session gives you, e.g.

  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_<your session id>
  ```

## The message board

The Claude Docs "Go2 Robot Dog Lab Guide" (Agent chat tab) stays in use for anything Oliver follows live: lab
protocols, requests during tests, robot status. Use git messages for code, results, and work between agents.
This holds until Oliver says otherwise. The board up to 2026-10-23 is archived in
`coordination/board_archive_2026-10-23.md`.
