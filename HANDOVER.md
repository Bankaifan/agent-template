# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): design on main, implementation issues #269-#273 exist.

## Current state (measured 2026-11-10)
- Open PRs: #283 (answer receiver workflow, #207) and #284 (orchestrator gate, #238). Both risk:security, review approved, review:1.
- Free agent:dev slots 2, free PR slots 3 at start of this run.
- Started this run: #252 (failure watch 2/4) and #269 (test scoping 1/5). Slip comments written, overlap check passed, model:sonnet and agent:dev set.
- Main CI: status runs queued or success, none red at measurement time.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.
- #154 is Daniel's (risk:security flip of main ruleset): not started by the orchestrator.
- #208 waits for #207 (PR #283) to merge. #239-#241 follow #238.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Whether the parent issues #171, #191, #125, #190 close once splits land: open.
- #282 (owner issue, not approved): not started.

## Next 3 steps
1. Get #283, #284 and the #252/#269 PRs through review; then #208 and #239 follow.
2. Next approved issues: #253, #270, #148 (check overlap first).
3. Later #112, #134.
