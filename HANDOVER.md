# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design `docs/design/0002-unblocker-role.md`, merged). Implementation issues #102-#106.

## Current state (measured 2026-11-09)
- Open PRs: #126 (for #117, risk:security, review required; validate green, risk run failed on pull_request_target - open).
- #102, #103, #104, #113, #114, #118: merged and closed.
- `agent:dev` open: #117 (PR #126) and #124 (merge train, design study slip posted, output docs/design/0003-merge-train.md).
- #105 (4/5 workflow, risk:security), #106 (5/5 docs): not started, prio:3. #92 stays needs-human and closes with #106.

## Open
- Why the risk workflow failed on #126 (pull_request_target run 42716364169).
- Whether silent orchestrator runs get an unblocker run; settled in #105.
- #105 needs actions:write on the author app token for the agent-fix dispatch.
- #117 needs a second app token scoped to the template repo (Daniel to provision).

## Next 3 steps
1. Review PR #126; remove `agent:dev` from #117 once merged.
2. When the #124 design PR merges, create implementation issues from its split.
3. Later candidates: #125 (design first), #105 (needs Daniel's approval), #119, #120, #112.
