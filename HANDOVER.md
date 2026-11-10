# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007): designs merged.

## Current state (measured 2026-11-10)
- No open PRs. Main CI: last runs green (validate on main was in_progress at measurement).
- Merged this session: #246 (roles, closes #133), #247 (check_test_evidence.py, Refs #132).
- Removed agent:dev from #132 (PR #247 merged). Wiring into CI/Makefile is a carry, not yet an issue (open).
- Started #190 (failure watch) as a design task: slip posted, model:sonnet and agent:dev set. Output: docs/design/0008-failure-watch.md.
- #92, #191, #124, #125 are design parents with split issues; not started directly.
- #105: done on main, issue still open, Daniel closes.
- Design 0007 split issues #237-#241 exist (open, not on the trusted list, so not started).
- #148 not started. #154 is Daniel's. #244 is not approved.
- #99/#100 may still be open; #190 should auto-close such issues (open).

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open.
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- #171, #191, #125 are parent issues of designs; whether they close once splits land: open.
- Why #237-#241 are not approved or listed: open.
- Wiring of check_test_evidence.py into CI needs a follow-up slip (workflow file, risk:security).

## Next 3 steps
1. Design 0008 PR for #190: after merge remove agent:dev, create split issues.
2. #205, #206 (answer receiver), wiring slip for check_test_evidence.py.
3. Later #119, #120, #112, #148.
