# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273; #269-#272 merged (nightly workflow on main).

## Current state (measured 2026-11-10, run 29)
- Open PRs: none. No agent/rule-keeper PRs open.
- Free agent:dev slots 3, free PR slots 5 at start of this run.
- Main CI: no red run in the last 10 (runs skipped, cancelled or in progress).
- #312 and #311 are merged (commits f2b1536, 8052d56).
- #309 (risk.yml gate failure): not a code defect (intentional owner gate on PR #307). Daniel answered "Ja", answer receiver owns it. Not touched.
- #313 (guard issue "Fail a silent run"): its cause (silent orchestrator run) was fixed by #312. Not started: no code defect known; Daniel may close it. Open: whether it recurs.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.

## Open
- #273 (docs 5/5) is next in the design split; check overlap first.
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).

## Next 3 steps
1. Get the #273 PR (started this run, overlap exit 0, agent:dev set) through review.
2. Re-check #313 after the next orchestrator run; close-or-fix decision.
3. Later #112.
