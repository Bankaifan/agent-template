# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Issue #18: review requests for `needs-human`, design study before big work, better dependabot classification.

## Current state
PR on branch `agent/18-review-requests-design-study`. ADR: `docs/decisions/0006-*.md`.
- `agent-fix`, `agent-review`, `dependabot-automerge` add `--add-reviewer Bankaifan` next to `needs-human`.
- New role `.agents/roles/design-reviewer.md` (picked by `agent-review` when only `docs/design/` changed); template `docs/design/README.md`.
- `tools/trusted_issues.py` trusts `Design:`-line issues written by `AUTHOR_BOT` (file must exist on main); the orchestrator gets `AUTHOR_BOT`.
- `tools/dependabot_update_type.py` takes fetch-metadata JSON (highest type wins), parses range titles.
- Tests: `tests/test_dependabot_update_type.py`, `tests/test_trusted_issues.py`.

## Open decisions
- Whether `dependabot/fetch-metadata` (v3.1.0, pinned) works from a `workflow_run` event is not verified; the step is `continue-on-error` and the title is the fallback (open).
- The design flow was not run end to end (open).
- `agent-review.yml` was touched too (not in the slip's file list) because it adds `needs-human` at the round limit.

## Next 3 steps
1. Daniel reviews and merges once CI is green.
2. Watch the first dependabot major/grouped PR: the log shows `PR #n: <kind>`.
3. Try the design flow on the next big issue.
