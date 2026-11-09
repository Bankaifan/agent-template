# 0003 Merge train

Issue: #124 (design study, no implementation in this PR).

## 1. Goal

Parallel agent PRs land one after another without human help. Two PRs that are green alone must not break `main`
together, and a conflict between them must start a fix round at once instead of waiting for a tick. A rebase must not
cost a full model re-review when the PR's own diff did not change. GitHub's merge queue is not available for repos owned
by a personal account, so the train is built from scripts, the ruleset and the existing agent-fix round.

## 2. Current state

- `.github/rulesets/main.json`: `strict_required_status_checks_policy: false`, so a PR may merge while behind `main`.
  `dismiss_stale_reviews_on_push` and `require_last_push_approval` are true, so every push drops the approval.
  Merge method is rebase only. Required checks: `validate`, `agent-smoke`, `risk`, `security-review`.
- `.github/workflows/automerge.yml`: enables `gh pr merge --auto --rebase` after an approval by the approver app
  (and again on a `security-review` success status). It never updates a branch.
- `tools/status.py`: conflicts (`mergeStateStatus == DIRTY`) get one fix round, dispatched at most one at a time on the
  next tick (30 or 60 min). `rebase_candidates()` already calls `PUT pulls/N/update-branch` with `update_method=rebase`,
  but only for own single-commit PRs whose last `validate` failed while main was red.
- `.agents/roles/orchestrator.md` and `orchestrator.yml:146`: slips "must touch disjoint files" is a prompt rule only.
  Nothing compares a new slip with the files of open agent PRs.
- `tools/ci/post_verdict.py`: the approver app approves or requests changes; `agent-review.yml` reviews on every green
  `validate` of a new head SHA (key: SHA + PR body hash, `agent_guard.py reviewed`). A rebase gives a new SHA, so a
  full sonnet review would run again.
- `tools/ci/risk.py`: `risk` and `security-review` are statuses per head SHA. A new SHA needs both again.
- `CODEOWNERS` lists only security-relevant paths; other agent PRs need no human.

## 3. Options with trade-offs

Order of merging:
- A. GitHub merge queue. Not available for personal-account repos. Rejected.
- B. Do nothing but strict checks. Every merge makes all other PRs BEHIND and auto-merge never updates a branch, so PRs
  stall until someone rebases. Rejected alone, needed together with C.
- C. Strict checks plus a script that rebases one PR at a time (the train). Chosen.

Re-approval after a rebase:
- R1. Always full model re-review. Safe, but costs a sonnet run per PR per landed PR (quadratic with parallel PRs).
- R2. Turn off `dismiss_stale_reviews_on_push`. Real changes would keep a stale approval. Rejected (weakens the review).
- R3. Script approval when the PR's own diff is unchanged (`git range-diff`), model review otherwise. Chosen.
- R4. Compare `gh pr diff` text of old and new head. Cheaper to implement, but line numbers and hunk context shift when
  main touched the same file, so it gives false "changed". `range-diff` (patch-id based) ignores that.

Prevention of overlap:
- P1. Prompt rule only (today). Not enforced.
- P2. A script the orchestrator must call before starting a slip: it lists the files of open agent PRs and the files
  named in the slip and fails on overlap. Chosen; the orchestrator is a model, so the check is advisory input for it,
  plus a hard second check in the train (conflict fix) if it is bypassed.

## 4. Chosen approach

**4.1 Prevention (point 1).** New `tools/overlap.py`: `overlap.py check <slip-file-list>` reads `gh pr list --state open`
files for agent PRs and exits 1 with the overlapping paths. The orchestrator role and `orchestrator.yml` prompt call it
before labelling `agent:dev`; on overlap the slip waits (comment "waits for PR #N") and starts when that PR is merged.
Lock files like `HANDOVER.md` are excluded. This repo has no `CHANGELOG.md`; for a project that has one, its conflict rate is open (see 9, Q1).

**4.2 Strict order (point 2).** Ruleset `strict_required_status_checks_policy: true`. Only a PR whose head contains the
current `main` tip can merge. This is the one owner decision (section 9). It goes last in the rollout, after 4.3 works,
because strict without the train stalls every second PR.

