"""Progress rule for the review rounds: keep fixing while rounds resolve findings (decision 0021).

A round is a head with a finding: the approver app requested changes, the security review said `changes`, or CI was
red. The task stops (restart once, then parked: tools/restart.py limit) only when the same finding is still open after
STUCK_AFTER fix rounds in a row (it is on three reviewed heads in a row) or after agent_guard.MAX_ROUNDS rounds.
The reviewer writes every `changes` point as `changes[F<n>]: file:line reason` and keeps the id of a finding that is
still open; a review that names no id counts as the one finding `?`, the security review as the one finding `security`.

CLI (needs the gh CLI with GH_TOKEN and GH_REPO; `verdict` also APPROVER_BOT):
  review_rounds.py verdict PR   after a review: `none` (no round counted), `limit` (review:stop or MAX_ROUNDS),
                                `stuck` or `fix`
  review_rounds.py red PR       a red CI that is not a form failure: `limit`, `stuck` (third red head in a row, labels
                                ci-red:1, ci-red:2), else count the round (review:N, ci-red:N) and print `fix`
  review_rounds.py green PR     validate went green: remove every ci-red:* label, print what was removed
  review_rounds.py stop PR      add the label review:stop
A gh failure or bad JSON is not caught: the step fails visibly, there is no fallback verdict.
"""
import os
import re
import sys

import agent_guard
from agent_guard import MAX_ROUNDS, STOP, round_no

STUCK_AFTER = 2  # failed fix rounds in a row for one finding
SECURITY_PREFIX = "Security review asks for changes"  # = tools/ci/post_verdict.REQUEST_PREFIX (pinned by a test)
_ID = re.compile(r"\bchanges\[([A-Za-z0-9][\w.-]{0,30})\]")
_RED = re.compile(r"ci-red:(\d+)")


def finding_ids(body):
    """Ids of the `changes[ID]` points of a review body."""
    return set(_ID.findall(body or ""))


def history(reviews, approver):
    """Open findings per reviewed head, in the order the heads were first reviewed by the approver app. Per head: the
    ids of its latest code review (approved: none; changes requested without an id: `?`), plus `security` while a
    security request for changes on that head stands."""
    heads = {}
    for r in reviews:
        sha, state, body = r.get("commit_id"), r.get("state"), r.get("body") or ""
        if not sha or state not in ("APPROVED", "CHANGES_REQUESTED"):
            continue
        if not agent_guard.same_login((r.get("user") or {}).get("login"), approver):
            continue
        head = heads.setdefault(sha, {"code": set(), "security": False})
        if body.startswith(SECURITY_PREFIX):
            head["security"] = head["security"] or state == "CHANGES_REQUESTED"
        else:
            head["code"] = (finding_ids(body) or {"?"}) if state == "CHANGES_REQUESTED" else set()
    return [h["code"] | ({"security"} if h["security"] else set()) for h in heads.values()]


def stuck(hist):
    """True when one finding is open on each of the last STUCK_AFTER + 1 reviewed heads."""
    last = hist[-(STUCK_AFTER + 1):]
    return len(last) == STUCK_AFTER + 1 and bool(set.intersection(*last))


def red_streak(labels):
    """Red heads in a row: highest N of the `ci-red:N` labels, 0 without one."""
    return max((int(m.group(1)) for m in map(_RED.fullmatch, labels) if m), default=0)


def pr_labels(pr, run):
    return set(run("pr", "view", str(pr), "--json", "labels", "--jq", ".labels[].name").splitlines())


def verdict(pr, approver, run=agent_guard.gh):
    labels = pr_labels(pr, run)
    if STOP in labels or round_no(labels) >= MAX_ROUNDS:
        return "limit"
    if not round_no(labels):
        return "none"
    return "stuck" if stuck(history(agent_guard.reviews_of(pr, run), approver)) else "fix"


def red(pr, run=agent_guard.gh):
    labels = pr_labels(pr, run)
    if STOP in labels or round_no(labels) >= MAX_ROUNDS:
        return "limit"
    streak = red_streak(labels)
    if streak >= STUCK_AFTER:
        return "stuck"
    agent_guard.add_labels("pr", pr, [f"review:{round_no(labels) + 1}", f"ci-red:{streak + 1}"], run)
    return "fix"


def green(pr, run=agent_guard.gh):
    gone = sorted(n for n in pr_labels(pr, run) if _RED.fullmatch(n))
    if gone:
        run("pr", "edit", str(pr), *[a for n in gone for a in ("--remove-label", n)])
    return gone


def main(argv):
    if len(argv) != 3 or not argv[2].isdigit():
        print(__doc__, file=sys.stderr)
        return 2
    cmd, pr = argv[1], argv[2]
    if cmd == "verdict":
        print(verdict(pr, os.environ["APPROVER_BOT"]))
    elif cmd == "red":
        print(red(pr))
    elif cmd == "green":
        print(" ".join(green(pr)) or "no ci-red label")
    elif cmd == "stop":
        agent_guard.add_labels("pr", pr, [STOP])
        print(STOP)
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
