import copy
import json
import subprocess

import agent_guard
import pytest
import reapprove

APPROVER, OWNER = "reviewer-app", "Bankaifan"
OLD, NEW = "a" * 40, "b" * 40
BODY = "Closes #1"
BH = agent_guard.body_hash(BODY)
CODEOWNERS = "/AGENTS.md @Bankaifan\n/.github/rulesets/ @Bankaifan\n"

PATCH = "From x\n---\n a.py | 1 +\ndiff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1,2 @@\n x\n+y\n"
OTHER = PATCH.replace("+y", "+z")

PR = {"number": 5, "state": "OPEN", "headRefOid": NEW, "headRefName": "agent/1-x", "isCrossRepository": False,
      "labels": [], "commits": [{"oid": NEW}], "files": [{"path": "tools/a.py"}], "body": BODY}


def review(state="APPROVED", sha=OLD, body=f"ok\nbody-hash: {BH}", rid=1, user=APPROVER):
    return {"id": rid, "user": {"login": user}, "state": state, "commit_id": sha, "body": body}


def event(rid=1, prev="approved"):
    return {"event": "review_dismissed", "dismissed_review": {"review_id": rid}, "previous_review_state": prev}


def patches(new=PATCH, old=PATCH):
    return lambda sha: new if sha == NEW else old


def decide(pr=PR, reviews=None, timeline=(), fetch=None, codeowners=CODEOWNERS):
    return reapprove.decide(pr, [review()] if reviews is None else reviews, list(timeline), NEW, APPROVER,
                            codeowners, OWNER, fetch or patches())


def with_pr(**kw):
    p = copy.deepcopy(PR)
    p.update(kw)
    return p


def test_same_patch_and_body_hash_approves():
    old, pid, why = decide()
    assert (old, why) == (OLD, None) and pid


def test_changed_patch_refuses():
    assert decide(fetch=patches(new=OTHER))[2] == "patch changed"


def test_empty_patch_refuses():
    assert decide(fetch=patches(new="", old=""))[2] == "patch changed"


def test_edited_body_refuses():
    assert decide(reviews=[review(body="ok\nbody-hash: " + "0" * 16)])[2]
    assert decide(reviews=[review(body="ok")])[2]


@pytest.mark.parametrize("pr", [
    with_pr(commits=[{"oid": OLD}, {"oid": NEW}]),
    with_pr(labels=[{"name": "risk:security"}]),
    with_pr(labels=[{"name": "needs-human"}]),
    with_pr(files=[{"path": "AGENTS.md"}]),
    with_pr(files=[{"path": ".github/rulesets/main.json"}]),
    with_pr(files=[{"path": "docs/design/0009-x.md"}]),
    with_pr(files=[]),
    with_pr(state="CLOSED"),
    with_pr(isCrossRepository=True),
    with_pr(headRefName="feature/x"),
])
def test_ineligible_pr_refuses(pr):
    assert decide(pr=pr)[2]


def test_no_earlier_approval_refuses():
    assert decide(reviews=[])[2]
    assert decide(reviews=[review(user="someone-else")])[2]


def test_changes_requested_refuses():
    assert decide(reviews=[review(state="CHANGES_REQUESTED")])[2]


def test_dismissed_counts_only_with_prior_state_approved():
    assert decide(reviews=[review(state="DISMISSED")], timeline=[event(prev="approved")])[2] is None
    assert decide(reviews=[review(state="DISMISSED")], timeline=[event(prev="changes_requested")])[2]


def test_unreadable_prior_state_refuses():
    assert decide(reviews=[review(state="DISMISSED")], timeline=[])[2]
    assert decide(reviews=[review(state="DISMISSED")], timeline=[event(prev=None)])[2]
    assert decide(reviews=[review(state="DISMISSED")], timeline=[event(rid=99)])[2]


def test_script_review_chains_from_newest_head():
    mid = "c" * 40
    chain = [review(sha=OLD, rid=1), review(state="DISMISSED", sha=mid, rid=2,
                                            body=f"Re-approved without model\n\nbody-hash: {BH}")]
    old, _, why = decide(reviews=chain, timeline=[event(rid=2)], fetch=lambda s: PATCH)
    assert (old, why) == (mid, None)


def test_newest_review_decides():
    older_ok_newer_bad = [review(rid=1), review(state="CHANGES_REQUESTED", sha="c" * 40, rid=2)]
    assert decide(reviews=older_ok_newer_bad)[2]


def test_already_reviewed_head_refuses():
    assert decide(reviews=[review(sha=NEW)])[2]


def _git(tmp_path, *args):
    return subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout


