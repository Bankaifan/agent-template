# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005, merged). Answer receiver (#191, design 0006, merged).

## Current state (measured 2026-11-10)
- #217 (overlap guard, #150) is merged (guard commit c69fb53 on main).
- Open PR #223 (for #204, risk:security, needs-human, APPROVED): validate/classify failed once, agent-fix and unblocker ended silently. Slip rewritten once already; do not touch a third time.
- Started this run: #210 (slip posted, model:sonnet + agent:dev). Overlap guard exit 0. Free PR slots now 1.
- Main CI: last 10 runs green, skipped or cancelled; no red main.
- Started earlier: #125 design study, no PR seen (open).
- Design 0005 issues #197-#201 exist (prio:1, not approved, no agent:dev).
- #92 stays needs-human. Design 0004: #148 not started. Design 0003: #150 in PR #217, #152 not started; #154 is Daniel's.
- #105 looks superseded by #147 (unblocker.yml exists); not started.
- #99, #100 (overdue scheduled run issues): not started.

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open (#181 closed).
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Whether the fixed agent-fix log fetch (2b8b234) lets #223 go green: open.
- #171 and #191 are parent issues of designs 0005/0006; whether they get closed once the splits land: open.
- #125 design must not duplicate design 0006 (answer receiver).

## Next 3 steps
1. Merge of #223 (#204); then #152, #212, #205, #206.
2. Result of #210; remove agent:dev from #150 (merged).
3. Later #129, #132, #133, #119, #120, #112, #148.
