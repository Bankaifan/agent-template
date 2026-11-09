# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design `docs/design/0002-unblocker-role.md`, merged). Implementation issues #102-#106.

## Current state (measured 2026-11-09)
- Open PRs: none. Main CI: last status run green.
- #102, #103 (PR #111) and #104 (PR #116, role file): merged and closed.
- #105 (4/5 workflow, risk:security), #106 (5/5 docs): not started, prio:3, in that order. #92 closes with #106.
- `agent:dev` open: #113 (post_verdict dismisses own security request-changes, prio:1) and
  #114 (read-back for remaining Daniel-facing comments, prio:2). Both have `model:sonnet` and a slip.
- #74: no longer labeled `agent:dev`; remaining read-back work is tracked in #114.

## Open
- Whether silent orchestrator runs get an unblocker run; settled in #105.
- The workflow PR (#105) needs actions:write on the author app token for the agent-fix dispatch (note in PR #111).

## Next 3 steps
1. Review the PRs for #113 and #114; remove `agent:dev` once they merge.
2. Then start #105 when a slot frees up (needs Daniel's approval, risk:security).
3. Later candidates: #117, #120, #112 (approved), #118 and #119 (ideas, not approved).
