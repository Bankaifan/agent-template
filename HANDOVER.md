# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) rebuilt on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-09)
- Open PRs: none. Merged today: #157 (0004 1a read confinement), #158 (0004 2 fetch + outgoing filter), #126 gone from the open list.
- `agent:dev` open: #145 (0004 1b, model:sonnet) and #147 (0004 3 unblocker workflow, slip rewritten, model:sonnet).
- #117 has no `agent:dev` and no `needs-human` label now; its PR is not open. Status open.
- Issues from design 0004: #148 (4 docs) not started.
- Issues from design 0003: #150 (overlap guard), #151 (train core), #152 (train workflow), #153 (re-approval), #154 (strict flip, Daniel).
- #106 (docs 5/5) not started; #92 stays needs-human.

## Open
- Why #117's PR #126 is no longer open (merged or closed): not checked.
- #117 needs a second app token scoped to the template repo (Daniel to provision).
- Overdue scheduled-run issues #98, #99, #100 (prio:1): not triaged; `gh run list --workflow scout` returned nothing.
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. When #145 or #147 merges: remove `agent:dev`; start #153 and #151 (disjoint), then #150, #152; #154 last, Daniel.
2. Triage #98-#100 and #156 (orchestrator runs ending silently).
3. Later #125 (design first), #119, #120, #112.
