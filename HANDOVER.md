# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273 all merged (commit e59821c documents NIGHTLY_HEAVY_TESTS).

## Current state (measured 2026-11-10, run 30)
- Open PRs: #320 (pin orchestrator silent-run guard, for #313, labels review:1). No agent/rule-keeper PRs open.
- Free agent:dev slots 2, free PR slots 4 at start of this run.
- Main CI: no red run in the last 10 (runs skipped, cancelled, pending or in progress).
- #309 (risk.yml gate failure): intentional owner gate on PR #307, Daniel answered "Ja", answer receiver owns it. Not touched.
- #112 (run-name): not started, overlap.py exit 1: .github/workflows/orchestrator.yml overlaps slip #313 (PR #320). Retry after #320 merges.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).

## Next 3 steps
1. Get PR #320 through review and merge.
2. Start #112 once #320 has merged (overlap check first).
3. Close-or-fix decision for #313 after #320.