**4.3 Train step (point 3).** New `tools/train.py`, no model, run by a new workflow `train.yml` on `push` to `main`
(the merge just landed) and by `status.py` as a fallback every tick. It uses the author app token (a push by
`GITHUB_TOKEN` would not start `validate`). Algorithm per run, under `concurrency: train`:
1. List open agent PRs (same predicate as `status.py` `is_agent_pr`), skipping `needs-human`, drafts and `agent/*` PRs
   superseded by a newer PR for the same issue.
2. In flight: if an agent PR has auto-merge enabled and is neither BEHIND nor DIRTY (it sits on the current tip and waits
   for checks or review), stop. The next `push` to main starts the next run. This keeps exactly one PR in flight.
3. Candidate: the oldest PR (by number) with auto-merge enabled and `mergeStateStatus == BEHIND`. PRs without auto-merge
   are not ready and are not rebased (saves CI minutes).
4. DIRTY candidate (older first): dispatch `agent-fix.yml` with input `pr` immediately via the existing
   `status.py handle_conflict()` (reuse, one fix job at a time, round limit stays). A textual conflict is therefore found
   without waiting for the status tick, because the train probes with `update-branch` and reads the 422 "merge conflict".
5. Otherwise: store the old head SHA in a PR comment marker `train-base: <old-sha> <main-sha>`, then
   `PUT pulls/N/update-branch` with `update_method=rebase`. The rebase pushes with the author's commit intact (linear
   history, Daniel stays sole author). CI, review and auto-merge continue as today.

The rebase changes the SHA. Auto-merge stays armed (it is a PR property); the approval is restored by 4.4.

**4.4 Cheap re-approval (point 4).** New `tools/ci/reapprove.py`, run from a new workflow `reapprove.yml` on
`pull_request: synchronize` for `agent/*` branches (job-level `if`, runs from `main`, checks out main, never executes PR
code). It decides between script approval and model review:
1. Old head = the SHA in the latest `train-base` marker, or else the `commit_id` of the approver app's latest
   `APPROVED` review (dismissed reviews keep their `commit_id`). No old head: model review.
2. Fetch both heads as objects only (`git fetch origin <sha>`); run `git range-diff <old-base>..<old-head>
   <new-base>..<new-head>`. The PR is "unchanged" only if every commit pair is `=` (identical patch-id) and the commit
   count is equal. Any `!`, `<` or `>` means a real change: model review as today.
3. Also required for script approval: the PR's risk class is `none` or `infra` (not `security`: Daniel's approval is his,
   a script never renews it); the PR touches no CODEOWNERS path; the PR body hash equals that of the approved review.
4. Then, with the approver app token: submit an `APPROVE` review whose body ends with `body-hash: <hash>` and
   `reapproved-by-script: range-diff clean <old-sha> -> <new-sha>`. `agent_guard.py reviewed` already treats SHA + body
   hash as the key, so `agent-review` would skip the model for this SHA when the script has approved first. Order:
   `agent-review.yml` waits for `reapprove` (it triggers on `validate` success, which takes minutes; `reapprove` finishes in
   seconds) and `reapprove.py` also writes the guard marker.
5. Carry the statuses: `risk` re-computes on its own (cheap script). `security-review` is re-posted as `success` for the
   new SHA only when the old SHA had `success` and the range-diff is clean (`risk.py verdict`-style write). A real change
   stays `pending` and the security reviewer runs.

What the script does not prove: that the rebased PR works on the new main. `validate` and `agent-smoke` run on the new
head for that; the strict policy ensures they ran on the current tip. The model review judged the diff of the PR, and
the diff is byte-identical by patch-id, so a re-review would see the same text.

## 5. Migration and compatibility

- No breaking change for Daniel's workflow. Dependabot PRs and Daniel's own PRs are not agent PRs and are untouched by
  the train (dependabot has its own flow; with strict on they are updated by Dependabot's own rebase or `@dependabot rebase`.
  Open: Q2, whether the train should also rebase dependabot PRs).
- `status.py` keeps its red-main rebase and conflict handling; the train calls the same functions so there is one code
  path. The train and `status.py` both use the `update-branch` API, which is idempotent if the branch is already current.
- Rollout order keeps main protected at every step: scripts first, ruleset change last.

## 6. Test and verification plan

Unit tests (pytest, fake `gh` runner like `tests/test_status.py`) written with the code; each must fail on today's code:
- `test_overlap.py`: a slip file in an open agent PR is reported; disjoint files pass; excluded files pass.
- `test_train.py`: oldest BEHIND PR with auto-merge is chosen; no action while one is in flight; a DIRTY PR dispatches
  `agent-fix` once; `needs-human` and non-agent PRs are skipped; the marker comment is written before `update-branch`.
