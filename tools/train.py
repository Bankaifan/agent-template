"""Merge train core (docs/design/0003-merge-train.md, sections 4.3 and 5): lets approved agent PRs land one after another.

Model-free. The workflow (a later PR) runs it on push to main, on a schedule and on dispatch. One run:
1. Candidates: open same-repo agent PRs (status.is_agent_pr), not needs-human, not design PRs (only docs/design/ files),
   with an APPROVED review of the approver app on their current head (agent_guard.has_review).
   Oldest PR number first. A CHANGES_REQUESTED or dismissed review does not count.
2. One in flight: if a candidate is CLEAN, UNSTABLE or HAS_HOOKS, or BLOCKED with a required check running, it is about
   to merge. "Running" counts only the checks that `.github/rulesets/main.json` requires (none listed: every check).
   The run does nothing; the push of that merge starts the next run.
3. The oldest BEHIND candidate with auto-merge enabled is rebased (PUT pulls/N/update-branch, update_method=rebase).
4. The oldest DIRTY candidate gets status.handle_conflict at once, unless an agent-fix run is queued or running.
   First, if it is a one-commit PR that bumps VERSION, `rebump_branch` tries the model-free re-bump (tools/rebump.py,
   design 0013 step 2) in a scratch clone: only when the conflict set is exactly VERSION and CHANGELOG.md the branch is
   rebased onto main with the re-bumped files and force-pushed (with lease on the head it read). The push dismisses the
   approval, so the reviews run on the new head. Any refusal or error: today's handle_conflict path, unchanged.
5. A PR waiting only for the owner (waiting_for_owner) is skipped: it never counts as in flight, so the next ready PR
   lands. When main moves it is still rebased (BEHIND, even without auto-merge) or sent to agent-fix (DIRTY), so the
   owner approves the current head; the push re-runs the agent reviews. After his approval it is a normal candidate.
6. Prints numbers and actions, never tokens. A failed gh call is reported and ends the run with exit 1, before
   any label change of that run.

CLI: train.py   do the run. Environment: GH_REPO, APPROVER_BOT (unset: nothing is approved, nothing happens),
     OWNER (default Bankaifan). Needs the gh CLI with GH_TOKEN.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import agent_guard
import status

REBUMP = Path(__file__).resolve().parent / "rebump.py"  # always main's copy: the PR's code is never run
CONFLICT_FILES = {"VERSION", "CHANGELOG.md"}
COMMITTER = ("Daniel", "476059+Bankaifan@users.noreply.github.com")

IN_FLIGHT = {"CLEAN", "UNSTABLE", "HAS_HOOKS"}
ACTIVE_RUN = {"in_progress", "queued", "waiting", "requested", "pending"}
LIST_FIELDS = ("number,title,url,headRefName,headRefOid,labels,mergeStateStatus,statusCheckRollup,"
               "isCrossRepository,files,autoMergeRequest,reviewRequests")


def jlist(run, *args):
    return json.loads(run(*args))


def is_design_pr(pr):
    files = [f.get("path", "") for f in pr.get("files") or []]
    return bool(files) and all(f.startswith("docs/design/") for f in files)


def approved_on_head(pr, reviews, approver):
    """Only APPROVED reviews count: has_review alone also matches a CHANGES_REQUESTED review on the same head."""
    approved = [r for r in reviews if (r.get("state") or "").upper() == "APPROVED"]
    return agent_guard.has_review(approved, approver, pr["headRefOid"])


MAX_WAITING = 5  # waiting-for-owner PRs at once; beyond that new security slips wait


def waiting_for_owner(pr, reviews, approver, owner, required=None):
    """Agent PR with every agent review approved at its head, green CI (security-review included) and only the
    owner's approval missing: risk:security, a review request to the owner, no needs-human, not a design PR."""
    return (status.is_agent_pr(pr) and "risk:security" in status.names(pr) and "needs-human" not in status.names(pr)
            and not is_design_pr(pr) and status.ci_state(pr.get("statusCheckRollup"), required) == "green"
            and any(status.same_login(r.get("login"), owner) for r in pr.get("reviewRequests") or [])
            and approved_on_head(pr, reviews, approver))


def candidates(prs, reviews_of, approver):
    """Approved agent PRs, oldest first. reviews_of(number) is called only for PRs that pass the cheap filters."""
    out = []
    for p in prs:
        if not status.is_agent_pr(p) or "needs-human" in status.names(p) or is_design_pr(p):
            continue
        if approved_on_head(p, reviews_of(p["number"]), approver):
            out.append(p)
    return sorted(out, key=lambda p: p["number"])


def in_flight(pr, required=None):
    state = pr.get("mergeStateStatus")
    return state in IN_FLIGHT or (state == "BLOCKED"
                                  and status.ci_state(pr.get("statusCheckRollup"), required) == "running")


def plan(cands, fix_busy, waiting=(), required=None):
    """(PR in flight or None, PR to rebase or None, PR for a conflict fix or None). Nothing else happens while one is in flight.
    `waiting` = numbers of waiting-for-owner PRs: never in flight, rebased when BEHIND even without auto-merge.
    `required` = the ruleset's required checks; a non-required check neither holds the train nor counts as red."""
    busy = next((p for p in cands if p["number"] not in waiting and in_flight(p, required)), None)
    if busy:
        return busy, None, None
    rebase = next((p for p in cands if p.get("mergeStateStatus") == "BEHIND"
                   and (p.get("autoMergeRequest") or p["number"] in waiting)), None)
    conflict = None if fix_busy else next(iter(status.conflict_prs(cands)), None)
    return None, rebase, conflict


