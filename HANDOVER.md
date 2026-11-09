# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) rebuilt on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-09)
- Open PRs: #126 (for #117, risk:security, APPROVED, review:2). Designs 0003 (#142) and 0004 (#144) merged.
- `agent:dev` open: #117 (needs-human, PR #126), #149 (0004 1a read confinement, prio:1), #146 (0004 2 fetch and filter, prio:1). #149 and #146 just started, model:sonnet.
- Issues from design 0004: #149 (1a), #145 (1b, after 1a), #146 (2), #147 (3 unblocker workflow, needs 1a and 2), #148 (4 docs).
- Issues from design 0003: #150 (overlap guard), #151 (train core), #152 (train workflow), #153 (re-approval), #154 (strict flip, needs-human).
- #105 and #124 lost `agent:dev` (design PRs merged). #106 (docs 5/5) not started; #92 stays needs-human.

## Open
- Why the risk workflow failed on #126 (pull_request_target run 42716364169).
- Whether Glob/Grep honour deny rules and whether the token is readable via the process environment: measured in #149.
- #117 needs a second app token scoped to the template repo (Daniel to provision).
- Overdue scheduled-run issues #98, #99, #100 (prio:1): not triaged.
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. Merge of #126: remove `agent:dev` from #117. Start #145 after #149 merges; #147 needs #149 and #146.
2. Next from design 0003: #153 and #151 (disjoint), then #150, #152; #154 last, Daniel.
3. Triage #98-#100; later #125 (design first), #119, #120, #112.
