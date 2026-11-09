# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design `docs/design/0002-unblocker-role.md`, merged). Implementation issues #102-#106.

## Current state (measured 2026-11-09)
- Open PRs: none. Main CI: last validate run on main green.
- #102, #103, #104, #113, #114: merged and closed.
- `agent:dev` open: #117 (Scout forwards template ideas, prio:2) and #118 (closing-keyword check fails closed, prio:2). Both have `model:sonnet` and a slip; files are disjoint.
- #105 (4/5 workflow, risk:security), #106 (5/5 docs): not started, prio:3, in that order. #92 stays needs-human and closes with #106.

## Open
- Whether silent orchestrator runs get an unblocker run; settled in #105.
- The workflow PR (#105) needs actions:write on the author app token for the agent-fix dispatch (note in PR #111).
- #117 needs a second app token scoped to the template repo (Daniel to provision).

## Next 3 steps
1. Review the PRs for #117 and #118; remove `agent:dev` once they merge.
2. Then start #105 when a slot frees up (needs Daniel's approval, risk:security).
3. Later candidates: #124, #125, #119, #120 (approved), #112 (approved, prio 4).
