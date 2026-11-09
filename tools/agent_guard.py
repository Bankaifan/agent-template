"""Shared helpers for the agent workflows: login normalization, labels that always exist, silent-run guard.

CLI (needs the gh CLI with GH_TOKEN and GH_REPO):
  agent_guard.py login LOGIN                 print the normalized login
  agent_guard.py same A B                    exit 0 if both logins name the same account
  agent_guard.py label pr|issue N LABEL...   create each label if missing, then add it
  agent_guard.py agent-pr AUTHOR [LABELS]    exit 0 if the PR is an agent PR (env AUTHOR_BOT, OWNER; LABELS comma list)
  agent_guard.py reviewed PR SHA             exit 0 if the approver app (env APPROVER_BOT) reviewed SHA
  agent_guard.py silent dev ISSUE SINCE      after agent-dev: no PR for agent/ISSUE-* created at/after SINCE (UTC ISO) -> escalate
  agent_guard.py silent fix PR HEAD_BEFORE   after agent-fix: PR head unchanged -> escalate
  agent_guard.py silent review PR SHA        after agent-review: no approver review for SHA -> escalate
Escalate = comment (run URL, last lines of the execution file), label needs-human, request OWNER's review.
Environment for escalation: RUN_URL, EXEC_FILE (path of the action's execution file), OWNER (default Bankaifan).
"""
import json
import os
import re
import subprocess
import sys

OWNER_DEFAULT = "Bankaifan"
TAIL_LINES = 15
TAIL_CHARS = 1500
_SECRET = re.compile(r"(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9_-]{20,})")


def norm_login(login):
    """`app/x`, `x[bot]` and `x` all name the same account; compare case-insensitively."""
    s = (login or "").strip()
    s = s.removeprefix("app/")
    s = s.removesuffix("[bot]")
    return s.lower()


def same_login(a, b):
    na = norm_login(a)
    return bool(na) and na == norm_login(b)


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def ensure_label(name, run=gh):
    """Create the label if missing. A failure is not fatal: the label may exist and the add will tell."""
    try:
        run("label", "create", name, "--force")
    except (subprocess.CalledProcessError, OSError):
        pass


def add_labels(kind, number, labels, run=gh):
    for name in labels:
        ensure_label(name, run)
    run(kind, "edit", str(number), *[a for name in labels for a in ("--add-label", name)])


def is_agent_pr(author, labels, author_bot, owner):
    """Own-branch PRs by the author app or by the owner's account are reviewed; others only with agent:review."""
    return same_login(author, author_bot) or same_login(author, owner) or "agent:review" in labels


def has_review(reviews, approver, sha):
    return any(r.get("commit_id") == sha and same_login((r.get("user") or {}).get("login"), approver)
               for r in reviews)


def dev_has_pr(prs, issue, since):
    """A PR for agent/ISSUE-* created by this run: createdAt >= SINCE (same UTC ISO format, compares as text).
    Older PRs for the same issue number, open or closed, must not hide a silent run."""
    prefix = f"agent/{issue}-"
    return any(p.get("headRefName", "").startswith(prefix) and p.get("createdAt", "") >= since for p in prs)


def head_moved(before, after):
    return bool(after) and after != before


def tail_text(text, lines=TAIL_LINES, chars=TAIL_CHARS):
    """Last lines of the execution file, secret-looking tokens masked, fences neutralized, length capped."""
    out = "\n".join(text.splitlines()[-lines:])[-chars:].replace("```", "'''")
    return _SECRET.sub("***", out)


def report(kind, what, run_url, exec_text):
    tail = tail_text(exec_text) if exec_text else "(no execution file)"
    return (f"agent-{kind} run finished silently: {what}.\n\nRun: {run_url or '(unknown)'}\n\n"
            f"Last lines of the execution file:\n```\n{tail}\n```\n"
            "Labelled needs-human; Daniel is asked to look at it.")


def read_exec(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, TypeError):
        return ""


def escalate(kind, number, is_pr, what, owner, run=gh):
    body = report(kind, what, os.environ.get("RUN_URL", ""), read_exec(os.environ.get("EXEC_FILE", "")))
    thing = "pr" if is_pr else "issue"
    add_labels(thing, number, ["needs-human"], run)
    run(thing, "comment", str(number), "--body", body)
    if is_pr:
        author = json.loads(run("pr", "view", str(number), "--json", "author"))["author"]["login"]
        if not same_login(author, owner):  # nobody can review their own PR
            try:
                run("pr", "edit", str(number), "--add-reviewer", owner)
            except subprocess.CalledProcessError:
                print("review request failed")
    else:  # an issue has no reviewers: assigning puts it in the owner's inbox
        try:
            run("issue", "edit", str(number), "--add-assignee", owner)
        except subprocess.CalledProcessError:
            print("assignment failed")


def reviews_of(pr, run=gh):
    pages = json.loads(run("api", "--paginate", "--slurp", f"repos/{os.environ['GH_REPO']}/pulls/{pr}/reviews"))
    return [r for page in pages for r in page]


def main(argv):
    owner = os.environ.get("OWNER", OWNER_DEFAULT)
    cmd, args = (argv[1], argv[2:]) if len(argv) > 1 else ("", [])
    if cmd == "login" and len(args) == 1:
        print(norm_login(args[0]))
    elif cmd == "same" and len(args) == 2:
        return 0 if same_login(*args) else 1
    elif cmd == "label" and len(args) >= 3 and args[0] in ("pr", "issue"):
        add_labels(args[0], args[1], args[2:])
    elif cmd == "agent-pr" and len(args) in (1, 2):
        labels = (args[1] if len(args) == 2 else "").split(",")
        return 0 if is_agent_pr(args[0], labels, os.environ.get("AUTHOR_BOT", ""), owner) else 1
    elif cmd == "reviewed" and len(args) == 2:
        return 0 if has_review(reviews_of(args[0]), os.environ.get("APPROVER_BOT", ""), args[1]) else 1
    elif cmd == "silent" and len(args) >= 2:
        kind, number = args[0], args[1]
        if kind == "dev" and len(args) == 3:
            prs = json.loads(gh("pr", "list", "--state", "all", "--limit", "100", "--json", "headRefName,createdAt"))
            if not dev_has_pr(prs, number, args[2]):
                escalate("dev", number, False, f"no PR was produced for the agent/{number}-* branch", owner)
        elif kind == "fix" and len(args) == 3:
            after = json.loads(gh("pr", "view", number, "--json", "headRefOid"))["headRefOid"]
            if not head_moved(args[2], after):
                escalate("fix", number, True, "no fix was produced (the PR head has no new commit)", owner)
        elif kind == "review" and len(args) == 3:
            if not has_review(reviews_of(number), os.environ.get("APPROVER_BOT", ""), args[2]):
                escalate("review", number, True, "no review by the approver app exists for the head commit", owner)
        else:
            return 2
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
