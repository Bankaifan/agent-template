# 0019 NIGHT-RUN: a night without a person

Asked for by the owner on 2026-11-23 after a night in a downstream project where a person stepped in at every
point below. Name of the work: `NIGHT-RUN`.

## Rules
1. **A silent run is repeated once.** A review run that leaves no review, or a fix run that leaves the head and the
   PR body unchanged, marks the head with the label `silent:<sha7>` and starts once more (review: validate is started
   again; fix: `agent-fix` is dispatched with `why=retry`). Only a second silent run on the same head reaches the
   guard (`agent_guard.py silent`: restart, stuck issue or park, unchanged). The token that starts the run again is
   the author app with `actions` only and is created after the model step.
2. **Single commands, no wider allow list.** The reviewer's Bash list stays `gh pr view`, `gh pr review`,
   `gh issue view`. `cat`, `ls` or `cd` are not added: Bash reads are not covered by the Read deny list, so they
   would open the runner's files to a judging model. The prompt and the role now say so, as the security review did.
3. **Branches are rebased, never merged.** The train rebases the next PR itself (`tools/branch_repair.py`): straight
   line on main, merges of main dropped, every subject `V<VERSION>-<NAME>: ` with main's VERSION, one
   `--force-with-lease` push. The update-branch API (rebase) is the fallback. An open agent PR whose subjects fail the
   form check is repaired the same way without a model. A `Merge branch 'main' into ...` commit is no form error.
4. **A release does not turn open PRs red.** The form check accepts a subject of any version; the version in the
   subjects follows at the next rebase by rule 3.
5. **Supersede needs the same work.** A newer agent PR closes an older one only if its body says `Supersedes #<old>`,
   or both work on one issue and the newer one changes every file of the older one (changelog fragments aside).
6. **The train closes issues.** The open issue of a merged agent PR is closed (`tools/landed.py`), unless the PR
   says `Refs #N` for it or the issue was reopened.
7. **Measured tolerances are the agents' decision** (`.agents/roles/balancer.md`): new range = lowest run minus 1
   to highest run plus 1; far outside the plan (factor 2) the config value changes instead.

## Not changed
`tools/agent_guard.py` and the other CODEOWNERS paths. The serial train with batches (decision 0018) already lands
PRs without a person; rule 3 and rule 6 remove the two manual steps that were left.