- `test_reapprove.py`: identical patch-ids approve; one changed line does not; a `security` PR does not; a missing old head
  does not; a body-hash change does not; with a real git repo in a tmp dir (rebase over an unrelated main commit gives `=`,
  rebase over a conflicting change with manual resolution gives `!`).
- `test_rules_json.py`: `main.json` has `strict_required_status_checks_policy: true` after the ruleset PR and the required
  contexts are unchanged.
Live proof before the ruleset flip (read-only on production plus one scratch PR pair): two throwaway agent PRs on disjoint
files; merge one; the train rebases the other, `reapprove` approves it, auto-merge lands it without a model run. Command
output goes into the PR body of the rollout PR. Open: whether `git fetch origin <old-sha>` works for a force-pushed-away
commit on GitHub; measure in PR 2. Fallback: the train writes the old head into a `refs/train/<pr>` ref, or compares via
the compare API.

## 7. Rollback

- Set `strict_required_status_checks_policy` back to `false` (Daniel, ruleset) and delete the `train.yml` and `reapprove.yml`
  triggers. Everything else is additive and inert without them.
- If `reapprove` approves wrongly: remove the workflow; the approval is a normal review and `dismiss_stale_reviews_on_push`
  still drops it on the next push. Each script approval carries both SHAs so it is auditable.
- Stalled train (PR in flight never merges): `status.py` already escalates orphans after 10 min without `validate`; the train
  also ignores a PR in flight that has `needs-human`.

## 8. Split into PR-sized implementation issues

Order matters; files are disjoint so they can be worked one after another without conflicts.

1. **Overlap check for slips.** Files: `tools/overlap.py`, `tests/test_overlap.py`, `.agents/roles/orchestrator.md`,
   `.github/workflows/orchestrator.yml`. Risk: `risk:infra` (workflow prompt text only, no permissions). Model: haiku.
2. **Train script and workflow.** Files: `tools/train.py`, `tests/test_train.py`, `.github/workflows/train.yml`, a small hook
   in `tools/status.py` (fallback call) and `tests/test_status.py`. Risk: `risk:infra`; the workflow needs token permissions
   for the author app, so likely `risk:security` (permissions). Keep `permissions: contents: read`, app token as in `status.yml`.
   Model: sonnet. Also measures the open `git fetch <old-sha>` question.
3. **Script re-approval.** Files: `tools/ci/reapprove.py`, `tests/test_reapprove.py`, `.github/workflows/reapprove.yml`,
   `.github/workflows/agent-review.yml` (wait or skip for a script-approved SHA). Approves with the approver app: `risk:security`
   (approval logic, token), reviewed by the security reviewer; Daniel approves. Model: sonnet.
4. **Ruleset flip.** Files: `.github/rulesets/main.json`, `tests/test_rules_json.py`, `docs/decisions/0010-merge-train.md`.
   Risk: `risk:security` (`.github/rulesets/` is a CODEOWNERS path). Daniel applies the ruleset in the GitHub settings after
   the merge (the file is the record; `bypass_actors` unchanged). Only after PR 2 and 3 are live and the live proof is in the PR.
5. **Optional, only for a project that has a `CHANGELOG.md` and only if its conflict rate (Q1, open) justifies it:**
   CHANGELOG hot-file handling. Files: open. Not applicable to this repo (no `CHANGELOG.md`).

## 9. Owner decisions

1. **Ruleset change** (only item that needs Daniel): `strict_required_status_checks_policy` false -> true on `main`
   (implementation PR 4, after the train works). Effect: a PR can merge only when its branch contains the latest `main`.
   Cost: more CI runs, one per landed PR per waiting PR. Worst case: a stuck train blocks merging until Daniel sets the flag
   back to false.

Open questions, no Daniel input needed (agents decide in the implementation PRs; marked "open" until measured):
- Q1. Open: how often a `CHANGELOG.md` conflicts. This repo has none, so the rate is unmeasured here. For a project that has
  one, decide between accepting the fix round and an `Unreleased` section per PR file. Not decided here.
- Q2. Whether dependabot PRs join the train. Open; v1 excludes them.
- Q3. Whether `git fetch <old-sha>` of an overwritten commit works on GitHub (see 6). Open until PR 2.
