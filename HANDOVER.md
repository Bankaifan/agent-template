# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).

## Current state (measured 2026-11-10)
- Merged: #161 (scout routing, #117), #162 (unblocker workflow, #147), #163 (handover).
- Open PRs: #164 (#139 guard marker, risk:security, CHANGES_REQUESTED twice by security review; agent-fix running).
- `agent:dev` open: #139 (PR #164), #98 (slip written: overdue scheduled runs, root cause for #98-#100).
- #105 is now only the remainder of #162: setup.yml (unblock:1, UNBLOCKER) and orchestrator step 2 skip (slip item 3b). Not started.
- #106 (docs) waits for #105. #92 stays needs-human.
- Issues from design 0004: #148 (docs) not started. Design 0003: #150-#154 not started (#154 is Daniel's).

## Open
- Why #98, #99, #100 (overdue scheduled runs) were raised: cause not found yet (#98 slip covers it).
- Security review of #164: class 2 unblocker issues must not become trusted; marker enforced only in unblock.check_outgoing; guard_mark.py not in CODEOWNERS (Daniel).
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. When #98 merges: remove `agent:dev`, close #99 and #100 if the cause is shared; then start #105 (disjoint files from #164).
2. When #164 merges: remove `agent:dev` from #139; start #153 and #151 (disjoint), then #150, #152; triage #156.
3. Later #125 (design first), #119, #120, #112.
