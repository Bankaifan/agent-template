# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273; #269 script merged.

## Current state (measured 2026-11-10)
- Open PRs: #304 (test scoping 2/5, #270, review:1). No agent/rule-keeper PRs open.
- Free agent:dev slots 3, free PR slots 4 at start of this run.
- Merged: #134 wiring into the weekly summary (86611e9). Main CI: no red run in the last 10.
- Started this run: #148 (docs for the boundary). Slip rewritten: decision number 0013 (0011, 0012 taken). Overlap check passed, agent:dev set.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.
- #154 is Daniel's (risk:security flip of main ruleset): not started by the orchestrator.

## Open
- #271-#273 depend on #270 (PR #304) merging; #271 and #272 are risk:security.
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #282 (owner issue, not approved): not started.
- Prerequisites 1a/1b of design 0004 not re-verified individually for #148.

## Next 3 steps
1. Get #304 and the #148 PR through review.
2. After #304 merges: #271 (check overlap first).
3. Later #112.
