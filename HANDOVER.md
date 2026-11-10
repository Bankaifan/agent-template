# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273; #269-#272 merged (nightly workflow on main).

## Current state (measured 2026-11-10)
- Open PRs: none. No agent/rule-keeper PRs open.
- Free agent:dev slots 3, free PR slots 5 at start of this run.
- Main CI: no red run in the last 10 (recent runs skipped or in progress).
- Started this run: #312 (orchestrator runs end silently, prio:1, files orchestrator.yml and orchestrator role) and #311 (agent-fix.yml checkout failure, prio:2). Slips written, overlap exit 0, model:sonnet and agent:dev set.
- #313 (same run as #312, "Fail a silent run"): not started, overlaps #312 files; retry after #312 merges.
- #309 (risk.yml classify failure): already has agent:dev and needs-human, not touched this run.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.

## Open
- #273 (docs 5/5) is next in the design split; check overlap first.
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- Cause of the #309 risk.yml failure and the #311 checkout failure: open.

## Next 3 steps
1. Get the #312 and #311 PRs through review.
2. Then #313 and #273 (overlap check first).
3. Later #112.
