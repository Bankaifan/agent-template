# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.
Test scoping (#135, design 0009): implementation issues #269-#273; #269 and #270 merged.

## Current state (measured 2026-11-10)
- Open PRs: #308 (test scoping 3/5, #271, approved, review:1, risk:infra), #307 (merge train 5, #154, needs-human, waits for Daniel). No agent/rule-keeper PRs open.
- Free agent:dev slots 2, free PR slots 3 at start of this run.
- Main CI: no red run in the last 10 (runs in progress were for PR 308).
- Started this run: #272 (nightly workflow, 4/5, risk:security). Slip written, overlap check passed (exit 0), model:sonnet and agent:dev set.
- #309 (failing risk.yml classify run): not approved, not started.
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190, #135 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step): not started.
- #154 is Daniel's (PR #307 needs his review): not touched.

## Open
- #273 (docs 5/5) should follow after #271 and #272 merge.
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #282 (owner issue, not approved): not started.
- Cause of the #309 risk.yml failure: open.

## Next 3 steps
1. Get #308 and the #272 PR through review.
2. After both merge: #273 (check overlap first).
3. Later #112.