def git_env(token=""):
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_COMMITTER_NAME": COMMITTER[0],
           "GIT_COMMITTER_EMAIL": COMMITTER[1], "GIT_AUTHOR_NAME": COMMITTER[0], "GIT_AUTHOR_EMAIL": COMMITTER[1]}
    if token:  # through the environment, never argv
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="http.extraheader",
                   GIT_CONFIG_VALUE_0=f"AUTHORIZATION: basic {basic}")
    return env


def rebump_branch(pr, remote, token="", base="main"):
    """Model-free fix of a DIRTY PR whose conflict set is only VERSION and CHANGELOG.md (design 0013 step 2).
    True: the PR branch was rebased onto `base` with the re-bumped files and pushed. False: nothing was pushed
    (not a candidate, any other conflict, rebump refused, push lost the lease or any git error); the caller falls
    back to the agent-fix path."""
    branch, head = pr["headRefName"], pr["headRefOid"]
    if "VERSION" not in [f.get("path") for f in pr.get("files") or []]:
        return False
    env = git_env(token)

    def git(tmp, *args, check=True):
        return subprocess.run(["git", *args], cwd=tmp, env=env, check=check, capture_output=True, text=True)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            git(tmp, "init", "-q")
            git(tmp, "fetch", "-q", remote, f"+refs/heads/{base}:refs/remotes/origin/{base}",
                f"+refs/heads/{branch}:refs/remotes/origin/pr")
            if git(tmp, "rev-parse", "refs/remotes/origin/pr").stdout.strip() != head:
                return False  # the head moved since the list
            git(tmp, "checkout", "-q", "--detach", head)
            if git(tmp, "rev-list", "--count", f"origin/{base}..HEAD").stdout.strip() != "1":
                return False
            if subprocess.run([sys.executable, "-I", str(REBUMP), f"origin/{base}"], check=False, cwd=tmp,
                              env=env, capture_output=True, text=True).returncode != 0:
                return False
            texts = {f: Path(tmp, f).read_text(encoding="utf-8") for f in sorted(CONFLICT_FILES)}
            git(tmp, "checkout", "-q", "--", *sorted(CONFLICT_FILES))
            stopped = git(tmp, "rebase", f"origin/{base}", check=False).returncode != 0
            if stopped and not set(git(tmp, "diff", "--name-only", "--diff-filter=U").stdout.split()) <= CONFLICT_FILES:
                git(tmp, "rebase", "--abort", check=False)
                return False
            for f, text in texts.items():
                Path(tmp, f).write_text(text, encoding="utf-8")
            git(tmp, "add", *sorted(CONFLICT_FILES))
            if stopped:
                git(tmp, "-c", "core.editor=true", "rebase", "--continue")
            else:
                git(tmp, "commit", "-q", "--amend", "--no-edit")
            git(tmp, "push", "-q", f"--force-with-lease=refs/heads/{branch}:{head}", remote, f"HEAD:refs/heads/{branch}")
    except (subprocess.CalledProcessError, OSError):
        return False
    return True


def run_train(env, run=status.gh, rebumper=None):
    repo = env["GH_REPO"]
    if rebumper is None:
        def rebumper(p):
            return rebump_branch(p, f"https://github.com/{repo}.git", env.get("GH_TOKEN", ""))
    owner = env.get("OWNER", status.OWNER_DEFAULT)
    approver = env.get("APPROVER_BOT", "")
    required = status.required_contexts()  # None: every check counts
    try:
        prs = jlist(run, "pr", "list", "--state", "open", "--limit", str(status.PR_LIMIT), "--json", LIST_FIELDS)

        def reviews_of(number):
            pages = jlist(run, "api", "--paginate", "--slurp", f"repos/{repo}/pulls/{number}/reviews")
            return [r for page in pages for r in page]

        cands = candidates(prs, reviews_of, approver)
        waiting = {p["number"] for p in cands
                   if waiting_for_owner(p, reviews_of(p["number"]), approver, owner, required)}
        fix_runs = jlist(run, "run", "list", "--workflow", "agent-fix.yml", "--limit", "5", "--json", "status")
        fix_busy = any(r.get("status") in ACTIVE_RUN for r in fix_runs)
        busy, rebase, conflict = plan(cands, fix_busy, waiting, required)
        if busy:
            print(f"waiting: PR #{busy['number']} is about to merge; the train runs again after its push")
            return 0
        if rebase:
            run("api", "-X", "PUT", f"repos/{repo}/pulls/{rebase['number']}/update-branch", "-f", "update_method=rebase")
            print(f"rebased PR #{rebase['number']} onto main")
        if conflict:
            if rebumper(conflict):
                print(f"conflict PR #{conflict['number']}: re-bumped VERSION and CHANGELOG.md, pushed; reviews run on the new head")
            else:
                print(f"conflict PR #{conflict['number']}: {status.handle_conflict(conflict, owner, run)}")
        if not rebase and not conflict:
            print(f"nothing to do; approved candidates: {len(cands)}, waiting for owner: {len(waiting)}")
    except subprocess.CalledProcessError as e:
        print(f"train stopped: a gh call exited {e.returncode}; this run changed no labels")
        return 1
    return 0


def main(argv):
    if len(argv) == 1:
        return run_train(os.environ)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
