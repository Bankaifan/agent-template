# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-10)
- Merged: #166 (overdue grace test, #98), #167 (guard marker, #139), #168 (train core, #151), #162 (unblocker workflow), #161 (scout routing), #106 (unblocker docs, decision 0010).
- Open PRs: none. Main: last runs green (validate, risk, status).
- `agent:dev` open: #141 (rule keeper item 5, haiku), #156 (silent orchestrator runs, model:sonnet). Slips written this run.
- #105, #99, #100, #106 are done on main but issues may still be open; closing was denied to the orchestrator, so Daniel closes them (#99/#100 share the #98 cause, fixed in #166).
- #92 stays needs-human. Design 0004: #148 (docs) not started. Design 0003: #150, #152, #153 not started; #154 is Daniel's.

## Open
- #156 cause not confirmed (likely denied Bash calls: pipes, gh workflow list, issue close).
- Whether status run on main still raises overdue issues after #166: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. When #141/#156 merge: remove agent:dev; start #153 and #150 (disjoint), then #152.
2. Then #125 (design first), #124 remainder.
3. Later #119, #120, #112, #148.
