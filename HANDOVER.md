# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-10)
- Merged: #166, #167, #168, #162, #161, #106, #141, #156, #172.
- Closed unmerged: #177 (for #171) and #181 (for #153).
- Open PRs: none. Free PR slots 3, free agent:dev slots 0 (script count).
- Main: status green; orchestrator run in progress.
- `agent:dev` still on issues #171 and #153, but their PRs are closed: needs a decision (restart:1 already set on both).
- #105, #99, #100, #106 are done on main but issues may still be open; closing is denied to the orchestrator, so Daniel closes them.
- #92 stays needs-human. Design 0004: #148 (docs) not started. Design 0003: #150, #152 not started; #154 is Daniel's.

## Open
- Why #177 and #181 were closed (review rejection or owner): open.
- Whether #171 and #153 get restarted or their slots are freed: open.
- Whether status run on main still raises overdue issues after #166: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. Resolve the agent:dev slots held by #171 and #153 (closed PRs).
2. Then start #150, then #152; #182 and #179 (prio:1).
3. Later #125 (design first), #119, #120, #112, #148.
