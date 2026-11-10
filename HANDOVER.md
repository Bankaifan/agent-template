# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): design on main, implementation follows.

## Current state (measured 2026-11-10)
- Open PRs: #263 (#206 answer core, risk:security, needs-human, CHANGES_REQUESTED). The second security review at head 994fdc0 could not read the diff (tool denial, no finding); the first one approved. Daniel waits for #267. The unblocker ended without a verdict twice. #132 wiring merged (352cda8).
- Main CI: status and validate runs green or in progress at measurement time, none red.
- Design 0009 (test scoping, #135) merged on main (0cf9e76). Implementation issues #269-#273 exist (prio:3, not started).
- Free agent:dev slots 0, free PR slots 1. Nothing started this run.
- #134 friction reports: PR #259 merged; wiring into tools/weekly_summary.py is a follow-up (#254 owns that file).
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.
- #148 not started. #154 is Daniel's. #244, #266, #267 are not approved.
- #252, #253, #254 are not on the trusted list as approved (open: why).

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Whether the parent issues #171, #191, #125, #190 close once splits land: open.
- Why #237-#241 and #252-#254 are not listed as approved: open.
- Why the unblocker and the second security review fail on #263: open (#267 covers the review).

## Next 3 steps
1. Land #267 (needs approval), then re-run the security review on #263; then #207 and #208.
2. #135 implementation issues #269-#273 from design 0009 (start #269 and #270 when slots free up), then #252 once approved.
3. Later #112, #148.
