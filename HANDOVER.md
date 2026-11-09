# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Two threads in flight: #19 template sync (design study merged in `docs/design/0001-template-sync.md`) and #22
(no silent agent runs, labels never missing, client IDs, login normalization, job-level concurrency).

## Current state
- #19: design merged; two owner decisions open (author app on the template repo; widened trust for `Template sync`
  issues). After Daniel's decision the orchestrator creates the four implementation issues with a `Design:` line.
- #22: PR on branch `agent/22-silent-runs-labels-logins`. `tools/agent_guard.py` (login normalization, label
  create-then-add, silent dev/fix/review detection -> comment, `needs-human`, Daniel). agent-dev/fix/review end with an
  `if: always()` step; concurrency only on dev/fix jobs; label adds via guard copy from main; all app tokens via `client-id` (`AUTHOR_CLIENT_ID` / `APPROVER_CLIENT_ID`,
  already set by Daniel).

## Open decisions
- #19: whether the author app can read a private template repo is not verified; sync not run end to end.
- #22: developer may now run read-only `gh release view/list` (release notes for major updates); nothing broader.

## Next 3 steps
1. Daniel decides the two #19 owner decisions.
2. Merge #22 after review; watch the first run with an escalation step.
3. Orchestrator creates the #19 implementation issues.
