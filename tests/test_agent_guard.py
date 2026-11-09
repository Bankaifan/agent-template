import json
import subprocess

import agent_guard as g
import pytest


@pytest.mark.parametrize("form", ["bankaifan-agent-author", "app/bankaifan-agent-author",
                                  "bankaifan-agent-author[bot]", "app/Bankaifan-Agent-Author[bot]"])
def test_all_login_forms_match(form):
    assert g.same_login(form, "bankaifan-agent-author[bot]")
    assert g.norm_login(form) == "bankaifan-agent-author"


def test_empty_and_different_logins_never_match():
    assert not g.same_login("", "")
    assert not g.same_login(None, "x")
    assert not g.same_login("mallory", "bankaifan-agent-author[bot]")


class Recorder:
    def __init__(self, fail_create=False, replies=None):
        self.calls, self.fail_create, self.replies = [], fail_create, replies or {}

    def __call__(self, *args):
        self.calls.append(args)
        if self.fail_create and args[:2] == ("label", "create"):
            raise subprocess.CalledProcessError(1, "gh")
        return self.replies.get(args[:2], "")


def test_labels_are_created_before_they_are_added():
    r = Recorder()
    g.add_labels("pr", 7, ["review:3", "needs-human"], r)
    assert r.calls == [("label", "create", "review:3", "--force"), ("label", "create", "needs-human", "--force"),
                       ("pr", "edit", "7", "--add-label", "review:3", "--add-label", "needs-human")]


def test_label_create_failure_does_not_stop_the_add():
    r = Recorder(fail_create=True)
    g.add_labels("issue", 3, ["agent:dev"], r)
    assert r.calls[-1] == ("issue", "edit", "3", "--add-label", "agent:dev")


T0 = "2026-11-09T10:00:00Z"


def test_dev_without_pr_is_silent():
    new = "2026-11-09T10:05:00Z"
    assert not g.dev_has_pr([{"headRefName": "agent/21-x", "createdAt": new}, {"headRefName": "main", "createdAt": new}], "22", T0)
    assert g.dev_has_pr([{"headRefName": "agent/22-slug", "createdAt": new}], "22", T0)
    assert not g.dev_has_pr([{"headRefName": "agent/220-slug", "createdAt": new}], "22", T0)


def test_dev_old_pr_for_same_issue_does_not_count():
    assert not g.dev_has_pr([{"headRefName": "agent/22-slug", "createdAt": "2026-11-01T00:00:00Z"}], "22", T0)


def test_fix_without_new_commit_is_silent():
    assert not g.head_moved("abc", "abc")
    assert not g.head_moved("abc", "")
    assert g.head_moved("abc", "def")


def test_review_missing_for_head_sha():
    reviews = [{"commit_id": "old", "user": {"login": "ap[bot]"}}, {"commit_id": "new", "user": {"login": "mallory"}}]
    assert not g.has_review(reviews, "ap[bot]", "new")
    assert g.has_review(reviews, "app/ap", "old")


def test_agent_pr_by_author_app_owner_or_label():
    assert g.is_agent_pr("app/my-author", [""], "my-author[bot]", "Bankaifan")
    assert g.is_agent_pr("Bankaifan", [""], "my-author[bot]", "Bankaifan")
    assert g.is_agent_pr("someone", ["agent:review"], "my-author[bot]", "Bankaifan")
    assert not g.is_agent_pr("someone", [""], "my-author[bot]", "Bankaifan")


def test_report_has_run_url_tail_and_masks_tokens():
    text = "\n".join(f"line {i}" for i in range(40)) + "\nghp_" + "a" * 30
    body = g.report("dev", "no PR was produced", "https://x/run/1", text)
    assert "https://x/run/1" in body and "line 39" in body and "line 5\n" not in body
    assert "ghp_" not in body and "***" in body
    assert "(no execution file)" in g.report("fix", "x", "", "")