def test_patch_id_of_a_mode_only_change_is_measured(tmp_path):
    """Measured with real git: does `git patch-id --verbatim` see a file-mode-only change?"""
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.sh").write_text("hi\n")
    _git(tmp_path, "add", "a.sh")
    _git(tmp_path, "commit", "-qm", "one")
    (tmp_path / "a.sh").chmod(0o755)
    _git(tmp_path, "commit", "-qam", "mode only")
    mode_patch = _git(tmp_path, "format-patch", "-1", "--stdout")
    assert "old mode 100644" in mode_patch and "new mode 100755" in mode_patch
    # Measured: a mode-only patch does get an id (it is not empty), so a mode change cannot hide as "no patch".
    mode_id = reapprove.patch_id(mode_patch)
    assert mode_id
    # The case that matters: the same content change, once without and once with an added mode change, must differ.
    (tmp_path / "a.sh").write_text("hi\nmore\n")
    _git(tmp_path, "commit", "-qam", "content only")
    content_only = _git(tmp_path, "format-patch", "-1", "--stdout")
    _git(tmp_path, "reset", "-q", "--hard", "HEAD~2")
    (tmp_path / "a.sh").write_text("hi\nmore\n")
    (tmp_path / "a.sh").chmod(0o755)
    _git(tmp_path, "commit", "-qam", "content and mode")
    content_and_mode = _git(tmp_path, "format-patch", "-1", "--stdout")
    assert reapprove.patch_id(content_only) != reapprove.patch_id(content_and_mode)
    assert reapprove.patch_id(content_only) != mode_id


def test_patch_id_ignores_commit_metadata_but_sees_content(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / "a").write_text("x\n")
    _git(tmp_path, "add", "a")
    _git(tmp_path, "commit", "-qm", "base")
    (tmp_path / "a").write_text("x\ny\n")
    _git(tmp_path, "commit", "-qam", "first")
    p1 = _git(tmp_path, "format-patch", "-1", "--stdout")
    _git(tmp_path, "commit", "-q", "--amend", "-m", "other subject")
    p2 = _git(tmp_path, "format-patch", "-1", "--stdout")
    assert p1 != p2 and reapprove.patch_id(p1) == reapprove.patch_id(p2) != ""


def make_run(pr=PR, reviews=None, timeline=(), patch_new=PATCH, patch_old=PATCH, fail=False):
    calls = []

    def run(*args):
        calls.append(args)
        if fail:
            raise subprocess.CalledProcessError(1, "gh")
        if args[:2] == ("pr", "view"):
            return json.dumps(pr)
        if args[0] == "api" and args[-1].endswith("/reviews"):
            return json.dumps([[review()] if reviews is None else reviews])
        if args[0] == "api" and args[-1].endswith("/timeline"):
            return json.dumps([list(timeline)])
        if args[0] == "api" and "/commits/" in args[-3]:
            return patch_new if args[-3].endswith(NEW) else patch_old
        return ""

    run.calls = calls
    return run


ENV = {"GH_REPO": "o/r", "APPROVER_BOT": APPROVER}


@pytest.fixture(autouse=True)
def _repo_env(monkeypatch):
    monkeypatch.setenv("GH_REPO", "o/r")


def test_run_approves_with_the_marker_body():
    run = make_run()
    assert reapprove.run_reapprove(5, NEW, ENV, run) == 0
    review_call = next(c for c in run.calls if c[-1:] and "event=APPROVE" in c)
    assert f"commit_id={NEW}" in review_call and "POST" in review_call
    assert review_call[3].endswith("/pulls/5/reviews")
    assert f"body-hash: {BH}" in review_call[-1] and "Re-approved without model" in review_call[-1]
    assert not [c for c in run.calls if c[:2] == ("pr", "review")]


def test_run_refuses_when_head_moves_before_posting():
    base = make_run()

    def run(*args):
        if args[:2] == ("pr", "view") and args[-1] == "headRefOid":
            return json.dumps({"headRefOid": "c" * 40})
        return base(*args)

    run.calls = base.calls
    assert reapprove.run_reapprove(5, NEW, ENV, run) == 1
    assert not [c for c in run.calls if "event=APPROVE" in c]


def test_100_files_refuses():
    pr = {**PR, "files": [{"path": f"src/f{i}.py"} for i in range(100)]}
    assert decide(pr=pr)[2]


def test_run_refuses_without_review_call_when_patch_changed():
    run = make_run(patch_new=OTHER)
    assert reapprove.run_reapprove(5, NEW, ENV, run) == 1
    assert not [c for c in run.calls if c[:2] == ("pr", "review")]


def test_run_refuses_when_head_moved_or_gh_fails_or_no_approver():
    assert reapprove.run_reapprove(5, "c" * 40, ENV, make_run()) == 1
    assert reapprove.run_reapprove(5, NEW, ENV, make_run(fail=True)) == 1
    assert reapprove.run_reapprove(5, NEW, {"GH_REPO": "o/r"}, make_run()) == 1


def test_main_usage():
    assert reapprove.main(["reapprove.py"]) == 2
