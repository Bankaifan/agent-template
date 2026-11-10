# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): design on main, implementation follows.

## Current state (measured 2026-11-10)
- Open PRs: #263 (#206 answer core, risk:security, needs-human, CHANGES_REQUESTED, round:9390f74), #276 (parallel caps, risk:infra, CHANGES_REQUESTED), #278 (#244 agent tools, risk:security, CHANGES_REQUESTED).
- Free agent:dev slots 1, free PR slots 0. Nothing started this run.
- Main CI: status success; agent-review, agent-security-review and status in progress at measurement time, none red.
- #263: the second security review could not read the diff earlier; the unblocker ended without a verdict twice. Not touched again.
- Design 0009 merged. Implementation issues #269-#273 exist (prio:3, not started).
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.
- #154 is Daniel's (risk:security flip of main ruleset).

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Whether the parent issues #171, #191, #125, #190 close once splits land: open.
- Why the unblocker and the second security review fail on #263: open.

## Next 3 steps
1. Get #263, #276, #278 through review so PR slots free up; then #206 follows, then #207 and #208.
2. #206 agent:dev slot is free: start next approved issue once a PR slot opens (#237, #252, #269, #270).
3. Later #112, #148.
