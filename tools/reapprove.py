"""Cheap re-approval (docs/design/0003-merge-train.md, section 4.4): approve a rebased head without the model.

CLI: reapprove.py PR SHA   exit 0 = approved by script, exit 1 = refused (the model review runs as today).
Environment: GH_REPO, APPROVER_BOT, OWNER (default Bankaifan), GH_TOKEN of the approver app. Runs from main, inside
agent-review.yml; the PR text, the patch and the review bodies are data and are never executed or opened as files.

Approves only if all hold (every doubt refuses, fail closed):
1. Agent PR, open, one commit, no needs-human, not risk:security, not a design PR, no CODEOWNERS path touched.
2. The newest earlier approver review (head OLD != SHA) was an APPROVED review when submitted and names the current
   `body-hash:`. A dismissed review counts only if the PR timeline confirms `previous_review_state` APPROVED.
3. `git patch-id --verbatim` of the commit patch of OLD equals the one of SHA (patches from the API, nothing checked out).
A script review carries the body-hash line, so the next comparison chains from it.
"""
import json
import os
import pathlib
import subprocess
import sys

import agent_guard

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "ci"))
import risk

PATCH_ACCEPT = "Accept: application/vnd.github.patch"
PR_FIELDS = "number,state,headRefOid,headRefName,isCrossRepository,labels,commits,files,body"


def patch_id(patch_text):
    """`git patch-id --verbatim` of a commit patch; '' if there is no id (empty patch)."""
    out = subprocess.run(["git", "patch-id", "--verbatim"], input=patch_text, capture_output=True, text=True,
                         check=True).stdout
    return out.split()[0] if out.split() else ""


def _names(pr):
    return {lab["name"] for lab in pr.get("labels") or []}


def pr_eligible(pr, codeowners, owner):
    """Reason the PR is not eligible for a script approval, else None."""
    files = [f.get("path", "") for f in pr.get("files") or []]
    if pr.get("state") != "OPEN":
        return "not open"
    if not pr.get("headRefName", "").startswith("agent/") or pr.get("isCrossRepository"):
        return "not an own-repo agent PR"
    if len(pr.get("commits") or []) != 1:
        return "not exactly one commit"
    if _names(pr) & {"needs-human", "risk:security"}:
        return "needs-human or risk:security"
    if files and all(f.startswith("docs/design/") for f in files):
        return "design PR"
    if len(files) >= 100:
        return "100 or more files (the file list is capped)"
    if not files or any(risk.owned_by(f, codeowners, owner) for f in files):
        return "no files or a CODEOWNERS path"
    return None


def prior_state_approved(review, timeline):
    """True if the review was an approval when submitted. A DISMISSED review needs a timeline event whose
    previous_review_state is 'approved'; a missing or other value refuses."""
    state = (review.get("state") or "").upper()
    if state == "APPROVED":
        return True
    if state != "DISMISSED":
        return False
    for ev in timeline:
        if ev.get("event") != "review_dismissed":
            continue
        d = ev.get("dismissed_review") or {}
        if d.get("review_id") != review.get("id"):
            continue
        prev = ev.get("previous_review_state") or d.get("previous_review_state")
        if str(prev or "").lower() == "approved":
            return True
    return False


def previous_head(reviews, timeline, approver, sha, bhash):
    """Head OLD of the newest earlier approver review if it qualifies (approved, same body-hash), else None."""
    mine = [r for r in reviews if agent_guard.same_login((r.get("user") or {}).get("login"), approver)]
    if not mine or any(r.get("commit_id") == sha for r in mine):
        return None  # no earlier review, or this head is already reviewed
    newest = mine[-1]
    m = agent_guard._BODY_HASH_LINE.search(newest.get("body") or "")
    if not m or m.group(1).lower() != bhash or not prior_state_approved(newest, timeline):
        return None
    return newest.get("commit_id") or None


def decide(pr, reviews, timeline, sha, approver, codeowners, owner, fetch_patch):
    """(old_sha, patch_id, None) to approve, or (None, None, reason). fetch_patch(sha) returns the commit patch text."""
    why = pr_eligible(pr, codeowners, owner)
    if why:
        return None, None, why
    bhash = agent_guard.body_hash(pr.get("body"))
    old = previous_head(reviews, timeline, approver, sha, bhash)
    if not old:
        return None, None, "no qualifying earlier approval"
    new_id, old_id = patch_id(fetch_patch(sha)), patch_id(fetch_patch(old))
    if not new_id or new_id != old_id:
        return None, None, "patch changed"
    return old, new_id, None


def run_reapprove(pr_number, sha, env, run=agent_guard.gh):
    repo, approver = env["GH_REPO"], env.get("APPROVER_BOT", "")
    owner = env.get("OWNER", agent_guard.OWNER_DEFAULT)
    if not approver:
        print("refused: APPROVER_BOT is unset")
        return 1
    try:
        pr = json.loads(run("pr", "view", str(pr_number), "--json", PR_FIELDS))
        if pr.get("headRefOid") != sha:
            print("refused: head moved")
            return 1
        reviews = agent_guard.reviews_of(pr_number, run)
        pages = json.loads(run("api", "--paginate", "--slurp", f"repos/{repo}/issues/{pr_number}/timeline"))
        timeline = [e for page in pages for e in page]
        codeowners = risk.read_text(".github/CODEOWNERS")

        def fetch(s):
            return run("api", f"repos/{repo}/commits/{s}", "-H", PATCH_ACCEPT)

        old, pid, why = decide(pr, reviews, timeline, sha, approver, codeowners, owner, fetch)
        if why:
            print(f"refused: {why}")
            return 1
        body = (f"Re-approved without model: patch unchanged since {old} (patch-id {pid}).\n\n"
                f"body-hash: {agent_guard.body_hash(pr.get('body'))}")
        if json.loads(run("pr", "view", str(pr_number), "--json", "headRefOid")).get("headRefOid") != sha:
            print("refused: head moved")
            return 1
        # Pinned to SHA through the API: `gh pr review` would approve whatever the head is at that moment.
        run("api", "-X", "POST", f"repos/{repo}/pulls/{pr_number}/reviews",
            "-f", f"commit_id={sha}", "-f", "event=APPROVE", "-f", f"body={body}")
    except (subprocess.CalledProcessError, ValueError, KeyError, OSError) as e:
        print(f"refused: {type(e).__name__}")  # unreadable data or a failed call: the model reviews
        return 1
    print(f"approved PR #{pr_number} at {sha} without model (patch-id {pid})")
    return 0


def main(argv):
    if len(argv) == 3:
        return run_reapprove(argv[1], argv[2], os.environ)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
