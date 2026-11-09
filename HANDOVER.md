# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. Written by the orchestrator at the end of each session. -->

## Goal
Issue #11: secure agent inputs and make triggers reliable.

## Current state
PR for #11 is open (branch `agent/11-secure-inputs-reliable-triggers`). Not verified end to end; only `make check` and pytest ran locally.
See `docs/decisions/0004-secure-inputs-reliable-triggers.md`.

## Open decisions
- Author app permissions: Actions and Workflows read/write must be granted (untested).
- Do `workflow_run` events fire for runs created by the author app, and does the orchestrator see them?

## Next 3 steps
1. Daniel sets repo variables `AUTHOR_BOT` and `APPROVER_BOT`, grants the author app the new permissions, runs `setup`.
2. Merge the PR.
3. First real run: agent PR with green CI, one with red CI, one merge of a HANDOVER.md-only PR.

## Known traps
- The ruleset file is not applied automatically; it must be re-imported.
