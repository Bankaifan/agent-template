# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-10)
- Merged: #166, #167, #168, #162, #161, #106, #141, #156, #172 (waiting-for-owner PRs free slots; agent:dev removed from #172, issue closed).
- Open PRs: #177 (risk:tightening for #171), review CHANGES_REQUESTED, labels review:1, review:2, risk:security.
- Main: validate, risk, status green on the last runs; orchestrator and status runs in progress.
- `agent:dev` open: #171 (PR #177) and #153 (merge train 4, re-approval; started this run with model:sonnet).
- #105, #99, #100, #106 are done on main but issues may still be open; closing is denied to the orchestrator, so Daniel closes them.
- #92 stays needs-human. Design 0004: #148 (docs) not started. Design 0003: #150, #152 not started; #154 is Daniel's.

## Open
- Whether status run on main still raises overdue issues after #166: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Whether #153 and #177 conflict in tests or workflows: open.

## Next 3 steps
1. When #177 merges: remove agent:dev from #171; start #150, then #152.
2. Then #125 (design first), #124 remainder.
3. Later #119, #120, #112, #148.
