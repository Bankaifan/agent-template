# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-10)
- Merged: #166, #167, #168, #162, #161, #106, #141, #156, #172.
- Closed unmerged: #177 (for #171) and #181 (for #153).
- Open PRs: #184 (for #171, risk:security, review:1 and review:2 set; `risk` run failed, `validate` in progress).
- Started this run: #179 (slip posted, model:sonnet, agent:dev). Free agent:dev slots were 1, PR slots 2 (script count).
- `agent:dev` still on #153 although #181 is closed: open decision.
- #105, #99, #100, #106 are done on main but issues may still be open; Daniel closes them.
- #92 stays needs-human. Design 0004: #148 not started. Design 0003: #150, #152 not started; #154 is Daniel's.

## Open
- Why the `risk` run on #184 failed: open.
- Whether #153 is restarted or its slot freed: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. Watch #184 (risk check) and #179.
2. Then start #182 (touches gates; wait for #184 to merge), #150, #152.
3. Later #125 (design first), #119, #120, #112, #148.
