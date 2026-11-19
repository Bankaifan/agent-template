# 0018 BATCH-TRAIN: approved PRs land together

Decided by Daniel on 2026-11-19. Name of the work: `BATCH-TRAIN`.

## Problem
`main` requires an up-to-date branch, so the train (`tools/train.py`) lands one PR at a time: every merge sends the
next approved PR through rebase, CI and re-approval again. Several developers run in parallel, the merge is serial.

## Rule
When two or more approved agent PRs are ready, the train lands them as ONE pull request.

1. **Members.** Open same-repo `agent/<N>-...` PRs that are approved by the approver app at their current head, green,
   not `parked`, without a `risk:*` label, not waiting for the owner, and whose changed files are pairwise disjoint
   (oldest first, at most 8). Fewer than two: the serial path as before.
2. **Build.** No model. The train cherry-picks every member (merge base to head) onto current `main` in a scratch
   clone, drops a member whose pick conflicts or whose files changed on `main` since it branched, and force-pushes the result to the one branch `agent/batch`. The PR is
   titled `Batch: #a, #b`; its body has the line `Batch: #a@<sha7> #b@<sha7>` and the closing keywords of its members.
3. **Approval.** Nothing new is trusted. `tools/reapprove.py` (approver app, after green CI, as for every agent PR)
   approves the batch without a model only if every member is still open and approved at the recorded head, and every
   file of the batch diff belongs to exactly one member with the same blob line and patch id as in that member's own diff,
   and every member's own `risk` check and `security-review` status are green. No `docs/design/` file, no merge commit.
   The batch diff must be risk `none` and touch no CODEOWNERS path. Anything else refuses; a refused batch is not
   reviewed by a model, the train closes it and the members take the serial path.
4. **Landing.** The batch merges like any approved agent PR (auto-merge, rebase). The next train run closes the
   members with one line `Merged with #<batch>.`; their issues close through the batch's closing keywords.
5. **Failure.** A batch that is red, conflicting, refused or out of date with its members is closed (out of date:
   rebuilt). The same member set is never batched twice in a row: after a failed batch those PRs go serially.
6. **Nobody fixes a batch.** No fix round, no restart, no park, no supersede for `agent/batch`: it is a script product.

Switch: repo variable `TRAIN_BATCH` (default `on`, `off` keeps the serial train).
