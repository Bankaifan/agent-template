# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.

## Current state (measured 2026-11-10)
- Open PRs: #263 (#206 answer core, risk:security, CHANGES_REQUESTED at 994fdc0, needs-human; unblocker owns it, its last run ended without a verdict). #132 wiring merged (352cda8).
- Security review of #263 failed twice as a process failure (diff unreadable, tool calls denied), not as a finding.
- Main CI: status runs green or cancelled by concurrency; one in progress at measurement time.
- Design 0009 (test scoping, #135) merged on main (0cf9e76). Implementation issues #269-#273 created this run (prio:3, not started, no free slot).
- Free agent:dev slots 0 this run, free PR slots 2. Nothing started.
- #134 friction reports: PR #259 merged; wiring into tools/weekly_summary.py is a follow-up (#254 owns that file).
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.
- #148 not started. #154 is Daniel's. #244 is not approved.
- #252, #253, #254 are not on the trusted list as approved (open: why).

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Whether the parent issues #171, #191, #125, #190 close once splits land: open.
- Why #237-#241 and #252-#254 are not listed as approved: open.

## Next 3 steps
1. Merge #263 (#206); then #207 and #208.
2. Start #269 and #270 (disjoint) when slots free up, then #252 once it is on the trusted list.
3. Later #112, #148.