def test_report_lists_denied_calls_not_the_raw_tail():
    denials = [{"tool_name": "Bash", "tool_input": {"command": "cat a.txt ghp_" + "b" * 30}},
               {"tool_name": "Read", "tool_input": {"file_path": "/etc/x"}}]
    denials += [{"tool_name": "Bash", "tool_input": {"command": f"ls {i}"}} for i in range(12)]
    text = json.dumps([{"type": "assistant"}, {"type": "result", "permission_denials": denials}])
    body = g.report("dev", "no PR", "https://x/run/1", text)
    assert "Denied tool calls:" in body and "Bash: cat a.txt" in body and "Read: /etc/x" in body
    assert "ghp_" not in body and "... and 4 more" in body and "ls 7" in body and "ls 8" not in body
    assert '"type"' not in body


def test_denied_calls_mask_token_straddling_the_cut():
    cmd = "x" * 140 + " ghp_" + "c" * 30
    out = g.denied_calls(json.dumps({"permission_denials": [{"tool_name": "Bash", "tool_input": {"command": cmd}}]}))
    assert out and "ghp_" not in out[0] and "c" * 5 not in out[0]


def test_report_without_denials_keeps_the_tail():
    body = g.report("dev", "no PR", "", json.dumps([{"type": "result", "permission_denials": []}]))
    assert "no denied tool calls found" in body and "permission_denials" in body


def test_escalate_issue_labels_comments_assigns(monkeypatch):
    monkeypatch.delenv("EXEC_FILE", raising=False)
    r = Recorder()
    g.escalate("dev", "22", False, "no PR", "Bankaifan", r)
    kinds = [c[:2] for c in r.calls]
    assert ("issue", "comment") in kinds and ("issue", "edit") in kinds
    assert r.calls[-1] == ("issue", "edit", "22", "--add-assignee", "Bankaifan")


def test_escalate_pr_requests_review_unless_owner_is_author(monkeypatch):
    monkeypatch.delenv("EXEC_FILE", raising=False)
    r = Recorder(replies={("pr", "view"): json.dumps({"author": {"login": "app/my-author"}})})
    g.escalate("fix", "5", True, "no fix", "Bankaifan", r)
    assert ("pr", "edit", "5", "--add-reviewer", "Bankaifan") in r.calls
    r = Recorder(replies={("pr", "view"): json.dumps({"author": {"login": "Bankaifan"}})})
    g.escalate("fix", "5", True, "no fix", "Bankaifan", r)
    assert ("pr", "edit", "5", "--add-reviewer", "Bankaifan") not in r.calls


@pytest.fixture
def stub_gh(tmp_path, monkeypatch):
    """A fake `gh` on PATH: logs each call to calls.log, answers `pr list`, `pr view` and `api` from env JSON."""
    script = tmp_path / "gh"
    script.write_text(
        '#!/bin/sh\necho "$*" >> "$GH_LOG"\n'
        'case "$1 $2" in\n'
        '  "pr list") printf %s "$GH_PR_LIST" ;;\n'
        '  "pr view") printf %s "$GH_PR_VIEW" ;;\n'
        '  "api --paginate") printf %s "$GH_REVIEWS" ;;\n'
        'esac\n')
    script.chmod(0o755)
    log = tmp_path / "calls.log"
    log.write_text("")
    monkeypatch.setenv("PATH", f"{tmp_path}:/usr/bin:/bin")
    monkeypatch.setenv("GH_LOG", str(log))
    monkeypatch.setenv("GH_REPO", "o/r")
    monkeypatch.delenv("EXEC_FILE", raising=False)
    monkeypatch.setenv("GH_PR_LIST", "[]")
    monkeypatch.setenv("GH_PR_VIEW", json.dumps({"headRefOid": "abc", "author": {"login": "app/x"}}))
    monkeypatch.setenv("GH_REVIEWS", "[[]]")
    return lambda: log.read_text().splitlines()


def test_cli_same_exit_codes():
    assert g.main(["g", "same", "app/Foo", "foo[bot]"]) == 0
    assert g.main(["g", "same", "mallory", "foo[bot]"]) == 1
    assert g.main(["g", "same", "", ""]) == 1


def test_cli_agent_pr_exit_codes(monkeypatch):
    monkeypatch.setenv("AUTHOR_BOT", "my-author[bot]")
    assert g.main(["g", "agent-pr", "app/my-author"]) == 0
    assert g.main(["g", "agent-pr", "someone", "x,agent:review"]) == 0
    assert g.main(["g", "agent-pr", "someone", "x"]) == 1
    assert g.main(["g", "agent-pr", "someone"]) == 1


