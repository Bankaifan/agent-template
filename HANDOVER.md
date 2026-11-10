# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005, merged). Answer receiver (#191, design 0006, merged).

## Current state (measured 2026-11-10)
- Open PRs: #217 (for #150 overlap guard, risk:security, review:1, CHANGES_REQUESTED, agent-fix running). #213 no longer open.
- Main CI: status run in progress at measure time; no red run seen in the last 10.
- Started this run: #125 as a design study (slip written, model:sonnet, agent:dev). Output docs/design/NNNN-orchestrator-events.md.
- Created earlier from design 0006: #204 (hold, prio:1), #205-#208 (prio:3). Not approved, no agent:dev.
- Design 0005 issues #197-#201 exist (prio:1, not approved, no agent:dev).
- #92 stays needs-human. Design 0004: #148 not started. Design 0003: #150 in PR #217, #152 not started; #154 is Daniel's.
- #105 (Unblocker 4/5) looks superseded by #147 (unblocker.yml exists); not started.
- #99, #100 (overdue scheduled run issues): not dev work, not started.
- #195 state after this run: open (not re-measured).

## Open
- Design 0005 section 9 (Limit 5 exception) is a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open (#181 closed).
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).
- Exact cause of the #184 re-label: open, #204 reproduces it first.
- #171 and #191 are parent issues of designs 0005/0006; whether they get closed once the splits land: open.
- #125 design must not duplicate design 0006 (answer receiver).

## Next 3 steps
1. Merge of #217 (#150); then #152 and #212.
2. Start #204 and #205 once approved; #197 and #198 once on the trusted list.
3. Later #129, #132, #133, #119, #120, #112, #148.
