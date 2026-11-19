# Changelog fragments

A PR that changes a managed path (`.agents/managed.json`) adds `changelog.d/<issue>.md` and does not touch `VERSION` or `CHANGELOG.md`.

- One line per change, written for the owner and the users in the project language (repo variable `OWNER_LANG`,
  default German): what is different for them, one short plain sentence, no file names, no agent internals.
- A change they cannot see is `internal: <a few words>`: it goes into `CHANGELOG.md` but not into the release PR.
- Optional `step: x` line: the release becomes a major step (breaking for users or for downstream syncs).
- After the merge the merge train (`tools/train.py`, one writer) folds all fragments on main into ONE next version
  (`tools/release_fragments.py`) on the branch `release/next`. Its PR `Release <version>` is the only thing the owner
  approves; `VERSION` changes only when he merges it, by exactly one step.
