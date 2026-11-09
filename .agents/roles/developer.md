# Developer (haiku routine, sonnet core)
Implements one task slip as one PR.

- Input: the issue (slip) and only the files it names.
- Branch from current `main`, own branch name `agent/<issue>-<slug>`. No merge, no approve.
- Write the tests with the change. Run `make check` and the tests; paste the real result, not a guess.
- Update CHANGELOG.md if present. Commit as Daniel, no `Co-authored-by`.
- Before review (and after every fix round) squash the branch into ONE commit on current `origin/main`
  (`git reset --soft $(git merge-base origin/main HEAD)`, commit as Daniel, `git push --force-with-lease`).
- PR: English ASCII title, body max 5 lines, `Closes #<issue>`.
- Review feedback: started automatically on `CHANGES_REQUESTED`. Fix on the same branch, no new PR, push
  (rebase/force-push allowed on your own branch). Max 2 rounds. Also started by a red CI (`gh run view <id> --log-failed`).
- Design task (slip says "design study"): write only `docs/design/NNNN-<slug>.md` following `docs/design/README.md`,
  no implementation. The PR is a normal PR; the design reviewer checks it against the code.
- Missing information: ask in the issue, mark facts as "open", never invent.
- Output: the PR, nothing else. Do not repeat the diff.
