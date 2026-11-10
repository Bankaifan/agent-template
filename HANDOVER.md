# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273; #269 script merged.

## Current state (measured 2026-11-10)
- #290 (prefilter per event, #239) merged: commit 2c296ae on main. Open PR list not re-measured (gh pr list denied in this run).
- Open PRs: #292 (failure watch 3/4, #253, review:1), #294 (empty changes verdict, #292 issue). Free agent:dev slots 3, free PR slots 3 at start of this run.
- Started this run: #241 (orchestrator events 5/5, docs). Slip written, overlap check passed, agent:dev set.
- Orchestrator events 1-4 (#237-#240) are closed.
- Merged: answer receiver (#283 area), orchestrator gate, failure watch module (#287), friction script (#259), prefilter per event (#290).
- Main CI: status/validate runs queued or in progress, none red at measurement time.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.
- #154 is Daniel's (risk:security flip of main ruleset): not started by the orchestrator.

## Open
- #148 (docs 4): decision number 0011 is now used by the answer receiver; slip must pick a free number. Prerequisites 1a, 1b, 3 not verified.
- #134 wiring into the weekly summary is a follow-up after #254.
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #282 (owner issue, not approved): not started.

## Next 3 steps
1. Get PR #292 (#253) and the #241 PR through review.
2. Next approved issues: #270, #254 (after #253; both touch status/weekly files, check overlap first), #148.
3. Later #112.
