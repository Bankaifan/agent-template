# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-10)
- Merged: #166 (overdue grace test, #98), #167 (guard marker, #139), #168 (train core, #151), #162 (unblocker workflow), #161 (scout routing).
- Open PRs: none.
- `agent:dev` open: #106 (unblocker docs, slip written, just started).
- #105 is done on main (b932f68, 4724e4c); agent:dev removed. Closing issues was denied to the orchestrator, so #105, #99, #100 are still open and need closing by Daniel (#99/#100 share the #98 cause, fixed in #166).
- #92 stays needs-human. Design 0004: #148 (docs) not started. Design 0003: #150, #152, #153 not started; #154 is Daniel's.

## Open
- #156 (orchestrator runs end silently): likely denied Bash calls (pipes, gh workflow list, issue close need approval); cause not confirmed.
- Whether status run on main still raises overdue issues after #166: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. When #106 merges: remove `agent:dev` from #106; start #153 and #150 (disjoint), then #152.
2. Triage #156 (allow-list gap vs. real bug); then #141, #125 (design first).
3. Later #119, #120, #112, #148.
