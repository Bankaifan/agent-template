# Handover
<!-- Overwrite, do not append. History lives in git and CHANGELOG. Max 60 lines. -->

## Goal
Unblocker role (#92, design 0002) on the untrusted-text boundary (design 0004, merged). Merge train (#124, design 0003, merged).
Risk class tightening (#171, design 0005, merged). Answer receiver (#191, design 0006, PR #194 open).

## Current state (measured 2026-11-10)
- Merged: #193 (design 0005), #196 (security PRs merge on AI security review), #189, #187, #185.
- Closed unmerged: #184 (for #171), #181, #177.
- Open PRs: #194 (design 0006, approved by reviewer, section "Owner decisions" says none, left to auto-merge).
- Open agent:dev issues: #191 (design in #194). #171 had agent:dev removed this run (design PR merged).
- Created this run from design 0005: #197, #198, #199, #200, #201 (prio:1, no agent:dev yet).
- Free agent:dev slots were 0, PR slots 2 (script count): nothing started.
- #92 stays needs-human. Design 0004: #148 not started. Design 0003: #150, #152 not started; #154 is Daniel's.

## Open
- Design 0005 section 9 (Limit 5 exception) is still a yes/no question for Daniel; it blocks #201 only.
- Whether #153 is restarted: open (#181 closed).
- #117 follow-up: second app token scoped to the template repo (Daniel to provision).
- How the ruleset file reaches the live ruleset (#154).

## Next 3 steps
1. Merge of #194, then create implementation issues from design 0006 section 8.
2. Start #197 and #198 (disjoint files), then #199, #200.
3. Later #182, #150, #152, #125 (design first), #119, #120, #112, #148.
