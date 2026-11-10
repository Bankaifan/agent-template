# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005), Answer receiver (#191, design 0006), Orchestrator events (#125, design 0007), Failure watch (#190, design 0008): designs merged.

## Current state (measured 2026-11-10)
- Open PRs: #257 (#251 trusted title allowlist, risk:security); its `risk` check failed at 08:43, `validate` was still running.
- Main CI: status runs green; orchestrator run in progress at measurement time.
- Started #134 (friction reports): slip posted, model:sonnet and agent:dev set. Wiring into tools/weekly_summary.py is a follow-up (#254 owns that file).
- #132: slip done (check_test_evidence.py is on main); CI wiring still needs a follow-up slip (workflow file, risk:security).
- #105: done on main, issue still open, Daniel closes.
- #92, #191, #124, #125, #190 are design parents with split issues; not started directly.
- #120 needs Daniel's decision (permission change vs. drop alert step), no Recommended line: not started.
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
1. Check PR #257 (#251) outcome; then #252 once it is on the trusted list.
2. #135, #206 (answer receiver), wiring slip for check_test_evidence.py.
3. Later #112, #148.
