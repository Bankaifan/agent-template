# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Three threads: #19 template sync (design merged in `docs/design/0001-template-sync.md`), #22 (silent-run guards),
#27 model-free status run.

## Current state
- #27: PR #40 on branch `agent/27-status-run`. `.github/workflows/status.yml` + `tools/status.py` + `tests/test_status.py`.
  Cron ticks at :07/:37; the gate step honours repo variable `STATUS_INTERVAL` (default 30 min public, 60 min private).
  Also runs on `workflow_dispatch` and after agent-dev/fix/review. Maintains the issue "Agent status" (pinned),
  re-triggers orphans once (label `status:retriggered`), then needs-human + review request for Daniel, approves held
  runs of author-app PRs, and starts a fix round for PRs with merge conflicts.
- Conflict rounds: the status run bumps `review:N` and dispatches `agent-fix.yml -f pr=N`. This needed a small
  `workflow_dispatch` input in `agent-fix.yml` (outside the slip's file list, inside Daniel's approval for workflows).
- `make check` and tests green locally (119 passed).
- #19 and #22: see their PRs/issues; unchanged by this work.

## Open
- Not verified on GitHub: author app has `actions: write` (needed for approving runs and dispatching agent-fix) and
  may pin issues. Failures are printed and do not stop the run.
- Matching running agent-dev jobs to issues relies on the run title (issue title or `#N`); open.
- #19: owner decisions still open.

## Next 3 steps
1. Review and merge PR #40; run `status` once with workflow_dispatch and check the issue "Agent status".
2. Confirm the app permissions above.
3. Daniel decides the #19 owner decisions.
