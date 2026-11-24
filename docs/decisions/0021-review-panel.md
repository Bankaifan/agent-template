# 0021 REVIEW-PANEL: a code reviewer with specialists, rounds by progress

Name of the work: `REVIEW-PANEL`. Changes the round limit of decisions 0002 and 0004.

## Decision
1. The reviewer becomes the lead code reviewer (`.agents/roles/reviewer.md`). In the same model run it starts
   specialist reviewers as parallel subagents: `silent-failure-hunter`, `pr-test-analyzer`, `type-design-analyzer`
   (haiku, Read/Glob/Grep only, they never run PR code). `tools/review_select.py` picks them from the added lines of
   the staged diff, no model involved; a docs-only change gets none. The lead checks every reported point against the
   diff, classes it and submits the one review. No comment or simplification specialist: that is style (`cleaner.md`).
2. The fixed limit of 3 reviews is replaced by a progress rule (`tools/review_rounds.py`): fix rounds continue while
   they resolve findings. The task restarts once, then is parked (`tools/restart.py limit`, unchanged), only when the
   same finding is still open after two fix rounds in a row, or at the emergency brake of 8 rounds.

## Why own role files and not the pr-review-toolkit plugin
The action could install the plugin (`plugins`, `plugin_marketplaces`). Against it:
- no documented way to pin a plugin version: unpinned third-party prompt text in a job that holds the approver token;
- its agents assume a working checkout they may run, and report confidence scores instead of our verdict classes;
- loading plugins under `--setting-sources user` is undocumented.
The role files are short, byte-capped (`docs/budgets.json`) and written in our own words.

## The round rule and its assumptions
- A round is a head with a finding: the approver app requests changes, the security review says `changes`, or CI is
  red. Labels `review:N` count them; `review:stop` marks a PR that hit the rule.
- Findings carry ids: every `changes` point is `changes[F<n>]: file:line reason`, and a finding still open keeps its
  id. An id on three reviewed heads in a row is stuck.
- A review that requests changes without an id counts as the one finding `?`: it degrades to the old limit of two fix
  rounds, never to an endless loop. The security review has no ids and counts as the one finding `security`.
- A red CI has no finding text. The streak of red heads in a row is counted instead (labels `ci-red:1`, `ci-red:2`,
  cleared when validate is green on a reviewed head): the third red head in a row stops.
- The reviewer counts a head before it reviews, so the brake gives 8 reviews and 7 fix rounds.

## Cost (estimate, not measured)
The specialists run on haiku and read only the diff (the delta in later rounds). Rough: +10-15% of one sonnet review
per specialist, plus +10-20% for the lead's extra turns. Per review: about +0% (docs only), +25% (one specialist), up
to about +60% (all three). The worst case per PR rises from 3 to 8 reviews, though only while findings keep getting
resolved.

## Open
- Not verified end to end: that subagents start under `--setting-sources user`, and whether their turns count against
  `--max-turns` (raised from 20 to 30). The line `reviewers: ...` in every review shows what ran; if a subagent
  cannot be started, the lead does its check from the role file.