def test_cli_label_creates_then_adds(stub_gh):
    assert g.main(["g", "label", "pr", "7", "agent:review"]) == 0
    assert stub_gh() == ["label create agent:review --force", "pr edit 7 --add-label agent:review"]


def test_cli_unknown_command_fails():
    assert g.main(["g", "bogus"]) == 2
    assert g.main(["g", "silent", "dev", "22"]) == 2


def test_silent_dev_escalates_without_new_pr(stub_gh, monkeypatch):
    monkeypatch.setenv("GH_PR_LIST", json.dumps([{"headRefName": "agent/22-x", "createdAt": "2026-11-01T00:00:00Z"}]))
    assert g.main(["g", "silent", "dev", "22", T0]) == 0
    assert any(c.startswith("issue comment 22") for c in stub_gh())
    assert "issue edit 22 --add-label needs-human" in stub_gh()


def test_silent_dev_quiet_with_new_pr(stub_gh, monkeypatch):
    monkeypatch.setenv("GH_PR_LIST", json.dumps([{"headRefName": "agent/22-x", "createdAt": "2026-11-09T10:05:00Z"}]))
    assert g.main(["g", "silent", "dev", "22", T0]) == 0
    assert not any(c.startswith("issue comment") for c in stub_gh())


def test_silent_fix_paths(stub_gh):
    assert g.main(["g", "silent", "fix", "5", "abc"]) == 0  # head unchanged -> escalate
    assert any(c.startswith("pr comment 5") for c in stub_gh())
    open_log = stub_gh()
    assert g.main(["g", "silent", "fix", "5", "old"]) == 0  # head moved -> quiet
    assert len(stub_gh()) == len(open_log) + 1  # only the pr view


def test_silent_review_paths(stub_gh, monkeypatch):
    monkeypatch.setenv("APPROVER_BOT", "ap[bot]")
    monkeypatch.delenv("PR_BODY", raising=False)  # CI sets it; this test checks the SHA-only path
    assert g.main(["g", "silent", "review", "5", "sha1"]) == 0  # no review -> escalate
    assert any(c.startswith("pr comment 5") for c in stub_gh())
    monkeypatch.setenv("GH_REVIEWS", json.dumps([[{"commit_id": "sha1", "user": {"login": "ap[bot]"}}]]))
    assert g.main(["g", "reviewed", "5", "sha1"]) == 0
    assert g.main(["g", "reviewed", "5", "other"]) == 1
    n = len(stub_gh())
    assert g.main(["g", "silent", "review", "5", "sha1"]) == 0
    assert not any(c.startswith("pr comment") for c in stub_gh()[n:])


def test_body_edit_on_same_sha_needs_a_new_review():
    revs = [{"commit_id": "s", "user": {"login": "ap[bot]"}, "body": "ok\nbody-hash: " + g.body_hash("Closes #1")}]
    assert g.has_review(revs, "ap", "s", "Closes #1")
    assert not g.has_review(revs, "ap", "s", "Refs #1")  # body edited: review again
    assert not g.has_review(revs, "ap", "t", "Closes #1")  # other SHA
    assert g.has_review([dict(revs[0], body="no marker")], "ap", "s")  # no body given: SHA only


def test_cli_reviewed_keys_on_body_hash(stub_gh, monkeypatch, capsys):
    monkeypatch.setenv("APPROVER_BOT", "ap[bot]")
    monkeypatch.setenv("PR_BODY", "Refs #1")
    assert g.main(["g", "body-hash"]) == 0
    h = capsys.readouterr().out.strip()
    assert h == g.body_hash("Refs #1") and len(h) == 12
    rev = {"commit_id": "s", "user": {"login": "ap[bot]"}, "body": "x\nbody-hash: " + h}
    monkeypatch.setenv("GH_REVIEWS", json.dumps([[rev]]))
    assert g.main(["g", "reviewed", "5", "s"]) == 0
    monkeypatch.setenv("PR_BODY", "Refs #2")
    assert g.main(["g", "reviewed", "5", "s"]) == 1
