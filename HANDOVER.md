# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) rebuilt on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-10)
- Open PRs: #162 (#147 unblocker workflow, checks queued), #161 (#117 scout routing, approved, needs-human, waiting for Daniel).
- `agent:dev` open: #147 and #139 (guard-created issues trusted, slip written, model:sonnet).
- #117 is on hold per Daniel's comment (wait for #105 design study) although PR #161 exists; Daniel decides.
- Issues from design 0004: #148 (4 docs) not started.
- Issues from design 0003: #150, #151, #152, #153, #154 (Daniel); none started.
- #105 and #106 wait for #162 to merge; #92 stays needs-human.

## Open
- #98, #99, #100 (overdue scheduled runs, prio:1): `gh run list --workflow scout` returns nothing; cause not found. Should be trusted by #139.
- #117 needs a second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. When #162 merges: remove `agent:dev` from #147; start #153 and #151 (disjoint), then #150, #152.
2. When #139 merges: triage #98-#100 and #156 (orchestrator runs ending silently).
3. Later #125 (design first), #119, #120, #112.
